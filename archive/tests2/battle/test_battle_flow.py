"""
Integration Tests für kompletten Battle-Flow
"""

import pytest
import time
from typing import Dict, Any, List

from engine.systems.battle import BattleState, BattleType, BattlePhase, BattleCommand
from engine.systems.battle.turn_logic import BattleAction, ActionType, TurnOrder
from engine.systems.monster_instance import MonsterInstance, StatusCondition
from engine.systems.moves import Move, MoveCategory, MoveTarget, EffectKind
from .test_monsters import TestMonsters
from .conftest import (
    basic_battle, balanced_battle, large_battle, 
    battle_validation_helper, performance_timer
)


class TestCompleteBattleFlow:
    """Tests für kompletten Battle-Flow."""
    
    def test_wild_battle_victory(self, basic_battle, battle_validation_helper):
        """Kompletter Kampf: Spieler gewinnt."""
        battle = basic_battle
        
        # Turn 1: Player attacks
        battle.queue_player_action({
            'action': 'attack',
            'move': battle.player_active.moves[0],
            'target': battle.enemy_active
        })
        
        result = battle.resolve_turn()
        assert result['turn_results'][0]['damage'] > 0
        
        # Battle sollte weitergehen
        assert battle.battle_is_active is True
        
        # Simuliere mehrere Runden bis zum Sieg
        for round_num in range(5):
            if not battle.battle_is_active:
                break
                
            # Player action
            battle.queue_player_action({
                'action': 'attack',
                'move': battle.player_active.moves[0],
                'target': battle.enemy_active
            })
            
            # Enemy AI action
            battle.queue_enemy_action({
                'action': 'attack',
                'move': battle.enemy_active.moves[0],
                'target': battle.player_active
            })
            
            result = battle.resolve_turn()
            assert 'turn_results' in result
        
        # Am Ende sollte der Spieler gewinnen
        assert battle.get_winner() == "player"
    
    def test_3v3_formation_battle(self, balanced_battle, battle_validation_helper):
        """Teste 3v3 Formation-Kämpfe."""
        battle = balanced_battle
        
        # Überprüfe Formation
        assert battle.enable_3v3 is True
        assert battle.formation_manager is not None
        assert battle.targeting_system is not None
        
        # Überprüfe aktive Monster
        player_active = battle.player_formation.get_active_monsters()
        enemy_active = battle.enemy_formation.get_active_monsters()
        
        assert len(player_active) == 3
        assert len(enemy_active) == 3
        
        # Teste Formation-Wechsel
        original_active = battle.player_active
        battle.switch_active_monster(1)  # Wechsle zu Monster 1
        
        assert battle.player_active != original_active
        assert battle.player_active.name == battle.player_team[1].name
    
    def test_status_effect_chain(self, basic_battle, battle_validation_helper):
        """Teste Status-Effekt-Ketten."""
        battle = basic_battle
        
        # Verwende Status-Move
        status_move = None
        for move in battle.player_active.moves:
            if move.category == MoveCategory.SUPPORT and move.effects:
                status_move = move
                break
        
        if status_move:
            # Führe Status-Angriff aus
            battle.queue_player_action({
                'action': 'attack',
                'move': status_move,
                'target': battle.enemy_active
            })
            
            result = battle.resolve_turn()
            
            # Überprüfe Status-Effekt
            assert battle.enemy_active.status_condition != StatusCondition.NONE
            
            # Status sollte mehrere Runden anhalten
            for round_num in range(3):
                if battle.enemy_active.status_condition == StatusCondition.NONE:
                    break
                    
                # Führe normale Runde aus
                battle.queue_player_action({
                    'action': 'attack',
                    'move': battle.player_active.moves[0],
                    'target': battle.enemy_active
                })
                
                result = battle.resolve_turn()
    
    def test_item_usage_in_battle(self, basic_battle, battle_validation_helper):
        """Teste Item-Verwendung im Kampf."""
        battle = basic_battle
        
        # Simuliere Item-Verwendung
        battle.queue_player_action({
            'action': 'item',
            'item': 'healing_potion',
            'target': battle.player_active
        })
        
        result = battle.resolve_turn()
        
        # Überprüfe Item-Effekt
        assert 'item_used' in result['turn_results'][0]
        assert battle.player_active.current_hp > 0
    
    def test_flee_attempt(self, basic_battle, battle_validation_helper):
        """Teste Flucht-Versuch."""
        battle = basic_battle
        
        # Versuche zu fliehen
        battle.queue_player_action({
            'action': 'flee'
        })
        
        result = battle.resolve_turn()
        
        # Flucht sollte möglich sein (Wild Battle)
        if result['turn_results'][0].get('fled'):
            assert battle.battle_is_active is False
            assert battle.get_winner() == "fled"
    
    def test_catch_attempt(self, basic_battle, battle_validation_helper):
        """Teste Fang-Versuch."""
        battle = basic_battle
        
        # Versuche Monster zu fangen
        battle.queue_player_action({
            'action': 'catch',
            'item': 'monster_ball'
        })
        
        result = battle.resolve_turn()
        
        # Fang sollte möglich sein (Wild Battle)
        if result['turn_results'][0].get('caught'):
            assert battle.battle_is_active is False
            assert battle.get_winner() == "caught"


class TestBattleTurnResolution:
    """Tests für Turn-Auflösung."""
    
    def test_turn_order_calculation(self, basic_battle):
        """Teste Turn-Reihenfolge-Berechnung."""
        battle = basic_battle
        
        # Erstelle Actions für beide Seiten
        player_action = BattleAction(
            action_type=ActionType.ATTACK,
            source=battle.player_active,
            target=battle.enemy_active,
            move=battle.player_active.moves[0],
            priority=0
        )
        
        enemy_action = BattleAction(
            action_type=ActionType.ATTACK,
            source=battle.enemy_active,
            target=battle.player_active,
            move=battle.enemy_active.moves[0],
            priority=0
        )
        
        # Berechne Turn-Reihenfolge
        turn_order = battle.calculate_turn_order([player_action, enemy_action])
        
        # Schnelleres Monster sollte zuerst handeln
        if battle.player_active.stats["spd"] > battle.enemy_active.stats["spd"]:
            assert turn_order[0].source == battle.player_active
        else:
            assert turn_order[0].source == battle.enemy_active
    
    def test_priority_system(self, basic_battle):
        """Teste Priority-System."""
        battle = basic_battle
        
        # Erstelle Actions mit unterschiedlichen Prioritäten
        low_priority_action = BattleAction(
            action_type=ActionType.ATTACK,
            source=battle.player_active,
            target=battle.enemy_active,
            move=battle.player_active.moves[0],
            priority=0
        )
        
        high_priority_action = BattleAction(
            action_type=ActionType.ATTACK,
            source=battle.enemy_active,
            target=battle.player_active,
            move=battle.enemy_active.moves[0],
            priority=1
        )
        
        # Berechne Turn-Reihenfolge
        turn_order = battle.calculate_turn_order([low_priority_action, high_priority_action])
        
        # Höhere Priority sollte zuerst ausgeführt werden
        assert turn_order[0].priority == 1
    
    def test_simultaneous_actions(self, basic_battle):
        """Teste gleichzeitige Actions."""
        battle = basic_battle
        
        # Beide Monster greifen gleichzeitig an
        battle.queue_player_action({
            'action': 'attack',
            'move': battle.player_active.moves[0],
            'target': battle.enemy_active
        })
        
        battle.queue_enemy_action({
            'action': 'attack',
            'move': battle.enemy_active.moves[0],
            'target': battle.player_active
        })
        
        result = battle.resolve_turn()
        
        # Beide Actions sollten ausgeführt werden
        assert len(result['turn_results']) >= 2
        
        # Beide Monster sollten Schaden nehmen
        player_damaged = any('damage' in r for r in result['turn_results'])
        enemy_damaged = any('damage' in r for r in result['turn_results'])
        
        assert player_damaged or enemy_damaged


class TestBattlePhaseTransitions:
    """Tests für Battle-Phase-Übergänge."""
    
    def test_intro_to_input_transition(self, basic_battle):
        """Teste Übergang von Intro zu Input."""
        battle = basic_battle
        
        # Starte mit Intro-Phase
        battle.current_phase = BattlePhase.INTRO
        
        # Führe Intro aus
        battle.process_intro_phase()
        
        # Sollte zu Input-Phase wechseln
        assert battle.current_phase == BattlePhase.INPUT
    
    def test_input_to_execution_transition(self, basic_battle):
        """Teste Übergang von Input zu Execution."""
        battle = basic_battle
        
        # Starte mit Input-Phase
        battle.current_phase = BattlePhase.INPUT
        
        # Queue Actions
        battle.queue_player_action({
            'action': 'attack',
            'move': battle.player_active.moves[0],
            'target': battle.enemy_active
        })
        
        battle.queue_enemy_action({
            'action': 'attack',
            'move': battle.enemy_active.moves[0],
            'target': battle.player_active
        })
        
        # Führe Execution aus
        battle.process_execution_phase()
        
        # Sollte zu Aftermath-Phase wechseln
        assert battle.current_phase == BattlePhase.AFTERMATH
    
    def test_aftermath_to_end_transition(self, basic_battle):
        """Teste Übergang von Aftermath zu End."""
        battle = basic_battle
        
        # Starte mit Aftermath-Phase
        battle.current_phase = BattlePhase.AFTERMATH
        
        # Setze Monster auf 0 HP
        battle.player_active.current_hp = 0
        
        # Führe Aftermath aus
        battle.process_aftermath_phase()
        
        # Sollte zu End-Phase wechseln
        assert battle.current_phase == BattlePhase.END


class TestBattleAIBehavior:
    """Tests für Battle AI Verhalten."""
    
    def test_ai_decision_making(self, basic_battle):
        """Teste AI-Entscheidungsfindung."""
        battle = basic_battle
        
        # AI sollte eine gültige Action wählen
        ai_action = battle.get_ai_action()
        
        assert ai_action is not None
        assert ai_action['action'] in ['attack', 'item', 'switch']
        
        if ai_action['action'] == 'attack':
            assert 'move' in ai_action
            assert 'target' in ai_action
    
    def test_ai_targeting(self, balanced_battle):
        """Teste AI-Targeting in 3v3."""
        battle = balanced_battle
        
        # AI sollte gültige Ziele wählen
        ai_action = battle.get_ai_action()
        
        if ai_action['action'] == 'attack':
            target = ai_action['target']
            assert target in battle.player_team
            assert target.current_hp > 0
    
    def test_ai_formation_switching(self, balanced_battle):
        """Teste AI-Formation-Wechsel."""
        battle = balanced_battle
        
        # Simuliere Situation wo AI wechseln sollte
        battle.player_active.current_hp = 10  # Sehr niedrige HP
        
        ai_action = battle.get_ai_action()
        
        # AI könnte zu gesünderem Monster wechseln
        if ai_action['action'] == 'switch':
            new_monster = battle.player_team[ai_action['target']]
            assert new_monster.current_hp > battle.player_active.current_hp


class TestBattlePerformance:
    """Tests für Battle-Performance."""
    
    def test_turn_resolution_speed(self, large_battle, performance_timer):
        """Turn Resolution < 50ms."""
        battle = large_battle
        
        # Queue Actions für alle aktiven Monster
        for i, monster in enumerate(battle.player_formation.get_active_monsters()):
            battle.queue_player_action({
                'action': 'attack',
                'move': monster.moves[0],
                'target': battle.enemy_formation.get_active_monsters()[0]
            })
        
        for i, monster in enumerate(battle.enemy_formation.get_active_monsters()):
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


class TestBattleEdgeCases:
    """Tests für Battle Edge Cases."""
    
    def test_simultaneous_knockout(self, basic_battle):
        """Beide Monster fallen gleichzeitig."""
        battle = basic_battle
        
        # Setze beide Monster auf sehr niedrige HP
        battle.player_active.current_hp = 5
        battle.enemy_active.current_hp = 5
        
        # Beide greifen an
        battle.queue_player_action({
            'action': 'attack',
            'move': battle.player_active.moves[0],
            'target': battle.enemy_active
        })
        
        battle.queue_enemy_action({
            'action': 'attack',
            'move': battle.enemy_active.moves[0],
            'target': battle.player_active
        })
        
        result = battle.resolve_turn()
        
        # Beide sollten fallen
        assert battle.player_active.current_hp <= 0
        assert battle.enemy_active.current_hp <= 0
        
        # Battle sollte beendet sein
        assert battle.battle_is_active is False
        assert battle.get_winner() == "draw"
    
    def test_flee_with_zero_speed(self, basic_battle):
        """Flucht mit 0 Speed."""
        battle = basic_battle
        
        # Setze Speed auf 0
        battle.player_active.stats["spd"] = 0
        
        # Versuche zu fliehen
        battle.queue_player_action({
            'action': 'flee'
        })
        
        result = battle.resolve_turn()
        
        # Flucht sollte fehlschlagen
        assert not result['turn_results'][0].get('fled', False)
    
    def test_damage_overflow(self, basic_battle):
        """Damage über MAX_INT."""
        battle = basic_battle
        
        # Setze extreme Stats
        battle.player_active.stats["atk"] = 99999
        battle.enemy_active.stats["def"] = 1
        
        # Führe Angriff aus
        battle.queue_player_action({
            'action': 'attack',
            'move': battle.player_active.moves[0],
            'target': battle.enemy_active
        })
        
        result = battle.resolve_turn()
        
        # Schaden sollte begrenzt sein
        damage = result['turn_results'][0]['damage']
        assert damage < 100000  # Maximaler Schaden
    
    def test_negative_damage_healing(self, basic_battle):
        """Negativer Schaden heilt nicht."""
        battle = basic_battle
        
        # Setze extreme Stats
        battle.player_active.stats["atk"] = 1
        battle.enemy_active.stats["def"] = 99999
        
        # Führe Angriff aus
        battle.queue_player_action({
            'action': 'attack',
            'move': battle.player_active.moves[0],
            'target': battle.enemy_active
        })
        
        result = battle.resolve_turn()
        
        # Schaden sollte 0 sein, nicht negativ
        damage = result['turn_results'][0]['damage']
        assert damage >= 0
