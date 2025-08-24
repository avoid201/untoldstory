"""
Comprehensive Test Suite for Advanced Type System
Tests performance, correctness, and edge cases
"""

import unittest
import time
import json
import numpy as np
from pathlib import Path
from unittest.mock import Mock, patch
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.systems.types import (
    TypeChart, TypeSystemAPI, TypeAttribute, BattleCondition,
    TypeData, TypeRelation, type_chart, type_api
)
from engine.systems.battle.damage_calc import (
    DamageCalculator, DamageCalculationPipeline, DamageModifier,
    CriticalTier, DamageType, SpecialDamageCalculator
)


class TestTypeChart(unittest.TestCase):
    """Test TypeChart functionality and performance."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.chart = TypeChart()
        self.api = TypeSystemAPI()
    
    def test_singleton_pattern(self):
        """Test that TypeChart is a singleton."""
        chart1 = TypeChart()
        chart2 = TypeChart()
        self.assertIs(chart1, chart2)
    
    def test_basic_effectiveness(self):
        """Test basic type effectiveness lookups."""
        # Test super effective
        self.assertEqual(self.chart.get_effectiveness("Feuer", "Pflanze"), 2.0)
        
        # Test not very effective
        self.assertEqual(self.chart.get_effectiveness("Feuer", "Wasser"), 0.5)
        
        # Test neutral
        self.assertEqual(self.chart.get_effectiveness("Feuer", "Mystik"), 1.0)
    
    def test_dual_type_calculation(self):
        """Test effectiveness against dual types."""
        # Feuer vs Pflanze/Wasser (2.0 * 0.5 = 1.0)
        multiplier = self.chart.calculate_type_multiplier("Feuer", ["Pflanze", "Wasser"])
        self.assertAlmostEqual(multiplier, 1.0)
        
        # Wasser vs Feuer/Erde (2.0 * 2.0 = 4.0, capped at 3.0)
        multiplier = self.chart.calculate_type_multiplier("Wasser", ["Feuer", "Erde"])
        self.assertLessEqual(multiplier, 3.0)
    
    def test_inverse_battle_condition(self):
        """Test inverse battle mechanics."""
        # Normal: Feuer > Pflanze (2.0)
        normal = self.chart.get_effectiveness("Feuer", "Pflanze", BattleCondition.NORMAL)
        self.assertEqual(normal, 2.0)
        
        # Inverse: Should be 0.5
        inverse = self.chart.get_effectiveness("Feuer", "Pflanze", BattleCondition.INVERSE)
        self.assertEqual(inverse, 0.5)
    
    def test_performance_requirements(self):
        """Test that lookups meet performance requirements."""
        # Warm up cache
        self.chart.get_effectiveness("Feuer", "Wasser")
        
        # Test lookup speed
        start = time.perf_counter()
        for _ in range(10000):
            self.chart.get_effectiveness("Feuer", "Wasser")
        elapsed = time.perf_counter() - start
        
        avg_time = elapsed / 10000
        self.assertLess(avg_time, 0.001, f"Lookup too slow: {avg_time*1000:.3f}ms")
    
    def test_adaptive_resistance(self):
        """Test adaptive resistance accumulation."""
        # Clear any existing resistances
        self.chart.reset_adaptive_resistances()
        
        # Initial effectiveness
        initial = self.chart.calculate_type_multiplier("Feuer", ["Pflanze"])
        self.assertEqual(initial, 2.0)
        
        # Accumulate resistance
        for _ in range(10):
            self.chart.accumulate_adaptive_resistance("Feuer", "Pflanze")
        
        # Check reduced effectiveness
        adapted = self.chart.get_effectiveness("Feuer", "Pflanze")
        self.assertLess(adapted, initial)
        
        # Reset for other tests
        self.chart.reset_adaptive_resistances()
    
    def test_type_coverage_analysis(self):
        """Test offensive coverage analysis."""
        move_types = ["Feuer", "Wasser", "Erde"]
        coverage = self.chart.get_type_coverage_analysis(move_types)
        
        self.assertIn('super_effective', coverage)
        self.assertIn('coverage_score', coverage)
        self.assertIn('recommendations', coverage)
        
        # Should have good coverage
        self.assertGreater(coverage['coverage_score'], 0.5)
    
    def test_defensive_profile(self):
        """Test defensive profile generation."""
        profile = self.chart.get_defensive_profile(["Feuer", "Pflanze"])
        
        self.assertIn('weaknesses', profile)
        self.assertIn('resistances', profile)
        self.assertIn('defensive_score', profile)
        
        # Fire/Grass should be weak to Luft (Flying)
        self.assertIn("Luft", profile['weaknesses'])
    
    def test_balance_validation(self):
        """Test type balance validation."""
        analysis = self.chart.validate_type_balance()
        
        self.assertIn('balance_score', analysis)
        self.assertIn('overpowered_types', analysis)
        self.assertIn('underpowered_types', analysis)
        
        # Balance score should be reasonable
        self.assertGreater(analysis['balance_score'], 0.5)
    
    def test_synergy_calculation(self):
        """Test type synergy bonuses."""
        # Types with synergy
        synergy_bonus = self.chart._calculate_synergy_bonus(["Feuer", "Erde"])
        self.assertGreaterEqual(synergy_bonus, 1.0)
        
        # Types without special synergy
        no_synergy = self.chart._calculate_synergy_bonus(["Feuer", "Wasser"])
        self.assertEqual(no_synergy, 1.0)
    
    def test_cache_performance(self):
        """Test caching improves performance."""
        # Clear cache
        self.chart.lookup_cache.clear()
        self.chart._cache_hits = 0
        self.chart._cache_misses = 0
        
        # First lookup (cache miss)
        self.chart.get_effectiveness("Feuer", "Wasser")
        self.assertEqual(self.chart._cache_misses, 1)
        
        # Second lookup (cache hit)
        self.chart.get_effectiveness("Feuer", "Wasser")
        self.assertEqual(self.chart._cache_hits, 1)
        
        # Check cache effectiveness
        stats = self.chart.get_performance_stats()
        self.assertGreater(stats['cache_hit_rate'], 0)


class TestDamageCalculator(unittest.TestCase):
    """Test damage calculation system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.chart = TypeChart()
        self.calculator = DamageCalculator(self.chart, seed=42)
        
        # Create mock monsters
        self.create_mock_monsters()
        
        # Create mock move
        self.move = Mock()
        self.move.id = "tackle"
        self.move.power = 100
        self.move.accuracy = 100
        self.move.type = "Feuer"
        self.move.category = "phys"
    
    def create_mock_monsters(self):
        """Create mock monster instances for testing."""
        # Attacker
        self.attacker = Mock()
        self.attacker.level = 50
        self.attacker.stats = {
            'hp': 200, 'atk': 150, 'def': 100,
            'mag': 120, 'res': 100, 'spd': 110
        }
        self.attacker.stat_stages = {
            'atk': 0, 'def': 0, 'mag': 0,
            'res': 0, 'spd': 0, 'acc': 0, 'eva': 0
        }
        self.attacker.species = Mock()
        self.attacker.species.types = ["Feuer"]
        self.attacker.status = None
        
        # Defender
        self.defender = Mock()
        self.defender.level = 50
        self.defender.current_hp = 180
        self.defender.max_hp = 180
        self.defender.stats = {
            'hp': 180, 'atk': 100, 'def': 120,
            'mag': 100, 'res': 110, 'spd': 90
        }
        self.defender.stat_stages = {
            'atk': 0, 'def': 0, 'mag': 0,
            'res': 0, 'spd': 0, 'acc': 0, 'eva': 0
        }
        self.defender.species = Mock()
        self.defender.species.types = ["Pflanze"]
        self.defender.status = None
    
    def test_basic_damage_calculation(self):
        """Test basic damage calculation."""
        result = self.calculator.calculate(self.attacker, self.defender, self.move)
        
        self.assertFalse(result.missed)
        self.assertFalse(result.blocked)
        self.assertGreater(result.damage, 0)
        
        # Should be super effective (Feuer > Pflanze)
        self.assertEqual(result.effectiveness, 2.0)
        self.assertIn("effektiv", result.effectiveness_text.lower())
    
    def test_stab_bonus(self):
        """Test STAB bonus application."""
        # With STAB (Feuer type using Feuer move)
        result_stab = self.calculator.calculate(self.attacker, self.defender, self.move)
        
        # Without STAB
        self.attacker.species.types = ["Wasser"]
        result_no_stab = self.calculator.calculate(self.attacker, self.defender, self.move)
        
        # STAB should increase damage
        self.assertGreater(result_stab.damage, result_no_stab.damage)
        self.assertIn("STAB", result_stab.modifiers_applied)
    
    def test_critical_hit(self):
        """Test critical hit mechanics."""
        # Force critical hit
        self.calculator.pipeline.remove_stage("critical_hit")
        
        def force_crit(context):
            context['result'].critical_tier = CriticalTier.NORMAL
            context['result'].damage = int(context['result'].damage * 1.5)
            context['result'].modifiers_applied.append("Critical NORMAL")
            context['result'].is_critical = True
        
        self.calculator.pipeline.add_stage("critical_hit", force_crit, 2)
        
        result = self.calculator.calculate(self.attacker, self.defender, self.move)
        self.assertEqual(result.critical_tier, CriticalTier.NORMAL)
        self.assertTrue(result.is_critical)
        self.assertIn("Critical", str(result.modifiers_applied))
    
    def test_accuracy_check(self):
        """Test accuracy mechanics."""
        # Low accuracy move
        self.move.accuracy = 30
        
        hits = 0
        for _ in range(100):
            result = self.calculator.calculate(self.attacker, self.defender, self.move)
            if not result.missed:
                hits += 1
        
        # Should hit approximately 30% of the time (with some variance)
        self.assertGreater(hits, 15)
        self.assertLess(hits, 45)
    
    def test_damage_modifiers(self):
        """Test damage modifier system."""
        # Add weather modifier
        weather_mod = DamageModifier(
            name="Sunny Weather",
            multiplier=1.5,
            condition=lambda ctx: ctx['move'].type == "Feuer",
            priority=5
        )
        
        self.calculator.add_global_modifier(weather_mod)
        
        result = self.calculator.calculate(self.attacker, self.defender, self.move)
        self.assertIn("Sunny Weather", result.modifiers_applied)
        
        # Clean up
        self.calculator.remove_global_modifier("Sunny Weather")
    
    def test_multi_hit_calculation(self):
        """Test multi-hit move calculation."""
        result = self.calculator.calculate_multi_hit(
            self.attacker, self.defender, self.move, hit_count=3
        )
        
        self.assertEqual(result.hit_count, 3)
        self.assertEqual(len(result.individual_damages), 3)
        self.assertGreater(result.get_total_damage(), result.individual_damages[0])
    
    def test_damage_preview(self):
        """Test damage preview without RNG."""
        preview = self.calculator.preview_damage(
            self.attacker, self.defender, self.move
        )
        
        self.assertIn('min', preview)
        self.assertIn('max', preview)
        self.assertIn('average', preview)
        
        # Min should be less than max
        self.assertLess(preview['min'], preview['max'])
        
        # Average should be between min and max
        self.assertGreater(preview['average'], preview['min'])
        self.assertLess(preview['average'], preview['max'])
    
    def test_performance_requirements(self):
        """Test that damage calculation meets performance requirements."""
        # Warm up
        self.calculator.calculate(self.attacker, self.defender, self.move)
        
        # Test calculation speed
        start = time.perf_counter()
        for _ in range(1000):
            self.calculator.calculate(self.attacker, self.defender, self.move)
        elapsed = time.perf_counter() - start
        
        avg_time = elapsed / 1000
        self.assertLess(avg_time, 0.01, f"Calculation too slow: {avg_time*1000:.3f}ms")
    
    def test_special_damage_types(self):
        """Test special damage calculation methods."""
        # Fixed damage
        fixed_result = SpecialDamageCalculator.calculate_fixed(50)
        self.assertEqual(fixed_result.damage, 50)
        
        # Percentage damage
        percent_result = SpecialDamageCalculator.calculate_percentage(
            self.defender, 0.25
        )
        self.assertEqual(percent_result.damage, 45)  # 25% of 180 HP
        
        # Level-based damage
        level_result = SpecialDamageCalculator.calculate_level_based(
            self.attacker.level, 1.5
        )
        self.assertEqual(level_result.damage, 75)  # 50 * 1.5


class TestTypeSystemAPI(unittest.TestCase):
    """Test high-level Type System API."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.api = TypeSystemAPI()
    
    def test_effectiveness_check(self):
        """Test type effectiveness checking."""
        result = self.api.check_type_effectiveness(
            "Feuer", ["Pflanze"], ["Feuer"]
        )
        
        self.assertIn('multiplier', result)
        self.assertIn('message', result)
        self.assertIn('color', result)
        self.assertTrue(result['is_super_effective'])
    
    def test_team_composition_analysis(self):
        """Test team composition analysis."""
        team = [
            ["Feuer", "Erde"],
            ["Wasser", "Pflanze"],
            ["Luft", "Energie"]
        ]
        
        analysis = self.api.analyze_team_composition(team)
        
        self.assertIn('offensive_coverage', analysis)
        self.assertIn('defensive_weaknesses', analysis)
        self.assertIn('synergy_score', analysis)
        self.assertIn('balance_score', analysis)
        
        # Should have decent coverage
        self.assertGreater(
            analysis['offensive_coverage']['coverage_score'], 0.5
        )
    
    def test_matchup_prediction(self):
        """Test battle matchup prediction."""
        prediction = self.api.predict_matchup(
            ["Feuer", "Erde"],
            ["Pflanze", "Wasser"]
        )
        
        self.assertIn('advantage', prediction)
        self.assertIn('confidence', prediction)
        self.assertIn('key_factors', prediction)
        
        # Fire/Ground should have mixed matchup against Grass/Water
        self.assertIn(prediction['advantage'], ['attacker', 'defender', 'neutral'])
    
    def test_battle_condition_setting(self):
        """Test setting battle conditions."""
        self.api.set_battle_condition(BattleCondition.INVERSE)
        self.assertEqual(self.api.battle_condition, BattleCondition.INVERSE)
        
        # Check that effectiveness is inverted
        result = self.api.check_type_effectiveness("Feuer", ["Pflanze"])
        self.assertFalse(result['is_super_effective'])
        
        # Reset to normal
        self.api.set_battle_condition(BattleCondition.NORMAL)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system."""
    
    def setUp(self):
        """Set up integrated system."""
        self.chart = TypeChart()
        self.api = TypeSystemAPI()
        self.calculator = DamageCalculator(self.chart)
    
    def test_full_battle_turn(self):
        """Test a complete battle turn calculation."""
        # Create more realistic mocks
        attacker = Mock()
        attacker.level = 75
        attacker.stats = {'atk': 200, 'def': 150, 'mag': 180, 
                         'res': 140, 'spd': 160, 'hp': 250}
        attacker.stat_stages = {'atk': 1, 'def': 0, 'mag': 0,
                               'res': 0, 'spd': 0, 'acc': 0, 'eva': 0}
        attacker.species = Mock(types=["Feuer", "Erde"])
        attacker.status = None
        
        defender = Mock()
        defender.level = 70
        defender.current_hp = 220
        defender.max_hp = 220
        defender.stats = {'atk': 140, 'def': 180, 'mag': 160,
                         'res': 170, 'spd': 140, 'hp': 220}
        defender.stat_stages = {'atk': 0, 'def': -1, 'mag': 0,
                               'res': 0, 'spd': 0, 'acc': 0, 'eva': 0}
        defender.species = Mock(types=["Wasser", "Pflanze"])
        defender.status = None
        
        move = Mock()
        move.id = "earthquake"
        move.power = 120
        move.accuracy = 100
        move.type = "Erde"
        move.category = "phys"
        
        # Calculate damage
        result = self.calculator.calculate(attacker, defender, move)
        
        # Verify reasonable damage
        self.assertGreater(result.damage, 50)
        self.assertLess(result.damage, defender.max_hp)
        
        # Check performance
        self.assertLess(result.calculation_time, 0.01)
    
    def test_memory_usage(self):
        """Test that memory usage stays within limits."""
        import sys
        
        # Get initial size
        initial_size = sys.getsizeof(self.chart)
        
        # Perform many calculations
        for _ in range(1000):
            self.chart.get_effectiveness("Feuer", "Wasser")
            self.chart.calculate_type_multiplier("Feuer", ["Wasser", "Pflanze"])
        
        # Check size hasn't grown too much
        final_size = sys.getsizeof(self.chart)
        growth = final_size - initial_size
        
        # Should stay under 10MB growth
        self.assertLess(growth, 10 * 1024 * 1024)


class TestPerformanceBenchmark(unittest.TestCase):
    """Performance benchmarking tests."""
    
    def setUp(self):
        """Set up for benchmarking."""
        self.chart = TypeChart()
        self.calculator = DamageCalculator(self.chart)
    
    def test_benchmark_type_lookups(self):
        """Benchmark type effectiveness lookups."""
        iterations = 100000
        
        start = time.perf_counter()
        for _ in range(iterations):
            self.chart.get_effectiveness("Feuer", "Wasser")
        elapsed = time.perf_counter() - start
        
        ops_per_second = iterations / elapsed
        print(f"\nType lookups: {ops_per_second:.0f} ops/sec")
        print(f"Average time: {elapsed/iterations*1000000:.2f} μs")
        
        # Should handle at least 100k lookups per second
        self.assertGreater(ops_per_second, 100000)
    
    def test_benchmark_damage_calculation(self):
        """Benchmark full damage calculations."""
        # Create simple mocks
        attacker = Mock()
        attacker.level = 50
        attacker.stats = {'atk': 100, 'def': 100, 'mag': 100,
                         'res': 100, 'spd': 100, 'hp': 100}
        attacker.stat_stages = {'atk': 0, 'def': 0, 'mag': 0,
                               'res': 0, 'spd': 0, 'acc': 0, 'eva': 0}
        attacker.species = Mock(types=["Feuer"])
        attacker.status = None
        
        defender = Mock()
        defender.level = 50
        defender.current_hp = 100
        defender.max_hp = 100
        defender.stats = attacker.stats.copy()
        defender.stat_stages = {'atk': 0, 'def': 0, 'mag': 0,
                               'res': 0, 'spd': 0, 'acc': 0, 'eva': 0}
        defender.species = Mock(types=["Wasser"])
        defender.status = None
        
        move = Mock()
        move.id = "test"
        move.power = 100
        move.accuracy = 100
        move.type = "Feuer"
        move.category = "phys"
        
        iterations = 10000
        
        start = time.perf_counter()
        for _ in range(iterations):
            self.calculator.calculate(attacker, defender, move)
        elapsed = time.perf_counter() - start
        
        ops_per_second = iterations / elapsed
        print(f"\nDamage calculations: {ops_per_second:.0f} ops/sec")
        print(f"Average time: {elapsed/iterations*1000:.3f} ms")
        
        # Should handle at least 1000 calculations per second
        self.assertGreater(ops_per_second, 1000)


def run_tests():
    """Run all tests with detailed output."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestTypeChart))
    suite.addTests(loader.loadTestsFromTestCase(TestDamageCalculator))
    suite.addTests(loader.loadTestsFromTestCase(TestTypeSystemAPI))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestPerformanceBenchmark))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {(result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100:.1f}%")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)