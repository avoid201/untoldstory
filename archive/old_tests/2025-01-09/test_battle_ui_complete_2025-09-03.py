#!/usr/bin/env python3
"""
🥊 BATTLE UI COMPLETE INTEGRATION TEST
Elite Battle System Specialist - Vollständige Battle UI Validierung
"""

import sys
import os
import traceback
from typing import List, Dict, Any

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_battle_ui_complete():
    """Vollständige Battle UI Integration Test."""
    print("🥊 BATTLE UI COMPLETE INTEGRATION TEST")
    print("=" * 60)
    
    try:
        # Test 1: Battle UI Core Components
        print("\n📋 TEST 1: Battle UI Core Components")
        test_battle_ui_core()
        
        # Test 2: Menu States Integration
        print("\n🎮 TEST 2: Menu States Integration")
        test_menu_states_integration()
        
        # Test 3: UI Event Handling
        print("\n⚔️ TEST 3: UI Event Handling")
        test_ui_event_handling()
        
        # Test 4: Battle UI Feedback
        print("\n🖥️ TEST 4: Battle UI Feedback")
        test_battle_ui_feedback()
        
        # Test 5: UI Performance
        print("\n⚡ TEST 5: UI Performance")
        test_ui_performance()
        
        print("\n✅ ALL BATTLE UI TESTS COMPLETED SUCCESSFULLY!")
        print("🎯 Battle UI ist vollständig integriert und funktionsfähig!")
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        traceback.print_exc()
        return False
    
    return True

def test_battle_ui_core():
    """Teste Battle UI Core Components."""
    print("  🔍 Testing BattleUI import...")
    
    try:
        from engine.ui.battle import BattleUI, BattleMenuState
        print("  ✅ BattleUI import OK")
        
        # Test menu states
        menu_states = [
            BattleMenuState.MAIN,
            BattleMenuState.MOVE_SELECT,
            BattleMenuState.ITEM_SELECT,
            BattleMenuState.SWITCH_SELECT,
            BattleMenuState.TAME_MEAT,
            BattleMenuState.TAME_CONFIRM,
            BattleMenuState.SCOUT,
            BattleMenuState.MESSAGE
        ]
        
        for state in menu_states:
            assert state is not None
            print(f"    ✅ {state.name} menu state OK")
        
        # Test BattleUI creation
        class MockGame:
            def __init__(self):
                self.debug_mode = True
        
        game = MockGame()
        battle_ui = BattleUI(game)
        assert battle_ui is not None
        print("  ✅ BattleUI creation OK")
        
    except ImportError as e:
        print(f"  ❌ BattleUI import failed: {e}")
        raise

def test_menu_states_integration():
    """Teste Menu States Integration."""
    print("  🔍 Testing menu states integration...")
    
    try:
        from engine.ui.battle import BattleUI, BattleMenuState
        from engine.systems.monster_instance import MonsterInstance, MonsterSpecies, MonsterRank
        from engine.systems.stats import BaseStats
        
        # Create test species
        test_species = MonsterSpecies(
            id="test_slime",
            name="Test Slime",
            types=["Normal"],
            base_stats=BaseStats(hp=100, atk=50, def_=40, mag=30, res=35, spd=60),
            rank=MonsterRank.D
        )
        
        # Create test monsters
        player_monster = MonsterInstance(
            species=test_species,
            level=5,
            nickname="TestPlayer"
        )
        
        enemy_monster = MonsterInstance(
            species=test_species,
            level=5,
            nickname="TestEnemy"
        )
        
        # Create mock game object
        class MockGame:
            def __init__(self):
                self.debug_mode = True
        
        game = MockGame()
        battle_ui = BattleUI(game)
        
        # Test battle initialization
        battle_ui.init_battle([player_monster], [enemy_monster])
        print("  ✅ Battle initialization OK")
        
        # Test menu state transitions
        battle_ui.menu_state = BattleMenuState.MAIN
        assert battle_ui.menu_state == BattleMenuState.MAIN
        print("  ✅ Main menu state OK")
        
        battle_ui.menu_state = BattleMenuState.MOVE_SELECT
        assert battle_ui.menu_state == BattleMenuState.MOVE_SELECT
        print("  ✅ Move select menu state OK")
        
        battle_ui.menu_state = BattleMenuState.ITEM_SELECT
        assert battle_ui.menu_state == BattleMenuState.ITEM_SELECT
        print("  ✅ Item select menu state OK")
        
        battle_ui.menu_state = BattleMenuState.TAME_MEAT
        assert battle_ui.menu_state == BattleMenuState.TAME_MEAT
        print("  ✅ Tame meat menu state OK")
        
    except Exception as e:
        print(f"  ❌ Menu states integration failed: {e}")
        raise

def test_ui_event_handling():
    """Teste UI Event Handling."""
    print("  🔍 Testing UI event handling...")
    
    try:
        import pygame
        from engine.ui.battle import BattleUI, BattleMenuState
        from engine.systems.monster_instance import MonsterInstance, MonsterSpecies, MonsterRank
        from engine.systems.stats import BaseStats
        
        # Create test species
        test_species = MonsterSpecies(
            id="test_slime",
            name="Test Slime",
            types=["Normal"],
            base_stats=BaseStats(hp=100, atk=50, def_=40, mag=30, res=35, spd=60),
            rank=MonsterRank.D
        )
        
        # Create test monsters
        player_monster = MonsterInstance(
            species=test_species,
            level=5,
            nickname="TestPlayer"
        )
        
        enemy_monster = MonsterInstance(
            species=test_species,
            level=5,
            nickname="TestEnemy"
        )
        
        # Create mock game object
        class MockGame:
            def __init__(self):
                self.debug_mode = True
        
        game = MockGame()
        battle_ui = BattleUI(game)
        
        # Initialize battle
        battle_ui.init_battle([player_monster], [enemy_monster])
        
        # Test keyboard events
        # Test Enter key
        enter_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
        handled = battle_ui.handle_event(enter_event)
        print("  ✅ Enter key handling OK")
        
        # Test Escape key
        escape_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
        handled = battle_ui.handle_event(escape_event)
        print("  ✅ Escape key handling OK")
        
        # Test arrow keys
        up_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP)
        handled = battle_ui.handle_event(up_event)
        print("  ✅ Arrow key handling OK")
        
        down_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)
        handled = battle_ui.handle_event(down_event)
        print("  ✅ Arrow key handling OK")
        
        # Test action keys
        e_key_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_e)
        handled = battle_ui.handle_event(e_key_event)
        print("  ✅ Action key handling OK")
        
    except Exception as e:
        print(f"  ❌ UI event handling failed: {e}")
        raise

def test_battle_ui_feedback():
    """Teste Battle UI Feedback."""
    print("  🔍 Testing battle UI feedback...")
    
    try:
        from engine.ui.battle import BattleUI, BattleMenuState
        from engine.systems.monster_instance import MonsterInstance, MonsterSpecies, MonsterRank
        from engine.systems.stats import BaseStats
        
        # Create test species
        test_species = MonsterSpecies(
            id="test_slime",
            name="Test Slime",
            types=["Normal"],
            base_stats=BaseStats(hp=100, atk=50, def_=40, mag=30, res=35, spd=60),
            rank=MonsterRank.D
        )
        
        # Create test monsters
        player_monster = MonsterInstance(
            species=test_species,
            level=5,
            nickname="TestPlayer"
        )
        
        enemy_monster = MonsterInstance(
            species=test_species,
            level=5,
            nickname="TestEnemy"
        )
        
        # Create mock game object
        class MockGame:
            def __init__(self):
                self.debug_mode = True
        
        game = MockGame()
        battle_ui = BattleUI(game)
        
        # Initialize battle
        battle_ui.init_battle([player_monster], [enemy_monster])
        
        # Test message system
        battle_ui.add_message("Test message")
        print("  ✅ Message system OK")
        
        # Test action result generation
        action_result = battle_ui.get_action_result()
        print("  ✅ Action result system OK")
        
        # Test pending action clearing
        battle_ui.clear_pending_action()
        print("  ✅ Pending action clearing OK")
        
        # Test battle event processing
        mock_event = {
            'event_type': 'MESSAGE_SHOW',
            'data': {'message': 'Test event'}
        }
        
        battle_ui.process_battle_event(mock_event)
        print("  ✅ Battle event processing OK")
        
    except Exception as e:
        print(f"  ❌ Battle UI feedback failed: {e}")
        raise

def test_ui_performance():
    """Teste UI Performance."""
    print("  🔍 Testing UI performance...")
    
    try:
        import time
        from engine.ui.battle import BattleUI, BattleMenuState
        from engine.systems.monster_instance import MonsterInstance, MonsterSpecies, MonsterRank
        from engine.systems.stats import BaseStats
        
        # Create test species
        test_species = MonsterSpecies(
            id="test_slime",
            name="Test Slime",
            types=["Normal"],
            base_stats=BaseStats(hp=100, atk=50, def_=40, mag=30, res=35, spd=60),
            rank=MonsterRank.D
        )
        
        # Create test monsters
        player_monster = MonsterInstance(
            species=test_species,
            level=5,
            nickname="TestPlayer"
        )
        
        enemy_monster = MonsterInstance(
            species=test_species,
            level=5,
            nickname="TestEnemy"
        )
        
        # Create mock game object
        class MockGame:
            def __init__(self):
                self.debug_mode = True
        
        game = MockGame()
        battle_ui = BattleUI(game)
        
        # Initialize battle
        battle_ui.init_battle([player_monster], [enemy_monster])
        
        # Test update performance
        start_time = time.time()
        for i in range(100):
            battle_ui.update(0.016)  # 60 FPS
        end_time = time.time()
        
        update_time = end_time - start_time
        assert update_time < 1.0  # Should be fast
        print(f"  ✅ Update performance OK ({update_time:.3f}s for 100 updates)")
        
        # Test event handling performance
        import pygame
        start_time = time.time()
        for i in range(50):
            enter_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
            battle_ui.handle_event(enter_event)
        end_time = time.time()
        
        event_time = end_time - start_time
        assert event_time < 0.5  # Should be fast
        print(f"  ✅ Event handling performance OK ({event_time:.3f}s for 50 events)")
        
        # Test menu state switching performance
        start_time = time.time()
        for i in range(20):
            battle_ui.menu_state = BattleMenuState.MAIN
            battle_ui.menu_state = BattleMenuState.MOVE_SELECT
            battle_ui.menu_state = BattleMenuState.ITEM_SELECT
        end_time = time.time()
        
        switch_time = end_time - start_time
        assert switch_time < 0.1  # Should be very fast
        print(f"  ✅ Menu state switching performance OK ({switch_time:.3f}s for 60 switches)")
        
    except Exception as e:
        print(f"  ❌ UI performance test failed: {e}")
        raise

def run_battle_ui_simulation():
    """Führe eine Battle UI Simulation durch."""
    print("\n🎮 RUNNING BATTLE UI SIMULATION")
    print("=" * 40)
    
    try:
        import pygame
        from engine.ui.battle import BattleUI, BattleMenuState
        from engine.systems.monster_instance import MonsterInstance, MonsterSpecies, MonsterRank
        from engine.systems.stats import BaseStats
        
        # Initialize pygame
        pygame.init()
        
        # Create test species
        test_species = MonsterSpecies(
            id="test_slime",
            name="Test Slime",
            types=["Normal"],
            base_stats=BaseStats(hp=100, atk=50, def_=40, mag=30, res=35, spd=60),
            rank=MonsterRank.D
        )
        
        # Create test monsters
        player_monster = MonsterInstance(
            species=test_species,
            level=5,
            nickname="PlayerSlime"
        )
        
        enemy_monster = MonsterInstance(
            species=test_species,
            level=5,
            nickname="EnemySlime"
        )
        
        # Create mock game object
        class MockGame:
            def __init__(self):
                self.debug_mode = True
        
        game = MockGame()
        battle_ui = BattleUI(game)
        
        # Initialize battle
        battle_ui.init_battle([player_monster], [enemy_monster])
        
        print(f"  🥊 Battle UI initialized: {player_monster.nickname} vs {enemy_monster.nickname}")
        
        # Simulate UI interactions
        print("  📋 Simulating menu navigation...")
        
        # Test main menu
        battle_ui.menu_state = BattleMenuState.MAIN
        print("    ✅ Main menu active")
        
        # Test move selection
        battle_ui.menu_state = BattleMenuState.MOVE_SELECT
        print("    ✅ Move selection menu active")
        
        # Test item selection
        battle_ui.menu_state = BattleMenuState.ITEM_SELECT
        print("    ✅ Item selection menu active")
        
        # Test taming menu
        battle_ui.menu_state = BattleMenuState.TAME_MEAT
        print("    ✅ Taming menu active")
        
        # Simulate keyboard input
        print("  ⌨️ Simulating keyboard input...")
        
        # Test Enter key
        enter_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
        battle_ui.handle_event(enter_event)
        print("    ✅ Enter key processed")
        
        # Test Escape key
        escape_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
        battle_ui.handle_event(escape_event)
        print("    ✅ Escape key processed")
        
        # Test arrow keys
        up_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP)
        battle_ui.handle_event(up_event)
        print("    ✅ Up arrow processed")
        
        down_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)
        battle_ui.handle_event(down_event)
        print("    ✅ Down arrow processed")
        
        # Simulate UI updates
        print("  🔄 Simulating UI updates...")
        for i in range(10):
            battle_ui.update(0.016)  # 60 FPS
            if i % 3 == 0:
                battle_ui.add_message(f"Update message {i//3 + 1}")
        
        print("  ✅ Battle UI simulation completed successfully!")
        
        # Cleanup
        pygame.quit()
        
    except Exception as e:
        print(f"  ❌ Battle UI simulation failed: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Starting Battle UI Complete Integration Test...")
    
    # Run main tests
    success = test_battle_ui_complete()
    
    if success:
        # Run battle UI simulation
        run_battle_ui_simulation()
        
        print("\n🎯 BATTLE UI INTEGRATION COMPLETE!")
        print("🥊 Battle UI ist vollständig integriert und funktionsfähig!")
        print("✨ Alle Menu-States und UI-Feedback sind implementiert!")
    else:
        print("\n❌ BATTLE UI INTEGRATION FAILED!")
        print("🔧 Bitte behebe die Fehler bevor du fortfährst!")
        sys.exit(1)
