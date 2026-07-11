---
name: godmode-paperwork
description: Create controlled, local-first document case files with immutable intake, native PDF extraction, page-scoped OCR escalation, evidence anchors, validation gates, and reproducible archives. Use when Codex must organize or verify sensitive tax, legal, compliance, audit, or administrative paperwork without silently installing tools, uploading documents, submitting forms, deleting originals, or treating model output as verified evidence.
---

# GodMode Paperwork

Operate an evidence-first document pipeline. Treat OCR and model interpretation as probabilistic inputs; make hashes, source anchors, validation rules, review decisions, and archive construction reproducible and auditable.

## Non-negotiable boundaries

- Keep every case root outside Git worktrees and plugin caches.
- Preserve originals byte-for-byte. Never move, overwrite, rename in place, delete, or submit them.
- Run the bundled CLI offline. Never add network, cloud, installer, or autonomous filing behavior.
- Stop on integrity failures. Return `REVIEW` when evidence is incomplete or uncertain.
- Require explicit human approval for critical claims and release of a review-bearing archive.
- Describe results as prepared or validated evidence, not legal advice, tax advice, compliance certification, or guaranteed truth.
- Treat the named local binaries and trained language files as an external trust boundary. The CLI records their resolved paths, versions, hashes, and argument contracts but cannot prove that a binary is benign.
- Treat audit hashes and declared-human approvals as internal consistency evidence, not signatures or protection against an attacker who can rewrite the whole case.
- Require Python 3.11 or newer. Native Windows behavior remains deferred; use a validated Unix-like environment for this release.

## Run the workflow

Set the CLI path once:

```bash
PAPERWORK="<skill-directory>/scripts/paperwork.py"
```

1. Inspect local capabilities without installing anything:

   ```bash
   python3 "$PAPERWORK" --json doctor --languages deu,eng --require pdf-native,pdf-render,ocr
   ```

2. Create a case in a deliberately chosen non-Git directory:

   On macOS, do not use `/tmp`: it resolves through a symlink and the strict
   case-path policy rejects it. Use `/private/tmp` only for disposable tests.

   ```bash
   python3 "$PAPERWORK" intake \
     --case /secure/cases/example \
     --case-id example-2026 \
     --input /path/to/document.pdf \
     --assurance EXTRACTION \
     --languages deu,eng
   ```

3. Extract existing PDF text before OCR:

   ```bash
   python3 "$PAPERWORK" extract --case /secure/cases/example
   ```

4. Route only unresolved pages to local OCR:

   ```bash
   python3 "$PAPERWORK" route --case /secure/cases/example
   ```

5. Resolve a page only after `route` places it in `VISUAL_REVIEW`. This applies to both `EXTRACTION` and `CASEWORK`:

   ```bash
   python3 "$PAPERWORK" resolve-page --case /secure/cases/example --input /secure/input/page-resolution.json
   ```

6. For `CASEWORK`, write requirements, claims, and approvals only through the schema-checked commands. Keep each input JSON outside the case root:

   ```bash
   python3 "$PAPERWORK" requirements --case /secure/cases/example --input /secure/input/requirements.json
   python3 "$PAPERWORK" claim --case /secure/cases/example --input /secure/input/claim.json
   python3 "$PAPERWORK" approve --case /secure/cases/example --input /secure/input/approval.json
   ```

   Never edit `records/*.jsonl`, `requirements.json`, page routes, or validation state manually.

7. Validate the selected assurance level, then verify integrity:

   ```bash
   python3 "$PAPERWORK" validate --case /secure/cases/example
   python3 "$PAPERWORK" verify --case /secure/cases/example
   ```

8. Pack only after validation. A plain tar archive requires an explicit acknowledgement:

   ```bash
   python3 "$PAPERWORK" pack \
     --case /secure/cases/example \
     --output /secure/exports/example.paperwork.tar \
     --contents evidence \
     --actor operator \
     --acknowledge-plain-archive
   python3 "$PAPERWORK" verify --pack /secure/exports/example.paperwork.tar
   ```

Any successful mutation invalidates the prior validation. Validate again immediately before packing. Pack refuses a state, audit head, or audit count that differs from the latest validation.

In 2.10, both `evidence` and `full` packs retain every state-bound case artifact so an extracted case remains independently verifiable. The labels are reserved for a future versioned subset contract.

Use `--json` for machine-readable results and inspect exit codes before continuing: `0` is `PASS`, `10` is `REVIEW`, `2` is CLI usage error, `20`-`26` are controlled failures, and `70` is an internal error.

## Read references progressively

- Read [evidence-contract.md](references/evidence-contract.md) before adding claims, requirements, approvals, or downstream automation.
- Read [ocr-escalation.md](references/ocr-escalation.md) when native extraction is incomplete or OCR tools are missing.
- Read [safety-and-review.md](references/safety-and-review.md) before handling sensitive material, closing review findings, or packing a case.

The eight JSON Schemas under `assets/schemas/` distinguish persisted records from mutation inputs: approval input and stored approval are separate, visual page resolution has its own input schema, and claim anchors encode method-specific bounding-box rules. For OCR anchors the CLI derives the normalized box from the unique contiguous TSV word sequence; a supplied box must match exactly. The CLI remains the enforcement authority and uses only Python's standard library.
