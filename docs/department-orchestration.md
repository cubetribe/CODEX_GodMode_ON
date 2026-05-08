# Department Orchestration

Department mode is the optional scaling layer for GodMode tasks that cross multiple ownership areas.

Use it with `$godmode-workflow` and `$godmode-departments` only when the normal lean lane would blur ownership, validation, or release risk.

## Lanes

| Lane | When to use it |
| --- | --- |
| Lean lane | Small or clear single-scope work. The main thread orchestrates, `builder` writes, and `validator` plus `tester` close the gate. |
| Guided lane | Add `researcher`, `architect`, or `api_guardian` when source discovery, design risk, or contract risk matters. |
| Department lane | Add bounded department agents when work crosses runtime, workflow, governance, quality, docs, or CI/security ownership. |

## Department agents

| Department | Agent | Scope |
| --- | --- | --- |
| Runtime Platform | `runtime_platform` | Codex runtime defaults, toolchains, sandboxing, local-vs-cloud behavior, and environment issues |
| Workflow Design | `workflow_design` | skill boundaries, routing, handoffs, prompts, reports, and state conventions |
| Workspace Governance | `workspace_governance` | AGENTS layering, branch policy, release law, repo rules, and local project constitutions |
| Quality Operations | `quality_operations` | validation strategy, smoke paths, installer checks, and eval-style checks |
| Docs & Developer Experience | `docs_dx` | README, setup docs, prompts, and contributor-facing clarity |
| CI & Security | `ci_security_guardian` | GitHub Actions, CODEOWNERS, Dependabot, pinned actions, permissions, and repository protection |

## Routing rules

1. Run governance preflight first.
2. Freeze write scopes before more than one writer starts.
3. Prefer department agents as advisory lanes.
4. Keep `builder` as the single normal implementation writer.
5. Keep `validator` and `tester` as the required quality gate.
6. Route API, schema, CLI, config, or user-visible contract changes through `api_guardian`.
7. Stop before commit, push, merge, release, or deploy unless the user explicitly approves the action.

## When not to use it

Do not activate department mode for small edits, one-file docs fixes, straightforward bug fixes, or tasks where one `builder` plus normal validation is enough.

Extra agents should reduce ambiguity. If they only add latency, token cost, or coordination overhead, stay in the lean lane.
