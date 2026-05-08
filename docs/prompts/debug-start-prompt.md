# Debug Start Prompt

Use this for reproducible bugs, regressions, and failing validation paths.

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

Context:
- <error message, reproduction steps, affected path, or suspected boundary>

Done when:
- <root cause is explained and the failure is fixed or clearly isolated>
```

## Best for

- reproducible bugs
- regressions after changes
- build, test, or runtime failures
- cases where a minimal fix matters more than broad refactoring

## Optional extras

- add the exact failing command or test when one exists
- add the current stack skill such as `$web-platforms`, `$apple-platforms`, or `$flutter-dart` if it should shape the run immediately
- affected platform such as `SwiftUI`, `Next.js`, `Node.js`, or `Flutter`
- prepend `$web-platforms`, `$apple-platforms`, or `$flutter-dart` if stack-specific guidance should trigger immediately
- add `$godmode-departments` only when the bug crosses runtime, workflow, governance, docs, or validation ownership
- the command or path where the failure happens
- explicit non-goals so the fix stays narrow
- any versioning, contract, or rollout docs that the fix must preserve
