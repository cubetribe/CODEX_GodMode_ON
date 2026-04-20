---
name: godmode-debug
description: Activate the dedicated GodMode debugging lane for reproducible bugs, regressions, and failing validation paths.
---

# GodMode Debug

Use this skill together with `godmode-workflow` when the task is mainly
about diagnosing and fixing a bug instead of building a new feature.

## Purpose

Turn on the dedicated debugging lane without replacing the main GodMode
orchestrator.

## When to use

- reproducible bugs
- failing builds, tests, or runtime paths
- regressions after a recent change
- cases where root-cause isolation matters more than broad implementation

## When not to use

- net-new feature work
- broad refactors without a concrete failure to chase
- findings-first analysis where no fix is expected yet

## Required behavior

1. Keep `godmode-workflow` as the top-level control loop.
2. Restate the failure in observable terms before changing code.
3. Prefer the loop: reproduce -> isolate -> fix -> re-test.
4. Keep changes minimal until the likely root cause is understood.
5. Record the exact failing command, path, or reproduction steps when they
   exist.
6. If the fix grows into a multi-domain change, add `godmode-departments`
   before broader parallel work.
7. If config, schema, CLI, or other contract surfaces change, route through
   `api_guardian`.
8. Do not hide the failure under unrelated cleanup or speculative refactors.

## Output expectation

Return a concise debug status with:

- reproduced failure or reason it could not be reproduced
- likely boundary or root-cause hypothesis
- minimal fix scope
- re-test result
