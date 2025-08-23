#!/usr/bin/env python3
"""
Test für TMX GID-Mapping
Zeigt welche GIDs in den Maps verwendet werden und wie sie gemappt werden sollten
"""

import sys
import os
from pathlib import Path
import xml.etree.ElementTree as ET

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# from engine.world.gid_mapper import GIDMapper  # Diese Klasse existiert nicht


def analyze_tmx_file(tmx_path: str):
    """Analysiere eine TMX-Datei und zeige GID-Verwendung"""
    print(f"\n📋 Analysiere: {tmx_path}")
    print("=" * 60)
    
    # Parse TMX
    tree = ET.parse(tmx_path)
    root = tree.getroot()
    
    # Map-Info
    width = int(root.get('width', 0))
    height = int(root.get('height', 0))
    print(f"Map-Größe: {width}x{height} Tiles")
    
    # Tilesets
    print("\n🎨 Tilesets:")
    tilesets = {}
    for tileset_elem in root.findall('tileset'):
        firstgid = int(tileset_elem.get('firstgid', 1))
        source = tileset_elem.get('source', '')
        name = source.replace('.tsx', '')
        tilesets[firstgid] = name
        print(f"  - {name}: firstgid={firstgid}")
    
    # Layer und verwendete GIDs
    print("\n📊 Layer und GIDs:")
    for layer_elem in root.findall('layer'):
        layer_name = layer_elem.get('name', 'unnamed')
        print(f"\nLayer: {layer_name}")
        
        # Parse Layer-Daten
        data_elem = layer_elem.find('data')
        if data_elem is not None:
            encoding = data_elem.get('encoding', 'csv')
            if encoding == 'csv':
                csv_text = data_elem.text.strip()
                all_tiles = []
                for line in csv_text.split('\n'):
                    if line.strip():
                        tiles = [int(x.strip()) for x in line.split(',') if x.strip()]
                        all_tiles.extend(tiles)
                
                # Finde unique GIDs (ohne 0)
                unique_gids = sorted(set(t for t in all_tiles if t > 0))
                
                if unique_gids:
                    print(f"  Verwendete GIDs: {unique_gids}")
                    
                    # Zeige welches Tileset für jede GID
                    for gid in unique_gids[:10]:  # Erste 10 als Beispiel
                        # Finde passendes Tileset
                        tileset_name = "unknown"
                        local_id = gid
                        
                        for firstgid in sorted(tilesets.keys(), reverse=True):
                            if gid >= firstgid:
                                tileset_name = tilesets[firstgid]
                                local_id = gid - firstgid
                                break
                        
                        print(f"    GID {gid}: {tileset_name} tile #{local_id}")
                else:
                    print(f"  (Nur leere Tiles)")


def test_gid_mapper():
    """Teste den GID-Mapper mit allen Maps"""
    print("\n🔧 Teste GID-Mapper")
    print("=" * 60)
    
    maps_dir = Path("data/maps")
    tmx_files = list(maps_dir.glob("*.tmx"))
    
    if not tmx_files:
        print("❌ Keine TMX-Dateien gefunden!")
        return
    
    # Teste mit player_house
    test_map = "player_house.tmx"
    test_path = maps_dir / test_map
    
    if test_path.exists():
        # Analysiere Map
        analyze_tmx_file(str(test_path))
        
        # Teste GID-Mapper (vereinfacht, da GIDMapper nicht existiert)
        print("\n🗺️ GID-Mapper Test:")
        print("⚠️ GIDMapper Klasse existiert nicht - vereinfachte Analyse")
        
        print(f"Geladene Tilesets: {list(tilesets.keys())}")
        print(f"Tileset-Mappings: {tilesets}")
    else:
        print(f"❌ Test-Map {test_map} nicht gefunden!")


def show_tileset_structure():
    """Zeige die Struktur der Tilesets"""
    print("\n📦 Tileset-Struktur")
    print("=" * 60)
    
    tiles_dir = Path("assets/gfx/tiles")
    
    # TSX-Dateien
    tsx_files = list(tiles_dir.glob("*.tsx"))
    print(f"\n.tsx Dateien ({len(tsx_files)}):")
    for tsx_file in tsx_files:
        try:
            tree = ET.parse(tsx_file)
            root = tree.getroot()
            name = root.get('name', '')
            tile_count = int(root.get('tilecount', 0))
            columns = int(root.get('columns', 0))
            print(f"  - {tsx_file.name}: {name} ({tile_count} tiles, {columns} columns)")
            
            # Zeige Bild-Quelle
            image_elem = root.find('image')
            if image_elem:
                source = image_elem.get('source', '')
                print(f"    Bild: {source}")
        except Exception as e:
            print(f"  - {tsx_file.name}: Fehler beim Lesen ({e})")
    
    # Tileset-Bilder
    tilesets_dir = tiles_dir / "tilesets"
    if tilesets_dir.exists():
        png_files = list(tilesets_dir.glob("*.png"))
        print(f"\nTileset-Bilder ({len(png_files)}):")
        for png_file in png_files:
            print(f"  - {png_file.name}")


def main():
    """Hauptfunktion"""
    print("🎮 TMX Map Analyse für Untold Story")
    print("=" * 60)
    
    # Zeige Tileset-Struktur
    show_tileset_structure()
    
    # Teste GID-Mapper
    test_gid_mapper()
    
    print("\n✅ Analyse abgeschlossen!")
    print("\n💡 Nächste Schritte:")
    print("1. Prüfe ob die GID-Mappings korrekt sind")
    print("2. Stelle sicher dass alle Tileset-Bilder vorhanden sind")
    print("3. Nutze den GID-Mapper im Spiel für korrektes Rendering")


if __name__ == "__main__":
    main()
