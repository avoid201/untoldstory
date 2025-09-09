#!/usr/bin/env python3
"""
Validierungs-Script für die Code-Bereinigung
Testet alle konsolidierten Imports und Funktionalitäten
"""

import sys
import traceback
from pathlib import Path

# Add project to path
sys.path.insert(0, '/Users/leon/Desktop/untold_story')

def test_imports():
    """Teste alle kritischen Imports nach der Bereinigung."""
    
    print("=" * 60)
    print("🧪 UNTOLD STORY - Import Validation Test")
    print("=" * 60 + "\n")
    
    tests = [
        ("BattleResult", "from engine.systems.battle.battle_enums import BattleResult"),
        ("BattlePhase", "from engine.systems.battle.battle_enums import BattlePhase"),
        ("TypeChart", "from engine.systems.types import TypeChart"),
        ("UnifiedDamageCalculator", "from engine.systems.unified_damage_calculator import UnifiedDamageCalculator"),
        ("SimpleBattleManager", "from engine.systems.battle.core.battle_manager import SimpleBattleManager"),
        ("BattleScene", "from engine.scenes.battle_scene import BattleScene"),
    ]
    
    passed = 0
    failed = []
    
    for name, import_str in tests:
        try:
            exec(import_str)
            print(f"✅ {name:<25} Import erfolgreich")
            passed += 1
        except Exception as e:
            error_msg = str(e).split('\n')[0]  # First line of error
            failed.append((name, error_msg))
            print(f"❌ {name:<25} Import fehlgeschlagen: {error_msg}")
    
    print("\n" + "=" * 60)
    print(f"📊 Ergebnis: {passed}/{len(tests)} Tests bestanden")
    
    if failed:
        print("\n⚠️  Fehlgeschlagene Imports:")
        for name, error in failed:
            print(f"   - {name}: {error}")
    else:
        print("✨ Alle Imports funktionieren korrekt!")
    
    return len(failed) == 0

def test_enum_values():
    """Teste ob die Enum-Werte korrekt sind."""
    
    print("\n" + "=" * 60)
    print("🔍 Testing Enum Values")
    print("=" * 60 + "\n")
    
    try:
        from engine.systems.battle.battle_enums import BattleResult, BattlePhase
        
        # Test BattleResult
        print("BattleResult values:")
        for result in BattleResult:
            print(f"  - {result.name}: {result.value}")
        
        # Test specific values
        assert hasattr(BattleResult, 'VICTORY'), "BattleResult.VICTORY fehlt"
        assert hasattr(BattleResult, 'DEFEAT'), "BattleResult.DEFEAT fehlt"
        assert hasattr(BattleResult, 'FLED'), "BattleResult.FLED fehlt"
        assert hasattr(BattleResult, 'CAUGHT'), "BattleResult.CAUGHT fehlt"
        
        print("\n✅ Alle BattleResult-Werte vorhanden")
        
        # Test BattlePhase
        print("\nBattlePhase values:")
        phase_count = 0
        for phase in BattlePhase:
            phase_count += 1
            if phase_count <= 5:  # Show first 5
                print(f"  - {phase.name}: {phase.value}")
        if phase_count > 5:
            print(f"  ... und {phase_count - 5} weitere")
        
        print(f"\n✅ {phase_count} BattlePhase-Werte definiert")
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler beim Testen der Enum-Werte: {e}")
        return False

def test_unified_calculator():
    """Teste den UnifiedDamageCalculator."""
    
    print("\n" + "=" * 60)
    print("⚔️ Testing UnifiedDamageCalculator")
    print("=" * 60 + "\n")
    
    try:
        from engine.systems.unified_damage_calculator import unified_damage_calculator
        
        # Check singleton
        from engine.systems.unified_damage_calculator import UnifiedDamageCalculator
        calc2 = UnifiedDamageCalculator()
        
        assert unified_damage_calculator is calc2, "Singleton pattern funktioniert nicht"
        print("✅ Singleton pattern funktioniert")
        
        # Check methods exist
        methods = ['calculate_damage', 'calculate_recoil_damage', 
                  'calculate_drain_damage', 'get_performance_stats']
        
        for method in methods:
            assert hasattr(unified_damage_calculator, method), f"Methode {method} fehlt"
            print(f"✅ Methode {method} vorhanden")
        
        # Test performance stats
        stats = unified_damage_calculator.get_performance_stats()
        print(f"\n📊 Performance Stats: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler beim Testen des UnifiedDamageCalculator: {e}")
        traceback.print_exc()
        return False

def check_archive():
    """Überprüfe ob die Archiv-Struktur erstellt wurde."""
    
    print("\n" + "=" * 60)
    print("📦 Checking Archive Structure")
    print("=" * 60 + "\n")
    
    archive_path = Path('/Users/leon/Desktop/untold_story/archive')
    
    required_dirs = [
        archive_path,
        archive_path / 'duplicate_code',
        archive_path / 'deprecated'
    ]
    
    for dir_path in required_dirs:
        if dir_path.exists():
            print(f"✅ {dir_path.name}/ vorhanden")
            # List files in directory
            files = list(dir_path.glob('*'))
            if files and dir_path != archive_path:
                print(f"   Enthält {len(files)} Datei(en):")
                for f in files[:3]:  # Show first 3
                    print(f"   - {f.name}")
        else:
            print(f"❌ {dir_path.name}/ fehlt")
    
    # Check for archived files
    archived_files = list((archive_path / 'duplicate_code').glob('*'))
    if archived_files:
        print(f"\n✅ {len(archived_files)} Dateien wurden archiviert")
    
    return True

def main():
    """Hauptfunktion für alle Tests."""
    
    print("\n🚀 UNTOLD STORY - Code Consolidation Validation\n")
    
    all_passed = True
    
    # Run all tests
    all_passed &= test_imports()
    all_passed &= test_enum_values()
    all_passed &= test_unified_calculator()
    all_passed &= check_archive()
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✨ ERFOLG! Alle Tests bestanden!")
        print("Die Code-Bereinigung war erfolgreich.")
    else:
        print("⚠️  WARNUNG! Einige Tests sind fehlgeschlagen.")
        print("Bitte überprüfe die Fehler oben.")
    print("=" * 60 + "\n")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
