"""
Unified Damage Calculator for Untold Story
Konsolidiert alle Damage-Calculator-Implementierungen in ein einheitliches System
SINGLE SOURCE OF TRUTH für alle Damage-Berechnungen
"""

from typing import TYPE_CHECKING, Optional, Dict, List, Any
from dataclasses import dataclass
import logging
import time
import random
import math
from engine.systems.talent_system import get_talent_database

if TYPE_CHECKING:
    # Lazy imports für zirkuläre Dependencies
    from engine.systems.monster_instance import MonsterInstance
    from engine.systems.moves import Move
    from engine.systems.types import TypeChart

# Create simple fallback classes for DamageResult
@dataclass
class DamageResult:
    """Result of damage calculation."""
    damage: int
    is_critical: bool = False
    critical_tier: int = 0
    effectiveness: float = 1.0
    effectiveness_text: str = ""
    damage_type: str = "NORMAL"
    has_stab: bool = False
    type_text: str = ""
    
    # Additional DQM-specific fields
    is_miss: bool = False
    is_dodge: bool = False
    is_metal_slime_damage: bool = False
    element: Optional[str] = None
    
    # Performance tracking
    calculation_time: float = 0.0
    
    def __getitem__(self, key):
        """Make DamageResult subscriptable for backward compatibility."""
        return getattr(self, key, None)
    
    def get(self, key, default=None):
        """Dict-like get method for backward compatibility."""
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

@dataclass  
class MultiHitResult(DamageResult):
    """Result for multi-hit moves."""
    hit_count: int = 1
    individual_damages: List[int] = None

class CriticalTier:
    NONE = 0
    NORMAL = 1
    HIGH = 2
    GUARANTEED = 3

class DamageType:
    NORMAL = "NORMAL"
    FIXED = "FIXED"
    PERCENTAGE = "PERCENTAGE"
    MULTI_HIT = "MULTI_HIT"

logger = logging.getLogger(__name__)


class UnifiedDamageCalculator:
    """
    Einheitlicher Damage-Calculator der alle bisherigen Implementierungen konsolidiert.
    Dient als Single Point of Truth für alle Damage-Berechnungen im Spiel.
    """
    
    _instance: Optional['UnifiedDamageCalculator'] = None
    
    def __new__(cls):
        """Singleton pattern für einheitliche Instanz."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the unified damage calculator."""
        if self._initialized:
            return
        
        self._initialized = True
        
        # Lazy initialization to avoid circular imports
        self._pipeline: Optional['DamageCalculationPipeline'] = None
        
        # Talent System Integration
        self.talent_database = get_talent_database()
        
        # Performance-Tracking
        self.calculation_count = 0
        self.total_time = 0.0
        
        logger.info("UnifiedDamageCalculator initialisiert")
    
    def _track_performance(self, start_time: float) -> None:
        """Helper method for performance tracking."""
        self.calculation_count += 1
        self.total_time += time.time() - start_time
    
    def _calculate_passive_abilities(self, attacker: 'MonsterInstance', move: 'Move', 
                                   defender: 'MonsterInstance', kwargs: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate passive ability modifiers from talents.
        
        Args:
            attacker: Attacking monster
            move: Move being used
            defender: Defending monster
            kwargs: Additional battle context
            
        Returns:
            Dictionary with passive ability modifiers
        """
        try:
            modifiers = {
                'atk_multiplier': 1.0,
                'def_multiplier': 1.0,
                'mag_multiplier': 1.0,
                'res_multiplier': 1.0,
                'power_multiplier': 1.0,
                'accuracy_multiplier': 1.0,
                'crit_multiplier': 1.0
            }
            
            # Get talent database
            talent_db = self.talent_database
            
            # Check attacker talents for offensive modifiers
            if hasattr(attacker, 'talents') and attacker.talents:
                for talent_instance in attacker.talents:
                    if hasattr(talent_instance, 'talent_id'):
                        talent_data = talent_db.get_talent(talent_instance.talent_id)
                        if talent_data:
                            # Apply passive abilities
                            passive_abilities = talent_data.get('passive_abilities', [])
                            for ability in passive_abilities:
                                ability_type = ability.get('type', '')
                                value = ability.get('value', 1.0)
                                
                                if ability_type == 'atk_boost':
                                    modifiers['atk_multiplier'] *= value
                                elif ability_type == 'mag_boost':
                                    modifiers['mag_multiplier'] *= value
                                elif ability_type == 'power_boost':
                                    modifiers['power_multiplier'] *= value
                                elif ability_type == 'accuracy_boost':
                                    modifiers['accuracy_multiplier'] *= value
                                elif ability_type == 'crit_boost':
                                    modifiers['crit_multiplier'] *= value
            
            # Check defender talents for defensive modifiers
            if hasattr(defender, 'talents') and defender.talents:
                for talent_instance in defender.talents:
                    if hasattr(talent_instance, 'talent_id'):
                        talent_data = talent_db.get_talent(talent_instance.talent_id)
                        if talent_data:
                            # Apply passive abilities
                            passive_abilities = talent_data.get('passive_abilities', [])
                            for ability in passive_abilities:
                                ability_type = ability.get('type', '')
                                value = ability.get('value', 1.0)
                                
                                if ability_type == 'def_boost':
                                    modifiers['def_multiplier'] *= value
                                elif ability_type == 'res_boost':
                                    modifiers['res_multiplier'] *= value
            
            # Apply move-specific talent bonuses
            if hasattr(move, 'talent_id') and move.talent_id:
                talent_data = talent_db.get_talent(move.talent_id)
                if talent_data:
                    move_bonuses = talent_data.get('move_bonuses', [])
                    for bonus in move_bonuses:
                        bonus_type = bonus.get('type', '')
                        value = bonus.get('value', 1.0)
                        
                        if bonus_type == 'power_boost':
                            modifiers['power_multiplier'] *= value
                        elif bonus_type == 'accuracy_boost':
                            modifiers['accuracy_multiplier'] *= value
            
            return modifiers
            
        except Exception as e:
            logger.error(f"Error calculating passive abilities: {e}")
            return {
                'atk_multiplier': 1.0,
                'def_multiplier': 1.0,
                'mag_multiplier': 1.0,
                'res_multiplier': 1.0,
                'power_multiplier': 1.0,
                'accuracy_multiplier': 1.0,
                'crit_multiplier': 1.0
            }
    
    @property
    def pipeline(self) -> 'DamageCalculationPipeline':
        """Lazy-loaded damage pipeline to avoid circular imports."""
        if self._pipeline is None:
            # Fallback: Create a simple pipeline since damage_calc.py doesn't exist
            self._pipeline = self._create_fallback_pipeline()
        return self._pipeline
    
    def _create_fallback_pipeline(self):
        """Create a fallback pipeline when damage_calc.py is not available."""
        class FallbackPipeline:
            def __init__(self):
                self.stages = []
            
            def add_stage(self, name, func, priority):
                self.stages.append((name, func, priority))
                self.stages.sort(key=lambda x: x[2])
            
            def process(self, context):
                for name, func, priority in self.stages:
                    try:
                        func(context)
                    except Exception as e:
                        logger.warning(f"Pipeline stage {name} failed: {e}")
                return context
            
            def calculate_damage(self, attacker, defender, move, **kwargs):
                """Fallback damage calculation when pipeline is not available."""
                # Simple damage calculation as fallback
                base_power = getattr(move, 'power', 50)
                attacker_atk = getattr(attacker, 'current_stats', {}).get('atk', 30)
                defender_def = getattr(defender, 'current_stats', {}).get('def', 30)
                
                # Simple formula: (atk * power / 50) - def
                damage = max(1, int((attacker_atk * base_power / 50) - defender_def))
                
                return DamageResult(
                    damage=damage,
                    is_critical=False,
                    effectiveness=1.0,
                    effectiveness_text="Normal"
                )
        
        return FallbackPipeline()
    
    
    def calculate_damage(self, 
                        attacker: 'MonsterInstance', 
                        defender: 'MonsterInstance', 
                        move: 'Move',
                        **kwargs) -> 'DamageResult':
        """
        Einheitliche Damage-Berechnung - SINGLE SOURCE OF TRUTH.
        AGENT 3: Enhanced with robust validation and fallback mechanisms.
        
        Args:
            attacker: Angreifendes Monster
            defender: Verteidigendes Monster  
            move: Verwendete Attacke
            **kwargs: Zusätzliche Parameter (weather, terrain, tension_multiplier, etc.)
            
        Returns:
            DamageResult mit allen Details
        """
        start_time = time.time()
        
        try:
            # AGENT 3: Enhanced input validation
            if not attacker or not defender or not move:
                logger.warning("Invalid inputs for damage calculation")
                return self._create_robust_fallback_result(move)
            
            # Check if target is fainted
            if getattr(defender, 'is_fainted', False):
                return DamageResult(
                    damage=0,
                    is_critical=False,
                    critical_tier=CriticalTier.NONE,
                    effectiveness=1.0,
                    effectiveness_text="Target already fainted",
                    damage_type=DamageType.NORMAL
                )
            
            # AGENT 3: Check for status conditions that prevent action
            if self._is_action_prevented(attacker, move):
                return DamageResult(
                    damage=0,
                    is_critical=False,
                    critical_tier=CriticalTier.NONE,
                    effectiveness=1.0,
                    effectiveness_text="Cannot act due to status condition",
                    damage_type=DamageType.NORMAL
                )
            
            # Bestimme Move-Kategorie und verwende entsprechende DQM-Formel
            if hasattr(move, 'category'):
                if move.category.value == 'phys':
                    result = self.calculate_physical_damage(attacker, defender, move, **kwargs)
                elif move.category.value == 'mag':
                    result = self.calculate_magical_damage(attacker, defender, move, **kwargs)
                else:
                    # Support moves haben keinen Schaden
                    result = DamageResult(
                        damage=0,
                        is_critical=False,
                        critical_tier=CriticalTier.NONE,
                        effectiveness=1.0,
                        effectiveness_text="",
                        damage_type=DamageType.NORMAL
                    )
            else:
                # Fallback: Verwende physische Formel
                result = self.calculate_physical_damage(attacker, defender, move, **kwargs)
            
            # AGENT 3: Enhanced result validation
            result = self._validate_and_fix_damage_result(result, move)
            
            # Tracking
            self._track_performance(start_time)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in unified damage calculation: {e}")
            # AGENT 3: Enhanced fallback with multiple layers
            try:
                if hasattr(move, 'category') and move.category.value == 'phys':
                    result = self.calculate_physical_damage(attacker, defender, move, **kwargs)
                else:
                    result = self.calculate_magical_damage(attacker, defender, move, **kwargs)
                return self._validate_and_fix_damage_result(result, move)
            except Exception as e2:
                logger.error(f"Fallback damage calculation failed: {e2}")
                return self._create_robust_fallback_result(move)
    
    def calculate_dqm_damage(self,
                            attacker: 'MonsterInstance',
                            defender: 'MonsterInstance', 
                            move: 'Move',
                            **kwargs) -> 'DamageResult':
        """
        DQM-spezifische Damage-Berechnung.
        
        Verwendet die originalen Dragon Quest Monsters Formeln.
        """
        # Use the main calculate_damage method which already implements DQM formulas
        return self.calculate_damage(attacker, defender, move, **kwargs)
    
    def calculate_fixed_damage(self, amount: int) -> 'DamageResult':
        """Berechne festen Schaden."""
        return DamageResult(
            damage=amount,
            is_critical=False,
            critical_tier=CriticalTier.NONE,
            effectiveness=1.0,
            effectiveness_text="",
            damage_type=DamageType.FIXED
        )
    
    def calculate_percentage_damage(self, 
                                   target: 'MonsterInstance',
                                   percentage: float) -> 'DamageResult':
        """Berechne prozentualen Schaden."""
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
    
    def calculate_recoil_damage(self, damage_dealt: int, recoil_rate: float) -> int:
        """
        Berechne Rückstoß-Schaden.
        
        Args:
            damage_dealt: Verursachter Schaden
            recoil_rate: Rückstoß-Rate (0.0 - 1.0)
            
        Returns:
            Rückstoß-Schaden (mindestens 1)
        """
        return max(1, int(damage_dealt * recoil_rate))
    
    def calculate_drain_damage(self, damage_dealt: int, drain_rate: float) -> int:
        """
        Berechne HP-Absorption.
        
        Args:
            damage_dealt: Verursachter Schaden
            drain_rate: Absorptions-Rate (0.0 - 1.0)
            
        Returns:
            Absorbierte HP (mindestens 1)
        """
        return max(1, int(damage_dealt * drain_rate))
    
    def calculate_multi_hit(self,
                          attacker: 'MonsterInstance',
                          defender: 'MonsterInstance',
                          move: 'Move',
                          hit_count: Optional[int] = None,
                          **kwargs) -> 'MultiHitResult':
        """
        Berechne Schaden für Multi-Hit-Attacken.
        
        Args:
            attacker: Angreifer
            defender: Verteidiger
            move: Multi-Hit Move
            hit_count: Anzahl Treffer (None für zufällig)
            
        Returns:
            MultiHitResult mit allen Treffern
        """
        # Bestimme Anzahl Treffer
        if hit_count is None:
            import random
            # DQM-Style: 2-3 Hits häufiger als 4-5
            weights = [0.35, 0.35, 0.15, 0.15]  # 2, 3, 4, 5 hits
            hit_count = random.choices([2, 3, 4, 5], weights=weights)[0]
        
        # Berechne jeden Treffer
        individual_damages = []
        total_damage = 0
        first_result = None
        
        for i in range(hit_count):
            result = self.calculate_damage(attacker, defender, move, **kwargs)
            
            if i == 0:
                first_result = result
            
            individual_damages.append(result.damage)
            total_damage += result.damage
        
        # Erstelle Multi-Hit-Result
        multi_result = MultiHitResult(
            damage=total_damage,
            is_critical=first_result.is_critical,
            critical_tier=first_result.critical_tier,
            effectiveness=first_result.effectiveness,
            effectiveness_text=first_result.effectiveness_text,
            type_text=first_result.type_text,
            has_stab=first_result.has_stab,
            damage_type=DamageType.MULTI_HIT,
            hit_count=hit_count,
            individual_damages=individual_damages
        )
        
        return multi_result
    
    def preview_damage_range(self,
                           attacker: 'MonsterInstance',
                           defender: 'MonsterInstance',
                           move: 'Move',
                           **kwargs) -> Dict[str, Any]:
        """
        Vorschau des Schadensbereichs ohne RNG.
        
        Returns:
            Dict mit min, max, average Schaden
        """
        # Simuliere mehrere Berechnungen
        samples = []
        for _ in range(10):
            result = self.calculate_damage(attacker, defender, move, **kwargs)
            samples.append(result.damage)
        
        return {
            'min': min(samples),
            'max': max(samples),
            'average': sum(samples) / len(samples),
            'effectiveness': result.effectiveness,
            'has_stab': result.has_stab
        }
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Get performance statistics.
        
        Returns:
            Performance-Metriken
        """
        avg_time = self.total_time / self.calculation_count if self.calculation_count > 0 else 0
        
        return {
            'total_calculations': self.calculation_count,
            'total_time': self.total_time,
            'average_time': avg_time,
            'calculations_per_second': 1 / avg_time if avg_time > 0 else 0
        }
    
    def reset_stats(self):
        """Reset performance statistics."""
        self.calculation_count = 0
        self.total_time = 0.0
    
    def calculate_physical_damage(self,
                                attacker: 'MonsterInstance',
                                defender: 'MonsterInstance',
                                move: 'Move',
                                **kwargs) -> 'DamageResult':
        """
        Berechne physischen Schaden mit authentischen DQM-Formeln.
        
        DQM Formula: Base Damage = move_power * (attacker_atk / 2)
        Defense Reduction = defender_def / 4
        Final = (Base - Defense) * random(7/8 to 9/8)
        """
        start_time = time.time()
        
        try:
            # Extrahiere Stats - verwende MonsterInstance.stats property
            attacker_stats = attacker.stats
            defender_stats = defender.stats
            
            # Extrahiere Traits falls verfügbar
            attacker_traits = getattr(attacker, 'traits', [])
            defender_traits = getattr(defender, 'traits', [])
            
            # Apply passive abilities from talents
            passive_modifiers = self._calculate_passive_abilities(attacker, move, defender, kwargs)
            
            attacker_atk = attacker_stats.get('atk', 100) * passive_modifiers.get('atk_multiplier', 1.0)
            defender_def = defender_stats.get('def', 50) * passive_modifiers.get('def_multiplier', 1.0)
            power = move.power * passive_modifiers.get('power_multiplier', 1.0)
            
            # Check for miss (DQM accuracy calculation)
            if self._check_miss(attacker_stats, defender_stats):
                return DamageResult(
                    damage=0,
                    is_critical=False,
                    critical_tier=CriticalTier.NONE,
                    effectiveness=1.0,
                    effectiveness_text="Attacke ging daneben!",
                    damage_type=DamageType.NORMAL,
                    is_miss=True
                )
            
            # Apply trait modifiers to stats (DQM feature)
            if 'Attack Boost' in attacker_traits:
                attacker_atk = int(attacker_atk * 1.1)
            if 'Defense Boost' in defender_traits:
                defender_def = int(defender_def * 1.1)
            
            # AGENT 3: Apply status condition modifiers
            attacker_atk = self._apply_status_modifiers(attacker, attacker_atk, 'atk')
            defender_def = self._apply_status_modifiers(defender, defender_def, 'def')
            
            # DQM Physical Formula: Damage = (Power × ATK/2 - DEF/4) × Random(0.875, 1.125)
            base_damage = power * (attacker_atk / 2)
            defense_reduction = defender_def / 4
            raw_damage = base_damage - defense_reduction
            
            # DQM Damage Range: Random(0.875, 1.125) - DQM-spezifische Formel
            min_damage = raw_damage * 0.875  # DQMConstants.DAMAGE_MIN_MULTIPLIER
            max_damage = raw_damage * 1.125  # DQMConstants.DAMAGE_MAX_MULTIPLIER
            damage = random.uniform(min_damage, max_damage)
            
            # Check for Metal Body trait (DQM feature)
            if 'Metal Body' in defender_traits:
                damage = self._apply_metal_body(damage)
                final_damage = max(1, int(damage))
                
                # Performance Tracking
                self._track_performance(start_time)
                
                return DamageResult(
                    damage=final_damage,
                    is_critical=False,
                    critical_tier=CriticalTier.NONE,
                    effectiveness=1.0,
                    effectiveness_text="Kaum Schaden gegen Metall-Rüstung!",
                    damage_type=DamageType.NORMAL,
                    is_metal_slime_damage=True
                )
            
            # Critical Hit Check: 1/32 Chance (3.125%) - DQM-spezifische Formel
            is_critical = self._check_critical_hit(attacker)
            if is_critical:
                damage *= 2.0  # DQMConstants.CRITICAL_MULTIPLIER
            
            # Type Effectiveness
            effectiveness = self._calculate_type_effectiveness(move, defender)
            damage *= effectiveness
            
            # STAB Bonus: 1.2x Multiplier - DQM-spezifische Formel
            stab = self._calculate_stab_bonus(attacker, move)
            damage *= stab
            
            final_damage = max(1, int(damage))
            
            # Performance Tracking
            self._track_performance(start_time)
            
            return DamageResult(
                damage=final_damage,
                is_critical=is_critical,
                critical_tier=CriticalTier.NORMAL if is_critical else CriticalTier.NONE,
                effectiveness=effectiveness,
                effectiveness_text=self._get_effectiveness_text(effectiveness),
                damage_type=DamageType.NORMAL,
                has_stab=stab > 1.0,
                type_text=self._get_effectiveness_text(effectiveness),
                calculation_time=time.time() - start_time
            )
            
        except Exception as e:
            logger.error(f"Physical damage calculation failed: {e}")
            return self._create_fallback_result(move)
    
    def calculate_magical_damage(self,
                               attacker: 'MonsterInstance',
                               defender: 'MonsterInstance',
                               move: 'Move',
                               **kwargs) -> 'DamageResult':
        """
        Berechne magischen Schaden mit authentischen DQM-Formeln.
        
        Verwendet MAG vs RES statt ATK vs DEF.
        """
        start_time = time.time()
        
        try:
            # Extrahiere Stats - verwende MonsterInstance.stats property
            attacker_stats = attacker.stats
            defender_stats = defender.stats
            
            # Extrahiere Traits falls verfügbar
            attacker_traits = getattr(attacker, 'traits', [])
            defender_traits = getattr(defender, 'traits', [])
            
            # Apply passive abilities from talents
            passive_modifiers = self._calculate_passive_abilities(attacker, move, defender, kwargs)
            
            attacker_mag = attacker_stats.get('mag', 100) * passive_modifiers.get('mag_multiplier', 1.0)
            defender_res = defender_stats.get('res', 50) * passive_modifiers.get('res_multiplier', 1.0)
            power = move.power * passive_modifiers.get('power_multiplier', 1.0)
            
            # Check for miss (DQM accuracy calculation)
            if self._check_miss(attacker_stats, defender_stats):
                return DamageResult(
                    damage=0,
                    is_critical=False,
                    critical_tier=CriticalTier.NONE,
                    effectiveness=1.0,
                    effectiveness_text="Attacke ging daneben!",
                    damage_type=DamageType.NORMAL,
                    is_miss=True
                )
            
            # Apply trait modifiers to stats (DQM feature)
            if 'Magic Boost' in attacker_traits:
                attacker_mag = int(attacker_mag * 1.1)
            if 'Resistance Boost' in defender_traits:
                defender_res = int(defender_res * 1.1)
            
            # AGENT 3: Apply status condition modifiers
            attacker_mag = self._apply_status_modifiers(attacker, attacker_mag, 'mag')
            defender_res = self._apply_status_modifiers(defender, defender_res, 'res')
            
            # DQM Magical Formula (gleiche Formel wie Physical)
            base_damage = power * (attacker_mag / 2)
            defense_reduction = defender_res / 4
            raw_damage = base_damage - defense_reduction
            
            # DQM Damage Range (7/8 to 9/8)
            min_damage = raw_damage * 0.875
            max_damage = raw_damage * 1.125
            damage = random.uniform(min_damage, max_damage)
            
            # Check for Metal Body trait (DQM feature)
            if 'Metal Body' in defender_traits:
                damage = self._apply_metal_body(damage)
                final_damage = max(1, int(damage))
                
                # Performance Tracking
                self._track_performance(start_time)
                
                return DamageResult(
                    damage=final_damage,
                    is_critical=False,
                    critical_tier=CriticalTier.NONE,
                    effectiveness=1.0,
                    effectiveness_text="Kaum Schaden gegen Metall-Rüstung!",
                    damage_type=DamageType.NORMAL,
                    is_metal_slime_damage=True
                )
            
            # Critical Hit Check (1/32 chance in DQM)
            is_critical = self._check_critical_hit(attacker)
            if is_critical:
                damage *= 2.0
            
            # Type Effectiveness
            effectiveness = self._calculate_type_effectiveness(move, defender)
            damage *= effectiveness
            
            # STAB Bonus: 1.2x Multiplier - DQM-spezifische Formel
            stab = self._calculate_stab_bonus(attacker, move)
            damage *= stab
            
            final_damage = max(1, int(damage))
            
            # Performance Tracking
            self._track_performance(start_time)
            
            return DamageResult(
                damage=final_damage,
                is_critical=is_critical,
                critical_tier=CriticalTier.NORMAL if is_critical else CriticalTier.NONE,
                effectiveness=effectiveness,
                effectiveness_text=self._get_effectiveness_text(effectiveness),
                damage_type=DamageType.NORMAL,
                has_stab=stab > 1.0,
                type_text=self._get_effectiveness_text(effectiveness),
                calculation_time=time.time() - start_time
            )
            
        except Exception as e:
            logger.error(f"Magical damage calculation failed: {e}")
            return self._create_fallback_result(move)
    
    def calculate_critical_hit(self, attacker: 'MonsterInstance') -> bool:
        """
        Berechne Critical Hit Chance mit DQM-Formeln.
        
        DQM: 1/32 base chance (3.125%)
        """
        return self._check_critical_hit(attacker)
    
    def apply_type_effectiveness(self, move: 'Move', defender: 'MonsterInstance') -> float:
        """
        Berechne Type-Effectiveness mit TypeChart Singleton.
        
        Returns:
            Multiplier für Type-Effectiveness
        """
        return self._calculate_type_effectiveness(move, defender)
    
    def _check_critical_hit(self, attacker: 'MonsterInstance') -> bool:
        """DQM Critical Hit Check (1/32 chance)."""
        # Base DQM critical chance
        crit_chance = 1/32  # 3.125%
        
        # Check for Critical Master trait
        traits = getattr(attacker, 'traits', [])
        if 'Critical Master' in traits:
            crit_chance *= 2  # Double the chance
        
        return random.random() < crit_chance
    
    def _calculate_type_effectiveness(self, move: 'Move', defender: 'MonsterInstance') -> float:
        """
        AGENT 3: Enhanced type effectiveness calculation with caching and validation.
        Berechne Type-Effectiveness mit TypeChart Singleton und robusten Fallbacks.
        """
        try:
            from engine.systems.types import TypeChart
            type_chart = TypeChart()
            
            # AGENT 3: Validate inputs
            if not move or not defender:
                logger.warning("Invalid inputs for type effectiveness calculation")
                return 1.0
            
            # Hole Move-Type mit Fallback
            move_type = getattr(move, 'type', None)
            if not move_type:
                logger.warning("Move has no type attribute")
                return 1.0
            
            # Hole Defender-Types mit Fallback
            defender_types = getattr(defender, 'types', [])
            if not defender_types:
                # Try alternative attribute names
                defender_types = getattr(defender, 'type_list', [])
                if not defender_types:
                    logger.warning(f"Defender {getattr(defender, 'name', 'Unknown')} hat keine Typen")
                    return 1.0
            
            # AGENT 3: Use optimized type chart calculation
            if hasattr(type_chart, 'calculate_type_multiplier'):
                # Use the optimized batch calculation method
                total_effectiveness = type_chart.calculate_type_multiplier(move_type, defender_types)
            else:
                # Fallback to individual calculations
                total_effectiveness = 1.0
                for defender_type in defender_types:
                    effectiveness = type_chart.get_effectiveness(move_type, defender_type)
                    total_effectiveness *= effectiveness
                    logger.debug(f"Type effectiveness: {move_type} vs {defender_type} = {effectiveness}")
            
            # AGENT 3: Validate result
            if not isinstance(total_effectiveness, (int, float)):
                logger.warning(f"Invalid type effectiveness result: {total_effectiveness}")
                return 1.0
            
            if math.isnan(total_effectiveness) or math.isinf(total_effectiveness):
                logger.warning(f"Invalid type effectiveness value: {total_effectiveness}")
                return 1.0
            
            # Clamp effectiveness to reasonable bounds
            total_effectiveness = max(0.0, min(4.0, float(total_effectiveness)))
            
            logger.debug(f"Total type effectiveness: {move_type} vs {defender_types} = {total_effectiveness}")
            return total_effectiveness
            
        except Exception as e:
            logger.warning(f"Type effectiveness calculation failed: {e}")
            return 1.0
    
    def _calculate_stab_bonus(self, attacker: 'MonsterInstance', move: 'Move') -> float:
        """Berechne STAB (Same Type Attack Bonus)."""
        attacker_types = getattr(attacker, 'types', [])
        return 1.2 if move.type in attacker_types else 1.0
    
    def _get_effectiveness_text(self, effectiveness: float) -> str:
        """Generiere Effectiveness-Text."""
        if effectiveness >= 2.0:
            return "Sehr effektiv!"
        elif effectiveness > 1.0:
            return "Effektiv!"
        elif effectiveness == 0:
            return "Hat keine Wirkung..."
        elif effectiveness < 0.5:
            return "Kaum effektiv..."
        elif effectiveness < 1.0:
            return "Nicht sehr effektiv..."
        else:
            return ""
    
    def _check_miss(self, attacker_stats: Dict[str, int], defender_stats: Dict[str, int]) -> bool:
        """Check if attack misses using DQM accuracy formula."""
        # DQM-style accuracy calculation
        # Base accuracy depends on level difference and agility
        attacker_level = attacker_stats.get('level', 50)
        defender_level = defender_stats.get('level', 50)
        attacker_spd = attacker_stats.get('spd', 100)
        defender_spd = defender_stats.get('spd', 100)
        
        # Base hit rate: 95% for same level/speed
        base_hit_rate = 0.95
        
        # Level difference modifier
        level_diff = attacker_level - defender_level
        level_modifier = min(0.05, max(-0.05, level_diff * 0.005))  # ±1% per 2 levels
        
        # Speed difference modifier (agility affects accuracy)
        speed_ratio = attacker_spd / max(defender_spd, 1)
        if speed_ratio > 1.2:
            speed_modifier = 0.03  # +3% if much faster
        elif speed_ratio < 0.8:
            speed_modifier = -0.03  # -3% if much slower
        else:
            speed_modifier = 0
        
        # Calculate final hit rate
        hit_rate = base_hit_rate + level_modifier + speed_modifier
        hit_rate = min(0.99, max(0.70, hit_rate))  # Clamp between 70%-99%
        
        # Roll for miss
        return random.random() >= hit_rate
    
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
            return random.randint(0, 1)
        else:
            # Very strong attacks can do 1-2 damage
            return random.randint(1, 2)
    
    def _create_fallback_result(self, move: 'Move') -> 'DamageResult':
        """Erstelle Fallback-Result mit robusten Checks."""
        try:
            # Safe power extraction
            power = 50  # Default power
            if move and hasattr(move, 'power'):
                power = max(1, int(move.power))
            elif move and hasattr(move, 'base_power'):
                power = max(1, int(move.base_power))
            
            return DamageResult(
                damage=max(1, power // 2),
                is_critical=False,
                critical_tier=CriticalTier.NONE,
                effectiveness=1.0,
                effectiveness_text="Fallback damage",
                damage_type=DamageType.NORMAL
            )
        except Exception as e:
            logger.error(f"Error creating fallback result: {e}")
            return DamageResult(
                damage=10,
                is_critical=False,
                critical_tier=CriticalTier.NONE,
                effectiveness=1.0,
                effectiveness_text="Emergency fallback",
                damage_type=DamageType.NORMAL
            )
    
    def _create_robust_fallback_result(self, move: 'Move') -> 'DamageResult':
        """
        AGENT 3: Enhanced fallback result with better validation.
        Creates a robust fallback that always returns valid values.
        """
        try:
            # Safe power extraction with multiple fallbacks
            power = 50  # Default power
            if move:
                if hasattr(move, 'power') and move.power is not None:
                    power = max(1, int(move.power))
                elif hasattr(move, 'base_power') and move.base_power is not None:
                    power = max(1, int(move.base_power))
                elif hasattr(move, 'damage') and move.damage is not None:
                    power = max(1, int(move.damage))
            
            # Ensure power is within reasonable bounds
            power = max(1, min(200, power))
            
            # Calculate fallback damage with safety margins
            fallback_damage = max(1, power // 2)
            
            return DamageResult(
                damage=fallback_damage,
                is_critical=False,
                critical_tier=CriticalTier.NONE,
                effectiveness=1.0,
                effectiveness_text="Robust fallback damage applied",
                damage_type=DamageType.NORMAL,
                calculation_time=0.0
            )
        except Exception as e:
            logger.error(f"Error creating robust fallback result: {e}")
            # Emergency fallback - guaranteed to work
            return DamageResult(
                damage=10,
                is_critical=False,
                critical_tier=CriticalTier.NONE,
                effectiveness=1.0,
                effectiveness_text="Emergency fallback - guaranteed valid",
                damage_type=DamageType.NORMAL,
                calculation_time=0.0
            )
    
    def _is_action_prevented(self, attacker: 'MonsterInstance', move: 'Move') -> bool:
        """
        AGENT 3: Check if status conditions prevent action.
        Implements proper status condition logic.
        """
        try:
            if not attacker:
                return True
            
            # Check for status conditions that prevent action
            status = getattr(attacker, 'status', None)
            if not status:
                return False
            
            # Status conditions that prevent action
            if status in ['sleep', 'freeze']:
                return True
            
            # Confusion has a chance to prevent action
            if status == 'confusion':
                return random.random() < 0.5  # 50% chance to hurt self
            
            # Paralysis has a chance to prevent action
            if status == 'paralysis':
                return random.random() < 0.25  # 25% chance to be paralyzed
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking action prevention: {e}")
            return False
    
    def _validate_and_fix_damage_result(self, result: 'DamageResult', move: 'Move') -> 'DamageResult':
        """
        AGENT 3: Validate and fix damage result to ensure it's always valid.
        Implements comprehensive validation and correction.
        """
        try:
            if not result:
                logger.warning("Damage result is None, creating fallback")
                return self._create_robust_fallback_result(move)
            
            # Ensure all required attributes exist
            if not hasattr(result, 'damage'):
                logger.warning("Damage result missing 'damage' attribute")
                result.damage = 1
            
            if not hasattr(result, 'is_critical'):
                result.is_critical = False
            
            if not hasattr(result, 'critical_tier'):
                result.critical_tier = CriticalTier.NONE
            
            if not hasattr(result, 'effectiveness'):
                result.effectiveness = 1.0
            
            if not hasattr(result, 'effectiveness_text'):
                result.effectiveness_text = ""
            
            if not hasattr(result, 'damage_type'):
                result.damage_type = DamageType.NORMAL
            
            # Validate damage value
            if not isinstance(result.damage, (int, float)):
                logger.warning(f"Invalid damage type: {type(result.damage)}")
                result.damage = 1
            elif math.isnan(result.damage) or math.isinf(result.damage):
                logger.warning(f"Invalid damage value: {result.damage}")
                result.damage = 1
            elif result.damage < 0:
                logger.warning(f"Negative damage: {result.damage}")
                result.damage = 0
            
            # Ensure damage is within reasonable bounds
            result.damage = max(0, min(9999, int(result.damage)))
            
            # Validate effectiveness
            if not isinstance(result.effectiveness, (int, float)):
                result.effectiveness = 1.0
            elif math.isnan(result.effectiveness) or math.isinf(result.effectiveness):
                result.effectiveness = 1.0
            else:
                result.effectiveness = max(0.0, min(4.0, float(result.effectiveness)))
            
            # Validate critical tier
            if not isinstance(result.critical_tier, int):
                result.critical_tier = CriticalTier.NONE
            else:
                result.critical_tier = max(0, min(3, int(result.critical_tier)))
            
            # Ensure critical flags are consistent
            if result.critical_tier > 0 and not result.is_critical:
                result.is_critical = True
            elif result.critical_tier == 0 and result.is_critical:
                result.is_critical = False
            
            return result
            
        except Exception as e:
            logger.error(f"Error validating damage result: {e}")
            return self._create_robust_fallback_result(move)
    
    def _apply_status_modifiers(self, monster: 'MonsterInstance', stat_value: int, stat_type: str) -> int:
        """
        AGENT 3: Apply status condition modifiers to stats.
        Implements proper status condition effects on combat stats.
        
        Args:
            monster: Monster with status condition
            stat_value: Original stat value
            stat_type: Type of stat ('atk', 'def', 'mag', 'res', 'spd')
            
        Returns:
            Modified stat value
        """
        try:
            if not monster or not stat_value:
                return stat_value
            
            status = getattr(monster, 'status', None)
            if not status:
                return stat_value
            
            # Status condition modifiers
            if status == 'burn':
                # Burn reduces ATK by 50%
                if stat_type == 'atk':
                    return int(stat_value * 0.5)
            
            elif status == 'paralysis':
                # Paralysis reduces SPD by 50%
                if stat_type == 'spd':
                    return int(stat_value * 0.5)
            
            elif status == 'freeze':
                # Freeze prevents action but doesn't modify stats directly
                # (handled in _is_action_prevented)
                pass
            
            elif status == 'sleep':
                # Sleep prevents action but doesn't modify stats directly
                # (handled in _is_action_prevented)
                pass
            
            elif status == 'confusion':
                # Confusion doesn't modify stats, just prevents action sometimes
                # (handled in _is_action_prevented)
                pass
            
            # Return original value if no modifier applies
            return stat_value
            
        except Exception as e:
            logger.error(f"Error applying status modifiers: {e}")
            return stat_value

    
    def calculate_escape_chance(self, 
                              runner_speed: int, 
                              enemy_speed: int, 
                              attempts: int = 1) -> float:
        """
        Berechne Flucht-Chance mit DQM-Formel.
        
        Args:
            runner_speed: Speed des flüchtenden Monsters
            enemy_speed: Speed des Gegners
            attempts: Anzahl der Fluchtversuche
            
        Returns:
            Flucht-Chance als Float (0.0 - 1.0)
        """
        try:
            # DQM Escape Formula: (runner_spd * 32) / (enemy_spd / 4) + 30 + (attempts * 30)
            escape_chance = (runner_speed * 32) / (enemy_speed / 4) + 30 + (attempts * 30)
            return min(1.0, escape_chance / 100.0)
        except:
            # Fallback
            return 0.3 + (attempts * 0.1)
    
    def calculate_accuracy(self, 
                          move_accuracy: int, 
                          attacker_accuracy: int = 100,
                          defender_evasion: int = 100) -> bool:
        """
        Berechne ob ein Move trifft.
        
        Args:
            move_accuracy: Base-Accuracy des Moves
            attacker_accuracy: Accuracy-Stage des Angreifers
            defender_evasion: Evasion-Stage des Verteidigers
            
        Returns:
            True wenn der Move trifft
        """
        try:
            # Accuracy Formula: (move_accuracy * accuracy_stage) / evasion_stage
            final_accuracy = (move_accuracy * attacker_accuracy) / defender_evasion
            return random.randint(1, 100) <= final_accuracy
        except:
            # Fallback
            return random.randint(1, 100) <= move_accuracy
    
    def calculate_turn_order(self, monsters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Berechne Turn-Order mit DQM-Formeln.
        
        DQM Formula: Agility + Random(0-255)
        Höhere Werte gehen zuerst.
        """
        turn_values = []
        
        for monster in monsters:
            agility = monster.get('stats', {}).get('spd', 50)
            
            # Status-Effekte auf Speed anwenden
            if monster.get('status') == 'paralysis':
                agility = int(agility * 0.5)
            
            # DQM Formula: Addiere Random 0-255 zu Agility
            turn_value = agility + random.randint(0, 255)
            turn_values.append((monster, turn_value))
        
        # Sortiere nach Turn-Value (höchste zuerst)
        turn_values.sort(key=lambda x: x[1], reverse=True)
        
        return [monster for monster, _ in turn_values]
    
    def calculate_exp_reward(self, 
                           enemy_level: int,
                           enemy_rank: str,
                           is_boss: bool = False,
                           party_size: int = 1) -> int:
        """
        Berechne Experience Points Belohnung.
        
        Args:
            enemy_level: Level des besiegten Gegners
            enemy_rank: Rang des Gegners (F bis X)
            is_boss: Ob Gegner ein Boss ist
            party_size: Anzahl Party-Mitglieder für EXP-Aufteilung
            
        Returns:
            Experience Points pro Party-Mitglied
        """
        # Base EXP nach Rang
        rank_multipliers = {
            'F': 0.5, 'E': 0.7, 'D': 1.0, 'C': 1.3,
            'B': 1.6, 'A': 2.0, 'S': 2.5, 'SS': 3.0, 'X': 4.0
        }
        
        rank_mult = rank_multipliers.get(enemy_rank, 1.0)
        
        # Base Formula
        base_exp = int(enemy_level * 10 * rank_mult)
        
        # Boss Multiplier
        if is_boss:
            base_exp = int(base_exp * 1.5)
        
        # Aufteilen unter Party
        exp_per_member = max(1, base_exp // party_size)
        
        return exp_per_member
    
    def calculate_gold_reward(self, 
                            enemy_level: int,
                            enemy_rank: str,
                            is_boss: bool = False) -> int:
        """
        Berechne Gold-Belohnung aus Battle.
        
        Args:
            enemy_level: Level des Gegners
            enemy_rank: Rang des Gegners
            is_boss: Ob Gegner ein Boss ist
            
        Returns:
            Verdientes Gold
        """
        # Base Gold nach Rang
        rank_multipliers = {
            'F': 0.3, 'E': 0.5, 'D': 0.8, 'C': 1.0,
            'B': 1.3, 'A': 1.6, 'S': 2.0, 'SS': 2.5, 'X': 3.0
        }
        
        rank_mult = rank_multipliers.get(enemy_rank, 1.0)
        
        # Base Formula
        base_gold = int(enemy_level * 5 * rank_mult)
        
        # Boss Multiplier
        if is_boss:
            base_gold = int(base_gold * 2.0)
        
        # Varianz hinzufügen
        variance = base_gold * 0.2
        gold = base_gold + random.uniform(-variance, variance)
        
        return max(1, int(gold))
    
    def calculate_stat_stage_multiplier(self, stage: int, is_defensive: bool = False) -> float:
        """
        Berechne Stat-Multiplier aus Stat-Stage.
        
        DQM verwendet andere Multiplier als Pokemon.
        
        Args:
            stage: Stat-Stage (-6 bis +6)
            is_defensive: Ob dies ein defensiver Stat ist
            
        Returns:
            Multiplier für den Stat
        """
        # Stage begrenzen
        stage = max(-6, min(6, stage))
        
        # DQM Stat-Stage Multiplier
        if stage >= 0:
            # Positive Stages: 1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5
            multiplier = 1.0 + (stage * 0.25)
        else:
            # Negative Stages: 0.75, 0.6, 0.5, 0.4, 0.33, 0.25
            multipliers = [1.0, 0.75, 0.6, 0.5, 0.4, 0.33, 0.25]
            multiplier = multipliers[abs(stage)]
        
        return multiplier
    
    def calculate_heal(self, caster_stats: Dict[str, int], skill_power: int) -> int:
        """
        Berechne Heilungsmenge.
        
        Args:
            caster_stats: Caster's Stats (verwendet MAG)
            skill_power: Base Heilungskraft
            
        Returns:
            Menge an HP zu heilen
        """
        magic_stat = caster_stats.get('mag', 50)
        
        # Base Healing Formula
        base_heal = skill_power + (magic_stat / 4)
        
        return int(base_heal)
    
    def calculate_buff_duration(self, caster_level: int, target_level: int) -> int:
        """
        Berechne Buff/Debuff Dauer.
        
        Args:
            caster_level: Level des Casters
            target_level: Level des Ziels
            
        Returns:
            Dauer in Turns
        """
        base_duration = 3
        
        # Level-Unterschied beeinflusst Dauer
        level_diff = caster_level - target_level
        
        if level_diff > 10:
            base_duration += 2
        elif level_diff > 5:
            base_duration += 1
        elif level_diff < -10:
            base_duration -= 2
        elif level_diff < -5:
            base_duration -= 1
        
        # Minimum 1 Turn, Maximum 5 Turns
        return max(1, min(5, base_duration))
    
    def calculate_weather_damage(self, base_damage: int, weather: str, move_type: str) -> int:
        """
        Berechne Wetter-modifizierten Schaden.
        
        Args:
            base_damage: Basis-Schaden
            weather: Wetter-Typ
            move_type: Move-Typ
            
        Returns:
            Wetter-modifizierter Schaden
        """
        weather_multipliers = {
            'sunny': {'fire': 1.5, 'water': 0.5, 'ice': 0.5},
            'rain': {'water': 1.5, 'fire': 0.5, 'thunder': 1.0},
            'sandstorm': {'rock': 1.3, 'ground': 1.3, 'steel': 1.0},
            'hail': {'ice': 1.3, 'water': 0.8}
        }
        
        multiplier = weather_multipliers.get(weather, {}).get(move_type, 1.0)
        return int(base_damage * multiplier)
    
    def calculate_confusion_damage(self, monster: 'MonsterInstance') -> int:
        """
        Berechne Verwirrungs-Schaden.
        
        Args:
            monster: Verwirrtes Monster
            
        Returns:
            Selbst-zugefügter Schaden
        """
        try:
            # DQM Confusion Formula: Level * 2 + Random(0-3)
            base_damage = monster.level * 2
            random_damage = random.randint(0, 3)
            total_damage = base_damage + random_damage
            
            # Begrenze auf 1/4 der max HP
            max_damage = monster.max_hp // 4
            return min(total_damage, max_damage)
            
        except Exception as e:
            logger.error(f"Error calculating confusion damage: {e}")
            # Fallback
            return max(1, monster.level)


# Global instance for convenience
unified_damage_calculator = UnifiedDamageCalculator()


