# AGENTS.md — Prototype Mode

> ⚠️ **THIS IS A PROTOTYPE WORKSPACE — LOCAL TESTING ONLY**
>
> Code created here is **not** production-ready.
> Do **not** deploy, push to `main`, or use real credentials here.

This file is the minimal governance overlay for a prototype or spike workspace.
Copy it into any `prototype/` or `spike/` directory to signal prototype intent
to Codex and any contributor who opens the folder.

---

## Prototype rules

- All source files must carry the `PROTOTYPE ONLY` header comment
  (see `$godmode-prototype` for the exact format per language).
- No real API keys, tokens, passwords, or production credentials.
  Use `placeholder_` or `test_` prefixed values only.
- No connections to production databases, message queues, or live
  external services.
- File naming: prefix with `proto_` OR keep all files inside this
  `prototype/` or `spike/` directory.
- Output is for local validation only — do not share externally.

## What is skipped in prototype mode

| Gate | Status in prototype mode |
| --- | --- |
| `api_guardian` | Skipped — no contract or schema enforcement |
| `validator` | Skipped — no full structural checks |
| `tester` | Reduced — one smoke command only |
| `scribe` | Skipped — no changelog updates |
| `github_manager` | Skipped — no PR, no push |

## What is still required

- `builder` writes all code
- one smoke command confirms the code runs or produces output
- migration checklist is included in output and reviewed before promotion

## Routing

Use `$godmode-prototype` to run a task in this mode.

When you are ready to bring prototype output to production, switch to
`$godmode-workflow` in the real project workspace and work through the
migration checklist.

## Validation note

`tester` in prototype mode runs only the single smoke command specified in
the task. Full suite runs happen after migration to production under
`$godmode-workflow`.
