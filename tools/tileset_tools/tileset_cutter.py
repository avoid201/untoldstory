#!/usr/bin/env python3
"""
Tileset Cutter Tool
Schneidet Tilesets in einzelne 16x16 Tiles und organisiert sie mit IDs und Namen
"""

import os
import sys
from PIL import Image
import json
from pathlib import Path
import zipfile
from typing import Dict, List, Tuple

class TilesetCutter:
    def __init__(self, tile_size: int = 16):
        self.tile_size = tile_size
        self.tile_counter = 0
        self.tile_info = {}
        
    def process_tileset(self, image_path: str, category: str) -> List[Dict]:
        """Verarbeitet ein einzelnes Tileset und schneidet es in Tiles"""
        tiles = []
        
        try:
            img = Image.open(image_path)
            
            # Konvertiere zu RGBA für Transparenz-Support
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            width, height = img.size
            cols = width // self.tile_size
            rows = height // self.tile_size
            
            print(f"Processing {image_path}: {cols}x{rows} tiles")
            
            for row in range(rows):
                for col in range(cols):
                    # Schneide das Tile aus
                    left = col * self.tile_size
                    top = row * self.tile_size
                    right = left + self.tile_size
                    bottom = top + self.tile_size
                    
                    tile = img.crop((left, top, right, bottom))
                    
                    # Überprüfe ob das Tile nicht komplett transparent ist
                    if not self.is_empty_tile(tile):
                        tile_id = f"{self.tile_counter:04d}"
                        tile_name = self.get_tile_name(category, row, col)
                        
                        tile_data = {
                            'id': tile_id,
                            'name': tile_name,
                            'category': category,
                            'source': os.path.basename(image_path),
                            'position': {'row': row, 'col': col},
                            'image': tile
                        }
                        
                        tiles.append(tile_data)
                        self.tile_counter += 1
                        
        except Exception as e:
            print(f"Error processing {image_path}: {e}")
            
        return tiles
    
    def is_empty_tile(self, tile: Image.Image) -> bool:
        """Prüft ob ein Tile komplett transparent oder leer ist"""
        if tile.mode == 'RGBA':
            # Prüfe ob alle Alpha-Werte 0 sind
            alpha = tile.split()[-1]
            return alpha.getbbox() is None
        else:
            # Für nicht-transparente Bilder: prüfe ob alle Pixel gleich sind
            pixels = list(tile.getdata())
            return all(p == pixels[0] for p in pixels)
    
    def get_tile_name(self, category: str, row: int, col: int) -> str:
        """Generiert einen beschreibenden Namen für das Tile"""
        # Basierend auf der Kategorie und Position verschiedene Namen generieren
        tile_names = {
            'terrain': {
                (0, 0): 'grass_topleft',
                (0, 1): 'grass_top',
                (0, 2): 'grass_topright',
                (1, 0): 'grass_left',
                (1, 1): 'grass_center',
                (1, 2): 'grass_right',
                (2, 0): 'grass_bottomleft',
                (2, 1): 'grass_bottom',
                (2, 2): 'grass_bottomright',
            },
            'building': {
                (0, 0): 'wall_topleft',
                (0, 1): 'wall_top',
                (0, 2): 'wall_topright',
                (1, 0): 'wall_left',
                (1, 1): 'wall_center',
                (1, 2): 'wall_right',
            },
            'water': {
                (0, 0): 'water_1',
                (0, 1): 'water_2',
                (0, 2): 'water_3',
                (0, 3): 'water_4',
            },
            'objects': {
                (0, 0): 'tree_1',
                (0, 1): 'tree_2',
                (0, 2): 'bush_1',
                (0, 3): 'rock_1',
            },
            'interior': {
                (0, 0): 'floor_wood',
                (0, 1): 'floor_stone',
                (0, 2): 'carpet_red',
                (1, 0): 'table_1',
                (1, 1): 'chair_1',
                (1, 2): 'bed_1',
            }
        }
        
        # Versuche einen spezifischen Namen zu finden
        if category in tile_names and (row, col) in tile_names[category]:
            return tile_names[category][(row, col)]
        else:
            # Fallback: generischer Name
            return f"{category}_r{row}_c{col}"
    
    def save_tiles(self, tiles: List[Dict], output_dir: str):
        """Speichert die geschnittenen Tiles in einer organisierten Ordnerstruktur"""
        output_path = Path(output_dir)
        
        # Erstelle Hauptordner
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Gruppiere Tiles nach Kategorie
        categories = {}
        for tile_data in tiles:
            category = tile_data['category']
            if category not in categories:
                categories[category] = []
            categories[category].append(tile_data)
        
        # Speichere Tiles in Kategorieordnern
        for category, category_tiles in categories.items():
            category_path = output_path / category
            category_path.mkdir(exist_ok=True)
            
            for tile_data in category_tiles:
                # Dateiname: ID_Name.png
                filename = f"{tile_data['id']}_{tile_data['name']}.png"
                filepath = category_path / filename
                
                # Speichere das Bild
                tile_data['image'].save(filepath, 'PNG')
                
                # Speichere Info ohne das Bild-Objekt
                tile_info = {k: v for k, v in tile_data.items() if k != 'image'}
                self.tile_info[tile_data['id']] = tile_info
        
        # Speichere Tile-Info als JSON
        info_file = output_path / 'tile_info.json'
        with open(info_file, 'w') as f:
            json.dump(self.tile_info, f, indent=2)
        
        print(f"Saved {len(tiles)} tiles to {output_path}")
    
    def create_zip(self, source_dir: str, output_file: str):
        """Erstellt eine ZIP-Datei mit allen geschnittenen Tiles"""
        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            source_path = Path(source_dir)
            
            for file_path in source_path.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(source_path)
                    zipf.write(file_path, arcname)
        
        print(f"Created ZIP file: {output_file}")

def main():
    """Hauptfunktion zum Verarbeiten der Tilesets"""
    
    # Konfiguration
    tileset_configs = [
        # Format: (Dateiname, Kategorie)
        ('tileset1.png', 'terrain'),
        ('tileset2.png', 'objects'),
        ('tileset3.png', 'building'),
        ('tileset4.png', 'interior'),
        ('tileset5.png', 'water'),
        ('tileset6.png', 'decoration'),
        ('tileset7.png', 'misc'),
    ]
    
    # Output-Verzeichnisse
    output_dir = '/Users/leon/Desktop/untold_story/assets/gfx/individual_tiles'
    zip_output = '/Users/leon/Desktop/untold_story/individual_tiles.zip'
    
    # Erstelle Cutter-Instanz
    cutter = TilesetCutter(tile_size=16)
    
    # Verarbeite alle Tilesets
    all_tiles = []
    
    # Hinweis: Du musst die Tileset-Bilder hier platzieren
    input_dir = '/Users/leon/Desktop/untold_story/assets/gfx/tiles/tilesets_to_cut'
    Path(input_dir).mkdir(parents=True, exist_ok=True)
    
    print(f"Please place your tileset images in: {input_dir}")
    print("Expected files:")
    for filename, category in tileset_configs:
        print(f"  - {filename} ({category})")
    
    # Prüfe ob Dateien existieren
    for filename, category in tileset_configs:
        filepath = os.path.join(input_dir, filename)
        if os.path.exists(filepath):
            print(f"\nProcessing {filename} as {category}...")
            tiles = cutter.process_tileset(filepath, category)
            all_tiles.extend(tiles)
        else:
            print(f"Warning: {filepath} not found, skipping...")
    
    if all_tiles:
        # Speichere alle Tiles
        cutter.save_tiles(all_tiles, output_dir)
        
        # Erstelle ZIP-Datei
        cutter.create_zip(output_dir, zip_output)
        
        print(f"\n✅ Successfully processed {len(all_tiles)} tiles!")
        print(f"📁 Output directory: {output_dir}")
        print(f"🗜️ ZIP file: {zip_output}")
    else:
        print("\n⚠️ No tiles were processed. Please add your tileset images to the input directory.")

if __name__ == "__main__":
    main()
