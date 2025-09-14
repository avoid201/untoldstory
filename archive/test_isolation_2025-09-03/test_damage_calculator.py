"""
Tests für Damage Calculator Consolidation
Testet Konsistenz zwischen alten und neuen Calculator-Implementierungen
"""

import unittest
import random
from unittest.mock import Mock, patch
from typing import Dict, Any, List

# Import der Calculator
from engine.systems.unified_damage_calculator import (
    UnifiedDamageCalculator, 
    DQMCalculator,  # Deprecated wrapper
    DQMDamageResult,  # Deprecated wrapper
    DQMSkillCalculator,  # Deprecated wrapper
    unified_damage_calculator
)


class TestDamageCalculatorConsolidation(unittest.TestCase):
    """Test-Klasse für Damage Calculator Konsolidierung."""
    
    def setUp(self):
        """Setup für jeden Test."""
        self.unified = UnifiedDamageCalculator()
        self.dqm_legacy = DQMCalculator(rng_seed=42)  # Deterministic für Tests
        
        # Mock Monster-Objekte
        self.mock_attacker = self._create_mock_monster({
            'atk': 100, 'def': 50, 'mag': 80, 'res': 40, 'spd': 75
        }, types=['Feuer'], traits=['Critical Master'])
        
        self.mock_defender = self._create_mock_monster({
            'atk': 80, 'def': 60, 'mag': 70, 'res': 50, 'spd': 65
        }, types=['Wasser'])
        
        self.mock_move_physical = self._create_mock_move(50, 'Feuer', 'phys')
        self.mock_move_magical = self._create_mock_move(60, 'Feuer', 'mag')
    
    def _create_mock_monster(self, stats: Dict[str, int], types: List[str] = None, traits: List[str] = None):
        """Erstelle Mock-Monster für Tests."""
        monster = Mock()
        monster.stats = stats
        monster.types = types or ['Normal']
        monster.traits = traits or []
        monster.level = 50
        monster.max_hp = 100
        return monster
    
    def _create_mock_move(self, power: int, move_type: str, category: str):
        """Erstelle Mock-Move für Tests."""
        move = Mock()
        move.power = power
        move.type = move_type
        move.category = Mock()
        move.category.value = category
        return move
    
    def test_physical_damage_consistency(self):
        """Teste Konsistenz zwischen Unified und Legacy Physical Damage."""
        # Test mit deterministischem Seed
        with patch('random.uniform', return_value=1.0):  # Max damage
            with patch('random.random', return_value=0.01):  # No critical, no miss
                
                # Unified Calculator
                unified_result = self.unified.calculate_physical_damage(
                    self.mock_attacker, self.mock_defender, self.mock_move_physical
                )
                
                # Legacy Calculator
                legacy_result = self.dqm_legacy.calculate_damage(
                    attacker_stats=self.mock_attacker.stats,
                    defender_stats=self.mock_defender.stats,
                    move_power=self.mock_move_physical.power,
                    move_element=self.mock_move_physical.type,
                    is_physical=True,
                    attacker_traits=self.mock_attacker.traits,
                    defender_traits=self.mock_defender.traits
                )
                
                # Vergleiche Ergebnisse
                self.assertEqual(unified_result.damage, legacy_result.damage)
                self.assertEqual(unified_result.is_critical, legacy_result.is_critical)
                self.assertEqual(unified_result.effectiveness, legacy_result.effectiveness)
    
    def test_dqm_trait_modifiers(self):
        """Teste DQM Trait-Modifikatoren."""
        # Test Attack Boost trait
        attacker_with_boost = self._create_mock_monster(
            {'atk': 100, 'def': 50, 'mag': 80, 'res': 40, 'spd': 75},
            types=['Feuer'],
            traits=['Attack Boost']
        )
        
        with patch('random.uniform', return_value=1.0):
            with patch('random.random', return_value=0.01):
                result = self.unified.calculate_physical_damage(
                    attacker_with_boost, self.mock_defender, self.mock_move_physical
                )
                
                # Attack Boost sollte 10% mehr Schaden verursachen
                self.assertGreater(result.damage, 0)
    
    def test_metal_body_trait(self):
        """Teste Metal Body Trait (Metal Slime Defense)."""
        defender_with_metal = self._create_mock_monster(
            {'atk': 80, 'def': 60, 'mag': 70, 'res': 50, 'spd': 65},
            types=['Wasser'],
            traits=['Metal Body']
        )
        
        # Test mit deterministischem Seed um Miss zu vermeiden
        with patch('random.random', return_value=0.01):  # Kein Miss
            result = self.unified.calculate_physical_damage(
                self.mock_attacker, defender_with_metal, self.mock_move_physical
            )
        
        # Metal Body sollte Schaden drastisch reduzieren
        self.assertLessEqual(result.damage, 2)  # Max 1-2 damage
        self.assertEqual(result.effectiveness_text, "Kaum Schaden gegen Metall-Rüstung!")
    
    def test_miss_calculation(self):
        """Teste Miss-Berechnung."""
        # Test mit sehr niedriger Hit-Rate
        with patch('random.random', return_value=0.99):  # Sollte missen
            result = self.unified.calculate_physical_damage(
                self.mock_attacker, self.mock_defender, self.mock_move_physical
            )
            
            # Sollte missen
            self.assertEqual(result.damage, 0)
            self.assertEqual(result.effectiveness_text, "Attacke ging daneben!")
    
    def test_magical_damage_consistency(self):
        """Teste Konsistenz zwischen Unified und Legacy Magical Damage."""
        with patch('random.uniform', return_value=1.0):
            with patch('random.random', return_value=0.01):
                
                # Unified Calculator
                unified_result = self.unified.calculate_magical_damage(
                    self.mock_attacker, self.mock_defender, self.mock_move_magical
                )
                
                # Legacy Calculator
                legacy_result = self.dqm_legacy.calculate_damage(
                    attacker_stats=self.mock_attacker.stats,
                    defender_stats=self.mock_defender.stats,
                    move_power=self.mock_move_magical.power,
                    move_element=self.mock_move_magical.type,
                    is_physical=False,
                    attacker_traits=self.mock_attacker.traits,
                    defender_traits=self.mock_defender.traits
                )
                
                # Vergleiche Ergebnisse
                self.assertEqual(unified_result.damage, legacy_result.damage)
                self.assertEqual(unified_result.is_critical, legacy_result.is_critical)
                self.assertEqual(unified_result.effectiveness, legacy_result.effectiveness)
    
    def test_critical_hit_consistency(self):
        """Teste Critical Hit Berechnung."""
        # Test mit hoher Critical Chance
        with patch('random.random', return_value=0.01):  # Sollte Critical sein
            unified_critical = self.unified.calculate_critical_hit(self.mock_attacker)
            self.assertTrue(unified_critical)
        
        # Test mit niedriger Critical Chance
        with patch('random.random', return_value=0.99):  # Sollte nicht Critical sein
            unified_critical = self.unified.calculate_critical_hit(self.mock_attacker)
            self.assertFalse(unified_critical)
    
    def test_type_effectiveness_consistency(self):
        """Teste Type-Effectiveness Berechnung."""
        # Feuer vs Wasser sollte nicht sehr effektiv sein
        effectiveness = self.unified.apply_type_effectiveness(
            self.mock_move_physical, self.mock_defender
        )
        
        # Da TypeChart nicht verfügbar ist, sollte Fallback 1.0 zurückgeben
        self.assertEqual(effectiveness, 1.0)
    
    def test_turn_order_consistency(self):
        """Teste Turn-Order Berechnung."""
        monsters = [
            {'name': 'Monster1', 'stats': {'spd': 100}},
            {'name': 'Monster2', 'stats': {'spd': 80}},
            {'name': 'Monster3', 'stats': {'spd': 120}}
        ]
        
        # Test mit deterministischem Seed
        with patch('random.randint', return_value=100):
            unified_order = self.unified.calculate_turn_order(monsters)
            legacy_order = self.dqm_legacy.calculate_turn_order(monsters)
            
            # Sollten identische Reihenfolge haben
            self.assertEqual(len(unified_order), len(legacy_order))
            for i, (u_monster, l_monster) in enumerate(zip(unified_order, legacy_order)):
                self.assertEqual(u_monster['name'], l_monster['name'])
    
    def test_exp_reward_consistency(self):
        """Teste EXP-Reward Berechnung."""
        # Test verschiedene Ränge
        test_cases = [
            (50, 'F', False, 1),  # Level 50, Rang F, kein Boss, 1 Party-Mitglied
            (50, 'A', True, 3),   # Level 50, Rang A, Boss, 3 Party-Mitglieder
            (100, 'X', False, 1), # Level 100, Rang X, kein Boss, 1 Party-Mitglied
        ]
        
        for level, rank, is_boss, party_size in test_cases:
            unified_exp = self.unified.calculate_exp_reward(level, rank, is_boss, party_size)
            legacy_exp = self.dqm_legacy.calculate_exp_reward(level, rank, is_boss, party_size)
            
            self.assertEqual(unified_exp, legacy_exp)
            self.assertGreater(unified_exp, 0)  # Sollte immer positiv sein
    
    def test_gold_reward_consistency(self):
        """Teste Gold-Reward Berechnung."""
        # Test mit deterministischem Seed für Varianz
        with patch('random.uniform', return_value=0.0):  # Keine Varianz
            unified_gold = self.unified.calculate_gold_reward(50, 'A', True)
            legacy_gold = self.dqm_legacy.calculate_gold_reward(50, 'A', True)
            
            self.assertEqual(unified_gold, legacy_gold)
            self.assertGreater(unified_gold, 0)
    
    def test_stat_stage_multiplier_consistency(self):
        """Teste Stat-Stage-Multiplier Berechnung."""
        test_stages = [-6, -3, -1, 0, 1, 3, 6]
        
        for stage in test_stages:
            unified_mult = self.unified.calculate_stat_stage_multiplier(stage)
            legacy_mult = self.dqm_legacy.calculate_stat_stage_multiplier(stage)
            
            self.assertEqual(unified_mult, legacy_mult)
            self.assertGreater(unified_mult, 0)
    
    def test_heal_calculation_consistency(self):
        """Teste Heal-Berechnung."""
        caster_stats = {'mag': 100}
        skill_power = 50
        
        unified_heal = self.unified.calculate_heal(caster_stats, skill_power)
        legacy_heal = DQMSkillCalculator.calculate_heal(caster_stats, skill_power)
        
        self.assertEqual(unified_heal, legacy_heal)
        self.assertGreater(unified_heal, 0)
    
    def test_buff_duration_consistency(self):
        """Teste Buff-Duration Berechnung."""
        test_cases = [
            (50, 50),  # Gleiche Level
            (60, 50),  # Caster höher
            (50, 60),  # Target höher
            (100, 50), # Großer Unterschied
        ]
        
        for caster_level, target_level in test_cases:
            unified_duration = self.unified.calculate_buff_duration(caster_level, target_level)
            legacy_duration = DQMSkillCalculator.calculate_buff_duration(caster_level, target_level)
            
            self.assertEqual(unified_duration, legacy_duration)
            self.assertGreaterEqual(unified_duration, 1)
            self.assertLessEqual(unified_duration, 5)
    
    def test_escape_chance_consistency(self):
        """Teste Escape-Chance Berechnung."""
        test_cases = [
            (100, 50, 1),   # Schneller als Gegner
            (50, 100, 1),   # Langsamer als Gegner
            (75, 75, 3),    # Gleiche Speed, mehrere Versuche
        ]
        
        for runner_speed, enemy_speed, attempts in test_cases:
            unified_chance = self.unified.calculate_escape_chance(runner_speed, enemy_speed, attempts)
            legacy_chance = self.dqm_legacy.calculate_escape_chance(
                {'spd': runner_speed}, {'spd': enemy_speed}, attempts
            )
            
            self.assertEqual(unified_chance, legacy_chance)
            self.assertGreaterEqual(unified_chance, 0.0)
            self.assertLessEqual(unified_chance, 1.0)
    
    def test_accuracy_consistency(self):
        """Teste Accuracy-Berechnung."""
        # Test mit deterministischem Seed
        with patch('random.randint', return_value=50):  # 50% Chance
            unified_hit = self.unified.calculate_accuracy(80, 100, 100)
            legacy_hit = self.dqm_legacy.calculate_accuracy(80, {}, {})
            
            # Unified sollte bool zurückgeben, Legacy float
            self.assertIsInstance(unified_hit, bool)
            self.assertIsInstance(legacy_hit, float)
            self.assertGreaterEqual(legacy_hit, 0.0)
            self.assertLessEqual(legacy_hit, 1.0)
    
    def test_deprecated_wrapper_warnings(self):
        """Teste dass deprecated Wrapper Warnungen ausgeben."""
        with patch('engine.systems.unified_damage_calculator.logger') as mock_logger:
            # Erstelle deprecated Calculator
            deprecated_calc = DQMCalculator()
            
            # Prüfe dass Warning geloggt wurde
            mock_logger.warning.assert_called_with(
                "DQMCalculator is DEPRECATED. Use UnifiedDamageCalculator instead."
            )
    
    def test_dqm_damage_result_compatibility(self):
        """Teste DQMDamageResult Backward Compatibility."""
        result = DQMDamageResult(
            damage=50,
            is_critical=True,
            effectiveness=2.0,
            is_miss=False,
            element='Feuer'
        )
        
        # Test dict-like access
        self.assertEqual(result['damage'], 50)
        self.assertEqual(result['is_critical'], True)
        self.assertEqual(result.get('nonexistent', 'default'), 'default')
        
        # Test final_damage property
        self.assertEqual(result.final_damage, 50)
        
        # Test get_message
        message = result.get_message()
        self.assertIn("Kritischer Treffer!", message)
    
    def test_performance_tracking(self):
        """Teste Performance-Tracking des Unified Calculators."""
        # Reset stats
        self.unified.reset_stats()
        
        # Führe einige Berechnungen durch mit deterministischem Seed
        with patch('random.random', return_value=0.01):  # Keine Misses
            with patch('random.uniform', return_value=1.0):  # Max damage
                for _ in range(10):
                    self.unified.calculate_physical_damage(
                        self.mock_attacker, self.mock_defender, self.mock_move_physical
                    )
        
        # Prüfe Stats
        stats = self.unified.get_performance_stats()
        self.assertEqual(stats['total_calculations'], 10)
        self.assertGreater(stats['total_time'], 0)
        self.assertGreater(stats['average_time'], 0)
        self.assertGreater(stats['calculations_per_second'], 0)
    
    def test_fallback_mechanisms(self):
        """Teste Fallback-Mechanismen bei Fehlern."""
        # Test mit ungültigen Objekten
        invalid_attacker = Mock()
        invalid_attacker.stats = {}  # Leere Stats
        invalid_defender = Mock()
        invalid_defender.stats = {}
        invalid_move = Mock()
        invalid_move.power = 0
        
        # Sollte nicht crashen
        result = self.unified.calculate_physical_damage(
            invalid_attacker, invalid_defender, invalid_move
        )
        
        self.assertIsNotNone(result)
        self.assertGreaterEqual(result.damage, 1)  # Mindestens 1 Schaden
    
    def test_singleton_behavior(self):
        """Teste Singleton-Verhalten des Unified Calculators."""
        calc1 = UnifiedDamageCalculator()
        calc2 = UnifiedDamageCalculator()
        
        # Sollten die gleiche Instanz sein
        self.assertIs(calc1, calc2)
        self.assertIs(calc1, unified_damage_calculator)


class TestDamageCalculatorIntegration(unittest.TestCase):
    """Integration-Tests für Damage Calculator."""
    
    def test_real_world_scenario(self):
        """Teste realistische Battle-Szenario."""
        unified = UnifiedDamageCalculator()
        
        # Erstelle realistische Monster
        attacker = Mock()
        attacker.stats = {'atk': 120, 'def': 80, 'mag': 90, 'res': 70, 'spd': 100}
        attacker.types = ['Feuer']
        attacker.traits = ['Attack Boost']
        attacker.level = 45
        
        defender = Mock()
        defender.stats = {'atk': 100, 'def': 110, 'mag': 80, 'res': 90, 'spd': 85}
        defender.types = ['Wasser']
        defender.traits = ['Defense Boost']
        defender.level = 42
        
        move = Mock()
        move.power = 75
        move.type = 'Feuer'
        move.category = Mock()
        move.category.value = 'phys'
        
        # Führe Damage-Berechnung durch
        result = unified.calculate_physical_damage(attacker, defender, move)
        
        # Prüfe dass Ergebnis sinnvoll ist
        self.assertGreater(result.damage, 0)
        self.assertLess(result.damage, 10000)  # Nicht unrealistisch hoch (DQM kann hohe Werte haben)
        self.assertIsInstance(result.is_critical, bool)
        self.assertGreater(result.effectiveness, 0)
        self.assertIsInstance(result.effectiveness_text, str)
    
    def test_multi_hit_calculation(self):
        """Teste Multi-Hit Damage-Berechnung."""
        unified = UnifiedDamageCalculator()
        
        attacker = Mock()
        attacker.stats = {'atk': 100, 'def': 50, 'mag': 80, 'res': 40, 'spd': 75}
        attacker.types = ['Normal']
        attacker.traits = []
        
        defender = Mock()
        defender.stats = {'atk': 80, 'def': 60, 'mag': 70, 'res': 50, 'spd': 65}
        defender.types = ['Normal']
        defender.traits = []
        
        move = Mock()
        move.power = 25  # Niedrige Power für Multi-Hit
        move.type = 'Normal'
        move.category = Mock()
        move.category.value = 'phys'
        
        # Teste Multi-Hit mit 3 Treffern
        result = unified.calculate_multi_hit(attacker, defender, move, hit_count=3)
        
        self.assertEqual(result.hit_count, 3)
        self.assertEqual(len(result.individual_damages), 3)
        self.assertGreater(result.damage, 0)
        self.assertEqual(result.damage, sum(result.individual_damages))


if __name__ == '__main__':
    # Führe Tests aus
    unittest.main(verbosity=2)
