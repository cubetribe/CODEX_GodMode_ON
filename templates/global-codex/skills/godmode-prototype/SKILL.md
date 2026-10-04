---
name: godmode-prototype
description: Explore an idea in a disposable local prototype; production promotion requires a new contract.
---

# GodMode Core Prototype

> **PROTOTYPE ONLY — LOCAL TESTING — DO NOT DEPLOY**

This is a standalone primary mode. Do not combine it with workflow, debug, or
review mode. Do not use real credentials, production data, live services,
shared branches, or release paths.

For help or an empty task, explain this mode briefly and show a goal/done
example. With a clear task, start immediately in the user's language.

1. State goal, local boundary, file scope, and user-visible done criterion.
2. Keep the parent as sole writer. Put output under `prototype/` or `spike/`, or
   prefix names with `proto_`.
3. Put this adapted header in every generated source file:

   ```text
   PROTOTYPE ONLY — NOT FOR PRODUCTION
   Created for local testing. Do not commit, deploy, or use real credentials.
   ```

4. Exercise the promised path end to end and record the command and observation.
5. Report unverified edges and this promotion checklist:
   governance and architecture reviewed; watermarks removed; placeholders moved
   to approved configuration; relevant contracts reviewed; production checks
   run; outcome proven; release law followed.

Start a separate `$godmode-workflow` run before production or shared use.
