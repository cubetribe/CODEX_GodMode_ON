# Roadmap

This roadmap is not a list of “nice someday ideas.” It is the delivery path for the Codex GodMode port.

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

- a new reader understands the purpose, target shape, and next implementation step without extra context

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

- every step between intake and completion is documented as a deterministic flow

## Phase 3: Guardrails and helper tools

Goal:

- build the few helpers that make the system safer and more auditable

Expected contents:

- preflight checks
- API impact detection
- report validation
- pre-push approval guard

Done when:

- critical rules are not only described but can also be enforced technically

## Phase 4: Reference implementation

Goal:

- express the documented architecture as a runnable reference inside the repo

Expected contents:

- first custom agents
- first skills
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
