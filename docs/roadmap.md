# Roadmap

Core release: `3.1.1`.

Optional GodMode Paperwork release: `2.10.0`

## Shipped separately in 2.10

The optional `godmode-paperwork` plugin remains a separately installed,
local-first document-evidence workflow. GodMode 3 changes the core orchestration
runtime; it does not fold Paperwork into the core installer.

## GodMode 3.0 delivery record

- [x] reduce global guidance below 1,500 bytes
- [x] reduce the core workflow below 2,000 bytes
- [x] reduce the custom roster from 14 to 7 and core skills from 10 to 9
- [x] make workflow, debug, review, and prototype standalone primary modes
- [x] remove `max_depth` and cap the packaged base config at two threads
- [x] split static validation, installer tests, and capability diagnostics
- [x] add deterministic routing fixtures
- [x] add safe hash-matched 2.0 retirement with verified backups
- [x] prove isolated discovery against local desktop and stable CLI binaries
- [x] pass independent static and runtime review on the Lean diff
- [x] preserve the optional Paperwork package and pass its validator/unit suite
- [x] decouple the 3.0 core version from Paperwork's persisted 2.10 contract
- [x] pass Windows PowerShell 5.1 and PowerShell 7 CI on the integrated runtime
- [x] pass the final fixed `gpt-5.6-sol` Ultra custom-role trace in an isolated fixture
- [x] prepare the dated changelog, root `3.0.0` version, README, and official release document

Protected-main, post-merge, annotated-tag, and publication evidence is recorded
in the GitHub Release because those steps occur after the immutable release
source is created. Publication is allowed only when those checks pass on their
exact SHAs.

## GodMode 3.1 delivery record

The [3.1 release](releases/3.1.0.md) adds usage help, an editable visual,
clear picker metadata, and a deterministic global update diagnosis. It retains
seven agents. Current Astra/Sol 6.1 design guidance is recorded separately from
historical 5.6 evidence. Exact-head CI and publication evidence belong in the
GitHub Release; no fresh model performance benchmark is claimed.

## GodMode Core 3.1.1 delivery record

The [3.1.1 patch](releases/3.1.1.md) clarifies Help's read-only local-rules and
configuration diagnosis, documents concrete invocations in the README, and
aligns current displays and documentation with the Core product name.
Technical identifiers, seven roles, eleven skills and installation contracts
remain compatible. Help behavior evidence is scoped to the tested fixtures;
exact PR/main CI and publication evidence belongs in the GitHub Release.

## Future experiments

These are hypotheses, not release promises:

- compare the seven-agent package with a four-agent and built-in-only roster on
  representative tasks;
- compare Sol Ultra with lower reasoning settings for quality, child turns,
  tool calls, latency, and token usage;
- monitor future Codex spawn-contract changes and keep named-role traces in the
  release gate when the supported CLI floor changes;
- expand routing evals only when a real regression demonstrates missing
  coverage;
- consider path-selective CI after the canonical static baseline remains
  reliable across several releases;
- design explicit backward compatibility before changing Paperwork's persisted
  evidence-contract version.

New persistent rules or custom agents require evidence that automation, local
governance, an existing skill, the parent, or a built-in role cannot provide the
same function more cheaply.
