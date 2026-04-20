# Default Start Prompt

Use this for most GodMode sessions.

These prompts assume the global install has already been applied.

## Prompt

```text
$godmode-workflow

Goal: <goal>

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

- add `$godmode-departments` for multi-domain work that needs explicit routing and write-scope control
- add `$godmode-debug` when the task is mainly bug-fixing or failure isolation
- add `$godmode-review` when the task is mainly findings-first analysis
- add `$greenfield-bootstrap` if the workspace is empty or still lacks repo-local governance
- add `$web-platforms`, `$apple-platforms`, or `$flutter-dart` only when stack-specific guidance should shape the run immediately
- include a validation command, explicit non-goals, or release-policy references only when they materially change the task
