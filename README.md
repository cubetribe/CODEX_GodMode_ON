# CODEX_GodMode_ON

`CODEX_GodMode_ON` ist ein Community-Repo fuer saubere, wiederverwendbare Codex-Setups.

Der Fokus liegt auf:

- globalen Codex-Defaults
- repo-spezifischen Regeln
- wiederverwendbaren Skills
- Hooks und Workflow-Bausteinen
- dokumentierten Best Practices fuer Teams

## Community

Die Diskussion rund um dieses Projekt laeuft in der Community von [Vibe Coding - Germany.de](https://vibecoding-germany.de).

Wenn du das Setup aehnlich nutzt, dort Ideen, Erfahrungen und Verbesserungen teilen willst, ist das der richtige Ort fuer Austausch und Feedback.

## Worum es hier geht

Das Ziel ist ein Codex-Setup, das in mehreren Projekten konsistent funktioniert:

1. derselbe Workflow ueber verschiedene Repos hinweg
2. weniger Wiederholung in Startprompts
3. klare Trennung zwischen persoenlichen Defaults und Team-Regeln

Die Kernidee:

- globale Regeln nach `~/.codex/`
- Team- und Repo-Regeln ins Projekt
- wiederkehrende Ablaeufe als Skill statt als immer laengerer Prompt

## Empfohlene Struktur

Die aktuelle OpenAI-Doku stuetzt diese Trennung:

```text
~/.codex/
  AGENTS.md
  config.toml

repo-root/
  AGENTS.md
  .codex/
    config.toml
    rules/
  .agents/
    skills/
```

Wichtig:

- `AGENTS.md` ist fuer dauerhafte Regeln und Arbeitsstil gedacht.
- `.codex/config.toml` ist fuer repo-spezifische technische Defaults gedacht und wird in trusted projects als Projekt-Layer ausgewertet.
- Repo-Skills liegen laut aktueller offizieller Doku unter `.agents/skills`.
- Dateien naeher am aktuellen Arbeitsverzeichnis haben Vorrang.

## Was dieses Repo liefern soll

- dokumentierte Setup-Empfehlungen
- direkt nutzbare Beispiel-Dateien
- Skills fuer wiederkehrende Workflows
- Platz fuer Hooks und spaetere Automationen
- Community-getriebene Verbesserung der Codex-Praxis

## Einstieg

- Die erste inhaltliche Grundlage steht in [docs/global-codex-setup.md](/Users/denniswestermann/Library/Mobile Documents/com~apple~CloudDocs/Desktop/Coding Projekte/CODEX_GodMode_ON/docs/global-codex-setup.md).
- Die Repo-Regeln fuer dieses Projekt stehen in [AGENTS.md](/Users/denniswestermann/Library/Mobile Documents/com~apple~CloudDocs/Desktop/Coding Projekte/CODEX_GodMode_ON/AGENTS.md).
- Ein erstes Skill-Beispiel liegt in [.agents/skills/release-manager/SKILL.md](/Users/denniswestermann/Library/Mobile Documents/com~apple~CloudDocs/Desktop/Coding Projekte/CODEX_GodMode_ON/.agents/skills/release-manager/SKILL.md).

## Status

Das Repo ist noch in der Bootstrap-Phase, aber die Grundstruktur steht jetzt so, dass wir als Naechstes gezielt:

- weitere Skills
- Hook-Beispiele
- Repo-Templates
- konkrete Team-Workflows
- GitHub-Governance

einbauen koennen.

## Mitmachen

Wenn du helfen willst, starte mit [CONTRIBUTING.md](/Users/denniswestermann/Library/Mobile Documents/com~apple~CloudDocs/Desktop/Coding Projekte/CODEX_GodMode_ON/CONTRIBUTING.md) und bring Feedback idealerweise zuerst ueber das Forum ein: [vibecoding-germany.de](https://vibecoding-germany.de)
