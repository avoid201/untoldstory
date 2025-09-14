"""
Battle Scene Components - Consolidated.
All battle scene sub-components in one place for better organization.
"""

import pygame
import random
import logging
from typing import Optional, Dict, TYPE_CHECKING, Any

logger = logging.getLogger(__name__)

from engine.systems.battle.battle_enums import BattlePhase
from engine.systems.monster_instance import MonsterInstance

if TYPE_CHECKING:
    from engine.scenes.battle_scene import BattleScene


class BattleScenePhases:
    """Phase management for battle flow."""
    
    def __init__(self, scene: 'BattleScene'):
        self.scene = scene
    
    def update_intro_phase(self, dt: float):
        """Handle intro animations and messages."""
        # Wait for intro message
        if self.scene.phase_timer > 2.0:  # 2 seconds intro
            self.scene.current_phase = BattlePhase.INPUT
            self.scene.waiting_for_input = True
            print("Intro phase complete - waiting for input")
    
    def update_input_phase(self, dt: float):
        """Handle player input phase."""
        # Wait for player input
        if not self.scene.waiting_for_input:
            # Player has made a choice, move to execution
            self.scene.current_phase = BattlePhase.RESOLVE
            self.scene.phase_timer = 0
            print("Moving to execution phase")
    
    def update_execution_phase(self, dt: float):
        """Handle action execution phase."""
        # Execute turn if actions are ready
        if self.scene.all_actions_ready():
            self.scene.execute_turn()
        else:
            # Wait for more actions
            pass
    
    def update_aftermath_phase(self, dt: float):
        """Handle end-of-turn effects."""
        # Process status effects, weather, etc.
        if self.scene.phase_timer > 1.0:  # 1 second aftermath
            # Check if battle should continue
            if self.scene.battle_state.is_valid():
                self.scene.current_phase = BattlePhase.INPUT
                self.scene.waiting_for_input = True
                print("Aftermath complete - waiting for input")
            else:
                self.scene.current_phase = BattlePhase.END
                print("Battle ending")
    
    def update_end_phase(self, dt: float):
        """Handle battle end."""
        # Process battle results
        if self.scene.phase_timer > 1.0:  # 1 second end
            self.scene.end_battle()
    
    def next_message(self):
        """Show next message in queue."""
        if hasattr(self.scene.battle_ui, 'message_queue') and self.scene.battle_ui.message_queue:
            self.scene.battle_ui._next_message()
        else:
            # No more messages, continue
            if self.scene.current_phase == BattlePhase.MESSAGE:
                self.scene.current_phase = BattlePhase.INPUT
                self.scene.waiting_for_input = True


class BattleSceneEffects:
    """Visual effects for battle scene."""
    
    def __init__(self, scene: 'BattleScene'):
        self.scene = scene
        self.game = scene.game
        self.battle_state = scene.battle_state
        self.battle_ui = scene.battle_ui
    
    def process_status_effects(self):
        """Process end-of-turn status effects via BattleController."""
        # Let BattleController handle status effects
        if hasattr(self.scene, 'battle_controller'):
            self.scene.battle_controller.process_status_effects()
        else:
            # Fallback: show message but don't process
            self.battle_ui.show_message("Battle-Controller nicht verfügbar für Status-Effekte!")
    
    def check_defeated(self):
        """Check for defeated monsters via BattleController."""
        # Let BattleController handle defeated monster checks
        if hasattr(self.scene, 'battle_controller'):
            self.scene.battle_controller.check_defeated_monsters()
        else:
            # Fallback: show message but don't process
            self.battle_ui.show_message("Battle-Controller nicht verfügbar für Defeat-Check!")
    
    def check_battle_end(self) -> 'BattleResult':
        """Check if battle should end via BattleController."""
        from engine.systems.battle.battle_enums import BattleResult
        
        # Let BattleController handle battle end checks
        if hasattr(self.scene, 'battle_controller'):
            return self.scene.battle_controller.check_battle_end()
        else:
            # Fallback: return ongoing
            return BattleResult.ONGOING
    
    def calculate_exp_reward(self, defeated: MonsterInstance) -> int:
        """Calculate experience points for defeating a monster."""
        # Base EXP based on level and rank
        rank_multipliers = {
            'F': 0.5, 'E': 0.7, 'D': 0.9, 'C': 1.0,
            'B': 1.2, 'A': 1.5, 'S': 2.0, 'SS': 2.5, 'X': 3.0
        }
        
        base_exp = defeated.level * 10
        rank_mult = rank_multipliers.get(defeated.rank, 1.0)
        
        # Wild vs trainer bonus
        trainer_mult = 1.5 if not self.scene.is_wild else 1.0
        
        # Boss bonus
        boss_mult = 2.0 if self.scene.is_boss else 1.0
        
        return int(base_exp * rank_mult * trainer_mult * boss_mult)
    
    def distribute_rewards(self):
        """Distribute EXP and items to party."""
        if self.scene.exp_gained > 0:
            # Distribute to all participating monsters
            participants = [
                m for m in self.battle_state.player_team 
                if m and m.current_hp > 0
            ]
            
            if participants:
                exp_per_monster = self.scene.exp_gained // len(participants)
                
                for monster in participants:
                    old_level = monster.level
                    monster.gain_exp(exp_per_monster)
                    
                    self.battle_ui.show_message(
                        f"{monster.nickname or monster.species_name} kriegt {exp_per_monster} EXP!"
                    )
                    
                    # Check for level up
                    if monster.level > old_level:
                        self.battle_ui.show_message(
                            f"{monster.nickname or monster.species_name} ist jetzt Level {monster.level}!"
                        )
                        
                        # Check for new moves
                        if hasattr(monster, 'check_learned_moves'):
                            new_moves = monster.check_learned_moves()
                            for move_id in new_moves:
                                move = self.game.resources.get_move(move_id)
                                if move:
                                    self.battle_ui.show_message(
                                        f"{monster.nickname or monster.species_name} lernt {move.name}!"
                                    )
                                    
                                    # Track learned moves for sync
                                    if not hasattr(monster, 'new_moves_learned'):
                                        monster.new_moves_learned = []
                                    monster.new_moves_learned.append(move_id)
    
    def sync_party_after_battle(self):
        """Sync party monsters with battle state changes."""
        # Update party monsters with battle changes (HP, EXP, status, new moves)
        for i, battle_monster in enumerate(self.battle_state.player_team):
            if battle_monster and i < len(self.game.party_manager.party.members):
                party_monster = self.game.party_manager.party.members[i]
                if party_monster and party_monster.id == battle_monster.id:
                    # Sync HP and status
                    party_monster.current_hp = battle_monster.current_hp
                    party_monster.status = battle_monster.status
                    
                    # Sync EXP and level
                    party_monster.experience = battle_monster.experience
                    party_monster.level = battle_monster.level
                    
                    # Sync PP for moves
                    party_monster.moves = battle_monster.moves
                    
                    # Sync any new moves learned
                    if hasattr(battle_monster, 'new_moves_learned'):
                        for move_id in battle_monster.new_moves_learned:
                            party_monster.learn_move(move_id)
    
    def update(self, dt: float) -> None:
        """Update all battle effects and animations."""
        try:
            # Update UI animations if available
            if hasattr(self.scene.battle_ui, 'state') and self.scene.battle_ui.state:
                self.scene.battle_ui.state.update_animations(dt)
            
            # Update renderer animations
            if hasattr(self.scene.battle_ui, 'renderer'):
                renderer = self.scene.battle_ui.renderer
                
                # Update HP bar animations
                if hasattr(renderer, 'hp_updates'):
                    for monster_id, update in list(renderer.hp_updates.items()):
                        if update.get('timer', 0) > 0:
                            update['timer'] -= dt
                            if update['timer'] <= 0:
                                update['animated'] = False
                
                # Update faint animations
                if hasattr(renderer, 'faint_animations'):
                    for monster_id, timer in list(renderer.faint_animations.items()):
                        renderer.faint_animations[monster_id] -= dt
                        if renderer.faint_animations[monster_id] <= 0:
                            del renderer.faint_animations[monster_id]
                
                # Update appear animations
                if hasattr(renderer, 'appear_animations'):
                    for monster_id, timer in list(renderer.appear_animations.items()):
                        renderer.appear_animations[monster_id] -= dt
                        if renderer.appear_animations[monster_id] <= 0:
                            del renderer.appear_animations[monster_id]
                
                # Update screen effects
                if hasattr(renderer, 'camera_shake'):
                    if renderer.camera_shake.get('duration', 0) > 0:
                        renderer.camera_shake['duration'] -= dt
                        if renderer.camera_shake['duration'] <= 0:
                            renderer.camera_shake['intensity'] = 0
                
                if hasattr(renderer, 'screen_flash'):
                    if renderer.screen_flash.get('duration', 0) > 0:
                        renderer.screen_flash['duration'] -= dt
                        if renderer.screen_flash['duration'] <= 0:
                            renderer.screen_flash['alpha'] = 0
            
            logger.debug(f"Effects updated (dt={dt:.3f})")
            
        except Exception as e:
            logger.error(f"Error updating effects: {e}")
    
    def finalize_caught_monster(self):
        """Add caught monster to party or storage."""
        if self.scene.caught_monster:
            success, message = self.game.party_manager.add_to_party(self.scene.caught_monster)
            print(f"Monster caught: {message}")
    
    def handle_defeat(self):
        """Handle player defeat."""
        # Heal party and return to last heal point
        self.game.party_manager.party.heal_all()
        
        # Set player position to last heal point
        if hasattr(self.game, 'last_heal_point'):
            # Return to last saved position
            pass
        else:
            # Return to player house as default
            self.game.current_map = 'player_house'
            self.game.player_pos = (5, 5)


class BattleSceneInput:
    """Input handling for battle scene."""
    
    def __init__(self, scene: 'BattleScene'):
        self.scene = scene
        self.battle_state = scene.battle_state
        self.battle_ui = scene.battle_ui
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle input events."""
        try:
            if event.type == pygame.KEYDOWN:
                # Map keys to actions
                action = None
                
                if event.key in [pygame.K_e, pygame.K_RETURN, pygame.K_SPACE]:
                    action = 'confirm'
                elif event.key in [pygame.K_q, pygame.K_ESCAPE]:
                    action = 'back'
                elif event.key == pygame.K_w:
                    action = 'up'
                elif event.key == pygame.K_s:
                    action = 'down'
                elif event.key == pygame.K_a:
                    action = 'left'
                elif event.key == pygame.K_d:
                    action = 'right'
                
                if action:
                    print(f"Battle Input: {action}")
                    
                    # Handle different battle phases
                    if self.scene.current_phase == BattlePhase.INPUT:
                        # Let UI handle input and get action
                        player_action = self.battle_ui.handle_input(action, self.battle_state)
                        
                        if player_action:
                            print(f"Player action: {player_action}")
                            # Store player action
                            self.scene.pending_actions['player_0'] = player_action
                            self.scene.waiting_for_input = False
                            
                            # Check if all actions collected
                            if self.scene.all_actions_ready():
                                self.scene.execute_turn()
                    
                    elif self.scene.current_phase == BattlePhase.MESSAGE:
                        # Skip message on any key
                        self.scene.phase_manager.next_message()
                    
                    elif self.scene.current_phase == BattlePhase.INIT:
                        # Skip intro on any key
                        self.scene.current_phase = BattlePhase.INPUT
                        self.scene.waiting_for_input = True
                        print("Battle started - waiting for input")
                
                return True
            
            return False
            
        except Exception as e:
            print(f"Fehler bei der Input-Verarbeitung: {str(e)}")
            return False
    
    def create_battle_action(self, player_action: dict) -> Optional['BattleAction']:
        """Create a BattleAction from player input."""
        try:
            from engine.systems.battle.turn_logic_clean import BattleAction, ActionType
            
            action_type = player_action.get('action')
            if action_type == 'attack':
                # Get selected move
                move_index = player_action.get('move_index', 0)
                if hasattr(self.battle_state, 'player_active') and self.battle_state.player_active:
                    moves = self.battle_state.player_active.moves
                    if moves and move_index < len(moves):
                        move = moves[move_index]
                        return BattleAction(
                            actor=self.battle_state.player_active,
                            action_type=ActionType.ATTACK,
                            move=move,
                            target=self.battle_state.enemy_active
                        )
            
            elif action_type == 'flee':
                return BattleAction(
                    actor=self.battle_state.player_active,
                    action_type=ActionType.FLEE
                )
            
            elif action_type == 'tame':
                # Get meat bonus if available
                meat_bonus = player_action.get('meat_bonus', 0)
                return BattleAction(
                    actor=self.battle_state.player_active,
                    action_type=ActionType.TAME,
                    target=self.battle_state.enemy_active,
                    meat_bonus=meat_bonus
                )
            
            elif action_type == 'switch':
                # Handle monster switching using the complete Party system
                try:
                    switch_target_id = player_action.get('target_monster')
                    if not switch_target_id:
                        print("ERROR: No target monster specified for switch")
                        return None
                    
                    # Get party manager
                    if not hasattr(self.scene.game, 'party_manager') or not self.scene.game.party_manager:
                        print("ERROR: No party manager available for switching")
                        return None
                    
                    party = self.scene.game.party_manager.party
                    
                    # Find the target monster in the party
                    target_monster = None
                    for monster in party.get_conscious_members():
                        if hasattr(monster, 'id') and monster.id == switch_target_id:
                            target_monster = monster
                            break
                        elif monster.name == switch_target_id:  # Fallback to name matching
                            target_monster = monster
                            break
                    
                    if not target_monster:
                        print(f"ERROR: Target monster {switch_target_id} not found or fainted")
                        return None
                    
                    # Check if already active
                    current_active = party.get_active()
                    if current_active and current_active == target_monster:
                        print(f"ERROR: {target_monster.name} is already the active monster")
                        return None
                    
                    # Create switch battle action
                    return BattleAction(
                        actor=self.battle_state.player_active,
                        action_type=ActionType.SWITCH,
                        switch_to=target_monster
                    )
                    
                except Exception as e:
                    print(f"ERROR in switch action: {e}")
                    return None
            
            print(f"Unknown action type: {action_type}")
            return None
            
        except Exception as e:
            print(f"Fehler beim Erstellen der BattleAction: {str(e)}")
            return None
    
    def process_action(self, action: Dict[str, Any]) -> bool:
        """
        Process and validate action from UI.
        
        Args:
            action: Action dictionary from UI
            
        Returns:
            True if action was processed successfully
        """
        try:
            if not action:
                logger.debug("No action to process")
                return False
            
            # Validate action has required fields
            if 'type' not in action:
                logger.error(f"Action missing 'type' field: {action}")
                return False
            
            # Validate actor is a MonsterInstance, not a string
            if 'actor' in action:
                if isinstance(action['actor'], str):
                    logger.error(f"Actor is string '{action['actor']}', should be MonsterInstance")
                    # Try to fix it
                    if action['actor'] == 'player' and self.scene.battle_state:
                        action['actor'] = self.scene.battle_state.player_active
                    elif action['actor'] == 'enemy' and self.scene.battle_state:
                        action['actor'] = self.scene.battle_state.enemy_active
                    else:
                        return False
            
            # Validate target is a MonsterInstance if present
            if 'target' in action:
                if isinstance(action['target'], str):
                    logger.error(f"Target is string '{action['target']}', should be MonsterInstance")
                    # Try to fix it
                    if action['target'] == 'player' and self.scene.battle_state:
                        action['target'] = self.scene.battle_state.player_active
                    elif action['target'] == 'enemy' and self.scene.battle_state:
                        action['target'] = self.scene.battle_state.enemy_active
                    else:
                        return False
            
            # Log successful action
            action_type = action.get('type')
            actor_name = action['actor'].name if 'actor' in action and hasattr(action['actor'], 'name') else 'Unknown'
            logger.info(f"Processing {action_type} action from {actor_name}")
            
            # Queue action for processing
            if self.scene.battle_ui:
                self.scene.battle_ui.pending_action = action
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error processing action: {e}")
            return False
    
    def get_ai_action(self, actor_id: str) -> Optional[Dict]:
        """Get AI-determined action for an actor."""
        # Get the monster
        idx = int(actor_id.split('_')[1])
        monster = self.battle_state.enemy_team[idx]
        
        if not monster or monster.current_hp <= 0:
            return None
        
        # Use AI to determine action
        action = self.scene.battle_ai.choose_action(
            monster,
            self.battle_state.enemy_team,
            self.battle_state.player_team,
            self.battle_state
        )
        
        # Add actor ID
        if action:
            action['actor'] = actor_id
        
        return action


class BattleSceneActions:
    """Action execution for battle scene."""
    
    def __init__(self, scene: 'BattleScene'):
        self.scene = scene
        self.game = scene.game
        self.battle_state = scene.battle_state
        self.battle_ui = scene.battle_ui
    
    def execute_action(self, action: Dict):
        """Execute a single action."""
        actor_id = action['actor']
        action_type = action['type']
        
        # Get actor monster
        if actor_id.startswith('player'):
            idx = int(actor_id.split('_')[1])
            actor = self.battle_state.player_team[idx]
        else:
            idx = int(actor_id.split('_')[1])
            actor = self.battle_state.enemy_team[idx]
        
        if not actor or actor.current_hp <= 0:
            return
        
        # Execute based on type
        if action_type == 'attack':
            self.execute_attack(actor, action)
        elif action_type == 'tame':
            self.execute_tame(actor, action)
        elif action_type == 'item':
            self.execute_item(actor, action)
        elif action_type == 'flee':
            self.execute_flee(actor, action)
    
    def execute_attack(self, actor: MonsterInstance, action: Dict):
        """Execute an attack action via BattleController."""
        move_id = action['move_id']
        targets = action.get('targets', [])
        
        # Get move data
        move_data = self.game.resources.get_move(move_id)
        if not move_data:
            return
        
        # Show attack message
        self.battle_ui.show_message(
            f"{actor.nickname or actor.species_name} setzt {move_data.name} ein!"
        )
        
        # Execute against each target via BattleController
        for target_id in targets:
            # Get target monster
            if target_id.startswith('player'):
                idx = int(target_id.split('_')[1])
                target = self.battle_state.player_team[idx]
            else:
                idx = int(target_id.split('_')[1])
                target = self.battle_state.enemy_team[idx]
            
            if not target or target.current_hp <= 0:
                continue
            
            # Create BattleAction and queue with controller
            from engine.systems.battle.turn_logic_clean import BattleAction, ActionType
            attack_action = BattleAction(
                actor=actor,
                action_type=ActionType.ATTACK,
                move=move_data,
                target=target
            )
            
            # Let BattleController handle execution
            if hasattr(self.scene, 'battle_controller'):
                self.scene.battle_controller.queue_action(attack_action)
            else:
                # Fallback: show message but don't execute
                self.battle_ui.show_message("Battle-Controller nicht verfügbar!")
    
    def execute_tame(self, actor: MonsterInstance, action: Dict):
        """Execute a taming attempt via BattleController."""
        # Only works on wild monsters
        if not self.scene.is_wild:
            self.battle_ui.show_message("Kannst du knicken bei Trainer-Monstern!")
            return
        
        # Get target (first enemy)
        target = self.battle_state.enemy_team[0] if self.battle_state.enemy_team else None
        if not target:
            return
        
        # Get meat bonus from action if available
        meat_bonus = action.get('meat_bonus', 0)
        
        # Create BattleAction and queue with controller
        from engine.systems.battle.turn_logic_clean import BattleAction, ActionType
        taming_action = BattleAction(
            actor=actor,
            action_type=ActionType.TAME,
            target=target,
            meat_bonus=meat_bonus
        )
        
        # Let BattleController handle execution
        if hasattr(self.scene, 'battle_controller'):
            self.scene.battle_controller.queue_action(taming_action)
        else:
            # Fallback: show message but don't execute
            self.battle_ui.show_message("Battle-Controller nicht verfügbar!")
    
    def execute_item(self, actor: MonsterInstance, action: Dict):
        """Execute item use via BattleController."""
        item_id = action.get('item_id')
        target_id = action.get('target')
        
        # Get target monster
        target = None
        if target_id.startswith('player'):
            idx = int(target_id.split('_')[1])
            target = self.battle_state.player_team[idx]
        else:
            idx = int(target_id.split('_')[1])
            target = self.battle_state.enemy_team[idx]
        
        if not target:
            self.battle_ui.show_message("Ziel nicht gefunden!")
            return
        
        # Create BattleAction and queue with controller
        from engine.systems.battle.turn_logic_clean import BattleAction, ActionType
        item_action = BattleAction(
            actor=actor,
            action_type=ActionType.ITEM,
            target=target,
            item_id=item_id
        )
        
        # Let BattleController handle execution
        if hasattr(self.scene, 'battle_controller'):
            self.scene.battle_controller.queue_action(item_action)
        else:
            # Fallback: show message but don't execute
            self.battle_ui.show_message("Battle-Controller nicht verfügbar!")
    
    def execute_flee(self, actor: MonsterInstance, action: Dict):
        """Attempt to flee from battle via BattleController."""
        if not self.scene.can_flee:
            self.battle_ui.show_message("Hier gibt's kein Entkommen!")
            return
        
        # Create BattleAction and queue with controller
        from engine.systems.battle.turn_logic_clean import BattleAction, ActionType
        flee_action = BattleAction(
            actor=actor,
            action_type=ActionType.FLEE
        )
        
        # Let BattleController handle execution
        if hasattr(self.scene, 'battle_controller'):
            self.scene.battle_controller.queue_action(flee_action)
        else:
            # Fallback: show message but don't execute
            self.battle_ui.show_message("Battle-Controller nicht verfügbar!")


class BattleSceneIntegration:
    """Integration validation and synchronization for battle scene components."""
    
    def __init__(self, scene: 'BattleScene'):
        self.scene = scene
    
    def validate_ui_integration(self) -> Dict[str, bool]:
        """
        Validate that all UI components are properly integrated.
        
        Returns:
            Dictionary of component -> is_valid status
        """
        validation = {}
        
        try:
            # Check battle_ui exists
            validation['battle_ui'] = self.scene.battle_ui is not None
            
            if self.scene.battle_ui:
                # Check renderer
                validation['renderer'] = hasattr(self.scene.battle_ui, 'renderer')
                
                # Check input handler
                validation['input_handler'] = hasattr(self.scene.battle_ui, 'input_handler')
                
                # Check menu manager
                validation['menu_manager'] = hasattr(self.scene.battle_ui, 'menu_manager')
                
                # Check state
                validation['state'] = hasattr(self.scene.battle_ui, 'state')
                
                # Check critical renderer methods
                if hasattr(self.scene.battle_ui, 'renderer'):
                    renderer = self.scene.battle_ui.renderer
                    validation['update_hp_bar'] = hasattr(renderer, 'update_hp_bar')
                    validation['show_status_effect'] = hasattr(renderer, 'show_status_effect')
                    validation['play_faint_animation'] = hasattr(renderer, 'play_faint_animation')
                    validation['play_appear_animation'] = hasattr(renderer, 'play_appear_animation')
                
                # Check critical input methods
                if hasattr(self.scene.battle_ui, 'input_handler'):
                    handler = self.scene.battle_ui.input_handler
                    validation['process_move_selection'] = hasattr(handler, 'process_move_selection')
                    validation['process_item_selection'] = hasattr(handler, 'process_item_selection')
                    validation['process_switch_selection'] = hasattr(handler, 'process_switch_selection')
                
                # Check menu manager methods
                if hasattr(self.scene.battle_ui, 'menu_manager'):
                    manager = self.scene.battle_ui.menu_manager
                    validation['get_items_for_category'] = hasattr(manager, 'get_items_for_category')
                    validation['get_moves_by_category'] = hasattr(manager, 'get_moves_by_category')
            
            # Log validation results
            for component, is_valid in validation.items():
                if not is_valid:
                    logger.warning(f"Integration check failed: {component}")
                else:
                    logger.debug(f"Integration check passed: {component}")
            
            # Overall validation
            validation['overall'] = all(validation.values())
            
            return validation
            
        except Exception as e:
            logger.error(f"Error validating UI integration: {e}")
            return {'overall': False, 'error': str(e)}
    
    def sync_ui_state(self) -> None:
        """Synchronize UI state with battle state."""
        try:
            if not self.scene.battle_ui or not self.scene.battle_state:
                return
            
            ui = self.scene.battle_ui
            battle_state = self.scene.battle_state
            
            # Sync active monsters
            if hasattr(ui, 'state'):
                ui.state.player_active = battle_state.player_active
                ui.state.enemy_active = battle_state.enemy_active
                ui.state.player_team = battle_state.player_team
                ui.state.enemy_team = battle_state.enemy_team
            
            # Sync to UI components
            ui.battle_state = battle_state
            
            # Sync to renderer if available
            if hasattr(ui, 'renderer'):
                ui.renderer.state = ui.state
            
            # Sync to input handler if available
            if hasattr(ui, 'input_handler'):
                ui.input_handler.battle_ui = ui
            
            logger.debug("UI state synchronized with battle state")
            
        except Exception as e:
            logger.error(f"Error syncing UI state: {e}")
    
    def initialize(self) -> bool:
        """
        Initialize battle scene components.
        
        Returns:
            True if initialization successful
        """
        try:
            logger.info("Initializing battle scene components")
            
            # Validate battle systems
            if not self.scene.battle_controller:
                logger.error("No battle controller available")
                return False
            
            if not self.scene.battle_state:
                logger.error("No battle state available")
                return False
            
            # Validate UI components
            validation = self.validate_ui_integration()
            if not validation.get('overall', False):
                logger.error(f"UI integration validation failed: {validation}")
                return False
            
            # Sync initial state
            self.sync_ui_state()
            
            # Initialize effect systems
            if hasattr(self, 'effects'):
                self.effects.initialize()
            
            # Log successful initialization
            logger.info("Battle scene components initialized successfully")
            
            # Run final integration test
            test_action = {
                'type': 'test',
                'actor': self.scene.battle_state.player_active,
                'target': self.scene.battle_state.enemy_active
            }
            
            if self.process_action(test_action):
                logger.info("Integration test passed - action processing works")
                # Clear test action
                if self.scene.battle_ui:
                    self.scene.battle_ui.pending_action = None
            else:
                logger.warning("Integration test failed - action processing may have issues")
            
            return True
            
        except Exception as e:
            logger.error(f"Error initializing battle scene components: {e}")
            return False
    
    def process_action(self, action: Dict[str, Any]) -> bool:
        """
        Process and validate action from UI.
        
        Args:
            action: Action dictionary from UI
            
        Returns:
            True if action was processed successfully
        """
        try:
            if not action:
                logger.debug("No action to process")
                return False
            
            # Validate action has required fields
            if 'type' not in action:
                logger.error(f"Action missing 'type' field: {action}")
                return False
            
            # Validate actor is a MonsterInstance, not a string
            if 'actor' in action:
                if isinstance(action['actor'], str):
                    logger.error(f"Actor is string '{action['actor']}', should be MonsterInstance")
                    # Try to fix it
                    if action['actor'] == 'player' and self.scene.battle_state:
                        action['actor'] = self.scene.battle_state.player_active
                    elif action['actor'] == 'enemy' and self.scene.battle_state:
                        action['actor'] = self.scene.battle_state.enemy_active
                    else:
                        return False
            
            # Validate target is a MonsterInstance if present
            if 'target' in action:
                if isinstance(action['target'], str):
                    logger.error(f"Target is string '{action['target']}', should be MonsterInstance")
                    # Try to fix it
                    if action['target'] == 'player' and self.scene.battle_state:
                        action['target'] = self.scene.battle_state.player_active
                    elif action['target'] == 'enemy' and self.scene.battle_state:
                        action['target'] = self.scene.battle_state.enemy_active
                    else:
                        return False
            
            # Log successful action
            action_type = action.get('type')
            actor_name = action['actor'].name if 'actor' in action and hasattr(action['actor'], 'name') else 'Unknown'
            logger.info(f"Processing {action_type} action from {actor_name}")
            
            # Queue action for processing
            if self.scene.battle_ui:
                self.scene.battle_ui.pending_action = action
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error processing action: {e}")
            return False
