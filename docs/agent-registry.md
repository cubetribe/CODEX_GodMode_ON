# Agent Registry

Updated: 2026-07-10

This registry documents the 14 GodMode agents packaged under
`templates/global-codex/agents/` and installed into `$CODEX_HOME/agents/`.
The package source stays outside repo-local discovery paths so this bootstrap
repository does not expose duplicate project and personal agents.

## Runtime contract

No manifest sets `model` or `model_reasoning_effort`. Every agent inherits the
parent session's model and reasoning level. GPT-5.6 is recommended for demanding
orchestration when available; Ultra is an opt-in for complex multi-agent work,
not a package requirement.

Read-only agents use `sandbox_mode = "read-only"`. A writable manifest defines
role capability, not permission to mutate arbitrary paths: the parent must still
assign an explicit write scope through the six-field delegation envelope.

## Core agents

| Agent | Sandbox | Purpose |
| --- | --- | --- |
| `researcher` | read-only | source verification, repository discovery, and factual framing |
| `architect` | read-only | design, interfaces, risks, rollback, and smallest viable plan |
| `api_guardian` | read-only | API, schema, CLI, config, and compatibility review |
| `builder` | workspace-write | single normal implementation writer |
| `validator` | read-only | structural, static, contract, and consistency validation |
| `tester` | workspace-write | executable checks and temporary test outputs |
| `scribe` | workspace-write | documentation and release artifacts after gates pass |
| `github_manager` | read-only | branch, PR, release, and repository-governance framing |

## Department agents

| Agent | Sandbox | Purpose |
| --- | --- | --- |
| `runtime_platform` | read-only | runtime defaults, toolchains, sandbox, and environment behavior |
| `workflow_design` | read-only | workflow procedures, skills, handoffs, prompts, reports, and state |
| `workspace_governance` | read-only | AGENTS layering, release law, branch policy, and repo rules |
| `quality_operations` | read-only | validation plans, installer checks, smoke paths, and eval-style checks |
| `docs_dx` | read-only | README, setup guidance, prompts, and developer experience |
| `ci_security_guardian` | workspace-write | GitHub Actions, CODEOWNERS, pinned actions, permissions, and repository protection |

Department agents are advisory by default. Even a writable role receives only a
frozen, isolated scope when the parent workflow explicitly needs it.

## Installed count and verification

- core agents: 8
- department agents: 6
- total packaged agents: 14

The installer updates the current 14 GodMode-owned manifest paths exactly while
leaving unrelated user-owned agent files alone. Verify the package and installed
runtime with:

```bash
./scripts/check-local-env.sh
./scripts/apply-global-codex-setup.sh --check
```

On Windows, use `./scripts/apply-global-codex-setup.ps1 --check` for the second
command.
