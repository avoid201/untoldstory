#!/usr/bin/env python3
"""
Battle UI Demo for Untold Story.
Test script for the new battle interface system.
"""

import pygame
import sys
import time
from pathlib import Path

# Add engine to path
sys.path.insert(0, str(Path(__file__).parent / "engine"))

from engine.ui.battle_ui import BattleUI, BattleMenuState
from engine.ui.battle_log import BattleLog, MessagePriority, MessageCategory
from engine.ui.battle_styles import set_battle_theme, get_current_style
from engine.core.config import Colors, LOGICAL_WIDTH, LOGICAL_HEIGHT


class MockMonster:
    """Mock monster class for testing."""
    
    def __init__(self, name: str, level: int, hp: int, max_hp: int, status: str = None):
        self.name = name
        self.level = level
        self.current_hp = hp
        self.max_hp = max_hp
        self.status_condition = status
        self.moves = [MockMove("Tackle", 20, 25, "normal")]
    
    def is_fainted(self):
        return self.current_hp <= 0


class MockMove:
    """Mock move class for testing."""
    
    def __init__(self, name: str, current_pp: int, max_pp: int, move_type: str):
        self.name = name
        self.current_pp = current_pp
        self.max_pp = max_pp
        self.type = move_type


class BattleUIDemo:
    """Demo application for the Battle UI system."""
    
    def __init__(self):
        pygame.init()
        
        # Display setup
        self.screen = pygame.display.set_mode((LOGICAL_WIDTH * 4, LOGICAL_HEIGHT * 4))
        pygame.display.set_caption("Untold Story - Battle UI Demo")
        self.clock = pygame.time.Clock()
        
        # Create mock game object
        self.game = type('MockGame', (), {})()
        
        # Initialize UI components
        self.battle_ui = BattleUI(self.game)
        self.battle_log = BattleLog()
        
        # Create mock monsters
        self.player_monsters = [
            MockMonster("Feuerdrache", 25, 45, 60),
            MockMonster("Wasserball", 22, 38, 55),
            MockMonster("Graspflanze", 20, 42, 58)
        ]
        
        self.enemy_monsters = [
            MockMonster("Steingolem", 24, 52, 65, "paralysis"),
            MockMonster("Eisvogel", 21, 35, 50)
        ]
        
        # Initialize battle
        self.battle_ui.init_battle(self.player_monsters, self.enemy_monsters)
        
        # Demo state
        self.demo_timer = 0
        self.current_demo = 0
        self.demo_actions = [
            self._demo_attack,
            self._demo_status_effect,
            self._demo_taming,
            self._demo_item_usage,
            self._demo_critical_hit
        ]
        
        # Add initial messages
        self._add_demo_messages()
        
        # Set theme
        set_battle_theme('modern')
    
    def _add_demo_messages(self):
        """Add initial demo messages to the battle log."""
        self.battle_log.add_message("Willkommen zum Battle UI Demo!", 
                                   MessagePriority.NORMAL, MessageCategory.SYSTEM)
        self.battle_log.add_message("Ein wilder Steingolem erscheint!", 
                                   MessagePriority.NORMAL, MessageCategory.BATTLE_EVENTS)
        self.battle_log.add_message("Dein Feuerdrache macht sich bereit!", 
                                   MessagePriority.NORMAL, MessageCategory.BATTLE_EVENTS)
    
    def _demo_attack(self):
        """Demo attack sequence."""
        self.battle_log.add_attack_message("Feuerdrache", "Steingolem", "Feuerstoß", 25)
        self.battle_ui.add_damage_number(25, (100, 80))
        self.battle_ui.trigger_screen_shake(3, 0.2)
        
        # Update monster HP
        self.enemy_monsters[0].current_hp = max(0, self.enemy_monsters[0].current_hp - 25)
    
    def _demo_status_effect(self):
        """Demo status effect application."""
        self.battle_log.add_status_message("Steingolem", "Verbrennung", True)
        self.battle_ui.trigger_flash_effect(0.3)
        
        # Apply status
        self.enemy_monsters[0].status_condition = "burn"
    
    def _demo_taming(self):
        """Demo taming attempt."""
        self.battle_log.add_taming_message("Feuerdrache", "Steingolem", True)
        self.battle_ui.trigger_flash_effect(0.5)
    
    def _demo_item_usage(self):
        """Demo item usage."""
        self.battle_log.add_item_message("Feuerdrache", "Heiltrank", "Feuerdrache", 20)
        
        # Heal monster
        self.player_monsters[0].current_hp = min(
            self.player_monsters[0].max_hp,
            self.player_monsters[0].current_hp + 20
        )
    
    def _demo_critical_hit(self):
        """Demo critical hit."""
        self.battle_log.add_attack_message("Wasserball", "Eisvogel", "Aqua-Jet", 35, 
                                         is_critical=True, is_super_effective=True)
        self.battle_ui.add_damage_number(35, (80, 60), is_critical=True, is_super_effective=True)
        self.battle_ui.trigger_screen_shake(5, 0.4)
        self.battle_ui.trigger_flash_effect(0.6)
        
        # Update monster HP
        self.enemy_monsters[1].current_hp = max(0, self.enemy_monsters[1].current_hp - 35)
    
    def run(self):
        """Main demo loop."""
        running = True
        
        while running:
            dt = self.clock.tick(60) / 1000.0
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    self._handle_keydown(event.key)
            
            # Update demo
            self._update_demo(dt)
            
            # Update UI
            self.battle_ui.update(dt)
            
            # Draw everything
            self._draw()
            
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()
    
    def _handle_keydown(self, key):
        """Handle keyboard input."""
        if key == pygame.K_ESCAPE:
            pygame.event.post(pygone.event.Event(pygame.QUIT))
        elif key == pygame.K_SPACE:
            # Trigger next demo action
            self.current_demo = (self.current_demo + 1) % len(self.demo_actions)
            self.demo_actions[self.current_demo]()
        elif key == pygame.K_1:
            set_battle_theme('default')
        elif key == pygame.K_2:
            set_battle_theme('dark')
        elif key == pygame.K_3:
            set_battle_theme('light')
        elif key == pygame.K_4:
            set_battle_theme('retro')
        elif key == pygame.K_5:
            set_battle_theme('modern')
        elif key == pygame.K_e:
            # Export battle log
            filename = self.battle_log.export_to_file()
            print(f"Battle log exported to: {filename}")
        elif key == pygame.K_j:
            # Export to JSON
            filename = self.battle_log.export_to_json()
            print(f"Battle log exported to JSON: {filename}")
        elif key == pygame.K_TAB:
            # Toggle menu state
            current_state = self.battle_ui.menu_state
            states = list(BattleMenuState)
            next_state = states[(states.index(current_state) + 1) % len(states)]
            self.battle_ui.set_menu_state(next_state)
        else:
            # Pass input to UI components
            self.battle_ui.handle_input(key)
            self.battle_log.handle_input(key)
    
    def _update_demo(self, dt):
        """Update demo state."""
        self.demo_timer += dt
        
        # Auto-trigger demo actions every 3 seconds
        if self.demo_timer >= 3.0:
            self.demo_timer = 0
            self.demo_actions[self.current_demo]()
    
    def _draw(self):
        """Draw the demo interface."""
        # Clear screen
        self.screen.fill((20, 20, 30))
        
        # Create logical surface
        logical_surface = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT))
        logical_surface.fill((40, 40, 60))
        
        # Draw battle UI
        self.battle_ui.draw(logical_surface)
        
        # Draw battle log
        self.battle_log.draw(logical_surface)
        
        # Draw demo info
        self._draw_demo_info(logical_surface)
        
        # Scale to window
        scaled_surface = pygame.transform.scale(logical_surface, 
                                             (LOGICAL_WIDTH * 4, LOGICAL_HEIGHT * 4))
        self.screen.blit(scaled_surface, (0, 0))
    
    def _draw_demo_info(self, surface):
        """Draw demo information and controls."""
        font = pygame.font.Font(None, 14)
        
        info_lines = [
            "=== BATTLE UI DEMO ===",
            "SPACE: Trigger demo action",
            "TAB: Cycle menu states",
            "1-5: Change themes",
            "E: Export log to TXT",
            "J: Export log to JSON",
            "Arrow keys: Navigate menus",
            "ESC: Quit demo"
        ]
        
        for i, line in enumerate(info_lines):
            color = Colors.YELLOW if i == 0 else Colors.WHITE
            text = font.render(line, True, color)
            surface.blit(text, (LOGICAL_WIDTH - 200, 10 + i * 16))


if __name__ == "__main__":
    demo = BattleUIDemo()
    demo.run()
