---
name: godmode-prototype
description: Build a disposable local-only prototype through a fast single-writer loop with mandatory watermarks and end-to-end outcome evidence. Use only when production correctness, security review, and release readiness are explicitly deferred.
---

# GodMode Prototype

> **PROTOTYPE ONLY — LOCAL TESTING — DO NOT DEPLOY**

Use the parent session's selected model and reasoning level. Do not use real
credentials, production data, live services, shared branches, or release paths.
Move to `$godmode-workflow` before any production or shared use.

## Fast lane

1. State the goal, local boundary, three-bullet plan, file scope, and a
   user-visible done criterion.
2. Assign one `builder` all prototype writes. Put files under `prototype/` or
   `spike/`, or prefix their names with `proto_`.
3. Add the prototype watermark to every generated source file.
4. Run the smallest end-to-end check that exercises the promised behavior.
5. Record the command, actual output or observation, and any unverified edge.
6. Return the files, outcome evidence, and migration checklist.

Starting a process, rendering an empty shell, or merely creating the expected
files does not prove completion. Exercise the user's actual path or artifact
from input to observable result. If that cannot be demonstrated locally, mark
the prototype incomplete and state the missing evidence.

## Required watermark

Adapt this block to the source language:

```text
PROTOTYPE ONLY — NOT FOR PRODUCTION
Created in GodMode Prototype Mode for local testing.
Do not commit to main, deploy, or use real credentials.
Run through $godmode-workflow before production use.
```

## Migration checklist

- [ ] Reassess repository governance and architecture
- [ ] Remove prototype watermarks and temporary names or directories
- [ ] Replace placeholders through approved secret and configuration paths
- [ ] Review changed contracts with `api_guardian` when applicable
- [ ] Run independent `validator` and `tester` gates
- [ ] Prove the production done criterion end to end
- [ ] Follow the repository's release law and obtain required approvals

Do not use this mode when the output will be shipped, shared externally, or
connected to production systems.
