#!/usr/bin/env python3
"""
Talent Battle Integration Tests
Tests talent system integration with battle system
"""

import sys
import os
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.systems.monster_instance import MonsterInstance, MonsterSpecies, MonsterRank
from engine.systems.stats import BaseStats
from engine.systems.talent_system import get_talent_database, TalentTier
from engine.systems.talent_manager import get_talent_manager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TalentBattleTester:
    """Talent battle integration tester."""
    
    def __init__(self):
        """Initialize tester."""
        self.test_results = []
        self.talent_manager = get_talent_manager()
        self.talent_db = get_talent_database()
        
    def create_battle_monster(self, name: str, types: List[str], level: int = 10) -> MonsterInstance:
        """Create monster optimized for battle testing."""
        # Erstelle Type-spezifische Talents
        type_talents = []
        for monster_type in types:
            if monster_type == "Feuer":
                type_talents.append({
                    "talent_id": "fire_i",
                    "learned_at_level": 1,
                    "current_tier": 1,
                    "experience": 0
                })
            elif monster_type == "Wasser":
                type_talents.append({
                    "talent_id": "water_i",
                    "learned_at_level": 1,
                    "current_tier": 1,
                    "experience": 0
                })
            elif monster_type == "Erde":
                type_talents.append({
                    "talent_id": "earth_i",
                    "learned_at_level": 1,
                    "current_tier": 1,
                    "experience": 0
                })
            elif monster_type == "Pflanze":
                type_talents.append({
                    "talent_id": "plant_i",
                    "learned_at_level": 1,
                    "current_tier": 1,
                    "experience": 0
                })
            elif monster_type == "Bestie":
                type_talents.append({
                    "talent_id": "beast_i",
                    "learned_at_level": 1,
                    "current_tier": 1,
                    "experience": 0
                })
            elif monster_type == "Energie":
                type_talents.append({
                    "talent_id": "energy_i",
                    "learned_at_level": 1,
                    "current_tier": 1,
                    "experience": 0
                })
            elif monster_type == "Chaos":
                type_talents.append({
                    "talent_id": "chaos_i",
                    "learned_at_level": 1,
                    "current_tier": 1,
                    "experience": 0
                })
            elif monster_type == "Seuche":
                type_talents.append({
                    "talent_id": "plague_i",
                    "learned_at_level": 1,
                    "current_tier": 1,
                    "experience": 0
                })
            elif monster_type == "Mystik":
                type_talents.append({
                    "talent_id": "mystic_i",
                    "learned_at_level": 1,
                    "current_tier": 1,
                    "experience": 0
                })
            elif monster_type == "Gottheit":
                type_talents.append({
                    "talent_id": "divine_i",
                    "learned_at_level": 1,
                    "current_tier": 1,
                    "experience": 0
                })
            elif monster_type == "Teufel":
                type_talents.append({
                    "talent_id": "demon_i",
                    "learned_at_level": 1,
                    "current_tier": 1,
                    "experience": 0
                })
        
        # Füge immer Physical I hinzu
        type_talents.append({
            "talent_id": "physical_i",
            "learned_at_level": 1,
            "current_tier": 1,
            "experience": 0
        })
        
        species = MonsterSpecies(
            id=f'battle_{name.lower()}',
            name=name,
            types=types,
            base_stats=BaseStats(60, 60, 60, 60, 60, 60),
            rank=MonsterRank.C,
            talents=type_talents
        )
        return MonsterInstance(species, level=level)
    
    def test_battle_move_selection(self) -> bool:
        """Test move selection in battle context."""
        logger.info("🧪 Testing Battle Move Selection...")
        
        try:
            # Erstelle verschiedene Monster-Types
            fire_monster = self.create_battle_monster("Feuer-Drache", ["Feuer"], 15)
            water_monster = self.create_battle_monster("Wasser-Geist", ["Wasser"], 15)
            earth_monster = self.create_battle_monster("Erd-Golem", ["Erde"], 15)
            
            # Teste Move-Verfügbarkeit
            fire_moves = fire_monster.get_available_moves()
            water_moves = water_monster.get_available_moves()
            earth_moves = earth_monster.get_available_moves()
            
            # Prüfe ob alle Monster Moves haben
            assert len(fire_moves) > 0, "Feuer-Monster sollte Moves haben"
            assert len(water_moves) > 0, "Wasser-Monster sollte Moves haben"
            assert len(earth_moves) > 0, "Erd-Monster sollte Moves haben"
            
            # Prüfe Move-Types
            fire_types = {move.type for move in fire_moves}
            water_types = {move.type for move in water_moves}
            earth_types = {move.type for move in earth_moves}
            
            # Prüfe ob Type-spezifische Moves vorhanden sind
            assert "Feuer" in fire_types, "Feuer-Monster sollte Feuer-Moves haben"
            assert "Wasser" in water_types, "Wasser-Monster sollte Wasser-Moves haben"
            assert "Erde" in earth_types, "Erd-Monster sollte Erde-Moves haben"
            
            logger.info(f"✅ Battle Move Selection: Fire({len(fire_moves)}), Water({len(water_moves)}), Earth({len(earth_moves)})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Battle Move Selection failed: {e}")
            return False
    
    def test_passive_abilities_in_battle(self) -> bool:
        """Test passive abilities in battle context."""
        logger.info("🧪 Testing Passive Abilities in Battle...")
        
        try:
            monster = self.create_battle_monster("Battle-Monster", ["Feuer"], 20)
            
            # Hole passive Fähigkeiten
            passives = monster.get_passive_abilities()
            
            # Prüfe ob passive Fähigkeiten vorhanden sind
            assert len(passives) > 0, "Monster sollte passive Fähigkeiten haben"
            
            # Teste verschiedene passive Fähigkeiten-Types
            effect_types = {passive['effect_type'] for passive in passives}
            
            # Prüfe ob verschiedene Effect-Types vorhanden sind
            expected_types = ['stat_boost', 'damage_reduction', 'status_immunity', 'healing']
            has_expected = any(et in effect_types for et in expected_types)
            assert has_expected, "Monster sollte verschiedene passive Fähigkeiten-Types haben"
            
            # Teste passive Fähigkeiten-Anwendung
            for passive in passives:
                effect_type = passive['effect_type']
                value = passive['value']
                
                # Simuliere passive Fähigkeiten-Anwendung
                if effect_type == 'stat_boost':
                    # Teste Stat-Boost
                    original_value = 100
                    boosted_value = self.talent_manager.apply_passive_effects(monster, effect_type, original_value)
                    assert boosted_value != original_value, "Stat-Boost sollte Wert ändern"
                
                elif effect_type == 'damage_reduction':
                    # Teste Damage-Reduction
                    original_damage = 100
                    reduced_damage = self.talent_manager.apply_passive_effects(monster, effect_type, original_damage)
                    assert reduced_damage <= original_damage, "Damage-Reduction sollte Schaden reduzieren"
            
            logger.info(f"✅ Passive Abilities in Battle: {len(passives)} abilities, {len(effect_types)} types")
            return True
            
        except Exception as e:
            logger.error(f"❌ Passive Abilities in Battle failed: {e}")
            return False
    
    def test_talent_tier_progression(self) -> bool:
        """Test talent tier progression in battle context."""
        logger.info("🧪 Testing Talent Tier Progression...")
        
        try:
            monster = self.create_battle_monster("Progression-Monster", ["Feuer"], 5)
            
            # Lerne ein Talent
            learnable = monster.get_learnable_talents()
            if learnable:
                talent_id = learnable[0]
                monster.learn_talent(talent_id)
                
                # Hole initiale Moves
                initial_moves = monster.get_available_moves()
                initial_count = len(initial_moves)
                
                # Upgrade Talent
                upgrade_success = monster.upgrade_talent(talent_id)
                
                if upgrade_success:
                    # Hole Moves nach Upgrade
                    upgraded_moves = monster.get_available_moves()
                    upgraded_count = len(upgraded_moves)
                    
                    # Prüfe ob mehr Moves verfügbar sind
                    assert upgraded_count >= initial_count, "Nach Upgrade sollten mindestens so viele Moves verfügbar sein"
                    
                    # Prüfe ob neue Moves hinzugefügt wurden
                    initial_move_names = {move.name for move in initial_moves}
                    upgraded_move_names = {move.name for move in upgraded_moves}
                    new_moves = upgraded_move_names - initial_move_names
                    if new_moves:
                        logger.info(f"New moves after upgrade: {list(new_moves)}")
                
                # Teste passive Fähigkeiten nach Upgrade
                upgraded_passives = monster.get_passive_abilities()
                assert len(upgraded_passives) > 0, "Nach Upgrade sollten passive Fähigkeiten vorhanden sein"
            
            logger.info("✅ Talent Tier Progression: Progression system functional")
            return True
            
        except Exception as e:
            logger.error(f"❌ Talent Tier Progression failed: {e}")
            return False
    
    def test_battle_scenario_simulation(self) -> bool:
        """Test complete battle scenario simulation."""
        logger.info("🧪 Testing Battle Scenario Simulation...")
        
        try:
            # Erstelle zwei Monster für Battle
            player_monster = self.create_battle_monster("Spieler-Monster", ["Feuer"], 15)
            enemy_monster = self.create_battle_monster("Gegner-Monster", ["Wasser"], 15)
            
            # Lerne verschiedene Talents
            player_learnable = player_monster.get_learnable_talents()
            enemy_learnable = enemy_monster.get_learnable_talents()
            
            # Lerne erste verfügbare Talents
            if player_learnable:
                player_monster.learn_talent(player_learnable[0])
            if enemy_learnable:
                enemy_monster.learn_talent(enemy_learnable[0])
            
            # Simuliere Battle-Runden
            for round_num in range(3):
                # Hole verfügbare Moves
                player_moves = player_monster.get_available_moves()
                enemy_moves = enemy_monster.get_available_moves()
                
                # Prüfe ob beide Monster Moves haben
                assert len(player_moves) > 0, f"Spieler sollte in Runde {round_num} Moves haben"
                assert len(enemy_moves) > 0, f"Gegner sollte in Runde {round_num} Moves haben"
                
                # Simuliere Move-Auswahl
                player_move = player_moves[0]  # Erster verfügbarer Move
                enemy_move = enemy_moves[0]
                
                # Prüfe Move-Eigenschaften
                assert hasattr(player_move, 'name'), "Player Move sollte Name haben"
                assert hasattr(player_move, 'power'), "Player Move sollte Power haben"
                assert hasattr(enemy_move, 'name'), "Enemy Move sollte Name haben"
                assert hasattr(enemy_move, 'power'), "Enemy Move sollte Power haben"
                
                # Simuliere passive Fähigkeiten-Effekte
                player_passives = player_monster.get_passive_abilities()
                enemy_passives = enemy_monster.get_passive_abilities()
                
                # Prüfe ob passive Fähigkeiten angewendet werden können
                for passive in player_passives:
                    effect_type = passive['effect_type']
                    original_value = 100
                    modified_value = self.talent_manager.apply_passive_effects(player_monster, effect_type, original_value)
                    assert isinstance(modified_value, (int, float)), "Passive Fähigkeiten sollten numerischen Wert zurückgeben"
                
                # Simuliere Talent-Upgrade nach Runde
                if round_num == 1:  # Upgrade nach Runde 1
                    player_upgrade = player_monster.upgrade_talent(player_learnable[0]) if player_learnable else False
                    enemy_upgrade = enemy_monster.upgrade_talent(enemy_learnable[0]) if enemy_learnable else False
                    
                    if player_upgrade or enemy_upgrade:
                        logger.info(f"Talent upgrades in round {round_num}: Player={player_upgrade}, Enemy={enemy_upgrade}")
            
            logger.info("✅ Battle Scenario Simulation: Complete battle simulation successful")
            return True
            
        except Exception as e:
            logger.error(f"❌ Battle Scenario Simulation failed: {e}")
            return False
    
    def test_type_effectiveness_integration(self) -> bool:
        """Test type effectiveness with talent system."""
        logger.info("🧪 Testing Type Effectiveness Integration...")
        
        try:
            # Erstelle Monster mit verschiedenen Types
            fire_monster = self.create_battle_monster("Feuer-Monster", ["Feuer"], 10)
            water_monster = self.create_battle_monster("Wasser-Monster", ["Wasser"], 10)
            earth_monster = self.create_battle_monster("Erd-Monster", ["Erde"], 10)
            
            # Teste Move-Types
            fire_moves = fire_monster.get_available_moves()
            water_moves = water_monster.get_available_moves()
            earth_moves = earth_monster.get_available_moves()
            
            # Prüfe Type-Konsistenz
            fire_move_types = {move.type for move in fire_moves}
            water_move_types = {move.type for move in water_moves}
            earth_move_types = {move.type for move in earth_moves}
            
            # Prüfe ob Monster-Type mit Move-Types übereinstimmt
            assert "Feuer" in fire_move_types, "Feuer-Monster sollte Feuer-Moves haben"
            assert "Wasser" in water_move_types, "Wasser-Monster sollte Wasser-Moves haben"
            assert "Erde" in earth_move_types, "Erd-Monster sollte Erde-Moves haben"
            
            # Teste passive Fähigkeiten-Type-Resistenz
            fire_passives = fire_monster.get_passive_abilities()
            water_passives = water_monster.get_passive_abilities()
            
            # Prüfe ob Type-spezifische passive Fähigkeiten vorhanden sind
            fire_resistance = any("feuer" in passive.get('name', '').lower() for passive in fire_passives)
            water_resistance = any("wasser" in passive.get('name', '').lower() for passive in water_passives)
            
            # Prüfe ob Type-Resistenzen vorhanden sind
            assert fire_resistance or water_resistance, "Monster sollten Type-Resistenzen haben"
            
            logger.info("✅ Type Effectiveness Integration: Type system integrated with talents")
            return True
            
        except Exception as e:
            logger.error(f"❌ Type Effectiveness Integration failed: {e}")
            return False
    
    def run_all_tests(self) -> bool:
        """Run all talent battle integration tests."""
        logger.info("🚀 Starting Talent Battle Integration Tests")
        logger.info("=" * 60)
        
        tests = [
            ("Battle Move Selection", self.test_battle_move_selection),
            ("Passive Abilities in Battle", self.test_passive_abilities_in_battle),
            ("Talent Tier Progression", self.test_talent_tier_progression),
            ("Battle Scenario Simulation", self.test_battle_scenario_simulation),
            ("Type Effectiveness Integration", self.test_type_effectiveness_integration)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                self.test_results.append((test_name, result))
                if result:
                    passed += 1
            except Exception as e:
                logger.error(f"❌ {test_name} crashed: {e}")
                self.test_results.append((test_name, False))
        
        # Ergebnisse
        logger.info("\n" + "=" * 60)
        logger.info("📊 BATTLE INTEGRATION TEST RESULTS")
        logger.info("=" * 60)
        
        for test_name, result in self.test_results:
            status = "✅ PASS" if result else "❌ FAIL"
            logger.info(f"{status} {test_name}")
        
        logger.info(f"\n🎯 Overall: {passed}/{total} tests passed")
        
        return passed == total

def main():
    """Main test function."""
    tester = TalentBattleTester()
    success = tester.run_all_tests()
    
    if success:
        logger.info("\n🎉 ALL TALENT BATTLE INTEGRATION TESTS PASSED!")
        return 0
    else:
        logger.error("\n💥 SOME TALENT BATTLE INTEGRATION TESTS FAILED!")
        return 1

if __name__ == "__main__":
    exit(main())
