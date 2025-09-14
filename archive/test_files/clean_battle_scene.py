"""
Battle Scene for Untold Story - CLEAN VERSION
Bereinigt von AI-Duplikations-Chaos
"""

import pygame
import random
from typing import Optional, List, Dict, Any
from enum import Enum, auto

from engine.core.scene_base import Scene
from engine.core.config import Colors, GameState
from engine.ui.battle_ui import BattleUI, BattleMenuState, MoveSelector
from engine.systems.battle.battle import BattleState, BattlePhase, BattleType
from engine.systems.battle.battle_ai import BattleAI
from engine.systems.monster_instance import MonsterInstance


class BattleResult(Enum):
    """Possible battle outcomes."""
    ONGOING = auto()
    VICTORY = auto()
    DEFEAT = auto()
    FLED = auto()
    CAUGHT = auto()


class BattleScene(Scene):
    """Main battle scene - CLEANED from AI system duplication."""
    
    def __init__(self, game):
        super().__init__(game)
        
        # Battle components - SINGLE consistent system
        self.battle_ui = BattleUI(game)
        self.battle_state = None  # Will be initialized in on_enter
        self.battle_ai = BattleAI()
        
        # UI components
        self.move_selector = MoveSelector()
        
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
        
        # Rewards
        self.exp_gained = 0
        self.items_gained = []
        self.money_gained = 0
        self.caught_monster = None
        
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
            
            # Handle battle UI input first
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
                'name': 'Tackle', 'power': 40, 'category': type('Cat', (), {'value': 'phys'})(),
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
                self._end_battle()
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
            self.caught_monster = enemy
            self.battle_result = BattleResult.CAUGHT
            self._end_battle()
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
    
    def update(self, dt: float) -> None:
        """Update battle logic."""
        try:
            if not self.battle_state:
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
    
    def _end_battle(self):
        """End the battle and return to field."""
        try:
            # Process rewards if victory
            if self.battle_result == BattleResult.VICTORY:
                self._process_rewards()
            
            # Add caught monster to party if applicable
            if self.caught_monster and hasattr(self.game, 'party_manager'):
                success, msg = self.game.party_manager.add_to_party(self.caught_monster)
                if success:
                    self.battle_ui.add_message(msg)
            
            # Return to previous scene
            self.game.pop_scene()
            
        except Exception as e:
            print(f"End battle error: {e}")
            self.game.pop_scene()
    
    def _process_rewards(self):
        """Process battle rewards."""
        try:
            if self.battle_state and self.battle_state.enemy_active:
                exp = self.battle_state.enemy_active.level * 10
                money = self.battle_state.enemy_active.level * 5
                
                self.battle_ui.add_message(f"Du erhältst {exp} EP und {money} Geld!")
                
                # Give EXP to active monster if possible
                if self.battle_state.player_active and hasattr(self.battle_state.player_active, 'gain_exp'):
                    self.battle_state.player_active.gain_exp(exp)
                
        except Exception as e:
            print(f"Reward processing error: {e}")
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw battle scene."""
        try:
            # Clear screen
            surface.fill(Colors.BATTLE_BG)
            
            # Draw battle UI
            if self.battle_ui:
                self.battle_ui.draw(surface)
            
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
