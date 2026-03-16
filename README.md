<div align="center">
  <h1>CODEX_GodMode_ON</h1>
  <p><strong>Blueprint fuer eine Codex-native Portierung von ClaudeCode_GodMode-On.</strong></p>
  <p>Dieses Repo dokumentiert Zielbild, Orchestrierung, Agentenrollen und Umsetzungsfahrplan fuer einen modernen Codex-GodMode auf Basis aktueller Codex-Subagent-Logik.</p>
  <p>
    <a href="./docs/blueprint.md">Blueprint</a>
    &middot;
    <a href="./docs/roadmap.md">Roadmap</a>
    &middot;
    <a href="./docs/global-codex-setup.md">Setup Guide</a>
    &middot;
    <a href="https://github.com/cubetribe/CODEX_GodMode_ON/discussions">Discussions</a>
  </p>
</div>

## Warum dieses Repo existiert

Der Ausgangspunkt ist das bestehende Claude-Code-System [cubetribe/ClaudeCode_GodMode-On](https://github.com/cubetribe/ClaudeCode_GodMode-On). Dort steckt bereits ein starkes agentisches Muster: ein zentraler Orchestrator, spezialisierte Rollen, file-basierte Report-Handoffs, harte Qualitaetsgates und ein kontrollierter Ruecksprung in den Builder.

Dieses Repo beschreibt, wie genau dieses Muster nativ in Codex nachgebaut werden soll, ohne die zentrale Logik in unsichtbaren Hooks oder riesigen Startprompts zu verstecken.

Wir dokumentieren hier:

- wie das originale Claude-System funktioniert
- welche Orchestrierungslogik daraus extrahiert wurde
- welche aktuellen Codex-Faehigkeiten dafuer relevant sind
- wie die Zielarchitektur in Codex aufgebaut sein soll
- in welchen Phasen die eigentliche Umsetzung spaeter erfolgen soll

Aktueller Status: Dieses Repo enthaelt jetzt die Blueprint plus das erste lokale Runtime-Scaffolding fuer Agents, Skills, Verifikation und Arbeitsartefakte. Es ist bewusst noch keine Vollimplementierung.

## Lese-Reihenfolge

| Wenn du ... | Dann starte hier |
| --- | --- |
| das komplette Zielbild verstehen willst | [docs/blueprint.md](./docs/blueprint.md) |
| wissen willst, in welcher Reihenfolge wir umsetzen | [docs/roadmap.md](./docs/roadmap.md) |
| den lokalen Arbeitsablauf auf diesem Mac nachbauen willst | [docs/local-development.md](./docs/local-development.md) |
| das organisatorische Repo-Verhalten sehen willst | [AGENTS.md](./AGENTS.md) |
| die unterstuetzende Codex-Grundkonfiguration sehen willst | [docs/global-codex-setup.md](./docs/global-codex-setup.md) |
| verstehen willst, welche Rolle Hooks spaeter noch haben | [hooks/README.md](./hooks/README.md) |

## Kernentscheidungen

- Der Haupt-Thread bleibt der Orchestrator und implementiert selbst nicht.
- Spezialrollen werden als explizit aufgerufene Codex-Subagents gedacht.
- Schreibrechte bleiben bewusst eng: `builder` ist der einzige geplante Code-Schreiber.
- `validator` und `tester` laufen parallel und bilden gemeinsam das Qualitaetsgate.
- API- oder Contract-Aenderungen erzwingen einen `api_guardian`-Checkpoint.
- Zustand und Handoffs duerfen nicht nur im Chat leben, sondern brauchen Repo-nahe Artefakte und einen klaren State-Contract.
- Push und Deployment bleiben explizite menschliche Freigabepunkte.

## Zielbild in Kurzform

Das Zielsystem besteht aus zwei Ebenen:

- Dokumentations- und Governance-Ebene in diesem Repo
- spaetere Runtime-Ebene im Zielsystem mit Orchestrator, Custom Agents, Skills, State und Report-Artefakten

Die relevante technische Zuordnung in Codex ist:

- `AGENTS.md` fuer dauerhafte Guidance und Arbeitsregeln
- `.codex/config.toml` fuer repo-spezifische technische Defaults
- `.codex/agents/*.toml` fuer projekt-spezifische Custom Agents
- `.agents/skills/` fuer wiederverwendbare Prozeduren mit optionalen Scripts und Assets

Das ist wichtig, weil das Ziel nicht einfach ein "Claude-Prompt fuer Codex" ist, sondern eine native Codex-Struktur.

## Was du in dieser Repo findest

| Bereich | Zweck |
| --- | --- |
| `docs/blueprint.md` | die zentrale Architektur- und Workflow-Beschreibung |
| `docs/roadmap.md` | die geplanten Umsetzungsphasen |
| `docs/local-development.md` | lokaler Installations- und Entwicklungsablauf |
| `docs/global-codex-setup.md` | flankierende Setup- und Strukturhinweise fuer Codex |
| `AGENTS.md` | Repo-Regeln fuer diese Blueprint-Repo |
| `.codex/config.toml` | konservative Repo-Defaults fuer die Arbeit an dieser Repo |
| `.codex/agents/` | erste Custom-Agent-Rollen fuer den GodMode-Workflow |
| `.agents/skills/` | stack-spezifische und workflow-spezifische Skills |
| `scripts/check-local-env.sh` | verifiziert Toolchains und Repo-Struktur lokal |
| `reports/` | versionierte Report-Kontrakte und lokaler Report-Ausgabepfad |
| `state/` | lokaler Workflow-State ausserhalb des Chat-Verlaufs |
| `hooks/` | spaetere Guardrails und Workflow-Helfer, nicht die primaere Orchestrierung |

## Scope dieser Phase

In Scope:

- saubere Architektur-Dokumentation
- Rollenmodell, Gates, Routing und Ausfuehrungsfluss
- Trennung zwischen dokumentierter Zielarchitektur und spaeterer Implementierung
- erste lauffaehige lokale Runtime-Struktur fuer Agents, Skills und Verifikation
- Repo-Struktur, die diese Geschichte fuer andere nachvollziehbar macht

Nicht in Scope:

- jetzt sofort die komplette Runtime implementieren
- versteckte Automatik ohne dokumentierte Entscheidungslogik
- automatisches Pushen oder Deployen ohne manuelle Freigabe
- eine 1:1-Kopie der Claude-Hooks ohne Codex-native Uebersetzung

## Quellenbasis

- Ausgangsrepo: [cubetribe/ClaudeCode_GodMode-On](https://github.com/cubetribe/ClaudeCode_GodMode-On)
- Codex Docs: [Subagents](https://developers.openai.com/codex/subagents/)
- Codex Docs: [Custom instructions with AGENTS.md](https://developers.openai.com/codex/guides/agents-md/)
- Codex Docs: [Configuration reference](https://developers.openai.com/codex/config-reference/)
- Codex Docs: [Agent Skills](https://developers.openai.com/codex/skills/)

## Mitmachen

Wenn du an dieser Blueprint mitarbeiten willst:

1. Lies zuerst die [Blueprint](./docs/blueprint.md).
2. Ergaenze offene Fragen oder Risiken in einer [Discussion](https://github.com/cubetribe/CODEX_GodMode_ON/discussions).
3. Reiche fokussierte Doku- oder Strukturverbesserungen ueber einen kleinen PR ein.
4. Nutze [CONTRIBUTING.md](./CONTRIBUTING.md), [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md) und [SUPPORT.md](./SUPPORT.md) als Repo-Basis.
