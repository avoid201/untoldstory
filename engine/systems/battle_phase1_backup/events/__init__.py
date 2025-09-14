"""
Battle Events Package
====================
Split from monolithic event_processor.py to comply with 300-line limit.
"""

from .event_types import EventType, BattleEvent
from .event_queue import EventQueue
from .event_processor import EventProcessor

__all__ = [
    'EventType',
    'BattleEvent', 
    'EventQueue',
    'EventProcessor'
]
