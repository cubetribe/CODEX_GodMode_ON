# Roadmap

Updated: 2026-07-11

Current release: 2.10.0

Version 2.10 extends the installable GPT-5.6-era local orchestration baseline
with an optional, local-first document evidence workflow.
This roadmap separates shipped behavior from future hardening so planned work is
not mistaken for a current runtime feature.

## Shipped milestones

| Milestone | Status | Outcome |
| --- | --- | --- |
| Architecture blueprint | shipped | native Codex layers, roles, gates, and authority boundaries documented |
| Global runtime package | shipped | 14 agents and 10 skills installed outside repo-local discovery paths |
| Optional department routing | shipped | lean, guided, and bounded cross-domain lanes |
| Production companion modes | shipped | workflow, debug, review, department, and local prototype procedures |
| Repository guardrails | shipped | governance, changelog law, validation law, CI/security baseline |
| Safe cross-platform install | shipped in 2.0 | byte-preserved config, managed guidance, separate profiles, exact drift checks |
| Model-inheritance contract | shipped in 2.0 | parent session chooses model and reasoning; custom agents do not pin entitlements |
| Evidence-backed completion | shipped in 2.0 | user-visible done criteria mapped to concrete outcomes, including prototypes |
| Optional Paperwork plugin | shipped in 2.10 | immutable intake, local OCR escalation, evidence anchors, validation, review gates, and reproducible archives |

## 2.10 release scope

Version 2.10 preserves the 2.0 core runtime and adds:

- a repository marketplace with `godmode-paperwork` available by explicit install
- a Python-standard-library CLI for controlled intake, extraction, routing,
  casework, validation, verification, and packaging
- native PDF extraction before page-scoped local OCR, with unresolved pages
  forced through an explicit visual-review queue
- immutable originals, canonical records, source-anchored claims, scoped human
  approvals, a hash-chained audit, and state-bound validation
- deterministic uncompressed tar archives with exact manifests, receipts, and
  SHA-256 sidecars
- adversarial regression coverage for path escape, stale validation, approval
  replay, archive forgery, OCR coordinate mismatch, and escalation bypass

## Next hardening areas

These are candidates, not promised current behavior:

### Workflow evaluation fixtures

- representative web, Apple, Flutter, debug, review, and department runs
- measurable skill-trigger and agent-routing cases
- handoff accuracy and done-evidence quality checks
- regression cases for over-delegation and scope leakage

### Durable artifact contracts

- optional schemas for generated reports and resumable state
- staleness markers that force re-verification against current repository state
- clearer examples of intake, routing, contract freeze, and release handoff

### Paperwork hardening

- additional real-world fixtures for image-only PDFs and multilingual OCR
- native Windows validation or a documented WSL support contract
- optional signed receipts backed by a separately managed identity system
- carefully reviewed Office and TIFF intake without weakening the fail-closed
  path and case-integrity model
- usability studies for review queues and qualified-professional handoff

### Installer lifecycle hardening

- additional Windows and Linux distribution coverage
- compatibility fixtures for future Codex profile and configuration changes
- explicit migration tests for every future managed-file format change
- clearer package provenance and checksum workflows if distribution expands

### Community evidence

- documented real-world activation and upgrade cases
- issue templates that capture resolved CLI, profile, and drift evidence
- contributor examples that demonstrate safe lean and department routing

## Non-goals

The roadmap does not currently include:

- a scheduled local orchestration daemon
- a hidden hook-driven auto-spawner
- Responses API beta integration presented as local Codex behavior
- unlimited nested or recursively autonomous subagents
- automatic commit, push, merge, release, or deploy authority
- a mandatory GPT-5.6 or Ultra entitlement

Any future change to those boundaries requires explicit architecture review,
source verification, migration design, and a new release contract.
