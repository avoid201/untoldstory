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

# Import trait system
from engine.systems.battle.monster_traits import get_trait_database, TraitManager, TraitTrigger

if TYPE_CHECKING:
    from engine.systems.monster_instance import MonsterInstance
    from engine.systems.moves import Move
    from engine.systems.types import TypeChart


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
    critical_tier: CriticalTier = CriticalTier.NONE
    effectiveness: float = 1.0
    effectiveness_text: str = ""
    damage_type: DamageType = DamageType.NORMAL
    
    # Additional flags
    blocked: bool = False
    missed: bool = False
    has_stab: bool = False
    type_text: str = ""  # Compatibility with old system
    
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
        self.trait_manager = None  # Will be set if traits are enabled
    
    def setup_default_stages(self) -> None:
        """Set up default calculation stages."""
        self.add_stage("accuracy_check", self._accuracy_stage, 0)
        self.add_stage("traits_pre_damage", self._traits_pre_damage_stage, 1)
        self.add_stage("base_damage", self._base_damage_stage, 2)
        self.add_stage("critical_hit", self._critical_stage, 3)
        self.add_stage("traits_on_attack", self._traits_on_attack_stage, 4)
        self.add_stage("stab", self._stab_stage, 5)
        self.add_stage("type_effectiveness", self._type_effectiveness_stage, 6)
        self.add_stage("trait_resistances", self._trait_resistances_stage, 7)
        self.add_stage("traits_on_defend", self._traits_on_defend_stage, 8)
        self.add_stage("weather", self._weather_stage, 10)
        self.add_stage("terrain", self._terrain_stage, 11)
        self.add_stage("status", self._status_stage, 12)
        self.add_stage("random_spread", self._random_stage, 13)
        self.add_stage("traits_final", self._traits_final_stage, 14)
        self.add_stage("finalize", self._finalize_stage, 15)
    
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

    def calculate_damage(self, attacker: 'MonsterInstance', 
                        defender: 'MonsterInstance', 
                        move: 'Move') -> DamageResult:
        """
        Calculate damage for a move using the pipeline.
        
        Args:
            attacker: Attacking monster
            defender: Defending monster
            move: Move being used
            
        Returns:
            DamageResult with calculated damage
        """
        try:
            # Create context for pipeline
            context = {
                'attacker': attacker,
                'defender': defender,
                'move': move,
                'rng': random.Random(),
                'result': DamageResult(
                    damage=0,
                    is_critical=False,
                    critical_tier=CriticalTier.NONE,
                    effectiveness=1.0,
                    effectiveness_text="",
                    type_text="",
                    damage_type=DamageType.NORMAL
                )
            }
            
            # Execute pipeline
            result = self.execute(context)
            
            # Apply tension multiplier if available
            if hasattr(attacker, 'tension_multiplier'):
                result.damage = int(result.damage * attacker.tension_multiplier)
            
            return result
            
        except Exception as e:
            # Assuming logger is defined elsewhere or will be added
            # logger.error(f"Fehler bei der Schadensberechnung: {str(e)}")
            # Return safe fallback
            return DamageResult(
                damage=0,
                is_critical=False,
                critical_tier=CriticalTier.NONE,
                effectiveness=1.0,
                effectiveness_text="",
                type_text="Fehler bei der Berechnung",
                damage_type=DamageType.NORMAL
            )
    
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
            context['result'].type_text = "Daneben!"
    
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
        
        # Get stats (use modified stats if available)
        if move.category == 'phys':
            if 'attacker_stats_modified' in context and 'atk' in context['attacker_stats_modified']:
                attack_stat = context['attacker_stats_modified']['atk']
            else:
                attack_stat = self._get_effective_stat(attacker, 'atk')
            defense_stat = self._get_effective_stat(defender, 'def')
        else:  # 'mag'
            if 'attacker_stats_modified' in context and 'mag' in context['attacker_stats_modified']:
                attack_stat = context['attacker_stats_modified']['mag']
            else:
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
            
            # Apply critical multiplier based on tier (DQM-style)
            multipliers = {
                CriticalTier.NORMAL: 2.0,      # DQM standard is 2x
                CriticalTier.IMPROVED: 2.25,
                CriticalTier.GUARANTEED: 2.5,
                CriticalTier.DEVASTATING: 3.0  # Rare super critical
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
        context['result'].type_text = context['result'].effectiveness_text  # Compatibility
        
        if effectiveness != 1.0:
            context['result'].modifiers_applied.append(f"Type {effectiveness}x")
    
    def _trait_resistances_stage(self, context: Dict[str, Any]) -> None:
        """Apply trait-based elemental resistances."""
        if context['result'].damage == 0:
            return
        
        defender = context['defender']
        move = context['move']
        
        # Check for elemental resistance traits
        if hasattr(defender, 'traits'):
            resistance_map = {
                "Fire Breath Guard": ("fire", 0.5),
                "Ice Breath Guard": ("ice", 0.5),
                "Bang Ward": ("explosion", 0.5),
            }
            
            # Get move element (try different attributes)
            move_element = None
            if hasattr(move, 'element'):
                move_element = str(move.element).lower()
            elif hasattr(move, 'type'):
                move_element = str(move.type).lower()
            
            if move_element:
                for trait_name in defender.traits:
                    if trait_name in resistance_map:
                        resist_element, resist_value = resistance_map[trait_name]
                        if move_element == resist_element:
                            context['result'].damage = int(context['result'].damage * resist_value)
                            context['result'].modifiers_applied.append(f"Trait: {trait_name}")
                            break
        
        # Legacy trait manager support
        if hasattr(defender, 'trait_manager'):
            if hasattr(context['move'], 'element'):
                resistances = defender.trait_manager.get_element_resistances()
                move_element = str(context['move'].element).lower()
                if move_element in resistances:
                    resistance = resistances[move_element]
                    context['result'].damage = int(context['result'].damage * resistance)
                    context['result'].modifiers_applied.append(f"Element Guard: {move_element}")
    
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
        """Apply random damage spread (DQM uses 7/8 to 9/8)."""
        if context['result'].damage == 0:
            return
        
        rng = context['rng']
        # DQM damage range: 87.5% to 112.5% of base damage
        random_factor = rng.uniform(0.875, 1.125)
        context['result'].damage = int(context['result'].damage * random_factor)
    
    def _finalize_stage(self, context: Dict[str, Any]) -> None:
        """Finalize damage calculation."""
        result = context['result']
        
        # Minimum damage is 1 (unless immune or missed)
        if result.effectiveness > 0 and result.damage < 1 and not result.missed:
            result.damage = 1
        
        # Set calculation time
        result.calculation_time = time.time() - context.get('start_time', time.time())
    
    def _traits_pre_damage_stage(self, context: Dict[str, Any]) -> None:
        """Apply pre-damage calculation traits."""
        if not self._has_traits(context):
            return
        
        attacker = context['attacker']
        defender = context['defender']
        
        # Process direct traits for stat boosts
        if hasattr(attacker, 'traits'):
            trait_db = get_trait_database()
            
            for trait_name in attacker.traits:
                trait = trait_db.get_trait(trait_name)
                if not trait:
                    continue
                
                # Attack Boost trait
                if trait_name == "Attack Boost":
                    if 'attacker_stats_modified' not in context:
                        context['attacker_stats_modified'] = attacker.stats.copy()
                    context['attacker_stats_modified']['atk'] = int(context['attacker_stats_modified']['atk'] * 1.1)
        
        # Legacy trait manager support
        if hasattr(attacker, 'trait_manager'):
            trait_context = {
                'phase': 'pre_damage',
                'stats': attacker.stats.copy(),
                'hp_percent': attacker.current_hp / max(1, attacker.max_hp)
            }
            attacker.trait_manager.process_traits(TraitTrigger.ALWAYS, trait_context)
            # Apply stat modifications
            if 'stats' in trait_context:
                context['attacker_stats_modified'] = trait_context['stats']
    
    def _traits_on_attack_stage(self, context: Dict[str, Any]) -> None:
        """Apply attacker traits during damage calculation."""
        if not self._has_traits(context) or context['result'].damage == 0:
            return
        
        attacker = context['attacker']
        
        # Check for direct traits on attacker
        if hasattr(attacker, 'traits'):
            trait_db = get_trait_database()
            
            for trait_name in attacker.traits:
                trait = trait_db.get_trait(trait_name)
                if not trait:
                    continue
                
                # Critical Master - additional crit chance
                if trait_name == "Critical Master" and not context['result'].is_critical:
                    if random.random() < 0.0625:  # Additional 1/16 chance
                        context['result'].is_critical = True
                        context['result'].damage = int(context['result'].damage * 2)
                        context['result'].modifiers_applied.append("Trait: Critical Master")
                
                # Attack Boost
                elif trait_name == "Attack Boost":
                    context['result'].damage = int(context['result'].damage * 1.1)
                    context['result'].modifiers_applied.append("Trait: Attack Boost")
        
        # Legacy trait manager support
        if hasattr(attacker, 'trait_manager'):
            trait_context = {
                'phase': 'on_attack',
                'damage': context['result'].damage,
                'hp_percent': attacker.current_hp / max(1, attacker.max_hp),
                'is_critical': context['result'].is_critical
            }
            
            effects = attacker.trait_manager.process_traits(TraitTrigger.ON_ATTACK, trait_context)
            
            # Apply damage modifications
            if 'damage' in trait_context:
                context['result'].damage = trait_context['damage']
            
            # Add applied traits to modifiers list
            for effect in effects:
                if 'trait' in effect:
                    context['result'].modifiers_applied.append(f"Trait: {effect['trait']}")
    
    def _traits_on_defend_stage(self, context: Dict[str, Any]) -> None:
        """Apply defender traits during damage calculation."""
        if not self._has_traits(context) or context['result'].damage == 0:
            return
        
        defender = context['defender']
        
        # Check for direct traits on defender
        if hasattr(defender, 'traits'):
            trait_db = get_trait_database()
            
            for trait_name in defender.traits:
                trait = trait_db.get_trait(trait_name)
                if not trait:
                    continue
                
                # Metal Body - massive defense
                if trait_name == "Metal Body":
                    if context['result'].damage < 1000:
                        context['result'].damage = random.choice([0, 1])  # 0 or 1 damage
                    else:
                        context['result'].damage = random.randint(1, 2)  # 1-2 for strong attacks
                    context['result'].modifiers_applied.append("Trait: Metal Body")
                    return  # No other defense traits apply
                
                # Defense Boost
                elif trait_name == "Defense Boost":
                    context['result'].damage = int(context['result'].damage * 0.9)
                    context['result'].modifiers_applied.append("Trait: Defense Boost")
                
                # Counter trait
                elif trait_name == "Counter":
                    if random.random() < 0.25:  # 25% counter chance
                        # Set a flag for counter-attack
                        if not hasattr(defender, 'pending_counter'):
                            defender.pending_counter = context['attacker']
                        context['result'].modifiers_applied.append("Trait: Counter activated")
        
        # Legacy trait manager support
        if hasattr(defender, 'trait_manager'):
            trait_context = {
                'phase': 'on_defend',
                'damage': context['result'].damage,
                'hp_percent': defender.current_hp / max(1, defender.max_hp),
                'attacker': context['attacker'],
                'move': context['move']
            }
            
            effects = defender.trait_manager.process_traits(TraitTrigger.ON_DEFEND, trait_context)
            
            # Apply damage modifications
            if 'damage' in trait_context:
                context['result'].damage = trait_context['damage']
            
            # Check for counter traits
            for effect in effects:
                if effect.get('counter'):
                    context['counter_attack'] = effect
                elif effect.get('damage_return'):
                    context['thorns_damage'] = effect.get('value', 0)
    
    def _traits_final_stage(self, context: Dict[str, Any]) -> None:
        """Apply final trait modifications."""
        if not self._has_traits(context):
            return
        
        # Apply any pending counter or thorn damage
        if 'counter_attack' in context:
            context['result'].modifiers_applied.append("Counter activated")
        
        if 'thorns_damage' in context:
            context['result'].recoil_damage = int(context['result'].damage * context['thorns_damage'])
            context['result'].modifiers_applied.append("Thorns damage")
        
        # Check for direct counter traits
        defender = context.get('defender')
        if defender and hasattr(defender, 'pending_counter'):
            context['result'].modifiers_applied.append("Counter trait activated")
            # The counter-attack will be handled by the battle system
    
    def _has_traits(self, context: Dict[str, Any]) -> bool:
        """Check if traits system is enabled."""
        attacker = context.get('attacker')
        defender = context.get('defender')
        return (hasattr(attacker, 'traits') or hasattr(defender, 'traits') or 
                hasattr(attacker, 'trait_manager') or hasattr(defender, 'trait_manager'))
    
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
        # Base critical ratio (DQM uses 1/32)
        base_ratio = 1/32
        
        # Check for Critical Master trait (both systems)
        if hasattr(attacker, 'trait_manager') and attacker.trait_manager.has_trait('Critical Master'):
            base_ratio *= 2  # Double critical chance
        
        if hasattr(attacker, 'traits') and 'Critical Master' in attacker.traits:
            base_ratio *= 2  # Double critical chance
        
        # Get critical stage
        crit_stage = 0
        if hasattr(move, 'crit_ratio'):
            crit_ratio = move.crit_ratio
            if crit_ratio > 1/4:
                crit_stage = 2
            elif crit_ratio > 1/8:
                crit_stage = 1
        
        # Critical hit chance by stage (DQM rates)
        chances = [1/32, 1/16, 1/8, 1/4, 1/2]
        chance = chances[min(crit_stage, 4)]
        
        # Apply trait multiplier
        chance *= base_ratio
        
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
    Backwards compatible with legacy system.
    """
    
    # Legacy constants for compatibility
    BASE_CRIT_RATE = 1/32  # Changed to DQM rate (was 1/16)
    CRIT_MULTIPLIER = 2.0   # Changed to DQM multiplier (was 1.5)
    STAB_MULTIPLIER = 1.2
    RANDOM_MIN = 0.875  # DQM uses 7/8 (was 0.85)
    RANDOM_MAX = 1.125  # DQM uses 9/8 (was 1.0)
    
    def __init__(self, type_chart: Optional['TypeChart'] = None, seed: Optional[int] = None):
        """
        Initialize damage calculator.
        
        Args:
            type_chart: Type effectiveness chart (optional for compatibility)
            seed: Random seed for deterministic behavior
        """
        # Import here to avoid circular dependency
        from engine.systems.types import type_chart as global_type_chart
        
        self.type_chart = type_chart or global_type_chart
        self.rng = random.Random(seed)
        self.pipeline = DamageCalculationPipeline()
        
        # Global modifiers that apply to all calculations
        self.global_modifiers: List[DamageModifier] = []
        
        # Performance tracking
        self.total_calculations = 0
        self.total_time = 0.0
    
    def process_traits_in_damage(self, attacker, defender, base_damage, is_critical):
        """Apply trait effects to damage calculation."""
        trait_db = get_trait_database()
        final_damage = base_damage
        
        # Check attacker traits
        if hasattr(attacker, 'traits'):
            for trait_name in attacker.traits:
                trait = trait_db.get_trait(trait_name)
                if not trait:
                    continue
                    
                # Critical Master doubles crit chance
                if trait_name == "Critical Master" and not is_critical:
                    if random.random() < 0.0625:  # Additional 1/16 chance
                        is_critical = True
                        final_damage *= 2
                
                # Attack Boost
                elif trait_name == "Attack Boost":
                    final_damage *= 1.1
        
        # Check defender traits
        if hasattr(defender, 'traits'):
            for trait_name in defender.traits:
                trait = trait_db.get_trait(trait_name)
                if not trait:
                    continue
                
                # Metal Body - massive defense
                if trait_name == "Metal Body":
                    if final_damage < 1000:
                        final_damage = random.choice([0, 1])  # 0 or 1 damage
                    else:
                        final_damage = random.randint(1, 2)  # 1-2 for strong attacks
                    return int(final_damage), is_critical
                
                # Defense Boost
                elif trait_name == "Defense Boost":
                    final_damage *= 0.9
                
                # Counter trait
                elif trait_name == "Counter":
                    if random.random() < 0.25:  # 25% counter chance
                        # Set a flag for counter-attack
                        if not hasattr(defender, 'pending_counter'):
                            defender.pending_counter = attacker
        
        return int(final_damage), is_critical

    def check_trait_resistances(self, defender, element):
        """Check if defender has elemental resistance traits."""
        if not hasattr(defender, 'traits'):
            return 1.0
        
        resistance_map = {
            "Fire Breath Guard": ("fire", 0.5),
            "Ice Breath Guard": ("ice", 0.5),
            "Bang Ward": ("explosion", 0.5),
        }
        
        multiplier = 1.0
        for trait_name in defender.traits:
            if trait_name in resistance_map:
                resist_element, resist_value = resistance_map[trait_name]
                if element == resist_element:
                    multiplier *= resist_value
        
        return multiplier

    def calculate(self, 
                 attacker: 'MonsterInstance',
                 defender: 'MonsterInstance',
                 move: 'Move',
                 type_chart: Optional[Dict[Tuple[str, str], float]] = None,
                 weather: Optional[str] = None,
                 terrain: Optional[str] = None,
                 **kwargs) -> DamageResult:
        """
        Calculate damage with full pipeline.
        Compatible with both old and new API.
        
        Args:
            attacker: Attacking monster
            defender: Defending monster
            move: Move being used
            type_chart: Legacy type chart dict (ignored, for compatibility)
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
                effectiveness_text="",
                type_text=""
            ),
            'start_time': start_time,
            **kwargs
        }
        
        # Execute pipeline
        result = self.pipeline.execute(context)
        
        # Apply traits to damage
        if hasattr(self, 'process_traits_in_damage'):
            damage, is_critical = self.process_traits_in_damage(
                attacker, defender, result.damage, result.is_critical
            )
            result.damage = damage
            result.is_critical = is_critical
        
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
            type_text=first_result.type_text,
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


# Legacy compatibility classes
class FixedDamage:
    """Handles fixed and special damage calculations (legacy compatibility)."""
    
    @staticmethod
    def calculate_fixed(amount: int) -> DamageResult:
        """Calculate fixed damage."""
        return SpecialDamageCalculator.calculate_fixed(amount)
    
    @staticmethod
    def calculate_percent(target: 'MonsterInstance', percent: float) -> DamageResult:
        """Calculate percentage-based damage."""
        return SpecialDamageCalculator.calculate_percentage(target, percent)
    
    @staticmethod
    def calculate_recoil(damage_dealt: int, recoil_percent: float) -> int:
        """Calculate recoil damage."""
        return SpecialDamageCalculator.calculate_recoil(damage_dealt, recoil_percent)


class DamageModifiers:
    """Additional damage modifiers for special conditions (legacy compatibility)."""
    
    @staticmethod
    def apply_weather(damage: int, move_type: str, weather: str) -> int:
        """Apply weather-based damage modifiers."""
        weather_mods = {
            'sunny': {'Feuer': 1.5, 'Wasser': 0.5},
            'rain': {'Wasser': 1.5, 'Feuer': 0.5},
            'sandstorm': {'Erde': 1.2},
            'hail': {'Luft': 1.2}
        }
        
        if weather in weather_mods and move_type in weather_mods[weather]:
            return int(damage * weather_mods[weather][move_type])
        
        return damage
    
    @staticmethod
    def apply_terrain(damage: int, move_type: str, terrain: str) -> int:
        """Apply terrain-based damage modifiers."""
        terrain_mods = {
            'grassy': {'Pflanze': 1.3},
            'electric': {'Energie': 1.3},
            'psychic': {'Mystik': 1.3},
            'misty': {'Chaos': 0.5}
        }
        
        if terrain in terrain_mods and move_type in terrain_mods[terrain]:
            return int(damage * terrain_mods[terrain][move_type])
        
        return damage


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
            type_text="",
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
            type_text="",
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
            type_text="",
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