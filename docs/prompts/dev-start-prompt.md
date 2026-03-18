# Dev Start Prompt

Use this for implementation work.

## Prompt

```text
GODMODE DEV

Goal: <goal>

Use repo workflow, available tools, agents, and skills.
Loop: research -> plan -> build -> validate.
Use subagents when useful.
Keep changes minimal. Verify before push.
```

## Best for

- new features
- scoped refactors
- setup and documentation work that still needs validation

## Optional extras

- target files or directories
- required validation command such as `pnpm test`, `xcodebuild test`, or `flutter test`
- explicit non-goals to keep scope tight
