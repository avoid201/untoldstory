#!/usr/bin/env python3
"""
Erstellt Individual Tiles basierend auf den Tileset-Mustern
"""

import os
import sys

# Füge benötigte Imports hinzu
try:
    from PIL import Image
except ImportError:
    print("Installing Pillow...")
    os.system("pip install Pillow")
    from PIL import Image

import json
from pathlib import Path
import zipfile
import io

class TilesetProcessor:
    def __init__(self, tile_size=16):
        self.tile_size = tile_size
        self.tile_counter = 0
        
    def create_tilesets_from_patterns(self):
        """Erstellt Tilesets basierend auf typischen Mustern"""
        tilesets = []
        
        # Tileset 1: Basic Terrain (128x64)
        img1 = Image.new('RGBA', (128, 64), (0, 0, 0, 0))
        terrain_colors = [
            # Zeile 1: Grass variations
            [(34, 139, 34), (0, 100, 0), (124, 252, 0), (50, 205, 50),
             (34, 139, 34), (0, 128, 0), (85, 107, 47), (107, 142, 35)],
            # Zeile 2: Dirt/Earth
            [(139, 90, 43), (160, 82, 45), (139, 69, 19), (165, 42, 42),
             (184, 134, 11), (205, 133, 63), (210, 180, 140), (188, 143, 143)],
            # Zeile 3: Stone/Rock
            [(128, 128, 128), (105, 105, 105), (112, 128, 144), (119, 136, 153),
             (169, 169, 169), (192, 192, 192), (211, 211, 211), (220, 220, 220)],
            # Zeile 4: Water/Sand
            [(30, 144, 255), (65, 105, 225), (0, 191, 255), (135, 206, 235),
             (255, 228, 181), (255, 222, 173), (238, 203, 173), (255, 218, 185)]
        ]
        
        for y, row_colors in enumerate(terrain_colors):
            for x, color in enumerate(row_colors):
                tile = Image.new('RGBA', (16, 16), color + (255,))
                # Add some texture
                for px in range(0, 16, 3):
                    for py in range(0, 16, 3):
                        if (px + py) % 6 == 0:
                            darker = tuple(max(0, c - 20) for c in color)
                            tile.putpixel((px, py), darker + (255,))
                img1.paste(tile, (x * 16, y * 16))
        tilesets.append(('terrain', img1))
        
        # Tileset 2: Nature Objects (256x256)
        img2 = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
        for y in range(16):
            for x in range(16):
                tile = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
                
                # Trees (first 4x4)
                if y < 4 and x < 4:
                    # Tree top
                    if y < 2:
                        tile.ellipse([(2, 2), (14, 14)], fill=(0, 100 + x*20, 0, 255))
                    # Tree trunk
                    else:
                        tile.rectangle([(6, 0), (10, 16)], fill=(101, 67, 33, 255))
                # Bushes (4x4)
                elif y < 4 and x < 8:
                    tile.ellipse([(3, 5), (13, 13)], fill=(0, 128, 0, 255))
                # Rocks (4x4)
                elif y < 4:
                    gray = 80 + (x * 10)
                    tile.ellipse([(4, 6), (12, 14)], fill=(gray, gray, gray, 255))
                # Flowers (next 4 rows)
                elif y < 8:
                    # Stem
                    tile.rectangle([(7, 8), (9, 16)], fill=(0, 128, 0, 255))
                    # Flower
                    colors = [(255, 0, 0), (255, 255, 0), (255, 0, 255), (255, 255, 255)]
                    flower_color = colors[(x + y) % 4]
                    tile.ellipse([(5, 4), (11, 10)], fill=flower_color + (255,))
                # Fences
                elif y < 10:
                    tile.rectangle([(0, 7), (16, 9)], fill=(139, 69, 19, 255))
                    if x % 2 == 0:
                        tile.rectangle([(7, 0), (9, 16)], fill=(139, 69, 19, 255))
                # Signs and posts
                elif y < 12:
                    tile.rectangle([(7, 4), (9, 16)], fill=(101, 67, 33, 255))
                    if x % 3 == 0:
                        tile.rectangle([(3, 2), (13, 8)], fill=(160, 82, 45, 255))
                # Items/Collectibles
                else:
                    # Coins, gems, etc
                    item_colors = [(255, 215, 0), (192, 192, 192), (255, 0, 0), (0, 255, 0)]
                    item_color = item_colors[x % 4]
                    tile.ellipse([(5, 5), (11, 11)], fill=item_color + (255,))
                
                img2.paste(tile, (x * 16, y * 16))
        tilesets.append(('objects', img2))
        
        # Tileset 3: Water Animations (128x128)
        img3 = Image.new('RGBA', (128, 128), (0, 0, 0, 0))
        for y in range(8):
            for x in range(8):
                tile = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
                
                # Animated water frames
                if y < 4:
                    blue_val = 200 + ((x + y) * 10) % 55
                    tile.rectangle([(0, 0), (16, 16)], fill=(30, 144, blue_val, 255))
                    # Wave pattern
                    for wy in range(2, 14, 3):
                        wave_x = (wy + x * 2) % 16
                        tile.rectangle([(wave_x, wy), (min(wave_x + 3, 15), wy + 1)], 
                                     fill=(60, 180, 255, 255))
                # Shore tiles
                else:
                    # Sand base
                    tile.rectangle([(0, 0), (16, 16)], fill=(255, 228, 181, 255))
                    # Water edges
                    if x == 0:  # Left shore
                        tile.rectangle([(0, 0), (8, 16)], fill=(30, 144, 255, 255))
                    elif x == 1:  # Right shore
                        tile.rectangle([(8, 0), (16, 16)], fill=(30, 144, 255, 255))
                    elif x == 2:  # Top shore
                        tile.rectangle([(0, 0), (16, 8)], fill=(30, 144, 255, 255))
                    elif x == 3:  # Bottom shore
                        tile.rectangle([(0, 8), (16, 16)], fill=(30, 144, 255, 255))
                    elif x == 4:  # Corner TL
                        tile.rectangle([(0, 0), (8, 8)], fill=(30, 144, 255, 255))
                    elif x == 5:  # Corner TR
                        tile.rectangle([(8, 0), (16, 8)], fill=(30, 144, 255, 255))
                    elif x == 6:  # Corner BL
                        tile.rectangle([(0, 8), (8, 16)], fill=(30, 144, 255, 255))
                    elif x == 7:  # Corner BR
                        tile.rectangle([(8, 8), (16, 16)], fill=(30, 144, 255, 255))
                
                img3.paste(tile, (x * 16, y * 16))
        tilesets.append(('water', img3))
        
        # Tileset 4: Buildings (192x128)
        img4 = Image.new('RGBA', (192, 128), (0, 0, 0, 0))
        for y in range(8):
            for x in range(12):
                tile = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
                
                # Roofs
                if y < 3:
                    roof_colors = [(150, 50, 50), (50, 50, 150), (50, 150, 50)]
                    roof_color = roof_colors[x % 3]
                    tile.rectangle([(0, 0), (16, 16)], fill=roof_color + (255,))
                    # Roof tiles pattern
                    for rx in range(0, 16, 4):
                        tile.line([(rx, 0), (rx, 16)], fill=(0, 0, 0, 100), width=1)
                # Walls
                elif y < 6:
                    wall_color = (200, 180, 140)
                    tile.rectangle([(0, 0), (16, 16)], fill=wall_color + (255,))
                    # Brick pattern
                    for by in range(0, 16, 4):
                        tile.line([(0, by), (16, by)], fill=(150, 130, 90, 255), width=1)
                        if by % 8 == 0:
                            for bx in range(0, 16, 8):
                                tile.line([(bx, by), (bx, by+4)], fill=(150, 130, 90, 255), width=1)
                        else:
                            for bx in range(4, 16, 8):
                                tile.line([(bx, by), (bx, by+4)], fill=(150, 130, 90, 255), width=1)
                # Doors and Windows
                else:
                    if x % 2 == 0:
                        # Door
                        tile.rectangle([(2, 0), (14, 16)], fill=(101, 67, 33, 255))
                        tile.ellipse([(6, 7), (10, 11)], fill=(70, 40, 20, 255))  # Handle
                    else:
                        # Window
                        tile.rectangle([(0, 0), (16, 16)], fill=(200, 180, 140, 255))  # Wall
                        tile.rectangle([(2, 2), (14, 14)], fill=(135, 206, 235, 255))  # Glass
                        # Frame
                        tile.line([(8, 2), (8, 14)], fill=(101, 67, 33, 255), width=2)
                        tile.line([(2, 8), (14, 8)], fill=(101, 67, 33, 255), width=2)
                
                img4.paste(tile, (x * 16, y * 16))
        tilesets.append(('building', img4))
        
        # Tileset 5: Interior/Furniture (128x96)
        img5 = Image.new('RGBA', (128, 96), (0, 0, 0, 0))
        for y in range(6):
            for x in range(8):
                tile = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
                
                # Floors
                if y < 2:
                    if x < 4:
                        # Wood floor
                        tile.rectangle([(0, 0), (16, 16)], fill=(139, 69, 19, 255))
                        for fy in range(0, 16, 2):
                            tile.line([(0, fy), (16, fy)], fill=(160, 82, 45, 255), width=1)
                    else:
                        # Tile floor
                        tile.rectangle([(0, 0), (16, 16)], fill=(200, 200, 200, 255))
                        tile.rectangle([(0, 0), (1, 16)], fill=(150, 150, 150, 255))
                        tile.rectangle([(0, 0), (16, 1)], fill=(150, 150, 150, 255))
                # Furniture
                elif y < 4:
                    furniture_color = (101, 67, 33)
                    if x == 0:  # Table
                        tile.rectangle([(2, 4), (14, 12)], fill=furniture_color + (255,))
                        tile.rectangle([(3, 12), (5, 16)], fill=furniture_color + (255,))
                        tile.rectangle([(11, 12), (13, 16)], fill=furniture_color + (255,))
                    elif x == 1:  # Chair
                        tile.rectangle([(4, 6), (12, 14)], fill=furniture_color + (255,))
                        tile.rectangle([(4, 2), (12, 8)], fill=furniture_color + (255,))
                    elif x == 2:  # Bed
                        tile.rectangle([(1, 4), (15, 16)], fill=(139, 0, 0, 255))
                        tile.rectangle([(2, 2), (14, 6)], fill=(255, 255, 255, 255))
                    elif x == 3:  # Bookshelf
                        tile.rectangle([(2, 0), (14, 16)], fill=furniture_color + (255,))
                        for sy in range(2, 14, 4):
                            tile.rectangle([(3, sy), (13, sy+3)], fill=(0, 0, 128, 255))
                    elif x == 4:  # Chest
                        tile.rectangle([(3, 6), (13, 14)], fill=(139, 90, 43, 255))
                        tile.rectangle([(7, 5), (9, 7)], fill=(255, 215, 0, 255))
                    else:  # Decorations
                        tile.ellipse([(5, 5), (11, 11)], fill=(random_color := ((x*40)%255, (y*60)%255, 100, 255)))
                # Carpets
                else:
                    carpet_colors = [(139, 0, 0), (0, 0, 139), (0, 139, 0), (139, 0, 139)]
                    carpet_color = carpet_colors[x % 4]
                    tile.rectangle([(0, 0), (16, 16)], fill=carpet_color + (255,))
                    # Pattern
                    for cx in range(2, 14, 3):
                        for cy in range(2, 14, 3):
                            tile.ellipse([(cx, cy), (cx+2, cy+2)], fill=(255, 215, 0, 255))
                
                img5.paste(tile, (x * 16, y * 16))
        tilesets.append(('interior', img5))
        
        # Tileset 6: UI Elements (128x32)
        img6 = Image.new('RGBA', (128, 32), (0, 0, 0, 0))
        for y in range(2):
            for x in range(8):
                tile = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
                
                if y == 0:
                    # Buttons
                    tile.rectangle([(1, 1), (15, 15)], fill=(192, 192, 192, 255))
                    tile.rectangle([(2, 2), (14, 14)], fill=(128, 128, 128, 255))
                    # Button states
                    if x % 3 == 0:  # Normal
                        tile.rectangle([(3, 3), (13, 13)], fill=(160, 160, 160, 255))
                    elif x % 3 == 1:  # Hover
                        tile.rectangle([(3, 3), (13, 13)], fill=(180, 180, 180, 255))
                    else:  # Pressed
                        tile.rectangle([(3, 3), (13, 13)], fill=(100, 100, 100, 255))
                else:
                    # Icons
                    icon_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
                    icon_color = icon_colors[x % 4]
                    if x < 4:
                        # Simple shapes
                        tile.ellipse([(4, 4), (12, 12)], fill=icon_color + (255,))
                    else:
                        # Diamonds
                        tile.polygon([(8, 2), (14, 8), (8, 14), (2, 8)], fill=icon_color + (255,))
                
                img6.paste(tile, (x * 16, y * 16))
        tilesets.append(('ui', img6))
        
        return tilesets
    
    def process_and_create_zip(self, output_path):
        """Verarbeitet Tilesets und erstellt ZIP-Datei"""
        
        # Erstelle Tilesets
        tilesets = self.create_tilesets_from_patterns()
        
        # Öffne ZIP-Datei
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            all_tiles = []
            tile_info = {}
            
            # Verarbeite jedes Tileset
            for category, tileset_img in tilesets:
                width, height = tileset_img.size
                cols = width // self.tile_size
                rows = height // self.tile_size
                
                category_tiles = 0
                
                for row in range(rows):
                    for col in range(cols):
                        # Schneide Tile
                        left = col * self.tile_size
                        top = row * self.tile_size
                        tile = tileset_img.crop((left, top, left + self.tile_size, top + self.tile_size))
                        
                        # Prüfe ob nicht leer
                        if tile.getbbox() is not None:
                            tile_id = f"{self.tile_counter:04d}"
                            
                            # Generiere beschreibenden Namen
                            tile_name = self.generate_tile_name(category, row, col)
                            
                            # Speichere Tile in ZIP
                            filename = f"{tile_id}_{tile_name}.png"
                            filepath = f"{category}/{filename}"
                            
                            img_bytes = io.BytesIO()
                            tile.save(img_bytes, 'PNG', optimize=True)
                            zipf.writestr(filepath, img_bytes.getvalue())
                            
                            # Speichere Metadaten
                            tile_info[tile_id] = {
                                'id': tile_id,
                                'name': tile_name,
                                'category': category,
                                'position': {'row': row, 'col': col},
                                'source': f"{category}_tileset"
                            }
                            
                            self.tile_counter += 1
                            category_tiles += 1
                            all_tiles.append(category)
                
                print(f"  {category}: {category_tiles} tiles")
            
            # Speichere Metadaten
            zipf.writestr('tile_info.json', json.dumps(tile_info, indent=2))
            
            # Erstelle Statistik
            stats = {
                'total_tiles': self.tile_counter,
                'categories': {}
            }
            for cat in set(all_tiles):
                stats['categories'][cat] = all_tiles.count(cat)
            
            zipf.writestr('statistics.json', json.dumps(stats, indent=2))
            
            # Erstelle README
            readme = self.create_readme(stats)
            zipf.writestr('README.md', readme)
            
            return stats
    
    def generate_tile_name(self, category, row, col):
        """Generiert beschreibende Namen für Tiles"""
        
        names = {
            'terrain': {
                0: ['grass_light', 'grass_dark', 'grass_bright', 'grass_medium',
                    'grass_plain', 'grass_forest', 'grass_dry', 'grass_lush'],
                1: ['dirt_dry', 'dirt_wet', 'dirt_dark', 'dirt_red',
                    'dirt_gold', 'dirt_sandy', 'dirt_light', 'dirt_rocky'],
                2: ['stone_gray', 'stone_dark', 'stone_blue', 'stone_light',
                    'stone_bright', 'stone_silver', 'stone_white', 'stone_pale'],
                3: ['water_deep', 'water_ocean', 'water_clear', 'water_shallow',
                    'sand_beach', 'sand_desert', 'sand_light', 'sand_soft']
            },
            'water': {
                0: 'water_anim1', 1: 'water_anim2', 2: 'water_anim3', 3: 'water_anim4',
                4: 'shore_left', 5: 'shore_right', 6: 'shore_top', 7: 'shore_bottom'
            },
            'objects': {
                0: 'tree_oak', 1: 'tree_pine', 2: 'tree_small', 3: 'tree_dead',
                4: 'bush_green', 5: 'bush_berry', 6: 'bush_flower', 7: 'bush_dry',
                8: 'rock_small', 9: 'rock_large', 10: 'rock_mossy', 11: 'rock_sharp'
            },
            'building': {
                0: 'roof_red', 1: 'roof_blue', 2: 'roof_green',
                3: 'wall_brick', 4: 'wall_stone', 5: 'wall_wood',
                6: 'door_wood', 7: 'window_glass'
            },
            'interior': {
                0: 'floor_wood', 1: 'floor_tile',
                2: 'table', 3: 'chair', 4: 'bed', 5: 'bookshelf',
                6: 'carpet_red', 7: 'carpet_blue'
            },
            'ui': {
                0: 'button_normal', 1: 'button_hover', 2: 'button_pressed',
                3: 'icon_health', 4: 'icon_mana', 5: 'icon_gold'
            }
        }
        
        # Versuche spezifischen Namen zu finden
        if category in names:
            if isinstance(names[category], dict):
                if row in names[category]:
                    name_list = names[category][row]
                    if col < len(name_list):
                        return name_list[col]
                elif row * 8 + col in names[category]:
                    return names[category][row * 8 + col]
            elif row * 8 + col in names[category]:
                return names[category][row * 8 + col]
        
        # Fallback
        return f"{category}_r{row}c{col}"
    
    def create_readme(self, stats):
        """Erstellt README-Inhalt"""
        return f"""# Individual Tiles for Untold Story

## 📊 Statistics
- **Total Tiles:** {stats['total_tiles']}
- **Categories:** {len(stats['categories'])}

## 📁 Structure
```
individual_tiles/
├── terrain/     ({stats['categories'].get('terrain', 0)} tiles)
├── objects/     ({stats['categories'].get('objects', 0)} tiles)
├── water/       ({stats['categories'].get('water', 0)} tiles)
├── building/    ({stats['categories'].get('building', 0)} tiles)
├── interior/    ({stats['categories'].get('interior', 0)} tiles)
├── ui/          ({stats['categories'].get('ui', 0)} tiles)
├── tile_info.json
├── statistics.json
└── README.md
```

## 🎮 File Format
- **Naming:** `[ID]_[description].png`
- **Example:** `0001_grass_light.png`
- **Size:** All tiles are 16x16 pixels
- **Format:** PNG with transparency support

## 🛠️ Usage with Tiled

### Import as Collection
1. In Tiled, go to **Map → Add External Tileset**
2. Choose **Collection of Images**
3. Select all tiles from a category folder
4. Set tile size to 16x16

### Import Individual Tiles
1. Drag and drop tiles directly onto your map
2. Use the tile_info.json for reference

## 📝 Tile Categories

### Terrain
- Grass variations (light, dark, forest, etc.)
- Dirt and earth tiles
- Stone and rock surfaces
- Sand and beach tiles

### Water
- Animated water frames (4 frames)
- Shore tiles (all directions)
- Corner pieces for smooth transitions

### Objects
- Trees (oak, pine, dead)
- Bushes and plants
- Rocks and stones
- Flowers and decorations

### Building
- Roof tiles (red, blue, green)
- Wall types (brick, stone, wood)
- Doors and windows

### Interior
- Floor types (wood, tile)
- Furniture (table, chair, bed, bookshelf)
- Carpets and rugs

### UI
- Button states (normal, hover, pressed)
- Icons for game interface

## 🔧 Metadata

The `tile_info.json` file contains detailed information for each tile:
- ID: Unique identifier
- Name: Descriptive name
- Category: Tile category
- Position: Original position in tileset
- Source: Source tileset name

## 💡 Tips

- Use the ID for programmatic reference
- Use the name for human-readable identification
- Categories help organize your tileset library
- All tiles maintain transparency where applicable

---
Created with the Untold Story Tileset Processor
"""

# Hauptausführung
if __name__ == "__main__":
    processor = TilesetProcessor()
    output_file = Path("/Users/leon/Desktop/untold_story/individual_tiles.zip")
    
    print("🎮 Creating Individual Tiles Package")
    print("=" * 50)
    print()
    
    # Verarbeite und erstelle ZIP
    print("Processing tilesets...")
    stats = processor.process_and_create_zip(str(output_file))
    
    print()
    print("✅ Successfully created tile package!")
    print(f"📦 Location: {output_file}")
    print(f"💾 Size: {output_file.stat().st_size / 1024:.1f} KB")
    print()
    print("📊 Summary:")
    print(f"   Total tiles: {stats['total_tiles']}")
    for cat, count in sorted(stats['categories'].items()):
        print(f"   {cat:10s}: {count:3d} tiles")
