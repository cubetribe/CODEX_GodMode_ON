---
name: godmode-debug
description: Reproduce, isolate, fix, and re-test regressions or runtime failures with bounded evidence gathering, one implementation writer, and outcome-based verification. Use with godmode-workflow when a failure needs diagnosis before repair.
---

# GodMode Debug

Use this skill with `$godmode-workflow`. Keep the failing behavior as the
primary contract from discovery through verification.

## Debug route

1. Capture the symptom, expected behavior, smallest reproduction, environment,
   and current evidence.
2. Reproduce before proposing a fix. If direct reproduction is impossible, use
   the closest deterministic proxy and state the gap.
3. Delegate independent read-only investigations in parallel when authorized
   and useful. Use `runtime_platform` for toolchain or OS behavior and
   `researcher` for source or repository evidence.
4. Synthesize one root-cause hypothesis and freeze the fix scope, regression
   assertion, rollback risk, and done criterion. Obtain a user gate if the fix
   materially changes the approved plan or contract.
5. Assign one `builder` the smallest safe fix. Do not parallelize tracked-file
   writes.
6. Run `validator` and `tester` independently against the original failing path
   and the surrounding regression surface.
7. Close only when the original symptom is resolved and the user-visible done
   criterion has concrete evidence. A created file or started process alone is
   not proof.

Every delegated task must declare objective, inputs, required output, write
scope, done criterion, and escalation condition as defined by
`$godmode-workflow`.

If evidence disproves the hypothesis, return to isolation with the new facts;
do not stack speculative fixes.
