# GodMode 3 Lean Architecture

Status: implemented in `[Unreleased]`, not yet released. `VERSION` remains
`2.10.0` until separately authorized major-release preparation.

## Design objective

GodMode keeps constraints that are difficult or dangerous to infer and removes
ceremonial phases. A strong parent model should normally finish a scoped task
without a custom agent. Delegation is an exception for an independent,
material uncertainty or useful read-only parallelism.

## Authority layers

From broadest to narrowest:

1. platform and product instructions;
2. managed global `~/.codex/AGENTS.md`;
3. repository and nested `AGENTS.md` files;
4. one selected primary mode skill;
5. task-specific user instructions.

In this repository, root `AGENTS.md` is normative for implementation,
`CHANGELOG.md` and `VERSION` govern release state, and deterministic scripts
define what named checks prove. Other docs describe those contracts and must
not redefine them.

## Runtime flow

```text
governance and authority
        ↓
goal + scope + observable done criteria
        ↓
material unknown?
  no ───────────────→ parent works alone
  yes → 1..2 narrow specialists (advisors read-only; tester disposable output only)
        ↓
parent or one built-in worker writes
        ↓
static validator and/or runtime tester, selected by risk
        ↓
evidence against each done criterion + residual risk
```

The default is zero specialists. Custom specialists never delegate again.
There is one tracked-file writer for overlapping scope. Commit, push, release,
deploy, and other external mutations remain separate authority boundaries.

## Primary modes

Exactly one primary mode applies to a run:

| Mode | Contract |
| --- | --- |
| `godmode-workflow` | implementation or migration |
| `godmode-debug` | reproduce, isolate, repair, re-test |
| `godmode-review` | read-only assessment with findings first |
| `godmode-prototype` | disposable local-only build with watermarks |

Greenfield, release, and stack skills are support layers. A primary mode does
not activate another primary mode as a companion.

GodMode Paperwork is a separately installed optional plugin, not another core
primary mode and not part of the core installer. Its explicit
`$godmode-paperwork` skill owns a local-first document-evidence workflow with
fail-closed integrity checks and declared human review boundaries.

## Custom-agent boundary

The core package ships seven optional agents. `api_guardian`,
`runtime_platform`, `workflow_design`, `docs_dx`, and `ci_security_guardian`
investigate narrow domains. `validator` owns static structure and contracts.
`tester` owns executable behavior and may create temporary tool output but not
edit tracked source.

Generic discovery and writing use the parent or Codex built-ins such as
`explorer` and `worker`; they do not need permanent GodMode duplicates.

Agent manifests intentionally omit model and effort pins. Resolution is
per-setting: an explicit spawn setting wins, then a configured `[agents]`
default, then the parent value. A pin in a custom manifest would override that
inheritance and is therefore avoided.

## Validation selection

| Changed surface | Minimum evidence |
| --- | --- |
| Markdown, links, core metadata, config, contracts | `check-static`, optionally `validator` |
| Installer or executable behavior | focused fixture, optionally `tester` |
| Plugin manifest, schema, docs, or code | plugin validator and focused plugin tests |
| Mixed migration, security, or release-critical work | all affected static and runtime gates |
| Local tool availability | `check-capabilities`, diagnostic only |

Required documentation and `[Unreleased]` text are written before final gates.
Any later tracked edit invalidates the affected evidence.

## Configuration

The packaged base config caps concurrency at two. It currently uses the
compatible `max_threads = 2` alias because stable Codex `0.144.1` rejects the
newer documented key while the tested desktop build accepts both. `max_depth`
was removed because it is not a documented current contract. No-recursive
delegation is declared in prompts, not enforced as a technical sandbox boundary.
Deterministic fixtures lint that contract; live model behavior needs a separate
trace.

Models, reasoning effort, MCP servers, plugins, and integrations remain
user-owned. The installer migrates only an exact rendered 2.0 package config
without trust or with the current source repository's generated trust entry to
the Lean base; all other existing configs remain byte-for-byte unchanged unless
`--reset-config` is explicitly selected.

## Installation ownership and migration

`templates/global-codex/managed-assets.tsv` is the managed core roster and
retirement ledger. A normal upgrade:

1. validates every present retired asset against its normalized 2.0 digest;
2. aborts before writes on modified, symlinked, or structurally unknown data;
3. copies exact legacy assets into a unique backup archive and verifies it;
4. removes only those verified paths;
5. installs the seven agents, nine skills, profiles, and inventory;
6. runs an exact managed-asset check, excluding preserved user config.

Unrelated custom agents, skills, and optional plugins remain untouched.
Paperwork is distributed through `.agents/plugins/marketplace.json`; its cases
and exports stay outside Git worktrees and plugin caches.

## State and reports

Ordinary single-session tasks need neither. Use ignored local state only for a
long, paused, or handed-off run. It records source revision, authority, writer,
scope, done criteria, evidence, blockers, and next action. Generated research
belongs under `reports/generated/`; release truth remains in `CHANGELOG.md`.

## Non-goals

- guaranteeing better quality solely from fewer files;
- automatically choosing models or reasoning effort;
- silently installing optional plugins or their dependencies;
- hiding user config behind package defaults;
- proving Windows behavior from macOS;
- turning a local green run into permission to commit, push, or release.
