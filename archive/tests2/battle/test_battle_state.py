"""
Unit Tests für Battle State Initialisierung und Validierung
"""

import pytest
from typing import List

from engine.systems.battle import BattleState, BattleType, BattlePhase
from engine.systems.monster_instance import MonsterInstance
from .test_monsters import TestMonsters
from .conftest import battle_validation_helper


class TestBattleStateInitialization:
    """Tests für Battle State Initialisierung."""
    
    def test_valid_initialization(self, battle_validation_helper):
        """Teste normale Initialisierung."""
        battle = BattleState(
            player_team=[TestMonsters.create_currywurst_phoenix()],
            enemy_team=[TestMonsters.create_schachtschreck()],
            battle_type=BattleType.WILD
        )
        
        battle_validation_helper.assert_valid_battle_state(battle)
        assert battle.battle_type == BattleType.WILD
        assert battle.can_flee is True
        assert battle.can_catch is True
        assert battle.enable_3v3 is False
    
    def test_trainer_battle_initialization(self, battle_validation_helper):
        """Teste Trainer-Battle Initialisierung."""
        battle = BattleState(
            player_team=[TestMonsters.create_ruhrpott_ritter()],
            enemy_team=[TestMonsters.create_bergmann_meister()],
            battle_type=BattleType.TRAINER
        )
        
        battle_validation_helper.assert_valid_battle_state(battle)
        assert battle.battle_type == BattleType.TRAINER
        assert battle.can_flee is False
        assert battle.can_catch is False
    
    def test_3v3_battle_initialization(self, battle_validation_helper):
        """Teste 3v3 Battle Initialisierung."""
        battle = BattleState(
            player_team=TestMonsters.create_balanced_team(),
            enemy_team=TestMonsters.create_balanced_team(),
            battle_type=BattleType.TRAINER,
            enable_3v3=True
        )
        
        battle_validation_helper.assert_valid_battle_state(battle)
        assert battle.enable_3v3 is True
        assert battle.formation_manager is not None
        assert battle.targeting_system is not None
    
    def test_empty_team_rejection(self):
        """Teste dass leere Teams abgelehnt werden."""
        with pytest.raises(ValueError, match="Player and enemy teams cannot be empty"):
            BattleState(
                player_team=[],
                enemy_team=[TestMonsters.create_schachtschreck()],
                battle_type=BattleType.WILD
            )
        
        with pytest.raises(ValueError, match="Player and enemy teams cannot be empty"):
            BattleState(
                player_team=[TestMonsters.create_currywurst_phoenix()],
                enemy_team=[],
                battle_type=BattleType.WILD
            )
    
    def test_invalid_monster_type_rejection(self):
        """Teste dass ungültige Monster-Typen abgelehnt werden."""
        invalid_monster = {"name": "Invalid", "level": 10}
        
        with pytest.raises(TypeError, match="All team members must be MonsterInstance objects"):
            BattleState(
                player_team=[invalid_monster],
                enemy_team=[TestMonsters.create_schachtschreck()],
                battle_type=BattleType.WILD
            )
    
    def test_fainted_team_handling(self, battle_validation_helper):
        """Teste Handling von bewusstlosen Teams."""
        # Erstelle Monster mit 0 HP
        fainted_monster = TestMonsters.create_weak_monster()
        fainted_monster.current_hp = 0
        
        # Das System sollte die HP automatisch reparieren
        battle = BattleState(
            player_team=[fainted_monster],
            enemy_team=[TestMonsters.create_schachtschreck()],
            battle_type=BattleType.WILD
        )
        
        battle_validation_helper.assert_valid_battle_state(battle)
        assert battle.player_active.current_hp > 0
    
    def test_battle_phase_initialization(self):
        """Teste dass der Battle-Phase korrekt initialisiert wird."""
        battle = BattleState(
            player_team=[TestMonsters.create_currywurst_phoenix()],
            enemy_team=[TestMonsters.create_schachtschreck()],
            battle_type=BattleType.WILD
        )
        
        assert hasattr(battle, 'current_phase')
        assert battle.current_phase in [BattlePhase.INTRO, BattlePhase.INPUT]
    
    def test_active_monster_selection(self, battle_validation_helper):
        """Teste dass aktive Monster korrekt ausgewählt werden."""
        battle = BattleState(
            player_team=[TestMonsters.create_currywurst_phoenix()],
            enemy_team=[TestMonsters.create_schachtschreck()],
            battle_type=BattleType.WILD
        )
        
        battle_validation_helper.assert_valid_battle_state(battle)
        assert battle.player_active.name == "Currywurst-Phoenix"
        assert battle.enemy_active.name == "Schachtschreck"
    
    def test_team_size_validation(self):
        """Teste Team-Größen-Validierung."""
        # Teste zu große Teams
        large_team = [TestMonsters.create_currywurst_phoenix()] * 10
        
        with pytest.raises(ValueError):
            BattleState(
                player_team=large_team,
                enemy_team=[TestMonsters.create_schachtschreck()],
                battle_type=BattleType.WILD
            )
    
    def test_battle_options_initialization(self):
        """Teste Battle-Optionen-Initialisierung."""
        battle = BattleState(
            player_team=[TestMonsters.create_currywurst_phoenix()],
            enemy_team=[TestMonsters.create_schachtschreck()],
            battle_type=BattleType.WILD,
            can_flee=False,
            can_catch=False
        )
        
        assert battle.can_flee is False
        assert battle.can_catch is False
    
    def test_formation_type_initialization(self):
        """Teste Formation-Typ-Initialisierung."""
        battle = BattleState(
            player_team=TestMonsters.create_balanced_team(),
            enemy_team=TestMonsters.create_balanced_team(),
            battle_type=BattleType.TRAINER,
            enable_3v3=True,
            player_formation_type="aggressive",
            enemy_formation_type="defensive"
        )
        
        assert battle.enable_3v3 is True
        assert battle.formation_manager is not None


class TestBattleStateValidation:
    """Tests für Battle State Validierung."""
    
    def test_validate_battle_state_success(self, basic_battle):
        """Teste erfolgreiche Battle-State-Validierung."""
        assert basic_battle.validate_battle_state() is True
    
    def test_validate_battle_state_with_fainted_monsters(self):
        """Teste Validierung mit bewusstlosen Monstern."""
        battle = BattleState(
            player_team=[TestMonsters.create_weak_monster()],
            enemy_team=[TestMonsters.create_schachtschreck()],
            battle_type=BattleType.WILD
        )
        
        # Setze HP auf 0
        battle.player_active.current_hp = 0
        
        # Validierung sollte fehlschlagen
        assert battle.validate_battle_state() is False
    
    def test_validate_battle_state_with_invalid_stats(self):
        """Teste Validierung mit ungültigen Stats."""
        monster = TestMonsters.create_weak_monster()
        monster.current_hp = -10  # Ungültige HP
        
        battle = BattleState(
            player_team=[monster],
            enemy_team=[TestMonsters.create_schachtschreck()],
            battle_type=BattleType.WILD
        )
        
        # Validierung sollte fehlschlagen
        assert battle.validate_battle_state() is False


class TestBattleStateProperties:
    """Tests für Battle State Eigenschaften."""
    
    def test_battle_is_active_property(self, basic_battle):
        """Teste battle_is_active Property."""
        assert basic_battle.battle_is_active is True
    
    def test_battle_is_active_when_finished(self):
        """Teste battle_is_active wenn Battle beendet ist."""
        battle = BattleState(
            player_team=[TestMonsters.create_weak_monster()],
            enemy_team=[TestMonsters.create_schachtschreck()],
            battle_type=BattleType.WILD
        )
        
        # Setze alle Monster auf 0 HP
        battle.player_active.current_hp = 0
        battle.enemy_active.current_hp = 0
        
        assert battle.battle_is_active is False
    
    def test_winner_determination(self):
        """Teste Gewinner-Bestimmung."""
        battle = BattleState(
            player_team=[TestMonsters.create_weak_monster()],
            enemy_team=[TestMonsters.create_schachtschreck()],
            battle_type=BattleType.WILD
        )
        
        # Setze Spieler-Monster auf 0 HP
        battle.player_active.current_hp = 0
        
        assert battle.get_winner() == "enemy"
    
    def test_draw_determination(self):
        """Teste Unentschieden-Bestimmung."""
        battle = BattleState(
            player_team=[TestMonsters.create_weak_monster()],
            enemy_team=[TestMonsters.create_schachtschreck()],
            battle_type=BattleType.WILD
        )
        
        # Setze beide Monster auf 0 HP
        battle.player_active.current_hp = 0
        battle.enemy_active.current_hp = 0
        
        assert battle.get_winner() == "draw"


class TestBattleStateEdgeCases:
    """Tests für Battle State Edge Cases."""
    
    def test_single_monster_teams(self, battle_validation_helper):
        """Teste Teams mit nur einem Monster."""
        battle = BattleState(
            player_team=[TestMonsters.create_currywurst_phoenix()],
            enemy_team=[TestMonsters.create_schachtschreck()],
            battle_type=BattleType.WILD
        )
        
        battle_validation_helper.assert_valid_battle_state(battle)
        assert len(battle.player_team) == 1
        assert len(battle.enemy_team) == 1
    
    def test_maximum_monster_teams(self, battle_validation_helper):
        """Teste Teams mit maximaler Monster-Anzahl."""
        max_team = TestMonsters.create_team_for_3v3()[:6]  # Max 6 Monster
        
        battle = BattleState(
            player_team=max_team,
            enemy_team=max_team,
            battle_type=BattleType.TRAINER,
            enable_3v3=True
        )
        
        battle_validation_helper.assert_valid_battle_state(battle)
        assert len(battle.player_team) == 6
        assert len(battle.enemy_team) == 6
    
    def test_monster_with_zero_stats(self):
        """Teste Monster mit 0 Stats."""
        monster = TestMonsters.create_monster_with_custom_stats({
            "hp": 0, "mp": 0, "atk": 0, "def": 0, "mag": 0, "res": 0, "spd": 0
        })
        
        # Das System sollte die Stats auf Standardwerte setzen
        battle = BattleState(
            player_team=[monster],
            enemy_team=[TestMonsters.create_schachtschreck()],
            battle_type=BattleType.WILD
        )
        
        assert battle.player_active.current_hp > 0
        assert battle.player_active.max_hp > 0
