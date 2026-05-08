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
- document the target architecture, roles, and gates

Deliverables:

- `README.md` as the public entry point
- `docs/blueprint.md` as the architecture core
- `docs/roadmap.md` as the delivery plan

Done when:

- a new reader understands the purpose, target shape, and implementation status without extra context

## Phase 1: Repository scaffolding

Goal:

- prepare the target structure in the repo without building the full runtime yet

Expected contents:

- `.codex/agents/`
- state and report directories
- documented `[agents]` configuration examples

Done when:

- the visible repo structure matches the blueprint

## Phase 2: Orchestrator contract

Goal:

- lock down the control contract of the main orchestrator

Expected contents:

- state schema
- report schema
- routing rules
- gate definitions
- resume and failure paths

Done when:

- every step between intake and completion is documented as a deterministic Codex workflow

## Phase 3: Guardrails and helper tools

Goal:

- build the few helpers that make the system safer and more auditable

Expected contents:

- preflight checks
- API impact detection
- report validation
- pre-push approval guard

Done when:

- critical install and readiness rules are not only described but can also be checked locally

## Phase 4: Reference implementation

Goal:

- express the documented architecture as a runnable reference inside the repo

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
- refinement of unclear roles and gates
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
