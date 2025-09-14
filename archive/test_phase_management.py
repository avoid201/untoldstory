#!/usr/bin/env python3
"""
Test script for AGENT 4: Phase Management Coordinator
Tests the correct phase flow: START → INPUT → EXECUTION → AFTERMATH → INPUT
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.systems.battle.battle_controller import BattleController
from engine.systems.battle.battle_enums import BattlePhase, BattleType
from engine.systems.monster_instance import MonsterInstance
from engine.systems.monsters import MonsterDatabase

def test_phase_transitions():
    """Test the complete phase transition flow."""
    print("🧪 AGENT 4: Testing Phase Management Coordinator")
    print("=" * 60)
    
    try:
        # Create test monsters
        db = MonsterDatabase()
        species = db.get_species_by_name("Glutstummel")  # Glutstummel
        if not species:
            print("❌ Could not create test monster")
            return False
        
        player_monster = species.create_instance(level=5)
        enemy_monster = species.create_instance(level=5)
        
        # Create battle controller
        controller = BattleController(
            player_team=[player_monster],
            enemy_team=[enemy_monster],
            battle_type=BattleType.WILD
        )
        
        print(f"✓ BattleController created")
        print(f"✓ Initial phase: {controller.state.phase.value}")
        
        # Test 1: Initialize battle (should go START → INPUT)
        print("\n📋 Test 1: Battle Initialization")
        init_result = controller.initialize([player_monster], [enemy_monster])
        
        if init_result.get('success'):
            print(f"✓ Battle initialized successfully")
            print(f"✓ Phase after init: {controller.state.phase.value}")
            print(f"✓ Waiting for input: {controller.state.waiting_for_input}")
            
            if controller.state.phase != BattlePhase.INPUT:
                print(f"❌ Expected INPUT phase, got {controller.state.phase.value}")
                return False
        else:
            print(f"❌ Battle initialization failed: {init_result}")
            return False
        
        # Test 2: Phase validation
        print("\n📋 Test 2: Phase Transition Validation")
        
        # Test valid transitions
        valid_transitions = [
            (BattlePhase.INPUT, BattlePhase.EXECUTION),
            (BattlePhase.EXECUTION, BattlePhase.AFTERMATH),
            (BattlePhase.AFTERMATH, BattlePhase.INPUT)
        ]
        
        for from_phase, to_phase in valid_transitions:
            if controller.validate_phase_transition(from_phase, to_phase):
                print(f"✓ Valid transition: {from_phase.value} → {to_phase.value}")
            else:
                print(f"❌ Invalid transition: {from_phase.value} → {to_phase.value}")
                return False
        
        # Test invalid transitions
        invalid_transitions = [
            (BattlePhase.INPUT, BattlePhase.AFTERMATH),
            (BattlePhase.EXECUTION, BattlePhase.INPUT),
            (BattlePhase.AFTERMATH, BattlePhase.EXECUTION)
        ]
        
        for from_phase, to_phase in invalid_transitions:
            if not controller.validate_phase_transition(from_phase, to_phase):
                print(f"✓ Correctly rejected invalid transition: {from_phase.value} → {to_phase.value}")
            else:
                print(f"❌ Should have rejected invalid transition: {from_phase.value} → {to_phase.value}")
                return False
        
        # Test 3: Phase info
        print("\n📋 Test 3: Phase Information")
        phase_info = controller.get_current_phase_info()
        print(f"✓ Current phase: {phase_info['phase']}")
        print(f"✓ Waiting for input: {phase_info['waiting_for_input']}")
        print(f"✓ Is player turn: {phase_info['is_player_turn']}")
        print(f"✓ Turn count: {phase_info['turn_count']}")
        
        # Test 4: Manual phase transitions
        print("\n📋 Test 4: Manual Phase Transitions")
        
        # INPUT → EXECUTION
        controller._transition_to_execution_phase()
        if controller.state.phase == BattlePhase.EXECUTION:
            print("✓ INPUT → EXECUTION transition successful")
        else:
            print(f"❌ INPUT → EXECUTION failed, current phase: {controller.state.phase.value}")
            return False
        
        # EXECUTION → AFTERMATH
        controller._transition_to_aftermath_phase()
        if controller.state.phase == BattlePhase.AFTERMATH:
            print("✓ EXECUTION → AFTERMATH transition successful")
        else:
            print(f"❌ EXECUTION → AFTERMATH failed, current phase: {controller.state.phase.value}")
            return False
        
        # AFTERMATH → INPUT
        controller._transition_aftermath_to_input()
        if controller.state.phase == BattlePhase.INPUT and controller.state.waiting_for_input:
            print("✓ AFTERMATH → INPUT transition successful")
        else:
            print(f"❌ AFTERMATH → INPUT failed, current phase: {controller.state.phase.value}")
            return False
        
        print("\n🎉 All phase management tests passed!")
        print("✅ AGENT 4: Phase Management Coordinator is working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_phase_transitions()
    sys.exit(0 if success else 1)
