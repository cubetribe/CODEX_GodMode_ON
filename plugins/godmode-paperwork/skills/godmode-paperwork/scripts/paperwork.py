#!/usr/bin/env python3
"""GodMode Paperwork 2.10.0 offline command-line interface."""

from __future__ import annotations

import argparse
import sys
from typing import Any, Sequence

from paperwork_core import INTEGRITY, INTERNAL, PROCESSING, USAGE, PaperworkError, VERSION, canonical_bytes
from paperwork_casework import add_approval, add_claim, resolve_page, set_requirements
from paperwork_pipeline import doctor, extract, intake, route
from paperwork_validation import pack, validate, verify_case, verify_pack


class UsageParseError(Exception):
    pass


class PaperworkArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise UsageParseError(message)


def build_parser() -> argparse.ArgumentParser:
    parser = PaperworkArgumentParser(
        prog="paperwork",
        description="Deterministic local-first document evidence pipeline.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    parser.add_argument("--json", action="store_true", help="Emit canonical machine-readable JSON.")
    parser.add_argument("--quiet", action="store_true", help="Suppress normal command output.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    doctor_parser = subparsers.add_parser("doctor", help="Inspect local capabilities without installing tools.")
    doctor_parser.add_argument("--languages", default="deu,eng")
    doctor_parser.add_argument("--require", default="pdf-native,pdf-render,ocr")

    intake_parser = subparsers.add_parser("intake", help="Create or extend an immutable document inventory.")
    intake_parser.add_argument("--case", required=True)
    intake_parser.add_argument("--case-id", required=True)
    intake_parser.add_argument("--input", action="append", required=True)
    intake_parser.add_argument("--recursive", action="store_true")
    intake_parser.add_argument("--assurance", choices=("INVENTORY", "EXTRACTION", "CASEWORK"), default="EXTRACTION")
    intake_parser.add_argument("--languages", default="deu,eng")
    intake_parser.add_argument("--actor", default="codex")

    extract_parser = subparsers.add_parser("extract", help="Extract native PDF text before OCR.")
    extract_parser.add_argument("--case", required=True)
    extract_parser.add_argument("--document")
    extract_parser.add_argument("--actor", default="codex")

    route_parser = subparsers.add_parser("route", help="Route unresolved pages through local OCR.")
    route_parser.add_argument("--case", required=True)
    route_parser.add_argument("--document")
    route_parser.add_argument("--actor", default="codex")

    validate_parser = subparsers.add_parser("validate", help="Evaluate the configured assurance gate.")
    validate_parser.add_argument("--case", required=True)
    validate_parser.add_argument("--actor", default="codex")

    for command, help_text in (
        ("requirements", "Set the bounded CASEWORK requirements contract."),
        ("claim", "Add or replace one source-anchored CASEWORK claim."),
        ("approve", "Add or replace one declared-human approval."),
        ("resolve-page", "Resolve one queued page from declared-human visual text."),
    ):
        mutation_parser = subparsers.add_parser(command, help=help_text)
        mutation_parser.add_argument("--case", required=True)
        mutation_parser.add_argument("--input", required=True)
        mutation_parser.add_argument("--actor", default="codex")

    verify_parser = subparsers.add_parser("verify", help="Read-only integrity verification.")
    verify_target = verify_parser.add_mutually_exclusive_group(required=True)
    verify_target.add_argument("--case")
    verify_target.add_argument("--pack")

    pack_parser = subparsers.add_parser("pack", help="Create a reproducible uncompressed evidence archive.")
    pack_parser.add_argument("--case", required=True)
    pack_parser.add_argument("--output", required=True)
    pack_parser.add_argument("--contents", choices=("evidence", "full"), default="evidence")
    pack_parser.add_argument("--actor", required=True)
    pack_parser.add_argument("--acknowledge-plain-archive", action="store_true")
    pack_parser.add_argument("--allow-review", action="store_true")
    pack_parser.add_argument("--approved-by")
    pack_parser.add_argument("--approval-note-file")
    return parser


def _dispatch(arguments: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    if arguments.command == "doctor":
        return doctor(arguments.languages, arguments.require)
    if arguments.command == "intake":
        return intake(
            arguments.case,
            arguments.case_id,
            arguments.input,
            arguments.recursive,
            arguments.assurance,
            arguments.languages,
            arguments.actor,
        )
    if arguments.command == "extract":
        return extract(arguments.case, arguments.document, arguments.actor)
    if arguments.command == "route":
        return route(arguments.case, arguments.document, arguments.actor)
    if arguments.command == "validate":
        return validate(arguments.case, arguments.actor)
    if arguments.command == "requirements":
        return set_requirements(arguments.case, arguments.input, arguments.actor)
    if arguments.command == "claim":
        return add_claim(arguments.case, arguments.input, arguments.actor)
    if arguments.command == "approve":
        return add_approval(arguments.case, arguments.input, arguments.actor)
    if arguments.command == "resolve-page":
        return resolve_page(arguments.case, arguments.input, arguments.actor)
    if arguments.command == "verify":
        return verify_case(arguments.case) if arguments.case else verify_pack(arguments.pack)
    if arguments.command == "pack":
        return pack(
            arguments.case,
            arguments.output,
            arguments.contents,
            arguments.actor,
            arguments.acknowledge_plain_archive,
            arguments.allow_review,
            arguments.approved_by,
            arguments.approval_note_file,
        )
    raise PaperworkError(f"unsupported command: {arguments.command}", INTERNAL)


def _print(payload: dict[str, Any], *, json_mode: bool, quiet: bool, error: bool = False) -> None:
    if quiet:
        return
    stream = sys.stderr if error and not json_mode else sys.stdout
    if json_mode:
        stream.write(canonical_bytes(payload).decode("utf-8"))
        return
    status = payload.get("status", "FAIL" if error else "PASS")
    command = payload.get("command", "paperwork")
    message = payload.get("message")
    print(f"[{status}] {command}{': ' + str(message) if message else ''}", file=stream)
    if command == "doctor" and isinstance(payload.get("capabilities"), dict):
        for name, capability in sorted(payload["capabilities"].items()):
            if capability.get("status") == "DEFERRED":
                capability_status = "DEFERRED"
            else:
                capability_status = "PRESENT" if capability.get("present") else "MISSING"
            print(f"capability {name}: {capability_status}", file=stream)
            if capability.get("missing_languages"):
                print(f"  missing languages: {','.join(capability['missing_languages'])}", file=stream)
    for key in ("case", "output", "pack", "archive_sha256", "validation_digest"):
        if payload.get(key) is not None:
            print(f"{key}: {payload[key]}", file=stream)


def main(argv: Sequence[str] | None = None) -> int:
    raw = list(sys.argv[1:] if argv is None else argv)
    json_mode = "--json" in raw
    quiet = "--quiet" in raw
    raw = [item for item in raw if item not in {"--json", "--quiet"}]
    if "--version" in raw and len(raw) > 1:
        raw = ["--version"]
    try:
        arguments = build_parser().parse_args(raw)
        code, payload = _dispatch(arguments)
        _print(payload, json_mode=json_mode, quiet=quiet)
        return code
    except UsageParseError as exc:
        payload = {
            "command": raw[0] if raw else "paperwork",
            "status": "FAIL",
            "message": str(exc),
            "exit_code": USAGE,
        }
        if not json_mode and not quiet:
            build_parser().print_usage(sys.stderr)
        _print(payload, json_mode=json_mode, quiet=quiet, error=True)
        return USAGE
    except PaperworkError as exc:
        payload = {
            "command": raw[0] if raw else "paperwork",
            "status": "FAIL",
            "message": exc.message,
            "exit_code": exc.code,
            "details": exc.details,
        }
        _print(payload, json_mode=json_mode, quiet=quiet, error=True)
        return exc.code
    except OSError:
        command = raw[0] if raw else "paperwork"
        code = INTEGRITY if command == "verify" else PROCESSING
        payload = {
            "command": command,
            "status": "FAIL",
            "message": "filesystem operation failed",
            "exit_code": code,
        }
        _print(payload, json_mode=json_mode, quiet=quiet, error=True)
        return code
    except KeyboardInterrupt:
        payload = {"command": raw[0] if raw else "paperwork", "status": "FAIL", "message": "interrupted", "exit_code": INTERNAL}
        _print(payload, json_mode=json_mode, quiet=quiet, error=True)
        return INTERNAL
    except Exception as exc:  # Fail closed without exposing case data or a traceback.
        payload = {
            "command": raw[0] if raw else "paperwork",
            "status": "FAIL",
            "message": f"internal error: {type(exc).__name__}",
            "exit_code": INTERNAL,
        }
        _print(payload, json_mode=json_mode, quiet=quiet, error=True)
        return INTERNAL


if __name__ == "__main__":
    raise SystemExit(main())
