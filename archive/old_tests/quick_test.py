#!/usr/bin/env python3
"""
Quick Test für TMX Tile Loading
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import pygame
from engine.graphics.sprite_manager import SpriteManager

def quick_test():
    """Schneller Test ob Tiles geladen werden"""
    
    print("🔍 Quick Tile Loading Test")
    print("=" * 50)
    
    # Initialisiere pygame
    pygame.init()
    pygame.display.set_mode((1, 1))  # Minimal für Surface-Loading
    
    # Initialisiere SpriteManager
    sprite_manager = SpriteManager.get()
    
    # Lade player_house Tilesets
    tmx_path = Path("data/maps/player_house.tmx")
    print(f"\n📋 Lade Tilesets aus: {tmx_path}")
    sprite_manager.load_tmx_tilesets(tmx_path)
    
    # Teste spezifische GIDs aus der Map
    test_cases = [
        (6, "Fenster (Building)"),
        (13, "Boden (Interior)"),
        (14, "Wand (Interior)"),
        (15, "Tür (Interior)"),
        (16, "Möbel 1"),
        (17, "Möbel 2"),
        (18, "Möbel 3"),
        (19, "Möbel 4"),
        (21, "Pflanze")
    ]
    
    print("\n📊 Teste GIDs:")
    success_count = 0
    
    for gid, description in test_cases:
        surface = sprite_manager.get_tile_by_gid(gid)
        if surface:
            print(f"  ✅ GID {gid:2d}: {description} - OK ({surface.get_size()})")
            success_count += 1
        else:
            print(f"  ❌ GID {gid:2d}: {description} - FEHLT")
    
    print(f"\n📈 Ergebnis: {success_count}/{len(test_cases)} Tiles geladen")
    
    if hasattr(sprite_manager, 'gid_to_surface'):
        total_gids = len(sprite_manager.gid_to_surface)
        print(f"💾 Gesamt im Cache: {total_gids} GIDs")
        
        if total_gids > 0:
            print(f"   Verfügbare GIDs: {sorted(sprite_manager.gid_to_surface.keys())}")
    
    if success_count == len(test_cases):
        print("\n✅ Alle Tiles erfolgreich geladen!")
        return True
    else:
        print("\n⚠️ Einige Tiles fehlen noch.")
        return False

if __name__ == "__main__":
    success = quick_test()
    
    if success:
        print("\n💡 Du kannst jetzt das Spiel starten:")
        print("   python3 main.py")
        print("\nOder die Map anschauen:")
        print("   python3 view_map.py")
    else:
        print("\n💡 Debug-Tipps:")
        print("1. Prüfe ob die Tileset-Bilder existieren:")
        print("   ls assets/gfx/tiles/tilesets/")
        print("2. Führe das Debug-Skript aus:")
        print("   python3 debug_tilesets.py")
