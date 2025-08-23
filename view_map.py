#!/usr/bin/env python3
"""
TMX Map Viewer für macOS
Zeigt die player_house Map mit korrektem Rendering
"""

import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import pygame
import xml.etree.ElementTree as ET
from engine.graphics.sprite_manager import SpriteManager


def load_and_display_map():
    """Lade und zeige die player_house Map"""
    
    # Initialisiere pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Untold Story - Player House")
    clock = pygame.time.Clock()
    
    print("🎮 Lade player_house Map...")
    
    # Initialisiere SpriteManager
    sprite_manager = SpriteManager.get()
    
    # Lade alle TMX Tilesets
    tmx_path = Path("data/maps/player_house.tmx")
    sprite_manager.load_tmx_tilesets(tmx_path)
    
    # Parse Map
    tree = ET.parse(tmx_path)
    root = tree.getroot()
    
    width = int(root.get('width', 0))
    height = int(root.get('height', 0))
    tile_size = 16
    
    # Lade Layer
    layers = []
    for layer_elem in root.findall('layer'):
        layer_name = layer_elem.get('name', 'unnamed')
        data_elem = layer_elem.find('data')
        
        if data_elem and data_elem.get('encoding') == 'csv':
            csv_text = data_elem.text.strip()
            layer_data = []
            
            for line in csv_text.split('\n'):
                if line.strip():
                    row = [int(x.strip()) for x in line.split(',') if x.strip()]
                    layer_data.append(row)
            
            layers.append((layer_name, layer_data))
            print(f"✅ Layer geladen: {layer_name}")
    
    # Zeige GID-Info
    if hasattr(sprite_manager, 'gid_to_surface'):
        print(f"📊 {len(sprite_manager.gid_to_surface)} GIDs im Cache")
    
    # Skalierungsfaktor für bessere Sichtbarkeit
    scale = 4
    
    # Game Loop
    running = True
    show_grid = False
    show_info = True
    
    print("\n🕹️ Steuerung:")
    print("  G - Grid an/aus")
    print("  I - Info an/aus")
    print("  ESC - Beenden")
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_g:
                    show_grid = not show_grid
                elif event.key == pygame.K_i:
                    show_info = not show_info
        
        # Clear screen
        screen.fill((50, 50, 50))
        
        # Berechne zentrierte Position
        map_width = width * tile_size * scale
        map_height = height * tile_size * scale
        offset_x = (800 - map_width) // 2
        offset_y = (600 - map_height) // 2
        
        # Rendere alle Layer
        for layer_name, layer_data in layers:
            for y in range(len(layer_data)):
                for x in range(len(layer_data[y])):
                    gid = layer_data[y][x]
                    
                    if gid == 0:
                        continue
                    
                    # Hole Tile
                    tile_surface = sprite_manager.get_tile_by_gid(gid)
                    
                    if tile_surface:
                        # Skaliere Tile
                        scaled_tile = pygame.transform.scale(
                            tile_surface, 
                            (tile_size * scale, tile_size * scale)
                        )
                        
                        # Position
                        pos_x = offset_x + x * tile_size * scale
                        pos_y = offset_y + y * tile_size * scale
                        
                        screen.blit(scaled_tile, (pos_x, pos_y))
                    else:
                        # Platzhalter für fehlende Tiles
                        pos_x = offset_x + x * tile_size * scale
                        pos_y = offset_y + y * tile_size * scale
                        
                        placeholder = pygame.Surface((tile_size * scale, tile_size * scale))
                        placeholder.fill((255, 0, 255))
                        pygame.draw.rect(placeholder, (0, 0, 0), 
                                       placeholder.get_rect(), 2)
                        
                        # GID-Text
                        font = pygame.font.Font(None, 12)
                        text = font.render(str(gid), True, (255, 255, 255))
                        text_rect = text.get_rect(center=(tile_size * scale // 2, 
                                                         tile_size * scale // 2))
                        placeholder.blit(text, text_rect)
                        
                        screen.blit(placeholder, (pos_x, pos_y))
        
        # Grid
        if show_grid:
            for x in range(width + 1):
                pygame.draw.line(screen, (100, 100, 100),
                               (offset_x + x * tile_size * scale, offset_y),
                               (offset_x + x * tile_size * scale, offset_y + map_height), 1)
            for y in range(height + 1):
                pygame.draw.line(screen, (100, 100, 100),
                               (offset_x, offset_y + y * tile_size * scale),
                               (offset_x + map_width, offset_y + y * tile_size * scale), 1)
        
        # Info
        if show_info:
            font = pygame.font.Font(None, 24)
            info_texts = [
                "Player House",
                f"Größe: {width}x{height}",
                f"[G] Grid: {'AN' if show_grid else 'AUS'}",
                f"[I] Info: AN",
                "[ESC] Beenden"
            ]
            
            for i, text in enumerate(info_texts):
                text_surface = font.render(text, True, (255, 255, 255))
                screen.blit(text_surface, (10, 10 + i * 25))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()


if __name__ == "__main__":
    print("🏠 Untold Story - Player House Viewer")
    print("=" * 50)
    
    try:
        load_and_display_map()
    except Exception as e:
        print(f"❌ Fehler: {e}")
        import traceback
        traceback.print_exc()
