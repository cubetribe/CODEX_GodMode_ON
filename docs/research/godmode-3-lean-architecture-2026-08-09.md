# Research Rationale: GodMode 3 Lean

Date: 2026-08-09

Status: decision record for the unreleased 3.0 candidate. Social-media sources
are anecdotal signals, not architectural authority.

## Question

Which persistent orchestration rules still improve delivery with GPT-5.6
Sol/Ultra, and which mainly increase context, child turns, and duplicated work?

## Evidence hierarchy

1. current official OpenAI product and prompting documentation;
2. empirical studies with described datasets and methods;
3. Reddit/X reports used only to generate or corroborate local test hypotheses;
4. reproducible behavior of this repository and the locally installed CLIs.

## Official guidance

OpenAI's [latest-model prompting guidance](https://developers.openai.com/api/docs/guides/latest-model)
argues for leaner instructions with strong models: keep domain context, hard
constraints, approval boundaries, and success criteria, while avoiding
unnecessary process prescription. Its internal coding-agent ablation reports
roughly 10–15% higher quality, 41–66% fewer total tokens, and 33–67% lower cost
with a leaner system prompt. OpenAI presents these as directional results to
revalidate on one's own workload, not a universal guarantee.

The official [Codex subagents documentation](https://learn.chatgpt.com/docs/agent-configuration/subagents)
states that subagent runs use more tokens than comparable single-agent work and
are best suited to independent, read-heavy investigation or context isolation.
It also provides built-in roles such as `explorer` and `worker` and recommends
that custom agents be narrow and opinionated. This weakens the case for generic
permanent Researcher, Architect, and Builder duplicates.

[Skills guidance](https://learn.chatgpt.com/docs/build-skills) describes
progressive disclosure: Codex first sees skill metadata and loads full
instructions when the skill activates. The architectural consequence is small,
independent mode and stack skills instead of a global all-stack handbook or an
automatic chain of companion skills.

The [configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference)
names `agents.max_concurrent_threads_per_session` as the current field and
`max_threads` as a legacy alias. It does not document `max_depth` as a current
agent limit. The 3.0 package therefore removes depth claims. A local
compatibility test found that desktop Codex `0.147.0-alpha.1.2` accepts the new
field, while stable Homebrew Codex `0.144.1` rejects it and accepts the alias.
The package temporarily uses `max_threads = 2` and records that as an empirical
compatibility exception.

## Empirical studies

The ETH Zürich paper
[Evaluating AGENTS.md: Are Repository-Level Context Files Helpful for Coding Agents?](https://arxiv.org/abs/2602.11988)
evaluates 138 issues from twelve repositories. Its reported comparisons show
that added context files raised inference cost and step counts without a
reliable average correctness improvement; automatically generated context was
particularly unhelpful. The most transferable result is that persistent files
should contain minimal, non-discoverable requirements rather than an entire
development playbook.

A smaller supporting study,
[Do Context Files Help Coding Agents?](https://arxiv.org/abs/2607.27250), reports
no measurable correctness improvement across its more limited multi-agent
ablation. Its sample is too small to settle the question, but it supports local
A/B measurement instead of assuming more instructions are safer.

## Community signals

Reddit reports such as
[Excessive token consumption. Resolved?](https://www.reddit.com/r/codex/comments/1v3x1s4/excessive_token_consumption_resolved/)
describe lower consumption after limiting subagents, reusing threads, and
reducing fork context. Another thread,
[Ultra and subagents will burn tokens](https://www.reddit.com/r/codex/comments/1usiwqw/psa_and_workaround_ultra_and_subagents_will_burn/),
warns that inherited high effort across child agents can multiply quota use.
These are individual experiences and may include transient product behavior;
they justify measuring child turns and effort inheritance, not encoding the
posts as universal rules.

The X discussion around the ETH result, for example
[this summary](https://x.com/Saboo_Shubham_/status/2026134519317934393), shows
strong community interest in minimal human-authored context. A separate
[context-rot discussion](https://x.com/carlosvillu/status/2025967908443050337)
argues that large available windows do not make irrelevant context free. Both
are treated only as practice signals because the posts are not independent
controlled evidence.

## Repository audit findings

GodMode 2.0 had 14 custom agents, ten skills, a 4,502-byte global prompt, a
4,824-byte workflow skill, mandatory validator/tester semantics, and a writing
Scribe after both gates. That last sequence meant the validated diff was not
necessarily the final diff. The aggregate local check also executed the Unix
installer suite, and CI executed the same suite again.

The useful invariants were much smaller:

- read applicable governance and preserve unrelated work;
- clarify authority, write scope, and observable done criteria;
- keep one writer;
- delegate only independent work with material benefit;
- validate the final state according to risk;
- treat commit, push, release, deploy, and other external mutations separately.

## Decision

The 3.0 candidate keeps those invariants and adopts:

- zero-subagent default, at most two selected specialists, packaged-base
  concurrency two, no recursive delegation;
- parent or one built-in worker as writer;
- seven narrow optional custom agents;
- four exclusive primary modes and five support/stack skills;
- static Validator versus executable Tester boundaries;
- deterministic checks for syntax, links, metadata, rosters, and migrations;
- state only for long, paused, or handed-off work;
- hash-matched, recoverable removal of retired 2.0 assets.

This is a justified architecture change, not proof that every lean run is
better. Final release readiness still requires repository-specific installer,
discovery, routing, Windows, and live model evidence.
