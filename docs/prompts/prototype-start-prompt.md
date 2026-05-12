# Prototype Start Prompt

Use this for rapid local spikes, proof-of-concept experiments, and fast idea
exploration where speed matters more than production-readiness.

> ⚠️ All output from this prompt is **PROTOTYPE ONLY** — not for production.

These prompts assume the global install has already been applied.

---

## Prompt

```text
$godmode-prototype

Goal: <one sentence — what to build or explore>

Context:
- <stack, relevant files, or constraints — keep it short>

Done when:
- <one liner: what "working" looks like, e.g. "script runs and prints result">
```

---

## Best for

- technical spikes to answer a specific question quickly
- exploring a new library, API shape, or pattern locally
- rapid proof-of-concept before committing to full implementation
- local demos that will never ship directly

## What this skips

api_guardian, full validator and tester suites, scribe, changelog,
github_manager, governance preflight.

## What this keeps

builder, one smoke command, prototype watermarks on all generated output,
migration checklist.

## Optional extras

- specify a file naming convention (`proto_` prefix or `prototype/` folder)
- add a placeholder credential format if the task needs mock auth
- add a specific smoke command if you already know what "working" looks like

---

## When you are ready for production

Switch to the standard dev prompt and run through `$godmode-workflow`.
The migration checklist in the prototype output tells you exactly what still
needs to happen before production.

```text
$godmode-workflow

Goal: <promote prototype to production>

Context:
- prototype output is in <path>
- migration checklist: <paste checklist from prototype output>

Done when:
- validator and tester gates are green
- target repository release law is followed
- explicit approval given before push
```
