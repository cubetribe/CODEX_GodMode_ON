# Hooks

Dieses Verzeichnis ist bewusst nur eine Nebenschiene des Zielsystems.

Wichtig fuer diese Repo:

- Die primaere Orchestrierung soll in Codex selbst liegen: `AGENTS.md`, `.codex/config.toml`, spaetere `.codex/agents/*.toml`, explizites Subagent-Routing und dokumentierte Gates.
- Hooks duerfen die Architektur nicht "heimlich steuern".
- Hooks sind nur fuer Guardrails und wiederholbare technische Checks gedacht.

Geplante Beispiele:

- Preflight-Checks vor einem Workflow-Start
- API-Impact-Erkennung auf Basis von Diffs
- Validierung von Agenten-Reports gegen ein Report-Schema
- Pre-push-Schutz, damit nichts ohne explizite Freigabe hochgeschoben wird

Das Verzeichnis bleibt also erhalten, aber mit klar begrenzter Aufgabe: absichern, nicht orchestrieren.
