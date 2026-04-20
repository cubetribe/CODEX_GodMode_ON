# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog.

## [Unreleased]

### Added

- `greenfield-bootstrap`, a new skill plus starter prompt and project-bootstrap template for creating repo-local governance before parallel implementation starts
- `godmode-debug` and `godmode-review`, two focused workflow-companion skills for bug work and findings-first assessment
- a maintainer-focused improvement-sprint prompt under `docs/prompts/improvement-sprint-prompt.md`
- `ci_security_guardian`, a new GitHub security and CI department agent, plus baseline `CODEOWNERS` and pinned GitHub Actions CI coverage
- GitHub Dependabot updates for Actions plus a pinned CodeQL workflow for repository security scanning
- `docs/agent-registry.md`, a machine-readable register of the installed GodMode agents
- a research brief for the next post-merge decision about whether GodMode should stay as one primary skill or split into several narrower workflow skills

### Changed

- updated `release-manager` so it discovers the repo's release law before deciding how changelog, version, or fragment files should be handled
- updated the starter prompts to require governance preflight and to surface release, versioning, and policy constraints as explicit task inputs
- codified changelog law and validation law in `AGENTS.md`
- expanded `scripts/check-local-env.sh` to validate agent contracts, skill frontmatter, changelog and version alignment, shell syntax, and CI-mode repo checks
- hardened local and CI validation so GitHub workflow security rules are checked for pinned actions, explicit permissions, and disallowed `pull_request_target`
- aligned `README.md`, `docs/blueprint.md`, `docs/department-orchestration.md`, `docs/local-development.md`, and `docs/roadmap.md` with the current department-agent runtime and guardrail model
- simplified the documented entry surface toward a skill-first model where `$godmode-workflow` is primary and prompt files are optional examples rather than the main runtime interface
- aligned the GodMode prompt examples around a minimal skill-first format and documented `departments`, `debug`, and `review` as focused companion lanes

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
