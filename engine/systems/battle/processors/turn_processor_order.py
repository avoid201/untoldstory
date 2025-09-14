"""
Turn Processor Order - Turn Order Calculation
============================================
Turn order calculation with DQM formulas and speed-based ordering.
Split from turn_processor.py to comply with 300-line limit.
"""

import logging
import random
from typing import Dict, Any, List, Tuple, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from engine.systems.battle.battle_state import BattleState
    from engine.systems.monster_instance import MonsterInstance
    from engine.systems.battle.turn_logic import BattleAction, ActionType

logger = logging.getLogger(__name__)


class TurnProcessorOrder:
    """
    Turn order calculation logic.
    Handles DQM-style turn order calculation with speed and priority.
    """
    
    def __init__(self, battle_state: 'BattleState' = None):
        """Initialize turn order processor."""
        self.state = battle_state
        self._rng = random.Random()
        logger.info("TurnProcessorOrder initialized")
    
    def calculate_turn_order(self, actions: List['BattleAction']) -> List[Tuple[int, 'BattleAction']]:
        """
        DELEGATES to consolidated TurnOrder.calculate_turn_order().
        This method maintains compatibility while using the single source of truth.
        
        Args:
            actions: List of battle actions
            
        Returns:
            List of (speed_roll, action) tuples sorted by turn order
        """
        # Import consolidated turn order calculation
        from ..turn_logic import TurnOrder
        
        # Use consolidated implementation
        sorted_actions = TurnOrder().calculate_turn_order(actions)
        
        # Convert to expected format for compatibility
        turn_order = []
        for action in sorted_actions:
            if not action or not action.actor:
                continue
            
            # Calculate speed roll for compatibility
            base_speed = action.actor.stats.get('spd', 50) if action.actor.stats else 50
            speed_roll = base_speed + self._rng.randint(0, 255)
            
            turn_order.append((speed_roll, action))
        
        return turn_order
    
    def _get_action_priority(self, action: 'BattleAction') -> int:
        """
        Get action priority for turn order calculation.
        
        Args:
            action: Battle action
            
        Returns:
            Priority value (higher = goes first)
        """
        try:
            # Default priority
            priority = 0
            
            # Check for move priority
            if hasattr(action, 'move') and action.move:
                if hasattr(action.move, 'priority'):
                    priority += action.move.priority
                elif hasattr(action.move, 'speed_priority'):
                    priority += action.move.speed_priority
            
            # Action type priorities
            if hasattr(action, 'action_type'):
                action_type = action.action_type
                if hasattr(action_type, 'name'):
                    if action_type.name == 'FLEE':
                        priority += 6
                    elif action_type.name == 'SWITCH':
                        priority += 5
                    elif action_type.name == 'ITEM':
                        priority += 4
                    elif action_type.name == 'TAME':
                        priority += 3
                    elif action_type.name == 'ATTACK':
                        priority += 1
                    elif action_type.name == 'SCOUT':
                        priority += 2
            
            return priority
            
        except Exception as e:
            logger.error(f"Error getting action priority: {e}")
            return 0
    
    def calculate_speed_with_modifiers(self, monster: 'MonsterInstance') -> int:
        """
        Calculate effective speed with stat stage modifiers.
        
        Args:
            monster: Monster to calculate speed for
            
        Returns:
            Effective speed value
        """
        try:
            if not monster or not hasattr(monster, 'stats'):
                return 50
            
            base_speed = monster.stats.get('spd', 50)
            
            # Apply stat stage modifiers
            if hasattr(monster, 'stat_stages') and 'spd' in monster.stat_stages:
                stage = monster.stat_stages['spd']
                if stage > 0:
                    multiplier = (2 + stage) / 2
                else:
                    multiplier = 2 / (2 - stage)
                base_speed = int(base_speed * multiplier)
            
            # Apply status effect modifiers
            if hasattr(monster, 'status') and monster.status:
                if hasattr(monster.status, 'name'):
                    if monster.status.name == 'PARALYSIS':
                        base_speed = int(base_speed * 0.5)
            
            return max(1, base_speed)  # Minimum speed of 1
            
        except Exception as e:
            logger.error(f"Error calculating speed with modifiers: {e}")
            return 50
    
    def get_turn_order_breakdown(self, actions: List['BattleAction']) -> List[Dict[str, Any]]:
        """
        Get detailed breakdown of turn order calculation.
        
        Args:
            actions: List of battle actions
            
        Returns:
            List of turn order details
        """
        breakdown = []
        
        for action in actions:
            if not action or not hasattr(action, 'actor'):
                continue
            
            actor = action.actor
            priority = self._get_action_priority(action)
            base_speed = self.calculate_speed_with_modifiers(actor)
            speed_roll = base_speed + self._rng.randint(0, 255)
            
            # Player advantage
            player_advantage = 1 if actor == self.state.player_active else 0
            final_speed = speed_roll + player_advantage
            
            breakdown.append({
                'actor': actor.name if hasattr(actor, 'name') else str(actor),
                'priority': priority,
                'base_speed': base_speed,
                'speed_roll': speed_roll,
                'player_advantage': player_advantage,
                'final_speed': final_speed,
                'action_type': action.action_type.name if hasattr(action, 'action_type') else 'UNKNOWN'
            })
        
        # Sort by final speed (descending)
        breakdown.sort(key=lambda x: x['final_speed'], reverse=True)
        return breakdown
    
    def validate_turn_order(self, turn_order: List[Tuple[int, 'BattleAction']]) -> Tuple[bool, str]:
        """
        Validate turn order for consistency.
        
        Args:
            turn_order: Calculated turn order
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            if not turn_order:
                return False, "Empty turn order"
            
            # Check for duplicate actions
            action_ids = []
            for speed, action in turn_order:
                if hasattr(action, 'id'):
                    if action.id in action_ids:
                        return False, f"Duplicate action ID: {action.id}"
                    action_ids.append(action.id)
            
            # Check for valid speed values
            for speed, action in turn_order:
                if speed < 0:
                    return False, f"Invalid speed value: {speed}"
            
            return True, "Turn order is valid"
            
        except Exception as e:
            logger.error(f"Error validating turn order: {e}")
            return False, f"Validation error: {e}"
    
    def get_priority_breakdown(self) -> Dict[str, int]:
        """
        Get priority breakdown for different action types.
        
        Returns:
            Dictionary of action type priorities
        """
        return {
            'FLEE': 6,
            'SWITCH': 5,
            'ITEM': 4,
            'TAME': 3,
            'SCOUT': 2,
            'ATTACK': 1,
            'PASS': 0
        }
