"""
Battle Validation Module
Contains all validation logic for battle states and actions
Consolidated validation system for the entire battle system
"""

import logging
from typing import List, Optional, Dict, Any, TYPE_CHECKING
from engine.systems.monster_instance import MonsterInstance

if TYPE_CHECKING:
    from engine.systems.battle.turn_logic import BattleAction

logger = logging.getLogger(__name__)


class BattleValidator:
    """Validates battle states and actions."""
    
    @staticmethod
    def validate_battle_state(player_active: Optional[MonsterInstance],
                             enemy_active: Optional[MonsterInstance],
                             player_team: List[MonsterInstance],
                             enemy_team: List[MonsterInstance]) -> bool:
        """
        Validates the current battle state.
        
        Args:
            player_active: Active player monster
            enemy_active: Active enemy monster
            player_team: Player's team
            enemy_team: Enemy's team
            
        Returns:
            True if the battle state is valid, False otherwise
        """
        try:
            # Check if active monsters exist
            if not player_active or not enemy_active:
                logger.error("Active monsters are missing!")
                return False
            
            # Validate monster stats
            if not BattleValidator._validate_monster_stats(player_active):
                logger.error(f"Invalid stats for player monster: {player_active.name}")
                return False
            
            if not BattleValidator._validate_monster_stats(enemy_active):
                logger.error(f"Invalid stats for enemy monster: {enemy_active.name}")
                return False
            
            # Check if teams are valid
            if not BattleValidator.has_able_monsters(player_team):
                logger.error("No able monsters in player team!")
                return False
            
            if not BattleValidator.has_able_monsters(enemy_team):
                logger.error("No able monsters in enemy team!")
                return False
            
            # Check if battle can continue
            if not BattleValidator.is_battle_valid(player_active, enemy_active, player_team, enemy_team):
                logger.error("Battle cannot continue!")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating battle state: {str(e)}")
            return False
    
    @staticmethod
    def _validate_monster_stats(monster: MonsterInstance) -> bool:
        """
        Validates a monster's stats.
        
        Args:
            monster: The monster to validate
            
        Returns:
            True if all stats are valid, False otherwise
        """
        if not monster:
            return False
        
        try:
            # Check if stats exists and is a dict
            if not hasattr(monster, 'stats') or not isinstance(monster.stats, dict):
                # Try to create stats from current_stats if available
                if hasattr(monster, 'current_stats'):
                    logger.warning(f"Monster {monster.name} has no stats dict, creating from current_stats")
                    monster.stats = {
                        'hp': monster.current_stats.hp if hasattr(monster.current_stats, 'hp') else 100,
                        'atk': monster.current_stats.atk if hasattr(monster.current_stats, 'atk') else 50,
                        'def': monster.current_stats.def_ if hasattr(monster.current_stats, 'def_') else 40,
                        'mag': monster.current_stats.mag if hasattr(monster.current_stats, 'mag') else 45,
                        'res': monster.current_stats.res if hasattr(monster.current_stats, 'res') else 35,
                        'spd': monster.current_stats.spd if hasattr(monster.current_stats, 'spd') else 60
                    }
                else:
                    logger.error(f"Monster {monster.name} has no valid stats!")
                    return False
            
            # Check required stats
            required_stats = ["hp", "atk", "def", "mag", "res", "spd"]
            for stat in required_stats:
                if stat not in monster.stats:
                    logger.error(f"Stat '{stat}' missing for monster {monster.name}!")
                    return False
                
                if not isinstance(monster.stats[stat], (int, float)) or monster.stats[stat] < 0:
                    logger.error(f"Invalid value for stat '{stat}' in monster {monster.name}: {monster.stats[stat]}")
                    return False
            
            # Check stat_stages
            if not hasattr(monster, 'stat_stages') or monster.stat_stages is None:
                logger.warning(f"Monster {monster.name} has no stat_stages, creating default")
                monster.stat_stages = {'atk': 0, 'def': 0, 'mag': 0, 'res': 0, 'spd': 0}
            
            # Check moves
            if not hasattr(monster, 'moves') or not isinstance(monster.moves, list):
                logger.warning(f"Monster {monster.name} has no valid moves, adding basic move")
                # Add a basic move as fallback
                from engine.systems.moves import MoveRegistry
                registry = MoveRegistry()
                basic_move = registry.get_move("tackle")
                if basic_move:
                    monster.moves = [basic_move]
                else:
                    # Create a minimal move object
                    monster.moves = [type('Move', (), {
                        'id': 'tackle',
                        'name': 'Tackle',
                        'power': 40,
                        'type': 'Normal',
                        'category': type('Cat', (), {'value': 'phys'})()
                    })()]
            
            # Check basic attributes
            if not hasattr(monster, 'name') or not hasattr(monster, 'level'):
                logger.error(f"Monster missing basic attributes!")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating monster: {str(e)}")
            return False
    
    @staticmethod
    def has_able_monsters(team: List[MonsterInstance]) -> bool:
        """
        Check if team has any conscious monsters.
        
        Args:
            team: Team to check
            
        Returns:
            True if team has able monsters, False otherwise
        """
        try:
            if not team:
                return False
            
            for monster in team:
                if monster and not getattr(monster, 'is_fainted', False) and monster.current_hp > 0:
                    return True
            return False
        except Exception as e:
            logger.error(f"Error checking able monsters: {str(e)}")
            return False
    
    @staticmethod
    def is_battle_valid(player_active: Optional[MonsterInstance],
                       enemy_active: Optional[MonsterInstance],
                       player_team: List[MonsterInstance],
                       enemy_team: List[MonsterInstance]) -> bool:
        """
        Check if battle can continue.
        
        Args:
            player_active: Active player monster
            enemy_active: Active enemy monster
            player_team: Player's team
            enemy_team: Enemy's team
            
        Returns:
            True if battle can continue, False otherwise
        """
        try:
            # Check if teams have able monsters
            if not BattleValidator.has_able_monsters(player_team):
                return False
            if not BattleValidator.has_able_monsters(enemy_team):
                return False
            
            # Check if active monsters are valid and not fainted
            if not player_active or getattr(player_active, 'is_fainted', False):
                return False
            if not enemy_active or getattr(enemy_active, 'is_fainted', False):
                return False
            
            return True
        except Exception as e:
            logger.error(f"Error validating battle: {str(e)}")
            return False
    
    @staticmethod
    def validate_action_complete(action, state=None, is_player=True, detailed=False):
        """
        CONSOLIDATED ACTION VALIDATION - Single source of truth for ALL action validation.
        Replaces all validate_action, _validate_action, and validate_action_with_errors methods.
        
        Args:
            action: Action dict or BattleAction object to validate
            state: Optional BattleState for context validation
            is_player: Whether this is a player action (for dict actions)
            detailed: If True, returns detailed error information
            
        Returns:
            If detailed=False: bool (is_valid)
            If detailed=True: dict with 'valid', 'errors', 'warnings' keys
        """
        try:
            # Handle None/empty actions
            if not action:
                error_msg = "Action validation failed: Action is None or empty"
                logger.error(error_msg)
                if detailed:
                    return {"valid": False, "errors": [error_msg], "warnings": []}
                return False
            
            errors = []
            warnings = []
            
            # Handle dict actions (legacy support)
            if isinstance(action, dict):
                is_valid, error_list = BattleValidator.validate_action_data(action, is_player)
                errors.extend(error_list)
                
                # Additional context validation if state provided
                if state and is_valid:
                    context_valid, context_errors = BattleValidator._validate_action_context(action, state)
                    if not context_valid:
                        errors.extend(context_errors)
                        is_valid = False
                
                if detailed:
                    return {"valid": is_valid, "errors": errors, "warnings": warnings}
                return is_valid
            
            # Handle BattleAction objects
            if hasattr(action, 'action_type'):
                is_valid = BattleValidator.validate_battle_action(action)
                
                # Additional context validation if state provided
                if state and is_valid:
                    context_valid, context_errors = BattleValidator._validate_battle_action_context(action, state)
                    if not context_valid:
                        errors.extend(context_errors)
                        is_valid = False
                
                if detailed:
                    return {"valid": is_valid, "errors": errors, "warnings": warnings}
                return is_valid
            
            # Unknown action type
            error_msg = f"Action validation failed: Unknown action type {type(action)}"
            logger.error(error_msg)
            if detailed:
                return {"valid": False, "errors": [error_msg], "warnings": []}
            return False
            
        except Exception as e:
            error_msg = f"Action validation error: {e}"
            logger.error(error_msg)
            if detailed:
                return {"valid": False, "errors": [error_msg], "warnings": []}
            return False
    
    @staticmethod
    def _validate_action_context(action_dict: dict, state) -> tuple[bool, List[str]]:
        """Validate action in context of current battle state."""
        errors = []
        
        try:
            # Check if action is possible in current phase
            from engine.systems.battle.battle_enums import BattlePhase
            if hasattr(state, 'phase') and state.phase != BattlePhase.INPUT:
                errors.append(f"Action not allowed in {state.phase.name} phase")
            
            # Check if actors are valid
            if 'actor' in action_dict:
                actor = action_dict['actor']
                if hasattr(actor, 'is_fainted') and actor.is_fainted:
                    errors.append("Actor is fainted and cannot act")
            
            # Check if targets are valid
            if 'target' in action_dict:
                target = action_dict['target']
                if hasattr(target, 'is_fainted') and target.is_fainted:
                    errors.append("Target is fainted")
            
            return len(errors) == 0, errors
            
        except Exception as e:
            logger.error(f"Context validation error: {e}")
            return False, [f"Context validation error: {e}"]
    
    @staticmethod
    def _validate_battle_action_context(action, state) -> tuple[bool, List[str]]:
        """Validate BattleAction in context of current battle state."""
        errors = []
        
        try:
            # Check if action is possible in current phase
            from engine.systems.battle.battle_enums import BattlePhase
            if hasattr(state, 'phase') and state.phase != BattlePhase.INPUT:
                errors.append(f"Action not allowed in {state.phase.name} phase")
            
            # Check if actor is valid
            if hasattr(action, 'actor') and action.actor:
                if hasattr(action.actor, 'is_fainted') and action.actor.is_fainted:
                    errors.append("Actor is fainted and cannot act")
            
            # Check if target is valid
            if hasattr(action, 'target') and action.target:
                if hasattr(action.target, 'is_fainted') and action.target.is_fainted:
                    errors.append("Target is fainted")
            
            return len(errors) == 0, errors
            
        except Exception as e:
            logger.error(f"BattleAction context validation error: {e}")
            return False, [f"BattleAction context validation error: {e}"]
    
    @staticmethod
    def validate_action_dict(action: dict) -> bool:
        """
        Validate a battle action dictionary.
        
        Args:
            action: Action dictionary to validate
            
        Returns:
            True if action is valid, False otherwise
        """
        try:
            # Check if action is a dict
            if not action or not isinstance(action, dict):
                logger.error("Action validation failed: Not a valid dictionary")
                return False
            
            # Check required fields - support ALL action key variations
            action_type = (action.get('type') or 
                          action.get('action') or 
                          action.get('action_type'))
            
            if not action_type:
                logger.error("Action validation failed: Missing action type (need 'type', 'action', or 'action_type')")
                return False
            
            # Special handling for UI actions
            if action_type == 'menu_select':
                return 'option' in action
            
            # Check battle action requirements
            if 'actor' not in action:
                logger.error("Action validation failed: Battle action needs actor")
                return False
            
            actor = action.get('actor')
            if not actor or not isinstance(actor, MonsterInstance):
                logger.error("Action validation failed: Invalid actor in action")
                return False
            
            # Check if actor is not fainted
            if actor.is_fainted:
                logger.error(f"Action validation failed: Actor '{actor.name}' is fainted and cannot perform action")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Action dict validation error: {e}")
            return False
    
    @staticmethod
    def validate_action_data(action_data: Dict[str, Any], is_player: bool = True) -> tuple[bool, List[str]]:
        """
        Validate action data structure with comprehensive checks and standardized error messages.
        
        Args:
            action_data: Action data dictionary to validate
            is_player: Whether this is a player action (for context)
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        try:
            # Check required fields
            if not action_data:
                errors.append("Action validation failed: No action data provided")
                return False, errors
            
            if not isinstance(action_data, dict):
                errors.append("Action validation failed: Action data must be a dictionary")
                return False, errors
            
            # Must have action type - support ALL key variations
            action_type = (action_data.get('type') or 
                          action_data.get('action') or 
                          action_data.get('action_type'))
            
            if not action_type:
                errors.append("Action validation failed: Missing action type (need 'type', 'action', or 'action_type')")
                return False, errors
            
            # Validate action type exists
            try:
                from engine.systems.battle.turn_logic import ActionType
                ActionType.from_string(action_type)
            except (KeyError, ValueError):
                errors.append(f"Action validation failed: Invalid action type '{action_type}'")
                return False, errors
            
            # Type-specific validation with detailed error messages
            if action_type in ['attack', 'move', 'skill']:
                if not action_data.get('move') and not action_data.get('move_id') and not action_data.get('move_name'):
                    errors.append(f"Action validation failed: {action_type} action requires 'move', 'move_id', or 'move_name' field")
            
            elif action_type == 'item':
                if not action_data.get('item_id') and not action_data.get('item'):
                    errors.append("Action validation failed: Item action requires 'item_id' or 'item' field")
            
            elif action_type == 'switch':
                if not action_data.get('switch_to'):
                    errors.append("Action validation failed: Switch action requires 'switch_to' field")
            
            elif action_type == 'tame':
                if not action_data.get('target'):
                    errors.append("Action validation failed: Tame action requires 'target' field")
            
            elif action_type == 'use_meat':
                if not action_data.get('meat_type'):
                    errors.append("Action validation failed: Use meat action requires 'meat_type' field")
            
            elif action_type == 'scout':
                if not action_data.get('target'):
                    errors.append("Action validation failed: Scout action requires 'target' field")
            
            # Validate actor if present
            actor = action_data.get('actor')
            if actor:
                if hasattr(actor, 'is_fainted') and actor.is_fainted:
                    errors.append(f"Action validation failed: Actor '{actor.name}' is fainted and cannot act")
                    return False, errors
            
            return len(errors) == 0, errors
            
        except Exception as e:
            errors.append(f"Action validation error: {e}")
            return False, errors
    
    @staticmethod
    def validate_battle_action(action: 'BattleAction') -> bool:
        """
        Validate BattleAction object with comprehensive error checking.
        
        Args:
            action: BattleAction to validate
            
        Returns:
            True if action is valid, False otherwise
        """
        try:
            if not action:
                logger.error("BattleAction validation failed: Action is None")
                return False
            
            if not hasattr(action, 'action_type'):
                logger.error("BattleAction validation failed: Missing action_type attribute")
                return False
            
            if not action.actor:
                logger.error("BattleAction validation failed: Missing actor")
                return False
            
            # Check if actor can act (not fainted, not prevented by status)
            if getattr(action.actor, 'is_fainted', False) or action.actor.current_hp <= 0:
                logger.error(f"BattleAction validation failed: Actor '{action.actor.name}' is fainted (HP: {action.actor.current_hp})")
                return False
            
            # Check status conditions that prevent action
            if hasattr(action.actor, 'status_manager'):
                if not action.actor.status_manager.can_act():
                    status = getattr(action.actor.status_manager, 'get_active_status', lambda: 'unknown')()
                    logger.error(f"BattleAction validation failed: Actor '{action.actor.name}' cannot act due to status: {status}")
                    return False
            
            # Validate action-specific requirements with detailed error messages
            if action.action_type.name == 'ATTACK':
                if not action.target:
                    logger.error("BattleAction validation failed: Attack action missing target monster")
                    return False
                if not action.move:
                    logger.error("BattleAction validation failed: Attack action missing move")
                    return False
            
            elif action.action_type.name == 'SWITCH':
                if not action.switch_to:
                    logger.error("BattleAction validation failed: Switch action missing switch_to target")
                    return False
            
            elif action.action_type.name == 'ITEM':
                if not action.item_id:
                    logger.error("BattleAction validation failed: Item action missing item_id")
                    return False
            
            elif action.action_type.name == 'TAME':
                if not action.target:
                    logger.error("BattleAction validation failed: Tame action missing target monster")
                    return False
            
            elif action.action_type.name == 'USE_MEAT':
                if not action.meat_type:
                    logger.error("BattleAction validation failed: Use meat action missing meat_type")
                    return False
            
            elif action.action_type.name == 'SCOUT':
                if not action.target:
                    logger.error("BattleAction validation failed: Scout action missing target monster")
                    return False
            
            # Action is valid
            logger.debug(f"BattleAction validation passed: {action.action_type.name}")
            return True
            
        except Exception as e:
            logger.error(f"BattleAction validation error: {e}")
            return False
    
    @staticmethod
    def validate_action_sequence(actions: List['BattleAction']) -> tuple[bool, List[str]]:
        """
        Validate a sequence of actions - consolidated from turn_logic.
        
        Args:
            actions: List of BattleActions
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        try:
            for i, action in enumerate(actions):
                if not action:
                    errors.append(f"Action {i}: Action is None")
                    continue
                
                if not BattleValidator.validate_battle_action(action):
                    errors.append(f"Action {i}: Invalid action")
                    continue
                
                # Check for duplicate actor actions
                for j, other_action in enumerate(actions[i+1:], i+1):
                    if (action.actor and other_action.actor and 
                        action.actor == other_action.actor):
                        errors.append(f"Action {i} and {j}: Duplicate actor")
            
            return len(errors) == 0, errors
            
        except Exception as e:
            errors.append(f"Error in action sequence validation: {e}")
            return False, errors
