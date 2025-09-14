"""
Battle Validator Facade - Emergency Split
=========================================
Facade to maintain compatibility while splitting the 898-line battle_validation.py
"""

import logging
from typing import List, Optional, Dict, Any, Tuple, TYPE_CHECKING
from engine.systems.monster_instance import MonsterInstance

if TYPE_CHECKING:
    from engine.systems.battle.turn_logic import BattleAction

logger = logging.getLogger(__name__)


class BattleValidator:
    """
    EMERGENCY FACADE - Simplified BattleValidator to comply with 300-line limit.
    This replaces the 898-line monolithic battle_validation.py
    """
    
    @staticmethod
    def validate_battle_state(player_active: Optional[MonsterInstance],
                             enemy_active: Optional[MonsterInstance],
                             player_team: List[MonsterInstance],
                             enemy_team: List[MonsterInstance]) -> bool:
        """
        Validates the current battle state.
        
        Args:
            player_active: Active player monster
            enemy_active: Active enemy monster
            player_team: Player's team
            enemy_team: Enemy's team
            
        Returns:
            True if the battle state is valid, False otherwise
        """
        try:
            # Check if active monsters exist
            if not player_active or not enemy_active:
                logger.error("Active monsters are missing!")
                return False
            
            # Validate monster stats
            if not BattleValidator._validate_monster_stats(player_active):
                logger.error(f"Invalid stats for player monster: {player_active.name}")
                return False
            
            if not BattleValidator._validate_monster_stats(enemy_active):
                logger.error(f"Invalid stats for enemy monster: {enemy_active.name}")
                return False
            
            # Check if teams have valid monsters
            if not player_team or len(player_team) == 0:
                logger.error("Player team is empty!")
                return False
            
            if not enemy_team or len(enemy_team) == 0:
                logger.error("Enemy team is empty!")
                return False
            
            # Check if active monsters are in their respective teams
            if player_active not in player_team:
                logger.error("Player active monster not in player team!")
                return False
            
            if enemy_active not in enemy_team:
                logger.error("Enemy active monster not in enemy team!")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Battle state validation failed: {e}")
            return False
    
    @staticmethod
    def _validate_monster_stats(monster: MonsterInstance) -> bool:
        """Validate monster stats."""
        try:
            if not monster:
                return False
            
            # Check HP
            if not hasattr(monster, 'current_hp') or monster.current_hp < 0:
                return False
            
            if not hasattr(monster, 'max_hp') or monster.max_hp <= 0:
                return False
            
            if monster.current_hp > monster.max_hp:
                return False
            
            # Check stats
            if not hasattr(monster, 'stats'):
                return False
            
            required_stats = ['atk', 'def', 'spd', 'hp']
            for stat in required_stats:
                if stat not in monster.stats or monster.stats[stat] <= 0:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Monster stats validation failed: {e}")
            return False
    
    @staticmethod
    def validate_action(action: 'BattleAction', 
                       player_active: Optional[MonsterInstance],
                       enemy_active: Optional[MonsterInstance]) -> Tuple[bool, List[str]]:
        """
        Validates a battle action.
        
        Args:
            action: The action to validate
            player_active: Active player monster
            enemy_active: Active enemy monster
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        try:
            if not action:
                errors.append("Action is None")
                return False, errors
            
            # Check actor
            if not hasattr(action, 'actor') or not action.actor:
                errors.append("No actor specified")
                return False, errors
            
            # Check if actor can act
            if action.actor.current_hp <= 0:
                errors.append(f"{action.actor.name} is fainted and cannot act")
                return False, errors
            
            # Check action type specific requirements
            if hasattr(action, 'action_type'):
                if action.action_type.name == 'ATTACK':
                    if not hasattr(action, 'move') or not action.move:
                        errors.append("No move specified for attack")
                        return False, errors
                    
                    if not hasattr(action, 'target') or not action.target:
                        errors.append("No target specified for attack")
                        return False, errors
                
                elif action.action_type.name == 'SWITCH':
                    if not hasattr(action, 'switch_to') or not action.switch_to:
                        errors.append("No switch target specified")
                        return False, errors
            
            return True, errors
            
        except Exception as e:
            errors.append(f"Action validation error: {e}")
            return False, errors
    
    @staticmethod
    def validate_team(team: List[MonsterInstance], team_name: str = "team") -> Tuple[bool, List[str]]:
        """
        Validates a team of monsters.
        
        Args:
            team: List of monsters
            team_name: Name of the team for error messages
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        try:
            if not team or len(team) == 0:
                errors.append(f"{team_name} is empty")
                return False, errors
            
            # Check each monster in the team
            for i, monster in enumerate(team):
                if not monster:
                    errors.append(f"{team_name}[{i}] is None")
                    continue
                
                if not BattleValidator._validate_monster_stats(monster):
                    errors.append(f"{team_name}[{i}] ({monster.name}) has invalid stats")
            
            return len(errors) == 0, errors
            
        except Exception as e:
            errors.append(f"Team validation error: {e}")
            return False, errors
    
    @staticmethod
    def validate_move(move: Dict[str, Any], monster: MonsterInstance) -> Tuple[bool, List[str]]:
        """
        Validates a move for a monster.
        
        Args:
            move: Move dictionary
            monster: Monster using the move
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        try:
            if not move:
                errors.append("Move is None")
                return False, errors
            
            # Check required move properties
            required_props = ['name', 'power']
            for prop in required_props:
                if prop not in move:
                    errors.append(f"Move missing required property: {prop}")
            
            # Check power value
            if 'power' in move and move['power'] <= 0:
                errors.append("Move power must be positive")
            
            # Check accuracy
            if 'accuracy' in move and (move['accuracy'] < 0 or move['accuracy'] > 100):
                errors.append("Move accuracy must be between 0 and 100")
            
            return len(errors) == 0, errors
            
        except Exception as e:
            errors.append(f"Move validation error: {e}")
            return False, errors
    
    @staticmethod
    def get_validation_summary(validation_results: List[Tuple[bool, List[str]]]) -> Dict[str, Any]:
        """
        Get a summary of validation results.
        
        Args:
            validation_results: List of (is_valid, errors) tuples
            
        Returns:
            Dictionary with validation summary
        """
        total_validations = len(validation_results)
        successful_validations = sum(1 for is_valid, _ in validation_results if is_valid)
        failed_validations = total_validations - successful_validations
        
        all_errors = []
        for _, errors in validation_results:
            all_errors.extend(errors)
        
        return {
            'total_validations': total_validations,
            'successful_validations': successful_validations,
            'failed_validations': failed_validations,
            'success_rate': (successful_validations / total_validations * 100) if total_validations > 0 else 0,
            'total_errors': len(all_errors),
            'errors': all_errors
        }
