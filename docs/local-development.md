# Local Development

This page is for maintainers of the bootstrap repository, not for end users starting everyday Codex sessions.

This repository is developed locally on this Mac and mirrored back to GitHub without hidden setup steps.

## Operating mode

This repo is now `main`-first:

- keep `main` current
- do the work locally
- validate locally
- push `main` when explicitly approved

Use a different branch only if you explicitly decide to.

## Required tools

Expected toolchain classes:

- `git`
- `python3`
- `node`, `npm`, `pnpm`
- `swift`, `xcodebuild`
- `flutter`, `dart`
- `codex`

## First checks

From the repository root:

```bash
./scripts/check-local-env.sh
```

To apply the matching user-level Codex setup on this Mac:

```bash
./scripts/apply-global-codex-setup.sh
```

Optional full check:

```bash
./scripts/check-local-env.sh --full
```

`--full` also runs `flutter doctor -v`, so it takes longer.

The same script is also used in GitHub Actions. In CI, it switches to repo-validation mode instead of requiring the full local Mac toolchain.

## Global profiles

The example global config installs four profiles:

- `swiftui`
- `web`
- `flutter`
- `review`

Examples:

```bash
codex --profile swiftui
codex --profile web
codex --profile flutter
codex --profile review
```

To verify the global setup:

```bash
./scripts/apply-global-codex-setup.sh --check
```

## Repo structure

- `.codex/agents/` contains the canonical GodMode agent-role definitions
- `.codex/agents/` now also contains the first optional department-oriented agent definitions
- `.agents/skills/` contains the canonical reusable workflow and stack skills
- `templates/global-codex/` contains the global `AGENTS.md` and `config.toml` templates
- `reports/generated/` is for local generated reports
- `state/` is for local workflow state

## Recommended loop

1. `git pull --ff-only origin main`
2. run `./scripts/check-local-env.sh`
3. optionally run `./scripts/apply-global-codex-setup.sh`
4. re-run `./scripts/apply-global-codex-setup.sh` after changing global guidance, agents, or skills
5. validate the installed setup, not just the repo files
6. start Codex in a representative workspace
7. start with `$godmode-workflow` and add only the extra skills the task really needs
8. make the smallest safe change
9. run the relevant validations only
10. commit on `main` when you really want to keep the change
11. push `main` when explicitly approved

## Definition of Done

A GodMode run is done only when all of these are true:

- `validator` gate is green
- `tester` gate is green
- `CHANGELOG.md` under `[Unreleased]` reflects the current unreleased branch state
- when department mode is active, the write-scope matrix has no single-writer conflict for the touched paths

## Good first skills in this repo

- `godmode-workflow`
- `godmode-departments`
- `godmode-debug`
- `godmode-review`
- `greenfield-bootstrap`
- `apple-platforms`
- `web-platforms`
- `flutter-dart`
- `release-manager`

## Not part of this step

- a dedicated GUI for the agent system
- a fully automated runtime outside Codex
- deployment automation or release automation beyond the repo validation CI

Those can come later once the global install flow is stable.
