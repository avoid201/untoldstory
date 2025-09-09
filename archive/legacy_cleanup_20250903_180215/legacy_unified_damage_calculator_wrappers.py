"""
LEGACY BACKUP: Deprecated wrapper classes from unified_damage_calculator.py
This file contains all the deprecated wrapper classes that were removed.
"""

import logging
from typing import Dict, List, Any, Optional
import random

logger = logging.getLogger(__name__)

# DEPRECATED: Use DamageResult instead
DQMDamageResult = None  # Will be imported from main file

class DQMCalculator:
    """
    DEPRECATED: Legacy DQMCalculator für Backward Compatibility.
    Verwendet unified_damage_calculator intern.
    """
    
    def __init__(self, rng_seed: Optional[int] = None):
        """Initialize deprecated DQM calculator."""
        self.rng = random.Random(rng_seed)
        self._unified = None  # Will be set to unified_damage_calculator
        logger.warning("DQMCalculator is DEPRECATED. Use UnifiedDamageCalculator instead.")
    
    def calculate_damage(self, 
                        attacker_stats: Dict[str, int],
                        defender_stats: Dict[str, int],
                        move_power: int,
                        move_element: Optional[str] = None,
                        is_physical: bool = True,
                        attacker_traits: Optional[List[str]] = None,
                        defender_traits: Optional[List[str]] = None):
        """
        DEPRECATED: Legacy damage calculation.
        Delegiert an unified_damage_calculator.
        """
        # Implementation would delegate to unified calculator
        pass
    
    def calculate_turn_order(self, monsters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """DEPRECATED: Delegiert an unified_damage_calculator."""
        pass
    
    def calculate_escape_chance(self, 
                               runner_stats: Dict[str, int],
                               enemy_stats: Dict[str, int],
                               escape_attempts: int = 0) -> float:
        """DEPRECATED: Delegiert an unified_damage_calculator."""
        pass
    
    def calculate_exp_reward(self, 
                            enemy_level: int,
                            enemy_rank: str,
                            is_boss: bool = False,
                            party_size: int = 1) -> int:
        """DEPRECATED: Delegiert an unified_damage_calculator."""
        pass
    
    def calculate_gold_reward(self, 
                             enemy_level: int,
                             enemy_rank: str,
                             is_boss: bool = False) -> int:
        """DEPRECATED: Delegiert an unified_damage_calculator."""
        pass
    
    def calculate_stat_stage_multiplier(self, stage: int, is_defensive: bool = False) -> float:
        """DEPRECATED: Delegiert an unified_damage_calculator."""
        pass
    
    def calculate_accuracy(self,
                          move_accuracy: int,
                          attacker_stats: Dict[str, int],
                          defender_stats: Dict[str, int],
                          weather: Optional[str] = None) -> float:
        """DEPRECATED: Delegiert an unified_damage_calculator."""
        pass


class DQMSkillCalculator:
    """
    DEPRECATED: Legacy DQMSkillCalculator für Backward Compatibility.
    Verwendet unified_damage_calculator intern.
    """
    
    @staticmethod
    def calculate_heal(caster_stats: Dict[str, int], skill_power: int) -> int:
        """DEPRECATED: Delegiert an unified_damage_calculator."""
        pass
    
    @staticmethod
    def calculate_buff_duration(caster_level: int, target_level: int) -> int:
        """DEPRECATED: Delegiert an unified_damage_calculator."""
        pass


class DQMDamageStage:
    """
    DEPRECATED: Legacy DQMDamageStage für Backward Compatibility.
    Verwendet unified_damage_calculator intern.
    """
    
    def __init__(self):
        """Initialize deprecated DQM damage stage."""
        self.calculator = None  # Will be set to unified_damage_calculator
        logger.warning("DQMDamageStage is DEPRECATED. Use UnifiedDamageCalculator instead.")
    
    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """DEPRECATED: Delegiert an unified_damage_calculator."""
        pass


# Backwards compatibility aliases
def calculate_damage(attacker, defender, move, **kwargs):
    """Legacy compatibility function - DELEGATES TO UNIFIED CALCULATOR."""
    pass

def calculate_recoil(damage: int, rate: float) -> int:
    """Legacy compatibility function - DELEGATES TO UNIFIED CALCULATOR."""
    pass

def calculate_drain(damage: int, rate: float) -> int:
    """Legacy compatibility function - DELEGATES TO UNIFIED CALCULATOR."""
    pass

def calculate_escape_chance(runner_speed: int, enemy_speed: int, attempts: int = 1) -> float:
    """Legacy compatibility function - DELEGATES TO UNIFIED CALCULATOR."""
    pass

def calculate_accuracy(move_accuracy: int, attacker_accuracy: int = 100, defender_evasion: int = 100) -> bool:
    """Legacy compatibility function - DELEGATES TO UNIFIED CALCULATOR."""
    pass
