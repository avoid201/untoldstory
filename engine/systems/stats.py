"""
Stats System for Untold Story
Handles base stats, stat stages, level progression, and experience
"""

from typing import Dict, Tuple, Optional
from enum import Enum
from dataclasses import dataclass
import math


class Stat(Enum):
    """Core stats for monsters."""
    HP = "hp"       # Hit Points
    ATK = "atk"     # Physical Attack
    DEF = "def"     # Physical Defense
    MAG = "mag"     # Magic Attack
    RES = "res"     # Magic Resistance
    SPD = "spd"     # Speed (determines turn order)
    ACC = "acc"     # Accuracy (not a base stat, used in battle)
    EVA = "eva"     # Evasion (not a base stat, used in battle)


class GrowthCurve(Enum):
    """Experience growth curves for leveling."""
    FAST = "fast"              # 0.8 * n^3
    MEDIUM_FAST = "medium_fast"  # n^3
    MEDIUM_SLOW = "medium_slow"  # 1.2 * n^3 - 15 * n^2 + 100 * n - 140
    SLOW = "slow"              # 1.25 * n^3


@dataclass
class BaseStats:
    """Base stat values for a monster species."""
    hp: int
    atk: int
    def_: int  # 'def' is a Python keyword
    mag: int
    res: int
    spd: int
    
    def to_dict(self) -> Dict[str, int]:
        """Convert to dictionary format."""
        return {
            "hp": self.hp,
            "atk": self.atk,
            "def": self.def_,
            "mag": self.mag,
            "res": self.res,
            "spd": self.spd
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, int]) -> 'BaseStats':
        """Create from dictionary format."""
        return cls(
            hp=data["hp"],
            atk=data["atk"],
            def_=data["def"],
            mag=data["mag"],
            res=data["res"],
            spd=data["spd"]
        )


class StatStages:
    """
    Manages stat stage modifiers in battle.
    Stages range from -6 to +6, affecting stats multiplicatively.
    """
    
    # Stage multipliers (index 0 = stage -6, index 6 = stage 0, index 12 = stage +6)
    STAGE_MULTIPLIERS = [
        0.25,   # -6
        0.28,   # -5
        0.33,   # -4
        0.40,   # -3
        0.50,   # -2
        0.66,   # -1
        1.00,   # 0
        1.50,   # +1
        2.00,   # +2
        2.50,   # +3
        3.00,   # +4
        3.50,   # +5
        4.00    # +6
    ]
    
    # Accuracy/Evasion use different multipliers
    ACC_EVA_MULTIPLIERS = [
        0.33,   # -6
        0.36,   # -5
        0.43,   # -4
        0.50,   # -3
        0.60,   # -2
        0.75,   # -1
        1.00,   # 0
        1.33,   # +1
        1.66,   # +2
        2.00,   # +3
        2.33,   # +4
        2.66,   # +5
        3.00    # +6
    ]
    
    def __init__(self) -> None:
        """Initialize all stages to 0."""
        self.stages = {
            Stat.ATK: 0,
            Stat.DEF: 0,
            Stat.MAG: 0,
            Stat.RES: 0,
            Stat.SPD: 0,
            Stat.ACC: 0,
            Stat.EVA: 0
        }
    
    def get_stage(self, stat: Stat) -> int:
        """Get the current stage for a stat."""
        return self.stages.get(stat, 0)
    
    def modify_stage(self, stat: Stat, change: int) -> int:
        """
        Modify a stat stage by a certain amount.
        
        Args:
            stat: The stat to modify
            change: Amount to change (-6 to +6)
            
        Returns:
            The actual change applied (may be limited by bounds)
        """
        if stat not in self.stages:
            return 0
        
        old_stage = self.stages[stat]
        new_stage = max(-6, min(6, old_stage + change))
        actual_change = new_stage - old_stage
        
        self.stages[stat] = new_stage
        return actual_change
    
    def get_multiplier(self, stat: Stat) -> float:
        """
        Get the multiplier for a stat based on its stage.
        
        Args:
            stat: The stat to get multiplier for
            
        Returns:
            The multiplier value
        """
        stage = self.get_stage(stat)
        index = stage + 6  # Convert to array index
        
        if stat in [Stat.ACC, Stat.EVA]:
            return self.ACC_EVA_MULTIPLIERS[index]
        else:
            return self.STAGE_MULTIPLIERS[index]
    
    def reset(self) -> None:
        """Reset all stages to 0."""
        for stat in self.stages:
            self.stages[stat] = 0
    
    def reset_negative(self) -> None:
        """Reset only negative stages to 0 (used for switching out)."""
        for stat in self.stages:
            if self.stages[stat] < 0:
                self.stages[stat] = 0


class Experience:
    """Experience and leveling system."""
    
    MAX_LEVEL = 100
    MIN_LEVEL = 1
    
    @staticmethod
    def get_exp_for_level(level: int, curve: GrowthCurve) -> int:
        """
        Calculate total experience needed for a specific level.
        
        Args:
            level: Target level
            curve: Growth curve type
            
        Returns:
            Total experience points needed
        """
        if level < 1:
            return 0
        elif level == 1:
            return 0
        
        n = level
        if curve == GrowthCurve.FAST:
            return int(0.8 * (n ** 3))
        elif curve == GrowthCurve.MEDIUM_FAST:
            return int(n ** 3)
        elif curve == GrowthCurve.MEDIUM_SLOW:
            return int(1.2 * (n ** 3) - 15 * (n ** 2) + 100 * n - 140)
        elif curve == GrowthCurve.SLOW:
            return int(1.25 * (n ** 3))
        else:
            return int(n ** 3)
    
    @staticmethod
    def get_level_for_exp(exp: int, curve: GrowthCurve) -> int:
        """
        Calculate level from total experience.
        
        Args:
            exp: Total experience points
            curve: Growth curve type
            
        Returns:
            Current level (1-100)
        """
        for level in range(1, Experience.MAX_LEVEL + 1):
            if Experience.get_exp_for_level(level + 1, curve) > exp:
                return level
        return Experience.MAX_LEVEL
    
    @staticmethod
    def get_exp_to_next_level(current_exp: int, current_level: int, 
                             curve: GrowthCurve) -> int:
        """
        Calculate experience needed to reach next level.
        
        Args:
            current_exp: Current total experience
            current_level: Current level
            curve: Growth curve type
            
        Returns:
            Experience points needed for next level
        """
        if current_level >= Experience.MAX_LEVEL:
            return 0
        
        next_level_total = Experience.get_exp_for_level(current_level + 1, curve)
        return max(0, next_level_total - current_exp)
    
    @staticmethod
    def calculate_exp_yield(base_yield: int, defeated_level: int, 
                           winner_level: int, is_wild: bool = True) -> int:
        """
        Calculate experience points gained from defeating a monster.
        
        Args:
            base_yield: Base experience yield of defeated monster
            defeated_level: Level of defeated monster
            winner_level: Level of winning monster
            is_wild: Whether the defeated monster was wild
            
        Returns:
            Experience points gained
        """
        # Base formula similar to Pokémon
        exp = base_yield * defeated_level / 5
        
        # Trainer battles give 1.5x experience
        if not is_wild:
            exp *= 1.5
        
        # Level difference modifier (less exp if you're higher level)
        level_diff = defeated_level - winner_level
        if level_diff > 0:
            exp *= 1.0 + (level_diff * 0.1)  # Bonus for beating stronger
        elif level_diff < -10:
            exp *= 0.5  # Penalty for beating much weaker
        elif level_diff < 0:
            exp *= 1.0 + (level_diff * 0.02)  # Small penalty for beating weaker
        
        return max(1, int(exp))


class StatCalculator:
    """Calculates actual stats from base stats, level, and IVs."""
    
    @staticmethod
    def calculate_hp(base: int, level: int, iv: int = 0, ev: int = 0) -> int:
        """
        Calculate HP stat.
        
        Args:
            base: Base HP stat
            level: Monster level
            iv: Individual value (0-31)
            ev: Effort value (0-255)
            
        Returns:
            Calculated HP value
        """
        if base == 1:  # Special case for 1 HP monsters
            return 1
        
        # Simplified Pokémon formula
        return int(((2 * base + iv + ev // 4) * level) // 100) + level + 10
    
    @staticmethod
    def calculate_stat(base: int, level: int, iv: int = 0, ev: int = 0,
                       nature_mod: float = 1.0) -> int:
        """
        Calculate non-HP stat.
        
        Args:
            base: Base stat value
            level: Monster level
            iv: Individual value (0-31)
            ev: Effort value (0-255)
            nature_mod: Nature modifier (0.9, 1.0, or 1.1)
            
        Returns:
            Calculated stat value
        """
        # Simplified Pokémon formula
        stat = int(((2 * base + iv + ev // 4) * level) // 100) + 5
        return int(stat * nature_mod)
    
    @staticmethod
    def calculate_all_stats(base_stats: BaseStats, level: int,
                           ivs: Optional[Dict[str, int]] = None,
                           evs: Optional[Dict[str, int]] = None,
                           nature: Optional[str] = None) -> Dict[str, int]:
        """
        Calculate all stats for a monster.
        
        Args:
            base_stats: Base stats of the species
            level: Monster level
            ivs: Individual values (optional)
            evs: Effort values (optional)
            nature: Nature name (optional)
            
        Returns:
            Dictionary of calculated stats
        """
        if ivs is None:
            ivs = {stat: 0 for stat in ["hp", "atk", "def", "mag", "res", "spd"]}
        if evs is None:
            evs = {stat: 0 for stat in ["hp", "atk", "def", "mag", "res", "spd"]}
        
        # Nature modifiers (simplified - normally based on specific nature)
        nature_mods = {stat: 1.0 for stat in ["atk", "def", "mag", "res", "spd"]}
        
        return {
            "hp": StatCalculator.calculate_hp(
                base_stats.hp, level, ivs.get("hp", 0), evs.get("hp", 0)
            ),
            "atk": StatCalculator.calculate_stat(
                base_stats.atk, level, ivs.get("atk", 0), evs.get("atk", 0),
                nature_mods["atk"]
            ),
            "def": StatCalculator.calculate_stat(
                base_stats.def_, level, ivs.get("def", 0), evs.get("def", 0),
                nature_mods["def"]
            ),
            "mag": StatCalculator.calculate_stat(
                base_stats.mag, level, ivs.get("mag", 0), evs.get("mag", 0),
                nature_mods["mag"]
            ),
            "res": StatCalculator.calculate_stat(
                base_stats.res, level, ivs.get("res", 0), evs.get("res", 0),
                nature_mods["res"]
            ),
            "spd": StatCalculator.calculate_stat(
                base_stats.spd, level, ivs.get("spd", 0), evs.get("spd", 0),
                nature_mods["spd"]
            )
        }


class DamageCalculator:
    """Handles damage calculation for battles."""
    
    @staticmethod
    def calculate_damage(attacker_level: int,
                        power: int,
                        attack_stat: int,
                        defense_stat: int,
                        type_effectiveness: float = 1.0,
                        stab: float = 1.0,
                        critical: bool = False,
                        random_factor: float = 1.0,
                        other_modifiers: float = 1.0) -> int:
        """
        Calculate damage using the standard formula.
        
        Args:
            attacker_level: Level of attacking monster
            power: Move power
            attack_stat: Attack or Magic stat (with stages applied)
            defense_stat: Defense or Resistance stat (with stages applied)
            type_effectiveness: Type matchup multiplier
            stab: Same-type attack bonus
            critical: Whether the hit is critical
            random_factor: Random multiplier (0.85-1.0)
            other_modifiers: Any other multipliers (weather, abilities, etc.)
            
        Returns:
            Final damage value
        """
        # Base damage formula (similar to Pokémon)
        base = (((2 * attacker_level / 5 + 2) * power * attack_stat / defense_stat) / 50) + 2
        
        # Apply modifiers
        damage = base
        damage *= type_effectiveness
        damage *= stab
        
        if critical:
            damage *= 1.5
        
        damage *= random_factor
        damage *= other_modifiers
        
        return max(1, int(damage))