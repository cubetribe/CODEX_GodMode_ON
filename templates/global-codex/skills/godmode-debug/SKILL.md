---
name: godmode-debug
description: Reproduce a failure, isolate its cause, fix it, and verify the original path.
---

# GodMode Debug

This is a standalone primary mode; do not combine it with workflow, review, or
prototype mode. Keep the failing behavior as the contract.

For help or an empty task, explain this mode briefly and show a goal/done
example. With a clear task, start immediately in the user's language.

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
