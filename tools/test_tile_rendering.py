#!/usr/bin/env python3
"""
Test-Skript für Tile-Rendering
Testet die neue Funktionalität für furniture_placement und decoration Arrays
"""

import sys
import os
from pathlib import Path

# Füge die Projektwurzel zum Python-Pfad hinzu, damit `engine.*` importierbar ist
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

try:
    import pygame
    from engine.graphics.sprite_manager import SpriteManager
    from engine.graphics.tile_renderer import TileRenderer
    
    # Initialisiere pygame (ohne Display)
    pygame.init()
    # Headless-Display für convert()/convert_alpha()
    try:
        pygame.display.set_mode((1, 1))
    except Exception:
        pass
    
    print("🧪 Teste Tile-Rendering mit furniture_placement und decoration...")
    print("=" * 60)
    
    # Erstelle SpriteManager
    sm = SpriteManager()
    
    # Erstelle TileRenderer
    tr = TileRenderer(sm)
    
    # Erstelle eine Test-Kamera (Dummy)
    class DummyCamera:
        def __init__(self):
            self.position = (0, 0)
    
    camera = DummyCamera()
    
    # Lade Test-Map-Daten
    test_map_data = {
        "id": "test_map",
        "name": "Test Map",
        "size": {"w": 10, "h": 10, "tile": 64},
        "layers": {
            "ground": [
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
            ],
            "decor": [
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            ]
        },
        "furniture_placement": [
            {"x": 2, "y": 2, "tile_id": 21, "name": "Computer"},
            {"x": 3, "y": 2, "tile_id": 22, "name": "Computer"},
            {"x": 2, "y": 3, "tile_id": 23, "name": "Computer"},
            {"x": 3, "y": 3, "tile_id": 24, "name": "Computer"},
            {"x": 6, "y": 4, "tile_id": 25, "name": "Bücherregal"},
            {"x": 7, "y": 4, "tile_id": 26, "name": "Bücherregal"}
        ],
        "decoration": [
            {"x": 1, "y": 1, "tile_id": 33, "name": "Kunst"},
            {"x": 8, "y": 1, "tile_id": 34, "name": "Kunst"},
            {"x": 1, "y": 8, "tile_id": 35, "name": "Kunst"},
            {"x": 8, "y": 8, "tile_id": 36, "name": "Kunst"}
        ]
    }
    
    print("\n📊 Test-Map-Daten:")
    print(f"  Ground Layer: {len(test_map_data['layers']['ground'])}x{len(test_map_data['layers']['ground'][0])}")
    print(f"  Furniture: {len(test_map_data['furniture_placement'])} Objekte")
    print(f"  Decoration: {len(test_map_data['decoration'])} Objekte")
    
    print("\n🔍 Teste Tile-Sprite-Zugriff:")
    
    # Teste Standard-Tiles
    for tile_id in [1, 2, 4, 5, 7, 9, 10]:
        sprite = sm.get_tile_sprite(tile_id)
        if sprite:
            print(f"  ✅ Tile {tile_id}: Sprite geladen ({sprite.get_size()})")
        else:
            print(f"  ❌ Tile {tile_id}: Kein Sprite gefunden")
    
    # Teste Furniture-Tiles
    for furniture in test_map_data["furniture_placement"]:
        tile_id = furniture["tile_id"]
        sprite = sm.get_tile_sprite(tile_id)
        if sprite:
            print(f"  ✅ Furniture {tile_id} ({furniture['name']}): Sprite geladen ({sprite.get_size()})")
        else:
            print(f"  ❌ Furniture {tile_id} ({furniture['name']}): Kein Sprite gefunden")
    
    # Teste Decoration-Tiles
    for decoration in test_map_data["decoration"]:
        tile_id = decoration["tile_id"]
        sprite = sm.get_tile_sprite(tile_id)
        if sprite:
            print(f"  ✅ Decoration {tile_id} ({decoration['name']}): Sprite geladen ({sprite.get_size()})")
        else:
            print(f"  ❌ Decoration {tile_id} ({decoration['name']}): Kein Sprite gefunden")
    
    print("\n🎯 Teste TileRenderer-Methoden:")
    
    # Teste _render_furniture_placement
    try:
        # Erstelle einen Dummy-Screen für den Test
        dummy_screen = pygame.Surface((800, 600))
        tr._render_furniture_placement(dummy_screen, test_map_data, camera.position)
        print("  ✅ _render_furniture_placement: Methode funktioniert")
    except Exception as e:
        print(f"  ❌ _render_furniture_placement: Fehler - {e}")
    
    # Teste _render_decoration
    try:
        tr._render_decoration(dummy_screen, test_map_data, camera.position)
        print("  ✅ _render_decoration: Methode funktioniert")
    except Exception as e:
        print(f"  ❌ _render_decoration: Fehler - {e}")
    
    # Teste render_map
    try:
        tr.render_map(dummy_screen, test_map_data, camera.position)
        print("  ✅ render_map: Methode funktioniert")
    except Exception as e:
        print(f"  ❌ render_map: Fehler - {e}")
    
    print("\n📊 Cache-Status nach Tests:")
    cache_info = sm.get_cache_info()
    for key, value in cache_info.items():
        print(f"  {key}: {value}")
    
    print("\n✅ Tile-Rendering-Test abgeschlossen!")
    
except ImportError as e:
    print(f"❌ Import-Fehler: {e}")
except Exception as e:
    print(f"❌ Fehler: {e}")
    import traceback
    traceback.print_exc()
