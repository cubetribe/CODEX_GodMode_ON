# Safety and review

## Local handling

- Request an explicit case root and explicit inputs. Never scan a home directory implicitly.
- On macOS, reject `/tmp` because it traverses a symlink; use `/private/tmp` only
  for disposable synthetic tests and a deliberately protected location for real cases.
- Refuse case roots inside any Git worktree and reject symbolic links, hard links, traversal paths, and unexpected case files.
- Apply restrictive permissions where the platform supports them: case directories `0700`, working files `0600`, and originals `0400`.
- Keep absolute source paths out of records and archives.
- Do not install tools, access networks, upload documents, send messages, submit forms, delete material, or destroy paper originals.

## Review states

`PASS` means the configured mechanical gate passed. It does not certify the underlying statement. `REVIEW` means a human must resolve uncertainty. `FAIL` means a policy, integrity, processing, or validation invariant was violated and downstream release must stop.

Visual inspection is a fallback for individual unresolved pages, not a deterministic foundation. Feed declared-human text, normalized bounding box, reviewer name, and note through `resolve-page --input`; never rewrite a page record manually. Require a separate scoped human confirmation for every critical claim.

## High-stakes use

Use the workflow to prepare and trace evidence for tax, legal, compliance, and administrative work. Do not characterize output as professional advice or automatically authoritative. Keep filing, submission, deadline decisions, deletion, and final legal or tax conclusions behind a qualified human gate.

## Archive release

Archives are uncompressed tar files and are not encrypted. Require `--acknowledge-plain-archive`. Refuse failed or stale validation. Releasing a review-bearing case additionally requires `--allow-review`, a named declared-human approver, and a UTF-8 note file; the note is included and hashed inside the archive. Both 2.10 content labels retain the complete state-bound case so extraction remains verifiable. Write the archive outside the case, Git worktrees, and Codex runtime storage, never overwrite it, and verify the exact canonical USTAR bytes, manifest, complete materialized case, receipt, and SHA-256 sidecar before transfer. Appended bytes and unmanifested or state-unbound files are integrity failures. A structurally valid review-bearing archive still returns `REVIEW`, not `PASS`.
