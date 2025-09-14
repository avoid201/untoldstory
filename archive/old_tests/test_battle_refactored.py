"""
Battle System Test Suite
========================
Testet das bereinigte Battle System.
"""

import unittest
import sys
sys.path.insert(0, "/Users/leon/Desktop/untold_story")

from engine.systems.battle import (
    UnifiedBattleManager,
    BattleAction,
    ActionType,
    damage_calculator,
    battle_action_executor
)
from engine.systems.monster_instance import MonsterInstance
from engine.systems.moves import Move


class TestBattleSystemIntegration(unittest.TestCase):
    """Testet die Integration des bereinigten Battle Systems."""
    
    def setUp(self):
        """Setup für jeden Test."""
        self.battle_manager = UnifiedBattleManager(None)
        
        # Create test monsters
        self.player_monster = self._create_test_monster("Testmon", level=10)
        self.enemy_monster = self._create_test_monster("Gegnermon", level=8)
        
        # Create test move
        self.test_move = Move(
            name="Tackle",
            power=40,
            accuracy=100,
            pp=35,
            type="Normal",
            category="phys",
            priority=0
        )
    
    def _create_test_monster(self, name, level=5):
        """Erstellt ein Test-Monster."""
        monster = MonsterInstance(
            species=type('Species', (), {
                'name': name,
                'types': ('Normal',)
            })(),
            level=level
        )
        monster.name = name
        monster.current_hp = 100
        monster.max_hp = 100
        monster.stats = {
            'atk': 50,
            'def': 40,
            'mag': 45,
            'res': 35,
            'spd': 60
        }
        monster.stat_stages = {}
        monster.is_fainted = False
        return monster
    
    def test_battle_initialization(self):
        """Testet die Battle-Initialisierung."""
        success = self.battle_manager.start_battle(
            [self.player_monster],
            [self.enemy_monster]
        )
        self.assertTrue(success)
        self.assertEqual(self.battle_manager.player_active, self.player_monster)
        self.assertEqual(self.battle_manager.enemy_active, self.enemy_monster)
    
    def test_action_creation(self):
        """Testet die Erstellung von Battle Actions."""
        action = BattleAction(
            actor=self.player_monster,
            action_type=ActionType.ATTACK,
            target=self.enemy_monster,
            move=self.test_move
        )
        
        self.assertTrue(action.is_valid())
        self.assertEqual(action.priority, 0)
    
    def test_damage_calculation(self):
        """Testet die Damage-Berechnung."""
        result = damage_calculator.calculate_damage(
            self.player_monster,
            self.enemy_monster,
            self.test_move
        )
        
        self.assertIsNotNone(result)
        self.assertGreater(result.damage, 0)
    
    def test_action_execution(self):
        """Testet die Action-Ausführung."""
        action = BattleAction(
            actor=self.player_monster,
            action_type=ActionType.ATTACK,
            target=self.enemy_monster,
            move=self.test_move
        )
        
        result = battle_action_executor.execute_action(
            action,
            self.battle_manager
        )
        
        self.assertIsNotNone(result)
        self.assertEqual(result['type'], 'attack')
    
    def test_no_duplicate_imports(self):
        """Testet, dass keine doppelten Importe existieren."""
        # Try importing from old locations - should still work via wrappers
        try:
            from engine.systems.battle.battle_actions import BattleAction as BA
            from engine.systems.battle.unified_battle_actions import BattleAction as UBA
            # Both should be the same class
            self.assertEqual(BA, UBA)
        except ImportError:
            pass  # Expected if old modules are removed


if __name__ == '__main__':
    unittest.main()
