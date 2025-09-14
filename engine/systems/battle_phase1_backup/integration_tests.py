#!/usr/bin/env python3
"""
Battle System Integration Tests - Emergency Split
================================================
Simplified integration tests to comply with 300-line limit.
"""

import sys
import os
# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))

import time
from typing import List, Dict, Any

def create_test_monster(name: str) -> Dict[str, Any]:
    """Create a test monster for integration testing"""
    return {
        'name': name,
        'nickname': name,
        'level': 5,
        'current_hp': 100,
        'max_hp': 100,
        'is_fainted': False,
        'status': None,
        'status_turns': 0,
        'stats': {'atk': 50, 'def': 40, 'spd': 60, 'hp': 100},
        'moves': [{'name': 'Tackle', 'power': 40, 'type': 'NORMAL', 'accuracy': 100}]
    }

def test_imports() -> bool:
    """Test 1: All imports work correctly"""
    print("🧪 Testing imports...")
    
    try:
        from engine.systems.battle import BattleController, BattleState
        from engine.systems.battle import ActionProcessor, EventProcessor
        from engine.systems.battle import BattleValidator, BattleErrorRecovery
        from engine.systems.battle.core import BattleControllerCore
        from engine.systems.battle.processors import AttackActionProcessor
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

def test_battle_controller() -> bool:
    """Test 2: BattleController can be initialized"""
    print("🧪 Testing BattleController...")
    
    try:
        from engine.systems.battle import BattleController
        
        player_team = [create_test_monster("PlayerMonster")]
        enemy_team = [create_test_monster("EnemyMonster")]
        
        controller = BattleController(
            player_team=player_team,
            enemy_team=enemy_team
        )
        
        assert controller is not None, "Controller should be instantiable"
        assert hasattr(controller, 'state'), "Controller should have state"
        
        print("✅ BattleController test successful")
        return True
    except Exception as e:
        print(f"❌ BattleController test failed: {e}")
        return False

def test_core_modules() -> bool:
    """Test 3: Core modules work"""
    print("🧪 Testing core modules...")
    
    try:
        from engine.systems.battle.core import (
            BattleControllerCore, BattleControllerState,
            BattleControllerActions, BattleControllerPhases
        )
        
        player_team = [create_test_monster("PlayerMonster")]
        enemy_team = [create_test_monster("EnemyMonster")]
        
        core = BattleControllerCore(player_team, enemy_team)
        state = BattleControllerState()
        actions = BattleControllerActions()
        phases = BattleControllerPhases()
        
        assert core is not None, "Core should be instantiable"
        assert state is not None, "State should be instantiable"
        assert actions is not None, "Actions should be instantiable"
        assert phases is not None, "Phases should be instantiable"
        
        print("✅ Core modules test successful")
        return True
    except Exception as e:
        print(f"❌ Core modules test failed: {e}")
        return False

def test_processors() -> bool:
    """Test 4: Processor system works"""
    print("🧪 Testing processors...")
    
    try:
        from engine.systems.battle.processors import (
            AttackActionProcessor, ItemActionProcessor, SpecialActionProcessor
        )
        from engine.systems.battle import BattleState
        
        battle_state = BattleState(
            player_team=[create_test_monster("PlayerMonster")],
            enemy_team=[create_test_monster("EnemyMonster")],
            player_active=create_test_monster("PlayerMonster"),
            enemy_active=create_test_monster("EnemyMonster")
        )
        
        attack_processor = AttackActionProcessor(battle_state)
        item_processor = ItemActionProcessor(battle_state)
        special_processor = SpecialActionProcessor(battle_state)
        
        assert attack_processor is not None, "Attack processor should be instantiable"
        assert item_processor is not None, "Item processor should be instantiable"
        assert special_processor is not None, "Special processor should be instantiable"
        
        print("✅ Processors test successful")
        return True
    except Exception as e:
        print(f"❌ Processors test failed: {e}")
        return False

def test_error_recovery() -> bool:
    """Test 5: Error recovery system works"""
    print("🧪 Testing error recovery...")
    
    try:
        from engine.systems.battle import BattleErrorRecovery
        
        @BattleErrorRecovery.with_fallback(fallback_value={'success': False, 'error': 'Test fallback'})
        def test_function():
            raise Exception("Test error")
        
        result = test_function()
        assert result['success'] == False, "Fallback should be called"
        assert 'error' in result, "Fallback should contain error info"
        
        print("✅ Error recovery test successful")
        return True
    except Exception as e:
        print(f"❌ Error recovery test failed: {e}")
        return False

def test_file_sizes() -> bool:
    """Test 6: All files are under 300 lines"""
    print("🧪 Testing file sizes...")
    
    try:
        import os
        import glob
        
        battle_dir = "/Users/leon/Desktop/untold_story/engine/systems/battle"
        python_files = glob.glob(f"{battle_dir}/**/*.py", recursive=True)
        
        oversized_files = []
        for file_path in python_files:
            if '__pycache__' in file_path or '_EMERGENCY_BACKUP' in file_path:
                continue
                
            with open(file_path, 'r', encoding='utf-8') as f:
                line_count = len(f.readlines())
            
            if line_count > 300:
                oversized_files.append((file_path, line_count))
        
        if oversized_files:
            print(f"❌ Files exceed 300 lines:")
            for file_path, line_count in oversized_files:
                print(f"  - {file_path}: {line_count} lines")
            return False
        
        print("✅ All files under 300 lines")
        return True
        
    except Exception as e:
        print(f"❌ File size test failed: {e}")
        return False

def main():
    """Run all integration tests"""
    print("🚀 BATTLE SYSTEM INTEGRATION TESTS (Emergency Split)")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_battle_controller,
        test_core_modules,
        test_processors,
        test_error_recovery,
        test_file_sizes
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"💥 Test {test.__name__} crashed: {e}")
            failed += 1
    
    print("\n📊 INTEGRATION TEST RESULTS")
    print("=" * 60)
    print(f"✅ Tests passed: {passed}")
    print(f"❌ Tests failed: {failed}")
    print(f"📈 Success rate: {(passed / (passed + failed)) * 100:.1f}%")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED!")
        print("🎮 Battle System is ready for production!")
        return 0
    else:
        print(f"\n💥 {failed} TESTS FAILED!")
        print("🔧 Integration needs fixes before production.")
        return 1

if __name__ == "__main__":
    sys.exit(main())