"""Deterministic primitives for the offline GodMode Paperwork CLI."""

from __future__ import annotations

import contextlib
import datetime as dt
from decimal import Decimal, InvalidOperation
import hashlib
import json
import os
from pathlib import Path
from pathlib import PurePosixPath
import re
import shutil
import stat
import subprocess
import tempfile
import unicodedata
from typing import Any, Iterator, Sequence


VERSION = "2.10.0"
MAX_DECIMAL_CHARACTERS = 256

PASS = 0
REVIEW = 10
USAGE = 2
INVALID = 20
CAPABILITY_MISSING = 21
INTEGRITY = 22
PROCESSING = 23
VALIDATION_FAILED = 24
POLICY_DENIAL = 25
CASE_LOCKED = 26
INTERNAL = 70

ASSURANCE_LEVELS = ("INVENTORY", "EXTRACTION", "CASEWORK")
PROCESSABLE_MEDIA = {
    ".pdf": "application/pdf",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
}
INVENTORY_MEDIA = {
    ".tif": "image/tiff",
    ".tiff": "image/tiff",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".zip": "application/zip",
    ".tar": "application/x-tar",
    ".gz": "application/gzip",
}

CASE_SCHEMA = "godmode.paperwork.case/v1"
DOCUMENT_SCHEMA = "godmode.paperwork.document/v1"
PAGE_SCHEMA = "godmode.paperwork.page/v1"
CLAIM_SCHEMA = "godmode.paperwork.claim/v1"
APPROVAL_SCHEMA = "godmode.paperwork.approval/v1"
FINDING_SCHEMA = "godmode.paperwork.finding/v1"
REQUIREMENTS_SCHEMA = "godmode.paperwork.requirements/v1"
REVIEW_SCHEMA = "godmode.paperwork.review/v1"
VALIDATION_SCHEMA = "godmode.paperwork.validation/v1"
AUDIT_SCHEMA = "godmode.paperwork.audit/v1"
PACK_MANIFEST_SCHEMA = "godmode.paperwork.pack-manifest/v1"
PACK_RECEIPT_SCHEMA = "godmode.paperwork.pack-receipt/v1"
PAGE_RESOLUTION_SCHEMA = "godmode.paperwork.page-resolution/v1"

CASE_RECORDS = {
    "documents": DOCUMENT_SCHEMA,
    "pages": PAGE_SCHEMA,
    "claims": CLAIM_SCHEMA,
    "approvals": APPROVAL_SCHEMA,
    "findings": FINDING_SCHEMA,
}

GOVERNED_STATE_PATHS = (
    "records/documents.jsonl",
    "records/pages.jsonl",
    "records/claims.jsonl",
    "records/approvals.jsonl",
    "records/findings.jsonl",
    "records/requirements.json",
    "review/queue.jsonl",
)


class PaperworkError(Exception):
    """Controlled CLI failure with a stable exit status."""

    def __init__(self, message: str, code: int, details: dict[str, Any] | None = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def require_utc_timestamp(value: Any, label: str, code: int = INVALID) -> str:
    if not isinstance(value, str) or re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z", value) is None:
        raise PaperworkError(f"{label} must be canonical UTC ISO-8601", code)
    try:
        parsed = dt.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError as exc:
        raise PaperworkError(f"{label} must be canonical UTC ISO-8601", code) from exc
    if parsed.strftime("%Y-%m-%dT%H:%M:%SZ") != value:
        raise PaperworkError(f"{label} must be canonical UTC ISO-8601", code)
    return value


def parse_finite_decimal(value: Any, label: str, code: int = INVALID) -> Decimal:
    if (
        not isinstance(value, str)
        or len(value) > MAX_DECIMAL_CHARACTERS
        or re.fullmatch(r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?", value) is None
    ):
        raise PaperworkError(f"{label} must be a finite fixed-format decimal string", code)
    try:
        parsed = Decimal(value)
    except InvalidOperation as exc:
        raise PaperworkError(f"{label} must be a finite fixed-format decimal string", code) from exc
    if not parsed.is_finite():
        raise PaperworkError(f"{label} must be finite", code)
    return parsed


def normalize(value: Any) -> Any:
    if isinstance(value, str):
        normalized = unicodedata.normalize("NFC", value)
        if any(0xD800 <= ord(character) <= 0xDFFF for character in normalized):
            raise PaperworkError("Unicode surrogate code points are forbidden", INVALID)
        return normalized
    if isinstance(value, float):
        raise PaperworkError("floating-point values are forbidden; use decimal strings", INVALID)
    if isinstance(value, dict):
        if not all(isinstance(key, str) for key in value):
            raise PaperworkError("JSON object keys must be strings", INVALID)
        result: dict[str, Any] = {}
        for key, item in value.items():
            normalized_key = normalize(key)
            if normalized_key in result:
                raise PaperworkError("JSON object keys collide after Unicode normalization", INVALID)
            result[normalized_key] = normalize(item)
        return result
    if isinstance(value, list):
        return [normalize(item) for item in value]
    if value is None or isinstance(value, (bool, int)):
        return value
    raise PaperworkError(f"unsupported canonical JSON type: {type(value).__name__}", INVALID)


class _DuplicateJSONKeyError(ValueError):
    pass


def parse_json_bytes(raw: bytes, label: str, code: int = INVALID) -> Any:
    def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise _DuplicateJSONKeyError(f"duplicate object key: {key}")
            result[key] = value
        return result

    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=unique_object)
        return normalize(value)
    except (UnicodeError, json.JSONDecodeError, ValueError, OverflowError, RecursionError, PaperworkError) as exc:
        raise PaperworkError(f"invalid {label}: {exc}", code) from exc


def canonical_bytes(value: Any) -> bytes:
    data = normalize(value)
    return (json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def canonical_digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def assert_no_symlink_chain(raw_path: Path) -> Path:
    path = raw_path.expanduser()
    if not path.is_absolute():
        path = Path.cwd() / path
    cursor = path
    while True:
        if cursor.is_symlink():
            raise PaperworkError(f"symbolic links are forbidden: {cursor}", POLICY_DENIAL)
        if cursor.parent == cursor:
            break
        cursor = cursor.parent
    return path.resolve(strict=False)


def read_external_bytes(raw_path: str | Path, maximum_bytes: int, label: str) -> tuple[Path, bytes]:
    path = assert_no_symlink_chain(Path(raw_path))
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise PaperworkError(f"{label} cannot be opened safely: {exc}", POLICY_DENIAL) from exc
    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
            raise PaperworkError(f"{label} must be a regular non-linked file", POLICY_DENIAL)
        if metadata.st_size > maximum_bytes:
            raise PaperworkError(f"{label} exceeds {maximum_bytes} bytes", POLICY_DENIAL)
        with os.fdopen(descriptor, "rb", closefd=False) as handle:
            content = handle.read(maximum_bytes + 1)
        if len(content) > maximum_bytes:
            raise PaperworkError(f"{label} exceeds {maximum_bytes} bytes", POLICY_DENIAL)
        return path, content
    finally:
        os.close(descriptor)


def nearest_existing(path: Path) -> Path:
    cursor = path
    while not cursor.exists() and cursor.parent != cursor:
        cursor = cursor.parent
    return cursor


def git_worktree_for(path: Path) -> Path | None:
    cursor = nearest_existing(path)
    for ancestor in (cursor, *cursor.parents):
        if (ancestor / ".git").exists():
            return ancestor.resolve()
    git = shutil.which("git")
    if not git:
        return None
    try:
        result = subprocess.run(
            [git, "-C", str(cursor), "rev-parse", "--show-toplevel"],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
            env=tool_environment(),
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0 or not result.stdout.strip():
        return None
    return Path(result.stdout.strip()).resolve()


def is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def require_outside_git(path: Path, label: str) -> None:
    worktree = git_worktree_for(path)
    if worktree is not None:
        raise PaperworkError(f"{label} must be outside every Git worktree: {worktree}", POLICY_DENIAL)


def require_outside_runtime_roots(path: Path, label: str) -> None:
    home = Path.home().resolve()
    codex_home = Path(os.environ.get("CODEX_HOME", str(home / ".codex"))).expanduser().resolve(strict=False)
    reserved = (codex_home, (home / ".agents").resolve(strict=False))
    for root in reserved:
        if is_relative_to(path, root):
            raise PaperworkError(f"{label} must be outside Codex and skill runtime storage: {root}", POLICY_DENIAL)


def validate_case_path(raw_path: str | Path, *, must_exist: bool) -> Path:
    path = assert_no_symlink_chain(Path(raw_path))
    if path == Path.home().resolve():
        raise PaperworkError("the home directory cannot be used as a case root", POLICY_DENIAL)
    require_outside_runtime_roots(path, "case root")
    require_outside_git(path, "case root")
    if must_exist:
        if not path.is_dir() or not (path / "case.json").is_file():
            raise PaperworkError(f"not a Paperwork case: {path}", INVALID)
    elif path.exists() and not path.is_dir():
        raise PaperworkError(f"case root is not a directory: {path}", INVALID)
    return path


def validate_output_path(raw_path: str | Path, case_root: Path) -> Path:
    path = assert_no_symlink_chain(Path(raw_path))
    if path.suffixes[-2:] != [".paperwork", ".tar"]:
        raise PaperworkError("archive output must end in .paperwork.tar", INVALID)
    if is_relative_to(path, case_root):
        raise PaperworkError("archive output must be outside the case root", POLICY_DENIAL)
    require_outside_runtime_roots(path, "archive output")
    require_outside_git(path, "archive output")
    for candidate in (path, Path(f"{path}.sha256"), Path(f"{path}.receipt.json")):
        if candidate.exists() or candidate.is_symlink():
            raise PaperworkError(f"refusing to overwrite output: {candidate}", POLICY_DENIAL)
    return path


def ensure_dir(path: Path, mode: int = 0o700) -> None:
    try:
        path.mkdir(parents=True, exist_ok=True)
        before = path.lstat()
        if not stat.S_ISDIR(before.st_mode):
            raise PaperworkError("private directory is linked or not a directory", INTEGRITY)
        path.chmod(mode)
        after = path.lstat()
    except PaperworkError:
        raise
    except OSError as exc:
        raise PaperworkError("private directory cannot be prepared", PROCESSING) from exc
    if not stat.S_ISDIR(after.st_mode) or stat.S_IMODE(after.st_mode) != mode:
        raise PaperworkError("private directory permissions do not match the required mode", PROCESSING)


def atomic_write(path: Path, content: bytes, mode: int = 0o600) -> None:
    ensure_dir(path.parent)
    descriptor, temp_name = tempfile.mkstemp(prefix=f".{path.name}.tmp-", dir=path.parent)
    temp = Path(temp_name)
    try:
        try:
            os.fchmod(descriptor, mode)
        except OSError:
            pass
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, path)
        try:
            path.chmod(mode)
        except OSError:
            pass
    finally:
        if temp.exists():
            temp.unlink()


def write_json(path: Path, value: Any, mode: int = 0o600) -> None:
    atomic_write(path, canonical_bytes(value), mode)


def read_json(path: Path) -> Any:
    try:
        with path.open("rb") as handle:
            raw = handle.read()
    except OSError as exc:
        raise PaperworkError(f"invalid JSON file {path}: {exc}", INVALID) from exc
    normalized = parse_json_bytes(raw, f"JSON file {path}")
    if raw != canonical_bytes(normalized):
        raise PaperworkError(f"non-canonical JSON file: {path}", INVALID)
    return normalized


def read_jsonl(path: Path, schema: str | None = None) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise PaperworkError(f"cannot read record file {path}: {exc}", INVALID) from exc
    for number, line in enumerate(lines, 1):
        if not line:
            raise PaperworkError(f"blank JSONL line in {path}:{number}", INVALID)
        try:
            record = parse_json_bytes(line.encode("utf-8"), f"JSONL record in {path}:{number}")
        except PaperworkError as exc:
            raise PaperworkError(f"invalid JSONL record in {path}:{number}: {exc}", INVALID) from exc
        if not isinstance(record, dict):
            raise PaperworkError(f"JSONL record must be an object in {path}:{number}", INVALID)
        if schema and record.get("schema") != schema:
            raise PaperworkError(f"wrong schema in {path}:{number}", INVALID)
        if canonical_bytes(record).decode("utf-8").rstrip("\n") != line:
            raise PaperworkError(f"non-canonical JSONL record in {path}:{number}", INVALID)
        records.append(record)
    return records


def write_jsonl(path: Path, records: Sequence[dict[str, Any]]) -> None:
    content = b"".join(canonical_bytes(record) for record in records)
    atomic_write(path, content)


def _read_json_for_integrity(path: Path) -> Any:
    try:
        return read_json(path)
    except PaperworkError as exc:
        if exc.code == INVALID:
            raise PaperworkError(exc.message, INTEGRITY) from exc
        raise


def _read_jsonl_for_integrity(path: Path, schema: str) -> list[dict[str, Any]]:
    try:
        return read_jsonl(path, schema)
    except PaperworkError as exc:
        if exc.code == INVALID:
            raise PaperworkError(exc.message, INTEGRITY) from exc
        raise


def upsert_records(
    path: Path,
    schema: str,
    additions: Sequence[dict[str, Any]],
    key_fields: Sequence[str],
) -> list[dict[str, Any]]:
    current = read_jsonl(path, schema)
    keyed = {tuple(record.get(field) for field in key_fields): record for record in current}
    for record in additions:
        if record.get("schema") != schema:
            raise PaperworkError(f"record does not match {schema}", INVALID)
        keyed[tuple(record.get(field) for field in key_fields)] = record
    ordered = [keyed[key] for key in sorted(keyed, key=lambda item: tuple(str(part) for part in item))]
    write_jsonl(path, ordered)
    return ordered


def tool_environment() -> dict[str, str]:
    environment = os.environ.copy()
    environment.update({"LC_ALL": "C", "LANG": "C", "TZ": "UTC", "OMP_THREAD_LIMIT": "1"})
    return environment


def run_tool(arguments: Sequence[str], timeout: int, *, text: bool = False) -> subprocess.CompletedProcess[Any]:
    if not arguments or not all(isinstance(item, str) and item for item in arguments):
        raise PaperworkError("invalid subprocess arguments", INTERNAL)
    try:
        return subprocess.run(
            list(arguments),
            check=False,
            capture_output=True,
            text=text,
            timeout=timeout,
            env=tool_environment(),
        )
    except subprocess.TimeoutExpired as exc:
        raise PaperworkError(f"tool timed out after {timeout}s: {Path(arguments[0]).name}", PROCESSING) from exc
    except OSError as exc:
        raise PaperworkError(f"tool could not run: {arguments[0]}: {exc}", PROCESSING) from exc


def capability_executable(name: str) -> dict[str, Any]:
    resolved = shutil.which(name)
    if not resolved:
        return {"name": name, "present": False}
    path = Path(resolved).resolve()
    version = "unknown"
    for flag in ("--version", "-v"):
        try:
            result = run_tool([str(path), flag], 10, text=True)
        except PaperworkError:
            continue
        output = (result.stdout or "") + (result.stderr or "")
        if result.returncode == 0 and output.strip():
            version = output.strip().splitlines()[0][:200]
            break
    digest = None
    try:
        if path.is_file():
            digest = sha256_file(path)
    except OSError:
        pass
    return {"name": name, "present": True, "path": str(path), "version": version, "sha256": digest}


def executable_provenance(
    executable: str,
    argument_contract: list[str],
    *,
    language_data: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    path = Path(executable).resolve()
    if not path.is_file():
        raise PaperworkError(f"tool executable is not a file: {path}", CAPABILITY_MISSING)
    version = "unknown"
    for flag in ("--version", "-v"):
        result = run_tool([str(path), flag], 10, text=True)
        output = (result.stdout or "") + (result.stderr or "")
        if result.returncode == 0 and output.strip():
            version = output.strip().splitlines()[0][:200]
            break
    if version == "unknown":
        raise PaperworkError(f"tool version could not be determined: {path}", CAPABILITY_MISSING)
    return {
        "executable": str(path),
        "executable_sha256": sha256_file(path),
        "version": version,
        "argument_contract": argument_contract,
        "language_data": language_data or [],
    }


def case_paths(root: Path) -> dict[str, Path]:
    return {
        "case": root / "case.json",
        "documents": root / "records" / "documents.jsonl",
        "pages": root / "records" / "pages.jsonl",
        "claims": root / "records" / "claims.jsonl",
        "approvals": root / "records" / "approvals.jsonl",
        "findings": root / "records" / "findings.jsonl",
        "requirements": root / "records" / "requirements.json",
        "reviews": root / "review" / "queue.jsonl",
        "validation": root / "validation" / "latest.json",
        "lock": root / ".paperwork.lock",
    }


@contextlib.contextmanager
def case_mutation_transaction(root: Path) -> Iterator[None]:
    """Restore governed state and remove newly created case files on failure."""

    original_files: set[str] = set()
    original_directories: set[str] = set()
    snapshots: dict[str, tuple[bytes, int]] = {}
    root_mode = stat.S_IMODE(root.stat().st_mode)
    try:
        for path in sorted(root.rglob("*")):
            relative = path.relative_to(root).as_posix()
            if path.is_symlink():
                raise PaperworkError(f"symbolic link in case transaction: {path}", INTEGRITY)
            if path.is_file():
                original_files.add(relative)
                if relative == "case.json" or relative.startswith(("records/", "review/", "validation/")):
                    metadata = path.stat()
                    snapshots[relative] = (path.read_bytes(), stat.S_IMODE(metadata.st_mode))
            elif path.is_dir():
                original_directories.add(relative)
        yield
    except BaseException as original_error:
        rollback_errors: list[str] = []
        try:
            current_paths = sorted(root.rglob("*"), key=lambda item: (len(item.parts), str(item)), reverse=True)
        except OSError as exc:
            current_paths = []
            rollback_errors.append(str(exc))
        for path in current_paths:
            relative = path.relative_to(root).as_posix()
            try:
                if (path.is_file() or path.is_symlink()) and relative not in original_files:
                    path.unlink()
            except OSError as exc:
                rollback_errors.append(f"remove {relative}: {exc}")
        for relative, (content, mode) in snapshots.items():
            try:
                atomic_write(root / relative, content, mode)
            except OSError as exc:
                rollback_errors.append(f"restore {relative}: {exc}")
        for path in current_paths:
            relative = path.relative_to(root).as_posix()
            if relative in original_directories:
                continue
            try:
                if path.is_dir() and not path.is_symlink():
                    path.rmdir()
            except OSError:
                pass
        try:
            root.chmod(root_mode)
        except OSError as exc:
            rollback_errors.append(f"restore case-root mode: {exc}")
        if rollback_errors:
            raise PaperworkError(
                "case transaction rollback failed: " + "; ".join(rollback_errors),
                INTEGRITY,
            ) from original_error
        raise


def initialize_case(root: Path, case_id: str, assurance: str, languages: list[str]) -> None:
    if not re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?", case_id):
        raise PaperworkError("case-id must be a lowercase hyphenated slug of at most 64 characters", INVALID)
    if assurance not in ASSURANCE_LEVELS:
        raise PaperworkError(f"unsupported assurance level: {assurance}", INVALID)
    if not languages or any(not re.fullmatch(r"[A-Za-z0-9_-]+", language) for language in languages):
        raise PaperworkError("languages must be a non-empty comma-separated safe identifier list", INVALID)
    existing_entries = [item for item in root.iterdir() if item.name != ".paperwork.lock"] if root.exists() else []
    if existing_entries:
        if not (root / "case.json").is_file():
            raise PaperworkError("case root exists and is not empty", POLICY_DENIAL)
        case = read_json(root / "case.json")
        if case.get("case_id") != case_id:
            raise PaperworkError("case-id does not match the existing case", POLICY_DENIAL)
        return
    for relative in ("originals", "records", "work", "review", "validation", "audit"):
        ensure_dir(root / relative)
    paths = case_paths(root)
    for name, schema in CASE_RECORDS.items():
        write_jsonl(paths[name], [])
    write_jsonl(paths["reviews"], [])
    write_json(
        paths["requirements"],
        {
            "schema": REQUIREMENTS_SCHEMA,
            "required_documents": [],
            "required_claims": [],
            "rules": [],
        },
    )
    created_at = utc_now()
    genesis_payload = {
        "schema": AUDIT_SCHEMA,
        "sequence": 1,
        "timestamp": created_at,
        "action": "GENESIS",
        "actor": "system",
        "previous_sha256": None,
        "details": {
            "schema": CASE_SCHEMA,
            "case_id": case_id,
            "assurance": assurance,
            "languages": languages,
            "created_at": created_at,
            "tool_version": VERSION,
            "state_files": governed_state_files(root),
        },
    }
    genesis_sha256 = canonical_digest(genesis_payload)
    write_json(
        paths["case"],
        {
            "schema": CASE_SCHEMA,
            "case_id": case_id,
            "assurance": assurance,
            "languages": languages,
            "created_at": created_at,
            "tool_version": VERSION,
            "audit_genesis_sha256": genesis_sha256,
            "audit_head_sha256": genesis_sha256,
            "audit_count": 1,
        },
    )
    genesis_record = dict(genesis_payload)
    genesis_record["event_sha256"] = genesis_sha256
    write_json(root / "audit" / f"000001-{genesis_sha256}.json", genesis_record)


@contextlib.contextmanager
def case_lock(root: Path, actor: str) -> Iterator[None]:
    lock_path = case_paths(root)["lock"]
    try:
        descriptor = os.open(lock_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as exc:
        raise PaperworkError(f"case is locked: {lock_path}", CASE_LOCKED) from exc
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(canonical_bytes({"actor": actor, "pid": os.getpid(), "started_at": utc_now()}))
        yield
    finally:
        try:
            lock_path.unlink()
        except FileNotFoundError:
            pass


def append_audit(root: Path, action: str, actor: str, details: dict[str, Any]) -> dict[str, Any]:
    if not case_paths(root)["lock"].is_file():
        raise PaperworkError("audit mutations require the case lock", INTERNAL)
    audit_dir = root / "audit"
    ensure_dir(audit_dir)
    files = sorted(audit_dir.glob("*.json"))
    if not files:
        raise PaperworkError("audit genesis is missing", INTEGRITY)
    case = _read_json_for_integrity(case_paths(root)["case"])
    previous = case.get("audit_head_sha256")
    if len(files) != case.get("audit_count"):
        raise PaperworkError("audit count differs from case.json", INTEGRITY)
    audited_details = dict(details)
    audited_details["state_files"] = governed_state_files(root)
    payload = {
        "schema": AUDIT_SCHEMA,
        "sequence": case["audit_count"] + 1,
        "timestamp": utc_now(),
        "action": action,
        "actor": actor,
        "previous_sha256": previous,
        "details": audited_details,
    }
    event_sha = canonical_digest(payload)
    record = dict(payload)
    record["event_sha256"] = event_sha
    path = audit_dir / f"{payload['sequence']:06d}-{event_sha}.json"
    write_json(path, record)
    case["audit_head_sha256"] = event_sha
    case["audit_count"] = payload["sequence"]
    write_json(case_paths(root)["case"], case)
    return record


def invalidate_validation(root: Path) -> None:
    validation = case_paths(root)["validation"]
    if validation.exists():
        validation.unlink()


def governed_state_files(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for relative in GOVERNED_STATE_PATHS:
        path = root / relative
        if not path.is_file() or path.is_symlink() or path.stat().st_nlink != 1:
            raise PaperworkError(f"governed state file is missing or linked: {relative}", INTEGRITY)
        result[relative] = sha256_file(path)
    return result


def add_review(root: Path, reason: str, document: str | None = None, page: int | None = None) -> None:
    path = case_paths(root)["reviews"]
    current = read_jsonl(path, REVIEW_SCHEMA)
    identity = canonical_digest({"reason": reason, "document": document, "page": page})[:24]
    if any(item.get("id") == identity and item.get("status") == "OPEN" for item in current):
        return
    current.append(
        {
            "schema": REVIEW_SCHEMA,
            "id": identity,
            "status": "OPEN",
            "reason": reason,
            "document": document,
            "page": page,
        }
    )
    write_jsonl(path, sorted(current, key=lambda item: item["id"]))


def verify_audit(root: Path, case: dict[str, Any]) -> dict[str, Any]:
    previous = None
    files = sorted((root / "audit").glob("*.json"))
    if not files:
        raise PaperworkError("audit chain is empty", INTEGRITY)
    head = None
    for expected_sequence, path in enumerate(files, 1):
        record = _read_json_for_integrity(path)
        if not isinstance(record, dict) or record.get("schema") != AUDIT_SCHEMA or record.get("sequence") != expected_sequence:
            raise PaperworkError(f"invalid audit sequence: {path}", INTEGRITY)
        require_utc_timestamp(record.get("timestamp"), "audit timestamp", INTEGRITY)
        event_sha = record.get("event_sha256")
        payload = dict(record)
        payload.pop("event_sha256", None)
        if event_sha != canonical_digest(payload):
            raise PaperworkError(f"audit digest mismatch: {path}", INTEGRITY)
        if record.get("previous_sha256") != previous:
            raise PaperworkError(f"broken audit chain: {path}", INTEGRITY)
        if path.name != f"{expected_sequence:06d}-{event_sha}.json":
            raise PaperworkError(f"audit filename mismatch: {path}", INTEGRITY)
        previous = event_sha
        head = event_sha
        if expected_sequence == 1:
            expected_details = {
                "schema": case.get("schema"),
                "case_id": case.get("case_id"),
                "assurance": case.get("assurance"),
                "languages": case.get("languages"),
                "created_at": case.get("created_at"),
                "tool_version": case.get("tool_version"),
            }
            genesis_details = record.get("details")
            if (
                record.get("action") != "GENESIS"
                or record.get("actor") != "system"
                or not isinstance(genesis_details, dict)
                or any(genesis_details.get(key) != value for key, value in expected_details.items())
                or not isinstance(genesis_details.get("state_files"), dict)
                or event_sha != case.get("audit_genesis_sha256")
                or record.get("timestamp") != case.get("created_at")
            ):
                raise PaperworkError("audit genesis does not match case.json", INTEGRITY)
    if case.get("audit_count") != len(files) or case.get("audit_head_sha256") != head:
        raise PaperworkError("audit head or count differs from case.json", INTEGRITY)
    latest = _read_json_for_integrity(files[-1])
    if not isinstance(latest, dict) or not isinstance(latest.get("details"), dict):
        raise PaperworkError("latest audit event is not an object", INTEGRITY)
    latest_state_files = latest["details"].get("state_files")
    if latest_state_files != governed_state_files(root):
        raise PaperworkError("governed state differs from the latest audit receipt", INTEGRITY)
    return {"head": head, "count": len(files), "last": latest}


def strict_relative_posix(value: Any, expected: str, label: str) -> str:
    if not isinstance(value, str) or not value or "\\" in value:
        raise PaperworkError(f"{label} must be a relative POSIX path", INTEGRITY)
    pure = PurePosixPath(value)
    if pure.is_absolute() or ".." in pure.parts or pure.as_posix() != value or value != expected:
        raise PaperworkError(f"{label} does not match its document/page key", INTEGRITY)
    return value


def document_original_path(digest: str) -> str:
    return f"originals/{digest[:2]}/{digest}"


def page_artifact_path(document: str, page: int, stage: str, extension: str) -> str:
    return f"work/{document}/{stage}/page-{page:04d}.{extension}"


def compute_state_entries(root: Path) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    excluded = {".paperwork.lock", "validation/latest.json"}
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        if relative in excluded:
            continue
        if path.is_symlink() or path.stat().st_nlink != 1:
            raise PaperworkError(f"linked file cannot enter state digest: {relative}", INTEGRITY)
        entries.append({"path": relative, "bytes": path.stat().st_size, "sha256": sha256_file(path)})
    return entries


def compute_state_digest(root: Path) -> str:
    entries = compute_state_entries(root)
    return canonical_digest({"schema": "godmode.paperwork.state/v1", "files": entries})


def approval_scope_digest(state: dict[str, Any], scope_type: str, scope_id: str) -> str:
    if scope_type == "claim":
        target = next((item for item in state["claims"] if item.get("id") == scope_id), None)
    elif scope_type == "page":
        target = next(
            (item for item in state["pages"] if f"{item.get('document')}:{item.get('page')}" == scope_id),
            None,
        )
    else:
        target = None
    if target is None:
        raise PaperworkError("approval scope does not resolve to the current case object", INVALID)
    return canonical_digest(target)


def expected_case_file(path: Path, root: Path) -> bool:
    relative = path.relative_to(root).as_posix()
    fixed = {
        "case.json",
        "records/documents.jsonl",
        "records/pages.jsonl",
        "records/claims.jsonl",
        "records/approvals.jsonl",
        "records/findings.jsonl",
        "records/requirements.json",
        "review/queue.jsonl",
        "validation/latest.json",
    }
    if relative in fixed:
        return True
    if re.fullmatch(r"originals/[0-9a-f]{2}/[0-9a-f]{64}", relative):
        return True
    if re.fullmatch(r"audit/[0-9]{6}-[0-9a-f]{64}\.json", relative):
        return True
    if re.fullmatch(r"work/[0-9a-f]{64}/(?:native|final)/page-[0-9]{4}\.txt", relative):
        return True
    if re.fullmatch(r"work/[0-9a-f]{64}/render/page-[0-9]{4}\.png", relative):
        return True
    if re.fullmatch(r"work/[0-9a-f]{64}/ocr/page-[0-9]{4}\.(?:txt|tsv|hocr)", relative):
        return True
    return False


def _verify_provenance(provenance: Any, key: tuple[str, int]) -> None:
    if not isinstance(provenance, dict):
        raise PaperworkError(f"missing tool provenance: {key}", INTEGRITY)
    for name, record in provenance.items():
        if not isinstance(name, str) or not isinstance(record, dict):
            raise PaperworkError(f"invalid tool provenance: {key}", INTEGRITY)
        executable = record.get("executable")
        executable_hash = record.get("executable_sha256")
        contract = record.get("argument_contract")
        if (
            not isinstance(executable, str)
            or not Path(executable).is_absolute()
            or not isinstance(executable_hash, str)
            or re.fullmatch(r"[0-9a-f]{64}", executable_hash) is None
            or not isinstance(record.get("version"), str)
            or not isinstance(contract, list)
            or not contract
            or not all(isinstance(item, str) and item for item in contract)
        ):
            raise PaperworkError(f"incomplete tool provenance for {name}: {key}", INTEGRITY)
        language_data = record.get("language_data", [])
        if not isinstance(language_data, list):
            raise PaperworkError(f"invalid language provenance for {name}: {key}", INTEGRITY)
        for language in language_data:
            if (
                not isinstance(language, dict)
                or not isinstance(language.get("language"), str)
                or not isinstance(language.get("path"), str)
                or not Path(language["path"]).is_absolute()
                or re.fullmatch(r"[0-9a-f]{64}", str(language.get("sha256", ""))) is None
            ):
                raise PaperworkError(f"invalid language data provenance for {name}: {key}", INTEGRITY)


def verify_case_integrity(
    root: Path,
    *,
    check_unexpected: bool = True,
    allow_lock: bool = False,
    verify_validation: bool = True,
) -> dict[str, Any]:
    paths = case_paths(root)
    if paths["lock"].exists() and not allow_lock:
        raise PaperworkError(f"case is locked: {paths['lock']}", CASE_LOCKED)
    case = _read_json_for_integrity(paths["case"])
    if (
        not isinstance(case, dict)
        or case.get("schema") != CASE_SCHEMA
        or set(case)
        != {
            "schema",
            "case_id",
            "assurance",
            "languages",
            "created_at",
            "tool_version",
            "audit_genesis_sha256",
            "audit_head_sha256",
            "audit_count",
        }
        or case.get("assurance") not in ASSURANCE_LEVELS
        or re.fullmatch(r"[0-9a-f]{64}", str(case.get("audit_genesis_sha256", ""))) is None
        or re.fullmatch(r"[0-9a-f]{64}", str(case.get("audit_head_sha256", ""))) is None
        or not isinstance(case.get("audit_count"), int)
        or isinstance(case.get("audit_count"), bool)
        or case["audit_count"] < 1
    ):
        raise PaperworkError("invalid case schema", INTEGRITY)
    require_utc_timestamp(case.get("created_at"), "case created_at", INTEGRITY)
    documents = _read_jsonl_for_integrity(paths["documents"], DOCUMENT_SCHEMA)
    pages = _read_jsonl_for_integrity(paths["pages"], PAGE_SCHEMA)
    claims = _read_jsonl_for_integrity(paths["claims"], CLAIM_SCHEMA)
    approvals = _read_jsonl_for_integrity(paths["approvals"], APPROVAL_SCHEMA)
    _read_jsonl_for_integrity(paths["findings"], FINDING_SCHEMA)
    reviews = _read_jsonl_for_integrity(paths["reviews"], REVIEW_SCHEMA)
    requirements = _read_json_for_integrity(paths["requirements"])
    if not isinstance(requirements, dict) or requirements.get("schema") != REQUIREMENTS_SCHEMA:
        raise PaperworkError("invalid requirements schema", INTEGRITY)

    seen_hashes: set[str] = set()
    referenced_artifacts: set[str] = set()
    for document in documents:
        digest = document.get("sha256")
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise PaperworkError("invalid document hash", INTEGRITY)
        if digest in seen_hashes:
            raise PaperworkError(f"duplicate document record: {digest}", INTEGRITY)
        seen_hashes.add(digest)
        original_relative = strict_relative_posix(
            document.get("original"), document_original_path(digest), f"document original {digest}"
        )
        referenced_artifacts.add(original_relative)
        original = root / original_relative
        if not original.is_file() or sha256_file(original) != digest:
            raise PaperworkError(f"original integrity failure: {digest}", INTEGRITY)
        if original.stat().st_size != document.get("bytes"):
            raise PaperworkError(f"original size mismatch: {digest}", INTEGRITY)
        names = document.get("source_names")
        if (
            not isinstance(names, list)
            or not names
            or not all(isinstance(name, str) for name in names)
            or len(names) != len(set(names))
        ):
            raise PaperworkError(f"invalid deduplication aliases: {digest}", INTEGRITY)
        if any(Path(str(name)).is_absolute() or "/" in str(name) or "\\" in str(name) for name in names):
            raise PaperworkError(f"source alias leaks a path: {digest}", INTEGRITY)

    page_keys: set[tuple[str, int]] = set()
    for page in pages:
        page_number = page.get("page")
        document_hash = page.get("document")
        if not isinstance(page_number, int) or isinstance(page_number, bool):
            raise PaperworkError("page number must be an integer", INTEGRITY)
        key = (str(document_hash), page_number)
        if key in page_keys or key[0] not in seen_hashes or key[1] < 1:
            raise PaperworkError(f"invalid or duplicate page record: {key}", INTEGRITY)
        page_keys.add(key)
        artifact = page.get("final_artifact")
        artifact_hash = page.get("artifact_sha256")
        if artifact is not None:
            artifact_relative = strict_relative_posix(
                artifact,
                page_artifact_path(key[0], key[1], "final", "txt"),
                f"final artifact {key}",
            )
            artifact_path = root / artifact_relative
            referenced_artifacts.add(artifact_relative)
            if not artifact_path.is_file() or sha256_file(artifact_path) != artifact_hash:
                raise PaperworkError(f"page artifact integrity failure: {key}", INTEGRITY)
        for path_field, hash_field, stage, extension in (
            ("native_artifact", "native_sha256", "native", "txt"),
            ("render_artifact", "render_sha256", "render", "png"),
        ):
            candidate = page.get(path_field)
            if candidate is not None:
                candidate_relative = strict_relative_posix(
                    candidate,
                    page_artifact_path(key[0], key[1], stage, extension),
                    f"{path_field} {key}",
                )
                candidate_path = root / candidate_relative
                referenced_artifacts.add(candidate_relative)
                if not candidate_path.is_file() or sha256_file(candidate_path) != page.get(hash_field):
                    raise PaperworkError(f"page {path_field} integrity failure: {key}", INTEGRITY)
        ocr_artifacts = page.get("ocr_artifacts", [])
        if not isinstance(ocr_artifacts, list):
            raise PaperworkError(f"invalid OCR artifact list: {key}", INTEGRITY)
        seen_ocr_paths: set[str] = set()
        for candidate in ocr_artifacts:
            if not isinstance(candidate, dict):
                raise PaperworkError(f"invalid OCR artifact record: {key}", INTEGRITY)
            raw_path = candidate.get("path")
            valid_paths = {
                page_artifact_path(key[0], key[1], "ocr", extension)
                for extension in ("txt", "tsv", "hocr")
            }
            if (
                not isinstance(raw_path, str)
                or re.fullmatch(r"[0-9a-f]{64}", str(candidate.get("sha256", ""))) is None
                or raw_path not in valid_paths
                or raw_path in seen_ocr_paths
            ):
                raise PaperworkError(f"OCR artifact path does not match page key: {key}", INTEGRITY)
            candidate_relative = strict_relative_posix(raw_path, raw_path, f"OCR artifact {key}")
            seen_ocr_paths.add(candidate_relative)
            referenced_artifacts.add(candidate_relative)
            candidate_path = root / candidate_relative
            if not candidate_path.is_file() or sha256_file(candidate_path) != candidate.get("sha256"):
                raise PaperworkError(f"OCR artifact integrity failure: {key}", INTEGRITY)
        dimensions = page.get("ocr_page_dimensions")
        dimensions_valid = (
            isinstance(dimensions, dict)
            and set(dimensions) == {"width", "height"}
            and all(
                isinstance(dimensions.get(field), int)
                and not isinstance(dimensions.get(field), bool)
                and dimensions[field] > 0
                for field in ("width", "height")
            )
        )
        if dimensions is not None and not dimensions_valid:
            raise PaperworkError(f"invalid OCR page dimensions: {key}", INTEGRITY)
        route = page.get("route")
        if route == "OCR" and not dimensions_valid:
            raise PaperworkError(f"invalid OCR page dimensions: {key}", INTEGRITY)
        if not isinstance(route, str) or route not in {
            "NATIVE",
            "OCR_REQUIRED",
            "OCR",
            "VISUAL_REVIEW",
            "VISUAL",
        }:
            raise PaperworkError(f"invalid page route: {key}", INTEGRITY)
        if page.get("provenance") is not None:
            _verify_provenance(page["provenance"], key)

    for claim in claims:
        anchors = claim.get("anchors")
        if not isinstance(anchors, list):
            raise PaperworkError(f"invalid claim anchors: {claim.get('id')}", INTEGRITY)
        for anchor in anchors:
            if not isinstance(anchor, dict):
                raise PaperworkError(f"invalid claim anchor: {claim.get('id')}", INTEGRITY)
            page_number = anchor.get("page")
            if not isinstance(page_number, int) or isinstance(page_number, bool) or page_number < 1:
                raise PaperworkError(f"invalid claim anchor page: {claim.get('id')}", INTEGRITY)
            key = (str(anchor.get("document")), page_number)
            matching = next((item for item in pages if (item["document"], item["page"]) == key), None)
            if matching is None or anchor.get("artifact_sha256") != matching.get("artifact_sha256"):
                raise PaperworkError(f"claim anchor reference failure: {claim.get('id')}", INTEGRITY)

    approval_fields = {
        "schema",
        "id",
        "human",
        "approved_by",
        "scope_type",
        "scope_id",
        "scope_digest",
        "decision",
        "note",
    }
    for approval in approvals:
        if set(approval) != approval_fields or re.fullmatch(r"[0-9a-f]{64}", str(approval.get("scope_digest", ""))) is None:
            raise PaperworkError(f"invalid approval scope binding: {approval.get('id')}", INTEGRITY)

    audit = verify_audit(root, case)

    if check_unexpected:
        for path in sorted(root.rglob("*")):
            if path == paths["lock"]:
                continue
            if path.is_symlink():
                raise PaperworkError(f"symbolic link in case: {path}", INTEGRITY)
            if path.is_file():
                if path.stat().st_nlink != 1:
                    raise PaperworkError(f"hard-linked file in case: {path}", INTEGRITY)
                if not expected_case_file(path, root):
                    raise PaperworkError(f"unexpected file in case: {path}", INTEGRITY)
                relative = path.relative_to(root).as_posix()
                if relative.startswith(("originals/", "work/")) and relative not in referenced_artifacts:
                    raise PaperworkError(f"unreferenced artifact in case: {path}", INTEGRITY)
            elif not path.is_dir():
                raise PaperworkError(f"unexpected special file in case: {path}", INTEGRITY)

    state_entries = compute_state_entries(root)
    state_digest = canonical_digest({"schema": "godmode.paperwork.state/v1", "files": state_entries})
    if paths["validation"].exists():
        validation = _read_json_for_integrity(paths["validation"])
        validation_fields = {
            "schema",
            "case_id",
            "assurance",
            "status",
            "issues",
            "review_items",
            "validated_at",
            "validator_version",
            "state_digest",
            "audit_head_sha256",
            "audit_count",
            "digest",
        }
        if not isinstance(validation, dict) or set(validation) != validation_fields or validation.get("schema") != VALIDATION_SCHEMA:
            raise PaperworkError("invalid latest validation schema", INTEGRITY)
        digest = validation.get("digest")
        payload = dict(validation)
        payload.pop("digest", None)
        if digest != canonical_digest(payload):
            raise PaperworkError("latest validation digest mismatch", INTEGRITY)
        if verify_validation and (
            validation.get("state_digest") != state_digest
            or validation.get("audit_head_sha256") != audit["head"]
            or validation.get("audit_count") != audit["count"]
        ):
            raise PaperworkError("latest validation is stale for the current case state", INTEGRITY)
        if verify_validation:
            last_event = audit["last"]
            details = last_event.get("details", {})
            result_digest = canonical_digest(
                {
                    "status": validation.get("status"),
                    "issues": validation.get("issues"),
                    "review_items": validation.get("review_items"),
                }
            )
            if (
                last_event.get("action") != "VALIDATE"
                or last_event.get("event_sha256") != validation.get("audit_head_sha256")
                or last_event.get("sequence") != validation.get("audit_count")
                or last_event.get("timestamp") != validation.get("validated_at")
                or details.get("status") != validation.get("status")
                or details.get("case_id") != validation.get("case_id")
                or details.get("assurance") != validation.get("assurance")
                or details.get("validator_version") != validation.get("validator_version")
                or details.get("result_digest") != result_digest
                or validation.get("case_id") != case.get("case_id")
                or validation.get("assurance") != case.get("assurance")
                or validation.get("validator_version") != VERSION
            ):
                raise PaperworkError("latest validation does not match its VALIDATE audit event", INTEGRITY)

    return {
        "case": case,
        "documents": documents,
        "pages": pages,
        "claims": claims,
        "approvals": approvals,
        "reviews": reviews,
        "requirements": requirements,
        "audit": audit,
        "state_digest": state_digest,
        "state_entries": state_entries,
    }


def safe_relative(root: Path, path: Path) -> str:
    resolved = path.resolve()
    if not is_relative_to(resolved, root.resolve()):
        raise PaperworkError(f"path escapes case root: {path}", INTEGRITY)
    return resolved.relative_to(root.resolve()).as_posix()


def copy_original_transactional(source: Path, destination: Path, expected_hash: str) -> None:
    ensure_dir(destination.parent)
    descriptor, temp_name = tempfile.mkstemp(prefix=f".{destination.name}.tmp-", dir=destination.parent)
    temp = Path(temp_name)
    try:
        try:
            os.fchmod(descriptor, 0o600)
        except OSError:
            pass
        digest = hashlib.sha256()
        source_flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
        try:
            source_descriptor = os.open(source, source_flags)
        except OSError as exc:
            os.close(descriptor)
            raise PaperworkError(f"source cannot be opened safely: {source.name}", POLICY_DENIAL) from exc
        source_stat = os.fstat(source_descriptor)
        if not stat.S_ISREG(source_stat.st_mode) or source_stat.st_nlink != 1:
            os.close(source_descriptor)
            os.close(descriptor)
            raise PaperworkError(f"source is linked or not a regular file: {source.name}", POLICY_DENIAL)
        with os.fdopen(source_descriptor, "rb") as input_handle, os.fdopen(descriptor, "wb") as output_handle:
            for block in iter(lambda: input_handle.read(1024 * 1024), b""):
                digest.update(block)
                output_handle.write(block)
            output_handle.flush()
            os.fsync(output_handle.fileno())
        if digest.hexdigest() != expected_hash:
            raise PaperworkError(f"source changed during intake: {source.name}", INTEGRITY)
        if destination.exists():
            if sha256_file(destination) != expected_hash:
                raise PaperworkError(f"content-addressed original collision: {expected_hash}", INTEGRITY)
            temp.unlink()
        else:
            os.replace(temp, destination)
            try:
                destination.chmod(0o400)
            except OSError:
                pass
    finally:
        if temp.exists():
            temp.unlink()


def parse_languages(value: str) -> list[str]:
    languages = sorted(set(part.strip() for part in value.split(",") if part.strip()))
    if not languages or any(not re.fullmatch(r"[A-Za-z0-9_-]+", item) for item in languages):
        raise PaperworkError("invalid language list", INVALID)
    return languages


def parse_document_selector(value: str | None) -> str | None:
    if value is None:
        return None
    match = re.fullmatch(r"sha256:([0-9a-f]{64})", value)
    if not match:
        raise PaperworkError("document selector must be sha256:<64 lowercase hex characters>", INVALID)
    return match.group(1)
