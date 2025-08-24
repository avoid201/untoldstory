#!/usr/bin/env python3
"""
Test-Script für vollständigen Story-Flow
Nach allen Fixes - Test der kompletten Story-Sequenz
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_story_ready():
    """Teste ob alle Story-Komponenten bereit sind."""
    print("=" * 70)
    print("STORY-KOMPONENTEN TEST")
    print("=" * 70)
    print()
    
    # 1. Story Manager
    print("1. Story Manager:")
    from engine.systems.story import StoryManager
    story = StoryManager()
    
    critical_flags = [
        'game_started', 'first_awakening', 'has_starter',
        'left_house_first_time', 'professor_intro_started',
        'rival_first_encounter', 'timerifts_started'
    ]
    
    all_flags_ok = True
    for flag in critical_flags:
        value = story.get_flag(flag)
        status = "✅" if value is not None else "❌"
        print(f"   {status} {flag}: {value}")
        if value is None:
            all_flags_ok = False
    
    # 2. Player mit last_map
    print("\n2. Player-Tracking:")
    from engine.world.player import Player
    player = Player(0, 0)
    
    has_last_map = hasattr(player, 'last_map')
    print(f"   {'✅' if has_last_map else '❌'} Player hat last_map Attribut: {has_last_map}")
    if has_last_map:
        print(f"   → Initial: {player.last_map}")
    
    # 3. Party Manager
    print("\n3. Party Manager:")
    from engine.systems.party import PartyManager, Party
    manager = PartyManager()
    
    # Test Party-Reset
    old_party = manager.party
    manager.party = Party()
    print(f"   ✅ Party kann zurückgesetzt werden")
    print(f"   → Party ist leer: {manager.party.is_empty()}")
    
    # 4. Dialoge
    print("\n4. Story-Dialoge:")
    import json
    with open('data/game_data/dialogues.json', 'r', encoding='utf-8') as f:
        dialogues = json.load(f)
    
    story_dialogues = [
        'mom_morning_wake',
        'professor_fossil_intro',
        'klaus_first_battle',
        'fossil_glutkohle'
    ]
    
    for dialogue_id in story_dialogues:
        exists = dialogue_id in dialogues
        status = "✅" if exists else "❌"
        print(f"   {status} {dialogue_id}: {'vorhanden' if exists else 'FEHLT'}")
    
    print("\n" + "=" * 70)
    
    if all_flags_ok and has_last_map:
        print("✅ ALLE KOMPONENTEN BEREIT!")
        print("\n🎮 STORY-FLOW ANLEITUNG:")
        print("=" * 70)
        print()
        print("1. SPIEL STARTEN:")
        print("   python main.py")
        print()
        print("2. HAUPTMENÜ:")
        print("   → 'Neues Spiel' wählen")
        print()
        print("3. SPIELERHAUS:")
        print("   → Du wachst am Bett auf")
        print("   → Optional: Mit Mutter (NPC) interagieren")
        print("   → Haus durch Tür verlassen (nach unten gehen)")
        print()
        print("4. KOHLENSTADT:")
        print("   → [Story] sollte triggern: 'Erstes Mal Haus verlassen'")
        print("   → Interner Monolog über Kohlenstadt")
        print("   → Museum suchen und betreten")
        print()
        print("5. MUSEUM:")
        print("   → [Story] sollte triggern: 'Professor-Intro'")
        print("   → Professor Budde's derbe Einführung")
        print("   → Am Ende: Wechsel zur Starter-Auswahl")
        print()
        print("6. STARTER-AUSWAHL:")
        print("   → A/D: Zwischen Startern wechseln")
        print("   → E: Starter bestätigen")
        print("   → Nach Auswahl: Zurück zum Museum")
        print()
        print("7. MUSEUM VERLASSEN:")
        print("   → Zurück nach Kohlenstadt")
        print("   → [Story] sollte triggern: 'Klaus Kampf'")
        print("   → Klaus spawnt und fordert zum Kampf")
        print()
        print("TASTENBELEGUNG:")
        print("   WASD - Bewegung")
        print("   E    - Interaktion/Bestätigen")
        print("   Q    - Abbrechen/Pause")
        print("   TAB  - Debug-Modus")
        print()
        print("DEBUG-OUTPUT:")
        print("   [Story] Map-Wechsel: ... → ...")
        print("   [Story] Triggere: ...")
        print("   [StarterScene] ...")
        print()
    else:
        print("⚠️  EINIGE KOMPONENTEN FEHLEN!")
        print("Bitte überprüfe die Fehler oben.")
    
    print("=" * 70)
    print()

if __name__ == "__main__":
    test_story_ready()
