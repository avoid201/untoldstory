"""
Damage calculation system for battles.
Implements Pokémon-style damage formula with modern mechanics.
"""

from typing import TYPE_CHECKING, Optional, Dict, Tuple
from dataclasses import dataclass
import random
import math

if TYPE_CHECKING:
    from engine.systems.monster_instance import MonsterInstance
    from engine.systems.moves import Move


@dataclass
class DamageResult:
    """Result of a damage calculation."""
    damage: int
    is_critical: bool
    effectiveness: float
    type_text: str  # "super effective", "not very effective", etc.
    blocked: bool = False
    missed: bool = False
    
    def get_effectiveness_text(self) -> str:
        """Get text description of effectiveness."""
        if self.effectiveness >= 2.0:
            return "Sehr effektiv!"
        elif self.effectiveness > 1.0:
            return "Effektiv!"
        elif self.effectiveness == 0:
            return "Hat keine Wirkung..."
        elif self.effectiveness < 1.0:
            return "Nicht sehr effektiv..."
        return ""


class DamageCalculator:
    """Handles all damage calculations for battles."""
    
    # Base critical hit chance (1/16 ≈ 6.25%)
    BASE_CRIT_RATE = 1/16
    
    # Critical hit damage multiplier
    CRIT_MULTIPLIER = 1.5
    
    # STAB (Same Type Attack Bonus) multiplier
    STAB_MULTIPLIER = 1.2
    
    # Random damage spread range
    RANDOM_MIN = 0.85
    RANDOM_MAX = 1.0
    
    def __init__(self, seed: Optional[int] = None):
        """
        Initialize damage calculator.
        
        Args:
            seed: Random seed for deterministic behavior
        """
        self.rng = random.Random(seed)
    
    def calculate(self, 
                 attacker: 'MonsterInstance',
                 defender: 'MonsterInstance', 
                 move: 'Move',
                 type_chart: Dict[Tuple[str, str], float]) -> DamageResult:
        """
        Calculate damage for a move.
        
        Args:
            attacker: Attacking monster
            defender: Defending monster
            move: Move being used
            type_chart: Type effectiveness chart
            
        Returns:
            DamageResult with damage and metadata
        """
        # Check if move hits
        if not self._check_accuracy(attacker, defender, move):
            return DamageResult(
                damage=0,
                is_critical=False,
                effectiveness=1.0,
                type_text="Daneben!",
                missed=True
            )
        
        # Support moves and moves with 0 power don't deal damage
        if move.category == 'support' or move.power <= 0:
            return DamageResult(
                damage=0,
                is_critical=False,
                effectiveness=1.0,
                type_text=""
            )
        
        # Get stats based on move category
        if move.category == 'phys':
            attack_stat = self._get_effective_stat(attacker, 'atk')
            defense_stat = self._get_effective_stat(defender, 'def')
        else:  # 'mag'
            attack_stat = self._get_effective_stat(attacker, 'mag')
            defense_stat = self._get_effective_stat(defender, 'res')
        
        # Check for critical hit
        is_critical = self._check_critical(attacker, move)
        
        # Apply critical hit stat stage bypassing
        if is_critical:
            # Ignore negative attack stages and positive defense stages
            if move.category == 'phys':
                if attacker.stat_stages.get('atk', 0) < 0:
                    attack_stat = attacker.stats['atk']
                if defender.stat_stages.get('def', 0) > 0:
                    defense_stat = defender.stats['def']
            else:
                if attacker.stat_stages.get('mag', 0) < 0:
                    attack_stat = attacker.stats['mag']
                if defender.stat_stages.get('res', 0) > 0:
                    defense_stat = defender.stats['res']
        
        # Base damage formula (Pokémon Gen V+)
        level = attacker.level
        power = move.power
        
        base_damage = (((2 * level / 5 + 2) * power * attack_stat / defense_stat) / 50) + 2
        base_damage = int(base_damage)
        
        # Apply modifiers
        damage = base_damage
        
        # Critical hit multiplier
        if is_critical:
            damage = int(damage * self.CRIT_MULTIPLIER)
        
        # STAB (Same Type Attack Bonus)
        if self._has_stab(attacker, move):
            damage = int(damage * self.STAB_MULTIPLIER)
        
        # Type effectiveness
        effectiveness = self._calculate_effectiveness(move.type, defender, type_chart)
        damage = int(damage * effectiveness)
        
        # Random spread (85-100%)
        random_factor = self.rng.uniform(self.RANDOM_MIN, self.RANDOM_MAX)
        damage = int(damage * random_factor)
        
        # Minimum damage is 1 (unless immune)
        if effectiveness > 0 and damage < 1:
            damage = 1
        
        # Apply damage reduction from burn
        if attacker.status == 'burn' and move.category == 'phys':
            damage = int(damage * 0.5)
        
        return DamageResult(
            damage=damage,
            is_critical=is_critical,
            effectiveness=effectiveness,
            type_text=self._get_effectiveness_text(effectiveness)
        )
    
    def _get_effective_stat(self, monster: 'MonsterInstance', stat: str) -> int:
        """
        Get effective stat value including stat stages.
        
        Args:
            monster: Monster to get stat from
            stat: Stat name ('atk', 'def', 'mag', 'res', 'spd')
            
        Returns:
            Effective stat value
        """
        base_stat = monster.stats.get(stat, 100)
        stage = monster.stat_stages.get(stat, 0)
        
        # Stat stage multipliers
        if stage >= 0:
            multiplier = (2 + stage) / 2
        else:
            multiplier = 2 / (2 - stage)
        
        return int(base_stat * multiplier)
    
    def _check_accuracy(self, attacker: 'MonsterInstance', 
                       defender: 'MonsterInstance',
                       move: 'Move') -> bool:
        """
        Check if a move hits.
        
        Args:
            attacker: Attacking monster
            defender: Defending monster
            move: Move being used
            
        Returns:
            True if move hits
        """
        # Moves with -1 accuracy always hit
        if move.accuracy < 0:
            return True
        
        # Get accuracy and evasion stages
        acc_stage = attacker.stat_stages.get('acc', 0)
        eva_stage = defender.stat_stages.get('eva', 0)
        
        # Combined stage for accuracy calculation
        combined_stage = acc_stage - eva_stage
        combined_stage = max(-6, min(6, combined_stage))
        
        # Accuracy multiplier from stages
        if combined_stage >= 0:
            stage_multiplier = (3 + combined_stage) / 3
        else:
            stage_multiplier = 3 / (3 - combined_stage)
        
        # Final accuracy
        final_accuracy = move.accuracy * stage_multiplier
        
        # Paralysis reduces accuracy by 25%
        if attacker.status == 'paralysis':
            final_accuracy *= 0.75
        
        # Roll for hit
        roll = self.rng.uniform(0, 100)
        return roll < final_accuracy
    
    def _check_critical(self, attacker: 'MonsterInstance', move: 'Move') -> bool:
        """
        Check if an attack is a critical hit.
        
        Args:
            attacker: Attacking monster
            move: Move being used
            
        Returns:
            True if critical hit
        """
        # Base critical hit ratio
        crit_ratio = self.BASE_CRIT_RATE
        
        # Some moves have increased critical hit ratio
        if hasattr(move, 'crit_ratio'):
            crit_ratio = move.crit_ratio
        
        # Critical hit stages (items, abilities, etc. would modify this)
        crit_stage = 0
        
        # Apply critical hit stage modifiers
        if crit_stage == 0:
            chance = crit_ratio
        elif crit_stage == 1:
            chance = 1/8
        elif crit_stage == 2:
            chance = 1/4
        elif crit_stage == 3:
            chance = 1/3
        else:  # crit_stage >= 4
            chance = 1/2
        
        return self.rng.random() < chance
    
    def _has_stab(self, attacker: 'MonsterInstance', move: 'Move') -> bool:
        """
        Check if move gets STAB bonus.
        
        Args:
            attacker: Attacking monster
            move: Move being used
            
        Returns:
            True if STAB applies
        """
        return move.type in attacker.species.types
    
    def _calculate_effectiveness(self, move_type: str,
                                defender: 'MonsterInstance',
                                type_chart: Dict[Tuple[str, str], float]) -> float:
        """
        Calculate type effectiveness multiplier.
        
        Args:
            move_type: Type of the move
            defender: Defending monster
            type_chart: Type effectiveness chart
            
        Returns:
            Effectiveness multiplier
        """
        effectiveness = 1.0
        
        for def_type in defender.species.types:
            multiplier = type_chart.get((move_type, def_type), 1.0)
            effectiveness *= multiplier
        
        return effectiveness
    
    def _get_effectiveness_text(self, effectiveness: float) -> str:
        """
        Get text description for effectiveness.
        
        Args:
            effectiveness: Effectiveness multiplier
            
        Returns:
            Text description
        """
        if effectiveness >= 2.0:
            return "Sehr effektiv!"
        elif effectiveness > 1.0:
            return "Effektiv!"
        elif effectiveness == 0:
            return "Hat keine Wirkung..."
        elif effectiveness < 1.0:
            return "Nicht sehr effektiv..."
        return ""


class FixedDamage:
    """Handles fixed and special damage calculations."""
    
    @staticmethod
    def calculate_fixed(amount: int) -> DamageResult:
        """
        Calculate fixed damage (always deals exact amount).
        
        Args:
            amount: Fixed damage amount
            
        Returns:
            DamageResult with fixed damage
        """
        return DamageResult(
            damage=amount,
            is_critical=False,
            effectiveness=1.0,
            type_text=""
        )
    
    @staticmethod
    def calculate_percent(target: 'MonsterInstance', percent: float) -> DamageResult:
        """
        Calculate percentage-based damage.
        
        Args:
            target: Target monster
            percent: Percentage of max HP (0.0 to 1.0)
            
        Returns:
            DamageResult with percentage damage
        """
        damage = int(target.max_hp * percent)
        damage = max(1, damage)  # Minimum 1 damage
        
        return DamageResult(
            damage=damage,
            is_critical=False,
            effectiveness=1.0,
            type_text=""
        )
    
    @staticmethod
    def calculate_recoil(damage_dealt: int, recoil_percent: float) -> int:
        """
        Calculate recoil damage.
        
        Args:
            damage_dealt: Damage dealt to opponent
            recoil_percent: Percentage of damage taken as recoil
            
        Returns:
            Recoil damage amount
        """
        recoil = int(damage_dealt * recoil_percent)
        return max(1, recoil)  # Minimum 1 recoil damage


class DamageModifiers:
    """Additional damage modifiers for special conditions."""
    
    @staticmethod
    def apply_weather(damage: int, move_type: str, weather: str) -> int:
        """
        Apply weather-based damage modifiers.
        
        Args:
            damage: Base damage
            move_type: Type of the move
            weather: Current weather condition
            
        Returns:
            Modified damage
        """
        # Simplified weather effects
        modifiers = {
            'sunny': {'feuer': 1.5, 'wasser': 0.5},
            'rain': {'wasser': 1.5, 'feuer': 0.5},
            'sandstorm': {'erde': 1.2},
            'hail': {'luft': 1.2}
        }
        
        if weather in modifiers and move_type in modifiers[weather]:
            return int(damage * modifiers[weather][move_type])
        
        return damage
    
    @staticmethod
    def apply_terrain(damage: int, move_type: str, terrain: str) -> int:
        """
        Apply terrain-based damage modifiers.
        
        Args:
            damage: Base damage
            move_type: Type of the move
            terrain: Current terrain type
            
        Returns:
            Modified damage
        """
        # Simplified terrain effects
        modifiers = {
            'grassy': {'pflanze': 1.3},
            'electric': {'energie': 1.3},
            'psychic': {'mystik': 1.3},
            'misty': {'chaos': 0.5}  # Reduces chaos-type damage
        }
        
        if terrain in modifiers and move_type in modifiers[terrain]:
            return int(damage * modifiers[terrain][move_type])
        
        return damage