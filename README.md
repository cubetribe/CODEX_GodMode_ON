# Codex GodMode

GodMode is a lean, globally installable orchestration layer for Codex. It keeps
authority, worktree safety, one-writer delivery, recoverable migration, and
observable validation explicit without prescribing every reasoning step.

The current core release is **GodMode `3.0.0`**. It is a major rebuild for
strong parent models such as GPT-5.6 Sol: less standing context, fewer generic
roles, deliberate specialist selection, and more deterministic verification.
Read the comprehensive
[GodMode 3.0 release document](docs/releases/3.0.0.md) for the rationale,
breaking changes, measured package reductions, migration contract, rollback,
and release evidence.

## What changed in GodMode 3

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

The most important behavioral change is the default: the parent works alone.
It delegates only a bounded, independent uncertainty that materially improves
the result, and uses at most two specialists. A packaged specialist is selected
with its registered `agent_type`; a matching task name alone does not activate
the role.

### Why the system became smaller

GodMode 2.x protected useful invariants, but repeated them through 14 custom
agents, ten skills, a large workflow prompt, mandatory double validation, and a
post-gate Scribe. With a stronger orchestrator, those layers could duplicate
discovery, planning, implementation, and review while filling context and
multiplying child turns.

GodMode 3 keeps the rules that are hard or unsafe to infer—authority, one
writer, external-action boundaries, role selection, safe retirement, and
outcome evidence—and moves syntax, inventory, links, metadata, and migration
contracts into deterministic checks. Stack detail and special procedures load
only when their skills are relevant.

| Checked-in surface | 2.10 core | 3.0 core |
| --- | ---: | ---: |
| Custom agents | 14 | 7 |
| Agent-manifest source | 7,771 bytes | 3,400 bytes |
| Core skills | 10 | 9 |
| Global GodMode guidance | 4,502 bytes | 1,254 bytes |
| Core workflow skill | 4,824 bytes | 1,766 bytes |
| Packaged base concurrency cap | 6 | 2 |

These are UTF-8 source and inventory measurements, not tokenizer, quota,
latency, cost, or quality measurements. Real-world savings remain dependent on
the task, selected model, reasoning effort, tools, and whether delegation is
actually useful.

Models and reasoning effort are not pinned. GPT-5.6 Sol is the intended strong
orchestrator for demanding work, with Ultra useful when complexity justifies
its latency and token cost, but the package remains model-neutral.

## Optional Paperwork plugin

GodMode Paperwork remains an explicit opt-in plugin at its independent version
`2.10.0`. It provides immutable intake, native-first PDF extraction,
page-scoped local OCR, evidence anchors, bounded validation, human review gates,
and reproducible archives. It performs no network upload, silent dependency
installation, form submission, original deletion, or professional
certification.

The 3.0 core installers never install Paperwork, and existing Paperwork 2.10
cases require no 3.0 migration. Read the
[operator guide](./docs/godmode-paperwork.md) and
[research decision](./docs/research/godmode-paperwork-local-first-2026-07-11.md).

## Install locally

Requirements: Codex CLI `0.147.0+` and Bash on macOS/Linux or PowerShell 5.1+/7
on Windows. Repository validation additionally needs Git and Python 3.11+.

Use the immutable release tag for installation:

```bash
git fetch origin --tags
git checkout v3.0.0
./scripts/apply-global-codex-setup.sh
./scripts/apply-global-codex-setup.sh --check
```

Windows:

```powershell
git fetch origin --tags
git checkout v3.0.0
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

The package uses the current documented
`agents.max_concurrent_threads_per_session = 2` field. Codex CLI `0.147.0` is
the supported floor because its GPT-5.6 Sol spawn surface exposes the
`agent_type` needed to bind a packaged specialist; `0.144.x` can create a
generic Child with the requested task name instead. The exact compatibility
evidence lives in the [setup guide](docs/global-codex-setup.md). The
undocumented `max_depth` setting has been removed. No-recursive delegation is
a prompt contract, not a platform guarantee. Deterministic fixtures lint
routing; live model traces are separate release evidence.

## Repository map

| Path | Purpose |
| --- | --- |
| `AGENTS.md` | repository governance |
| `.codex/config.toml` | repo-local defaults without model pins |
| `templates/global-codex/` | global core guidance, config, agents, profiles, and skills |
| `templates/prototype-mode/` | disposable prototype overlay |
| `.agents/plugins/marketplace.json` | catalog for optional plugins |
| `plugins/godmode-paperwork/` | independently versioned optional local-first document plugin and tests |
| `scripts/check-static.sh` | deterministic core and plugin contract gate |
| `scripts/test-global-codex-setup.*` | cross-platform installer regressions |
| `docs/` | architecture, setup, operation, prompts, and research |
| `reports/` and `state/` | optional analysis and resumable state |

## Documentation

- [GodMode 3.0 official release document](docs/releases/3.0.0.md)
- [Architecture](docs/blueprint.md)
- [Agent registry](docs/agent-registry.md)
- [Global setup and recovery](docs/global-codex-setup.md)
- [Paperwork operator guide](docs/godmode-paperwork.md)
- [Local development](docs/local-development.md)
- [Prototype mode](docs/prototype-mode.md)
- [Lean research rationale](docs/research/godmode-3-lean-architecture-2026-08-09.md)
- [Roadmap](docs/roadmap.md)

Root `VERSION` tracks the core release. Optional plugins carry their own local
version contract. Commit, push, merge, tag, and publication remain separate
authority boundaries during development.
