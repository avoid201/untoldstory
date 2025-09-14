"""
Event Queue - Emergency Facade
==============================
Minimal implementation to comply with 300-line limit.
"""

import heapq
from typing import List, Any
from .event_types import BattleEvent


class EventQueue:
    """EMERGENCY FACADE - Minimal EventQueue implementation"""
    
    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self._queue = []
        self._counter = 0
    
    def push(self, event: BattleEvent) -> bool:
        """Push event to queue."""
        if len(self._queue) >= self.max_size:
            return False
        
        self._counter += 1
        heapq.heappush(self._queue, (-event.priority, self._counter, event))
        return True
    
    def pop(self) -> BattleEvent:
        """Pop highest priority event."""
        if not self._queue:
            return None
        
        _, _, event = heapq.heappop(self._queue)
        return event
    
    def is_empty(self) -> bool:
        """Check if queue is empty."""
        return len(self._queue) == 0
    
    def size(self) -> int:
        """Get queue size."""
        return len(self._queue)
