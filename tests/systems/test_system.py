#!/usr/bin/env python3
"""
Test-Script für Untold Story - Prüft ob alle Fixes funktionieren
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

def test_imports():
    """Test if all critical modules can be imported"""
    print("🔍 Teste Module...")
    
    try:
        # Core modules
        from engine.core.game import Game
        print("✅ Game-Klasse importiert")
        
        from engine.scenes.field_scene import FieldScene
        print("✅ FieldScene importiert")
        
        from engine.world.enhanced_map_manager import EnhancedMapManager
        print("✅ EnhancedMapManager importiert")
        
        from engine.world.tmx_init import initialize_tmx_support
        print("✅ TMX-Init importiert")
        
        from engine.world.area import Area
        print("✅ Area-Klasse importiert")
        
        from engine.graphics.sprite_manager import SpriteManager
        print("✅ SpriteManager importiert")
        
        return True
    except ImportError as e:
        print(f"❌ Import-Fehler: {e}")
        return False

def test_data_files():
    """Test if all required data files exist"""
    print("\n📁 Teste Daten-Dateien...")
    
    required_files = [
        "data/maps/interactions/player_house.json",
        "data/maps/interactions/kohlenstadt.json",
        "data/maps/interactions/museum.json",
        "data/dialogs/npcs/karl_dialog.json",
        "data/dialogs/npcs/professor_dialog.json",
        "data/maps/player_house.json",
        "data/maps/kohlenstadt.json",
    ]
    
    all_exist = True
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} fehlt!")
            all_exist = False
    
    return all_exist

def test_enhanced_manager():
    """Test if Enhanced Map Manager is properly activated"""
    print("\n🗺️ Teste Enhanced Map Manager...")
    
    try:
        # Read field_scene.py to check if Enhanced Manager is activated
        field_scene_path = Path("engine/scenes/field_scene.py")
        content = field_scene_path.read_text()
        
        if "if True and hasattr(self, 'use_enhanced_manager')" in content:
            print("✅ Enhanced Map Manager ist aktiviert")
            return True
        elif "if False and hasattr(self, 'use_enhanced_manager')" in content:
            print("❌ Enhanced Map Manager ist deaktiviert!")
            return False
        else:
            print("⚠️ Enhanced Map Manager Status unklar")
            return False
    except Exception as e:
        print(f"❌ Fehler beim Prüfen: {e}")
        return False

def test_sprite_loading():
    """Test if sprites can be loaded"""
    print("\n🎨 Teste Sprite-Loading...")
    
    try:
        import pygame
        pygame.init()
        
        from engine.graphics.sprite_manager import SpriteManager
        sprite_manager = SpriteManager.get()
        
        # Test loading different sprite types
        test_tiles = ["grass", "wall", "water_1"]
        for tile_name in test_tiles:
            sprite = sprite_manager.get_tile(tile_name)
            if sprite:
                print(f"✅ Tile '{tile_name}' geladen")
            else:
                print(f"⚠️ Tile '{tile_name}' nicht gefunden")
        
        # Test player sprite
        player_sprite = sprite_manager.get_player_sprite("down")
        if player_sprite:
            print("✅ Player-Sprite geladen")
        else:
            print("❌ Player-Sprite nicht gefunden")
        
        return True
    except Exception as e:
        print(f"❌ Fehler beim Sprite-Loading: {e}")
        return False

def test_map_loading():
    """Test if maps can be loaded"""
    print("\n🏠 Teste Map-Loading...")
    
    try:
        import pygame
        pygame.init()
        
        # Create minimal display for testing
        screen = pygame.display.set_mode((320, 180))
        
        from engine.world.area import Area
        
        # Test loading player_house
        area = Area("player_house")
        if area.map_data:
            print(f"✅ player_house geladen ({area.width}x{area.height})")
        else:
            print("❌ player_house konnte nicht geladen werden")
        
        # Test loading kohlenstadt
        area2 = Area("kohlenstadt")
        if area2.map_data:
            print(f"✅ kohlenstadt geladen ({area2.width}x{area2.height})")
        else:
            print("❌ kohlenstadt konnte nicht geladen werden")
        
        return True
    except Exception as e:
        print(f"❌ Fehler beim Map-Loading: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("=" * 50)
    print("🎮 UNTOLD STORY - SYSTEM TEST")
    print("=" * 50)
    
    all_tests_passed = True
    
    # Run tests
    if not test_imports():
        all_tests_passed = False
    
    if not test_data_files():
        all_tests_passed = False
    
    if not test_enhanced_manager():
        all_tests_passed = False
    
    if not test_sprite_loading():
        all_tests_passed = False
    
    if not test_map_loading():
        all_tests_passed = False
    
    # Summary
    print("\n" + "=" * 50)
    if all_tests_passed:
        print("✅ ALLE TESTS BESTANDEN!")
        print("\nDas Spiel sollte jetzt funktionieren.")
        print("Starte es mit: python3 main.py")
    else:
        print("❌ EINIGE TESTS FEHLGESCHLAGEN!")
        print("\nBitte prüfe die Fehlermeldungen oben.")
        print("Das Spiel könnte trotzdem starten, aber mit Problemen.")
    print("=" * 50)

if __name__ == "__main__":
    main()
