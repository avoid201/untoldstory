"""
Battle Controller Module
Main coordinator for battle system, delegates to specialized modules
"""

import logging
import random
from typing import List, Optional, Dict, Any, Callable
from engine.systems.monster_instance import MonsterInstance, StatusCondition
from engine.systems.battle.battle_enums import BattleType, BattlePhase, BattleCommand, AIPersonality
from engine.systems.battle.battle_validation import BattleValidator
from engine.systems.battle.battle_tension import TensionManager
from engine.systems.battle.battle_actions import BattleActionExecutor
from engine.systems.battle.turn_logic import BattleAction, ActionType, TurnOrder
from engine.systems.battle.battle_ai import BattleAI
from engine.systems.battle.battle_events import (
    BattleEventGenerator, EventType, BattleEvent,
    create_battle_event_system
)
from engine.systems.battle.battle_formation import (
    BattleFormation, FormationManager, FormationType, MonsterSlot
)
from engine.systems.battle.target_system import (
    TargetingSystem, TargetType, TargetScope, TargetSelection
)
from engine.systems.battle.dqm_formulas import DQMCalculator, DQMDamageStage

logger = logging.getLogger(__name__)


class BattleState:
    """
    Complete battle state management system.
    Coordinates all battle subsystems and maintains battle state.
    """
    
    def __init__(self, 
                 player_team: List[MonsterInstance],
                 enemy_team: List[MonsterInstance],
                 battle_type: BattleType = BattleType.WILD,
                 can_flee: bool = True,
                 can_catch: bool = True,
                 enable_3v3: bool = False,
                 player_formation_type: FormationType = FormationType.STANDARD,
                 enemy_formation_type: FormationType = FormationType.STANDARD):
        """
        Initialize battle state.
        
        Args:
            player_team: Player's monster team
            enemy_team: Enemy monster team
            battle_type: Type of battle
            can_flee: Whether fleeing is allowed
            can_catch: Whether catching is allowed
        """
        # Validate input parameters
        # Ensure all monsters have positive HP
        for monster in player_team + enemy_team:
            if not hasattr(monster, 'current_hp') or monster.current_hp <= 0:
                if hasattr(monster, 'max_hp'):
                    monster.current_hp = monster.max_hp
                else:
                    monster.current_hp = 100
                    monster.max_hp = 100
                print(f"WARNING: Fixed {monster.name} HP to {monster.current_hp}")
                if not player_team or not enemy_team:
            raise ValueError("Player and enemy teams cannot be empty!")
        
        if not all(isinstance(m, MonsterInstance) for m in player_team + enemy_team):
            raise TypeError("All team members must be MonsterInstance objects!")
        
        self.player_team = player_team
        self.enemy_team = enemy_team
        self.battle_type = battle_type
        self.can_flee = can_flee and battle_type == BattleType.WILD
        self.can_catch = can_catch and battle_type == BattleType.WILD
        
        # 3v3 Battle System Support
        self.enable_3v3 = enable_3v3 and len(player_team) > 1
        self.formation_manager: Optional[FormationManager] = None
        self.targeting_system: Optional[TargetingSystem] = None
        
        if self.enable_3v3:
            # Initialize 3v3 formations
            self.formation_manager = FormationManager()
            self.player_formation = self.formation_manager.create_formation(
                "player", player_team[:6], player_formation_type
            )
            self.enemy_formation = self.formation_manager.create_formation(
                "enemy", enemy_team[:6], enemy_formation_type
            )
            self.targeting_system = TargetingSystem(
                self.player_formation, self.enemy_formation
            )
            
            # Set active monsters from formations
            player_active_slots = self.player_formation.get_active_monsters()
            enemy_active_slots = self.enemy_formation.get_active_monsters()
            
            # For compatibility, set first active as primary
            self.player_active = player_active_slots[0].monster if player_active_slots else None
            self.enemy_active = enemy_active_slots[0].monster if enemy_active_slots else None
        else:
            # Traditional 1v1 mode
            self.player_active: Optional[MonsterInstance] = None
            self.enemy_active: Optional[MonsterInstance] = None
            self._initialize_active_monsters()
        
        # Battle state
        self.phase = BattlePhase.INIT
        self.turn_count = 0
        self.action_queue: List[BattleAction] = []
        
        # Battle history/log
        self.battle_log: List[str] = []
        self.last_action_results: Optional[Dict[str, Any]] = None
        
        # Rewards
        self.exp_earned = 0
        self.money_earned = 0
        self.items_earned: List[str] = []
        
        # Field effects
        self.field_effects: Dict[str, Any] = {}
        
        # Escape attempts
        self.escape_attempts = 0
        
        # Initialize subsystems
        self.validator = BattleValidator()
        self.tension_manager = TensionManager()
        self.action_executor = BattleActionExecutor()
        self.battle_ai = BattleAI()
        
        # Initialize event system
        self.event_generator = create_battle_event_system(self)
        self.pending_events = []
        
        # Initialize tension for all monsters
        for monster in player_team + enemy_team:
            self.tension_manager.initialize_monster(monster)
        
        # Set AI personalities
        self.ai_personalities: Dict[MonsterInstance, AIPersonality] = {}
        for monster in enemy_team:
            self.ai_personalities[monster] = self._determine_ai_personality(monster)
        
        # Validate battle state
        if not self.validate_battle_state():
            logger.error("Battle state is invalid after initialization!")
            raise RuntimeError("Battle state could not be validated!")
    
    def _initialize_active_monsters(self):
        """Initialize active monsters for both teams."""
        # Set first non-fainted monster as active for player
        for monster in self.player_team:
            if monster and not monster.is_fainted:
                self.player_active = monster
                break
        
        # Set first non-fainted monster as active for enemy
        for monster in self.enemy_team:
            if monster and not monster.is_fainted:
                self.enemy_active = monster
                break
        
        # Validate active monsters
        if not self.player_active:
            raise ValueError("No able monster found in player team!")
        if not self.enemy_active:
            raise ValueError("No able monster found in enemy team!")
    
    def validate_battle_state(self) -> bool:
        """
        Validate the current battle state.
        
        Returns:
            True if battle state is valid, False otherwise
        """
        return self.validator.validate_battle_state(
            self.player_active, 
            self.enemy_active,
            self.player_team,
            self.enemy_team
        )
    
    def has_able_monsters(self, team: List[MonsterInstance]) -> bool:
        """Check if team has any conscious monsters."""
        return self.validator.has_able_monsters(team)
    
    def is_valid(self) -> bool:
        """Check if battle can continue."""
        return self.validator.is_battle_valid(
            self.player_active,
            self.enemy_active,
            self.player_team,
            self.enemy_team
        )
    
    def queue_player_action(self, action: Dict[str, Any]) -> bool:
        """
        Queue a player action for the current turn.
        Supports both 1v1 and 3v3 modes.
        
        Args:
            action: Action dictionary with action_type, actor, move, target, etc.
            
        Returns:
            True if action was queued successfully, False otherwise
        """
        try:
            # Validate action
            if not self.validator.validate_action(action):
                return False
            
            action_type = action.get('action')
            
            # Handle UI actions
            if action_type == 'menu_select':
                result = self.process_ui_action(action)
                if result:
                    logger.info(f"UI action processed: {result}")
                    return True
                else:
                    logger.warning("UI action could not be processed")
                    return False
            
            # Create BattleAction(s)
            if self.enable_3v3:
                # In 3v3 mode, we may need to queue multiple actions
                battle_actions = self._create_3v3_battle_actions(action)
                if not battle_actions:
                    return False
                
                # Add all actions to queue
                for battle_action in battle_actions:
                    self.action_queue.append(battle_action)
                    logger.info(f"3v3 Action queued for {battle_action.actor.name}: {action_type}")
            else:
                # Traditional 1v1 mode
                battle_action = self._create_battle_action(action)
                if not battle_action:
                    return False
                
                # Add to queue
                self.action_queue.append(battle_action)
                logger.info(f"Action queued for {battle_action.actor.name}: {action_type}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error queuing player action: {str(e)}")
            return False
    
    def _create_battle_action(self, action_dict: Dict[str, Any]) -> Optional[BattleAction]:
        """Create a BattleAction from an action dictionary."""
        try:
            action_type = action_dict.get('action')
            actor = action_dict.get('actor')
            
            if action_type == 'attack':
                move = action_dict.get('move')
                target = action_dict.get('target')
                
                if not move or not target:
                    logger.error("Attack action needs move and target!")
                    return None
                
                return BattleAction(
                    action_type=ActionType.ATTACK,
                    actor=actor,
                    move=move,
                    target=target
                )
            
            elif action_type == 'tame':
                return BattleAction(
                    action_type=ActionType.TAME,
                    actor=actor,
                    target=self.enemy_active
                )
            
            elif action_type == 'item':
                item = action_dict.get('item')
                target = action_dict.get('target')
                
                return BattleAction(
                    action_type=ActionType.ITEM,
                    actor=actor,
                    target=target or actor,
                    item=item
                )
            
            elif action_type == 'switch':
                switch_to = action_dict.get('switch_to')
                
                return BattleAction(
                    action_type=ActionType.SWITCH,
                    actor=actor,
                    target=switch_to or actor
                )
            
            elif action_type == 'flee':
                return BattleAction(
                    action_type=ActionType.FLEE,
                    actor=actor,
                    target=actor
                )
            
            else:
                logger.error(f"Unknown action type: {action_type}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating BattleAction: {str(e)}")
            return None
    
    def _create_3v3_battle_actions(self, action_dict: Dict[str, Any]) -> List[BattleAction]:
        """Create BattleActions for 3v3 mode."""
        try:
            action_type = action_dict.get('action')
            actions = []
            
            if action_type == 'attack':
                # Get all active monsters that can act
                active_monsters = self.player_formation.get_active_monsters()
                
                for slot in active_monsters:
                    if slot.can_act():
                        monster = slot.monster
                        # Get move for this monster
                        move = action_dict.get('move')
                        
                        # Determine targets based on move type
                        target_type = self._get_move_target_type(move)
                        target_selection = self.targeting_system.get_valid_targets(
                            "player", target_type
                        )
                        
                        # Create action for each target
                        for target_slot in target_selection.all_targets:
                            action = BattleAction(
                                action_type=ActionType.ATTACK,
                                actor=monster,
                                move=move,
                                target=target_slot.monster
                            )
                            actions.append(action)
            
            elif action_type == 'formation_change':
                # Change formation type
                new_formation = action_dict.get('formation_type', FormationType.STANDARD)
                self.player_formation.apply_formation(new_formation)
                logger.info(f"Formation changed to {new_formation.value}")
                # No battle action needed, just state change
                
            else:
                # For other actions, fall back to single action
                action = self._create_battle_action(action_dict)
                if action:
                    actions = [action]
            
            return actions
            
        except Exception as e:
            logger.error(f"Error creating 3v3 BattleActions: {str(e)}")
            return []
    
    def _get_move_target_type(self, move) -> TargetType:
        """Determine target type from move."""
        try:
            if not move:
                return TargetType.SINGLE
            
            # Check move properties
            if hasattr(move, 'target_type'):
                target_str = str(move.target_type).lower()
                if 'all' in target_str:
                    return TargetType.ALL_ENEMIES
                elif 'row' in target_str:
                    return TargetType.ROW_ENEMY
                elif 'spread' in target_str:
                    return TargetType.SPREAD
                elif 'adjacent' in target_str:
                    return TargetType.ADJACENT
            
            # Default to single target
            return TargetType.SINGLE
            
        except Exception as e:
            logger.error(f"Error determining move target type: {str(e)}")
            return TargetType.SINGLE
    
    def resolve_turn(self, use_events: bool = True) -> Dict[str, Any]:
        """
        Resolve the current turn with all queued actions.
        
        Args:
            use_events: Whether to use the event system for turn resolution
        
        Returns:
            Dictionary with turn results
        """
        try:
            # Validate battle state
            if not self.validate_battle_state():
                logger.error("Battle state is invalid, cannot resolve turn!")
                return {'error': 'Invalid battle state'}
            
            # Check for actions
            if not self.action_queue:
                logger.warning("No actions in queue for turn resolution!")
                return {'error': 'No actions to resolve'}
            
            # Sort actions by priority
            if self.enable_3v3 and self.formation_manager:
                # 3v3 mode: Get turn order from all active monsters
                turn_order = self.formation_manager.get_turn_order()
                
                # Create ordered action queue based on speed
                ordered_queue = []
                for team_id, slot in turn_order:
                    # Find actions for this monster
                    monster_actions = [a for a in self.action_queue 
                                     if a.actor == slot.monster]
                    ordered_queue.extend(monster_actions)
                
                # Add any remaining actions (switches, items, etc.)
                remaining = [a for a in self.action_queue 
                           if a not in ordered_queue]
                ordered_queue.extend(remaining)
                
                self.action_queue = ordered_queue
            else:
                # 1v1 mode: Use DQM turn order formula: Agility + Random(0-255)
                dqm_calc = DQMCalculator()
                # Convert actions to DQM format
                monsters_data = []
                for action in self.action_queue:
                    monsters_data.append({
                        'stats': {'spd': action.actor.stats.get('spd', 50)},
                        'action': action,
                        'status': getattr(action.actor, 'status', None)
                    })
                # Calculate DQM turn order
                sorted_monsters = dqm_calc.calculate_turn_order(monsters_data)
                self.action_queue = [m['action'] for m in sorted_monsters]
            
            # Execute actions
            turn_results = []
            
            if use_events:
                # Generate events for the turn
                events = []
                for event in self.event_generator.turn_execution_generator(self.action_queue):
                    events.append(event)
                    # Store events for UI processing
                    self.pending_events.append(event)
                
                # Process the actual actions
                for action in self.action_queue:
                    try:
                        result = self.action_executor.execute_action(action, self)
                        if result:
                            turn_results.append(result)
                    except Exception as e:
                        logger.error(f"Error executing action: {str(e)}")
                        turn_results.append({'error': str(e), 'action': action.action_type})
            else:
                # Original execution without events
                for action in self.action_queue:
                    try:
                        result = self.action_executor.execute_action(action, self)
                        if result:
                            turn_results.append(result)
                    except Exception as e:
                        logger.error(f"Error executing action: {str(e)}")
                        turn_results.append({'error': str(e), 'action': action.action_type})
            
            # Process status effects
            self._process_status_effects()
            
            # Check battle end
            battle_ended = self._check_battle_end()
            
            # Clear action queue
            self.action_queue.clear()
            
            # Update turn counter
            self.turn_count += 1
            
            # Update battle log from action executor
            self.battle_log.extend(self.action_executor.battle_log)
            self.action_executor.battle_log.clear()
            
            # Save turn results
            self.last_action_results = {
                'turn_results': turn_results,
                'battle_ended': battle_ended,
                'turn_count': self.turn_count
            }
            
            logger.info(f"Turn {self.turn_count} resolved successfully")
            return self.last_action_results
            
        except Exception as e:
            logger.error(f"Error resolving turn: {str(e)}")
            return {'error': str(e)}
    
    def _process_status_effects(self):
        """Process end-of-turn status effects."""
        try:
            # Process player status
            if self.player_active and hasattr(self.player_active, 'status'):
                self._process_monster_status(self.player_active)
            
            # Process enemy status
            if self.enemy_active and hasattr(self.enemy_active, 'status'):
                self._process_monster_status(self.enemy_active)
                
        except Exception as e:
            logger.error(f"Error processing status effects: {str(e)}")
    
    def _process_monster_status(self, monster: MonsterInstance):
        """Process status effects for a single monster."""
        try:
            if not monster or not hasattr(monster, 'status'):
                return
            
            status = monster.status
            if not status:
                return
            
            # Process different status effects
            if status == StatusCondition.POISON:
                damage = max(1, monster.max_hp // 16)
                monster.take_damage(damage)
                self.battle_log.append(f"{monster.name} suffers poison damage!")
            
            elif status == StatusCondition.BURN:
                damage = max(1, monster.max_hp // 16)
                monster.take_damage(damage)
                self.battle_log.append(f"{monster.name} suffers burn damage!")
            
            elif status == StatusCondition.SLEEP:
                # 20% chance to wake up
                if random.random() < 0.2:
                    monster.status = StatusCondition.NORMAL
                    self.battle_log.append(f"{monster.name} woke up!")
                    
        except Exception as e:
            logger.error(f"Error processing monster status: {str(e)}")
    
    def _check_battle_end(self) -> Optional[str]:
        """Check if battle has ended and return result."""
        try:
            # Check player team
            if not self.has_able_monsters(self.player_team):
                return 'defeat'
            
            # Check enemy team
            if not self.has_able_monsters(self.enemy_team):
                return 'victory'
            
            # Check active monsters
            if self.player_active and self.player_active.is_fainted:
                # Try to switch
                if not self._switch_to_next_monster():
                    return 'defeat'
            
            if self.enemy_active and self.enemy_active.is_fainted:
                # Try to switch enemy
                if not self._switch_enemy_monster():
                    return 'victory'
            
            # In 3v3 mode, check formations
            if self.enable_3v3 and self.formation_manager:
                winner = self.formation_manager.check_victory_conditions()
                if winner:
                    return 'victory' if winner == 'player' else 'defeat'
            
            return None  # Battle continues
            
        except Exception as e:
            logger.error(f"Error checking battle end: {str(e)}")
            return 'error'
    
    def _switch_to_next_monster(self) -> bool:
        """Switch to next available monster in player team."""
        try:
            for monster in self.player_team:
                if monster and not monster.is_fainted and monster != self.player_active:
                    self.player_active = monster
                    self.battle_log.append(f"{monster.name} is now active!")
                    return True
            
            return False  # No other monster available
            
        except Exception as e:
            logger.error(f"Error switching player monster: {str(e)}")
            return False
    
    def _switch_enemy_monster(self) -> bool:
        """Switch to next available monster in enemy team."""
        try:
            for monster in self.enemy_team:
                if monster and not monster.is_fainted and monster != self.enemy_active:
                    self.enemy_active = monster
                    self.battle_log.append(f"Enemy sends out {monster.name}!")
                    return True
            
            return False  # No other monster available
            
        except Exception as e:
            logger.error(f"Error switching enemy monster: {str(e)}")
            return False
    
    def _determine_ai_personality(self, monster: MonsterInstance) -> AIPersonality:
        """Determine AI personality based on monster species and stats."""
        try:
            if not monster:
                return AIPersonality.TACTICAL
            
            # Get monster name
            monster_name = ""
            if hasattr(monster, 'name') and monster.name:
                monster_name = str(monster.name).lower()
            elif hasattr(monster, 'species') and monster.species:
                if hasattr(monster.species, 'name'):
                    monster_name = str(monster.species.name).lower()
                else:
                    monster_name = str(monster.species).lower()
            else:
                return AIPersonality.TACTICAL
            
            # Determine personality based on name
            if any(word in monster_name for word in ['dragon', 'tiger', 'wolf', 'bear']):
                return AIPersonality.AGGRESSIVE
            elif any(word in monster_name for word in ['turtle', 'shield', 'wall', 'guard']):
                return AIPersonality.DEFENSIVE
            elif any(word in monster_name for word in ['angel', 'heal', 'fairy', 'priest']):
                return AIPersonality.HEALER
            elif any(word in monster_name for word in ['sage', 'wizard', 'mage', 'wise']):
                return AIPersonality.WISE
            elif any(word in monster_name for word in ['berserker', 'chaos', 'wild']):
                return AIPersonality.RECKLESS
            
            return AIPersonality.TACTICAL
            
        except Exception as e:
            logger.error(f"Error determining AI personality: {str(e)}")
            return AIPersonality.TACTICAL
    
    def process_ui_action(self, action_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process UI actions and convert them to battle actions."""
        try:
            action_type = action_data.get('action')
            
            if action_type == 'menu_select':
                option = action_data.get('option')
                if option == 'psyche_up':
                    return self.tension_manager.psyche_up(self.player_active)
                elif option == 'meditate':
                    return self.action_executor.execute_special_command('meditate', self.player_active, self)
                elif option == 'intimidate':
                    return self.action_executor.execute_special_command('intimidate', self.player_active, self)
                else:
                    return {'action': f'open_{option}_menu', 'message': f'Opening {option} menu'}
            
            return None
            
        except Exception as e:
            logger.error(f"Error processing UI action: {str(e)}")
            return {'error': str(e)}
    
    def get_battle_status(self) -> Dict[str, Any]:
        """Get current battle status for UI."""
        try:
            status = {
                'phase': self.phase.value,
                'turn_count': self.turn_count,
                'can_flee': self.can_flee,
                'can_catch': self.can_catch,
                'battle_type': self.battle_type.value,
                'mode': '3v3' if self.enable_3v3 else '1v1'
            }
            
            if self.enable_3v3 and self.formation_manager:
                # 3v3 mode status
                player_active = self.player_formation.get_active_monsters()
                enemy_active = self.enemy_formation.get_active_monsters()
                
                status['player_formation'] = {
                    'type': self.player_formation.formation_type.value,
                    'active_count': len(player_active),
                    'monsters': [
                        {
                            'name': slot.monster.name,
                            'position': slot.position.name,
                            'current_hp': slot.monster.current_hp,
                            'max_hp': slot.monster.max_hp,
                            'level': slot.monster.level
                        } for slot in player_active
                    ]
                }
                
                status['enemy_formation'] = {
                    'type': self.enemy_formation.formation_type.value,
                    'active_count': len(enemy_active),
                    'monsters': [
                        {
                            'name': slot.monster.name,
                            'position': slot.position.name,
                            'current_hp': slot.monster.current_hp,
                            'max_hp': slot.monster.max_hp,
                            'level': slot.monster.level
                        } for slot in enemy_active
                    ]
                }
                
                # Formation display
                status['formation_display'] = self.formation_manager.display_all_formations()
            else:
                # 1v1 mode status
                status['player_active'] = {
                    'name': self.player_active.name if self.player_active else None,
                    'current_hp': self.player_active.current_hp if self.player_active else 0,
                    'max_hp': self.player_active.max_hp if self.player_active else 0,
                    'level': self.player_active.level if self.player_active else 0
                } if self.player_active else None
                
                status['enemy_active'] = {
                    'name': self.enemy_active.name if self.enemy_active else None,
                    'current_hp': self.enemy_active.current_hp if self.enemy_active else 0,
                    'max_hp': self.enemy_active.max_hp if self.enemy_active else 0,
                    'level': self.enemy_active.level if self.enemy_active else 0
                } if self.enemy_active else None
            
            return status
        except Exception as e:
            logger.error(f"Error getting battle status: {str(e)}")
            return {'error': str(e)}
    
    def get_available_moves(self, monster: MonsterInstance) -> List:
        """Get available moves for a monster."""
        try:
            if not monster or not hasattr(monster, 'moves'):
                return []
            
            available_moves = []
            for move in monster.moves:
                if move and hasattr(move, 'pp') and hasattr(move, 'max_pp'):
                    if move.pp > 0:
                        available_moves.append(move)
            
            return available_moves
            
        except Exception as e:
            logger.error(f"Error getting available moves: {str(e)}")
            return []
    
    def get_available_switches(self) -> List[MonsterInstance]:
        """Get available monsters for switching."""
        try:
            available = []
            for monster in self.player_team:
                if monster and not monster.is_fainted and monster != self.player_active:
                    available.append(monster)
            return available
        except Exception as e:
            logger.error(f"Error getting available switches: {str(e)}")
            return []
    
    def get_pending_events(self) -> List[BattleEvent]:
        """
        Get all pending events and clear the queue.
        
        Returns:
            List of pending events
        """
        events = self.pending_events.copy()
        self.pending_events.clear()
        return events
    
    def process_event(self, event: BattleEvent) -> Optional[Dict[str, Any]]:
        """
        Process a single event and return any required UI updates.
        
        Args:
            event: Event to process
            
        Returns:
            Dictionary with UI update instructions, or None
        """
        try:
            # Map event types to UI updates
            if event.event_type == EventType.MESSAGE_SHOW:
                return {
                    'type': 'message',
                    'message': event.data.get('message', ''),
                    'duration': event.duration
                }
            
            elif event.event_type == EventType.HP_BAR_UPDATE:
                target = event.data.get('target')
                if target:
                    return {
                        'type': 'hp_update',
                        'target': target.name,
                        'current_hp': target.current_hp,
                        'max_hp': target.max_hp
                    }
            
            elif event.event_type == EventType.ANIMATION_PLAY:
                return {
                    'type': 'animation',
                    'animation': event.data.get('animation', ''),
                    'duration': event.duration,
                    'blocking': event.blocking
                }
            
            elif event.event_type == EventType.DAMAGE_DEALT:
                return {
                    'type': 'damage',
                    'target': event.data.get('target', {}).name,
                    'damage': event.data.get('damage', 0)
                }
            
            elif event.event_type == EventType.CRITICAL_HIT:
                return {
                    'type': 'critical',
                    'actor': event.data.get('actor', {}).name
                }
            
            elif event.event_type == EventType.MONSTER_FAINTED:
                return {
                    'type': 'faint',
                    'monster': event.data.get('monster', {}).name
                }
            
            elif event.event_type == EventType.BATTLE_END:
                return {
                    'type': 'battle_end',
                    'result': event.data.get('result', 'unknown')
                }
            
            # Add more event type mappings as needed
            
            return None
            
        except Exception as e:
            logger.error(f"Error processing event {event}: {str(e)}")
            return None
    
    def register_event_handler(self, event_type: EventType, handler: Callable) -> None:
        """
        Register a custom event handler.
        
        Args:
            event_type: Type of event to handle
            handler: Handler function
        """
        self.event_generator.register_handler(event_type, handler)
    
    def start_battle(self, use_events: bool = True) -> Dict[str, Any]:
        """
        Initialize and start the battle.
        
        Args:
            use_events: Whether to use the event system
            
        Returns:
            Battle start information
        """
        try:
            self.phase = BattlePhase.START
            self.turn_count = 1
            
            # Reset all battle states
            for monster in (self.player_team + self.enemy_team):
                if hasattr(monster, 'stat_stages'):
                    monster.stat_stages = {stat: 0 for stat in ['atk', 'def', 'mag', 'res', 'spd']}
            
            if use_events:
                # Generate battle start events
                for event in self.event_generator.battle_start_generator():
                    self.pending_events.append(event)
            else:
                # Original battle intro message
                if self.battle_type == BattleType.WILD:
                    self.battle_log.append(f"A wild {self.enemy_active.name} appears!")
                elif self.battle_type == BattleType.TRAINER:
                    self.battle_log.append("Trainer challenges you to battle!")
            
            # Set phase to input
            self.phase = BattlePhase.INPUT
            
            return {
                "player_active": self.player_active.name if self.player_active else None,
                "enemy_active": self.enemy_active.name if self.enemy_active else None,
                "battle_type": self.battle_type.value,
                "turn": self.turn_count,
                "phase": self.phase.value
            }
            
        except Exception as e:
            logger.error(f"Error starting battle: {str(e)}")
            return {"error": str(e)}
    
    def calculate_dqm_damage(self, attacker, defender, move):
        """Calculate damage using DQM formulas."""
        dqm_calc = DQMCalculator()
        result = dqm_calc.calculate_damage(
            attacker_stats=attacker.stats,
            defender_stats=defender.stats,
            move_power=move.power if hasattr(move, 'power') else 50,
            is_physical=move.category == 'phys' if hasattr(move, 'category') else True,
            tension_level=self.tension_manager.get_multiplier(attacker) if self.tension_manager else 0,
            attacker_traits=getattr(attacker, 'traits', []),
            defender_traits=getattr(defender, 'traits', [])
        )
        return result
