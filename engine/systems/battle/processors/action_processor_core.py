"""
Action Processor Core - Core action processing logic
===================================================
Core action processing functionality extracted from action_processor.py
to comply with 300-line limit.
"""

import logging
from typing import List, Optional, Dict, Any, Tuple, TYPE_CHECKING

from engine.systems.battle.turn_logic import BattleAction, ActionType
from engine.systems.battle.battle_validation import BattleValidator
from engine.systems.battle.event_processor import EventType
from engine.systems.battle.error_recovery import BattleErrorRecovery, with_battle_fallback
from engine.systems.talent_system import get_talent_database

if TYPE_CHECKING:
    from engine.systems.battle.battle_state import BattleState
    from engine.systems.monster_instance import MonsterInstance
    from engine.systems.moves import Move
    from engine.systems.conditions import StatusCondition
    from engine.systems.battle.turn_processor import TurnProcessor

logger = logging.getLogger(__name__)


class ActionProcessorCore:
    """
    Core action processing functionality.
    Handles action queuing, validation, and basic execution logic.
    """
    
    def __init__(self, battle_state: 'BattleState'):
        """Initialize action processor core."""
        self.state = battle_state
        self.validator = BattleValidator()
        self.action_queue: List[BattleAction] = []
        
        # Talent System Integration
        self.talent_database = get_talent_database()
        
        logger.info("ActionProcessorCore initialized")
    
    def add_action(self, action: BattleAction) -> bool:
        """
        Add action to queue.
        
        Args:
            action: Battle action to add
            
        Returns:
            True if action was added successfully
        """
        try:
            # Validate action before adding
            is_valid, errors = self.validator.validate_action(
                action, self.state.player_active, self.state.enemy_active
            )
            
            if not is_valid:
                logger.warning(f"Invalid action rejected: {errors}")
                return False
            
            # Add to queue
            self.action_queue.append(action)
            logger.info(f"Action added to queue: {action.action_type} by {action.actor.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding action to queue: {e}")
            return False
    
    def clear_queue(self) -> None:
        """Clear action queue."""
        try:
            self.action_queue.clear()
            logger.info("Action queue cleared")
        except Exception as e:
            logger.error(f"Error clearing action queue: {e}")
    
    def get_queue_size(self) -> int:
        """Get current queue size."""
        return len(self.action_queue)
    
    def get_next_action(self) -> Optional[BattleAction]:
        """Get next action from queue."""
        try:
            if self.action_queue:
                return self.action_queue.pop(0)
            return None
        except Exception as e:
            logger.error(f"Error getting next action: {e}")
            return None
    
    def peek_next_action(self) -> Optional[BattleAction]:
        """Peek at next action without removing it."""
        try:
            if self.action_queue:
                return self.action_queue[0]
            return None
        except Exception as e:
            logger.error(f"Error peeking at next action: {e}")
            return None
    
    def validate_action_queue(self) -> Tuple[bool, List[str]]:
        """
        Validate entire action queue.
        
        Returns:
            Tuple of (is_valid, error_messages)
        """
        try:
            errors = []
            
            for i, action in enumerate(self.action_queue):
                is_valid, action_errors = self.validator.validate_action(
                    action, self.state.player_active, self.state.enemy_active
                )
                
                if not is_valid:
                    errors.append(f"Action {i+1}: {', '.join(action_errors)}")
            
            return len(errors) == 0, errors
            
        except Exception as e:
            logger.error(f"Error validating action queue: {e}")
            return False, [f"Validation error: {e}"]
    
    def get_queue_info(self) -> Dict[str, Any]:
        """Get information about current queue."""
        try:
            return {
                'queue_size': len(self.action_queue),
                'actions': [
                    {
                        'action_type': action.action_type,
                        'actor': action.actor.name if action.actor and hasattr(action.actor, 'name') else 'Unknown',
                        'target': action.target.name if action.target and hasattr(action.target, 'name') else 'None',
                        'move': action.move.name if action.move and hasattr(action.move, 'name') else 'None'
                    }
                    for action in self.action_queue
                ]
            }
        except Exception as e:
            logger.error(f"Error getting queue info: {e}")
            return {'queue_size': 0, 'actions': []}
    
    def can_add_action(self, action: BattleAction) -> Tuple[bool, str]:
        """
        Check if action can be added to queue.
        
        Args:
            action: Action to check
            
        Returns:
            Tuple of (can_add, reason)
        """
        try:
            # Check if queue is full (max 10 actions)
            if len(self.action_queue) >= 10:
                return False, "Action queue is full"
            
            # Check if actor is conscious
            if action.actor and hasattr(action.actor, 'current_hp') and action.actor.current_hp <= 0:
                return False, "Actor is fainted"
            
            # Check if target is valid for action type
            if action.action_type in ['ATTACK', 'SPECIAL']:
                if not action.target:
                    return False, "Attack action requires target"
                
                if action.target and hasattr(action.target, 'current_hp') and action.target.current_hp <= 0:
                    return False, "Target is fainted"
            
            return True, "Action can be added"
            
        except Exception as e:
            logger.error(f"Error checking if action can be added: {e}")
            return False, f"Error: {e}"
    
    def get_action_priority(self, action: BattleAction) -> int:
        """
        Get action priority for turn order.
        
        Args:
            action: Action to get priority for
            
        Returns:
            Priority value (higher = goes first)
        """
        try:
            # Base priority by action type
            priority_map = {
                'FLEE': 6,
                'SWITCH': 5,
                'ITEM': 4,
                'TAME': 3,
                'ATTACK': 2,
                'SPECIAL': 2,
                'SCOUT': 1,
                'PASS': 0
            }
            
            base_priority = priority_map.get(action.action_type, 0)
            
            # Add move priority if it's an attack
            if action.action_type in ['ATTACK', 'SPECIAL'] and action.move:
                if hasattr(action.move, 'priority'):
                    base_priority += action.move.priority
            
            return base_priority
            
        except Exception as e:
            logger.error(f"Error getting action priority: {e}")
            return 0
    
    def sort_actions_by_priority(self, actions: List[BattleAction]) -> List[BattleAction]:
        """
        Sort actions by priority and speed.
        
        Args:
            actions: List of actions to sort
            
        Returns:
            Sorted list of actions
        """
        try:
            def sort_key(action):
                priority = self.get_action_priority(action)
                speed = getattr(action.actor, 'current_stats', {}).get('spd', 0) if action.actor else 0
                return (-priority, -speed)  # Negative for descending order
            
            return sorted(actions, key=sort_key)
            
        except Exception as e:
            logger.error(f"Error sorting actions by priority: {e}")
            return actions
    
    def execute_action_with_message(self, action: 'BattleAction') -> Dict[str, Any]:
        """
        Execute action with message integration for sequential processing.
        AGENT 2: Implementiert Message-Events vor Action-Execution.
        
        Args:
            action: BattleAction to execute
            
        Returns:
            Dictionary with execution results
        """
        try:
            if not action or not action.actor:
                return {'success': False, 'message': 'Invalid action'}
            
            logger.info(f"🎯 ActionProcessorCore: Executing action with message integration")
            
            # Emit ACTION_ANNOUNCE event (Message-Bestätigung erforderlich)
            message = f"{action.actor.name} setzt {action.move.name if action.move else action.action_type.name} ein!"
            self._emit_event(EventType.MESSAGE_SHOW, {
                'message': message,
                'duration': 1.5,
                'blocking': True  # Requires user confirmation
            })
            
            # Execute action using appropriate processor
            action_result = self._execute_action_internal(action)
            
            # Emit ACTION_COMPLETE event
            self._emit_event(EventType.ACTION_COMPLETE, {
                'action': action.action_type.name,
                'actor': action.actor.name,
                'success': action_result.get('success', False),
                'result': action_result
            })
            
            return action_result
            
        except Exception as e:
            logger.error(f"Error executing action with message: {e}")
            return {'success': False, 'message': f'Action execution error: {e}'}
    
    
    def _execute_action_internal(self, action: 'BattleAction') -> Dict[str, Any]:
        """Internal action execution logic."""
        try:
            # Get appropriate processor
            processor = self._get_action_processor(action.action_type)
            if not processor:
                return {'success': False, 'message': f'No processor for action type: {action.action_type}'}
            
            # Execute action
            result = processor.execute(action)
            
            # Emit damage and HP update events if successful
            if result.get('success', False) and result.get('damage_dealt', 0) > 0:
                self._emit_damage_events(action, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing action internally: {e}")
            return {'success': False, 'message': f'Action execution error: {e}'}
    
    def _get_action_processor(self, action_type: 'ActionType'):
        """Get appropriate action processor for action type."""
        try:
            from .attack_action_processor import AttackActionProcessor
            from .switch_action_processor import SwitchActionProcessor
            from .item_action_processor import ItemActionProcessor
            from .special_action_processor import SpecialActionProcessor
            from ..logic.turn_logic_core import ActionType
            
            processors = {
                ActionType.ATTACK: AttackActionProcessor(self.state),
                ActionType.SWITCH: SwitchActionProcessor(self.state),
                ActionType.ITEM: ItemActionProcessor(self.state),
                ActionType.TAME: SpecialActionProcessor(self.state),
                ActionType.RUN: SpecialActionProcessor(self.state)
            }
            
            return processors.get(action_type)
            
        except Exception as e:
            logger.error(f"Error getting action processor: {e}")
            return None
    
    def _emit_damage_events(self, action: 'BattleAction', result: Dict[str, Any]) -> None:
        """Emit damage and HP update events."""
        try:
            if not action.target:
                return
            
            damage = result.get('damage_dealt', 0)
            if damage > 0:
                # Emit DAMAGE_DEALT event
                self._emit_event(EventType.DAMAGE_DEALT, {
                    'target': action.target,
                    'damage': damage,
                    'is_critical': result.get('is_critical', False),
                    'is_super_effective': result.get('is_super_effective', False)
                })
                
                # Emit HP_BAR_UPDATE event
                self._emit_event(EventType.HP_BAR_UPDATE, {
                    'target': action.target,
                    'current_hp': action.target.current_hp,
                    'max_hp': action.target.max_hp,
                    'damage': damage
                })
                
        except Exception as e:
            logger.error(f"Error emitting damage events: {e}")
    
    def _emit_event(self, event_type: EventType, data: Dict[str, Any]) -> None:
        """Emit event through battle state event processor."""
        try:
            if hasattr(self.state, 'event_processor') and self.state.event_processor:
                self.state.event_processor.emit_event(event_type, data)
        except Exception as e:
            logger.warning(f"Failed to emit {event_type.name} event: {e}")
    
    def get_action_statistics(self) -> Dict[str, Any]:
        """Get action processing statistics."""
        try:
            stats = {
                'total_actions_processed': 0,
                'successful_actions': 0,
                'failed_actions': 0,
                'action_types': {},
                'average_processing_time': 0.0
            }
            
            # This would be populated by actual processing
            # For now, return basic stats
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting action statistics: {e}")
            return {}
    
    def reset_processor(self) -> None:
        """Reset processor state."""
        try:
            self.clear_queue()
            logger.info("Action processor core reset")
        except Exception as e:
            logger.error(f"Error resetting processor: {e}")
    
    def cleanup(self) -> None:
        """Cleanup processor resources."""
        try:
            self.clear_queue()
            logger.info("Action processor core cleaned up")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
