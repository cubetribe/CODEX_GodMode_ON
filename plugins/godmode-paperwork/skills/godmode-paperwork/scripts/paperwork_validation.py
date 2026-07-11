"""Validation, integrity verification, and reproducible packaging."""

from __future__ import annotations

import contextlib
import datetime as dt
import hashlib
import io
import os
from pathlib import Path, PurePosixPath
import re
import stat
import tarfile
import tempfile
from typing import Any

from paperwork_core import (
    INTEGRITY,
    INVALID,
    PACK_MANIFEST_SCHEMA,
    PACK_RECEIPT_SCHEMA,
    PASS,
    POLICY_DENIAL,
    PROCESSING,
    REVIEW,
    CASE_LOCKED,
    VALIDATION_FAILED,
    VALIDATION_SCHEMA,
    VERSION,
    PaperworkError,
    append_audit,
    assert_no_symlink_chain,
    canonical_bytes,
    canonical_digest,
    case_lock,
    case_mutation_transaction,
    case_paths,
    compute_state_digest,
    invalidate_validation,
    is_relative_to,
    parse_finite_decimal,
    parse_json_bytes,
    read_json,
    read_external_bytes,
    require_utc_timestamp,
    sha256_file,
    utc_now,
    validate_case_path,
    validate_output_path,
    verify_case_integrity,
    write_json,
)


ALLOWED_RULES = {"required_claim", "required_document", "equals", "decimal_sum", "date_order", "format", "unique"}
FINAL_ROUTES = {"NATIVE", "OCR", "VISUAL"}
PACK_MANIFEST_FIELDS = {
    "schema",
    "case_id",
    "contents",
    "actor",
    "validation_status",
    "validation_digest",
    "state_digest",
    "audit_head_sha256",
    "audit_count",
    "approval",
    "entries",
}
PACK_RECEIPT_FIELDS = {
    "schema",
    "archive",
    "archive_sha256",
    "case_id",
    "contents",
    "actor",
    "created_at",
    "validation_status",
    "validation_digest",
    "state_digest",
    "audit_head_sha256",
    "audit_count",
    "approval",
    "plain_archive_acknowledged",
}


@contextlib.contextmanager
def _mutation(root: Path, actor: str):
    with case_lock(root, actor):
        with case_mutation_transaction(root):
            yield


def _open_reviews(reviews: list[dict[str, Any]]) -> list[str]:
    return sorted(item["id"] for item in reviews if item.get("status") == "OPEN")


def _fixed_decimal(value: Any, label: str) -> tuple[int, int]:
    parse_finite_decimal(value, label)
    assert isinstance(value, str)
    negative = value.startswith("-")
    unsigned = value[1:] if negative else value
    whole, separator, fraction = unsigned.partition(".")
    scale = len(fraction) if separator else 0
    coefficient = int(whole + fraction)
    return (-coefficient if negative else coefficient), scale


def _scale_fixed(value: tuple[int, int], scale: int) -> int:
    coefficient, current_scale = value
    return coefficient * (10 ** (scale - current_scale))


def _valid_bbox(value: Any) -> bool:
    if not isinstance(value, list) or len(value) != 4 or not all(isinstance(item, str) for item in value):
        return False
    coordinates = [parse_finite_decimal(item, "bbox coordinate") for item in value]
    if any(item < 0 or item > 1 for item in coordinates):
        return False
    return coordinates[0] <= coordinates[2] and coordinates[1] <= coordinates[3]


def _validate_claims(
    root: Path,
    pages: list[dict[str, Any]],
    claims: list[dict[str, Any]],
    approvals: list[dict[str, Any]],
) -> tuple[dict[str, dict[str, Any]], list[str]]:
    page_map = {(item["document"], item["page"]): item for item in pages}
    claim_map: dict[str, dict[str, Any]] = {}
    issues: list[str] = []
    for claim in claims:
        claim_id = claim.get("id")
        if not isinstance(claim_id, str) or not claim_id or claim_id in claim_map:
            issues.append(f"invalid or duplicate claim id: {claim_id!r}")
            continue
        claim_map[claim_id] = claim
        if not isinstance(claim.get("name"), str) or not isinstance(claim.get("value"), str):
            issues.append(f"claim {claim_id} requires string name and value")
        anchors = claim.get("anchors")
        if not isinstance(anchors, list) or not anchors:
            issues.append(f"claim {claim_id} has no evidence anchor")
            continue
        for index, anchor in enumerate(anchors, 1):
            if not isinstance(anchor, dict):
                issues.append(f"claim {claim_id} anchor {index} is not an object")
                continue
            key = (anchor.get("document"), anchor.get("page"))
            page = page_map.get(key)
            if page is None:
                issues.append(f"claim {claim_id} anchor {index} references a missing page")
                continue
            method = anchor.get("method")
            if method not in ("NATIVE", "OCR", "VISUAL") or page.get("route") != method:
                issues.append(f"claim {claim_id} anchor {index} method does not match the final route")
            artifact = page.get("final_artifact")
            artifact_hash = page.get("artifact_sha256")
            if not isinstance(artifact, str) or not isinstance(artifact_hash, str):
                issues.append(f"claim {claim_id} anchor {index} has no final artifact")
                continue
            artifact_path = root / artifact
            if not artifact_path.is_file() or sha256_file(artifact_path) != artifact_hash:
                issues.append(f"claim {claim_id} anchor {index} final artifact is not reproducible")
                continue
            if anchor.get("artifact_sha256") != artifact_hash:
                issues.append(f"claim {claim_id} anchor {index} artifact hash differs")
            quote = anchor.get("quote")
            if not isinstance(quote, str) or not quote:
                issues.append(f"claim {claim_id} anchor {index} has no exact quote")
            else:
                try:
                    text = artifact_path.read_text(encoding="utf-8")
                except (OSError, UnicodeError):
                    issues.append(f"claim {claim_id} anchor {index} artifact is not UTF-8 text")
                else:
                    if quote not in text:
                        issues.append(f"claim {claim_id} anchor {index} quote is absent from the final artifact")
            if method in ("OCR", "VISUAL") and not _valid_bbox(anchor.get("bbox")):
                issues.append(f"claim {claim_id} anchor {index} requires a normalized bbox")
        if claim.get("critical") is True:
            confirmed = any(
                approval.get("human") is True
                and approval.get("scope_type") == "claim"
                and approval.get("scope_id") == claim_id
                and approval.get("scope_digest") == canonical_digest(claim)
                and approval.get("decision") == "CONFIRMED"
                and isinstance(approval.get("approved_by"), str)
                and approval["approved_by"].strip()
                and approval["approved_by"].strip().lower() not in {"codex", "model", "ai"}
                for approval in approvals
            )
            if not confirmed:
                issues.append(f"critical claim {claim_id} lacks human confirmation")
    return claim_map, issues


def _iso_date(value: str) -> dt.date | None:
    try:
        parsed = dt.date.fromisoformat(value)
    except (TypeError, ValueError):
        return None
    return parsed if parsed.isoformat() == value else None


def _iban_valid(value: str) -> bool:
    compact = "".join(value.split()).upper()
    if not re.fullmatch(r"[A-Z]{2}[0-9]{2}[A-Z0-9]{11,30}", compact):
        return False
    rearranged = compact[4:] + compact[:4]
    digits = "".join(str(ord(char) - 55) if char.isalpha() else char for char in rearranged)
    remainder = 0
    for char in digits:
        remainder = (remainder * 10 + int(char)) % 97
    return remainder == 1


def _format_valid(value: str, format_name: str) -> bool:
    if format_name == "iso-date":
        return _iso_date(value) is not None
    if format_name == "integer":
        return re.fullmatch(r"-?(?:0|[1-9][0-9]*)", value) is not None
    if format_name == "decimal":
        return re.fullmatch(r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?", value) is not None
    if format_name == "currency":
        return re.fullmatch(r"-?(?:0|[1-9][0-9]*)\.[0-9]{2}", value) is not None
    if format_name == "iban":
        return _iban_valid(value)
    raise PaperworkError(f"unsupported format: {format_name}", INVALID)


def _claim_value(claims: dict[str, dict[str, Any]], claim_id: Any, rule_id: str) -> str:
    if not isinstance(claim_id, str) or claim_id not in claims:
        raise PaperworkError(f"rule {rule_id} references an unknown claim: {claim_id!r}", INVALID)
    return claims[claim_id]["value"]


def _required_document_matches(
    documents: list[dict[str, Any]],
    sha256: Any,
    media_type: Any,
    label: str,
) -> bool:
    if sha256 is None and media_type is None:
        raise PaperworkError(f"{label} requires sha256 or media_type", INVALID)
    if sha256 is not None and (
        not isinstance(sha256, str) or re.fullmatch(r"[0-9a-f]{64}", sha256) is None
    ):
        raise PaperworkError(f"{label} sha256 is invalid", INVALID)
    if media_type is not None and (not isinstance(media_type, str) or not media_type):
        raise PaperworkError(f"{label} media_type is invalid", INVALID)
    return any(
        (sha256 is None or item["sha256"] == sha256)
        and (media_type is None or item["media_type"] == media_type)
        for item in documents
    )


def _validate_rules(
    requirements: dict[str, Any],
    documents: list[dict[str, Any]],
    claims: dict[str, dict[str, Any]],
) -> list[str]:
    issues: list[str] = []
    required_claims = requirements.get("required_claims", [])
    required_documents = requirements.get("required_documents", [])
    rules = requirements.get("rules", [])
    if not all(isinstance(item, list) for item in (required_claims, required_documents, rules)):
        raise PaperworkError("requirements lists are invalid", INVALID)
    for claim_id in required_claims:
        if claim_id not in claims:
            issues.append(f"required claim is missing: {claim_id}")
    for requirement in required_documents:
        if not isinstance(requirement, dict):
            raise PaperworkError("required_document entries must be objects", INVALID)
        if set(requirement) - {"sha256", "media_type"}:
            raise PaperworkError("required_document entries contain unknown fields", INVALID)
        if not _required_document_matches(
            documents,
            requirement.get("sha256"),
            requirement.get("media_type"),
            "required document",
        ):
            issues.append(f"required document is missing: {requirement}")

    for position, rule in enumerate(rules, 1):
        if not isinstance(rule, dict):
            raise PaperworkError(f"rule {position} must be an object", INVALID)
        rule_type = rule.get("type")
        rule_id = str(rule.get("id", f"rule-{position}"))
        if not isinstance(rule_type, str) or rule_type not in ALLOWED_RULES:
            raise PaperworkError(f"rule {rule_id} uses unsupported type: {rule_type}", INVALID)
        passed = False
        if rule_type == "required_claim":
            claim_ref = rule.get("claim")
            passed = isinstance(claim_ref, str) and claim_ref in claims
        elif rule_type == "required_document":
            passed = _required_document_matches(
                documents,
                rule.get("sha256"),
                rule.get("media_type"),
                f"rule {rule_id}",
            )
        elif rule_type == "equals":
            passed = _claim_value(claims, rule.get("left"), rule_id) == _claim_value(claims, rule.get("right"), rule_id)
        elif rule_type == "decimal_sum":
            terms = rule.get("terms")
            if not isinstance(terms, list) or not terms or len(terms) > 1000:
                raise PaperworkError(f"rule {rule_id} requires 1 to 1000 terms", INVALID)
            expected = _fixed_decimal(
                _claim_value(claims, rule.get("total"), rule_id),
                f"rule {rule_id} total",
            )
            term_values = [
                _fixed_decimal(_claim_value(claims, item, rule_id), f"rule {rule_id} term")
                for item in terms
            ]
            tolerance = _fixed_decimal(rule.get("tolerance", "0"), f"rule {rule_id} tolerance")
            if tolerance[0] < 0:
                raise PaperworkError(f"rule {rule_id} tolerance must not be negative", INVALID)
            scale = max(item[1] for item in [expected, tolerance, *term_values])
            actual_integer = sum(_scale_fixed(item, scale) for item in term_values)
            passed = abs(actual_integer - _scale_fixed(expected, scale)) <= _scale_fixed(tolerance, scale)
        elif rule_type == "date_order":
            before = _iso_date(_claim_value(claims, rule.get("before"), rule_id))
            after = _iso_date(_claim_value(claims, rule.get("after"), rule_id))
            passed = before is not None and after is not None and before <= after
        elif rule_type == "format":
            value = _claim_value(claims, rule.get("claim"), rule_id)
            passed = _format_valid(value, str(rule.get("format")))
        elif rule_type == "unique":
            references = rule.get("claims")
            if not isinstance(references, list) or not references:
                raise PaperworkError(f"rule {rule_id} requires non-empty claims", INVALID)
            values = [_claim_value(claims, item, rule_id) for item in references]
            passed = len(values) == len(set(values))
        if not passed:
            issues.append(f"validation rule failed: {rule_id}")
    return issues


def validate(case_value: str, actor: str) -> tuple[int, dict[str, Any]]:
    root = validate_case_path(case_value, must_exist=True)
    with _mutation(root, actor):
        state = verify_case_integrity(root, allow_lock=True, verify_validation=False)
        paths = case_paths(root)
        invalidate_validation(root)
        assurance = state["case"]["assurance"]
        review_items = _open_reviews(state["reviews"])
        issues: list[str] = []

        if assurance in {"EXTRACTION", "CASEWORK"}:
            page_map: dict[str, set[int]] = {}
            for page in state["pages"]:
                page_map.setdefault(page["document"], set()).add(page["page"])
                if page.get("route") not in FINAL_ROUTES:
                    review_items.append(f"unresolved-page:{page['document']}:{page['page']}")
                elif not page.get("final_artifact") or not page.get("artifact_sha256"):
                    issues.append(f"final route lacks an artifact: {page['document']}:{page['page']}")
            for document in state["documents"]:
                if not document["processable"]:
                    continue
                expected = document.get("pages_expected")
                if not isinstance(expected, int) or expected < 1:
                    review_items.append(f"page-count-unresolved:{document['sha256']}")
                    continue
                actual = page_map.get(document["sha256"], set())
                if actual != set(range(1, expected + 1)):
                    issues.append(f"incomplete page coverage: {document['sha256']}")

        if assurance == "CASEWORK":
            claims = state["claims"]
            approvals = state["approvals"]
            if not claims:
                issues.append("CASEWORK assurance requires at least one claim")
            claim_map, claim_issues = _validate_claims(root, state["pages"], claims, approvals)
            issues.extend(claim_issues)
            issues.extend(_validate_rules(state["requirements"], state["documents"], claim_map))

        review_items = sorted(set(review_items))
        if issues:
            status = "FAIL"
            code = VALIDATION_FAILED
        elif review_items:
            status = "REVIEW"
            code = REVIEW
        else:
            status = "PASS"
            code = PASS
        issues = sorted(set(issues))
        result_digest = canonical_digest({"status": status, "issues": issues, "review_items": review_items})
        event = append_audit(
            root,
            "VALIDATE",
            actor,
            {
                "status": status,
                "case_id": state["case"]["case_id"],
                "assurance": assurance,
                "validator_version": VERSION,
                "result_digest": result_digest,
            },
        )
        state_digest = compute_state_digest(root)
        payload = {
            "schema": VALIDATION_SCHEMA,
            "case_id": state["case"]["case_id"],
            "assurance": assurance,
            "status": status,
            "issues": issues,
            "review_items": review_items,
            "validated_at": event["timestamp"],
            "validator_version": VERSION,
            "state_digest": state_digest,
            "audit_head_sha256": event["event_sha256"],
            "audit_count": event["sequence"],
        }
        digest = canonical_digest(payload)
        payload["digest"] = digest
        write_json(paths["validation"], payload)
    return code, {"command": "validate", "case": str(root), **payload}


def verify_case(case_value: str) -> tuple[int, dict[str, Any]]:
    root = validate_case_path(case_value, must_exist=True)
    try:
        state = verify_case_integrity(root)
    except PaperworkError as exc:
        if exc.code not in {INTEGRITY, CASE_LOCKED}:
            raise
        return exc.code, {
            "command": "verify",
            "target": "case",
            "status": "FAIL",
            "integrity_status": "FAIL",
            "validation_status": "UNKNOWN",
            "ready_for_pack": False,
            "case": str(root),
            "message": exc.message,
        }
    validation_path = case_paths(root)["validation"]
    validation_status = "MISSING"
    if validation_path.is_file():
        validation_status = read_json(validation_path).get("status", "UNKNOWN")
    if validation_status == "PASS":
        code, status, ready = PASS, "PASS", True
    elif validation_status in ("MISSING", "REVIEW"):
        code, status, ready = REVIEW, "REVIEW", False
    elif validation_status == "FAIL":
        code, status, ready = VALIDATION_FAILED, "FAIL", False
    else:
        code, status, ready = INTEGRITY, "FAIL", False
    return code, {
        "command": "verify",
        "target": "case",
        "status": status,
        "integrity_status": "PASS",
        "validation_status": validation_status,
        "ready_for_pack": ready,
        "case": str(root),
        "case_id": state["case"]["case_id"],
        "documents": len(state["documents"]),
        "pages": len(state["pages"]),
    }


def _safe_tar_name(name: str) -> bool:
    if not isinstance(name, str) or not name or "\\" in name or "\x00" in name:
        return False
    path = PurePosixPath(name)
    return (
        name not in {".", ".."}
        and not name.endswith("/")
        and not path.is_absolute()
        and path.as_posix() == name
        and all(part not in {"", ".", ".."} for part in path.parts)
    )


@contextlib.contextmanager
def _open_regular(path: Path, label: str, maximum_bytes: int | None = None):
    try:
        safe_path = assert_no_symlink_chain(path)
    except PaperworkError as exc:
        raise PaperworkError(f"{label} path is unsafe: {exc.message}", INTEGRITY) from exc
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(safe_path, flags)
    except OSError as exc:
        raise PaperworkError(f"{label} cannot be opened safely: {exc}", INTEGRITY) from exc
    try:
        metadata = os.fstat(descriptor)
        current = os.lstat(safe_path)
        if (
            not stat.S_ISREG(metadata.st_mode)
            or metadata.st_nlink != 1
            or not stat.S_ISREG(current.st_mode)
            or (metadata.st_dev, metadata.st_ino) != (current.st_dev, current.st_ino)
        ):
            raise PaperworkError(f"{label} is linked, replaced, or not a regular file", INTEGRITY)
        if maximum_bytes is not None and metadata.st_size > maximum_bytes:
            raise PaperworkError(f"{label} exceeds {maximum_bytes} bytes", INTEGRITY)
        with os.fdopen(descriptor, "rb") as handle:
            descriptor = -1
            yield safe_path, handle, metadata
    finally:
        if descriptor >= 0:
            os.close(descriptor)


def _require_open_path_unchanged(path: Path, handle: Any, original: os.stat_result, label: str) -> None:
    try:
        current_path = os.lstat(path)
        current_handle = os.fstat(handle.fileno())
    except OSError as exc:
        raise PaperworkError(f"{label} changed during verification: {exc}", INTEGRITY) from exc
    identity = (original.st_dev, original.st_ino)
    if (
        not stat.S_ISREG(current_path.st_mode)
        or current_path.st_nlink != 1
        or (current_path.st_dev, current_path.st_ino) != identity
        or (current_handle.st_dev, current_handle.st_ino) != identity
        or current_handle.st_size != original.st_size
        or current_handle.st_mtime_ns != original.st_mtime_ns
        or current_handle.st_ctime_ns != original.st_ctime_ns
    ):
        raise PaperworkError(f"{label} changed during verification", INTEGRITY)


def _read_limited(handle: Any, maximum_bytes: int, label: str) -> bytes:
    try:
        content = handle.read(maximum_bytes + 1)
    except OSError as exc:
        raise PaperworkError(f"{label} cannot be read: {exc}", INTEGRITY) from exc
    if len(content) > maximum_bytes:
        raise PaperworkError(f"{label} exceeds {maximum_bytes} bytes", INTEGRITY)
    return content


@contextlib.contextmanager
def _read_tar(archive: tarfile.TarFile):
    try:
        with archive:
            yield archive
    except PaperworkError:
        raise
    except (OSError, tarfile.TarError, EOFError, UnicodeError, ValueError) as exc:
        raise PaperworkError(f"invalid tar archive: {exc}", INTEGRITY) from exc


@contextlib.contextmanager
def _write_tar(handle: Any):
    try:
        with tarfile.open(fileobj=handle, mode="w", format=tarfile.USTAR_FORMAT) as archive:
            yield archive
    except PaperworkError:
        raise
    except (OSError, tarfile.TarError, EOFError, UnicodeError, ValueError) as exc:
        raise PaperworkError(f"archive creation failed: {exc}", PROCESSING) from exc


@contextlib.contextmanager
def _verification_tempfile(label: str):
    try:
        with tempfile.TemporaryFile(mode="w+b") as handle:
            yield handle
    except PaperworkError:
        raise
    except OSError as exc:
        raise PaperworkError(f"{label} temporary storage failed: {exc}", INTEGRITY) from exc


@contextlib.contextmanager
def _verification_directory(label: str):
    try:
        with tempfile.TemporaryDirectory(prefix="godmode-paperwork-verify-") as directory:
            yield Path(directory)
    except PaperworkError:
        raise
    except OSError as exc:
        raise PaperworkError(f"{label} temporary storage failed: {exc}", INTEGRITY) from exc


def _materialize_and_verify_case(
    archive: tarfile.TarFile,
    entry_by_name: dict[str, dict[str, Any]],
    manifest: dict[str, Any],
) -> None:
    case_names = sorted(name for name in entry_by_name if name.startswith("case/"))
    with _verification_directory("packed case") as directory:
        root = directory / "case"
        try:
            root.mkdir(mode=0o700)
            for name in case_names:
                relative = PurePosixPath(name).relative_to("case")
                target = root.joinpath(*relative.parts)
                target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
                source = archive.extractfile(name)
                if source is None:
                    raise PaperworkError(f"packed case member cannot be read: {name}", INTEGRITY)
                with target.open("xb") as destination:
                    for block in iter(lambda: source.read(1024 * 1024), b""):
                        destination.write(block)
                target.chmod(0o600)
        except PaperworkError:
            raise
        except (OSError, tarfile.TarError, EOFError) as exc:
            raise PaperworkError(f"packed case cannot be materialized: {exc}", INTEGRITY) from exc

        state = verify_case_integrity(root)
        validation_path = case_paths(root)["validation"]
        try:
            with validation_path.open("rb") as handle:
                validation_bytes = handle.read(10 * 1024 * 1024 + 1)
        except OSError as exc:
            raise PaperworkError(f"packed validation cannot be read: {exc}", INTEGRITY) from exc
        if len(validation_bytes) > 10 * 1024 * 1024:
            raise PaperworkError("packed validation is too large", INTEGRITY)
        validation = parse_json_bytes(validation_bytes, "packed validation JSON", INTEGRITY)
        if not isinstance(validation, dict) or validation_bytes != canonical_bytes(validation):
            raise PaperworkError("packed validation is not canonical", INTEGRITY)

        expected_entries: dict[str, dict[str, Any]] = {}
        for entry in state["state_entries"]:
            name = f"case/{entry['path']}"
            expected_entries[name] = {
                "path": name,
                "bytes": entry["bytes"],
                "sha256": entry["sha256"],
                "mode": 0o400 if name.startswith("case/originals/") else 0o600,
            }
        validation_name = "case/validation/latest.json"
        expected_entries[validation_name] = {
            "path": validation_name,
            "bytes": len(validation_bytes),
            "sha256": hashlib.sha256(validation_bytes).hexdigest(),
            "mode": 0o600,
        }
        actual_case_entries = {name: entry_by_name[name] for name in case_names}
        if actual_case_entries != expected_entries:
            raise PaperworkError("archive case entries do not match the verified case state", INTEGRITY)

        bindings = {
            "case_id": state["case"]["case_id"],
            "validation_status": validation.get("status"),
            "validation_digest": validation.get("digest"),
            "state_digest": state["state_digest"],
            "audit_head_sha256": state["audit"]["head"],
            "audit_count": state["audit"]["count"],
        }
        for field, expected in bindings.items():
            if manifest.get(field) != expected:
                raise PaperworkError(f"pack manifest {field} is not bound to the packed case", INTEGRITY)


def _require_canonical_archive(
    archive_snapshot: Any,
    archive: tarfile.TarFile,
    members: list[tarfile.TarInfo],
) -> None:
    with _verification_tempfile("canonical archive") as rebuilt:
        try:
            with tarfile.open(fileobj=rebuilt, mode="w", format=tarfile.USTAR_FORMAT) as destination:
                for member in members:
                    source = archive.extractfile(member)
                    if source is None:
                        raise PaperworkError(f"archive member cannot be reconstructed: {member.name}", INTEGRITY)
                    destination.addfile(_tar_info(member.name, member.size, member.mode), source)
            rebuilt.seek(0)
            archive_snapshot.seek(0)
            while True:
                original_block = archive_snapshot.read(1024 * 1024)
                rebuilt_block = rebuilt.read(1024 * 1024)
                if original_block != rebuilt_block:
                    raise PaperworkError(
                        "archive bytes are not the exact canonical USTAR representation",
                        INTEGRITY,
                    )
                if not original_block:
                    break
        except PaperworkError:
            raise
        except (OSError, tarfile.TarError, EOFError, UnicodeError, ValueError) as exc:
            raise PaperworkError(f"archive cannot be reconstructed canonically: {exc}", INTEGRITY) from exc


def verify_pack(pack_value: str) -> tuple[int, dict[str, Any]]:
    pack = Path(pack_value)
    sidecar = Path(f"{pack}.sha256")
    receipt_path = Path(f"{pack}.receipt.json")
    with (
        _open_regular(pack, "archive") as (pack, pack_handle, pack_metadata),
        _open_regular(sidecar, "archive SHA-256 sidecar", 4096) as (sidecar, sidecar_handle, sidecar_metadata),
        _open_regular(receipt_path, "archive receipt", 1024 * 1024) as (
            receipt_path,
            receipt_handle,
            receipt_metadata,
        ),
        _verification_tempfile("archive snapshot") as archive_snapshot,
    ):
        archive_digest = hashlib.sha256()
        for block in iter(lambda: pack_handle.read(1024 * 1024), b""):
            archive_digest.update(block)
            archive_snapshot.write(block)
        archive_hash = archive_digest.hexdigest()
        archive_snapshot.seek(0)

        expected_sidecar = f"{archive_hash}  {pack.name}\n".encode("utf-8")
        sidecar_content = _read_limited(sidecar_handle, 4096, "archive SHA-256 sidecar")
        if sidecar_content != expected_sidecar:
            raise PaperworkError("archive SHA-256 sidecar mismatch", INTEGRITY)
        receipt_content = _read_limited(receipt_handle, 1024 * 1024, "archive receipt")
        receipt = parse_json_bytes(
            receipt_content,
            "archive receipt JSON",
            INTEGRITY,
        )
        if (
            not isinstance(receipt, dict)
            or receipt_content != canonical_bytes(receipt)
            or set(receipt) != PACK_RECEIPT_FIELDS
        ):
            raise PaperworkError("archive receipt fields do not match the contract", INTEGRITY)
        require_utc_timestamp(receipt.get("created_at"), "archive receipt created_at", INTEGRITY)
        for field in ("archive_sha256", "validation_digest", "state_digest", "audit_head_sha256"):
            value = receipt.get(field)
            if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None:
                raise PaperworkError(f"archive receipt {field} is invalid", INTEGRITY)
        if (
            receipt.get("schema") != PACK_RECEIPT_SCHEMA
            or receipt.get("archive") != pack.name
            or receipt.get("archive_sha256") != archive_hash
            or receipt.get("plain_archive_acknowledged") is not True
            or receipt.get("contents") not in ("evidence", "full")
            or receipt.get("validation_status") not in ("PASS", "REVIEW")
            or not isinstance(receipt.get("actor"), str)
            or not receipt["actor"]
            or not isinstance(receipt.get("audit_count"), int)
            or isinstance(receipt.get("audit_count"), bool)
            or receipt["audit_count"] < 1
        ):
            raise PaperworkError("archive receipt mismatch", INTEGRITY)

        try:
            archive = tarfile.open(fileobj=archive_snapshot, mode="r:")
        except (OSError, tarfile.TarError) as exc:
            raise PaperworkError(f"invalid tar archive: {exc}", INTEGRITY) from exc
        with _read_tar(archive) as archive:
            members = archive.getmembers()
            if len(members) > 100_000:
                raise PaperworkError("archive contains too many members", INTEGRITY)
            names = [item.name for item in members]
            if len(names) != len(set(names)):
                raise PaperworkError("duplicate tar member", INTEGRITY)
            for member in members:
                if not _safe_tar_name(member.name) or not member.isfile() or member.issym() or member.islnk():
                    raise PaperworkError(f"unsafe tar member: {member.name}", INTEGRITY)
                if member.uid != 0 or member.gid != 0 or member.mtime != 0 or member.uname or member.gname:
                    raise PaperworkError(f"non-normalized tar metadata: {member.name}", INTEGRITY)
            if "PACK-MANIFEST.json" not in names:
                raise PaperworkError("pack manifest is missing", INTEGRITY)
            manifest_handle = archive.extractfile("PACK-MANIFEST.json")
            if manifest_handle is None:
                raise PaperworkError("pack manifest cannot be read", INTEGRITY)
            manifest_bytes = manifest_handle.read(10 * 1024 * 1024 + 1)
            if len(manifest_bytes) > 10 * 1024 * 1024:
                raise PaperworkError("pack manifest is too large", INTEGRITY)
            manifest = parse_json_bytes(manifest_bytes, "pack manifest JSON", INTEGRITY)
            if (
                not isinstance(manifest, dict)
                or manifest_bytes != canonical_bytes(manifest)
                or set(manifest) != PACK_MANIFEST_FIELDS
                or manifest.get("schema") != PACK_MANIFEST_SCHEMA
            ):
                raise PaperworkError("pack manifest is not canonical", INTEGRITY)
            for field in ("validation_digest", "state_digest", "audit_head_sha256"):
                value = manifest.get(field)
                if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None:
                    raise PaperworkError(f"pack manifest {field} is invalid", INTEGRITY)
            if (
                manifest.get("contents") not in ("evidence", "full")
                or manifest.get("validation_status") not in ("PASS", "REVIEW")
                or not isinstance(manifest.get("case_id"), str)
                or not manifest["case_id"]
                or not isinstance(manifest.get("actor"), str)
                or not manifest["actor"]
                or not isinstance(manifest.get("audit_count"), int)
                or isinstance(manifest.get("audit_count"), bool)
                or manifest["audit_count"] < 1
            ):
                raise PaperworkError("pack manifest fields are invalid", INTEGRITY)
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
                if manifest.get(field) != receipt.get(field):
                    raise PaperworkError(f"{field} differs between manifest and receipt", INTEGRITY)

            entries = manifest.get("entries")
            if not isinstance(entries, list):
                raise PaperworkError("pack manifest entries are invalid", INTEGRITY)
            expected_names = {"PACK-MANIFEST.json"}
            entry_by_name: dict[str, dict[str, Any]] = {}
            for entry in entries:
                if (
                    not isinstance(entry, dict)
                    or set(entry) != {"path", "bytes", "sha256", "mode"}
                    or not isinstance(entry.get("path"), str)
                    or not _safe_tar_name(entry["path"])
                    or not isinstance(entry.get("bytes"), int)
                    or isinstance(entry.get("bytes"), bool)
                    or entry["bytes"] < 0
                    or not isinstance(entry.get("sha256"), str)
                    or re.fullmatch(r"[0-9a-f]{64}", entry["sha256"]) is None
                    or entry.get("mode") not in (0o400, 0o600)
                ):
                    raise PaperworkError("pack manifest contains an unsafe entry", INTEGRITY)
                name = entry["path"]
                if name != "PACK-APPROVAL-NOTE.txt" and not name.startswith("case/"):
                    raise PaperworkError(f"manifest entry is outside the case contract: {name}", INTEGRITY)
                if name in entry_by_name:
                    raise PaperworkError(f"duplicate manifest entry: {name}", INTEGRITY)
                entry_by_name[name] = entry
                expected_names.add(name)
                try:
                    member = archive.getmember(name)
                except KeyError as exc:
                    raise PaperworkError(f"manifest member is missing: {name}", INTEGRITY) from exc
                handle = archive.extractfile(member)
                if handle is None:
                    raise PaperworkError(f"manifest member cannot be read: {name}", INTEGRITY)
                member_digest = hashlib.sha256()
                size = 0
                for block in iter(lambda: handle.read(1024 * 1024), b""):
                    member_digest.update(block)
                    size += len(block)
                if size != entry["bytes"] or member_digest.hexdigest() != entry["sha256"]:
                    raise PaperworkError(f"manifest member digest mismatch: {name}", INTEGRITY)
                if member.mode != entry["mode"]:
                    raise PaperworkError(f"manifest member mode mismatch: {name}", INTEGRITY)
            if set(names) != expected_names:
                raise PaperworkError("tar contains unmanifested members", INTEGRITY)
            required_case_members = {
                "case/case.json",
                "case/records/documents.jsonl",
                "case/records/pages.jsonl",
                "case/records/claims.jsonl",
                "case/records/approvals.jsonl",
                "case/records/findings.jsonl",
                "case/records/requirements.json",
                "case/review/queue.jsonl",
                "case/validation/latest.json",
            }
            if not required_case_members <= set(entry_by_name):
                raise PaperworkError("archive does not contain a complete verifiable case", INTEGRITY)
            approval = manifest.get("approval")
            note_name = "PACK-APPROVAL-NOTE.txt"
            note_present = note_name in entry_by_name
            if manifest["validation_status"] == "REVIEW" and approval is None:
                raise PaperworkError("REVIEW archives require a declared-human approval gate", INTEGRITY)
            if manifest["validation_status"] == "PASS" and (approval is not None or note_present):
                raise PaperworkError("PASS archives must not contain a review approval gate", INTEGRITY)
            if approval is None:
                if note_present:
                    raise PaperworkError("archive contains an approval note without an approval gate", INTEGRITY)
            else:
                approved_by = approval.get("approved_by") if isinstance(approval, dict) else None
                note_sha256 = approval.get("note_sha256") if isinstance(approval, dict) else None
                if (
                    not isinstance(approval, dict)
                    or set(approval) != {"approved_by", "declared_human", "note_path", "note_sha256"}
                    or approval.get("declared_human") is not True
                    or not isinstance(approved_by, str)
                    or approved_by != approved_by.strip()
                    or not approved_by
                    or approved_by.lower() in {"codex", "model", "ai"}
                    or approval.get("note_path") != note_name
                    or not isinstance(note_sha256, str)
                    or re.fullmatch(r"[0-9a-f]{64}", note_sha256) is None
                    or entry_by_name.get(note_name, {}).get("sha256") != note_sha256
                ):
                    raise PaperworkError("archive approval note is not bound to the manifest", INTEGRITY)
                note_handle = archive.extractfile(note_name)
                if note_handle is None:
                    raise PaperworkError("archive approval note cannot be read", INTEGRITY)
                note_bytes = _read_limited(note_handle, 1024 * 1024, "archive approval note")
                try:
                    note_text = note_bytes.decode("utf-8")
                except UnicodeError as exc:
                    raise PaperworkError("archive approval note is not UTF-8", INTEGRITY) from exc
                if not note_text.strip():
                    raise PaperworkError("archive approval note is empty", INTEGRITY)

            expected_order = ([note_name] if approval is not None else []) + sorted(
                name for name in entry_by_name if name.startswith("case/")
            ) + ["PACK-MANIFEST.json"]
            if names != expected_order or archive.getmember("PACK-MANIFEST.json").mode != 0o600:
                raise PaperworkError("archive member order or manifest mode is not canonical", INTEGRITY)
            _materialize_and_verify_case(archive, entry_by_name, manifest)
            _require_canonical_archive(archive_snapshot, archive, members)

        try:
            pack_handle.seek(0)
            current_archive_digest = hashlib.sha256()
            for block in iter(lambda: pack_handle.read(1024 * 1024), b""):
                current_archive_digest.update(block)
            sidecar_handle.seek(0)
            current_sidecar = _read_limited(sidecar_handle, 4096, "archive SHA-256 sidecar")
            receipt_handle.seek(0)
            current_receipt = _read_limited(receipt_handle, 1024 * 1024, "archive receipt")
        except OSError as exc:
            raise PaperworkError(f"archive files changed during verification: {exc}", INTEGRITY) from exc
        if (
            current_archive_digest.hexdigest() != archive_hash
            or current_sidecar != sidecar_content
            or current_receipt != receipt_content
        ):
            raise PaperworkError("archive files changed during verification", INTEGRITY)
        _require_open_path_unchanged(pack, pack_handle, pack_metadata, "archive")
        _require_open_path_unchanged(sidecar, sidecar_handle, sidecar_metadata, "archive SHA-256 sidecar")
        _require_open_path_unchanged(receipt_path, receipt_handle, receipt_metadata, "archive receipt")
        validation_status = receipt["validation_status"]
    return (REVIEW if validation_status == "REVIEW" else PASS), {
        "command": "verify",
        "target": "pack",
        "status": "REVIEW" if validation_status == "REVIEW" else "PASS",
        "integrity_status": "PASS",
        "validation_status": validation_status,
        "ready_for_release": validation_status == "PASS",
        "pack": str(pack),
        "archive_sha256": archive_hash,
        "validation_digest": receipt["validation_digest"],
    }


def _case_files(root: Path, contents: str) -> list[Path]:
    # Both 2.10 modes retain every state-bound artifact so the packed case can
    # be extracted and independently verified. The label is reserved for a
    # future, separately versioned subset contract.
    _ = contents
    files: list[Path] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.name == ".paperwork.lock":
            continue
        files.append(path)
    return files


def _tar_info(name: str, size: int, mode: int) -> tarfile.TarInfo:
    info = tarfile.TarInfo(name)
    info.size = size
    info.mode = mode
    info.uid = 0
    info.gid = 0
    info.uname = ""
    info.gname = ""
    info.mtime = 0
    return info


def _temporary_file(directory: Path, label: str) -> tuple[Path, Any]:
    descriptor, name = tempfile.mkstemp(prefix=f".{label}-", dir=directory)
    try:
        os.fchmod(descriptor, 0o600)
    except OSError:
        pass
    return Path(name), os.fdopen(descriptor, "w+b")


def _write_open_temp(handle: Any, content: bytes) -> None:
    handle.write(content)
    handle.flush()
    os.fsync(handle.fileno())


class _HashingReader:
    def __init__(self, handle: Any):
        self.handle = handle
        self.digest = hashlib.sha256()
        self.bytes_read = 0

    def read(self, size: int = -1) -> bytes:
        block = self.handle.read(size)
        self.digest.update(block)
        self.bytes_read += len(block)
        return block


def pack(
    case_value: str,
    output_value: str,
    contents: str,
    actor: str,
    acknowledge_plain_archive: bool,
    allow_review: bool,
    approved_by: str | None,
    approval_note_file: str | None,
) -> tuple[int, dict[str, Any]]:
    if not acknowledge_plain_archive:
        raise PaperworkError("plain tar archives require --acknowledge-plain-archive", POLICY_DENIAL)
    root = validate_case_path(case_value, must_exist=True)
    output = validate_output_path(output_value, root)
    parent_existed = output.parent.exists()
    output.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    if not parent_existed:
        try:
            output.parent.chmod(0o700)
        except OSError:
            pass
    with case_lock(root, actor):
        state = verify_case_integrity(root, allow_lock=True)
        validation_path = case_paths(root)["validation"]
        if not validation_path.is_file():
            raise PaperworkError("case must be validated before packing", POLICY_DENIAL)
        validation = read_json(validation_path)
        if (
            validation.get("state_digest") != state["state_digest"]
            or validation.get("audit_head_sha256") != state["audit"]["head"]
            or validation.get("audit_count") != state["audit"]["count"]
        ):
            raise PaperworkError("latest validation is stale", INTEGRITY)
        status = validation.get("status")
        if status == "FAIL":
            raise PaperworkError("failed validation prohibits packing", POLICY_DENIAL)
        approval: dict[str, Any] | None = None
        approval_note: bytes | None = None
        if status == "REVIEW":
            if not allow_review or not approved_by or not approval_note_file:
                raise PaperworkError(
                    "review-bearing archives require --allow-review, --approved-by, and --approval-note-file",
                    POLICY_DENIAL,
                )
            if approved_by.strip().lower() in {"codex", "model", "ai"}:
                raise PaperworkError("archive approval must name a declared human", POLICY_DENIAL)
            note_path, approval_note = read_external_bytes(approval_note_file, 1024 * 1024, "approval note")
            if is_relative_to(note_path, root):
                raise PaperworkError("approval note must be outside the case root", POLICY_DENIAL)
            try:
                approval_note.decode("utf-8")
            except UnicodeError as exc:
                raise PaperworkError("approval note must be UTF-8 text", INVALID) from exc
            if not approval_note.strip():
                raise PaperworkError("approval note must not be empty", POLICY_DENIAL)
            approval = {
                "approved_by": approved_by.strip(),
                "declared_human": True,
                "note_path": "PACK-APPROVAL-NOTE.txt",
                "note_sha256": hashlib.sha256(approval_note).hexdigest(),
            }
        elif allow_review or approved_by or approval_note_file:
            raise PaperworkError("review approval flags are only valid for REVIEW cases", INVALID)
        if status not in ("PASS", "REVIEW"):
            raise PaperworkError("latest validation has an unknown status", INTEGRITY)

        expected_state = {entry["path"]: entry for entry in state["state_entries"]}
        validation_bytes = canonical_bytes(validation)
        expected_state["validation/latest.json"] = {
            "path": "validation/latest.json",
            "bytes": len(validation_bytes),
            "sha256": hashlib.sha256(validation_bytes).hexdigest(),
        }
        files = _case_files(root, contents)
        relative_files = {path.relative_to(root).as_posix(): path for path in files}
        if set(relative_files) != set(expected_state):
            raise PaperworkError("case files differ from the validated state snapshot", INTEGRITY)
        case_members: list[tuple[str, Path, int, dict[str, Any]]] = []
        for relative in sorted(relative_files):
            name = f"case/{relative}"
            mode = 0o400 if name.startswith("case/originals/") else 0o600
            case_members.append((name, relative_files[relative], mode, expected_state[relative]))

        archive_temp, archive_handle = _temporary_file(output.parent, "paperwork-archive")
        sidecar_temp, sidecar_handle = _temporary_file(output.parent, "paperwork-sha256")
        receipt_temp, receipt_handle = _temporary_file(output.parent, "paperwork-receipt")
        temporary = [archive_temp, sidecar_temp, receipt_temp]
        published: list[Path] = []
        archive_hash = ""
        try:
            entries: list[dict[str, Any]] = []
            with _write_tar(archive_handle) as archive:
                if approval_note is not None:
                    note_digest = hashlib.sha256(approval_note).hexdigest()
                    archive.addfile(
                        _tar_info("PACK-APPROVAL-NOTE.txt", len(approval_note), 0o600),
                        io.BytesIO(approval_note),
                    )
                    entries.append(
                        {
                            "path": "PACK-APPROVAL-NOTE.txt",
                            "bytes": len(approval_note),
                            "sha256": note_digest,
                            "mode": 0o600,
                        }
                    )
                for name, path, mode, expected in case_members:
                    with _open_regular(path, f"case member {name}") as (safe_path, handle, metadata):
                        if metadata.st_size != expected["bytes"]:
                            raise PaperworkError(f"case member size changed before packing: {name}", INTEGRITY)
                        reader = _HashingReader(handle)
                        archive.addfile(_tar_info(name, metadata.st_size, mode), reader)
                        digest = reader.digest.hexdigest()
                        if reader.bytes_read != expected["bytes"] or digest != expected["sha256"]:
                            raise PaperworkError(f"case member changed after validation: {name}", INTEGRITY)
                        _require_open_path_unchanged(safe_path, handle, metadata, f"case member {name}")
                    entries.append(
                        {
                            "path": name,
                            "bytes": expected["bytes"],
                            "sha256": expected["sha256"],
                            "mode": mode,
                        }
                    )
                manifest = {
                    "schema": PACK_MANIFEST_SCHEMA,
                    "case_id": state["case"]["case_id"],
                    "contents": contents,
                    "actor": actor,
                    "validation_status": status,
                    "validation_digest": validation["digest"],
                    "state_digest": validation["state_digest"],
                    "audit_head_sha256": validation["audit_head_sha256"],
                    "audit_count": validation["audit_count"],
                    "approval": approval,
                    "entries": sorted(entries, key=lambda item: item["path"]),
                }
                manifest_bytes = canonical_bytes(manifest)
                archive.addfile(
                    _tar_info("PACK-MANIFEST.json", len(manifest_bytes), 0o600),
                    io.BytesIO(manifest_bytes),
                )
            current = verify_case_integrity(root, allow_lock=True)
            if current["state_digest"] != validation["state_digest"]:
                raise PaperworkError("case changed while the archive was being built", CASE_LOCKED)
            archive_handle.flush()
            os.fsync(archive_handle.fileno())
            archive_handle.seek(0)
            archive_digest = hashlib.sha256()
            for block in iter(lambda: archive_handle.read(1024 * 1024), b""):
                archive_digest.update(block)
            archive_hash = archive_digest.hexdigest()
            _write_open_temp(sidecar_handle, f"{archive_hash}  {output.name}\n".encode("utf-8"))
            receipt = {
                "schema": PACK_RECEIPT_SCHEMA,
                "archive": output.name,
                "archive_sha256": archive_hash,
                "case_id": state["case"]["case_id"],
                "contents": contents,
                "actor": actor,
                "created_at": utc_now(),
                "validation_status": status,
                "validation_digest": validation["digest"],
                "state_digest": validation["state_digest"],
                "audit_head_sha256": validation["audit_head_sha256"],
                "audit_count": validation["audit_count"],
                "approval": approval,
                "plain_archive_acknowledged": True,
            }
            _write_open_temp(receipt_handle, canonical_bytes(receipt))
            publication = (
                (sidecar_temp, Path(f"{output}.sha256")),
                (receipt_temp, Path(f"{output}.receipt.json")),
                (archive_temp, output),
            )
            for source, destination in publication:
                os.link(source, destination)
                published.append(destination)
                source.unlink()
            verify_pack(str(output))
        except BaseException:
            for path in reversed(published):
                try:
                    path.unlink()
                except FileNotFoundError:
                    pass
            raise
        finally:
            for handle in (archive_handle, sidecar_handle, receipt_handle):
                if not handle.closed:
                    handle.close()
            for path in temporary:
                try:
                    path.unlink()
                except FileNotFoundError:
                    pass
    return (REVIEW if status == "REVIEW" else PASS), {
        "command": "pack",
        "status": status,
        "case": str(root),
        "output": str(output),
        "contents": contents,
        "archive_sha256": archive_hash,
        "validation_digest": validation["digest"],
    }
