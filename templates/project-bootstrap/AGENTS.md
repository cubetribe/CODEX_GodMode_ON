# AGENTS.md

## Project rules

- Document the project purpose and current state in the repo root.
- Keep repo-specific architecture, release rules, and user-visible contracts explicit and easy to find.
- Prefer one canonical source for versioning and release behavior. Do not let multiple files compete silently.
- Record assumptions briefly until the real project constraints are known.

## Execution flow

- Bootstrap local governance before parallel implementation work starts.
- Inspect the current workspace first and adapt these rules as the project becomes concrete.
- Before editing, report workspace root, current branch if present, touched files, and expected impact when that is not already obvious.
- Run only the checks that match the changed scope.

## Documentation and release

- Decide where the release policy lives and keep later changes aligned with it.
- Update docs when contracts, config, or operations change.
- If the project will use manual changelog entries, say so explicitly.
- If the project will use release fragments or release-managed version files, say so explicitly.

## Validation

- Keep at least one documented validation entrypoint for the current stack.
