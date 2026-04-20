#!/usr/bin/env bash

set -euo pipefail

full_check=false
ci_mode=false

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

check_agent_contracts() {
  if ! command -v python3 >/dev/null 2>&1; then
    printf '[missing] python3 (required for TOML validation)\n'
    status=1
    return
  fi

  for file in "$repo_root"/.codex/agents/*.toml; do
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

required = ["name", "description", "sandbox_mode", "developer_instructions"]
missing = [key for key in required if not data.get(key)]
if missing:
    print("missing required fields: " + ", ".join(missing))
    sys.exit(1)

expected = os.path.splitext(os.path.basename(path))[0]
if data["name"] != expected:
    print(f"name field '{data['name']}' does not match filename '{expected}'")
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

check_skill_frontmatter() {
  for file in "$repo_root"/.agents/skills/*/SKILL.md; do
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

check_unreleased_when_dirty() {
  local dirty=false
  local unreleased_has_entry=false

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

  if [[ "$dirty" == true && "$unreleased_has_entry" != true ]]; then
    printf '[invalid] CHANGELOG.md: [Unreleased] must contain at least one bullet when the worktree is dirty\n'
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
check_path ".codex/agents"
check_path ".codex/agents/builder.toml"
check_path ".codex/agents/ci_security_guardian.toml"
check_path ".codex/agents/researcher.toml"
check_path ".codex/agents/runtime_platform.toml"
check_path ".codex/agents/workflow_design.toml"
check_path ".codex/agents/workspace_governance.toml"
check_path ".codex/agents/quality_operations.toml"
check_path ".codex/agents/docs_dx.toml"
check_path ".agents/skills"
check_path ".agents/skills/godmode-workflow/SKILL.md"
check_path ".agents/skills/godmode-departments/SKILL.md"
check_path ".agents/skills/godmode-debug/SKILL.md"
check_path ".agents/skills/godmode-review/SKILL.md"
check_path ".agents/skills/greenfield-bootstrap/SKILL.md"
check_path ".agents/skills/web-platforms/SKILL.md"
check_path ".github/CODEOWNERS"
check_path ".github/dependabot.yml"
check_path ".github/workflows/ci.yml"
check_path ".github/workflows/codeql.yml"
check_path "docs/blueprint.md"
check_path "docs/global-codex-setup.md"
check_path "docs/local-development.md"
check_path "docs/prompts/dev-start-prompt.md"
check_path "docs/prompts/debug-start-prompt.md"
check_path "docs/prompts/greenfield-start-prompt.md"
check_path "docs/prompts/improvement-sprint-prompt.md"
check_path "docs/prompts/review-start-prompt.md"
check_path "docs/prompts/web-start-prompt.md"
check_path "docs/prompts/apple-start-prompt.md"
check_path "docs/prompts/flutter-start-prompt.md"
check_path "templates/global-codex/AGENTS.md"
check_path "templates/global-codex/config.toml"
check_path "templates/project-bootstrap/AGENTS.md"
check_path "scripts/apply-global-codex-setup.sh"
check_path "scripts/check-local-env.sh"
check_path "reports"
check_path "state"

printf '\nRepo validation:\n'
check_agent_contracts
check_skill_frontmatter
check_unreleased_when_dirty
check_version_alignment
check_shell_syntax
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
