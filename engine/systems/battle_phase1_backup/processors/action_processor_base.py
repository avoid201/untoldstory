"""
Base action processor with validation - max 150 lines
Provides common functionality for all specialized action processors
"""

import logging
from typing import Dict, Any, List, Tuple, TYPE_CHECKING
from abc import ABC, abstractmethod

from engine.systems.battle.battle_validation import BattleValidator
from engine.systems.battle.turn_logic import BattleAction, ActionType

if TYPE_CHECKING:
    from engine.systems.battle.battle_state import BattleState
    from engine.systems.monster_instance import MonsterInstance
    from engine.systems.conditions import StatusCondition

logger = logging.getLogger(__name__)


class ActionProcessorBase(ABC):
    """Base class for all action processors with common validation and error handling"""
    
    def __init__(self, battle_state: 'BattleState'):
        """Initialize base processor with battle state and validator"""
        self.state = battle_state
        self.validator = BattleValidator()
    
    @abstractmethod
    def can_handle(self, action: BattleAction) -> bool:
        """Check if this processor can handle the action type"""
        pass
    
    @abstractmethod  
    def execute(self, action: BattleAction) -> Dict[str, Any]:
        """Execute the action with error recovery - MUST return valid dict"""
        pass
    
    def validate_with_recovery(self, action: BattleAction) -> Tuple[bool, List[str]]:
        """Validate action with detailed error messages and recovery"""
        try:
            is_valid = self.validator.validate_battle_action(action)
            if is_valid:
                return True, []
            else:
                return False, ["Action validation failed"]
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return False, [str(e)]
    
    def validate_action_detailed(self, action: BattleAction) -> Tuple[bool, List[str]]:
        """Enhanced validation with detailed error reporting"""
        errors = []
        
        try:
            # Basic validation
            if not action:
                errors.append("Action is None or empty")
                return False, errors
            
            if not hasattr(action, 'action_type'):
                errors.append("Action missing action_type attribute")
                return False, errors
            
            if not action.actor:
                errors.append("Action missing actor")
                return False, errors
            
            # Check if actor can act (not fainted, not prevented by status)
            if getattr(action.actor, 'is_fainted', False):
                errors.append(f"Actor '{action.actor.name}' is fainted and cannot act")
                return False, errors
            
            # Check status conditions that prevent action
            if hasattr(action.actor, 'status_manager'):
                if not action.actor.status_manager.can_act():
                    status = getattr(action.actor.status_manager, 'get_active_status', lambda: 'unknown')()
                    errors.append(f"Actor '{action.actor.name}' cannot act due to status: {status}")
                    return False, errors
            elif hasattr(action.actor, 'status') and action.actor.status:
                # Enhanced status checking with specific conditions
                if action.actor.status == StatusCondition.SLEEP:
                    errors.append(f"Actor '{action.actor.name}' is asleep and cannot act")
                    return False, errors
                elif action.actor.status == StatusCondition.FREEZE:
                    errors.append(f"Actor '{action.actor.name}' is frozen and cannot act")
                    return False, errors
                elif action.actor.status == StatusCondition.PARALYSIS:
                    # Paralysis has a chance to prevent action
                    import random
                    if random.random() < 0.25:  # 25% chance to be fully paralyzed
                        errors.append(f"Actor '{action.actor.name}' is fully paralyzed and cannot act")
                        return False, errors
                elif action.actor.status == StatusCondition.CONFUSION:
                    # Confusion has a chance to prevent action
                    import random
                    if random.random() < 0.50:  # 50% chance to hurt self instead
                        errors.append(f"Actor '{action.actor.name}' is confused and hurt itself")
                        return False, errors
            
            return len(errors) == 0, errors
            
        except Exception as e:
            errors.append(f"Error during action validation: {str(e)}")
            return False, errors
    
    def create_error_result(self, action_type: str, error_msg: str, **kwargs) -> Dict[str, Any]:
        """Create standardized error result with fallback values"""
        result = {
            'type': action_type,
            'success': False,
            'error': error_msg,
            'message': f'Fehler bei {action_type}: {error_msg}'
        }
        result.update(kwargs)
        return result
    
    def create_success_result(self, action_type: str, message: str, **kwargs) -> Dict[str, Any]:
        """Create standardized success result"""
        result = {
            'type': action_type,
            'success': True,
            'message': message
        }
        result.update(kwargs)
        return result
    
    def safe_hp_reduction(self, target: 'MonsterInstance', damage: int) -> int:
        """Safely reduce HP with bounds checking"""
        try:
            if not target or not hasattr(target, 'current_hp'):
                return 0
            
            old_hp = target.current_hp
            target.current_hp = max(0, target.current_hp - damage)
            actual_damage = old_hp - target.current_hp
            
            logger.debug(f"Applied {actual_damage} damage to {target.name} ({old_hp} -> {target.current_hp})")
            return actual_damage
            
        except Exception as e:
            logger.error(f"Error reducing HP: {e}")
            return 0
