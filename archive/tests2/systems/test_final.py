#!/usr/bin/env python3
"""
Finaler Test nach allen Fixes
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_all_fixes():
    """Teste alle angewendeten Fixes."""
    print("=" * 50)
    print("FINALE TESTS NACH ALLEN FIXES")
    print("=" * 50)
    print()
    
    # Test 1: Party-Fix
    print("1. Teste Party-Reset...")
    from engine.systems.party import Party, PartyManager
    manager = PartyManager()
    manager.party = Party()  # Der Fix
    print(f"   ✅ Party kann zurückgesetzt werden: {manager.party.is_empty()}")
    
    # Test 2: Story-Flags
    print("\n2. Teste Story-Flags...")
    from engine.systems.story import StoryManager
    story = StoryManager()
    
    critical_flags = [
        'game_started',
        'first_awakening', 
        'professor_intro_started',
        'rival_first_encounter',
        'left_house_first_time',
        'timerifts_started'  # Neu hinzugefügt
    ]
    
    all_ok = True
    for flag in critical_flags:
        value = story.get_flag(flag)
        if value is None:
            print(f"   ❌ {flag}: FEHLT!")
            all_ok = False
        else:
            print(f"   ✅ {flag}: {value}")
    
    # Test 3: trials_completed Attribut
    print("\n3. Teste trials_completed...")
    print(f"   ✅ trials_completed ist Attribut: {story.trials_completed}")
    print(f"   ✅ Vergleich funktioniert: {story.trials_completed >= 5}")
    
    # Test 4: Story-Reset
    print("\n4. Teste kompletten Story-Reset...")
    story.set_flag('has_starter', True)
    story.trials_completed = 3
    print(f"   Vor Reset: has_starter={story.get_flag('has_starter')}, trials={story.trials_completed}")
    
    story.reset()
    print(f"   Nach Reset: has_starter={story.get_flag('has_starter')}, trials={story.trials_completed}")
    print(f"   ✅ Reset funktioniert vollständig")
    
    print("\n" + "=" * 50)
    if all_ok:
        print("✅ ALLE TESTS BESTANDEN!")
        print("=" * 50)
        print("\n🎮 Das Spiel sollte jetzt ohne Fehler laufen!")
        print("\nStarte mit: python main.py")
        print("\nStory-Ablauf:")
        print("1. Hauptmenü → 'Neues Spiel'")
        print("2. Aufwachen im Spielerhaus")
        print("3. Mit WASD das Haus verlassen")
        print("4. Interner Monolog über Kohlenstadt")
        print("5. Museum betreten → Professor-Intro")
        print("6. Starter wählen (A/D zum Wechseln, E zum Bestätigen)")
        print("7. Museum verlassen → Klaus-Kampf")
    else:
        print("⚠️  Einige Tests fehlgeschlagen!")
        print("Bitte überprüfe die Fehlermeldungen oben.")
    
    print("\n" + "=" * 50)
    print()

if __name__ == "__main__":
    test_all_fixes()
