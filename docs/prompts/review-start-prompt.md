# Review Start Prompt

Use this for analysis, review, and architecture assessment.

## Prompt

```text
GODMODE REVIEW

Goal: <system / change / problem to assess>

Use repo workflow, available tools, agents, and skills.
Loop: inspect -> analyze -> verify -> report.
Use subagents when useful.
Findings first. No code changes unless asked.
```

## Best for

- code or architecture reviews
- understanding an existing repo or subsystem
- risk, scope, or integration assessments before implementation

## Optional extras

- affected files or modules
- review focus such as `bugs`, `regressions`, `architecture`, or `release risk`
- whether you want analysis only or a later implementation proposal
