#!/usr/bin/env python3
"""
Test des neuen Tile-Systems mit JSON-Maps und individuellen Tiles
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pygame
from engine.graphics.sprite_manager import SpriteManager
from engine.graphics.tile_renderer import TileRenderer
from engine.world.map_loader import MapLoader

def test_sprite_manager():
    """Testet den SpriteManager mit den neuen individuellen Tiles"""
    print("🧪 Teste SpriteManager...")
    
    # Initialisiere pygame
    pygame.init()
    pygame.display.set_mode((320, 180))
    
    # Erstelle SpriteManager
    sprite_manager = SpriteManager.get()
    
    # Lade alle Sprites
    sprite_manager._ensure_loaded()
    
    # Prüfe geladene Tiles
    print(f"✅ Geladene Tiles: {len(sprite_manager._tiles)}")
    print(f"✅ Geladene Objects: {len(sprite_manager._objects)}")
    print(f"✅ Geladene Player: {len(sprite_manager._player_dir_map)}")
    print(f"✅ Geladene NPCs: {len(sprite_manager._npc_dir_map)}")
    print(f"✅ Geladene Monster: {len(sprite_manager._monster)}")
    
    # Teste einige spezifische Tiles
    test_tiles = ["grass", "path", "water", "tree_small"]
    for tile_name in test_tiles:
        tile_sprite = sprite_manager.get_tile(tile_name)
        if tile_sprite:
            print(f"✅ Tile '{tile_name}' geladen: {tile_sprite.get_size()}")
        else:
            print(f"❌ Tile '{tile_name}' nicht gefunden")
    
    # Teste Cache-Info
    cache_info = sprite_manager.get_cache_info()
    print(f"✅ Cache-Info: {cache_info['total_sprites']} Sprites geladen")
    
    return sprite_manager

def test_map_loader():
    """Testet den MapLoader mit den neuen JSON-Maps"""
    print("\n🧪 Teste MapLoader...")
    
    # Teste das Laden verschiedener Maps
    test_maps = ["kohlenstadt", "bergmannsheil", "player_house"]
    
    for map_id in test_maps:
        try:
            map_data = MapLoader.load_map(map_id)
            print(f"✅ Map '{map_id}' geladen:")
            print(f"   - Größe: {map_data.width}x{map_data.height}")
            print(f"   - Tile-Größe: {map_data.tile_size}")
            print(f"   - Layer: {list(map_data.layers.keys())}")
            print(f"   - Warps: {len(map_data.warps)}")
            print(f"   - Triggers: {len(map_data.triggers)}")
        except Exception as e:
            print(f"❌ Fehler beim Laden von Map '{map_id}': {e}")

def test_tile_renderer(sprite_manager):
    """Testet den TileRenderer mit den neuen Tiles"""
    print("\n🧪 Teste TileRenderer...")
    
    # Erstelle TileRenderer
    tile_renderer = TileRenderer(sprite_manager)
    
    # Teste das Rendern eines einfachen Tiles
    test_tile = sprite_manager.get_tile("grass")
    if test_tile:
        print(f"✅ Test-Tile geladen: {test_tile.get_size()}")
        
        # Erstelle eine Test-Surface
        test_surface = pygame.Surface((64, 64))
        test_surface.fill((0, 0, 0))
        
        # Teste das Rendern
        try:
            # Rendere ein einzelnes Tile
            test_surface.blit(test_tile, (0, 0))
            print("✅ Tile erfolgreich gerendert")
        except Exception as e:
            print(f"❌ Fehler beim Rendern: {e}")
    else:
        print("❌ Test-Tile konnte nicht geladen werden")

def test_tile_mapping():
    """Testet das Tile-Mapping-System"""
    print("\n🧪 Teste Tile-Mapping...")
    
    sprite_manager = SpriteManager.get()
    
    # Teste einige Tile-IDs aus dem Mapping
    test_ids = ["1", "11", "15", "26"]
    
    for tile_id in test_ids:
        # Versuche über das Mapping zu laden
        tile_sprite = sprite_manager.get_tile_by_mapping(tile_id)
        if tile_sprite:
            print(f"✅ Tile-ID '{tile_id}' über Mapping geladen: {tile_sprite.get_size()}")
        else:
            print(f"❌ Tile-ID '{tile_id}' über Mapping nicht gefunden")
        
        # Versuche direkt über den Namen zu laden
        tile_info = sprite_manager.get_tile_info(tile_id)
        if tile_info:
            sprite_file = tile_info.get("sprite_file", "")
            tile_name = sprite_file.replace(".png", "").lower()
            direct_sprite = sprite_manager.get_tile(tile_name)
            if direct_sprite:
                print(f"   ✅ Direkt über Namen '{tile_name}' geladen")
            else:
                print(f"   ❌ Direkt über Namen '{tile_name}' nicht gefunden")

def main():
    """Hauptfunktion für alle Tests"""
    print("🚀 Starte Tests des neuen Tile-Systems...")
    
    try:
        # Teste SpriteManager
        sprite_manager = test_sprite_manager()
        
        # Teste MapLoader
        test_map_loader()
        
        # Teste TileRenderer
        test_tile_renderer(sprite_manager)
        
        # Teste Tile-Mapping
        test_tile_mapping()
        
        print("\n🎉 Alle Tests abgeschlossen!")
        
    except Exception as e:
        print(f"\n💥 Fehler während der Tests: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        pygame.quit()

if __name__ == "__main__":
    main()
