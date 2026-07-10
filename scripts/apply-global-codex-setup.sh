#!/usr/bin/env bash

set -euo pipefail

minimum_codex_version="0.134.0"
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
codex_home="${CODEX_HOME:-$HOME/.codex}"
user_skills_home="${HOME}/.agents/skills"
trust_project=true
check_only=false
reset_config=false
reset_agents=false

usage() {
  cat <<'EOF'
Usage:
  ./scripts/apply-global-codex-setup.sh [options]

Options:
  --check                Verify managed files exactly without applying changes
  --codex-home PATH      Override the target Codex home directory
  --user-skills-home PATH
                         Override the target user skills directory
  --repo PATH            Override the repository root used for package sources and trust
  --no-trust-project     Do not add or check the repository trust entry
  --reset-config         Back up and replace config.toml and conflicting managed profiles
  --reset-agents         Back up and replace AGENTS.md instead of preserving user guidance
  -h, --help             Show this help text

Environment:
  CODEX_BIN              Codex executable name or path (default: resolved codex on PATH)
EOF
}

invalid_argument() {
  printf '%s\n' "$1" >&2
  usage >&2
  exit 2
}

require_option_value() {
  local option="$1"
  local count="$2"
  if ((count < 2)); then
    invalid_argument "Missing value for option: ${option}"
  fi
}

while (($# > 0)); do
  case "$1" in
    --check)
      check_only=true
      shift
      ;;
    --codex-home)
      require_option_value "$1" "$#"
      codex_home="$2"
      shift 2
      ;;
    --user-skills-home)
      require_option_value "$1" "$#"
      user_skills_home="$2"
      shift 2
      ;;
    --repo)
      require_option_value "$1" "$#"
      repo_root="$2"
      shift 2
      ;;
    --no-trust-project)
      trust_project=false
      shift
      ;;
    --reset-config)
      reset_config=true
      shift
      ;;
    --reset-agents)
      reset_agents=true
      shift
      ;;
    -h | --help)
      usage
      exit 0
      ;;
    *)
      invalid_argument "Unknown option: $1"
      ;;
  esac
done

if [[ -z "$codex_home" || -z "$user_skills_home" || -z "$repo_root" ]]; then
  invalid_argument "Path options must not be empty."
fi

if [[ "$check_only" == true && ("$reset_config" == true || "$reset_agents" == true) ]]; then
  invalid_argument "--check cannot be combined with --reset-config or --reset-agents."
fi

if [[ ! -d "$repo_root" ]]; then
  printf 'Repository root is not a directory: %s\n' "$repo_root" >&2
  exit 1
fi
repo_root="$(cd "$repo_root" && pwd -P)"

template_root="${repo_root}/templates/global-codex"
source_agents="${template_root}/AGENTS.md"
source_config="${template_root}/config.toml"
source_repo_agents="${template_root}/agents"
source_repo_profiles="${template_root}/profiles"
source_repo_skills="${template_root}/skills"
target_agents="${codex_home}/AGENTS.md"
target_config="${codex_home}/config.toml"
target_agents_dir="${codex_home}/agents"
playwright_output="${codex_home}/playwright-output/isolated"
timestamp="$(date +%Y-%m-%dT%H-%M-%S)"
backup_root="${codex_home}/backups/install-archives/${timestamp}-$$"
agents_marker_begin='<!-- CODEX_GODMODE_GLOBAL_AGENTS:BEGIN -->'
agents_marker_end='<!-- CODEX_GODMODE_GLOBAL_AGENTS:END -->'
legacy_v1_1_agents_sha256='b660e0f29ea87e1817b702c5a52d960fe7230f807ec8adb927c18f14ed101451'
profile_names=(
  godmode-swiftui.config.toml
  godmode-web.config.toml
  godmode-flutter.config.toml
  godmode-review.config.toml
)

fail() {
  local message="$1"
  local exit_code="${2:-1}"
  printf '%s\n' "$message" >&2
  exit "$exit_code"
}

require_file() {
  [[ -f "$1" ]] || fail "Required file missing: $1"
}

require_dir() {
  [[ -d "$1" ]] || fail "Required directory missing: $1"
}

version_at_least() {
  local actual="$1"
  local required="$2"
  local actual_major actual_minor actual_patch required_major required_minor required_patch
  IFS=. read -r actual_major actual_minor actual_patch <<<"$actual"
  IFS=. read -r required_major required_minor required_patch <<<"$required"
  ((10#$actual_major > 10#$required_major)) ||
    ((10#$actual_major == 10#$required_major && 10#$actual_minor > 10#$required_minor)) ||
    ((10#$actual_major == 10#$required_major && 10#$actual_minor == 10#$required_minor && 10#$actual_patch >= 10#$required_patch))
}

resolve_codex_runtime() {
  local requested="${CODEX_BIN:-codex}"
  local version_output=""
  local parsed_version=""

  [[ -n "$requested" ]] || fail "CODEX_BIN must not be empty." 3
  if [[ "$requested" == */* ]]; then
    [[ -x "$requested" && ! -d "$requested" ]] || fail "Codex executable is missing or not executable: $requested" 3
    codex_bin="$requested"
  else
    codex_bin="$(command -v "$requested" 2>/dev/null || true)"
    [[ -n "$codex_bin" ]] || fail "Codex CLI was not found. Install Codex >= ${minimum_codex_version} or set CODEX_BIN." 3
  fi

  if ! version_output="$("$codex_bin" --version 2>&1)"; then
    fail "Could not query Codex version from ${codex_bin}: ${version_output}" 3
  fi
  parsed_version="$(printf '%s\n' "$version_output" | sed -nE 's/.*[^0-9]([0-9]+\.[0-9]+\.[0-9]+).*/\1/p' | head -n 1)"
  [[ -n "$parsed_version" ]] || fail "Could not parse Codex version from: ${version_output}" 3
  if ! version_at_least "$parsed_version" "$minimum_codex_version"; then
    fail "Incompatible Codex CLI ${parsed_version} at ${codex_bin}; version >= ${minimum_codex_version} is required." 3
  fi
  if ! "$codex_bin" help doctor >/dev/null 2>&1; then
    fail "Codex CLI ${parsed_version} at ${codex_bin} does not support 'codex help doctor'." 3
  fi

  printf 'Codex preflight: %s (%s)\n' "$codex_bin" "$version_output"
}

agents_marker_state() {
  local path="$1"
  awk -v begin="$agents_marker_begin" -v end="$agents_marker_end" '
    {
      line = $0
      sub(/\r$/, "", line)
      if (line == begin) {
        begin_count++
        begin_line = NR
      }
      if (line == end) {
        end_count++
        end_line = NR
      }
    }
    END {
      if (begin_count == 0 && end_count == 0) exit 10
      if (begin_count == 1 && end_count == 1 && begin_line < end_line) exit 0
      exit 1
    }
  ' "$path"
}

extract_managed_agents() {
  local path="$1"
  awk -v begin="$agents_marker_begin" -v end="$agents_marker_end" '
    {
      line = $0
      sub(/\r$/, "", line)
      if (line == begin) in_managed = 1
      if (in_managed) print line
      if (line == end && in_managed) exit
    }
  ' "$path"
}

source_without_markers() {
  awk -v begin="$agents_marker_begin" -v end="$agents_marker_end" '
    $0 != begin && $0 != end { print }
  ' "$source_agents"
}

normalized_sha256_file() {
  if command -v shasum >/dev/null 2>&1; then
    sed $'s/\r$//' "$1" | shasum -a 256 | awk '{print $1}'
  elif command -v sha256sum >/dev/null 2>&1; then
    sed $'s/\r$//' "$1" | sha256sum | awk '{print $1}'
  else
    return 1
  fi
}

is_known_unmarked_agents() {
  local path="$1"
  local digest=""
  if cmp -s "$path" <(source_without_markers); then
    return 0
  fi
  digest="$(normalized_sha256_file "$path" 2>/dev/null || true)"
  [[ "$digest" == "$legacy_v1_1_agents_sha256" ]]
}

toml_escape() {
  printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g'
}

project_trust_header() {
  printf '[projects."%s"]' "$(toml_escape "$repo_root")"
}

has_project_trust() {
  local config_path="$1"
  grep -F "$(project_trust_header)" "$config_path" >/dev/null 2>&1
}

warn_legacy_inline_profiles() {
  local config_path="$1"
  if grep -Eq '^[[:space:]]*\[profiles\.' "$config_path" 2>/dev/null; then
    printf '[warn] %s contains legacy inline [profiles.*] tables; Codex >= 0.134.0 loads separate NAME.config.toml files instead.\n' "$config_path" >&2
  fi
}

preflight_sources_and_targets() {
  local profile_name=""
  local source_profile=""
  local target_profile=""
  local marker_status=0

  require_file "$source_agents"
  require_file "$source_config"
  require_dir "$source_repo_agents"
  require_dir "$source_repo_profiles"
  require_dir "$source_repo_skills"
  for profile_name in "${profile_names[@]}"; do
    require_file "${source_repo_profiles}/${profile_name}"
  done

  if ! agents_marker_state "$source_agents"; then
    fail "Packaged AGENTS.md must contain exactly one ordered managed marker pair: $source_agents"
  fi

  [[ ! -e "$target_config" || -f "$target_config" ]] || fail "Target config is not a regular file: $target_config"
  [[ ! -e "$target_agents" || -f "$target_agents" ]] || fail "Target AGENTS is not a regular file: $target_agents"

  if [[ -f "$target_agents" ]]; then
    if agents_marker_state "$target_agents"; then
      marker_status=0
    else
      marker_status=$?
      if [[ "$marker_status" -ne 10 ]]; then
        fail "Malformed managed markers in ${target_agents}; expected exactly one BEGIN followed by one END."
      fi
    fi
  fi

  for profile_name in "${profile_names[@]}"; do
    source_profile="${source_repo_profiles}/${profile_name}"
    target_profile="${codex_home}/${profile_name}"
    if [[ -e "$target_profile" && ! -f "$target_profile" ]]; then
      fail "Managed profile target is not a regular file: ${target_profile}" 4
    fi
    if [[ -f "$target_profile" ]] && ! cmp -s "$source_profile" "$target_profile"; then
      if [[ "$reset_config" != true ]]; then
        fail "Managed profile conflict: ${target_profile}. Re-run with --reset-config to back up and replace managed profiles." 4
      fi
    fi
  done
}

backup_path() {
  local path="$1"
  local destination=""
  [[ -e "$path" || -L "$path" ]] || return 0

  case "$path" in
    "$target_agents") destination="${backup_root}/root/AGENTS.md" ;;
    "$target_config") destination="${backup_root}/root/config.toml" ;;
    "$target_agents_dir"/*) destination="${backup_root}/agents/$(basename "$path")" ;;
    "$user_skills_home"/*) destination="${backup_root}/skills/$(basename "$path")" ;;
    "$codex_home"/*.config.toml) destination="${backup_root}/profiles/$(basename "$path")" ;;
    *) destination="${backup_root}/misc/$(basename "$path")" ;;
  esac

  mkdir -p "$(dirname "$destination")"
  cp -R "$path" "$destination"
  printf 'Backed up %s -> %s\n' "$path" "$destination"
}

atomic_install_file() {
  local source_path="$1"
  local target_path="$2"
  local target_dir=""
  local temp_path=""
  target_dir="$(dirname "$target_path")"
  temp_path="$(mktemp "${target_dir}/.$(basename "$target_path").tmp.XXXXXX")"
  install -m 0644 "$source_path" "$temp_path"
  mv -f "$temp_path" "$target_path"
}

archive_legacy_discovery_conflicts() {
  local path=""
  local archived_path=""
  local found=false

  if [[ -d "$target_agents_dir" ]]; then
    while IFS= read -r path; do
      [[ -n "$path" ]] || continue
      found=true
      archived_path="${backup_root}/legacy-discovery-conflicts/agents/$(basename "$path")"
      mkdir -p "$(dirname "$archived_path")"
      mv "$path" "$archived_path"
      printf 'Archived legacy agent backup %s -> %s\n' "$path" "$archived_path"
    done < <(find "$target_agents_dir" -maxdepth 1 -mindepth 1 -name '*.backup-*' | sort)
  fi

  if [[ -d "$user_skills_home" ]]; then
    while IFS= read -r path; do
      [[ -n "$path" ]] || continue
      found=true
      archived_path="${backup_root}/legacy-discovery-conflicts/skills/$(basename "$path")"
      mkdir -p "$(dirname "$archived_path")"
      mv "$path" "$archived_path"
      printf 'Archived legacy skill backup %s -> %s\n' "$path" "$archived_path"
    done < <(find "$user_skills_home" -maxdepth 1 -mindepth 1 -name '*.backup-*' | sort)
  fi

  if [[ "$found" == true ]]; then
    printf 'Legacy discovery conflicts were moved under %s\n' "$backup_root"
  fi
}

render_config_template() {
  local output_path="$1"
  local escaped_codex_home=""
  escaped_codex_home="$(printf '%s' "$(toml_escape "$codex_home")" | sed 's/[&#]/\\&/g')"
  sed "s#__CODEX_HOME__#${escaped_codex_home}#g" "$source_config" >"$output_path"
}

append_project_trust() {
  local config_path="$1"
  if has_project_trust "$config_path"; then
    return 0
  fi
  printf '\n%s\ntrust_level = "trusted"\n' "$(project_trust_header)" >>"$config_path"
  printf 'Added trusted project: %s\n' "$repo_root"
}

install_config() {
  local temp_path=""

  if [[ -f "$target_config" && "$reset_config" != true ]]; then
    printf 'Preserved existing config byte-for-byte: %s\n' "$target_config"
    if [[ "$trust_project" == true ]] && ! has_project_trust "$target_config"; then
      printf '[warn] Existing config is unchanged and has no trust entry for %s. Add it manually or use --reset-config.\n' "$repo_root" >&2
    fi
    warn_legacy_inline_profiles "$target_config"
    return 0
  fi

  if [[ -f "$target_config" ]]; then
    backup_path "$target_config"
  fi
  temp_path="$(mktemp "${codex_home}/.config.toml.tmp.XXXXXX")"
  render_config_template "$temp_path"
  if [[ "$trust_project" == true ]]; then
    append_project_trust "$temp_path"
  fi
  chmod 0644 "$temp_path"
  mv -f "$temp_path" "$target_config"
  if [[ "$reset_config" == true ]]; then
    printf 'Reset global config from template: %s\n' "$target_config"
  else
    printf 'Installed global config from template: %s\n' "$target_config"
  fi
}

install_agents_template() {
  local marker_status=0
  local temp_path=""

  if [[ ! -f "$target_agents" ]]; then
    atomic_install_file "$source_agents" "$target_agents"
    printf 'Installed global AGENTS template: %s\n' "$target_agents"
    return 0
  fi

  if [[ "$reset_agents" == true ]]; then
    backup_path "$target_agents"
    atomic_install_file "$source_agents" "$target_agents"
    printf 'Reset global AGENTS from template: %s\n' "$target_agents"
    return 0
  fi

  if agents_marker_state "$target_agents"; then
    if cmp -s "$source_agents" <(extract_managed_agents "$target_agents"); then
      printf 'Managed global AGENTS block already exact: %s\n' "$target_agents"
      return 0
    fi

    backup_path "$target_agents"
    temp_path="$(mktemp "${codex_home}/.AGENTS.md.tmp.XXXXXX")"
    awk -v begin="$agents_marker_begin" -v end="$agents_marker_end" '
      FNR == NR { source = source $0 ORS; next }
      {
        line = $0
        sub(/\r$/, "", line)
      }
      line == begin {
        printf "%s", source
        in_managed = 1
        next
      }
      in_managed && line == end {
        in_managed = 0
        next
      }
      !in_managed { print $0 }
    ' "$source_agents" "$target_agents" >"$temp_path"
    chmod 0644 "$temp_path"
    mv -f "$temp_path" "$target_agents"
    printf 'Updated exact managed AGENTS block and preserved user guidance: %s\n' "$target_agents"
    return 0
  else
    marker_status=$?
  fi

  if [[ "$marker_status" -ne 10 ]]; then
    fail "Malformed managed markers reached install unexpectedly: $target_agents"
  fi

  backup_path "$target_agents"
  if is_known_unmarked_agents "$target_agents"; then
    atomic_install_file "$source_agents" "$target_agents"
    printf 'Migrated unmarked GodMode v1.1 AGENTS guidance without duplication: %s\n' "$target_agents"
    return 0
  fi

  temp_path="$(mktemp "${codex_home}/.AGENTS.md.tmp.XXXXXX")"
  {
    cat "$source_agents"
    printf '\n## Preserved User Guidance\n\n'
    printf '<!-- Preserved from the previous ~/.codex/AGENTS.md during the %s install. -->\n\n' "$timestamp"
    cat "$target_agents"
    [[ ! -s "$target_agents" ]] || [[ "$(tail -c 1 "$target_agents" | wc -l | tr -d ' ')" == "1" ]] || printf '\n'
  } >"$temp_path"
  chmod 0644 "$temp_path"
  mv -f "$temp_path" "$target_agents"
  printf 'Installed managed AGENTS block and preserved custom user guidance: %s\n' "$target_agents"
}

install_profiles() {
  local profile_name=""
  local source_path=""
  local target_path=""
  for profile_name in "${profile_names[@]}"; do
    source_path="${source_repo_profiles}/${profile_name}"
    target_path="${codex_home}/${profile_name}"
    if [[ -f "$target_path" ]] && cmp -s "$source_path" "$target_path"; then
      printf 'Managed profile already exact: %s\n' "$target_path"
      continue
    fi
    if [[ -e "$target_path" || -L "$target_path" ]]; then
      backup_path "$target_path"
    fi
    atomic_install_file "$source_path" "$target_path"
    printf 'Installed managed profile: %s\n' "$target_path"
  done
}

install_agent_files() {
  local source_path=""
  local target_path=""
  for source_path in "${source_repo_agents}"/*.toml; do
    [[ -f "$source_path" ]] || continue
    target_path="${target_agents_dir}/$(basename "$source_path")"
    if [[ -f "$target_path" ]] && cmp -s "$source_path" "$target_path"; then
      continue
    fi
    if [[ -e "$target_path" || -L "$target_path" ]]; then
      backup_path "$target_path"
      rm -rf "$target_path"
    fi
    atomic_install_file "$source_path" "$target_path"
  done
}

skill_dirs_exact() {
  local source_dir="$1"
  local target_dir="$2"
  [[ -d "$target_dir" ]] && diff -qr "$source_dir" "$target_dir" >/dev/null 2>&1
}

install_skill_dirs() {
  local source_dir=""
  local target_dir=""
  local stage_dir=""
  for source_dir in "${source_repo_skills}"/*; do
    [[ -d "$source_dir" ]] || continue
    target_dir="${user_skills_home}/$(basename "$source_dir")"
    if skill_dirs_exact "$source_dir" "$target_dir"; then
      continue
    fi
    if [[ -e "$target_dir" || -L "$target_dir" ]]; then
      backup_path "$target_dir"
    fi
    stage_dir="$(mktemp -d "${user_skills_home}/.$(basename "$source_dir").tmp.XXXXXX")"
    cp -R "${source_dir}/." "$stage_dir/"
    rm -rf "$target_dir"
    mv "$stage_dir" "$target_dir"
  done
}

check_path() {
  local path="$1"
  local label="$2"
  if [[ -e "$path" ]]; then
    printf '[ok] %s: %s\n' "$label" "$path"
  else
    printf '[missing] %s: %s\n' "$label" "$path"
    return 1
  fi
}

check_exact_file() {
  local source_path="$1"
  local target_path="$2"
  local label="$3"
  if [[ -f "$target_path" ]] && cmp -s "$source_path" "$target_path"; then
    printf '[ok] %s exact\n' "$label"
  else
    printf '[drift] %s: %s\n' "$label" "$target_path"
    return 1
  fi
}

check_exact_skill() {
  local source_dir="$1"
  local target_dir="$2"
  local label="$3"
  if skill_dirs_exact "$source_dir" "$target_dir"; then
    printf '[ok] %s exact\n' "$label"
  else
    printf '[drift] %s: %s\n' "$label" "$target_dir"
    return 1
  fi
}

check_no_legacy_discovery_conflicts() {
  local root="$1"
  local label="$2"
  local conflicts=""
  if [[ ! -d "$root" ]]; then
    printf '[ok] %s clean\n' "$label"
    return 0
  fi
  conflicts="$(find "$root" -maxdepth 1 -mindepth 1 -name '*.backup-*' | sort || true)"
  if [[ -n "$conflicts" ]]; then
    printf '[invalid] %s contains legacy backup artifacts\n%s\n' "$label" "$conflicts"
    return 1
  fi
  printf '[ok] %s clean\n' "$label"
}

run_check() {
  local status=0
  local source_path=""
  local target_path=""
  local source_dir=""
  local profile_name=""
  local marker_status=0

  check_path "$target_agents" "Global AGENTS" || status=1
  check_path "$target_config" "Global config" || status=1
  check_path "$target_agents_dir" "Global agents dir" || status=1
  check_path "$user_skills_home" "User skills home" || status=1
  check_path "$playwright_output" "Playwright output" || status=1
  check_no_legacy_discovery_conflicts "$target_agents_dir" "Global agents dir" || status=1
  check_no_legacy_discovery_conflicts "$user_skills_home" "User skills home" || status=1

  if [[ -f "$target_agents" ]]; then
    if agents_marker_state "$target_agents"; then
      if cmp -s "$source_agents" <(extract_managed_agents "$target_agents"); then
        printf '[ok] Global AGENTS managed block exact\n'
      else
        printf '[drift] Global AGENTS managed block\n'
        status=1
      fi
    else
      marker_status=$?
      printf '[invalid] Global AGENTS marker state (%s)\n' "$marker_status"
      status=1
    fi
  fi

  if [[ -f "$target_config" ]]; then
    warn_legacy_inline_profiles "$target_config"
    if [[ "$trust_project" == true ]]; then
      if has_project_trust "$target_config"; then
        printf '[ok] trusted project entry\n'
      else
        printf '[warn] Existing config has no trust entry for %s and remains unchanged.\n' "$repo_root" >&2
      fi
    fi
  fi

  for profile_name in "${profile_names[@]}"; do
    check_exact_file "${source_repo_profiles}/${profile_name}" "${codex_home}/${profile_name}" "Managed profile ${profile_name}" || status=1
  done

  for source_path in "${source_repo_agents}"/*.toml; do
    [[ -f "$source_path" ]] || continue
    target_path="${target_agents_dir}/$(basename "$source_path")"
    check_exact_file "$source_path" "$target_path" "Global agent $(basename "$source_path" .toml)" || status=1
  done

  for source_dir in "${source_repo_skills}"/*; do
    [[ -d "$source_dir" ]] || continue
    check_exact_skill "$source_dir" "${user_skills_home}/$(basename "$source_dir")" "Global skill $(basename "$source_dir")" || status=1
  done

  if [[ "$status" -ne 0 ]]; then
    printf '\nGlobal Codex setup check failed.\n' >&2
    return 1
  fi
  printf '\nGlobal Codex setup check passed.\n'
}

# Nothing below this point mutates a target until every preflight gate is green.
resolve_codex_runtime
preflight_sources_and_targets

if [[ "$check_only" == true ]]; then
  run_check
  exit $?
fi

mkdir -p "$codex_home" "$user_skills_home" "$playwright_output" "$target_agents_dir"
archive_legacy_discovery_conflicts
install_agents_template
install_config
install_profiles
install_agent_files
install_skill_dirs

printf '\nInstalled global Codex setup to %s\n' "$codex_home"
printf 'Installed global agents to %s\n' "$target_agents_dir"
printf 'Installed user skill root at %s\n' "$user_skills_home"
printf 'Prepared Playwright output directory at %s\n' "$playwright_output"

run_check
