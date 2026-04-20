---
name: release-manager
description: Classify release impact, discover the repo's release law, and draft the correct release artifact or PR copy for the current workspace.
---

1. Discover the repo's release law first from `AGENTS.md`, `README.md`, `CONTRIBUTING.md`, PR templates, and versioning or governance docs.
2. Determine whether the change is `major`, `minor`, `patch`, or `none`.
3. If the repo explicitly uses unreleased changelog entries, draft the `CHANGELOG.md` update it expects.
4. If the repo uses change fragments or release-managed changelog/version files, draft or update the fragment and leave `VERSION` and `CHANGELOG.md` alone unless the task is explicit release preparation.
5. Suggest a Conventional Commit style title that matches the real scope.
6. Produce a short PR summary with:
   - what changed
   - why it changed
   - what was validated
   - remaining risks or assumptions
7. Do not invent version bumps, release notes, or changelog edits that conflict with the repo's documented policy.
