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


@dataclass
class DQMDamageResult:
    """Result of DQM damage calculation."""
    damage: int
    is_critical: bool = False
    effectiveness: float = 1.0
    element: DQMElement = DQMElement.NEUTRAL
    
    # Additional DQM-specific fields
    is_miss: bool = False
    is_dodge: bool = False
    is_metal_slime_damage: bool = False  # For metal enemies (0-1 damage)
    tension_multiplier: float = 1.0
    
    def __getitem__(self, key):
        """Make DQMDamageResult subscriptable for backward compatibility."""
        return getattr(self, key, None)
    
    def get(self, key, default=None):
        """Dict-like get method."""
        return getattr(self, key, default)
    
    @property
    def final_damage(self):
        """Alias for damage for compatibility."""
        return self.damage
    
    def get_message(self) -> str:
        """Get battle message for this result."""
        if self.is_miss:
            return "Attacke ging daneben!"
        if self.is_dodge:
            return "Ausgewichen!"
        if self.is_critical:
            return "Kritischer Treffer!"
        if self.is_metal_slime_damage:
            return "Kaum Schaden gegen Metall-Rüstung!"
        if self.effectiveness > 1.5:
            return "Sehr effektiv!"
        if self.effectiveness < 0.5:
            return "Nicht sehr effektiv..."
        return ""


class DQMCalculator:
    """
    Authentic Dragon Quest Monsters battle calculations.
    Based on reverse-engineered formulas from the DQM series.
    """
    
    def __init__(self, rng_seed: Optional[int] = None):
        """
        Initialize DQM calculator.
        
        Args:
            rng_seed: Seed for random number generator (for testing)
        """
        self.rng = random.Random(rng_seed)
    
    def calculate_damage(self, 
                        attacker_stats: Dict[str, int],
                        defender_stats: Dict[str, int],
                        move_power: int,
                        move_element: Optional[DQMElement] = None,
                        is_physical: bool = True,
                        tension_level: int = 0,
                        attacker_traits: Optional[List[str]] = None,
                        defender_traits: Optional[List[str]] = None) -> DQMDamageResult:
        """
        Calculate damage using authentic DQM formula.
        
        Formula from SlimeBattleSystem:
        - Base Damage = move_power * (attacker_stat / 2)
        - Defense Reduction = defender_stat / 4
        - Final = (Base - Defense) * random(7/8 to 9/8)
        - Critical: 1/32 chance for 2x damage
        
        Args:
            attacker_stats: Attacker's stats dictionary
            defender_stats: Defender's stats dictionary  
            move_power: Base power of the move
            move_element: Element type of the move
            is_physical: Whether move uses ATK/DEF (True) or MAG/RES (False)
            tension_level: Current tension level (0-100)
            attacker_traits: List of attacker traits
            defender_traits: List of defender traits
            
        Returns:
            DQMDamageResult with calculated damage
        """
        attacker_traits = attacker_traits or []
        defender_traits = defender_traits or []
        
        # Check for miss (can be expanded with accuracy calculation)
        if self._check_miss(attacker_stats, defender_stats):
            return DQMDamageResult(damage=0, is_miss=True)
        
        # Get relevant stats
        if is_physical:
            attack_stat = attacker_stats.get('atk', 100)
            defense_stat = defender_stats.get('def', 50)
        else:
            attack_stat = attacker_stats.get('mag', 100)
            defense_stat = defender_stats.get('res', 50)
        
        # Apply trait modifiers to stats
        if 'Attack Boost' in attacker_traits:
            attack_stat = int(attack_stat * 1.1)
        if 'Defense Boost' in defender_traits:
            defense_stat = int(defense_stat * 1.1)
        
        # DQM Formula: Base Damage
        base_damage = move_power * (attack_stat / 2)
        
        # DQM Formula: Defense reduction (def/4 in DQM vs def/2 in Pokemon)
        defense_reduction = defense_stat / 4
        
        # Calculate raw damage
        raw_damage = base_damage - defense_reduction
        
        # Apply damage range (7/8 to 9/8)
        min_damage = raw_damage * DQMConstants.DAMAGE_MIN_MULTIPLIER
        max_damage = raw_damage * DQMConstants.DAMAGE_MAX_MULTIPLIER
        
        # Random damage within range
        damage = self.rng.uniform(min_damage, max_damage)
        
        # Check for critical hit (1/32 chance in DQM)
        is_critical = False
        if self._check_critical(attacker_traits):
            damage *= DQMConstants.CRITICAL_MULTIPLIER
            is_critical = True
        
        # Apply tension multiplier
        tension_multiplier = self._calculate_tension_multiplier(tension_level)
        damage *= tension_multiplier
        
        # Check for Metal Slime trait (massive defense)
        if 'Metal Body' in defender_traits:
            damage = self._apply_metal_body(damage)
            return DQMDamageResult(
                damage=int(damage),
                is_critical=is_critical,
                is_metal_slime_damage=True,
                tension_multiplier=tension_multiplier,
                element=move_element or DQMElement.NEUTRAL
            )
        
        # Minimum damage is 1 (unless it's a miss)
        final_damage = max(1, int(damage))
        
        return DQMDamageResult(
            damage=final_damage,
            is_critical=is_critical,
            tension_multiplier=tension_multiplier,
            element=move_element or DQMElement.NEUTRAL
        )
    
    def calculate_turn_order(self, monsters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Calculate turn order using DQM formula.
        
        DQM Formula: Agility + Random(0-255)
        Higher total goes first.
        
        Args:
            monsters: List of monster dictionaries with 'stats' containing 'spd'
            
        Returns:
            Sorted list of monsters in turn order
        """
        turn_values = []
        
        for monster in monsters:
            agility = monster.get('stats', {}).get('spd', 50)
            
            # Apply status effects to speed
            if monster.get('status') == 'paralysis':
                agility = int(agility * 0.5)
            
            # DQM Formula: Add random 0-255 to agility
            turn_value = agility + self.rng.randint(0, DQMConstants.AGILITY_RANDOM_MAX)
            turn_values.append((monster, turn_value))
        
        # Sort by turn value (highest first)
        turn_values.sort(key=lambda x: x[1], reverse=True)
        
        # Log turn order for debugging
        logger.debug("Turn order calculated:")
        for monster, value in turn_values:
            name = monster.get('name', 'Unknown')
            logger.debug(f"  {name}: {value}")
        
        return [monster for monster, _ in turn_values]
    
    def calculate_escape_chance(self, 
                               runner_stats: Dict[str, int],
                               enemy_stats: Dict[str, int],
                               escape_attempts: int = 0) -> float:
        """
        Calculate chance to escape from battle.
        
        DQM escape formula based on agility difference.
        
        Args:
            runner_stats: Stats of the escaping monster
            enemy_stats: Stats of the enemy monster  
            escape_attempts: Number of previous escape attempts
            
        Returns:
            Probability of successful escape (0.0 to 1.0)
        """
        runner_speed = runner_stats.get('spd', 50)
        enemy_speed = enemy_stats.get('spd', 50)
        
        # Base chance
        chance = DQMConstants.ESCAPE_BASE_CHANCE
        
        # Modify by speed difference
        speed_ratio = runner_speed / max(1, enemy_speed)
        
        if speed_ratio >= 2.0:
            # Much faster: guaranteed escape
            return 1.0
        elif speed_ratio >= 1.5:
            # Faster: high chance
            chance = 0.8
        elif speed_ratio >= 1.0:
            # Similar speed: normal chance
            chance = 0.6
        elif speed_ratio >= 0.5:
            # Slower: lower chance
            chance = 0.3
        else:
            # Much slower: very low chance
            chance = 0.1
        
        # Each attempt increases chance
        chance += escape_attempts * 0.1
        
        # Cap at 95% (always small chance of failure)
        return min(0.95, chance)
    
    def calculate_exp_reward(self, 
                            enemy_level: int,
                            enemy_rank: str,
                            is_boss: bool = False,
                            party_size: int = 1) -> int:
        """
        Calculate experience points reward.
        
        Args:
            enemy_level: Level of defeated enemy
            enemy_rank: Rank of enemy (F to X)
            is_boss: Whether enemy is a boss
            party_size: Number of party members to split exp
            
        Returns:
            Experience points earned per party member
        """
        # Base exp by rank
        rank_multipliers = {
            'F': 0.5, 'E': 0.7, 'D': 1.0, 'C': 1.3,
            'B': 1.6, 'A': 2.0, 'S': 2.5, 'SS': 3.0, 'X': 4.0
        }
        
        rank_mult = rank_multipliers.get(enemy_rank, 1.0)
        
        # Base formula
        base_exp = int(enemy_level * 10 * rank_mult)
        
        # Boss multiplier
        if is_boss:
            base_exp = int(base_exp * DQMConstants.EXP_MULTIPLIER)
        
        # Split among party
        exp_per_member = max(1, base_exp // party_size)
        
        return exp_per_member
    
    def calculate_gold_reward(self, 
                             enemy_level: int,
                             enemy_rank: str,
                             is_boss: bool = False) -> int:
        """
        Calculate gold reward from battle.
        
        Args:
            enemy_level: Level of defeated enemy
            enemy_rank: Rank of enemy
            is_boss: Whether enemy is a boss
            
        Returns:
            Gold earned
        """
        # Base gold by rank
        rank_multipliers = {
            'F': 0.3, 'E': 0.5, 'D': 0.8, 'C': 1.0,
            'B': 1.3, 'A': 1.6, 'S': 2.0, 'SS': 2.5, 'X': 3.0
        }
        
        rank_mult = rank_multipliers.get(enemy_rank, 1.0)
        
        # Base formula
        base_gold = int(enemy_level * 5 * rank_mult)
        
        # Boss multiplier
        if is_boss:
            base_gold = int(base_gold * 2.0)
        
        # Add variance
        variance = base_gold * DQMConstants.GOLD_VARIANCE
        gold = base_gold + self.rng.uniform(-variance, variance)
        
        return max(1, int(gold))
    
    def calculate_stat_stage_multiplier(self, stage: int, is_defensive: bool = False) -> float:
        """
        Calculate stat multiplier from stat stage.
        
        DQM uses different multipliers than Pokemon.
        
        Args:
            stage: Stat stage (-6 to +6)
            is_defensive: Whether this is a defensive stat
            
        Returns:
            Multiplier for the stat
        """
        # Clamp stage
        stage = max(DQMConstants.STAT_STAGE_MIN, 
                   min(DQMConstants.STAT_STAGE_MAX, stage))
        
        # DQM stat stage multipliers
        if stage >= 0:
            # Positive stages: 1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5
            multiplier = 1.0 + (stage * 0.25)
        else:
            # Negative stages: 0.75, 0.6, 0.5, 0.4, 0.33, 0.25
            multipliers = [1.0, 0.75, 0.6, 0.5, 0.4, 0.33, 0.25]
            multiplier = multipliers[abs(stage)]
        
        return multiplier
    
    def calculate_accuracy(self,
                          move_accuracy: int,
                          attacker_stats: Dict[str, int],
                          defender_stats: Dict[str, int],
                          weather: Optional[str] = None) -> float:
        """
        Calculate final accuracy of a move.
        
        Args:
            move_accuracy: Base accuracy of the move (0-100)
            attacker_stats: Attacker's stats
            defender_stats: Defender's stats
            weather: Current weather condition
            
        Returns:
            Final hit chance (0.0 to 1.0)
        """
        if move_accuracy < 0:  # Never miss moves
            return 1.0
        
        base_accuracy = move_accuracy / 100.0
        
        # Speed-based accuracy modifier
        attacker_speed = attacker_stats.get('spd', 50)
        defender_speed = defender_stats.get('spd', 50)
        
        speed_ratio = attacker_speed / max(1, defender_speed)
        
        # Speed affects accuracy slightly
        if speed_ratio > 1.5:
            base_accuracy *= 1.1
        elif speed_ratio < 0.67:
            base_accuracy *= 0.9
        
        # Weather effects
        if weather == 'sandstorm':
            base_accuracy *= 0.8  # Reduced accuracy in sandstorm
        elif weather == 'fog':
            base_accuracy *= 0.6  # Heavily reduced in fog
        
        # Cap between 5% and 100%
        return max(0.05, min(1.0, base_accuracy))
    
    def _check_miss(self, attacker_stats: Dict[str, int], 
                   defender_stats: Dict[str, int]) -> bool:
        """Check if attack misses (simplified for now)."""
        # TODO: Implement full accuracy calculation
        # For now, just a small chance to miss
        return self.rng.random() < 0.05  # 5% miss chance
    
    def _check_critical(self, attacker_traits: List[str]) -> bool:
        """
        Check for critical hit using DQM rate.
        
        Args:
            attacker_traits: List of attacker's traits
            
        Returns:
            True if critical hit occurs
        """
        crit_chance = DQMConstants.CRITICAL_HIT_CHANCE
        
        # Critical Master trait increases crit chance
        if 'Critical Master' in attacker_traits:
            crit_chance *= 2  # Double the chance
        
        return self.rng.random() < crit_chance
    
    def _calculate_tension_multiplier(self, tension_level: int) -> float:
        """
        Calculate damage multiplier from tension.
        
        DQM Tension levels:
        - 0: Normal (1.0x)
        - 5: Psyched up (1.2x)
        - 20: High tension (1.5x)
        - 50: Super high tension (2.0x)
        - 100: Max tension (2.5x)
        
        Args:
            tension_level: Current tension (0-100)
            
        Returns:
            Damage multiplier
        """
        if tension_level >= 100:
            return 2.5
        elif tension_level >= 50:
            return 2.0
        elif tension_level >= 20:
            return 1.5
        elif tension_level >= 5:
            return 1.2
        else:
            return 1.0
    
    def _apply_metal_body(self, damage: float) -> int:
        """
        Apply Metal Body trait (metal slime defense).
        
        Metal enemies take 0-1 damage from most attacks.
        
        Args:
            damage: Original damage
            
        Returns:
            Reduced damage (0 or 1)
        """
        if damage < 10:
            # Weak attacks do 0 damage
            return 0
        elif damage < 100:
            # Normal attacks do 0-1 damage
            return self.rng.randint(0, 1)
        else:
            # Very strong attacks can do 1-2 damage
            return self.rng.randint(1, 2)


class DQMSkillCalculator:
    """Calculator for DQM-specific skill mechanics."""
    
    @staticmethod
    def calculate_heal(caster_stats: Dict[str, int], 
                      skill_power: int,
                      tension_level: int = 0) -> int:
        """
        Calculate healing amount.
        
        Args:
            caster_stats: Caster's stats (uses MAG)
            skill_power: Base healing power
            tension_level: Current tension
            
        Returns:
            Amount of HP to heal
        """
        magic_stat = caster_stats.get('mag', 50)
        
        # Base healing formula
        base_heal = skill_power + (magic_stat / 4)
        
        # Apply tension
        calc = DQMCalculator()
        tension_mult = calc._calculate_tension_multiplier(tension_level)
        
        return int(base_heal * tension_mult)
    
    @staticmethod
    def calculate_buff_duration(caster_level: int, 
                               target_level: int) -> int:
        """
        Calculate buff/debuff duration.
        
        Args:
            caster_level: Level of the caster
            target_level: Level of the target
            
        Returns:
            Duration in turns
        """
        base_duration = 3
        
        # Level difference affects duration
        level_diff = caster_level - target_level
        
        if level_diff > 10:
            base_duration += 2
        elif level_diff > 5:
            base_duration += 1
        elif level_diff < -10:
            base_duration -= 2
        elif level_diff < -5:
            base_duration -= 1
        
        # Minimum 1 turn, maximum 5 turns
        return max(1, min(5, base_duration))


# Integration helper for existing damage_calc.py
class DQMDamageStage:
    """Pipeline stage for DQM damage calculation."""
    
    def __init__(self):
        """Initialize DQM damage stage."""
        self.calculator = DQMCalculator()
    
    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process damage calculation using DQM formulas.
        
        Args:
            context: Pipeline context with attacker, defender, move
            
        Returns:
            Updated context with DQM damage
        """
        attacker = context['attacker']
        defender = context['defender']
        move = context['move']
        
        # Extract stats
        attacker_stats = {
            'atk': attacker.stats.get('atk', 100),
            'def': attacker.stats.get('def', 50),
            'mag': attacker.stats.get('mag', 100),
            'res': attacker.stats.get('res', 50),
            'spd': attacker.stats.get('spd', 75)
        }
        
        defender_stats = {
            'atk': defender.stats.get('atk', 100),
            'def': defender.stats.get('def', 50),
            'mag': defender.stats.get('mag', 100),
            'res': defender.stats.get('res', 50),
            'spd': defender.stats.get('spd', 75)
        }
        
        # Get move properties
        is_physical = move.category == 'phys'
        power = move.power
        
        # Get tension if available
        tension = 0
        if hasattr(attacker, 'tension'):
            tension = attacker.tension
        
        # Calculate using DQM formula
        result = self.calculator.calculate_damage(
            attacker_stats=attacker_stats,
            defender_stats=defender_stats,
            move_power=power,
            is_physical=is_physical,
            tension_level=tension
        )
        
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
