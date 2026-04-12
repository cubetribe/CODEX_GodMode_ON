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
source_repo_agents="${repo_root}/.codex/agents"
source_repo_skills="${repo_root}/.agents/skills"
target_agents="${codex_home}/AGENTS.md"
target_config="${codex_home}/config.toml"
target_agents_dir="${codex_home}/agents"
playwright_output="${codex_home}/playwright-output/isolated"
timestamp="$(date +%Y-%m-%dT%H-%M-%S)"

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
    local backup_path="${path}.backup-${timestamp}"
    cp -R "$path" "$backup_path"
    printf 'Backed up %s -> %s\n' "$path" "$backup_path"
  fi
}

render_config_template() {
  local escaped_codex_home
  escaped_codex_home="$(printf '%s' "$codex_home" | sed 's/[\/&]/\\&/g')"
  sed "s#__CODEX_HOME__#${escaped_codex_home}#g" "$source_config" > "$target_config"
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
  for source_path in "${source_repo_agents}"/*.toml; do
    [[ -f "$source_path" ]] || continue
    local target_path="${target_agents_dir}/$(basename "$source_path")"
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

run_check() {
  local status=0

  check_path "$target_agents" "Global AGENTS" || status=1
  check_path "$target_config" "Global config" || status=1
  check_path "$target_agents_dir" "Global agents dir" || status=1
  check_path "$user_skills_home" "User skills home" || status=1
  check_path "$playwright_output" "Playwright output" || status=1
  check_path "${target_agents_dir}/builder.toml" "Global agent builder" || status=1
  check_path "${target_agents_dir}/researcher.toml" "Global agent researcher" || status=1
  check_path "${target_agents_dir}/runtime_platform.toml" "Global agent runtime_platform" || status=1
  check_path "${target_agents_dir}/workflow_design.toml" "Global agent workflow_design" || status=1
  check_path "${target_agents_dir}/workspace_governance.toml" "Global agent workspace_governance" || status=1
  check_path "${target_agents_dir}/quality_operations.toml" "Global agent quality_operations" || status=1
  check_path "${target_agents_dir}/docs_dx.toml" "Global agent docs_dx" || status=1
  check_path "${user_skills_home}/godmode-workflow/SKILL.md" "Global skill godmode-workflow" || status=1
  check_path "${user_skills_home}/godmode-departments/SKILL.md" "Global skill godmode-departments" || status=1
  check_path "${user_skills_home}/greenfield-bootstrap/SKILL.md" "Global skill greenfield-bootstrap" || status=1
  check_path "${user_skills_home}/web-platforms/SKILL.md" "Global skill web-platforms" || status=1

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

  if [[ -f "${target_agents_dir}/builder.toml" ]]; then
    check_contains "${target_agents_dir}/builder.toml" 'name = "builder"' "installed builder agent name" || status=1
  fi

  if [[ -f "${target_agents_dir}/runtime_platform.toml" ]]; then
    check_contains "${target_agents_dir}/runtime_platform.toml" 'name = "runtime_platform"' "installed runtime_platform agent name" || status=1
  fi

  if [[ -f "${user_skills_home}/godmode-workflow/SKILL.md" ]]; then
    check_contains "${user_skills_home}/godmode-workflow/SKILL.md" "GodMode Workflow" "installed godmode skill" || status=1
  fi

  if [[ -f "${user_skills_home}/godmode-departments/SKILL.md" ]]; then
    check_contains "${user_skills_home}/godmode-departments/SKILL.md" "GodMode Departments" "installed godmode departments skill" || status=1
  fi

  if [[ -f "${user_skills_home}/greenfield-bootstrap/SKILL.md" ]]; then
    check_contains "${user_skills_home}/greenfield-bootstrap/SKILL.md" "Greenfield Bootstrap" "installed greenfield skill" || status=1
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
