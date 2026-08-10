#!/usr/bin/env python3
"""Deterministic repository checks for the GodMode package."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ERRORS: list[str] = []


def fail(message: str) -> None:
    ERRORS.append(message)
    print(f"[fail] {message}")


def ok(message: str) -> None:
    print(f"[ok] {message}")


def require(condition: bool, message: str) -> bool:
    if not condition:
        fail(message)
        return False
    return True


def load_toml(path: Path) -> dict:
    try:
        with path.open("rb") as handle:
            return tomllib.load(handle)
    except (OSError, tomllib.TOMLDecodeError) as error:
        fail(f"invalid TOML {path.relative_to(ROOT)}: {error}")
        return {}


def normalized_sha256(path: Path) -> str:
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def inventory_rows() -> list[tuple[str, str, str, str]]:
    path = ROOT / "templates/global-codex/managed-assets.tsv"
    rows: list[tuple[str, str, str, str]] = []
    if not require(path.is_file(), "managed asset inventory exists"):
        return rows
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) != 4:
            fail(f"managed inventory line {number} must have four tab-separated fields")
            continue
        status, kind, name, digest = parts
        require(status in {"active", "retired"}, f"inventory line {number} has valid status")
        require(kind in {"agent", "skill", "profile"}, f"inventory line {number} has valid kind")
        require(bool(re.fullmatch(r"[a-z0-9][a-z0-9_.-]*", name)), f"inventory line {number} has safe name")
        if status == "retired":
            require(kind in {"agent", "skill"}, f"inventory line {number} has a supported retired kind")
        expected_digest = "-" if status == "active" else r"[0-9a-f]{64}"
        require(bool(re.fullmatch(expected_digest, digest)), f"inventory line {number} has valid digest")
        rows.append((status, kind, name, digest))
    identities = [(kind, name) for _, kind, name, _ in rows]
    require(len(identities) == len(set(identities)), "managed inventory identities are unique")
    return rows


def check_inventory_and_roster() -> None:
    rows = inventory_rows()
    active = {(kind, name) for status, kind, name, _ in rows if status == "active"}
    retired = [(kind, name, digest) for status, kind, name, digest in rows if status == "retired"]

    agent_dir = ROOT / "templates/global-codex/agents"
    skill_dir = ROOT / "templates/global-codex/skills"
    profile_dir = ROOT / "templates/global-codex/profiles"
    actual_agents = {("agent", path.stem) for path in agent_dir.glob("*.toml")}
    actual_skills = {
        ("skill", path.parent.name) for path in skill_dir.glob("*/SKILL.md") if path.is_file()
    }
    actual_profiles = {("profile", path.name) for path in profile_dir.glob("*.toml")}
    require(actual_agents == {item for item in active if item[0] == "agent"}, "inventory matches seven packaged agents")
    require(actual_skills == {item for item in active if item[0] == "skill"}, "inventory matches nine packaged skills")
    require(actual_profiles == {item for item in active if item[0] == "profile"}, "inventory matches four profiles")
    require(len(actual_agents) == 7, "agent roster is lean (7)")
    require(len(actual_skills) == 9, "skill roster is lean (9)")

    fixture_root = ROOT / "tests/fixtures/global-codex-2.0"
    for kind, name, digest in retired:
        if kind == "agent":
            fixture = fixture_root / "agents" / f"{name}.toml"
            live = agent_dir / f"{name}.toml"
        elif kind == "skill":
            fixture = fixture_root / "skills" / name / "SKILL.md"
            live = skill_dir / name / "SKILL.md"
        else:
            fail(f"retired inventory kind is unsupported: {kind}/{name}")
            continue
        require(not live.exists(), f"retired asset is absent from package: {kind}/{name}")
        if require(fixture.is_file(), f"retired fixture exists: {kind}/{name}"):
            require(normalized_sha256(fixture) == digest, f"retired fixture digest matches: {kind}/{name}")
    legacy_config = fixture_root / "config.toml"
    if require(legacy_config.is_file(), "GodMode 2.0 config fixture exists"):
        require(
            normalized_sha256(legacy_config) == "986ad8fcb66a829008db8ec9b003bdf60884e15c23c76ffa2347f319a49b767d",
            "GodMode 2.0 config fixture is immutable",
        )
        rendered = legacy_config.read_text(encoding="utf-8").replace("__CODEX_HOME__", "/tmp/codex-home")
        try:
            tomllib.loads(rendered)
        except tomllib.TOMLDecodeError as error:
            fail(f"rendered GodMode 2.0 config fixture is invalid TOML: {error}")
    ok("managed inventory, active roster, and retirement fixtures")


def check_agents() -> None:
    agent_dir = ROOT / "templates/global-codex/agents"
    for path in sorted(agent_dir.glob("*.toml")):
        data = load_toml(path)
        expected_keys = {"name", "description", "sandbox_mode", "developer_instructions"}
        require(set(data) == expected_keys, f"agent contract keys are minimal: {path.name}")
        require(data.get("name") == path.stem, f"agent name matches filename: {path.name}")
        require(bool(str(data.get("description", "")).strip()), f"agent description exists: {path.name}")
        expected_sandbox = "workspace-write" if path.stem == "tester" else "read-only"
        require(data.get("sandbox_mode") == expected_sandbox, f"agent sandbox is correct: {path.name}")
        require(bool(str(data.get("developer_instructions", "")).strip()), f"agent instructions exist: {path.name}")
    ok("agent TOML contracts")


def parse_frontmatter(path: Path) -> dict[str, str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        fail(f"skill frontmatter missing: {path.relative_to(ROOT)}")
        return {}
    try:
        end = lines.index("---", 1)
    except ValueError:
        fail(f"skill frontmatter is not closed: {path.relative_to(ROOT)}")
        return {}
    result: dict[str, str] = {}
    for line in lines[1:end]:
        if ":" not in line:
            fail(f"invalid skill frontmatter line in {path.relative_to(ROOT)}: {line}")
            continue
        key, value = line.split(":", 1)
        result[key.strip()] = value.strip()
    return result


def check_skills() -> None:
    retired_names = {
        "researcher",
        "architect",
        "builder",
        "scribe",
        "github_manager",
        "workspace_governance",
        "quality_operations",
        "godmode-departments",
    }
    for path in sorted((ROOT / "templates/global-codex/skills").glob("*/SKILL.md")):
        metadata = parse_frontmatter(path)
        require(set(metadata) == {"name", "description"}, f"skill metadata is minimal: {path.parent.name}")
        require(metadata.get("name") == path.parent.name, f"skill name matches directory: {path.parent.name}")
        require(bool(metadata.get("description")), f"skill description exists: {path.parent.name}")
        if path.parent.name.startswith("godmode-"):
            body = path.read_text(encoding="utf-8")
            for retired in retired_names:
                require(f"`{retired}`" not in body, f"skill {path.parent.name} does not route to retired {retired}")
    workflow_yaml = ROOT / "templates/global-codex/skills/godmode-workflow/agents/openai.yaml"
    if require(workflow_yaml.is_file(), "GodMode workflow UI metadata exists"):
        text = workflow_yaml.read_text(encoding="utf-8")
        for key in ("display_name:", "short_description:", "default_prompt:"):
            require(key in text, f"workflow UI metadata contains {key[:-1]}")
        require("$godmode-workflow" in text, "workflow UI prompt explicitly invokes the skill")
    global_agents = ROOT / "templates/global-codex/AGENTS.md"
    workflow = ROOT / "templates/global-codex/skills/godmode-workflow/SKILL.md"
    require(global_agents.stat().st_size <= 1500, "global AGENTS prompt is at most 1500 bytes")
    require(workflow.stat().st_size <= 2000, "workflow skill is at most 2000 bytes")
    ok("skill metadata, routing, and prompt budgets")


def check_configs() -> None:
    config_specs = [
        (ROOT / ".codex/config.toml", "on-request"),
        (ROOT / "templates/global-codex/config.toml", "on-request"),
        (ROOT / "templates/prototype-mode/config.toml", "never"),
    ]
    forbidden = {
        "model",
        "model_reasoning_effort",
        "max_concurrent_threads_per_session",
        "max_depth",
        "mcp_servers",
    }
    for path, approval in config_specs:
        data = load_toml(path)
        agents = data.get("agents", {})
        require(agents.get("max_threads") == 2, f"agent cap is 2: {path.relative_to(ROOT)}")
        require(data.get("approval_policy") == approval, f"approval policy is correct: {path.relative_to(ROOT)}")
        require(data.get("sandbox_mode") == "workspace-write", f"sandbox is workspace-write: {path.relative_to(ROOT)}")
        for key in forbidden:
            require(key not in data and key not in agents, f"{path.relative_to(ROOT)} omits legacy or user-owned {key}")
    allowed_profile_keys = {"web_search", "model_reasoning_summary", "model_verbosity"}
    for path in sorted((ROOT / "templates/global-codex/profiles").glob("*.toml")):
        data = load_toml(path)
        require(set(data).issubset(allowed_profile_keys), f"profile keys are portable: {path.name}")
    ok("TOML syntax and lean configuration contract")


def check_markdown_links() -> None:
    link_pattern = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
    checked = 0
    for path in sorted(ROOT.rglob("*.md")):
        if ".git" in path.parts or "reports/generated" in path.as_posix():
            continue
        text = path.read_text(encoding="utf-8")
        for match in link_pattern.finditer(text):
            target = match.group(1).strip()
            if target.startswith("<") and target.endswith(">"):
                target = target[1:-1]
            if not target or target.startswith(("#", "http://", "https://", "mailto:")):
                continue
            target = target.split("#", 1)[0]
            if not target:
                continue
            resolved = (path.parent / target).resolve()
            require(resolved.exists(), f"relative Markdown link resolves: {path.relative_to(ROOT)} -> {target}")
            checked += 1
    ok(f"relative Markdown links ({checked})")


def check_shell_and_diff() -> None:
    shell_files = sorted((ROOT / "scripts").glob("*.sh"))
    for path in shell_files:
        result = subprocess.run(["bash", "-n", str(path)], capture_output=True, text=True)
        require(result.returncode == 0, f"bash syntax: {path.name}{': ' + result.stderr.strip() if result.stderr else ''}")
    diff = subprocess.run(["git", "diff", "--check"], cwd=ROOT, capture_output=True, text=True)
    require(diff.returncode == 0, f"git diff whitespace check{': ' + diff.stdout.strip() if diff.stdout else ''}")
    routing = subprocess.run(
        [sys.executable, str(ROOT / "scripts/run-routing-evals.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    require(routing.returncode == 0, f"routing evals{': ' + routing.stdout.strip() if routing.stdout else ''}")
    ok("shell syntax and diff hygiene")


def check_json_files() -> None:
    paths = [
        ROOT / "state/templates/orchestration-state.template.json",
        ROOT / "evals/routing/cases.json",
        ROOT / "evals/routing/live-result.schema.json",
    ]
    for path in paths:
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            fail(f"invalid JSON {path.relative_to(ROOT)}: {error}")
    ok("JSON fixtures")


def check_plugins() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/validate-codex-plugins.py"), "--repo-root", str(ROOT)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    details = "\n".join(part.strip() for part in (result.stdout, result.stderr) if part.strip())
    require(result.returncode == 0, f"plugin contract{': ' + details if details else ''}")
    if result.returncode == 0:
        ok("repository Codex marketplace and plugins")


def check_release_state() -> None:
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    released = re.findall(r"^## \[(\d+\.\d+\.\d+)\] - ", changelog, flags=re.MULTILINE)
    require(bool(re.fullmatch(r"\d+\.\d+\.\d+", version)), "VERSION is semantic")
    require(bool(released) and released[0] == version, "VERSION matches latest released changelog section")

    tracked_result = subprocess.run(
        ["git", "diff", "--name-only", "HEAD"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    untracked_result = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    changed = set(tracked_result.stdout.splitlines()) | set(untracked_result.stdout.splitlines())
    prefixes = (
        ".agents/",
        ".codex/",
        ".github/",
        "docs/",
        "evals/",
        "plugins/",
        "reports/",
        "scripts/",
        "state/",
        "templates/",
        "tests/",
    )
    root_files = {"README.md", "AGENTS.md", "CONTRIBUTING.md", "SECURITY.md", "VERSION"}
    user_relevant = any(
        name != "CHANGELOG.md"
        and not name.startswith("reports/generated/")
        and (name in root_files or name.startswith(prefixes))
        for name in changed
    )
    if user_relevant:
        require("CHANGELOG.md" in changed, "user-relevant working-tree changes include an [Unreleased] changelog edit")
        base_result = subprocess.run(
            ["git", "show", "HEAD:CHANGELOG.md"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        section_pattern = re.compile(r"^## \[Unreleased\]\s*(.*?)(?=^## \[)", flags=re.MULTILINE | re.DOTALL)
        current_match = section_pattern.search(changelog)
        base_match = section_pattern.search(base_result.stdout) if base_result.returncode == 0 else None
        require(current_match is not None, "current changelog has an [Unreleased] section")
        require(base_match is not None, "baseline changelog has an [Unreleased] section")
        if current_match is not None and base_match is not None:
            require(current_match.group(1) != base_match.group(1), "[Unreleased] content differs from the released baseline")
    ok("release-state alignment")


def check_required_paths() -> None:
    paths = [
        "AGENTS.md",
        "README.md",
        "CHANGELOG.md",
        "VERSION",
        ".agents/plugins/marketplace.json",
        "plugins/godmode-paperwork/.codex-plugin/plugin.json",
        "plugins/godmode-paperwork/skills/godmode-paperwork/SKILL.md",
        "templates/global-codex/AGENTS.md",
        "templates/global-codex/config.toml",
        "templates/global-codex/managed-assets.tsv",
        "tests/fixtures/global-codex-2.0/config.toml",
        "scripts/apply-global-codex-setup.sh",
        "scripts/apply-global-codex-setup.ps1",
        "scripts/test-global-codex-setup.sh",
        "scripts/test-global-codex-setup.ps1",
        "scripts/validate-codex-plugins.py",
        "state/templates/orchestration-state.template.json",
    ]
    for relative in paths:
        require((ROOT / relative).exists(), f"required path exists: {relative}")
    require(not (ROOT / ".codex/agents").exists(), "repo-local packaged agent discovery is absent")
    require(not (ROOT / ".agents/skills").exists(), "repo-local packaged skill discovery is absent")
    ok("required package paths")


def main() -> int:
    check_required_paths()
    check_inventory_and_roster()
    check_agents()
    check_skills()
    check_configs()
    check_json_files()
    check_plugins()
    check_markdown_links()
    check_shell_and_diff()
    check_release_state()
    if ERRORS:
        print(f"\nStatic validation failed with {len(ERRORS)} finding(s).")
        return 1
    print("\nStatic validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
