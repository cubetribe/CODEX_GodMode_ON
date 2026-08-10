# Codex GodMode

GodMode is a small, globally installable orchestration layer for Codex. It
protects authority, worktree safety, one-writer delivery, and observable
validation without prescribing every reasoning step.

The repository release is `2.10.0`. The current `[Unreleased]` work is a
breaking **3.0 Lean candidate** and is not a published release yet.

## What changes in GodMode 3 Lean

- 7 optional custom agents instead of 14
- 9 independently triggered core skills instead of companion chains
- zero subagents by default, at most two selected specialists, and a packaged
  base-config thread cap of two
- parent or one built-in worker as the only tracked-file writer
- separate static `validator` and executable `tester` responsibilities
- risk-based gates instead of mandatory double validation
- safe retirement of exact GodMode 2.0 assets with verified backups
- separate package checks, installer tests, capability diagnostics, and routing
  evals

Models and reasoning effort are not pinned. GPT-5.6 Sol is the intended strong
orchestrator, with Ultra useful for genuinely complex work, but the package
remains model-neutral.

## Optional Paperwork plugin

GodMode Paperwork, released separately in 2.10, remains an explicit opt-in
plugin for controlled local document work. It provides immutable intake,
native-first PDF extraction, page-scoped local OCR, evidence anchors, bounded
validation, human review gates, and reproducible archives. It performs no
network upload, silent dependency installation, form submission, original
deletion, or professional certification.

The Lean core installers never install Paperwork. Read the
[operator guide](./docs/godmode-paperwork.md) and
[research decision](./docs/research/godmode-paperwork-local-first-2026-07-11.md).

## Install locally

Requirements: Codex CLI `0.144.1+` and Bash on macOS/Linux or PowerShell 5.1+/7
on Windows. Repository validation additionally needs Git and Python 3.11+.

```bash
./scripts/apply-global-codex-setup.sh
./scripts/apply-global-codex-setup.sh --check
```

Windows:

```powershell
.\scripts\apply-global-codex-setup.ps1
.\scripts\apply-global-codex-setup.ps1 -Check
```

The installers preserve custom or modified `$CODEX_HOME/config.toml` files
byte-for-byte. An exact rendered GodMode 2.0 base config is backed up and
migrated to the Lean base; use reset flags only for intentional replacement of
other user-owned config. Exact retired 2.0 assets are backed up and removed.
Modified or structurally unknown legacy assets stop the upgrade before any
package write with exit `5`.

### Install Paperwork explicitly

```bash
codex plugin marketplace add cubetribe/CODEX_GodMode_ON --ref v2.10.0
codex plugin add godmode-paperwork@codex-godmode-on
codex plugin list --json
```

Start a fresh Codex task, then invoke `$godmode-paperwork` explicitly. The plugin
reports missing Poppler, Tesseract, or language data but never installs them.

## Start a run

Start a fresh Codex task after core installation, then invoke one primary mode:

```text
Use $godmode-workflow to implement <goal>.
Done when: <observable result>.
Constraints: <material boundaries>.
```

Primary modes are exclusive:

| Mode | Use for |
| --- | --- |
| `$godmode-workflow` | non-trivial implementation and migration |
| `$godmode-debug` | reproduce, isolate, fix, and re-test |
| `$godmode-review` | read-only findings-first assessment |
| `$godmode-prototype` | disposable local-only exploration |

Support skills add only relevant knowledge: `greenfield-bootstrap`,
`release-manager`, `apple-platforms`, `web-platforms`, and `flutter-dart`.
Use `$godmode-paperwork` explicitly for its separate document workflow.

## Runtime model

The seven custom agents are narrow and optional:

| Agent | Boundary |
| --- | --- |
| `api_guardian` | compatibility contracts |
| `validator` | static structure and consistency |
| `tester` | executable behavior |
| `runtime_platform` | OS, sandbox, and toolchain uncertainty |
| `workflow_design` | orchestration and skill contracts |
| `docs_dx` | substantial public documentation |
| `ci_security_guardian` | CI and repository security review |

Default routing is no custom agent. Use at most two specialists for named
independent uncertainties. Advisory roles are read-only; `tester` may create
disposable output but never edit tracked source. Specialists do not delegate
again. The parent or one built-in worker writes.

## Validate this repository

```bash
./scripts/check-static.sh
./scripts/test-global-codex-setup.sh
./scripts/test-isolated-codex-runtime.sh
python3 -m unittest discover -s plugins/godmode-paperwork/tests -v
./scripts/check-capabilities.sh --full
```

`check-static` validates the core package and plugin manifests. Installer suites
prove migration behavior. The isolated runtime test installs into a temporary
home and verifies discovery plus profile parsing without touching the real user
setup. Paperwork has a focused offline unit suite. `check-capabilities` only
diagnoses the workstation.

## Configuration compatibility

The current Codex reference names
`agents.max_concurrent_threads_per_session`; `max_threads` is its legacy alias.
The package intentionally uses `max_threads = 2` because the desktop CLI
`0.147.0-alpha.1.2` accepts the new name while stable Homebrew Codex `0.144.1`
rejects it; both tested binaries accept the alias. The undocumented `max_depth`
setting has been removed. No-recursive delegation is a prompt contract, not a
platform guarantee. Deterministic fixtures lint routing; live model traces are
separate release evidence.

## Repository map

| Path | Purpose |
| --- | --- |
| `AGENTS.md` | repository governance |
| `.codex/config.toml` | repo-local defaults without model pins |
| `templates/global-codex/` | global core guidance, config, agents, profiles, and skills |
| `templates/prototype-mode/` | disposable prototype overlay |
| `.agents/plugins/marketplace.json` | catalog for optional plugins |
| `plugins/godmode-paperwork/` | optional local-first document plugin and tests |
| `scripts/check-static.sh` | deterministic core and plugin contract gate |
| `scripts/test-global-codex-setup.*` | cross-platform installer regressions |
| `docs/` | architecture, setup, operation, prompts, and research |
| `reports/` and `state/` | optional analysis and resumable state |

## Documentation

- [Architecture](docs/blueprint.md)
- [Agent registry](docs/agent-registry.md)
- [Global setup and recovery](docs/global-codex-setup.md)
- [Paperwork operator guide](docs/godmode-paperwork.md)
- [Local development](docs/local-development.md)
- [Prototype mode](docs/prototype-mode.md)
- [Lean research rationale](docs/research/godmode-3-lean-architecture-2026-08-09.md)
- [Roadmap](docs/roadmap.md)

`VERSION` changes only during explicitly authorized release preparation.
Commit, push, merge, tag, and publication are separate boundaries.
