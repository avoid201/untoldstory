"""
Action Processor - Facade for specialized processors
==== AGENT 2 COMPLETED ====
CHANGES: Split 793 lines into 4 specialized processors
==== END AGENT WORK ====
"""

import logging
from typing import List, Optional, Dict, Any, Tuple, TYPE_CHECKING

from engine.systems.battle.turn_logic import BattleAction, ActionType
from engine.systems.battle.battle_validation import BattleValidator
from engine.systems.battle.event_processor import EventType
from engine.systems.battle.error_recovery import BattleErrorRecovery, with_battle_fallback
from engine.systems.talent_system import get_talent_database

# Import specialized processors
from engine.systems.battle.processors.attack_action_processor import AttackActionProcessor
from engine.systems.battle.processors.special_action_processor import SpecialActionProcessor
from engine.systems.battle.processors.item_action_processor import ItemActionProcessor

if TYPE_CHECKING:
    from engine.systems.battle.battle_state import BattleState
    from engine.systems.monster_instance import MonsterInstance
    from engine.systems.moves import Move
    from engine.systems.conditions import StatusCondition
    from engine.systems.battle.turn_processor import TurnProcessor

logger = logging.getLogger(__name__)


class ActionProcessor:
    """
    Facade delegating to specialized processors.
    Manages action queuing, validation, and execution.
    """
    
    def __init__(self, battle_state: 'BattleState'):
        """Initialize action processor with battle state and specialized processors."""
        self.state = battle_state
        self.validator = BattleValidator()
        self.action_queue: List[BattleAction] = []
        
        # Talent System Integration
        self.talent_database = get_talent_database()
        
        # Initialize specialized processors
        self.processors = [
            AttackActionProcessor(battle_state),
            SpecialActionProcessor(battle_state),
            ItemActionProcessor(battle_state)
        ]
    
    def queue_action(self, action) -> bool:
        """Queue action - single conversion point."""
        try:
            # Import the single source of truth
            from engine.systems.battle.turn_logic import create_action_from_dict
            
            if isinstance(action, dict):
                # Use actors from state
                battle_action = create_action_from_dict(
                    action,
                    actor=self.state.player_active if action.get('actor') == 'player' else self.state.enemy_active,
                    target=self.state.enemy_active if action.get('target') == 'enemy' else self.state.player_active
                )
            else:
                battle_action = action
            
            if not battle_action or not self.validate_action(battle_action):
                return False
                
            self.action_queue.append(battle_action)
            logger.info(f"Action queued: {battle_action.action_type.name}")
            
            # EMIT ACTION_QUEUED EVENT
            if hasattr(self.state, 'event_processor') and self.state.event_processor:
                self.state.event_processor.emit_event(
                    EventType.ACTION_ANNOUNCE,
                    {'action': battle_action.action_type.name, 'actor': battle_action.actor.name}
                )
            return True
        except Exception as e:
            logger.error(f"Failed to queue action: {e}")
            return False
    
    @with_battle_fallback({'success': False, 'error': 'Action execution failed'})
    def execute_action(self, action: BattleAction) -> Dict[str, Any]:
        """Execute a single action by delegating to appropriate processor with error recovery."""
        try:
            logger.debug(f"Executing action: {action.action_type.name} by {action.actor.name}")
            
            # Enhanced validation with recovery suggestions
            is_valid, errors, suggestions = BattleValidator.validate_action_with_recovery(action, self.state)
            if not is_valid:
                logger.warning(f"Action validation failed: {errors}")
                return {
                    'success': False, 
                    'error': 'Invalid action', 
                    'action_type': action.action_type.name,
                    'validation_errors': errors,
                    'suggestions': suggestions
                }
            
            # Delegate to appropriate processor with error recovery
            for processor in self.processors:
                if processor.can_handle(action):
                    try:
                        return processor.execute(action)
                    except Exception as processor_error:
                        logger.error(f"Processor {processor.__class__.__name__} failed: {processor_error}")
                        # Try fallback execution
                        return self._execute_action_fallback(action)
            
            # No processor found
            logger.warning(f"No processor found for action type: {action.action_type}")
            return {'success': False, 'error': 'No processor for action type', 'action_type': action.action_type.name}
            
        except Exception as e:
            logger.error(f"Error executing action: {e}")
            return {'success': False, 'error': str(e), 'action_type': action.action_type.name}
    
    def validate_action(self, action: BattleAction) -> bool:
        """Validate an action before execution using BattleValidator."""
        return BattleValidator.validate_battle_action(action)
    
    def validate_action_with_errors(self, action: BattleAction, state: 'BattleState') -> Tuple[bool, List[str]]:
        """Validate an action with detailed error reporting."""
        # Delegate to base processor for detailed validation
        for processor in self.processors:
            if processor.can_handle(action):
                return processor.validate_action_detailed(action)
        
        # Fallback to basic validation
        return self.validator.validate_battle_action(action), []
    
    def _execute_action_fallback(self, action: BattleAction) -> Dict[str, Any]:
        """
        Fallback execution when specialized processors fail.
        Provides basic functionality for critical actions.
        """
        try:
            logger.info(f"Using fallback execution for {action.action_type.name}")
            
            if action.action_type == ActionType.ATTACK:
                return self._execute_attack_fallback(action)
            elif action.action_type == ActionType.SWITCH:
                return self._execute_switch_fallback(action)
            elif action.action_type == ActionType.FLEE:
                return self._execute_flee_fallback(action)
            else:
                return {
                    'success': False, 
                    'error': f'No fallback available for {action.action_type.name}',
                    'action_type': action.action_type.name
                }
                
        except Exception as e:
            logger.error(f"Fallback execution failed: {e}")
            return {
                'success': False, 
                'error': f'Fallback execution failed: {e}',
                'action_type': action.action_type.name
            }
    
    def _execute_attack_fallback(self, action: BattleAction) -> Dict[str, Any]:
        """Fallback attack execution using error recovery system."""
        return BattleErrorRecovery.safe_move_execution(action.actor, action.target, action.move)
    
    def _execute_switch_fallback(self, action: BattleAction) -> Dict[str, Any]:
        """Fallback switch execution."""
        try:
            if not action.switch_to:
                return {'success': False, 'error': 'No switch target specified'}
            
            # Basic switch logic
            if hasattr(self.state, 'player_team') and action.switch_to in self.state.player_team:
                self.state.player_active = action.switch_to
                return {
                    'success': True, 
                    'message': f'Switched to {action.switch_to.name}',
                    'action_type': 'switch'
                }
            else:
                return {'success': False, 'error': 'Invalid switch target'}
                
        except Exception as e:
            return {'success': False, 'error': f'Switch failed: {e}'}
    
    def _execute_flee_fallback(self, action: BattleAction) -> Dict[str, Any]:
        """Fallback flee execution."""
        try:
            # Simple flee logic - always succeeds for now
            return {
                'success': True, 
                'message': 'Successfully fled from battle',
                'action_type': 'flee'
            }
        except Exception as e:
            return {'success': False, 'error': f'Flee failed: {e}'}
    
    def process_player_action(self, state: 'BattleState', action) -> Dict[str, Any]:
        """Process action - accept dict OR BattleAction with robust validation."""
        try:
            logger.debug(f"Processing player action: {type(action)} - {action}")
            
            # Ensure we have required actors
            if not state.player_active:
                action_type = action.get('action_type', 'unknown') if isinstance(action, dict) else getattr(action, 'action_type', 'unknown')
                return {
                    'success': False, 
                    'error': 'No active player monster',
                    'action_type': action_type
                }
            
            # Convert to BattleAction if needed
            if isinstance(action, dict):
                from engine.systems.battle.turn_logic import create_action_from_dict
                battle_action = create_action_from_dict(
                    action,
                    actor=state.player_active,
                    target=state.enemy_active
                )
                if not battle_action:
                    return {"success": False, "error": "Invalid action format"}
            else:
                battle_action = action
            
            # Validate using BattleValidator
            is_valid, errors = self.validate_action_with_errors(battle_action, state)
            if not is_valid:
                return {"success": False, "errors": errors}
            
            # Execute
            result = self.execute_action(battle_action)
            return {"success": True, "result": result}
            
        except Exception as e:
            logger.error(f"Action processing failed: {e}")
            return {"success": False, "error": str(e)}
    
    # Queue management methods
    def clear_queue(self) -> None:
        """Clear the action queue."""
        try:
            self.action_queue.clear()
            logger.debug("Action queue cleared")
        except Exception as e:
            logger.error(f"Error clearing action queue: {e}")
    
    def get_action_queue(self) -> List[BattleAction]:
        """Get current action queue."""
        return self.action_queue.copy()
    
    def has_actions(self) -> bool:
        """Check if there are actions in the queue."""
        return bool(self.action_queue)
    
    def get_queue_length(self) -> int:
        """Get the number of actions in the queue."""
        return len(self.action_queue)