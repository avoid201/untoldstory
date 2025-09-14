# Untold Story - Mastermap für KI-Entwicklung

## 📋 Projekt-Übersicht

**Untold Story** ist ein 2D top-down JRPG in Python mit pygame-ce, inspiriert von Dragon Quest Monsters und Pokémon. Das Spiel spielt im Ruhrpott mit deutschen Dialogen und lokalen Slang.

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

---

## 📁 Vollständige Modul-Referenz

### 🏗️ Core-Module (`engine/core/`)

#### `game.py` - Hauptspiel-Controller
**Klassen:**
- `Game`: Hauptgame-Loop und Scene-Management

**Wichtige Imports:**
```python
from engine.core.event_processor import EventProcessor
from engine.core.debug_overlay import DebugOverlayManager
from engine.core.resources import ResourceManager
from engine.systems.story import StoryManager
from engine.systems.party import PartyManager
from engine.systems.cutscene import CutsceneManager
from engine.audio.audio_manager import AudioManager
from engine.graphics.tile_renderer import TileRenderer
```

**Methoden:**
- `__init__()`: Initialisiert alle Manager
- `run()`: Hauptgame-Loop
- `push_scene()`: Scene auf Stack legen
- `pop_scene()`: Scene vom Stack entfernen
- `set_sprite_manager()`: Sprite-Manager setzen

#### `scene_base.py` - Scene-Interface
**Klassen:**
- `Scene`: Abstract Base für alle Szenen

**Methoden:**
- `enter()`: Scene-Initialisierung
- `exit()`: Scene-Cleanup
- `update(dt)`: Frame-Update
- `draw(surface)`: Rendering
- `handle_event(event)`: Input-Verarbeitung

#### `resources.py` - Resource-Management
**Klassen:**
- `ResourceType`: Enum für Asset-Typen
- `LRUCache`: Memory-Management Cache
- `ResourceManager`: Zentraler Asset-Loader

**Methoden:**
- `load_json()`: JSON-Dateien laden
- `load_image()`: Bilder laden und cachen
- `get_cache_info()`: Cache-Statistiken
- `clear_cache()`: Cache leeren

#### `config.py` - Zentrale Konfiguration
**Klassen:**
- `Colors`: Farbkonstanten
- `InputConfig`: Input-Mapping
- `BattleConfig`: Battle-System-Parameter
- `MonsterConfig`: Monster-System-Parameter
- `AudioConfig`: Audio-Einstellungen
- `GraphicsConfig`: Grafik-Einstellungen
- `BalanceConfig`: Gameplay-Balance
- `DebugConfig`: Debug-Features
- `NetworkConfig`: Netzwerk-Settings
- `SaveConfig`: Save-System-Parameter
- `LocalizationConfig`: Lokalisierung
- `PerformanceConfig`: Performance-Tuning
- `Fonts`: Font-Konfiguration
- `UI`: UI-Layout-Parameter
- `GameState`: Spielzustände-Enum

#### `input_manager.py` - Input-System
**Klassen:**
- `InputConfig`: Input-Konfiguration
- `InputState`: Aktueller Input-Zustand
- `InputManager`: Input-Verarbeitung

#### `event_processor.py` - Event-System
**Klassen:**
- `DebugKeyConfig`: Debug-Tastenbelegung
- `EventProcessor`: Zentrale Event-Verarbeitung

#### `debug_overlay.py` - Debug-Interface
**Klassen:**
- `DebugInfo`: Debug-Informationen
- `DebugOverlayManager`: Debug-Overlay-Verwaltung

#### `base_interfaces.py` - Interface-Definitionen
**Klassen:**
- `IUpdateable`: Update-Interface
- `IDrawable`: Render-Interface
- `IEventHandler`: Event-Handler-Interface
- `IInitializable`: Initialisierungs-Interface
- `BaseScene`: Scene-Basis-Klasse
- `BaseEntity`: Entity-Basis-Klasse
- `BaseRenderer`: Renderer-Basis-Klasse
- `BaseManager`: Manager-Basis-Klasse
- `BaseCalculator`: Calculator-Basis-Klasse
- `BaseValidator`: Validator-Basis-Klasse
- `BaseFactory`: Factory-Basis-Klasse
- `ISearchable`: Such-Interface
- `EventType`: Event-Typen-Enum
- `GameEvent`: Event-Datenstruktur
- `EventBus`: Event-Bus-System
- `Singleton`: Singleton-Metaclass

---

### ⚔️ Battle-System-Module (`engine/systems/battle/`)

#### `unified_battle_manager.py` - Haupt-Battle-Controller
**Klassen:**
- `UnifiedBattleManager`: Hauptklasse für Battle-Logic
- `SimpleBattleManager`: Vereinfachte Battle-Variante

**Methoden:**
- `start_battle()`: Battle initialisieren
- `process_turn()`: Turn verarbeiten
- `calculate_damage()`: Schaden berechnen
- `check_victory_conditions()`: Siegbedingungen prüfen
- `end_battle()`: Battle beenden

#### `unified_battle_actions.py` - Action-System
**Klassen:**
- `ActionType`: Action-Typen-Enum
- `BattleAction`: Action-Datenstruktur
- `UnifiedBattleActionExecutor`: Action-Ausführung
- `TurnOrderCalculator`: Turn-Order-Berechnung

#### `battle_controller.py` - Battle-State-Management
**Klassen:**
- `BattleState`: Battle-Zustand
- `BattleController`: Battle-Controller

#### `battle_ai.py` - KI-System
**Klassen:**
- `AIPersonality`: KI-Persönlichkeiten-Enum
- `AIDifficulty`: KI-Schwierigkeitsgrade
- `AIDecision`: KI-Entscheidung
- `BattleAI`: Haupt-KI-Klasse

#### `unified_damage_calc.py` - Schadens-Berechnung
**Klassen:**
- `DamageType`: Schadens-Typen-Enum
- `CriticalTier`: Critical-Hit-Stufen
- `DamageResult`: Schadens-Ergebnis
- `UnifiedDamageCalculator`: Hauptschadens-Calculator

#### `battle_enums.py` - Battle-Enumerationen
**Klassen:**
- `BattleType`: Battle-Typen
- `BattlePhase`: Battle-Phasen
- `BattleResult`: Battle-Ergebnisse
- `BattleCommand`: Battle-Kommandos
- `AIPersonality`: KI-Persönlichkeiten

#### `battle_animations.py` - Animation-System
**Klassen:**
- `AnimationType`: Animations-Typen-Enum
- `Animation`: Animation-Datenstruktur
- `ParticleEffect`: Partikel-Effekte
- `BattleAnimationSystem`: Animations-Manager

#### `battle_integration.py` - System-Integration
**Klassen:**
- `BattleIntegration`: Integration-Layer

#### Integration-Module (`engine/systems/battle/integration/`)

##### `battle_integration_layer.py`
**Klassen:**
- `BattleContext`: Battle-Kontext
- `BattleIntegrationLayer`: Integration-Layer

##### `battle_audio_controller.py`
**Klassen:**
- `SoundEffect`: Sound-Effekte-Enum
- `BattleAudioController`: Audio-Controller

##### `battle_save_state.py`
**Klassen:**
- `BattleSaveType`: Save-Typen-Enum
- `BattleSaveData`: Save-Daten
- `BattleSaveState`: Save-State-Manager

##### `battle_story_hooks.py`
**Klassen:**
- `StoryEventType`: Story-Event-Typen
- `StoryEvent`: Story-Event-Daten
- `BattleStoryHooks`: Story-Integration

##### `battle_ui_bridge.py`
**Klassen:**
- `DamageEvent`: Damage-Event
- `BattleUIBridge`: UI-Bridge

---

### 👾 Monster-System-Module (`engine/systems/`)

#### `monster_instance.py` - Monster-Instanzen
**Klassen:**
- `MonsterRank`: Rank-System (F-X)
- `StatusCondition`: Status-Conditions
- `BaseStats`: Basis-Stats
- `MonsterSpecies`: Monster-Arten
- `MonsterInstance`: Individual-Monster

**Wichtige Methoden:**
- `create_from_species()`: Monster aus Species erstellen
- `level_up()`: Monster leveln
- `learn_move()`: Move lernen
- `apply_status()`: Status-Condition anwenden
- `calculate_stats()`: Stats berechnen

#### `monsters.py` - Monster-Database
**Klassen:**
- `MonsterDatabase`: Singleton Monster-DB

**Methoden:**
- `get_species()`: Species abrufen
- `get_by_name()`: Monster nach Name suchen
- `get_by_rank()`: Monster nach Rank filtern
- `get_starters()`: Starter-Monster

#### `moves.py` - Move-System
**Klassen:**
- `MoveCategory`: Move-Kategorien (Physical/Magical/Support)
- `MoveTarget`: Targeting-System
- `EffectKind`: Effekt-Typen
- `MoveEffect`: Move-Effekte
- `Move`: Move-Datenstruktur
- `MoveExecutor`: Move-Ausführung
- `MoveRegistry`: Move-Registry

#### `stats.py` - Stats-System
**Klassen:**
- `Stat`: Stats-Enum (HP/ATK/DEF/MAG/RES/SPD)
- `GrowthCurve`: Wachstums-Kurven
- `BaseStats`: Basis-Stats
- `StatStages`: Stat-Modifikationen
- `Experience`: EXP-System
- `StatCalculator`: Stats-Berechnung
- `DamageCalculator`: Legacy Damage-Calculator

#### `types.py` - Type-System
**Klassen:**
- `TypeAttribute`: Type-Eigenschaften
- `BattleCondition`: Battle-Conditions
- `TypeData`: Type-Daten
- `TypeRelation`: Type-Beziehungen
- `TypeChart`: Type-Effectiveness-Chart
- `TypeSystemAPI`: Type-System-API

#### `party.py` - Team-Management
**Klassen:**
- `Party`: Monster-Team
- `StorageBox`: Storage-Box
- `StorageSystem`: Storage-System
- `PartyManager`: Team-Manager

#### `taming.py` - Taming-System
**Klassen:**
- `TameResult`: Taming-Ergebnisse
- `TameModifier`: Taming-Modifikatoren
- `TamingTips`: Taming-Tipps

#### `synthesis.py` - Fusion-System
**Klassen:**
- `SynthesisManager`: Fusion-Manager

#### `conditions.py` - Status-Conditions
**Klassen:**
- `ConditionType`: Condition-Typen
- `StatusCondition`: Status-Condition-Klasse
- `StatusConditions`: Conditions-Collection
- `ConditionManager`: Condition-Manager

---

### 🎨 UI-System-Module (`engine/ui/`)

#### `battle_ui.py` - Battle-Interface
**Klassen:**
- `BattleMenuState`: Menu-States
- `BattleSprite`: Battle-Sprites
- `DamageNumber`: Floating-Damage-Numbers
- `BattleHUD`: Battle-HUD
- `BattleMenu`: Battle-Menu
- `MoveSelector`: Move-Auswahl
- `TargetSelector`: Target-Auswahl
- `DamageNumbers`: Damage-Number-System
- `BattleUI`: Haupt-Battle-UI

#### `dqm_battle_ui.py` - DQM-Style Battle-UI
**Klassen:**
- `BattleMenuType`: DQM-Menu-Typen
- `DQMColors`: DQM-Farbschema
- `DQMBattleUI`: DQM-Style-UI

#### `menus.py` - Menu-System
**Klassen:**
- `MenuBase`: Menu-Basis-Klasse
- `InventoryMenu`: Inventar-Menu
- `PartyMenu`: Team-Menu
- `QuestMenu`: Quest-Menu
- `SaveMenu`: Save-Menu
- `ConfirmDialog`: Bestätigungs-Dialog

#### `dialogue.py` - Dialog-System
**Klassen:**
- `DialogueBox`: Dialog-Box
- `DialoguePage`: Dialog-Seite
- `DialogueChoice`: Dialog-Wahlmöglichkeit

#### `hud.py` - HUD-System
**Klassen:**
- `HUD`: Haupt-HUD

#### `transitions.py` - Übergangs-System
**Klassen:**
- `TransitionManager`: Übergangs-Manager

#### `enhanced_menus.py` - Erweiterte Menus
**Klassen:**
- `MenuState`: Menu-States
- `MenuTransition`: Menu-Übergänge
- `MenuItem`: Menu-Items
- `EnhancedMenuBase`: Erweiterte Menu-Basis
- `EnhancedInventoryMenu`: Erweitertes Inventar-Menu
- `EnhancedPartyMenu`: Erweitertes Team-Menu
- `MenuManager`: Menu-Manager

#### `modern_ui_patterns.py` - Moderne UI-Patterns
**Klassen:**
- `AnimationType`: UI-Animations-Typen
- `HoverState`: Hover-States
- `Animation`: UI-Animation
- `HoverEffect`: Hover-Effekte
- `ModernUIElement`: Moderne UI-Elemente
- `AnimatedButton`: Animierte Buttons
- `TooltipManager`: Tooltip-System
- `TransitionManager`: UI-Übergangs-Manager

#### `accessibility.py` - Barrierefreiheit
**Klassen:**
- `AccessibilityLevel`: Barrierefreiheits-Level
- `VisualAid`: Visuelle Hilfen
- `KeyboardShortcut`: Tastatur-Shortcuts
- `VisualAidConfig`: Visuelle-Hilfen-Config
- `AccessibilityManager`: Barrierefreiheits-Manager
- `VisualAidRenderer`: Visuelle-Hilfen-Renderer
- `AccessibilityUI`: Barrierefreiheits-UI

#### `battle_styles.py` - Battle-Styling
**Klassen:**
- `BattleStyle`: Battle-Styles
- `BattleThemes`: Battle-Themes
- `StyleUtils`: Style-Utilities

#### `battle_log.py` - Battle-Log
**Klassen:**
- `MessagePriority`: Message-Prioritäten
- `MessageCategory`: Message-Kategorien
- `BattleMessage`: Battle-Messages
- `BattleLog`: Battle-Log-System

---

### 🗺️ World-System-Module (`engine/world/`)

#### `area.py` - Spielbare Regionen
**Klassen:**
- `AreaConfig`: Area-Konfiguration
- `Area`: Spielbare Area

#### `player.py` - Spieler-Entity
**Klassen:**
- `Player`: Spieler-Klasse (erbt von Entity)

#### `entity.py` - Entity-Basis-System
**Klassen:**
- `Direction`: Richtungs-Enum
- `EntitySprite`: Entity-Sprite-Config
- `Entity`: Basis-Entity-Klasse

#### `npc.py` - NPC-System
**Klassen:**
- `MovementPattern`: Movement-Patterns
- `NPCConfig`: NPC-Konfiguration
- `NPC`: NPC-Klasse

#### `npc_manager.py` - NPC-Management
**Klassen:**
- `ManagedNPC`: Verwaltete NPCs

#### `map_loader.py` - Map-Loading
**Klassen:**
- `Warp`: Warp-Daten
- `Trigger`: Trigger-Daten
- `MapData`: Map-Daten
- `MapLoader`: Map-Loader

#### `camera.py` - Kamera-System
**Klassen:**
- `Camera`: Kamera-Klasse

#### `tiles.py` - Tile-System
**Konstanten:**
- `TILE_SIZE = 16`: Tile-Größe
- Utility-Funktionen für Tile-Koordinaten

#### `tile_manager.py` - Tile-Management
**Klassen:**
- `TileData`: Tile-Daten
- `TileManager`: Tile-Manager

#### `interaction_manager.py` - Interaktions-System
**Klassen:**
- `NPCData`: NPC-Daten
- `WarpData`: Warp-Daten
- `ObjectData`: Object-Daten
- `TriggerData`: Trigger-Daten
- `InteractionData`: Interaktions-Daten
- `InteractionManager`: Interaktions-Manager

#### `pathfinding.py` - Pathfinding
**Funktionen:**
- `a_star()`: A*-Pathfinding-Algorithmus

#### `pathfinding_mixin.py` - Pathfinding-Mixin
**Klassen:**
- `PathfindingMixin`: Pathfinding-Funktionalität

#### Weitere World-Module:
- `movement_states.py`: Bewegungs-Zustände
- `map_transition.py`: Map-Übergänge
- `ledge_handler.py`: Ledge-Jump-System
- `tile_ids.py`: Tile-IDs
- `gid_mapper.py`: GID-Mapping
- `tmx_init.py`: TMX-Initialisierung

---

### 🎮 Scene-System-Module (`engine/scenes/`)

#### `field_scene.py` - Overworld-Scene
**Klassen:**
- `FieldScene`: Haupt-Overworld-Scene

#### `battle_scene.py` - Battle-Scene
**Klassen:**
- `BattleResult`: Battle-Ergebnisse
- `BattleRewards`: Battle-Belohnungen
- `BattleScene`: Haupt-Battle-Scene

#### `starter_scene.py` - Starter-Auswahl
**Klassen:**
- `ManagerStatus`: Manager-Status
- `StarterScene`: Starter-Auswahl-Scene

#### `main_menu_scene.py` - Hauptmenü
**Klassen:**
- `MenuOption`: Menu-Optionen
- `MainMenuScene`: Hauptmenü-Scene

#### `start_scene.py` - Start-Scene
**Klassen:**
- `StartScene`: Start-Scene

#### `pause_scene.py` - Pause-Menu
**Klassen:**
- `PauseOption`: Pause-Optionen
- `PauseScene`: Pause-Scene

#### Field-Scene-Module (`engine/scenes/field/`)
- `story.py`: `FieldStorySystem`
- `encounters.py`: `FieldEncounterSystem`
- `interaction.py`: `FieldInteractionSystem`
- `map_system.py`: `MapLoadResult`, `UnifiedMapSystem`

---

### 🎨 Graphics-System-Module (`engine/graphics/`)

#### `sprite_manager.py` - Sprite-Management
**Klassen:**
- `SpriteManager`: Singleton Sprite-Manager

**Methoden:**
- `get_tile_sprite()`: Tile-Sprites abrufen
- `get_monster_sprite()`: Monster-Sprites abrufen
- `get_player_sprite()`: Player-Sprites abrufen
- `get_npc_sprite()`: NPC-Sprites abrufen

#### `tile_renderer.py` - Tile-Rendering
**Klassen:**
- `TileRenderer`: Tile-Renderer

#### `render_manager.py` - Render-Management
**Klassen:**
- `RenderLayer`: Render-Layer
- `RenderManager`: Render-Manager

---

### 🔊 Audio-System-Module (`engine/audio/`)

#### `audio_manager.py` - Audio-Management
**Klassen:**
- `AudioManager`: Audio-Manager

---

### 🛠️ Development-Tools (`engine/devtools/`)

#### `hot_reload.py` - Hot-Reload-System
**Klassen:**
- `FileWatcher`: Datei-Überwachung
- `HotReloadHandler`: Hot-Reload-Handler
- `HotReloader`: Hot-Reload-Manager
- `AssetCache`: Asset-Cache

#### `error_handler.py` - Error-Handling
**Klassen:**
- `ErrorSeverity`: Fehler-Schweregrade
- `ErrorEntry`: Fehler-Einträge
- `ErrorHandler`: Fehler-Handler

#### `input_debug.py` - Input-Debugging
**Klassen:**
- `InputEvent`: Input-Events
- `InputDebugger`: Input-Debugger

---

### 📦 Items-System-Module (`engine/items/`)

#### `running_shoes.py` - Laufschuhe-Item
**Klassen:**
- `RunningShoes`: Laufschuhe-Funktionalität

---

### 🎯 System-Module (`engine/systems/`)

#### `items.py` - Item-System
**Klassen:**
- `ItemCategory`: Item-Kategorien
- `ItemRarity`: Item-Seltenheit
- `ItemTarget`: Item-Ziele
- `EffectType`: Effekt-Typen
- `ItemEffect`: Item-Effekte
- `Item`: Item-Klasse
- `ItemEffectExecutor`: Item-Effekt-Ausführung
- `ItemRegistry`: Item-Registry
- `Inventory`: Inventar-System

#### `save.py` - Save-System
**Klassen:**
- `SaveMetadata`: Save-Metadaten
- `SaveSystem`: Save-System
- `GameStateSerializer`: Game-State-Serializer

#### `story.py` - Story-System
**Klassen:**
- `StoryPhase`: Story-Phasen
- `StoryFlag`: Story-Flags
- `CutsceneScript`: Cutscene-Scripts
- `StoryManager`: Story-Manager
- `DialogueManager`: Dialog-Manager
- `CutscenePlayer`: Cutscene-Player

#### `cutscene.py` - Cutscene-System
**Klassen:**
- `CutsceneAction`: Cutscene-Actions
- `Cutscene`: Cutscene-Klasse
- `CutsceneManager`: Cutscene-Manager

#### `quests.py` - Quest-System
**Klassen:**
- `QuestType`: Quest-Typen
- `QuestStatus`: Quest-Status
- `QuestObjective`: Quest-Ziele
- `QuestReward`: Quest-Belohnungen
- `Quest`: Quest-Klasse
- `QuestManager`: Quest-Manager

#### `weather.py` - Wetter-System
**Klassen:**
- `WeatherTransition`: Wetter-Übergänge
- `WeatherAnimation`: Wetter-Animationen
- `WeatherSystem`: Wetter-System

#### `field_effects.py` - Field-Effects
**Klassen:**
- `EffectCategory`: Effekt-Kategorien
- `WeatherType`: Wetter-Typen
- `TerrainType`: Terrain-Typen
- `SpecialEffectType`: Spezial-Effekt-Typen
- `FieldEffect`: Field-Effect-Basis
- `WeatherEffect`: Wetter-Effekte
- `TerrainEffect`: Terrain-Effekte
- `SpecialEffect`: Spezial-Effekte
- `FieldEffectManager`: Field-Effect-Manager

---

## 📊 Vollständige JSON-Datenstrukturen

### `data/monsters.json` - Monster-Database (8005 Zeilen)
**Struktur pro Monster:**
```json
{
  "id": 1,
  "name": "Glutstummel",
  "era": "present|past|future",
  "rank": "F|E|D|C|B|A|S|SS|X",
  "types": ["Feuer", "Wasser", "Erde", "Luft", "Pflanze", "Bestie", "Energie", "Chaos", "Seuche", "Mystik", "Gottheit", "Teufel"],
  "base_stats": {
    "hp": 40, "atk": 54, "def": 38,
    "mag": 24, "res": 20, "spd": 44
  },
  "growth": {
    "curve": "fast|medium_fast|medium_slow|slow",
    "yield": 48
  },
  "capture_rate": 249,
  "traits": ["Entflammbar", "Hitzkopf", ...],
  "learnset": [
    {"level": 1, "move": "Kratzer"},
    {"level": 5, "move": "Funken"}
  ],
  "evolution": null | {
    "level": 16,
    "to": "species_name",
    "conditions": []
  },
  "description": "Ruhrpott-Dialekt Beschreibung"
}
```

### `data/moves.json` - Move-Database (289 Zeilen)
**Struktur pro Move:**
```json
{
  "id": "ember",
  "name": "Glut",
  "type": "Feuer",
  "category": "phys|mag|support",
  "power": 40,
  "accuracy": 100,
  "pp": 25,
  "priority": 0,
  "targeting": "enemy|ally|self|all|random",
  "effects": [
    {
      "kind": "status|damage|heal|buff|debuff",
      "status": "burn|poison|paralysis|sleep|freeze|confusion",
      "chance": 10,
      "value": 20,
      "stat": "atk|def|mag|res|spd|acc|eva",
      "stages": -1,
      "target_type": "self|enemy|ally"
    }
  ],
  "description": "Deutsche Beschreibung"
}
```

### `data/types.json` - Type-Chart (196 Zeilen)
**Struktur:**
```json
{
  "types": [
    "Feuer", "Wasser", "Erde", "Luft", "Pflanze", 
    "Bestie", "Energie", "Chaos", "Seuche", 
    "Mystik", "Gottheit", "Teufel"
  ],
  "chart": [
    {
      "attacker": "Feuer",
      "defender": "Wasser", 
      "multiplier": 0.5
    }
  ]
}
```

**Multiplier-Werte:**
- `2.0`: Super effektiv
- `1.5`: Effektiv
- `1.0`: Normal
- `0.5`: Nicht sehr effektiv
- `0.0`: Keine Wirkung

### `data/items.json` - Item-Database (707 Zeilen)
**Struktur pro Item:**
```json
{
  "id": "trank",
  "name": "Trank",
  "description": "Deutsche Beschreibung",
  "category": "HEALING|BATTLE|RARE|KEY|BERRIES",
  "rarity": "COMMON|UNCOMMON|RARE|EPIC|LEGENDARY",
  "target": "SINGLE_ALLY|ALL_ALLIES|SINGLE_ENEMY|ALL_ENEMIES|SELF",
  "price": 100,
  "sell_price": 50,
  "use_in_battle": true,
  "use_in_field": true,
  "consumable": true,
  "stack_size": 99,
  "sprite_index": 0,
  "flavor_text": "Ruhrpott-Slang Beschreibung",
  "unlock_level": 1,
  "effects": [
    {
      "type": "HEAL_HP|HEAL_PP|CURE_STATUS|BOOST_STAT|DAMAGE",
      "value": 20,
      "chance": 1.0,
      "message": "Heilungs-Message",
      "target_type": "SINGLE_ALLY"
    }
  ]
}
```

### `data/field_effects.json` - Field-Effects (271 Zeilen)
**Kategorien:**
- **Weather**: Regen, Sonne, Schnee, Sturm
- **Terrain**: Gras, Wasser, Gestein, Lava
- **Special**: Magnetfeld, Zeitverzerrung

### Map-Dateien (`data/maps/`)
**Verfügbare Maps:**
- `kohlenstadt.json`: Hauptstadt
- `player_house.json`: Spielerhaus
- `museum.json`: Museum
- `route1.json`: Route 1
- `bergmannsheil.json`: Krankenhaus
- `rival_house.json`: Rivalen-Haus
- `penny.json`: Penny-Markt
- `doenerbude.json`: Döner-Bude

**Map-Struktur:**
```json
{
  "id": "kohlenstadt",
  "name": "Kohlenstadt",
  "width": 32,
  "height": 32,
  "tilesets": [...],
  "layers": [
    {
      "name": "ground",
      "data": [...]
    }
  ],
  "warps": [
    {
      "from": {"x": 15, "y": 30},
      "to": {"map": "route1", "x": 15, "y": 1}
    }
  ],
  "npcs": [...],
  "encounters": [...]
}
```

### Dialog-Dateien (`data/dialogs/`)
**NPC-Dialoge:**
- `professor_dialog.json`: Professor-Dialoge
- `karl_dialog.json`: Karl-Dialoge (Rival)
- `mom_dialog.json`: Mutter-Dialoge

**Dialog-Struktur:**
```json
{
  "npc_id": "professor",
  "dialogs": {
    "first_meeting": [
      {
        "text": "Ey, wat machste denn hier?",
        "speaker": "Professor",
        "choices": [
          {
            "text": "Ich bin hier für mein erstes Monster!",
            "next": "give_starter"
          }
        ]
      }
    ]
  }
}
```

---

## 🎨 Asset-System-Übersicht

### Monster-Sprites (`assets/gfx/monster/`)
**Datei-Format:** `{id}.png` (1.png bis 151.png)
**Größe:** 64x64 Pixel pro Monster
**Verfügbare Monster-IDs:** 1-151 (vollständige Gen 1 + Custom)

### Tile-System
**Tile-Größe:** 16x16 Pixel
**Unterstützte Formate:** 
- TMX (Tiled Map Editor)
- JSON (Custom Format)
- PNG Tilesets

### Audio-System (`assets/audio/`)
**BGM-Format:** OGG Vorbis
**SFX-Format:** WAV/OGG
**Kategorien:**
- Battle-Music
- Field-Music  
- Menu-Sounds
- Battle-SFX
- UI-Sounds

---

## 🔗 Import-Dependencies-Map

### Core-Dependencies
```
game.py → event_processor, debug_overlay, resources, story, party, cutscene, audio_manager, tile_renderer
scene_base.py → pygame
resources.py → pygame, pathlib, json, time
config.py → enum, pathlib
```

### Battle-System-Dependencies
```
unified_battle_manager.py → monster_instance, moves, stats, types, battle_enums
battle_ai.py → monster_instance, moves, types
unified_damage_calc.py → monster_instance, moves, types, stats
battle_controller.py → unified_battle_manager, battle_enums
```

### UI-Dependencies
```
battle_ui.py → pygame, battle_enums, monster_instance
menus.py → pygame, items, monster_instance, quests
dialogue.py → pygame, story
```

### World-Dependencies
```
area.py → pygame, map_loader, sprite_manager, entity, npc
player.py → entity, tiles, items.running_shoes
npc.py → entity, pathfinding_mixin
map_loader.py → json, pathlib
```

---

## 🎯 Kritische System-Interaktionen

### Startup-Sequenz
1. **main.py** → pygame init, sprite loading
2. **Game.__init__()** → Manager initialization
3. **ResourceManager** → Asset caching
4. **SpriteManager** → Sprite loading
5. **StartScene** → First scene push

### Battle-Flow-Sequenz
1. **FieldScene** → encounter trigger
2. **BattleScene.on_enter()** → battle setup
3. **UnifiedBattleManager** → battle logic
4. **BattleUI** → user interface
5. **UnifiedDamageCalculator** → damage calculation
6. **BattleAI** → enemy decisions

### Save/Load-Sequenz
1. **SaveSystem** → save initiation
2. **GameStateSerializer** → state collection
3. **PartyManager** → party serialization
4. **StoryManager** → story flags
5. **JSON + ZIP** → file compression

---

## 🔧 Entwickler-Checkliste

### Neue Klasse hinzufügen
- [ ] Type-Hints verwenden
- [ ] Docstrings hinzufügen  
- [ ] Base-Interface implementieren (falls zutreffend)
- [ ] Error-Handling einbauen
- [ ] Logging implementieren
- [ ] Unit-Tests schreiben

### Neues System integrieren
- [ ] Manager-Pattern verwenden
- [ ] Dependency-Injection über Game-Klasse
- [ ] Event-System nutzen
- [ ] Performance-Caching implementieren
- [ ] Debug-Features hinzufügen
- [ ] Save/Load-Support

### Asset hinzufügen
- [ ] Korrekte Datei-Namenskonvention
- [ ] Sprite-Manager-Integration
- [ ] Resource-Caching
- [ ] Fallback-Handling
- [ ] Performance-Testing

---

*Diese Mastermap wird regelmäßig aktualisiert um Änderungen im Codebase zu reflektieren.*
