---
name: apple-platforms
description: Apply conservative best practices for SwiftUI work on macOS and iOS, including state flow, target-safe changes, and focused Xcode validation.
---

# Apple Platforms

Use this skill when working in SwiftUI codebases for macOS or iOS.

## Working rules

- Keep views small and composable.
- Keep a single source of truth and store state in the least common ancestor that actually needs it.
- Use `@State` for transient UI state, not as a persistence layer.
- Pass mutable state through `Binding` when a child edits parent-owned state.
- Share broader observable model data through environment-based injection when the project already uses that pattern.
- Prefer current Observation APIs when the project baseline supports them, but do not force a migration when deployment targets or toolchains still require older patterns.
- Keep business logic and side effects out of large `body` implementations.
- Preserve previews when the project already uses them.
- Follow the observation and data-flow system already used by the project instead of mixing patterns casually.
- Be explicit about platform differences between macOS and iOS.
- Treat concurrency and main-thread UI updates as correctness concerns, not style issues.

## Validation

- use `xcodebuild -list` first if the scheme or destination is unclear
- prefer targeted `xcodebuild build` or `xcodebuild test` commands over broad guesses
- keep validation scoped to the touched target when possible

## Watch for

- state duplication across view, view model, and model layers
- heavy logic in views
- accidental preview breakage
- platform-specific code moved into shared files without checking the target impact
- unreviewed concurrency changes around UI updates
