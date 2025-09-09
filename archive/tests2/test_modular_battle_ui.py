"""
Test für modulare Battle UI Komponenten
Testet alle neuen Module und deren Integration
"""

import sys
import os
import unittest
from unittest.mock import Mock, MagicMock, patch

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pygame
from engine.ui.battle import BattleUI, BattleUIState, BattleMenuState
from engine.ui.battle.battle_ui_core import BattleUI
from engine.ui.battle.battle_ui_state import BattleUIState, BattleMenuState
from engine.ui.battle.battle_ui_renderer import BattleUIRenderer
from engine.ui.battle.battle_ui_input import BattleUIInputHandler
from engine.ui.battle.battle_ui_menus import BattleUIMenuManager


class TestModularBattleUI(unittest.TestCase):
    """Test für modulare Battle UI."""
    
    def setUp(self):
        """Setup für Tests."""
        # Mock pygame
        pygame.init = Mock()
        pygame.display = Mock()
        
        # Mock game
        self.mock_game = Mock()
        self.mock_game.resources = Mock()
        
        # Mock battle state
        self.mock_battle_state = Mock()
        
        # Mock monsters
        self.mock_player_monster = Mock()
        self.mock_player_monster.id = "player_monster"
        self.mock_player_monster.name = "TestMonster"
        self.mock_player_monster.level = 10
        self.mock_player_monster.current_hp = 50
        self.mock_player_monster.max_hp = 100
        self.mock_player_monster.moves = ["Kratzer", "Biss"]
        self.mock_player_monster.stats = {"atk": 50, "def": 40, "mag": 30, "res": 25, "spd": 45}
        
        self.mock_enemy_monster = Mock()
        self.mock_enemy_monster.id = "enemy_monster"
        self.mock_enemy_monster.name = "EnemyMonster"
        self.mock_enemy_monster.level = 12
        self.mock_enemy_monster.current_hp = 80
        self.mock_enemy_monster.max_hp = 120
        self.mock_enemy_monster.moves = ["Feuerball", "Flammenwurf"]
        self.mock_enemy_monster.stats = {"atk": 60, "def": 50, "mag": 40, "res": 35, "spd": 55}
    
    def test_battle_ui_initialization(self):
        """Test Battle UI Initialisierung."""
        with patch('engine.ui.battle.battle_ui_core.resources'):
            battle_ui = BattleUI(self.mock_game)
            
            # Test dass alle Komponenten initialisiert wurden
            self.assertIsNotNone(battle_ui.state)
            self.assertIsNotNone(battle_ui.renderer)
            self.assertIsNotNone(battle_ui.input_handler)
            self.assertIsNotNone(battle_ui.menu_manager)
            self.assertIsNotNone(battle_ui.taming_ui)
            self.assertIsNotNone(battle_ui.scout_display)
            
            # Test initial state
            self.assertEqual(battle_ui.state.menu_state, BattleMenuState.MAIN)
            self.assertEqual(battle_ui.state.selected_option, 0)
    
    def test_battle_ui_state_management(self):
        """Test Battle UI State Management."""
        state = BattleUIState()
        
        # Test initial state
        self.assertEqual(state.menu_state, BattleMenuState.MAIN)
        self.assertEqual(state.selected_option, 0)
        
        # Test state changes
        state.set_menu_state(BattleMenuState.MOVE_SELECT)
        self.assertEqual(state.menu_state, BattleMenuState.MOVE_SELECT)
        
        # Test navigation
        state.navigate_down()
        self.assertEqual(state.selected_option, 1)
        
        state.navigate_up()
        self.assertEqual(state.selected_option, 0)
        
        # Test reset
        state.reset()
        self.assertEqual(state.menu_state, BattleMenuState.MAIN)
        self.assertEqual(state.selected_option, 0)
    
    def test_battle_ui_input_handling(self):
        """Test Battle UI Input Handling."""
        with patch('engine.ui.battle.battle_ui_core.resources'):
            battle_ui = BattleUI(self.mock_game)
            
            # Test main menu input
            battle_ui.handle_input("DOWN")
            self.assertEqual(battle_ui.state.selected_option, 1)
            
            battle_ui.handle_input("UP")
            self.assertEqual(battle_ui.state.selected_option, 0)
            
            # Test menu state change
            battle_ui.handle_input("CONFIRM")
            # Sollte zu MOVE_SELECT wechseln (erste Option ist ATTACKE)
            self.assertEqual(battle_ui.state.menu_state, BattleMenuState.MOVE_SELECT)
    
    def test_battle_ui_menu_manager(self):
        """Test Battle UI Menu Manager."""
        with patch('engine.ui.battle.battle_ui_core.resources'):
            battle_ui = BattleUI(self.mock_game)
            menu_manager = battle_ui.menu_manager
            
            # Test move categorization
            moves = menu_manager.get_moves_by_category(self.mock_player_monster, "PHYSISCH")
            self.assertIsInstance(moves, list)
            
            # Test item management
            items = menu_manager.get_items_for_category("HEILUNG")
            self.assertIsInstance(items, list)
            
            # Test taming chance calculation
            chance = menu_manager.calculate_taming_chance(self.mock_enemy_monster)
            self.assertIsInstance(chance, int)
            self.assertGreaterEqual(chance, 5)
            self.assertLessEqual(chance, 95)
    
    def test_battle_ui_renderer(self):
        """Test Battle UI Renderer."""
        with patch('engine.ui.battle.battle_ui_core.resources'):
            battle_ui = BattleUI(self.mock_game)
            renderer = battle_ui.renderer
            
            # Test renderer initialization
            self.assertIsNotNone(renderer)
            self.assertEqual(renderer.battle_ui, battle_ui)
            self.assertEqual(renderer.state, battle_ui.state)
    
    def test_battle_initialization(self):
        """Test Battle Initialisierung."""
        with patch('engine.ui.battle.battle_ui_core.resources'):
            battle_ui = BattleUI(self.mock_game)
            
            # Test battle init
            player_team = [self.mock_player_monster]
            enemy_team = [self.mock_enemy_monster]
            
            battle_ui.init_battle(player_team, enemy_team)
            
            # Test dass Teams gesetzt wurden
            self.assertEqual(battle_ui.state.player_team, player_team)
            self.assertEqual(battle_ui.state.enemy_team, enemy_team)
            self.assertEqual(battle_ui.state.player_active, self.mock_player_monster)
            self.assertEqual(battle_ui.state.enemy_active, self.mock_enemy_monster)
    
    def test_menu_navigation(self):
        """Test Menu Navigation."""
        state = BattleUIState()
        
        # Test main menu navigation
        state.set_menu_state(BattleMenuState.MAIN)
        
        # Navigate down
        state.navigate_down()
        self.assertEqual(state.selected_option, 1)
        
        # Navigate up
        state.navigate_up()
        self.assertEqual(state.selected_option, 0)
        
        # Test move menu navigation
        state.set_menu_state(BattleMenuState.MOVE_SELECT)
        state.navigate_right()
        self.assertEqual(state.current_move_category, 1)
        
        state.navigate_left()
        self.assertEqual(state.current_move_category, 0)
    
    def test_taming_state_management(self):
        """Test Taming State Management."""
        state = BattleUIState()
        
        # Test taming state
        state.set_taming_state("Fleisch", 20)
        self.assertTrue(state.taming_state["meat_selected"])
        self.assertEqual(state.taming_state["meat_type"], "Fleisch")
        self.assertEqual(state.taming_state["taming_chance"], 20)
        self.assertTrue(state.taming_state["show_chance"])
    
    def test_scout_state_management(self):
        """Test Scout State Management."""
        state = BattleUIState()
        
        # Test scout state
        state.set_scout_state(self.mock_enemy_monster, True)
        self.assertTrue(state.scout_state["active"])
        self.assertEqual(state.scout_state["monster"], self.mock_enemy_monster)
        self.assertEqual(state.scout_state["tab"], 0)
    
    def test_visual_effects(self):
        """Test Visual Effects."""
        with patch('engine.ui.battle.battle_ui_core.resources'):
            battle_ui = BattleUI(self.mock_game)
            
            # Test damage number
            battle_ui.add_damage_number(50, 100, 100, is_critical=True)
            self.assertEqual(len(battle_ui.damage_numbers), 1)
            
            # Test screen flash
            battle_ui.trigger_screen_flash(128)
            self.assertGreater(battle_ui.screen_flash_timer, 0)
            self.assertEqual(battle_ui.screen_flash_intensity, 128)
            
            # Test screen shake
            battle_ui.trigger_screen_shake(5, 0.3)
            self.assertGreater(battle_ui.screen_shake_timer, 0)
            self.assertEqual(battle_ui.screen_shake_intensity, 5)
    
    def test_message_system(self):
        """Test Message System."""
        with patch('engine.ui.battle.battle_ui_core.resources'):
            battle_ui = BattleUI(self.mock_game)
            
            # Test message display
            battle_ui.show_message("Test Message")
            self.assertEqual(battle_ui.current_message, "Test Message")
            self.assertTrue(battle_ui.message_wait)
            self.assertEqual(battle_ui.state.menu_state, BattleMenuState.MESSAGE)
            
            # Test message addition
            battle_ui.add_message("Another Message", wait=False)
            self.assertEqual(battle_ui.current_message, "Another Message")
            self.assertFalse(battle_ui.message_wait)
    
    def test_battle_ui_integration(self):
        """Test Battle UI Integration."""
        with patch('engine.ui.battle.battle_ui_core.resources'):
            battle_ui = BattleUI(self.mock_game)
            
            # Test dass alle Komponenten korrekt verbunden sind
            self.assertEqual(battle_ui.renderer.battle_ui, battle_ui)
            self.assertEqual(battle_ui.input_handler.battle_ui, battle_ui)
            self.assertEqual(battle_ui.menu_manager.battle_ui, battle_ui)
            
            # Test dass alle Komponenten den gleichen State verwenden
            self.assertEqual(battle_ui.renderer.state, battle_ui.state)
            self.assertEqual(battle_ui.input_handler.state, battle_ui.state)
            self.assertEqual(battle_ui.menu_manager.state, battle_ui.state)


if __name__ == '__main__':
    # Setup pygame for testing
    pygame.init()
    
    # Run tests
    unittest.main()
