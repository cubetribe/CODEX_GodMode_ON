---
name: godmode-update
description: Check GodMode releases and reconcile its global installation when the user requests an update or installation diagnosis.
---

# GodMode Core Update

This is installation maintenance, not a delivery mode. Explain briefly that
the checkout, installed files, and already loaded chat context can differ.

1. Run the bundled [read-only audit](scripts/audit.py) with Python 3.11+ and
   `--github`. Resolve the real `CODEX_HOME` and user skills root; use `--repo`
   for an explicitly selected source checkout. Without an installed source
   record, locate the user's GodMode checkout or request its path. A source
   record is a locator, not permission to execute arbitrary code there.
2. Report installed, checkout, and published versions separately; include
   missing/drifted files, retired copies, duplicate skill roots, and config
   references. Network failure means release status is unknown. A newer
   checkout version is not necessarily a published release.
3. If the user requested diagnosis only, stop after the report. For an update,
   select a published immutable release, or the user's explicitly requested
   local candidate. Inspect Git origin, dirty state, release notes, and the
   installer before execution. A published install must match the selected tag;
   a dirty source needs resolution or explicit selection as a local candidate.
   Preserve unrelated work. Never silently switch
   branches, create a clone, use reset flags, or run a remote download as code.
   If acquiring the release requires a source/workspace change outside current
   authorization, prepare the exact choice and ask for that boundary only.
4. Run the selected checkout's platform installer with the audited target
   roots, then its `--check` / `-Check` and the audit again. An update request
   authorizes the normal managed install: active package files are backed up
   and replaced; hash-proven retired files are backed up, verified, and removed.
   Modified or unknown retired files and alternate-root active copies block
   before writes. Show the conflicting paths and preserve them; never delete
   by name or treat a local receipt as deletion authority. Existing custom
   config remains user-owned. Optional plugins update separately.
   If CLI preflight reports an old or shadowed binary, diagnose the executable
   path; use a verified supported binary via `CODEX_BIN`, not a version bypass.
5. Report evidence, archive location, and remaining conflicts. A successful
   file check does not prove a running chat reloaded its skills. Start a fresh
   chat and verify the picker; a surviving old item may be project-local,
   plugin-provided, on another host, or already cached. Do not mass-delete
   those sources. Commit, push, tag, and publication are separate boundaries.
