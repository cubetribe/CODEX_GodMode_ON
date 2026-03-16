# Codex global sauber konfigurieren

Stabilerer Workflow, weniger Prompt-Wiederholung, sauberere Teamarbeit.

Diese Notiz fasst ein Codex-Setup zusammen, bei dem persoenliche Defaults global liegen und Team-Regeln direkt im Repository versioniert werden.

## Die Kurzversion

Die aktuelle offizielle Codex-Doku stuetzt im Kern dieses Modell:

- persoenliche Guidance in `~/.codex/AGENTS.md`
- persoenliche technische Defaults in `~/.codex/config.toml`
- Repo-Regeln in `AGENTS.md`
- Repo-Defaults in `.codex/config.toml`
- repo-spezifische Skills in `.agents/skills/`

Wichtig fuer die Prioritaet:

- `AGENTS.md`-Dateien naeher am aktuellen Arbeitsverzeichnis haben Vorrang.
- `.codex/config.toml` wird in trusted projects vom Repo-Root Richtung aktuelles Verzeichnis ausgewertet; die naechste Datei gewinnt.

## Ziel

Dieses Setup loest drei typische Probleme gleichzeitig:

1. derselbe Workflow in allen Projekten
2. weniger Wiederholung in Startprompts
3. klare Trennung zwischen persoenlichen Defaults und Team-Regeln

## 1. Globalen Codex-Ordner anlegen

Codex nutzt `~/.codex` als Home fuer persoenliche Konfiguration und globale Instruktionen.

```bash
mkdir -p ~/.codex
```

## 2. Globales `AGENTS.md` anlegen

Globale Arbeitsregeln gehoeren in `~/.codex/AGENTS.md`.

Beispiel:

```md
# ~/.codex/AGENTS.md

## Default working style
- Work only inside the currently opened project / current checkout.
- Never create sibling folders, cloned repos, copied repos, or git worktrees unless I explicitly ask.
- Never create, switch, delete, or rename branches unless I explicitly ask.
- Keep diffs small, safe, and buildable.
- Do not touch unrelated files.
- Record assumptions briefly.

## Execution flow
- For non-trivial tasks: Research Brief -> Plan -> Build -> Validate -> Release Summary.
- Before editing, report: repo root, current branch, touched files, and expected impact.
- After changes, run only the relevant checks for the changed scope.

## Release / versioning
- Classify every change as: major / minor / patch / none.
- Never reuse a version number for behavior-changing code.
- If versioning is manual, update CHANGELOG.md under [Unreleased].
- If release automation exists, do not hand-bump versions unless repo convention explicitly requires it.
- Suggest Conventional Commit style commit messages.

## Safety gates
- Never commit unless I explicitly say yes.
- Never push unless I explicitly say yes.
- Never force-push.
```

Warum das sinnvoll ist:

- `AGENTS.md` wird vor der Arbeit geladen.
- globale Guidance ist fuer persoenliche Defaults gedacht.
- repo-nahe Guidance ist besser fuer Team-Regeln und Codebase-spezifisches Verhalten.

## 3. Optional: Custom Instructions in der App

In der Codex App kannst du persoenliche Custom Instructions direkt in den Einstellungen pflegen. Laut offizieller Doku aktualisiert das dein persoenliches `AGENTS.md`.

## 4. Globales `config.toml` anlegen

Fuer laengerfristige technische Defaults eignet sich `~/.codex/config.toml`.

Beispiel:

```toml
model = "gpt-5.4"
approval_policy = "on-request"
sandbox_mode = "workspace-write"
web_search = "cached"

[sandbox_workspace_write]
writable_roots = []
network_access = false
```

Warum diese Werte ein sinnvoller Startpunkt sind:

- `gpt-5.4` wird in der offiziellen Sample-Config als empfohlene Beispielwahl fuer die Hauptmodell-Auswahl gezeigt.
- `approval_policy = "on-request"` ist der dokumentierte interaktive Mittelweg.
- `sandbox_mode = "workspace-write"` erlaubt Aenderungen im Projekt, aber nicht uneingeschraenkt alles.
- `writable_roots = []` und `network_access = false` halten den Default bewusst eng.
- `web_search = "cached"` nutzt laut Doku standardmaessig einen OpenAI-maintained Index statt Live-Fetching.

## 5. Repo-Regeln ins Projekt verschieben

Das Team-spezifische Verhalten gehoert nicht in den globalen Prompt, sondern ins Repo.

Empfohlene Struktur:

```text
repo-root/
  AGENTS.md
  .codex/
    config.toml
    rules/
  .agents/
    skills/
```

Ein schlankes Repo-`AGENTS.md` kann so aussehen:

```md
# AGENTS.md

## Project rules
- Run:
  - pnpm lint
  - pnpm test
  - pnpm build
- Do not modify infrastructure or CI without explicit request.
- Use existing folder structure and naming conventions.
- Update docs only if behavior or setup changed.

## Versioning
- Classify each change as major / minor / patch / none.
- Prepare a CHANGELOG entry under [Unreleased].
- If the repo has release automation, prepare inputs; do not invent manual version bumps.
```

## 6. Wiederkehrende Logik als Skill modellieren

Wenn immer wieder dieselbe Release-, Review- oder Setup-Logik auftaucht, ist ein Skill sauberer als immer laengeres `AGENTS.md`.

Die aktuelle offizielle Doku beschreibt repo-spezifische Skills unter:

```text
.agents/skills/
```

Das ist ein wichtiger Punkt, weil aeltere Beispiele oder Community-Posts teils noch `.codex/skills/` nennen. Fuer die aktuelle offizielle Doku ist `.agents/skills/` der relevante Repo-Pfad.

Beispiel-Idee:

```text
.agents/skills/release-manager/SKILL.md
```

Aufgabe des Skills:

- Release-Impact klassifizieren
- Changelog-Text vorbereiten
- Commit-Message vorschlagen
- PR-Summary erzeugen

## 7. In der App bewusst `Local` oder `Worktree` waehlen

Wenn du direkt im aktuellen Checkout arbeiten willst, nutze `Local`.

Was die aktuelle offizielle Doku klar sagt:

- neue Threads koennen explizit auf `Worktree` gestartet werden
- Threads lassen sich zwischen `Local` und `Worktree` per Handoff bewegen
- Automations koennen pro Automation auf `Local` oder `Worktree` laufen
- Codex-verwaltete Worktrees liegen unter `$CODEX_HOME/worktrees`

Wichtige Einordnung:

- Ich habe in den aktuell geprueften offiziellen Seiten keine dokumentierte globale Einstellung gefunden, die jede neue App-Session automatisch dauerhaft auf `Local` statt `Worktree` erzwingt.
- Das ist eine Schlussfolgerung aus den geprueften Doku-Seiten, nicht eine explizit dokumentierte Negativ-Aussage.

## 8. Setup verifizieren

Nach Aenderungen an `AGENTS.md` oder `config.toml` am besten eine neue Session starten.

Zum schnellen Test:

```bash
codex "Show which instruction files are active."
```

oder:

```bash
codex --ask-for-approval never "Summarize the current instructions."
```

## Was ich nicht mehr empfehlen wuerde

Keinen riesigen Startprompt als Hauptmechanismus.

Die robustere Aufteilung ist:

- `~/.codex/AGENTS.md` fuer persoenliche Defaults
- `~/.codex/config.toml` fuer globale technische Defaults
- `AGENTS.md` im Repo fuer Team-Regeln
- `.codex/config.toml` fuer Repo-Defaults
- `.agents/skills/` fuer wiederkehrende Workflows

## Quellen

- OpenAI Codex docs: [Config basics](https://developers.openai.com/codex/config-basic)
- OpenAI Codex docs: [Custom instructions with AGENTS.md](https://developers.openai.com/codex/guides/agents-md)
- OpenAI Codex docs: [Customization](https://developers.openai.com/codex/concepts/customization)
- OpenAI Codex docs: [Agent Skills](https://developers.openai.com/codex/skills)
- OpenAI Codex docs: [Configuration reference](https://developers.openai.com/codex/config-reference)
- OpenAI Codex docs: [Sample configuration](https://developers.openai.com/codex/config-sample)
- OpenAI Codex docs: [Worktrees](https://developers.openai.com/codex/app/worktrees)
- OpenAI Codex docs: [Automations](https://developers.openai.com/codex/app/automations)
- OpenAI Codex docs: [Codex app settings](https://developers.openai.com/codex/app/settings)
