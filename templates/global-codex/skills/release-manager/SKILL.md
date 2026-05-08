---
name: release-manager
description: Classify release impact, discover the repo's release law, and draft the correct release artifact or PR copy for the current workspace.
---

1. Determine whether the change is `major`, `minor`, `patch`, or `none`.
2. Discover the repo's release law from `AGENTS.md`, `README.md`, `CONTRIBUTING.md`, PR templates, and versioning or governance docs before deciding how to update release artifacts.
3. If the repo explicitly uses unreleased changelog entries, draft the `CHANGELOG.md` update it expects.
4. If the repo uses change fragments or release-managed changelog/version files, draft or update the fragment and leave `VERSION` and `CHANGELOG.md` alone unless the task is explicit release preparation.
5. When explicitly preparing a release, move the entry into the dated release section and verify `VERSION`.
6. Suggest a Conventional Commit style title that matches the real scope.
7. Produce a short PR summary with:
   - what changed
   - why it changed
   - what was validated
   - remaining risks or assumptions
8. Do not invent version bumps, release notes, or changelog edits that conflict with the repo's documented policy.
