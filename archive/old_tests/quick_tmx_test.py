#!/usr/bin/env python3
"""
Quick TMX Test - Schneller Test des TMX-Systems
"""

import sys
from pathlib import Path

def quick_test():
    print("\n" + "="*60)
    print("🔍 QUICK TMX SYSTEM CHECK")
    print("="*60)
    
    # 1. Prüfe TMX-Dateien
    print("\n1️⃣ TMX-Dateien:")
    tmx_files = list(Path("data/maps").glob("*.tmx"))
    for tmx in tmx_files:
        print(f"   ✅ {tmx.name}")
    
    # 2. Prüfe TSX-Dateien
    print("\n2️⃣ TSX-Tilesets:")
    tsx_files = list(Path("assets/gfx/tiles").glob("*.tsx"))
    for tsx in tsx_files:
        print(f"   ✅ {tsx.name}")
    
    # 3. Prüfe Tileset-Bilder
    print("\n3️⃣ Tileset-Bilder:")
    img_files = list(Path("assets/gfx/tiles/tilesets").glob("*.png"))
    for img in img_files:
        print(f"   ✅ {img.name}")
    
    # 4. Prüfe Interaktions-JSONs
    print("\n4️⃣ Interaktions-JSONs:")
    json_dir = Path("data/maps/interactions")
    if json_dir.exists():
        json_files = list(json_dir.glob("*.json"))
        for jf in json_files:
            print(f"   ✅ {jf.name}")
    else:
        print(f"   ❌ Ordner nicht gefunden: {json_dir}")
    
    # 5. Teste TMX-Parser
    print("\n5️⃣ TMX-Parser Test:")
    try:
        import xml.etree.ElementTree as ET
        
        tmx_path = Path("data/maps/player_house.tmx")
        if tmx_path.exists():
            tree = ET.parse(tmx_path)
            root = tree.getroot()
            
            print(f"   Map: {tmx_path.name}")
            print(f"   Größe: {root.get('width')}x{root.get('height')}")
            print(f"   Tile-Größe: {root.get('tilewidth')}x{root.get('tileheight')}")
            
            # Tilesets
            tilesets = root.findall('tileset')
            print(f"   Tilesets: {len(tilesets)}")
            for ts in tilesets:
                firstgid = ts.get('firstgid')
                source = ts.get('source')
                print(f"     - GID {firstgid}: {source}")
            
            # Layers
            layers = root.findall('layer')
            print(f"   Layers: {len(layers)}")
            for layer in layers:
                name = layer.get('name')
                data = layer.find('data')
                if data is not None:
                    encoding = data.get('encoding', 'none')
                    print(f"     - {name} (encoding: {encoding})")
        else:
            print(f"   ❌ TMX nicht gefunden: {tmx_path}")
            
    except Exception as e:
        print(f"   ❌ Parser-Fehler: {e}")
    
    # 6. Teste Pygame
    print("\n6️⃣ Pygame Test:")
    try:
        import pygame
        pygame.init()
        
        # Erstelle Test-Surface
        test_surf = pygame.Surface((16, 16))
        test_surf.fill((255, 0, 0))
        
        print(f"   ✅ Pygame funktioniert")
        print(f"   Version: {pygame.version.ver}")
        
        pygame.quit()
        
    except Exception as e:
        print(f"   ❌ Pygame-Fehler: {e}")
    
    # 7. Teste TMX-Integration
    print("\n7️⃣ TMX-Integration Test:")
    try:
        from tmx_integration_complete import TMXMapLoader, TMXMap
        print(f"   ✅ TMX-Module importiert")
        
        # Erstelle Loader
        loader = TMXMapLoader()
        print(f"   ✅ TMXMapLoader erstellt")
        
        # Versuche Map zu laden
        tmx_path = Path("data/maps/player_house.tmx")
        if tmx_path.exists():
            try:
                pygame.init()  # Für Surface-Erstellung
                map_data = loader.load_map(tmx_path)
                print(f"   ✅ Map geladen: {map_data.width}x{map_data.height}")
                print(f"   GIDs geladen: {len(map_data.gid_to_surface)}")
                pygame.quit()
            except Exception as e:
                print(f"   ⚠️ Lade-Fehler: {e}")
        
    except ImportError as e:
        print(f"   ❌ Import-Fehler: {e}")
    except Exception as e:
        print(f"   ❌ Fehler: {e}")
    
    print("\n" + "="*60)
    print("✅ Quick-Test abgeschlossen!")
    print("="*60 + "\n")

if __name__ == "__main__":
    quick_test()
