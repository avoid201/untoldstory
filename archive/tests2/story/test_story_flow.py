#!/usr/bin/env python3
"""
Test-Script für die Untold Story Startsequenz mit Ruhrpott-Vibe

Dieses Script testet:
1. Neues Spiel starten im Spielerhaus
2. Story-Events beim Verlassen des Hauses
3. Professor-Intro im Museum
4. Starter-Auswahl
5. Klaus-Kampf nach Museum-Verlassen

Verwendung:
python test_story_flow.py
"""

import pygame
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.core.game import Game
from engine.systems.story import StoryManager
from engine.systems.party import PartyManager

def test_story_initialization():
    """Teste die Story-Manager Initialisierung."""
    print("=" * 50)
    print("TESTE STORY-MANAGER INITIALISIERUNG")
    print("=" * 50)
    
    story_manager = StoryManager()
    
    # Teste wichtige Flags
    flags_to_check = [
        'game_started',
        'first_awakening', 
        'has_starter',
        'left_house_first_time',
        'professor_intro_started',
        'rival_first_encounter'
    ]
    
    for flag in flags_to_check:
        value = story_manager.get_flag(flag)
        print(f"Flag '{flag}': {value}")
    
    print("\nPhase:", story_manager.phase)
    print("Nächstes Ziel:", story_manager.get_next_objective())
    print()

def test_story_progression():
    """Teste die Story-Progression."""
    print("=" * 50)
    print("TESTE STORY-PROGRESSION")
    print("=" * 50)
    
    story_manager = StoryManager()
    
    # Simuliere Story-Progression
    print("1. Spielstart...")
    story_manager.set_flag('game_started', True)
    story_manager.set_flag('first_awakening', True)
    print(f"   Ziel: {story_manager.get_next_objective()}")
    
    print("\n2. Haus verlassen...")
    story_manager.set_flag('left_house_first_time', True)
    print(f"   Ziel: {story_manager.get_next_objective()}")
    
    print("\n3. Professor getroffen...")
    story_manager.set_flag('met_professor', True)
    print(f"   Ziel: {story_manager.get_next_objective()}")
    
    print("\n4. Starter erhalten...")
    story_manager.set_flag('has_starter', True)
    story_manager.set_flag('starter_choice', 1)  # Glutkohle
    print(f"   Ziel: {story_manager.get_next_objective()}")
    
    print("\n5. Rivale besiegt...")
    story_manager.set_flag('rival_first_encounter', True)
    story_manager.set_flag('rival_battle_1', True)
    story_manager.rival_battles_won += 1
    print(f"   Ziel: {story_manager.get_next_objective()}")
    print()

def test_dialogue_loading():
    """Teste das Laden der Ruhrpott-Dialoge."""
    print("=" * 50)
    print("TESTE DIALOG-SYSTEM")
    print("=" * 50)
    
    import json
    
    # Lade Dialoge
    with open('data/game_data/dialogues.json', 'r', encoding='utf-8') as f:
        dialogues = json.load(f)
    
    # Teste wichtige Story-Dialoge
    important_dialogues = [
        'mom_morning_wake',
        'professor_fossil_intro',
        'klaus_first_battle',
        'fossil_glutkohle',
        'fossil_tropfstein',
        'fossil_lehmling',
        'fossil_windei'
    ]
    
    for dialogue_id in important_dialogues:
        if dialogue_id in dialogues:
            dialogue = dialogues[dialogue_id]
            print(f"\n{dialogue_id}:")
            if 'text' in dialogue and dialogue['text']:
                print(f"  Erste Zeile: {dialogue['text'][0][:60]}...")
            if 'responses' in dialogue and dialogue['responses']:
                print(f"  Antworten: {dialogue['responses']}")
        else:
            print(f"\n{dialogue_id}: FEHLT!")
    print()

def test_game_flow():
    """Teste den kompletten Spielablauf."""
    print("=" * 50)
    print("TESTE SPIELABLAUF")
    print("=" * 50)
    
    print("""
    TESTING FLOW:
    1. Starte das Spiel mit 'python main.py'
    2. Wähle 'Neues Spiel' im Hauptmenü
    3. Du solltest im Spielerhaus aufwachen
    4. Verlasse das Haus → Interner Monolog über Kohlenstadt
    5. Gehe ins Museum → Professor-Intro mit derbem Dialog
    6. Wähle einen Starter (Glutkohle, Tropfstein, Lehmling oder Windei)
    7. Verlasse das Museum → Klaus spawnt und will kämpfen
    8. Nach dem Kampf kannst du frei erkunden
    
    TASTENBELEGUNG:
    - WASD: Bewegung
    - E/Enter: Interaktion
    - Tab: Debug-Modus
    - Q/Escape: Pause
    
    DEBUG-BEFEHLE (im Debug-Modus):
    - G: Grid anzeigen
    - C: Kollisionen anzeigen
    - B: Kampf erzwingen (Debug-Modus muss aktiv sein)
    """)

def main():
    """Hauptfunktion für Tests."""
    print("\n" + "=" * 50)
    print("UNTOLD STORY - RUHRPOTT STORY TEST")
    print("=" * 50 + "\n")
    
    # Teste einzelne Komponenten
    test_story_initialization()
    test_story_progression()
    test_dialogue_loading()
    test_game_flow()
    
    print("\n" + "=" * 50)
    print("TESTS ABGESCHLOSSEN!")
    print("Starte nun das Spiel mit 'python main.py' zum Testen.")
    print("=" * 50 + "\n")

if __name__ == "__main__":
    main()
