# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog.

## [Unreleased]

## [1.1.0] - 2026-05-12

### Added

- `$godmode-prototype` skill — a local-only fast lane for rapid prototyping with minimal governance, no security review, and maximum iteration speed; all output is watermarked `PROTOTYPE ONLY` and ships with a migration checklist
- `templates/prototype-mode/AGENTS.md` — minimal governance overlay to drop into any `prototype/` or `spike/` workspace
- `templates/prototype-mode/config.toml` — lean Codex config for prototype sessions that keeps the model user-defined while setting `model_reasoning_effort = "high"`, `approval_policy = "never"`, and `max_threads = 2`
- `docs/prototype-mode.md` — reference guide covering the prototype loop, watermark format, file naming rules, migration checklist, and relationship to the rest of the skill family
- `docs/prompts/prototype-start-prompt.md` — copy-paste start prompt for prototype sessions, including a production-promotion prompt template
- GitHub Sponsors funding configuration so the repository can show a Sponsor button.

### Changed

- pinned every packaged GodMode agent to `model = "gpt-5.5"` and `model_reasoning_effort = "high"`
- expanded local validation to reject packaged agents or config profiles that drift below `gpt-5.5` or below `high` reasoning

## [1.0.0] - 2026-05-08

### Added

- companion GodMode skills for debug, review, department routing, and greenfield bootstrap workflows
- optional department custom agents for runtime, workflow, governance, quality, docs, and CI/security advisory lanes
- `ci_security_guardian`, a GitHub security and CI department agent for Actions, CODEOWNERS, pinned workflows, and repository security posture
- baseline `CODEOWNERS`, Dependabot for GitHub Actions, and pinned CodeQL/CI workflow coverage
- Windows PowerShell global installer path and matching `-Check` verification command
- `docs/agent-registry.md`, an auditable register of the installed GodMode agents
- department orchestration, project bootstrap, report, and workflow-state templates
- expanded release documentation for install, upgrade, workflow routing, validation, and maintainer release prep

### Changed

- refreshed the GodMode workflow guidance against current Codex subagent, skills, AGENTS layering, and agent-eval guidance
- updated the global Codex default model from `gpt-5.4` to `gpt-5.5`
- expanded local and global setup checks to cover the shipped companion skills, department agents, package sources, and CI workflow security
- moved packaged agents and skills out of repo-local Codex discovery paths to prevent duplicate project and personal entries after global installation
- split Codex app and CLI slash-command guidance in the public docs
- promoted the documented runtime from the 0.2 bootstrap line to a 1.0 release-ready package

### Fixed

- made the local environment check robust against `flutter --version` broken-pipe behavior under `pipefail`
- prevented the bootstrap repo from exposing duplicate `CODEX_GodMode_ON` project skills after the same runtime is installed globally

### Upgrade notes

- Run `./scripts/apply-global-codex-setup.sh` or `.\scripts\apply-global-codex-setup.ps1` after updating to install the new skills, optional department agents, and `gpt-5.5` default.
- Run `./scripts/apply-global-codex-setup.sh --check` or `.\scripts\apply-global-codex-setup.ps1 -Check` to verify the user-level runtime after installation.

## [0.2.1] - 2026-03-19

### Added

- stack-specific starter prompts for `web`, `apple`, and `flutter`

### Changed

- surfaced the stack-specific starters directly in the README for copy-paste use
- expanded the README with explicit usage guidance for `$` skill mentions, `/` slash commands, and agent usage
- expanded repo validation to cover the new prompt files

## [0.2.0] - 2026-03-19

### Added

- true global installation of the GodMode agents into `~/.codex/agents/`
- true global installation of the GodMode skills into `~/.agents/skills/`
- end-to-end installer checks for the installed agent and skill runtime

### Changed

- rewrote the public prompts so they target the installed global workflow instead of a repo-local workflow
- made the public starter prompts explicitly invoke `$godmode-workflow` for more reliable activation
- repositioned the repository as the bootstrap and reference repo for a one-time global install
- updated the global guidance to inspect the current workspace first and treat repo-local assets as optional overrides

## [0.1.3] - 2026-03-18

### Changed

- moved the repository back to a `main`-first delivery model
- rewrote the public entry documents in English
- moved the explanation and copy-paste starter prompts to the top of the README

## [0.1.2] - 2026-03-17

### Added

- ultra-short start prompt for `GODMODE REVIEW`

### Changed

- surfaced all three starter prompts directly in the README for copy-paste use

## [0.1.1] - 2026-03-16

### Added

- ultra-short start prompts for `GODMODE DEV` and `GODMODE DEBUG`
- reproducible global Codex templates under `templates/global-codex/`
- idempotent `scripts/apply-global-codex-setup.sh` for installing the documented Mac setup
- stack-oriented Codex profiles for `swiftui`, `web`, `flutter`, and `review`

### Changed

- surfaced both starter prompts directly in the README for copy-paste use
- documented the global profile workflow and local apply/check flow in the setup guides
- expanded local environment verification to cover the new template and apply-script assets

## [0.1.0] - 2026-03-16

### Added

- initial repository bootstrap
- first documentation for layered Codex configuration
- repo-level `AGENTS.md` and `.codex/config.toml`
- first example skill in `.agents/skills/`
- community health files and friendlier contribution entry points
- issue forms and discussion forms for GitHub collaboration
- repository security policy
- first local runtime scaffolding for `.codex/agents/`
- stack-specific skills for Apple platforms, web/backend, and Flutter/Dart
- local environment verification script
- local development guide plus `reports/` and `state/` structure

### Changed

- repositioned the repository around the Codex GodMode blueprint
- added a documented architecture and workflow blueprint for the port from `ClaudeCode_GodMode-On`
- clarified the distinction between `.codex/agents/*.toml` and `.agents/skills/`
- replaced placeholder roadmap and hook notes with implementation-oriented guidance
