"""
Core battle system modules - split from monolithic controller
Contains specialized modules for different aspects of battle control.
"""

from .battle_controller_core import BattleControllerCore
from .battle_controller_state import BattleControllerStateMixin as BattleControllerState
from .battle_controller_actions import BattleControllerActionsMixin as BattleControllerActions
from .battle_controller_phases import BattleControllerPhasesMixin as BattleControllerPhases

__all__ = [
    'BattleControllerCore',
    'BattleControllerState', 
    'BattleControllerActions',
    'BattleControllerPhases'
]
