# Department-Agent Orchestration Plan

Date: 2026-04-12
Workspace: `/Volumes/2TB_CodingProjekte/Coding_Projekte/CODEX_GodMode_ON-Lokal`
Branch: `main`
Scope: reverse-engineer the department-based working model used in `VersionCue` and translate it into a concrete GodMode target plan for Codex as of April 2026.

## Purpose

Design a stronger GodMode operating model where:

- the main thread acts as `CEO/CTO`
- specialized department agents own bounded domains
- planning and contract freeze happen before parallel implementation
- reports and state stay outside chat history
- Codex-native best practices remain aligned with current official docs

## Inputs Used

### Local repositories

- Current repo:
  - `AGENTS.md`
  - `README.md`
  - `docs/blueprint.md`
  - `.codex/config.toml`
  - `.codex/agents/*.toml`
  - `.agents/skills/godmode-workflow/SKILL.md`
- Neighbor repo:
  - `/Volumes/2TB_CodingProjekte/Coding_Projekte/VersionCue/docs/product/project-groups/*`
  - `/Volumes/2TB_CodingProjekte/Coding_Projekte/VersionCue/docs/architecture/workstream-integration-contracts.md`
  - `/Volumes/2TB_CodingProjekte/Coding_Projekte/VersionCue/docs/product/delivery-execution-plan.md`
  - `/Volumes/2TB_CodingProjekte/Coding_Projekte/VersionCue/reports/generated/godmode-foundation-discovery.md`

### Official online sources checked on 2026-04-12

- Codex Prompting Guide:
  - `https://developers.openai.com/cookbook/examples/gpt-5/codex_prompting_guide`
- Codex best practices:
  - `https://developers.openai.com/codex/learn/best-practices`
- AGENTS.md guidance:
  - `https://developers.openai.com/codex/guides/agents-md`
- Skills guidance:
  - `https://developers.openai.com/codex/skills`
- Subagents concepts:
  - `https://developers.openai.com/codex/concepts/subagents`
- Building an AI-Native Engineering Team:
  - `https://developers.openai.com/codex/guides/build-ai-native-engineering-team`
- Reasoning best practices:
  - `https://developers.openai.com/api/docs/guides/reasoning-best-practices`

## Reverse-Engineered Pattern From `VersionCue`

### What worked

- The project was split into explicit workstreams:
  - `Core Platform`
  - `Internal Workspace`
  - `Upload & Storage`
  - `Public Review`
  - `Ops And Quality`
- Parallel work was enabled by non-code artifacts first, not by agent cleverness.
- The key enabling artifacts were:
  - a frozen vocabulary
  - explicit route ownership
  - source-of-truth mapping
  - blocking decisions before parallel build
  - required cross-team contracts
  - entry gates and exit gates
  - per-workstream mission, write scope, dependencies, deliverables, and out-of-scope
- A delivery execution plan defined:
  - start order
  - allowed parallelism
  - phase gates
  - frozen assumptions
- Governance and ops docs reduced drift:
  - public contracts
  - env contract
  - local readiness
  - smoke checks
  - seed strategy

### What was weak

- Ownership was documented, but not strongly machine-enforced.
- Some docs drifted from the actual MVP contract.
- Orchestration state was only partially persisted.
- The method was strong, but still manual. That let planning gaps leak into implementation.

### Main lesson

The winning pattern was not "many agents at once." The winning pattern was:

1. freeze shared terms and contracts
2. freeze ownership boundaries
3. define start order and gates
4. only then let departments work in parallel

## Codex Best-Practice Takeaways For April 2026

### Verified facts from official docs

- Codex does not auto-spawn subagents. Parallel agent work must be explicitly requested.
- Subagents are most useful for read-heavy work such as exploration, triage, review, testing, and summarization.
- Write-heavy parallelism should be used carefully because it increases coordination cost and edit conflicts.
- `gpt-5.4` is the default starting point for main agents and ambiguous multi-step work.
- `gpt-5.4-mini` is appropriate for fast read-heavy supporting agents.
- `AGENTS.md` should stay practical, layered, and concise. More specific files override broader ones.
- Skills rely on progressive disclosure. Clear descriptions matter because implicit activation depends on them.
- Reliable Codex usage improves when the repo makes "what good looks like" explicit for testing, review, and done criteria.
- The Codex Prompting Guide recommends a strong bias for action, good tool usage, and parallel read operations where safe.

### Design implications for this repo

- GodMode should keep the main thread as orchestrator instead of turning it into another builder.
- Department agents should be specialized and bounded by ownership, not generic "do everything" workers.
- Workflow roles should remain, but as staff functions or mandatory gates around department work.
- Report summaries should come back to the main thread instead of raw logs to reduce context pollution.
- The repo should distinguish between:
  - runtime law
  - workflow law
  - workspace governance
  - validation and release law

## Proposed GodMode Target Model

### Control structure

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

### Why this split

- The current GodMode repo is still largely workflow-role-centric.
- The `VersionCue` technique was stronger because it was domain-centric.
- The best hybrid model is:
  - departments own domains and write scopes
  - staff offices own planning, research, contract review, and release review

## Recommended Ownership Model

| Unit | Role in system | Primary ownership |
| --- | --- | --- |
| `CEO/CTO Orchestrator` | intake, routing, sequencing, gate decisions, escalation | main thread only |
| `Research Office` | repo discovery, external verification, option framing | current `researcher` |
| `Architecture Office` | plans, interfaces, change shape, rollback | current `architect` |
| `Contract Office` | AGENTS, config, agent/skill contracts, state/report schema, installer alignment | current `api_guardian` plus contract-specific rules |
| `Release Office` | docs finalization, release framing, PR/release discipline | current `scribe` plus `github_manager` |
| `Runtime Platform` | `.codex/config.toml`, `.codex/agents/`, runtime defaults, thread limits, state format | new department agent |
| `Workflow Design` | `.agents/skills/`, orchestration loops, handoffs, resume behavior, prompt protocols | new department agent |
| `Workspace Governance` | `AGENTS.md`, templates, repo-local constitution rules | new department agent |
| `Quality & Operations` | `scripts/`, checks, install/verify flow, smoke paths, environment readiness | new department agent |
| `Docs & Developer Experience` | `README.md`, `docs/`, prompt docs, operator guidance | new department agent |
| `Web`, `Apple`, `Flutter` guilds | advisory skill/domain support | existing skills stay advisory |

## Mandatory Pre-Parallelization Artifacts

The following should exist before two or more departments are allowed to write in parallel.

### 1. Intake Brief

Required fields:

- objective
- non-goals
- release impact
- affected departments
- contract sensitivity
- expected validations

### 2. Department Routing Map

Required fields:

- involved departments
- upstream/downstream order
- blocker relationships
- which staff office must review before build starts

### 3. Frozen Vocabulary And Contract Pack

Required fields:

- frozen terms
- frozen interfaces
- invariants
- user-visible contract surfaces
- out-of-scope items for this slice

### 4. Write-Scope Matrix

Required fields:

- department
- owned paths
- forbidden paths
- temporary lease if a cross-cutting edit is needed

### 5. State Record

Required fields:

- task id
- current phase
- active departments
- gate status
- unresolved blockers
- last verified assumptions

### 6. Report Contract

Every department report should stay short and structured:

- what was checked
- what changed or should change
- blockers
- contract assumptions
- next required handoff

### 7. Gate Checklist

At minimum:

- architecture gate
- contract gate
- validation gate
- test gate
- release/docs gate when applicable

## Recommended Routing Law

### Default routing sequence

1. `CEO/CTO Orchestrator` performs governance preflight.
2. `Research Office` verifies repo facts or external facts when needed.
3. `Architecture Office` creates the smallest safe plan.
4. `Contract Office` reviews any contract-sensitive scope.
5. The relevant department agents execute bounded work.
6. `validator` and `tester` run as gates.
7. `Release Office` runs only after gates are green.

### Parallelization rules

- Parallelize read-heavy work first.
- Do not parallelize write-heavy work without disjoint write scopes.
- Default rule: one active writer per path.
- Limit active department branches to 2-4, even if technical thread limits are higher.
- The main thread should only receive summaries, not raw intermediate output.

### Model defaults

| Use case | Recommended model |
| --- | --- |
| CEO/CTO orchestration | `gpt-5.4` |
| architecture or contract decisions | `gpt-5.4` |
| read-heavy scouting and discovery | `gpt-5.4-mini` |
| large review/test scans where speed matters | `gpt-5.4-mini` |

## Concrete Plan For This Repo

### Phase 0: Freeze the redesign law

Outcome:

- agree that the primary split becomes department-based
- agree that current workflow roles become staff offices or gates

Deliverables:

- one architecture decision doc for the department model
- one routing law doc
- one write-scope matrix template
- one state record template

### Phase 1: Introduce the artifacts, not the full runtime

Outcome:

- GodMode can operate with department planning before any new department agents are introduced

Deliverables:

- `reports/generated/` report template for department handoffs
- `state/` template for active orchestration state
- documentation that defines required pre-parallelization artifacts

Why first:

- this captures the strongest `VersionCue` advantage immediately
- it reduces the risk of another manually parallelized run with soft contracts

### Phase 2: Refactor the conceptual model in docs

Outcome:

- canonical docs describe CEO/CTO plus departments plus staff offices

Deliverables:

- update `docs/blueprint.md`
- update `README.md`
- update `docs/roadmap.md`
- add a department-architecture doc under `docs/`

### Phase 3: Add new department agents

Recommended new agents:

- `runtime_platform`
- `workflow_design`
- `workspace_governance`
- `quality_operations`
- `docs_dx`

Rules:

- keep existing `researcher`, `architect`, `api_guardian`, `validator`, `tester`, `scribe`, `github_manager`
- do not remove the current roles until docs, templates, and runtime behavior are aligned
- each new agent must declare:
  - exact scope
  - when it triggers
  - when it must not trigger
  - whether it can write

### Phase 4: Rework skill surface

Outcome:

- skills activate the right department behavior instead of only the old workflow loop

Recommended actions:

- keep `$godmode-workflow` as the top-level entry skill
- add department-specific reusable skills only where the procedure repeats
- keep skill descriptions sharp so implicit matching stays reliable
- do not create a skill for every concept unless it solves a repeated workflow problem

### Phase 5: Add machine-readable coordination enforcement

Outcome:

- ownership and contract drift become detectable

Recommended actions:

- add a write-scope registry or lease file
- add script checks for:
  - docs alignment
  - missing contract updates
  - agent/skill/template drift
  - state file integrity
- consider `CODEOWNERS` or equivalent ownership scaffolding if GitHub governance is part of rollout

### Phase 6: Run one real pilot

Pilot goal:

- one non-trivial repo task executed with:
  - CEO/CTO orchestration
  - staff-office preflight
  - department routing
  - bounded department execution
  - validator/tester gates
  - final release/docs synthesis

Success criteria:

- no ambiguous ownership during execution
- no contract drift discovered late
- state and reports are sufficient to resume the run
- the main thread stays concise and decision-focused

## Recommended First Implementation Slice

If work starts immediately, the lowest-risk first slice is:

1. document the department model
2. add the planning artifacts and templates
3. keep current agent files intact
4. pilot the model using the existing roles plus manual department labels
5. only then add new department agents

This sequence avoids changing too many layers at once.

## Key Risks And Countermeasures

| Risk | Countermeasure |
| --- | --- |
| departments act on inconsistent assumptions | require frozen contract pack before parallel start |
| multiple agents edit the same files | enforce write-scope matrix and single-writer rule |
| main thread gets flooded with noise | return only short department reports |
| docs, agents, skills, and templates drift apart | make `Contract Office` gate mandatory for runtime-law changes |
| too much complexity too early | introduce artifacts first, agents second |
| skills become vague and trigger badly | keep descriptions narrow and explicit |
| human loses control of the strategy | keep routing, release, push, and deploy under human plus CEO/CTO control |

## Recommendation

Proceed with a staged redesign, not a big-bang rewrite.

The immediate value is not "more agents." The immediate value is:

- stronger orchestration law
- mandatory planning artifacts
- explicit department routing
- persistent state and handoffs

Once those exist, department agents become safer and more useful.
