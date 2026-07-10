# Default Start Prompt

Use this after the global runtime is installed and a fresh Codex task is open.

## Prompt

```text
$godmode-workflow

Goal: <goal>

Context:
- <repo, branch, errors, architecture, or relevant files>

Constraints:
- <non-goals, files to avoid, compatibility, or authority boundaries>

Done when:
- <observable behavior>
- <focused validation command or artifact>
- <release output, if already authorized>
```

## Best for

- features and scoped refactors
- setup, migration, and documentation work that needs validation
- compatibility changes involving API, schema, CLI, or config surfaces
- release preparation with explicit GitHub authority

For a long task, use `/plan` first to refine and approve the approach, then
optionally `/goal` for persistent continuation. The GodMode gates and permission
boundaries still apply.

## Useful additions

- required validation such as `pnpm test`, `xcodebuild test`, or `flutter test`
- explicit write scopes or protected files
- repo-local release law and branch protection
- `$web-platforms`, `$apple-platforms`, or `$flutter-dart` when stack guidance
  should shape the run
- GPT-5.6 selected in the parent session when available for demanding work;
  Ultra only when complex multi-agent coordination justifies it
