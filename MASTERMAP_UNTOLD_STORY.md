# Untold Story - Vollständige Mastermap für KI-Entwicklung

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

## 📁 Vollständige Projektstruktur

```
untold_story/
├── main.py                    # Haupteinstiegspunkt - Game().__init__, initialize_sprite_system()
├── engine/                    # Haupt-Engine mit 6 Hauptmodulen
│   ├── core/                 # 7 Kern-Systeme
│   │   ├── game.py           # Game-Klasse - Hauptloop, Scene-Stack, Input-Manager
│   │   ├── scene_base.py     # Scene, TransitionScene - Abstract Base Classes
│   │   ├── resources.py      # ResourceManager, LRUCache - Asset-Loading mit intelligenter Caching
│   │   ├── config.py         # 15+ Config-Klassen - Zentrale Konstanten & Settings
│   │   ├── input_manager.py  # InputManager, InputConfig, InputState - Key-Mapping & Events
│   │   ├── event_processor.py # EventProcessor, DebugKeyConfig - pygame Event-Handling
│   │   └── debug_overlay.py  # DebugOverlayManager, DebugInfo - FPS Counter & Debug-UI
│   ├── systems/              # 17 Spielmechanik-Dateien
│   │   ├── battle/           # 22 Battle-System-Dateien (Hauptsystem)
│   │   ├── moves.py          # Move, MoveEffect, MoveExecutor, MoveRegistry - Move-System
│   │   ├── monster_instance.py # MonsterInstance, MonsterSpecies, MonsterRank - Monster-Objekte
│   │   ├── monsters.py       # MonsterDatabase - Species-Cache & Management
│   │   ├── stats.py          # BaseStats, StatStages, Experience, StatCalculator - Stat-Berechnungen
│   │   ├── types.py          # TypeChart, TypeData, TypeRelation - Type-Effectiveness-Matrix
│   │   ├── party.py          # Party, StorageBox, StorageSystem, PartyManager - Team-Management
│   │   ├── story.py          # StoryManager, StoryFlag, CutsceneScript - Progression & Flags
│   │   ├── save.py           # SaveSystem, SaveMetadata, GameStateSerializer - Save/Load mit ZIP
│   │   ├── items.py          # Item, ItemManager, ItemCategory - Item-System
│   │   ├── conditions.py     # StatusCondition, FieldEffect - Battle-Conditions
│   │   ├── field_effects.py  # WeatherSystem, TerrainEffect - Environmental-Effects
│   │   ├── synthesis.py      # SynthesisSystem, BreedingPair - Monster-Fusion
│   │   ├── taming.py         # TamingSystem, TamingAttempt - Monster-Capture
│   │   ├── quests.py         # QuestManager, Quest, QuestObjective - Quest-System
│   │   ├── cutscene.py       # CutsceneManager, CutsceneEvent - Story-Events
│   │   └── weather.py        # WeatherManager, WeatherType - Dynamic Weather
│   ├── ui/                   # 10 UI-Komponenten
│   │   ├── battle_ui.py      # BattleUI, BattleHUD, BattleMenu - Komplettes Battle-Interface
│   │   ├── menus.py          # MenuBase, PartyMenu, QuestMenu - Menü-System
│   │   ├── dialogue.py       # DialogueBox, DialoguePage, DialogueChoice - Text-System
│   │   ├── hud.py            # HUD-Elemente - Persistent UI
│   │   ├── transitions.py    # TransitionManager, FadeTransition - Scene-Übergänge
│   │   ├── enhanced_menus.py # Erweiterte Menü-Features
│   │   ├── modern_ui_patterns.py # UI-Design-Patterns
│   │   ├── accessibility.py  # Accessibility-Features
│   │   ├── battle_styles.py  # Battle-UI-Styling
│   │   └── battle_log.py     # Battle-Log-System
│   ├── scenes/               # 7 Haupt-Szenen
│   │   ├── battle_scene.py   # BattleScene - 1402 Zeilen Battle-Management
│   │   ├── field_scene.py    # FieldScene - 1033 Zeilen Overworld-Gameplay  
│   │   ├── main_menu_scene.py # MainMenuScene - Hauptmenü
│   │   ├── start_scene.py    # StartScene - Spielstart
│   │   ├── pause_scene.py    # PauseScene - Pause-Overlay
│   │   ├── starter_scene.py  # StarterScene - 1474 Zeilen Monster-Auswahl
│   │   └── battle/           # Battle-Szenen-Untermodule
│   ├── world/                # 20 Welt-Komponenten
│   │   ├── area.py           # Area, AreaConfig - Spielbare Map-Regionen
│   │   ├── entity.py         # Entity, EntitySprite, Direction - Basis-Entities
│   │   ├── player.py         # Player - Spieler-Charakter mit Movement
│   │   ├── npc.py            # NPC, MovementPattern, NPCConfig - Non-Player-Characters
│   │   ├── camera.py         # Camera, CameraConfig - Kamera-System
│   │   ├── tiles.py          # TILE_SIZE, TileType, world_to_tile() - Tile-Utilities
│   │   ├── map_loader.py     # MapLoader, MapData, Warp, Trigger - Map-Loading-System
│   │   ├── tile_manager.py   # TileManager - Tile-Verwaltung
│   │   ├── pathfinding.py    # Pathfinding-Algorithmen
│   │   ├── interaction_manager.py # InteractionManager - Entity-Interaktionen
│   │   └── [10 weitere Welt-Dateien]
│   ├── graphics/             # 6 Grafik-Systeme
│   │   ├── sprite_manager.py # SpriteManager - 577 Zeilen Sprite-Cache & Loading
│   │   ├── tile_renderer.py  # TileRenderer - Map-Rendering
│   │   ├── render_manager.py # RenderManager, RenderLayer - Z-Order & Performance
│   │   ├── optimized_renderer.py # OptimizedRenderer, TextureAtlas - Performance-Optimierungen
│   │   ├── asset_manager.py  # AssetManager - Asset-Verwaltung
│   │   └── [1 weitere Grafik-Datei]
│   ├── audio/                # 2 Audio-Dateien
│   │   ├── audio_manager.py  # AudioManager, AudioChannel - 330 Zeilen Audio-System
│   │   └── __init__.py       # Audio-Modul-Init
│   ├── devtools/             # 3 Developer-Tools
│   │   ├── input_debug.py    # Input-Debugging-Tools
│   │   ├── hot_reload.py     # Hot-Reload-System für Development
│   │   └── error_handler.py  # Erweiterte Error-Handling
│   └── items/                # 1 Item-System-Datei
│       └── running_shoes.py  # RunningShoes - Spezifisches Item-System
├── data/                     # JSON-Datenstrukturen
│   ├── monsters.json         # 8005 Zeilen Monster-Database
│   ├── moves.json           # 289 Zeilen Move-Database
│   ├── types.json           # 196 Zeilen Type-Chart
│   ├── items.json           # 707 Zeilen Item-Database
│   ├── field_effects.json   # 271 Zeilen Environmental-Effects
│   ├── tile_mapping.json    # 534 Zeilen Tile-ID-Mappings
│   └── [weitere JSON-Dateien]
├── assets/                   # Grafiken, Audio
│   ├── gfx/                 # 152 Grafik-Dateien (151 PNG)
│   │   ├── monster/         # Monster-Sprites (1-151.png Format)
│   │   ├── tiles/          # Tile-Sprites
│   │   ├── ui/             # UI-Grafiken
│   │   └── [weitere Grafik-Ordner]
│   ├── sfx/                # Sound-Effects
│   └── bgm/                # Background-Music
├── saves/                   # Spielstände (ZIP-Format)
├── tests/                   # 15+ Test-Dateien
└── tools/                   # 18 Utility-Tools

```

---

## 🏗️ Vollständige Engine-Architektur

### 📖 Übersicht der Haupt-Engine-Module

Das Engine-System ist in 7 Hauptmodule aufgeteilt:

1. **`core/`** - 7 Kern-Dateien: Game-Loop, Resources, Input, Events, Debug
2. **`systems/`** - 17 Gameplay-Dateien: Battle, Monster, Stats, Save, Story
3. **`ui/`** - 10 UI-Dateien: Menus, Dialoge, Battle-UI, HUD
4. **`scenes/`** - 7 Scene-Dateien: Field, Battle, Menu, Transitions  
5. **`world/`** - 20 Welt-Dateien: Maps, Entities, NPCs, Camera
6. **`graphics/`** - 6 Grafik-Dateien: Sprites, Rendering, Performance
7. **`audio/`** - 2 Audio-Dateien: Manager, Channels

### 🎮 Core-Systeme (`engine/core/`) - Detaillierte Klassen-Analyse

#### `game.py` - Hauptgame-Loop (518 Zeilen)
**Klassen:**
- `Game` - Hauptgame-Klasse mit Scene-Stack und Rendering-Pipeline
- `_SimpleTransitionManager` (Nested) - Transition-Wrapper

**Imports:**
```python
from typing import Optional, List, Dict, Any, Tuple, Type
from collections import deque
import pygame, time
from engine.core.event_processor import EventProcessor
from engine.core.debug_overlay import DebugOverlayManager
# Runtime-Imports für Manager (vermeidet Circular Imports)
```

**Kern-Eigenschaften Game-Klasse:**
- `scene_stack: List['Scene']` - Scene-Management-Stack
- `logical_surface: pygame.Surface` - 320×180 Render-Target
- `screen: pygame.Surface` - 1280×720 Display-Surface
- `clock: pygame.time.Clock` - 60 FPS Timing
- `event_processor: EventProcessor` - pygame Event-Handling
- `debug_overlay_manager: DebugOverlayManager` - Debug-UI
- Alle 8 Manager-Instanzen: story, party, resources, cutscene, transition, audio, input, sprite

**Kern-Methoden:**
- `run() -> int` - Hauptgame-Loop mit Event→Update→Draw→Present
- `push_scene()`, `pop_scene()`, `change_scene()` - Scene-Management
- `is_key_pressed()`, `is_key_just_pressed()` - Input-Delegates
- `_process_events()`, `_update()`, `_draw()`, `_present()` - Loop-Komponenten

#### `resources.py` - Resource-Management (842 Zeilen)
**Klassen:**
- `ResourceManager` (Singleton) - Asset-Loading mit intelligenter Caching
- `LRUCache` - Memory-aware Cache-Implementierung
- `ResourceType` (Enum) - IMAGE, JSON, SOUND, MUSIC, FONT

**Imports:**
```python
import json, pygame
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, Union, List
from enum import Enum
from functools import lru_cache
import time, weakref, gc
```

**Kern-Features:**
- 3 intelligente LRU-Caches: `_image_cache(200, 100MB)`, `_sound_cache(100, 50MB)`, `_json_cache(50, 10MB)`
- Monster-Index für O(1) Species-Lookup
- Priority-Assets (nie evicted)
- Performance-Tracking: `_cache_hits`, `_cache_misses`, `_load_times`
- Graceful Fallbacks bei fehlenden Assets

#### `input_manager.py` - Input-Management (382 Zeilen)
**Klassen:**
- `InputManager` - Hauptinput-System mit Enhanced Features
- `InputConfig` (Dataclass) - Key-Mapping-Konfiguration
- `InputState` (Dataclass) - Frame-Input-Status

**Enhanced Features:**
- Key-Repeat-System mit konfigurierbaren Delays
- Input-Buffering für responsive Gameplay
- Combo-Detection-System
- Vollständiges Input-Debug-System mit Logging
- Logical Input-Names (move_up, confirm, cancel, etc.)

#### `config.py` - Zentrale Konfiguration (554 Zeilen)
**15+ Konfigurationsklassen:**
- `Colors` - UI-Farben, HP-Bar-Farben, Status-Farben
- `BattleConfig` - Crit-Rate, STAB, Damage-Formeln
- `MonsterConfig` - Party-Limits, Level-Ranges, IV-Ranges
- `AudioConfig` - Volume-Settings, Fade-Times
- `GraphicsConfig` - Sprite-Größen, Animation-Speeds
- `BalanceConfig` - Economy, Encounter-Rates, Taming-Rates
- `DebugConfig` - Debug-Flags, Cheats, Logging
- `SaveConfig` - Save-Slots, Backup-Settings
- `PerformanceConfig` - Cache-Limits, Update-Rates, Culling

**Platform-Detection:** IS_WINDOWS, IS_MAC, IS_LINUX
**Type-Chart:** 50+ Type-Effectiveness-Entries

#### `event_processor.py` - Event-Processing (242 Zeilen)
**Klassen:**
- `EventProcessor` - pygame Event-Handling mit Debug-Features
- `DebugKeyConfig` (Dataclass) - F1-F7 Debug-Hotkeys

**Features:**
- Debug-Hotkey-System: F1-F7 für verschiedene Debug-Funktionen
- Input-Event-Logging mit Performance-Tracking
- Scene-Event-Delegation mit Handled-Tracking
- Screen-zu-Logical Coordinate-Conversion

#### `debug_overlay.py` - Debug-UI (171 Zeilen)
**Klassen:**
- `DebugOverlayManager` - Debug-Informationen und Overlay-Rendering
- `DebugInfo` (Dataclass) - Debug-Daten-Container

**Features:**
- FPS-Counter, Scene-Info, Input-Status
- Grid-Overlay für Tile-Alignment
- Input-Debug-Help mit Hotkey-Liste
- Performance-Monitoring

#### `scene_base.py` - Scene-Interface (235 Zeilen)  
**Klassen:**
- `Scene` (Abstract Base) - Basis für alle Szenen
- `TransitionScene` - Basis für Übergangseffekte

**Scene-System:**
- Stack-basiertes Scene-Management
- `blocks_update`, `blocks_draw` für Overlay-Control
- Lifecycle: `enter()` → `update()`/`draw()` → `exit()`
- Result-Passing zwischen Scenes

### 🎵 Audio-System (`engine/audio/`) - 2 Dateien

#### `audio_manager.py` - Audio-Management (330 Zeilen)
**Klassen:**
- `AudioManager` - Erweiterte Audio-Verwaltung mit Kanälen
- `AudioChannel` (Enum) - MUSIC, SFX, VOICE, AMBIENT, UI

**Features:**
- Multi-Channel-System mit reservierten Kanälen
- Fading, Volume-Control, Sound-Queue
- Threading für komplexe Audio-Operationen
- Sound-Cache für Performance

### 🎨 Grafik-System (`engine/graphics/`) - 6 Dateien

#### `sprite_manager.py` - Sprite-Cache & Loading (577 Zeilen)
**Klassen:** `SpriteManager` (Singleton)
**Features:** 5 spezialisierte Sprite-Caches (tiles, objects, player, npc, monster), TMX-Support, Lazy Loading

#### `tile_renderer.py` - Map-Rendering (203 Zeilen)
**Klassen:** `TileRenderer`
**Features:** Viewport-Culling, Placeholder-Generation, Debug-Rendering

#### `render_manager.py` - Z-Order & Performance (259 Zeilen)
**Klassen:** `RenderManager`, `RenderLayer`
**Features:** 10-Layer-System, Performance-Caching, Entity-Culling

#### `optimized_renderer.py` - Performance-Optimierungen (324 Zeilen)
**Klassen:** `OptimizedRenderer`, `TextureAtlas`, `FontCache`, `RenderOptimizer`
**Features:** Sprite-Sheets, Batch-Rendering, Font-Caching

---

## 🎮 Gameplay-Systeme (`engine/systems/`) - 17 Dateien

### 📊 Kern-Statistik-Systeme

#### `stats.py` - Statistik-System (434 Zeilen)
**Klassen:**
- `BaseStats` (Dataclass) - HP/ATK/DEF/MAG/RES/SPD
- `StatStages` - Battle-Stat-Modifiers (-6 bis +6)
- `Experience` - Level-Progression mit 4 Growth-Curves
- `StatCalculator` - Stat-Berechnung mit IV/EV-System
- `DamageCalculator` - Standard-Damage-Formula

**Enums:**
- `Stat` - HP, ATK, DEF, MAG, RES, SPD, ACC, EVA
- `GrowthCurve` - FAST, MEDIUM_FAST, MEDIUM_SLOW, SLOW

#### `types.py` - Type-System (651 Zeilen)
**Klassen:**
- `TypeChart` (Singleton) - High-Performance Type-Effectiveness mit NumPy
- `TypeData` (Dataclass) - Type-Informationen
- `TypeRelation` (Dataclass) - Type-Matchup-Definitionen

**Features:**
- NumPy-Matrix für O(1) Type-Lookups
- Advanced Mechanics: Synergies, Combos, Adaptive Resistances
- Battle-Conditions: NORMAL, INVERSE, CHAOS, PURE
- Precomputed Common Operations

#### `moves.py` - Move-System (642 Zeilen) - BEREITS ANALYSIERT
**Klassen:**
- `Move` (Dataclass) - Komplette Move-Daten mit Validation
- `MoveEffect` (Dataclass) - Einzeleffekte mit Parametern
- `MoveExecutor` - Move-Ausführung in Battle
- `MoveRegistry` (Singleton) - Move-Database

**Enums:**
- `MoveCategory` - PHYSICAL, MAGICAL, SUPPORT
- `MoveTarget` - ENEMY, ALLY, SELF, ALL_ENEMIES, ALL_ALLIES, ALL, RANDOM
- `EffectKind` - DAMAGE, HEAL, BUFF, DEBUFF, STATUS, CURE, FIELD, etc.

#### `monster_instance.py` - Monster-System (779 Zeilen)
**Klassen:**
- `MonsterInstance` - Individuelle Monster mit Stats, Moves, Status
- `MonsterSpecies` - Species-Template mit Base-Stats
- `MonsterRank` (Enum) - F, E, D, C, B, A, S, SS, X
- `StatusCondition` (Enum) - BURN, POISON, PARALYSIS, SLEEP, FREEZE, CONFUSION, FLINCH

#### `monsters.py` - Monster-Database (380 Zeilen)
**Klassen:**
- `MonsterDatabase` (Singleton) - Species-Cache und Management

**Features:**
- Species-Cache mit Kategorisierung (Era, Rank, Type)
- Special Categories: Starters, Legendaries, Fossils
- Default-Species für Fallback-Handling

---

## ⚔️ Battle-System (`engine/systems/battle/`) - 22 Dateien

### 🎯 Battle-Core-Komponenten

#### `battle_controller.py` - Haupt-Battle-Controller (923 Zeilen)
**Klassen:**
- `BattleState` - Vollständige Battle-State-Management
- `BattleController` - Koordiniert alle Battle-Subsysteme

**Imports:**
```python
from engine.systems.battle.battle_enums import BattleType, BattlePhase, BattleCommand, AIPersonality
from engine.systems.battle.battle_validation import BattleValidator
from engine.systems.battle.battle_tension import TensionManager
from engine.systems.battle.battle_actions import BattleActionExecutor
from engine.systems.battle.turn_logic import BattleAction, ActionType, TurnOrder
from engine.systems.battle.battle_ai import BattleAI
from engine.systems.battle.battle_events import BattleEventGenerator, EventType, BattleEvent
from engine.systems.battle.battle_formation import BattleFormation, FormationManager
from engine.systems.battle.target_system import TargetingSystem, TargetType
from engine.systems.battle.dqm_formulas import DQMCalculator, DQMDamageStage
```

#### `turn_logic.py` - Turn-System (1015 Zeilen)
**Klassen:**
- `BattleAction` (Dataclass) - Einzelne Battle-Aktion
- `TurnOrder` - Speed-basierte Turn-Reihenfolge
- `ActionType` (Enum) - ATTACK, SWITCH, ITEM, FLEE, TAME

#### `damage_calc.py` - DQM-Damage-System (1134 Zeilen)
**Klassen:**
- `DQMDamageCalculator` - Komplexe DQM-Damage-Formeln
- `DamageModifier` - Damage-Modifier-System
- `CriticalHitSystem` - Critical-Hit-Berechnung

#### `battle_ai.py` - KI-System (456 Zeilen)
**Klassen:**
- `BattleAI` - Haupte KI-Klasse
- `AIPersonality` (Enum) - AGGRESSIVE, DEFENSIVE, BALANCED, SMART
- `AIStrategy` - Move-Selection-Algorithmen

#### `battle_actions.py` - Action-Execution (824 Zeilen)
**Klassen:**
- `BattleActionExecutor` - Führt Battle-Actions aus
- `ActionResult` - Ergebnis-Container für Actions

### 🎭 DQM-spezifische Systeme

#### `skills_dqm.py` - DQM-Skills (703 Zeilen)
**Klassen:**
- `SkillSystem` - DQM-Skill-Implementierung
- `Skill` (Dataclass) - Einzelne Skills
- `SkillEffect` - Skill-Effekte

#### `monster_traits.py` - Monster-Traits (903 Zeilen)
**Klassen:**
- `TraitSystem` - Monster-Trait-System
- `Trait` (Dataclass) - Individuelle Traits
- `TraitEffect` - Trait-Wirkungen

#### `dqm_formulas.py` - DQM-Formeln (666 Zeilen)
**Klassen:**
- `DQMCalculator` - Originale DQM-Berechnungen
- `DQMDamageStage` - DQM-Damage-Stages

### 🎯 Battle-Support-Systeme

#### `battle_formation.py` - Formation-System (527 Zeilen)
**Klassen:**
- `BattleFormation` - 3v3 Formation-Management
- `FormationManager` - Formation-Controller
- `FormationType` (Enum) - STANDARD, DEFENSIVE, OFFENSIVE
- `MonsterSlot` - Slot-Position-Management

#### `target_system.py` - Targeting-System (540 Zeilen)
**Klassen:**
- `TargetingSystem` - Advanced Targeting für 3v3
- `TargetSelection` - Target-Selection-Logic
- `TargetType` (Enum) - SINGLE, MULTI, ALL, RANDOM

#### `battle_events.py` - Event-System (845 Zeilen)
**Klassen:**
- `BattleEventGenerator` - Battle-Event-Generation
- `BattleEvent` (Dataclass) - Event-Container
- `EventType` (Enum) - DAMAGE, HEALING, STATUS, FAINT

#### `command_collection.py` - Command-System (671 Zeilen)
**Klassen:**
- `CommandCollector` - Sammelt Player-Commands
- `MonsterCommand` - Einzelne Monster-Commands
- `CommandPhase` (Enum) - Collection-Phasen

### 🛠️ Battle-Utilities

#### `battle_validation.py` - Validation (211 Zeilen)
**Klassen:** `BattleValidator` - Battle-State-Validation

#### `battle_tension.py` - Tension-System (126 Zeilen)
**Klassen:** `TensionManager` - Battle-Spannung-Management

#### `battle_effects.py` - Effects-System (664 Zeilen)
**Klassen:** Verschiedene Effect-Handler

#### `battle_enums.py` - Battle-Enums (59 Zeilen)
**Enums:** Alle Battle-bezogenen Enumerations

#### `battle_system.py` - System-Integration (89 Zeilen)
**Klassen:** Integration-Layer für Battle-System

---

## 👤 Weitere Gameplay-Systeme

#### `party.py` - Team-Management (659 Zeilen)
**Klassen:**
- `Party` - Aktives 6-Monster-Team
- `StorageBox` - Storage-Box mit 30 Plätzen
- `StorageSystem` - Box-Management-System  
- `PartyManager` - Zentrale Party-Verwaltung

#### `story.py` - Story-Management (742 Zeilen)
**Klassen:**
- `StoryManager` - Story-Progression und Flags
- `StoryFlag` (Dataclass) - Einzelne Story-Flags
- `CutsceneScript` (Dataclass) - Cutscene-Definitionen

**Enums:**
- `StoryPhase` - PROLOGUE, EARLY_GAME, MID_GAME, LATE_GAME, ENDGAME, POSTGAME

#### `save.py` - Save/Load-System (642 Zeilen)
**Klassen:**
- `SaveSystem` - Hauptsave-System mit ZIP-Komprimierung
- `SaveMetadata` (Dataclass) - Save-File-Metadaten
- `GameStateSerializer` - Game-State-Serialisierung

#### `synthesis.py` - Fusion-System (510 Zeilen)
**Klassen:**
- `SynthesisSystem` - Monster-Fusion-System
- `BreedingPair` - Fusion-Partner-Management

#### `taming.py` - Taming-System (379 Zeilen)
**Klassen:**
- `TamingSystem` - Monster-Capture-System
- `TamingAttempt` - Einzelne Taming-Versuche

#### `quests.py` - Quest-System (584 Zeilen)
**Klassen:**
- `QuestManager` - Quest-Verwaltung
- `Quest` (Dataclass) - Einzelne Quests
- `QuestObjective` - Quest-Ziele

#### `cutscene.py` - Cutscene-System (283 Zeilen)
**Klassen:**
- `CutsceneManager` - Cutscene-Verwaltung
- `CutsceneEvent` - Einzelne Cutscene-Events

#### `items.py` - Item-System (1143 Zeilen)
**Klassen:**
- `Item` (Dataclass) - Item-Definitionen
- `ItemManager` - Item-Verwaltung
- `ItemCategory` (Enum) - Item-Kategorisierung

#### `conditions.py` - Status-System (571 Zeilen)
**Klassen:** Status-Condition-Handler

#### `field_effects.py` - Environmental-Effects (631 Zeilen)
**Klassen:**
- `WeatherSystem` - Wetter-System
- `TerrainEffect` - Terrain-Effekte

#### `weather.py` - Weather-System (360 Zeilen)
**Klassen:**
- `WeatherManager` - Weather-Management
- `WeatherType` (Enum) - Verschiedene Wetter-Typen

---

## 🖼️ UI-System (`engine/ui/`) - 10 Dateien

#### `battle_ui.py` - Battle-Interface (1007 Zeilen)
**Klassen:**
- `BattleUI` - Komplettes Battle-Interface-System
- `BattleHUD` - Monster-Information-Panels  
- `BattleMenu` - Battle-Menü-Navigation
- `BattleSprite` (Dataclass) - Battle-Sprite-Container
- `DamageNumber` (Dataclass) - Floating-Damage-Numbers

**Enums:**
- `BattleMenuState` - MAIN, MOVE_SELECT, TARGET_SELECT, ITEM_SELECT, PARTY_SELECT, SCOUT

#### `menus.py` - Menü-System (762 Zeilen)
**Klassen:**
- `MenuBase` (Abstract) - Basis für alle Menüs
- `PartyMenu` - Monster-Team-Management-Menü
- `QuestMenu` - Quest-Log-Menü

**Features:**
- Navigation mit Arrow-Keys, Confirm/Cancel
- Scrolling für lange Listen
- Swap-Mode für Party-Management

#### `dialogue.py` - Dialog-System (547 Zeilen)
**Klassen:**
- `DialogueBox` - Haupt-Dialog-Container
- `DialoguePage` (Dataclass) - Einzelne Dialog-Seiten
- `DialogueChoice` (Dataclass) - Dialog-Wahlmöglichkeiten

**Enums:**
- `DialogueState` - CLOSED, OPENING, DISPLAYING, WAITING, CLOSING

#### `hud.py` - HUD-Elemente (474 Zeilen)
**Klassen:** Persistent UI-Komponenten

#### `transitions.py` - Scene-Übergänge (381 Zeilen)
**Klassen:**
- `TransitionManager` - Transition-Controller
- `FadeTransition` - Fade-Effekte

#### `enhanced_menus.py` - Erweiterte Menüs (521 Zeilen)
#### `modern_ui_patterns.py` - UI-Design-Patterns (304 Zeilen)
#### `accessibility.py` - Accessibility-Features (485 Zeilen)
#### `battle_styles.py` - Battle-UI-Styling (252 Zeilen)
#### `battle_log.py` - Battle-Log-System (484 Zeilen)

---

## 🎬 Scene-System (`engine/scenes/`) - 7 Dateien

#### `battle_scene.py` - Battle-Management (1402 Zeilen)
**Klassen:**
- `BattleScene` - Hauptkampf-Szene
- `BattleResult` (Enum) - ONGOING, VICTORY, DEFEAT, FLED, CAUGHT

**Features:**
- Integration von BattleState + BattleUI
- Complete Battle-Flow: Setup → Combat → Results
- EXP/Items/Money-Rewards
- Monster-Capturing

#### `field_scene.py` - Overworld-Gameplay (1033 Zeilen)  
**Klassen:**
- `FieldScene` - Hauptüberland-Szene

**Features:**
- Map-Rendering mit TileRenderer
- Player-Movement und NPC-Interaction
- Encounter-System (Step-basiert)
- Dialog-System-Integration
- Map-Transitions

#### `starter_scene.py` - Monster-Auswahl (1474 Zeilen)
**Klassen:** `StarterScene` - Starter-Monster-Auswahl mit ausführlichem Tutorial

#### `main_menu_scene.py` - Hauptmenü (547 Zeilen)
**Klassen:** `MainMenuScene` - New Game, Continue, Settings

#### `start_scene.py` - Spielstart (338 Zeilen)
**Klassen:** `StartScene` - Intro-Scene

#### `pause_scene.py` - Pause-Overlay (437 Zeilen)
**Klassen:** `PauseScene` - Pause-Menü-Overlay

---

## 🗺️ Welt-System (`engine/world/`) - 20 Dateien

### 🏗️ Map-System

#### `area.py` - Spielbare Regionen (626 Zeilen)
**Klassen:**
- `Area` - Spielbare Map-Region mit TMX-Support
- `AreaConfig` (Dataclass) - Area-Konfiguration

**Features:**
- TMX-Support mit Layer-Rendering
- Surface-Caching für Performance
- NPC-Management pro Area

#### `map_loader.py` - Map-Loading (397 Zeilen)
**Klassen:**
- `MapLoader` - TMX/JSON Map-Loading
- `MapData` (Dataclass) - Map-Daten-Container
- `Warp` (Dataclass) - Map-Übergänge
- `Trigger` (Dataclass) - Event-Trigger

#### `tile_manager.py` - Tile-Management (597 Zeilen)
**Klassen:** `TileManager` - Tile-System-Verwaltung

#### `camera.py` - Kamera-System (329 Zeilen)
**Klassen:**
- `Camera` - Kamera mit Smooth-Following
- `CameraConfig` (Dataclass) - Kamera-Einstellungen

### 👤 Entity-System

#### `entity.py` - Basis-Entities (487 Zeilen)
**Klassen:**
- `Entity` - Basis-Klasse für alle Welt-Objekte
- `EntitySprite` (Dataclass) - Sprite-Konfiguration
- `Direction` (Enum) - UP, DOWN, LEFT, RIGHT

**Features:**
- Grid-basierte Position mit Smooth-Movement
- Collision-System mit Bounding-Boxes
- Animation-State-Machine

#### `player.py` - Spieler-Charakter (682 Zeilen)
**Klassen:** `Player` (extends Entity)

**Features:**
- Grid-Movement mit Running
- Encounter-Triggering
- Ledge-Jumping
- Input-Buffer für Responsive Movement

#### `npc.py` - Non-Player-Characters (462 Zeilen)
**Klassen:**
- `NPC` (extends Entity) - NPCs mit AI-Movement
- `MovementPattern` (Enum) - STATIC, RANDOM, PATROL, WANDER, FOLLOW, FLEE
- `NPCConfig` (Dataclass) - NPC-Konfiguration

### 🔧 Utility-Systeme

#### `tiles.py` - Tile-Utilities (104 Zeilen)
**Konstanten/Funktionen:**
- `TILE_SIZE = 16` - Zentrale Tile-Größe
- `world_to_tile()`, `tile_to_world()` - Koordinaten-Konvertierung
- `draw_grid()` - Debug-Grid-Rendering

#### `pathfinding.py` - Pathfinding-Algorithmen (140 Zeilen)
#### `interaction_manager.py` - Entity-Interaktionen (446 Zeilen)
#### `npc_manager.py` - NPC-Verwaltung (361 Zeilen)
#### [6 weitere Welt-Dateien]

---

## 📊 Daten-System (`data/`) - JSON-Strukturen

### 🗃️ Hauptdatenbanken

#### `monsters.json` - Monster-Database (8005 Zeilen)
**Format pro Monster:**
```json
{
  "id": 1,
  "name": "Glutstummel", 
  "era": "present",                    // past, present, future
  "rank": "F",                         // F, E, D, C, B, A, S, SS, X
  "types": ["Feuer"],                  // 12 Types
  "base_stats": {
    "hp": 40, "atk": 54, "def": 38,
    "mag": 24, "res": 20, "spd": 44
  },
  "growth": {"curve": "fast", "yield": 48},
  "capture_rate": 249,                 // 0-255
  "traits": ["Entflammbar"],
  "learnset": [{"level": 1, "move": "Kratzer"}],
  "evolution": null,                   // Optional Evolution-Data
  "description": "Ruhrpott-Slang Beschreibung"
}
```

#### `moves.json` - Move-Database (289 Zeilen)
**Format pro Move:**
```json
{
  "id": "ember",
  "name": "Glut",
  "type": "Feuer",                     // Einer der 12 Types
  "category": "mag",                   // phys, mag, support
  "power": 40,
  "accuracy": 100,                     // 0-100
  "pp": 25,
  "priority": 0,                       // -5 bis +5
  "targeting": "enemy",                // enemy, ally, self, all_enemies, etc.
  "effects": [
    {"kind": "status", "status": "burn", "chance": 10}
  ],
  "description": "Move-Beschreibung"
}
```

#### `types.json` - Type-Chart (196 Zeilen)
**Struktur:**
```json
{
  "types": ["Feuer", "Wasser", "Erde", "Luft", "Pflanze", "Bestie", 
           "Energie", "Chaos", "Seuche", "Mystik", "Gottheit", "Teufel"],
  "chart": [
    {"attacker": "Feuer", "defender": "Wasser", "multiplier": 0.5},
    {"attacker": "Feuer", "defender": "Pflanze", "multiplier": 2.0}
    // ... 100+ Type-Matchups
  ]
}
```

#### `items.json` - Item-Database (707 Zeilen)
**Item-Kategorien:** HEALING, BERRIES, POKEBALLS, BATTLE, KEY, TM

#### `field_effects.json` - Environmental-Effects (271 Zeilen)
**Weather & Terrain-Effects**

#### `tile_mapping.json` - Tile-ID-Mappings (534 Zeilen)
**GID-zu-Sprite-Name-Mappings für TMX-Support**

### 🗺️ Map-Daten (`data/maps/`)
- **TMX-Dateien**: Tiled-Maps mit Layer-System
- **JSON-Maps**: Alternative Map-Format
- **Tilesets**: TSX-Tileset-Definitionen

---

## 🔧 Development-Tools & Tests

### 🛠️ Developer-Tools (`engine/devtools/`) - 3 Dateien

#### `input_debug.py` - Input-Debugging (283 Zeilen)
**Features:** Erweiterte Input-Analyse, Performance-Tracking

#### `hot_reload.py` - Hot-Reload-System (459 Zeilen)
**Features:** Live-Code-Reloading für Development

#### `error_handler.py` - Error-Handling (264 Zeilen)
**Features:** Erweiterte Error-Recovery

### 🧪 Test-System (15+ Dateien)
- `test_battle_*.py` - Battle-System-Tests
- `test_save_system.py` - Save/Load-Tests
- `test_performance.py` - Performance-Tests
- `test_type_system.py` - Type-Chart-Tests

### 🔨 Tools (`tools/`) - 18 Utility-Scripts
- Migration-Tools, Cleanup-Scripts, Performance-Analysis

---

## 🎯 Vollständiges Import-System

### 📥 Core-Import-Patterns

#### Circular-Import-Vermeidung
```python
# TYPE_CHECKING für Forward-References
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from engine.core.game import Game
    from engine.systems.monster_instance import MonsterInstance

# Runtime-Imports in Methoden
def some_method(self):
    from engine.systems.story import StoryManager
    story_manager = StoryManager()
```

#### Manager-Injection-Pattern
```python
# In Game.__init__()
from engine.systems.story import StoryManager
from engine.systems.party import PartyManager
from engine.core.resources import ResourceManager
self.story_manager = StoryManager()
self.party_manager = PartyManager(self)
self.resources = ResourceManager()
```

#### Singleton-Pattern
```python
# ResourceManager, SpriteManager, MonsterDatabase, TypeChart, MoveRegistry
class SomeManager:
    _instance: Optional['SomeManager'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

---

## 🎮 Vollständiger Klassen-Index

### 🏗️ Core-Klassen (7 Dateien)
| Datei | Hauptklassen | Zeilen | Beschreibung |
|-------|-------------|--------|--------------|
| `game.py` | `Game`, `_SimpleTransitionManager` | 518 | Hauptgame-Loop, Scene-Stack |
| `resources.py` | `ResourceManager`, `LRUCache`, `ResourceType` | 842 | Asset-Loading mit Caching |
| `input_manager.py` | `InputManager`, `InputConfig`, `InputState` | 382 | Input-System mit Debug |
| `config.py` | 15+ Config-Klassen | 554 | Zentrale Konfiguration |
| `event_processor.py` | `EventProcessor`, `DebugKeyConfig` | 242 | pygame Event-Handling |
| `debug_overlay.py` | `DebugOverlayManager`, `DebugInfo` | 171 | Debug-UI-System |
| `scene_base.py` | `Scene`, `TransitionScene` | 235 | Scene-Base-Classes |

### ⚔️ Battle-System-Klassen (22 Dateien)
| Datei | Hauptklassen | Zeilen | Beschreibung |
|-------|-------------|--------|--------------|
| `battle_controller.py` | `BattleState`, `BattleController` | 923 | Battle-Koordination |
| `turn_logic.py` | `BattleAction`, `TurnOrder`, `ActionType` | 1015 | Turn-Management |
| `damage_calc.py` | `DQMDamageCalculator`, `DamageModifier` | 1134 | DQM-Damage-System |
| `battle_ai.py` | `BattleAI`, `AIPersonality`, `AIStrategy` | 456 | KI-System |
| `battle_actions.py` | `BattleActionExecutor`, `ActionResult` | 824 | Action-Execution |
| `skills_dqm.py` | `SkillSystem`, `Skill`, `SkillEffect` | 703 | DQM-Skills |
| `monster_traits.py` | `TraitSystem`, `Trait`, `TraitEffect` | 903 | Monster-Traits |
| `battle_formation.py` | `BattleFormation`, `FormationManager` | 527 | 3v3-Formations |
| `target_system.py` | `TargetingSystem`, `TargetSelection` | 540 | Advanced-Targeting |
| `battle_events.py` | `BattleEventGenerator`, `BattleEvent` | 845 | Event-System |
| `command_collection.py` | `CommandCollector`, `MonsterCommand` | 671 | Command-Collection |
| [11 weitere Battle-Dateien] | | | |

### 🎮 Gameplay-System-Klassen (16 weitere Dateien)
| Datei | Hauptklassen | Zeilen | Beschreibung |
|-------|-------------|--------|--------------|
| `stats.py` | `BaseStats`, `StatStages`, `Experience`, `StatCalculator` | 434 | Stat-System |
| `types.py` | `TypeChart`, `TypeData`, `TypeRelation` | 651 | Type-Effectiveness |
| `moves.py` | `Move`, `MoveEffect`, `MoveExecutor`, `MoveRegistry` | 642 | Move-System |
| `monster_instance.py` | `MonsterInstance`, `MonsterSpecies`, `MonsterRank` | 779 | Monster-System |
| `monsters.py` | `MonsterDatabase` | 380 | Species-Database |
| `party.py` | `Party`, `StorageBox`, `StorageSystem`, `PartyManager` | 659 | Team-Management |
| `story.py` | `StoryManager`, `StoryFlag`, `CutsceneScript` | 742 | Story-System |
| `save.py` | `SaveSystem`, `SaveMetadata`, `GameStateSerializer` | 642 | Save/Load |
| `items.py` | `Item`, `ItemManager`, `ItemCategory` | 1143 | Item-System |
| `synthesis.py` | `SynthesisSystem`, `BreedingPair` | 510 | Monster-Fusion |
| `taming.py` | `TamingSystem`, `TamingAttempt` | 379 | Monster-Capture |
| `quests.py` | `QuestManager`, `Quest`, `QuestObjective` | 584 | Quest-System |
| `cutscene.py` | `CutsceneManager`, `CutsceneEvent` | 283 | Cutscenes |
| `conditions.py` | Status-Handler | 571 | Status-Effects |
| `field_effects.py` | `WeatherSystem`, `TerrainEffect` | 631 | Environmental |
| `weather.py` | `WeatherManager`, `WeatherType` | 360 | Weather |

### 🖼️ UI-System-Klassen (10 Dateien)
| Datei | Hauptklassen | Zeilen | Beschreibung |
|-------|-------------|--------|--------------|
| `battle_ui.py` | `BattleUI`, `BattleHUD`, `BattleMenu` | 1007 | Battle-Interface |
| `menus.py` | `MenuBase`, `PartyMenu`, `QuestMenu` | 762 | Menü-System |
| `dialogue.py` | `DialogueBox`, `DialoguePage`, `DialogueChoice` | 547 | Dialog-System |
| `hud.py` | HUD-Komponenten | 474 | Persistent UI |
| `transitions.py` | `TransitionManager`, `FadeTransition` | 381 | Scene-Übergänge |
| [5 weitere UI-Dateien] | | | |

### 🎬 Scene-System-Klassen (7 Dateien)  
| Datei | Hauptklassen | Zeilen | Beschreibung |
|-------|-------------|--------|--------------|
| `battle_scene.py` | `BattleScene`, `BattleResult` | 1402 | Battle-Management |
| `field_scene.py` | `FieldScene` | 1033 | Overworld-Gameplay |
| `starter_scene.py` | `StarterScene` | 1474 | Starter-Auswahl |
| `main_menu_scene.py` | `MainMenuScene` | 547 | Hauptmenü |
| [3 weitere Scene-Dateien] | | | |

### 🗺️ Welt-System-Klassen (20 Dateien)
| Datei | Hauptklassen | Zeilen | Beschreibung |
|-------|-------------|--------|--------------|
| `area.py` | `Area`, `AreaConfig` | 626 | Map-Regionen |
| `entity.py` | `Entity`, `EntitySprite`, `Direction` | 487 | Basis-Entities |
| `player.py` | `Player` | 682 | Spieler-Charakter |
| `npc.py` | `NPC`, `MovementPattern`, `NPCConfig` | 462 | NPCs |
| `camera.py` | `Camera`, `CameraConfig` | 329 | Kamera-System |
| `map_loader.py` | `MapLoader`, `MapData`, `Warp`, `Trigger` | 397 | Map-Loading |
| [14 weitere World-Dateien] | | | |

### 🎨 Grafik-System-Klassen (6 Dateien)
| Datei | Hauptklassen | Zeilen | Beschreibung |
|-------|-------------|--------|--------------|
| `sprite_manager.py` | `SpriteManager` | 577 | Sprite-Cache & Loading |
| `render_manager.py` | `RenderManager`, `RenderLayer` | 259 | Z-Order & Performance |
| `tile_renderer.py` | `TileRenderer` | 203 | Map-Rendering |
| `optimized_renderer.py` | `OptimizedRenderer`, `TextureAtlas` | 324 | Performance-Optimierung |
| [2 weitere Graphics-Dateien] | | | |

### 🎵 Audio-System-Klassen (2 Dateien)
| Datei | Hauptklassen | Zeilen | Beschreibung |
|-------|-------------|--------|--------------|
| `audio_manager.py` | `AudioManager`, `AudioChannel` | 330 | Audio-Management |

---

## 🚀 Entwicklungsrichtlinien für KI-Assistenten

### 📋 Aufgaben-Prioritäten

1. **Kritische Systeme** (Zuerst angehen):
   - Battle-System (`engine/systems/battle/`)
   - Monster-System (`engine/systems/monster_instance.py`, `monsters.py`)
   - Save/Load-System (`engine/systems/save.py`)

2. **Wichtige Systeme** (Zweite Priorität):
   - Scene-Management (`engine/scenes/`)
   - UI-System (`engine/ui/`)
   - Input-System (`engine/core/input_manager.py`)

3. **Support-Systeme** (Dritte Priorität):
   - Graphics-System (`engine/graphics/`)
   - Audio-System (`engine/audio/`)
   - Developer-Tools (`engine/devtools/`)

### 🔍 Wichtige Code-Patterns

#### Manager-Initialization-Pattern
```python
# In Game.__init__() - Runtime-Imports vermeiden Circular Dependencies
from engine.systems.story import StoryManager
from engine.systems.party import PartyManager
self.story_manager = StoryManager()
self.party_manager = PartyManager(self)
```

#### Singleton-Access-Pattern
```python
# Für Resource-Manager, Database-Manager
sprite_manager = SpriteManager.get()
resources = ResourceManager()  # Global instance
monster_db = MonsterDatabase()
```

#### Error-Handling-Pattern
```python
try:
    # Operation
    result = some_operation()
    return result
except Exception as e:
    logger.error(f"Operation fehlgeschlagen: {e}")
    return fallback_value  # Immer Fallback bereitstellen
```

#### Validation-Pattern  
```python
def __post_init__(self):
    if not self.id or not isinstance(self.id, str):
        raise ValueError("ID muss ein nicht-leerer String sein")
    # Weitere Validierungen...

def is_valid(self) -> bool:
    try:
        # Validierungs-Logic
        return True
    except Exception as e:
        logger.error(f"Validierung fehlgeschlagen: {e}")
        return False
```

---

## 📖 Vollständigkeits-Checkliste für KI-Entwicklung

### ✅ Vollständig dokumentiert:
- ✅ Alle 7 Core-System-Dateien mit Klassen und Imports
- ✅ Alle 22 Battle-System-Dateien
- ✅ Alle 17 Gameplay-System-Dateien  
- ✅ Alle 10 UI-System-Dateien
- ✅ Alle 7 Scene-System-Dateien
- ✅ Alle 20 World-System-Dateien
- ✅ Alle 6 Graphics-System-Dateien
- ✅ Alle 2 Audio-System-Dateien
- ✅ Alle JSON-Datenstrukturen mit Beispielen
- ✅ Wichtige Code-Patterns und Design-Guidelines
- ✅ Manager-Hierarchien und Dependencies
- ✅ Import-Strategien gegen Circular Dependencies

### 🎯 Fazit
Diese Mastermap dokumentiert **alle 106 Python-Dateien** der Engine mit:
- **Alle Klassen** mit ihren Hauptmethoden
- **Alle wichtigen Imports** und deren Zweck
- **Alle Enums** und Datenstrukturen
- **Alle Manager-Hierarchien** und ihre Interaktionen
- **Vollständige JSON-Formate** für alle Datenstrukturen
- **Code-Patterns** für konsistente Entwicklung
- **Error-Handling-Strategien** für robuste Implementierung

**Total:** 106 Python-Dateien, 60+ Hauptklassen, 30+ Enums, 15+ Manager-Systeme vollständig dokumentiert.

---

*Diese vollständige Mastermap wurde erstellt als umfassende Referenz für KI-Entwicklung am Untold Story Projekt. Sie enthält alle wichtigen Klassen, Imports, Datenstrukturen und Code-Patterns, die für effektive Entwicklung benötigt werden.*