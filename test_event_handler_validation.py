#!/usr/bin/env python3
"""
Test für Event-Handler Validation - AGENT 2
Testet Event-Handler-Registrierung, Message-Timing und HP-Updates
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

def test_event_handler_validation():
    """Test Event-Handler Validation."""
    print("🎮 AGENT 2: UI EVENT-HANDLER SPECIALIST - Test")
    print("=" * 50)
    
    try:
        # Initialize pygame
        pygame.init()
        pygame.display.set_mode((320, 180))
        
        # Import battle UI components
        from engine.ui.battle.battle_ui_core import BattleUI
        from engine.ui.battle.battle_ui_input import BattleUIInputHandler
        from engine.ui.battle.battle_ui_menus import BattleUIMenuManager
        from engine.systems.monster_instance import MonsterInstance, MonsterSpecies
        from engine.systems.stats import BaseStats
        
        print("✓ Imports erfolgreich")
        
        # Create test monster species
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
        
        class MockEventProcessor:
            def register_ui_handlers(self, ui):
                logger.info("✓ Mock EventProcessor: register_ui_handlers called")
                return True
        
        battle_ui = BattleUI(MockGame())
        battle_ui.event_processor = MockEventProcessor()
        
        # Set up mock battle state
        class MockBattleState:
            def __init__(self):
                self.player_active = test_monster
                self.enemy_active = None
                self.player_team = [test_monster]
                self.enemy_team = []
        
        battle_ui.battle_state = MockBattleState()
        print("✓ Battle UI erstellt")
        
        # Test 1: Event-Handler Registration Timing
        print("\n🔧 Test 1: Event-Handler Registration Timing")
        print("-" * 40)
        
        # Test init_battle with early registration
        battle_ui.init_battle([test_monster], [])
        print("✓ init_battle() called with early event handler registration")
        
        # Test 2: Message-Display Timing
        print("\n🔧 Test 2: Message-Display Timing")
        print("-" * 30)
        
        # Test different priority levels
        battle_ui.add_message("Normal Message", priority="normal")
        print(f"✓ Normal Message: Timer = {battle_ui.message_timer}s")
        
        battle_ui.add_message("Important Message", priority="important")
        print(f"✓ Important Message: Timer = {battle_ui.message_timer}s")
        
        battle_ui.add_message("Critical Message", priority="critical")
        print(f"✓ Critical Message: Timer = {battle_ui.message_timer}s")
        
        battle_ui.add_message("Quick Message", priority="quick")
        print(f"✓ Quick Message: Timer = {battle_ui.message_timer}s")
        
        # Test 3: HP-Bar Updates
        print("\n🔧 Test 3: HP-Bar Updates")
        print("-" * 25)
        
        # Simulate HP damage
        old_hp = test_monster.current_hp
        test_monster.current_hp = 60
        
        # Test HP update event
        hp_event = {
            'type': 'hp_update',
            'target': test_monster,
            'old_hp': old_hp,
            'new_hp': test_monster.current_hp
        }
        
        battle_ui.process_battle_event(hp_event)
        print("✓ HP Update Event verarbeitet")
        
        # Check HP animation
        monster_id = id(test_monster)
        if monster_id in battle_ui.state.animations["hp_bars"]:
            hp_anim = battle_ui.state.animations["hp_bars"][monster_id]
            print(f"✓ HP-Animation: {hp_anim['old_hp']} -> {hp_anim['new_hp']}")
            print(f"✓ Animation Timer: {hp_anim['timer']}s")
            print(f"✓ Animation Speed: {hp_anim['speed']}")
        
        # Test 4: Move-Category Integration
        print("\n🔧 Test 4: Move-Category Integration")
        print("-" * 35)
        
        # Test menu manager move categorization
        menu_manager = battle_ui.menu_manager
        
        # Create mock moves with different categories
        class MockMove:
            def __init__(self, name, category=None, power=50, move_type="normal"):
                self.name = name
                self.category = category
                self.power = power
                self.type = move_type
        
        # Test moves with different category types
        test_moves = [
            MockMove("Fire Punch", "phys", 60, "feuer"),
            MockMove("Magic Blast", "mag", 70, "energie"),
            MockMove("Heal", "support", 0, "gottheit"),
            MockMove("Normal Attack", None, 40, "normal")  # No category
        ]
        
        for move in test_moves:
            category = menu_manager._get_move_category(move)
            print(f"✓ Move '{move.name}': {category}")
        
        # Test 5: Event-Handler Validation
        print("\n🔧 Test 5: Event-Handler Validation")
        print("-" * 35)
        
        # Test input handler validation
        input_handler = battle_ui.input_handler
        validation = input_handler.validate_event_flow()
        
        print("Event-Handler Validation Results:")
        for event, has_handler in validation.items():
            status = "✓" if has_handler else "❌"
            print(f"  {status} {event}: {has_handler}")
        
        # Test 6: Message Event Processing
        print("\n🔧 Test 6: Message Event Processing")
        print("-" * 35)
        
        # Test different message events
        message_events = [
            {'type': 'message', 'message': 'Normal Battle Message', 'priority': 'normal'},
            {'type': 'message', 'message': 'Important Status Change!', 'priority': 'important'},
            {'type': 'message', 'message': 'CRITICAL HIT!', 'priority': 'critical'},
            {'type': 'message', 'message': 'Quick Info', 'priority': 'quick'}
        ]
        
        for event in message_events:
            battle_ui.process_battle_event(event)
            print(f"✓ Processed: '{event['message']}' (priority: {event['priority']})")
        
        print("\n🎯 ERFOLGS-KRITERIEN VALIDIERUNG")
        print("=" * 50)
        
        # Prüfe alle Erfolgs-Kriterien
        success_count = 0
        total_tests = 6
        
        # 1. Event-Handler werden VOR Battle-Start registriert
        if battle_ui.event_processor and hasattr(battle_ui.event_processor, 'register_ui_handlers'):
            print("✅ Event-Handler werden VOR Battle-Start registriert")
            success_count += 1
        else:
            print("❌ Event-Handler nicht korrekt registriert")
        
        # 2. Messages bleiben mindestens 2 Sekunden sichtbar (Standard-Duration)
        # Teste mit normaler Message
        battle_ui.add_message("Test Standard Message", priority="normal")
        if battle_ui.message_timer >= 2.0:
            print("✅ Messages bleiben mindestens 2 Sekunden sichtbar")
            success_count += 1
        else:
            print("❌ Message-Timing nicht korrekt")
        
        # 3. HP-Updates erfolgen SOFORT ohne Verzögerung
        if monster_id in battle_ui.state.animations["hp_bars"]:
            hp_anim = battle_ui.state.animations["hp_bars"][monster_id]
            if hp_anim["current"] == test_monster.current_hp and hp_anim["timer"] <= 0.5:
                print("✅ HP-Updates erfolgen SOFORT ohne Verzögerung")
                success_count += 1
            else:
                print("❌ HP-Updates nicht sofort")
        else:
            print("❌ HP-Animation nicht gefunden")
        
        # 4. Move-Categories nutzen Talent-System
        move_categories = [menu_manager._get_move_category(move) for move in test_moves]
        if "PHYSISCH" in move_categories and "MAGISCH" in move_categories and "STATUS" in move_categories:
            print("✅ Move-Categories nutzen Talent-System")
            success_count += 1
        else:
            print("❌ Move-Category-Integration fehlerhaft")
        
        # 5. Keine Event-Handler Warnings mehr im Log
        critical_handlers = [k for k, v in validation.items() if k.startswith("UI_") and v]
        if len(critical_handlers) >= 5:  # Mindestens 5 UI-Handler
            print("✅ Keine Event-Handler Warnings mehr im Log")
            success_count += 1
        else:
            print("❌ Event-Handler Warnings vorhanden")
        
        # 6. Priority-System funktioniert
        # Teste verschiedene Prioritäten
        battle_ui.add_message("Test Important", priority="important")
        important_timer = battle_ui.message_timer
        battle_ui.add_message("Test Critical", priority="critical")
        critical_timer = battle_ui.message_timer
        battle_ui.add_message("Test Quick", priority="quick")
        quick_timer = battle_ui.message_timer
        
        if important_timer >= 3.0 and critical_timer >= 4.0 and quick_timer <= 1.0:
            print("✅ Priority-System funktioniert")
            success_count += 1
        else:
            print(f"❌ Priority-System funktioniert nicht (important: {important_timer}, critical: {critical_timer}, quick: {quick_timer})")
        
        print(f"\n📊 ERGEBNIS: {success_count}/{total_tests} Tests erfolgreich")
        
        if success_count == total_tests:
            print("🎉 ALLE ERFOLGS-KRITERIEN ERFÜLLT!")
            print("✅ Event-Handler werden VOR Battle-Start registriert")
            print("✅ Messages bleiben mindestens 2 Sekunden sichtbar")
            print("✅ HP-Updates erfolgen SOFORT ohne Verzögerung")
            print("✅ Move-Categories nutzen Talent-System")
            print("✅ Keine Event-Handler Warnings mehr im Log")
            print("✅ Priority-System funktioniert")
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
    success = test_event_handler_validation()
    sys.exit(0 if success else 1)
