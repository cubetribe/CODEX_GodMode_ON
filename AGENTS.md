# AGENTS.md

## Project rules

- This repository documents practical Codex setup patterns for individuals and teams.
- Prefer current official OpenAI Codex documentation when changing setup guidance or product claims.
- Keep repo guidance small, explicit, and easy to audit.
- Use `AGENTS.md` for durable repo rules, `.codex/config.toml` for repo defaults, and `.agents/skills/` for reusable workflows.
- Do not add speculative guidance about Codex features without a source or a clear note that it is an inference.

## Documentation rules

- Favor short, working examples over long theory.
- Call out when the official docs are explicit and when a conclusion is an inference from those docs.
- If OpenAI changes a path or feature name, update examples to match the current docs.

## Validation

- For docs-only changes, verify paths, links, and structural consistency.
- For new example skills, keep metadata concise and descriptions triggerable.

## Release impact

- Docs, structure, and example-only changes are usually `none`.
- Changes that alter recommended config behavior should be classified explicitly.
