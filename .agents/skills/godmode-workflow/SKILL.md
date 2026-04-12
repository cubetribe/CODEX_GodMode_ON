---
name: godmode-workflow
description: Run a non-trivial task through the Codex GodMode workflow with explicit routing, single-writer discipline, parallel quality gates, and human approval before push.
---

# GodMode Workflow

Use this skill when a task is large enough to benefit from explicit orchestration instead of a single undifferentiated agent run.

For very large multi-domain work, pair this skill with `godmode-departments` to activate the explicit department-routing layer.

## Core rules

- The main thread is the orchestrator.
- Scale the workflow to the task. Start with the smallest viable team and only fan out when the task crosses ownership boundaries or contract risk.
- Start every non-trivial run with a governance preflight: inspect the nearest `AGENTS.md`, repo-root `README.md`, `CONTRIBUTING.md`, PR template, and any versioning or contract docs that govern the touched scope.
- Treat repo docs as binding once discovered, even when the repo has no root `AGENTS.md`.
- If the workspace is empty, newly initialized, or missing repo-local governance, bootstrap the local project constitution first.
- Use focused subagents explicitly; do not assume Codex will spawn them on its own.
- `builder` is the single intended source-code writer.
- `validator` and `tester` are both required before final docs or release output.
- Existing `reports/` and `state/` are inputs, not truth. Re-verify their assumptions against current repo docs and code before reusing them.
- Do not fan out into parallel implementation work until the local governance scaffold exists.
- Push happens only after explicit user approval.

## Default flow

1. inspect workspace shape and governance surface
2. if the workspace is greenfield or missing repo-local governance, bootstrap it first
3. classify the task and choose the smallest viable team
4. run preflight and initialize state
5. use `researcher` when source verification or repo discovery is still needed
6. use `architect` to define the smallest viable change
7. use `api_guardian` if API, schema, CLI, config, or user-visible contracts changed
8. if the task crosses multiple ownership areas, freeze routing, write scopes, and contracts before broader delegation
9. use `builder` for implementation
10. run `validator` and `tester` in parallel when safe
11. if either gate fails, route back to `builder` or `architect`
12. use `scribe` only after the gates are green
13. use `github_manager` for PR/release framing when needed

## Outputs

- keep the main thread concise
- write local generated reports under `reports/generated/` when a persisted handoff is useful
- keep local workflow state under `state/`
- record which repo rules or governance docs controlled the work when that affects implementation, docs, or release output
- refresh or supersede stale workflow state instead of silently carrying it forward
- when greenfield bootstrap was required, record which local governance files were created before implementation began

## Do not use when

- the task is a one-line answer
- there is no meaningful implementation or validation step
- the task is pure brainstorming with no execution
