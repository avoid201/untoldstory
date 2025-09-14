#!/usr/bin/env python3
"""
Talent UI Integration Tests
Tests talent system integration with UI components
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

class TalentUITester:
    """Talent UI integration tester."""
    
    def __init__(self):
        """Initialize tester."""
        self.test_results = []
        self.talent_manager = get_talent_manager()
        self.talent_db = get_talent_database()
        
    def create_ui_test_monster(self, name: str, types: List[str], level: int = 10) -> MonsterInstance:
        """Create monster optimized for UI testing."""
        species = MonsterSpecies(
            id=f'ui_{name.lower()}',
            name=name,
            types=types,
            base_stats=BaseStats(50, 50, 50, 50, 50, 50),
            rank=MonsterRank.C,
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
    
    def test_talent_display_data(self) -> bool:
        """Test talent display data generation."""
        logger.info("🧪 Testing Talent Display Data...")
        
        try:
            monster = self.create_ui_test_monster("UI-Monster", ["Feuer"], 15)
            
            # Teste Talent-Info für Display
            talent_infos = []
            for talent_instance in monster.talents:
                info = monster.get_talent_info(talent_instance.talent_id)
                if info:
                    talent_infos.append(info)
            
            # Prüfe ob Talent-Infos generiert wurden
            assert len(talent_infos) > 0, "Monster sollte Talent-Infos für Display haben"
            
            # Prüfe Display-Daten-Struktur
            for info in talent_infos:
                # Prüfe erforderliche Display-Felder
                assert "name" in info, "Talent-Info sollte Name für Display haben"
                assert "description" in info, "Talent-Info sollte Beschreibung für Display haben"
                assert "category" in info, "Talent-Info sollte Kategorie für Display haben"
                assert "current_tier" in info, "Talent-Info sollte aktuelles Tier für Display haben"
                assert "max_tier" in info, "Talent-Info sollte maximales Tier für Display haben"
                assert "can_learn" in info, "Talent-Info sollte Lern-Status für Display haben"
                assert "can_upgrade" in info, "Talent-Info sollte Upgrade-Status für Display haben"
                assert "moves" in info, "Talent-Info sollte Moves für Display haben"
                assert "passive_abilities" in info, "Talent-Info sollte passive Fähigkeiten für Display haben"
                
                # Prüfe Datentypen
                assert isinstance(info["name"], str), "Talent-Name sollte String sein"
                assert isinstance(info["description"], str), "Talent-Beschreibung sollte String sein"
                assert isinstance(info["category"], str), "Talent-Kategorie sollte String sein"
                assert isinstance(info["current_tier"], (int, type(None))), "Talent-Tier sollte Integer oder None sein"
                assert isinstance(info["max_tier"], int), "Maximales Talent-Tier sollte Integer sein"
                assert isinstance(info["can_learn"], bool), "Lern-Status sollte Boolean sein"
                assert isinstance(info["can_upgrade"], bool), "Upgrade-Status sollte Boolean sein"
                assert isinstance(info["moves"], list), "Moves sollten Liste sein"
                assert isinstance(info["passive_abilities"], list), "Passive Fähigkeiten sollten Liste sein"
            
            logger.info(f"✅ Talent Display Data: {len(talent_infos)} talent infos generated")
            return True
            
        except Exception as e:
            logger.error(f"❌ Talent Display Data failed: {e}")
            return False
    
    def test_move_display_data(self) -> bool:
        """Test move display data generation."""
        logger.info("🧪 Testing Move Display Data...")
        
        try:
            monster = self.create_ui_test_monster("Move-UI-Monster", ["Feuer"], 15)
            
            # Hole verfügbare Moves
            moves = monster.get_available_moves()
            
            # Prüfe ob Moves vorhanden sind
            assert len(moves) > 0, "Monster sollte Moves für UI haben"
            
            # Prüfe Move-Display-Daten
            for move in moves:
                # Prüfe erforderliche Display-Felder
                assert hasattr(move, 'name'), "Move sollte Name für UI haben"
                assert hasattr(move, 'type'), "Move sollte Type für UI haben"
                assert hasattr(move, 'power'), "Move sollte Power für UI haben"
                assert hasattr(move, 'accuracy'), "Move sollte Accuracy für UI haben"
                assert hasattr(move, 'description'), "Move sollte Beschreibung für UI haben"
                
                # Prüfe Datentypen
                assert isinstance(move.name, str), "Move-Name sollte String sein"
                assert isinstance(move.type, str), "Move-Type sollte String sein"
                assert isinstance(move.power, (int, float)), "Move-Power sollte numerisch sein"
                assert isinstance(move.accuracy, (int, float)), "Move-Accuracy sollte numerisch sein"
                assert isinstance(move.description, str), "Move-Beschreibung sollte String sein"
                
                # Prüfe Werte-Bereiche
                assert 0 <= move.power <= 200, "Move-Power sollte im gültigen Bereich sein"
                assert 0 <= move.accuracy <= 100, "Move-Accuracy sollte im gültigen Bereich sein"
            
            logger.info(f"✅ Move Display Data: {len(moves)} moves ready for UI")
            return True
            
        except Exception as e:
            logger.error(f"❌ Move Display Data failed: {e}")
            return False
    
    def test_passive_abilities_display(self) -> bool:
        """Test passive abilities display data."""
        logger.info("🧪 Testing Passive Abilities Display...")
        
        try:
            monster = self.create_ui_test_monster("Passive-UI-Monster", ["Feuer"], 15)
            
            # Hole passive Fähigkeiten
            passives = monster.get_passive_abilities()
            
            # Prüfe ob passive Fähigkeiten vorhanden sind
            assert len(passives) > 0, "Monster sollte passive Fähigkeiten für UI haben"
            
            # Prüfe passive Fähigkeiten-Display-Daten
            for passive in passives:
                # Prüfe erforderliche Display-Felder
                assert "name" in passive, "Passive Fähigkeit sollte Name für UI haben"
                assert "description" in passive, "Passive Fähigkeit sollte Beschreibung für UI haben"
                assert "effect_type" in passive, "Passive Fähigkeit sollte Effect-Type für UI haben"
                assert "value" in passive, "Passive Fähigkeit sollte Wert für UI haben"
                assert "talent_id" in passive, "Passive Fähigkeit sollte Talent-ID für UI haben"
                
                # Prüfe Datentypen
                assert isinstance(passive["name"], str), "Passive Fähigkeit-Name sollte String sein"
                assert isinstance(passive["description"], str), "Passive Fähigkeit-Beschreibung sollte String sein"
                assert isinstance(passive["effect_type"], str), "Passive Fähigkeit-Effect-Type sollte String sein"
                assert isinstance(passive["value"], (int, float)), "Passive Fähigkeit-Wert sollte numerisch sein"
                assert isinstance(passive["talent_id"], str), "Passive Fähigkeit-Talent-ID sollte String sein"
                
                # Prüfe Werte-Bereiche
                assert 0 <= passive["value"] <= 10, "Passive Fähigkeit-Wert sollte im gültigen Bereich sein"
            
            logger.info(f"✅ Passive Abilities Display: {len(passives)} abilities ready for UI")
            return True
            
        except Exception as e:
            logger.error(f"❌ Passive Abilities Display failed: {e}")
            return False
    
    def test_talent_learning_ui_data(self) -> bool:
        """Test talent learning UI data generation."""
        logger.info("🧪 Testing Talent Learning UI Data...")
        
        try:
            monster = self.create_ui_test_monster("Learning-UI-Monster", ["Feuer"], 15)
            
            # Hole lernbare Talents
            learnable = monster.get_learnable_talents()
            
            # Prüfe ob lernbare Talents vorhanden sind
            assert len(learnable) > 0, "Monster sollte lernbare Talents für UI haben"
            
            # Teste Talent-Learning-UI-Daten für jedes lernbare Talent
            for talent_id in learnable:
                info = monster.get_talent_info(talent_id)
                
                if info:
                    # Prüfe Learning-UI-spezifische Felder
                    assert "can_learn" in info, "Talent-Info sollte can_learn für UI haben"
                    assert "learned" in info, "Talent-Info sollte learned-Status für UI haben"
                    assert "current_tier" in info, "Talent-Info sollte current_tier für UI haben"
                    assert "max_tier" in info, "Talent-Info sollte max_tier für UI haben"
                    
                    # Prüfe Learning-Status
                    assert isinstance(info["can_learn"], bool), "can_learn sollte Boolean sein"
                    assert isinstance(info["learned"], bool), "learned sollte Boolean sein"
                    assert isinstance(info["current_tier"], (int, type(None))), "current_tier sollte Integer oder None sein"
                    assert isinstance(info["max_tier"], int), "max_tier sollte Integer sein"
                    
                    # Prüfe Konsistenz
                    if info["learned"]:
                        assert info["current_tier"] is not None, "Gelernte Talents sollten current_tier haben"
                        assert info["current_tier"] > 0, "current_tier sollte positiv sein"
                    else:
                        assert info["current_tier"] is None, "Nicht gelernte Talents sollten current_tier None haben"
            
            logger.info(f"✅ Talent Learning UI Data: {len(learnable)} learnable talents ready for UI")
            return True
            
        except Exception as e:
            logger.error(f"❌ Talent Learning UI Data failed: {e}")
            return False
    
    def test_talent_upgrade_ui_data(self) -> bool:
        """Test talent upgrade UI data generation."""
        logger.info("🧪 Testing Talent Upgrade UI Data...")
        
        try:
            monster = self.create_ui_test_monster("Upgrade-UI-Monster", ["Feuer"], 20)
            
            # Lerne ein Talent
            learnable = monster.get_learnable_talents()
            if learnable:
                talent_id = learnable[0]
                monster.learn_talent(talent_id)
                
                # Hole Talent-Info nach dem Lernen
                info = monster.get_talent_info(talent_id)
                
                if info:
                    # Prüfe Upgrade-UI-spezifische Felder
                    assert "can_upgrade" in info, "Talent-Info sollte can_upgrade für UI haben"
                    assert "current_tier" in info, "Talent-Info sollte current_tier für UI haben"
                    assert "max_tier" in info, "Talent-Info sollte max_tier für UI haben"
                    
                    # Prüfe Upgrade-Status
                    assert isinstance(info["can_upgrade"], bool), "can_upgrade sollte Boolean sein"
                    assert isinstance(info["current_tier"], int), "current_tier sollte Integer sein"
                    assert isinstance(info["max_tier"], int), "max_tier sollte Integer sein"
                    
                    # Prüfe Tier-Konsistenz
                    assert info["current_tier"] <= info["max_tier"], "current_tier sollte <= max_tier sein"
                    assert info["current_tier"] > 0, "current_tier sollte positiv sein"
                    assert info["max_tier"] > 0, "max_tier sollte positiv sein"
                    
                    # Teste Upgrade-Möglichkeit
                    if info["can_upgrade"]:
                        # Simuliere Upgrade
                        upgrade_success = monster.upgrade_talent(talent_id)
                        
                        if upgrade_success:
                            # Hole aktualisierte Info
                            updated_info = monster.get_talent_info(talent_id)
                            
                            if updated_info:
                                # Prüfe ob Tier erhöht wurde
                                assert updated_info["current_tier"] > info["current_tier"], "Tier sollte nach Upgrade erhöht worden sein"
            
            logger.info("✅ Talent Upgrade UI Data: Upgrade UI data generation successful")
            return True
            
        except Exception as e:
            logger.error(f"❌ Talent Upgrade UI Data failed: {e}")
            return False
    
    def test_ui_data_consistency(self) -> bool:
        """Test UI data consistency across different monster types."""
        logger.info("🧪 Testing UI Data Consistency...")
        
        try:
            # Teste verschiedene Monster-Types
            monster_types = [
                (["Feuer"], "Feuer-Monster"),
                (["Wasser"], "Wasser-Monster"),
                (["Erde"], "Erd-Monster"),
                (["Luft"], "Luft-Monster"),
                (["Pflanze"], "Pflanzen-Monster")
            ]
            
            ui_data_consistency = True
            
            for types, name in monster_types:
                monster = self.create_ui_test_monster(name, types, 15)
                
                # Teste Talent-Display-Daten
                talent_infos = []
                for talent_instance in monster.talents:
                    info = monster.get_talent_info(talent_instance.talent_id)
                    if info:
                        talent_infos.append(info)
                
                # Prüfe ob alle Talent-Infos konsistente Struktur haben
                for info in talent_infos:
                    required_fields = ["name", "description", "category", "can_learn", "can_upgrade", "moves", "passive_abilities"]
                    for field in required_fields:
                        if field not in info:
                            logger.error(f"Missing field {field} in talent info for {name}")
                            ui_data_consistency = False
                
                # Teste Move-Display-Daten
                moves = monster.get_available_moves()
                for move in moves:
                    required_attrs = ["name", "type", "power", "accuracy", "description"]
                    for attr in required_attrs:
                        if not hasattr(move, attr):
                            logger.error(f"Missing attribute {attr} in move for {name}")
                            ui_data_consistency = False
                
                # Teste Passive-Fähigkeiten-Display-Daten
                passives = monster.get_passive_abilities()
                for passive in passives:
                    required_fields = ["name", "description", "effect_type", "value", "talent_id"]
                    for field in required_fields:
                        if field not in passive:
                            logger.error(f"Missing field {field} in passive ability for {name}")
                            ui_data_consistency = False
            
            assert ui_data_consistency, "UI data should be consistent across monster types"
            
            logger.info("✅ UI Data Consistency: All monster types have consistent UI data")
            return True
            
        except Exception as e:
            logger.error(f"❌ UI Data Consistency failed: {e}")
            return False
    
    def run_all_tests(self) -> bool:
        """Run all talent UI integration tests."""
        logger.info("🚀 Starting Talent UI Integration Tests")
        logger.info("=" * 60)
        
        tests = [
            ("Talent Display Data", self.test_talent_display_data),
            ("Move Display Data", self.test_move_display_data),
            ("Passive Abilities Display", self.test_passive_abilities_display),
            ("Talent Learning UI Data", self.test_talent_learning_ui_data),
            ("Talent Upgrade UI Data", self.test_talent_upgrade_ui_data),
            ("UI Data Consistency", self.test_ui_data_consistency)
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
        logger.info("📊 UI INTEGRATION TEST RESULTS")
        logger.info("=" * 60)
        
        for test_name, result in self.test_results:
            status = "✅ PASS" if result else "❌ FAIL"
            logger.info(f"{status} {test_name}")
        
        logger.info(f"\n🎯 Overall: {passed}/{total} tests passed")
        
        return passed == total

def main():
    """Main test function."""
    tester = TalentUITester()
    success = tester.run_all_tests()
    
    if success:
        logger.info("\n🎉 ALL TALENT UI INTEGRATION TESTS PASSED!")
        return 0
    else:
        logger.error("\n💥 SOME TALENT UI INTEGRATION TESTS FAILED!")
        return 1

if __name__ == "__main__":
    exit(main())
