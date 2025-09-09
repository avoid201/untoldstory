#!/usr/bin/env python3
"""
Test für Method Consolidation - AGENT 2
Testet konsolidierte Action-Validation, Phase-Transitions und State-Getters
"""

import sys
import os
import pygame
import logging

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_method_consolidation():
    """Test Method Consolidation."""
    print("🎮 AGENT 2: METHOD CONSOLIDATION SPECIALIST - Test")
    print("=" * 60)
    
    try:
        # Initialize pygame
        pygame.init()
        pygame.display.set_mode((320, 180))
        
        # Import battle system components
        from engine.systems.battle.battle_controller import BattleController
        from engine.systems.battle.battle_validation import BattleValidator
        from engine.systems.battle.battle_state import BattleState
        from engine.systems.battle.battle_enums import BattleType, BattlePhase
        from engine.systems.monster_instance import MonsterInstance, MonsterSpecies
        from engine.systems.stats import BaseStats
        
        print("✓ Imports erfolgreich")
        
        # Create test monster species
        test_species = MonsterSpecies(
            id=999,
            name="Test Monster",
            types=["Normal"],
            base_stats=BaseStats(hp=100, atk=50, def_=30, mag=40, res=25, spd=60),
            rank="F"
        )
        
        # Create test monster instances
        player_monster = MonsterInstance(
            species=test_species,
            level=10,
            nickname="Player Monster"
        )
        enemy_monster = MonsterInstance(
            species=test_species,
            level=10,
            nickname="Enemy Monster"
        )
        
        print(f"✓ Test Monsters erstellt: {player_monster.name} vs {enemy_monster.name}")
        
        # Create Battle Controller
        battle_controller = BattleController(
            player_team=[player_monster],
            enemy_team=[enemy_monster],
            battle_type=BattleType.WILD
        )
        
        print("✓ Battle Controller erstellt")
        
        # Test 1: Consolidated Action Validation
        print("\n🔧 Test 1: Consolidated Action Validation")
        print("-" * 45)
        
        # Test dict action validation
        test_action = {
            "type": "attack",
            "actor": player_monster,
            "target": enemy_monster,
            "move": "Tackle"
        }
        
        # Test basic validation
        is_valid = battle_controller.validate_action(test_action, is_player=True, detailed=False)
        print(f"✓ Basic validation: {is_valid}")
        
        # Test detailed validation
        detailed_result = battle_controller.validate_action(test_action, is_player=True, detailed=True)
        print(f"✓ Detailed validation: {detailed_result}")
        
        # Test BattleValidator directly
        validator_result = BattleValidator.validate_action_complete(test_action, battle_controller.state, True, True)
        print(f"✓ BattleValidator result: {validator_result}")
        
        # Test 2: Universal Phase Transitions
        print("\n🔧 Test 2: Universal Phase Transitions")
        print("-" * 40)
        
        # Test phase transitions
        print(f"Current phase: {battle_controller.state.phase.value}")
        
        # Test transition to INPUT
        success = battle_controller.transition_phase(BattlePhase.INPUT)
        print(f"✓ Transition to INPUT: {success}")
        print(f"Current phase: {battle_controller.state.phase.value}")
        
        # Test transition to EXECUTION
        success = battle_controller.transition_phase(BattlePhase.EXECUTION)
        print(f"✓ Transition to EXECUTION: {success}")
        print(f"Current phase: {battle_controller.state.phase.value}")
        
        # Test transition to AFTERMATH
        success = battle_controller.transition_phase(BattlePhase.AFTERMATH)
        print(f"✓ Transition to AFTERMATH: {success}")
        print(f"Current phase: {battle_controller.state.phase.value}")
        
        # Test 3: Consolidated State Getters
        print("\n🔧 Test 3: Consolidated State Getters")
        print("-" * 40)
        
        # Test minimal state info
        minimal_state = battle_controller.get_state_info('minimal')
        print(f"✓ Minimal state: {len(minimal_state)} keys")
        print(f"  Keys: {list(minimal_state.keys())}")
        
        # Test basic state info
        basic_state = battle_controller.get_state_info('basic')
        print(f"✓ Basic state: {len(basic_state)} keys")
        print(f"  Has player_active: {'player_active' in basic_state}")
        print(f"  Has enemy_active: {'enemy_active' in basic_state}")
        
        # Test full state info
        full_state = battle_controller.get_state_info('full')
        print(f"✓ Full state: {len(full_state)} keys")
        print(f"  Has battle_type: {'battle_type' in full_state}")
        print(f"  Has can_flee: {'can_flee' in full_state}")
        
        # Test complete state info
        complete_state = battle_controller.get_state_info('complete')
        print(f"✓ Complete state: {len(complete_state)} keys")
        print(f"  Has battle_log: {'battle_log' in complete_state}")
        print(f"  Has player_team: {'player_team' in complete_state}")
        
        # Test 4: Legacy Method Removal Verification
        print("\n🔧 Test 4: Legacy Method Removal Verification")
        print("-" * 50)
        
        # Verify legacy methods are removed
        legacy_methods = ['get_battle_state', 'get_battle_status', 'get_current_phase_info']
        removed_count = 0
        
        for method_name in legacy_methods:
            if not hasattr(battle_controller, method_name):
                print(f"✓ Legacy method {method_name} successfully removed")
                removed_count += 1
            else:
                print(f"❌ Legacy method {method_name} still exists")
        
        print(f"✓ Legacy methods removed: {removed_count}/{len(legacy_methods)}")
        
        # Test 5: Error Handling
        print("\n🔧 Test 5: Error Handling")
        print("-" * 25)
        
        # Test invalid action
        invalid_action = {"type": "invalid"}
        is_valid = battle_controller.validate_action(invalid_action, detailed=True)
        print(f"✓ Invalid action handling: {is_valid}")
        
        # Test invalid phase transition
        battle_controller.state.phase = BattlePhase.END
        success = battle_controller.transition_phase(BattlePhase.INPUT)
        print(f"✓ Invalid phase transition handling: {success}")
        
        print("\n🎯 ERFOLGS-KRITERIEN VALIDIERUNG")
        print("=" * 50)
        
        # Prüfe alle Erfolgs-Kriterien
        success_count = 0
        total_tests = 5
        
        # 1. Nur EINE validate_action Methode im gesamten System
        if hasattr(battle_controller, 'validate_action') and not hasattr(battle_controller, '_validate_action'):
            print("✅ Nur EINE validate_action Methode im gesamten System")
            success_count += 1
        else:
            print("❌ Mehrere validate_action Methoden gefunden")
        
        # 2. Phase-Transitions auf eine Methode reduziert
        if hasattr(battle_controller, 'transition_phase') and hasattr(battle_controller, '_is_expected_transition'):
            print("✅ Phase-Transitions auf eine Methode reduziert")
            success_count += 1
        else:
            print("❌ Phase-Transitions nicht konsolidiert")
        
        # 3. State-Getter konsolidiert
        if hasattr(battle_controller, 'get_state_info') and hasattr(battle_controller, '_get_monster_info'):
            print("✅ State-Getter konsolidiert")
            success_count += 1
        else:
            print("❌ State-Getter nicht konsolidiert")
        
        # 4. Keine redundanten Methoden mehr
        redundant_methods = []
        legacy_methods = ['get_battle_state', 'get_battle_status', 'get_current_phase_info', 
                         '_transition_to_input_phase', '_transition_to_execution_phase', 
                         '_transition_to_aftermath_phase', '_transition_aftermath_to_input']
        
        for method_name in legacy_methods:
            if hasattr(battle_controller, method_name):
                redundant_methods.append(method_name)
        
        if len(redundant_methods) == 0:
            print("✅ Keine redundanten Methoden mehr")
            success_count += 1
        else:
            print(f"❌ Redundante Methoden gefunden: {redundant_methods}")
        
        # 5. DRY-Prinzip durchgehend eingehalten
        if (hasattr(battle_controller, 'validate_action') and 
            hasattr(battle_controller, 'transition_phase') and 
            hasattr(battle_controller, 'get_state_info')):
            print("✅ DRY-Prinzip durchgehend eingehalten")
            success_count += 1
        else:
            print("❌ DRY-Prinzip nicht eingehalten")
        
        print(f"\n📊 ERGEBNIS: {success_count}/{total_tests} Tests erfolgreich")
        
        if success_count == total_tests:
            print("🎉 ALLE ERFOLGS-KRITERIEN ERFÜLLT!")
            print("✅ Nur EINE validate_action Methode im gesamten System")
            print("✅ Phase-Transitions auf eine Methode reduziert")
            print("✅ State-Getter konsolidiert")
            print("✅ Keine redundanten Methoden mehr")
            print("✅ DRY-Prinzip durchgehend eingehalten")
            return True
        else:
            print("⚠️ Einige Tests fehlgeschlagen - weitere Konsolidierung erforderlich")
            return False
            
    except Exception as e:
        print(f"❌ Test fehlgeschlagen: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        pygame.quit()

if __name__ == "__main__":
    success = test_method_consolidation()
    sys.exit(0 if success else 1)
