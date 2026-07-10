# Prototype Mode

Updated: 2026-07-10

Prototype mode is a disposable, local-only fast lane. It reduces production
governance while keeping one writer, mandatory watermarks, and end-to-end
evidence for the behavior the prototype promises.

> **PROTOTYPE ONLY — LOCAL TESTING — DO NOT DEPLOY**

Use `$godmode-prototype` instead of `$godmode-workflow` for the spike. Return to
the full workflow before the result is shared, promoted, committed to `main`, or
connected to production.

## Contract

- no real credentials, production data, live services, shared branches, or
  release paths
- one `builder` owns all prototype writes
- files live under `prototype/` or `spike/`, or use a `proto_` prefix
- every generated source file carries the prototype watermark
- the run exercises the user's actual path from input to observable result
- output includes the command, result or observation, unverified edges, and a
  migration checklist

Creating expected files, starting a process, or rendering an empty shell is not
completion. If the promised behavior cannot be demonstrated locally, report the
prototype as incomplete and name the missing evidence.

## Model and runtime

Prototype mode inherits the parent session's model and reasoning level. GPT-5.6
can be selected for a demanding spike when available, but the package does not
hard-pin it or Ultra.

The lean prototype config is a project config, not a named global profile. Copy
it to the prototype workspace:

```bash
mkdir -p .codex
cp /path/to/CODEX_GodMode_ON-Lokal/templates/prototype-mode/config.toml \
  .codex/config.toml
```

It sets `workspace-write`, disables approval interruptions and network access,
and limits subagents to two threads at one depth. Because
`approval_policy = "never"` is intentionally permissive inside the workspace,
use this config only for disposable local work. The model and reasoning effort
remain inherited.

You can also copy `templates/prototype-mode/AGENTS.md` into the prototype or
spike workspace as its minimal governance overlay.

## When to use it

Use prototype mode for:

- a technical spike answering one focused question
- rapid comparison of local approaches
- a disposable proof of concept
- a local demo that will not ship directly

Do not use it when:

- the output is intended for production, staging, a shared branch, or external
  users
- real credentials, production databases, or live external services are needed
- API or data-contract safety cannot be deferred
- the production workflow is feasible and the output is not truly disposable

## Fast loop

```text
1. state goal, local boundary, three-bullet plan, file scope, and observable result
2. assign one builder all writes
3. add a watermark to every generated source file
4. run the smallest end-to-end check that exercises the promised behavior
5. record command, actual result or observation, and unverified edges
6. return files, evidence, and migration checklist
```

Prototype mode skips the full governance, contract, structural, documentation,
and release gates. It does not skip proof that the prototype itself works.

## Watermark

Adapt this block to the source language:

```text
PROTOTYPE ONLY — NOT FOR PRODUCTION
Created in GodMode Prototype Mode for local testing.
Do not commit to main, deploy, or use real credentials.
Run through $godmode-workflow before production use.
```

Examples:

```python
# PROTOTYPE ONLY — NOT FOR PRODUCTION
# Created in GodMode Prototype Mode for local testing.
# Do not commit to main, deploy, or use real credentials.
# Run through $godmode-workflow before production use.
```

```typescript
// PROTOTYPE ONLY — NOT FOR PRODUCTION
// Created in GodMode Prototype Mode for local testing.
// Do not commit to main, deploy, or use real credentials.
// Run through $godmode-workflow before production use.
```

## Safe fixtures

Use placeholders, mocks, and disposable local resources:

- `placeholder_api_key` or `test_token`
- `localhost` or `127.0.0.1`
- an in-memory or disposable local database
- deterministic fixtures instead of live API calls

Keep network access disabled. If the experiment cannot proceed without a live
production-like dependency, it has outgrown prototype mode.

## Promotion checklist

Start a new production workspace task with `$godmode-workflow`, then:

- [ ] reassess repository governance and architecture
- [ ] move or rename files out of prototype-only locations
- [ ] remove every prototype watermark
- [ ] replace placeholders through approved secret and configuration paths
- [ ] review changed API, schema, CLI, or config contracts with `api_guardian`
- [ ] run independent `validator` and `tester` gates
- [ ] prove the production done criterion end to end
- [ ] follow the target repository's release law
- [ ] obtain explicit authority for commit, push, deploy, or another external
      mutation

Prototype output does not become production-ready merely by removing its
watermark.

## Shipped files

| File | Purpose |
| --- | --- |
| `templates/global-codex/skills/godmode-prototype/SKILL.md` | executable skill contract |
| `templates/prototype-mode/AGENTS.md` | minimal local governance overlay |
| `templates/prototype-mode/config.toml` | lean project-level runtime config |
| `docs/prompts/prototype-start-prompt.md` | copy-paste task starter |

Unlike debug, review, and department routing, prototype mode is not a companion
layer inside the production workflow. It replaces that workflow temporarily for
throwaway exploration, then hands promotion back to `$godmode-workflow`.
