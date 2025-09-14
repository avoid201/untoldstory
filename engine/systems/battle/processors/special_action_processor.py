"""
Special action processing - max 200 lines
Handles Tame, Flee, Scout, and Switch actions with robust error recovery
"""

import logging
import random
from typing import Dict, Any, TYPE_CHECKING

from engine.systems.battle.processors.action_processor_base import ActionProcessorBase
from engine.systems.battle.turn_logic import BattleAction, ActionType
from engine.systems.battle.event_processor import EventType

if TYPE_CHECKING:
    from engine.systems.battle.battle_state import BattleState
    from engine.systems.monster_instance import MonsterInstance

logger = logging.getLogger(__name__)


class SpecialActionProcessor(ActionProcessorBase):
    """Handles special actions: Tame, Flee, Scout, Switch"""
    
    def can_handle(self, action: BattleAction) -> bool:
        """Check if this processor can handle special actions"""
        # Handle both BattleAction objects and dictionaries
        if hasattr(action, 'action_type'):
            return action.action_type in [ActionType.TAME, ActionType.FLEE, ActionType.SCOUT, ActionType.SWITCH]
        elif isinstance(action, dict):
            action_type = action.get('action_type')
            return action_type in ['TAME', 'FLEE', 'SCOUT', 'SWITCH']
        return False
    
    def execute(self, action: BattleAction) -> Dict[str, Any]:
        """Execute special action with error recovery"""
        try:
            # Handle both BattleAction objects and dictionaries
            if hasattr(action, 'action_type'):
                action_type = action.action_type
            elif isinstance(action, dict):
                action_type_str = action.get('action_type', 'TAME')
                action_type = ActionType.from_string(action_type_str)
            else:
                action_type = ActionType.TAME
            
            if action_type == ActionType.TAME:
                return self._execute_tame(action)
            elif action_type == ActionType.FLEE:
                return self._execute_flee(action)
            elif action_type == ActionType.SCOUT:
                return self._execute_scout(action)
            elif action_type == ActionType.SWITCH:
                return self._execute_switch(action)
            else:
                return self.create_error_result(
                    str(action_type).lower(),
                    f'Unknown special action type: {action_type}'
                )
        except Exception as e:
            logger.error(f"Error executing special action: {e}")
            return self.create_error_result(
                str(action_type).lower(),
                str(e)
            )
    
    def _execute_tame(self, action: BattleAction) -> Dict[str, Any]:
        """Execute tame action with MeatSystem integration and robust error recovery"""
        try:
            # Emit tame announcement event
            self._emit_action_announcement(action, f"{action.actor.name} versucht {action.target.name} zu zähmen!")
            
            # Get MeatSystem instance with fallback
            meat_system = self._get_meat_system()
            
            # Check if taming is allowed
            if not getattr(self.state, 'can_catch', False):
                return self.create_error_result(
                    'tame',
                    'Taming not allowed in this battle',
                    success=False
                )
            
            if not action.target or getattr(action.target, 'is_fainted', False) or action.target.current_hp <= 0:
                return self.create_error_result(
                    'tame',
                    'Target not available for taming',
                    success=False
                )
            
            # Calculate taming chance using MeatSystem
            base_chance = 0.3  # 30% base chance
            hp_percent = action.target.current_hp / action.target.max_hp
            monster_rank = getattr(action.target, 'rank', 'D')  # Default to D rank
            monster_status = None
            
            # Get status condition if available
            if hasattr(action.target, 'status_manager'):
                monster_status = action.target.status_manager.get_active_status()
            
            # Use MeatSystem to calculate final taming chance
            taming_result = meat_system.calculate_taming_chance(
                base_chance=base_chance,
                monster_hp_percent=hp_percent,
                monster_rank=monster_rank,
                monster_status=monster_status
            )
            
            final_chance = taming_result['final_chance']
            success = random.random() < final_chance
            
            # Log taming attempt
            logger.info(f"Taming attempt: {action.target.name} - Chance: {final_chance:.2%} - Success: {success}")
            
            if success:
                # Successful taming
                self.state.caught_monster = action.target
                message = f"{action.target.name} wurde erfolgreich gezähmt!"
                
                # Add meat bonus info to message if applicable
                if taming_result['meat_active']:
                    message += f" (Fleisch-Bonus: {taming_result['meat_name']})"
                
                return self.create_success_result(
                    'tame',
                    message,
                    success=True,
                    caught_monster=action.target,
                    taming_chance=final_chance,
                    meat_bonus=taming_result['modifiers']['meat_bonus']
                )
            else:
                # Failed taming
                message = f"Zähmung von {action.target.name} fehlgeschlagen! (Chance war {final_chance:.1%})"
                
                return self.create_success_result(
                    'tame',
                    message,
                    success=False,
                    taming_chance=final_chance,
                    meat_bonus=taming_result['modifiers']['meat_bonus']
                )
                
        except Exception as e:
            logger.error(f"Error executing tame: {e}")
            return self.create_error_result(
                'tame',
                str(e),
                success=False
            )
    
    def _execute_flee(self, action: BattleAction) -> Dict[str, Any]:
        """Execute flee action with error recovery"""
        try:
            # This would delegate to the flee calculation system
            # For now, return a placeholder result
            return self.create_success_result(
                'flee',
                'Successfully fled',
                actor=action.actor,
                success=True
            )
        except Exception as e:
            logger.error(f"Error executing flee: {e}")
            return self.create_error_result('flee', str(e))
    
    def _execute_scout(self, action: BattleAction) -> Dict[str, Any]:
        """Execute scout action with error recovery"""
        try:
            # Emit scout announcement event
            self._emit_action_announcement(action, f"{action.actor.name} späht {action.target.name} aus!")
            
            # This would handle monster scouting
            # For now, return a placeholder result
            return self.create_success_result(
                'scout',
                'Scouting successful',
                actor=action.actor,
                target=action.target,
                success=True
            )
        except Exception as e:
            logger.error(f"Error executing scout: {e}")
            return self.create_error_result('scout', str(e))
    
    def _execute_switch(self, action: BattleAction) -> Dict[str, Any]:
        """Execute switch action with error recovery"""
        try:
            # Emit switch announcement event
            self._emit_action_announcement(action, f"{action.actor.name} wechselt zu {action.switch_to.name}!")
            
            # This would handle monster switching
            # For now, return a placeholder result
            return self.create_success_result(
                'switch',
                'Switch successful',
                actor=action.actor,
                old_monster=action.actor,
                new_monster=action.switch_to,
                success=True
            )
        except Exception as e:
            logger.error(f"Error executing switch: {e}")
            return self.create_error_result('switch', str(e))
    
    
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
