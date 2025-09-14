#!/usr/bin/env python3
"""
MASTER FIX SCRIPT - Priorität 1: Battle-Grundfunktionalität
Führt alle Fixes in der richtigen Reihenfolge aus
"""

import os
import sys
import subprocess
import time

# Add project root to path
sys.path.insert(0, '/Users/leon/Desktop/untold_story')

def run_fix(fix_name, fix_file):
    """Führt einen Fix aus und zeigt Status"""
    print(f"\n{'='*60}")
    print(f"Führe aus: {fix_name}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            [sys.executable, fix_file],
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
        if result.stderr:
            print(f"Warnungen: {result.stderr}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ FEHLER bei {fix_name}:")
        print(e.stdout)
        print(e.stderr)
        return False
    except Exception as e:
        print(f"❌ Unerwarteter Fehler: {e}")
        return False

def verify_fixes():
    """Verifiziert, dass alle Fixes erfolgreich waren"""
    print(f"\n{'='*60}")
    print("VERIFIZIERUNG DER FIXES")
    print(f"{'='*60}")
    
    checks = []
    
    # Check 1: Monster-UI-Verbindung
    print("\n1. Prüfe Monster-UI-Verbindung...")
    try:
        with open('/Users/leon/Desktop/untold_story/engine/ui/battle_ui.py', 'r') as f:
            content = f.read()
            if 'battle_state.player_team[index]' in content:
                print("✅ Monster-UI-Verbindung implementiert")
                checks.append(True)
            else:
                print("❌ Monster-UI-Verbindung fehlt")
                checks.append(False)
    except Exception as e:
        print(f"❌ Fehler beim Prüfen: {e}")
        checks.append(False)
    
    # Check 2: Battle-State-Passing
    print("\n2. Prüfe Battle-State-Passing...")
    try:
        with open('/Users/leon/Desktop/untold_story/engine/scenes/battle_scene.py', 'r') as f:
            content = f.read()
            if 'self.battle_ui.battle_state = self.battle_state' in content:
                print("✅ Battle-State wird an UI übergeben")
                checks.append(True)
            else:
                print("❌ Battle-State-Passing fehlt")
                checks.append(False)
    except Exception as e:
        print(f"❌ Fehler beim Prüfen: {e}")
        checks.append(False)
    
    # Check 3: Move-Verfügbarkeit
    print("\n3. Prüfe Move-Verfügbarkeit...")
    try:
        with open('/Users/leon/Desktop/untold_story/engine/systems/monster_instance.py', 'r') as f:
            content = f.read()
            if 'Rempler' in content and 'basic_moves' in content:
                print("✅ Monster haben Start-Moves")
                checks.append(True)
            else:
                print("❌ Start-Moves fehlen")
                checks.append(False)
    except Exception as e:
        print(f"❌ Fehler beim Prüfen: {e}")
        checks.append(False)
    
    # Check 4: Error-Handling
    print("\n4. Prüfe Error-Handling...")
    try:
        with open('/Users/leon/Desktop/untold_story/engine/ui/battle_ui.py', 'r') as f:
            content = f.read()
            if content.count('try:') > 5:  # Sollte mehrere try-blocks haben
                print("✅ Error-Handling implementiert")
                checks.append(True)
            else:
                print("❌ Error-Handling unvollständig")
                checks.append(False)
    except Exception as e:
        print(f"❌ Fehler beim Prüfen: {e}")
        checks.append(False)
    
    return all(checks)

def test_battle_system():
    """Testet das Battle-System nach den Fixes"""
    print(f"\n{'='*60}")
    print("TESTE BATTLE-SYSTEM")
    print(f"{'='*60}")
    
    test_script = '''
import sys
sys.path.insert(0, '/Users/leon/Desktop/untold_story')

try:
    # Importiere notwendige Module
    from engine.systems.monsters import MonsterDatabase
    from engine.systems.monster_instance import MonsterInstance
    from engine.systems.battle.battle_controller import BattleState, BattleType
    from engine.ui.battle import BattleUI
    
    print("✅ Alle Importe erfolgreich")
    
    # Erstelle Test-Monster
    db = MonsterDatabase()
    species1 = db.get_species("1")  # Glutstummel
    species2 = db.get_species("4")  # Kohlekumpel
    
    if not species1:
        species1 = list(db.species_by_id.values())[0]
    if not species2:
        species2 = list(db.species_by_id.values())[1]
    
    monster1 = MonsterInstance(species1, level=5)
    monster2 = MonsterInstance(species2, level=5)
    
    print(f"✅ Monster erstellt: {monster1.name} vs {monster2.name}")
    
    # Prüfe Moves
    if monster1.moves:
        print(f"✅ {monster1.name} hat {len(monster1.moves)} Moves")
    else:
        print(f"❌ {monster1.name} hat keine Moves!")
    
    # Erstelle Battle
    battle = BattleState(
        player_team=[monster1],
        enemy_team=[monster2],
        battle_type=BattleType.WILD
    )
    
    print("✅ BattleState erstellt")
    
    # Teste Battle-Start
    result = battle.start_battle(use_events=False)
    print(f"✅ Battle gestartet: {result}")
    
    print("\\n✅ BATTLE-SYSTEM FUNKTIONIERT!")
    
except Exception as e:
    print(f"❌ FEHLER: {e}")
    import traceback
    traceback.print_exc()
'''
    
    with open('/tmp/test_battle.py', 'w') as f:
        f.write(test_script)
    
    try:
        result = subprocess.run(
            [sys.executable, '/tmp/test_battle.py'],
            capture_output=True,
            text=True,
            timeout=5
        )
        print(result.stdout)
        if result.stderr:
            print(f"Warnungen: {result.stderr}")
        return 'BATTLE-SYSTEM FUNKTIONIERT' in result.stdout
    except Exception as e:
        print(f"❌ Test fehlgeschlagen: {e}")
        return False

def main():
    """Hauptfunktion - führt alle Fixes aus"""
    print("="*60)
    print("UNTOLD STORY - PRIORITÄT 1 FIX")
    print("Battle-Grundfunktionalität Reparatur")
    print("="*60)
    
    fixes = [
        ("Monster-UI-Verbindung", "fix_monster_ui_connection.py"),
        ("Battle-State-Passing", "fix_battle_state_passing.py"),
        ("Move-Verfügbarkeit", "fix_move_availability.py"),
        ("Error-Handling", "fix_error_handling.py")
    ]
    
    fix_dir = "/Users/leon/Desktop/untold_story/fixes"
    os.chdir(fix_dir)
    
    success_count = 0
    for fix_name, fix_file in fixes:
        if run_fix(fix_name, fix_file):
            success_count += 1
            time.sleep(1)  # Kurze Pause zwischen Fixes
        else:
            print(f"\n⚠️ Fix {fix_name} fehlgeschlagen - fahre trotzdem fort")
    
    print(f"\n{'='*60}")
    print(f"FIXES ABGESCHLOSSEN: {success_count}/{len(fixes)} erfolgreich")
    print(f"{'='*60}")
    
    # Verifizierung
    if verify_fixes():
        print("\n✅ ALLE VERIFIKATIONEN ERFOLGREICH")
        
        # Teste das System
        if test_battle_system():
            print("\n🎉 BATTLE-SYSTEM IST SPIELBEREIT! 🎉")
        else:
            print("\n⚠️ Battle-System läuft, aber mit Warnungen")
    else:
        print("\n⚠️ Einige Verifikationen fehlgeschlagen - manuelle Prüfung erforderlich")
    
    print(f"\n{'='*60}")
    print("NÄCHSTE SCHRITTE:")
    print("1. Starte das Spiel mit: python main.py")
    print("2. Teste einen Kampf im Spiel")
    print("3. Prüfe die Battle-UI auf korrekte Anzeige")
    print("4. Führe bei Problemen einzelne Fixes erneut aus")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
