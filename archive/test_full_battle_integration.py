#!/usr/bin/env python3
"""
Vollständiger Battle Integration Test
Testet das komplette Battle System mit UI Integration
"""

import sys
import os
import traceback
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_full_battle_integration():
    """Test the complete battle integration with UI."""
    print("🎮 Testing Full Battle Integration...")
    
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
        
        # Test UI state sync
        if battle_scene.battle_ui.battle_state:
            print("✅ UI state synchronized")
        else:
            print("❌ UI state not synchronized")
            return False
        
        # Test action creation
        test_move = Move(
            id="test_attack",
            name="Test Attack",
            type="normal",
            category=MoveCategory.PHYSICAL,
            power=40,
            accuracy=100,
            priority=0,
            targeting=MoveTarget.ENEMY,
            effects=[],
            description="A basic test attack"
        )
        
        # Test UI action creation
        ui_action = {
            "type": "attack",
            "actor": player_monster,
            "move": test_move,
            "target": enemy_monster
        }
        
        # Test action processing
        battle_scene._process_player_action(ui_action)
        
        print("✅ Action processed successfully")
        
        # Check if battle ended
        if battle_controller.state.battle_ended:
            print(f"✅ Battle ended: {battle_controller.state.battle_result}")
        else:
            print("✅ Battle continues")
        
        print("🎉 Full battle integration test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_full_battle_integration()
    sys.exit(0 if success else 1)
