"""
Battle Action Handler Fix
Simplified action processing for battle system
"""

from enum import Enum, auto
from typing import Dict, Any, Optional

class SimpleActionType(Enum):
    """Simplified action types."""
    ATTACK = auto()
    DEFEND = auto()
    ITEM = auto()
    FLEE = auto()
    SWITCH = auto()
    SPECIAL = auto()
    MENU = auto()

def create_simple_action(action_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Create a simplified battle action."""
    action_type = action_data.get('action', '')
    
    if action_type == 'attack':
        return {
            'type': 'attack',
            'actor': action_data.get('actor'),
            'move': action_data.get('move'),
            'target': action_data.get('target'),
            'move_index': action_data.get('move_index', 0)
        }
    elif action_type == 'flee':
        return {
            'type': 'flee',
            'actor': action_data.get('actor')
        }
    elif action_type in ['tame', 'scout', 'switch', 'item']:
        return {
            'type': action_type,
            'actor': action_data.get('actor')
        }
    elif action_type == 'menu_select':
        # This is a UI action, not a battle action
        return None
    else:
        # Default attack action
        return {
            'type': 'attack',
            'actor': action_data.get('actor'),
            'move': None,
            'target': None
        }
