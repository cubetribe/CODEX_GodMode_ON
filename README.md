<div align="center">
  <h1>CODEX_GodMode_ON</h1>
  <p><em>Two years of refinement. The loop is now closed.</em></p>
  <p><strong>A globally installable workflow that turns Codex into a structured, self-orchestrating engineering team —<br>and uses that same system to build and improve itself.</strong></p>
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

---

> This could have been a paid product. It's open source — built from two years
> of love for the community.

## What This Is

Most AI coding setups are prompt packs. This is not.

CODEX_GodMode_ON is a complete, installable runtime: **14 custom agents**, 10
workflow skills, explicit quality gates, persistent state artifacts, and an
orchestration model refined over two years of real-world use. Every design
decision has been sharpened continuously — and for the past several months, a
threshold was crossed.

**Codex now helps build CODEX_GodMode_ON. The system improves itself.**

That's not a metaphor. The workflow you install here is the same workflow used
to evolve and ship this repository. When Codex runs inside a GodMode session, it
operates with the same roles, gates, and governance that produced the code it's
running on. Research → plan → build → validate. Explicit orchestration. Hard
stops before push or deploy. The main thread stays the orchestrator. Always.

This is the loop closing. The runtime is stable. It's yours for free.

## What's New

The latest release adds **prototype mode** on top of the production workflow:

**`$godmode-prototype`** — a local-only fast lane for rapid spikes and
throwaway proof-of-concepts. It skips production gates, forces `PROTOTYPE ONLY`
watermarks, and hands promotion back to `$godmode-workflow`.

The 1.0 runtime also added three dedicated workflow modes and a security layer:

**`$godmode-debug`** — a dedicated bug-hunting lane with a strict reproduce →
isolate → fix → re-test loop. Add it when you need to chase a regression,
failing build, or unexpected runtime behavior. It changes how Codex approaches
the problem from the first step.

**`$godmode-review`** — a findings-first review skill. Codex stays read-heavy,
reports issues with file and line references, and makes no edits unless you
explicitly ask. Use it for code review, architecture assessment, or pre-release
risk checks.

**`$godmode-departments`** — the optional scaling layer for work that crosses
multiple ownership areas. Instead of a single orchestrator loop, this activates
bounded department tracks with explicit handoffs and frozen write scopes. Not
the default — but powerful when a task genuinely spans domains.

**`$greenfield-bootstrap`** — bootstraps local repo governance in empty or
undocumented workspaces before parallel implementation starts. No more agents
writing into a repo that has no rules yet.

**`ci_security_guardian`** — a new department agent that owns GitHub Actions,
CODEOWNERS, pinned workflow actions, and repository-protection posture.
Mandatory when `.github/**` or CI surfaces change.

**`docs/agent-registry.md`** — an auditable register of the full installed
agent runtime. Single source of truth for what's installed and what each agent
is responsible for.

## The Runtime At A Glance

Install once. Use everywhere.

| Layer | What's installed |
| --- | --- |
| **Core agents** | `researcher`, `architect`, `api_guardian`, `builder`, `validator`, `tester`, `scribe`, `github_manager` — pinned to `gpt-5.5` / `high` |
| **Department agents** | `runtime_platform`, `workflow_design`, `workspace_governance`, `quality_operations`, `docs_dx`, `ci_security_guardian` — pinned to `gpt-5.5` / `high` |
| **Workflow skills** | `$godmode-workflow`, `$godmode-prototype`, `$godmode-debug`, `$godmode-review`, `$godmode-departments`, `$greenfield-bootstrap`, `$web-platforms`, `$apple-platforms`, `$flutter-dart`, `$release-manager` |
| **Stack profiles** | SwiftUI / iOS, React / Next.js, Flutter / Dart, Review mode |
| **Persistent artifacts** | `reports/`, `state/` — workflow history stays in the repo, not only in chat |

14 agents. 10 skills. One global install. Any workspace.

---

## Start Here

Install the workflow once — you never need to pull this repo into a project
again:

```bash
./scripts/apply-global-codex-setup.sh
```

Verify the installed runtime:

```bash
./scripts/apply-global-codex-setup.sh --check
```

Open any workspace in the Codex app or CLI and start with `$godmode-workflow`.
That's the default entry for most work.

```text
$godmode-workflow

Goal: <goal>

Context:
- <relevant files, errors, architecture notes, or constraints>

Done when:
- <what finished looks like>
```

Add a companion skill only when the task truly changes shape:

| Add this                | When it materially helps                                                                      |
| ----------------------- | --------------------------------------------------------------------------------------------- |
| `$godmode-debug`        | reproducible bugs, failing builds/tests, or regressions — reproduce → isolate → fix → re-test |
| `$godmode-review`       | findings-first review that should stay read-heavy; no edits unless asked                      |
| `$godmode-departments`  | multi-domain work that needs frozen write scopes, handoffs, and explicit department routing   |
| `$greenfield-bootstrap` | empty folders, new repos, or workspaces missing repo-local governance                         |
| `$web-platforms`        | React, Next.js, or Node.js work where stack rules should shape the run from step one          |
| `$apple-platforms`      | SwiftUI, macOS, or iOS work where Apple-platform guidance matters from the start              |
| `$flutter-dart`         | Flutter or Dart work where analyzer/test/state-flow guidance should be active immediately     |

For throwaway local spikes, use `$godmode-prototype` instead of
`$godmode-workflow`. Prototype mode is not a companion skill; it is a separate
local-only fast lane with watermark and migration rules.

Optional example prompts live under [docs/prompts/](./docs/prompts/) — they're
starting points, not required templates.

## How To Use It

1. Install the global runtime once with the matching setup script for your platform.
2. Open any workspace in the Codex app or CLI.
3. Start with `$godmode-workflow` and describe the real task.
4. Add context, constraints, and a `Done when` condition for non-trivial work.
5. Add a companion skill only when the workflow genuinely changes.

## Scaling The Team

GodMode scales to the task. Don't start with a ten-agent setup unless the work
actually crosses multiple ownership areas.

**Lean lane** — orchestrator + `builder` + normal quality gates. Best for small,
single-scope work where the risk is low and the path is clear.

**Guided lane** — add `researcher`, `architect`, or `api_guardian` when
uncertainty, design risk, or API contract risk rises. The orchestrator still
drives; these agents feed in before `builder` writes.

**Department lane** — activate 2–4 bounded department tracks via
`$godmode-departments` only when the task spans multiple domains and needs
explicit handoffs and frozen write scopes.

The full department model is documented in
[docs/department-orchestration.md](./docs/department-orchestration.md). It's an
optional scaling layer, not the default path for every run.

## Skills, Slash Commands, and Agents

### Skills

Skills are invoked with `$`, not `@`. Type `$` in the Codex composer to mention
a skill directly. In the Codex app, enabled skills also appear in the
slash-command list.

| Skill                   | Use it for                                                      |
| ----------------------- | --------------------------------------------------------------- |
| `$godmode-workflow`     | primary entry — research → plan → build → validate delivery     |
| `$godmode-prototype`    | local-only rapid spikes with watermarks and migration checklist |
| `$godmode-debug`        | reproduce → isolate → fix → re-test bug work                    |
| `$godmode-review`       | findings-first assessment, no edits unless asked                |
| `$godmode-departments`  | optional routing for multi-domain work with frozen write scopes |
| `$greenfield-bootstrap` | bootstraps local governance in empty or undocumented workspaces |
| `$web-platforms`        | React, Next.js, and Node.js stack guidance                      |
| `$apple-platforms`      | SwiftUI, macOS, and iOS guidance                                |
| `$flutter-dart`         | Flutter and Dart guidance                                       |
| `$release-manager`      | release impact, changelog, and PR copy                          |

### Slash commands

In the Codex app, type `/` to open the slash-command list. Useful built-in
commands include `/status`, `/review`, and `/plan-mode`. In interactive Codex
CLI sessions, useful commands include `/status`, `/review`, `/plan`, `/agent`,
`/permissions`, `/mcp`, and `/model`. Slash commands are for session control;
the skill layer is the durable runtime interface.

### Agents

The GodMode runtime installs 14 custom agents globally.

**Core agents** handle the standard research → plan → build → validate loop:

| Agent            | Role                                                    |
| ---------------- | ------------------------------------------------------- |
| `researcher`     | read-only source verification and repo discovery        |
| `architect`      | read-only design and smallest viable change plan        |
| `api_guardian`   | read-only API, schema, CLI, config, and contract review |
| `builder`        | the single normal implementation writer                 |
| `validator`      | structural, static, and consistency validation          |
| `tester`         | focused executable checks and runtime verification      |
| `scribe`         | docs and release notes after quality gates pass         |
| `github_manager` | branch, PR, and release framing — no push by default    |

**Department agents** activate only when the task crosses multiple ownership
areas:

| Agent                  | Use it for                                                          |
| ---------------------- | ------------------------------------------------------------------- |
| `runtime_platform`     | Codex runtime defaults, toolchain, sandbox, and environment         |
| `workflow_design`      | workflow procedures, skill boundaries, and handoff design           |
| `workspace_governance` | AGENTS layering, local repo rules, and release law                  |
| `quality_operations`   | validation scope, install checks, and repeatable smoke paths        |
| `docs_dx`              | README, setup docs, prompts, and contributor-facing clarity         |
| `ci_security_guardian` | GitHub Actions, CODEOWNERS, pinned actions, and repository security |

To use the installed agents, ask Codex directly to use or split work across
those roles. In the CLI, `/agent` lets you switch between active agent threads
after subagents have been spawned. Start with the smallest viable team and
expand only when the task needs it.

## What This Repo Is

This repository is the documented reference and installer source for a
Codex-native version of the GodMode workflow:

- explicit orchestration instead of hidden automation
- a clear main thread acting as orchestrator
- focused specialist agents with hard role boundaries
- optional department routing for larger multi-domain tasks
- persistent reports and state artifacts that survive the chat session
- explicit quality gates before any release or completion

It is not just a prompt pack. It is the bootstrap repo for the globally
installed system. The same system builds itself.

## What You Get

| Area                                  | Purpose                                                                    |
| ------------------------------------- | -------------------------------------------------------------------------- |
| `README.md`                           | public entry point and primary skill-first start model                     |
| `docs/blueprint.md`                   | full architecture and workflow design                                      |
| `docs/department-orchestration.md`    | scalable department-based routing model                                    |
| `docs/agent-registry.md`              | auditable register of the installed agent runtime                          |
| `docs/prototype-mode.md`              | local-only prototype lane contract, templates, and migration path          |
| `docs/roadmap.md`                     | phased delivery plan                                                       |
| `docs/local-development.md`           | maintainer operating guide                                                 |
| `docs/global-codex-setup.md`          | reproducible install guide for the global runtime                          |
| `docs/prompts/`                       | optional example prompts built on top of the skill runtime                 |
| `templates/global-codex/agents/`      | packaged GodMode agent role definitions → installed to `~/.codex/agents/`  |
| `templates/global-codex/skills/`      | packaged GodMode skills → installed to `~/.agents/skills/`                 |
| `templates/global-codex/`             | global `AGENTS.md`, `config.toml`, agent, and skill package sources        |
| `templates/project-bootstrap/`        | starter template for repo-local governance in greenfield work              |
| `scripts/check-local-env.sh`          | local repo validation                                                      |
| `scripts/apply-global-codex-setup.sh` | install the documented global setup, agents, and skills                    |
| `reports/` + `reports/templates/`     | persistent report conventions and reusable templates                       |
| `state/` + `state/templates/`         | persistent workflow state conventions and orchestration templates          |

## Core Decisions

- The main thread stays the orchestrator.
- The orchestrator chooses the smallest viable team for the task.
- Repo governance discovery is mandatory before implementation, release, or
  documentation edits.
- Greenfield work must bootstrap local governance before parallel delivery
  starts.
- Department mode is optional — activate it only when a task genuinely crosses
  multiple ownership areas.
- Multi-domain work passes through research, architecture, and contract review
  before departments write in parallel.
- `builder` is the single normal code writer; validation and testing stay
  read-heavy.
- `validator` and `tester` form a joint quality gate.
- `api_guardian` is mandatory for any API, schema, CLI, or config-surface
  change.
- Reports and state live in the repo, not only in chat history.
- Push and deploy remain explicit human decisions.
- This repository operates on `main` by default.
- Daily use works from any workspace after a one-time global install.

## Read Next

| If you want to...                                            | Start here                                                             |
| ------------------------------------------------------------ | ---------------------------------------------------------------------- |
| understand the full target architecture                      | [docs/blueprint.md](./docs/blueprint.md)                               |
| learn when to stay lean and when to fan out into departments | [docs/department-orchestration.md](./docs/department-orchestration.md) |
| run local-only throwaway spikes safely                       | [docs/prototype-mode.md](./docs/prototype-mode.md)                     |
| see what gets delivered in what order                        | [docs/roadmap.md](./docs/roadmap.md)                                   |
| run and evolve this repo locally                             | [docs/local-development.md](./docs/local-development.md)               |
| install the matching global Codex setup                      | [docs/global-codex-setup.md](./docs/global-codex-setup.md)             |

## Sources

- Source repo:
  [cubetribe/ClaudeCode_GodMode-On](https://github.com/cubetribe/ClaudeCode_GodMode-On)
- Codex docs:
  [Subagents](https://developers.openai.com/codex/concepts/subagents)
- Codex docs:
  [Slash commands in Codex CLI](https://developers.openai.com/codex/cli/slash-commands)
- Codex docs:
  [Codex app commands](https://developers.openai.com/codex/app/commands)
- Codex docs:
  [Best practices](https://developers.openai.com/codex/learn/best-practices)
- Codex docs:
  [Custom instructions with AGENTS.md](https://developers.openai.com/codex/guides/agents-md/)
- Codex docs:
  [Configuration reference](https://developers.openai.com/codex/config-reference/)
- Codex docs: [Agent Skills](https://developers.openai.com/codex/skills/)
- OpenAI Cookbook:
  [Codex Prompting Guide](https://developers.openai.com/cookbook/examples/gpt-5/codex_prompting_guide)

## Contributing

1. Keep the README truthful and immediately usable.
2. Keep prompts copy-paste friendly.
3. Keep architecture docs explicit and auditable.
4. Keep the repository aligned around `main` unless a branch is explicitly
   requested.
