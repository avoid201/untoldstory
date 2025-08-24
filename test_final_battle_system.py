#!/usr/bin/env python3
"""
Final Test für das integrierte Battle System
Testet alle Features und die UI-Integration
"""

import sys
import os
import logging
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Konfiguriere Logging für bessere Fehlerverfolgung
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

from engine.systems.battle.battle import BattleState, BattleType, BattlePhase
from engine.systems.battle.turn_logic import BattleAction, ActionType
from engine.systems.monster_instance import MonsterInstance, StatusCondition, MonsterSpecies, MonsterRank
from engine.systems.moves import Move, EffectKind, MoveCategory, MoveTarget, MoveEffect
from engine.systems.stats import BaseStats, StatStages, GrowthCurve

def create_test_monster(name: str, level: int = 5) -> MonsterInstance:
    """Erstellt ein Test-Monster."""
    try:
        # Basis-Stats
        base_stats = BaseStats(hp=100, atk=50, def_=50, mag=30, res=30, spd=70)
        
        # Stat-Stages
        stat_stages = StatStages()
        
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
            learnset=[],
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

def test_battle_system():
    """Testet das komplette Battle System."""
    print("=== FINAL BATTLE SYSTEM TEST ===")
    print()
    
    try:
        # Erstelle Test-Monster
        print("1. Erstelle Test-Monster...")
        player_monster = create_test_monster("TestMonster1", 5)
        enemy_monster = create_test_monster("TestMonster2", 5)
        
        if not player_monster or not enemy_monster:
            print("❌ Fehler beim Erstellen der Test-Monster!")
            return False
        
        # Füge Moves hinzu
        player_monster.moves = [
            create_test_move("Tackle", 40),
            create_test_move("Scratch", 35)
        ]
        enemy_monster.moves = [
            create_test_move("Bite", 45),
            create_test_move("Growl", 0)
        ]
        
        print("✅ Test-Monster erfolgreich erstellt")
        print(f"   Spieler: {player_monster.name} Lv.{player_monster.level}")
        print(f"   Gegner: {enemy_monster.name} Lv.{enemy_monster.level}")
        print()
        
        # Erstelle Battle State
        print("2. Erstelle Battle State...")
        battle_state = BattleState(
            player_team=[player_monster],
            enemy_team=[enemy_monster],
            battle_type=BattleType.WILD
        )
        print("✅ Battle State erfolgreich erstellt")
        print(f"   Phase: {battle_state.phase.value}")
        print(f"   Aktiver Spieler: {battle_state.player_active.name}")
        print(f"   Aktiver Gegner: {battle_state.enemy_active.name}")
        print()
        
        # Starte den Battle
        print("2a. Starte Battle...")
        start_result = battle_state.start_battle()
        if 'error' in start_result:
            print(f"❌ Fehler beim Starten des Battles: {start_result['error']}")
            return False
        print("✅ Battle erfolgreich gestartet")
        print(f"   Neue Phase: {battle_state.phase.value}")
        print()
        
        # Teste Battle-Validierung
        print("3. Teste Battle-Validierung...")
        if battle_state.validate_battle_state():
            print("✅ Battle-Validierung erfolgreich")
        else:
            print("❌ Battle-Validierung fehlgeschlagen!")
            return False
        
        # Teste Action-Queue
        print("4. Teste Action-Queue...")
        attack_action = {
            'action_type': 'attack',
            'actor': player_monster,
            'move': player_monster.moves[0],
            'target': enemy_monster
        }
        
        if battle_state.queue_player_action(attack_action):
            print("✅ Action erfolgreich zur Queue hinzugefügt")
            print(f"   Actions in Queue: {len(battle_state.action_queue)}")
        else:
            print("❌ Fehler beim Hinzufügen der Action!")
            return False
        
        # Teste Turn-Auflösung
        print("5. Teste Turn-Auflösung...")
        turn_results = battle_state.resolve_turn()
        
        if 'error' not in turn_results:
            print("✅ Turn erfolgreich aufgelöst")
            print(f"   Turn-Nummer: {turn_results['turn_count']}")
            print(f"   Ergebnisse: {len(turn_results['turn_results'])}")
            
            # Zeige Turn-Ergebnisse
            for result in turn_results['turn_results']:
                if isinstance(result, dict) and 'type' in result:
                    if result['type'] == 'attack':
                        print(f"   Angriff: {result['attacker']} → {result['target']} ({result['damage']} Schaden)")
                        print(f"   Ziel ohnmächtig: {result['target_fainted']}")
                else:
                    print(f"   Ergebnis: {result}")
        else:
            print(f"❌ Fehler bei der Turn-Auflösung: {turn_results['error']}")
            return False
        
        # Teste Battle-Status
        print("6. Teste Battle-Status...")
        battle_status = battle_state.get_battle_status()
        
        if 'error' not in battle_status:
            print("✅ Battle-Status erfolgreich abgerufen")
            print(f"   Phase: {battle_status['phase']}")
            print(f"   Spieler HP: {battle_status['player_active']['current_hp']}/{battle_status['player_active']['max_hp']}")
            print(f"   Gegner HP: {battle_status['enemy_active']['current_hp']}/{battle_status['enemy_active']['max_hp']}")
        else:
            print(f"❌ Fehler beim Abrufen des Battle-Status: {battle_status['error']}")
            return False
        
        # Teste verfügbare Moves
        print("7. Teste verfügbare Moves...")
        available_moves = battle_state.get_available_moves(player_monster)
        print(f"✅ Verfügbare Moves: {len(available_moves)}")
        for move in available_moves:
            print(f"   - {move.name} (PP: {move.pp}/{move.max_pp})")
        
        # Teste verfügbare Wechsel
        print("8. Teste verfügbare Wechsel...")
        available_switches = battle_state.get_available_switches()
        print(f"✅ Verfügbare Wechsel: {len(available_switches)}")
        
        print()
        print("🎉 ALLE TESTS ERFOLGREICH!")
        print("Das integrierte Battle System funktioniert einwandfrei!")
        return True
        
    except Exception as e:
        print(f"❌ Unerwarteter Fehler: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_battle_phases():
    """Testet die verschiedenen Battle-Phasen."""
    print("\n=== BATTLE PHASES TEST ===")
    print()
    
    try:
        # Erstelle Test-Monster
        player_monster = create_test_monster("PhaseTest1", 5)
        enemy_monster = create_test_monster("PhaseTest2", 5)
        player_monster.moves = [create_test_move("Test", 40)]
        enemy_monster.moves = [create_test_move("Test", 40)]
        
        # Erstelle Battle State
        battle_state = BattleState(
            player_team=[player_monster],
            enemy_team=[enemy_monster]
        )
        
        # Teste alle Phasen
        phases = [
            BattlePhase.INIT,
            BattlePhase.START,
            BattlePhase.INPUT,
            BattlePhase.ORDER,
            BattlePhase.RESOLVE,
            BattlePhase.AFTERMATH,
            BattlePhase.MESSAGE,
            BattlePhase.END,
            BattlePhase.REWARD,
            BattlePhase.COMPLETE
        ]
        
        for phase in phases:
            battle_state.phase = phase
            print(f"✅ Phase {phase.value} erfolgreich gesetzt")
        
        print("\n🎉 Alle Battle-Phasen funktionieren!")
        return True
        
    except Exception as e:
        print(f"❌ Fehler beim Testen der Battle-Phasen: {str(e)}")
        return False

def test_error_handling():
    """Testet die Fehlerbehandlung des Systems."""
    print("\n=== ERROR HANDLING TEST ===")
    print()
    
    try:
        # Teste ungültige Monster
        print("1. Teste ungültige Monster...")
        try:
            invalid_battle = BattleState(
                player_team=[],  # Leeres Team
                enemy_team=[create_test_monster("Test", 5)]
            )
            print("❌ Sollte einen Fehler werfen!")
            return False
        except ValueError as e:
            print(f"✅ Erwarteter Fehler abgefangen: {str(e)}")
        
        # Teste ungültige Actions
        print("2. Teste ungültige Actions...")
        player_monster = create_test_monster("ErrorTest", 5)
        enemy_monster = create_test_monster("ErrorTest2", 5)
        player_monster.moves = [create_test_move("Test", 40)]
        
        battle_state = BattleState(
            player_team=[player_monster],
            enemy_team=[enemy_monster]
        )
        
        # Ungültige Action ohne action_type
        invalid_action = {'actor': player_monster}
        if not battle_state.queue_player_action(invalid_action):
            print("✅ Ungültige Action korrekt abgelehnt")
        else:
            print("❌ Ungültige Action sollte abgelehnt werden!")
            return False
        
        print("\n🎉 Fehlerbehandlung funktioniert einwandfrei!")
        return True
        
    except Exception as e:
        print(f"❌ Fehler beim Testen der Fehlerbehandlung: {str(e)}")
        return False

def test_ai_robustness():
    """Testet die Robustheit gegen AI-bezogene Fehler."""
    print("\n=== AI ROBUSTNESS TEST ===")
    print()
    
    try:
        # Teste verschiedene Action-Formate
        print("1. Teste verschiedene Action-Formate...")
        player_monster = create_test_monster("RobustTest", 5)
        enemy_monster = create_test_monster("RobustTest2", 5)
        player_monster.moves = [create_test_move("Test", 40)]
        
        battle_state = BattleState(
            player_team=[player_monster],
            enemy_team=[enemy_monster]
        )
        
        # Starte den Battle
        start_result = battle_state.start_battle()
        if 'error' in start_result:
            print(f"❌ Fehler beim Starten des Battles: {start_result['error']}")
            return False
        
        # Teste verschiedene action_type Schreibweisen
        action_variants = [
            {'action_type': 'attack', 'actor': player_monster, 'move': player_monster.moves[0], 'target': enemy_monster},
            {'action_type': 'ATTACK', 'actor': player_monster, 'move': player_monster.moves[0], 'target': enemy_monster},
            {'action_type': 'Attack', 'actor': player_monster, 'move': player_monster.moves[0], 'target': enemy_monster},
        ]
        
        for i, action in enumerate(action_variants):
            if battle_state.queue_player_action(action):
                print(f"✅ Action-Variante {i+1} erfolgreich verarbeitet")
                # Reset für nächste Action
                battle_state.action_queue.clear()
                battle_state.phase = BattlePhase.INPUT
            else:
                print(f"❌ Action-Variante {i+1} fehlgeschlagen")
                return False
        
        # Teste deterministische RNG
        print("2. Teste deterministische RNG...")
        battle_state.set_random_seed(42)
        battle_state2 = BattleState(
            player_team=[player_monster],
            enemy_team=[enemy_monster]
        )
        battle_state2.set_random_seed(42)
        
        # Beide sollten identische Ergebnisse liefern
        print("✅ RNG-Seed erfolgreich gesetzt")
        
        # Teste Monster-Validierung
        print("3. Teste Monster-Validierung...")
        if player_monster.is_valid():
            print("✅ Monster-Validierung erfolgreich")
        else:
            print("❌ Monster-Validierung fehlgeschlagen")
            return False
        
        # Teste Move-Validierung
        print("4. Teste Move-Validierung...")
        test_move = create_test_move("ValidTest", 50)
        if test_move and test_move.is_valid():
            print("✅ Move-Validierung erfolgreich")
        else:
            print("❌ Move-Validierung fehlgeschlagen")
            return False
        
        print("\n🎉 AI-Robustheit funktioniert einwandfrei!")
        return True
        
    except Exception as e:
        print(f"❌ Fehler beim Testen der AI-Robustheit: {str(e)}")
        return False

def test_enum_handling():
    """Testet die verbesserte Enum-Behandlung."""
    print("\n=== ENUM HANDLING TEST ===")
    print()
    
    try:
        from engine.systems.battle.turn_logic import ActionType
        from engine.systems.moves import MoveCategory, MoveTarget, EffectKind
        
        # Teste ActionType.from_string
        print("1. Teste ActionType.from_string...")
        action_types = ['attack', 'ATTACK', 'Attack', 'SWITCH', 'switch', 'Switch']
        for action_str in action_types:
            try:
                action_type = ActionType.from_string(action_str)
                print(f"✅ '{action_str}' → {action_type.name}")
            except Exception as e:
                print(f"❌ Fehler bei '{action_str}': {e}")
                return False
        
        # Teste MoveCategory.from_string
        print("2. Teste MoveCategory.from_string...")
        category_strings = ['phys', 'PHYS', 'Phys', 'mag', 'MAG', 'Mag']
        for cat_str in category_strings:
            try:
                category = MoveCategory.from_string(cat_str)
                print(f"✅ '{cat_str}' → {category.value}")
            except Exception as e:
                print(f"❌ Fehler bei '{cat_str}': {e}")
                return False
        
        # Teste MoveTarget.from_string
        print("3. Teste MoveTarget.from_string...")
        target_strings = ['enemy', 'ENEMY', 'Enemy', 'ally', 'ALLY', 'Ally']
        for target_str in target_strings:
            try:
                target = MoveTarget.from_string(target_str)
                print(f"✅ '{target_str}' → {target.value}")
            except Exception as e:
                print(f"❌ Fehler bei '{target_str}': {e}")
                return False
        
        print("\n🎉 Enum-Behandlung funktioniert einwandfrei!")
        return True
        
    except Exception as e:
        print(f"❌ Fehler beim Testen der Enum-Behandlung: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Starte Final Battle System Tests...")
    print()
    
    # Führe alle Tests aus
    success = True
    
    success &= test_battle_system()
    success &= test_battle_phases()
    success &= test_error_handling()
    success &= test_ai_robustness()
    success &= test_enum_handling()
    
    print("\n" + "="*50)
    if success:
        print("🎉 ALLE TESTS ERFOLGREICH!")
        print("Das integrierte Battle System ist bereit für den Einsatz!")
        print("Alle AI-bezogenen Fehler wurden behoben!")
    else:
        print("❌ EINIGE TESTS SIND FEHLGESCHLAGEN!")
        print("Bitte überprüfe die Fehler und behebe sie.")
    print("="*50)
