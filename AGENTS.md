# AGENTS.md

## Project rules

- This repository documents and packages the globally installable GodMode runtime for Codex.
- This repository is `main`-first. Do not create or switch to feature branches unless the user explicitly asks for one.
- Prefer current official OpenAI Codex documentation when changing setup guidance or product claims.
- Keep repo guidance explicit, auditable, and clearly separated from future implementation work.
- Use `AGENTS.md` for durable repo rules, `.codex/config.toml` for repo defaults, `.codex/agents/` for the canonical GodMode custom agents, and `.agents/skills/` for the canonical GodMode reusable procedures.
- Do not add speculative guidance about Codex features without a source or a clear note that it is an inference.
- If the original Claude repository is referenced, distinguish between extracted facts from the source repo and new Codex design decisions.
- Keep `.codex/agents/`, `.agents/skills/`, installer behavior, and docs aligned when role names or workflow gates change.

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

- `validator` is the structural gate. It checks TOML syntax for `.codex/agents/*.toml`, Markdown consistency, internal links, and role-name consistency across `AGENTS.md`, `.codex/agents/*.toml`, and `.agents/skills/`. It does not edit source files.
- `tester` is the executable gate. It runs `./scripts/check-local-env.sh`, verifies shell-script syntax with `bash -n`, and confirms that new skills carry `name` and `description` frontmatter.
- Both gates must be explicitly recorded as pass or fail before `scribe` updates changelog text, reports, or final summary artifacts.

## Release impact

- Docs, structure, and example-only changes are usually `none`.
- Changes that alter recommended config behavior should be classified explicitly.
