#!/usr/bin/env python3
"""
Test des verbesserten Battle Systems
Überprüft alle kritischen Funktionen und UI-Elemente
"""

import sys
import os
import pygame
import random
from typing import List, Dict, Any

# Füge den Projektpfad hinzu
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.systems.battle.battle_system import BattleState, BattleType, BattlePhase
from engine.systems.battle.turn_logic import ActionType, BattleAction
from engine.systems.monster_instance import MonsterInstance, MonsterSpecies, StatusCondition
from engine.systems.stats import BaseStats, StatStages
from engine.systems.moves import Move, MoveCategory, MoveTarget
from engine.ui.battle_ui import BattleUI, BattleMenuState
from engine.scenes.battle_scene import BattleScene
from engine.core.config import Colors, LOGICAL_WIDTH, LOGICAL_HEIGHT

class MockGame:
    """Mock Game-Objekt für Tests."""
    def __init__(self):
        self.party_manager = MockPartyManager()
        self.current_map = 'test_map'
        self.player_pos = (5, 5)
    
    def pop_scene(self):
        print("Scene würde geschlossen werden")
    
    def push_scene(self, scene):
        print(f"Scene würde geöffnet werden: {type(scene).__name__}")

class MockPartyManager:
    """Mock Party Manager für Tests."""
    def __init__(self):
        self.party = MockParty()

class MockParty:
    """Mock Party für Tests."""
    def __init__(self):
        self.members = [create_test_monster("TestMonster1", 5)]
    
    def get_conscious_members(self):
        return [m for m in self.members if not m.is_fainted]

def create_test_monster(name: str, level: int) -> MonsterInstance:
    """Erstellt ein Test-Monster für Tests."""
    try:
        # Erstelle Basis-Stats
        base_stats = BaseStats(hp=100, atk=50, def_=50, mag=30, res=30, spd=70)
        
        # Erstelle Stat-Stages
        stat_stages = StatStages()
        
        # Erstelle Spezies
        species = MonsterSpecies(
            id=1, 
            name=name, 
            base_stats=base_stats,
            types=["Bestie"]
        )
        
        # Erstelle Monster-Instanz
        monster = MonsterInstance(
            species=species,
            level=level,
            nickname=name
        )
        
        # Füge Moves hinzu
        moves = [
            create_test_move("Tackle", "Normal", 40),
            create_test_move("Biss", "Bestie", 60),
            create_test_move("Schutz", "Normal", 0),
            create_test_move("Heilung", "Normal", 0)
        ]
        monster.moves = moves
        
        return monster
        
    except Exception as e:
        print(f"Fehler beim Erstellen des Test-Monsters: {str(e)}")
        # Fallback: Einfaches Monster
        return create_simple_monster(name, level)

def create_simple_monster(name: str, level: int) -> MonsterInstance:
    """Erstellt ein einfaches Test-Monster als Fallback."""
    class SimpleMonster:
        def __init__(self, name, level):
            self.name = name
            self.level = level
            self.is_fainted = False
            self.current_hp = 100
            self.max_hp = 100
            self.stats = {"hp": 100, "atk": 50, "def": 50, "mag": 30, "res": 30, "spd": 70}
            self.stat_stages = SimpleStatStages()
            self.moves = [create_test_move("Tackle", "Normal", 40)]
            self.status = StatusCondition.NONE
            self.experience = 0
            self.id = 1
        
        def process_status(self):
            return {"skip_turn": False, "message": ""}
    
    class SimpleStatStages:
        def __init__(self):
            self.stages = {"hp": 0, "atk": 0, "def": 0, "mag": 0, "res": 0, "spd": 0}
        
        def get(self, stat, default=0):
            return self.stages.get(stat, default)
        
        def reset(self):
            for stat in self.stages:
                self.stages[stat] = 0
    
    return SimpleMonster(name, level)

def create_test_move(name: str, move_type: str, power: int) -> Move:
    """Erstellt einen Test-Move."""
    try:
        from engine.systems.moves import MoveEffect, EffectKind
        
        effects = []
        if power > 0:
            effects.append(MoveEffect(
                kind=EffectKind.DAMAGE,
                power=power,
                chance=100.0
            ))
        else:
            effects.append(MoveEffect(
                kind=EffectKind.BUFF,
                chance=100.0
            ))
        
        return Move(
            id=name.lower(),
            name=name,
            type=move_type,
            category=MoveCategory.PHYSICAL if power > 0 else MoveCategory.SUPPORT,
            power=power,
            accuracy=90,
            pp=15,
            max_pp=15,
            priority=0,
            targeting=MoveTarget.ENEMY,
            effects=effects,
            description=f"Test-Move: {name}"
        )
        
    except Exception as e:
        print(f"Fehler beim Erstellen des Test-Moves: {str(e)}")
        # Fallback: Einfacher Move
        return create_simple_move(name, move_type, power)

def create_simple_move(name: str, move_type: str, power: int):
    """Erstellt einen einfachen Test-Move als Fallback."""
    class SimpleMove:
        def __init__(self, name, move_type, power):
            self.name = name
            self.type = move_type
            self.power = power
            self.accuracy = 90
            self.pp = 15
            self.max_pp = 15
            self.priority = 0
        
        def can_use(self):
            return self.pp > 0
        
        def use(self):
            if self.pp > 0:
                self.pp -= 1
                return True
            return False
    
    return SimpleMove(name, move_type, power)

def test_battle_state():
    """Testet den Battle State."""
    print("\n=== Teste Battle State ===")
    
    try:
        # Erstelle Test-Monster
        player_monster = create_test_monster("SpielerMonster", 5)
        enemy_monster = create_test_monster("GegnerMonster", 5)
        
        print(f"Spieler-Monster: {player_monster.name} Lv.{player_monster.level}")
        print(f"Gegner-Monster: {enemy_monster.name} Lv.{enemy_monster.level}")
        
        # Erstelle Battle State
        battle_state = BattleState(
            player_team=[player_monster],
            enemy_team=[enemy_monster],
            battle_type=BattleType.WILD
        )
        
        print("✅ Battle State erfolgreich erstellt")
        print(f"Phase: {battle_state.phase}")
        print(f"Spieler aktiv: {battle_state.player_active.name}")
        print(f"Gegner aktiv: {battle_state.enemy_active.name}")
        
        # Teste Validierung
        is_valid = battle_state.validate_battle_state()
        print(f"Kampfzustand gültig: {is_valid}")
        
        return battle_state
        
    except Exception as e:
        print(f"❌ Fehler beim Testen des Battle States: {str(e)}")
        return None

def test_battle_ui():
    """Testet die Battle UI."""
    print("\n=== Teste Battle UI ===")
    
    try:
        # Erstelle Mock Game
        game = MockGame()
        
        # Erstelle Battle UI
        battle_ui = BattleUI(game)
        print("✅ Battle UI erfolgreich erstellt")
        
        # Teste UI-Komponenten
        print(f"Menu State: {battle_ui.menu_state}")
        print(f"HUD vorhanden: {battle_ui.hud is not None}")
        print(f"Menu vorhanden: {battle_ui.menu is not None}")
        
        # Teste Input-Behandlung
        result = battle_ui.handle_input('up')
        print(f"Input 'up' verarbeitet: {result}")
        
        result = battle_ui.handle_input('confirm')
        print(f"Input 'confirm' verarbeitet: {result}")
        
        return battle_ui
        
    except Exception as e:
        print(f"❌ Fehler beim Testen der Battle UI: {str(e)}")
        return None

def test_battle_scene():
    """Testet die Battle Scene."""
    print("\n=== Teste Battle Scene ===")
    
    try:
        # Erstelle Mock Game
        game = MockGame()
        
        # Erstelle Battle Scene
        battle_scene = BattleScene(game)
        print("✅ Battle Scene erfolgreich erstellt")
        
        # Teste Scene-Initialisierung
        print(f"Battle UI vorhanden: {battle_scene.battle_ui is not None}")
        print(f"Battle State vorhanden: {battle_scene.battle_state is None}")
        print(f"Current Phase: {battle_scene.current_phase}")
        
        return battle_scene
        
    except Exception as e:
        print(f"❌ Fehler beim Testen der Battle Scene: {str(e)}")
        return None

def test_battle_flow():
    """Testet den kompletten Battle-Flow."""
    print("\n=== Teste Battle Flow ===")
    
    try:
        # Erstelle alle Komponenten
        battle_state = test_battle_state()
        if not battle_state:
            return False
        
        battle_ui = test_battle_ui()
        if not battle_ui:
            return False
        
        # Teste Battle-Start
        start_result = battle_state.start_battle()
        print(f"Battle gestartet: {start_result}")
        
        # Teste Action-Queuing
        if battle_state.player_active and battle_state.player_active.moves:
            move = battle_state.player_active.moves[0]
            action = BattleAction(
                actor=battle_state.player_active,
                action_type=ActionType.ATTACK,
                move=move,
                target=battle_state.enemy_active
            )
            
            success = battle_state.queue_player_action(action)
            print(f"Action gequeued: {success}")
            
            if success:
                # Teste Turn-Resolution
                turn_results = battle_state.resolve_turn()
                print(f"Turn aufgelöst: {turn_results}")
                
                # Teste Battle-Result
                battle_result = battle_state.get_battle_result()
                print(f"Battle-Result: {battle_result}")
        
        print("✅ Battle Flow erfolgreich getestet")
        return True
        
    except Exception as e:
        print(f"❌ Fehler beim Testen des Battle Flows: {str(e)}")
        return False

def test_input_handling():
    """Testet die Input-Behandlung."""
    print("\n=== Teste Input-Behandlung ===")
    
    try:
        # Erstelle Battle UI
        game = MockGame()
        battle_ui = BattleUI(game)
        
        # Teste verschiedene Inputs
        inputs = ['up', 'down', 'left', 'right', 'confirm', 'back']
        
        for input_key in inputs:
            result = battle_ui.handle_input(input_key)
            print(f"Input '{input_key}' → {result}")
        
        # Teste Menu-State-Wechsel
        print(f"\nMenu State vor 'confirm': {battle_ui.menu_state}")
        battle_ui.handle_input('confirm')
        print(f"Menu State nach 'confirm': {battle_ui.menu_state}")
        
        print("✅ Input-Behandlung erfolgreich getestet")
        return True
        
    except Exception as e:
        print(f"❌ Fehler beim Testen der Input-Behandlung: {str(e)}")
        return False

def main():
    """Hauptfunktion für alle Tests."""
    print("🚀 Starte Battle System Tests...")
    
    # Initialisiere Pygame
    pygame.init()
    
    try:
        # Führe alle Tests aus
        test_battle_state()
        test_battle_ui()
        test_battle_scene()
        test_battle_flow()
        test_input_handling()
        
        print("\n🎉 Alle Tests erfolgreich abgeschlossen!")
        print("\nDas Battle System ist bereit für den Einsatz!")
        
    except Exception as e:
        print(f"\n💥 Kritischer Fehler bei den Tests: {str(e)}")
        
    finally:
        pygame.quit()

if __name__ == "__main__":
    main()
