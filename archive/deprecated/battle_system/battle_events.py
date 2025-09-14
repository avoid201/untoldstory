"""
Battle Event System
Generator-based event system for clean battle flow and UI updates

Based on MRPG's yield-based battle system approach
"""

import logging
from typing import Generator, Dict, Any, List, Optional, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum, auto
from collections import deque
import time

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
    
    def __init__(self, battle_state):
        """
        Initialize event generator.
        
        Args:
            battle_state: The battle state to generate events for
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
        if event_type in self.event_handlers:
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
            data={'battle_type': self.battle_state.battle_type}
        )
        
        # Show battle background
        yield BattleEvent(
            EventType.ANIMATION_PLAY,
            data={'animation': 'battle_transition'},
            duration=1.0,
            blocking=True
        )
        
        # Announce enemy appearance
        if self.battle_state.battle_type.value == 'wild':
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
        yield BattleEvent(
            EventType.TURN_START,
            data={'turn': self.battle_state.turn_count}
        )
        
        # Execute each action
        for action in actions:
            # Skip if actor is fainted
            if hasattr(action.actor, 'is_fainted') and action.actor.is_fainted:
                continue
            
            # Announce action
            yield BattleEvent(
                EventType.ACTION_ANNOUNCE,
                data={'action': action, 'actor': action.actor}
            )
            
            # Generate events based on action type
            if action.action_type.value == 'attack':
                yield from self._attack_event_generator(action)
            elif action.action_type.value == 'item':
                yield from self._item_event_generator(action)
            elif action.action_type.value == 'switch':
                yield from self._switch_event_generator(action)
            elif action.action_type.value == 'flee':
                yield from self._flee_event_generator(action)
            elif action.action_type.value == 'tame':
                yield from self._tame_event_generator(action)
            
            # Check for faints after each action
            yield from self._check_faint_events()
        
        # Process end-of-turn effects
        yield from self._end_of_turn_generator()
        
        # Turn end
        yield BattleEvent(
            EventType.TURN_END,
            data={'turn': self.battle_state.turn_count}
        )
    
    def _attack_event_generator(self, action) -> Generator[BattleEvent, None, None]:
        """Generate events for an attack action."""
        actor = action.actor
        target = action.target
        move = action.move
        
        # Attack message
        yield BattleEvent(
            EventType.MESSAGE_SHOW,
            data={'message': f"{actor.name} setzt {move.name} ein!"},
            duration=1.0
        )
        
        # Attack animation
        yield BattleEvent(
            EventType.ANIMATION_PLAY,
            data={
                'animation': f"move_{move.name.lower()}",
                'source': actor,
                'target': target
            },
            duration=1.5,
            blocking=True
        )
        
        # Calculate damage (using DQM formulas)
        from engine.systems.battle.damage_calc import DamageCalculator
        damage_calc = DamageCalculator()
        result = damage_calc.calculate(actor, target, move)
        
        # Check for miss
        if result.missed:
            yield BattleEvent(
                EventType.MISS,
                data={'actor': actor, 'target': target}
            )
            yield BattleEvent(
                EventType.MESSAGE_SHOW,
                data={'message': "Daneben!"},
                duration=1.0
            )
            return
        
        # Check for critical hit
        if result.is_critical:
            yield BattleEvent(
                EventType.CRITICAL_HIT,
                data={'actor': actor}
            )
            yield BattleEvent(
                EventType.SCREEN_FLASH,
                data={'color': 'white', 'duration': 0.2}
            )
            yield BattleEvent(
                EventType.MESSAGE_SHOW,
                data={'message': "Kritischer Treffer!"},
                duration=0.5
            )
        
        # Show effectiveness
        if result.effectiveness_text:
            yield BattleEvent(
                EventType.MESSAGE_SHOW,
                data={'message': result.effectiveness_text},
                duration=0.5
            )
        
        # Deal damage
        yield BattleEvent(
            EventType.DAMAGE_DEALT,
            data={
                'target': target,
                'damage': result.damage,
                'attacker': actor
            }
        )
        
        # Show damage number
        yield BattleEvent(
            EventType.EFFECT_SHOW,
            data={
                'effect': 'damage_number',
                'value': result.damage,
                'position': target
            },
            duration=0.5
        )
        
        # Update HP bar
        target.take_damage(result.damage)
        yield BattleEvent(
            EventType.HP_BAR_UPDATE,
            data={'target': target}
        )
        
        # Camera shake for big hits
        if result.damage > target.max_hp * 0.3:
            yield BattleEvent(
                EventType.CAMERA_SHAKE,
                data={'intensity': 'medium', 'duration': 0.3}
            )
    
    def _item_event_generator(self, action) -> Generator[BattleEvent, None, None]:
        """Generate events for item use."""
        actor = action.actor
        item = action.item_id
        target = action.target or actor
        
        yield BattleEvent(
            EventType.MESSAGE_SHOW,
            data={'message': f"{actor.name} benutzt {item}!"},
            duration=1.0
        )
        
        yield BattleEvent(
            EventType.ITEM_USE,
            data={
                'item': item,
                'user': actor,
                'target': target
            }
        )
        
        # Item effect animation
        yield BattleEvent(
            EventType.ANIMATION_PLAY,
            data={
                'animation': f"item_{item.lower()}",
                'target': target
            },
            duration=1.0
        )
        
        # Apply item effect (simplified)
        # In real implementation, this would call item system
        if 'potion' in item.lower():
            heal_amount = 50
            target.heal(heal_amount)
            
            yield BattleEvent(
                EventType.HEALING_DONE,
                data={
                    'target': target,
                    'amount': heal_amount
                }
            )
            
            yield BattleEvent(
                EventType.HP_BAR_UPDATE,
                data={'target': target}
            )
    
    def _switch_event_generator(self, action) -> Generator[BattleEvent, None, None]:
        """Generate events for monster switching."""
        current = action.actor
        switch_to = action.switch_to
        
        # Withdraw current monster
        yield BattleEvent(
            EventType.MESSAGE_SHOW,
            data={'message': f"{current.name}, komm zurück!"},
            duration=1.0
        )
        
        yield BattleEvent(
            EventType.ANIMATION_PLAY,
            data={
                'animation': 'monster_withdraw',
                'target': current
            },
            duration=0.5
        )
        
        # Send out new monster
        yield BattleEvent(
            EventType.MESSAGE_SHOW,
            data={'message': f"Los, {switch_to.name}!"},
            duration=1.0
        )
        
        yield BattleEvent(
            EventType.MONSTER_SWITCH,
            data={
                'old': current,
                'new': switch_to
            }
        )
        
        yield BattleEvent(
            EventType.MONSTER_APPEAR,
            data={'monster': switch_to},
            duration=0.5
        )
        
        # Update battle state
        if current == self.battle_state.player_active:
            self.battle_state.player_active = switch_to
        
        yield BattleEvent(
            EventType.HP_BAR_UPDATE,
            data={'target': switch_to}
        )
    
    def _flee_event_generator(self, action) -> Generator[BattleEvent, None, None]:
        """Generate events for escape attempt."""
        runner = action.actor
        
        yield BattleEvent(
            EventType.MESSAGE_SHOW,
            data={'message': f"{runner.name} versucht zu fliehen!"},
            duration=1.0
        )
        
        yield BattleEvent(
            EventType.ESCAPE_ATTEMPT,
            data={'runner': runner}
        )
        
        # Calculate escape chance using DQM formula
        from engine.systems.battle.dqm_integration import get_dqm_integration
        dqm = get_dqm_integration()
        
        escape_chance = dqm.calculate_escape_chance(
            runner,
            self.battle_state.enemy_active,
            self.battle_state.escape_attempts
        )
        
        import random
        if random.random() < escape_chance:
            yield BattleEvent(
                EventType.MESSAGE_SHOW,
                data={'message': "Du bist entkommen!"},
                duration=1.5
            )
            
            yield BattleEvent(
                EventType.BATTLE_END,
                data={'result': 'escaped'}
            )
        else:
            self.battle_state.escape_attempts += 1
            yield BattleEvent(
                EventType.MESSAGE_SHOW,
                data={'message': "Flucht gescheitert!"},
                duration=1.0
            )
    
    def _tame_event_generator(self, action) -> Generator[BattleEvent, None, None]:
        """Generate events for taming attempt."""
        actor = action.actor
        target = self.battle_state.enemy_active
        
        yield BattleEvent(
            EventType.MESSAGE_SHOW,
            data={'message': f"{actor.name} versucht {target.name} zu zähmen!"},
            duration=1.5
        )
        
        yield BattleEvent(
            EventType.TAME_ATTEMPT,
            data={
                'tamer': actor,
                'target': target
            }
        )
        
        # Taming animation
        yield BattleEvent(
            EventType.ANIMATION_PLAY,
            data={
                'animation': 'taming_attempt',
                'source': actor,
                'target': target
            },
            duration=2.0,
            blocking=True
        )
        
        # Calculate taming chance (simplified)
        hp_ratio = target.current_hp / target.max_hp
        base_chance = 0.3 * (1 - hp_ratio)  # Lower HP = higher chance
        
        import random
        if random.random() < base_chance:
            yield BattleEvent(
                EventType.MESSAGE_SHOW,
                data={'message': f"{target.name} wurde gezähmt!"},
                duration=2.0
            )
            
            yield BattleEvent(
                EventType.BATTLE_END,
                data={'result': 'tamed', 'tamed_monster': target}
            )
        else:
            yield BattleEvent(
                EventType.MESSAGE_SHOW,
                data={'message': "Zähmen fehlgeschlagen!"},
                duration=1.0
            )
    
    def _check_faint_events(self) -> Generator[BattleEvent, None, None]:
        """Check for and generate faint events."""
        # Check player monster
        if self.battle_state.player_active.is_fainted:
            yield BattleEvent(
                EventType.MONSTER_FAINTED,
                data={'monster': self.battle_state.player_active}
            )
            
            yield BattleEvent(
                EventType.MESSAGE_SHOW,
                data={'message': f"{self.battle_state.player_active.name} wurde besiegt!"},
                duration=1.5
            )
            
            # Check for available switches
            if not self.battle_state.has_able_monsters(self.battle_state.player_team):
                yield BattleEvent(
                    EventType.BATTLE_END,
                    data={'result': 'defeat'}
                )
            else:
                # Force switch
                yield BattleEvent(
                    EventType.MENU_OPEN,
                    data={'menu': 'force_switch'},
                    blocking=True
                )
        
        # Check enemy monster
        if self.battle_state.enemy_active.is_fainted:
            yield BattleEvent(
                EventType.MONSTER_FAINTED,
                data={'monster': self.battle_state.enemy_active}
            )
            
            yield BattleEvent(
                EventType.MESSAGE_SHOW,
                data={'message': f"{self.battle_state.enemy_active.name} wurde besiegt!"},
                duration=1.5
            )
            
            # Calculate rewards
            from engine.systems.battle.dqm_integration import get_dqm_integration
            dqm = get_dqm_integration()
            rewards = dqm.calculate_rewards(
                self.battle_state.enemy_active,
                is_boss=self.battle_state.battle_type.value == 'boss',
                party_size=len([m for m in self.battle_state.player_team if not m.is_fainted])
            )
            
            yield BattleEvent(
                EventType.MESSAGE_SHOW,
                data={'message': f"Erhielt {rewards['exp']} EXP!"},
                duration=1.0
            )
            
            yield BattleEvent(
                EventType.MESSAGE_SHOW,
                data={'message': f"Erhielt {rewards['gold']} Gold!"},
                duration=1.0
            )
            
            # Check for more enemies
            if not self.battle_state.has_able_monsters(self.battle_state.enemy_team):
                yield BattleEvent(
                    EventType.BATTLE_END,
                    data={'result': 'victory'}
                )
    
    def _end_of_turn_generator(self) -> Generator[BattleEvent, None, None]:
        """Generate end-of-turn events."""
        # Process status effects
        for monster in [self.battle_state.player_active, self.battle_state.enemy_active]:
            if not monster or monster.is_fainted:
                continue
            
            if hasattr(monster, 'status') and monster.status:
                if monster.status == 'poison':
                    damage = max(1, monster.max_hp // 16)
                    
                    yield BattleEvent(
                        EventType.MESSAGE_SHOW,
                        data={'message': f"{monster.name} leidet unter Gift!"},
                        duration=1.0
                    )
                    
                    yield BattleEvent(
                        EventType.DAMAGE_DEALT,
                        data={
                            'target': monster,
                            'damage': damage,
                            'source': 'poison'
                        }
                    )
                    
                    monster.take_damage(damage)
                    
                    yield BattleEvent(
                        EventType.HP_BAR_UPDATE,
                        data={'target': monster}
                    )
                
                elif monster.status == 'burn':
                    damage = max(1, monster.max_hp // 16)
                    
                    yield BattleEvent(
                        EventType.MESSAGE_SHOW,
                        data={'message': f"{monster.name} leidet unter Verbrennung!"},
                        duration=1.0
                    )
                    
                    yield BattleEvent(
                        EventType.DAMAGE_DEALT,
                        data={
                            'target': monster,
                            'damage': damage,
                            'source': 'burn'
                        }
                    )
                    
                    monster.take_damage(damage)
                    
                    yield BattleEvent(
                        EventType.HP_BAR_UPDATE,
                        data={'target': monster}
                    )
        
        # Weather effects
        if hasattr(self.battle_state, 'weather') and self.battle_state.weather:
            if self.battle_state.weather == 'sandstorm':
                yield BattleEvent(
                    EventType.MESSAGE_SHOW,
                    data={'message': "Der Sandsturm wütet!"},
                    duration=0.5
                )
                
                # Damage non-ground types
                for monster in [self.battle_state.player_active, self.battle_state.enemy_active]:
                    if monster and not monster.is_fainted:
                        if 'Erde' not in monster.species.types:
                            damage = max(1, monster.max_hp // 16)
                            monster.take_damage(damage)
                            
                            yield BattleEvent(
                                EventType.HP_BAR_UPDATE,
                                data={'target': monster}
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
