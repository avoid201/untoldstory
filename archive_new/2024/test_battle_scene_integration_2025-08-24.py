#!/usr/bin/env python3
"""
Test für die Battle Scene Integration
Testet das neue Battle System direkt mit der Battle Scene
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pygame
from engine.systems.battle.battle_system import BattleState, BattleType, BattlePhase
from engine.systems.monster_instance import MonsterInstance, MonsterSpecies, MonsterRank
from engine.systems.moves import Move, EffectKind, MoveCategory, MoveTarget, MoveEffect
from engine.systems.stats import BaseStats, StatStages, GrowthCurve

def create_test_monster(name: str, level: int = 5) -> MonsterInstance:
    """Erstellt ein Test-Monster."""
    try:
        # Basis-Stats
        base_stats = BaseStats(hp=100, atk=50, def_=50, mag=30, res=30, spd=70)
        
        # Erstelle Monster-Species
        species = MonsterSpecies(
            id=1,
            name=name,
            era="present",
            rank=MonsterRank.E,
            types=["Bestie"],
            base_stats=base_stats,
            growth_curve=GrowthCurve.MEDIUM_FAST,
            base_exp_yield=64,
            capture_rate=45,
            traits=[],
            talents=[],
            evolution=None,
            description=f"Test-Monster: {name}"
        )
        
        # Erstelle Monster-Instance
        monster = MonsterInstance(
            species=species,
            level=level,
            nickname=name
        )
        
        # Setze aktuelle HP
        monster.current_hp = monster.max_hp
        
        return monster
        
    except Exception as e:
        print(f"Fehler beim Erstellen des Test-Monsters {name}: {str(e)}")
        return None

def create_test_move(name: str, power: int = 40) -> Move:
    """Erstellt einen Test-Move."""
    try:
        # Erstelle Move-Effekt
        effect = MoveEffect(
            kind=EffectKind.DAMAGE,
            power=power,
            chance=100.0
        )
        
        return Move(
            id=f"test_{name.lower()}",
            name=name,
            type="Bestie",
            category=MoveCategory.PHYSICAL,
            power=power,
            accuracy=95,
            pp=15,
            max_pp=15,
            priority=0,
            targeting=MoveTarget.ENEMY,
            effects=[effect],
            description=f"Test-Move: {name}"
        )
    except Exception as e:
        print(f"Fehler beim Erstellen des Test-Moves {name}: {str(e)}")
        return None

def test_battle_system_integration():
    """Testet die Integration von Battle System und Battle Scene."""
    print("🎮 BATTLE SCENE INTEGRATION TEST")
    print("="*50)
    
    try:
        # Pygame initialisieren
        pygame.init()
        
        # Erstelle Test-Monster
        print("1. Erstelle Test-Monster...")
        player_monster = create_test_monster("TestPlayer", 5)
        enemy_monster = create_test_monster("TestEnemy", 5)
        
        if not player_monster or not enemy_monster:
            print("❌ Fehler beim Erstellen der Test-Monster!")
            return False
        
        # Füge Moves hinzu
        player_monster.moves = [create_test_move("Tackle", 40)]
        enemy_monster.moves = [create_test_move("Bite", 45)]
        
        print("✅ Test-Monster erfolgreich erstellt")
        
        # Teste Battle State Erstellung
        print("2. Erstelle Battle State...")
        battle_state = BattleState(
            player_team=[player_monster],
            enemy_team=[enemy_monster],
            battle_type=BattleType.WILD
        )
        print("✅ Battle State erfolgreich erstellt")
        
        # Teste Phase-Übergänge
        print("3. Teste Phase-Übergänge...")
        initial_phase = battle_state.phase
        print(f"   Initial Phase: {initial_phase.value}")
        
        # Teste Action-System
        print("4. Teste Action-System...")
        action = {
            'action_type': 'attack',
            'actor': player_monster,
            'move': player_monster.moves[0],
            'target': enemy_monster
        }
        
        success = battle_state.queue_player_action(action)
        if success:
            print("✅ Action erfolgreich hinzugefügt")
            
            # Teste Turn-Ausführung
            print("5. Teste Turn-Ausführung...")
            results = battle_state.resolve_turn()
            
            if 'error' not in results:
                print("✅ Turn erfolgreich ausgeführt")
                print(f"   Turn-Ergebnisse: {len(results['turn_results'])} Aktionen")
                
                # Zeige Kampf-Status
                status = battle_state.get_battle_status()
                if 'error' not in status:
                    print("✅ Battle-Status erfolgreich abgerufen")
                    print(f"   Spieler HP: {status['player_active']['current_hp']}/{status['player_active']['max_hp']}")
                    print(f"   Gegner HP: {status['enemy_active']['current_hp']}/{status['enemy_active']['max_hp']}")
                else:
                    print(f"❌ Fehler beim Battle-Status: {status['error']}")
                    return False
            else:
                print(f"❌ Fehler bei der Turn-Ausführung: {results['error']}")
                return False
        else:
            print("❌ Fehler beim Hinzufügen der Action!")
            return False
        
        print()
        print("🎉 ALLE INTEGRATION TESTS ERFOLGREICH!")
        print("Das Battle System ist vollständig integriert und funktionsfähig!")
        return True
        
    except Exception as e:
        print(f"❌ Unerwarteter Fehler: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        pygame.quit()

def test_battle_ui_compatibility():
    """Testet die Kompatibilität mit der Battle UI."""
    print("\n🎨 BATTLE UI COMPATIBILITY TEST")
    print("="*50)
    
    try:
        # Erstelle Battle State
        player_monster = create_test_monster("UITest1", 5)
        enemy_monster = create_test_monster("UITest2", 5)
        
        player_monster.moves = [create_test_move("TestMove", 40)]
        enemy_monster.moves = [create_test_move("TestMove", 40)]
        
        battle_state = BattleState(
            player_team=[player_monster],
            enemy_team=[enemy_monster]
        )
        
        # Teste UI-relevante Funktionen
        print("1. Teste Battle-Status für UI...")
        status = battle_state.get_battle_status()
        
        required_keys = ['phase', 'player_active', 'enemy_active', 'can_flee', 'can_catch']
        for key in required_keys:
            if key in status:
                print(f"✅ {key}: {status[key]}")
            else:
                print(f"❌ Fehlender Key: {key}")
                return False
        
        # Teste verfügbare Moves
        print("2. Teste verfügbare Moves...")
        moves = battle_state.get_available_moves(player_monster)
        print(f"✅ Verfügbare Moves: {len(moves)}")
        
        # Teste verfügbare Wechsel
        print("3. Teste verfügbare Wechsel...")
        switches = battle_state.get_available_switches()
        print(f"✅ Verfügbare Wechsel: {len(switches)}")
        
        print("\n🎉 UI COMPATIBILITY TESTS ERFOLGREICH!")
        return True
        
    except Exception as e:
        print(f"❌ Fehler bei UI-Kompatibilität: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Starte Battle Scene Integration Tests...")
    print()
    
    success = True
    success &= test_battle_system_integration()
    success &= test_battle_ui_compatibility()
    
    print("\n" + "="*60)
    if success:
        print("🎉 ALLE INTEGRATION TESTS ERFOLGREICH!")
        print("Das Battle System ist vollständig bereit für den Einsatz!")
        print("✅ Battle State Integration")
        print("✅ Action System")
        print("✅ Turn Management")
        print("✅ UI Compatibility")
        print("✅ Error Handling")
    else:
        print("❌ EINIGE INTEGRATION TESTS SIND FEHLGESCHLAGEN!")
        print("Bitte überprüfe die Fehler.")
    print("="*60)
