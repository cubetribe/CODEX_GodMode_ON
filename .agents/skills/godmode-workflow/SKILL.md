---
name: godmode-workflow
description: Run a non-trivial task through the Codex GodMode workflow with explicit routing, single-writer discipline, parallel quality gates, and human approval before push.
---

# GodMode Workflow

Use this skill when a task is large enough to benefit from explicit orchestration instead of a single undifferentiated agent run.

## Core rules

- The main thread is the orchestrator.
- Use focused subagents explicitly; do not assume Codex will spawn them on its own.
- `builder` is the single intended source-code writer.
- `validator` and `tester` are both required before final docs or release output.
- Push happens only after explicit user approval.

## Default flow

1. classify the task
2. run preflight and initialize state
3. use `researcher` when source verification or repo discovery is still needed
4. use `architect` to define the smallest viable change
5. use `api_guardian` if API, schema, CLI, config, or user-visible contracts changed
6. use `builder` for implementation
7. run `validator` and `tester` in parallel when safe
8. if either gate fails, route back to `builder` or `architect`
9. use `scribe` only after the gates are green
10. use `github_manager` for PR/release framing when needed

## Outputs

- keep the main thread concise
- write local generated reports under `reports/generated/` when a persisted handoff is useful
- keep local workflow state under `state/`

## Do not use when

- the task is a one-line answer
- there is no meaningful implementation or validation step
- the task is pure brainstorming with no execution
