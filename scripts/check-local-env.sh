#!/usr/bin/env bash

set -euo pipefail

full_check=false
if [[ "${1:-}" == "--full" ]]; then
  full_check=true
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
      npm) output="$(npm -v 2>&1 || true)" ;;
      pnpm) output="$(pnpm -v 2>&1 || true)" ;;
      swift) output="$(swift --version 2>&1 || true)" ;;
      xcodebuild) output="$(xcodebuild -version 2>&1 || true)" ;;
      flutter) output="$(flutter --version 2>&1 || true)" ;;
      dart) output="$(dart --version 2>&1 || true)" ;;
      git) git --version ;;
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

check_path() {
  local path="$1"
  if [[ -e "$repo_root/$path" ]]; then
    printf '[ok] %s\n' "$path"
  else
    printf '[missing] %s\n' "$path"
    status=1
  fi
}

printf 'Repo root: %s\n' "$repo_root"

for cmd in git node npm pnpm swift xcodebuild flutter dart; do
  check_cmd "$cmd"
done

printf '\nRepo structure:\n'
check_path "AGENTS.md"
check_path "README.md"
check_path ".codex/config.toml"
check_path ".codex/agents"
check_path ".codex/agents/builder.toml"
check_path ".codex/agents/researcher.toml"
check_path ".codex/agents/runtime_platform.toml"
check_path ".codex/agents/workflow_design.toml"
check_path ".codex/agents/workspace_governance.toml"
check_path ".codex/agents/quality_operations.toml"
check_path ".codex/agents/docs_dx.toml"
check_path ".agents/skills"
check_path ".agents/skills/godmode-workflow/SKILL.md"
check_path ".agents/skills/godmode-departments/SKILL.md"
check_path ".agents/skills/greenfield-bootstrap/SKILL.md"
check_path ".agents/skills/web-platforms/SKILL.md"
check_path "docs/blueprint.md"
check_path "docs/global-codex-setup.md"
check_path "docs/local-development.md"
check_path "docs/prompts/dev-start-prompt.md"
check_path "docs/prompts/debug-start-prompt.md"
check_path "docs/prompts/greenfield-start-prompt.md"
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

if [[ "$full_check" == true ]] && command -v flutter >/dev/null 2>&1; then
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
