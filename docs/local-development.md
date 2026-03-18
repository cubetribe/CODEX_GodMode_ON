# Local Development

This repository is meant to be developed locally on this Mac and mirrored back to GitHub without hidden setup steps.

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

- `.codex/agents/` contains agent-role definitions
- `.agents/skills/` contains reusable procedures and stack guidance
- `reports/generated/` is for local generated reports
- `state/` is for local workflow state

## Recommended loop

1. `git pull --ff-only origin main`
2. run `./scripts/check-local-env.sh`
3. optionally run `./scripts/apply-global-codex-setup.sh`
4. start Codex from the repo root
5. use the starter prompt that matches the task
6. make the smallest safe change
7. run the relevant validations only
8. commit on `main` when you really want to keep the change
9. push `main` when explicitly approved

## Good first skills in this repo

- `godmode-workflow`
- `apple-platforms`
- `web-platforms`
- `flutter-dart`
- `release-manager`

## Not part of this step

- a dedicated GUI for the agent system
- a fully automated runtime outside Codex
- CI/CD or release automation

Those can come later once the local reference structure is stable.
