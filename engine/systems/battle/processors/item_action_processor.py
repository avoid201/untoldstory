"""
Item action processing - max 150 lines
Handles Item and Meat usage actions with robust error recovery
"""

import logging
from typing import Dict, Any, TYPE_CHECKING

from engine.systems.battle.processors.action_processor_base import ActionProcessorBase
from engine.systems.battle.turn_logic import BattleAction, ActionType
from engine.systems.battle.event_processor import EventType

if TYPE_CHECKING:
    from engine.systems.battle.battle_state import BattleState
    from engine.systems.monster_instance import MonsterInstance

logger = logging.getLogger(__name__)


class ItemActionProcessor(ActionProcessorBase):
    """Handles item and meat usage actions"""
    
    def can_handle(self, action: BattleAction) -> bool:
        """Check if this processor can handle item actions"""
        # Handle both BattleAction objects and dictionaries
        if hasattr(action, 'action_type'):
            return action.action_type in [ActionType.ITEM, ActionType.USE_MEAT]
        elif isinstance(action, dict):
            action_type = action.get('action_type')
            return action_type in ['ITEM', 'USE_MEAT']
        return False
    
    def execute(self, action: BattleAction) -> Dict[str, Any]:
        """Execute item action with error recovery"""
        try:
            # Handle both BattleAction objects and dictionaries
            if hasattr(action, 'action_type'):
                action_type = action.action_type
            elif isinstance(action, dict):
                action_type_str = action.get('action_type', 'ITEM')
                action_type = ActionType.from_string(action_type_str)
            else:
                action_type = ActionType.ITEM
            
            if action_type == ActionType.ITEM:
                return self._execute_item(action)
            elif action_type == ActionType.USE_MEAT:
                return self._execute_use_meat(action)
            else:
                return self.create_error_result(
                    str(action_type).lower(),
                    f'Unknown item action type: {action_type}'
                )
        except Exception as e:
            logger.error(f"Error executing item action: {e}")
            return self.create_error_result(
                str(action_type).lower(),
                str(e)
            )
    
    def _execute_item(self, action: BattleAction) -> Dict[str, Any]:
        """Execute item action with error recovery"""
        try:
            # Emit item usage announcement event
            item_name = action.item.name if hasattr(action, 'item') and action.item else "Item"
            self._emit_action_announcement(action, f"{action.actor.name} verwendet {item_name}!")
            
            # Get game instance (via battle_state) and remove item
            if hasattr(self.state, 'game') and hasattr(self.state.game, 'inventory'):
                success = self.state.game.inventory.remove_item(action.item_id, 1)
                if not success:
                    return self.create_error_result(
                        'item',
                        'Item not available in inventory',
                        success=False
                    )
            else:
                logger.warning("No inventory system available, skipping item removal")
            
            # Check if this is a meat item for taming
            if self._is_meat_item(action.item_id):
                return self._execute_meat_item(action)
            
            # This would delegate to the item system
            # For now, return a placeholder result
            return self.create_success_result(
                'item',
                'Item used successfully',
                actor=action.actor,
                target=action.target,
                item=action.item,
                success=True
            )
            
        except Exception as e:
            logger.error(f"Error executing item: {e}")
            return self.create_error_result('item', str(e), success=False)
    
    def _execute_use_meat(self, action: BattleAction) -> Dict[str, Any]:
        """Execute use meat action with MeatSystem integration and robust error recovery"""
        try:
            # Emit meat usage announcement event
            meat_name = action.meat_type.name if action.meat_type else "Fleisch"
            self._emit_action_announcement(action, f"{action.actor.name} verwendet {meat_name}!")
            
            # Validate action
            if not action.meat_type:
                return self.create_error_result(
                    'use_meat',
                    'Missing meat_type',
                    success=False
                )
            
            # Get MeatSystem instance with fallback
            meat_system = self._get_meat_system()
            
            # Use meat through MeatSystem
            success, message = meat_system.use_meat(
                meat_type=action.meat_type,
                battle_state=self.state
            )
            
            # Log meat usage
            logger.info(f"Meat usage attempt: {action.meat_type.name} - Success: {success}")
            
            # Get meat bonus safely
            meat_bonus = 0.0
            try:
                meat_bonus = meat_system.get_taming_bonus() if success else 0.0
            except Exception as e:
                logger.warning(f"Could not get meat bonus: {e}")
                meat_bonus = 0.0
            
            return self.create_success_result(
                'use_meat',
                message,
                actor=action.actor,
                meat_type=action.meat_type,
                success=success,
                meat_bonus=meat_bonus
            )
            
        except Exception as e:
            logger.error(f"Error executing use meat: {e}")
            return self.create_error_result(
                'use_meat',
                str(e),
                success=False
            )
    
    
    def _is_meat_item(self, item_id: str) -> bool:
        """Check if item is a meat item for taming."""
        meat_items = ['fleisch', 'lecker_fleisch', 'edelfleisch', 'goldfleisch']
        return item_id in meat_items
    
    def _execute_meat_item(self, action: BattleAction) -> Dict[str, Any]:
        """Execute meat item usage - sets persistent meat effect for battle."""
        try:
            # Get meat bonus based on item type
            meat_bonus = self._get_meat_bonus(action.item_id)
            meat_bonus_percent = meat_bonus / 100.0  # Convert to decimal
            
            # Set persistent meat effect in battle state
            self.state.active_meat_effect = action.item_id
            self.state.meat_bonus = meat_bonus_percent
            
            # Create success message
            meat_name = action.item.name if hasattr(action, 'item') and action.item else action.item_id
            message = f"{meat_name} wurde verwendet! Zähm-Bonus: +{meat_bonus}% für den Rest des Kampfes!"
            
            return self.create_success_result(
                'meat_item',
                message,
                actor=action.actor,
                meat_type=action.item_id,
                meat_bonus=meat_bonus_percent,
                success=True,
                persistent_effect=True
            )
            
        except Exception as e:
            logger.error(f"Error executing meat item: {e}")
            return self.create_error_result('meat_item', str(e), success=False)
    
    def _get_meat_bonus(self, item_id: str) -> int:
        """Get meat bonus based on item type."""
        meat_bonuses = {
            'fleisch': 20,
            'lecker_fleisch': 30,
            'edelfleisch': 40,
            'goldfleisch': 80
        }
        return meat_bonuses.get(item_id, 0)
    
    
    def _emit_action_announcement(self, action: BattleAction, message: str) -> None:
        """Emit action announcement event"""
        try:
            if hasattr(self.state, 'event_processor') and self.state.event_processor:
                self.state.event_processor.emit_event(
                    EventType.MESSAGE_SHOW,
                    {'message': message, 'duration': 1.5}
                )
        except Exception as e:
            logger.warning(f"Failed to emit action announcement: {e}")
