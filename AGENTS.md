# AGENTS.md

## Project rules

- This repository documents and packages the globally installable GodMode runtime for Codex.
- This repository is `main`-first. Do not create or switch to feature branches unless the user explicitly asks for one.
- Prefer current official OpenAI Codex documentation when changing setup guidance or product claims.
- Keep repo guidance explicit, auditable, and clearly separated from future implementation work.
- Use `AGENTS.md` for durable repo rules, `.codex/config.toml` for repo defaults, `templates/global-codex/agents/` for packaged GodMode custom agents, and `templates/global-codex/skills/` for packaged GodMode reusable procedures.
- Do not keep the packaged global GodMode agents or skills in repo-local discovery paths such as `.codex/agents/` or `.agents/skills/`; after global installation that creates duplicate project and personal entries in Codex.
- Do not add speculative guidance about Codex features without a source or a clear note that it is an inference.
- If the original Claude repository is referenced, distinguish between extracted facts from the source repo and new Codex design decisions.
- Keep `templates/global-codex/agents/`, `templates/global-codex/skills/`, installer behavior, and docs aligned when role names or workflow gates change.

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
