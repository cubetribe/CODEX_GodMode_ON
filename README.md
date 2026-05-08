<div align="center">
  <h1>CODEX_GodMode_ON</h1>
  <p><strong>Version 1.0.0: install once globally, then start any Codex session with the prompts below.</strong></p>
  <p>This repository packages a globally installable Codex workflow inspired by <a href="https://github.com/cubetribe/ClaudeCode_GodMode-On">ClaudeCode_GodMode-On</a>.</p>
  <p>
    <a href="./docs/blueprint.md">Blueprint</a>
    &middot;
    <a href="./docs/roadmap.md">Roadmap</a>
    &middot;
    <a href="./docs/local-development.md">Local Dev</a>
    &middot;
    <a href="./docs/global-codex-setup.md">Global Setup</a>
  </p>
</div>

## Start Here

Users should not need to pull this repository into every new session.

Install or update the workflow once:

```bash
./scripts/apply-global-codex-setup.sh
```

Verify the installed runtime:

```bash
./scripts/apply-global-codex-setup.sh --check
```

After that, start Codex in any workspace and copy one of these prompts exactly as-is.

These prompts intentionally use skill mentions such as `$godmode-workflow`, `$godmode-debug`, `$web-platforms`, `$apple-platforms`, and `$flutter-dart`. That is the documented Codex skill invocation path.

This repository is the installer, reference implementation, and contribution surface for the global setup.

## What 1.0.0 Means

`1.0.0` is the first release where the documented GodMode runtime is treated as a complete, installable baseline:

- global installation of the core custom agents and workflow skills
- companion lanes for debug, review, department routing, and greenfield bootstrap
- optional department agents for large cross-domain work
- current Codex guidance for subagents, skills, AGENTS layering, app commands, and CLI commands
- `gpt-5.5` as the default model in the shipped global config template
- local and global validation scripts that check the packaged runtime surface
- packaged agents and skills stored outside repo-local discovery paths so this bootstrap repo does not show duplicate project and personal skill entries after global install

This is still an explicit Codex workflow, not a separate hidden automation engine. Codex only uses subagents when you ask it to delegate work.

Files:

- [docs/prompts/dev-start-prompt.md](./docs/prompts/dev-start-prompt.md)
- [docs/prompts/debug-start-prompt.md](./docs/prompts/debug-start-prompt.md)
- [docs/prompts/review-start-prompt.md](./docs/prompts/review-start-prompt.md)
- [docs/prompts/web-start-prompt.md](./docs/prompts/web-start-prompt.md)
- [docs/prompts/apple-start-prompt.md](./docs/prompts/apple-start-prompt.md)
- [docs/prompts/flutter-start-prompt.md](./docs/prompts/flutter-start-prompt.md)

Dev:

```text
$godmode-workflow

GODMODE DEV

Goal: <goal>

Inspect the current workspace first.
Loop: research -> plan -> build -> validate.
```

Debug:

```text
$godmode-workflow
$godmode-debug

GODMODE DEBUG

Goal: <bug / symptom / expected result>

Inspect the current workspace first.
Loop: reproduce -> isolate -> fix -> re-test.
```

Review:

```text
$godmode-workflow
$godmode-review

GODMODE REVIEW

Goal: <system / change / problem to assess>

Inspect the current workspace first.
Loop: inspect -> analyze -> verify -> report.
Findings first. No code changes unless asked.
```

Stack-specific dev starters:

Web:

```text
$godmode-workflow
$web-platforms

GODMODE WEB

Goal: <goal>

Inspect the current workspace first.
Loop: research -> plan -> build -> validate.
```

Apple:

```text
$godmode-workflow
$apple-platforms

GODMODE APPLE

Goal: <goal>

Inspect the current workspace first.
Loop: research -> plan -> build -> validate.
```

Flutter:

```text
$godmode-workflow
$flutter-dart

GODMODE FLUTTER

Goal: <goal>

Inspect the current workspace first.
Loop: research -> plan -> build -> validate.
```

## Recommended Task Shape

The short prompts above are intentionally minimal. For bigger work, add this structure after `Goal`:

```text
Context: <repo, product, branch, or relevant background>
Constraints: <non-goals, files to avoid, compatibility requirements>
Done when: <validation commands, expected behavior, release output>
```

That shape keeps the main thread, specialists, and later validation aligned.

## How To Use It

1. Install the global runtime once with `./scripts/apply-global-codex-setup.sh`.
2. Open any workspace in the Codex app or CLI.
3. Paste one of the prompts from this README into a new thread.
4. Replace `Goal` with the real task.
5. Add `Context`, `Constraints`, and `Done when` for non-trivial work.
6. Let Codex inspect the workspace first, then follow the requested loop.

## Workflow At A Glance

The normal GodMode loop is:

1. inspect workspace and governance
2. research only when source verification or repo discovery is needed
3. design the smallest viable change
4. route API, CLI, config, or schema impact through `api_guardian`
5. implement through the single normal writer, `builder`
6. run `validator` and `tester` before final docs or release output
7. summarize release impact and stop before commit, push, merge, or deploy unless the user explicitly approves

Use `$godmode-departments` only when a task crosses multiple ownership areas and needs advisory lanes before the builder starts.

## Skills, Slash Commands, and Agents

### Skills

- Skills are invoked with `$`, not with `@`.
- Example: `$godmode-workflow`, `$godmode-debug`, `$godmode-review`, `$web-platforms`, `$apple-platforms`, `$flutter-dart`
- In Codex, you can type `$` in the composer to mention a skill directly.
- In the Codex app, enabled skills can also appear in the slash-command list.
- Use `$godmode-departments` only for large cross-domain work, and use `$greenfield-bootstrap` before parallel work in empty or undocumented workspaces.

Installed workflow skills:

| Skill | Use it for |
| --- | --- |
| `$godmode-workflow` | normal research -> plan -> build -> validate delivery |
| `$godmode-debug` | reproduce -> isolate -> fix -> re-test work |
| `$godmode-review` | findings-first assessment with no edits unless asked |
| `$godmode-departments` | optional routing for large cross-domain work |
| `$greenfield-bootstrap` | first local governance in empty or undocumented workspaces |
| `$web-platforms` | React, Next.js, and Node.js guidance |
| `$apple-platforms` | SwiftUI, macOS, and iOS guidance |
| `$flutter-dart` | Flutter and Dart guidance |
| `$release-manager` | release impact, changelog, and PR copy |

### Slash commands

- In the Codex app, type `/` in the composer to open the slash-command list. Useful app commands include `/status`, `/review`, `/plan-mode`, and `/mcp`.
- In the Codex CLI, useful interactive commands include `/status`, `/review`, `/plan`, `/agent`, `/permissions`, `/mcp`, and `/model`.
- Slash commands are for session control; the workflow prompts in this repo are for task startup.

### Agents and subagents

- The GodMode runtime installs custom agents such as `researcher`, `architect`, `builder`, `validator`, `tester`, `scribe`, and `api_guardian`.
- It also installs optional department agents such as `runtime_platform`, `workflow_design`, `workspace_governance`, `quality_operations`, and `docs_dx`.
- The documented prompt surface in this repo uses skills to start the workflow, not `@agent` mentions.
- To use the installed agents, ask Codex directly to use or split work across those roles.
- Codex subagents are available by default, but Codex only spawns them when you explicitly ask for delegation.
- In the CLI, `/agent` lets you switch between active agent threads after subagents have been spawned.

Core agents:

| Agent | Role |
| --- | --- |
| `researcher` | read-only source verification and repo discovery |
| `architect` | read-only design and smallest viable change plan |
| `api_guardian` | read-only API, schema, CLI, config, and contract review |
| `builder` | the single normal implementation writer |
| `validator` | read-heavy structural, static, and consistency validation |
| `tester` | focused executable checks and runtime verification |
| `scribe` | docs and release-note work after quality gates pass |
| `github_manager` | branch, PR, and release framing without pushing by default |

Optional department agents:

| Agent | Use it for |
| --- | --- |
| `runtime_platform` | Codex runtime defaults, toolchain, sandbox, and environment concerns |
| `workflow_design` | workflow procedures, skill boundaries, and durable handoff design |
| `workspace_governance` | AGENTS layering, local repo rules, and release law |
| `quality_operations` | validation scope, install checks, and repeatable smoke paths |
| `docs_dx` | README, setup docs, prompts, and contributor-facing clarity |

## Which Prompt To Use

- Use `GODMODE DEV` for general implementation.
- Use `GODMODE DEBUG` for reproduce -> isolate -> fix work.
- Use `GODMODE REVIEW` for analysis-only or findings-first review.
- Use `GODMODE WEB` for React, Next.js, and Node.js work.
- Use `GODMODE APPLE` for SwiftUI, macOS, and iOS work.
- Use `GODMODE FLUTTER` for Flutter and Dart work.

## What This Repo Is

This repository is the documented reference and installer source for a Codex-native version of the GodMode workflow:

- explicit orchestration instead of hidden automation
- a clear main thread acting as orchestrator
- focused specialist agents
- conventions for persistent reports and state artifacts
- explicit quality gates before completion

It is not just a prompt pack. It is the bootstrap repo for the globally installed system.

## Updating From 0.2.x

From a previous 0.2.x install:

1. Pull or download this repository update.
2. Run `./scripts/check-local-env.sh` from the repo root.
3. Run `./scripts/apply-global-codex-setup.sh`.
4. Run `./scripts/apply-global-codex-setup.sh --check`.
5. Start a new Codex thread in any workspace and use one of the prompts above.

The installer backs up existing global files before replacing them. It updates `~/.codex/AGENTS.md`, `~/.codex/config.toml`, `~/.codex/agents/`, and `~/.agents/skills/`.

This repository intentionally stores the packaged agents and skills under `templates/global-codex/agents/` and `templates/global-codex/skills/`, not under repo-local `.codex/agents/` or `.agents/skills/`. That prevents duplicate `CODEX_GodMode_ON` and personal entries in the Codex skill picker after the global runtime is installed.

## What You Get

| Area | Purpose |
| --- | --- |
| `README.md` | the public entry point and copy-paste prompts |
| `docs/blueprint.md` | the architecture and workflow design |
| `docs/roadmap.md` | phased delivery plan |
| `docs/local-development.md` | maintainer operating guide for this repo |
| `docs/global-codex-setup.md` | reproducible install guide for the global runtime |
| `docs/prompts/` | standalone prompt documents |
| `templates/global-codex/agents/` | packaged GodMode agent role definitions that the installer publishes to `~/.codex/agents/` |
| `templates/global-codex/skills/` | packaged GodMode skills that the installer publishes to `~/.agents/skills/` |
| `templates/global-codex/` | global `AGENTS.md`, `config.toml`, agent, and skill templates |
| `scripts/check-local-env.sh` | local repo validation |
| `scripts/apply-global-codex-setup.sh` | install the documented global setup, agents, and skills |
| `reports/` | persistent report conventions |
| `state/` | persistent workflow state conventions |

## Core Decisions

- The main thread stays the orchestrator.
- The normal code writer is `builder`; validation and testing stay read-heavy.
- `validator` and `tester` form a joint quality gate.
- `api_guardian` is mandatory for API, schema, CLI, or config-surface changes.
- Reports and state live in the repo, not only in chat history.
- Multi-agent fan-out is optional; use it when a task crosses ownership boundaries or when read-heavy work can run independently.
- Push and deploy remain explicit human decisions.
- This repository now operates on `main` by default.
- Daily use should work from any workspace after a one-time global install.

## Validation

For this release line, the expected maintainer checks are:

```bash
git diff --check
./scripts/check-local-env.sh
./scripts/apply-global-codex-setup.sh --check
```

When changing installer behavior, also run a clean temporary install with custom `--codex-home` and `--user-skills-home` paths.

## Read Next

| If you want to... | Start here |
| --- | --- |
| understand the full target architecture | [docs/blueprint.md](./docs/blueprint.md) |
| see what gets delivered in what order | [docs/roadmap.md](./docs/roadmap.md) |
| run and evolve the repo locally | [docs/local-development.md](./docs/local-development.md) |
| install the matching global Codex setup | [docs/global-codex-setup.md](./docs/global-codex-setup.md) |

## Sources

- Source repo: [cubetribe/ClaudeCode_GodMode-On](https://github.com/cubetribe/ClaudeCode_GodMode-On)
- Codex docs: [Subagents](https://developers.openai.com/codex/subagents/)
- Codex docs: [Slash commands in Codex CLI](https://developers.openai.com/codex/cli/slash-commands)
- Codex docs: [Codex app commands](https://developers.openai.com/codex/app/commands)
- Codex docs: [Custom instructions with AGENTS.md](https://developers.openai.com/codex/guides/agents-md/)
- Codex docs: [Configuration reference](https://developers.openai.com/codex/config-reference/)
- Codex docs: [Agent Skills](https://developers.openai.com/codex/skills/)
- Codex docs: [Best practices](https://developers.openai.com/codex/learn/best-practices)
- OpenAI API docs: [Models](https://developers.openai.com/api/docs/models)
- OpenAI API docs: [Agents orchestration](https://developers.openai.com/api/docs/guides/agents/orchestration)
- OpenAI API docs: [Evaluate agent workflows](https://developers.openai.com/api/docs/guides/agent-evals)

## Contributing

If you contribute here:

1. Keep the README truthful and immediately usable.
2. Keep prompts copy-paste friendly.
3. Keep architecture docs explicit and auditable.
4. Keep the repository aligned around `main` unless a branch is explicitly requested.
