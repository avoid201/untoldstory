"""
Turn Logic Actions - Battle action creation and management
=========================================================
Battle action creation, validation, and management logic.
"""

from typing import Dict, Any, Optional, TYPE_CHECKING
import logging

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from engine.systems.monster_instance import MonsterInstance
    from engine.systems.moves import Move
    from .turn_logic_core import BattleAction, ActionType


def create_battle_action_from_dict(action_data: Dict[str, Any]) -> Optional['BattleAction']:
    """
    Create a BattleAction from dictionary data.
    
    Args:
        action_data: Dictionary containing action data
        
    Returns:
        BattleAction object or None if creation failed
    """
    try:
        from .turn_logic_core import ActionType, BattleAction
        
        # Extract required fields
        action_type_str = action_data.get('action_type', 'attack')
        actor = action_data.get('actor')
        target = action_data.get('target')
        move = action_data.get('move')
        switch_to = action_data.get('switch_to')
        item_id = action_data.get('item_id')
        
        # Convert action type string to enum with proper error handling
        action_type = ActionType.safe_convert(action_type_str)
        
        # Validate actor
        if not actor:
            logger.error("No actor specified for battle action")
            return None
        
        # Create move if not provided for attack actions
        if action_type == ActionType.ATTACK and not move:
            move = _create_default_attack_move()
        
        return BattleAction(
            action_type=action_type,
            actor=actor,
            target=target,
            move=move,
            switch_to=switch_to,
            item_id=item_id
        )
        
    except Exception as e:
        logger.error(f"Error creating BattleAction from dict: {e}")
        return None


def validate_battle_action(action: 'BattleAction') -> tuple[bool, str]:
    """
    Validate a battle action.
    
    Args:
        action: BattleAction to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        if not action:
            return False, "Action is None"
        
        if not action.actor:
            return False, "No actor specified"
        
        if action.action_type == ActionType.ATTACK and not action.move:
            return False, "Attack action requires a move"
        
        if action.action_type == ActionType.SWITCH and not action.switch_to:
            return False, "Switch action requires switch_to target"
        
        if action.action_type == ActionType.ITEM and not action.item_id:
            return False, "Item action requires item_id"
        
        return True, "Action is valid"
        
    except Exception as e:
        logger.error(f"Error validating battle action: {e}")
        return False, f"Validation error: {e}"


def _create_default_attack_move():
    """Create a default attack move for actions without specific moves."""
    try:
        from engine.systems.moves import Move, MoveCategory, MoveTarget, MoveEffect, EffectKind
        
        return Move(
            id="default_attack",
            name="Angriff",
            type="Normal",
            category=MoveCategory.PHYSICAL,
            power=40,
            accuracy=100,
            priority=0,
            targeting=MoveTarget.ENEMY,
            effects=[MoveEffect(kind=EffectKind.DAMAGE, power=40)],
            description="Standard-Angriff",
            contact=True,
            sound_based=False,
            punching=False,
            biting=False,
            pulse=False,
            multi_hit=None,
            drain_percent=0,
            recoil_percent=0,
            multi_hit_min=1,
            multi_hit_max=1
        )
    except Exception as e:
        logger.error(f"Error creating default attack move: {e}")
        return None
