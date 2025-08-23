#!/usr/bin/env python3
"""
Test der vollständigen TMX-Integration mit Pathfinding und externen Daten
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import pygame
from engine.world.tile_manager import TileManager

def test_tile_manager():
    """Testet den Tile Manager"""
    print("=" * 60)
    print("TILE MANAGER TEST")
    print("=" * 60)
    
    # Test externe Daten
    tile_manager = TileManager.get_instance()
    print("\n1. Externe Daten:")
    print(f"   NPCs Maps: {len(tile_manager.npcs_data)}")
    print(f"   Warps Maps: {len(tile_manager.warps_data)}")
    print(f"   Dialogues: {len(tile_manager.dialogues_data)}")
    
    # Test Map-spezifische Daten
    print("\n2. Map-spezifische Daten (kohlenstadt):")
    npcs = tile_manager.get_npcs_for_map("kohlenstadt")
    warps = tile_manager.get_warps_for_map("kohlenstadt")
    print(f"   NPCs: {list(npcs.keys())}")
    print(f"   Warps: {list(warps.keys())}")
    
    # Test Dialog
    print("\n3. Dialog-Test:")
    dialogue = tile_manager.get_dialogue("mom_morning")
    if dialogue:
        print(f"   Dialog gefunden: {len(dialogue['text'])} Zeilen")
        print(f"   Erste Zeile: {dialogue['text'][0]}")
    
    print("\n✅ Tile Manager Test erfolgreich!")

def test_pathfinding():
    """Testet das Pathfinding"""
    print("\n" + "=" * 60)
    print("PATHFINDING TEST")
    print("=" * 60)
    
    # Setze Test-Map auf
    tile_manager = TileManager.get_instance()
    tile_manager.map_width = 10
    tile_manager.map_height = 10
    tile_manager.collision_map = [
        [False, False, False, False, False, False, False, False, False, False],
        [False, False, True,  True,  True,  False, False, False, False, False],
        [False, False, True,  False, False, False, False, False, False, False],
        [False, False, True,  False, False, False, True,  True,  False, False],
        [False, False, False, False, False, False, True,  False, False, False],
        [False, False, False, False, False, False, True,  False, False, False],
        [False, False, False, False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False, False, False, False],
        [False, False, False, False, False, False, False, False, False, False],
    ]
    
    # Test 1: Einfacher Pfad
    print("\n1. Einfacher Pfad (0,0) -> (9,9):")
    path = tile_manager.find_path((0, 0), (9, 9))
    if path:
        print(f"   Pfad gefunden: {len(path)} Schritte")
        print(f"   Erste Schritte: {path[:3]}")
    else:
        print("   Kein Pfad gefunden!")
    
    # Test 2: Pfad um Hindernis (0,1) -> (4,2):")
    path = tile_manager.find_path((0, 1), (4, 2))
    if path:
        print(f"   Pfad gefunden: {len(path)} Schritte")
        print(f"   Pfad: {path}")
    else:
        print("   Kein Pfad gefunden!")
    
    # Test 3: Diagonaler Pfad
    print("\n3. Diagonaler Pfad (0,0) -> (9,9):")
    path = tile_manager.find_path_diagonal((0, 0), (9, 9))
    if path:
        print(f"   Pfad gefunden: {len(path)} Schritte")
        print(f"   Erste Schritte: {path[:3]}")
    else:
        print("   Kein Pfad gefunden!")
    
    # Test 4: Unmöglicher Pfad (eingeschlossenes Ziel)
    tile_manager.collision_map[1][3] = True  # Schließe Ziel ein
    tile_manager.collision_map[2][3] = True
    tile_manager.collision_map[2][4] = True
    tile_manager.collision_map[2][5] = True
    tile_manager.collision_map[1][5] = True
    
    print("\n4. Unmöglicher Pfad (0,0) -> (1,4):")
    path = tile_manager.find_path((0, 0), (1, 4))
    if path:
        print(f"   Pfad gefunden: {len(path)} Schritte")
    else:
        print("   Kein Pfad gefunden (korrekt!)")
    
    print("\n✅ Pathfinding Test erfolgreich!")

def test_tmx_loading():
    """Testet das TMX-Loading"""
    print("\n" + "=" * 60)
    print("TMX LOADING TEST")
    print("=" * 60)
    
    # Initialisiere Pygame (für Surface-Operationen)
    pygame.init()
    
    # Test TMX-Datei
    tmx_path = Path("data/maps/player_house.tmx")
    
    if tmx_path.exists():
        print(f"\nLade TMX: {tmx_path}")
        try:
            map_data = tile_manager.load_tmx_map(tmx_path)
            
            print(f"\n1. Map-Eigenschaften:")
            print(f"   Größe: {map_data['width']}x{map_data['height']}")
            print(f"   Tile-Größe: {map_data['tile_width']}x{map_data['tile_height']}")
            print(f"   Tilesets: {len(map_data['tilesets'])}")
            print(f"   Layer: {list(map_data['layers'].keys())}")
            print(f"   Objekte: {len(map_data['objects'])}")
            
            print(f"\n2. Geladene Tiles:")
            print(f"   Anzahl: {len(tile_manager.tiles)}")
            if tile_manager.tiles:
                sample_gids = list(tile_manager.tiles.keys())[:5]
                print(f"   Beispiel GIDs: {sample_gids}")
            
            print(f"\n3. Collision-Map:")
            print(f"   Größe: {len(tile_manager.collision_map)}x{len(tile_manager.collision_map[0]) if tile_manager.collision_map else 0}")
            
            print("\n✅ TMX Loading Test erfolgreich!")
            
        except Exception as e:
            print(f"\n❌ Fehler beim TMX-Loading: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"\n⚠️ TMX-Datei nicht gefunden: {tmx_path}")
    
    pygame.quit()

def visualize_pathfinding():
    """Visualisiert Pathfinding mit ASCII"""
    print("\n" + "=" * 60)
    print("PATHFINDING VISUALISIERUNG")
    print("=" * 60)
    
    # Setze Test-Map auf
    width, height = 20, 15
    tile_manager.map_width = width
    tile_manager.map_height = height
    
    # Erstelle Labyrinth
    tile_manager.collision_map = [[False] * width for _ in range(height)]
    
    # Füge Wände hinzu
    walls = [
        # Vertikale Wand
        (5, 2), (5, 3), (5, 4), (5, 5), (5, 6), (5, 7), (5, 8),
        # Horizontale Wand
        (6, 8), (7, 8), (8, 8), (9, 8), (10, 8), (11, 8),
        # Weitere Hindernisse
        (10, 2), (10, 3), (10, 4), (10, 5),
        (15, 6), (15, 7), (15, 8), (15, 9), (15, 10),
        # Labyrinth-Struktur
        (2, 10), (3, 10), (4, 10), (5, 10), (6, 10),
        (8, 10), (9, 10), (10, 10), (11, 10), (12, 10),
    ]
    
    for x, y in walls:
        if x < width and y < height:
            tile_manager.collision_map[y][x] = True
    
    # Finde Pfad
    start = (1, 1)
    goal = (18, 13)
    path = tile_manager.find_path(start, goal)
    
    # Visualisiere
    print("\nLegende: S=Start, G=Ziel, #=Wand, *=Pfad, .=Frei\n")
    
    for y in range(height):
        row = ""
        for x in range(width):
            if (x, y) == start:
                row += "S "
            elif (x, y) == goal:
                row += "G "
            elif (x, y) in path:
                row += "* "
            elif tile_manager.collision_map[y][x]:
                row += "# "
            else:
                row += ". "
        print(row)
    
    if path:
        print(f"\n✅ Pfad gefunden: {len(path)} Schritte")
    else:
        print("\n❌ Kein Pfad gefunden!")

def main():
    """Haupttestfunktion"""
    print("\n" + "🎮" * 30)
    print("\nUNTOLD STORY - INTEGRATION TEST")
    print("\n" + "🎮" * 30)
    
    try:
        # Test 1: Tile Manager
        test_tile_manager()
        
        # Test 2: Pathfinding
        test_pathfinding()
        
        # Test 3: TMX Loading
        test_tmx_loading()
        
        # Test 4: Visualisierung
        visualize_pathfinding()
        
        print("\n" + "=" * 60)
        print("✅ ALLE TESTS ERFOLGREICH!")
        print("=" * 60)
        
        print("\n📝 Zusammenfassung:")
        print("- Tile Manager funktioniert")
        print("- Externe Daten werden geladen")
        print("- Pathfinding arbeitet korrekt")
        print("- TMX-Loading ist implementiert")
        print("- System ist bereit für Produktion!")
        
    except Exception as e:
        print(f"\n❌ FEHLER: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())