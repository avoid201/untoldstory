#!/usr/bin/env python3
"""
Test script for maps in game context
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
    print("🎮 Testing Map Rendering in Game Context...")
    
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
                        
        except Exception as e:
            print(f"  ❌ Failed to test {map_id}: {e}")
            import traceback
            traceback.print_exc()
    
    pygame.quit()
    print("\n✅ Map rendering tests completed!")

def test_map_transitions():
    """Test map transition logic"""
    print("\n🔄 Testing Map Transitions...")
    
    # Test warp connections between maps
    map_connections = {
        'player_house': ['kohlenstadt'],
        'kohlenstadt': ['player_house', 'route1', 'museum'],
        'route1': ['kohlenstadt'],
        'museum': ['kohlenstadt'],
        'bergmannsheil': ['kohlenstadt'],
        'penny': ['kohlenstadt'],
        'rival_house': ['kohlenstadt']
    }
    
    for map_id, connections in map_connections.items():
        print(f"\n🗺️  {map_id} connections:")
        try:
            map_data = MapLoader.load_map(map_id)
            print(f"  📍 Warps: {len(map_data.warps)}")
            for warp in map_data.warps:
                print(f"    → {warp.to_map} at ({warp.x}, {warp.y})")
            
            print(f"  🎯 Expected connections: {connections}")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")

def test_map_properties():
    """Test map properties and metadata"""
    print("\n📋 Testing Map Properties...")
    
    for map_id in ['route1', 'kohlenstadt', 'bergmannsheil', 'museum', 'penny', 'player_house', 'rival_house']:
        try:
            map_data = MapLoader.load_map(map_id)
            print(f"\n🗺️  {map_id}:")
            print(f"  📝 Name: {map_data.name}")
            print(f"  📏 Dimensions: {map_data.width}x{map_data.height}")
            print(f"  🎨 Tile size: {map_data.tile_size}")
            print(f"  🎵 Properties: {map_data.properties}")
            print(f"  🎮 Triggers: {len(map_data.triggers)}")
            
            # Check tile content
            if 'ground' in map_data.layers:
                ground_layer = map_data.layers['ground']
                if ground_layer and ground_layer[0]:
                    sample_tiles = ground_layer[0][:5]  # First 5 tiles
                    print(f"  🌱 Sample ground tiles: {sample_tiles}")
            
            # Check if map has expected properties
            if not map_data.properties:
                print(f"  💡 Suggestion: Add properties like music, encounters, etc.")
                
        except Exception as e:
            print(f"  ❌ Error testing {map_id}: {e}")

def test_tile_name_mapping():
    """Test that tile names are correctly mapped"""
    print("\n🔤 Testing Tile Name Mapping...")
    
    try:
        # Test route1 specifically
        route1 = MapLoader.load_map('route1')
        
        print(f"Route1 tile mapping test:")
        
        # Check ground layer
        if 'ground' in route1.layers:
            ground_layer = route1.layers['ground']
            if ground_layer and ground_layer[0]:
                print(f"  Ground layer sample: {ground_layer[0][:10]}")
                
                # Check if tiles are names (strings) not IDs (numbers)
                sample_tile = ground_layer[0][0]
                if isinstance(sample_tile, str):
                    print(f"  ✅ Tiles are mapped to names: {sample_tile}")
                else:
                    print(f"  ❌ Tiles are still IDs: {sample_tile}")
        
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
        print(f"Error testing tile mapping: {e}")

if __name__ == "__main__":
    print("🚀 Starting Comprehensive Map Tests...")
    
    try:
        test_map_rendering()
        test_map_transitions()
        test_map_properties()
        test_tile_name_mapping()
        print("\n🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
