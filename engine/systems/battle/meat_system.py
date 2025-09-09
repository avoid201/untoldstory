"""
Meat System for Dragon Quest Monsters-style taming.
Handles meat items and their effects on taming chances.
"""

import logging
from typing import Dict, Optional, Tuple, Any
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class MeatType(Enum):
    """Different types of meat with their taming bonuses."""
    NONE = ("Kein Fleisch", 0.0, 0)
    NORMAL = ("Fleisch", 0.2, 50)  # +20% taming chance, costs 50 gold
    SUPER = ("Edelfleisch", 0.4, 200)  # +40% taming chance, costs 200 gold
    DIVINE = ("Götterfleisch", 0.8, 1000)  # +80% taming chance, costs 1000 gold
    
    def __init__(self, display_name: str, bonus: float, cost: int):
        self.display_name = display_name
        self.bonus = bonus
        self.cost = cost


@dataclass
class MeatEffect:
    """Active meat effect in battle."""
    meat_type: MeatType
    turns_remaining: int = -1  # -1 means entire battle
    was_used_this_battle: bool = False
    
    def is_active(self) -> bool:
        """Check if the meat effect is still active."""
        return self.turns_remaining != 0
    
    def get_bonus(self) -> float:
        """Get the current taming bonus."""
        return self.meat_type.bonus if self.is_active() else 0.0
    
    def consume_turn(self):
        """Consume a turn of the meat effect (if turn-limited)."""
        if self.turns_remaining > 0:
            self.turns_remaining -= 1


class MeatSystem:
    """
    Manages the DQM-style meat system for monster taming.
    Meat is used BEFORE taming attempts and affects ALL subsequent attempts.
    Implemented as Singleton to ensure single instance across the game.
    """
    
    _instance: Optional['MeatSystem'] = None
    
    def __new__(cls):
        """Singleton pattern for single instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the meat system."""
        if self._initialized:
            return
        
        self._initialized = True
        self.active_effect: Optional[MeatEffect] = None
        self.meat_inventory: Dict[MeatType, int] = {
            MeatType.NORMAL: 3,  # Start with 3 normal meat
            MeatType.SUPER: 1,   # Start with 1 super meat
            MeatType.DIVINE: 0   # Start with 0 divine meat
        }
        logger.info("Meat system initialized as singleton")
    
    def has_meat(self, meat_type: MeatType) -> bool:
        """Check if player has the specified meat type."""
        if meat_type == MeatType.NONE:
            return True  # Always can choose no meat
        return self.meat_inventory.get(meat_type, 0) > 0
    
    def get_available_meat(self) -> Dict[MeatType, int]:
        """Get all available meat types and quantities."""
        available = {MeatType.NONE: -1}  # Always have "no meat" option
        for meat_type, count in self.meat_inventory.items():
            if count > 0:
                available[meat_type] = count
        return available
    
    def use_meat(self, meat_type: MeatType, battle_state=None) -> Tuple[bool, str]:
        """
        Use meat to enhance taming chances for the battle.
        
        Args:
            meat_type: Type of meat to use
            battle_state: Current battle state (optional)
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Check if meat is already active
            if self.active_effect and self.active_effect.is_active():
                if self.active_effect.meat_type == meat_type:
                    return False, f"{meat_type.display_name} ist bereits aktiv!"
                elif self.active_effect.meat_type.bonus >= meat_type.bonus:
                    return False, f"Stärkeres Fleisch ({self.active_effect.meat_type.display_name}) ist bereits aktiv!"
            
            # Check availability
            if meat_type != MeatType.NONE and not self.has_meat(meat_type):
                return False, f"Kein {meat_type.display_name} vorhanden!"
            
            # Use the meat
            if meat_type != MeatType.NONE:
                self.meat_inventory[meat_type] -= 1
                self.active_effect = MeatEffect(
                    meat_type=meat_type,
                    turns_remaining=-1,  # Lasts entire battle
                    was_used_this_battle=True
                )
                
                message = f"{meat_type.display_name} wurde verwendet! Zähm-Chance +{int(meat_type.bonus * 100)}% für den gesamten Kampf!"
                logger.info(f"Used {meat_type.name}: {message}")
                
                # Add to battle log if available
                if battle_state and hasattr(battle_state, 'battle_log'):
                    battle_state.battle_log.append(message)
                
                return True, message
            else:
                # Choosing no meat
                self.active_effect = None
                return True, "Kein Fleisch verwendet."
                
        except Exception as e:
            logger.error(f"Error using meat: {str(e)}")
            return False, f"Fehler beim Verwenden von Fleisch: {str(e)}"
    
    def get_taming_bonus(self) -> float:
        """
        Get the current taming bonus from active meat.
        
        Returns:
            Bonus as a float (0.0 to 0.8)
        """
        if self.active_effect and self.active_effect.is_active():
            return self.active_effect.get_bonus()
        return 0.0
    
    def get_active_meat_name(self) -> str:
        """Get the name of currently active meat."""
        if self.active_effect and self.active_effect.is_active():
            return self.active_effect.meat_type.display_name
        return "Keins"
    
    def calculate_taming_chance(self, base_chance: float, monster_hp_percent: float, 
                               monster_rank: str, monster_status: Optional[str] = None) -> Dict[str, any]:
        """
        Calculate the final taming chance with all modifiers.
        
        Args:
            base_chance: Base taming chance (0.0 to 1.0)
            monster_hp_percent: Monster's current HP percentage (0.0 to 1.0)
            monster_rank: Monster's rank (F, E, D, C, B, A, S, SS, X)
            monster_status: Monster's status condition (optional)
            
        Returns:
            Dictionary with chance breakdown
        """
        modifiers = {}
        
        # Base chance
        modifiers['base'] = base_chance
        
        # HP bonus (lower HP = higher chance)
        hp_bonus = (1.0 - monster_hp_percent) * 0.3  # Max 30% at 0 HP
        modifiers['hp_bonus'] = hp_bonus
        
        # Meat bonus
        meat_bonus = self.get_taming_bonus()
        modifiers['meat_bonus'] = meat_bonus
        
        # Rank modifier
        rank_modifiers = {
            'F': 0.10,   # +10%
            'E': 0.05,   # +5%
            'D': 0.00,   # ±0%
            'C': -0.05,  # -5%
            'B': -0.10,  # -10%
            'A': -0.15,  # -15%
            'S': -0.20,  # -20%
            'SS': -0.25, # -25%
            'X': -0.30   # -30%
        }
        rank_bonus = rank_modifiers.get(monster_rank, 0.0)
        modifiers['rank_bonus'] = rank_bonus
        
        # Status modifier
        status_modifiers = {
            'sleep': 0.15,      # +15%
            'freeze': 0.10,     # +10%
            'paralysis': 0.10,  # +10%
            'confusion': 0.05,  # +5%
            'poison': 0.00,     # ±0%
            'burn': 0.00        # ±0%
        }
        status_bonus = 0.0
        if monster_status:
            status_bonus = status_modifiers.get(monster_status.lower(), 0.0)
        modifiers['status_bonus'] = status_bonus
        
        # Calculate final chance
        final_chance = base_chance + hp_bonus + meat_bonus + rank_bonus + status_bonus
        final_chance = max(0.05, min(0.95, final_chance))  # Clamp between 5% and 95%
        
        return {
            'final_chance': final_chance,
            'modifiers': modifiers,
            'meat_active': self.active_effect is not None,
            'meat_name': self.get_active_meat_name()
        }
    
    def reset_battle_effect(self):
        """Reset meat effect at the end of battle."""
        self.active_effect = None
        logger.info("Meat effects reset for new battle")
    
    def add_meat_to_inventory(self, meat_type: MeatType, quantity: int = 1):
        """Add meat to the inventory."""
        if meat_type != MeatType.NONE:
            self.meat_inventory[meat_type] = self.meat_inventory.get(meat_type, 0) + quantity
            logger.info(f"Added {quantity}x {meat_type.display_name} to inventory")
    
    def remove_meat_from_inventory(self, meat_type: MeatType, quantity: int = 1) -> bool:
        """
        Remove meat from inventory.
        
        Returns:
            True if successful, False if not enough meat
        """
        if meat_type == MeatType.NONE:
            return True
            
        current = self.meat_inventory.get(meat_type, 0)
        if current >= quantity:
            self.meat_inventory[meat_type] = current - quantity
            return True
        return False
    
    def get_inventory_display(self) -> str:
        """Get a formatted string of the meat inventory."""
        lines = ["Fleisch-Inventar:"]
        for meat_type, count in self.meat_inventory.items():
            if count > 0:
                lines.append(f"  {meat_type.display_name}: {count}x")
        
        if len(lines) == 1:
            lines.append("  (Kein Fleisch vorhanden)")
        
        return "\n".join(lines)
    
    def save_state(self) -> Dict:
        """Save the meat system state for saving."""
        return {
            'inventory': {meat_type.name: count for meat_type, count in self.meat_inventory.items()},
            'active_effect': {
                'meat_type': self.active_effect.meat_type.name,
                'turns_remaining': self.active_effect.turns_remaining,
                'was_used': self.active_effect.was_used_this_battle
            } if self.active_effect else None
        }
    
    def load_state(self, state: Dict):
        """Load the meat system state from save data."""
        try:
            # Load inventory
            if 'inventory' in state:
                for meat_name, count in state['inventory'].items():
                    try:
                        meat_type = MeatType[meat_name]
                        self.meat_inventory[meat_type] = count
                    except KeyError:
                        logger.warning(f"Unknown meat type in save: {meat_name}")
            
            # Load active effect
            if state.get('active_effect'):
                effect_data = state['active_effect']
                try:
                    meat_type = MeatType[effect_data['meat_type']]
                    self.active_effect = MeatEffect(
                        meat_type=meat_type,
                        turns_remaining=effect_data.get('turns_remaining', -1),
                        was_used_this_battle=effect_data.get('was_used', False)
                    )
                except KeyError:
                    logger.warning(f"Could not restore active meat effect")
                    
        except Exception as e:
            logger.error(f"Error loading meat system state: {str(e)}")


    # Item System Integration Methods
    def get_item_id_from_meat_type(self, meat_type: MeatType) -> Optional[str]:
        """Get item ID from meat type."""
        meat_to_item = {
            MeatType.NORMAL: 'fleisch',
            MeatType.SUPER: 'edelfleisch', 
            MeatType.DIVINE: 'goldfleisch'
        }
        return meat_to_item.get(meat_type)
    
    def get_meat_type_from_item_id(self, item_id: str) -> Optional[MeatType]:
        """Get meat type from item ID."""
        item_to_meat = {
            'fleisch': MeatType.NORMAL,
            'edelfleisch': MeatType.SUPER,
            'goldfleisch': MeatType.DIVINE,
            'lecker_fleisch': MeatType.SUPER,  # Alternative mapping
            'meat': MeatType.NORMAL,           # English fallback
            'super_meat': MeatType.SUPER,      # English fallback
            'divine_meat': MeatType.DIVINE     # English fallback
        }
        return item_to_meat.get(item_id)
    
    def is_meat_item(self, item_id: str) -> bool:
        """Check if an item is a meat item."""
        return self.get_meat_type_from_item_id(item_id) is not None
    
    def sync_with_item_inventory(self, item_inventory: Dict[str, int]):
        """
        Sync meat system inventory with item inventory.
        
        Args:
            item_inventory: The item inventory dict (item_id -> count)
        """
        try:
            # Reset meat inventory
            for meat_type in [MeatType.NORMAL, MeatType.SUPER, MeatType.DIVINE]:
                self.meat_inventory[meat_type] = 0
            
            # Add meat from items
            for item_id, count in item_inventory.items():
                meat_type = self.get_meat_type_from_item_id(item_id)
                if meat_type and meat_type != MeatType.NONE:
                    self.meat_inventory[meat_type] = count
                    logger.info(f"Synced {count}x {meat_type.display_name} from item {item_id}")
                    
        except Exception as e:
            logger.error(f"Error syncing meat inventory: {str(e)}")
    
    def consume_meat_item(self, item_id: str, item_inventory: Dict[str, int]) -> bool:
        """
        Consume a meat item from inventory when used.
        
        Args:
            item_id: The item ID to consume
            item_inventory: The item inventory dict
            
        Returns:
            True if successful, False otherwise
        """
        try:
            meat_type = self.get_meat_type_from_item_id(item_id)
            if not meat_type or meat_type == MeatType.NONE:
                return False
            
            # Check if item exists in inventory
            if item_inventory.get(item_id, 0) <= 0:
                return False
            
            # Remove from item inventory
            item_inventory[item_id] -= 1
            if item_inventory[item_id] <= 0:
                del item_inventory[item_id]
            
            # Sync with meat system
            self.sync_with_item_inventory(item_inventory)
            
            return True
            
        except Exception as e:
            logger.error(f"Error consuming meat item: {str(e)}")
            return False
    
    def add_meat_as_item(self, meat_type: MeatType, item_inventory: Dict[str, int], 
                         quantity: int = 1) -> bool:
        """
        Add meat to item inventory.
        
        Args:
            meat_type: Type of meat to add
            item_inventory: The item inventory dict
            quantity: Amount to add
            
        Returns:
            True if successful
        """
        try:
            item_id = self.get_item_id_from_meat_type(meat_type)
            if not item_id:
                return False
            
            # Add to inventory
            item_inventory[item_id] = item_inventory.get(item_id, 0) + quantity
            
            logger.info(f"Added {quantity}x {item_id} to inventory")
            return True
            
        except Exception as e:
            logger.error(f"Error adding meat as item: {str(e)}")
            return False
    
    def validate_meat_items(self, item_inventory: Dict[str, int]) -> Dict[str, Any]:
        """
        Validate meat items in inventory.
        
        Args:
            item_inventory: The item inventory dict
            
        Returns:
            Validation results
        """
        results = {
            'valid_meat_items': [],
            'invalid_meat_items': [],
            'total_meat_count': 0
        }
        
        for item_id, count in item_inventory.items():
            if self.is_meat_item(item_id):
                meat_type = self.get_meat_type_from_item_id(item_id)
                if meat_type:
                    results['valid_meat_items'].append({
                        'item_id': item_id,
                        'meat_type': meat_type.display_name,
                        'count': count,
                        'bonus': meat_type.bonus
                    })
                    results['total_meat_count'] += count
                else:
                    results['invalid_meat_items'].append(item_id)
        
        return results
    
    def apply_meat_effect_from_item(self, item_id: str, target: Optional[Any] = None, 
                                   battle_state: Optional[Any] = None) -> Optional[Dict[str, Any]]:
        """
        Apply meat effect for item system integration.
        
        Args:
            item_id: The meat item ID
            target: Target monster (optional)
            battle_state: Battle state (optional)
            
        Returns:
            Result dictionary with success, message, catch_chance
        """
        try:
            # Check if it's a meat item
            if not self.is_meat_item(item_id):
                return None
            
            # Get meat type
            meat_type = self.get_meat_type_from_item_id(item_id)
            if not meat_type:
                return None
            
            # If we have battle state, use the meat system
            if battle_state and hasattr(battle_state, 'meat_system'):
                meat_system = battle_state.meat_system
                success, message = meat_system.use_meat(meat_type, battle_state)
                
                return {
                    'success': success,
                    'message': message,
                    'catch_chance': meat_type.bonus,
                    'meat_type': meat_type.display_name
                }
            else:
                # Fallback for non-battle usage
                return {
                    'success': True,
                    'message': f"{meat_type.display_name} verwendet!",
                    'catch_chance': meat_type.bonus,
                    'meat_type': meat_type.display_name
                }
                
        except Exception as e:
            logger.error(f"Error applying meat effect: {str(e)}")
            return {
                'success': False,
                'message': f"Fehler beim Verwenden von {item_id}",
                'catch_chance': 0
            }


def get_meat_system() -> MeatSystem:
    """Get the singleton meat system instance."""
    return MeatSystem()


def handle_meat_item_use(item_data: Dict[str, Any], battle_state) -> Dict[str, Any]:
    """
    Handle the use of a meat item in battle.
    
    Args:
        item_data: Item data dictionary
        battle_state: Current battle state
        
    Returns:
        Result dictionary
    """
    try:
        item_id = item_data.get('id')
        
        # Get meat system
        meat_system = get_meat_system()
        
        # Check if it's a meat item
        if not meat_system.is_meat_item(item_id):
            return {'error': 'Not a meat item'}
        
        # Get meat type
        meat_type = meat_system.get_meat_type_from_item_id(item_id)
        if not meat_type:
            return {'error': 'Invalid meat type'}
        
        # Get meat system from battle state
        if not hasattr(battle_state, 'meat_system'):
            return {'error': 'No meat system in battle'}
        
        battle_meat_system = battle_state.meat_system
        
        # Use the meat
        success, message = battle_meat_system.use_meat(meat_type, battle_state)
        
        if success:
            # Consume from item inventory if available
            if hasattr(battle_state, 'player_inventory'):
                meat_system.consume_meat_item(
                    item_id, 
                    battle_state.player_inventory
                )
            
            return {
                'success': True,
                'message': message,
                'meat_type': meat_type.display_name,
                'bonus': meat_type.bonus,
                'enemy_gets_turn': True  # Important: enemy attacks after meat use
            }
        else:
            return {
                'success': False,
                'message': message
            }
            
    except Exception as e:
        logger.error(f"Error handling meat item use: {str(e)}")
        return {'error': str(e)}
