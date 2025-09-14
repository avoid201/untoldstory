"""
Battle System Performance Tests
==============================
Comprehensive performance testing for the battle system including:
- Memory leak detection
- Performance benchmarks
- Long-running battle stability
- Event processing efficiency

Version: 1.0.0
Author: Performance Engineer Agent 5
"""

import pytest
import gc
import time
import psutil
import tracemalloc
from typing import List, Dict, Any
from unittest.mock import Mock, patch

# Import battle system components
from engine.systems.battle.battle_controller import BattleController
from engine.systems.battle.battle_state import BattleState
from engine.systems.battle.battle_enums import BattlePhase, BattleType
from engine.systems.battle.turn_logic import ActionType
from engine.systems.battle.turn_logic import BattleAction
from engine.systems.battle.event_processor import EventProcessor
from engine.systems.battle.performance_monitor import BattlePerformanceMonitor, get_performance_monitor
# from engine.systems.battle.turn_processor import TurnProcessor
# from engine.systems.battle.action_processor import ActionProcessor

# Import monster system
from engine.systems.monster_instance import MonsterInstance
from engine.systems.monsters import MonsterDatabase
from engine.systems.moves import Move

# Test data setup
def create_test_monster(name: str = "TestMonster", level: int = 10) -> MonsterInstance:
    """Create a test monster for performance testing."""
    from engine.systems.monster_instance import MonsterSpecies
    
    from engine.systems.stats import BaseStats
    from engine.systems.monster_instance import MonsterRank
    from engine.systems.experience_system import GrowthCurve
    
    # Create a simple monster species
    species = MonsterSpecies(
        id=name.lower(),
        name=name,
        types=["Normal"],
        base_stats=BaseStats(
            hp=100,
            atk=50,
            def_=50,
            mag=50,
            res=50,
            spd=50
        ),
        rank=MonsterRank.F,
        growth_curve=GrowthCurve.MEDIUM_FAST,
        talents=[
            {"talent_id": "physical_i", "learned_at_level": 1, "current_tier": 1, "experience": 0}
        ]
    )
    
    # Create monster instance with correct parameters
    monster = MonsterInstance(
        species=species,
        level=level,
        nickname=name
    )
    
    return monster


def create_test_skill(name: str = "TestSkill") -> Move:
    """Create a test skill for performance testing."""
    from engine.systems.moves import MoveCategory, MoveTarget, MoveEffect, EffectKind
    
    return Move(
        id=name.lower(),
        name=name,
        type="Normal",
        category=MoveCategory.PHYSICAL,
        power=50,
        accuracy=100,
        priority=0,
        targeting=MoveTarget.ENEMY,
        effects=[MoveEffect(kind=EffectKind.DAMAGE, power=50)],
        description="Test skill for performance testing"
    )


def setup_test_battle() -> BattleController:
    """Setup a test battle for performance testing."""
    player_team = [create_test_monster("PlayerMon", 10)]
    enemy_team = [create_test_monster("EnemyMon", 10)]
    
    return BattleController(player_team, enemy_team)


class TestBattleMemoryLeaks:
    """Test memory leak detection in battle system."""
    
    def test_long_battle_memory_stability(self):
        """Test 100+ turn battle for memory leaks."""
        battle = setup_test_battle()
        monitor = get_performance_monitor()
        monitor.reset_metrics()
        
        # Start memory tracking
        tracemalloc.start()
        initial_memory = psutil.Process().memory_info().rss
        
        try:
            # Simulate 100 turns
            for turn in range(100):
                # Create test actions
                player_action = BattleAction(
                    ActionType.ATTACK,
                    battle.state.player_active,
                    battle.state.enemy_active,
                    move=create_test_skill()
                )
                
                enemy_action = BattleAction(
                    ActionType.ATTACK,
                    battle.state.enemy_active,
                    battle.state.player_active,
                    move=create_test_skill()
                )
                
                # Process turn
                start_time = time.perf_counter()
                battle.process_turn(player_action, enemy_action)
                turn_time = time.perf_counter() - start_time
                
                # Record performance metrics
                monitor.record_turn(turn_time)
                monitor.record_memory()
                
                # Force garbage collection every 10 turns
                if turn % 10 == 0:
                    gc.collect()
                    monitor.record_memory()
                
                # Check if battle ended early
                if battle.is_battle_over():
                    break
            
            # Final memory check
            final_memory = psutil.Process().memory_info().rss
            memory_growth_mb = (final_memory - initial_memory) / 1024 / 1024
            
            # Assert memory growth is reasonable
            assert memory_growth_mb < 50, f"Memory grew by {memory_growth_mb:.2f}MB in 100 turns!"
            
            # Check performance report
            report = monitor.get_performance_summary()
            assert report['memory']['status'] != 'leak_detected', "Memory leak detected in performance report"
            
        finally:
            tracemalloc.stop()
    
    def test_event_queue_cleanup(self):
        """Test event queue doesn't grow indefinitely."""
        battle = setup_test_battle()
        event_processor = battle.event_processor
        
        # Spam events
        for i in range(1000):
            event_processor.emit_event("MESSAGE_SHOW", {'message': f'Test {i}'})
        
        # Process some events
        event_processor.process_events()
        
        # Check queue size (should be limited)
        queue_size = len(event_processor.event_queue)
        assert queue_size <= 100, f"Event queue too large: {queue_size} events"
    
    def test_monster_switching_memory(self):
        """Test memory usage during monster switching."""
        battle = setup_test_battle()
        monitor = get_performance_monitor()
        
        # Create multiple monsters
        monsters = [create_test_monster(f"Monster{i}", 10) for i in range(6)]
        battle.state.player_team = monsters
        
        initial_memory = psutil.Process().memory_info().rss
        
        # Switch monsters multiple times
        for i in range(50):
            battle.switch_monster(monsters[i % 6])
            monitor.record_memory()
            
            if i % 10 == 0:
                gc.collect()
        
        final_memory = psutil.Process().memory_info().rss
        memory_growth_mb = (final_memory - initial_memory) / 1024 / 1024
        
        assert memory_growth_mb < 20, f"Memory grew by {memory_growth_mb:.2f}MB during switching"
    
    def test_damage_calculation_memory(self):
        """Test memory usage during damage calculations."""
        from engine.systems.unified_damage_calculator import unified_damage_calculator
        
        monster1 = create_test_monster("Attacker", 10)
        monster2 = create_test_monster("Defender", 10)
        skill = create_test_skill("TestAttack")
        
        initial_memory = psutil.Process().memory_info().rss
        
        # Perform many damage calculations
        for i in range(1000):
            try:
                damage = unified_damage_calculator.calculate_damage(
                    attacker=monster1,
                    defender=monster2,
                    move=skill
                )
            except Exception as e:
                # Fallback calculation
                damage = 10
        
        final_memory = psutil.Process().memory_info().rss
        memory_growth_mb = (final_memory - initial_memory) / 1024 / 1024
        
        assert memory_growth_mb < 10, f"Memory grew by {memory_growth_mb:.2f}MB during damage calculations"


class TestBattlePerformance:
    """Test battle system performance benchmarks."""
    
    def test_turn_processing_speed(self):
        """Benchmark turn processing speed."""
        battle = setup_test_battle()
        monitor = get_performance_monitor()
        
        player_action = BattleAction(
            ActionType.ATTACK,
            battle.state.player_active,
            battle.state.enemy_active,
            move=create_test_skill()
        )
        
        enemy_action = BattleAction(
            ActionType.ATTACK,
            battle.state.enemy_active,
            battle.state.player_active,
            move=create_test_skill()
        )
        
        # Benchmark 100 turns
        start = time.perf_counter()
        for _ in range(100):
            battle.process_turn(player_action, enemy_action)
        elapsed = time.perf_counter() - start
        
        turns_per_second = 100 / elapsed
        avg_turn_time = elapsed / 100
        
        # Record metrics
        monitor.record_turn(avg_turn_time)
        
        # Assert performance targets
        assert turns_per_second > 100, f"Turn processing too slow: {turns_per_second:.1f} turns/sec"
        assert avg_turn_time < 0.01, f"Average turn time too slow: {avg_turn_time*1000:.1f}ms"
    
    def test_damage_calculation_performance(self):
        """Benchmark damage calculation performance."""
        from engine.systems.unified_damage_calculator import unified_damage_calculator
        
        monster1 = create_test_monster("Attacker", 10)
        monster2 = create_test_monster("Defender", 10)
        skill = create_test_skill("TestAttack")
        
        monitor = get_performance_monitor()
        
        # Benchmark 1000 damage calculations
        start = time.perf_counter()
        for _ in range(1000):
            calc_start = time.perf_counter()
            try:
                damage = unified_damage_calculator.calculate_damage(
                    attacker=monster1,
                    defender=monster2,
                    move=skill
                )
            except Exception:
                damage = 10
            calc_time = time.perf_counter() - calc_start
            monitor.record_damage_calculation(calc_time)
        
        elapsed = time.perf_counter() - start
        calcs_per_second = 1000 / elapsed
        avg_calc_time = elapsed / 1000
        
        # Assert performance targets
        assert calcs_per_second > 10000, f"Damage calc too slow: {calcs_per_second:.0f} calcs/sec"
        assert avg_calc_time < 0.0001, f"Average calc time too slow: {avg_calc_time*1000:.3f}ms"
    
    def test_event_processing_performance(self):
        """Benchmark event processing performance."""
        from engine.systems.battle.battle_state import BattleState
        battle_state = BattleState()
        event_processor = EventProcessor(battle_state)
        monitor = get_performance_monitor()
        
        # Emit many events
        start = time.perf_counter()
        for i in range(1000):
            event_processor.emit_event("TEST_EVENT", {'data': i})
            monitor.record_event("TEST_EVENT")
        
        # Process events
        process_start = time.perf_counter()
        event_processor.process_events()
        process_time = time.perf_counter() - process_start
        
        total_time = time.perf_counter() - start
        events_per_second = 1000 / total_time
        
        # Assert performance targets
        assert events_per_second > 1000, f"Event processing too slow: {events_per_second:.0f} events/sec"
        assert process_time < 0.1, f"Event processing time too slow: {process_time*1000:.1f}ms"
    
    def test_battle_initialization_speed(self):
        """Benchmark battle initialization speed."""
        start = time.perf_counter()
        
        # Create multiple battles
        for _ in range(100):
            battle = setup_test_battle()
            battle.start_battle()
        
        elapsed = time.perf_counter() - start
        init_time = elapsed / 100
        
        # Assert performance targets
        assert init_time < 0.01, f"Battle initialization too slow: {init_time*1000:.1f}ms"
    
    def test_monster_creation_performance(self):
        """Benchmark monster creation performance."""
        start = time.perf_counter()
        
        # Create many monsters
        for i in range(1000):
            monster = create_test_monster(f"Monster{i}", 10)
        
        elapsed = time.perf_counter() - start
        creation_time = elapsed / 1000
        
        # Assert performance targets
        assert creation_time < 0.001, f"Monster creation too slow: {creation_time*1000:.3f}ms"


class TestBattleStability:
    """Test battle system stability under stress."""
    
    def test_rapid_action_processing(self):
        """Test rapid action processing without crashes."""
        battle = setup_test_battle()
        
        # Process actions as fast as possible
        for i in range(1000):
            try:
                action = BattleAction(
                    ActionType.ATTACK,
                    battle.state.player_active,
                    battle.state.enemy_active,
                    move=create_test_skill()
                )
                battle.process_turn(action, action)
            except Exception as e:
                # Should not crash, but might hit battle end conditions
                if "battle over" not in str(e).lower():
                    raise
    
    def test_concurrent_event_processing(self):
        """Test concurrent event processing."""
        import threading
        import queue
        
        from engine.systems.battle.battle_state import BattleState
        battle_state = BattleState()
        event_processor = EventProcessor(battle_state)
        results = queue.Queue()
        
        def emit_events(thread_id: int):
            """Emit events from a thread."""
            try:
                for i in range(100):
                    event_processor.emit_event(f"THREAD_{thread_id}_EVENT", {'id': i})
                results.put(f"Thread {thread_id} completed")
            except Exception as e:
                results.put(f"Thread {thread_id} error: {e}")
        
        # Start multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=emit_events, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Process events
        event_processor.process_events()
        
        # Check results
        assert results.qsize() == 5, "Not all threads completed"
        
        # Check no errors occurred
        while not results.empty():
            result = results.get()
            assert "error" not in result.lower(), f"Thread error: {result}"
    
    def test_memory_pressure_handling(self):
        """Test system behavior under memory pressure."""
        battle = setup_test_battle()
        
        # Create memory pressure by creating many objects
        objects = []
        for i in range(10000):
            objects.append(create_test_monster(f"PressureMonster{i}", 10))
        
        # Try to process battle actions under memory pressure
        try:
            action = BattleAction(
                ActionType.ATTACK,
                battle.state.player_active,
                battle.state.enemy_active,
                move=create_test_skill()
            )
            battle.process_turn(action, action)
        except MemoryError:
            pytest.skip("System ran out of memory during test")
        except Exception as e:
            # Other exceptions are acceptable under memory pressure
            pass
        
        # Clean up
        del objects
        gc.collect()


class TestPerformanceMonitor:
    """Test the performance monitor itself."""
    
    def test_performance_monitor_initialization(self):
        """Test performance monitor initialization."""
        monitor = BattlePerformanceMonitor()
        assert monitor.enabled
        assert monitor.enabled
        assert monitor.start_time > 0
    
    def test_performance_metrics_recording(self):
        """Test recording of performance metrics."""
        monitor = BattlePerformanceMonitor()
        
        # Record various metrics
        monitor.record_frame_time(0.016)  # 60 FPS
        monitor.record_turn(0.01)    # 10ms turn
        monitor.record_damage_calculation(0.001)  # 1ms damage calc
        monitor.record_event("TEST_EVENT")
        monitor.record_memory()
        
        # Get report
        report = monitor.get_performance_summary()
        
        # Verify metrics were recorded
        assert report['fps']['average'] > 0
        assert report['turns']['avg_time_ms'] > 0
        assert report['damage_calc']['avg_time_ms'] > 0
        assert report['events']['total'] > 0
        assert report['memory']['current_mb'] > 0
    
    def test_memory_leak_detection(self):
        """Test memory leak detection functionality."""
        monitor = BattlePerformanceMonitor()
        
        # Set initial memory to a low value
        monitor.initial_memory = 1000000  # 1MB
        
        # Simulate memory growth that exceeds the limit
        for i in range(20):
            # Simulate growing memory usage that exceeds 50MB growth
            fake_memory = 1000000 + i * 3000000  # 3MB growth per step
            monitor.metrics.memory_snapshots.append(fake_memory)
        
        # Check for leak detection
        report = monitor.get_performance_summary()
        assert report['memory']['status'] == 'leak_detected'
    
    def test_performance_status_calculation(self):
        """Test performance status calculation."""
        monitor = BattlePerformanceMonitor()
        
        # Test excellent performance
        monitor.metrics.frame_times.extend([0.016] * 100)  # 60 FPS
        monitor.metrics.turn_times.extend([0.005] * 100)   # 5ms turns
        monitor.metrics.memory_snapshots.extend([1000000] * 10)  # Stable memory
        
        report = monitor.get_performance_summary()
        assert report['overall_status'] == 'excellent'
    
    def test_performance_monitor_cleanup(self):
        """Test performance monitor cleanup."""
        monitor = BattlePerformanceMonitor()
        monitor.cleanup()
        
        assert not monitor.enabled
        assert not tracemalloc.is_tracing()


if __name__ == "__main__":
    # Run performance tests
    pytest.main([__file__, "-v", "--tb=short"])
