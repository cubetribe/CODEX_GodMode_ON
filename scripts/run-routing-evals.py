#!/usr/bin/env python3
"""Validate the checked-in routing fixtures against the lean mode contract."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "evals/routing/cases.json"
SCHEMA = ROOT / "evals/routing/live-result.schema.json"
SKILL_ROOT = ROOT / "templates/global-codex/skills"
GLOBAL_AGENTS = ROOT / "templates/global-codex/AGENTS.md"
PRIMARY = {"godmode-workflow", "godmode-debug", "godmode-review", "godmode-prototype"}
SPECIALISTS = {
    "api_guardian",
    "validator",
    "tester",
    "runtime_platform",
    "workflow_design",
    "docs_dx",
    "ci_security_guardian",
}


def check_packaged_contract(failures: list[str]) -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    properties = schema.get("properties", {})
    schema_modes = set(properties.get("primary_mode", {}).get("enum", []))
    specialist_schema = properties.get("specialists", {})
    schema_specialists = set(specialist_schema.get("items", {}).get("enum", []))
    schema_checks = [
        (schema.get("additionalProperties") is False, "live schema rejects extra fields"),
        (set(schema.get("required", [])) == {"case", "primary_mode", "specialists", "writer", "gate", "verdict"}, "live schema has the complete result contract"),
        (schema_modes == PRIMARY, "live schema primary-mode enum matches the package"),
        (schema_specialists == SPECIALISTS, "live schema specialist enum matches the package"),
        (specialist_schema.get("maxItems") == 2, "live schema caps specialists at two"),
        (specialist_schema.get("uniqueItems") is True, "live schema rejects duplicate specialists"),
    ]
    for passed, label in schema_checks:
        if not passed:
            failures.append(f"packaged contract: {label}")
            print(f"[fail] packaged contract: {label}")

    global_contract = GLOBAL_AGENTS.read_text(encoding="utf-8")
    global_checks = [
        ("Default to working without subagents" in global_contract, "global prompt defaults to no subagents"),
        ("delegated agents must not delegate again" in global_contract, "global prompt forbids recursive delegation"),
        ("sole tracked-file writer" in global_contract, "global prompt has one tracked-file writer"),
        ("`tester` may create disposable tool output" in global_contract, "global prompt states the tester write exception"),
    ]
    for passed, label in global_checks:
        if not passed:
            failures.append(f"packaged contract: {label}")
            print(f"[fail] packaged contract: {label}")

    for mode in sorted(PRIMARY):
        path = SKILL_ROOT / mode / "SKILL.md"
        text = path.read_text(encoding="utf-8")
        other_names = {item.removeprefix("godmode-") for item in PRIMARY - {mode}}
        checks = [
            (f"name: {mode}" in text, "frontmatter name"),
            ("primary mode" in text.lower(), "primary-mode declaration"),
            ("do not combine" in text.lower(), "exclusive-mode rule"),
            (all(name in text.lower() for name in other_names), "names every incompatible primary mode"),
        ]
        for passed, label in checks:
            if not passed:
                failures.append(f"{mode}: {label}")
                print(f"[fail] {mode}: {label}")


def main() -> int:
    cases = json.loads(CASES.read_text(encoding="utf-8"))
    failures: list[str] = []
    check_packaged_contract(failures)
    seen: set[str] = set()
    for case in cases:
        case_id = case.get("id", "<missing>")
        prompt = case.get("prompt", "")
        expected = case.get("primary_mode")
        allowed = case.get("max_specialists")
        modes = set(re.findall(r"\$(godmode-(?:workflow|debug|review|prototype))\b", prompt))
        specialists = set(re.findall(r"\$(\w+)\b", prompt)) & SPECIALISTS
        checks = [
            (case_id not in seen, "unique id"),
            (expected in PRIMARY, "known primary mode"),
            (modes == {expected}, "exactly one expected primary mode"),
            (isinstance(allowed, int) and 0 <= allowed <= 2, "specialist budget from 0 to 2"),
            (len(specialists) <= allowed if isinstance(allowed, int) else False, "prompt respects specialist budget"),
        ]
        seen.add(case_id)
        case_failures = [label for passed, label in checks if not passed]
        if case_failures:
            failures.append(f"{case_id}: {', '.join(case_failures)}")
            print(f"[fail] {case_id}: {', '.join(case_failures)}")
        else:
            print(f"[pass] {case_id}: {expected}, specialists={len(specialists)}/{allowed}")
    if failures:
        print(f"\nRouting evals failed with {len(failures)} case(s).")
        return 1
    print(f"\nAll {len(cases)} routing fixtures and packaged contract checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
