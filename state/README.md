# State

This directory is for local workflow state that should not live only in chat history.

## Recommended use

- local state files such as `workflow-state.local.json`
- no sensitive secrets
- no automatic assumption that state files should be versioned
- keep reusable examples and starter schemas under `state/templates/`
- prefer a small orchestration state record over ad hoc notes spread across chat

The actual JSON state files are ignored by default through `.gitignore`.
