# Configure Codex Globally

This note explains the user-level Codex setup that turns this repository into a one-time installer instead of a per-session dependency.

This page documents the `1.0.0` runtime layout.

The goal is simple:

- install once
- use the GodMode workflow in any workspace
- keep a clean split between global runtime and local project capabilities

## Recommended layer model

The current Codex documentation supports this structure:

- personal guidance in `~/.codex/AGENTS.md`
- personal technical defaults in `~/.codex/config.toml`
- personal custom agents in `~/.codex/agents/*.toml`
- personal reusable skills in `~/.agents/skills/`
- repo rules in `AGENTS.md`
- repo defaults in `.codex/config.toml`
- project-specific custom agents in `.codex/agents/*.toml`
- repo-specific reusable procedures in `.agents/skills/`

Discovery rules that matter:

- Codex reads global guidance from `AGENTS.override.md` when present, otherwise `AGENTS.md`
- project guidance is layered from the project root down to the current working directory
- in each project directory, `AGENTS.override.md` takes precedence over `AGENTS.md`
- files closer to the current working directory win because they appear later in the merged instruction chain
- `.codex/config.toml` is loaded only for trusted projects
- same-name skills are not AGENTS-style merged; keep skill names focused and avoid accidental duplicates

## Fast start by platform

This repository ships a reproducible global setup under:

- `templates/global-codex/AGENTS.md`
- `templates/global-codex/config.toml`
- `templates/global-codex/agents/`
- `templates/global-codex/skills/`
- `scripts/apply-global-codex-setup.sh`
- `scripts/apply-global-codex-setup.ps1`

Apply the matching installer for your platform:

macOS/Linux:

```bash
./scripts/apply-global-codex-setup.sh
```

Windows:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\apply-global-codex-setup.ps1
```

These installers do five things:

- installs `~/.codex/AGENTS.md` and `~/.codex/config.toml` from the repo templates
- installs the GodMode agents to `~/.codex/agents/`
- installs the GodMode skills to `~/.agents/skills/`
- ensures `~/.codex/playwright-output/isolated` exists
- adds the current repo path as a trusted project

It also archives prior install snapshots under `~/.codex/backups/` instead of
leaving `*.backup-*` files or directories inside the active agent and skill
discovery roots. That matters because in-place backups can surface as duplicate
skills or agents in Codex.

It also replaces the `__CODEX_HOME__` placeholder inside the config template so the Playwright output path stays portable.

To verify the result:

macOS/Linux:

```bash
./scripts/apply-global-codex-setup.sh --check
```

Windows:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\apply-global-codex-setup.ps1 -Check
```

## Upgrade from 0.2.x

The previous public line was `0.2.1`. Version `1.0.0` expands the installed runtime and changes the default model to `gpt-5.5`.

Use this sequence:

```bash
git pull --ff-only origin main
./scripts/check-local-env.sh
./scripts/apply-global-codex-setup.sh
./scripts/apply-global-codex-setup.sh --check
```

On Windows, use the PowerShell installer and `-Check` command instead of the shell script.

The installer creates timestamped backups before replacing existing files or directories. After the upgrade, `~/.codex/agents/` should contain 14 agent manifests and `~/.agents/skills/` should contain the nine skills shipped by this repo.

If you maintain hand-edited personal guidance in `~/.codex/AGENTS.md` or `~/.codex/config.toml`, inspect the generated backup files and reapply personal edits intentionally.

This bootstrap repository intentionally does not keep the packaged runtime under repo-local `.codex/agents/` or `.agents/skills/`. Those are official project discovery paths; keeping the global package source there would make Codex show duplicate project and personal skills when this repository is open after installation.

## Minimal global files

Create the Codex home directory if needed:

```bash
mkdir -p ~/.codex
```

Global guidance belongs in `~/.codex/AGENTS.md`.

Example:

```md
# ~/.codex/AGENTS.md

## Default working style
- Work only inside the currently opened project.
- Keep diffs small, safe, and buildable.
- Do not touch unrelated files.

## Execution flow
- For non-trivial tasks: Research -> Plan -> Build -> Validate -> Release Summary.
- Start with a governance preflight and identify the repo's release and documentation rules before editing versioned artifacts.
- Before editing, report repo root, current branch, touched files, and expected impact.

## Safety gates
- Never commit unless I explicitly say yes.
- Never push unless I explicitly say yes.
- Never force-push.
```

Global technical defaults belong in `~/.codex/config.toml`.

Example:

```toml
model = "gpt-5.5"
approval_policy = "on-request"
sandbox_mode = "workspace-write"
web_search = "cached"

[sandbox_workspace_write]
writable_roots = []
network_access = false
```

Why this is a good baseline:

- `gpt-5.5` is the current frontier default for coding and professional work
- `approval_policy = "on-request"` keeps risky actions interactive
- `sandbox_mode = "workspace-write"` allows project edits without full machine access
- `web_search = "cached"` is conservative by default

Changing the model default is a release-impacting behavior change. Keep it documented in `CHANGELOG.md` and verify the installed config after applying the setup script.

## Global profiles

The repo templates install four user-level profiles:

- `swiftui` for Apple platform work
- `web` for React, Next.js, and Node.js work
- `flutter` for Flutter and Dart work
- `review` for review and audit sessions

Examples:

```bash
codex --profile swiftui
codex --profile web
codex --profile flutter
codex --profile review
```

These profiles are intentionally thin. The workflow itself comes from the globally installed `AGENTS.md`, custom agents, and skills.

For greenfield work, the installed skills also include
`greenfield-bootstrap` so a new repo can establish local rules before the
rest of the workflow fans out.

## Installed runtime layout

After running the installer, the user-level runtime looks like this:

```text
~/.codex/
  AGENTS.md
  config.toml
  agents/
    researcher.toml
    architect.toml
    api_guardian.toml
    builder.toml
    validator.toml
    tester.toml
    scribe.toml
    github_manager.toml
    runtime_platform.toml
    workflow_design.toml
    workspace_governance.toml
    quality_operations.toml
    docs_dx.toml
    ci_security_guardian.toml

~/.agents/
  skills/
    godmode-workflow/
    godmode-debug/
    godmode-review/
    godmode-departments/
    greenfield-bootstrap/
    apple-platforms/
    web-platforms/
    flutter-dart/
    release-manager/
```

The first eight agents remain the role-centric baseline. The department-oriented agents are optional additions for larger multi-domain runs and do not mean every task should fan out by default.

The matching skill split is:

- `godmode-workflow` as the primary entry skill for most runs
- `godmode-departments` as the explicit opt-in layer for department-mode routing
- `godmode-debug` as the focused companion for reproduce -> isolate -> fix work
- `godmode-review` as the focused companion for findings-first assessment work

That is the important UX boundary: users do not need this repository open in every new Codex session after installation.

## Runtime roles

The 1.0 runtime installs these core agents:

| Agent | Purpose |
| --- | --- |
| `researcher` | read-only research, source verification, and repo discovery |
| `architect` | read-only plan, boundary, and risk design |
| `api_guardian` | read-only API, schema, CLI, config, and user-visible contract review |
| `builder` | single normal implementation writer |
| `validator` | read-heavy consistency, static, and structural validation |
| `tester` | executable checks and focused runtime verification |
| `scribe` | docs, changelog, and release-note work after gates pass |
| `github_manager` | branch, PR, release, and governance framing |

It also installs optional department agents for large cross-domain runs:

| Agent | Purpose |
| --- | --- |
| `runtime_platform` | runtime defaults, sandboxing, tools, and environment concerns |
| `workflow_design` | orchestration procedures, skill boundaries, and handoff artifacts |
| `workspace_governance` | AGENTS layering, release law, and local project rules |
| `quality_operations` | validation plans, install checks, smoke paths, and eval-oriented checks |
| `docs_dx` | public docs, setup guidance, prompts, and developer experience |
| `ci_security_guardian` | GitHub Actions, CODEOWNERS, pinned actions, and repository security posture |

Department agents are advisory lanes. They do not replace the default `researcher` -> `architect` -> `builder` -> `validator` and `tester` route.

## Runtime skills

| Skill | Purpose |
| --- | --- |
| `godmode-workflow` | the normal non-trivial task loop |
| `godmode-debug` | reproduce -> isolate -> fix -> re-test work |
| `godmode-review` | findings-first review with no edits unless requested |
| `godmode-departments` | optional routing for cross-domain work |
| `greenfield-bootstrap` | create local governance before parallel work in empty or undocumented repos |
| `apple-platforms` | SwiftUI, macOS, and iOS guidance |
| `web-platforms` | React, Next.js, and Node.js guidance |
| `flutter-dart` | Flutter and Dart guidance |
| `release-manager` | release impact, changelog, and PR framing |

## Repo layout

Recommended structure:

```text
repo-root/
  AGENTS.md
  .codex/
    config.toml
    agents/
  .agents/
    skills/
```

Why the split matters:

- `AGENTS.md` defines durable guidance
- `.codex/config.toml` defines technical defaults
- `.codex/agents/*.toml` defines role-specific custom agents
- `.agents/skills/` stores reusable procedures
- workspace-local files remain project-scoped guidance or capabilities when a project needs them

In this bootstrap repository, packaged global runtime sources live under `templates/global-codex/agents/` and `templates/global-codex/skills/` instead. Downstream projects should still use `.codex/agents/` and `.agents/skills/` when they intentionally need project-local agents or skills.

## Why not a giant start prompt

The durable pattern is:

- `~/.codex/AGENTS.md` for personal defaults
- `~/.codex/config.toml` for personal technical defaults
- `~/.codex/agents/*.toml` for personal custom agents
- `~/.agents/skills/` for personal reusable workflow skills
- repo `AGENTS.md` for team or project rules
- repo `.codex/config.toml` for technical repo defaults
- repo `.codex/agents/*.toml` for project roles
- repo `.agents/skills/` for reusable procedures
- this repo's `templates/global-codex/agents/` and `templates/global-codex/skills/` for package sources that should not be discovered as project-local duplicates

This repository keeps prompts short on purpose because the real behavior belongs in those layers.

`AGENTS.md` files form a layered instruction chain. Skills are discovered capabilities with progressive disclosure: Codex sees metadata first and reads the full `SKILL.md` only when it selects the skill.

## Validation and smoke tests

Before publishing a release or telling users to update, run:

```bash
git diff --check
./scripts/check-local-env.sh
./scripts/apply-global-codex-setup.sh --check
```

For installer changes, verify a clean target:

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

That smoke test proves a first-time install can create the full runtime without relying on this machine's existing `~/.codex` or `~/.agents` state.

## Smoke-test the install

After applying the installer, start Codex in any workspace and use a minimal skill-first prompt such as:

```text
$godmode-workflow

Goal: <goal>
Context:
- <files, errors, constraints>
Done when:
- <finish condition>
```

Add companion skills such as `$godmode-departments`, `$godmode-debug`,
`$godmode-review`, `$greenfield-bootstrap`, or stack-specific skills only
when the task actually needs them. The prompt should not refer to this
repository as a required runtime dependency.

## Notes about Local vs Worktree

If you want to work directly in the checked-out repository, use `Local`.

Current Codex documentation makes these points explicit:

- new threads can be started in `Worktree`
- threads can move between `Local` and `Worktree`
- automations can run in either mode
- Codex-managed worktrees live under `$CODEX_HOME/worktrees`

I have not seen a documented global setting that forces every new session to use `Local` automatically. That is an inference from the currently reviewed docs, not an explicit negative statement from OpenAI.

## Sources

- OpenAI Codex docs: [Config basics](https://developers.openai.com/codex/config-basic)
- OpenAI Codex docs: [Custom instructions with AGENTS.md](https://developers.openai.com/codex/guides/agents-md)
- OpenAI Codex docs: [Customization](https://developers.openai.com/codex/concepts/customization)
- OpenAI Codex docs: [Best practices](https://developers.openai.com/codex/learn/best-practices)
- OpenAI Codex docs: [Agent Skills](https://developers.openai.com/codex/skills)
- OpenAI Codex docs: [Subagents](https://developers.openai.com/codex/subagents)
- OpenAI Codex docs: [Configuration reference](https://developers.openai.com/codex/config-reference)
- OpenAI Codex docs: [Sample configuration](https://developers.openai.com/codex/config-sample)
- OpenAI API docs: [All models](https://developers.openai.com/api/docs/models/all)
- OpenAI Codex docs: [Worktrees](https://developers.openai.com/codex/app/worktrees)
- OpenAI Codex docs: [Automations](https://developers.openai.com/codex/app/automations)
- OpenAI Codex docs: [Codex app settings](https://developers.openai.com/codex/app/settings)
