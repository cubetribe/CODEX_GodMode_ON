---
name: godmode-review
description: Perform a findings-first code, architecture, contract, or release-risk review with bounded read-only specialists and evidence-backed severity. Use when the requested outcome is assessment rather than implementation.
---

# GodMode Review

Use this skill with `$godmode-workflow` while keeping the review read-only.

## Review route

1. Freeze the target, governing instructions, comparison base, severity model,
   and review done criterion.
2. Inspect the actual change and relevant tests before relying on summaries.
3. Delegate independent read-only lanes in parallel when authorized and useful:
   `architect` for integration risk, `api_guardian` for compatibility surfaces,
   `quality_operations` for validation gaps, and focused specialists as needed.
4. Require each delegation to declare objective, inputs, output, `read-only`
   scope, done criterion, and escalation condition.
5. Reconcile overlapping findings and verify each against code, config, command
   output, or governing documentation.
6. Report findings first, ordered by severity, with tight file or line
   references. Then report questions, residual risks, and coverage gaps.

Prioritize correctness, regression, security, contract, and missing-test risk
over style-only preferences. If no actionable findings remain, say so directly
and identify what was not verified.

Do not edit files or silently turn the review into a fix. If the user requests
implementation, return to `$godmode-workflow`, freeze a write scope, obtain any
material user gate, and assign one writer.
