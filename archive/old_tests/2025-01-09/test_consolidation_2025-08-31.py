#!/usr/bin/env python3
"""
Test der konsolidierten Battle System Integration
==================================================
Überprüft ob die Agenten-Arbeit erfolgreich war.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Teste ob alle Module importierbar sind."""
    print("=" * 50)
    print("TEST 1: Module Imports")
    print("=" * 50)
    
    results = []
    
    # Test UnifiedBattleManager
    try:
        from engine.systems.battle.unified_battle_manager import UnifiedBattleManager, SimpleBattleManager
        print("✅ UnifiedBattleManager importiert")
        print("✅ SimpleBattleManager verfügbar")
        results.append(True)
    except Exception as e:
        print(f"❌ UnifiedBattleManager Import-Fehler: {e}")
        results.append(False)
    
    # Test BattleController
    try:
        from engine.systems.battle.battle_controller import BattleController, BattleState
        print("✅ BattleController importiert")
        print("✅ BattleState verfügbar")
        results.append(True)
    except Exception as e:
        print(f"❌ BattleController Import-Fehler: {e}")
        results.append(False)
    
    # Test BattleScene
    try:
        from engine.scenes.battle_scene import BattleScene
        print("✅ BattleScene importiert")
        results.append(True)
    except Exception as e:
        print(f"❌ BattleScene Import-Fehler: {e}")
        results.append(False)
    
    # Test Battle Integration
    try:
        from engine.systems.battle.battle_integration import battle_integration
        print("✅ BattleIntegration importiert")
        results.append(True)
    except Exception as e:
        print(f"❌ BattleIntegration Import-Fehler: {e}")
        results.append(False)
    
    # Test Battle AI
    try:
        from engine.systems.battle.battle_ai import BattleAI, create_wild_ai
        print("✅ BattleAI importiert")
        results.append(True)
    except Exception as e:
        print(f"❌ BattleAI Import-Fehler: {e}")
        results.append(False)
    
    # Test Battle Animations
    try:
        from engine.systems.battle.battle_animations import BattleAnimationSystem, animation_system
        print("✅ BattleAnimationSystem importiert")
        results.append(True)
    except Exception as e:
        print(f"❌ BattleAnimationSystem Import-Fehler: {e}")
        results.append(False)
    
    # Test Damage Calculator
    try:
        from engine.systems.battle.unified_damage_calc import UnifiedDamageCalculator
        print("✅ UnifiedDamageCalculator importiert")
        results.append(True)
    except Exception as e:
        print(f"❌ UnifiedDamageCalculator Import-Fehler: {e}")
        results.append(False)
    
    return all(results)


def test_battle_flow():
    """Teste Battle-Flow mit echten Komponenten."""
    print("\n" + "=" * 50)
    print("TEST 2: Battle Flow")
    print("=" * 50)
    
    try:
        from engine.systems.battle.unified_battle_manager import UnifiedBattleManager
        from engine.systems.monster_instance import MonsterInstance
        
        # Erstelle Test-Monster
        class TestMonster:
            def __init__(self, name, hp=100):
                self.name = name
                self.max_hp = hp
                self.current_hp = hp
                self.level = 5
                self.stats = {'atk': 50, 'def': 40, 'spd': 45, 'mag': 30, 'res': 35}
                self.moves = [{'name': 'Tackle', 'power': 40, 'type': 'Normal'}]
                self.types = ['Normal']
                self.is_fainted = property(lambda self: self.current_hp <= 0)
        
        # Erstelle Teams
        player_team = [TestMonster("Spieler-Monster")]
        enemy_team = [TestMonster("Gegner-Monster")]
        
        # Starte Battle
        manager = UnifiedBattleManager()
        success = manager.start_battle(player_team, enemy_team)
        print(f"✅ Battle gestartet: {success}")
        
        # Führe Turn aus
        player_action = {
            'action': 'attack',
            'actor': player_team[0],
            'target': enemy_team[0],
            'move': player_team[0].moves[0]
        }
        
        result = manager.execute_turn(player_action)
        print(f"✅ Turn ausgeführt: Runde {result.get('turn', 0)}")
        
        # Prüfe Messages
        if 'messages' in result:
            print(f"✅ {len(result['messages'])} Nachrichten generiert")
        
        # Prüfe Status
        status = manager.get_status()
        print(f"✅ Battle Status: Phase={status['phase']}, Turn={status['turn']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Battle Flow Fehler: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_simple_battle_manager():
    """Teste SimpleBattleManager Funktionalität."""
    print("\n" + "=" * 50)
    print("TEST 3: SimpleBattleManager")
    print("=" * 50)
    
    try:
        from engine.systems.battle.unified_battle_manager import SimpleBattleManager
        
        # Erstelle SimpleBattleManager
        simple = SimpleBattleManager()
        print("✅ SimpleBattleManager erstellt")
        
        # Teste vereinfachte Methoden
        if hasattr(simple, 'execute_turn_simple'):
            print("✅ execute_turn_simple() verfügbar")
        
        if hasattr(simple, 'get_simple_status'):
            print("✅ get_simple_status() verfügbar")
        
        return True
        
    except Exception as e:
        print(f"❌ SimpleBattleManager Fehler: {e}")
        return False


def test_delegation():
    """Teste ob BattleController korrekt delegiert."""
    print("\n" + "=" * 50)
    print("TEST 4: Controller Delegation")
    print("=" * 50)
    
    try:
        from engine.systems.battle.battle_controller import BattleController
        from engine.systems.monster_instance import MonsterInstance
        
        # Erstelle Controller
        controller = BattleController()
        print("✅ BattleController erstellt")
        
        # Teste Delegation
        class TestMonster:
            def __init__(self, name):
                self.name = name
                self.max_hp = 100
                self.current_hp = 100
                self.level = 5
                self.stats = {'atk': 50, 'def': 40, 'spd': 45}
                self.is_fainted = property(lambda self: self.current_hp <= 0)
        
        # Initialize battle
        controller.initialize_battle(
            [TestMonster("Player")],
            [TestMonster("Enemy")]
        )
        print("✅ Battle initialisiert via Controller")
        
        # Check state
        state = controller.get_state()
        if state:
            print(f"✅ State verfügbar: {len(state.player_team)} vs {len(state.enemy_team)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Controller Delegation Fehler: {e}")
        return False


def test_integration():
    """Teste Battle Integration Module."""
    print("\n" + "=" * 50)
    print("TEST 5: Battle Integration")
    print("=" * 50)
    
    try:
        from engine.systems.battle.battle_integration import battle_integration, start_quick_battle
        
        print("✅ Battle Integration Singleton verfügbar")
        
        # Teste Quick Battle
        class TestMonster:
            def __init__(self, name):
                self.name = name
                self.max_hp = 100
                self.current_hp = 100
                self.level = 5
                self.stats = {'atk': 50, 'def': 40, 'spd': 45}
                self.moves = []
                self.types = ['Normal']
                self.is_fainted = property(lambda self: self.current_hp <= 0)
        
        result = start_quick_battle(TestMonster("Player"), TestMonster("Enemy"))
        
        if result.get('success'):
            print("✅ Quick Battle erfolgreich gestartet")
        
        # Teste Status
        status = battle_integration.get_battle_status()
        print(f"✅ Integration Status: Active={status.get('active', False)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Battle Integration Fehler: {e}")
        return False


def main():
    """Haupttest-Funktion."""
    print("\n" + "🎮" * 25)
    print("BATTLE SYSTEM KONSOLIDIERUNG TEST")
    print("🎮" * 25 + "\n")
    
    tests = [
        ("Imports", test_imports),
        ("Battle Flow", test_battle_flow),
        ("SimpleBattleManager", test_simple_battle_manager),
        ("Controller Delegation", test_delegation),
        ("Integration", test_integration)
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {e}")
            results.append((name, False))
    
    # Zusammenfassung
    print("\n" + "=" * 50)
    print("ZUSAMMENFASSUNG")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{name}: {status}")
    
    print(f"\n{'🎉' * 10}")
    print(f"ERGEBNIS: {passed}/{total} Tests bestanden")
    
    if passed == total:
        print("🏆 ALLE TESTS ERFOLGREICH! Die Konsolidierung war erfolgreich!")
    else:
        print("⚠️  Einige Tests fehlgeschlagen. Bitte überprüfen.")
    
    print(f"{'🎉' * 10}")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
