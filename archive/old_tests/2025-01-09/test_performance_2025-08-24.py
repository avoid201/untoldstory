#!/usr/bin/env python3
"""
Performance Test für Untold Story Optimierungen
"""

import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

def test_area_performance():
    """Testet Area-Rendering Performance"""
    print("=== AREA PERFORMANCE TEST ===")
    
    try:
        from engine.world.area import Area
        
        test_maps = ['player_house', 'kohlenstadt']
        
        for map_id in test_maps:
            print(f"\nTeste Map: {map_id}")
            
            # Kaltes Laden
            start_time = time.time()
            area1 = Area(map_id)
            cold_time = time.time() - start_time
            
            # Warmes Laden
            start_time = time.time()
            area2 = Area(map_id)
            warm_time = time.time() - start_time
            
            improvement = ((cold_time - warm_time) / cold_time * 100) if cold_time > 0 else 0
            print(f"  Kalt: {cold_time:.3f}s, Warm: {warm_time:.3f}s")
            print(f"  Verbesserung: {improvement:.1f}%")
            
    except Exception as e:
        print(f"Fehler: {e}")

def test_type_performance():
    """Testet Typ-System Performance"""
    print("\n=== TYPE SYSTEM PERFORMANCE TEST ===")
    
    try:
        from engine.systems.types import TypeChart
        
        type_chart = TypeChart()
        
        # Teste Berechnungen
        test_types = ['Feuer', 'Wasser', 'Erde']
        
        start_time = time.time()
        for _ in range(1000):
            for att in test_types:
                for def_ in test_types:
                    type_chart.get_effectiveness(att, def_)
        
        calc_time = time.time() - start_time
        print(f"  1000 Berechnungen: {calc_time:.3f}s")
        
        # Cache-Statistiken
        stats = type_chart.get_performance_stats()
        print(f"  Cache-Hit-Rate: {stats['cache_hit_rate']:.2%}")
        
    except Exception as e:
        print(f"Fehler: {e}")

def main():
    """Hauptfunktion"""
    print("UNTOLD STORY - PERFORMANCE TEST")
    print("=" * 40)
    
    test_area_performance()
    test_type_performance()
    
    print("\n" + "=" * 40)
    print("TEST ABGESCHLOSSEN")

if __name__ == "__main__":
    main()
