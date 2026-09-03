# Changelog

Alle wesentlichen Änderungen an der DFG-Kursverwaltung werden in dieser Datei dokumentiert.

## [0.3.0] - 2026-09-03

### Hinzugefügt

* Portablen Windows-Build mit PyInstaller im `onedir`-Format eingerichtet
* Reproduzierbares PowerShell-Buildskript `scripts/build-windows.ps1` hinzugefügt
* Windows-Anwendungsicon für EXE, Titelleiste und Taskleiste eingerichtet

### Geändert

* Ressourcenpfade für den Betrieb als gepackte PyInstaller-Anwendung angepasst
* Benutzerrolle Instruktor vollständig von individuellen Kurstagberechtigungen entkoppelt

### Datenbank

* Datenbankschema auf Schema-Version 10 erweitert
* Veraltete Tabelle `benutzer_kurstage` und zugehörigen Index entfernt
* Migration von Schema 9 auf Schema 10 mit Foreign-Key- und Integritätsprüfung umgesetzt
* Erstellung einer neuen Datenbank direkt mit Schema-Version 10 verifiziert

## [0.2.0] - 2026-09-03

### Hinzugefügt

* SQLite-Datenmodell für Personen, Telefonnummern, Drohnen, Lehrgänge, Kurstage, Standorte, Kurszuordnungen und Kursergebnisse umgesetzt
* Personenrollen mit Gültigkeitszeiträumen und Historie eingeführt
* Benutzerrollen und Berechtigungsmodell für Administrator, Kursverwaltung und Instruktor umgesetzt
* GUI für Personen, Lehrgänge, Kurstage, Standorte und Kurszuordnungen erweitert
* Kursergebnisse für Teilnehmer mit den Ergebnissen `Bestanden`, `Nicht bestanden` und `Attest erteilt` eingeführt
* Kursatteste für alle Lehrgangstypen ermöglicht
* Anzeige und Zusammenfassung der Kursergebnisse in Kurszuordnungen und Personenansicht ergänzt
* CSV-Import und -Export für Kursergebnisse umgesetzt
* Sicherungs- und Wiederherstellungsfunktionen erweitert
* Mehrsprachige Benutzeroberfläche für Deutsch, Englisch, Französisch, Italienisch und Rätoromanisch umgesetzt

### Geändert

* Benutzer und Personen fachlich klar getrennt
* Berechtigungen der Benutzerrolle Instruktor überarbeitet
* Kursbearbeitung für Instruktoren von einer individuellen Kurstagzuordnung entkoppelt
* Bezeichnung `Prüfungsergebnis` in der Benutzeroberfläche durch `Kursergebnis` ersetzt
* Kursergebnis von einem booleschen Prüfungsstatus auf einen allgemeinen Ergebnistyp umgestellt
* Import- und Exportformat für Kursergebnisse von `Bestanden` auf `Ergebnis` umgestellt

### Datenbank

* Datenbankschema schrittweise bis Schema-Version 9 erweitert
* Schema 8 auf Schema 9 migriert
* Feld `bestanden` der Kursergebnisse durch `ergebnis` ersetzt
* Bestehende Werte bei der Migration nach `passed` beziehungsweise `failed` übernommen
* Neuer Ergebniswert `attested` für erteilte Kursatteste eingeführt
* Migration mit Datensatz-, Foreign-Key- und Integritätsprüfungen abgesichert

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
