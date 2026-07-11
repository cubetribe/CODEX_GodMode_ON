"""Doctor, intake, extraction, and routing commands for GodMode Paperwork."""

from __future__ import annotations

import contextlib
import csv
from decimal import Decimal, ROUND_HALF_UP
import os
from pathlib import Path
import re
import shutil
import stat
import tempfile
import unicodedata
from typing import Any

from paperwork_core import (
    CAPABILITY_MISSING,
    DOCUMENT_SCHEMA,
    INTEGRITY,
    INVALID,
    INVENTORY_MEDIA,
    PAGE_SCHEMA,
    PASS,
    POLICY_DENIAL,
    PROCESSABLE_MEDIA,
    PROCESSING,
    REVIEW,
    VERSION,
    PaperworkError,
    add_review,
    append_audit,
    assert_no_symlink_chain,
    atomic_write,
    capability_executable,
    case_lock,
    case_mutation_transaction,
    case_paths,
    copy_original_transactional,
    ensure_dir,
    executable_provenance,
    initialize_case,
    invalidate_validation,
    is_relative_to,
    parse_document_selector,
    parse_finite_decimal,
    parse_languages,
    run_tool,
    safe_relative,
    sha256_file,
    upsert_records,
    validate_case_path,
    verify_case_integrity,
    write_jsonl,
)


CAPABILITY_TOOLS = {
    "pdf-native": ("pdfinfo", "pdftotext"),
    "pdf-render": ("pdftoppm",),
    "ocr": ("tesseract",),
    "ocr-derivative": ("ocrmypdf",),
    "signature": ("pdfsig",),
    "advanced-layout": (),
}


@contextlib.contextmanager
def _mutation(root: Path, actor: str):
    with case_lock(root, actor):
        with case_mutation_transaction(root):
            yield


def _tesseract_languages(executable: str) -> list[str]:
    result = run_tool([executable, "--list-langs"], 20, text=True)
    if result.returncode != 0:
        return []
    lines = [line.strip() for line in (result.stdout or "").splitlines()]
    return sorted(line for line in lines if re.fullmatch(r"[A-Za-z0-9_-]+", line))


def _tesseract_language_data(executable: str, languages: list[str]) -> list[dict[str, str]]:
    result = run_tool([executable, "--list-langs"], 20, text=True)
    if result.returncode != 0:
        raise PaperworkError("Tesseract language inventory failed", CAPABILITY_MISSING)
    output = (result.stdout or "") + (result.stderr or "")
    candidates: list[Path] = []
    match = re.search(r'available languages in "([^"]+)"', output)
    if match:
        candidates.append(Path(match.group(1)))
    if os.environ.get("TESSDATA_PREFIX"):
        candidates.append(Path(os.environ["TESSDATA_PREFIX"]))
    executable_path = Path(executable).resolve()
    candidates.extend(
        [
            executable_path.parent / "tessdata",
            executable_path.parent.parent / "share" / "tessdata",
        ]
    )
    for directory in candidates:
        records: list[dict[str, str]] = []
        for language in languages:
            path = (directory / f"{language}.traineddata").resolve()
            if not path.is_file():
                records = []
                break
            records.append({"language": language, "path": str(path), "sha256": sha256_file(path)})
        if records:
            return records
    raise PaperworkError("Tesseract language data files could not be hashed", CAPABILITY_MISSING)


def doctor(languages_value: str, required_value: str) -> tuple[int, dict[str, Any]]:
    languages = parse_languages(languages_value)
    required = sorted(set(part.strip() for part in required_value.split(",") if part.strip()))
    unknown = [item for item in required if item not in CAPABILITY_TOOLS]
    if unknown:
        raise PaperworkError(f"unknown required capabilities: {', '.join(unknown)}", INVALID)

    tool_names = sorted({tool for tools in CAPABILITY_TOOLS.values() for tool in tools})
    tools = {name: capability_executable(name) for name in tool_names}
    available_languages: list[str] = []
    if tools["tesseract"]["present"]:
        available_languages = _tesseract_languages(tools["tesseract"]["path"])

    capabilities: dict[str, dict[str, Any]] = {}
    for capability, names in CAPABILITY_TOOLS.items():
        present = all(tools[name]["present"] for name in names)
        missing_languages: list[str] = []
        if capability == "ocr" and present:
            missing_languages = sorted(set(languages) - set(available_languages))
            present = not missing_languages
        capabilities[capability] = {
            "present": present,
            "tools": [tools[name] for name in names],
            "missing_languages": missing_languages,
        }
    capabilities["advanced-layout"] = {
        "present": False,
        "status": "DEFERRED",
        "tools": [],
        "missing_languages": [],
    }
    missing = [item for item in required if not capabilities[item]["present"]]
    result = {
        "command": "doctor",
        "status": "PASS" if not missing else "FAIL",
        "version": VERSION,
        "languages": languages,
        "required": required,
        "missing": missing,
        "capabilities": capabilities,
        "installation_attempted": False,
    }
    return (PASS if not missing else CAPABILITY_MISSING), result


def _input_files(raw_inputs: list[str], recursive: bool, case_root: Path) -> list[Path]:
    files: list[Path] = []
    home = Path.home().resolve()
    for raw in raw_inputs:
        path = assert_no_symlink_chain(Path(raw))
        if not path.exists():
            raise PaperworkError(f"input does not exist: {path}", INVALID)
        if path == home:
            raise PaperworkError("refusing to scan the home directory", POLICY_DENIAL)
        if path.is_dir() and recursive and (path.parent == path or is_relative_to(home, path)):
            raise PaperworkError("refusing a recursive input that contains the home or filesystem root", POLICY_DENIAL)
        candidates: list[Path]
        try:
            if path.is_dir():
                iterator = path.rglob("*") if recursive else path.iterdir()
                candidates = sorted(iterator)
            elif path.is_file():
                candidates = [path]
            else:
                raise PaperworkError(f"unsupported input object: {path}", POLICY_DENIAL)
        except OSError as exc:
            raise PaperworkError(f"input cannot be inspected safely: {path}: {exc}", PROCESSING) from exc
        for candidate in candidates:
            try:
                if candidate.is_symlink():
                    raise PaperworkError(f"symbolic-link input is forbidden: {candidate}", POLICY_DENIAL)
                if candidate.is_dir():
                    continue
                if not candidate.is_file() or candidate.stat().st_nlink != 1:
                    raise PaperworkError(f"special or hard-linked input is forbidden: {candidate}", POLICY_DENIAL)
                resolved = candidate.resolve()
            except OSError as exc:
                raise PaperworkError(f"input changed during inspection: {candidate}: {exc}", PROCESSING) from exc
            if is_relative_to(resolved, case_root):
                raise PaperworkError("a case cannot ingest files from itself", POLICY_DENIAL)
            files.append(resolved)
    unique = sorted(set(files), key=lambda item: str(item))
    if not unique:
        raise PaperworkError("no input files selected", INVALID)
    return unique


def _media_for(path: Path) -> tuple[str, bool]:
    extension = path.suffix.lower()
    if extension in PROCESSABLE_MEDIA:
        return PROCESSABLE_MEDIA[extension], True
    return INVENTORY_MEDIA.get(extension, "application/octet-stream"), False


def intake(
    case_value: str,
    case_id: str,
    inputs: list[str],
    recursive: bool,
    assurance: str,
    languages_value: str,
    actor: str,
) -> tuple[int, dict[str, Any]]:
    root = validate_case_path(case_value, must_exist=False)
    files = _input_files(inputs, recursive, root)
    source_names: dict[Path, str] = {}
    for source in files:
        source_name = unicodedata.normalize("NFC", source.name)
        if (
            not source_name
            or source_name in {".", ".."}
            or Path(source_name).is_absolute()
            or "/" in source_name
            or "\\" in source_name
        ):
            raise PaperworkError(f"source basename is unsafe: {source.name!r}", POLICY_DENIAL)
        source_names[source] = source_name
    languages = parse_languages(languages_value)
    if root.exists():
        entries = [item for item in root.iterdir() if item.name != ".paperwork.lock"]
        if entries and not (root / "case.json").is_file():
            raise PaperworkError("case root exists and is not an existing Paperwork case", POLICY_DENIAL)
    else:
        try:
            ensure_dir(root, 0o700)
        except PaperworkError as exc:
            raise PaperworkError("case root cannot be created safely", POLICY_DENIAL) from exc
    paths = case_paths(root)
    inventory_only: list[str] = []
    added: list[str] = []
    duplicates: list[str] = []
    with _mutation(root, actor):
        existing = paths["case"].exists()
        if not existing:
            ensure_dir(root, 0o700)
        initialize_case(root, case_id, assurance, languages)
        state = verify_case_integrity(root, allow_lock=True)
        case = state["case"]
        if case.get("assurance") != assurance or case.get("languages") != languages:
            raise PaperworkError("assurance or languages differ from the existing case", POLICY_DENIAL)
        if existing:
            invalidate_validation(root)
        documents = state["documents"]
        by_hash = {item["sha256"]: item for item in documents}
        for source in files:
            try:
                source_hash = sha256_file(source)
            except OSError as exc:
                raise PaperworkError(f"source cannot be hashed safely: {source.name}: {exc}", PROCESSING) from exc
            source_name = source_names[source]
            media_type, processable = _media_for(source)
            if source_hash in by_hash:
                record = by_hash[source_hash]
                names = sorted(set(record["source_names"] + [source_name]))
                if names != record["source_names"]:
                    record["source_names"] = names
                duplicates.append(source_hash)
                continue
            relative = Path("originals") / source_hash[:2] / source_hash
            destination = root / relative
            copy_original_transactional(source, destination, source_hash)
            record = {
                "schema": DOCUMENT_SCHEMA,
                "sha256": source_hash,
                "bytes": destination.stat().st_size,
                "media_type": media_type,
                "original": relative.as_posix(),
                "source_names": [source_name],
                "processable": processable,
                "support_status": "SUPPORTED" if processable else "INVENTORY_ONLY",
                "pages_expected": None,
            }
            by_hash[source_hash] = record
            added.append(source_hash)
            if not processable:
                inventory_only.append(source_hash)
                add_review(root, f"unsupported media type retained for inventory: {media_type}", source_hash)
        write_jsonl(paths["documents"], [by_hash[key] for key in sorted(by_hash)])
        append_audit(
            root,
            "INTAKE",
            actor,
            {
                "added": added,
                "duplicates": sorted(set(duplicates)),
                "inventory_only": inventory_only,
            },
        )
        verify_case_integrity(root, allow_lock=True)

    status = "REVIEW" if inventory_only else "PASS"
    return (
        REVIEW if inventory_only else PASS,
        {
            "command": "intake",
            "status": status,
            "case": str(root),
            "case_id": case_id,
            "added": added,
            "duplicates": sorted(set(duplicates)),
            "inventory_only": inventory_only,
        },
    )


def _require_tools(names: list[str]) -> dict[str, str]:
    result: dict[str, str] = {}
    missing: list[str] = []
    for name in names:
        resolved = shutil.which(name)
        if resolved:
            result[name] = str(Path(resolved).resolve())
        else:
            missing.append(name)
    if missing:
        raise PaperworkError(f"missing local capabilities: {', '.join(missing)}", CAPABILITY_MISSING)
    return result


def _pdf_pages(pdfinfo: str, original: Path) -> int | None:
    result = run_tool([pdfinfo, str(original)], 60, text=True)
    if result.returncode != 0:
        return None
    match = re.search(r"^Pages:\s*([0-9]+)\s*$", result.stdout or "", re.MULTILINE)
    if not match:
        return None
    pages = int(match.group(1))
    return pages if pages > 0 else None


def _native_quality(text: str, tool_ok: bool) -> tuple[bool, int, str]:
    alphanumeric = sum(character.isalnum() for character in text)
    replacement = text.count("\ufffd")
    ratio = Decimal(replacement) / Decimal(max(len(text), 1))
    return tool_ok and alphanumeric >= 32 and ratio <= Decimal("0.02"), alphanumeric, str(ratio)


def extract(case_value: str, document_value: str | None, actor: str) -> tuple[int, dict[str, Any]]:
    root = validate_case_path(case_value, must_exist=True)
    selected_hash = parse_document_selector(document_value)
    page_updates: list[dict[str, Any]] = []
    document_updates: list[dict[str, Any]] = []
    review_pages: list[str] = []
    processed: list[str] = []
    tools_audit: dict[str, Any] = {}
    with _mutation(root, actor):
        state = verify_case_integrity(root, allow_lock=True)
        paths = case_paths(root)
        documents = state["documents"]
        if selected_hash and not any(item["sha256"] == selected_hash for item in documents):
            raise PaperworkError(f"document is not in the case: {selected_hash}", INVALID)
        targets = [
            item
            for item in documents
            if item["processable"] and (selected_hash is None or item["sha256"] == selected_hash)
        ]
        if not targets:
            return PASS, {
                "command": "extract",
                "status": "PASS",
                "case": str(root),
                "documents": [],
                "pages": 0,
                "requires_routing": [],
            }
        target_hashes = {item["sha256"] for item in targets}
        if any(page["document"] in target_hashes for page in state["pages"]):
            raise PaperworkError("selected documents already have extraction records", POLICY_DENIAL)
        needs_pdf_tools = any(item["media_type"] == "application/pdf" for item in targets)
        tools = _require_tools(["pdfinfo", "pdftotext"] if needs_pdf_tools else [])
        pdf_provenance: dict[str, Any] = {}
        if needs_pdf_tools:
            pdf_provenance = {
                "pdfinfo": executable_provenance(
                    tools["pdfinfo"], ["pdfinfo", "CASE_ORIGINAL"]
                ),
                "pdftotext": executable_provenance(
                    tools["pdftotext"],
                    ["pdftotext", "-f", "PAGE", "-l", "PAGE", "-layout", "CASE_ORIGINAL", "NATIVE_OUTPUT"],
                ),
            }
            tools_audit.update(pdf_provenance)
        invalidate_validation(root)
        for document in targets:
            digest = document["sha256"]
            original = root / document["original"]
            if sha256_file(original) != digest:
                raise PaperworkError(f"original changed before extraction: {digest}", INTEGRITY)
            if document["bytes"] > 500 * 1024 * 1024:
                add_review(root, "document exceeds the 500 MiB MVP processing limit", digest)
                review_pages.append(digest)
                continue
            processed.append(digest)
            if document["media_type"] != "application/pdf":
                updated = dict(document)
                updated["pages_expected"] = 1
                document_updates.append(updated)
                page_updates.append(
                    {
                        "schema": PAGE_SCHEMA,
                        "document": digest,
                        "page": 1,
                        "route": "OCR_REQUIRED",
                        "native_artifact": None,
                        "native_alphanumeric": 0,
                        "replacement_ratio": "0",
                        "final_artifact": None,
                        "artifact_sha256": None,
                        "provenance": {},
                    }
                )
                review_pages.append(f"{digest}:1")
                continue

            pages = _pdf_pages(tools["pdfinfo"], original)
            if pages is None:
                add_review(root, "PDF is encrypted, corrupt, or unreadable by pdfinfo", digest)
                review_pages.append(digest)
                continue
            if pages > 2000:
                add_review(root, "PDF exceeds the 2000-page MVP processing limit", digest)
                review_pages.append(digest)
                continue
            updated = dict(document)
            updated["pages_expected"] = pages
            document_updates.append(updated)
            document_work_dir = root / "work" / digest
            native_dir = document_work_dir / "native"
            final_dir = document_work_dir / "final"
            for directory in (document_work_dir, native_dir, final_dir):
                ensure_dir(directory, 0o700)
            for page_number in range(1, pages + 1):
                native_path = native_dir / f"page-{page_number:04d}.txt"
                descriptor, temp_name = tempfile.mkstemp(prefix=f".{native_path.name}.tool-", dir=native_dir)
                os.close(descriptor)
                temp_path = Path(temp_name)
                result = run_tool(
                    [
                        tools["pdftotext"],
                        "-f",
                        str(page_number),
                        "-l",
                        str(page_number),
                        "-layout",
                        str(original),
                        str(temp_path),
                    ],
                    60,
                )
                try:
                    if temp_path.exists():
                        with temp_path.open("rb") as handle:
                            raw = handle.read()
                    else:
                        raw = b""
                except OSError as exc:
                    raise PaperworkError(f"native page output cannot be read: {exc}", PROCESSING) from exc
                if temp_path.exists():
                    temp_path.unlink()
                text = raw.decode("utf-8", errors="replace")
                encoded = text.encode("utf-8")
                atomic_write(native_path, encoded)
                accepted, alphanumeric, replacement_ratio = _native_quality(text, result.returncode == 0)
                relative_native = safe_relative(root, native_path)
                if accepted:
                    final_path = final_dir / f"page-{page_number:04d}.txt"
                    atomic_write(final_path, encoded)
                    page_updates.append(
                        {
                            "schema": PAGE_SCHEMA,
                            "document": digest,
                            "page": page_number,
                            "route": "NATIVE",
                            "native_artifact": relative_native,
                            "native_sha256": sha256_file(native_path),
                            "native_alphanumeric": alphanumeric,
                            "replacement_ratio": replacement_ratio,
                            "final_artifact": safe_relative(root, final_path),
                            "artifact_sha256": sha256_file(final_path),
                            "provenance": pdf_provenance,
                        }
                    )
                else:
                    page_updates.append(
                        {
                            "schema": PAGE_SCHEMA,
                            "document": digest,
                            "page": page_number,
                            "route": "OCR_REQUIRED",
                            "native_artifact": relative_native,
                            "native_sha256": sha256_file(native_path),
                            "native_alphanumeric": alphanumeric,
                            "replacement_ratio": replacement_ratio,
                            "final_artifact": None,
                            "artifact_sha256": None,
                            "provenance": pdf_provenance,
                        }
                    )
                    review_pages.append(f"{digest}:{page_number}")

        if document_updates:
            upsert_records(paths["documents"], DOCUMENT_SCHEMA, document_updates, ["sha256"])
        if page_updates:
            upsert_records(paths["pages"], PAGE_SCHEMA, page_updates, ["document", "page"])
        append_audit(
            root,
            "EXTRACT",
            actor,
            {
                "documents": processed,
                "pages": len(page_updates),
                "requires_routing": review_pages,
                "tools": tools_audit,
            },
        )

    status = "REVIEW" if review_pages else "PASS"
    return (
        REVIEW if review_pages else PASS,
        {
            "command": "extract",
            "status": status,
            "case": str(root),
            "documents": processed,
            "pages": len(page_updates),
            "requires_routing": review_pages,
        },
    )


def _tsv_metrics(path: Path) -> tuple[bool, Decimal, dict[str, int] | None]:
    dimensions: dict[str, int] | None = None
    maximum_right = 0
    maximum_bottom = 0
    boxes: list[tuple[int, int]] = []
    try:
        if path.stat().st_size > 100 * 1024 * 1024:
            return False, Decimal("0"), None
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle, delimiter="\t")
            required = {"level", "left", "top", "width", "height", "conf", "text"}
            if not reader.fieldnames or not required <= set(reader.fieldnames):
                return False, Decimal("0"), None
            weighted = Decimal("0")
            weight = 0
            for row in reader:
                numeric = [row.get(field, "") for field in ("level", "left", "top", "width", "height")]
                if any(not isinstance(value, str) or re.fullmatch(r"[0-9]{1,9}", value) is None for value in numeric):
                    return False, Decimal("0"), None
                level = int(row["level"])
                left = int(row["left"])
                top = int(row["top"])
                width = int(row["width"])
                height = int(row["height"])
                if level not in {1, 2, 3, 4, 5} or max(left, top, width, height) > 100_000_000:
                    return False, Decimal("0"), None
                maximum_right = max(maximum_right, left + width)
                maximum_bottom = max(maximum_bottom, top + height)
                boxes.append((left + width, top + height))
                if level == 1 and width > 0 and height > 0:
                    dimensions = {"width": width, "height": height}
                text = row.get("text", "")
                if not isinstance(text, str):
                    return False, Decimal("0"), None
                character_weight = sum(not character.isspace() for character in text)
                if character_weight == 0:
                    continue
                try:
                    confidence = parse_finite_decimal(row.get("conf", "-1"), "Tesseract TSV confidence")
                except PaperworkError:
                    return False, Decimal("0"), None
                if confidence < -1 or confidence > 100:
                    return False, Decimal("0"), None
                if confidence < 0:
                    continue
                weighted += confidence * character_weight
                weight += character_weight
    except (OSError, UnicodeError, csv.Error, ValueError, ArithmeticError):
        return False, Decimal("0"), None
    if dimensions is None and maximum_right > 0 and maximum_bottom > 0:
        dimensions = {"width": maximum_right, "height": maximum_bottom}
    if dimensions is not None and any(
        right > dimensions["width"] or bottom > dimensions["height"] for right, bottom in boxes
    ):
        return False, Decimal("0"), None
    if weight == 0 or dimensions is None:
        return False, Decimal("0"), dimensions
    return True, (weighted / weight).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP), dimensions


def _render_page(root: Path, document: dict[str, Any], page_number: int, pdftoppm: str) -> Path:
    digest = document["sha256"]
    original = root / document["original"]
    document_work_dir = root / "work" / digest
    render_dir = document_work_dir / "render"
    ensure_dir(document_work_dir, 0o700)
    ensure_dir(render_dir, 0o700)
    render_path = render_dir / f"page-{page_number:04d}.png"
    if render_path.exists():
        raise PaperworkError(f"refusing to overwrite existing render artifact: {render_path}", INTEGRITY)
    if document["media_type"] == "application/pdf":
        descriptor, prefix_name = tempfile.mkstemp(prefix=f".page-{page_number:04d}.render-", dir=render_dir)
        os.close(descriptor)
        prefix = Path(prefix_name)
        prefix.unlink()
        produced = Path(f"{prefix}.png")
        if produced.exists():
            produced.unlink()
        result = run_tool(
            [
                pdftoppm,
                "-f",
                str(page_number),
                "-l",
                str(page_number),
                "-r",
                "300",
                "-png",
                "-singlefile",
                str(original),
                str(prefix),
            ],
            120,
        )
        if result.returncode != 0 or not produced.is_file():
            if produced.exists():
                produced.unlink()
            raise PaperworkError(f"failed to render {digest} page {page_number}", PROCESSING)
        os.replace(produced, render_path)
        try:
            render_path.chmod(0o600)
        except OSError:
            pass
    else:
        try:
            content = original.read_bytes()
        except OSError as exc:
            raise PaperworkError(f"image original cannot be read for rendering: {exc}", PROCESSING) from exc
        atomic_write(render_path, content)
    return render_path


def _secure_ocr_outputs(paths: tuple[Path, ...]) -> None:
    for path in paths:
        try:
            metadata = path.lstat()
        except FileNotFoundError:
            continue
        except OSError as exc:
            raise PaperworkError(f"OCR output cannot be inspected safely: {path}: {exc}", PROCESSING) from exc
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
            raise PaperworkError(f"OCR output is linked or not a regular file: {path}", INTEGRITY)
        try:
            path.chmod(0o600)
            if stat.S_IMODE(path.lstat().st_mode) != 0o600:
                raise OSError("mode did not become 0600")
        except OSError as exc:
            raise PaperworkError(f"OCR output cannot be restricted to mode 0600: {path}: {exc}", PROCESSING) from exc


def route(case_value: str, document_value: str | None, actor: str) -> tuple[int, dict[str, Any]]:
    root = validate_case_path(case_value, must_exist=True)
    selected_hash = parse_document_selector(document_value)
    updates: list[dict[str, Any]] = []
    routed: list[str] = []
    visual_review: list[str] = []
    with _mutation(root, actor):
        state = verify_case_integrity(root, allow_lock=True)
        documents = {item["sha256"]: item for item in state["documents"]}
        if selected_hash and selected_hash not in documents:
            raise PaperworkError(f"document is not in the case: {selected_hash}", INVALID)
        pending = [
            page
            for page in state["pages"]
            if page["route"] == "OCR_REQUIRED"
            and (selected_hash is None or page["document"] == selected_hash)
        ]
        if not pending:
            existing_review = [
                f"{page['document']}:{page['page']}"
                for page in state["pages"]
                if page["route"] == "VISUAL_REVIEW"
                and (selected_hash is None or page["document"] == selected_hash)
            ]
            return (REVIEW if existing_review else PASS), {
                "command": "route",
                "status": "REVIEW" if existing_review else "PASS",
                "case": str(root),
                "routed": [],
                "visual_review": existing_review,
            }
        needs_pdf_render = any(documents[page["document"]]["media_type"] == "application/pdf" for page in pending)
        tools = _require_tools((["pdftoppm"] if needs_pdf_render else []) + ["tesseract"])
        languages = state["case"]["languages"]
        available = _tesseract_languages(tools["tesseract"])
        missing_languages = sorted(set(languages) - set(available))
        if missing_languages:
            raise PaperworkError(f"Tesseract language data missing: {', '.join(missing_languages)}", CAPABILITY_MISSING)
        language_data = _tesseract_language_data(tools["tesseract"], languages)
        route_provenance: dict[str, Any] = {
            "tesseract": executable_provenance(
                tools["tesseract"],
                [
                    "tesseract",
                    "RENDERED_PAGE",
                    "OCR_OUTPUT_BASE",
                    "-l",
                    "+".join(languages),
                    "--oem",
                    "1",
                    "--psm",
                    "3",
                    "txt",
                    "tsv",
                    "hocr",
                ],
                language_data=language_data,
            )
        }
        if needs_pdf_render:
            route_provenance["pdftoppm"] = executable_provenance(
                tools["pdftoppm"],
                [
                    "pdftoppm",
                    "-f",
                    "PAGE",
                    "-l",
                    "PAGE",
                    "-r",
                    "300",
                    "-png",
                    "-singlefile",
                    "CASE_ORIGINAL",
                    "RENDER_OUTPUT_PREFIX",
                ],
            )
        invalidate_validation(root)
        for page in pending:
            digest = page["document"]
            page_number = page["page"]
            key = f"{digest}:{page_number}"
            document = documents[digest]
            render_path = _render_page(root, document, page_number, tools.get("pdftoppm", ""))
            document_work_dir = root / "work" / digest
            ocr_dir = document_work_dir / "ocr"
            ensure_dir(document_work_dir, 0o700)
            ensure_dir(ocr_dir, 0o700)
            base = ocr_dir / f"page-{page_number:04d}"
            for extension in (".txt", ".tsv", ".hocr"):
                candidate = Path(f"{base}{extension}")
                if candidate.exists():
                    raise PaperworkError(f"refusing to overwrite existing OCR artifact: {candidate}", INTEGRITY)
            timed_out = False
            try:
                result = run_tool(
                    [
                        tools["tesseract"],
                        str(render_path),
                        str(base),
                        "-l",
                        "+".join(languages),
                        "--oem",
                        "1",
                        "--psm",
                        "3",
                        "txt",
                        "tsv",
                        "hocr",
                    ],
                    180,
                )
            except PaperworkError as exc:
                if exc.code != PROCESSING:
                    raise
                timed_out = True
                result = None
            text_path = Path(f"{base}.txt")
            tsv_path = Path(f"{base}.tsv")
            hocr_path = Path(f"{base}.hocr")
            _secure_ocr_outputs((text_path, tsv_path, hocr_path))
            try:
                text = text_path.read_text(encoding="utf-8", errors="replace") if text_path.is_file() else ""
            except OSError as exc:
                raise PaperworkError(f"OCR text output cannot be read: {exc}", PROCESSING) from exc
            alphanumeric = sum(character.isalnum() for character in text)
            valid_tsv, confidence, page_dimensions = _tsv_metrics(tsv_path)
            accepted = (
                not timed_out
                and result is not None
                and result.returncode == 0
                and text_path.is_file()
                and hocr_path.is_file()
                and alphanumeric >= 8
                and valid_tsv
                and confidence >= Decimal("70.00")
            )
            update = dict(page)
            combined_provenance = dict(page.get("provenance", {}))
            combined_provenance.update(route_provenance)
            update.update(
                {
                    "render_artifact": safe_relative(root, render_path),
                    "render_sha256": sha256_file(render_path),
                    "ocr_alphanumeric": alphanumeric,
                    "ocr_confidence": format(confidence, ".2f") if valid_tsv else None,
                    "ocr_page_dimensions": page_dimensions,
                    "ocr_artifacts": [
                        {"path": safe_relative(root, candidate), "sha256": sha256_file(candidate)}
                        for candidate in (text_path, tsv_path, hocr_path)
                        if candidate.is_file()
                    ],
                    "provenance": combined_provenance,
                }
            )
            if accepted:
                final_path = root / "work" / digest / "final" / f"page-{page_number:04d}.txt"
                atomic_write(final_path, text.encode("utf-8"))
                update.update(
                    {
                        "route": "OCR",
                        "final_artifact": safe_relative(root, final_path),
                        "artifact_sha256": sha256_file(final_path),
                    }
                )
                routed.append(key)
            else:
                update.update({"route": "VISUAL_REVIEW", "final_artifact": None, "artifact_sha256": None})
                reason = "OCR timed out" if timed_out else "OCR did not meet deterministic acceptance thresholds"
                add_review(root, reason, digest, page_number)
                visual_review.append(key)
            updates.append(update)
        upsert_records(case_paths(root)["pages"], PAGE_SCHEMA, updates, ["document", "page"])
        append_audit(
            root,
            "ROUTE",
            actor,
            {
                "routed_ocr": routed,
                "visual_review": visual_review,
                "languages": languages,
                "tools": route_provenance,
            },
        )

    return (
        REVIEW if visual_review else PASS,
        {
            "command": "route",
            "status": "REVIEW" if visual_review else "PASS",
            "case": str(root),
            "routed": routed,
            "visual_review": visual_review,
        },
    )
