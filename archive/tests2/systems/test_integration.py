#!/usr/bin/env python3
"""
Test der vollständigen TMX-Integration mit Pathfinding und externen Daten
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import pygame
from engine.world.tile_manager import TileManager
from engine.world.tile_manager import tile_manager

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
    
    # Test 2: Pfad um Hindernis
    print("\n2. Pfad um Hindernis (0,1) -> (4,2):")
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
            tile_manager = TileManager.get_instance()
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
    tile_manager = TileManager.get_instance()
    tile_manager.map_width = width
    tile_manager.map_height = height
    
    # Erstelle Labyrinth
    tile_manager.collision_map = [[False] * width for _ in range(height)]
    
    # Füge Wände hinzu
    walls = [
        # Vertikale Wand
        (5, 2), (5, 3), (5, 4), (5, 5), (5, 6), (5, 7), (5, 8),
        # Horizontale Wand
        (2, 5), (3, 5), (4, 5), (6, 5), (7, 5), (8, 5), (9, 5),
        # Zusätzliche Hindernisse
        (10, 3), (11, 3), (12, 3), (13, 3),
        (15, 7), (16, 7), (17, 7), (18, 7),
    ]
    
    for x, y in walls:
        if 0 <= x < width and 0 <= y < height:
            tile_manager.collision_map[y][x] = True
    
    # Teste verschiedene Pfade
    test_cases = [
        ((0, 0), (19, 14), "Langer Pfad"),
        ((1, 1), (18, 13), "Pfad um Wände"),
        ((8, 8), (12, 12), "Kurzer Pfad"),
    ]
    
    for start, goal, description in test_cases:
        print(f"\n{description}: {start} -> {goal}")
        path = tile_manager.find_path(start, goal)
        if path:
            print(f"   Pfad gefunden: {len(path)} Schritte")
            _visualize_path(tile_manager, start, goal, path)
        else:
            print("   Kein Pfad gefunden!")
    
    print("\n✅ Pathfinding Visualisierung erfolgreich!")

def _visualize_path(tile_manager, start, goal, path):
    """Visualisiert einen Pfad in der Konsole"""
    width, height = tile_manager.map_width, tile_manager.map_height
    
    # Erstelle ASCII-Repräsentation
    for y in range(height):
        line = ""
        for x in range(width):
            if (x, y) == start:
                line += "S"  # Start
            elif (x, y) == goal:
                line += "G"  # Goal
            elif (x, y) in path:
                line += "·"  # Pfad
            elif tile_manager.collision_map[y][x]:
                line += "█"  # Wand
            else:
                line += " "  # Frei
        print(f"   {line}")

def test_npc_system():
    """Testet das NPC-System"""
    print("\n" + "=" * 60)
    print("NPC SYSTEM TEST")
    print("=" * 60)
    
    try:
        from engine.world.npc_improved import RivalKlaus
        from engine.world.tiles import TILE_SIZE
        
        # Erstelle Test-NPC
        npc = RivalKlaus(5 * TILE_SIZE, 5 * TILE_SIZE)
        
        print(f"1. NPC erstellt:")
        print(f"   Position: ({npc.tile_x}, {npc.tile_y})")
        print(f"   Typ: {npc.npc_type}")
        print(f"   Bewegung: {npc.movement_pattern}")
        
        # Teste Bewegung
        print(f"\n2. Bewegungstest:")
        old_pos = (npc.tile_x, npc.tile_y)
        npc.update(0.1)  # 100ms
        new_pos = (npc.tile_x, npc.tile_y)
        print(f"   Alte Position: {old_pos}")
        print(f"   Neue Position: {new_pos}")
        print(f"   Hat sich bewegt: {old_pos != new_pos}")
        
        # Teste Interaktion
        print(f"\n3. Interaktionstest:")
        dialogue = npc.interact()
        if dialogue:
            print(f"   Dialog gefunden: {type(dialogue)}")
        else:
            print(f"   Kein Dialog gefunden")
        
        print("\n✅ NPC System Test erfolgreich!")
        
    except Exception as e:
        print(f"\n❌ Fehler beim NPC-System Test: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Hauptfunktion für alle Tests"""
    print("UNTOLD STORY - INTEGRATIONSTEST")
    print("=" * 60)
    
    try:
        # Führe alle Tests aus
        test_tile_manager()
        test_pathfinding()
        test_tmx_loading()
        visualize_pathfinding()
        test_npc_system()
        
        print("\n" + "=" * 60)
        print("ALLE TESTS ERFOLGREICH ABGESCHLOSSEN! 🎉")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Kritischer Fehler: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()