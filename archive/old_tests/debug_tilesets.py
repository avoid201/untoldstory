#!/usr/bin/env python3
"""
Debug-Skript für TMX-Tileset-Loading
"""

import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import pygame
import xml.etree.ElementTree as ET


def debug_tileset_loading():
    """Debug das Laden der Tilesets"""
    
    pygame.init()
    
    # Teste Tileset-Loading
    print("🔍 Debug Tileset Loading")
    print("=" * 60)
    
    # Prüfe TSX-Dateien
    tsx_files = [
        "data/maps/tiles_building1.tsx",
        "data/maps/tiles_interior1.tsx"
    ]
    
    for tsx_path in tsx_files:
        path = Path(tsx_path)
        if path.exists():
            print(f"✅ TSX gefunden: {tsx_path}")
            
            # Parse TSX
            tree = ET.parse(path)
            root = tree.getroot()
            
            # Extrahiere Info
            name = root.get('name')
            tilecount = root.get('tilecount')
            
            # Finde Bild
            image_elem = root.find('image')
            if image_elem:
                source = image_elem.get('source')
                print(f"   Name: {name}")
                print(f"   Tiles: {tilecount}")
                print(f"   Bild: {source}")
                
                # Prüfe ob Bild existiert
                if source.startswith("../../"):
                    # Relativer Pfad von data/maps aus
                    img_path = Path("data/maps") / source
                    img_path = img_path.resolve()
                else:
                    img_path = path.parent / source
                
                if img_path.exists():
                    print(f"   ✅ Bild gefunden: {img_path}")
                    
                    # Lade und zeige Größe
                    img = pygame.image.load(str(img_path))
                    w, h = img.get_size()
                    print(f"   Größe: {w}x{h} px")
                else:
                    print(f"   ❌ Bild nicht gefunden: {img_path}")
        else:
            print(f"❌ TSX nicht gefunden: {tsx_path}")
    
    # Teste SpriteManager
    print("\n🔧 Teste SpriteManager...")
    from engine.graphics.sprite_manager import SpriteManager
    
    sprite_manager = SpriteManager.get()
    
    # Lade TMX
    tmx_path = Path("data/maps/player_house.tmx")
    sprite_manager.load_tmx_tilesets(tmx_path)
    
    # Prüfe GIDs
    if hasattr(sprite_manager, 'gid_to_surface'):
        gid_count = len(sprite_manager.gid_to_surface)
        print(f"✅ GIDs geladen: {gid_count}")
        
        # Teste spezifische GIDs aus der Map
        test_gids = [6, 13, 14, 15, 16, 17, 18, 19, 21]
        print("\nTeste GIDs aus player_house:")
        for gid in test_gids:
            surface = sprite_manager.get_tile_by_gid(gid)
            if surface:
                print(f"   GID {gid}: ✅ Surface geladen ({surface.get_size()})")
            else:
                print(f"   GID {gid}: ❌ Keine Surface")
    else:
        print("❌ Keine GID-zu-Surface Mapping")


def show_tileset_preview():
    """Zeige eine Vorschau der Tilesets"""
    pygame.init()
    screen = pygame.display.set_mode((800, 400))
    pygame.display.set_caption("Tileset Preview")
    clock = pygame.time.Clock()
    
    # Lade Tileset-Bilder
    tilesets = [
        ("tiles_building_preview.png", "Building Tiles"),
        ("tiles_interior_preview.png", "Interior Tiles")
    ]
    
    images = []
    for filename, title in tilesets:
        path = Path("assets/gfx/tiles/tilesets") / filename
        if path.exists():
            img = pygame.image.load(str(path))
            images.append((img, title))
            print(f"✅ Geladen: {title}")
        else:
            print(f"❌ Nicht gefunden: {path}")
    
    # Zeige Bilder
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        screen.fill((50, 50, 50))
        
        # Zeichne Tilesets
        y_offset = 20
        for img, title in images:
            # Titel
            font = pygame.font.Font(None, 24)
            text = font.render(title, True, (255, 255, 255))
            screen.blit(text, (10, y_offset))
            
            # Tileset (skaliert für bessere Sichtbarkeit)
            scaled = pygame.transform.scale(img, 
                                           (img.get_width() * 3, 
                                            img.get_height() * 3))
            screen.blit(scaled, (10, y_offset + 30))
            
            y_offset += scaled.get_height() + 60
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()


if __name__ == "__main__":
    print("🎮 TMX Tileset Debug")
    print("=" * 60)
    
    # Debug Tileset Loading
    debug_tileset_loading()
    
    print("\n" + "=" * 60)
    print("Möchtest du eine Vorschau der Tilesets sehen? (j/n)")
    answer = input("> ").strip().lower()
    
    if answer == 'j':
        show_tileset_preview()
    
    print("\n✅ Debug abgeschlossen!")
