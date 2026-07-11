# Global Codex Setup

Updated: 2026-07-11

Runtime version: 2.10.0

This guide installs the GodMode runtime once at user level so its agents,
skills, profiles, and guidance are available from any workspace.

Version 2.10 also publishes an optional `godmode-paperwork` plugin. It is not
part of the global core installer and must be selected explicitly.

## Requirements

- Codex CLI `0.134.0` or newer
- `codex help doctor` support in the resolved executable
- Git and a local checkout of this repository
- Bash on macOS/Linux, or Windows PowerShell 5.1/PowerShell 7 on Windows

GPT-5.6 is a model family, not a Codex CLI version. Select it in the parent
session when your account supports it and the task warrants it. Packaged agents
inherit that selection; the installer does not hard-code model entitlements or
reasoning effort. Ultra is an opt-in for complex multi-agent work.

## Diagnose Codex before installation

On macOS or Linux:

```bash
type -a codex
codex --version
codex help doctor
codex doctor
```

`type -a` matters: an obsolete executable earlier on `PATH` can make a current
desktop installation appear broken. The installer rejects a missing,
incompatible, or capability-incomplete CLI before writing any target file.

On Windows:

```powershell
Get-Command codex -All
codex --version
codex help doctor
codex doctor
```

Codex can update itself on supported installations:

```bash
codex update
```

The GodMode installer never updates Codex silently. You can point it at a
specific compatible binary for diagnosis or installation:

```bash
CODEX_BIN=/absolute/path/to/codex ./scripts/apply-global-codex-setup.sh --check
```

```powershell
$env:CODEX_BIN = 'C:\absolute\path\to\codex.exe'
.\scripts\apply-global-codex-setup.ps1 --check
```

### macOS Homebrew formula shadowing

Older machines may still resolve the obsolete Homebrew formula named `codex`
instead of the current cask. If `brew list --formula codex` and `type -a codex`
confirm that case, replace it deliberately:

```bash
brew uninstall --formula codex
brew install --cask codex
hash -r
type -a codex
codex --version
codex doctor
```

Do not uninstall a working package merely because these commands are shown;
first confirm which executable your shell is actually resolving.

## Install

From the repository root on macOS or Linux:

```bash
./scripts/apply-global-codex-setup.sh
./scripts/apply-global-codex-setup.sh --check
```

On Windows:

```powershell
.\scripts\apply-global-codex-setup.ps1
.\scripts\apply-global-codex-setup.ps1 --check
```

Then run `codex doctor` and start a fresh Codex task. Existing tasks do not
rebuild their global instruction and capability snapshot automatically.

## Install optional GodMode Paperwork

Paperwork is distributed through the repository's Codex marketplace so that
its sensitive-document contract does not become an implicit capability of every
core installation.

Add the released marketplace, install the plugin, and verify discovery:

```bash
codex plugin marketplace add cubetribe/CODEX_GodMode_ON --ref v2.10.0
codex plugin list --marketplace codex-godmode-on --available --json
codex plugin add godmode-paperwork@codex-godmode-on
codex plugin list --json
```

Start a fresh task and invoke `$godmode-paperwork` explicitly. Its metadata
disables implicit invocation. The plugin requires Python 3.11 or newer and can
use locally installed Poppler (`pdfinfo`, `pdftotext`, `pdftoppm`) and Tesseract
with the requested language data. Its `doctor` command reports capabilities but
does not install, download, update, or upload anything.

Keep case roots and exports outside Git worktrees, the repository checkout, and
Codex plugin caches. On macOS, `/tmp` resolves through a symlink and is rejected
by the strict path policy; use `/private/tmp` only for disposable tests, not for
long-lived sensitive cases. See [GodMode Paperwork](./godmode-paperwork.md) for
the complete operator contract.

## Installed layout

The default targets are:

```text
$CODEX_HOME/
|- AGENTS.md
|- config.toml
|- godmode-swiftui.config.toml
|- godmode-web.config.toml
|- godmode-flutter.config.toml
|- godmode-review.config.toml
|- agents/
|  `- 14 GodMode .toml manifests
|- playwright-output/isolated/
`- backups/install-archives/<unique-run-id>/

~/.agents/skills/
`- 10 GodMode skill directories
```

When `CODEX_HOME` is unset, it defaults to `~/.codex`. The skills home defaults
to `~/.agents/skills`.

The repository package source remains under `templates/global-codex/`. It is
not copied into project-local `.codex/agents/` or `.agents/skills/`, which would
make Codex discover duplicate personal and project entries in this repo.

The optional plugin remains under `plugins/godmode-paperwork/` and is exposed by
`.agents/plugins/marketplace.json`. The core installers deliberately do not copy
it into the global skill directory.

## Safe configuration behavior

### Existing `config.toml`

If `$CODEX_HOME/config.toml` already exists, installation preserves every byte
by default. It does not parse, merge, reorder, downgrade, or add a project trust
entry. This protects quoted keys, multiline values, model providers, MCP
servers, plugins, projects, model selection, reasoning level, and future fields
the package does not own.

The installer prints a warning when the existing file lacks a trust entry for
this repository, or contains legacy inline `[profiles.*]` tables. Add trust
manually if desired; migrate legacy profiles deliberately. Neither warning
authorizes a rewrite.

If no config exists, the installer renders the bundled base template, expands
the portable Playwright output path, and adds this repository as trusted unless
`--no-trust-project` is set.

Use a reset only when you intentionally want to replace the whole file with the
bundled base config:

```bash
./scripts/apply-global-codex-setup.sh --reset-config
```

```powershell
.\scripts\apply-global-codex-setup.ps1 --reset-config
```

The reset creates a backup first. It is a breaking, explicit choice; it is not
a repair step to run casually.

### Separate managed profiles

Codex `0.134.0+` loads named profiles from separate files at the root of
`$CODEX_HOME`. Version 2.0 installs:

```bash
codex --profile godmode-swiftui
codex --profile godmode-web
codex --profile godmode-flutter
codex --profile godmode-review
```

These files do not choose a model or reasoning level. A pre-existing managed
profile with different content is treated as a conflict and stops the installer
before any write. Review it, then use `--reset-config` if replacing that managed
profile is intentional. Unrelated user profile files remain untouched.

Inline tables such as `[profiles.web]` are legacy for this CLI generation. The
installer reports them in an existing config but does not silently edit them.

### Global `AGENTS.md`

The managed guidance is bounded by exactly one ordered pair:

```text
<!-- CODEX_GODMODE_GLOBAL_AGENTS:BEGIN -->
...
<!-- CODEX_GODMODE_GLOBAL_AGENTS:END -->
```

On repeat installation, only that block is replaced exactly; content outside it
is preserved. A recognized unmarked v1.1 GodMode template is migrated without
duplication. Any other unmarked file is retained under `Preserved User Guidance`
after the managed block. Duplicate, reversed, or incomplete markers fail the
preflight before any mutation.

Use `--reset-agents` only to replace the complete global guidance file after a
backup:

```bash
./scripts/apply-global-codex-setup.sh --reset-agents
```

```powershell
.\scripts\apply-global-codex-setup.ps1 --reset-agents
```

### Agents, skills, and backups

The installer makes each current GodMode-owned agent file and skill directory
exactly match the package source. Replacing a managed skill directory removes
stale files inside that directory. It does not delete unrelated user-owned
agents, skills, or profiles.

Changed managed targets are archived under a unique per-run directory:

```text
$CODEX_HOME/backups/install-archives/<timestamp-and-run-id>/
```

Legacy `*.backup-*` artifacts are moved out of live agent and skill discovery
roots so they cannot appear as duplicate capabilities.

## Installer options

Both installers support the same long options:

| Option | Meaning |
| --- | --- |
| `--check` | verify the installed managed runtime without applying changes |
| `--codex-home PATH` | override the Codex home target |
| `--user-skills-home PATH` | override the user skill target |
| `--repo PATH` | use another checkout as package source and trust target |
| `--no-trust-project` | do not add or require this repository's trust entry |
| `--reset-config` | back up and replace config plus conflicting managed profiles |
| `--reset-agents` | back up and replace the complete global `AGENTS.md` |
| `-h`, `--help` | print usage |

`--check` cannot be combined with a reset option.

Exit codes are stable for automation:

| Code | Meaning |
| --- | --- |
| `0` | success |
| `1` | general preflight, drift, marker, source, or install failure |
| `2` | invalid arguments or option combination |
| `3` | missing or incompatible Codex CLI/capability |
| `4` | conflicting managed profile without explicit reset |

## Exact verification contract

`--check` verifies:

- the managed global `AGENTS.md` block is exact and correctly marked
- all four managed profile files are exact
- all 14 current packaged agent files are exact
- every packaged skill directory is exact, including nested metadata
- required directories and base config exist
- live discovery roots contain no legacy `*.backup-*` artifacts
- the selected Codex CLI meets the minimum version and capability contract

The checker intentionally does not compare an existing user `config.toml` with
the bundled template; byte-preservation is the contract for that file. A missing
trust entry or legacy inline profile is reported without rewriting it.

## Upgrade from 1.x

1. Update the checkout and inspect release notes.
2. Confirm the resolved CLI with `type -a codex`, `codex --version`, and
   `codex doctor`.
3. Run the normal installer without reset flags.
4. Confirm that your existing `config.toml` hash or byte comparison is unchanged.
5. Run the exact `--check` command.
6. Start a fresh task and invoke `$godmode-workflow` explicitly once.
7. Use `codex --profile godmode-web` or another namespaced profile when needed.

The known v1.1 global guidance migrates automatically. Model and reasoning pins
in installed GodMode agent manifests are replaced by the 2.0 model-inheritance
contract. User-owned model selection in `config.toml` remains unchanged.

## Test the package without touching your home

On macOS or Linux:

```bash
tmp_root="$(mktemp -d)"
tmp_codex="$tmp_root/.codex"
tmp_skills="$tmp_root/.agents/skills"

./scripts/apply-global-codex-setup.sh \
  --codex-home "$tmp_codex" \
  --user-skills-home "$tmp_skills" \
  --no-trust-project
./scripts/apply-global-codex-setup.sh --check \
  --codex-home "$tmp_codex" \
  --user-skills-home "$tmp_skills" \
  --no-trust-project
```

For the maintained regression matrix:

```bash
./scripts/test-global-codex-setup.sh
```

On Windows:

```powershell
.\scripts\test-global-codex-setup.ps1
```

The GitHub workflow enforces that PowerShell fixture on Windows PowerShell 5.1
and PowerShell 7. This documentation does not imply that both Windows runtimes
were executed on a non-Windows developer machine.

The regression suites cover clean installation and exact check, complex TOML
preservation, profile conflict/reset behavior, v1.1 and custom guidance
migration, malformed markers, drift repair, idempotence, and documented exit
codes.

## Activation smoke test

After a successful install, open a fresh task in a representative workspace:

```text
$godmode-workflow

Goal: Inspect this workspace and return a read-only governance and capability preflight.
Done when: The response names the applicable instructions, selected model inheritance,
and whether a bounded research subagent would materially help. Do not edit files.
```

This checks skill discovery and the orchestration contract without granting a
write or release action.

## Troubleshooting

### “The installer says Codex is too old”

Run `type -a codex` or `Get-Command codex -All`. Update or remove the shadowing
installation, clear the shell command cache, and rerun `codex --version`.

### “My custom config did not receive the base defaults”

That is intentional in 2.0. Existing config is user-owned and preserved
byte-for-byte. Copy individual settings manually, or use `--reset-config` only
after reviewing its full replacement behavior and backup.

### “The managed profile conflicts”

The installer stopped before writes to protect the existing file. Compare it
with `templates/global-codex/profiles/`, preserve any personal behavior under a
different profile name, then use `--reset-config` if replacement is intended.

### “My global guidance has malformed markers”

Restore one BEGIN marker followed by one END marker. Alternatively, back up the
complete malformed `AGENTS.md` outside `$CODEX_HOME`, remove the malformed
target, and run the normal installer so it can create a clean managed file.
`--reset-agents` does not bypass malformed-marker preflight; the installer will
not guess around duplicate, missing, or reversed markers.

### “The old task still behaves like 1.x”

Start a fresh task. Global instructions, skills, profiles, and custom agent
metadata are discovered when Codex constructs the task context.

## Boundaries

- installation is local and user-level; it is not a daemon or scheduled task
- the installer does not enable Responses API beta features
- profile and agent inheritance do not guarantee account access to GPT-5.6 or
  Ultra
- hooks are not required to spawn or complete the GodMode workflow
- push, merge, release, deploy, and other external changes still require their
  own authority
