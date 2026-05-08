# Debug Start Prompt

Use this for bug fixing and fault isolation.

These prompts assume the global install has already been applied.

## Prompt

```text
$godmode-workflow
$godmode-debug

GODMODE DEBUG

Goal: <bug / symptom / expected result>
Context: <where it fails, recent change, environment, or affected user flow>
Constraints: <non-goals or files to avoid>
Done when: <re-test command and expected passing signal>

Inspect the current workspace first.
Loop: reproduce -> isolate -> fix -> re-test.
```

## Best for

- reproducible bugs
- regressions after changes
- build, test, or runtime failures

## Optional extras

- exact error message
- reproduction steps
- affected platform such as `SwiftUI`, `Next.js`, `Node.js`, or `Flutter`
- prepend `$web-platforms`, `$apple-platforms`, or `$flutter-dart` if stack-specific guidance should trigger immediately
- add `$godmode-departments` only when the bug crosses runtime, workflow, governance, docs, or validation ownership
- the command or path where the failure happens
