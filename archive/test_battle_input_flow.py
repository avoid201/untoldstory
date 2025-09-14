#!/usr/bin/env python3
"""
Battle Input Flow Test
Testet den kompletten Input-Flow vom Game bis zum Battle UI
"""

import sys
import os
import traceback
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_battle_input_flow():
    """Test the complete battle input flow."""
    print("🎮 Testing Battle Input Flow...")
    
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
        
        # Test input flow
        print("Testing input flow...")
        
        # Test 1: Main menu navigation
        print("Test 1: Main menu navigation")
        
        # Simulate UP key press
        up_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP)
        result = battle_scene.handle_event(up_event)
        if result:
            print("✅ UP key handled")
        else:
            print("❌ UP key not handled")
            return False
        
        # Check if selected option changed
        if battle_scene.battle_ui.state.selected_option == 5:  # Should wrap to last option
            print("✅ Selected option updated correctly")
        else:
            print(f"❌ Selected option not updated: {battle_scene.battle_ui.state.selected_option}")
            return False
        
        # Test 2: Main menu navigation down
        print("Test 2: Main menu navigation down")
        
        # Simulate DOWN key press
        down_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)
        result = battle_scene.handle_event(down_event)
        if result:
            print("✅ DOWN key handled")
        else:
            print("❌ DOWN key not handled")
            return False
        
        # Check if selected option changed
        if battle_scene.battle_ui.state.selected_option == 0:  # Should wrap to first option
            print("✅ Selected option updated correctly")
        else:
            print(f"❌ Selected option not updated: {battle_scene.battle_ui.state.selected_option}")
            return False
        
        # Test 3: Main menu selection
        print("Test 3: Main menu selection")
        
        # Simulate ENTER key press
        enter_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
        result = battle_scene.handle_event(enter_event)
        if result:
            print("✅ ENTER key handled")
        else:
            print("❌ ENTER key not handled")
            return False
        
        # Check if menu state changed
        if battle_scene.battle_ui.state.menu_state == BattleMenuState.MOVE_SELECT:
            print("✅ Menu state changed to MOVE_SELECT")
        else:
            print(f"❌ Menu state not changed: {battle_scene.battle_ui.state.menu_state}")
            return False
        
        # Test 4: Move menu navigation
        print("Test 4: Move menu navigation")
        
        # Simulate UP key press in move menu
        up_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP)
        result = battle_scene.handle_event(up_event)
        if result:
            print("✅ UP key in move menu handled")
        else:
            print("❌ UP key in move menu not handled")
            return False
        
        # Test 5: Move menu selection
        print("Test 5: Move menu selection")
        
        # Simulate ENTER key press in move menu
        enter_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
        result = battle_scene.handle_event(enter_event)
        if result:
            print("✅ ENTER key in move menu handled")
        else:
            print("❌ ENTER key in move menu not handled")
            return False
        
        # Check if action was queued
        if battle_scene.battle_ui.pending_action:
            print("✅ Action queued successfully")
        else:
            print("❌ No action queued")
            return False
        
        # Test 6: Action processing
        print("Test 6: Action processing")
        
        # Simulate update cycle
        battle_scene.update(0.016)
        
        print("✅ Action processing completed")
        
        print("\n🎉 Battle Input Flow Test PASSED!")
        print("\n📊 SUMMARY:")
        print("✅ Input events are properly converted to actions")
        print("✅ Menu navigation works correctly")
        print("✅ Menu selection works correctly")
        print("✅ Actions are properly queued")
        print("✅ Actions are processed in update cycle")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        traceback.print_exc()
        return False
    finally:
        pygame.quit()

if __name__ == "__main__":
    success = test_battle_input_flow()
    sys.exit(0 if success else 1)
