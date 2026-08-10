# GodMode Paperwork

Updated: 2026-07-11

GodMode Paperwork is the optional 2.10 plugin for controlled, local-first work
with tax, legal, compliance, audit, and administrative documents. It builds a
traceable evidence case; it does not make a professional decision, certify legal
compliance, file a form, destroy an original, or promise error-free OCR.

## Why it is optional

The core GodMode runtime is a general engineering orchestrator. Paperwork needs
stricter storage, privacy, review, and integrity rules. It therefore ships in the
same governed repository, but through an independently versioned Codex
marketplace entry with explicit installation and invocation.

GodMode 3 installs seven core agents and nine core skills. Neither the 2.10 nor
3.0 core installer copies or activates Paperwork. Root core releases do not
change the Paperwork evidence contract; the plugin remains `2.10.0` until a
separate backward-compatible Paperwork release is designed and tested.

## Install

Add the released marketplace and install the plugin:

```bash
codex plugin marketplace add cubetribe/CODEX_GodMode_ON --ref v2.10.0
codex plugin list --marketplace codex-godmode-on --available --json
codex plugin add godmode-paperwork@codex-godmode-on
codex plugin list --json
```

Start a fresh Codex task, then invoke the skill explicitly:

```text
$godmode-paperwork

Create an EXTRACTION case for these explicitly named documents. Keep all data
local, run doctor first, and stop for review rather than guessing.
```

Implicit invocation is disabled. This reduces the chance that a general request
accidentally enters a sensitive-document workflow.

## Runtime requirements

- Python 3.11 or newer
- a validated Unix-like environment for the 2.10 release
- Poppler tools for PDFs: `pdfinfo`, `pdftotext`, and `pdftoppm`
- Tesseract and the requested `.traineddata` languages for local OCR

The CLI reports missing capabilities and exits. It never installs, downloads,
updates, or uploads a tool or language file. OCRmyPDF may be detected as an
optional derivative capability but is not required by the workflow.

From a repository checkout, set the CLI path for direct verification:

```bash
PAPERWORK="$PWD/plugins/godmode-paperwork/skills/godmode-paperwork/scripts/paperwork.py"
python3 "$PAPERWORK" --json doctor \
  --languages deu,eng \
  --require pdf-native,pdf-render,ocr
```

`doctor` records capability facts only. A missing tool is an explicit setup
decision for the operator, not permission for Codex to change the machine.

## Choose a case location

Every case must be in an explicitly selected directory outside:

- Git worktrees
- the GodMode repository
- Codex plugin and skill caches
- symbolic-link paths

Use protected local or encrypted storage appropriate for the document
sensitivity. On macOS, `/tmp` resolves through a symlink and is rejected by the
strict path policy. `/private/tmp` is acceptable only for disposable synthetic
tests, not long-lived personal records.

The workflow refuses symbolic links, hard links, traversal paths, unexpected
files, and linked archive outputs. It attempts directory mode `0700`, working
file mode `0600`, and immutable-original mode `0400` where supported.

## Assurance levels

| Level | Mechanical contract |
| --- | --- |
| `INVENTORY` | immutable intake, deduplication, hashes, schemas, and audit integrity |
| `EXTRACTION` | inventory plus complete page coverage, deterministic routing, artifacts, and review handling |
| `CASEWORK` | extraction plus claims, evidence anchors, bounded requirements, and critical-claim approvals |

Choose the lowest level that proves the intended result. A larger assurance
level creates more work and more review obligations; it does not create legal
certainty.

## Controlled workflow

### 1. Intake only named inputs

```bash
python3 "$PAPERWORK" --json intake \
  --case /protected/cases/tax-2025 \
  --case-id tax-2025 \
  --input /protected/inbox/invoice-001.pdf \
  --input /protected/inbox/invoice-002.pdf \
  --assurance EXTRACTION \
  --languages deu,eng \
  --actor operator
```

Intake copies each original byte-for-byte into a content-addressed location,
records its SHA-256, deduplicates equal content, and stores only source base
names. It never moves, renames in place, overwrites, or deletes an input.

### 2. Extract native PDF text first

```bash
python3 "$PAPERWORK" --json extract \
  --case /protected/cases/tax-2025 \
  --actor operator
```

Native text is accepted page by page only when the deterministic quality gate
passes. Unresolved pages enter `OCR_REQUIRED`; the command does not run OCR
implicitly.

### 3. Route unresolved pages to local OCR

```bash
python3 "$PAPERWORK" --json route \
  --case /protected/cases/tax-2025 \
  --actor operator
```

Only unresolved pages are rendered at 300 DPI and passed to local Tesseract.
TXT, TSV, and hOCR outputs are retained. The page record binds the resolved
executable path, version, SHA-256, argument contract, requested languages, and
language-data hashes.

Low confidence, malformed output, a timeout, missing language data, or another
unresolved condition enters `VISUAL_REVIEW`. A page can be resolved visually
only after it reaches that route; direct bypass from `OCR_REQUIRED` is refused.

### 4. Resolve queued visual pages

At either `EXTRACTION` or `CASEWORK`, resolve a page only after `route` places it
in `VISUAL_REVIEW`:

```bash
python3 "$PAPERWORK" --json resolve-page \
  --case /protected/cases/tax-2025 \
  --input /protected/case-input/page-resolution.json \
  --actor operator
```

The input follows `page-resolution.schema.json` and records declared-human text,
a normalized box, reviewer name, and note. It cannot bypass local OCR routing.

### 5. Add bounded CASEWORK records

For `CASEWORK`, prepare schema-conforming requirements, claims, and approval
inputs outside the case and publish them only through these commands:

```bash
python3 "$PAPERWORK" --json requirements \
  --case /protected/cases/tax-2025 \
  --input /protected/case-input/requirements.json \
  --actor operator

python3 "$PAPERWORK" --json claim \
  --case /protected/cases/tax-2025 \
  --input /protected/case-input/claim.json \
  --actor operator

python3 "$PAPERWORK" --json approve \
  --case /protected/cases/tax-2025 \
  --input /protected/case-input/approval.json \
  --actor operator
```

The schema directory distinguishes mutation inputs from persisted records.
`approval-input.schema.json` deliberately omits `scope_digest`; the CLI derives
that digest and the stored record follows `approval.schema.json`. Claim anchors
encode method-specific box rules: NATIVE forbids a box, OCR may omit it for
deterministic derivation, and VISUAL requires it.

Allowed rules are `required_claim`, `required_document`, `equals`,
`decimal_sum`, `date_order`, `format`, and `unique`. There is no expression
evaluator, executable rule language, or caller-supplied regular expression.
Decimal sums use exact fixed-point integer arithmetic rather than a rounded
floating or default-precision decimal context. Numeric decimal strings are
limited to 256 characters, and one sum accepts at most 1000 terms.

Every claim needs an exact quote, document hash, page number, final-artifact
hash, and route. OCR quotes must resolve to one unique contiguous TSV word
sequence; the CLI derives the normalized bounding box. Replacing a claim changes
its scope digest and makes any earlier approval ineligible.

### 6. Validate and verify

```bash
python3 "$PAPERWORK" --json validate \
  --case /protected/cases/tax-2025 \
  --actor operator

python3 "$PAPERWORK" --json verify \
  --case /protected/cases/tax-2025
```

Validation is bound to the current complete state digest, audit head, audit
count, result, assurance level, and validator version. Every successful later
mutation removes the previous validation. Manual state changes make it stale or
fail integrity verification.

`verify --case` reports both integrity and validation readiness. Only a current
`PASS` result is ready for normal packaging.

### 7. Package outside the case and Git

```bash
python3 "$PAPERWORK" --json pack \
  --case /protected/cases/tax-2025 \
  --output /protected/exports/tax-2025.paperwork.tar \
  --contents evidence \
  --actor operator \
  --acknowledge-plain-archive

python3 "$PAPERWORK" --json verify \
  --pack /protected/exports/tax-2025.paperwork.tar
```

The archive is deterministic, uncompressed, and unencrypted. It includes an
exact manifest and is accompanied by a SHA-256 sidecar and canonical receipt.
Verification reconstructs the canonical USTAR bytes, rejects appended payloads,
materializes the complete packed case in isolated temporary storage, runs the
normal case-integrity verifier, and binds its state, audit, and validation back
to the manifest and receipt. The command refuses overwrite, failed validation,
stale state, unsafe paths, or missing acknowledgement of the plain archive.

In 2.10, both `evidence` and `full` include every state-bound case artifact. This
keeps an extracted case independently verifiable, including native and OCR
provenance. The labels are reserved for a future separately versioned subset
contract.

A `REVIEW` archive additionally requires all of:

```text
--allow-review
--approved-by "Named Human"
--approval-note-file /protected/review/release-note.txt
```

The UTF-8 note is included in and hashed by the archive. The name is a declared
human identity, not cryptographic authentication.

`verify --pack` separates archive integrity from case readiness. A review-bearing
archive returns exit `10`, `integrity_status: PASS`,
`validation_status: REVIEW`, and `ready_for_release: false`.

## Exit contract

| Code | Meaning |
| --- | --- |
| `0` | `PASS` |
| `10` | `REVIEW`; a human decision remains |
| `2` | CLI usage error |
| `20` | invalid controlled input |
| `21` | required local capability missing |
| `22` | integrity failure |
| `23` | processing failure |
| `24` | validation failed |
| `25` | policy denial |
| `26` | case locked |
| `70` | unexpected internal error |

Automation must branch on the exit code, not only on whether JSON was printed.
Canonical JSON output is available through the global `--json` flag.

## What the evidence proves

The case can demonstrate byte identity, internal record consistency, execution
provenance, exact text anchors, bounded mechanical rules, declared review
decisions, and reproducible packaging.

It cannot prove that:

- OCR text is factually correct
- a document is genuine or legally effective
- every relevant document was supplied
- a named reviewer is cryptographically authenticated
- a tax or legal conclusion is professionally correct
- the full case survived a coherent rewrite by an attacker controlling all case
  files and hashes

Keep deadlines, filing, external transfer, deletion, paper-original destruction,
and final high-stakes conclusions behind a qualified human decision.

## Design and source record

The architectural choice, threat model, regulatory research, OCR rationale, and
alternatives are documented in
[GodMode Paperwork: local-first research and architecture decision](./research/godmode-paperwork-local-first-2026-07-11.md).

Primary product references:

- [Build Codex plugins](https://learn.chatgpt.com/docs/build-plugins)
- [Build Codex skills](https://learn.chatgpt.com/docs/build-skills)
- [Tesseract command-line usage](https://tesseract-ocr.github.io/tessdoc/Command-Line-Usage.html)
- [Poppler](https://poppler.freedesktop.org/)
