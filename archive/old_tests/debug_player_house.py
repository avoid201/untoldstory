#!/usr/bin/env python3
"""Debug-Tool für Player House TMX Loading"""

import sys
import os
from pathlib import Path
import pygame

# Projektpfad einrichten
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

def test_player_house_loading():
    """Testet das Laden der player_house Map"""
    print("=" * 60)
    print("🏠 PLAYER HOUSE LOADING TEST")
    print("=" * 60)
    
    # 1. Prüfe ob die Datei existiert
    tmx_path = PROJECT_ROOT / 'data' / 'maps' / 'player_house.tmx'
    print(f"\n1️⃣ TMX Datei Check:")
    print(f"   Pfad: {tmx_path}")
    print(f"   Existiert: {tmx_path.exists()}")
    
    if tmx_path.exists():
        print(f"   Größe: {tmx_path.stat().st_size} bytes")
        # Zeige erste Zeilen der TMX
        with open(tmx_path, 'r') as f:
            lines = f.readlines()[:5]
            print(f"   Erste Zeilen:")
            for line in lines:
                print(f"     {line.strip()}")
    
    # 2. Teste MapLoader
    print(f"\n2️⃣ MapLoader Test:")
    try:
        from engine.world.map_loader import MapLoader
        map_data = MapLoader.load_map("player_house")
        print(f"   ✅ Map erfolgreich geladen!")
        print(f"   Name: {map_data.name}")
        print(f"   Größe: {map_data.width}x{map_data.height}")
        print(f"   Tilesets: {len(map_data.tilesets)}")
        print(f"   Layers: {list(map_data.layers.keys())}")
    except Exception as e:
        print(f"   ❌ Fehler beim Laden: {e}")
        import traceback
        traceback.print_exc()
    
    # 3. Teste Area-Klasse
    print(f"\n3️⃣ Area Klasse Test:")
    try:
        from engine.world.area import Area
        area = Area("player_house")
        print(f"   ✅ Area erfolgreich erstellt!")
        print(f"   Name: {area.name}")
        print(f"   Map ID: {area.map_id}")
        print(f"   Größe: {area.width}x{area.height}")
        print(f"   TMX Pfad: {area.tmx_path}")
        print(f"   Hat map_data: {hasattr(area, 'map_data')}")
        print(f"   Hat layers: {hasattr(area, 'layers')}")
        print(f"   Hat layer_surfaces: {hasattr(area, 'layer_surfaces')}")
    except Exception as e:
        print(f"   ❌ Fehler bei Area: {e}")
        import traceback
        traceback.print_exc()
    
    # 4. Teste Field Scene Loading
    print(f"\n4️⃣ Field Scene Loading Test:")
    try:
        # Minimale pygame-Initialisierung
        pygame.init()
        
        # Erstelle minimales Game-Objekt
        class MockGame:
            def __init__(self):
                self.logical_size = (320, 180)
                self.sprite_manager = None
                
                # Story Manager Mock
                class MockStoryManager:
                    def get_flag(self, flag):
                        return False
                    def set_flag(self, flag, value):
                        pass
                
                # Party Manager Mock  
                class MockPartyManager:
                    class Party:
                        def is_empty(self):
                            return True
                        def get_conscious_members(self):
                            return []
                    
                    def __init__(self):
                        self.party = self.Party()
                
                self.story_manager = MockStoryManager()
                self.party_manager = MockPartyManager()
                
                # Resources Mock
                class MockResources:
                    def load_json(self, *args, **kwargs):
                        return []
                    def get_monster_species(self, species_id):
                        return None
                
                self.resources = MockResources()
        
        mock_game = MockGame()
        
        # SpriteManager initialisieren
        from engine.graphics.sprite_manager import SpriteManager
        from engine.world.tmx_init import initialize_tmx_support
        
        sprite_manager = SpriteManager.get()
        initialize_tmx_support()
        mock_game.sprite_manager = sprite_manager
        
        # Field Scene erstellen
        from engine.scenes.field_scene import FieldScene
        field_scene = FieldScene(mock_game)
        
        # Versuche Map zu laden
        field_scene.load_map("player_house")
        print(f"   ✅ Field Scene hat Map geladen!")
        print(f"   Current Area: {field_scene.current_area is not None}")
        if field_scene.current_area:
            print(f"   Area Name: {field_scene.current_area.name}")
            
    except Exception as e:
        print(f"   ❌ Fehler bei Field Scene: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pygame.quit()
    
    # 5. Überprüfe Tileset-Dateien
    print(f"\n5️⃣ Tileset Dateien Check:")
    tileset_dir = PROJECT_ROOT / 'assets' / 'gfx' / 'tiles' / 'tilesets'
    if tileset_dir.exists():
        tilesets = list(tileset_dir.glob('*.png'))
        print(f"   Gefunden: {len(tilesets)} Tileset-Bilder")
        for ts in tilesets[:5]:  # Zeige nur erste 5
            print(f"   - {ts.name}")
    else:
        print(f"   ❌ Tileset-Verzeichnis existiert nicht!")
    
    print("\n" + "=" * 60)
    print("TEST ABGESCHLOSSEN")
    print("=" * 60)

if __name__ == "__main__":
    test_player_house_loading()
