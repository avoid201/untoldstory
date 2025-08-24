#!/usr/bin/env python3
"""
Advanced Tileset Cutter Tool for Untold Story
Automatisches Schneiden und Benennen von Tilesets in 16x16 Tiles
"""

import os
import sys
from PIL import Image
import json
from pathlib import Path
import zipfile
import hashlib
from typing import Dict, List, Tuple, Optional
import numpy as np

class AdvancedTilesetCutter:
    def __init__(self, tile_size: int = 16):
        self.tile_size = tile_size
        self.tile_counter = 0
        self.tile_info = {}
        self.duplicate_check = {}  # Hash -> erste Tile-ID
        
        # Erweiterte Namenszuordnungen basierend auf typischen Tileset-Mustern
        self.pattern_names = self.load_pattern_names()
        
    def load_pattern_names(self) -> Dict:
        """Lädt vordefinierte Muster für Tile-Benennung"""
        return {
            'terrain': {
                # Autotile patterns (3x3 blocks)
                'grass': ['topleft', 'top', 'topright', 'left', 'center', 'right', 'bottomleft', 'bottom', 'bottomright'],
                'dirt': ['topleft', 'top', 'topright', 'left', 'center', 'right', 'bottomleft', 'bottom', 'bottomright'],
                'stone': ['topleft', 'top', 'topright', 'left', 'center', 'right', 'bottomleft', 'bottom', 'bottomright'],
                'sand': ['topleft', 'top', 'topright', 'left', 'center', 'right', 'bottomleft', 'bottom', 'bottomright'],
                'path': ['horizontal', 'vertical', 'corner_tl', 'corner_tr', 'corner_bl', 'corner_br', 'junction_t', 'junction_b'],
            },
            'water': {
                'animated': ['frame1', 'frame2', 'frame3', 'frame4'],
                'edges': ['shore_top', 'shore_right', 'shore_bottom', 'shore_left', 'corner_tl', 'corner_tr', 'corner_bl', 'corner_br'],
            },
            'building': {
                'wall': ['top', 'middle', 'bottom', 'window', 'door_top', 'door_bottom'],
                'roof': ['peak', 'left_slope', 'right_slope', 'flat', 'chimney', 'dormer'],
                'floor': ['wood', 'stone', 'tile', 'carpet'],
            },
            'objects': {
                'nature': ['tree_top', 'tree_trunk', 'bush', 'flower', 'rock', 'stump'],
                'furniture': ['table', 'chair', 'bed_top', 'bed_bottom', 'chest', 'barrel'],
                'decoration': ['sign', 'fence', 'lamp', 'statue', 'fountain', 'well'],
            },
            'interior': {
                'furniture': ['table_small', 'table_large', 'chair_front', 'chair_side', 'bed', 'bookshelf'],
                'appliances': ['stove', 'sink', 'cabinet', 'counter'],
                'decoration': ['rug', 'painting', 'plant', 'clock', 'mirror'],
            }
        }
    
    def get_tile_hash(self, tile: Image.Image) -> str:
        """Erstellt einen Hash für ein Tile zur Duplikat-Erkennung"""
        return hashlib.md5(tile.tobytes()).hexdigest()
    
    def analyze_tile_content(self, tile: Image.Image) -> Dict:
        """Analysiert den Inhalt eines Tiles für bessere Benennung"""
        if tile.mode != 'RGBA':
            tile = tile.convert('RGBA')
        
        # Konvertiere zu numpy array für Analyse
        data = np.array(tile)
        
        # Analysiere Farben
        alpha = data[:, :, 3]
        non_transparent = alpha > 0
        
        if not non_transparent.any():
            return {'type': 'empty', 'transparency': 1.0}
        
        # Berechne durchschnittliche Farbe (ohne Alpha)
        rgb_data = data[non_transparent][:, :3]
        avg_color = rgb_data.mean(axis=0)
        
        # Bestimme dominante Farbe
        dominant_color = self.get_dominant_color(avg_color)
        
        # Berechne Transparenz-Verhältnis
        transparency_ratio = 1.0 - (non_transparent.sum() / (16 * 16))
        
        # Erkenne Muster
        pattern_type = self.detect_pattern_type(data)
        
        return {
            'type': 'content',
            'dominant_color': dominant_color,
            'transparency': transparency_ratio,
            'pattern': pattern_type,
            'avg_color': avg_color.tolist()
        }
    
    def get_dominant_color(self, avg_color: np.ndarray) -> str:
        """Bestimmt die dominante Farbe basierend auf RGB-Werten"""
        r, g, b = avg_color
        
        # Einfache Farbkategorisierung
        if g > r and g > b and g > 100:
            return 'green'  # Gras, Bäume
        elif b > r and b > g and b > 100:
            return 'blue'   # Wasser
        elif r > 150 and g > 100 and b < 100:
            return 'brown'  # Erde, Holz
        elif r > 150 and g > 150 and b > 150:
            return 'gray'   # Stein
        elif r > 200 and g > 180 and b < 150:
            return 'yellow' # Sand
        else:
            return 'mixed'
    
    def detect_pattern_type(self, data: np.ndarray) -> str:
        """Erkennt Muster im Tile (Kanten, Ecken, etc.)"""
        alpha = data[:, :, 3]
        
        # Prüfe Kanten
        top_edge = alpha[0, :].mean()
        bottom_edge = alpha[-1, :].mean()
        left_edge = alpha[:, 0].mean()
        right_edge = alpha[:, -1].mean()
        
        edges = [top_edge, bottom_edge, left_edge, right_edge]
        transparent_edges = sum(1 for e in edges if e < 128)
        
        if transparent_edges == 3:
            return 'corner'
        elif transparent_edges == 2:
            if (top_edge < 128 and bottom_edge < 128) or (left_edge < 128 and right_edge < 128):
                return 'straight'
            else:
                return 'edge'
        elif transparent_edges == 1:
            return 'edge'
        else:
            return 'fill'
    
    def generate_smart_name(self, category: str, row: int, col: int, 
                           tile_analysis: Dict, tileset_name: str) -> str:
        """Generiert einen intelligenten Namen basierend auf Analyse"""
        base_name = category
        
        # Nutze Analyse-Daten
        if tile_analysis['type'] == 'empty':
            return f"empty_{row}_{col}"
        
        # Farb-basierte Benennung
        color = tile_analysis.get('dominant_color', '')
        pattern = tile_analysis.get('pattern', '')
        
        # Spezielle Muster erkennen
        if color == 'green' and pattern == 'fill':
            base_name = 'grass'
        elif color == 'blue':
            base_name = 'water'
        elif color == 'brown' and pattern == 'fill':
            base_name = 'dirt'
        elif color == 'gray':
            base_name = 'stone'
        elif color == 'yellow':
            base_name = 'sand'
        
        # Pattern-Suffix hinzufügen
        if pattern == 'corner':
            # Bestimme welche Ecke basierend auf Position
            if row == 0 and col == 0:
                pattern_suffix = 'topleft'
            elif row == 0:
                pattern_suffix = 'topright'
            elif col == 0:
                pattern_suffix = 'bottomleft'
            else:
                pattern_suffix = 'bottomright'
        elif pattern == 'edge':
            if row == 0:
                pattern_suffix = 'top'
            elif row > 0 and col == 0:
                pattern_suffix = 'left'
            elif col > 0:
                pattern_suffix = 'right'
            else:
                pattern_suffix = 'bottom'
        else:
            pattern_suffix = f"r{row}_c{col}"
        
        return f"{base_name}_{pattern_suffix}"
    
    def process_tileset(self, image_path: str, category: str = None) -> List[Dict]:
        """Verarbeitet ein einzelnes Tileset mit intelligenter Analyse"""
        tiles = []
        
        # Bestimme Kategorie aus Dateinamen wenn nicht angegeben
        if not category:
            filename = os.path.basename(image_path).lower()
            if 'terrain' in filename:
                category = 'terrain'
            elif 'water' in filename:
                category = 'water'
            elif 'building' in filename:
                category = 'building'
            elif 'object' in filename:
                category = 'objects'
            elif 'interior' in filename:
                category = 'interior'
            elif 'npc' in filename:
                category = 'npcs'
            else:
                category = 'misc'
        
        try:
            img = Image.open(image_path)
            
            # Konvertiere zu RGBA für Transparenz-Support
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            width, height = img.size
            cols = width // self.tile_size
            rows = height // self.tile_size
            
            print(f"Processing {os.path.basename(image_path)}: {cols}x{rows} tiles ({category})")
            
            tileset_name = Path(image_path).stem
            
            for row in range(rows):
                for col in range(cols):
                    # Schneide das Tile aus
                    left = col * self.tile_size
                    top = row * self.tile_size
                    right = left + self.tile_size
                    bottom = top + self.tile_size
                    
                    tile = img.crop((left, top, right, bottom))
                    
                    # Analysiere Tile
                    tile_analysis = self.analyze_tile_content(tile)
                    
                    # Überprüfe ob das Tile nicht leer ist
                    if tile_analysis['type'] != 'empty' or tile_analysis['transparency'] < 0.95:
                        # Prüfe auf Duplikate
                        tile_hash = self.get_tile_hash(tile)
                        
                        tile_id = f"{self.tile_counter:04d}"
                        tile_name = self.generate_smart_name(category, row, col, 
                                                            tile_analysis, tileset_name)
                        
                        # Wenn Duplikat, markiere es
                        if tile_hash in self.duplicate_check:
                            original_id = self.duplicate_check[tile_hash]
                            tile_name = f"{tile_name}_dup{original_id}"
                        else:
                            self.duplicate_check[tile_hash] = tile_id
                        
                        tile_data = {
                            'id': tile_id,
                            'name': tile_name,
                            'category': category,
                            'source': os.path.basename(image_path),
                            'position': {'row': row, 'col': col},
                            'analysis': tile_analysis,
                            'image': tile,
                            'hash': tile_hash
                        }
                        
                        tiles.append(tile_data)
                        self.tile_counter += 1
                        
        except Exception as e:
            print(f"Error processing {image_path}: {e}")
            
        return tiles
    
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
        
        # Erstelle Statistik
        stats = {
            'total_tiles': len(tiles),
            'categories': {},
            'duplicates_found': 0
        }
        
        # Speichere Tiles in Kategorieordnern
        for category, category_tiles in categories.items():
            category_path = output_path / category
            category_path.mkdir(exist_ok=True)
            
            stats['categories'][category] = len(category_tiles)
            
            for tile_data in category_tiles:
                # Dateiname: ID_Name.png
                filename = f"{tile_data['id']}_{tile_data['name']}.png"
                filepath = category_path / filename
                
                # Speichere das Bild
                tile_data['image'].save(filepath, 'PNG', optimize=True)
                
                # Prüfe auf Duplikate
                if '_dup' in tile_data['name']:
                    stats['duplicates_found'] += 1
                
                # Speichere Info ohne das Bild-Objekt
                tile_info = {k: v for k, v in tile_data.items() 
                           if k not in ['image', 'hash']}
                self.tile_info[tile_data['id']] = tile_info
        
        # Speichere Tile-Info als JSON
        info_file = output_path / 'tile_info.json'
        with open(info_file, 'w') as f:
            json.dump(self.tile_info, f, indent=2)
        
        # Speichere Statistik
        stats_file = output_path / 'statistics.json'
        with open(stats_file, 'w') as f:
            json.dump(stats, f, indent=2)
        
        print(f"\n📊 Statistics:")
        print(f"  Total tiles: {stats['total_tiles']}")
        print(f"  Duplicates found: {stats['duplicates_found']}")
        for cat, count in stats['categories'].items():
            print(f"  {cat}: {count} tiles")
    
    def create_zip(self, source_dir: str, output_file: str):
        """Erstellt eine ZIP-Datei mit allen geschnittenen Tiles"""
        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            source_path = Path(source_dir)
            
            file_count = 0
            for file_path in source_path.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(source_path)
                    zipf.write(file_path, arcname)
                    file_count += 1
        
        print(f"\n📦 Created ZIP file: {output_file}")
        print(f"   Contains {file_count} files")
        
        # Zeige Dateigröße
        size_mb = os.path.getsize(output_file) / (1024 * 1024)
        print(f"   Size: {size_mb:.2f} MB")

def main():
    """Hauptfunktion zum Verarbeiten der Tilesets"""
    
    # Output-Verzeichnisse
    project_root = Path('/Users/leon/Desktop/untold_story')
    output_dir = project_root / 'assets' / 'gfx' / 'individual_tiles'
    zip_output = project_root / 'individual_tiles.zip'
    
    # Erstelle Cutter-Instanz
    cutter = AdvancedTilesetCutter(tile_size=16)
    
    # Sammle alle Tileset-Dateien
    tileset_sources = []
    
    # Suche nach vorhandenen Tilesets
    tileset_dirs = [
        project_root / 'assets' / 'gfx' / 'tiles' / 'tilesets',
        project_root / 'assets' / 'gfx' / 'tiles',
        project_root / 'assets' / 'gfx',
    ]
    
    print("🔍 Searching for tilesets...")
    
    for search_dir in tileset_dirs:
        if search_dir.exists():
            # Suche nach PNG-Dateien
            for png_file in search_dir.glob('*.png'):
                # Ignoriere bereits geschnittene Tiles
                if 'individual' not in str(png_file) and 'preview' not in str(png_file).lower():
                    tileset_sources.append(str(png_file))
    
    # Füge manuell platzierte Tilesets hinzu
    manual_dir = project_root / 'tilesets_to_cut'
    if manual_dir.exists():
        for png_file in manual_dir.glob('*.png'):
            tileset_sources.append(str(png_file))
    
    # Entferne Duplikate
    tileset_sources = list(set(tileset_sources))
    
    if not tileset_sources:
        print("\n⚠️ No tilesets found!")
        print(f"Please place your tileset images in: {manual_dir}")
        manual_dir.mkdir(parents=True, exist_ok=True)
        return
    
    print(f"\n📋 Found {len(tileset_sources)} tilesets:")
    for source in tileset_sources:
        print(f"  - {os.path.basename(source)}")
    
    # Verarbeite alle gefundenen Tilesets
    all_tiles = []
    
    for tileset_path in tileset_sources:
        tiles = cutter.process_tileset(tileset_path)
        all_tiles.extend(tiles)
    
    if all_tiles:
        # Speichere alle Tiles
        print(f"\n💾 Saving {len(all_tiles)} tiles...")
        cutter.save_tiles(all_tiles, str(output_dir))
        
        # Erstelle ZIP-Datei
        cutter.create_zip(str(output_dir), str(zip_output))
        
        print(f"\n✅ Successfully processed {len(all_tiles)} tiles!")
        print(f"📁 Output directory: {output_dir}")
        print(f"🗜️ ZIP file: {zip_output}")
        
        # Erstelle README
        readme_path = output_dir / 'README.md'
        with open(readme_path, 'w') as f:
            f.write("# Individual Tiles for Untold Story\n\n")
            f.write("## Structure\n")
            f.write("- Each category has its own folder\n")
            f.write("- Files are named: `ID_description.png`\n")
            f.write("- `tile_info.json` contains metadata for all tiles\n")
            f.write("- `statistics.json` contains processing statistics\n\n")
            f.write("## Usage with Tiled\n")
            f.write("1. Import individual tiles as needed\n")
            f.write("2. Use the ID for reference\n")
            f.write("3. Transparency is preserved where present\n")
        
    else:
        print("\n⚠️ No tiles were processed.")

if __name__ == "__main__":
    # Installiere benötigte Pakete falls nicht vorhanden
    try:
        import numpy
        from PIL import Image
    except ImportError:
        print("Installing required packages...")
        os.system("pip install Pillow numpy")
        print("Please run the script again.")
        sys.exit(1)
    
    main()
