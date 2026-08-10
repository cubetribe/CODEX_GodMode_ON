# State

This directory is for resumable state on long, paused, or handed-off work only.

## Use it when

- work will span sessions, pause, or move to another owner
- the next session needs an explicit authority and write-scope handoff

Do not create state for ordinary single-session work. When state is justified:

- no sensitive secrets
- copy `templates/orchestration-state.template.json` into an ignored local JSON
- keep it compact and let the parent session own updates
- record source revision, authority, sole writer, scope, done criteria, evidence,
  blockers, and next action

State is working memory, never proof. Re-check repository files and commands
before relying on an older record.
