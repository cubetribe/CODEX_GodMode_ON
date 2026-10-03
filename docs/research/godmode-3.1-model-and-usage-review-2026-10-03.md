# GodMode 3.1: model, usage, and update review

Reviewed on 2026-10-03. This is a design decision record, not a benchmark.

## Evidence and decision

The user's desktop screenshot shows `/god` opening a skill picker containing
Workflow, Debug, Review, Prototype, optional Paperwork, and the retired
Departments skill. We inspected the screenshot locally; it is not copied into
the repository. The installed workflow still contains the pre-3.0 generic role
chain. A read-only local comparison found the seven retired agents and the
Departments skill matching the immutable 2.0 fixtures, with no installed 3.0
inventory. This supports the inference that the global installer was not
applied to this installation after the repository update.

[OpenAI's Astra skill guidance](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra)
recommends narrow descriptions and revisiting accumulated instructions.
[GPT-6 prompting guidance](https://developers.openai.com/api/docs/guides/latest-model#prompting-best-practices)
identifies approval pauses, instruction sensitivity, delegation behavior, and
overbroad testing as areas to control. The model-family guidance includes
GPT-6 Astra and GPT-6.1 Sol; it recommends evaluating prompts with the selected
model and workload rather than assuming identical behavior.

[Codex best practices](https://learn.chatgpt.com/guides/best-practices)
recommends a goal, context, constraints, and observable completion. It currently
recommends Sol 6.1 when available with the client's default effort, and Light
(`low`) as an Astra starting point. GodMode does not impose either selection.
[Skills documentation](https://learn.chatgpt.com/docs/skills-and-plugins)
documents explicit Codex `$` skill mentions. The `/god` menu route is an observed
desktop interaction, not a claimed built-in slash command.

Inference: the short 3.0 parent contract, optional specialists, one writer, and
risk-based gates remain a defensible baseline for both requested models. We
retain the seven agents and add concise conditional help, narrower discovery
descriptions, continuation of authorized work, and a stop rule for broadening
tests. Help and Update load only when relevant; they are not companion chains.

## Installation contract

The existing installer removes exact 2.0 retired files safely. Two real gaps
remain: original 1.x variants have different hashes, and the alternate global
skill root is not checked. 3.1 adds immutable historical variants, a cumulative
hash ledger, both-root detection, version/source/skills-root installation
records, and an offline-capable read-only audit. Active package replacement
continues to back up and overwrite managed names; user config remains preserved.
Modified retired data stops before writes. Local records locate installations;
they never grant deletion authority. Future retirements require explicit ledger
entries and immutable fixtures, including every supported released variant.

## Limits and validation

Deterministic routing fixtures prove prompt/metadata consistency, not actual
model delegation. Static, installer, audit, and isolated discovery tests prove
their respective package surfaces. Windows behavior requires Windows CI.
No new live Astra or Sol 6.1 behavioral benchmark was run for this update; we
make no claim of measured optimality, token savings, latency, or superior task
quality. Historical 5.6 release evidence remains historical.

Local capability evidence: the PATH CLI is 0.144.1 and correctly fails the
installer's 0.147.0 floor before writes. The current desktop bundles
`codex-cli/bin/codex` at 0.159.0-alpha.12.1; the isolated discovery/profile test
passes with that explicitly selected binary. This proves discovery and parsing
on that client, not stable Windows compatibility or live model quality.

Before making model-specific performance claims, run the same representative
implementation, failure reproduction, and review tasks with both requested
models, record client/model/effort/revision, and inspect actual role binding,
authority boundaries, tool results, completion, and unnecessary pauses.
