"""
Battle Scene for Untold Story - OPTIMIZED VERSION
Elite Battle System Specialist - Vollständig optimierte Battle Scene
"""

import pygame
import random
from typing import Optional, List, Dict, Any
from enum import Enum, auto

from engine.core.scene_base import Scene
from engine.core.config import Colors, GameState
from engine.ui.battle_ui import BattleUI, BattleMenuState
from engine.ui.battle_rewards_ui import BattleRewardsUI
from engine.systems.battle.battle_controller import BattleState, BattlePhase, BattleType
from engine.systems.battle.battle_ai import BattleAI
from engine.systems.battle.battle_enums import BattleResult
from engine.systems.battle.reward_system import RewardSystem, BattleRewards
from engine.systems.monster_instance import MonsterInstance
from engine.core.debug_utils import debug_battle_info, debug_battle_error, debug_battle_debug


class BattleScene(Scene):
    """Optimized Battle Scene mit vollständiger Integration."""

    def __init__(self, game):
        super().__init__(game)
        
        # Battle components
        self.battle_ui = BattleUI(game)
        self.battle_rewards_ui = BattleRewardsUI()
        self.battle_state = None
        self.battle_controller = None
        self.battle_ai = BattleAI()
        self.reward_system = RewardSystem()
        
        # Battle menu state
        self.current_menu_state = BattleMenuState.MAIN
        self.selected_move = None
        
        # Battle configuration
        self.is_wild = False
        self.is_boss = False
        self.can_flee = True
        self.battle_bg = None
        
        # Battle state
        self.current_phase = BattlePhase.INIT
        self.waiting_for_input = False
        self.battle_result = BattleResult.ONGOING
        self.showing_rewards = False
        self._battle_ended = False
        
        # Rewards data
        self.battle_rewards = None
        
        # Performance optimizations
        self._last_update_time = 0
        self._update_interval = 1/60  # 60 FPS
        self._pending_actions = []
        
    def on_enter(self, **kwargs):
        """Initialize battle from kwargs - OPTIMIZED VERSION."""
        try:
            # Reset battle state flags
            self.battle_result = BattleResult.ONGOING
            self._battle_ended = False
            self.showing_rewards = False
            self._pending_actions.clear()
            
            # Extract battle parameters
            self.is_wild = kwargs.get('is_wild', True)
            self.can_flee = kwargs.get('can_flee', True)
            self.is_boss = kwargs.get('is_boss', False)
            
            # Get player team
            if not kwargs.get('player_team'):
                if not hasattr(self.game, 'party_manager') or not self.game.party_manager:
                    if self.game.debug_mode:
                        print("ERROR: Kein Party Manager verfügbar!")
                    self.game.pop_scene()
                    return
                
                player_team = self.game.party_manager.party.get_conscious_members()
                
                if not player_team:
                    if self.game.debug_mode:
                        print("ERROR: Keine kampffähigen Monster im Team!")
                    self.game.pop_scene()
                    return
            else:
                player_team = kwargs.get('player_team', [])
            
            # Get enemy team
            enemy_team = kwargs.get('enemy_team', [])
            if not enemy_team:
                # Create default enemy monster
                from engine.systems.monsters import MonsterDatabase
                db = MonsterDatabase()
                species = db.get_random_species()
                if species:
                    enemy = species.create_instance(level=5)
                    enemy_team = [enemy]
            
            # Initialize battle using BattleState
            self.battle_state = BattleState(
                player_team=player_team,
                enemy_team=enemy_team,
                battle_type=BattleType.WILD if self.is_wild else BattleType.TRAINER,
                can_flee=self.can_flee,
                can_catch=self.is_wild
            )
            
            # Verbinde Battle-State mit UI
            self.battle_ui.battle_state = self.battle_state
            debug_battle_info("Battle-State mit UI verbunden")
            
            # Start the battle
            from engine.systems.battle.battle_controller import BattleController
            self.battle_controller = BattleController(self.battle_state)
            battle_info = self.battle_controller.start_battle()
            
            # Initialize UI
            self.battle_ui.init_battle(player_team, enemy_team)
            self.battle_ui.battle_state = self.battle_state
            
            # Initialize demo inventory for testing (remove in production)
            if self.game.debug_mode:
                self.battle_ui.init_demo_inventory()
                debug_battle_info("Demo inventory mit Test-Items initialisiert")
            
            # Set initial phase
            self.current_phase = BattlePhase.INPUT
            self.waiting_for_input = True
            
        except Exception as e:
            if self.game.debug_mode:
                print(f"ERROR: Battle initialization failed: {e}")
            import traceback
            traceback.print_exc()
            self.game.pop_scene()
            return
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle input events - OPTIMIZED VERSION."""
        try:
            if not self.battle_state or self._battle_ended:
                return False
            
            # Handle rewards UI input first
            if self.showing_rewards:
                return self._handle_rewards_input(event)
            
            # Handle battle UI input
            handled = self.battle_ui.handle_event(event)
            if handled:
                # Check if UI generated an action
                action_result = self.battle_ui.get_action_result()
                if action_result:
                    debug_battle_info(f"BattleScene received action: {action_result}")
                    self._process_battle_action(action_result)
                    self.battle_ui.clear_pending_action()
                return True
                    
        except Exception as e:
            if self.game.debug_mode:
                print(f"Error in handle_event: {e}")
            
        return False
    
    def _handle_rewards_input(self, event: pygame.event.Event) -> bool:
        """Handle rewards UI input."""
        if event.type == pygame.KEYDOWN:
            action = None
            if event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                action = 'confirm'
            elif event.key == pygame.K_ESCAPE:
                action = 'escape'
            
            if action:
                self.battle_rewards_ui.handle_input(action)
                if self.battle_rewards_ui.is_complete():
                    self.showing_rewards = False
                    self._end_battle()
                    return True
        return False
    
    def _process_battle_action(self, action_result):
        """Process battle actions from UI - OPTIMIZED VERSION."""
        if not action_result or not self.battle_state:
            return
        
        # Import required classes
        from engine.systems.battle.turn_logic_clean import BattleAction, ActionType
        from engine.systems.moves import move_registry
        
        # Handle both 'action' and 'type' fields for compatibility
        action_type = action_result.get('action') or action_result.get('type')
        
        try:
            if action_type == 'attack':
                self._process_attack_action(action_result)
            elif action_type == 'item':
                self._process_item_action(action_result)
            elif action_type == 'switch':
                self._process_switch_action(action_result)
            elif action_type == 'tame':
                self._process_tame_action(action_result)
            elif action_type == 'scout':
                self._process_scout_action(action_result)
            elif action_type == 'flee':
                self._process_flee_action(action_result)
            else:
                debug_battle_error(f"Unknown action type: {action_type}")
                return
            
            # Execute turn after queuing action
            self._execute_battle_turn()
            
        except Exception as e:
            if self.game.debug_mode:
                print(f"Error processing battle action: {e}")
                import traceback
                traceback.print_exc()
    
    def _process_attack_action(self, action_result):
        """Process attack action."""
        from engine.systems.moves import move_registry
        from engine.systems.battle.turn_logic_clean import BattleAction, ActionType
        move_id = action_result.get('move_id')
        move = move_registry.get_move(move_id) or move_registry.get_move('tackle')
        if move:
            battle_action = BattleAction(
                action_type=ActionType.ATTACK,
                actor=self.battle_state.player_active,
                target=self.battle_state.enemy_active,
                move=move
            )
            self.battle_controller.queue_player_action(battle_action)
    
    def _process_item_action(self, action_result):
        """Process item action."""
        from engine.systems.battle.turn_logic_clean import BattleAction, ActionType
        item_id = action_result.get('item_id')
        target = action_result.get('target', self.battle_state.player_active)
        battle_action = BattleAction(
            action_type=ActionType.ITEM,
            actor=self.battle_state.player_active,
            target=target,
            item_id=item_id
        )
        self.battle_controller.queue_player_action(battle_action)
    
    def _process_switch_action(self, action_result):
        """Process switch action."""
        from engine.systems.battle.turn_logic_clean import BattleAction, ActionType
        monster_index = action_result.get('monster_index', 0)
        if 0 <= monster_index < len(self.battle_state.player_team):
            new_monster = self.battle_state.player_team[monster_index]
            battle_action = BattleAction(
                action_type=ActionType.SWITCH,
                actor=self.battle_state.player_active,
                target=new_monster,
                switch_to=new_monster
            )
            self.battle_controller.queue_player_action(battle_action)
    
    def _process_tame_action(self, action_result):
        """Process taming action."""
        from engine.systems.battle.turn_logic_clean import BattleAction, ActionType
        # Initialize meat system if missing
        if not hasattr(self.battle_controller, 'meat_system'):
            from engine.systems.battle.meat_system import MeatSystem
            self.battle_controller.meat_system = MeatSystem()
        
        meat_bonus = action_result.get('meat_bonus', 0)
        if meat_bonus > 0:
            # Use meat system to apply bonus
            from engine.systems.battle.meat_system import MeatType
            meat_type = MeatType.NORMAL if meat_bonus <= 20 else MeatType.SUPER
            self.battle_controller.meat_system.use_meat(meat_type, self.battle_state)
        
        battle_action = BattleAction(
            action_type=ActionType.TAME,
            actor=self.battle_state.player_active,
            target=self.battle_state.enemy_active
        )
        self.battle_controller.queue_player_action(battle_action)
    
    def _process_scout_action(self, action_result):
        """Process scout action."""
        from engine.systems.battle.turn_logic_clean import BattleAction, ActionType
        battle_action = BattleAction(
            action_type=ActionType.SCOUT,
            actor=self.battle_state.player_active,
            target=self.battle_state.enemy_active
        )
        self.battle_controller.queue_player_action(battle_action)
    
    def _process_flee_action(self, action_result):
        """Process flee action."""
        from engine.systems.battle.turn_logic_clean import BattleAction, ActionType
        battle_action = BattleAction(
            action_type=ActionType.FLEE,
            actor=self.battle_state.player_active,
            target=None
        )
        self.battle_controller.queue_player_action(battle_action)
    
    def _execute_battle_turn(self):
        """Execute battle turn - OPTIMIZED VERSION."""
        try:
            # Execute player turn
            player_result = self.battle_controller.execute_turn()
            
            # Check if battle ended
            if player_result and player_result != BattleResult.ONGOING:
                self.battle_result = player_result
                self._handle_battle_end()
                return
            
            # Execute enemy turn
            enemy_result = self.battle_controller.execute_enemy_turn()
            
            # Check if battle ended
            if enemy_result and enemy_result != BattleResult.ONGOING:
                self.battle_result = enemy_result
                self._handle_battle_end()
                return
            
            # Check battle end conditions
            self.check_battle_end()
            
        except Exception as e:
            debug_battle_error(f"Error executing battle turn: {e}")
    
    def _handle_battle_end(self):
        """Handle battle end - OPTIMIZED VERSION."""
        try:
            if self.battle_result == BattleResult.VICTORY:
                self.battle_ui.add_message("Du hast gewonnen!")
                self._show_rewards()
            elif self.battle_result == BattleResult.DEFEAT:
                self.battle_ui.add_message("Du hast verloren!")
                self._show_defeat_screen()
            elif self.battle_result == BattleResult.CAUGHT:
                self.battle_ui.add_message("Monster gefangen!")
                self._show_taming_success()
            elif self.battle_result == BattleResult.FLED:
                self.battle_ui.add_message("Erfolgreich geflohen!")
                self._end_battle()
                
        except Exception as e:
            debug_battle_error(f"Battle end handling failed: {e}")
            self._end_battle()
    
    def update(self, dt: float) -> None:
        """Update battle logic - OPTIMIZED VERSION."""
        try:
            if not self.battle_state or self._battle_ended:
                return
            
            # Performance optimization: Limit update frequency
            current_time = pygame.time.get_ticks() / 1000.0
            if current_time - self._last_update_time < self._update_interval:
                return
            self._last_update_time = current_time
            
            # Update rewards UI if showing
            if self.showing_rewards:
                if self.battle_rewards_ui.update(dt):
                    debug_battle_info("Rewards display complete, ending battle")
                    self.showing_rewards = False
                    self._end_battle()
                return
            
            # Update battle phase management
            self.update_battle_phase()
            
            # Process pending events from controller
            if hasattr(self, 'battle_controller'):
                events = self.battle_controller.get_pending_events()
                for event in events:
                    self.battle_ui.process_battle_event(event)
            
            # Update UI
            self.battle_ui.update(dt)
            
            # Update BattleController if available
            if hasattr(self, 'battle_controller'):
                battle_result = self.battle_controller.update(dt)
                
                # Check if battle ended
                if battle_result and battle_result != BattleResult.ONGOING:
                    self.battle_result = battle_result
                    self.current_phase = BattlePhase.END
                    self._handle_battle_end()
                    
        except Exception as e:
            if self.game.debug_mode:
                print(f"Update error: {e}")
    
    def update_battle_phase(self):
        """Manage battle phase transitions - OPTIMIZED VERSION."""
        if not self.battle_state:
            return
        
        if self.current_phase == BattlePhase.INIT:
            self.initialize_battle()
            self.current_phase = BattlePhase.START
            
        elif self.current_phase == BattlePhase.START:
            self.show_battle_intro()
            self.current_phase = BattlePhase.INPUT
            
        elif self.current_phase == BattlePhase.INPUT:
            # Wait for player input - action processing happens in _process_battle_action
            pass
            
        elif self.current_phase == BattlePhase.END:
            self._handle_battle_end()
    
    def initialize_battle(self):
        """Initialize battle state and UI - OPTIMIZED VERSION."""
        try:
            debug_battle_info("Initializing battle...")
            
            # Ensure battle state is properly set up
            if not self.battle_state.player_active:
                self.battle_state.player_active = self.battle_state.player_team[0]
            if not self.battle_state.enemy_active:
                self.battle_state.enemy_active = self.battle_state.enemy_team[0]
            
            # Initialize UI with battle state
            self.battle_ui.init_battle(
                self.battle_state.player_team,
                self.battle_state.enemy_team
            )
            
            debug_battle_info("Battle initialized successfully")
            
        except Exception as e:
            debug_battle_error(f"Battle initialization failed: {e}")
    
    def show_battle_intro(self):
        """Show battle introduction messages - OPTIMIZED VERSION."""
        try:
            if self.battle_state.enemy_active:
                enemy_name = getattr(self.battle_state.enemy_active, 'name', 'Wildes Monster')
                if self.is_wild:
                    message = f"Ein wildes {enemy_name} erscheint!"
                else:
                    message = f"{enemy_name} greift an!"
                
                self.battle_ui.add_message(message)
                debug_battle_info(f"Battle intro: {message}")
                
        except Exception as e:
            debug_battle_error(f"Battle intro failed: {e}")
    
    def check_battle_end(self) -> bool:
        """Check if battle should end - OPTIMIZED VERSION."""
        try:
            if not self.battle_state:
                return False
            
            # Player defeated - all monsters fainted
            if all(m.current_hp <= 0 for m in self.battle_state.player_team):
                self.battle_result = BattleResult.DEFEAT
                debug_battle_info("Player defeated - all monsters fainted")
                return True
            
            # Enemy defeated
            if self.battle_state.enemy_active.current_hp <= 0:
                if len(self.battle_state.enemy_team) > 1:
                    # More enemies available - switch enemy monster
                    self.switch_enemy_monster()
                    return False
                else:
                    self.battle_result = BattleResult.VICTORY
                    debug_battle_info("Enemy defeated - victory!")
                    return True
            
            # Successful taming
            if hasattr(self.battle_state, 'monster_caught') and self.battle_state.monster_caught:
                self.battle_result = BattleResult.CAUGHT
                debug_battle_info("Monster caught successfully!")
                return True
            
            # Successful flee
            if hasattr(self.battle_state, 'fled') and self.battle_state.fled:
                self.battle_result = BattleResult.FLED
                debug_battle_info("Successfully fled from battle")
                return True
            
            return False
            
        except Exception as e:
            debug_battle_error(f"Battle end check failed: {e}")
            return False
    
    def switch_enemy_monster(self):
        """Switch to next enemy monster - OPTIMIZED VERSION."""
        try:
            if not self.battle_state or len(self.battle_state.enemy_team) <= 1:
                return
            
            # Find next conscious enemy
            for monster in self.battle_state.enemy_team:
                if monster.current_hp > 0 and monster != self.battle_state.enemy_active:
                    self.battle_state.enemy_active = monster
                    self.battle_ui.add_message(f"{monster.name} kommt ins Spiel!")
                    debug_battle_info(f"Switched to enemy: {monster.name}")
                    break
                    
        except Exception as e:
            debug_battle_error(f"Enemy switch failed: {e}")
    
    def _show_defeat_screen(self):
        """Show defeat screen and return to field - OPTIMIZED VERSION."""
        try:
            self.battle_ui.add_message("Du wurdest besiegt...")
            
            # End battle after delay
            if not hasattr(self, '_defeat_timer'):
                self._defeat_timer = 0
            
            self._defeat_timer += 0.016  # Assume 60 FPS
            if self._defeat_timer > 3.0:  # 3 seconds
                self._end_battle()
                
        except Exception as e:
            debug_battle_error(f"Defeat screen failed: {e}")
            self._end_battle()
    
    def _show_taming_success(self):
        """Show taming success screen - OPTIMIZED VERSION."""
        try:
            if self.battle_state and self.battle_state.enemy_active:
                monster_name = getattr(self.battle_state.enemy_active, 'name', 'Monster')
                self.battle_ui.add_message(f"{monster_name} wurde gezähmt!")
                
                # Add caught monster to rewards
                if not hasattr(self, 'battle_rewards'):
                    self.battle_rewards = type('Rewards', (), {})()
                self.battle_rewards.caught_monster = self.battle_state.enemy_active
                
                # Show rewards with caught monster
                self._show_rewards()
                
        except Exception as e:
            debug_battle_error(f"Taming success screen failed: {e}")
            self._end_battle()
    
    def _show_rewards(self):
        """Calculate and show battle rewards - OPTIMIZED VERSION."""
        try:
            # Mark all active monsters as participated
            if self.battle_state and self.battle_state.player_active:
                self.battle_state.player_active.participated = True
            
            # Determine victory type
            victory_type = 'normal'
            if self.battle_result == BattleResult.CAUGHT:
                victory_type = 'caught'
            elif self.battle_state and self.battle_state.player_active:
                # Check for perfect victory (no damage taken)
                if self.battle_state.player_active.current_hp == self.battle_state.player_active.max_hp:
                    victory_type = 'perfect'
            
            # Calculate rewards - with fallback if reward_system fails
            try:
                self.battle_rewards = self.reward_system.calculate_battle_rewards(
                    self.battle_state,
                    victory_type
                )
            except Exception as e:
                if self.game.debug_mode:
                    print(f"[Flint] Reward system failed: {e}, using fallback rewards")
                # Create minimal fallback rewards
                from dataclasses import dataclass
                @dataclass
                class FallbackRewards:
                    exp_gained: dict = None
                    money_gained: int = 50
                    items_gained: list = None
                    level_ups: dict = None
                    caught_monster: object = None
                
                self.battle_rewards = FallbackRewards()
                self.battle_rewards.exp_gained = {}
                self.battle_rewards.items_gained = []
            
            # Add caught monster to rewards
            if self.battle_result == BattleResult.CAUGHT and self.battle_state and self.battle_state.caught_monster:
                self.battle_rewards.caught_monster = self.battle_state.caught_monster
            
            # Apply rewards to game state
            self.give_rewards(self.battle_rewards)
            
            # Prepare rewards data for UI - with safe access
            rewards_ui_data = {
                'exp_gained': getattr(self.battle_rewards, 'exp_gained', {}),
                'money_gained': getattr(self.battle_rewards, 'money_gained', 0),
                'items_gained': getattr(self.battle_rewards, 'items_gained', []),
                'level_ups': getattr(self.battle_rewards, 'level_ups', {})
            }
            
            # For caught monsters, just show simple victory without EXP
            if self.battle_result == BattleResult.CAUGHT:
                rewards_ui_data['exp_gained'] = {}  # No EXP for catching
                rewards_ui_data['money_gained'] = 100  # Small reward for catching
                # Add caught monster info for display
                if self.battle_state and self.battle_state.caught_monster:
                    rewards_ui_data['caught_monster'] = True
                    rewards_ui_data['caught_monster_name'] = self.battle_state.caught_monster.name
            
            # Show rewards UI
            self.battle_rewards_ui.show_rewards(rewards_ui_data)
            self.showing_rewards = True
            
        except Exception as e:
            if self.game.debug_mode:
                print(f"Error showing rewards: {e}")
            import traceback
            traceback.print_exc()
            # If error, just end battle
            self._end_battle()
    
    def give_rewards(self, rewards):
        """Apply battle rewards to player - OPTIMIZED VERSION."""
        try:
            # Give EXP to participating monsters
            if hasattr(rewards, 'exp_gained') and rewards.exp_gained:
                for monster in self.battle_state.player_team:
                    if monster.current_hp > 0 and hasattr(monster, 'add_experience'):
                        monster_id = getattr(monster, 'id', str(id(monster)))
                        if monster_id in rewards.exp_gained:
                            exp_amount = rewards.exp_gained[monster_id]
                            level_up = monster.add_experience(exp_amount)
                            if level_up:
                                self.show_level_up(monster, level_up)
            
            # Give items
            if hasattr(rewards, 'items_gained') and rewards.items_gained:
                for item_id, count in rewards.items_gained:
                    if hasattr(self.game, 'item_manager'):
                        self.game.item_manager.add_item(item_id, count)
                    elif hasattr(self.game, 'player_data'):
                        if not hasattr(self.game.player_data, 'inventory'):
                            self.game.player_data.inventory = {}
                        if item_id in self.game.player_data.inventory:
                            self.game.player_data.inventory[item_id] += count
                        else:
                            self.game.player_data.inventory[item_id] = count
            
            # Give money
            if hasattr(rewards, 'money_gained') and rewards.money_gained > 0:
                if hasattr(self.game, 'player_data'):
                    if not hasattr(self.game.player_data, 'money'):
                        self.game.player_data.money = 0
                    self.game.player_data.money += rewards.money_gained
            
            debug_battle_info("Rewards applied successfully")
            
        except Exception as e:
            debug_battle_error(f"Failed to apply rewards: {e}")
    
    def show_level_up(self, monster, level_up_data):
        """Show level up information - OPTIMIZED VERSION."""
        try:
            if hasattr(level_up_data, 'new_level'):
                self.battle_ui.add_message(f"{monster.name} ist auf Level {level_up_data.new_level} aufgestiegen!")
                
                # Show learned moves if any
                if hasattr(level_up_data, 'learned_moves') and level_up_data.learned_moves:
                    for move in level_up_data.learned_moves:
                        self.battle_ui.add_message(f"{monster.name} hat {move} gelernt!")
                        
        except Exception as e:
            debug_battle_error(f"Level up display failed: {e}")
    
    def _end_battle(self):
        """End the battle and return to field - OPTIMIZED VERSION."""
        # Return to previous scene (only once!)
        if self._battle_ended:
            return
        
        self._battle_ended = True
        
        try:
            # Add caught monster to party if applicable
            if self.battle_result == BattleResult.CAUGHT and self.battle_state and self.battle_state.caught_monster:
                if hasattr(self.game, 'party_manager'):
                    success, msg = self.game.party_manager.add_to_party(self.battle_state.caught_monster)
                    if success:
                        debug_battle_info(f"Monster zu Party hinzugefügt: {msg}")
                    else:
                        debug_battle_error(f"Fehler beim Hinzufügen zur Party: {msg}")
                else:
                    debug_battle_error("Kein Party-Manager verfügbar!")
            
            self.game.pop_scene()
            
        except Exception as e:
            if self.game.debug_mode:
                print(f"End battle error: {e}")
            import traceback
            traceback.print_exc()
            # Still try to pop scene even on error
            try:
                self.game.pop_scene()
            except:
                pass
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw battle scene - OPTIMIZED VERSION."""
        try:
            # Clear screen
            surface.fill(Colors.BATTLE_BG)
            
            # Draw battle UI
            if self.battle_ui:
                self.battle_ui.draw(surface)
            
            # Draw rewards UI if showing
            if self.showing_rewards and self.battle_rewards_ui:
                self.battle_rewards_ui.draw(surface)
            
            # Debug info
            if self.game.debug_mode:
                self._draw_debug_info(surface)
    
        except Exception as e:
            if self.game.debug_mode:
                print(f"Draw error: {e}")
    
    def _draw_debug_info(self, surface: pygame.Surface):
        """Draw debug information - OPTIMIZED VERSION."""
        try:
            font = pygame.font.Font(None, 24)
        
            debug_info = [
                f"Phase: {self.current_phase.name if self.current_phase else 'None'}",
                f"Result: {self.battle_result.name}",
            ]
            
            if self.battle_state:
                player_name = self.battle_state.player_active.name if self.battle_state.player_active else 'None'
                enemy_name = self.battle_state.enemy_active.name if self.battle_state.enemy_active else 'None'
                debug_info.extend([
                    f"Player: {player_name}",
                    f"Enemy: {enemy_name}",
                ])
            
            for i, info in enumerate(debug_info):
                text = font.render(info, True, (255, 255, 0))
                surface.blit(text, (5, 5 + i * 20))
                
        except Exception as e:
            if self.game.debug_mode:
                print(f"Debug draw error: {e}")
