---
name: godmode-review
description: Review code, architecture, or contracts read-only and report verified findings by severity.
---

# GodMode Core Review

This is a standalone primary mode; do not combine it with workflow, debug, or
prototype mode. The entire run is read-only.

For help or an empty task, explain this mode briefly and show a goal/done
example. With a clear task, start immediately in the user's language.

1. Freeze target, instructions, comparison base, severity model, and done
   criterion. Inspect the actual change and tests before trusting summaries.
2. Default to no subagents. Use at most two narrow read-only specialists for
   independent risks; they may not delegate again.
3. Verify every finding against code, config, command output, or governing docs.
   Reconcile duplicates and unsupported claims.
4. Report findings first by severity with tight references, then questions,
   residual risks, and coverage gaps. If none remain, say so directly.

Prioritize correctness, regression, security, contract, and missing-test risk
over style. Do not edit files or silently turn the review into a fix. A later
implementation request starts a new primary-mode contract.
