"""
Item system for healing, buffs, taming, and equipment.
"""

from typing import TYPE_CHECKING, Optional, Dict, List, Any, Callable, Tuple
from dataclasses import dataclass
from enum import Enum, auto
import json

if TYPE_CHECKING:
    from engine.systems.monster_instance import MonsterInstance
    from engine.systems.party import Party


class ItemType(Enum):
    """Types of items."""
    HEALING = auto()      # Heals HP/status
    BUFF = auto()         # Temporary stat boosts
    TAMING = auto()       # Used for taming monsters
    EVOLUTION = auto()    # Triggers evolution
    KEY = auto()          # Story/quest items
    BATTLE = auto()       # Battle-only items
    EQUIPMENT = auto()    # Held items for monsters
    MISC = auto()         # Other items


class ItemTarget(Enum):
    """Valid targets for item use."""
    SINGLE_MONSTER = auto()   # One monster
    ALL_PARTY = auto()        # Entire party
    SINGLE_ENEMY = auto()     # One enemy (battle only)
    ALL_ENEMIES = auto()      # All enemies (battle only)
    FIELD = auto()            # Field effect
    NONE = auto()             # No target needed


@dataclass
class ItemEffect:
    """Effect of using an item."""
    effect_type: str
    value: Any
    chance: float = 1.0
    message: str = ""


@dataclass
class Item:
    """Base item class."""
    id: str
    name: str
    description: str
    item_type: ItemType
    target: ItemTarget
    price: int
    sell_price: int
    usable_in_battle: bool
    usable_in_field: bool
    consumable: bool
    effects: List[ItemEffect]
    sprite_index: int = 0
    
    def can_use(self, in_battle: bool = False) -> bool:
        """Check if item can be used in current context."""
        if in_battle:
            return self.usable_in_battle
        return self.usable_in_field
    
    def use(self, target: Optional['MonsterInstance'] = None,
            party: Optional['Party'] = None,
            in_battle: bool = False) -> List[str]:
        """
        Use the item.
        
        Args:
            target: Target monster
            party: Party (for party-wide items)
            in_battle: Whether in battle
            
        Returns:
            List of result messages
        """
        messages = []
        
        for effect in self.effects:
            import random
            if random.random() > effect.chance:
                continue
            
            result = self._apply_effect(effect, target, party)
            if result:
                messages.append(result)
        
        return messages
    
    def _apply_effect(self, effect: ItemEffect,
                     target: Optional['MonsterInstance'],
                     party: Optional['Party']) -> Optional[str]:
        """Apply a single effect."""
        if effect.effect_type == 'heal_hp':
            if target:
                if isinstance(effect.value, float):
                    # Percentage heal
                    amount = int(target.max_hp * effect.value)
                else:
                    # Fixed heal
                    amount = effect.value
                
                actual = min(amount, target.max_hp - target.current_hp)
                target.current_hp += actual
                return f"{target.nickname or target.species.name} heilt {actual} KP!"
        
        elif effect.effect_type == 'heal_status':
            if target and target.status == effect.value:
                target.status = None
                target.status_turns = 0
                return f"{target.nickname or target.species.name} wurde von {effect.value} geheilt!"
        
        elif effect.effect_type == 'heal_all_status':
            if target and target.status:
                old_status = target.status
                target.status = None
                target.status_turns = 0
                return f"{target.nickname or target.species.name} wurde von {old_status} geheilt!"
        
        elif effect.effect_type == 'revive':
            if target and target.current_hp == 0:
                target.current_hp = int(target.max_hp * effect.value)
                return f"{target.nickname or target.species.name} wurde wiederbelebt!"
        
        elif effect.effect_type == 'buff_stat':
            if target:
                stat, stages = effect.value
                current = target.stat_stages.get(stat, 0)
                new_stage = max(-6, min(6, current + stages))
                target.stat_stages[stat] = new_stage
                
                stat_names = {
                    'atk': 'Angriff', 'def': 'Verteidigung',
                    'mag': 'Magie', 'res': 'Resistenz',
                    'spd': 'Initiative'
                }
                return f"{target.nickname or target.species.name}'s {stat_names.get(stat, stat)} steigt!"
        
        elif effect.effect_type == 'restore_pp':
            if target:
                move_index = effect.value.get('move', 0)
                amount = effect.value.get('amount', 10)
                
                if 0 <= move_index < len(target.moves) and target.moves[move_index]:
                    move = target.moves[move_index]
                    restored = min(amount, move.max_pp - move.current_pp)
                    move.current_pp += restored
                    return f"{move.name} erhält {restored} AP!"
        
        elif effect.effect_type == 'gain_exp':
            if target:
                target.gain_exp(effect.value)
                return f"{target.nickname or target.species.name} erhält {effect.value} EP!"
        
        elif effect.effect_type == 'level_up':
            if target:
                for _ in range(effect.value):
                    if target.level < 100:
                        target.level_up()
                return f"{target.nickname or target.species.name} erreicht Level {target.level}!"
        
        elif effect.effect_type == 'increase_happiness':
            if target and hasattr(target, 'happiness'):
                target.happiness = min(255, target.happiness + effect.value)
                return f"{target.nickname or target.species.name} wird glücklicher!"
        
        return effect.message if effect.message else None


class ItemDatabase:
    """Database of all items."""
    
    def __init__(self):
        """Initialize item database."""
        self.items: Dict[str, Item] = {}
        self._load_items()
    
    def _load_items(self) -> None:
        """Load items from data file or create defaults."""
        # Healing items
        self.items['potion'] = Item(
            id='potion',
            name='Trank',
            description='Heilt 20 KP',
            item_type=ItemType.HEALING,
            target=ItemTarget.SINGLE_MONSTER,
            price=100,
            sell_price=50,
            usable_in_battle=True,
            usable_in_field=True,
            consumable=True,
            effects=[ItemEffect('heal_hp', 20)]
        )
        
        self.items['super_potion'] = Item(
            id='super_potion',
            name='Supertrank',
            description='Heilt 50 KP',
            item_type=ItemType.HEALING,
            target=ItemTarget.SINGLE_MONSTER,
            price=300,
            sell_price=150,
            usable_in_battle=True,
            usable_in_field=True,
            consumable=True,
            effects=[ItemEffect('heal_hp', 50)]
        )
        
        self.items['hyper_potion'] = Item(
            id='hyper_potion',
            name='Hypertrank',
            description='Heilt 100 KP',
            item_type=ItemType.HEALING,
            target=ItemTarget.SINGLE_MONSTER,
            price=800,
            sell_price=400,
            usable_in_battle=True,
            usable_in_field=True,
            consumable=True,
            effects=[ItemEffect('heal_hp', 100)]
        )
        
        self.items['max_potion'] = Item(
            id='max_potion',
            name='Top-Trank',
            description='Heilt alle KP',
            item_type=ItemType.HEALING,
            target=ItemTarget.SINGLE_MONSTER,
            price=2000,
            sell_price=1000,
            usable_in_battle=True,
            usable_in_field=True,
            consumable=True,
            effects=[ItemEffect('heal_hp', 1.0)]  # 100% heal
        )
        
        # Status healing
        self.items['antidote'] = Item(
            id='antidote',
            name='Gegengift',
            description='Heilt Vergiftung',
            item_type=ItemType.HEALING,
            target=ItemTarget.SINGLE_MONSTER,
            price=100,
            sell_price=50,
            usable_in_battle=True,
            usable_in_field=True,
            consumable=True,
            effects=[ItemEffect('heal_status', 'poison')]
        )
        
        self.items['burn_heal'] = Item(
            id='burn_heal',
            name='Brandsalbe',
            description='Heilt Verbrennung',
            item_type=ItemType.HEALING,
            target=ItemTarget.SINGLE_MONSTER,
            price=100,
            sell_price=50,
            usable_in_battle=True,
            usable_in_field=True,
            consumable=True,
            effects=[ItemEffect('heal_status', 'burn')]
        )
        
        self.items['ice_heal'] = Item(
            id='ice_heal',
            name='Auftaumittel',
            description='Heilt Einfrierung',
            item_type=ItemType.HEALING,
            target=ItemTarget.SINGLE_MONSTER,
            price=100,
            sell_price=50,
            usable_in_battle=True,
            usable_in_field=True,
            consumable=True,
            effects=[ItemEffect('heal_status', 'freeze')]
        )
        
        self.items['awakening'] = Item(
            id='awakening',
            name='Aufwecker',
            description='Weckt schlafende Monster',
            item_type=ItemType.HEALING,
            target=ItemTarget.SINGLE_MONSTER,
            price=100,
            sell_price=50,
            usable_in_battle=True,
            usable_in_field=True,
            consumable=True,
            effects=[ItemEffect('heal_status', 'sleep')]
        )
        
        self.items['paralyz_heal'] = Item(
            id='paralyz_heal',
            name='Anti-Paralyse',
            description='Heilt Paralyse',
            item_type=ItemType.HEALING,
            target=ItemTarget.SINGLE_MONSTER,
            price=100,
            sell_price=50,
            usable_in_battle=True,
            usable_in_field=True,
            consumable=True,
            effects=[ItemEffect('heal_status', 'paralysis')]
        )
        
        self.items['full_heal'] = Item(
            id='full_heal',
            name='Totalheilung',
            description='Heilt alle Statusprobleme',
            item_type=ItemType.HEALING,
            target=ItemTarget.SINGLE_MONSTER,
            price=400,
            sell_price=200,
            usable_in_battle=True,
            usable_in_field=True,
            consumable=True,
            effects=[ItemEffect('heal_all_status', None)]
        )
        
        # Revival
        self.items['revive'] = Item(
            id='revive',
            name='Wiederbelebung',
            description='Belebt besiegte Monster mit halben KP wieder',
            item_type=ItemType.HEALING,
            target=ItemTarget.SINGLE_MONSTER,
            price=1000,
            sell_price=500,
            usable_in_battle=False,
            usable_in_field=True,
            consumable=True,
            effects=[ItemEffect('revive', 0.5)]
        )
        
        self.items['max_revive'] = Item(
            id='max_revive',
            name='Top-Wiederbelebung',
            description='Belebt besiegte Monster mit vollen KP wieder',
            item_type=ItemType.HEALING,
            target=ItemTarget.SINGLE_MONSTER,
            price=2500,
            sell_price=1250,
            usable_in_battle=False,
            usable_in_field=True,
            consumable=True,
            effects=[ItemEffect('revive', 1.0)]
        )
        
        # Battle items
        self.items['x_attack'] = Item(
            id='x_attack',
            name='X-Angriff',
            description='Erhöht Angriff im Kampf',
            item_type=ItemType.BATTLE,
            target=ItemTarget.SINGLE_MONSTER,
            price=500,
            sell_price=250,
            usable_in_battle=True,
            usable_in_field=False,
            consumable=True,
            effects=[ItemEffect('buff_stat', ('atk', 1))]
        )
        
        self.items['x_defense'] = Item(
            id='x_defense',
            name='X-Verteidigung',
            description='Erhöht Verteidigung im Kampf',
            item_type=ItemType.BATTLE,
            target=ItemTarget.SINGLE_MONSTER,
            price=500,
            sell_price=250,
            usable_in_battle=True,
            usable_in_field=False,
            consumable=True,
            effects=[ItemEffect('buff_stat', ('def', 1))]
        )
        
        self.items['x_speed'] = Item(
            id='x_speed',
            name='X-Tempo',
            description='Erhöht Initiative im Kampf',
            item_type=ItemType.BATTLE,
            target=ItemTarget.SINGLE_MONSTER,
            price=500,
            sell_price=250,
            usable_in_battle=True,
            usable_in_field=False,
            consumable=True,
            effects=[ItemEffect('buff_stat', ('spd', 1))]
        )
        
        # Taming items (from taming.py)
        self.items['fleisch'] = Item(
            id='fleisch',
            name='Fleisch',
            description='Normales Fleisch zum Zähmen',
            item_type=ItemType.TAMING,
            target=ItemTarget.SINGLE_ENEMY,
            price=100,
            sell_price=50,
            usable_in_battle=True,
            usable_in_field=False,
            consumable=True,
            effects=[ItemEffect('taming_bonus', 1.5)]
        )
        
        self.items['lecker_fleisch'] = Item(
            id='lecker_fleisch',
            name='Lecker Fleisch',
            description='Schmackhaftes Fleisch, beliebt bei Monstern',
            item_type=ItemType.TAMING,
            target=ItemTarget.SINGLE_ENEMY,
            price=300,
            sell_price=150,
            usable_in_battle=True,
            usable_in_field=False,
            consumable=True,
            effects=[ItemEffect('taming_bonus', 2.0)]
        )
        
        self.items['edel_fleisch'] = Item(
            id='edel_fleisch',
            name='Edelfleisch',
            description='Hochwertiges Fleisch für anspruchsvolle Monster',
            item_type=ItemType.TAMING,
            target=ItemTarget.SINGLE_ENEMY,
            price=1000,
            sell_price=500,
            usable_in_battle=True,
            usable_in_field=False,
            consumable=True,
            effects=[ItemEffect('taming_bonus', 3.0)]
        )
        
        self.items['gold_fleisch'] = Item(
            id='gold_fleisch',
            name='Goldfleisch',
            description='Legendäres Fleisch mit magischer Anziehungskraft',
            item_type=ItemType.TAMING,
            target=ItemTarget.SINGLE_ENEMY,
            price=5000,
            sell_price=2500,
            usable_in_battle=True,
            usable_in_field=False,
            consumable=True,
            effects=[ItemEffect('taming_bonus', 5.0)]
        )
        
        # PP restoration
        self.items['ether'] = Item(
            id='ether',
            name='Äther',
            description='Stellt 10 AP einer Attacke wieder her',
            item_type=ItemType.HEALING,
            target=ItemTarget.SINGLE_MONSTER,
            price=500,
            sell_price=250,
            usable_in_battle=False,
            usable_in_field=True,
            consumable=True,
            effects=[ItemEffect('restore_pp', {'move': 0, 'amount': 10})]
        )
        
        self.items['max_ether'] = Item(
            id='max_ether',
            name='Top-Äther',
            description='Stellt alle AP einer Attacke wieder her',
            item_type=ItemType.HEALING,
            target=ItemTarget.SINGLE_MONSTER,
            price=1500,
            sell_price=750,
            usable_in_battle=False,
            usable_in_field=True,
            consumable=True,
            effects=[ItemEffect('restore_pp', {'move': 0, 'amount': 99})]
        )
        
        # Experience items
        self.items['rare_candy'] = Item(
            id='rare_candy',
            name='Seltene Süßigkeit',
            description='Erhöht das Level eines Monsters um 1',
            item_type=ItemType.BUFF,
            target=ItemTarget.SINGLE_MONSTER,
            price=5000,
            sell_price=2500,
            usable_in_battle=False,
            usable_in_field=True,
            consumable=True,
            effects=[ItemEffect('level_up', 1)]
        )
        
        self.items['exp_share'] = Item(
            id='exp_share',
            name='EP-Teiler',
            description='Teilt Erfahrung mit allen Gruppenmitgliedern',
            item_type=ItemType.EQUIPMENT,
            target=ItemTarget.NONE,
            price=3000,
            sell_price=1500,
            usable_in_battle=False,
            usable_in_field=False,
            consumable=False,
            effects=[]
        )
        
        # Key items
        self.items['map'] = Item(
            id='map',
            name='Karte',
            description='Eine Karte der Region',
            item_type=ItemType.KEY,
            target=ItemTarget.NONE,
            price=0,
            sell_price=0,
            usable_in_battle=False,
            usable_in_field=True,
            consumable=False,
            effects=[]
        )
        
        self.items['fossil'] = Item(
            id='fossil',
            name='Fossil',
            description='Ein uraltes Monster-Fossil',
            item_type=ItemType.KEY,
            target=ItemTarget.NONE,
            price=0,
            sell_price=0,
            usable_in_battle=False,
            usable_in_field=False,
            consumable=False,
            effects=[]
        )
    
    def get_item(self, item_id: str) -> Optional[Item]:
        """Get an item by ID."""
        return self.items.get(item_id)
    
    def load_from_file(self, filepath: str) -> None:
        """Load items from JSON file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            for item_data in data.get('items', []):
                item = self._create_item_from_data(item_data)
                if item:
                    self.items[item.id] = item
        except Exception as e:
            print(f"Failed to load items: {e}")
    
    def _create_item_from_data(self, data: Dict) -> Optional[Item]:
        """Create an item from dictionary data."""
        try:
            effects = []
            for effect_data in data.get('effects', []):
                effect = ItemEffect(
                    effect_type=effect_data['type'],
                    value=effect_data.get('value'),
                    chance=effect_data.get('chance', 1.0),
                    message=effect_data.get('message', '')
                )
                effects.append(effect)
            
            return Item(
                id=data['id'],
                name=data['name'],
                description=data['description'],
                item_type=ItemType[data['type'].upper()],
                target=ItemTarget[data['target'].upper()],
                price=data['price'],
                sell_price=data.get('sell_price', data['price'] // 2),
                usable_in_battle=data.get('usable_in_battle', False),
                usable_in_field=data.get('usable_in_field', True),
                consumable=data.get('consumable', True),
                effects=effects,
                sprite_index=data.get('sprite_index', 0)
            )
        except Exception as e:
            print(f"Failed to create item from data: {e}")
            return None


class Inventory:
    """Player's inventory."""
    
    MAX_STACK = 99
    
    def __init__(self):
        """Initialize inventory."""
        self.items: Dict[str, int] = {}  # item_id -> quantity
        self.key_items: List[str] = []   # List of key item IDs
        self.money = 1000  # Starting money
    
    def add_item(self, item_id: str, quantity: int = 1) -> bool:
        """
        Add items to inventory.
        
        Args:
            item_id: Item ID
            quantity: Number to add
            
        Returns:
            True if added successfully
        """
        current = self.items.get(item_id, 0)
        new_quantity = min(current + quantity, self.MAX_STACK)
        
        if new_quantity == current:
            return False  # Stack full
        
        self.items[item_id] = new_quantity
        return True
    
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
    
    def get_item_count(self, item_id: str) -> int:
        """Get quantity of an item."""
        return self.items.get(item_id, 0)
    
    def get_all_items(self) -> List[Tuple[str, int]]:
        """Get all items with quantities."""
        return list(self.items.items())
    
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