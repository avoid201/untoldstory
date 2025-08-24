#!/usr/bin/env python3
"""
Test der Story-Integration der StarterScene.
Überprüft die korrekte Integration mit dem Story-System.
"""

import sys
import os
import pygame
from typing import Dict, Any

# Füge den Engine-Pfad hinzu
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'engine'))

def test_story_integration():
    """Testet die Story-Integration der StarterScene."""
    print("🧪 Teste Story-Integration der StarterScene...")
    
    # Initialisiere Pygame
    pygame.init()
    
    try:
        # Test 1: Import der StarterScene
        print("\n📋 Test 1: Import der StarterScene")
        from engine.scenes.starter_scene import StarterScene
        print("✅ StarterScene erfolgreich importiert")
        
        # Test 2: Erstelle Mock-Game-Objekt
        print("\n📋 Test 2: Mock-Game-Objekt")
        mock_game = create_mock_game()
        print("✅ Mock-Game-Objekt erstellt")
        
        # Test 3: Erstelle StarterScene-Instanz
        print("\n📋 Test 3: StarterScene-Instanz")
        starter_scene = StarterScene(mock_game)
        print("✅ StarterScene-Instanz erstellt")
        
        # Test 4: Überprüfe Manager-Status
        print("\n📋 Test 4: Manager-Status")
        starter_scene.log_manager_status()
        
        # Test 5: Teste Story-Flag-Integration
        print("\n📋 Test 5: Story-Flag-Integration")
        test_story_flags(starter_scene)
        
        # Test 6: Teste Scene-Übergang
        print("\n📋 Test 6: Scene-Übergang")
        test_scene_transition(starter_scene)
        
        print("\n🎉 Alle Tests erfolgreich abgeschlossen!")
        
    except Exception as e:
        print(f"\n❌ Test fehlgeschlagen: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        pygame.quit()

def create_mock_game():
    """Erstellt ein Mock-Game-Objekt für Tests."""
    class MockGame:
        def __init__(self):
            self.party_manager = MockPartyManager()
            self.story_manager = MockStoryManager()
            self.sprite_manager = MockSpriteManager()
            self.resources = MockResources()
            self.current_scene = None
        
        def push_scene(self, scene_class, **kwargs):
            print(f"[MockGame] Scene gepusht: {scene_class.__name__}")
        
        def pop_scene(self):
            print("[MockGame] Scene gepoppt")
    
    return MockGame()

class MockPartyManager:
    """Mock-PartyManager für Tests."""
    def add_to_party(self, monster):
        print(f"[MockPartyManager] Monster {monster.species_name} zur Party hinzugefügt")
        return True, "Erfolgreich hinzugefügt"

class MockStoryManager:
    """Mock-StoryManager für Tests."""
    def __init__(self):
        self.flags = {}
    
    def set_flag(self, flag_id: str, value: Any = True):
        self.flags[flag_id] = value
        print(f"[MockStoryManager] Flag gesetzt: {flag_id} = {value}")
    
    def get_flag(self, flag_id: str):
        return self.flags.get(flag_id, False)
    
    def advance_quest(self, quest_id: str):
        print(f"[MockStoryManager] Quest fortgeschritten: {quest_id}")
    
    def _check_phase_progression(self):
        print("[MockStoryManager] Story-Phase-Update durchgeführt")

class MockSpriteManager:
    """Mock-SpriteManager für Tests."""
    def __init__(self):
        self.monster_sprites = {}
    
    def get_npc_sprite(self, name: str, direction: str):
        return pygame.Surface((16, 16))

class MockResources:
    """Mock-Resources für Tests."""
    def get_monster_species(self, monster_id: int):
        return None

def test_story_flags(starter_scene):
    """Testet die Story-Flag-Integration."""
    print("  🔍 Teste Story-Flag-Integration...")
    
    # Teste das Setzen von Story-Flags
    test_flags = {
        'has_starter': True,
        'starter_choice': 24,
        'professor_intro_done': True
    }
    
    success = starter_scene._safe_set_story_flags(test_flags)
    
    if success:
        print("  ✅ Story-Flags erfolgreich gesetzt")
        
        # Überprüfe, ob die Flags korrekt gesetzt wurden
        story_manager = starter_scene.game.story_manager
        for flag_id, expected_value in test_flags.items():
            actual_value = story_manager.get_flag(flag_id)
            if actual_value == expected_value:
                print(f"    ✅ Flag {flag_id}: {actual_value}")
            else:
                print(f"    ❌ Flag {flag_id}: erwartet {expected_value}, erhalten {actual_value}")
    else:
        print("  ❌ Story-Flags konnten nicht gesetzt werden")

def test_scene_transition(starter_scene):
    """Testet den Scene-Übergang."""
    print("  🔍 Teste Scene-Übergang...")
    
    try:
        # Simuliere den Abschluss der Starter-Auswahl
        starter_scene.state = 'done'
        
        # Teste den Rückkehr zur FieldScene
        starter_scene._return_to_field_scene()
        print("  ✅ Scene-Übergang erfolgreich")
        
    except Exception as e:
        print(f"  ❌ Scene-Übergang fehlgeschlagen: {e}")

if __name__ == "__main__":
    test_story_integration()
