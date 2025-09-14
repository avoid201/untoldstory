"""
Battle Event System - RESTORED FROM ARCHIVE
Generator-based event system for clean battle flow and UI updates
Based on MRPG's yield-based battle system approach
"""

import logging
from typing import Generator, Dict, Any, List, Optional, Tuple, Callable, TYPE_CHECKING
from dataclasses import dataclass, field
from enum import Enum, auto
from collections import deque
import time

from engine.systems.monster_instance import StatusCondition

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
        """Dict-like get method for compatibility."""
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
        """Make BattleEvent subscriptable for backward compatibility."""
        return self.get(key)


class EventQueue:
    """Queue for managing battle events."""
    
    def __init__(self):
        """Initialize event queue."""
        self.events: deque[BattleEvent] = deque()
        self.processing: Optional[BattleEvent] = None
        self.history: List[BattleEvent] = []
        self.paused = False
    
    def add(self, event: BattleEvent) -> None:
        """Add an event to the queue."""
        self.events.append(event)
        logger.debug(f"Event added to queue: {event}")
    
    def add_priority(self, event: BattleEvent) -> None:
        """Add a high-priority event to the front of the queue."""
        self.events.appendleft(event)
        logger.debug(f"Priority event added: {event}")
    
    def get_next(self) -> Optional[BattleEvent]:
        """Get the next event to process."""
        if self.paused or not self.events:
            return None
        
        # Sort by priority if needed
        if len(self.events) > 1:
            sorted_events = sorted(self.events, key=lambda e: e.priority, reverse=True)
            self.events = deque(sorted_events)
        
        event = self.events.popleft()
        self.processing = event
        return event
    
    def complete_current(self) -> None:
        """Mark current event as complete."""
        if self.processing:
            self.history.append(self.processing)
            self.processing = None
    
    def clear(self) -> None:
        """Clear all pending events."""
        self.events.clear()
        self.processing = None
    
    def pause(self) -> None:
        """Pause event processing."""
        self.paused = True
    
    def resume(self) -> None:
        """Resume event processing."""
        self.paused = False
    
    def is_empty(self) -> bool:
        """Check if queue is empty."""
        return len(self.events) == 0 and self.processing is None
    
    def has_blocking(self) -> bool:
        """Check if there's a blocking event being processed."""
        return self.processing is not None and self.processing.blocking


class BattleEventGenerator:
    """
    Generator-based battle event system.
    Yields events for clean battle flow and UI updates.
    """
    
    def __init__(self, battle_state=None):
        """
        Initialize event generator.
        
        Args:
            battle_state: The battle state to generate events for (optional)
        """
        self.battle_state = battle_state
        self.event_queue = EventQueue()
        self.event_handlers: Dict[EventType, List[Callable]] = {}
        self.current_phase = "init"
        
        # Register default handlers
        self._register_default_handlers()
    
    def _register_default_handlers(self) -> None:
        """Register default event handlers."""
        # These can be overridden by the UI layer
        self.register_handler(EventType.MESSAGE_SHOW, self._default_message_handler)
        self.register_handler(EventType.WAIT, self._default_wait_handler)
    
    def register_handler(self, event_type: EventType, handler: Callable) -> None:
        """
        Register a handler for an event type.
        
        Args:
            event_type: Type of event to handle
            handler: Function to call when event occurs
        """
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    def unregister_handler(self, event_type: EventType, handler: Callable) -> None:
        """Unregister an event handler."""
        if event_type in self.event_handlers and handler in self.event_handlers[event_type]:
            self.event_handlers[event_type].remove(handler)
    
    def emit(self, event: BattleEvent) -> None:
        """
        Emit an event to all registered handlers.
        
        Args:
            event: Event to emit
        """
        if event.event_type in self.event_handlers:
            for handler in self.event_handlers[event.event_type]:
                try:
                    handler(event)
                except Exception as e:
                    logger.error(f"Error in event handler: {str(e)}")
    
    def battle_start_generator(self) -> Generator[BattleEvent, None, None]:
        """
        Generate events for battle start.
        
        Yields:
            Battle start events
        """
        # Battle intro
        yield BattleEvent(
            EventType.BATTLE_START,
            data={'battle_type': self.battle_state.battle_type if self.battle_state else 'wild'}
        )
        
        # Show battle background
        yield BattleEvent(
            EventType.ANIMATION_PLAY,
            data={'animation': 'battle_transition'},
            duration=1.0,
            blocking=True
        )
        
        if self.battle_state:
            # Announce enemy appearance
            if hasattr(self.battle_state, 'battle_type') and self.battle_state.battle_type.value == 'wild':
                if hasattr(self.battle_state, 'enemy_active') and self.battle_state.enemy_active:
                    enemy_name = self.battle_state.enemy_active.name
                    yield BattleEvent(
                        EventType.MESSAGE_SHOW,
                        data={'message': f"Ein wilder {enemy_name} erscheint!"},
                        duration=1.5
                    )
                    
                    # Enemy appear animation
                    yield BattleEvent(
                        EventType.MONSTER_APPEAR,
                        data={'monster': self.battle_state.enemy_active},
                        duration=0.5
                    )
            else:
                yield BattleEvent(
                    EventType.MESSAGE_SHOW,
                    data={'message': "Trainer fordert dich heraus!"},
                    duration=1.5
                )
            
            # Player monster entrance
            if hasattr(self.battle_state, 'player_active') and self.battle_state.player_active:
                yield BattleEvent(
                    EventType.MESSAGE_SHOW,
                    data={'message': f"Los, {self.battle_state.player_active.name}!"},
                    duration=1.0
                )
                
                yield BattleEvent(
                    EventType.MONSTER_APPEAR,
                    data={'monster': self.battle_state.player_active},
                    duration=0.5
                )
            
            # Update HP bars
            if hasattr(self.battle_state, 'player_active') and hasattr(self.battle_state, 'enemy_active'):
                yield BattleEvent(
                    EventType.HP_BAR_UPDATE,
                    data={
                        'player': self.battle_state.player_active,
                        'enemy': self.battle_state.enemy_active
                    }
                )
        
        # Phase change to input
        yield BattleEvent(
            EventType.PHASE_CHANGE,
            data={'phase': 'input'}
        )
    
    def turn_execution_generator(self, actions: List) -> Generator[BattleEvent, None, None]:
        """
        Generate events for turn execution.
        
        Args:
            actions: List of actions to execute
            
        Yields:
            Turn execution events
        """
        # Turn start
        turn_count = 1
        if self.battle_state and hasattr(self.battle_state, 'turn_count'):
            turn_count = self.battle_state.turn_count
            
        yield BattleEvent(
            EventType.TURN_START,
            data={'turn': turn_count}
        )
        
        # Execute each action
        for action in actions:
            # Skip if actor is fainted
            if hasattr(action, 'actor') and hasattr(action.actor, 'is_fainted') and action.actor.is_fainted:
                continue
            
            # Announce action
            yield BattleEvent(
                EventType.ACTION_ANNOUNCE,
                data={'action': action, 'actor': action.actor if hasattr(action, 'actor') else None}
            )
            
            # Generate events based on action type
            if hasattr(action, 'action_type'):
                action_type_value = action.action_type.value if hasattr(action.action_type, 'value') else str(action.action_type)
                
                if action_type_value == 'attack':
                    yield from self._attack_event_generator(action)
                elif action_type_value == 'item':
                    yield from self._item_event_generator(action)
                elif action_type_value == 'switch':
                    yield from self._switch_event_generator(action)
                elif action_type_value == 'flee':
                    yield from self._flee_event_generator(action)
                elif action_type_value == 'tame':
                    yield from self._tame_event_generator(action)
            
            # Check for faints after each action
            yield from self._check_faint_events()
        
        # Process end-of-turn effects
        yield from self._end_of_turn_generator()
        
        # Turn end
        yield BattleEvent(
            EventType.TURN_END,
            data={'turn': turn_count}
        )
    
    def _attack_event_generator(self, action) -> Generator[BattleEvent, None, None]:
        """Generate events for an attack action."""
        actor = action.actor if hasattr(action, 'actor') else None
        target = action.target if hasattr(action, 'target') else None
        move = action.move if hasattr(action, 'move') else None
        
        if not actor or not target or not move:
            return
        
        # Attack message
        move_name = move.name if hasattr(move, 'name') else 'Angriff'
        yield BattleEvent(
            EventType.MESSAGE_SHOW,
            data={'message': f"{actor.name} setzt {move_name} ein!"},
            duration=1.0
        )
        
        # Attack animation
        yield BattleEvent(
            EventType.ANIMATION_PLAY,
            data={
                'animation': f"move_{move_name.lower()}",
                'source': actor,
                'target': target
            },
            duration=1.5,
            blocking=True
        )
        
        # Calculate damage using UnifiedDamageCalculator (SINGLE SOURCE OF TRUTH)
        try:
            from engine.systems.unified_damage_calculator import unified_damage_calculator
            damage_result = unified_damage_calculator.calculate_damage(
                attacker=actor,
                defender=target,
                move=move
            )
            damage = damage_result.damage
        except Exception as e:
            logger.warning(f"Error calculating damage with UnifiedDamageCalculator, using fallback: {str(e)}")
            # Fallback: Simple damage calculation based on move power
            move_power = getattr(move, 'power', 50)
            damage = max(1, move_power // 2)
        
        # Deal damage
        yield BattleEvent(
            EventType.DAMAGE_DEALT,
            data={
                'target': target,
                'damage': damage,
                'attacker': actor
            }
        )
        
        # Update HP bar
        if hasattr(target, 'take_damage'):
            target.take_damage(damage)
        
        yield BattleEvent(
            EventType.HP_BAR_UPDATE,
            data={'target': target}
        )
    
    def _item_event_generator(self, action) -> Generator[BattleEvent, None, None]:
        """Generate events for item use."""
        # Simplified implementation
        yield BattleEvent(
            EventType.MESSAGE_SHOW,
            data={'message': "Item-System noch nicht implementiert!"},
            duration=1.0
        )
    
    def _switch_event_generator(self, action) -> Generator[BattleEvent, None, None]:
        """Generate events for monster switching."""
        # Simplified implementation
        yield BattleEvent(
            EventType.MESSAGE_SHOW,
            data={'message': "Monster-Wechsel!"},
            duration=1.0
        )
    
    def _flee_event_generator(self, action) -> Generator[BattleEvent, None, None]:
        """Generate events for escape attempt."""
        # Simplified implementation
        yield BattleEvent(
            EventType.MESSAGE_SHOW,
            data={'message': "Fluchtversuch!"},
            duration=1.0
        )
    
    def _tame_event_generator(self, action) -> Generator[BattleEvent, None, None]:
        """Generate events for taming attempt."""
        # Simplified implementation
        yield BattleEvent(
            EventType.MESSAGE_SHOW,
            data={'message': "Zähmversuch!"},
            duration=1.0
        )
    
    def _check_faint_events(self) -> Generator[BattleEvent, None, None]:
        """Check for and generate faint events."""
        if not self.battle_state:
            return
            
        # Check player team for fainted monsters
        if hasattr(self.battle_state, 'player_team'):
            for i, monster in enumerate(self.battle_state.player_team):
                if monster and monster.current_hp <= 0 and not monster.is_fainted:
                    monster.is_fainted = True
                    logger.info(f"Player monster {monster.nickname or monster.species.name} fainted!")
                    
                    yield BattleEvent(
                        event_type=EventType.MONSTER_FAINTED,
                        data={
                            'monster': monster,
                            'team_type': 'player',
                            'position': i,
                            'message': f"{monster.nickname or monster.species.name} ist ohnmächtig geworden!"
                        },
                        duration=2.0,
                        blocking=True
                    )
        
                # Check enemy team for fainted monsters
        if hasattr(self.battle_state, 'enemy_team'):
            for i, monster in enumerate(self.battle_state.enemy_team):
                if monster and monster.current_hp <= 0 and not monster.is_fainted:
                    monster.is_fainted = True
                    logger.info(f"Enemy monster {monster.nickname or monster.species.name} fainted!")
                    
                    yield BattleEvent(
                        event_type=EventType.MONSTER_FAINTED,
                        data={
                            'monster': monster,
                            'team_type': 'enemy',
                            'position': i,
                            'message': f"Das wilde {monster.species.name} ist ohnmächtig geworden!"
                        },
                        duration=2.0,
                        blocking=True
                    )
    
    def _end_of_turn_generator(self) -> Generator[BattleEvent, None, None]:
        """Generate end-of-turn events."""
        if not self.battle_state:
            return
            
        # Process status damage for all active monsters
        active_monsters = []
        if hasattr(self.battle_state, 'player_active') and self.battle_state.player_active:
            active_monsters.append(self.battle_state.player_active)
        if hasattr(self.battle_state, 'enemy_active') and self.battle_state.enemy_active:
            active_monsters.append(self.battle_state.enemy_active)
            
        for monster in active_monsters:
            if monster and monster.current_hp > 0:
                # Burn damage: -1/8 of max HP
                if hasattr(monster, 'status') and monster.status == StatusCondition.BURN:
                    burn_damage = max(1, monster.max_hp // 8)
                    monster.current_hp = max(0, monster.current_hp - burn_damage)
                    
                    yield BattleEvent(
                        event_type=EventType.STATUS_DAMAGE,
                        data={
                            'monster': monster,
                            'damage': burn_damage,
                            'status': 'burn',
                            'message': f"{monster.nickname or monster.species.name} erleidet Verbrennungsschaden!"
                        },
                        duration=1.5,
                        blocking=False
                    )
                
                # Poison damage: -1/16 of max HP
                elif hasattr(monster, 'status') and monster.status == StatusCondition.POISON:
                    poison_damage = max(1, monster.max_hp // 16)
                    monster.current_hp = max(0, monster.current_hp - poison_damage)
                    
                    yield BattleEvent(
                        event_type=EventType.STATUS_DAMAGE,
                        data={
                            'monster': monster,
                            'damage': poison_damage,
                            'status': 'poison',
                            'message': f"{monster.nickname or monster.species.name} erleidet Giftsschaden!"
                        },
                        duration=1.5,
                        blocking=False
                    )
                
                # Stat stage decay (DQM-style: stages decay by 1 each turn)
                for stat in ['atk', 'def', 'mag', 'res', 'spd', 'acc', 'eva']:
                    if stat in monster.stat_stages and monster.stat_stages[stat] != 0:
                        old_stage = monster.stat_stages[stat]
                        # Decay towards 0
                        if old_stage > 0:
                            monster.stat_stages[stat] = max(0, old_stage - 1)
                        else:
                            monster.stat_stages[stat] = min(0, old_stage + 1)
                        
                        if monster.stat_stages[stat] != old_stage:
                            stat_names = {
                                'atk': 'Angriff', 'def': 'Verteidigung',
                                'mag': 'Magie', 'res': 'Resistenz',
                                'spd': 'Initiative', 'acc': 'Genauigkeit', 'eva': 'Fluchtwert'
                            }
                            
                            yield BattleEvent(
                                event_type=EventType.STAT_CHANGE,
                                data={
                                    'monster': monster,
                                    'stat': stat,
                                    'old_stage': old_stage,
                                    'new_stage': monster.stat_stages[stat],
                                    'message': f"{monster.nickname or monster.species.name}'s {stat_names.get(stat, stat)} normalisiert sich!"
                                },
                                duration=1.0,
                                blocking=False
                            )
        
        # Weather effects (if any)
        if hasattr(self.battle_state, 'weather') and self.battle_state.weather:
            yield BattleEvent(
                event_type=EventType.WEATHER_EFFECT,
                data={
                    'weather': self.battle_state.weather,
                    'message': f"Das Wetter wirkt sich aus: {self.battle_state.weather}"
                },
                duration=1.0,
                blocking=False
            )
    
    def _default_message_handler(self, event: BattleEvent) -> None:
        """Default handler for message events."""
        logger.info(f"Battle Message: {event.data.get('message', '')}")
    
    def _default_wait_handler(self, event: BattleEvent) -> None:
        """Default handler for wait events."""
        time.sleep(event.duration)
    
    def process_events(self) -> None:
        """Process all queued events."""
        while not self.event_queue.is_empty():
            event = self.event_queue.get_next()
            if event:
                self.emit(event)
                
                # Wait for blocking events
                if event.blocking:
                    time.sleep(event.duration)
                
                self.event_queue.complete_current()


# Helper functions for integration
def create_battle_event_system(battle_state) -> BattleEventGenerator:
    """
    Create a battle event system for a battle state.
    
    Args:
        battle_state: The battle state to use
        
    Returns:
        Configured event generator
    """
    return BattleEventGenerator(battle_state)


def generate_turn_events(event_gen: BattleEventGenerator, 
                         actions: List) -> List[BattleEvent]:
    """
    Generate all events for a turn.
    
    Args:
        event_gen: Event generator
        actions: List of actions for the turn
        
    Returns:
        List of events to process
    """
    events = []
    for event in event_gen.turn_execution_generator(actions):
        events.append(event)
    return events


# Export classes and functions
__all__ = [
    'EventType',
    'BattleEvent',
    'EventQueue', 
    'BattleEventGenerator',
    'create_battle_event_system',
    'generate_turn_events'
]
