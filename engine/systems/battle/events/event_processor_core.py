"""
Event Processor Core - Consolidated Facade
=========================================
Facade for event processing logic split into specialized modules.
Consolidated from event_processor_core.py split into 2 modules.
"""

import logging
from typing import List, Dict, Any, Optional, Callable, TYPE_CHECKING
import heapq
import time

# Import specialized event processor modules
from .event_processor_queue import EventProcessorQueue
from .event_processor_management import EventProcessorManagement

if TYPE_CHECKING:
    from engine.systems.battle.battle_state import BattleState

from engine.systems.battle.events.event_types import EventType, BattleEvent

logger = logging.getLogger(__name__)


class EventProcessorCore:
    """
    CONSOLIDATED EVENT PROCESSOR CORE - Facade for event processing.
    Delegates to specialized modules for different aspects of event processing.
    """
    
    MAX_QUEUE_SIZE = 100
    MAX_HISTORY_SIZE = 50
    CLEANUP_INTERVAL = 10  # Cleanup every 10 events
    
    def __init__(self, battle_state: 'BattleState'):
        """Initialize event processor core with specialized modules."""
        self.state = battle_state
        
        # Initialize specialized processors
        self.queue = EventProcessorQueue(battle_state)
        self.management = EventProcessorManagement(battle_state)
        
        # Compatibility attributes
        self.event_handlers = self.management.event_handlers
        self.event_history = self.queue.event_history
        self.processing = self.queue.processing
        self._event_queue = self.queue._event_queue
        self._event_counter = self.queue._event_counter
        self._event_count = self.queue._event_count
        self._start_time = self.queue._start_time
        self._last_cleanup = self.queue._last_cleanup
        
        logger.info("EventProcessorCore initialized with specialized modules")
    
    # Event queue methods - delegate to EventProcessorQueue
    def emit_event(self, event_or_type, data: Optional[Dict[str, Any]] = None) -> bool:
        """Emit an event - delegates to EventProcessorQueue."""
        return self.queue.emit_event(event_or_type, data)
    
    def process_events(self) -> int:
        """Process all events - delegates to EventProcessorQueue."""
        return self.queue.process_events()
    
    def get_event_statistics(self) -> Dict[str, Any]:
        """Get event statistics - delegates to EventProcessorQueue."""
        return self.queue.get_event_statistics()
    
    def clear_event_queue(self):
        """Clear event queue - delegates to EventProcessorQueue."""
        self.queue.clear_event_queue()
    
    def _cleanup_old_events(self):
        """Cleanup old events - delegates to EventProcessorQueue."""
        self.queue._cleanup_old_events()
    
    def _get_event_priority(self, event_type: EventType) -> int:
        """Get event priority - delegates to EventProcessorQueue."""
        return self.queue._get_event_priority(event_type)
    
    def _process_single_event(self, event: BattleEvent):
        """Process single event - delegates to EventProcessorQueue."""
        self.queue._process_single_event(event)
    
    # Event handler management methods - delegate to EventProcessorManagement
    def register_handler(self, event_type: EventType, handler: Callable):
        """Register event handler - delegates to EventProcessorManagement."""
        self.management.register_handler(event_type, handler)
        # Also register with queue for processing
        self.queue.event_handlers = self.management.event_handlers
    
    def unregister_handler(self, event_type: EventType, handler: Callable):
        """Unregister event handler - delegates to EventProcessorManagement."""
        self.management.unregister_handler(event_type, handler)
        # Also unregister from queue
        self.queue.event_handlers = self.management.event_handlers
    
    def get_handlers_for_event(self, event_type: EventType) -> List[Callable]:
        """Get handlers for event - delegates to EventProcessorManagement."""
        return self.management.get_handlers_for_event(event_type)
    
    def get_handler_count(self, event_type: EventType) -> int:
        """Get handler count - delegates to EventProcessorManagement."""
        return self.management.get_handler_count(event_type)
    
    def register_safe_handler(self, event_type: EventType, handler: Callable):
        """Register safe handler - delegates to EventProcessorManagement."""
        success = self.management.register_safe_handler(event_type, handler)
        if success:
            # Also register with queue for processing
            self.queue.event_handlers = self.management.event_handlers
        return success
    
    def get_handler_statistics(self) -> Dict[str, Any]:
        """Get handler statistics - delegates to EventProcessorManagement."""
        return self.management.get_handler_statistics()
    
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
    
    def get_comprehensive_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics combining queue and handler data."""
        try:
            queue_stats = self.get_event_statistics()
            handler_stats = self.get_handler_statistics()
            
            return {
                'queue_statistics': queue_stats,
                'handler_statistics': handler_stats,
                'combined_uptime': queue_stats.get('uptime_seconds', 0),
                'total_events_processed': queue_stats.get('total_events_processed', 0),
                'total_handlers': handler_stats.get('total_handlers', 0)
            }
            
        except Exception as e:
            logger.error(f"Error getting comprehensive statistics: {e}")
            return {'error': str(e)}
    
    def has_pending_events(self) -> bool:
        """Check if there are pending events in the queue."""
        return self.queue.has_pending_events()
    
    def cleanup(self):
        """Cleanup all event processor core resources."""
        try:
            self.queue.cleanup()
            self.management.cleanup()
            logger.info("EventProcessorCore cleaned up")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")