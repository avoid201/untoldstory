"""
Action Processor - Handles Action Management
Manages action queuing, validation, and execution
"""

import logging
import random
from typing import List, Optional, Dict, Any, Tuple, TYPE_CHECKING

from engine.systems.battle.turn_logic import BattleAction, ActionType
from engine.systems.battle.battle_validation import BattleValidator
from engine.systems.battle.meat_system import MeatSystem
from engine.systems.battle.event_processor import EventType
from engine.systems.unified_damage_calculator import unified_damage_calculator
from engine.systems.talent_system import get_talent_database

if TYPE_CHECKING:
    from engine.systems.battle.battle_state import BattleState
    from engine.systems.monster_instance import MonsterInstance
    from engine.systems.moves import Move
    from engine.systems.conditions import StatusCondition
    from engine.systems.battle.turn_processor import TurnProcessor

logger = logging.getLogger(__name__)


class ActionProcessor:
    """
    Manages only actions and their execution.
    Handles action queuing, validation, and conversion.
    """
    
    def __init__(self, battle_state: 'BattleState'):
        """Initialize action processor with battle state."""
        self.state = battle_state
        self.validator = BattleValidator()
        self.action_queue: List[BattleAction] = []
        
        # Talent System Integration
        self.talent_database = get_talent_database()
    
    def queue_action(self, action) -> bool:
        """Queue action - single conversion point."""
        try:
            # Import the single source of truth
            from engine.systems.battle.turn_logic import create_action_from_dict
            
            if isinstance(action, dict):
                # Use actors from state
                battle_action = create_action_from_dict(
                    action,
                    actor=self.state.player_active if action.get('actor') == 'player' else self.state.enemy_active,
                    target=self.state.enemy_active if action.get('target') == 'enemy' else self.state.player_active
                )
            else:
                battle_action = action
            
            if not battle_action or not self.validate_action(battle_action):
                return False
                
            self.action_queue.append(battle_action)
            logger.info(f"Action queued: {battle_action.action_type.name}")
            
            # EMIT ACTION_QUEUED EVENT
            if hasattr(self.state, 'event_processor') and self.state.event_processor:
                self.state.event_processor.emit_event(
                    EventType.ACTION_ANNOUNCE,
                    {'action': battle_action.action_type.name, 'actor': battle_action.actor.name}
                )
            return True
        except Exception as e:
            logger.error(f"Failed to queue action: {e}")
            return False
    
    def execute_action(self, action: BattleAction) -> Dict[str, Any]:
        """
        Execute a single action.
        
        Args:
            action: BattleAction to execute
            
        Returns:
            Dictionary with action result
        """
        try:
            logger.debug(f"Executing action: {action.action_type.name} by {action.actor.name}")
            
            # Validate action before execution
            if not self.validate_action(action):
                return {'error': 'Invalid action', 'action_type': action.action_type.name}
            
            # Execute based on action type
            if action.action_type == ActionType.ATTACK:
                return self._execute_attack(action)
            elif action.action_type == ActionType.TAME:
                return self._execute_tame(action)
            elif action.action_type == ActionType.FLEE:
                return self._execute_flee(action)
            elif action.action_type == ActionType.SWITCH:
                return self._execute_switch(action)
            elif action.action_type == ActionType.ITEM:
                return self._execute_item(action)
            elif action.action_type == ActionType.USE_MEAT:
                return self._execute_use_meat(action)
            elif action.action_type == ActionType.SCOUT:
                return self._execute_scout(action)
            else:
                logger.warning(f"Unknown action type: {action.action_type}")
                return {'error': 'Unknown action type', 'action_type': action.action_type.name}
            
        except Exception as e:
            logger.error(f"Error executing action: {e}")
            return {'error': str(e), 'action_type': action.action_type.name}
    
    def validate_action(self, action: BattleAction) -> bool:
        """
        Validate an action before execution using BattleValidator.
        
        Args:
            action: BattleAction to validate
            
        Returns:
            True if action is valid, False otherwise
        """
        return BattleValidator.validate_battle_action(action)
    
    def validate_action_with_errors(self, action: BattleAction, state: 'BattleState') -> Tuple[bool, List[str]]:
        """
        Validate an action with detailed error reporting.
        
        Args:
            action: BattleAction to validate
            state: Current battle state for context
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
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
            
            # Validate action-specific requirements
            if action.action_type.name == 'ATTACK':
                if not action.target:
                    errors.append("Attack action missing target monster")
                elif action.target.current_hp <= 0:
                    errors.append(f"Target '{action.target.name}' is already fainted")
                if not action.move:
                    errors.append("Attack action missing move")
            
            elif action.action_type.name == 'SWITCH':
                if not action.switch_to:
                    errors.append("Switch action missing switch_to target")
            
            elif action.action_type.name == 'ITEM':
                if not action.item_id:
                    errors.append("Item action missing item_id")
            
            elif action.action_type.name == 'TAME':
                if not action.target:
                    errors.append("Tame action missing target monster")
                if not state.can_catch:
                    errors.append("Taming is not allowed in this battle")
            
            elif action.action_type.name == 'USE_MEAT':
                if not action.meat_type:
                    errors.append("Use meat action missing meat_type")
            
            elif action.action_type.name == 'SCOUT':
                if not action.target:
                    errors.append("Scout action missing target monster")
            
            return len(errors) == 0, errors
            
        except Exception as e:
            errors.append(f"Error during action validation: {str(e)}")
            return False, errors
    
    def get_available_actions(self, monster: 'MonsterInstance') -> List[BattleAction]:
        """
        Get all available actions for a monster.
        
        Args:
            monster: Monster to get actions for
            
        Returns:
            List of available BattleActions
        """
        try:
            available_actions = []
            
            if not monster or monster.current_hp <= 0:
                return available_actions
            
            # Check if monster can act
            if hasattr(monster, 'status_manager'):
                if not monster.status_manager.can_act():
                    return available_actions
            elif hasattr(monster, 'status') and monster.status:
                # Fallback for direct status checking
                if monster.status.value in ['sleep', 'freeze', 'paralysis']:
                    return available_actions
            
            # Get available moves
            available_moves = []
            if hasattr(monster, 'moves'):
                for move in monster.moves:
                    if self._can_use_move(move, monster):
                        available_moves.append(move)
            
            # Create attack actions for available moves
            for move in available_moves:
                action = BattleAction(
                    action_type=ActionType.ATTACK,
                    actor=monster,
                    move=move,
                    target=self.state.enemy_active  # Default target
                )
                available_actions.append(action)
            
            # Add switch actions for other team members
            if monster == self.state.player_active:
                for team_member in self.state.player_team:
                    if team_member != monster and team_member.current_hp > 0:
                        action = BattleAction(
                            action_type=ActionType.SWITCH,
                            actor=monster,
                            switch_to=team_member
                        )
                        available_actions.append(action)
            
            # Add item actions (if items are available)
            # This would be implemented based on inventory system
            
            # Add flee action (if allowed)
            if self.state.can_flee:
                action = BattleAction(
                    action_type=ActionType.FLEE,
                    actor=monster,
                    target=monster
                )
                available_actions.append(action)
            
            # Add tame action (if applicable)
            if self.state.can_catch and self.state.enemy_active:
                action = BattleAction(
                    action_type=ActionType.TAME,
                    actor=monster,
                    target=self.state.enemy_active
                )
                available_actions.append(action)
            
            return available_actions
            
        except Exception as e:
            logger.error(f"Error getting available actions: {e}")
            return []
    
    def _can_use_move(self, move: 'Move', monster: 'MonsterInstance') -> bool:
        """Check if monster can use move"""
        try:
            # Basic validation
            if not move or not monster:
                return False
            
            # Check if monster is not fainted
            if getattr(monster, 'is_fainted', False) or monster.current_hp <= 0:
                return False
            
            # Check status effects
            if hasattr(monster, 'status'):
                if monster.status == StatusCondition.SLEEP:
                    return False
            
            # DQM-style: Moves have unlimited usage (no PP system)
            # Check if move is generally usable
            if hasattr(move, 'can_use'):
                return move.can_use()
            
            # Fallback: Move is usable if it exists
            return True
            
        except Exception as e:
            logger.error(f"Error in move validation: {e}")
            return False
    
    def clear_queue(self) -> None:
        """Clear the action queue."""
        try:
            self.action_queue.clear()
            logger.debug("Action queue cleared")
            
        except Exception as e:
            logger.error(f"Error clearing action queue: {e}")
    
    def get_action_queue(self) -> List[BattleAction]:
        """Get current action queue."""
        return self.action_queue.copy()
    
    def has_actions(self) -> bool:
        """Check if there are actions in the queue."""
        return bool(self.action_queue)
    
    def get_queue_length(self) -> int:
        """Get the number of actions in the queue."""
        return len(self.action_queue)
    
    def process_player_action(self, state: 'BattleState', action) -> Dict[str, Any]:
        """Process action - accept dict OR BattleAction with robust validation."""
        try:
            logger.debug(f"Processing player action: {type(action)} - {action}")
            
            # Ensure we have required actors
            if not state.player_active:
                action_type = action.get('action_type', 'unknown') if isinstance(action, dict) else getattr(action, 'action_type', 'unknown')
                return {
                    'success': False, 
                    'error': 'No active player monster',
                    'action_type': action_type
                }
            
            # Convert to BattleAction if needed
            if isinstance(action, dict):
                from engine.systems.battle.turn_logic import create_action_from_dict
                battle_action = create_action_from_dict(
                    action,
                    actor=state.player_active,
                    target=state.enemy_active
                )
                if not battle_action:
                    return {"success": False, "error": "Invalid action format"}
            else:
                battle_action = action
            
            # Validate using BattleValidator
            is_valid, errors = self.validate_action_with_errors(battle_action, state)
            if not is_valid:
                return {"success": False, "errors": errors}
            
            # Execute
            result = self.execute_action(battle_action)
            return {"success": True, "result": result}
            
        except Exception as e:
            logger.error(f"Action processing failed: {e}")
            return {"success": False, "error": str(e)}
    
    # Private methods for action execution
    
    
    def _execute_attack(self, action: BattleAction) -> Dict[str, Any]:
        """Execute an attack action with robust error recovery."""
        try:
            # Validate inputs before damage calculation
            if not action.actor or not action.target or not action.move:
                return {
                    'type': 'attack',
                    'damage': 0,
                    'is_critical': False,
                    'effectiveness': 1.0,
                    'message': 'Invalid attack action',
                    'error': 'Missing actor, target, or move'
                }
            
            # Check if target is already fainted
            if getattr(action.target, 'is_fainted', False):
                return {
                    'type': 'attack',
                    'damage': 0,
                    'is_critical': False,
                    'effectiveness': 1.0,
                    'message': 'Target is already fainted',
                    'error': 'Target already fainted'
                }
            
            # VOR damage calculation: Message-Event für "X setzt Y ein!"
            if hasattr(self.state, 'event_processor') and self.state.event_processor:
                self.state.event_processor.emit_event(
                    EventType.MESSAGE_SHOW,
                    {'message': f"{action.actor.name} setzt {action.move.name} ein!", 'duration': 1.5}
                )
            
            # Apply talent-based passive abilities before damage calculation
            self._apply_talent_passives(action)
            
            # Use unified damage calculator with error recovery
            calc = unified_damage_calculator
            damage_result = calc.calculate_damage(
                attacker=action.actor,
                defender=action.target,
                move=action.move
            )
            
            # Validate damage result
            if not damage_result or not hasattr(damage_result, 'damage'):
                logger.warning("Damage calculation returned invalid result, using fallback")
                damage_result = type('DamageResult', (), {
                    'damage': max(1, action.move.power // 2),
                    'is_critical': False,
                    'effectiveness': 1.0,
                    'get_message': lambda: "Normal damage"
                })()
            
            # Ensure damage is non-negative
            actual_damage = max(0, getattr(damage_result, 'damage', 0))
            
            # Apply damage with safety checks
            if hasattr(action.target, 'current_hp'):
                old_hp = action.target.current_hp
                action.target.current_hp = max(0, action.target.current_hp - actual_damage)
                logger.debug(f"Applied {actual_damage} damage to {action.target.name} ({old_hp} -> {action.target.current_hp})")
                
                # NACH Damage-Application: HP_BAR_UPDATE Event
                if hasattr(self.state, 'event_processor') and self.state.event_processor:
                    self.state.event_processor.emit_event(
                        EventType.HP_BAR_UPDATE,
                        {'target': action.target, 'old_hp': old_hp, 'new_hp': action.target.current_hp}
                    )
                
                # DAMAGE_DEALT Event für Damage-Numbers
                if hasattr(self.state, 'event_processor') and self.state.event_processor:
                    self.state.event_processor.emit_event(
                        EventType.DAMAGE_DEALT,
                        {
                            'target': action.target, 
                            'damage': actual_damage, 
                            'is_critical': getattr(damage_result, 'is_critical', False),
                            'is_super_effective': getattr(damage_result, 'effectiveness', 1.0) > 1.0,
                            'attacker': action.actor
                        }
                    )
            
            # DQM-style: No PP consumption - Moves have unlimited usage
            
            return {
                'type': 'attack',
                'damage': actual_damage,
                'is_critical': getattr(damage_result, 'is_critical', False),
                'effectiveness': getattr(damage_result, 'effectiveness', 1.0),
                'message': getattr(damage_result, 'get_message', lambda: "Attack successful")()
            }
            
        except Exception as e:
            logger.error(f"Error executing attack: {e}")
            # Fallback damage calculation
            try:
                fallback_damage = max(1, action.move.power // 2) if action.move else 10
                if hasattr(action.target, 'current_hp'):
                    action.target.current_hp = max(0, action.target.current_hp - fallback_damage)
                
                return {
                    'type': 'attack',
                    'damage': fallback_damage,
                    'is_critical': False,
                    'effectiveness': 1.0,
                    'message': 'Fallback damage applied',
                    'error': str(e)
                }
            except Exception as e2:
                logger.error(f"Fallback damage calculation also failed: {e2}")
                return {
                    'type': 'attack',
                    'damage': 0,
                    'is_critical': False,
                    'effectiveness': 1.0,
                    'message': 'Attack failed completely',
                    'error': f"Primary: {e}, Fallback: {e2}"
                }
    
    def _apply_talent_passives(self, action: BattleAction) -> None:
        """
        Apply passive abilities from talents before action execution.
        
        Args:
            action: BattleAction to apply passives to
        """
        try:
            if not action.talent_instance or not hasattr(action.talent_instance, 'get_passive_abilities'):
                return
            
            # Get passive abilities from talent
            passive_abilities = action.talent_instance.get_passive_abilities()
            
            # Apply each passive ability
            for ability in passive_abilities:
                ability_type = ability.get('type', '')
                value = ability.get('value', 1.0)
                
                if ability_type == 'stat_boost':
                    # Apply stat boosts to monster
                    stat_type = ability.get('stat', '')
                    if stat_type and hasattr(action.actor, 'stats'):
                        current_value = action.actor.stats.get(stat_type, 0)
                        action.actor.stats[stat_type] = int(current_value * value)
                
                elif ability_type == 'move_power_boost':
                    # Apply move power boost
                    if action.move and hasattr(action.move, 'power'):
                        action.move.power = int(action.move.power * value)
                
                elif ability_type == 'accuracy_boost':
                    # Apply accuracy boost
                    if action.move and hasattr(action.move, 'accuracy'):
                        action.move.accuracy = min(100, int(action.move.accuracy * value))
                
                elif ability_type == 'crit_boost':
                    # Apply critical hit boost
                    if hasattr(action.actor, 'crit_rate'):
                        action.actor.crit_rate = min(100, int(action.actor.crit_rate * value))
            
        except Exception as e:
            logger.error(f"Error applying talent passives: {e}")
    
    def _execute_tame(self, action: BattleAction) -> Dict[str, Any]:
        """Execute a tame action with MeatSystem integration and robust error recovery."""
        try:
            # VOR Taming: Message-Event für "X versucht Y zu zähmen!"
            if hasattr(self.state, 'event_processor') and self.state.event_processor:
                self.state.event_processor.emit_event(
                    EventType.MESSAGE_SHOW,
                    {'message': f"{action.actor.name} versucht {action.target.name} zu zähmen!", 'duration': 1.5}
                )
            
            # Get MeatSystem instance with fallback
            meat_system = None
            if hasattr(self.state, 'meat_system') and self.state.meat_system:
                meat_system = self.state.meat_system
            else:
                meat_system = MeatSystem()  # Singleton instance
                logger.warning("Using fallback MeatSystem instance")
            
            # Check if taming is allowed
            if not getattr(self.state, 'can_catch', False):
                return {
                    'type': 'tame',
                    'success': False,
                    'message': 'Zähmung ist in diesem Kampf nicht möglich!'
                }
            
            if not action.target or getattr(action.target, 'is_fainted', False) or action.target.current_hp <= 0:
                return {
                    'type': 'tame',
                    'success': False,
                    'message': 'Ziel ist nicht verfügbar für Zähmung!'
                }
            
            # Calculate taming chance using MeatSystem
            base_chance = 0.3  # 30% base chance
            hp_percent = action.target.current_hp / action.target.max_hp
            monster_rank = getattr(action.target, 'rank', 'D')  # Default to D rank
            monster_status = None
            
            # Get status condition if available
            if hasattr(action.target, 'status_manager'):
                monster_status = action.target.status_manager.get_active_status()
            
            # Use MeatSystem to calculate final taming chance
            taming_result = meat_system.calculate_taming_chance(
                base_chance=base_chance,
                monster_hp_percent=hp_percent,
                monster_rank=monster_rank,
                monster_status=monster_status
            )
            
            final_chance = taming_result['final_chance']
            success = random.random() < final_chance
            
            # Log taming attempt
            logger.info(f"Taming attempt: {action.target.name} - Chance: {final_chance:.2%} - Success: {success}")
            
            if success:
                # Successful taming
                self.state.caught_monster = action.target
                message = f"{action.target.name} wurde erfolgreich gezähmt!"
                
                # Add meat bonus info to message if applicable
                if taming_result['meat_active']:
                    message += f" (Fleisch-Bonus: {taming_result['meat_name']})"
                
                return {
                    'type': 'tame',
                    'success': True,
                    'message': message,
                    'caught_monster': action.target,
                    'taming_chance': final_chance,
                    'meat_bonus': taming_result['modifiers']['meat_bonus']
                }
            else:
                # Failed taming
                message = f"Zähmung von {action.target.name} fehlgeschlagen!"
                
                # Add chance info to message
                message += f" (Chance war {final_chance:.1%})"
                
                return {
                    'type': 'tame',
                    'success': False,
                    'message': message,
                    'taming_chance': final_chance,
                    'meat_bonus': taming_result['modifiers']['meat_bonus']
                }
                
        except Exception as e:
            logger.error(f"Error executing tame: {e}")
            return {
                'type': 'tame',
                'success': False,
                'error': str(e),
                'message': f'Fehler bei Zähmung: {str(e)}'
            }
    
    def _execute_flee(self, action: BattleAction) -> Dict[str, Any]:
        """Execute a flee action."""
        try:
            # This would delegate to the flee calculation system
            # For now, return a placeholder result
            return {
                'type': 'flee',
                'actor': action.actor,
                'success': True,  # Placeholder
                'message': 'Successfully fled'
            }
        except Exception as e:
            logger.error(f"Error executing flee: {e}")
            return {'error': str(e), 'type': 'flee'}
    
    def _execute_switch(self, action: BattleAction) -> Dict[str, Any]:
        """Execute a switch action."""
        try:
            # VOR Switch: Message-Event für "X wechselt zu Y!"
            if hasattr(self.state, 'event_processor') and self.state.event_processor:
                self.state.event_processor.emit_event(
                    EventType.MESSAGE_SHOW,
                    {'message': f"{action.actor.name} wechselt zu {action.switch_to.name}!", 'duration': 1.5}
                )
            
            # This would handle monster switching
            # For now, return a placeholder result
            return {
                'type': 'switch',
                'actor': action.actor,
                'old_monster': action.actor,
                'new_monster': action.switch_to,
                'success': True
            }
        except Exception as e:
            logger.error(f"Error executing switch: {e}")
            return {'error': str(e), 'type': 'switch'}
    
    def _execute_item(self, action: BattleAction) -> Dict[str, Any]:
        """Execute an item action."""
        try:
            # VOR Item Usage: Message-Event für "X verwendet Item!"
            if hasattr(self.state, 'event_processor') and self.state.event_processor:
                item_name = action.item.name if hasattr(action, 'item') and action.item else "Item"
                self.state.event_processor.emit_event(
                    EventType.MESSAGE_SHOW,
                    {'message': f"{action.actor.name} verwendet {item_name}!", 'duration': 1.5}
                )
            
            # Get game instance (via battle_state)
            if hasattr(self.state, 'game') and hasattr(self.state.game, 'inventory'):
                success = self.state.game.inventory.remove_item(action.item_id, 1)
                if not success:
                    return {'error': 'Item not available'}
            
            # This would delegate to the item system
            # For now, return a placeholder result
            return {
                'type': 'item',
                'actor': action.actor,
                'target': action.target,
                'item': action.item,
                'success': True
            }
        except Exception as e:
            logger.error(f"Error executing item: {e}")
            return {'error': str(e), 'type': 'item'}
    
    def _execute_use_meat(self, action: BattleAction) -> Dict[str, Any]:
        """Execute a use meat action with MeatSystem integration and robust error recovery."""
        try:
            # VOR Meat Usage: Message-Event für "X verwendet Fleisch!"
            if hasattr(self.state, 'event_processor') and self.state.event_processor:
                meat_name = action.meat_type.name if action.meat_type else "Fleisch"
                self.state.event_processor.emit_event(
                    EventType.MESSAGE_SHOW,
                    {'message': f"{action.actor.name} verwendet {meat_name}!", 'duration': 1.5}
                )
            
            # Validate action
            if not action.meat_type:
                return {
                    'type': 'use_meat',
                    'success': False,
                    'error': 'Missing meat_type',
                    'message': 'Kein Fleisch-Typ angegeben!'
                }
            
            # Get MeatSystem instance with fallback
            meat_system = None
            if hasattr(self.state, 'meat_system') and self.state.meat_system:
                meat_system = self.state.meat_system
            else:
                meat_system = MeatSystem()  # Singleton instance
                logger.warning("Using fallback MeatSystem instance for meat usage")
            
            # Use meat through MeatSystem
            success, message = meat_system.use_meat(
                meat_type=action.meat_type,
                battle_state=self.state
            )
            
            # Log meat usage
            logger.info(f"Meat usage attempt: {action.meat_type.name} - Success: {success}")
            
            # Get meat bonus safely
            meat_bonus = 0.0
            try:
                meat_bonus = meat_system.get_taming_bonus() if success else 0.0
            except Exception as e:
                logger.warning(f"Could not get meat bonus: {e}")
                meat_bonus = 0.0
            
            return {
                'type': 'use_meat',
                'actor': action.actor,
                'meat_type': action.meat_type,
                'success': success,
                'message': message,
                'meat_bonus': meat_bonus
            }
            
        except Exception as e:
            logger.error(f"Error executing use meat: {e}")
            return {
                'type': 'use_meat',
                'success': False,
                'error': str(e),
                'message': f'Fehler beim Verwenden von Fleisch: {str(e)}'
            }
    
    def _execute_scout(self, action: BattleAction) -> Dict[str, Any]:
        """Execute a scout action."""
        try:
            # VOR Scout: Message-Event für "X späht Y aus!"
            if hasattr(self.state, 'event_processor') and self.state.event_processor:
                self.state.event_processor.emit_event(
                    EventType.MESSAGE_SHOW,
                    {'message': f"{action.actor.name} späht {action.target.name} aus!", 'duration': 1.5}
                )
            
            # This would handle monster scouting
            # For now, return a placeholder result
            return {
                'type': 'scout',
                'actor': action.actor,
                'target': action.target,
                'success': True
            }
        except Exception as e:
            logger.error(f"Error executing scout: {e}")
            return {'error': str(e), 'type': 'scout'}
