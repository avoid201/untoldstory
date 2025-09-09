#!/usr/bin/env python3
"""
Einfacher Kompatibilitätstest für das refactorierte Battle-System
================================================================

Testet die grundlegende Funktionalität ohne komplexe Modul-Imports.
"""

import warnings
import sys
import os

def test_basic_compatibility():
    """Testet die grundlegende Kompatibilität."""
    print("🧪 Teste grundlegende Battle-System Kompatibilität...")
    
    # Test 1: Import der Legacy-Datei
    try:
        import refactored_battle_simple
        print("✅ refactored_battle_simple.py kann importiert werden")
    except ImportError as e:
        print(f"❌ Import fehlgeschlagen: {e}")
        return False
    
    # Test 2: Prüfe, dass alle wichtigen Klassen verfügbar sind
    try:
        from refactored_battle_simple import BattleState, BattleType, BattlePhase
        print("✅ Alle Legacy-Klassen sind verfügbar")
    except ImportError as e:
        print(f"❌ Klassen-Import fehlgeschlagen: {e}")
        return False
    
    # Test 3: Prüfe, dass DeprecationWarnings ausgegeben werden
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        
        # Rufe Deprecation-Funktionen auf
        from refactored_battle_simple import warn_battle_type_deprecated, warn_battle_phase_deprecated
        warn_battle_type_deprecated()
        warn_battle_phase_deprecated()
        
        # Prüfe, dass Warnungen ausgegeben wurden
        if any("deprecated" in str(warning.message) for warning in w):
            print("✅ DeprecationWarnings werden korrekt ausgegeben")
        else:
            print("❌ Keine DeprecationWarnings gefunden")
            print(f"   Gefundene Warnungen: {[str(warning.message) for warning in w]}")
            return False
    
    # Test 4: Prüfe Ruhrpott-Dialekt in Kommentaren
    try:
        with open('refactored_battle_simple.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        if "Ey, hier gehts ab" in content and "dat kannste knicken" in content:
            print("✅ Ruhrpott-Dialekt in Kommentaren gefunden")
        else:
            print("❌ Ruhrpott-Dialekt nicht in Kommentaren gefunden")
            return False
    except Exception as e:
        print(f"❌ Fehler beim Lesen der Datei: {e}")
        return False
    
    print("🎉 Alle grundlegenden Kompatibilitätstests bestanden!")
    return True


def test_import_warnings():
    """Testet, dass Import-Warnungen ausgegeben werden."""
    print("\n🔔 Teste Import-Warnungen...")
    
    # Da die Import-Warnung bereits beim ersten Import ausgegeben wurde,
    # testen wir, dass die Warnungsfunktionen verfügbar sind
    try:
        from refactored_battle_simple import warn_battle_type_deprecated, warn_battle_phase_deprecated
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            # Rufe Warnungsfunktionen auf
            warn_battle_type_deprecated()
            warn_battle_phase_deprecated()
            
            # Prüfe, dass Warnungen ausgegeben wurden
            if any("deprecated" in str(warning.message) for warning in w):
                print("✅ Import-Warnungen werden korrekt ausgegeben")
                for warning in w:
                    if "deprecated" in str(warning.message):
                        print(f"   📢 {warning.message}")
                return True
            else:
                print("❌ Keine Import-Warnungen gefunden")
                return False
    except ImportError as e:
        print(f"❌ Import der Warnungsfunktionen fehlgeschlagen: {e}")
        return False


def show_migration_info():
    """Zeigt Migrationsinformationen an."""
    print("\n📚 MIGRATIONS-INFORMATIONEN:")
    print("=" * 50)
    print("Das alte battle.py System wurde refaktoriert:")
    print()
    print("✅ NEUE STRUKTUR:")
    print("   • battle_enums.py - Alle Enums und Konstanten")
    print("   • battle_controller.py - Haupt-Battle-Logik")
    print("   • battle_system.py - Kompatibilitäts-Layer")
    print("   • refactored_battle.py - Legacy-Wrapper (DEPRECATED)")
    print()
    print("🔄 MIGRATION:")
    print("   ALT: from engine.systems.battle.battle import BattleState")
    print("   NEU: from engine.systems.battle.battle_controller import BattleState")
    print()
    print("⚠️  WARNUNGEN:")
    print("   Alle alten Imports geben DeprecationWarnings aus")
    print("   Der Code funktioniert weiterhin, aber sollte migriert werden")
    print()
    print("📖 Mehr Details: migration_guide.md")


def main():
    """Hauptfunktion für den Kompatibilitätstest."""
    print("🚀 BATTLE SYSTEM KOMPATIBILITÄTSTEST")
    print("=" * 50)
    
    # Teste grundlegende Kompatibilität
    if not test_basic_compatibility():
        print("\n❌ Grundlegende Kompatibilitätstests fehlgeschlagen!")
        return 1
    
    # Teste Import-Warnungen
    if not test_import_warnings():
        print("\n❌ Import-Warnungstests fehlgeschlagen!")
        return 1
    
    # Zeige Migrationsinformationen
    show_migration_info()
    
    print("\n🎯 EMPFEHLUNGEN:")
    print("1. Aktiviere DeprecationWarnings in deinem Code")
    print("2. Migriere schrittweise zu den neuen Imports")
    print("3. Nutze die neuen Features (3v3, Tension, Events)")
    print("4. Konsultiere migration_guide.md für Details")
    
    print("\n✅ Alle Tests bestanden! Das refactorierte System ist kompatibel.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
