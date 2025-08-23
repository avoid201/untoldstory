#!/usr/bin/env python3
"""
Gefixter Test für TMX GID Loading
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import pygame
import xml.etree.ElementTree as ET


def test_fixed_parsing():
    """Testet das korrekte Parsing und Rendering"""
    
    print("🎮 TMX Fixed Parsing Test")
    print("=" * 60)
    
    # Initialisiere pygame
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption("Fixed Parsing Test")
    clock = pygame.time.Clock()
    
    # Initialisiere SpriteManager - aber NUR für player_house!
    from engine.graphics.sprite_manager import SpriteManager
    
    sprite_manager = SpriteManager.get()
    
    # Initialisiere GID-Mapping
    sprite_manager.gid_to_surface = {}
    sprite_manager._loaded_tilesets = set()
    
    # Lade NUR player_house Tilesets
    print("\n1️⃣ Lade NUR player_house Tilesets...")
    tmx_path = Path("data/maps/player_house.tmx")
    sprite_manager.load_tmx_tilesets(tmx_path)
    
    print(f"✅ GIDs geladen: {len(sprite_manager.gid_to_surface)}")
    if sprite_manager.gid_to_surface:
        print(f"   GIDs: {sorted(sprite_manager.gid_to_surface.keys())}")
    
    # Parse Map mit FIXEM Parsing
    print("\n2️⃣ Parse player_house Map...")
    tree = ET.parse(tmx_path)
    root = tree.getroot()
    
    width = int(root.get('width', 0))
    height = int(root.get('height', 0))
    print(f"Map-Größe: {width}x{height}")
    
    # Parse Layer RICHTIG
    layers = []
    for layer_elem in root.findall('layer'):
        layer_name = layer_elem.get('name', 'unnamed')
        data_elem = layer_elem.find('data')
        
        # FIX: Prüfe ob Element existiert, nicht ob es "truthy" ist
        if data_elem is not None and data_elem.get('encoding') == 'csv':
            csv_text = data_elem.text.strip()
            layer_data = []
            
            for line in csv_text.split('\n'):
                if line.strip():
                    row = []
                    for tile_str in line.split(','):
                        tile_str = tile_str.strip()
                        if tile_str and tile_str != '':
                            try:
                                gid = int(tile_str)
                                row.append(gid)
                            except ValueError:
                                pass
                    if row:
                        layer_data.append(row)
            
            if layer_data:
                layers.append((layer_name, layer_data))
                print(f"✅ Layer geladen: {layer_name} ({len(layer_data)}x{len(layer_data[0])})")
                
                # Zeige verwendete GIDs
                used_gids = set()
                for row in layer_data:
                    for gid in row:
                        if gid > 0:
                            used_gids.add(gid)
                if used_gids:
                    print(f"   Verwendete GIDs: {sorted(used_gids)}")
    
    if not layers:
        print("❌ Keine Layer gefunden!")
        return
    
    # Rendere Map
    print("\n3️⃣ Rendere Map...")
    scale = 3
    
    running = True
    show_grid = False
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_g:
                    show_grid = not show_grid
        
        screen.fill((30, 30, 40))
        
        # Rendere Layer
        offset_x = (640 - width * 16 * scale) // 2
        offset_y = (480 - height * 16 * scale) // 2
        
        tiles_rendered = 0
        missing_gids = set()
        
        for layer_name, layer_data in layers:
            for y in range(len(layer_data)):
                for x in range(len(layer_data[y])):
                    gid = layer_data[y][x]
                    
                    if gid == 0:
                        continue
                    
                    # Hole Tile
                    tile = sprite_manager.get_tile_by_gid(gid)
                    
                    if tile:
                        # Skaliere und zeichne
                        scaled = pygame.transform.scale(tile, (16 * scale, 16 * scale))
                        pos = (offset_x + x * 16 * scale, offset_y + y * 16 * scale)
                        screen.blit(scaled, pos)
                        tiles_rendered += 1
                    else:
                        missing_gids.add(gid)
                        # Pink placeholder
                        pos = (offset_x + x * 16 * scale, offset_y + y * 16 * scale)
                        pygame.draw.rect(screen, (255, 0, 255), 
                                       (pos[0], pos[1], 16 * scale, 16 * scale))
        
        # Grid
        if show_grid:
            for i in range(width + 1):
                x = offset_x + i * 16 * scale
                pygame.draw.line(screen, (100, 100, 100), (x, offset_y), 
                               (x, offset_y + height * 16 * scale), 1)
            for i in range(height + 1):
                y = offset_y + i * 16 * scale
                pygame.draw.line(screen, (100, 100, 100), (offset_x, y), 
                               (offset_x + width * 16 * scale, y), 1)
        
        # Info
        font = pygame.font.Font(None, 24)
        texts = [
            f"player_house.tmx",
            f"Tiles: {tiles_rendered}/{width*height*len(layers)}",
            f"GIDs im Cache: {len(sprite_manager.gid_to_surface)}",
            f"[G] Grid: {'AN' if show_grid else 'AUS'}",
            "[ESC] Beenden"
        ]
        if missing_gids:
            texts.insert(3, f"Fehlende GIDs: {sorted(missing_gids)}")
        
        for i, text in enumerate(texts):
            color = (255, 255, 255) if "Fehlende" not in text else (255, 100, 100)
            text_surf = font.render(text, True, color)
            screen.blit(text_surf, (10, 10 + i * 25))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    print("\n✅ Test beendet")


if __name__ == "__main__":
    test_fixed_parsing()
