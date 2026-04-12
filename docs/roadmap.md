# Roadmap

This roadmap is not a list of “nice someday ideas.” It is the delivery path for the Codex GodMode port.

## Phase 0: Blueprint baseline

Goal:

- analyze the source system
- verify current Codex capabilities
- document the initial orchestrator, roles, and gates

Deliverables:

- `README.md` as the public entry point
- `docs/blueprint.md` as the architecture core
- `docs/roadmap.md` as the delivery plan

Done when:

- a new reader understands the purpose, target shape, and next implementation step without extra context

## Phase 1: Optional department scaffolding

Goal:

- add the planning artifacts that make larger multi-domain runs safe without forcing department mode on every task

Expected contents:

- department-routing documentation
- intake, handoff, and write-scope templates
- state templates for resumable orchestration
- clear guidance that the smallest viable team should be the default

Done when:

- a contributor can choose lean, guided, or department mode without guessing what artifacts are required

## Phase 2: Blueprint and docs alignment

Goal:

- align the public docs with the scalable target model while keeping current runtime state separate from the future design

Expected contents:

- updated `README.md`
- updated `docs/blueprint.md`
- department model doc
- roadmap and repo conventions aligned with the new scaling law

Done when:

- the docs clearly answer:
  - what exists today
  - what the target model is
  - when to stay lean
  - when to fan out

## Phase 3: Department-aware runtime additions

Goal:

- add department-specific runtime pieces only after the docs and templates are stable

Expected contents:

- first department-oriented agent definitions
- skill refinements where procedures repeat
- runtime rules for write scopes and bounded delegation

Done when:

- the runtime can scale up into department mode without replacing the existing role-centric baseline

## Phase 4: Guardrails and enforcement

Goal:

- build the helpers that make the system safer and more auditable

Expected contents:

- preflight checks
- contract drift checks
- report and state validation
- write-scope enforcement helpers
- approval and release guardrails where needed

Done when:

- critical rules are not only described but can also be checked technically

## Phase 5: Pilot runs and hardening

Goal:

- test the scalable reference against real use cases and sharpen the weak points

Expected contents:

- demo runs across lean, guided, and department modes
- discussion-driven feedback
- refinement of unclear boundaries and gates
- versioning of the blueprint and later of the runtime

Done when:

- the system is stable enough for repeated use, understandable to contributors outside the core team, and does not require maximum fan-out to be effective
