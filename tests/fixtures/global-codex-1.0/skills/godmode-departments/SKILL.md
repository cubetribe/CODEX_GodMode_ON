---
name: godmode-departments
description: Activate optional department-based routing for cross-domain Codex tasks that need frozen ownership and advisory handoffs before implementation.
---

# GodMode Departments

Use this skill together with `godmode-workflow` only when a task crosses multiple concerns strongly enough that one linear workflow would blur ownership.

## When it fits

- runtime or platform behavior is entangled with workflow design
- repo governance or release law is part of the implementation decision
- validation strategy or docs UX needs a dedicated advisory pass
- a long-running task needs clearer ownership boundaries before `builder` starts

## Department map

- `runtime_platform`: environment, tooling, sandbox, OS, local-vs-cloud, and runtime behavior
- `workflow_design`: orchestration flow, prompt structure, skill boundaries, and durable state/report design
- `workspace_governance`: `AGENTS.md`, release law, branch policy, repo contracts, and instruction layering
- `quality_operations`: validation scope, regression gates, eval ideas, and repeatable checks
- `docs_dx`: README, setup docs, prompts, and user-facing clarity
- `ci_security_guardian`: GitHub Actions, CODEOWNERS, pinned actions, and repository security posture

## Routing rules

- Run governance preflight first; department mode does not skip it.
- Codex only spawns subagents when you explicitly ask it to. Name the department agent you want.
- Department agents are advisory and read-heavy by default.
- Keep a single writer. `builder` or `scribe` owns edits after the advisory lanes converge.
- Stop using department mode once ownership is clear and continue under `$godmode-workflow`, `$godmode-debug`, or `$godmode-review`.

## Do not use when

- the default workflow is already clear
- the task is small enough that extra routing would slow it down
