# ARCHIVED: 2025-01-03 - Replaced by unified_damage_calculator.py
"""
Dragon Quest Monsters Battle Formulas
Authentic DQM damage calculations and battle mechanics

Based on:
- SlimeBattleSystem (https://github.com/Joshalexjacobs/SlimeBattleSystem)
- DQM series mechanics analysis
- Community reverse-engineering efforts
"""

import random
import math
from typing import Optional, Tuple, Dict, Any, List
from dataclasses import dataclass
from enum import Enum, auto
import logging

logger = logging.getLogger(__name__)


class DQMConstants:
    """Constants for DQM battle mechanics."""
    
    # Critical Hit
    CRITICAL_HIT_CHANCE = 1/32  # DQM uses 1/32 instead of Pokemon's 1/16
    CRITICAL_MULTIPLIER = 2.0   # Always 2x in DQM
    
    # Damage Range
    DAMAGE_MIN_MULTIPLIER = 0.875  # 7/8 of base damage
    DAMAGE_MAX_MULTIPLIER = 1.125  # 9/8 of base damage
    
    # Turn Order
    AGILITY_RANDOM_MAX = 255  # Random 0-255 added to agility for turn order
    
    # Escape Formula
    ESCAPE_BASE_CHANCE = 0.5  # Base 50% chance
    ESCAPE_SPEED_FACTOR = 0.3  # How much speed difference affects escape
    
    # Status Effect Durations (in turns)
    SLEEP_MIN_TURNS = 1
    SLEEP_MAX_TURNS = 4
    CONFUSION_MIN_TURNS = 2
    CONFUSION_MAX_TURNS = 5
    
    # Stat Stage Limits
    STAT_STAGE_MIN = -6
    STAT_STAGE_MAX = 6
    
    # Experience and Gold
    EXP_MULTIPLIER = 1.5  # Boss battles give 1.5x exp
    GOLD_VARIANCE = 0.2   # Gold can vary by ±20%


class DQMElement(Enum):
    """DQM-style element types."""
    FIRE = "fire"        # Frizz family
    ICE = "ice"          # Crack family  
    THUNDER = "thunder"  # Zap family
    WIND = "wind"        # Woosh family
    EARTH = "earth"      # Bang family
    WATER = "water"      # Splash family
    DARK = "dark"        # Zam family
    LIGHT = "light"      # Heal/Holy family
    NEUTRAL = "neutral"  # Physical attacks


# DEPRECATED: Use DamageResult from unified_damage_calculator instead
from engine.systems.unified_damage_calculator import DamageResult
DQMDamageResult = DamageResult


class DQMCalculator:
    """
    DEPRECATED: Legacy DQMCalculator für Backward Compatibility.
    Verwendet UnifiedDamageCalculator intern.
    """
    
    def __init__(self, rng_seed: Optional[int] = None):
        """
        Initialize DQM calculator.
        
        Args:
            rng_seed: Seed for random number generator (for testing)
        """
        self.rng = random.Random(rng_seed)
        # Use UnifiedDamageCalculator as Single Source of Truth
        from engine.systems.unified_damage_calculator import unified_damage_calculator
        self._unified = unified_damage_calculator
        logger.warning("DQMCalculator is DEPRECATED. Use UnifiedDamageCalculator instead.")
    
    def calculate_damage(self, 
                        attacker_stats: Dict[str, int],
                        defender_stats: Dict[str, int],
                        move_power: int,
                        move_element: Optional[DQMElement] = None,
                        is_physical: bool = True,
                        attacker_traits: Optional[List[str]] = None,
                        defender_traits: Optional[List[str]] = None) -> DamageResult:
        """
        DEPRECATED: Legacy damage calculation.
        Delegiert an UnifiedDamageCalculator.
        """
        # Erstelle Mock-Objekte für die neue API
        class MockMove:
            def __init__(self, power, element, is_physical):
                self.power = power
                self.type = element or "Normal"
                self.category = type('Category', (), {'value': 'phys' if is_physical else 'mag'})()
        
        class MockMonster:
            def __init__(self, stats, traits=None):
                self.stats = stats
                self.traits = traits or []
                self.types = [move_element] if move_element else ["Normal"]
        
        mock_move = MockMove(move_power, move_element, is_physical)
        mock_attacker = MockMonster(attacker_stats, attacker_traits)
        mock_defender = MockMonster(defender_stats, defender_traits)
        
        # Verwende unified calculator
        if is_physical:
            result = self._unified.calculate_physical_damage(mock_attacker, mock_defender, mock_move)
        else:
            result = self._unified.calculate_magical_damage(mock_attacker, mock_defender, mock_move)
        
        # Setze zusätzliche Felder für Backward Compatibility
        result.element = move_element
        return result
    
    def calculate_turn_order(self, monsters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """DEPRECATED: Delegiert an UnifiedDamageCalculator."""
        return self._unified.calculate_turn_order(monsters)
    
    def calculate_escape_chance(self, 
                               runner_stats: Dict[str, int],
                               enemy_stats: Dict[str, int],
                               escape_attempts: int = 0) -> float:
        """DEPRECATED: Delegiert an UnifiedDamageCalculator."""
        return self._unified.calculate_escape_chance(
            runner_stats.get('spd', 50),
            enemy_stats.get('spd', 50),
            escape_attempts
        )
    
    def calculate_exp_reward(self, 
                            enemy_level: int,
                            enemy_rank: str,
                            is_boss: bool = False,
                            party_size: int = 1) -> int:
        """DEPRECATED: Delegiert an UnifiedDamageCalculator."""
        return self._unified.calculate_exp_reward(enemy_level, enemy_rank, is_boss, party_size)
    
    def calculate_gold_reward(self, 
                             enemy_level: int,
                             enemy_rank: str,
                             is_boss: bool = False) -> int:
        """DEPRECATED: Delegiert an UnifiedDamageCalculator."""
        return self._unified.calculate_gold_reward(enemy_level, enemy_rank, is_boss)
    
    def calculate_stat_stage_multiplier(self, stage: int, is_defensive: bool = False) -> float:
        """DEPRECATED: Delegiert an UnifiedDamageCalculator."""
        return self._unified.calculate_stat_stage_multiplier(stage, is_defensive)
    
    def calculate_accuracy(self,
                          move_accuracy: int,
                          attacker_stats: Dict[str, int],
                          defender_stats: Dict[str, int],
                          weather: Optional[str] = None) -> float:
        """DEPRECATED: Delegiert an UnifiedDamageCalculator."""
        return float(self._unified.calculate_accuracy(move_accuracy, 100, 100))
    
    # Private methods removed - now handled by UnifiedDamageCalculator


class DQMSkillCalculator:
    """DEPRECATED: Calculator for DQM-specific skill mechanics."""
    
    @staticmethod
    def calculate_heal(caster_stats: Dict[str, int], 
                      skill_power: int) -> int:
        """DEPRECATED: Delegiert an UnifiedDamageCalculator."""
        from engine.systems.unified_damage_calculator import unified_damage_calculator
        return unified_damage_calculator.calculate_heal(caster_stats, skill_power)
    
    @staticmethod
    def calculate_buff_duration(caster_level: int, 
                               target_level: int) -> int:
        """DEPRECATED: Delegiert an UnifiedDamageCalculator."""
        from engine.systems.unified_damage_calculator import unified_damage_calculator
        return unified_damage_calculator.calculate_buff_duration(caster_level, target_level)


# Integration helper for existing damage_calc.py
class DQMDamageStage:
    """DEPRECATED: Pipeline stage for DQM damage calculation."""
    
    def __init__(self):
        """Initialize DQM damage stage."""
        # Use UnifiedDamageCalculator as Single Source of Truth
        from engine.systems.unified_damage_calculator import unified_damage_calculator
        self.calculator = unified_damage_calculator
        logger.warning("DQMDamageStage is DEPRECATED. Use UnifiedDamageCalculator instead.")
    
    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        DEPRECATED: Process damage calculation using DQM formulas.
        Delegiert an UnifiedDamageCalculator.
        """
        attacker = context['attacker']
        defender = context['defender']
        move = context['move']
        
        # Verwende unified calculator
        result = self.calculator.calculate_damage(attacker, defender, move)
        
        # Update context
        context['result'].damage = result.damage
        context['result'].is_critical = result.is_critical
        
        if result.is_critical:
            context['result'].critical_tier = 1  # Map to existing system
            
        return context


# Export main classes
__all__ = [
    'DQMCalculator',
    'DQMDamageResult',
    'DQMConstants',
    'DQMElement',
    'DQMSkillCalculator',
    'DQMDamageStage'
]
