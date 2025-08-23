#!/usr/bin/env python3
"""
Direkte Integration des TMX-Fixes in das bestehende System
Patcht die Area-Klasse, um TMX-Tiles korrekt zu rendern
"""

import shutil
from pathlib import Path
import json

def backup_file(file_path: Path):
    """Erstellt ein Backup einer Datei"""
    backup_path = file_path.with_suffix(file_path.suffix + '.backup')
    if not backup_path.exists():
        shutil.copy(file_path, backup_path)
        print(f"✅ Backup erstellt: {backup_path}")
    else:
        print(f"ℹ️  Backup existiert bereits: {backup_path}")

def patch_area_file():
    """Patcht die area.py Datei für korrektes TMX-Rendering"""
    area_path = Path("engine/world/area.py")
    
    if not area_path.exists():
        print(f"❌ Datei nicht gefunden: {area_path}")
        return False
    
    # Backup erstellen
    backup_file(area_path)
    
    # Neuer Area-Code mit TMX-Fix
    new_area_code = '''"""
Area - Repräsentiert eine spielbare Map-Region
Mit verbessertem TMX-Support und korrektem Tile-Rendering
"""

import pygame
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from engine.world.tiles import TILE_SIZE, TileType
from engine.world.map_loader import MapLoader, MapData
from engine.graphics.sprite_manager import SpriteManager
from engine.world.entity import Entity
from engine.world.npc_improved import ImprovedNPC as NPC
from engine.core.resources import resources

@dataclass
class AreaConfig:
    """Konfiguration für eine Area"""
    map_id: str
    name: str = ""
    music: Optional[str] = None
    encounter_rate: float = 0.0
    weather: Optional[str] = None

class Area:
    """Eine spielbare Map-Region mit TMX-Support"""
    
    def __init__(self, map_id: str):
        """
        Initialisiert eine Area aus einer Map-ID.
        
        Args:
            map_id: ID der zu ladenden Map (ohne Dateiendung)
        """
        self.map_id = map_id
        self.map_data: Optional[MapData] = None
        self.sprite_manager = SpriteManager.get()
        
        # Surfaces für jede Layer
        self.layer_surfaces: Dict[str, pygame.Surface] = {}
        
        # Entities und NPCs
        self.entities: List[Entity] = []
        self.npcs: List[NPC] = []
        
        # TMX-spezifische Daten
        self.tmx_path: Optional[Path] = None
        self.gid_to_surface: Dict[int, pygame.Surface] = {}
        
        # Lade die Map
        self._load_map()
        
    def _load_map(self):
        """Lädt die Map-Daten"""
        try:
            # Versuche TMX direkt zu laden
            tmx_path = Path("data/maps") / f"{self.map_id}.tmx"
            if tmx_path.exists():
                self.tmx_path = tmx_path
                self._load_tmx_direct()
            else:
                # Fallback auf MapLoader
                self.map_data = MapLoader.load_map(self.map_id)
                self._render_layers()
                
        except Exception as e:
            print(f"[Area] Fehler beim Laden der Map {self.map_id}: {e}")
            # Erstelle leere Map als Fallback
            self._create_empty_map()
    
    def _load_tmx_direct(self):
        """Lädt TMX-Map direkt mit korrektem Tile-Rendering"""
        print(f"[Area] Lade TMX direkt: {self.tmx_path}")
        
        # Parse TMX
        tree = ET.parse(self.tmx_path)
        root = tree.getroot()
        
        # Map-Eigenschaften
        self.width = int(root.get('width', 32))
        self.height = int(root.get('height', 32))
        self.tile_width = int(root.get('tilewidth', 16))
        self.tile_height = int(root.get('tileheight', 16))
        
        # Lade alle Tilesets und erstelle GID-Mapping
        self._load_tmx_tilesets(root)
        
        # Lade und rendere Layer
        self._load_tmx_layers(root)
        
        # Lade Objekte (Warps, NPCs, etc.)
        self._load_tmx_objects(root)
    
    def _load_tmx_tilesets(self, root):
        """Lädt alle Tilesets aus der TMX"""
        for tileset_elem in root.findall('tileset'):
            firstgid = int(tileset_elem.get('firstgid', 1))
            source = tileset_elem.get('source', '')
            
            if source:
                tsx_path = self.tmx_path.parent / source
                if tsx_path.exists():
                    self._load_tsx_tileset(tsx_path, firstgid)
    
    def _load_tsx_tileset(self, tsx_path: Path, firstgid: int):
        """Lädt ein einzelnes Tileset aus einer TSX-Datei"""
        try:
            tree = ET.parse(tsx_path)
            root = tree.getroot()
            
            tile_width = int(root.get('tilewidth', 16))
            tile_height = int(root.get('tileheight', 16))
            tile_count = int(root.get('tilecount', 0))
            columns = int(root.get('columns', 1))
            
            # Finde Bild
            image_elem = root.find('image')
            if image_elem is None:
                return
            
            # Konstruiere Bildpfad
            image_source = image_elem.get('source', '')
            if image_source.startswith('../../'):
                image_path = Path(image_source.replace('../../', ''))
            else:
                image_path = tsx_path.parent / image_source
            
            if not image_path.exists():
                print(f"[Area] Tileset-Bild nicht gefunden: {image_path}")
                return
            
            # Lade Tileset-Bild
            tileset_surface = pygame.image.load(str(image_path)).convert_alpha()
            
            # Extrahiere einzelne Tiles
            for tile_id in range(tile_count):
                col = tile_id % columns
                row = tile_id // columns
                
                x = col * tile_width
                y = row * tile_height
                
                # Extrahiere Tile
                tile_surf = pygame.Surface((tile_width, tile_height), pygame.SRCALPHA)
                tile_surf.blit(tileset_surface, (0, 0), (x, y, tile_width, tile_height))
                
                # Skaliere auf TILE_SIZE falls nötig
                if tile_width != TILE_SIZE or tile_height != TILE_SIZE:
                    tile_surf = pygame.transform.scale(tile_surf, (TILE_SIZE, TILE_SIZE))
                
                # Speichere mit GID
                gid = firstgid + tile_id
                self.gid_to_surface[gid] = tile_surf
            
            print(f"[Area] Geladen: {tsx_path.name} - {tile_count} Tiles (firstgid={firstgid})")
            
        except Exception as e:
            print(f"[Area] Fehler beim Laden von Tileset {tsx_path}: {e}")
    
    def _load_tmx_layers(self, root):
        """Lädt und rendert alle Layer aus der TMX"""
        for layer_elem in root.findall('layer'):
            layer_name = layer_elem.get('name', 'default')
            layer_width = int(layer_elem.get('width', self.width))
            layer_height = int(layer_elem.get('height', self.height))
            
            # Erstelle Surface für diesen Layer
            layer_surface = pygame.Surface(
                (layer_width * TILE_SIZE, layer_height * TILE_SIZE),
                pygame.SRCALPHA
            )
            
            # Parse Tile-Daten
            data_elem = layer_elem.find('data')
            if data_elem is not None:
                encoding = data_elem.get('encoding', 'csv')
                
                if encoding == 'csv':
                    # Parse CSV-Daten
                    csv_text = data_elem.text.strip()
                    y = 0
                    for line in csv_text.split('\\n'):
                        if not line.strip():
                            continue
                        
                        x = 0
                        for gid_str in line.split(','):
                            if not gid_str.strip():
                                continue
                            
                            gid = int(gid_str.strip())
                            
                            # Entferne Flip-Flags
                            FLIP_FLAGS = 0x80000000 | 0x40000000 | 0x20000000
                            clean_gid = gid & ~FLIP_FLAGS
                            
                            # Hole Tile-Surface
                            if clean_gid > 0 and clean_gid in self.gid_to_surface:
                                tile_surf = self.gid_to_surface[clean_gid]
                                layer_surface.blit(tile_surf, (x * TILE_SIZE, y * TILE_SIZE))
                            
                            x += 1
                        y += 1
            
            # Speichere gerenderten Layer
            self.layer_surfaces[layer_name] = layer_surface
            print(f"[Area] Layer gerendert: {layer_name}")
    
    def _load_tmx_objects(self, root):
        """Lädt Objekte (Warps, NPCs, etc.) aus der TMX"""
        for objectgroup_elem in root.findall('objectgroup'):
            group_name = objectgroup_elem.get('name', '')
            
            for obj_elem in objectgroup_elem.findall('object'):
                obj_type = obj_elem.get('type', '').lower()
                obj_name = obj_elem.get('name', '')
                obj_x = float(obj_elem.get('x', 0))
                obj_y = float(obj_elem.get('y', 0))
                
                # Konvertiere zu Tile-Koordinaten
                tile_x = int(obj_x // TILE_SIZE)
                tile_y = int(obj_y // TILE_SIZE)
                
                # Verarbeite nach Typ
                if obj_type == 'npc':
                    # Erstelle NPC
                    self._create_npc(tile_x, tile_y, obj_name)
                elif obj_type == 'warp':
                    # Speichere Warp-Info (wird vom MapLoader verarbeitet)
                    pass
    
    def _create_npc(self, tile_x: int, tile_y: int, npc_id: str):
        """Erstellt einen NPC"""
        try:
            npc = NPC(
                x=tile_x * TILE_SIZE,
                y=tile_y * TILE_SIZE,
                npc_id=npc_id
            )
            self.npcs.append(npc)
        except Exception as e:
            print(f"[Area] Fehler beim Erstellen von NPC {npc_id}: {e}")
    
    def _render_layers(self):
        """Rendert Layer aus MapData (Fallback für nicht-TMX)"""
        if not self.map_data:
            return
        
        for layer_name, layer_data in self.map_data.layers.items():
            if layer_name == "collision":
                continue  # Collision wird nicht gerendert
            
            # Erstelle Surface für Layer
            surface = pygame.Surface(
                (self.map_data.width * TILE_SIZE, 
                 self.map_data.height * TILE_SIZE),
                pygame.SRCALPHA
            )
            
            # Rendere jeden Tile
            for y, row in enumerate(layer_data):
                for x, tile in enumerate(row):
                    if tile:
                        # Hole Sprite
                        sprite = self._get_tile_sprite(tile)
                        if sprite:
                            surface.blit(sprite, (x * TILE_SIZE, y * TILE_SIZE))
            
            self.layer_surfaces[layer_name] = surface
    
    def _get_tile_sprite(self, tile_id) -> Optional[pygame.Surface]:
        """Holt ein Tile-Sprite"""
        # Versuche verschiedene Methoden
        sprite = self.sprite_manager.get_tile_sprite(tile_id)
        if sprite:
            return sprite
        
        # Fallback auf direktes Tile
        if isinstance(tile_id, str):
            sprite = self.sprite_manager.get_tile(tile_id)
            if sprite:
                return sprite
        
        # Fallback: Erstelle farbiges Rechteck basierend auf ID
        surface = pygame.Surface((TILE_SIZE, TILE_SIZE))
        
        # Verschiedene Farben für verschiedene Tile-Typen
        if isinstance(tile_id, str):
            if 'grass' in tile_id:
                surface.fill((34, 139, 34))
            elif 'dirt' in tile_id or 'path' in tile_id:
                surface.fill((139, 90, 43))
            elif 'water' in tile_id:
                surface.fill((64, 164, 223))
            elif 'wall' in tile_id:
                surface.fill((105, 105, 105))
            else:
                surface.fill((128, 128, 128))
        else:
            # Numerische ID: Verwende Farbpalette
            colors = [
                (34, 139, 34),   # Grün (Gras)
                (139, 90, 43),   # Braun (Erde)
                (64, 164, 223),  # Blau (Wasser)
                (105, 105, 105), # Grau (Stein)
                (255, 215, 0),   # Gold (Sand)
            ]
            color = colors[tile_id % len(colors)]
            surface.fill(color)
        
        return surface
    
    def _create_empty_map(self):
        """Erstellt eine leere Fallback-Map"""
        self.width = 20
        self.height = 15
        
        # Erstelle einfachen Gras-Hintergrund
        surface = pygame.Surface(
            (self.width * TILE_SIZE, self.height * TILE_SIZE)
        )
        surface.fill((34, 139, 34))  # Grün
        
        self.layer_surfaces["ground"] = surface
    
    def draw(self, screen: pygame.Surface, camera_x: int = 0, camera_y: int = 0):
        """
        Zeichnet die Area auf den Bildschirm.
        
        Args:
            screen: Ziel-Surface
            camera_x: Kamera X-Offset
            camera_y: Kamera Y-Offset
        """
        # Zeichne Layer in korrekter Reihenfolge
        layer_order = ["ground", "decor", "Tile Layer 1", "Tile Layer 2", 
                      "objects", "Tile Layer 3", "overlay", "Tile Layer 4"]
        
        for layer_name in layer_order:
            if layer_name in self.layer_surfaces:
                screen.blit(self.layer_surfaces[layer_name], 
                          (-camera_x, -camera_y))
    
    def update(self, dt: float):
        """
        Aktualisiert die Area.
        
        Args:
            dt: Delta-Zeit in Sekunden
        """
        # Update NPCs
        for npc in self.npcs:
            npc.update(dt)
        
        # Update Entities  
        for entity in self.entities:
            entity.update(dt)
    
    def get_collision_at(self, x: int, y: int) -> bool:
        """
        Prüft Kollision an einer Position.
        
        Args:
            x: X-Position in Pixeln
            y: Y-Position in Pixeln
            
        Returns:
            True wenn Kollision, sonst False
        """
        # Konvertiere zu Tile-Koordinaten
        tile_x = x // TILE_SIZE
        tile_y = y // TILE_SIZE
        
        # Prüfe Map-Grenzen
        if self.map_data:
            if tile_x < 0 or tile_x >= self.map_data.width:
                return True
            if tile_y < 0 or tile_y >= self.map_data.height:
                return True
            
            # Prüfe Collision-Layer
            if "collision" in self.map_data.layers:
                collision_layer = self.map_data.layers["collision"]
                if collision_layer[tile_y][tile_x]:
                    return True
        else:
            # TMX-basierte Kollision
            if hasattr(self, 'width') and hasattr(self, 'height'):
                if tile_x < 0 or tile_x >= self.width:
                    return True
                if tile_y < 0 or tile_y >= self.height:
                    return True
        
        # Prüfe NPC-Kollisionen
        for npc in self.npcs:
            npc_tile_x = npc.x // TILE_SIZE
            npc_tile_y = npc.y // TILE_SIZE
            if npc_tile_x == tile_x and npc_tile_y == tile_y:
                return True
        
        return False
    
    def get_warp_at(self, x: int, y: int):
        """
        Holt Warp-Informationen an einer Position.
        
        Args:
            x: X-Position in Pixeln
            y: Y-Position in Pixeln
            
        Returns:
            Warp-Objekt oder None
        """
        if not self.map_data:
            return None
        
        tile_x = x // TILE_SIZE
        tile_y = y // TILE_SIZE
        
        for warp in self.map_data.warps:
            if warp.x == tile_x and warp.y == tile_y:
                return warp
        
        return None
    
    def get_trigger_at(self, x: int, y: int):
        """
        Holt Trigger-Informationen an einer Position.
        
        Args:
            x: X-Position in Pixeln
            y: Y-Position in Pixeln
            
        Returns:
            Trigger-Objekt oder None
        """
        if not self.map_data:
            return None
        
        tile_x = x // TILE_SIZE
        tile_y = y // TILE_SIZE
        
        for trigger in self.map_data.triggers:
            if trigger.x == tile_x and trigger.y == tile_y:
                return trigger
        
        return None
'''
    
    # Schreibe neue Area-Datei
    with open(area_path, 'w', encoding='utf-8') as f:
        f.write(new_area_code)
    
    print(f"✅ Area-Datei gepatcht: {area_path}")
    return True

def verify_tileset_images():
    """Verifiziert, dass alle benötigten Tileset-Bilder vorhanden sind"""
    tilesets_dir = Path("assets/gfx/tiles/tilesets")
    required_images = [
        "tiles_building_preview.png",
        "tiles_interior_preview.png",
        "tiles_ground_preview.png",
        "tiles_terrain_preview.png",
        "objects_preview.png"
    ]
    
    print("\n📁 Überprüfe Tileset-Bilder:")
    all_present = True
    
    for image in required_images:
        image_path = tilesets_dir / image
        if image_path.exists():
            print(f"  ✅ {image}")
        else:
            print(f"  ❌ {image} - FEHLT!")
            all_present = False
    
    return all_present

def create_test_script():
    """Erstellt ein Test-Skript zum Überprüfen des Fixes"""
    test_script = '''#!/usr/bin/env python3
"""
Test-Skript für TMX-Rendering
"""

import pygame
import sys
from pathlib import Path

# Füge Projekt-Root zum Path hinzu
sys.path.insert(0, str(Path.cwd()))

from engine.world.area import Area
from engine.graphics.sprite_manager import SpriteManager

def test_tmx_rendering():
    """Testet das TMX-Rendering mit der gepatchten Area-Klasse"""
    
    # Initialisiere Pygame
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption("TMX Rendering Test")
    clock = pygame.time.Clock()
    
    # Initialisiere SpriteManager
    sprite_manager = SpriteManager.get()
    
    # Lade Test-Map
    print("Lade player_house Map...")
    area = Area("player_house")
    
    # Kamera-Position
    camera_x = 0
    camera_y = 0
    
    # Game Loop
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        
        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Kamera-Steuerung
        keys = pygame.key.get_pressed()
        camera_speed = 200 * dt  # Pixel pro Sekunde
        
        if keys[pygame.K_LEFT]:
            camera_x -= camera_speed
        if keys[pygame.K_RIGHT]:
            camera_x += camera_speed
        if keys[pygame.K_UP]:
            camera_y -= camera_speed
        if keys[pygame.K_DOWN]:
            camera_y += camera_speed
        
        # Update
        area.update(dt)
        
        # Draw
        screen.fill((0, 0, 0))
        area.draw(screen, camera_x, camera_y)
        
        # Info-Text
        font = pygame.font.Font(None, 36)
        text = font.render(f"TMX Test - Pfeiltasten zum Bewegen", True, (255, 255, 255))
        screen.blit(text, (10, 10))
        
        pygame.display.flip()
    
    pygame.quit()
    print("Test beendet.")

if __name__ == "__main__":
    test_tmx_rendering()
'''
    
    test_path = Path("test_tmx_rendering.py")
    with open(test_path, 'w') as f:
        f.write(test_script)
    
    print(f"✅ Test-Skript erstellt: {test_path}")

def main():
    """Hauptfunktion"""
    print("=" * 60)
    print("TMX RENDERING FIX - DIREKTE INTEGRATION")
    print("=" * 60)
    
    # 1. Verifiziere Tileset-Bilder
    if not verify_tileset_images():
        print("\n⚠️  Warnung: Nicht alle Tileset-Bilder vorhanden!")
        print("   Das Rendering könnte fehlschlagen.")
    
    # 2. Patche Area-Datei
    print("\n📝 Patche Area-Klasse...")
    if patch_area_file():
        print("✅ Area-Klasse erfolgreich gepatcht!")
    else:
        print("❌ Fehler beim Patchen der Area-Klasse")
        return
    
    # 3. Erstelle Test-Skript
    print("\n🧪 Erstelle Test-Skript...")
    create_test_script()
    
    print("\n" + "=" * 60)
    print("✅ FIX ERFOLGREICH INTEGRIERT")
    print("=" * 60)
    
    print("\n📋 Nächste Schritte:")
    print("1. Führe das Test-Skript aus: python3 test_tmx_rendering.py")
    print("2. Verwende die Pfeiltasten zum Bewegen der Kamera")
    print("3. Prüfe, ob die Tiles korrekt angezeigt werden")
    print("\nFalls Probleme auftreten:")
    print("- Stelle sicher, dass alle Tileset-Bilder vorhanden sind")
    print("- Prüfe die Konsolen-Ausgabe auf Fehler")
    print("- Restore das Backup: engine/world/area.py.backup")

if __name__ == "__main__":
    main()
