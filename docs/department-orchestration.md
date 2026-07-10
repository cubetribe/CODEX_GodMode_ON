# Department Orchestration

Updated: 2026-07-10

Department mode is the optional scaling layer for GodMode tasks that cross
multiple ownership areas. Use `$godmode-workflow` with
`$godmode-departments` only when a lean lane would blur ownership, contracts,
validation, or release risk.

## Lanes

| Lane | Team shape | Use it when |
| --- | --- | --- |
| Lean | orchestrator, one `builder`, `validator`, `tester` | one clear scope with low cross-domain risk |
| Guided | lean lane plus selected staff agents | source discovery, architecture, or contract review matters |
| Department | guided lane plus 2–4 bounded department tracks | ownership crosses runtime, workflow, governance, quality, docs, or CI/security |

Independent read-only tracks can run in parallel. Tracked-file writes remain
with one normal `builder`; a department writer is an exception that requires an
explicit, isolated file scope.

## Departments

| Department | Agent | Scope |
| --- | --- | --- |
| Runtime Platform | `runtime_platform` | Codex defaults, toolchain, sandbox, local-vs-cloud behavior, and environment |
| Workflow Design | `workflow_design` | skill boundaries, routing, handoffs, prompts, reports, and state conventions |
| Workspace Governance | `workspace_governance` | AGENTS layering, branch policy, release law, and local constitutions |
| Quality Operations | `quality_operations` | validation strategy, regression gates, installer checks, and eval-style evidence |
| Docs & Developer Experience | `docs_dx` | README, setup docs, prompts, and contributor-facing clarity |
| CI & Security | `ci_security_guardian` | Actions, CODEOWNERS, Dependabot, pinned actions, permissions, and protection |

## Delegation envelope

Each department task must state:

1. objective
2. inputs and governing instructions
3. required output
4. allowed write scope, or `read-only`
5. done criterion
6. escalation condition

This contract prevents an advisory track from becoming an open-ended second
implementation lane.

## Routing sequence

1. run governance and capability preflight
2. choose the smallest viable team
3. use parallel read-only discovery only for independent questions
4. synthesize findings, review changed contracts, and freeze vocabulary and
   write scopes
5. assign one normal implementation writer
6. run independent `validator` and `tester` gates
7. map every done criterion to outcome evidence
8. let `scribe` and `github_manager` frame release work only after gates pass
9. stop at commit, push, merge, release, deploy, or another external mutation
   unless that exact action is authorized

Useful durable artifacts include the intake brief, routing map, write-scope
matrix, handoff reports, and workflow state templates under `reports/` and
`state/`. Re-read them against the current repository before relying on them.

## When not to use it

Do not activate department mode for a small edit, a one-file documentation fix,
a straightforward defect, or any task where one writer plus normal validation
is clearer. More agents should reduce uncertainty or produce independent
evidence; otherwise they only add coordination cost.
