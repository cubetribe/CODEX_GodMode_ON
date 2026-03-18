# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog.

## [Unreleased]

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
