---
name: godmode-debug
description: Reproduce, isolate, fix, and re-test a regression or runtime failure with one writer and evidence from the original failing path.
---

# GodMode Debug

This is a standalone primary mode; do not combine it with workflow, review, or
prototype mode. Keep the failing behavior as the contract.

1. Record symptom, expectation, smallest reproduction, environment, and current
   evidence. Reproduce before editing; otherwise name the proxy and gap.
2. Default to no subagents. Use `runtime_platform` or `api_guardian` only for a
   named independent uncertainty, read-only, with no further delegation.
3. Freeze one root-cause hypothesis, smallest fix scope, regression assertion,
   rollback risk, and done criterion.
4. Keep one tracked-file writer: the parent or one built-in worker.
5. Re-run the original failure path and focused regression checks. Use
   `validator` for static risk and `tester` for runtime risk; use both only when
   justified or required.
6. Close only with evidence that the original symptom is resolved. If evidence
   disproves the hypothesis, return to isolation instead of stacking fixes.
