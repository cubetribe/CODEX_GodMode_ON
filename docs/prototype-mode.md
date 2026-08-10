# Prototype Mode

`$godmode-prototype` is an exclusive local-only primary mode for disposable
exploration. It is not a companion to workflow, debug, or review mode and does
not create production-ready output.

## Boundaries

- no real credentials, production data, live services, shared branches, or
  release paths;
- parent is the sole writer;
- output stays under `prototype/` or `spike/`, or uses `proto_` names;
- every generated source file carries a `PROTOTYPE ONLY` watermark;
- one focused end-to-end check exercises the promised user path;
- file creation or process startup alone is not completion evidence.

Copy the overlay when creating a dedicated spike workspace:

```bash
mkdir -p prototype/.codex
cp templates/prototype-mode/AGENTS.md prototype/AGENTS.md
cp templates/prototype-mode/config.toml prototype/.codex/config.toml
```

Then start with:

```text
Use $godmode-prototype.
Goal: <disposable local outcome>.
Done when: <observable local behavior>.
Constraints: no credentials, production data, live services, or release work.
```

The prototype config uses approval `never`, workspace-write sandboxing, disabled
sandbox-process network, cached Codex web search, and at most two concurrent
agent threads. The skill still defaults to the parent working alone.

## Required watermark

Adapt this header to the source language:

```text
PROTOTYPE ONLY — NOT FOR PRODUCTION
Created for local testing. Do not commit, deploy, or use real credentials.
```

## Promotion

Promotion is a new production contract, not continuation of prototype mode:

1. move to the real project workspace and start a separate
   `$godmode-workflow` run;
2. reassess governance, architecture, contracts, and secret/config handling;
3. remove temporary paths, names, and every watermark;
4. replace mocks and placeholders through approved production boundaries;
5. run validation selected for the actual production risk;
6. prove the production done criterion and follow release law.

Never commit prototype output directly to `main` or deploy it as-is.
