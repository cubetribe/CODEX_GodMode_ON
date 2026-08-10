# Reports

This directory is for generated analysis that is useful beyond chat but is not
part of the release ledger.

## Rules

- generated runtime reports should go under `reports/generated/`
- do not store secrets, full chat transcripts, or unrelated logs
- keep reports concise: scope, evidence, decision, open risk
- use `state/` instead when a long or paused task needs resumable execution
- record user-relevant unreleased behavior in `CHANGELOG.md`, never only here

`reports/generated/` is ignored by Git. Durable architectural rationale belongs
under `docs/research/`.
