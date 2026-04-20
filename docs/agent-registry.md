# Agent Registry

Updated: 2026-04-16

This register is the current repo-level source of truth for the installed GodMode
agents. `Contract Office` should compare it against `.codex/agents/*.toml` during
governed runs.

| agent | toml_path | department | sandbox_mode | primary_ownership | triggers_when |
| --- | --- | --- | --- | --- | --- |
| `researcher` | [`.codex/agents/researcher.toml`](../.codex/agents/researcher.toml) | `Research Office` | `read-only` | repository analysis, source verification, and problem framing | source verification, repo discovery, or fact-finding is still needed |
| `architect` | [`.codex/agents/architect.toml`](../.codex/agents/architect.toml) | `Architecture Office` | `read-only` | smallest viable plan, interface shape, rollback, and dependency order | change shape, interface boundaries, or rollback risk are still unclear |
| `api_guardian` | [`.codex/agents/api_guardian.toml`](../.codex/agents/api_guardian.toml) | `Contract Office` | `read-only` | API, schema, CLI, config, and user-visible contract review | contracts, config surfaces, schemas, or user-visible outputs change |
| `builder` | [`.codex/agents/builder.toml`](../.codex/agents/builder.toml) | `Implementation Lane` | `workspace-write` | smallest safe implementation change | the task is clear and a bounded implementation is ready |
| `validator` | [`.codex/agents/validator.toml`](../.codex/agents/validator.toml) | `Quality Gate` | `read-only` | structural correctness, static checks, and repo consistency | a changed scope needs structural validation before closeout |
| `tester` | [`.codex/agents/tester.toml`](../.codex/agents/tester.toml) | `Quality Gate` | `workspace-write` | targeted execution, runtime verification, and reproduction checks | real commands, tests, or runtime verification must be executed |
| `scribe` | [`.codex/agents/scribe.toml`](../.codex/agents/scribe.toml) | `Release Office` | `workspace-write` | changelog text, final docs, and summary artifacts after green gates | implementation and required gates are complete |
| `github_manager` | [`.codex/agents/github_manager.toml`](../.codex/agents/github_manager.toml) | `Release Office` | `read-only` | branch, PR, release, and GitHub governance coordination | branch strategy, PR framing, or release/governance coordination is needed |
| `runtime_platform` | [`.codex/agents/runtime_platform.toml`](../.codex/agents/runtime_platform.toml) | `Runtime Platform` | `workspace-write` | `.codex/agents/**`, runtime defaults, and state/runtime scaffolding | runtime defaults, agent definitions, or state scaffolding change |
| `workflow_design` | [`.codex/agents/workflow_design.toml`](../.codex/agents/workflow_design.toml) | `Workflow Design` | `workspace-write` | `.agents/skills/**`, routing templates, and orchestration procedures | reusable workflow behavior, routing artifacts, or skill law changes |
| `workspace_governance` | [`.codex/agents/workspace_governance.toml`](../.codex/agents/workspace_governance.toml) | `Workspace Governance` | `workspace-write` | `AGENTS.md`, governance templates, and bootstrap constitutions | repo governance or governance template law changes |
| `quality_operations` | [`.codex/agents/quality_operations.toml`](../.codex/agents/quality_operations.toml) | `Quality & Operations` | `workspace-write` | `scripts/**`, readiness checks, and install/verify flow | local validation, readiness checks, or install/verify flow change |
| `docs_dx` | [`.codex/agents/docs_dx.toml`](../.codex/agents/docs_dx.toml) | `Docs & Developer Experience` | `workspace-write` | `README.md`, `docs/**`, and prompt surfaces | contributor docs, prompts, or maintainer guidance change |
| `ci_security_guardian` | [`.codex/agents/ci_security_guardian.toml`](../.codex/agents/ci_security_guardian.toml) | `Quality & Operations` | `workspace-write` | `.github/workflows/**`, `.github/CODEOWNERS`, `.github/dependabot.yml`, and GitHub security guidance | `.github/**`, CI/CD behavior, or repository-protection guidance change |
