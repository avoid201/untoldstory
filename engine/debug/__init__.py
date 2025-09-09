"""
Debug System Module for Untold Story
Konsolidiertes Debug-System mit einfachen Exports
"""

from .debug_system import (
    # Main debug system
    DebugSystem,
    debug,
    
    # Enums
    DebugLevel,
    DebugCategory,
    
    # Classes
    LogManager,
    DebugOverlay,
    DebugInfo,
    
    # Convenience functions
    log_debug,
    log_info,
    log_warning,
    log_error,
    log_critical,
    log_performance,
    
    # Battle-specific functions
    debug_battle_error,
    debug_battle_info,
    debug_battle_debug,
    
    # Scene-specific functions
    debug_scene_error,
    debug_scene_info,
    debug_scene_debug,
    
    # System-specific functions
    debug_system_error,
    debug_system_info,
    debug_system_debug,
)

# Initialize debug system on import
debug.initialize()

__all__ = [
    # Main system
    'DebugSystem',
    'debug',
    
    # Enums
    'DebugLevel',
    'DebugCategory',
    
    # Classes
    'LogManager',
    'DebugOverlay',
    'DebugInfo',
    
    # Logging functions
    'log_debug',
    'log_info',
    'log_warning',
    'log_error',
    'log_critical',
    'log_performance',
    
    # Battle functions
    'debug_battle_error',
    'debug_battle_info',
    'debug_battle_debug',
    
    # Scene functions
    'debug_scene_error',
    'debug_scene_info',
    'debug_scene_debug',
    
    # System functions
    'debug_system_error',
    'debug_system_info',
    'debug_system_debug',
]
