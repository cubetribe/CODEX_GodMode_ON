# Global Codex Setup

Published core version: `3.0.0`. See the
[official release document](./releases/3.0.0.md) for the full rationale,
breaking changes, migration contract, rollback, and evidence boundaries.
GodMode Paperwork remains separately versioned at `2.10.0`.

## Requirements

- Codex CLI `0.147.0` or newer
- Bash on macOS/Linux, or Windows PowerShell 5.1/PowerShell 7
- Git and Python 3.11+ for repository validation

Confirm which CLI will run:

```bash
type -a codex
codex --version
```

The installer checks the resolved binary and `codex help doctor` before any
target write. Override it with `CODEX_BIN=/absolute/path/to/codex` when needed.

## Install the Lean core

For a released installation, check out the immutable tag first:

```bash
git fetch origin --tags
git checkout v3.0.0
```

macOS/Linux:

```bash
./scripts/apply-global-codex-setup.sh
./scripts/apply-global-codex-setup.sh --check
```

Windows:

```powershell
.\scripts\apply-global-codex-setup.ps1
.\scripts\apply-global-codex-setup.ps1 -Check
```

Installed surfaces:

| Source | Default target |
| --- | --- |
| managed global guidance | `$CODEX_HOME/AGENTS.md` |
| seven custom agents | `$CODEX_HOME/agents/*.toml` |
| base config | `$CODEX_HOME/config.toml` on a fresh install |
| four profiles | `$CODEX_HOME/godmode-*.config.toml` |
| inventory | `$CODEX_HOME/godmode/managed-assets.tsv` |
| nine core skills | `~/.agents/skills/<name>/` |

Start a fresh Codex task after installation so discovery is rebuilt.

## Install the optional Paperwork plugin

Paperwork is distributed separately and is never copied by the core installer:

```bash
codex plugin marketplace add cubetribe/CODEX_GodMode_ON --ref v2.10.0
codex plugin add godmode-paperwork@codex-godmode-on
codex plugin list --json
```

Start a fresh task and invoke `$godmode-paperwork` explicitly. Run its `doctor`
command before case intake. It reports missing Poppler, Tesseract, or language
data but never installs them. Keep cases and exports outside Git worktrees and
plugin caches. Its manifest is governed by
`plugins/godmode-paperwork/VERSION`, not the root core version. See
[GodMode Paperwork](./godmode-paperwork.md).

## Existing user configuration

A custom or modified existing `config.toml` is preserved byte-for-byte,
including user model, reasoning, provider, MCP, plugin, and project settings.
If it lacks the current project trust entry, the installer warns but does not
merge TOML. One exception is an exact rendered GodMode 2.0 base config without a
trust entry or with the sole generated trust entry matching the current
`--repo` source: it is backed up and migrated to the Lean base so the old
six-thread cap, `max_depth`, and bundled Playwright servers do not survive an
otherwise exact upgrade. A different trust entry counts as a user modification
and is preserved.

Use this only when replacement is intentional:

```bash
./scripts/apply-global-codex-setup.sh --reset-config
```

The PowerShell spelling is also `--reset-config`. Conflicting managed profile
files stop with exit `4` unless that option is supplied. `--reset-agents`
similarly replaces the whole global `AGENTS.md`; normal installation updates
only the marked GodMode block and preserves surrounding user guidance.

## 2.0 to 3.0 retirement migration

The managed inventory records seven retired agents and the retired
`godmode-departments` skill with their normalized 2.0 SHA-256 digests.

Before any package mutation, the installer classifies every present retired
path:

- absent: continue;
- exact known 2.0 file, including CRLF-normalized text: eligible for migration;
- modified file, symlink, wrong type, or skill directory with extra content:
  stop with exit `5` and write nothing.

Eligible paths are copied to a unique archive, verified again, then removed
from live discovery. Custom names not listed in the inventory are untouched.
The installed inventory is written last, after current agents and skills.

Backups live under:

```text
$CODEX_HOME/backups/install-archives/<timestamp-run-id>/
```

Retired assets are under `retired/agents/` and `retired/skills/`. Config,
profile, AGENTS, and ordinary managed replacements have their own subfolders.

To restore, stop Codex, copy the desired archived item back to its original
path, and start a fresh task. A restored retired item intentionally makes the
3.0 `--check` fail until it is removed or the 2.0 runtime is fully restored.

## Configuration contract

The base config sets workspace-write sandboxing, approval on request, cached web
search, no sandbox network, and an agent concurrency cap of two. It does not pin
a model, effort, MCP server, plugin, or integration.

When a parent selects one of the seven packaged specialists, it must pass the
matching `agent_type`. A matching `task_name` alone creates a generic child and
does not load the custom manifest.

The package uses the current documented
`max_concurrent_threads_per_session = 2` field. The stable supported floor is
Codex CLI `0.147.0`: its GPT-5.6 Sol V2 spawn contract exposes `agent_type`, so
the parent can select a packaged custom agent. The tested `0.144.x` contract
omitted that field; a matching `task_name` only named a generic Child and did
not load the role manifest. The package removed `max_depth`; recursive
delegation is prohibited by the routing contract but not claimed as a
config-enforced guarantee.

Profiles are separate `$CODEX_HOME/NAME.config.toml` files:

```bash
codex --profile godmode-web
codex --profile godmode-swiftui
codex --profile godmode-flutter
codex --profile godmode-review
```

Profiles remain model-neutral.

## Verification and diagnostics

`--check` verifies exact managed core assets, the managed AGENTS block, profiles,
inventory, skill directories, absence of retired paths, and absence of backup
artifacts inside live discovery roots.

Repository-side checks are separate:

```bash
./scripts/check-static.sh
./scripts/test-global-codex-setup.sh
./scripts/test-isolated-codex-runtime.sh
python3 -m unittest discover -s plugins/godmode-paperwork/tests -v
./scripts/check-capabilities.sh --full
```

The isolated runtime test creates a temporary `HOME` and `CODEX_HOME`, installs
there, renders model-visible prompt input, checks nine-skill discovery, rejects
the retired skill, and parses the review profile. It does not mutate the real
user setup or call a model. The static gate also validates the optional plugin
manifest; Paperwork behavior is covered by its focused offline unit suite.

PowerShell 5.1 and 7 jobs are configured in Windows CI and are required on the
exact release pull-request head. A macOS run does not claim Windows coverage.

Live multi-agent release traces against stable CLI `0.147.0` use a persistent,
isolated temporary Codex home rather than `--ephemeral`. The public JSONL stream
is not treated as the sole Child-lifecycle record, so role selection and
commands are verified from the persisted parent/child session graph and Child
rollout. Final self-report text alone is never a pass condition.

## Exit codes

| Code | Meaning |
| ---: | --- |
| `0` | install or exact check passed |
| `1` | validation/check failure |
| `2` | invalid arguments |
| `3` | missing or incompatible Codex CLI |
| `4` | conflicting managed profile without reset authority |
| `5` | unsafe retirement or managed-inventory conflict |
