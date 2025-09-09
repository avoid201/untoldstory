#!/usr/bin/env python3
"""
Test-Script für Pathfinding NPCs - FLINT HAMMERHEAD EDITION
Testet die neuen intelligenten NPC-Movement-Patterns!

Verwendung:
python3 test_pathfinding_npcs.py
"""

import pygame
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.core.game import Game
from engine.scenes.field_scene import FieldScene
from engine.world.npc import MovementPattern

def test_pathfinding_setup():
    """Teste ob Pathfinding richtig eingebaut is."""
    print("=" * 50)
    print("🔨 TESTE PATHFINDING-SETUP - FLINT WAR HIER!")
    print("=" * 50)
    
    # Check ob PathfindingMixin existiert
    try:
        from engine.world.pathfinding_mixin import PathfindingMixin
        print("✅ PathfindingMixin gefunden!")
        
        # Check Methoden
        methods = ['find_path_to', 'follow_path', 'wander_with_pathfinding', 
                  'follow_player', 'patrol_with_pathfinding']
        for method in methods:
            if hasattr(PathfindingMixin, method):
                print(f"  ✓ {method} vorhanden")
            else:
                print(f"  ✗ {method} FEHLT!")
    except ImportError as e:
        print(f"❌ PathfindingMixin konnte nicht geladen werden: {e}")
    
    print()

def test_npc_patterns():
    """Teste die verschiedenen Movement-Patterns."""
    print("=" * 50)
    print("🎮 TESTE NPC MOVEMENT-PATTERNS")
    print("=" * 50)
    
    from engine.world.npc import MovementPattern
    
    patterns = {
        "STATIC": "NPC bleibt stehen (langweilig)",
        "RANDOM": "Zufällige Bewegung (alter Kram)",
        "PATROL": "Festgelegte Route (okay)",
        "WANDER": "🆕 Intelligentes Wandern mit A*!",
        "FOLLOW": "🆕 Folgt dem Spieler!",
        "FLEE": "🆕 Rennt vor'm Spieler weg!"
    }
    
    for pattern_name, description in patterns.items():
        if hasattr(MovementPattern, pattern_name):
            print(f"✅ {pattern_name}: {description}")
        else:
            print(f"❌ {pattern_name} fehlt!")
    
    print()

def test_npc_configuration():
    """Teste die NPC-Konfiguration in Kohlenstadt."""
    print("=" * 50)
    print("📋 TESTE NPC-KONFIGURATION")
    print("=" * 50)
    
    import json
    
    # Lade NPC-Daten
    with open('data/game_data/npcs.json', 'r', encoding='utf-8') as f:
        npcs_data = json.load(f)
    
    kohlenstadt_npcs = npcs_data.get('kohlenstadt', {})
    
    print(f"Kohlenstadt hat {len(kohlenstadt_npcs)} NPCs:\n")
    
    for npc_name, npc_config in kohlenstadt_npcs.items():
        pattern = npc_config.get('movement_pattern', 'static')
        position = npc_config.get('position', [0, 0])
        
        # Highlight neue Patterns
        if pattern in ['wander', 'follow', 'flee']:
            print(f"  🆕 {npc_name}: {pattern.upper()} @ {position}")
        else:
            print(f"     {npc_name}: {pattern} @ {position}")
    
    print()

def test_game_instructions():
    """Zeige Anleitung zum Testen."""
    print("=" * 50)
    print("🎯 TEST-ANLEITUNG FÜR PATHFINDING")
    print("=" * 50)
    
    print("""
    SO TESTEST DU DIE NEUEN NPC-PATTERNS:
    
    1. Starte das Spiel mit 'python3 main.py'
    2. Neues Spiel → Haus verlassen → Kohlenstadt
    
    DANN CHECK DIE NPCS:
    
    🚶 OLD MINER FRITZ (Position: 15,20)
       → WANDER-Pattern: Läuft intelligent rum mit Pathfinding
       → Umgeht Hindernisse automatisch!
    
    👦 YOUNGSTER KEVIN (Position: 10,30)  
       → FOLLOW-Pattern: Folgt dir wie'n Hund!
       → Hält Abstand von 2-5 Tiles
    
    🏪 MERCHANT HANS (Position: 14,8)
       → FLEE-Pattern: Rennt vor dir weg!
       → Schüchterner Typ, wa?
    
    🔍 DEBUG-MODUS:
       TAB - Debug an/aus
       G   - Grid anzeigen
       
    PROBLEME CHECKEN:
    - Schaue in der Konsole nach "[PathfindingMixin]" Meldungen
    - Check ob NPCs sich bewegen (dauert paar Sekunden)
    - Bei Problemen: Sind die Collision-Layer richtig?
    """)
    
    print()

def main():
    """Hauptfunktion für Tests."""
    print("\n" + "=" * 50)
    print("⚒️  UNTOLD STORY - PATHFINDING TEST")
    print("    FLINT HAMMERHEAD MACHT DAS KLAR!")
    print("=" * 50 + "\n")
    
    # Teste Komponenten
    test_pathfinding_setup()
    test_npc_patterns()
    test_npc_configuration()
    test_game_instructions()
    
    print("=" * 50)
    print("✅ TESTS ABGESCHLOSSEN!")
    print("Jetzt ab ins Spiel und die NPCs angucken!")
    print("GLÜCK AUF! 🔨")
    print("=" * 50 + "\n")

if __name__ == "__main__":
    main()
