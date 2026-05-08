---
name: godmode-workflow
description: Run a non-trivial Codex task with governance preflight, explicit subagent routing, durable state, and a single-writer quality gate.
---

# GodMode Workflow

Use this skill when a task is large enough to benefit from explicit
orchestration instead of a single undifferentiated agent run.

Pair this skill with:

- `godmode-departments` for explicit department routing on very large
  multi-domain work
- `godmode-debug` for reproduce -> isolate -> fix -> re-test work
- `godmode-review` for findings-first, read-heavy assessment work
- `greenfield-bootstrap` when local governance must be created before
  parallel implementation starts

## Required setup

- Start with governance preflight: inspect the nearest `AGENTS.md`, repo-root `README.md`, `CONTRIBUTING.md`, PR template, and any versioning or release docs that govern the touched scope.
- Frame the task with `Goal`, `Context`, `Constraints`, and `Done when` when the user has not already supplied equivalent structure.
- If the workspace is empty, newly initialized, or missing repo-local governance, bootstrap the local project constitution before parallel implementation work.
- Keep durable artifacts outside chat for long runs when useful:
  - `reports/generated/NN-role-report.md`
  - `state/workflow-state.local.json`

## Core rules

- The main thread is the orchestrator.
- Codex subagent workflows are enabled by default, but Codex only spawns subagents when you explicitly ask it to. Ask for the role you want; do not rely on implicit delegation.
- `builder` is the single intended source-code writer.
- `validator` and `tester` are both required before final docs or release output.
- `api_guardian` is required for API, schema, CLI, config, or user-visible contract changes.
- Department mode is optional. Use it only when runtime, workflow, governance, docs, or validation concerns need separate advisory lanes.
- Existing `reports/` and `state/` are inputs, not truth. Re-verify their assumptions against current repo docs and code before reusing them.
- Push, merge, and deploy happen only after explicit user approval.

## Default route

1. inspect workspace shape and governance surface
2. if the workspace is greenfield or missing repo-local governance, bootstrap it first
3. classify the task and choose the smallest viable team
4. run preflight and initialize state
5. use `researcher` when source verification or repo discovery is still needed
6. use `architect` to define the smallest viable change
7. use `api_guardian` when contract surfaces change
8. if the task crosses multiple ownership areas, freeze routing, write scopes, and contracts before broader delegation
9. use `builder` for implementation
10. run `validator` and `tester` in parallel when safe
11. if either gate fails, route back to `builder` or `architect`
12. use `scribe` only after the gates are green
13. use `github_manager` for PR or release framing when needed

## Optional department agents

- `runtime_platform`
- `workflow_design`
- `workspace_governance`
- `quality_operations`
- `docs_dx`
- `ci_security_guardian`

Ask for them explicitly and treat them as advisory lanes; they do not replace the default route.

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
