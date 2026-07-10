#!/usr/bin/env bash

set -euo pipefail

full_check=false
ci_mode=false
minimum_codex_version="0.134.0"

for arg in "$@"; do
  case "$arg" in
    --full) full_check=true ;;
    --ci) ci_mode=true ;;
    *)
      printf 'Unknown argument: %s\n' "$arg" >&2
      exit 2
      ;;
  esac
done

if [[ "${GITHUB_ACTIONS:-}" == "true" ]]; then
  ci_mode=true
fi

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
status=0

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

check_codex_runtime() {
  local requested="${CODEX_BIN:-codex}"
  local resolved=""
  local version_output=""
  local parsed_version=""
  local locations=""
  local location=""
  local location_count=0

  if [[ "$ci_mode" == true ]]; then
    printf '[skip] codex capability preflight (ci mode)\n'
    return
  fi

  if [[ -z "$requested" ]]; then
    printf '[invalid] CODEX_BIN must not be empty\n'
    status=1
    return
  fi
  if [[ "$requested" == */* ]]; then
    if [[ ! -x "$requested" || -d "$requested" ]]; then
      printf '[missing] Codex executable: %s\n' "$requested"
      status=1
      return
    fi
    resolved="$requested"
    printf '[info] CODEX_BIN override: %s\n' "$resolved"
  else
    resolved="$(command -v "$requested" 2>/dev/null || true)"
    if [[ -z "$resolved" ]]; then
      printf '[missing] codex (requires >= %s)\n' "$minimum_codex_version"
      status=1
      return
    fi
    locations="$(type -a "$requested" 2>/dev/null | sed -n "s/^${requested} is //p" | awk '!seen[$0]++')"
    location_count="$(printf '%s\n' "$locations" | awk 'NF { count++ } END { print count + 0 }')"
    if ((location_count > 1)); then
      printf '[warn] shadowed Codex installations; shell resolves %s first:\n' "$resolved"
      while IFS= read -r location; do
        [[ -n "$location" ]] || continue
        version_output="$("$location" --version 2>&1 || true)"
        printf '  - %s (%s)\n' "$location" "${version_output:-version unavailable}"
      done <<<"$locations"
    fi
  fi

  if ! version_output="$("$resolved" --version 2>&1)"; then
    printf '[invalid] Codex version query failed: %s\n' "$resolved"
    status=1
    return
  fi
  parsed_version="$(printf '%s\n' "$version_output" | sed -nE 's/.*[^0-9]([0-9]+\.[0-9]+\.[0-9]+).*/\1/p' | head -n 1)"
  if [[ -z "$parsed_version" ]] || ! version_at_least "$parsed_version" "$minimum_codex_version"; then
    printf '[invalid] Codex %s at %s; version >= %s required\n' "${parsed_version:-unknown}" "$resolved" "$minimum_codex_version"
    status=1
    return
  fi
  if ! "$resolved" help doctor >/dev/null 2>&1; then
    printf '[invalid] Codex %s lacks the doctor help capability: %s\n' "$parsed_version" "$resolved"
    status=1
    return
  fi
  printf '[ok] codex: %s (%s), doctor capability present\n' "$resolved" "$parsed_version"
}

check_cmd() {
  local cmd="$1"
  if command -v "$cmd" >/dev/null 2>&1; then
    local output=""
    printf '[ok] %s: ' "$cmd"
    case "$cmd" in
      node) output="$(node -v 2>&1 || true)" ;;
      python3) output="$(python3 --version 2>&1 || true)" ;;
      npm) output="$(npm -v 2>&1 || true)" ;;
      pnpm) output="$(pnpm -v 2>&1 || true)" ;;
      swift) output="$(swift --version 2>&1 || true)" ;;
      xcodebuild) output="$(xcodebuild -version 2>&1 || true)" ;;
      flutter) output="$(flutter --version 2>&1 || true)" ;;
      dart) output="$(dart --version 2>&1 || true)" ;;
      git) output="$(git --version 2>&1 || true)" ;;
      *) echo "present" ;;
    esac

    if [[ "$cmd" == "xcodebuild" && -n "$output" ]]; then
      printf '%s\n' "$output" | sed -n '1,2p' | tr '\n' ' '
      printf '\n'
    elif [[ -n "$output" ]]; then
      printf '%s\n' "$output" | sed -n '1p'
    fi
  else
    printf '[missing] %s\n' "$cmd"
    status=1
  fi
}

skip_cmd() {
  local cmd="$1"
  printf '[skip] %s (ci mode)\n' "$cmd"
}

check_path() {
  local path="$1"
  if [[ -e "$repo_root/$path" ]]; then
    printf '[ok] %s\n' "$path"
  else
    printf '[missing] %s\n' "$path"
    status=1
  fi
}

check_absent() {
  local path="$1"
  if [[ -e "$repo_root/$path" ]]; then
    printf '[unexpected] %s\n' "$path"
    status=1
  else
    printf '[ok] absent %s\n' "$path"
  fi
}

check_agent_contracts() {
  if ! command -v python3 >/dev/null 2>&1; then
    printf '[missing] python3 (required for TOML validation)\n'
    status=1
    return
  fi

  for file in "$repo_root"/templates/global-codex/agents/*.toml; do
    local output=""
    if output="$(python3 - "$file" 2>&1 <<'PY'
import os
import sys

try:
    import tomllib
except ModuleNotFoundError:
    try:
        import tomli as tomllib
    except ModuleNotFoundError:
        print("python3 requires tomllib or tomli for TOML validation")
        sys.exit(2)

path = sys.argv[1]
with open(path, "rb") as handle:
    data = tomllib.load(handle)

required = [
    "name",
    "description",
    "sandbox_mode",
    "developer_instructions",
]
missing = [key for key in required if not data.get(key)]
if missing:
    print("missing required fields: " + ", ".join(missing))
    sys.exit(1)

expected = os.path.splitext(os.path.basename(path))[0]
if data["name"] != expected:
    print(f"name field '{data['name']}' does not match filename '{expected}'")
    sys.exit(1)

for forbidden in ("model", "model_reasoning_effort"):
    if forbidden in data:
        print(f"{forbidden} must be omitted so the agent inherits the parent session")
        sys.exit(1)
PY
    )"; then
      printf '[ok] %s\n' "${file#"$repo_root"/}"
    else
      printf '[invalid] %s: %s\n' "${file#"$repo_root"/}" "$output"
      status=1
    fi
  done
}

check_toml_config() {
  local path="$1"
  local output=""

  if output="$(python3 - "$repo_root/$path" 2>&1 <<'PY'
import sys

try:
    import tomllib
except ModuleNotFoundError:
    try:
        import tomli as tomllib
    except ModuleNotFoundError:
        print("python3 requires tomllib or tomli for TOML validation")
        sys.exit(2)

with open(sys.argv[1], "rb") as handle:
    data = tomllib.load(handle)

for forbidden in ("model", "model_reasoning_effort", "plan_mode_reasoning_effort"):
    if forbidden in data:
        print(f"{forbidden} must be omitted so the parent session selection is inherited")
        sys.exit(1)

if "profiles" in data:
    print("inline [profiles.*] tables are unsupported; use separate NAME.config.toml files")
    sys.exit(1)

agents = data.get("agents", {})
expected_threads = 2 if sys.argv[1].endswith("templates/prototype-mode/config.toml") else 6
if agents.get("max_threads") != expected_threads or agents.get("max_depth") != 1:
    print(
        f"agents must set max_threads={expected_threads} and max_depth=1, "
        f"found {agents!r}"
    )
    sys.exit(1)
PY
  )"; then
    printf '[ok] %s\n' "$path"
  else
    printf '[invalid] %s: %s\n' "$path" "$output"
    status=1
  fi
}

check_profile_config() {
  local path="$1"
  local output=""

  if output="$(python3 - "$repo_root/$path" 2>&1 <<'PY'
import os
import sys

try:
    import tomllib
except ModuleNotFoundError:
    try:
        import tomli as tomllib
    except ModuleNotFoundError:
        print("python3 requires tomllib or tomli for TOML validation")
        sys.exit(2)

with open(sys.argv[1], "rb") as handle:
    data = tomllib.load(handle)

for forbidden in (
    "model",
    "model_reasoning_effort",
    "plan_mode_reasoning_effort",
    "profiles",
    "agents",
):
    if forbidden in data:
        print(f"{forbidden} is not allowed in a managed GodMode profile")
        sys.exit(1)

expected = {
    "godmode-swiftui.config.toml": {"web_search": "cached"},
    "godmode-web.config.toml": {"web_search": "live"},
    "godmode-flutter.config.toml": {"web_search": "cached"},
    "godmode-review.config.toml": {
        "model_reasoning_summary": "concise",
        "model_verbosity": "low",
        "web_search": "cached",
    },
}
name = os.path.basename(sys.argv[1])
if name not in expected:
    print(f"unexpected managed profile name: {name}")
    sys.exit(1)
if data != expected[name]:
    print(f"profile keys differ from the managed contract: {data!r}")
    sys.exit(1)
PY
  )"; then
    printf '[ok] %s\n' "$path"
  else
    printf '[invalid] %s: %s\n' "$path" "$output"
    status=1
  fi
}

check_skill_frontmatter() {
  for file in "$repo_root"/templates/global-codex/skills/*/SKILL.md; do
    if awk '
      BEGIN { in_frontmatter = 0; end_frontmatter = 0; has_name = 0; has_description = 0 }
      NR == 1 {
        if ($0 != "---") {
          exit 1
        }
        in_frontmatter = 1
        next
      }
      in_frontmatter && $0 == "---" {
        end_frontmatter = 1
        exit ! (has_name && has_description)
      }
      in_frontmatter && $0 ~ /^name:[[:space:]]*[^[:space:]].*$/ { has_name = 1 }
      in_frontmatter && $0 ~ /^description:[[:space:]]*[^[:space:]].*$/ { has_description = 1 }
      END {
        if (!end_frontmatter) {
          exit 1
        }
      }
    ' "$file"; then
      printf '[ok] %s\n' "${file#"$repo_root"/}"
    else
      printf '[invalid] %s: missing name/description frontmatter\n' "${file#"$repo_root"/}"
      status=1
    fi
  done
}

check_skill_openai_yaml() {
  local path="templates/global-codex/skills/godmode-workflow/agents/openai.yaml"
  local output=""

  if output="$(python3 - "$repo_root/$path" 2>&1 <<'PY'
import re
import sys

path = sys.argv[1]
with open(path, encoding="utf-8") as handle:
    lines = [line.rstrip("\n") for line in handle]

if not lines or lines[0] != "interface:":
    print("top-level interface mapping is required")
    sys.exit(1)

values = {}
pattern = re.compile(r'^  ([a-z_]+): "([^"\\]*(?:\\.[^"\\]*)*)"$')
for line in lines[1:]:
    if not line.strip():
        continue
    match = pattern.fullmatch(line)
    if not match:
        print(f"invalid or unquoted interface line: {line!r}")
        sys.exit(1)
    values[match.group(1)] = match.group(2)

expected_keys = {"display_name", "short_description", "default_prompt"}
if set(values) != expected_keys:
    print(f"expected only {sorted(expected_keys)}, found {sorted(values)}")
    sys.exit(1)
if not values["display_name"]:
    print("display_name must not be empty")
    sys.exit(1)
length = len(values["short_description"])
if not 25 <= length <= 64:
    print(f"short_description must be 25-64 characters, found {length}")
    sys.exit(1)
if "$godmode-workflow" not in values["default_prompt"]:
    print("default_prompt must explicitly mention $godmode-workflow")
    sys.exit(1)
PY
  )"; then
    printf '[ok] %s\n' "$path"
  else
    printf '[invalid] %s: %s\n' "$path" "$output"
    status=1
  fi
}

check_installer_regressions() {
  local output=""
  local groups=""
  if output="$("$repo_root/scripts/test-global-codex-setup.sh" 2>&1)"; then
    groups="$(printf '%s\n' "$output" | sed -nE 's/^All ([0-9]+) global Codex installer regression groups passed\.$/\1/p' | tail -n 1)"
    printf '[ok] scripts/test-global-codex-setup.sh (%s regression groups)\n' "${groups:-unknown}"
  else
    printf '[invalid] scripts/test-global-codex-setup.sh:\n%s\n' "$output"
    status=1
  fi
}

check_unreleased_when_dirty() {
  local dirty=false
  local unreleased_has_entry=false
  local latest_release_has_entry=false
  local current_version=""

  if git -C "$repo_root" status --short --untracked-files=normal | grep -q .; then
    dirty=true
  fi

  if awk '
    /^## \[Unreleased\]$/ { in_unreleased = 1; next }
    in_unreleased && /^## \[/ { exit }
    in_unreleased && /^- / { found = 1 }
    END { exit(found ? 0 : 1) }
  ' "$repo_root/CHANGELOG.md"; then
    unreleased_has_entry=true
  fi

  current_version="$(tr -d '[:space:]' < "$repo_root/VERSION")"
  if awk -v version="$current_version" '
    $0 == "## [" version "]" || $0 ~ ("^## \\[" version "\\] - ") { in_release = 1; next }
    in_release && /^## \[/ { exit }
    in_release && /^- / { found = 1 }
    END { exit(found ? 0 : 1) }
  ' "$repo_root/CHANGELOG.md"; then
    latest_release_has_entry=true
  fi

  if [[ "$dirty" == true && "$unreleased_has_entry" != true && "$latest_release_has_entry" != true ]]; then
    printf '[invalid] CHANGELOG.md: dirty work must have bullets under [Unreleased] or the current VERSION release section\n'
    status=1
    return
  fi

  printf '[ok] CHANGELOG.md unreleased policy\n'
}

check_version_alignment() {
  local latest_version=""
  local current_version=""

  latest_version="$(
    awk '
      /^## \[Unreleased\]$/ { seen_unreleased = 1; next }
      seen_unreleased && /^## \[/ {
        line = $0
        sub(/^## \[/, "", line)
        sub(/\].*$/, "", line)
        print line
        exit
      }
    ' "$repo_root/CHANGELOG.md"
  )"

  current_version="$(tr -d '[:space:]' < "$repo_root/VERSION")"

  if [[ -z "$latest_version" ]]; then
    printf '[invalid] CHANGELOG.md: could not determine latest released version heading\n'
    status=1
  elif [[ "$current_version" != "$latest_version" ]]; then
    printf '[invalid] VERSION: expected %s but found %s\n' "$latest_version" "$current_version"
    status=1
  else
    printf '[ok] VERSION matches CHANGELOG.md (%s)\n' "$current_version"
  fi
}

check_shell_syntax() {
  while IFS= read -r file; do
    if bash -n "$file"; then
      printf '[ok] %s\n' "${file#"$repo_root"/}"
    else
      printf '[invalid] %s: bash -n failed\n' "${file#"$repo_root"/}"
      status=1
    fi
  done < <(find "$repo_root" -type f -name '*.sh' | sort)
}

check_workflow_security() {
  local grep_cmd="grep"
  local grep_has_rg=false

  if command -v rg >/dev/null 2>&1; then
    grep_cmd="rg"
    grep_has_rg=true
  fi

  while IFS= read -r file; do
    local relative="${file#"$repo_root"/}"

    if [[ "$grep_has_rg" == true ]]; then
      if $grep_cmd -n '^[[:space:]]*pull_request_target:' "$file" >/dev/null; then
        printf '[invalid] %s: pull_request_target is not allowed in this repo\n' "$relative"
        status=1
      else
        printf '[ok] %s: no pull_request_target trigger\n' "$relative"
      fi
    else
      if $grep_cmd -Eq '^[[:space:]]*pull_request_target:' "$file"; then
        printf '[invalid] %s: pull_request_target is not allowed in this repo\n' "$relative"
        status=1
      else
        printf '[ok] %s: no pull_request_target trigger\n' "$relative"
      fi
    fi

    if [[ "$grep_has_rg" == true ]]; then
      if $grep_cmd -q '^[[:space:]]*permissions:' "$file"; then
        printf '[ok] %s: explicit permissions block\n' "$relative"
      else
        printf '[invalid] %s: missing explicit permissions block\n' "$relative"
        status=1
      fi
    else
      if $grep_cmd -Eq '^[[:space:]]*permissions:' "$file"; then
        printf '[ok] %s: explicit permissions block\n' "$relative"
      else
        printf '[invalid] %s: missing explicit permissions block\n' "$relative"
        status=1
      fi
    fi

    while IFS= read -r line; do
      local ref=""
      ref="$(printf '%s\n' "$line" | sed -E 's/^[[:space:]]*uses:[[:space:]]*([^[:space:]#]+).*/\1/')"

      if [[ "$ref" == ./* ]] || [[ "$ref" == docker://* ]]; then
        continue
      fi

      if [[ "$ref" =~ @[0-9a-f]{40}$ ]]; then
        continue
      fi

      printf '[invalid] %s: action must be pinned to a full commit SHA (%s)\n' "$relative" "$ref"
      status=1
    done < <(
      if [[ "$grep_has_rg" == true ]]; then
        $grep_cmd '^[[:space:]]*uses:[[:space:]]*' "$file"
      else
        $grep_cmd -E '^[[:space:]]*uses:[[:space:]]*' "$file" || true
      fi
    )
  done < <(find "$repo_root/.github/workflows" -type f \( -name '*.yml' -o -name '*.yaml' \) | sort)
}

printf 'Repo root: %s\n' "$repo_root"
printf 'Mode: %s\n' "$([[ "$ci_mode" == true ]] && echo ci || echo local)"

printf '\nTooling:\n'
check_cmd git
check_cmd python3
check_codex_runtime
if [[ "$ci_mode" == true ]]; then
  for cmd in node npm pnpm swift xcodebuild flutter dart; do
    skip_cmd "$cmd"
  done
else
  for cmd in node npm pnpm swift xcodebuild flutter dart; do
    check_cmd "$cmd"
  done
fi

printf '\nRepo structure:\n'
check_path "AGENTS.md"
check_path "README.md"
check_path ".codex/config.toml"
check_path "templates/global-codex/agents"
check_path "templates/global-codex/agents/api_guardian.toml"
check_path "templates/global-codex/agents/architect.toml"
check_path "templates/global-codex/agents/builder.toml"
check_path "templates/global-codex/agents/ci_security_guardian.toml"
check_path "templates/global-codex/agents/github_manager.toml"
check_path "templates/global-codex/agents/researcher.toml"
check_path "templates/global-codex/agents/scribe.toml"
check_path "templates/global-codex/agents/tester.toml"
check_path "templates/global-codex/agents/validator.toml"
check_path "templates/global-codex/agents/runtime_platform.toml"
check_path "templates/global-codex/agents/workflow_design.toml"
check_path "templates/global-codex/agents/workspace_governance.toml"
check_path "templates/global-codex/agents/quality_operations.toml"
check_path "templates/global-codex/agents/docs_dx.toml"
check_path "templates/global-codex/profiles"
check_path "templates/global-codex/profiles/godmode-swiftui.config.toml"
check_path "templates/global-codex/profiles/godmode-web.config.toml"
check_path "templates/global-codex/profiles/godmode-flutter.config.toml"
check_path "templates/global-codex/profiles/godmode-review.config.toml"
check_path "templates/global-codex/skills"
check_path "templates/global-codex/skills/godmode-workflow/SKILL.md"
check_path "templates/global-codex/skills/godmode-workflow/agents/openai.yaml"
check_path "templates/global-codex/skills/godmode-prototype/SKILL.md"
check_path "templates/global-codex/skills/godmode-departments/SKILL.md"
check_path "templates/global-codex/skills/godmode-debug/SKILL.md"
check_path "templates/global-codex/skills/godmode-review/SKILL.md"
check_path "templates/global-codex/skills/greenfield-bootstrap/SKILL.md"
check_path "templates/global-codex/skills/apple-platforms/SKILL.md"
check_path "templates/global-codex/skills/flutter-dart/SKILL.md"
check_path "templates/global-codex/skills/release-manager/SKILL.md"
check_path "templates/global-codex/skills/web-platforms/SKILL.md"
check_absent ".codex/agents"
check_absent ".agents/skills"
check_path ".github/CODEOWNERS"
check_path ".github/dependabot.yml"
check_path ".github/workflows/ci.yml"
check_path ".github/workflows/codeql.yml"
check_path "docs/blueprint.md"
check_path "docs/agent-registry.md"
check_path "docs/department-orchestration.md"
check_path "docs/prototype-mode.md"
check_path "docs/global-codex-setup.md"
check_path "docs/local-development.md"
check_path "docs/prompts/dev-start-prompt.md"
check_path "docs/prompts/debug-start-prompt.md"
check_path "docs/prompts/greenfield-start-prompt.md"
check_path "docs/prompts/improvement-sprint-prompt.md"
check_path "docs/prompts/prototype-start-prompt.md"
check_path "docs/prompts/review-start-prompt.md"
check_path "docs/prompts/web-start-prompt.md"
check_path "docs/prompts/apple-start-prompt.md"
check_path "docs/prompts/flutter-start-prompt.md"
check_path "templates/global-codex/AGENTS.md"
check_path "templates/global-codex/config.toml"
check_path "templates/project-bootstrap/AGENTS.md"
check_path "templates/prototype-mode/AGENTS.md"
check_path "templates/prototype-mode/config.toml"
check_path "scripts/apply-global-codex-setup.sh"
check_path "scripts/apply-global-codex-setup.ps1"
check_path "scripts/check-local-env.sh"
check_path "scripts/test-global-codex-setup.sh"
check_path "scripts/test-global-codex-setup.ps1"
check_path "reports"
check_path "reports/README.md"
check_path "reports/templates/role-report.md"
check_path "state"
check_path "state/README.md"
check_path "state/templates/workflow-state.local.json"

printf '\nRepo validation:\n'
check_agent_contracts
check_toml_config ".codex/config.toml"
check_toml_config "templates/global-codex/config.toml"
check_toml_config "templates/prototype-mode/config.toml"
check_profile_config "templates/global-codex/profiles/godmode-swiftui.config.toml"
check_profile_config "templates/global-codex/profiles/godmode-web.config.toml"
check_profile_config "templates/global-codex/profiles/godmode-flutter.config.toml"
check_profile_config "templates/global-codex/profiles/godmode-review.config.toml"
check_skill_frontmatter
check_skill_openai_yaml
check_unreleased_when_dirty
check_version_alignment
check_shell_syntax
check_installer_regressions
check_workflow_security

if [[ "$full_check" == true ]] && [[ "$ci_mode" != true ]] && command -v flutter >/dev/null 2>&1; then
  printf '\nFlutter doctor:\n'
  if ! flutter doctor -v; then
    status=1
  fi
fi

if [[ "$status" -ne 0 ]]; then
  printf '\nLocal environment check failed.\n'
  exit "$status"
fi

printf '\nLocal environment check passed.\n'
