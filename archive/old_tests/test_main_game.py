#!/usr/bin/env python3
"""
Test für das Hauptspiel mit TMX-Maps
"""

import pygame
import sys
from pathlib import Path

# Füge Projekt-Root zum Path hinzu
sys.path.insert(0, str(Path.cwd()))

def test_main_game():
    """Testet das Hauptspiel mit den gepatchten TMX-Maps"""
    
    print("=" * 60)
    print("TEST HAUPTSPIEL MIT TMX-MAPS")
    print("=" * 60)
    
    # Test 1: Prüfe ob Area-Klasse korrekt geladen werden kann
    print("\n1. Teste Area-Klasse...")
    try:
        from engine.world.area import Area
        print("   ✅ Area-Klasse kann importiert werden")
    except Exception as e:
        print(f"   ❌ Fehler beim Import: {e}")
        return
    
    # Test 2: Teste Map-Loading direkt
    print("\n2. Teste direktes Map-Loading...")
    try:
        pygame.init()
        pygame.display.set_mode((640, 480))
        
        area = Area("player_house")
        print(f"   ✅ Map 'player_house' geladen")
        
        # Prüfe ob TMX geladen wurde
        if hasattr(area, 'tmx_path') and area.tmx_path:
            print(f"   ✅ TMX-Datei verwendet: {area.tmx_path}")
        else:
            print("   ⚠️  Keine TMX-Datei gefunden, Fallback verwendet")
        
        # Prüfe Layer
        if hasattr(area, 'layer_surfaces'):
            print(f"   ✅ Layer geladen: {list(area.layer_surfaces.keys())}")
        else:
            print("   ❌ Keine Layer gefunden")
            
    except Exception as e:
        print(f"   ❌ Fehler beim Map-Loading: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Teste FieldScene-Kompatibilität
    print("\n3. Teste FieldScene-Kompatibilität...")
    try:
        from engine.scenes.field_scene import FieldScene
        from engine.core.game import Game
        
        # Erstelle minimal Game-Objekt
        screen = pygame.display.set_mode((320, 180))
        logical_surface = pygame.Surface((320, 180))
        
        game = Game(
            screen=screen,
            logical_surface=logical_surface,
            logical_size=(320, 180),
            window_size=(640, 360),
            scale_factor=2
        )
        
        # Initialisiere SpriteManager
        from engine.graphics.sprite_manager import SpriteManager
        sprite_manager = SpriteManager.get()
        game.sprite_manager = sprite_manager
        
        print("   ✅ Game-Objekt erstellt")
        
        # Erstelle FieldScene
        field_scene = FieldScene(game)
        print("   ✅ FieldScene erstellt")
        
        # Versuche Map zu laden
        field_scene.load_map("player_house")
        print("   ✅ Map in FieldScene geladen")
        
        if field_scene.current_area:
            print(f"   ✅ Area aktiv: {field_scene.current_area.map_id}")
        else:
            print("   ❌ Keine Area aktiv")
            
    except Exception as e:
        print(f"   ❌ FieldScene-Test fehlgeschlagen: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 4: Teste Rendering
    print("\n4. Teste Rendering...")
    try:
        if field_scene and field_scene.current_area:
            # Rendere einen Frame
            field_scene.draw(logical_surface)
            print("   ✅ Rendering erfolgreich")
            
            # Zeige Fenster kurz
            screen.blit(logical_surface, (0, 0))
            pygame.display.flip()
            
            # Warte kurz
            pygame.time.wait(1000)
        else:
            print("   ⚠️  Kein Rendering-Test möglich")
            
    except Exception as e:
        print(f"   ❌ Rendering fehlgeschlagen: {e}")
    
    pygame.quit()
    
    print("\n" + "=" * 60)
    print("TEST ABGESCHLOSSEN")
    print("=" * 60)
    
    print("\n📋 Zusammenfassung:")
    print("Wenn alle Tests grün sind, sollte das Hauptspiel funktionieren.")
    print("Falls nicht, prüfe die Fehlermeldungen oben.")
    print("\nStarte das Spiel mit: python3 main.py")

if __name__ == "__main__":
    test_main_game()
