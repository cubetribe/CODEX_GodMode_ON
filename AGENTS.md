# AGENTS.md

## Project rules

- This repository documents the blueprint for a Codex-native port of `ClaudeCode_GodMode-On`.
- This repository is `main`-first. Do not create or switch to feature branches unless the user explicitly asks for one.
- Prefer current official OpenAI Codex documentation when changing setup guidance or product claims.
- Keep repo guidance explicit, auditable, and clearly separated from future implementation work.
- Use `AGENTS.md` for durable repo rules, `.codex/config.toml` for repo defaults, `.codex/agents/` for future custom agent definitions, and `.agents/skills/` for reusable procedures.
- Do not add speculative guidance about Codex features without a source or a clear note that it is an inference.
- If the original Claude repository is referenced, distinguish between extracted facts from the source repo and new Codex design decisions.
- Keep `.codex/agents/`, `.agents/skills/`, and docs aligned when role names or workflow gates change.

## Documentation rules

- Favor concise explanations, but do not collapse away the core orchestration logic.
- Call out when the official docs are explicit and when a conclusion is an inference from those docs.
- Keep the "current repo state" separate from the "target architecture" so readers do not confuse the blueprint with an implemented system.
- If OpenAI changes a path or feature name, update examples to match the current docs.

## Validation

- For docs-only changes, verify paths, links, structural consistency, and that role names stay consistent across files.
- For new example skills, keep metadata concise and descriptions triggerable.
- For runtime-scaffolding changes, run `./scripts/check-local-env.sh`.

## Release impact

- Docs, structure, and example-only changes are usually `none`.
- Changes that alter recommended config behavior should be classified explicitly.
