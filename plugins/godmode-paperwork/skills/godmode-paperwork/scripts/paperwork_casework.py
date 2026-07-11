"""Schema-checked mutation commands for Paperwork evidence."""

from __future__ import annotations

import contextlib
import csv
from decimal import Decimal, ROUND_HALF_UP
import hashlib
from pathlib import Path
import re
from typing import Any

from paperwork_core import (
    APPROVAL_SCHEMA,
    CLAIM_SCHEMA,
    INVALID,
    PAGE_RESOLUTION_SCHEMA,
    PAGE_SCHEMA,
    PASS,
    POLICY_DENIAL,
    REQUIREMENTS_SCHEMA,
    REVIEW_SCHEMA,
    PaperworkError,
    append_audit,
    approval_scope_digest,
    atomic_write,
    canonical_digest,
    case_lock,
    case_mutation_transaction,
    case_paths,
    invalidate_validation,
    is_relative_to,
    page_artifact_path,
    parse_finite_decimal,
    parse_json_bytes,
    read_jsonl,
    read_external_bytes,
    sha256_file,
    upsert_records,
    validate_case_path,
    verify_case_integrity,
    write_json,
    write_jsonl,
)


RULE_FIELDS = {
    "required_claim": {"id", "type", "claim"},
    "required_document": {"id", "type", "sha256", "media_type"},
    "equals": {"id", "type", "left", "right"},
    "decimal_sum": {"id", "type", "terms", "total", "tolerance"},
    "date_order": {"id", "type", "before", "after"},
    "format": {"id", "type", "claim", "format"},
    "unique": {"id", "type", "claims"},
}


def _load_input(path_value: str, root: Path) -> dict[str, Any]:
    path, raw = read_external_bytes(path_value, 10 * 1024 * 1024, "mutation input")
    if is_relative_to(path, root):
        raise PaperworkError("mutation input must be outside the case root", POLICY_DENIAL)
    value = parse_json_bytes(raw, "mutation input JSON")
    if not isinstance(value, dict):
        raise PaperworkError("mutation input must contain one JSON object", INVALID)
    return value


@contextlib.contextmanager
def _mutation(root: Path, actor: str):
    with case_lock(root, actor):
        with case_mutation_transaction(root):
            yield


def _exact_fields(record: dict[str, Any], required: set[str], optional: set[str] | None = None) -> None:
    optional = optional or set()
    if not required <= set(record) or set(record) - required - optional:
        raise PaperworkError(
            f"record fields must be exactly required={sorted(required)} optional={sorted(optional)}",
            INVALID,
        )


def _slug(value: Any, label: str) -> str:
    if not isinstance(value, str) or re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,126}[a-z0-9])?", value) is None:
        raise PaperworkError(f"{label} must be a lowercase hyphenated identifier", INVALID)
    return value


def _bbox(value: Any) -> list[str]:
    if not isinstance(value, list) or len(value) != 4 or not all(isinstance(item, str) for item in value):
        raise PaperworkError("bbox must contain four decimal strings", INVALID)
    coordinates = [parse_finite_decimal(item, "bbox coordinate") for item in value]
    if any(item < 0 or item > 1 for item in coordinates) or coordinates[0] > coordinates[2] or coordinates[1] > coordinates[3]:
        raise PaperworkError("bbox must be normalized and ordered from 0 to 1", INVALID)
    return value


def _declared_human(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip() or value.strip().lower() in {"codex", "model", "ai"}:
        raise PaperworkError(f"{label} must explicitly name a declared human reviewer", POLICY_DENIAL)
    return value.strip()


def _require_casework(state: dict[str, Any]) -> None:
    if state["case"].get("assurance") != "CASEWORK":
        raise PaperworkError("this command requires CASEWORK assurance", POLICY_DENIAL)


def _validate_requirements(record: dict[str, Any]) -> None:
    _exact_fields(record, {"schema", "required_documents", "required_claims", "rules"})
    if record.get("schema") != REQUIREMENTS_SCHEMA:
        raise PaperworkError("wrong requirements schema", INVALID)
    required_documents = record["required_documents"]
    required_claims = record["required_claims"]
    rules = record["rules"]
    if not all(isinstance(item, list) for item in (required_documents, required_claims, rules)):
        raise PaperworkError("requirements fields must be arrays", INVALID)
    if not all(isinstance(item, str) and item for item in required_claims) or len(required_claims) != len(set(required_claims)):
        raise PaperworkError("required_claims must contain unique identifiers", INVALID)
    for document in required_documents:
        if not isinstance(document, dict) or not document or set(document) - {"sha256", "media_type"}:
            raise PaperworkError("required_documents entries may contain sha256 and media_type only", INVALID)
        if "sha256" in document and (
            not isinstance(document["sha256"], str)
            or re.fullmatch(r"[0-9a-f]{64}", document["sha256"]) is None
        ):
            raise PaperworkError("required document sha256 is invalid", INVALID)
        if "media_type" in document and (not isinstance(document["media_type"], str) or not document["media_type"]):
            raise PaperworkError("required document media_type is invalid", INVALID)
    seen_rules: set[str] = set()
    for rule in rules:
        if not isinstance(rule, dict) or not isinstance(rule.get("type"), str) or rule["type"] not in RULE_FIELDS:
            raise PaperworkError("requirements contain an unsupported rule type", INVALID)
        rule_type = rule["type"]
        allowed = RULE_FIELDS[rule_type]
        if set(rule) != allowed and not (rule_type == "required_document" and set(rule) <= allowed and {"id", "type"} < set(rule)):
            raise PaperworkError(f"rule {rule_type} has invalid fields", INVALID)
        rule_id = _slug(rule.get("id"), "rule id")
        if rule_id in seen_rules:
            raise PaperworkError(f"duplicate rule id: {rule_id}", INVALID)
        seen_rules.add(rule_id)
        if rule_type == "required_document":
            if "sha256" in rule and (
                not isinstance(rule["sha256"], str)
                or re.fullmatch(r"[0-9a-f]{64}", rule["sha256"]) is None
            ):
                raise PaperworkError(f"rule {rule_id} has invalid sha256", INVALID)
            if "media_type" in rule and (
                not isinstance(rule["media_type"], str) or not rule["media_type"]
            ):
                raise PaperworkError(f"rule {rule_id} has invalid media_type", INVALID)
        if rule_type == "format" and (
            not isinstance(rule.get("format"), str)
            or rule["format"] not in {"iso-date", "integer", "decimal", "currency", "iban"}
        ):
            raise PaperworkError("format rule uses an unsupported format", INVALID)
        for list_field in ("terms", "claims"):
            if list_field in rule and (
                not isinstance(rule[list_field], list)
                or not rule[list_field]
                or (list_field == "terms" and len(rule[list_field]) > 1000)
                or not all(isinstance(item, str) and item for item in rule[list_field])
            ):
                raise PaperworkError(f"rule {rule_id} has invalid {list_field}", INVALID)
        if "tolerance" in rule:
            tolerance = parse_finite_decimal(rule["tolerance"], f"rule {rule_id} tolerance")
            if tolerance < 0:
                raise PaperworkError(f"rule {rule_id} has invalid tolerance", INVALID)


def set_requirements(case_value: str, input_value: str, actor: str) -> tuple[int, dict[str, Any]]:
    root = validate_case_path(case_value, must_exist=True)
    record = _load_input(input_value, root)
    _validate_requirements(record)
    with _mutation(root, actor):
        state = verify_case_integrity(root, allow_lock=True)
        _require_casework(state)
        invalidate_validation(root)
        write_json(case_paths(root)["requirements"], record)
        append_audit(root, "REQUIREMENTS_SET", actor, {"requirements_sha256": canonical_digest(record)})
    return PASS, {"command": "requirements", "status": "PASS", "case": str(root)}


def _ocr_quote_bbox(root: Path, page: dict[str, Any], quote: str) -> list[str]:
    dimensions = page.get("ocr_page_dimensions")
    if (
        not isinstance(dimensions, dict)
        or set(dimensions) != {"width", "height"}
        or not isinstance(dimensions.get("width"), int)
        or not isinstance(dimensions.get("height"), int)
        or dimensions["width"] <= 0
        or dimensions["height"] <= 0
    ):
        raise PaperworkError("OCR page dimensions are missing", INVALID)
    tsv_record = next(
        (
            item
            for item in page.get("ocr_artifacts", [])
            if isinstance(item, dict) and str(item.get("path", "")).endswith(".tsv")
        ),
        None,
    )
    if tsv_record is None:
        raise PaperworkError("OCR TSV artifact is missing", INVALID)
    words: list[dict[str, Any]] = []
    try:
        with (root / tsv_record["path"]).open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle, delimiter="\t")
            required = {"level", "left", "top", "width", "height", "text"}
            if not reader.fieldnames or not required <= set(reader.fieldnames):
                raise PaperworkError("OCR TSV lacks positional fields", INVALID)
            for row in reader:
                text = row.get("text", "")
                if not isinstance(text, str) or not text.strip():
                    continue
                numeric = [row.get(field, "") for field in ("left", "top", "width", "height")]
                if any(not isinstance(value, str) or re.fullmatch(r"[0-9]{1,9}", value) is None for value in numeric):
                    raise PaperworkError("OCR TSV contains invalid word coordinates", INVALID)
                coordinates = {field: int(row[field]) for field in ("left", "top", "width", "height")}
                if (
                    coordinates["left"] + coordinates["width"] > dimensions["width"]
                    or coordinates["top"] + coordinates["height"] > dimensions["height"]
                ):
                    raise PaperworkError("OCR TSV word coordinates exceed page dimensions", INVALID)
                words.append({"text": text.strip(), **coordinates})
    except (OSError, UnicodeError, csv.Error, ValueError, ArithmeticError) as exc:
        raise PaperworkError(f"OCR TSV cannot be read: {exc}", INVALID) from exc
    quote_words = quote.split()
    if not quote_words:
        raise PaperworkError("OCR quote has no words", INVALID)
    matches: list[list[dict[str, Any]]] = []
    for start in range(0, len(words) - len(quote_words) + 1):
        candidate = words[start : start + len(quote_words)]
        if [item["text"] for item in candidate] == quote_words:
            matches.append(candidate)
    if len(matches) != 1:
        raise PaperworkError("OCR quote must map to exactly one contiguous TSV word sequence", INVALID)
    match = matches[0]
    left = min(item["left"] for item in match)
    top = min(item["top"] for item in match)
    right = max(item["left"] + item["width"] for item in match)
    bottom = max(item["top"] + item["height"] for item in match)
    values = (
        Decimal(left) / Decimal(dimensions["width"]),
        Decimal(top) / Decimal(dimensions["height"]),
        Decimal(right) / Decimal(dimensions["width"]),
        Decimal(bottom) / Decimal(dimensions["height"]),
    )
    return [format(value.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP), ".6f") for value in values]


def _validate_claim(root: Path, state: dict[str, Any], claim: dict[str, Any]) -> None:
    _exact_fields(claim, {"schema", "id", "name", "value", "critical", "anchors"})
    if claim.get("schema") != CLAIM_SCHEMA:
        raise PaperworkError("wrong claim schema", INVALID)
    _slug(claim.get("id"), "claim id")
    if not isinstance(claim.get("name"), str) or not claim["name"].strip() or not isinstance(claim.get("value"), str):
        raise PaperworkError("claim name and value must be strings", INVALID)
    if not isinstance(claim.get("critical"), bool):
        raise PaperworkError("claim critical must be boolean", INVALID)
    anchors = claim.get("anchors")
    if not isinstance(anchors, list) or not anchors:
        raise PaperworkError("claim requires at least one anchor", INVALID)
    pages = {(page["document"], page["page"]): page for page in state["pages"]}
    for anchor in anchors:
        if not isinstance(anchor, dict):
            raise PaperworkError("claim anchor must be an object", INVALID)
        method = anchor.get("method")
        document = anchor.get("document")
        page_number = anchor.get("page")
        if (
            not isinstance(method, str)
            or method not in {"NATIVE", "OCR", "VISUAL"}
            or not isinstance(document, str)
            or re.fullmatch(r"[0-9a-f]{64}", document) is None
            or not isinstance(page_number, int)
            or isinstance(page_number, bool)
            or page_number < 1
        ):
            raise PaperworkError("claim anchor method, document, or page is invalid", INVALID)
        required = {"document", "page", "quote", "artifact_sha256", "method"}
        optional = {"bbox"} if method in {"OCR", "VISUAL"} else set()
        _exact_fields(anchor, required, optional)
        page = pages.get((document, page_number))
        if page is None or page.get("route") != method:
            raise PaperworkError("claim anchor does not match a final page route", INVALID)
        if anchor.get("artifact_sha256") != page.get("artifact_sha256"):
            raise PaperworkError("claim anchor artifact hash differs from its page", INVALID)
        quote = anchor.get("quote")
        if not isinstance(quote, str) or not quote:
            raise PaperworkError("claim anchor quote must not be empty", INVALID)
        artifact = root / page["final_artifact"]
        try:
            artifact_text = artifact.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            raise PaperworkError(f"claim artifact cannot be read as UTF-8: {exc}", INVALID) from exc
        if quote not in artifact_text:
            raise PaperworkError("claim anchor quote is absent from the final artifact", INVALID)
        if method == "OCR":
            derived_bbox = _ocr_quote_bbox(root, page, quote)
            supplied_bbox = anchor.get("bbox")
            if supplied_bbox is None:
                anchor["bbox"] = derived_bbox
            else:
                _bbox(supplied_bbox)
                supplied_values = [parse_finite_decimal(item, "OCR bbox coordinate") for item in supplied_bbox]
                derived_values = [parse_finite_decimal(item, "derived OCR bbox coordinate") for item in derived_bbox]
                if supplied_values != derived_values:
                    raise PaperworkError("supplied OCR bbox does not match the deterministic TSV position", INVALID)
                anchor["bbox"] = derived_bbox
        elif method == "VISUAL":
            _bbox(anchor.get("bbox"))


def add_claim(case_value: str, input_value: str, actor: str) -> tuple[int, dict[str, Any]]:
    root = validate_case_path(case_value, must_exist=True)
    claim = _load_input(input_value, root)
    with _mutation(root, actor):
        state = verify_case_integrity(root, allow_lock=True)
        _require_casework(state)
        _validate_claim(root, state, claim)
        invalidate_validation(root)
        upsert_records(case_paths(root)["claims"], CLAIM_SCHEMA, [claim], ["id"])
        append_audit(
            root,
            "CLAIM_UPSERT",
            actor,
            {"claim_id": claim["id"], "claim_sha256": canonical_digest(claim)},
        )
    return PASS, {"command": "claim", "status": "PASS", "case": str(root), "claim_id": claim["id"]}


def _validate_approval(state: dict[str, Any], approval: dict[str, Any]) -> None:
    _exact_fields(
        approval,
        {"schema", "id", "human", "approved_by", "scope_type", "scope_id", "decision", "note"},
    )
    if approval.get("schema") != APPROVAL_SCHEMA or approval.get("human") is not True:
        raise PaperworkError("approval must declare schema and human=true", INVALID)
    _slug(approval.get("id"), "approval id")
    _declared_human(approval.get("approved_by"), "approved_by")
    if not isinstance(approval.get("scope_type"), str) or approval["scope_type"] not in ("claim", "page"):
        raise PaperworkError("approval scope_type is invalid", INVALID)
    if not isinstance(approval.get("decision"), str) or approval["decision"] not in (
        "CONFIRMED",
        "APPROVED_WITH_REVIEW",
    ):
        raise PaperworkError("approval decision is invalid", INVALID)
    if not isinstance(approval.get("note"), str) or not approval["note"].strip():
        raise PaperworkError("approval note must not be empty", INVALID)
    scope_id = approval.get("scope_id")
    if not isinstance(scope_id, str) or not scope_id:
        raise PaperworkError("approval scope_id must be a non-empty string", INVALID)
    if approval["scope_type"] == "claim" and scope_id not in {claim["id"] for claim in state["claims"]}:
        raise PaperworkError("approval references an unknown claim", INVALID)
    if approval["scope_type"] == "page":
        valid_pages = {f"{page['document']}:{page['page']}" for page in state["pages"]}
        if scope_id not in valid_pages:
            raise PaperworkError("approval references an unknown page", INVALID)
    approval["scope_digest"] = approval_scope_digest(state, approval["scope_type"], scope_id)


def add_approval(case_value: str, input_value: str, actor: str) -> tuple[int, dict[str, Any]]:
    root = validate_case_path(case_value, must_exist=True)
    approval = _load_input(input_value, root)
    with _mutation(root, actor):
        state = verify_case_integrity(root, allow_lock=True)
        _require_casework(state)
        _validate_approval(state, approval)
        invalidate_validation(root)
        upsert_records(case_paths(root)["approvals"], APPROVAL_SCHEMA, [approval], ["id"])
        append_audit(
            root,
            "APPROVAL_UPSERT",
            actor,
            {"approval_id": approval["id"], "approval_sha256": canonical_digest(approval)},
        )
    return PASS, {"command": "approve", "status": "PASS", "case": str(root), "approval_id": approval["id"]}


def resolve_page(case_value: str, input_value: str, actor: str) -> tuple[int, dict[str, Any]]:
    root = validate_case_path(case_value, must_exist=True)
    resolution = _load_input(input_value, root)
    _exact_fields(
        resolution,
        {"schema", "document", "page", "text", "bbox", "confirmed_by", "note"},
    )
    if resolution.get("schema") != PAGE_RESOLUTION_SCHEMA:
        raise PaperworkError("wrong page resolution schema", INVALID)
    document = resolution.get("document")
    page_number = resolution.get("page")
    if re.fullmatch(r"[0-9a-f]{64}", str(document)) is None or not isinstance(page_number, int) or isinstance(page_number, bool) or page_number < 1:
        raise PaperworkError("page resolution document/page is invalid", INVALID)
    text = resolution.get("text")
    if not isinstance(text, str) or not text.strip():
        raise PaperworkError("page resolution text must not be empty", INVALID)
    bbox = _bbox(resolution.get("bbox"))
    confirmed_by = _declared_human(resolution.get("confirmed_by"), "confirmed_by")
    note = resolution.get("note")
    if not isinstance(note, str) or not note.strip():
        raise PaperworkError("page resolution note must not be empty", INVALID)

    with _mutation(root, actor):
        state = verify_case_integrity(root, allow_lock=True)
        page = next(
            (item for item in state["pages"] if item["document"] == document and item["page"] == page_number),
            None,
        )
        if page is None or page.get("route") != "VISUAL_REVIEW":
            raise PaperworkError("page must pass through route into VISUAL_REVIEW before visual resolution", POLICY_DENIAL)
        invalidate_validation(root)
        final_relative = page_artifact_path(document, page_number, "final", "txt")
        final_path = root / final_relative
        atomic_write(final_path, text.encode("utf-8"))
        updated = dict(page)
        updated.update(
            {
                "route": "VISUAL",
                "final_artifact": final_relative,
                "artifact_sha256": sha256_file(final_path),
                "visual_resolution": {
                    "bbox": bbox,
                    "declared_by": confirmed_by,
                    "note_sha256": hashlib.sha256(note.encode("utf-8")).hexdigest(),
                },
            }
        )
        upsert_records(case_paths(root)["pages"], PAGE_SCHEMA, [updated], ["document", "page"])
        reviews = read_jsonl(case_paths(root)["reviews"], REVIEW_SCHEMA)
        for review in reviews:
            if review.get("status") == "OPEN" and review.get("document") == document and review.get("page") == page_number:
                review["status"] = "RESOLVED"
                review["resolved_by"] = confirmed_by
                review["resolution_note_sha256"] = hashlib.sha256(note.encode("utf-8")).hexdigest()
        write_jsonl(case_paths(root)["reviews"], reviews)
        append_audit(
            root,
            "PAGE_RESOLVED_VISUAL",
            actor,
            {
                "document": document,
                "page": page_number,
                "artifact_sha256": updated["artifact_sha256"],
                "declared_by": confirmed_by,
            },
        )
    return PASS, {
        "command": "resolve-page",
        "status": "PASS",
        "case": str(root),
        "document": document,
        "page": page_number,
    }
