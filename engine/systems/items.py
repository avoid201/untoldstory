"""
Comprehensive item system for Untold Story.
Handles healing, status curing, taming, stat boosts, and special effects.
"""

from typing import TYPE_CHECKING, Optional, Dict, List, Any, Callable, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum, auto
import json
import random

if TYPE_CHECKING:
    from engine.systems.monster_instance import MonsterInstance
    from engine.systems.party import Party
    from engine.systems.monsters import MonsterSpecies
    from engine.systems.battle.battle_system import BattleState as Battle


class ItemCategory(Enum):
    """Item categories for organization."""
    HEALING = auto()      # HP restoration and revival
    STATUS = auto()        # Status condition cures
    TAMING = auto()        # Monster taming assistance
    BATTLE = auto()        # Battle-only stat boosts
    SPECIAL = auto()       # Unique effects and key items
    EQUIPMENT = auto()     # Held items for monsters
    MISC = auto()          # Other utility items


class ItemRarity(Enum):
    """Item rarity levels."""
    COMMON = auto()        # Basic items, easy to find
    UNCOMMON = auto()      # Better items, moderate rarity
    RARE = auto()          # Powerful items, hard to find
    EPIC = auto()          # Very powerful, very rare
    LEGENDARY = auto()     # Ultimate items, extremely rare


class ItemTarget(Enum):
    """Valid targets for item use."""
    SELF = auto()          # User only
    SINGLE_ALLY = auto()   # One ally monster
    ALL_ALLIES = auto()    # All ally monsters
    SINGLE_ENEMY = auto()  # One enemy (battle only)
    ALL_ENEMIES = auto()   # All enemies (battle only)
    FIELD = auto()          # Field effect
    NONE = auto()          # No target needed


class EffectType(Enum):
    """Types of effects items can have."""
    HEAL_HP = auto()           # Restore HP
    HEAL_STATUS = auto()        # Cure status condition
    HEAL_ALL_STATUS = auto()    # Cure all status conditions
    REVIVE = auto()             # Revive fainted monster
    BUFF_STAT = auto()          # Increase stat stages
    DEBUFF_STAT = auto()        # Decrease stat stages
    RESTORE_PP = auto()         # Restore move PP
    GAIN_EXP = auto()           # Gain experience
    LEVEL_UP = auto()           # Level up monster
    TAMING_BONUS = auto()       # Increase taming chance
    ESCAPE = auto()             # Escape from battle
    REPEL = auto()              # Repel wild monsters
    TELEPORT = auto()           # Teleport to safe location
    SYNTHESIS = auto()          # Monster fusion bonus
    HAPPINESS = auto()          # Increase happiness


@dataclass
class ItemEffect:
    """Effect of using an item."""
    effect_type: EffectType
    value: Any
    chance: float = 1.0
    message: str = ""
    target_type: ItemTarget = ItemTarget.SELF
    duration: Optional[int] = None  # For temporary effects
    conditions: Dict[str, Any] = field(default_factory=dict)  # Special conditions


@dataclass
class Item:
    """Complete item class with all properties."""
    id: str
    name: str
    description: str
    category: ItemCategory
    rarity: ItemRarity
    target: ItemTarget
    price: int
    sell_price: int
    use_in_battle: bool
    use_in_field: bool
    consumable: bool
    stack_size: int = 99
    effects: List[ItemEffect] = field(default_factory=list)
    sprite_index: int = 0
    flavor_text: str = ""
    unlock_level: int = 1  # Required player level to use
    
    def can_use(self, in_battle: bool = False, player_level: int = 1) -> bool:
        """Check if item can be used in current context."""
        if player_level < self.unlock_level:
            return False
        
        if in_battle:
            return self.use_in_battle
        return self.use_in_field
    
    def get_effectiveness_message(self, target: Optional['MonsterInstance'] = None) -> str:
        """Get message about item effectiveness."""
        if not target:
            return ""
        
        # Check type immunities for status items
        for effect in self.effects:
            if effect.effect_type == EffectType.HEAL_STATUS:
                if self._is_immune_to_status(target, effect.value):
                    return f"{target.nickname or target.species.name} ist immun gegen diesen Status!"
        
        return ""
    
    def _is_immune_to_status(self, monster: 'MonsterInstance', status: str) -> bool:
        """Check if monster is immune to a status."""
        # Type-based immunities
        status_immunities = {
            'burn': ['feuer'],
            'freeze': ['feuer', 'luft'],
            'poison': ['seuche', 'teufel'],
            'paralysis': ['energie']
        }
        
        if status in status_immunities:
            immune_types = status_immunities[status]
            for monster_type in monster.species.types:
                if monster_type in immune_types:
                    return True
        
        return False


class ItemEffectExecutor:
    """Executes item effects with proper validation and messaging."""
    
    def __init__(self):
        """Initialize effect executor."""
        self.rng = random.Random()
    
    def execute_item_effects(self, item: Item, 
                           user: Optional['MonsterInstance'] = None,
                           target: Optional['MonsterInstance'] = None,
                           party: Optional['Party'] = None,
                           battle: Optional['Battle'] = None) -> List[str]:
        """
        Execute all effects of an item.
        
        Args:
            item: Item being used
            user: Monster using the item
            target: Target monster
            party: Player's party
            battle: Current battle state
            
        Returns:
            List of result messages
        """
        messages = []
        
        # Check effectiveness
        effectiveness_msg = item.get_effectiveness_message(target)
        if effectiveness_msg:
            messages.append(effectiveness_msg)
            return messages
        
        # Execute each effect
        for effect in item.effects:
            if self.rng.random() > effect.chance:
                continue
            
            result = self._apply_effect(effect, item, user, target, party, battle)
            if result:
                messages.append(result)
        
        return messages
    
    def _apply_effect(self, effect: ItemEffect, item: Item,
                     user: Optional['MonsterInstance'],
                     target: Optional['MonsterInstance'],
                     party: Optional['Party'],
                     battle: Optional['Battle']) -> Optional[str]:
        """Apply a single item effect."""
        
        if effect.effect_type == EffectType.HEAL_HP:
            return self._heal_hp(effect, target)
        
        elif effect.effect_type == EffectType.HEAL_STATUS:
            return self._heal_status(effect, target)
        
        elif effect.effect_type == EffectType.HEAL_ALL_STATUS:
            return self._heal_all_status(target)
        
        elif effect.effect_type == EffectType.REVIVE:
            return self._revive_monster(effect, target)
        
        elif effect.effect_type == EffectType.BUFF_STAT:
            return self._buff_stat(effect, target)
        
        elif effect.effect_type == EffectType.DEBUFF_STAT:
            return self._debuff_stat(effect, target)
        
        elif effect.effect_type == EffectType.RESTORE_PP:
            return self._restore_pp(effect, target)
        
        elif effect.effect_type == EffectType.GAIN_EXP:
            return self._gain_exp(effect, target)
        
        elif effect.effect_type == EffectType.LEVEL_UP:
            return self._level_up(effect, target)
        
        elif effect.effect_type == EffectType.TAMING_BONUS:
            return self._apply_taming_bonus(effect, target, battle)
        
        elif effect.effect_type == EffectType.ESCAPE:
            return self._escape_battle(battle)
        
        elif effect.effect_type == EffectType.REPEL:
            return self._apply_repel(effect, user)
        
        elif effect.effect_type == EffectType.TELEPORT:
            return self._teleport(effect, user)
        
        elif effect.effect_type == EffectType.SYNTHESIS:
            return self._apply_synthesis_bonus(effect, user)
        
        elif effect.effect_type == EffectType.HAPPINESS:
            return self._increase_happiness(effect, target)
        
        return effect.message if effect.message else None
    
    def _heal_hp(self, effect: ItemEffect, target: 'MonsterInstance') -> str:
        """Heal HP effect."""
        if not target:
            return "Kein Ziel ausgewählt!"
        
        if isinstance(effect.value, float):
            # Percentage heal
            amount = int(target.max_hp * effect.value)
        else:
            # Fixed heal
            amount = effect.value
        
        actual = min(amount, target.max_hp - target.current_hp)
        target.current_hp += actual
        
        if actual > 0:
            return f"{target.nickname or target.species.name} heilt {actual} KP!"
        else:
            return f"{target.nickname or target.species.name} hat bereits volle KP!"
    
    def _heal_status(self, effect: ItemEffect, target: 'MonsterInstance') -> str:
        """Heal status condition effect."""
        if not target or not target.status:
            return "Kein Statusproblem vorhanden!"
        
        if target.status == effect.value:
            old_status = target.status
            target.status = None
            target.status_turns = 0
            return f"{target.nickname or target.species.name} wurde von {old_status} geheilt!"
        
        return f"Dieses Item heilt nicht {target.status}!"
    
    def _heal_all_status(self, target: 'MonsterInstance') -> str:
        """Heal all status conditions effect."""
        if not target or not target.status:
            return "Kein Statusproblem vorhanden!"
        
        old_status = target.status
        target.status = None
        target.status_turns = 0
        return f"{target.nickname or target.species.name} wurde von {old_status} geheilt!"
    
    def _revive_monster(self, effect: ItemEffect, target: 'MonsterInstance') -> str:
        """Revive fainted monster effect."""
        if not target or target.current_hp > 0:
            return "Das Monster lebt noch!"
        
        if isinstance(effect.value, float):
            # Percentage revive
            target.current_hp = int(target.max_hp * effect.value)
        else:
            # Fixed HP revive
            target.current_hp = min(effect.value, target.max_hp)
        
        return f"{target.nickname or target.species.name} wurde wiederbelebt!"
    
    def _buff_stat(self, effect: ItemEffect, target: 'MonsterInstance') -> str:
        """Buff stat effect."""
        if not target:
            return "Kein Ziel ausgewählt!"
        
        stat, stages = effect.value
        current = target.stat_stages.get(stat, 0)
        new_stage = max(-6, min(6, current + stages))
        
        if new_stage == current:
            return f"{target.nickname or target.species.name}'s {stat} kann nicht weiter erhöht werden!"
        
        target.stat_stages[stat] = new_stage
        
        stat_names = {
            'atk': 'Angriff', 'def': 'Verteidigung',
            'mag': 'Magie', 'res': 'Resistenz',
            'spd': 'Initiative', 'acc': 'Genauigkeit', 'eva': 'Fluchtwert'
        }
        
        return f"{target.nickname or target.species.name}'s {stat_names.get(stat, stat)} steigt!"
    
    def _debuff_stat(self, effect: ItemEffect, target: 'MonsterInstance') -> str:
        """Debuff stat effect."""
        if not target:
            return "Kein Ziel ausgewählt!"
        
        stat, stages = effect.value
        current = target.stat_stages.get(stat, 0)
        new_stage = max(-6, min(6, current - stages))
        
        if new_stage == current:
            return f"{target.nickname or target.species.name}'s {stat} kann nicht weiter gesenkt werden!"
        
        target.stat_stages[stat] = new_stage
        
        stat_names = {
            'atk': 'Angriff', 'def': 'Verteidigung',
            'mag': 'Magie', 'res': 'Resistenz',
            'spd': 'Initiative', 'acc': 'Genauigkeit', 'eva': 'Fluchtwert'
        }
        
        return f"{target.nickname or target.species.name}'s {stat_names.get(stat, stat)} sinkt!"
    
    def _restore_pp(self, effect: ItemEffect, target: 'MonsterInstance') -> str:
        """Restore PP effect."""
        if not target:
            return "Kein Ziel ausgewählt!"
        
        move_index = effect.value.get('move', 0)
        amount = effect.value.get('amount', 10)
        
        if 0 <= move_index < len(target.moves) and target.moves[move_index]:
            move = target.moves[move_index]
            restored = min(amount, move.max_pp - move.current_pp)
            move.current_pp += restored
            return f"{move.name} erhält {restored} AP!"
        
        return "Keine gültige Attacke gefunden!"
    
    def _gain_exp(self, effect: ItemEffect, target: 'MonsterInstance') -> str:
        """Gain experience effect."""
        if not target:
            return "Kein Ziel ausgewählt!"
        
        target.gain_exp(effect.value)
        return f"{target.nickname or target.species.name} erhält {effect.value} EP!"
    
    def _level_up(self, effect: ItemEffect, target: 'MonsterInstance') -> str:
        """Level up effect."""
        if not target:
            return "Kein Ziel ausgewählt!"
        
        levels_gained = 0
        for _ in range(effect.value):
            if target.level < 100:
                target.level_up()
                levels_gained += 1
        
        if levels_gained > 0:
            return f"{target.nickname or target.species.name} erreicht Level {target.level}!"
        else:
            return f"{target.nickname or target.species.name} kann nicht weiter aufleveln!"
    
    def _apply_taming_bonus(self, effect: ItemEffect, target: 'MonsterInstance', battle: Optional['Battle']) -> str:
        """Apply taming bonus effect."""
        if not battle or not battle.is_wild:
            return "Taming-Bonus funktioniert nur bei wilden Monstern!"
        
        # This would integrate with the taming system
        return f"Taming-Bonus von {effect.value}x angewendet!"
    
    def _escape_battle(self, battle: Optional['Battle']) -> str:
        """Escape from battle effect."""
        if not battle:
            return "Nicht im Kampf!"
        
        # This would trigger battle escape
        return "Fluchtversuch gestartet!"
    
    def _apply_repel(self, effect: ItemEffect, user: 'MonsterInstance') -> str:
        """Apply repel effect."""
        if not user:
            return "Kein Benutzer gefunden!"
        
        # This would apply repel effect
        return f"Repel-Effekt für {effect.value} Schritte aktiviert!"
    
    def _teleport(self, effect: ItemEffect, user: 'MonsterInstance') -> str:
        """Teleport effect."""
        if not user:
            return "Kein Benutzer gefunden!"
        
        # This would trigger teleport
        return "Teleportation gestartet!"
    
    def _apply_synthesis_bonus(self, effect: ItemEffect, user: 'MonsterInstance') -> str:
        """Apply synthesis bonus effect."""
        if not user:
            return "Kein Benutzer gefunden!"
        
        # This would apply synthesis bonus
        return f"Synthese-Bonus von {effect.value}x angewendet!"
    
    def _increase_happiness(self, effect: ItemEffect, target: 'MonsterInstance') -> str:
        """Increase happiness effect."""
        if not target:
            return "Kein Ziel ausgewählt!"
        
        if hasattr(target, 'happiness'):
            old_happiness = target.happiness
            target.happiness = min(255, target.happiness + effect.value)
            increase = target.happiness - old_happiness
            return f"{target.nickname or target.species.name} wird glücklicher! (+{increase})"
        
        return "Dieses Monster hat kein Glücks-System!"


class ItemRegistry:
    """Singleton registry for all items in the game."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize item registry."""
        if hasattr(self, 'initialized'):
            return
        
        self.items: Dict[str, Item] = {}
        self.effect_executor = ItemEffectExecutor()
        self._load_default_items()
        self.initialized = True
    
    def _load_default_items(self):
        """Load default items into registry."""
        # Healing Items
        self._register_healing_items()
        # Status Items
        self._register_status_items()
        # Taming Items
        self._register_taming_items()
        # Battle Items
        self._register_battle_items()
        # Special Items
        self._register_special_items()
    
    def _register_healing_items(self):
        """Register all healing items."""
        healing_items = [
            {
                'id': 'trank',
                'name': 'Trank',
                'description': 'Heilt 20 KP eines Monsters',
                'category': ItemCategory.HEALING,
                'rarity': ItemRarity.COMMON,
                'target': ItemTarget.SINGLE_ALLY,
                'price': 100,
                'sell_price': 50,
                'use_in_battle': True,
                'use_in_field': True,
                'consumable': True,
                'effects': [ItemEffect(EffectType.HEAL_HP, 20)]
            },
            {
                'id': 'supertrank',
                'name': 'Supertrank',
                'description': 'Heilt 50 KP eines Monsters',
                'category': ItemCategory.HEALING,
                'rarity': ItemRarity.COMMON,
                'target': ItemTarget.SINGLE_ALLY,
                'price': 300,
                'sell_price': 150,
                'use_in_battle': True,
                'use_in_field': True,
                'consumable': True,
                'effects': [ItemEffect(EffectType.HEAL_HP, 50)]
            },
            {
                'id': 'hypertrank',
                'name': 'Hypertrank',
                'description': 'Heilt 100 KP eines Monsters',
                'category': ItemCategory.HEALING,
                'rarity': ItemRarity.UNCOMMON,
                'target': ItemTarget.SINGLE_ALLY,
                'price': 800,
                'sell_price': 400,
                'use_in_battle': True,
                'use_in_field': True,
                'consumable': True,
                'effects': [ItemEffect(EffectType.HEAL_HP, 100)]
            },
            {
                'id': 'top_trank',
                'name': 'Top-Trank',
                'description': 'Heilt alle KP eines Monsters vollständig',
                'category': ItemCategory.HEALING,
                'rarity': ItemRarity.RARE,
                'target': ItemTarget.SINGLE_ALLY,
                'price': 2000,
                'sell_price': 1000,
                'use_in_battle': True,
                'use_in_field': True,
                'consumable': True,
                'effects': [ItemEffect(EffectType.HEAL_HP, 1.0)]
            },
            {
                'id': 'wiederbelebung',
                'name': 'Wiederbelebung',
                'description': 'Belebt ein besiegtes Monster mit halben KP wieder',
                'category': ItemCategory.HEALING,
                'rarity': ItemRarity.RARE,
                'target': ItemTarget.SINGLE_ALLY,
                'price': 1000,
                'sell_price': 500,
                'use_in_battle': False,
                'use_in_field': True,
                'consumable': True,
                'effects': [ItemEffect(EffectType.REVIVE, 0.5)]
            },
            {
                'id': 'top_wiederbelebung',
                'name': 'Top-Wiederbelebung',
                'description': 'Belebt ein besiegtes Monster mit vollen KP wieder',
                'category': ItemCategory.HEALING,
                'rarity': ItemRarity.EPIC,
                'target': ItemTarget.SINGLE_ALLY,
                'price': 2500,
                'sell_price': 1250,
                'use_in_battle': False,
                'use_in_field': True,
                'consumable': True,
                'effects': [ItemEffect(EffectType.REVIVE, 1.0)]
            }
        ]
        
        for item_data in healing_items:
            self._create_and_register_item(item_data)
    
    def _register_status_items(self):
        """Register all status healing items."""
        status_items = [
            {
                'id': 'gegengift',
                'name': 'Gegengift',
                'description': 'Heilt Vergiftung bei einem Monster',
                'category': ItemCategory.STATUS,
                'rarity': ItemRarity.COMMON,
                'target': ItemTarget.SINGLE_ALLY,
                'price': 100,
                'sell_price': 50,
                'use_in_battle': True,
                'use_in_field': True,
                'consumable': True,
                'effects': [ItemEffect(EffectType.HEAL_STATUS, 'poison')]
            },
            {
                'id': 'brandsalbe',
                'name': 'Brandsalbe',
                'description': 'Heilt Verbrennung bei einem Monster',
                'category': ItemCategory.STATUS,
                'rarity': ItemRarity.COMMON,
                'target': ItemTarget.SINGLE_ALLY,
                'price': 100,
                'sell_price': 50,
                'use_in_battle': True,
                'use_in_field': True,
                'consumable': True,
                'effects': [ItemEffect(EffectType.HEAL_STATUS, 'burn')]
            },
            {
                'id': 'auftaumittel',
                'name': 'Auftaumittel',
                'description': 'Weckt ein eingefrorenes Monster auf',
                'category': ItemCategory.STATUS,
                'rarity': ItemRarity.COMMON,
                'target': ItemTarget.SINGLE_ALLY,
                'price': 100,
                'sell_price': 50,
                'use_in_battle': True,
                'use_in_field': True,
                'consumable': True,
                'effects': [ItemEffect(EffectType.HEAL_STATUS, 'freeze')]
            },
            {
                'id': 'aufwecker',
                'name': 'Aufwecker',
                'description': 'Weckt ein schlafendes Monster auf',
                'category': ItemCategory.STATUS,
                'rarity': ItemRarity.COMMON,
                'target': ItemTarget.SINGLE_ALLY,
                'price': 100,
                'sell_price': 50,
                'use_in_battle': True,
                'use_in_field': True,
                'consumable': True,
                'effects': [ItemEffect(EffectType.HEAL_STATUS, 'sleep')]
            },
            {
                'id': 'anti_paralyse',
                'name': 'Anti-Paralyse',
                'description': 'Heilt Paralyse bei einem Monster',
                'category': ItemCategory.STATUS,
                'rarity': ItemRarity.COMMON,
                'target': ItemTarget.SINGLE_ALLY,
                'price': 100,
                'sell_price': 50,
                'use_in_battle': True,
                'use_in_field': True,
                'consumable': True,
                'effects': [ItemEffect(EffectType.HEAL_STATUS, 'paralysis')]
            },
            {
                'id': 'totalheilung',
                'name': 'Totalheilung',
                'description': 'Heilt alle Statusprobleme bei einem Monster',
                'category': ItemCategory.STATUS,
                'rarity': ItemRarity.UNCOMMON,
                'target': ItemTarget.SINGLE_ALLY,
                'price': 400,
                'sell_price': 200,
                'use_in_battle': True,
                'use_in_field': True,
                'consumable': True,
                'effects': [ItemEffect(EffectType.HEAL_ALL_STATUS, None)]
            }
        ]
        
        for item_data in status_items:
            self._create_and_register_item(item_data)
    
    def _register_taming_items(self):
        """Register all taming items."""
        taming_items = [
            {
                'id': 'fleisch',
                'name': 'Fleisch',
                'description': 'Normales Fleisch zum Zähmen wilder Monster',
                'category': ItemCategory.TAMING,
                'rarity': ItemRarity.COMMON,
                'target': ItemTarget.SINGLE_ENEMY,
                'price': 100,
                'sell_price': 50,
                'use_in_battle': True,
                'use_in_field': False,
                'consumable': True,
                'effects': [ItemEffect(EffectType.TAMING_BONUS, 1.5)]
            },
            {
                'id': 'lecker_fleisch',
                'name': 'Lecker Fleisch',
                'description': 'Schmackhaftes Fleisch, beliebt bei den meisten Monstern',
                'category': ItemCategory.TAMING,
                'rarity': ItemRarity.UNCOMMON,
                'target': ItemTarget.SINGLE_ENEMY,
                'price': 300,
                'sell_price': 150,
                'use_in_battle': True,
                'use_in_field': False,
                'consumable': True,
                'effects': [ItemEffect(EffectType.TAMING_BONUS, 2.0)]
            },
            {
                'id': 'edelfleisch',
                'name': 'Edelfleisch',
                'description': 'Hochwertiges Fleisch für anspruchsvolle Monster',
                'category': ItemCategory.TAMING,
                'rarity': ItemRarity.RARE,
                'target': ItemTarget.SINGLE_ENEMY,
                'price': 1000,
                'sell_price': 500,
                'use_in_battle': True,
                'use_in_field': False,
                'consumable': True,
                'effects': [ItemEffect(EffectType.TAMING_BONUS, 3.0)]
            },
            {
                'id': 'goldfleisch',
                'name': 'Goldfleisch',
                'description': 'Legendäres Fleisch mit magischer Anziehungskraft',
                'category': ItemCategory.TAMING,
                'rarity': ItemRarity.LEGENDARY,
                'target': ItemTarget.SINGLE_ENEMY,
                'price': 5000,
                'sell_price': 2500,
                'use_in_battle': True,
                'use_in_field': False,
                'consumable': True,
                'effects': [ItemEffect(EffectType.TAMING_BONUS, 5.0)]
            }
        ]
        
        for item_data in taming_items:
            self._create_and_register_item(item_data)
    
    def _register_battle_items(self):
        """Register all battle items."""
        battle_items = [
            {
                'id': 'x_angriff',
                'name': 'X-Angriff',
                'description': 'Erhöht den Angriff eines Monsters im Kampf',
                'category': ItemCategory.BATTLE,
                'rarity': ItemRarity.COMMON,
                'target': ItemTarget.SINGLE_ALLY,
                'price': 500,
                'sell_price': 250,
                'use_in_battle': True,
                'use_in_field': False,
                'consumable': True,
                'effects': [ItemEffect(EffectType.BUFF_STAT, ('atk', 1))]
            },
            {
                'id': 'x_verteidigung',
                'name': 'X-Verteidigung',
                'description': 'Erhöht die Verteidigung eines Monsters im Kampf',
                'category': ItemCategory.BATTLE,
                'rarity': ItemRarity.COMMON,
                'target': ItemTarget.SINGLE_ALLY,
                'price': 500,
                'sell_price': 250,
                'use_in_battle': True,
                'use_in_field': False,
                'consumable': True,
                'effects': [ItemEffect(EffectType.BUFF_STAT, ('def', 1))]
            },
            {
                'id': 'x_tempo',
                'name': 'X-Tempo',
                'description': 'Erhöht die Initiative eines Monsters im Kampf',
                'category': ItemCategory.BATTLE,
                'rarity': ItemRarity.COMMON,
                'target': ItemTarget.SINGLE_ALLY,
                'price': 500,
                'sell_price': 250,
                'use_in_battle': True,
                'use_in_field': False,
                'consumable': True,
                'effects': [ItemEffect(EffectType.BUFF_STAT, ('spd', 1))]
            },
            {
                'id': 'x_magie',
                'name': 'X-Magie',
                'description': 'Erhöht die Magie eines Monsters im Kampf',
                'category': ItemCategory.BATTLE,
                'rarity': ItemRarity.COMMON,
                'target': ItemTarget.SINGLE_ALLY,
                'price': 500,
                'sell_price': 250,
                'use_in_battle': True,
                'use_in_field': False,
                'consumable': True,
                'effects': [ItemEffect(EffectType.BUFF_STAT, ('mag', 1))]
            },
            {
                'id': 'x_genauigkeit',
                'name': 'X-Genauigkeit',
                'description': 'Erhöht die Genauigkeit eines Monsters im Kampf',
                'category': ItemCategory.BATTLE,
                'rarity': ItemRarity.COMMON,
                'target': ItemTarget.SINGLE_ALLY,
                'price': 500,
                'sell_price': 250,
                'use_in_battle': True,
                'use_in_field': False,
                'consumable': True,
                'effects': [ItemEffect(EffectType.BUFF_STAT, ('acc', 1))]
            }
        ]
        
        for item_data in battle_items:
            self._create_and_register_item(item_data)
    
    def _register_special_items(self):
        """Register all special items."""
        special_items = [
            {
                'id': 'seltene_suessigkeit',
                'name': 'Seltene Süßigkeit',
                'description': 'Erhöht das Level eines Monsters um 1',
                'category': ItemCategory.SPECIAL,
                'rarity': ItemRarity.EPIC,
                'target': ItemTarget.SINGLE_ALLY,
                'price': 5000,
                'sell_price': 2500,
                'use_in_battle': False,
                'use_in_field': True,
                'consumable': True,
                'effects': [ItemEffect(EffectType.LEVEL_UP, 1)]
            },
            {
                'id': 'aether',
                'name': 'Äther',
                'description': 'Stellt 10 AP einer Attacke wieder her',
                'category': ItemCategory.SPECIAL,
                'rarity': ItemRarity.UNCOMMON,
                'target': ItemTarget.SINGLE_ALLY,
                'price': 500,
                'sell_price': 250,
                'use_in_battle': False,
                'use_in_field': True,
                'consumable': True,
                'effects': [ItemEffect(EffectType.RESTORE_PP, {'move': 0, 'amount': 10})]
            },
            {
                'id': 'top_aether',
                'name': 'Top-Äther',
                'description': 'Stellt alle AP einer Attacke wieder her',
                'category': ItemCategory.SPECIAL,
                'rarity': ItemRarity.RARE,
                'target': ItemTarget.SINGLE_ALLY,
                'price': 1500,
                'sell_price': 750,
                'use_in_battle': False,
                'use_in_field': True,
                'consumable': True,
                'effects': [ItemEffect(EffectType.RESTORE_PP, {'move': 0, 'amount': 99})]
            },
            {
                'id': 'fluchtseil',
                'name': 'Fluchtseil',
                'description': 'Ermöglicht die Flucht aus Höhlen und Dungeons',
                'category': ItemCategory.SPECIAL,
                'rarity': ItemRarity.COMMON,
                'target': ItemTarget.NONE,
                'price': 200,
                'sell_price': 100,
                'use_in_battle': False,
                'use_in_field': True,
                'consumable': True,
                'effects': [ItemEffect(EffectType.TELEPORT, 'cave_exit')]
            },
            {
                'id': 'repel',
                'name': 'Repel',
                'description': 'Hält wilde Monster für 100 Schritte fern',
                'category': ItemCategory.SPECIAL,
                'rarity': ItemRarity.COMMON,
                'target': ItemTarget.NONE,
                'price': 300,
                'sell_price': 150,
                'use_in_battle': False,
                'use_in_field': True,
                'consumable': True,
                'effects': [ItemEffect(EffectType.REPEL, 100)]
            },
            {
                'id': 'super_repel',
                'name': 'Super-Repel',
                'description': 'Hält wilde Monster für 200 Schritte fern',
                'category': ItemCategory.SPECIAL,
                'rarity': ItemRarity.UNCOMMON,
                'target': ItemTarget.NONE,
                'price': 500,
                'sell_price': 250,
                'use_in_battle': False,
                'use_in_field': True,
                'consumable': True,
                'effects': [ItemEffect(EffectType.REPEL, 200)]
            }
        ]
        
        for item_data in special_items:
            self._create_and_register_item(item_data)
    
    def _create_and_register_item(self, item_data: Dict[str, Any]):
        """Create and register an item from data."""
        try:
            item = Item(
                id=item_data['id'],
                name=item_data['name'],
                description=item_data['description'],
                category=item_data['category'],
                rarity=item_data['rarity'],
                target=item_data['target'],
                price=item_data['price'],
                sell_price=item_data['sell_price'],
                use_in_battle=item_data['use_in_battle'],
                use_in_field=item_data['use_in_field'],
                consumable=item_data['consumable'],
                effects=item_data['effects']
            )
            self.items[item.id] = item
        except Exception as e:
            print(f"Fehler beim Erstellen von Item {item_data.get('id', 'unknown')}: {e}")
    
    def get_item(self, item_id: str) -> Optional[Item]:
        """Get an item by ID."""
        return self.items.get(item_id)
    
    def get_all_items(self) -> Dict[str, Item]:
        """Get all items."""
        return self.items.copy()
    
    def get_items_by_category(self, category: ItemCategory) -> List[Item]:
        """Get all items of a specific category."""
        return [item for item in self.items.values() if item.category == category]
    
    def get_items_by_rarity(self, rarity: ItemRarity) -> List[Item]:
        """Get all items of a specific rarity."""
        return [item for item in self.items.values() if item.rarity == rarity]
    
    def get_items_by_target(self, target: ItemTarget) -> List[Item]:
        """Get all items with a specific target."""
        return [item for item in self.items.values() if item.target == target]
    
    def search_items(self, query: str) -> List[Item]:
        """Search items by name or description."""
        query = query.lower()
        results = []
        
        for item in self.items.values():
            if (query in item.name.lower() or 
                query in item.description.lower()):
                results.append(item)
        
        return results
    
    def load_from_file(self, filepath: str) -> None:
        """Load items from JSON file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            for item_data in data.get('items', []):
                self._create_and_register_item(item_data)
        except Exception as e:
            print(f"Fehler beim Laden der Items: {e}")


class Inventory:
    """Player's inventory with improved management."""
    
    MAX_STACK = 99
    
    def __init__(self):
        """Initialize inventory."""
        self.items: Dict[str, int] = {}  # item_id -> quantity
        self.key_items: List[str] = []   # List of key item IDs
        self.money = 1000  # Starting money
        self.item_registry = ItemRegistry()
    
    def add_item(self, item_id: str, quantity: int = 1) -> bool:
        """
        Add items to inventory.
        
        Args:
            item_id: Item ID
            quantity: Number to add
            
        Returns:
            True if added successfully
        """
        if item_id not in self.item_registry.items:
            return False
        
        current = self.items.get(item_id, 0)
        item = self.item_registry.get_item(item_id)
        
        if item and item.stack_size:
            max_stack = min(item.stack_size, self.MAX_STACK)
            new_quantity = min(current + quantity, max_stack)
            
            if new_quantity == current:
                return False  # Stack full
            
            self.items[item_id] = new_quantity
            return True
        
        return False
    
    def remove_item(self, item_id: str, quantity: int = 1) -> bool:
        """
        Remove items from inventory.
        
        Args:
            item_id: Item ID
            quantity: Number to remove
            
        Returns:
            True if removed successfully
        """
        current = self.items.get(item_id, 0)
        
        if current < quantity:
            return False
        
        new_quantity = current - quantity
        if new_quantity == 0:
            del self.items[item_id]
        else:
            self.items[item_id] = new_quantity
        
        return True
    
    def has_item(self, item_id: str, quantity: int = 1) -> bool:
        """Check if inventory has enough of an item."""
        return self.items.get(item_id, 0) >= quantity
    
    def can_use_item(self, item_id: str, in_battle: bool = False, player_level: int = 1) -> bool:
        """Check if an item can be used."""
        item = self.item_registry.get_item(item_id)
        if not item:
            return False
        
        if not self.has_item(item_id):
            return False
        
        return item.can_use(in_battle, player_level)
    
    def use_item(self, item_id: str, target: Optional['MonsterInstance'] = None,
                party: Optional['Party'] = None, battle: Optional['Battle'] = None,
                in_battle: bool = False) -> List[str]:
        """
        Use an item.
        
        Args:
            item_id: Item ID to use
            target: Target monster
            party: Player's party
            battle: Current battle state
            in_battle: Whether in battle
            
        Returns:
            List of result messages
        """
        if not self.can_use_item(item_id, in_battle):
            return ["Item kann nicht verwendet werden!"]
        
        item = self.item_registry.get_item(item_id)
        if not item:
            return ["Unbekanntes Item!"]
        
        # Execute effects
        messages = self.item_registry.effect_executor.execute_item_effects(
            item, None, target, party, battle
        )
        
        # Consume item if consumable
        if item.consumable:
            self.remove_item(item_id, 1)
            messages.append(f"{item.name} wurde verbraucht!")
        
        return messages
    
    def get_items_by_category(self, category: ItemCategory) -> List[Tuple[Item, int]]:
        """Get all items of a specific category with quantities."""
        result = []
        for item_id, quantity in self.items.items():
            item = self.item_registry.get_item(item_id)
            if item and item.category == category:
                result.append((item, quantity))
        return result
    
    def get_items_by_rarity(self, rarity: ItemRarity) -> List[Tuple[Item, int]]:
        """Get all items of a specific rarity with quantities."""
        result = []
        for item_id, quantity in self.items.items():
            item = self.item_registry.get_item(item_id)
            if item and item.rarity == rarity:
                result.append((item, quantity))
        return result
    
    def add_key_item(self, item_id: str) -> bool:
        """Add a key item."""
        if item_id not in self.key_items:
            self.key_items.append(item_id)
            return True
        return False
    
    def has_key_item(self, item_id: str) -> bool:
        """Check if has key item."""
        return item_id in self.key_items
    
    def add_money(self, amount: int) -> None:
        """Add money."""
        self.money = min(self.money + amount, 999999)
    
    def remove_money(self, amount: int) -> bool:
        """Remove money if sufficient."""
        if self.money >= amount:
            self.money -= amount
            return True
        return False
    
    def get_item_count(self, item_id: str) -> str:
        """Get quantity of an item."""
        return self.items.get(item_id, 0)
    
    def get_all_items(self) -> List[Tuple[str, int]]:
        """Get all items with quantities."""
        return list(self.items.items())
    
    def get_inventory_value(self) -> int:
        """Calculate total value of inventory items."""
        total = 0
        for item_id, quantity in self.items.items():
            item = self.item_registry.get_item(item_id)
            if item:
                total += item.sell_price * quantity
        return total
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for saving."""
        return {
            'items': self.items.copy(),
            'key_items': self.key_items.copy(),
            'money': self.money
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Inventory':
        """Create from dictionary."""
        inventory = cls()
        inventory.items = data.get('items', {}).copy()
        inventory.key_items = data.get('key_items', []).copy()
        inventory.money = data.get('money', 1000)
        return inventory


# Legacy compatibility
ItemDatabase = ItemRegistry
