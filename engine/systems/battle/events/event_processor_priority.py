"""
Event Processor Priority - Event Priority Management
===================================================
Event priority management and queue operations.
Split from event_processor_queue.py to comply with 300-line limit.
"""

import logging
from typing import List, Dict, Any, Optional, Callable, TYPE_CHECKING
import heapq
import time

if TYPE_CHECKING:
    from engine.systems.battle.battle_state import BattleState

from engine.systems.battle.events.event_types import EventType, BattleEvent

logger = logging.getLogger(__name__)


class EventProcessorPriority:
    """
    Event priority management functionality.
    Handles event priority calculation and queue operations.
    """
    
    def __init__(self, battle_state: 'BattleState'):
        """Initialize event priority processor."""
        self.state = battle_state
        self._event_queue = []
        self._event_counter = 0
        logger.info("EventProcessorPriority initialized")
    
    def _get_event_priority(self, event_type: EventType) -> int:
        """Get priority for event type (lower number = higher priority)."""
        priority_map = {
            # Critical battle events (highest priority)
            EventType.BATTLE_END: 1,
            EventType.MONSTER_FAINTED: 2,
            EventType.DAMAGE_DEALT: 3,
            EventType.HP_BAR_UPDATE: 4,
            
            # UI and messaging events
            EventType.MESSAGE_SHOW: 5,
            EventType.ANIMATION_PLAY: 6,
            EventType.MENU_OPEN: 7,
            EventType.MENU_CLOSE: 8,
            
            # Action events
            EventType.ACTION_ANNOUNCE: 9,
            EventType.ACTION_START: 10,
            EventType.ACTION_EXECUTE: 11,
            EventType.ACTION_END: 12,
            EventType.ACTION_COMPLETE: 13,
            
            # Turn and phase events
            EventType.TURN_START: 14,
            EventType.TURN_END: 15,
            EventType.PHASE_CHANGE: 16,
            EventType.BATTLE_START: 17,
            
            # Status and stat events
            EventType.STATUS_APPLIED: 18,
            EventType.STAT_CHANGE: 19,
            EventType.LEVEL_UP: 20,
            
            # Combat mechanics
            EventType.CRITICAL_HIT: 21,
            EventType.SUPER_EFFECTIVE: 22,
            EventType.NOT_EFFECTIVE: 23,
            EventType.NOT_VERY_EFFECTIVE: 24,
            EventType.NO_EFFECT: 25,
            EventType.IMMUNE: 26,
            EventType.MISS: 27,
            EventType.DODGE: 28,
            EventType.BLOCK: 29,
            EventType.REFLECT: 30,
            EventType.ABSORB: 31,
            
            # Monster events
            EventType.MONSTER_SWITCH: 32,
            EventType.HEAL: 33,
            EventType.REVIVE: 34,
            EventType.TRANSFORM: 35,
            EventType.COPY: 36,
            EventType.STEAL: 37,
            EventType.SWAP: 38,
            EventType.TRAP: 39,
            EventType.SEAL: 40,
            EventType.UNSEAL: 41,
            
            # Special moves and abilities
            EventType.CHARGE: 42,
            EventType.DISCHARGE: 43,
            EventType.SUMMON: 44,
            EventType.BANISH: 45,
            
            # Battle actions
            EventType.ESCAPE_ATTEMPT: 46,
            EventType.ITEM_USE: 47,
            EventType.TAME_ATTEMPT: 48,
            
            # Dialog events
            EventType.DIALOG_SHOW: 49,
            EventType.DIALOG_CHOICE: 50,
            
            # Weather and terrain
            EventType.WEATHER_EFFECT: 51,
            EventType.TERRAIN_EFFECT: 52,
            
            # Wait events
            EventType.WAIT: 53,
            EventType.WAIT_FOR_INPUT: 54,
            EventType.WAIT_FOR_ANIMATION: 55,
            
            # Energy management events (lower priority)
            EventType.ACCUMULATE: 60,
            EventType.RELEASE: 61,
            EventType.STORE: 62,
            EventType.RETRIEVE: 63,
            EventType.CREATE: 64,
            EventType.DESTROY: 65,
            EventType.CALL: 66,
            EventType.DISMISS: 67,
            EventType.INVOKE: 68,
            EventType.EVOKE: 69,
            EventType.MANIFEST: 70,
            EventType.DEMANIFEST: 71,
            EventType.MATERIALIZE: 72,
            EventType.DEMATERIALIZE: 73,
            EventType.INCARNATE: 74,
            EventType.EXCARNATE: 75,
            EventType.EMBODY: 76,
            EventType.DISEMBODY: 77,
            EventType.INSTANTIATE: 78,
            EventType.DEINSTANTIATE: 79,
            EventType.REALIZE: 80,
            EventType.UNREALIZE: 81,
            EventType.ACTUALIZE: 82,
            EventType.DEACTUALIZE: 83,
            EventType.CONCRETIZE: 84,
            EventType.ABSTRACIZE: 85,
            EventType.SOLIDIFY: 86,
            EventType.LIQUEFY: 87,
            EventType.GASIFY: 88,
            EventType.PLASMAFY: 89,
            EventType.CRYSTALLIZE: 90,
            EventType.AMORPHIZE: 91,
            EventType.ORGANIZE: 92,
            EventType.DISORGANIZE: 93,
            EventType.STRUCTURE: 94,
            EventType.DESTRUCTURE: 95,
            EventType.FORM: 96,
            EventType.DEFORM: 97,
            EventType.SHAPE: 98,
            EventType.UNSHAPE: 99,
            EventType.MOLD: 100,
            EventType.UNMOLD: 101,
            EventType.CRAFT: 102,
            EventType.UNCRAFT: 103,
            EventType.BUILD: 104,
            EventType.UNBUILD: 105,
            EventType.CONSTRUCT: 106,
            EventType.DECONSTRUCT: 107,
            EventType.ASSEMBLE: 108,
            EventType.DISASSEMBLE: 109,
            EventType.COMPOSE: 110,
            EventType.DECOMPOSE: 111,
            EventType.SYNTHESIZE: 112,
            EventType.ANALYZE: 113,
            EventType.SCAN: 114,
            EventType.PROBE: 115,
            EventType.EXAMINE: 116,
            EventType.INSPECT: 117,
            EventType.OBSERVE: 118,
            EventType.MONITOR: 119,
            EventType.TRACK: 120,
            EventType.TRACE: 121,
            EventType.FOLLOW: 122
        }
        
        return priority_map.get(event_type, 50)  # Default priority for unknown events
    
    def add_event_to_queue(self, event: BattleEvent) -> bool:
        """Add event to priority queue."""
        try:
            priority = self._get_event_priority(event.event_type)
            heapq.heappush(self._event_queue, (priority, self._event_counter, event))
            self._event_counter += 1
            return True
        except Exception as e:
            logger.error(f"Error adding event to queue: {e}")
            return False
    
    def get_next_event(self) -> Optional[BattleEvent]:
        """Get next event from priority queue."""
        try:
            if not self._event_queue:
                return None
            
            priority, event_id, event = heapq.heappop(self._event_queue)
            return event
        except Exception as e:
            logger.error(f"Error getting next event: {e}")
            return None
    
    def peek_next_event(self) -> Optional[BattleEvent]:
        """Peek at next event without removing it."""
        try:
            if not self._event_queue:
                return None
            
            priority, event_id, event = self._event_queue[0]
            return event
        except Exception as e:
            logger.error(f"Error peeking at next event: {e}")
            return None
    
    def get_queue_size(self) -> int:
        """Get current queue size."""
        return len(self._event_queue)
    
    def is_queue_empty(self) -> bool:
        """Check if queue is empty."""
        return len(self._event_queue) == 0
    
    def clear_queue(self):
        """Clear the event queue."""
        try:
            self._event_queue.clear()
            self._event_counter = 0
            logger.info("Event queue cleared")
        except Exception as e:
            logger.error(f"Error clearing queue: {e}")
    
    def get_queue_statistics(self) -> Dict[str, Any]:
        """Get queue statistics."""
        try:
            return {
                'queue_size': len(self._event_queue),
                'event_counter': self._event_counter,
                'is_empty': self.is_queue_empty()
            }
        except Exception as e:
            logger.error(f"Error getting queue statistics: {e}")
            return {'error': str(e)}
    
    def get_priority_breakdown(self) -> Dict[str, int]:
        """Get priority breakdown for all event types."""
        try:
            breakdown = {}
            for event_type in EventType:
                priority = self._get_event_priority(event_type)
                breakdown[event_type.name] = priority
            return breakdown
        except Exception as e:
            logger.error(f"Error getting priority breakdown: {e}")
            return {}
    
    def has_pending_events(self) -> bool:
        """Check if there are pending events in the queue."""
        return len(self._event_queue) > 0
    
    def cleanup(self):
        """Cleanup event priority processor resources."""
        try:
            self.clear_queue()
            logger.info("EventProcessorPriority cleaned up")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
