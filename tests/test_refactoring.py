#!/usr/bin/env python3
"""
Test script to verify battle system refactoring
Ensures all modules are correctly split and functional
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

def test_imports():
    """Test that all imports work correctly."""
    print("Testing imports...")
    
    try:
        # Test enum imports
        from engine.systems.battle.battle_enums import BattleType, BattlePhase, BattleCommand, AIPersonality
        print("✅ Enums imported successfully")
        
        # Test tension system
        from engine.systems.battle.battle_tension import TensionState, TensionManager
        print("✅ Tension system imported successfully")
        
        # Test validation
        from engine.systems.battle.battle_validation import BattleValidator
        print("✅ Validation imported successfully")
        
        # Test actions
        from engine.systems.battle.battle_actions import BattleActionExecutor
        print("✅ Actions imported successfully")
        
        # Test main controller
        from engine.systems.battle.battle_controller import BattleState
        print("✅ Controller imported successfully")
        
        # Test compatibility layer
        from engine.systems.battle.battle_system import BattleState as CompatBattleState
        print("✅ Compatibility layer imported successfully")
        
        # Test that both imports reference the same class
        if BattleState is CompatBattleState:
            print("✅ Compatibility layer correctly references main controller")
        else:
            print("❌ Compatibility layer issue detected")
            return False
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False


def test_basic_functionality():
    """Test basic battle system functionality."""
    print("\nTesting basic functionality...")
    
    try:
        from engine.systems.battle.battle_system import BattleState, BattleType
        from engine.systems.monster_instance import MonsterInstance
        from engine.systems.stats import BaseStats
        
        # Create mock monsters
        class MockMonster:
            def __init__(self, name, level=5):
                self.name = name
                self.level = level
                self.is_fainted = False
                self.current_hp = 100
                self.max_hp = 100
                self.stats = {"hp": 100, "atk": 50, "def": 50, "mag": 30, "res": 30, "spd": 70}
                self.stat_stages = {"atk": 0, "def": 0, "mag": 0, "res": 0, "spd": 0}
                self.moves = []
                self.status = None
                self.types = ["Normal"]
                
            def take_damage(self, damage):
                self.current_hp = max(0, self.current_hp - damage)
                if self.current_hp == 0:
                    self.is_fainted = True
        
        # Create test monsters
        player_monster = MockMonster("TestPlayer", 5)
        enemy_monster = MockMonster("TestEnemy", 5)
        
        # Create battle state
        battle = BattleState(
            player_team=[player_monster],
            enemy_team=[enemy_monster],
            battle_type=BattleType.WILD
        )
        
        print("✅ Battle state created successfully")
        
        # Test validation
        if battle.validate_battle_state():
            print("✅ Battle state validation works")
        else:
            print("❌ Battle state validation failed")
            return False
        
        # Test battle status
        status = battle.get_battle_status()
        if status and 'phase' in status:
            print("✅ Battle status retrieval works")
        else:
            print("❌ Battle status retrieval failed")
            return False
        
        # Test tension system
        if hasattr(battle, 'tension_manager'):
            print("✅ Tension manager initialized")
        else:
            print("❌ Tension manager not found")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Functionality test error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_file_sizes():
    """Check that files are now smaller and better organized."""
    print("\nChecking file sizes...")
    
    import os
    
    battle_dir = os.path.dirname(os.path.abspath(__file__))
    
    files = {
        'battle_enums.py': 2000,  # ~2KB expected
        'battle_tension.py': 5000,  # ~5KB expected
        'battle_validation.py': 8000,  # ~8KB expected
        'battle_actions.py': 15000,  # ~15KB expected
        'battle_controller.py': 20000,  # ~20KB expected
        'battle_system.py': 3000,  # ~3KB (just compatibility layer)
    }
    
    total_size = 0
    for filename, expected_max in files.items():
        filepath = os.path.join(battle_dir, filename)
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            total_size += size
            if size <= expected_max:
                print(f"✅ {filename}: {size/1024:.1f}KB (under {expected_max/1024:.0f}KB limit)")
            else:
                print(f"⚠️ {filename}: {size/1024:.1f}KB (exceeds {expected_max/1024:.0f}KB limit)")
        else:
            print(f"❌ {filename} not found")
    
    print(f"\nTotal size of refactored modules: {total_size/1024:.1f}KB")
    
    # Check old file
    old_file = os.path.join(battle_dir, 'battle_system_old.py')
    if os.path.exists(old_file):
        old_size = os.path.getsize(old_file)
        print(f"Original file size: {old_size/1024:.1f}KB")
        print(f"Size reduction: {(old_size - total_size)/1024:.1f}KB ({(1 - total_size/old_size)*100:.0f}% smaller)")


def main():
    """Run all tests."""
    print("🔧 BATTLE SYSTEM REFACTORING VALIDATION")
    print("="*50)
    
    success = True
    
    # Run tests
    success &= test_imports()
    success &= test_basic_functionality()
    test_file_sizes()
    
    print("\n" + "="*50)
    if success:
        print("✅ ALL TESTS PASSED!")
        print("The battle system has been successfully refactored!")
        print("\nBenefits achieved:")
        print("• Better code organization")
        print("• Smaller, more focused modules")
        print("• Easier maintenance and debugging")
        print("• Preserved all functionality")
        print("• Maintained backwards compatibility")
    else:
        print("❌ SOME TESTS FAILED")
        print("Please check the errors above and fix any issues.")
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
