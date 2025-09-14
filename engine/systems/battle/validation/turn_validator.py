"""
Turn Validator - Specialized Turn Validation
===========================================
DELEGATES to BattleValidationCore for consolidated validation.
Contains specialized turn-specific validation methods.

DELEGATED FUNCTIONS (to BattleValidationCore):
- validate_turn_action() - DELEGATES to validate_action()
- validate_move_execution() - DELEGATES to consolidated implementation

SPECIALIZED FUNCTIONS (not duplicated elsewhere):
- validate_turn_order() - Turn-specific validation
- validate_battle_state() - Turn-specific validation
- get_validation_suggestions() - Turn-specific functionality
- _has_item() - Turn-specific helper
- _can_switch_to() - Turn-specific helper
"""

import logging
from typing import Tuple, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from engine.systems.battle.battle_state import BattleState
    from engine.systems.battle.turn_logic import BattleAction
    from engine.systems.monster_instance import MonsterInstance

logger = logging.getLogger(__name__)


class TurnValidator:
    """
    Specialized validator for turn-specific actions.
    DELEGATES to BattleValidator for core validation logic.
    """
    
    @staticmethod
    def validate_turn_action(action: 'BattleAction', state: 'BattleState') -> Tuple[bool, str]:
        """
        Validate action before turn execution.
        DELEGATES to BattleValidator for core validation.
        
        Args:
            action: The battle action to validate
            state: Current battle state
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # DELEGATE to BattleValidationCore for core validation
            from .battle_validation_core import BattleValidationCore
            
            is_valid, errors = BattleValidationCore.validate_action(
                action, 
                state.player_active, 
                state.enemy_active
            )
            
            if not is_valid:
                return False, errors[0] if errors else "Validation failed"
            
            # Additional turn-specific validation
            # Check actor is alive
            if not action.actor or action.actor.current_hp <= 0:
                return False, "Actor is fainted"
            
            # Check target is valid (if specified)
            if action.target and action.target.current_hp <= 0:
                return False, "Target is already fainted"
            
            # Check MP for moves
            if action.move and hasattr(action.move, 'mp_cost'):
                if action.move.mp_cost > action.actor.current_mp:
                    return False, "Not enough MP"
            
            # Check item availability
            if hasattr(action.action_type, 'name') and action.action_type.name == "ITEM":
                if not TurnValidator._has_item(action.item_id, state):
                    return False, "Item not available"
            
            # Check switch target is valid
            if hasattr(action.action_type, 'name') and action.action_type.name == "SWITCH":
                if not TurnValidator._can_switch_to(action.switch_to, state):
                    return False, "Cannot switch to that monster"
            
            # Check if actor has already acted this turn
            if hasattr(action.actor, 'has_acted_this_turn') and action.actor.has_acted_this_turn:
                return False, "Actor has already acted this turn"
            
            return True, "Valid"
            
        except Exception as e:
            logger.error(f"Action validation failed: {e}")
            return False, f"Validation error: {str(e)}"
    
    @staticmethod
    def validate_turn_order(actions: list, state: 'BattleState') -> Tuple[bool, str]:
        """
        Validate turn order for multiple actions.
        
        Args:
            actions: List of battle actions
            state: Current battle state
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            if not actions:
                return False, "No actions provided"
            
            # Check each action
            for action in actions:
                is_valid, error = TurnValidator.validate_turn_action(action, state)
                if not is_valid:
                    return False, f"Invalid action: {error}"
            
            # Check for duplicate actors
            actors = [action.actor for action in actions if action.actor]
            if len(actors) != len(set(actors)):
                return False, "Duplicate actors in turn"
            
            return True, "Valid turn order"
            
        except Exception as e:
            logger.error(f"Turn order validation failed: {e}")
            return False, f"Turn order validation error: {str(e)}"
    
    @staticmethod
    def _has_item(item_id: str, state: 'BattleState') -> bool:
        """Check if item is available."""
        try:
            # This would check against player's inventory
            # For now, return True as placeholder
            return True
        except Exception as e:
            logger.error(f"Item check failed: {e}")
            return False
    
    @staticmethod
    def _can_switch_to(monster: 'MonsterInstance', state: 'BattleState') -> bool:
        """Check if can switch to specified monster."""
        try:
            if not monster:
                return False
            
            # Check if monster is in player team
            if monster not in state.player_team:
                return False
            
            # Check if monster is alive
            if monster.current_hp <= 0:
                return False
            
            # Check if monster is already active
            if monster == state.player_active:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Switch validation failed: {e}")
            return False
    
    @staticmethod
    def validate_battle_state(state: 'BattleState') -> Tuple[bool, str]:
        """
        Validate overall battle state.
        
        Args:
            state: Current battle state
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check if battle is still active
            if state.battle_ended:
                return False, "Battle has already ended"
            
            # Check if active monsters exist
            if not state.player_active or not state.enemy_active:
                return False, "Missing active monsters"
            
            # Check if active monsters are alive
            if state.player_active.current_hp <= 0:
                return False, "Player monster is fainted"
            
            if state.enemy_active.current_hp <= 0:
                return False, "Enemy monster is fainted"
            
            # Check if teams have living monsters
            player_alive = any(monster.current_hp > 0 for monster in state.player_team)
            enemy_alive = any(monster.current_hp > 0 for monster in state.enemy_team)
            
            if not player_alive:
                return False, "Player team is defeated"
            
            if not enemy_alive:
                return False, "Enemy team is defeated"
            
            return True, "Valid battle state"
            
        except Exception as e:
            logger.error(f"Battle state validation failed: {e}")
            return False, f"Battle state validation error: {str(e)}"
    
    @staticmethod
    def validate_move_execution(action: 'BattleAction', state: 'BattleState') -> Tuple[bool, str]:
        """
        DELEGATES to consolidated BattleValidationCore.validate_move_execution().
        This method maintains compatibility while using the single source of truth.
        """
        from .battle_validation_core import BattleValidationCore
        return BattleValidationCore.validate_move_execution(action, state)
    
    @staticmethod
    def get_validation_suggestions(action: 'BattleAction', state: 'BattleState') -> list:
        """
        Get suggestions for invalid actions.
        
        Args:
            action: The battle action
            state: Current battle state
            
        Returns:
            List of suggestion strings
        """
        suggestions = []
        
        try:
            # Check if actor is fainted
            if not action.actor or action.actor.current_hp <= 0:
                suggestions.append("Switch to a living monster")
                return suggestions
            
            # Check MP issues
            if action.move and hasattr(action.move, 'mp_cost'):
                if action.move.mp_cost > action.actor.current_mp:
                    suggestions.append("Use a move with lower MP cost")
                    suggestions.append("Use an item to restore MP")
            
            # Check item issues
            if hasattr(action.action_type, 'name') and action.action_type.name == "ITEM":
                if not TurnValidator._has_item(action.item_id, state):
                    suggestions.append("Use a different item")
                    suggestions.append("Attack instead")
            
            # Check switch issues
            if hasattr(action.action_type, 'name') and action.action_type.name == "SWITCH":
                if not TurnValidator._can_switch_to(action.switch_to, state):
                    suggestions.append("Switch to a different monster")
                    suggestions.append("Attack instead")
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Failed to get validation suggestions: {e}")
            return ["Try a different action"]
