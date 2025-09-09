# Untold Story - Automatisch Generierte Code-Analyse

## 📊 Gesamt-Statistiken

- **Dateien:** 108
- **Zeilen:** 49,495
- **Klassen:** 373
- **Funktionen:** 80
- **Methoden:** 1957
- **Imports:** 895

## 🏗️ Module-Übersicht

### engine › audio (1 Dateien)

| Datei | Zeilen | Klassen | Funktionen | Beschreibung |
|-------|--------|---------|------------|--------------|
| `audio_manager.py` | 329 | 2 | 0 | Audio Manager für Untold Story |

### engine › core (9 Dateien)

| Datei | Zeilen | Klassen | Funktionen | Beschreibung |
|-------|--------|---------|------------|--------------|
| `config.py` | 559 | 15 | 2 | Central configuration and constants for the game. |
| `debug_config.py` | 70 | 1 | 0 | Debug-Konfiguration für Untold Story |
| `debug_overlay.py` | 169 | 2 | 0 | Debug Overlay Manager für Untold Story |
| `debug_utils.py` | 230 | 3 | 14 | Debug Utilities für Untold Story |
| `event_processor.py` | 255 | 2 | 0 | Event Processor für Untold Story |
| `game.py` | 543 | 2 | 0 | Main Game Loop and Scene Management for Untold Sto... |
| `input_manager.py` | 385 | 3 | 0 | Refactored Input Manager für Untold Story |
| `resources.py` | 1080 | 3 | 0 | Resource Loading and Caching System for Untold Sto... |
| `scene_base.py` | 235 | 2 | 0 | Base Scene Interface for Untold Story |

### engine › devtools (3 Dateien)

| Datei | Zeilen | Klassen | Funktionen | Beschreibung |
|-------|--------|---------|------------|--------------|
| `error_handler.py` | 263 | 3 | 0 | Zentrales Fehlerbehandlungssystem für Untold Story... |
| `hot_reload.py` | 459 | 4 | 0 | Hot reload system for development. |
| `input_debug.py` | 287 | 2 | 1 | Input Debug Tools für Untold Story |

### engine › graphics (5 Dateien)

| Datei | Zeilen | Klassen | Funktionen | Beschreibung |
|-------|--------|---------|------------|--------------|
| `asset_manager.py` | 454 | 6 | 0 | Asset-Manager für Untold Story |
| `optimized_renderer.py` | 323 | 6 | 0 | Optimierter Renderer für Untold Story |
| `render_manager.py` | 258 | 2 | 0 | Render Manager für Untold Story |
| `sprite_manager.py` | 577 | 1 | 0 | Keine Beschreibung |
| `tile_renderer.py` | 202 | 2 | 0 | Tile rendering system for map display. |

### engine › items (1 Dateien)

| Datei | Zeilen | Klassen | Funktionen | Beschreibung |
|-------|--------|---------|------------|--------------|
| `running_shoes.py` | 49 | 1 | 0 | Running Shoes Item für das Movement System |

### engine › scenes (7 Dateien)

| Datei | Zeilen | Klassen | Funktionen | Beschreibung |
|-------|--------|---------|------------|--------------|
| `battle_scene.py` | 626 | 2 | 0 | Battle Scene for Untold Story - SYNTAX FIXED VERSI... |
| `debug_monster_scene.py` | 277 | 1 | 0 | Debug Monster Selection Scene for Untold Story |
| `field_scene.py` | 1070 | 1 | 0 | Field Scene for Untold Story - AUFGERÄUMT VON FLIN... |
| `main_menu_scene.py` | 582 | 2 | 0 | Main menu scene for game start, load, and options. |
| `pause_scene.py` | 478 | 3 | 0 | Pause scene overlay for in-game menu. |
| `start_scene.py` | 380 | 1 | 0 | Start Scene for Untold Story |
| `starter_scene.py` | 1444 | 5 | 0 | Starter selection scene for Untold Story. |

### engine › scenes › battle (4 Dateien)

| Datei | Zeilen | Klassen | Funktionen | Beschreibung |
|-------|--------|---------|------------|--------------|
| `battle_scene_actions.py` | 177 | 1 | 0 | Battle Scene Action Execution. |
| `battle_scene_effects.py` | 152 | 1 | 0 | Battle Scene Effects and Rewards. |
| `battle_scene_input.py` | 189 | 1 | 0 | Battle Scene Input Handler. |
| `battle_scene_phases.py` | 72 | 1 | 0 | Battle Scene Phase Management. |

### engine › scenes › field (4 Dateien)

| Datei | Zeilen | Klassen | Funktionen | Beschreibung |
|-------|--------|---------|------------|--------------|
| `encounters.py` | 244 | 1 | 0 | Encounter & Battle System für FieldScene |
| `interaction.py` | 314 | 1 | 0 | Interaktions-System für FieldScene |
| `map_system.py` | 393 | 2 | 0 | Vereinheitlichtes Map-Loading System für Untold St... |
| `story.py` | 294 | 1 | 0 | Story Event System für FieldScene |

### engine › systems (22 Dateien)

| Datei | Zeilen | Klassen | Funktionen | Beschreibung |
|-------|--------|---------|------------|--------------|
| `conditions.py` | 580 | 4 | 0 | Detailed status condition system. |
| `cutscene.py` | 424 | 3 | 0 | Cutscene System für Untold Story |
| `experience_system.py` | 455 | 3 | 0 | Experience and Level System for Untold Story. |
| `field_effects.py` | 630 | 9 | 6 | Field Effects System for Untold Story |
| `items.py` | 497 | 9 | 0 | Comprehensive item system for Untold Story. |
| `items_clean.py` | 390 | 9 | 0 | Comprehensive item system for Untold Story. |
| `monster_instance.py` | 811 | 4 | 0 | Monster Instance System |
| `monsters.py` | 388 | 1 | 0 | Monster Species Database for Untold Story |
| `moves.py` | 711 | 7 | 0 | Move System for Untold Story |
| `party.py` | 658 | 4 | 0 | Party management system for monster teams. |
| `quests.py` | 579 | 6 | 0 | Quest system for tracking objectives, side quests,... |
| `save.py` | 648 | 3 | 0 | Save/Load system using JSON and ZIP compression. |
| `settings.py` | 381 | 7 | 0 | Settings System für Untold Story |
| `stats.py` | 484 | 7 | 0 | Stats System for Untold Story |
| `story.py` | 879 | 6 | 0 | Story system for managing plot progression, flags,... |
| `synthesis.py` | 510 | 5 | 0 | Monster synthesis/fusion system. |
| `talent_system.py` | 712 | 6 | 1 | 🎯 DQM Talent System - Dragon Quest Monsters Authen... |
| `taming.py` | 378 | 3 | 5 | Taming system for Untold Story. |
| `types.py` | 651 | 6 | 0 | Type System for Untold Story RPG |
| `unified_damage_calculator.py` | 1135 | 12 | 5 | Unified Damage Calculator for Untold Story |
| `weather.py` | 363 | 3 | 2 | Weather System for Untold Story |
| `world_state.py` | 175 | 2 | 0 | World State Management System for Untold Story |

### engine › systems › battle (15 Dateien)

| Datei | Zeilen | Klassen | Funktionen | Beschreibung |
|-------|--------|---------|------------|--------------|
| `battle_actions.py` | 843 | 4 | 2 | Battle Actions Module |
| `battle_ai.py` | 453 | 3 | 0 | AI system for enemy battle decisions. |
| `battle_controller.py` | 1138 | 2 | 0 | Battle Controller Module |
| `battle_effects.py` | 664 | 6 | 0 | Effect executor for battle system. |
| `battle_enums.py` | 67 | 5 | 0 | Battle Enums and Constants |
| `battle_events.py` | 637 | 4 | 2 | Battle Event System - RESTORED FROM ARCHIVE |
| `battle_system.py` | 85 | 0 | 3 | Battle System Compatibility Layer |
| `battle_validation.py` | 236 | 1 | 0 | Battle Validation Module |
| `dqm_formulas.py` | 706 | 7 | 0 | Dragon Quest Monsters Battle Formulas |
| `dqm_integration.py` | 317 | 1 | 3 | DQM Integration Module |
| `meat_system.py` | 298 | 3 | 1 | Meat System for Dragon Quest Monsters-style taming... |
| `reward_system.py` | 477 | 4 | 1 | Battle Rewards System for Untold Story. |
| `skills_dqm_integrated.py` | 322 | 6 | 1 | 🔮 Dragon Quest Monsters Skill System - INTEGRIERT ... |
| `status_effects_dqm.py` | 359 | 3 | 0 | DQM-Specific Status Effects System |
| `turn_logic_clean.py` | 414 | 3 | 2 | Turn order and priority system for battles. |

### engine › systems › battle › core (1 Dateien)

| Datei | Zeilen | Klassen | Funktionen | Beschreibung |
|-------|--------|---------|------------|--------------|
| `battle_manager.py` | 360 | 1 | 0 | Simplified Battle Manager for DQM-style battles. |

### engine › ui (16 Dateien)

| Datei | Zeilen | Klassen | Funktionen | Beschreibung |
|-------|--------|---------|------------|--------------|
| `accessibility.py` | 500 | 7 | 0 | Accessibility-System für Untold Story |
| `battle_log.py` | 483 | 4 | 0 | Battle Logging System for Untold Story. |
| `battle_menu_transitions.py` | 249 | 3 | 1 | Battle Menu Transitions - Phase 2 UI Polish |
| `battle_rewards_ui.py` | 567 | 3 | 0 | Battle Rewards UI for displaying victory rewards. |
| `battle_styles.py` | 251 | 3 | 3 | Battle UI Style Configuration for Untold Story. |
| `battle_ui.py` | 1662 | 4 | 0 | Pixel JRPG Battle UI für Untold Story |
| `battle_ui_enhancements.py` | 1057 | 5 | 7 | Battle UI Extensions for Enhanced Battle System |
| `battle_ui_utils.py` | 342 | 6 | 0 | Battle UI Utilities - Zentrale Hilfsfunktionen für... |
| `dialogue.py` | 547 | 4 | 0 | Dialogue System for Untold Story |
| `enhanced_menus.py` | 520 | 7 | 0 | Verbesserte Menü-Struktur für Untold Story |
| `hud.py` | 570 | 5 | 0 | HUD (Heads-Up Display) overlays for field and batt... |
| `menus.py` | 777 | 6 | 0 | Menu system for inventory, party management, quest... |
| `modern_ui_patterns.py` | 303 | 8 | 0 | Moderne UI-Patterns für Untold Story |
| `scout_display.py` | 772 | 3 | 0 | Scout Display component for the battle system. |
| `taming_ui.py` | 485 | 3 | 0 | Taming UI component for the battle system. |
| `transitions.py` | 381 | 6 | 0 | Screen Transition Effects for Untold Story |

### engine › world (20 Dateien)

| Datei | Zeilen | Klassen | Funktionen | Beschreibung |
|-------|--------|---------|------------|--------------|
| `area.py` | 627 | 2 | 0 | Area - Repräsentiert eine spielbare Map-Region |
| `camera.py` | 329 | 2 | 0 | Camera System for Untold Story |
| `enhanced_map_manager.py` | 709 | 1 | 0 | Enhanced Map Manager for Untold Story |
| `entity.py` | 487 | 3 | 0 | Base Entity System for Untold Story |
| `gid_mapper.py` | 70 | 1 | 0 | GID Mapper für TMX-Maps |
| `interaction_manager.py` | 445 | 6 | 0 | Interaction Manager for Untold Story |
| `ledge_handler.py` | 86 | 1 | 0 | Ledge Handler für das Grid-basierte Movement Syste... |
| `map_loader.py` | 397 | 4 | 0 | Map Loading and Normalization for Untold Story |
| `map_transition.py` | 54 | 1 | 0 | Map Transition System für smooth Übergänge zwische... |
| `movement_states.py` | 17 | 1 | 0 | Movement States für das Grid-basierte Movement Sys... |
| `npc.py` | 461 | 3 | 0 | NPC - Non-Player Character System for Untold Story |
| `npc_improved.py` | 662 | 3 | 0 | Verbessertes NPC-System mit Pathfinding und Bewegu... |
| `npc_manager.py` | 368 | 2 | 0 | NPC Manager for Untold Story |
| `pathfinding.py` | 139 | 1 | 5 | Grid-based A* pathfinding for 16x16 tile maps. |
| `pathfinding_mixin.py` | 261 | 1 | 0 | PathfindingMixin für NPCs - ENDLICH INTELLIGENTE B... |
| `player.py` | 682 | 1 | 0 | Keine Beschreibung |
| `tile_ids.py` | 257 | 0 | 4 | Tile ID Konstanten für das Untold Story Spiel. |
| `tile_manager.py` | 597 | 2 | 0 | Tile Manager - Zentrales Tile-Management mit TMX-S... |
| `tiles.py` | 103 | 3 | 8 | Keine Beschreibung |
| `tmx_init.py` | 44 | 0 | 1 | TMX Initialization Module - Real Implementation |

## 🔍 Detaillierte Code-Analyse

### engine › audio

#### `audio_manager.py` (329 Zeilen)

**Beschreibung:** Audio Manager für Untold Story
Erweiterte Audio-Verwaltung mit Kanälen, Fading und Mix-Kontrolle

**Imports:**
```python
import pygame
import threading
from typing import Dict, Optional, List, Tuple
from pathlib import Path
from enum import Enum
from engine.core.resources import ResourceManager
```

**Klassen:**
- `AudioChannel(Enum)` (Zeile 13)
  - Audio channel types for organization.
- `AudioManager` (Zeile 22)
  - Enhanced audio manager with channel mixing and advanced features.
  - **Methoden:** `__init__()`, `set_master_volume()`, `set_channel_volume()`, `get_effective_volume()`, `load_sound()`, ... (+11 weitere)

### engine › core

#### `config.py` (559 Zeilen)

**Beschreibung:** Central configuration and constants for the game.

**Imports:**
```python
from enum import Enum, auto
from typing import Dict, Tuple, Any
import os
from pathlib import Path
from engine.world.tiles import TILE_SIZE
import platform
```

**Konstanten:** GAME_TITLE, GAME_VERSION, GAME_AUTHOR, LOGICAL_WIDTH, LOGICAL_HEIGHT, WINDOW_SCALE, WINDOW_WIDTH, WINDOW_HEIGHT, TARGET_FPS, VSYNC, HALF_TILE, PLAYER_COLLISION_SIZE, PLAYER_SPEED, NPC_SPEED, RUN_MULTIPLIER, DIAGONAL_FACTOR, BASE_DIR, ASSETS_DIR, DATA_DIR, SAVES_DIR, LOGS_DIR, GFX_DIR, SFX_DIR, BGM_DIR, FONTS_DIR, MAPS_DIR, DIALOGS_DIR, PLATFORM, IS_WINDOWS, IS_MAC, IS_LINUX, USER_DATA_DIR, USER_DATA_DIR, USER_DATA_DIR, CAMERA_DEADZONE_WIDTH, CAMERA_DEADZONE_HEIGHT, CAMERA_FOLLOW_SPEED

**Klassen:**
- `Colors` (Zeile 58)
  - Common color constants.
- `InputConfig` (Zeile 104)
  - Input configuration.
- `BattleConfig` (Zeile 132)
  - Battle system configuration.
- `MonsterConfig` (Zeile 167)
  - Monster system configuration.
- `AudioConfig` (Zeile 273)
  - Audio configuration.
- `GraphicsConfig` (Zeile 289)
  - Graphics configuration.
- `BalanceConfig` (Zeile 317)
  - Game balance configuration.
- `DebugConfig` (Zeile 348)
  - Debug configuration.
- `NetworkConfig` (Zeile 371)
  - Network configuration.
- `SaveConfig` (Zeile 380)
  - Save system configuration.
- `LocalizationConfig` (Zeile 393)
  - Localization settings.
- `PerformanceConfig` (Zeile 407)
  - Performance optimization settings.
- `Fonts` (Zeile 454)
  - Font configuration for the game.
- `UI` (Zeile 475)
  - UI configuration constants.
- `GameState(Enum)` (Zeile 498)
  - Game state enumeration.

**Funktionen:** `get_config_value()`, `set_config_value()`

#### `debug_config.py` (70 Zeilen)

**Beschreibung:** Debug-Konfiguration für Untold Story
Zentrale Konfiguration für Debug-Features und Hotkeys

**Imports:**
```python
from engine.core.debug_utils import debug_manager, DebugLevel, DebugCategory
```

**Klassen:**
- `DebugConfig` (Zeile 9)
  - Debug-Konfiguration für das Spiel.
  - **Methoden:** `initialize_debug_system()`, `get_debug_help_text()`, `print_debug_status()`

#### `debug_overlay.py` (169 Zeilen)

**Beschreibung:** Debug Overlay Manager für Untold Story
Verwaltet Debug-Informationen und Overlay-Rendering

**Imports:**
```python
import pygame
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from engine.core.debug_utils import debug_system_error
from engine.world.tiles import TILE_SIZE
```

**Klassen:**
- `@dataclass DebugInfo` (Zeile 12)
  - Debug-Informationen für das Overlay.
- `DebugOverlayManager` (Zeile 25)
  - Verwaltet Debug-Overlay und -Informationen.
  - **Methoden:** `__init__()`, `_init_font()`, `draw_debug_overlay()`, `_collect_debug_info()`, `_draw_debug_text()`, ... (+3 weitere)

#### `debug_utils.py` (230 Zeilen)

**Beschreibung:** Debug Utilities für Untold Story
Zentrale Debug-Funktionen und Logging-System

**Imports:**
```python
import sys
from typing import Optional, Any, Dict
from enum import Enum, auto
```

**Klassen:**
- `DebugLevel(Enum)` (Zeile 11)
  - Debug-Level für verschiedene Arten von Debug-Informationen.
- `DebugCategory(Enum)` (Zeile 20)
  - Kategorien für Debug-Outputs.
- `DebugManager` (Zeile 32)
  - Zentraler Debug-Manager für das Spiel.
  - **Methoden:** `__init__()`, `set_game_instance()`, `is_enabled()`, `should_log()`, `log()`, ... (+9 weitere)

**Funktionen:** `debug_error()`, `debug_warning()`, `debug_info()`, `debug_debug()`, `debug_trace()`, `debug_battle_error()`, `debug_battle_info()`, `debug_battle_debug()`, `debug_scene_error()`, `debug_scene_info()`, `debug_scene_debug()`, `debug_system_error()`, `debug_system_info()`, `debug_system_debug()`

#### `event_processor.py` (255 Zeilen)

**Beschreibung:** Event Processor für Untold Story
Verarbeitet pygame Events und aktualisiert Input-Status

**Imports:**
```python
import pygame
import time
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass
from engine.core.debug_utils import debug_manager, debug_system_info
from engine.core.debug_utils import debug_manager
```

**Klassen:**
- `@dataclass DebugKeyConfig` (Zeile 13)
  - Konfiguration für Debug-Hotkeys.
- `EventProcessor` (Zeile 27)
  - Verarbeitet pygame Events und aktualisiert Input-Status.
  - **Methoden:** `__init__()`, `_setup_debug_actions()`, `process_events()`, `_handle_debug_hotkeys()`, `_toggle_debug_overlay()`, ... (+12 weitere)

#### `game.py` (543 Zeilen)

**Beschreibung:** Main Game Loop and Scene Management for Untold Story - REFACTORED VERSION
Handles the core game loop, input processing, scene stack, and rendering pipeline

**Imports:**
```python
from typing import Optional, List, Dict, Any, Tuple, Type
from collections import deque
import pygame
import time
from engine.core.event_processor import EventProcessor
from engine.core.debug_overlay import DebugOverlayManager
from engine.core.debug_utils import debug_manager, debug_system_info, debug_system_error
from engine.core.debug_utils import debug_manager
from engine.systems.story import StoryManager
from engine.systems.party import PartyManager
from engine.core.resources import ResourceManager
from engine.systems.cutscene import CutsceneManager
from engine.ui.transitions import TransitionManager
from engine.systems.settings import SettingsManager
from engine.systems.items_clean import Inventory
from engine.systems.quests import QuestManager
from engine.systems.world_state import world_state
from engine.audio.audio_manager import AudioManager
from engine.ui.transitions import TransitionManager
from engine.ui.transitions import TransitionManager
from engine.world.tiles import TILE_SIZE
from engine.core.input_manager import InputManager, InputConfig
from engine.devtools.input_debug import get_input_debugger
from engine.graphics.tile_renderer import TileRenderer
from engine.scenes.start_scene import StartScene
from engine.ui.transitions import FadeTransition
from engine.ui.transitions import TransitionType
```

**Klassen:**
- `Game` (Zeile 17)
  - Core game class that manages the main loop, scene stack, input, and rendering.
  - **Methoden:** `__init__()`, `initialize_graphics()`, `init_input_system()`, `_init_story_system()`, `set_sprite_manager()`, ... (+13 weitere)
  - **Properties:** `current_scene`
- `_SimpleTransitionManager` (Zeile 119)
  - **Methoden:** `__init__()`, `start()`, `create_transition()`

#### `input_manager.py` (385 Zeilen)

**Beschreibung:** Refactored Input Manager für Untold Story
Vereinfachte Version ohne Code-Duplikation

**Imports:**
```python
import pygame
from typing import Dict, Set, Optional, Tuple, List
from dataclasses import dataclass, field
import time
import time
import time
```

**Klassen:**
- `@dataclass InputConfig` (Zeile 12)
  - Konfiguration für Input-Mapping.
- `@dataclass InputState` (Zeile 43)
  - Zentraler Input-Status.
- `InputManager` (Zeile 52)
  - Vereinfachter Input-Manager ohne Code-Duplikation.
  - **Methoden:** `__init__()`, `_build_input_map()`, `_create_key_name_mapping()`, `_get_key_name()`, `_log_input()`, ... (+17 weitere)

#### `resources.py` (1080 Zeilen)

**Beschreibung:** Resource Loading and Caching System for Untold Story
Handles loading and caching of images, JSON data, sounds, and other assets
OPTIMIERT: Intelligente LRU-Cache-Strategien und verbessertes Memory-Management

**Imports:**
```python
import json
import pygame
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, Union, List
from enum import Enum
from functools import lru_cache
import time
import weakref
import gc
import array
import math
```

**Klassen:**
- `ResourceType(Enum)` (Zeile 17)
  - Types of resources that can be loaded.
- `LRUCache` (Zeile 25)
  - OPTIMIERT: Intelligente LRU-Cache-Implementierung mit Memory-Management.
  - **Methoden:** `__init__()`, `get()`, `put()`, `_evict_least_recent()`, `cleanup()`, ... (+1 weitere)
- `ResourceManager` (Zeile 107)
  - Singleton resource manager for loading and caching game assets.
  - **Methoden:** `__new__()`, `__init__()`, `_ensure_display_and_load_essentials()`, `_cleanup_caches()`, `_cleanup_legacy_cache()`, ... (+31 weitere)

#### `scene_base.py` (235 Zeilen)

**Beschreibung:** Base Scene Interface for Untold Story
Defines the abstract base class for all game scenes

**Imports:**
```python
from abc import ABC, abstractmethod
from typing import Optional, Any, Dict
import pygame
```

**Klassen:**
- `Scene(ABC)` (Zeile 11)
  - Abstract base class for all game scenes.
  - **Methoden:** `__init__()`, `enter()`, `exit()`, `pause()`, `resume()`, ... (+8 weitere)
- `TransitionScene(Scene)` (Zeile 175)
  - Base class for transition effects between scenes.
  - **Methoden:** `__init__()`, `update()`, `handle_event()`

### engine › devtools

#### `error_handler.py` (263 Zeilen)

**Beschreibung:** Zentrales Fehlerbehandlungssystem für Untold Story.
Protokolliert Fehler, zeigt Warnungen an und ermöglicht Fehleranalyse.

**Imports:**
```python
import sys
import traceback
import logging
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from pathlib import Path
from enum import Enum
import pygame
```

**Klassen:**
- `ErrorSeverity(Enum)` (Zeile 17)
  - Schweregrade für Fehler.
- `@dataclass ErrorEntry` (Zeile 26)
  - Ein protokollierter Fehler.
- `ErrorHandler` (Zeile 36)
  - Zentrales Fehlerbehandlungssystem.
  - **Methoden:** `__init__()`, `_setup_logging()`, `log_error()`, `handle_exception()`, `handle_critical_error()`, ... (+3 weitere)

#### `hot_reload.py` (459 Zeilen)

**Beschreibung:** Hot reload system for development.
Automatically reloads assets and data when files change.

**Imports:**
```python
import os
import json
import time
from pathlib import Path
from typing import Dict, Set, Callable, Any, Optional
from dataclasses import dataclass
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent
from engine.core.config import DATA_DIR, ASSETS_DIR
import toml
import toml
import fnmatch
```

**Klassen:**
- `@dataclass FileWatcher` (Zeile 20)
  - Watches a file for changes.
- `HotReloadHandler(FileSystemEventHandler)` (Zeile 28)
  - Handles file system events for hot reload.
  - **Methoden:** `__init__()`, `on_modified()`
- `HotReloader` (Zeile 47)
  - Hot reload system for game assets and data.
  - **Methoden:** `__init__()`, `start()`, `stop()`, `file_changed()`, `_verify_file_integrity()`, ... (+15 weitere)
- `AssetCache` (Zeile 411)
  - Cache for hot-reloadable assets.
  - **Methoden:** `__init__()`, `get()`, `set()`, `clear()`, `clear_all()`, ... (+1 weitere)

#### `input_debug.py` (287 Zeilen)

**Beschreibung:** Input Debug Tools für Untold Story
Erweiterte Debug-Funktionen für Keyboard-Input-Analyse

**Imports:**
```python
import pygame
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import time
import json
```

**Klassen:**
- `@dataclass InputEvent` (Zeile 14)
  - Einzelner Input-Event mit allen relevanten Informationen.
- `InputDebugger` (Zeile 27)
  - Erweiterter Input-Debugger für detaillierte Fehleranalyse.
  - **Methoden:** `__init__()`, `record_event()`, `set_filter()`, `clear_filter()`, `get_filtered_events()`, ... (+8 weitere)

**Funktionen:** `get_input_debugger()`

### engine › graphics

#### `asset_manager.py` (454 Zeilen)

**Beschreibung:** Asset-Manager für Untold Story
Verbessert Asset-Organisation und -Qualität

**Imports:**
```python
import pygame
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, Set
from dataclasses import dataclass
from enum import Enum, auto
import json
import hashlib
from PIL import Image
import io
from engine.core.config import ASSETS_DIR, GFX_DIR, SFX_DIR, BGM_DIR
```

**Klassen:**
- `AssetType(Enum)` (Zeile 20)
  - Arten von Assets.
- `AssetQuality(Enum)` (Zeile 30)
  - Qualitätsstufen für Assets.
- `@dataclass AssetInfo` (Zeile 39)
  - Metadaten für ein Asset.
- `AssetValidator` (Zeile 53)
  - Validiert Asset-Qualität und -Konsistenz.
  - **Methoden:** `__init__()`, `validate_asset()`, `_calculate_quality_score()`, `_generate_tags()`, `_calculate_file_hash()`
- `AssetOptimizer` (Zeile 187)
  - Optimiert Assets für bessere Performance.
  - **Methoden:** `__init__()`, `optimize_sprite()`, `create_sprite_atlas()`
- `AssetManager` (Zeile 281)
  - Hauptklasse für Asset-Verwaltung.
  - **Methoden:** `__init__()`, `scan_assets()`, `_scan_directory()`, `get_asset()`, `optimize_assets()`, ... (+3 weitere)

#### `optimized_renderer.py` (323 Zeilen)

**Beschreibung:** Optimierter Renderer für Untold Story
Implementiert verbessertes Caching, Asset-Atlasierung und effizientes Font-Rendering

**Imports:**
```python
import pygame
import weakref
from typing import Dict, List, Tuple, Optional, Any, Set
from dataclasses import dataclass
from pathlib import Path
import json
import hashlib
from engine.core.config import LOGICAL_WIDTH, LOGICAL_HEIGHT, TILE_SIZE
```

**Klassen:**
- `@dataclass CachedSurface` (Zeile 17)
  - Gecachte Oberfläche mit Metadaten.
- `@dataclass AtlasRegion` (Zeile 27)
  - Region in einem Texture-Atlas.
- `TextureAtlas` (Zeile 36)
  - Texture-Atlas für effizientes Rendering.
  - **Methoden:** `__init__()`, `add_texture()`, `get_region()`, `get_atlas_surface()`, `get_usage_percentage()`
- `FontCache` (Zeile 97)
  - Cache für gerenderte Font-Texturen.
  - **Methoden:** `__init__()`, `get_font()`, `render_text()`, `_cleanup_cache()`, `update()`
- `OptimizedRenderer` (Zeile 175)
  - Optimierter Renderer mit verbesserten Performance-Features.
  - **Methoden:** `__init__()`, `add_to_atlas()`, `render_text()`, `render_sprite()`, `render_batch()`, ... (+5 weitere)
- `RenderOptimizer` (Zeile 271)
  - Optimiert Rendering-Operationen.
  - **Methoden:** `__init__()`, `optimize_surface()`, `create_sprite_sheet()`

#### `render_manager.py` (258 Zeilen)

**Beschreibung:** Render Manager für Untold Story
Koordinierte Rendering-Operationen mit korrekter Z-Order-Behandlung

**Imports:**
```python
import pygame
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from world.area import Area
from world.entity import Entity
from world.camera import Camera
from tile_renderer import TileRenderer
from sprite_manager import SpriteManager
```

**Klassen:**
- `@dataclass RenderLayer` (Zeile 16)
  - Repräsentiert eine Rendering-Ebene mit Z-Index.
  - **Methoden:** `__post_init__()`
- `RenderManager` (Zeile 27)
  - Verwaltet alle Rendering-Operationen mit Performance-Optimierungen.
  - **Methoden:** `__init__()`, `_setup_default_layers()`, `add_layer()`, `add_entity_to_layer()`, `remove_entity_from_layer()`, ... (+18 weitere)

#### `sprite_manager.py` (577 Zeilen)

**Imports:**
```python
from __future__ import annotations
import os
from pathlib import Path
from typing import Dict, Optional, Tuple, Any
import json
import pygame
from engine.world.tiles import TILE_SIZE
import xml.etree.ElementTree as ET
import xml.etree.ElementTree as ET
```

**Klassen:**
- `SpriteManager` (Zeile 11)
  - Zentraler Asset-Cache.
  - **Methoden:** `get()`, `__new__()`, `__init__()`, `_ensure_loaded()`, `_ensure_display()`, ... (+29 weitere)
  - **Properties:** `monster_sprites`

#### `tile_renderer.py` (202 Zeilen)

**Beschreibung:** Tile rendering system for map display.

**Imports:**
```python
import pygame
from typing import List, Optional, Tuple, Dict, Any
from sprite_manager import SpriteManager
from world.tiles import TILE_SIZE
from world.camera import Camera
```

**Klassen:**
- `Camera` (Zeile 12)
  - **Methoden:** `__init__()`
- `TileRenderer` (Zeile 16)
  - Rendert Tiles aus dem SpriteManager.
  - **Methoden:** `__init__()`, `render_layer()`, `_get_tile_sprite()`, `_create_placeholder_tile()`, `_is_empty_tile()`, ... (+3 weitere)

### engine › items

#### `running_shoes.py` (49 Zeilen)

**Beschreibung:** Running Shoes Item für das Movement System
Ermöglicht dem Spieler das Rennen

**Klassen:**
- `RunningShoes` (Zeile 7)
  - Running shoes item that enables running.
  - **Methoden:** `give_running_shoes()`, `can_run()`, `check_running_shoes_obtained()`, `show_running_tutorial()`, `get_running_speed_multiplier()`

### engine › scenes

#### `battle_scene.py` (626 Zeilen)

**Beschreibung:** Battle Scene for Untold Story - SYNTAX FIXED VERSION
Alle Syntax-Fehler behoben, funktionsfähig

**Imports:**
```python
import pygame
import random
from typing import Optional, List, Dict, Any
from enum import Enum, auto
from engine.core.scene_base import Scene
from engine.core.config import Colors, GameState
from engine.ui.battle_ui import BattleUI, BattleMenuState
from engine.ui.battle_rewards_ui import BattleRewardsUI
from engine.systems.battle.battle_controller import BattleState, BattlePhase, BattleType
from engine.systems.battle.battle_ai import BattleAI
from engine.systems.battle.battle_enums import BattleResult
from engine.systems.battle.reward_system import RewardSystem, BattleRewards
from engine.systems.monster_instance import MonsterInstance
from engine.core.debug_utils import debug_battle_info, debug_battle_error, debug_battle_debug
from engine.systems.monsters import MonsterDatabase
from engine.systems.battle.battle_controller import BattleController
import traceback
from engine.systems.moves import MoveRegistry
from engine.systems.battle.turn_logic_clean import BattleAction, ActionType
from engine.systems.battle.turn_logic_clean import BattleAction, ActionType
from engine.systems.battle.turn_logic_clean import BattleAction, ActionType
from engine.systems.battle.turn_logic_clean import BattleAction, ActionType
from dataclasses import dataclass
import traceback
import traceback
```

**Klassen:**
- `BattleScene(Scene)` (Zeile 23)
  - Main battle scene - SYNTAX FIXED.
  - **Methoden:** `__init__()`, `on_enter()`, `handle_event()`, `_handle_keyboard_input()`, `_handle_attack_action()`, ... (+12 weitere)
- `@dataclass FallbackRewards` (Zeile 491)

#### `debug_monster_scene.py` (277 Zeilen)

**Beschreibung:** Debug Monster Selection Scene for Untold Story
Allows selecting a monster from the database to start on Route 1

**Imports:**
```python
import pygame
from typing import Optional, List, Dict, Any
from engine.core.scene_base import Scene
from engine.core.resources import resources
from engine.systems.monsters import MonsterDatabase
from engine.systems.monster_instance import MonsterInstance
from engine.scenes.start_scene import StartScene
from engine.scenes.field_scene import FieldScene
import traceback
```

**Klassen:**
- `DebugMonsterScene(Scene)` (Zeile 14)
  - Debug scene for selecting a monster to start with on Route 1.
  - **Methoden:** `__init__()`, `_load_fonts()`, `_load_monsters()`, `enter()`, `handle_event()`, ... (+6 weitere)

#### `field_scene.py` (1070 Zeilen)

**Beschreibung:** Field Scene for Untold Story - AUFGERÄUMT VON FLINT!
Main overworld gameplay scene mit Map, Player, NPCs und Interaktionen
Jetzt ohne den ganzen überflüssigen Scheiß!

**Imports:**
```python
import pygame
import random
import json
from typing import Optional, List, Dict, Any, Tuple
from engine.core.scene_base import Scene
from engine.core.resources import resources
from engine.world.tiles import TILE_SIZE, world_to_tile, tile_to_world, draw_grid
from engine.world.map_loader import MapLoader, MapData, Warp, Trigger
from engine.world.camera import Camera, CameraConfig
from engine.world.entity import Entity, Direction
from engine.world.player import Player
from engine.ui.dialogue import DialogueBox, DialoguePage, DialogueChoice
from engine.world.map_transition import MapTransition
from engine.systems.monster_instance import MonsterInstance
from engine.ui.transitions import TransitionType
from engine.graphics.sprite_manager import SpriteManager
from engine.graphics.tile_renderer import TileRenderer
from engine.world.area import Area
import os
from engine.world.player import Player
from engine.world.tiles import TILE_SIZE
from engine.scenes.starter_scene import StarterScene
from engine.world.map_loader import MapLoader
from engine.world.camera import Camera, CameraConfig
from engine.world.area import Area
import traceback
from engine.world.map_loader import MapData
from engine.world.tiles import TILE_SIZE
from engine.world.area import Area
from engine.world.tiles import TILE_SIZE
from engine.world.npc import NPC
from engine.world.npc import MovementPattern
from engine.world.entity import Direction
from engine.world.entity import Direction
from engine.scenes.pause_scene import PauseScene
from engine.graphics.render_manager import RenderManager
from engine.world.tiles import draw_grid
from engine.scenes.starter_scene import StarterScene
from engine.world.npc import NPC
from engine.world.map_loader import Warp
from engine.systems.monster_instance import MonsterInstance
from engine.systems.monster_instance import MonsterInstance
from engine.systems.monster_instance import MonsterSpecies
from engine.systems.stats import BaseStats
from engine.scenes.battle_scene import BattleScene
```

**Klassen:**
- `FieldScene(Scene)` (Zeile 29)
  - Main overworld gameplay scene - jetzt aufgeräumt!.
  - **Methoden:** `__init__()`, `_load_graphics()`, `_initialize_player()`, `_check_starter_requirement()`, `enter()`, ... (+30 weitere)

#### `main_menu_scene.py` (582 Zeilen)

**Beschreibung:** Main menu scene for game start, load, and options.

**Imports:**
```python
import pygame
from typing import TYPE_CHECKING, Optional, List, Tuple
from enum import Enum, auto
from engine.core.scene_base import Scene
from engine.ui.transitions import FadeTransition
from engine.systems.save import SaveSystem, SaveMetadata
from engine.core.game import Game
from engine.systems.party import Party
from engine.scenes.field_scene import FieldScene
from engine.systems.save import GameStateSerializer
from engine.scenes.field_scene import FieldScene
```

**Klassen:**
- `MenuOption(Enum)` (Zeile 17)
  - Main menu options.
- `MainMenuScene(Scene)` (Zeile 26)
  - Main menu scene.
  - **Methoden:** `__init__()`, `_check_saves()`, `handle_event()`, `_handle_main_menu_input()`, `_handle_submenu_input()`, ... (+15 weitere)

#### `pause_scene.py` (478 Zeilen)

**Beschreibung:** Pause scene overlay for in-game menu.

**Imports:**
```python
import pygame
from typing import TYPE_CHECKING, Optional, List
from enum import Enum, auto
from engine.core.scene_base import Scene
from engine.core.game import Game
from engine.scenes.field_scene import FieldScene
from engine.ui.enhanced_menus import EnhancedInventoryMenu
from engine.ui.menus import InventoryMenu
from engine.ui.enhanced_menus import EnhancedPartyMenu
from engine.ui.menus import PartyMenu
from engine.ui.menus import QuestMenu
from engine.ui.menus import SaveMenu
from engine.ui.menus import ConfirmDialog
from engine.scenes.main_menu_scene import MainMenuScene
```

**Klassen:**
- `PauseOption(Enum)` (Zeile 16)
  - Pause menu options.
- `PauseScene(Scene)` (Zeile 27)
  - Pause menu overlay scene.
  - **Methoden:** `__init__()`, `handle_event()`, `_handle_menu_input()`, `_select_option()`, `_resume_game()`, ... (+14 weitere)
- `SimpleOptionsMenu` (Zeile 198)
  - **Methoden:** `__init__()`, `handle_event()`, `update()`, `draw()`

#### `start_scene.py` (380 Zeilen)

**Beschreibung:** Start Scene for Untold Story
Title screen with "Press Start" prompt

**Imports:**
```python
import pygame
import math
from typing import Optional
from engine.core.scene_base import Scene
from engine.core.resources import resources
import random
from engine.scenes.main_menu_scene import MainMenuScene
from engine.scenes.debug_monster_scene import DebugMonsterScene
```

**Klassen:**
- `StartScene(Scene)` (Zeile 13)
  - Title screen scene with animated logo and press start prompt.
  - **Methoden:** `__init__()`, `_load_fonts()`, `_init_particles()`, `enter()`, `exit()`, ... (+9 weitere)

#### `starter_scene.py` (1444 Zeilen)

**Beschreibung:** Starter selection scene for Untold Story.
Player chooses their first monster from Professor Budde's fossils.

**Imports:**
```python
import pygame
import math
import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from engine.core.scene_base import Scene
from engine.core.config import LOGICAL_WIDTH, LOGICAL_HEIGHT, Colors
from engine.systems.monster_instance import MonsterInstance
from engine.ui.dialogue import DialogueBox
from engine.systems.moves import move_registry
from engine.systems.monster_instance import MonsterSpecies, MonsterInstance, MonsterRank
from engine.systems.stats import BaseStats, GrowthCurve
from engine.systems.monster_instance import MonsterSpecies, MonsterInstance
from engine.systems.stats import BaseStats, GrowthCurve
from engine.systems.monster_instance import MonsterRank
from engine.ui.dialogue import DialoguePage
from engine.ui.dialogue import DialogueState
from engine.ui.dialogue import DialogueState
from engine.ui.dialogue import DialoguePage
from engine.ui.dialogue import DialoguePage
from engine.ui.dialogue import DialoguePage
from engine.systems.story import StoryManager
from engine.scenes.field_scene import FieldScene
```

**Klassen:**
- `@dataclass ManagerStatus` (Zeile 18)
  - Status information for a manager.
- `StarterScene(Scene)` (Zeile 25)
  - Scene for selecting starter monster.
  - **Methoden:** `__init__()`, `_load_fonts_with_fallbacks()`, `_check_manager_availability()`, `_log_manager_status()`, `_safe_get_monster_species()`, ... (+32 weitere)
- `DummyMove` (Zeile 494)
  - **Methoden:** `__init__()`
- `CrashPreventionMonster` (Zeile 718)
  - **Methoden:** `__init__()`
- `DummyStoryManager` (Zeile 1109)
  - **Methoden:** `set_flag()`, `get_flag()`, `advance_quest()`, `_check_phase_progression()`

### engine › scenes › battle

#### `battle_scene_actions.py` (177 Zeilen)

**Beschreibung:** Battle Scene Action Execution.
Handles execution of battle actions like attacks, items, fleeing, etc.

**Imports:**
```python
import random
from typing import Optional, Dict, TYPE_CHECKING
from engine.systems.monster_instance import MonsterInstance
from battle_scene import BattleScene
from engine.systems.battle.turn_logic_clean import BattleAction, ActionType
from engine.systems.battle.turn_logic_clean import BattleAction, ActionType
from engine.systems.battle.turn_logic_clean import BattleAction, ActionType
from engine.systems.battle.turn_logic_clean import BattleAction, ActionType
```

**Klassen:**
- `BattleSceneActionHandler` (Zeile 15)
  - Handles battle action execution within the BattleScene context.
  - **Methoden:** `__init__()`, `execute_action()`, `execute_attack()`, `execute_tame()`, `execute_item()`, ... (+1 weitere)

#### `battle_scene_effects.py` (152 Zeilen)

**Beschreibung:** Battle Scene Effects and Rewards.
Handles status effects, experience distribution, and battle end conditions.

**Imports:**
```python
from typing import TYPE_CHECKING
from engine.systems.monster_instance import MonsterInstance
from battle_scene import BattleScene, BattleResult
from battle_scene import BattleResult
```

**Klassen:**
- `BattleEffectsManager` (Zeile 13)
  - Manages battle effects and rewards.
  - **Methoden:** `__init__()`, `process_status_effects()`, `check_defeated()`, `check_battle_end()`, `calculate_exp_reward()`, ... (+4 weitere)

#### `battle_scene_input.py` (189 Zeilen)

**Beschreibung:** Battle Scene Input Handler.
Manages input during battle and converts it to battle actions.

**Imports:**
```python
import pygame
from typing import Optional, Dict, TYPE_CHECKING
from engine.systems.battle.battle_controller import BattlePhase
from battle_scene import BattleScene
from engine.systems.battle.turn_logic_clean import BattleAction, ActionType
```

**Klassen:**
- `BattleInputHandler` (Zeile 15)
  - Handles input during battle.
  - **Methoden:** `__init__()`, `handle_event()`, `create_battle_action()`, `get_ai_action()`

#### `battle_scene_phases.py` (72 Zeilen)

**Beschreibung:** Battle Scene Phase Management.
Handles different battle phases and their transitions.

**Imports:**
```python
from typing import TYPE_CHECKING
from engine.systems.battle.battle_controller import BattlePhase
from battle_scene import BattleScene
```

**Klassen:**
- `BattlePhaseManager` (Zeile 13)
  - Manages battle phase transitions and updates.
  - **Methoden:** `__init__()`, `update_intro_phase()`, `update_input_phase()`, `update_execution_phase()`, `update_aftermath_phase()`, ... (+2 weitere)

### engine › scenes › field

#### `encounters.py` (244 Zeilen)

**Beschreibung:** Encounter & Battle System für FieldScene
Verwaltet Zufallsbegegnungen und Kampf-Initialisierung

**Imports:**
```python
import random
from typing import Optional
from engine.systems.monster_instance import MonsterInstance
from engine.scenes.battle_scene import BattleScene
import threading
from engine.scenes.battle_scene import BattleScene
```

**Klassen:**
- `FieldEncounterSystem` (Zeile 11)
  - Verwaltet das Encounter-System in der Field-Scene.
  - **Methoden:** `__init__()`, `check_encounter()`, `_get_tile_type()`, `execute_encounter_check()`, `start_wild_battle()`, ... (+8 weitere)

#### `interaction.py` (314 Zeilen)

**Beschreibung:** Interaktions-System für FieldScene
Kümmert sich um alle Spieler-Interaktionen mit NPCs und Objekten

**Imports:**
```python
from typing import Optional, Tuple, List
from engine.ui.dialogue import DialogueBox, DialoguePage, DialogueChoice
from engine.core.resources import resources
from engine.world.tiles import world_to_tile
from engine.world.entity import Direction
from engine.world.map_loader import Trigger
from engine.world.npc import NPC
from engine.scenes.starter_scene import StarterScene
```

**Klassen:**
- `FieldInteractionSystem` (Zeile 14)
  - Verwaltet alle Interaktionen in der Field-Scene.
  - **Methoden:** `__init__()`, `update()`, `handle_interaction()`, `_check_npc_interaction()`, `_check_trigger_interaction()`, ... (+15 weitere)

#### `map_system.py` (393 Zeilen)

**Beschreibung:** Vereinheitlichtes Map-Loading System für Untold Story
Flint Hammerhead räumt das Chaos auf!

Dieses Modul kümmert sich um ALLES was mit Map-Loading zu tun hat.
Keine doppelten Methoden mehr, nur noch EINE zentrale Stelle!

**Imports:**
```python
import pygame
import json
import os
from typing import Optional, Dict, Any, Tuple, List
from dataclasses import dataclass
from engine.world.tiles import TILE_SIZE, tile_to_world
from engine.world.map_loader import MapLoader, MapData, Warp
from engine.world.area import Area
from engine.world.camera import Camera, CameraConfig
from engine.core.resources import resources
from engine.world.enhanced_map_manager import EnhancedMapManager
from engine.world.npc import NPC
```

**Klassen:**
- `@dataclass MapLoadResult` (Zeile 23)
  - Ergebnis eines Map-Load Vorgangs.
- `UnifiedMapSystem` (Zeile 34)
  - Das EINE Map-System für alles!
Keine Duplikate mehr, keine Verwirrung!.
  - **Methoden:** `__init__()`, `_load_map_config()`, `load_map()`, `_load_map_data()`, `_create_area()`, ... (+8 weitere)

#### `story.py` (294 Zeilen)

**Beschreibung:** Story Event System für FieldScene
Verwaltet alle Story-bezogenen Events und Trigger

**Imports:**
```python
from typing import List
from engine.ui.dialogue import DialoguePage
from engine.systems.monster_instance import MonsterInstance
from engine.world.npc import NPC
from engine.world.tiles import TILE_SIZE
from engine.world.entity import Direction
from engine.scenes.starter_scene import StarterScene
```

**Klassen:**
- `FieldStorySystem` (Zeile 14)
  - Verwaltet Story-Events in der Field-Scene.
  - **Methoden:** `__init__()`, `check_story_events()`, `_check_first_house_leave()`, `_check_museum_entry()`, `_check_timerift_event()`, ... (+11 weitere)

### engine › systems

#### `conditions.py` (580 Zeilen)

**Beschreibung:** Detailed status condition system.
Handles all status effects, their mechanics, and interactions.

**Imports:**
```python
from typing import TYPE_CHECKING, Optional, Dict, List, Tuple, Callable
from dataclasses import dataclass
from enum import Enum, auto
import random
from engine.systems.monster_instance import MonsterInstance
from engine.systems.monsters import MonsterSpecies
from engine.systems.unified_damage_calculator import unified_damage_calculator
```

**Klassen:**
- `ConditionType(Enum)` (Zeile 16)
  - Types of status conditions.
- `@dataclass StatusCondition` (Zeile 25)
  - Definition of a status condition.
- `StatusConditions` (Zeile 54)
  - Registry of all status conditions.
- `ConditionManager` (Zeile 233)
  - Manages status conditions for a monster.
  - **Methoden:** `__init__()`, `can_inflict_primary()`, `inflict_primary()`, `inflict_volatile()`, `cure_primary()`, ... (+9 weitere)

#### `cutscene.py` (424 Zeilen)

**Beschreibung:** Cutscene System für Untold Story
Verwaltet skriptbasierte Ereignisse und Sequenzen

**Imports:**
```python
from typing import List, Dict, Any, Callable, Optional
from dataclasses import dataclass
import pygame
from engine.ui.dialogue import DialoguePage
from engine.systems.world_state import world_state
from engine.systems.world_state import world_state
from engine.systems.world_state import world_state
from engine.systems.world_state import world_state
from engine.systems.world_state import world_state
from engine.systems.world_state import world_state
from engine.core.resources import resources
```

**Klassen:**
- `@dataclass CutsceneAction` (Zeile 15)
  - Eine einzelne Aktion in einer Cutscene.
- `Cutscene` (Zeile 23)
  - Eine skriptbasierte Ereignissequenz.
  - **Methoden:** `__init__()`, `add_action()`, `start()`, `update()`, `_next_action()`, ... (+2 weitere)
- `CutsceneManager` (Zeile 330)
  - Verwaltet alle Cutscenes im Spiel.
  - **Methoden:** `__init__()`, `_register_cutscenes()`, `play()`, `update()`

#### `experience_system.py` (455 Zeilen)

**Beschreibung:** Experience and Level System for Untold Story.
Handles EXP gain, level up, and stat growth.

**Imports:**
```python
import math
import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import random
```

**Klassen:**
- `GrowthCurve(Enum)` (Zeile 15)
  - Different EXP growth curves (DQM style).
- `@dataclass LevelUpResult` (Zeile 26)
  - Result of a level up.
- `ExperienceSystem` (Zeile 35)
  - Manages experience points and leveling for monsters.
  - **Methoden:** `calculate_exp_for_level()`, `calculate_exp_to_next_level()`, `calculate_level_from_exp()`, `calculate_battle_exp()`, `distribute_exp()`, ... (+5 weitere)

#### `field_effects.py` (630 Zeilen)

**Beschreibung:** Field Effects System for Untold Story
Handles weather, terrain, and special battlefield modifiers

**Imports:**
```python
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum, auto
import random
import json
```

**Klassen:**
- `EffectCategory(Enum)` (Zeile 13)
  - Categories of field effects.
- `WeatherType(Enum)` (Zeile 20)
  - Available weather conditions.
- `TerrainType(Enum)` (Zeile 30)
  - Available terrain types.
- `SpecialEffectType(Enum)` (Zeile 39)
  - Special battlefield effects.
- `@dataclass FieldEffect` (Zeile 47)
  - Base class for all field effects.
  - **Methoden:** `is_active()`, `advance_turn()`, `extend_duration()`, `to_dict()`, `from_dict()`
- `@dataclass WeatherEffect(FieldEffect)` (Zeile 93)
  - Weather-based field effect.
  - **Methoden:** `__post_init__()`, `_setup_weather_properties()`, `modify_damage()`, `modify_accuracy()`, `check_immunity()`, ... (+2 weitere)
- `@dataclass TerrainEffect(FieldEffect)` (Zeile 176)
  - Terrain-based field effect.
  - **Methoden:** `__post_init__()`, `_setup_terrain_properties()`, `modify_damage()`, `check_status_immunity()`, `get_hp_regen()`, ... (+2 weitere)
- `@dataclass SpecialEffect(FieldEffect)` (Zeile 247)
  - Special battlefield effect.
  - **Methoden:** `__post_init__()`, `_setup_special_properties()`, `apply_special_effect()`, `_apply_zeitriss_effect()`, `_apply_gravity_effect()`, ... (+2 weitere)
- `FieldEffectManager` (Zeile 336)
  - Manages all active field effects in battle.
  - **Methoden:** `__init__()`, `add_effect()`, `remove_effect()`, `get_effect()`, `get_weather()`, ... (+12 weitere)

**Funktionen:** `create_sunny_weather()`, `create_rain_weather()`, `create_sandstorm_weather()`, `create_grassy_terrain()`, `create_electric_terrain()`, `create_zeitriss_effect()`

#### `items.py` (497 Zeilen)

**Beschreibung:** Comprehensive item system for Untold Story.
Handles healing, status curing, taming, stat boosts, and special effects.

**Imports:**
```python
from typing import TYPE_CHECKING, Optional, Dict, List, Any, Callable, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum, auto
import json
import random
from engine.systems.monster_instance import MonsterInstance
from engine.systems.party import Party
from engine.systems.monsters import MonsterSpecies
from engine.systems.battle.battle_controller import BattleState
import json
import os
```

**Klassen:**
- `ItemCategory(Enum)` (Zeile 19)
  - Item categories for organization.
- `ItemRarity(Enum)` (Zeile 30)
  - Item rarity levels.
- `ItemTarget(Enum)` (Zeile 39)
  - Target types for item use.
- `EffectType(Enum)` (Zeile 50)
  - Types of effects items can have.
- `@dataclass ItemEffect` (Zeile 70)
  - Effect of using an item.
- `@dataclass Item` (Zeile 82)
  - Complete item class with all properties.
- `ItemEffectExecutor` (Zeile 103)
  - Executes item effects on targets.
  - **Methoden:** `__init__()`, `execute_item_effects()`, `_apply_effect()`, `_heal_hp()`, `_heal_status()`, ... (+4 weitere)
- `ItemRegistry` (Zeile 236)
  - Registry for all game items.
  - **Methoden:** `__init__()`, `_register_default_items()`, `register_item()`, `get_item()`, `get_all_items()`, ... (+1 weitere)
- `Inventory` (Zeile 413)
  - Simple inventory system to hold player items.
  - **Methoden:** `__init__()`, `add_item()`, `remove_item()`, `has_item()`, `get_quantity()`, ... (+5 weitere)

#### `items_clean.py` (390 Zeilen)

**Beschreibung:** Comprehensive item system for Untold Story.
Handles healing, status curing, taming, stat boosts, and special effects.

**Imports:**
```python
from typing import TYPE_CHECKING, Optional, Dict, List, Any, Callable, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum, auto
import json
import random
from engine.systems.monster_instance import MonsterInstance
from engine.systems.party import Party
from engine.systems.monsters import MonsterSpecies
from engine.systems.battle.battle_controller import BattleState
```

**Klassen:**
- `ItemCategory(Enum)` (Zeile 19)
  - Item categories for organization.
- `ItemRarity(Enum)` (Zeile 30)
  - Item rarity levels.
- `ItemTarget(Enum)` (Zeile 39)
  - Target types for item use.
- `EffectType(Enum)` (Zeile 50)
  - Types of effects items can have.
- `@dataclass ItemEffect` (Zeile 70)
  - Effect of using an item.
- `@dataclass Item` (Zeile 82)
  - Complete item class with all properties.
- `ItemEffectExecutor` (Zeile 103)
  - Executes item effects on targets.
  - **Methoden:** `__init__()`, `execute_item_effects()`, `_apply_effect()`, `_heal_hp()`, `_heal_status()`, ... (+4 weitere)
- `ItemRegistry` (Zeile 236)
  - Registry for all game items.
  - **Methoden:** `__init__()`, `_register_default_items()`, `register_item()`, `get_item()`, `get_all_items()`
- `Inventory` (Zeile 313)
  - Simple inventory system to hold player items.
  - **Methoden:** `__init__()`, `add_item()`, `remove_item()`, `has_item()`, `get_quantity()`, ... (+4 weitere)

#### `monster_instance.py` (811 Zeilen)

**Beschreibung:** Monster Instance System
Handles individual monster instances with stats, status, and battle mechanics

**Imports:**
```python
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
import random
import logging
from engine.systems.stats import BaseStats, StatCalculator, Experience, GrowthCurve, StatStages
from engine.systems.moves import Move, move_registry
from engine.core.resources import resources
from engine.systems.experience_system import ExperienceSystem, LevelUpResult
from engine.systems.talent_system import TalentInstance, TalentDatabase, get_talent_database
from engine.systems.stats import StatCalculator
from engine.systems.moves import move_registry
from engine.systems.moves import Move, MoveCategory, MoveTarget, MoveEffect, EffectKind
from engine.systems.moves import Move, MoveCategory, MoveTarget, MoveEffect, EffectKind
```

**Klassen:**
- `StatusCondition(Enum)` (Zeile 20)
  - Status conditions that can affect monsters.
  - **Methoden:** `from_string()`
- `MonsterRank(Enum)` (Zeile 42)
  - Monster Rank für Balance/Tiers.
  - **Methoden:** `__lt__()`, `__le__()`, `__gt__()`, `__ge__()`
- `@dataclass MonsterSpecies` (Zeile 71)
  - Defines a monster species with base stats and characteristics.
  - **Methoden:** `__post_init__()`, `create_instance()`, `from_dict()`
- `MonsterInstance` (Zeile 181)
  - Monster instance for battle system.
  - **Methoden:** `__init__()`, `_generate_ivs()`, `_generate_nature()`, `_calculate_stats()`, `_initialize_talents()`, ... (+22 weitere)
  - **Properties:** `types`, `stats`, `species_name`

#### `monsters.py` (388 Zeilen)

**Beschreibung:** Monster Species Database for Untold Story
Loads and manages all monster species data

**Imports:**
```python
from typing import Dict, List, Optional, Any
from engine.systems.monster_instance import MonsterSpecies, MonsterInstance, MonsterRank
from engine.systems.stats import GrowthCurve, BaseStats
from engine.core.resources import resources
import random
```

**Klassen:**
- `MonsterDatabase` (Zeile 13)
  - Central database for all monster species.
  - **Methoden:** `__new__()`, `__init__()`, `_load_species_data()`, `_create_species_from_dict()`, `_create_default_species()`, ... (+13 weitere)

#### `moves.py` (711 Zeilen)

**Beschreibung:** Move System for Untold Story
Handles move data, effects, and execution

**Imports:**
```python
from typing import Dict, List, Optional, Any, Callable, Tuple, Union, TYPE_CHECKING
from enum import Enum
from dataclasses import dataclass
import logging
from engine.core.resources import resources
from engine.systems.monster_instance import MonsterInstance
from engine.systems.types import TypeChart
import random
import random
from engine.systems.unified_damage_calculator import unified_damage_calculator
from engine.core.resources import resources
```

**Klassen:**
- `MoveCategory(Enum)` (Zeile 19)
  - Categories of moves.
  - **Methoden:** `from_string()`
- `MoveTarget(Enum)` (Zeile 36)
  - Targeting options for moves.
  - **Methoden:** `from_string()`
- `EffectKind(Enum)` (Zeile 57)
  - Types of move effects.
  - **Methoden:** `from_string()`
- `@dataclass MoveEffect` (Zeile 84)
  - Single effect of a move.
  - **Methoden:** `__post_init__()`, `from_dict()`, `is_valid()`
- `@dataclass Move` (Zeile 166)
  - Complete move data.
  - **Methoden:** `__post_init__()`, `from_dict()`, `can_use()`, `is_disabled()`, `use()`, ... (+3 weitere)
- `MoveExecutor` (Zeile 378)
  - Executes moves in battle.
  - **Methoden:** `execute_move()`, `_check_accuracy()`, `_execute_effect()`, `_calculate_damage()`, `_calculate_healing()`
- `MoveRegistry` (Zeile 515)
  - Registry for all available moves.
  - **Methoden:** `__init__()`, `_load_moves()`, `_create_move_from_dict()`, `get_move()`, `register_move()`, ... (+3 weitere)

#### `party.py` (658 Zeilen)

**Beschreibung:** Party management system for monster teams.
Handles active party of 6 and storage boxes.

**Imports:**
```python
from typing import TYPE_CHECKING, List, Optional, Dict, Tuple
from dataclasses import dataclass, field
import json
from engine.systems.monster_instance import MonsterInstance
from engine.systems.monsters import MonsterSpecies
from engine.systems.monster_instance import MonsterInstance
from engine.systems.monster_instance import MonsterInstance
```

**Klassen:**
- `@dataclass Party` (Zeile 16)
  - Active party of up to 6 monsters.
  - **Methoden:** `__init__()`, `add_monster()`, `remove_monster()`, `swap_positions()`, `get_active()`, ... (+14 weitere)
- `@dataclass StorageBox` (Zeile 225)
  - Storage box for extra monsters.
  - **Methoden:** `__init__()`, `add_monster()`, `remove_monster()`, `get_monster()`, `get_all_monsters()`, ... (+9 weitere)
- `StorageSystem` (Zeile 353)
  - Manages all storage boxes.
  - **Methoden:** `__init__()`, `add_box()`, `get_box()`, `get_current_box()`, `set_current_box()`, ... (+8 weitere)
- `PartyManager` (Zeile 538)
  - Manages party and storage together.
  - **Methoden:** `__init__()`, `add_to_party()`, `add_to_box()`, `deposit_from_party()`, `withdraw_to_party()`, ... (+3 weitere)

#### `quests.py` (579 Zeilen)

**Beschreibung:** Quest system for tracking objectives, side quests, and rewards.

**Imports:**
```python
from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass, field
from enum import Enum, auto
import json
```

**Klassen:**
- `QuestType(Enum)` (Zeile 11)
  - Types of quests.
- `QuestStatus(Enum)` (Zeile 20)
  - Status of a quest.
- `@dataclass QuestObjective` (Zeile 30)
  - A single quest objective.
  - **Methoden:** `is_complete()`, `update()`, `get_progress_text()`
- `@dataclass QuestReward` (Zeile 62)
  - Reward for completing a quest.
- `@dataclass Quest` (Zeile 73)
  - A quest definition.
  - **Methoden:** `is_available()`, `is_active()`, `is_complete()`, `get_active_objectives()`, `get_completion_percentage()`
- `QuestManager` (Zeile 120)
  - Manages all quests in the game.
  - **Methoden:** `__init__()`, `_load_quests()`, `add_quest()`, `get_quest()`, `start_quest()`, ... (+16 weitere)

#### `save.py` (648 Zeilen)

**Beschreibung:** Save/Load system using JSON and ZIP compression.
Includes checksum validation for save integrity.

**Imports:**
```python
import json
import zipfile
import hashlib
import os
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import shutil
import os
import shutil
import shutil
import shutil
from engine.systems.party import PartyManager
from engine.systems.story import StoryManager
from engine.systems.quests import QuestManager
from engine.systems.items_clean import Inventory
from engine.systems.monsters import MonsterSpecies
from engine.systems.party import PartyManager
from engine.systems.story import StoryManager
from engine.systems.quests import QuestManager
from engine.systems.items_clean import Inventory
from engine.systems.monsters import MonsterSpecies
```

**Klassen:**
- `@dataclass SaveMetadata` (Zeile 18)
  - Metadata for a save file.
  - **Methoden:** `to_dict()`, `from_dict()`
- `SaveSystem` (Zeile 63)
  - Handles saving and loading game data.
  - **Methoden:** `__init__()`, `save_game()`, `_validate_game_data()`, `load_game()`, `_try_load_save()`, ... (+12 weitere)
- `GameStateSerializer` (Zeile 539)
  - Serializes and deserializes complete game state.
  - **Methoden:** `serialize()`, `deserialize()`

#### `settings.py` (381 Zeilen)

**Beschreibung:** Settings System für Untold Story
Lädt und speichert Einstellungen aus/in settings.toml

**Imports:**
```python
import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import toml
import shutil
from engine.audio.audio_manager import AudioChannel
```

**Konstanten:** TOML_AVAILABLE, TOML_AVAILABLE

**Klassen:**
- `TextSpeed(Enum)` (Zeile 21)
  - Text speed options.
- `@dataclass AudioSettings` (Zeile 29)
  - Audio configuration.
- `@dataclass DisplaySettings` (Zeile 43)
  - Display configuration.
  - **Properties:** `window_width`, `window_height`
- `@dataclass GraphicsSettings` (Zeile 62)
  - Graphics configuration.
- `@dataclass ControlsSettings` (Zeile 74)
  - Controls configuration.
- `@dataclass GameplaySettings` (Zeile 88)
  - Gameplay configuration.
- `SettingsManager` (Zeile 102)
  - Zentrale Settings-Verwaltung.
  - **Methoden:** `__init__()`, `load_settings()`, `save_settings()`, `toggle_music()`, `toggle_sound()`, ... (+7 weitere)

#### `stats.py` (484 Zeilen)

**Beschreibung:** Stats System for Untold Story
Handles base stats, stat stages, level progression, and experience

**Imports:**
```python
from typing import Dict, Tuple, Optional
from enum import Enum
from dataclasses import dataclass
import math
import logging
```

**Klassen:**
- `Stat(Enum)` (Zeile 12)
  - Core stats for monsters.
- `GrowthCurve(Enum)` (Zeile 24)
  - Experience growth curves for leveling.
- `@dataclass BaseStats` (Zeile 33)
  - Base stat values for a monster species.
  - **Methoden:** `to_dict()`, `get()`, `from_dict()`
- `StatStages` (Zeile 78)
  - Manages stat stage modifiers in battle.
  - **Methoden:** `__init__()`, `get_stage()`, `modify_stage()`, `get_multiplier()`, `reset()`, ... (+1 weitere)
- `@dataclass Experience` (Zeile 186)
  - Experience and leveling system.
  - **Methoden:** `__post_init__()`, `set_level()`, `add_exp()`, `get_exp_for_level()`, `get_level_for_exp()`, ... (+2 weitere)
- `StatCalculator` (Zeile 318)
  - Calculates actual stats from base stats, level, and IVs.
  - **Methoden:** `calculate_hp()`, `calculate_stat()`, `calculate_all_stats()`
- `DamageCalculator` (Zeile 429)
  - Handles damage calculation for battles.
  - **Methoden:** `calculate_damage()`

#### `story.py` (879 Zeilen)

**Beschreibung:** Story system for managing plot progression, flags, and cutscenes.

**Imports:**
```python
from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass, field
from enum import Enum, auto
import json
from engine.systems.monster_instance import MonsterInstance
from engine.systems.monsters import MonsterDatabase
from engine.scenes.battle_scene import BattleScene
from engine.ui.dialogue import DialogueChoice
```

**Klassen:**
- `StoryPhase(Enum)` (Zeile 11)
  - Main story phases.
- `@dataclass StoryFlag` (Zeile 22)
  - A single story flag.
  - **Methoden:** `set()`, `get()`, `toggle()`
- `@dataclass CutsceneScript` (Zeile 45)
  - Script for a cutscene.
- `StoryManager` (Zeile 57)
  - Manages story progression and flags.
  - **Methoden:** `__init__()`, `reset()`, `_init_core_flags()`, `_init_scripts()`, `add_flag()`, ... (+14 weitere)
- `DialogueManager` (Zeile 483)
  - Manages NPC dialogues based on story progression.
  - **Methoden:** `__init__()`, `_load_dialogues()`, `get_dialogue()`, `add_dialogue()`
- `CutscenePlayer` (Zeile 623)
  - Plays cutscene scripts.
  - **Methoden:** `__init__()`, `start_cutscene()`, `update()`, `_execute_command()`, `dialogue_complete()`, ... (+4 weitere)

#### `synthesis.py` (510 Zeilen)

**Beschreibung:** Monster synthesis/fusion system.
Combines two parent monsters to create a new offspring with inherited traits.

**Imports:**
```python
from typing import TYPE_CHECKING, Optional, List, Tuple, Dict, Set
from dataclasses import dataclass
import random
import math
from engine.systems.monster_instance import MonsterInstance
from engine.systems.monsters import MonsterSpecies
from engine.systems.moves import Move
```

**Klassen:**
- `@dataclass SynthesisResult` (Zeile 18)
  - Result of a synthesis attempt.
- `SynthesisRules` (Zeile 30)
  - Rules and formulas for monster synthesis.
  - **Methoden:** `can_synthesize()`
- `SynthesisCalculator` (Zeile 102)
  - Calculates synthesis results.
  - **Methoden:** `__init__()`, `synthesize()`, `_check_special_recipe()`, `_calculate_offspring_species()`, `_calculate_plus_value()`, ... (+5 weitere)
- `SynthesisPreview` (Zeile 391)
  - Preview synthesis results without consuming monsters.
  - **Methoden:** `preview()`
- `TraitEffects` (Zeile 439)
  - Effects of inherited traits.
  - **Methoden:** `apply_trait_modifiers()`

#### `talent_system.py` (712 Zeilen)

**Beschreibung:** 🎯 DQM Talent System - Dragon Quest Monsters Authentic Talent System
Implementiert das authentische DQM Talent-System für Move-Verfügbarkeit

**Imports:**
```python
from typing import Dict, List, Optional, Any, Tuple, Set
from enum import Enum, auto
from dataclasses import dataclass, field
import json
import logging
from pathlib import Path
import random
```

**Klassen:**
- `TalentCategory(Enum)` (Zeile 15)
  - Talent-Kategorien basierend auf DQM.
- `TalentTier(Enum)` (Zeile 25)
  - Talent-Stufen (wie in DQM).
- `@dataclass TalentMove` (Zeile 34)
  - Einzelner Move innerhalb eines Talents.
- `@dataclass Talent` (Zeile 43)
  - Einzelnes Talent (z.
  - **Methoden:** `get_moves_for_tier()`, `can_upgrade_to_tier()`
- `@dataclass TalentInstance` (Zeile 74)
  - Individuelle Talent-Instanz eines Monsters.
  - **Methoden:** `get_experience_to_next_tier()`, `add_experience()`
- `TalentDatabase` (Zeile 112)
  - Zentrale Datenbank für alle DQM Talents
Basiert auf authentischen Dragon Quest Monsters Talent-System.
  - **Methoden:** `__init__()`, `_initialize_default_talents()`, `_load_from_json()`, `_create_talent_from_dict()`, `get_talent()`, ... (+7 weitere)

**Funktionen:** `get_talent_database()`

#### `taming.py` (378 Zeilen)

**Beschreibung:** Taming system for Untold Story.
Handles the capture/recruitment of wild monsters with DQM-style mechanics.

**Imports:**
```python
import random
from typing import Optional, List, Tuple, Dict, Any, TYPE_CHECKING
from dataclasses import dataclass
from enum import Enum
from engine.systems.monster_instance import MonsterInstance
from engine.systems.monsters import MonsterSpecies
```

**Klassen:**
- `TameResult(Enum)` (Zeile 17)
  - Possible outcomes of a taming attempt.
- `@dataclass TameModifier` (Zeile 26)
  - Modifier affecting tame chance.
- `TamingTips` (Zeile 339)
  - Helper class for taming tips and strategies.
  - **Methoden:** `get_tips_for_monster()`, `get_general_tips()`

**Funktionen:** `calculate_tame_chance()`, `calculate_offensive_pressure()`, `attempt_tame()`, `get_tame_modifiers()`, `calculate_display_chance()`

#### `types.py` (651 Zeilen)

**Beschreibung:** Type System for Untold Story RPG
High-performance type effectiveness calculations using NumPy
OPTIMIERT: NumPy-Integration und Matrix-Caching

**Imports:**
```python
import json
import time
import warnings
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from enum import IntEnum, Enum
from dataclasses import dataclass
from functools import lru_cache
import random
import numpy as np
import logging
```

**Konstanten:** NUMPY_AVAILABLE, NUMPY_AVAILABLE

**Klassen:**
- `TypeAttribute(IntEnum)` (Zeile 28)
  - Special attributes that types can have.
- `BattleCondition(Enum)` (Zeile 35)
  - Special battle conditions that modify type effectiveness.
- `@dataclass TypeData` (Zeile 43)
  - Container for type information.
  - **Methoden:** `has_attribute()`
- `@dataclass TypeRelation` (Zeile 56)
  - Represents a relationship between two types.
  - **Methoden:** `inverse()`
- `TypeChart` (Zeile 72)
  - High-performance type effectiveness chart using NumPy.
  - **Methoden:** `__new__()`, `__init__()`, `_load_type_data()`, `_use_default_data()`, `_build_matrix()`, ... (+8 weitere)
- `TypeSystemAPI` (Zeile 418)
  - High-level API for type system interactions.
  - **Methoden:** `__init__()`, `set_battle_condition()`, `check_type_effectiveness()`, `analyze_team_composition()`, `_calculate_team_synergy()`, ... (+1 weitere)

#### `unified_damage_calculator.py` (1135 Zeilen)

**Beschreibung:** Unified Damage Calculator for Untold Story
Konsolidiert alle Damage-Calculator-Implementierungen in ein einheitliches System
SINGLE SOURCE OF TRUTH für alle Damage-Berechnungen

**Imports:**
```python
from typing import TYPE_CHECKING, Optional, Dict, List, Any, Union
from dataclasses import dataclass
import logging
import time
import random
import math
from engine.systems.monster_instance import MonsterInstance
from engine.systems.moves import Move
from engine.systems.types import TypeChart
from engine.systems.battle.dqm_formulas import DQMCalculator
import random
from engine.systems.types import TypeChart
```

**Klassen:**
- `@dataclass DamageResult` (Zeile 22)
  - Result of damage calculation.
- `@dataclass MultiHitResult(DamageResult)` (Zeile 34)
  - Result for multi-hit moves.
- `CriticalTier` (Zeile 39)
- `DamageType` (Zeile 45)
- `UnifiedDamageCalculator` (Zeile 54)
  - Einheitlicher Damage-Calculator der alle bisherigen Implementierungen konsolidiert.
  - **Methoden:** `__new__()`, `__init__()`, `_create_fallback_pipeline()`, `calculate_damage()`, `calculate_dqm_damage()`, ... (+28 weitere)
  - **Properties:** `pipeline`, `dqm_calculator`
- `FallbackPipeline` (Zeile 96)
  - **Methoden:** `__init__()`, `add_stage()`, `process()`, `calculate_damage()`
- `DQMDamageResult` (Zeile 921)
  - DEPRECATED: Legacy DQMDamageResult für Backward Compatibility.
  - **Methoden:** `__init__()`, `__getitem__()`, `get()`, `get_message()`
  - **Properties:** `final_damage`
- `DQMCalculator` (Zeile 966)
  - DEPRECATED: Legacy DQMCalculator für Backward Compatibility.
  - **Methoden:** `__init__()`, `calculate_damage()`, `calculate_turn_order()`, `calculate_escape_chance()`, `calculate_exp_reward()`, ... (+3 weitere)
- `MockMove` (Zeile 991)
  - **Methoden:** `__init__()`
- `MockMonster` (Zeile 997)
  - **Methoden:** `__init__()`
- `DQMSkillCalculator` (Zeile 1065)
  - DEPRECATED: Legacy DQMSkillCalculator für Backward Compatibility.
  - **Methoden:** `calculate_heal()`, `calculate_buff_duration()`
- `DQMDamageStage` (Zeile 1082)
  - DEPRECATED: Legacy DQMDamageStage für Backward Compatibility.
  - **Methoden:** `__init__()`, `process()`

**Funktionen:** `calculate_damage()`, `calculate_recoil()`, `calculate_drain()`, `calculate_escape_chance()`, `calculate_accuracy()`

#### `weather.py` (363 Zeilen)

**Beschreibung:** Weather System for Untold Story
Handles weather transitions, animations, and ability interactions

**Imports:**
```python
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum, auto
import random
import json
from field_effects import WeatherEffect, WeatherType, FieldEffectManager
from engine.systems.unified_damage_calculator import unified_damage_calculator
```

**Klassen:**
- `WeatherTransition(Enum)` (Zeile 15)
  - Types of weather transitions.
- `@dataclass WeatherAnimation` (Zeile 24)
  - Weather animation configuration.
- `WeatherSystem` (Zeile 34)
  - Manages weather mechanics and transitions.
  - **Methoden:** `__init__()`, `_setup_default_animations()`, `_setup_weather_setters()`, `get_weather_animation()`, `can_set_weather()`, ... (+18 weitere)

**Funktionen:** `create_weather_from_move()`, `create_weather_from_ability()`

#### `world_state.py` (175 Zeilen)

**Beschreibung:** World State Management System for Untold Story
Tracks persistent world states like doors, switches, items collected, etc.

**Imports:**
```python
from typing import Dict, Set, Any, Optional
from dataclasses import dataclass, field
import json
import os
```

**Klassen:**
- `@dataclass MapObjectState` (Zeile 13)
  - Represents the state of an interactive map object.
- `WorldState` (Zeile 21)
  - Manages persistent world state across game sessions.
  - **Methoden:** `__init__()`, `set_object_state()`, `get_object_state()`, `is_door_open()`, `set_door_state()`, ... (+15 weitere)

### engine › systems › battle

#### `battle_actions.py` (843 Zeilen)

**Beschreibung:** Battle Actions Module
Handles execution of all battle actions

**Imports:**
```python
import logging
import random
from typing import Dict, Any, Optional, List, TYPE_CHECKING
from engine.systems.monster_instance import MonsterInstance, StatusCondition
from engine.systems.battle.turn_logic_clean import BattleAction, ActionType
from engine.systems.battle.meat_system import MeatSystem, MeatType
from engine.systems.battle.battle_effects import ItemEffectHandler
from engine.systems.battle.skills_dqm_integrated import SkillDatabase, SkillType, SkillElement, SkillTarget
from engine.systems.battle.battle_controller import BattleState
from engine.systems.unified_damage_calculator import unified_damage_calculator
from engine.systems.unified_damage_calculator import unified_damage_calculator
```

**Klassen:**
- `SkillType` (Zeile 25)
  - Fallback SkillType enum.
- `SkillElement` (Zeile 34)
  - Fallback SkillElement enum.
- `SkillTarget` (Zeile 47)
  - Fallback SkillTarget enum.
- `BattleActionExecutor` (Zeile 67)
  - Executes battle actions.
  - **Methoden:** `__init__()`, `execute_action()`, `_execute_attack()`, `_execute_tame()`, `_execute_use_meat()`, ... (+14 weitere)

**Funktionen:** `get_skill_database()`, `get_skill_database()`

#### `battle_ai.py` (453 Zeilen)

**Beschreibung:** AI system for enemy battle decisions.
Implements heuristic-based decision making with difficulty levels.

**Imports:**
```python
from typing import TYPE_CHECKING, List, Optional, Dict, Tuple
from dataclasses import dataclass
from enum import Enum, auto
import random
from engine.systems.monster_instance import MonsterInstance
from engine.systems.moves import Move
from engine.systems.battle.battle_controller import BattleState
from engine.systems.battle.turn_logic_clean import BattleAction
from engine.systems.battle.turn_logic_clean import BattleAction, ActionType
from engine.systems.battle.turn_logic_clean import BattleAction, ActionType
```

**Klassen:**
- `AILevel(Enum)` (Zeile 18)
  - AI difficulty levels.
- `@dataclass MoveScore` (Zeile 28)
  - Score for a potential move choice.
  - **Methoden:** `__repr__()`
- `BattleAI` (Zeile 39)
  - AI controller for enemy monsters in battle.
  - **Methoden:** `__init__()`, `choose_action()`, `decide_action()`, `_random_action()`, `_score_move()`, ... (+3 weitere)

#### `battle_controller.py` (1138 Zeilen)

**Beschreibung:** Battle Controller Module
Main coordinator for battle system, delegates to specialized modules

**Imports:**
```python
import logging
import random
from typing import List, Optional, Dict, Any, TYPE_CHECKING, Callable
from engine.systems.monster_instance import MonsterInstance, StatusCondition
from engine.systems.battle.battle_enums import BattleType, BattlePhase, AIPersonality
from engine.systems.battle.battle_validation import BattleValidator
from engine.systems.battle.turn_logic_clean import BattleAction, ActionType, TurnOrder
from engine.systems.battle.battle_events import EventType, BattleEvent, BattleEventGenerator
from engine.systems.battle.meat_system import MeatSystem, MeatType
from engine.systems.unified_damage_calculator import UnifiedDamageCalculator
from engine.systems.battle.battle_actions import BattleActionExecutor
from engine.systems.battle.battle_ai import BattleAI
from engine.systems.battle.battle_actions import BattleActionExecutor
from engine.systems.battle.battle_ai import BattleAI
from engine.systems.unified_damage_calculator import unified_damage_calculator
from engine.systems.unified_damage_calculator import unified_damage_calculator
from engine.systems.battle.battle_enums import BattleResult
from engine.systems.battle.battle_enums import BattleResult
from engine.systems.battle.battle_enums import BattleResult
from engine.systems.battle.battle_enums import BattleResult
import random
from engine.systems.battle.battle_enums import BattleResult
import random
```

**Klassen:**
- `BattleState` (Zeile 27)
  - Complete battle state management system.
  - **Methoden:** `__init__()`, `_initialize_active_monsters()`, `validate_battle_state()`, `has_able_monsters()`, `is_valid()`, ... (+11 weitere)
  - **Properties:** `action_executor`, `battle_ai`
- `BattleController` (Zeile 590)
  - Main battle controller class.
  - **Methoden:** `__init__()`, `get_available_moves()`, `get_available_switches()`, `get_pending_events()`, `process_event()`, ... (+17 weitere)

#### `battle_effects.py` (664 Zeilen)

**Beschreibung:** Effect executor for battle system.
Handles all move effects, status conditions, stat changes, and item effects.

**Imports:**
```python
from typing import TYPE_CHECKING, Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum, auto
import random
import logging
from engine.systems.monster_instance import MonsterInstance
from engine.systems.battle.battle_controller import BattleState
from engine.systems.items import Item, ItemEffect
```

**Klassen:**
- `EffectType(Enum)` (Zeile 20)
  - Types of effects that can occur in battle.
- `@dataclass EffectResult` (Zeile 45)
  - Result of applying an effect.
- `ItemEffectHandler` (Zeile 53)
  - Handles item effects in battle context.
  - **Methoden:** `__init__()`, `execute_item_effect()`, `_apply_item_effect()`, `_heal_hp_effect()`, `_heal_status_effect()`, ... (+6 weitere)
- `StatusEffects` (Zeile 276)
  - Handles status condition effects.
  - **Methoden:** `can_apply_status()`, `apply_status()`, `process_status_damage()`
- `StatChangeEffects` (Zeile 382)
  - Handles stat stage changes.
  - **Methoden:** `change_stat()`
- `EffectExecutor` (Zeile 448)
  - Main effect executor for battle.
  - **Methoden:** `__init__()`, `execute_effect()`, `execute_item_effects()`, `execute_move_effects()`, `clear_turn_flags()`, ... (+1 weitere)

#### `battle_enums.py` (67 Zeilen)

**Beschreibung:** Battle Enums and Constants
Contains all battle-related enumerations and constant values

**Imports:**
```python
from enum import Enum
```

**Klassen:**
- `BattleType(Enum)` (Zeile 9)
  - Types of battles.
- `BattlePhase(Enum)` (Zeile 21)
  - Phases of battle.
- `BattleCommand(Enum)` (Zeile 36)
  - DQM-style battle commands.
- `AIPersonality(Enum)` (Zeile 49)
  - DQM AI personality types.
- `BattleResult(Enum)` (Zeile 59)
  - Possible battle outcomes - Unified definition.

#### `battle_events.py` (637 Zeilen)

**Beschreibung:** Battle Event System - RESTORED FROM ARCHIVE
Generator-based event system for clean battle flow and UI updates
Based on MRPG's yield-based battle system approach

**Imports:**
```python
import logging
from typing import Generator, Dict, Any, List, Optional, Tuple, Callable, TYPE_CHECKING
from dataclasses import dataclass, field
from enum import Enum, auto
from collections import deque
import time
from engine.systems.monster_instance import StatusCondition
from engine.systems.unified_damage_calculator import unified_damage_calculator
```

**Klassen:**
- `EventType(Enum)` (Zeile 19)
  - Types of battle events.
- `@dataclass BattleEvent` (Zeile 76)
  - Represents a single battle event.
  - **Methoden:** `__str__()`
- `EventQueue` (Zeile 89)
  - Queue for managing battle events.
  - **Methoden:** `__init__()`, `add()`, `add_priority()`, `get_next()`, `complete_current()`, ... (+5 weitere)
- `BattleEventGenerator` (Zeile 151)
  - Generator-based battle event system.
  - **Methoden:** `__init__()`, `_register_default_handlers()`, `register_handler()`, `unregister_handler()`, `emit()`, ... (+12 weitere)

**Funktionen:** `create_battle_event_system()`, `generate_turn_events()`

#### `battle_system.py` (85 Zeilen)

**Beschreibung:** Battle System Compatibility Layer
Re-exports all battle system components for backwards compatibility

**Imports:**
```python
from engine.systems.battle.battle_enums import BattleType, BattlePhase, BattleCommand, AIPersonality
from engine.systems.battle.battle_validation import BattleValidator
from engine.systems.battle.battle_actions import BattleActionExecutor
from engine.systems.battle.battle_controller import BattleState
```

**Funktionen:** `get_battle_state()`, `create_battle()`, `validate_battle_state()`

#### `battle_validation.py` (236 Zeilen)

**Beschreibung:** Battle Validation Module
Contains all validation logic for battle states and actions

**Imports:**
```python
import logging
from typing import List, Optional
from engine.systems.monster_instance import MonsterInstance
from engine.systems.moves import MoveRegistry
```

**Klassen:**
- `BattleValidator` (Zeile 13)
  - Validates battle states and actions.
  - **Methoden:** `validate_battle_state()`, `_validate_monster_stats()`, `has_able_monsters()`, `is_battle_valid()`, `validate_action()`

#### `dqm_formulas.py` (706 Zeilen)

**Beschreibung:** Dragon Quest Monsters Battle Formulas
Authentic DQM damage calculations and battle mechanics

Based on:
- SlimeBattleSystem (https://github.com/Joshalexjacobs/SlimeBattleSystem)
- DQM series mechanics analysis
- Community reverse-engineering efforts

**Imports:**
```python
import random
import math
from typing import Optional, Tuple, Dict, Any, List
from dataclasses import dataclass
from enum import Enum, auto
import logging
from engine.systems.unified_damage_calculator import unified_damage_calculator
```

**Klassen:**
- `DQMConstants` (Zeile 21)
  - Constants for DQM battle mechanics.
- `DQMElement(Enum)` (Zeile 54)
  - DQM-style element types.
- `@dataclass DQMDamageResult` (Zeile 68)
  - Result of DQM damage calculation.
  - **Methoden:** `__getitem__()`, `get()`, `__post_init__()`, `get_message()`
  - **Properties:** `final_damage`
- `DQMCalculator` (Zeile 116)
  - Authentic Dragon Quest Monsters battle calculations.
  - **Methoden:** `__init__()`, `calculate_damage()`, `calculate_turn_order()`, `calculate_escape_chance()`, `calculate_exp_reward()`, ... (+6 weitere)
- `DQMSkillCalculator` (Zeile 533)
  - Calculator for DQM-specific skill mechanics.
  - **Methoden:** `calculate_heal()`, `calculate_buff_duration()`
- `DQMDamageStage` (Zeile 590)
  - Pipeline stage for DQM damage calculation.
  - **Methoden:** `__init__()`, `process()`, `_calculate_dqm_damage_fallback()`
- `SimpleResult` (Zeile 688)
  - **Methoden:** `__init__()`

#### `dqm_integration.py` (317 Zeilen)

**Beschreibung:** DQM Integration Module
Integrates Dragon Quest Monsters formulas into the existing battle system

**Imports:**
```python
import logging
from typing import Dict, Any, List, Optional, TYPE_CHECKING
from engine.systems.unified_damage_calculator import UnifiedDamageCalculator, DQMCalculator, DQMSkillCalculator
from engine.systems.unified_damage_calculator import unified_damage_calculator
from engine.systems.unified_damage_calculator import DQMCalculator
from engine.systems.unified_damage_calculator import DQMSkillCalculator
from engine.systems.battle.dqm_formulas import DQMDamageStage
```

**Klassen:**
- `DQMIntegration` (Zeile 21)
  - Integration layer for DQM formulas into the existing battle system.
  - **Methoden:** `__init__()`, `integrate_with_pipeline()`, `rollback_integration()`, `_dqm_base_damage_stage()`, `_metal_body_stage()`, ... (+4 weitere)
  - **Properties:** `unified_calculator`, `dqm_calculator`, `dqm_skill_calc`, `dqm_stage`

**Funktionen:** `get_dqm_integration()`, `enable_dqm_formulas()`, `disable_dqm_formulas()`

#### `meat_system.py` (298 Zeilen)

**Beschreibung:** Meat System for Dragon Quest Monsters-style taming.
Handles meat items and their effects on taming chances.

**Imports:**
```python
import logging
from typing import Dict, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
```

**Klassen:**
- `MeatType(Enum)` (Zeile 14)
  - Different types of meat with their taming bonuses.
  - **Methoden:** `__init__()`
- `@dataclass MeatEffect` (Zeile 28)
  - Active meat effect in battle.
  - **Methoden:** `is_active()`, `get_bonus()`, `consume_turn()`
- `MeatSystem` (Zeile 48)
  - Manages the DQM-style meat system for monster taming.
  - **Methoden:** `__init__()`, `has_meat()`, `get_available_meat()`, `use_meat()`, `get_taming_bonus()`, ... (+8 weitere)

**Funktionen:** `get_meat_system()`

#### `reward_system.py` (477 Zeilen)

**Beschreibung:** Battle Rewards System for Untold Story.
Handles EXP distribution, item drops, and money rewards.

**Imports:**
```python
import random
import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
from engine.systems.experience_system import ExperienceSystem, LevelUpResult
```

**Klassen:**
- `DropRarity(Enum)` (Zeile 17)
  - Item drop rarity tiers.
  - **Methoden:** `__init__()`
- `@dataclass ItemDrop` (Zeile 31)
  - Represents a potential item drop.
- `@dataclass BattleRewards` (Zeile 41)
  - Complete battle rewards package.
- `RewardSystem` (Zeile 51)
  - Manages all battle rewards including EXP, money, and items.
  - **Methoden:** `__init__()`, `initialize_drop_tables()`, `calculate_battle_rewards()`, `_calculate_monster_exp()`, `_calculate_monster_money()`, ... (+6 weitere)

**Funktionen:** `get_reward_system()`

#### `skills_dqm_integrated.py` (322 Zeilen)

**Beschreibung:** 🔮 Dragon Quest Monsters Skill System - INTEGRIERT MIT TALENT-SYSTEM
Verwendet das neue Talent-System für DQM-authentische Skills

**Imports:**
```python
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum, auto
from dataclasses import dataclass, field
import json
import logging
from engine.systems.talent_system import get_talent_database, TalentInstance, TalentTier
```

**Klassen:**
- `SkillElement(Enum)` (Zeile 17)
  - Elementar-Typen für Skills - MAPPED ZU TALENT-SYSTEM.
- `SkillType(Enum)` (Zeile 31)
  - Skill-Kategorien.
- `SkillTarget(Enum)` (Zeile 43)
  - Ziel-Typen für Skills.
- `@dataclass SkillTier` (Zeile 55)
  - Repräsentiert eine Stufe in einer Skill-Familie.
- `@dataclass SkillFamily` (Zeile 66)
  - Eine Familie von verwandten Skills (z.
  - **Methoden:** `get_tier()`, `get_by_name()`, `can_upgrade()`
- `DQMSkillDatabase` (Zeile 92)
  - Zentrale Datenbank für alle DQM Skills - INTEGRIERT MIT TALENT-SYSTEM
Verwendet das Talent-System als Basis für DQM-Skills.
  - **Methoden:** `__init__()`, `get_skill_family_from_talent()`, `_get_element_from_talent_id()`, `_get_power_for_move()`, `_get_mp_cost_for_move()`, ... (+10 weitere)

**Funktionen:** `get_skill_database()`

#### `status_effects_dqm.py` (359 Zeilen)

**Beschreibung:** DQM-Specific Status Effects System
Implements all Dragon Quest Monsters status conditions

**Imports:**
```python
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, Dict, Any, List
import random
import logging
```

**Klassen:**
- `DQMStatus(Enum)` (Zeile 14)
  - All DQM status conditions.
- `@dataclass StatusEffect` (Zeile 37)
  - A single status effect with duration.
  - **Methoden:** `tick()`
- `DQMStatusManager` (Zeile 51)
  - Manages all status effects for a monster.
  - **Methoden:** `__init__()`, `apply_status()`, `remove_status()`, `cure_all_status()`, `process_turn_start()`, ... (+11 weitere)

#### `turn_logic_clean.py` (414 Zeilen)

**Beschreibung:** Turn order and priority system for battles.
Handles initiative, speed calculations, and action resolution order.
Simplified version for 1v1 battles only.

**Imports:**
```python
import logging
from typing import List, Optional, TYPE_CHECKING
from dataclasses import dataclass
from enum import Enum, auto
import random
from engine.systems.monster_instance import MonsterInstance
from engine.systems.moves import Move
```

**Klassen:**
- `ActionType(Enum)` (Zeile 20)
  - Types of actions that can be taken in battle.
  - **Methoden:** `from_string()`
- `@dataclass BattleAction` (Zeile 58)
  - Represents a single action in battle.
  - **Methoden:** `__post_init__()`, `is_valid()`, `to_dict()`
  - **Properties:** `priority`, `speed`
- `TurnOrder` (Zeile 195)
  - Manages turn order and action resolution in battle.
  - **Methoden:** `__init__()`, `set_seed()`, `clear()`, `add_action()`, `sort_actions()`, ... (+5 weitere)

**Funktionen:** `create_action_from_dict()`, `validate_action_sequence()`

### engine › systems › battle › core

#### `battle_manager.py` (360 Zeilen)

**Beschreibung:** Simplified Battle Manager for DQM-style battles.
Handles core battle flow with proper HP management and scene transitions.

**Imports:**
```python
import pygame
import random
from typing import Optional, List, Dict, Any
from enum import Enum, auto
from engine.systems.battle.battle_controller import BattlePhase
from engine.systems.battle.battle_enums import BattleResult
from engine.systems.items_clean import ItemEffectExecutor, item_registry
```

**Klassen:**
- `SimpleBattleManager` (Zeile 17)
  - Simplified battle manager that actually works.
  - **Methoden:** `__init__()`, `start_battle()`, `handle_player_attack()`, `execute_enemy_turn()`, `handle_flee()`, ... (+10 weitere)

### engine › ui

#### `accessibility.py` (500 Zeilen)

**Beschreibung:** Accessibility-System für Untold Story
Implementiert Keyboard-Shortcuts, Tooltips und visuelle Hilfen für bessere Benutzerfreundlichkeit

**Imports:**
```python
import pygame
from typing import Dict, List, Tuple, Optional, Callable, Any
from dataclasses import dataclass
from enum import Enum, auto
from engine.core.config import Colors
```

**Klassen:**
- `AccessibilityLevel(Enum)` (Zeile 13)
  - Accessibility-Stufen.
- `VisualAid(Enum)` (Zeile 20)
  - Arten von visuellen Hilfen.
- `@dataclass KeyboardShortcut` (Zeile 30)
  - Ein Keyboard-Shortcut.
- `@dataclass VisualAidConfig` (Zeile 40)
  - Konfiguration für visuelle Hilfen.
- `AccessibilityManager` (Zeile 49)
  - Verwaltet alle Accessibility-Features.
  - **Methoden:** `__init__()`, `_setup_default_shortcuts()`, `_setup_default_visual_aids()`, `add_shortcut()`, `add_visual_aid()`, ... (+16 weitere)
- `VisualAidRenderer` (Zeile 222)
  - Rendert visuelle Hilfen.
  - **Methoden:** `__init__()`, `add_visual_aid()`, `remove_visual_aid()`, `update()`, `draw()`, ... (+5 weitere)
- `AccessibilityUI` (Zeile 367)
  - UI für Accessibility-Einstellungen.
  - **Methoden:** `__init__()`, `_setup_ui()`, `_toggle_tooltips()`, `_toggle_high_contrast()`, `_toggle_large_text()`, ... (+4 weitere)

#### `battle_log.py` (483 Zeilen)

**Beschreibung:** Battle Logging System for Untold Story.
Handles battle message history, categorization, and export functionality.

**Imports:**
```python
import pygame
import json
import time
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from enum import Enum, auto
from pathlib import Path
from engine.core.config import Colors, LOGICAL_WIDTH, LOGICAL_HEIGHT
import random
```

**Klassen:**
- `MessagePriority(Enum)` (Zeile 17)
  - Message priority levels.
- `MessageCategory(Enum)` (Zeile 25)
  - Message categories for organization.
- `@dataclass BattleMessage` (Zeile 39)
  - Individual battle message with metadata.
- `BattleLog` (Zeile 54)
  - Comprehensive battle logging system.
  - **Methoden:** `__init__()`, `_init_message_templates()`, `add_message()`, `add_template_message()`, `add_attack_message()`, ... (+15 weitere)

#### `battle_menu_transitions.py` (249 Zeilen)

**Beschreibung:** Battle Menu Transitions - Phase 2 UI Polish
Provides smooth visual transitions between menu states

**Imports:**
```python
import pygame
import math
from typing import Optional, Tuple
from enum import Enum, auto
import random
```

**Klassen:**
- `TransitionType(Enum)` (Zeile 12)
  - Types of menu transitions.
- `MenuTransitionManager` (Zeile 24)
  - Manages smooth transitions between battle menus.
  - **Methoden:** `__init__()`, `start_transition()`, `update()`, `draw_transition()`, `_ease_out_quad()`
- `MenuEffectManager` (Zeile 136)
  - Manages visual effects for menu interactions.
  - **Methoden:** `__init__()`, `add_selection_sparkle()`, `add_confirmation_flash()`, `update()`, `draw()`, ... (+4 weitere)

**Funktionen:** `create_menu_transition_system()`

#### `battle_rewards_ui.py` (567 Zeilen)

**Beschreibung:** Battle Rewards UI for displaying victory rewards.
Shows EXP gain, level ups, money, and item drops with animations.

**Imports:**
```python
import pygame
import math
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
from engine.core.config import LOGICAL_WIDTH, LOGICAL_HEIGHT, Colors
from engine.ui.battle_ui_utils import fonts, colors, text_utils
```

**Klassen:**
- `RewardUIState(Enum)` (Zeile 16)
  - States for the reward UI flow.
- `@dataclass RewardAnimation` (Zeile 28)
  - Animation data for rewards.
  - **Methoden:** `update()`
- `BattleRewardsUI` (Zeile 51)
  - UI for displaying battle rewards with animations.
  - **Methoden:** `__init__()`, `show_rewards()`, `update()`, `_next_state()`, `_setup_exp_animation()`, ... (+12 weitere)

#### `battle_styles.py` (251 Zeilen)

**Beschreibung:** Battle UI Style Configuration for Untold Story.
CSS-like styling system for battle interface elements.

**Imports:**
```python
from typing import Dict, Tuple, Any
from dataclasses import dataclass
from engine.core.config import Colors
```

**Klassen:**
- `@dataclass BattleStyle` (Zeile 12)
  - Style configuration for battle UI elements.
  - **Methoden:** `__post_init__()`
- `BattleThemes` (Zeile 98)
  - Predefined battle UI themes.
  - **Methoden:** `default()`, `dark()`, `light()`, `retro()`, `modern()`
- `StyleUtils` (Zeile 173)
  - Utility functions for battle UI styling.
  - **Methoden:** `get_hp_color()`, `get_status_color()`, `get_type_color()`, `apply_style_variations()`

**Funktionen:** `set_battle_theme()`, `get_current_style()`, `customize_style()`

#### `battle_ui.py` (1662 Zeilen)

**Beschreibung:** Pixel JRPG Battle UI für Untold Story
DQM × Pokémon Hybrid mit deutschem Ruhrpott-Flair

UI-Hierarchie:
- BattleUI (Container)
  ├── TamingUI (DQM-spezifisches Taming)
  ├── ScoutDisplay (Monster-Informationen)
  ├── BattleRewardsUI (Belohnungen)
  └── BattleUIEnhancements (Verbesserte Menüs)

**Imports:**
```python
import pygame
import math
import random
from dataclasses import dataclass
from typing import Optional, List, Tuple, Dict, Any, TYPE_CHECKING
from enum import Enum, auto
from engine.core.config import LOGICAL_WIDTH, LOGICAL_HEIGHT, Colors, Fonts, UI
from engine.core.resources import resources
from engine.ui.taming_ui import TamingUI, TamingUIState
from engine.ui.scout_display import ScoutDisplay, ScoutDisplayTab
from engine.ui.battle_ui_utils import fonts, types, sprites, colors, text_utils
from engine.systems.items import item_registry
from engine.systems.unified_damage_calculator import UnifiedDamageCalculator
from engine.systems.battle.battle_enums import BattleResult
from engine.systems.battle.battle_enums import BattleResult
import traceback
from engine.systems.items import item_registry, ItemEffectExecutor
import traceback
```

**Konstanten:** TILE_SIZE, UI_SCALE, FONT_SIZE

**Klassen:**
- `@dataclass BattleSprite` (Zeile 40)
  - Container for a battle sprite.
- `@dataclass DamageNumber` (Zeile 50)
  - Floating damage number effect.
- `BattleMenuState(Enum)` (Zeile 60)
  - Battle menu states - DQM style.
- `PixelBattleUI` (Zeile 73)
  - Pixel-perfect Battle UI im klassischen JRPG-Style.
  - **Methoden:** `__init__()`, `_init_fonts()`, `draw()`, `_draw_battlefield()`, `_draw_monsters()`, ... (+43 weitere)
  - **Properties:** `taming_ui`, `scout_display`

#### `battle_ui_enhancements.py` (1057 Zeilen)

**Beschreibung:** Battle UI Extensions for Enhanced Battle System
Erweitert das bestehende Battle UI mit den neuen Features

**Imports:**
```python
from typing import List, Tuple, Optional, Dict
import pygame
from engine.ui.battle_ui_utils import fonts, types, colors, text_utils
import time
import math
import math
from engine.ui.battle_ui import BattleMenuState
from engine.ui.battle_ui import BattleMenuState
```

**Klassen:**
- `SkillMenu` (Zeile 11)
  - Skills-Untermenü für Battle System mit visuellen Highlights.
  - **Methoden:** `__init__()`, `set_skills()`, `draw()`, `_update_animations()`, `_draw_gradient_background()`, ... (+5 weitere)
  - **Properties:** `font`, `detail_font`, `big_font`
- `ItemMenu` (Zeile 271)
  - Items-Menü für Battle System mit Effekt-Anzeige.
  - **Methoden:** `__init__()`, `set_items()`, `draw()`, `_update_animations()`, `_draw_warm_gradient_background()`, ... (+6 weitere)
  - **Properties:** `font`, `detail_font`, `big_font`
- `EnhancedMainBattleMenu` (Zeile 587)
  - Visuell verbessertes Haupt-Battle-Menü.
  - **Methoden:** `__init__()`, `set_battle_type()`, `draw()`, `_update_animations()`, `_draw_elegant_background()`, ... (+5 weitere)
  - **Properties:** `font`, `big_font`
- `SkillMenu` (Zeile 848)
  - **Methoden:** `__init__()`, `set_skills()`, `draw()`, `handle_input()`
- `ItemMenu` (Zeile 976)
  - **Methoden:** `__init__()`, `set_items()`, `draw()`, `handle_input()`

**Funktionen:** `enhance_battle_menu_for_new_system()`, `enhanced_draw()`, `add_skill_menu_to_ui()`, `enhanced_handle_input()`, `enhanced_draw()`, `add_item_menu_to_ui()`, `integrate_enhanced_battle_ui()`

#### `battle_ui_utils.py` (342 Zeilen)

**Beschreibung:** Battle UI Utilities - Zentrale Hilfsfunktionen für alle Battle UI-Komponenten.
Konsolidiert doppelte Funktionalitäten und stellt gemeinsame Services bereit.

**Imports:**
```python
import pygame
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from engine.core.config import Colors
from engine.systems.types import TypeChart
from engine.systems.types import TypeChart
from engine.core.resources import resources
from engine.core.resources import resources
```

**Klassen:**
- `@dataclass TypeInfo` (Zeile 14)
  - Type information with color and effectiveness data.
- `BattleUIFontManager` (Zeile 21)
  - Zentrale Font-Verwaltung für alle Battle UI-Komponenten.
  - **Methoden:** `__new__()`, `get_font()`
  - **Properties:** `tiny`, `small`, `normal`, `large`, `huge`
- `BattleUITypeManager` (Zeile 65)
  - Zentrale Type-Verwaltung für alle Battle UI-Komponenten.
  - **Methoden:** `__new__()`, `__init__()`, `_init_type_colors()`, `get_type_color()`, `get_type_effectiveness()`, ... (+2 weitere)
- `BattleUISpriteManager` (Zeile 165)
  - Zentrale Sprite-Verwaltung für alle Battle UI-Komponenten.
  - **Methoden:** `__new__()`, `get_monster_sprite()`, `_get_monster_sprite_id()`, `_create_fallback_sprite()`
- `BattleUIColorManager` (Zeile 242)
  - Zentrale Color-Verwaltung für alle Battle UI-Komponenten.
  - **Methoden:** `__new__()`, `__init__()`, `_init_colors()`, `get_color()`, `get_hp_color()`
- `BattleUITextUtils` (Zeile 294)
  - Text utilities for Battle UI components.
  - **Methoden:** `wrap_text()`, `draw_text_with_shadow()`

#### `dialogue.py` (547 Zeilen)

**Beschreibung:** Dialogue System for Untold Story
Handles dialogue boxes with typewriter effect, paging, and choices

**Imports:**
```python
import pygame
from typing import List, Optional, Tuple, Callable, Dict, Any
from enum import Enum
from dataclasses import dataclass
from engine.core.resources import resources
```

**Klassen:**
- `DialogueState(Enum)` (Zeile 12)
  - States for dialogue box.
- `@dataclass DialoguePage` (Zeile 22)
  - Single page of dialogue.
- `@dataclass DialogueChoice` (Zeile 33)
  - Choice option in dialogue.
- `DialogueBox` (Zeile 41)
  - Dialogue box UI component with typewriter effect and choices.
  - **Methoden:** `__init__()`, `_load_fonts()`, `show_dialogue()`, `show_text()`, `show_choices()`, ... (+16 weitere)

#### `enhanced_menus.py` (520 Zeilen)

**Beschreibung:** Verbesserte Menü-Struktur für Untold Story
Integriert moderne UI-Patterns und erhöht die Benutzerfreundlichkeit

**Imports:**
```python
import pygame
from typing import TYPE_CHECKING, Optional, List, Dict, Any, Callable
from dataclasses import dataclass
from enum import Enum, auto
from abc import ABC, abstractmethod
from modern_ui_patterns import ModernUIElement, AnimatedButton, TooltipManager, TransitionManager, Animation, AnimationType
from engine.core.config import Colors
from engine.core.game import Game
from engine.systems.monster_instance import MonsterInstance
from engine.systems.items import Item
from engine.systems.quests import Quest
```

**Klassen:**
- `MenuState(Enum)` (Zeile 25)
  - Zustände des Hauptmenüs.
- `MenuTransition(Enum)` (Zeile 35)
  - Übergangstypen zwischen Menüs.
- `@dataclass MenuItem` (Zeile 44)
  - Ein Menü-Eintrag.
- `EnhancedMenuBase(ModernUIElement)` (Zeile 54)
  - Verbesserte Basis-Klasse für alle Menüs.
  - **Methoden:** `__init__()`, `_setup_animations()`, `add_menu_item()`, `handle_event()`, `_handle_keyboard()`, ... (+13 weitere)
- `EnhancedInventoryMenu(EnhancedMenuBase)` (Zeile 320)
  - Verbessertes Inventar-Menü.
  - **Methoden:** `__init__()`, `_setup_menu_items()`, `_refresh_items()`, `_use_item()`, `_equip_item()`, ... (+2 weitere)
- `EnhancedPartyMenu(EnhancedMenuBase)` (Zeile 395)
  - Verbessertes Team-Menü.
  - **Methoden:** `__init__()`, `_setup_menu_items()`, `_show_status()`, `_show_moves()`, `_reorder_team()`, ... (+1 weitere)
- `MenuManager` (Zeile 449)
  - Verwaltet alle Menüs und Übergänge.
  - **Methoden:** `__init__()`, `show_main_menu()`, `show_inventory()`, `show_party()`, `_push_menu()`, ... (+4 weitere)

#### `hud.py` (570 Zeilen)

**Beschreibung:** HUD (Heads-Up Display) overlays for field and battle scenes.

**Imports:**
```python
import pygame
from typing import TYPE_CHECKING, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum, auto
from engine.core.game import Game
from engine.systems.monster_instance import MonsterInstance
```

**Klassen:**
- `NotificationType(Enum)` (Zeile 15)
  - Types of HUD notifications.
- `@dataclass Notification` (Zeile 27)
  - A HUD notification.
- `FieldHUD` (Zeile 39)
  - HUD for the field/overworld.
  - **Methoden:** `__init__()`, `set_location()`, `add_notification()`, `update()`, `draw()`, ... (+5 weitere)
- `BattleHUD` (Zeile 345)
  - HUD for battle scenes.
  - **Methoden:** `__init__()`, `add_damage_number()`, `add_status_message()`, `update()`, `draw()`, ... (+3 weitere)
- `@dataclass DamageNumber` (Zeile 516)
  - Floating damage number display.
  - **Methoden:** `update()`, `draw()`

#### `menus.py` (777 Zeilen)

**Beschreibung:** Menu system for inventory, party management, quests, and more.

**Imports:**
```python
import pygame
from typing import TYPE_CHECKING, Optional, List, Dict, Any, Callable
from dataclasses import dataclass
from enum import Enum, auto
from abc import ABC, abstractmethod
from engine.core.game import Game
from engine.systems.monster_instance import MonsterInstance
from engine.systems.items import Item
from engine.systems.quests import Quest
from engine.systems.save import SaveSystem
from engine.systems.save import GameStateSerializer
```

**Klassen:**
- `MenuBase(ABC)` (Zeile 18)
  - Base class for all menus.
  - **Methoden:** `__init__()`, `handle_event()`, `update()`, `draw()`, `draw_window()`
- `InventoryMenu(MenuBase)` (Zeile 77)
  - Inventory management menu.
  - **Methoden:** `__init__()`, `_refresh_items()`, `handle_event()`, `update()`, `draw()`, ... (+2 weitere)
- `PartyMenu(MenuBase)` (Zeile 228)
  - Party management menu.
  - **Methoden:** `__init__()`, `handle_event()`, `update()`, `draw()`
- `QuestMenu(MenuBase)` (Zeile 406)
  - Quest log menu.
  - **Methoden:** `__init__()`, `_refresh_quests()`, `handle_event()`, `update()`, `draw()`, ... (+3 weitere)
- `SaveMenu(MenuBase)` (Zeile 583)
  - Save game menu.
  - **Methoden:** `__init__()`, `handle_event()`, `_save_to_slot()`, `update()`, `draw()`
- `ConfirmDialog(MenuBase)` (Zeile 696)
  - Confirmation dialog.
  - **Methoden:** `__init__()`, `handle_event()`, `update()`, `draw()`

#### `modern_ui_patterns.py` (303 Zeilen)

**Beschreibung:** Moderne UI-Patterns für Untold Story
Implementiert Animationen, Hover-Effekte und visuelle Feedback-Mechanismen

**Imports:**
```python
import pygame
import math
from typing import Dict, Tuple, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum, auto
from dataclasses import dataclass
from engine.core.config import Colors
```

**Klassen:**
- `AnimationType(Enum)` (Zeile 15)
  - Arten von UI-Animationen.
- `HoverState(Enum)` (Zeile 28)
  - Hover-Zustände für UI-Elemente.
- `@dataclass Animation` (Zeile 37)
  - Animation-Konfiguration.
  - **Methoden:** `update()`, `is_finished()`
- `@dataclass HoverEffect` (Zeile 70)
  - Hover-Effekt-Konfiguration.
- `ModernUIElement` (Zeile 78)
  - Basis-Klasse für moderne UI-Elemente mit Animationen und Hover-Effekten.
  - **Methoden:** `__init__()`, `add_animation()`, `update()`, `handle_hover()`, `get_hover_scale()`, ... (+1 weitere)
- `AnimatedButton(ModernUIElement)` (Zeile 139)
  - Animierter Button mit Hover-Effekten.
  - **Methoden:** `__init__()`, `handle_click()`, `draw()`
- `TooltipManager` (Zeile 214)
  - Verwaltet Tooltips für UI-Elemente.
  - **Methoden:** `__init__()`, `add_tooltip()`, `update()`, `draw()`
- `UITransitionManager` (Zeile 269)
  - Verwaltet Übergänge zwischen UI-Zuständen (umbenannt von TransitionManager).
  - **Methoden:** `__init__()`, `start_fade()`, `update()`, `draw()`

#### `scout_display.py` (772 Zeilen)

**Beschreibung:** Scout Display component for the battle system.
Shows detailed monster analysis in DQM style.

**Imports:**
```python
import pygame
import math
from typing import Optional, Dict, List, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from engine.core.config import LOGICAL_WIDTH, LOGICAL_HEIGHT, Colors
from engine.ui.battle_ui_utils import fonts, types, sprites, colors, text_utils
```

**Klassen:**
- `ScoutDisplayTab(Enum)` (Zeile 16)
  - Tabs for the scout display.
- `@dataclass MonsterAnalysis` (Zeile 26)
  - Complete analysis data for a monster.
- `ScoutDisplay` (Zeile 46)
  - Monster analysis display system.
  - **Methoden:** `__init__()`, `show_monster_analysis()`, `_analyze_monster()`, `_calculate_type_effectiveness()`, `_calculate_taming_difficulty()`, ... (+18 weitere)

#### `taming_ui.py` (485 Zeilen)

**Beschreibung:** Taming UI component for the battle system.
Shows meat selection and taming chance calculation with visual feedback.

**Imports:**
```python
import pygame
import math
from typing import Optional, Dict, List, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from engine.core.config import LOGICAL_WIDTH, LOGICAL_HEIGHT, Colors
from engine.ui.battle_ui_utils import fonts, colors, text_utils
from engine.systems.battle.meat_system import MeatType, MeatSystem
```

**Klassen:**
- `TamingUIState(Enum)` (Zeile 17)
  - States for the taming UI flow.
- `@dataclass TamingAnimation` (Zeile 27)
  - Animation data for taming attempt.
- `TamingUI` (Zeile 37)
  - Complete taming UI system with meat selection and chance display.
  - **Methoden:** `__init__()`, `init_taming()`, `show_meat_selection()`, `show_taming_chance()`, `start_taming_animation()`, ... (+10 weitere)

#### `transitions.py` (381 Zeilen)

**Beschreibung:** Screen Transition Effects for Untold Story
Provides fade, wipe, and other transition effects between scenes

**Imports:**
```python
import pygame
import math
from typing import Optional, Tuple
from enum import Enum
from engine.core.scene_base import TransitionScene, Scene
```

**Klassen:**
- `TransitionType(Enum)` (Zeile 13)
  - Types of transition effects.
- `FadeTransition(TransitionScene)` (Zeile 27)
  - Fade transition between two scenes.
  - **Methoden:** `__init__()`, `draw()`
- `WipeTransition(TransitionScene)` (Zeile 80)
  - Wipe transition that reveals the new scene progressively.
  - **Methoden:** `__init__()`, `draw()`, `_draw_wipe_edge()`
- `RadialTransition(TransitionScene)` (Zeile 167)
  - Radial/iris transition that opens or closes in a circle.
  - **Methoden:** `__init__()`, `draw()`
- `BattleSwirlTransition(TransitionScene)` (Zeile 246)
  - Swirling transition effect commonly used for battle encounters.
  - **Methoden:** `__init__()`, `update()`, `draw()`
- `TransitionManager` (Zeile 328)
  - Factory for creating transitions.
  - **Methoden:** `create_transition()`

### engine › world

#### `area.py` (627 Zeilen)

**Beschreibung:** Area - Repräsentiert eine spielbare Map-Region
Mit verbessertem TMX-Support und korrektem Tile-Rendering
OPTIMIERT: Surface-Caching und reduzierte JSON-Operationen

**Imports:**
```python
import pygame
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from functools import lru_cache
import time
from engine.world.tiles import TILE_SIZE, TileType
from engine.world.map_loader import MapLoader, MapData
from engine.graphics.sprite_manager import SpriteManager
from engine.world.entity import Entity
from engine.world.npc import NPC
from engine.core.resources import resources
from engine.world.tile_manager import TileManager
import traceback
from pathfinding import find_path
from engine.world.tile_manager import TileManager
from engine.world.tile_manager import TileManager
```

**Klassen:**
- `@dataclass AreaConfig` (Zeile 23)
  - Konfiguration für eine Area.
- `Area` (Zeile 31)
  - Eine spielbare Map-Region mit TMX-Support und Performance-Optimierungen.
  - **Methoden:** `__init__()`, `_cleanup_cache()`, `_get_cached_surface()`, `_cache_surface()`, `_get_cached_json()`, ... (+20 weitere)
  - **Properties:** `layers`

#### `camera.py` (329 Zeilen)

**Beschreibung:** Camera System for Untold Story
Handles viewport management, following targets, and smooth camera movement

**Imports:**
```python
import pygame
from typing import Optional, Tuple
from dataclasses import dataclass
from core.config import CAMERA_DEADZONE_WIDTH, CAMERA_DEADZONE_HEIGHT, CAMERA_FOLLOW_SPEED
import random
```

**Klassen:**
- `@dataclass CameraConfig` (Zeile 13)
  - Configuration for camera behavior.
- `Camera` (Zeile 23)
  - 2D camera for following entities and managing the viewport.
  - **Methoden:** `__init__()`, `_update_deadzone()`, `set_position()`, `center_on()`, `set_follow_target()`, ... (+13 weitere)

#### `enhanced_map_manager.py` (709 Zeilen)

**Beschreibung:** Enhanced Map Manager for Untold Story
Orchestrates loading of TMX visual data and JSON interaction data
Provides clean separation of concerns between visuals and game logic

**Imports:**
```python
import pygame
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Optional, Tuple, List, Any
from engine.world.area import Area
from engine.world.map_loader import MapLoader, MapData
from engine.world.interaction_manager import InteractionManager, WarpData
from engine.world.npc_manager import NPCManager
from engine.world.tiles import TILE_SIZE
from engine.ui.dialogue import DialoguePage
from engine.world.map_transition import MapTransition
from engine.systems.items import ItemRegistry
from engine.systems.world_state import world_state
from engine.systems.cutscene import Cutscene
from engine.ui.dialogue import DialoguePage
from engine.scenes.battle_scene import BattleScene
from engine.scenes.starter_scene import StarterScene
```

**Klassen:**
- `EnhancedMapManager` (Zeile 21)
  - Enhanced map management system that properly separates visual (TMX) 
and logic (JSON) data for clean, maintainable map creation.
  - **Methoden:** `__init__()`, `load_map()`, `_load_tmx_visuals()`, `_create_fallback_visuals()`, `_setup_collision()`, ... (+21 weitere)

#### `entity.py` (487 Zeilen)

**Beschreibung:** Base Entity System for Untold Story
Defines the base class for all game entities (player, NPCs, objects)

**Imports:**
```python
import pygame
from typing import Optional, Tuple, Dict, Any, List
from enum import Enum
from dataclasses import dataclass
from engine.world.tiles import TILE_SIZE, world_to_tile, tile_to_world
import os
```

**Klassen:**
- `Direction(Enum)` (Zeile 14)
  - Cardinal directions for entity facing.
  - **Methoden:** `from_vector()`
  - **Properties:** `vector`
- `@dataclass EntitySprite` (Zeile 45)
  - Sprite configuration for an entity.
  - **Methoden:** `__post_init__()`
- `Entity` (Zeile 69)
  - Base class for all world entities.
  - **Methoden:** `__init__()`, `_load_sprite()`, `get_rect()`, `get_center()`, `get_tile_position()`, ... (+14 weitere)

#### `gid_mapper.py` (70 Zeilen)

**Beschreibung:** GID Mapper für TMX-Maps
Mappt Global IDs aus TMX-Dateien auf die richtigen Tiles

**Imports:**
```python
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Tuple
```

**Klassen:**
- `GIDMapper` (Zeile 10)
  - Mappt TMX GIDs auf Tileset-Tiles.
  - **Methoden:** `__init__()`, `load_tmx()`, `_load_tileset_info()`, `get_tileset_and_id()`, `clear_flip_flags()`

#### `interaction_manager.py` (445 Zeilen)

**Beschreibung:** Interaction Manager for Untold Story
Manages all interactive elements loaded from JSON data files
Provides clean separation between visual TMX and game logic

**Imports:**
```python
import json
import pygame
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from engine.world.tiles import TILE_SIZE
```

**Klassen:**
- `@dataclass NPCData` (Zeile 17)
  - Data structure for NPC configuration.
- `@dataclass WarpData` (Zeile 30)
  - Data structure for warp points.
- `@dataclass ObjectData` (Zeile 43)
  - Data structure for interactive objects.
- `@dataclass TriggerData` (Zeile 57)
  - Data structure for event triggers.
- `@dataclass InteractionData` (Zeile 69)
  - Complete interaction data for a map.
- `InteractionManager` (Zeile 78)
  - Manages all interactive elements in the game world.
  - **Methoden:** `__init__()`, `load_interactions()`, `_parse_interaction_data()`, `check_conditions()`, `get_npc_at()`, ... (+7 weitere)

#### `ledge_handler.py` (86 Zeilen)

**Beschreibung:** Ledge Handler für das Grid-basierte Movement System
Behandelt das Springen über Kanten (Ledges)

**Imports:**
```python
from typing import List, Tuple, Optional
from engine.world.movement_states import MovementState
from engine.world.entity import Entity
```

**Klassen:**
- `LedgeHandler` (Zeile 11)
  - Handles ledge jumping mechanics.
  - **Methoden:** `can_jump_ledge()`, `execute_ledge_jump()`

#### `map_loader.py` (397 Zeilen)

**Beschreibung:** Map Loading and Normalization for Untold Story
Handles both simple internal JSON format and Tiled JSON export format

**Imports:**
```python
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from engine.core.resources import resources
from engine.world.tiles import TILE_SIZE, TileType
import xml.etree.ElementTree as ET
```

**Klassen:**
- `@dataclass Warp` (Zeile 16)
  - Represents a warp point to another map.
- `@dataclass Trigger` (Zeile 29)
  - Represents an interactive trigger on the map.
- `@dataclass MapData` (Zeile 38)
  - Normalized map data structure.
- `MapLoader` (Zeile 52)
  - Handles loading and normalization of map data.
  - **Methoden:** `load_map()`, `_load_simple_map()`, `_load_tiled_map()`, `_load_tmx_file()`, `_parse_warps()`, ... (+3 weitere)

#### `map_transition.py` (54 Zeilen)

**Beschreibung:** Map Transition System für smooth Übergänge zwischen Maps
Behandelt das Laden neuer Maps und Positionierung des Spielers

**Imports:**
```python
from typing import Dict, Any, Optional
from engine.world.entity import Direction
```

**Klassen:**
- `MapTransition` (Zeile 10)
  - Handles smooth transitions between maps.
  - **Methoden:** `execute_transition()`

#### `movement_states.py` (17 Zeilen)

**Beschreibung:** Movement States für das Grid-basierte Movement System
Vermeidet zirkuläre Imports zwischen player.py und ledge_handler.py

**Imports:**
```python
from enum import Enum
```

**Klassen:**
- `MovementState(Enum)` (Zeile 9)
  - Bewegungszustände des Spielers.

#### `npc.py` (461 Zeilen)

**Beschreibung:** NPC - Non-Player Character System for Untold Story
Handles NPCs with different movement patterns and behaviors

**Imports:**
```python
import pygame
import random
import time
from typing import Optional, List, Tuple, Dict, Any
from enum import Enum
from dataclasses import dataclass
from engine.world.entity import Entity, Direction
from engine.world.tiles import TILE_SIZE, world_to_tile, tile_to_world
from engine.world.pathfinding_mixin import PathfindingMixin
```

**Klassen:**
- `MovementPattern(Enum)` (Zeile 18)
  - Movement patterns for NPCs.
- `@dataclass NPCConfig` (Zeile 29)
  - Configuration for an NPC.
- `NPC(Entity, PathfindingMixin)` (Zeile 43)
  - Non-Player Character with movement patterns and dialogue.
  - **Methoden:** `__init__()`, `set_collision_layer()`, `set_sprite_manager()`, `set_area()`, `set_player_reference()`, ... (+11 weitere)

#### `npc_improved.py` (662 Zeilen)

**Beschreibung:** Verbessertes NPC-System mit Pathfinding und Bewegungsmustern

**Imports:**
```python
import pygame
import random
from typing import Optional, List, Tuple, Dict
from enum import Enum
from dataclasses import dataclass
from engine.world.entity import Direction
import time
from engine.world.tiles import TILE_SIZE
from engine.world.tile_manager import tile_manager
from engine.world.entity import Entity, EntitySprite, Direction
from engine.world.npc import MovementPattern
from engine.ui.dialogue import DialoguePage
from engine.world.tile_manager import TileManager
```

**Klassen:**
- `@dataclass NPCConfig` (Zeile 22)
  - Konfiguration für einen NPC.
- `ImprovedNPC` (Zeile 35)
  - Verbesserter NPC mit Pathfinding und intelligenten Bewegungsmustern.
  - **Methoden:** `__init__()`, `_load_sprite()`, `update()`, `_update_smooth_movement()`, `_decide_next_move()`, ... (+13 weitere)
- `RivalKlaus(ImprovedNPC)` (Zeile 563)
  - Klaus - der Rivale des Spielers.
  - **Methoden:** `__init__()`, `get_dialogue()`

#### `npc_manager.py` (368 Zeilen)

**Beschreibung:** NPC Manager for Untold Story
Handles spawning, management, and behavior of NPCs from interaction data

**Imports:**
```python
import pygame
import json
import random
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from engine.world.entity import Entity, EntitySprite, Direction
from engine.world.tiles import TILE_SIZE
from engine.ui.dialogue import DialoguePage
```

**Klassen:**
- `ManagedNPC(Entity)` (Zeile 17)
  - An NPC entity managed by the NPC Manager.
  - **Methoden:** `__init__()`, `_load_npc_sprite()`, `set_facing()`, `update()`, `_execute_movement()`, ... (+5 weitere)
- `NPCManager` (Zeile 241)
  - Manages all NPCs in the game world.
  - **Methoden:** `__init__()`, `spawn_npcs()`, `_check_spawn_conditions()`, `clear_npcs()`, `get_npc_by_id()`, ... (+3 weitere)

#### `pathfinding.py` (139 Zeilen)

**Beschreibung:** Grid-based A* pathfinding for 16x16 tile maps.

- Four-directional movement (no diagonals)
- Uses `Area.is_tile_solid(x, y)` to determine walkability

**Imports:**
```python
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple
import heapq
```

**Klassen:**
- `@dataclass(order=False) Node` (Zeile 19)
  - **Properties:** `f_cost`

**Funktionen:** `manhattan()`, `reconstruct_path()`, `in_bounds()`, `get_neighbors()`, `find_path()`

#### `pathfinding_mixin.py` (261 Zeilen)

**Beschreibung:** PathfindingMixin für NPCs - ENDLICH INTELLIGENTE BEWEGUNG!
Flint Hammerhead macht dat hier ordentlich, wa!

**Imports:**
```python
from typing import Optional, List, Tuple
from engine.world.pathfinding import find_path
from engine.world.tiles import world_to_tile, tile_to_world
import random
import time
```

**Klassen:**
- `PathfindingMixin` (Zeile 13)
  - Mixin für NPCs mit intelligenter Wegfindung.
  - **Methoden:** `__init__()`, `find_path_to()`, `follow_path()`, `wander_with_pathfinding()`, `follow_player()`, ... (+1 weitere)

#### `player.py` (682 Zeilen)

**Imports:**
```python
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, List, Tuple, Callable
import pygame
from engine.world.entity import Entity, Direction, EntitySprite
from engine.world.tiles import TILE_SIZE, world_to_tile
from engine.world.movement_states import MovementState
from engine.world.ledge_handler import LedgeHandler
from engine.items.running_shoes import RunningShoes
from engine.graphics.sprite_manager import SpriteManager
from engine.core.game import Game
from engine.graphics.sprite_manager import SpriteManager
```

**Klassen:**
- `Player(Entity)` (Zeile 13)
  - Pokémon-style grid-based Player Controller
- Tile-zu-Tile Bewegung
- Smooth animations zwischen Tiles
- Turn-in-place bei kurzem Tastendruck
- Running mit B-Taste
- Auto-interact beim Laufen gegen NPCs/Objekte.
  - **Methoden:** `__init__()`, `_load_player_sprite()`, `set_collision_map()`, `handle_input()`, `direction_just_pressed()`, ... (+21 weitere)

#### `tile_ids.py` (257 Zeilen)

**Beschreibung:** Tile ID Konstanten für das Untold Story Spiel.
Alle IDs basieren auf der tile_mapping.json und dem manifest.json.

**Konstanten:** GRASS_1, GRASS_2, GRASS_3, GRASS_4, GRASS, TALL_GRASS_1, TALL_GRASS_2, TALL_GRASS, DIRT_1, DIRT_2, PATH_1, PATH_2, PATH, GRAVEL_1, GRAVEL_2, GRAVEL, SAND_1, SAND_2, SNOW, WOOD_FLOOR, STONE_FLOOR, CARPET, BUSH_1, BUSH_2, BUSH, ROCK_1, ROCK_2, ROCK, FLOWER_RED, FLOWER_BLUE, STUMP, LEDGE, CLIFF_FACE, STAIRS_H, STAIRS_V, STAIRS, WATER_1, WATER_2, WATER_EDGE_N, WATER_EDGE_S, WATER_EDGE_W, WATER_EDGE_E, WATER_CORNER_NE, WATER_CORNER_NW, WATER_CORNER_SE, WATER_CORNER_SW, WALL_BRICK, WALL_PLASTER, WALL, ROOF_RED, ROOF_BLUE, ROOF_RIDGE, ROOF, WARP_CARPET, FENCE_H, FENCE_V, WINDOW, DOOR, SIGN, TABLE, CHAIR, BED, BOOKSHELF, TV, POTTED_PLANT, CRATE, BARREL, LAMP_POST, MAILBOX, WELL, GRAVESTONE, BOULDER, TREE_SMALL, PLAYER_DOWN, PLAYER_UP, PLAYER_LEFT, PLAYER_RIGHT, NPC_VILLAGER_M_BASE, NPC_VILLAGER_F_BASE, NPC_GUARD_BASE, NPC_SCIENTIST_BASE, NPC_NURSE_BASE, NPC_MERCHANT_BASE, NPC_FISHER_BASE, NPC_BIKER_BASE, NPC_RANGER_BASE, NPC_MINER_BASE, NPC_MONK_BASE, NPC_KID_BASE, NPC_A_BASE, NPC_B_BASE

**Funktionen:** `get_npc_sprite_id()`, `is_solid_tile()`, `is_transparent_tile()`, `get_tile_category()`

#### `tile_manager.py` (597 Zeilen)

**Beschreibung:** Tile Manager - Zentrales Tile-Management mit TMX-Support und Pathfinding

**Imports:**
```python
import pygame
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
import heapq
import json
from engine.world.tiles import TILE_SIZE
```

**Klassen:**
- `@dataclass TileData` (Zeile 16)
  - Daten für ein einzelnes Tile.
  - **Methoden:** `__post_init__()`
- `TileManager` (Zeile 27)
  - Verwaltet alle Tile-bezogenen Operationen.
  - **Methoden:** `__new__()`, `__init__()`, `get_instance()`, `_load_external_data()`, `load_tmx_map()`, ... (+16 weitere)

#### `tiles.py` (103 Zeilen)

**Imports:**
```python
from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, List
from enum import IntEnum
import pygame
```

**Klassen:**
- `TileType(IntEnum)` (Zeile 12)
  - Common tile type IDs for collision and interaction.
- `@dataclass(frozen=True) Vec2` (Zeile 30)
- `TileLayer(IntEnum)` (Zeile 34)
  - Layer indices for map rendering.

**Funktionen:** `tile_to_world()`, `world_to_tile()`, `rect_from_tile()`, `draw_grid()`, `get_tile_rect()`, `rect_to_tiles()`, `is_tile_solid()`, `is_rect_colliding()`

#### `tmx_init.py` (44 Zeilen)

**Beschreibung:** TMX Initialization Module - Real Implementation

**Imports:**
```python
from engine.graphics.sprite_manager import SpriteManager
from engine.world.enhanced_map_manager import EnhancedMapManager
```

**Funktionen:** `initialize_tmx_support()`
