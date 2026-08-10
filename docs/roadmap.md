# Roadmap

Released version: `2.10.0`

Current workspace target: unreleased `3.0.0` Lean candidate. Version, tag, and
publication change only during authorized release preparation.

## Shipped separately in 2.10

The optional `godmode-paperwork` plugin remains a separately installed,
local-first document-evidence workflow. GodMode 3 changes the core orchestration
runtime; it does not fold Paperwork into the core installer.

## 3.0 candidate gates

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
- [ ] preserve the optional Paperwork package and pass its validator/unit suite
- [ ] pass Windows PowerShell 5.1 and PowerShell 7 CI on the completed diff
- [ ] pass live `gpt-5.6-sol` Ultra routing traces in an isolated fixture
- [ ] prepare the dated changelog and aligned `3.0.0` distribution versions
- [ ] pass protected-main PR and post-merge release gates on exact SHAs

## Post-3.0 experiments

These are hypotheses, not release promises:

- compare the seven-agent package with a four-agent and built-in-only roster on
  representative tasks;
- compare Sol Ultra with lower reasoning settings for quality, child turns,
  tool calls, latency, and token usage;
- replace the compatibility `max_threads` alias once the stable supported CLI
  accepts the current documented field;
- expand routing evals only when a real regression demonstrates missing
  coverage;
- consider path-selective CI after the canonical static baseline remains
  reliable across several releases;
- design explicit backward compatibility before changing Paperwork's persisted
  evidence-contract version.

New persistent rules or custom agents require evidence that automation, local
governance, an existing skill, the parent, or a built-in role cannot provide the
same function more cheaply.
