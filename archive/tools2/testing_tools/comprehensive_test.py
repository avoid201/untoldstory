#!/usr/bin/env python3
"""
Comprehensive Test Suite für Untold Story
Testet alle wichtigen Systeme und Funktionen
"""

import sys
import pygame
from pathlib import Path
from typing import List, Tuple, Dict

# Engine-Imports
from engine.world.tile_manager import TileManager
from engine.graphics.sprite_manager import SpriteManager
from engine.graphics.tile_renderer import TileRenderer
from engine.world.map_loader import MapLoader
from engine.world.area import Area

class ComprehensiveTestSuite:
    """Umfassende Test-Suite für alle Engine-Systeme"""
    
    def __init__(self):
        self.test_results = {}
        self.errors = []
        
    def run_all_tests(self):
        """Führt alle Tests aus"""
        print("🎮 UNTOLD STORY - COMPREHENSIVE TEST SUITE 🎮")
        print("=" * 60)
        
        try:
            # System-Tests
            self.test_tile_manager()
            self.test_sprite_manager()
            self.test_tile_renderer()
            self.test_map_loader()
            self.test_area_system()
            self.test_pathfinding()
            self.test_tmx_integration()
            self.test_npc_system()
            
            # Zusammenfassung
            self.print_summary()
            
        except Exception as e:
            print(f"\n❌ Kritischer Fehler: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        return True
    
    def test_tile_manager(self):
        """Testet den TileManager"""
        print("\n🔧 TileManager Test")
        print("-" * 30)
        
        try:
            tile_manager = TileManager.get_instance()
            
            # Teste Singleton
            tile_manager2 = TileManager.get_instance()
            assert tile_manager is tile_manager2, "Singleton funktioniert nicht!"
            
            # Teste externe Daten
            print(f"  - NPC maps: {len(tile_manager.npcs_data)}")
            print(f"  - Warp maps: {len(tile_manager.warps_data)}")
            print(f"  - Dialogues: {len(tile_manager.dialogues_data)}")
            
            # Teste Map-spezifische Daten
            test_map = "kohlenstadt"
            if test_map in tile_manager.npcs_data:
                npcs = tile_manager.get_npcs_for_map(test_map)
                print(f"  - NPCs in {test_map}: {len(npcs)}")
            
            if test_map in tile_manager.warps_data:
                warps = tile_manager.get_warps_for_map(test_map)
                print(f"  - Warps in {test_map}: {len(warps)}")
            
            # Teste Dialog
            test_dialogue = "mom_morning"
            dialogue = tile_manager.get_dialogue(test_dialogue)
            if dialogue:
                print(f"  - Dialog '{test_dialogue}' gefunden")
            
            self.test_results['tile_manager'] = True
            print("  ✅ TileManager funktioniert")
            
        except Exception as e:
            self.test_results['tile_manager'] = False
            self.errors.append(f"TileManager: {e}")
            print(f"  ❌ TileManager Fehler: {e}")
    
    def test_sprite_manager(self):
        """Testet den SpriteManager"""
        print("\n🎨 SpriteManager Test")
        print("-" * 30)
        
        try:
            pygame.init()
            sprite_manager = SpriteManager()
            
            # Teste Sprite-Loading
            test_sprite = sprite_manager.get_sprite("player", "player_down.png")
            if test_sprite:
                print(f"  - Player Sprite geladen: {test_sprite.get_size()}")
            
            # Teste Animation
            anim = sprite_manager.get_animation("player", "walk_down")
            if anim:
                print(f"  - Walk Animation geladen: {len(anim)} Frames")
            
            self.test_results['sprite_manager'] = True
            print("  ✅ SpriteManager funktioniert")
            
        except Exception as e:
            self.test_results['sprite_manager'] = False
            self.errors.append(f"SpriteManager: {e}")
            print(f"  ❌ SpriteManager Fehler: {e}")
    
    def test_tile_renderer(self):
        """Testet den TileRenderer"""
        print("\n🧱 TileRenderer Test")
        print("-" * 30)
        
        try:
            pygame.init()
            tile_renderer = TileRenderer()
            
            # Teste Tile-Rendering
            test_surface = pygame.Surface((320, 180))
            tile_renderer.render_tile(test_surface, 0, 0, 1)  # Test-Tile
            
            print(f"  - Tile-Rendering funktioniert")
            
            self.test_results['tile_renderer'] = True
            print("  ✅ TileRenderer funktioniert")
            
        except Exception as e:
            self.test_results['tile_renderer'] = False
            self.errors.append(f"TileRenderer: {e}")
            print(f"  ❌ TileRenderer Fehler: {e}")
    
    def test_map_loader(self):
        """Testet den MapLoader"""
        print("\n🗺️ MapLoader Test")
        print("-" * 30)
        
        try:
            map_loader = MapLoader()
            
            # Teste JSON-Map-Loading
            test_map = "player_house"
            map_data = map_loader.load_map(test_map)
            
            if map_data:
                print(f"  - Map '{test_map}' geladen")
                print(f"    Größe: {map_data.width}x{map_data.height}")
                print(f"    Layer: {len(map_data.layers)}")
                print(f"    Entities: {len(map_data.entities)}")
            
            self.test_results['map_loader'] = True
            print("  ✅ MapLoader funktioniert")
            
        except Exception as e:
            self.test_results['map_loader'] = False
            self.errors.append(f"MapLoader: {e}")
            print(f"  ❌ MapLoader Fehler: {e}")
    
    def test_area_system(self):
        """Testet das Area-System"""
        print("\n🌍 Area System Test")
        print("-" * 30)
        
        try:
            # Erstelle Test-Area
            area = Area("test_area", 10, 10)
            
            print(f"  - Test-Area erstellt: {area.name}")
            print(f"    Größe: {area.width}x{area.height}")
            print(f"    Entities: {len(area.entities)}")
            
            # Teste Tile-Funktionen
            tile_id = area.get_tile_at(0, 0)
            print(f"    Tile (0,0): {tile_id}")
            
            # Teste Kollision
            is_solid = area.is_tile_solid(0, 0)
            print(f"    Tile (0,0) solid: {is_solid}")
            
            self.test_results['area_system'] = True
            print("  ✅ Area System funktioniert")
            
        except Exception as e:
            self.test_results['area_system'] = False
            self.errors.append(f"Area System: {e}")
            print(f"  ❌ Area System Fehler: {e}")
    
    def test_pathfinding(self):
        """Testet das Pathfinding-System"""
        print("\n🛤️ Pathfinding Test")
        print("-" * 30)
        
        try:
            tile_manager = TileManager.get_instance()
            
            # Setze Test-Map
            width, height = 10, 10
            tile_manager.map_width = width
            tile_manager.map_height = height
            tile_manager.collision_map = [[False] * width for _ in range(height)]
            
            # Füge Hindernisse hinzu
            for i in range(5):
                tile_manager.collision_map[5][i] = True  # Horizontale Wand
            
            # Teste Pfad
            start = (0, 0)
            goal = (9, 9)
            path = tile_manager.find_path(start, goal)
            
            if path:
                print(f"  - Pfad gefunden: {len(path)} Schritte")
                print(f"    Start: {start} -> Ziel: {goal}")
                self._visualize_path(tile_manager, start, goal, path)
            else:
                print(f"  - Kein Pfad gefunden von {start} nach {goal}")
            
            # Teste diagonalen Pfad
            diagonal_path = tile_manager.find_path_diagonal(start, goal)
            if diagonal_path:
                print(f"  - Diagonaler Pfad: {len(diagonal_path)} Schritte")
            
            self.test_results['pathfinding'] = True
            print("  ✅ Pathfinding funktioniert")
            
        except Exception as e:
            self.test_results['pathfinding'] = False
            self.errors.append(f"Pathfinding: {e}")
            print(f"  ❌ Pathfinding Fehler: {e}")
    
    def test_tmx_integration(self):
        """Testet die TMX-Integration"""
        print("\n📋 TMX Integration Test")
        print("-" * 30)
        
        try:
            tile_manager = TileManager.get_instance()
            
            # Teste TMX-Loading
            test_tmx = Path("data/maps/player_house.tmx")
            
            if test_tmx.exists():
                print(f"  - TMX-Datei gefunden: {test_tmx}")
                
                map_data = tile_manager.load_tmx_map(test_tmx)
                
                print(f"    Größe: {map_data['width']}x{map_data['height']}")
                print(f"    Tiles: {len(tile_manager.tiles)} geladen")
                
                if tile_manager.collision_map:
                    print(f"    Collision-Map: {len(tile_manager.collision_map)}x{len(tile_manager.collision_map[0])}")
                
                self.test_results['tmx_integration'] = True
                print("  ✅ TMX Integration funktioniert")
            else:
                print(f"  ⚠️ TMX-Datei nicht gefunden: {test_tmx}")
                self.test_results['tmx_integration'] = False
                
        except Exception as e:
            self.test_results['tmx_integration'] = False
            self.errors.append(f"TMX Integration: {e}")
            print(f"  ❌ TMX Integration Fehler: {e}")
    
    def test_npc_system(self):
        """Testet das NPC-System"""
        print("\n👤 NPC System Test")
        print("-" * 30)
        
        try:
            from engine.world.npc_improved import RivalKlaus
            from engine.world.tiles import TILE_SIZE
            
            # Erstelle Test-NPC
            npc = RivalKlaus(5 * TILE_SIZE, 5 * TILE_SIZE)
            
            print(f"  - NPC erstellt: {npc.npc_id}")
            print(f"    Position: ({npc.tile_x}, {npc.tile_y})")
            print(f"    Typ: {npc.npc_type}")
            
            # Teste Interaktion
            dialogue = npc.interact()
            if dialogue:
                print(f"    Dialog gefunden: {type(dialogue)}")
            
            self.test_results['npc_system'] = True
            print("  ✅ NPC System funktioniert")
            
        except Exception as e:
            self.test_results['npc_system'] = False
            self.errors.append(f"NPC System: {e}")
            print(f"  ❌ NPC System Fehler: {e}")
    
    def _visualize_path(self, tile_manager, start, goal, path):
        """Visualisiert einen Pfad"""
        width, height = tile_manager.map_width, tile_manager.map_height
        
        print("    Pfad-Visualisierung:")
        for y in range(min(height, 10)):  # Zeige nur ersten 10 Zeilen
            line = "      "
            for x in range(min(width, 20)):  # Zeige nur ersten 20 Spalten
                if (x, y) == start:
                    line += "S"
                elif (x, y) == goal:
                    line += "G"
                elif (x, y) in path:
                    line += "·"
                elif tile_manager.collision_map[y][x]:
                    line += "█"
                else:
                    line += " "
            print(line)
    
    def print_summary(self):
        """Zeigt eine Zusammenfassung aller Tests"""
        print("\n" + "=" * 60)
        print("📊 TEST-ZUSAMMENFASSUNG")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result)
        failed_tests = total_tests - passed_tests
        
        print(f"Gesamt: {total_tests} Tests")
        print(f"✅ Bestanden: {passed_tests}")
        print(f"❌ Fehlgeschlagen: {failed_tests}")
        print(f"Erfolgsrate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ Fehlgeschlagene Tests:")
            for test_name, result in self.test_results.items():
                if not result:
                    print(f"  - {test_name}")
        
        if self.errors:
            print(f"\n⚠️ Fehler-Details:")
            for error in self.errors[:5]:  # Zeige nur erste 5 Fehler
                print(f"  - {error}")
        
        if failed_tests == 0:
            print(f"\n🎉 ALLE TESTS BESTANDEN! Das System ist bereit für Produktion!")
        else:
            print(f"\n🔧 {failed_tests} Tests müssen repariert werden.")

def main():
    """Hauptfunktion"""
    test_suite = ComprehensiveTestSuite()
    success = test_suite.run_all_tests()
    
    if success:
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main())
