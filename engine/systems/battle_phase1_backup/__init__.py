"""
Battle System Package for Untold Story
=====================================
Clean interface for battle system after refactoring by Agent 1-4.
All modules are now properly integrated and tested.

Version: 2.0.0 (Post-Refactoring)
"""

# Core Components (User-facing)
from .battle_state import BattleState
from .battle_controller import BattleController
from .turn_processor import TurnProcessor
from .action_processor import ActionProcessor
from .event_processor import EventProcessor
from .status_processor import StatusProcessor
from .battle_validation import BattleValidator
from .error_recovery import BattleErrorRecovery

# Enums
from .battle_enums import (
    BattleType,
    BattlePhase,
    BattleCommand,
    AIPersonality,
    BattleResult
)

# Action System
from .turn_logic import BattleAction, ActionType, TurnOrder
from .battle_ai import BattleAI

# Version after refactoring
__version__ = "2.0.0"

# Public API
__all__ = [
    # Core Components
    'BattleState',
    'BattleController',
    'TurnProcessor',
    'ActionProcessor',
    'EventProcessor',
    'StatusProcessor',
    'BattleValidator',
    'BattleErrorRecovery',
    
    # Enums
    'BattleType', 
    'BattlePhase',
    'BattleCommand',
    'AIPersonality',
    'BattleResult',
    
    # Action System
    'BattleAction',
    'ActionType',
    'TurnOrder',
    'BattleAI',
]

# Deprecation warnings for old imports
def __getattr__(name):
    """Handle deprecated imports with warnings"""
    deprecated = {
        'BattleManager': 'BattleController',
        'BattleEngine': 'BattleController',
        'ItemEffectHandler': 'ItemEffectExecutor (from engine.systems.items)',
    }
    
    if name in deprecated:
        import warnings
        warnings.warn(
            f"{name} is deprecated, use {deprecated[name]} instead",
            DeprecationWarning,
            stacklevel=2
        )
        return globals()[deprecated[name]]
    
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
