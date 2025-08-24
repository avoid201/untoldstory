#!/usr/bin/env python3
"""
Tiled Integration Tool - Erstellt TSX-Dateien für einzelne Tiles
"""

import os
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List
import xml.dom.minidom as minidom

class TiledTilesetGenerator:
    def __init__(self, tiles_dir: str, tile_size: int = 16):
        self.tiles_dir = Path(tiles_dir)
        self.tile_size = tile_size
        
    def create_collection_tileset(self, category: str, tiles: List[Dict]) -> str:
        """Erstellt eine TSX-Datei für eine Tile-Collection"""
        
        # Root element
        tileset = ET.Element('tileset')
        tileset.set('version', '1.10')
        tileset.set('tiledversion', '1.10.0')
        tileset.set('name', f'{category}_tiles')
        tileset.set('tilewidth', str(self.tile_size))
        tileset.set('tileheight', str(self.tile_size))
        tileset.set('tilecount', str(len(tiles)))
        tileset.set('columns', '0')  # 0 für Collection-Tilesets
        
        # Grid element (für Collection-Tilesets)
        grid = ET.SubElement(tileset, 'grid')
        grid.set('orientation', 'orthogonal')
        grid.set('width', '1')
        grid.set('height', '1')
        
        # Füge jeden Tile hinzu
        for i, tile_info in enumerate(tiles):
            tile_elem = ET.SubElement(tileset, 'tile')
            tile_elem.set('id', str(i))
            
            # Füge Bild hinzu
            image = ET.SubElement(tile_elem, 'image')
            # Relativer Pfad vom TSX-Verzeichnis
            rel_path = f"individual_tiles/{category}/{tile_info['filename']}"
            image.set('source', rel_path)
            image.set('width', str(self.tile_size))
            image.set('height', str(self.tile_size))
            
            # Füge Properties hinzu
            props = ET.SubElement(tile_elem, 'properties')
            
            # Original ID
            prop_id = ET.SubElement(props, 'property')
            prop_id.set('name', 'original_id')
            prop_id.set('value', tile_info['id'])
            
            # Name
            prop_name = ET.SubElement(props, 'property')
            prop_name.set('name', 'tile_name')
            prop_name.set('value', tile_info['name'])
            
            # Source tileset
            if 'source' in tile_info:
                prop_source = ET.SubElement(props, 'property')
                prop_source.set('name', 'source_tileset')
                prop_source.set('value', tile_info['source'])
            
            # Analyse-Daten wenn vorhanden
            if 'analysis' in tile_info:
                analysis = tile_info['analysis']
                if 'dominant_color' in analysis:
                    prop_color = ET.SubElement(props, 'property')
                    prop_color.set('name', 'dominant_color')
                    prop_color.set('value', analysis['dominant_color'])
                
                if 'pattern' in analysis:
                    prop_pattern = ET.SubElement(props, 'property')
                    prop_pattern.set('name', 'pattern_type')
                    prop_pattern.set('value', analysis['pattern'])
        
        # Formatiere XML schön
        xml_str = ET.tostring(tileset, encoding='unicode')
        dom = minidom.parseString(xml_str)
        pretty_xml = dom.toprettyxml(indent='  ')
        
        # Entferne leere Zeilen
        lines = [line for line in pretty_xml.split('\n') if line.strip()]
        return '\n'.join(lines)
    
    def create_image_tileset(self, name: str, image_path: str, 
                            tile_count: int, columns: int) -> str:
        """Erstellt eine TSX-Datei für ein Image-basiertes Tileset"""
        
        tileset = ET.Element('tileset')
        tileset.set('version', '1.10')
        tileset.set('tiledversion', '1.10.0')
        tileset.set('name', name)
        tileset.set('tilewidth', str(self.tile_size))
        tileset.set('tileheight', str(self.tile_size))
        tileset.set('tilecount', str(tile_count))
        tileset.set('columns', str(columns))
        
        # Image element
        image = ET.SubElement(tileset, 'image')
        image.set('source', image_path)
        image.set('width', str(columns * self.tile_size))
        rows = (tile_count + columns - 1) // columns
        image.set('height', str(rows * self.tile_size))
        
        # Formatiere XML
        xml_str = ET.tostring(tileset, encoding='unicode')
        dom = minidom.parseString(xml_str)
        pretty_xml = dom.toprettyxml(indent='  ')
        
        lines = [line for line in pretty_xml.split('\n') if line.strip()]
        return '\n'.join(lines)
    
    def generate_tiled_files(self, output_dir: str):
        """Generiert alle TSX-Dateien für Tiled"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Lade tile_info.json
        info_file = self.tiles_dir / 'tile_info.json'
        if not info_file.exists():
            print(f"❌ tile_info.json not found in {self.tiles_dir}")
            return
        
        with open(info_file, 'r') as f:
            tile_info = json.load(f)
        
        # Gruppiere Tiles nach Kategorie
        categories = {}
        for tile_id, info in tile_info.items():
            category = info['category']
            if category not in categories:
                categories[category] = []
            
            # Füge Dateiname hinzu
            info['filename'] = f"{tile_id}_{info['name']}.png"
            categories[category].append(info)
        
        # Erstelle TSX für jede Kategorie
        created_files = []
        
        for category, tiles in categories.items():
            # Sortiere Tiles nach ID
            tiles.sort(key=lambda x: x['id'])
            
            # Erstelle Collection-TSX
            tsx_content = self.create_collection_tileset(category, tiles)
            
            # Speichere TSX-Datei
            tsx_file = output_path / f'{category}_collection.tsx'
            with open(tsx_file, 'w', encoding='utf-8') as f:
                f.write(tsx_content)
            
            created_files.append(tsx_file)
            print(f"✅ Created {tsx_file.name} with {len(tiles)} tiles")
        
        # Erstelle Master-TSX mit allen Tiles
        all_tiles = []
        for category_tiles in categories.values():
            all_tiles.extend(category_tiles)
        all_tiles.sort(key=lambda x: x['id'])
        
        master_tsx = self.create_collection_tileset('all', all_tiles)
        master_file = output_path / 'master_collection.tsx'
        with open(master_file, 'w', encoding='utf-8') as f:
            f.write(master_tsx)
        
        print(f"✅ Created master_collection.tsx with {len(all_tiles)} tiles")
        
        # Erstelle Tiled-Projekt-Datei
        self.create_tiled_project(output_path, created_files)
        
        return created_files
    
    def create_tiled_project(self, output_dir: Path, tsx_files: List[Path]):
        """Erstellt eine Tiled-Projekt-Datei"""
        
        project = {
            "automappingRulesFile": "",
            "commands": [],
            "extensionsPath": "extensions",
            "folders": [
                "."
            ],
            "propertyTypes": [
                {
                    "id": 1,
                    "name": "TileType",
                    "storageType": "string",
                    "values": [
                        "terrain",
                        "water", 
                        "building",
                        "object",
                        "interior"
                    ],
                    "valuesAsFlags": False
                }
            ]
        }
        
        project_file = output_dir / 'untold_story_tiles.tiled-project'
        with open(project_file, 'w') as f:
            json.dump(project, f, indent=2)
        
        print(f"✅ Created Tiled project file: {project_file.name}")

def main():
    """Hauptfunktion"""
    project_root = Path('/Users/leon/Desktop/untold_story')
    tiles_dir = project_root / 'assets' / 'gfx' / 'individual_tiles'
    tiled_output = project_root / 'assets' / 'gfx' / 'tiles'
    
    if not tiles_dir.exists():
        print("❌ Individual tiles directory not found!")
        print("Please run the tileset_cutter.py script first.")
        return
    
    print("🎮 Generating Tiled tileset files...")
    
    generator = TiledTilesetGenerator(tiles_dir)
    generator.generate_tiled_files(str(tiled_output))
    
    print("\n📝 Instructions for Tiled:")
    print("1. Open Tiled Map Editor")
    print("2. File -> Open Project")
    print(f"3. Navigate to: {tiled_output / 'untold_story_tiles.tiled-project'}")
    print("4. The tilesets are now ready to use!")
    print("\nTileset files:")
    print("- master_collection.tsx: All tiles in one collection")
    print("- [category]_collection.tsx: Tiles grouped by category")
    print("\nEach tile has properties with its original ID and name.")

if __name__ == "__main__":
    main()
