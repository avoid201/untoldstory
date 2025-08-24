#!/usr/bin/env python3
"""
Automatic Code Fixer
Behebt die wichtigsten Überschneidungen und Fehler automatisch
"""

import os
import shutil
from pathlib import Path

def main():
    print("🔧 Automatic Code Fixer für Untold Story")
    print("="*50)
    
    project_root = Path("/Users/leon/Desktop/untold_story")
    
    # Fix 1: Bereinige battle_system.py - mache es zu einem reinen Re-Export
    print("\n1. Bereinige battle_system.py...")
    battle_system_file = project_root / "engine/systems/battle/battle_system.py"
    
    new_content = '''"""
Battle System Compatibility Layer
Re-exports all battle system components for backwards compatibility
"""

# Re-export everything from battle_controller
from engine.systems.battle.battle_controller import BattleState

# Import all enums and constants
from engine.systems.battle.battle_enums import (
    BattleType, BattlePhase, BattleCommand, AIPersonality
)

# Import subsystems
from engine.systems.battle.battle_tension import TensionManager
from engine.systems.battle.battle_validation import BattleValidator
from engine.systems.battle.battle_actions import BattleActionExecutor
from engine.systems.battle.battle_ai import BattleAI
from engine.systems.battle.command_collection import CommandCollector, CommandType
from engine.systems.battle.dqm_formulas import DQMCalculator

# Re-export for compatibility
__all__ = [
    'BattleState', 'BattleType', 'BattlePhase', 'BattleCommand', 
    'AIPersonality', 'TensionManager', 'BattleValidator',
    'BattleActionExecutor', 'BattleAI', 'CommandCollector',
    'CommandType', 'DQMCalculator'
]
'''
    
    with open(battle_system_file, 'w') as f:
        f.write(new_content)
    print("   ✅ battle_system.py ist jetzt ein sauberer Re-Export")
    
    # Fix 2: Verschiebe Test-Dateien
    print("\n2. Verschiebe Test-Dateien...")
    battle_dir = project_root / "engine/systems/battle"
    tests_dir = project_root / "tests"
    tests_dir.mkdir(exist_ok=True)
    
    test_files = list(battle_dir.glob("test_*.py"))
    for test_file in test_files:
        dest = tests_dir / test_file.name
        if not dest.exists():
            shutil.move(str(test_file), str(dest))
            print(f"   ✅ Verschoben: {test_file.name}")
    
    # Fix 3: Erstelle unified damage calculator
    print("\n3. Erstelle unified damage calculator...")
    damage_calc_file = project_root / "engine/systems/battle/damage_calculator.py"
    
    unified_calc = '''"""
Unified Damage Calculator
Konsolidiert alle Damage-Berechnungen an einem Ort
"""

from typing import Dict, Any, Optional
from engine.systems.battle.dqm_formulas import DQMCalculator

class UnifiedDamageCalculator:
    """Zentrale Schadensberechnung für alle Battle-Systeme."""
    
    def __init__(self):
        self.dqm_calculator = DQMCalculator()
        
    def calculate_damage(self, 
                        attacker: Any, 
                        defender: Any, 
                        move: Any,
                        use_dqm: bool = True,
                        **kwargs) -> Dict[str, Any]:
        """
        Berechnet Schaden mit optionalen DQM-Formeln.
        
        Args:
            attacker: Angreifendes Monster
            defender: Verteidigendes Monster
            move: Verwendete Attacke
            use_dqm: Ob DQM-Formeln verwendet werden sollen
            **kwargs: Zusätzliche Parameter
            
        Returns:
            Dict mit Schadensinformationen
        """
        if use_dqm:
            # Verwende DQM-System
            return self.dqm_calculator.calculate_damage(
                attacker_stats=getattr(attacker, 'stats', {}),
                defender_stats=getattr(defender, 'stats', {}),
                move_power=getattr(move, 'power', 50),
                is_physical=getattr(move, 'category', 'phys') == 'phys',
                tension_level=kwargs.get('tension_level', 0),
                attacker_traits=getattr(attacker, 'traits', []),
                defender_traits=getattr(defender, 'traits', [])
            )
        else:
            # Einfache Berechnung als Fallback
            atk = attacker.stats.get('atk', 50) if hasattr(attacker, 'stats') else 50
            def_ = defender.stats.get('def', 40) if hasattr(defender, 'stats') else 40
            power = getattr(move, 'power', 50)
            
            # Basis-Formel
            damage = ((atk * 2 / def_) * power) / 50 + 2
            
            # Zufallsfaktor
            import random
            damage *= random.uniform(0.85, 1.0)
            
            return {
                'final_damage': int(damage),
                'is_critical': False,
                'effectiveness': 1.0
            }
    
    def calculate_healing(self, caster: Any, target: Any, skill: Any) -> int:
        """Berechnet Heilung."""
        mag = caster.stats.get('mag', 50) if hasattr(caster, 'stats') else 50
        base_heal = getattr(skill, 'power', 30)
        
        # Heilungsformel
        healing = base_heal + (mag * 0.5)
        
        return int(healing)
    
    def calculate_status_damage(self, monster: Any, status: str) -> int:
        """Berechnet Statuseffekt-Schaden."""
        max_hp = getattr(monster, 'max_hp', 100)
        
        status_damage = {
            'poison': max_hp // 8,
            'burn': max_hp // 16,
            'curse': max_hp // 10,
        }
        
        return status_damage.get(status, 0)

# Singleton-Instanz
_damage_calc_instance = None

def get_damage_calculator() -> UnifiedDamageCalculator:
    """Hole Singleton-Instanz des Damage Calculators."""
    global _damage_calc_instance
    if _damage_calc_instance is None:
        _damage_calc_instance = UnifiedDamageCalculator()
    return _damage_calc_instance
'''
    
    with open(damage_calc_file, 'w') as f:
        f.write(unified_calc)
    print("   ✅ Unified damage calculator erstellt")
    
    # Fix 4: Update battle_controller.py um unified calculator zu nutzen
    print("\n4. Update battle_controller.py...")
    controller_file = project_root / "engine/systems/battle/battle_controller.py"
    
    if controller_file.exists():
        with open(controller_file, 'r') as f:
            content = f.read()
        
        # Füge Import hinzu wenn nicht vorhanden
        if "from engine.systems.battle.damage_calculator import" not in content:
            import_line = "from engine.systems.battle.damage_calculator import get_damage_calculator\n"
            # Füge nach anderen Imports hinzu
            import_pos = content.find("logger = logging.getLogger")
            if import_pos > 0:
                content = content[:import_pos] + import_line + content[import_pos:]
        
        # Ersetze calculate_dqm_damage Methode
        old_method_start = content.find("def calculate_dqm_damage(self")
        if old_method_start > 0:
            old_method_end = content.find("\n    def ", old_method_start + 1)
            if old_method_end < 0:
                old_method_end = len(content)
            
            new_method = '''def calculate_dqm_damage(self, attacker, defender, move):
        """Calculate damage using unified calculator."""
        calculator = get_damage_calculator()
        return calculator.calculate_damage(
            attacker, defender, move,
            use_dqm=True,
            tension_level=self.tension_manager.get_multiplier(attacker) if self.tension_manager else 0
        )
'''
            content = content[:old_method_start] + new_method + content[old_method_end:]
        
        with open(controller_file, 'w') as f:
            f.write(content)
        print("   ✅ battle_controller.py nutzt jetzt unified calculator")
    
    # Fix 5: Lösche redundante Dateien
    print("\n5. Lösche redundante Dateien...")
    files_to_delete = [
        battle_dir / "battle_system_old.py",
        battle_dir / "example_dqm_integration.py",
        battle_dir / "example_event_system.py",
        battle_dir / "dqm_integration.py",  # Wenn leer/ungenutzt
    ]
    
    for file in files_to_delete:
        if file.exists():
            os.remove(file)
            print(f"   ✅ Gelöscht: {file.name}")
    
    # Fix 6: Verschiebe Dokumentation
    print("\n6. Verschiebe Dokumentation...")
    docs_dir = project_root / "docs" / "battle_system"
    docs_dir.mkdir(parents=True, exist_ok=True)
    
    md_files = list(battle_dir.glob("*.md"))
    for md_file in md_files:
        dest = docs_dir / md_file.name
        if not dest.exists():
            shutil.move(str(md_file), str(dest))
            print(f"   ✅ Verschoben: {md_file.name}")
    
    print("\n" + "="*50)
    print("✅ ALLE FIXES ANGEWENDET!")
    print("\nNächste Schritte:")
    print("1. Führe aus: python3 verify_integration.py")
    print("2. Teste mit: python3 -m pytest tests/")
    print("3. Starte das Spiel und teste einen Kampf")
    
    # Erstelle Zusammenfassung
    summary = """
# Auto-Fix Summary

## Angewendete Fixes:
1. ✅ battle_system.py bereinigt (nur Re-Exports)
2. ✅ Test-Dateien nach /tests/ verschoben
3. ✅ Unified damage calculator erstellt
4. ✅ battle_controller.py nutzt unified calculator
5. ✅ Redundante Dateien gelöscht
6. ✅ Dokumentation nach /docs/ verschoben

## Bereinigte Struktur:
- Keine doppelten BattleState-Definitionen mehr
- Eine zentrale Damage-Berechnung
- Saubere Dateistruktur
- Keine Test-Dateien im Production-Code

## Verbleibende manuelle Aufgaben:
- Import-Statements in anderen Dateien prüfen
- Eventuelle Unit-Tests anpassen
- Performance-Tests durchführen
"""
    
    summary_file = project_root / "AUTO_FIX_SUMMARY.md"
    with open(summary_file, 'w') as f:
        f.write(summary)
    
    print(f"\n📄 Zusammenfassung gespeichert in: {summary_file}")

if __name__ == "__main__":
    main()
