#!/usr/bin/env python3
"""
Performance Test Script für Untold Story Optimierungen
Misst die Performance-Verbesserungen der implementierten Optimierungen
"""

import time
import cProfile
import pstats
import io
import sys
import os
from pathlib import Path

# Füge den Projektpfad hinzu
sys.path.insert(0, str(Path(__file__).parent))

def test_area_rendering_performance():
    """Testet die Performance des optimierten Area-Rendering-Systems"""
    print("=== AREA RENDERING PERFORMANCE TEST ===")
    
    try:
        from engine.world.area import Area
        from engine.core.resources import resources
        
        # Teste verschiedene Map-Größen
        test_maps = ['player_house', 'kohlenstadt', 'route1']
        
        for map_id in test_maps:
            print(f"\nTeste Map: {map_id}")
            
            # Erste Ladung (kalt)
            start_time = time.time()
            area1 = Area(map_id)
            cold_load_time = time.time() - start_time
            
            # Zweite Ladung (warm - aus Cache)
            start_time = time.time()
            area2 = Area(map_id)
            warm_load_time = time.time() - start_time
            
            # Cache-Statistiken
            cache_hits = area2._cache_hits
            cache_misses = area2._cache_misses
            
            print(f"  Kaltes Laden: {cold_load_time:.3f}s")
            print(f"  Warmes Laden: {warm_load_time:.3f}s")
            print(f"  Cache-Hits: {cache_hits}, Cache-Misses: {cache_misses}")
            print(f"  Verbesserung: {((cold_load_time - warm_load_time) / cold_load_time * 100):.1f}%")
            
    except Exception as e:
        print(f"Fehler beim Area-Performance-Test: {e}")

def test_type_system_performance():
    """Testet die Performance des optimierten Typ-Systems"""
    print("\n=== TYPE SYSTEM PERFORMANCE TEST ===")
    
    try:
        from engine.systems.types import TypeChart
        
        # Erstelle TypeChart-Instanz
        type_chart = TypeChart()
        
        # Teste Einzel-Typ-Berechnungen
        test_types = ['Feuer', 'Wasser', 'Erde', 'Luft', 'Pflanze', 'Bestie']
        
        print("\nEinzel-Typ-Berechnungen:")
        start_time = time.time()
        
        for _ in range(1000):
            for att in test_types:
                for def_ in test_types:
                    type_chart.get_effectiveness(att, def_)
        
        single_type_time = time.time() - start_time
        print(f"  1000 Berechnungen: {single_type_time:.3f}s")
        
        # Teste Dual-Typ-Berechnungen
        print("\nDual-Typ-Berechnungen:")
        start_time = time.time()
        
        for _ in range(1000):
            for att in test_types:
                type_chart.calculate_type_multiplier(att, ['Feuer', 'Wasser'])
                type_chart.calculate_type_multiplier(att, ['Erde', 'Luft'])
        
        dual_type_time = time.time() - start_time
        print(f"  1000 Berechnungen: {dual_type_time:.3f}s")
        
        # Performance-Statistiken
        stats = type_chart.get_performance_stats()
        print(f"\nCache-Statistiken:")
        print(f"  Cache-Hit-Rate: {stats['cache_hit_rate']:.2%}")
        print(f"  Durchschnittliche Berechnungszeit: {stats['avg_calculation_time']:.6f}s")
        print(f"  NumPy verfügbar: {stats['numpy_available']}")
        
    except Exception as e:
        print(f"Fehler beim Typ-System-Performance-Test: {e}")

def test_battle_system_performance():
    """Testet die Performance des optimierten Kampf-Systems"""
    print("\n=== BATTLE SYSTEM PERFORMANCE TEST ===")
    
    try:
        from engine.systems.battle.battle_system import BattleState, BattleType
        from engine.systems.monster_instance import MonsterInstance
        
        # Erstelle Test-Monster
        def create_test_monster(name: str, level: int = 10):
            monster = MonsterInstance()
            monster.name = name
            monster.level = level
            monster.current_hp = 100
            monster.stats = {'hp': 100, 'atk': 50, 'def': 50, 'spd': 50}
            monster.is_fainted = False
            return monster
        
        player_team = [create_test_monster("Test1"), create_test_monster("Test2")]
        enemy_team = [create_test_monster("Enemy1"), create_test_monster("Enemy2")]
        
        # Erstelle BattleState
        battle = BattleState(player_team, enemy_team, BattleType.WILD)
        
        # Teste Validierungs-Performance
        print("\nValidierungs-Performance:")
        
        # Erste Validierung (kalt)
        start_time = time.time()
        for _ in range(100):
            battle.validate_battle_state()
        cold_validation_time = time.time() - start_time
        
        # Zweite Validierung (warm - aus Cache)
        start_time = time.time()
        for _ in range(100):
            battle.validate_battle_state()
        warm_validation_time = time.time() - start_time
        
        print(f"  Kalte Validierung (100x): {cold_validation_time:.3f}s")
        print(f"  Warme Validierung (100x): {warm_validation_time:.3f}s")
        print(f"  Verbesserung: {((cold_validation_time - warm_validation_time) / cold_validation_time * 100):.1f}%")
        
    except Exception as e:
        print(f"Fehler beim Kampf-System-Performance-Test: {e}")

def test_resource_management_performance():
    """Testet die Performance des optimierten Ressourcen-Managements"""
    print("\n=== RESOURCE MANAGEMENT PERFORMANCE TEST ===")
    
    try:
        from engine.core.resources import resources
        
        # Teste Bild-Loading-Performance
        print("\nBild-Loading-Performance:")
        
        # Teste verschiedene Bildgrößen
        test_images = [
            'monster/1.png',
            'monster/10.png', 
            'monster/100.png'
        ]
        
        for image_path in test_images:
            if resources.path_exists(image_path):
                # Erste Ladung (kalt)
                start_time = time.time()
                surface1 = resources.load_image(image_path)
                cold_load_time = time.time() - start_time
                
                # Zweite Ladung (warm - aus Cache)
                start_time = time.time()
                surface2 = resources.load_image(image_path)
                warm_load_time = time.time() - start_time
                
                print(f"  {image_path}:")
                print(f"    Kaltes Laden: {cold_load_time:.3f}s")
                print(f"    Warmes Laden: {warm_load_time:.3f}s")
                print(f"    Verbesserung: {((cold_load_time - warm_load_time) / cold_load_time * 100):.1f}%")
            else:
                print(f"  {image_path}: Nicht gefunden")
        
        # Cache-Statistiken
        print(f"\nCache-Statistiken:")
        print(f"  Cache-Hits: {resources._cache_hits}")
        print(f"  Cache-Misses: {resources._cache_misses}")
        if resources._cache_hits + resources._cache_misses > 0:
            hit_rate = resources._cache_hits / (resources._cache_hits + resources._cache_misses)
            print(f"  Cache-Hit-Rate: {hit_rate:.2%}")
        
    except Exception as e:
        print(f"Fehler beim Ressourcen-Management-Performance-Test: {e}")

def run_comprehensive_profile():
    """Führt ein umfassendes Profiling durch"""
    print("\n=== COMPREHENSIVE PROFILING ===")
    
    def profile_function():
        """Funktion die profiliert werden soll"""
        # Teste alle Systeme
        test_area_rendering_performance()
        test_type_system_performance()
        test_battle_system_performance()
        test_resource_management_performance()
    
    # Profiling
    pr = cProfile.Profile()
    pr.enable()
    
    profile_function()
    
    pr.disable()
    
    # Statistiken ausgeben
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats(20)  # Top 20 Funktionen
    
    print("\nTop 20 Funktionen nach CPU-Zeit:")
    print(s.getvalue())

def main():
    """Hauptfunktion für Performance-Tests"""
    print("UNTOLD STORY - PERFORMANCE OPTIMIERUNG TEST")
    print("=" * 50)
    
    # Einzelne Tests
    test_area_rendering_performance()
    test_type_system_performance()
    test_battle_system_performance()
    test_resource_management_performance()
    
    # Umfassendes Profiling
    run_comprehensive_profile()
    
    print("\n" + "=" * 50)
    print("PERFORMANCE-TEST ABGESCHLOSSEN")
    print("Überprüfe die Ergebnisse oben für Details zu den Optimierungen.")

if __name__ == "__main__":
    main()
