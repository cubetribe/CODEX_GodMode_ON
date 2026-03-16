---
name: flutter-dart
description: Apply conservative best practices for Flutter and Dart work, including composable widgets, explicit state boundaries, and focused analyze/test runs.
---

# Flutter and Dart

Use this skill when working in Flutter or Dart repositories.

## Working rules

- Keep widgets small, composable, and easy to reason about.
- Keep business logic out of `build` methods.
- Default to a clear split between UI and data layers.
- In UI, prefer views plus view-model-like state holders when the project needs indirection.
- In data, keep repositories and services separate, with repositories as the source of truth.
- Use abstract repositories when multiple implementations or environments are likely.
- Follow the project's existing state-management approach instead of mixing paradigms casually.
- Prefer unidirectional data flow.
- Use `const` constructors and immutable data where it is natural and already supported by the code.
- Keep platform-specific behavior explicit when code spans iOS, Android, desktop, or web.
- Treat formatting and analyzer output as part of correctness, not cosmetic cleanup.

## Validation

- run `dart format` or `flutter format` if the repo expects it
- run `dart analyze` for Dart packages
- run `flutter analyze` for Flutter code
- run focused `flutter test` or `dart test` commands for the changed area
- use integration tests for end-to-end behavior when the repo has them

## Watch for

- async work triggered repeatedly from widget build paths
- overly broad `setState` or state updates that are hard to trace
- UI widgets that absorb domain logic
- repositories depending directly on other repositories
- plugin calls directly inside code that should stay easy to test
- assuming `dart:io` is available for web targets
- generated or platform files changed without a clear reason
