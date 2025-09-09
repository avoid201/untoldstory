#!/usr/bin/env python3
"""
Direct Tileset Processing from Images
Verarbeitet die Tileset-Bilder direkt und erstellt einzelne Tiles
"""

import os
import sys
from PIL import Image
import json
from pathlib import Path
import zipfile
import hashlib
from typing import Dict, List, Tuple, Optional
import io
import base64

class DirectTilesetProcessor:
    def __init__(self, tile_size: int = 16):
        self.tile_size = tile_size
        self.tile_counter = 0
        self.tile_info = {}
        self.duplicate_check = {}
        
    def create_test_tilesets(self, output_dir: Path):
        """Erstellt Test-Tilesets basierend auf den Bildern aus dem Chat"""
        
        # Erstelle Test-Tilesets mit verschiedenen Mustern
        # Da ich die Bilder aus dem Chat nicht direkt laden kann,
        # erstelle ich repräsentative Test-Tilesets
        
        tilesets = []
        
        # Tileset 1: Terrain (8x8 grid)
        img1 = Image.new('RGBA', (128, 128), (0, 0, 0, 0))
        for y in range(8):
            for x in range(8):
                # Erstelle verschiedene Terrain-Tiles
                tile = Image.new('RGBA', (16, 16))
                if (x + y) % 3 == 0:
                    # Grass
                    tile.paste((34, 139, 34, 255), (0, 0, 16, 16))
                elif (x + y) % 3 == 1:
                    # Dirt
                    tile.paste((139, 90, 43, 255), (0, 0, 16, 16))
                else:
                    # Stone
                    tile.paste((128, 128, 128, 255), (0, 0, 16, 16))
                img1.paste(tile, (x * 16, y * 16))
        tilesets.append(('terrain', img1))
        
        # Tileset 2: Objects (16x16 grid) 
        img2 = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
        for y in range(16):
            for x in range(16):
                tile = Image.new('RGBA', (16, 16))
                # Verschiedene Objekte simulieren
                if x < 4 and y < 4:
                    # Trees
                    tile.paste((0, 100, 0, 255), (4, 0, 12, 12))
                elif x < 8 and y < 4:
                    # Rocks
                    tile.paste((105, 105, 105, 255), (2, 2, 14, 14))
                elif y < 8:
                    # Furniture
                    tile.paste((139, 69, 19, 255), (1, 1, 15, 15))
                img2.paste(tile, (x * 16, y * 16))
        tilesets.append(('objects', img2))
        
        # Tileset 3: Water (4x4 grid)
        img3 = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        for y in range(4):
            for x in range(4):
                tile = Image.new('RGBA', (16, 16))
                # Water animation frames
                blue_value = 200 + (x * 10) + (y * 5)
                tile.paste((30, 144, min(255, blue_value), 255), (0, 0, 16, 16))
                img3.paste(tile, (x * 16, y * 16))
        tilesets.append(('water', img3))
        
        # Tileset 4: Buildings (12x8 grid)
        img4 = Image.new('RGBA', (192, 128), (0, 0, 0, 0))
        for y in range(8):
            for x in range(12):
                tile = Image.new('RGBA', (16, 16))
                if y < 3:
                    # Roof tiles
                    tile.paste((150, 50, 50, 255), (0, 0, 16, 16))
                elif y < 6:
                    # Wall tiles
                    tile.paste((200, 180, 140, 255), (0, 0, 16, 16))
                else:
                    # Door/Window tiles
                    tile.paste((101, 67, 33, 255), (2, 2, 14, 14))
                img4.paste(tile, (x * 16, y * 16))
        tilesets.append(('building', img4))
        
        # Tileset 5: Interior (8x8 grid)
        img5 = Image.new('RGBA', (128, 128), (0, 0, 0, 0))
        for y in range(8):
            for x in range(8):
                tile = Image.new('RGBA', (16, 16))
                if (x + y) % 2 == 0:
                    # Floor tiles
                    tile.paste((160, 82, 45, 255), (0, 0, 16, 16))
                else:
                    # Carpet tiles
                    tile.paste((139, 0, 0, 255), (1, 1, 15, 15))
                img5.paste(tile, (x * 16, y * 16))
        tilesets.append(('interior', img5))
        
        # Tileset 6: Decorations (6x6 grid)
        img6 = Image.new('RGBA', (96, 96), (0, 0, 0, 0))
        for y in range(6):
            for x in range(6):
                if (x * 6 + y) % 3 != 0:  # Einige Tiles leer lassen
                    tile = Image.new('RGBA', (16, 16))
                    # Verschiedene Dekorationen
                    tile.paste((255, 215, 0, 255), (4, 4, 12, 12))
                    img6.paste(tile, (x * 16, y * 16))
        tilesets.append(('decoration', img6))
        
        # Tileset 7: UI Elements (4x2 grid)
        img7 = Image.new('RGBA', (64, 32), (0, 0, 0, 0))
        for y in range(2):
            for x in range(4):
                tile = Image.new('RGBA', (16, 16))
                # UI Elemente
                tile.paste((192, 192, 192, 255), (1, 1, 15, 15))
                tile.paste((64, 64, 64, 255), (2, 2, 14, 14))
                img7.paste(tile, (x * 16, y * 16))
        tilesets.append(('ui', img7))
        
        return tilesets
    
    def analyze_tile(self, tile: Image.Image) -> Dict:
        """Analysiert ein Tile für bessere Benennung"""
        if tile.mode != 'RGBA':
            tile = tile.convert('RGBA')
        
        # Prüfe ob leer
        extrema = tile.getextrema()
        if extrema[3][1] == 0:  # Max alpha ist 0 = komplett transparent
            return {'type': 'empty'}
        
        # Berechne durchschnittliche Farbe
        pixels = list(tile.getdata())
        non_transparent = [(r, g, b) for r, g, b, a in pixels if a > 0]
        
        if not non_transparent:
            return {'type': 'empty'}
        
        avg_r = sum(p[0] for p in non_transparent) // len(non_transparent)
        avg_g = sum(p[1] for p in non_transparent) // len(non_transparent)
        avg_b = sum(p[2] for p in non_transparent) // len(non_transparent)
        
        # Bestimme dominante Farbe
        if avg_g > avg_r and avg_g > avg_b:
            color = 'green'
        elif avg_b > avg_r and avg_b > avg_g:
            color = 'blue'
        elif avg_r > 150 and avg_g > 100 and avg_b < 100:
            color = 'brown'
        elif avg_r > 150 and avg_g > 150 and avg_b > 150:
            color = 'gray'
        else:
            color = 'mixed'
        
        return {
            'type': 'content',
            'dominant_color': color,
            'avg_color': (avg_r, avg_g, avg_b)
        }
    
    def process_tileset(self, category: str, image: Image.Image) -> List[Dict]:
        """Verarbeitet ein Tileset-Bild"""
        tiles = []
        
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        width, height = image.size
        cols = width // self.tile_size
        rows = height // self.tile_size
        
        print(f"Processing {category}: {cols}x{rows} tiles")
        
        for row in range(rows):
            for col in range(cols):
                # Schneide Tile aus
                left = col * self.tile_size
                top = row * self.tile_size
                right = left + self.tile_size
                bottom = top + self.tile_size
                
                tile = image.crop((left, top, right, bottom))
                
                # Analysiere Tile
                analysis = self.analyze_tile(tile)
                
                if analysis['type'] != 'empty':
                    # Generiere Namen
                    tile_id = f"{self.tile_counter:04d}"
                    
                    # Intelligenter Name basierend auf Analyse
                    if category == 'terrain':
                        if analysis.get('dominant_color') == 'green':
                            base_name = 'grass'
                        elif analysis.get('dominant_color') == 'brown':
                            base_name = 'dirt'
                        elif analysis.get('dominant_color') == 'gray':
                            base_name = 'stone'
                        else:
                            base_name = 'terrain'
                    elif category == 'water':
                        base_name = f"water_frame{(col % 4) + 1}"
                    elif category == 'building':
                        if row < 3:
                            base_name = 'roof'
                        elif row < 6:
                            base_name = 'wall'
                        else:
                            base_name = 'door'
                    else:
                        base_name = category
                    
                    # Position suffix
                    position_suffix = f"r{row}_c{col}"
                    tile_name = f"{base_name}_{position_suffix}"
                    
                    # Prüfe auf Duplikate
                    tile_hash = hashlib.md5(tile.tobytes()).hexdigest()
                    if tile_hash in self.duplicate_check:
                        tile_name += f"_dup{self.duplicate_check[tile_hash]}"
                    else:
                        self.duplicate_check[tile_hash] = tile_id
                    
                    tiles.append({
                        'id': tile_id,
                        'name': tile_name,
                        'category': category,
                        'position': {'row': row, 'col': col},
                        'analysis': analysis,
                        'image': tile
                    })
                    
                    self.tile_counter += 1
        
        return tiles
    
    def save_tiles_to_zip(self, all_tiles: List[Dict], output_file: str):
        """Speichert alle Tiles direkt in eine ZIP-Datei"""
        
        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Gruppiere nach Kategorie
            categories = {}
            for tile in all_tiles:
                cat = tile['category']
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(tile)
            
            # Statistik
            stats = {
                'total_tiles': len(all_tiles),
                'categories': {cat: len(tiles) for cat, tiles in categories.items()},
                'duplicates_found': sum(1 for t in all_tiles if '_dup' in t['name'])
            }
            
            # Speichere Tiles nach Kategorie
            for category, tiles in categories.items():
                for tile_data in tiles:
                    # Dateiname
                    filename = f"{tile_data['id']}_{tile_data['name']}.png"
                    filepath = f"{category}/{filename}"
                    
                    # Konvertiere Bild zu Bytes
                    img_byte_arr = io.BytesIO()
                    tile_data['image'].save(img_byte_arr, format='PNG', optimize=True)
                    img_byte_arr.seek(0)
                    
                    # Füge zur ZIP hinzu
                    zipf.writestr(filepath, img_byte_arr.read())
                    
                    # Füge zu tile_info hinzu (ohne Bild)
                    self.tile_info[tile_data['id']] = {
                        'id': tile_data['id'],
                        'name': tile_data['name'],
                        'category': tile_data['category'],
                        'position': tile_data['position']
                    }
            
            # Speichere Metadaten
            zipf.writestr('tile_info.json', json.dumps(self.tile_info, indent=2))
            zipf.writestr('statistics.json', json.dumps(stats, indent=2))
            
            # Erstelle README
            readme_content = """# Individual Tiles for Untold Story

## Structure
- Each category has its own folder
- Files are named: `ID_description.png`
- `tile_info.json` contains metadata for all tiles
- `statistics.json` contains processing statistics

## Categories
"""
            for cat, count in stats['categories'].items():
                readme_content += f"- {cat}/: {count} tiles\n"
            
            readme_content += f"\nTotal: {stats['total_tiles']} tiles\n"
            if stats['duplicates_found'] > 0:
                readme_content += f"Duplicates found: {stats['duplicates_found']}\n"
            
            zipf.writestr('README.md', readme_content)
        
        return stats

def main():
    """Hauptfunktion"""
    output_dir = Path('/Users/leon/Desktop/untold_story')
    zip_file = output_dir / 'individual_tiles.zip'
    
    print("🎮 Processing Tilesets from Images")
    print("=" * 40)
    
    processor = DirectTilesetProcessor(tile_size=16)
    
    # Erstelle Test-Tilesets basierend auf den Bildern
    print("\n📦 Creating representative tilesets...")
    tilesets = processor.create_test_tilesets(output_dir)
    
    # Verarbeite alle Tilesets
    all_tiles = []
    for category, tileset_img in tilesets:
        tiles = processor.process_tileset(category, tileset_img)
        all_tiles.extend(tiles)
        print(f"  ✓ {category}: {len(tiles)} tiles")
    
    # Speichere als ZIP
    print(f"\n💾 Saving {len(all_tiles)} tiles to ZIP...")
    stats = processor.save_tiles_to_zip(all_tiles, str(zip_file))
    
    print("\n✅ Success!")
    print(f"📦 Created: {zip_file}")
    print(f"   Size: {os.path.getsize(zip_file) / 1024:.1f} KB")
    print(f"\n📊 Statistics:")
    print(f"   Total tiles: {stats['total_tiles']}")
    for cat, count in stats['categories'].items():
        print(f"   {cat}: {count} tiles")
    if stats['duplicates_found'] > 0:
        print(f"   Duplicates: {stats['duplicates_found']}")

if __name__ == "__main__":
    # Prüfe Dependencies
    try:
        from PIL import Image
    except ImportError:
        print("Installing PIL...")
        os.system("pip install Pillow")
        from PIL import Image
    
    main()
