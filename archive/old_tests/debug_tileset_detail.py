#!/usr/bin/env python3
"""
Detailliertes Debug für Tileset-Loading
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

def debug_tileset_loading():
    """Zeigt genau was beim Tileset-Loading passiert"""
    
    print("🔍 Detailliertes Tileset Debug")
    print("=" * 60)
    
    # 1. Prüfe Dateien
    print("\n1️⃣ Datei-Check:")
    
    # TSX in data/maps
    tsx_files = list(Path("data/maps").glob("*.tsx"))
    print(f"TSX-Dateien in data/maps: {len(tsx_files)}")
    for f in tsx_files:
        print(f"  - {f.name}")
    
    # Bilder
    img_files = list(Path("assets/gfx/tiles/tilesets").glob("*.png"))
    print(f"\nBilder in assets/gfx/tiles/tilesets: {len(img_files)}")
    for f in img_files:
        print(f"  - {f.name}")
    
    # 2. Teste manuelles Loading
    print("\n2️⃣ Manuelles Tileset-Loading:")
    
    import pygame
    pygame.init()
    pygame.display.set_mode((1, 1))
    
    # Teste tiles_interior1.tsx
    tsx_path = Path("data/maps/tiles_interior1.tsx")
    if tsx_path.exists():
        print(f"\nLade {tsx_path}...")
        
        import xml.etree.ElementTree as ET
        tree = ET.parse(tsx_path)
        root = tree.getroot()
        
        name = root.get('name')
        tilecount = int(root.get('tilecount', 0))
        columns = int(root.get('columns', 1))
        
        print(f"  Name: {name}")
        print(f"  Tiles: {tilecount}")
        print(f"  Columns: {columns}")
        
        image_elem = root.find('image')
        if image_elem:
            source = image_elem.get('source')
            print(f"  Bild-Quelle: {source}")
            
            # Versuche Bild zu laden
            if source.startswith("../../"):
                img_path = Path(source.replace("../../", ""))
            else:
                img_path = tsx_path.parent / source
            
            print(f"  Aufgelöster Pfad: {img_path}")
            
            if img_path.exists():
                print(f"  ✅ Bild existiert!")
                
                # Lade es
                try:
                    surface = pygame.image.load(str(img_path))
                    w, h = surface.get_size()
                    print(f"  ✅ Bild geladen: {w}x{h} px")
                    
                    # Extrahiere ein paar Tiles
                    print(f"\n  Extrahiere Tiles mit firstgid=13:")
                    for i in range(min(3, tilecount)):
                        col = i % columns
                        row = i // columns
                        x = col * 16
                        y = row * 16
                        
                        tile = pygame.Surface((16, 16), pygame.SRCALPHA)
                        tile.blit(surface, (0, 0), (x, y, 16, 16))
                        
                        gid = 13 + i  # firstgid=13
                        print(f"    GID {gid}: Tile {i} bei ({x},{y})")
                        
                except Exception as e:
                    print(f"  ❌ Fehler beim Laden: {e}")
            else:
                print(f"  ❌ Bild existiert NICHT!")
    
    # 3. Teste SpriteManager
    print("\n3️⃣ Teste SpriteManager mit TMX:")
    
    from engine.graphics.sprite_manager import SpriteManager
    sprite_manager = SpriteManager()
    
    # Initialisiere GID-Mapping
    sprite_manager.gid_to_surface = {}
    sprite_manager._loaded_tilesets = set()
    
    # Lade player_house tilesets
    tmx_path = Path("data/maps/player_house.tmx")
    print(f"\nLade Tilesets aus {tmx_path}...")
    
    sprite_manager.load_tmx_tilesets(tmx_path)
    
    print(f"\nGeladene GIDs: {len(sprite_manager.gid_to_surface)}")
    if sprite_manager.gid_to_surface:
        print(f"GIDs: {sorted(sprite_manager.gid_to_surface.keys())}")
        
        # Teste spezifische GIDs
        test_gids = [13, 14, 15]
        print(f"\nTeste GIDs {test_gids}:")
        for gid in test_gids:
            if gid in sprite_manager.gid_to_surface:
                surf = sprite_manager.gid_to_surface[gid]
                print(f"  GID {gid}: ✅ Surface {surf.get_size()}")
            else:
                print(f"  GID {gid}: ❌ Nicht gefunden")

if __name__ == "__main__":
    debug_tileset_loading()
