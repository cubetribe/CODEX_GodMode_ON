# Default Start Prompt

Use this for most GodMode sessions.

These prompts assume the global install has already been applied.

## Prompt

```text
$godmode-workflow

Goal: <goal>
Context: <repo, package, branch, or relevant background>
Constraints: <non-goals, files to avoid, compatibility requirements>
Done when: <commands, expected behavior, or release output>

Context:
- <relevant files, errors, constraints, or architecture notes>

Done when:
- <what finished looks like>
```

## Best for

- new features
- scoped refactors
- setup and documentation work that still needs validation
- most repo-local work where `godmode-workflow` is enough on its own

## Optional extras

- target files or directories
- required validation command such as `pnpm test`, `xcodebuild test`, or `flutter test`
- explicit non-goals to keep scope tight
- prepend `$web-platforms`, `$apple-platforms`, or `$flutter-dart` if stack-specific guidance should trigger immediately
- local rules or release law that should govern the task
