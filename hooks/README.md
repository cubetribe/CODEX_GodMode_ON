# Hooks

This directory is intentionally secondary.

Important for this repository:

- the primary orchestration should live in Codex itself
- hooks must not secretly drive the architecture
- hooks are for guardrails and repeatable technical checks only

Planned examples:

- preflight checks before a workflow starts
- diff-based API impact detection
- report validation against a report schema
- pre-push protection so nothing is pushed without explicit approval

In short: protect the system, do not orchestrate it.
