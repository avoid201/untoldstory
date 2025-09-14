"""
Action Processor - Facade for specialized action processors
==========================================================
Facade maintaining backward compatibility while delegating to specialized modules.
All action processing logic split into specialized modules to comply with 300-line limit.
"""

import logging
from typing import List, Optional, Dict, Any, Tuple, TYPE_CHECKING

from engine.systems.battle.turn_logic import BattleAction, ActionType
from engine.systems.battle.battle_validation import BattleValidator
from engine.systems.battle.event_processor import EventType
from engine.systems.battle.error_recovery import BattleErrorRecovery, with_battle_fallback
from engine.systems.talent_system import get_talent_database

# Import specialized processors
from .processors.action_processor_core import ActionProcessorCore
from .processors.action_processor_delegation import ActionProcessorDelegation

if TYPE_CHECKING:
    from engine.systems.battle.battle_state import BattleState
    from engine.systems.monster_instance import MonsterInstance
    from engine.systems.moves import Move
    from engine.systems.conditions import StatusCondition
    from engine.systems.battle.turn_processor import TurnProcessor

logger = logging.getLogger(__name__)


class ActionProcessor:
    """
    ACTION PROCESSOR FACADE - Delegates to specialized action processor modules.
    Maintains backward compatibility while using modular architecture.
    """
    
    def __init__(self, battle_state: 'BattleState'):
        """Initialize action processor with battle state and specialized processors."""
        self.state = battle_state
        self.validator = BattleValidator()
        
        # Talent System Integration
        self.talent_database = get_talent_database()
        
        # Initialize specialized processors
        self.core = ActionProcessorCore(battle_state)
        self.delegation = ActionProcessorDelegation(battle_state)
        
        logger.info("ActionProcessor initialized with specialized modules")
    
    # Core functionality - delegate to ActionProcessorCore
    def add_action(self, action: BattleAction) -> bool:
        """Add action to queue - delegates to ActionProcessorCore."""
        return self.core.add_action(action)
    
    def clear_queue(self) -> None:
        """Clear action queue - delegates to ActionProcessorCore."""
        self.core.clear_queue()
    
    def get_queue_size(self) -> int:
        """Get current queue size - delegates to ActionProcessorCore."""
        return self.core.get_queue_size()
    
    def get_next_action(self) -> Optional[BattleAction]:
        """Get next action from queue - delegates to ActionProcessorCore."""
        return self.core.get_next_action()
    
    def peek_next_action(self) -> Optional[BattleAction]:
        """Peek at next action - delegates to ActionProcessorCore."""
        return self.core.peek_next_action()
    
    def validate_action_queue(self) -> Tuple[bool, List[str]]:
        """Validate action queue - delegates to ActionProcessorCore."""
        return self.core.validate_action_queue()
    
    def get_queue_info(self) -> Dict[str, Any]:
        """Get queue information - delegates to ActionProcessorCore."""
        return self.core.get_queue_info()
    
    def can_add_action(self, action: BattleAction) -> Tuple[bool, str]:
        """Check if action can be added - delegates to ActionProcessorCore."""
        return self.core.can_add_action(action)
    
    def get_action_priority(self, action: BattleAction) -> int:
        """Get action priority - delegates to ActionProcessorCore."""
        return self.core.get_action_priority(action)
    
    def sort_actions_by_priority(self, actions: List[BattleAction]) -> List[BattleAction]:
        """Sort actions by priority - delegates to ActionProcessorCore."""
        return self.core.sort_actions_by_priority(actions)
    
    def get_action_statistics(self) -> Dict[str, Any]:
        """Get action statistics - delegates to ActionProcessorCore."""
        return self.core.get_action_statistics()
    
    # Execution functionality - delegate to ActionProcessorDelegation
    def execute_action(self, action: BattleAction) -> Dict[str, Any]:
        """Execute battle action - delegates to ActionProcessorDelegation."""
        return self.delegation.execute_action(action)
    
    def execute_action_with_recovery(self, action: BattleAction) -> Dict[str, Any]:
        """Execute action with recovery - delegates to ActionProcessorDelegation."""
        return self.delegation.execute_action_with_recovery(action)
    
    def get_processor_info(self) -> Dict[str, Any]:
        """Get processor information - delegates to ActionProcessorDelegation."""
        return self.delegation.get_processor_info()
    
    # Legacy compatibility methods
    def process_action(self, action: BattleAction) -> Dict[str, Any]:
        """Legacy method - delegates to execute_action."""
        return self.execute_action(action)
    
    def process_action_with_fallback(self, action: BattleAction) -> Dict[str, Any]:
        """Legacy method - delegates to execute_action_with_recovery."""
        return self.execute_action_with_recovery(action)
    
    def get_available_actions(self, monster: 'MonsterInstance') -> List[str]:
        """Get available actions for monster."""
        try:
            actions = []
            
            # Check if monster is conscious
            if monster and hasattr(monster, 'current_hp') and monster.current_hp > 0:
                actions.extend(['ATTACK', 'SPECIAL', 'ITEM', 'SCOUT'])
                
                # Check if can switch
                if hasattr(self.state, 'player_team'):
                    conscious_monsters = [m for m in self.state.player_team 
                                       if hasattr(m, 'current_hp') and m.current_hp > 0]
                    if len(conscious_monsters) > 1:
                        actions.append('SWITCH')
                
                # Check if can tame
                if hasattr(self.state, 'can_catch') and self.state.can_catch:
                    actions.append('TAME')
                
                # Check if can flee
                if hasattr(self.state, 'can_flee') and self.state.can_flee:
                    actions.append('FLEE')
            
            return actions
            
        except Exception as e:
            logger.error(f"Error getting available actions: {e}")
            return []
    
    def get_available_moves(self, monster: 'MonsterInstance') -> List['Move']:
        """Get available moves for monster."""
        try:
            if not monster or not hasattr(monster, 'get_available_moves'):
                return []
            
            return monster.get_available_moves()
            
        except Exception as e:
            logger.error(f"Error getting available moves: {e}")
            return []
    
    def can_use_move(self, monster: 'MonsterInstance', move: 'Move') -> Tuple[bool, str]:
        """Check if monster can use move."""
        try:
            if not monster or not move:
                return False, "Missing monster or move"
            
            # Check if monster is conscious
            if hasattr(monster, 'current_hp') and monster.current_hp <= 0:
                return False, "Monster is fainted"
            
            # Check MP requirements
            if hasattr(move, 'mp_cost') and hasattr(monster, 'current_mp'):
                if monster.current_mp < move.mp_cost:
                    return False, "Not enough MP"
            
            return True, "Can use move"
            
        except Exception as e:
            logger.error(f"Error checking if move can be used: {e}")
            return False, f"Error: {e}"
    
    def reset_processor(self) -> None:
        """Reset processor state."""
        try:
            self.core.reset_processor()
            logger.info("Action processor reset")
        except Exception as e:
            logger.error(f"Error resetting processor: {e}")
    
    def cleanup(self) -> None:
        """Cleanup processor resources."""
        try:
            self.core.cleanup()
            self.delegation.cleanup()
            logger.info("Action processor cleaned up")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")