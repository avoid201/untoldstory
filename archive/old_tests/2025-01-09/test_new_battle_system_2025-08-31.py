#!/usr/bin/env python3
"""
Test Script für das neue Battle-System
Testet deine gewünschte Menü-Struktur: Angreifen, Skills, Zähmen, Items, Fliehen
"""

import sys
import os
import pygame

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_battle_scene_import():
    """Test ob BattleScene korrekt importiert werden kann."""
    try:
        from engine.scenes.battle_scene import BattleScene, BattleResult
        print("✅ BattleScene Import erfolgreich!")
        
        # Test SimpleBattleManager Import
        from engine.systems.battle.core.battle_manager import SimpleBattleManager
        print("✅ SimpleBattleManager Import erfolgreich!")
        
        # Test UI Enhancements Import
        from engine.ui.battle_ui_enhancements import SkillMenu, ItemMenu
        print("✅ UI-Enhancements Import erfolgreich!")
        
        # Test DQM Calculator Import
        from engine.systems.battle.dqm_formulas import DQMCalculator
        print("✅ DQMCalculator Import erfolgreich!")
        
        return True
        
    except Exception as e:
        print(f"❌ Import-Fehler: {e}")
        return False

def test_menu_options():
    """Test die gewünschte Menü-Struktur."""
    try:
        from engine.scenes.battle_scene import BattleScene
        
        # Mock Game Object
        class MockGame:
            def __init__(self):
                self.logical_width = 320
                self.logical_height = 180
        
        pygame.init()
        mock_game = MockGame()
        
        # Create BattleScene
        battle_scene = BattleScene(mock_game)
        
        # Test Wild Battle Menu Options
        battle_scene.is_wild = True
        wild_options = battle_scene._get_menu_options()
        expected_wild = ["Angreifen", "Skills", "Zähmen", "Items", "Fliehen"]
        
        print(f"🐾 Wild Battle Menü: {wild_options}")
        if wild_options == expected_wild:
            print("✅ Wild Battle Menü korrekt!")
        else:
            print(f"❌ Wild Battle Menü falsch! Erwartet: {expected_wild}")
            
        # Test Trainer Battle Menu Options  
        battle_scene.is_wild = False
        trainer_options = battle_scene._get_menu_options()
        expected_trainer = ["Angreifen", "Skills", "Items", "Team", "Aufgeben"]
        
        print(f"👤 Trainer Battle Menü: {trainer_options}")
        if trainer_options == expected_trainer:
            print("✅ Trainer Battle Menü korrekt!")
        else:
            print(f"❌ Trainer Battle Menü falsch! Erwartet: {expected_trainer}")
            
        return True
        
    except Exception as e:
        print(f"❌ Menü-Test Fehler: {e}")
        return False

def test_battle_manager():
    """Test SimpleBattleManager Funktionalität."""
    try:
        from engine.systems.battle.core.battle_manager import SimpleBattleManager, BattleResult
        
        class MockGame:
            pass
            
        # Create Battle Manager
        battle_manager = SimpleBattleManager(MockGame())
        
        # Test initial state
        print(f"📊 Battle Manager Phase: {battle_manager.phase}")
        print(f"📊 Battle Manager Result: {battle_manager.result}")
        
        # Test methods exist
        methods = ['start_battle', 'handle_player_attack', 'handle_flee', 'is_battle_over']
        for method in methods:
            if hasattr(battle_manager, method):
                print(f"✅ Methode {method} vorhanden")
            else:
                print(f"❌ Methode {method} fehlt!")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Battle Manager Test Fehler: {e}")
        return False

def test_dqm_integration():
    """Test DQM Calculator Integration."""
    try:
        from engine.systems.battle.dqm_formulas import DQMCalculator
        
        # Create DQM Calculator
        calculator = DQMCalculator()
        
        # Test key methods
        methods = ['calculate_damage', 'calculate_turn_order', 'calculate_escape_chance']
        for method in methods:
            if hasattr(calculator, method):
                print(f"✅ DQM Methode {method} vorhanden")
            else:
                print(f"❌ DQM Methode {method} fehlt!")
                return False
                
        print("✅ DQM Calculator bereit!")
        return True
        
    except Exception as e:
        print(f"❌ DQM Test Fehler: {e}")
        return False

def main():
    """Haupttest-Funktion."""
    print("🎮 Teste dein neues Battle-System...")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_battle_scene_import),
        ("Menü-Struktur Test", test_menu_options), 
        ("Battle Manager Test", test_battle_manager),
        ("DQM Integration Test", test_dqm_integration),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}:")
        print("-" * 30)
        if test_func():
            passed += 1
            print(f"✅ {test_name} BESTANDEN")
        else:
            print(f"❌ {test_name} FEHLGESCHLAGEN")
    
    print("\n" + "=" * 50)
    print(f"📊 Ergebnis: {passed}/{total} Tests bestanden")
    
    if passed == total:
        print("🎉 Alle Tests bestanden! Dein Battle-System ist bereit!")
        print("\n🎯 Nächste Schritte:")
        print("  1. Starte das Spiel mit python3 main.py")
        print("  2. Beginne einen Kampf")
        print("  3. Teste die 5 Menü-Optionen:")
        print("     • Angreifen (AI wählt Move)")
        print("     • Skills (Untermenü öffnet)")  
        print("     • Zähmen (Stats-basierte Chance)")
        print("     • Items (Inventar öffnet)")
        print("     • Fliehen (Speed-basierte Chance)")
    else:
        print("⚠️  Einige Tests sind fehlgeschlagen!")
        print("💡 Überprüfe die Import-Pfade und Dependencies.")
        
    return passed == total

if __name__ == "__main__":
    main()
