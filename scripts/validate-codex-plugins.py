#!/usr/bin/env python3
"""Validate the repository-owned Codex marketplace and local plugin manifests."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any


NAME = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$")
SEMVER = re.compile(r"^(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")
ALLOWED_MANIFEST_FIELDS = {
    "name",
    "version",
    "description",
    "author",
    "homepage",
    "repository",
    "license",
    "keywords",
    "skills",
    "mcpServers",
    "apps",
    "interface",
}
REQUIRED_INTERFACE_FIELDS = {
    "displayName",
    "shortDescription",
    "longDescription",
    "developerName",
    "category",
    "capabilities",
    "defaultPrompt",
}


class Validator:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.errors: list[str] = []

    def error(self, message: str) -> None:
        self.errors.append(message)

    def load_json(self, path: Path) -> Any:
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            self.error(f"missing JSON file: {path.relative_to(self.root)}")
        except (OSError, UnicodeError, json.JSONDecodeError, ValueError, RecursionError) as exc:
            self.error(f"invalid JSON file {path.relative_to(self.root)}: {exc}")
        return None

    def safe_repo_path(self, raw: str, base: Path, label: str) -> Path | None:
        if not isinstance(raw, str) or not raw.startswith("./"):
            self.error(f"{label} must be a ./-relative path")
            return None
        path = (base / raw).resolve()
        try:
            path.relative_to(self.root)
        except ValueError:
            self.error(f"{label} escapes the repository: {raw}")
            return None
        return path

    def validate_skill(self, skill: Path) -> None:
        skill_file = skill / "SKILL.md"
        if not skill_file.is_file():
            self.error(f"missing skill file: {skill_file.relative_to(self.root)}")
            return
        text = skill_file.read_text(encoding="utf-8")
        if "[TODO:" in text:
            self.error(f"skill contains TODO placeholder: {skill_file.relative_to(self.root)}")
        match = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
        if not match:
            self.error(f"skill frontmatter is invalid: {skill_file.relative_to(self.root)}")
        else:
            fields: dict[str, str] = {}
            for line in match.group(1).splitlines():
                if ":" not in line:
                    self.error(f"skill frontmatter line is invalid: {line!r}")
                    continue
                key, value = line.split(":", 1)
                fields[key.strip()] = value.strip()
            if set(fields) != {"name", "description"}:
                self.error(f"skill frontmatter must contain only name and description: {skill_file.relative_to(self.root)}")
            if fields.get("name") != skill.name or not fields.get("description"):
                self.error(f"skill metadata does not match its directory: {skill_file.relative_to(self.root)}")
        metadata = skill / "agents" / "openai.yaml"
        if not metadata.is_file():
            self.error(f"missing skill UI metadata: {metadata.relative_to(self.root)}")
            return
        metadata_text = metadata.read_text(encoding="utf-8")
        for field in ("display_name", "short_description", "default_prompt"):
            if not re.search(rf'^  {field}: "[^"\\]*(?:\\.[^"\\]*)*"$', metadata_text, re.MULTILINE):
                self.error(f"openai.yaml lacks quoted {field}: {metadata.relative_to(self.root)}")
        if f"${skill.name}" not in metadata_text:
            self.error(f"openai.yaml default prompt must mention ${skill.name}: {metadata.relative_to(self.root)}")
        if skill.name == "godmode-paperwork" and not re.search(
            r"^policy:\n  allow_implicit_invocation: false$", metadata_text, re.MULTILINE
        ):
            self.error("godmode-paperwork must require explicit skill invocation")
        if skill.name == "godmode-paperwork":
            schema_root = skill / "assets" / "schemas"
            required_schemas = {
                "approval-input.schema.json",
                "approval.schema.json",
                "case.schema.json",
                "claim.schema.json",
                "document.schema.json",
                "page-resolution.schema.json",
                "page.schema.json",
                "requirements.schema.json",
            }
            actual_schemas = {path.name for path in schema_root.glob("*.json")} if schema_root.is_dir() else set()
            if actual_schemas != required_schemas:
                self.error(
                    "godmode-paperwork schemas differ from the required input/record contract: "
                    f"expected={sorted(required_schemas)} actual={sorted(actual_schemas)}"
                )
            for schema_name in sorted(actual_schemas):
                schema = self.load_json(schema_root / schema_name)
                if not isinstance(schema, dict) or schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
                    self.error(f"invalid Draft 2020-12 schema: {schema_name}")

    def validate_manifest(self, plugin_root: Path, expected_name: str) -> None:
        manifest_path = plugin_root / ".codex-plugin" / "plugin.json"
        manifest = self.load_json(manifest_path)
        if not isinstance(manifest, dict):
            return
        version_path = plugin_root / "VERSION"
        try:
            plugin_version = version_path.read_text(encoding="utf-8").strip()
        except (OSError, UnicodeError) as exc:
            self.error(f"missing or unreadable plugin VERSION for {expected_name}: {exc}")
            plugin_version = ""
        if "[TODO:" in manifest_path.read_text(encoding="utf-8"):
            self.error(f"plugin manifest contains a TODO placeholder: {manifest_path.relative_to(self.root)}")
        unknown = set(manifest) - ALLOWED_MANIFEST_FIELDS
        if unknown:
            self.error(f"unsupported plugin manifest fields in {expected_name}: {sorted(unknown)}")
        if manifest.get("name") != expected_name or plugin_root.name != expected_name:
            self.error(f"plugin name, folder, and marketplace entry differ: {expected_name}")
        if not isinstance(manifest.get("version"), str) or not SEMVER.fullmatch(manifest["version"]):
            self.error(f"plugin version is not strict semver: {expected_name}")
        if not SEMVER.fullmatch(plugin_version):
            self.error(f"plugin VERSION is not strict semver: {expected_name}")
        elif manifest.get("version") != plugin_version:
            self.error(
                f"plugin manifest version {manifest.get('version')!r} differs from plugin VERSION {plugin_version}: {expected_name}"
            )
        if not isinstance(manifest.get("description"), str) or not manifest["description"].strip():
            self.error(f"plugin description is missing: {expected_name}")
        author = manifest.get("author")
        if not isinstance(author, dict) or not isinstance(author.get("name"), str) or not author["name"].strip():
            self.error(f"plugin author.name is missing: {expected_name}")
        interface = manifest.get("interface")
        if not isinstance(interface, dict):
            self.error(f"plugin interface is missing: {expected_name}")
        else:
            missing = REQUIRED_INTERFACE_FIELDS - set(interface)
            if missing:
                self.error(f"plugin interface is incomplete for {expected_name}: {sorted(missing)}")
            for field in REQUIRED_INTERFACE_FIELDS - {"capabilities", "defaultPrompt"}:
                if not isinstance(interface.get(field), str) or not interface[field].strip():
                    self.error(f"plugin interface.{field} is invalid: {expected_name}")
            capabilities = interface.get("capabilities")
            prompts = interface.get("defaultPrompt")
            if not isinstance(capabilities, list) or not capabilities or not all(isinstance(item, str) and item for item in capabilities):
                self.error(f"plugin capabilities are invalid: {expected_name}")
            if (
                not isinstance(prompts, list)
                or not 1 <= len(prompts) <= 3
                or not all(isinstance(item, str) and 0 < len(item) <= 128 for item in prompts)
            ):
                self.error(f"plugin defaultPrompt must contain 1-3 strings of at most 128 characters: {expected_name}")
        for field in ("skills", "apps"):
            if field in manifest:
                path = self.safe_repo_path(manifest[field], plugin_root, f"plugin {expected_name} {field}")
                if path is not None and not path.exists():
                    self.error(f"plugin {expected_name} {field} path does not exist: {manifest[field]}")
        if isinstance(manifest.get("mcpServers"), str):
            path = self.safe_repo_path(manifest["mcpServers"], plugin_root, f"plugin {expected_name} mcpServers")
            if path is not None and not path.is_file():
                self.error(f"plugin {expected_name} mcpServers path does not exist")
        skills_root = plugin_root / "skills"
        skills = sorted(path for path in skills_root.iterdir() if path.is_dir()) if skills_root.is_dir() else []
        if manifest.get("skills") and not skills:
            self.error(f"plugin declares skills but contains none: {expected_name}")
        for skill in skills:
            self.validate_skill(skill)

    def run(self) -> int:
        marketplace_path = self.root / ".agents" / "plugins" / "marketplace.json"
        marketplace = self.load_json(marketplace_path)
        if not isinstance(marketplace, dict):
            return self.finish()
        if not NAME.fullmatch(str(marketplace.get("name", ""))):
            self.error("marketplace name must be lowercase hyphen-case")
        interface = marketplace.get("interface")
        if interface is not None and (not isinstance(interface, dict) or not isinstance(interface.get("displayName"), str)):
            self.error("marketplace interface.displayName is invalid")
        entries = marketplace.get("plugins")
        if not isinstance(entries, list) or not entries:
            self.error("marketplace plugins must be a non-empty array")
            return self.finish()
        seen: set[str] = set()
        for index, entry in enumerate(entries):
            if not isinstance(entry, dict):
                self.error(f"marketplace plugin entry {index} is not an object")
                continue
            name = entry.get("name")
            if not isinstance(name, str) or not NAME.fullmatch(name) or name in seen:
                self.error(f"marketplace plugin name is invalid or duplicated: {name!r}")
                continue
            seen.add(name)
            source = entry.get("source")
            expected_source = {"source": "local", "path": f"./plugins/{name}"}
            if source != expected_source:
                self.error(f"marketplace source must be {expected_source!r}: {name}")
                continue
            policy = entry.get("policy")
            if not isinstance(policy, dict):
                self.error(f"marketplace policy is missing: {name}")
            else:
                if policy.get("installation") not in {"NOT_AVAILABLE", "AVAILABLE", "INSTALLED_BY_DEFAULT"}:
                    self.error(f"invalid installation policy: {name}")
                if policy.get("authentication") not in {"ON_INSTALL", "ON_USE"}:
                    self.error(f"invalid authentication policy: {name}")
                if name == "godmode-paperwork" and policy.get("installation") != "AVAILABLE":
                    self.error("godmode-paperwork must remain optional with installation=AVAILABLE")
                if name == "godmode-paperwork" and policy.get("authentication") != "ON_INSTALL":
                    self.error("godmode-paperwork marketplace policy must remain authentication=ON_INSTALL")
            if not isinstance(entry.get("category"), str) or not entry["category"]:
                self.error(f"marketplace category is missing: {name}")
            plugin_root = self.root / "plugins" / name
            if not plugin_root.is_dir() or plugin_root.is_symlink():
                self.error(f"plugin directory is missing or linked: {name}")
                continue
            self.validate_manifest(plugin_root, name)
        for path in (self.root / "plugins").rglob("*"):
            if path.is_symlink():
                self.error(f"symbolic link in plugin tree: {path.relative_to(self.root)}")
        return self.finish()

    def finish(self) -> int:
        if self.errors:
            for error in self.errors:
                print(f"[invalid] {error}", file=sys.stderr)
            return 1
        print("[ok] repository Codex marketplace and plugins")
        return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    arguments = parser.parse_args()
    return Validator(arguments.repo_root).run()


if __name__ == "__main__":
    raise SystemExit(main())
