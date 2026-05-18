#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
codex_home="${CODEX_HOME:-$HOME/.codex}"
user_skills_home="${HOME}/.agents/skills"
trust_project=true
check_only=false

usage() {
  cat <<'EOF'
Usage:
  ./scripts/apply-global-codex-setup.sh [options]

Options:
  --check                Verify the installed global setup instead of applying it
  --codex-home PATH      Override the target Codex home directory
  --user-skills-home PATH
                         Override the target user skills directory
  --repo PATH            Override the repository root used for templates, agents, skills, and trust
  --no-trust-project     Do not add the repository path to [projects."<path>"]
  -h, --help             Show this help text
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --check)
      check_only=true
      shift
      ;;
    --codex-home)
      codex_home="$2"
      shift 2
      ;;
    --user-skills-home)
      user_skills_home="$2"
      shift 2
      ;;
    --repo)
      repo_root="$2"
      shift 2
      ;;
    --no-trust-project)
      trust_project=false
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      printf 'Unknown option: %s\n' "$1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

template_root="${repo_root}/templates/global-codex"
source_agents="${template_root}/AGENTS.md"
source_config="${template_root}/config.toml"
source_repo_agents="${repo_root}/templates/global-codex/agents"
source_repo_skills="${repo_root}/templates/global-codex/skills"
target_agents="${codex_home}/AGENTS.md"
target_config="${codex_home}/config.toml"
target_agents_dir="${codex_home}/agents"
playwright_output="${codex_home}/playwright-output/isolated"
timestamp="$(date +%Y-%m-%dT%H-%M-%S)"
backup_root="${codex_home}/backups/install-archives/${timestamp}"

require_file() {
  local path="$1"
  if [[ ! -f "$path" ]]; then
    printf 'Required file missing: %s\n' "$path" >&2
    exit 1
  fi
}

require_dir() {
  local path="$1"
  if [[ ! -d "$path" ]]; then
    printf 'Required directory missing: %s\n' "$path" >&2
    exit 1
  fi
}

backup_path() {
  local path="$1"
  if [[ -e "$path" ]]; then
    local backup_path=""
    case "$path" in
      "$target_agents")
        backup_path="${backup_root}/root/AGENTS.md"
        ;;
      "$target_config")
        backup_path="${backup_root}/root/config.toml"
        ;;
      "$target_agents_dir"/*)
        backup_path="${backup_root}/agents/$(basename "$path")"
        ;;
      "$user_skills_home"/*)
        backup_path="${backup_root}/skills/$(basename "$path")"
        ;;
      *)
        backup_path="${backup_root}/misc/$(basename "$path")"
        ;;
    esac
    mkdir -p "$(dirname "$backup_path")"
    cp -R "$path" "$backup_path"
    printf 'Backed up %s -> %s\n' "$path" "$backup_path"
  fi
}

archive_legacy_discovery_conflicts() {
  local path=""
  local found=false

  if [[ -d "$target_agents_dir" ]]; then
    while IFS= read -r path; do
      local archived_path=""
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
      local archived_path=""
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
  local escaped_codex_home rendered_tmp
  escaped_codex_home="$(printf '%s' "$codex_home" | sed 's/[\/&]/\\&/g')"
  rendered_tmp="$(mktemp)"
  sed "s#__CODEX_HOME__#${escaped_codex_home}#g" "$source_config" > "$rendered_tmp"

  if [[ ! -f "$target_config" ]]; then
    mv "$rendered_tmp" "$target_config"
    return 0
  fi

  local merged_tmp summary_tmp
  merged_tmp="$(mktemp)"
  summary_tmp="$(mktemp)"

  awk -v summary_file="$summary_tmp" '
    function flush_section(   ) {
      if (cur_name != "") {
        if (file_index == 1) {
          tmpl_body[cur_name] = cur_buf
          tmpl_order[++tmpl_order_n] = cur_name
          tmpl_section[cur_name] = 1
        } else {
          exist_body[cur_name] = cur_buf
          exist_order[++exist_order_n] = cur_name
          exist_section[cur_name] = 1
        }
        cur_name = ""
        cur_buf = ""
      }
    }
    FNR == 1 {
      flush_section()
      file_index++
    }
    {
      line = $0
      if (line ~ /^[[:space:]]*\[[^]]+\][[:space:]]*$/) {
        flush_section()
        name = line
        sub(/^[[:space:]]*\[/, "", name)
        sub(/\][[:space:]]*$/, "", name)
        cur_name = name
        cur_buf = line
        next
      }
      if (cur_name != "") {
        cur_buf = cur_buf "\n" line
        next
      }
      if (file_index == 1) {
        tmpl_top[++tmpl_top_n] = line
        if (match(line, /^[[:space:]]*[A-Za-z_][A-Za-z0-9_-]*[[:space:]]*=/)) {
          key = line
          sub(/^[[:space:]]*/, "", key)
          sub(/[[:space:]]*=.*$/, "", key)
          tmpl_top_key[key] = 1
        }
      } else {
        if (match(line, /^[[:space:]]*[A-Za-z_][A-Za-z0-9_-]*[[:space:]]*=/)) {
          key = line
          sub(/^[[:space:]]*/, "", key)
          sub(/[[:space:]]*=.*$/, "", key)
          exist_top_key_order[++exist_key_n] = key
          exist_top_line[key] = line
        }
      }
    }
    END {
      flush_section()

      preserved_key_n = 0
      preserved_keys = ""
      for (i = 1; i <= exist_key_n; i++) {
        k = exist_top_key_order[i]
        if (!(k in tmpl_top_key)) {
          preserved_key_list[++preserved_key_n] = k
          preserved_keys = (preserved_keys == "" ? k : preserved_keys ", " k)
        }
      }

      preserved_section_n = 0
      preserved_sections = ""
      for (i = 1; i <= exist_order_n; i++) {
        n = exist_order[i]
        if (!(n in tmpl_section)) {
          preserved_section_list[++preserved_section_n] = n
          preserved_sections = (preserved_sections == "" ? "[" n "]" : preserved_sections ", [" n "]")
        }
      }

      for (i = 1; i <= tmpl_top_n; i++) {
        print tmpl_top[i]
      }
      if (preserved_key_n > 0) {
        if (tmpl_top_n > 0 && tmpl_top[tmpl_top_n] != "") print ""
        print "# --- preserved top-level keys from previous config.toml ---"
        for (i = 1; i <= preserved_key_n; i++) {
          print exist_top_line[preserved_key_list[i]]
        }
        print ""
      }
      for (i = 1; i <= tmpl_order_n; i++) {
        print tmpl_body[tmpl_order[i]]
      }
      if (preserved_section_n > 0) {
        print ""
        print "# --- preserved sections from previous config.toml ---"
        for (i = 1; i <= preserved_section_n; i++) {
          print exist_body[preserved_section_list[i]]
          print ""
        }
      }

      printf "%d\t%s\n%d\t%s\n", preserved_key_n, preserved_keys, preserved_section_n, preserved_sections > summary_file
    }
  ' "$rendered_tmp" "$target_config" > "$merged_tmp"

  mv "$merged_tmp" "$target_config"
  rm -f "$rendered_tmp"

  if [[ -s "$summary_tmp" ]]; then
    local key_count key_list sec_count sec_list
    {
      IFS=$'\t' read -r key_count key_list
      IFS=$'\t' read -r sec_count sec_list
    } < "$summary_tmp"
    if [[ "${key_count:-0}" -gt 0 ]]; then
      printf 'Preserved %s top-level key(s) from previous config.toml: %s\n' "$key_count" "$key_list"
    fi
    if [[ "${sec_count:-0}" -gt 0 ]]; then
      printf 'Preserved %s section(s) from previous config.toml: %s\n' "$sec_count" "$sec_list"
    fi
  fi
  rm -f "$summary_tmp"
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

check_contains() {
  local path="$1"
  local pattern="$2"
  local label="$3"
  if grep -F "$pattern" "$path" >/dev/null 2>&1; then
    printf '[ok] %s\n' "$label"
  else
    printf '[missing] %s\n' "$label"
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
    printf '[invalid] %s contains legacy backup artifacts that may surface as duplicate entries\n' "$label"
    printf '%s\n' "$conflicts"
    return 1
  fi

  printf '[ok] %s clean\n' "$label"
}

ensure_project_trust() {
  local config_path="$1"
  local project_path="$2"

  if grep -F "[projects.\"${project_path}\"]" "$config_path" >/dev/null 2>&1; then
    printf 'Project trust entry already present: %s\n' "$project_path"
    return 0
  fi

  printf '\n[projects.%s]\ntrust_level = "trusted"\n' "\"${project_path}\"" >> "$config_path"
  printf 'Added trusted project: %s\n' "$project_path"
}

install_agent_files() {
  local source_path
  local target_path=""
  for source_path in "${source_repo_agents}"/*.toml; do
    [[ -f "$source_path" ]] || continue
    target_path="${target_agents_dir}/$(basename "$source_path")"
    backup_path "$target_path"
    install -m 0644 "$source_path" "$target_path"
  done
}

install_skill_dirs() {
  local source_dir
  for source_dir in "${source_repo_skills}"/*; do
    [[ -d "$source_dir" ]] || continue
    local skill_name
    skill_name="$(basename "$source_dir")"
    local target_dir="${user_skills_home}/${skill_name}"
    if [[ -d "$target_dir" ]]; then
      backup_path "$target_dir"
    fi
    mkdir -p "$target_dir"
    cp -R "${source_dir}/." "$target_dir/"
  done
}

run_dynamic_runtime_checks() {
  local status_ref="$1"
  local source_path=""
  local agent_name=""
  local skill_dir=""
  local skill_name=""
  local target_skill=""

  for source_path in "${source_repo_agents}"/*.toml; do
    [[ -f "$source_path" ]] || continue
    agent_name="$(basename "$source_path")"
    check_path "${target_agents_dir}/${agent_name}" "Global agent ${agent_name%.toml}" || printf -v "$status_ref" '1'
    if [[ -f "${target_agents_dir}/${agent_name}" ]]; then
      check_contains "${target_agents_dir}/${agent_name}" "name = \"${agent_name%.toml}\"" "installed ${agent_name%.toml} agent name" || printf -v "$status_ref" '1'
      check_contains "${target_agents_dir}/${agent_name}" 'model = "gpt-5.5"' "installed ${agent_name%.toml} agent model" || printf -v "$status_ref" '1'
      check_contains "${target_agents_dir}/${agent_name}" 'model_reasoning_effort = "high"' "installed ${agent_name%.toml} agent reasoning" || printf -v "$status_ref" '1'
    fi
  done

  for skill_dir in "${source_repo_skills}"/*; do
    [[ -d "$skill_dir" ]] || continue
    skill_name="$(basename "$skill_dir")"
    target_skill="${user_skills_home}/${skill_name}/SKILL.md"
    check_path "$target_skill" "Global skill ${skill_name}" || printf -v "$status_ref" '1'
    if [[ -f "$target_skill" ]]; then
      check_contains "$target_skill" "name: ${skill_name}" "installed ${skill_name} skill metadata" || printf -v "$status_ref" '1'
    fi
  done
}

run_check() {
  local status=0

  check_path "$target_agents" "Global AGENTS" || status=1
  check_path "$target_config" "Global config" || status=1
  check_path "$target_agents_dir" "Global agents dir" || status=1
  check_path "$user_skills_home" "User skills home" || status=1
  check_path "$playwright_output" "Playwright output" || status=1
  check_no_legacy_discovery_conflicts "$target_agents_dir" "Global agents dir" || status=1
  check_no_legacy_discovery_conflicts "$user_skills_home" "User skills home" || status=1
  run_dynamic_runtime_checks status

  if [[ -f "$target_config" ]]; then
    check_contains "$target_config" "[profiles.swiftui]" "config profile swiftui" || status=1
    check_contains "$target_config" "[profiles.web]" "config profile web" || status=1
    check_contains "$target_config" "[profiles.flutter]" "config profile flutter" || status=1
    check_contains "$target_config" "[profiles.review]" "config profile review" || status=1
    if [[ "$trust_project" == true ]]; then
      check_contains "$target_config" "[projects.\"${repo_root}\"]" "trusted project entry" || status=1
    fi
  fi

  if [[ -f "$target_agents" ]]; then
    check_contains "$target_agents" "## Profile intents" "global AGENTS profile guidance" || status=1
    check_contains "$target_agents" "## Global workflow" "global AGENTS workflow guidance" || status=1
  fi

  if [[ "$status" -ne 0 ]]; then
    printf '\nGlobal Codex setup check failed.\n'
    exit "$status"
  fi

  printf '\nGlobal Codex setup check passed.\n'
}

require_file "$source_agents"
require_file "$source_config"
require_dir "$source_repo_agents"
require_dir "$source_repo_skills"

if [[ "$check_only" == true ]]; then
  run_check
  exit 0
fi

mkdir -p "$codex_home" "$user_skills_home" "$playwright_output" "$target_agents_dir"

archive_legacy_discovery_conflicts

backup_path "$target_agents"
backup_path "$target_config"

install -m 0644 "$source_agents" "$target_agents"
render_config_template
chmod 0644 "$target_config"
install_agent_files
install_skill_dirs

if [[ "$trust_project" == true ]]; then
  ensure_project_trust "$target_config" "$repo_root"
fi

printf '\nInstalled global Codex setup to %s\n' "$codex_home"
printf 'Installed global agents to %s\n' "$target_agents_dir"
printf 'Installed user skill root at %s\n' "$user_skills_home"
printf 'Prepared Playwright output directory at %s\n' "$playwright_output"

run_check
