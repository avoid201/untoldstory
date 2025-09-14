#!/usr/bin/env python3
"""
Test-Suite für die Kampfsystem-Bugfixes
Validiert alle kritischen Reparaturen
"""

import sys
import os
import logging
from unittest.mock import Mock, MagicMock

# Füge den Engine-Pfad hinzu
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'engine'))

# Konfiguriere Logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_division_by_zero_fix():
    """Testet den Division-by-Zero-Fix in der Fluchtberechnung."""
    print("🧪 Teste Division-by-Zero-Fix...")
    
    try:
        from engine.systems.battle.turn_logic_fixed import SpeedTier
        
        # Test mit ungültigen Geschwindigkeitswerten
        result1 = SpeedTier.calculate_flee_chance(100, 0)  # Division durch Null
        assert result1 == 1.0, f"Erwartet: 1.0, Bekommen: {result1}"
        
        result2 = SpeedTier.calculate_flee_chance(100, -5)  # Negative Geschwindigkeit
        assert result2 == 1.0, f"Erwartet: 1.0, Bekommen: {result2}"
        
        result3 = SpeedTier.calculate_flee_chance(0, 100)  # Läufer-Geschwindigkeit 0
        assert result3 == 0.0, f"Erwartet: 0.0, Bekommen: {result3}"
        
        print("✅ Division-by-Zero-Fix funktioniert!")
        return True
        
    except Exception as e:
        print(f"❌ Division-by-Zero-Fix fehlgeschlagen: {str(e)}")
        return False

def test_none_checks():
    """Testet die None-Checks für Monster-Attribute."""
    print("🧪 Teste None-Checks...")
    
    try:
        from engine.systems.battle.turn_logic_fixed import BattleAction, ActionType
        
        # Erstelle Mock-Monster ohne gültige Stats
        mock_monster = Mock()
        mock_monster.name = "TestMonster"
        mock_monster.stats = {}  # Leeres Stats-Dict
        
        # Erstelle BattleAction mit ungültigem Monster
        action = BattleAction(
            actor=mock_monster,
            action_type=ActionType.ATTACK
        )
        
        # Teste sichere Geschwindigkeitsberechnung
        speed = action.get_speed()
        assert speed == 1, f"Erwartet: 1 (Fallback), Bekommen: {speed}"
        
        print("✅ None-Checks funktionieren!")
        return True
        
    except Exception as e:
        print(f"❌ None-Checks fehlgeschlagen: {str(e)}")
        return False

def test_stat_stages_validation():
    """Testet die Stat-Stages-Validierung."""
    print("🧪 Teste Stat-Stages-Validierung...")
    
    try:
        from engine.systems.battle.turn_logic_fixed import BattleAction, ActionType
        
        # Erstelle Mock-Monster ohne stat_stages
        mock_monster = Mock()
        mock_monster.name = "TestMonster"
        mock_monster.stats = {"spd": 50}
        mock_monster.stat_stages = None  # Keine stat_stages
        
        # Erstelle BattleAction
        action = BattleAction(
            actor=mock_monster,
            action_type=ActionType.ATTACK
        )
        
        # Teste sichere Geschwindigkeitsberechnung
        speed = action.get_speed()
        assert speed == 50, f"Erwartet: 50, Bekommen: {speed}"
        
        print("✅ Stat-Stages-Validierung funktioniert!")
        return True
        
    except Exception as e:
        print(f"❌ Stat-Stages-Validierung fehlgeschlagen: {str(e)}")
        return False

def test_battle_action_validation():
    """Testet die BattleAction-Validierung."""
    print("🧪 Teste BattleAction-Validierung...")
    
    try:
        from engine.systems.battle.turn_logic_fixed import BattleAction, ActionType, TurnOrder
        
        # Erstelle TurnOrder
        turn_order = TurnOrder()
        
        # Teste mit None-Aktion
        turn_order.add_action(None)
        assert len(turn_order.actions) == 0, "None-Aktionen sollten nicht hinzugefügt werden"
        
        # Teste mit ungültiger Aktion
        mock_monster = Mock()
        mock_monster.name = "TestMonster"
        mock_monster.stats = {"spd": 50}
        
        action = BattleAction(
            actor=mock_monster,
            action_type=ActionType.ATTACK
        )
        
        turn_order.add_action(action)
        assert len(turn_order.actions) == 1, "Gültige Aktion sollte hinzugefügt werden"
        
        print("✅ BattleAction-Validierung funktioniert!")
        return True
        
    except Exception as e:
        print(f"❌ BattleAction-Validierung fehlgeschlagen: {str(e)}")
        return False

def test_speed_calculations():
    """Testet die Geschwindigkeitsberechnungen."""
    print("🧪 Teste Geschwindigkeitsberechnungen...")
    
    try:
        from engine.systems.battle.turn_logic_fixed import SpeedTier
        
        # Teste Geschwindigkeitsverhältnis
        ratio1 = SpeedTier.calculate_speed_ratio(100, 50)
        assert ratio1 == 2.0, f"Erwartet: 2.0, Bekommen: {ratio1}"
        
        ratio2 = SpeedTier.calculate_speed_ratio(50, 100)
        assert ratio2 == 0.5, f"Erwartet: 0.5, Bekommen: {ratio2}"
        
        # Teste mit ungültigen Werten
        ratio3 = SpeedTier.calculate_speed_ratio(100, 0)
        assert ratio3 == 2.0, f"Erwartet: 2.0 (Fallback), Bekommen: {ratio3}"
        
        print("✅ Geschwindigkeitsberechnungen funktionieren!")
        return True
        
    except Exception as e:
        print(f"❌ Geschwindigkeitsberechnungen fehlgeschlagen: {str(e)}")
        return False

def test_trick_room_effects():
    """Testet die Trick Room Effekte."""
    print("🧪 Teste Trick Room Effekte...")
    
    try:
        from engine.systems.battle.turn_logic_fixed import TrickRoom
        
        # Erstelle Trick Room
        trick_room = TrickRoom(duration=3)
        
        # Teste Aktivierung
        trick_room.activate()
        assert trick_room.active == True, "Trick Room sollte aktiv sein"
        assert trick_room.turns_remaining == 3, "Verbleibende Runden sollten 3 sein"
        
        # Teste Tick
        expired = trick_room.tick()
        assert expired == False, "Trick Room sollte nicht abgelaufen sein"
        assert trick_room.turns_remaining == 2, "Verbleibende Runden sollten 2 sein"
        
        # Teste Geschwindigkeitsmodifikation
        modified_speed = trick_room.modify_speed(100, 999)
        assert modified_speed == 899, f"Erwartet: 899, Bekommen: {modified_speed}"
        
        print("✅ Trick Room Effekte funktionieren!")
        return True
        
    except Exception as e:
        print(f"❌ Trick Room Effekte fehlgeschlagen: {str(e)}")
        return False

def test_error_handling():
    """Testet die allgemeine Fehlerbehandlung."""
    print("🧪 Teste allgemeine Fehlerbehandlung...")
    
    try:
        from engine.systems.battle.turn_logic_fixed import TurnManager
        
        # Erstelle TurnManager mit Mock-Game
        mock_game = Mock()
        turn_manager = TurnManager(mock_game)
        
        # Teste ungültige Phase
        turn_manager.set_phase("invalid_phase")
        assert turn_manager.get_current_phase() == "input", "Phase sollte unverändert bleiben"
        
        # Teste sichere Methoden
        turn_manager.start_new_turn()
        assert turn_manager.turn_count == 1, "Runden-Zähler sollte erhöht werden"
        
        print("✅ Allgemeine Fehlerbehandlung funktioniert!")
        return True
        
    except Exception as e:
        print(f"❌ Allgemeine Fehlerbehandlung fehlgeschlagen: {str(e)}")
        return False

def run_all_tests():
    """Führt alle Tests aus."""
    print("🚀 Starte Kampfsystem-Bugfix-Tests...\n")
    
    tests = [
        test_division_by_zero_fix,
        test_none_checks,
        test_stat_stages_validation,
        test_battle_action_validation,
        test_speed_calculations,
        test_trick_room_effects,
        test_error_handling
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} hat eine Ausnahme geworfen: {str(e)}")
        print()
    
    print(f"📊 Testergebnisse: {passed}/{total} Tests bestanden")
    
    if passed == total:
        print("🎉 Alle Tests bestanden! Das Kampfsystem ist repariert.")
        return True
    else:
        print("⚠️  Einige Tests fehlgeschlagen. Überprüfe die Implementierung.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
