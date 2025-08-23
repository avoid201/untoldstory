#!/usr/bin/env python3
"""
Debug GID Loading - Findet heraus was schief läuft
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import pygame
import xml.etree.ElementTree as ET

def analyze_problem():
    """Analysiert das GID-Problem"""
    
    print("🔍 GID Loading Analyse")
    print("=" * 60)
    
    # 1. Prüfe TMX-Datei
    print("\n1️⃣ TMX-Datei Analyse:")
    tmx_path = Path("data/maps/player_house.tmx")
    tree = ET.parse(tmx_path)
    root = tree.getroot()
    
    print("Tilesets in TMX:")
    for tileset in root.findall('tileset'):
        firstgid = tileset.get('firstgid')
        source = tileset.get('source')
        print(f"  - firstgid={firstgid}, source={source}")
    
    # 2. Prüfe TSX-Dateien
    print("\n2️⃣ TSX-Dateien im data/maps Ordner:")
    maps_dir = Path("data/maps")
    for tsx_file in maps_dir.glob("*.tsx"):
        print(f"  ✅ {tsx_file.name}")
        
        # Parse TSX
        tsx_tree = ET.parse(tsx_file)
        tsx_root = tsx_tree.getroot()
        
        name = tsx_root.get('name')
        tilecount = tsx_root.get('tilecount')
        columns = tsx_root.get('columns')
        
        image = tsx_root.find('image')
        if image is not None:
            source = image.get('source')
            print(f"     Name: {name}, Tiles: {tilecount}, Columns: {columns}")
            print(f"     Bild: {source}")
            
            # Prüfe ob Bild existiert
            if source.startswith("../../"):
                img_path = Path(source.replace("../../", ""))
            else:
                img_path = maps_dir / source
            
            if img_path.exists():
                print(f"     ✅ Bild gefunden: {img_path}")
            else:
                print(f"     ❌ Bild NICHT gefunden: {img_path}")
    
    # 3. Teste SpriteManager
    print("\n3️⃣ SpriteManager Test:")
    pygame.init()
    pygame.display.set_mode((1, 1))
    
    from engine.graphics.sprite_manager import SpriteManager
    sprite_manager = SpriteManager.get()
    
    # Debug: Zeige was _load_tileset_from_tsx macht
    print("\nLade Tilesets mit load_tmx_tilesets:")
    sprite_manager.load_tmx_tilesets(tmx_path)
    
    # Prüfe GID-Mapping
    if hasattr(sprite_manager, 'gid_to_surface'):
        gid_count = len(sprite_manager.gid_to_surface)
        print(f"\n✅ GIDs im Cache: {gid_count}")
        
        if sprite_manager.gid_to_surface:
            print("Vorhandene GIDs:")
            for gid in sorted(sprite_manager.gid_to_surface.keys())[:30]:
                print(f"  GID {gid}")
    else:
        print("\n❌ Kein gid_to_surface Attribut!")
    
    # 4. Teste spezifische GIDs
    print("\n4️⃣ Teste Map-GIDs:")
    
    # GIDs aus der player_house Map
    used_gids = [6, 13, 14, 15, 16, 17, 18, 19, 21]
    
    for gid in used_gids:
        surface = sprite_manager.get_tile_by_gid(gid)
        if surface:
            print(f"  ✅ GID {gid}: Geladen")
        else:
            print(f"  ❌ GID {gid}: FEHLT")
    
    # 5. Zeige was die alte Methode lädt
    print("\n5️⃣ Was lädt _load_tileset_from_tsx?")
    if hasattr(sprite_manager, '_tiles'):
        print(f"Tiles in _tiles: {len(sprite_manager._tiles)}")
        if sprite_manager._tiles:
            sample = list(sprite_manager._tiles.keys())[:10]
            print(f"Beispiel-Keys: {sample}")

if __name__ == "__main__":
    analyze_problem()
