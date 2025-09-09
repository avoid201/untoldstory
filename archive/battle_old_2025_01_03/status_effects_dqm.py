"""
DQM Status Effects System
Unified status condition system for Dragon Quest Monsters style gameplay
"""

from enum import Enum
from typing import Dict, List, Optional, Tuple, Any, TYPE_CHECKING
from dataclasses import dataclass
import random
import logging

if TYPE_CHECKING:
    from engine.systems.monster_instance import MonsterInstance

logger = logging.getLogger(__name__)


class StatusCondition(Enum):
    """DQM-style status conditions that can affect monsters."""
    NONE = "none"
    BURN = "burn"          # Feuer damage over time, halves ATK
    POISON = "poison"      # Seuche damage over time
    PARALYSIS = "paralysis"  # May skip turn, reduces SPD
    SLEEP = "sleep"        # Cannot act for 1-3 turns
    FREEZE = "freeze"      # Cannot act until thawed
    CONFUSION = "confusion"  # May hurt itself
    FLINCH = "flinch"      # Skip next turn only
    BADLY_POISONED = "badly_poisoned"  # Escalating poison damage
    TRAPPED = "trapped"    # Cannot switch out
    CURSE = "curse"        # Loses 1/4 max HP per turn
    TAUNT = "taunt"        # Can only use attacking moves
    TORMENT = "torment"    # Cannot use same move twice in a row
    
    @classmethod
    def from_string(cls, value: str) -> 'StatusCondition':
        """Konvertiere String zu StatusCondition mit Fallback."""
        try:
            if isinstance(value, str):
                return cls(value.lower())
            elif hasattr(value, 'value'):
                return cls(value.value.lower())
            return value
        except ValueError:
            logger.warning(f"Unbekannte StatusCondition: {value}, verwende NONE")
            return cls.NONE


@dataclass
class StatusEffect:
    """Definition of a status effect with its properties."""
    id: str
    name: str
    description: str
    color: Tuple[int, int, int] = (150, 150, 150)
    
    # Effect properties
    prevents_action: bool = False
    prevents_switching: bool = False
    damages_on_turn: bool = False
    modifies_stats: bool = False
    
    # Duration
    min_duration: int = -1  # -1 = permanent
    max_duration: int = -1
    
    # Type immunities
    immune_types: List[str] = None
    
    # Messages
    inflict_message: str = "wurde mit {name} belegt!"
    recover_message: str = "hat sich von {name} erholt!"
    blocked_message: str = "kann nicht handeln!"
    damage_message: str = "leidet unter {name}!"
    
    def __post_init__(self):
        if self.immune_types is None:
            self.immune_types = []


class DQMStatusManager:
    """Manages DQM-style status effects for a monster."""
    
    def __init__(self, monster: 'MonsterInstance'):
        """
        Initialize DQM status manager.
        
        Args:
            monster: Monster to manage status effects for
        """
        self.monster = monster
        self.primary_condition: Optional[StatusCondition] = StatusCondition.NONE
        self.primary_duration: int = 0
        self.volatile_conditions: Dict[StatusCondition, int] = {}  # condition -> duration
        self.condition_counters: Dict[str, int] = {}  # For escalating effects
        self.last_move_used: Optional[str] = None  # For torment tracking
        
        # Status effect definitions
        self.status_effects = self._initialize_status_effects()
    
    def _initialize_status_effects(self) -> Dict[StatusCondition, StatusEffect]:
        """Initialize all status effect definitions."""
        return {
            StatusCondition.BURN: StatusEffect(
                id='burn',
                name='Verbrennung',
                description='Verursacht Schaden und halbiert physischen Angriff',
                color=(200, 50, 0),
                damages_on_turn=True,
                modifies_stats=True,
                immune_types=['feuer'],
                inflict_message='wurde verbrannt!',
                recover_message='ist nicht mehr verbrannt!',
                damage_message='leidet unter der Verbrennung!'
            ),
            StatusCondition.FREEZE: StatusEffect(
                id='freeze',
                name='Einfrierung',
                description='Monster kann nicht handeln bis es auftaut',
                color=(100, 200, 255),
                prevents_action=True,
                min_duration=1,
                max_duration=5,
                immune_types=['feuer', 'luft'],
                inflict_message='wurde eingefroren!',
                recover_message='ist aufgetaut!',
                blocked_message='ist eingefroren!'
            ),
            StatusCondition.PARALYSIS: StatusEffect(
                id='paralysis',
                name='Paralyse',
                description='25% Chance nicht handeln zu können, Initiative halbiert',
                color=(200, 200, 0),
                modifies_stats=True,
                immune_types=['energie'],
                inflict_message='wurde paralysiert!',
                recover_message='ist nicht mehr paralysiert!',
                blocked_message='ist vollständig paralysiert!'
            ),
            StatusCondition.POISON: StatusEffect(
                id='poison',
                name='Vergiftung',
                description='Verursacht Schaden am Ende jeder Runde',
                color=(150, 0, 200),
                damages_on_turn=True,
                immune_types=['seuche', 'teufel'],
                inflict_message='wurde vergiftet!',
                recover_message='ist nicht mehr vergiftet!',
                damage_message='leidet unter der Vergiftung!'
            ),
            StatusCondition.BADLY_POISONED: StatusEffect(
                id='badly_poisoned',
                name='Schwere Vergiftung',
                description='Schaden erhöht sich jede Runde',
                color=(100, 0, 150),
                damages_on_turn=True,
                immune_types=['seuche', 'teufel'],
                inflict_message='wurde schwer vergiftet!',
                recover_message='ist nicht mehr vergiftet!',
                damage_message='leidet schwer unter der Vergiftung!'
            ),
            StatusCondition.SLEEP: StatusEffect(
                id='sleep',
                name='Schlaf',
                description='Monster schläft und kann nicht handeln',
                color=(100, 100, 100),
                prevents_action=True,
                min_duration=1,
                max_duration=3,
                inflict_message='ist eingeschlafen!',
                recover_message='ist aufgewacht!',
                blocked_message='schläft tief und fest!'
            ),
            StatusCondition.CONFUSION: StatusEffect(
                id='confusion',
                name='Verwirrung',
                description='33% Chance sich selbst anzugreifen',
                color=(200, 100, 200),
                min_duration=1,
                max_duration=4,
                inflict_message='wurde verwirrt!',
                recover_message='ist nicht mehr verwirrt!',
                blocked_message='ist verwirrt!'
            ),
            StatusCondition.FLINCH: StatusEffect(
                id='flinch',
                name='Zurückschrecken',
                description='Kann diese Runde nicht handeln',
                color=(150, 150, 0),
                prevents_action=True,
                min_duration=1,
                max_duration=1,
                inflict_message='ist zurückgeschreckt!',
                blocked_message='kann nicht handeln!'
            ),
            StatusCondition.TRAPPED: StatusEffect(
                id='trapped',
                name='Gefangen',
                description='Kann nicht ausgewechselt werden',
                color=(100, 50, 0),
                prevents_switching=True,
                damages_on_turn=True,
                min_duration=2,
                max_duration=5,
                inflict_message='wurde gefangen!',
                recover_message='ist frei!',
                damage_message='wird zerquetscht!'
            ),
            StatusCondition.CURSE: StatusEffect(
                id='curse',
                name='Fluch',
                description='Verliert 1/4 max KP pro Runde',
                color=(50, 0, 50),
                damages_on_turn=True,
                inflict_message='wurde verflucht!',
                recover_message='Der Fluch wurde gebrochen!',
                damage_message='leidet unter dem Fluch!'
            ),
            StatusCondition.TAUNT: StatusEffect(
                id='taunt',
                name='Verhöhnung',
                description='Kann nur Angriffsattacken einsetzen',
                color=(200, 100, 0),
                min_duration=3,
                max_duration=3,
                inflict_message='lässt sich provozieren!',
                recover_message='beruhigt sich wieder!'
            ),
            StatusCondition.TORMENT: StatusEffect(
                id='torment',
                name='Qual',
                description='Kann keine Attacke zweimal hintereinander einsetzen',
                color=(100, 0, 100),
                inflict_message='wird gequält!',
                recover_message='ist nicht mehr gequält!'
            )
        }
    
    def can_inflict_primary(self, condition: StatusCondition) -> Tuple[bool, str]:
        """
        Check if a primary condition can be inflicted.
        
        Args:
            condition: Condition to inflict
            
        Returns:
            Tuple of (can_inflict, reason_if_not)
        """
        if self.primary_condition != StatusCondition.NONE:
            return False, f"{self.monster.nickname or self.monster.species.name} hat bereits einen Status!"
        
        if condition not in self.status_effects:
            return False, "Unbekannte Statusveränderung!"
        
        effect = self.status_effects[condition]
        
        # Check type immunity
        if effect.immune_types:
            for monster_type in self.monster.species.types:
                if monster_type in effect.immune_types:
                    return False, f"{monster_type}-Typ ist immun gegen {effect.name}!"
        
        return True, ""
    
    def inflict_primary(self, condition: StatusCondition, duration: Optional[int] = None) -> Tuple[bool, str]:
        """
        Inflict a primary status condition.
        
        Args:
            condition: Condition to inflict
            duration: Override duration (None for default)
            
        Returns:
            Tuple of (success, message)
        """
        can_inflict, reason = self.can_inflict_primary(condition)
        if not can_inflict:
            return False, reason
        
        effect = self.status_effects[condition]
        
        # Set duration
        if duration is not None:
            self.primary_duration = duration
        elif effect.min_duration > 0:
            # Random duration in range
            self.primary_duration = random.randint(
                effect.min_duration,
                effect.max_duration
            )
        else:
            self.primary_duration = -1  # Permanent
        
        self.primary_condition = condition
        
        # Initialize counter for escalating conditions
        if condition == StatusCondition.BADLY_POISONED:
            self.condition_counters['poison_counter'] = 1
        
        # Update monster's status field for compatibility
        self.monster.status = condition.value
        self.monster.status_turns = self.primary_duration
        
        return True, f"{self.monster.name} {effect.inflict_message}"
    
    def inflict_volatile(self, condition: StatusCondition, duration: Optional[int] = None) -> bool:
        """
        Inflict a volatile status condition.
        
        Args:
            condition: Condition to inflict
            duration: Override duration
            
        Returns:
            True if inflicted successfully
        """
        if condition not in self.status_effects:
            return False
        
        effect = self.status_effects[condition]
        
        # Check if already has this condition
        if condition in self.volatile_conditions:
            return False
        
        # Set duration
        if duration is not None:
            self.volatile_conditions[condition] = duration
        elif effect.min_duration > 0:
            self.volatile_conditions[condition] = random.randint(
                effect.min_duration,
                effect.max_duration
            )
        else:
            self.volatile_conditions[condition] = -1
        
        return True
    
    def cure_primary(self) -> bool:
        """Cure the primary status condition."""
        if self.primary_condition == StatusCondition.NONE:
            return False
        
        self.primary_condition = StatusCondition.NONE
        self.primary_duration = 0
        self.condition_counters.clear()
        
        # Update monster's status field
        self.monster.status = None
        self.monster.status_turns = 0
        
        return True
    
    def cure_volatile(self, condition: StatusCondition) -> bool:
        """Cure a specific volatile condition."""
        if condition in self.volatile_conditions:
            del self.volatile_conditions[condition]
            return True
        return False
    
    def cure_all_volatile(self) -> None:
        """Cure all volatile conditions."""
        self.volatile_conditions.clear()
    
    def can_act(self) -> bool:
        """
        Check if monster can act this turn.
        
        Returns:
            True if monster can act, False if prevented by conditions
        """
        # Check primary condition
        if self.primary_condition != StatusCondition.NONE:
            effect = self.status_effects.get(self.primary_condition)
            if effect and effect.prevents_action:
                return False
        
        # Check volatile conditions
        for condition in self.volatile_conditions:
            effect = self.status_effects.get(condition)
            if effect and effect.prevents_action:
                return False
        
        return True
    
    def process_turn_start(self) -> List[str]:
        """
        Process conditions at turn start.
        
        Returns:
            List of messages
        """
        messages = []
        
        # Check if action is prevented
        if self.primary_condition != StatusCondition.NONE:
            effect = self.status_effects[self.primary_condition]
            
            if effect.prevents_action:
                if self.primary_condition == StatusCondition.SLEEP:
                    # Check for wake up
                    if self.primary_duration > 0:
                        self.primary_duration -= 1
                        if self.primary_duration == 0:
                            self.cure_primary()
                            messages.append(effect.recover_message)
                        else:
                            messages.append(effect.blocked_message)
                            return messages  # Can't act
                    
                elif self.primary_condition == StatusCondition.FREEZE:
                    # 20% chance to thaw
                    if random.random() < 0.2:
                        self.cure_primary()
                        messages.append(effect.recover_message)
                    else:
                        messages.append(effect.blocked_message)
                        return messages  # Can't act
                
                elif self.primary_condition == StatusCondition.PARALYSIS:
                    # 25% chance to be fully paralyzed
                    if random.random() < 0.25:
                        messages.append(effect.blocked_message)
                        return messages  # Can't act
        
        # Check volatile conditions
        if StatusCondition.FLINCH in self.volatile_conditions:
            messages.append("ist zurückgeschreckt!")
            self.cure_volatile(StatusCondition.FLINCH)  # Flinch only lasts one action
            return messages  # Can't act
        
        if StatusCondition.CONFUSION in self.volatile_conditions:
            # Confusion turn countdown
            if self.volatile_conditions[StatusCondition.CONFUSION] > 0:
                self.volatile_conditions[StatusCondition.CONFUSION] -= 1
                if self.volatile_conditions[StatusCondition.CONFUSION] == 0:
                    self.cure_volatile(StatusCondition.CONFUSION)
                    messages.append("ist nicht mehr verwirrt!")
                else:
                    # 33% chance to hurt itself
                    if random.random() < 0.33:
                        messages.append("ist verwirrt und verletzt sich selbst!")
                        # Calculate confusion damage
                        damage = self._calculate_confusion_damage()
                        self.monster.current_hp = max(0, self.monster.current_hp - damage)
                        messages.append(f"Erleidet {damage} Schaden!")
                        return messages  # Can't act normally
        
        return messages
    
    def process_turn_end(self) -> List[str]:
        """
        Process conditions at turn end.
        
        Returns:
            List of messages
        """
        messages = []
        
        # Process primary condition damage
        if self.primary_condition != StatusCondition.NONE:
            effect = self.status_effects[self.primary_condition]
            
            if effect.damages_on_turn:
                damage = 0
                
                if self.primary_condition == StatusCondition.BURN:
                    damage = max(1, self.monster.max_hp // 8)
                
                elif self.primary_condition == StatusCondition.POISON:
                    damage = max(1, self.monster.max_hp // 8)
                
                elif self.primary_condition == StatusCondition.BADLY_POISONED:
                    counter = self.condition_counters.get('poison_counter', 1)
                    damage = max(1, (self.monster.max_hp * counter) // 16)
                    self.condition_counters['poison_counter'] = min(15, counter + 1)
                
                if damage > 0:
                    self.monster.current_hp = max(0, self.monster.current_hp - damage)
                    messages.append(effect.damage_message)
                    messages.append(f"Erleidet {damage} Schaden!")
        
        # Process volatile condition damage
        if StatusCondition.TRAPPED in self.volatile_conditions:
            damage = max(1, self.monster.max_hp // 8)
            self.monster.current_hp = max(0, self.monster.current_hp - damage)
            messages.append("wird zerquetscht!")
            messages.append(f"Erleidet {damage} Schaden!")
        
        if StatusCondition.CURSE in self.volatile_conditions:
            damage = max(1, self.monster.max_hp // 4)
            self.monster.current_hp = max(0, self.monster.current_hp - damage)
            messages.append("leidet unter dem Fluch!")
            messages.append(f"Erleidet {damage} Schaden!")
        
        # Process duration countdowns
        for condition in list(self.volatile_conditions.keys()):
            if self.volatile_conditions[condition] > 0:
                self.volatile_conditions[condition] -= 1
                if self.volatile_conditions[condition] == 0:
                    self.cure_volatile(condition)
                    effect = self.status_effects[condition]
                    messages.append(effect.recover_message)
        
        return messages
    
    def _calculate_confusion_damage(self) -> int:
        """Calculate self-inflicted confusion damage."""
        try:
            # Import here to avoid circular dependency
            from engine.systems.unified_damage_calculator import unified_damage_calculator
            
            # Use unified calculator for confusion damage
            return unified_damage_calculator.calculate_confusion_damage(self.monster)
            
        except Exception as e:
            logger.error(f"Error calculating confusion damage: {e}")
            
            # Fallback to original calculation
            level = self.monster.level
            attack = self.monster.stats['atk']
            defense = self.monster.stats['def']
            damage = (((2 * level / 5 + 2) * 40 * attack / defense) / 50) + 2
            damage *= random.uniform(0.85, 1.0)
            return max(1, int(damage))
    
    def get_stat_modifiers(self) -> Dict[str, float]:
        """
        Get stat modifiers from conditions.
        
        Returns:
            Dictionary of stat -> multiplier
        """
        modifiers = {}
        
        if self.primary_condition == StatusCondition.BURN:
            modifiers['atk'] = 0.5  # Halve physical attack
        
        elif self.primary_condition == StatusCondition.PARALYSIS:
            modifiers['spd'] = 0.5  # Halve speed
        
        return modifiers
    
    def can_switch(self) -> bool:
        """Check if monster can switch out."""
        if StatusCondition.TRAPPED in self.volatile_conditions:
            return False
        
        # Check for other trapping effects
        # Check for ability/move-based trapping
        if hasattr(self, 'ability_trapping') and self.ability_trapping:
            return False
        if hasattr(self, 'move_trapping') and self.move_trapping:
            return False
        
        return True
    
    def can_use_move(self, move_category: str) -> bool:
        """
        Check if a move category can be used.
        
        Args:
            move_category: 'phys', 'mag', or 'support'
            
        Returns:
            True if move can be used
        """
        if StatusCondition.TAUNT in self.volatile_conditions:
            # Can only use damaging moves
            return move_category in ['phys', 'mag']
        
        if StatusCondition.TORMENT in self.volatile_conditions:
            # Can't use same move twice
            # This needs to be checked against last_move_used
            pass
        
        return True
    
    def reset_battle_conditions(self) -> None:
        """Reset all battle-only conditions."""
        self.volatile_conditions.clear()
        self.last_move_used = None
        
        # Keep primary conditions as they persist outside battle


# Export the main StatusCondition enum for compatibility
__all__ = ['StatusCondition', 'DQMStatusManager', 'StatusEffect']
