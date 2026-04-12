---
name: godmode-departments
description: Activate the optional department-based GodMode routing layer for large multi-domain tasks that need frozen ownership, handoffs, and controlled delegation.
---

# GodMode Departments

Use this skill together with `godmode-workflow` when the task is large enough that one generic build lane would create ambiguity across runtime, workflow, governance, operations, or docs ownership.

## Purpose

Turn on the explicit department-routing layer without making it the default for every run.

## When to use

- the task crosses multiple ownership areas
- routing, write scopes, and contracts must be frozen before broader delegation
- several specialized agents need bounded scopes and handoffs
- the run should stay resumable outside chat history

## When not to use

- the task is a small or medium single-scope change
- `godmode-workflow` plus normal roles is enough
- the only extra need is quick research, architecture input, or contract review

## Required behavior

1. Keep `godmode-workflow` as the top-level control loop.
2. Choose only the departments that are actually needed.
3. Start with staff-office preflight before department writing begins.
4. Create or refresh:
   - intake brief
   - department routing map
   - write-scope matrix
   - orchestration state record
5. Keep one active writer per path unless a temporary lease is explicitly recorded.
6. Route summaries back to the orchestrator instead of raw logs.
7. Keep `validator` and `tester` as the required quality gate.

## Department choices

- `runtime_platform` for `.codex/config.toml`, `.codex/agents/`, and runtime-law changes
- `workflow_design` for `.agents/skills/`, routing templates, and orchestration artifacts
- `workspace_governance` for `AGENTS.md` and governance templates
- `quality_operations` for `scripts/`, readiness checks, and install/verify flow
- `docs_dx` for `README.md`, `docs/`, and prompt surfaces

## Output expectation

Return a concise routing decision:

- selected departments
- required staff offices
- write-scope boundaries
- blockers before parallel work can start
