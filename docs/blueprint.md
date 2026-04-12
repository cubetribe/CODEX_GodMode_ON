# Blueprint: Codex GodMode

Updated: 2026-04-12

This document is the core architecture blueprint for the Codex-native port of [cubetribe/ClaudeCode_GodMode-On](https://github.com/cubetribe/ClaudeCode_GodMode-On).

The goal is not to copy the Claude implementation blindly. The goal is to preserve the strong orchestration pattern and translate it into a modern Codex structure built around:

- `AGENTS.md`
- `.codex/config.toml`
- `.codex/agents/*.toml`
- `.agents/skills/`
- persistent `reports/` and `state/`

## Current Repo State

Today this repository ships a role-centric GodMode baseline:

- the main thread acts as orchestrator
- the installed runtime centers on `researcher`, `architect`, `api_guardian`, `builder`, `validator`, `tester`, `scribe`, and `github_manager`
- the repo now also ships first optional department-oriented agents for runtime, workflow, governance, operations, and docs surfaces
- reusable procedures live in skills such as `$godmode-workflow`
- persistent reports and state are present, but still lightweight

This is the current repo state, not the final target architecture.

## Verified Codex Constraints

The current official Codex docs support the following design assumptions:

- Codex uses explicit subagent workflows rather than hidden automatic delegation.
- Read-heavy work is the safest default for parallel subagents.
- Write-heavy parallelism requires careful ownership boundaries.
- `AGENTS.md` remains the primary layered governance surface.
- Skills are the right place for reusable procedures, not for every one-off idea.
- `gpt-5.4` is the default model for main orchestration and deeper reasoning.
- `gpt-5.4-mini` is appropriate for faster supporting scans and read-heavy helpers.

## Core Architecture Direction

GodMode should evolve into a two-layer system:

1. a `CEO/CTO` orchestrator in the main thread
2. an optional department layer for larger, multi-domain tasks

The word optional matters. Not every task should fan out into many agents.

## Scalable Routing Modes

### Lean lane

Use this for small, single-scope work.

- orchestrator
- `builder`
- normal validation and test gates

This should remain the default for many day-to-day tasks.

### Guided lane

Use this when the task is still small enough to avoid departments, but planning or contracts matter.

- orchestrator
- optional `researcher`
- `architect`
- optional `api_guardian`
- `builder`
- `validator` and `tester`

### Department lane

Use this only when the task crosses multiple ownership areas and needs explicit handoffs.

- orchestrator
- staff-office preflight
- 2-4 bounded department tracks
- validation gates
- release/docs closeout if needed

## Target Control Structure

```text
CEO/CTO Orchestrator (main thread, read-only)
|- Staff Offices
|  |- Research Office
|  |- Architecture Office
|  |- Contract Office
|  `- Release Office
|- Product Departments
|  |- Runtime Platform
|  |- Workflow Design
|  |- Workspace Governance
|  |- Quality & Operations
|  `- Docs & Developer Experience
`- Specialist Guilds
   |- Web
   |- Apple
   `- Flutter
```

## Current Roles Mapped Into The Target Model

| Current role | Target place | Notes |
| --- | --- | --- |
| `researcher` | `Research Office` | read-only fact finding |
| `architect` | `Architecture Office` | design, rollback, dependency planning |
| `api_guardian` | `Contract Office` | contract and surface review |
| `builder` | implementation lane | still the normal writer |
| `validator` | quality gate | read-heavy structural checks |
| `tester` | quality gate | executable verification |
| `scribe` | `Release Office` | final docs and summary layer |
| `github_manager` | `Release Office` | PR/release/governance coordination |

The department layer is now partially scaffolded in the runtime, but it remains optional and should not replace the role-centric baseline for routine work.

## Department Responsibilities

| Department | Owns |
| --- | --- |
| `Runtime Platform` | `.codex/config.toml`, `.codex/agents/`, runtime defaults, state schema |
| `Workflow Design` | `.agents/skills/`, orchestration loops, handoffs, resume behavior |
| `Workspace Governance` | `AGENTS.md`, templates, repo-local constitutions |
| `Quality & Operations` | `scripts/`, checks, install/verify flow, smoke paths |
| `Docs & Developer Experience` | `README.md`, `docs/`, prompts, operator guidance |

## Routing Law

The target routing law is:

1. governance preflight
2. choose the smallest viable team
3. if uncertainty is high, use `Research Office`
4. if structure is unclear, use `Architecture Office`
5. if contracts are touched, use `Contract Office`
6. only then activate departments when the task truly spans multiple ownership areas
7. keep one active writer per path unless a temporary lease is explicitly granted
8. run `validator` and `tester`
9. use `Release Office` only after the gates are green

## Mandatory Artifacts For Department Mode

Department mode should not start without these artifacts:

- `Intake Brief`
- `Department Routing Map`
- `Frozen Vocabulary And Contract Pack`
- `Write-Scope Matrix`
- `Department Handoff Report`
- `State Record`

These artifacts are now documented in [docs/department-orchestration.md](./department-orchestration.md) and templated under `reports/templates/` and `state/templates/`.

## Invariants

- The orchestrator does not implement code directly.
- The orchestrator chooses the smallest viable team instead of defaulting to maximum fan-out.
- Repo governance must be discovered before planning or editing.
- Greenfield work must create repo-local governance before parallel delivery starts.
- `builder` remains the normal code writer.
- `validator` and `tester` remain the required joint quality gate.
- `api_guardian` remains mandatory when contract surfaces are touched.
- Push and deploy still require explicit human approval.
- State and reports support resume, but current repo docs and code remain the source of truth.

## Staged Rollout

This repo should evolve in this order:

1. document optional department routing and the mandatory artifacts
2. add templates for intake, routing, write scopes, handoffs, and state
3. align README, blueprint, roadmap, and skill guidance
4. add department-specific agents only after the documents and templates are stable
5. add machine-readable enforcement later

## Why this port matters

The value does not come from "more agents." The value comes from:

- hard ownership boundaries
- controlled handoffs
- auditable gates
- explicit human approval for risky actions
- the ability to scale up and back down depending on the task

Codex now has the native building blocks for that pattern. This repo exists to turn those ideas into a documented, versioned, and eventually fully implemented system.

## Sources

- Source repo: [cubetribe/ClaudeCode_GodMode-On](https://github.com/cubetribe/ClaudeCode_GodMode-On)
- Codex docs: [Subagents](https://developers.openai.com/codex/concepts/subagents)
- Codex docs: [Best practices](https://developers.openai.com/codex/learn/best-practices)
- Codex docs: [Agent Skills](https://developers.openai.com/codex/skills)
- Codex docs: [Custom instructions with AGENTS.md](https://developers.openai.com/codex/guides/agents-md/)
- Codex docs: [Configuration reference](https://developers.openai.com/codex/config-reference/)
- OpenAI Cookbook: [Codex Prompting Guide](https://developers.openai.com/cookbook/examples/gpt-5/codex_prompting_guide)
