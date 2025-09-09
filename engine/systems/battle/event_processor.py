"""
Event Processor für das Battle System.
Verwaltet nur Events und deren Verarbeitung - getrennt von der Battle-Logik.
"""

import logging
from typing import List, Dict, Any, Optional, Callable, TYPE_CHECKING
from dataclasses import dataclass, field
from enum import Enum, auto
import heapq
import time

if TYPE_CHECKING:
    from engine.systems.battle.battle_state import BattleState
    from engine.systems.monster_instance import MonsterInstance

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Types of battle events."""
    # Phase transitions
    BATTLE_START = auto()
    PHASE_CHANGE = auto()
    TURN_START = auto()
    TURN_END = auto()
    BATTLE_END = auto()
    
    # Action events
    ACTION_ANNOUNCE = auto()
    ACTION_EXECUTE = auto()
    ACTION_COMPLETE = auto()
    
    # Combat events
    DAMAGE_DEALT = auto()
    HEALING_DONE = auto()
    STATUS_APPLIED = auto()
    STATUS_REMOVED = auto()
    STATUS_DAMAGE = auto()
    STAT_CHANGE = auto()
    
    # Monster events
    MONSTER_FAINTED = auto()
    MONSTER_REVIVED = auto()
    MONSTER_SWITCH = auto()
    MONSTER_APPEAR = auto()
    
    # Visual events
    ANIMATION_PLAY = auto()
    EFFECT_SHOW = auto()
    CAMERA_SHAKE = auto()
    SCREEN_FLASH = auto()
    
    # UI events
    MESSAGE_SHOW = auto()
    MENU_OPEN = auto()
    MENU_CLOSE = auto()
    HP_BAR_UPDATE = auto()
    
    # Special events
    CRITICAL_HIT = auto()
    MISS = auto()
    ESCAPE_ATTEMPT = auto()
    ITEM_USE = auto()
    TAME_ATTEMPT = auto()
    
    # Dialog events
    DIALOG_SHOW = auto()
    DIALOG_CHOICE = auto()
    
    # Weather/Terrain events
    WEATHER_EFFECT = auto()
    TERRAIN_EFFECT = auto()
    
    # Wait events
    WAIT = auto()
    WAIT_FOR_INPUT = auto()
    WAIT_FOR_ANIMATION = auto()


@dataclass
class BattleEvent:
    """Represents a single battle event."""
    event_type: EventType
    data: Dict[str, Any] = field(default_factory=dict)
    duration: float = 0.0  # Duration in seconds
    priority: int = 0  # Higher priority events process first
    blocking: bool = False  # Whether this event blocks others
    
    def __str__(self) -> str:
        """String representation."""
        return f"BattleEvent({self.event_type.name}, data={self.data})"
    
    def get(self, key, default=None):
        """Dict-like get method."""
        if key == 'message':
            return self.data.get('message', default)
        elif key == 'target':
            return self.data.get('target', default)
        elif key == 'damage':
            return self.data.get('damage', default)
        elif key == 'type':
            return self.event_type
        else:
            return self.data.get(key, default)
    
    def __getitem__(self, key):
        """Make BattleEvent subscriptable."""
        return self.get(key)


# UIUpdate class removed - using plain dictionaries instead


class EventProcessor:
    """Verwaltet nur Events und deren Verarbeitung"""
    
    def __init__(self, battle_state: 'BattleState'):
        """
        Initialize event processor.
        
        Args:
            battle_state: The battle state to process events for
        """
        self.state = battle_state
        self.event_handlers: Dict[EventType, List[Callable]] = {}
        self.event_history: List[BattleEvent] = []
        self.processing = False
        
        # Priority queue for efficient event processing
        self._event_queue = []
        self._event_counter = 0  # For stable sorting
        
        # Performance monitoring
        self._event_count = 0
        
        # Caching for performance optimization
        self._validation_cache = {}
        self._last_validation = 0
        self._cache_duration = 60  # Cache validation results for 60 seconds
        self._start_time = time.time()
        self._processing_times = []
        self._last_cleanup_time = time.time()
        
        # Register default handlers
        self._register_default_handlers()
    
    def _register_default_handlers(self) -> None:
        """Register default event handlers."""
        # These can be overridden by the UI layer
        self.register_handler(EventType.MESSAGE_SHOW, self._default_message_handler)
        self.register_handler(EventType.WAIT, self._default_wait_handler)
        self.register_handler(EventType.HP_BAR_UPDATE, self._default_hp_update_handler)
    
    def register_handler(self, event_type: EventType, handler: Callable) -> 'EventProcessor':
        """
        Register a handler for an event type with enhanced logging.
        
        Args:
            event_type: Type of event to handle
            handler: Function to call when event occurs
            
        Returns:
            Self for method chaining
        """
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        
        self.event_handlers[event_type].append(handler)
        
        # ENHANCED LOGGING:
        handler_name = getattr(handler, '__name__', str(handler))
        handler_count = len(self.event_handlers[event_type])
        
        # Better logging format
        logger.info(f"[EVENT HANDLER] ✓ Registered {event_type.name}")
        logger.info(f"  → Handler: {handler_name}")
        logger.info(f"  → Total handlers for {event_type.name}: {handler_count}")
        
        # Return for chaining
        return self
    
    def unregister_handler(self, event_type: EventType, handler: Callable) -> None:
        """Unregister an event handler."""
        if event_type in self.event_handlers and handler in self.event_handlers[event_type]:
            self.event_handlers[event_type].remove(handler)
            logger.debug(f"Unregistered handler for {event_type.name}")
    
    def emit_event(self, event_or_type, data: Optional[Dict[str, Any]] = None) -> None:
        """
        Emit event with error recovery.
        Supports both BattleEvent objects and EventType+data.
        
        Args:
            event_or_type: BattleEvent object or EventType enum
            data: Optional data dict (only used if event_or_type is EventType)
        """
        try:
            # Handle both BattleEvent objects and EventType+data
            if isinstance(event_or_type, BattleEvent):
                event = event_or_type
            else:
                # Create BattleEvent from EventType and data
                event = BattleEvent(
                    event_type=event_or_type,
                    data=data or {}
                )
            
            logger.debug(f"[EVENT] Emitting {event.event_type.name}")
            
            # Performance tracking
            self._event_count += 1
            
            if not self.processing:
                # Add to priority queue instead of simple list
                self._event_counter += 1
                # Use negative priority for max-heap behavior (higher priority first)
                heapq.heappush(self._event_queue, (-event.priority, self._event_counter, event))
                
                # AGGRESSIVE CLEANUP - Every 50 events for better performance
                if len(self.event_history) > 50:
                    self.event_history = self.event_history[-25:]
                    logger.debug(f"[AGGRESSIVE CLEANUP] Trimmed event history to 25 events")
                
                if len(self._event_queue) > 30:
                    # Keep only top priority events - AGGRESSIVE CLEANUP
                    self._compact_queue()
            
            # Call handlers with error recovery
            if event.event_type in self.event_handlers:
                for handler in self.event_handlers[event.event_type]:
                    try:
                        handler(event)
                        logger.debug(f"  ✓ Handler executed: {getattr(handler, '__name__', 'unknown')}")
                    except Exception as e:
                        # Don't crash on handler error
                        logger.error(f"  ❌ Handler failed: {e}")
                        continue
            else:
                logger.debug(f"  No handlers registered for {event.event_type.name}")
                
        except Exception as e:
            event_name = getattr(event_or_type, 'name', str(event_or_type))
            logger.error(f"[EVENT ERROR] Failed to emit {event_name}: {e}")
    
    def process_events(self) -> List[Dict[str, Any]]:
        """
        Process all pending events and return UI updates.
        
        Returns:
            List of UI update dictionaries to apply
        """
        if self.processing:
            return []
        
        self.processing = True
        ui_updates: List[Dict[str, Any]] = []
        processing_start = time.time()
        
        try:
            # CRITICAL: Use priority queue for efficient event processing
            while self._event_queue:
                # Get highest priority event (heapq returns min, so we use negative priority)
                priority, counter, event = heapq.heappop(self._event_queue)
                logger.info(f"[PROCESSING EVENT] {event.event_type.name} (Priority: {-priority}, Queue: {len(self._event_queue)} remaining)")
                
                # Process the event
                self.emit_event(event)
                
                # CRITICAL: Create UI update dict for EVERY event
                ui_update = self._create_ui_update(event)
                if ui_update:
                    ui_updates.append(ui_update)
                
                # CRITICAL: Handle blocking events correctly
                if event.blocking and event.duration > 0:
                    time.sleep(event.duration)
                
                # Add to history (cleanup already handled in emit_event)
                self.event_history.append(event)
        
        finally:
            self.processing = False
            
            # Track processing time
            processing_time = time.time() - processing_start
            self._processing_times.append(processing_time)
            
            # Keep only last 100 processing times for average calculation
            if len(self._processing_times) > 100:
                self._processing_times = self._processing_times[-100:]
        
        return ui_updates
    
    def _create_ui_update(self, event: BattleEvent) -> Optional[Dict[str, Any]]:
        """
        Create UI update dictionary with better mapping.
        
        Args:
            event: Event to convert
            
        Returns:
            UI update dictionary or None
        """
        # Enhanced mapping - ALL EventTypes covered
        ui_mapping = {
            # Phase transitions
            EventType.BATTLE_START: "battle_start",
            EventType.PHASE_CHANGE: "phase_change",
            EventType.TURN_START: "turn_start",
            EventType.TURN_END: "turn_end",
            EventType.BATTLE_END: "battle_end",
            
            # Action events
            EventType.ACTION_ANNOUNCE: "action_announce",
            EventType.ACTION_EXECUTE: "action_execute",
            EventType.ACTION_COMPLETE: "action_complete",
            
            # Combat events
            EventType.DAMAGE_DEALT: "damage",
            EventType.HEALING_DONE: "healing",
            EventType.STATUS_APPLIED: "status_change",
            EventType.STATUS_REMOVED: "status_change",
            EventType.STATUS_DAMAGE: "status_damage",
            EventType.STAT_CHANGE: "stat_change",
            
            # Monster events
            EventType.MONSTER_FAINTED: "monster_faint",
            EventType.MONSTER_REVIVED: "monster_revived",
            EventType.MONSTER_SWITCH: "monster_switch",
            EventType.MONSTER_APPEAR: "monster_appear",
            
            # Visual events
            EventType.ANIMATION_PLAY: "animation",
            EventType.EFFECT_SHOW: "effect_show",
            EventType.CAMERA_SHAKE: "camera_shake",
            EventType.SCREEN_FLASH: "screen_flash",
            
            # UI events
            EventType.MESSAGE_SHOW: "message",
            EventType.MENU_OPEN: "menu_open",
            EventType.MENU_CLOSE: "menu_close",
            EventType.HP_BAR_UPDATE: "hp_bar",
            
            # Special events
            EventType.CRITICAL_HIT: "critical",
            EventType.MISS: "miss",
            EventType.ESCAPE_ATTEMPT: "escape_attempt",
            EventType.ITEM_USE: "item_use",
            EventType.TAME_ATTEMPT: "tame_attempt",
            
            # Dialog events
            EventType.DIALOG_SHOW: "dialog_show",
            EventType.DIALOG_CHOICE: "dialog_choice",
            
            # Weather/Terrain events
            EventType.WEATHER_EFFECT: "weather_effect",
            EventType.TERRAIN_EFFECT: "terrain_effect",
            
            # Wait events
            EventType.WAIT: "wait",
            EventType.WAIT_FOR_INPUT: "wait_for_input",
            EventType.WAIT_FOR_ANIMATION: "wait_for_animation"
        }
        
        ui_type = ui_mapping.get(event.event_type, "generic")
        
        # Create dictionary with all necessary fields
        data = event.data.copy() if event.data else {}
        data['type'] = ui_type  # CRITICAL for UI
        data['priority'] = event.priority
        
        return data
    
    def clear_events(self) -> None:
        """Clear all pending events."""
        self._event_queue.clear()
        logger.debug("Cleared all pending events and priority queue")
    
    def cleanup_event_history(self, max_size: int = 100) -> None:
        """
        Clean up event history to prevent memory leaks.
        
        Args:
            max_size: Maximum number of events to keep in history (OPTIMIZED TO 100)
        """
        if len(self.event_history) > max_size:
            old_size = len(self.event_history)
            self.event_history = self.event_history[-50:]  # Keep last 50 events
            logger.info(f"[EVENT CLEANUP] Trimmed event history from {old_size} to {len(self.event_history)} events")
    
    def get_event_history(self, limit: int = 50) -> List[BattleEvent]:
        """
        Get recent event history.
        
        Args:
            limit: Maximum number of events to return
            
        Returns:
            List of recent events
        """
        return self.event_history[-limit:] if self.event_history else []
    
    def has_pending_events(self) -> bool:
        """
        Check if there are pending events.
        
        Returns:
            True if there are pending events
        """
        return bool(self._event_queue)
    
    def has_blocking_events(self) -> bool:
        """
        Check if there are blocking events pending.
        
        Returns:
            True if there are blocking events
        """
        # Check priority queue for blocking events
        return any(event.blocking for _, _, event in self._event_queue)
    
    # Default event handlers
    def _default_message_handler(self, event: BattleEvent) -> None:
        """Default handler for message events."""
        message = event.data.get('message', '')
        logger.info(f"Battle Message: {message}")
    
    def _default_wait_handler(self, event: BattleEvent) -> None:
        """Default handler for wait events."""
        if event.duration > 0:
            time.sleep(event.duration)
    
    def _default_hp_update_handler(self, event: BattleEvent) -> None:
        """Default handler for HP bar updates."""
        target = event.data.get('target')
        if target:
            # Use consistent attribute access
            target_name = getattr(target, 'name', 'Unknown')
            current_hp = getattr(target, 'current_hp', 0)
            max_hp = getattr(target, 'max_hp', 1)
            logger.debug(f"HP update for {target_name}: {current_hp}/{max_hp}")
    
    # Event Factory Methods
    def create_event(self, event_type: EventType, data: Dict[str, Any] = None, 
                    duration: float = 0.0, priority: int = 0, blocking: bool = False) -> BattleEvent:
        """
        Factory method to create BattleEvent objects.
        
        Args:
            event_type: Type of event
            data: Event data
            duration: Event duration
            priority: Event priority
            blocking: Whether event blocks others
            
        Returns:
            BattleEvent object
        """
        return BattleEvent(
            event_type=event_type,
            data=data or {},
            duration=duration,
            priority=priority,
            blocking=blocking
        )
    
    # Convenience methods for common events
    def emit_damage_event(self, target: 'MonsterInstance', damage: int, attacker: 'MonsterInstance') -> None:
        """Emit a damage event."""
        event = self.create_event(
            EventType.DAMAGE_DEALT,
            data={
                'target': target,
                'damage': damage,
                'attacker': attacker,
                'message': f"{target.name if hasattr(target, 'name') else 'Unknown'} erleidet {damage} Schaden!"
            },
            duration=0.5
        )
        self.emit_event(event)
    
    def emit_healing_event(self, target: 'MonsterInstance', healing: int) -> None:
        """Emit a healing event."""
        event = self.create_event(
            EventType.HEALING_DONE,
            data={
                'target': target,
                'healing': healing,
                'message': f"{target.name if hasattr(target, 'name') else 'Unknown'} wurde um {healing} geheilt!"
            },
            duration=0.5
        )
        self.emit_event(event)
    
    def emit_status_event(self, target: 'MonsterInstance', status: str, applied: bool = True) -> None:
        """Emit a status change event."""
        event_type = EventType.STATUS_APPLIED if applied else EventType.STATUS_REMOVED
        action = "erhielt" if applied else "wurde von"
        
        event = self.create_event(
            event_type,
            data={
                'target': target,
                'status': status,
                'message': f"{target.name if hasattr(target, 'name') else 'Unknown'} {action} {status}!"
            },
            duration=1.0
        )
        self.emit_event(event)
    
    def emit_faint_event(self, monster: 'MonsterInstance', team_type: str, position: int) -> None:
        """Emit a monster faint event."""
        event = self.create_event(
            EventType.MONSTER_FAINTED,
            data={
                'monster': monster,
                'team_type': team_type,
                'position': position,
                'message': f"{monster.name if hasattr(monster, 'name') else 'Unknown'} ist ohnmächtig geworden!"
            },
            duration=2.0,
            blocking=True
        )
        self.emit_event(event)
    
    def emit_phase_change_event(self, phase: str) -> None:
        """Emit a phase change event."""
        event = self.create_event(
            EventType.PHASE_CHANGE,
            data={'phase': phase},
            priority=10  # High priority for phase changes
        )
        self.emit_event(event)
    
    def emit_message_event(self, message: str, duration: float = 1.0) -> None:
        """Emit a message event."""
        event = self.create_event(
            EventType.MESSAGE_SHOW,
            data={'message': message},
            duration=duration
        )
        self.emit_event(event)
    
    def register_ui_handlers(self, ui_component) -> None:
        """Register all UI event handlers at once."""
        if not ui_component:
            logger.warning("No UI component provided for handler registration")
            return
        
        # Store UI component reference for named methods
        self._ui_component = ui_component
            
        # Map event types to named methods - NO LAMBDA FUNCTIONS
        handler_map = {
            # Core UI events
            EventType.MESSAGE_SHOW: self._handle_message_show,
            EventType.HP_BAR_UPDATE: self._handle_hp_bar_update,
            EventType.DAMAGE_DEALT: self._handle_damage_dealt,
            EventType.HEALING_DONE: self._handle_healing_done,
            EventType.STATUS_APPLIED: self._handle_status_applied,
            EventType.MONSTER_FAINTED: self._handle_monster_fainted,
            EventType.PHASE_CHANGE: self._handle_phase_change,
            EventType.TURN_START: self._handle_turn_start,
            EventType.TURN_END: self._handle_turn_end,
            
            # Action events - CRITICAL MISSING HANDLER ADDED
            EventType.ACTION_ANNOUNCE: self._handle_action_announce,
            EventType.ACTION_EXECUTE: self._handle_action_execute,
            EventType.ACTION_COMPLETE: self._handle_action_complete,
            
            # Additional critical events - MISSING HANDLERS ADDED
            EventType.STATUS_REMOVED: self._handle_status_removed,
            EventType.STATUS_DAMAGE: self._handle_status_damage,
            EventType.STAT_CHANGE: self._handle_stat_change,
            EventType.MONSTER_REVIVED: self._handle_monster_revived,
            EventType.ESCAPE_ATTEMPT: self._handle_escape_attempt,
            EventType.DIALOG_SHOW: self._handle_dialog_show,
            EventType.DIALOG_CHOICE: self._handle_dialog_choice,
            EventType.WEATHER_EFFECT: self._handle_weather_effect,
            EventType.TERRAIN_EFFECT: self._handle_terrain_effect,
            EventType.WAIT: self._handle_wait,
            
            # Visual effects
            EventType.ANIMATION_PLAY: self._handle_animation_play,
            EventType.CAMERA_SHAKE: self._handle_camera_shake,
            EventType.SCREEN_FLASH: self._handle_screen_flash,
            EventType.EFFECT_SHOW: self._handle_effect_show,
            
            # Menu events
            EventType.MENU_OPEN: self._handle_menu_open,
            EventType.MENU_CLOSE: self._handle_menu_close,
            
            # Special combat events
            EventType.CRITICAL_HIT: self._handle_critical_hit,
            EventType.MISS: self._handle_miss,
            
            # Monster events
            EventType.MONSTER_SWITCH: self._handle_monster_switch,
            EventType.MONSTER_APPEAR: self._handle_monster_appear,
            
            # Item/Tame events
            EventType.ITEM_USE: self._handle_item_use,
            EventType.TAME_ATTEMPT: self._handle_tame_attempt,
            
            # Wait events
            EventType.WAIT_FOR_INPUT: self._handle_wait_for_input,
            EventType.WAIT_FOR_ANIMATION: self._handle_wait_for_animation,
            
            # Battle lifecycle events - MISSING HANDLERS ADDED
            EventType.BATTLE_START: self._handle_battle_start,
            EventType.BATTLE_END: self._handle_battle_end,
        }
        
        # Register all handlers
        for event_type, handler in handler_map.items():
            self.register_handler(event_type, handler)
            
        logger.info(f"✓ Registered {len(handler_map)} UI event handlers")

    # Named UI Event Handlers - NO LAMBDA FUNCTIONS
    def _handle_message_show(self, event: BattleEvent) -> None:
        """Handle message show events."""
        if hasattr(self._ui_component, 'add_message'):
            self._ui_component.add_message(event.data.get('message', ''))
    
    def _handle_hp_bar_update(self, event: BattleEvent) -> None:
        """Handle HP bar update events."""
        if hasattr(self._ui_component, 'update_hp_bar'):
            self._ui_component.update_hp_bar(event.data.get('target'))
    
    def _handle_damage_dealt(self, event: BattleEvent) -> None:
        """Handle damage dealt events."""
        if hasattr(self._ui_component, 'show_damage_number'):
            self._ui_component.show_damage_number(
                event.data.get('target'), 
                event.data.get('damage', 0), 
                event.data.get('is_critical', False)
            )
    
    def _handle_healing_done(self, event: BattleEvent) -> None:
        """Handle healing done events."""
        if hasattr(self._ui_component, 'show_healing_number'):
            self._ui_component.show_healing_number(
                event.data.get('target'), 
                event.data.get('healing', 0)
            )
    
    def _handle_status_applied(self, event: BattleEvent) -> None:
        """Handle status applied events."""
        if hasattr(self._ui_component, 'show_status_effect'):
            self._ui_component.show_status_effect(
                event.data.get('target'), 
                event.data.get('status')
            )
    
    def _handle_monster_fainted(self, event: BattleEvent) -> None:
        """Handle monster fainted events."""
        if hasattr(self._ui_component, 'play_faint_animation'):
            self._ui_component.play_faint_animation(event.data.get('monster'))
    
    def _handle_phase_change(self, event: BattleEvent) -> None:
        """Handle phase change events."""
        if hasattr(self._ui_component, '_handle_phase_change'):
            self._ui_component._handle_phase_change(event.data)
    
    def _handle_turn_start(self, event: BattleEvent) -> None:
        """Handle turn start events."""
        if hasattr(self._ui_component, 'waiting_for_input'):
            self._ui_component.waiting_for_input = True
    
    def _handle_turn_end(self, event: BattleEvent) -> None:
        """Handle turn end events."""
        if hasattr(self._ui_component, 'waiting_for_input'):
            self._ui_component.waiting_for_input = False
    
    def _handle_animation_play(self, event: BattleEvent) -> None:
        """Handle animation play events."""
        if hasattr(self._ui_component, 'play_animation'):
            self._ui_component.play_animation(
                event.data.get('animation_type'), 
                event.data.get('target')
            )
    
    def _handle_camera_shake(self, event: BattleEvent) -> None:
        """Handle camera shake events."""
        if hasattr(self._ui_component, 'shake_camera'):
            self._ui_component.shake_camera(
                event.data.get('intensity', 1.0), 
                event.data.get('duration', 0.5)
            )
    
    def _handle_screen_flash(self, event: BattleEvent) -> None:
        """Handle screen flash events."""
        if hasattr(self._ui_component, 'flash_screen'):
            self._ui_component.flash_screen(
                event.data.get('color', (255, 255, 255)), 
                event.data.get('duration', 0.3)
            )
    
    def _handle_effect_show(self, event: BattleEvent) -> None:
        """Handle effect show events."""
        if hasattr(self._ui_component, 'show_effect'):
            self._ui_component.show_effect(
                event.data.get('effect_type'), 
                event.data.get('position')
            )
    
    def _handle_menu_open(self, event: BattleEvent) -> None:
        """Handle menu open events."""
        if hasattr(self._ui_component, 'open_menu'):
            self._ui_component.open_menu(event.data.get('menu_type'))
    
    def _handle_menu_close(self, event: BattleEvent) -> None:
        """Handle menu close events."""
        if hasattr(self._ui_component, 'close_menu'):
            self._ui_component.close_menu()
    
    def _handle_critical_hit(self, event: BattleEvent) -> None:
        """Handle critical hit events."""
        if hasattr(self._ui_component, 'show_critical_effect'):
            self._ui_component.show_critical_effect(event.data.get('target'))
    
    def _handle_miss(self, event: BattleEvent) -> None:
        """Handle miss events."""
        if hasattr(self._ui_component, 'show_miss_effect'):
            self._ui_component.show_miss_effect(event.data.get('target'))
    
    def _handle_monster_switch(self, event: BattleEvent) -> None:
        """Handle monster switch events."""
        if hasattr(self._ui_component, 'show_switch_animation'):
            self._ui_component.show_switch_animation(
                event.data.get('old_monster'), 
                event.data.get('new_monster')
            )
    
    def _handle_monster_appear(self, event: BattleEvent) -> None:
        """Handle monster appear events."""
        if hasattr(self._ui_component, 'show_appear_animation'):
            self._ui_component.show_appear_animation(event.data.get('monster'))
    
    def _handle_item_use(self, event: BattleEvent) -> None:
        """Handle item use events."""
        if hasattr(self._ui_component, 'show_item_effect'):
            self._ui_component.show_item_effect(
                event.data.get('item'), 
                event.data.get('target')
            )
    
    def _handle_tame_attempt(self, event: BattleEvent) -> None:
        """Handle tame attempt events."""
        if hasattr(self._ui_component, 'show_tame_animation'):
            self._ui_component.show_tame_animation(event.data.get('target'))
    
    def _handle_wait_for_input(self, event: BattleEvent) -> None:
        """Handle wait for input events."""
        if hasattr(self._ui_component, 'waiting_for_input'):
            self._ui_component.waiting_for_input = True
    
    def _handle_wait_for_animation(self, event: BattleEvent) -> None:
        """Handle wait for animation events."""
        if hasattr(self._ui_component, 'wait_for_animation'):
            self._ui_component.wait_for_animation(event.data.get('duration', 1.0))
    
    # Action Event Handlers - CRITICAL MISSING HANDLERS ADDED
    def _handle_action_announce(self, event: BattleEvent) -> None:
        """Handle action announce events."""
        if hasattr(self._ui_component, 'show_action_announcement'):
            self._ui_component.show_action_announcement(event.data.get('action_name', ''))
        else:
            # Fallback: show as message
            action_name = event.data.get('action_name', 'Aktion')
            logger.debug(f"Action announced: {action_name}")
    
    def _handle_action_execute(self, event: BattleEvent) -> None:
        """Handle action execute events."""
        if hasattr(self._ui_component, 'show_action_execution'):
            self._ui_component.show_action_execution(event.data.get('action_data', {}))
        else:
            # Fallback: show as message
            action_data = event.data.get('action_data', {})
            logger.debug(f"Action executing: {action_data}")
    
    def _handle_action_complete(self, event: BattleEvent) -> None:
        """Handle action complete events - CRITICAL MISSING HANDLER."""
        if hasattr(self._ui_component, 'show_action_completion'):
            self._ui_component.show_action_completion(event.data.get('action_result', {}))
        else:
            # Fallback: show as message
            action_result = event.data.get('action_result', {})
            logger.debug(f"Action completed: {action_result}")
    
    # Additional Critical Event Handlers - MISSING HANDLERS ADDED
    def _handle_status_removed(self, event: BattleEvent) -> None:
        """Handle status removed events."""
        if hasattr(self._ui_component, 'show_status_removal'):
            self._ui_component.show_status_removal(
                event.data.get('target'), 
                event.data.get('status')
            )
        else:
            logger.debug(f"Status removed: {event.data.get('status', 'Unknown')}")
    
    def _handle_status_damage(self, event: BattleEvent) -> None:
        """Handle status damage events."""
        if hasattr(self._ui_component, 'show_status_damage'):
            self._ui_component.show_status_damage(
                event.data.get('target'), 
                event.data.get('damage', 0),
                event.data.get('status')
            )
        else:
            logger.debug(f"Status damage: {event.data.get('damage', 0)}")
    
    def _handle_stat_change(self, event: BattleEvent) -> None:
        """Handle stat change events."""
        if hasattr(self._ui_component, 'show_stat_change'):
            self._ui_component.show_stat_change(
                event.data.get('target'), 
                event.data.get('stat'),
                event.data.get('change', 0)
            )
        else:
            logger.debug(f"Stat change: {event.data.get('stat', 'Unknown')} by {event.data.get('change', 0)}")
    
    def _handle_monster_revived(self, event: BattleEvent) -> None:
        """Handle monster revived events."""
        if hasattr(self._ui_component, 'show_revive_animation'):
            self._ui_component.show_revive_animation(event.data.get('monster'))
        else:
            logger.debug(f"Monster revived: {event.data.get('monster', 'Unknown')}")
    
    def _handle_escape_attempt(self, event: BattleEvent) -> None:
        """Handle escape attempt events."""
        if hasattr(self._ui_component, 'show_escape_attempt'):
            self._ui_component.show_escape_attempt(event.data.get('success', False))
        else:
            logger.debug(f"Escape attempt: {event.data.get('success', False)}")
    
    def _handle_dialog_show(self, event: BattleEvent) -> None:
        """Handle dialog show events."""
        if hasattr(self._ui_component, 'show_dialog'):
            self._ui_component.show_dialog(event.data.get('text', ''))
        else:
            logger.debug(f"Dialog shown: {event.data.get('text', '')}")
    
    def _handle_dialog_choice(self, event: BattleEvent) -> None:
        """Handle dialog choice events."""
        if hasattr(self._ui_component, 'show_dialog_choice'):
            self._ui_component.show_dialog_choice(event.data.get('choices', []))
        else:
            logger.debug(f"Dialog choice: {event.data.get('choices', [])}")
    
    def _handle_weather_effect(self, event: BattleEvent) -> None:
        """Handle weather effect events."""
        if hasattr(self._ui_component, 'show_weather_effect'):
            self._ui_component.show_weather_effect(
                event.data.get('weather_type'),
                event.data.get('intensity', 1.0)
            )
        else:
            logger.debug(f"Weather effect: {event.data.get('weather_type', 'Unknown')}")
    
    def _handle_terrain_effect(self, event: BattleEvent) -> None:
        """Handle terrain effect events."""
        if hasattr(self._ui_component, 'show_terrain_effect'):
            self._ui_component.show_terrain_effect(
                event.data.get('terrain_type'),
                event.data.get('effect')
            )
        else:
            logger.debug(f"Terrain effect: {event.data.get('terrain_type', 'Unknown')}")
    
    def _handle_wait(self, event: BattleEvent) -> None:
        """Handle wait events."""
        if hasattr(self._ui_component, 'wait'):
            self._ui_component.wait(event.data.get('duration', 1.0))
        else:
            logger.debug(f"Wait: {event.data.get('duration', 1.0)} seconds")
    
    # Battle Lifecycle Event Handlers - MISSING HANDLERS ADDED
    def _handle_battle_start(self, event: BattleEvent) -> None:
        """Handle battle start events."""
        if hasattr(self._ui_component, 'show_battle_start'):
            self._ui_component.show_battle_start(event.data.get('battle_info', {}))
        else:
            logger.debug(f"Battle started: {event.data.get('battle_info', {})}")
    
    def _handle_battle_end(self, event: BattleEvent) -> None:
        """Handle battle end events."""
        if hasattr(self._ui_component, 'show_battle_end'):
            self._ui_component.show_battle_end(event.data.get('result', {}))
        else:
            logger.debug(f"Battle ended: {event.data.get('result', {})}")

    def validate_event_flow(self) -> Dict[str, bool]:
        """Validate that all critical events have handlers - ENHANCED VALIDATION."""
        critical_events = [
            # Core battle flow
            EventType.DAMAGE_DEALT,
            EventType.HP_BAR_UPDATE,
            EventType.MESSAGE_SHOW,
            EventType.TURN_START,
            EventType.TURN_END,
            EventType.PHASE_CHANGE,
            
            # Action flow - CRITICAL MISSING EVENTS ADDED
            EventType.ACTION_ANNOUNCE,
            EventType.ACTION_EXECUTE,
            EventType.ACTION_COMPLETE,
            
            # Visual feedback
            EventType.ANIMATION_PLAY,
            EventType.CAMERA_SHAKE,
            EventType.SCREEN_FLASH,
            EventType.EFFECT_SHOW,
            
            # Combat mechanics
            EventType.STATUS_APPLIED,
            EventType.STATUS_REMOVED,
            EventType.STATUS_DAMAGE,
            EventType.STAT_CHANGE,
            EventType.MONSTER_FAINTED,
            EventType.MONSTER_REVIVED,
            EventType.CRITICAL_HIT,
            EventType.MISS,
            
            # UI interaction
            EventType.MENU_OPEN,
            EventType.MENU_CLOSE,
            EventType.WAIT_FOR_INPUT,
            EventType.WAIT_FOR_ANIMATION,
            EventType.WAIT,
            
            # Monster events
            EventType.MONSTER_SWITCH,
            EventType.MONSTER_APPEAR,
            
            # Item/Tame events
            EventType.ITEM_USE,
            EventType.TAME_ATTEMPT,
            
            # Special events
            EventType.ESCAPE_ATTEMPT,
            
            # Dialog events
            EventType.DIALOG_SHOW,
            EventType.DIALOG_CHOICE,
            
            # Weather/Terrain events
            EventType.WEATHER_EFFECT,
            EventType.TERRAIN_EFFECT,
            
            # Battle lifecycle
            EventType.BATTLE_START,
            EventType.BATTLE_END
        ]
        
        validation = {}
        missing_handlers = []
        
        for event_type in critical_events:
            has_handlers = event_type in self.event_handlers and len(self.event_handlers[event_type]) > 0
            validation[event_type.name] = has_handlers
            if not has_handlers:
                missing_handlers.append(event_type.name)
                logger.warning(f"⚠️ No handlers for critical event: {event_type.name}")
        
        # Summary
        total_critical = len(critical_events)
        handled_critical = sum(1 for v in validation.values() if v)
        
        if missing_handlers:
            logger.error(f"❌ Event Flow Validation FAILED: {len(missing_handlers)} critical events missing handlers")
            logger.error(f"Missing handlers: {', '.join(missing_handlers)}")
        else:
            logger.info(f"✅ Event Flow Validation PASSED: {handled_critical}/{total_critical} critical events have handlers")
        
        return validation

    def verify_connections(self) -> Dict[str, int]:
        """
        Verify all handler connections.
        
        Returns:
            Dictionary mapping event types to handler counts
        """
        report = {}
        for event_type, handlers in self.event_handlers.items():
            report[event_type.name] = len(handlers)
        
        logger.info("[EVENT SYSTEM] Handler connections:")
        for event_name, count in report.items():
            logger.info(f"  {event_name}: {count} handlers")
        
        return report
    
    def verify_event_flow_sequence(self) -> Dict[str, Any]:
        """
        Verify critical event flow sequence: MESSAGE → ACTION → DAMAGE → HP_UPDATE.
        
        Returns:
            Dictionary with flow validation results
        """
        flow_validation = {
            'message_to_action': False,
            'action_to_damage': False,
            'damage_to_hp_update': False,
            'complete_flow': False,
            'missing_handlers': [],
            'flow_issues': []
        }
        
        # Check if all required handlers exist
        required_flow_events = [
            EventType.MESSAGE_SHOW,
            EventType.ACTION_ANNOUNCE,
            EventType.ACTION_EXECUTE,
            EventType.ACTION_COMPLETE,
            EventType.DAMAGE_DEALT,
            EventType.HP_BAR_UPDATE
        ]
        
        for event_type in required_flow_events:
            if event_type not in self.event_handlers or len(self.event_handlers[event_type]) == 0:
                flow_validation['missing_handlers'].append(event_type.name)
        
        # Check if all handlers exist
        if not flow_validation['missing_handlers']:
            flow_validation['message_to_action'] = True
            flow_validation['action_to_damage'] = True
            flow_validation['damage_to_hp_update'] = True
            flow_validation['complete_flow'] = True
            logger.info("✅ Event Flow Validation PASSED: MESSAGE → ACTION → DAMAGE → HP_UPDATE")
        else:
            flow_validation['flow_issues'].append(f"Missing handlers: {', '.join(flow_validation['missing_handlers'])}")
            logger.error(f"❌ Event Flow Validation FAILED: Missing handlers for flow sequence")
        
        return flow_validation
    
    def validate_all_handlers(self) -> Dict[str, Any]:
        """
        Comprehensive validation of all event handlers with caching for performance.
        
        Returns:
            Dictionary with detailed validation results
        """
        # Check cache first
        current_time = time.time()
        if (current_time - self._last_validation < self._cache_duration and 
            'validation_result' in self._validation_cache):
            logger.debug("Using cached validation result")
            return self._validation_cache['validation_result']
        
        validation_result = {
            'total_event_types': len(EventType),
            'handlers_registered': len(self.event_handlers),
            'missing_handlers': [],
            'critical_missing': [],
            'handler_coverage_percent': 0.0,
            'validation_passed': False,
            'warnings': [],
            'recommendations': []
        }
        
        # Get all EventType values
        all_event_types = list(EventType)
        critical_events = [
            EventType.MESSAGE_SHOW,
            EventType.ACTION_ANNOUNCE,
            EventType.ACTION_EXECUTE,
            EventType.ACTION_COMPLETE,
            EventType.DAMAGE_DEALT,
            EventType.HP_BAR_UPDATE,
            EventType.TURN_START,
            EventType.TURN_END,
            EventType.PHASE_CHANGE,
            EventType.MONSTER_FAINTED,
            EventType.STATUS_APPLIED,
            EventType.BATTLE_START,
            EventType.BATTLE_END
        ]
        
        # Check all event types
        for event_type in all_event_types:
            if event_type not in self.event_handlers or len(self.event_handlers[event_type]) == 0:
                validation_result['missing_handlers'].append(event_type.name)
                
                if event_type in critical_events:
                    validation_result['critical_missing'].append(event_type.name)
                    logger.warning(f"⚠️ CRITICAL: No handlers for {event_type.name}")
                else:
                    logger.debug(f"Missing handler for {event_type.name}")
        
        # Calculate coverage
        covered_events = len(all_event_types) - len(validation_result['missing_handlers'])
        validation_result['handler_coverage_percent'] = (covered_events / len(all_event_types)) * 100
        
        # Determine if validation passed
        validation_result['validation_passed'] = len(validation_result['critical_missing']) == 0
        
        # Generate warnings and recommendations
        if validation_result['critical_missing']:
            validation_result['warnings'].append(f"Critical events missing handlers: {', '.join(validation_result['critical_missing'])}")
        
        if validation_result['handler_coverage_percent'] < 90:
            validation_result['warnings'].append(f"Low handler coverage: {validation_result['handler_coverage_percent']:.1f}%")
        
        if len(validation_result['missing_handlers']) > 0:
            validation_result['recommendations'].append("Register handlers for missing event types")
        
        if validation_result['handler_coverage_percent'] < 100:
            validation_result['recommendations'].append("Consider implementing handlers for all event types for complete coverage")
        
        # Log results
        if validation_result['validation_passed']:
            logger.info(f"✅ Handler Validation PASSED: {validation_result['handler_coverage_percent']:.1f}% coverage ({covered_events}/{len(all_event_types)} events)")
        else:
            logger.error(f"❌ Handler Validation FAILED: {len(validation_result['critical_missing'])} critical events missing handlers")
        
        # Cache the result
        self._validation_cache['validation_result'] = validation_result
        self._last_validation = current_time
        
        return validation_result
    
    def test_event_flow_sequence(self) -> bool:
        """
        Test the complete event flow sequence with sample events.
        
        Returns:
            True if flow test passes
        """
        try:
            logger.info("🧪 Testing Event Flow Sequence...")
            
            # Test 1: Message Show
            self.emit_event(EventType.MESSAGE_SHOW, {'message': 'Test message'})
            
            # Test 2: Action Announce
            self.emit_event(EventType.ACTION_ANNOUNCE, {'action_name': 'Test Attack'})
            
            # Test 3: Action Execute
            self.emit_event(EventType.ACTION_EXECUTE, {'action_data': {'move': 'Test Move'}})
            
            # Test 4: Action Complete
            self.emit_event(EventType.ACTION_COMPLETE, {'action_result': {'success': True}})
            
            # Test 5: Damage Dealt
            self.emit_event(EventType.DAMAGE_DEALT, {'damage': 25, 'target': 'test_target'})
            
            # Test 6: HP Bar Update
            self.emit_event(EventType.HP_BAR_UPDATE, {'target': 'test_target', 'current_hp': 75, 'max_hp': 100})
            
            logger.info("✅ Event Flow Sequence Test PASSED")
            return True
            
        except Exception as e:
            logger.error(f"❌ Event Flow Sequence Test FAILED: {e}")
            return False
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get memory usage statistics for the event processor.
        
        Returns:
            Dictionary with memory statistics
        """
        import sys
        
        stats = {
            'event_history_size': len(self.event_history),
            'priority_queue_size': len(self._event_queue),
            'total_handlers': sum(len(handlers) for handlers in self.event_handlers.values()),
            'handler_types': len(self.event_handlers),
            'memory_usage_mb': sys.getsizeof(self) / (1024 * 1024)
        }
        
        # Calculate estimated memory usage
        history_memory = len(self.event_history) * 1024  # Rough estimate per event
        queue_memory = len(self._event_queue) * 1024
        handlers_memory = stats['total_handlers'] * 512
        
        stats['estimated_memory_kb'] = (history_memory + queue_memory + handlers_memory) / 1024
        stats['memory_efficient'] = stats['event_history_size'] <= 50 and stats['priority_queue_size'] <= 30
        
        return stats
    
    def optimize_memory(self) -> None:
        """Optimize memory usage by cleaning up old data - AGGRESSIVE CLEANUP."""
        # Clean event history aggressively - AGGRESSIVE CLEANUP
        if len(self.event_history) > 50:
            self.event_history = self.event_history[-25:]
            logger.info("[AGGRESSIVE CLEANUP] Trimmed event history to 25 events")
        
        # Clear priority queue if too large - AGGRESSIVE CLEANUP
        if len(self._event_queue) > 30:
            self._compact_queue()
            logger.info("[AGGRESSIVE CLEANUP] Compacted priority queue")
        
        logger.info("[AGGRESSIVE CLEANUP] Memory optimization completed")
    
    def _compact_queue(self) -> None:
        """Compact the priority queue to keep only top priority events."""
        if len(self._event_queue) <= 15:  # Don't compact if already small
            return
        
        # Keep only top 15 priority events
        temp_queue = []
        for _ in range(min(15, len(self._event_queue))):
            if self._event_queue:
                temp_queue.append(heapq.heappop(self._event_queue))
        
        self._event_queue = temp_queue
        heapq.heapify(self._event_queue)
        logger.debug(f"[AGGRESSIVE CLEANUP] Compacted priority queue to {len(self._event_queue)} events")
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get comprehensive performance metrics for the event processor.
        
        Returns:
            Dictionary with performance statistics
        """
        current_time = time.time()
        uptime = current_time - self._start_time
        
        # Calculate events per second
        events_per_second = self._event_count / uptime if uptime > 0 else 0
        
        # Calculate average processing time
        avg_processing_time_ms = 0
        if self._processing_times:
            avg_processing_time_ms = (sum(self._processing_times) / len(self._processing_times)) * 1000
        
        # Calculate memory usage
        memory_usage_mb = self._get_memory_usage()
        
        # Calculate handler count
        handler_count = sum(len(handlers) for handlers in self.event_handlers.values())
        
        # Calculate cleanup frequency
        cleanup_frequency = 0
        if uptime > 0:
            cleanup_frequency = self._event_count / max(1, (current_time - self._last_cleanup_time))
        
        metrics = {
            'events_per_second': round(events_per_second, 2),
            'memory_usage_mb': round(memory_usage_mb, 4),
            'queue_size': len(self._event_queue),
            'history_size': len(self.event_history),
            'handler_count': handler_count,
            'handler_types': len(self.event_handlers),
            'avg_processing_time_ms': round(avg_processing_time_ms, 2),
            'total_events_processed': self._event_count,
            'uptime_seconds': round(uptime, 2),
            'cleanup_frequency': round(cleanup_frequency, 2),
            'memory_efficient': len(self.event_history) <= 50 and len(self._event_queue) <= 30,
            'performance_grade': self._calculate_performance_grade(events_per_second, avg_processing_time_ms, memory_usage_mb)
        }
        
        return metrics
    
    def _get_memory_usage(self) -> float:
        """Calculate estimated memory usage in MB."""
        import sys
        
        # Base object size
        base_size = sys.getsizeof(self)
        
        # Event history memory (rough estimate)
        history_memory = len(self.event_history) * 1024  # ~1KB per event
        
        # Queue memory
        queue_memory = len(self._event_queue) * 1024  # ~1KB per queued event
        
        # Handler memory
        handler_memory = sum(len(handlers) for handlers in self.event_handlers.values()) * 512  # ~512B per handler
        
        total_bytes = base_size + history_memory + queue_memory + handler_memory
        return total_bytes / (1024 * 1024)  # Convert to MB
    
    def _calculate_performance_grade(self, events_per_second: float, avg_processing_time_ms: float, memory_usage_mb: float) -> str:
        """Calculate performance grade based on metrics."""
        score = 0
        
        # Events per second scoring (higher is better)
        if events_per_second >= 100:
            score += 3
        elif events_per_second >= 50:
            score += 2
        elif events_per_second >= 10:
            score += 1
        
        # Processing time scoring (lower is better)
        if avg_processing_time_ms <= 1:
            score += 3
        elif avg_processing_time_ms <= 5:
            score += 2
        elif avg_processing_time_ms <= 10:
            score += 1
        
        # Memory usage scoring (lower is better)
        if memory_usage_mb <= 1:
            score += 3
        elif memory_usage_mb <= 5:
            score += 2
        elif memory_usage_mb <= 10:
            score += 1
        
        # Convert score to grade
        if score >= 8:
            return "A+"
        elif score >= 6:
            return "A"
        elif score >= 4:
            return "B"
        elif score >= 2:
            return "C"
        else:
            return "D"
