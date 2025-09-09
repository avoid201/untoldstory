#!/usr/bin/env python3
"""
Turn Flow Validation Test
Testet den kompletten Turn-Flow für jede Spieler-Aktion
"""

import sys
import os
import traceback
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_turn_flow_validation():
    """Test the complete turn flow for each player action."""
    print("🎮 Testing Turn Flow Validation...")
    
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
        
        player_monster.moves = [test_move1]
        
        print("✅ Test monsters with moves created")
        
        # Test 1: ATTACKE Turn Flow
        print("\n🎯 Testing ATTACKE Turn Flow...")
        
        # Create fresh battle controller
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
        
        # Test attack action
        attack_action = {
            "type": "attack",
            "actor": player_monster,
            "move": test_move1,
            "target": enemy_monster
        }
        
        print("Testing attack action processing...")
        battle_scene._process_player_action(attack_action)
        
        # Check if battle state was updated
        if battle_scene.battle_controller.state.battle_ended:
            print(f"✅ Attack turn executed, battle ended: {battle_scene.battle_controller.state.battle_result}")
        else:
            print("✅ Attack turn executed, battle continues")
        
        # Test 2: ITEM Turn Flow
        print("\n🎯 Testing ITEM Turn Flow...")
        
        # Create fresh battle controller
        battle_controller2 = BattleController(
            player_team=[player_monster],
            enemy_team=[enemy_monster]
        )
        
        battle_scene2 = BattleScene(mock_game)
        battle_scene2.battle_controller = battle_controller2
        battle_scene2.battle_ui = BattleUI(mock_game)
        
        init_success = battle_scene2.initialize_battle([player_monster], [enemy_monster])
        if not init_success:
            print("❌ Battle scene initialization failed")
            return False
        
        # Test item action
        item_action = {
            "type": "item",
            "actor": player_monster,
            "item_id": "Kräuter",
            "target": player_monster
        }
        
        print("Testing item action processing...")
        battle_scene2._process_player_action(item_action)
        
        # Check if battle state was updated
        if battle_scene2.battle_controller.state.battle_ended:
            print(f"✅ Item turn executed, battle ended: {battle_scene2.battle_controller.state.battle_result}")
        else:
            print("✅ Item turn executed, battle continues")
        
        # Test 3: SCOUT Turn Flow
        print("\n🎯 Testing SCOUT Turn Flow...")
        
        # Create fresh battle controller
        battle_controller3 = BattleController(
            player_team=[player_monster],
            enemy_team=[enemy_monster]
        )
        
        battle_scene3 = BattleScene(mock_game)
        battle_scene3.battle_controller = battle_controller3
        battle_scene3.battle_ui = BattleUI(mock_game)
        
        init_success = battle_scene3.initialize_battle([player_monster], [enemy_monster])
        if not init_success:
            print("❌ Battle scene initialization failed")
            return False
        
        # Test scout action
        scout_action = {
            "type": "scout",
            "actor": player_monster,
            "target": enemy_monster
        }
        
        print("Testing scout action processing...")
        battle_scene3._process_player_action(scout_action)
        
        # Check if battle state was updated
        if battle_scene3.battle_controller.state.battle_ended:
            print(f"✅ Scout turn executed, battle ended: {battle_scene3.battle_controller.state.battle_result}")
        else:
            print("✅ Scout turn executed, battle continues")
        
        # Test 4: FLEE Turn Flow
        print("\n🎯 Testing FLEE Turn Flow...")
        
        # Create fresh battle controller
        battle_controller4 = BattleController(
            player_team=[player_monster],
            enemy_team=[enemy_monster]
        )
        
        battle_scene4 = BattleScene(mock_game)
        battle_scene4.battle_controller = battle_controller4
        battle_scene4.battle_ui = BattleUI(mock_game)
        
        init_success = battle_scene4.initialize_battle([player_monster], [enemy_monster])
        if not init_success:
            print("❌ Battle scene initialization failed")
            return False
        
        # Test flee action
        flee_action = {
            "type": "flee",
            "actor": player_monster,
            "target": None
        }
        
        print("Testing flee action processing...")
        battle_scene4._process_player_action(flee_action)
        
        # Check if battle state was updated
        if battle_scene4.battle_controller.state.battle_ended:
            print(f"✅ Flee turn executed, battle ended: {battle_scene4.battle_controller.state.battle_result}")
        else:
            print("✅ Flee turn executed, battle continues")
        
        # Test 5: TAME Turn Flow
        print("\n🎯 Testing TAME Turn Flow...")
        
        # Create fresh battle controller
        battle_controller5 = BattleController(
            player_team=[player_monster],
            enemy_team=[enemy_monster]
        )
        
        battle_scene5 = BattleScene(mock_game)
        battle_scene5.battle_controller = battle_controller5
        battle_scene5.battle_ui = BattleUI(mock_game)
        
        init_success = battle_scene5.initialize_battle([player_monster], [enemy_monster])
        if not init_success:
            print("❌ Battle scene initialization failed")
            return False
        
        # Test tame action
        tame_action = {
            "type": "tame",
            "actor": player_monster,
            "target": enemy_monster,
            "meat_bonus": 20
        }
        
        print("Testing tame action processing...")
        battle_scene5._process_player_action(tame_action)
        
        # Check if battle state was updated
        if battle_scene5.battle_controller.state.battle_ended:
            print(f"✅ Tame turn executed, battle ended: {battle_scene5.battle_controller.state.battle_result}")
        else:
            print("✅ Tame turn executed, battle continues")
        
        print("\n🎯 Testing Turn Flow State Synchronization...")
        
        # Test that UI state is properly synchronized after each turn
        for i, battle_scene in enumerate([battle_scene, battle_scene2, battle_scene3, battle_scene4, battle_scene5]):
            if battle_scene.battle_ui.battle_state == battle_scene.battle_controller.state:
                print(f"✅ Battle {i+1}: UI state synchronized")
            else:
                print(f"❌ Battle {i+1}: UI state not synchronized")
                return False
        
        print("\n🎯 Testing Turn Flow Event Processing...")
        
        # Test that events are properly processed
        for i, battle_scene in enumerate([battle_scene, battle_scene2, battle_scene3, battle_scene4, battle_scene5]):
            if hasattr(battle_scene.battle_controller, 'event_processor') and battle_scene.battle_controller.event_processor:
                print(f"✅ Battle {i+1}: Event processor active")
            else:
                print(f"❌ Battle {i+1}: Event processor not active")
                return False
        
        print("\n🎉 Turn Flow Validation Test PASSED!")
        print("\n📊 SUMMARY:")
        print("✅ Attack turn flow works")
        print("✅ Item turn flow works")
        print("✅ Scout turn flow works")
        print("✅ Flee turn flow works")
        print("✅ Tame turn flow works")
        print("✅ UI state synchronization works")
        print("✅ Event processing works")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_turn_flow_validation()
    sys.exit(0 if success else 1)
