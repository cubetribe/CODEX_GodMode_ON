# Greenfield Start Prompt

Use this for empty folders, new repositories, or projects that do not yet have local governance.

These prompts assume the global install has already been applied.

## Prompt

```text
$godmode-workflow
$greenfield-bootstrap

Goal: <project to start>

Context:
- <stack, repo shape, release model, or initial constraints>

Done when:
- <repo-local governance exists and the first safe implementation step is clear>
```

## Best for

- empty project folders
- brand-new repositories
- first-pass setup before multiple agents work in parallel
- imported codebases that still lack repo-root rules

## Optional extras

- target stack such as `Next.js`, `SwiftUI`, `Flutter`, or `Node.js`
- expected release model such as manual changelog or change fragments
- initial validation command
- non-goals so the bootstrap stays minimal
