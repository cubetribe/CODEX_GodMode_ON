# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog.

## [Unreleased]

### Added

- a managed asset inventory and immutable 1.1/2.0 fixtures for recoverable runtime migrations
- safe retirement of exact legacy GodMode assets with normalized SHA-256 verification, unique backups, no-write conflict exit `5`, CRLF coverage, and preservation of unrelated custom agents and skills
- deterministic `check-static`, separate capability diagnostics, five routing fixtures, and a multi-binary-capable isolated discovery/profile test that never touches the real user home
- a tracked research decision record covering official OpenAI guidance, empirical AGENTS.md studies, community signals, and local compatibility evidence

### Changed

- rebuilt the runtime as the major-impact GodMode 3 Lean candidate: zero subagents by default, at most two selected specialists, a packaged-base thread cap of two, no recursive specialist delegation, and parent or one built-in worker as the sole tracked-file writer
- reduced the packaged roster from 14 custom agents to seven narrow optional specialists and made every specialist except the runtime-only `tester` read-only
- separated `validator` ownership of static structure from `tester` ownership of executable behavior and made gate selection proportional to scope and risk
- made workflow, debug, review, and prototype independent primary modes instead of companion chains
- kept the managed global `AGENTS.md` below 1,500 bytes and the core workflow skill below 2,000 bytes, moving stack detail and specialized procedures into progressively loaded skills
- split the old aggregate environment check into a compatibility dispatcher, a deterministic package gate, explicit installer suites, and workstation-only diagnostics
- raised the installer minimum to the locally verified Codex CLI `0.144.1` and retained the compatible `max_threads = 2` alias because stable `0.144.1` rejects the newer documented field while both locally tested CLIs accept the alias
- made exact rendered GodMode 2.0 configs without trust or with the current source repository's generated trust entry recoverably migrate to the Lean base while preserving every modified or custom config byte-for-byte
- rewrote the README, architecture, registry, setup, development, prototype, roadmap, prompts, reports, and state guidance around one normative Lean contract
- limited workflow state to long, paused, or handed-off runs and expanded its template with revision, authority, writer, scope, done criteria, and evidence

### Fixed

- made the Windows dangling-link regression create and then remove its temporary target so Windows PowerShell 5.1 reaches the intended installer no-write assertion

### Removed

- custom agents `researcher`, `architect`, `builder`, `scribe`, `github_manager`, `workspace_governance`, and `quality_operations`
- the `godmode-departments` skill, department orchestration guide, historical improvement-sprint prompt, and department/report handoff templates
- undocumented `agents.max_depth`, bundled Playwright MCP servers, and the managed Playwright output directory from the portable base config
- mandatory validator/tester double gates and the post-validation writing Scribe phase

### Breaking changes

- a normal upgrade removes hash-matched GodMode 2.0 retired agents and `godmode-departments` from live discovery after verified backup; modified or structurally unknown copies must be resolved manually
- automation and documentation that reference the seven retired agent names, the department skill, mandatory double gates, or Playwright MCP defaults must migrate to the Lean routing contract
- Codex CLI versions older than `0.144.1` are no longer supported by the installers

### Upgrade notes

- Run the platform installer normally. Do not use reset flags unless replacement of user-owned config or the full managed AGENTS file is intentional.
- An exact rendered 2.0 package config is backed up and migrated automatically; any modified or custom config remains user-owned and unchanged.
- If installation exits `5`, inspect the named legacy path. The installer has not changed package targets; preserve or rename user-modified content before retrying.
- Backups are stored under `$CODEX_HOME/backups/install-archives/<run-id>/`, with retired files under `retired/agents/` and `retired/skills/`.
- Start a fresh Codex task after a successful install, then run `--check`. The repository's isolated runtime script can verify discovery without modifying the real home.
- `VERSION` remains `2.10.0`; a dated `3.0.0` section, version bump, tag, and publication require a separate authorized release-preparation step after all final gates pass.

## [2.10.0] - 2026-07-11

### Added

- optional `godmode-paperwork` Codex plugin, distributed through the repository marketplace and invoked explicitly as `$godmode-paperwork`
- offline Python 3.11+ CLI for capability inspection, immutable intake, native extraction, page-scoped OCR routing, controlled CASEWORK records, validation, verification, and reproducible packaging
- content-addressed originals, canonical records, SHA-256 deduplication, base-name-only source aliases without absolute paths, strict case paths, case locks, and a hash-chained internal audit
- native-first Poppler extraction and local Tesseract escalation with retained TXT, TSV, and hOCR artifacts, deterministic quality thresholds, and executable/language-data provenance
- evidence claims with exact quotes, artifact hashes, route binding, and OCR bounding boxes derived from unique contiguous TSV word sequences
- bounded requirements for required records, equality, exact fixed-point decimal sums, date ordering, formats, and uniqueness without dynamic evaluation
- scoped human approvals bound to the current claim or page digest, plus a separate declared-human release gate for review-bearing archives
- deterministic uncompressed tar packs with normalized metadata, exact manifests, canonical receipts, SHA-256 sidecars, and independent safe verification
- operator guide, architecture decision, regulatory research notes, schemas, plugin metadata, marketplace validation, and focused CI coverage

### Changed

- documented the runtime as 14 core agents, 10 core skills, and one separately installed optional plugin
- extended repository governance, CODEOWNERS, security guidance, contribution rules, local validation, and Markdown lint coverage to plugin surfaces
- kept the global GodMode installer and core templates unchanged so Paperwork does not silently expand existing installations

### Security

- fail closed on linked or escaping paths, unsafe or non-normalized source aliases, unexpected case files, original or artifact tampering, audit truncation, stale validation, malformed Unicode, non-finite or overlong decimals, OCR coordinate mismatch, archive traversal, trailing archive payloads, receipt forgery, partial publication, and visual-review escalation bypass
- roll back governed state and newly created artifacts when intake, extraction, OCR routing, casework, or validation aborts partway through
- bind packing to the validated per-file state snapshot; verify exact canonical archive bytes and the complete materialized case through safe single-open snapshots; reject missing state, appended payloads, path replacement, and malformed review gates
- restrict OCR outputs to mode `0600` and work directories to `0700` on the supported Unix-like runtime before recording or hashing them
- map expected filesystem and permission failures to controlled integrity or processing exits without leaking sensitive paths
- invalidate validation after every governed mutation and reject reused human approvals after the approved scope changes
- perform no network access, cloud OCR, silent tool installation, document upload, form submission, original deletion, or paper-destruction action
- record external OCR binaries and language data as an explicit trust boundary rather than treating local installation as proof of safety

### Upgrade notes

- Add the released marketplace with `codex plugin marketplace add cubetribe/CODEX_GodMode_ON --ref v2.10.0`, then install `godmode-paperwork@codex-godmode-on` explicitly.
- Start a fresh Codex task and invoke `$godmode-paperwork`; implicit invocation is disabled.
- Run `doctor` before case intake. The plugin reports missing Poppler, Tesseract, or language data but never installs them.
- Keep every case and export outside Git worktrees and plugin caches. On macOS, use `/private/tmp` rather than `/tmp` only for disposable synthetic tests.
- `PASS` describes a configured mechanical gate, not legal, tax, compliance, authenticity, or professional certification.

## [2.0.0] - 2026-07-10

### Added

- four Codex `0.134.0+` profile files — `godmode-swiftui`, `godmode-web`, `godmode-flutter`, and `godmode-review` — installed as separate `$CODEX_HOME/*.config.toml` files
- capability-aware installer preflight for Codex CLI `0.134.0` or newer, including version and `codex doctor` support checks
- exact managed-asset verification for global agents, skills, profiles, and the managed `AGENTS.md` block
- cross-platform installer regression suites, with Windows PowerShell 5.1 and PowerShell 7 coverage enforced in CI
- OpenAI UI metadata for `$godmode-workflow`
- an outcome-evidence gate that maps each done criterion to an observed command result, artifact, or user-visible behavior

### Changed

- rebuilt `$godmode-workflow` around governance and capability preflight, bounded parallel discovery, synthesis and contract freeze, one implementation writer, independent validation, outcome evidence, and release handoff
- let every packaged agent inherit the parent session model and reasoning level; GPT-5.6 is recommended for demanding work when the account supports it, with Ultra as an opt-in for complex multi-agent runs
- allowed bounded proactive read-only delegation when the user, project guidance, or an active skill authorizes it, using a six-field delegation envelope and a single normal writer
- made `/plan` followed by optional `/goal` the documented native path for long-running work
- required prototype mode to exercise the promised behavior end to end instead of treating file creation or process startup as completion
- made installer backups unique per run and kept backup artifacts outside live Codex discovery roots

### Fixed

- preserved an existing user `config.toml` byte-for-byte instead of replacing it with package defaults, preventing loss of model, reasoning, provider, MCP, plugin, and project settings while leaving complex TOML syntax untouched
- preserved user guidance outside exactly one ordered GodMode marker pair in global `AGENTS.md`, migrated the known v1.1 template without duplication, and rejected malformed markers before any write
- detected and repaired exact skill-directory drift instead of checking skill names only
- rejected conflicting managed profiles before mutation unless the user explicitly requests `--reset-config`
- diagnosed stale or shadowed Codex executables before installation instead of reporting a misleading activation success

### Removed

- packaged GPT-5.5 and fixed reasoning-effort pins from the repo config, global config, profiles, and all 14 agent manifests
- legacy inline `[profiles.*]` installation
- stale `/plan-mode` guidance and the claim that subagents only run after a direct user request

### Breaking changes

- existing user config is no longer replaced by package defaults; it stays byte-for-byte unchanged unless `--reset-config` is explicitly selected
- profile invocation changes from legacy inline names such as `web` to separate namespaced files such as `codex --profile godmode-web`
- delegated agents no longer force GPT-5.5/high and instead inherit the parent session's selected model and reasoning level

### Upgrade notes

- Install Codex CLI `0.134.0` or newer, confirm the executable with `type -a codex` and `codex --version`, then rerun the platform installer.
- The installer leaves an existing `config.toml` unchanged. Use `--reset-config` only when you intentionally want the bundled base config and managed profiles to replace conflicting managed files.
- Start a fresh Codex task after installation so the updated global guidance, agents, skills, and profiles are reloaded.
- Thanks to [@BSG2000](https://github.com/BSG2000) for reporting and contributing toward safe preservation of user-owned installer configuration.

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
