#!/usr/bin/env python3
"""
Detaillierter UI-Interaktions-Test
Testet jede einzelne UI-Interaktion im Detail
"""

import sys
import os
import traceback
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_detailed_ui_interactions():
    """Test detailed UI interactions for each menu option."""
    print("🎮 Testing Detailed UI Interactions...")
    
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
        
        # Create test monsters with moves
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
        
        # Add some moves to player monster
        test_move1 = Move(
            id="test_move1",
            name="Test Move 1",
            type="normal",
            category=MoveCategory.PHYSICAL,
            power=40,
            accuracy=100,
            priority=0,
            targeting=MoveTarget.ENEMY,
            effects=[],
            description="Test move 1"
        )
        
        test_move2 = Move(
            id="test_move2",
            name="Test Move 2",
            type="normal",
            category=MoveCategory.MAGICAL,
            power=35,
            accuracy=95,
            priority=0,
            targeting=MoveTarget.ENEMY,
            effects=[],
            description="Test move 2"
        )
        
        player_monster.moves = [test_move1, test_move2]
        
        print("✅ Test monsters with moves created")
        
        # Create battle controller
        battle_controller = BattleController(
            player_team=[player_monster],
            enemy_team=[enemy_monster]
        )
        
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
        
        # Test 1: ATTACKE - Move Selection Flow
        print("\n🎯 Testing ATTACKE - Move Selection Flow...")
        
        battle_scene.battle_ui.current_menu_state = BattleMenuState.MAIN
        battle_scene.battle_ui.selected_option = 0  # ATTACKE
        
        # Navigate to move selection
        result = battle_scene.battle_ui.handle_input("confirm", battle_scene.battle_ui.battle_state)
        
        if battle_scene.battle_ui.current_menu_state != BattleMenuState.MOVE_SELECT:
            print(f"❌ Failed to enter MOVE_SELECT: {battle_scene.battle_ui.current_menu_state}")
            return False
        
        print("✅ Entered MOVE_SELECT state")
        
        # Test move navigation
        initial_move = battle_scene.battle_ui.selected_move
        battle_scene.battle_ui.handle_input("down", battle_scene.battle_ui.battle_state)
        
        if battle_scene.battle_ui.selected_move != initial_move + 1:
            print(f"❌ Move navigation down failed: {battle_scene.battle_ui.selected_move}")
            return False
        
        print("✅ Move navigation down works")
        
        battle_scene.battle_ui.handle_input("up", battle_scene.battle_ui.battle_state)
        
        if battle_scene.battle_ui.selected_move != initial_move:
            print(f"❌ Move navigation up failed: {battle_scene.battle_ui.selected_move}")
            return False
        
        print("✅ Move navigation up works")
        
        # Test move selection
        result = battle_scene.battle_ui.handle_input("confirm", battle_scene.battle_ui.battle_state)
        
        if not result or result.get("type") != "attack":
            print(f"❌ Move selection failed: {result}")
            return False
        
        print("✅ Move selection creates attack action")
        
        # Test cancel from move selection
        battle_scene.battle_ui.current_menu_state = BattleMenuState.MOVE_SELECT
        battle_scene.battle_ui.handle_input("cancel", battle_scene.battle_ui.battle_state)
        
        if battle_scene.battle_ui.current_menu_state != BattleMenuState.MAIN:
            print(f"❌ Cancel from MOVE_SELECT failed: {battle_scene.battle_ui.current_menu_state}")
            return False
        
        print("✅ Cancel from MOVE_SELECT works")
        
        # Test 2: ITEM - Item Selection Flow
        print("\n🎯 Testing ITEM - Item Selection Flow...")
        
        battle_scene.battle_ui.current_menu_state = BattleMenuState.MAIN
        battle_scene.battle_ui.selected_option = 1  # ITEM
        
        result = battle_scene.battle_ui.handle_input("confirm", battle_scene.battle_ui.battle_state)
        
        if battle_scene.battle_ui.current_menu_state != BattleMenuState.ITEM_SELECT:
            print(f"❌ Failed to enter ITEM_SELECT: {battle_scene.battle_ui.current_menu_state}")
            return False
        
        print("✅ Entered ITEM_SELECT state")
        
        # Test item navigation
        initial_item = battle_scene.battle_ui.selected_item
        battle_scene.battle_ui.handle_input("down", battle_scene.battle_ui.battle_state)
        
        if battle_scene.battle_ui.selected_item != initial_item + 1:
            print(f"❌ Item navigation down failed: {battle_scene.battle_ui.selected_item}")
            return False
        
        print("✅ Item navigation down works")
        
        battle_scene.battle_ui.handle_input("up", battle_scene.battle_ui.battle_state)
        
        if battle_scene.battle_ui.selected_item != initial_item:
            print(f"❌ Item navigation up failed: {battle_scene.battle_ui.selected_item}")
            return False
        
        print("✅ Item navigation up works")
        
        # Test item selection
        result = battle_scene.battle_ui.handle_input("confirm", battle_scene.battle_ui.battle_state)
        
        if not result or result.get("type") != "item":
            print(f"❌ Item selection failed: {result}")
            return False
        
        print("✅ Item selection creates item action")
        
        # Test cancel from item selection
        battle_scene.battle_ui.current_menu_state = BattleMenuState.ITEM_SELECT
        battle_scene.battle_ui.handle_input("cancel", battle_scene.battle_ui.battle_state)
        
        if battle_scene.battle_ui.current_menu_state != BattleMenuState.MAIN:
            print(f"❌ Cancel from ITEM_SELECT failed: {battle_scene.battle_ui.current_menu_state}")
            return False
        
        print("✅ Cancel from ITEM_SELECT works")
        
        # Test 3: WECHSEL - Switch Selection Flow
        print("\n🎯 Testing WECHSEL - Switch Selection Flow...")
        
        battle_scene.battle_ui.current_menu_state = BattleMenuState.MAIN
        battle_scene.battle_ui.selected_option = 2  # WECHSEL
        
        result = battle_scene.battle_ui.handle_input("confirm", battle_scene.battle_ui.battle_state)
        
        if battle_scene.battle_ui.current_menu_state != BattleMenuState.SWITCH_SELECT:
            print(f"❌ Failed to enter SWITCH_SELECT: {battle_scene.battle_ui.current_menu_state}")
            return False
        
        print("✅ Entered SWITCH_SELECT state")
        
        # Test team member navigation (only works with multiple team members)
        initial_member = battle_scene.battle_ui.selected_team_member
        team_size = len(battle_scene.battle_ui.battle_state.player_team)
        
        if team_size > 1:
            battle_scene.battle_ui.handle_input("down", battle_scene.battle_ui.battle_state)
            
            if battle_scene.battle_ui.selected_team_member != initial_member + 1:
                print(f"❌ Team member navigation down failed: {battle_scene.battle_ui.selected_team_member}")
                return False
            
            print("✅ Team member navigation down works")
            
            battle_scene.battle_ui.handle_input("up", battle_scene.battle_ui.battle_state)
            
            if battle_scene.battle_ui.selected_team_member != initial_member:
                print(f"❌ Team member navigation up failed: {battle_scene.battle_ui.selected_team_member}")
                return False
            
            print("✅ Team member navigation up works")
        else:
            print("✅ Team member navigation skipped (only one team member)")
        
        # Test team member selection
        result = battle_scene.battle_ui.handle_input("confirm", battle_scene.battle_ui.battle_state)
        
        if team_size > 1:
            if not result or result.get("type") != "switch":
                print(f"❌ Team member selection failed: {result}")
                return False
            
            print("✅ Team member selection creates switch action")
        else:
            # With only one team member, switch should fail (can't switch to self)
            if result is None:
                print("✅ Team member selection correctly fails (can't switch to self)")
            else:
                print(f"❌ Team member selection should fail with one member: {result}")
                return False
        
        # Test cancel from switch selection
        battle_scene.battle_ui.current_menu_state = BattleMenuState.SWITCH_SELECT
        battle_scene.battle_ui.handle_input("cancel", battle_scene.battle_ui.battle_state)
        
        if battle_scene.battle_ui.current_menu_state != BattleMenuState.MAIN:
            print(f"❌ Cancel from SWITCH_SELECT failed: {battle_scene.battle_ui.current_menu_state}")
            return False
        
        print("✅ Cancel from SWITCH_SELECT works")
        
        # Test 4: ZÄHMEN - Tame Selection Flow
        print("\n🎯 Testing ZÄHMEN - Tame Selection Flow...")
        
        battle_scene.battle_ui.current_menu_state = BattleMenuState.MAIN
        battle_scene.battle_ui.selected_option = 3  # ZÄHMEN
        
        result = battle_scene.battle_ui.handle_input("confirm", battle_scene.battle_ui.battle_state)
        
        if battle_scene.battle_ui.current_menu_state != BattleMenuState.TAME_MEAT:
            print(f"❌ Failed to enter TAME_MEAT: {battle_scene.battle_ui.current_menu_state}")
            return False
        
        print("✅ Entered TAME_MEAT state")
        
        # Test meat selection navigation
        initial_meat = battle_scene.battle_ui.selected_item
        battle_scene.battle_ui.handle_input("down", battle_scene.battle_ui.battle_state)
        
        if battle_scene.battle_ui.selected_item != initial_meat + 1:
            print(f"❌ Meat navigation down failed: {battle_scene.battle_ui.selected_item}")
            return False
        
        print("✅ Meat navigation down works")
        
        battle_scene.battle_ui.handle_input("up", battle_scene.battle_ui.battle_state)
        
        if battle_scene.battle_ui.selected_item != initial_meat:
            print(f"❌ Meat navigation up failed: {battle_scene.battle_ui.selected_item}")
            return False
        
        print("✅ Meat navigation up works")
        
        # Test meat selection
        result = battle_scene.battle_ui.handle_input("confirm", battle_scene.battle_ui.battle_state)
        
        if not result or result.get("type") != "use_meat":
            print(f"❌ Meat selection failed: {result}")
            return False
        
        print("✅ Meat selection creates use_meat action")
        
        # Test cancel from meat selection
        battle_scene.battle_ui.current_menu_state = BattleMenuState.TAME_MEAT
        battle_scene.battle_ui.handle_input("cancel", battle_scene.battle_ui.battle_state)
        
        if battle_scene.battle_ui.current_menu_state != BattleMenuState.MAIN:
            print(f"❌ Cancel from TAME_MEAT failed: {battle_scene.battle_ui.current_menu_state}")
            return False
        
        print("✅ Cancel from TAME_MEAT works")
        
        # Test 5: SPÄHEN - Scout Action
        print("\n🎯 Testing SPÄHEN - Scout Action...")
        
        battle_scene.battle_ui.current_menu_state = BattleMenuState.MAIN
        battle_scene.battle_ui.selected_option = 4  # SPÄHEN
        
        result = battle_scene.battle_ui.handle_input("confirm", battle_scene.battle_ui.battle_state)
        
        if not result or result.get("type") != "scout":
            print(f"❌ Scout action failed: {result}")
            return False
        
        print("✅ Scout action created successfully")
        
        # Test 6: FLUCHT - Flee Action
        print("\n🎯 Testing FLUCHT - Flee Action...")
        
        battle_scene.battle_ui.current_menu_state = BattleMenuState.MAIN
        battle_scene.battle_ui.selected_option = 5  # FLUCHT
        
        result = battle_scene.battle_ui.handle_input("confirm", battle_scene.battle_ui.battle_state)
        
        if not result or result.get("type") != "flee":
            print(f"❌ Flee action failed: {result}")
            return False
        
        print("✅ Flee action created successfully")
        
        print("\n🎉 Detailed UI Interactions Test PASSED!")
        print("\n📊 SUMMARY:")
        print("✅ All 6 main menu options work")
        print("✅ All menu transitions work")
        print("✅ All navigation (up/down) works")
        print("✅ All confirmations work")
        print("✅ All cancellations work")
        print("✅ All action creations work")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_detailed_ui_interactions()
    sys.exit(0 if success else 1)
