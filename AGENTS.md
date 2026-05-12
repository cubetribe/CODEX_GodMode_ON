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

## Changelog law

- `CHANGELOG.md` under `[Unreleased]` is the only durable home for unreleased, user-relevant changes in this repo, including changes to prompts, skills, agents, templates, scripts, and setup guidance.
- `reports/generated/` is only for analysis artifacts such as discovery notes, orchestration plans, and other generated reports. It is not a release ledger and must not replace the changelog.
- `state/` is only for in-flight workflow state such as phase status, gate status, and resumable execution records. It must not be used as the human release summary.
- `scribe` writes only after the required gates pass. If a run needs both changelog text and generated reports, `CHANGELOG.md` must be updated first before any new report artifact is created.

## Validation law

- `validator` is the structural gate. It checks TOML syntax for `templates/global-codex/agents/*.toml`, Markdown consistency, internal links, and role-name consistency across `AGENTS.md`, `templates/global-codex/agents/*.toml`, and `templates/global-codex/skills/`. It does not edit source files.
- `tester` is the executable gate. It runs `./scripts/check-local-env.sh`, verifies shell-script syntax with `bash -n`, and confirms that new skills carry `name` and `description` frontmatter.
- Both gates must be explicitly recorded as pass or fail before `scribe` updates changelog text, reports, or final summary artifacts.

## Prototype mode

- `$godmode-prototype` is a local-only fast lane. It is **not** a companion to `$godmode-workflow` — it replaces it for throwaway exploration.
- Prototype output must never be committed to `main` or deployed directly. The migration checklist in the skill output is the documented path to production.
- All generated source files in prototype mode must carry the `PROTOTYPE ONLY` header comment. This is non-negotiable.
- No real credentials, production database connections, or live service endpoints may appear in prototype output.
- The prototype skill ships under `templates/global-codex/skills/godmode-prototype/`. The governance overlay and lean config ship under `templates/prototype-mode/`.
- When a prototype is promoted to production, route it through `$godmode-workflow` with the full `validator` + `tester` gate. The prototype watermarks must be removed before that run completes.

## Release impact

- Docs, structure, and example-only changes are usually `none`.
- Changes that alter recommended config behavior should be classified explicitly.
