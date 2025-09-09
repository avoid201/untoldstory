"""
Item integration for meat system.
Links item database with meat system functionality.
"""

import logging
from typing import Dict, Optional, Any
from engine.systems.battle.meat_system import MeatSystem, MeatType

logger = logging.getLogger(__name__)


class MeatItemBridge:
    """
    Bridge between the item system and meat system.
    Maps item IDs to meat types and handles conversion.
    """
    
    # Map item IDs to meat types
    ITEM_TO_MEAT_MAP = {
        'fleisch': MeatType.NORMAL,
        'edelfleisch': MeatType.SUPER,
        'goldfleisch': MeatType.DIVINE,
        'lecker_fleisch': MeatType.SUPER,  # Alternative mapping
        'meat': MeatType.NORMAL,           # English fallback
        'super_meat': MeatType.SUPER,      # English fallback
        'divine_meat': MeatType.DIVINE     # English fallback
    }
    
    @classmethod
    def get_meat_type_from_item(cls, item_id: str) -> Optional[MeatType]:
        """
        Get meat type from item ID.
        
        Args:
            item_id: The item ID to convert
            
        Returns:
            MeatType or None if not a meat item
        """
        return cls.ITEM_TO_MEAT_MAP.get(item_id)
    
    @classmethod
    def is_meat_item(cls, item_id: str) -> bool:
        """Check if an item is a meat item."""
        return item_id in cls.ITEM_TO_MEAT_MAP
    
    @classmethod
    def get_item_id_from_meat(cls, meat_type: MeatType) -> Optional[str]:
        """
        Get item ID from meat type.
        
        Args:
            meat_type: The meat type to convert
            
        Returns:
            Item ID or None
        """
        meat_to_item = {
            MeatType.NORMAL: 'fleisch',
            MeatType.SUPER: 'edelfleisch', 
            MeatType.DIVINE: 'goldfleisch'
        }
        return meat_to_item.get(meat_type)
    
    @classmethod
    def sync_meat_inventory_with_items(cls, meat_system: MeatSystem, item_inventory: Dict[str, int]):
        """
        Sync meat system inventory with item inventory.
        
        Args:
            meat_system: The meat system to sync
            item_inventory: The item inventory dict (item_id -> count)
        """
        try:
            # Reset meat inventory
            for meat_type in [MeatType.NORMAL, MeatType.SUPER, MeatType.DIVINE]:
                meat_system.meat_inventory[meat_type] = 0
            
            # Add meat from items
            for item_id, count in item_inventory.items():
                meat_type = cls.get_meat_type_from_item(item_id)
                if meat_type and meat_type != MeatType.NONE:
                    meat_system.meat_inventory[meat_type] = count
                    logger.info(f"Synced {count}x {meat_type.display_name} from item {item_id}")
                    
        except Exception as e:
            logger.error(f"Error syncing meat inventory: {str(e)}")
    
    @classmethod
    def consume_meat_item(cls, item_id: str, item_inventory: Dict[str, int], 
                          meat_system: MeatSystem) -> bool:
        """
        Consume a meat item from inventory when used.
        
        Args:
            item_id: The item ID to consume
            item_inventory: The item inventory dict
            meat_system: The meat system
            
        Returns:
            True if successful, False otherwise
        """
        try:
            meat_type = cls.get_meat_type_from_item(item_id)
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
            cls.sync_meat_inventory_with_items(meat_system, item_inventory)
            
            return True
            
        except Exception as e:
            logger.error(f"Error consuming meat item: {str(e)}")
            return False
    
    @classmethod
    def add_meat_as_item(cls, meat_type: MeatType, item_inventory: Dict[str, int], 
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
            item_id = cls.get_item_id_from_meat(meat_type)
            if not item_id:
                return False
            
            # Add to inventory
            item_inventory[item_id] = item_inventory.get(item_id, 0) + quantity
            
            logger.info(f"Added {quantity}x {item_id} to inventory")
            return True
            
        except Exception as e:
            logger.error(f"Error adding meat as item: {str(e)}")
            return False
    
    @classmethod
    def validate_meat_items(cls, item_inventory: Dict[str, int]) -> Dict[str, Any]:
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
            if cls.is_meat_item(item_id):
                meat_type = cls.get_meat_type_from_item(item_id)
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
    
    @classmethod
    def apply_meat_effect(cls, item_id: str, target: Optional[Any] = None, 
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
            if not cls.is_meat_item(item_id):
                return None
            
            # Get meat type
            meat_type = cls.get_meat_type_from_item(item_id)
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
        
        # Check if it's a meat item
        if not MeatItemBridge.is_meat_item(item_id):
            return {'error': 'Not a meat item'}
        
        # Get meat type
        meat_type = MeatItemBridge.get_meat_type_from_item(item_id)
        if not meat_type:
            return {'error': 'Invalid meat type'}
        
        # Get meat system from battle state
        if not hasattr(battle_state, 'meat_system'):
            return {'error': 'No meat system in battle'}
        
        meat_system = battle_state.meat_system
        
        # Use the meat
        success, message = meat_system.use_meat(meat_type, battle_state)
        
        if success:
            # Consume from item inventory if available
            if hasattr(battle_state, 'player_inventory'):
                MeatItemBridge.consume_meat_item(
                    item_id, 
                    battle_state.player_inventory,
                    meat_system
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
