---
name: godmode-review
description: Run a findings-first review with governance preflight, explicit evidence gathering, and no implementation unless the user asks for it.
---

# GodMode Review

Use this skill together with `godmode-workflow` for code review, architecture assessment, release-risk review, and repo understanding when the primary output is analysis.

## Required setup

- Start with governance preflight before reviewing code or release artifacts.
- Frame the request with `Goal`, `Context`, `Constraints`, and `Done when`.
- Write a report under `reports/generated/` when the review needs a durable handoff or audit trail.

## Core rules

- Findings come first, ordered by severity with file references when available.
- Do not make code changes unless the user later asks for implementation.
- Codex only spawns subagents when you explicitly ask it to. Use explicit specialist roles for evidence gathering or contract review.
- Prefer bug risk, regression risk, contract risk, and missing validation over style-only commentary.

## Default route

1. scope the review target and governing docs
2. use `researcher` for codebase mapping or source verification
3. use `architect` for design and integration risk
4. use `api_guardian` for API, schema, CLI, or config-surface review
5. use `quality_operations` when test or validation coverage needs audit
6. summarize findings, open questions, and residual risks

## Optional helpers

- `workspace_governance` for release law, repo rules, or instruction layering questions
- `docs_dx` for public docs, prompts, and setup guidance review

## Do not use when

- the user wants implementation completed now without a findings-first review lane
- the workspace lacks initial governance and needs bootstrapping first
