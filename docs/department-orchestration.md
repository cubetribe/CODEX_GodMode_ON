# Department Orchestration

Updated: 2026-04-17

This document explains how GodMode should scale from a lean orchestrator loop into a department-based model without forcing every task through a large multi-agent setup.

## Principle

The orchestrator should choose the smallest viable team for the task.

That means:

- do not default to maximum fan-out
- do not create departments for single-scope work
- do introduce departments when ownership, contracts, and handoffs would otherwise become ambiguous

The explicit skill entrypoint for this mode is `godmode-departments`, used together with `godmode-workflow`.

`godmode-debug` and `godmode-review` are narrower workflow companions. They do
not imply department mode on their own.

## Current State Versus Target State

### Current repo state

- the installed runtime is role-centric
- the main thread orchestrates
- the standard roles are `researcher`, `architect`, `api_guardian`, `builder`, `validator`, `tester`, `scribe`, and `github_manager`
- the repo now also includes optional department-oriented agents for runtime, workflow, governance, operations, docs, and GitHub security/CI surfaces
- the repo also includes focused workflow companions for debugging and
  findings-first review without forcing department mode

### Target state

- the main thread acts as `CEO/CTO`
- staff offices support planning and governance
- department tracks are activated only when the task spans multiple ownership areas

## Scaling Modes

### Lean mode

Use when:

- the change stays within one main ownership area
- the risk is low
- no special contract freeze is needed

Typical team:

- orchestrator
- `builder`
- `validator`
- `tester`

### Guided mode

Use when:

- research is needed
- the design is still unclear
- a contract or config surface may change

Typical team:

- orchestrator
- optional `researcher`
- `architect`
- optional `api_guardian`
- `builder`
- `validator`
- `tester`

### Department mode

Use when:

- the task touches multiple ownership areas
- several parts of the repo need explicit handoffs
- contract freeze must happen before implementation spreads
- resuming the run later would be risky without persistent routing/state artifacts

Typical team:

- orchestrator
- staff-office preflight
- 2-4 active department tracks
- validation gates
- optional release closeout

## Staff Offices

| Office | Source role | Responsibility |
| --- | --- | --- |
| `Research Office` | `researcher` | repo discovery, source verification, external research |
| `Architecture Office` | `architect` | shape the plan, define interfaces, expose dependency order |
| `Contract Office` | `api_guardian` | review config, schema, API, prompt-surface, and state/report contracts |
| `Release Office` | `scribe` + `github_manager` | docs finalization, PR framing, release and governance checks |

## Departments

| Department | Owns |
| --- | --- |
| `Runtime Platform` | `.codex/config.toml`, `.codex/agents/`, runtime defaults, state schema |
| `Workflow Design` | `.agents/skills/`, orchestration loops, handoff rules, resume behavior |
| `Workspace Governance` | `AGENTS.md`, templates, governance layering |
| `Quality & Operations` | `scripts/`, verification flow, local readiness, smoke paths |
| `Docs & Developer Experience` | `README.md`, `docs/`, prompts, maintainer guidance |

## Optional Department Agents

| Agent | Department | Owns | Triggered when |
| --- | --- | --- | --- |
| `runtime_platform` | `Runtime Platform` | `.codex/agents/**`, runtime defaults, state scaffolding | runtime defaults, agent definitions, or state scaffolding change |
| `workflow_design` | `Workflow Design` | `.agents/skills/**`, routing templates, orchestration procedures | workflow law, reusable skill behavior, or routing artifacts change |
| `workspace_governance` | `Workspace Governance` | `AGENTS.md`, governance templates, bootstrap constitutions | repo governance or template law changes |
| `quality_operations` | `Quality & Operations` | `scripts/**`, readiness checks, smoke paths | local validation, readiness checks, or install/verify flow changes |
| `docs_dx` | `Docs & Developer Experience` | `README.md`, `docs/**`, prompt surfaces | contributor docs, prompts, or maintainer guidance change |
| `ci_security_guardian` | `Quality & Operations` | `.github/workflows/**`, `.github/CODEOWNERS`, `.github/dependabot.yml`, GitHub security guidance | any `.github/**` or CI/CD behavior changes, and optionally as a release gate before release prep |

## When To Escalate Into Department Mode

Escalate when two or more of these are true:

- more than one department owns the touched files
- the task needs frozen contracts before writing starts
- the task needs a resumable state record outside chat
- the task needs parallel read-heavy discovery before safe implementation
- a broad documentation, runtime, and template alignment pass is required

Stay out of department mode when:

- the work is a small fix
- one writer can finish safely without handoffs
- the only extra need is a quick research or architecture pass

## Mandatory Artifacts

Department mode should create or refresh these artifacts first:

- intake brief:
  - [reports/templates/intake-brief-template.md](../reports/templates/intake-brief-template.md)
- department routing map:
  - [reports/templates/department-routing-map-template.md](../reports/templates/department-routing-map-template.md)
- write-scope matrix:
  - [reports/templates/write-scope-matrix-template.md](../reports/templates/write-scope-matrix-template.md)
- department handoff report:
  - [reports/templates/department-handoff-template.md](../reports/templates/department-handoff-template.md)
- orchestration state record:
  - [state/templates/orchestration-state.template.json](../state/templates/orchestration-state.template.json)

## Routing Law

1. Run governance preflight.
2. Choose lean, guided, or department mode.
3. If the task is multi-domain, run staff-office preflight before department writing begins.
4. Freeze vocabulary, routing, write scopes, and contract assumptions.
5. Keep one active writer per path unless a temporary lease is explicitly recorded.
6. Route findings and summaries back to the orchestrator, not full raw logs.
7. Keep `validator` and `tester` as the required quality gate.

## Example Choices

### Small repo-local fix

Use lean mode.

### Medium-risk config or contract change

Use guided mode with `architect` and `api_guardian`.

### Cross-cutting GodMode redesign

Use department mode with:

- `Runtime Platform`
- `Workflow Design`
- `Workspace Governance`
- `Docs & Developer Experience`

`Quality & Operations` joins when scripts, checks, or readiness flow are affected.
