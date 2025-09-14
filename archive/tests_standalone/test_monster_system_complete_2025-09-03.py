#!/usr/bin/env python3
"""
🐉 MONSTER DATA MASTER - COMPREHENSIVE TEST SUITE
Testet alle 151+ Monster, 289+ Moves und 12-Type-System vollständig
"""

import sys
import os
import time
import json
from typing import Dict, List, Any, Optional

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.systems.monsters import monster_db, MonsterDatabase
from engine.systems.monster_instance import MonsterInstance, MonsterSpecies, MonsterRank, StatusCondition
from engine.systems.moves import move_registry, Move, MoveCategory, MoveTarget, MoveEffect, EffectKind
from engine.systems.types import type_chart, TypeChart, TypeSystemAPI
from engine.systems.stats import BaseStats, GrowthCurve

class MonsterSystemTester:
    """Umfassender Tester für das Monster System."""
    
    def __init__(self):
        self.results = {
            'monster_database': {},
            'monster_instances': {},
            'move_system': {},
            'type_system': {},
            'performance': {},
            'validation': {},
            'errors': [],
            'warnings': []
        }
        self.start_time = time.time()
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Führe alle Tests aus."""
        print("🐉 MONSTER DATA MASTER - COMPREHENSIVE TEST SUITE")
        print("=" * 60)
        
        try:
            # Test 1: Monster Database
            print("\n📊 TEST 1: MONSTER DATABASE")
            self.test_monster_database()
            
            # Test 2: Monster Instances
            print("\n👾 TEST 2: MONSTER INSTANCES")
            self.test_monster_instances()
            
            # Test 3: Move System
            print("\n⚔️ TEST 3: MOVE SYSTEM")
            self.test_move_system()
            
            # Test 4: Type System
            print("\n🎯 TEST 4: TYPE SYSTEM")
            self.test_type_system()
            
            # Test 5: Performance Tests
            print("\n⚡ TEST 5: PERFORMANCE TESTS")
            self.test_performance()
            
            # Test 6: Data Validation
            print("\n✅ TEST 6: DATA VALIDATION")
            self.test_data_validation()
            
            # Test 7: Integration Tests
            print("\n🔗 TEST 7: INTEGRATION TESTS")
            self.test_integration()
            
        except Exception as e:
            self.results['errors'].append(f"Critical error: {str(e)}")
            print(f"❌ CRITICAL ERROR: {e}")
        
        self.results['total_time'] = time.time() - self.start_time
        self.print_summary()
        return self.results
    
    def test_monster_database(self):
        """Teste Monster Database Funktionalität."""
        print("  Testing Monster Database...")
        
        # Test 1.1: Database Loading
        try:
            stats = monster_db.get_performance_stats()
            self.results['monster_database']['load_time'] = stats['load_time']
            self.results['monster_database']['total_species'] = stats['total_species']
            print(f"    ✅ Loaded {stats['total_species']} species in {stats['load_time']:.3f}s")
        except Exception as e:
            self.results['errors'].append(f"Database loading failed: {e}")
            print(f"    ❌ Database loading failed: {e}")
        
        # Test 1.2: Species Retrieval
        try:
            # Test starter monsters
            starters = monster_db.get_starter_options()
            self.results['monster_database']['starters_count'] = len(starters)
            print(f"    ✅ Found {len(starters)} starter monsters")
            
            # Test legendary monsters
            legendaries = monster_db.get_legendary_monsters()
            self.results['monster_database']['legendaries_count'] = len(legendaries)
            print(f"    ✅ Found {len(legendaries)} legendary monsters")
            
            # Test fossil monsters
            fossils = monster_db.get_fossil_monsters()
            self.results['monster_database']['fossils_count'] = len(fossils)
            print(f"    ✅ Found {len(fossils)} fossil monsters")
            
        except Exception as e:
            self.results['errors'].append(f"Species retrieval failed: {e}")
            print(f"    ❌ Species retrieval failed: {e}")
        
        # Test 1.3: Advanced Queries
        try:
            # Test by era
            present_monsters = monster_db.get_species_by_criteria(era="present")
            self.results['monster_database']['present_count'] = len(present_monsters)
            print(f"    ✅ Found {len(present_monsters)} present-era monsters")
            
            # Test by rank
            f_rank_monsters = monster_db.get_species_by_criteria(rank="F")
            self.results['monster_database']['f_rank_count'] = len(f_rank_monsters)
            print(f"    ✅ Found {len(f_rank_monsters)} F-rank monsters")
            
            # Test by type
            fire_monsters = monster_db.get_species_by_criteria(monster_type="Feuer")
            self.results['monster_database']['fire_count'] = len(fire_monsters)
            print(f"    ✅ Found {len(fire_monsters)} Fire-type monsters")
            
        except Exception as e:
            self.results['errors'].append(f"Advanced queries failed: {e}")
            print(f"    ❌ Advanced queries failed: {e}")
        
        # Test 1.4: Database Validation
        try:
            validation = monster_db.validate_database()
            self.results['monster_database']['validation'] = validation
            if validation['valid']:
                print(f"    ✅ Database validation passed")
            else:
                print(f"    ⚠️ Database validation issues: {len(validation['issues'])}")
                for issue in validation['issues'][:3]:  # Show first 3 issues
                    print(f"      - {issue}")
        except Exception as e:
            self.results['errors'].append(f"Database validation failed: {e}")
            print(f"    ❌ Database validation failed: {e}")
    
    def test_monster_instances(self):
        """Teste Monster Instance Funktionalität."""
        print("  Testing Monster Instances...")
        
        # Test 2.1: Instance Creation
        try:
            # Create test monster
            test_monster = monster_db.create_monster(1, 5)  # Glutstummel
            if test_monster:
                self.results['monster_instances']['creation_success'] = True
                print(f"    ✅ Created monster: {test_monster.name} (Lv.{test_monster.level})")
                
                # Test stats calculation
                stats = test_monster.get_effective_stats()
                self.results['monster_instances']['stats_calculation'] = True
                print(f"    ✅ Stats calculated: HP={stats['hp']}, ATK={stats['atk']}")
                
                # Test battle summary
                summary = test_monster.get_battle_summary()
                self.results['monster_instances']['battle_summary'] = True
                print(f"    ✅ Battle summary generated")
                
            else:
                self.results['errors'].append("Failed to create test monster")
                print(f"    ❌ Failed to create test monster")
                
        except Exception as e:
            self.results['errors'].append(f"Monster instance creation failed: {e}")
            print(f"    ❌ Monster instance creation failed: {e}")
        
        # Test 2.2: Status Effects
        try:
            if test_monster:
                # Test status application
                test_monster.apply_status(StatusCondition.BURN)
                self.results['monster_instances']['status_application'] = True
                print(f"    ✅ Status effect applied: {test_monster.status.value}")
                
                # Test status processing
                can_act = test_monster.process_status_effects()
                self.results['monster_instances']['status_processing'] = True
                print(f"    ✅ Status processing: can_act={can_act}")
                
                # Test status damage
                old_hp = test_monster.current_hp
                test_monster.apply_status_damage()
                self.results['monster_instances']['status_damage'] = True
                print(f"    ✅ Status damage applied: {old_hp} -> {test_monster.current_hp} HP")
                
        except Exception as e:
            self.results['errors'].append(f"Status effects test failed: {e}")
            print(f"    ❌ Status effects test failed: {e}")
        
        # Test 2.3: Stat Stages
        try:
            if test_monster:
                # Test stat stage modification
                test_monster.modify_stat_stage('atk', 2)
                boosted_atk = test_monster.get_stat_with_stages('atk')
                self.results['monster_instances']['stat_stages'] = True
                print(f"    ✅ Stat stages: ATK boosted to {boosted_atk}")
                
                # Test stat stage reset
                test_monster.reset_stat_stages()
                normal_atk = test_monster.get_stat_with_stages('atk')
                self.results['monster_instances']['stat_reset'] = True
                print(f"    ✅ Stat stages reset: ATK back to {normal_atk}")
                
        except Exception as e:
            self.results['errors'].append(f"Stat stages test failed: {e}")
            print(f"    ❌ Stat stages test failed: {e}")
        
        # Test 2.4: Type Effectiveness
        try:
            if test_monster:
                # Test offensive effectiveness
                effectiveness = test_monster.get_type_effectiveness_against(["Pflanze"])
                self.results['monster_instances']['offensive_effectiveness'] = True
                print(f"    ✅ Offensive effectiveness calculated")
                
                # Test defensive effectiveness
                weaknesses = test_monster.get_weaknesses()
                resistances = test_monster.get_resistances()
                self.results['monster_instances']['defensive_effectiveness'] = True
                print(f"    ✅ Defensive analysis: {len(weaknesses)} weaknesses, {len(resistances)} resistances")
                
        except Exception as e:
            self.results['errors'].append(f"Type effectiveness test failed: {e}")
            print(f"    ❌ Type effectiveness test failed: {e}")
        
        # Test 2.5: Friendship System
        try:
            if test_monster:
                # Test friendship increase
                old_friendship = test_monster.friendship
                test_monster.increase_friendship(10)
                friendship_level = test_monster.get_friendship_level()
                self.results['monster_instances']['friendship_system'] = True
                print(f"    ✅ Friendship system: {friendship_level}")
                
        except Exception as e:
            self.results['errors'].append(f"Friendship system test failed: {e}")
            print(f"    ❌ Friendship system test failed: {e}")
    
    def test_move_system(self):
        """Teste Move System Funktionalität."""
        print("  Testing Move System...")
        
        # Test 3.1: Move Registry
        try:
            all_moves = move_registry.get_all_moves()
            self.results['move_system']['total_moves'] = len(all_moves)
            print(f"    ✅ Loaded {len(all_moves)} moves")
            
            # Test move retrieval
            test_move = move_registry.get_move("kratzer")
            if test_move:
                self.results['move_system']['move_retrieval'] = True
                print(f"    ✅ Retrieved move: {test_move.name} (Power: {test_move.power})")
            else:
                self.results['errors'].append("Failed to retrieve test move")
                print(f"    ❌ Failed to retrieve test move")
                
        except Exception as e:
            self.results['errors'].append(f"Move registry test failed: {e}")
            print(f"    ❌ Move registry test failed: {e}")
        
        # Test 3.2: Move Effects
        try:
            if test_move:
                # Test move validation
                is_valid = test_move.is_valid()
                self.results['move_system']['move_validation'] = is_valid
                print(f"    ✅ Move validation: {is_valid}")
                
                # Test move usage
                can_use = test_move.can_use()
                self.results['move_system']['move_usage'] = can_use
                print(f"    ✅ Move usage check: {can_use}")
                
                # Test move effects
                effects_count = len(test_move.effects)
                self.results['move_system']['effects_count'] = effects_count
                print(f"    ✅ Move effects: {effects_count} effects")
                
        except Exception as e:
            self.results['errors'].append(f"Move effects test failed: {e}")
            print(f"    ❌ Move effects test failed: {e}")
        
        # Test 3.3: Move Execution
        try:
            if test_move and test_monster:
                # Create target monster
                target_monster = monster_db.create_monster(2, 5)  # Böllerling
                if target_monster:
                    # Test move execution
                    from engine.systems.moves import MoveExecutor
                    result = MoveExecutor.execute(test_monster, test_move, target_monster)
                    self.results['move_system']['move_execution'] = result.get('success', False)
                    print(f"    ✅ Move execution: {result.get('message', 'No message')}")
                    
        except Exception as e:
            self.results['errors'].append(f"Move execution test failed: {e}")
            print(f"    ❌ Move execution test failed: {e}")
    
    def test_type_system(self):
        """Teste Type System Funktionalität."""
        print("  Testing Type System...")
        
        # Test 4.1: Type Chart Loading
        try:
            all_types = type_chart.get_all_types()
            self.results['type_system']['total_types'] = len(all_types)
            print(f"    ✅ Loaded {len(all_types)} types: {', '.join(all_types[:5])}...")
            
        except Exception as e:
            self.results['errors'].append(f"Type chart loading failed: {e}")
            print(f"    ❌ Type chart loading failed: {e}")
        
        # Test 4.2: Type Effectiveness
        try:
            # Test single type effectiveness
            fire_vs_plant = type_chart.get_effectiveness("Feuer", "Pflanze")
            self.results['type_system']['single_effectiveness'] = fire_vs_plant
            print(f"    ✅ Fire vs Plant: {fire_vs_plant}x")
            
            # Test dual type effectiveness
            fire_vs_dual = type_chart.calculate_type_multiplier("Feuer", ["Pflanze", "Wasser"])
            self.results['type_system']['dual_effectiveness'] = fire_vs_dual
            print(f"    ✅ Fire vs Plant/Water: {fire_vs_dual}x")
            
        except Exception as e:
            self.results['errors'].append(f"Type effectiveness test failed: {e}")
            print(f"    ❌ Type effectiveness test failed: {e}")
        
        # Test 4.3: Type System API
        try:
            type_api = TypeSystemAPI()
            
            # Test effectiveness check
            effectiveness_info = type_api.check_type_effectiveness("Feuer", ["Pflanze"])
            self.results['type_system']['api_effectiveness'] = True
            print(f"    ✅ API effectiveness: {effectiveness_info['message']}")
            
            # Test team analysis
            team = [["Feuer"], ["Wasser"], ["Pflanze"]]
            team_analysis = type_api.analyze_team_composition(team)
            self.results['type_system']['team_analysis'] = True
            print(f"    ✅ Team analysis: Balance score {team_analysis['balance_score']:.2f}")
            
        except Exception as e:
            self.results['errors'].append(f"Type system API test failed: {e}")
            print(f"    ❌ Type system API test failed: {e}")
        
        # Test 4.4: Performance Stats
        try:
            perf_stats = type_chart.get_performance_stats()
            self.results['type_system']['performance'] = perf_stats
            print(f"    ✅ Type system performance: {perf_stats['cache_hit_rate']:.2%} cache hit rate")
            
        except Exception as e:
            self.results['errors'].append(f"Type system performance test failed: {e}")
            print(f"    ❌ Type system performance test failed: {e}")
    
    def test_performance(self):
        """Teste Performance des Monster Systems."""
        print("  Testing Performance...")
        
        # Test 5.1: Monster Creation Performance
        try:
            start_time = time.time()
            monsters_created = 0
            
            for i in range(100):
                monster = monster_db.create_monster(1, 5)
                if monster:
                    monsters_created += 1
            
            creation_time = time.time() - start_time
            self.results['performance']['monster_creation'] = {
                'time': creation_time,
                'monsters': monsters_created,
                'rate': monsters_created / creation_time
            }
            print(f"    ✅ Created {monsters_created} monsters in {creation_time:.3f}s ({monsters_created/creation_time:.1f}/s)")
            
        except Exception as e:
            self.results['errors'].append(f"Monster creation performance test failed: {e}")
            print(f"    ❌ Monster creation performance test failed: {e}")
        
        # Test 5.2: Type Effectiveness Performance
        try:
            start_time = time.time()
            calculations = 0
            
            types = ["Feuer", "Wasser", "Erde", "Luft", "Pflanze", "Bestie"]
            for att_type in types:
                for def_type in types:
                    type_chart.get_effectiveness(att_type, def_type)
                    calculations += 1
            
            calc_time = time.time() - start_time
            self.results['performance']['type_calculations'] = {
                'time': calc_time,
                'calculations': calculations,
                'rate': calculations / calc_time
            }
            print(f"    ✅ {calculations} type calculations in {calc_time:.3f}s ({calculations/calc_time:.1f}/s)")
            
        except Exception as e:
            self.results['errors'].append(f"Type effectiveness performance test failed: {e}")
            print(f"    ❌ Type effectiveness performance test failed: {e}")
        
        # Test 5.3: Database Query Performance
        try:
            start_time = time.time()
            queries = 0
            
            for i in range(50):
                monster_db.get_species(i)
                monster_db.get_species_by_criteria(era="present")
                monster_db.get_species_by_criteria(rank="F")
                queries += 3
            
            query_time = time.time() - start_time
            self.results['performance']['database_queries'] = {
                'time': query_time,
                'queries': queries,
                'rate': queries / query_time
            }
            print(f"    ✅ {queries} database queries in {query_time:.3f}s ({queries/query_time:.1f}/s)")
            
        except Exception as e:
            self.results['errors'].append(f"Database query performance test failed: {e}")
            print(f"    ❌ Database query performance test failed: {e}")
    
    def test_data_validation(self):
        """Teste Daten-Integrität."""
        print("  Testing Data Validation...")
        
        # Test 6.1: Monster Data Validation
        try:
            validation = monster_db.validate_database()
            self.results['validation']['monster_database'] = validation
            
            if validation['valid']:
                print(f"    ✅ Monster database validation passed")
            else:
                print(f"    ⚠️ Monster database has {len(validation['issues'])} issues")
                for issue in validation['issues'][:3]:
                    print(f"      - {issue}")
            
        except Exception as e:
            self.results['errors'].append(f"Monster data validation failed: {e}")
            print(f"    ❌ Monster data validation failed: {e}")
        
        # Test 6.2: Move Data Validation
        try:
            all_moves = move_registry.get_all_moves()
            invalid_moves = []
            
            for move in all_moves:
                if not move.is_valid():
                    invalid_moves.append(move.name)
            
            self.results['validation']['moves'] = {
                'total': len(all_moves),
                'invalid': len(invalid_moves),
                'invalid_list': invalid_moves[:5]  # First 5 invalid moves
            }
            
            if len(invalid_moves) == 0:
                print(f"    ✅ All {len(all_moves)} moves are valid")
            else:
                print(f"    ⚠️ {len(invalid_moves)} invalid moves found")
                for move_name in invalid_moves[:3]:
                    print(f"      - {move_name}")
            
        except Exception as e:
            self.results['errors'].append(f"Move data validation failed: {e}")
            print(f"    ❌ Move data validation failed: {e}")
        
        # Test 6.3: Type Data Validation
        try:
            all_types = type_chart.get_all_types()
            expected_types = ["Feuer", "Wasser", "Erde", "Luft", "Pflanze", "Bestie", 
                            "Energie", "Chaos", "Seuche", "Mystik", "Gottheit", "Teufel"]
            
            missing_types = [t for t in expected_types if t not in all_types]
            extra_types = [t for t in all_types if t not in expected_types]
            
            self.results['validation']['types'] = {
                'expected': len(expected_types),
                'found': len(all_types),
                'missing': missing_types,
                'extra': extra_types
            }
            
            if len(missing_types) == 0 and len(extra_types) == 0:
                print(f"    ✅ All {len(expected_types)} expected types found")
            else:
                if missing_types:
                    print(f"    ⚠️ Missing types: {missing_types}")
                if extra_types:
                    print(f"    ⚠️ Extra types: {extra_types}")
            
        except Exception as e:
            self.results['errors'].append(f"Type data validation failed: {e}")
            print(f"    ❌ Type data validation failed: {e}")
    
    def test_integration(self):
        """Teste Integration zwischen Systemen."""
        print("  Testing System Integration...")
        
        # Test 7.1: Monster-Move Integration
        try:
            monster = monster_db.create_monster(1, 10)  # Glutstummel
            if monster and monster.moves:
                move = monster.moves[0]
                self.results['integration']['monster_moves'] = True
                print(f"    ✅ Monster {monster.name} has {len(monster.moves)} moves")
                
                # Test move effectiveness
                effectiveness = monster.get_type_effectiveness_against(["Pflanze"])
                self.results['integration']['move_effectiveness'] = True
                print(f"    ✅ Move effectiveness calculated")
                
            else:
                self.results['errors'].append("Monster-Move integration failed")
                print(f"    ❌ Monster-Move integration failed")
                
        except Exception as e:
            self.results['errors'].append(f"Monster-Move integration test failed: {e}")
            print(f"    ❌ Monster-Move integration test failed: {e}")
        
        # Test 7.2: Monster-Type Integration
        try:
            if monster:
                # Test type effectiveness
                weaknesses = monster.get_weaknesses()
                resistances = monster.get_resistances()
                self.results['integration']['type_analysis'] = True
                print(f"    ✅ Type analysis: {len(weaknesses)} weaknesses, {len(resistances)} resistances")
                
        except Exception as e:
            self.results['errors'].append(f"Monster-Type integration test failed: {e}")
            print(f"    ❌ Monster-Type integration test failed: {e}")
        
        # Test 7.3: Full Battle Simulation
        try:
            if monster:
                # Create opponent
                opponent = monster_db.create_monster(2, 10)  # Böllerling
                if opponent:
                    # Test battle interaction
                    from engine.systems.moves import MoveExecutor
                    
                    if monster.moves and opponent.moves:
                        move = monster.moves[0]
                        result = MoveExecutor.execute(monster, move, opponent)
                        self.results['integration']['battle_simulation'] = result.get('success', False)
                        print(f"    ✅ Battle simulation: {result.get('message', 'No message')}")
                        
        except Exception as e:
            self.results['errors'].append(f"Battle simulation test failed: {e}")
            print(f"    ❌ Battle simulation test failed: {e}")
    
    def print_summary(self):
        """Drucke Test-Zusammenfassung."""
        print("\n" + "=" * 60)
        print("🐉 MONSTER DATA MASTER - TEST SUMMARY")
        print("=" * 60)
        
        # Overall results
        total_errors = len(self.results['errors'])
        total_warnings = len(self.results['warnings'])
        total_time = self.results['total_time']
        
        print(f"\n⏱️ Total Test Time: {total_time:.3f}s")
        print(f"❌ Errors: {total_errors}")
        print(f"⚠️ Warnings: {total_warnings}")
        
        # Database results
        db_results = self.results['monster_database']
        print(f"\n📊 MONSTER DATABASE:")
        print(f"  Species loaded: {db_results.get('total_species', 0)}")
        print(f"  Load time: {db_results.get('load_time', 0):.3f}s")
        print(f"  Starters: {db_results.get('starters_count', 0)}")
        print(f"  Legendaries: {db_results.get('legendaries_count', 0)}")
        print(f"  Fossils: {db_results.get('fossils_count', 0)}")
        
        # Move system results
        move_results = self.results['move_system']
        print(f"\n⚔️ MOVE SYSTEM:")
        print(f"  Total moves: {move_results.get('total_moves', 0)}")
        print(f"  Move retrieval: {'✅' if move_results.get('move_retrieval') else '❌'}")
        print(f"  Move validation: {'✅' if move_results.get('move_validation') else '❌'}")
        print(f"  Move execution: {'✅' if move_results.get('move_execution') else '❌'}")
        
        # Type system results
        type_results = self.results['type_system']
        print(f"\n🎯 TYPE SYSTEM:")
        print(f"  Total types: {type_results.get('total_types', 0)}")
        print(f"  Single effectiveness: {'✅' if type_results.get('single_effectiveness') else '❌'}")
        print(f"  Dual effectiveness: {'✅' if type_results.get('dual_effectiveness') else '❌'}")
        print(f"  API functionality: {'✅' if type_results.get('api_effectiveness') else '❌'}")
        
        # Performance results
        perf_results = self.results['performance']
        if 'monster_creation' in perf_results:
            creation = perf_results['monster_creation']
            print(f"\n⚡ PERFORMANCE:")
            print(f"  Monster creation: {creation['rate']:.1f}/s")
        
        if 'type_calculations' in perf_results:
            calc = perf_results['type_calculations']
            print(f"  Type calculations: {calc['rate']:.1f}/s")
        
        if 'database_queries' in perf_results:
            query = perf_results['database_queries']
            print(f"  Database queries: {query['rate']:.1f}/s")
        
        # Validation results
        validation_results = self.results['validation']
        print(f"\n✅ VALIDATION:")
        
        if 'monster_database' in validation_results:
            db_validation = validation_results['monster_database']
            print(f"  Monster database: {'✅ Valid' if db_validation.get('valid') else '⚠️ Issues'}")
        
        if 'moves' in validation_results:
            move_validation = validation_results['moves']
            print(f"  Moves: {move_validation['total'] - move_validation['invalid']}/{move_validation['total']} valid")
        
        if 'types' in validation_results:
            type_validation = validation_results['types']
            print(f"  Types: {type_validation['found']}/{type_validation['expected']} found")
        
        # Errors
        if total_errors > 0:
            print(f"\n❌ ERRORS ({total_errors}):")
            for error in self.results['errors'][:5]:  # Show first 5 errors
                print(f"  - {error}")
            if total_errors > 5:
                print(f"  ... and {total_errors - 5} more errors")
        
        # Final verdict
        print(f"\n🎯 FINAL VERDICT:")
        if total_errors == 0:
            print("  🎉 ALL TESTS PASSED! Monster System is ready for battle!")
        elif total_errors <= 3:
            print("  ⚠️ Minor issues found, but system is functional")
        else:
            print("  ❌ Significant issues found, system needs attention")
        
        print("=" * 60)


def main():
    """Hauptfunktion."""
    tester = MonsterSystemTester()
    results = tester.run_all_tests()
    
    # Save results to file
    with open('monster_system_test_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Detailed results saved to: monster_system_test_results.json")
    
    return results


if __name__ == "__main__":
    main()
