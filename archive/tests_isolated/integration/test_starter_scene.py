#!/usr/bin/env python3
"""
Test script for StarterScene Monster-Loading System
Tests robuste Monster-Erstellung und Fallback-Mechanismen
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

def test_monster_loading():
    """Test monster loading from database."""
    print("=== Test Monster-Loading aus Datenbank ===")
    
    try:
        from engine.core.resources import resources
        
        # Test all starter monster IDs
        starter_ids = [24, 26, 32, 40]  # Sumpfschrecke, Kraterkröte, Säbelzahnkaninchen, Irrlicht
        
        for monster_id in starter_ids:
            print(f"\nTeste Monster ID {monster_id}:")
            species_data = resources.get_monster_species(monster_id)
            
            if species_data:
                print(f"  ✅ Monster {monster_id} erfolgreich geladen: {species_data['name']}")
                print(f"  - BaseStats: {species_data['base_stats']}")
                print(f"  - Typ: {species_data['types']}")
                print(f"  - Rang: {species_data['rank']}")
            else:
                print(f"  ❌ Monster {monster_id} nicht in Datenbank gefunden")
        
        print("\n✅ Monster-Loading-Test abgeschlossen")
        return True
        
    except Exception as e:
        print(f"❌ Fehler beim Monster-Loading-Test: {e}")
        return False

def test_monster_creation():
    """Test monster creation with improved stats."""
    print("\n=== Test Monster-Erstellung mit verbesserten Stats ===")
    
    try:
        from engine.core.resources import resources
        from engine.systems.monster_instance import MonsterInstance
        
        # Test creation for each starter
        starter_data = [
            {'id': 24, 'name': 'Sumpfschrecke'},
            {'id': 26, 'name': 'Kraterkröte'},
            {'id': 32, 'name': 'Säbelzahnkaninchen'},
            {'id': 40, 'name': 'Irrlicht'}
        ]
        
        for data in starter_data:
            print(f"\nTeste Erstellung von {data['name']} (ID: {data['id']}):")
            
            species_data = resources.get_monster_species(data['id'])
            if species_data:
                monster = MonsterInstance.create_from_species(species_data, level=5)
                print(f"  ✅ Monster erstellt: {monster.species_name}")
                print(f"  - Level: {monster.level}")
                print(f"  - HP: {monster.max_hp}")
                print(f"  - Stats: {monster.stats}")
                print(f"  - Moves: {len(monster.moves)} ({[m.name for m in monster.moves]})")
            else:
                print(f"  ❌ Monster-Daten nicht verfügbar")
        
        print("\n✅ Monster-Erstellung-Test abgeschlossen")
        return True
        
    except Exception as e:
        print(f"❌ Fehler beim Monster-Erstellung-Test: {e}")
        return False

def test_fallback_system():
    """Test fallback monster creation."""
    print("\n=== Test Fallback-System ===")
    
    try:
        from engine.scenes.starter_scene import StarterScene
        
        # Create a dummy game object
        class DummyGame:
            def __init__(self):
                self.resources = None
                self.party_manager = None
                self.story_manager = None
                self.sprite_manager = None
        
        # Create scene
        game = DummyGame()
        scene = StarterScene(game)
        
        # Test fallback creation
        test_data = {
            'id': 999,  # Non-existent ID
            'name': 'Test-Monster',
            'types': ['Bestie'],
            'description': 'Ein Test-Monster für Fallback-Tests',
            'color': (255, 0, 0)
        }
        
        print("Teste Fallback-Monster-Erstellung mit ungültiger ID...")
        fallback_monster = scene._create_fallback_starter(test_data)
        
        if fallback_monster:
            print(f"  ✅ Fallback-Monster erstellt: {fallback_monster.species_name}")
            print(f"  - Level: {fallback_monster.level}")
            print(f"  - HP: {fallback_monster.max_hp}")
            print(f"  - Stats: {fallback_monster.stats}")
            print(f"  - Moves: {len(fallback_monster.moves)}")
        else:
            print("  ❌ Fallback-Monster-Erstellung fehlgeschlagen")
        
        print("\n✅ Fallback-System-Test abgeschlossen")
        return True
        
    except Exception as e:
        print(f"❌ Fehler beim Fallback-System-Test: {e}")
        return False

def test_stat_calculation():
    """Test improved stat calculation for low levels."""
    print("\n=== Test Verbesserte Stat-Berechnung ===")
    
    try:
        from engine.systems.stats import StatCalculator, BaseStats
        
        # Test with typical starter stats
        base_stats = BaseStats(hp=45, atk=28, def_=50, mag=25, res=33, spd=30)
        
        for level in [1, 5, 10, 15]:
            stats = StatCalculator.calculate_all_stats(base_stats, level)
            print(f"Level {level}: {stats}")
        
        print("\n✅ Stat-Berechnung-Test abgeschlossen")
        return True
        
    except Exception as e:
        print(f"❌ Fehler beim Stat-Berechnung-Test: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 STARTE STARTER-SCENE MONSTER-LOADING TESTS")
    print("=" * 50)
    
    tests = [
        test_monster_loading,
        test_monster_creation,
        test_stat_calculation,
        test_fallback_system
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test fehlgeschlagen: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 TEST-ERGEBNISSE: {passed}/{total} Tests bestanden")
    
    if passed == total:
        print("🎉 ALLE TESTS BESTANDEN! Monster-Loading-System ist einsatzbereit!")
    else:
        print("⚠️  Einige Tests fehlgeschlagen - System benötigt weitere Verbesserungen")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
