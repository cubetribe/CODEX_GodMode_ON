# Prototype Mode

Updated: 2026-05-12

Prototype mode is the local-only fast lane in the GodMode runtime. It trades
governance depth for raw iteration speed when you need to explore an idea,
answer a technical question quickly, or validate a concept before committing
to full implementation.

## The core contract

Prototype mode makes one explicit trade-off: **speed now, production-readiness later.**

Every prototype output is watermarked `PROTOTYPE ONLY` and comes with a
migration checklist. Nothing leaves local development without going through
`$godmode-workflow` first.

Prototype mode does **not** downgrade the main model. The prototype config
leaves `model` unset so Codex uses the user's selected model, global default,
or explicit CLI `--model` value. The profile sets reasoning effort to `high`
because prototype code should still be good code.

## When to use prototype mode

Use `$godmode-prototype` when:

- you are exploring a new idea or architecture before investing in full implementation
- you need to answer a specific technical question quickly (a spike)
- you want to try multiple approaches in rapid succession
- you are building a local demo that will never ship directly
- `$godmode-workflow` would slow you down and the output is genuinely throwaway

Do not use `$godmode-prototype` when:

- the output will go to production, staging, or be committed to `main`
- the task touches real credentials, production databases, live APIs, or live
  external services
- correctness and contract safety cannot be deferred
- `$godmode-workflow` is feasible in the available time

## What prototype mode skips and keeps

| Gate | Prototype mode | Full `$godmode-workflow` |
| --- | --- | --- |
| Governance preflight | ❌ Skipped | ✅ Required |
| `api_guardian` | ❌ Skipped | ✅ Required when contracts change |
| `validator` | ❌ Skipped | ✅ Required |
| `tester` | ⚡ One smoke command | ✅ Full suite required |
| `scribe` | ❌ Skipped | ✅ Required after gates pass |
| `github_manager` | ❌ Skipped | ✅ Required for PRs |
| `builder` | ✅ Required | ✅ Required |
| Prototype watermark | ✅ Required | ❌ Not applicable |
| Migration checklist | ✅ Required | ❌ Not applicable |

## The prototype loop

```text
1. State the goal — one sentence
2. 3-bullet plan — what to build, where files go, what "running" means
3. Build — builder writes code with prototype header
4. Smoke — one command proves the code runs
5. Done — output includes migration checklist
```

## Prototype watermark

Every source file generated in prototype mode must begin with this header,
adapted to the language:

**Python / Shell:**

```python
# ⚠️ PROTOTYPE ONLY — NOT FOR PRODUCTION
# Created in GodMode Prototype Mode — local testing only.
# Do NOT commit to main, deploy, or use real credentials here.
# Run through $godmode-workflow before any production use.
```

**JavaScript / TypeScript / Swift / Dart / Go:**

```javascript
// ⚠️ PROTOTYPE ONLY — NOT FOR PRODUCTION
// Created in GodMode Prototype Mode — local testing only.
// Do NOT commit to main, deploy, or use real credentials here.
// Run through $godmode-workflow before any production use.
```

The watermark is not optional. It is the primary signal to anyone who opens
the file that this code is not ready for production and must not be deployed
or committed to a shared branch.

## File naming and placement

All prototype output must follow one of these conventions:

- **`proto_` prefix** — e.g. `proto_auth_flow.py`, `proto_api_client.ts`
- **`prototype/` directory** — e.g. `prototype/auth_flow.py`
- **`spike/` directory** — e.g. `spike/auth_flow.py`

This makes prototype files visually obvious in any file tree and prevents
accidental inclusion in production commits.

## No real credentials

Prototype code must not contain real API keys, tokens, passwords, or
production database connection strings. Use:

- `placeholder_api_key`
- `test_token`
- `localhost` or `127.0.0.1` for service addresses
- `sqlite:///:memory:` for databases

Prototype mode is local-only. Keep network access disabled and use local mocks,
fixtures, or disposable local services instead of live external endpoints.

## Migration checklist

When prototype output is validated and ready to become production code,
open a `$godmode-workflow` session and work through this checklist:

- [ ] Remove all `PROTOTYPE ONLY` header comments
- [ ] Rename or move files (remove `proto_` prefix, move out of `prototype/` or `spike/`)
- [ ] Replace all placeholder credentials, URLs, and config values
- [ ] Route through `architect` for design review
- [ ] Run `api_guardian` if any contracts, schemas, or CLI surfaces changed
- [ ] Run `validator` + `tester` — both gates must be green
- [ ] Follow the target repository's release law (`CHANGELOG.md`, change
  fragments, release-please, semantic-release, or no release artifact)
- [ ] Get explicit human approval before push or deploy

## Config and templates

The following files ship with prototype mode:

| File | Purpose |
| --- | --- |
| `templates/global-codex/skills/godmode-prototype/SKILL.md` | The skill — invoke with `$godmode-prototype` |
| `templates/prototype-mode/AGENTS.md` | Minimal governance overlay — copy into `prototype/` directories |
| `templates/prototype-mode/config.toml` | Lean local config that keeps the model user-defined — use for prototype sessions |
| `docs/prompts/prototype-start-prompt.md` | Copy-paste start prompt |

## Relationship to the rest of the GodMode skill family

```text
$godmode-workflow          ← main orchestrator for production work
  ├── $godmode-departments ← optional multi-domain routing layer
  ├── $godmode-debug       ← focused bug-fixing lane
  ├── $godmode-review      ← findings-first assessment lane
  ├── $greenfield-bootstrap ← governance creation for new workspaces
  └── $godmode-prototype   ← ⚡ local fast lane (this skill)
                             NOT a companion to godmode-workflow
                             REPLACES it for throwaway exploration
```

Unlike the other companion skills, `$godmode-prototype` is **not** a
companion to `$godmode-workflow`. It **replaces** it for throwaway
exploration. When you are ready to go to production, you switch **back**
to `$godmode-workflow`.

## Why this is not called "vibe mode"

Prototype mode still has rules:

- builder writes all code (not the orchestrator)
- a smoke test is required
- watermarks are mandatory
- migration checklist is mandatory

The goal is maximum speed within a defined boundary, not an unconstrained
free-for-all. The boundary exists so that prototype output is always clearly
marked and the path to production is always documented.
