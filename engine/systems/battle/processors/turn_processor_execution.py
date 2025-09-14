"""
Turn Processor Execution - Action Sequencer for Sequential Battle Actions
=======================================================================
Action-Sequenz-Controller für sequenzielle Battle-Actions mit Message-Bestätigung.
DQM × Pokémon Hybrid System mit Speed-basierter Turn-Order.
"""

import logging
import random
from typing import Dict, Any, List, Tuple, Optional, TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from engine.systems.battle.battle_state import BattleState
    from engine.systems.monster_instance import MonsterInstance
    from engine.systems.battle.turn_logic import BattleAction, ActionType
    from engine.systems.battle.event_processor import EventProcessor

from engine.systems.battle.events.event_types import EventType

logger = logging.getLogger(__name__)


class ActionSequencerState(Enum):
    """Action Sequencer State Machine."""
    IDLE = "idle"
    EXECUTING = "executing"
    WAIT_FOR_INPUT = "wait_for_input"
    TURN_END = "turn_end"


class ActionSequencer:
    """
    Action-Sequenz-Controller für sequenzielle Battle-Actions.
    
    Implementiert DQM-Formel: Speed + Random(0-255) für Turn-Order.
    Actions werden nacheinander ausgeführt mit Message-Bestätigung.
    """
    
    def __init__(self, battle_state: 'BattleState' = None):
        """Initialize Action Sequencer."""
        self.battle_state = battle_state
        self.state = ActionSequencerState.IDLE
        self.action_queue: List['BattleAction'] = []
        self.current_action_index = 0
        self.turn_results = {}
        
        # Action Processor Integration
        self.action_processor = None
        
        logger.info("ActionSequencer initialized")
    
    def set_action_processor(self, action_processor) -> None:
        """Set the action processor for this sequencer."""
        self.action_processor = action_processor
        logger.info("Action processor set for sequencer")
    
    def execute_turn(self, actions: List['BattleAction']) -> Dict[str, Any]:
        """
        Execute a complete turn with sequential action processing.
        
        DQM-Formel: Speed + Random(0-255) für Turn-Order
        Actions werden nacheinander ausgeführt mit Message-Bestätigung.
        
        Args:
            actions: List of battle actions to execute
            
        Returns:
            Dictionary with execution results
        """
        try:
            if not actions:
                return {'success': False, 'message': 'No actions to execute'}
            
            logger.info(f"🎯 ActionSequencer: Starting turn with {len(actions)} actions")
            
            # Reset state
            self.state = ActionSequencerState.EXECUTING
            self.current_action_index = 0
            self.turn_results = {
                'success': True,
                'actions_executed': 0,
                'actions_failed': 0,
                'turn_events': [],
                'damage_dealt': 0,
                'monsters_fainted': 0,
                'battle_ended': False,
                'battle_result': None
            }
            
            # DQM-Formel: Speed + Random(0-255) für Turn-Order
            sorted_actions = self._calculate_turn_order(actions)
            self.action_queue = sorted_actions
            
            logger.info(f"🎯 Turn order calculated: {[f'{action.actor.name} ({action.action_type.name})' for action in sorted_actions]}")
            
            # Emit TURN_START event
            self._emit_event(EventType.TURN_START, {
                'turn_count': getattr(self.battle_state, 'turn_count', 0),
                'actions': [{'type': action.action_type.name, 'actor': action.actor.name} for action in sorted_actions]
            })
            
            # Process first action
            return self.process_next()
            
        except Exception as e:
            logger.error(f"Error executing turn: {e}")
            self.state = ActionSequencerState.IDLE
            return {'success': False, 'message': f'Turn execution error: {e}'}
    
    def process_next(self) -> Dict[str, Any]:
        """
        Process the next action in the queue.
        
        Returns:
            Dictionary with processing results
        """
        try:
            if self.state != ActionSequencerState.EXECUTING:
                return {'success': False, 'message': 'Sequencer not in executing state'}
            
            if self.current_action_index >= len(self.action_queue):
                # All actions processed, end turn
                return self._end_turn()
            
            action = self.action_queue[self.current_action_index]
            logger.info(f"🎯 Processing action {self.current_action_index + 1}/{len(self.action_queue)}: {action.actor.name} uses {action.action_type.name}")
            
            # Check if actor can act
            if not self._can_actor_act(action.actor):
                logger.warning(f"Actor {action.actor.name} cannot act, skipping action")
                self.current_action_index += 1
                return self.process_next()
            
            # Emit ACTION_ANNOUNCE event (Message-Bestätigung erforderlich)
            self._emit_action_message(action)
            
            # Set state to wait for input
            self.state = ActionSequencerState.WAIT_FOR_INPUT
            
            return {
                'success': True,
                'message': 'Waiting for message confirmation',
                'action_index': self.current_action_index,
                'total_actions': len(self.action_queue),
                'current_action': action,
                'state': self.state.value
            }
            
        except Exception as e:
            logger.error(f"Error processing next action: {e}")
            return {'success': False, 'message': f'Action processing error: {e}'}
    
    def confirm_message_and_execute(self) -> Dict[str, Any]:
        """
        Confirm message and execute the current action.
        Called after MESSAGE_SHOW event is confirmed by UI.
        
        Returns:
            Dictionary with execution results
        """
        try:
            if self.state != ActionSequencerState.WAIT_FOR_INPUT:
                return {'success': False, 'message': 'Sequencer not waiting for input'}
            
            if self.current_action_index >= len(self.action_queue):
                return {'success': False, 'message': 'No action to execute'}
            
            action = self.action_queue[self.current_action_index]
            
            # Emit ACTION_START event
            self._emit_event(EventType.ACTION_START, {
                'action': action.action_type.name,
                'actor': action.actor.name,
                'target': action.target.name if action.target else None
            })
            
            # Execute action
            action_result = self._execute_action(action)
            
            # Emit ACTION_END event
            self._emit_event(EventType.ACTION_END, {
                'action': action.action_type.name,
                'actor': action.actor.name,
                'success': action_result.get('success', False),
                'result': action_result
            })
            
            # Update turn results
            if action_result.get('success', False):
                self.turn_results['actions_executed'] += 1
                self.turn_results['turn_events'].extend(action_result.get('events', []))
                self.turn_results['damage_dealt'] += action_result.get('damage_dealt', 0)
                self.turn_results['monsters_fainted'] += action_result.get('monsters_fainted', 0)
                logger.info(f"✅ Action {self.current_action_index + 1} executed successfully")
            else:
                self.turn_results['actions_failed'] += 1
                logger.warning(f"❌ Action execution failed: {action_result.get('message', 'Unknown error')}")
            
            # Check if battle should end after this action
            battle_end_result = self._check_battle_end_after_action()
            if battle_end_result and battle_end_result.get('battle_ended'):
                logger.info(f"🏁 Battle ended during action execution! Result: {battle_end_result.get('result')}")
                self.turn_results['battle_ended'] = True
                self.turn_results['battle_result'] = battle_end_result.get('result')
                
                # Emit BATTLE_END event
                self._emit_event(EventType.BATTLE_END, {
                    'result': battle_end_result.get('result'),
                    'turn_count': getattr(self.battle_state, 'turn_count', 0)
                })
                
                self.state = ActionSequencerState.TURN_END
                return self.turn_results
            
            # Move to next action
            self.current_action_index += 1
            self.state = ActionSequencerState.EXECUTING
            
            # Process next action or end turn
            if self.current_action_index >= len(self.action_queue):
                return self._end_turn()
            else:
                return self.process_next()
            
        except Exception as e:
            logger.error(f"Error confirming message and executing action: {e}")
            return {'success': False, 'message': f'Action execution error: {e}'}
    
    def _calculate_turn_order(self, actions: List['BattleAction']) -> List['BattleAction']:
        """
        Calculate turn order using DQM formula: Speed + Random(0-255).
        
        Args:
            actions: List of actions to sort
            
        Returns:
            Sorted list of actions by turn order
        """
        try:
            def get_initiative(action):
                """Calculate initiative for action using DQM formula."""
                if not action.actor:
                    return 0
                
                # DQM-Formel: Speed + Random(0-255)
                base_speed = getattr(action.actor, 'current_stats', {}).get('spd', 0)
                random_bonus = random.randint(0, 255)
                initiative = base_speed + random_bonus
                
                # Status-Effekte berücksichtigen
                if hasattr(action.actor, 'status') and action.actor.status:
                    status_name = getattr(action.actor.status, 'name', '')
                    if status_name == 'PARALYSIS':
                        initiative = int(initiative * 0.5)
                
                # Stat-Stage Modifikatoren
                if hasattr(action.actor, 'stat_stages') and action.actor.stat_stages:
                    spd_stage = action.actor.stat_stages.get('spd', 0)
                    if spd_stage > 0:
                        multiplier = (2 + spd_stage) / 2
                    else:
                        multiplier = 2 / (2 - spd_stage)
                    initiative = int(initiative * multiplier)
                
                return initiative
            
            # Sort by initiative (descending)
            sorted_actions = sorted(actions, key=get_initiative, reverse=True)
            
            logger.info(f"🎯 Turn order calculated:")
            for i, action in enumerate(sorted_actions):
                initiative = get_initiative(action)
                logger.info(f"  {i+1}. {action.actor.name} ({action.action_type.name}) - Initiative: {initiative}")
            
            return sorted_actions
            
        except Exception as e:
            logger.error(f"Error calculating turn order: {e}")
            return actions
    
    def _emit_action_message(self, action: 'BattleAction') -> None:
        """Emit action message event for UI display."""
        try:
            message = f"{action.actor.name} setzt {action.move.name if action.move else action.action_type.name} ein!"
            
            self._emit_event(EventType.MESSAGE_SHOW, {
                'message': message,
                'duration': 1.5,
                'blocking': True  # Requires user confirmation
            })
            
        except Exception as e:
            logger.error(f"Error emitting action message: {e}")
    
    def _execute_action(self, action: 'BattleAction') -> Dict[str, Any]:
        """Execute a single action using the action processor."""
        try:
            if not self.action_processor:
                return {'success': False, 'message': 'No action processor available'}
            
            return self.action_processor.execute_action(action)
            
        except Exception as e:
            logger.error(f"Error executing action: {e}")
            return {'success': False, 'message': f'Action execution error: {e}'}
    
    def _can_actor_act(self, actor: 'MonsterInstance') -> bool:
        """Check if actor can perform actions."""
        try:
            if not actor:
                return False
            
            # Check if fainted
            if hasattr(actor, 'current_hp') and actor.current_hp <= 0:
                return False
            
            # Check status effects that prevent action
            if hasattr(actor, 'status') and actor.status:
                status_name = getattr(actor.status, 'name', '')
                if status_name in ['SLEEP', 'FREEZE', 'FLINCH']:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking if actor can act: {e}")
            return False
    
    def _check_battle_end_after_action(self) -> Dict[str, Any]:
        """Check if battle should end after an action."""
        try:
            if not self.battle_state:
                return {'battle_ended': False}
            
            # Use consolidated battle end detection
            from ..battle_end_detection import BattleEndDetection
            battle_end_info = BattleEndDetection.check_and_handle_battle_end(self.battle_state)
            
            # Convert to expected format
            if battle_end_info.get('battle_ended', False):
                return {
                    'battle_ended': True,
                    'result': battle_end_info.get('result'),
                    'reason': battle_end_info.get('reason', 'Unknown')
                }
            else:
                return {'battle_ended': False}
            
        except Exception as e:
            logger.error(f"Error checking battle end after action: {e}")
            return {'battle_ended': False}
    
    def _end_turn(self) -> Dict[str, Any]:
        """End the current turn and return results."""
        try:
            logger.info(f"🏁 Turn ended: {self.turn_results['actions_executed']} actions executed, {self.turn_results['actions_failed']} failed")
            
            # Emit TURN_END event
            self._emit_event(EventType.TURN_END, {
                'turn_count': getattr(self.battle_state, 'turn_count', 0),
                'actions_executed': self.turn_results['actions_executed'],
                'actions_failed': self.turn_results['actions_failed'],
                'battle_ended': self.turn_results['battle_ended']
            })
            
            # Reset state
            self.state = ActionSequencerState.IDLE
            self.action_queue.clear()
            self.current_action_index = 0
            
            return self.turn_results
            
        except Exception as e:
            logger.error(f"Error ending turn: {e}")
            return {'success': False, 'message': f'Turn end error: {e}'}
    
    def _emit_event(self, event_type: EventType, data: Dict[str, Any]) -> None:
        """Emit event through battle state event processor."""
        try:
            if hasattr(self.battle_state, 'event_processor') and self.battle_state.event_processor:
                self.battle_state.event_processor.emit_event(event_type, data)
        except Exception as e:
            logger.warning(f"Failed to emit {event_type.name} event: {e}")
    
    def get_current_state(self) -> Dict[str, Any]:
        """Get current sequencer state."""
        return {
            'state': self.state.value,
            'current_action_index': self.current_action_index,
            'total_actions': len(self.action_queue),
            'actions_executed': self.turn_results.get('actions_executed', 0),
            'actions_failed': self.turn_results.get('actions_failed', 0)
        }
    
    def reset(self) -> None:
        """Reset sequencer to idle state."""
        self.state = ActionSequencerState.IDLE
        self.action_queue.clear()
        self.current_action_index = 0
        self.turn_results = {}
        logger.info("ActionSequencer reset")


# Import core components for backward compatibility
from .turn_processor_execution_core import TurnProcessorExecutionCore
from .turn_processor_execution_events import TurnProcessorExecutionEvents

# Re-export main classes
__all__ = [
    'ActionSequencer',
    'ActionSequencerState',
    'TurnProcessorExecutionCore',
    'TurnProcessorExecutionEvents'
]

# Create alias for backward compatibility
TurnProcessorExecution = TurnProcessorExecutionCore
