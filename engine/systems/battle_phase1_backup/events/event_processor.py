"""
Event Processor - Emergency Facade
==================================
Minimal implementation to comply with 300-line limit.
"""

import logging
from typing import List, Dict, Any, Optional, Callable, TYPE_CHECKING
from .event_types import EventType, BattleEvent
from .event_queue import EventQueue

if TYPE_CHECKING:
    from engine.systems.battle.battle_state import BattleState

logger = logging.getLogger(__name__)


class EventProcessor:
    """EMERGENCY FACADE - Minimal EventProcessor implementation"""
    
    def __init__(self, battle_state: 'BattleState'):
        self.state = battle_state
        self.event_handlers: Dict[EventType, List[Callable]] = {}
        self.event_history: List[BattleEvent] = []
        self.processing = False
        self._event_queue = EventQueue(max_size=100)
        logger.info("EventProcessor initialized")
    
    def register_handler(self, event_type: EventType, handler: Callable) -> 'EventProcessor':
        """Register a handler for an event type."""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        
        self.event_handlers[event_type].append(handler)
        logger.info(f"Registered handler for {event_type.name}")
        return self
    
    def emit_event(self, event_or_type, data: Optional[Dict[str, Any]] = None) -> bool:
        """Emit an event."""
        try:
            if isinstance(event_or_type, BattleEvent):
                event = event_or_type
            else:
                event = BattleEvent(
                    event_type=event_or_type,
                    data=data or {}
                )
            
            # Add to queue
            if not self._event_queue.push(event):
                logger.warning("Event queue full, dropping event")
                return False
            
            # Call handlers
            if event.event_type in self.event_handlers:
                for handler in self.event_handlers[event.event_type]:
                    try:
                        handler(event)
                    except Exception as e:
                        logger.error(f"Handler failed: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to emit event: {e}")
            return False
    
    def process_events(self) -> List[Dict[str, Any]]:
        """Process all pending events."""
        if self.processing:
            return []
        
        self.processing = True
        ui_updates = []
        
        try:
            while not self._event_queue.is_empty():
                event = self._event_queue.pop()
                if event:
                    ui_updates.append({
                        'type': event.event_type.name,
                        'data': event.data,
                        'timestamp': 0.0
                    })
            
            return ui_updates
            
        except Exception as e:
            logger.error(f"Event processing failed: {e}")
            return []
        finally:
            self.processing = False
