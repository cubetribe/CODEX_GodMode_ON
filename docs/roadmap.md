# Roadmap

Diese Roadmap beschreibt nicht "alles, was irgendwann nett waere", sondern die geplanten Lieferphasen fuer die Codex-GodMode-Portierung.

## Phase 0 - Blueprint

Ziel:

- Ausgangssystem analysieren
- aktuelle Codex-Faehigkeiten verifizieren
- Zielarchitektur, Rollen und Gates sauber dokumentieren

Lieferobjekte:

- `README.md` als Repo-Einstieg
- `docs/blueprint.md` als Architekturkern
- `docs/roadmap.md` als Umsetzungsfahrplan

Fertig wenn:

- ein externer Leser versteht Zweck, Zielbild und naechsten Umsetzungsschritt ohne Zusatzkontext

## Phase 1 - Repo-Scaffolding fuer das Zielsystem

Ziel:

- die dokumentierte Zielstruktur im Repo vorbereiten, ohne die volle Runtime bereits zu bauen

Geplante Inhalte:

- `.codex/agents/` fuer Custom-Agent-Definitionen
- State- und Report-Verzeichnisstruktur
- dokumentierte Beispielkonfiguration fuer `[agents]`

Fertig wenn:

- die Repo-Struktur dem Blueprint sichtbar entspricht

## Phase 2 - Orchestrator-Vertrag

Ziel:

- den Steuerungsvertrag des Haupt-Orchestrators festziehen

Geplante Inhalte:

- State-Schema
- Report-Schema
- Routing-Regeln
- Gate-Definitionen
- Resume- und Fehlerpfade

Fertig wenn:

- jeder Schritt zwischen Intake und Abschluss als deterministischer Ablauf dokumentiert ist

## Phase 3 - Guardrails und Hilfswerkzeuge

Ziel:

- die wenigen Helfer bauen, die das System hart und nachvollziehbar absichern

Geplante Inhalte:

- Preflight-Checks
- API-Impact-Erkennung
- Report-Validierung
- Pre-push-Gate fuer explizite Freigabe

Fertig wenn:

- kritische Regeln nicht nur beschrieben, sondern technisch absicherbar sind

## Phase 4 - Referenzimplementierung im Repo

Ziel:

- die dokumentierte Architektur als lauffaehige Referenz im Repo abbilden

Geplante Inhalte:

- erste Custom Agents
- erste Skills
- Beispielablauf fuer Feature-, Bugfix- und API-Change-Workflows

Fertig wenn:

- ein neuer Nutzer den Workflow lokal reproduzieren kann

## Phase 5 - Validierung und Community-Haertung

Ziel:

- die Referenz an realen Faellen pruefen und schaerfen

Geplante Inhalte:

- Demo-Durchlaeufe
- Feedback aus Discussions
- Ueberarbeitung unklarer Rollen und Gates
- Versionierung der Blueprint und spaeter der Runtime

Fertig wenn:

- das System fuer wiederholte Nutzung stabil genug und fuer andere nachvollziehbar ist
