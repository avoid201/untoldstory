#!/usr/bin/env python3
"""
Test script for TMX map loading
Tests the new TMX support in MapLoader
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from engine.world.map_loader import MapLoader
from engine.core.resources import resources

def test_tmx_loading():
    """Test loading of TMX maps"""
    print("🧪 Testing TMX Map Loading...")
    
    # Test maps to try
    test_maps = [
        'route1',
        'kohlenstadt', 
        'bergmannsheil',
        'museum',
        'penny',
        'player_house',
        'rival_house'
    ]
    
    for map_id in test_maps:
        print(f"\n📋 Testing map: {map_id}")
        try:
            # Try to load the map
            map_data = MapLoader.load_map(map_id)
            
            print(f"  ✅ Successfully loaded {map_id}")
            print(f"    - Name: {map_data.name}")
            print(f"    - Size: {map_data.width}x{map_data.height}")
            print(f"    - Tile size: {map_data.tile_size}")
            print(f"    - Layers: {list(map_data.layers.keys())}")
            print(f"    - Warps: {len(map_data.warps)}")
            print(f"    - Triggers: {len(map_data.triggers)}")
            print(f"    - Properties: {map_data.properties}")
            
            # Validate the map
            issues = MapLoader.validate_map(map_data)
            if issues:
                print(f"    ⚠️  Validation issues:")
                for issue in issues:
                    print(f"      - {issue}")
            else:
                print(f"    ✅ Map validation passed")
                
        except Exception as e:
            print(f"  ❌ Failed to load {map_id}: {e}")
            import traceback
            traceback.print_exc()

def test_specific_map_details():
    """Test specific details of loaded maps"""
    print("\n🔍 Testing specific map details...")
    
    try:
        # Test route1 specifically
        route1 = MapLoader.load_map('route1')
        print(f"Route1 layers: {list(route1.layers.keys())}")
        
        # Check if we have the expected layers
        if 'tile layer 1' in route1.layers:
            layer = route1.layers['tile layer 1']
            print(f"Tile Layer 1 size: {len(layer)}x{len(layer[0]) if layer else 0}")
            print(f"Sample tiles: {layer[0][:5] if layer else 'No data'}")
        
        if 'decor' in route1.layers:
            decor = route1.layers['decor']
            print(f"Decor layer size: {len(decor)}x{len(decor[0]) if decor else 0}")
            print(f"Sample decor: {decor[0][:5] if decor else 'No data'}")
            
    except Exception as e:
        print(f"Error testing specific details: {e}")

if __name__ == "__main__":
    print("🚀 Starting TMX Map Loading Tests...")
    
    try:
        test_tmx_loading()
        test_specific_map_details()
        print("\n✅ All tests completed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
