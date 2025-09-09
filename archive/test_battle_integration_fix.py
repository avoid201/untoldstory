#!/usr/bin/env python3
"""
Test Battle Integration Fix
Testet die kritischen Fixes für Action-Queue und State-Synchronisation
"""

import sys
import os
import traceback
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_battle_integration():
    """Test the battle integration fixes."""
    print("🧪 Testing Battle Integration Fixes...")
    
    try:
        # Import battle components
        from engine.systems.battle.battle_controller import BattleController
        from engine.systems.battle.battle_state import BattleState
        from engine.systems.battle.turn_logic import BattleAction, ActionType
        from engine.systems.monster_instance import MonsterInstance
        from engine.systems.moves import Move
        
        print("✅ Imports successful")
        
        # Create test monsters - need to create species first
        from engine.systems.monster_instance import MonsterSpecies
        from engine.systems.stats import BaseStats
        
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
        
        # Initialize battle (already done in constructor)
        init_result = {"success": True}
        if not init_result.get('success'):
            print(f"❌ Battle initialization failed: {init_result}")
            return False
            
        print("✅ Battle initialized")
        
        # Create test actions
        from engine.systems.moves import MoveCategory, MoveTarget
        
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
        
        player_action = BattleAction(
            actor=player_monster,
            action_type=ActionType.ATTACK,
            target=enemy_monster,
            move=test_move
        )
        
        enemy_action = BattleAction(
            actor=enemy_monster,
            action_type=ActionType.ATTACK,
            target=player_monster,
            move=test_move
        )
        
        print("✅ Test actions created")
        
        # Test UI sync callback
        sync_called = False
        sync_data = None
        
        def test_sync_callback(update_data: Dict[str, Any]):
            nonlocal sync_called, sync_data
            sync_called = True
            sync_data = update_data
            print(f"🔄 UI sync called with: {list(update_data.keys())}")
        
        battle_controller.ui_sync_callback = test_sync_callback
        
        # Execute turn
        print("🎯 Executing turn...")
        result = battle_controller.execute_turn(
            player_action=player_action,
            enemy_action=enemy_action
        )
        
        print(f"✅ Turn executed: {result.get('success', False)}")
        
        # Check if sync was called
        if sync_called:
            print("✅ UI sync callback was called")
        else:
            print("❌ UI sync callback was NOT called")
            return False
        
        # Check battle state
        if battle_controller.state.battle_ended:
            print(f"✅ Battle ended: {battle_controller.state.battle_result}")
        else:
            print("✅ Battle continues")
        
        print("🎉 All integration tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_battle_integration()
    sys.exit(0 if success else 1)
