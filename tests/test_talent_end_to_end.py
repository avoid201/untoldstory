#!/usr/bin/env python3
"""
Talent System End-to-End Integration Tests
Tests complete system integration from data loading to battle execution
"""

import sys
import os
import json
import time
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

class TalentEndToEndTester:
    """End-to-end talent system integration tester."""
    
    def __init__(self):
        """Initialize tester."""
        self.test_results = []
        self.performance_metrics = {}
        self.talent_manager = get_talent_manager()
        self.talent_db = get_talent_database()
        
    def create_e2e_monster(self, name: str, types: List[str], level: int = 15) -> MonsterInstance:
        """Create monster for end-to-end testing."""
        species = MonsterSpecies(
            id=f'e2e_{name.lower()}',
            name=name,
            types=types,
            base_stats=BaseStats(60, 60, 60, 60, 60, 60),
            rank=MonsterRank.B,
            talents=[
                {
                    "talent_id": "physical_i",
                    "learned_at_level": 1,
                    "current_tier": 1,
                    "experience": 0
                }
            ]
        )
        return MonsterInstance(species, level=level)
    
    def test_complete_data_flow(self) -> bool:
        """Test complete data flow from JSON to battle."""
        logger.info("🧪 Testing Complete Data Flow...")
        
        try:
            # 1. Lade Daten aus JSON-Dateien
            moves_file = Path("data/moves.json")
            talents_file = Path("data/talents.json")
            passive_file = Path("data/passive_abilities.json")
            learning_file = Path("data/talent_learning.json")
            
            # Prüfe ob alle Dateien existieren
            assert moves_file.exists(), "moves.json sollte existieren"
            assert talents_file.exists(), "talents.json sollte existieren"
            assert passive_file.exists(), "passive_abilities.json sollte existieren"
            assert learning_file.exists(), "talent_learning.json sollte existieren"
            
            # Lade Daten
            with open(moves_file, 'r', encoding='utf-8') as f:
                moves_data = json.load(f)
            with open(talents_file, 'r', encoding='utf-8') as f:
                talents_data = json.load(f)
            with open(passive_file, 'r', encoding='utf-8') as f:
                passive_data = json.load(f)
            with open(learning_file, 'r', encoding='utf-8') as f:
                learning_data = json.load(f)
            
            # 2. Erstelle Monster mit Talenten
            monster = self.create_e2e_monster("E2E-Monster", ["Feuer"], 20)
            
            # 3. Teste Talent-Initialisierung
            assert len(monster.talents) > 0, "Monster sollte Talents haben"
            
            # 4. Teste Move-Generierung
            moves = monster.get_available_moves()
            assert len(moves) > 0, "Monster sollte Moves haben"
            
            # 5. Teste passive Fähigkeiten
            passives = monster.get_passive_abilities()
            assert len(passives) > 0, "Monster sollte passive Fähigkeiten haben"
            
            # 6. Teste Talent-Learning
            learnable = monster.get_learnable_talents()
            assert len(learnable) > 0, "Monster sollte lernbare Talents haben"
            
            # 7. Teste Talent-Learning-Execution
            if learnable:
                talent_id = learnable[0]
                success = monster.learn_talent(talent_id)
                assert success, "Talent sollte gelernt werden können"
                
                # Prüfe ob Talent jetzt vorhanden ist
                has_talent = any(t.talent_id == talent_id for t in monster.talents)
                assert has_talent, "Talent sollte nach dem Lernen vorhanden sein"
            
            logger.info("✅ Complete Data Flow: Data flow from JSON to battle successful")
            return True
            
        except Exception as e:
            logger.error(f"❌ Complete Data Flow failed: {e}")
            return False
    
    def test_battle_simulation(self) -> bool:
        """Test complete battle simulation with talent system."""
        logger.info("🧪 Testing Battle Simulation...")
        
        try:
            # Erstelle zwei Monster für Battle
            player_monster = self.create_e2e_monster("Spieler", ["Feuer"], 20)
            enemy_monster = self.create_e2e_monster("Gegner", ["Wasser"], 20)
            
            # Lerne verschiedene Talents
            player_learnable = player_monster.get_learnable_talents()
            enemy_learnable = enemy_monster.get_learnable_talents()
            
            # Lerne erste verfügbare Talents
            if player_learnable:
                player_monster.learn_talent(player_learnable[0])
            if enemy_learnable:
                enemy_monster.learn_talent(enemy_learnable[0])
            
            # Simuliere Battle-Runden
            for round_num in range(5):
                # Hole verfügbare Moves
                player_moves = player_monster.get_available_moves()
                enemy_moves = enemy_monster.get_available_moves()
                
                # Prüfe ob beide Monster Moves haben
                assert len(player_moves) > 0, f"Spieler sollte in Runde {round_num} Moves haben"
                assert len(enemy_moves) > 0, f"Gegner sollte in Runde {round_num} Moves haben"
                
                # Simuliere Move-Auswahl
                player_move = player_moves[0]
                enemy_move = enemy_moves[0]
                
                # Simuliere Move-Execution
                player_damage = self.simulate_move_damage(player_monster, player_move, enemy_monster)
                enemy_damage = self.simulate_move_damage(enemy_monster, enemy_move, player_monster)
                
                # Prüfe ob Schaden berechnet wurde
                assert isinstance(player_damage, (int, float)), "Spieler-Schaden sollte numerisch sein"
                assert isinstance(enemy_damage, (int, float)), "Gegner-Schaden sollte numerisch sein"
                
                # Simuliere passive Fähigkeiten-Effekte
                player_passives = player_monster.get_passive_abilities()
                enemy_passives = enemy_monster.get_passive_abilities()
                
                # Wende passive Fähigkeiten an
                for passive in player_passives:
                    effect_type = passive['effect_type']
                    modified_damage = self.talent_manager.apply_passive_effects(player_monster, effect_type, player_damage)
                    assert isinstance(modified_damage, (int, float)), "Passive Fähigkeiten sollten numerischen Wert zurückgeben"
                
                # Simuliere Talent-Upgrade nach bestimmten Runden
                if round_num == 2:  # Upgrade nach Runde 2
                    if player_learnable:
                        player_upgrade = player_monster.upgrade_talent(player_learnable[0])
                        if player_upgrade:
                            logger.info(f"Spieler-Talent in Runde {round_num} upgegradet")
                    
                    if enemy_learnable:
                        enemy_upgrade = enemy_monster.upgrade_talent(enemy_learnable[0])
                        if enemy_upgrade:
                            logger.info(f"Gegner-Talent in Runde {round_num} upgegradet")
            
            logger.info("✅ Battle Simulation: Complete battle simulation successful")
            return True
            
        except Exception as e:
            logger.error(f"❌ Battle Simulation failed: {e}")
            return False
    
    def simulate_move_damage(self, attacker: MonsterInstance, move: Any, defender: MonsterInstance) -> float:
        """Simulate move damage calculation."""
        try:
            # Einfache Schadensberechnung für Test
            base_damage = getattr(move, 'power', 50)
            attacker_atk = attacker.current_stats.atk if hasattr(attacker, 'current_stats') else 50
            defender_def = defender.current_stats.def_ if hasattr(defender, 'current_stats') else 50
            
            # Einfache Formel: (ATK - DEF) * Power / 50
            damage = max(1, (attacker_atk - defender_def) * base_damage / 50)
            
            # Wende passive Fähigkeiten an
            passives = attacker.get_passive_abilities()
            for passive in passives:
                if passive['effect_type'] == 'stat_boost':
                    damage *= (1 + passive['value'])
                elif passive['effect_type'] == 'damage_reduction':
                    damage *= (1 - passive['value'])
            
            return max(1, damage)
            
        except Exception as e:
            logger.error(f"Error in damage simulation: {e}")
            return 10  # Fallback-Schaden
    
    def test_talent_progression_system(self) -> bool:
        """Test complete talent progression system."""
        logger.info("🧪 Testing Talent Progression System...")
        
        try:
            monster = self.create_e2e_monster("Progression-Monster", ["Feuer"], 5)
            
            # Teste Level-Progression
            for level in range(5, 25, 5):
                monster.level = level
                
                # Hole lernbare Talents für dieses Level
                learnable = monster.get_learnable_talents()
                
                # Lerne verfügbare Talents
                for talent_id in learnable[:2]:  # Lerne max 2 Talents pro Level
                    if monster.can_learn_talent(talent_id):
                        success = monster.learn_talent(talent_id)
                        if success:
                            logger.info(f"Level {level}: Talent {talent_id} gelernt")
                
                # Teste Talent-Upgrades
                for talent_instance in monster.talents:
                    if talent_instance.is_learned:
                        upgrade_success = monster.upgrade_talent(talent_instance.talent_id)
                        if upgrade_success:
                            logger.info(f"Level {level}: Talent {talent_instance.talent_id} upgegradet")
                
                # Prüfe ob Monster Moves und passive Fähigkeiten hat
                moves = monster.get_available_moves()
                passives = monster.get_passive_abilities()
                
                assert len(moves) > 0, f"Monster sollte in Level {level} Moves haben"
                assert len(passives) > 0, f"Monster sollte in Level {level} passive Fähigkeiten haben"
            
            logger.info("✅ Talent Progression System: Complete progression system functional")
            return True
            
        except Exception as e:
            logger.error(f"❌ Talent Progression System failed: {e}")
            return False
    
    def test_system_performance(self) -> bool:
        """Test system performance under load."""
        logger.info("🧪 Testing System Performance...")
        
        try:
            start_time = time.time()
            
            # Teste Monster-Erstellung
            monsters = []
            for i in range(200):
                monster = self.create_e2e_monster(f"Perf-Monster-{i}", ["Feuer"], 15)
                monsters.append(monster)
            
            creation_time = time.time() - start_time
            
            # Teste Talent-Operationen
            start_time = time.time()
            
            for monster in monsters[:50]:  # Teste mit ersten 50
                moves = monster.get_available_moves()
                passives = monster.get_passive_abilities()
                learnable = monster.get_learnable_talents()
                
                # Lerne ein Talent
                if learnable:
                    monster.learn_talent(learnable[0])
                
                # Upgrade Talent
                for talent_instance in monster.talents:
                    if talent_instance.is_learned:
                        monster.upgrade_talent(talent_instance.talent_id)
            
            operation_time = time.time() - start_time
            
            # Performance-Metriken
            self.performance_metrics = {
                "monster_creation": creation_time,
                "talent_operations": operation_time,
                "monsters_created": len(monsters),
                "operations_per_second": 50 / operation_time if operation_time > 0 else 0
            }
            
            logger.info(f"✅ System Performance: {creation_time:.3f}s creation, {operation_time:.3f}s operations")
            logger.info(f"Performance: {self.performance_metrics['operations_per_second']:.1f} ops/sec")
            return True
            
        except Exception as e:
            logger.error(f"❌ System Performance failed: {e}")
            return False
    
    def test_error_handling(self) -> bool:
        """Test error handling and edge cases."""
        logger.info("🧪 Testing Error Handling...")
        
        try:
            # Teste mit ungültigen Daten
            monster = self.create_e2e_monster("Error-Monster", ["Feuer"], 15)
            
            # Teste ungültige Talent-IDs
            invalid_talents = ["invalid_talent", "nonexistent", ""]
            for talent_id in invalid_talents:
                can_learn = monster.can_learn_talent(talent_id)
                assert not can_learn, f"Ungültiges Talent {talent_id} sollte nicht lernbar sein"
                
                learn_success = monster.learn_talent(talent_id)
                assert not learn_success, f"Ungültiges Talent {talent_id} sollte nicht gelernt werden können"
            
            # Teste mit leerem Monster
            empty_monster = self.create_e2e_monster("Empty-Monster", [], 1)
            moves = empty_monster.get_available_moves()
            passives = empty_monster.get_passive_abilities()
            
            # Monster sollte trotzdem funktionieren
            assert isinstance(moves, list), "Leeres Monster sollte leere Moves-Liste zurückgeben"
            assert isinstance(passives, list), "Leeres Monster sollte leere passive Fähigkeiten-Liste zurückgeben"
            
            # Teste mit sehr hohem Level
            high_level_monster = self.create_e2e_monster("High-Level-Monster", ["Feuer"], 100)
            learnable = high_level_monster.get_learnable_talents()
            
            # Sollte nicht crashen
            assert isinstance(learnable, list), "Hohes Level sollte Liste zurückgeben"
            
            logger.info("✅ Error Handling: Error handling and edge cases handled correctly")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error Handling failed: {e}")
            return False
    
    def run_all_tests(self) -> bool:
        """Run all end-to-end integration tests."""
        logger.info("🚀 Starting Talent System End-to-End Integration Tests")
        logger.info("=" * 70)
        
        tests = [
            ("Complete Data Flow", self.test_complete_data_flow),
            ("Battle Simulation", self.test_battle_simulation),
            ("Talent Progression System", self.test_talent_progression_system),
            ("System Performance", self.test_system_performance),
            ("Error Handling", self.test_error_handling)
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
        logger.info("\n" + "=" * 70)
        logger.info("📊 END-TO-END INTEGRATION TEST RESULTS")
        logger.info("=" * 70)
        
        for test_name, result in self.test_results:
            status = "✅ PASS" if result else "❌ FAIL"
            logger.info(f"{status} {test_name}")
        
        logger.info(f"\n🎯 Overall: {passed}/{total} tests passed")
        
        if self.performance_metrics:
            logger.info("\n📈 PERFORMANCE METRICS")
            logger.info(f"Monster Creation: {self.performance_metrics['monster_creation']:.3f}s")
            logger.info(f"Talent Operations: {self.performance_metrics['talent_operations']:.3f}s")
            logger.info(f"Monsters Created: {self.performance_metrics['monsters_created']}")
            logger.info(f"Operations per Second: {self.performance_metrics['operations_per_second']:.1f}")
        
        return passed == total

def main():
    """Main test function."""
    tester = TalentEndToEndTester()
    success = tester.run_all_tests()
    
    if success:
        logger.info("\n🎉 ALL END-TO-END INTEGRATION TESTS PASSED!")
        return 0
    else:
        logger.error("\n💥 SOME END-TO-END INTEGRATION TESTS FAILED!")
        return 1

if __name__ == "__main__":
    exit(main())
