"""
Battle AI - Emergency Facade
============================
Minimal implementation to comply with 300-line limit.
"""

import logging
from typing import Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from engine.systems.battle.battle_state import BattleState

logger = logging.getLogger(__name__)


class BattleAI:
    """EMERGENCY FACADE - Minimal BattleAI implementation"""
    
    def __init__(self, difficulty: str = "normal"):
        self.difficulty = difficulty
        logger.info(f"BattleAI initialized with difficulty: {difficulty}")
    
    def choose_action(self, state: 'BattleState') -> Dict[str, Any]:
        """Choose an action for the AI."""
        return {
            'action_type': 'ATTACK',
            'move': {'name': 'Tackle', 'power': 40},
            'target': 'player'
        }
