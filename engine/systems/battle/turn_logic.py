"""
Turn Logic - Facade for modular turn-based battle logic
======================================================
Facade providing unified interface for turn-based battle logic.
"""

# Import core components
from .logic.turn_logic_core import ActionType, BattleAction, TurnOrder
from .logic.turn_logic_actions import create_battle_action_from_dict, validate_battle_action
from .logic.turn_logic_validation import validate_turn_order, validate_action_sequence, get_action_priority_score

# Re-export main classes and functions for backward compatibility
__all__ = [
    'ActionType',
    'BattleAction', 
    'TurnOrder',
    'create_battle_action_from_dict',
    'create_action_from_dict',  # Alias for backward compatibility
    'validate_battle_action',
    'validate_turn_order',
    'validate_action_sequence',
    'get_action_priority_score'
]

# Create alias for backward compatibility
create_action_from_dict = create_battle_action_from_dict