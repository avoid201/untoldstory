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
    """Types of effects items and battle actions can have."""
    # Item Effects
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
    RESTORE_PP = auto()         # Restore move PP/AP
    
    # Battle Effects
    DAMAGE = auto()             # Deal damage
    HEAL = auto()               # Heal HP
    STATUS = auto()             # Apply status condition
    STAT_CHANGE = auto()        # Change stat stages
    WEATHER = auto()            # Change weather
    TERRAIN = auto()            # Change terrain
    PROTECT = auto()            # Protect from damage
    RECOIL = auto()             # Recoil damage
    DRAIN = auto()              # Drain HP/MP
    FLINCH = auto()             # Cause flinch
    CONFUSE = auto()            # Cause confusion
    TRAP = auto()               # Trap effect
    SUBSTITUTE = auto()         # Substitute effect
    REFLECT = auto()            # Reflect damage
    LIGHT_SCREEN = auto()       # Light screen effect
    ITEM_HEAL = auto()          # Item healing effect
    ITEM_STATUS = auto()        # Item status effect
    ITEM_STAT = auto()          # Item stat effect
    ITEM_SPECIAL = auto()       # Special item effect


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
                           battle: Optional['Battle'] = None) -> List[str]:
        """
        Execute all effects of an item.
        
        Returns:
            List of effect messages
        """
        messages = []
        
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

        elif effect.effect_type == EffectType.ESCAPE:
            return self._escape_battle(battle)
        elif effect.effect_type == EffectType.RESTORE_PP:
            return self._restore_pp(effect, target)
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
    
    def _restore_pp(self, effect: ItemEffect, target: Optional['MonsterInstance']) -> Optional[str]:
        """Restore move PP/AP."""
        if not target:
            return None
        
        # Effect value should be a dict with move and amount
        if isinstance(effect.value, dict):
            move_index = effect.value.get('move', 0)
            amount = effect.value.get('amount', 10)
            
            # Check if target has moves and the specified move exists
            available_moves = target.get_available_moves()
            if available_moves and move_index < len(available_moves):
                move = available_moves[move_index]
                if hasattr(move, 'current_pp'):
                    old_pp = move.current_pp
                    move.current_pp = min(move.max_pp, move.current_pp + amount)
                    restored = move.current_pp - old_pp
                    return f"{target.name}s {move.name} AP um {restored} wiederhergestellt!"
        
        return None


class ItemRegistry:
    """Registry for all game items."""
    
    def __init__(self):
        """Initialize registry."""
        self.items: Dict[str, Item] = {}
        self._register_default_items()
        self._load_items_from_json()
    
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
    
    def _load_items_from_json(self):
        """Load items from JSON file."""
        try:
            import json
            import os
            
            # Get path to items.json
            json_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'data', 'items.json'
            )
            
            if not os.path.exists(json_path):
                print(f"[ItemRegistry] items.json not found at {json_path}")
                return
            
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Process each item from JSON
            for item_data in data.get('items', []):
                try:
                    # Parse category
                    category_str = item_data.get('category', 'MISC')
                    try:
                        category = ItemCategory[category_str]
                    except KeyError:
                        category = ItemCategory.MISC
                    
                    # Parse rarity
                    rarity_str = item_data.get('rarity', 'COMMON')
                    try:
                        rarity = ItemRarity[rarity_str]
                    except KeyError:
                        rarity = ItemRarity.COMMON
                    
                    # Parse target
                    target_str = item_data.get('target', 'NONE')
                    try:
                        target = ItemTarget[target_str]
                    except KeyError:
                        target = ItemTarget.NONE
                    
                    # Parse effects
                    effects = []
                    for effect_data in item_data.get('effects', []):
                        effect_type_str = effect_data.get('type', '')
                        try:
                            effect_type = EffectType[effect_type_str]
                        except KeyError:
                            continue
                        
                        target_type_str = effect_data.get('target_type', 'SELF')
                        try:
                            target_type = ItemTarget[target_type_str]
                        except KeyError:
                            target_type = ItemTarget.SELF
                        
                        effect = ItemEffect(
                            effect_type=effect_type,
                            value=effect_data.get('value'),
                            chance=effect_data.get('chance', 1.0),
                            message=effect_data.get('message', ''),
                            target_type=target_type
                        )
                        effects.append(effect)
                    
                    # Create and register item
                    item = Item(
                        id=item_data.get('id', 'unknown'),
                        name=item_data.get('name', 'Unknown'),
                        description=item_data.get('description', ''),
                        category=category,
                        rarity=rarity,
                        target=target,
                        price=item_data.get('price', 0),
                        sell_price=item_data.get('sell_price', 0),
                        use_in_battle=item_data.get('use_in_battle', False),
                        use_in_field=item_data.get('use_in_field', False),
                        consumable=item_data.get('consumable', True),
                        effects=effects,
                        stack_size=item_data.get('stack_size', 99),
                        icon=item_data.get('icon', 'item_generic.png'),
                        sort_order=item_data.get('sort_order', 0)
                    )
                    
                    # Only override if not already registered
                    if item.id not in self.items:
                        self.register_item(item)
                    
                except Exception as e:
                    print(f"[ItemRegistry] Error loading item {item_data.get('id', 'unknown')}: {e}")
                    continue
            
            print(f"[ItemRegistry] Loaded {len(self.items)} items total")
            
        except Exception as e:
            print(f"[ItemRegistry] Error loading items from JSON: {e}")


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
        """Convert inventory to dictionary for serialization."""
        return {
            'items': self.items.copy(),
            'max_slots': self.max_slots
        }


class ItemManager:
    """Manages item usage in battle and field."""
    
    def __init__(self, inventory: Inventory):
        """Initialize item manager with player inventory."""
        self.inventory = inventory
        self.registry = item_registry
        self.effect_executor = ItemEffectExecutor()
        self._current_battle_state = None  # For DQM meat integration
    
    def use_battle_item(self, item_id: str, target: Optional['MonsterInstance'] = None) -> Dict[str, Any]:
        """
        Use item in battle and return result.
        
        Args:
            item_id: Item identifier
            target: Target monster (for healing/status items)
            
        Returns:
            Dictionary with success status, messages, and effects
        """
        # Check if item exists
        item = self.registry.get_item(item_id)
        if not item:
            return {'success': False, 'message': 'Item existiert nicht!'}
        
        # Check if item can be used in battle
        if not item.use_in_battle:
            return {'success': False, 'message': 'Item kann nicht im Kampf verwendet werden!'}
        
        # Check if player has the item
        if not self.inventory.has_item(item_id, 1):
            return {'success': False, 'message': 'Du hast dieses Item nicht!'}
        
        # Check if item is consumable and remove it
        if item.consumable:
            if not self.inventory.remove_item(item_id, 1):
                return {'success': False, 'message': 'Item konnte nicht entfernt werden!'}
        
        # Execute item effects
        result = {'success': True, 'message': '', 'effects': {}}
        
        # Handle different item categories
        if item.category == ItemCategory.HEALING:
            result.update(self._handle_healing_item(item, target))
        elif item.category == ItemCategory.STATUS:
            result.update(self._handle_status_item(item, target))
        elif item.category == ItemCategory.BATTLE:
            result.update(self._handle_battle_item(item, target))
        elif item.category == ItemCategory.TAMING:
            result.update(self._handle_taming_item(item, target))
        else:
            result.update(self._handle_generic_item(item, target))
        
        return result
    
    def _handle_healing_item(self, item: Item, target: Optional['MonsterInstance']) -> Dict[str, Any]:
        """Handle healing items."""
        if not target:
            return {'success': False, 'message': 'Kein Ziel ausgewählt!'}
        
        if target.is_fainted:
            return {'success': False, 'message': 'Ohnmächtige Monster können nicht geheilt werden!'}
        
        # Execute healing effects
        messages = self.effect_executor.execute_item_effects(item, target=target)
        
        return {
            'success': True,
            'message': '; '.join(messages) if messages else f"{item.name} wurde verwendet!",
            'effects': {'healing': True}
        }
    
    def _handle_status_item(self, item: Item, target: Optional['MonsterInstance']) -> Dict[str, Any]:
        """Handle status cure items."""
        if not target:
            return {'success': False, 'message': 'Kein Ziel ausgewählt!'}
        
        if target.is_fainted:
            return {'success': False, 'message': 'Ohnmächtige Monster können nicht behandelt werden!'}
        
        # Execute status effects
        messages = self.effect_executor.execute_item_effects(item, target=target)
        
        return {
            'success': True,
            'message': '; '.join(messages) if messages else f"{item.name} wurde verwendet!",
            'effects': {'status_cure': True}
        }
    
    def _handle_battle_item(self, item: Item, target: Optional['MonsterInstance']) -> Dict[str, Any]:
        """Handle battle stat boost items."""
        if not target:
            return {'success': False, 'message': 'Kein Ziel ausgewählt!'}
        
        if target.is_fainted:
            return {'success': False, 'message': 'Ohnmächtige Monster können keine Items verwenden!'}
        
        # Execute battle effects
        messages = self.effect_executor.execute_item_effects(item, target=target)
        
        return {
            'success': True,
            'message': '; '.join(messages) if messages else f"{item.name} wurde verwendet!",
            'effects': {'stat_boost': True}
        }
    
    def _handle_taming_item(self, item: Item, target: Optional['MonsterInstance']) -> Dict[str, Any]:
        """Handle taming items (meat) - DQM-Integration."""
        # Check if it's a meat item
        if self._is_meat_item(item.id):
            # Get meat bonus based on item type
            meat_bonus = self._get_meat_bonus(item.id)
            
            # Check if there's an enemy to tame
            if not target:
                return {'success': False, 'message': 'Kein Monster zum Zähmen verfügbar!'}
            
            # Check if enemy is wild
            if not getattr(target, 'is_wild', True):
                return {'success': False, 'message': 'Dieses Monster kann nicht gezähmt werden!'}
            
            # Calculate taming chance
            base_chance = 0.15  # 15% base chance
            meat_bonus_percent = meat_bonus / 100.0
            final_chance = min(base_chance + meat_bonus_percent, 0.95)  # Max 95%
            
            # Roll for success
            import random
            success = random.random() < final_chance
            
            if success:
                # Taming successful
                message = f"{target.name} wurde erfolgreich gezähmt!"
                return {
                    'success': True,
                    'message': message,
                    'effects': {'taming_success': True, 'consume_turn': True}
                }
            else:
                # Taming failed
                message = f"Zähmversuch fehlgeschlagen! {target.name} ist nicht interessiert."
                return {
                    'success': True,
                    'message': message,
                    'effects': {'taming_success': False, 'consume_turn': True}
                }
        
        # Fallback for non-meat taming items
        taming_bonus = 1.0
        
        # Extract taming bonus from effects
        for effect in item.effects:
            if effect.effect_type == EffectType.TAMING_BONUS:
                taming_bonus = effect.value
                break
        
        return {
            'success': True,
            'message': f"{item.name} wurde vorbereitet! Zähm-Bonus: +{int((taming_bonus - 1) * 100)}%",
            'effects': {'taming_bonus': taming_bonus, 'consume_turn': True}
        }
    
    def _is_meat_item(self, item_id: str) -> bool:
        """Check if item is a meat item for taming."""
        meat_items = ['fleisch', 'lecker_fleisch', 'edelfleisch', 'goldfleisch']
        return item_id in meat_items
    
    def _get_meat_bonus(self, item_id: str) -> int:
        """Get meat bonus based on item type."""
        meat_bonuses = {
            'fleisch': 20,
            'lecker_fleisch': 30,
            'edelfleisch': 40,
            'goldfleisch': 80
        }
        return meat_bonuses.get(item_id, 0)
    
    def _handle_generic_item(self, item: Item, target: Optional['MonsterInstance']) -> Dict[str, Any]:
        """Handle generic items."""
        messages = self.effect_executor.execute_item_effects(item, target=target)
        
        return {
            'success': True,
            'message': '; '.join(messages) if messages else f"{item.name} wurde verwendet!",
            'effects': {}
        }
    
    def get_available_battle_items(self) -> List[Item]:
        """Get all items that can be used in battle."""
        available_items = []
        
        for item_id in self.inventory.items:
            item = self.registry.get_item(item_id)
            if item and item.use_in_battle and self.inventory.has_item(item_id, 1):
                available_items.append(item)
        
        return available_items
    
    def get_items_by_category(self, category: ItemCategory) -> List[Item]:
        """Get items by category that player has."""
        items = []
        
        for item_id in self.inventory.items:
            item = self.registry.get_item(item_id)
            if item and item.category == category and self.inventory.has_item(item_id, 1):
                items.append(item)
        
        return items
    
    def set_battle_state(self, battle_state):
        """Set the current battle state for DQM meat integration."""
        self._current_battle_state = battle_state
    
    def sync_meat_inventory(self):
        """Sync meat inventory with item inventory using MeatSystem."""
        try:
            meat_system = get_meat_system()
            meat_system.sync_with_item_inventory(self.inventory.items)
            print("Meat inventory synced successfully")
        except Exception as e:
            print(f"Error syncing meat inventory: {e}")
    
    def use_meat_item(self, item_id: str, battle_state=None) -> Dict[str, Any]:
        """
        Use a meat item with proper DQM-style handling.
        
        Args:
            item_id: The meat item ID
            battle_state: Current battle state (optional)
            
        Returns:
            Result dictionary with success status and effects
        """
        try:
            # Check if it's a meat item
            meat_system = get_meat_system()
            if not meat_system.is_meat_item(item_id):
                return {'success': False, 'message': 'Item ist kein Fleisch!'}
            
            # Get meat type
            meat_type = meat_system.get_meat_type_from_item_id(item_id)
            if not meat_type:
                return {'success': False, 'message': 'Ungültiger Fleisch-Typ!'}
            
            # Check if player has the item
            if not self.inventory.has_item(item_id, 1):
                return {'success': False, 'message': 'Du hast dieses Fleisch nicht!'}
            
            # Use the meat item bridge for proper handling
            if battle_state:
                item_data = {
                    'id': item_id,
                    'name': self.registry.get_item(item_id).name if self.registry.get_item(item_id) else item_id,
                    'description': self.registry.get_item(item_id).description if self.registry.get_item(item_id) else ""
                }
                result = handle_meat_item_use(item_data, battle_state)
                
                # Remove item from inventory if successful
                if result.get('success', False):
                    self.inventory.remove_item(item_id, 1)
                
                return result
            else:
                # Fallback for non-battle usage - still consume the item
                self.inventory.remove_item(item_id, 1)
                return {
                    'success': True,
                    'message': f"{meat_type.display_name} wurde vorbereitet! Zähm-Bonus: +{int(meat_type.bonus * 100)}%",
                    'effects': {'taming_bonus': 1.0 + meat_type.bonus, 'consume_turn': True}
                }
                
        except Exception as e:
            print(f"Error using meat item {item_id}: {e}")
            return {'success': False, 'message': f'Fehler beim Verwenden von Fleisch: {str(e)}'}


# Global item registry instance
item_registry = ItemRegistry()

# Export classes and instances for external use  
__all__ = [
    'Item', 'ItemCategory', 'ItemRarity', 'ItemTarget', 'ItemEffect', 'EffectType',
    'ItemEffectExecutor', 'ItemRegistry', 'Inventory', 'ItemManager', 'item_registry'
]
