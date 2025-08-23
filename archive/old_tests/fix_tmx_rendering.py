#!/usr/bin/env python3
"""
Quick Fix für TMX Tile-Rendering
Patcht das bestehende System für korrektes GID-Mapping
"""

import sys
import os
from pathlib import Path
import pygame
import xml.etree.ElementTree as ET

# Add project root
sys.path.insert(0, str(Path(__file__).parent))


def patch_sprite_manager():
    """
    Erweitert den SpriteManager um direktes GID-zu-Surface Mapping
    """
    from engine.graphics.sprite_manager import SpriteManager
    
    # Füge neue Methode hinzu für GID-basiertes Loading
    def load_tileset_with_gids(self, tsx_path: Path, firstgid: int):
        """Lädt ein Tileset und mappt GIDs direkt zu Surfaces"""
        try:
            # Parse TSX
            tree = ET.parse(tsx_path)
            root = tree.getroot()
            
            tile_width = int(root.get('tilewidth', 16))
            tile_height = int(root.get('tileheight', 16))
            tile_count = int(root.get('tilecount', 0))
            columns = int(root.get('columns', 1))
            
            # Finde Bild
            image_elem = root.find('image')
            if not image_elem:
                return
            
            image_source = image_elem.get('source', '')
            image_path = tsx_path.parent / image_source
            
            if not image_path.exists():
                print(f"⚠️ Tileset-Bild nicht gefunden: {image_path}")
                return
            
            # Lade Tileset-Bild
            tileset_surface = pygame.image.load(str(image_path)).convert_alpha()
            
            # Erstelle GID-Mapping
            if not hasattr(self, 'gid_to_surface'):
                self.gid_to_surface = {}
            
            # Extrahiere Tiles
            for local_id in range(tile_count):
                col = local_id % columns
                row = local_id // columns
                
                x = col * tile_width
                y = row * tile_height
                
                # Extrahiere Tile
                tile_surface = pygame.Surface((tile_width, tile_height), pygame.SRCALPHA)
                tile_surface.blit(tileset_surface, (0, 0), (x, y, tile_width, tile_height))
                
                # Skaliere falls nötig
                if tile_width != 16 or tile_height != 16:
                    tile_surface = pygame.transform.scale(tile_surface, (16, 16))
                
                # Speichere mit GID
                gid = firstgid + local_id
                self.gid_to_surface[gid] = tile_surface
            
            print(f"✅ Tileset geladen: {tsx_path.name} ({tile_count} tiles, firstgid={firstgid})")
            
        except Exception as e:
            print(f"❌ Fehler beim Laden von {tsx_path}: {e}")
    
    # Füge neue Methode zum Abrufen von Tiles per GID hinzu
    def get_tile_by_gid(self, gid: int):
        """Hole Tile-Surface direkt über GID"""
        if not hasattr(self, 'gid_to_surface'):
            self.gid_to_surface = {}
        
        # Entferne Flip-Flags
        clean_gid = gid & 0x0FFFFFFF
        
        return self.gid_to_surface.get(clean_gid)
    
    # Patche die Klasse
    SpriteManager.load_tileset_with_gids = load_tileset_with_gids
    SpriteManager.get_tile_by_gid = get_tile_by_gid
    
    print("✅ SpriteManager gepatcht")
    return SpriteManager


def load_tmx_tilesets(sprite_manager, tmx_path: Path):
    """Lade alle Tilesets aus einer TMX-Datei"""
    try:
        tree = ET.parse(tmx_path)
        root = tree.getroot()
        
        # Lade alle Tilesets
        for tileset_elem in root.findall('tileset'):
            firstgid = int(tileset_elem.get('firstgid', 1))
            source = tileset_elem.get('source', '')
            
            if source:
                # Finde TSX-Datei
                tsx_path = Path("assets/gfx/tiles") / source
                if not tsx_path.exists():
                    tsx_path = Path("data/maps") / source
                
                if tsx_path.exists():
                    sprite_manager.load_tileset_with_gids(tsx_path, firstgid)
        
        return True
    except Exception as e:
        print(f"❌ Fehler beim Laden der Tilesets: {e}")
        return False


def test_fixed_rendering():
    """Teste das gefixtete Rendering"""
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("TMX Fix Test - Untold Story")
    clock = pygame.time.Clock()
    
    # Patche und initialisiere SpriteManager
    patch_sprite_manager()
    from engine.graphics.sprite_manager import SpriteManager
    sprite_manager = SpriteManager.get()
    
    # Lade Tilesets für player_house
    tmx_path = Path("data/maps/player_house.tmx")
    if not tmx_path.exists():
        print(f"❌ Map nicht gefunden: {tmx_path}")
        return
    
    print(f"\n📋 Lade Map: {tmx_path.name}")
    load_tmx_tilesets(sprite_manager, tmx_path)
    
    # Parse Map-Daten
    tree = ET.parse(tmx_path)
    root = tree.getroot()
    
    width = int(root.get('width', 0))
    height = int(root.get('height', 0))
    print(f"Map-Größe: {width}x{height}")
    
    # Lade Layer
    layers = {}
    for layer_elem in root.findall('layer'):
        layer_name = layer_elem.get('name', 'unnamed')
        data_elem = layer_elem.find('data')
        
        if data_elem and data_elem.get('encoding') == 'csv':
            csv_text = data_elem.text.strip()
            layer_data = []
            
            for line in csv_text.split('\n'):
                if line.strip():
                    row = [int(x.strip()) for x in line.split(',') if x.strip()]
                    layer_data.append(row)
            
            layers[layer_name] = layer_data
            print(f"Layer geladen: {layer_name}")
    
    # Game Loop
    camera_x, camera_y = 0, 0
    running = True
    show_grid = False
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_g:
                    show_grid = not show_grid
                    print(f"Grid: {'AN' if show_grid else 'AUS'}")
        
        # Kamera-Bewegung
        keys = pygame.key.get_pressed()
        speed = 5
        if keys[pygame.K_LEFT]: camera_x -= speed
        if keys[pygame.K_RIGHT]: camera_x += speed
        if keys[pygame.K_UP]: camera_y -= speed
        if keys[pygame.K_DOWN]: camera_y += speed
        
        # Clear screen
        screen.fill((50, 50, 50))
        
        # Rendere alle Layer
        for layer_name, layer_data in layers.items():
            for y in range(len(layer_data)):
                for x in range(len(layer_data[y])):
                    gid = layer_data[y][x]
                    
                    if gid == 0:
                        continue
                    
                    # Hole Tile über GID
                    tile_surface = sprite_manager.get_tile_by_gid(gid)
                    
                    if tile_surface:
                        screen_x = x * 16 - camera_x
                        screen_y = y * 16 - camera_y
                        screen.blit(tile_surface, (screen_x, screen_y))
                    else:
                        # Platzhalter für fehlende Tiles
                        screen_x = x * 16 - camera_x
                        screen_y = y * 16 - camera_y
                        placeholder = pygame.Surface((16, 16))
                        placeholder.fill((255, 0, 255))
                        screen.blit(placeholder, (screen_x, screen_y))
        
        # Grid anzeigen
        if show_grid:
            for x in range(0, width * 16, 16):
                pygame.draw.line(screen, (100, 100, 100), 
                               (x - camera_x, 0), (x - camera_x, height * 16), 1)
            for y in range(0, height * 16, 16):
                pygame.draw.line(screen, (100, 100, 100), 
                               (0, y - camera_y), (width * 16, y - camera_y), 1)
        
        # Debug-Info
        font = pygame.font.Font(None, 24)
        info_texts = [
            f"Map: player_house.tmx",
            f"Kamera: ({camera_x}, {camera_y})",
            f"Layer: {len(layers)}",
            f"[G] Grid: {'AN' if show_grid else 'AUS'}",
            f"[Pfeiltasten] Bewegen"
        ]
        
        for i, text in enumerate(info_texts):
            text_surface = font.render(text, True, (255, 255, 255))
            screen.blit(text_surface, (10, 10 + i * 25))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()


def apply_fix_to_game():
    """Wendet den Fix auf das Hauptspiel an"""
    print("\n🔧 Wende Fix auf das Spiel an...")
    
    # Erstelle Patch-Datei
    patch_content = '''
# TMX Rendering Fix
# Füge diese Zeilen in engine/graphics/sprite_manager.py ein

def load_all_tmx_tilesets(self):
    """Lade alle Tilesets aus den TMX-Dateien"""
    from pathlib import Path
    import xml.etree.ElementTree as ET
    
    # Initialisiere GID-Mapping
    if not hasattr(self, 'gid_to_surface'):
        self.gid_to_surface = {}
    
    # Lade alle TMX-Dateien
    maps_dir = Path("data/maps")
    for tmx_file in maps_dir.glob("*.tmx"):
        try:
            tree = ET.parse(tmx_file)
            root = tree.getroot()
            
            for tileset_elem in root.findall('tileset'):
                firstgid = int(tileset_elem.get('firstgid', 1))
                source = tileset_elem.get('source', '')
                
                if source and source not in self._loaded_tilesets:
                    tsx_path = Path("assets/gfx/tiles") / source
                    if tsx_path.exists():
                        self.load_tileset_with_gids(tsx_path, firstgid)
                        self._loaded_tilesets.add(source)
        except:
            pass

# Rufe diese Methode in _load_tiles() auf:
# self.load_all_tmx_tilesets()
'''
    
    patch_file = Path("tmx_fix_patch.txt")
    patch_file.write_text(patch_content)
    print(f"✅ Patch-Anleitung erstellt: {patch_file}")
    
    return patch_file


def main():
    """Hauptfunktion"""
    print("🎮 TMX Rendering Fix für Untold Story")
    print("=" * 60)
    
    print("\nWähle eine Option:")
    print("1. Test-Rendering mit Fix")
    print("2. Analysiere TMX-Dateien")
    print("3. Erstelle Patch für Hauptspiel")
    print("4. Alles ausführen")
    
    choice = input("\nOption (1-4): ").strip()
    
    if choice == "1" or choice == "4":
        print("\n▶️ Starte Test-Rendering...")
        test_fixed_rendering()
    
    if choice == "2" or choice == "4":
        print("\n▶️ Analysiere TMX-Dateien...")
        os.system("python test_tmx_analysis.py")
    
    if choice == "3" or choice == "4":
        print("\n▶️ Erstelle Patch...")
        patch_file = apply_fix_to_game()
        print(f"\n📋 Patch-Anleitung in: {patch_file}")
    
    print("\n✅ Fertig!")
    print("\n💡 Nächste Schritte:")
    print("1. Teste das Rendering mit Option 1")
    print("2. Wenn es funktioniert, wende den Patch an")
    print("3. Starte das Hauptspiel mit: python main.py")


if __name__ == "__main__":
    main()
