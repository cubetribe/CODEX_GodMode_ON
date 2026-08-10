# Local Development

The released core version is `3.0.0`. Protected `main` delivery uses a pull
request. Commit, push, merge, tag, and publication remain separate authority
boundaries. GodMode Paperwork is an independently versioned optional plugin,
currently `2.10.0`.

## Preflight

Read root `AGENTS.md`, `README.md`, `CONTRIBUTING.md`, `CHANGELOG.md`, and the
files governing the changed surface. Preserve unrelated work. Keep one writer
for overlapping tracked files and finish required docs plus `[Unreleased]`
before final validation.

## Repository map

| Path | Purpose |
| --- | --- |
| `templates/global-codex/` | installable core guidance, config, roster, agents, profiles, and skills |
| `templates/prototype-mode/` | local-only prototype overlay |
| `.agents/plugins/marketplace.json` | optional plugin catalog |
| `plugins/godmode-paperwork/` | separately installed Paperwork plugin and focused tests |
| `scripts/apply-global-codex-setup.*` | cross-platform core installers |
| `scripts/test-global-codex-setup.*` | installer and migration regression suites |
| `scripts/check-static.py` | deterministic package contract |
| `scripts/validate-codex-plugins.py` | plugin metadata and package contract |
| `scripts/check-capabilities.sh` | workstation diagnostics only |
| `evals/routing/` | mode and specialist-budget fixtures |
| `tests/fixtures/` | immutable historical installer inputs |
| `state/` | optional resumable local state |
| `reports/generated/` | ignored analysis output, never release truth |

Packaged core agents and skills must not appear under repo-local
`.codex/agents/` or `.agents/skills/`, because that would duplicate entries after
global install. Optional plugins are distributed only through the marketplace.

## Validation by scope

Run the deterministic repository gate:

```bash
./scripts/check-static.sh
```

It parses TOML and JSON, validates core inventory/rosters, skill metadata,
prompt budgets, links, routing fixtures, shell syntax, diff hygiene, release
alignment, and the optional plugin manifest.

For Bash installer, migration, inventory, or installed-runtime changes:

```bash
./scripts/test-global-codex-setup.sh
./scripts/test-isolated-codex-runtime.sh
```

The regression suite covers fresh installs, exact checks, targeted 2.0 config
migration, custom config preservation, profile conflict/reset, unique backups,
known 1.1 guidance, exact 2.0 retirement, CRLF normalization, no-write conflicts,
marker safety, drift repair, idempotence, and stable exit classes.

PowerShell changes require the Windows CI matrix:

```powershell
.\scripts\test-global-codex-setup.ps1
```

For changes to Paperwork itself:

```bash
python3 scripts/validate-codex-plugins.py --repo-root .
python3 -m unittest discover -s plugins/godmode-paperwork/tests -v
```

Keep real cases, originals, and exports outside Git worktrees and plugin caches.
Use only synthetic disposable fixtures in repository tests.

For local tool diagnosis:

```bash
./scripts/check-capabilities.sh
./scripts/check-capabilities.sh --full
```

This is not a package gate. Missing optional SDKs are informational; a broken
required Codex version is reported as invalid, never `[ok]`.

`./scripts/check-local-env.sh` remains a compatibility dispatcher: default runs
static plus capabilities, `--ci` runs static only, and `--full` adds full
capability diagnostics. It never runs installer or plugin runtime suites
implicitly.

## Changing the managed roster

Keep these surfaces aligned in one change:

1. `templates/global-codex/agents/` and `skills/`;
2. `templates/global-codex/managed-assets.tsv`;
3. both installers and both regression suites when migration behavior changes;
4. root/global governance and relevant primary skills;
5. README, registry, blueprint, setup guide, and `[Unreleased]`.

An active removal becomes a retirement row only when the installer has an exact
historical fixture and normalized digest. Never add a tombstone that could
match arbitrary user content. Conflict detection must complete before target
directories, backups, or current assets are written.

## Prompt and role changes

Global guidance is budgeted at 1,500 bytes and the core workflow at 2,000 bytes.
Put stack detail in stack skills and repository law in repository governance.
Primary modes remain mutually exclusive. Avoid generic custom roles that the
parent or built-in `explorer`/`worker` already cover.

`validator` is static and read-only. `tester` is runtime-focused, may create
temporary output, and does not edit tracked source. Update their descriptions,
docs, and routing evals together if that boundary changes.

When selecting a packaged role, the parent must pass the matching `agent_type`.
`task_name` is only a task label. The routing contract and deterministic check
must change together if Codex changes that tool interface.

## Release preparation

Normal development updates only `[Unreleased]`. Root `VERSION` must match the
latest dated core changelog release. Each optional plugin owns a local
`plugins/<name>/VERSION`; its manifest must match that file.

A core-only release does not bump Paperwork. When Paperwork itself changes,
align its local version, manifest, CLI output, documentation, and compatibility
tests. Its persisted evidence and validator versions must not change without an
explicit backward-compatibility design and frozen cross-version fixtures.

For an authorized release:

1. reconcile current `origin/main` and run final static, Bash installer,
   isolated runtime, affected-plugin, live-routing, and Windows CI evidence;
2. resolve every release-critical finding;
3. move `[Unreleased]` into a dated section, update root `VERSION`, and write
   the official release document before final gates;
4. rerun affected local gates after those tracked edits;
5. deliver through a protected-main pull request and wait for every required
   check on the exact head SHA;
6. squash-merge, then wait for push CI on the resulting `main` SHA;
7. tag that exact SHA and publish the GitHub release without moving the tag.

Stable CLI `0.147.0` multi-agent release traces must use a persistent isolated
Codex home. `--ephemeral` cannot reliably materialize Child threads, and the
public JSONL stream omits part of their lifecycle. Verify named `agent_type`,
Child commands, exit status, and unchanged fixtures from the persisted session
graph and rollouts; a final model-written `PASS` is insufficient.
