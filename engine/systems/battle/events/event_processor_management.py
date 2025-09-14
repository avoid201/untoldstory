"""
Event Processor Management - Event Handler Management
===================================================
Event handler management and registration functionality.
Split from event_processor_core.py to comply with 300-line limit.
"""

import logging
from typing import List, Dict, Any, Optional, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from engine.systems.battle.battle_state import BattleState

from engine.systems.battle.events.event_types import EventType, BattleEvent

logger = logging.getLogger(__name__)


class EventProcessorManagement:
    """
    Event handler management functionality.
    Handles event handler registration and management.
    """
    
    def __init__(self, battle_state: 'BattleState'):
        """Initialize event management processor."""
        self.state = battle_state
        self.event_handlers: Dict[EventType, List[Callable]] = {}
        logger.info("EventProcessorManagement initialized")
    
    def register_handler(self, event_type: EventType, handler: Callable):
        """Register an event handler."""
        try:
            if event_type not in self.event_handlers:
                self.event_handlers[event_type] = []
            
            self.event_handlers[event_type].append(handler)
            logger.debug(f"Registered handler for {event_type}")
            
        except Exception as e:
            logger.error(f"Error registering handler: {e}")
    
    def unregister_handler(self, event_type: EventType, handler: Callable):
        """Unregister an event handler."""
        try:
            if event_type in self.event_handlers:
                if handler in self.event_handlers[event_type]:
                    self.event_handlers[event_type].remove(handler)
                    logger.debug(f"Unregistered handler for {event_type}")
                    
        except Exception as e:
            logger.error(f"Error unregistering handler: {e}")
    
    def get_handlers_for_event(self, event_type: EventType) -> List[Callable]:
        """Get all handlers for a specific event type."""
        try:
            return self.event_handlers.get(event_type, [])
        except Exception as e:
            logger.error(f"Error getting handlers for event: {e}")
            return []
    
    def get_handler_count(self, event_type: EventType) -> int:
        """Get the number of handlers for an event type."""
        try:
            return len(self.event_handlers.get(event_type, []))
        except Exception as e:
            logger.error(f"Error getting handler count: {e}")
            return 0
    
    def get_all_registered_handlers(self) -> Dict[EventType, List[Callable]]:
        """Get all registered handlers."""
        try:
            return dict(self.event_handlers)
        except Exception as e:
            logger.error(f"Error getting all handlers: {e}")
            return {}
    
    def clear_handlers_for_event(self, event_type: EventType):
        """Clear all handlers for a specific event type."""
        try:
            if event_type in self.event_handlers:
                self.event_handlers[event_type].clear()
                logger.debug(f"Cleared handlers for {event_type}")
        except Exception as e:
            logger.error(f"Error clearing handlers for event: {e}")
    
    def clear_all_handlers(self):
        """Clear all event handlers."""
        try:
            self.event_handlers.clear()
            logger.info("All event handlers cleared")
        except Exception as e:
            logger.error(f"Error clearing all handlers: {e}")
    
    def validate_handler(self, handler: Callable) -> bool:
        """Validate that a handler is callable and has correct signature."""
        try:
            if not callable(handler):
                logger.error("Handler is not callable")
                return False
            
            # Check if handler accepts BattleEvent parameter
            import inspect
            sig = inspect.signature(handler)
            params = list(sig.parameters.keys())
            
            if len(params) != 1:
                logger.warning(f"Handler should accept exactly 1 parameter (BattleEvent), got {len(params)}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating handler: {e}")
            return False
    
    def create_safe_handler(self, handler: Callable) -> Callable:
        """Create a safe wrapper for a handler that catches exceptions."""
        def safe_handler(event: BattleEvent):
            try:
                handler(event)
            except Exception as e:
                logger.error(f"Error in event handler: {e}")
        
        return safe_handler
    
    def register_safe_handler(self, event_type: EventType, handler: Callable):
        """Register a handler with automatic error handling."""
        try:
            if not self.validate_handler(handler):
                logger.error(f"Invalid handler for {event_type}")
                return False
            
            safe_handler = self.create_safe_handler(handler)
            self.register_handler(event_type, safe_handler)
            return True
            
        except Exception as e:
            logger.error(f"Error registering safe handler: {e}")
            return False
    
    def get_handler_statistics(self) -> Dict[str, Any]:
        """Get statistics about registered handlers."""
        try:
            total_handlers = sum(len(handlers) for handlers in self.event_handlers.values())
            event_types_with_handlers = len(self.event_handlers)
            
            handler_counts = {}
            for event_type, handlers in self.event_handlers.items():
                handler_counts[event_type.name] = len(handlers)
            
            return {
                'total_handlers': total_handlers,
                'event_types_with_handlers': event_types_with_handlers,
                'handler_counts_by_type': handler_counts,
                'average_handlers_per_type': total_handlers / event_types_with_handlers if event_types_with_handlers > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting handler statistics: {e}")
            return {'error': str(e)}
    
    def list_handlers_for_event(self, event_type: EventType) -> List[str]:
        """List handler names for a specific event type."""
        try:
            handlers = self.event_handlers.get(event_type, [])
            handler_names = []
            
            for handler in handlers:
                if hasattr(handler, '__name__'):
                    handler_names.append(handler.__name__)
                else:
                    handler_names.append(str(handler))
            
            return handler_names
            
        except Exception as e:
            logger.error(f"Error listing handlers for event: {e}")
            return []
    
    def cleanup(self):
        """Cleanup event management processor resources."""
        try:
            self.clear_all_handlers()
            logger.info("EventProcessorManagement cleaned up")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
