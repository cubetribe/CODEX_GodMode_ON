---
name: godmode-help
description: Explain GodMode usage or review local instruction and configuration overlaps when the user asks for help.
---

# GodMode Core Help

Explain in the user's language; keep the answer short and tailored to their
question. This is help, not a delivery mode. Do not start implementation or
modify the installation merely because this skill was selected.

For an empty/general help request, mention the available read-only configuration
check. For local rule/configuration questions or symptoms such as ignored
project instructions, follow [configuration check](references/configuration-check.md).
Start that requested check directly; ordinary usage questions need no file audit.

GodMode gives Codex reusable procedures (skills) and optional, bounded roles
(agents). The main chat owns the task, decisions, and integration. Normally it
works alone. At most two useful specialists inspect independent uncertainties;
they do not delegate. Advisors are read-only. The tester may produce temporary
test output, but only the parent or one built-in worker edits tracked source.
These roles are instructions and permission settings, not separately trained
models or a guarantee of correctness. Models and reasoning remain user-owned.

In the desktop skill picker, type `/god`, select a visible GodMode skill, then
describe the task. UI availability varies; the portable text invocation is:

```text
Use $godmode-workflow to add CSV export.
Context: the existing export screen.
Done when: the downloaded CSV opens with the expected columns.
Constraints: preserve the current JSON export.
```

Choose one delivery mode: workflow for implementation, debug for a reproducible
failure, review for findings without source edits, prototype for disposable
local exploration. Help explains; update checks releases and reconciles the
global installation. Paperwork is a separately installed optional plugin.
Selecting a delivery-mode skill without a goal yields help; with a goal, work starts.
Do not insist on a prompt template if the user's request is already clear.

If removed roles or `godmode-departments` still appear, explain that updating a
Git checkout does not update global files. Recommend `$godmode-update`, then a
fresh chat after successful installation. Never infer installation health from
a version label alone. Commit, push, publication, and deployment require their
own authorization.
