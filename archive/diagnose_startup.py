#!/usr/bin/env python3
"""
Diagnostik-Script für Untold Story Startup-Fehler
"""

import sys
import os
import traceback

# Füge Projekt-Root zum Path hinzu
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def diagnose_startup():
    """Diagnostiziere warum das Spiel nicht startet."""
    
    print("=" * 60)
    print("🔍 UNTOLD STORY - STARTUP DIAGNOSTIK")
    print("=" * 60)
    
    # 1. Teste Game Import
    print("\n1. Teste Game Import...")
    try:
        from engine.core.game import Game
        print("✓ Game importiert")
    except ImportError as e:
        print(f"❌ Game Import fehlgeschlagen: {e}")
        traceback.print_exc()
        return False
    
    # 2. Teste Game Initialisierung
    print("\n2. Teste Game Initialisierung...")
    try:
        game = Game()
        print("✓ Game Objekt erstellt")
    except Exception as e:
        print(f"❌ Game Initialisierung fehlgeschlagen: {e}")
        traceback.print_exc()
        return False
    
    # 3. Teste Scene Import
    print("\n3. Teste Scene Imports...")
    try:
        from engine.scenes.start_scene import StartScene
        print("✓ StartScene importiert")
    except ImportError as e:
        print(f"❌ StartScene Import fehlgeschlagen: {e}")
        traceback.print_exc()
        
    # 4. Teste Menu System
    print("\n4. Teste Menu System...")
    try:
        from engine.ui.menu_system import MenuManager
        print("✓ MenuManager importiert")
    except ImportError as e:
        print(f"❌ MenuManager Import fehlgeschlagen: {e}")
        # Versuche alte Imports
        try:
            from engine.ui.menus import MenuBase
            print("⚠️ Alte menus.py noch vorhanden!")
        except:
            pass
        try:
            from engine.ui.enhanced_menus import EnhancedMenuBase
            print("⚠️ Alte enhanced_menus.py noch vorhanden!")
        except:
            pass
        traceback.print_exc()
    
    # 5. Teste Battle UI
    print("\n5. Teste Battle UI...")
    try:
        from engine.ui.battle.battle_ui_core import BattleUI
        print("✓ BattleUI importiert")
    except ImportError as e:
        print(f"❌ BattleUI Import fehlgeschlagen: {e}")
        # Versuche alten Import
        try:
            from engine.ui.battle_ui import BattleUI
            print("⚠️ Alte battle_ui.py noch vorhanden!")
        except:
            pass
        traceback.print_exc()
    
    # 6. Prüfe kritische Dateien
    print("\n6. Prüfe kritische Dateien...")
    critical_files = [
        "engine/core/game.py",
        "engine/core/resources.py",
        "engine/core/config.py",
        "engine/ui/menu_system.py",
        "main.py"
    ]
    
    for filepath in critical_files:
        if os.path.exists(filepath):
            print(f"✓ {filepath} existiert")
        else:
            print(f"❌ {filepath} FEHLT!")
    
    return True

if __name__ == "__main__":
    diagnose_startup()
    
    print("\n" + "=" * 60)
    print("Versuche main.py direkt zu importieren...")
    print("=" * 60)
    
    try:
        import main
        print("✓ main.py erfolgreich importiert")
    except Exception as e:
        print(f"❌ main.py Import fehlgeschlagen:")
        print(f"   {e}")
        traceback.print_exc()
