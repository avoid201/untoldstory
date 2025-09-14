# 🏗️ Projektstruktur - Untold Story

> **Detaillierte Übersicht über die Organisation und Struktur des Projekts**

[![Zurück zur Hauptdokumentation](README.md)](README.md) | [📚 Dokumentations-Index](README.md#-dokumentations-index)

---

## 📋 Inhaltsverzeichnis

- [🎯 Überblick](#-überblick)
- [📁 Verzeichnisstruktur](#-verzeichnisstruktur)
- [🔧 Engine-Systeme](#-engine-systeme)
- [📊 Datenorganisation](#-datenorganisation)
- [🎨 Asset-Management](#-asset-management)
- [🛠️ Entwicklungs-Tools](#️-entwicklungs-tools)
- [📚 Dokumentations-Struktur](#-dokumentations-struktur)
- [🧪 Test-Organisation](#-test-organisation)
- [📦 Archiv-Struktur](#-archiv-struktur)
- [🎯 Best Practices](#-best-practices)

---

## 🎯 Überblick

Die Projektstruktur von **Untold Story** folgt dem Prinzip der **modularen Architektur** mit klarer Trennung von Verantwortlichkeiten. Jedes Verzeichnis hat eine spezifische Aufgabe und trägt zur Gesamtorganisation bei.

### 🏗️ Architektur-Prinzipien

- **Separation of Concerns**: Klare Trennung zwischen Engine, Daten und Assets
- **Modularität**: Wiederverwendbare Komponenten
- **Skalierbarkeit**: Einfache Erweiterung neuer Features
- **Wartbarkeit**: Übersichtliche Struktur für Entwickler
- **Performance**: Optimierte Ressourcenverwaltung

---

## 📁 Verzeichnisstruktur

```
untold_story/
├── 🎮 engine/                    # 🚀 Spiel-Engine (Kern-Systeme)
│   ├── core/                     # 🔧 Grundlegende Engine-Komponenten
│   ├── systems/                  # ⚙️ Spielmechanik-Systeme
│   ├── ui/                       # 🖥️ Benutzeroberfläche
│   └── world/                    # 🌍 Welt- und Karten-Systeme
├── 📊 data/                      # 📋 Spiel-Daten (JSON-Format)
│   ├── monsters/                 # 👹 Monster-Definitionen
│   ├── items/                    # 🎒 Item-Daten
│   ├── maps/                     # 🗺️ Karten-Daten
│   ├── quests/                   # 📜 Quest-Informationen
│   └── config/                   # ⚙️ Konfigurationsdateien
├── 🎨 assets/                    # 🖼️ Grafik- und Audio-Ressourcen
│   ├── graphics/                 # 🎨 Visuelle Assets
│   ├── audio/                    # 🔊 Audio-Assets
│   ├── fonts/                    # 🔤 Schriftarten
│   └── shaders/                  # ✨ Grafik-Shader
├── 📚 docs/                      # 📖 Alle Dokumentation
│   ├── README.md                 # 🏠 Hauptdokumentation
│   ├── features/                 # 🎯 Feature-Dokumentation
│   ├── guides/                   # 📖 Entwicklungs-Guides
│   ├── technical/                # ⚙️ Technische Dokumentation
│   ├── summaries/                # 📋 Implementierungs-Zusammenfassungen
│   └── reports/                  # 📊 Entwicklungsberichte
├── 🛠️ tools/                     # 🔧 Entwicklungs- und Utility-Tools
│   ├── tileset_tools/            # 🎨 Tileset-Verarbeitung
│   ├── validation_tools/         # ✅ Daten-Validierung
│   ├── utility_tools/            # 🛠️ Allgemeine Utilities
│   └── build_tools/              # 🏗️ Build- und Deployment
├── 🧪 tests/                     # 🧪 Test-Suite
│   ├── unit/                     # 🔬 Unit-Tests
│   ├── integration/              # 🔗 Integrations-Tests
│   └── performance/              # ⚡ Performance-Tests
├── 📦 archive/                   # 📦 Abgeschlossene Aufgaben
│   ├── completed_tasks/          # ✅ Fertiggestellte Features
│   ├── old_versions/             # 📋 Alte Versionen
│   └── research/                 # 🔬 Forschungs-Ergebnisse
├── 🚀 main.py                    # 🎮 Spiel-Einstiegspunkt
├── 📦 requirements.txt            # 🐍 Python-Abhängigkeiten
├── ⚙️ config.py                   # ⚙️ Hauptkonfiguration
├── 🧪 test_runner.py             # 🧪 Test-Ausführung
└── 📖 README.md                  # 🏠 Projekt-Übersicht
```

---

## 🔧 Engine-Systeme

### 🚀 Core-Engine (`engine/core/`)

Das **Core-System** bildet das Fundament der gesamten Engine und verwaltet die grundlegenden Spielmechanismen.

#### 📁 Verzeichnisstruktur
```
engine/core/
├── __init__.py                   # 🐍 Python-Paket-Initialisierung
├── game_loop.py                  # 🔄 Hauptspielschleife
├── scene_manager.py              # 🎭 Szenen-Verwaltung
├── resource_manager.py           # 📦 Ressourcen-Management
├── input_handler.py              # ⌨️ Eingabe-Verarbeitung
├── audio_manager.py              # 🔊 Audio-System
├── renderer.py                   # 🎨 Rendering-Engine
└── debug_system.py               # 🐛 Debug-Funktionen
```

#### 🎯 Hauptkomponenten

- **Game Loop**: Hauptspielschleife mit FPS-Kontrolle
- **Scene Manager**: Verwaltung verschiedener Spielszenen
- **Resource Manager**: Asset-Loading und -Caching
- **Input Handler**: Einheitliche Eingabe-Verarbeitung
- **Audio Manager**: Musik und Soundeffekte
- **Renderer**: Hardware-beschleunigtes Rendering
- **Debug System**: Entwickler-Tools (TAB-Taste)

### ⚙️ Spielsysteme (`engine/systems/`)

Die **Spielsysteme** implementieren die eigentlichen Spielmechaniken und -logik.

#### 📁 Verzeichnisstruktur
```
engine/systems/
├── __init__.py                   # 🐍 Python-Paket-Initialisierung
├── battle_system.py              # ⚔️ Kampfsystem
├── monster_system.py             # 👹 Monster-Verwaltung
├── item_system.py                # 🎒 Item-System
├── quest_system.py               # 📜 Quest-System
├── save_system.py                # 💾 Speichersystem
├── synthesis_system.py           # 🔬 Monster-Synthese
├── encounter_system.py           # 🎯 Begegnungs-System
└── world_system.py               # 🌍 Welt-Verwaltung
```

#### 🎯 Hauptsysteme

- **Battle System**: Turn-basiertes Kampfsystem
- **Monster System**: Monster-Verwaltung und -Entwicklung
- **Item System**: Item-Verwaltung und -Verwendung
- **Quest System**: Quest-Logik und -Fortschritt
- **Save System**: Speichern/Laden mit JSON/ZIP
- **Synthesis System**: Monster-Fusion
- **Encounter System**: Zufällige Begegnungen
- **World System**: Welt-Verwaltung und -Logik

### 🖥️ UI-System (`engine/ui/`)

Das **UI-System** verwaltet alle Benutzeroberflächen-Elemente und Menüs.

#### 📁 Verzeichnisstruktur
```
engine/ui/
├── __init__.py                   # 🐍 Python-Paket-Initialisierung
├── base_ui.py                    # 🏗️ Basis-UI-Klasse
├── menu_system.py                # 📋 Menü-System
├── battle_ui.py                  # ⚔️ Kampf-Interface
├── inventory_ui.py               # 🎒 Inventar-Interface
├── monster_ui.py                 # 👹 Monster-Interface
├── world_ui.py                   # 🌍 Welt-Interface
├── dialog_system.py              # 💬 Dialog-System
└── hud.py                        # 🖥️ Heads-Up-Display
```

#### 🎯 UI-Komponenten

- **Base UI**: Gemeinsame UI-Funktionalitäten
- **Menu System**: Hauptmenüs und Untermenüs
- **Battle UI**: Kampf-Interface und -Animationen
- **Inventory UI**: Inventar-Verwaltung
- **Monster UI**: Monster-Status und -Verwaltung
- **World UI**: Welt-Interface und -Kontrolle
- **Dialog System**: Gespräche und Texte
- **HUD**: Spieler-Informationen

### 🌍 Welt-System (`engine/world/`)

Das **Welt-System** verwaltet Karten, Entitäten und die Spielwelt.

#### 📁 Verzeichnisstruktur
```
engine/world/
├── __init__.py                   # 🐍 Python-Paket-Initialisierung
├── map_manager.py                # 🗺️ Karten-Verwaltung
├── entity_manager.py             # 👤 Entitäten-Verwaltung
├── camera_system.py              # 📷 Kamera-System
├── collision_system.py           # 💥 Kollisionserkennung
├── pathfinding.py                # 🛤️ Wegfindung
├── weather_system.py             # 🌤️ Wetter-System
└── event_system.py               # 🎭 Event-System
```

#### 🎯 Welt-Komponenten

- **Map Manager**: Karten-Loading und -Verwaltung
- **Entity Manager**: Spieler, NPCs, Monster
- **Camera System**: Kamera-Bewegung und -Zoom
- **Collision System**: Kollisionserkennung
- **Pathfinding**: Wegfindung für NPCs
- **Weather System**: Dynamisches Wetter
- **Event System**: Welt-Events und -Trigger

---

## 📊 Datenorganisation

### 📋 Datenstruktur (`data/`)

Alle Spiel-Daten werden in **JSON-Format** gespeichert, was eine einfache Bearbeitung und Wartung ermöglicht.

#### 📁 Verzeichnisstruktur
```
data/
├── monsters/                     # 👹 Monster-Definitionen
│   ├── types.json               # 🏷️ Monster-Typen
│   ├── ranks.json               # 🏆 Monster-Ränge
│   ├── abilities.json           # ⚡ Monster-Fähigkeiten
│   └── evolution.json           # 🔄 Evolutions-Pfade
├── items/                       # 🎒 Item-Daten
│   ├── categories.json          # 📂 Item-Kategorien
│   ├── effects.json             # ✨ Item-Effekte
│   └── recipes.json             # 🧪 Crafting-Rezepte
├── maps/                        # 🗺️ Karten-Daten
│   ├── tilesets.json            # 🎨 Tileset-Definitionen
│   ├── layers.json              # 📚 Karten-Ebenen
│   └── collisions.json          # 💥 Kollisions-Daten
├── quests/                      # 📜 Quest-Informationen
│   ├── main_quests.json         # 🎯 Haupt-Quests
│   ├── side_quests.json         # 🔍 Neben-Quests
│   └── rewards.json             # 🎁 Quest-Belohnungen
└── config/                      # ⚙️ Konfigurationsdateien
    ├── game_config.json         # 🎮 Spiel-Konfiguration
    ├── audio_config.json        # 🔊 Audio-Einstellungen
    └── graphics_config.json     # 🎨 Grafik-Einstellungen
```

#### 🎯 Datenformate

- **JSON-Struktur**: Hierarchische Datenorganisation
- **Schema-Validierung**: Automatische Datenüberprüfung
- **Versionierung**: Daten-Versionskontrolle
- **Backup-System**: Automatische Datensicherung

---

## 🎨 Asset-Management

### 🖼️ Grafik-Assets (`assets/graphics/`)

Alle visuellen Assets werden in verschiedenen Formaten und Auflösungen bereitgestellt.

#### 📁 Verzeichnisstruktur
```
assets/graphics/
├── sprites/                      # 🎭 Charakter-Sprites
│   ├── player/                   # 👤 Spieler-Charakter
│   ├── npcs/                     # 👥 NPCs
│   ├── monsters/                 # 👹 Monster-Sprites
│   └── effects/                  # ✨ Effekt-Sprites
├── tilesets/                     # 🎨 Karten-Tilesets
│   ├── outdoor/                  # 🌳 Außen-Bereiche
│   ├── indoor/                   # 🏠 Innen-Bereiche
│   ├── dungeons/                 # 🕳️ Dungeon-Bereiche
│   └── ui/                       # 🖥️ UI-Elemente
├── backgrounds/                  # 🖼️ Hintergrundbilder
├── icons/                        # 🔖 Icon-Sammlung
└── animations/                   # 🎬 Animations-Sequenzen
```

#### 🎯 Asset-Spezifikationen

- **Auflösung**: 320×180 (logisch), 1280×720 (skaliert)
- **Format**: PNG für Transparenz, JPG für Hintergründe
- **Farbpalette**: 256-Farben für Retro-Look
- **Animation**: Frame-basierte Animationen

### 🔊 Audio-Assets (`assets/audio/`)

Audio-Assets umfassen Musik, Soundeffekte und Sprachausgabe.

#### 📁 Verzeichnisstruktur
```
assets/audio/
├── music/                        # 🎵 Hintergrundmusik
│   ├── main_theme/               # 🎼 Hauptthema
│   ├── battle/                   # ⚔️ Kampfmusik
│   ├── towns/                    # 🏘️ Stadtmusik
│   └── dungeons/                 # 🕳️ Dungeon-Musik
├── sfx/                          # 🔊 Soundeffekte
│   ├── ui/                       # 🖥️ UI-Sounds
│   ├── battle/                   # ⚔️ Kampf-Sounds
│   ├── environment/              # 🌍 Umwelt-Sounds
│   └── monsters/                 # 👹 Monster-Sounds
└── voice/                        # 🗣️ Sprachausgabe
    ├── german/                   # 🇩🇪 Deutsche Sprache
    └── ruhrpott/                 # 🏭 Ruhrpott-Dialekt
```

#### 🎯 Audio-Spezifikationen

- **Format**: OGG für Musik, WAV für Soundeffekte
- **Qualität**: 44.1 kHz, 16-bit
- **Komprimierung**: Vorbis für Musik
- **Sprachausgabe**: Deutsche Lokalisierung

---

## 🛠️ Entwicklungs-Tools

### 🎨 Tileset-Tools (`tools/tileset_tools/`)

Tools für die Verarbeitung und Optimierung von Tilesets.

#### 📁 Verzeichnisstruktur
```
tools/tileset_tools/
├── __init__.py                   # 🐍 Python-Paket-Initialisierung
├── tileset_cutter.py             # ✂️ Tileset-Aufteilung
├── advanced_tileset_cutter.py    # 🔧 Erweiterter Tileset-Cutter
├── tileset_optimizer.py          # ⚡ Tileset-Optimierung
├── collision_generator.py        # 💥 Kollisions-Generator
└── tileset_validator.py          # ✅ Tileset-Validierung
```

#### 🎯 Tool-Funktionen

- **Tileset-Cutting**: Automatische Tileset-Aufteilung
- **Optimierung**: Größen- und Qualitätsoptimierung
- **Kollisionserkennung**: Automatische Kollisions-Daten
- **Validierung**: Tileset-Integritätsprüfung

### ✅ Validierungs-Tools (`tools/validation_tools/`)

Tools für die Validierung und Qualitätssicherung von Daten und Assets.

#### 📁 Verzeichnisstruktur
```
tools/validation_tools/
├── __init__.py                   # 🐍 Python-Paket-Initialisierung
├── data_validator.py             # 📊 Daten-Validierung
├── enhanced_validator.py         # 🔧 Erweiterte Validierung
├── asset_validator.py            # 🎨 Asset-Validierung
├── performance_validator.py      # ⚡ Performance-Validierung
└── integration_validator.py      # 🔗 Integrations-Validierung
```

#### 🎯 Validierungs-Funktionen

- **Daten-Validierung**: JSON-Schema-Überprüfung
- **Asset-Validierung**: Grafik- und Audio-Überprüfung
- **Performance-Validierung**: Leistungs-Tests
- **Integrations-Validierung**: System-Integration-Tests

---

## 📚 Dokumentations-Struktur

### 🏠 Hauptdokumentation (`docs/`)

Alle Projekt-Dokumentation ist zentral im `docs/` Verzeichnis organisiert.

#### 📁 Verzeichnisstruktur
```
docs/
├── README.md                     # 🏠 Hauptdokumentation
├── PROJECT_STRUCTURE.md          # 🏗️ Projektstruktur (Diese Datei)
├── features/                     # 🎯 Feature-Dokumentation
│   ├── BATTLE_SYSTEM.md          # ⚔️ Kampfsystem
│   ├── MONSTER_SYSTEM.md         # 👹 Monster-System
│   ├── ITEM_SYSTEM.md            # 🎒 Item-System
│   └── WORLD_SYSTEM.md           # 🌍 Welt-System
├── guides/                       # 📖 Entwicklungs-Guides
│   ├── BEGINNER_GUIDE.md         # 🚀 Anfänger-Guide
│   ├── SYSTEM_INTEGRATION.md     # 🔗 System-Integration
│   ├── ASSET_INTEGRATION.md      # 🎨 Asset-Integration
│   └── TESTING_GUIDE.md          # 🧪 Testing-Guide
├── technical/                    # ⚙️ Technische Dokumentation
│   ├── ENGINE_ARCHITECTURE.md    # 🏗️ Engine-Architektur
│   ├── RESOURCE_MANAGEMENT.md    # 📦 Ressourcen-Management
│   ├── PERFORMANCE_OPTIMIZATION.md # ⚡ Performance-Optimierung
│   └── DEBUG_SYSTEM.md           # 🐛 Debug-System
├── summaries/                    # 📋 Implementierungs-Zusammenfassungen
│   ├── IMPLEMENTATION_STATUS.md  # 📊 Implementierungs-Status
│   ├── SYSTEM_UPDATES.md         # 🔄 System-Updates
│   └── MIGRATION_GUIDES.md       # 🚚 Migration-Guides
└── reports/                      # 📊 Entwicklungsberichte
    ├── WEEKLY_UPDATES.md         # 📅 Wöchentliche Updates
    ├── MILESTONE_REPORTS.md      # 🎯 Milestone-Berichte
    └── BUG_REPORTS.md            # 🐛 Bug-Reports
```

#### 🎯 Dokumentations-Kategorien

- **Features**: Spiel-Feature-Beschreibungen
- **Guides**: Schritt-für-Schritt Anleitungen
- **Technical**: Technische Implementierungsdetails
- **Summaries**: Implementierungs-Zusammenfassungen
- **Reports**: Entwicklungs-Status und -Berichte

---

## 🧪 Test-Organisation

### 🧪 Test-Struktur (`tests/`)

Umfassende Test-Suite für alle Projekt-Komponenten.

#### 📁 Verzeichnisstruktur
```
tests/
├── __init__.py                   # 🐍 Python-Paket-Initialisierung
├── unit/                         # 🔬 Unit-Tests
│   ├── test_engine/              # 🚀 Engine-Tests
│   ├── test_systems/             # ⚙️ System-Tests
│   ├── test_ui/                  # 🖥️ UI-Tests
│   └── test_world/               # 🌍 Welt-Tests
├── integration/                  # 🔗 Integrations-Tests
│   ├── test_system_integration/  # 🔗 System-Integration
│   ├── test_data_integration/    # 📊 Daten-Integration
│   └── test_asset_integration/   # 🎨 Asset-Integration
├── performance/                  # ⚡ Performance-Tests
│   ├── test_rendering/           # 🎨 Rendering-Performance
│   ├── test_audio/               # 🔊 Audio-Performance
│   └── test_memory/              # 💾 Speicher-Performance
├── conftest.py                   # ⚙️ Test-Konfiguration
└── test_runner.py                # 🏃 Test-Ausführung
```

#### 🎯 Test-Kategorien

- **Unit Tests**: Einzelne Komponenten-Tests
- **Integration Tests**: System-Integration-Tests
- **Performance Tests**: Leistungs- und Optimierungs-Tests
- **Test Runner**: Zentrale Test-Ausführung

---

## 📦 Archiv-Struktur

### 📦 Archiv-Organisation (`archive/`)

Das Archiv verwaltet abgeschlossene Aufgaben und historische Versionen.

#### 📁 Verzeichnisstruktur
```
archive/
├── completed_tasks/              # ✅ Fertiggestellte Features
│   ├── PROJECT_ORGANIZATION.md   # 🏗️ Projekt-Organisation
│   ├── ARCHIVE_SUMMARY.md        # 📋 Archiv-Zusammenfassung
│   └── FEATURE_IMPLEMENTATIONS/  # 🎯 Feature-Implementierungen
├── old_versions/                 # 📋 Alte Versionen
│   ├── v0.1/                     # 📦 Version 0.1
│   ├── v0.2/                     # 📦 Version 0.2
│   └── v0.3/                     # 📦 Version 0.3
└── research/                     # 🔬 Forschungs-Ergebnisse
    ├── GAME_MECHANICS.md         # 🎮 Spielmechaniken-Forschung
    ├── TECHNICAL_APPROACHES.md   # 🔧 Technische Ansätze
    └── ART_STYLE_RESEARCH.md     # 🎨 Kunststil-Forschung
```

#### 🎯 Archiv-Kategorien

- **Completed Tasks**: Fertiggestellte Features und Aufgaben
- **Old Versions**: Historische Projektversionen
- **Research**: Forschungs-Ergebnisse und -Entscheidungen

---

## 🎯 Best Practices

### 🏗️ Struktur-Prinzipien

#### 📁 Verzeichnis-Organisation
- **Klare Hierarchie**: Logische Verzeichnisstruktur
- **Konsistente Namensgebung**: Einheitliche Benennungskonventionen
- **Modulare Aufteilung**: Wiederverwendbare Komponenten
- **Dokumentation**: Jedes Verzeichnis hat eine klare Aufgabe

#### 🔧 Code-Organisation
- **Separation of Concerns**: Klare Trennung von Verantwortlichkeiten
- **Interface-First**: Definiere Schnittstellen vor Implementierung
- **Dependency Injection**: Lose gekoppelte Komponenten
- **Error Handling**: Robuste Fehlerbehandlung

#### 📚 Dokumentations-Standards
- **Markdown-Format**: Einheitliche Dokumentationssprache
- **Strukturierte Inhalte**: Klare Gliederung und Navigation
- **Code-Beispiele**: Praktische Implementierungsbeispiele
- **Regelmäßige Updates**: Aktuelle Dokumentation

### 🚀 Entwicklungs-Workflow

#### 📋 Feature-Entwicklung
1. **Planung**: Feature in Dokumentation definieren
2. **Implementierung**: Code nach definierten Standards
3. **Testing**: Umfassende Tests für neue Features
4. **Dokumentation**: Feature-Dokumentation aktualisieren
5. **Review**: Code-Review und Qualitätssicherung

#### 🔄 Wartung und Updates
- **Regelmäßige Reviews**: Monatliche Struktur-Überprüfung
- **Performance-Monitoring**: Kontinuierliche Leistungsüberwachung
- **Dependency-Updates**: Aktualisierung von Abhängigkeiten
- **Archiv-Pflege**: Regelmäßige Archiv-Bereinigung

---

## 🎯 Nächste Schritte

1. **Verstehe die [Engine-Architektur](technical/ENGINE_ARCHITECTURE.md)**
2. **Lies die [Feature-Dokumentation](features/)**
3. **Folge den [Entwicklungs-Guides](guides/)**
4. **Schau dir die [technische Dokumentation](technical/) an**

---

**Zurück zur [Hauptdokumentation](README.md)** | **📚 [Dokumentations-Index](README.md#-dokumentations-index)**

---

*"Dat is ja mal ne richtig durchdachte Struktur, wa? Jetzt kannste richtig strukturiert entwickeln!"* 🏗️✨
