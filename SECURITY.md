# Security Policy

Dieses Repository enthaelt vor allem Dokumentation, Konfigurationsbeispiele, Skills und Workflow-Helfer. Trotzdem koennen auch hier sicherheitsrelevante Probleme auftauchen.

## Bitte melde insbesondere

- versehentlich veroeffentlichte Geheimnisse oder Tokens
- unsichere Beispiel-Konfigurationen
- Hooks oder Skripte mit riskantem Verhalten
- Doku, die zu unsicheren Defaults fuehren koennte
- Pfad-, Archiv- oder Integritaetsfehler in `godmode-paperwork`
- unbeabsichtigte Netzwerk-, Upload-, Installations-, Loesch- oder Uebermittlungsfunktionen bei sensiblen Dokumenten

## GodMode Paperwork

Paperwork-Faelle, Originaldokumente und Exporte gehoeren niemals in dieses
Repository. Das Plugin verarbeitet lokal, installiert keine Werkzeuge, ruft
keine Cloud-OCR auf und uebermittelt keine Formulare. Seine Hash-Kette und
benannten menschlichen Freigaben belegen interne Konsistenz, sind aber keine
digitale Signatur und kein Schutz gegen eine Person, die den gesamten Fall samt
aller Hashes kontrolliert neu schreiben kann.

Ein `PASS` bestaetigt nur die konfigurierten mechanischen Regeln. Es ersetzt
weder Rechts- oder Steuerberatung noch eine fachliche, regulatorische oder
gerichtsfeste Beurteilung.

## So bitte melden

- keine sensiblen Details in ein oeffentliches Issue schreiben
- nutze GitHub private vulnerability reporting auf der Advisories-Seite des Repos
- wenn es nicht sensibel ist, oeffne ein normales Issue mit genug Kontext zur Reproduktion

## Was hilfreich ist

- betroffene Datei oder betroffener Bereich
- moeglicher Impact
- kurze Reproduktion oder Begruendung
- Vorschlag fuer sichere Abhilfe, falls vorhanden
