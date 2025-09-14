#!/usr/bin/env python3
"""
Event Performance Test
======================
Testet die Performance des optimierten Event Systems.
"""

import time
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from engine.systems.battle.event_processor import EventProcessor
from engine.systems.battle.events.event_types import EventType, BattleEvent


class MockBattleState:
    """Mock BattleState für Tests."""
    def __init__(self):
        self.event_processor = None


def test_event_processing():
    """Teste Event-Verarbeitung."""
    print("🧪 TESTING EVENT PROCESSING")
    print("-" * 40)
    
    state = MockBattleState()
    processor = EventProcessor(state)
    
    # Teste verschiedene Events
    success_count = 0
    total_events = 0
    
    # Verschiedene Events sollten durchgehen
    for i in range(10):
        result = processor.emit_event(
            EventType.DAMAGE_DEALT,
            {'damage': i, 'target': f'enemy_{i}', 'actor': f'player_{i}'}
        )
        total_events += 1
        if result:
            success_count += 1
    
    print(f"✅ Erfolgreiche Events: {success_count}")
    print(f"📊 Total Events: {total_events}")
    print(f"📊 Success Rate: {success_count / total_events * 100:.1f}%")
    
    assert success_count >= 10, "Zu viele Events blockiert!"
    print("✅ Event Processing Test BESTANDEN\n")


def test_memory_management():
    """Teste Memory Management."""
    print("🧪 TESTING MEMORY MANAGEMENT")
    print("-" * 40)
    
    state = MockBattleState()
    processor = EventProcessor(state)
    
    # Emittiere viele Events
    for i in range(1000):
        processor.emit_event(
            EventType.MESSAGE_SHOW,
            {'message': f'Test message {i}', 'duration': 0.1}
        )
    
    stats = processor.get_performance_stats()
    
    print(f"📊 Queue Size: {stats['queue_size']}")
    print(f"📊 History Size: {stats['history_size']}")
    print(f"📊 Memory Usage: {stats['memory_usage_mb']:.2f} MB")
    print(f"📊 Events per Second: {stats['events_per_second']:.1f}")
    
    assert stats['queue_size'] <= 100, f"Queue overflow! Size: {stats['queue_size']}"
    assert stats['memory_usage_mb'] < 10, f"Memory leak! Usage: {stats['memory_usage_mb']:.2f} MB"
    print("✅ Memory Management Test BESTANDEN\n")


def test_performance_under_load():
    """Teste Performance unter Last."""
    print("🧪 TESTING PERFORMANCE UNDER LOAD")
    print("-" * 40)
    
    state = MockBattleState()
    processor = EventProcessor(state)
    
    start_time = time.time()
    
    # Emittiere viele verschiedene Events
    for i in range(500):
        processor.emit_event(
            EventType.DAMAGE_DEALT,
            {'damage': i % 100, 'target': f'enemy_{i % 10}', 'actor': f'player_{i % 5}'}
        )
        
        if i % 50 == 0:
            processor.emit_event(
                EventType.MESSAGE_SHOW,
                {'message': f'Progress: {i}/500', 'duration': 0.1}
            )
    
    end_time = time.time()
    duration = end_time - start_time
    
    stats = processor.get_performance_stats()
    
    print(f"⏱️  Duration: {duration:.2f} seconds")
    print(f"📊 Total Events: {stats['total_events']}")
    print(f"📊 Events per Second: {stats['events_per_second']:.1f}")
    print(f"📊 Memory Usage: {stats['memory_usage_mb']:.2f} MB")
    
    assert duration < 5.0, f"Performance zu langsam! Duration: {duration:.2f}s"
    assert stats['events_per_second'] > 100, f"Events per second zu niedrig! {stats['events_per_second']:.1f}"
    print("✅ Performance Test BESTANDEN\n")


def run_all_tests():
    """Führe alle Tests aus."""
    print("🚀 EVENT SYSTEM PERFORMANCE TESTS")
    print("=" * 50)
    
    try:
        test_event_processing()
        test_memory_management()
        test_performance_under_load()
        
        print("🎉 ALLE TESTS BESTANDEN!")
        print("✅ Event System ist optimiert und performant!")
        
    except Exception as e:
        print(f"❌ TEST FEHLGESCHLAGEN: {e}")
        return False
    
    return True


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
