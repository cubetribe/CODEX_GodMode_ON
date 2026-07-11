# Blueprint: Codex GodMode 2.10

Updated: 2026-07-11

This is the architecture contract for the Codex-native port of
[cubetribe/ClaudeCode_GodMode-On](https://github.com/cubetribe/ClaudeCode_GodMode-On).
Version 2.10 is an implemented, installable runtime, not a future design sketch.

The port preserves the useful pattern — explicit orchestration, specialist
roles, quality gates, and human authority boundaries — while using native Codex
guidance, configuration, custom agents, skills, and subagents.

## Current 2.10 runtime

The repository ships:

- a global `AGENTS.md` contract with one managed marker block
- a model-neutral base `config.toml` with a bounded six-thread, one-depth agent
  budget
- 14 custom agent manifests under `templates/global-codex/agents/`
- 10 reusable skills under `templates/global-codex/skills/`
- four separate `godmode-*.config.toml` stack profiles
- safe macOS/Linux and Windows installers with exact drift checks
- shell, Windows PowerShell 5.1, and PowerShell 7 regression coverage
- repository validation, CI/security checks, report templates, and state
  conventions
- one optional, separately installed `godmode-paperwork` plugin with a local-only
  deterministic workflow for sensitive document evidence

The package source stays under `templates/global-codex/`. Putting the same
assets in this repository's `.codex/agents/` or `.agents/skills/` paths would
create duplicate project and personal capabilities after global installation.

## Native Codex boundaries

The 2.10 design follows these verified Codex behaviors:

- subagents are a stable Codex capability and may be activated by a direct
  request, applicable project guidance, or an active skill
- child agents inherit the parent session's model, reasoning, sandbox, and
  approval context unless an authorized surface overrides it
- independent read-heavy work is the safest use of parallel subagents
- profiles in Codex `0.134.0+` are separate `$CODEX_HOME/NAME.config.toml` files
- `AGENTS.md` supplies layered durable guidance, agent TOML files define roles,
  and skills hold reusable procedures
- `/plan` can refine work and optional `/goal` can persist a long run without
  expanding permissions

GPT-5.6 is recommended for demanding parent sessions when the account supports
it. Ultra is useful for selected complex multi-agent work, but neither model nor
reasoning entitlement is hard-coded in this package. Every custom agent inherits
the choice made for the parent session.

GodMode local orchestration is not a scheduled-task daemon and is not the
Responses API multi-agent beta. It does not require hidden hooks to spawn work.

## System layers

| Layer | Source | Responsibility |
| --- | --- | --- |
| Repository governance | `AGENTS.md` | rules for changing and releasing this package |
| Global governance | `templates/global-codex/AGENTS.md` | default orchestration policy after installation |
| Technical defaults | `.codex/config.toml`, `templates/global-codex/config.toml` | sandbox, approval, web-search, MCP, and agent limits |
| Stack profiles | `templates/global-codex/profiles/` | optional profile-specific behavior without model pins |
| Custom agents | `templates/global-codex/agents/*.toml` | narrow roles and sandbox boundaries |
| Skills | `templates/global-codex/skills/*/SKILL.md` | repeatable delivery procedures |
| Optional plugins | `.agents/plugins/marketplace.json`, `plugins/` | separately installed capabilities with their own stricter contracts |
| Durable artifacts | `reports/`, `state/` | evidence and resumable project context when needed |

## Orchestration contract

```text
1. governance and capability preflight
2. bounded parallel discovery
3. synthesis, contract review, and frozen write scope
4. one implementation writer
5. independent structural validator and executable tester
6. done-criterion outcome evidence
7. documentation and release handoff
8. separately authorized commit, push, merge, release, or deploy
```

### 1. Governance and capability preflight

The orchestrator inspects the nearest `AGENTS.md`, contribution guidance,
release law, contracts, workspace, branch, dirty state, tools, and relevant
skills before editing. Empty or undocumented projects get repo-local governance
before parallel implementation begins.

### 2. Bounded discovery

Use `researcher` and focused specialists only for unresolved facts. Parallelize
independent reads when it materially improves speed or confidence. Each handoff
must include evidence, affected paths or interfaces, and remaining questions.

### 3. Synthesis and contract freeze

The main task reconciles discovery into one plan, write scope, interface set,
validation strategy, risks, and observable done criteria. `architect` reviews
design decisions; `api_guardian` reviews API, schema, CLI, config, and other
compatibility surfaces. Material ambiguity returns to the user instead of being
guessed through.

### 4. Single-writer implementation

One `builder` owns normal tracked-file changes. A contract gap returns the run
to synthesis. Parallel writes are allowed only when ownership is genuinely
isolated and explicitly assigned; they are never the default optimization.

### 5. Independent quality gates

`validator` checks structure, contracts, static consistency, and repository
rules. `tester` runs focused executable verification and may create temporary
test outputs. Safe independent checks may run in parallel after the writer has
finished. Failures route back to the writer or to synthesis, then the relevant
gate repeats.

### 6. Outcome-evidence gate

Every done criterion maps to concrete evidence: a command result, test result,
rendered artifact, observed UI or API behavior, or a named manual check. File
presence, process startup, or a generic zero exit code is not enough when the
request promises an end-to-end result.

### 7. Scribe and release handoff

`scribe` updates only the documentation and release artifacts required by the
repository's release law, after quality and outcome gates pass.
`github_manager` frames branch, PR, and release work only within authority the
user has already granted.

## Paperwork extension contract

GodMode Paperwork is integrated at the repository and release level, but not at
the core installation level. The marketplace exposes it as `AVAILABLE`; the
user installs it separately and invokes `$godmode-paperwork` explicitly.

Its deterministic claim is limited to workflow control and artifact
reproducibility:

```text
explicit inputs
  -> immutable content-addressed originals
  -> native extraction
  -> page-scoped local OCR where required
  -> visual review only after OCR routing
  -> evidence anchors and bounded rules
  -> state-bound validation
  -> reproducible archive and independent verification
```

OCR text, document interpretation, and model reasoning remain fallible. Critical
claims require a scoped declared-human approval, and a `REVIEW` archive requires
a separate declared-human release gate with a note. The CLI performs no network access, tool
installation, document submission, or original destruction. Audit hashes detect
partial or accidental changes inside the case; they are not signatures and do
not protect against a coherent rewrite by an attacker controlling the case.

## Delegation envelope

Every delegated task states all six fields:

1. objective
2. inputs and governing instructions
3. required output
4. allowed write scope, or `read-only`
5. done criterion
6. escalation condition

Open-ended role delegation is outside the 2.10 contract.

## Scaling lanes

| Lane | Team shape | Use it when |
| --- | --- | --- |
| Lean | orchestrator, `builder`, `validator`, `tester` | one clear, low-cross-domain scope |
| Guided | lean lane plus selected `researcher`, `architect`, or `api_guardian` | facts, design, or contracts need independent review |
| Department | guided lane plus 2–4 bounded department tracks | ownership spans runtime, workflow, governance, quality, docs, or CI/security |

More agents are not inherently better. A specialist is justified when it
improves capability isolation, policy clarity, evidence quality, or safe
parallel discovery.

## Core roles

| Agent | Contract |
| --- | --- |
| `researcher` | read-only fact finding and source verification |
| `architect` | read-only design, interfaces, risk, and rollback thinking |
| `api_guardian` | read-only compatibility and contract review |
| `builder` | single normal implementation writer |
| `validator` | read-only structural and static gate |
| `tester` | executable verification with temporary-output authority |
| `scribe` | documentation and release artifacts after gates pass |
| `github_manager` | GitHub workflow framing within granted authority |

The six optional department roles are specified in
[Department Orchestration](./department-orchestration.md) and audited in the
[Agent Registry](./agent-registry.md).

## Persistent artifacts

Reports and state are useful when a run must survive compaction, handoff, or a
long pause. They are conventions and templates, not an autonomous runtime
engine. Current repository evidence always wins over stale artifacts.

Department mode can use:

- an intake brief
- a routing map
- a write-scope matrix
- focused handoff reports
- a resumable state record

## Safety invariants

- the main task remains orchestrator and decision owner
- proactive delegation must be authorized by the user, project guidance, or an
  active skill and must materially help
- independent reads may run in parallel; one normal writer owns implementation
- `api_guardian` is required for changed contract surfaces
- `validator` and `tester` must both pass before release documentation
- completion is evidence-backed and residual risks are explicit
- commit, push, merge, release, deploy, and external mutations are separate
  authority boundaries

## What 2.10 does not claim

- automatic execution outside an active Codex task
- a background scheduler or daemon
- Responses API beta compatibility
- machine-enforced report or state schemas
- unlimited or recursively deep agent fan-out
- a model entitlement that every user or account must have
- legally compliant storage, evidentiary certification, professional advice, or
  error-free OCR and interpretation

## Primary sources

- [Codex subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents)
- [Codex models](https://learn.chatgpt.com/docs/models)
- [Advanced configuration and profiles](https://learn.chatgpt.com/docs/config-file/config-advanced#profiles)
- [Long-running work and goals](https://learn.chatgpt.com/docs/long-running-work)
- [Build Codex skills](https://learn.chatgpt.com/docs/build-skills)
- [Build Codex plugins](https://learn.chatgpt.com/docs/build-plugins)
- [Codex hooks](https://learn.chatgpt.com/docs/hooks)
- [Codex CLI command reference](https://learn.chatgpt.com/docs/developer-commands?surface=cli)
- [Custom instructions with AGENTS.md](https://developers.openai.com/codex/guides/agents-md/)
