# Web Start Prompt

Use this for React, Next.js, and Node.js implementation work.

These prompts assume the global install has already been applied.

## Prompt

```text
$godmode-workflow
$web-platforms

GODMODE WEB

Goal: <goal>
Context: <app, package, route, API surface, or framework version>
Constraints: <non-goals, browser targets, compatibility requirements>
Done when: <lint, test, build, or runtime check>

Inspect the current workspace first.
Loop: research -> plan -> build -> validate.
```

## Best for

- React component work
- Next.js App Router changes
- Node.js backend or package changes
- full-stack web work where the same task crosses frontend and backend boundaries

## Optional extras

- affected app, package, or directory
- required validation command such as `pnpm lint`, `pnpm test`, or `pnpm build`
- explicit contract surface such as route handlers, `package.json` exports, or environment loading
