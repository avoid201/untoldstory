# Untold Story - Mastermap für KI-Entwicklung

## 📋 Projekt-Übersicht

**Untold Story** ist ein 2D top-down RPG in Python mit pygame-ce, inspiriert von Dragon Quest Monsters und Pokémon. Das Spiel spielt im Ruhrpott mit deutschen Dialogen und lokalen Slang.

### 🎯 Kern-Features
- **Monster-Taming-System**: DQM-inspiriert (ohne Pokéballs)
- **Turn-based Battle**: Mit 12 Typen und 9 Rängen (F-X)
- **3v3 Battles**: Strategische Teamkämpfe
- **Ruhrpott-Setting**: Deutsche Dialoge mit lokalem Slang
- **Grid-basierte Bewegung**: 16x16 Tiles
- **Synthesis-System**: Monster-Fusion-Mechanik

### 🔧 Technische Specs
- **Python**: 3.13.5+
- **pygame-ce**: 2.5+
- **Auflösung**: Logisch 320×180, skaliert auf 1280×720
- **Ziel-FPS**: 60
- **Speicherformat**: JSON → ZIP

---

## 📁 Projektstruktur

```
untold_story/
├── main.py                    # Haupteinstiegspunkt
├── engine/                    # Haupt-Engine
│   ├── core/                 # Kern-Systeme
│   ├── systems/              # Spielmechaniken
│   ├── ui/                   # UI-Komponenten
│   ├── scenes/              # Szenen-Management
│   ├── world/               # Welt und Entities
│   ├── graphics/            # Rendering und Sprites
│   └── audio/               # Audio-System
├── data/                     # JSON-Daten
├── assets/                   # Grafiken, Audio
├── saves/                    # Spielstände
└── tests/                    # Test-Dateien
```

---

## 🏗️ Engine-Architektur

### Core-Systeme (`engine/core/`)

#### `game.py` - Hauptgame-Loop
- **Klasse**: `Game`
- **Verantwortung**: Scene-Stack, Input, Rendering-Pipeline
- **Wichtige Manager**:
  - `event_processor`: Event-Verarbeitung
  - `debug_overlay_manager`: Debug-UI
  - `story_manager`: Story-Zustand
  - `party_manager`: Monster-Team
  - `sprite_manager`: Grafik-Cache

#### `scene_base.py` - Scene-Interface
- **Klasse**: `Scene` (Abstract Base)
- **Methoden**: `enter()`, `exit()`, `update()`, `draw()`
- **Scene-Stack**: Unterstützt Overlays (z.B. Pause über Field)

#### `resources.py` - Resource-Management
- **Klasse**: `ResourceManager`
- **Features**: LRU-Cache, Memory-Management
- **Unterstützte Formate**: JSON, PNG, Audio
- **Cache-Strategien**: Intelligente Eviction-Policies

#### `config.py` - Zentrale Konfiguration
- **Display**: Logische/Window-Größen
- **Movement**: Geschwindigkeiten, Kollision
- **Paths**: Asset- und Daten-Verzeichnisse
- **Colors**: Standard-Farbpalette

---

## ⚔️ Battle-System (`engine/systems/battle/`)

### Kern-Komponenten

#### `battle.py` - Battle-State-Machine
- **Klassen**: `BattleState`, `BattlePhase`, `BattleType`
- **Phasen**: INIT → START → INPUT → ORDER → RESOLVE → AFTERMATH → END
- **Team-Management**: Player/Enemy Teams mit Active Monsters

#### `battle_controller.py` - Battle-Controller
- **Klasse**: `BattleController`
- **Funktionen**: Turn-Order, Action-Resolution, Victory-Conditions

#### `turn_logic.py` - Turn-System
- **Klassen**: `BattleAction`, `TurnOrder`
- **Action-Types**: Attack, Switch, Item, Flee, Tame
- **Priority-System**: Speed-basierte Turn-Order

#### `damage_calc.py` - Schadens-Berechnung
- **DQM-Formeln**: Komplexe Damage-Calculations
- **Type-Effectiveness**: 12-Type-Chart
- **Stats**: HP/ATK/DEF/MAG/RES/SPD

#### `battle_ai.py` - KI-System
- **Schwierigkeitsgrade**: Easy/Medium/Hard/Boss
- **Move-Selection**: Weighted-Choice basierend auf Effectiveness
- **Strategy-Patterns**: Aggressive, Defensive, Balanced

---

## 👾 Monster-System (`engine/systems/`)

### Monster-Datenstrukturen

#### `monster_instance.py` - Monster-Instanzen
- **Klassen**: `MonsterInstance`, `MonsterSpecies`, `MonsterRank`
- **Stats**: Level-based mit Growth-Curves
- **Status**: BURN, POISON, PARALYSIS, SLEEP, FREEZE, CONFUSION
- **Ranks**: F (Common) → X (Legendary)

#### `monsters.py` - Monster-Database
- **Klasse**: `MonsterDatabase` (Singleton)
- **Features**: Species-Cache, Era-Kategorien (Past/Present/Future)
- **Suche**: By ID, Name, Rank, Type

#### `moves.py` - Move-System
- **Klassen**: `Move`, `MoveEffect`, `MoveExecutor`
- **Categories**: Physical, Magical, Support
- **Targeting**: Enemy, Ally, Self, All, Random
- **Effects**: Damage, Heal, Buff, Debuff, Status

### Gameplay-Systeme

#### `party.py` - Team-Management
- **Klassen**: `PartyManager`, `StorageSystem`
- **Limits**: Max 6 aktive Monster, Storage Boxes für Extras
- **Storage**: 30 Boxen mit je 30 Plätzen

#### `taming.py` - Taming-System
- **DQM-Style**: Ohne Pokéballs
- **Factors**: Monster-Health, Rank, Player-Level
- **Success-Rate**: Dynamische Berechnung

#### `synthesis.py` - Fusion-System
- **Monster-Fusion**: Zwei Monster → Neues Monster
- **Requirements**: Level, Compatibility
- **Results**: Breed-Tables, Inherited Moves

---

## 🎨 UI-System (`engine/ui/`)

### UI-Komponenten

#### `battle_ui.py` - Battle-Interface
- **Klassen**: `BattleUI`, `BattleHUD`, `BattleMenu`
- **Features**: HP-Bars, Damage-Numbers, Menu-Navigation
- **States**: Main, Move-Select, Target-Select, Item-Select

#### `menus.py` - Menu-System
- **Base**: `MenuBase` (Abstract)
- **Implementations**: `PartyMenu`, `QuestMenu`, `InventoryMenu`
- **Navigation**: Arrow-Keys, Confirm/Cancel

#### `dialogue.py` - Dialog-System
- **Klassen**: `DialogueBox`, `DialoguePage`, `DialogueChoice`
- **States**: OPENING, DISPLAYING, WAITING, CLOSING
- **Choices**: Branching Dialogue-Trees

#### `hud.py` - HUD-Elements
- **Persistent UI**: Party-Status, Mini-Map, Buttons
- **Adaptive**: Verschiedene Scene-Modi

---

## 🗺️ Welt-System (`engine/world/`)

### Map-System

#### `area.py` - Spielbare Regionen
- **Klasse**: `Area`
- **Features**: TMX-Support, Layer-Rendering, NPC-Management
- **Performance**: Surface-Caching, Culling

#### `map_loader.py` - Map-Loading
- **Formate**: TMX (Tiled), JSON
- **Features**: Warps, Triggers, Collision-Data
- **Validation**: Map-Integrity-Checks

#### `player.py` - Spieler-Entity
- **Movement**: Grid-based mit smoothing
- **States**: IDLE, WALKING, RUNNING
- **Features**: Ledge-Jumping, Encounter-Triggering

#### `npc.py` - NPC-System
- **Movement-Patterns**: Static, Random, Patrol, Wander, Follow, Flee
- **Interaction**: Dialogue-Trigger, Battle-Challenges
- **Pathfinding**: A*-Algorithm für intelligente Bewegung

---

## 🎮 Szenen-System (`engine/scenes/`)

### Hauptszenen

#### `field_scene.py` - Overworld
- **Features**: Map-Rendering, Player-Movement, NPC-Interaction
- **Encounter-System**: Step-basierte Wild-Battles
- **Transitions**: Map-zu-Map Übergänge

#### `battle_scene.py` - Kampf-Interface
- **Integration**: BattleState + BattleUI
- **Phases**: Complete Battle-Flow
- **Results**: EXP, Items, Money, Captured Monsters

#### `main_menu_scene.py` - Hauptmenü
- **Options**: New Game, Continue, Settings
- **Save-Slots**: 3 Slots mit Metadata

#### `starter_scene.py` - Starter-Auswahl
- **Monster-Selection**: Erste 3 Monster wählen
- **Tutorial**: Einführung in Battle-System

---

## 💾 Daten-Systeme (`data/`)

### JSON-Formate

#### `monsters.json` - Monster-Database
```json
{
  "id": 1,
  "name": "Glutstummel",
  "era": "present",
  "rank": "F",
  "types": ["Feuer"],
  "base_stats": {
    "hp": 40, "atk": 54, "def": 38,
    "mag": 24, "res": 20, "spd": 44
  },
  "growth": {"curve": "fast", "yield": 48},
  "capture_rate": 249,
  "traits": ["Entflammbar"],
  "learnset": [
    {"level": 1, "move": "Kratzer"}
  ],
  "evolution": null
}
```

#### `moves.json` - Move-Database
```json
{
  "id": "ember",
  "name": "Glut",
  "type": "Feuer",
  "category": "mag",
  "power": 40,
  "accuracy": 100,
  "pp": 25,
  "priority": 0,
  "targeting": "enemy",
  "effects": [
    {"kind": "status", "status": "burn", "chance": 10}
  ]
}
```

#### `types.json` - Type-Chart
```json
{
  "types": ["Feuer", "Wasser", "Erde", "Luft", "Pflanze", "Bestie", "Energie", "Chaos", "Seuche", "Mystik", "Gottheit", "Teufel"],
  "chart": [
    {"attacker": "Feuer", "defender": "Wasser", "multiplier": 0.5}
  ]
}
```

---

## 💾 Speicher-System (`engine/systems/save.py`)

### Save-Format
- **Komprimierung**: JSON → ZIP
- **Validierung**: Checksum-basierte Integrität
- **Slots**: 3 Speicherplätze
- **Backups**: Automatische Sicherung
- **Metadata**: Timestamp, Playtime, Location, Level

### Speicher-Inhalt
- **Player-Data**: Position, Stats, Flags
- **Party**: Aktuelle Monster-Teams
- **Storage**: Box-System für gesammelte Monster
- **Story**: Flags, Quest-Progress, Completed Events
- **World**: Map-States, NPC-Positions

---

## 🎯 Wichtige Design-Patterns

### Singleton-Pattern
- `MonsterDatabase`: Globale Monster-Registry
- `SpriteManager`: Sprite-Cache-System
- `ResourceManager`: Asset-Loading

### Manager-Pattern
- **Separation of Concerns**: Jedes System hat eigenen Manager
- **Dependency Injection**: Manager werden in Game-Klasse initialisiert
- **State Management**: Zentrale Zustandsverwaltung

### Event-System
- **EventProcessor**: Zentrale Event-Verarbeitung
- **Battle-Events**: Turn-basierte Event-Queue
- **UI-Events**: Menu-Navigation und Dialoge

---

## 🔀 Datenfluss-Architektur

### Startup-Flow
1. `main.py` → pygame init
2. `Game.__init__()` → Manager-Initialisierung
3. Sprite-System laden
4. Erste Scene (StartScene) pushen

### Battle-Flow
1. **FieldScene** → Encounter-Trigger
2. **BattleScene.on_enter()** → Teams setup
3. **BattleState** → Phase-Machine
4. **Turn-Resolution** → Actions → Results
5. **Battle-End** → Rewards → Return to Field

### Save/Load-Flow
1. **GameStateSerializer** → Sammle alle Manager-States
2. **SaveSystem** → JSON-Serialisierung + ZIP
3. **Checksum** → Integritäts-Validierung
4. **Load** → Reverse Process mit Validation

---

## 🧩 Code-Konventionen

### Naming-Conventions
- **Englisch**: Alle Code/Kommentare
- **Deutsch**: Alle In-Game-Texte (Ruhrpott-Dialekt)
- **Type-Hints**: Überall verwenden
- **Dataclasses**: Für Datenstrukturen

### Error-Handling
- **Graceful Degradation**: Bei fehlenden Assets
- **Logging**: Umfassendes Error-Logging
- **Fallbacks**: Immer Backup-Verhalten bereitstellen

### Performance-Optimierungen
- **Caching**: Sprites, Maps, JSON-Daten
- **Culling**: Viewport-basiertes Rendering
- **Lazy Loading**: Assets on-demand laden

---

## 📝 Wichtige Klassen-Hierarchien

### Entity-System
```
Entity (Basis)
├── Player (Spieler-spezifisch)
└── NPC (verschiedene Movement-Patterns)
```

### Scene-System
```
Scene (Abstract Base)
├── FieldScene (Overworld)
├── BattleScene (Kämpfe)
├── MainMenuScene (Hauptmenü)
└── StarterScene (Monster-Auswahl)
```

### Monster-System
```
MonsterSpecies (Template)
└── MonsterInstance (Individuelle Monster)
    ├── Stats (Level-basiert)
    ├── Moves (4 Moves max)
    └── Status (Conditions)
```

---

## 🔧 Entwickler-Guidelines

### Code-Änderungen
1. **Module fokussiert halten**: Große Systeme aufteilen
2. **Debug-Features**: Hinter TAB-Taste
3. **Data-driven**: Systeme über JSON konfigurierbar
4. **Deterministic RNG**: Für Testing verwenden
5. **Edge-Cases**: Immer behandeln

### Testing-Konventionen
- **Unit Tests**: Für einzelne Systeme
- **Integration Tests**: Für System-Interaktionen
- **Performance Tests**: Für kritische Pfade
- **Save/Load Tests**: Für Data-Integrity

### Asset-Guidelines
- **Sprites**: 16x16 für Entities, variabel für UI
- **Audio**: OGG/WAV für SFX, OGG für BGM
- **Maps**: TMX (Tiled) oder JSON
- **Data**: JSON mit Validierung

---

## 🚀 Häufige Entwicklungsaufgaben

### Neues Monster hinzufügen
1. **monsters.json**: Neue Monster-Daten
2. **sprites**: Monster-Sprite in `assets/gfx/monster/`
3. **moves**: Learnset definieren
4. **areas**: In Encounter-Tables eintragen

### Neue Map erstellen
1. **Tiled**: TMX-Map erstellen
2. **JSON**: Optional JSON-Export
3. **data/maps/**: Map-Datei ablegen
4. **field_scene.py**: Warp-Connections setzen

### Neuen Move hinzufügen
1. **moves.json**: Move-Daten definieren
2. **effects**: MoveEffect-Configuration
3. **learnsets**: In Monster-Learnsets eintragen
4. **AI**: Battle-AI für neuen Move trainieren

### New UI-Element
1. **ui/**: Neue UI-Klasse erstellen
2. **MenuBase**: Von Base-Klasse erben
3. **Input-Handling**: Event-Verarbeitung
4. **Integration**: In entsprechende Scene einbinden

---

## 🔍 Debug-Features

### Debug-Overlay (TAB-Taste)
- **Performance**: FPS, Frame-Time, Memory
- **Position**: Player-Grid-Coordinates
- **Battle**: HP, Stats, Turn-Order
- **AI**: Move-Selection-Logic

### Console-Commands
- **F1**: Debug-Grid toggle
- **F2**: Collision-Boxes anzeigen
- **F3**: Performance-Overlay
- **F12**: Screenshot

---

## 📊 Performance-Hotspots

### Kritische Bereiche
1. **Sprite-Loading**: Lazy-Loading implementiert
2. **Map-Rendering**: Viewport-Culling
3. **Battle-Calculations**: Cached Results
4. **Save/Load**: ZIP-Komprimierung

### Optimierungs-Strategien
- **Asset-Caching**: LRU-Cache mit Memory-Limits
- **Render-Batching**: Layer-basiertes Rendering
- **Event-Pooling**: Object-Reuse für häufige Events
- **JSON-Caching**: Parsed Data cachen

---

## 🎯 System-Interaktionen

### Manager-Dependencies
```
Game
├── ResourceManager (Assets)
├── StoryManager (Flags/Progress)
├── PartyManager (Monster-Teams)
├── SpriteManager (Graphics)
└── AudioManager (Sound/Music)
```

### Data-Flow
```
JSON Files → ResourceManager → System-Managers → Game-Logic → UI → Rendering
```

### Event-Flow
```
pygame.Event → EventProcessor → Current Scene → System-Updates → Rendering
```

---

## 🌟 Besonderheiten des Projekts

### Ruhrpott-Atmosphäre
- **Dialoge**: Authentischer Ruhrpott-Slang
- **Monster**: Regional inspirierte Kreaturen
- **Setting**: Industrielle Umgebung mit Fantasy-Elementen

### DQM-Inspiration
- **Taming**: Strategisches Monster-Fangen
- **Breeding**: Synthesis-System für neue Monster
- **Skills**: Unique Abilities pro Monster
- **Ranks**: Seltenheis- und Power-System

### Performance-Fokus
- **60 FPS**: Konstante Frame-Rate
- **Memory-Management**: Intelligentes Caching
- **Scaling**: 4x Pixel-Perfect Scaling

---

## 🔧 Setup für neue Entwickler

### Dependencies installieren
```bash
pip install -r requirements.txt
```

### Spiel starten
```bash
python main.py
```

### Tests ausführen
```bash
python -m pytest tests/
```

---

## 📋 TODO-Template für KI-Entwicklung

Bei komplexen Aufgaben sollten KIs folgende TODO-Struktur verwenden:

1. **Analyse**: Code-Bereiche verstehen
2. **Planning**: Änderungen strukturieren  
3. **Implementation**: Schrittweise Umsetzung
4. **Testing**: Funktionalität validieren
5. **Integration**: In bestehendes System einbinden
6. **Documentation**: Code dokumentieren

---

## ⚠️ Häufige Fallstricke

### Import-Probleme
- **Circular Imports**: TYPE_CHECKING verwenden
- **Manager-Dependencies**: Über Game-Instanz injizieren
- **Optional Imports**: Try/Except für optionale Features

### Performance-Issues
- **Asset-Loading**: Niemals in Update-Loop laden
- **Collision-Checks**: Spatial-Partitioning verwenden
- **Rendering**: Dirty-Rectangles für Updates

### Data-Consistency
- **Save-Validation**: Immer Checksum verwenden
- **State-Synchronization**: Manager-States konsistent halten
- **Error-Recovery**: Graceful Fallbacks bereitstellen

---

## 🎯 Erweiterungspunkte

### Geplante Features
- **Online-Battles**: Multiplayer-System
- **Tournament-Mode**: Structured Competition
- **Breeding-Expansion**: Advanced Genetics
- **Story-Expansion**: Mehr Regionen und Charaktere

### Moddability
- **JSON-Configuration**: Vollständig data-driven
- **Asset-System**: Einfacher Asset-Austausch
- **Script-System**: Lua für Custom-Events
- **Plugin-Architecture**: Für Community-Erweiterungen

---

## 📞 Wichtige Kontakte und Referenzen

### File-Referenzen für häufige Tasks
- **Monster-Balance**: `data/monsters.json`
- **Move-Effects**: `engine/systems/moves.py`
- **Battle-Logic**: `engine/systems/battle/`
- **UI-Layouts**: `engine/ui/`
- **Map-Data**: `data/maps/`

### Debug-Hilfsmittel
- **Battle-Testing**: `test_battle_interactive.py`
- **Performance-Analysis**: `performance_dashboard.html`
- **Save-Validation**: `validate_migration.py`

---

*Diese Mastermap wird regelmäßig aktualisiert um Änderungen im Codebase zu reflektieren.*