# State

This directory is for local workflow state that should not live only in chat history.

## Recommended use

- local state files such as `workflow-state.local.json`
- no sensitive secrets
- no automatic assumption that state files should be versioned
- keep state small enough that a future Codex turn can re-read it quickly
- prefer explicit statuses over long prose

The actual JSON state files are ignored by default through `.gitignore`.

## Suggested state fields

```json
{
  "task": "short task name",
  "phase": "research|plan|build|validate|release",
  "branch": "current branch if relevant",
  "governing_docs": ["AGENTS.md", "README.md"],
  "touched_files": [],
  "open_questions": [],
  "validation": []
}
```

Treat state files as working memory, not as proof. Re-check repo files and validation evidence before relying on old state.
