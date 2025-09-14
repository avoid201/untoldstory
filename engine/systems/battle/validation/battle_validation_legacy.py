"""
Battle Validation Legacy - Legacy compatibility methods
=====================================================
Legacy methods for backward compatibility with battle validation.
"""

from typing import Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from engine.systems.monster_instance import MonsterInstance

from .battle_validation_core import BattleValidationCore
from .battle_validation_moves import BattleValidationMoves
from .battle_validation_talents import BattleValidationTalents


class BattleValidationLegacy:
    """Legacy compatibility methods for battle validation."""
    
    @staticmethod
    def _validate_monster_stats(monster: 'MonsterInstance') -> bool:
        """Legacy method - delegates to BattleValidationCore."""
        return BattleValidationCore._validate_monster_stats(monster)
    
    @staticmethod
    def _validate_move_availability(move_dict: Dict[str, Any], monster: 'MonsterInstance') -> bool:
        """Legacy method - delegates to BattleValidationMoves."""
        return BattleValidationMoves._validate_move_availability(move_dict, monster)
    
    @staticmethod
    def get_talent_exp_requirements(talent_id: str, current_tier: int) -> Dict[str, Any]:
        """Legacy method - delegates to BattleValidationTalents."""
        return BattleValidationTalents.get_talent_exp_requirements(talent_id, current_tier)
    
    @staticmethod
    def validate_talent_availability(monster: 'MonsterInstance', talent_id: str) -> tuple[bool, str]:
        """Legacy method - delegates to BattleValidationTalents."""
        return BattleValidationTalents.validate_talent_availability(monster, talent_id)
    
    @staticmethod
    def validate_talent_move_combination(monster: 'MonsterInstance', talent_id: str, move_id: str) -> tuple[bool, str]:
        """Legacy method - delegates to BattleValidationTalents."""
        return BattleValidationTalents.validate_talent_move_combination(monster, talent_id, move_id)
    
    @staticmethod
    def validate_talent_synthesis_compatibility(monster1: 'MonsterInstance', monster2: 'MonsterInstance') -> tuple[bool, str]:
        """Legacy method - delegates to BattleValidationTalents."""
        return BattleValidationTalents.validate_talent_synthesis_compatibility(monster1, monster2)
    
    @staticmethod
    def get_talent_bonus_for_synthesis(monster1: 'MonsterInstance', monster2: 'MonsterInstance') -> float:
        """Legacy method - delegates to BattleValidationTalents."""
        return BattleValidationTalents.get_talent_bonus_for_synthesis(monster1, monster2)
