---
name: godmode-debug
description: Run a reproducible bug or failing validation path through a disciplined reproduce, isolate, fix, and re-test loop.
---

# GodMode Debug

Use this skill together with `godmode-workflow` for regressions, failing builds, failing tests, runtime bugs, and unclear breakages that need evidence before a fix.

## Required setup

- Start with governance preflight before changing files.
- Frame the task with `Goal`, `Context`, `Constraints`, and `Done when`.
- Capture durable evidence in `reports/generated/` when the repro is non-trivial or likely to be resumed later.

## Core rules

- Reproduce first. Do not guess at fixes before the failure is observed or a concrete proxy signal is identified.
- Codex only spawns subagents when you explicitly ask it to. Use explicit roles for investigation or verification; do not assume background delegation.
- `builder` remains the single normal code writer.
- Keep the repro and validation loop as small and deterministic as possible.
- If the issue is actually a review-only or architecture question, pair the run with `$godmode-review` instead.

## Default route

1. capture the failing symptom, repro steps, and expected result
2. use `researcher` or `runtime_platform` if environment, tooling, or platform behavior is still unclear
3. use `architect` only when the root cause suggests a wider design issue
4. use `builder` for the smallest safe fix
5. run `validator` and `tester` against the failing path
6. if the repro still fails, loop back with updated evidence
7. use `scribe` only after the fix and re-test are green

## Optional helpers

- `runtime_platform` for sandbox, toolchain, local-vs-cloud, or OS-specific behavior
- `quality_operations` for tightening reproduction commands, assertions, or regression coverage

## Do not use when

- the task is a general feature request
- the workspace needs first-time governance scaffolding; pair the run with `$greenfield-bootstrap` first
