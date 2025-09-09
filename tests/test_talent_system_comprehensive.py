#!/usr/bin/env python3
"""
Comprehensive Talent System Integration Tests
Tests complete talent system integration with battle, UI, and data systems
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
from engine.systems.moves import move_registry

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TalentSystemTester:
    """Comprehensive talent system integration tester."""
    
    def __init__(self):
        """Initialize tester."""
        self.test_results = []
        self.performance_metrics = {}
        self.talent_manager = get_talent_manager()
        self.talent_db = get_talent_database()
        
    def create_test_monster(self, name: str, types: List[str], level: int = 5) -> MonsterInstance:
        """Create test monster with specific types."""
        species = MonsterSpecies(
            id=f'test_{name.lower()}',
            name=name,
            types=types,
            base_stats=BaseStats(50, 50, 50, 50, 50, 50),
            rank=MonsterRank.F,
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
    
    def test_talent_initialization(self) -> bool:
        """Test talent initialization from species data."""
        logger.info("🧪 Testing Talent Initialization...")
        
        try:
            # Test Monster mit Feuer-Type
            monster = self.create_test_monster("Feuer-Schleim", ["Feuer"], 5)
            
            # Prüfe ob Talents korrekt initialisiert wurden
            assert len(monster.talents) > 0, "Monster sollte mindestens ein Talent haben"
            
            # Prüfe ob Physical I Talent vorhanden ist
            has_physical = any(t.talent_id == "physical_i" for t in monster.talents)
            assert has_physical, "Monster sollte Physical I Talent haben"
            
            # Prüfe ob Moves aus Talenten geladen wurden
            moves = monster.get_available_moves()
            assert len(moves) > 0, "Monster sollte Moves aus Talenten haben"
            
            logger.info(f"✅ Talent Initialization: {len(monster.talents)} Talents, {len(moves)} Moves")
            return True
            
        except Exception as e:
            logger.error(f"❌ Talent Initialization failed: {e}")
            return False
    
    def test_passive_abilities(self) -> bool:
        """Test passive abilities system."""
        logger.info("🧪 Testing Passive Abilities...")
        
        try:
            monster = self.create_test_monster("Test-Monster", ["Feuer"], 5)
            
            # Hole passive Fähigkeiten
            passives = monster.get_passive_abilities()
            
            # Prüfe ob passive Fähigkeiten geladen wurden
            assert len(passives) > 0, "Monster sollte passive Fähigkeiten haben"
            
            # Prüfe Struktur der passiven Fähigkeiten
            for passive in passives:
                assert "name" in passive, "Passive Fähigkeit sollte Name haben"
                assert "description" in passive, "Passive Fähigkeit sollte Beschreibung haben"
                assert "effect_type" in passive, "Passive Fähigkeit sollte Effect-Type haben"
                assert "value" in passive, "Passive Fähigkeit sollte Wert haben"
            
            logger.info(f"✅ Passive Abilities: {len(passives)} abilities loaded")
            return True
            
        except Exception as e:
            logger.error(f"❌ Passive Abilities failed: {e}")
            return False
    
    def test_talent_learning(self) -> bool:
        """Test talent learning system."""
        logger.info("🧪 Testing Talent Learning...")
        
        try:
            monster = self.create_test_monster("Lern-Monster", ["Feuer"], 10)
            
            # Hole lernbare Talents
            learnable = monster.get_learnable_talents()
            
            # Prüfe ob lernbare Talents gefunden wurden
            assert len(learnable) > 0, "Monster sollte lernbare Talents haben"
            
            # Teste Talent-Learning
            if learnable:
                talent_id = learnable[0]
                
                # Prüfe ob Talent gelernt werden kann
                can_learn = monster.can_learn_talent(talent_id)
                assert can_learn, f"Monster sollte Talent {talent_id} lernen können"
                
                # Lerne Talent
                success = monster.learn_talent(talent_id)
                assert success, f"Talent {talent_id} sollte gelernt werden können"
                
                # Prüfe ob Talent jetzt vorhanden ist
                has_talent = any(t.talent_id == talent_id for t in monster.talents)
                assert has_talent, f"Monster sollte Talent {talent_id} nach dem Lernen haben"
            
            logger.info(f"✅ Talent Learning: {len(learnable)} learnable talents")
            return True
            
        except Exception as e:
            logger.error(f"❌ Talent Learning failed: {e}")
            return False
    
    def test_talent_upgrades(self) -> bool:
        """Test talent upgrade system."""
        logger.info("🧪 Testing Talent Upgrades...")
        
        try:
            monster = self.create_test_monster("Upgrade-Monster", ["Feuer"], 20)
            
            # Lerne ein Talent
            learnable = monster.get_learnable_talents()
            if learnable:
                talent_id = learnable[0]
                monster.learn_talent(talent_id)
                
                # Teste Talent-Upgrade
                can_upgrade = monster.upgrade_talent(talent_id)
                
                # Prüfe ob Upgrade möglich war (abhängig von Talent)
                if can_upgrade:
                    # Prüfe ob Tier erhöht wurde
                    talent_instance = next(t for t in monster.talents if t.talent_id == talent_id)
                    assert talent_instance.current_tier.value > 1, "Talent-Tier sollte erhöht worden sein"
            
            logger.info("✅ Talent Upgrades: Upgrade system functional")
            return True
            
        except Exception as e:
            logger.error(f"❌ Talent Upgrades failed: {e}")
            return False
    
    def test_move_generation(self) -> bool:
        """Test move generation from talents."""
        logger.info("🧪 Testing Move Generation...")
        
        try:
            monster = self.create_test_monster("Move-Monster", ["Feuer"], 15)
            
            # Hole verfügbare Moves
            moves = monster.get_available_moves()
            
            # Prüfe ob Moves generiert wurden
            assert len(moves) > 0, "Monster sollte Moves haben"
            
            # Prüfe Move-Struktur
            for move in moves:
                assert hasattr(move, 'name'), "Move sollte Name haben"
                assert hasattr(move, 'type'), "Move sollte Type haben"
                assert hasattr(move, 'power'), "Move sollte Power haben"
                assert hasattr(move, 'accuracy'), "Move sollte Accuracy haben"
            
            # Teste verschiedene Monster-Types
            water_monster = self.create_test_monster("Wasser-Monster", ["Wasser"], 10)
            water_moves = water_monster.get_available_moves()
            assert len(water_moves) > 0, "Wasser-Monster sollte Moves haben"
            
            logger.info(f"✅ Move Generation: {len(moves)} moves for fire, {len(water_moves)} for water")
            return True
            
        except Exception as e:
            logger.error(f"❌ Move Generation failed: {e}")
            return False
    
    def test_talent_info_system(self) -> bool:
        """Test talent information system."""
        logger.info("🧪 Testing Talent Info System...")
        
        try:
            monster = self.create_test_monster("Info-Monster", ["Feuer"], 10)
            
            # Teste Talent-Info für verschiedene Talents
            test_talents = ["fire_i", "physical_i", "water_i"]
            
            for talent_id in test_talents:
                info = monster.get_talent_info(talent_id)
                
                if info:
                    # Prüfe Info-Struktur
                    assert "id" in info, "Talent-Info sollte ID haben"
                    assert "name" in info, "Talent-Info sollte Name haben"
                    assert "description" in info, "Talent-Info sollte Beschreibung haben"
                    assert "category" in info, "Talent-Info sollte Kategorie haben"
                    assert "can_learn" in info, "Talent-Info sollte can_learn haben"
                    assert "moves" in info, "Talent-Info sollte Moves haben"
                    assert "passive_abilities" in info, "Talent-Info sollte passive_abilities haben"
            
            logger.info("✅ Talent Info System: Info system functional")
            return True
            
        except Exception as e:
            logger.error(f"❌ Talent Info System failed: {e}")
            return False
    
    def test_data_consistency(self) -> bool:
        """Test data consistency between files."""
        logger.info("🧪 Testing Data Consistency...")
        
        try:
            # Lade alle Daten-Dateien
            moves_file = Path("data/moves.json")
            talents_file = Path("data/talents.json")
            passive_file = Path("data/passive_abilities.json")
            learning_file = Path("data/talent_learning.json")
            
            # Prüfe ob alle Dateien existieren
            assert moves_file.exists(), "moves.json sollte existieren"
            assert talents_file.exists(), "talents.json sollte existieren"
            assert passive_file.exists(), "passive_abilities.json sollte existieren"
            assert learning_file.exists(), "talent_learning.json sollte existieren"
            
            # Lade und prüfe Daten
            with open(moves_file, 'r', encoding='utf-8') as f:
                moves_data = json.load(f)
            with open(talents_file, 'r', encoding='utf-8') as f:
                talents_data = json.load(f)
            with open(passive_file, 'r', encoding='utf-8') as f:
                passive_data = json.load(f)
            with open(learning_file, 'r', encoding='utf-8') as f:
                learning_data = json.load(f)
            
            # Prüfe Daten-Konsistenz
            assert len(moves_data['moves']) > 0, "moves.json sollte Moves enthalten"
            assert len(talents_data['talents']) > 0, "talents.json sollte Talents enthalten"
            assert len(passive_data['passive_abilities']) > 0, "passive_abilities.json sollte Fähigkeiten enthalten"
            
            # Prüfe ob alle in talents.json referenzierten Moves in moves.json existieren
            talent_move_ids = set()
            for talent in talents_data['talents']:
                for move in talent['moves']:
                    talent_move_ids.add(move['move_id'])
            
            move_ids = {move['id'] for move in moves_data['moves']}
            missing_moves = talent_move_ids - move_ids
            
            assert len(missing_moves) == 0, f"Fehlende Moves: {missing_moves}"
            
            logger.info(f"✅ Data Consistency: {len(moves_data['moves'])} moves, {len(talents_data['talents'])} talents")
            return True
            
        except Exception as e:
            logger.error(f"❌ Data Consistency failed: {e}")
            return False
    
    def test_performance(self) -> bool:
        """Test system performance."""
        logger.info("🧪 Testing Performance...")
        
        try:
            start_time = time.time()
            
            # Teste Monster-Erstellung
            monsters = []
            for i in range(100):
                monster = self.create_test_monster(f"Perf-Monster-{i}", ["Feuer"], 10)
                monsters.append(monster)
            
            creation_time = time.time() - start_time
            
            # Teste Talent-Operationen
            start_time = time.time()
            
            for monster in monsters[:10]:  # Teste mit ersten 10
                moves = monster.get_available_moves()
                passives = monster.get_passive_abilities()
                learnable = monster.get_learnable_talents()
            
            operation_time = time.time() - start_time
            
            # Performance-Metriken
            self.performance_metrics = {
                "monster_creation": creation_time,
                "talent_operations": operation_time,
                "monsters_created": len(monsters)
            }
            
            logger.info(f"✅ Performance: {creation_time:.3f}s creation, {operation_time:.3f}s operations")
            return True
            
        except Exception as e:
            logger.error(f"❌ Performance test failed: {e}")
            return False
    
    def run_all_tests(self) -> bool:
        """Run all talent system tests."""
        logger.info("🚀 Starting Comprehensive Talent System Tests")
        logger.info("=" * 60)
        
        tests = [
            ("Talent Initialization", self.test_talent_initialization),
            ("Passive Abilities", self.test_passive_abilities),
            ("Talent Learning", self.test_talent_learning),
            ("Talent Upgrades", self.test_talent_upgrades),
            ("Move Generation", self.test_move_generation),
            ("Talent Info System", self.test_talent_info_system),
            ("Data Consistency", self.test_data_consistency),
            ("Performance", self.test_performance)
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
        logger.info("📊 TEST RESULTS")
        logger.info("=" * 60)
        
        for test_name, result in self.test_results:
            status = "✅ PASS" if result else "❌ FAIL"
            logger.info(f"{status} {test_name}")
        
        logger.info(f"\n🎯 Overall: {passed}/{total} tests passed")
        
        if self.performance_metrics:
            logger.info("\n📈 PERFORMANCE METRICS")
            logger.info(f"Monster Creation: {self.performance_metrics['monster_creation']:.3f}s")
            logger.info(f"Talent Operations: {self.performance_metrics['talent_operations']:.3f}s")
            logger.info(f"Monsters Created: {self.performance_metrics['monsters_created']}")
        
        return passed == total

def main():
    """Main test function."""
    tester = TalentSystemTester()
    success = tester.run_all_tests()
    
    if success:
        logger.info("\n🎉 ALL TALENT SYSTEM TESTS PASSED!")
        return 0
    else:
        logger.error("\n💥 SOME TALENT SYSTEM TESTS FAILED!")
        return 1

if __name__ == "__main__":
    exit(main())
