"""
Performance Tests für Battle-System
"""

import pytest
import time
import random
from typing import Dict, Any, List

from engine.systems.battle import BattleState, BattleType, BattlePhase
from engine.systems.unified_damage_calculator import unified_damage_calculator
from engine.systems.battle.battle_ai import BattleAI
from engine.systems.battle.status_effects_dqm import StatusEffectManager
from engine.systems.battle.monster_traits import TraitManager
from engine.systems.monster_instance import MonsterInstance, StatusCondition
from engine.systems.moves import Move, MoveCategory, MoveTarget, EffectKind
from .test_monsters import TestMonsters
from .conftest import (
    basic_battle, balanced_battle, large_battle, 
    performance_timer
)


class TestBattlePerformance:
    """Performance Tests für Battle-System."""
    
    def test_battle_initialization_speed(self, performance_timer):
        """Battle-Initialisierung < 100ms."""
        performance_timer.start()
        
        # Erstelle mehrere Battles
        for _ in range(10):
            battle = BattleState(
                player_team=TestMonsters.create_balanced_team(),
                enemy_team=TestMonsters.create_balanced_team(),
                battle_type=BattleType.TRAINER,
                enable_3v3=True
            )
        
        performance_timer.stop()
        
        # 10 Battle-Initialisierungen sollten unter 100ms dauern
        performance_timer.assert_faster_than(0.1, "Battle-Initialisierung")
    
    def test_turn_resolution_speed(self, large_battle, performance_timer):
        """Turn Resolution < 50ms."""
        battle = large_battle
        
        # Queue Actions für alle aktive Monster
        for monster in battle.player_formation.get_active_monsters():
            battle.queue_player_action({
                'action': 'attack',
                'move': monster.moves[0],
                'target': battle.enemy_formation.get_active_monsters()[0]
            })
        
        for monster in battle.enemy_formation.get_active_monsters():
            battle.queue_enemy_action({
                'action': 'attack',
                'move': monster.moves[0],
                'target': battle.player_formation.get_active_monsters()[0]
            })
        
        performance_timer.start()
        result = battle.resolve_turn()
        performance_timer.stop()
        
        # Turn Resolution sollte unter 50ms dauern
        performance_timer.assert_faster_than(0.05, "Turn Resolution")
    
    def test_ai_decision_speed(self, large_battle, performance_timer):
        """AI Decision < 20ms."""
        battle = large_battle
        
        performance_timer.start()
        
        # AI sollte schnell entscheiden
        for _ in range(10):
            battle.get_ai_action()
        
        performance_timer.stop()
        
        # 10 AI-Entscheidungen sollten unter 20ms dauern
        performance_timer.assert_faster_than(0.02, "AI Decision")
    
    def test_battle_state_validation_speed(self, large_battle, performance_timer):
        """Battle State Validation < 10ms."""
        battle = large_battle
        
        performance_timer.start()
        
        # Validierung sollte schnell sein
        for _ in range(100):
            battle.validate_battle_state()
        
        performance_timer.stop()
        
        # 100 Validierungen sollten unter 10ms dauern
        performance_timer.assert_faster_than(0.01, "Battle State Validation")
    
    def test_formation_management_speed(self, balanced_battle, performance_timer):
        """Formation Management < 15ms."""
        battle = balanced_battle
        
        performance_timer.start()
        
        # Formation-Operationen sollten schnell sein
        for _ in range(50):
            battle.player_formation.get_active_monsters()
            battle.player_formation.switch_monster(0, 1)
            battle.player_formation.get_monster_position(0)
        
        performance_timer.stop()
        
        # 50 Formation-Operationen sollten unter 15ms dauern
        performance_timer.assert_faster_than(0.015, "Formation Management")
    
    def test_targeting_system_speed(self, balanced_battle, performance_timer):
        """Targeting System < 10ms."""
        battle = balanced_battle
        
        performance_timer.start()
        
        # Targeting sollte schnell sein
        for _ in range(100):
            battle.targeting_system.get_valid_targets("enemy")
            battle.targeting_system.get_valid_targets("ally")
            battle.targeting_system.validate_target(battle.player_active, battle.enemy_active)
        
        performance_timer.stop()
        
        # 100 Targeting-Operationen sollten unter 10ms dauern
        performance_timer.assert_faster_than(0.01, "Targeting System")


class TestDamageCalculationPerformance:
    """Performance Tests für Damage-Berechnung."""
    
    def test_single_damage_calculation_speed(self, performance_timer):
        """Einzelne Damage-Berechnung < 1ms."""
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
        
        # Einzelne Berechnung sollte sehr schnell sein
        for _ in range(1000):
            unified_damage_calculator.calculate_damage(
                attacker=attacker,
                defender=defender,
                move=move
            )
        
        performance_timer.stop()
        
        # 1000 Berechnungen sollten unter 100ms dauern
        performance_timer.assert_faster_than(0.1, "Einzelne Damage-Berechnung")
    
    def test_bulk_damage_calculation_speed(self, performance_timer):
        """Bulk Damage-Berechnung < 10ms."""
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
    
    def test_critical_hit_calculation_speed(self, performance_timer):
        """Kritische Treffer-Berechnung < 5ms."""
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
        
        # Kritische Treffer sollten schnell berechnet werden
        for _ in range(1000):
            unified_damage_calculator.calculate_damage(
                attacker=attacker,
                defender=defender,
                move=move,
                check_critical=True
            )
        
        performance_timer.stop()
        
        # 1000 kritische Treffer-Berechnungen sollten unter 100ms dauern
        performance_timer.assert_faster_than(0.1, "Kritische Treffer-Berechnung")
    
    def test_type_effectiveness_calculation_speed(self, performance_timer):
        """Typ-Effektivitäts-Berechnung < 5ms."""
        attacker = TestMonsters.create_currywurst_phoenix()
        defender = TestMonsters.create_schachtschreck()
        move = Move(
            name="Feuer-Angriff",
            power=60,
            pp=20,
            category=MoveCategory.MAGICAL,
            target=MoveTarget.ENEMY,
            type="fire"
        )
        
        performance_timer.start()
        
        # Typ-Effektivität sollte schnell berechnet werden
        for _ in range(1000):
            unified_damage_calculator.calculate_type_effectiveness(
                move_type=move.type,
                defender_types=defender.types
            )
        
        performance_timer.stop()
        
        # 1000 Typ-Effektivitäts-Berechnungen sollten unter 100ms dauern
        performance_timer.assert_faster_than(0.1, "Typ-Effektivitäts-Berechnung")


class TestStatusEffectPerformance:
    """Performance Tests für Status-Effekte."""
    
    def test_status_effect_processing_speed(self, large_battle, performance_timer):
        """Status-Effekt-Verarbeitung < 5ms."""
        battle = large_battle
        
        # Erstelle viele Monster mit Status-Effekten
        for monster in battle.player_team + battle.enemy_team:
            monster.status_condition = StatusCondition.POISON
            monster.add_status_effect("burn", duration=3)
            monster.add_status_effect("paralysis", duration=2)
        
        performance_timer.start()
        
        # Verarbeite Status-Effekte für alle Monster
        battle.process_status_effects()
        
        performance_timer.stop()
        
        # Status-Effekt-Verarbeitung sollte unter 5ms dauern
        performance_timer.assert_faster_than(0.005, "Status-Effekt-Verarbeitung")
    
    def test_status_effect_application_speed(self, basic_battle, performance_timer):
        """Status-Effekt-Anwendung < 2ms."""
        battle = basic_battle
        
        # Erstelle Status-Move
        status_move = Move(
            name="Status-Angriff",
            power=0,
            pp=15,
            category=MoveCategory.SUPPORT,
            target=MoveTarget.ENEMY,
            type="poison",
            effects=[MoveEffect(
                kind=EffectKind.STATUS,
                status="poison",
                chance=100.0
            )]
        )
        
        performance_timer.start()
        
        # Status-Effekt sollte schnell angewendet werden
        for _ in range(100):
            battle.apply_status_effect(
                target=battle.enemy_active,
                status="poison",
                duration=3
            )
        
        performance_timer.stop()
        
        # 100 Status-Effekt-Anwendungen sollten unter 20ms dauern
        performance_timer.assert_faster_than(0.02, "Status-Effekt-Anwendung")
    
    def test_status_effect_removal_speed(self, basic_battle, performance_timer):
        """Status-Effekt-Entfernung < 2ms."""
        battle = basic_battle
        
        # Setze mehrere Status-Effekte
        battle.player_active.status_condition = StatusCondition.POISON
        battle.player_active.add_status_effect("burn", duration=3)
        battle.player_active.add_status_effect("paralysis", duration=2)
        
        performance_timer.start()
        
        # Status-Effekte sollten schnell entfernt werden
        for _ in range(100):
            battle.remove_status_effect(battle.player_active, "poison")
            battle.remove_status_effect(battle.player_active, "burn")
            battle.remove_status_effect(battle.player_active, "paralysis")
        
        performance_timer.stop()
        
        # 100 Status-Effekt-Entfernungen sollten unter 20ms dauern
        performance_timer.assert_faster_than(0.02, "Status-Effekt-Entfernung")


class TestTraitPerformance:
    """Performance Tests für Monster-Traits."""
    
    def test_trait_calculation_speed(self, large_battle, performance_timer):
        """Trait-Berechnung < 10ms."""
        battle = large_battle
        
        performance_timer.start()
        
        # Berechne Traits für alle Monster
        for monster in battle.player_team + battle.enemy_team:
            monster.get_effective_stat("atk")
            monster.get_effective_stat("def")
            monster.get_effective_stat("mag")
            monster.get_effective_stat("res")
            monster.get_effective_stat("spd")
            monster.get_active_traits()
        
        performance_timer.stop()
        
        # Trait-Berechnung sollte unter 10ms dauern
        performance_timer.assert_faster_than(0.01, "Trait-Berechnung")
    
    def test_trait_activation_speed(self, basic_battle, performance_timer):
        """Trait-Aktivierung < 5ms."""
        battle = basic_battle
        
        performance_timer.start()
        
        # Trait-Aktivierung sollte schnell sein
        for _ in range(100):
            battle.player_active.activate_traits()
            battle.enemy_active.activate_traits()
        
        performance_timer.stop()
        
        # 100 Trait-Aktivierungen sollten unter 50ms dauern
        performance_timer.assert_faster_than(0.05, "Trait-Aktivierung")
    
    def test_trait_synergy_calculation_speed(self, balanced_battle, performance_timer):
        """Trait-Synergie-Berechnung < 15ms."""
        battle = balanced_battle
        
        performance_timer.start()
        
        # Trait-Synergien sollten schnell berechnet werden
        for _ in range(50):
            battle.calculate_team_trait_synergies()
            battle.calculate_formation_bonuses()
        
        performance_timer.stop()
        
        # 50 Trait-Synergie-Berechnungen sollten unter 75ms dauern
        performance_timer.assert_faster_than(0.075, "Trait-Synergie-Berechnung")


class TestBattleAIPerformance:
    """Performance Tests für Battle AI."""
    
    def test_ai_decision_tree_speed(self, large_battle, performance_timer):
        """AI Decision Tree < 25ms."""
        battle = large_battle
        
        performance_timer.start()
        
        # AI sollte schnell durch den Decision Tree gehen
        for _ in range(20):
            battle.ai_controller.evaluate_battle_state()
            battle.ai_controller.choose_action()
            battle.ai_controller.select_target()
        
        performance_timer.stop()
        
        # 20 AI-Entscheidungen sollten unter 50ms dauern
        performance_timer.assert_faster_than(0.05, "AI Decision Tree")
    
    def test_ai_targeting_speed(self, balanced_battle, performance_timer):
        """AI Targeting < 10ms."""
        battle = balanced_battle
        
        performance_timer.start()
        
        # AI-Targeting sollte schnell sein
        for _ in range(100):
            battle.ai_controller.find_best_target("enemy")
            battle.ai_controller.find_best_target("ally")
            battle.ai_controller.evaluate_target_priority(battle.player_active)
        
        performance_timer.stop()
        
        # 100 AI-Targeting-Operationen sollten unter 100ms dauern
        performance_timer.assert_faster_than(0.1, "AI Targeting")
    
    def test_ai_formation_switching_speed(self, balanced_battle, performance_timer):
        """AI Formation Switching < 20ms."""
        battle = balanced_battle
        
        performance_timer.start()
        
        # AI-Formation-Wechsel sollte schnell sein
        for _ in range(50):
            battle.ai_controller.evaluate_formation()
            battle.ai_controller.choose_formation_switch()
            battle.ai_controller.execute_formation_change()
        
        performance_timer.stop()
        
        # 50 AI-Formation-Operationen sollten unter 100ms dauern
        performance_timer.assert_faster_than(0.1, "AI Formation Switching")


class TestMemoryUsage:
    """Tests für Speicherverbrauch."""
    
    def test_battle_state_memory_usage(self, large_battle):
        """Battle State sollte nicht zu viel Speicher verbrauchen."""
        import sys
        
        # Messe Speicherverbrauch
        initial_memory = sys.getsizeof(large_battle)
        
        # Battle State sollte unter 1MB sein
        assert initial_memory < 1024 * 1024, f"Battle State zu groß: {initial_memory / 1024:.2f}KB"
    
    def test_monster_instance_memory_usage(self):
        """Monster-Instanzen sollten nicht zu viel Speicher verbrauchen."""
        import sys
        
        monster = TestMonsters.create_currywurst_phoenix()
        memory_usage = sys.getsizeof(monster)
        
        # Monster-Instanz sollte unter 10KB sein
        assert memory_usage < 10 * 1024, f"Monster-Instanz zu groß: {memory_usage / 1024:.2f}KB"
    
    def test_move_memory_usage(self):
        """Moves sollten nicht zu viel Speicher verbrauchen."""
        import sys
        
        move = Move(
            name="Test-Angriff",
            power=50,
            pp=20,
            category=MoveCategory.PHYSICAL,
            target=MoveTarget.ENEMY,
            type="normal"
        )
        
        memory_usage = sys.getsizeof(move)
        
        # Move sollte unter 5KB sein
        assert memory_usage < 5 * 1024, f"Move zu groß: {memory_usage / 1024:.2f}KB"


class TestScalability:
    """Tests für Skalierbarkeit."""
    
    def test_large_team_performance(self, performance_timer):
        """Performance mit großen Teams."""
        # Erstelle sehr große Teams
        large_player_team = [TestMonsters.create_currywurst_phoenix() for _ in range(20)]
        large_enemy_team = [TestMonsters.create_schachtschreck() for _ in range(20)]
        
        performance_timer.start()
        
        # Battle sollte auch mit großen Teams schnell initialisiert werden
        battle = BattleState(
            player_team=large_player_team,
            enemy_team=large_enemy_team,
            battle_type=BattleType.TRAINER,
            enable_3v3=True
        )
        
        performance_timer.stop()
        
        # Initialisierung sollte unter 200ms dauern
        performance_timer.assert_faster_than(0.2, "Große Team-Initialisierung")
    
    def test_many_status_effects_performance(self, basic_battle, performance_timer):
        """Performance mit vielen Status-Effekten."""
        battle = basic_battle
        
        # Füge viele Status-Effekte hinzu
        for i in range(10):
            battle.player_active.add_status_effect(f"status_{i}", duration=5)
        
        performance_timer.start()
        
        # Status-Effekt-Verarbeitung sollte schnell bleiben
        for _ in range(10):
            battle.process_status_effects()
        
        performance_timer.stop()
        
        # 10 Verarbeitungen sollten unter 50ms dauern
        performance_timer.assert_faster_than(0.05, "Viele Status-Effekte")
    
    def test_complex_trait_combinations_performance(self, basic_battle, performance_timer):
        """Performance mit komplexen Trait-Kombinationen."""
        battle = basic_battle
        
        # Füge komplexe Traits hinzu
        for i in range(5):
            battle.player_active.add_trait(f"complex_trait_{i}", {
                "stat_modifiers": {"atk": i * 10, "def": i * 5},
                "conditional_effects": [f"effect_{i}"],
                "synergies": [f"synergy_{i}"]
            })
        
        performance_timer.start()
        
        # Trait-Berechnung sollte schnell bleiben
        for _ in range(10):
            battle.player_active.calculate_all_trait_effects()
        
        performance_timer.stop()
        
        # 10 Berechnungen sollten unter 30ms dauern
        performance_timer.assert_faster_than(0.03, "Komplexe Trait-Kombinationen")
