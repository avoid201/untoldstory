"""
Event Types and BattleEvent Class
=================================
Extracted from event_processor.py to comply with 300-line limit.
"""

from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, Any


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
    ACTION_START = auto()
    ACTION_EXECUTE = auto()
    ACTION_END = auto()
    ACTION_COMPLETE = auto()
    
    # Combat events
    DAMAGE_DEALT = auto()
    STATUS_APPLIED = auto()
    STAT_CHANGE = auto()
    
    # Monster events
    MONSTER_FAINTED = auto()
    MONSTER_SWITCH = auto()
    
    # UI events
    MESSAGE_SHOW = auto()
    MENU_OPEN = auto()
    MENU_CLOSE = auto()
    HP_BAR_UPDATE = auto()
    ANIMATION_PLAY = auto()  # Animation events
    
    # Combat mechanics
    CRITICAL_HIT = auto()
    MISS = auto()
    DODGE = auto()
    BLOCK = auto()
    REFLECT = auto()
    ABSORB = auto()
    
    # Special moves
    CHARGE = auto()
    DISCHARGE = auto()
    SUMMON = auto()
    BANISH = auto()
    
    # Battle actions
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
    
    # Level up events
    LEVEL_UP = auto()
    
    # Type effectiveness events
    SUPER_EFFECTIVE = auto()
    NOT_EFFECTIVE = auto()
    NOT_VERY_EFFECTIVE = auto()
    NO_EFFECT = auto()
    IMMUNE = auto()
    
    # Additional combat events
    HEAL = auto()
    REVIVE = auto()
    TRANSFORM = auto()
    COPY = auto()
    STEAL = auto()
    SWAP = auto()
    TRAP = auto()
    SEAL = auto()
    UNSEAL = auto()
    
    # Energy management events
    ACCUMULATE = auto()
    RELEASE = auto()
    STORE = auto()
    RETRIEVE = auto()
    CREATE = auto()
    DESTROY = auto()
    CALL = auto()
    DISMISS = auto()
    INVOKE = auto()
    EVOKE = auto()
    MANIFEST = auto()
    DEMANIFEST = auto()
    MATERIALIZE = auto()
    DEMATERIALIZE = auto()
    INCARNATE = auto()
    EXCARNATE = auto()
    EMBODY = auto()
    DISEMBODY = auto()
    INSTANTIATE = auto()
    DEINSTANTIATE = auto()
    REALIZE = auto()
    UNREALIZE = auto()
    ACTUALIZE = auto()
    DEACTUALIZE = auto()
    CONCRETIZE = auto()
    ABSTRACIZE = auto()
    SOLIDIFY = auto()
    LIQUEFY = auto()
    GASIFY = auto()
    PLASMAFY = auto()
    CRYSTALLIZE = auto()
    AMORPHIZE = auto()
    ORGANIZE = auto()
    DISORGANIZE = auto()
    STRUCTURE = auto()
    DESTRUCTURE = auto()
    FORM = auto()
    DEFORM = auto()
    SHAPE = auto()
    UNSHAPE = auto()
    MOLD = auto()
    UNMOLD = auto()
    CRAFT = auto()
    UNCRAFT = auto()
    BUILD = auto()
    UNBUILD = auto()
    CONSTRUCT = auto()
    DECONSTRUCT = auto()
    ASSEMBLE = auto()
    DISASSEMBLE = auto()
    COMPOSE = auto()
    DECOMPOSE = auto()
    SYNTHESIZE = auto()
    ANALYZE = auto()
    SCAN = auto()
    PROBE = auto()
    EXAMINE = auto()
    INSPECT = auto()
    OBSERVE = auto()
    MONITOR = auto()
    TRACK = auto()
    TRACE = auto()
    FOLLOW = auto()


@dataclass
class BattleEvent:
    """Represents a single battle event."""
    event_type: EventType
    data: Dict[str, Any] = field(default_factory=dict)
    duration: float = 0.0  # Duration in seconds
    priority: int = 0  # Higher priority events process first
    blocking: bool = False  # Whether this event blocks others
    timestamp: float = field(default_factory=lambda: __import__('time').time())  # Event creation time
    
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
