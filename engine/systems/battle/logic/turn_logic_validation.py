"""
Turn Logic Validation - Battle action validation logic
=====================================================
Validation logic for battle actions and turn order.
"""

from typing import List, Dict, Any, TYPE_CHECKING
import logging

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from engine.systems.monster_instance import MonsterInstance
    from .turn_logic_core import BattleAction


def validate_turn_order(actions: List['BattleAction']) -> tuple[bool, List[str]]:
    """
    Validate turn order for battle actions.
    
    Args:
        actions: List of battle actions
        
    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []
    
    try:
        if not actions:
            errors.append("No actions provided")
            return False, errors
        
        # Check for duplicate actors
        actors = [action.actor for action in actions if action and action.actor]
        if len(actors) != len(set(actors)):
            errors.append("Duplicate actors in turn order")
        
        # Check for invalid actions
        for i, action in enumerate(actions):
            if not action:
                errors.append(f"Action at index {i} is None")
                continue
            
            if not action.actor:
                errors.append(f"Action at index {i} has no actor")
                continue
            
            # Check if actor is fainted
            if hasattr(action.actor, 'current_hp') and action.actor.current_hp <= 0:
                errors.append(f"Actor {action.actor.name} is fainted but has action")
        
        return len(errors) == 0, errors
        
    except Exception as e:
        logger.error(f"Error validating turn order: {e}")
        return False, [f"Validation error: {e}"]


def validate_action_sequence(actions: List['BattleAction']) -> tuple[bool, List[str]]:
    """
    Validate sequence of battle actions.
    
    Args:
        actions: List of battle actions in sequence
        
    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []
    
    try:
        if not actions:
            errors.append("No actions in sequence")
            return False, errors
        
        # Check for valid action types
        valid_action_types = {'attack', 'switch', 'item', 'run', 'tame'}
        for i, action in enumerate(actions):
            if not action:
                continue
            
            action_type = getattr(action.action_type, 'value', str(action.action_type))
            if action_type not in valid_action_types:
                errors.append(f"Invalid action type at index {i}: {action_type}")
        
        # Check for conflicting actions (e.g., multiple switches by same actor)
        actor_actions = {}
        for i, action in enumerate(actions):
            if not action or not action.actor:
                continue
            
            actor_id = getattr(action.actor, 'id', id(action.actor))
            if actor_id not in actor_actions:
                actor_actions[actor_id] = []
            actor_actions[actor_id].append((i, action))
        
        for actor_id, actor_action_list in actor_actions.items():
            if len(actor_action_list) > 1:
                # Check for conflicting action types
                action_types = [action.action_type for _, action in actor_action_list]
                if len(set(action_types)) > 1:
                    errors.append(f"Actor {actor_id} has conflicting action types: {action_types}")
        
        return len(errors) == 0, errors
        
    except Exception as e:
        logger.error(f"Error validating action sequence: {e}")
        return False, [f"Validation error: {e}"]


def get_action_priority_score(action: 'BattleAction') -> int:
    """
    Get priority score for action (higher = goes first).
    
    Args:
        action: BattleAction to score
        
    Returns:
        Priority score
    """
    try:
        if not action or not action.actor:
            return 0
        
        # Base priority from move
        base_priority = action.get_priority() if hasattr(action, 'get_priority') else 0
        
        # Speed bonus
        speed = getattr(action.actor, 'stats', {}).get('spd', 50)
        speed_bonus = speed // 10  # Convert speed to priority bonus
        
        # Status effect penalties
        status_penalty = 0
        if hasattr(action.actor, 'status') and action.actor.status:
            status_name = getattr(action.actor.status, 'name', '')
            if status_name == 'PARALYSIS':
                status_penalty = 50
            elif status_name == 'SLEEP':
                status_penalty = 100
            elif status_name == 'FREEZE':
                status_penalty = 75
        
        return base_priority + speed_bonus - status_penalty
        
    except Exception as e:
        logger.error(f"Error calculating action priority score: {e}")
        return 0
