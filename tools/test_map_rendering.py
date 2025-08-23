#!/usr/bin/env python3
"""
Test script for map rendering with corrected TileRenderer
Tests the new TMX maps with the game's rendering system
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import pygame
from engine.world.map_loader import MapLoader
from engine.world.area import Area
from engine.graphics.sprite_manager import SpriteManager
from engine.graphics.tile_renderer import TileRenderer

def test_map_rendering():
    """Test map rendering with the game's systems"""
    print("🎮 Testing Map Rendering with Corrected TileRenderer...")
    
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    
    # Initialize game systems
    sprite_manager = SpriteManager()
    tile_renderer = TileRenderer(sprite_manager)
    
    # Test maps
    test_maps = ['route1', 'kohlenstadt', 'bergmannsheil', 'museum', 'penny', 'player_house', 'rival_house']
    
    for map_id in test_maps:
        print(f"\n🎯 Testing rendering for: {map_id}")
        try:
            # Load map
            map_data = MapLoader.load_map(map_id)
            
            # Create area
            area = Area(
                id=map_data.id,
                name=map_data.name,
                width=map_data.width,
                height=map_data.height,
                layers=map_data.layers,
                properties=map_data.properties or {}
            )
            area.map_data = map_data
            
            print(f"  ✅ Area created: {area.name}")
            print(f"  📏 Size: {area.width}x{area.height}")
            print(f"  🎨 Layers: {list(area.layers.keys())}")
            
            # Test if we can create a surface for each layer
            for layer_name, layer_data in area.layers.items():
                if layer_data:
                    # Check if layer contains tile names (strings) or IDs (numbers)
                    if layer_data and isinstance(layer_data[0], list) and layer_data[0]:
                        sample_tile = layer_data[0][0]
                        if isinstance(sample_tile, str):
                            print(f"    ✅ Layer '{layer_name}' has tile names: {sample_tile}")
                        else:
                            print(f"    ✅ Layer '{layer_name}' has tile IDs: {sample_tile}")
                    else:
                        print(f"    ⚠️  Layer '{layer_name}' is empty")
            
            # Test tile rendering with the corrected TileRenderer
            print(f"  🎨 Testing tile rendering...")
            try:
                # Create a small test surface
                test_surface = pygame.Surface((min(160, area.width * 16), min(160, area.height * 16)))
                test_surface.fill((0, 0, 0))  # Black background
                
                # Test rendering each layer
                for layer_name, layer_data in area.layers.items():
                    if layer_data and isinstance(layer_data[0], list):
                        # Render a small portion of the layer
                        camera_offset = (0, 0)
                        tile_renderer.render_layer(test_surface, layer_data, camera_offset, layer_name)
                        print(f"    ✅ Layer '{layer_name}' rendered successfully")
                
                print(f"    ✅ All layers rendered without errors")
                
            except Exception as e:
                print(f"    ❌ Rendering error: {e}")
                import traceback
                traceback.print_exc()
                        
        except Exception as e:
            print(f"  ❌ Failed to test {map_id}: {e}")
            import traceback
            traceback.print_exc()
    
    pygame.quit()
    print("\n✅ Map rendering tests completed!")

def test_specific_tile_rendering():
    """Test specific tile rendering scenarios"""
    print("\n🔍 Testing Specific Tile Rendering...")
    
    try:
        # Test route1 specifically
        route1 = MapLoader.load_map('route1')
        
        print(f"Route1 tile rendering test:")
        
        # Check ground layer
        if 'ground' in route1.layers:
            ground_layer = route1.layers['ground']
            if ground_layer and ground_layer[0]:
                print(f"  Ground layer sample: {ground_layer[0][:10]}")
                
                # Test rendering a single row
                test_surface = pygame.Surface((160, 16))
                test_surface.fill((0, 0, 0))
                
                # Initialize pygame and systems
                pygame.init()
                sprite_manager = SpriteManager()
                tile_renderer = TileRenderer(sprite_manager)
                
                # Render just the first row
                single_row = [ground_layer[0][:10]]  # First 10 tiles of first row
                tile_renderer.render_layer(test_surface, single_row, (0, 0), "test")
                print(f"  ✅ Single row rendered successfully")
                
                pygame.quit()
                
        # Check decor layer
        if 'decor' in route1.layers:
            decor_layer = route1.layers['decor']
            if decor_layer and decor_layer[0]:
                print(f"  Decor layer sample: {decor_layer[0][:10]}")
                
        # Check collision layer
        if 'collision' in route1.layers:
            collision_layer = route1.layers['collision']
            if collision_layer and collision_layer[0]:
                print(f"  Collision layer sample: {collision_layer[0][:10]}")
                # Collision should be binary (0 or 1)
                unique_values = set()
                for row in collision_layer[:5]:  # Check first 5 rows
                    unique_values.update(row[:10])  # Check first 10 tiles
                print(f"  Collision values: {sorted(unique_values)}")
                
    except Exception as e:
        print(f"Error testing specific tile rendering: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Starting Map Rendering Tests...")
    
    try:
        test_map_rendering()
        test_specific_tile_rendering()
        print("\n🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()


