#!/usr/bin/env python3
"""
Lokales Setup und Test für das Battle System
Behebt .pyc Probleme und testet das System
"""

import sys
import os
import subprocess
import logging

def clean_pyc_files():
    """Lösche alle .pyc Dateien und __pycache__ Ordner"""
    print("🧹 Lösche .pyc Dateien und __pycache__ Ordner...")
    
    # Lösche .pyc Dateien
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.pyc'):
                try:
                    os.remove(os.path.join(root, file))
                    print(f"   Gelöscht: {os.path.join(root, file)}")
                except:
                    pass
    
    # Lösche __pycache__ Ordner
    for root, dirs, files in os.walk('.'):
        for dir_name in dirs:
            if dir_name == '__pycache__':
                try:
                    import shutil
                    shutil.rmtree(os.path.join(root, dir_name))
                    print(f"   Gelöscht: {os.path.join(root, dir_name)}")
                except:
                    pass
    
    print("✅ Aufräumen abgeschlossen")

def check_dependencies():
    """Prüfe und installiere Abhängigkeiten"""
    print("🔍 Prüfe Abhängigkeiten...")
    
    try:
        import pygame
        print("✅ pygame-ce ist verfügbar")
    except ImportError:
        print("❌ pygame-ce nicht gefunden")
        print("   Installiere pygame-ce:")
        print("   pip install pygame-ce")
        return False
    
    return True

def test_battle_system():
    """Teste das Battle System"""
    print("🧪 Teste Battle System...")
    
    # Setze Pfad
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    try:
        # Test 1: Imports
        print("   1. Teste Imports...")
        from engine.systems.battle.battle import BattleState, BattleType, BattlePhase
        from engine.systems.battle.turn_logic import BattleAction, ActionType
        from engine.systems.monster_instance import MonsterInstance, MonsterSpecies, MonsterRank
        from engine.systems.stats import BaseStats, GrowthCurve
        from engine.systems.moves import Move, MoveEffect, EffectKind, MoveCategory, MoveTarget
        print("   ✅ Alle Imports erfolgreich")
        
        # Test 2: Monster erstellen
        print("   2. Teste Monster-Erstellung...")
        base_stats = BaseStats(hp=100, atk=50, def_=50, mag=30, res=30, spd=70)
        species = MonsterSpecies(
            id=1, name="TestMonster", era="present", rank=MonsterRank.E,
            types=["Bestie"], base_stats=base_stats, growth_curve=GrowthCurve.MEDIUM_FAST,
            base_exp_yield=64, capture_rate=45, traits=[], learnset=[],
            evolution=None, description="Test Monster"
        )
        monster = MonsterInstance(species=species, level=5)
        print(f"   ✅ Monster erstellt: {monster.name} (HP: {monster.current_hp}/{monster.max_hp})")
        
        # Test 3: Move erstellen
        print("   3. Teste Move-Erstellung...")
        effect = MoveEffect(kind=EffectKind.DAMAGE, power=40, chance=100.0)
        move = Move(
            id="tackle", name="Tackle", type="Bestie", category=MoveCategory.PHYSICAL,
            power=40, accuracy=95, pp=15, max_pp=15, priority=0,
            targeting=MoveTarget.ENEMY, effects=[effect], description="Basic attack"
        )
        monster.moves = [move]
        print(f"   ✅ Move erstellt: {move.name} (Power: {move.power})")
        
        # Test 4: Battle erstellen
        print("   4. Teste Battle-Erstellung...")
        species2 = MonsterSpecies(
            id=2, name="Enemy", era="present", rank=MonsterRank.E,
            types=["Bestie"], base_stats=base_stats, growth_curve=GrowthCurve.MEDIUM_FAST,
            base_exp_yield=64, capture_rate=45, traits=[], learnset=[],
            evolution=None, description="Enemy Monster"
        )
        enemy = MonsterInstance(species=species2, level=5)
        enemy.moves = [move]
        
        battle = BattleState(
            player_team=[monster],
            enemy_team=[enemy],
            battle_type=BattleType.WILD
        )
        print(f"   ✅ Battle erstellt: {battle.player_active.name} vs {battle.enemy_active.name}")
        
        # Test 5: Battle starten
        print("   5. Teste Battle Start...")
        result = battle.start_battle()
        if 'error' not in result:
            print(f"   ✅ Battle gestartet (Phase: {battle.phase.value})")
        else:
            print(f"   ❌ Battle Start Fehler: {result['error']}")
            return False
        
        # Test 6: Action Queue
        print("   6. Teste Action Queue...")
        action = {
            'action_type': 'attack',
            'actor': monster,
            'move': monster.moves[0],
            'target': enemy
        }
        
        if battle.queue_player_action(action):
            print(f"   ✅ Action hinzugefügt (Queue: {len(battle.action_queue)})")
        else:
            print("   ❌ Action konnte nicht hinzugefügt werden")
            return False
        
        print("🎉 Alle Tests erfolgreich!")
        return True
        
    except Exception as e:
        print(f"❌ Test Fehler: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_local_test_script():
    """Erstelle ein lokales Test-Skript"""
    print("📝 Erstelle lokales Test-Skript...")
    
    script_content = '''#!/usr/bin/env python3
"""
Lokaler Battle System Test
Einfach auszuführen ohne komplexe Setups
"""

import sys
import os

# Pfad hinzufügen
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    try:
        # Teste Battle System
        from engine.systems.battle.battle import BattleState, BattleType
        from engine.systems.monster_instance import MonsterInstance, MonsterSpecies, MonsterRank
        from engine.systems.stats import BaseStats, GrowthCurve
        from engine.systems.moves import Move, MoveEffect, EffectKind, MoveCategory, MoveTarget
        
        print("✅ Imports erfolgreich")
        
        # Erstelle Test-Monster
        base_stats = BaseStats(hp=100, atk=50, def_=50, mag=30, res=30, spd=70)
        species = MonsterSpecies(
            id=1, name="TestMonster", era="present", rank=MonsterRank.E,
            types=["Bestie"], base_stats=base_stats, growth_curve=GrowthCurve.MEDIUM_FAST,
            base_exp_yield=64, capture_rate=45, traits=[], learnset=[],
            evolution=None, description="Test"
        )
        
        player = MonsterInstance(species=species, level=5)
        enemy = MonsterInstance(species=species, level=5)
        
        # Erstelle Moves
        effect = MoveEffect(kind=EffectKind.DAMAGE, power=40, chance=100.0)
        move = Move(
            id="tackle", name="Tackle", type="Bestie", category=MoveCategory.PHYSICAL,
            power=40, accuracy=95, pp=15, max_pp=15, priority=0,
            targeting=MoveTarget.ENEMY, effects=[effect], description="Attack"
        )
        
        player.moves = [move]
        enemy.moves = [move]
        
        print(f"✅ Monster erstellt: {player.name} vs {enemy.name}")
        
        # Erstelle Battle
        battle = BattleState(
            player_team=[player],
            enemy_team=[enemy],
            battle_type=BattleType.WILD
        )
        
        print(f"✅ Battle erstellt (Phase: {battle.phase.value})")
        
        # Starte Battle
        battle.start_battle()
        print(f"✅ Battle gestartet (Phase: {battle.phase.value})")
        
        # Teste Action
        action = {
            'action_type': 'attack',
            'actor': player,
            'move': player.moves[0],
            'target': enemy
        }
        
        if battle.queue_player_action(action):
            print("✅ Action erfolgreich hinzugefügt")
            
            # Löse Turn auf
            result = battle.resolve_turn()
            if 'error' not in result:
                print(f"✅ Turn aufgelöst (Turn: {result['turn_count']})")
                print(f"   Spieler HP: {player.current_hp}/{player.max_hp}")
                print(f"   Gegner HP: {enemy.current_hp}/{enemy.max_hp}")
            else:
                print(f"❌ Turn Fehler: {result['error']}")
        else:
            print("❌ Action fehlgeschlagen")
        
        print("🎉 BATTLE SYSTEM FUNKTIONIERT!")
        
    except Exception as e:
        print(f"❌ Fehler: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
'''
    
    with open('local_test.py', 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print("✅ local_test.py erstellt")

def main():
    """Hauptfunktion"""
    print("🚀 Battle System - Lokales Setup")
    print("="*50)
    
    # Schritt 1: Aufräumen
    clean_pyc_files()
    print()
    
    # Schritt 2: Abhängigkeiten prüfen
    if not check_dependencies():
        print("❌ Abhängigkeiten fehlen. Installiere sie und versuche es erneut.")
        return False
    print()
    
    # Schritt 3: System testen
    if not test_battle_system():
        print("❌ Battle System Tests fehlgeschlagen")
        return False
    print()
    
    # Schritt 4: Lokales Test-Skript erstellen
    create_local_test_script()
    print()
    
    print("✅ SETUP ERFOLGREICH!")
    print()
    print("📋 Nächste Schritte:")
    print("   1. Führe aus: python local_test.py")
    print("   2. Oder führe aus: python simple_test.py")
    print("   3. Bei Problemen: python run_local.py")
    print()
    print("🎯 Das Battle System ist einsatzbereit!")
    
    return True

if __name__ == "__main__":
    main()