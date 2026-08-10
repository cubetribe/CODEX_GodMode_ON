#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
codex_bins=()

usage() {
  printf 'Usage: %s [--codex-bin PATH]...\n' "$0"
}

while (($# > 0)); do
  case "$1" in
    --codex-bin)
      (($# >= 2)) || { usage >&2; exit 2; }
      codex_bins+=("$2")
      shift 2
      ;;
    -h | --help)
      usage
      exit 0
      ;;
    *)
      printf 'Unknown option: %s\n' "$1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if ((${#codex_bins[@]} == 0)); then
  command -v codex >/dev/null 2>&1 && codex_bins+=("$(command -v codex)")
  [[ ! -x /Applications/ChatGPT.app/Contents/Resources/codex ]] || codex_bins+=("/Applications/ChatGPT.app/Contents/Resources/codex")
fi
((${#codex_bins[@]} > 0)) || { printf 'No Codex executable found.\n' >&2; exit 1; }

runtime_root="$(mktemp -d "${TMPDIR:-/tmp}/godmode-isolated-runtime.XXXXXX")"
cleanup() {
  [[ -n "$runtime_root" && -d "$runtime_root" && "$runtime_root" == *godmode-isolated-runtime.* ]] || return 0
  rm -rf "$runtime_root"
}
trap cleanup EXIT

runtime_home="${runtime_root}/home"
codex_home="${runtime_home}/.codex"
skills_home="${runtime_home}/.agents/skills"
mkdir -p "$runtime_home"

HOME="$runtime_home" CODEX_HOME="$codex_home" CODEX_BIN="${codex_bins[0]}" \
  "${repo_root}/scripts/apply-global-codex-setup.sh" \
  --repo "$repo_root" \
  --codex-home "$codex_home" \
  --user-skills-home "$skills_home" \
  --no-trust-project >/dev/null

HOME="$runtime_home" CODEX_HOME="$codex_home" CODEX_BIN="${codex_bins[0]}" \
  "${repo_root}/scripts/apply-global-codex-setup.sh" \
  --repo "$repo_root" \
  --codex-home "$codex_home" \
  --user-skills-home "$skills_home" \
  --no-trust-project --check >/dev/null

active_skills=(
  apple-platforms flutter-dart godmode-debug godmode-prototype godmode-review
  godmode-workflow greenfield-bootstrap release-manager web-platforms
)
retired_skills=(godmode-departments)

prompt_index=0
for codex_bin in "${codex_bins[@]}"; do
  prompt_index=$((prompt_index + 1))
  [[ -x "$codex_bin" ]] || { printf '[fail] Codex executable is not executable: %s\n' "$codex_bin" >&2; exit 1; }
  version="$("$codex_bin" --version 2>&1)"
  prompt_json="${runtime_root}/prompt-${prompt_index}.json"
  # Dollar-prefixed skill names are literal prompt syntax.
  # shellcheck disable=SC2016
  HOME="$runtime_home" CODEX_HOME="$codex_home" "$codex_bin" -C "$repo_root" \
    debug prompt-input 'Use $godmode-workflow for a tiny documentation change.' >"$prompt_json"
  for skill in "${active_skills[@]}"; do
    grep -F -- "- ${skill}:" "$prompt_json" >/dev/null || { printf '[fail] %s did not discover %s\n' "$codex_bin" "$skill" >&2; exit 1; }
  done
  for skill in "${retired_skills[@]}"; do
    if grep -F -- "- ${skill}:" "$prompt_json" >/dev/null; then
      printf '[fail] %s discovered retired skill %s\n' "$codex_bin" "$skill" >&2
      exit 1
    fi
  done
  profile_json="${prompt_json%.json}-profile.json"
  # shellcheck disable=SC2016
  HOME="$runtime_home" CODEX_HOME="$codex_home" "$codex_bin" -p godmode-review -C "$repo_root" \
    debug prompt-input 'Use $godmode-review and keep this read-only.' >"$profile_json"
  grep -F -- 'godmode-review' "$profile_json" >/dev/null || { printf '[fail] review profile discovery failed: %s\n' "$codex_bin" >&2; exit 1; }
  printf '[pass] isolated discovery and profile parse: %s (%s)\n' "$codex_bin" "$version"
done

printf '\nIsolated Codex runtime test passed for %s executable(s).\n' "${#codex_bins[@]}"
