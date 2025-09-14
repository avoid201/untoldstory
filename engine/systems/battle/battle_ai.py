"""
Battle AI - Consolidated Implementation
=====================================
Single source of truth for all AI logic.
Consolidated from battle_ai.py and EMERGENCY_FACADES.py
"""

import logging
from typing import Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from engine.systems.battle.battle_state import BattleState

logger = logging.getLogger(__name__)


class BattleAI:
    """
    CONSOLIDATED BATTLE AI - Single source of truth for all AI logic.
    Consolidated from battle_ai.py and EMERGENCY_FACADES.py
    """
    
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
    
    def get_action(self, actor, target, available_moves) -> Dict[str, Any]:
        """Get action for AI (compatibility method)."""
        if not available_moves:
            return {
                'action_type': 'ATTACK',
                'move': {'name': 'Tackle', 'power': 40},
                'target': 'player'
            }
        
        # Choose first available move
        move = available_moves[0]
        return {
            'action_type': 'ATTACK',
            'move': {
                'name': move.name,
                'power': getattr(move, 'power', 40),
                'type': getattr(move, 'type', 'Normal')
            },
            'target': 'player'
        }