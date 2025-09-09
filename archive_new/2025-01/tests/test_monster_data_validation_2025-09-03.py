#!/usr/bin/env python3
"""
🐉 MONSTER DATA MASTER - DATA VALIDATION & DQM FORMULAS
Validiert alle 151+ Monster und testet DQM-Style Stat-Berechnungen
"""

import sys
import os
import json
from typing import Dict, List, Any, Optional

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.systems.monsters import monster_db
from engine.systems.monster_instance import MonsterInstance, MonsterSpecies, MonsterRank
from engine.systems.stats import BaseStats, StatCalculator, GrowthCurve
from engine.systems.moves import move_registry
from engine.systems.types import type_chart

class MonsterDataValidator:
    """Validiert Monster-Daten und testet DQM-Style Formulas."""
    
    def __init__(self):
        self.results = {
            'monster_validation': {},
            'stats_validation': {},
            'dqm_formulas': {},
            'data_integrity': {},
            'errors': [],
            'warnings': []
        }
    
    def run_validation(self) -> Dict[str, Any]:
        """Führe vollständige Datenvalidierung durch."""
        print("🐉 MONSTER DATA MASTER - DATA VALIDATION")
        print("=" * 50)
        
        # Test 1: Monster Data Validation
        print("\n📊 MONSTER DATA VALIDATION")
        self.validate_monster_data()
        
        # Test 2: Stats Validation
        print("\n📈 STATS VALIDATION")
        self.validate_stats()
        
        # Test 3: DQM Formulas
        print("\n🧮 DQM FORMULAS TEST")
        self.test_dqm_formulas()
        
        # Test 4: Data Integrity
        print("\n🔍 DATA INTEGRITY CHECK")
        self.check_data_integrity()
        
        self.print_summary()
        return self.results
    
    def validate_monster_data(self):
        """Validiere Monster-Daten."""
        print("  Validating monster data...")
        
        try:
            # Get all species
            all_species = list(monster_db.species.values())
            total_species = len(all_species)
            
            # Validation counters
            valid_species = 0
            invalid_species = 0
            missing_descriptions = 0
            invalid_ranks = 0
            invalid_types = 0
            
            # Valid ranks
            valid_ranks = {'F', 'E', 'D', 'C', 'B', 'A', 'S', 'SS', 'X'}
            
            # Valid types
            valid_types = set(type_chart.get_all_types())
            
            for species in all_species:
                is_valid = True
                
                # Check name
                if not species.name or len(species.name.strip()) == 0:
                    self.results['errors'].append(f"Species {species.id}: Missing name")
                    is_valid = False
                
                # Check types
                if not species.types or len(species.types) == 0:
                    self.results['errors'].append(f"Species {species.id} ({species.name}): Missing types")
                    is_valid = False
                    invalid_types += 1
                else:
                    for monster_type in species.types:
                        if monster_type not in valid_types:
                            self.results['errors'].append(f"Species {species.id} ({species.name}): Invalid type '{monster_type}'")
                            is_valid = False
                            invalid_types += 1
                
                # Check rank
                if not hasattr(species, 'rank') or species.rank.value not in valid_ranks:
                    self.results['errors'].append(f"Species {species.id} ({species.name}): Invalid rank '{getattr(species, 'rank', 'None')}'")
                    is_valid = False
                    invalid_ranks += 1
                
                # Check base stats
                if not hasattr(species, 'base_stats') or not species.base_stats:
                    self.results['errors'].append(f"Species {species.id} ({species.name}): Missing base stats")
                    is_valid = False
                else:
                    # Validate individual stats
                    stats = species.base_stats
                    if stats.hp <= 0 or stats.atk <= 0 or stats.def_ <= 0 or stats.mag <= 0 or stats.res <= 0 or stats.spd <= 0:
                        self.results['errors'].append(f"Species {species.id} ({species.name}): Invalid base stats")
                        is_valid = False
                
                # Check description
                if not hasattr(species, 'description') or not species.description or len(species.description.strip()) == 0:
                    missing_descriptions += 1
                    self.results['warnings'].append(f"Species {species.id} ({species.name}): Missing description")
                
                if is_valid:
                    valid_species += 1
                else:
                    invalid_species += 1
            
            self.results['monster_validation'] = {
                'total_species': total_species,
                'valid_species': valid_species,
                'invalid_species': invalid_species,
                'missing_descriptions': missing_descriptions,
                'invalid_ranks': invalid_ranks,
                'invalid_types': invalid_types,
                'validation_rate': valid_species / total_species if total_species > 0 else 0
            }
            
            print(f"    ✅ Total species: {total_species}")
            print(f"    ✅ Valid species: {valid_species}")
            print(f"    ⚠️ Invalid species: {invalid_species}")
            print(f"    ⚠️ Missing descriptions: {missing_descriptions}")
            print(f"    ⚠️ Invalid ranks: {invalid_ranks}")
            print(f"    ⚠️ Invalid types: {invalid_types}")
            print(f"    📊 Validation rate: {valid_species/total_species*100:.1f}%")
            
        except Exception as e:
            self.results['errors'].append(f"Monster data validation failed: {e}")
            print(f"    ❌ Monster data validation failed: {e}")
    
    def validate_stats(self):
        """Validiere Stat-Berechnungen."""
        print("  Validating stat calculations...")
        
        try:
            # Test different levels and ranks
            test_cases = [
                {'species_id': 1, 'level': 5, 'rank': 'F'},   # Glutstummel
                {'species_id': 50, 'level': 25, 'rank': 'C'}, # Mid-game
                {'species_id': 100, 'level': 50, 'rank': 'A'}, # High-level
                {'species_id': 140, 'level': 75, 'rank': 'S'}, # Legendary
            ]
            
            valid_calculations = 0
            invalid_calculations = 0
            
            for test_case in test_cases:
                try:
                    species = monster_db.get_species(test_case['species_id'])
                    if not species:
                        continue
                    
                    # Create monster instance
                    monster = MonsterInstance(species, test_case['level'])
                    
                    # Validate stats
                    stats = monster.current_stats
                    if (stats.hp > 0 and stats.atk > 0 and stats.def_ > 0 and 
                        stats.mag > 0 and stats.res > 0 and stats.spd > 0):
                        valid_calculations += 1
                        
                        # Check if stats are reasonable for level
                        if stats.hp < test_case['level'] * 2:  # Minimum HP check
                            self.results['warnings'].append(f"Species {test_case['species_id']} Lv.{test_case['level']}: Low HP ({stats.hp})")
                        
                        print(f"    ✅ Species {test_case['species_id']} Lv.{test_case['level']}: HP={stats.hp}, ATK={stats.atk}")
                    else:
                        invalid_calculations += 1
                        self.results['errors'].append(f"Species {test_case['species_id']} Lv.{test_case['level']}: Invalid calculated stats")
                        
                except Exception as e:
                    invalid_calculations += 1
                    self.results['errors'].append(f"Species {test_case['species_id']} Lv.{test_case['level']}: Calculation error - {e}")
            
            self.results['stats_validation'] = {
                'test_cases': len(test_cases),
                'valid_calculations': valid_calculations,
                'invalid_calculations': invalid_calculations,
                'success_rate': valid_calculations / len(test_cases) if test_cases else 0
            }
            
            print(f"    ✅ Valid calculations: {valid_calculations}/{len(test_cases)}")
            print(f"    ❌ Invalid calculations: {invalid_calculations}/{len(test_cases)}")
            
        except Exception as e:
            self.results['errors'].append(f"Stats validation failed: {e}")
            print(f"    ❌ Stats validation failed: {e}")
    
    def test_dqm_formulas(self):
        """Teste DQM-Style Stat-Formeln."""
        print("  Testing DQM-style formulas...")
        
        try:
            # Test DQM-style stat growth
            test_monster = monster_db.create_monster(1, 5)  # Glutstummel
            if not test_monster:
                raise Exception("Failed to create test monster")
            
            # Test stat progression across levels
            levels_to_test = [5, 10, 25, 50, 75, 100]
            stat_progression = {}
            
            for level in levels_to_test:
                monster = monster_db.create_monster(1, level)
                if monster:
                    stats = monster.current_stats
                    stat_progression[level] = {
                        'hp': stats.hp,
                        'atk': stats.atk,
                        'def': stats.def_,
                        'mag': stats.mag,
                        'res': stats.res,
                        'spd': stats.spd
                    }
            
            # Validate progression
            valid_progression = True
            for i in range(1, len(levels_to_test)):
                prev_level = levels_to_test[i-1]
                curr_level = levels_to_test[i]
                
                prev_stats = stat_progression[prev_level]
                curr_stats = stat_progression[curr_level]
                
                # Check if stats generally increase with level
                for stat_name in ['hp', 'atk', 'def', 'mag', 'res', 'spd']:
                    if curr_stats[stat_name] < prev_stats[stat_name]:
                        self.results['warnings'].append(f"Stat {stat_name} decreased from Lv.{prev_level} to Lv.{curr_level}")
                        valid_progression = False
            
            # Test IV impact
            iv_impact_test = True
            try:
                # Create two monsters with different IVs (simulated)
                monster1 = monster_db.create_monster(1, 50)
                monster2 = monster_db.create_monster(1, 50)
                
                if monster1 and monster2:
                    stats1 = monster1.current_stats
                    stats2 = monster2.current_stats
                    
                    # IVs should create variation (though small with current system)
                    total_diff = sum([
                        abs(stats1.hp - stats2.hp),
                        abs(stats1.atk - stats2.atk),
                        abs(stats1.def_ - stats2.def_),
                        abs(stats1.mag - stats2.mag),
                        abs(stats1.res - stats2.res),
                        abs(stats1.spd - stats2.spd)
                    ])
                    
                    if total_diff == 0:
                        self.results['warnings'].append("IV system not creating stat variation")
                        iv_impact_test = False
                    
            except Exception as e:
                self.results['warnings'].append(f"IV impact test failed: {e}")
                iv_impact_test = False
            
            self.results['dqm_formulas'] = {
                'stat_progression': stat_progression,
                'valid_progression': valid_progression,
                'iv_impact_test': iv_impact_test,
                'levels_tested': len(levels_to_test)
            }
            
            print(f"    ✅ Stat progression tested across {len(levels_to_test)} levels")
            print(f"    ✅ Valid progression: {valid_progression}")
            print(f"    ✅ IV impact test: {iv_impact_test}")
            
            # Show progression example
            if stat_progression:
                print(f"    📊 Example progression (Glutstummel):")
                for level in [5, 25, 50, 100]:
                    if level in stat_progression:
                        stats = stat_progression[level]
                        print(f"      Lv.{level}: HP={stats['hp']}, ATK={stats['atk']}, DEF={stats['def']}")
            
        except Exception as e:
            self.results['errors'].append(f"DQM formulas test failed: {e}")
            print(f"    ❌ DQM formulas test failed: {e}")
    
    def check_data_integrity(self):
        """Prüfe Daten-Integrität."""
        print("  Checking data integrity...")
        
        try:
            # Check for duplicate IDs
            species_ids = list(monster_db.species.keys())
            duplicate_ids = len(species_ids) - len(set(species_ids))
            
            # Check for missing species in sequence
            expected_ids = set(range(1, 152))  # 1-151
            actual_ids = set(species_ids)
            missing_ids = expected_ids - actual_ids
            extra_ids = actual_ids - expected_ids
            
            # Check move data integrity
            all_moves = move_registry.get_all_moves()
            invalid_moves = [move for move in all_moves if not move.is_valid()]
            
            # Check type data integrity
            all_types = type_chart.get_all_types()
            expected_types = ["Feuer", "Wasser", "Erde", "Luft", "Pflanze", "Bestie", 
                            "Energie", "Chaos", "Seuche", "Mystik", "Gottheit", "Teufel"]
            missing_types = [t for t in expected_types if t not in all_types]
            extra_types = [t for t in all_types if t not in expected_types]
            
            self.results['data_integrity'] = {
                'duplicate_ids': duplicate_ids,
                'missing_ids': list(missing_ids),
                'extra_ids': list(extra_ids),
                'invalid_moves': len(invalid_moves),
                'missing_types': missing_types,
                'extra_types': extra_types,
                'total_species': len(species_ids),
                'total_moves': len(all_moves),
                'total_types': len(all_types)
            }
            
            print(f"    ✅ Total species: {len(species_ids)}")
            print(f"    ✅ Total moves: {len(all_moves)}")
            print(f"    ✅ Total types: {len(all_types)}")
            
            if duplicate_ids > 0:
                print(f"    ❌ Duplicate IDs: {duplicate_ids}")
            else:
                print(f"    ✅ No duplicate IDs")
            
            if missing_ids:
                print(f"    ⚠️ Missing IDs: {sorted(list(missing_ids))[:10]}...")
            else:
                print(f"    ✅ No missing IDs")
            
            if extra_ids:
                print(f"    ⚠️ Extra IDs: {sorted(list(extra_ids))[:10]}...")
            else:
                print(f"    ✅ No extra IDs")
            
            if invalid_moves:
                print(f"    ❌ Invalid moves: {len(invalid_moves)}")
            else:
                print(f"    ✅ All moves valid")
            
            if missing_types:
                print(f"    ❌ Missing types: {missing_types}")
            else:
                print(f"    ✅ All expected types present")
            
            if extra_types:
                print(f"    ⚠️ Extra types: {extra_types}")
            else:
                print(f"    ✅ No extra types")
            
        except Exception as e:
            self.results['errors'].append(f"Data integrity check failed: {e}")
            print(f"    ❌ Data integrity check failed: {e}")
    
    def print_summary(self):
        """Drucke Validierungs-Zusammenfassung."""
        print("\n" + "=" * 50)
        print("🐉 MONSTER DATA MASTER - VALIDATION SUMMARY")
        print("=" * 50)
        
        # Overall results
        total_errors = len(self.results['errors'])
        total_warnings = len(self.results['warnings'])
        
        print(f"\n❌ Errors: {total_errors}")
        print(f"⚠️ Warnings: {total_warnings}")
        
        # Monster validation
        monster_results = self.results['monster_validation']
        if monster_results:
            print(f"\n📊 MONSTER VALIDATION:")
            print(f"  Total species: {monster_results['total_species']}")
            print(f"  Valid species: {monster_results['valid_species']}")
            print(f"  Validation rate: {monster_results['validation_rate']*100:.1f}%")
            print(f"  Missing descriptions: {monster_results['missing_descriptions']}")
        
        # Stats validation
        stats_results = self.results['stats_validation']
        if stats_results:
            print(f"\n📈 STATS VALIDATION:")
            print(f"  Test cases: {stats_results['test_cases']}")
            print(f"  Success rate: {stats_results['success_rate']*100:.1f}%")
        
        # DQM formulas
        dqm_results = self.results['dqm_formulas']
        if dqm_results:
            print(f"\n🧮 DQM FORMULAS:")
            print(f"  Valid progression: {'✅' if dqm_results['valid_progression'] else '❌'}")
            print(f"  IV impact test: {'✅' if dqm_results['iv_impact_test'] else '❌'}")
            print(f"  Levels tested: {dqm_results['levels_tested']}")
        
        # Data integrity
        integrity_results = self.results['data_integrity']
        if integrity_results:
            print(f"\n🔍 DATA INTEGRITY:")
            print(f"  Duplicate IDs: {integrity_results['duplicate_ids']}")
            print(f"  Missing IDs: {len(integrity_results['missing_ids'])}")
            print(f"  Invalid moves: {integrity_results['invalid_moves']}")
            print(f"  Missing types: {len(integrity_results['missing_types'])}")
        
        # Errors
        if total_errors > 0:
            print(f"\n❌ ERRORS ({total_errors}):")
            for error in self.results['errors'][:5]:
                print(f"  - {error}")
            if total_errors > 5:
                print(f"  ... and {total_errors - 5} more errors")
        
        # Warnings
        if total_warnings > 0:
            print(f"\n⚠️ WARNINGS ({total_warnings}):")
            for warning in self.results['warnings'][:5]:
                print(f"  - {warning}")
            if total_warnings > 5:
                print(f"  ... and {total_warnings - 5} more warnings")
        
        # Final verdict
        print(f"\n🎯 FINAL VERDICT:")
        if total_errors == 0:
            print("  🎉 ALL VALIDATIONS PASSED! Monster data is ready!")
        elif total_errors <= 5:
            print("  ⚠️ Minor issues found, but data is mostly valid")
        else:
            print("  ❌ Significant issues found, data needs attention")
        
        print("=" * 50)


def main():
    """Hauptfunktion."""
    validator = MonsterDataValidator()
    results = validator.run_validation()
    
    # Save results to file
    with open('monster_data_validation_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Detailed results saved to: monster_data_validation_results.json")
    
    return results


if __name__ == "__main__":
    main()
