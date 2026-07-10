<div align="center">
  <h1>CODEX_GodMode_ON</h1>
  <p><em>Local Codex orchestration with bounded subagents and evidence-backed delivery.</em></p>
  <p><strong>14 custom agents, 10 reusable skills, safe cross-platform installers,<br>and explicit quality gates for work from discovery through release.</strong></p>
  <p>
    <a href="./docs/global-codex-setup.md">Install</a>
    &middot;
    <a href="./docs/blueprint.md">Blueprint</a>
    &middot;
    <a href="./docs/agent-registry.md">Agents</a>
    &middot;
    <a href="./docs/department-orchestration.md">Departments</a>
    &middot;
    <a href="./docs/local-development.md">Maintain</a>
  </p>
</div>

---

## What this is

CODEX_GodMode_ON is a globally installable orchestration runtime for Codex. It
turns a non-trivial engineering request into a controlled delivery loop:

```text
governance and capability preflight
  -> bounded parallel discovery
  -> synthesis and frozen contract
  -> one implementation writer
  -> independent validator and tester
  -> user-visible outcome evidence
  -> documentation and release handoff
```

The main task remains the orchestrator and decision owner. Independent reads can
run in parallel; tracked-file implementation has one normal writer. Every
delegation carries an objective, inputs, required output, write scope, done
criterion, and escalation condition.

This is a local, skill-driven Codex workflow. It is not a scheduled-task daemon,
an external state-machine service, or the Responses API multi-agent beta.

## What's new in 2.0

Version 2.0 is the GPT-5.6-era orchestration release:

- all custom agents inherit the parent session model and reasoning selection;
  no repository file hard-pins an account entitlement
- GPT-5.6 is recommended for demanding work when available, and Ultra is an
  opt-in for complex multi-agent runs rather than an installer default
- Codex CLI `0.134.0` or newer is required and checked before installation
- stack profiles are separate, namespaced `$CODEX_HOME/*.config.toml` files
- an existing `config.toml` is preserved byte-for-byte unless you explicitly
  request `--reset-config`
- the managed global `AGENTS.md` block is updated exactly while guidance outside
  its single ordered marker pair is preserved
- agents, skills, profiles, and managed guidance are checked for exact drift
- prototype mode must prove the promised behavior end to end
- shell, Windows PowerShell 5.1, and PowerShell 7 installer regressions are part
  of the repository's CI contract

These changes fix the common “installed but not activated” failure mode caused
by an obsolete CLI on `PATH`, legacy inline profiles, or stale installed skills.
See the [2.0 research record](./docs/research/codex-5.6-local-orchestration-2026-07-10.md)
for the verified compatibility evidence.

## Runtime at a glance

| Layer | Installed runtime |
| --- | --- |
| Core agents | `researcher`, `architect`, `api_guardian`, `builder`, `validator`, `tester`, `scribe`, `github_manager` |
| Department agents | `runtime_platform`, `workflow_design`, `workspace_governance`, `quality_operations`, `docs_dx`, `ci_security_guardian` |
| Workflow skills | `$godmode-workflow`, `$godmode-prototype`, `$godmode-debug`, `$godmode-review`, `$godmode-departments` |
| Support skills | `$greenfield-bootstrap`, `$web-platforms`, `$apple-platforms`, `$flutter-dart`, `$release-manager` |
| Profiles | `godmode-swiftui`, `godmode-web`, `godmode-flutter`, `godmode-review` |
| Durable conventions | `reports/` and `state/` for evidence and resumable project context when a run needs them |

Every packaged agent inherits the parent session model and reasoning level.
Select GPT-5.6 in the parent task when it is available and the work warrants it;
use Ultra selectively when coordinated subagents add real value.

## Install and activate

First confirm that the terminal resolves a current Codex CLI:

```bash
type -a codex
codex --version
codex help doctor
```

Then install and verify on macOS or Linux:

```bash
./scripts/apply-global-codex-setup.sh
./scripts/apply-global-codex-setup.sh --check
codex doctor
```

On Windows:

```powershell
.\scripts\apply-global-codex-setup.ps1
.\scripts\apply-global-codex-setup.ps1 --check
codex doctor
```

Start a fresh Codex task after installation so global guidance and capabilities
are reloaded. The installer never updates Codex itself. If the preflight rejects
the resolved binary, update Codex deliberately and rerun it. Full diagnostics,
macOS Homebrew remediation, backup behavior, and exit codes are documented in
[Global Codex Setup](./docs/global-codex-setup.md).

## Start a run

Invoke the primary skill directly:

```text
$godmode-workflow

Goal: <goal>
Context: <repo, constraints, errors, or relevant architecture>
Done when: <observable behavior, validation command, or release result>
```

For a long task, you can use `/plan` to refine and approve the approach, then
optionally `/goal` for persistent continuation. Those commands do not replace
GodMode's gates or broaden permissions.

Use a companion skill only when the task shape calls for it:

| Skill | Use it for |
| --- | --- |
| `$godmode-debug` | reproduce, isolate, fix, and re-test a defect |
| `$godmode-review` | findings-first, read-heavy review with no edits unless requested |
| `$godmode-departments` | bounded advisory lanes for genuinely cross-domain work |
| `$greenfield-bootstrap` | repo-local governance for an empty or undocumented workspace |
| `$web-platforms` | React, Next.js, and Node.js guidance |
| `$apple-platforms` | SwiftUI, macOS, and iOS guidance |
| `$flutter-dart` | Flutter and Dart guidance |
| `$release-manager` | release impact, changelog law, and release copy |

Use `$godmode-prototype` instead of `$godmode-workflow` for a disposable,
local-only spike. Prototype output is watermarked, cannot use production data or
services, and must demonstrate its actual promised outcome before it is called
complete. Promotion returns to the full workflow.

## Stack profiles

Codex `0.134.0+` loads profiles from separate files in `$CODEX_HOME`. The
installer publishes these exact names:

```bash
codex --profile godmode-swiftui
codex --profile godmode-web
codex --profile godmode-flutter
codex --profile godmode-review
```

Profiles add focused runtime behavior such as web-search or review-output
settings. They do not select a model or reasoning level. Existing inline
`[profiles.*]` tables are reported as legacy and are not rewritten silently.

## How the team scales

**Lean lane:** the orchestrator assigns one `builder`, then `validator` and
`tester` close the quality gate.

**Guided lane:** add `researcher`, `architect`, or `api_guardian` when source
uncertainty, design risk, or a public contract needs independent attention.

**Department lane:** activate bounded runtime, workflow, governance, quality,
docs, or CI/security tracks only when ownership genuinely crosses domains.
Parallel department work is read-only by default; any write scope must be
isolated and explicit.

The orchestrator freezes scope and contracts before implementation. Completion
requires evidence for every done criterion, not merely new files, a started
process, or a generic smoke command.

## Agent roles

| Agent | Responsibility |
| --- | --- |
| `researcher` | source verification, repository discovery, and factual framing |
| `architect` | design choices, interfaces, risks, and smallest viable plan |
| `api_guardian` | API, schema, CLI, config, and compatibility review |
| `builder` | single normal implementation writer |
| `validator` | read-heavy structural and static consistency gate |
| `tester` | focused executable and runtime verification |
| `scribe` | documentation and release notes after gates pass |
| `github_manager` | branch, PR, and release framing within granted authority |

The six optional department agents are listed in the
[Agent Registry](./docs/agent-registry.md) and routed by the
[Department Model](./docs/department-orchestration.md).

## Repository map

| Path | Purpose |
| --- | --- |
| `AGENTS.md` | repository governance for this package |
| `.codex/config.toml` | repo-local technical defaults, without model pins |
| `templates/global-codex/` | source package for global guidance, config, agents, profiles, and skills |
| `templates/prototype-mode/` | local-only prototype overlay and lean config |
| `scripts/apply-global-codex-setup.sh` | macOS/Linux installer and exact checker |
| `scripts/apply-global-codex-setup.ps1` | Windows installer and exact checker |
| `scripts/check-local-env.sh` | package and environment validation |
| `scripts/test-global-codex-setup.*` | cross-platform installer regression fixtures |
| `docs/` | architecture, setup, operation, prompts, and research |
| `reports/` and `state/` | optional durable run artifacts and templates |

The packaged global runtime deliberately lives under `templates/`. Placing it
under repo-local `.codex/agents/` or `.agents/skills/` would make Codex discover
duplicate project and personal capabilities after installation.

## Safety boundaries

- repository governance is inspected before non-trivial work
- `api_guardian` reviews API, schema, CLI, config, and other contract changes
- implementation uses one normal writer; independent validation follows
- commit, push, merge, release, deploy, and other external mutations remain
  separate authority boundaries
- project reports and state are re-verified against current repository evidence
- local orchestration does not depend on hidden hooks or background scheduling

## Read next

| Need | Document |
| --- | --- |
| install, upgrade, or diagnose activation | [Global Codex Setup](./docs/global-codex-setup.md) |
| understand the orchestration contract | [Blueprint](./docs/blueprint.md) |
| inspect every installed role | [Agent Registry](./docs/agent-registry.md) |
| route larger multi-domain work | [Department Orchestration](./docs/department-orchestration.md) |
| run a disposable spike | [Prototype Mode](./docs/prototype-mode.md) |
| maintain or release this repository | [Local Development](./docs/local-development.md) |
| see shipped and future work | [Roadmap](./docs/roadmap.md) |

## Primary sources

- [Codex subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents)
- [Codex models](https://learn.chatgpt.com/docs/models)
- [Advanced configuration and profiles](https://learn.chatgpt.com/docs/config-file/config-advanced#profiles)
- [Long-running work and goals](https://learn.chatgpt.com/docs/long-running-work)
- [Build Codex skills](https://learn.chatgpt.com/docs/build-skills)
- [Codex CLI command reference](https://learn.chatgpt.com/docs/developer-commands?surface=cli)
- [Custom instructions with AGENTS.md](https://developers.openai.com/codex/guides/agents-md/)

## Contributing

Keep the public contract truthful, keep installers safe for user-owned
configuration, and keep agents, skills, profiles, docs, and checks aligned.
Follow [CONTRIBUTING.md](./CONTRIBUTING.md) and the repository's `AGENTS.md`
before changing a governed surface.
