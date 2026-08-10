# Agent Registry

Status: current GodMode `3.0.0` core roster.

The core packages seven optional custom agents under
`templates/global-codex/agents/`. The parent defaults to no custom agent and
starts one only for a named, independent need. Specialists do not delegate.
The parent must pass the matching `agent_type`; `task_name` alone does not load
the selected manifest.

| Agent | Sandbox | Use only for | Output boundary |
| --- | --- | --- | --- |
| `api_guardian` | read-only | public API, schema, CLI, config, or migration compatibility | GO/NO-GO, contract, evidence, follow-up |
| `validator` | read-only | static syntax, structure, links, naming, and cross-file consistency | commands or inspections, pass/fail, findings |
| `tester` | workspace-write | build, execution, reproduction, and user-visible behavior | commands, observation, pass/fail, runtime gaps |
| `runtime_platform` | read-only | one OS, sandbox, toolchain, or environment uncertainty | evidence, confidence, narrow next step |
| `workflow_design` | read-only | one routing, skill, prompt, handoff, or resumability question | smallest design and trade-offs |
| `docs_dx` | read-only | substantial setup or public documentation clarity risk | concrete corrections with sources |
| `ci_security_guardian` | read-only | CI permissions, action pins, trust boundaries, and secret handling | GO/NO-GO and smallest remediation |

`tester` may write temporary tool output because builds and test frameworks can
require it, but it never edits tracked source. `validator` does not reproduce
runtime behavior. Both are used together only when repository law or migration,
security, mixed-contract, or release risk justifies both.

## Removed 2.0 roles

`researcher`, `architect`, `builder`, `scribe`, `github_manager`,
`workspace_governance`, and `quality_operations` were retired in 3.0.
Their useful work belongs to the strong parent, Codex built-ins
(`explorer`/`worker`), the release skill, or one of the narrow agents above. The
installer removes only hash-matched 2.0 copies and preserves verified backups.

## Model resolution

Manifests contain no model or reasoning-effort pins. For each setting, Codex
resolves an explicit spawn value first, then a matching `[agents]` default, then
the parent value. Adding a pin to a manifest changes that contract and requires
compatibility review.

## Source of truth

- active and retired roster: `templates/global-codex/managed-assets.tsv`
- agent behavior: each TOML manifest
- routing: the selected primary skill
- deterministic roster checks: `scripts/check-static.py`
