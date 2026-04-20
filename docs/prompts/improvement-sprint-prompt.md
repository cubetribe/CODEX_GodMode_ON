# GodMode Improvement Sprint — Codex Prompt

**Branch:** `codex/plane-fachagentenorganisation`  
**Datum:** 2026-04-16  
**Zweck:** Geführter Verbesserungs-Sprint über vier klar begrenzte Baustellen.

---

## Kontext

Du arbeitest im Repo `CODEX_GodMode_ON-Lokal`. Das ist das Referenz- und Installer-Repo für das GodMode-Laufzeitsystem. Lies vor dem Start:

- `AGENTS.md` (Repo-Regeln und Release-Gesetz)
- `docs/department-orchestration.md` (aktueller vs. Zielzustand)
- `docs/blueprint.md` (Architekturziel)
- `reports/generated/department-agent-orchestration-plan-2026-04-12.md` (letzter Orchestrierungsplan)
- `.codex/agents/*.toml` (alle aktuellen Agenten)
- `.agents/skills/godmode-workflow/SKILL.md` und `godmode-departments/SKILL.md`
- `CHANGELOG.md` und `VERSION`

Nutze `$godmode-departments` zusammen mit `$godmode-workflow`. Der aktuelle Stand auf dem Branch hat bereits unstaged Changes und neue ungetrackte Dateien — behandle diese als Eingabe, nicht als fertig committet.

---

## Ziel

Vier Baustellen schließen, die das System jetzt bremsen. Jede Baustelle hat einen klaren Eigentümer und definierte Lieferobjekte. Arbeite in der unten beschriebenen Reihenfolge. Öffne keine Baustelle, bevor die vorherige ein schriftliches Gate-Ergebnis hat.

---

## Baustelle 1 — CHANGELOG als Single Point of Truth

**Problem:** Der `[Unreleased]`-Abschnitt in `CHANGELOG.md` ist leer, obwohl auf dem aktuellen Branch signifikante Änderungen vorliegen. Gleichzeitig entstehen Einzel-Artefakte unter `reports/generated/`, die nirgendwo konsolidiert werden. Das Ergebnis: viele Dokumente, kein Single Point of Truth.

**Eigentümer:** `scribe` mit Abstimmung durch `release-manager`-Skill und Freigabe durch `workspace_governance`

**Aufgaben:**

1. Lies alle unstaged/untracked Änderungen auf dem Branch:
   - `.agents/skills/release-manager/SKILL.md` (modified)
   - `docs/prompts/apple-start-prompt.md` (modified)
   - `docs/prompts/debug-start-prompt.md` (modified)
   - `docs/prompts/dev-start-prompt.md` (modified)
   - `docs/prompts/flutter-start-prompt.md` (modified)
   - `docs/prompts/review-start-prompt.md` (modified)
   - `docs/prompts/web-start-prompt.md` (modified)
   - `.agents/skills/greenfield-bootstrap/SKILL.md` (neu)
   - `docs/prompts/greenfield-start-prompt.md` (neu)
   - `templates/project-bootstrap/` (neu)

2. Klassifiziere die Release-Auswirkung nach dem Muster in `AGENTS.md` (major / minor / patch / none).

3. Befülle den `[Unreleased]`-Abschnitt in `CHANGELOG.md` mit einem präzisen, menschenlesbaren Eintrag. Nutze das bestehende Keep-a-Changelog-Format des Repos. Erfinde keine Version — die Entscheidung für einen Versions-Bump liegt beim Menschen.

4. Definiere ein verbindliches Protokoll in `AGENTS.md` (Abschnitt "Changelog law"), das regelt:
   - Was ausschließlich in `CHANGELOG.md [Unreleased]` gehört (alle nutzerrelevanten Änderungen)
   - Was ausschließlich in `reports/generated/` gehört (Analyse-Artefakte, Orchestrierungspläne)
   - Was ausschließlich in `state/` gehört (laufender Workflow-Status)
   - Dass `scribe` nur nach bestandenen Gates schreibt und immer zuerst `CHANGELOG.md` aktualisiert, bevor neue Reports entstehen

**Gate:** `validator` prüft Formatübereinstimmung mit existierenden Changelog-Einträgen und Konsistenz der neuen Changelog-Regel mit dem bestehenden `AGENTS.md`-Inhalt.

---

## Baustelle 2 — GitHub Security & CI/CD Agent

**Problem:** Der bestehende `github_manager` ist read-only und deckt ausschließlich PR/Release-Framing ab. GitHub-Sicherheit (Branch Protection, CODEOWNERS, Dependabot, Secret Scanning, CodeQL, GitHub Actions) ist vollständig unbedient — obwohl es für jedes professionelle Repo ein Pflichtthema ist.

**Eigentümer:** `runtime_platform` für den neuen Agenten, `workflow_design` für den optionalen Skill, `quality_operations` für Verifikation

**Aufgaben:**

1. Erstelle `.codex/agents/ci_security_guardian.toml` mit folgender Spezifikation:
   - `name = "ci_security_guardian"`
   - `sandbox_mode = "workspace-write"` (muss Workflow-YAML schreiben können)
   - Zuständigkeit: `.github/workflows/**`, `.github/CODEOWNERS`, `.github/dependabot.yml`, alle GitHub-Sicherheitskonfigurationen
   - Explizites `developer_instructions`-Feld mit folgenden Regeln:
     - Erstelle oder reviewe GitHub Actions Workflows nach aktuellem Security-Best-Practice (Pin actions auf SHA, kein `pull_request_target` ohne Reviewpflicht, least-privilege `permissions`)
     - Verwalte `CODEOWNERS` für kritische Pfade: `.codex/agents/`, `.agents/skills/`, `AGENTS.md`, `.github/workflows/`
     - Konfiguriere Dependabot für Actions und direkte Abhängigkeiten
     - Aktiviere Secret Scanning und Push Protection wenn möglich
     - Empfehle CodeQL für dieses Repo (Shell-Skripte, Markdown-Linting)
     - Niemals Secrets in Workflow-YAML schreiben; immer auf `${{ secrets.NAME }}` verweisen
     - Niemals pushen oder History rewriten ohne explizite Nutzerfreigabe
     - Alle Empfehlungen als konkretes Go/No-Go mit Begründung zurückgeben

2. Aktualisiere `docs/department-orchestration.md`: Füge `ci_security_guardian` in die Rollentabelle ein und beschreibe, wann er ausgelöst wird (immer wenn `.github/**` oder CI/CD-Verhalten verändert wird, und als optionaler Gate-Check vor jedem Release).

3. Erstelle einen minimalen, sofort nutzbaren GitHub-Actions-Workflow unter `.github/workflows/ci.yml` mit:
   - Trigger: `push` auf alle Branches, `pull_request` auf `main`
   - Jobs: `validate` (führt `./scripts/check-local-env.sh` aus), `lint-markdown` (z.B. mit `markdownlint-cli2`)
   - Korrekte `permissions`-Sektion (least privilege)
   - Alle Actions auf SHA-Commit-Hash gepinnt

4. Erstelle `.github/CODEOWNERS` mit Ownership-Regeln für die kritischen Pfade dieses Repos.

**Gate:** `validator` prüft TOML-Syntax des neuen Agenten und Konsistenz mit bestehenden Agent-Definitionen. `tester` führt `./scripts/check-local-env.sh` lokal aus.

---

## Baustelle 3 — Test- & Validierungsverfeinerung

**Problem:** `tester` und `validator` existieren als Agenten, aber es gibt keine standardisierten Test-Entrypoints, keine Smoke-Test-Definitionen und keine Dokumentation darüber, was "grüne Gates" konkret bedeutet — was zu unterschiedlichen Interpretationen führt.

**Eigentümer:** `quality_operations`, abgestimmt mit `tester` und `validator`

**Aufgaben:**

1. Definiere in `AGENTS.md` (neuer Abschnitt "Validation law") was die Gates konkret prüfen:
   - **Validator-Gate:** Strukturprüfung (TOML-Syntax aller Agenten, Markdown-Konsistenz, interne Linkintegrität, Rollenname-Konsistenz zwischen `AGENTS.md`, `.codex/agents/*.toml`, `.agents/skills/`), keine Quelldateiänderungen
   - **Tester-Gate:** Führe `./scripts/check-local-env.sh` aus, prüfe alle Shell-Skripte auf Syntax-Fehler (`bash -n`), bestätige dass neue Skills ein `name`- und `description`-Frontmatter haben
   - Beide Gates müssen explizit als bestanden/fehlgeschlagen protokolliert werden, bevor `scribe` schreibt

2. Erweitere `./scripts/check-local-env.sh` um folgende Checks (oder erstelle ein separates `./scripts/validate-repo.sh`):
   - Alle `.codex/agents/*.toml` haben `name`, `description`, `sandbox_mode`, `developer_instructions`
   - Alle `.agents/skills/*/SKILL.md` haben `name`- und `description`-Frontmatter
   - `CHANGELOG.md [Unreleased]` ist nicht leer wenn ungetrackte oder unstaged Änderungen existieren
   - `VERSION`-Datei stimmt mit letztem Versionstag in `CHANGELOG.md` überein
   - Rollenname in `.codex/agents/*.toml` stimmt mit `name`-Feld überein

3. Dokumentiere in `docs/local-development.md` den vollständigen "Definition of Done" für einen GodMode-Lauf:
   - Validator-Gate grün
   - Tester-Gate grün
   - `CHANGELOG.md [Unreleased]` aktuell
   - Kein Single-Writer-Konflikt in Write-Scope-Matrix

**Gate:** `validator` prüft das neue Skript auf Bash-Syntax-Fehler. `tester` führt es einmal vollständig aus.

---

## Baustelle 4 — Dokumentation: Current State ↔ Target State Lücke schließen

**Problem:** Die Dokumentation unterscheidet korrekt zwischen aktuellem Stand und Zielzustand, aber die neuen Artefakte aus dem aktuellen Branch (greenfield-bootstrap, neue Prompts, verbesserter release-manager) sind in keinem der zentralen Docs eingetragen. Dadurch wächst die Lücke zwischen Code und Dokumentation mit jeder Iteration.

**Eigentümer:** `docs_dx`, Freigabe durch `workspace_governance`

**Aufgaben:**

1. Aktualisiere `docs/blueprint.md`: Trage den aktuellen Zustand der Department-Agenten korrekt ein — welche bereits als `.toml` existieren, welche noch Zielzustand sind.

2. Aktualisiere `docs/roadmap.md`: Markiere abgeschlossene Phasen aus dem Orchestrierungsplan (`department-agent-orchestration-plan-2026-04-12.md`) als erledigt. Füge die vier Baustellen dieses Sprints als laufende Phase ein.

3. Aktualisiere `README.md`: Ergänze den neuen `greenfield-bootstrap`-Skill und den neuen `ci_security_guardian`-Agenten in der Übersicht der verfügbaren Agenten und Skills.

4. Überprüfe alle modifizierten Prompts unter `docs/prompts/` darauf, ob sie noch auf das aktuelle Department-Modell verweisen (insbesondere: korrekte Skill-Namen, korrekte Agenten-Namen, kein Verweis auf veraltete Rollen).

5. Erstelle eine knappe Datei `docs/agent-registry.md` als maschinenlesbares Single-Point-of-Truth-Register aller Agenten:
   - Spalten: `agent`, `toml_path`, `department`, `sandbox_mode`, `primary_ownership`, `triggers_when`
   - Einer Zeile pro Agent (inkl. neuer `ci_security_guardian`)
   - Dieser Register wird von `Contract Office` bei jedem Lauf als Referenz genutzt

**Gate:** `validator` prüft alle internen Links in den geänderten Docs, prüft Rollenname-Konsistenz zwischen `agent-registry.md` und `.codex/agents/*.toml`.

---

## Ausführungsreihenfolge & Parallelisierungsregeln

```text
Phase 0 (sequentiell):
  → governance preflight: lies AGENTS.md, blueprint.md, den letzten Orchestrierungsplan
  → researcher verifiziert unstaged/untracked Änderungen vollständig

Phase 1 (sequentiell):
  → Baustelle 1 (CHANGELOG + Protokoll) muss zuerst abgeschlossen sein
    Reason: Changelog-Gesetz regelt, was alle anderen Baustellen dokumentieren dürfen

Phase 2 (parallelisierbar, disjunkte Write-Scopes):
  → Baustelle 2 (.github/**, .codex/agents/, docs/department-orchestration.md)
  → Baustelle 3 (scripts/, AGENTS.md Abschnitt Validation, docs/local-development.md)
  Einzel-Writer-Regel: ein Schreiber pro Pfad

Phase 3 (sequentiell, nach Phase 2):
  → Baustelle 4 (docs/blueprint.md, docs/roadmap.md, README.md, agent-registry.md)
    Reason: nutzt Ergebnisse aus Phase 2 als Input

Phase 4 (alle Gates):
  → validator läuft über alle geänderten Scopes
  → tester führt ./scripts/check-local-env.sh und neues Validierungsskript aus
  → scribe schreibt CHANGELOG.md [Unreleased] final

Phase 5 (Freigabe durch Mensch):
  → kein Push, kein PR ohne explizite Bestätigung
```

---

## Nicht im Scope dieses Sprints

- Versions-Bump oder Release-Tagging (bleibt beim Menschen)
- Änderungen an `.codex/config.toml`
- Neue Stack-spezifische Skills (Web, Apple, Flutter) — außer Prompt-Korrekturen
- Umstrukturierung des Branching-Modells
- Deployment-Automatisierung oder externe CI-Dienst-Integration

---

## Erwartetes Ergebnis

Am Ende dieses Sprints:

- `CHANGELOG.md [Unreleased]` ist befüllt und das Changelog-Gesetz ist in `AGENTS.md` verankert
- Ein `ci_security_guardian`-Agent existiert mit vollständiger TOML-Definition und einem Basis-CI-Workflow
- Die Testgates sind in `AGENTS.md` als verbindliche Prüfliste definiert und durch ein erweitertes Skript automatisierbar
- `docs/agent-registry.md` existiert als Single Point of Truth für alle Agenten
- Alle Docs-Lücken zwischen current state und target state sind geschlossen

Kein spekulativer Code. Nur was wirklich im Repo verankert und durch Gates verifiziert ist.
