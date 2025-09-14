"""
Tests für Damage-Berechnung und DQM-Formeln
"""

import pytest
import random
from typing import Dict, Any

from engine.systems.unified_damage_calculator import unified_damage_calculator
from engine.systems.battle.dqm_formulas import DQMCalculator, DQMDamageStage
from engine.systems.monster_instance import MonsterInstance
from engine.systems.moves import Move, MoveCategory, MoveTarget, EffectKind
from .test_monsters import TestMonsters
from .conftest import battle_validation_helper


class TestDamageCalculation:
    """Tests für grundlegende Damage-Berechnung."""
    
    def test_physical_damage_formula(self, battle_validation_helper):
        """Teste physische Damage-Berechnung."""
        attacker = TestMonsters.create_currywurst_phoenix()
        defender = TestMonsters.create_schachtschreck()
        move = Move(
            name="Test-Angriff",
            power=60,
            pp=20,
            category=MoveCategory.PHYSICAL,
            target=MoveTarget.ENEMY,
            type="normal"
        )
        
        damage = unified_damage_calculator.calculate_damage(
            attacker=attacker,
            defender=defender,
            move=move
        )
        
        battle_validation_helper.assert_valid_damage(damage)
        assert damage > 0
        
        # Damage sollte proportional zur Power und ATK sein
        expected_min = move.power * attacker.stats["atk"] // 100
        assert damage >= expected_min
    
    def test_magical_damage_formula(self, battle_validation_helper):
        """Teste magische Damage-Berechnung."""
        attacker = TestMonsters.create_currywurst_phoenix()
        defender = TestMonsters.create_schachtschreck()
        move = Move(
            name="Test-Zauber",
            power=80,
            pp=15,
            category=MoveCategory.MAGICAL,
            target=MoveTarget.ENEMY,
            type="fire"
        )
        
        damage = unified_damage_calculator.calculate_damage(
            attacker=attacker,
            defender=defender,
            move=move
        )
        
        battle_validation_helper.assert_valid_damage(damage)
        assert damage > 0
        
        # Magischer Schaden sollte MAG statt ATK verwenden
        expected_min = move.power * attacker.stats["mag"] // 100
        assert damage >= expected_min
    
    def test_critical_hit_calculation(self, mock_rng):
        """Teste kritische Treffer (DQM: 1/32 Chance)."""
        attacker = TestMonsters.create_currywurst_phoenix()
        defender = TestMonsters.create_schachtschreck()
        move = Move(
            name="Test-Angriff",
            power=50,
            pp=20,
            category=MoveCategory.PHYSICAL,
            target=MoveTarget.ENEMY,
            type="normal"
        )
        
        # Teste mehrere Berechnungen für kritische Treffer
        critical_hits = 0
        total_tests = 1000
        
        for _ in range(total_tests):
            damage = unified_damage_calculator.calculate_damage(
                attacker=attacker,
                defender=defender,
                move=move
            )
            
            # Prüfe ob kritischer Treffer (1.5x Schaden)
            if damage > move.power * attacker.stats["atk"] // 100 * 1.3:
                critical_hits += 1
        
        # Kritische Treffer sollten etwa 1/32 = 3.125% sein
        critical_rate = critical_hits / total_tests
        assert 0.02 <= critical_rate <= 0.05  # Toleranz für RNG
    
    def test_type_effectiveness(self, battle_validation_helper):
        """Teste Typ-Effektivität."""
        # Feuer vs. Erde sollte effektiv sein
        fire_attacker = TestMonsters.create_currywurst_phoenix()
        earth_defender = TestMonsters.create_schachtschreck()
        
        fire_move = Move(
            name="Feuer-Angriff",
            power=60,
            pp=20,
            category=MoveCategory.MAGICAL,
            target=MoveTarget.ENEMY,
            type="fire"
        )
        
        normal_move = Move(
            name="Normal-Angriff",
            power=60,
            pp=20,
            category=MoveCategory.PHYSICAL,
            target=MoveTarget.ENEMY,
            type="normal"
        )
        
        fire_damage = unified_damage_calculator.calculate_damage(
            attacker=fire_attacker,
            defender=earth_defender,
            move=fire_move
        )
        
        normal_damage = unified_damage_calculator.calculate_damage(
            attacker=fire_attacker,
            defender=earth_defender,
            move=normal_move
        )
        
        # Feuer sollte effektiver gegen Erde sein
        assert fire_damage > normal_damage
    
    def test_tension_multiplier(self, battle_validation_helper):
        """Teste Tension-System (0-100 Punkte)."""
        attacker = TestMonsters.create_currywurst_phoenix()
        defender = TestMonsters.create_schachtschreck()
        move = Move(
            name="Test-Angriff",
            power=50,
            pp=20,
            category=MoveCategory.PHYSICAL,
            target=MoveTarget.ENEMY,
            type="normal"
        )
        
        # Teste ohne Tension
        base_damage = unified_damage_calculator.calculate_damage(
            attacker=attacker,
            defender=defender,
            move=move
        )
        
        # Teste mit hoher Tension
        attacker.tension = 100
        tension_damage = unified_damage_calculator.calculate_damage(
            attacker=attacker,
            defender=defender,
            move=move
        )
        
        # Tension sollte den Schaden erhöhen
        assert tension_damage > base_damage
        
        # Tension sollte proportional sein (max 2x)
        assert tension_damage <= base_damage * 2.5
    
    def test_level_multiplier(self, battle_validation_helper):
        """Teste Level-Multiplikator."""
        low_level_attacker = TestMonsters.create_schachtschreck()  # Level 5
        high_level_attacker = TestMonsters.create_currywurst_phoenix()  # Level 25
        defender = TestMonsters.create_weak_monster()
        
        move = Move(
            name="Test-Angriff",
            power=50,
            pp=20,
            category=MoveCategory.PHYSICAL,
            target=MoveTarget.ENEMY,
            type="normal"
        )
        
        low_damage = unified_damage_calculator.calculate_damage(
            attacker=low_level_attacker,
            defender=defender,
            move=move
        )
        
        high_damage = unified_damage_calculator.calculate_damage(
            attacker=high_level_attacker,
            defender=defender,
            move=move
        )
        
        # Höhere Level sollten mehr Schaden machen
        assert high_damage > low_damage
    
    def test_defense_reduction(self, battle_validation_helper):
        """Teste Verteidigungs-Reduktion."""
        attacker = TestMonsters.create_currywurst_phoenix()
        high_def_defender = TestMonsters.create_tank_monster()
        low_def_defender = TestMonsters.create_weak_monster()
        
        move = Move(
            name="Test-Angriff",
            power=50,
            pp=20,
            category=MoveCategory.PHYSICAL,
            target=MoveTarget.ENEMY,
            type="normal"
        )
        
        high_def_damage = unified_damage_calculator.calculate_damage(
            attacker=attacker,
            defender=high_def_defender,
            move=move
        )
        
        low_def_damage = unified_damage_calculator.calculate_damage(
            attacker=attacker,
            defender=low_def_defender,
            move=move
        )
        
        # Gegen hohe Verteidigung sollte weniger Schaden gemacht werden
        assert high_def_damage < low_def_damage


class TestDQMDamageStages:
    """Tests für DQM Damage Stages."""
    
    def test_damage_stage_calculation(self):
        """Teste Damage Stage Berechnung."""
        calculator = DQMCalculator()
        
        # Teste verschiedene Stages
        stages = [-6, -3, 0, 3, 6]
        expected_multipliers = [0.25, 0.5, 1.0, 2.0, 4.0]
        
        for stage, expected in zip(stages, expected_multipliers):
            multiplier = calculator.get_damage_stage_multiplier(stage)
            assert abs(multiplier - expected) < 0.01
    
    def test_damage_stage_limits(self):
        """Teste Damage Stage Limits."""
        calculator = DQMCalculator()
        
        # Teste extreme Werte
        assert calculator.get_damage_stage_multiplier(-10) == 0.25  # Min
        assert calculator.get_damage_stage_multiplier(10) == 4.0    # Max
    
    def test_stat_stage_application(self):
        """Teste Anwendung von Stat Stages."""
        calculator = DQMCalculator()
        
        base_stat = 100
        stages = [-2, 0, 2]
        expected_values = [50, 100, 200]
        
        for stage, expected in zip(stages, expected_values):
            modified_stat = calculator.apply_stat_stage(base_stat, stage)
            assert modified_stat == expected


class TestDamageEdgeCases:
    """Tests für Damage-Berechnung Edge Cases."""
    
    def test_zero_power_move(self, battle_validation_helper):
        """Teste Move mit 0 Power."""
        attacker = TestMonsters.create_currywurst_phoenix()
        defender = TestMonsters.create_schachtschreck()
        move = Move(
            name="Null-Angriff",
            power=0,
            pp=20,
            category=MoveCategory.PHYSICAL,
            target=MoveTarget.ENEMY,
            type="normal"
        )
        
        damage = unified_damage_calculator.calculate_damage(
            attacker=attacker,
            defender=defender,
            move=move
        )
        
        # 0 Power sollte 0 Schaden machen
        assert damage == 0
    
    def test_extreme_stat_values(self, battle_validation_helper):
        """Teste extreme Stat-Werte."""
        # Monster mit sehr hohen Stats
        high_stat_monster = TestMonsters.create_monster_with_custom_stats({
            "atk": 999, "def": 999, "hp": 999
        })
        
        # Monster mit sehr niedrigen Stats
        low_stat_monster = TestMonsters.create_monster_with_custom_stats({
            "atk": 1, "def": 1, "hp": 1
        })
        
        move = Move(
            name="Test-Angriff",
            power=50,
            pp=20,
            category=MoveCategory.PHYSICAL,
            target=MoveTarget.ENEMY,
            type="normal"
        )
        
        # Hohe Stats sollten hohen Schaden machen
        high_damage = unified_damage_calculator.calculate_damage(
            attacker=high_stat_monster,
            defender=low_stat_monster,
            move=move
        )
        
        # Niedrige Stats sollten niedrigen Schaden machen
        low_damage = unified_damage_calculator.calculate_damage(
            attacker=low_stat_monster,
            defender=high_stat_monster,
            move=move
        )
        
        assert high_damage > low_damage
        battle_validation_helper.assert_valid_damage(high_damage)
        battle_validation_helper.assert_valid_damage(low_damage)
    
    def test_negative_damage_handling(self, battle_validation_helper):
        """Teste Handling von negativem Schaden."""
        attacker = TestMonsters.create_weak_monster()
        defender = TestMonsters.create_tank_monster()
        move = Move(
            name="Schwacher Angriff",
            power=10,
            pp=20,
            category=MoveCategory.PHYSICAL,
            target=MoveTarget.ENEMY,
            type="normal"
        )
        
        damage = unified_damage_calculator.calculate_damage(
            attacker=attacker,
            defender=defender,
            move=move
        )
        
        # Schaden sollte nie negativ sein
        assert damage >= 0
    
    def test_damage_overflow_protection(self, battle_validation_helper):
        """Teste Schutz vor Damage-Overflow."""
        # Monster mit extrem hohen Stats
        extreme_monster = TestMonsters.create_monster_with_custom_stats({
            "atk": 9999, "def": 1, "hp": 9999
        })
        
        move = Move(
            name="Extremer Angriff",
            power=999,
            pp=20,
            category=MoveCategory.PHYSICAL,
            target=MoveTarget.ENEMY,
            type="normal"
        )
        
        damage = unified_damage_calculator.calculate_damage(
            attacker=extreme_monster,
            defender=TestMonsters.create_weak_monster(),
            move=move
        )
        
        # Schaden sollte begrenzt sein
        assert damage < 10000  # Maximaler Schaden
        battle_validation_helper.assert_valid_damage(damage)


class TestDamageCalculationPerformance:
    """Tests für Damage-Berechnung Performance."""
    
    def test_damage_calculation_speed(self, performance_timer):
        """Teste Geschwindigkeit der Damage-Berechnung."""
        attacker = TestMonsters.create_currywurst_phoenix()
        defender = TestMonsters.create_schachtschreck()
        move = Move(
            name="Test-Angriff",
            power=50,
            pp=20,
            category=MoveCategory.PHYSICAL,
            target=MoveTarget.ENEMY,
            type="normal"
        )
        
        performance_timer.start()
        
        # Führe 1000 Berechnungen durch
        for _ in range(1000):
            unified_damage_calculator.calculate_damage(
                attacker=attacker,
                defender=defender,
                move=move
            )
        
        performance_timer.stop()
        
        # 1000 Berechnungen sollten unter 100ms dauern
        performance_timer.assert_faster_than(0.1, "Damage-Berechnung")
    
    def test_bulk_damage_calculation(self, performance_timer):
        """Teste Bulk Damage-Berechnung für 3v3 Battles."""
        player_team = TestMonsters.create_balanced_team()
        enemy_team = TestMonsters.create_balanced_team()
        
        move = Move(
            name="Flächen-Angriff",
            power=60,
            pp=15,
            category=MoveCategory.MAGICAL,
            target=MoveTarget.ALL_ENEMIES,
            type="fire"
        )
        
        performance_timer.start()
        
        # Berechne Schaden für alle Gegner
        for attacker in player_team:
            for defender in enemy_team:
                unified_damage_calculator.calculate_damage(
                    attacker=attacker,
                    defender=defender,
                    move=move
                )
        
        performance_timer.stop()
        
        # 9 Berechnungen sollten unter 10ms dauern
        performance_timer.assert_faster_than(0.01, "Bulk Damage-Berechnung")
