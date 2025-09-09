#!/usr/bin/env python3
"""
Schnelle Status-Überprüfung für Untold Story
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

def test_imports():
    """Testet alle wichtigen Imports"""
    print("🔍 TESTING CORE IMPORTS...")
    
    try:
        import pygame
        print(f"✅ pygame: {pygame.version.ver}")
    except ImportError as e:
        print(f"❌ pygame: {e}")
        return False
    
    try:
        from engine.core.game import Game
        print("✅ engine.core.game")
    except ImportError as e:
        print(f"❌ engine.core.game: {e}")
        return False
    
    try:
        from engine.systems.battle.battle_controller import BattleController
        print("✅ battle_controller")
    except ImportError as e:
        print(f"❌ battle_controller: {e}")
    
    try:
        from engine.scenes.battle_scene import BattleScene
        print("✅ battle_scene")
    except ImportError as e:
        print(f"❌ battle_scene: {e}")
    
    try:
        from engine.scenes.field_scene import FieldScene
        print("✅ field_scene")
    except ImportError as e:
        print(f"❌ field_scene: {e}")
    
    try:
        from engine.systems.monsters import MonsterDatabase
        print("✅ monster_database")
    except ImportError as e:
        print(f"❌ monster_database: {e}")
    
    return True

def test_data_files():
    """Testet ob wichtige Datendateien vorhanden sind"""
    print("\n🔍 TESTING DATA FILES...")
    
    data_files = [
        "data/monsters.json",
        "data/moves.json",
        "data/types.json",
        "data/items.json"
    ]
    
    for file_path in data_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING!")

def test_battle_system():
    """Testet das Battle System"""
    print("\n🔍 TESTING BATTLE SYSTEM...")
    
    try:
        from engine.systems.battle.battle_controller import BattleController
        from engine.systems.monster_instance import MonsterInstance
        from engine.systems.monsters import MonsterDatabase
        
        # Try to load monster database
        monster_db = MonsterDatabase()
        print("✅ MonsterDatabase initialized")
        
        # Try to get a monster species
        glutstummel = monster_db.get_species("glutstummel")
        if glutstummel:
            print("✅ Glutstummel loaded successfully")
            
            # Try to create monster instance
            monster = MonsterInstance(glutstummel, level=5)
            print(f"✅ MonsterInstance created: {monster.species.name} Lv.{monster.level}")
        else:
            print("❌ Could not load Glutstummel")
            
    except Exception as e:
        print(f"❌ Battle System error: {e}")
        import traceback
        traceback.print_exc()

def test_asset_loading():
    """Testet Asset-Loading"""
    print("\n🔍 TESTING ASSET LOADING...")
    
    try:
        from engine.graphics.sprite_manager import SpriteManager
        sprite_manager = SpriteManager.get()
        print("✅ SpriteManager initialized")
        
        # Check if assets folder exists
        if Path("assets").exists():
            print("✅ assets/ folder found")
        else:
            print("❌ assets/ folder missing")
            
    except Exception as e:
        print(f"❌ Asset loading error: {e}")

def main():
    """Hauptfunktion"""
    print("=== UNTOLD STORY STATUS CHECK ===\n")
    
    if not test_imports():
        print("\n❌ CRITICAL: Core imports failed!")
        return 1
    
    test_data_files()
    test_battle_system()
    test_asset_loading()
    
    print("\n=== STATUS CHECK COMPLETE ===")
    return 0

if __name__ == "__main__":
    sys.exit(main())
