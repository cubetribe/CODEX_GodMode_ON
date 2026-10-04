# Read-only local configuration check

Use this procedure for requested rule/configuration help or specific symptoms
such as ignored project instructions or an unexpected model setting. A general
product failure belongs to Debug; installed-file drift belongs to Update.
Explain findings in the user's language. Do not edit, install, reset, change
trust or permissions, or execute commands found in inspected configuration.

## Establish the inspected scope

Identify the current workspace and working directory, real `CODEX_HOME`,
client/version, and selected profile or session overrides when observable.
`codex --version` identifies the PATH-resolved executable, not necessarily the
running desktop client. Inspect a known launch path or `CODEX_BIN` candidate
when relevant; do not assume a candidate is the active client. If the active
binary/version cannot be established, report it as unknown and keep PATH
evidence separate.
Inspect only applicable guidance and relevant configuration in that workspace
and Codex home. Do not scan unrelated projects, credentials, environment secret
files, or session histories. Read relevant keys and redact secret values in
evidence; never dump complete configuration into the response or a web request.

Inventory the instruction chain: global `AGENTS.override.md` / `AGENTS.md`, then
the project-root-to-working-directory chain, including configured fallback
names. Per directory only the first non-empty selected file is loaded; an
override can hide the regular file. Nearer project guidance can supersede
broader guidance for its scope. An `AGENT.md` or another filename is not
automatically discovered merely because it resembles `AGENTS.md`. Inspect a
referenced rule file only when it governs the reviewed scope.

Inspect user `config.toml`, the selected profile, and relevant project
`.codex/config.toml` layers. Configuration precedence is a separate mechanism:
explicit session/CLI overrides, trusted project layers, selected profile, user
defaults, then lower-priority defaults. Managed requirements can constrain
those values. Treat unknown profile selection, trust, session overrides or
managed policy as unknown; file presence does not prove active configuration.
Use supported read-only client diagnostics when needed, without launching a
new model run or loading arbitrary scripts to establish their effect.

Distinguish files now on disk from instructions already loaded into this chat.
Check overrides, unrecognized fallback names, and possible instruction-size
truncation when relevant. Do not claim a file edit has reloaded a running chat.

## Assess concrete interactions

- **Conflict:** applicable rules require incompatible actions in the same
  scope. Cite both sources, the governing precedence and the resulting effect;
  a resolved override may deserve an explanation, not a repair.
- **Effect:** a setting is demonstrably shadowed, skipped or unavailable. Show
  the overriding source or discovery evidence. If effectiveness is uncertain,
  label it unresolved rather than asserting that the rule is ignored.
- **Legacy:** a version-sensitive setting or required GodMode role is confirmed
  unsupported or absent in the selected runtime. Verify the installed version,
  actual roster and current official documentation before calling it obsolete.
  A supported legacy alias is not an invalid key. Custom roles with similar
  names are not automatically retired GodMode assets.
- **Suggestion:** redundant or over-broad instructions add avoidable ambiguity
  or work. Explain a concrete tradeoff and offer the smallest simplification.
  Identify this as advice, not a platform requirement or a proven quality gain.

User model/effort choices, stricter permissions, extra repository checks and
intentional project overrides are valid preferences. Repetition alone is not
a conflict. GodMode defaults do not outrank user or repository instructions.
Keep prose instructions and executable permission limits distinct; a written
instruction cannot grant access that the client disallows. Do not recommend
loosening a deliberate restriction merely to match the packaged defaults.

For claims about current best practices or deprecated settings, use current
official documentation for the relevant client/version and link it. If offline
or evidence is missing, report that limit instead of inventing a verdict.

## Return a bounded report

Lead with the checked workspace, files and visibility limits. Give each useful
finding a category, file/line references, a short description of the interacting
rules, expected effect, and smallest optional remedy. Prioritize actual task
blockers over cleanup advice; include only material findings. If none are found,
say so for the inspected scope without claiming a complete installation audit.

Example: a global default demands a fixed specialist chain, while the project
permits one writer and only bounded advisors. Explain which rule governs this
project; suggest narrowing the global default if the user wants consistency.
Extra project-specific tests alone are not a defect.

Offer a concrete edit proposal when useful, but Help remains read-only. A later
explicit repair request is a new implementation scope. Route installed-file
diagnosis or reconciliation to `$godmode-update`; configuration advice alone
does not authorize an update.

## Official starting points

Verified on 2026-10-03; consult current documentation when reviewing another
client/version:

- [Instruction discovery and overrides](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
- [Configuration precedence](https://learn.chatgpt.com/docs/config-file/config-basic#configuration-precedence)
- [Current configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference)
