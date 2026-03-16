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
    printf '[ok] %s: ' "$cmd"
    case "$cmd" in
      node) node -v ;;
      npm) npm -v ;;
      pnpm) pnpm -v ;;
      swift) swift --version | head -n 1 ;;
      xcodebuild) xcodebuild -version | head -n 2 | tr '\n' ' ' ; printf '\n' ;;
      flutter) flutter --version | head -n 1 ;;
      dart) dart --version 2>&1 | head -n 1 ;;
      git) git --version ;;
      *) echo "present" ;;
    esac
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
check_path ".codex/config.toml"
check_path ".codex/agents"
check_path ".agents/skills"
check_path "docs/blueprint.md"
check_path "docs/local-development.md"
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
