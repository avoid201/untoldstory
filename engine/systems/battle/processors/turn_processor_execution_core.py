"""
Turn Processor Execution Core - Core turn execution logic
========================================================
Core turn execution and action processing logic.
"""

import logging
import time
from typing import Dict, Any, List, Tuple, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from engine.systems.battle.battle_state import BattleState
    from engine.systems.monster_instance import MonsterInstance
    from engine.systems.battle.turn_logic import BattleAction, ActionType
    from engine.systems.battle.event_processor import EventProcessor

from engine.systems.battle.events.event_types import EventType

logger = logging.getLogger(__name__)


class TurnProcessorExecutionCore:
    """
    Core turn execution logic.
    Handles execution of battle actions and turn processing.
    """
    
    def __init__(self, battle_state: 'BattleState' = None):
        """Initialize turn execution processor."""
        self.battle_state = battle_state
        self.action_processor = None  # Will be set by set_action_processor
        
    def set_action_processor(self, action_processor) -> None:
        """Set the action processor for this turn processor."""
        self.action_processor = action_processor
        self.action_processors = {}
        self._setup_action_processors()
        logger.info("TurnProcessorExecutionCore initialized")
    
    def _setup_action_processors(self):
        """Setup action processors for different action types."""
        try:
            from .attack_action_processor import AttackActionProcessor
            from .switch_action_processor import SwitchActionProcessor
            from .item_action_processor import ItemActionProcessor
            from .special_action_processor import SpecialActionProcessor
            from ..logic.turn_logic_core import ActionType
            
            self.action_processors = {
                ActionType.ATTACK: AttackActionProcessor(self.battle_state),
                ActionType.SWITCH: SwitchActionProcessor(self.battle_state),
                ActionType.ITEM: ItemActionProcessor(self.battle_state),
                ActionType.TAME: SpecialActionProcessor(self.battle_state),
                ActionType.RUN: SpecialActionProcessor(self.battle_state)
            }
            logger.info("Action processors setup complete")
        except Exception as e:
            logger.error(f"Error setting up action processors: {e}")
            self.action_processors = {}
    
    def execute_turn(self, actions: List['BattleAction']) -> Dict[str, Any]:
        """
        Execute a complete turn with sequential action processing.
        AGENT 2: Implementiert sequenzielle Action-Ausführung mit Message-Bestätigung.
        
        Args:
            actions: List of battle actions to execute
            
        Returns:
            Dictionary with execution results
        """
        try:
            if not actions:
                return {'success': False, 'message': 'No actions to execute'}
            
            logger.info(f"🎯 TurnProcessorExecutionCore: Starting sequential turn with {len(actions)} actions")
            
            # Use ActionSequencer for sequential processing
            from .turn_processor_execution import ActionSequencer
            sequencer = ActionSequencer(self.battle_state)
            sequencer.set_action_processor(self)
            
            # Execute turn with sequencer
            return sequencer.execute_turn(actions)
            
        except Exception as e:
            logger.error(f"Error executing turn: {e}")
            return {'success': False, 'message': f'Turn execution error: {e}'}
    
    def execute_action(self, action: 'BattleAction') -> Dict[str, Any]:
        """
        Execute a single battle action.
        
        Args:
            action: BattleAction to execute
            
        Returns:
            Dictionary with action execution results
        """
        try:
            if not action or not action.actor:
                return {'success': False, 'message': 'Invalid action'}
            
            # Check if actor can act
            if not self._can_actor_act(action.actor):
                return {'success': False, 'message': 'Actor cannot act'}
            
            # Get appropriate processor
            processor = self.action_processors.get(action.action_type)
            if not processor:
                return {'success': False, 'message': f'No processor for action type: {action.action_type}'}
            
            # Execute action with performance monitoring
            start_time = time.time()
            result = processor.execute(action)
            execution_time = time.time() - start_time
            
            # Log performance if needed
            if execution_time > 0.1:  # 100ms threshold
                logger.warning(f"Slow action execution: {execution_time:.3f}s for {action.action_type}")
            
            return result
            
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
    
    def _check_battle_end_conditions(self) -> Dict[str, Any]:
        """Check if battle should end - CONSOLIDATED IMPLEMENTATION."""
        try:
            if not self.battle_state:
                return {'battle_ended': False}
            
            # Use consolidated battle end detection
            from ..battle_end_detection import BattleEndDetection
            battle_end_info = BattleEndDetection.check_and_handle_battle_end(self.battle_state)
            
            # Convert to expected format for backward compatibility
            if battle_end_info.get('battle_ended', False):
                return {
                    'battle_ended': True,
                    'result': battle_end_info.get('result'),
                    'reason': battle_end_info.get('reason', 'Unknown')
                }
            else:
                return {'battle_ended': False}
            
        except Exception as e:
            logger.error(f"Error checking battle end conditions: {e}")
            return {'battle_ended': False}
    
    def _check_battle_end_after_action(self) -> Dict[str, Any]:
        """Check if battle should end after an action (wrapper for _check_battle_end_conditions)."""
        return self._check_battle_end_conditions()
    
    # _emit_battle_end_event method removed - now handled by BattleEndDetection
    
    def _emit_turn_event(self, event_type: EventType, data: Dict[str, Any]) -> None:
        """Emit turn event through battle state event processor."""
        try:
            if hasattr(self.battle_state, 'event_processor') and self.battle_state.event_processor:
                self.battle_state.event_processor.emit_event(event_type, data)
        except Exception as e:
            logger.warning(f"Failed to emit {event_type.name} event: {e}")
