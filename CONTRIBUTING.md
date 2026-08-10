# Contributing

Danke, dass du `CODEX_GodMode_ON` besser machen willst.

Dieses Repo soll moeglichst leicht zu verstehen und leicht zu erweitern sein. Bevor du Zeit in einen groesseren Beitrag steckst, nutze bitte den passenden Einstiegspunkt.

## Der beste Startweg

1. Frage oder Unsicherheit: nutze [GitHub Discussions](https://github.com/cubetribe/CODEX_GodMode_ON/discussions)
2. Groessere Idee oder Richtungsfrage: starte erst eine [Ideas-Diskussion](https://github.com/cubetribe/CODEX_GodMode_ON/discussions/categories/ideas)
3. Laengere Community-Debatte: nutze das Forum [Vibe Coding - Germany.de](https://vibecoding-germany.de)
4. Konkreter Fehler oder klarer Verbesserungsvorschlag: nutze die passenden Issue-Formulare
5. Danach gerne einen kleinen, fokussierten Pull Request oeffnen

## Wobei Hilfe gerade besonders wertvoll ist

- bessere Codex-Konfigurationsbeispiele
- Skills fuer wiederkehrende Workflows
- optionale Plugins mit engem, nachvollziehbarem Sicherheitsvertrag
- Hook-Beispiele mit klarer Wirkung
- Doku, die komplizierte Dinge einfacher erklaert
- Repo- und GitHub-Struktur, die fuer neue Leute sofort einladend wirkt

## Wie wir Beitraege moegen

- klein und klar abgegrenzt
- praktisch statt theoretisch
- mit erkennbarem Use Case
- ohne unnoetige Seiteneffekte
- gut dokumentiert, wenn Verhalten oder Setup betroffen sind

## Repo-Konventionen

- repo instructions: `AGENTS.md`
- repo config: `.codex/config.toml`
- packaged skills: `templates/global-codex/skills/`
- packaged custom agents: `templates/global-codex/agents/`
- optional plugin marketplace: `.agents/plugins/marketplace.json`
- optional plugins: `plugins/`
- maintainer docs: `docs/local-development.md`
- release notes: `CHANGELOG.md` and `VERSION`

## Vor dem PR kurz checken

- passt die Aenderung wirklich zum Ziel dieses Repos?
- gibt es schon eine laufende Diskussion dazu?
- ist der Diff klein genug, um schnell reviewt zu werden?
- wurden Doku oder Beispiele aktualisiert, falls sich Verhalten aendert?
- wurde der Release Impact als `none`, `patch`, `minor` oder `major` eingeordnet?
- wurde `./scripts/check-static.sh` ausgefuehrt und bei Installer-Aenderungen die passende Regression unter `scripts/test-global-codex-setup.*`?
- wurden bei Plugin-Aenderungen `python3 scripts/validate-codex-plugins.py --repo-root .` und die fokussierten Plugin-Tests ausgefuehrt?
- bleiben Dokumentfaelle, Originale und Exporte sicher ausserhalb des Git-Repositories?

## Freundlicher Rahmen

Bitte halte dich an [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md) und nutze [SUPPORT.md](./SUPPORT.md), wenn du unsicher bist, welcher Kanal fuer dein Anliegen der richtige ist.
