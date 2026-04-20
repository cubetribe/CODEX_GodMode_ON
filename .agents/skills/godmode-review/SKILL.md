---
name: godmode-review
description: Activate the findings-first GodMode review lane for code, architecture, and release-risk assessment.
---

# GodMode Review

Use this skill together with `godmode-workflow` when the task is mainly
analysis, review, or risk assessment and should stay read-heavy by default.

## Purpose

Turn on a findings-first review lane without replacing the main GodMode
orchestrator.

## When to use

- code review before merge
- architecture or subsystem assessment
- release-risk or regression-risk review
- repo understanding where findings matter more than immediate edits

## When not to use

- straightforward implementation work
- debugging that already has a concrete failing path to fix
- cases where the user already asked directly for code changes first

## Required behavior

1. Keep `godmode-workflow` as the top-level control loop.
2. Stay read-heavy by default and do not edit code unless the user asks.
3. Present findings first, ordered by severity, with file references when
   possible.
4. Make assumptions, testing gaps, and confidence visible instead of
   burying them in summary text.
5. Verify conclusions against repo governance, changed files, and available
   validation evidence.
6. Treat built-in review surfaces such as `/review` as complementary for
   diff-focused review, not as a replacement for broader repo or
   architecture assessment.
7. If the user later asks to implement fixes, stay under `godmode-workflow`
   and return to the normal build and validation lane.

## Output expectation

Return a concise review result with:

- scope reviewed
- findings first
- open questions or assumptions
- residual risks or missing validation
