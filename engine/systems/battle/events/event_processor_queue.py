"""
Event Processor Queue - Consolidated Facade
==========================================
Facade for event queue management logic split into specialized modules.
Consolidated from event_processor_queue.py split into 2 modules.
"""

import logging
from typing import List, Dict, Any, Optional, Callable, TYPE_CHECKING
import heapq
import time

# Import specialized event processor modules
from .event_processor_priority import EventProcessorPriority

if TYPE_CHECKING:
    from engine.systems.battle.battle_state import BattleState

from engine.systems.battle.events.event_types import EventType, BattleEvent

logger = logging.getLogger(__name__)


class EventProcessorQueue:
    """
    CONSOLIDATED EVENT PROCESSOR QUEUE - Facade for event queue management.
    Delegates to specialized modules for different aspects of event queue management.
    """
    
    MAX_QUEUE_SIZE = 100
    MAX_HISTORY_SIZE = 50
    CLEANUP_INTERVAL = 10  # Cleanup every 10 events
    
    def __init__(self, battle_state: 'BattleState'):
        """Initialize event queue processor with specialized modules."""
        self.state = battle_state
        self.event_handlers: Dict[EventType, List[Callable]] = {}
        self.event_history: List[BattleEvent] = []
        self.processing = False
        
        # Initialize specialized processors
        self.priority = EventProcessorPriority(battle_state)
        
        # Compatibility attributes
        self._event_queue = self.priority._event_queue
        self._event_counter = self.priority._event_counter
        
        # Performance tracking
        self._event_count = 0
        self._start_time = time.time()
        self._last_cleanup = time.time()
        
        logger.info("EventProcessorQueue initialized with specialized modules")
    
    def emit_event(self, event_or_type, data: Optional[Dict[str, Any]] = None) -> bool:
        """
        Emit an event to the processing queue.
        
        Args:
            event_or_type: EventType enum or BattleEvent object
            data: Optional event data
            
        Returns:
            True if event was queued successfully
        """
        try:
            # Check queue size limit BEFORE adding
            current_size = self.priority.get_queue_size()
            if current_size >= self.MAX_QUEUE_SIZE:
                logger.warning(f"Event queue full ({current_size}/{self.MAX_QUEUE_SIZE}), performing emergency cleanup")
                self._emergency_cleanup()
            
            # Create event object
            if isinstance(event_or_type, EventType):
                event = BattleEvent(
                    event_type=event_or_type,
                    data=data or {}
                )
            elif isinstance(event_or_type, BattleEvent):
                event = event_or_type
            else:
                logger.error(f"Invalid event type: {type(event_or_type)}")
                return False
            
            # Add to queue using priority processor
            success = self.priority.add_event_to_queue(event)
            if success:
                self._event_counter += 1
                self._event_count += 1
                
                # Periodic cleanup
                if self._event_count % self.CLEANUP_INTERVAL == 0:
                    self._cleanup_old_events()
            else:
                logger.error(f"Failed to add event to queue: {event.event_type}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error emitting event: {e}")
            return False
    
    def process_events(self) -> int:
        """
        Process all events in the queue.
        
        Returns:
            Number of events processed
        """
        try:
            if self.processing:
                return 0  # Prevent recursive processing
            
            self.processing = True
            processed_count = 0
            
            while not self.priority.is_queue_empty():
                try:
                    event = self.priority.get_next_event()
                    if not event:
                        break
                    
                    # Process the event
                    self._process_single_event(event)
                    
                    # Add to history
                    self.event_history.append(event)
                    if len(self.event_history) > self.MAX_HISTORY_SIZE:
                        self.event_history.pop(0)
                    
                    processed_count += 1
                    
                except Exception as e:
                    logger.error(f"Error processing event: {e}")
                    continue
            
            return processed_count
            
        finally:
            self.processing = False
    
    def _process_single_event(self, event: BattleEvent):
        """Process a single event."""
        try:
            # Get handlers for this event type
            handlers = self.event_handlers.get(event.event_type, [])
            
            if not handlers:
                logger.debug(f"No handlers for event type: {event.event_type}")
                return
            
            # Call all handlers
            for handler in handlers:
                try:
                    handler(event)
                except Exception as e:
                    logger.error(f"Error in event handler: {e}")
                    
        except Exception as e:
            logger.error(f"Error processing single event: {e}")
    
    def _cleanup_old_events(self):
        """Clean up old events to prevent memory leaks."""
        try:
            current_time = time.time()
            
            # Remove events older than 5 minutes
            cutoff_time = current_time - 300
            
            # Clean up history
            self.event_history = [
                event for event in self.event_history 
                if hasattr(event, 'timestamp') and event.timestamp > cutoff_time
            ]
            
            # Clean up queue (remove oldest events)
            if self.priority.get_queue_size() > self.MAX_QUEUE_SIZE // 2:
                # Keep only the most recent half
                temp_events = []
                while not self.priority.is_queue_empty() and len(temp_events) < self.MAX_QUEUE_SIZE // 2:
                    event = self.priority.get_next_event()
                    if event:
                        temp_events.append(event)
                
                # Clear and re-add events
                self.priority.clear_queue()
                for event in temp_events:
                    self.priority.add_event_to_queue(event)
            
            self._last_cleanup = current_time
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def _emergency_cleanup(self):
        """Emergency cleanup when queue is full."""
        try:
            logger.warning("Performing emergency queue cleanup")
            
            # Clear all low-priority events (priority > 50)
            temp_events = []
            while not self.priority.is_queue_empty():
                event = self.priority.get_next_event()
                if event and self.priority._get_event_priority(event.event_type) <= 50:
                    temp_events.append(event)
            
            # Clear queue and re-add high-priority events
            self.priority.clear_queue()
            for event in temp_events:
                self.priority.add_event_to_queue(event)
            
            # Clear old history
            self.event_history.clear()
            
            logger.info(f"Emergency cleanup completed, {len(temp_events)} high-priority events retained")
            
        except Exception as e:
            logger.error(f"Error during emergency cleanup: {e}")
            # Last resort: clear everything
            self.priority.clear_queue()
            self.event_history.clear()
    
    def get_event_statistics(self) -> Dict[str, Any]:
        """Get event processing statistics."""
        try:
            current_time = time.time()
            uptime = current_time - self._start_time
            
            return {
                'total_events_processed': self._event_count,
                'events_in_queue': self.priority.get_queue_size(),
                'events_in_history': len(self.event_history),
                'uptime_seconds': uptime,
                'events_per_second': self._event_count / uptime if uptime > 0 else 0,
                'registered_handlers': sum(len(handlers) for handlers in self.event_handlers.values()),
                'event_types_handled': len(self.event_handlers)
            }
            
        except Exception as e:
            logger.error(f"Error getting event statistics: {e}")
            return {'error': str(e)}
    
    def clear_event_queue(self):
        """Clear all events from the queue."""
        try:
            self.priority.clear_queue()
            self.event_history.clear()
            logger.info("Event queue and history cleared")
            
        except Exception as e:
            logger.error(f"Error clearing event queue: {e}")
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get detailed queue status."""
        try:
            return {
                'queue_size': self.priority.get_queue_size(),
                'is_empty': self.priority.is_queue_empty(),
                'event_counter': self._event_counter,
                'total_events': self._event_count,
                'uptime': time.time() - self._start_time
            }
        except Exception as e:
            logger.error(f"Error getting queue status: {e}")
            return {'error': str(e)}
    
    def has_pending_events(self) -> bool:
        """Check if there are pending events in the queue."""
        return self.priority.has_pending_events()
    
    def register_handler(self, event_type: EventType, handler: Callable):
        """Register an event handler for a specific event type."""
        try:
            if event_type not in self.event_handlers:
                self.event_handlers[event_type] = []
            self.event_handlers[event_type].append(handler)
            logger.debug(f"Registered handler for {event_type.name}")
        except Exception as e:
            logger.error(f"Error registering handler: {e}")
    
    def unregister_handler(self, event_type: EventType, handler: Callable):
        """Unregister an event handler."""
        try:
            if event_type in self.event_handlers:
                if handler in self.event_handlers[event_type]:
                    self.event_handlers[event_type].remove(handler)
                    logger.debug(f"Unregistered handler for {event_type.name}")
        except Exception as e:
            logger.error(f"Error unregistering handler: {e}")
    
    def get_queue_health(self) -> Dict[str, Any]:
        """Get queue health information."""
        try:
            current_size = self.priority.get_queue_size()
            return {
                'queue_size': current_size,
                'max_size': self.MAX_QUEUE_SIZE,
                'utilization_percent': (current_size / self.MAX_QUEUE_SIZE) * 100,
                'is_healthy': current_size < self.MAX_QUEUE_SIZE * 0.8,
                'needs_cleanup': current_size > self.MAX_QUEUE_SIZE * 0.9,
                'history_size': len(self.event_history),
                'max_history': self.MAX_HISTORY_SIZE
            }
        except Exception as e:
            logger.error(f"Error getting queue health: {e}")
            return {'error': str(e)}
    
    def cleanup(self):
        """Cleanup event queue processor resources."""
        try:
            self.priority.cleanup()
            self.clear_event_queue()
            self.event_handlers.clear()
            logger.info("EventProcessorQueue cleaned up")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")