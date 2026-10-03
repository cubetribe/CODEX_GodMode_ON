# Global Codex Setup

Core version: `3.1.0`. See [3.1 release document](releases/3.1.0.md) and the
[usage guide](usage.md). The following tag example installs 3.1. See the historical
[official release document](./releases/3.0.0.md) for the full rationale,
breaking changes, migration contract, rollback, and evidence boundaries.
GodMode Paperwork remains separately versioned at `2.10.0`.

## Requirements

- Codex CLI `0.147.0` or newer
- Bash on macOS/Linux, or Windows PowerShell 5.1/PowerShell 7
- Git and Python 3.11+ for repository validation
- Python 3.11+ for the read-only Update audit; the core installers do not need Python

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
git checkout v3.1.0
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
| installation version and locators | `$CODEX_HOME/godmode/{VERSION,source-repo.txt,user-skills-home.txt}` |
| eleven core skills | `~/.agents/skills/<name>/` |

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

## Retirement and installation ownership

The managed inventory records seven retired agents and the retired
`godmode-departments` skill with normalized 2.0 SHA-256 digests. The cumulative
`legacy-hashes.tsv` ledger additionally records immutable 1.0/1.1 originals;
2.10 uses the accepted 2.0 retired core variants. Both the selected user skill
root and `$CODEX_HOME/skills` are inspected.

Before any package mutation, the installer classifies every present retired
path:

- absent: continue;
- exact known released file, including CRLF-normalized text: eligible for migration;
- modified file, symlink, wrong type, or skill directory with extra content:
  stop with exit `5` and write nothing.

Eligible paths are copied to a unique archive, verified again, then removed
from live discovery. Custom names not listed in the inventory are untouched.
Active managed agent and skill names retain the existing backup-and-replace
contract, including extra content in those managed directories. Active copies
in the alternate skill root are conflicts and must be deliberately resolved
first. User config remains preserved. Custom backup names are not moved by
the package's legacy-backup cleanup.

After assets are installed, the installer writes inventory and locator records
and runs its exact check. Records are diagnostic, not proof of file ownership.
Future removals must keep cumulative retired entries with immutable hashes;
never infer deletion authority from an old installed inventory or receipt.

Backups live under:

```text
$CODEX_HOME/backups/install-archives/<timestamp-run-id>/
```

Retired assets are under `retired/agents/`, `retired/skills/`, and
`retired/legacy-skills/` (alternate-root copies). Config,
profile, AGENTS, and ordinary managed replacements have their own subfolders.

To restore, stop Codex, copy the desired archived item back to its original
path, and start a fresh task. A restored retired item intentionally makes the
current `--check` fail until it is removed or the older runtime is fully restored.

## Diagnose or update

Select `$godmode-update` or run the bundled Python helper from this checkout:

```bash
python3 templates/global-codex/skills/godmode-update/scripts/audit.py --repo . --github
```

Use `--codex-home PATH` and `--user-skills-home PATH` for non-default targets.
After 3.1 installation the helper can find the source and skills root from
the locator files. It reports installed, checkout, and latest public stable
release versions separately; GitHub failure is unknown, not up to date. The
helper is read-only and never downloads or executes a release. It also checks
actual content, retired config declarations, and both global skill roots. Exit
0 means the audited installation is exact and any requested release lookup
completed; 1 means findings or unknown release lookup; 2 means invalid input or
missing source. It does not compare project-local/plugin/other-host discovery.

Choose the intended immutable release or explicitly selected local candidate,
inspect its source and dirty state, run its normal platform installer, then
`--check` / `-Check` and the audit again. For an old installation without the
new Update skill, this checkout helper provides the bootstrap diagnosis.
Start a fresh chat after successful installation and verify the skill picker.

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
inventory, version/locator records, skill directories, absence of retired paths,
active alternate-root duplicates, and known managed backup artifacts inside
live discovery roots. User config content is outside this exact file check;
the audit separately reports retired role declarations there.

Repository-side checks are separate:

```bash
./scripts/check-static.sh
./scripts/test-global-codex-setup.sh
python3 tests/test_godmode_audit.py -v
./scripts/test-isolated-codex-runtime.sh
python3 -m unittest discover -s plugins/godmode-paperwork/tests -v
./scripts/check-capabilities.sh --full
```

The isolated runtime test creates a temporary `HOME` and `CODEX_HOME`, installs
there, renders model-visible prompt input, checks eleven-skill discovery, rejects
the retired skill, and parses the review profile. It does not mutate the real
user setup or call a model. The static gate also validates the optional plugin
manifest; Paperwork behavior is covered by its focused offline unit suite.
If PATH points to an unsupported old binary, select the verified current one
with `test-isolated-codex-runtime.sh --codex-bin /absolute/path/to/codex`; the
script's automatic candidate list is diagnostic and does not bypass its floor.

PowerShell 5.1 and 7 jobs are configured in Windows CI and are required on the
exact release pull-request head. A macOS run does not claim Windows coverage.

Historical 3.0 live multi-agent release traces against stable CLI `0.147.0` used a persistent,
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
| `5` | unsafe retirement, alternate-root conflict, linked discovery root, or installation-record conflict |
