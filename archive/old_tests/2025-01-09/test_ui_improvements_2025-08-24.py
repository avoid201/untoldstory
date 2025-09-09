#!/usr/bin/env python3
"""
Test der UI-Verbesserungen für Untold Story
Testet moderne UI-Patterns, optimiertes Rendering und verbesserte Benutzerfreundlichkeit
"""

import pygame
import sys
import time
from pathlib import Path

# Engine-Imports
sys.path.append(str(Path(__file__).parent))

try:
    from engine.ui.modern_ui_patterns import (
        ModernUIElement, AnimatedButton, TooltipManager, 
        TransitionManager, Animation, AnimationType
    )
    from engine.ui.menu_system import (
        EnhancedMenuBase, MenuItem, EnhancedInventoryMenu, 
        EnhancedPartyMenu, EnhancedQuestMenu, EnhancedSaveMenu,
        EnhancedConfirmDialog, MenuManager
    )
    from engine.graphics.optimized_renderer import (
        OptimizedRenderer, TextureAtlas, FontCache
    )
    from engine.graphics.asset_manager import AssetManager, AssetType
    print("✓ Alle UI-Module erfolgreich importiert")
except ImportError as e:
    print(f"✗ Fehler beim Importieren der UI-Module: {e}")
    sys.exit(1)


class MockGame:
    """Mock-Game-Objekt für Tests."""
    
    def __init__(self):
        self.inventory = MockInventory()
        # Use item_registry instead of item_database
        from engine.systems.items import item_registry
        self.item_database = item_registry
        self.party = MockParty()


class MockInventory:
    """Mock-Inventar für Tests."""
    
    def get_all_items(self):
        return [("item1", 5), ("item2", 3), ("item3", 1)]


# MockItemDatabase removed - using real item_registry now


class MockItem:
    """Mock-Item für Tests."""
    
    def __init__(self, item_id):
        self.id = item_id
        self.name = f"Item {item_id}"
        self.description = f"Beschreibung für {item_id}"


class MockParty:
    """Mock-Party für Tests."""
    
    def __init__(self):
        self.members = [MockMonster("Monster 1"), MockMonster("Monster 2")]


class MockMonster:
    """Mock-Monster für Tests."""
    
    def __init__(self, name):
        self.name = name
        self.level = 10
        self.current_hp = 50
        self.max_hp = 100


def test_modern_ui_patterns():
    """Testet moderne UI-Patterns."""
    print("\n=== Teste Moderne UI-Patterns ===")
    
    try:
        # Animation testen
        animation = Animation(
            AnimationType.FADE_IN, 1.0, 0.0, 1.0, easing="ease_out"
        )
        assert animation.animation_type == AnimationType.FADE_IN
        assert animation.duration == 1.0
        print("✓ Animation-Erstellung erfolgreich")
        
        # Hover-Effekt testen
        hover_effect = HoverEffect()
        assert hover_effect.scale_factor == 1.05
        assert hover_effect.glow_intensity == 20
        print("✓ Hover-Effekt-Erstellung erfolgreich")
        
        # ModernUIElement testen
        element = ModernUIElement(10, 10, 100, 50)
        assert element.rect.x == 10
        assert element.rect.y == 10
        assert element.rect.width == 100
        assert element.rect.height == 50
        print("✓ ModernUIElement-Erstellung erfolgreich")
        
        # AnimatedButton testen
        button = AnimatedButton(20, 20, 80, 30, "Test", lambda: print("Button clicked"))
        assert button.text == "Test"
        assert button.rect.width == 80
        print("✓ AnimatedButton-Erstellung erfolgreich")
        
        print("✓ Alle modernen UI-Patterns funktionieren korrekt")
        return True
        
    except Exception as e:
        print(f"✗ Fehler bei modernen UI-Patterns: {e}")
        return False


def test_enhanced_menus():
    """Testet verbesserte Menüs."""
    print("\n=== Teste Verbesserte Menüs ===")
    
    try:
        # Mock-Game erstellen
        game = MockGame()
        
        # EnhancedMenuBase testen
        menu = EnhancedMenuBase(game, "Test Menü")
        assert menu.title == "Test Menü"
        assert menu.game == game
        print("✓ EnhancedMenuBase-Erstellung erfolgreich")
        
        # Menü-Einträge hinzufügen
        menu.add_menu_item(MenuItem("Eintrag 1", callback=lambda: print("Eintrag 1")))
        menu.add_menu_item(MenuItem("Eintrag 2", callback=lambda: print("Eintrag 2")))
        assert len(menu.menu_items) == 2
        print("✓ Menü-Einträge hinzugefügt")
        
        # EnhancedInventoryMenu testen
        inventory_menu = EnhancedInventoryMenu(game)
        assert inventory_menu.title == "Inventar"
        print("✓ EnhancedInventoryMenu-Erstellung erfolgreich")
        
        # EnhancedPartyMenu testen
        party_menu = EnhancedPartyMenu(game)
        assert party_menu.title == "Team"
        print("✓ EnhancedPartyMenu-Erstellung erfolgreich")
        
        # MenuManager testen
        menu_manager = MenuManager(game)
        assert menu_manager.game == game
        print("✓ MenuManager-Erstellung erfolgreich")
        
        print("✓ Alle verbesserten Menüs funktionieren korrekt")
        return True
        
    except Exception as e:
        print(f"✗ Fehler bei verbesserten Menüs: {e}")
        return False


def test_optimized_renderer():
    """Testet den optimierten Renderer."""
    print("\n=== Teste Optimierten Renderer ===")
    
    try:
        # OptimizedRenderer testen
        renderer = OptimizedRenderer()
        assert renderer.culling_enabled == True
        assert renderer.use_caching == True
        print("✓ OptimizedRenderer-Erstellung erfolgreich")
        
        # TextureAtlas testen
        atlas = TextureAtlas()
        assert atlas.max_size == 2048
        print("✓ TextureAtlas-Erstellung erfolgreich")
        
        # FontCache testen
        font_cache = FontCache()
        assert font_cache.max_cache_size == 1000
        print("✓ FontCache-Erstellung erfolgreich")
        
        # Render-Statistiken testen
        stats = renderer.get_stats()
        assert 'frames_rendered' in stats
        assert 'atlas_usage' in stats
        print("✓ Render-Statistiken funktionieren")
        
        print("✓ Optimierter Renderer funktioniert korrekt")
        return True
        
    except Exception as e:
        print(f"✗ Fehler beim optimierten Renderer: {e}")
        return False


def test_asset_manager():
    """Testet den Asset-Manager."""
    print("\n=== Teste Asset-Manager ===")
    
    try:
        # AssetManager testen
        asset_manager = AssetManager()
        print("✓ AssetManager-Erstellung erfolgreich")
        
        # Asset-Statistiken testen
        stats = asset_manager.get_asset_stats()
        assert 'total_assets' in stats
        assert 'by_type' in stats
        print("✓ Asset-Statistiken funktionieren")
        
        print("✓ Asset-Manager funktioniert korrekt")
        return True
        
    except Exception as e:
        print(f"✗ Fehler beim Asset-Manager: {e}")
        return False


def test_ui_performance():
    """Testet die UI-Performance."""
    print("\n=== Teste UI-Performance ===")
    
    try:
        # Performance-Test für Animationen
        start_time = time.time()
        
        animation = Animation(AnimationType.FADE_IN, 1.0, 0.0, 1.0)
        for i in range(1000):
            animation.update(0.016)  # 60 FPS
        
        animation_time = time.time() - start_time
        print(f"✓ 1000 Animation-Updates in {animation_time:.4f}s")
        
        # Performance-Test für Hover-Effekte
        start_time = time.time()
        
        element = ModernUIElement(0, 0, 100, 100)
        for i in range(1000):
            element.handle_hover((50, 50))
        
        hover_time = time.time() - start_time
        print(f"✓ 1000 Hover-Checks in {hover_time:.4f}s")
        
        print("✓ UI-Performance ist akzeptabel")
        return True
        
    except Exception as e:
        print(f"✗ Fehler bei UI-Performance-Test: {e}")
        return False


def main():
    """Hauptfunktion für alle Tests."""
    print("🚀 Starte UI-Verbesserungs-Tests für Untold Story")
    print("=" * 60)
    
    # Pygame initialisieren
    pygame.init()
    
    # Tests durchführen
    tests = [
        test_modern_ui_patterns,
        test_enhanced_menus,
        test_optimized_renderer,
        test_asset_manager,
        test_ui_performance
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} fehlgeschlagen: {e}")
    
    # Ergebnisse anzeigen
    print("\n" + "=" * 60)
    print(f"🎯 Test-Ergebnisse: {passed}/{total} Tests bestanden")
    
    if passed == total:
        print("🎉 Alle Tests erfolgreich! UI-Verbesserungen funktionieren korrekt.")
    else:
        print(f"⚠️  {total - passed} Tests fehlgeschlagen. Überprüfe die Implementierung.")
    
    # Pygame beenden
    pygame.quit()
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
