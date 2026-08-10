#!/usr/bin/env bash

set -euo pipefail

minimum_codex_version="0.144.1"
full=false
if (($# > 1)); then
  printf 'Usage: %s [--full]\n' "$0" >&2
  exit 2
fi
if (($# == 1)); then
  [[ "$1" == "--full" ]] || { printf 'Unknown option: %s\n' "$1" >&2; exit 2; }
  full=true
fi

status=0

version_at_least() {
  local actual="$1" required="$2"
  local am an ap rm rn rp
  IFS=. read -r am an ap <<<"$actual"
  IFS=. read -r rm rn rp <<<"$required"
  ((10#$am > 10#$rm)) ||
    ((10#$am == 10#$rm && 10#$an > 10#$rn)) ||
    ((10#$am == 10#$rm && 10#$an == 10#$rn && 10#$ap >= 10#$rp))
}

check_command() {
  local name="$1"
  local path=""
  path="$(command -v "$name" 2>/dev/null || true)"
  if [[ -n "$path" ]]; then
    printf '[ok] %s: %s\n' "$name" "$path"
  else
    printf '[missing] %s\n' "$name"
    status=1
  fi
}

check_codex() {
  local requested="${CODEX_BIN:-codex}"
  local path="" output="" version=""
  if [[ "$requested" == */* ]]; then
    path="$requested"
  else
    path="$(command -v "$requested" 2>/dev/null || true)"
  fi
  if [[ -z "$path" || ! -x "$path" ]]; then
    printf '[missing] Codex executable (requires >= %s): %s\n' "$minimum_codex_version" "$requested"
    status=1
    return
  fi
  if ! output="$("$path" --version 2>&1)"; then
    printf '[invalid] Codex version query failed at %s: %s\n' "$path" "$output"
    status=1
    return
  fi
  version="$(printf '%s\n' "$output" | sed -nE 's/.*[^0-9]([0-9]+\.[0-9]+\.[0-9]+).*/\1/p' | head -n 1)"
  if [[ -z "$version" ]] || ! version_at_least "$version" "$minimum_codex_version"; then
    printf '[invalid] Codex %s at %s; version >= %s required\n' "${version:-unknown}" "$path" "$minimum_codex_version"
    status=1
    return
  fi
  if ! "$path" help doctor >/dev/null 2>&1; then
    printf '[invalid] Codex %s lacks doctor help: %s\n' "$version" "$path"
    status=1
    return
  fi
  printf '[ok] Codex %s: %s\n' "$version" "$path"
}

check_python() {
  local path="" version=""
  path="$(command -v python3 2>/dev/null || true)"
  if [[ -z "$path" ]]; then
    printf '[missing] python3 (requires >= 3.11.0)\n'
    status=1
    return
  fi
  version="$("$path" -c 'import sys; print(".".join(map(str, sys.version_info[:3])))' 2>/dev/null || true)"
  if [[ -z "$version" ]] || ! version_at_least "$version" "3.11.0"; then
    printf '[invalid] Python %s at %s; version >= 3.11.0 required\n' "${version:-unknown}" "$path"
    status=1
    return
  fi
  printf '[ok] Python %s: %s\n' "$version" "$path"
}

check_command git
check_python
check_command bash
check_codex

if [[ "$full" == true ]]; then
  for optional in rg shellcheck actionlint pwsh node npm flutter dart xcodebuild; do
    path="$(command -v "$optional" 2>/dev/null || true)"
    if [[ -n "$path" ]]; then
      printf '[info] optional %s: %s\n' "$optional" "$path"
    else
      printf '[info] optional %s: unavailable\n' "$optional"
    fi
  done
fi

if [[ "$status" -ne 0 ]]; then
  printf '\nCapability diagnostics failed.\n' >&2
  exit 1
fi
printf '\nCapability diagnostics passed.\n'
