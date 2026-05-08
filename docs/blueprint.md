# Blueprint: Codex GodMode

Updated: 2026-05-08

This document is the core architecture blueprint for the Codex-native port of [cubetribe/ClaudeCode_GodMode-On](https://github.com/cubetribe/ClaudeCode_GodMode-On).

`1.0.0` is the first release where this blueprint matches an installable runtime package instead of only a target design.

The goal is not to copy the Claude implementation blindly. The goal is to preserve the proven orchestration pattern and translate it into a modern Codex structure built around:

- `AGENTS.md`
- `.codex/config.toml`
- `templates/global-codex/agents/*.toml`
- `templates/global-codex/skills/`
- persistent `reports/` and `state/`

## Current 1.0 Runtime

The repository now ships:

- a global installer that publishes guidance, config, agents, and skills to the user's Codex home
- eight core role agents for the normal workflow
- six optional department agents for large cross-domain work
- nine reusable skills covering the normal workflow, debug lane, review lane, department routing, greenfield bootstrap, stack guidance, and release framing
- local checks that verify both the repo package and the installed global runtime
- package sources stored outside repo-local Codex discovery paths to avoid duplicate project and personal skills in this bootstrap repository

The runtime is intentionally explicit. The main thread remains responsible for deciding when to use a specialist, when to wait for results, when to loop back, and when to stop for human approval.

## Stage 1: Research Codex orchestration capabilities

Today this repository ships a role-centric GodMode baseline:

- Current Codex documentation describes the feature as `Subagents`, not as a separate “super-agent” product.
- Codex can spawn specialized agents in parallel and consolidate their output in the main thread.
- Current Codex releases enable subagent workflows by default, but Codex only spawns subagents when explicitly asked.
- Subagents inherit the parent sandbox and approval state, and live parent runtime overrides are reapplied to children.
- The built-in role types are `default`, `worker`, and `explorer`.
- Project-specific custom agents belong in `.codex/agents/*.toml`.
- Reusable procedures belong in `.agents/skills/`.
- Skills use progressive disclosure: metadata is visible first, and `SKILL.md` is loaded only when the skill is selected.
- `AGENTS.md` remains the main layered guidance mechanism.
- This bootstrap repo packages global agents and skills under `templates/global-codex/` because `.codex/agents/` and `.agents/skills/` would be discovered as project-local duplicates after global installation.

This is the current repo state, not the final target architecture.

- Codex cleanly separates guidance, technical configuration, custom agents, and reusable skills.
- Parallel subagents are best for read-heavy tasks such as research, mapping, and review.
- Write-heavy work should stay narrowly owned to avoid edit conflicts and unclear responsibility.
- Multi-agent splits are worthwhile only when they improve capability isolation, policy isolation, prompt clarity, trace legibility, or parallel read-heavy work.
- Prompt and workflow quality should be validated with concrete checks where possible, such as trigger behavior, command execution, handoff accuracy, and final-answer correctness.

Today the GodMode workflow surface is intentionally split like this:

- This port will be built around explicit subagent calls, not hidden hook automation.
- Roles will stay narrow and focused.
- Stable repeated procedures belong in focused skills.

This keeps the main entry surface stable while still letting recurring
workflow types become explicit skills.

## Verified Codex Constraints

The current official Codex docs support the following design assumptions:

- Codex uses explicit subagent workflows rather than hidden automatic delegation.
- Read-heavy work is the safest default for parallel subagents.
- Write-heavy parallelism requires careful ownership boundaries.
- `AGENTS.md` remains the primary layered governance surface.
- Skills are the right place for reusable procedures, not for every one-off idea.
- `gpt-5.5` is the default model for main orchestration and deeper reasoning in this runtime.
- smaller current Codex models can be appropriate for faster supporting scans and read-heavy helpers when explicitly selected.

## Core Architecture Direction

GodMode should evolve into a two-layer system:

1. a `CEO/CTO` orchestrator in the main thread
2. an optional department layer for larger, multi-domain tasks

The word optional matters. Not every task should fan out into many agents.

## Scalable Routing Modes

- The Codex-native version does not need an all-purpose agent. It needs an explicit orchestrator plus focused custom agents.
- The target repository structure is:
  - `AGENTS.md` for the orchestrator constitution
  - `.codex/config.toml` for technical defaults and `[agents]` limits
  - `templates/global-codex/agents/*.toml` for packaged global role definitions
  - `templates/global-codex/skills/` for packaged global reusable procedures
  - `reports/` and `state/` for persistent artifacts

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

- The main thread must explicitly say when subagents are started, waited on, reused, or closed.
- Resume cannot depend on chat history alone; state must stay visible outside the thread.
- Parallelism should never turn into multiple builders writing the same files.
- Use `Goal`, `Context`, `Constraints`, and `Done when` as the default task frame when the user has not already supplied equivalent structure.
- For long-horizon work, keep durable project memory in markdown reports, state files, or specs that can be re-read after compaction or resume.

### When to use multi-agent routing

Start with one agent whenever possible. Add specialists when one of these signals is present:

- the task crosses runtime, workflow, governance, docs, or validation ownership
- a specialist needs different tools, policy, or instructions
- read-heavy exploration, verification, or source research can run independently
- eval or review evidence shows routing, tool selection, or handoff accuracy is a risk

Avoid extra agents when they only add more prompts, approval surfaces, latency, or token cost without clarifying the work.

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

The department layer now has concrete runtime scaffolding, but it remains optional and should not replace the role-centric baseline for routine work.

## Department Agent Rollout Status

Already implemented as `.toml` agents in the current repo state:

- `runtime_platform`
- `workflow_design`
- `workspace_governance`
- `quality_operations`
- `docs_dx`
- `ci_security_guardian`

Still target-state behavior rather than a separate current `.toml` surface:

- department mode should stay optional instead of becoming the default path for every run
- machine-enforced write-scope governance is still evolving beyond the current docs, validation law, and repo checks
- specialist guilds such as web, Apple, and Flutter remain skills first, not dedicated department agents

## Department Responsibilities

| Department | Owns |
| --- | --- |
| `Runtime Platform` | `.codex/config.toml`, `templates/global-codex/agents/`, runtime defaults, state schema |
| `Workflow Design` | `templates/global-codex/skills/`, orchestration loops, handoffs, resume behavior |
| `Workspace Governance` | `AGENTS.md`, templates, repo-local constitutions |
| `Quality & Operations` | `scripts/`, checks, install/verify flow, smoke paths |
| `Docs & Developer Experience` | `README.md`, `docs/`, prompts, operator guidance |
| `CI & Security` | `.github/`, CODEOWNERS, Dependabot, pinned actions, workflow permissions |

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

Current repo state documents and templates these department-mode artifacts:

- `Intake Brief`
- `Department Routing Map`
- `Write-Scope Matrix`
- `Department Handoff Report`
- `State Record`

Still target-state rather than a separate current template:

- `Frozen Vocabulary And Contract Pack`

The current documented and templated artifacts live in [docs/department-orchestration.md](./department-orchestration.md) and under `reports/templates/` and `state/templates/`.

## Optional department agents

Department agents are not the default path. They exist to clarify ownership when a task spans multiple domains.

| Agent | Responsibility | Write access |
| --- | --- | --- |
| `runtime_platform` | Codex runtime defaults, toolchains, sandboxing, and environment behavior | no |
| `workflow_design` | workflow procedures, skill boundaries, and handoff artifacts | no |
| `workspace_governance` | AGENTS layering, release law, branch policy, and repo rules | no |
| `quality_operations` | validation plans, install checks, smoke paths, and eval-oriented checks | no |
| `docs_dx` | README, setup docs, prompts, and contributor-facing clarity | no |
| `ci_security_guardian` | GitHub Actions, CODEOWNERS, pinned actions, and repository security posture | no by default |

## Invariants

- The orchestrator does not implement code itself.
- `builder` is the only normal code-writing role.
- `validator` and `tester` are both required for a green quality gate.
- `api_guardian` is required when contract surfaces are touched.
- Department agents are advisory unless the parent workflow explicitly assigns a bounded write scope.
- Push and deploy never happen without explicit human approval.
- State and reports are the resume source of truth, not chat history alone.

## Staged Rollout

Current conventions:

- `reports/generated/NN-role-report.md`
- `state/workflow-state.local.json`
- `docs/` for architecture and operations
- `templates/global-codex/agents/*.toml` for packaged role definitions
- `templates/global-codex/skills/` for packaged reusable procedures

Future work may add stricter schemas or automated checks for these artifacts. Today they are conventions, not a separate runtime engine.

## Release boundary

The 1.0 release is a runtime-package milestone. It does not claim:

- automatic state-machine execution outside Codex
- hidden auto-spawning of subagents
- automatic report or state schema enforcement
- CI/CD, deployment, or GitHub release automation

Those are future hardening areas. The current contract is a documented, installable, validated Codex workflow package.

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
- Codex docs: [Subagents](https://developers.openai.com/codex/subagents/)
- Codex docs: [Subagent concepts](https://developers.openai.com/codex/concepts/subagents)
- Codex docs: [Agent Skills](https://developers.openai.com/codex/skills/)
- Codex docs: [Custom instructions with AGENTS.md](https://developers.openai.com/codex/guides/agents-md/)
- Codex docs: [Configuration reference](https://developers.openai.com/codex/config-reference/)
- Codex docs: [Best practices](https://developers.openai.com/codex/learn/best-practices)
- OpenAI API docs: [Agents orchestration](https://developers.openai.com/api/docs/guides/agents/orchestration)
- OpenAI API docs: [Evaluate agent workflows](https://developers.openai.com/api/docs/guides/agent-evals)
- OpenAI Developers blog: [Testing Agent Skills Systematically with Evals](https://developers.openai.com/blog/eval-skills)
- OpenAI Developers blog: [Run long horizon tasks with Codex](https://developers.openai.com/blog/run-long-horizon-tasks-with-codex)
