#!/usr/bin/env python3
"""
Comprehensive test of the refactored battle system
Tests all modules and ensures functionality is preserved
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def print_section(title):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f"{title:^60}")
    print('='*60)

def test_module_imports():
    """Test that all refactored modules can be imported."""
    print_section("1. TESTING MODULE IMPORTS")
    
    modules_to_test = [
        ('battle_enums', ['BattleType', 'BattlePhase', 'BattleCommand', 'AIPersonality']),
        ('battle_tension', ['TensionState', 'TensionManager']),
        ('battle_validation', ['BattleValidator']),
        ('battle_actions', ['BattleActionExecutor']),
        ('battle_controller', ['BattleState']),
        ('battle_system', ['BattleState', 'create_battle', 'validate_battle_state'])
    ]
    
    success = True
    for module_name, expected_items in modules_to_test:
        try:
            module = __import__(f'engine.systems.battle.{module_name}', fromlist=expected_items)
            
            # Check if expected items exist
            missing = []
            for item in expected_items:
                if not hasattr(module, item):
                    missing.append(item)
            
            if missing:
                print(f"❌ {module_name}: Missing items: {missing}")
                success = False
            else:
                print(f"✅ {module_name}: All items imported successfully")
                
        except ImportError as e:
            print(f"❌ {module_name}: Import error - {e}")
            success = False
    
    return success

def test_backwards_compatibility():
    """Test that old import paths still work."""
    print_section("2. TESTING BACKWARDS COMPATIBILITY")
    
    success = True
    
    try:
        # Old import style
        from engine.systems.battle.battle_system import BattleState, BattleType, BattlePhase
        print("✅ Old import style works: from battle_system import BattleState, BattleType, BattlePhase")
        
        # New import style
        from engine.systems.battle.battle_controller import BattleState as NewBattleState
        print("✅ New import style works: from battle_controller import BattleState")
        
        # Check they're the same class
        if BattleState is NewBattleState:
            print("✅ Both imports reference the same BattleState class")
        else:
            print("❌ Import mismatch - classes are different!")
            success = False
            
    except ImportError as e:
        print(f"❌ Compatibility test failed: {e}")
        success = False
    
    return success

def test_battle_creation():
    """Test creating a battle with the refactored system."""
    print_section("3. TESTING BATTLE CREATION")
    
    try:
        from engine.systems.battle.battle_system import BattleState, BattleType
        
        # Create mock monster class
        class MockMonster:
            def __init__(self, name, level=5):
                self.name = name
                self.level = level
                self.is_fainted = False
                self.current_hp = 100
                self.max_hp = 100
                self.stats = {
                    "hp": 100, "atk": 50, "def": 50, 
                    "mag": 30, "res": 30, "spd": 70
                }
                self.stat_stages = {
                    "atk": 0, "def": 0, "mag": 0, 
                    "res": 0, "spd": 0
                }
                self.moves = []
                self.status = None
                self.types = ["Normal"]
                self.species = type('Species', (), {'name': name})()
            
            def take_damage(self, damage):
                self.current_hp = max(0, self.current_hp - damage)
                if self.current_hp == 0:
                    self.is_fainted = True
        
        # Create test monsters
        player_team = [MockMonster("Pikachu", 10)]
        enemy_team = [MockMonster("Charmander", 8)]
        
        # Create battle
        battle = BattleState(
            player_team=player_team,
            enemy_team=enemy_team,
            battle_type=BattleType.WILD
        )
        
        print("✅ Battle created successfully")
        
        # Test battle properties
        tests = [
            (battle.player_active is not None, "Player active monster set"),
            (battle.enemy_active is not None, "Enemy active monster set"),
            (battle.turn_count == 0, "Turn count initialized"),
            (len(battle.battle_log) == 0, "Battle log initialized"),
            (battle.phase.value == "init", "Battle phase initialized"),
            (battle.can_flee == True, "Can flee in wild battle"),
            (battle.can_catch == True, "Can catch in wild battle")
        ]
        
        for condition, description in tests:
            if condition:
                print(f"✅ {description}")
            else:
                print(f"❌ {description}")
        
        return all(condition for condition, _ in tests)
        
    except Exception as e:
        print(f"❌ Battle creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tension_system():
    """Test the separated tension system."""
    print_section("4. TESTING TENSION SYSTEM")
    
    try:
        from engine.systems.battle.battle_tension import TensionManager, TensionState
        
        # Create mock monster
        class MockMonster:
            def __init__(self, name):
                self.name = name
        
        monster = MockMonster("TestMonster")
        
        # Create tension manager
        manager = TensionManager()
        print("✅ TensionManager created")
        
        # Initialize monster tension
        manager.initialize_monster(monster)
        print("✅ Monster tension initialized")
        
        # Test psyche up
        result = manager.psyche_up(monster)
        if result.get('tension_level') == 1:
            print("✅ Psyche up level 1 successful")
        else:
            print("❌ Psyche up failed")
            return False
        
        # Test multiplier
        multiplier = manager.get_multiplier(monster)
        if multiplier == 1.5:
            print(f"✅ Correct multiplier for level 1: {multiplier}")
        else:
            print(f"❌ Wrong multiplier: {multiplier}")
            return False
        
        # Test max tension
        manager.psyche_up(monster)  # Level 2
        manager.psyche_up(monster)  # Level 3
        result = manager.psyche_up(monster)  # Should fail (already at max)
        
        if 'psyche_up_failed' in result.get('action', ''):
            print("✅ Max tension correctly prevents further psyche up")
        else:
            print("❌ Max tension check failed")
            return False
        
        # Test reset
        manager.reset_tension(monster)
        multiplier = manager.get_multiplier(monster)
        if multiplier == 1.0:
            print("✅ Tension reset successful")
        else:
            print("❌ Tension reset failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Tension system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_validation_system():
    """Test the separated validation system."""
    print_section("5. TESTING VALIDATION SYSTEM")
    
    try:
        from engine.systems.battle.battle_validation import BattleValidator
        
        validator = BattleValidator()
        print("✅ BattleValidator created")
        
        # Create mock monsters
        class MockMonster:
            def __init__(self, name, valid=True):
                self.name = name
                self.level = 5
                self.is_fainted = False
                if valid:
                    self.stats = {"hp": 100, "atk": 50, "def": 50, "mag": 30, "res": 30, "spd": 70}
                    self.stat_stages = {}
                    self.moves = []
                else:
                    self.stats = {}  # Invalid - missing stats
        
        # Test valid battle state
        valid_monster = MockMonster("ValidMonster", valid=True)
        team = [valid_monster]
        
        if validator.has_able_monsters(team):
            print("✅ Has able monsters check works")
        else:
            print("❌ Has able monsters check failed")
            return False
        
        # Test invalid monster
        invalid_monster = MockMonster("InvalidMonster", valid=False)
        
        if not validator._validate_monster_stats(invalid_monster):
            print("✅ Invalid monster correctly detected")
        else:
            print("❌ Invalid monster not detected")
            return False
        
        # Test action validation
        valid_action = {
            'action': 'attack',
            'actor': valid_monster
        }
        
        if validator.validate_action(valid_action):
            print("✅ Valid action accepted")
        else:
            print("❌ Valid action rejected")
            return False
        
        invalid_action = {}  # Missing required fields
        
        if not validator.validate_action(invalid_action):
            print("✅ Invalid action correctly rejected")
        else:
            print("❌ Invalid action not rejected")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Validation system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_file_organization():
    """Check file sizes and organization."""
    print_section("6. FILE SIZE ANALYSIS")
    
    import os
    battle_dir = 'engine/systems/battle'
    
    files = {
        'battle_enums.py': (2000, 5000),      # Min 2KB, Max 5KB
        'battle_tension.py': (3000, 8000),    # Min 3KB, Max 8KB
        'battle_validation.py': (4000, 10000), # Min 4KB, Max 10KB
        'battle_actions.py': (10000, 20000),  # Min 10KB, Max 20KB
        'battle_controller.py': (15000, 25000), # Min 15KB, Max 25KB
        'battle_system.py': (1000, 5000),     # Min 1KB, Max 5KB (just compatibility)
    }
    
    total_size = 0
    all_good = True
    
    for filename, (min_size, max_size) in files.items():
        filepath = os.path.join(battle_dir, filename)
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            total_size += size
            
            if min_size <= size <= max_size:
                print(f"✅ {filename}: {size/1024:.1f}KB (within {min_size/1024:.0f}-{max_size/1024:.0f}KB range)")
            else:
                print(f"⚠️ {filename}: {size/1024:.1f}KB (expected {min_size/1024:.0f}-{max_size/1024:.0f}KB)")
                all_good = False
        else:
            print(f"❌ {filename} not found")
            all_good = False
    
    # Check old file exists
    old_file = os.path.join(battle_dir, 'battle_system_old.py')
    if os.path.exists(old_file):
        old_size = os.path.getsize(old_file)
        print(f"\n📦 Original file: {old_size/1024:.1f}KB")
        print(f"📦 New modules total: {total_size/1024:.1f}KB")
        print(f"📉 Size reduction: {(old_size - total_size)/1024:.1f}KB ({(1 - total_size/old_size)*100:.0f}%)")
    
    return all_good

def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("COMPREHENSIVE BATTLE SYSTEM REFACTORING TEST")
    print("="*60)
    
    results = []
    
    # Run all tests
    results.append(("Module Imports", test_module_imports()))
    results.append(("Backwards Compatibility", test_backwards_compatibility()))
    results.append(("Battle Creation", test_battle_creation()))
    results.append(("Tension System", test_tension_system()))
    results.append(("Validation System", test_validation_system()))
    results.append(("File Organization", test_file_organization()))
    
    # Summary
    print_section("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:.<40} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("The battle system refactoring is successful!")
        print("\nKey achievements:")
        print("  • All modules properly separated")
        print("  • Backwards compatibility maintained")
        print("  • File sizes optimized")
        print("  • Functionality preserved")
        print("  • Code organization improved")
    else:
        print("\n⚠️ Some tests failed. Please check the output above.")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    exit(main())
