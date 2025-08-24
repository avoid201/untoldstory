#!/usr/bin/env python3
"""
Erstellt Individual Tiles basierend auf den Tileset-Mustern
Korrigierte Version mit ImageDraw
"""

import os
import sys
from PIL import Image, ImageDraw
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
                draw = ImageDraw.Draw(tile)
                
                # Trees (first 4x4)
                if y < 4 and x < 4:
                    # Tree top
                    if y < 2:
                        draw.ellipse([(2, 2), (14, 14)], fill=(0, 100 + x*20, 0, 255))
                    # Tree trunk
                    else:
                        draw.rectangle([(6, 0), (10, 16)], fill=(101, 67, 33, 255))
                # Bushes (4x4)
                elif y < 4 and x < 8:
                    draw.ellipse([(3, 5), (13, 13)], fill=(0, 128, 0, 255))
                # Rocks (4x4)
                elif y < 4:
                    gray = 80 + (x * 10)
                    draw.ellipse([(4, 6), (12, 14)], fill=(gray, gray, gray, 255))
                # Flowers (next 4 rows)
                elif y < 8:
                    # Stem
                    draw.rectangle([(7, 8), (9, 16)], fill=(0, 128, 0, 255))
                    # Flower
                    colors = [(255, 0, 0), (255, 255, 0), (255, 0, 255), (255, 255, 255)]
                    flower_color = colors[(x + y) % 4]
                    draw.ellipse([(5, 4), (11, 10)], fill=flower_color + (255,))
                # Fences
                elif y < 10:
                    draw.rectangle([(0, 7), (16, 9)], fill=(139, 69, 19, 255))
                    if x % 2 == 0:
                        draw.rectangle([(7, 0), (9, 16)], fill=(139, 69, 19, 255))
                # Signs and posts
                elif y < 12:
                    draw.rectangle([(7, 4), (9, 16)], fill=(101, 67, 33, 255))
                    if x % 3 == 0:
                        draw.rectangle([(3, 2), (13, 8)], fill=(160, 82, 45, 255))
                # Items/Collectibles
                else:
                    # Coins, gems, etc
                    item_colors = [(255, 215, 0), (192, 192, 192), (255, 0, 0), (0, 255, 0)]
                    item_color = item_colors[x % 4]
                    draw.ellipse([(5, 5), (11, 11)], fill=item_color + (255,))
                
                img2.paste(tile, (x * 16, y * 16))
        tilesets.append(('objects', img2))
        
        # Tileset 3: Water Animations (128x128)
        img3 = Image.new('RGBA', (128, 128), (0, 0, 0, 0))
        for y in range(8):
            for x in range(8):
                tile = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
                draw = ImageDraw.Draw(tile)
                
                # Animated water frames
                if y < 4:
                    blue_val = 200 + ((x + y) * 10) % 55
                    draw.rectangle([(0, 0), (16, 16)], fill=(30, 144, blue_val, 255))
                    # Wave pattern
                    for wy in range(2, 14, 3):
                        wave_x = (wy + x * 2) % 16
                        draw.rectangle([(wave_x, wy), (min(wave_x + 3, 15), wy + 1)], 
                                     fill=(60, 180, 255, 255))
                # Shore tiles
                else:
                    # Sand base
                    draw.rectangle([(0, 0), (16, 16)], fill=(255, 228, 181, 255))
                    # Water edges
                    if x == 0:  # Left shore
                        draw.rectangle([(0, 0), (8, 16)], fill=(30, 144, 255, 255))
                    elif x == 1:  # Right shore
                        draw.rectangle([(8, 0), (16, 16)], fill=(30, 144, 255, 255))
                    elif x == 2:  # Top shore
                        draw.rectangle([(0, 0), (16, 8)], fill=(30, 144, 255, 255))
                    elif x == 3:  # Bottom shore
                        draw.rectangle([(0, 8), (16, 16)], fill=(30, 144, 255, 255))
                    elif x == 4:  # Corner TL
                        draw.rectangle([(0, 0), (8, 8)], fill=(30, 144, 255, 255))
                    elif x == 5:  # Corner TR
                        draw.rectangle([(8, 0), (16, 8)], fill=(30, 144, 255, 255))
                    elif x == 6:  # Corner BL
                        draw.rectangle([(0, 8), (8, 16)], fill=(30, 144, 255, 255))
                    elif x == 7:  # Corner BR
                        draw.rectangle([(8, 8), (16, 16)], fill=(30, 144, 255, 255))
                
                img3.paste(tile, (x * 16, y * 16))
        tilesets.append(('water', img3))
        
        # Tileset 4: Buildings (192x128)
        img4 = Image.new('RGBA', (192, 128), (0, 0, 0, 0))
        for y in range(8):
            for x in range(12):
                tile = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
                draw = ImageDraw.Draw(tile)
                
                # Roofs
                if y < 3:
                    roof_colors = [(150, 50, 50), (50, 50, 150), (50, 150, 50)]
                    roof_color = roof_colors[x % 3]
                    draw.rectangle([(0, 0), (16, 16)], fill=roof_color + (255,))
                    # Roof tiles pattern
                    for rx in range(0, 16, 4):
                        draw.line([(rx, 0), (rx, 16)], fill=(0, 0, 0, 100), width=1)
                # Walls
                elif y < 6:
                    wall_color = (200, 180, 140)
                    draw.rectangle([(0, 0), (16, 16)], fill=wall_color + (255,))
                    # Brick pattern
                    for by in range(0, 16, 4):
                        draw.line([(0, by), (16, by)], fill=(150, 130, 90, 255), width=1)
                        if by % 8 == 0:
                            for bx in range(0, 16, 8):
                                draw.line([(bx, by), (bx, by+4)], fill=(150, 130, 90, 255), width=1)
                        else:
                            for bx in range(4, 16, 8):
                                draw.line([(bx, by), (bx, by+4)], fill=(150, 130, 90, 255), width=1)
                # Doors and Windows
                else:
                    if x % 2 == 0:
                        # Door
                        draw.rectangle([(2, 0), (14, 16)], fill=(101, 67, 33, 255))
                        draw.ellipse([(6, 7), (10, 11)], fill=(70, 40, 20, 255))  # Handle
                    else:
                        # Window
                        draw.rectangle([(0, 0), (16, 16)], fill=(200, 180, 140, 255))  # Wall
                        draw.rectangle([(2, 2), (14, 14)], fill=(135, 206, 235, 255))  # Glass
                        # Frame
                        draw.line([(8, 2), (8, 14)], fill=(101, 67, 33, 255), width=2)
                        draw.line([(2, 8), (14, 8)], fill=(101, 67, 33, 255), width=2)
                
                img4.paste(tile, (x * 16, y * 16))
        tilesets.append(('building', img4))
        
        # Tileset 5: Interior/Furniture (128x96)
        img5 = Image.new('RGBA', (128, 96), (0, 0, 0, 0))
        for y in range(6):
            for x in range(8):
                tile = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
                draw = ImageDraw.Draw(tile)
                
                # Floors
                if y < 2:
                    if x < 4:
                        # Wood floor
                        draw.rectangle([(0, 0), (16, 16)], fill=(139, 69, 19, 255))
                        for fy in range(0, 16, 2):
                            draw.line([(0, fy), (16, fy)], fill=(160, 82, 45, 255), width=1)
                    else:
                        # Tile floor
                        draw.rectangle([(0, 0), (16, 16)], fill=(200, 200, 200, 255))
                        draw.rectangle([(0, 0), (1, 16)], fill=(150, 150, 150, 255))
                        draw.rectangle([(0, 0), (16, 1)], fill=(150, 150, 150, 255))
                # Furniture
                elif y < 4:
                    furniture_color = (101, 67, 33)
                    if x == 0:  # Table
                        draw.rectangle([(2, 4), (14, 12)], fill=furniture_color + (255,))
                        draw.rectangle([(3, 12), (5, 16)], fill=furniture_color + (255,))
                        draw.rectangle([(11, 12), (13, 16)], fill=furniture_color + (255,))
                    elif x == 1:  # Chair
                        draw.rectangle([(4, 6), (12, 14)], fill=furniture_color + (255,))
                        draw.rectangle([(4, 2), (12, 8)], fill=furniture_color + (255,))
                    elif x == 2:  # Bed
                        draw.rectangle([(1, 4), (15, 16)], fill=(139, 0, 0, 255))
                        draw.rectangle([(2, 2), (14, 6)], fill=(255, 255, 255, 255))
                    elif x == 3:  # Bookshelf
                        draw.rectangle([(2, 0), (14, 16)], fill=furniture_color + (255,))
                        for sy in range(2, 14, 4):
                            draw.rectangle([(3, sy), (13, sy+3)], fill=(0, 0, 128, 255))
                    elif x == 4:  # Chest
                        draw.rectangle([(3, 6), (13, 14)], fill=(139, 90, 43, 255))
                        draw.rectangle([(7, 5), (9, 7)], fill=(255, 215, 0, 255))
                    else:  # Decorations
                        color = ((x*40)%255, (y*60)%255, 100, 255)
                        draw.ellipse([(5, 5), (11, 11)], fill=color)
                # Carpets
                else:
                    carpet_colors = [(139, 0, 0), (0, 0, 139), (0, 139, 0), (139, 0, 139)]
                    carpet_color = carpet_colors[x % 4]
                    draw.rectangle([(0, 0), (16, 16)], fill=carpet_color + (255,))
                    # Pattern
                    for cx in range(2, 14, 3):
                        for cy in range(2, 14, 3):
                            draw.ellipse([(cx, cy), (cx+2, cy+2)], fill=(255, 215, 0, 255))
                
                img5.paste(tile, (x * 16, y * 16))
        tilesets.append(('interior', img5))
        
        # Tileset 6: UI Elements (128x32)
        img6 = Image.new('RGBA', (128, 32), (0, 0, 0, 0))
        for y in range(2):
            for x in range(8):
                tile = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
                draw = ImageDraw.Draw(tile)
                
                if y == 0:
                    # Buttons
                    draw.rectangle([(1, 1), (15, 15)], fill=(192, 192, 192, 255))
                    draw.rectangle([(2, 2), (14, 14)], fill=(128, 128, 128, 255))
                    # Button states
                    if x % 3 == 0:  # Normal
                        draw.rectangle([(3, 3), (13, 13)], fill=(160, 160, 160, 255))
                    elif x % 3 == 1:  # Hover
                        draw.rectangle([(3, 3), (13, 13)], fill=(180, 180, 180, 255))
                    else:  # Pressed
                        draw.rectangle([(3, 3), (13, 13)], fill=(100, 100, 100, 255))
                else:
                    # Icons
                    icon_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
                    icon_color = icon_colors[x % 4]
                    if x < 4:
                        # Simple shapes
                        draw.ellipse([(4, 4), (12, 12)], fill=icon_color + (255,))
                    else:
                        # Diamonds
                        draw.polygon([(8, 2), (14, 8), (8, 14), (2, 8)], fill=icon_color + (255,))
                
                img6.paste(tile, (x * 16, y * 16))
        tilesets.append(('ui', img6))
        
        # Tileset 7: Special/Decoration (96x64)
        img7 = Image.new('RGBA', (96, 64), (0, 0, 0, 0))
        for y in range(4):
            for x in range(6):
                tile = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
                draw = ImageDraw.Draw(tile)
                
                if y == 0:  # Gems
                    gem_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), 
                                 (255, 255, 0), (255, 0, 255), (0, 255, 255)]
                    if x < 6:
                        color = gem_colors[x]
                        draw.polygon([(8, 2), (14, 8), (8, 14), (2, 8)], fill=color + (255,))
                elif y == 1:  # Keys and items
                    # Key shape
                    draw.ellipse([(5, 3), (11, 9)], fill=(255, 215, 0, 255))
                    draw.rectangle([(7, 8), (9, 14)], fill=(255, 215, 0, 255))
                    if x % 2 == 0:
                        draw.rectangle([(6, 13), (10, 14)], fill=(255, 215, 0, 255))
                elif y == 2:  # Potions
                    # Bottle shape
                    draw.ellipse([(5, 8), (11, 14)], fill=(100, 100, 100, 200))
                    draw.rectangle([(7, 4), (9, 9)], fill=(100, 100, 100, 200))
                    draw.rectangle([(6, 2), (10, 4)], fill=(139, 69, 19, 255))
                    # Liquid
                    potion_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255),
                                    (255, 255, 0), (255, 0, 255), (0, 255, 255)]
                    if x < 6:
                        draw.ellipse([(6, 9), (10, 13)], fill=potion_colors[x] + (180,))
                else:  # Misc decorations
                    draw.ellipse([(4, 4), (12, 12)], fill=(200, 200, 200, 255))
                    draw.ellipse([(6, 6), (10, 10)], fill=(150, 150, 150, 255))
                
                img7.paste(tile, (x * 16, y * 16))
        tilesets.append(('special', img7))
        
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
            },
            'special': {
                0: 'gem_red', 1: 'gem_green', 2: 'gem_blue',
                3: 'gem_yellow', 4: 'gem_purple', 5: 'gem_cyan',
                6: 'key_gold', 7: 'key_silver', 8: 'key_bronze',
                9: 'potion_health', 10: 'potion_mana', 11: 'potion_stamina'
            }
        }
        
        # Versuche spezifischen Namen zu finden
        if category in names:
            if isinstance(names[category], dict):
                if row in names[category]:
                    name_list = names[category][row]
                    if isinstance(name_list, list) and col < len(name_list):
                        return name_list[col]
                idx = row * 8 + col
                if idx in names[category]:
                    return names[category][idx]
            else:
                idx = row * 8 + col
                if idx in names[category]:
                    return names[category][idx]
        
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
├── special/     ({stats['categories'].get('special', 0)} tiles)
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

### Special
- Gems (6 colors)
- Keys (gold, silver, bronze)
- Potions (health, mana, stamina)
- Decorative elements

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
