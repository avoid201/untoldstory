#!/usr/bin/env python3
"""
Battle UI Rendering Test
Testet das Battle UI Rendering
"""

import sys
import os
import traceback
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_battle_ui_rendering():
    """Test the battle UI rendering."""
    print("🎮 Testing Battle UI Rendering...")
    
    try:
        # Import all components
        from engine.systems.battle.battle_controller import BattleController
        from engine.systems.battle.battle_state import BattleState
        from engine.systems.battle.turn_logic import BattleAction, ActionType
        from engine.systems.monster_instance import MonsterInstance, MonsterSpecies
        from engine.systems.stats import BaseStats
        from engine.systems.moves import Move, MoveCategory, MoveTarget
        from engine.ui.battle import BattleUI
        from engine.scenes.battle_scene import BattleScene
        from engine.ui.battle.battle_ui_state import BattleMenuState
        import pygame
        
        print("✅ All imports successful")
        
        # Initialize pygame
        pygame.init()
        
        # Create test monsters
        player_species = MonsterSpecies(
            id="test_player",
            name="Test Player",
            types=["Normal"],
            base_stats=BaseStats(hp=100, atk=50, def_=30, mag=20, res=25, spd=40)
        )
        
        enemy_species = MonsterSpecies(
            id="test_enemy",
            name="Test Enemy",
            types=["Normal"], 
            base_stats=BaseStats(hp=80, atk=45, def_=25, mag=15, res=20, spd=35)
        )
        
        player_monster = MonsterInstance(species=player_species, level=5)
        enemy_monster = MonsterInstance(species=enemy_species, level=5)
        
        print("✅ Test monsters created")
        
        # Create mock game object
        class MockGame:
            def __init__(self):
                self.sprite_manager = None
                self.resource_manager = None
                self.debug_mode = True
        
        # Create battle scene
        mock_game = MockGame()
        battle_scene = BattleScene(mock_game)
        
        # Initialize battle scene
        battle_scene.battle_controller = BattleController(
            player_team=[player_monster],
            enemy_team=[enemy_monster]
        )
        battle_scene.battle_ui = BattleUI(mock_game)
        
        # Test battle initialization
        init_success = battle_scene.initialize_battle([player_monster], [enemy_monster])
        if not init_success:
            print("❌ Battle scene initialization failed")
            return False
        
        print("✅ Battle scene initialized")
        
        # Test UI state
        if not battle_scene.battle_ui.battle_state:
            print("❌ UI state not synchronized")
            return False
        
        print("✅ UI state synchronized")
        
        # Test UI rendering
        print("Testing UI rendering...")
        
        # Create a test surface
        test_surface = pygame.Surface((320, 180))
        
        # Test draw method
        try:
            battle_scene.battle_ui.draw(test_surface)
            print("✅ UI draw method works")
        except Exception as e:
            print(f"❌ UI draw method failed: {e}")
            return False
        
        # Test menu state
        if battle_scene.battle_ui.state.menu_state == BattleMenuState.MAIN:
            print("✅ Menu state is MAIN")
        else:
            print(f"❌ Menu state is not MAIN: {battle_scene.battle_ui.state.menu_state}")
            return False
        
        # Test monster data
        if battle_scene.battle_ui.battle_state.player_active:
            print(f"✅ Player monster: {battle_scene.battle_ui.battle_state.player_active.name}")
        else:
            print("❌ Player monster not found")
            return False
        
        if battle_scene.battle_ui.battle_state.enemy_active:
            print(f"✅ Enemy monster: {battle_scene.battle_ui.battle_state.enemy_active.name}")
        else:
            print("❌ Enemy monster not found")
            return False
        
        # Test menu options
        print("Testing menu options...")
        battle_scene.battle_ui.handle_input("down", battle_scene.battle_ui.battle_state)
        if battle_scene.battle_ui.state.selected_option == 1:
            print("✅ Menu navigation works")
        else:
            print(f"❌ Menu navigation failed: {battle_scene.battle_ui.state.selected_option}")
            return False
        
        battle_scene.battle_ui.handle_input("up", battle_scene.battle_ui.battle_state)
        if battle_scene.battle_ui.state.selected_option == 0:
            print("✅ Menu navigation back works")
        else:
            print(f"❌ Menu navigation back failed: {battle_scene.battle_ui.state.selected_option}")
            return False
        
        print("\n🎉 Battle UI Rendering Test PASSED!")
        print("\n📊 SUMMARY:")
        print("✅ UI initialization works")
        print("✅ UI state synchronization works")
        print("✅ UI rendering works")
        print("✅ Menu state is correct")
        print("✅ Monster data is accessible")
        print("✅ Menu navigation works")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        traceback.print_exc()
        return False
    finally:
        try:
            pygame.quit()
        except:
            pass

if __name__ == "__main__":
    success = test_battle_ui_rendering()
    sys.exit(0 if success else 1)
