"""
Status Conditions System
Unified status condition system for the battle system
"""

from enum import Enum
from typing import Optional

class StatusCondition(Enum):
    """Status conditions that can affect monsters."""
    NONE = "none"
    BURN = "burn"          # Feuer damage over time, halves ATK
    POISON = "poison"      # Seuche damage over time
    PARALYSIS = "paralysis"  # May skip turn, reduces SPD
    SLEEP = "sleep"        # Cannot act for 1-3 turns
    FREEZE = "freeze"      # Cannot act until thawed
    CONFUSION = "confusion"  # May hurt itself
    FLINCH = "flinch"      # Skip next turn only
    BADLY_POISONED = "badly_poisoned"  # Escalating poison damage
    TRAPPED = "trapped"    # Cannot switch out
    CURSE = "curse"        # Loses 1/4 max HP per turn
    TAUNT = "taunt"        # Can only use attacking moves
    TORMENT = "torment"    # Cannot use same move twice in a row
    
    @classmethod
    def from_string(cls, value: str) -> 'StatusCondition':
        """Convert string to StatusCondition with fallback."""
        try:
            if isinstance(value, str):
                return cls(value.lower())
            elif hasattr(value, 'value'):
                return cls(value.value.lower())
            return value
        except ValueError:
            return cls.NONE

# DQMStatusManager removed - functionality integrated into battle/status_processor.py
