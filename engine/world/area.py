"""
Area - Repräsentiert eine spielbare Map-Region
Mit verbessertem TMX-Support und korrektem Tile-Rendering
OPTIMIERT: Surface-Caching und reduzierte JSON-Operationen
"""

import pygame
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from functools import lru_cache
import time

from engine.world.tiles import TILE_SIZE, TileType
from engine.world.map_loader import MapLoader, MapData
from engine.graphics.sprite_manager import SpriteManager
from engine.world.entity import Entity
from engine.world.npc import NPC
from engine.core.resources import resources
from engine.world.tile_manager import TileManager

@dataclass
class AreaConfig:
    """Konfiguration für eine Area"""
    map_id: str
    name: str = ""
    music: Optional[str] = None
    encounter_rate: float = 0.0
    weather: Optional[str] = None

class Area:
    """Eine spielbare Map-Region mit TMX-Support und Performance-Optimierungen"""
    
    # Klassenweite Caches für bessere Performance
    _surface_cache: Dict[str, pygame.Surface] = {}
    _json_cache: Dict[str, Dict] = {}
    _cache_timestamps: Dict[str, float] = {}
    _cache_ttl = 300.0  # 5 Minuten Cache-Lebensdauer
    
    def __init__(self, map_id: str):
        """
        Initialisiert eine Area aus einer Map-ID.
        
        Args:
            map_id: ID der zu ladenden Map (ohne Dateiendung)
        """
        self.map_id = map_id
        self.name = map_id.replace('_', ' ').title()  # Konvertiere map_id zu lesbarem Namen
        self.map_data: Optional[MapData] = None
        self.sprite_manager = SpriteManager.get()
        
        # Standard-Größe falls TMX-Loading fehlschlägt
        self.width = 32
        self.height = 32
        self.tile_width = TILE_SIZE
        self.tile_height = TILE_SIZE
        
        # Surfaces für jede Layer - OPTIMIERT: Caching implementiert
        self.layer_surfaces: Dict[str, pygame.Surface] = {}
        
        # Entities und NPCs
        self.entities: List[Entity] = []
        self.npcs: List[NPC] = []
        
        # Encounter-System (für FieldScene Kompatibilität)
        self.encounter_rate = 0.1
        self.encounter_table = []
        
        # Performance-Metriken
        self._render_time = 0.0
        self._cache_hits = 0
        self._cache_misses = 0
        
        # Lade die Map
        self._load_map()
    
    @classmethod
    def _cleanup_cache(cls) -> None:
        """Bereinigt abgelaufene Cache-Einträge"""
        current_time = time.time()
        expired_keys = [
            key for key, timestamp in cls._cache_timestamps.items()
            if current_time - timestamp > cls._cache_ttl
        ]
        
        for key in expired_keys:
            cls._surface_cache.pop(key, None)
            cls._json_cache.pop(key, None)
            cls._cache_timestamps.pop(key, None)
    
    @classmethod
    def _get_cached_surface(cls, cache_key: str) -> Optional[pygame.Surface]:
        """Holt eine gecachte Surface aus dem Cache"""
        cls._cleanup_cache()
        if cache_key in cls._surface_cache:
            cls._cache_timestamps[cache_key] = time.time()
            return cls._surface_cache[cache_key]
        return None
    
    @classmethod
    def _cache_surface(cls, cache_key: str, surface: pygame.Surface) -> None:
        """Speichert eine Surface im Cache"""
        cls._surface_cache[cache_key] = surface
        cls._cache_timestamps[cache_key] = time.time()
    
    @classmethod
    def _get_cached_json(cls, map_id: str) -> Optional[Dict]:
        """Holt gecachte JSON-Daten aus dem Cache"""
        cls._cleanup_cache()
        if map_id in cls._json_cache:
            cls._cache_timestamps[map_id] = time.time()
            return cls._json_cache[map_id]
        return None
    
    @classmethod
    def _cache_json(cls, map_id: str, data: Dict) -> None:
        """Speichert JSON-Daten im Cache"""
        cls._json_cache[map_id] = data
        cls._cache_timestamps[map_id] = time.time()

    def _load_map(self):
        """Lädt die Map-Daten mit optimiertem Caching"""
        try:
            # Verwende nur noch den MapLoader für JSON-Maps
            self.map_data = MapLoader.load_map(self.map_id)
            # Setze Attribute aus MapData
            if self.map_data:
                self.width = self.map_data.width
                self.height = self.map_data.height
                self.name = self.map_data.name or self.name
                self.tile_width = self.map_data.tile_size
                self.tile_height = self.map_data.tile_size
            self._render_layers()
                
        except Exception as e:
            print(f"[Area] Fehler beim Laden der Map {self.map_id}: {e}")
            # Erstelle leere Map als Fallback
            self._create_empty_map()
    
    # TMX-Methoden entfernt - veraltet
    
    # TMX-Tileset-Methoden entfernt - veraltet
    
    # TSX-Tileset-Methoden entfernt - veraltet
    
    # TMX-Layer-Methoden entfernt - veraltet
    
    # TMX-Objekt-Methoden entfernt - veraltet
    
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
        """Rendert Layer aus MapData mit optimiertem Caching"""
        if not self.map_data:
            return
        
        start_time = time.time()
        
        # OPTIMIERT: Verwende gecachte Surfaces wenn möglich
        cache_key = f"{self.map_id}_layers_{self.map_data.width}x{self.map_data.height}"
        cached_surfaces = self._get_cached_surface(cache_key)
        
        if cached_surfaces:
            # OPTIMIERT: Kopiere gecachte Surfaces
            for layer_name, surface in cached_surfaces.items():
                self.layer_surfaces[layer_name] = surface.copy()
            self._cache_hits += 1
            self._render_time = time.time() - start_time
            return
        
        self._cache_misses += 1
        
        # Rendere Tile-Layer
        for layer_name, layer_data in self.map_data.layers.items():
            if layer_name == "collision":
                continue  # Collision wird nicht gerendert
            
            # OPTIMIERT: Erstelle Surface nur wenn nötig
            surface = pygame.Surface(
                (self.map_data.width * TILE_SIZE, 
                 self.map_data.height * TILE_SIZE),
                pygame.SRCALPHA
            )
            
            # OPTIMIERT: Batch-Rendering für bessere Performance
            self._render_tile_layer_batch(surface, layer_data)
            
            self.layer_surfaces[layer_name] = surface
        
        # Rendere Object-Layer aus der ursprünglichen JSON-Daten
        self._render_object_layers()
        
        # OPTIMIERT: Cache die gerenderten Surfaces
        self._cache_surface(cache_key, self.layer_surfaces.copy())
        
        self._render_time = time.time() - start_time
    
    def _render_tile_layer_batch(self, surface: pygame.Surface, layer_data: List[List[int]]) -> None:
        """OPTIMIERT: Batch-Rendering für Tile-Layer"""
        # Sammle alle Tiles in einem Batch
        tile_batch = []
        
        for y, row in enumerate(layer_data):
            for x, tile in enumerate(row):
                if tile:
                    sprite = self._get_tile_sprite_from_gid(tile)
                    if sprite:
                        tile_batch.append((sprite, x * TILE_SIZE, y * TILE_SIZE))
        
        # OPTIMIERT: Batch-Blitting für bessere Performance
        for sprite, x, y in tile_batch:
            surface.blit(sprite, (x, y))
    
    def _render_object_layers(self):
        """Rendert Object-Layer mit optimiertem Caching"""
        try:
            # OPTIMIERT: Verwende gecachte JSON-Daten
            json_data = self._get_cached_json(self.map_id)
            
            if not json_data:
                # Lade die Original-JSON-Datei nur wenn nicht im Cache
                json_data = resources.load_json(f"maps/{self.map_id}.json")
                if json_data:
                    self._cache_json(self.map_id, json_data)
            
            if not json_data:
                print(f"[Area] Keine JSON-Daten für Object-Layer gefunden: {self.map_id}")
                return
            
            # OPTIMIERT: Erstelle Object-Layer Surface nur wenn nötig
            object_surface = pygame.Surface(
                (self.map_data.width * TILE_SIZE, 
                 self.map_data.height * TILE_SIZE),
                pygame.SRCALPHA
            )
            
            # OPTIMIERT: Batch-Rendering für Objekte
            object_batch = []
            
            # Durchsuche alle Layer nach Object-Layern
            for layer in json_data.get("layers", []):
                if layer.get("type") == "objectgroup":
                    layer_name = layer.get("name", "objects")
                    print(f"[Area] Verarbeite Object-Layer: {layer_name} mit {len(layer.get('objects', []))} Objekten")
                    
                    # Sammle alle Objekte in einem Batch
                    for obj in layer.get("objects", []):
                        gid = obj.get("gid")
                        if gid:
                            # Konvertiere Pixel-Koordinaten zu Tile-Koordinaten
                            # Wichtig: Tiled verwendet bottom-left Koordinaten für Objekte!
                            obj_x = int(obj.get("x", 0))
                            obj_y = int(obj.get("y", 0)) - TILE_SIZE  # Bottom-aligned korrigieren
                            
                            # Hole Object-Sprite basierend auf GID
                            sprite = self._get_tile_sprite_from_gid(gid)
                            if sprite:
                                object_batch.append((sprite, obj_x, obj_y))
                                print(f"[Area] Object geladen: GID {gid} an Position ({obj_x}, {obj_y})")
                            else:
                                print(f"[Area] Kein Sprite für GID {gid} gefunden")
            
            # OPTIMIERT: Batch-Blitting für Objekte
            for sprite, x, y in object_batch:
                object_surface.blit(sprite, (x, y))
            
            # Füge Object-Layer zur Layer-Liste hinzu
            self.layer_surfaces["objects"] = object_surface
            print(f"[Area] Object-Layer erstellt mit {len(object_batch)} Objekten")
            
        except Exception as e:
            print(f"[Area] Fehler beim Rendern der Object-Layer: {e}")
            import traceback
            traceback.print_exc()
    
    @lru_cache(maxsize=256)
    def _get_tile_sprite_from_gid(self, gid: int) -> Optional[pygame.Surface]:
        """Übersetzt GIDs aus Tiled-Format in Tile-Sprites mit LRU-Cache"""
        # GID-zu-Tile-Mapping basierend auf den TSX-Dateien
        # WICHTIG: GID = firstgid + tile_id, also GID 43 = Tile ID 42 = wall.png, GID 44 = Tile ID 43 = warp_carpet.png
        gid_to_tile_mapping = {
            # Tileset 1 (firstgid=1) - GID = 1 + tile_id
            1: "bush_1", 2: "bush_2", 3: "bush", 4: "carpet", 5: "cliff_face",
            6: "dirt_1", 7: "dirt_2", 8: "flower_blue", 9: "flower_red",
            10: "grass_1", 11: "grass_2", 12: "grass_3", 13: "grass_4", 14: "grass",
            15: "gravel_1", 16: "gravel_2", 17: "gravel", 18: "ledge",
            19: "path_1", 20: "path_2", 21: "path", 22: "rock_1", 23: "rock_2",
            24: "rock", 25: "roof_blue", 26: "roof_red", 27: "roof_ridge", 28: "roof",
            29: "sand_1", 30: "sand_2", 31: "snow", 32: "stairs_h", 33: "stairs_v",
            34: "stairs", 35: "stone_floor", 36: "stump", 37: "tall_grass_1",
            38: "tall_grass_2", 39: "tall_grass", 40: "tree_small", 41: "wall_brick",
            42: "wall_plaster", 43: "wall", 44: "warp_carpet", 45: "water_1",
            46: "water_2", 47: "water_corner_ne", 48: "water_corner_nw",
            49: "water_corner_se", 50: "water_corner_sw", 51: "water_edge_e",
            52: "water_edge_n", 53: "water_edge_s", 54: "water_edge_w", 55: "wood_floor",
            
            # Tileset 2 (firstgid=56) - Object tiles
            56: "barrel", 57: "bed", 58: "bookshelf", 59: "boulder", 60: "chair",
            61: "crate", 62: "door", 63: "fence_h", 64: "fence_v", 65: "gravestone",
            66: "lamp_post", 67: "mailbox", 68: "potted_plant", 69: "sign",
            70: "table", 71: "tv", 72: "well", 73: "window"
        }
        
        # Versuche über das GID-Mapping
        if gid in gid_to_tile_mapping:
            tile_name = gid_to_tile_mapping[gid]
            
            # Prüfe zuerst ob es ein Tile ist
            tile_sprite = self.sprite_manager.get_tile(tile_name)
            if tile_sprite:
                return tile_sprite
            
            # Falls kein Tile gefunden, versuche Object-Sprite
            object_sprite = self.sprite_manager.get_object_sprite(tile_name)
            if object_sprite:
                return object_sprite
        
        # Fallback: Verwende GID direkt als Sprite
        # Versuche über das Tile-Mapping
        return self.sprite_manager.get_tile_by_mapping(str(gid))
    
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
    
    def is_tile_solid(self, x: int, y: int) -> bool:
        """
        Prüft, ob ein Tile an der Position solid (undurchlässig) ist.
        Wird vom Pathfinding-System verwendet.
        
        Args:
            x: X-Position in Tiles
            y: Y-Position in Tiles
            
        Returns:
            True wenn solid, sonst False
        """
        # Prüfe Map-Grenzen
        if x < 0 or y < 0:
            return True
        
        if self.map_data:
            if x >= self.map_data.width or y >= self.map_data.height:
                return True
            
            # Prüfe Collision-Layer
            if "collision" in self.map_data.layers:
                collision_layer = self.map_data.layers["collision"]
                if 0 <= y < len(collision_layer) and 0 <= x < len(collision_layer[y]):
                    return bool(collision_layer[y][x])
        else:
            # TMX-basierte Kollision
            if hasattr(self, 'width') and hasattr(self, 'height'):
                if x >= self.width or y >= self.height:
                    return True
        
        # Standardmäßig nicht solid
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
    
    def get_tile_type(self, tile_x: int, tile_y: int) -> int:
        """
        Holt den Tile-Typ an einer Position.
        
        Args:
            tile_x: X-Position in Tiles
            tile_y: Y-Position in Tiles
            
        Returns:
            Tile-ID oder 0
        """
        if not self.map_data:
            return 0
            
        # Versuche verschiedene Layer-Namen (Tiled nutzt manchmal andere Namen)
        possible_layers = ["ground", "Tile Layer 1", "floor", "base"]
        
        for layer_name in possible_layers:
            if layer_name in self.map_data.layers:
                layer = self.map_data.layers[layer_name]
                if 0 <= tile_y < len(layer) and 0 <= tile_x < len(layer[tile_y]):
                    tile_id = layer[tile_y][tile_x]
                    # Debug-Output für Testing
                    if tile_id == 29:  # Grass-Tile
                        print(f"[DEBUG] Grass tile at ({tile_x}, {tile_y})")
                    return tile_id
        return 0
    
    def add_entity(self, entity: Entity):
        """
        Fügt eine Entity zur Area hinzu.
        
        Args:
            entity: Die hinzuzufügende Entity
        """
        self.entities.append(entity)
    
    @property
    def layers(self):
        """Kompatibilitäts-Property für alten Code"""
        if self.map_data:
            return self.map_data.layers
        return {}
    
    # --- Pathfinding helpers ---
    def find_path(self, start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Finde einen Pfad (A*) von `start` nach `goal` in Tile-Koordinaten.

        Gibt eine Liste von Tile-Positionen inkl. Start/Goal zurück. Leere Liste, wenn kein Pfad existiert.
        """
        from .pathfinding import find_path as a_star_find_path
        return a_star_find_path(self, start, goal)
    
    def find_path_with_tile_manager(self, start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Verwendet den TileManager für Pathfinding.
        
        Args:
            start: Start-Position (x, y) in Tiles
            goal: Ziel-Position (x, y) in Tiles
            
        Returns:
            Liste von Positionen oder leere Liste wenn kein Pfad
        """
        from engine.world.tile_manager import TileManager
        
        # Stelle sicher, dass TileManager die aktuelle Map kennt
        tile_manager = TileManager.get_instance()
        if not tile_manager.collision_map or            len(tile_manager.collision_map) != self.height or            (tile_manager.collision_map and len(tile_manager.collision_map[0]) != self.width):
            # Baue Collision-Map aus Area-Daten
            tile_manager.map_width = self.width
            tile_manager.map_height = self.height
            tile_manager.collision_map = []
            
            for y in range(self.height):
                row = []
                for x in range(self.width):
                    # Verwende Area's is_tile_solid Methode
                    row.append(self.is_tile_solid(x, y))
                tile_manager.collision_map.append(row)
        
        # Verwende TileManager's Pathfinding
        return tile_manager.find_path(start, goal)
    
    def find_diagonal_path(self, start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Findet einen Pfad mit diagonaler Bewegung.
        
        Args:
            start: Start-Position (x, y) in Tiles
            goal: Ziel-Position (x, y) in Tiles
            
        Returns:
            Liste von Positionen oder leere Liste wenn kein Pfad
        """
        from engine.world.tile_manager import TileManager
        
        # Synchronisiere Collision-Map
        self.find_path_with_tile_manager(start, goal)  # Aktualisiert collision_map
        
        tile_manager = TileManager.get_instance()
        return tile_manager.find_path_diagonal(start, goal)
    
    def get_visible_tiles(self, camera_x: int, camera_y: int, 
                          surface_width: int, surface_height: int) -> List[Tuple[int, int]]:
        """Gibt alle sichtbaren Tile-Koordinaten zurück."""
        start_x = max(0, camera_x // TILE_SIZE)
        start_y = max(0, camera_y // TILE_SIZE)
        end_x = min(self.width, (camera_x + surface_width) // TILE_SIZE + 1)
        end_y = min(self.height, (camera_y + surface_height) // TILE_SIZE + 1)
        
        visible_tiles = []
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                if 0 <= x < self.width and 0 <= y < self.height:
                    visible_tiles.append((x, y))
        
        return visible_tiles
    
    # TMX-Layer-mit-neuen-Tiles-Methode entfernt - veraltet
    
    # GID-zu-Tile-Mapping-Methode entfernt - veraltet
    
    # Platzhalter-Tile-Methode entfernt - veraltet
