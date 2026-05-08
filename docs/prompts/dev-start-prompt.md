# Dev Start Prompt

Use this for implementation work.

These prompts assume the global install has already been applied.

## Prompt

```text
$godmode-workflow

GODMODE DEV

Goal: <goal>
Context: <repo, package, branch, or relevant background>
Constraints: <non-goals, files to avoid, compatibility requirements>
Done when: <commands, expected behavior, or release output>

Inspect the current workspace first.
Loop: research -> plan -> build -> validate.
```

## Best for

- new features
- scoped refactors
- setup and documentation work that still needs validation

## Optional extras

- target files or directories
- required validation command such as `pnpm test`, `xcodebuild test`, or `flutter test`
- explicit non-goals to keep scope tight
- prepend `$web-platforms`, `$apple-platforms`, or `$flutter-dart` if stack-specific guidance should trigger immediately
- local rules or release law that should govern the task
