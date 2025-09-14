"""
Battle Validation Core - Core validation logic
==============================================
Core battle validation functionality extracted from battle_validation.py
to comply with 300-line limit.
"""

import logging
from typing import List, Optional, Dict, Any, Tuple, TYPE_CHECKING
from engine.systems.monster_instance import MonsterInstance

if TYPE_CHECKING:
    from engine.systems.battle.turn_logic import BattleAction
    from engine.systems.battle.battle_state import BattleState

logger = logging.getLogger(__name__)


class BattleValidationCore:
    """
    Core battle validation functionality.
    Handles basic battle state and action validation.
    """
    
    @staticmethod
    def validate_battle_state(player_active: Optional[MonsterInstance],
                             enemy_active: Optional[MonsterInstance],
                             player_team: List[MonsterInstance],
                             enemy_team: List[MonsterInstance]) -> bool:
        """Validate battle state - basic validation."""
        try:
            # Check if teams exist
            if not player_team or not enemy_team:
                logger.warning("Empty teams detected")
                return False
            
            # Check if active monsters exist
            if not player_active or not enemy_active:
                logger.warning("Missing active monsters")
                return False
            
            # Check if active monsters are in their respective teams
            if player_active not in player_team:
                logger.warning("Player active monster not in team")
                return False
            
            if enemy_active not in enemy_team:
                logger.warning("Enemy active monster not in team")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Battle state validation failed: {e}")
            return False
    
    @staticmethod
    def validate_action(action: 'BattleAction', 
                       player_active: Optional[MonsterInstance],
                       enemy_active: Optional[MonsterInstance]) -> Tuple[bool, List[str]]:
        """Validate battle action - basic validation."""
        try:
            errors = []
            
            # Check if action exists
            if not action:
                errors.append("No action provided")
                return False, errors
            
            # Check if actor exists
            if not action.actor:
                errors.append("No actor specified")
                return False, errors
            
            # Check if actor is conscious
            if hasattr(action.actor, 'current_hp') and action.actor.current_hp <= 0:
                errors.append("Actor is fainted")
                return False, errors
            
            # Check if target is valid for action type
            if action.action_type in ['ATTACK', 'SPECIAL']:
                if not action.target:
                    errors.append("Attack action requires target")
                    return False, errors
                
                if hasattr(action.target, 'current_hp') and action.target.current_hp <= 0:
                    errors.append("Target is fainted")
                    return False, errors
            
            return True, errors
            
        except Exception as e:
            logger.error(f"Action validation failed: {e}")
            return False, [f"Validation error: {e}"]
    
    @staticmethod
    def validate_action_with_recovery(action: 'BattleAction', state: 'BattleState') -> Tuple[bool, List[str], List[str]]:
        """Validate action with recovery suggestions."""
        try:
            is_valid, errors = BattleValidationCore.validate_action(
                action, state.player_active, state.enemy_active
            )
            
            recovery_suggestions = []
            
            if not is_valid:
                # Generate recovery suggestions based on errors
                for error in errors:
                    if "fainted" in error.lower():
                        recovery_suggestions.append("Switch to a conscious monster")
                    elif "no target" in error.lower():
                        recovery_suggestions.append("Select a valid target")
                    elif "no action" in error.lower():
                        recovery_suggestions.append("Select a valid action")
            
            return is_valid, errors, recovery_suggestions
            
        except Exception as e:
            logger.error(f"Action validation with recovery failed: {e}")
            return False, [f"Validation error: {e}"], ["Check battle state"]
    
    @staticmethod
    def validate_team_composition(team: List[MonsterInstance]) -> Tuple[bool, List[str]]:
        """Validate team composition."""
        try:
            errors = []
            
            # Check team size
            if len(team) == 0:
                errors.append("Team is empty")
                return False, errors
            
            if len(team) > 6:
                errors.append("Team has too many monsters (max 6)")
                return False, errors
            
            # Check for conscious monsters
            conscious_monsters = [m for m in team if hasattr(m, 'current_hp') and m.current_hp > 0]
            if len(conscious_monsters) == 0:
                errors.append("No conscious monsters in team")
                return False, errors
            
            return True, errors
            
        except Exception as e:
            logger.error(f"Team composition validation failed: {e}")
            return False, [f"Validation error: {e}"]
    
    @staticmethod
    def validate_battle_phase(phase: str, required_phase: str) -> bool:
        """Validate battle phase."""
        try:
            return phase == required_phase
        except Exception as e:
            logger.error(f"Phase validation failed: {e}")
            return False
    
    @staticmethod
    def validate_monster_instance(monster: MonsterInstance) -> Tuple[bool, List[str]]:
        """Validate monster instance."""
        try:
            errors = []
            
            # Check if monster exists
            if not monster:
                errors.append("Monster instance is None")
                return False, errors
            
            # Check required attributes
            required_attrs = ['name', 'level', 'current_hp', 'max_hp']
            for attr in required_attrs:
                if not hasattr(monster, attr):
                    errors.append(f"Missing required attribute: {attr}")
                    return False, errors
            
            # Check HP values
            if hasattr(monster, 'current_hp') and hasattr(monster, 'max_hp'):
                if monster.current_hp < 0:
                    errors.append("Current HP cannot be negative")
                    return False, errors
                
                if monster.max_hp <= 0:
                    errors.append("Max HP must be positive")
                    return False, errors
                
                if monster.current_hp > monster.max_hp:
                    errors.append("Current HP cannot exceed max HP")
                    return False, errors
            
            # Check level
            if hasattr(monster, 'level'):
                if monster.level < 1 or monster.level > 100:
                    errors.append("Level must be between 1 and 100")
                    return False, errors
            
            return True, errors
            
        except Exception as e:
            logger.error(f"Monster instance validation failed: {e}")
            return False, [f"Validation error: {e}"]