# Review Start Prompt

Use this for findings-first code, architecture, and release-risk review.

These prompts assume the global install has already been applied.

## Prompt

```text
$godmode-workflow
$godmode-review

GODMODE REVIEW

Goal: <system / change / problem to assess>
Context: <files, branch, PR, release, or architecture background>
Constraints: <review focus, non-goals, and whether edits are allowed>
Done when: <finding format, validation expectation, or decision needed>

Context:
- <files, diff, risks, constraints, or review focus>

Done when:
- <what the review output should contain>
```

## Best for

- code or architecture reviews
- understanding an existing repo or subsystem
- risk, scope, or integration assessments before implementation
- pre-merge or pre-release review where edits are not the default outcome

## Optional extras

- affected files or modules
- review focus such as `bugs`, `regressions`, `architecture`, or `release risk`
- whether you want analysis only or a later implementation proposal
- prepend `$web-platforms`, `$apple-platforms`, or `$flutter-dart` if stack-specific guidance should trigger immediately
- add `$godmode-departments` only for broad multi-domain architecture or release-risk reviews
- whether local workspace rules should override the global defaults
