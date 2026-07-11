# Evidence contract

## Record model

Store canonical UTF-8 JSON with LF line endings, NFC-normalized strings, sorted keys, compact separators, and no floating-point values. Use decimal strings when precision matters. Every record carries a `schema` identifier.

The case contains:

- `case.json` for identity, assurance, languages, and creation metadata
- immutable, content-addressed files under `originals/`
- JSONL records for documents, pages, claims, approvals, and findings
- `requirements.json` for bounded validation rules
- separate native, rendered, OCR, and final artifacts under `work/`
- a hash-chained internal `audit/` directory written only through the CLI
- the latest validation result, complete state digest, audit head, and audit count under `validation/`

`case.json` binds the genesis event and current audit head/count. Validation runs while holding the case lock, appends its validation audit event, then hashes every case file except `validation/latest.json` and the transient lock. Every later CLI mutation removes the old validation. `verify` and `pack` reject stale state.

This establishes internal consistency and detects accidental or partial changes. It is not a digital signature and cannot defeat an attacker who can coherently rewrite the complete case and all hashes.

## Evidence anchors

Anchor every claim to:

- `document`: the original SHA-256
- `page`: one-based page number
- `quote`: exact text present in that page's final artifact
- `artifact_sha256`: hash of the final artifact containing the quote
- `method`: `NATIVE`, `OCR`, or `VISUAL`
- `bbox`: four decimal strings from `0` to `1` for `OCR` and `VISUAL`

For OCR anchors, the CLI resolves the exact quote to one unique contiguous TSV
word sequence and derives the normalized box from those word coordinates. A
caller-provided OCR box is accepted only when it matches that derived value.

An anchor is invalid when its original, page, artifact, hash, quote, method, or bounding box cannot be reproduced. Hashes prove byte integrity, not truth, authorship, legal effect, or completeness.

## Assurance levels

- `INVENTORY`: verify case schemas, immutable-original hashes, deduplication, and the audit chain.
- `EXTRACTION`: additionally require page coverage, deterministic routes, artifact hashes, and explicit handling of reviews.
- `CASEWORK`: additionally require claims, requirements, anchors, bounded rules, and human approvals for critical claims.

Allowed rule types are `required_claim`, `required_document`, `equals`, `decimal_sum`, `date_order`, `format`, and `unique`. Decimal sums use exact fixed-point integer arithmetic, accept decimal strings of at most 256 characters, and allow at most 1000 terms. Never introduce dynamic evaluation, executable expressions, or arbitrary regular expressions.

Create CASEWORK requirements, claims, and approvals only with `requirements --input`, `claim --input`, and `approve --input`. Resolve a queued visual page at either `EXTRACTION` or `CASEWORK` assurance only with `resolve-page --input`. The CLI validates fields, anchors, routes, path ownership, and references before publishing canonical records and an audit event. Input files remain outside the case.

## Human approvals

Treat approval as a claim- or page-scoped record, not a blanket trust flag. A qualifying record names the human approver, sets `human` to true, identifies the scope and identifier, binds the current scope digest, and states the decision. Replacing a claim or page makes the prior approval ineligible. Archive release uses its own declared-human note gate. These are explicit declarations, not cryptographic identity verification. Model output alone never closes a critical claim or release gate.
