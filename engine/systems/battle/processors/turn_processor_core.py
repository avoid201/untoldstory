"""
Turn Processor Core - Basic Turn Logic
=====================================
Core turn processing logic and state management.
Split from turn_processor.py to comply with 300-line limit.
"""

import logging
import random
import time
from typing import Dict, Any, List, Tuple, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from engine.systems.battle.battle_state import BattleState
    from engine.systems.monster_instance import MonsterInstance
    from engine.systems.battle.turn_logic import BattleAction, ActionType
    from engine.systems.battle.event_processor import EventProcessor

from engine.systems.battle.events.event_types import EventType
from engine.systems.battle.turn_logic import ActionType

logger = logging.getLogger(__name__)


class TurnProcessorCore:
    """
    Core turn processing logic.
    Handles basic turn state management and initialization.
    """
    
    def __init__(self, battle_state: 'BattleState' = None):
        """Initialize turn processor core."""
        self.state = battle_state
        self.turn_count = 0
        self.action_processor = None
        self.current_turn_order: List[Tuple[int, 'BattleAction']] = []
        self.turn_history: List[Dict[str, Any]] = []
        self._rng = random.Random()
        
        # Add turn_order for compatibility
        from engine.systems.battle.turn_logic import TurnOrder
        self.turn_order = TurnOrder()
        
        logger.info("TurnProcessorCore initialized")
    
    def set_action_processor(self, action_processor):
        """Set action processor."""
        self.action_processor = action_processor
        logger.debug("Action processor set")
    
    def start_turn(self) -> Dict[str, Any]:
        """
        Start a new turn.
        
        Returns:
            Dict with turn start result
        """
        try:
            self.turn_count += 1
            logger.info(f"Starting turn {self.turn_count}")
            
            # Emit turn start event
            if hasattr(self.state, 'event_processor') and self.state.event_processor:
                self.state.event_processor.emit_event(
                    EventType.TURN_START,
                    {'turn_count': self.turn_count}
                )
            
            return {
                'success': True,
                'turn_count': self.turn_count,
                'message': f'Turn {self.turn_count} started'
            }
            
        except Exception as e:
            logger.error(f"Error starting turn: {e}")
            return {
                'success': False,
                'error': f'Failed to start turn: {e}'
            }
    
    def end_turn(self) -> Dict[str, Any]:
        """
        End current turn.
        
        Returns:
            Dict with turn end result
        """
        try:
            logger.info(f"Ending turn {self.turn_count}")
            
            # Emit turn end event
            if hasattr(self.state, 'event_processor') and self.state.event_processor:
                self.state.event_processor.emit_event(
                    EventType.TURN_END,
                    {'turn_count': self.turn_count}
                )
            
            # Process end of turn effects
            self._process_end_of_turn()
            
            return {
                'success': True,
                'turn_count': self.turn_count,
                'message': f'Turn {self.turn_count} ended'
            }
            
        except Exception as e:
            logger.error(f"Error ending turn: {e}")
            return {
                'success': False,
                'error': f'Failed to end turn: {e}'
            }
    
    def _process_end_of_turn(self):
        """Process status effects at end of turn"""
        try:
            if not self.state:
                return
            
            # Process status effects for all monsters
            if hasattr(self.state, 'player_active') and self.state.player_active:
                self._process_monster_status_effects(self.state.player_active)
            
            if hasattr(self.state, 'enemy_active') and self.state.enemy_active:
                self._process_monster_status_effects(self.state.enemy_active)
            
            logger.debug("End of turn status effects processed")
            
        except Exception as e:
            logger.error(f"Error processing end of turn effects: {e}")
    
    def _process_monster_status_effects(self, monster: 'MonsterInstance'):
        """Process status effects for a specific monster."""
        try:
            if not monster or not hasattr(monster, 'status'):
                return
            
            # Process burn damage
            if hasattr(monster.status, 'name') and monster.status.name == 'BURN':
                damage = max(1, monster.max_hp // 8)
                monster.current_hp = max(0, monster.current_hp - damage)
                logger.info(f"{monster.name} takes {damage} burn damage")
            
            # Process poison damage
            elif hasattr(monster.status, 'name') and monster.status.name == 'POISON':
                damage = max(1, monster.max_hp // 16)
                monster.current_hp = max(0, monster.current_hp - damage)
                logger.info(f"{monster.name} takes {damage} poison damage")
            
        except Exception as e:
            logger.error(f"Error processing status effects for {monster.name}: {e}")
    
    def get_turn_info(self) -> Dict[str, Any]:
        """
        Get current turn information.
        
        Returns:
            Dict with turn information
        """
        return {
            'turn_count': self.turn_count,
            'current_turn_order': len(self.current_turn_order),
            'turn_history_length': len(self.turn_history),
            'has_action_processor': self.action_processor is not None
        }
    
    def reset_turn_state(self):
        """Reset turn state for new battle."""
        self.turn_count = 0
        self.current_turn_order.clear()
        self.turn_history.clear()
        logger.info("Turn state reset")
    
    def add_turn_to_history(self, turn_data: Dict[str, Any]):
        """Add turn data to history."""
        try:
            self.turn_history.append({
                'turn_count': self.turn_count,
                'timestamp': time.time(),
                'data': turn_data
            })
            
            # Limit history size
            if len(self.turn_history) > 50:
                self.turn_history.pop(0)
                
        except Exception as e:
            logger.error(f"Error adding turn to history: {e}")
    
    def get_turn_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent turn history.
        
        Args:
            limit: Maximum number of turns to return
            
        Returns:
            List of recent turn data
        """
        return self.turn_history[-limit:] if self.turn_history else []
