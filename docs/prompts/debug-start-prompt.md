# Debug Start Prompt

Use this for bug fixing and fault isolation.

## Prompt

```text
GODMODE DEBUG

Goal: <bug / symptom / expected result>

Use repo workflow, available tools, agents, and skills.
Loop: reproduce -> isolate -> fix -> re-test.
Use subagents when useful.
Stay on the failing path until green.
```

## Best for

- reproducible bugs
- regressions after changes
- build, test, or runtime failures

## Optional extras

- exact error message
- reproduction steps
- affected platform such as `SwiftUI`, `Next.js`, `Node.js`, or `Flutter`
