"""
Turn Logic Core - Core turn-based battle logic
=============================================
Core turn order calculation and action creation logic.
"""

from enum import Enum
from typing import List, Any, Optional, Dict, TYPE_CHECKING
import logging

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from engine.systems.monster_instance import MonsterInstance
    from engine.systems.moves import Move


class ActionType(Enum):
    """Action types for battle actions."""
    ATTACK = "attack"
    SWITCH = "switch"
    ITEM = "item"
    RUN = "run"
    TAME = "tame"
    
    @classmethod
    def from_string(cls, value: str) -> 'ActionType':
        """Create ActionType from string value with proper error handling."""
        try:
            if isinstance(value, str):
                # Normalize the string
                value = value.lower().strip()
                
                # Direct mapping
                if value == "attack":
                    return cls.ATTACK
                elif value == "switch":
                    return cls.SWITCH
                elif value == "item":
                    return cls.ITEM
                elif value == "run":
                    return cls.RUN
                elif value == "tame":
                    return cls.TAME
                
                # Try to find by value
                for action_type in cls:
                    if action_type.value == value:
                        return action_type
                
                # Try to find by name (case insensitive)
                for action_type in cls:
                    if action_type.name.lower() == value.upper():
                        return action_type
                
                # If nothing matches, log warning and return default
                logger.warning(f"Unknown action type: '{value}', defaulting to ATTACK")
                return cls.ATTACK
            else:
                logger.warning(f"Invalid action type value: {value} (type: {type(value)}), defaulting to ATTACK")
                return cls.ATTACK
        except Exception as e:
            logger.error(f"Error converting action type '{value}': {e}, defaulting to ATTACK")
            return cls.ATTACK
    
    @classmethod
    def safe_convert(cls, value: str) -> 'ActionType':
        """Safely convert string to ActionType with fallback."""
        try:
            return cls.from_string(value)
        except Exception as e:
            logger.error(f"Safe convert failed for '{value}': {e}")
            return cls.ATTACK


class BattleAction:
    """Battle action data structure."""
    
    def __init__(self, action_type: ActionType, actor: 'MonsterInstance', 
                 target: 'MonsterInstance' = None, move: 'Move' = None,
                 switch_to: 'MonsterInstance' = None, item_id: str = None):
        self.action_type = action_type
        self.actor = actor
        self.target = target
        self.move = move
        self.switch_to = switch_to
        self.item_id = item_id
    
    def get_priority(self) -> int:
        """Get action priority for turn order calculation."""
        if self.move and hasattr(self.move, 'priority'):
            return self.move.priority
        return 0


class TurnOrder:
    """CONSOLIDATED Turn Order Calculation - Single source of truth for all turn order logic."""
    
    def __init__(self):
        """Initialize turn order processor."""
        self.actions = []
    
    def clear(self):
        """Clear all actions from turn order."""
        self.actions = []
    
    def add_action(self, action: BattleAction):
        """Add action to turn order."""
        if action:
            self.actions.append(action)
    
    def calculate_turn_order(self, actions: List[BattleAction] = None) -> List[BattleAction]:
        """Calculate turn order for given actions or stored actions."""
        if actions is not None:
            return self._calculate_turn_order(actions)
        return self._calculate_turn_order(self.actions)
    
    @staticmethod
    def _calculate_turn_order(actions: List[BattleAction]) -> List[BattleAction]:
        """
        CONSOLIDATED Turn Order Calculation - Single source of truth for all turn order logic.
        Consolidated from turn_logic.py, turn_processor_order.py, and dqm_integration.py.

        DQM Turn Order Rules:
        1. Priority (Move priority - higher goes first)
        2. Speed + Random(0-255)
        3. Player advantage bei Gleichstand

        Args:
            actions: List of battle actions

        Returns:
            List of actions sorted by turn order (first to act first)
        """
        if not actions:
            return []

        import random

        # Calculate turn order for each action
        turn_order_data = []

        for action in actions:
            if not action or not action.actor:
                continue

            # Get action priority
            priority = action.get_priority()

            # Get base speed
            base_speed = action.actor.stats.get('spd', 50) if action.actor.stats else 50

            # Apply stat stage modifiers
            if hasattr(action.actor, 'stat_stages') and hasattr(action.actor.stat_stages, 'spd'):
                stage = action.actor.stat_stages.spd
                if stage > 0:
                    multiplier = (2 + stage) / 2
                else:
                    multiplier = 2 / (2 - stage)
                base_speed = int(base_speed * multiplier)

            # Apply status effect modifiers
            if hasattr(action.actor, 'status') and action.actor.status:
                if hasattr(action.actor.status, 'name'):
                    if action.actor.status if isinstance(action.actor.status, str) else action.actor.status.name == 'PARALYSIS':
                        base_speed = int(base_speed * 0.5)

            # DQM Formula: Speed + Random(0-255)
            speed_roll = base_speed + random.randint(0, 255)

            # Player advantage bei Gleichstand
            player_bonus = 1 if (hasattr(action.actor, 'is_player') and action.actor.is_player) else 0
            final_speed = speed_roll + player_bonus

            turn_order_data.append({
                'action': action,
                'priority': priority,
                'base_speed': base_speed,
                'speed_roll': speed_roll,
                'final_speed': final_speed
            })

        # Sort by priority first (higher priority goes first), then by final speed (higher speed goes first)
        turn_order_data.sort(key=lambda x: (-x['priority'], -x['final_speed']))

        # Return actions in order
        return [data['action'] for data in turn_order_data]

    @staticmethod
    def get_turn_order_breakdown(actions: List[BattleAction]) -> List[Dict[str, Any]]:
        """
        Get detailed breakdown of turn order calculation.

        Args:
            actions: List of battle actions

        Returns:
            List of turn order details with calculations
        """
        if not actions:
            return []

        import random

        breakdown = []

        for action in actions:
            if not action or not action.actor:
                continue

            # Get action priority
            priority = action.get_priority()

            # Get base speed
            base_speed = action.actor.stats.get('spd', 50) if action.actor.stats else 50

            # Apply stat stage modifiers
            if hasattr(action.actor, 'stat_stages') and hasattr(action.actor.stat_stages, 'spd'):
                stage = action.actor.stat_stages.spd
                if stage > 0:
                    multiplier = (2 + stage) / 2
                else:
                    multiplier = 2 / (2 - stage)
                base_speed = int(base_speed * multiplier)

            # Apply status effect modifiers
            if hasattr(action.actor, 'status') and action.actor.status:
                if hasattr(action.actor.status, 'name'):
                    if action.actor.status if isinstance(action.actor.status, str) else action.actor.status.name == 'PARALYSIS':
                        base_speed = int(base_speed * 0.5)

            # DQM Formula: Speed + Random(0-255)
            speed_roll = base_speed + random.randint(0, 255)

            # Player advantage bei Gleichstand
            player_bonus = 1 if (hasattr(action.actor, 'is_player') and action.actor.is_player) else 0
            final_speed = speed_roll + player_bonus

            breakdown.append({
                'actor': action.actor.name if hasattr(action.actor, 'name') else 'Unknown',
                'priority': priority,
                'base_speed': base_speed,
                'speed_roll': speed_roll,
                'player_advantage': player_bonus,
                'final_speed': final_speed,
                'action_type': action.action_type.name if hasattr(action, 'action_type') else 'UNKNOWN'
            })

        # Sort by final speed (descending)
        breakdown.sort(key=lambda x: x['final_speed'], reverse=True)
        return breakdown
