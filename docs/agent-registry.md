# Agent Registry

This registry documents the packaged GodMode agents installed by `./scripts/apply-global-codex-setup.sh`.

Source files live under `templates/global-codex/agents/` so this bootstrap repository does not expose duplicate project-local agents after the same runtime is installed globally.

## Core agents

| Agent | Source | Purpose |
| --- | --- | --- |
| `researcher` | `templates/global-codex/agents/researcher.toml` | read-only source verification, repo discovery, and problem framing |
| `architect` | `templates/global-codex/agents/architect.toml` | read-only design, interfaces, risks, and smallest viable change plan |
| `api_guardian` | `templates/global-codex/agents/api_guardian.toml` | read-only API, schema, CLI, config, and contract-surface review |
| `builder` | `templates/global-codex/agents/builder.toml` | implementation-focused writer for the smallest safe change |
| `validator` | `templates/global-codex/agents/validator.toml` | read-heavy structural, static, and consistency validation |
| `tester` | `templates/global-codex/agents/tester.toml` | focused executable checks and runtime verification |
| `scribe` | `templates/global-codex/agents/scribe.toml` | docs, changelog, and release-note work after quality gates pass |
| `github_manager` | `templates/global-codex/agents/github_manager.toml` | branch, PR, release, and repository-governance framing |

## Department agents

| Agent | Source | Purpose |
| --- | --- | --- |
| `runtime_platform` | `templates/global-codex/agents/runtime_platform.toml` | runtime defaults, toolchains, sandboxing, and environment behavior |
| `workflow_design` | `templates/global-codex/agents/workflow_design.toml` | workflow procedures, skill boundaries, and handoff artifacts |
| `workspace_governance` | `templates/global-codex/agents/workspace_governance.toml` | AGENTS layering, release law, branch policy, and repo rules |
| `quality_operations` | `templates/global-codex/agents/quality_operations.toml` | validation plans, install checks, smoke paths, and eval-oriented checks |
| `docs_dx` | `templates/global-codex/agents/docs_dx.toml` | README, setup docs, prompts, and contributor-facing clarity |
| `ci_security_guardian` | `templates/global-codex/agents/ci_security_guardian.toml` | GitHub Actions, CODEOWNERS, pinned actions, and repository security posture |

## Installed count

- Core agents: 8
- Department agents: 6
- Total packaged agents: 14

Run `./scripts/check-local-env.sh` to verify the package sources and `./scripts/apply-global-codex-setup.sh --check` to verify the installed global runtime.
