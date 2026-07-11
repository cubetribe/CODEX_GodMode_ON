# GodMode Paperwork: local-first research and architecture decision

Date: 2026-07-11

Status: implemented for 2.10.0

## Decision

Ship GodMode Paperwork in this repository as an optional Codex plugin. Keep the
14-agent and 10-skill core runtime unchanged. Expose the plugin through the
repo-scoped marketplace as `AVAILABLE`, require a separate install, and disable
implicit skill invocation.

This is the best balance between integration and isolation:

- one repository, governance model, version, CI system, and release
- no automatic expansion of every global GodMode installation
- a dedicated safety and evidence contract for sensitive documents
- a clean future extraction path if Paperwork becomes an independent product

## Question being answered

The requested mode should organize sensitive paperwork such as tax records or
complex legal case material, prefer economical local OCR, escalate uncertainty
in a controlled way, and produce evidence that can be validated rather than a
free-form model summary.

The central design question is not whether OCR can be made infallible. It cannot.
The question is which parts can be deterministic and which parts must remain
explicitly probabilistic or human-controlled.

## Options considered

| Option | Advantages | Problems | Decision |
| --- | --- | --- | --- |
| Add a core global skill | simplest invocation and installation | silently expands every install; core installer copies every packaged skill; weaker separation for sensitive data | rejected |
| Add an optional plugin in this repository | integrated governance and release; explicit install; dedicated metadata, scripts, schemas, tests, and docs | adds a second installation path to maintain | selected |
| Create a separate repository now | strongest product boundary and independent lifecycle | duplicates governance and release work before the interface is proven | deferred |

OpenAI's plugin guidance describes plugins as the distribution surface for a
stable package that can bundle reusable skills, while its skill guidance
recommends plugins for reusable distribution rather than local experimentation.
It also defines the repository marketplace path, required plugin manifest, and
bundled skill layout. Those documented boundaries support the selected option:
[Build plugins](https://learn.chatgpt.com/docs/build-plugins) and
[Build skills](https://learn.chatgpt.com/docs/build-skills).

## What “deterministic” means here

Deterministic in 2.10 means:

- explicit inputs and a caller-selected case root
- byte-preserved originals addressed by SHA-256
- canonical JSON and JSONL records
- stable page routes and bounded thresholds
- fixed validation rule types with decimal strings instead of floating point
- exact evidence quotes and artifact hashes
- OCR boxes derived from a unique TSV word sequence
- state-bound validation and a hash-chained internal audit
- normalized tar metadata, stable member ordering, exact manifests, and sidecars
- stable exit codes for automation

It does **not** mean:

- perfect OCR
- complete document supply
- true model interpretation
- document authenticity
- legal or tax correctness
- cryptographic identity of a named human
- tamper resistance against an attacker who can coherently rewrite the complete
  case and every internal hash

The model is therefore used as an orchestrator and assistant, not as the root of
trust. Codex can help select the assurance level, explain review items, and draft
schema-conforming records. The bundled Python CLI owns mechanical intake,
routing, validation, and packaging. This separation gets more value from a
capable current parent model without turning model confidence into evidence.

## OCR architecture

### Selected ladder

1. `doctor` inspects capabilities and never installs anything.
2. PDF pages use Poppler native text extraction first.
3. Only unresolved pages are rendered at 300 DPI.
4. Local Tesseract runs only on those pages and preserves TXT, TSV, and hOCR.
5. Deterministic quality thresholds accept or reject the OCR page.
6. Remaining pages enter `VISUAL_REVIEW`.
7. A declared human supplies the final visual resolution through a checked
   command; critical claims require a separate scoped confirmation.

Tesseract's official command-line documentation exposes TSV word text,
coordinates, and confidence. That makes it suitable for deriving reproducible
page anchors rather than accepting an invented model rectangle:
[Tesseract command-line usage](https://tesseract-ocr.github.io/tessdoc/Command-Line-Usage.html).
Poppler provides the local PDF utilities used for page count, native extraction,
and rendering: [Poppler](https://poppler.freedesktop.org/).

### Why no silent local installation

Automatic package installation would cross a material authority and supply-chain
boundary. Package manager choice, administrator privileges, binary provenance,
language data, update policy, and system compatibility belong to the operator.
The “economical local OCR first” goal is preserved by capability detection and
page-scoped execution, not by changing the machine without approval.

The plugin records resolved executable paths, versions, hashes, argument
contracts, and Tesseract language-data hashes. This improves reproducibility but
does not prove that an installed binary is safe.

### Why no automatic model-window escalation

Sending a sensitive page to a model may cross a privacy boundary and makes the
result non-deterministic. The CLI therefore stops at `VISUAL_REVIEW` and never
opens a network, uploads a page, or calls a model. In an active Codex task, the
user may deliberately authorize visual assistance for selected pages, but the
result still requires a named human declaration before it becomes final case
evidence. Automatic vision escalation remains outside 2.10.

## Evidence and approval design

A claim is useful only when another reviewer can reproduce where it came from.
Each claim therefore binds:

- original document SHA-256
- one-based page number
- exact quote in the selected final artifact
- final-artifact SHA-256
- extraction method
- normalized bounding box for OCR or visual material

Critical claims require a human approval bound to the current canonical claim
digest. Replacing a claim invalidates the old approval. A review-bearing archive
requires a separate declared-human release gate and note file, included and hashed in the pack.

These are explicit declarations, not digital signatures. A future signed-receipt
feature would require a separately managed identity and key lifecycle rather
than a stronger prompt.

## Regulatory and records-management research

The following sources inform safeguards; the plugin does not claim conformance
or certification.

### BSI TR-03138 RESISCAN

The current BSI technical guideline addresses controlled scanning processes and
the evidentiary risks involved when paper originals may later be destroyed. It
emphasizes an organized process, protection-needs analysis, quality assurance,
and traceability. Paperwork adopts process separation, quality gates, retained
artifacts, and review records, but expressly forbids original destruction and
does not call itself RESISCAN-conformant:
[BSI TR-03138 RESISCAN, version 1.5](https://www.bsi.bund.de/SharedDocs/Downloads/DE/BSI/Publikationen/TechnischeRichtlinien/TR03138/TR-03138_V1_5.pdf?__blob=publicationFile&v=15).

### German GoBD

The German tax-record guidance addresses traceability, completeness,
availability, procedural documentation, and machine-readable access. The 2025
amendment also reflects the mandatory domestic B2B e-invoice transition. A local
evidence pack can support review and documentation, but software alone cannot
establish that a taxpayer's complete organizational process satisfies GoBD:
[BMF GoBD second amendment, 14 July 2025](https://www.bundesfinanzministerium.de/Content/DE/Downloads/BMF_Schreiben/Weitere_Steuerthemen/Abgabenordnung/2025-07-14-GoBD-2-aenderung.pdf?__blob=publicationFile&v=4)
and the [official 2025 consolidated guidance](https://amtliche-handbuecher.bundesfinanzministerium.de/ao/2025/Anhaenge/BMF-Schreiben-und-gleichlautende-Laendererlasse/Anhang-33/anhang-33.html).

### GDPR principles

Article 5 of the GDPR includes purpose limitation, data minimization, accuracy,
storage limitation, and integrity/confidentiality principles. Local processing,
explicit inputs, path redaction, no upload, and refusal to scan an entire home
directory reduce exposure. They do not supply a legal basis, retention policy,
access-control program, or controller obligations for the operator:
[Regulation (EU) 2016/679, Article 5](https://eur-lex.europa.eu/eli/reg/2016/679/oj).

## Threat model

### Protected against

- accidental input modification after intake
- duplicate originals under different names
- path disclosure through stored source paths
- symbolic links, hard links, traversal, and unsafe tar members
- partial or stale record edits
- validation reused after a governed mutation
- critical approval replay after claim replacement
- a forged receipt that differs from the archive manifest
- a manifest-consistent archive that omits state-bound originals or audit events
- payload bytes appended after the canonical USTAR end marker
- visual resolution used to bypass the OCR stage
- dynamic validation expressions, rounded decimal sums, or non-finite numeric tricks
- silent overwrite and partial archive publication

### Not protected against

- compromise of the host or external OCR binaries
- a coherent rewrite of the complete case and all internal hashes
- malicious or mistaken human declarations
- documents omitted before intake
- semantic fraud in an authentic-looking source
- disclosure after an unencrypted archive leaves the protected location

## Privacy and storage outcome

- no network imports or shell-string execution in the bundled CLI
- no implicit recursive discovery; explicit recursion is refused for a directory
  that contains the home directory or filesystem root
- no real documents in repository fixtures
- no cases or exports inside Git or plugin caches
- uncompressed archives are explicitly acknowledged and never described as
  encrypted
- final transfer, retention, deletion, and filing remain operator decisions

## Verification performed for 2.10

The release gate includes focused tests for native-first extraction, page-scoped
OCR, low-confidence and timeout review routing, immutable-original integrity,
audit truncation, stale validation, approval scope replay, exact OCR boxes,
non-finite inputs, exact large fixed-point sums, Unicode normalization and
surrogate rejection, path escape, linked files, private OCR modes, archive
traversal, trailing bytes, complete packed-case binding, receipt/manifest
binding, deterministic packaging, publication cleanup, and validation-readiness
reporting.

It also includes repository marketplace validation, Python compilation, the
full GodMode package check, an isolated Codex marketplace installation, and a
real local Poppler/Tesseract outcome using synthetic content.

## Future decision triggers

Reconsider a separate repository only when at least one becomes true:

- Paperwork needs independent release cadence or maintainers
- plugin distribution grows beyond this marketplace
- a signed identity service, UI, or separate executable becomes a product
- support obligations materially exceed the core GodMode governance model

Until then, the optional in-repository plugin keeps the contract discoverable,
auditable, and easy to remove without coupling it to every GodMode install.
