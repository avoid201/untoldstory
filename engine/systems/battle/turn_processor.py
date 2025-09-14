"""
Turn Processor - Consolidated Facade
===================================
Facade for all turn processing logic split into specialized modules.
Consolidated from turn_processor.py split into 3 modules.
"""

import logging
import random
import time
from typing import Dict, Any, List, Tuple, Optional, TYPE_CHECKING

# Import specialized turn processor modules
from .processors.turn_processor_core import TurnProcessorCore
from .processors.turn_processor_order import TurnProcessorOrder
from .processors.turn_processor_execution import TurnProcessorExecution

if TYPE_CHECKING:
    from engine.systems.battle.battle_state import BattleState
    from engine.systems.monster_instance import MonsterInstance
    from engine.systems.battle.turn_logic import BattleAction, ActionType
    from engine.systems.battle.event_processor import EventProcessor

from engine.systems.battle.events.event_types import EventType
from engine.systems.battle.turn_logic import ActionType

logger = logging.getLogger(__name__)


class TurnProcessor:
    """
    CONSOLIDATED TURN PROCESSOR - Facade for all turn processing.
    Delegates to specialized modules for different aspects of turn processing.
    """
    
    def __init__(self, battle_state: 'BattleState' = None):
        """Initialize turn processor with specialized modules."""
        self.state = battle_state
        
        # Initialize specialized processors
        self.core = TurnProcessorCore(battle_state)
        self.order = TurnProcessorOrder(battle_state)
        self.execution = TurnProcessorExecution(battle_state)
        
        # Compatibility attributes
        self.turn_count = 0
        self.action_processor = None
        self.current_turn_order: List[Tuple[int, 'BattleAction']] = []
        self.turn_history: List[Dict[str, Any]] = []
        self._rng = random.Random()
        
        # Add turn_order for compatibility
        from engine.systems.battle.turn_logic import TurnOrder
        self.turn_order = TurnOrder()
        
        logger.info("TurnProcessor initialized with specialized modules")
    
    def set_action_processor(self, action_processor):
        """Set action processor for all specialized modules."""
        self.action_processor = action_processor
        self.core.set_action_processor(action_processor)
        self.execution.set_action_processor(action_processor)
        logger.debug("Action processor set for all modules")
    
    # Core turn processing methods - delegate to TurnProcessorCore
    def start_turn(self) -> Dict[str, Any]:
        """Start a new turn - delegates to TurnProcessorCore."""
        result = self.core.start_turn()
        self.turn_count = self.core.turn_count
        return result
    
    def end_turn(self) -> Dict[str, Any]:
        """End current turn - delegates to TurnProcessorCore."""
        result = self.core.end_turn()
        self.turn_count = self.core.turn_count
        return result
    
    def get_turn_info(self) -> Dict[str, Any]:
        """Get current turn information - delegates to TurnProcessorCore."""
        return self.core.get_turn_info()
    
    def reset_turn_state(self):
        """Reset turn state - delegates to TurnProcessorCore."""
        self.core.reset_turn_state()
        self.turn_count = 0
        self.current_turn_order.clear()
        self.turn_history.clear()
    
    def add_turn_to_history(self, turn_data: Dict[str, Any]):
        """Add turn data to history - delegates to TurnProcessorCore."""
        self.core.add_turn_to_history(turn_data)
        self.turn_history = self.core.turn_history
    
    def get_turn_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent turn history - delegates to TurnProcessorCore."""
        return self.core.get_turn_history(limit)
    
    # Turn order calculation methods - delegate to TurnProcessorOrder
    def calculate_turn_order(self, actions: List['BattleAction']) -> List[Tuple[int, 'BattleAction']]:
        """Calculate turn order - delegates to TurnProcessorOrder."""
        return self.order.calculate_turn_order(actions)
    
    def get_turn_order_breakdown(self, actions: List['BattleAction']) -> List[Dict[str, Any]]:
        """Get turn order breakdown - delegates to TurnProcessorOrder."""
        return self.order.get_turn_order_breakdown(actions)
    
    def validate_turn_order(self, turn_order: List[Tuple[int, 'BattleAction']]) -> Tuple[bool, str]:
        """Validate turn order - delegates to TurnProcessorOrder."""
        return self.order.validate_turn_order(turn_order)
    
    def get_priority_breakdown(self) -> Dict[str, int]:
        """Get priority breakdown - delegates to TurnProcessorOrder."""
        return self.order.get_priority_breakdown()
    
    # Turn execution methods - delegate to TurnProcessorExecution
    def execute_turn(self, actions: List['BattleAction']) -> Dict[str, Any]:
        """Execute a complete turn - delegates to TurnProcessorExecution."""
        return self.execution.execute_turn(actions)
    
    def process_turn(self, player_action: 'BattleAction' = None, enemy_action: 'BattleAction' = None) -> Dict[str, Any]:
        """Process a complete turn - delegates to TurnProcessorExecution."""
        if player_action and enemy_action:
            actions = [player_action, enemy_action]
            return self.execution.execute_turn(actions)
        else:
            return self.execution.process_turn(player_action, enemy_action)
    
    def process_multi_battle_turn(self, 
                                 player_actions: List['BattleAction'],
                                 enemy_actions: List['BattleAction']) -> Dict[str, Any]:
        """Process multi-battle turn - delegates to TurnProcessorExecution."""
        return self.execution.process_multi_battle_turn(player_actions, enemy_actions)
    
    # Legacy compatibility methods
    def _execute_single_action(self, action: 'BattleAction') -> Dict[str, Any]:
        """Legacy method - delegates to TurnProcessorExecution."""
        return self.execution._execute_single_action(action)
    
    def _process_end_of_turn(self):
        """Legacy method - delegates to TurnProcessorCore."""
        return self.core._process_end_of_turn()
    
    def _emit_turn_event(self, event_type: EventType, data: Dict[str, Any]):
        """Emit turn event - delegates to TurnProcessorCore."""
        if hasattr(self.state, 'event_processor') and self.state.event_processor:
            self.state.event_processor.emit_event(event_type, data)