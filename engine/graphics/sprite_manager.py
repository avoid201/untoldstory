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
        self.tiles_dir = self.project_root / "data" / "maps" / "tiles"  # Neuer Pfad für individuelle Tiles
        self.objects_dir = self.project_root / "data" / "maps" / "objects"  # Korrigierter Pfad für Object-Tiles
        self.player_dir = self.project_root / "data" / "maps" / "player"  # Neuer Pfad für Player-Sprites
        self.npc_dir = self.project_root / "data" / "maps" / "npc"
        self.monster_dir = self.project_root / "assets" / "gfx" / "monster"
        
        # Sprite-Caches
        self._tiles: Dict[str, pygame.Surface] = {}
        self._objects: Dict[str, pygame.Surface] = {}
        self._player_dir_map: Dict[str, pygame.Surface] = {}
        self._npc_dir_map: Dict[Tuple[str, str], pygame.Surface] = {}
        self._monster: Dict[str, pygame.Surface] = {}
        
        # Tile-Mappings für JSON-Maps
        self._tile_mappings: Dict[str, Any] = {}
        
        # Sprite-Cache für alle Sprites
        self.sprite_cache: Dict[str, pygame.Surface] = {}
        
        # Lazy Loading
        self._loaded = False
        
        # GID-zu-Surface Mapping für TMX-Support (Legacy)
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
            
        # Player hinzufügen
        for direction, surf in self._player_dir_map.items():
            self.sprite_cache[f"player_{direction}"] = surf
            
        # NPCs hinzufügen
        for (npc_id, direction), surf in self._npc_dir_map.items():
            self.sprite_cache[f"npc_{npc_id}_{direction}"] = surf
            
        # Monster hinzufügen
        for monster_id, surf in self._monster.items():
            self.sprite_cache[f"monster_{monster_id}"] = surf

    @property
    def monster_sprites(self) -> Dict[str, pygame.Surface]:
        """Gibt den Monster-Sprite-Cache zurück."""
        self._ensure_loaded()
        return self._monster

    def get_tile_sprite(self, tile_id: Any) -> Optional[pygame.Surface]:
        """
        Hauptmethode zum Abrufen von Tile-Sprites.
        Unterstützt sowohl GID-basierte als auch String-basierte Tile-IDs.
        """
        # Zuerst im Cache suchen
        if isinstance(tile_id, str):
            # String-basierter Zugriff
            sprite = self._tiles.get(tile_id.lower())
            if sprite is not None:
                return sprite
            sprite = self.sprite_cache.get(f"tile_{tile_id}")
            if sprite is not None:
                return sprite
        elif isinstance(tile_id, int) and tile_id > 0:
            # GID-basierter Zugriff (Legacy TMX-Support)
            sprite = self.gid_to_surface.get(tile_id)
            if sprite is not None:
                return sprite
            
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
        """Lädt individuelle Tiles aus dem data/maps/tiles Ordner."""
        try:
            # Lade individuelle Tiles
            self._tiles.update(self._load_dir_16px(self.tiles_dir))
            print(f"[SpriteManager] Individuelle Tiles geladen: {len(self._tiles)}")
            
            # Lade auch Legacy-Tilesets falls vorhanden
            legacy_tilesets_dir = self.project_root / "assets" / "gfx" / "tiles" / "tilesets"
            if legacy_tilesets_dir.exists():
                print(f"[SpriteManager] WARN: Legacy tilesets gefunden in {legacy_tilesets_dir}")
                # Hier könnten wir Legacy-Tilesets laden falls nötig
                
        except Exception as e:
            print(f"[SpriteManager] ERR beim Laden der Tiles: {e}")
            # Erstelle Fallback-Tiles
            self._create_fallback_tiles()
    
    def _create_fallback_tiles(self) -> None:
        """Erstellt Fallback-Tiles falls das Laden fehlschlägt."""
        print("[SpriteManager] Erstelle Fallback-Tiles...")
        
        # Erstelle ein einfaches Gras-Tile
        grass = pygame.Surface((TILE_SIZE, TILE_SIZE))
        grass.fill((34, 139, 34))  # Forest Green
        self._tiles["grass"] = grass
        self._tiles["grass_1"] = grass
        
        # Erstelle ein Weg-Tile
        path = pygame.Surface((TILE_SIZE, TILE_SIZE))
        path.fill((139, 69, 19))  # Saddle Brown
        self._tiles["path"] = path
        self._tiles["path_1"] = path
        
        # Erstelle ein Wasser-Tile
        water = pygame.Surface((TILE_SIZE, TILE_SIZE))
        water.fill((0, 191, 255))  # Deep Sky Blue
        self._tiles["water"] = water
        self._tiles["water_1"] = water

    def _load_tile_mappings(self) -> None:
        """Lädt die Tile-Mappings aus der JSON-Datei."""
        try:
            mapping_path = self.project_root / "data" / "tile_mapping.json"
            if mapping_path.exists():
                with open(mapping_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._tile_mappings = data.get("tile_mappings", {})
                print(f"[SpriteManager] Tile-Mappings geladen: {len(self._tile_mappings)}")
            else:
                print("[SpriteManager] WARN: tile_mapping.json nicht gefunden")
        except Exception as e:
            print(f"[SpriteManager] ERR beim Laden der Tile-Mappings: {e}")

    def get_tile(self, tile_name: str) -> Optional[pygame.Surface]:
        """Holt einen Tile-Sprite nach Namen."""
        return self._tiles.get(tile_name.lower())

    def get_tile_by_gid(self, gid: int) -> Optional[pygame.Surface]:
        """Holt einen Tile-Sprite nach GID (Legacy TMX-Support)."""
        return self.gid_to_surface.get(gid)

    def get_tile_by_mapping(self, tile_id: str) -> Optional[pygame.Surface]:
        """Holt einen Tile-Sprite über das Tile-Mapping."""
        mapping = self._tile_mappings.get(tile_id)
        if mapping:
            sprite_file = mapping.get("sprite_file", "")
            if sprite_file:
                # Versuche den Sprite direkt zu laden
                tile_name = sprite_file.replace(".png", "").lower()
                return self._tiles.get(tile_name)
        return None

    def get_tile_info(self, tile_id: int | str) -> Optional[Dict[str, Any]]:
        """Gibt Mapping-Infos für eine Tile-ID zurück."""
        key = str(int(tile_id)) if isinstance(tile_id, int) else str(tile_id)
        return self._tile_mappings.get(key)
    
    def get_npc_sprite(self, npc_id: str, direction: str = "down") -> Optional[pygame.Surface]:
        """Get an NPC sprite by ID and direction."""
        self._ensure_loaded()
        
        # Try to get from sprite cache first
        npc_key = f"npc_{npc_id}_{direction}"
        if npc_key in self.sprite_cache:
            return self.sprite_cache[npc_key]
        
        # Try to get from NPC direction map
        npc_tuple = (npc_id, direction)
        if npc_tuple in self._npc_dir_map:
            return self._npc_dir_map[npc_tuple]
        
        # Fallback: Try with "down" direction if other direction not found
        if direction != "down":
            fallback_tuple = (npc_id, "down")
            if fallback_tuple in self._npc_dir_map:
                return self._npc_dir_map[fallback_tuple]
        
        return None
    
    def get_monster_sprite(self, monster_id: str) -> Optional[pygame.Surface]:
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
    
    def get_player(self, direction: str) -> Optional[pygame.Surface]:
        """Alias für get_player_sprite für Kompatibilität."""
        return self.get_player_sprite(direction)
    
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

    def _load_objects(self) -> None:
        """Lädt Object-Sprites aus dem objects Ordner."""
        self._objects = self._load_dir_16px(self.objects_dir)
        print(f"[SpriteManager] Objects: {len(self._objects)}")

    def _load_player(self) -> None:
        """Lädt Player-Sprites für alle Richtungen."""
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
        """Lädt NPC-Sprites für alle Varianten."""
        # {npc_name}_{direction}.png  (z.B. villager_f_down.png)
        if not self.npc_dir.exists():
            return
        for p in self.npc_dir.glob("*.png"):
            name = p.stem  # e.g., villager_f_down
            parts = name.split("_")
            if len(parts) < 2:
                continue
            # Letzter Teil ist die Richtung, Rest ist der NPC-Name
            direction = parts[-1]
            npc_id = "_".join(parts[:-1])
            
            if direction not in ["up", "down", "left", "right"]:
                continue
                
            try:
                surf = pygame.image.load(str(p)).convert_alpha()
                self._npc_dir_map[(npc_id, direction)] = surf
            except Exception as e:
                print(f"[SpriteManager] ERR loading {p.name}: {e}")
        print(f"[SpriteManager] NPC variants: {len(self._npc_dir_map)}")

    def _load_monsters(self) -> None:
        """Lädt Monster-Sprites nach Dex-ID."""
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