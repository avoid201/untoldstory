"""
Error Recovery System - Robust Fallback Mechanisms
================================================
Comprehensive error recovery system for battle operations.
Provides fallback mechanisms for all critical battle functions.
"""

import logging
from typing import Dict, Any, List, Optional, Callable, Union, TYPE_CHECKING
import traceback
import time

if TYPE_CHECKING:
    from engine.systems.battle.battle_state import BattleState
    from engine.systems.monster_instance import MonsterInstance

logger = logging.getLogger(__name__)


class BattleErrorRecovery:
    """Robust error recovery system for battle operations."""
    
    def __init__(self, battle_state: 'BattleState' = None):
        """Initialize error recovery system."""
        self.battle_state = battle_state
        self.error_count = 0
        self.max_errors = 10
        self.error_history: List[Dict[str, Any]] = []
        self.fallback_actions: Dict[str, Callable] = {}
        
        # Initialize fallback actions
        self._init_fallback_actions()
        
        logger.info("BattleErrorRecovery initialized with robust fallback mechanisms")
    
    def _init_fallback_actions(self):
        """Initialize fallback actions for critical operations."""
        self.fallback_actions = {
            'damage_calculation': self._fallback_damage_calc,
            'move_execution': self._fallback_move_execution,
            'status_application': self._fallback_status_application,
            'monster_switch': self._fallback_monster_switch,
            'battle_phase_transition': self._fallback_phase_transition,
            'event_processing': self._fallback_event_processing,
            'ui_update': self._fallback_ui_update
        }
    
    def with_fallback(self, fallback_value: Any = None, operation_type: str = None):
        """Decorator for error recovery with operation-specific fallbacks."""
        def decorator(func):
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    self._handle_error(func.__name__, e, operation_type)
                    
                    # Try operation-specific fallback
                    if operation_type and operation_type in self.fallback_actions:
                        try:
                            return self.fallback_actions[operation_type](*args, **kwargs)
                        except Exception as fallback_error:
                            logger.error(f"Fallback for {operation_type} also failed: {fallback_error}")
                    
                    return fallback_value
            return wrapper
        return decorator
    
    @staticmethod
    def with_fallback_static(fallback_value: Any = None, operation_type: str = None):
        """Static decorator for error recovery."""
        def decorator(func):
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Error in {func.__name__}: {e}")
                    
                    # Try operation-specific fallback
                    if operation_type == 'damage_calculation':
                        try:
                            # Simple fallback damage calculation
                            if len(args) >= 3:
                                attacker, target, move = args[0], args[1], args[2]
                                attack = getattr(attacker, 'attack', 50) if attacker else 50
                                defense = getattr(target, 'defense', 50) if target else 50
                                power = getattr(move, 'power', 40) if move else 40
                                damage = max(1, (attack * 2 - defense) * power // 100)
                                return {'damage': damage, 'is_critical': False, 'is_super_effective': False, 'fallback': True}
                        except Exception as fallback_error:
                            logger.error(f"Fallback damage calc failed: {fallback_error}")
                    
                    return fallback_value
            return wrapper
        return decorator
    
    def _handle_error(self, function_name: str, error: Exception, operation_type: str = None):
        """Handle error with logging and recovery tracking."""
        self.error_count += 1
        
        error_info = {
            'timestamp': time.time(),
            'function': function_name,
            'operation_type': operation_type,
            'error': str(error),
            'traceback': traceback.format_exc()
        }
        
        self.error_history.append(error_info)
        
        # Keep only recent errors
        if len(self.error_history) > 50:
            self.error_history = self.error_history[-50:]
        
        logger.error(f"Error in {function_name}: {error}")
        
        # Check if we're hitting error limits
        if self.error_count > self.max_errors:
            logger.critical(f"Too many errors ({self.error_count}), battle may be unstable")
    
    def _fallback_damage_calc(self, *args, **kwargs) -> Dict[str, Any]:
        """Fallback damage calculation using simple formula."""
        try:
            # Simple damage formula: (attack * 2 - defense) / 4
            if len(args) >= 3:
                attacker, target, move = args[0], args[1], args[2]
                
                attack = getattr(attacker, 'attack', 50)
                defense = getattr(target, 'defense', 50)
                power = getattr(move, 'power', 40) if move else 40
                
                damage = max(1, (attack * 2 - defense) * power // 100)
                
                return {
                    'damage': damage,
                    'is_critical': False,
                    'is_super_effective': False,
                    'fallback': True
                }
            
            return {'damage': 1, 'fallback': True}
        except Exception as e:
            logger.error(f"Fallback damage calc failed: {e}")
            return {'damage': 1, 'fallback': True}
    
    def _fallback_move_execution(self, *args, **kwargs) -> Dict[str, Any]:
        """Fallback move execution."""
        try:
            return {
                'success': True,
                'message': 'Move executed (fallback)',
                'damage': 0,
                'fallback': True
            }
        except Exception as e:
            logger.error(f"Fallback move execution failed: {e}")
            return {'success': False, 'message': 'Move failed', 'fallback': True}
    
    def _fallback_status_application(self, *args, **kwargs) -> Dict[str, Any]:
        """Fallback status application."""
        try:
            return {
                'success': True,
                'status_applied': False,
                'message': 'Status application attempted (fallback)',
                'fallback': True
            }
        except Exception as e:
            logger.error(f"Fallback status application failed: {e}")
            return {'success': False, 'message': 'Status application failed', 'fallback': True}
    
    def _fallback_monster_switch(self, *args, **kwargs) -> Dict[str, Any]:
        """Fallback monster switch."""
        try:
            return {
                'success': True,
                'message': 'Monster switched (fallback)',
                'fallback': True
            }
        except Exception as e:
            logger.error(f"Fallback monster switch failed: {e}")
            return {'success': False, 'message': 'Monster switch failed', 'fallback': True}
    
    def _fallback_phase_transition(self, *args, **kwargs) -> Dict[str, Any]:
        """Fallback phase transition."""
        try:
            return {
                'success': True,
                'message': 'Phase transition completed (fallback)',
                'fallback': True
            }
        except Exception as e:
            logger.error(f"Fallback phase transition failed: {e}")
            return {'success': False, 'message': 'Phase transition failed', 'fallback': True}
    
    def _fallback_event_processing(self, *args, **kwargs) -> Dict[str, Any]:
        """Fallback event processing."""
        try:
            return {
                'success': True,
                'events_processed': 0,
                'message': 'Event processing completed (fallback)',
                'fallback': True
            }
        except Exception as e:
            logger.error(f"Fallback event processing failed: {e}")
            return {'success': False, 'message': 'Event processing failed', 'fallback': True}
    
    def _fallback_ui_update(self, *args, **kwargs) -> Dict[str, Any]:
        """Fallback UI update."""
        try:
            return {
                'success': True,
                'message': 'UI updated (fallback)',
                'fallback': True
            }
        except Exception as e:
            logger.error(f"Fallback UI update failed: {e}")
            return {'success': False, 'message': 'UI update failed', 'fallback': True}
    
    def safe_execute(self, func: Callable, *args, **kwargs) -> Dict[str, Any]:
        """Safely execute a function with error recovery."""
        try:
            result = func(*args, **kwargs)
            return {
                'success': True,
                'result': result,
                'fallback': False
            }
        except Exception as e:
            self._handle_error(func.__name__, e)
            return {
                'success': False,
                'error': str(e),
                'result': None,
                'fallback': True
            }
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics for monitoring."""
        return {
            'total_errors': self.error_count,
            'recent_errors': len(self.error_history),
            'error_rate': self.error_count / max(1, time.time() - (self.error_history[0]['timestamp'] if self.error_history else time.time())),
            'is_stable': self.error_count < self.max_errors
        }
    
    def reset_error_count(self):
        """Reset error count (call after successful operations)."""
        self.error_count = 0
        logger.info("Error count reset")


def with_battle_fallback(fallback_value: Any = None, operation_type: str = None):
    """Convenience function for battle error recovery."""
    return BattleErrorRecovery().with_fallback(fallback_value, operation_type)


def safe_battle_operation(operation_type: str, func: Callable, *args, **kwargs) -> Dict[str, Any]:
    """Safely execute a battle operation with error recovery."""
    recovery = BattleErrorRecovery()
    return recovery.safe_execute(func, *args, **kwargs)


class BattleErrorHandler:
    """Centralized error handler for battle system."""
    
    def __init__(self):
        self.recovery_system = BattleErrorRecovery()
        self.critical_errors = 0
        self.max_critical_errors = 5
    
    def handle_critical_error(self, error: Exception, context: str = "") -> bool:
        """Handle critical errors that could crash the battle."""
        self.critical_errors += 1
        
        logger.critical(f"Critical error in {context}: {error}")
        
        if self.critical_errors >= self.max_critical_errors:
            logger.critical("Too many critical errors, battle system unstable")
            return False
        
        return True
    
    def handle_recoverable_error(self, error: Exception, context: str = "") -> bool:
        """Handle recoverable errors."""
        logger.warning(f"Recoverable error in {context}: {error}")
        return True
    
    def reset_critical_errors(self):
        """Reset critical error count."""
        self.critical_errors = 0
        logger.info("Critical error count reset")


# Global error handler instance
battle_error_handler = BattleErrorHandler()