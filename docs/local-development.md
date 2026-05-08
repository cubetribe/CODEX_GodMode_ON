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

## Release prep

Current release target: `1.0.0`.

Before publishing a release:

1. confirm `VERSION` matches the intended release
2. move relevant `CHANGELOG.md` entries from `[Unreleased]` into the dated release section
3. run `git diff --check`
4. run `./scripts/check-local-env.sh`
5. run `./scripts/apply-global-codex-setup.sh --check`
6. run a clean-target installer smoke test when installer behavior changed
7. inspect `git diff --stat` and confirm no unrelated files changed
8. prepare a clear release summary and upgrade notes

Clean-target installer smoke test:

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

Do not commit, tag, push, or publish a GitHub release until that action is explicitly approved.

## Repo structure

- `.codex/agents/` contains the canonical GodMode agent-role definitions
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
7. use the starter prompt that matches the task
8. make the smallest safe change
9. run the relevant validations only
10. commit on `main` when you really want to keep the change
11. push `main` when explicitly approved

## Validation matrix

| Change type | Minimum validation |
| --- | --- |
| docs-only copy changes | `git diff --check` plus link/path consistency review |
| skills or agent metadata | `./scripts/check-local-env.sh` |
| installer or global template changes | `./scripts/apply-global-codex-setup.sh --check` and clean-target smoke test |
| model or config defaults | docs review, changelog entry, installer check |
| release prep | all checks above plus `VERSION` and `CHANGELOG.md` review |

## Good first skills in this repo

- `godmode-workflow`
- `godmode-debug`
- `godmode-review`
- `godmode-departments`
- `greenfield-bootstrap`
- `apple-platforms`
- `web-platforms`
- `flutter-dart`
- `release-manager`

## Not part of this step

- a dedicated GUI for the agent system
- a fully automated runtime outside Codex
- CI/CD or release automation

Those can come later once the global install flow is stable.
