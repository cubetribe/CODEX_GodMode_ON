from __future__ import annotations

import ast
from contextlib import contextmanager
import io
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tarfile
import tempfile
import unittest
from unittest import mock


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = PLUGIN_ROOT / "skills" / "godmode-paperwork" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import paperwork_core as core  # noqa: E402
import paperwork_casework as casework  # noqa: E402
import paperwork_pipeline as pipeline  # noqa: E402
import paperwork_validation as validation  # noqa: E402


FAKE_TOOL = r'''#!{python}
import os
from pathlib import Path
import sys

name = Path(sys.argv[0]).name
args = sys.argv[1:]
if "--version" in args or "-v" in args:
    print(f"{{name}} fake 1.0")
    raise SystemExit(0)
if name == "pdfinfo":
    print(f"Pages: {{os.environ.get('FAKE_PAGES', '2')}}")
elif name == "pdftotext":
    page = int(args[args.index("-f") + 1])
    text = "Native invoice date 2026-01-01 total 100.00 reference ABCDEFGHIJKLMNOPQRSTUVWXYZ\n" if page == 1 else "x\n"
    Path(args[-1]).write_text(text, encoding="utf-8")
elif name == "pdftoppm":
    Path(args[-1] + ".png").write_bytes(b"synthetic-png")
elif name == "tesseract":
    if "--list-langs" in args:
        print(f"List of available languages in \"{{Path(sys.argv[0]).parent / 'tessdata'}}\" (2):")
        print("deu")
        print("eng")
    else:
        base = Path(args[1])
        confidence = os.environ.get("FAKE_OCR_CONF", "95")
        base.with_suffix(".txt").write_text("OCR invoice total 100.00\n", encoding="utf-8")
        header = "level\tpage_num\tblock_num\tpar_num\tline_num\tword_num\tleft\ttop\twidth\theight\tconf\ttext\n"
        rows = [
            "1\t1\t0\t0\t0\t0\t0\t0\t1000\t2000\t-1\t",
            "5\t1\t1\t1\t1\t1\t100\t200\t50\t40\t" + confidence + "\tOCR",
            "5\t1\t1\t1\t1\t2\t160\t200\t100\t40\t" + confidence + "\tinvoice",
            "5\t1\t1\t1\t1\t3\t270\t200\t70\t40\t" + confidence + "\ttotal",
            "5\t1\t1\t1\t1\t4\t350\t200\t100\t40\t" + confidence + "\t100.00",
        ]
        base.with_suffix(".tsv").write_text(header + "\n".join(rows) + "\n", encoding="utf-8")
        base.with_suffix(".hocr").write_text("<html><body>OCR invoice total 100.00</body></html>\n", encoding="utf-8")
'''


class PaperworkTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="paperwork-test-")
        # macOS exposes /var as a symlink to /private/var; use the real case path
        # so the production no-symlink policy is exercised rather than bypassed.
        self.root = Path(self.temp.name).resolve()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def fake_tools(self, names=("pdfinfo", "pdftotext", "pdftoppm", "tesseract")) -> Path:
        directory = self.root / "bin"
        directory.mkdir(exist_ok=True)
        tessdata = directory / "tessdata"
        tessdata.mkdir(exist_ok=True)
        for language in ("deu", "eng"):
            (tessdata / f"{language}.traineddata").write_bytes(f"fake-{language}".encode("utf-8"))
        script = FAKE_TOOL.format(python=sys.executable)
        for name in names:
            path = directory / name
            path.write_text(script, encoding="utf-8")
            path.chmod(0o755)
        return directory

    @contextmanager
    def path(self, directory: Path):
        with mock.patch.dict(os.environ, {"PATH": str(directory)}, clear=False):
            yield

    def source(self, name: str, content: bytes) -> Path:
        path = self.root / name
        path.write_bytes(content)
        return path

    def json_input(self, name: str, value: dict[str, object]) -> Path:
        path = self.root / name
        core.write_json(path, value)
        return path

    def new_case(self, assurance="EXTRACTION", content=b"synthetic-pdf") -> tuple[Path, Path]:
        source = self.source("input.pdf", content)
        case = self.root / "case"
        code, _ = pipeline.intake(str(case), "case-2026", [str(source)], False, assurance, "deu,eng", "tester")
        self.assertEqual(code, core.PASS)
        return case, source

    def native_case(self, assurance="EXTRACTION") -> Path:
        tools = self.fake_tools()
        with self.path(tools), mock.patch.dict(os.environ, {"FAKE_PAGES": "1"}, clear=False):
            case, _ = self.new_case(assurance)
            code, _ = pipeline.extract(str(case), None, "tester")
        self.assertEqual(code, core.PASS)
        return case

    def page_anchor(self, case: Path, quote: str, method="NATIVE", bbox=None) -> dict[str, object]:
        pages = core.read_jsonl(core.case_paths(case)["pages"], core.PAGE_SCHEMA)
        page = next((item for item in pages if item.get("route") == method), pages[0])
        anchor: dict[str, object] = {
            "document": page["document"],
            "page": page["page"],
            "quote": quote,
            "artifact_sha256": page["artifact_sha256"],
            "method": method,
        }
        if bbox is not None:
            anchor["bbox"] = bbox
        return anchor

    def forge_pack(
        self,
        source: Path,
        destination: Path,
        *,
        drop_prefixes: tuple[str, ...] = (),
        mutate_manifest=None,
        trailing: bytes = b"",
    ) -> None:
        payloads: list[tuple[tarfile.TarInfo, bytes]] = []
        manifest: dict[str, object] | None = None
        with tarfile.open(source, "r:") as archive:
            for member in archive.getmembers():
                handle = archive.extractfile(member)
                self.assertIsNotNone(handle)
                content = handle.read()
                if member.name == "PACK-MANIFEST.json":
                    manifest = json.loads(content)
                elif not any(member.name.startswith(prefix) for prefix in drop_prefixes):
                    payloads.append((member, content))
        self.assertIsNotNone(manifest)
        retained = {member.name for member, _ in payloads}
        manifest["entries"] = [entry for entry in manifest["entries"] if entry["path"] in retained]
        if mutate_manifest is not None:
            mutate_manifest(manifest)
        manifest_bytes = core.canonical_bytes(manifest)
        with tarfile.open(destination, "w", format=tarfile.USTAR_FORMAT) as archive:
            for member, content in payloads:
                info = tarfile.TarInfo(member.name)
                info.size = len(content)
                info.mode = member.mode
                info.uid = info.gid = info.mtime = 0
                info.uname = info.gname = ""
                archive.addfile(info, io.BytesIO(content))
            info = tarfile.TarInfo("PACK-MANIFEST.json")
            info.size = len(manifest_bytes)
            info.mode = 0o600
            info.uid = info.gid = info.mtime = 0
            info.uname = info.gname = ""
            archive.addfile(info, io.BytesIO(manifest_bytes))
        if trailing:
            with destination.open("ab") as handle:
                handle.write(trailing)
        digest = core.sha256_file(destination)
        Path(f"{destination}.sha256").write_text(f"{digest}  {destination.name}\n", encoding="utf-8")
        receipt = core.read_json(Path(f"{source}.receipt.json"))
        receipt["archive"] = destination.name
        receipt["archive_sha256"] = digest
        for field in (
            "case_id",
            "contents",
            "actor",
            "validation_status",
            "validation_digest",
            "state_digest",
            "audit_head_sha256",
            "audit_count",
            "approval",
        ):
            receipt[field] = manifest[field]
        core.write_json(Path(f"{destination}.receipt.json"), receipt)

    def test_doctor_reports_present_and_missing_capabilities(self) -> None:
        all_tools = self.fake_tools()
        with self.path(all_tools):
            code, result = pipeline.doctor("deu,eng", "pdf-native,pdf-render,ocr")
        self.assertEqual(code, core.PASS)
        self.assertFalse(result["installation_attempted"])
        self.assertTrue(result["capabilities"]["ocr"]["present"])
        deferred_code, deferred = pipeline.doctor("deu,eng", "advanced-layout")
        self.assertEqual(deferred_code, core.CAPABILITY_MISSING)
        self.assertEqual(deferred["capabilities"]["advanced-layout"]["status"], "DEFERRED")

        missing_render = self.root / "missing-bin"
        missing_render.mkdir()
        script = FAKE_TOOL.format(python=sys.executable)
        for name in ("pdfinfo", "pdftotext", "tesseract"):
            path = missing_render / name
            path.write_text(script, encoding="utf-8")
            path.chmod(0o755)
        with self.path(missing_render):
            code, result = pipeline.doctor("deu,eng", "pdf-native,pdf-render,ocr")
        self.assertEqual(code, core.CAPABILITY_MISSING)
        self.assertEqual(result["missing"], ["pdf-render"])

    def test_intake_deduplicates_and_keeps_relative_aliases(self) -> None:
        first = self.source("first.pdf", b"same")
        second = self.source("second.pdf", b"same")
        case = self.root / "case"
        code, result = pipeline.intake(
            str(case), "dedupe-case", [str(first), str(second)], False, "INVENTORY", "deu,eng", "tester"
        )
        self.assertEqual(code, core.PASS)
        documents = core.read_jsonl(core.case_paths(case)["documents"], core.DOCUMENT_SCHEMA)
        self.assertEqual(len(documents), 1)
        self.assertEqual(documents[0]["source_names"], ["first.pdf", "second.pdf"])
        self.assertEqual(len(result["duplicates"]), 1)
        self.assertFalse(any(Path(name).is_absolute() for name in documents[0]["source_names"]))

    def test_intake_normalizes_equivalent_unicode_aliases_before_deduplication(self) -> None:
        first_directory = self.root / "first-source"
        second_directory = self.root / "second-source"
        first_directory.mkdir()
        second_directory.mkdir()
        first = first_directory / "é.pdf"
        second = second_directory / "e\u0301.pdf"
        first.write_bytes(b"same")
        second.write_bytes(b"same")
        case = self.root / "unicode-case"
        code, _ = pipeline.intake(
            str(case), "unicode-case", [str(first), str(second)], False, "INVENTORY", "deu,eng", "tester"
        )
        self.assertEqual(code, core.PASS)
        state = core.verify_case_integrity(case)
        self.assertEqual(state["documents"][0]["source_names"], ["é.pdf"])

    def test_intake_rejects_backslash_basename_before_case_creation(self) -> None:
        source = self.source("invoice\\escape.pdf", b"unsafe-name")
        case = self.root / "unsafe-name-case"
        with self.assertRaises(core.PaperworkError) as failure:
            pipeline.intake(
                str(case), "unsafe-name-case", [str(source)], False, "INVENTORY", "deu,eng", "tester"
            )
        self.assertEqual(failure.exception.code, core.POLICY_DENIAL)
        self.assertFalse(case.exists())

    def test_private_directory_mode_is_verified_fail_closed(self) -> None:
        directory = self.root / "mode-contract"
        directory.mkdir(mode=0o755)
        directory.chmod(0o755)
        with mock.patch.object(Path, "chmod", return_value=None):
            with self.assertRaises(core.PaperworkError) as failure:
                core.ensure_dir(directory, 0o700)
        self.assertEqual(failure.exception.code, core.PROCESSING)

    def test_intake_rolls_back_when_a_later_original_copy_fails(self) -> None:
        first = self.source("a-first.pdf", b"first")
        second = self.source("b-second.pdf", b"second")
        case = self.root / "case"
        real_copy = pipeline.copy_original_transactional
        calls = 0

        def fail_second_copy(source, destination, expected_hash):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise core.PaperworkError("synthetic copy failure", core.PROCESSING)
            return real_copy(source, destination, expected_hash)

        with mock.patch.object(pipeline, "copy_original_transactional", side_effect=fail_second_copy):
            with self.assertRaises(core.PaperworkError) as failure:
                pipeline.intake(
                    str(case), "rollback-case", [str(first), str(second)], False, "INVENTORY", "deu,eng", "tester"
                )
        self.assertEqual(failure.exception.code, core.PROCESSING)
        self.assertEqual([path for path in case.rglob("*") if path.is_file()], [])

        code, _ = pipeline.intake(
            str(case), "rollback-case", [str(first), str(second)], False, "INVENTORY", "deu,eng", "tester"
        )
        self.assertEqual(code, core.PASS)
        core.verify_case_integrity(case)

    def test_extract_and_route_roll_back_partial_multi_page_work(self) -> None:
        tools = self.fake_tools()
        with self.path(tools):
            case, _ = self.new_case()
            real_run = pipeline.run_tool

            def fail_second_native(arguments, timeout, text=False):
                if (
                    Path(arguments[0]).name == "pdftotext"
                    and "-f" in arguments
                    and arguments[arguments.index("-f") + 1] == "2"
                ):
                    raise core.PaperworkError("synthetic page-two failure", core.PROCESSING)
                return real_run(arguments, timeout, text=text)

            with mock.patch.object(pipeline, "run_tool", side_effect=fail_second_native):
                with self.assertRaises(core.PaperworkError) as extract_failure:
                    pipeline.extract(str(case), None, "tester")
            self.assertEqual(extract_failure.exception.code, core.PROCESSING)
            state = core.verify_case_integrity(case)
            self.assertEqual(state["pages"], [])
            self.assertEqual([path for path in (case / "work").rglob("*") if path.is_file()], [])
            extract_code, _ = pipeline.extract(str(case), None, "tester")
            self.assertEqual(extract_code, core.REVIEW)

        first_image = self.source("first.png", b"first-image")
        second_image = self.source("second.png", b"second-image")
        image_case = self.root / "image-case"
        pipeline.intake(
            str(image_case),
            "image-case",
            [str(first_image), str(second_image)],
            False,
            "EXTRACTION",
            "deu,eng",
            "tester",
        )
        pipeline.extract(str(image_case), None, "tester")
        real_render = pipeline._render_page
        render_calls = 0

        def fail_second_render(root, document, page_number, pdftoppm):
            nonlocal render_calls
            render_calls += 1
            if render_calls == 2:
                raise core.PaperworkError("synthetic second render failure", core.PROCESSING)
            return real_render(root, document, page_number, pdftoppm)

        with self.path(tools), mock.patch.object(pipeline, "_render_page", side_effect=fail_second_render):
            with self.assertRaises(core.PaperworkError) as route_failure:
                pipeline.route(str(image_case), None, "tester")
        self.assertEqual(route_failure.exception.code, core.PROCESSING)
        state = core.verify_case_integrity(image_case)
        self.assertTrue(all(page["route"] == "OCR_REQUIRED" for page in state["pages"]))
        self.assertEqual([path for path in (image_case / "work").rglob("*") if path.is_file()], [])
        with self.path(tools):
            route_code, _ = pipeline.route(str(image_case), None, "tester")
        self.assertEqual(route_code, core.PASS)

    def test_unsupported_input_is_inventory_review(self) -> None:
        source = self.source("notes.txt", b"inventory only")
        case = self.root / "case"
        code, result = pipeline.intake(
            str(case), "inventory-case", [str(source)], False, "INVENTORY", "deu,eng", "tester"
        )
        self.assertEqual(code, core.REVIEW)
        self.assertEqual(result["status"], "REVIEW")
        document = core.read_jsonl(core.case_paths(case)["documents"], core.DOCUMENT_SCHEMA)[0]
        self.assertFalse(document["processable"])
        self.assertEqual(document["support_status"], "INVENTORY_ONLY")

    def test_git_case_and_linked_input_are_denied(self) -> None:
        repository_case = PLUGIN_ROOT / "forbidden-case"
        with self.assertRaises(core.PaperworkError) as denied:
            core.validate_case_path(repository_case, must_exist=False)
        self.assertEqual(denied.exception.code, core.POLICY_DENIAL)

    def test_runtime_storage_and_recursive_home_ancestors_are_denied(self) -> None:
        codex_home = self.root / "codex-home"
        with mock.patch.dict(os.environ, {"CODEX_HOME": str(codex_home)}, clear=False):
            with self.assertRaises(core.PaperworkError) as case_denied:
                core.validate_case_path(codex_home / "plugins" / "cache" / "case", must_exist=False)
            self.assertEqual(case_denied.exception.code, core.POLICY_DENIAL)
            with self.assertRaises(core.PaperworkError) as output_denied:
                core.validate_output_path(
                    codex_home / "exports" / "case.paperwork.tar",
                    self.root / "outside-case",
                )
            self.assertEqual(output_denied.exception.code, core.POLICY_DENIAL)

        users = self.root / "users"
        fake_home = users / "alice"
        fake_home.mkdir(parents=True)
        self.source("users/shared.pdf", b"shared")
        with mock.patch.object(Path, "home", return_value=fake_home):
            with self.assertRaises(core.PaperworkError) as recursive_denied:
                pipeline._input_files([str(users)], True, self.root / "case")
        self.assertEqual(recursive_denied.exception.code, core.POLICY_DENIAL)

    def test_rejected_occupied_case_directory_keeps_its_mode(self) -> None:
        occupied = self.root / "occupied"
        occupied.mkdir(mode=0o755)
        occupied.chmod(0o755)
        (occupied / "keep.txt").write_text("owned by the user", encoding="utf-8")
        source = self.source("occupied-input.pdf", b"input")
        before = stat.S_IMODE(occupied.stat().st_mode)
        with self.assertRaises(core.PaperworkError) as denied:
            pipeline.intake(
                str(occupied), "occupied", [str(source)], False, "INVENTORY", "deu,eng", "tester"
            )
        self.assertEqual(denied.exception.code, core.POLICY_DENIAL)
        self.assertEqual(stat.S_IMODE(occupied.stat().st_mode), before)
        self.assertEqual((occupied / "keep.txt").read_text(encoding="utf-8"), "owned by the user")

        real = self.source("real.pdf", b"data")
        linked = self.root / "linked.pdf"
        linked.symlink_to(real)
        with self.assertRaises(core.PaperworkError) as denied:
            pipeline.intake(
                str(self.root / "case"), "link-case", [str(linked)], False, "INVENTORY", "deu,eng", "tester"
            )
        self.assertEqual(denied.exception.code, core.POLICY_DENIAL)

    def test_hard_linked_input_is_denied(self) -> None:
        real = self.source("real.pdf", b"data")
        linked = self.root / "hard.pdf"
        os.link(real, linked)
        with self.assertRaises(core.PaperworkError) as denied:
            pipeline.intake(
                str(self.root / "case"), "hard-case", [str(linked)], False, "INVENTORY", "deu,eng", "tester"
            )
        self.assertEqual(denied.exception.code, core.POLICY_DENIAL)

    def test_native_first_then_page_scoped_ocr_passes(self) -> None:
        tools = self.fake_tools()
        with self.path(tools):
            case, _ = self.new_case()
            extract_code, extract_result = pipeline.extract(str(case), None, "tester")
            route_code, route_result = pipeline.route(str(case), None, "tester")
            validate_code, validate_result = validation.validate(str(case), "tester")
        self.assertEqual(extract_code, core.REVIEW)
        self.assertEqual(len(extract_result["requires_routing"]), 1)
        self.assertEqual(route_code, core.PASS)
        self.assertEqual(len(route_result["routed"]), 1)
        pages = core.read_jsonl(core.case_paths(case)["pages"], core.PAGE_SCHEMA)
        self.assertEqual([page["route"] for page in pages], ["NATIVE", "OCR"])
        for directory in (path for path in (case / "work").rglob("*") if path.is_dir()):
            self.assertEqual(stat.S_IMODE(directory.stat().st_mode), 0o700, directory)
        for artifact in pages[1]["ocr_artifacts"]:
            self.assertEqual(stat.S_IMODE((case / artifact["path"]).stat().st_mode), 0o600)
        self.assertEqual(validate_code, core.PASS)
        self.assertEqual(validate_result["status"], "PASS")

    def test_low_confidence_ocr_routes_to_review(self) -> None:
        tools = self.fake_tools()
        with self.path(tools), mock.patch.dict(os.environ, {"FAKE_OCR_CONF": "25"}, clear=False):
            case, _ = self.new_case()
            pipeline.extract(str(case), None, "tester")
            code, result = pipeline.route(str(case), None, "tester")
        self.assertEqual(code, core.REVIEW)
        self.assertEqual(len(result["visual_review"]), 1)
        pages = core.read_jsonl(core.case_paths(case)["pages"], core.PAGE_SCHEMA)
        self.assertEqual(pages[1]["route"], "VISUAL_REVIEW")

    def test_ocr_timeout_routes_to_review(self) -> None:
        tools = self.fake_tools()
        with self.path(tools):
            case, _ = self.new_case()
            pipeline.extract(str(case), None, "tester")
            real_run = pipeline.run_tool

            def timeout_tesseract(arguments, timeout, text=False):
                if Path(arguments[0]).name == "tesseract" and "--list-langs" not in arguments:
                    raise core.PaperworkError("timeout", core.PROCESSING)
                return real_run(arguments, timeout, text=text)

            with mock.patch.object(pipeline, "run_tool", side_effect=timeout_tesseract):
                code, result = pipeline.route(str(case), None, "tester")
        self.assertEqual(code, core.REVIEW)
        self.assertEqual(len(result["visual_review"]), 1)

    def test_partial_or_malformed_ocr_routes_to_a_verifiable_review(self) -> None:
        tools = self.fake_tools()
        image = self.source("scan.png", b"synthetic-scan")
        case = self.root / "case"
        pipeline.intake(str(case), "partial-ocr", [str(image)], False, "EXTRACTION", "deu,eng", "tester")
        pipeline.extract(str(case), None, "tester")
        real_run = pipeline.run_tool

        def partial_tesseract(arguments, timeout, text=False):
            if Path(arguments[0]).name == "tesseract" and "--list-langs" not in arguments and "--version" not in arguments:
                base = Path(arguments[2])
                base.with_suffix(".txt").write_text("partial OCR text\n", encoding="utf-8")
                return subprocess.CompletedProcess(arguments, 1, stdout=b"", stderr=b"synthetic failure")
            return real_run(arguments, timeout, text=text)

        with self.path(tools), mock.patch.object(pipeline, "run_tool", side_effect=partial_tesseract):
            code, result = pipeline.route(str(case), None, "tester")
        self.assertEqual(code, core.REVIEW)
        self.assertEqual(len(result["visual_review"]), 1)
        state = core.verify_case_integrity(case)
        page = state["pages"][0]
        self.assertEqual(page["route"], "VISUAL_REVIEW")
        self.assertIsNone(page["ocr_page_dimensions"])
        self.assertEqual(len(page["ocr_artifacts"]), 1)
        self.assertEqual(stat.S_IMODE((case / page["ocr_artifacts"][0]["path"]).stat().st_mode), 0o600)

        malformed = self.root / "malformed.tsv"
        malformed.write_text(
            "level\tleft\ttop\twidth\theight\tconf\ttext\n"
            f"5\t{'9' * 5000}\t0\t1\t1\t99\tword\n",
            encoding="utf-8",
        )
        valid, confidence, dimensions = pipeline._tsv_metrics(malformed)
        self.assertFalse(valid)
        self.assertEqual(confidence, 0)
        self.assertIsNone(dimensions)

        truncated = self.root / "truncated.tsv"
        truncated.write_text(
            "level\tleft\ttop\twidth\theight\tconf\ttext\n5\t0\t0\t1\n",
            encoding="utf-8",
        )
        valid, confidence, dimensions = pipeline._tsv_metrics(truncated)
        self.assertFalse(valid)
        self.assertEqual(confidence, 0)
        self.assertIsNone(dimensions)

    def test_original_tamper_is_integrity_failure(self) -> None:
        case, _ = self.new_case("INVENTORY")
        document = core.read_jsonl(core.case_paths(case)["documents"], core.DOCUMENT_SCHEMA)[0]
        original = case / document["original"]
        original.chmod(0o600)
        original.write_bytes(b"tampered")
        with self.assertRaises(core.PaperworkError) as failure:
            core.verify_case_integrity(case)
        self.assertEqual(failure.exception.code, core.INTEGRITY)

    def test_case_lock_is_fail_closed(self) -> None:
        case, _ = self.new_case("INVENTORY")
        core.case_paths(case)["lock"].write_text("locked", encoding="utf-8")
        with self.assertRaises(core.PaperworkError) as failure:
            core.verify_case_integrity(case)
        self.assertEqual(failure.exception.code, core.CASE_LOCKED)

    def test_validation_is_invalidated_by_cli_mutation_and_manual_state_is_stale(self) -> None:
        case, _ = self.new_case("INVENTORY")
        code, _ = validation.validate(str(case), "tester")
        self.assertEqual(code, core.PASS)
        validation_path = core.case_paths(case)["validation"]
        self.assertTrue(validation_path.is_file())

        second = self.source("second.pdf", b"second-document")
        pipeline.intake(str(case), "case-2026", [str(second)], False, "INVENTORY", "deu,eng", "tester")
        self.assertFalse(validation_path.exists())
        with self.assertRaises(core.PaperworkError) as denied:
            validation.pack(str(case), str(self.root / "stale.paperwork.tar"), "evidence", "tester", True, False, None, None)
        self.assertEqual(denied.exception.code, core.POLICY_DENIAL)

        validation.validate(str(case), "tester")
        requirements = core.read_json(core.case_paths(case)["requirements"])
        requirements["required_claims"] = ["manual-change"]
        core.write_json(core.case_paths(case)["requirements"], requirements)
        with self.assertRaises(core.PaperworkError) as stale:
            core.verify_case_integrity(case)
        self.assertEqual(stale.exception.code, core.INTEGRITY)
        with self.assertRaises(core.PaperworkError) as pack_stale:
            validation.pack(str(case), str(self.root / "manual-stale.paperwork.tar"), "evidence", "tester", True, False, None, None)
        self.assertEqual(pack_stale.exception.code, core.INTEGRITY)

    def test_validation_result_and_version_are_bound_to_validate_audit_event(self) -> None:
        source = self.source("notes.txt", b"inventory only")
        case = self.root / "case"
        pipeline.intake(str(case), "review-case", [str(source)], False, "INVENTORY", "deu,eng", "tester")
        code, _ = validation.validate(str(case), "tester")
        self.assertEqual(code, core.REVIEW)
        validation_path = core.case_paths(case)["validation"]
        original = core.read_json(validation_path)
        variants = [
            {**original, "status": "PASS", "review_items": []},
            {**original, "validator_version": "99.0.0"},
        ]
        for mutated in variants:
            with self.subTest(mutated=mutated):
                payload = dict(mutated)
                payload.pop("digest", None)
                mutated["digest"] = core.canonical_digest(payload)
                core.write_json(validation_path, mutated)
                with self.assertRaises(core.PaperworkError) as failure:
                    core.verify_case_integrity(case)
                self.assertEqual(failure.exception.code, core.INTEGRITY)
                core.write_json(validation_path, original)

    def test_artifact_paths_reject_absolute_escape_and_mismatched_keys(self) -> None:
        case = self.native_case()
        paths = core.case_paths(case)
        original_pages = core.read_jsonl(paths["pages"], core.PAGE_SCHEMA)
        variants = [
            "/tmp/page.txt",
            "../page.txt",
            f"work/{'0' * 64}/final/page-0001.txt",
        ]
        for value in variants:
            with self.subTest(value=value):
                mutated = [dict(item) for item in original_pages]
                mutated[0]["final_artifact"] = value
                core.write_jsonl(paths["pages"], mutated)
                with self.assertRaises(core.PaperworkError) as failure:
                    core.verify_case_integrity(case)
                self.assertEqual(failure.exception.code, core.INTEGRITY)
                core.write_jsonl(paths["pages"], original_pages)

    def test_audit_requires_genesis_and_bound_head_count(self) -> None:
        case, _ = self.new_case("INVENTORY")
        audit_files = sorted((case / "audit").glob("*.json"))
        self.assertGreaterEqual(len(audit_files), 2)
        audit_files[-1].unlink()
        with self.assertRaises(core.PaperworkError) as truncated:
            core.verify_case_integrity(case)
        self.assertEqual(truncated.exception.code, core.INTEGRITY)

        second_source = self.source("empty-audit.pdf", b"empty-audit")
        second_case = self.root / "second-case"
        pipeline.intake(
            str(second_case), "second-case", [str(second_source)], False, "INVENTORY", "deu,eng", "tester"
        )
        for path in (second_case / "audit").glob("*.json"):
            path.unlink()
        with self.assertRaises(core.PaperworkError) as empty:
            core.verify_case_integrity(second_case)
        self.assertEqual(empty.exception.code, core.INTEGRITY)

    def test_case_created_at_is_bound_to_audit_genesis(self) -> None:
        case, _ = self.new_case("INVENTORY")
        case_path = core.case_paths(case)["case"]
        record = core.read_json(case_path)
        record["created_at"] = "2030-01-01T00:00:00Z"
        core.write_json(case_path, record)
        with self.assertRaises(core.PaperworkError) as failure:
            core.verify_case_integrity(case)
        self.assertEqual(failure.exception.code, core.INTEGRITY)

    def test_page_and_audit_bind_tool_and_language_provenance(self) -> None:
        tools = self.fake_tools()
        with self.path(tools):
            case, _ = self.new_case()
            pipeline.extract(str(case), None, "tester")
            pipeline.route(str(case), None, "tester")
        pages = core.read_jsonl(core.case_paths(case)["pages"], core.PAGE_SCHEMA)
        native = pages[0]["provenance"]
        self.assertEqual(set(native), {"pdfinfo", "pdftotext"})
        for record in native.values():
            self.assertEqual(core.sha256_file(Path(record["executable"])), record["executable_sha256"])
            self.assertTrue(record["argument_contract"])
        ocr = pages[1]["provenance"]["tesseract"]
        self.assertEqual([item["language"] for item in ocr["language_data"]], ["deu", "eng"])
        for item in ocr["language_data"]:
            self.assertEqual(core.sha256_file(Path(item["path"])), item["sha256"])
        latest_audit = core.read_json(sorted((case / "audit").glob("*.json"))[-1])
        self.assertIn("tesseract", latest_audit["details"]["tools"])

    def test_bad_quote_and_critical_claim_without_human_fail(self) -> None:
        case = self.native_case("CASEWORK")
        bad_claim = self.json_input(
            "bad-quote-claim.json",
            {
                "schema": core.CLAIM_SCHEMA,
                "id": "total",
                "name": "Total",
                "value": "100.00",
                "critical": True,
                "anchors": [self.page_anchor(case, "not present")],
            },
        )
        with self.assertRaises(core.PaperworkError) as bad_quote:
            casework.add_claim(str(case), str(bad_claim), "tester")
        self.assertEqual(bad_quote.exception.code, core.INVALID)
        claim = self.json_input(
            "critical-claim.json",
            {
                "schema": core.CLAIM_SCHEMA,
                "id": "total",
                "name": "Total",
                "value": "100.00",
                "critical": True,
                "anchors": [self.page_anchor(case, "total 100.00")],
            },
        )
        casework.add_claim(str(case), str(claim), "tester")
        code, result = validation.validate(str(case), "tester")
        self.assertEqual(code, core.VALIDATION_FAILED)
        self.assertTrue(any("lacks human confirmation" in issue for issue in result["issues"]))

    def test_decimal_sum_and_date_order_fail_without_eval(self) -> None:
        case = self.native_case("CASEWORK")
        anchor = self.page_anchor(case, "invoice")
        values = {
            "part-a": "40.00",
            "part-b": "50.00",
            "total": "100.00",
            "before": "2026-02-01",
            "after": "2026-01-01",
        }
        for claim_id, value in values.items():
            claim = self.json_input(
                f"{claim_id}.json",
                {
                    "schema": core.CLAIM_SCHEMA,
                    "id": claim_id,
                    "name": claim_id,
                    "value": value,
                    "critical": False,
                    "anchors": [anchor],
                },
            )
            casework.add_claim(str(case), str(claim), "tester")
        requirements = self.json_input(
            "failing-rules.json",
            {
                "schema": core.REQUIREMENTS_SCHEMA,
                "required_documents": [],
                "required_claims": [],
                "rules": [
                    {"id": "sum", "type": "decimal_sum", "terms": ["part-a", "part-b"], "total": "total", "tolerance": "0.00"},
                    {"id": "dates", "type": "date_order", "before": "before", "after": "after"},
                ],
            },
        )
        casework.set_requirements(str(case), str(requirements), "tester")
        code, result = validation.validate(str(case), "tester")
        self.assertEqual(code, core.VALIDATION_FAILED)
        self.assertEqual(
            result["issues"],
            ["validation rule failed: dates", "validation rule failed: sum"],
        )

    def test_decimal_sum_uses_exact_fixed_point_arithmetic(self) -> None:
        requirements = {
            "required_documents": [],
            "required_claims": [],
            "rules": [
                {
                    "id": "exact-sum",
                    "type": "decimal_sum",
                    "terms": ["a", "b"],
                    "total": "total",
                    "tolerance": "0",
                }
            ],
        }
        claims = {
            "a": {"value": "10000000000000000000000000000"},
            "b": {"value": "1"},
            "total": {"value": "10000000000000000000000000000"},
        }
        self.assertEqual(
            validation._validate_rules(requirements, [], claims),
            ["validation rule failed: exact-sum"],
        )

    def test_required_document_rule_rejects_empty_selector(self) -> None:
        case = self.native_case("CASEWORK")
        requirements = self.json_input(
            "empty-document-selector.json",
            {
                "schema": core.REQUIREMENTS_SCHEMA,
                "required_documents": [],
                "required_claims": [],
                "rules": [{"id": "document", "type": "required_document", "sha256": ""}],
            },
        )
        with self.assertRaises(core.PaperworkError) as failure:
            casework.set_requirements(str(case), str(requirements), "tester")
        self.assertEqual(failure.exception.code, core.INVALID)

    def test_casework_succeeds_through_safe_requirements_claim_and_approval_commands(self) -> None:
        case = self.native_case("CASEWORK")
        requirements = self.json_input(
            "requirements-input.json",
            {
                "schema": core.REQUIREMENTS_SCHEMA,
                "required_documents": [],
                "required_claims": ["total"],
                "rules": [{"id": "currency", "type": "format", "claim": "total", "format": "currency"}],
            },
        )
        claim = self.json_input(
            "claim-input.json",
            {
                "schema": core.CLAIM_SCHEMA,
                "id": "total",
                "name": "Total",
                "value": "100.00",
                "critical": True,
                "anchors": [self.page_anchor(case, "total 100.00")],
            },
        )
        bad_approval = self.json_input(
            "bad-approval.json",
            {
                "schema": core.APPROVAL_SCHEMA,
                "id": "total-confirmation",
                "human": True,
                "approved_by": "codex",
                "scope_type": "claim",
                "scope_id": "total",
                "decision": "CONFIRMED",
                "note": "A declared human must be named.",
            },
        )
        approval = self.json_input(
            "approval-input.json",
            {
                "schema": core.APPROVAL_SCHEMA,
                "id": "total-confirmation",
                "human": True,
                "approved_by": "Human Reviewer",
                "scope_type": "claim",
                "scope_id": "total",
                "decision": "CONFIRMED",
                "note": "I checked the source page and confirm this claim.",
            },
        )
        casework.set_requirements(str(case), str(requirements), "tester")
        casework.add_claim(str(case), str(claim), "tester")
        with self.assertRaises(core.PaperworkError) as denied:
            casework.add_approval(str(case), str(bad_approval), "tester")
        self.assertEqual(denied.exception.code, core.POLICY_DENIAL)
        casework.add_approval(str(case), str(approval), "tester")
        code, result = validation.validate(str(case), "tester")
        self.assertEqual(code, core.PASS)
        self.assertEqual(result["status"], "PASS")
        actions = [core.read_json(path)["action"] for path in sorted((case / "audit").glob("*.json"))]
        self.assertIn("REQUIREMENTS_SET", actions)
        self.assertIn("CLAIM_UPSERT", actions)
        self.assertIn("APPROVAL_UPSERT", actions)

    def test_claim_replacement_invalidates_prior_human_approval(self) -> None:
        case = self.native_case("CASEWORK")
        claim_path = self.json_input(
            "claim.json",
            {
                "schema": core.CLAIM_SCHEMA,
                "id": "total",
                "name": "Total",
                "value": "100.00",
                "critical": True,
                "anchors": [self.page_anchor(case, "total 100.00")],
            },
        )
        approval_path = self.json_input(
            "approval.json",
            {
                "schema": core.APPROVAL_SCHEMA,
                "id": "total-confirmation",
                "human": True,
                "approved_by": "Human Reviewer",
                "scope_type": "claim",
                "scope_id": "total",
                "decision": "CONFIRMED",
                "note": "Confirmed against the source page.",
            },
        )
        casework.add_claim(str(case), str(claim_path), "tester")
        casework.add_approval(str(case), str(approval_path), "tester")
        code, _ = validation.validate(str(case), "tester")
        self.assertEqual(code, core.PASS)

        replacement = core.read_json(claim_path)
        replacement["value"] = "101.00"
        core.write_json(claim_path, replacement)
        casework.add_claim(str(case), str(claim_path), "tester")
        code, result = validation.validate(str(case), "tester")
        self.assertEqual(code, core.VALIDATION_FAILED)
        self.assertIn("critical claim total lacks human confirmation", result["issues"])

    def test_non_finite_numbers_are_rejected_as_controlled_input_errors(self) -> None:
        case = self.native_case("CASEWORK")
        requirements = self.json_input(
            "infinite-requirements.json",
            {
                "schema": core.REQUIREMENTS_SCHEMA,
                "required_documents": [],
                "required_claims": [],
                "rules": [
                    {
                        "id": "sum",
                        "type": "decimal_sum",
                        "terms": ["part"],
                        "total": "total",
                        "tolerance": "Infinity",
                    }
                ],
            },
        )
        with self.assertRaises(core.PaperworkError) as infinite:
            casework.set_requirements(str(case), str(requirements), "tester")
        self.assertEqual(infinite.exception.code, core.INVALID)

        tools = self.fake_tools()
        with self.path(tools):
            ocr_source = self.source("ocr-input.pdf", b"ocr-pdf")
            ocr_case = self.root / "ocr-case"
            pipeline.intake(
                str(ocr_case), "ocr-case", [str(ocr_source)], False, "CASEWORK", "deu,eng", "tester"
            )
            pipeline.extract(str(ocr_case), None, "tester")
            pipeline.route(str(ocr_case), None, "tester")
        claim = self.json_input(
            "nan-bbox-claim.json",
            {
                "schema": core.CLAIM_SCHEMA,
                "id": "ocr-total",
                "name": "OCR total",
                "value": "100.00",
                "critical": False,
                "anchors": [
                    self.page_anchor(
                        ocr_case,
                        "OCR invoice total 100.00",
                        method="OCR",
                        bbox=["NaN", "0.100000", "0.450000", "0.120000"],
                    )
                ],
            },
        )
        with self.assertRaises(core.PaperworkError) as nan:
            casework.add_claim(str(ocr_case), str(claim), "tester")
        self.assertEqual(nan.exception.code, core.INVALID)

    def test_hostile_json_types_remain_controlled_errors(self) -> None:
        case = self.native_case("CASEWORK")
        huge = self.root / "huge.json"
        huge.write_text(
            '{"schema":"godmode.paperwork.requirements/v1","required_documents":[],"required_claims":[],"rules":[],"extra":'
            + "9" * 5000
            + "}",
            encoding="utf-8",
        )
        with self.assertRaises(core.PaperworkError) as huge_failure:
            casework.set_requirements(str(case), str(huge), "tester")
        self.assertEqual(huge_failure.exception.code, core.INVALID)

        duplicate = self.root / "duplicate.json"
        duplicate.write_text(
            '{"schema":"godmode.paperwork.requirements/v1","schema":"godmode.paperwork.requirements/v1",'
            '"required_documents":[],"required_claims":[],"rules":[]}',
            encoding="utf-8",
        )
        with self.assertRaises(core.PaperworkError) as duplicate_failure:
            casework.set_requirements(str(case), str(duplicate), "tester")
        self.assertEqual(duplicate_failure.exception.code, core.INVALID)

        surrogate = self.root / "surrogate.json"
        surrogate.write_bytes(
            b'{"schema":"godmode.paperwork.requirements/v1","required_documents":[],'
            b'"required_claims":["\\ud800"],"rules":[]}'
        )
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "paperwork.py"),
                "--json",
                "requirements",
                "--case",
                str(case),
                "--input",
                str(surrogate),
                "--actor",
                "tester",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, core.INVALID)
        self.assertEqual(json.loads(result.stdout)["exit_code"], core.INVALID)

        with self.assertRaises(core.PaperworkError) as normalized_key_collision:
            core.parse_json_bytes('{"é":1,"e\\u0301":2}'.encode("utf-8"), "normalization collision")
        self.assertEqual(normalized_key_collision.exception.code, core.INVALID)

        bad_requirements = self.json_input(
            "bad-types-requirements.json",
            {
                "schema": core.REQUIREMENTS_SCHEMA,
                "required_documents": [],
                "required_claims": [[]],
                "rules": [],
            },
        )
        with self.assertRaises(core.PaperworkError) as requirement_failure:
            casework.set_requirements(str(case), str(bad_requirements), "tester")
        self.assertEqual(requirement_failure.exception.code, core.INVALID)

        bad_claim = self.json_input(
            "bad-types-claim.json",
            {
                "schema": core.CLAIM_SCHEMA,
                "id": "bad-anchor",
                "name": "Bad anchor",
                "value": "x",
                "critical": False,
                "anchors": [
                    {
                        "document": [],
                        "page": {},
                        "quote": "invoice",
                        "artifact_sha256": "0" * 64,
                        "method": [],
                    }
                ],
            },
        )
        with self.assertRaises(core.PaperworkError) as claim_failure:
            casework.add_claim(str(case), str(bad_claim), "tester")
        self.assertEqual(claim_failure.exception.code, core.INVALID)

        bad_approval = self.json_input(
            "bad-types-approval.json",
            {
                "schema": core.APPROVAL_SCHEMA,
                "id": "bad-scope",
                "human": True,
                "approved_by": "Human Reviewer",
                "scope_type": "claim",
                "scope_id": [],
                "decision": "CONFIRMED",
                "note": "Invalid structured scope.",
            },
        )
        with self.assertRaises(core.PaperworkError) as approval_failure:
            casework.add_approval(str(case), str(bad_approval), "tester")
        self.assertEqual(approval_failure.exception.code, core.INVALID)

        for field in ("scope_type", "decision"):
            with self.subTest(approval_field=field):
                structured_approval = core.read_json(bad_approval)
                structured_approval["scope_id"] = "missing"
                structured_approval[field] = []
                path = self.json_input(f"bad-{field}.json", structured_approval)
                with self.assertRaises(core.PaperworkError) as structured_failure:
                    casework.add_approval(str(case), str(path), "tester")
                self.assertEqual(structured_failure.exception.code, core.INVALID)

    def test_non_object_integrity_files_fail_with_integrity_exit(self) -> None:
        case, _ = self.new_case("INVENTORY")
        core.atomic_write(core.case_paths(case)["case"], core.canonical_bytes([]))
        with self.assertRaises(core.PaperworkError) as case_failure:
            core.verify_case_integrity(case)
        self.assertEqual(case_failure.exception.code, core.INTEGRITY)

        source = self.source("second-case.pdf", b"second-case")
        second_case = self.root / "second-case"
        pipeline.intake(
            str(second_case), "second-case", [str(source)], False, "INVENTORY", "deu,eng", "tester"
        )
        core.atomic_write(core.case_paths(second_case)["requirements"], core.canonical_bytes([]))
        with self.assertRaises(core.PaperworkError) as requirements_failure:
            core.verify_case_integrity(second_case)
        self.assertEqual(requirements_failure.exception.code, core.INTEGRITY)

    def test_hostile_integrity_record_types_fail_with_integrity_exit(self) -> None:
        case, _ = self.new_case("INVENTORY")
        document_path = core.case_paths(case)["documents"]
        documents = core.read_jsonl(document_path, core.DOCUMENT_SCHEMA)
        documents[0]["source_names"] = [[]]
        core.write_jsonl(document_path, documents)
        with self.assertRaises(core.PaperworkError) as alias_failure:
            core.verify_case_integrity(case)
        self.assertEqual(alias_failure.exception.code, core.INTEGRITY)

        tools = self.fake_tools()
        ocr_source = self.source("hostile-ocr.png", b"hostile-ocr")
        ocr_case = self.root / "hostile-ocr-case"
        pipeline.intake(
            str(ocr_case), "hostile-ocr-case", [str(ocr_source)], False, "EXTRACTION", "deu,eng", "tester"
        )
        pipeline.extract(str(ocr_case), None, "tester")
        with self.path(tools):
            pipeline.route(str(ocr_case), None, "tester")
        page_path = core.case_paths(ocr_case)["pages"]
        pages = core.read_jsonl(page_path, core.PAGE_SCHEMA)
        pages[0]["ocr_artifacts"][0]["path"] = []
        core.write_jsonl(page_path, pages)
        with self.assertRaises(core.PaperworkError) as artifact_failure:
            core.verify_case_integrity(ocr_case)
        self.assertEqual(artifact_failure.exception.code, core.INTEGRITY)

        route_source = self.source("hostile-route.png", b"hostile-route")
        route_case = self.root / "hostile-route-case"
        pipeline.intake(
            str(route_case), "hostile-route-case", [str(route_source)], False, "EXTRACTION", "deu,eng", "tester"
        )
        pipeline.extract(str(route_case), None, "tester")
        route_page_path = core.case_paths(route_case)["pages"]
        route_pages = core.read_jsonl(route_page_path, core.PAGE_SCHEMA)
        route_pages[0]["route"] = []
        core.write_jsonl(route_page_path, route_pages)
        with self.assertRaises(core.PaperworkError) as route_failure:
            core.verify_case_integrity(route_case)
        self.assertEqual(route_failure.exception.code, core.INTEGRITY)

    def test_ocr_claim_bbox_is_derived_from_tsv_and_mismatch_is_rejected(self) -> None:
        tools = self.fake_tools()
        with self.path(tools):
            case, _ = self.new_case("CASEWORK")
            pipeline.extract(str(case), None, "tester")
            pipeline.route(str(case), None, "tester")
        claim = self.json_input(
            "ocr-claim.json",
            {
                "schema": core.CLAIM_SCHEMA,
                "id": "ocr-total",
                "name": "OCR total",
                "value": "100.00",
                "critical": False,
                "anchors": [self.page_anchor(case, "OCR invoice total 100.00", method="OCR")],
            },
        )
        casework.add_claim(str(case), str(claim), "tester")
        stored = core.read_jsonl(core.case_paths(case)["claims"], core.CLAIM_SCHEMA)[0]
        self.assertEqual(stored["anchors"][0]["bbox"], ["0.100000", "0.100000", "0.450000", "0.120000"])

        mismatch = self.json_input(
            "ocr-mismatch.json",
            {
                "schema": core.CLAIM_SCHEMA,
                "id": "ocr-mismatch",
                "name": "OCR mismatch",
                "value": "100.00",
                "critical": False,
                "anchors": [
                    self.page_anchor(
                        case,
                        "OCR invoice total 100.00",
                        method="OCR",
                        bbox=["0.000000", "0.000000", "1.000000", "1.000000"],
                    )
                ],
            },
        )
        with self.assertRaises(core.PaperworkError) as failure:
            casework.add_claim(str(case), str(mismatch), "tester")
        self.assertEqual(failure.exception.code, core.INVALID)

    def test_visual_page_resolution_uses_safe_command_and_resolves_queue(self) -> None:
        tools = self.fake_tools()
        with self.path(tools), mock.patch.dict(os.environ, {"FAKE_OCR_CONF": "25"}, clear=False):
            case, _ = self.new_case("CASEWORK")
            pipeline.extract(str(case), None, "tester")
            pipeline.route(str(case), None, "tester")
        page = core.read_jsonl(core.case_paths(case)["pages"], core.PAGE_SCHEMA)[1]
        resolution = self.json_input(
            "resolution-input.json",
            {
                "schema": core.PAGE_RESOLUTION_SCHEMA,
                "document": page["document"],
                "page": page["page"],
                "text": "Visually confirmed invoice total 100.00",
                "bbox": ["0.10", "0.20", "0.90", "0.80"],
                "confirmed_by": "Human Reviewer",
                "note": "Compared the rendered page with the original.",
            },
        )
        code, _ = casework.resolve_page(str(case), str(resolution), "tester")
        self.assertEqual(code, core.PASS)
        resolved_page = core.read_jsonl(core.case_paths(case)["pages"], core.PAGE_SCHEMA)[1]
        self.assertEqual(resolved_page["route"], "VISUAL")
        self.assertEqual(resolved_page["visual_resolution"]["declared_by"], "Human Reviewer")
        reviews = core.read_jsonl(core.case_paths(case)["reviews"], core.REVIEW_SCHEMA)
        self.assertTrue(all(item["status"] == "RESOLVED" for item in reviews))

    def test_visual_resolution_cannot_bypass_ocr_escalation(self) -> None:
        tools = self.fake_tools()
        with self.path(tools):
            case, _ = self.new_case("CASEWORK")
            pipeline.extract(str(case), None, "tester")
        page = core.read_jsonl(core.case_paths(case)["pages"], core.PAGE_SCHEMA)[1]
        self.assertEqual(page["route"], "OCR_REQUIRED")
        resolution = self.json_input(
            "premature-resolution.json",
            {
                "schema": core.PAGE_RESOLUTION_SCHEMA,
                "document": page["document"],
                "page": page["page"],
                "text": "Premature visual resolution",
                "bbox": ["0.10", "0.20", "0.90", "0.80"],
                "confirmed_by": "Human Reviewer",
                "note": "This must not bypass the local OCR attempt.",
            },
        )
        with self.assertRaises(core.PaperworkError) as denied:
            casework.resolve_page(str(case), str(resolution), "tester")
        self.assertEqual(denied.exception.code, core.POLICY_DENIAL)

    def test_review_pack_requires_human_gate_and_is_deterministic(self) -> None:
        source = self.source("notes.txt", b"inventory only")
        case = self.root / "case"
        pipeline.intake(str(case), "review-case", [str(source)], False, "INVENTORY", "deu,eng", "tester")
        validate_code, _ = validation.validate(str(case), "tester")
        self.assertEqual(validate_code, core.REVIEW)
        with self.assertRaises(core.PaperworkError) as denied:
            validation.pack(str(case), str(self.root / "denied.paperwork.tar"), "evidence", "tester", True, False, None, None)
        self.assertEqual(denied.exception.code, core.POLICY_DENIAL)

        note = self.source("approval.txt", b"Reviewed by the responsible human.")
        outputs = [self.root / "first.paperwork.tar", self.root / "second.paperwork.tar"]
        for output in outputs:
            code, _ = validation.pack(
                str(case), str(output), "evidence", "tester", True, True, "Human Reviewer", str(note)
            )
            self.assertEqual(code, core.REVIEW)
            verify_code, verify_result = validation.verify_pack(str(output))
            self.assertEqual(verify_code, core.REVIEW)
            self.assertEqual(verify_result["integrity_status"], "PASS")
            self.assertEqual(verify_result["validation_status"], "REVIEW")
            self.assertFalse(verify_result["ready_for_release"])
            with tarfile.open(output, "r:") as archive:
                self.assertEqual(archive.extractfile("PACK-APPROVAL-NOTE.txt").read(), note.read_bytes())
            receipt = core.read_json(Path(f"{output}.receipt.json"))
            self.assertTrue(receipt["approval"]["declared_human"])
        self.assertEqual(outputs[0].read_bytes(), outputs[1].read_bytes())
        self.assertEqual(core.sha256_file(outputs[0]), core.sha256_file(outputs[1]))

    def test_pack_streams_case_members_and_preserves_existing_output_directory_mode(self) -> None:
        case, _ = self.new_case("INVENTORY")
        validation.validate(str(case), "tester")
        export_dir = self.root / "existing-exports"
        export_dir.mkdir(mode=0o755)
        export_dir.chmod(0o755)
        output = export_dir / "streamed.paperwork.tar"
        with mock.patch.object(Path, "read_bytes", side_effect=AssertionError("pack must stream case members")):
            code, _ = validation.pack(str(case), str(output), "full", "tester", True, False, None, None)
        self.assertEqual(code, core.PASS)
        self.assertEqual(stat.S_IMODE(export_dir.stat().st_mode), 0o755)
        self.assertTrue(output.is_file())

    def test_evidence_pack_contains_a_self_verifiable_complete_case(self) -> None:
        case = self.native_case("EXTRACTION")
        validation.validate(str(case), "tester")
        output = self.root / "complete.paperwork.tar"
        code, _ = validation.pack(str(case), str(output), "evidence", "tester", True, False, None, None)
        self.assertEqual(code, core.PASS)
        extracted = self.root / "extracted"
        with tarfile.open(output, "r:") as archive:
            for member in archive.getmembers():
                target = extracted / member.name
                target.parent.mkdir(parents=True, exist_ok=True)
                handle = archive.extractfile(member)
                self.assertIsNotNone(handle)
                target.write_bytes(handle.read())
        state = core.verify_case_integrity(extracted / "case")
        self.assertEqual(state["case"]["case_id"], "case-2026")
        self.assertTrue(any(path.name.endswith(".txt") for path in (extracted / "case" / "work").rglob("*")))

    def test_verify_pack_rejects_manifest_consistent_but_incomplete_case(self) -> None:
        case, _ = self.new_case("INVENTORY")
        validation.validate(str(case), "tester")
        valid = self.root / "complete-source.paperwork.tar"
        forged = self.root / "incomplete.paperwork.tar"
        validation.pack(str(case), str(valid), "evidence", "tester", True, False, None, None)
        self.forge_pack(valid, forged, drop_prefixes=("case/originals/", "case/audit/"))
        with self.assertRaises(core.PaperworkError) as failure:
            validation.verify_pack(str(forged))
        self.assertEqual(failure.exception.code, core.INTEGRITY)

    def test_verify_pack_rejects_payload_after_canonical_tar_end(self) -> None:
        case, _ = self.new_case("INVENTORY")
        validation.validate(str(case), "tester")
        valid = self.root / "canonical-source.paperwork.tar"
        forged = self.root / "trailing-payload.paperwork.tar"
        validation.pack(str(case), str(valid), "evidence", "tester", True, False, None, None)
        self.forge_pack(valid, forged, trailing=b"UNMANIFESTED-SECRET-PAYLOAD")
        with self.assertRaises(core.PaperworkError) as failure:
            validation.verify_pack(str(forged))
        self.assertEqual(failure.exception.code, core.INTEGRITY)

    def test_verify_pack_rejects_integer_digest_fields(self) -> None:
        case, _ = self.new_case("INVENTORY")
        validation.validate(str(case), "tester")
        valid = self.root / "digest-source.paperwork.tar"
        forged = self.root / "integer-digests.paperwork.tar"
        validation.pack(str(case), str(valid), "evidence", "tester", True, False, None, None)

        def integer_digests(manifest):
            for field in ("validation_digest", "state_digest", "audit_head_sha256"):
                manifest[field] = int("1" * 64)

        self.forge_pack(valid, forged, mutate_manifest=integer_digests)
        with self.assertRaises(core.PaperworkError) as failure:
            validation.verify_pack(str(forged))
        self.assertEqual(failure.exception.code, core.INTEGRITY)

    def test_verify_pack_rejects_unhashable_contract_fields(self) -> None:
        case, _ = self.new_case("INVENTORY")
        validation.validate(str(case), "tester")
        valid = self.root / "unhashable-source.paperwork.tar"
        validation.pack(str(case), str(valid), "evidence", "tester", True, False, None, None)

        receipt_path = Path(f"{valid}.receipt.json")
        receipt = core.read_json(receipt_path)
        forged_receipt = dict(receipt)
        forged_receipt["contents"] = []
        core.write_json(receipt_path, forged_receipt)
        with self.assertRaises(core.PaperworkError) as receipt_failure:
            validation.verify_pack(str(valid))
        self.assertEqual(receipt_failure.exception.code, core.INTEGRITY)
        core.write_json(receipt_path, receipt)

        status_forged = self.root / "unhashable-status.paperwork.tar"

        def structured_status(manifest):
            manifest["validation_status"] = {}

        self.forge_pack(valid, status_forged, mutate_manifest=structured_status)
        status_receipt_path = Path(f"{status_forged}.receipt.json")
        status_receipt = core.read_json(status_receipt_path)
        status_receipt["validation_status"] = "PASS"
        core.write_json(status_receipt_path, status_receipt)
        with self.assertRaises(core.PaperworkError) as status_failure:
            validation.verify_pack(str(status_forged))
        self.assertEqual(status_failure.exception.code, core.INTEGRITY)

        mode_forged = self.root / "unhashable-mode.paperwork.tar"

        def structured_mode(manifest):
            manifest["entries"][0]["mode"] = []

        self.forge_pack(valid, mode_forged, mutate_manifest=structured_mode)
        with self.assertRaises(core.PaperworkError) as mode_failure:
            validation.verify_pack(str(mode_forged))
        self.assertEqual(mode_failure.exception.code, core.INTEGRITY)

    def test_verify_pack_requires_review_approval_and_note(self) -> None:
        source = self.source("review-only.txt", b"review")
        case = self.root / "review-contract-case"
        pipeline.intake(
            str(case), "review-contract-case", [str(source)], False, "INVENTORY", "deu,eng", "tester"
        )
        validation.validate(str(case), "tester")
        note = self.source("review-contract-note.txt", b"Confirmed by the responsible human.")
        valid = self.root / "review-source.paperwork.tar"
        forged = self.root / "review-without-gate.paperwork.tar"
        validation.pack(
            str(case), str(valid), "evidence", "tester", True, True, "Human Reviewer", str(note)
        )

        def remove_gate(manifest):
            manifest["approval"] = None

        self.forge_pack(
            valid,
            forged,
            drop_prefixes=("PACK-APPROVAL-NOTE.txt",),
            mutate_manifest=remove_gate,
        )
        with self.assertRaises(core.PaperworkError) as failure:
            validation.verify_pack(str(forged))
        self.assertEqual(failure.exception.code, core.INTEGRITY)

    def test_verify_pack_works_from_read_only_directory(self) -> None:
        case, _ = self.new_case("INVENTORY")
        validation.validate(str(case), "tester")
        directory = self.root / "read-only-pack"
        directory.mkdir()
        output = directory / "case.paperwork.tar"
        validation.pack(str(case), str(output), "evidence", "tester", True, False, None, None)
        files = [output, Path(f"{output}.sha256"), Path(f"{output}.receipt.json")]
        try:
            for path in files:
                path.chmod(0o444)
            directory.chmod(0o555)
            code, result = validation.verify_pack(str(output))
            self.assertEqual(code, core.PASS)
            self.assertTrue(result["ready_for_release"])
        finally:
            directory.chmod(0o755)
            for path in files:
                path.chmod(0o644)

    def test_pack_sidecar_publication_failure_cleans_all_outputs(self) -> None:
        case, _ = self.new_case("INVENTORY")
        validation.validate(str(case), "tester")
        export_dir = self.root / "failed-exports"
        export_dir.mkdir()
        output = export_dir / "failed.paperwork.tar"
        real_link = os.link
        calls = 0

        def fail_second_link(source, destination):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError("synthetic receipt publication failure")
            return real_link(source, destination)

        with mock.patch.object(validation.os, "link", side_effect=fail_second_link):
            with self.assertRaises(OSError):
                validation.pack(str(case), str(output), "evidence", "tester", True, False, None, None)
        self.assertEqual(list(export_dir.iterdir()), [])

    def test_pack_keyboard_interrupt_cleans_partial_publication(self) -> None:
        case, _ = self.new_case("INVENTORY")
        validation.validate(str(case), "tester")
        export_dir = self.root / "interrupted-exports"
        export_dir.mkdir()
        output = export_dir / "interrupt.paperwork.tar"
        real_link = os.link
        calls = 0

        def interrupt_second_link(source, destination):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise KeyboardInterrupt()
            return real_link(source, destination)

        with mock.patch.object(validation.os, "link", side_effect=interrupt_second_link):
            with self.assertRaises(KeyboardInterrupt):
                validation.pack(str(case), str(output), "evidence", "tester", True, False, None, None)
        self.assertEqual(list(export_dir.iterdir()), [])

    def test_pack_rejects_case_member_swap_after_validation(self) -> None:
        case, _ = self.new_case("INVENTORY")
        validation.validate(str(case), "tester")
        requirements_path = core.case_paths(case)["requirements"]
        original = requirements_path.read_bytes()
        real_case_files = validation._case_files

        def mutate_after_snapshot(root, contents):
            files = real_case_files(root, contents)
            forged = core.read_json(requirements_path)
            forged["required_claims"] = ["forged"]
            core.write_json(requirements_path, forged)
            return files

        output = self.root / "swap.paperwork.tar"
        try:
            with mock.patch.object(validation, "_case_files", side_effect=mutate_after_snapshot):
                with self.assertRaises(core.PaperworkError) as failure:
                    validation.pack(str(case), str(output), "evidence", "tester", True, False, None, None)
            self.assertEqual(failure.exception.code, core.INTEGRITY)
        finally:
            core.atomic_write(requirements_path, original)
        core.verify_case_integrity(case)
        self.assertFalse(output.exists())

    def test_verify_pack_rejects_archive_path_swap_during_verification(self) -> None:
        case, _ = self.new_case("INVENTORY")
        validation.validate(str(case), "tester")
        first = self.root / "first-swap.paperwork.tar"
        second = self.root / "second-swap.paperwork.tar"
        validation.pack(str(case), str(first), "evidence", "first-actor", True, False, None, None)
        validation.pack(str(case), str(second), "evidence", "second-actor", True, False, None, None)
        real_tar_open = validation.tarfile.open
        swapped = False

        def swap_path(*args, **kwargs):
            nonlocal swapped
            if not swapped:
                swapped = True
                os.replace(second, first)
            return real_tar_open(*args, **kwargs)

        with mock.patch.object(validation.tarfile, "open", side_effect=swap_path):
            with self.assertRaises(core.PaperworkError) as failure:
                validation.verify_pack(str(first))
        self.assertEqual(failure.exception.code, core.INTEGRITY)

    def test_verify_pack_rejects_in_place_archive_change_during_verification(self) -> None:
        case, _ = self.new_case("INVENTORY")
        validation.validate(str(case), "tester")
        output = self.root / "in-place.paperwork.tar"
        validation.pack(str(case), str(output), "evidence", "tester", True, False, None, None)
        real_tar_open = validation.tarfile.open
        changed = False

        def mutate_inode(*args, **kwargs):
            nonlocal changed
            if not changed:
                changed = True
                with output.open("r+b") as handle:
                    first = handle.read(1)
                    handle.seek(0)
                    handle.write(bytes([first[0] ^ 1]))
                    handle.flush()
                    os.fsync(handle.fileno())
            return real_tar_open(*args, **kwargs)

        with mock.patch.object(validation.tarfile, "open", side_effect=mutate_inode):
            with self.assertRaises(core.PaperworkError) as failure:
                validation.verify_pack(str(output))
        self.assertEqual(failure.exception.code, core.INTEGRITY)

    def test_pack_receipt_common_fields_are_bound_to_manifest(self) -> None:
        case, _ = self.new_case("INVENTORY")
        validation.validate(str(case), "tester")
        output = self.root / "bound.paperwork.tar"
        validation.pack(str(case), str(output), "evidence", "tester", True, False, None, None)
        receipt_path = Path(f"{output}.receipt.json")
        original = core.read_json(receipt_path)
        variants = {
            "case_id": "forged-case",
            "contents": "full",
            "actor": "forged-actor",
            "validation_status": "REVIEW",
            "validation_digest": "f" * 64,
            "state_digest": "e" * 64,
            "audit_head_sha256": "d" * 64,
            "audit_count": original["audit_count"] + 1,
            "approval": {
                "approved_by": "Forger",
                "declared_human": True,
                "note_path": "PACK-APPROVAL-NOTE.txt",
                "note_sha256": "c" * 64,
            },
        }
        for field, value in variants.items():
            with self.subTest(field=field):
                forged = dict(original)
                forged[field] = value
                core.write_json(receipt_path, forged)
                with self.assertRaises(core.PaperworkError) as failure:
                    validation.verify_pack(str(output))
                self.assertEqual(failure.exception.code, core.INTEGRITY)
                core.write_json(receipt_path, original)
        receipt_path.write_text(json.dumps(original, indent=2), encoding="utf-8")
        with self.assertRaises(core.PaperworkError) as noncanonical:
            validation.verify_pack(str(output))
        self.assertEqual(noncanonical.exception.code, core.INTEGRITY)
        core.write_json(receipt_path, original)

    def test_verify_case_reports_validation_readiness(self) -> None:
        missing_case, _ = self.new_case("INVENTORY")
        code, result = validation.verify_case(str(missing_case))
        self.assertEqual((code, result["status"], result["validation_status"], result["ready_for_pack"]), (core.REVIEW, "REVIEW", "MISSING", False))
        validation.validate(str(missing_case), "tester")
        code, result = validation.verify_case(str(missing_case))
        self.assertEqual((code, result["status"], result["validation_status"], result["ready_for_pack"]), (core.PASS, "PASS", "PASS", True))

        review_source = self.source("review.txt", b"inventory review")
        review_case = self.root / "review-case"
        pipeline.intake(str(review_case), "review-case", [str(review_source)], False, "INVENTORY", "deu,eng", "tester")
        validation.validate(str(review_case), "tester")
        code, result = validation.verify_case(str(review_case))
        self.assertEqual((code, result["status"], result["validation_status"], result["ready_for_pack"]), (core.REVIEW, "REVIEW", "REVIEW", False))

        tools = self.fake_tools()
        fail_source = self.source("fail.pdf", b"failing-case")
        fail_case = self.root / "fail-case"
        with self.path(tools), mock.patch.dict(os.environ, {"FAKE_PAGES": "1"}, clear=False):
            pipeline.intake(
                str(fail_case), "fail-case", [str(fail_source)], False, "CASEWORK", "deu,eng", "tester"
            )
            pipeline.extract(str(fail_case), None, "tester")
        validation.validate(str(fail_case), "tester")
        code, result = validation.verify_case(str(fail_case))
        self.assertEqual((code, result["status"], result["validation_status"], result["ready_for_pack"]), (core.VALIDATION_FAILED, "FAIL", "FAIL", False))

    def test_json_argparse_errors_are_canonical_exit_two(self) -> None:
        cli = SCRIPTS / "paperwork.py"
        result = subprocess.run(
            [sys.executable, str(cli), "--json", "intake"],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, core.USAGE)
        self.assertEqual(result.stderr, "")
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "FAIL")
        self.assertEqual(payload["exit_code"], core.USAGE)
        self.assertEqual(result.stdout.encode("utf-8"), core.canonical_bytes(payload))

    def test_cli_maps_expected_filesystem_failures_to_controlled_exits(self) -> None:
        cli = SCRIPTS / "paperwork.py"
        case, _ = self.new_case("INVENTORY")
        validation.validate(str(case), "tester")

        export_directory = self.root / "read-only-export"
        export_directory.mkdir()
        output = export_directory / "blocked.paperwork.tar"
        export_directory.chmod(0o555)
        try:
            pack_result = subprocess.run(
                [
                    sys.executable,
                    str(cli),
                    "--json",
                    "pack",
                    "--case",
                    str(case),
                    "--output",
                    str(output),
                    "--actor",
                    "tester",
                    "--acknowledge-plain-archive",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
        finally:
            export_directory.chmod(0o755)
        self.assertEqual(pack_result.returncode, core.PROCESSING)
        self.assertEqual(json.loads(pack_result.stdout)["message"], "filesystem operation failed")

        document = core.read_jsonl(core.case_paths(case)["documents"], core.DOCUMENT_SCHEMA)[0]
        original = case / document["original"]
        original.chmod(0o000)
        try:
            verify_result = subprocess.run(
                [sys.executable, str(cli), "--json", "verify", "--case", str(case)],
                check=False,
                capture_output=True,
                text=True,
            )
        finally:
            original.chmod(0o400)
        self.assertEqual(verify_result.returncode, core.INTEGRITY)
        self.assertEqual(json.loads(verify_result.stdout)["message"], "filesystem operation failed")

    def test_pack_verify_rejects_traversal(self) -> None:
        case, _ = self.new_case("INVENTORY")
        validation.validate(str(case), "tester")
        valid = self.root / "valid.paperwork.tar"
        validation.pack(str(case), str(valid), "evidence", "tester", True, False, None, None)
        with tarfile.open(valid, "r:") as archive:
            members = []
            for member in archive.getmembers():
                handle = archive.extractfile(member)
                self.assertIsNotNone(handle)
                members.append((member, handle.read()))
        original_receipt = core.read_json(Path(f"{valid}.receipt.json"))
        unsafe_names = ["../escape", "case\\..\\evil", "./a", "a//b", "a/./b", "."]
        for index, unsafe_name in enumerate(unsafe_names):
            with self.subTest(name=unsafe_name):
                pack = self.root / f"malicious-{index}.paperwork.tar"
                renamed = False
                with tarfile.open(pack, "w", format=tarfile.USTAR_FORMAT) as archive:
                    for member, content in members:
                        name = member.name
                        if not renamed and name != "PACK-MANIFEST.json":
                            name = unsafe_name
                            renamed = True
                        info = tarfile.TarInfo(name)
                        info.size = len(content)
                        info.mode = member.mode
                        info.uid = info.gid = info.mtime = 0
                        info.uname = info.gname = ""
                        archive.addfile(info, io.BytesIO(content))
                digest = core.sha256_file(pack)
                Path(f"{pack}.sha256").write_text(f"{digest}  {pack.name}\n", encoding="utf-8")
                receipt = dict(original_receipt)
                receipt["archive"] = pack.name
                receipt["archive_sha256"] = digest
                core.write_json(Path(f"{pack}.receipt.json"), receipt)
                with self.assertRaises(core.PaperworkError) as failure:
                    validation.verify_pack(str(pack))
                self.assertEqual(failure.exception.code, core.INTEGRITY)

    def test_pack_verify_rejects_non_string_manifest_paths_as_integrity_error(self) -> None:
        case, _ = self.new_case("INVENTORY")
        validation.validate(str(case), "tester")
        valid = self.root / "valid-manifest.paperwork.tar"
        validation.pack(str(case), str(valid), "evidence", "tester", True, False, None, None)
        receipt = core.read_json(Path(f"{valid}.receipt.json"))
        members: list[tuple[tarfile.TarInfo, bytes]] = []
        with tarfile.open(valid, "r:") as archive:
            for member in archive.getmembers():
                handle = archive.extractfile(member)
                self.assertIsNotNone(handle)
                content = handle.read()
                if member.name == "PACK-MANIFEST.json":
                    manifest = json.loads(content)
                    manifest["entries"][0]["path"] = 123
                    content = core.canonical_bytes(manifest)
                members.append((member, content))

        forged = self.root / "integer-path.paperwork.tar"
        with tarfile.open(forged, "w", format=tarfile.USTAR_FORMAT) as archive:
            for member, content in members:
                info = tarfile.TarInfo(member.name)
                info.size = len(content)
                info.mode = member.mode
                info.uid = info.gid = info.mtime = 0
                info.uname = info.gname = ""
                archive.addfile(info, io.BytesIO(content))
        digest = core.sha256_file(forged)
        Path(f"{forged}.sha256").write_text(f"{digest}  {forged.name}\n", encoding="utf-8")
        receipt["archive"] = forged.name
        receipt["archive_sha256"] = digest
        core.write_json(Path(f"{forged}.receipt.json"), receipt)
        with self.assertRaises(core.PaperworkError) as failure:
            validation.verify_pack(str(forged))
        self.assertEqual(failure.exception.code, core.INTEGRITY)

    def test_scripts_have_no_network_imports_or_shell_execution(self) -> None:
        forbidden = {"socket", "http", "urllib", "requests", "ftplib", "smtplib", "webbrowser"}
        for path in sorted(SCRIPTS.glob("*.py")):
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(path))
            imports = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imports.update(alias.name.split(".")[0] for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imports.add(node.module.split(".")[0])
                elif isinstance(node, ast.Call):
                    for keyword in node.keywords:
                        if keyword.arg == "shell" and isinstance(keyword.value, ast.Constant):
                            self.assertIsNot(keyword.value.value, True, path.name)
            self.assertFalse(imports & forbidden, f"{path.name}: {imports & forbidden}")

    def test_schema_assets_are_valid_json(self) -> None:
        schemas = sorted((PLUGIN_ROOT / "skills" / "godmode-paperwork" / "assets" / "schemas").glob("*.json"))
        self.assertEqual(len(schemas), 8)
        loaded = {}
        for path in schemas:
            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(data["$schema"], "https://json-schema.org/draft/2020-12/schema")
            loaded[path.name] = data
        self.assertNotIn("scope_digest", loaded["approval-input.schema.json"]["required"])
        self.assertIn("scope_digest", loaded["approval.schema.json"]["required"])
        self.assertEqual(
            loaded["page-resolution.schema.json"]["properties"]["schema"]["const"],
            core.PAGE_RESOLUTION_SCHEMA,
        )
        anchor_schema = loaded["claim.schema.json"]["properties"]["anchors"]["items"]
        self.assertEqual(len(anchor_schema["allOf"]), 2)


if __name__ == "__main__":
    unittest.main()
