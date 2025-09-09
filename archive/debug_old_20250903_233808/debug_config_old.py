"""
Unified Debug Configuration for Untold Story
Konsolidierte Debug-Konfiguration mit allen Debug-Features
"""

import sys
from typing import Optional, Any, Dict
from enum import Enum, auto


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


class DebugManager:
    """Zentraler Debug-Manager für das Spiel"""
    
    def __init__(self):
        self.enabled = False
        self.level = DebugLevel.INFO
        self.categories: Dict[DebugCategory, bool] = {
            category: True for category in DebugCategory
        }
        self.game_instance: Optional[Any] = None
        
    def set_game_instance(self, game_instance: Any) -> None:
        """Setzt die Game-Instanz für Debug-Zugriff"""
        self.game_instance = game_instance
        
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


class DebugConfig:
    """Unified Debug-Konfiguration für das Spiel"""
    
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
    
    @classmethod
    def initialize_debug_system(cls) -> None:
        """Initialisiert das Debug-System mit Standard-Konfiguration"""
        debug_manager.set_level(cls.DEFAULT_LEVEL)
        
        for category, enabled in cls.DEFAULT_CATEGORIES.items():
            debug_manager.categories[category] = enabled
            
    @classmethod
    def get_debug_help_text(cls) -> str:
        """Gibt Hilfe-Text für Debug-Hotkeys zurück"""
        help_lines = ["=== DEBUG HOTKEYS ==="]
        for key, description in cls.DEBUG_HOTKEYS.items():
            help_lines.append(f"{key}: {description}")
        return "\n".join(help_lines)
    
    @classmethod
    def print_debug_status(cls) -> None:
        """Druckt aktuellen Debug-Status"""
        status = debug_manager.get_debug_info()
        print("=== DEBUG STATUS ===")
        print(f"Enabled: {status['enabled']}")
        print(f"Level: {status['level']}")
        print("Categories:")
        for category, enabled in status['categories'].items():
            status_icon = "✓" if enabled else "✗"
            print(f"  {status_icon} {category}")


# Globale Debug-Manager-Instanz
debug_manager = DebugManager()


# Convenience-Funktionen
def debug_error(category: DebugCategory, message: str, *args, **kwargs) -> None:
    """Convenience-Funktion für Error-Logging"""
    debug_manager.error(category, message, *args, **kwargs)


def debug_warning(category: DebugCategory, message: str, *args, **kwargs) -> None:
    """Convenience-Funktion für Warning-Logging"""
    debug_manager.warning(category, message, *args, **kwargs)


def debug_info(category: DebugCategory, message: str, *args, **kwargs) -> None:
    """Convenience-Funktion für Info-Logging"""
    debug_manager.info(category, message, *args, **kwargs)


def debug_debug(category: DebugCategory, message: str, *args, **kwargs) -> None:
    """Convenience-Funktion für Debug-Logging"""
    debug_manager.debug(category, message, *args, **kwargs)


def debug_trace(category: DebugCategory, message: str, *args, **kwargs) -> None:
    """Convenience-Funktion für Trace-Logging"""
    debug_manager.trace(category, message, *args, **kwargs)


# Battle-spezifische Debug-Funktionen
def debug_battle_error(message: str, *args, **kwargs) -> None:
    """Battle-spezifische Error-Logging"""
    debug_manager.error(DebugCategory.BATTLE, message, *args, **kwargs)


def debug_battle_info(message: str, *args, **kwargs) -> None:
    """Battle-spezifische Info-Logging"""
    debug_manager.info(DebugCategory.BATTLE, message, *args, **kwargs)


def debug_battle_debug(message: str, *args, **kwargs) -> None:
    """Battle-spezifische Debug-Logging"""
    debug_manager.debug(DebugCategory.BATTLE, message, *args, **kwargs)


# Scene-spezifische Debug-Funktionen
def debug_scene_error(message: str, *args, **kwargs) -> None:
    """Scene-spezifische Error-Logging"""
    debug_manager.error(DebugCategory.SCENE, message, *args, **kwargs)


def debug_scene_info(message: str, *args, **kwargs) -> None:
    """Scene-spezifische Info-Logging"""
    debug_manager.info(DebugCategory.SCENE, message, *args, **kwargs)


def debug_scene_debug(message: str, *args, **kwargs) -> None:
    """Scene-spezifische Debug-Logging"""
    debug_manager.debug(DebugCategory.SCENE, message, *args, **kwargs)


# System-spezifische Debug-Funktionen
def debug_system_error(message: str, *args, **kwargs) -> None:
    """System-spezifische Error-Logging"""
    debug_manager.error(DebugCategory.SYSTEM, message, *args, **kwargs)


def debug_system_info(message: str, *args, **kwargs) -> None:
    """System-spezifische Info-Logging"""
    debug_manager.info(DebugCategory.SYSTEM, message, *args, **kwargs)


def debug_system_debug(message: str, *args, **kwargs) -> None:
    """System-spezifische Debug-Logging"""
    debug_manager.debug(DebugCategory.SYSTEM, message, *args, **kwargs)


# Automatische Initialisierung beim Import
DebugConfig.initialize_debug_system()