# Changelog

Alle wesentlichen Änderungen an der DFG-Kursverwaltung werden in dieser Datei dokumentiert.

## [0.1.0] - 2026-08-23

### Hinzugefügt

* Python-Projekt für die DFG-Kursverwaltung erstellt
* Virtuelle Python-Umgebung eingerichtet
* PySide6 als GUI-Framework eingerichtet
* SQLite als Datenbanksystem vorgesehen
* openpyxl für Excel-Import und -Export eingerichtet
* PyInstaller für die spätere Erstellung ausführbarer Anwendungen eingerichtet
* Grundlegende Projektstruktur erstellt
* Plattformübergreifende Entwicklung für Windows, macOS und Linux vorgesehen
* Projektmetadaten in `VERSION` angelegt

### Migration

* Bestehende PowerShell-Anwendung `DFG_Pfannenstiel_Adress_und_Kursverwaltung.ps1` dient als fachliche Grundlage
* Migration der bestehenden XML-Daten in die neue SQLite-Datenbank vorgesehen
