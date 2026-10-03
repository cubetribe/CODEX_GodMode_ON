#!/usr/bin/env python3
"""Read-only GodMode installation audit. No downloads or installer execution."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import sys
import tomllib
import urllib.request
from pathlib import Path

RELEASE_URL = "https://api.github.com/repos/cubetribe/CODEX_GodMode_ON/releases/latest"
NAME = re.compile(r"[a-z0-9][a-z0-9_.-]*")
SEMVER = re.compile(r"v?(\d+)\.(\d+)\.(\d+)")


def regular(path: Path) -> bool:
    return path.is_file() and not linked(path)


def linked(path: Path) -> bool:
    try:
        attributes = getattr(path.lstat(), "st_file_attributes", 0)
        return path.is_symlink() or bool(attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)
    except FileNotFoundError:
        return False


def read(path: Path) -> str:
    if not regular(path):
        raise ValueError(f"Missing or linked file: {path}")
    return path.read_text(encoding="utf-8").strip()


def digest(path: Path, normalize: bool = False) -> str:
    data = path.read_bytes()
    if normalize:
        data = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def manifest(root: Path) -> dict[str, str]:
    if linked(root) or not root.is_dir():
        raise ValueError(f"Not a regular directory: {root}")
    result = {}
    for item in sorted(root.rglob("*")):
        if linked(item):
            raise ValueError(f"Linked asset: {item}")
        if item.is_file():
            result[item.relative_to(root).as_posix()] = digest(item)
        elif not item.is_dir():
            raise ValueError(f"Non-regular asset: {item}")
        else:
            result[item.relative_to(root).as_posix() + "/"] = "directory"
    return result


def inventory(repo: Path) -> list[tuple[str, str, str, str]]:
    rows = []
    seen = set()
    for line in read(repo / "templates/global-codex/managed-assets.tsv").splitlines():
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) != 4:
            raise ValueError("Malformed managed inventory")
        status, kind, name, sha = parts
        if (status not in {"active", "retired"} or kind not in {"agent", "skill", "profile"}
                or not NAME.fullmatch(name) or (kind, name) in seen
                or (status == "active" and sha != "-")
                or (status == "retired" and (kind == "profile" or not re.fullmatch(r"[0-9a-f]{64}", sha)))):
            raise ValueError("Invalid managed inventory row")
        seen.add((kind, name))
        rows.append((status, kind, name, sha))
    if not rows:
        raise ValueError("Empty managed inventory")
    return rows


def latest_release() -> dict:
    request = urllib.request.Request(RELEASE_URL, headers={"User-Agent": "GodMode-audit", "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(request, timeout=15) as response:
        data = json.loads(response.read(1024 * 1024))
    tag = data.get("tag_name", "")
    if not SEMVER.fullmatch(tag) or data.get("draft") or data.get("prerelease"):
        raise ValueError("Latest release is not a stable semantic tag")
    return {"status": "known", "version": tag.removeprefix("v"),
            "url": f"https://github.com/cubetribe/CODEX_GodMode_ON/releases/tag/{tag}"}


def audit(repo: Path, codex_home: Path, skills_home: Path) -> dict:
    rows = inventory(repo)
    source = repo / "templates/global-codex"
    findings = []

    def finding(state: str, path: Path, detail: str) -> None:
        findings.append({"state": state, "path": str(path), "detail": detail})

    for root in (codex_home, codex_home / "agents", codex_home / "skills", skills_home, codex_home / "godmode"):
        if linked(root) or (root.exists() and not root.is_dir()):
            finding("conflict", root, "Discovery or receipt root is linked or not a directory")
    if findings:
        return {"checkout_version": read(repo / "VERSION"), "installed_version": "unknown", "findings": findings}

    version_path = codex_home / "godmode/VERSION"
    installed = read(version_path) if regular(version_path) else "unknown"
    checkout = read(repo / "VERSION")
    if installed != checkout:
        finding("version", version_path, f"Installed {installed}; checkout {checkout}")
    for receipt in ("source-repo.txt", "user-skills-home.txt"):
        target = codex_home / "godmode" / receipt
        expected = repo if receipt == "source-repo.txt" else skills_home
        if not regular(target) or Path(read(target)).resolve() != expected.resolve():
            finding("receipt", target, "Missing, linked, or different installation locator")

    retired = {(kind, name): {sha} for status, kind, name, sha in rows if status == "retired"}
    ledger = source / "legacy-hashes.tsv"
    for line in read(ledger).splitlines():
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) != 4 or tuple(parts[:2]) not in retired or not re.fullmatch(r"[0-9a-f]{64}", parts[2]):
            raise ValueError("Invalid legacy hash ledger")
        retired[tuple(parts[:2])].add(parts[2])

    roots = list(dict.fromkeys((skills_home.resolve(), (codex_home / "skills").resolve())))
    known = {(kind, name) for _, kind, name, _ in rows}
    for root, kind in [(codex_home / "agents", "agent")] + [(root, "skill") for root in roots]:
        if not root.is_dir():
            continue
        for item in root.iterdir():
            if ".backup-" not in item.name:
                continue
            base = item.name.split(".backup-", 1)[0]
            if kind == "agent":
                base = base.removesuffix(".toml")
            if (kind, base) in known:
                finding("discovery-backup", item, "Known managed backup remains in a discovery root")
    for status, kind, name, sha in rows:
        targets = ([codex_home / "agents" / f"{name}.toml"] if kind == "agent" else
                   [codex_home / name] if kind == "profile" else [root / name for root in roots])
        origin = (source / "agents" / f"{name}.toml" if kind == "agent" else
                  source / "profiles" / name if kind == "profile" else source / "skills" / name)
        for index, target in enumerate(targets):
            exists = target.exists() or linked(target)
            if status == "retired":
                if not exists:
                    continue
                exact = False
                try:
                    exact = (regular(target) and digest(target, True) in retired[(kind, name)] if kind == "agent" else
                             set(manifest(target)) == {"SKILL.md"} and digest(target / "SKILL.md", True) in retired[(kind, name)])
                except (ValueError, OSError):
                    pass
                finding("retired-exact" if exact else "conflict", target,
                        "Known package copy can be archived by installer" if exact else "Unrecognized retired content; preserve and resolve")
            elif kind == "skill" and index > 0:
                if exists:
                    finding("duplicate", target, "Alternate-root active skill; preserve and resolve before install")
            elif not exists:
                finding("missing", target, "Managed package asset is absent")
            else:
                try:
                    exact = (manifest(origin) == manifest(target) if kind == "skill" else
                             regular(target) and digest(origin) == digest(target))
                    if not exact:
                        finding("drift", target, "Active package content differs; normal install backs up and replaces")
                except (ValueError, OSError) as error:
                    finding("conflict", target, str(error))

    source_inventory = source / "managed-assets.tsv"
    target_inventory = codex_home / "godmode/managed-assets.tsv"
    if not regular(target_inventory) or digest(source_inventory) != digest(target_inventory):
        finding("drift", target_inventory, "Installed roster is missing or differs")
    target_guidance = codex_home / "AGENTS.md"
    if regular(target_guidance):
        text = target_guidance.read_text(encoding="utf-8").replace("\r\n", "\n")
        begin = "<!-- CODEX_GODMODE_GLOBAL_AGENTS:BEGIN -->"
        end = "<!-- CODEX_GODMODE_GLOBAL_AGENTS:END -->"
        lines = text.splitlines()
        begins = [i for i, line in enumerate(lines) if line == begin]
        ends = [i for i, line in enumerate(lines) if line == end]
        expected = (source / "AGENTS.md").read_text(encoding="utf-8").strip()
        if len(begins) != 1 or len(ends) != 1 or begins[0] >= ends[0] or "\n".join(lines[begins[0]:ends[0] + 1]) != expected:
            finding("drift", target_guidance, "Managed guidance differs or markers are invalid")
    else:
        finding("missing", target_guidance, "Global guidance missing or linked")
    config = codex_home / "config.toml"
    try:
        data = tomllib.loads(read(config))
        agents = data.get("agents", {})
        if not isinstance(agents, dict):
            raise ValueError("Config agents must be a table")
        for name in agents:
            if ("agent", name) in retired:
                finding("config-reference", config, f"User config still declares retired role {name}; resolve manually")
    except (OSError, ValueError, tomllib.TOMLDecodeError) as error:
        finding("config", config, str(error))
    return {"checkout_version": checkout, "installed_version": installed,
            "repo": str(repo), "codex_home": str(codex_home), "user_skills_home": str(skills_home),
            "findings": findings, "scope": "Core global roots only; project, plugin, other-host and cached chat state need separate inspection"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path)
    parser.add_argument("--codex-home", type=Path, default=Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex"))
    parser.add_argument("--user-skills-home", type=Path)
    parser.add_argument("--github", action="store_true", help="Read latest public stable release metadata; no code download")
    args = parser.parse_args()
    try:
        record = args.codex_home / "godmode"
        repo = args.repo or Path(read(record / "source-repo.txt"))
        skills = args.user_skills_home or (Path(read(record / "user-skills-home.txt")) if regular(record / "user-skills-home.txt") else Path.home() / ".agents/skills")
        result = audit(repo, args.codex_home, skills)
        result["published"] = {"status": "not-checked"}
        if args.github:
            try:
                result["published"] = latest_release()
            except (OSError, ValueError) as error:
                result["published"] = {"status": "unknown", "error": str(error)}
        healthy = not result["findings"]
        result["installation_exact"] = healthy
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if healthy and result["published"]["status"] != "unknown" else 1
    except (OSError, ValueError) as error:
        print(json.dumps({"installation_exact": False, "error": str(error)}))
        return 2


if __name__ == "__main__":
    sys.exit(main())
