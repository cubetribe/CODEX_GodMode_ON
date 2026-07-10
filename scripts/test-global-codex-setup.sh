#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
installer="${repo_root}/scripts/apply-global-codex-setup.sh"
source_agents="${repo_root}/templates/global-codex/AGENTS.md"
source_profiles="${repo_root}/templates/global-codex/profiles"
temp_root="$(mktemp -d "${TMPDIR:-/tmp}/godmode-installer-tests.XXXXXX")"
fake_codex="${temp_root}/bin/codex"
fake_date="${temp_root}/bin/date"
test_count=0

cleanup() {
  rm -rf "$temp_root"
}
trap cleanup EXIT

fail_test() {
  printf '[FAIL] %s\n' "$1" >&2
  exit 1
}

pass_test() {
  test_count=$((test_count + 1))
  printf '[PASS] %s\n' "$1"
}

assert_file() {
  [[ -f "$1" ]] || fail_test "expected file: $1"
}

assert_absent() {
  [[ ! -e "$1" ]] || fail_test "expected path to be absent: $1"
}

assert_contains() {
  grep -F -- "$2" "$1" >/dev/null 2>&1 || fail_test "expected '$2' in $1"
}

assert_not_contains() {
  if grep -F -- "$2" "$1" >/dev/null 2>&1; then
    fail_test "did not expect '$2' in $1"
  fi
}

sha256_file() {
  if command -v shasum >/dev/null 2>&1; then
    shasum -a 256 "$1" | awk '{print $1}'
  elif command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$1" | awk '{print $1}'
  else
    fail_test "shasum or sha256sum is required"
  fi
}

expect_status() {
  local expected="$1"
  shift
  local actual=0
  set +e
  "$@" >"${temp_root}/last-command.log" 2>&1
  actual=$?
  set -e
  if [[ "$actual" -ne "$expected" ]]; then
    printf '%s\n' "--- command output ---" >&2
    sed -n '1,240p' "${temp_root}/last-command.log" >&2
    fail_test "expected exit ${expected}, got ${actual}: $*"
  fi
}

new_case() {
  local name="$1"
  case_root="${temp_root}/${name}"
  case_home="${case_root}/codex-home"
  case_skills="${case_root}/user-skills"
  mkdir -p "$case_root"
}

run_installer() {
  PATH="$(dirname "$fake_codex"):$PATH" CODEX_BIN="$fake_codex" "$installer" \
    --repo "$repo_root" \
    --codex-home "$case_home" \
    --user-skills-home "$case_skills" \
    "$@"
}

write_unmarked_v1_1_agents() {
  local output="$1"
  # The backticks below are literal Markdown delimiters, not shell expansion.
  # shellcheck disable=SC2016
  sed \
    -e '/CODEX_GODMODE_GLOBAL_AGENTS:BEGIN/d' \
    -e '/CODEX_GODMODE_GLOBAL_AGENTS:END/d' \
    -e '/Use bounded proactive subagents/d' \
    -e '/Parallelize independent read-only discovery/d' \
    -e '/Let custom agents inherit the parent session/d' \
    -e 's/^- `godmode-swiftui`:/- `swiftui`:/' \
    -e 's/^- `godmode-web`:/- `web`:/' \
    -e 's/^- `godmode-flutter`:/- `flutter`:/' \
    -e 's/^- `godmode-review`:/- `review`:/' \
    "$source_agents" >"$output"
}

managed_manifest() {
  local home="$1"
  local skills="$2"
  (
    cd "$home"
    find AGENTS.md config.toml agents playwright-output \
      -type f -exec cksum {} \; 2>/dev/null | sort
    find . -maxdepth 1 -type f -name 'godmode-*.config.toml' \
      -exec cksum {} \; | sort
  )
  (
    cd "$skills"
    find . -type f -exec cksum {} \; | sort
  )
}

mkdir -p "$(dirname "$fake_codex")"
cat >"$fake_codex" <<'EOF'
#!/usr/bin/env bash
if [[ "${1:-}" == "--version" ]]; then
  printf '%s\n' "codex-cli 0.144.1"
  exit 0
fi
if [[ "${1:-}" == "help" && "${2:-}" == "doctor" ]]; then
  exit 0
fi
exit 1
EOF
chmod +x "$fake_codex"

cat >"$fake_date" <<'EOF'
#!/usr/bin/env bash
printf '%s\n' '2026-07-10T12-00-00'
EOF
chmod +x "$fake_date"

# Clean install and exact installed check.
new_case clean
run_installer >/dev/null
assert_file "$case_home/config.toml"
assert_file "$case_home/AGENTS.md"
assert_file "$case_home/godmode-swiftui.config.toml"
assert_file "$case_skills/godmode-workflow/agents/openai.yaml"
assert_contains "$case_home/config.toml" "[projects.\"${repo_root}\"]"
assert_not_contains "$case_home/config.toml" 'model = '
assert_not_contains "$case_home/config.toml" 'model_reasoning_effort = '
run_installer --check >/dev/null
pass_test "clean install and exact check"

# Existing config stays byte-for-byte identical, including TOML forms that a
# line-oriented merger would corrupt.
new_case preserve-config
mkdir -p "$case_home"
cat >"$case_home/config.toml" <<'EOF'
"quoted.root" = "keep = exact"
dotted.root = "also exact"
message = """
first line
[not.a.section]
last line
"""

[custom]
value = "untouched"
EOF
cp "$case_home/config.toml" "$case_root/config.before"
run_installer >/dev/null 2>&1
cmp -s "$case_root/config.before" "$case_home/config.toml" || fail_test "existing config changed"
run_installer --check >/dev/null 2>&1
pass_test "existing config byte preservation"

# A conflicting managed profile blocks all writes until explicit reset.
new_case profile-conflict
mkdir -p "$case_home"
printf '%s\n' '# user-modified managed profile' >"$case_home/godmode-web.config.toml"
expect_status 4 run_installer
assert_absent "$case_home/AGENTS.md"
assert_absent "$case_home/config.toml"
assert_absent "$case_skills"
run_installer --reset-config >/dev/null
cmp -s "$source_profiles/godmode-web.config.toml" "$case_home/godmode-web.config.toml" || fail_test "profile reset did not install exact source"
find "$case_home/backups/install-archives" -type f -path '*/profiles/godmode-web.config.toml' | grep -q . || fail_test "profile reset backup missing"
pass_test "managed profile conflict and reset"

# Separate reset processes must never overwrite one another's backups, even
# when their wall-clock timestamps share the same second.
new_case unique-backups
run_installer >/dev/null
printf '%s\n' 'custom_reset = "first"' >"$case_home/config.toml"
run_installer --reset-config >/dev/null
printf '%s\n' 'custom_reset = "second"' >"$case_home/config.toml"
run_installer --reset-config >/dev/null
backup_count="$(find "$case_home/backups/install-archives" -type f -path '*/root/config.toml' | wc -l | tr -d ' ')"
[[ "$backup_count" -ge 2 ]] || fail_test "reset runs reused one backup target"
pass_test "unique backup archives"

# The exact unmarked v1.1 guidance migrates to one managed block without being
# duplicated under Preserved User Guidance.
new_case agents-v1-1
mkdir -p "$case_home"
write_unmarked_v1_1_agents "$case_home/AGENTS.md"
legacy_digest="$(sha256_file "$case_home/AGENTS.md")"
[[ "$legacy_digest" == 'b660e0f29ea87e1817b702c5a52d960fe7230f807ec8adb927c18f14ed101451' ]] || fail_test "v1.1 fixture digest changed: $legacy_digest"
run_installer >/dev/null
cmp -s "$source_agents" "$case_home/AGENTS.md" || fail_test "v1.1 AGENTS did not migrate exactly"
assert_not_contains "$case_home/AGENTS.md" '## Preserved User Guidance'
pass_test "unmarked v1.1 AGENTS migration"

# The same known v1.1 guidance may come from a Windows checkout with CRLF.
new_case agents-v1-1-crlf
mkdir -p "$case_home"
write_unmarked_v1_1_agents "$case_root/AGENTS.lf"
awk '{ printf "%s\r\n", $0 }' "$case_root/AGENTS.lf" >"$case_home/AGENTS.md"
run_installer >/dev/null
cmp -s "$source_agents" "$case_home/AGENTS.md" || fail_test "CRLF v1.1 AGENTS did not migrate exactly"
assert_not_contains "$case_home/AGENTS.md" '## Preserved User Guidance'
pass_test "CRLF v1.1 AGENTS migration"

# Genuinely custom unmarked guidance is retained once and remains stable.
new_case custom-agents
mkdir -p "$case_home"
printf '%s\n' '# My custom global rule' '' '- Keep this exact guidance.' >"$case_home/AGENTS.md"
run_installer >/dev/null
assert_contains "$case_home/AGENTS.md" '## Preserved User Guidance'
assert_contains "$case_home/AGENTS.md" '- Keep this exact guidance.'
custom_count="$(grep -Fc -- '- Keep this exact guidance.' "$case_home/AGENTS.md")"
[[ "$custom_count" -eq 1 ]] || fail_test "custom AGENTS guidance was duplicated"
run_installer >/dev/null
custom_count="$(grep -Fc -- '- Keep this exact guidance.' "$case_home/AGENTS.md")"
[[ "$custom_count" -eq 1 ]] || fail_test "custom AGENTS guidance was duplicated on reinstall"
pass_test "custom AGENTS preservation"

# Marker text inside a user sentence is not a managed marker line and must not
# change the validated block boundaries.
new_case inline-marker-guidance
run_installer >/dev/null
cp "$case_home/AGENTS.md" "$case_root/managed.before"
{
  printf '%s\n' 'Do not type <!-- CODEX_GODMODE_GLOBAL_AGENTS:BEGIN --> manually.'
  cat "$case_root/managed.before"
} >"$case_home/AGENTS.md"
run_installer >/dev/null
first_line="$(sed -n '1p' "$case_home/AGENTS.md")"
[[ "$first_line" == 'Do not type <!-- CODEX_GODMODE_GLOBAL_AGENTS:BEGIN --> manually.' ]] || fail_test "inline marker guidance was changed"
assert_contains "$case_home/AGENTS.md" '# ~/.codex/AGENTS.md'
pass_test "inline marker guidance preservation"

# Duplicate, orphaned, and reversed marker pairs are rejected before writes.
for malformed in duplicate orphan reversed; do
  new_case "markers-${malformed}"
  mkdir -p "$case_home"
  case "$malformed" in
    duplicate)
      printf '%s\n' \
        '<!-- CODEX_GODMODE_GLOBAL_AGENTS:BEGIN -->' \
        '<!-- CODEX_GODMODE_GLOBAL_AGENTS:BEGIN -->' \
        '<!-- CODEX_GODMODE_GLOBAL_AGENTS:END -->' >"$case_home/AGENTS.md"
      ;;
    orphan)
      printf '%s\n' '<!-- CODEX_GODMODE_GLOBAL_AGENTS:END -->' >"$case_home/AGENTS.md"
      ;;
    reversed)
      printf '%s\n' \
        '<!-- CODEX_GODMODE_GLOBAL_AGENTS:END -->' \
        '<!-- CODEX_GODMODE_GLOBAL_AGENTS:BEGIN -->' >"$case_home/AGENTS.md"
      ;;
  esac
  expect_status 1 run_installer
  assert_absent "$case_home/config.toml"
  assert_absent "$case_home/agents"
  assert_absent "$case_skills"
done
pass_test "malformed AGENTS marker rejection"

# Exact checks detect both file drift and stale files inside owned skill dirs;
# a normal apply replaces those managed assets without touching unrelated ones.
new_case exact-drift
run_installer >/dev/null
printf '%s\n' '# drift' >>"$case_home/agents/researcher.toml"
printf '%s\n' 'stale' >"$case_skills/godmode-workflow/stale.txt"
mkdir -p "$case_home/agents" "$case_skills/custom-skill"
printf '%s\n' 'name = "custom"' >"$case_home/agents/custom.toml"
printf '%s\n' 'custom' >"$case_skills/custom-skill/keep.txt"
expect_status 1 run_installer --check
run_installer >/dev/null
cmp -s "$repo_root/templates/global-codex/agents/researcher.toml" "$case_home/agents/researcher.toml" || fail_test "agent drift was not repaired"
assert_absent "$case_skills/godmode-workflow/stale.txt"
assert_file "$case_home/agents/custom.toml"
assert_file "$case_skills/custom-skill/keep.txt"
run_installer --check >/dev/null
pass_test "exact drift detection and managed replacement"

# Two identical applies produce the same managed runtime bytes.
new_case idempotence
run_installer >/dev/null
managed_manifest "$case_home" "$case_skills" >"$case_root/manifest.before"
run_installer >/dev/null
managed_manifest "$case_home" "$case_skills" >"$case_root/manifest.after"
cmp -s "$case_root/manifest.before" "$case_root/manifest.after" || fail_test "second install changed managed runtime bytes"
pass_test "idempotent repeated install"

# Stable exit codes for invalid invocation and incompatible Codex.
new_case exit-codes
expect_status 2 env CODEX_BIN="$fake_codex" "$installer" --unknown
expect_status 3 env CODEX_BIN="${temp_root}/missing-codex" "$installer" \
  --repo "$repo_root" --codex-home "$case_home" --user-skills-home "$case_skills"
assert_absent "$case_home"
pass_test "argument and Codex preflight exit codes"

printf '\nAll %s global Codex installer regression groups passed.\n' "$test_count"
