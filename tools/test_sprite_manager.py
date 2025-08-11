#!/usr/bin/env python3
"""Test-Skript für die Sprite-Validierung"""

import pygame
import sys
import os

# Füge den graphics-Ordner zum Python-Pfad hinzu
current_dir = os.path.dirname(os.path.abspath(__file__))
graphics_dir = os.path.join(current_dir, "graphics")
sys.path.insert(0, graphics_dir)

try:
    from sprite_manager import SpriteManager
except ImportError:
    print("❌ Konnte SpriteManager nicht importieren. Überprüfe den Pfad.")
    sys.exit(1)

def test_sprite_loading():
    """Testet das Laden der Sprites"""
    print("🚀 Starte Sprite-Loading-Test...")
    
    # Initialisiere Pygame
    pygame.init()
    
    try:
        # Erstelle SpriteManager
        sprite_manager = SpriteManager()
        
        # Hole Cache-Informationen
        cache_info = sprite_manager.get_cache_info()
        
        print("\n📊 Sprite-Cache-Status:")
        print(f"  Gesamt-Sprites: {cache_info['total_sprites']}")
        print(f"  Tile-Mappings: {cache_info['tile_mappings']}")
        print(f"  Monster-Sprites: {cache_info['monster_sprites']}")
        print(f"  NPC-Sprites: {cache_info['npc_sprites']}")
        
        print("\n🔍 Erste 10 geladene Sprites:")
        for sprite_name in cache_info['sprite_names']:
            print(f"  - {sprite_name}")
        
        print("\n🎯 Erste 10 Tile-IDs:")
        for tile_id in cache_info['tile_ids']:
            tile_info = sprite_manager.get_tile_info(int(tile_id))
            sprite_file = tile_info.get("sprite_file") if tile_info else "unbekannt"
            print(f"  - Tile {tile_id}: {sprite_file}")
        
        # Teste einige spezifische Tiles
        print("\n🧪 Teste spezifische Tiles:")
        test_tiles = [1, 5, 6, 21, 25]
        for tile_id in test_tiles:
            sprite = sprite_manager.get_tile_sprite(tile_id)
            tile_info = sprite_manager.get_tile_info(tile_id)
            if sprite:
                print(f"  ✅ Tile {tile_id} ({tile_info.get('name', 'unbekannt')}): Sprite gefunden")
            else:
                print(f"  ❌ Tile {tile_id} ({tile_info.get('name', 'unbekannt')}): Kein Sprite")
        
        print("\n🎉 Test abgeschlossen!")
        
    except Exception as e:
        print(f"❌ Fehler beim Testen: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        pygame.quit()

if __name__ == "__main__":
    test_sprite_loading()
