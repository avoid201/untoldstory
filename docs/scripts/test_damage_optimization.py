#!/usr/bin/env python3
"""
Test script for AGENT 3: Damage Calculation Optimizer
Tests robust damage calculation, status modifiers, and type effectiveness
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.systems.unified_damage_calculator import UnifiedDamageCalculator, DamageResult
from engine.systems.types import TypeChart
from engine.systems.monster_instance import MonsterInstance
from engine.systems.monsters import MonsterDatabase

def test_robust_damage_calculation():
    """Test robust damage calculation with various edge cases."""
    print("🧪 AGENT 3: Testing Damage Calculation Optimizer")
    print("=" * 60)
    
    try:
        # Create test monsters
        db = MonsterDatabase()
        species = db.get_species_by_name("Glutstummel")
        if not species:
            print("❌ Could not create test monster")
            return False
        
        attacker = species.create_instance(level=5)
        defender = species.create_instance(level=5)
        
        # Create damage calculator
        calculator = UnifiedDamageCalculator()
        
        print(f"✓ UnifiedDamageCalculator created")
        
        # Test 1: Normal damage calculation
        print("\n📋 Test 1: Normal Damage Calculation")
        move = type('Move', (), {'power': 50, 'type': 'Feuer', 'category': type('Category', (), {'value': 'phys'})()})()
        
        result = calculator.calculate_damage(attacker, defender, move)
        
        if result and hasattr(result, 'damage') and result.damage >= 0:
            print(f"✓ Normal damage calculation successful: {result.damage}")
        else:
            print(f"❌ Normal damage calculation failed: {result}")
            return False
        
        # Test 2: Status modifier effects
        print("\n📋 Test 2: Status Modifier Effects")
        
        # Test burn effect on ATK
        attacker.status = 'burn'
        result_burn = calculator.calculate_damage(attacker, defender, move)
        attacker.status = None
        
        # Test paralysis effect on SPD
        attacker.status = 'paralysis'
        result_paralysis = calculator.calculate_damage(attacker, defender, move)
        attacker.status = None
        
        # Test freeze/sleep prevention
        attacker.status = 'freeze'
        result_freeze = calculator.calculate_damage(attacker, defender, move)
        attacker.status = None
        
        if (result_burn and result_freeze and 
            result_freeze.damage == 0 and  # Freeze should prevent action
            result_burn.damage <= result.damage):  # Burn should reduce or equal damage
            print("✓ Status modifiers working correctly")
        else:
            print(f"❌ Status modifiers not working: burn={result_burn.damage}, freeze={result_freeze.damage}, normal={result.damage}")
            return False
        
        # Test 3: Robust fallback mechanisms
        print("\n📋 Test 3: Robust Fallback Mechanisms")
        
        # Test with None inputs
        result_none = calculator.calculate_damage(None, defender, move)
        if result_none and result_none.damage > 0:
            print("✓ None attacker handled gracefully")
        else:
            print(f"❌ None attacker not handled: {result_none}")
            return False
        
        # Test with invalid move
        invalid_move = type('Move', (), {'power': None, 'type': None})()
        result_invalid = calculator.calculate_damage(attacker, defender, invalid_move)
        if result_invalid and hasattr(result_invalid, 'damage') and result_invalid.damage >= 0:
            print("✓ Invalid move handled gracefully")
        else:
            print(f"❌ Invalid move not handled: {result_invalid}")
            return False
        
        # Test 4: Type effectiveness optimization
        print("\n📋 Test 4: Type Effectiveness Optimization")
        
        type_chart = TypeChart()
        effectiveness = type_chart.get_effectiveness("Feuer", "Pflanze")
        
        if isinstance(effectiveness, (int, float)) and effectiveness > 0:
            print(f"✓ Type effectiveness calculation working: {effectiveness}")
        else:
            print(f"❌ Type effectiveness calculation failed: {effectiveness}")
            return False
        
        # Test 5: Performance validation
        print("\n📋 Test 5: Performance Validation")
        
        import time
        start_time = time.time()
        
        # Run multiple calculations
        for _ in range(100):
            calculator.calculate_damage(attacker, defender, move)
        
        end_time = time.time()
        avg_time = (end_time - start_time) / 100
        
        if avg_time < 0.01:  # Should be fast
            print(f"✓ Performance acceptable: {avg_time:.4f}s per calculation")
        else:
            print(f"⚠️ Performance slower than expected: {avg_time:.4f}s per calculation")
        
        # Test 6: Result validation
        print("\n📋 Test 6: Result Validation")
        
        result = calculator.calculate_damage(attacker, defender, move)
        
        # Check all required attributes
        required_attrs = ['damage', 'is_critical', 'critical_tier', 'effectiveness', 'damage_type']
        missing_attrs = [attr for attr in required_attrs if not hasattr(result, attr)]
        
        if not missing_attrs:
            print("✓ All required attributes present")
        else:
            print(f"❌ Missing attributes: {missing_attrs}")
            return False
        
        # Check damage bounds
        if 0 <= result.damage <= 9999:
            print("✓ Damage within reasonable bounds")
        else:
            print(f"❌ Damage out of bounds: {result.damage}")
            return False
        
        # Check effectiveness bounds
        if 0.0 <= result.effectiveness <= 4.0:
            print("✓ Effectiveness within reasonable bounds")
        else:
            print(f"❌ Effectiveness out of bounds: {result.effectiveness}")
            return False
        
        print("\n🎉 All damage optimization tests passed!")
        print("✅ AGENT 3: Damage Calculation Optimizer is working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_robust_damage_calculation()
    sys.exit(0 if success else 1)
