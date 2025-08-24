# Projektorganisation - Untold Story

## Aktuelle Probleme
- Viele verstreute README/Dokumentationsdateien im Root-Verzeichnis
- Test-Dateien vermischt mit Hauptcode
- Archive und Backup-Dateien unorganisiert
- Tools und Skripte verstreut

## Organisationsplan

### 1. Dokumentation konsolidieren
Alle README/Dokumentationsdateien in `docs/` verschieben:
- `Untold_Story_Uebersicht.md` → `docs/README.md` (Hauptdokumentation)
- Alle `*_SUMMARY.md` → `docs/summaries/`
- Alle `*_README.md` → `docs/readmes/`
- Alle `*_REPORT.md` → `docs/reports/`

### 2. Tests organisieren
Alle Test-Dateien in `tests/` verschieben:
- Alle `test_*.py` → `tests/`
- Unterkategorien: `tests/battle/`, `tests/story/`, `tests/systems/`

### 3. Tools konsolidieren
Alle Tool-Skripte in `tools/` verschieben:
- Alle `*_fix.py`, `*_migration.py`, `*_validator.py` → `tools/`
- Alle `create_*.py` → `tools/`

### 4. Archive bereinigen
- `archive/` → Nur wichtige Backups behalten
- `tilesets_to_cut/` → In `tools/` integrieren oder löschen

### 5. Root-Verzeichnis säubern
Nur essenzielle Dateien im Root behalten:
- `main.py`
- `start_game.py`
- `requirements.txt`
- `settings.toml`
- `.cursorrules`
- `README.md` (Hauptdokumentation)

### 6. Neue Struktur
```
untold_story/
├── README.md (Hauptdokumentation)
├── main.py
├── start_game.py
├── requirements.txt
├── settings.toml
├── .cursorrules
├── engine/ (Hauptcode)
├── data/ (Spieldaten)
├── assets/ (Grafiken/Audio)
├── docs/ (Alle Dokumentation)
│   ├── README.md
│   ├── summaries/
│   ├── readmes/
│   └── reports/
├── tests/ (Alle Tests)
│   ├── battle/
│   ├── story/
│   └── systems/
├── tools/ (Alle Tools/Skripte)
├── saves/ (Spielstände)
└── archive/ (Nur wichtige Backups)
```

## Wichtige Pfade die NICHT unterbrochen werden dürfen
- `engine/` - Hauptcode
- `data/` - Spieldaten
- `assets/` - Assets
- `saves/` - Spielstände
- Import-Pfade in Python-Dateien
- Relative Pfade in Konfigurationsdateien
