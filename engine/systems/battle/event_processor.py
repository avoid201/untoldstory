"""
Event Processor - Consolidated Facade
====================================
Facade for all event processing logic split into specialized modules.
Consolidated from event_processor.py split into 2 modules.
"""

import logging
from typing import List, Dict, Any, Optional, Callable, TYPE_CHECKING
import heapq
import time

# Import specialized event processor modules
from .events.event_processor_core import EventProcessorCore
from .events.event_processor_handlers import EventProcessorHandlers

if TYPE_CHECKING:
    from engine.systems.battle.battle_state import BattleState

try:
    from engine.systems.battle.events.event_types import EventType, BattleEvent
except ImportError:
    # Fallback if event_types is not available
    EventType = None
    BattleEvent = None

logger = logging.getLogger(__name__)


class EventProcessor:
    """
    CONSOLIDATED EVENT PROCESSOR - Facade for all event processing.
    Delegates to specialized modules for different aspects of event processing.
    """
    
    MAX_QUEUE_SIZE = 100
    MAX_HISTORY_SIZE = 50
    CLEANUP_INTERVAL = 10  # Cleanup every 10 events
    
    def __init__(self, battle_state: 'BattleState'):
        """Initialize event processor with specialized modules."""
        self.state = battle_state
        
        # Initialize specialized processors
        self.core = EventProcessorCore(battle_state)
        self.handlers = EventProcessorHandlers(battle_state)
        
        # Compatibility attributes
        self.event_handlers = self.core.event_handlers
        self.event_history = self.core.event_history
        self.processing = self.core.processing
        self._event_queue = self.core._event_queue
        self._event_counter = self.core._event_counter
        self._event_count = self.core._event_count
        self._start_time = self.core._start_time
        self._last_cleanup = self.core._last_cleanup
        
        # Register default handlers
        self.handlers.register_default_handlers(self.core)
        
        logger.info("EventProcessor initialized with specialized modules")
    
    # Core event processing methods - delegate to EventProcessorCore
    def emit_event(self, event_or_type, data: Optional[Dict[str, Any]] = None) -> bool:
        """Emit an event - delegates to EventProcessorCore."""
        return self.core.emit_event(event_or_type, data)
    
    def process_events(self) -> int:
        """Process all events - delegates to EventProcessorCore."""
        return self.core.process_events()
    
    def register_handler(self, event_type: EventType, handler: Callable):
        """Register event handler - delegates to EventProcessorCore."""
        self.core.register_handler(event_type, handler)
    
    def unregister_handler(self, event_type: EventType, handler: Callable):
        """Unregister event handler - delegates to EventProcessorCore."""
        self.core.unregister_handler(event_type, handler)
    
    def get_event_statistics(self) -> Dict[str, Any]:
        """Get event statistics - delegates to EventProcessorCore."""
        return self.core.get_event_statistics()
    
    def clear_event_queue(self):
        """Clear event queue - delegates to EventProcessorCore."""
        self.core.clear_event_queue()
    
    def _cleanup_old_events(self):
        """Cleanup old events - delegates to EventProcessorCore."""
        self.core._cleanup_old_events()
    
    # Handler management methods - delegate to EventProcessorHandlers
    def create_custom_handler(self, event_type: EventType, handler_func: Callable) -> Callable:
        """Create custom handler - delegates to EventProcessorHandlers."""
        return self.handlers.create_custom_handler(event_type, handler_func)
    
    def get_handler_count(self, event_type: EventType) -> int:
        """Get handler count - delegates to EventProcessorHandlers."""
        return self.handlers.get_handler_count(event_type)
    
    # Combined methods
    def emit_and_process(self, event_or_type, data: Optional[Dict[str, Any]] = None) -> bool:
        """Emit event and immediately process it."""
        try:
            success = self.emit_event(event_or_type, data)
            if success:
                self.process_events()
            return success
        except Exception as e:
            logger.error(f"Error in emit_and_process: {e}")
            return False
    
    def process_all_pending_events(self) -> int:
        """Process all pending events in the queue."""
        try:
            total_processed = 0
            while self._event_queue:
                processed = self.process_events()
                if processed == 0:
                    break
                total_processed += processed
            return total_processed
        except Exception as e:
            logger.error(f"Error processing all pending events: {e}")
            return 0
    
    def get_event_queue_status(self) -> Dict[str, Any]:
        """Get detailed event queue status."""
        try:
            return {
                'queue_size': len(self._event_queue),
                'history_size': len(self.event_history),
                'processing': self.processing,
                'event_counter': self._event_counter,
                'total_events': self._event_count,
                'uptime': time.time() - self._start_time
            }
        except Exception as e:
            logger.error(f"Error getting event queue status: {e}")
            return {'error': str(e)}
    
    def get_recent_events(self, count: int = 10) -> List[BattleEvent]:
        """Get recent events from history."""
        try:
            return list(self.event_history)[-count:] if self.event_history else []
        except Exception as e:
            logger.error(f"Error getting recent events: {e}")
            return []
    
    def get_events_by_type(self, event_type: EventType) -> List[BattleEvent]:
        """Get all events of a specific type from history."""
        try:
            return [event for event in self.event_history if event.event_type == event_type]
        except Exception as e:
            logger.error(f"Error getting events by type: {e}")
            return []
    
    def register_ui_handlers(self, ui_event_manager):
        """Register UI event handlers."""
        try:
            if hasattr(ui_event_manager, 'register_all_ui_handlers'):
                ui_event_manager.register_all_ui_handlers(self)
                logger.info("UI event handlers registered successfully")
            else:
                logger.warning("UI event manager missing register_all_ui_handlers method")
        except Exception as e:
            logger.error(f"Error registering UI handlers: {e}")
    
    def has_pending_events(self) -> bool:
        """Check if there are pending events in the queue."""
        return self.core.has_pending_events()
    
    def cleanup(self):
        """Cleanup all event processor resources."""
        try:
            self.core.cleanup()
            self.handlers.cleanup()
            logger.info("EventProcessor cleaned up")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    # Legacy compatibility methods
    def _register_default_handlers(self):
        """Legacy method - delegates to EventProcessorHandlers."""
        self.handlers.register_default_handlers(self.core)
    
    def _get_event_priority(self, event_type: EventType) -> int:
        """Legacy method - delegates to EventProcessorCore."""
        return self.core._get_event_priority(event_type)
    
    def _process_single_event(self, event: BattleEvent):
        """Legacy method - delegates to EventProcessorCore."""
        self.core._process_single_event(event)