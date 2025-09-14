"""
Unified Debug System for Untold Story
Konsolidiertes Debug-System mit allen Debug-Features in einem Modul
"""

import sys
import logging
import pygame
from pathlib import Path
from typing import Optional, List, Dict, Any, TYPE_CHECKING
from enum import Enum, auto
from dataclasses import dataclass

if TYPE_CHECKING:
    from engine.core.game import Game


class DebugLevel(Enum):
    """Debug-Level für verschiedene Arten von Debug-Informationen"""
    ERROR = auto()
    WARNING = auto()
    INFO = auto()
    DEBUG = auto()
    TRACE = auto()


class DebugCategory(Enum):
    """Kategorien für Debug-Outputs"""
    BATTLE = "BATTLE"
    INPUT = "INPUT"
    SCENE = "SCENE"
    RESOURCES = "RESOURCES"
    AI = "AI"
    NETWORK = "NETWORK"
    PERFORMANCE = "PERFORMANCE"
    SYSTEM = "SYSTEM"


@dataclass
class DebugInfo:
    """Debug-Informationen für das Overlay"""
    scene_name: str
    stack_size: int
    total_time: float
    frame_count: int
    mouse_pos: tuple[int, int]
    pressed_keys: List[str]
    movement_vector: tuple[int, int]
    input_debug_status: str
    fps: float


class LogManager:
    """Zentraler Log-Manager für das Spiel"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._setup_logging()
            self._initialized = True
    
    def _setup_logging(self):
        """Konfiguriert das Logging-System"""
        # Create logs directory
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        # Main logger
        self.logger = logging.getLogger("untold_story")
        self.logger.setLevel(logging.DEBUG)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Console handler (für wichtige Meldungen)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter(
            '%(levelname)s: %(message)s'
        )
        console_handler.setFormatter(console_format)
        self.logger.addHandler(console_handler)
        
        # File handler (für alle Meldungen)
        file_handler = logging.FileHandler(
            logs_dir / "game.log", 
            mode='a', 
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_format)
        self.logger.addHandler(file_handler)
        
        # Error file handler (nur für Fehler)
        error_handler = logging.FileHandler(
            logs_dir / "errors.log",
            mode='a',
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_format)
        self.logger.addHandler(error_handler)
    
    def debug(self, message: str, component: Optional[str] = None):
        """Debug-Level Nachricht"""
        self._log(logging.DEBUG, message, component)
    
    def info(self, message: str, component: Optional[str] = None):
        """Info-Level Nachricht"""
        self._log(logging.INFO, message, component)
    
    def warning(self, message: str, component: Optional[str] = None):
        """Warning-Level Nachricht"""
        self._log(logging.WARNING, message, component)
    
    def error(self, message: str, component: Optional[str] = None):
        """Error-Level Nachricht"""
        self._log(logging.ERROR, message, component)
    
    def critical(self, message: str, component: Optional[str] = None):
        """Critical-Level Nachricht"""
        self._log(logging.CRITICAL, message, component)
    
    def _log(self, level: int, message: str, component: Optional[str] = None):
        """Interne Log-Funktion"""
        if component:
            formatted_message = f"[{component}] {message}"
        else:
            formatted_message = message
        
        self.logger.log(level, formatted_message)


class DebugOverlay:
    """Debug-Overlay für visuelle Debug-Informationen"""
    
    def __init__(self, game: 'Game'):
        self.game = game
        self.font: Optional[pygame.font.Font] = None
        self._init_font()
    
    def _init_font(self) -> None:
        """Initialisiert die Debug-Font"""
        try:
            self.font = pygame.font.Font(None, 16)
        except Exception:
            self.log_error("Could not load debug font")
    
    def draw_fps(self, surface: pygame.Surface) -> None:
        """Zeichnet FPS-Zähler"""
        if not self.game.show_fps or not self.font:
            return
        
        fps_text = f"FPS: {self.game.clock.get_fps():.1f}"
        fps_surface = self.font.render(fps_text, True, (255, 255, 0))
        surface.blit(fps_surface, (2, 2))
    
    def draw_collision_boxes(self, surface: pygame.Surface) -> None:
        """Zeichnet Kollisions-Boxen"""
        if not hasattr(self.game, 'show_collision') or not self.game.show_collision:
            return
        
        # Hier könnten Kollisions-Boxen gezeichnet werden
        # Abhängig von der Implementierung des Spiels
        pass
    
    def draw_entity_info(self, surface: pygame.Surface) -> None:
        """Zeichnet Entity-Informationen"""
        if not hasattr(self.game, 'show_entity_info') or not self.game.show_entity_info:
            return
        
        # Hier könnten Entity-Informationen gezeichnet werden
        pass
    
    def draw_debug_overlay(self, surface: pygame.Surface) -> None:
        """Zeichnet das komplette Debug-Overlay"""
        if not self.game.debug_overlay_enabled or not self.font:
            return
        
        # Debug-Informationen sammeln
        debug_info = self._collect_debug_info()
        
        # Debug-Text zeichnen
        self._draw_debug_text(surface, debug_info)
        
        # Input-Debug Hotkey-Hilfe
        if hasattr(self.game, 'input_manager') and self.game.input_manager.debug_enabled:
            self._draw_debug_help(surface)
        
        # Grid zeichnen wenn aktiviert
        if self.game.show_grid:
            self._draw_grid(surface)
    
    def _collect_debug_info(self) -> DebugInfo:
        """Sammelt Debug-Informationen"""
        # Aktuelle gedrückte Tasten
        pressed_keys = []
        if hasattr(self.game, 'input_manager'):
            pressed_keys = [k for k, v in self.game.keys_pressed.items() if v]
            if pressed_keys:
                key_names = []
                for key in pressed_keys[:5]:  # Maximal 5 Tasten anzeigen
                    if hasattr(self.game.input_manager, '_get_key_name'):
                        key_names.append(self.game.input_manager._get_key_name(key))
                    else:
                        key_names.append(f"KEY_{key}")
                pressed_keys = key_names
        
        # Movement Vector
        movement = (0, 0)
        if hasattr(self.game, 'input_manager') and hasattr(self.game.input_manager, 'get_movement_vector'):
            movement = self.game.input_manager.get_movement_vector()
        
        # Input-Debug Status
        input_debug_status = "OFF"
        if hasattr(self.game, 'input_manager') and hasattr(self.game.input_manager, 'debug_enabled'):
            input_debug_status = "ON" if self.game.input_manager.debug_enabled else "OFF"
        
        return DebugInfo(
            scene_name=self.game.scene_stack[-1].__class__.__name__ if self.game.scene_stack else "None",
            stack_size=len(self.game.scene_stack),
            total_time=self.game.total_time,
            frame_count=self.game.frame_count,
            mouse_pos=self.game.mouse_pos,
            pressed_keys=pressed_keys,
            movement_vector=movement,
            input_debug_status=input_debug_status,
            fps=self.game.clock.get_fps()
        )
    
    def _draw_debug_text(self, surface: pygame.Surface, info: DebugInfo) -> None:
        """Zeichnet Debug-Text"""
        debug_lines = [
            f"Scene: {info.scene_name}",
            f"Stack: {info.stack_size}",
            f"Time: {info.total_time:.1f}s",
            f"Frame: {info.frame_count}",
            f"Mouse: {info.mouse_pos}",
        ]
        
        # Gedrückte Tasten hinzufügen
        if info.pressed_keys:
            debug_lines.append(f"Pressed: {', '.join(info.pressed_keys)}")
        
        # Movement Vector hinzufügen
        if info.movement_vector != (0, 0):
            debug_lines.append(f"Movement: {info.movement_vector}")
        
        # Input-Debug Status hinzufügen
        debug_lines.append(f"Input Debug: {info.input_debug_status}")
        
        # Debug-Text zeichnen
        y = 20
        for line in debug_lines:
            text_surface = self.font.render(line, True, (0, 255, 0))
            surface.blit(text_surface, (2, y))
            y += 12
    
    def _draw_debug_help(self, surface: pygame.Surface) -> None:
        """Zeichnet Debug-Hilfe"""
        help_lines = [
            "F1: Input-Log Summary",
            "F2: Clear Input-Log", 
            "F3: Toggle Input-Debug",
            "F4: Current Input-Status",
            "F5: Export Input-Analysis",
            "F6: Find Unhandled Inputs",
            "F7: Find Performance Issues",
            "F8: Debug-Hilfe"
        ]
        
        # Hilfe am unteren Bildschirmrand zeichnen
        y_help = self.game.logical_size[1] - 60
        for help_line in help_lines:
            text_surface = self.font.render(help_line, True, (255, 255, 0))
            surface.blit(text_surface, (2, y_help))
            y_help += 12
    
    def _draw_grid(self, surface: pygame.Surface) -> None:
        """Zeichnet ein Tile-Grid-Overlay"""
        from engine.world.tiles import TILE_SIZE
        color = (255, 255, 255, 64)  # Semi-transparent white
        
        # Vertikale Linien
        for x in range(0, self.game.logical_size[0] + 1, TILE_SIZE):
            pygame.draw.line(surface, color, 
                           (x, 0), (x, self.game.logical_size[1]), 1)
        
        # Horizontale Linien
        for y in range(0, self.game.logical_size[1] + 1, TILE_SIZE):
            pygame.draw.line(surface, color,
                           (0, y), (self.game.logical_size[0], y), 1)


class DebugSystem:
    """Complete debug system for development."""
    
    # Debug-Flags
    DEBUG_FLAGS = {
        'show_fps': True,
        'show_collision': False,
        'battle_info': True,
        'show_grid': False,
        'debug_overlay_enabled': False,
    }
    
    # Standard-Debug-Level
    DEFAULT_LEVEL = DebugLevel.INFO
    
    # Standard-Kategorien (alle aktiviert)
    DEFAULT_CATEGORIES = {
        DebugCategory.BATTLE: True,
        DebugCategory.INPUT: True,
        DebugCategory.SCENE: True,
        DebugCategory.RESOURCES: True,
        DebugCategory.AI: True,
        DebugCategory.NETWORK: False,  # Deaktiviert, da nicht verwendet
        DebugCategory.PERFORMANCE: True,
        DebugCategory.SYSTEM: True,
    }
    
    # Debug-Hotkeys
    DEBUG_HOTKEYS = {
        'TAB': 'Debug-Overlay ein/aus',
        'G': 'Grid anzeigen/verstecken (nur wenn Debug aktiv)',
        'F1': 'Input-Log Zusammenfassung',
        'F2': 'Input-Log leeren',
        'F3': 'Input-Debug ein/aus',
        'F4': 'Aktueller Input-Status',
        'F5': 'Input-Analyse exportieren',
        'F6': 'Unbehandelte Inputs finden',
        'F7': 'Performance-Probleme finden',
    }
    
    def __init__(self):
        self.enabled = False
        self.level = self.DEFAULT_LEVEL
        self.categories: Dict[DebugCategory, bool] = {
            category: True for category in DebugCategory
        }
        self.game_instance: Optional['Game'] = None
        self.log_manager = LogManager()
        self.overlay: Optional[DebugOverlay] = None
        
    def set_game_instance(self, game_instance: 'Game') -> None:
        """Setzt die Game-Instanz für Debug-Zugriff"""
        self.game_instance = game_instance
        if self.game_instance:
            self.overlay = DebugOverlay(self.game_instance)
        
    def is_enabled(self) -> bool:
        """Prüft ob Debug-Modus aktiviert ist"""
        if self.game_instance and hasattr(self.game_instance, 'debug_mode'):
            return self.game_instance.debug_mode
        return self.enabled
        
    def should_log(self, level: DebugLevel, category: DebugCategory) -> bool:
        """Prüft ob eine Debug-Meldung ausgegeben werden soll"""
        if not self.is_enabled():
            return False
            
        # Prüfe Level
        if level.value > self.level.value:
            return False
            
        # Prüfe Kategorie
        return self.categories.get(category, True)
        
    def log(self, level: DebugLevel, category: DebugCategory, message: str, 
            *args, **kwargs) -> None:
        """Zentrale Debug-Logging-Funktion"""
        if not self.should_log(level, category):
            return
            
        # Formatiere Nachricht
        formatted_message = f"[{category.value}] {message}"
        if args:
            formatted_message = formatted_message.format(*args)
            
        # Ausgabe
        if level == DebugLevel.ERROR:
            print(f"❌ {formatted_message}", file=sys.stderr)
        elif level == DebugLevel.WARNING:
            print(f"⚠️  {formatted_message}")
        elif level == DebugLevel.INFO:
            print(f"ℹ️  {formatted_message}")
        elif level == DebugLevel.DEBUG:
            print(f"🔍 {formatted_message}")
        elif level == DebugLevel.TRACE:
            print(f"🔬 {formatted_message}")
            
    def error(self, category: DebugCategory, message: str, *args, **kwargs) -> None:
        """Log Error-Level Nachricht"""
        self.log(DebugLevel.ERROR, category, message, *args, **kwargs)
        
    def warning(self, category: DebugCategory, message: str, *args, **kwargs) -> None:
        """Log Warning-Level Nachricht"""
        self.log(DebugLevel.WARNING, category, message, *args, **kwargs)
        
    def info(self, category: DebugCategory, message: str, *args, **kwargs) -> None:
        """Log Info-Level Nachricht"""
        self.log(DebugLevel.INFO, category, message, *args, **kwargs)
        
    def debug(self, category: DebugCategory, message: str, *args, **kwargs) -> None:
        """Log Debug-Level Nachricht"""
        self.log(DebugLevel.DEBUG, category, message, *args, **kwargs)
        
    def trace(self, category: DebugCategory, message: str, *args, **kwargs) -> None:
        """Log Trace-Level Nachricht"""
        self.log(DebugLevel.TRACE, category, message, *args, **kwargs)
        
    def toggle_category(self, category: DebugCategory) -> None:
        """Schaltet eine Debug-Kategorie ein/aus"""
        self.categories[category] = not self.categories[category]
        
    def set_level(self, level: DebugLevel) -> None:
        """Setzt das Debug-Level"""
        self.level = level
        
    def get_debug_info(self) -> Dict[str, Any]:
        """Gibt Debug-Informationen zurück"""
        return {
            'enabled': self.is_enabled(),
            'level': self.level.name,
            'categories': {cat.name: enabled for cat, enabled in self.categories.items()}
        }
    
    def print_debug_help(self) -> None:
        """Zeigt Debug-Hilfe an"""
        if not self.is_enabled():
            print("🔍 DEBUG-SYSTEM: Drücke TAB um Debug-Modus zu aktivieren")
            return
            
        print("\n" + "="*60)
        print("🔍 DEBUG-SYSTEM HILFE")
        print("="*60)
        print("TAB: Debug-System ein/aus")
        print("F1: Input-Log Zusammenfassung")
        print("F2: Input-Log löschen")
        print("F3: Input-Debug ein/aus")
        print("F4: Aktueller Input-Status")
        print("F5: Input-Analyse exportieren")
        print("F6: Unbehandelte Inputs finden")
        print("F7: Performance-Probleme finden")
        print("G: Grid ein/aus")
        print("="*60)
        print(f"Status: {'AKTIVIERT' if self.is_enabled() else 'DEAKTIVIERT'}")
        print(f"Level: {self.level.name}")
        print("Kategorien:")
        for category, enabled in self.categories.items():
            status = "✓" if enabled else "✗"
            print(f"  {status} {category.value}")
        print("="*60)
    
    @classmethod
    def initialize(cls) -> 'DebugSystem':
        """One-time setup for entire debug system."""
        instance = cls()
        instance.setup_logging()
        instance.load_debug_flags()
        return instance
    
    def setup_logging(self) -> None:
        """Setup logging system"""
        # Logging wird bereits durch LogManager initialisiert
        pass
    
    def load_debug_flags(self) -> None:
        """Load debug flags from config"""
        # Hier könnten Debug-Flags aus einer Konfigurationsdatei geladen werden
        pass
    
    def create_overlay(self) -> None:
        """Create debug overlay"""
        if self.game_instance:
            self.overlay = DebugOverlay(self.game_instance)


# Globale Debug-System-Instanz
debug = DebugSystem()


# Convenience-Funktionen für einfache Migration
def log_debug(message: str, component: str = "GAME"):
    """Convenience function for debug logging"""
    debug.log_manager.debug(message, component)


def log_info(message: str, component: str = "GAME"):
    """Convenience function for info logging"""
    debug.log_manager.info(message, component)


def log_warning(message: str, component: str = "GAME"):
    """Convenience function for warning logging"""
    debug.log_manager.warning(message, component)


def log_error(message: str, component: str = "GAME"):
    """Convenience function for error logging"""
    debug.log_manager.error(message, component)


def log_critical(message: str, component: str = "GAME"):
    """Convenience function for critical logging"""
    debug.log_manager.critical(message, component)


# Battle-spezifische Debug-Funktionen
def debug_battle_error(message: str, *args, **kwargs) -> None:
    """Battle-spezifische Error-Logging"""
    debug.error(DebugCategory.BATTLE, message, *args, **kwargs)


def debug_battle_info(message: str, *args, **kwargs) -> None:
    """Battle-spezifische Info-Logging"""
    debug.info(DebugCategory.BATTLE, message, *args, **kwargs)


def debug_battle_debug(message: str, *args, **kwargs) -> None:
    """Battle-spezifische Debug-Logging"""
    debug.debug(DebugCategory.BATTLE, message, *args, **kwargs)


# Scene-spezifische Debug-Funktionen
def debug_scene_error(message: str, *args, **kwargs) -> None:
    """Scene-spezifische Error-Logging"""
    debug.error(DebugCategory.SCENE, message, *args, **kwargs)


def debug_scene_info(message: str, *args, **kwargs) -> None:
    """Scene-spezifische Info-Logging"""
    debug.info(DebugCategory.SCENE, message, *args, **kwargs)


def debug_scene_debug(message: str, *args, **kwargs) -> None:
    """Scene-spezifische Debug-Logging"""
    debug.debug(DebugCategory.SCENE, message, *args, **kwargs)


# System-spezifische Debug-Funktionen
def debug_system_error(message: str, *args, **kwargs) -> None:
    """System-spezifische Error-Logging"""
    debug.error(DebugCategory.SYSTEM, message, *args, **kwargs)


def debug_system_info(message: str, *args, **kwargs) -> None:
    """System-spezifische Info-Logging"""
    debug.info(DebugCategory.SYSTEM, message, *args, **kwargs)


def debug_system_debug(message: str, *args, **kwargs) -> None:
    """System-spezifische Debug-Logging"""
    debug.debug(DebugCategory.SYSTEM, message, *args, **kwargs)


# Performance logging
def log_performance(operation: str, duration: float, component: str = "PERFORMANCE"):
    """Log performance metrics"""
    if duration > 0.1:  # Log slow operations (>100ms)
        debug.log_manager.warning(f"SLOW: {operation} took {duration:.3f}s", component)
    elif duration > 0.05:  # Log moderate operations (>50ms)
        debug.log_manager.info(f"{operation} took {duration:.3f}s", component)
    else:
        debug.log_manager.debug(f"{operation} took {duration:.3f}s", component)
