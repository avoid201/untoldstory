# 🧹 UNTOLD STORY - PROJEKT AUFRÄUMPLAN

## 📊 Aktuelle Situation

### Root-Verzeichnis Chaos:
- **67 einzelne Dateien** im Root (viel zu viele!)
- **Dutzende Test-Scripts** (test_*.py)
- **Viele Fix-Scripts** (fix_*.py, *_fix.py)
- **Massenweise Reports** (*.md Reports)
- **Mehrere Duplikate** der MASTERMAP

## 🎯 Ziel-Struktur

```
untold_story/
│
├── README.md                    # Haupt-Dokumentation
├── requirements.txt             # Dependencies
├── main.py                      # Einziger Entry Point
├── settings.toml               # Konfiguration
│
├── engine/                     # ✅ Bereits gut strukturiert
│   ├── core/                  # Core-System
│   ├── systems/               # Game-Systeme
│   ├── scenes/                # Game-Szenen
│   ├── ui/                    # UI-Komponenten
│   ├── world/                 # Welt-System
│   ├── graphics/              # Grafik-System
│   ├── audio/                 # Audio-System
│   └── items/                 # Item-System
│
├── data/                      # ✅ Game-Daten
│   ├── monsters/
│   ├── moves/
│   ├── items/
│   └── maps/
│
├── assets/                    # ✅ Assets
│   ├── sprites/
│   ├── sounds/
│   └── fonts/
│
├── docs/                      # 📚 Dokumentation
│   ├── architecture/          # NEU: Architektur-Docs
│   ├── guides/                # NEU: Entwickler-Guides
│   └── reports/               # NEU: Alle Reports hierhin
│
├── tests/                     # 🧪 Alle Tests
│   ├── unit/                  # Unit-Tests
│   ├── integration/           # Integration-Tests
│   └── performance/           # Performance-Tests
│
├── tools/                     # 🔧 Development Tools
│   ├── generators/            # Code-Generatoren
│   ├── analyzers/             # Code-Analyzer
│   └── migration/             # Migration-Tools
│
├── scripts/                   # NEU: Utility Scripts
│   ├── fixes/                 # Alle Fix-Scripts
│   ├── cleanup/               # Cleanup-Scripts
│   └── debug/                 # Debug-Scripts
│
├── archive/                   # 📦 Archiv (erweitert)
│   ├── old_implementations/
│   ├── deprecated_tests/
│   ├── legacy_reports/
│   └── experimental/
│
├── saves/                     # ✅ Spielstände
└── logs/                      # ✅ Logs
```

## 📋 Aufräum-Aktionen

### 1. **Reports verschieben** (24 Dateien)
```
MOVE TO: docs/reports/
- BATTLESCENE_*.md
- BATTLE_SYSTEM_*.md
- CLEANUP_*.md
- *_REPORT.md
- *_SUCCESS.md
- MASTERMAP_*.md (außer der aktuellen)
```

### 2. **Test-Scripts verschieben** (28 Dateien)
```
MOVE TO: tests/integration/
- test_*.py
- demo_*.py
- quick_test*.py

MOVE TO: tests/performance/
- test_performance*.py
```

### 3. **Fix-Scripts archivieren** (20 Dateien)
```
MOVE TO: scripts/fixes/
- fix_*.py
- *_fix.py
- *_fixer.py
- cleanup_*.py
- refactor_*.py
```

### 4. **Tools organisieren** (8 Dateien)
```
MOVE TO: tools/
- mastermap_generator.py
- enhanced_mastermap_generator.py
- validate_migration.py
- verify_integration.py
- conflict_*.py
- code_analysis.json
```

### 5. **Scripts konsolidieren** (6 Dateien)
```
MOVE TO: scripts/
- run_*.py
- start_game.py
- local_test.py
- install_dependencies.py
- *.sh Scripts
```

### 6. **Dokumentation aktualisieren**
```
KEEP IN ROOT:
- README.md (Hauptdokumentation)
- requirements.txt
- requirements-testing.txt
- settings.toml
- main.py

CREATE NEW:
- QUICKSTART.md (Schnellstart-Guide)
- ARCHITECTURE.md (Übersicht)
```

### 7. **Zu löschende/archivierende Dateien**
```
ARCHIVE:
- Alle alten Prompts (PROMPT_*.md)
- Duplicate MASTERMAP Versionen
- code_analysis_report.md (veraltet)
- untold-story-battle-system.md (duplicate)
```

### 8. **Engine-Ordner aufräumen**
```
engine/
- types_refactored.py -> systems/types_refactored.py
- Alle __pycache__ Ordner löschen
- .DS_Store Dateien löschen
```

## 🚀 Ausführungsplan

### Phase 1: Backup erstellen
```bash
# Komplettes Backup erstellen
cp -r /Users/leon/Desktop/untold_story /Users/leon/Desktop/untold_story_backup_$(date +%Y%m%d)
```

### Phase 2: Ordner-Struktur erstellen
- docs/reports/
- docs/guides/
- docs/architecture/
- tests/unit/
- tests/integration/
- tests/performance/
- scripts/fixes/
- scripts/cleanup/
- scripts/debug/
- tools/generators/
- tools/analyzers/
- tools/migration/

### Phase 3: Dateien verschieben
1. Reports → docs/reports/
2. Tests → tests/
3. Fix-Scripts → scripts/fixes/
4. Tools → tools/
5. Alte Versionen → archive/

### Phase 4: Aufräumen
- Alle __pycache__ löschen
- Alle .DS_Store löschen
- Duplikate entfernen
- Veraltete Dateien archivieren

### Phase 5: Dokumentation
- README.md aktualisieren
- QUICKSTART.md erstellen
- ARCHITECTURE.md erstellen
- Ordner-README.md files hinzufügen

## ⚠️ Wichtige Dateien (NICHT verschieben/löschen)
- main.py (Entry Point)
- requirements.txt
- settings.toml
- .git/ (Version Control)
- .venv/ (Virtual Environment)
- engine/ (Core Code)
- data/ (Game Data)
- assets/ (Game Assets)

## 📈 Erwartetes Ergebnis
- **Root-Verzeichnis:** Von 67 auf ~5 Dateien reduziert
- **Bessere Organisation:** Klare Trennung von Code, Tests, Docs, Tools
- **Einfachere Navigation:** Logische Struktur
- **Wartbarkeit:** Leichter zu finden und zu pflegen

## 🔧 Automatisierungs-Script
Soll ich ein Python-Script erstellen, das diese Aufräumarbeiten automatisch durchführt?
