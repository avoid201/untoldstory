"""
Comprehensive item system for Untold Story.
Handles healing, status curing, taming, stat boosts, and special effects.
"""

from typing import TYPE_CHECKING, Optional, Dict, List, Any, Callable, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum, auto
import json
import random

from engine.systems.battle.meat_item_bridge import MeatItemBridge

if TYPE_CHECKING:
    from engine.systems.monster_instance import MonsterInstance
    from engine.systems.party import Party
    from engine.systems.monsters import MonsterSpecies
    from engine.systems.battle.battle_controller import BattleState as Battle


class ItemCategory(Enum):
    """Item categories for organization."""
    HEALING = auto()      # HP restoration and revival
    STATUS = auto()        # Status condition cures
    TAMING = auto()        # Monster taming assistance
    BATTLE = auto()        # Battle-only stat boosts
    SPECIAL = auto()       # Unique effects and key items
    EQUIPMENT = auto()     # Held items for monsters
    MISC = auto()          # Other utility items
    MEAT = auto()          # DQM-style meat items for taming


class ItemRarity(Enum):
    """Item rarity levels."""
    COMMON = auto()
    UNCOMMON = auto()
    RARE = auto()
    EPIC = auto()
    LEGENDARY = auto()


class ItemTarget(Enum):
    """Target types for item use."""
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
    effects: List[ItemEffect] = field(default_factory=list)
    
    # Additional properties
    stack_size: int = 99
    icon: str = "item_generic.png"
    sort_order: int = 0


class ItemEffectExecutor:
    """Executes item effects on targets."""
    
    def __init__(self, rng_seed: Optional[int] = None):
        """Initialize executor with optional random seed."""
        self.rng = random.Random(rng_seed)
    
    def execute_item_effects(self, item: Item, 
                           user: Optional['MonsterInstance'] = None,
                           target: Optional['MonsterInstance'] = None,
                           party: Optional['Party'] = None,
                           battle: Optional['Battle'] = None) -> List[Dict[str, Any]]:
        """
        Execute all effects of an item.
        
        Returns:
            List of effect results with type, success, message, etc.
        """
        results = []
        
        # Check for meat items first - DQM Integration
        if item.category == ItemCategory.MEAT:
            # Use MeatItemBridge for meat effects
            bridge_result = MeatItemBridge.apply_meat_effect(
                item_id=item.id,
                target=target,
                battle_state=battle.state if battle else None
            )
            
            if bridge_result:
                results.append({
                    'type': 'taming',
                    'success': bridge_result.get('success', False),
                    'message': bridge_result.get('message', 'Fleisch verwendet'),
                    'catch_chance': bridge_result.get('catch_chance', 0)
                })
                return results
        
        # Execute each effect
        for effect in item.effects:
            if self.rng.random() > effect.chance:
                continue
            
            result = self._apply_effect(effect, item, user, target, party, battle)
            if result:
                results.append({
                    'type': 'effect',
                    'success': True,
                    'message': result
                })
        
        return results
    
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

        elif effect.effect_type == EffectType.ESCAPE:
            return self._escape_battle(battle)
        # Add more effect types as needed
        
        return None
    
    def _heal_hp(self, effect: ItemEffect, target: Optional['MonsterInstance']) -> Optional[str]:
        """Apply HP healing."""
        if not target:
            return None
        
        if isinstance(effect.value, (int, float)):
            if effect.value <= 1.0:  # Percentage healing
                heal_amount = int(target.max_hp * effect.value)
            else:  # Fixed healing
                heal_amount = int(effect.value)
        else:
            heal_amount = 50  # Default
        
        if hasattr(target, 'heal'):
            actual_heal = target.heal(heal_amount)
            return f"{target.name} wurde um {actual_heal} KP geheilt!"
        return None
    
    def _heal_status(self, effect: ItemEffect, target: Optional['MonsterInstance']) -> Optional[str]:
        """Cure specific status condition."""
        if not target or not hasattr(target, 'status'):
            return None
        
        status_to_cure = effect.value
        if hasattr(target, 'status') and target.status == status_to_cure:
            target.status = None
            return f"{target.name} wurde von {status_to_cure} geheilt!"
        return None
    
    def _heal_all_status(self, target: Optional['MonsterInstance']) -> Optional[str]:
        """Cure all status conditions."""
        if not target:
            return None
        
        if hasattr(target, 'status') and target.status:
            target.status = None
            return f"Alle Statusprobleme von {target.name} wurden geheilt!"
        return None
    
    def _revive_monster(self, effect: ItemEffect, target: Optional['MonsterInstance']) -> Optional[str]:
        """Revive a fainted monster."""
        if not target or not getattr(target, 'is_fainted', False):
            return None
        
        if isinstance(effect.value, float):
            hp_percent = effect.value
        else:
            hp_percent = 0.5
        
        target.current_hp = int(target.max_hp * hp_percent)
        target.is_fainted = False
        return f"{target.name} wurde wiederbelebt!"
    
    def _buff_stat(self, effect: ItemEffect, target: Optional['MonsterInstance']) -> Optional[str]:
        """Apply stat buff."""
        if not target:
            return None
        
        if isinstance(effect.value, tuple) and len(effect.value) == 2:
            stat, stages = effect.value
            # Apply stat stage changes if target supports it
            if hasattr(target, 'stat_stages'):
                current = getattr(target.stat_stages, stat, 0)
                new_stages = min(6, current + stages)
                setattr(target.stat_stages, stat, new_stages)
                return f"{target.name}s {stat.upper()} wurde erhöht!"
        return None
    

    
    def _escape_battle(self, battle: Optional['Battle']) -> Optional[str]:
        """Escape from battle."""
        if battle:
            # Set battle to flee state if possible
            return "Erfolgreich aus dem Kampf geflohen!"
        return None
    
    @staticmethod
    def is_meat_item(item_id: str) -> bool:
        """Check if item is a meat item."""
        return item_id.startswith('meat_') or '_meat' in item_id


class ItemRegistry:
    """Registry for all game items."""
    
    def __init__(self):
        """Initialize registry."""
        self.items: Dict[str, Item] = {}
        self._register_default_items()
    
    def _register_default_items(self):
        """Register basic healing items."""
        # Basic healing potion
        trank = Item(
            id="trank",
            name="Trank",
            description="Stellt 50 KP wieder her",
            category=ItemCategory.HEALING,
            rarity=ItemRarity.COMMON,
            target=ItemTarget.SINGLE_ALLY,
            price=200,
            sell_price=100,
            use_in_battle=True,
            use_in_field=True,
            consumable=True,
            effects=[ItemEffect(EffectType.HEAL_HP, 50)]
        )
        self.register_item(trank)
        
        # Super healing potion
        super_trank = Item(
            id="super_trank",
            name="Super-Trank", 
            description="Stellt 100 KP wieder her",
            category=ItemCategory.HEALING,
            rarity=ItemRarity.UNCOMMON,
            target=ItemTarget.SINGLE_ALLY,
            price=500,
            sell_price=250,
            use_in_battle=True,
            use_in_field=True,
            consumable=True,
            effects=[ItemEffect(EffectType.HEAL_HP, 100)]
        )
        self.register_item(super_trank)
        
        # Status cure
        heilmittel = Item(
            id="heilmittel",
            name="Heilmittel",
            description="Heilt alle Statusprobleme",
            category=ItemCategory.STATUS,
            rarity=ItemRarity.UNCOMMON,
            target=ItemTarget.SINGLE_ALLY,
            price=300,
            sell_price=150,
            use_in_battle=True,
            use_in_field=True,
            consumable=True,
            effects=[ItemEffect(EffectType.HEAL_ALL_STATUS, None)]
        )
        self.register_item(heilmittel)
    
    def register_item(self, item: Item) -> bool:
        """Register an item."""
        if item.id not in self.items:
            self.items[item.id] = item
            return True
        return False
    
    def get_item(self, item_id: str) -> Optional[Item]:
        """Get item by ID."""
        return self.items.get(item_id)
    
    def get_all_items(self) -> List[Item]:
        """Get all registered items."""
        return list(self.items.values())


class Inventory:
    """Simple inventory system to hold player items."""
    
    def __init__(self, max_slots: int = 999):
        """Initialize inventory with maximum slots."""
        self.items: Dict[str, int] = {}  # item_id -> quantity
        self.max_slots = max_slots
    
    def add_item(self, item_id: str, quantity: int = 1) -> bool:
        """
        Add items to inventory.
        
        Args:
            item_id: Item identifier
            quantity: Amount to add
            
        Returns:
            True if added successfully
        """
        if len(self.items) >= self.max_slots and item_id not in self.items:
            return False  # Inventory full
        
        self.items[item_id] = self.items.get(item_id, 0) + quantity
        return True
    
    def remove_item(self, item_id: str, quantity: int = 1) -> bool:
        """
        Remove items from inventory.
        
        Args:
            item_id: Item identifier  
            quantity: Amount to remove
            
        Returns:
            True if removed successfully
        """
        if item_id not in self.items or self.items[item_id] < quantity:
            return False
        
        self.items[item_id] -= quantity
        if self.items[item_id] <= 0:
            del self.items[item_id]
        
        return True
    
    def has_item(self, item_id: str, quantity: int = 1) -> bool:
        """Check if inventory contains specific item quantity."""
        return self.items.get(item_id, 0) >= quantity
    
    def get_quantity(self, item_id: str) -> int:
        """Get quantity of specific item."""
        return self.items.get(item_id, 0)
    
    def get_all_items(self) -> List[Tuple[str, int]]:
        """Get all items as (item_id, quantity) tuples."""
        return list(self.items.items())
    
    def is_full(self) -> bool:
        """Check if inventory is at maximum capacity."""
        return len(self.items) >= self.max_slots
    
    def get_slot_count(self) -> int:
        """Get current number of used slots."""
        return len(self.items)
    
    def clear(self) -> None:
        """Clear all items from inventory."""
        self.items.clear()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert inventory to dictionary for saving."""
        return {
            'items': self.items.copy(),
            'max_slots': self.max_slots
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Inventory':
        """Create inventory from saved dictionary."""
        inventory = cls(max_slots=data.get('max_slots', 999))
        inventory.items = data.get('items', {}).copy()
        return inventory


# Global item registry instance
item_registry = ItemRegistry()

# Export classes and instances for external use  
__all__ = [
    'Item', 'ItemCategory', 'ItemRarity', 'ItemTarget', 'ItemEffect', 'EffectType',
    'ItemEffectExecutor', 'ItemRegistry', 'Inventory', 'item_registry'
]
