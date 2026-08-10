# AGENTS.md

## Repository contract

- This repository packages the global GodMode runtime for Codex.
- Work on the current branch; create or switch branches only when the user asks.
- Preserve unrelated work and keep diffs scoped.
- Use official OpenAI docs for version-sensitive claims; label inference.
- Package agents only under `templates/global-codex/agents/` and skills only
  under `templates/global-codex/skills/`; never duplicate them in repo-local
  discovery paths.
- Use `.agents/plugins/marketplace.json` and `plugins/` for optional, separately
  installed extensions. Core installers must never install them silently.
- Keep plugin manifests, bundled skills, schemas, tests, marketplace policy, and
  docs aligned. Sensitive-document plugins stay local-first, fail closed on
  integrity errors, and require explicit human gates for high-stakes conclusions.

## Source of truth

- This file governs repository implementation.
- `CHANGELOG.md` and `VERSION` govern release state.
- Deterministic scripts define what named checks prove.
- Agent TOML and skill files define their runtime behavior.
- Other docs are descriptive; conflicts with these sources are defects.

## Change contract

- Use one writer for overlapping tracked files, including required docs and
  `[Unreleased]`. Finish those edits before final gates; a later tracked edit
  invalidates affected evidence.
- Default to zero subagents; use only useful bounded specialists. Advisory
  roles are read-only; `tester` may create disposable output but not edit
  tracked source.
- Keep current, future, and historical behavior clearly separated in docs.
- Keep agents, skills, inventory, installers, checks, and public docs aligned
  when a runtime contract changes.

## Validation

- Static docs/config/metadata/contracts: `./scripts/check-static.sh`.
- Installer/runtime behavior: run the focused executable fixture.
- Plugin changes: run `python3 scripts/validate-codex-plugins.py --repo-root .`
  and the plugin's focused test suite; test isolated marketplace installation
  when CLI behavior changes.
- Migration, security, mixed contract/runtime, or release-critical work: run
  both static and executable gates.
- `./scripts/check-capabilities.sh` diagnoses the workstation; it is not a
  package gate.
- Windows PowerShell behavior is proven by Windows CI, not macOS.

## Release law

- Put every unreleased user-relevant prompt, skill, agent, template, script,
  config, or setup change under `CHANGELOG.md` `[Unreleased]`.
- `reports/generated/` is analysis and `state/` is resumable working memory;
  neither replaces the changelog.
- Classify impact as major, minor, patch, or none. Change `VERSION` or create a
  dated release section only during explicitly authorized release preparation.
- Commit, push, tag, publication, and deployment remain separate boundaries.

## Prototype package

- `$godmode-prototype` is an exclusive local-only mode.
- Keep its skill, overlay, docs, prompts, and checks aligned.
- Prototype output cannot ship directly; promotion starts a new production
  contract with risk-appropriate gates.

## Release impact

- Docs, structure, and example-only changes are usually `none`.
- New optional user-facing plugins are normally `minor`.
- Incompatible core installer or runtime changes are `major`.
