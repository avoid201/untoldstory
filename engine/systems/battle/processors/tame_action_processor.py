"""
Tame action processing - max 150 lines
Handles taming actions with DQM-style mechanics and meat effects
"""

import logging
from typing import Dict, Any, TYPE_CHECKING
import random

from engine.systems.battle.processors.action_processor_base import ActionProcessorBase
from engine.systems.battle.turn_logic import BattleAction, ActionType
from engine.systems.battle.event_processor import EventType
from engine.systems.taming import attempt_tame, TameResult

if TYPE_CHECKING:
    from engine.systems.battle.battle_state import BattleState
    from engine.systems.monster_instance import MonsterInstance

logger = logging.getLogger(__name__)


class TameActionProcessor(ActionProcessorBase):
    """Handles taming actions with DQM-style mechanics"""
    
    def can_handle(self, action: BattleAction) -> bool:
        """Check if this processor can handle tame actions"""
        # Handle both BattleAction objects and dictionaries
        if hasattr(action, 'action_type'):
            return action.action_type == ActionType.TAME
        elif isinstance(action, dict):
            action_type = action.get('action_type')
            return action_type == 'TAME' or action_type == 'tame'
        elif isinstance(action, str):
            return action == 'tame' or action == 'TAME'
        return False
    
    def execute(self, action: BattleAction) -> Dict[str, Any]:
        """Execute tame action with DQM-style mechanics"""
        try:
            # Handle both BattleAction objects and dictionaries
            if hasattr(action, 'action_type'):
                actor = action.actor
                target = action.target
                meat_bonus = getattr(action, 'meat_bonus', 0.0)
                meat_type = getattr(action, 'meat_type', None)
            elif isinstance(action, dict):
                actor = action.get('actor')
                target = action.get('target')
                meat_bonus = action.get('meat_bonus', 0.0)
                meat_type = action.get('meat_type', None)
            else:
                return self.create_error_result('tame', 'Invalid action format')
            
            # Validate action
            if not actor or not target:
                return self.create_error_result(
                    'tame',
                    'Missing actor or target for taming',
                    success=False
                )
            
            # Check if target is wild
            if not getattr(target, 'is_wild', True):
                return self.create_error_result(
                    'tame',
                    'Dieses Monster kann nicht gezähmt werden!',
                    success=False
                )
            
            # Emit taming attempt announcement
            meat_info = f" mit {meat_type} (+{int(meat_bonus * 100)}%)" if meat_type else ""
            self._emit_action_announcement(action, f"{actor.name} versucht {target.name} zu zähmen{meat_info}!")
            
            # Use the existing taming system
            result, chance, message = attempt_tame(
                target=target,
                player_team=self.state.player_team,
                battle_state=self.state,
                item_used=meat_type,
                show_chance=True
            )
            
            # Apply meat bonus to the chance if meat was used
            if meat_type and meat_bonus > 0:
                # The taming system will handle the meat bonus internally
                # We just need to make sure it's passed correctly
                pass
            
            # Handle result
            if result == TameResult.SUCCESS:
                return self.create_success_result(
                    'tame',
                    message,
                    actor=actor,
                    target=target,
                    success=True,
                    taming_success=True,
                    final_chance=chance
                )
            elif result == TameResult.FAILED:
                return self.create_success_result(
                    'tame',
                    message,
                    actor=actor,
                    target=target,
                    success=True,
                    taming_success=False,
                    final_chance=chance
                )
            elif result == TameResult.IRRITATED:
                return self.create_error_result(
                    'tame',
                    message,
                    success=False
                )
            elif result == TameResult.INVALID:
                return self.create_error_result(
                    'tame',
                    message,
                    success=False
                )
            else:
                return self.create_error_result(
                    'tame',
                    f'Unknown taming result: {result}',
                    success=False
                )
                
        except Exception as e:
            logger.error(f"Error executing tame action: {e}")
            return self.create_error_result('tame', str(e), success=False)
    
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
