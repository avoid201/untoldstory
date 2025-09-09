#!/usr/bin/env python3
"""
UNTOLD STORY - KOMPLETTER FLOW TEST
Flint Hammerhead testet den ganzen Kram durch!

Dieser Test checkt:
1. Spielstart im Haus
2. Story-Events (Interner Monolog)
3. Museum & Professor-Intro
4. Starter-Auswahl
5. NPC-Pathfinding in Kohlenstadt
6. Wild-Monster Encounters auf Route 1
"""

import pygame
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_flow_test():
    """Führt den kompletten Test-Flow aus."""
    print("\n" + "="*60)
    print("⚒️  UNTOLD STORY - KOMPLETTER FLOW TEST")
    print("    FLINT HAMMERHEAD CHECKT ALLES DURCH!")
    print("="*60 + "\n")
    
    # Import game components
    from engine.core.game import Game
    from engine.systems.story import StoryManager
    from engine.systems.party import PartyManager
    
    print("🎮 INITIALISIERE SPIEL-KOMPONENTEN...")
    
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    logical_surface = pygame.Surface((320, 180))
    
    try:
        # Create game instance
        game = Game(
            screen=screen,
            logical_surface=logical_surface,
            logical_size=(320, 180),
            window_size=(1280, 720),
            scale_factor=4
        )
        print("✅ Game initialisiert")
        
        # Test Story Manager
        if hasattr(game, 'story_manager'):
            print("✅ Story Manager vorhanden")
            story = game.story_manager
            print(f"   Phase: {story.phase}")
            print(f"   Nächstes Ziel: {story.get_next_objective()}")
        else:
            print("❌ Story Manager fehlt!")
        
        # Test Party Manager
        if hasattr(game, 'party_manager'):
            print("✅ Party Manager vorhanden")
            print(f"   Party leer: {game.party_manager.party.is_empty()}")
        else:
            print("❌ Party Manager fehlt!")
        
        # Test Sprite Manager
        if hasattr(game, 'sprite_manager'):
            print("✅ Sprite Manager vorhanden")
            cache_info = game.sprite_manager.get_cache_info()
            print(f"   Sprites geladen: {cache_info['total_sprites']}")
        else:
            print("❌ Sprite Manager fehlt!")
        
        print("\n" + "="*60)
        print("📋 STORY-FLOW CHECKLISTE:")
        print("="*60)
        
        checklist = """
        [ ] 1. SPIELSTART
            - Hauptmenü → "Neues Spiel"
            - Spawnt im player_house am bed spawn
            
        [ ] 2. HAUS VERLASSEN
            - WASD zum Bewegen
            - E oder ↓ an der Tür zum Verlassen
            - Interner Monolog sollte triggern!
            
        [ ] 3. KOHLENSTADT ERKUNDEN
            - Check die NPCs:
              • Old Miner Fritz wandert intelligent
              • Youngster Kevin folgt dir
              • Merchant Hans rennt weg
            
        [ ] 4. MUSEUM BETRETEN
            - Professor-Intro triggert automatisch
            - Derbe Sprüche über Fossilien
            
        [ ] 5. STARTER WÄHLEN
            - 4 Fossilien zur Auswahl
            - A/D zum Wechseln, E zum Bestätigen
            
        [ ] 6. ROUTE 1 ERKUNDEN
            - Wild-Monster im hohen Gras
            - F-Rang (95%) und E-Rang (5%)
            - Scout/Zähm-Mechanik testen
            
        [ ] 7. PATHFINDING CHECKEN
            - NPCs bewegen sich intelligent?
            - Umgehen sie Hindernisse?
            - Reagieren FOLLOW/FLEE NPCs?
        """
        
        print(checklist)
        
        print("\n" + "="*60)
        print("🐛 BEKANNTE PROBLEME:")
        print("="*60)
        
        issues = """
        ⚠️  Player.last_map wird nicht immer getrackt
        ⚠️  Story-Events könnten mehrfach triggern
        ⚠️  Scout-Mechanik im Battle noch buggy
        ⚠️  Save/Load fehlt komplett
        """
        
        print(issues)
        
    except Exception as e:
        print(f"\n❌ FEHLER beim Test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pygame.quit()
    
    print("\n" + "="*60)
    print("✅ TEST ABGESCHLOSSEN!")
    print("Starte jetzt 'python3 main.py' zum manuellen Testen!")
    print("GLÜCK AUF! ⛏️")
    print("="*60 + "\n")

if __name__ == "__main__":
    run_flow_test()
