<div align="center">
  <h1>CODEX_GodMode_ON</h1>
  <p><strong>Saubere Codex-Setups. Wiederverwendbare Skills. Weniger Chaos im Team-Alltag.</strong></p>
  <p>Dieses Repo sammelt praktische Patterns fuer globale Defaults, repo-spezifische Regeln, Hooks und wiederkehrende Workflows rund um Codex.</p>
  <p>
    <a href="https://vibecoding-germany.de">Forum</a>
    &middot;
    <a href="https://github.com/cubetribe/CODEX_GodMode_ON/discussions">Discussions</a>
    &middot;
    <a href="./docs/global-codex-setup.md">Setup Guide</a>
    &middot;
    <a href="https://github.com/cubetribe/CODEX_GodMode_ON/issues/new/choose">Mitmachen</a>
  </p>
</div>

## Warum dieses Repo existiert

Viele Codex-Workflows starten mit zu viel Prompt-Wiederholung und zu wenig sauber versionierten Regeln. Dieses Projekt dreht das um:

- persoenliche Defaults leben global in `~/.codex/`
- Team-Regeln leben im Repository
- wiederkehrende Logik wird als Skill oder Hook greifbar
- Diskussionen und Verbesserungen bleiben fuer die Community nachvollziehbar

> Wenn du willst, dass Codex ueber mehrere Projekte hinweg stabil, vorhersagbar und teamfreundlich arbeitet, bist du hier richtig.

## Starte hier

| Wenn du ... | Dann starte hier |
| --- | --- |
| dein globales Codex-Setup aufraeumen willst | [Global setup guide](./docs/global-codex-setup.md) |
| verstehen willst, wie dieses Repo Regeln organisiert | [AGENTS.md](./AGENTS.md) und [`.codex/config.toml`](./.codex/config.toml) |
| eine Idee, Frage oder Erfahrung teilen willst | [GitHub Discussions](https://github.com/cubetribe/CODEX_GodMode_ON/discussions) |
| mit der deutschsprachigen Community diskutieren willst | [Vibe Coding - Germany.de](https://vibecoding-germany.de) |
| konkret beitragen willst | [CONTRIBUTING.md](./CONTRIBUTING.md) |

## Was du hier findest

| Bereich | Zweck |
| --- | --- |
| `docs/` | Guides, Erklaerungen und Best Practices |
| `.codex/` | repo-spezifische Codex-Defaults und Regeln |
| `.agents/skills/` | wiederverwendbare Skills fuer wiederkehrende Workflows |
| `hooks/` | Platz fuer Hook-Beispiele und Workflow-Helfer |
| `.github/` | freundliche Community-Einstiege fuer Issues, PRs und Discussions |

## Empfohlene Struktur

Die aktuelle Codex-Doku stuetzt im Kern diese Trennung:

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

Wichtige Leitlinien:

- `AGENTS.md` ist fuer dauerhafte Regeln und Arbeitsstil gedacht.
- `.codex/config.toml` ist fuer repo-spezifische technische Defaults gedacht.
- repo-spezifische Skills liegen laut aktuell gepruefter offizieller Doku unter `.agents/skills`.
- Dateien naeher am aktuellen Arbeitsverzeichnis haben Vorrang.

## Community und Austausch

Wir wollen die Repo nicht nur dokumentieren, sondern gemeinsam besser machen.

- Fragen und praktische Hilfe: [Discussions / Q&A](https://github.com/cubetribe/CODEX_GodMode_ON/discussions/categories/q-a)
- Ideen und Verbesserungsvorschlaege: [Discussions / Ideas](https://github.com/cubetribe/CODEX_GodMode_ON/discussions/categories/ideas)
- Beispiele aus der Praxis: [Discussions / Show and tell](https://github.com/cubetribe/CODEX_GodMode_ON/discussions/categories/show-and-tell)
- Laengere Community-Debatten: [Vibe Coding - Germany.de](https://vibecoding-germany.de)

## Wofuer dieses Repo gedacht ist

- Solobuilder, die nicht jeden Run neu erklaeren wollen
- kleine Teams, die Codex in mehreren Repos konsistent einsetzen moechten
- Communities, die Skills, Hooks und Arbeitsweisen austauschbar machen wollen
- Leute, die lieber strukturierte Defaults statt Monster-Prompts pflegen

## Aktueller Fokus

Im aktuellen Stand bauen wir die freundlichste moegliche Startbasis:

- klare Guides
- brauchbare Beispiel-Dateien
- gute Einstiegspunkte fuer Diskussionen
- saubere GitHub-Templates
- Platz fuer Skills, Hooks und spaetere Automationen

## Mitmachen

Wenn du helfen willst, nutze bitte zuerst die passende Route:

1. Frage stellen oder Gedanken sortieren: [Discussions](https://github.com/cubetribe/CODEX_GodMode_ON/discussions)
2. Laengere Community-Diskussion: [Forum](https://vibecoding-germany.de)
3. Konkreten Fehler, Doku-Luecke oder Verbesserungsvorschlag einreichen: [Issue chooser](https://github.com/cubetribe/CODEX_GodMode_ON/issues/new/choose)
4. Danach gerne einen fokussierten PR aufsetzen

Die genauen Spielregeln stehen in [CONTRIBUTING.md](./CONTRIBUTING.md), [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md) und [SUPPORT.md](./SUPPORT.md).
