---
name: release-manager
description: Classify release impact, draft changelog text, and suggest PR or commit copy for Codex configuration changes in this repository.
---

1. Determine whether the change is `major`, `minor`, `patch`, or `none`.
2. If behavior or recommended setup changed, draft a `CHANGELOG.md` entry under `[Unreleased]`; when explicitly preparing a release, move the entry into the dated release section and verify `VERSION`.
3. Suggest a Conventional Commit style title that matches the real scope.
4. Produce a short PR summary with:
   - what changed
   - why it changed
   - what was validated
   - remaining risks or assumptions
5. Do not invent version bumps if the repository has no release automation or versioning convention yet.
