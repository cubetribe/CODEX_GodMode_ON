# GodMode Core for Codex

GodMode Core is the free Community workflow package you install into your own
Codex setup. It helps Codex turn your task into a checked result. **Skills** provide
reusable procedures; **agents** take bounded specialist assignments when they
help. Your main chat owns the task and normally works alone.

## Choose your GodMode

| Product | Best fit | What it provides |
| --- | --- | --- |
| **GodMode Core for Codex** — this repository | You operate your own Codex setup | Self-installed skills, optional agents, verification procedures, and recoverable updates |
| [**GodMode Core for Claude Code**](https://github.com/cubetribe/ClaudeCode_GodMode-On) — currently CC_GodMode | You operate your own Claude Code setup | The separately maintained Claude workflow package, under its own license terms |
| [**GodMode Pro by Nerdsmiths**](https://godmode.nerdsmiths.de/) | You want an integrated application and assisted setup | A separate proprietary desktop application for project control, result review, maintained integrations, and scoped onboarding and support |

Core has no package subscription; your Codex or Claude access and usage remain
separate. Free availability does not change licensing or commercial permissions.
Pro has its own availability, pricing, and service terms; see the
[Nerdsmiths landing page](https://godmode.nerdsmiths.de/).
Read the [product-family guide](docs/product-family.md) for the agreed boundaries.

## Current package

The current package is **3.1.1**, with extended Help for local rules and settings.
See the [3.1.1 release document](docs/releases/3.1.1.md).
Installation is a separate step after downloading a release.

![GodMode Core: start, roles, and verified results](docs/assets/godmode-guide.svg)

## Start in 30 seconds

Open your project and a fresh Codex chat after installation. In the desktop
skill picker, type `/god`, select **GodMode Core Workflow**, and add your task.
This is skill search, not a built-in `/godmode` command. The portable text form:

```text
Use $godmode-workflow to add CSV export.
Context: the existing export screen.
Done when: the downloaded CSV opens with the expected columns.
Constraints: preserve the current JSON export.
```

Choose Debug for a failure, Review for assessment, or Prototype for a local
experiment. **GodMode Core Help** explains the choices and reviews local rules
when requested; **GodMode Core Update** checks
releases and installed files. With a clear task, work starts immediately.
Read the [German usage guide](docs/usage.md) for the explanation and examples.

Earlier installations may show **GodMode Workflow**, **GodMode Help**, and the
other previous display names. The Core display names ship in 3.1.1;
existing `$godmode-*` invocations remain compatible.

Updating Git does not update your global installation. Run the installer and
its check, then start a fresh chat. Removed roles still visible in the picker
are a reason to diagnose the installation, not to delete every custom agent.

## GodMode Core Help: usage and local rules

Select **GodMode Core Help** from the `/god` picker or invoke `$godmode-help`.
Use it to understand the modes, agent responsibilities, startup, or updates:

```text
Use $godmode-help to explain when I should choose Workflow, Debug, or Review.
```

Since 3.1.1, Help also reviews applicable local instructions and Codex settings:

```text
Use $godmode-help to review my local instructions and Codex settings.
Show concrete conflicts, outdated rules, and improvement suggestions with
file/line references. Do not edit files.
```

For this requested check, Help inspects relevant global/project `AGENTS.md`,
overrides and configured fallback files, plus applicable Codex settings and
selected profiles when observable. It distinguishes:

- conflicting rules and which instruction governs the inspected scope;
- settings or files demonstrably overridden, skipped, or unavailable;
- confirmed unsupported settings or missing required roles;
- optional simplifications with an explanation of their expected effect.

Each useful finding includes its source, effect, and smallest proposed remedy.
Current-best-practice or deprecation claims need relevant official sources;
missing evidence remains unresolved. Deliberate model choices, extra project
checks, stricter permissions, and user-owned roles are valid preferences.

Help performs a **read-only diagnosis** and preserves your settings. Ordinary
usage questions need no file scan. Unknown profiles, managed policy or launch
overrides limit the diagnosis; files on disk can differ from instructions
already loaded in a chat. A PATH CLI version is not automatically the running
desktop client's version. For installed-package drift or an actual update,
use `$godmode-update`. See the [German guide](docs/usage.md#eigene-regeln-und-einstellungen-prüfen).

## What 3.1.0 introduced

- concise help and understandable picker descriptions for each delivery mode;
- two small, separately loaded Help and Update skills (11 core skills total);
- a read-only audit of real files, duplicate skill roots, and published releases;
- version and source records so a checkout is distinguishable from an install;
- recoverable retirement of original 1.x variants and alternate-root old skills;
- prompt adjustments based on current Astra / Sol 6.1 documentation, while
  preserving user model choices and the seven-agent architecture.

See the [model and usage decision record](docs/research/godmode-3.1-model-and-usage-review-2026-10-03.md)
for sources and verification limits. We make no benchmark-proven optimality claim.
The historical [3.0 release document](docs/releases/3.0.0.md) records the Lean rebuild.

## Architecture retained from GodMode 3.0

- 7 optional custom agents instead of 14
- independently triggered core skills instead of companion chains
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

Models and reasoning effort are not pinned. GPT-6.1 Sol and GPT-6 Astra are
current choices when available; use the client default effort and increase it
when the task warrants it. The package remains model-neutral. See the linked
model review for official guidance and the absence of fresh live benchmarks.

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

For published installations, select an immutable tag from
[GitHub Releases](https://github.com/cubetribe/CODEX_GodMode_ON/releases).
For the current release:

```bash
git fetch origin --tags
git checkout v3.1.1
./scripts/apply-global-codex-setup.sh
./scripts/apply-global-codex-setup.sh --check
```

Windows:

```powershell
git fetch origin --tags
git checkout v3.1.1
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
Use `$godmode-help` for usage or local-rule diagnosis and `$godmode-update` for installation
maintenance. They are not delivery modes. Use `$godmode-paperwork` explicitly
for its separate document workflow.

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
python3 tests/test_godmode_audit.py -v
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

- [GodMode Core and Pro product family](docs/product-family.md)
- [GodMode usage and visual guide](docs/usage.md)
- [GodMode 3.1.1 release document](docs/releases/3.1.1.md)
- [GodMode 3.1.0 historical release document](docs/releases/3.1.0.md)
- [GodMode 3.0 historical release document](docs/releases/3.0.0.md)
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
