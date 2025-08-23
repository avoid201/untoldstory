"""
Detailed status condition system.
Handles all status effects, their mechanics, and interactions.
"""

from typing import TYPE_CHECKING, Optional, Dict, List, Tuple, Callable
from dataclasses import dataclass
from enum import Enum, auto
import random

if TYPE_CHECKING:
    from engine.systems.monster_instance import MonsterInstance
    from engine.systems.monsters import MonsterSpecies


class ConditionType(Enum):
    """Types of status conditions."""
    PRIMARY = auto()      # Main status (only one at a time)
    VOLATILE = auto()     # Battle-only status (multiple allowed)
    WEATHER = auto()      # Field weather effects
    TERRAIN = auto()      # Field terrain effects


@dataclass
class StatusCondition:
    """Definition of a status condition."""
    id: str
    name: str
    condition_type: ConditionType
    description: str
    icon: Optional[str] = None
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


class StatusConditions:
    """Registry of all status conditions."""
    
    # Primary conditions (only one at a time)
    BURN = StatusCondition(
        id='burn',
        name='Verbrennung',
        condition_type=ConditionType.PRIMARY,
        description='Verursacht Schaden und halbiert physischen Angriff',
        color=(200, 50, 0),
        damages_on_turn=True,
        modifies_stats=True,
        immune_types=['feuer'],
        inflict_message='wurde verbrannt!',
        recover_message='ist nicht mehr verbrannt!',
        damage_message='leidet unter der Verbrennung!'
    )
    
    FREEZE = StatusCondition(
        id='freeze',
        name='Einfrierung',
        condition_type=ConditionType.PRIMARY,
        description='Monster kann nicht handeln bis es auftaut',
        color=(100, 200, 255),
        prevents_action=True,
        min_duration=1,
        max_duration=5,
        immune_types=['feuer', 'luft'],
        inflict_message='wurde eingefroren!',
        recover_message='ist aufgetaut!',
        blocked_message='ist eingefroren!'
    )
    
    PARALYSIS = StatusCondition(
        id='paralysis',
        name='Paralyse',
        condition_type=ConditionType.PRIMARY,
        description='25% Chance nicht handeln zu können, Initiative halbiert',
        color=(200, 200, 0),
        modifies_stats=True,
        immune_types=['energie'],
        inflict_message='wurde paralysiert!',
        recover_message='ist nicht mehr paralysiert!',
        blocked_message='ist vollständig paralysiert!'
    )
    
    POISON = StatusCondition(
        id='poison',
        name='Vergiftung',
        condition_type=ConditionType.PRIMARY,
        description='Verursacht Schaden am Ende jeder Runde',
        color=(150, 0, 200),
        damages_on_turn=True,
        immune_types=['seuche', 'teufel'],
        inflict_message='wurde vergiftet!',
        recover_message='ist nicht mehr vergiftet!',
        damage_message='leidet unter der Vergiftung!'
    )
    
    BADLY_POISONED = StatusCondition(
        id='badly_poisoned',
        name='Schwere Vergiftung',
        condition_type=ConditionType.PRIMARY,
        description='Schaden erhöht sich jede Runde',
        color=(100, 0, 150),
        damages_on_turn=True,
        immune_types=['seuche', 'teufel'],
        inflict_message='wurde schwer vergiftet!',
        recover_message='ist nicht mehr vergiftet!',
        damage_message='leidet schwer unter der Vergiftung!'
    )
    
    SLEEP = StatusCondition(
        id='sleep',
        name='Schlaf',
        condition_type=ConditionType.PRIMARY,
        description='Monster schläft und kann nicht handeln',
        color=(100, 100, 100),
        prevents_action=True,
        min_duration=1,
        max_duration=3,
        inflict_message='ist eingeschlafen!',
        recover_message='ist aufgewacht!',
        blocked_message='schläft tief und fest!'
    )
    
    # Volatile conditions (battle-only, multiple allowed)
    CONFUSION = StatusCondition(
        id='confusion',
        name='Verwirrung',
        condition_type=ConditionType.VOLATILE,
        description='33% Chance sich selbst anzugreifen',
        color=(200, 100, 200),
        min_duration=1,
        max_duration=4,
        inflict_message='wurde verwirrt!',
        recover_message='ist nicht mehr verwirrt!',
        blocked_message='ist verwirrt!'
    )
    
    FLINCH = StatusCondition(
        id='flinch',
        name='Zurückschrecken',
        condition_type=ConditionType.VOLATILE,
        description='Kann diese Runde nicht handeln',
        color=(150, 150, 0),
        prevents_action=True,
        min_duration=1,
        max_duration=1,
        inflict_message='ist zurückgeschreckt!',
        blocked_message='kann nicht handeln!'
    )
    
    TRAPPED = StatusCondition(
        id='trapped',
        name='Gefangen',
        condition_type=ConditionType.VOLATILE,
        description='Kann nicht ausgewechselt werden',
        color=(100, 50, 0),
        prevents_switching=True,
        damages_on_turn=True,
        min_duration=2,
        max_duration=5,
        inflict_message='wurde gefangen!',
        recover_message='ist frei!',
        damage_message='wird zerquetscht!'
    )
    
    CURSE = StatusCondition(
        id='curse',
        name='Fluch',
        condition_type=ConditionType.VOLATILE,
        description='Verliert 1/4 max KP pro Runde',
        color=(50, 0, 50),
        damages_on_turn=True,
        inflict_message='wurde verflucht!',
        recover_message='Der Fluch wurde gebrochen!',
        damage_message='leidet unter dem Fluch!'
    )
    
    TAUNT = StatusCondition(
        id='taunt',
        name='Verhöhnung',
        condition_type=ConditionType.VOLATILE,
        description='Kann nur Angriffsattacken einsetzen',
        color=(200, 100, 0),
        min_duration=3,
        max_duration=3,
        inflict_message='lässt sich provozieren!',
        recover_message='beruhigt sich wieder!'
    )
    
    TORMENT = StatusCondition(
        id='torment',
        name='Qual',
        condition_type=ConditionType.VOLATILE,
        description='Kann keine Attacke zweimal hintereinander einsetzen',
        color=(100, 0, 100),
        inflict_message='wird gequält!',
        recover_message='ist nicht mehr gequält!'
    )
    
    # Registry
    ALL_CONDITIONS = {
        'burn': BURN,
        'freeze': FREEZE,
        'paralysis': PARALYSIS,
        'poison': POISON,
        'badly_poisoned': BADLY_POISONED,
        'sleep': SLEEP,
        'confusion': CONFUSION,
        'flinch': FLINCH,
        'trapped': TRAPPED,
        'curse': CURSE,
        'taunt': TAUNT,
        'torment': TORMENT
    }


class ConditionManager:
    """Manages status conditions for a monster."""
    
    def __init__(self, monster: 'MonsterInstance'):
        """
        Initialize condition manager.
        
        Args:
            monster: Monster to manage conditions for
        """
        self.monster = monster
        self.primary_condition: Optional[str] = None
        self.primary_duration: int = 0
        self.volatile_conditions: Dict[str, int] = {}  # condition_id -> duration
        self.condition_counters: Dict[str, int] = {}  # For escalating effects
        self.last_move_used: Optional[str] = None  # For torment tracking
    
    def can_inflict_primary(self, condition_id: str) -> Tuple[bool, str]:
        """
        Check if a primary condition can be inflicted.
        
        Args:
            condition_id: Condition to inflict
            
        Returns:
            Tuple of (can_inflict, reason_if_not)
        """
        if self.primary_condition:
            return False, f"{self.monster.nickname or self.monster.species.name} hat bereits einen Status!"
        
        condition = StatusConditions.ALL_CONDITIONS.get(condition_id)
        if not condition:
            return False, "Unbekannte Statusveränderung!"
        
        # Check type immunity
        if condition.immune_types:
            for monster_type in self.monster.species.types:
                if monster_type in condition.immune_types:
                    return False, f"{monster_type}-Typ ist immun gegen {condition.name}!"
        
        return True, ""
    
    def inflict_primary(self, condition_id: str, duration: Optional[int] = None) -> bool:
        """
        Inflict a primary status condition.
        
        Args:
            condition_id: Condition to inflict
            duration: Override duration (None for default)
            
        Returns:
            True if inflicted successfully
        """
        can_inflict, _ = self.can_inflict_primary(condition_id)
        if not can_inflict:
            return False
        
        condition = StatusConditions.ALL_CONDITIONS[condition_id]
        
        # Set duration
        if duration is not None:
            self.primary_duration = duration
        elif condition.min_duration > 0:
            # Random duration in range
            self.primary_duration = random.randint(
                condition.min_duration,
                condition.max_duration
            )
        else:
            self.primary_duration = -1  # Permanent
        
        self.primary_condition = condition_id
        
        # Initialize counter for escalating conditions
        if condition_id == 'badly_poisoned':
            self.condition_counters['poison_counter'] = 1
        
        # Update monster's status field for compatibility
        self.monster.status = condition_id
        self.monster.status_turns = self.primary_duration
        
        return True
    
    def inflict_volatile(self, condition_id: str, duration: Optional[int] = None) -> bool:
        """
        Inflict a volatile status condition.
        
        Args:
            condition_id: Condition to inflict
            duration: Override duration
            
        Returns:
            True if inflicted successfully
        """
        condition = StatusConditions.ALL_CONDITIONS.get(condition_id)
        if not condition or condition.condition_type != ConditionType.VOLATILE:
            return False
        
        # Check if already has this condition
        if condition_id in self.volatile_conditions:
            return False
        
        # Set duration
        if duration is not None:
            self.volatile_conditions[condition_id] = duration
        elif condition.min_duration > 0:
            self.volatile_conditions[condition_id] = random.randint(
                condition.min_duration,
                condition.max_duration
            )
        else:
            self.volatile_conditions[condition_id] = -1
        
        return True
    
    def cure_primary(self) -> bool:
        """Cure the primary status condition."""
        if not self.primary_condition:
            return False
        
        self.primary_condition = None
        self.primary_duration = 0
        self.condition_counters.clear()
        
        # Update monster's status field
        self.monster.status = None
        self.monster.status_turns = 0
        
        return True
    
    def cure_volatile(self, condition_id: str) -> bool:
        """Cure a specific volatile condition."""
        if condition_id in self.volatile_conditions:
            del self.volatile_conditions[condition_id]
            return True
        return False
    
    def cure_all_volatile(self) -> None:
        """Cure all volatile conditions."""
        self.volatile_conditions.clear()
    
    def process_turn_start(self) -> List[str]:
        """
        Process conditions at turn start.
        
        Returns:
            List of messages
        """
        messages = []
        
        # Check if action is prevented
        if self.primary_condition:
            condition = StatusConditions.ALL_CONDITIONS[self.primary_condition]
            
            if condition.prevents_action:
                if self.primary_condition == 'sleep':
                    # Check for wake up
                    if self.primary_duration > 0:
                        self.primary_duration -= 1
                        if self.primary_duration == 0:
                            self.cure_primary()
                            messages.append(condition.recover_message.format(
                                name=condition.name
                            ))
                        else:
                            messages.append(condition.blocked_message)
                            return messages  # Can't act
                    
                elif self.primary_condition == 'freeze':
                    # 20% chance to thaw
                    if random.random() < 0.2:
                        self.cure_primary()
                        messages.append(condition.recover_message.format(
                            name=condition.name
                        ))
                    else:
                        messages.append(condition.blocked_message)
                        return messages  # Can't act
                
                elif self.primary_condition == 'paralysis':
                    # 25% chance to be fully paralyzed
                    if random.random() < 0.25:
                        messages.append(condition.blocked_message)
                        return messages  # Can't act
        
        # Check volatile conditions
        if 'flinch' in self.volatile_conditions:
            messages.append("ist zurückgeschreckt!")
            self.cure_volatile('flinch')  # Flinch only lasts one action
            return messages  # Can't act
        
        if 'confusion' in self.volatile_conditions:
            # Confusion turn countdown
            if self.volatile_conditions['confusion'] > 0:
                self.volatile_conditions['confusion'] -= 1
                if self.volatile_conditions['confusion'] == 0:
                    self.cure_volatile('confusion')
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
        if self.primary_condition:
            condition = StatusConditions.ALL_CONDITIONS[self.primary_condition]
            
            if condition.damages_on_turn:
                damage = 0
                
                if self.primary_condition == 'burn':
                    damage = max(1, self.monster.max_hp // 8)
                
                elif self.primary_condition == 'poison':
                    damage = max(1, self.monster.max_hp // 8)
                
                elif self.primary_condition == 'badly_poisoned':
                    counter = self.condition_counters.get('poison_counter', 1)
                    damage = max(1, (self.monster.max_hp * counter) // 16)
                    self.condition_counters['poison_counter'] = min(15, counter + 1)
                
                if damage > 0:
                    self.monster.current_hp = max(0, self.monster.current_hp - damage)
                    messages.append(condition.damage_message.format(
                        name=condition.name
                    ))
                    messages.append(f"Erleidet {damage} Schaden!")
        
        # Process volatile condition damage
        if 'trapped' in self.volatile_conditions:
            damage = max(1, self.monster.max_hp // 8)
            self.monster.current_hp = max(0, self.monster.current_hp - damage)
            messages.append("wird zerquetscht!")
            messages.append(f"Erleidet {damage} Schaden!")
        
        if 'curse' in self.volatile_conditions:
            damage = max(1, self.monster.max_hp // 4)
            self.monster.current_hp = max(0, self.monster.current_hp - damage)
            messages.append("leidet unter dem Fluch!")
            messages.append(f"Erleidet {damage} Schaden!")
        
        # Process duration countdowns
        for condition_id in list(self.volatile_conditions.keys()):
            if self.volatile_conditions[condition_id] > 0:
                self.volatile_conditions[condition_id] -= 1
                if self.volatile_conditions[condition_id] == 0:
                    self.cure_volatile(condition_id)
                    condition = StatusConditions.ALL_CONDITIONS[condition_id]
                    messages.append(condition.recover_message.format(
                        name=condition.name
                    ))
        
        return messages
    
    def _calculate_confusion_damage(self) -> int:
        """Calculate self-inflicted confusion damage."""
        # Use a physical attack against own defense
        level = self.monster.level
        attack = self.monster.stats['atk']
        defense = self.monster.stats['def']
        
        # Simplified damage formula
        damage = (((2 * level / 5 + 2) * 40 * attack / defense) / 50) + 2
        
        # Random factor
        damage *= random.uniform(0.85, 1.0)
        
        return max(1, int(damage))
    
    def get_stat_modifiers(self) -> Dict[str, float]:
        """
        Get stat modifiers from conditions.
        
        Returns:
            Dictionary of stat -> multiplier
        """
        modifiers = {}
        
        if self.primary_condition == 'burn':
            modifiers['atk'] = 0.5  # Halve physical attack
        
        elif self.primary_condition == 'paralysis':
            modifiers['spd'] = 0.5  # Halve speed
        
        return modifiers
    
    def can_switch(self) -> bool:
        """Check if monster can switch out."""
        if 'trapped' in self.volatile_conditions:
            return False
        
        # Check for other trapping effects
        # TODO: Add ability/move-based trapping
        
        return True
    
    def can_use_move(self, move_category: str) -> bool:
        """
        Check if a move category can be used.
        
        Args:
            move_category: 'phys', 'mag', or 'support'
            
        Returns:
            True if move can be used
        """
        if 'taunt' in self.volatile_conditions:
            # Can only use damaging moves
            return move_category in ['phys', 'mag']
        
        if 'torment' in self.volatile_conditions:
            # Can't use same move twice
            # This needs to be checked against last_move_used
            pass
        
        return True
    
    def reset_battle_conditions(self) -> None:
        """Reset all battle-only conditions."""
        self.volatile_conditions.clear()
        self.last_move_used = None
        
        # Keep primary conditions as they persist outside battle