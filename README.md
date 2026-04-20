<div align="center">
  <h1>CODEX_GodMode_ON</h1>
  <p><strong>Install once globally. Then start Codex with a skill-first workflow in any workspace.</strong></p>
  <p>This repository packages a globally installable Codex workflow inspired by <a href="https://github.com/cubetribe/ClaudeCode_GodMode-On">ClaudeCode_GodMode-On</a>.</p>
  <p>
    <a href="./docs/blueprint.md">Blueprint</a>
    &middot;
    <a href="./docs/department-orchestration.md">Department Model</a>
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

Install the workflow once:

```bash
./scripts/apply-global-codex-setup.sh
```

After that, start Codex in any workspace and invoke the workflow skill directly.

The current recommended entry model is skill-first:

- keep durable behavior in `AGENTS.md`, config, agents, and skills
- keep the user prompt focused on the actual task, context, constraints, and done condition
- add extra skills only when they materially change the workflow

This repository is the installer, reference implementation, and contribution surface for the global setup.

Default start:

```text
$godmode-workflow

Goal: <goal>

Context:
- <relevant files, errors, architecture notes, or constraints>

Done when:
- <what finished looks like>
```

Add another skill only when the task really needs it:

| Add this | When it materially helps |
| --- | --- |
| `$godmode-departments` | multi-domain work that needs frozen write scopes, handoffs, and explicit department routing |
| `$godmode-debug` | reproducible bugs, failing builds/tests, or regressions that need a reproduce -> isolate -> fix -> re-test loop |
| `$godmode-review` | findings-first code, architecture, or release-risk review that should stay read-heavy by default |
| `$greenfield-bootstrap` | empty folders, new repos, or workspaces that still lack repo-local governance |
| `$web-platforms` | React, Next.js, or Node.js work where stack rules should shape the run immediately |
| `$apple-platforms` | SwiftUI, macOS, or iOS work where Apple-platform guidance should shape the run immediately |
| `$flutter-dart` | Flutter or Dart work where analyzer/test/state-flow guidance should shape the run immediately |

Optional example prompts:

- [docs/prompts/dev-start-prompt.md](./docs/prompts/dev-start-prompt.md) for the default minimal entry
- [docs/prompts/greenfield-start-prompt.md](./docs/prompts/greenfield-start-prompt.md) for bootstrap-heavy repos
- [docs/prompts/review-start-prompt.md](./docs/prompts/review-start-prompt.md) for findings-first review sessions
- [docs/prompts/debug-start-prompt.md](./docs/prompts/debug-start-prompt.md) and the stack examples under [docs/prompts/](./docs/prompts/) as optional examples, not required runtime surface

## How To Use It

1. Install the global runtime once with `./scripts/apply-global-codex-setup.sh`.
2. Open any workspace in the Codex app or CLI.
3. Start with `$godmode-workflow` and describe the real task.
4. Add context, constraints, and `Done when` only as needed.
5. Add a companion skill only when the workflow truly changes.

## Scaling The Team

GodMode should scale to the task. Do not start with a ten-agent setup unless the work really crosses multiple ownership areas.

- Lean lane: use the orchestrator plus `builder` and the normal validation gates for small, single-scope work.
- Guided lane: add `researcher`, `architect`, or `api_guardian` when uncertainty, design risk, or contract risk rises.
- Department lane: activate 2-4 bounded department tracks only when the task spans multiple domains and needs explicit handoffs.

The department model is documented in [docs/department-orchestration.md](./docs/department-orchestration.md). It is an optional scaling layer, not the default for every run.

Recommended entry model:

- `$godmode-workflow` is the primary entry skill.
- `$godmode-departments`, `$godmode-debug`, and `$godmode-review` are focused companion skills, not competing default entry points.
- stack or bootstrap skills should be added only when they change the run materially.

## Skills, Slash Commands, and Agents

### Skills

- Skills are invoked with `$`, not with `@`.
- Example: `$godmode-workflow`, `$godmode-departments`, `$godmode-debug`, `$godmode-review`, `$greenfield-bootstrap`, `$web-platforms`, `$apple-platforms`, `$flutter-dart`
- In Codex, you can type `$` in the composer to mention a skill directly.
- In the Codex app, enabled skills can also appear in the slash-command list.

### Slash commands

- In the Codex app, type `/` in the composer to open the slash-command list.
- Useful built-in commands include `/status`, `/review`, and `/plan-mode`.
- In interactive Codex sessions, slash commands are for session control; the main runtime surface in this repo is the skill layer, with prompt files kept as examples.

### Agents and subagents

- The GodMode runtime installs custom agents such as `researcher`, `architect`, `builder`, `validator`, `tester`, `scribe`, and `api_guardian`.
- The installed runtime now also ships optional department-oriented agents: `runtime_platform`, `workflow_design`, `workspace_governance`, `quality_operations`, `docs_dx`, and `ci_security_guardian`.
- Use `ci_security_guardian` whenever `.github/**`, GitHub Actions behavior, `CODEOWNERS`, or repository-protection guidance changes.
- The runtime is still role-centric by default. The department model is an optional routing layer for larger tasks, not the default path for every run.
- The documented prompt files in this repo are examples, not the durable runtime itself.
- The durable runtime surface is `AGENTS.md` plus config, agents, and skills.
- To use the installed agents, ask Codex directly to use or split work across those roles.
- In the CLI, `/agent` lets you switch between active agent threads after subagents have been spawned.
- Start with the smallest viable team, then expand only when the task needs more bounded ownership and handoffs.

## Which Skills To Add

- Start with `$godmode-workflow` for most tasks.
- Add `$godmode-departments` only when routing, handoffs, or write-scope control really become part of the task.
- Add `$godmode-debug` for bug work, failing validation paths, or regression hunting.
- Add `$godmode-review` for findings-first review sessions where edits are not the default outcome.
- Add `$greenfield-bootstrap` when the workspace still needs local governance before parallel work.
- Add stack skills only when their rules should influence the run from the first step.
- Use the debug, review, and stack-specific prompt files only as lightweight examples, not as required templates.

## What This Repo Is

This repository is the documented reference and installer source for a Codex-native version of the GodMode workflow:

- explicit orchestration instead of hidden automation
- a clear main thread acting as orchestrator
- focused specialist agents
- optional department routing for larger multi-domain tasks
- persistent reports and state artifacts
- hard quality gates before completion

It is not just a prompt pack. It is the bootstrap repo for the globally installed system.

## What You Get

| Area | Purpose |
| --- | --- |
| `README.md` | the public entry point and primary skill-first start model |
| `docs/blueprint.md` | the architecture and workflow design |
| `docs/department-orchestration.md` | the scalable department-based routing model |
| `docs/agent-registry.md` | machine-readable register of the current agent runtime |
| `docs/roadmap.md` | phased delivery plan |
| `docs/local-development.md` | maintainer operating guide for this repo |
| `docs/global-codex-setup.md` | reproducible install guide for the global runtime |
| `docs/prompts/` | optional example prompts built on top of the skill runtime |
| `.codex/agents/` | canonical GodMode agent role definitions that the installer publishes to `~/.codex/agents/` |
| `.agents/skills/` | canonical GodMode skills that the installer publishes to `~/.agents/skills/` |
| `templates/global-codex/` | global `AGENTS.md` and `config.toml` templates |
| `templates/project-bootstrap/` | starter template for repo-local governance in greenfield work |
| `scripts/check-local-env.sh` | local repo validation |
| `scripts/apply-global-codex-setup.sh` | install the documented global setup, agents, and skills |
| `reports/` | persistent report conventions |
| `reports/templates/` | reusable intake, routing, handoff, and write-scope templates |
| `state/` | persistent workflow state conventions |
| `state/templates/` | reusable orchestration state templates |

## Core Decisions

- The main thread stays the orchestrator.
- The orchestrator should choose the smallest viable team for the task.
- Repo governance discovery is mandatory before implementation, release, or documentation edits.
- Greenfield work must create local repo governance before parallel delivery starts.
- Department mode is optional and should activate only when the task crosses multiple ownership areas.
- Multi-domain work should pass through research, architecture, and contract review before departments write in parallel.
- The normal code writer is `builder`; validation and testing stay read-heavy.
- `validator` and `tester` form a joint quality gate.
- `api_guardian` is mandatory for API, schema, CLI, or config-surface changes.
- Reports and state live in the repo, not only in chat history.
- Push and deploy remain explicit human decisions.
- This repository now operates on `main` by default.
- Daily use should work from any workspace after a one-time global install.

## Read Next

| If you want to... | Start here |
| --- | --- |
| understand the full target architecture | [docs/blueprint.md](./docs/blueprint.md) |
| see when to stay lean and when to fan out into departments | [docs/department-orchestration.md](./docs/department-orchestration.md) |
| see what gets delivered in what order | [docs/roadmap.md](./docs/roadmap.md) |
| run and evolve the repo locally | [docs/local-development.md](./docs/local-development.md) |
| install the matching global Codex setup | [docs/global-codex-setup.md](./docs/global-codex-setup.md) |

## Sources

- Source repo: [cubetribe/ClaudeCode_GodMode-On](https://github.com/cubetribe/ClaudeCode_GodMode-On)
- Codex docs: [Subagents](https://developers.openai.com/codex/concepts/subagents)
- Codex docs: [Slash commands in Codex CLI](https://developers.openai.com/codex/cli/slash-commands)
- Codex docs: [Codex app commands](https://developers.openai.com/codex/app/commands)
- Codex docs: [Best practices](https://developers.openai.com/codex/learn/best-practices)
- Codex docs: [Custom instructions with AGENTS.md](https://developers.openai.com/codex/guides/agents-md/)
- Codex docs: [Configuration reference](https://developers.openai.com/codex/config-reference/)
- Codex docs: [Agent Skills](https://developers.openai.com/codex/skills/)
- OpenAI Cookbook: [Codex Prompting Guide](https://developers.openai.com/cookbook/examples/gpt-5/codex_prompting_guide)

## Contributing

If you contribute here:

1. Keep the README truthful and immediately usable.
2. Keep prompts copy-paste friendly.
3. Keep architecture docs explicit and auditable.
4. Keep the repository aligned around `main` unless a branch is explicitly requested.
