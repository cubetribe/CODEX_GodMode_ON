---
name: web-platforms
description: Apply conservative best practices for React, Next.js, and Node.js work, including explicit client boundaries, server-first data flow, and focused validation.
---

# Web Platforms

Use this skill when working in React, Next.js, or Node.js repositories.

## Working rules

- Prefer the framework's existing routing, rendering, and data-fetching patterns over introducing parallel ones.
- In Next.js App Router codebases, prefer Server Components by default and keep Client Component boundaries explicit and as narrow as possible.
- In Server Components, fetch data from the real source when possible instead of calling your own Route Handlers.
- Keep server-only code out of client bundles.
- Keep React components and hooks pure during render.
- Prefer deriving data during render over using effects for normal data flow.
- In Node.js services, keep module boundaries explicit and configuration loading centralized.
- For packages, treat `package.json` public entry points as an API surface and handle `exports` changes cautiously.
- Avoid hidden global state, silent environment assumptions, and broad side effects during module import.
- Detect the real package manager from lockfiles before running commands.

## Validation

- prefer the repo's own scripts first
- typical order is lint -> typecheck -> test -> build when those scripts exist
- scope commands to the changed package or app where possible
- keep React hooks lint rules enabled when the repo uses ESLint

## Watch for

- unnecessary client components
- mixing server code into browser paths
- fetching from your own Route Handlers inside Server Components
- effects that only mirror or derive existing state
- user-visible output changes that skip snapshot or integration review
- environment variables that are read ad hoc across the codebase
- broad dependency or config changes for a narrow fix
