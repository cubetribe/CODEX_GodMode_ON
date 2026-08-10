<!-- CODEX_GODMODE_GLOBAL_AGENTS:BEGIN -->
# ~/.codex/AGENTS.md

## Universal defaults

- Inspect the current workspace and applicable project instructions before changing files.
- Preserve existing and unrelated changes; keep all writes inside the requested scope.
- For non-trivial work, make the goal, write scope, material constraints, and observable done criteria explicit when they are not already clear.
- Default to working without subagents. Delegate only a bounded independent task when it materially improves the result; delegated agents must not delegate again.
- Select a packaged specialist with its matching `agent_type`; `task_name` alone does not load that role.
- Use the parent or one worker as the sole tracked-file writer. Advisory specialists remain read-only; `tester` may create disposable tool output but never edit tracked source.
- Select validation from the changed scope and risk, and validate the final state rather than an intermediate diff.
- Treat branch changes, commit, push, merge, release, deploy, and other external mutations as separately authorized actions.
- Use current primary documentation for version-sensitive claims and distinguish verified behavior from inference.
<!-- CODEX_GODMODE_GLOBAL_AGENTS:END -->
