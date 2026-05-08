# Reports

This directory is for persistent agent handoffs and locally reproducible reports.

## Recommended use

- versioned example or reference reports may stay in the repository
- generated runtime reports should go under `reports/generated/`
- reports should summarize decisions, evidence, and next routing steps
- do not store secrets, full chat transcripts, or unrelated logs

## Convention

- `reports/generated/NN-role-report.md`
- short, concrete summaries instead of full chat transcripts

## Suggested report shape

```md
# <date> <role> Report

## Scope

What was reviewed or changed.

## Findings

Facts, risks, or decisions that matter for the parent workflow.

## Validation

Commands run, results, and gaps.

## Handoff

Recommended next role or action.
```
