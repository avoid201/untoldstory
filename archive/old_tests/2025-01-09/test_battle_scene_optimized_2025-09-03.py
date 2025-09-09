#!/usr/bin/env python3
"""
🥊 BATTLE SCENE OPTIMIZED TEST
Elite Battle System Specialist - Test der optimierten Battle Scene
"""

import sys
import os
import traceback
from typing import List, Dict, Any

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_optimized_battle_scene():
    """Teste die optimierte Battle Scene."""
    print("🥊 BATTLE SCENE OPTIMIZED TEST")
    print("=" * 50)
    
    try:
        # Test 1: Battle Scene Import
        print("\n📋 TEST 1: Battle Scene Import")
        test_battle_scene_import()
        
        # Test 2: Battle Scene Initialization
        print("\n🎮 TEST 2: Battle Scene Initialization")
        test_battle_scene_initialization()
        
        # Test 3: Battle Action Processing
        print("\n⚔️ TEST 3: Battle Action Processing")
        test_battle_action_processing()
        
        # Test 4: Battle Flow Integration
        print("\n🔄 TEST 4: Battle Flow Integration")
        test_battle_flow_integration()
        
        # Test 5: Performance Optimization
        print("\n⚡ TEST 5: Performance Optimization")
        test_performance_optimization()
        
        print("\n✅ ALL BATTLE SCENE TESTS COMPLETED SUCCESSFULLY!")
        print("🎯 Optimierte Battle Scene ist vollständig funktionsfähig!")
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        traceback.print_exc()
        return False
    
    return True

def test_battle_scene_import():
    """Teste Battle Scene Import."""
    print("  🔍 Testing optimized battle scene import...")
    
    try:
        from engine.scenes.battle_scene_optimized import BattleScene
        print("  ✅ Optimized Battle Scene import OK")
        
        # Test original battle scene import
        from engine.scenes.battle_scene import BattleScene as OriginalBattleScene
        print("  ✅ Original Battle Scene import OK")
        
    except ImportError as e:
        print(f"  ❌ Battle Scene import failed: {e}")
        raise

def test_battle_scene_initialization():
    """Teste Battle Scene Initialization."""
    print("  🔍 Testing battle scene initialization...")
    
    try:
        from engine.scenes.battle_scene_optimized import BattleScene
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
                self.scenes = []
            
            def pop_scene(self):
                self.scenes.pop() if self.scenes else None
        
        # Test battle scene creation
        game = MockGame()
        battle_scene = BattleScene(game)
        
        # Test initialization with monsters
        battle_scene.on_enter(
            player_team=[player_monster],
            enemy_team=[enemy_monster],
            is_wild=True,
            can_flee=True
        )
        
        assert battle_scene.battle_state is not None
        assert battle_scene.battle_controller is not None
        assert battle_scene.battle_ui is not None
        print("  ✅ Battle Scene initialization OK")
        
    except Exception as e:
        print(f"  ❌ Battle Scene initialization failed: {e}")
        raise

def test_battle_action_processing():
    """Teste Battle Action Processing."""
    print("  🔍 Testing battle action processing...")
    
    try:
        from engine.scenes.battle_scene_optimized import BattleScene
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
                self.scenes = []
            
            def pop_scene(self):
                self.scenes.pop() if self.scenes else None
        
        # Test battle scene creation
        game = MockGame()
        battle_scene = BattleScene(game)
        
        # Initialize battle
        battle_scene.on_enter(
            player_team=[player_monster],
            enemy_team=[enemy_monster],
            is_wild=True,
            can_flee=True
        )
        
        # Test action processing methods
        action_result = {
            'action': 'attack',
            'move_id': 'tackle'
        }
        
        # Test _process_attack_action
        battle_scene._process_attack_action(action_result)
        print("  ✅ Attack action processing OK")
        
        # Test _process_item_action
        item_action = {
            'action': 'item',
            'item_id': 'potion',
            'target': player_monster
        }
        battle_scene._process_item_action(item_action)
        print("  ✅ Item action processing OK")
        
        # Test _process_switch_action
        switch_action = {
            'action': 'switch',
            'monster_index': 0
        }
        battle_scene._process_switch_action(switch_action)
        print("  ✅ Switch action processing OK")
        
        # Test _process_tame_action
        tame_action = {
            'action': 'tame',
            'meat_bonus': 20
        }
        battle_scene._process_tame_action(tame_action)
        print("  ✅ Tame action processing OK")
        
        # Test _process_scout_action
        scout_action = {
            'action': 'scout'
        }
        battle_scene._process_scout_action(scout_action)
        print("  ✅ Scout action processing OK")
        
        # Test _process_flee_action
        flee_action = {
            'action': 'flee'
        }
        battle_scene._process_flee_action(flee_action)
        print("  ✅ Flee action processing OK")
        
    except Exception as e:
        print(f"  ❌ Battle action processing failed: {e}")
        raise

def test_battle_flow_integration():
    """Teste Battle Flow Integration."""
    print("  🔍 Testing battle flow integration...")
    
    try:
        from engine.scenes.battle_scene_optimized import BattleScene
        from engine.systems.monster_instance import MonsterInstance, MonsterSpecies, MonsterRank
        from engine.systems.stats import BaseStats
        from engine.systems.battle.battle_enums import BattleResult
        
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
                self.scenes = []
            
            def pop_scene(self):
                self.scenes.pop() if self.scenes else None
        
        # Test battle scene creation
        game = MockGame()
        battle_scene = BattleScene(game)
        
        # Initialize battle
        battle_scene.on_enter(
            player_team=[player_monster],
            enemy_team=[enemy_monster],
            is_wild=True,
            can_flee=True
        )
        
        # Test battle phase management
        assert battle_scene.current_phase is not None
        print("  ✅ Battle phase management OK")
        
        # Test battle end checking
        battle_ended = battle_scene.check_battle_end()
        assert isinstance(battle_ended, bool)
        print("  ✅ Battle end checking OK")
        
        # Test battle state validation
        assert battle_scene.battle_state is not None
        assert battle_scene.battle_state.player_active is not None
        assert battle_scene.battle_state.enemy_active is not None
        print("  ✅ Battle state validation OK")
        
        # Test UI integration
        assert battle_scene.battle_ui is not None
        assert battle_scene.battle_ui.battle_state is not None
        print("  ✅ UI integration OK")
        
    except Exception as e:
        print(f"  ❌ Battle flow integration failed: {e}")
        raise

def test_performance_optimization():
    """Teste Performance Optimization."""
    print("  🔍 Testing performance optimization...")
    
    try:
        from engine.scenes.battle_scene_optimized import BattleScene
        from engine.systems.monster_instance import MonsterInstance, MonsterSpecies, MonsterRank
        from engine.systems.stats import BaseStats
        import time
        
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
                self.scenes = []
            
            def pop_scene(self):
                self.scenes.pop() if self.scenes else None
        
        # Test battle scene creation
        game = MockGame()
        battle_scene = BattleScene(game)
        
        # Initialize battle
        battle_scene.on_enter(
            player_team=[player_monster],
            enemy_team=[enemy_monster],
            is_wild=True,
            can_flee=True
        )
        
        # Test update performance
        start_time = time.time()
        for i in range(100):
            battle_scene.update(0.016)  # 60 FPS
        end_time = time.time()
        
        update_time = end_time - start_time
        assert update_time < 1.0  # Should be fast
        print(f"  ✅ Update performance OK ({update_time:.3f}s for 100 updates)")
        
        # Test action processing performance
        start_time = time.time()
        for i in range(50):
            action_result = {
                'action': 'attack',
                'move_id': 'tackle'
            }
            battle_scene._process_battle_action(action_result)
        end_time = time.time()
        
        action_time = end_time - start_time
        assert action_time < 0.5  # Should be fast
        print(f"  ✅ Action processing performance OK ({action_time:.3f}s for 50 actions)")
        
        # Test memory usage optimization
        assert hasattr(battle_scene, '_last_update_time')
        assert hasattr(battle_scene, '_update_interval')
        assert hasattr(battle_scene, '_pending_actions')
        print("  ✅ Memory optimization features OK")
        
    except Exception as e:
        print(f"  ❌ Performance optimization test failed: {e}")
        raise

def run_battle_scene_simulation():
    """Führe eine Battle Scene Simulation durch."""
    print("\n🎮 RUNNING BATTLE SCENE SIMULATION")
    print("=" * 40)
    
    try:
        from engine.scenes.battle_scene_optimized import BattleScene
        from engine.systems.monster_instance import MonsterInstance, MonsterSpecies, MonsterRank
        from engine.systems.stats import BaseStats
        import pygame
        
        # Initialize pygame (required for some components)
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
                self.scenes = []
            
            def pop_scene(self):
                self.scenes.pop() if self.scenes else None
        
        # Test battle scene creation
        game = MockGame()
        battle_scene = BattleScene(game)
        
        # Initialize battle
        battle_scene.on_enter(
            player_team=[player_monster],
            enemy_team=[enemy_monster],
            is_wild=True,
            can_flee=True
        )
        
        print(f"  🥊 Battle Scene initialized: {player_monster.nickname} vs {enemy_monster.nickname}")
        
        # Simulate battle updates
        for i in range(10):
            battle_scene.update(0.016)  # 60 FPS
            if i % 3 == 0:
                # Simulate player action
                action_result = {
                    'action': 'attack',
                    'move_id': 'tackle'
                }
                battle_scene._process_battle_action(action_result)
                print(f"    📋 Turn {i//3 + 1}: Player attacks")
        
        print("  ✅ Battle Scene simulation completed successfully!")
        
        # Cleanup
        pygame.quit()
        
    except Exception as e:
        print(f"  ❌ Battle Scene simulation failed: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Starting Battle Scene Optimized Test...")
    
    # Run main tests
    success = test_optimized_battle_scene()
    
    if success:
        # Run battle scene simulation
        run_battle_scene_simulation()
        
        print("\n🎯 BATTLE SCENE OPTIMIZATION COMPLETE!")
        print("🥊 Optimierte Battle Scene ist vollständig funktionsfähig!")
        print("✨ Performance-Optimierungen sind implementiert!")
    else:
        print("\n❌ BATTLE SCENE OPTIMIZATION FAILED!")
        print("🔧 Bitte behebe die Fehler bevor du fortfährst!")
        sys.exit(1)
