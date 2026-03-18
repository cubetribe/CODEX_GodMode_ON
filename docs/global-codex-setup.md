# Configure Codex Globally

This note explains the user-level Codex setup that matches this repository.

The goal is simple:

- stable defaults across projects
- less prompt repetition
- a clean split between personal defaults and repo-specific rules

## Recommended layer model

The current Codex documentation supports this structure:

- personal guidance in `~/.codex/AGENTS.md`
- personal technical defaults in `~/.codex/config.toml`
- repo rules in `AGENTS.md`
- repo defaults in `.codex/config.toml`
- project-specific custom agents in `.codex/agents/*.toml`
- repo-specific reusable procedures in `.agents/skills/`

Priority rules that matter:

- the closest `AGENTS.md` to the current working directory wins
- `.codex/config.toml` is loaded only for trusted projects

## Fast start on this Mac

This repository ships a reproducible global setup under:

- `templates/global-codex/AGENTS.md`
- `templates/global-codex/config.toml`
- `scripts/apply-global-codex-setup.sh`

Apply it with:

```bash
./scripts/apply-global-codex-setup.sh
```

That script does three things:

- installs `~/.codex/AGENTS.md` and `~/.codex/config.toml` from the repo templates
- ensures `~/.agents/skills/` and `~/.codex/playwright-output/isolated` exist
- adds the current repo path as a trusted project

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

These profiles are intentionally thin. The real workflow guidance still lives in:

- `AGENTS.md`
- repo `AGENTS.md`
- project-specific skills

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

## Why not a giant start prompt

The more durable pattern is:

- `~/.codex/AGENTS.md` for personal defaults
- `~/.codex/config.toml` for personal technical defaults
- repo `AGENTS.md` for team or project rules
- repo `.codex/config.toml` for technical repo defaults
- repo `.codex/agents/*.toml` for project roles
- repo `.agents/skills/` for reusable procedures

This repository keeps prompts short on purpose because the real behavior belongs in those layers.

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
- OpenAI Codex docs: [Agent Skills](https://developers.openai.com/codex/skills)
- OpenAI Codex docs: [Configuration reference](https://developers.openai.com/codex/config-reference)
- OpenAI Codex docs: [Sample configuration](https://developers.openai.com/codex/config-sample)
- OpenAI Codex docs: [Worktrees](https://developers.openai.com/codex/app/worktrees)
- OpenAI Codex docs: [Automations](https://developers.openai.com/codex/app/automations)
- OpenAI Codex docs: [Codex app settings](https://developers.openai.com/codex/app/settings)
