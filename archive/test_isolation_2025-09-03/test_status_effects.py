"""
Tests für Status-Effekte und Monster-Traits
"""

import pytest
import time
from typing import Dict, Any, List

from engine.systems.battle import BattleState, BattleType, BattlePhase
from engine.systems.monster_instance import MonsterInstance, StatusCondition
from engine.systems.battle.status_effects_dqm import StatusEffectManager
from engine.systems.battle.monster_traits import TraitManager, TraitEffect
from engine.systems.moves import Move, MoveCategory, MoveTarget, EffectKind
from .test_monsters import TestMonsters
from .conftest import (
    basic_battle, status_battle, battle_validation_helper,
    status_effect_factory, performance_timer
)


class TestStatusEffects:
    """Tests für Status-Effekte."""
    
    def test_poison_status_effect(self, basic_battle, battle_validation_helper):
        """Teste Gift-Status-Effekt."""
        battle = basic_battle
        
        # Erstelle Gift-Move
        poison_move = Move(
            name="Gift-Pfeil",
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
        
        # Führe Gift-Angriff aus
        battle.queue_player_action({
            'action': 'attack',
            'move': poison_move,
            'target': battle.enemy_active
        })
        
        result = battle.resolve_turn()
        
        # Gegner sollte vergiftet sein
        assert battle.enemy_active.status_condition == StatusCondition.POISON
        
        # Gift sollte Schaden über Zeit machen
        original_hp = battle.enemy_active.current_hp
        
        # Simuliere nächste Runde
        battle.process_aftermath_phase()
        
        # HP sollte durch Gift reduziert werden
        assert battle.enemy_active.current_hp < original_hp
    
    def test_sleep_status_effect(self, basic_battle, battle_validation_helper):
        """Teste Schlaf-Status-Effekt."""
        battle = basic_battle
        
        # Erstelle Schlaf-Move
        sleep_move = Move(
            name="Schlaf-Pulver",
            power=0,
            pp=15,
            category=MoveCategory.SUPPORT,
            target=MoveTarget.ENEMY,
            type="normal",
            effects=[MoveEffect(
                kind=EffectKind.STATUS,
                status="sleep",
                chance=100.0
            )]
        )
        
        # Führe Schlaf-Angriff aus
        battle.queue_player_action({
            'action': 'attack',
            'move': sleep_move,
            'target': battle.enemy_active
        })
        
        result = battle.resolve_turn()
        
        # Gegner sollte schlafen
        assert battle.enemy_active.status_condition == StatusCondition.SLEEP
        
        # Schlafendes Monster sollte nicht angreifen können
        battle.queue_enemy_action({
            'action': 'attack',
            'move': battle.enemy_active.moves[0],
            'target': battle.player_active
        })
        
        result = battle.resolve_turn()
        
        # Schlafendes Monster sollte übersprungen werden
        assert 'skipped_turn' in result['turn_results'][0]
    
    def test_burn_status_effect(self, basic_battle, battle_validation_helper):
        """Teste Verbrennungs-Status-Effekt."""
        battle = basic_battle
        
        # Erstelle Verbrennungs-Move
        burn_move = Move(
            name="Feuer-Angriff",
            power=60,
            pp=20,
            category=MoveCategory.MAGICAL,
            target=MoveTarget.ENEMY,
            type="fire",
            effects=[MoveEffect(
                kind=EffectKind.STATUS,
                status="burn",
                chance=30.0
            )]
        )
        
        # Führe Feuer-Angriff aus
        battle.queue_player_action({
            'action': 'attack',
            'move': burn_move,
            'target': battle.enemy_active
        })
        
        result = battle.resolve_turn()
        
        # Verbrennung sollte ATK halbieren
        if battle.enemy_active.status_condition == StatusCondition.BURN:
            original_atk = battle.enemy_active.stats["atk"]
            effective_atk = battle.enemy_active.get_effective_stat("atk")
            
            assert effective_atk < original_atk
            assert effective_atk == original_atk // 2
    
    def test_paralysis_status_effect(self, basic_battle, battle_validation_helper):
        """Teste Lähmungs-Status-Effekt."""
        battle = basic_battle
        
        # Erstelle Lähmungs-Move
        paralysis_move = Move(
            name="Blitz-Angriff",
            power=50,
            pp=20,
            category=MoveCategory.MAGICAL,
            target=MoveTarget.ENEMY,
            type="electric",
            effects=[MoveEffect(
                kind=EffectKind.STATUS,
                status="paralysis",
                chance=25.0
            )]
        )
        
        # Führe Blitz-Angriff aus
        battle.queue_player_action({
            'action': 'attack',
            'move': paralysis_move,
            'target': battle.enemy_active
        })
        
        result = battle.resolve_turn()
        
        # Lähmung sollte Speed reduzieren
        if battle.enemy_active.status_condition == StatusCondition.PARALYSIS:
            original_spd = battle.enemy_active.stats["spd"]
            effective_spd = battle.enemy_active.get_effective_stat("spd")
            
            assert effective_spd < original_spd
    
    def test_status_effect_duration(self, basic_battle, battle_validation_helper):
        """Teste Status-Effekt-Dauer."""
        battle = basic_battle
        
        # Erstelle Status-Move
        status_move = Move(
            name="Status-Angriff",
            power=0,
            pp=15,
            category=MoveCategory.SUPPORT,
            target=MoveTarget.ENEMY,
            type="normal",
            effects=[MoveEffect(
                kind=EffectKind.STATUS,
                status="poison",
                chance=100.0,
                duration=3
            )]
        )
        
        # Führe Status-Angriff aus
        battle.queue_player_action({
            'action': 'attack',
            'move': status_move,
            'target': battle.enemy_active
        })
        
        result = battle.resolve_turn()
        
        # Status sollte 3 Runden anhalten
        for round_num in range(3):
            assert battle.enemy_active.status_condition == StatusCondition.POISON
            
            # Simuliere nächste Runde
            battle.process_aftermath_phase()
        
        # Nach 3 Runden sollte Status verschwinden
        battle.process_aftermath_phase()
        assert battle.enemy_active.status_condition == StatusCondition.NONE


class TestMonsterTraits:
    """Tests für Monster-Traits."""
    
    def test_trait_activation(self, basic_battle, battle_validation_helper):
        """Teste Trait-Aktivierung."""
        battle = basic_battle
        
        # Überprüfe aktive Traits
        player_traits = battle.player_active.get_active_traits()
        assert len(player_traits) > 0
        
        # Teste spezifische Trait-Effekte
        for trait in player_traits:
            if "Immunität" in trait.name:
                # Immunitäts-Traits sollten Status-Effekte blockieren
                assert trait.has_immunity("poison") or trait.has_immunity("burn")
    
    def test_trait_stat_modifiers(self, basic_battle, battle_validation_helper):
        """Teste Trait-Stat-Modifikatoren."""
        battle = basic_battle
        
        # Überprüfe Basis-Stats
        base_atk = battle.player_active.stats["atk"]
        base_def = battle.player_active.stats["def"]
        
        # Überprüfe effektive Stats mit Traits
        effective_atk = battle.player_active.get_effective_stat("atk")
        effective_def = battle.player_active.get_effective_stat("def")
        
        # Stats sollten durch Traits modifiziert werden
        assert effective_atk != base_atk or effective_def != base_def
    
    def test_trait_type_affinity(self, basic_battle, battle_validation_helper):
        """Teste Trait-Typ-Affinität."""
        battle = basic_battle
        
        # Überprüfe Typ-Affinitäten
        fire_affinity = battle.player_active.get_type_affinity("fire")
        water_affinity = battle.player_active.get_type_affinity("water")
        
        # Currywurst-Phoenix sollte Feuer-Affinität haben
        if "fire" in battle.player_active.types:
            assert fire_affinity > 1.0  # Resistenz oder Stärke
    
    def test_trait_conditional_effects(self, basic_battle, battle_validation_helper):
        """Teste bedingte Trait-Effekte."""
        battle = basic_battle
        
        # Teste Traits die bei niedriger HP aktiviert werden
        low_hp_traits = battle.player_active.get_conditional_traits("low_hp")
        
        # Setze HP auf niedrigen Wert
        battle.player_active.current_hp = battle.player_active.max_hp // 4
        
        # Überprüfe aktivierte Traits
        active_traits = battle.player_active.get_active_traits()
        
        # Niedrig-HP-Traits sollten aktiv sein
        for trait in low_hp_traits:
            if trait.is_active(battle.player_active):
                assert trait in active_traits
    
    def test_trait_synergy(self, balanced_battle, battle_validation_helper):
        """Teste Trait-Synergien zwischen Team-Mitgliedern."""
        battle = balanced_battle
        
        # Überprüfe Team-Traits
        team_traits = battle.get_team_traits()
        
        # Team-Traits sollten alle aktiven Monster betreffen
        for trait in team_traits:
            affected_monsters = trait.get_affected_monsters(battle.player_team)
            assert len(affected_monsters) > 0


class TestStatusEffectInteractions:
    """Tests für Status-Effekt-Interaktionen."""
    
    def test_status_effect_immunity(self, basic_battle, battle_validation_helper):
        """Teste Status-Effekt-Immunität."""
        battle = basic_battle
        
        # Überprüfe Immunitäten
        immunities = battle.player_active.get_status_immunities()
        
        # Teste immunes Monster
        if "poison" in immunities:
            poison_move = Move(
                name="Gift-Angriff",
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
            
            # Gift sollte blockiert werden
            battle.queue_enemy_action({
                'action': 'attack',
                'move': poison_move,
                'target': battle.player_active
            })
            
            result = battle.resolve_turn()
            
            # Status sollte nicht angewendet werden
            assert battle.player_active.status_condition == StatusCondition.NONE
    
    def test_status_effect_cure(self, basic_battle, battle_validation_helper):
        """Teste Status-Effekt-Heilung."""
        battle = basic_battle
        
        # Setze Status-Effekt
        battle.player_active.status_condition = StatusCondition.POISON
        
        # Erstelle Heilungs-Move
        cure_move = Move(
            name="Heilung",
            power=0,
            pp=10,
            category=MoveCategory.SUPPORT,
            target=MoveTarget.SELF,
            type="normal",
            effects=[MoveEffect(
                kind=EffectKind.CURE,
                status="poison"
            )]
        )
        
        # Führe Heilung aus
        battle.queue_player_action({
            'action': 'attack',
            'move': cure_move,
            'target': battle.player_active
        })
        
        result = battle.resolve_turn()
        
        # Status sollte geheilt sein
        assert battle.player_active.status_condition == StatusCondition.NONE
    
    def test_status_effect_chain(self, basic_battle, battle_validation_helper):
        """Teste Status-Effekt-Ketten."""
        battle = basic_battle
        
        # Erstelle mehrere Status-Moves
        status_moves = [
            Move(
                name="Gift-Angriff",
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
            ),
            Move(
                name="Verbrennungs-Angriff",
                power=0,
                pp=15,
                category=MoveCategory.SUPPORT,
                target=MoveTarget.ENEMY,
                type="fire",
                effects=[MoveEffect(
                    kind=EffectKind.STATUS,
                    status="burn",
                    chance=100.0
                )]
            )
        ]
        
        # Wende mehrere Status-Effekte an
        for move in status_moves:
            battle.queue_player_action({
                'action': 'attack',
                'move': move,
                'target': battle.enemy_active
            })
            
            result = battle.resolve_turn()
        
        # Monster sollte mehrere Status-Effekte haben
        active_statuses = battle.enemy_active.get_active_status_effects()
        assert len(active_statuses) > 1


class TestStatusEffectPerformance:
    """Tests für Status-Effekt Performance."""
    
    def test_status_effect_processing_speed(self, large_battle, performance_timer):
        """Status-Effekt-Verarbeitung < 5ms."""
        battle = large_battle
        
        # Erstelle viele Monster mit Status-Effekten
        for monster in battle.player_team + battle.enemy_team:
            monster.status_condition = StatusCondition.POISON
        
        performance_timer.start()
        
        # Verarbeite Status-Effekte für alle Monster
        battle.process_status_effects()
        
        performance_timer.stop()
        
        # Status-Effekt-Verarbeitung sollte unter 5ms dauern
        performance_timer.assert_faster_than(0.005, "Status-Effekt-Verarbeitung")
    
    def test_trait_calculation_speed(self, large_battle, performance_timer):
        """Trait-Berechnung < 10ms."""
        battle = large_battle
        
        performance_timer.start()
        
        # Berechne Traits für alle Monster
        for monster in battle.player_team + battle.enemy_team:
            monster.get_effective_stat("atk")
            monster.get_effective_stat("def")
            monster.get_active_traits()
        
        performance_timer.stop()
        
        # Trait-Berechnung sollte unter 10ms dauern
        performance_timer.assert_faster_than(0.01, "Trait-Berechnung")


class TestStatusEffectEdgeCases:
    """Tests für Status-Effekt Edge Cases."""
    
    def test_multiple_status_effects(self, basic_battle, battle_validation_helper):
        """Teste mehrere Status-Effekte gleichzeitig."""
        battle = basic_battle
        
        # Setze mehrere Status-Effekte
        battle.player_active.status_condition = StatusCondition.POISON
        battle.player_active.add_status_effect("burn", duration=3)
        battle.player_active.add_status_effect("paralysis", duration=2)
        
        # Überprüfe alle aktiven Status-Effekte
        active_statuses = battle.player_active.get_active_status_effects()
        assert len(active_statuses) == 3
        
        # Status-Effekte sollten sich nicht widersprechen
        for status in active_statuses:
            assert status.is_valid_combination(active_statuses)
    
    def test_status_effect_overflow(self, basic_battle, battle_validation_helper):
        """Teste Status-Effekt-Overflow."""
        battle = basic_battle
        
        # Versuche zu viele Status-Effekte hinzuzufügen
        for i in range(10):
            battle.player_active.add_status_effect("poison", duration=1)
        
        # System sollte Status-Effekte begrenzen
        active_statuses = battle.player_active.get_active_status_effects()
        assert len(active_statuses) <= 5  # Max 5 Status-Effekte
    
    def test_invalid_status_combinations(self, basic_battle, battle_validation_helper):
        """Teste ungültige Status-Effekt-Kombinationen."""
        battle = basic_battle
        
        # Setze widersprüchliche Status-Effekte
        battle.player_active.status_condition = StatusCondition.SLEEP
        battle.player_active.add_status_effect("paralysis", duration=3)
        
        # System sollte widersprüchliche Effekte entfernen
        active_statuses = battle.player_active.get_active_status_effects()
        
        # Schlaf und Lähmung sollten nicht gleichzeitig möglich sein
        has_sleep = any(s.condition == StatusCondition.SLEEP for s in active_statuses)
        has_paralysis = any(s.condition == StatusCondition.PARALYSIS for s in active_statuses)
        
        assert not (has_sleep and has_paralysis)
