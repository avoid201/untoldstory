"""
Optimized Damage Calculation System for Untold Story
High-performance damage calculations with advanced mechanics
"""

import random
import math
import numpy as np
from typing import TYPE_CHECKING, Optional, Dict, List, Tuple, Any, Callable
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from functools import lru_cache
import time

if TYPE_CHECKING:
    from engine.systems.monster_instance import MonsterInstance
    from engine.systems.moves import Move
    from types_refactored import TypeChart


# Critical hit tiers for advanced critical mechanics
class CriticalTier(IntEnum):
    """Different levels of critical hits."""
    NONE = 0
    NORMAL = 1
    IMPROVED = 2
    GUARANTEED = 3
    DEVASTATING = 4


# Damage types for special calculations
class DamageType(Enum):
    """Types of damage for special mechanics."""
    NORMAL = "normal"
    FIXED = "fixed"
    PERCENTAGE = "percentage"
    RECOIL = "recoil"
    DRAIN = "drain"
    MULTI_HIT = "multi_hit"
    SPREAD = "spread"


@dataclass
class DamageResult:
    """Comprehensive result of damage calculation."""
    damage: int
    is_critical: bool
    critical_tier: CriticalTier
    effectiveness: float
    effectiveness_text: str
    damage_type: DamageType = DamageType.NORMAL
    
    # Additional flags
    blocked: bool = False
    missed: bool = False
    has_stab: bool = False
    
    # Advanced mechanics
    recoil_damage: int = 0
    drain_amount: int = 0
    
    # Modifiers applied
    modifiers_applied: List[str] = field(default_factory=list)
    
    # Performance tracking
    calculation_time: float = 0.0
    
    def get_effectiveness_text(self) -> str:
        """Get localized effectiveness text."""
        if self.effectiveness >= 4.0:
            return "Verheerend effektiv!!!"
        elif self.effectiveness >= 2.0:
            return "Sehr effektiv!"
        elif self.effectiveness > 1.0:
            return "Effektiv!"
        elif self.effectiveness == 0:
            return "Hat keine Wirkung..."
        elif self.effectiveness < 0.5:
            return "Kaum effektiv..."
        elif self.effectiveness < 1.0:
            return "Nicht sehr effektiv..."
        return ""


@dataclass
class DamageModifier:
    """Represents a damage modifier."""
    name: str
    multiplier: float
    condition: Optional[Callable] = None
    priority: int = 0
    
    def applies(self, context: Dict[str, Any]) -> bool:
        """Check if modifier applies in context."""
        if self.condition is None:
            return True
        return self.condition(context)


@dataclass
class MultiHitResult(DamageResult):
    """Result for multi-hit moves."""
    hit_count: int = 1
    individual_damages: List[int] = field(default_factory=list)
    
    def get_total_damage(self) -> int:
        """Get total damage across all hits."""
        return sum(self.individual_damages)


class DamageCalculationPipeline:
    """
    Pipeline for damage calculation with stages.
    Allows for modular and extensible damage calculation.
    """
    
    def __init__(self):
        """Initialize calculation pipeline."""
        self.stages: List[Tuple[str, Callable, int]] = []
        self.setup_default_stages()
    
    def setup_default_stages(self) -> None:
        """Set up default calculation stages."""
        self.add_stage("accuracy_check", self._accuracy_stage, 0)
        self.add_stage("base_damage", self._base_damage_stage, 1)
        self.add_stage("critical_hit", self._critical_stage, 2)
        self.add_stage("stab", self._stab_stage, 3)
        self.add_stage("type_effectiveness", self._type_effectiveness_stage, 4)
        self.add_stage("weather", self._weather_stage, 5)
        self.add_stage("terrain", self._terrain_stage, 6)
        self.add_stage("status", self._status_stage, 7)
        self.add_stage("random_spread", self._random_stage, 8)
        self.add_stage("finalize", self._finalize_stage, 9)
    
    def add_stage(self, name: str, function: Callable, priority: int) -> None:
        """Add a calculation stage."""
        self.stages.append((name, function, priority))
        self.stages.sort(key=lambda x: x[2])
    
    def remove_stage(self, name: str) -> None:
        """Remove a calculation stage."""
        self.stages = [(n, f, p) for n, f, p in self.stages if n != name]
    
    def execute(self, context: Dict[str, Any]) -> DamageResult:
        """Execute the calculation pipeline."""
        for name, function, _ in self.stages:
            function(context)
            
            # Early exit conditions
            if context['result'].missed or context['result'].blocked:
                break
        
        return context['result']
    
    def _accuracy_stage(self, context: Dict[str, Any]) -> None:
        """Check if move hits."""
        move = context['move']
        attacker = context['attacker']
        defender = context['defender']
        rng = context['rng']
        
        # Moves with -1 accuracy always hit
        if move.accuracy < 0:
            return
        
        # Get accuracy and evasion stages
        acc_stage = attacker.stat_stages.get('acc', 0)
        eva_stage = defender.stat_stages.get('eva', 0)
        
        # Combined stage for accuracy calculation
        combined_stage = max(-6, min(6, acc_stage - eva_stage))
        
        # Accuracy multiplier from stages
        if combined_stage >= 0:
            stage_multiplier = (3 + combined_stage) / 3
        else:
            stage_multiplier = 3 / (3 - combined_stage)
        
        # Final accuracy
        final_accuracy = move.accuracy * stage_multiplier
        
        # Status effects
        if attacker.status == 'paralysis':
            final_accuracy *= 0.75
        
        # Roll for hit
        if rng.uniform(0, 100) >= final_accuracy:
            context['result'].missed = True
    
    def _base_damage_stage(self, context: Dict[str, Any]) -> None:
        """Calculate base damage."""
        if context['result'].missed:
            return
        
        move = context['move']
        attacker = context['attacker']
        defender = context['defender']
        
        # Support moves don't deal damage
        if move.category == 'support' or move.power <= 0:
            context['result'].damage = 0
            return
        
        # Get stats
        if move.category == 'phys':
            attack_stat = self._get_effective_stat(attacker, 'atk')
            defense_stat = self._get_effective_stat(defender, 'def')
        else:  # 'mag'
            attack_stat = self._get_effective_stat(attacker, 'mag')
            defense_stat = self._get_effective_stat(defender, 'res')
        
        # Store for critical hit stage
        context['attack_stat'] = attack_stat
        context['defense_stat'] = defense_stat
        
        # Base damage formula
        level = attacker.level
        power = move.power
        
        base_damage = (((2 * level / 5 + 2) * power * attack_stat / defense_stat) / 50) + 2
        context['result'].damage = int(base_damage)
    
    def _critical_stage(self, context: Dict[str, Any]) -> None:
        """Check and apply critical hit."""
        if context['result'].damage == 0:
            return
        
        attacker = context['attacker']
        defender = context['defender']
        move = context['move']
        rng = context['rng']
        
        # Determine critical tier
        crit_tier = self._determine_critical_tier(attacker, move, rng)
        context['result'].critical_tier = crit_tier
        
        if crit_tier != CriticalTier.NONE:
            context['result'].is_critical = True
            
            # Recalculate stats ignoring stages
            if move.category == 'phys':
                if attacker.stat_stages.get('atk', 0) < 0:
                    context['attack_stat'] = attacker.stats['atk']
                if defender.stat_stages.get('def', 0) > 0:
                    context['defense_stat'] = defender.stats['def']
            else:
                if attacker.stat_stages.get('mag', 0) < 0:
                    context['attack_stat'] = attacker.stats['mag']
                if defender.stat_stages.get('res', 0) > 0:
                    context['defense_stat'] = defender.stats['res']
            
            # Apply critical multiplier based on tier
            multipliers = {
                CriticalTier.NORMAL: 1.5,
                CriticalTier.IMPROVED: 1.75,
                CriticalTier.GUARANTEED: 2.0,
                CriticalTier.DEVASTATING: 2.5
            }
            
            crit_multiplier = multipliers.get(crit_tier, 1.5)
            context['result'].damage = int(context['result'].damage * crit_multiplier)
            context['result'].modifiers_applied.append(f"Critical {crit_tier.name}")
    
    def _stab_stage(self, context: Dict[str, Any]) -> None:
        """Apply STAB bonus."""
        if context['result'].damage == 0:
            return
        
        move = context['move']
        attacker = context['attacker']
        
        if move.type in attacker.species.types:
            context['result'].has_stab = True
            context['result'].damage = int(context['result'].damage * 1.2)
            context['result'].modifiers_applied.append("STAB")
    
    def _type_effectiveness_stage(self, context: Dict[str, Any]) -> None:
        """Apply type effectiveness."""
        if context['result'].damage == 0:
            return
        
        move = context['move']
        defender = context['defender']
        type_chart = context['type_chart']
        
        effectiveness = type_chart.calculate_type_multiplier(
            move.type, defender.species.types
        )
        
        context['result'].effectiveness = effectiveness
        context['result'].damage = int(context['result'].damage * effectiveness)
        context['result'].effectiveness_text = context['result'].get_effectiveness_text()
        
        if effectiveness != 1.0:
            context['result'].modifiers_applied.append(f"Type {effectiveness}x")
    
    def _weather_stage(self, context: Dict[str, Any]) -> None:
        """Apply weather effects."""
        if context['result'].damage == 0:
            return
        
        weather = context.get('weather')
        if not weather:
            return
        
        move = context['move']
        damage = context['result'].damage
        
        # Weather effects on damage
        weather_mods = {
            'sunny': {'Feuer': 1.5, 'Wasser': 0.5},
            'rain': {'Wasser': 1.5, 'Feuer': 0.5},
            'sandstorm': {'Erde': 1.2},
            'hail': {'Luft': 1.2},
            'fog': {'Mystik': 1.3, 'Energie': 0.7}
        }
        
        if weather in weather_mods and move.type in weather_mods[weather]:
            mod = weather_mods[weather][move.type]
            context['result'].damage = int(damage * mod)
            context['result'].modifiers_applied.append(f"Weather {weather}")
    
    def _terrain_stage(self, context: Dict[str, Any]) -> None:
        """Apply terrain effects."""
        if context['result'].damage == 0:
            return
        
        terrain = context.get('terrain')
        if not terrain:
            return
        
        move = context['move']
        damage = context['result'].damage
        
        # Terrain effects on damage
        terrain_mods = {
            'grassy': {'Pflanze': 1.3},
            'electric': {'Energie': 1.3},
            'psychic': {'Mystik': 1.3},
            'misty': {'Chaos': 0.5},
            'volcanic': {'Feuer': 1.4, 'Wasser': 0.6}
        }
        
        if terrain in terrain_mods and move.type in terrain_mods[terrain]:
            mod = terrain_mods[terrain][move.type]
            context['result'].damage = int(damage * mod)
            context['result'].modifiers_applied.append(f"Terrain {terrain}")
    
    def _status_stage(self, context: Dict[str, Any]) -> None:
        """Apply status effect modifiers."""
        if context['result'].damage == 0:
            return
        
        attacker = context['attacker']
        move = context['move']
        
        # Burn reduces physical damage
        if attacker.status == 'burn' and move.category == 'phys':
            context['result'].damage = int(context['result'].damage * 0.5)
            context['result'].modifiers_applied.append("Burn")
    
    def _random_stage(self, context: Dict[str, Any]) -> None:
        """Apply random damage spread."""
        if context['result'].damage == 0:
            return
        
        rng = context['rng']
        random_factor = rng.uniform(0.85, 1.0)
        context['result'].damage = int(context['result'].damage * random_factor)
    
    def _finalize_stage(self, context: Dict[str, Any]) -> None:
        """Finalize damage calculation."""
        result = context['result']
        
        # Minimum damage is 1 (unless immune or missed)
        if result.effectiveness > 0 and result.damage < 1 and not result.missed:
            result.damage = 1
        
        # Set calculation time
        result.calculation_time = time.time() - context['start_time']
    
    def _get_effective_stat(self, monster: 'MonsterInstance', stat: str) -> int:
        """Get effective stat with stages."""
        base_stat = monster.stats.get(stat, 100)
        stage = monster.stat_stages.get(stat, 0)
        
        if stage >= 0:
            multiplier = (2 + stage) / 2
        else:
            multiplier = 2 / (2 - stage)
        
        return int(base_stat * multiplier)
    
    def _determine_critical_tier(self, attacker: 'MonsterInstance', 
                                move: 'Move', rng: random.Random) -> CriticalTier:
        """Determine critical hit tier."""
        # Base critical ratio
        base_ratio = 1/16
        
        # Get critical stage
        crit_stage = 0
        if hasattr(move, 'crit_ratio'):
            if move.crit_ratio > 1/8:
                crit_stage = 1
            elif move.crit_ratio > 1/4:
                crit_stage = 2
        
        # Critical hit chance by stage
        chances = [1/16, 1/8, 1/4, 1/3, 1/2]
        chance = chances[min(crit_stage, 4)]
        
        # Roll for critical
        if rng.random() >= chance:
            return CriticalTier.NONE
        
        # Determine tier based on additional roll
        tier_roll = rng.random()
        if tier_roll < 0.7:
            return CriticalTier.NORMAL
        elif tier_roll < 0.9:
            return CriticalTier.IMPROVED
        elif tier_roll < 0.98:
            return CriticalTier.GUARANTEED
        else:
            return CriticalTier.DEVASTATING


class DamageCalculator:
    """
    High-performance damage calculator with pipeline architecture.
    """
    
    def __init__(self, type_chart: 'TypeChart', seed: Optional[int] = None):
        """
        Initialize damage calculator.
        
        Args:
            type_chart: Type effectiveness chart
            seed: Random seed for deterministic behavior
        """
        self.type_chart = type_chart
        self.rng = random.Random(seed)
        self.pipeline = DamageCalculationPipeline()
        
        # Global modifiers that apply to all calculations
        self.global_modifiers: List[DamageModifier] = []
        
        # Performance tracking
        self.total_calculations = 0
        self.total_time = 0.0
    
    def calculate(self, 
                 attacker: 'MonsterInstance',
                 defender: 'MonsterInstance',
                 move: 'Move',
                 weather: Optional[str] = None,
                 terrain: Optional[str] = None,
                 **kwargs) -> DamageResult:
        """
        Calculate damage with full pipeline.
        
        Args:
            attacker: Attacking monster
            defender: Defending monster
            move: Move being used
            weather: Current weather
            terrain: Current terrain
            **kwargs: Additional context
            
        Returns:
            Complete damage result
        """
        start_time = time.time()
        
        # Build context
        context = {
            'attacker': attacker,
            'defender': defender,
            'move': move,
            'type_chart': self.type_chart,
            'weather': weather,
            'terrain': terrain,
            'rng': self.rng,
            'result': DamageResult(
                damage=0,
                is_critical=False,
                critical_tier=CriticalTier.NONE,
                effectiveness=1.0,
                effectiveness_text=""
            ),
            'start_time': start_time,
            **kwargs
        }
        
        # Execute pipeline
        result = self.pipeline.execute(context)
        
        # Apply global modifiers
        for modifier in self.global_modifiers:
            if modifier.applies(context):
                result.damage = int(result.damage * modifier.multiplier)
                result.modifiers_applied.append(modifier.name)
        
        # Track performance
        self.total_calculations += 1
        self.total_time += result.calculation_time
        
        return result
    
    def calculate_multi_hit(self,
                          attacker: 'MonsterInstance',
                          defender: 'MonsterInstance',
                          move: 'Move',
                          hit_count: Optional[int] = None,
                          **kwargs) -> MultiHitResult:
        """
        Calculate damage for multi-hit moves.
        
        Args:
            attacker: Attacking monster
            defender: Defending monster
            move: Move being used
            hit_count: Number of hits (None for random)
            **kwargs: Additional context
            
        Returns:
            Multi-hit damage result
        """
        # Determine hit count
        if hit_count is None:
            # Random 2-5 hits with weighted probability
            weights = [0.35, 0.35, 0.15, 0.15]  # 2, 3, 4, 5 hits
            hit_count = self.rng.choices([2, 3, 4, 5], weights=weights)[0]
        
        # Calculate each hit
        individual_damages = []
        first_result = None
        
        for i in range(hit_count):
            result = self.calculate(attacker, defender, move, **kwargs)
            
            if i == 0:
                first_result = result
            
            individual_damages.append(result.damage)
        
        # Build multi-hit result
        multi_result = MultiHitResult(
            damage=sum(individual_damages),
            is_critical=first_result.is_critical,
            critical_tier=first_result.critical_tier,
            effectiveness=first_result.effectiveness,
            effectiveness_text=first_result.effectiveness_text,
            has_stab=first_result.has_stab,
            modifiers_applied=first_result.modifiers_applied,
            calculation_time=first_result.calculation_time,
            hit_count=hit_count,
            individual_damages=individual_damages
        )
        
        return multi_result
    
    def preview_damage(self,
                      attacker: 'MonsterInstance',
                      defender: 'MonsterInstance',
                      move: 'Move',
                      **kwargs) -> Dict[str, Any]:
        """
        Preview damage range without RNG.
        
        Args:
            attacker: Attacking monster
            defender: Defending monster
            move: Move being used
            **kwargs: Additional context
            
        Returns:
            Damage preview with min/max/average
        """
        # Store current RNG state
        state = self.rng.getstate()
        
        # Calculate with minimum roll
        self.rng.seed(0)
        min_result = self.calculate(attacker, defender, move, **kwargs)
        
        # Calculate with maximum roll
        self.rng.seed(1)
        max_result = self.calculate(attacker, defender, move, **kwargs)
        
        # Restore RNG state
        self.rng.setstate(state)
        
        # Calculate average
        samples = []
        for i in range(10):
            self.rng.seed(i)
            result = self.calculate(attacker, defender, move, **kwargs)
            samples.append(result.damage)
        
        self.rng.setstate(state)
        
        return {
            'min': min_result.damage,
            'max': max_result.damage,
            'average': sum(samples) / len(samples),
            'effectiveness': min_result.effectiveness,
            'has_stab': min_result.has_stab,
            'can_critical': min_result.critical_tier != CriticalTier.NONE
        }
    
    def add_global_modifier(self, modifier: DamageModifier) -> None:
        """Add a global damage modifier."""
        self.global_modifiers.append(modifier)
        self.global_modifiers.sort(key=lambda x: x.priority)
    
    def remove_global_modifier(self, name: str) -> None:
        """Remove a global damage modifier."""
        self.global_modifiers = [m for m in self.global_modifiers if m.name != name]
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        avg_time = self.total_time / self.total_calculations if self.total_calculations > 0 else 0
        
        return {
            'total_calculations': self.total_calculations,
            'total_time': self.total_time,
            'average_time': avg_time,
            'calculations_per_second': 1 / avg_time if avg_time > 0 else 0
        }


class SpecialDamageCalculator:
    """Handles special damage calculation types."""
    
    @staticmethod
    def calculate_fixed(amount: int) -> DamageResult:
        """Calculate fixed damage."""
        return DamageResult(
            damage=amount,
            is_critical=False,
            critical_tier=CriticalTier.NONE,
            effectiveness=1.0,
            effectiveness_text="",
            damage_type=DamageType.FIXED
        )
    
    @staticmethod
    def calculate_percentage(target: 'MonsterInstance', 
                            percentage: float) -> DamageResult:
        """Calculate percentage-based damage."""
        damage = int(target.max_hp * percentage)
        damage = max(1, damage)
        
        return DamageResult(
            damage=damage,
            is_critical=False,
            critical_tier=CriticalTier.NONE,
            effectiveness=1.0,
            effectiveness_text="",
            damage_type=DamageType.PERCENTAGE
        )
    
    @staticmethod
    def calculate_level_based(level: int, multiplier: float = 1.0) -> DamageResult:
        """Calculate level-based damage."""
        damage = int(level * multiplier)
        
        return DamageResult(
            damage=damage,
            is_critical=False,
            critical_tier=CriticalTier.NONE,
            effectiveness=1.0,
            effectiveness_text="",
            damage_type=DamageType.FIXED
        )
    
    @staticmethod
    def calculate_recoil(damage_dealt: int, recoil_rate: float) -> int:
        """Calculate recoil damage."""
        return max(1, int(damage_dealt * recoil_rate))
    
    @staticmethod
    def calculate_drain(damage_dealt: int, drain_rate: float) -> int:
        """Calculate HP drain amount."""
        return max(1, int(damage_dealt * drain_rate))