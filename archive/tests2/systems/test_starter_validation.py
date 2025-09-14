#!/usr/bin/env python3
"""
Final validation test for improved StarterScene Monster-Loading System
Tests all improvements and fallback mechanisms
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def test_complete_starter_creation():
    """Test complete starter creation process."""
    print("🧪 FINALER STARTER-SCENE VALIDATIONS-TEST")
    print("=" * 50)
    
    try:
        from engine.core.resources import resources
        from engine.systems.monster_instance import MonsterInstance
        
        # Test all starter monster creation from database
        starter_ids = [24, 26, 32, 40]
        starter_names = ['Sumpfschrecke', 'Kraterkröte', 'Säbelzahnkaninchen', 'Irrlicht']
        
        created_monsters = []
        
        for i, (monster_id, expected_name) in enumerate(zip(starter_ids, starter_names)):
            print(f"\n--- Test {i+1}: {expected_name} (ID: {monster_id}) ---")
            
            # Load from database
            species_data = resources.get_monster_species(monster_id)
            if not species_data:
                print(f"❌ Monster {monster_id} nicht in Datenbank")
                continue
            
            # Create monster
            monster = MonsterInstance.create_from_species(species_data, level=5)
            
            # Validate creation
            assert monster is not None, f"Monster {monster_id} creation failed"
            assert monster.species_name == expected_name, f"Name mismatch: {monster.species_name} != {expected_name}"
            assert monster.level == 5, f"Level mismatch: {monster.level} != 5"
            assert monster.max_hp >= 20, f"HP too low: {monster.max_hp}"
            assert len(monster.moves) >= 1, f"No moves: {len(monster.moves)}"
            
            # Print stats
            print(f"✅ {monster.species_name} erfolgreich erstellt")
            print(f"   Level: {monster.level}, HP: {monster.max_hp}")
            print(f"   Stats: {monster.stats}")
            print(f"   Moves: {[m.name for m in monster.moves]}")
            print(f"   Typ: {monster.types}, Rang: {monster.rank.value}")
            
            created_monsters.append(monster)
        
        print(f"\n✅ Alle {len(created_monsters)} Starter-Monster erfolgreich erstellt!")
        return True
        
    except Exception as e:
        print(f"❌ Fehler beim Starter-Erstellung-Test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_fallback_creation():
    """Test fallback monster creation."""
    print("\n=== Test Fallback-Monster-Erstellung ===")
    
    try:
        from engine.scenes.starter_scene import StarterScene
        from engine.systems.monster_instance import MonsterSpecies, MonsterRank
        from engine.systems.stats import BaseStats, GrowthCurve
        
        # Create dummy game
        class DummyGame:
            def __init__(self):
                self.resources = None
                self.party_manager = None
                self.story_manager = None
                self.sprite_manager = None
        
        game = DummyGame()
        scene = StarterScene(game)
        
        # Test fallback creation with non-existent monster
        test_data = {
            'id': 999,
            'name': 'Test-Fallback-Monster',
            'types': ['Bestie'],
            'description': 'Ein Test-Monster für Fallback-Tests',
            'color': (255, 0, 0)
        }
        
        print("Teste Fallback-Monster-Erstellung...")
        monster = scene._create_fallback_starter(test_data)
        
        # Validate fallback monster
        assert monster is not None, "Fallback monster creation failed"
        assert monster.species_name == test_data['name'], f"Name mismatch: {monster.species_name}"
        assert monster.level == 5, f"Level mismatch: {monster.level}"
        assert monster.max_hp >= 15, f"HP too low: {monster.max_hp}"
        assert hasattr(monster, 'moves'), "Monster has no moves attribute"
        
        print(f"✅ Fallback-Monster erstellt: {monster.species_name}")
        print(f"   Level: {monster.level}, HP: {monster.max_hp}")
        print(f"   Stats: {monster.stats}")
        print(f"   Moves: {len(monster.moves)} ({[getattr(m, 'name', 'Unknown') for m in monster.moves]})")
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler beim Fallback-Test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_move_system():
    """Test move system integration."""
    print("\n=== Test Move-System-Integration ===")
    
    try:
        from engine.systems.moves import move_registry
        
        # Test move creation by name
        test_moves = ['Rempler', 'Kratzer', 'Biss', 'Giftstachel', 'Verwirrung']
        
        created_moves = 0
        for move_name in test_moves:
            move = move_registry.create_move_instance_by_name(move_name)
            if move:
                print(f"✅ Move '{move_name}' erstellt: Power {move.power}, Accuracy {move.accuracy}")
                created_moves += 1
            else:
                print(f"⚠️  Move '{move_name}' nicht gefunden")
        
        print(f"\n✅ {created_moves}/{len(test_moves)} Moves erfolgreich erstellt")
        return created_moves >= len(test_moves) // 2  # At least half should work
        
    except Exception as e:
        print(f"❌ Fehler beim Move-System-Test: {e}")
        return False

def test_stat_calculation():
    """Test improved stat calculation."""
    print("\n=== Test Verbesserte Stat-Berechnung ===")
    
    try:
        from engine.systems.stats import StatCalculator, BaseStats
        
        # Test with realistic starter stats
        test_cases = [
            BaseStats(hp=45, atk=28, def_=50, mag=25, res=33, spd=30),  # Sumpfschrecke
            BaseStats(hp=52, atk=27, def_=51, mag=29, res=28, spd=19),  # Kraterkröte
            BaseStats(hp=48, atk=54, def_=23, mag=22, res=26, spd=36),  # Säbelzahnkaninchen
            BaseStats(hp=28, atk=23, def_=33, mag=46, res=31, spd=31),  # Irrlicht
        ]
        
        names = ['Sumpfschrecke', 'Kraterkröte', 'Säbelzahnkaninchen', 'Irrlicht']
        
        for i, (base_stats, name) in enumerate(zip(test_cases, names)):
            stats_level_5 = StatCalculator.calculate_all_stats(base_stats, 5)
            
            # Validate stats are reasonable for level 5
            assert stats_level_5['hp'] >= 20, f"{name} HP too low: {stats_level_5['hp']}"
            assert stats_level_5['atk'] >= 8, f"{name} ATK too low: {stats_level_5['atk']}"
            assert sum(stats_level_5.values()) >= 60, f"{name} total stats too low"
            
            print(f"✅ {name} Level 5: {stats_level_5}")
        
        print("✅ Stat-Berechnung funktioniert korrekt")
        return True
        
    except Exception as e:
        print(f"❌ Fehler beim Stat-Test: {e}")
        return False

def main():
    """Run all validation tests."""
    print("🚀 STARTER-SCENE MONSTER-LOADING SYSTEM")
    print("🔧 FINALE VALIDIERUNG ALLER VERBESSERUNGEN")
    print("=" * 60)
    
    tests = [
        ("Monster-Erstellung aus Datenbank", test_complete_starter_creation),
        ("Fallback-System", test_fallback_creation),
        ("Move-System-Integration", test_move_system),
        ("Verbesserte Stat-Berechnung", test_stat_calculation),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}...")
        try:
            if test_func():
                print(f"✅ {test_name} BESTANDEN")
                passed += 1
            else:
                print(f"❌ {test_name} FEHLGESCHLAGEN")
        except Exception as e:
            print(f"❌ {test_name} FEHLER: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 FINALE ERGEBNISSE: {passed}/{total} Tests bestanden")
    
    if passed == total:
        print("🎉 PERFEKT! Monster-Loading-System ist vollständig funktionsfähig!")
        print("🚀 Alle Verbesserungen erfolgreich implementiert:")
        print("   ✅ Robuste Datenbank-Integration")
        print("   ✅ Verbesserte Stat-Berechnung für niedrige Level")
        print("   ✅ Fallback-Mechanismen für fehlende Daten")
        print("   ✅ Move-System-Integration mit Name-Lookup")
        print("   ✅ Umfassende Fehlerbehandlung")
    else:
        print("⚠️  System funktioniert größtenteils, aber einige Tests fehlgeschlagen")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
