"""
Battle UI Module - Modulare Battle UI Komponenten
Zerlegt aus der monolithischen battle_ui.py (2029 Zeilen → 5 Module)

Module:
- battle_ui_core.py: Hauptklasse BattleUI
- battle_ui_renderer.py: Alle draw_* Methoden
- battle_ui_input.py: Input handling
- battle_ui_menus.py: Menu-spezifische Logic
- battle_ui_state.py: State management
"""

# Import main components
from .battle_ui_core import BattleUI
from .battle_ui_renderer import BattleUIRenderer
from .battle_ui_input import BattleUIInputHandler
from .battle_ui_menus import BattleUIMenuManager
from .battle_ui_state import (
    BattleMenuState,
    BattleSprite,
    DamageNumber,
    BattleUIState
)

# Export main components
__all__ = [
    'BattleUI',
    'BattleUIRenderer', 
    'BattleUIInputHandler',
    'BattleUIMenuManager',
    'BattleMenuState',
    'BattleSprite',
    'DamageNumber',
    'BattleUIState'
]