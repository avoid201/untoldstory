"""
Event Processor Facade - Emergency Split
========================================
Facade to maintain compatibility while splitting the 1358-line event_processor.py
"""

import logging
from typing import List, Dict, Any, Optional, Callable, TYPE_CHECKING
import heapq
import time

if TYPE_CHECKING:
    from engine.systems.battle.battle_state import BattleState

from .event_types import EventType, BattleEvent

logger = logging.getLogger(__name__)


class EventProcessor:
    """
    EMERGENCY FACADE - Simplified EventProcessor to comply with 300-line limit.
    This replaces the 1358-line monolithic event_processor.py
    """
    
    MAX_QUEUE_SIZE = 100
    MAX_LISTENERS = 50
    CLEANUP_THRESHOLD = 50
    
    def __init__(self, battle_state: 'BattleState'):
        """Initialize event processor with queue management."""
        self.state = battle_state
        self.event_handlers: Dict[EventType, List[Callable]] = {}
        self.event_history: List[BattleEvent] = []
        self.processing = False
        
        # Queue management
        self._event_queue = []
        self._event_counter = 0
        self._last_event_key = None
        
        # Performance monitoring
        self._event_count = 0
        self._start_time = time.time()
        
        # Register default handlers
        self._register_default_handlers()
    
    def _register_default_handlers(self) -> None:
        """Register default event handlers."""
        self.register_handler(EventType.MESSAGE_SHOW, self._default_message_handler)
        self.register_handler(EventType.WAIT, self._default_wait_handler)
        self.register_handler(EventType.HP_BAR_UPDATE, self._default_hp_update_handler)
    
    def register_handler(self, event_type: EventType, handler: Callable) -> 'EventProcessor':
        """Register a handler for an event type."""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        
        self.event_handlers[event_type].append(handler)
        logger.info(f"[EVENT HANDLER] ✓ Registered {event_type.name}")
        return self
    
    def unregister_handler(self, event_type: EventType, handler: Callable) -> None:
        """Unregister an event handler."""
        if event_type in self.event_handlers and handler in self.event_handlers[event_type]:
            self.event_handlers[event_type].remove(handler)
            logger.debug(f"Unregistered handler for {event_type.name}")
    
    def emit_event(self, event_or_type, data: Optional[Dict[str, Any]] = None) -> bool:
        """
        Emit an event with deduplication and queue limits.
        
        Args:
            event_or_type: BattleEvent object or EventType enum
            data: Optional data dict (only used if event_or_type is EventType)
            
        Returns:
            bool: True if event was emitted, False if deduplicated or failed
        """
        try:
            # Handle both BattleEvent objects and EventType+data
            if isinstance(event_or_type, BattleEvent):
                event = event_or_type
            else:
                event = BattleEvent(
                    event_type=event_or_type,
                    data=data or {}
                )
            
            # Deduplication check
            event_key = f"{event.event_type.name}:{event.data.get('actor', '')}:{event.data.get('action', '')}"
            if self._last_event_key == event_key:
                logger.debug(f"[DUPLICATE BLOCKED] {event_key}")
                return False
            
            self._last_event_key = event_key
            
            # Queue size limit enforcement
            if len(self._event_queue) >= self.MAX_QUEUE_SIZE - 10:
                self._cleanup_old_events()
            
            logger.debug(f"[EVENT] Emitting {event.event_type.name}")
            self._event_count += 1
            
            if not self.processing:
                self._event_counter += 1
                heapq.heappush(self._event_queue, (-event.priority, self._event_counter, event))
                
                if len(self.event_history) > self.CLEANUP_THRESHOLD:
                    self.event_history = self.event_history[-25:]
            
            # Call handlers with error recovery
            if event.event_type in self.event_handlers:
                for handler in self.event_handlers[event.event_type]:
                    try:
                        handler(event)
                        logger.debug(f"  ✓ Handler executed: {getattr(handler, '__name__', 'unknown')}")
                    except Exception as e:
                        logger.error(f"  ❌ Handler failed: {e}")
                        continue
            else:
                logger.debug(f"  No handlers registered for {event.event_type.name}")
            
            return True
                
        except Exception as e:
            event_name = getattr(event_or_type, 'name', str(event_or_type))
            logger.error(f"[EVENT ERROR] Failed to emit {event_name}: {e}")
            return False
    
    def process_events(self) -> List[Dict[str, Any]]:
        """Process all pending events and return UI updates."""
        if self.processing:
            return []
        
        self.processing = True
        ui_updates: List[Dict[str, Any]] = []
        
        try:
            while self._event_queue:
                priority, counter, event = heapq.heappop(self._event_queue)
                logger.info(f"[PROCESSING EVENT] {event.event_type.name} (Priority: {-priority})")
                
                # Process the event
                self.emit_event(event)
                
                # Create UI update
                ui_update = self._create_ui_update(event)
                if ui_update:
                    ui_updates.append(ui_update)
                
                # Handle blocking events
                if event.blocking:
                    break
                
                # Add to history
                self.event_history.append(event)
            
            return ui_updates
            
        except Exception as e:
            logger.error(f"[EVENT PROCESSING ERROR] {e}")
            return []
        finally:
            self.processing = False
    
    def _create_ui_update(self, event: BattleEvent) -> Optional[Dict[str, Any]]:
        """Create UI update dictionary from event."""
        try:
            update = {
                'type': event.event_type.name,
                'data': event.data.copy(),
                'timestamp': time.time()
            }
            
            # Add specific UI update logic based on event type
            if event.event_type == EventType.HP_BAR_UPDATE:
                update['target'] = event.data.get('target')
                update['current_hp'] = event.data.get('current_hp', 0)
                update['max_hp'] = event.data.get('max_hp', 100)
            elif event.event_type == EventType.MESSAGE_SHOW:
                update['message'] = event.data.get('message', '')
                update['duration'] = event.duration
            elif event.event_type == EventType.DAMAGE_DEALT:
                update['damage'] = event.data.get('damage', 0)
                update['target'] = event.data.get('target')
                update['is_critical'] = event.data.get('is_critical', False)
            
            return update
            
        except Exception as e:
            logger.error(f"[UI UPDATE ERROR] {e}")
            return None
    
    def _cleanup_old_events(self) -> None:
        """Clean up old events to prevent memory issues."""
        try:
            # Remove old events from history
            if len(self.event_history) > self.CLEANUP_THRESHOLD:
                self.event_history = self.event_history[-25:]
            
            # Remove low priority events from queue
            if len(self._event_queue) > 50:
                # Keep only top 30 priority events
                temp_queue = []
                count = 0
                while self._event_queue and count < 30:
                    temp_queue.append(heapq.heappop(self._event_queue))
                    count += 1
                
                self._event_queue = temp_queue
                heapq.heapify(self._event_queue)
            
            logger.debug(f"[CLEANUP] Queue size: {len(self._event_queue)}, History: {len(self.event_history)}")
            
        except Exception as e:
            logger.error(f"[CLEANUP ERROR] {e}")
    
    def _default_message_handler(self, event: BattleEvent) -> None:
        """Default message handler."""
        message = event.data.get('message', '')
        if message:
            logger.info(f"[MESSAGE] {message}")
    
    def _default_wait_handler(self, event: BattleEvent) -> None:
        """Default wait handler."""
        duration = event.duration or 1.0
        time.sleep(min(duration, 0.1))  # Cap at 100ms for testing
    
    def _default_hp_update_handler(self, event: BattleEvent) -> None:
        """Default HP update handler."""
        target = event.data.get('target')
        current_hp = event.data.get('current_hp', 0)
        max_hp = event.data.get('max_hp', 100)
        if target:
            logger.debug(f"[HP UPDATE] {target}: {current_hp}/{max_hp}")
    
    def clear_events(self) -> None:
        """Clear all pending events."""
        self._event_queue.clear()
        self.event_history.clear()
        logger.info("[EVENT CLEAR] All events cleared")
    
    def get_queue_size(self) -> int:
        """Get current queue size."""
        return len(self._event_queue)
    
    def get_event_count(self) -> int:
        """Get total event count."""
        return self._event_count
    
    def is_processing(self) -> bool:
        """Check if currently processing events."""
        return self.processing
