# Local Development

Updated: 2026-07-10

Current release: 2.0.0

This guide is for maintainers of the bootstrap repository. End users should
start with [Global Codex Setup](./global-codex-setup.md).

## Governance preflight

Before editing, read the root `AGENTS.md`, `README.md`, `CONTRIBUTING.md`, the
pull-request template, `VERSION`, and `CHANGELOG.md`. Inspect the actual branch
and dirty state; preserve unrelated user changes.

The repository is `main`-first as a base and release line. Create a topic branch
only when the user explicitly authorizes it or the remote protection rules
require a pull request. The current GitHub protection requires PR-based delivery
to `main`; do not bypass it or force-push shared history.

## Toolchain and Codex diagnostics

Repository checks use Git, Bash, Python 3, Node tooling, and optional stack
toolchains. Runtime installation additionally requires Codex CLI `0.134.0` or
newer.

Start by confirming the executable that the shell resolves:

```bash
type -a codex
codex --version
codex help doctor
codex doctor
```

Use `codex update` for an installation that supports self-update. On macOS, an
obsolete Homebrew formula can shadow the current cask; the setup guide contains
the deliberate formula-to-cask remediation.

Run the repository contract:

```bash
./scripts/check-local-env.sh
```

If the intended compatible executable is not first on `PATH`:

```bash
CODEX_BIN=/absolute/path/to/codex ./scripts/check-local-env.sh
```

`--full` also runs the slower local Flutter diagnostic:

```bash
./scripts/check-local-env.sh --full
```

CI uses:

```bash
./scripts/check-local-env.sh --ci
```

CI mode validates the package without requiring a real local Codex executable
or every platform SDK.

## Package structure

| Path | Responsibility |
| --- | --- |
| `templates/global-codex/AGENTS.md` | managed global orchestration guidance |
| `templates/global-codex/config.toml` | model-neutral base config for missing/reset installs |
| `templates/global-codex/profiles/` | separate namespaced Codex `0.134.0+` profiles |
| `templates/global-codex/agents/` | 14 packaged custom agent manifests |
| `templates/global-codex/skills/` | 10 packaged reusable skills |
| `templates/prototype-mode/` | local-only prototype governance and config |
| `scripts/apply-global-codex-setup.*` | platform installers and exact installed-state checks |
| `scripts/test-global-codex-setup.*` | installer regression fixtures |
| `reports/`, `state/` | optional durable workflow artifacts and templates |

Do not move packaged agents or skills into this repository's `.codex/agents/`
or `.agents/skills/`. Codex would discover both project and personal copies
after installation.

## Profiles and model inheritance

The package installs four root-level profile files:

```bash
codex --profile godmode-swiftui
codex --profile godmode-web
codex --profile godmode-flutter
codex --profile godmode-review
```

Do not add inline `[profiles.*]` tables or model/reasoning pins to packaged
config, profiles, or agent manifests. The parent task owns model and reasoning
selection. GPT-5.6 is recommended for demanding work when available; Ultra is
an explicit task-level choice for complex multi-agent orchestration.

## Recommended implementation loop

1. run governance and capability preflight
2. record the intended write scope and release impact
3. use bounded parallel read-only discovery when independent tracks help
4. synthesize findings and freeze contracts and scopes
5. assign one normal implementation writer
6. run independent structural and executable gates
7. prove every done criterion with concrete outcome evidence
8. update docs and release artifacts only after gates pass
9. commit, push, merge, or release only within explicit authority

For a long session, `/plan` can refine the approach and optional `/goal` can
continue approved work. Neither command replaces repository gates.

## Validation matrix

| Change type | Minimum validation |
| --- | --- |
| docs-only copy | `git diff --check`, internal path/link review, Markdown lint |
| agent or skill metadata | `./scripts/check-local-env.sh --ci` plus frontmatter/TOML review |
| config or profile | package check, TOML parse, no inline profiles or model pins |
| shell installer | Bash syntax, ShellCheck, package check, shell regression suite |
| PowerShell installer | PowerShell fixture; CI enforces Windows PowerShell 5.1 and PowerShell 7 |
| GitHub workflow | package security check and `actionlint` |
| release preparation | every applicable row plus version/changelog and clean diff review |

The standard local release gate is:

```bash
bash -n scripts/apply-global-codex-setup.sh \
  scripts/check-local-env.sh \
  scripts/test-global-codex-setup.sh
shellcheck scripts/apply-global-codex-setup.sh \
  scripts/check-local-env.sh \
  scripts/test-global-codex-setup.sh
./scripts/test-global-codex-setup.sh
./scripts/check-local-env.sh --ci
git diff --check
```

Run the PowerShell fixture on Windows or rely on its dedicated CI matrix before
release; do not claim local Windows coverage from a non-Windows machine.

## Test an isolated installation

```bash
tmp_root="$(mktemp -d)"
tmp_codex="$tmp_root/.codex"
tmp_skills="$tmp_root/.agents/skills"

./scripts/apply-global-codex-setup.sh \
  --codex-home "$tmp_codex" \
  --user-skills-home "$tmp_skills" \
  --no-trust-project
./scripts/apply-global-codex-setup.sh --check \
  --codex-home "$tmp_codex" \
  --user-skills-home "$tmp_skills" \
  --no-trust-project
```

Installer changes must also prove complex existing config is byte-preserved,
profile conflict/reset behavior is preflight-safe, `AGENTS.md` marker migration
is deterministic, exact drift is repaired, and a second run is idempotent. The
maintained regression scripts encode those cases.

## Release preparation

For 2.0.0 and later releases:

1. classify impact and confirm the repository's manual `VERSION` plus
   `CHANGELOG.md` release law
2. keep `[Unreleased]` for future work and add a dated release section
3. run every applicable local gate and inspect the complete diff
4. push an authorized topic branch and open a PR against protected `main`
5. wait for required checks, including both Windows installer runtimes
6. merge through allowed repository policy without admin bypass
7. wait for the exact merge commit's `main` workflows
8. create the immutable release tag and GitHub release at that verified commit

Do not rewrite or force-move a published tag. Commit, push, merge, and release
remain separate external actions even when earlier engineering work is approved.

## Activation verification

After package gates pass, applying the runtime to the maintainer's real home is
a separate intentional step:

```bash
./scripts/apply-global-codex-setup.sh
./scripts/apply-global-codex-setup.sh --check
codex doctor
```

The installer preserves an existing config byte-for-byte by default. Start a
fresh task and invoke `$godmode-workflow` for a read-only preflight to verify
skill discovery and parent model inheritance.

## Out of scope

- a dedicated GUI for GodMode
- a background or scheduled local orchestration daemon
- Responses API beta integration
- automatic deployment or release authority
- unconditional GPT-5.6 or Ultra entitlement
