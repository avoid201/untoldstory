# -*- coding: utf-8 -*-
from __future__ import annotations
import os
from pathlib import Path
from typing import Dict, Optional, Tuple, Any
import json
import pygame

from engine.world.tiles import TILE_SIZE

class SpriteManager:
    """
    Zentraler Asset-Cache. Lädt 16x16-Sprites aus assets/gfx/*:
      - tiles/*.png        → Tiles per Name (z.B. "grass", "path")
      - objects/*.png      → Objects per Name (z.B. "tv", "sign", "chair", "table")
      - player/player_*.png→ Richtungs-Sprites
      - npc/npcX_*.png     → NPC-Gruppen X=A,B,... mit Richtungen
      - monster/<id>.png   → Dex-ID als "1".."151"
    """

    _instance: Optional["SpriteManager"] = None

    @staticmethod
    def get() -> "SpriteManager":
        if SpriteManager._instance is None:
            SpriteManager._instance = SpriteManager()
        return SpriteManager._instance

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, project_root: Path = None):
        """Initialisiert den SpriteManager mit dem angegebenen Projektpfad."""
        self.project_root = project_root or Path.cwd()
        
        # Pfade zu den Asset-Ordnern
        self.tiles_dir = self.project_root / "assets" / "gfx" / "tiles" / "tilesets"  # Korrigiert: tilesets Ordner
        self.objects_dir = self.project_root / "assets" / "gfx" / "objects"
        self.player_dir = self.project_root / "assets" / "gfx" / "player"
        self.npc_dir = self.project_root / "assets" / "gfx" / "npc"
        self.monster_dir = self.project_root / "assets" / "gfx" / "monster"
        
        # Sprite-Caches
        self._tiles: Dict[str, pygame.Surface] = {}
        self._objects: Dict[str, pygame.Surface] = {}
        self._player_dir_map: Dict[str, pygame.Surface] = {}
        self._npc_dir_map: Dict[Tuple[str, str], pygame.Surface] = {}
        self._monster: Dict[str, pygame.Surface] = {}
        
        # Tile-Mappings
        self._tile_mappings: Dict[str, Any] = {}
        
        # Sprite-Cache für alle Sprites
        self.sprite_cache: Dict[str, pygame.Surface] = {}
        
        # Lazy Loading
        self._loaded = False
        
        # GID-zu-Surface Mapping für TMX-Support
        self.gid_to_surface: Dict[int, pygame.Surface] = {}
        self._loaded_tilesets = set()  # Track loaded tilesets to avoid duplicates

    # ---------- Public API ----------

    def _ensure_loaded(self) -> None:
        """Lädt alle Sprites, falls noch nicht geschehen."""
        if not self._loaded:
            self._ensure_display()
            self._load_tile_mappings()
            self._load_tiles()
            self._load_objects()
            self._load_player()
            self._load_npcs()
            self._load_monsters()
            self._update_sprite_cache()
            self._loaded = True
    
    def _ensure_display(self) -> None:
        """Stellt sicher, dass pygame.display initialisiert ist."""
        try:
            pygame.display.get_surface()
        except pygame.error:
            # Display nicht initialisiert, erstelle einen temporären
            pygame.display.set_mode((320, 180))
            print("[SpriteManager] WARN: Created temporary display for sprite loading")
    
    def _update_sprite_cache(self) -> None:
        """Aktualisiert das globale sprite_cache mit allen geladenen Sprites."""
        self.sprite_cache.clear()
        
        # Tiles hinzufügen
        for name, surf in self._tiles.items():
            self.sprite_cache[f"tile_{name}"] = surf
        
        # Objects hinzufügen  
        for name, surf in self._objects.items():
            self.sprite_cache[f"object_{name}"] = surf
            
        # Player sprites hinzufügen
        for direction, surf in self._player_dir_map.items():
            self.sprite_cache[f"player_{direction}"] = surf
            
        # NPC sprites hinzufügen
        for (npc_id, direction), surf in self._npc_dir_map.items():
            self.sprite_cache[f"{npc_id}_{direction}"] = surf
            
        # Monster sprites hinzufügen
        for dex_id, surf in self._monster.items():
            self.sprite_cache[f"monster_{dex_id}"] = surf

    # Tiles / Objects by name (filename without .png)
    def get_tile(self, name: str) -> Optional[pygame.Surface]:
        self._ensure_loaded()
        return self._tiles.get(name)

    def get_object(self, name: str) -> Optional[pygame.Surface]:
        self._ensure_loaded()
        return self._objects.get(name)

    # Player by direction: "up","down","left","right"
    def get_player(self, direction: str) -> Optional[pygame.Surface]:
        self._ensure_loaded()
        return self._player_dir_map.get(direction)

    # NPC by id & direction: id like "npcA","npcB"
    def get_npc(self, npc_id: str, direction: str) -> Optional[pygame.Surface]:
        self._ensure_loaded()
        return self._npc_dir_map.get((npc_id, direction))

    # Monsters by dex id "1".."151" (also int supported)
    def get_monster(self, dex_id) -> Optional[pygame.Surface]:
        self._ensure_loaded()
        key = str(int(dex_id))
        return self._monster.get(key)
    
    # Universal sprite getter for compatibility
    def get_sprite(self, sprite_id: str) -> Optional[pygame.Surface]:
        """Allgemeine Methode zum Holen von Sprites nach ID."""
        self._ensure_loaded()
        return self.sprite_cache.get(sprite_id)
    
    def get_tile_by_gid(self, gid: int) -> Optional[pygame.Surface]:
        """Hole ein Tile direkt über seine GID (für TMX-Support)."""
        self._ensure_loaded()
        
        # Entferne Flip-Flags von der GID
        FLIPPED_HORIZONTALLY = 0x80000000
        FLIPPED_VERTICALLY = 0x40000000
        FLIPPED_DIAGONALLY = 0x20000000
        clean_gid = gid & ~(FLIPPED_HORIZONTALLY | FLIPPED_VERTICALLY | FLIPPED_DIAGONALLY)
        
        # Versuche zuerst das GID-Mapping
        if clean_gid in self.gid_to_surface:
            return self.gid_to_surface[clean_gid]
        
        # Fallback auf normales Tile-Loading
        return self.get_tile_sprite(clean_gid)
    
    def load_tmx_tilesets(self, tmx_path: Path) -> None:
        """Lade alle Tilesets aus einer TMX-Datei."""
        try:
            import xml.etree.ElementTree as ET
            
            tree = ET.parse(tmx_path)
            root = tree.getroot()
            
            # Lade alle Tilesets
            for tileset_elem in root.findall('tileset'):
                firstgid = int(tileset_elem.get('firstgid', 1))
                source = tileset_elem.get('source', '')
                
                if source and source not in self._loaded_tilesets:
                    # Finde TSX-Datei
                    tsx_path = Path("assets/gfx/tiles") / source
                    if not tsx_path.exists():
                        tsx_path = Path("data/maps") / source
                    
                    if tsx_path.exists():
                        self.load_tileset_with_gids(tsx_path, firstgid)
                        self._loaded_tilesets.add(source)
        except Exception as e:
            print(f"[SpriteManager] ERR loading TMX tilesets: {e}")
    
    def get_tile_sprite(self, tile_id) -> Optional[pygame.Surface]:
        """Holt ein Tile-Sprite nach Tile-ID oder -Name.

        Unterstützt:
        - int: GID aus TMX-Maps oder Legacy-ID
        - str: Name ohne .png (direkter Zugriff)
        """
        self._ensure_loaded()

        # Für Integer-IDs: Versuche zuerst GID-Mapping
        if isinstance(tile_id, int):
            # Versuche GID-basiertes Loading
            if hasattr(self, 'gid_to_surface') and tile_id in self.gid_to_surface:
                return self.gid_to_surface[tile_id]
            
            # Fallback auf get_tile_by_gid
            gid_result = self.get_tile_by_gid(tile_id)
            if gid_result is not None:
                return gid_result
        
        # String-basierter Zugriff
        if isinstance(tile_id, str):
            sprite = self.get_tile(tile_id)
            if sprite is not None:
                return sprite
            sprite = self.sprite_cache.get(f"tile_{tile_id}")
            if sprite is not None:
                return sprite
        else:
            # Legacy: Numerische ID über Mapping auflösen
            key = str(int(tile_id))
            mapping = self._tile_mappings.get(key)
            if mapping:
                sprite_file = mapping.get("sprite_file", "").lower()
                base = sprite_file.replace(".png", "")
                # Zuerst in tiles versuchen
                if base in self._tiles:
                    return self._tiles[base]
                # Dann in objects versuchen
                if base in self._objects:
                    return self._objects[base]
                # Fallback: vielleicht im Cache unter Dateiname
                cached = self.sprite_cache.get(base) or self.sprite_cache.get(f"tile_{base}")
                if cached is not None:
                    return cached

        # Fallback: Platzhalter
        surface = pygame.Surface((TILE_SIZE, TILE_SIZE))
        surface.fill((255, 0, 255))
        return surface

    # ---------- Internals ----------

    def _ensure_display(self) -> None:
        """Sorge dafür, dass convert()/convert_alpha() funktioniert."""
        if not pygame.get_init():
            pygame.init()
        if not pygame.display.get_init():
            # Fallback Display (wird vom Game überschrieben)
            pygame.display.set_mode((1, 1))

    def _load_dir_16px(self, folder: Path) -> Dict[str, pygame.Surface]:
        """Lädt alle PNGs aus einem Ordner, validiert 16x16 und konvertiert mit robusten Fallbacks."""
        out: Dict[str, pygame.Surface] = {}
        if not folder.exists():
            print(f"[SpriteManager] WARN: Ordner {folder} existiert nicht")
            return out
        
        for p in folder.glob("*.png"):
            try:
                surf = pygame.image.load(str(p)).convert_alpha()
                w, h = surf.get_size()
                
                if (w, h) != (TILE_SIZE, TILE_SIZE):
                    # Automatische Skalierung für falsche Größen mit Warnung
                    print(f"[SpriteManager] WARN {p.name}: expected {TILE_SIZE}x{TILE_SIZE}, got {w}x{h} - auto-scaling")
                    surf = pygame.transform.scale(surf, (TILE_SIZE, TILE_SIZE))
                
                key = p.stem.lower()
                out[key] = surf
                
            except Exception as e:
                print(f"[SpriteManager] ERR loading {p}: {e}")
                # Erstelle Placeholder für fehlgeschlagene Sprites
                key = p.stem.lower()
                out[key] = self._create_placeholder_sprite(key, folder.name)
        
        return out
    
    def _create_placeholder_sprite(self, name: str, category: str = "unknown") -> pygame.Surface:
        """Erstellt einen visuell erkennbaren Placeholder-Sprite."""
        placeholder = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        
        # Verschiedene Farben für verschiedene Asset-Kategorien
        color_map = {
            'tiles': (255, 0, 255),      # Magenta für Tiles
            'objects': (255, 255, 0),    # Gelb für Objects  
            'player': (0, 255, 255),     # Cyan für Player
            'npc': (255, 128, 0),        # Orange für NPCs
            'monster': (128, 255, 128),  # Hellgrün für Monster
        }
        
        base_color = color_map.get(category, (128, 128, 128))
        placeholder.fill(base_color)
        
        # Zeichne einen dunklen Rahmen
        pygame.draw.rect(placeholder, (0, 0, 0), (0, 0, TILE_SIZE, TILE_SIZE), 1)
        
        # Zeichne ein X als Fehler-Indikator
        pygame.draw.line(placeholder, (0, 0, 0), (2, 2), (TILE_SIZE-2, TILE_SIZE-2), 2)
        pygame.draw.line(placeholder, (0, 0, 0), (TILE_SIZE-2, 2), (2, TILE_SIZE-2), 2)
        
        # Zeichne einen Punkt in der Mitte
        center = TILE_SIZE // 2
        pygame.draw.circle(placeholder, (0, 0, 0), (center, center), 2)
        
        return placeholder

    def _load_tiles(self) -> None:
        """Lädt Tiles aus den .tsx Tileset-Dateien."""
        # DEAKTIVIERT - Wir laden Tilesets jetzt über load_tmx_tilesets()
        # Die alte Methode würde die GID-Mappings überschreiben
        print(f"[SpriteManager] Tiles: {len(self._tiles)}")

    def load_tileset_with_gids(self, tsx_path: Path, firstgid: int) -> None:
        """Lädt ein Tileset mit korrektem GID-Mapping für TMX-Support."""
        try:
            import xml.etree.ElementTree as ET
            
            # Parse .tsx Datei
            tree = ET.parse(tsx_path)
            root = tree.getroot()
            
            # Extrahiere Tileset-Informationen
            tile_width = int(root.get('tilewidth', 16))
            tile_height = int(root.get('tileheight', 16))
            tile_count = int(root.get('tilecount', 0))
            columns = int(root.get('columns', 1))
            tileset_name = root.get('name', '').lower()
            
            # Finde das Bild-Element
            image_elem = root.find('image')
            if image_elem is None:
                print(f"[SpriteManager] WARN: No image found in {tsx_path.name}")
                return
            
            # Lade das Tileset-Bild
            image_source = image_elem.get('source', '')
            if not image_source:
                print(f"[SpriteManager] WARN: No image source in {tsx_path.name}")
                return
            
            # Konstruiere den Pfad zum Tileset-Bild
            if image_source.startswith("../../"):
                # Relativer Pfad von data/maps aus
                tileset_image_path = Path(image_source.replace("../../", ""))
            else:
                tileset_image_path = tsx_path.parent / image_source
            
            if not tileset_image_path.exists():
                print(f"[SpriteManager] WARN: Tileset image not found: {tileset_image_path}")
                return
            
            # Lade das Tileset-Bild
            tileset_surface = pygame.image.load(str(tileset_image_path)).convert_alpha()
            
            # Extrahiere einzelne Tiles und mappe sie zu GIDs
            for tile_id in range(tile_count):
                # Berechne Position im Tileset
                col = tile_id % columns
                row = tile_id // columns
                
                # Berechne Pixel-Koordinaten
                x = col * tile_width
                y = row * tile_height
                
                # Extrahiere das einzelne Tile
                tile_surface = pygame.Surface((tile_width, tile_height), pygame.SRCALPHA)
                tile_surface.blit(tileset_surface, (0, 0), (x, y, tile_width, tile_height))
                
                # Skaliere auf TILE_SIZE falls nötig
                if tile_width != TILE_SIZE or tile_height != TILE_SIZE:
                    tile_surface = pygame.transform.scale(tile_surface, (TILE_SIZE, TILE_SIZE))
                
                # Speichere mit GID
                gid = firstgid + tile_id
                self.gid_to_surface[gid] = tile_surface
                
                # Speichere auch mit generiertem Namen für Kompatibilität
                tile_name = f"gid_{gid}"
                self._tiles[tile_name] = tile_surface
                self.sprite_cache[tile_name] = tile_surface
            
            print(f"[SpriteManager] Loaded tileset {tsx_path.name}: {tile_count} tiles (firstgid={firstgid})")
            
        except Exception as e:
            print(f"[SpriteManager] ERR loading tileset with GIDs {tsx_path.name}: {e}")
    
    def _load_tileset_from_tsx(self, tsx_path: Path) -> None:
        """Lädt ein Tileset aus einer .tsx Datei und extrahiert die einzelnen Tiles."""
        try:
            import xml.etree.ElementTree as ET
            
            # Parse .tsx Datei
            tree = ET.parse(tsx_path)
            root = tree.getroot()
            
            # Extrahiere Tileset-Informationen
            tile_width = int(root.get('tilewidth', 16))
            tile_height = int(root.get('tileheight', 16))
            tile_count = int(root.get('tilecount', 0))
            columns = int(root.get('columns', 1))
            tileset_name = root.get('name', '').lower()
            
            # Finde das Bild-Element
            image_elem = root.find('image')
            if image_elem is None:
                print(f"[SpriteManager] WARN: No image found in {tsx_path.name}")
                return
            
            # Lade das Tileset-Bild
            image_source = image_elem.get('source', '')
            if not image_source:
                print(f"[SpriteManager] WARN: No image source in {tsx_path.name}")
                return
            
            # Konstruiere den Pfad zum Tileset-Bild
            tileset_image_path = tsx_path.parent / image_source
            if not tileset_image_path.exists():
                print(f"[SpriteManager] WARN: Tileset image not found: {tileset_image_path}")
                return
            
            # Lade das Tileset-Bild
            tileset_surface = pygame.image.load(str(tileset_image_path)).convert_alpha()
            tileset_width, tileset_height = tileset_surface.get_size()
            
            # Extrahiere einzelne Tiles aus dem Tileset
            rows = (tile_count + columns - 1) // columns  # Berechne Anzahl der Reihen
            
            for tile_id in range(tile_count):
                # Berechne Position im Tileset
                col = tile_id % columns
                row = tile_id // columns
                
                # Berechne Pixel-Koordinaten
                x = col * tile_width
                y = row * tile_height
                
                # Extrahiere das einzelne Tile
                tile_surface = pygame.Surface((tile_width, tile_height), pygame.SRCALPHA)
                tile_surface.blit(tileset_surface, (0, 0), (x, y, tile_width, tile_height))
                
                # Skaliere auf TILE_SIZE falls nötig
                if tile_width != TILE_SIZE or tile_height != TILE_SIZE:
                    tile_surface = pygame.transform.scale(tile_surface, (TILE_SIZE, TILE_SIZE))
                
                # Generiere Tile-Namen basierend auf Tileset-Typ und Position
                tile_name = self._generate_tile_name_from_tileset(tile_id, tileset_name)
                
                # Speichere das Tile
                self._tiles[tile_name] = tile_surface
                self.sprite_cache[tile_name] = tile_surface
                
                print(f"[SpriteManager] Loaded tile: {tile_name} from {tsx_path.name}")
                
        except Exception as e:
            print(f"[SpriteManager] ERR loading tileset {tsx_path.name}: {e}")

    def _generate_tile_name_from_tileset(self, tile_id: int, tileset_name: str) -> str:
        """Generiert einen Tile-Namen basierend auf Tileset-Typ und Position."""
        # Map tileset names to tile categories
        if 'tiles1' in tileset_name or 'tiles' in tileset_name:
            # Ground tiles
            ground_tiles = [
                'grass_1', 'grass_2', 'grass_3', 'grass_4', 'grass',  # 0-4
                'dirt_1', 'dirt_2', 'dirt', 'path_1', 'path_2', 'path',  # 5-10
                'gravel_1', 'gravel_2', 'gravel', 'sand_1', 'sand_2', 'sand',  # 11-15
                'water_1', 'water_2', 'water', 'stone_1', 'stone_2', 'stone',  # 16-20
                'tree_small', 'bush', 'bush_1', 'bush_2'  # 21-23
            ]
            return ground_tiles[tile_id] if tile_id < len(ground_tiles) else f"tile_{tile_id}"
            
        elif 'objects1' in tileset_name or 'objects' in tileset_name:
            # Object tiles
            object_tiles = [
                'barrel', 'bed', 'bookshelf', 'boulder', 'chair', 'crate',  # 0-5
                'door', 'fence_h', 'fence_v', 'gravestone', 'lamp_post', 'mailbox',  # 6-11
                'potted_plant', 'sign', 'table', 'tv', 'well', 'window'  # 12-17
            ]
            return object_tiles[tile_id] if tile_id < len(object_tiles) else f"tile_{tile_id}"
            
        elif 'terrain' in tileset_name:
            # Terrain tiles
            terrain_tiles = [
                'cliff_face', 'flower_blue', 'flower_red', 'ledge', 'rock_1', 'rock_2',  # 0-5
                'rock', 'roof_blue', 'roof_red', 'roof_ridge', 'roof', 'stairs_h',  # 6-11
                'stairs_v', 'stairs', 'stone_floor', 'stump', 'tall_grass_1',  # 12-16
                'tall_grass_2', 'tall_grass', 'wall_brick', 'wall_plaster', 'wall',  # 17-21
                'warp_carpet', 'wood_floor'  # 22-23
            ]
            return terrain_tiles[tile_id] if tile_id < len(terrain_tiles) else f"tile_{tile_id}"
            
        elif 'building' in tileset_name or 'interior' in tileset_name:
            # Building tiles
            building_tiles = [
                'carpet', 'wall', 'window', 'door', 'stairs', 'roof',  # 0-5
                'floor', 'ceiling', 'pillar', 'arch', 'gate', 'bridge'  # 6-11
            ]
            return building_tiles[tile_id] if tile_id < len(building_tiles) else f"tile_{tile_id}"
            
        else:
            # Fallback: use generic name
            return f"tile_{tile_id}"
    
    def _create_placeholder_sprite(self, name: str, category: str) -> pygame.Surface:
        """Erstellt einen Platzhalter-Sprite für fehlende Assets."""
        placeholder = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        
        # Fülle mit einer auffälligen Farbe je nach Kategorie
        colors = {
            'player': (255, 0, 0),      # Rot für Player
            'npc': (0, 255, 0),         # Grün für NPCs
            'monster': (0, 0, 255),     # Blau für Monster
            'tile': (255, 255, 0),      # Gelb für Tiles
            'object': (255, 0, 255),    # Magenta für Objects
            'default': (128, 128, 128)  # Grau für alles andere
        }
        
        color = colors.get(category, colors['default'])
        placeholder.fill(color)
        
        # Zeichne einen schwarzen Rahmen
        pygame.draw.rect(placeholder, (0, 0, 0), (0, 0, TILE_SIZE, TILE_SIZE), 2)
        
        # Zeichne den Namen als Text (falls möglich)
        try:
            font = pygame.font.Font(None, 12)
            text_surf = font.render(name[:8], True, (0, 0, 0))
            text_rect = text_surf.get_rect(center=(TILE_SIZE//2, TILE_SIZE//2))
            placeholder.blit(text_surf, text_rect)
        except:
            pass  # Ignore font errors
        
        return placeholder
    
    def _load_dir_16px(self, directory: Path) -> Dict[str, pygame.Surface]:
        """Lädt alle 16x16 Sprites aus einem Verzeichnis."""
        sprites = {}
        
        if not directory.exists():
            return sprites
        
        for p in directory.glob("*.png"):
            try:
                surf = pygame.image.load(str(p)).convert_alpha()
                
                # Auto-skaliere falls nötig
                if surf.get_size() != (TILE_SIZE, TILE_SIZE):
                    surf = pygame.transform.scale(surf, (TILE_SIZE, TILE_SIZE))
                
                sprites[p.stem] = surf
                
            except Exception as e:
                print(f"[SpriteManager] ERR loading {p.name}: {e}")
                # Erstelle Platzhalter für fehlgeschlagene Sprites
                sprites[p.stem] = self._create_placeholder_sprite(p.stem, 'default')
        
        return sprites

    def _load_objects(self) -> None:
        self._objects = self._load_dir_16px(self.objects_dir)
        print(f"[SpriteManager] Objects: {len(self._objects)}")

    def _load_player(self) -> None:
        # player_{up,down,left,right}.png
        mapping = {
            "up":    self.player_dir / "player_up.png",
            "down":  self.player_dir / "player_down.png",
            "left":  self.player_dir / "player_left.png",
            "right": self.player_dir / "player_right.png",
        }
        for direction, path in mapping.items():
            if path.exists():
                try:
                    surf = pygame.image.load(str(path)).convert_alpha()
                    # Auto-skaliere falls nötig
                    if surf.get_size() != (TILE_SIZE, TILE_SIZE):
                        print(f"[SpriteManager] WARN Player {direction}: auto-scaling to {TILE_SIZE}x{TILE_SIZE}")
                        surf = pygame.transform.scale(surf, (TILE_SIZE, TILE_SIZE))
                    self._player_dir_map[direction] = surf
                except Exception as e:
                    print(f"[SpriteManager] ERR loading {path.name}: {e}")
                    # Erstelle Placeholder für fehlgeschlagenen Player-Sprite  
                    self._player_dir_map[direction] = self._create_placeholder_sprite(f"player_{direction}", "player")
            else:
                print(f"[SpriteManager] WARN missing {path.name}")
                # Erstelle Placeholder für fehlende Player-Sprites
                self._player_dir_map[direction] = self._create_placeholder_sprite(f"player_{direction}", "player")
        
        print(f"[SpriteManager] Player dirs: {list(self._player_dir_map.keys())}")

    def _load_npcs(self) -> None:
        # npcX_{up,down,left,right}.png  (X=A,B,C...)
        if not self.npc_dir.exists():
            return
        for p in self.npc_dir.glob("*.png"):
            name = p.stem  # e.g., npcA_up
            if not name.startswith("npc"):
                continue
            parts = name.split("_")
            if len(parts) != 2:
                continue
            npc_id, direction = parts[0], parts[1]  # npcA, up
            try:
                surf = pygame.image.load(str(p)).convert_alpha()
                self._npc_dir_map[(npc_id, direction)] = surf
            except Exception as e:
                print(f"[SpriteManager] ERR loading {p.name}: {e}")
        print(f"[SpriteManager] NPC variants: {len(self._npc_dir_map)}")

    def _load_monsters(self) -> None:
        if not self.monster_dir.exists():
            return
        for p in self.monster_dir.glob("*.png"):
            key = p.stem  # "1".."151"
            try:
                surf = pygame.image.load(str(p)).convert_alpha()
                self._monster[key] = surf
            except Exception as e:
                print(f"[SpriteManager] ERR loading {p.name}: {e}")
        print(f"[SpriteManager] Monsters: {len(self._monster)}")
    
    def get_sprite_cache_size(self) -> int:
        """Gibt die Anzahl der Sprites im Cache zurück (für Kompatibilität)."""
        self._ensure_loaded()
        return len(self.sprite_cache)

    # ---------- Mapping / Info ----------
    def _load_tile_mappings(self) -> None:
        """Lädt Tile-Mapping und priorisiert die Datei, deren Tilegröße zu TILE_SIZE passt."""
        data_dir = self.project_root / "data"
        candidates = [data_dir / "tile_mapping_new.json", data_dir / "tile_mapping.json"]
        loaded: list[tuple[str, Dict[str, Any], int]] = []  # (name, mapping, tile_size)

        for p in candidates:
            if not p.exists():
                continue
            try:
                with p.open("r", encoding="utf-8") as f:
                    j = json.load(f)
                    mapping = j.get("tile_mappings", {}) or {}
                    info = j.get("tileset_info", {}) or {}
                    tile_size = int(info.get("tile_size")) if "tile_size" in info else TILE_SIZE
                    if mapping:
                        loaded.append((p.name, mapping, tile_size))
            except Exception as e:
                print(f"[SpriteManager] WARN failed to load mapping {p.name}: {e}")

        # Bevorzuge Mapping mit passender Tilegröße
        chosen: tuple[str, Dict[str, Any], int] | None = None
        for name, mapping, ts in loaded:
            if ts == TILE_SIZE:
                chosen = (name, mapping, ts)
                break
        # Fallback: das mit den meisten Einträgen
        if chosen is None and loaded:
            chosen = max(loaded, key=lambda t: len(t[1]))

        if chosen:
            name, mapping, ts = chosen
            print(f"[SpriteManager] Tile mapping loaded from {name} (tile_size={ts}, {len(mapping)} entries)")
            self._tile_mappings = mapping
        else:
            self._tile_mappings = {}

    def get_tile_info(self, tile_id: int | str) -> Optional[Dict[str, Any]]:
        """Gibt Mapping-Infos für eine Tile-ID zurück."""
        self._ensure_loaded()
        key = str(tile_id)
        return self._tile_mappings.get(key)
    
    def get_tile_sprite(self, tile_id: int | str) -> Optional[pygame.Surface]:
        """Get a tile sprite by ID or name."""
        self._ensure_loaded()
        
        # Try to get from tile mappings first
        tile_info = self.get_tile_info(tile_id)
        if tile_info and 'sprite_name' in tile_id:
            sprite_name = tile_info['sprite_name']
            return self.sprite_cache.get(f"tile_{sprite_name}")
        
        # Try direct sprite cache lookup
        if isinstance(tile_id, str):
            return self.sprite_cache.get(f"tile_{tile_id}")
        
        # Try numeric ID lookup
        return self.sprite_cache.get(f"tile_{tile_id}")
    
    def get_npc_sprite(self, npc_id: str) -> Optional[pygame.Surface]:
        """Get an NPC sprite by ID."""
        self._ensure_loaded()
        
        # Try to get from sprite cache first
        if npc_id in self.sprite_cache:
            return self.sprite_cache[npc_id]
        
        # Try to get from NPC direction map
        for (npc_key, direction), sprite in self._npc_dir_map.items():
            if npc_key == npc_id:
                return sprite
        
        return None
    
    def get_monster_sprite(self, monster_id: str | int) -> Optional[pygame.Surface]:
        """Get a monster sprite by ID."""
        self._ensure_loaded()
        
        # Try to get from sprite cache first
        monster_key = f"monster_{monster_id}"
        if monster_key in self.sprite_cache:
            return self.sprite_cache[monster_key]
        
        # Try to get from monster map
        if str(monster_id) in self._monster:
            return self._monster[str(monster_id)]
        
        return None
    
    def get_player_sprite(self, direction: str) -> Optional[pygame.Surface]:
        """Get a player sprite by direction."""
        self._ensure_loaded()
        
        # Try to get from sprite cache first
        player_key = f"player_{direction}"
        if player_key in self.sprite_cache:
            return self.sprite_cache[player_key]
        
        # Try to get from player direction map
        if direction in self._player_dir_map:
            return self._player_dir_map[direction]
        
        return None
    
    def get_object_sprite(self, object_id: str) -> Optional[pygame.Surface]:
        """Get an object sprite by ID."""
        self._ensure_loaded()
        
        # Try to get from sprite cache first
        object_key = f"object_{object_id}"
        if object_key in self.sprite_cache:
            return self.sprite_cache[object_key]
        
        # Try to get from objects map
        if object_id in self._objects:
            return self._objects[object_id]
        
        return None
    
    def get_sprite(self, sprite_name: str) -> Optional[pygame.Surface]:
        """Get a sprite by name (generic method)."""
        self._ensure_loaded()
        return self.sprite_cache.get(sprite_name)

    def get_cache_info(self) -> Dict[str, Any]:
        """Gibt Statistiken zum Cache und den Mappings zurück."""
        self._ensure_loaded()
        return {
            "total_sprites": len(self.sprite_cache),
            "tile_mappings": len(self._tile_mappings),
            "monster_sprites": len(self._monster),
            "npc_sprites": len(self._npc_dir_map),
            "tile_ids": list(self._tile_mappings.keys())[:20],
            "sprite_names": list(self.sprite_cache.keys())[:20],
        }

    # ---------- Kompatibilitätsschicht ----------

    def load_tileset(self, filename: str) -> None:
        """Legacy-Methode ohne Funktion – Sprites werden bereits automatisch geladen."""
        self._ensure_loaded()
        # Exponiere Tiles unter erwartetem Namen
        self.tile_images = self._tiles

    def load_tileset_scaled(self, filename: str, src_size: int, target_size: int) -> None:
        """Legacy-Methode für hochskalierte Tiles. Führt aktuell keine Skalierung durch,
        stellt aber sicher, dass tile_images verfügbar ist."""
        self._ensure_loaded()
        self.tile_images = self._tiles
    
    def load_tmx_tilesets(self, tmx_path: Path) -> None:
        """Lädt alle Tilesets aus einer TMX-Datei"""
        try:
            import xml.etree.ElementTree as ET
            
            tree = ET.parse(tmx_path)
            root = tree.getroot()
            
            for tileset_elem in root.findall('tileset'):
                firstgid = int(tileset_elem.get('firstgid', 1))
                source = tileset_elem.get('source', '')
                
                if source:
                    tsx_path = tmx_path.parent / source
                    if tsx_path.exists():
                        self._load_tmx_tileset(tsx_path, firstgid)
                        
        except Exception as e:
            print(f"[SpriteManager] Error loading TMX tilesets: {e}")
    
    def _load_tmx_tileset(self, tsx_path: Path, firstgid: int) -> None:
        """Lädt ein Tileset und extrahiert Tiles"""
        try:
            import xml.etree.ElementTree as ET
            
            tree = ET.parse(tsx_path)
            root = tree.getroot()
            
            tilewidth = int(root.get('tilewidth', 16))
            tileheight = int(root.get('tileheight', 16))
            tilecount = int(root.get('tilecount', 0))
            columns = int(root.get('columns', 1))
            
            # Finde Bild-Pfad
            image_elem = root.find('image')
            if image_elem is None:
                return
            
            image_source = image_elem.get('source', '')
            if image_source.startswith('../../'):
                # Relativer Pfad von data/maps aus
                image_path = self.project_root / image_source.replace('../../', '')
            else:
                image_path = tsx_path.parent / image_source
            
            if not image_path.exists():
                print(f"[SpriteManager] Tileset image not found: {image_path}")
                return
            
            # Lade Tileset-Bild
            tileset_surface = pygame.image.load(str(image_path)).convert_alpha()
            
            # Extrahiere einzelne Tiles
            for tile_id in range(tilecount):
                col = tile_id % columns
                row = tile_id // columns
                
                x = col * tilewidth
                y = row * tileheight
                
                # Extrahiere Tile
                tile_surf = pygame.Surface((tilewidth, tileheight), pygame.SRCALPHA)
                tile_surf.blit(tileset_surface, (0, 0), (x, y, tilewidth, tileheight))
                
                # Skaliere auf TILE_SIZE falls nötig
                if tilewidth != TILE_SIZE or tileheight != TILE_SIZE:
                    tile_surf = pygame.transform.scale(tile_surf, (TILE_SIZE, TILE_SIZE))
                
                # Speichere mit GID
                gid = firstgid + tile_id
                self.gid_to_surface[gid] = tile_surf
            
            print(f"[SpriteManager] Loaded TMX tileset: {tsx_path.name} - {tilecount} tiles (firstgid={firstgid})")
            
        except Exception as e:
            print(f"[SpriteManager] Error loading TMX tileset {tsx_path}: {e}")
    
    def get_tile_by_gid(self, gid: int) -> Optional[pygame.Surface]:
        """Get a tile surface by GID (Global ID from TMX)."""
        return self.gid_to_surface.get(gid)