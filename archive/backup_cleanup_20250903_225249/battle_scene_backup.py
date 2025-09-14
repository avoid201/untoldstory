"""
Battle Scene for Untold Story - SYNTAX FIXED VERSION
Alle Syntax-Fehler behoben, funktionsfähig
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
from engine.systems.battle.battle_enums import BattleResult  # Unified import
from engine.systems.battle.reward_system import RewardSystem, BattleRewards
from engine.systems.monster_instance import MonsterInstance


class BattleScene(Scene):
    """Main battle scene - SYNTAX FIXED."""
    
    def __init__(self, game):
        super().__init__(game)
        
        # Battle components
        self.battle_ui = BattleUI(game)
        self.battle_rewards_ui = BattleRewardsUI()
        self.battle_state = None
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
        
        # Rewards data
        self.battle_rewards = None
        
    def on_enter(self, **kwargs):
        """Initialize battle from kwargs."""
        try:
            # Reset battle result
            self.battle_result = BattleResult.ONGOING
            
            # Extract battle parameters
            self.is_wild = kwargs.get('is_wild', True)
            self.can_flee = kwargs.get('can_flee', True)
            
            # Get player team
            if not kwargs.get('player_team'):
                if not hasattr(self.game, 'party_manager') or not self.game.party_manager:
                    print("ERROR: Kein Party Manager verfügbar!")
                    self.game.pop_scene()
                    return
                
                player_team = self.game.party_manager.party.get_conscious_members()
                
                if not player_team:
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
            
            # Start the battle
            battle_info = self.battle_state.start_battle()
            print(f"Battle started: {battle_info}")
            
            # Initialize UI
            self.battle_ui.init_battle(player_team, enemy_team)
            
        except Exception as e:
            print(f"ERROR: Battle initialization failed: {e}")
            import traceback
            traceback.print_exc()
            self.game.pop_scene()
            return
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle input events."""
        try:
            if not self.battle_state:
                return False
            
            # Handle rewards UI input first
            if self.showing_rewards:
                if event.type == pygame.KEYDOWN:
                    action = None
                    if event.key == pygame.K_RETURN:
                        action = 'confirm'
                    elif event.key == pygame.K_ESCAPE:
                        action = 'escape'
                    
                    if action and self.battle_rewards_ui.handle_input(action):
                        # Check if rewards are complete
                        if self.battle_rewards_ui.is_complete():
                            self.showing_rewards = False
                            self._end_battle()
                        return True
                return False
            
            # Handle battle UI input
            if self.battle_ui.handle_event(event):
                return True
            
            # Handle keyboard input for battle
            if event.type == pygame.KEYDOWN:
                return self._handle_keyboard_input(event)
                    
        except Exception as e:
            print(f"Error in handle_event: {e}")
            
        return False
    
    def _handle_keyboard_input(self, event: pygame.event.Event) -> bool:
        """Handle keyboard input for battle."""
        try:
            if event.key == pygame.K_ESCAPE:
                return self._handle_flee_action()
            elif event.key == pygame.K_1:
                return self._handle_attack_action()
            elif event.key == pygame.K_2 and self.is_wild:
                return self._handle_taming_action()
            elif event.key == pygame.K_3:
                return self._handle_item_action()
            elif event.key == pygame.K_4:
                return self._handle_switch_action()
            elif event.key == pygame.K_5:
                return self._handle_scout_action()
            elif event.key == pygame.K_RETURN:
                return self._execute_simple_attack()
                
        except Exception as e:
            print(f"Error handling keyboard input: {e}")
        
        return False
    
    def _handle_attack_action(self) -> bool:
        """Handle attack action."""
        if not self.battle_state or not self.battle_state.player_active:
            return False
            
        # Simple attack for now
        return self._execute_simple_attack()
    
    def _execute_simple_attack(self) -> bool:
        """Execute a simple attack."""
        try:
            if not self.battle_state:
                return False
            
            player = self.battle_state.player_active
            enemy = self.battle_state.enemy_active
            
            if not player or not enemy:
                return False
            
            # Use our DamageCalculationPipeline system
            from engine.systems.moves import MoveExecutor
            
            # Create a basic tackle move
            basic_move = type('Move', (), {
                'name': 'Tackle', 
                'power': 40, 
                'category': type('Cat', (), {'value': 'phys'})(),
                'type': player.types[0] if player.types else 'Bestie'
            })()
            
            damage = MoveExecutor._calculate_damage(basic_move, player, enemy)
            
            # Apply damage
            enemy.current_hp = max(0, enemy.current_hp - damage)
            self.battle_ui.add_message(f"{player.name} greift an für {damage} Schaden!")
            
            # Check for battle end
            if enemy.current_hp <= 0:
                enemy.is_fainted = True
                self.battle_result = BattleResult.VICTORY
                self.battle_ui.add_message("Du hast gewonnen!")
                self._show_rewards()
            else:
                # Enemy turn
                self._execute_enemy_turn()
                
            return True
                
        except Exception as e:
            print(f"Attack execution error: {e}")
            return False

    def _execute_enemy_turn(self):
        """Execute enemy turn."""
        try:
            if not self.battle_state:
                return
                
            enemy = self.battle_state.enemy_active
            player = self.battle_state.player_active
            
            if not enemy or not player:
                return
            
            # Simple enemy damage
            damage = 5 + enemy.level
            player.current_hp = max(0, player.current_hp - damage)
            
            self.battle_ui.add_message(f"{enemy.name} greift an für {damage} Schaden!")
            
            if player.current_hp <= 0:
                player.is_fainted = True
                self.battle_result = BattleResult.DEFEAT
                self.battle_ui.add_message("Du hast verloren!")
                # No rewards for defeat
                self._end_battle()
                
        except Exception as e:
            print(f"Enemy turn error: {e}")
    
    def _handle_taming_action(self) -> bool:
        """Handle taming action."""
        if not self.is_wild or not self.battle_state or not self.battle_state.enemy_active:
            self.battle_ui.add_message("Zähmen nur bei wilden Monstern möglich!")
            return False
        
        # Simple taming calculation
        enemy = self.battle_state.enemy_active
        hp_percent = enemy.current_hp / enemy.max_hp
        taming_chance = 0.3 + (1.0 - hp_percent) * 0.4  # Better chance with lower HP
        
        if random.random() < taming_chance:
            self.battle_ui.add_message(f"{enemy.name} wurde erfolgreich gezähmt!")
            self.battle_result = BattleResult.CAUGHT
            self._show_rewards()  # Show rewards for caught
        else:
            self.battle_ui.add_message("Zähmen fehlgeschlagen!")
            self._execute_enemy_turn()
        
        return True
    
    def _handle_flee_action(self) -> bool:
        """Handle flee action."""
        if not self.can_flee or not self.battle_state:
            self.battle_ui.add_message("Flucht nicht möglich!")
            return False
        
        # Simple flee calculation
        flee_chance = 0.8  # 80% success rate
        
        if random.random() < flee_chance:
            self.battle_ui.add_message("Erfolgreich geflohen!")
            self.battle_result = BattleResult.FLED
            self._end_battle()
        else:
            self.battle_ui.add_message("Flucht fehlgeschlagen!")
            self._execute_enemy_turn()
        
        return True
        
    def _handle_item_action(self) -> bool:
        """Handle item usage action."""
        if not self.battle_state:
            return False
        
        # Simplified item usage
        self.battle_ui.add_message("Item-System noch nicht implementiert!")
        return False
    
    def _handle_switch_action(self) -> bool:
        """Handle monster switching action."""
        if not self.battle_state or not hasattr(self.game, 'party_manager'):
            return False
        
        # Get available monsters to switch to
        available_monsters = []
        party = self.game.party_manager.party
        
        for i, monster in enumerate(party.members):
            if (monster and 
                monster != self.battle_state.player_active and 
                monster.current_hp > 0 and 
                not getattr(monster, 'is_fainted', False)):
                available_monsters.append((i, monster))
        
        if not available_monsters:
            self.battle_ui.add_message("Keine anderen Monster zum Wechseln!")
            return False
        
        # Switch to first available monster
        switch_index, new_monster = available_monsters[0]
        
        # Update battle state
        self.battle_state.player_active = new_monster
        self.battle_ui.add_message(f"{new_monster.name}, du bist dran!")
        
        self._execute_enemy_turn()
        return True
    
    def _handle_scout_action(self) -> bool:
        """Handle scout action to get enemy info."""
        if not self.battle_state or not self.battle_state.enemy_active:
            return False
        
        enemy = self.battle_state.enemy_active
        self.battle_ui.add_message(f"Spähen: {enemy.name}")
        self.battle_ui.add_message(f"Level: {enemy.level}")
        self.battle_ui.add_message(f"HP: {enemy.current_hp}/{enemy.max_hp}")
        
        if hasattr(enemy, 'types') and enemy.types:
            self.battle_ui.add_message(f"Typ: {', '.join(enemy.types)}")
        
        self._execute_enemy_turn()
        return True
    
    def update(self, dt: float) -> None:
        """Update battle logic."""
        try:
            if not self.battle_state:
                return
            
            # Update rewards UI if showing
            if self.showing_rewards:
                self.battle_rewards_ui.update(dt)
                return
        
            # Update UI
            self.battle_ui.update(dt)
            
            # Check if battle should end
            if self.battle_result != BattleResult.ONGOING:
                # Show result briefly then end
                if hasattr(self, '_end_timer'):
                    self._end_timer += dt
                    if self._end_timer > 2.0:
                        self._end_battle()
                else:
                    self._end_timer = 0
                    
        except Exception as e:
            print(f"Update error: {e}")
    
    def _show_rewards(self):
        """Calculate and show battle rewards."""
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
            
            # Calculate rewards
            self.battle_rewards = self.reward_system.calculate_battle_rewards(
                self.battle_state,
                victory_type
            )
            
            # Add caught monster to rewards
            if self.battle_result == BattleResult.CAUGHT and self.battle_state:
                self.battle_rewards.caught_monster = self.battle_state.enemy_active
            
            # Apply rewards to game state
            if hasattr(self.game, 'player_data'):
                # Apply money
                if not hasattr(self.game.player_data, 'money'):
                    self.game.player_data.money = 0
                self.game.player_data.money += self.battle_rewards.money_gained
                
                # Apply items to inventory
                if not hasattr(self.game.player_data, 'inventory'):
                    self.game.player_data.inventory = {}
                for item_id, quantity in self.battle_rewards.items_gained:
                    if item_id in self.game.player_data.inventory:
                        self.game.player_data.inventory[item_id] += quantity
                    else:
                        self.game.player_data.inventory[item_id] = quantity
            
            # Prepare rewards data for UI
            rewards_ui_data = {
                'exp_gained': self.battle_rewards.exp_gained,
                'money_gained': self.battle_rewards.money_gained,
                'items_gained': self.battle_rewards.items_gained,
                'level_ups': self.battle_rewards.level_ups
            }
            
            # Show rewards UI
            self.battle_rewards_ui.show_rewards(rewards_ui_data)
            self.showing_rewards = True
            
        except Exception as e:
            print(f"Error showing rewards: {e}")
            import traceback
            traceback.print_exc()
            # If error, just end battle
            self._end_battle()
    
    def _end_battle(self):
        """End the battle and return to field."""
        try:
            # Add caught monster to party if applicable
            if self.battle_rewards and self.battle_rewards.caught_monster:
                if hasattr(self.game, 'party_manager'):
                    success, msg = self.game.party_manager.add_to_party(self.battle_rewards.caught_monster)
                    if success:
                        self.battle_ui.add_message(msg)
            
            # Return to previous scene
            self.game.pop_scene()
            
        except Exception as e:
            print(f"End battle error: {e}")
            self.game.pop_scene()
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw battle scene."""
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
            print(f"Draw error: {e}")
    
    def _draw_debug_info(self, surface: pygame.Surface):
        """Draw debug information."""
        try:
            font = pygame.font.Font(None, 24)
        
            debug_info = [
                f"Phase: {self.current_phase.name if self.current_phase else 'None'}",
                f"Result: {self.battle_result.name}",
            ]
            
            if self.battle_state:
                debug_info.extend([
                    f"Player: {self.battle_state.player_active.name if self.battle_state.player_active else 'None'}",
                    f"Enemy: {self.battle_state.enemy_active.name if self.battle_state.enemy_active else 'None'}",
                ])
            
            for i, info in enumerate(debug_info):
                text = font.render(info, True, (255, 255, 0))
                surface.blit(text, (5, 5 + i * 20))
                
        except Exception as e:
            print(f"Debug draw error: {e}")
