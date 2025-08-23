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
    
    def get_tile_sprite(self, tile_id) -> Optional[pygame.Surface]:
        """Holt ein Tile-Sprite nach Tile-ID oder -Name.

        Unterstützt:
        - int: wird via data/tile_mapping_new.json (oder tile_mapping.json) auf Sprite-Dateien gemappt
        - str: Name ohne .png (direkter Zugriff)
        """
        self._ensure_loaded()

        # Direkter Zugriff per Name
        if isinstance(tile_id, str):
            sprite = self.get_tile(tile_id)
            if sprite is not None:
                return sprite
            sprite = self.sprite_cache.get(f"tile_{tile_id}")
            if sprite is not None:
                return sprite
        else:
            # Numerische ID über Mapping auflösen
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
        # Lade Tiles aus den .tsx Tileset-Dateien
        tiles_dir = self.project_root / "assets" / "gfx" / "tiles"
        if tiles_dir.exists():
            # Lade alle .tsx Dateien
            for tsx_file in tiles_dir.glob("*.tsx"):
                try:
                    self._load_tileset_from_tsx(tsx_file)
                except Exception as e:
                    print(f"[SpriteManager] ERR loading tileset {tsx_file.name}: {e}")
        
        print(f"[SpriteManager] Tiles: {len(self._tiles)}")

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