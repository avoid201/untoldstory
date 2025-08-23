#!/usr/bin/env python3
"""
Finaler Test für TMX GID Fix
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import pygame
import xml.etree.ElementTree as ET


def test_gid_fix():
    """Testet ob der GID-Fix funktioniert"""
    
    print("🎮 TMX GID Fix Test")
    print("=" * 60)
    
    # Initialisiere pygame
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption("GID Fix Test")
    clock = pygame.time.Clock()
    
    # Initialisiere Sprite System wie in main.py
    print("\n1️⃣ Initialisiere Sprite System...")
    from engine.graphics.sprite_manager import SpriteManager
    from engine.world.tmx_init import initialize_tmx_support
    
    sprite_manager = SpriteManager.get()
    
    # TMX-Support ZUERST
    print("2️⃣ Lade TMX-Tilesets...")
    initialize_tmx_support()
    
    # Dann den Rest
    sprite_manager._ensure_loaded()
    
    # Status
    if hasattr(sprite_manager, 'gid_to_surface'):
        print(f"\n✅ GIDs geladen: {len(sprite_manager.gid_to_surface)}")
        if sprite_manager.gid_to_surface:
            print(f"   Verfügbare GIDs: {sorted(sprite_manager.gid_to_surface.keys())}")
    else:
        print("\n❌ Keine GIDs geladen!")
        return
    
    # Lade Map-Daten
    print("\n3️⃣ Lade player_house Map...")
    tmx_path = Path("data/maps/player_house.tmx")
    tree = ET.parse(tmx_path)
    root = tree.getroot()
    
    width = int(root.get('width', 0))
    height = int(root.get('height', 0))
    
    # Parse Layer
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
    
    print(f"   Layers: {[name for name, _ in layers]}")
    
    # Rendere Map
    print("\n4️⃣ Rendere Map...")
    scale = 3
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
        
        screen.fill((30, 30, 40))
        
        # Rendere Layer
        offset_x = (640 - width * 16 * scale) // 2
        offset_y = (480 - height * 16 * scale) // 2
        
        tiles_rendered = 0
        missing_gids = set()
        
        for layer_name, layer_data in layers:
            for y, row in enumerate(layer_data):
                for x, gid in enumerate(row):
                    if gid == 0:
                        continue
                    
                    # Hole Tile über GID
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
        
        # Debug Info
        font = pygame.font.Font(None, 24)
        texts = [
            f"Tiles gerendert: {tiles_rendered}",
            f"GIDs im Cache: {len(sprite_manager.gid_to_surface)}",
        ]
        if missing_gids:
            texts.append(f"Fehlende GIDs: {sorted(missing_gids)}")
        
        for i, text in enumerate(texts):
            color = (255, 255, 255) if "Fehlende" not in text else (255, 100, 100)
            text_surf = font.render(text, True, color)
            screen.blit(text_surf, (10, 10 + i * 25))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    
    if tiles_rendered > 0 and not missing_gids:
        print("\n✅ Erfolg! Alle Tiles wurden korrekt gerendert!")
    else:
        print(f"\n⚠️ {tiles_rendered} Tiles gerendert, {len(missing_gids)} GIDs fehlen")
        if missing_gids:
            print(f"   Fehlende GIDs: {sorted(missing_gids)}")


if __name__ == "__main__":
    test_gid_fix()
