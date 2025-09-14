"""
Battle Validation Moves - Move validation logic
===============================================
Move validation functionality extracted from battle_validation.py
to comply with 300-line limit.
"""

import logging
from typing import List, Optional, Dict, Any, Tuple, TYPE_CHECKING
from engine.systems.monster_instance import MonsterInstance

if TYPE_CHECKING:
    from engine.systems.moves import Move
    from engine.systems.battle.turn_logic import BattleAction

logger = logging.getLogger(__name__)


class BattleValidationMoves:
    """
    Move validation functionality.
    Handles move-specific validation logic.
    """
    
    @staticmethod
    def validate_move(move: Dict[str, Any], monster: MonsterInstance) -> Tuple[bool, List[str]]:
        """
        CONSOLIDATED Move validation - Single source of truth for all move validation.
        Consolidated from battle_validation_moves.py, turn_validator.py, and skills_dqm_integrated.py.
        
        Args:
            move: Move dictionary or Move object
            monster: Monster using the move
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        try:
            errors = []
            
            # Check if move exists
            if not move:
                errors.append("No move provided")
                return False, errors
            
            # Check if monster exists
            if not monster:
                errors.append("No monster provided")
                return False, errors
            
            # Check if monster is conscious
            if hasattr(monster, 'current_hp') and monster.current_hp <= 0:
                errors.append("Monster is fainted")
                return False, errors
            
            # Check move power
            if hasattr(move, 'power'):
                if move.power < 0:
                    errors.append("Move power cannot be negative")
                    return False, errors
            elif isinstance(move, dict) and 'power' in move:
                if move['power'] < 0:
                    errors.append("Move power cannot be negative")
                    return False, errors
            
            # Check move accuracy
            if hasattr(move, 'accuracy'):
                if not (0 <= move.accuracy <= 100):
                    errors.append("Move accuracy must be between 0 and 100")
                    return False, errors
            elif isinstance(move, dict) and 'accuracy' in move:
                if not (0 <= move['accuracy'] <= 100):
                    errors.append("Move accuracy must be between 0 and 100")
                    return False, errors
            
            # Check MP requirements
            if hasattr(move, 'mp_cost'):
                if move.mp_cost < 0:
                    errors.append("MP cost cannot be negative")
                    return False, errors
                
                if hasattr(monster, 'current_mp') and monster.current_mp < move.mp_cost:
                    errors.append("Not enough MP to use this move")
                    return False, errors
            elif isinstance(move, dict) and 'mp_cost' in move:
                if move['mp_cost'] < 0:
                    errors.append("MP cost cannot be negative")
                    return False, errors
                
                if hasattr(monster, 'current_mp') and monster.current_mp < move['mp_cost']:
                    errors.append("Not enough MP to use this move")
                    return False, errors
            
            return True, errors
            
        except Exception as e:
            logger.error(f"Move validation failed: {e}")
            return False, [f"Validation error: {e}"]
    
    @staticmethod
    def validate_move_execution(action: 'BattleAction', state: 'BattleState') -> Tuple[bool, str]:
        """
        Validate move execution - checks if move can be executed.
        
        Args:
            action: Battle action to validate
            state: Current battle state
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check if action exists
            if not action:
                return False, "No action provided"
            
            # Check if actor exists and is conscious
            if not action.actor:
                return False, "No actor specified"
            
            if hasattr(action.actor, 'current_hp') and action.actor.current_hp <= 0:
                return False, "Actor is fainted"
            
            # Check if move exists
            if not action.move:
                return False, "No move specified"
            
            # Check MP requirements
            if hasattr(action.move, 'mp_cost'):
                if action.actor.current_mp < action.move.mp_cost:
                    return False, "Not enough MP to use this move"
            
            # Check if target is valid
            if action.target and hasattr(action.target, 'current_hp') and action.target.current_hp <= 0:
                return False, "Target is fainted"
            
            # Check move targeting
            if hasattr(action.move, 'targeting'):
                if action.move.targeting == 'enemy' and not action.target:
                    return False, "Move requires enemy target"
                
                if action.move.targeting == 'ally' and not action.target:
                    return False, "Move requires ally target"
            
            # Check move accuracy
            if hasattr(action.move, 'accuracy'):
                if action.move.accuracy < 100:
                    # This would be handled by RNG in actual execution
                    pass
            
            return True, "Move execution valid"
            
        except Exception as e:
            logger.error(f"Move execution validation failed: {e}")
            return False, f"Validation error: {e}"
    
    @staticmethod
    def get_available_moves_for_monster(monster: MonsterInstance) -> List[Dict[str, Any]]:
        """
        CONSOLIDATED Get available moves - Single source of truth.
        Consolidated from battle_validation_moves.py and skills_dqm_integrated.py.
        
        Args:
            monster: Monster to get moves for
            
        Returns:
            List of available move dictionaries
        """
        try:
            available_moves = monster.get_available_moves()
            move_list = []
            
            for move in available_moves:
                if hasattr(move, 'id'):
                    move_dict = {
                        'id': move.id,
                        'name': move.name,
                        'power': getattr(move, 'power', 0),
                        'accuracy': getattr(move, 'accuracy', 100),
                        'mp_cost': getattr(move, 'mp_cost', 0),
                        'type': getattr(move, 'type', 'Normal'),
                        'category': getattr(move, 'category', 'Physical'),
                        'description': getattr(move, 'description', '')
                    }
                    move_list.append(move_dict)
                elif isinstance(move, dict):
                    move_list.append(move)
            
            return move_list
            
        except Exception as e:
            logger.error(f"Failed to get available moves: {e}")
            return []
    
    @staticmethod
    def validate_move_availability(move: Dict[str, Any], monster: MonsterInstance) -> bool:
        """
        Validate if move is available for monster.
        
        Args:
            move: Move to check
            monster: Monster to check for
            
        Returns:
            True if move is available
        """
        try:
            # Check if monster has the move
            available_moves = BattleValidationMoves.get_available_moves_for_monster(monster)
            move_id = move.get('id') if isinstance(move, dict) else getattr(move, 'id', None)
            
            if not move_id:
                return False
            
            for available_move in available_moves:
                if isinstance(available_move, dict):
                    if available_move.get('id') == move_id:
                        return True
                elif hasattr(available_move, 'id'):
                    if available_move.id == move_id:
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Move availability validation failed: {e}")
            return False
    
    @staticmethod
    def validate_move_targeting(move: Dict[str, Any], target: Optional[MonsterInstance]) -> Tuple[bool, str]:
        """
        Validate move targeting requirements.
        
        Args:
            move: Move to validate
            target: Target monster
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check if move requires target
            targeting = move.get('targeting') if isinstance(move, dict) else getattr(move, 'targeting', None)
            
            if targeting == 'enemy' and not target:
                return False, "Move requires enemy target"
            
            if targeting == 'ally' and not target:
                return False, "Move requires ally target"
            
            if targeting == 'self' and target:
                return False, "Move targets self, no target should be specified"
            
            return True, "Targeting valid"
            
        except Exception as e:
            logger.error(f"Move targeting validation failed: {e}")
            return False, f"Validation error: {e}"