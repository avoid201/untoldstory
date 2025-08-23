"""
Tile Manager - Zentrales Tile-Management mit TMX-Support und Pathfinding
"""

import pygame
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
import heapq
import json

from engine.world.tiles import TILE_SIZE

@dataclass
class TileData:
    """Daten für ein einzelnes Tile"""
    gid: int
    surface: pygame.Surface
    collision: bool = False
    properties: Dict = None
    
    def __post_init__(self):
        if self.properties is None:
            self.properties = {}

class TileManager:
    """
    Verwaltet alle Tile-bezogenen Operationen.
    
    Features:
    - TMX/TSX Parsing mit korrektem GID-Mapping
    - Tile-Caching für Performance
    - Pathfinding mit A*-Algorithmus
    - Collision-Detection
    - Externe Daten-Integration (NPCs, Warps)
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        
        self._initialized = True
        
        # Tile-Daten
        self.tiles: Dict[int, TileData] = {}
        self.tilesets: Dict[str, Dict] = {}
        
        # Map-Daten
        self.collision_map: List[List[bool]] = []
        self.map_width: int = 0
        self.map_height: int = 0
        
        # Externe Daten
        self.npcs_data: Dict = {}
        self.warps_data: Dict = {}
        self.dialogues_data: Dict = {}
        
        # Pathfinding-Cache
        self._path_cache: Dict[Tuple, List] = {}
        
        # Lade externe Daten
        self._load_external_data()
    
    @classmethod
    def get_instance(cls) -> 'TileManager':
        """Gibt die Singleton-Instanz zurück"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def _load_external_data(self):
        """Lädt externe JSON-Daten"""
        game_data_path = Path("data/game_data")
        
        # NPCs laden
        npcs_file = game_data_path / "npcs.json"
        if npcs_file.exists():
            with open(npcs_file, 'r', encoding='utf-8') as f:
                self.npcs_data = json.load(f)
            print(f"[TileManager] NPCs geladen: {len(self.npcs_data)} Maps")
        
        # Warps laden
        warps_file = game_data_path / "warps.json"
        if warps_file.exists():
            with open(warps_file, 'r', encoding='utf-8') as f:
                self.warps_data = json.load(f)
            print(f"[TileManager] Warps geladen: {len(self.warps_data)} Maps")
        
        # Dialoge laden
        dialogues_file = game_data_path / "dialogues.json"
        if dialogues_file.exists():
            with open(dialogues_file, 'r', encoding='utf-8') as f:
                self.dialogues_data = json.load(f)
            print(f"[TileManager] Dialoge geladen: {len(self.dialogues_data)} Einträge")
    
    def load_tmx_map(self, tmx_path: Path) -> Dict:
        """
        Lädt eine TMX-Map komplett.
        
        Args:
            tmx_path: Pfad zur TMX-Datei
            
        Returns:
            Dictionary mit allen Map-Daten
        """
        print(f"[TileManager] Lade TMX: {tmx_path}")
        
        # Parse TMX
        tree = ET.parse(tmx_path)
        root = tree.getroot()
        
        # Map-Eigenschaften
        map_data = {
            'width': int(root.get('width', 32)),
            'height': int(root.get('height', 32)),
            'tile_width': int(root.get('tilewidth', 16)),
            'tile_height': int(root.get('tileheight', 16)),
            'layers': {},
            'tilesets': [],
            'objects': [],
            'properties': {}
        }
        
        self.map_width = map_data['width']
        self.map_height = map_data['height']
        
        # Lade Tilesets
        for tileset_elem in root.findall('tileset'):
            firstgid = int(tileset_elem.get('firstgid', 1))
            source = tileset_elem.get('source', '')
            
            if source:
                tsx_path = tmx_path.parent / source
                tileset_data = self._load_tsx_tileset(tsx_path, firstgid)
                if tileset_data:
                    map_data['tilesets'].append(tileset_data)
        
        # Lade Layer
        for layer_elem in root.findall('layer'):
            layer_name = layer_elem.get('name', 'default')
            layer_data = self._parse_layer(layer_elem)
            map_data['layers'][layer_name] = layer_data
            
            # Spezielle Behandlung für Collision-Layer
            if layer_name.lower() == 'collision':
                self._build_collision_map(layer_data)
        
        # Lade Objekte
        for objectgroup_elem in root.findall('objectgroup'):
            objects = self._parse_objects(objectgroup_elem)
            map_data['objects'].extend(objects)
        
        # Map-Properties
        properties_elem = root.find('properties')
        if properties_elem is not None:
            map_data['properties'] = self._parse_properties(properties_elem)
        
        return map_data
    
    def _load_tsx_tileset(self, tsx_path: Path, firstgid: int) -> Optional[Dict]:
        """Lädt ein TSX-Tileset"""
        if not tsx_path.exists():
            print(f"[TileManager] TSX nicht gefunden: {tsx_path}")
            return None
        
        try:
            tree = ET.parse(tsx_path)
            root = tree.getroot()
            
            tileset_data = {
                'name': root.get('name', tsx_path.stem),
                'firstgid': firstgid,
                'tile_width': int(root.get('tilewidth', 16)),
                'tile_height': int(root.get('tileheight', 16)),
                'tile_count': int(root.get('tilecount', 0)),
                'columns': int(root.get('columns', 1)),
                'tiles': {}
            }
            
            # Finde Bild
            image_elem = root.find('image')
            if image_elem is None:
                return tileset_data
            
            # Konstruiere Bildpfad
            image_source = image_elem.get('source', '')
            if image_source.startswith('../../'):
                image_path = Path(image_source.replace('../../', ''))
            else:
                image_path = tsx_path.parent / image_source
            
            if not image_path.exists():
                # Versuche alternative Pfade
                alt_paths = [
                    Path("assets/gfx/tiles/tilesets") / image_path.name,
                    Path("assets/gfx/tilesets") / image_path.name,
                    Path("data/tilesets") / image_path.name
                ]
                
                for alt_path in alt_paths:
                    if alt_path.exists():
                        image_path = alt_path
                        break
            
            if not image_path.exists():
                print(f"[TileManager] Tileset-Bild nicht gefunden: {image_path}")
                return tileset_data
            
            # Lade und zerschneide Tileset
            tileset_surface = pygame.image.load(str(image_path)).convert_alpha()
            self._extract_tiles(tileset_surface, tileset_data, firstgid)
            
            # Parse Tile-Properties
            for tile_elem in root.findall('tile'):
                tile_id = int(tile_elem.get('id', 0))
                gid = firstgid + tile_id
                
                # Properties
                props_elem = tile_elem.find('properties')
                if props_elem is not None:
                    properties = self._parse_properties(props_elem)
                    if gid in self.tiles:
                        self.tiles[gid].properties = properties
                        # Setze Collision basierend auf Properties
                        if properties.get('collision', False):
                            self.tiles[gid].collision = True
            
            print(f"[TileManager] Tileset geladen: {tileset_data['name']} ({tileset_data['tile_count']} Tiles)")
            return tileset_data
            
        except Exception as e:
            print(f"[TileManager] Fehler beim Laden von TSX {tsx_path}: {e}")
            return None
    
    def _extract_tiles(self, surface: pygame.Surface, tileset_data: Dict, firstgid: int):
        """Extrahiert einzelne Tiles aus einem Tileset"""
        tile_width = tileset_data['tile_width']
        tile_height = tileset_data['tile_height']
        columns = tileset_data['columns']
        tile_count = tileset_data['tile_count']
        
        for tile_id in range(tile_count):
            col = tile_id % columns
            row = tile_id // columns
            
            x = col * tile_width
            y = row * tile_height
            
            # Extrahiere Tile
            tile_surf = pygame.Surface((tile_width, tile_height), pygame.SRCALPHA)
            tile_surf.blit(surface, (0, 0), (x, y, tile_width, tile_height))
            
            # Skaliere auf TILE_SIZE falls nötig
            if tile_width != TILE_SIZE or tile_height != TILE_SIZE:
                tile_surf = pygame.transform.scale(tile_surf, (TILE_SIZE, TILE_SIZE))
            
            # Speichere Tile
            gid = firstgid + tile_id
            self.tiles[gid] = TileData(gid=gid, surface=tile_surf)
    
    def _parse_layer(self, layer_elem) -> List[List[int]]:
        """Parst einen TMX-Layer"""
        width = int(layer_elem.get('width', self.map_width))
        height = int(layer_elem.get('height', self.map_height))
        
        # Initialisiere Layer-Daten
        layer_data = [[0 for _ in range(width)] for _ in range(height)]
        
        # Parse Tile-Daten
        data_elem = layer_elem.find('data')
        if data_elem is not None:
            encoding = data_elem.get('encoding', 'csv')
            
            if encoding == 'csv':
                csv_text = data_elem.text.strip()
                tiles = []
                
                for line in csv_text.split('\n'):
                    if not line.strip():
                        continue
                    for gid_str in line.split(','):
                        if gid_str.strip():
                            gid = int(gid_str.strip())
                            # Entferne Flip-Flags
                            FLIP_FLAGS = 0x80000000 | 0x40000000 | 0x20000000
                            clean_gid = gid & ~FLIP_FLAGS
                            tiles.append(clean_gid)
                
                # Fülle Layer-Daten
                for y in range(height):
                    for x in range(width):
                        idx = y * width + x
                        if idx < len(tiles):
                            layer_data[y][x] = tiles[idx]
        
        return layer_data
    
    def _parse_objects(self, objectgroup_elem) -> List[Dict]:
        """Parst Objekte aus einem Objectgroup"""
        objects = []
        
        for obj_elem in objectgroup_elem.findall('object'):
            obj = {
                'id': int(obj_elem.get('id', 0)),
                'name': obj_elem.get('name', ''),
                'type': obj_elem.get('type', ''),
                'x': float(obj_elem.get('x', 0)),
                'y': float(obj_elem.get('y', 0)),
                'width': float(obj_elem.get('width', 0)),
                'height': float(obj_elem.get('height', 0)),
                'properties': {}
            }
            
            # Parse Properties
            props_elem = obj_elem.find('properties')
            if props_elem is not None:
                obj['properties'] = self._parse_properties(props_elem)
            
            objects.append(obj)
        
        return objects
    
    def _parse_properties(self, properties_elem) -> Dict:
        """Parst Properties aus einem Properties-Element"""
        properties = {}
        
        for prop_elem in properties_elem.findall('property'):
            name = prop_elem.get('name', '')
            value = prop_elem.get('value', '')
            prop_type = prop_elem.get('type', 'string')
            
            # Konvertiere Wert basierend auf Typ
            if prop_type == 'bool':
                value = value.lower() == 'true'
            elif prop_type == 'int':
                value = int(value)
            elif prop_type == 'float':
                value = float(value)
            
            properties[name] = value
        
        return properties
    
    def _build_collision_map(self, collision_layer: List[List[int]]):
        """Baut die Kollisions-Map auf"""
        self.collision_map = []
        
        for row in collision_layer:
            collision_row = []
            for tile_gid in row:
                # Tile-ID > 0 bedeutet Kollision
                collision_row.append(tile_gid > 0)
            self.collision_map.append(collision_row)
    
    def get_tile(self, gid: int) -> Optional[pygame.Surface]:
        """
        Holt ein Tile nach GID.
        
        Args:
            gid: Global Tile ID
            
        Returns:
            Tile-Surface oder None
        """
        if gid in self.tiles:
            return self.tiles[gid].surface
        return None
    
    def is_collision(self, x: int, y: int) -> bool:
        """
        Prüft ob eine Position eine Kollision hat.
        
        Args:
            x: X-Position in Tiles
            y: Y-Position in Tiles
            
        Returns:
            True wenn Kollision, sonst False
        """
        # Prüfe Map-Grenzen
        if x < 0 or x >= self.map_width or y < 0 or y >= self.map_height:
            return True
        
        # Prüfe Collision-Map
        if self.collision_map and y < len(self.collision_map) and x < len(self.collision_map[y]):
            return self.collision_map[y][x]
        
        return False
    
    def find_path(self, start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Findet einen Pfad mit A*-Algorithmus.
        
        Args:
            start: Start-Position (x, y) in Tiles
            goal: Ziel-Position (x, y) in Tiles
            
        Returns:
            Liste von Positionen oder leere Liste wenn kein Pfad
        """
        # Prüfe Cache
        cache_key = (start, goal)
        if cache_key in self._path_cache:
            return self._path_cache[cache_key].copy()
        
        # A* Implementierung
        def heuristic(a: Tuple[int, int], b: Tuple[int, int]) -> float:
            """Manhattan-Distanz als Heuristik"""
            return abs(a[0] - b[0]) + abs(a[1] - b[1])
        
        # Priority Queue: (f_score, counter, position)
        counter = 0
        open_set = [(0, counter, start)]
        came_from = {}
        g_score = {start: 0}
        f_score = {start: heuristic(start, goal)}
        closed_set = set()
        
        while open_set:
            current_f, _, current = heapq.heappop(open_set)
            
            if current == goal:
                # Rekonstruiere Pfad
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                
                # Cache Pfad
                self._path_cache[cache_key] = path.copy()
                
                return path
            
            if current in closed_set:
                continue
            
            closed_set.add(current)
            
            # Prüfe Nachbarn (4-direktional)
            neighbors = [
                (current[0] + 1, current[1]),  # Rechts
                (current[0] - 1, current[1]),  # Links
                (current[0], current[1] + 1),  # Unten
                (current[0], current[1] - 1)   # Oben
            ]
            
            for neighbor in neighbors:
                # Prüfe ob Nachbar begehbar ist
                if self.is_collision(neighbor[0], neighbor[1]):
                    continue
                
                if neighbor in closed_set:
                    continue
                
                tentative_g = g_score[current] + 1
                
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + heuristic(neighbor, goal)
                    
                    counter += 1
                    heapq.heappush(open_set, (f_score[neighbor], counter, neighbor))
        
        # Kein Pfad gefunden
        return []
    
    def find_path_diagonal(self, start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Findet einen Pfad mit diagonaler Bewegung.
        
        Args:
            start: Start-Position (x, y) in Tiles
            goal: Ziel-Position (x, y) in Tiles
            
        Returns:
            Liste von Positionen oder leere Liste wenn kein Pfad
        """
        def heuristic(a: Tuple[int, int], b: Tuple[int, int]) -> float:
            """Euclidean-Distanz für diagonale Bewegung"""
            dx = abs(a[0] - b[0])
            dy = abs(a[1] - b[1])
            return (dx * dx + dy * dy) ** 0.5
        
        # Priority Queue
        counter = 0
        open_set = [(0, counter, start)]
        came_from = {}
        g_score = {start: 0}
        f_score = {start: heuristic(start, goal)}
        closed_set = set()
        
        while open_set:
            current_f, _, current = heapq.heappop(open_set)
            
            if current == goal:
                # Rekonstruiere Pfad
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                return path
            
            if current in closed_set:
                continue
            
            closed_set.add(current)
            
            # Prüfe alle 8 Nachbarn
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue
                    
                    neighbor = (current[0] + dx, current[1] + dy)
                    
                    # Prüfe ob Nachbar begehbar ist
                    if self.is_collision(neighbor[0], neighbor[1]):
                        continue
                    
                    # Bei diagonaler Bewegung: Prüfe ob Ecken frei sind
                    if dx != 0 and dy != 0:
                        if self.is_collision(current[0] + dx, current[1]) or \
                           self.is_collision(current[0], current[1] + dy):
                            continue
                    
                    if neighbor in closed_set:
                        continue
                    
                    # Kosten: 1 für gerade, 1.414 für diagonal
                    move_cost = 1.414 if (dx != 0 and dy != 0) else 1
                    tentative_g = g_score[current] + move_cost
                    
                    if neighbor not in g_score or tentative_g < g_score[neighbor]:
                        came_from[neighbor] = current
                        g_score[neighbor] = tentative_g
                        f_score[neighbor] = tentative_g + heuristic(neighbor, goal)
                        
                        counter += 1
                        heapq.heappush(open_set, (f_score[neighbor], counter, neighbor))
        
        return []
    
    def clear_path_cache(self):
        """Leert den Pathfinding-Cache"""
        self._path_cache.clear()
    
    def get_npcs_for_map(self, map_id: str) -> Dict:
        """
        Holt alle NPCs für eine Map.
        
        Args:
            map_id: ID der Map
            
        Returns:
            Dictionary mit NPC-Daten
        """
        return self.npcs_data.get(map_id, {})
    
    def get_warps_for_map(self, map_id: str) -> Dict:
        """
        Holt alle Warps für eine Map.
        
        Args:
            map_id: ID der Map
            
        Returns:
            Dictionary mit Warp-Daten
        """
        return self.warps_data.get(map_id, {})
    
    def get_dialogue(self, dialogue_id: str) -> Dict:
        """
        Holt einen Dialog.
        
        Args:
            dialogue_id: ID des Dialogs
            
        Returns:
            Dialog-Daten oder None
        """
        return self.dialogues_data.get(dialogue_id, None)

# Singleton-Instanz wird über get_instance() Methode bereitgestellt