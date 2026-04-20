# Web Start Prompt

Use this for React, Next.js, and Node.js implementation work.

These prompts assume the global install has already been applied.

## Prompt

```text
$godmode-workflow
$web-platforms

Goal: <goal>

Context:
- <affected app, package, validation command, or contract surface>

Done when:
- <what finished looks like>
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
- add `$godmode-debug` or `$godmode-review` if the run is primarily debugging or assessment rather than implementation
- any release, versioning, or governance docs that the change must obey
