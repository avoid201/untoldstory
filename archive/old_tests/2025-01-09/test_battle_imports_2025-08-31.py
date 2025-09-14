#!/usr/bin/env python3
"""
Test script to verify all battle system imports work correctly
"""

import sys
import traceback

def test_imports():
    """Test all critical battle system imports."""
    
    errors = []
    
    # Test battle controller imports
    try:
        from engine.systems.battle.battle_controller import BattleState, BattleController
        print("✅ BattleController imports OK")
    except Exception as e:
        errors.append(f"❌ BattleController import failed: {e}")
        traceback.print_exc()
    
    # Test battle actions imports
    try:
        from engine.systems.battle.battle_actions import BattleActionExecutor
        print("✅ BattleActionExecutor imports OK")
    except Exception as e:
        errors.append(f"❌ BattleActionExecutor import failed: {e}")
        traceback.print_exc()
    
    # Test battle AI imports
    try:
        from engine.systems.battle.battle_ai import BattleAI
        print("✅ BattleAI imports OK")
    except Exception as e:
        errors.append(f"❌ BattleAI import failed: {e}")
        traceback.print_exc()
    
    # Test move system imports
    try:
        from engine.systems.moves import Move, MoveExecutor, MoveRegistry
        print("✅ Move system imports OK")
    except Exception as e:
        errors.append(f"❌ Move system import failed: {e}")
        traceback.print_exc()
    
    # Test unified damage calculator
    try:
        from engine.systems.unified_damage_calculator import UnifiedDamageCalculator
        print("✅ UnifiedDamageCalculator imports OK")
    except Exception as e:
        errors.append(f"❌ UnifiedDamageCalculator import failed: {e}")
        traceback.print_exc()
    
    # Test item system imports
    try:
        from engine.systems.items import ItemManager, Item, ItemEffectExecutor
        print("✅ Item system imports OK")
    except Exception as e:
        errors.append(f"❌ Item system import failed: {e}")
        traceback.print_exc()
    
    # Test battle scene imports
    try:
        from engine.scenes.battle_scene import BattleScene
        print("✅ BattleScene imports OK")
    except Exception as e:
        errors.append(f"❌ BattleScene import failed: {e}")
        traceback.print_exc()
    
    # Test battle UI imports
    try:
        from engine.ui.battle_ui import BattleUI, BattleMenuState
        print("✅ BattleUI imports OK")
    except Exception as e:
        errors.append(f"❌ BattleUI import failed: {e}")
        traceback.print_exc()
    
    # Test circular dependencies
    try:
        # This should work with lazy loading
        from engine.systems.battle.battle_controller import BattleController
        bc = BattleController(None)
        # Try to access the lazy-loaded BattleAI
        if hasattr(bc, 'battle_state') and bc.battle_state:
            ai = bc.battle_state.battle_ai
        print("✅ Circular dependency resolution OK")
    except Exception as e:
        errors.append(f"❌ Circular dependency test failed: {e}")
        traceback.print_exc()
    
    return errors

if __name__ == "__main__":
    print("=" * 60)
    print("BATTLE SYSTEM IMPORT TEST")
    print("=" * 60)
    
    errors = test_imports()
    
    print("\n" + "=" * 60)
    if errors:
        print("❌ TESTS FAILED")
        print("=" * 60)
        for error in errors:
            print(error)
        sys.exit(1)
    else:
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        print("Battle system imports are working correctly!")
        sys.exit(0)
