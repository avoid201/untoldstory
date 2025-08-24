"""
Central configuration and constants for the game.
"""

from enum import Enum, auto
from typing import Dict, Tuple, Any
import os
from pathlib import Path


# Game Info
GAME_TITLE = "Untold Story"
GAME_VERSION = "1.0.0"
GAME_AUTHOR = "Ruhrpott Games"

# Display Settings
LOGICAL_WIDTH = 320
LOGICAL_HEIGHT = 180
WINDOW_SCALE = 4
WINDOW_WIDTH = LOGICAL_WIDTH * WINDOW_SCALE
WINDOW_HEIGHT = LOGICAL_HEIGHT * WINDOW_SCALE
TARGET_FPS = 60
VSYNC = True

# Tile Settings
from engine.world.tiles import TILE_SIZE  # Import from central location
HALF_TILE = TILE_SIZE // 2
PLAYER_COLLISION_SIZE = 14  # Player collision box size within tile (16x16)

# Movement
PLAYER_SPEED = 2.0  # Basis-Geschwindigkeit für 16x16 Tiles
NPC_SPEED = 1.0     # NPC-Geschwindigkeit für 16x16 Tiles
RUN_MULTIPLIER = 1.5
DIAGONAL_FACTOR = 0.707  # For diagonal movement normalization

# Paths
BASE_DIR = Path(__file__).parent.parent.parent
ASSETS_DIR = BASE_DIR / "assets"
DATA_DIR = BASE_DIR / "data"
SAVES_DIR = BASE_DIR / "saves"
LOGS_DIR = BASE_DIR / "logs"

# Asset Paths
GFX_DIR = ASSETS_DIR / "gfx"
SFX_DIR = ASSETS_DIR / "sfx"
BGM_DIR = ASSETS_DIR / "bgm"
FONTS_DIR = ASSETS_DIR / "fonts"

# Data Paths
MAPS_DIR = DATA_DIR / "maps"
DIALOGS_DIR = DATA_DIR / "dialogs"

# Create directories if they don't exist
for directory in [SAVES_DIR, LOGS_DIR, ASSETS_DIR, DATA_DIR, GFX_DIR, SFX_DIR, BGM_DIR, MAPS_DIR, DIALOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Colors (RGB)
class Colors:
    """Common color constants."""
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    YELLOW = (255, 255, 0)
    CYAN = (0, 255, 255)
    MAGENTA = (255, 0, 255)
    
    # UI Colors
    UI_BG = (20, 20, 30)
    UI_BORDER = (100, 100, 120)
    UI_SELECTED = (255, 255, 255)
    UI_UNSELECTED = (150, 150, 150)
    UI_DISABLED = (80, 80, 80)
    
    # HP Bar Colors
    HP_HIGH = (0, 200, 0)
    HP_MED = (200, 200, 0)
    HP_LOW = (200, 0, 0)
    
    # Additional Colors
    LIGHT_GREEN = (150, 255, 150)
    LIGHT_BLUE = (150, 150, 255)
    LIGHT_RED = (255, 150, 150)
    LIGHT_YELLOW = (255, 255, 150)
    LIGHT_CYAN = (150, 255, 255)
    LIGHT_MAGENTA = (255, 150, 255)
    
    # Status Colors
    STATUS_BURN = (200, 50, 0)
    STATUS_FREEZE = (100, 200, 255)
    STATUS_PARALYSIS = (200, 200, 0)
    STATUS_POISON = (150, 0, 200)
    STATUS_SLEEP = (100, 100, 100)
    STATUS_CONFUSION = (200, 100, 200)


# Input Mapping
class InputConfig:
    """Input configuration."""
    # Movement
    MOVE_UP = ['w', 'up']
    MOVE_DOWN = ['s', 'down']
    MOVE_LEFT = ['a', 'left']
    MOVE_RIGHT = ['d', 'right']
    
    # Actions
    CONFIRM = ['e', 'return', 'space']
    CANCEL = ['q', 'escape']
    INTERACT = ['e', 'return', 'space']
    RUN = ['lshift', 'rshift']
    
    # Menu
    PAUSE = ['escape', 'p']
    INVENTORY = ['i']
    PARTY = ['m']
    QUESTS = ['j']
    
    # Debug
    DEBUG_TOGGLE = ['tab']
    GRID_TOGGLE = ['g']
    FPS_TOGGLE = ['f3']
    SCREENSHOT = ['f12']


# Battle Configuration
class BattleConfig:
    """Battle system configuration."""
    # Damage calculation
    BASE_CRIT_RATE = 0.0625  # 1/16
    CRIT_MULTIPLIER = 1.5
    STAB_MULTIPLIER = 1.2
    RANDOM_DAMAGE_MIN = 0.85
    RANDOM_DAMAGE_MAX = 1.0
    
    # Status effect damage
    BURN_DAMAGE_PERCENT = 0.125  # 1/8 max HP
    POISON_DAMAGE_PERCENT = 0.125
    CURSE_DAMAGE_PERCENT = 0.25  # 1/4 max HP
    
    # Stat stages
    MAX_STAT_STAGE = 6
    MIN_STAT_STAGE = -6
    
    # Experience
    BASE_EXP_YIELD = 100
    TRAINER_BONUS = 1.5
    
    # Catch rates
    BASE_CATCH_RATE = 0.3
    STATUS_BONUS = {
        'sleep': 2.5,
        'freeze': 2.3,
        'paralysis': 1.8,
        'confusion': 1.5,
        'burn': 1.3,
        'poison': 1.3
    }


# Monster Configuration
class MonsterConfig:
    """Monster system configuration."""
    # Party
    MAX_PARTY_SIZE = 6
    MAX_MOVES = 4
    
    # Levels
    MIN_LEVEL = 1
    MAX_LEVEL = 100
    
    # IVs (Individual Values)
    MIN_IV = 0
    MAX_IV = 31
    
    # Stat calculation
    HP_BASE = 10
    STAT_BASE = 5
    
    # Evolution
    DEFAULT_EVOLUTION_LEVEL = 16
    
    # Storage
    STORAGE_BOX_SIZE = 30
    INITIAL_BOXES = 4
    MAX_BOXES = 16


# Type Chart
TYPE_CHART: Dict[Tuple[str, str], float] = {
    # Format: (attacking_type, defending_type): multiplier
    # Feuer (Fire)
    ('feuer', 'pflanze'): 2.0,
    ('feuer', 'wasser'): 0.5,
    ('feuer', 'feuer'): 0.5,
    ('feuer', 'erde'): 1.0,
    
    # Wasser (Water)
    ('wasser', 'feuer'): 2.0,
    ('wasser', 'erde'): 2.0,
    ('wasser', 'wasser'): 0.5,
    ('wasser', 'pflanze'): 0.5,
    
    # Erde (Earth)
    ('erde', 'feuer'): 2.0,
    ('erde', 'energie'): 2.0,
    ('erde', 'luft'): 0.5,
    ('erde', 'pflanze'): 0.5,
    
    # Luft (Air)
    ('luft', 'pflanze'): 2.0,
    ('luft', 'bestie'): 2.0,
    ('luft', 'erde'): 0.5,
    ('luft', 'energie'): 0.5,
    
    # Pflanze (Plant)
    ('pflanze', 'wasser'): 2.0,
    ('pflanze', 'erde'): 2.0,
    ('pflanze', 'feuer'): 0.5,
    ('pflanze', 'pflanze'): 0.5,
    ('pflanze', 'luft'): 0.5,
    
    # Bestie (Beast)
    ('bestie', 'pflanze'): 2.0,
    ('bestie', 'mystik'): 2.0,
    ('bestie', 'feuer'): 0.5,
    ('bestie', 'bestie'): 0.5,
    
    # Energie (Energy)
    ('energie', 'wasser'): 2.0,
    ('energie', 'luft'): 2.0,
    ('energie', 'erde'): 0.5,
    ('energie', 'energie'): 0.5,
    
    # Chaos
    ('chaos', 'mystik'): 2.0,
    ('chaos', 'gottheit'): 2.0,
    ('chaos', 'chaos'): 0.5,
    ('chaos', 'teufel'): 0.5,
    
    # Seuche (Plague)
    ('seuche', 'pflanze'): 2.0,
    ('seuche', 'bestie'): 2.0,
    ('seuche', 'feuer'): 0.5,
    ('seuche', 'seuche'): 0.5,
    ('seuche', 'teufel'): 0.5,
    
    # Mystik (Mystic)
    ('mystik', 'seuche'): 2.0,
    ('mystik', 'bestie'): 0.5,
    ('mystik', 'chaos'): 0.5,
    ('mystik', 'mystik'): 0.5,
    
    # Gottheit (Divine)
    ('gottheit', 'teufel'): 2.0,
    ('gottheit', 'chaos'): 2.0,
    ('gottheit', 'gottheit'): 0.5,
    
    # Teufel (Demon)
    ('teufel', 'gottheit'): 2.0,
    ('teufel', 'mystik'): 2.0,
    ('teufel', 'feuer'): 0.5,
    ('teufel', 'teufel'): 0.5,
}


# Audio Settings
class AudioConfig:
    """Audio configuration."""
    MASTER_VOLUME = 0.7
    BGM_VOLUME = 0.5
    SFX_VOLUME = 0.8
    
    # Fade times (seconds)
    BGM_FADE_IN = 1.0
    BGM_FADE_OUT = 0.5
    
    # Sound channels
    NUM_CHANNELS = 8
    BGM_CHANNEL = 0  # Reserved for background music


# Graphics Settings
class GraphicsConfig:
    """Graphics configuration."""
    # Sprite sizes
    PLAYER_SPRITE_SIZE = 16  # 16x16 Pixel
    NPC_SPRITE_SIZE = 16     # 16x16 Pixel
    MONSTER_SPRITE_SIZE = 16 # 16x16 Pixel
    
    # Animation
    DEFAULT_ANIMATION_SPEED = 0.15  # Seconds per frame
    WALK_ANIMATION_FRAMES = 4
    IDLE_ANIMATION_FRAMES = 2
    
    # Transitions
    FADE_DURATION = 0.5
    BATTLE_SWIRL_DURATION = 1.0
    
    # Text
    TEXT_SPEED_SLOW = 0.05
    TEXT_SPEED_NORMAL = 0.03
    TEXT_SPEED_FAST = 0.01
    
    # UI
    DIALOGUE_BOX_HEIGHT = 48
    MENU_PADDING = 10
    MENU_BORDER_WIDTH = 2


# Game Balance
class BalanceConfig:
    """Game balance configuration."""
    # Economy
    STARTING_MONEY = 1000
    TRAINER_MONEY_MULTIPLIER = 2.0
    ITEM_SELL_RATIO = 0.5
    
    # Encounter rates
    GRASS_ENCOUNTER_RATE = 0.1  # 10% per step
    CAVE_ENCOUNTER_RATE = 0.15
    WATER_ENCOUNTER_RATE = 0.2
    
    # Taming
    BASE_TAMING_RATE = 0.25
    TAMING_ITEM_MULTIPLIERS = {
        'fleisch': 1.5,
        'lecker_fleisch': 2.0,
        'edel_fleisch': 3.0,
        'gold_fleisch': 5.0
    }
    
    # Synthesis
    MIN_SYNTHESIS_LEVEL = 10
    PLUS_VALUE_CAP = 99
    
    # Difficulty
    ENEMY_LEVEL_SCALING = 1.0
    WILD_MONSTER_LEVEL_VARIANCE = 2  # +/- levels


# Debug Settings
class DebugConfig:
    """Debug configuration."""
    SHOW_FPS = False
    SHOW_COLLISION = False
    SHOW_GRID = False
    SHOW_COORDINATES = False
    SHOW_ENTITY_INFO = False
    
    # Cheats (for development)
    INFINITE_MONEY = False
    INFINITE_HP = False
    ONE_HIT_KILL = False
    NO_RANDOM_ENCOUNTERS = False
    FAST_TEXT = False
    UNLOCK_ALL_AREAS = False
    
    # Logging
    LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
    LOG_TO_FILE = True
    LOG_TO_CONSOLE = True


# Network Settings (for future multiplayer)
class NetworkConfig:
    """Network configuration."""
    DEFAULT_PORT = 25565
    MAX_PLAYERS = 4
    TIMEOUT = 30.0
    HEARTBEAT_INTERVAL = 5.0


# Save Settings
class SaveConfig:
    """Save system configuration."""
    MAX_SAVE_SLOTS = 3
    MAX_BACKUPS = 3
    AUTO_SAVE_INTERVAL = 300.0  # 5 minutes
    SAVE_VERSION = "1.0.0"
    
    # File extensions
    SAVE_EXTENSION = ".sav"
    BACKUP_EXTENSION = ".bak"


# Localization
class LocalizationConfig:
    """Localization settings."""
    DEFAULT_LANGUAGE = "de_DE"  # German (Germany)
    SUPPORTED_LANGUAGES = ["de_DE", "en_US"]
    
    # Text encoding
    TEXT_ENCODING = "utf-8"
    
    # Date/time format
    DATE_FORMAT = "%d.%m.%Y"
    TIME_FORMAT = "%H:%M"


# Performance Settings
class PerformanceConfig:
    """Performance optimization settings."""
    # Caching
    MAX_CACHED_IMAGES = 100
    MAX_CACHED_SOUNDS = 50
    MAX_CACHED_MAPS = 10
    
    # Update rates
    PHYSICS_UPDATE_RATE = 60  # Hz
    AI_UPDATE_RATE = 10  # Hz
    
    # Culling
    ENTITY_CULL_DISTANCE = 20  # Tiles
    SOUND_CULL_DISTANCE = 15  # Tiles
    
    # Batching
    SPRITE_BATCH_SIZE = 100
    TILE_BATCH_SIZE = 500


# Platform-specific settings
import platform

PLATFORM = platform.system()
IS_WINDOWS = PLATFORM == "Windows"
IS_MAC = PLATFORM == "Darwin"
IS_LINUX = PLATFORM == "Linux"

# Platform-specific paths
if IS_WINDOWS:
    USER_DATA_DIR = Path.home() / "AppData" / "Local" / "UntoldStory"
elif IS_MAC:
    USER_DATA_DIR = Path.home() / "Library" / "Application Support" / "UntoldStory"
else:  # Linux and others
    USER_DATA_DIR = Path.home() / ".untoldstory"

# Create user data directory
USER_DATA_DIR.mkdir(parents=True, exist_ok=True)


# Camera
CAMERA_DEADZONE_WIDTH = 40   # Deadzone für 16x16 Tiles
CAMERA_DEADZONE_HEIGHT = 30  # Deadzone für 16x16 Tiles  
CAMERA_FOLLOW_SPEED = 8.0    # Kamera-Geschwindigkeit für 16x16 Tiles


# Font Configuration
class Fonts:
    """Font configuration for the game."""
    # Default font sizes
    TINY = 8
    SMALL = 12
    NORMAL = 16
    LARGE = 20
    HUGE = 24
    TITLE = 32
    
    # Font families
    DEFAULT = None  # pygame default
    MONOSPACE = "monospace"
    
    # Font weights (if supported)
    NORMAL_WEIGHT = "normal"
    BOLD = "bold"
    ITALIC = "italic"


# UI Configuration
class UI:
    """UI configuration constants."""
    # Colors
    BACKGROUND = (20, 20, 30)
    BORDER = (100, 100, 120)
    SELECTED = (255, 255, 255)
    UNSELECTED = (150, 150, 150)
    DISABLED = (80, 80, 80)
    
    # Dimensions
    DIALOGUE_BOX_HEIGHT = 48
    MENU_PADDING = 10
    MENU_BORDER_WIDTH = 2
    BUTTON_HEIGHT = 24
    BUTTON_PADDING = 8
    
    # Animation
    FADE_DURATION = 0.3
    MENU_SLIDE_DURATION = 0.2
    BUTTON_HOVER_DURATION = 0.1


# Game State Enum
class GameState(Enum):
    """Game state enumeration."""
    MAIN_MENU = "main_menu"
    PLAYING = "playing"
    PAUSED = "paused"
    BATTLE = "battle"
    DIALOGUE = "dialogue"
    MENU = "menu"
    TRANSITION = "transition"
    CUTSCENE = "cutscene"
    SAVE_LOAD = "save_load"
    QUIT = "quit"


def get_config_value(section: str, key: str, default: Any = None) -> Any:
    """
    Get a configuration value dynamically.
    
    Args:
        section: Configuration section
        key: Configuration key
        default: Default value if not found
        
    Returns:
        Configuration value
    """
    section_map = {
        'display': globals().get('DISPLAY_CONFIG', {}),
        'audio': AudioConfig.__dict__,
        'battle': BattleConfig.__dict__,
        'monster': MonsterConfig.__dict__,
        'graphics': GraphicsConfig.__dict__,
        'balance': BalanceConfig.__dict__,
        'debug': DebugConfig.__dict__,
        'save': SaveConfig.__dict__,
    }
    
    config_dict = section_map.get(section, {})
    return config_dict.get(key, default)


def set_config_value(section: str, key: str, value: Any) -> None:
    """
    Set a configuration value dynamically.
    
    Args:
        section: Configuration section
        key: Configuration key
        value: New value
    """
    section_map = {
        'audio': AudioConfig,
        'battle': BattleConfig,
        'monster': MonsterConfig,
        'graphics': GraphicsConfig,
        'balance': BalanceConfig,
        'debug': DebugConfig,
        'save': SaveConfig,
    }
    
    if section in section_map:
        setattr(section_map[section], key, value)