---
name: godmode-workflow
description: Orchestrate non-trivial Codex delivery through governance and capability preflight, bounded parallel discovery, a frozen single-writer contract, independent validation, outcome evidence, and release handoff. Use for complex implementation, migration, or release work that benefits from coordinated subagents.
---

# GodMode Workflow

Apply project instructions before this workflow. Use the smallest team that can
prove the requested outcome.

## Operating contract

- Keep the main thread as orchestrator and decision owner.
- Let every custom agent inherit the parent session's model and reasoning level.
- Delegate proactively only when the user, project guidance, or an active skill
  authorizes it and parallel work materially improves speed or quality.
- Keep delegation to one depth. Parallelize independent read-only work; keep one
  implementation writer for tracked files.
- Re-verify existing reports and state against current repository evidence.
- Treat commit, push, merge, release, deploy, and external mutations as separate
  authority boundaries unless the user already authorized them.

## Delegation envelope

State all six fields for every delegated task:

1. objective
2. inputs and governing instructions
3. required output
4. allowed write scope, or `read-only`
5. done criterion
6. escalation condition

Do not delegate an open-ended role without this contract.

## Delivery phases

### 1. Governance and capability preflight

- Inspect the nearest `AGENTS.md`, repository guidance, contribution rules,
  release law, and contracts that govern the requested scope.
- Inspect the actual workspace, branch, dirty state, tool availability, and
  applicable local skills or agents.
- Report assumptions, proposed write scope, and expected impact before editing
  when they are not already obvious.
- Bootstrap repo-local governance before parallel implementation in an empty or
  undocumented greenfield workspace.

### 2. Bounded discovery

- Use `researcher` and focused read-only specialists only for unresolved facts.
- Run independent discovery lanes in parallel when useful.
- Require evidence, affected paths or interfaces, and open questions; do not
  accept generic summaries as handoffs.

### 3. Synthesis and contract freeze

- Reconcile discovery into one plan, explicit write scope, interface decisions,
  validation commands, rollback risks, and user-visible done criteria.
- Use `architect` for design choices and `api_guardian` for API, schema, CLI,
  config, or other compatibility surfaces.
- Obtain user approval before a material plan, scope, risk, or external-state
  change unless that exact work was already authorized.
- Freeze the contract before implementation. Escalate instead of guessing when
  discovery leaves a material decision unresolved.

### 4. Single-writer implementation

- Give one `builder` the frozen write scope and done criteria.
- Do not run parallel writers over the same repository state.
- Stop implementation and return to synthesis when a contract gap appears.

### 5. Independent quality gates

- After the writer finishes, run `validator` and `tester` in parallel when safe.
- Keep `validator` read-only and focused on structure, contracts, and static
  consistency.
- Let `tester` create only necessary temporary outputs while reproducing the
  changed behavior with focused commands.
- Route implementation failures to `builder` and design failures to synthesis,
  then rerun the relevant gates.

### 6. Outcome-evidence gate

- Map every done criterion to concrete evidence: command output, test result,
  rendered artifact, observed UI/API behavior, or an explicitly documented
  manual check.
- Do not call work complete merely because files exist, a process starts, or a
  generic smoke command exits zero.
- State residual risks and anything not verified.

### 7. Scribe and release handoff

- Use `scribe` only after quality and outcome gates pass.
- Update only the documentation and release artifacts required by the
  repository's release law, and report checks truthfully.
- Use `github_manager` for branch, PR, or release framing when that surface is
  authorized.

## Optional native long-run path

For a long task, the user may start with `/plan`, approve the plan, and then use
`/goal` for persistent continuation. This is optional, does not replace the
workflow gates, and does not broaden permissions. The workflow also works in a
normal task without `/plan` or `/goal`.

## Companion skills

- `$godmode-debug` for reproduce-isolate-fix work
- `$godmode-review` for findings-first read-only assessment
- `$godmode-departments` for cross-domain advisory routing
- `$godmode-prototype` for explicitly local, disposable experiments
- `$greenfield-bootstrap` when repo-local governance is missing
