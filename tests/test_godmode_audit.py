"""Executable audit regressions, entirely offline and in temporary homes."""

import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "templates/global-codex/skills/godmode-update/scripts/audit.py"
spec = importlib.util.spec_from_file_location("godmode_audit", SCRIPT)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="godmode-audit-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.home = self.root / "codex home"
        self.skills = self.root / "skills"
        self.codex = self.root / "codex"
        self.codex.write_text('#!/bin/sh\ncase "$1" in --version) echo "codex-cli 0.147.0" ;; help) exit 0 ;; *) exit 1 ;; esac\n')
        self.codex.chmod(0o755)
        subprocess.run(["bash", str(ROOT / "scripts/apply-global-codex-setup.sh"), "--codex-home", str(self.home),
                        "--user-skills-home", str(self.skills), "--no-trust-project"],
                       env={**os.environ, "CODEX_BIN": str(self.codex)}, check=True, capture_output=True)

    def snapshot(self):
        return {str(p.relative_to(self.root)): (p.read_bytes() if p.is_file() and not p.is_symlink() else "directory")
                for p in self.root.rglob("*")}

    def test_exact_and_read_only_cli_locator(self):
        before = self.snapshot()
        result = subprocess.run([sys.executable, str(SCRIPT), "--codex-home", str(self.home)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(json.loads(result.stdout)["installation_exact"])
        self.assertEqual(before, self.snapshot())

    def test_reports_all_drift_retirement_duplicates_and_config(self):
        (self.home / "agents/validator.toml").write_text("custom")
        (self.skills / "godmode-debug/SKILL.md").unlink()
        alternate = self.home / "skills"
        alternate.mkdir()
        shutil.copytree(ROOT / "tests/fixtures/global-codex-2.0/skills/godmode-departments", alternate / "godmode-departments")
        shutil.copytree(ROOT / "templates/global-codex/skills/godmode-workflow", alternate / "godmode-workflow")
        (self.home / "config.toml").write_text('[agents.researcher]\nconfig_file = "external.toml"\n')
        before = self.snapshot()
        result = audit.audit(ROOT, self.home, self.skills)
        states = {x["state"] for x in result["findings"]}
        self.assertTrue({"drift", "retired-exact", "duplicate", "config-reference"}.issubset(states), result)
        self.assertEqual(before, self.snapshot())

    def test_modified_retired_and_symlink_are_conflicts(self):
        path = self.home / "agents/researcher.toml"
        shutil.copy(ROOT / "tests/fixtures/global-codex-2.0/agents/researcher.toml", path)
        path.write_text(path.read_text() + "# custom\n")
        (self.home / "skills").mkdir()
        (self.home / "skills/godmode-departments").symlink_to(self.root / "absent")
        states = [x for x in audit.audit(ROOT, self.home, self.skills)["findings"] if x["state"] == "conflict"]
        self.assertEqual(len(states), 2)

    def test_same_skill_root_has_no_duplicate(self):
        same = self.home / "skills"
        shutil.move(self.skills, same)
        (self.home / "godmode/user-skills-home.txt").write_text(str(same) + "\n")
        self.assertEqual(audit.audit(ROOT, self.home, same)["findings"], [])

    def test_missing_receipt_is_not_healthy(self):
        (self.home / "godmode/VERSION").unlink()
        result = audit.audit(ROOT, self.home, self.skills)
        self.assertEqual(result["installed_version"], "unknown")
        self.assertTrue(result["findings"])

    def test_inline_marker_text_is_preserved_user_guidance(self):
        path = self.home / "AGENTS.md"
        path.write_text(path.read_text() + '\nThis sentence quotes <!-- CODEX_GODMODE_GLOBAL_AGENTS:BEGIN --> inline.\n')
        self.assertEqual(audit.audit(ROOT, self.home, self.skills)["findings"], [])

    def test_managed_backups_in_both_roots_are_findings(self):
        (self.skills / "godmode-workflow.backup-old").mkdir()
        (self.home / "skills").mkdir()
        (self.home / "skills/godmode-departments.backup-old").mkdir()
        (self.skills / "custom.backup-user").mkdir()
        states = [x for x in audit.audit(ROOT, self.home, self.skills)["findings"] if x["state"] == "discovery-backup"]
        self.assertEqual(len(states), 2)

    def test_reparse_attribute_is_a_link(self):
        import stat
        from types import SimpleNamespace
        with patch.object(Path, "lstat", return_value=SimpleNamespace(st_file_attributes=stat.FILE_ATTRIBUTE_REPARSE_POINT, st_mode=stat.S_IFDIR)):
            self.assertTrue(audit.linked(self.home))

    def test_invalid_runtime_config_is_a_controlled_finding(self):
        for value in ('1', '["unexpected"]'):
            with self.subTest(value=value):
                (self.home / "config.toml").write_text(f'agents = {value}\n')
                findings = audit.audit(ROOT, self.home, self.skills)["findings"]
                self.assertTrue(any(x["state"] == "config" for x in findings))

    def test_dangling_reparse_candidate_is_not_absent(self):
        root = self.home / "skills"
        root.mkdir()
        candidate = root.resolve() / "godmode-departments"
        original = audit.linked
        with patch.object(audit, "linked", side_effect=lambda p: p == candidate or original(p)):
            findings = audit.audit(ROOT, self.home, self.skills)["findings"]
        self.assertTrue(any(x["state"] == "conflict" and x["path"] == str(candidate) for x in findings))

    def test_relative_skill_locator_works_from_a_different_directory(self):
        subprocess.run(["bash", str(ROOT / "scripts/apply-global-codex-setup.sh"), "--codex-home", str(self.home),
                        "--user-skills-home", "relative-skills", "--no-trust-project"], cwd=self.root,
                       env={**os.environ, "CODEX_BIN": str(self.codex)}, check=True, capture_output=True)
        result = subprocess.run([sys.executable, str(SCRIPT), "--codex-home", str(self.home)], cwd=ROOT,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_release_metadata_stable_only(self):
        for data, valid in [({"tag_name": "v3.0.0", "draft": False, "prerelease": False}, True),
                            ({"tag_name": "v9.0.0", "prerelease": True}, False),
                            ({"tag_name": "$(danger)"}, False)]:
            with self.subTest(data=data), patch.object(audit.urllib.request, "urlopen") as mock:
                mock.return_value.__enter__.return_value.read.return_value = json.dumps(data).encode()
                if valid:
                    self.assertEqual(audit.latest_release()["version"], "3.0.0")
                else:
                    with self.assertRaises(ValueError):
                        audit.latest_release()

    def test_network_failure_is_unknown_and_nonzero(self):
        args = ["audit.py", "--codex-home", str(self.home), "--github"]
        with patch.object(sys, "argv", args), patch.object(audit, "latest_release", side_effect=OSError("offline")), patch("builtins.print") as output:
            self.assertEqual(audit.main(), 1)
        self.assertEqual(json.loads(output.call_args.args[0])["published"]["status"], "unknown")


if __name__ == "__main__":
    unittest.main()
