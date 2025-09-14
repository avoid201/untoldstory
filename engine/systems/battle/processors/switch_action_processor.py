"""
Switch Action Processor - Monster Switching Logic
===============================================
Handles monster switching actions in battle.
"""

import logging
from typing import Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from engine.systems.battle.battle_state import BattleState
    from engine.systems.battle.turn_logic import BattleAction, ActionType

from engine.systems.battle.events.event_types import EventType

logger = logging.getLogger(__name__)


class SwitchActionProcessor:
    """
    Handles monster switching actions.
    """
    
    def __init__(self, battle_state: 'BattleState'):
        """Initialize switch action processor."""
        self.state = battle_state
        logger.debug("SwitchActionProcessor initialized")
    
    def can_handle(self, action: 'BattleAction') -> bool:
        """Check if this processor can handle the action."""
        if hasattr(action, 'action_type'):
            return action.action_type == ActionType.SWITCH
        elif isinstance(action, dict):
            return action.get('action_type') == 'SWITCH'
        return False
    
    def execute(self, action: 'BattleAction') -> Dict[str, Any]:
        """Execute switch action."""
        try:
            if not self.can_handle(action):
                return self.create_error_result(
                    'switch',
                    'Cannot handle this action type'
                )
            
            # Get switch target
            switch_to = action.switch_to if hasattr(action, 'switch_to') else action.get('switch_to')
            if not switch_to:
                return self.create_error_result(
                    'switch',
                    'No switch target specified'
                )
            
            # Check if switch target is valid
            if not self._is_valid_switch_target(switch_to):
                return self.create_error_result(
                    'switch',
                    'Invalid switch target'
                )
            
            # Perform switch
            old_monster = self.state.player_active
            self.state.player_active = switch_to
            
            # Emit switch event
            self._emit_switch_event(old_monster, switch_to)
            
            return self.create_success_result(
                'switch',
                f'Switched to {switch_to.name}',
                switched_from=old_monster,
                switched_to=switch_to
            )
            
        except Exception as e:
            logger.error(f"Error executing switch action: {e}")
            return self.create_error_result(
                'switch',
                str(e)
            )
    
    def _is_valid_switch_target(self, switch_to) -> bool:
        """Check if switch target is valid."""
        try:
            if not switch_to:
                return False
            
            # Check if monster is in player team
            if not any(monster == switch_to for monster in self.state.player_team):
                return False
            
            # Check if monster is not fainted
            if hasattr(switch_to, 'current_hp') and switch_to.current_hp <= 0:
                return False
            
            # Check if monster is not already active
            if switch_to == self.state.player_active:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating switch target: {e}")
            return False
    
    def _emit_switch_event(self, old_monster, new_monster) -> None:
        """Emit monster switch event."""
        try:
            if hasattr(self.state, 'event_processor') and self.state.event_processor:
                self.state.event_processor.emit_event(
                    EventType.MONSTER_SWITCH,
                    {
                        'player_active': new_monster,
                        'switched_from': old_monster,
                        'switched_to': new_monster
                    }
                )
                logger.debug(f"Monster switch event emitted: {old_monster.name} -> {new_monster.name}")
        except Exception as e:
            logger.warning(f"Failed to emit switch event: {e}")
    
    def create_success_result(self, action_type: str, message: str, **kwargs) -> Dict[str, Any]:
        """Create success result."""
        return {
            'success': True,
            'action_type': action_type,
            'message': message,
            **kwargs
        }
    
    def create_error_result(self, action_type: str, error: str) -> Dict[str, Any]:
        """Create error result."""
        return {
            'success': False,
            'action_type': action_type,
            'error': error
        }
