<div align="center">
  <h1>CODEX_GodMode_ON</h1>
  <p><strong>Copy-paste starter prompts first. Codex-native architecture blueprint second.</strong></p>
  <p>This repository documents and packages a main-first Codex workflow inspired by <a href="https://github.com/cubetribe/ClaudeCode_GodMode-On">ClaudeCode_GodMode-On</a>.</p>
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

This system is already in active use. The repository therefore needs to tell the truth immediately, at the top, and in English.

If you only need to start a new Codex thread, copy one of these prompts exactly as-is and replace `Goal`.

This repository is intentionally `main`-first:

- `main` is the delivery branch
- no standing side branches unless explicitly required
- prompts live in the README because they are part of the product surface

Files:

- [docs/prompts/dev-start-prompt.md](./docs/prompts/dev-start-prompt.md)
- [docs/prompts/debug-start-prompt.md](./docs/prompts/debug-start-prompt.md)
- [docs/prompts/review-start-prompt.md](./docs/prompts/review-start-prompt.md)

Dev:

```text
GODMODE DEV

Goal: <goal>

Use repo workflow, available tools, agents, and skills.
Loop: research -> plan -> build -> validate.
Use subagents when useful.
Keep changes minimal. Verify before push.
```

Debug:

```text
GODMODE DEBUG

Goal: <bug / symptom / expected result>

Use repo workflow, available tools, agents, and skills.
Loop: reproduce -> isolate -> fix -> re-test.
Use subagents when useful.
Stay on the failing path until green.
```

Review:

```text
GODMODE REVIEW

Goal: <system / change / problem to assess>

Use repo workflow, available tools, agents, and skills.
Loop: inspect -> analyze -> verify -> report.
Use subagents when useful.
Findings first. No code changes unless asked.
```

## What This Repo Is

This repository is the documented reference for a Codex-native version of the GodMode workflow:

- explicit orchestration instead of hidden automation
- a clear main thread acting as orchestrator
- focused specialist agents
- persistent reports and state artifacts
- hard quality gates before completion

It is not just a prompt pack. It is the blueprint, starter kit, and local reference structure for the system.

## What You Get

| Area | Purpose |
| --- | --- |
| `README.md` | the public entry point and copy-paste prompts |
| `docs/blueprint.md` | the architecture and workflow design |
| `docs/roadmap.md` | phased delivery plan |
| `docs/local-development.md` | local operating guide for this repo |
| `docs/global-codex-setup.md` | reproducible user-level Codex setup |
| `docs/prompts/` | standalone prompt documents |
| `.codex/agents/` | project-specific agent role definitions |
| `.agents/skills/` | reusable workflow and stack skills |
| `templates/global-codex/` | global Codex config templates |
| `scripts/check-local-env.sh` | local repo validation |
| `scripts/apply-global-codex-setup.sh` | install the documented global setup |
| `reports/` | persistent report conventions |
| `state/` | persistent workflow state conventions |

## Core Decisions

- The main thread stays the orchestrator.
- The normal code writer is `builder`; validation and testing stay read-heavy.
- `validator` and `tester` form a joint quality gate.
- `api_guardian` is mandatory for API, schema, CLI, or config-surface changes.
- Reports and state live in the repo, not only in chat history.
- Push and deploy remain explicit human decisions.
- This repository now operates on `main` by default.

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
- Codex docs: [Custom instructions with AGENTS.md](https://developers.openai.com/codex/guides/agents-md/)
- Codex docs: [Configuration reference](https://developers.openai.com/codex/config-reference/)
- Codex docs: [Agent Skills](https://developers.openai.com/codex/skills/)

## Contributing

If you contribute here:

1. Keep the README truthful and immediately usable.
2. Keep prompts copy-paste friendly.
3. Keep architecture docs explicit and auditable.
4. Keep the repository aligned around `main` unless a branch is explicitly requested.
