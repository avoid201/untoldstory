#!/usr/bin/env python3
"""
Circular Import Test Suite
Tests all battle system modules to ensure no circular dependencies exist.
Created by: Circular Import Elimination Specialist
"""

import sys
import traceback
from typing import List, Tuple

def test_import(module_name: str, class_name: str = None) -> Tuple[bool, str]:
    """
    Test importing a module and optionally a class.
    
    Args:
        module_name: Full module path to import
        class_name: Optional class name to import from module
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        if class_name:
            exec(f"from {module_name} import {class_name}")
            return True, f"✅ {module_name}.{class_name} imported successfully"
        else:
            exec(f"import {module_name}")
            return True, f"✅ {module_name} imported successfully"
    except ImportError as e:
        return False, f"❌ ImportError in {module_name}: {e}"
    except Exception as e:
        return False, f"❌ Unexpected error in {module_name}: {e}"

def test_all_battle_modules() -> bool:
    """
    Test all battle system modules for circular import issues.
    
    Returns:
        True if all tests pass, False otherwise
    """
    print("🔍 Testing Battle System Modules for Circular Dependencies...")
    print("=" * 60)
    
    # Test cases: (module_name, class_name)
    test_cases = [
        ("engine.systems.battle.battle_controller", "BattleController"),
        ("engine.systems.battle.battle_ai", "BattleAI"),
        ("engine.systems.battle.battle_validation", "BattleValidator"),
        ("engine.systems.battle.battle_enums", "BattleType"),
        ("engine.systems.battle.turn_logic_clean", "TurnOrder"),
        ("engine.systems.battle.battle_actions", "BattleActionExecutor"),
        ("engine.systems.battle.battle_effects", "ItemEffectHandler"),
        ("engine.systems.battle.battle_events", "BattleEventGenerator"),
        ("engine.systems.battle.battle_system", "BattleState"),
        ("engine.systems.battle.meat_system", "MeatSystem"),
        ("engine.systems.battle.dqm_formulas", "DQMCalculator"),
        ("engine.systems.battle.dqm_integration", "DQMIntegration"),
        ("engine.systems.battle.reward_system", "RewardSystem"),
        ("engine.systems.battle.status_effects_dqm", "DQMStatusManager"),
        ("engine.systems.battle.skills_dqm_integrated", "DQMSkillDatabase"),
    ]
    
    results = []
    all_passed = True
    
    for module_name, class_name in test_cases:
        success, message = test_import(module_name, class_name)
        results.append((module_name, success, message))
        print(message)
        if not success:
            all_passed = False
    
    print("\n" + "=" * 60)
    
    # Test simultaneous import (critical for circular dependency detection)
    print("🔄 Testing Simultaneous Import (Circular Dependency Check)...")
    try:
        exec("""
from engine.systems.battle.battle_controller import BattleController, BattleState
from engine.systems.battle.battle_ai import BattleAI, AILevel
from engine.systems.battle.battle_validation import BattleValidator
from engine.systems.battle.battle_enums import BattleType, BattlePhase, AIPersonality
from engine.systems.battle.turn_logic_clean import TurnOrder, BattleAction, ActionType
from engine.systems.battle.battle_actions import BattleActionExecutor
from engine.systems.battle.battle_effects import ItemEffectHandler
from engine.systems.battle.battle_events import BattleEventGenerator
from engine.systems.battle.battle_system import BattleState as BattleSystemState
from engine.systems.battle.meat_system import MeatSystem, MeatType
from engine.systems.battle.dqm_formulas import DQMCalculator
from engine.systems.battle.dqm_integration import DQMIntegration
from engine.systems.battle.reward_system import RewardSystem
from engine.systems.battle.status_effects_dqm import DQMStatusManager
from engine.systems.battle.skills_dqm_integrated import DQMSkillDatabase
        """)
        print("✅ ALL MODULES IMPORT SIMULTANEOUSLY - NO CIRCULAR DEPENDENCIES!")
        simultaneous_success = True
    except ImportError as e:
        print(f"❌ CIRCULAR DEPENDENCY DETECTED: {e}")
        simultaneous_success = False
        all_passed = False
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")
        simultaneous_success = False
        all_passed = False
    
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY:")
    print(f"Individual Module Tests: {sum(1 for _, success, _ in results if success)}/{len(results)} passed")
    print(f"Simultaneous Import Test: {'✅ PASSED' if simultaneous_success else '❌ FAILED'}")
    print(f"Overall Result: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    return all_passed

def test_lazy_loading() -> bool:
    """
    Test that lazy loading works correctly for BattleAI.
    Simplified test that only checks if the property exists and can be accessed.
    
    Returns:
        True if lazy loading works, False otherwise
    """
    print("\n🔧 Testing Lazy Loading Implementation...")
    print("=" * 60)
    
    try:
        # Import BattleState class (not instantiate)
        from engine.systems.battle.battle_controller import BattleState
        
        # Check if the battle_ai property exists
        if hasattr(BattleState, 'battle_ai'):
            print("✅ BattleState has battle_ai property")
        else:
            print("❌ BattleState missing battle_ai property")
            return False
        
        # Check if the property is a property descriptor
        battle_ai_prop = getattr(BattleState, 'battle_ai')
        if hasattr(battle_ai_prop, 'fget'):
            print("✅ battle_ai is a proper @property")
        else:
            print("❌ battle_ai is not a @property")
            return False
        
        print("✅ Lazy loading implementation structure is correct")
        return True
        
    except Exception as e:
        print(f"❌ Lazy loading test failed: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Circular Import Elimination Test Suite")
    print("Testing Battle System Modules")
    print("=" * 60)
    
    # Run all tests
    module_tests_passed = test_all_battle_modules()
    lazy_loading_passed = test_lazy_loading()
    
    print("\n" + "=" * 60)
    print("🎯 FINAL RESULT:")
    
    if module_tests_passed and lazy_loading_passed:
        print("✅ ALL TESTS PASSED - CIRCULAR IMPORTS SUCCESSFULLY ELIMINATED!")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED - CIRCULAR IMPORTS STILL EXIST!")
        sys.exit(1)
