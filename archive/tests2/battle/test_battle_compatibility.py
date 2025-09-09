"""
Tests für Battle System Rückwärtskompatibilität
==============================================

Testet, dass alle alten Battle-Aufrufe noch funktionieren,
aber DeprecationWarnings ausgeben.
"""

import unittest
import warnings
import sys
import os
from unittest.mock import Mock, patch
from typing import List

# Füge den übergeordneten Verzeichnis zum Python-Pfad hinzu
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

# Import der Legacy-Implementierung
from .refactored_battle import (
    BattleState,
    BattleType,
    BattlePhase,
    get_battle_state_legacy,
    create_battle_legacy,
    validate_battle_state_legacy,
    show_migration_help
)

# Import der neuen Systeme
from .battle_system import (
    BattleType as NewBattleType,
    BattlePhase as NewBattlePhase
)

# Import der Controller-Implementierung
from .battle_controller import BattleState as ControllerBattleState

# Mock MonsterInstance für Tests
class MockMonsterInstance:
    def __init__(self, name: str, hp: int = 100):
        self.name = name
        self.current_hp = hp
        self.max_hp = hp
        self.is_fainted = hp <= 0
    
    def __str__(self):
        return f"MockMonster({self.name})"


class TestBattleCompatibility(unittest.TestCase):
    """Testet die Rückwärtskompatibilität des refactorierten Battle-Systems."""
    
    def setUp(self):
        """Setup für jeden Test."""
        # Erstelle Mock-Monster für Tests
        self.player_monster = MockMonsterInstance("SpielerMonster", 100)
        self.enemy_monster = MockMonsterInstance("GegnerMonster", 100)
        self.player_team = [self.player_monster]
        self.enemy_team = [self.enemy_monster]
        
        # Capture DeprecationWarnings
        self.warning_catcher = warnings.catch_warnings(record=True)
        self.warnings = []
    
    def tearDown(self):
        """Cleanup nach jedem Test."""
        pass
    
    def capture_warnings(self):
        """Capture alle Warnungen während der Ausführung."""
        self.warnings = []
        with self.warning_catcher as w:
            yield w
        self.warnings = w
    
    def test_legacy_battle_type_enum(self):
        """Testet, dass Legacy BattleType Enum funktioniert."""
        with self.capture_warnings():
            # Teste alle Enum-Werte
            self.assertEqual(BattleType.WILD.value, "wild")
            self.assertEqual(BattleType.TRAINER.value, "trainer")
            self.assertEqual(BattleType.GYM.value, "gym")
            
            # Prüfe, dass Warnungen ausgegeben werden
            self.assertTrue(any("deprecated" in str(w.message) for w in self.warnings))
            self.assertTrue(any("battle_enums.BattleType" in str(w.message) for w in self.warnings))
    
    def test_legacy_battle_phase_enum(self):
        """Testet, dass Legacy BattlePhase Enum funktioniert."""
        with self.capture_warnings():
            # Teste alle Enum-Werte
            self.assertEqual(BattlePhase.INIT.value, "init")
            self.assertEqual(BattlePhase.START.value, "start")
            self.assertEqual(BattlePhase.INPUT.value, "input")
            
            # Prüfe, dass Warnungen ausgegeben werden
            self.assertTrue(any("deprecated" in str(w.message) for w in self.warnings))
            self.assertTrue(any("battle_enums.BattlePhase" in str(w.message) for w in self.warnings))
    
    def test_legacy_battle_state_creation(self):
        """Testet, dass Legacy BattleState erstellt werden kann."""
        with self.capture_warnings():
            # Erstelle Legacy BattleState
            battle = BattleState(
                player_team=self.player_team,
                enemy_team=self.enemy_team,
                battle_type=BattleType.WILD
            )
            
            # Prüfe, dass es sich um eine Instanz der neuen Implementierung handelt
            self.assertIsInstance(battle, ControllerBattleState)
            self.assertIsInstance(battle, NewBattleState)
            
            # Prüfe, dass Warnungen ausgegeben werden
            self.assertTrue(any("deprecated" in str(w.message) for w in self.warnings))
            self.assertTrue(any("battle_controller.BattleState" in str(w.message) for w in self.warnings))
    
    def test_legacy_battle_state_properties(self):
        """Testet, dass Legacy BattleState alle erwarteten Eigenschaften hat."""
        with self.capture_warnings():
            battle = BattleState(
                player_team=self.player_team,
                enemy_team=self.enemy_team,
                battle_type=BattleType.WILD
            )
            
            # Prüfe grundlegende Eigenschaften
            self.assertEqual(battle.battle_type.value, "wild")
            self.assertEqual(len(battle.player_team), 1)
            self.assertEqual(len(battle.enemy_team), 1)
            self.assertTrue(battle.can_flee)
            self.assertTrue(battle.can_catch)
    
    def test_legacy_battle_state_methods(self):
        """Testet, dass Legacy BattleState alle erwarteten Methoden hat."""
        with self.capture_warnings():
            battle = BattleState(
                player_team=self.player_team,
                enemy_team=self.enemy_team,
                battle_type=BattleType.TRAINER
            )
            
            # Prüfe, dass wichtige Methoden existieren
            self.assertTrue(hasattr(battle, 'validate_battle_state'))
            
            # Prüfe, dass Methoden aufrufbar sind
            self.assertTrue(callable(battle.validate_battle_state))
    
    def test_legacy_helper_functions(self):
        """Testet, dass alle Legacy-Helper-Funktionen funktionieren."""
        with self.capture_warnings():
            # Teste get_battle_state_legacy
            battle1 = get_battle_state_legacy(
                player_team=self.player_team,
                enemy_team=self.enemy_team
            )
            self.assertIsInstance(battle1, ControllerBattleState)
            
            # Teste create_battle_legacy
            battle2 = create_battle_legacy(
                player_team=self.player_team,
                enemy_team=self.enemy_team
            )
            self.assertIsInstance(battle2, ControllerBattleState)
            
            # Teste validate_battle_state_legacy
            is_valid = validate_battle_state_legacy(battle1)
            self.assertTrue(is_valid)
            
            # Prüfe, dass alle Funktionen Warnungen ausgeben
            self.assertTrue(any("deprecated" in str(w.message) for w in self.warnings))
    
    def test_enum_compatibility(self):
        """Testet, dass Legacy-Enums mit neuen Enums kompatibel sind."""
        with self.capture_warnings():
            # Teste Vergleich zwischen Legacy und neuen Enums
            legacy_type = BattleType.WILD
            new_type = NewBattleType.WILD
            
            # Werte sollten gleich sein
            self.assertEqual(legacy_type.value, new_type.value)
            
            # Legacy-Enum sollte als neues Enum verwendbar sein
            battle = BattleState(
                player_team=self.player_team,
                enemy_team=self.enemy_team,
                battle_type=legacy_type
            )
            
            # Battle sollte den korrekten Typ haben
            self.assertEqual(battle.battle_type.value, "wild")
    
    def test_battle_type_conversion(self):
        """Testet, dass Legacy BattleType korrekt zu neuen BattleType konvertiert wird."""
        with self.capture_warnings():
            # Erstelle Battle mit Legacy BattleType
            battle = BattleState(
                player_team=self.player_team,
                enemy_team=self.enemy_team,
                battle_type=BattleType.GYM
            )
            
            # Battle sollte den korrekten neuen BattleType haben
            self.assertEqual(battle.battle_type.value, "gym")
            self.assertIsInstance(battle.battle_type, NewBattleType)
    
    def test_migration_help_function(self):
        """Testet, dass die Migrationshilfe-Funktion funktioniert."""
        # Capture stdout für den Test
        from io import StringIO
        import sys
        
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        
        try:
            show_migration_help()
            output = sys.stdout.getvalue()
            
            # Prüfe, dass wichtige Informationen in der Ausgabe stehen
            self.assertIn("MIGRATION HILFE", output)
            self.assertIn("deprecated", output)
            self.assertIn("battle_controller", output)
            self.assertIn("battle_enums", output)
            self.assertIn("Ruhrpott", output)  # Prüfe auf lokale Dialekt-Referenzen
        finally:
            sys.stdout = old_stdout
    
    def test_import_warning(self):
        """Testet, dass beim Import der Legacy-Datei eine Warnung ausgegeben wird."""
        with self.capture_warnings():
            # Import der Legacy-Datei sollte eine Warnung ausgeben
            import refactored_battle
            
            # Prüfe, dass eine Import-Warnung ausgegeben wurde
            self.assertTrue(any("deprecated" in str(w.message) for w in self.warnings))
            self.assertTrue(any("Migriere zu" in str(w.message) for w in self.warnings))
    
    def test_all_attributes_available(self):
        """Testet, dass alle erwarteten Attribute verfügbar sind."""
        with self.capture_warnings():
            # Prüfe, dass alle wichtigen Attribute verfügbar sind
            self.assertTrue(hasattr(BattleState, '__init__'))
            self.assertTrue(hasattr(BattleType, 'WILD'))
            self.assertTrue(hasattr(BattlePhase, 'INIT'))
            
            # Prüfe, dass alle Legacy-Funktionen verfügbar sind
            self.assertTrue(callable(get_battle_state_legacy))
            self.assertTrue(callable(create_battle_legacy))
            self.assertTrue(callable(validate_battle_state_legacy))
    
    def test_ruhrpott_dialect_in_comments(self):
        """Testet, dass Ruhrpott-Dialekt in Kommentaren verwendet wird."""
        # Lese die Datei und prüfe auf lokale Dialekt-Referenzen
        with open('refactored_battle.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Prüfe auf typische Ruhrpott-Ausdrücke
        self.assertIn("Ey, hier gehts ab", content)
        self.assertIn("dat kannste knicken", content)
    
    def test_comprehensive_compatibility(self):
        """Umfassender Test der Kompatibilität."""
        with self.capture_warnings():
            # Teste alle Battle-Typen
            for battle_type in [BattleType.WILD, BattleType.TRAINER, BattleType.GYM]:
                battle = BattleState(
                    player_team=self.player_team,
                    enemy_team=self.enemy_team,
                    battle_type=battle_type
                )
                
                # Prüfe, dass Battle korrekt erstellt wurde
                self.assertIsInstance(battle, ControllerBattleState)
                self.assertEqual(battle.battle_type.value, battle_type.value)
            
            # Prüfe, dass alle Warnungen ausgegeben wurden
            self.assertTrue(len(self.warnings) > 0)
            self.assertTrue(all("deprecated" in str(w.message) for w in self.warnings))


if __name__ == '__main__':
    # Konfiguriere Test-Suite
    unittest.main(verbosity=2)
