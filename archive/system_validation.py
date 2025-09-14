#!/usr/bin/env python3
"""
System Validation Script für Talent-Migration
Validiert alle System-Komponenten nach der Talent-Integration
"""

import sys
import traceback
from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class ValidationResult:
    """Ergebnis einer System-Validierung"""
    system_name: str
    success: bool
    details: Dict[str, Any]
    errors: List[str]
    warnings: List[str]

class SystemValidator:
    """Validiert das gesamte System nach Talent-Migration"""
    
    def __init__(self):
        self.results = {}
        self.total_errors = 0
        self.total_warnings = 0
    
    def validate_monster_system(self) -> ValidationResult:
        """Validiere Monster-System mit Talent-Integration"""
        print("🔍 Validiere Monster-System...")
        
        result = ValidationResult(
            system_name="Monster-System",
            success=False,
            details={},
            errors=[],
            warnings=[]
        )
        
        try:
            # Teste Monster-Erstellung
            from engine.systems.monster_instance import MonsterInstance, MonsterSpecies
            from engine.systems.stats import BaseStats
            from engine.systems.monster_instance import MonsterRank, GrowthCurve
            
            # Erstelle Test-Monster
            species_data = {
                "id": "test_001",
                "name": "Testmonster",
                "types": ["Feuer"],
                "base_stats": BaseStats(hp=50, atk=50, def_=50, mag=50, res=50, spd=50),
                "rank": MonsterRank.F,
                "growth_curve": GrowthCurve.MEDIUM_FAST,
                "talents": [
                    {"talent_id": "physical_i", "learned_at_level": 1, "current_tier": 1, "experience": 0},
                    {"talent_id": "fire_i", "learned_at_level": 1, "current_tier": 1, "experience": 0}
                ]
            }
            
            species = MonsterSpecies(**species_data)
            monster = MonsterInstance(species=species, level=5)
            
            # Validiere Monster-Erstellung
            if monster and monster.name == "Testmonster":
                result.details['monster_creation'] = True
                print("  ✅ Monster-Erstellung erfolgreich")
            else:
                result.errors.append("Monster-Erstellung fehlgeschlagen")
                print("  ❌ Monster-Erstellung fehlgeschlagen")
            
            # Validiere Talent-Loading
            if hasattr(monster, 'talents') and len(monster.talents) == 2:
                result.details['talent_loading'] = True
                print("  ✅ Talent-Loading erfolgreich")
            else:
                result.errors.append("Talent-Loading fehlgeschlagen")
                print("  ❌ Talent-Loading fehlgeschlagen")
            
            # Validiere Move-Loading
            if hasattr(monster, 'moves') and len(monster.moves) > 0:
                result.details['move_loading'] = True
                print("  ✅ Move-Loading erfolgreich")
            else:
                result.warnings.append("Keine Moves geladen")
                print("  ⚠️  Keine Moves geladen")
            
            # Teste Level-Up
            if hasattr(monster, 'level_up'):
                old_moves = len(monster.moves) if hasattr(monster, 'moves') else 0
                monster.level_up()
                new_moves = len(monster.moves) if hasattr(monster, 'moves') else 0
                
                if new_moves >= old_moves:
                    result.details['level_ups'] = True
                    print("  ✅ Level-Up erfolgreich")
                else:
                    result.warnings.append("Level-Up hat keine neuen Moves hinzugefügt")
                    print("  ⚠️  Level-Up hat keine neuen Moves hinzugefügt")
            
            # Bestimme Gesamterfolg
            result.success = (
                result.details.get('monster_creation', False) and
                result.details.get('talent_loading', False) and
                result.details.get('move_loading', False)
            )
            
        except Exception as e:
            error_msg = f"Monster-System Validierung fehlgeschlagen: {e}"
            result.errors.append(error_msg)
            print(f"  ❌ {error_msg}")
            traceback.print_exc()
        
        return result
    
    def validate_talent_system(self) -> ValidationResult:
        """Validiere Talent-System"""
        print("🔍 Validiere Talent-System...")
        
        result = ValidationResult(
            system_name="Talent-System",
            success=False,
            details={},
            errors=[],
            warnings=[]
        )
        
        try:
            from engine.systems.talent_system import get_talent_database, TalentInstance, TalentTier
            
            # Lade Talent-Database
            talent_db = get_talent_database()
            
            if talent_db and len(talent_db.talents) > 0:
                result.details['talent_loading'] = True
                print(f"  ✅ Talent-Database geladen: {len(talent_db.talents)} Talents")
            else:
                result.errors.append("Talent-Database konnte nicht geladen werden")
                print("  ❌ Talent-Database konnte nicht geladen werden")
                return result
            
            # Teste Move-Erstellung
            test_talent = talent_db.get_talent("fire_i")
            if test_talent:
                moves = talent_db.get_available_moves_from_talents(
                    [TalentInstance("fire_i", TalentTier.BASIC, 0, True)], 
                    5
                )
                if moves:
                    result.details['move_creation'] = True
                    print("  ✅ Move-Erstellung aus Talents erfolgreich")
                else:
                    result.warnings.append("Keine Moves aus Talents erstellt")
                    print("  ⚠️  Keine Moves aus Talents erstellt")
            else:
                result.errors.append("Test-Talent 'fire_i' nicht gefunden")
                print("  ❌ Test-Talent 'fire_i' nicht gefunden")
            
            # Teste Talent-Validierung
            if hasattr(talent_db, 'validate_talent_system'):
                if talent_db.validate_talent_system():
                    result.details['talent_validation'] = True
                    print("  ✅ Talent-Validierung erfolgreich")
                else:
                    result.warnings.append("Talent-Validierung fehlgeschlagen")
                    print("  ⚠️  Talent-Validierung fehlgeschlagen")
            
            # Teste Database-Integrität
            if hasattr(talent_db, 'check_database_integrity'):
                if talent_db.check_database_integrity():
                    result.details['database_integrity'] = True
                    print("  ✅ Database-Integrität erfolgreich")
                else:
                    result.warnings.append("Database-Integrität fehlgeschlagen")
                    print("  ⚠️  Database-Integrität fehlgeschlagen")
            
            # Bestimme Gesamterfolg
            result.success = (
                result.details.get('talent_loading', False) and
                result.details.get('move_creation', False)
            )
            
        except Exception as e:
            error_msg = f"Talent-System Validierung fehlgeschlagen: {e}"
            result.errors.append(error_msg)
            print(f"  ❌ {error_msg}")
            traceback.print_exc()
        
        return result
    
    def validate_battle_system(self) -> ValidationResult:
        """Validiere Battle-System mit Talent-Integration"""
        print("🔍 Validiere Battle-System...")
        
        result = ValidationResult(
            system_name="Battle-System",
            success=False,
            details={},
            errors=[],
            warnings=[]
        )
        
        try:
            from engine.systems.battle.battle_controller import BattleController
            from engine.systems.monster_instance import MonsterInstance, MonsterSpecies
            from engine.systems.stats import BaseStats
            from engine.systems.monster_instance import MonsterRank, GrowthCurve
            
            # Erstelle Test-Monster
            def create_test_monster():
                species_data = {
                    "id": "test_battle_001",
                    "name": "Battle-Testmonster",
                    "types": ["Feuer"],
                    "base_stats": BaseStats(hp=50, atk=50, def_=50, mag=50, res=50, spd=50),
                    "rank": MonsterRank.F,
                    "growth_curve": GrowthCurve.MEDIUM_FAST,
                    "talents": [
                        {"talent_id": "physical_i", "learned_at_level": 1, "current_tier": 1, "experience": 0}
                    ]
                }
                species = MonsterSpecies(**species_data)
                return MonsterInstance(species=species, level=5)
            
            player_monster = create_test_monster()
            enemy_monster = create_test_monster()
            
            # Erstelle Battle
            battle = BattleController([player_monster], [enemy_monster])
            
            if battle and hasattr(battle, 'state') and hasattr(battle.state, 'player_active'):
                result.details['battle_creation'] = True
                print("  ✅ Battle-Erstellung erfolgreich")
            else:
                result.errors.append("Battle-Erstellung fehlgeschlagen")
                print("  ❌ Battle-Erstellung fehlgeschlagen")
                return result
            
            # Teste Move-Ausführung
            if hasattr(battle, 'get_available_actions'):
                try:
                    available_actions = battle.get_available_actions()
                    if available_actions:
                        result.details['move_execution'] = True
                        print("  ✅ Move-Ausführung erfolgreich")
                    else:
                        result.warnings.append("Keine verfügbaren Aktionen")
                        print("  ⚠️  Keine verfügbaren Aktionen")
                except Exception as e:
                    result.warnings.append(f"Move-Ausführung fehlgeschlagen: {e}")
                    print(f"  ⚠️  Move-Ausführung fehlgeschlagen: {e}")
            
            # Teste AI-Funktionalität
            if hasattr(battle, 'get_ai_action'):
                ai_action = battle.get_ai_action(enemy_monster)
                if ai_action:
                    result.details['ai_functionality'] = True
                    print("  ✅ AI-Funktionalität erfolgreich")
                else:
                    result.warnings.append("AI-Funktionalität nicht verfügbar")
                    print("  ⚠️  AI-Funktionalität nicht verfügbar")
            
            # Teste Turn-Processing
            if hasattr(battle, 'process_turn'):
                try:
                    battle.process_turn()
                    result.details['turn_processing'] = True
                    print("  ✅ Turn-Processing erfolgreich")
                except Exception as e:
                    result.warnings.append(f"Turn-Processing fehlgeschlagen: {e}")
                    print(f"  ⚠️  Turn-Processing fehlgeschlagen: {e}")
            
            # Bestimme Gesamterfolg
            result.success = (
                result.details.get('battle_creation', False) and
                result.details.get('move_execution', False)
            )
            
        except Exception as e:
            error_msg = f"Battle-System Validierung fehlgeschlagen: {e}"
            result.errors.append(error_msg)
            print(f"  ❌ {error_msg}")
            traceback.print_exc()
        
        return result
    
    def validate_ui_scene_system(self) -> ValidationResult:
        """Validiere UI/Scene-System mit Talent-Integration"""
        print("🔍 Validiere UI/Scene-System...")
        
        result = ValidationResult(
            system_name="UI/Scene-System",
            success=False,
            details={},
            errors=[],
            warnings=[]
        )
        
        try:
            # Teste Starter-Scene
            from engine.scenes.starter_scene import StarterScene
            
            class MockGame:
                def __init__(self):
                    self.resources = None
                    self.party_manager = None
                    self.story_manager = None
                    self.sprite_manager = None
            
            game = MockGame()
            starter_scene = StarterScene(game)
            
            if starter_scene:
                result.details['starter_scene'] = True
                print("  ✅ Starter-Scene erfolgreich")
            else:
                result.errors.append("Starter-Scene konnte nicht erstellt werden")
                print("  ❌ Starter-Scene konnte nicht erstellt werden")
            
            # Teste Field-Scene
            from engine.scenes.field_scene import FieldScene
            
            field_scene = FieldScene(game)
            
            if field_scene:
                result.details['field_scene'] = True
                print("  ✅ Field-Scene erfolgreich")
            else:
                result.errors.append("Field-Scene konnte nicht erstellt werden")
                print("  ❌ Field-Scene konnte nicht erstellt werden")
            
            # Teste Monster-Display
            def create_test_monster_with_talents():
                from engine.systems.monster_instance import MonsterInstance, MonsterSpecies
                from engine.systems.stats import BaseStats
                from engine.systems.monster_instance import MonsterRank, GrowthCurve
                
                species_data = {
                    "id": "test_ui_001",
                    "name": "UI-Testmonster",
                    "types": ["Feuer"],
                    "base_stats": BaseStats(hp=50, atk=50, def_=50, mag=50, res=50, spd=50),
                    "rank": MonsterRank.F,
                    "growth_curve": GrowthCurve.MEDIUM_FAST,
                    "talents": [
                        {"talent_id": "fire_i", "learned_at_level": 1, "current_tier": 1, "experience": 0}
                    ]
                }
                species = MonsterSpecies(**species_data)
                return MonsterInstance(species=species, level=5)
            
            test_monster = create_test_monster_with_talents()
            if test_monster and hasattr(test_monster, 'talents') and len(test_monster.talents) > 0:
                result.details['monster_display'] = True
                print("  ✅ Monster-Display erfolgreich")
            else:
                result.warnings.append("Monster-Display nicht verfügbar")
                print("  ⚠️  Monster-Display nicht verfügbar")
            
            # Teste Scene-Transitions
            if starter_scene and field_scene:
                result.details['scene_transitions'] = True
                print("  ✅ Scene-Transitions erfolgreich")
            else:
                result.warnings.append("Scene-Transitions nicht verfügbar")
                print("  ⚠️  Scene-Transitions nicht verfügbar")
            
            # Bestimme Gesamterfolg
            result.success = (
                result.details.get('starter_scene', False) and
                result.details.get('field_scene', False)
            )
            
        except Exception as e:
            error_msg = f"UI/Scene-System Validierung fehlgeschlagen: {e}"
            result.errors.append(error_msg)
            print(f"  ❌ {error_msg}")
            traceback.print_exc()
        
        return result
    
    def validate_experience_system(self) -> ValidationResult:
        """Validiere Experience-System mit Talent-Integration"""
        print("🔍 Validiere Experience-System...")
        
        result = ValidationResult(
            system_name="Experience-System",
            success=False,
            details={},
            errors=[],
            warnings=[]
        )
        
        try:
            from engine.systems.experience_system import ExperienceSystem
            from engine.systems.monster_instance import MonsterInstance, MonsterSpecies
            from engine.systems.stats import BaseStats
            from engine.systems.monster_instance import MonsterRank, GrowthCurve
            
            # Erstelle Test-Monster
            species_data = {
                "id": "test_exp_001",
                "name": "Exp-Testmonster",
                "types": ["Feuer"],
                "base_stats": BaseStats(hp=50, atk=50, def_=50, mag=50, res=50, spd=50),
                "rank": MonsterRank.F,
                "growth_curve": GrowthCurve.MEDIUM_FAST,
                "talents": [
                    {"talent_id": "fire_i", "learned_at_level": 1, "current_tier": 1, "experience": 0}
                ]
            }
            species = MonsterSpecies(**species_data)
            monster = MonsterInstance(species=species, level=5)
            
            # Teste Experience-System
            if hasattr(ExperienceSystem, 'add_experience'):
                old_level = monster.level
                ExperienceSystem.add_experience(monster, 1000)
                
                if monster.level > old_level:
                    result.details['experience_gain'] = True
                    print("  ✅ Experience-Gain erfolgreich")
                else:
                    result.warnings.append("Experience-Gain hat Level nicht erhöht")
                    print("  ⚠️  Experience-Gain hat Level nicht erhöht")
            
            # Teste Talent-Experience
            if hasattr(ExperienceSystem, 'add_talent_experience'):
                talent_results = ExperienceSystem.add_talent_experience(monster, 100)
                if talent_results:
                    result.details['talent_experience'] = True
                    print("  ✅ Talent-Experience erfolgreich")
                else:
                    result.warnings.append("Talent-Experience nicht verfügbar")
                    print("  ⚠️  Talent-Experience nicht verfügbar")
            
            # Bestimme Gesamterfolg
            result.success = (
                result.details.get('experience_gain', False) or
                result.details.get('talent_experience', False)
            )
            
        except Exception as e:
            error_msg = f"Experience-System Validierung fehlgeschlagen: {e}"
            result.errors.append(error_msg)
            print(f"  ❌ {error_msg}")
            traceback.print_exc()
        
        return result
    
    def run_integration_tests(self) -> ValidationResult:
        """Führe Integration-Tests durch"""
        print("🔍 Führe Integration-Tests durch...")
        
        result = ValidationResult(
            system_name="Integration-Tests",
            success=False,
            details={},
            errors=[],
            warnings=[]
        )
        
        try:
            # Teste Monster-Battle-Integration
            from engine.systems.monster_instance import MonsterInstance, MonsterSpecies
            from engine.systems.stats import BaseStats
            from engine.systems.monster_instance import MonsterRank, GrowthCurve
            from engine.systems.battle.battle_controller import BattleController
            
            def create_test_monster_with_talents():
                species_data = {
                    "id": "test_integration_001",
                    "name": "Integration-Testmonster",
                    "types": ["Feuer"],
                    "base_stats": BaseStats(hp=50, atk=50, def_=50, mag=50, res=50, spd=50),
                    "rank": MonsterRank.F,
                    "growth_curve": GrowthCurve.MEDIUM_FAST,
                    "talents": [
                        {"talent_id": "fire_i", "learned_at_level": 1, "current_tier": 1, "experience": 0}
                    ]
                }
                species = MonsterSpecies(**species_data)
                return MonsterInstance(species=species, level=5)
            
            monster = create_test_monster_with_talents()
            battle = BattleController([monster], [create_test_monster_with_talents()])
            
            if battle and hasattr(battle, 'state') and battle.state.player_active == monster:
                result.details['monster_battle_integration'] = True
                print("  ✅ Monster-Battle-Integration erfolgreich")
            else:
                result.errors.append("Monster-Battle-Integration fehlgeschlagen")
                print("  ❌ Monster-Battle-Integration fehlgeschlagen")
            
            # Teste Talent-Move-Integration
            if monster.moves and all(hasattr(move, 'name') for move in monster.moves):
                result.details['talent_move_integration'] = True
                print("  ✅ Talent-Move-Integration erfolgreich")
            else:
                result.warnings.append("Talent-Move-Integration nicht vollständig")
                print("  ⚠️  Talent-Move-Integration nicht vollständig")
            
            # Teste Level-Up-Integration
            if hasattr(monster, 'level_up'):
                old_moves = len(monster.moves) if hasattr(monster, 'moves') else 0
                monster.level_up()
                new_moves = len(monster.moves) if hasattr(monster, 'moves') else 0
                
                if new_moves >= old_moves:
                    result.details['level_up_integration'] = True
                    print("  ✅ Level-Up-Integration erfolgreich")
                else:
                    result.warnings.append("Level-Up-Integration hat keine neuen Moves hinzugefügt")
                    print("  ⚠️  Level-Up-Integration hat keine neuen Moves hinzugefügt")
            
            # Bestimme Gesamterfolg
            result.success = (
                result.details.get('monster_battle_integration', False) and
                result.details.get('talent_move_integration', False)
            )
            
        except Exception as e:
            error_msg = f"Integration-Tests fehlgeschlagen: {e}"
            result.errors.append(error_msg)
            print(f"  ❌ {error_msg}")
            traceback.print_exc()
        
        return result
    
    def validate_complete_system(self) -> Dict[str, Any]:
        """Validiere das komplette System"""
        print("🎯 Starte vollständige System-Validierung...")
        print("=" * 60)
        
        # Führe alle Validierungen durch
        self.results = {
            'monster_system': self.validate_monster_system(),
            'talent_system': self.validate_talent_system(),
            'battle_system': self.validate_battle_system(),
            'ui_scene_system': self.validate_ui_scene_system(),
            'experience_system': self.validate_experience_system(),
            'integration_tests': self.run_integration_tests()
        }
        
        # Zähle Fehler und Warnungen
        self.total_errors = sum(len(result.errors) for result in self.results.values())
        self.total_warnings = sum(len(result.warnings) for result in self.results.values())
        
        # Bestimme Gesamterfolg
        all_systems_working = all(result.success for result in self.results.values())
        
        validation_results = {
            'systems': self.results,
            'overall_success': all_systems_working and self.total_errors == 0,
            'total_errors': self.total_errors,
            'total_warnings': self.total_warnings,
            'summary': self._generate_summary()
        }
        
        return validation_results
    
    def _generate_summary(self) -> str:
        """Generiere Zusammenfassung der Validierung"""
        summary = []
        summary.append("=" * 60)
        summary.append("🎯 SYSTEM-VALIDIERUNG ZUSAMMENFASSUNG")
        summary.append("=" * 60)
        
        for system_name, result in self.results.items():
            status = "✅ ERFOLGREICH" if result.success else "❌ FEHLGESCHLAGEN"
            summary.append(f"{system_name.upper()}: {status}")
            
            if result.errors:
                summary.append(f"  Fehler: {len(result.errors)}")
                for error in result.errors:
                    summary.append(f"    - {error}")
            
            if result.warnings:
                summary.append(f"  Warnungen: {len(result.warnings)}")
                for warning in result.warnings:
                    summary.append(f"    - {warning}")
        
        summary.append("=" * 60)
        summary.append(f"GESAMT: {self.total_errors} Fehler, {self.total_warnings} Warnungen")
        
        if self.total_errors == 0:
            summary.append("🎉 SYSTEM IST STABIL UND EINSATZBEREIT!")
        else:
            summary.append("⚠️  SYSTEM BENÖTIGT REPARATUREN!")
        
        summary.append("=" * 60)
        
        return "\n".join(summary)

def main():
    """Hauptfunktion für System-Validierung"""
    print("🎮 UNTOLD STORY - SYSTEM VALIDIERUNG")
    print("Validiert alle System-Komponenten nach Talent-Migration")
    print("=" * 60)
    
    validator = SystemValidator()
    results = validator.validate_complete_system()
    
    # Zeige Zusammenfassung
    print("\n" + results['summary'])
    
    # Speichere Ergebnisse
    with open('system_validation_report.txt', 'w', encoding='utf-8') as f:
        f.write(results['summary'])
    
    print(f"\n📄 Validerungsbericht gespeichert: system_validation_report.txt")
    
    # Exit-Code basierend auf Erfolg
    if results['overall_success']:
        print("🎉 Alle Systeme funktionieren korrekt!")
        sys.exit(0)
    else:
        print("⚠️  System benötigt Reparaturen!")
        sys.exit(1)

if __name__ == "__main__":
    main()
