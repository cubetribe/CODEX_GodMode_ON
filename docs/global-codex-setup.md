# Configure Codex Globally

This note explains the user-level Codex setup that turns this repository into a one-time installer instead of a per-session dependency.

The goal is simple:

- install once
- use the GodMode workflow in any workspace
- keep a clean split between global runtime and local overrides

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

Priority rules that matter:

- the closest `AGENTS.md` to the current working directory wins
- `.codex/config.toml` is loaded only for trusted projects
- if a repo has no root `AGENTS.md`, Codex should still inspect repo-root `README.md`, `CONTRIBUTING.md`, PR templates, and release or governance docs before editing contracts or release artifacts
- if the workspace starts empty, create repo-local governance before parallel implementation begins

## Fast start on this Mac

This repository ships a reproducible global setup under:

- `templates/global-codex/AGENTS.md`
- `templates/global-codex/config.toml`
- `.codex/agents/`
- `.agents/skills/`
- `scripts/apply-global-codex-setup.sh`

Apply it with:

```bash
./scripts/apply-global-codex-setup.sh
```

That script does five things:

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

```bash
./scripts/apply-global-codex-setup.sh --check
```

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
model = "gpt-5.4"
approval_policy = "on-request"
sandbox_mode = "workspace-write"
web_search = "cached"

[sandbox_workspace_write]
writable_roots = []
network_access = false
```

Why this is a good baseline:

- `gpt-5.4` is a strong default model choice
- `approval_policy = "on-request"` keeps risky actions interactive
- `sandbox_mode = "workspace-write"` allows project edits without full machine access
- `web_search = "cached"` is conservative by default

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
    godmode-departments/
    godmode-debug/
    godmode-review/
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
- workspace-local copies remain optional overrides when a project needs them
- repos with custom versioning or documentation law should strongly prefer a root `AGENTS.md` so those rules are not left implicit in deeper docs only
- new repos should establish that root `AGENTS.md` early, before multi-agent delivery work starts

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

This repository keeps prompts short on purpose because the real behavior belongs in those layers.

The current best-practice entry pattern is:

- invoke `$godmode-workflow`
- describe the real task in plain language
- add context, constraints, and a done condition
- add companion skills only when they materially change the workflow

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
- OpenAI Cookbook: [Codex Prompting Guide](https://developers.openai.com/cookbook/examples/gpt-5/codex_prompting_guide)
- OpenAI Codex docs: [Configuration reference](https://developers.openai.com/codex/config-reference)
- OpenAI Codex docs: [Sample configuration](https://developers.openai.com/codex/config-sample)
- OpenAI Codex docs: [Worktrees](https://developers.openai.com/codex/app/worktrees)
- OpenAI Codex docs: [Automations](https://developers.openai.com/codex/app/automations)
- OpenAI Codex docs: [Codex app settings](https://developers.openai.com/codex/app/settings)
