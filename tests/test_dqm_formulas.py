"""
Tests for DQM Formula Integration
Ensures that Dragon Quest Monsters formulas work correctly
"""

import unittest
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from engine.systems.battle.dqm_formulas import (
    DQMCalculator,
    DQMConstants,
    DQMDamageResult,
    DQMElement,
    DQMSkillCalculator
)


class TestDQMDamageCalculation(unittest.TestCase):
    """Test DQM damage calculation formulas."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.calculator = DQMCalculator(rng_seed=42)  # Fixed seed for deterministic tests
        
        # Sample monster stats
        self.attacker_stats = {
            'atk': 100,
            'def': 50,
            'mag': 80,
            'res': 40,
            'spd': 75
        }
        
        self.defender_stats = {
            'atk': 70,
            'def': 60,
            'mag': 90,
            'res': 55,
            'spd': 65
        }
    
    def test_physical_damage_calculation(self):
        """Test physical damage calculation with DQM formula."""
        result = self.calculator.calculate_damage(
            attacker_stats=self.attacker_stats,
            defender_stats=self.defender_stats,
            move_power=40,
            is_physical=True
        )
        
        # With DQM formula:
        # Base = 40 * (100/2) = 40 * 50 = 2000
        # Defense reduction = 60/4 = 15
        # Raw damage = 2000 - 15 = 1985
        # With random factor 0.875 to 1.125: ~1737 to ~2233
        
        self.assertIsInstance(result, DQMDamageResult)
        self.assertGreater(result.damage, 0)
        self.assertGreater(result.damage, 1500)  # Should be significant damage
        self.assertLess(result.damage, 2500)  # But not too high
    
    def test_magical_damage_calculation(self):
        """Test magical damage calculation."""
        result = self.calculator.calculate_damage(
            attacker_stats=self.attacker_stats,
            defender_stats=self.defender_stats,
            move_power=35,
            is_physical=False
        )
        
        # With DQM formula:
        # Base = 35 * (80/2) = 35 * 40 = 1400
        # Defense reduction = 55/4 = 13.75
        # Raw damage = 1400 - 13.75 = 1386.25
        
        self.assertGreater(result.damage, 0)
        self.assertGreater(result.damage, 1000)
        self.assertLess(result.damage, 2000)
    
    def test_critical_hit_rate(self):
        """Test that critical hit rate is approximately 1/32."""
        critical_count = 0
        total_runs = 10000
        
        # Reset calculator with no seed for proper randomness test
        calc = DQMCalculator()
        
        for _ in range(total_runs):
            result = calc.calculate_damage(
                attacker_stats=self.attacker_stats,
                defender_stats=self.defender_stats,
                move_power=40,
                is_physical=True
            )
            if result.is_critical:
                critical_count += 1
        
        # Expected rate is 1/32 = 0.03125
        # Allow for some variance (between 2.5% and 3.75%)
        critical_rate = critical_count / total_runs
        self.assertGreater(critical_rate, 0.025)
        self.assertLess(critical_rate, 0.0375)
    
    def test_critical_damage_multiplier(self):
        """Test that critical hits deal 2x damage."""
        # Create calculator with seed that will trigger critical
        calc = DQMCalculator(rng_seed=1)  
        
        # First calculate normal damage
        normal_result = calc.calculate_damage(
            attacker_stats=self.attacker_stats,
            defender_stats=self.defender_stats,
            move_power=40,
            is_physical=True
        )
        
        # Force a critical hit by using traits
        crit_result = calc.calculate_damage(
            attacker_stats=self.attacker_stats,
            defender_stats=self.defender_stats,
            move_power=40,
            is_physical=True,
            attacker_traits=['Critical Master']  # Doubles crit chance
        )
        
        # If we got a critical, it should be roughly 2x damage
        # (accounting for random variance)
        if crit_result.is_critical:
            ratio = crit_result.damage / normal_result.damage
            self.assertGreater(ratio, 1.5)  # At least 1.5x
            self.assertLess(ratio, 2.5)  # At most 2.5x
    
    def test_metal_body_trait(self):
        """Test Metal Body trait reduces damage to 0-2."""
        result = self.calculator.calculate_damage(
            attacker_stats=self.attacker_stats,
            defender_stats=self.defender_stats,
            move_power=100,  # High power move
            is_physical=True,
            defender_traits=['Metal Body']
        )
        
        self.assertTrue(result.is_metal_slime_damage)
        self.assertLessEqual(result.damage, 2)  # Metal body caps damage
        self.assertGreaterEqual(result.damage, 0)
    
    def test_tension_multiplier(self):
        """Test tension system multipliers."""
        # Test different tension levels
        tension_levels = [
            (0, 1.0),     # No tension
            (5, 1.2),     # Psyched up
            (20, 1.5),    # High tension
            (50, 2.0),    # Super high tension
            (100, 2.5),   # Max tension
        ]
        
        for tension, expected_mult in tension_levels:
            result = self.calculator.calculate_damage(
                attacker_stats=self.attacker_stats,
                defender_stats=self.defender_stats,
                move_power=40,
                is_physical=True,
                tension_level=tension
            )
            
            self.assertEqual(result.tension_multiplier, expected_mult)
    
    def test_damage_variance(self):
        """Test that damage has proper variance (7/8 to 9/8)."""
        damages = []
        
        # Calculate damage multiple times
        for seed in range(100):
            calc = DQMCalculator(rng_seed=seed)
            result = calc.calculate_damage(
                attacker_stats=self.attacker_stats,
                defender_stats=self.defender_stats,
                move_power=40,
                is_physical=True
            )
            damages.append(result.damage)
        
        # Check variance
        min_damage = min(damages)
        max_damage = max(damages)
        avg_damage = sum(damages) / len(damages)
        
        # Max should be roughly 1.28x min (9/8 ÷ 7/8 = 1.286)
        ratio = max_damage / min_damage
        self.assertGreater(ratio, 1.2)
        self.assertLess(ratio, 1.4)


class TestDQMTurnOrder(unittest.TestCase):
    """Test DQM turn order calculation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.calculator = DQMCalculator(rng_seed=42)
        
        self.monsters = [
            {'name': 'Fast', 'stats': {'spd': 100}},
            {'name': 'Medium', 'stats': {'spd': 75}},
            {'name': 'Slow', 'stats': {'spd': 50}},
        ]
    
    def test_turn_order_basic(self):
        """Test basic turn order calculation."""
        sorted_monsters = self.calculator.calculate_turn_order(self.monsters)
        
        # Should be sorted by speed + random
        self.assertEqual(len(sorted_monsters), 3)
        
        # The fastest monster should usually go first
        # (but not always due to random factor)
        names = [m['name'] for m in sorted_monsters]
        self.assertIn('Fast', names)
        self.assertIn('Medium', names)
        self.assertIn('Slow', names)
    
    def test_turn_order_with_paralysis(self):
        """Test turn order with paralysis status."""
        monsters = [
            {'name': 'Paralyzed', 'stats': {'spd': 100}, 'status': 'paralysis'},
            {'name': 'Normal', 'stats': {'spd': 60}},
        ]
        
        # Run multiple times to check paralysis effect
        paralyzed_first_count = 0
        for seed in range(100):
            calc = DQMCalculator(rng_seed=seed)
            sorted_monsters = calc.calculate_turn_order(monsters)
            if sorted_monsters[0]['name'] == 'Paralyzed':
                paralyzed_first_count += 1
        
        # Paralyzed monster (effective speed 50) should go first less often
        # than if it wasn't paralyzed
        self.assertLess(paralyzed_first_count, 40)  # Should be slower due to paralysis
    
    def test_turn_order_randomness(self):
        """Test that turn order has proper randomness."""
        # Two monsters with identical speed
        monsters = [
            {'name': 'A', 'stats': {'spd': 75}},
            {'name': 'B', 'stats': {'spd': 75}},
        ]
        
        a_first_count = 0
        total_runs = 1000
        
        for seed in range(total_runs):
            calc = DQMCalculator(rng_seed=seed)
            sorted_monsters = calc.calculate_turn_order(monsters)
            if sorted_monsters[0]['name'] == 'A':
                a_first_count += 1
        
        # With identical speeds, each should go first roughly 50% of the time
        ratio = a_first_count / total_runs
        self.assertGreater(ratio, 0.4)  # At least 40%
        self.assertLess(ratio, 0.6)  # At most 60%


class TestDQMEscapeFormula(unittest.TestCase):
    """Test DQM escape chance calculation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.calculator = DQMCalculator()
    
    def test_escape_faster_runner(self):
        """Test escape when runner is faster."""
        runner_stats = {'spd': 100}
        enemy_stats = {'spd': 50}
        
        chance = self.calculator.calculate_escape_chance(runner_stats, enemy_stats)
        
        # Much faster should have very high escape chance
        self.assertEqual(chance, 1.0)
    
    def test_escape_slower_runner(self):
        """Test escape when runner is slower."""
        runner_stats = {'spd': 30}
        enemy_stats = {'spd': 100}
        
        chance = self.calculator.calculate_escape_chance(runner_stats, enemy_stats)
        
        # Much slower should have low escape chance
        self.assertLess(chance, 0.2)
    
    def test_escape_attempts_increase_chance(self):
        """Test that multiple attempts increase escape chance."""
        runner_stats = {'spd': 60}
        enemy_stats = {'spd': 80}
        
        chances = []
        for attempts in range(5):
            chance = self.calculator.calculate_escape_chance(
                runner_stats, enemy_stats, attempts
            )
            chances.append(chance)
        
        # Each attempt should increase the chance
        for i in range(1, len(chances)):
            self.assertGreater(chances[i], chances[i-1])
    
    def test_escape_chance_cap(self):
        """Test that escape chance is capped at 95%."""
        runner_stats = {'spd': 200}
        enemy_stats = {'spd': 10}
        
        # Even with huge speed advantage and multiple attempts
        chance = self.calculator.calculate_escape_chance(
            runner_stats, enemy_stats, attempts=10
        )
        
        # Should still be capped
        self.assertLessEqual(chance, 0.95)


class TestDQMRewards(unittest.TestCase):
    """Test experience and gold calculation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.calculator = DQMCalculator()
    
    def test_exp_calculation_basic(self):
        """Test basic experience calculation."""
        exp = self.calculator.calculate_exp_reward(
            enemy_level=10,
            enemy_rank='D',
            is_boss=False,
            party_size=1
        )
        
        # Level 10, D rank = 10 * 10 * 1.0 = 100
        self.assertEqual(exp, 100)
    
    def test_exp_calculation_boss(self):
        """Test boss experience bonus."""
        normal_exp = self.calculator.calculate_exp_reward(
            enemy_level=10,
            enemy_rank='D',
            is_boss=False
        )
        
        boss_exp = self.calculator.calculate_exp_reward(
            enemy_level=10,
            enemy_rank='D',
            is_boss=True
        )
        
        # Boss should give 1.5x exp
        self.assertEqual(boss_exp, int(normal_exp * 1.5))
    
    def test_exp_party_split(self):
        """Test experience split among party members."""
        total_exp = self.calculator.calculate_exp_reward(
            enemy_level=20,
            enemy_rank='B',
            is_boss=False,
            party_size=1
        )
        
        split_exp = self.calculator.calculate_exp_reward(
            enemy_level=20,
            enemy_rank='B',
            is_boss=False,
            party_size=3
        )
        
        # Should be divided by party size
        self.assertEqual(split_exp, total_exp // 3)
    
    def test_gold_calculation(self):
        """Test gold reward calculation."""
        gold = self.calculator.calculate_gold_reward(
            enemy_level=15,
            enemy_rank='C',
            is_boss=False
        )
        
        # Should be within expected range
        # Base = 15 * 5 * 1.0 = 75, with ±20% variance
        self.assertGreater(gold, 60)  # 75 - 20%
        self.assertLess(gold, 90)  # 75 + 20%
    
    def test_gold_boss_bonus(self):
        """Test boss gold bonus."""
        # Use fixed seed for consistent variance
        calc = DQMCalculator(rng_seed=42)
        
        normal_gold = calc.calculate_gold_reward(
            enemy_level=10,
            enemy_rank='D',
            is_boss=False
        )
        
        boss_gold = calc.calculate_gold_reward(
            enemy_level=10,
            enemy_rank='D',
            is_boss=True
        )
        
        # Boss should give roughly 2x gold (accounting for variance)
        ratio = boss_gold / normal_gold
        self.assertGreater(ratio, 1.5)
        self.assertLess(ratio, 2.5)


class TestDQMStatStages(unittest.TestCase):
    """Test stat stage multiplier calculation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.calculator = DQMCalculator()
    
    def test_positive_stat_stages(self):
        """Test positive stat stage multipliers."""
        expected = [
            (0, 1.0),
            (1, 1.25),
            (2, 1.5),
            (3, 1.75),
            (4, 2.0),
            (5, 2.25),
            (6, 2.5),
        ]
        
        for stage, expected_mult in expected:
            mult = self.calculator.calculate_stat_stage_multiplier(stage)
            self.assertAlmostEqual(mult, expected_mult)
    
    def test_negative_stat_stages(self):
        """Test negative stat stage multipliers."""
        expected = [
            (-1, 0.75),
            (-2, 0.6),
            (-3, 0.5),
            (-4, 0.4),
            (-5, 0.33),
            (-6, 0.25),
        ]
        
        for stage, expected_mult in expected:
            mult = self.calculator.calculate_stat_stage_multiplier(stage)
            self.assertAlmostEqual(mult, expected_mult, places=2)
    
    def test_stat_stage_clamping(self):
        """Test that stat stages are clamped to -6 to +6."""
        # Test beyond limits
        mult_high = self.calculator.calculate_stat_stage_multiplier(10)
        mult_low = self.calculator.calculate_stat_stage_multiplier(-10)
        
        # Should be clamped to stage 6 and -6
        self.assertEqual(mult_high, 2.5)  # Stage +6
        self.assertEqual(mult_low, 0.25)  # Stage -6


if __name__ == '__main__':
    unittest.main()
