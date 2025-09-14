#!/usr/bin/env python3
"""
Kompletter Battle Flow Test
Testet alle Spieler-Interaktionen und den Turn-Flow
"""

import sys
import os
import traceback
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_complete_battle_flow():
    """Test the complete battle flow with all player interactions."""
    print("🎮 Testing Complete Battle Flow...")
    
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
        
        print("✅ All imports successful")
        
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
        
        # Create battle controller
        battle_controller = BattleController(
            player_team=[player_monster],
            enemy_team=[enemy_monster]
        )
        
        print("✅ Battle controller created")
        
        # Create mock game object
        class MockGame:
            def __init__(self):
                self.sprite_manager = None
                self.resource_manager = None
        
        # Create battle scene
        mock_game = MockGame()
        battle_scene = BattleScene(mock_game)
        
        # Initialize battle scene
        battle_scene.battle_controller = battle_controller
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
        
        # Test all main menu options
        print("\n🎯 Testing Main Menu Options...")
        
        # Test 1: ATTACKE (Move Selection)
        print("Testing ATTACKE option...")
        battle_scene.battle_ui.current_menu_state = BattleMenuState.MAIN
        battle_scene.battle_ui.selected_option = 0  # ATTACKE
        
        # Simulate input
        result = battle_scene.battle_ui.handle_input("confirm", battle_scene.battle_ui.battle_state)
        
        if battle_scene.battle_ui.current_menu_state == BattleMenuState.MOVE_SELECT:
            print("✅ ATTACKE → MOVE_SELECT transition works")
        else:
            print(f"❌ ATTACKE transition failed: {battle_scene.battle_ui.current_menu_state}")
            return False
        
        # Test 2: ITEM (Item Selection)
        print("Testing ITEM option...")
        battle_scene.battle_ui.current_menu_state = BattleMenuState.MAIN
        battle_scene.battle_ui.selected_option = 1  # ITEM
        
        result = battle_scene.battle_ui.handle_input("confirm", battle_scene.battle_ui.battle_state)
        
        if battle_scene.battle_ui.current_menu_state == BattleMenuState.ITEM_SELECT:
            print("✅ ITEM → ITEM_SELECT transition works")
        else:
            print(f"❌ ITEM transition failed: {battle_scene.battle_ui.current_menu_state}")
            return False
        
        # Test 3: WECHSEL (Switch Selection)
        print("Testing WECHSEL option...")
        battle_scene.battle_ui.current_menu_state = BattleMenuState.MAIN
        battle_scene.battle_ui.selected_option = 2  # WECHSEL
        
        result = battle_scene.battle_ui.handle_input("confirm", battle_scene.battle_ui.battle_state)
        
        if battle_scene.battle_ui.current_menu_state == BattleMenuState.SWITCH_SELECT:
            print("✅ WECHSEL → SWITCH_SELECT transition works")
        else:
            print(f"❌ WECHSEL transition failed: {battle_scene.battle_ui.current_menu_state}")
            return False
        
        # Test 4: ZÄHMEN (Tame Selection)
        print("Testing ZÄHMEN option...")
        battle_scene.battle_ui.current_menu_state = BattleMenuState.MAIN
        battle_scene.battle_ui.selected_option = 3  # ZÄHMEN
        
        result = battle_scene.battle_ui.handle_input("confirm", battle_scene.battle_ui.battle_state)
        
        if battle_scene.battle_ui.current_menu_state == BattleMenuState.TAME_MEAT:
            print("✅ ZÄHMEN → TAME_MEAT transition works")
        else:
            print(f"❌ ZÄHMEN transition failed: {battle_scene.battle_ui.current_menu_state}")
            return False
        
        # Test 5: SPÄHEN (Scout Action)
        print("Testing SPÄHEN option...")
        battle_scene.battle_ui.current_menu_state = BattleMenuState.MAIN
        battle_scene.battle_ui.selected_option = 4  # SPÄHEN
        
        result = battle_scene.battle_ui.handle_input("confirm", battle_scene.battle_ui.battle_state)
        
        if result and result.get("type") == "scout":
            print("✅ SPÄHEN action created successfully")
        else:
            print(f"❌ SPÄHEN action failed: {result}")
            return False
        
        # Test 6: FLUCHT (Flee Action)
        print("Testing FLUCHT option...")
        battle_scene.battle_ui.current_menu_state = BattleMenuState.MAIN
        battle_scene.battle_ui.selected_option = 5  # FLUCHT
        
        result = battle_scene.battle_ui.handle_input("confirm", battle_scene.battle_ui.battle_state)
        
        if result and result.get("type") == "flee":
            print("✅ FLUCHT action created successfully")
        else:
            print(f"❌ FLUCHT action failed: {result}")
            return False
        
        print("\n🎯 Testing Move Selection Flow...")
        
        # Test Move Selection
        battle_scene.battle_ui.current_menu_state = BattleMenuState.MOVE_SELECT
        battle_scene.battle_ui.selected_move = 0
        
        # Test move navigation
        battle_scene.battle_ui.handle_input("down", battle_scene.battle_ui.battle_state)
        battle_scene.battle_ui.handle_input("up", battle_scene.battle_ui.battle_state)
        
        # Test move selection (should create attack action)
        result = battle_scene.battle_ui.handle_input("confirm", battle_scene.battle_ui.battle_state)
        
        if result and result.get("type") == "attack":
            print("✅ Move selection creates attack action")
        else:
            print(f"❌ Move selection failed: {result}")
            return False
        
        print("\n🎯 Testing Turn Flow...")
        
        # Test complete turn execution
        if result:
            # Process the action
            battle_scene._process_player_action(result)
            
            # Check if battle state was updated
            if battle_scene.battle_controller.state.battle_ended:
                print(f"✅ Turn executed, battle ended: {battle_scene.battle_controller.state.battle_result}")
            else:
                print("✅ Turn executed, battle continues")
        
        print("\n🎯 Testing UI State Synchronization...")
        
        # Check if UI state is properly synced
        if battle_scene.battle_ui.battle_state == battle_scene.battle_controller.state:
            print("✅ UI state is synchronized with controller")
        else:
            print("❌ UI state not synchronized")
            return False
        
        # Check if monster data is accessible
        if battle_scene.battle_ui.battle_state.player_active:
            print("✅ Player monster data accessible in UI")
        else:
            print("❌ Player monster data not accessible")
            return False
        
        if battle_scene.battle_ui.battle_state.enemy_active:
            print("✅ Enemy monster data accessible in UI")
        else:
            print("❌ Enemy monster data not accessible")
            return False
        
        print("\n🎉 Complete Battle Flow Test PASSED!")
        print("\n📊 SUMMARY:")
        print("✅ All 6 main menu options work")
        print("✅ Menu transitions work correctly")
        print("✅ Action creation works")
        print("✅ Turn execution works")
        print("✅ UI state synchronization works")
        print("✅ Monster data is accessible")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_complete_battle_flow()
    sys.exit(0 if success else 1)
