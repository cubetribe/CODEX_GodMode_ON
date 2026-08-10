#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
mode="local"

if (($# > 1)); then
  printf 'Usage: %s [--ci|--full]\n' "$0" >&2
  exit 2
fi
if (($# == 1)); then
  case "$1" in
    --ci) mode="ci" ;;
    --full) mode="full" ;;
    *) printf 'Unknown option: %s\n' "$1" >&2; exit 2 ;;
  esac
fi

"${repo_root}/scripts/check-static.sh"
if [[ "$mode" == "ci" ]]; then
  exit 0
fi
if [[ "$mode" == "full" ]]; then
  exec "${repo_root}/scripts/check-capabilities.sh" --full
fi
exec "${repo_root}/scripts/check-capabilities.sh"
