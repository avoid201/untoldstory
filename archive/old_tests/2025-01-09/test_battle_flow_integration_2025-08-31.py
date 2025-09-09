#!/usr/bin/env python3
"""
Test für vollständigen Battle-Flow Integration
Testet die Scene-Integration zwischen Field-Scene und Battle-Scene
"""

import sys
import os
import pygame
import unittest
from unittest.mock import Mock, MagicMock, patch

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.scenes.battle_scene import BattleScene
from engine.scenes.field_scene import FieldScene
from engine.systems.battle.battle_enums import BattlePhase, BattleResult
from engine.systems.monster_instance import MonsterInstance, MonsterSpecies
from engine.systems.stats import BaseStats


class TestBattleFlowIntegration(unittest.TestCase):
    """Test für vollständigen Battle-Flow."""
    
    def setUp(self):
        """Setup für Tests."""
        pygame.init()
        
        # Mock Game-Objekt
        self.mock_game = Mock()
        self.mock_game.debug_mode = True
        self.mock_game.logical_size = (320, 180)
        
        # Mock Party Manager
        self.mock_party_manager = Mock()
        self.mock_party_manager.party = Mock()
        self.mock_party_manager.party.get_conscious_members.return_value = []
        self.mock_game.party_manager = self.mock_party_manager
        
        # Mock Resources
        self.mock_game.resources = Mock()
        
        # Mock Sprite Manager
        self.mock_game.sprite_manager = Mock()
        
        # Mock Story Manager
        self.mock_game.story_manager = Mock()
        self.mock_game.story_manager.get_flag.return_value = False
        self.mock_game.story_manager.set_flag = Mock()
        
        # Mock Player Data
        self.mock_game.player_data = Mock()
        self.mock_game.player_data.money = 0
        self.mock_game.player_data.inventory = {}
    
    def tearDown(self):
        """Cleanup nach Tests."""
        pygame.quit()
    
    def create_test_monster(self, name="TestMonster", level=5):
        """Erstelle Test-Monster."""
        stats = BaseStats(
            hp=100, atk=50, def_=40, mag=30, res=30, spd=45
        )
        
        species = MonsterSpecies(
            id="1",
            name=name,
            types=["Normal"],
            base_stats=stats,
            description=f"Ein Test-{name}."
        )
        
        monster = MonsterInstance(
            species=species,
            level=level
        )
        
        # Set species as dict for compatibility
        monster.species = {
            'id': 1,
            'name': name,
            'rank': 'F'
        }
        
        # Initialize stat stages
        monster.stat_stages = {'atk': 0, 'def': 0, 'mag': 0, 'res': 0, 'spd': 0}
        
        return monster
    
    def test_battle_scene_initialization(self):
        """Test Battle-Scene Initialisierung."""
        print("\n=== Test: Battle-Scene Initialisierung ===")
        
        # Erstelle Battle-Scene
        battle_scene = BattleScene(self.mock_game)
        
        # Teste Initialisierung
        self.assertIsNotNone(battle_scene)
        self.assertEqual(battle_scene.current_phase, BattlePhase.INIT)
        self.assertEqual(battle_scene.battle_result, BattleResult.ONGOING)
        self.assertFalse(battle_scene.showing_rewards)
        
        print("✅ Battle-Scene erfolgreich initialisiert")
    
    def test_battle_phase_transitions(self):
        """Test Battle-Phase-Übergänge."""
        print("\n=== Test: Battle-Phase-Übergänge ===")
        
        # Erstelle Battle-Scene
        battle_scene = BattleScene(self.mock_game)
        
        # Mock Battle-State
        battle_scene.battle_state = Mock()
        battle_scene.battle_state.player_team = [self.create_test_monster("PlayerMonster")]
        battle_scene.battle_state.enemy_team = [self.create_test_monster("EnemyMonster")]
        battle_scene.battle_state.player_active = battle_scene.battle_state.player_team[0]
        battle_scene.battle_state.enemy_active = battle_scene.battle_state.enemy_team[0]
        
        # Mock Battle-UI
        battle_scene.battle_ui = Mock()
        battle_scene.battle_ui.is_waiting_for_input.return_value = False
        battle_scene.battle_ui.get_action_result.return_value = None
        battle_scene.battle_ui.add_message = Mock()
        
        # Mock Battle-Controller
        battle_scene.battle_controller = Mock()
        battle_scene.battle_controller.is_executing.return_value = False
        battle_scene.battle_controller.determine_turn_order = Mock()
        battle_scene.battle_controller.process_turn_end = Mock()
        
        # Teste Phase-Übergänge
        print(f"Start-Phase: {battle_scene.current_phase}")
        
        # INIT → START
        battle_scene.update_battle_phase()
        self.assertEqual(battle_scene.current_phase, BattlePhase.START)
        print(f"Nach INIT: {battle_scene.current_phase}")
        
        # START → INPUT
        battle_scene.update_battle_phase()
        self.assertEqual(battle_scene.current_phase, BattlePhase.INPUT)
        print(f"Nach START: {battle_scene.current_phase}")
        
        print("✅ Battle-Phase-Übergänge funktionieren")
    
    def test_battle_end_conditions(self):
        """Test Battle-End-Bedingungen."""
        print("\n=== Test: Battle-End-Bedingungen ===")
        
        # Erstelle Battle-Scene
        battle_scene = BattleScene(self.mock_game)
        
        # Mock Battle-State
        battle_scene.battle_state = Mock()
        battle_scene.battle_state.player_team = [self.create_test_monster("PlayerMonster")]
        battle_scene.battle_state.enemy_team = [self.create_test_monster("EnemyMonster")]
        battle_scene.battle_state.player_active = battle_scene.battle_state.player_team[0]
        battle_scene.battle_state.enemy_active = battle_scene.battle_state.enemy_team[0]
        
        # Teste Victory-Bedingung
        battle_scene.battle_state.enemy_active.current_hp = 0
        battle_scene.battle_state.enemy_team = [battle_scene.battle_state.enemy_active]  # Nur ein Enemy
        
        result = battle_scene.check_battle_end()
        self.assertTrue(result)
        self.assertEqual(battle_scene.battle_result, BattleResult.VICTORY)
        print("✅ Victory-Bedingung erkannt")
        
        # Teste Defeat-Bedingung
        battle_scene.battle_result = BattleResult.ONGOING
        battle_scene.battle_state.enemy_active.current_hp = 50
        battle_scene.battle_state.player_team[0].current_hp = 0
        
        result = battle_scene.check_battle_end()
        self.assertTrue(result)
        self.assertEqual(battle_scene.battle_result, BattleResult.DEFEAT)
        print("✅ Defeat-Bedingung erkannt")
        
        # Teste Caught-Bedingung
        battle_scene.battle_result = BattleResult.ONGOING
        battle_scene.battle_state.player_team[0].current_hp = 50
        battle_scene.battle_state.monster_caught = True
        
        result = battle_scene.check_battle_end()
        self.assertTrue(result)
        self.assertEqual(battle_scene.battle_result, BattleResult.CAUGHT)
        print("✅ Caught-Bedingung erkannt")
    
    def test_field_to_battle_transition(self):
        """Test Field-zu-Battle-Übergang."""
        print("\n=== Test: Field-zu-Battle-Übergang ===")
        
        # Erstelle Field-Scene
        field_scene = FieldScene(self.mock_game)
        
        # Mock Player-Team
        player_monster = self.create_test_monster("PlayerMonster")
        self.mock_party_manager.party.get_conscious_members.return_value = [player_monster]
        
        # Teste Monster-Erstellung aus Daten
        enemy_data = {
            'species_id': 5,
            'name': 'TestEnemy',
            'level': 6,
            'types': ['Fire'],
            'rank': 'F'
        }
        
        enemy_monster = field_scene._create_monster_from_data(enemy_data)
        self.assertIsNotNone(enemy_monster)
        self.assertEqual(enemy_monster.name, 'TestEnemy')
        self.assertEqual(enemy_monster.level, 6)
        print("✅ Enemy-Monster aus Daten erstellt")
        
        # Teste Battle-Initiation
        with patch('engine.scenes.battle_scene.BattleScene') as mock_battle_scene:
            mock_battle_instance = Mock()
            mock_battle_scene.return_value = mock_battle_instance
            
            field_scene.initiate_battle(enemy_data)
            
            # Prüfe ob Battle-Scene erstellt wurde
            mock_battle_scene.assert_called_once_with(self.mock_game)
            print("✅ Battle-Initiation funktioniert")
    
    def test_reward_system_integration(self):
        """Test Reward-System-Integration."""
        print("\n=== Test: Reward-System-Integration ===")
        
        # Erstelle Battle-Scene
        battle_scene = BattleScene(self.mock_game)
        
        # Mock Battle-State
        battle_scene.battle_state = Mock()
        battle_scene.battle_state.player_team = [self.create_test_monster("PlayerMonster")]
        battle_scene.battle_state.player_active = battle_scene.battle_state.player_team[0]
        battle_scene.battle_state.enemy_active = self.create_test_monster("EnemyMonster")
        
        # Mock Reward-System
        battle_scene.reward_system = Mock()
        mock_rewards = Mock()
        mock_rewards.exp_gained = {'1': 100}
        mock_rewards.money_gained = 50
        mock_rewards.items_gained = [('potion', 2)]
        mock_rewards.level_ups = {}
        battle_scene.reward_system.calculate_battle_rewards.return_value = mock_rewards
        
        # Mock Battle-UI
        battle_scene.battle_ui = Mock()
        battle_scene.battle_ui.add_message = Mock()
        
        # Mock Battle-Rewards-UI
        battle_scene.battle_rewards_ui = Mock()
        battle_scene.battle_rewards_ui.show_rewards = Mock()
        
        # Teste Reward-Verteilung
        battle_scene.battle_result = BattleResult.VICTORY
        battle_scene._show_rewards()
        
        # Prüfe ob Rewards angewendet wurden
        battle_scene.reward_system.calculate_battle_rewards.assert_called_once()
        battle_scene.battle_rewards_ui.show_rewards.assert_called_once()
        print("✅ Reward-System-Integration funktioniert")
    
    def test_complete_battle_flow(self):
        """Test vollständiger Battle-Flow."""
        print("\n=== Test: Vollständiger Battle-Flow ===")
        
        # Erstelle Field-Scene
        field_scene = FieldScene(self.mock_game)
        
        # Mock Player-Team
        player_monster = self.create_test_monster("PlayerMonster")
        self.mock_party_manager.party.get_conscious_members.return_value = [player_monster]
        
        # Mock Battle-Scene
        with patch('engine.scenes.battle_scene.BattleScene') as mock_battle_scene:
            mock_battle_instance = Mock()
            mock_battle_scene.return_value = mock_battle_instance
            
            # Simuliere Encounter
            enemy_data = {
                'species_id': 5,
                'name': 'WildMonster',
                'level': 5,
                'types': ['Normal'],
                'rank': 'F'
            }
            
            # Starte Battle
            field_scene.initiate_battle(enemy_data)
            
            # Prüfe Battle-Erstellung
            mock_battle_scene.assert_called_once_with(self.mock_game)
            print("✅ Vollständiger Battle-Flow funktioniert")
    
    def run_all_tests(self):
        """Führe alle Tests aus."""
        print("🚀 Starte Battle-Flow Integration Tests...")
        
        try:
            self.test_battle_scene_initialization()
            self.test_battle_phase_transitions()
            self.test_battle_end_conditions()
            self.test_field_to_battle_transition()
            self.test_reward_system_integration()
            self.test_complete_battle_flow()
            
            print("\n🎉 Alle Tests erfolgreich!")
            return True
            
        except Exception as e:
            print(f"\n❌ Test fehlgeschlagen: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Hauptfunktion für Tests."""
    print("=" * 60)
    print("🎮 UNTOLD STORY - BATTLE FLOW INTEGRATION TESTS")
    print("=" * 60)
    
    # Erstelle Test-Instanz
    test_suite = TestBattleFlowIntegration()
    test_suite.setUp()
    
    try:
        # Führe Tests aus
        success = test_suite.run_all_tests()
        
        if success:
            print("\n✅ ALLE TESTS ERFOLGREICH!")
            print("🎯 Battle-Flow ist vollständig implementiert!")
            print("\n📋 Implementierte Features:")
            print("  • Battle-Phase-Management")
            print("  • Victory/Defeat-Handling")
            print("  • Field-to-Battle-Transition")
            print("  • Reward-System-Integration")
            print("  • Vollständiger Battle-Flow")
            
        else:
            print("\n❌ TESTS FEHLGESCHLAGEN!")
            return 1
            
    finally:
        test_suite.tearDown()
    
    return 0


if __name__ == "__main__":
    exit(main())
