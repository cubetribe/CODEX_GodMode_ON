---
name: greenfield-bootstrap
description: Bootstrap repo-local governance before parallel Codex implementation starts in an empty, newly initialized, or undocumented workspace.
---

# Greenfield Bootstrap

Use this skill with `godmode-workflow` when the current workspace is empty, newly initialized, or missing the local governance needed for safe multi-step implementation.

## Required outcome

- establish a minimal repo-local constitution before parallel work starts
- keep the bootstrap small, truthful, and directly tied to the actual project

## Default route

1. inspect the workspace and confirm what exists
2. create or update the smallest local governance surface needed:
   - repo-root `AGENTS.md` or equivalent instructions file
   - basic README or setup note if the repo has none
   - validation and release-law notes for the touched scope
3. keep early structure explicit:
   - where config belongs
   - where agents belong
   - where project or user skills belong
4. only after that, continue under `$godmode-workflow`, `$godmode-debug`, or `$godmode-review`

## Core rules

- Do not invent architecture that the project has not chosen yet.
- Prefer durable markdown guidance over chat-only agreements.
- Keep initial rules short enough that they can realistically stay maintained.

## Do not use when

- the workspace already has clear local governance
- the task is only a one-off answer with no lasting repo changes
