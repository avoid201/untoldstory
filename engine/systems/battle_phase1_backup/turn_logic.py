"""
Turn Logic - DQM-Authentic Implementation
========================================
Turn-based battle logic with DQM formulas and proper action handling.
"""

from enum import Enum
from typing import List, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from engine.systems.monster_instance import MonsterInstance
    from engine.systems.moves import Move


class ActionType(Enum):
    """Action types for battle actions."""
    
    ATTACK = "ATTACK"
    SWITCH = "SWITCH"
    ITEM = "ITEM"
    RUN = "RUN"
    TAME = "TAME"
    GUARD = "GUARD"
    
    def __str__(self):
        return self.value


class BattleAction:
    """Represents a battle action with DQM-style validation."""
    
    def __init__(self, action_type: ActionType, actor: 'MonsterInstance' = None, 
                 target: 'MonsterInstance' = None, move: 'Move' = None, 
                 switch_to: 'MonsterInstance' = None, item_id: str = None):
        self.action_type = action_type
        self.actor = actor
        self.target = target
        self.move = move
        self.switch_to = switch_to
        self.item_id = item_id
        
        # Action metadata
        self.priority = 0
        self.timestamp = None
        
        # Validate action on creation
        self._validate_action()
    
    def _validate_action(self):
        """Validate action on creation."""
        if not self.action_type:
            raise ValueError("Action type is required")
        
        if not self.actor:
            raise ValueError("Actor is required")
        
        # Validate action-specific requirements
        if self.action_type == ActionType.ATTACK and not self.move:
            raise ValueError("Attack action requires a move")
        
        if self.action_type == ActionType.SWITCH and not self.switch_to:
            raise ValueError("Switch action requires switch_to target")
        
        if self.action_type == ActionType.ITEM and not self.item_id:
            raise ValueError("Item action requires item_id")
    
    def get_priority(self) -> int:
        """Get action priority for turn order."""
        if self.move and hasattr(self.move, 'priority'):
            return self.move.priority
        return 0
    
    def is_valid(self) -> bool:
        """Check if action is valid."""
        try:
            self._validate_action()
            return True
        except ValueError:
            return False
    
    def __str__(self):
        return f"BattleAction({self.action_type.value}, {self.actor.name if self.actor else 'None'})"


class TurnOrder:
    """Handles turn order calculation with DQM formulas."""
    
    @staticmethod
    def calculate_turn_order(actions: List[BattleAction]) -> List[BattleAction]:
        """
        Calculate turn order based on DQM rules:
        1. Priority (higher goes first)
        2. Speed + Random(0-255)
        3. Player advantage bei Gleichstand
        """
        if not actions:
            return []
        
        # Sort by priority first, then speed
        def sort_key(action):
            priority = action.get_priority()
            speed = action.actor.stats.get('spd', 50) if action.actor else 50
            # Player gets slight advantage
            player_bonus = 1 if action.actor and hasattr(action.actor, 'is_player') and action.actor.is_player else 0
            return (-priority, -(speed + player_bonus))
        
        return sorted(actions, key=sort_key)
    
    @staticmethod
    def calculate_speed_roll(monster: 'MonsterInstance') -> int:
        """Calculate speed roll for turn order (DQM formula)."""
        if not monster:
            return 0
        
        base_speed = monster.stats.get('spd', 50)
        import random
        return base_speed + random.randint(0, 255)
    
    @staticmethod
    def get_turn_order_with_speed(actions: List[BattleAction]) -> List[tuple]:
        """Get turn order with speed values for debugging."""
        turn_order = []
        
        for action in actions:
            if not action or not action.actor:
                continue
            
            priority = action.get_priority()
            speed_roll = TurnOrder.calculate_speed_roll(action.actor)
            
            turn_order.append((priority, speed_roll, action))
        
        # Sort by priority first, then speed
        turn_order.sort(key=lambda x: (-x[0], -x[1]))
        return turn_order
