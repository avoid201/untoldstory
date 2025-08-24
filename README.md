# 🎮 Untold Story - 2D RPG

> **Ein Monster-Taming RPG im Ruhrpott-Setting mit deutscher Lokalisierung**

[![Python](https://img.shields.io/badge/Python-3.13.5-blue.svg)](https://www.python.org/)
[![Pygame](https://img.shields.io/badge/Pygame-CE-2.5+-green.svg)](https://pygame.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Entwicklung-orange.svg)](docs/reports/)

## 📋 Inhaltsverzeichnis

- [🎯 Über das Projekt](#-über-das-projekt)
- [🚀 Schnellstart](#-schnellstart)
- [🏗️ Projektstruktur](#️-projektstruktur)
- [📚 Dokumentation](#-dokumentation)
- [🛠️ Entwicklung](#️-entwicklung)
- [🤝 Beitragen](#-beitragen)
- [📄 Lizenz](#-lizenz)

## 🎯 Über das Projekt

**Untold Story** ist ein 2D-RPG im Stil von Dragon Quest Monsters und Pokémon, angesiedelt im Ruhrpott mit authentischer deutscher Lokalisierung in Ruhrpott-Dialekt.

### ✨ Hauptmerkmale

- **🎭 Monster-Taming System**: Fange, trainiere und entwickle Monster
- **⚔️ Turn-basiertes Kampfsystem**: 12 Typen, 9 Ränge (F-X)
- **🗺️ Ruhrpott-Welt**: Authentische deutsche Umgebung
- **🔧 Synthese-System**: Monster-Fusion für neue Kreaturen
- **💾 Speichersystem**: JSON-basiert mit ZIP-Kompression
- **🎨 Pixel-Art Grafik**: 320×180 Auflösung, skaliert auf 1280×720

### 🎮 Spielmechaniken

- **Grid-basierte Bewegung**: 16×16 Tile-System
- **Kampfphasen**: Intro → Input → Execution → Aftermath → End
- **Party-System**: Maximal 6 Monster, Storage-Boxen für Überschuss
- **Taming**: DQM-Stil (keine Pokébälle)

## 🚀 Schnellstart

### Voraussetzungen

- Python 3.13.5+
- pygame-ce 2.5+
- Git

### Installation

```bash
# Repository klonen
git clone https://github.com/yourusername/untold_story.git
cd untold_story

# Virtuelle Umgebung erstellen (empfohlen)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# oder
venv\Scripts\activate     # Windows

# Abhängigkeiten installieren
pip install -r requirements.txt

# Spiel starten
python main.py
```

### 🎯 Erste Schritte

1. **Spiel starten**: `python main.py`
2. **Debug-Modus**: TAB-Taste für Entwicklerfunktionen
3. **Steuerung**: Pfeiltasten für Bewegung, ENTER für Interaktion
4. **Speichern**: Automatisch nach wichtigen Events

## 🏗️ Projektstruktur

```
untold_story/
├── 📁 engine/                 # 🎮 Spiel-Engine
│   ├── core/                  # Spielschleife, Szenen, Ressourcen
│   ├── systems/               # Spielmechaniken
│   ├── ui/                    # UI-Komponenten
│   └── world/                 # Karten, Entitäten, Kamera
├── 📁 data/                   # 📊 JSON-Daten
│   ├── monsters/              # Monster-Definitionen
│   ├── items/                 # Item-Daten
│   └── maps/                  # Karten-Daten
├── 📁 assets/                 # 🎨 Grafik & Audio
│   ├── graphics/              # Sprites, Tilesets
│   ├── audio/                 # Musik, Soundeffekte
│   └── fonts/                 # Schriftarten
├── 📁 docs/                   # 📚 Alle Dokumentation
│   ├── README.md              # 🏠 Hauptdokumentation
│   ├── features/              # 🎯 Spiel-Features
│   ├── guides/                # 📖 Entwicklungs-Guides
│   ├── technical/             # ⚙️ Technische Dokumentation
│   ├── summaries/             # 📋 Implementierungs-Zusammenfassungen
│   └── reports/               # 📊 Entwicklungsberichte
├── 📁 tools/                  # 🛠️ Entwicklungs-Tools
├── 📁 tests/                  # 🧪 Tests
├── 📁 archive/                # 📦 Abgeschlossene Aufgaben
├── main.py                    # 🚀 Spiel-Einstiegspunkt
├── requirements.txt            # 📦 Python-Abhängigkeiten
└── README.md                  # 🏠 Diese Datei
```

## 📚 Dokumentation

### 🎯 Übersicht & Features
- **[Spielübersicht](docs/README.md)** - Vollständige Spielbeschreibung
- **[Feature-Übersicht](docs/features/)** - Alle Spiel-Features
- **[Kampfsystem](docs/features/)** - Kampfmechaniken und Systeme
- **[Monster-System](docs/features/)** - Monster, Typen, Ränge
- **[Item-System](docs/features/)** - Items und deren Verwendung

### 📖 Entwicklungs-Guides
- **[Entwicklungs-Guides](docs/guides/)** - Schritt-für-Schritt Anleitungen
- **[System-Integration](docs/guides/)** - Integration verschiedener Systeme
- **[Encounters](docs/guides/)** - Begegnungen und Events

### ⚙️ Technische Dokumentation
- **[Implementierungen](docs/technical/)** - Technische Implementierungen
- **[System-Dokumentation](docs/technical/)** - Detaillierte Systemdokumentation
- **[Migration-Guides](docs/technical/)** - System-Migrationen

### 📋 Zusammenfassungen & Berichte
- **[Implementierungen](docs/summaries/)** - Implementierungs-Zusammenfassungen
- **[System-Updates](docs/summaries/)** - System-Update-Berichte
- **[Entwicklungsberichte](docs/reports/)** - Aktuelle Entwicklungsstände
- **[Status-Updates](docs/reports/)** - Projekt-Status-Updates

## 🛠️ Entwicklung

### 🏗️ Architektur

- **Modulare Struktur**: Fokus auf Wartbarkeit und Erweiterbarkeit
- **Daten-getrieben**: JSON-basierte Konfiguration
- **Ressourcen-Caching**: Optimierte Performance
- **Fehlerbehandlung**: Graceful Degradation bei fehlenden Assets

### 🧪 Entwicklungsumgebung

- **Debug-Modus**: TAB-Taste für Entwicklerfunktionen
- **Deterministische RNG**: Für konsistente Tests
- **Edge-Case-Behandlung**: Robuste Systeme
- **Type Hints**: Vollständige Python-Typisierung

### 📝 Code-Standards

- **Python 3.13.5+**: Moderne Python-Features
- **pygame-ce 2.5+**: Aktuelle Pygame-Version
- **Dataclasses**: Für Datenstrukturen
- **Konsistente Namensgebung**: Klare, beschreibende Namen
- **Dokumentation**: Alle Funktionen und Klassen dokumentiert

## 🤝 Beitragen

### 🚀 Erste Schritte

1. **Fork erstellen**: Repository forken
2. **Branch erstellen**: `git checkout -b feature/neue-funktion`
3. **Änderungen**: Code implementieren und testen
4. **Commit**: Aussagekräftige Commit-Messages
5. **Pull Request**: Detaillierte Beschreibung der Änderungen

### 📋 Beitragsrichtlinien

- **Code-Qualität**: PEP 8, Type Hints, Dokumentation
- **Tests**: Neue Features müssen getestet werden
- **Dokumentation**: Alle Änderungen dokumentieren
- **Deutsche Lokalisierung**: In-Game-Text in Ruhrpott-Dialekt
- **Englische Kommentare**: Code-Kommentare auf Englisch

### 🐛 Bug-Reports

- **Issue erstellen**: Mit detaillierter Beschreibung
- **Reproduzierbarkeit**: Schritte zum Nachstellen
- **System-Info**: OS, Python-Version, Pygame-Version
- **Screenshots**: Bei visuellen Problemen

## 📄 Lizenz

Dieses Projekt steht unter der **MIT-Lizenz**. Siehe [LICENSE](LICENSE) für Details.

---

## 🎯 Nächste Schritte

1. **Schaue in die [Dokumentation](docs/)**
2. **Lies die [Entwicklungs-Guides](docs/guides/)**
3. **Schau dir die [Feature-Übersicht](docs/features/) an**
4. **Starte mit dem [Schnellstart](#-schnellstart)**

---

**Entwickelt mit ❤️ im Ruhrpott**  
*"Ey, wat machste denn da? Lass uns zusammen was Großes erschaffen!"*
