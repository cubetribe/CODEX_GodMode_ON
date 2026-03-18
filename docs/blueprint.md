# Blueprint: Codex GodMode

Updated: 2026-03-18

This document is the core architecture blueprint for the Codex-native port of [cubetribe/ClaudeCode_GodMode-On](https://github.com/cubetribe/ClaudeCode_GodMode-On).

The goal is not to copy the Claude implementation blindly. The goal is to preserve the proven orchestration pattern and translate it into a modern Codex structure built around:

- `AGENTS.md`
- `.codex/config.toml`
- `.codex/agents/*.toml`
- `.agents/skills/`
- persistent `reports/` and `state/`

## Stage 1: Research Codex orchestration capabilities

### Findings

- Current Codex documentation describes the feature as `Subagents`, not as a separate “super-agent” product.
- Codex can spawn specialized agents in parallel and consolidate their output in the main thread.
- The built-in role types are `default`, `worker`, and `explorer`.
- Project-specific custom agents belong in `.codex/agents/*.toml`.
- Reusable procedures belong in `.agents/skills/`.
- `AGENTS.md` remains the main layered guidance mechanism.

### Architecture notes

- Codex cleanly separates guidance, technical configuration, custom agents, and reusable skills.
- Parallel subagents are best for read-heavy tasks such as research, mapping, and review.
- Write-heavy work should stay narrowly owned to avoid edit conflicts and unclear responsibility.

### Key decisions

- This port will be built around explicit subagent calls, not hidden hook automation.
- Roles will stay narrow and focused.
- Stable repeated procedures will later be moved into skills.

## Stage 2: Analyze `ClaudeCode_GodMode-On`

### Findings

- The source repository is a managed workflow system, not just a set of prompts.
- Its core pattern is:
  - non-implementing orchestrator
  - specialist roles
  - file-based report handoffs
  - quality gates
  - return loop back to the builder
- The main runtime roles are:
  - `researcher`
  - `architect`
  - `api_guardian`
  - `builder`
  - `validator`
  - `tester`
  - `scribe`
  - `github_manager`
- Communication relies heavily on report files rather than only on chat context.
- The strongest control mechanism is the dual quality gate: `validator` and `tester` both need to pass.

### Architecture notes

- Stability comes from strict role separation and clear handoffs, not from one oversized generalist agent.
- The original system expects long sessions and context loss, which is why it keeps its own state and restore mechanics.
- Some implementation details in the Claude repo are inconsistent and should not be copied as-is.

### Key decisions

- Preserve the role model, gate logic, report contracts, and explicit approval boundaries.
- Do not preserve the mix of hook magic, prompt pack behavior, and inconsistent state schemas.

## Stage 3: Codex-native target architecture

### Findings

- The Codex-native version does not need an all-purpose agent. It needs an explicit orchestrator plus focused custom agents.
- The target repository structure is:
  - `AGENTS.md` for the orchestrator constitution
  - `.codex/config.toml` for technical defaults and `[agents]` limits
  - `.codex/agents/*.toml` for role definitions
  - `.agents/skills/` for reusable procedures
  - `reports/` and `state/` for persistent artifacts

### Architecture notes

- The main thread remains the orchestrator and owns routing, gates, and approvals.
- `builder` stays the only normal code-writing role.
- `validator` and `tester` may run in parallel because they are validation-oriented and mostly read-heavy.
- `api_guardian` is conditional and activates only when API, schema, CLI, or config surfaces are affected.
- `scribe` and `github_manager` run only after the quality gate is green.

### Key decisions

- Introduce one clean state schema instead of carrying forward the inconsistent Claude state model.
- Keep report files in the design because they improve resume, auditability, and review.
- Reduce hooks to guardrails. Keep the real orchestration flow explicit in Codex.

## Stage 4: Runtime workflow design

### Findings

The target runtime loop is:

1. intake and task classification
2. preflight and state initialization
3. optional `researcher`
4. `architect`
5. conditional `api_guardian`
6. `builder`
7. parallel `validator` and `tester`
8. gate decision: done or back to `builder`
9. `scribe`
10. optional `github_manager`

### Architecture notes

- The main thread must explicitly say when subagents are started, waited on, reused, or closed.
- Resume cannot depend on chat history alone; state must stay visible outside the thread.
- Parallelism should never turn into multiple builders writing the same files.

### Error and retry model

- transient tool or MCP failure: retry once
- red quality gate: loop back to `builder`
- uncovered architecture issue: loop back to `architect`
- push, merge, or deploy: always require an explicit human decision

## Target flow

```mermaid
flowchart TD
    A["Intake and classification"] --> B["Preflight and state init"]
    B --> C{"Need research?"}
    C -->|yes| D["researcher"]
    C -->|no| E["architect"]
    D --> E
    E --> F{"API or contract impact?"}
    F -->|yes| G["api_guardian"]
    F -->|no| H["builder"]
    G --> H
    H --> I["validator"]
    H --> J["tester"]
    I --> K{"Both gates green?"}
    J --> K
    K -->|no| H
    K -->|yes| L["scribe"]
    L --> M{"Need PR or release action?"}
    M -->|yes| N["github_manager"]
    M -->|no| O["Done"]
    N --> O
```

## Runtime roles

| Role | Responsibility | Write access |
| --- | --- | --- |
| `orchestrator` | intake, routing, state, gates, approvals | no |
| `researcher` | external or internal research | no |
| `architect` | target structure, interfaces, risks, plan | no |
| `api_guardian` | API, schema, CLI, and config impact review | no |
| `builder` | smallest safe implementation | yes |
| `validator` | structural and static validation | no |
| `tester` | executable and test validation | no |
| `scribe` | changelog, docs, release notes, completion artifacts | docs only |
| `github_manager` | PR, release, and repo-facing coordination | no by default |

## Invariants

- The orchestrator does not implement code itself.
- `builder` is the only normal code-writing role.
- `validator` and `tester` are both required for a green quality gate.
- `api_guardian` is required when contract surfaces are touched.
- Push and deploy never happen without explicit human approval.
- State and reports are the resume source of truth, not chat history alone.

## Planned artifacts

Not fully implemented yet, but part of the intended design:

- `reports/v{workflow_version}/NN-role-report.md`
- `state/workflow-state.json`
- `docs/` for architecture and operations
- `.codex/agents/*.toml` for role definitions
- `.agents/skills/` for reusable procedures

## Why this port matters

The Claude template already proved that the value is not the model name. The value comes from:

- hard role separation
- controlled handoffs
- auditable gates
- clear human approval for risky actions

Codex now has the native building blocks for that pattern. This repo exists to turn those ideas into a documented, versioned, and eventually fully implemented system.

## Sources

- Source repo: [cubetribe/ClaudeCode_GodMode-On](https://github.com/cubetribe/ClaudeCode_GodMode-On)
- Codex docs: [Subagents](https://developers.openai.com/codex/subagents/)
- Codex docs: [Agent Skills](https://developers.openai.com/codex/skills/)
- Codex docs: [Custom instructions with AGENTS.md](https://developers.openai.com/codex/guides/agents-md/)
- Codex docs: [Configuration reference](https://developers.openai.com/codex/config-reference/)
