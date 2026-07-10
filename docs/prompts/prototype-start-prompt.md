# Prototype Start Prompt

Use this for a disposable local spike where production readiness is explicitly
deferred.

> **PROTOTYPE ONLY — LOCAL TESTING — DO NOT DEPLOY**

## Prompt

```text
$godmode-prototype

Goal: <one sentence describing what to build or learn>

Local boundary:
- <prototype/ or spike/ path>
- no real credentials, production data, or live services

Context:
- <stack, fixtures, and relevant local files>

Done when:
- <the complete user path from input to observable result>
- <command or manual interaction that proves that outcome end to end>
```

File creation, process startup, or an empty rendered shell is not enough. The
result must exercise the behavior promised under `Done when`. If that cannot be
shown locally, the prototype remains incomplete and the missing evidence must be
reported.

## Best for

- answering one technical question quickly
- comparing local implementation approaches
- a disposable proof of concept
- a local demo that will not ship directly

## The fast-lane contract

- one `builder` owns writes
- all generated source files carry the `PROTOTYPE ONLY` watermark
- use a `proto_` name or a `prototype/` or `spike/` directory
- keep network access off and use mocks or local fixtures
- return actual outcome evidence, unverified edges, and a migration checklist
- do not commit to `main`, push, deploy, or share as production output

## Promotion prompt

Open the real project in a fresh task and switch back to the production
workflow:

```text
$godmode-workflow

Goal: Promote the validated prototype into production-quality implementation.

Context:
- prototype path: <path>
- prototype evidence: <command and observed result>
- migration checklist: <paste checklist>

Done when:
- repository governance and contracts are satisfied
- prototype watermarks and temporary placement are removed
- validator and tester gates pass
- the production behavior is proven end to end
- release law and explicitly authorized external actions are complete
```
