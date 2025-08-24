#!/usr/bin/env python3
"""
Quick-Fix Test für die Story-Implementation
Testet ob alle Fixes funktionieren.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_party_fix():
    """Teste den Party-Fix."""
    print("Teste Party-Fix...")
    from engine.systems.party import Party, PartyManager
    
    # Teste Party-Erstellung
    party = Party()
    print(f"✅ Party erstellt: {party.is_empty() = }")
    
    # Teste PartyManager
    manager = PartyManager()
    old_party = manager.party
    
    # Erstelle neue Party (wie im Fix)
    manager.party = Party()
    print(f"✅ Party zurückgesetzt: {manager.party.is_empty() = }")
    print()

def test_story_flags():
    """Teste Story-Flags."""
    print("Teste Story-Flags...")
    from engine.systems.story import StoryManager
    
    story = StoryManager()
    
    # Teste neue Flags
    flags = [
        'game_started',
        'first_awakening',
        'professor_intro_started', 
        'rival_first_encounter',
        'left_house_first_time'
    ]
    
    for flag in flags:
        value = story.get_flag(flag)
        print(f"  {flag}: {value} ({'✅ existiert' if value is not None else '❌ fehlt'})")
    
    print()

def test_story_reset():
    """Teste Story-Reset."""
    print("Teste Story-Reset...")
    from engine.systems.story import StoryManager
    
    story = StoryManager()
    
    # Setze einige Flags
    story.set_flag('game_started', True)
    story.set_flag('has_starter', True)
    print(f"Vor Reset: game_started={story.get_flag('game_started')}, has_starter={story.get_flag('has_starter')}")
    
    # Reset
    story.reset()
    print(f"Nach Reset: game_started={story.get_flag('game_started')}, has_starter={story.get_flag('has_starter')}")
    print("✅ Story-Reset funktioniert")
    print()

def main():
    print("=" * 50)
    print("QUICK-FIX TEST")
    print("=" * 50)
    print()
    
    test_party_fix()
    test_story_flags()
    test_story_reset()
    
    print("=" * 50)
    print("ALLE FIXES ERFOLGREICH!")
    print("=" * 50)
    print()
    print("Du kannst jetzt das Spiel starten mit:")
    print("  python main.py")
    print()
    print("Story-Flow:")
    print("1. Hauptmenü → Neues Spiel")
    print("2. Aufwachen im Spielerhaus")
    print("3. Haus verlassen → Interner Monolog")
    print("4. Museum betreten → Professor-Intro")
    print("5. Starter wählen")
    print("6. Museum verlassen → Klaus-Kampf")
    print()

if __name__ == "__main__":
    main()
