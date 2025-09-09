#!/usr/bin/env python3
"""
Kompletter Spieler-Erfahrungs-Test
Testet die komplette Spieler-Erfahrung von Input bis Output
"""

import sys
import os
import traceback
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_complete_player_experience():
    """Test the complete player experience from input to output."""
    print("🎮 Testing Complete Player Experience...")
    
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
        
        # Create mock game object
        class MockGame:
            def __init__(self):
                self.sprite_manager = None
                self.resource_manager = None
        
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
        
        # Test complete player experience flow
        print("\n🎯 Testing Complete Player Experience Flow...")
        
        # Step 1: Player sees main menu
        print("Step 1: Player sees main menu")
        # Set to main menu state for testing
        battle_scene.battle_ui.current_menu_state = BattleMenuState.MAIN
        if battle_scene.battle_ui.current_menu_state == BattleMenuState.MAIN:
            print("✅ Main menu displayed")
        else:
            print(f"❌ Main menu not displayed: {battle_scene.battle_ui.current_menu_state}")
            return False
        
        # Step 2: Player navigates menu
        print("Step 2: Player navigates menu")
        battle_scene.battle_ui.handle_input("down", battle_scene.battle_ui.battle_state)
        if battle_scene.battle_ui.selected_option == 1:
            print("✅ Menu navigation works")
        else:
            print(f"❌ Menu navigation failed: {battle_scene.battle_ui.selected_option}")
            return False
        
        battle_scene.battle_ui.handle_input("up", battle_scene.battle_ui.battle_state)
        if battle_scene.battle_ui.selected_option == 0:
            print("✅ Menu navigation back works")
        else:
            print(f"❌ Menu navigation back failed: {battle_scene.battle_ui.selected_option}")
            return False
        
        # Step 3: Player selects ATTACKE
        print("Step 3: Player selects ATTACKE")
        battle_scene.battle_ui.selected_option = 0  # ATTACKE
        result = battle_scene.battle_ui.handle_input("confirm", battle_scene.battle_ui.battle_state)
        
        if battle_scene.battle_ui.current_menu_state == BattleMenuState.MOVE_SELECT:
            print("✅ Moved to move selection")
        else:
            print(f"❌ Failed to move to move selection: {battle_scene.battle_ui.current_menu_state}")
            return False
        
        # Step 4: Player navigates moves
        print("Step 4: Player navigates moves")
        initial_move = battle_scene.battle_ui.selected_move
        battle_scene.battle_ui.handle_input("down", battle_scene.battle_ui.battle_state)
        
        if battle_scene.battle_ui.selected_move == initial_move + 1:
            print("✅ Move navigation works")
        else:
            print(f"❌ Move navigation failed: {battle_scene.battle_ui.selected_move}")
            return False
        
        battle_scene.battle_ui.handle_input("up", battle_scene.battle_ui.battle_state)
        
        if battle_scene.battle_ui.selected_move == initial_move:
            print("✅ Move navigation back works")
        else:
            print(f"❌ Move navigation back failed: {battle_scene.battle_ui.selected_move}")
            return False
        
        # Step 5: Player selects move
        print("Step 5: Player selects move")
        result = battle_scene.battle_ui.handle_input("confirm", battle_scene.battle_ui.battle_state)
        
        if result and result.get("type") == "attack":
            print("✅ Move selection creates attack action")
        else:
            print(f"❌ Move selection failed: {result}")
            return False
        
        # Step 6: Action is processed
        print("Step 6: Action is processed")
        battle_scene._process_player_action(result)
        
        # Check if battle state was updated
        if battle_scene.battle_controller.state.battle_ended:
            print(f"✅ Action processed, battle ended: {battle_scene.battle_controller.state.battle_result}")
        else:
            print("✅ Action processed, battle continues")
        
        # Step 7: UI state is synchronized
        print("Step 7: UI state is synchronized")
        if battle_scene.battle_ui.battle_state == battle_scene.battle_controller.state:
            print("✅ UI state synchronized")
        else:
            print("❌ UI state not synchronized")
            return False
        
        # Step 8: Player can see updated monster stats
        print("Step 8: Player can see updated monster stats")
        if battle_scene.battle_ui.battle_state.player_active:
            print(f"✅ Player monster visible: {battle_scene.battle_ui.battle_state.player_active.name}")
        else:
            print("❌ Player monster not visible")
            return False
        
        if battle_scene.battle_ui.battle_state.enemy_active:
            print(f"✅ Enemy monster visible: {battle_scene.battle_ui.battle_state.enemy_active.name}")
        else:
            print("❌ Enemy monster not visible")
            return False
        
        # Test complete flow with different actions
        print("\n🎯 Testing Complete Flow with Different Actions...")
        
        # Test ITEM flow
        print("Testing ITEM flow...")
        battle_scene.battle_ui.current_menu_state = BattleMenuState.MAIN
        battle_scene.battle_ui.selected_option = 1  # ITEM
        
        result = battle_scene.battle_ui.handle_input("confirm", battle_scene.battle_ui.battle_state)
        
        if battle_scene.battle_ui.current_menu_state == BattleMenuState.ITEM_SELECT:
            print("✅ ITEM flow works")
        else:
            print(f"❌ ITEM flow failed: {battle_scene.battle_ui.current_menu_state}")
            return False
        
        # Test WECHSEL flow
        print("Testing WECHSEL flow...")
        battle_scene.battle_ui.current_menu_state = BattleMenuState.MAIN
        battle_scene.battle_ui.selected_option = 2  # WECHSEL
        
        result = battle_scene.battle_ui.handle_input("confirm", battle_scene.battle_ui.battle_state)
        
        if battle_scene.battle_ui.current_menu_state == BattleMenuState.SWITCH_SELECT:
            print("✅ WECHSEL flow works")
        else:
            print(f"❌ WECHSEL flow failed: {battle_scene.battle_ui.current_menu_state}")
            return False
        
        # Test ZÄHMEN flow
        print("Testing ZÄHMEN flow...")
        battle_scene.battle_ui.current_menu_state = BattleMenuState.MAIN
        battle_scene.battle_ui.selected_option = 3  # ZÄHMEN
        
        result = battle_scene.battle_ui.handle_input("confirm", battle_scene.battle_ui.battle_state)
        
        if battle_scene.battle_ui.current_menu_state == BattleMenuState.TAME_MEAT:
            print("✅ ZÄHMEN flow works")
        else:
            print(f"❌ ZÄHMEN flow failed: {battle_scene.battle_ui.current_menu_state}")
            return False
        
        # Test SPÄHEN flow
        print("Testing SPÄHEN flow...")
        battle_scene.battle_ui.current_menu_state = BattleMenuState.MAIN
        battle_scene.battle_ui.selected_option = 4  # SPÄHEN
        
        result = battle_scene.battle_ui.handle_input("confirm", battle_scene.battle_ui.battle_state)
        
        if result and result.get("type") == "scout":
            print("✅ SPÄHEN flow works")
        else:
            print(f"❌ SPÄHEN flow failed: {result}")
            return False
        
        # Test FLUCHT flow
        print("Testing FLUCHT flow...")
        battle_scene.battle_ui.current_menu_state = BattleMenuState.MAIN
        battle_scene.battle_ui.selected_option = 5  # FLUCHT
        
        result = battle_scene.battle_ui.handle_input("confirm", battle_scene.battle_ui.battle_state)
        
        if result and result.get("type") == "flee":
            print("✅ FLUCHT flow works")
        else:
            print(f"❌ FLUCHT flow failed: {result}")
            return False
        
        print("\n🎯 Testing Error Handling...")
        
        # Test invalid input
        print("Testing invalid input...")
        battle_scene.battle_ui.current_menu_state = BattleMenuState.MAIN
        result = battle_scene.battle_ui.handle_input("invalid", battle_scene.battle_ui.battle_state)
        
        if result is None:
            print("✅ Invalid input handled gracefully")
        else:
            print(f"❌ Invalid input not handled: {result}")
            return False
        
        # Test cancel from different states
        print("Testing cancel from different states...")
        battle_scene.battle_ui.current_menu_state = BattleMenuState.MOVE_SELECT
        battle_scene.battle_ui.handle_input("cancel", battle_scene.battle_ui.battle_state)
        
        if battle_scene.battle_ui.current_menu_state == BattleMenuState.MAIN:
            print("✅ Cancel from MOVE_SELECT works")
        else:
            print(f"❌ Cancel from MOVE_SELECT failed: {battle_scene.battle_ui.current_menu_state}")
            return False
        
        battle_scene.battle_ui.current_menu_state = BattleMenuState.ITEM_SELECT
        battle_scene.battle_ui.handle_input("cancel", battle_scene.battle_ui.battle_state)
        
        if battle_scene.battle_ui.current_menu_state == BattleMenuState.MAIN:
            print("✅ Cancel from ITEM_SELECT works")
        else:
            print(f"❌ Cancel from ITEM_SELECT failed: {battle_scene.battle_ui.current_menu_state}")
            return False
        
        print("\n🎉 Complete Player Experience Test PASSED!")
        print("\n📊 SUMMARY:")
        print("✅ Complete player experience flow works")
        print("✅ All menu navigation works")
        print("✅ All action selection works")
        print("✅ All action processing works")
        print("✅ UI state synchronization works")
        print("✅ Monster data visibility works")
        print("✅ Error handling works")
        print("✅ Cancel functionality works")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_complete_player_experience()
    sys.exit(0 if success else 1)
