#!/usr/bin/env python3
"""
Simple Visual TMX Test - Einfacher visueller Test
"""

import pygame
import sys
from pathlib import Path

def visual_test():
    """Einfacher visueller Test des TMX-Systems"""
    
    print("\n🎮 STARTE VISUELLEN TMX-TEST...")
    
    # Pygame initialisieren
    pygame.init()
    screen = pygame.display.set_mode((320, 240))
    pygame.display.set_caption("TMX Visual Test")
    clock = pygame.time.Clock()
    
    # Lade Tileset-Bilder direkt
    tiles_loaded = []
    tileset_path = Path("assets/gfx/tiles/tilesets")
    
    # Lade tiles_interior_preview.png
    interior_path = tileset_path / "tiles_interior_preview.png"
    building_path = tileset_path / "tiles_building_preview.png"
    
    interior_tiles = None
    building_tiles = None
    
    if interior_path.exists():
        interior_tiles = pygame.image.load(str(interior_path)).convert_alpha()
        print(f"✅ Geladen: {interior_path.name}")
    else:
        print(f"❌ Nicht gefunden: {interior_path}")
    
    if building_path.exists():
        building_tiles = pygame.image.load(str(building_path)).convert_alpha()
        print(f"✅ Geladen: {building_path.name}")
    else:
        print(f"❌ Nicht gefunden: {building_path}")
    
    # Map-Daten aus player_house.tmx (hardcoded für Test)
    # Layer 1: Boden
    map_layer1 = [
        [14,14,14,14,14,14,14,14,14],
        [14,13,13,13,13,13,13,13,14],
        [14,13,13,13,13,13,13,13,14],
        [14,13,13,13,13,13,13,13,14],
        [14,13,13,13,13,13,13,13,14],
        [14,14,14,15,15,14,14,14,14]
    ]
    
    # Layer 2: Objekte
    map_layer2 = [
        [0,0,6,0,0,0,6,0,0],
        [0,21,16,17,0,0,0,18,0],
        [0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,19,21,0],
        [0,0,0,0,0,0,0,0,0]
    ]
    
    print("\n🎮 STEUERUNG:")
    print("   ESC - Beenden")
    print("   SPACE - Info umschalten")
    print("\nFenster sollte sich öffnen...")
    
    running = True
    show_info = True
    font = pygame.font.Font(None, 14)
    
    while running:
        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    show_info = not show_info
        
        # Clear
        screen.fill((50, 50, 60))
        
        # Rendere Map (einfaches Rendering)
        tile_size = 16
        
        # Rendere Layer 1
        for y, row in enumerate(map_layer1):
            for x, gid in enumerate(row):
                if gid > 0:
                    # Bestimme welches Tileset
                    if gid >= 13:  # tiles_interior1 (firstgid=13)
                        if interior_tiles:
                            tile_id = gid - 13
                            src_x = (tile_id % 12) * 16
                            src_y = (tile_id // 12) * 16
                            screen.blit(interior_tiles, 
                                      (x * tile_size, y * tile_size),
                                      (src_x, src_y, 16, 16))
                    elif gid >= 1:  # tiles_building1 (firstgid=1)
                        if building_tiles:
                            tile_id = gid - 1
                            src_x = (tile_id % 12) * 16
                            src_y = (tile_id // 12) * 16
                            screen.blit(building_tiles,
                                      (x * tile_size, y * tile_size),
                                      (src_x, src_y, 16, 16))
        
        # Rendere Layer 2
        for y, row in enumerate(map_layer2):
            for x, gid in enumerate(row):
                if gid > 0:
                    if gid >= 13:  # tiles_interior1
                        if interior_tiles:
                            tile_id = gid - 13
                            src_x = (tile_id % 12) * 16
                            src_y = (tile_id // 12) * 16
                            screen.blit(interior_tiles,
                                      (x * tile_size, y * tile_size),
                                      (src_x, src_y, 16, 16))
                    elif gid >= 1:  # tiles_building1
                        if building_tiles:
                            tile_id = gid - 1
                            src_x = (tile_id % 12) * 16
                            src_y = (tile_id // 12) * 16
                            screen.blit(building_tiles,
                                      (x * tile_size, y * tile_size),
                                      (src_x, src_y, 16, 16))
        
        # Info-Overlay
        if show_info:
            info_text = [
                "TMX Visual Test",
                "Map: player_house (9x6)",
                f"Tilesets: {2 if interior_tiles and building_tiles else 1}",
                "SPACE: Info | ESC: Exit"
            ]
            
            y_pos = 5
            for line in info_text:
                text = font.render(line, True, (255, 255, 255))
                text_bg = pygame.Surface((text.get_width() + 4, text.get_height() + 2))
                text_bg.fill((0, 0, 0))
                text_bg.set_alpha(180)
                screen.blit(text_bg, (3, y_pos - 1))
                screen.blit(text, (5, y_pos))
                y_pos += 16
        
        # Update
        pygame.display.flip()
        clock.tick(60)
    
    print("\n✅ Test beendet!")
    pygame.quit()

if __name__ == "__main__":
    visual_test()
