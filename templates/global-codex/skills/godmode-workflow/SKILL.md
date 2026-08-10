---
name: godmode-workflow
description: Deliver non-trivial implementation or migration work with a frozen scope, one writer, risk-based validation, and outcome evidence.
---

# GodMode Workflow

Apply repository instructions first. This is a primary mode; do not combine it
with debug, review, or prototype mode in the same run.

1. Inspect governance, workspace state, release law, and the real changed
   surface. State goal, scope, done criteria, assumptions, and external-action
   boundaries.
2. Resolve only material unknowns. Default to no subagents. Use at most two
   narrow specialists when independent work materially improves the result;
   advisory roles are read-only, while `tester` may create only disposable
   tool output. Never ask specialists to delegate again.
3. Freeze the change contract: files or interfaces, compatibility decisions,
   risks, validation, rollback, and user-visible evidence. Ask before any
   material scope or authority expansion.
4. Keep one tracked-file writer: the parent or one built-in worker. Stop and
   refreeze if implementation exposes a contract gap.
5. Run validation proportional to risk. `validator` owns static structure;
   `tester` owns executable behavior. Use both only for migrations, security or
   release-critical changes, or when repository law requires both.
6. Map each done criterion to actual command output, test results, or observed
   behavior. Report residual risk and anything not verified.
7. Update required docs and unreleased notes before final gates. Treat commit,
   push, merge, release, deploy, and other external mutations as separate
   authority boundaries.

Every delegation states objective, inputs, expected output, write boundary,
done criterion, and escalation condition.
