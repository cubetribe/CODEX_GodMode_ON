# Roadmap

This roadmap is not a list of “nice someday ideas.” It is the delivery path for the Codex GodMode port.

Current release: `1.0.0`.

## Release status

| Phase | Status in 1.0.0 |
| --- | --- |
| Phase 0: Blueprint | complete |
| Phase 1: Repository scaffolding | complete |
| Phase 2: Orchestrator contract | complete as documented workflow guidance |
| Phase 3: Guardrails and helper tools | partially complete through install and environment checks |
| Phase 4: Reference implementation | complete as an installable Codex runtime package |
| Phase 5: Validation and community hardening | ongoing |

## Phase 0: Blueprint

Goal:

- analyze the source system
- verify current Codex capabilities
- document the initial orchestrator, roles, and gates

Deliverables:

- `README.md` as the public entry point
- `docs/blueprint.md` as the architecture core
- `docs/roadmap.md` as the delivery plan

Done when:

- a new reader understands the purpose, target shape, and implementation status without extra context

## Phase 1: Optional department scaffolding

Status: done

Goal:

- add the planning artifacts that make larger multi-domain runs safe without forcing department mode on every task

Expected contents:

- packaged agent definitions under `templates/global-codex/agents/`
- packaged skill definitions under `templates/global-codex/skills/`
- state and report directories
- documented `[agents]` configuration examples

Done when:

- a contributor can choose lean, guided, or department mode without guessing what artifacts are required

## Phase 2: Blueprint and docs alignment

Status: done

Goal:

- align the public docs with the scalable target model while keeping current runtime state separate from the future design

Expected contents:

- updated `README.md`
- updated `docs/blueprint.md`
- department model doc
- roadmap and repo conventions aligned with the new scaling law

Done when:

- every step between intake and completion is documented as a deterministic Codex workflow

## Phase 3: Department-aware runtime additions

Status: done

Goal:

- add department-specific runtime pieces only after the docs and templates are stable

Expected contents:

- first department-oriented agent definitions
- GitHub security and CI coverage for `.github/**` and repo-protection surfaces
- skill refinements where procedures repeat
- runtime rules for write scopes and bounded delegation

Done when:

- the runtime can scale up into department mode without replacing the existing role-centric baseline

## Phase 4: Guardrails and enforcement

Status: in progress

Goal:

- build the helpers that make the system safer and more auditable

Current sprint focus:

- fill `CHANGELOG.md` under `[Unreleased]` and codify the changelog law
- add `ci_security_guardian`, baseline CI, and `CODEOWNERS`
- codify the validation law and expand `scripts/check-local-env.sh`
- publish `docs/agent-registry.md` and close current-state versus target-state doc drift
- expand the GodMode skill family with dedicated debug and review companion skills

Expected contents:

- preflight checks
- contract drift checks
- report and state validation
- write-scope enforcement helpers
- approval and release guardrails where needed

Done when:

- critical install and readiness rules are not only described but can also be checked locally

## Phase 5: Pilot runs and hardening

Status: next

Goal:

- test the scalable reference against real use cases and sharpen the weak points

Expected contents:

- core custom agents and optional department agents
- core workflow skills, companion lane skills, and stack skills
- example flows for feature work, debugging, and API changes

Done when:

- a new user can reproduce the workflow locally

## Phase 5: Validation and community hardening

Goal:

- test the reference against real use cases and sharpen the weak points

Expected contents:

- demo runs
- discussion-driven feedback
- refinement of unclear boundaries and gates
- versioning of the blueprint and later of the runtime

Done when:

- the system is stable enough for repeated use and understandable to contributors outside the core team

## After 1.0.0

Likely next hardening areas:

- example reports and state files that demonstrate clean handoffs
- optional schema checks for `reports/` and `state/`
- eval-style examples for skill trigger accuracy and workflow routing
- broader documentation examples from real web, Apple, Flutter, review, and debug runs
- CI checks for shell scripts, markdown links, and packaged agent or skill metadata
