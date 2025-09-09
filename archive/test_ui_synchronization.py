#!/usr/bin/env python3
"""
Test für UI Update Synchronization - AGENT 3
Testet sofortige HP-Bar-Updates und Message-Darstellung
"""

import sys
import os
import pygame
import time
import logging

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_ui_synchronization():
    """Test UI Update Synchronization."""
    print("🎮 AGENT 3: UI UPDATE SYNCHRONIZER - Test")
    print("=" * 50)
    
    try:
        # Initialize pygame
        pygame.init()
        pygame.display.set_mode((320, 180))
        
        # Import battle UI components
        from engine.ui.battle.battle_ui_core import BattleUI
        from engine.ui.battle.battle_ui_state import BattleUIState
        from engine.systems.monster_instance import MonsterInstance
        from engine.systems.stats import BaseStats
        
        print("✓ Imports erfolgreich")
        
        # Create test monster species
        from engine.systems.monster_instance import MonsterSpecies
        test_species = MonsterSpecies(
            id=999,
            name="Test Monster",
            types=["Normal"],
            base_stats=BaseStats(hp=100, atk=50, def_=30, mag=40, res=25, spd=60),
            rank="F"
        )
        
        # Create test monster instance
        test_monster = MonsterInstance(
            species=test_species,
            level=10,
            nickname="Test Monster"
        )
        test_monster.current_hp = 80
        test_monster.max_hp = 100
        
        print(f"✓ Test Monster erstellt: {test_monster.name} ({test_monster.current_hp}/{test_monster.max_hp} HP)")
        
        # Create Battle UI
        class MockGame:
            pass
        
        battle_ui = BattleUI(MockGame())
        
        # Set up mock battle state
        class MockBattleState:
            def __init__(self):
                self.player_active = test_monster
                self.enemy_active = None
        
        battle_ui.battle_state = MockBattleState()
        print("✓ Battle UI erstellt")
        
        # Test 1: Sofortige HP-Bar-Updates
        print("\n🔧 Test 1: Sofortige HP-Bar-Updates")
        print("-" * 30)
        
        # Simuliere HP-Schaden
        old_hp = test_monster.current_hp
        test_monster.current_hp = 60  # 20 HP Schaden
        
        # Update HP Bar
        battle_ui.update_hp_bar(test_monster, animated=True)
        
        # Prüfe ob HP-Animation sofort gestartet wurde
        monster_id = id(test_monster)  # Verwende Python ID als Fallback
        if monster_id in battle_ui.state.animations["hp_bars"]:
            hp_anim = battle_ui.state.animations["hp_bars"][monster_id]
            print(f"✓ HP-Animation gestartet: {hp_anim['old_hp']} -> {hp_anim['new_hp']}")
            print(f"✓ Animation aktiv: {hp_anim['active']}")
            print(f"✓ Timer: {hp_anim['timer']}s")
        else:
            print("❌ HP-Animation nicht gefunden!")
        
        # Test 2: Message-Queue mit Timer
        print("\n🔧 Test 2: Message-Queue mit Timer")
        print("-" * 30)
        
        # Teste verschiedene Message-Typen
        battle_ui.add_message("Test Message 1", duration=1.0)
        battle_ui.add_message("Wichtige Message", duration=2.0)
        
        print(f"✓ Current Message: '{battle_ui.current_message}'")
        print(f"✓ Message Timer: {battle_ui.message_timer}s")
        print(f"✓ Message Wait: {battle_ui.waiting_for_input}")
        
        # Test 3: Event-Verarbeitung
        print("\n🔧 Test 3: Event-Verarbeitung")
        print("-" * 30)
        
        # Simuliere HP Update Event
        hp_event = {
            'type': 'hp_update',
            'target': test_monster,
            'old_hp': 60,
            'new_hp': 40
        }
        
        battle_ui.process_battle_event(hp_event)
        print("✓ HP Update Event verarbeitet")
        
        # Simuliere Message Event
        message_event = {
            'type': 'message',
            'message': 'Monster nimmt Schaden!',
            'duration': 1.5,
            'priority': 'normal'
        }
        
        battle_ui.process_battle_event(message_event)
        print("✓ Message Event verarbeitet")
        
        # Test 4: Damage Number Positionierung
        print("\n🔧 Test 4: Damage Number Positionierung")
        print("-" * 30)
        
        battle_ui.show_damage_number(test_monster, 25, is_critical=True)
        print("✓ Damage Number erstellt")
        
        # Prüfe Damage Numbers in State
        if battle_ui.state.animations["damage_numbers"]:
            damage = battle_ui.state.animations["damage_numbers"][0]
            print(f"✓ Damage Number: {damage['value']} at {damage['pos']}")
            print(f"✓ Color: {damage['color']}")
            print(f"✓ Critical: {damage['is_critical']}")
        
        # Test 5: Animation Updates
        print("\n🔧 Test 5: Animation Updates")
        print("-" * 30)
        
        # Simuliere Animation Update
        dt = 0.016  # 60 FPS
        battle_ui.state.update_animations(dt)
        print("✓ Animation Update durchgeführt")
        
        # Prüfe HP-Animation Progress
        if monster_id in battle_ui.state.animations["hp_bars"]:
            hp_anim = battle_ui.state.animations["hp_bars"][monster_id]
            if hp_anim["active"]:
                print(f"✓ HP-Animation läuft: {hp_anim['current']:.1f} HP")
                print(f"✓ Verbleibender Timer: {hp_anim['timer']:.3f}s")
        
        print("\n🎯 ERFOLGS-KRITERIEN VALIDIERUNG")
        print("=" * 50)
        
        # Prüfe alle Erfolgs-Kriterien
        success_count = 0
        total_tests = 5
        
        # 1. HP-Bars zeigen sofort aktuelle HP an
        if monster_id in battle_ui.state.animations["hp_bars"]:
            hp_anim = battle_ui.state.animations["hp_bars"][monster_id]
            if hp_anim["active"] and hp_anim["current"] == test_monster.current_hp:
                print("✅ HP-Bars zeigen sofort aktuelle HP an")
                success_count += 1
            else:
                print("❌ HP-Bars zeigen nicht sofort aktuelle HP an")
        else:
            print("❌ HP-Bars Animation nicht gefunden")
        
        # 2. Messages erscheinen und bleiben 1.5 Sekunden sichtbar
        if battle_ui.current_message and battle_ui.message_timer > 0:
            print("✅ Messages erscheinen und bleiben sichtbar")
            success_count += 1
        else:
            print("❌ Messages erscheinen nicht oder Timer nicht gesetzt")
        
        # 3. Damage-Numbers werden korrekt positioniert
        if battle_ui.state.animations["damage_numbers"]:
            damage = battle_ui.state.animations["damage_numbers"][0]
            if damage["pos"][0] > 0 and damage["pos"][1] > 0:
                print("✅ Damage-Numbers werden korrekt positioniert")
                success_count += 1
            else:
                print("❌ Damage-Numbers Positionierung fehlerhaft")
        else:
            print("❌ Damage-Numbers nicht gefunden")
        
        # 4. UI reagiert auf alle Battle-Events ohne Verzögerung
        if battle_ui.state.animations["hp_bars"] and battle_ui.current_message:
            print("✅ UI reagiert auf alle Battle-Events ohne Verzögerung")
            success_count += 1
        else:
            print("❌ UI reagiert nicht auf alle Battle-Events")
        
        # 5. Animation System funktioniert
        if battle_ui.state.is_animating():
            print("✅ Animation System funktioniert")
            success_count += 1
        else:
            print("❌ Animation System funktioniert nicht")
        
        print(f"\n📊 ERGEBNIS: {success_count}/{total_tests} Tests erfolgreich")
        
        if success_count == total_tests:
            print("🎉 ALLE ERFOLGS-KRITERIEN ERFÜLLT!")
            print("✅ HP-Bar-Updates sind sofort sichtbar")
            print("✅ Messages erscheinen korrekt mit Timer")
            print("✅ Damage-Numbers sind korrekt positioniert")
            print("✅ UI reagiert ohne Verzögerung auf Events")
            print("✅ Animation System funktioniert einwandfrei")
            return True
        else:
            print("⚠️ Einige Tests fehlgeschlagen - weitere Optimierung erforderlich")
            return False
            
    except Exception as e:
        print(f"❌ Test fehlgeschlagen: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        pygame.quit()

if __name__ == "__main__":
    success = test_ui_synchronization()
    sys.exit(0 if success else 1)
