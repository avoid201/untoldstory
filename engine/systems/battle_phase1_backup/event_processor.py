"""
Event Processor - Enhanced with Deduplication & Performance
==========================================================
Optimized event system with hash-based deduplication and memory management.
"""

import logging
from typing import List, Dict, Any, Optional, Callable, TYPE_CHECKING
import heapq
import time
import hashlib

if TYPE_CHECKING:
    from engine.systems.battle.battle_state import BattleState

from engine.systems.battle.events.event_types import EventType, BattleEvent

logger = logging.getLogger(__name__)


class EventProcessor:
    """
    Enhanced EventProcessor with advanced deduplication and performance monitoring.
    """
    
    MAX_QUEUE_SIZE = 100
    MAX_HISTORY_SIZE = 50
    MAX_HASH_CACHE = 1000
    CLEANUP_INTERVAL = 10  # Cleanup every 10 events
    COOLDOWN_DURATION = 0.1  # 100ms cooldown for same event type
    
    def __init__(self, battle_state: 'BattleState'):
        """Initialize event processor with enhanced management."""
        self.state = battle_state
        self.event_handlers: Dict[EventType, List[Callable]] = {}
        self.event_history: List[BattleEvent] = []
        self.processing = False
        
        # Enhanced queue management
        self._event_queue = []
        self._event_counter = 0
        self._last_event_key = None
        
        # Hash-based deduplication
        self._event_history_hash = set()
        self._event_cooldowns = {}  # Event-Type Cooldowns
        
        # Performance monitoring
        self._event_count = 0
        self._duplicate_count = 0
        self._start_time = time.time()
        self._last_cleanup = time.time()
        
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
    
    def _create_event_hash(self, event: BattleEvent) -> str:
        """Erstelle eindeutigen Hash für Event-Deduplication."""
        # Create hash from event type, actor, target, and value
        hash_data = f"{event.event_type.name}:{event.data.get('actor', '')}:{event.data.get('target', '')}:{event.data.get('value', '')}:{event.data.get('damage', '')}"
        return hashlib.md5(hash_data.encode()).hexdigest()[:16]
    
    def _is_on_cooldown(self, event_type: EventType) -> bool:
        """Check if event type is on cooldown."""
        current_time = time.time()
        if event_type in self._event_cooldowns:
            if current_time - self._event_cooldowns[event_type] < self.COOLDOWN_DURATION:
                return True
        self._event_cooldowns[event_type] = current_time
        return False
    
    def emit_event(self, event_or_type, data: Optional[Dict[str, Any]] = None) -> bool:
        """
        Emit an event with enhanced deduplication and queue limits.
        
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
            
            # Check cooldown (verhindert Spam)
            if self._is_on_cooldown(event.event_type):
                logger.debug(f"[COOLDOWN] Event {event.event_type.name} on cooldown, skipped")
                return False
            
            # Enhanced deduplication check
            event_hash = self._create_event_hash(event)
            if event_hash in self._event_history_hash:
                self._duplicate_count += 1
                logger.debug(f"[DUPLICATE BLOCKED] {event_hash[:8]}... - {event.event_type.name}")
                return False
            
            # Add to history with automatic cleanup
            self._event_history_hash.add(event_hash)
            if len(self._event_history_hash) > self.MAX_HASH_CACHE:
                # Keep only last 500 hashes
                self._event_history_hash = set(list(self._event_history_hash)[-500:])
            
            # Auto-cleanup check
            current_time = time.time()
            if current_time - self._last_cleanup > self.CLEANUP_INTERVAL:
                self._auto_cleanup()
                self._last_cleanup = current_time
            
            # Queue size limit enforcement
            if len(self._event_queue) >= self.MAX_QUEUE_SIZE - 10:
                self._cleanup_old_events()
            
            logger.debug(f"[EVENT] Emitting {event.event_type.name}")
            self._event_count += 1
            
            if not self.processing:
                self._event_counter += 1
                heapq.heappush(self._event_queue, (-event.priority, self._event_counter, event))
                
                if len(self.event_history) > self.MAX_HISTORY_SIZE:
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
    
    def _auto_cleanup(self) -> None:
        """Automatisches Memory Cleanup."""
        try:
            # Queue Cleanup
            if len(self._event_queue) > self.MAX_QUEUE_SIZE:
                # Behalte nur high-priority Events
                high_priority = [e for e in self._event_queue if e[0] < -5]
                self._event_queue = high_priority[:50]
                heapq.heapify(self._event_queue)
                logger.info(f"[CLEANUP] Queue cleanup: {len(self._event_queue)} events remaining")
            
            # History Cleanup
            if len(self.event_history) > self.MAX_HISTORY_SIZE:
                self.event_history = self.event_history[-25:]
            
            # Clear old cooldowns
            current_time = time.time()
            self._event_cooldowns = {
                k: v for k, v in self._event_cooldowns.items()
                if v > current_time
            }
            
            logger.debug(f"[CLEANUP] Memory optimized - Queue: {len(self._event_queue)}, History: {len(self.event_history)}")
            
        except Exception as e:
            logger.error(f"[CLEANUP ERROR] {e}")
    
    def _cleanup_old_events(self) -> None:
        """Clean up old events to prevent memory issues."""
        try:
            # Remove old events from history
            if len(self.event_history) > self.MAX_HISTORY_SIZE:
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
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Performance-Statistiken für Monitoring."""
        current_time = time.time()
        runtime = current_time - self._start_time
        
        return {
            'queue_size': len(self._event_queue),
            'history_size': len(self.event_history),
            'hash_cache_size': len(self._event_history_hash),
            'events_per_second': self._event_count / max(runtime, 1),
            'duplicate_rate': self._duplicate_count / max(self._event_count, 1),
            'memory_usage_mb': self._estimate_memory_usage() / 1024 / 1024,
            'total_events': self._event_count,
            'duplicates_blocked': self._duplicate_count,
            'runtime_seconds': runtime
        }
    
    def _estimate_memory_usage(self) -> int:
        """Schätze Memory Usage in Bytes."""
        try:
            import sys
            queue_size = sum(sys.getsizeof(event) for _, _, event in self._event_queue)
            history_size = sum(sys.getsizeof(event) for event in self.event_history)
            hash_size = len(self._event_history_hash) * 16  # MD5 hash size
            return queue_size + history_size + hash_size
        except:
            return 0
    
    def clear_events(self) -> None:
        """Clear all pending events."""
        self._event_queue.clear()
        self.event_history.clear()
        self._event_history_hash.clear()
        self._event_cooldowns.clear()
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
