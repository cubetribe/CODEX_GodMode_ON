# GPT-5.6-Era Codex Local Orchestration Research

Date: 2026-07-10

Status: implemented for 2.0.0; local shell gates passed, Windows CI is a release gate

## Executive conclusion

The original activation problem came from three independent compatibility
layers drifting apart:

1. the terminal resolved an obsolete Codex CLI (`0.27.0`) before a current
   desktop-bundled CLI
2. the 1.1 package installed inline `[profiles.*]` tables that Codex `0.134.0+`
   no longer loads as named profiles
3. four installed GodMode skills differed from the repository package while the
   released checker compared names instead of complete skill directories

GPT-5.6 is a model family, not a Codex software version. Version 2.0 therefore
lets packaged agents inherit the parent task's model and reasoning selection,
recommends GPT-5.6 for demanding work when an account supports it, and keeps
Ultra an explicit choice for complex multi-agent runs.

## Verified Codex facts

| Surface | Verified behavior | 2.0 decision |
| --- | --- | --- |
| GPT-5.6 | model family for current demanding work; availability varies by account | recommend it at the parent task, never hard-pin entitlement |
| Reasoning | deeper reasoning and multi-agent coordination trade latency and token use for capability | document Ultra as opt-in, not a package default |
| Subagents | stable; direct requests, applicable project guidance, and active skills can authorize delegation | replace the stale “explicit request only” claim |
| Agent limits | bounded thread and depth settings are available | retain `max_threads = 6` and `max_depth = 1` |
| Profiles | Codex `0.134.0+` loads `--profile NAME` from `$CODEX_HOME/NAME.config.toml` | ship four separate namespaced profile files |
| Long runs | `/plan` refines work and `/goal` can persist approved work without expanding permissions | document `/plan`, then optional `/goal` |
| Diagnostics | `codex doctor` and `codex update` are stable current commands | preflight version and doctor capability; never silently update Codex |
| Skills | `$skill` invocation and description matching are supported; `agents/openai.yaml` adds UI metadata | make the primary workflow concise, triggerable, and discoverable |
| Hooks | command hooks can enforce trusted mechanical policy | do not make hooks responsible for orchestration spawning |

## Historical pre-implementation evidence

The following snapshot explains why 2.0 was necessary; it is not the current
package state:

- repository `cubetribe/CODEX_GodMode_ON` was at `ce76f07`, version `1.1.0`
- six pre-existing modified files contained an unfinished installer-preservation
  attempt
- `/opt/homebrew/bin/codex` reported `codex-cli 0.27.0`
- `/Applications/ChatGPT.app/Contents/Resources/codex` reported
  `0.144.0-alpha.4`; the Homebrew cask and npm package reported `0.144.1`
- the global user config selected a GPT-5.6 variant with Ultra, while the repo
  config overrode it with GPT-5.5/high
- all 14 installed agent manifests matched the package, but
  `godmode-workflow`, `godmode-departments`, `godmode-debug`, and
  `godmode-review` differed from their package source
- divergent installed skills referenced non-portable concepts such as
  `enable_write_tools`, `request_feedback`, and an undefined conversation
  artifact directory
- the 1.1 checker inspected skill frontmatter only and falsely reported that
  runtime as current
- the unfinished TOML section merge reproduced data loss for multiline root
  values and quoted keys, downgraded model/reasoning values, and mishandled
  malformed `AGENTS.md` markers

## Implemented 2.0 orchestration loop

```text
governance and capability preflight
  -> bounded parallel read-only discovery
  -> synthesis, contract review, and frozen write scope
  -> one implementation writer
  -> independent structural validator and executable tester
  -> done-criterion outcome evidence
  -> documentation and release handoff
  -> separately authorized external actions
```

Every delegated task states six fields: objective, inputs and governing
instructions, required output, write scope, done criterion, and escalation
condition. Parallel reads are the normal optimization. Parallel writes require
genuinely isolated ownership and are not the default.

Completion is based on the user's observable outcome, not merely file presence,
process startup, or a generic smoke command. That change directly addresses the
prototype failure reported in GitHub issue #20, where structure existed but the
promised experience did not work end to end.

## Implemented activation contract

1. The installer leaves an existing user `config.toml` byte-for-byte unchanged
   unless `--reset-config` is explicit.
2. Four managed profiles are installed as separate
   `godmode-*.config.toml` files; conflicting managed profiles fail before
   writes unless reset is explicit.
3. Every custom agent inherits the parent model and reasoning selection.
4. Global `AGENTS.md` requires one ordered managed marker pair, migrates the
   known v1.1 template without duplication, and preserves custom guidance.
5. The checker compares each current GodMode-owned agent, skill, profile, and
   managed guidance block exactly while leaving unrelated user assets alone.
6. The resolved Codex executable must meet version `0.134.0` and doctor-command
   capability requirements before installation.
7. Backups use a unique per-run archive outside live discovery roots.
8. A successful installation is followed by exact verification, `codex doctor`,
   and a fresh task so global capabilities are reloaded.

## Validation outcome

The macOS/Linux installer regression fixture passed all 12 maintained groups,
including complex byte-preservation, profile conflict/reset, known v1.1 and
custom guidance migration, malformed-marker preflight, exact drift repair,
idempotence, and documented argument/runtime exit codes.

Repository validation, Bash syntax, ShellCheck, and `git diff --check` passed
for the implementation handoff. The PowerShell fixture mirrors the critical
cases; the GitHub workflow runs it under Windows PowerShell 5.1 and PowerShell 7
before the release can be considered platform-green. No local macOS result is
presented as proof of Windows execution.

## Boundaries

- local Codex subagents are not the Responses API multi-agent beta
- GodMode is a skill-driven local workflow, not a daemon or scheduled task
- model and Ultra availability, latency, and token use vary by account and task
- hooks do not own the orchestration lifecycle
- commit, push, merge, release, deploy, and other external mutations remain
  separate authority boundaries

## Primary sources

- [Codex subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents)
- [Codex models](https://learn.chatgpt.com/docs/models)
- [Advanced configuration: profiles](https://learn.chatgpt.com/docs/config-file/config-advanced#profiles)
- [Long-running work and goals](https://learn.chatgpt.com/docs/long-running-work)
- [Build Codex skills](https://learn.chatgpt.com/docs/build-skills)
- [Codex hooks](https://learn.chatgpt.com/docs/hooks)
- [Codex CLI command reference](https://learn.chatgpt.com/docs/developer-commands?surface=cli)
- [Codex CLI 0.144.1 release](https://github.com/openai/codex/releases/tag/rust-v0.144.1)
- [GPT-5.6 prompt guidance](https://developers.openai.com/api/docs/guides/prompt-guidance-gpt-5p6.md)
- [Codex changelog](https://developers.openai.com/codex/changelog)
