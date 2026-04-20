---
name: greenfield-bootstrap
description: Bootstrap a new or empty workspace so repo-local governance exists before parallel implementation starts.
---

# Greenfield Bootstrap

Use this skill when the workspace is empty, freshly initialized, or missing repo-local governance and the task is expected to grow beyond a one-file throwaway change.

## Purpose

Create the smallest local project constitution that stops global defaults from being the only active rules.

## Minimum bootstrap outputs

1. A repo-root `AGENTS.md` that defines local project rules and overrides the global defaults where needed.
2. A repo-root `README.md` or equivalent entrypoint that explains what the workspace is for.
3. One explicit home for release and documentation rules if the project will have versions, contributors, or multi-step delivery.
4. A brief statement of assumptions when stack, release model, or validation entrypoints are not fully known yet.

## Required behavior

- Do the bootstrap before parallelizing implementation.
- Keep the first pass minimal and auditable; do not generate a large policy bundle without a reason.
- If the user already implied a stack, product type, or deployment model, encode that in the local rules instead of leaving it generic.
- If versioning matters, choose one release model and document it clearly enough that later agents do not invent a second one.
- If the repo is only a temporary scratchpad or one-file utility, note that and avoid over-scaffolding.

## Suggested first-pass sequence

1. inspect the workspace shape and confirm that local governance is missing
2. capture the user goal, stack, and expected release shape
3. create repo-root `AGENTS.md`
4. create or update the minimum supporting docs needed for versioning, validation, or contributor flow
5. only then continue into normal GodMode planning and implementation
