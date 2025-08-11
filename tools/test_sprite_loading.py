#!/usr/bin/env python3
"""
Test-Skript für Sprite-Lade-Logik
Testet die Sprite-Lade-Funktionalität des SpriteManager
"""

import sys
import os
from pathlib import Path

# Füge den engine-Ordner zum Python-Pfad hinzu
sys.path.insert(0, str(Path(__file__).parent / "engine"))

try:
    import pygame
    from graphics.sprite_manager import SpriteManager
    
    # Initialisiere pygame (ohne Display)
    pygame.init()
    
    print("🧪 Teste Sprite-Lade-Logik...")
    print("=" * 50)
    
    # Erstelle SpriteManager
    sm = SpriteManager()
    
    print("\n📊 Cache-Status:")
    cache_info = sm.get_cache_info()
    for key, value in cache_info.items():
        print(f"  {key}: {value}")
    
    print("\n🔍 Teste spezifische Tile-IDs:")
    
    # Teste die wichtigsten Tile-IDs aus den Maps
    test_tile_ids = [1, 2, 4, 5, 7, 9, 10, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38]
    
    for tile_id in test_tile_ids:
        sprite = sm.get_tile_sprite(tile_id)
        if sprite:
            print(f"  ✅ Tile ID {tile_id}: Sprite geladen ({sprite.get_size()})")
        else:
            print(f"  ❌ Tile ID {tile_id}: Kein Sprite gefunden")
    
    print("\n🏠 Teste Player House Tiles:")
    player_house_tiles = [1, 7, 9, 5, 10]
    for tile_id in player_house_tiles:
        sprite = sm.get_tile_sprite(tile_id)
        if sprite:
            print(f"  ✅ Player House Tile {tile_id}: OK")
        else:
            print(f"  ❌ Player House Tile {tile_id}: Fehlt")
    
    print("\n🏙️ Teste Kohlenstadt Tiles:")
    kohlenstadt_tiles = [2, 4, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38]
    for tile_id in kohlenstadt_tiles:
        sprite = sm.get_tile_sprite(tile_id)
        if sprite:
            print(f"  ✅ Kohlenstadt Tile {tile_id}: OK")
        else:
            print(f"  ❌ Kohlenstadt Tile {tile_id}: Fehlt")
    
    print("\n🎯 Verfügbare Sprites im Cache:")
    sprite_keys = list(sm.sprite_cache.keys())
    sprite_keys.sort()
    for i, key in enumerate(sprite_keys[:20]):  # Zeige nur die ersten 20
        print(f"  {i+1:2d}. {key}")
    
    if len(sprite_keys) > 20:
        print(f"  ... und {len(sprite_keys) - 20} weitere")
    
    print("\n✅ Test abgeschlossen!")
    
except ImportError as e:
    print(f"❌ Import-Fehler: {e}")
    print("Stelle sicher, dass du im Projektverzeichnis bist und pygame installiert ist.")
except Exception as e:
    print(f"❌ Fehler: {e}")
    import traceback
    traceback.print_exc()
