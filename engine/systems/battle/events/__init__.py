"""
Battle Events Package
====================
Event system components for battle processing.
EventProcessor has been consolidated into main event_processor.py
"""

from .event_types import EventType, BattleEvent
from .event_queue import EventQueue

__all__ = [
    'EventType',
    'BattleEvent', 
    'EventQueue'
]
