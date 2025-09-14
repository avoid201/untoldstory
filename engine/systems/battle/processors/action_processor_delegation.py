"""
Action Processor Delegation - Action execution delegation
========================================================
Action execution delegation functionality extracted from action_processor.py
to comply with 300-line limit.
"""

import logging
from typing import List, Optional, Dict, Any, Tuple, TYPE_CHECKING

from engine.systems.battle.turn_logic import BattleAction, ActionType
from engine.systems.battle.battle_validation import BattleValidator
from engine.systems.battle.event_processor import EventType
from engine.systems.battle.error_recovery import BattleErrorRecovery, with_battle_fallback
from engine.systems.talent_system import get_talent_database

# Import specialized processors
from .attack_action_processor import AttackActionProcessor
from .special_action_processor import SpecialActionProcessor
from .item_action_processor import ItemActionProcessor
from .tame_action_processor import TameActionProcessor

if TYPE_CHECKING:
    from engine.systems.battle.battle_state import BattleState
    from engine.systems.monster_instance import MonsterInstance
    from engine.systems.moves import Move
    from engine.systems.conditions import StatusCondition
    from engine.systems.battle.turn_processor import TurnProcessor

logger = logging.getLogger(__name__)


class ActionProcessorDelegation:
    """
    Action execution delegation functionality.
    Handles delegation to specialized action processors.
    """
    
    def __init__(self, battle_state: 'BattleState'):
        """Initialize action processor delegation."""
        self.state = battle_state
        self.validator = BattleValidator()
        
        # Talent System Integration
        self.talent_database = get_talent_database()
        
        # Initialize specialized processors
        self.processors = [
            AttackActionProcessor(battle_state),
            SpecialActionProcessor(battle_state),
            ItemActionProcessor(battle_state),
            TameActionProcessor(battle_state)
        ]
        
        logger.info("ActionProcessorDelegation initialized with specialized processors")
    
    def execute_action(self, action: BattleAction) -> Dict[str, Any]:
        """
        Execute battle action - delegates to specialized processors.
        
        Args:
            action: Battle action to execute
            
        Returns:
            Execution result dictionary
        """
        try:
            # Validate action before execution
            is_valid, errors = self.validator.validate_action(
                action, self.state.player_active, self.state.enemy_active
            )
            
            if not is_valid:
                return {
                    'success': False,
                    'message': f"Invalid action: {', '.join(errors)}",
                    'damage_dealt': 0,
                    'monsters_fainted': 0,
                    'events': []
                }
            
            # Delegate to appropriate processor
            result = self._delegate_to_processor(action)
            
            # Log execution
            logger.info(f"Action executed: {action.action_type} by {action.actor.name}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing action: {e}")
            return {
                'success': False,
                'message': f"Execution error: {e}",
                'damage_dealt': 0,
                'monsters_fainted': 0,
                'events': []
            }
    
    def _delegate_to_processor(self, action: BattleAction) -> Dict[str, Any]:
        """
        Delegate action to appropriate specialized processor.
        
        Args:
            action: Action to delegate
            
        Returns:
            Execution result
        """
        try:
            action_type = action.action_type
            
            # Find appropriate processor
            for processor in self.processors:
                if hasattr(processor, 'can_handle') and processor.can_handle(action):
                    # Try both execute_action and execute methods
                    if hasattr(processor, 'execute_action'):
                        return processor.execute_action(action)
                    elif hasattr(processor, 'execute'):
                        return processor.execute(action)
                    else:
                        logger.warning(f"Processor {processor.__class__.__name__} has no execute method")
                        continue
            
            # Fallback for unknown action types
            logger.warning(f"No processor found for action type: {action_type}")
            return {
                'success': False,
                'message': f"No processor for action type: {action_type}",
                'damage_dealt': 0,
                'monsters_fainted': 0,
                'events': []
            }
            
        except Exception as e:
            logger.error(f"Error delegating to processor: {e}")
            return {
                'success': False,
                'message': f"Delegation error: {e}",
                'damage_dealt': 0,
                'monsters_fainted': 0,
                'events': []
            }
    
    def execute_action_with_recovery(self, action: BattleAction) -> Dict[str, Any]:
        """
        Execute action with error recovery.
        
        Args:
            action: Action to execute
            
        Returns:
            Execution result with recovery information
        """
        try:
            # Try normal execution first
            result = self.execute_action(action)
            
            if result['success']:
                return result
            
            # Try recovery if execution failed
            recovery_result = self._attempt_recovery(action, result)
            
            if recovery_result['success']:
                logger.info(f"Action recovered: {action.action_type}")
                return recovery_result
            
            # Return original failure if recovery failed
            return result
            
        except Exception as e:
            logger.error(f"Error in action execution with recovery: {e}")
            return {
                'success': False,
                'message': f"Execution error: {e}",
                'damage_dealt': 0,
                'monsters_fainted': 0,
                'events': [],
                'recovery_attempted': True,
                'recovery_successful': False
            }
    
    def _attempt_recovery(self, action: BattleAction, failed_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Attempt to recover from failed action execution.
        
        Args:
            action: Failed action
            failed_result: Result of failed execution
            
        Returns:
            Recovery result
        """
        try:
            # Basic recovery strategies
            recovery_strategies = [
                self._recovery_switch_target,
                self._recovery_use_fallback_move,
                self._recovery_skip_action
            ]
            
            for strategy in recovery_strategies:
                try:
                    result = strategy(action, failed_result)
                    if result['success']:
                        result['recovery_attempted'] = True
                        result['recovery_successful'] = True
                        return result
                except Exception as e:
                    logger.warning(f"Recovery strategy failed: {e}")
                    continue
            
            # No recovery strategy worked
            return {
                'success': False,
                'message': "All recovery strategies failed",
                'damage_dealt': 0,
                'monsters_fainted': 0,
                'events': [],
                'recovery_attempted': True,
                'recovery_successful': False
            }
            
        except Exception as e:
            logger.error(f"Error in recovery attempt: {e}")
            return {
                'success': False,
                'message': f"Recovery error: {e}",
                'damage_dealt': 0,
                'monsters_fainted': 0,
                'events': [],
                'recovery_attempted': True,
                'recovery_successful': False
            }
    
    def _recovery_switch_target(self, action: BattleAction, failed_result: Dict[str, Any]) -> Dict[str, Any]:
        """Recovery strategy: switch to different target."""
        try:
            # Find alternative target
            if action.action_type in ['ATTACK', 'SPECIAL']:
                if action.target == self.state.player_active:
                    # Switch to enemy target
                    action.target = self.state.enemy_active
                elif action.target == self.state.enemy_active:
                    # Switch to player target
                    action.target = self.state.player_active
                
                # Try execution again
                return self.execute_action(action)
            
            return failed_result
            
        except Exception as e:
            logger.error(f"Error in target switch recovery: {e}")
            return failed_result
    
    def _recovery_use_fallback_move(self, action: BattleAction, failed_result: Dict[str, Any]) -> Dict[str, Any]:
        """Recovery strategy: use fallback move."""
        try:
            if action.action_type in ['ATTACK', 'SPECIAL'] and action.move:
                # Try execution again with original move
                return self.execute_action(action)
            return failed_result
        except Exception as e:
            logger.error(f"Error in fallback move recovery: {e}")
            return failed_result
    
    def _recovery_skip_action(self, action: BattleAction, failed_result: Dict[str, Any]) -> Dict[str, Any]:
        """Recovery strategy: skip action gracefully."""
        try:
            # Emit skip event
            if hasattr(self.state, 'event_processor') and self.state.event_processor:
                self.state.event_processor.emit_event(
                    EventType.ACTION_COMPLETE,
                    {
                        'actor': action.actor,
                        'action': action.action_type,
                        'success': False,
                        'message': 'Action skipped due to error'
                    }
                )
            
            return {
                'success': True,
                'message': 'Action skipped',
                'damage_dealt': 0,
                'monsters_fainted': 0,
                'events': [EventType.ACTION_COMPLETE],
                'recovery_attempted': True,
                'recovery_successful': True
            }
            
        except Exception as e:
            logger.error(f"Error in skip action recovery: {e}")
            return failed_result
    
    def get_processor_info(self) -> Dict[str, Any]:
        """Get information about available processors."""
        try:
            return {
                'total_processors': len(self.processors),
                'processors': [processor.__class__.__name__ for processor in self.processors]
            }
        except Exception as e:
            logger.error(f"Error getting processor info: {e}")
            return {'total_processors': 0, 'processors': []}
    
    def cleanup(self) -> None:
        """Cleanup delegation resources."""
        try:
            for processor in self.processors:
                if hasattr(processor, 'cleanup'):
                    processor.cleanup()
            logger.info("Action processor delegation cleaned up")
        except Exception as e:
            logger.error(f"Error during delegation cleanup: {e}")
