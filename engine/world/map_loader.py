"""
Map Loading and Normalization for Untold Story
Handles both simple internal JSON format and Tiled JSON export format
"""

import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from engine.core.resources import resources
from engine.world.tiles import TILE_SIZE, TileType


@dataclass
class Warp:
    """Represents a warp point to another map."""
    x: int  # Tile X coordinate
    y: int  # Tile Y coordinate
    to_map: str  # Target map ID
    to_x: int  # Target tile X
    to_y: int  # Target tile Y
    direction: Optional[str] = None  # Optional: facing direction after warp


@dataclass
class Trigger:
    """Represents an interactive trigger on the map."""
    x: int  # Tile X coordinate
    y: int  # Tile Y coordinate
    event: str  # Event type (sign, cutscene, battle, etc.)
    args: Dict[str, Any]  # Event-specific arguments


@dataclass
class MapData:
    """Normalized map data structure."""
    id: str
    name: str
    width: int  # In tiles
    height: int  # In tiles
    tile_size: int
    layers: Dict[str, List[List[int]]]  # Layer name -> 2D tile array
    warps: List[Warp]
    triggers: List[Trigger]
    properties: Dict[str, Any]  # Custom properties (music, encounters, etc.)
    tilesets: List[Dict[str, Any]]  # Tileset data if from Tiled


class MapLoader:
    """Handles loading and normalization of map data."""
    
    @staticmethod
    def load_map(map_id: str) -> MapData:
        """
        Load a map by ID, auto-detecting format.
        
        Args:
            map_id: Map identifier (filename without extension)
            
        Returns:
            Normalized MapData object
            
        Raises:
            ValueError: If map cannot be loaded or parsed
        """
        # Try loading .tmx file first
        try:
            return MapLoader._load_tmx_file(map_id)
        except (FileNotFoundError, ValueError) as e:
            print(f"Could not load .tmx file for {map_id}: {e}")
        
        # Try loading from data/maps/ as JSON
        try:
            map_path = f"maps/{map_id}.json"
            map_json = resources.load_json(map_path)
            
            if not map_json:
                raise ValueError(f"Could not load map: {map_id}")
            
            # Detect format and normalize
            if "tiledversion" in map_json:
                return MapLoader._load_tiled_map(map_id, map_json)
            else:
                return MapLoader._load_simple_map(map_id, map_json)
        except Exception as e:
            raise ValueError(f"Could not load map {map_id} in any format: {e}")
    
    @staticmethod
    def _load_simple_map(map_id: str, data: Dict[str, Any]) -> MapData:
        """
        Load a map in simple internal format.
        
        Expected format:
        {
            "id": "map_id",
            "name": "Map Name",
            "size": {"w": 64, "h": 64, "tile": 16},
            "layers": {
                "ground": [[tile_ids...]],
                "decor": [[tile_ids...]],
                "collision": [[0/1...]]
            },
            "warps": [{"x": 10, "y": 5, "to": "other_map", "tx": 3, "ty": 7}],
            "triggers": [{"x": 12, "y": 8, "event": "sign", "args": {...}}],
            "properties": {"music": "town.ogg", "encounters": "town_day"}
        }
        """
        # Extract size
        size = data.get("size", {})
        width = size.get("w", 32)
        height = size.get("h", 32)
        tile_size = size.get("tile", TILE_SIZE)
        
        # Extract layers
        layers = {}
        for layer_name, layer_data in data.get("layers", {}).items():
            # Ensure it's a 2D array
            if layer_data and isinstance(layer_data[0], list):
                layers[layer_name] = layer_data
            else:
                # Convert 1D to 2D if needed
                layers[layer_name] = MapLoader._reshape_layer(layer_data, width, height)
        
        # Ensure required layers exist
        if "ground" not in layers:
            layers["ground"] = [[0] * width for _ in range(height)]
        if "collision" not in layers:
            layers["collision"] = [[0] * width for _ in range(height)]
        
        # Parse warps
        warps = []
        for warp_data in data.get("warps", []):
            warps.append(Warp(
                x=warp_data["x"],
                y=warp_data["y"],
                to_map=warp_data["to"],
                to_x=warp_data.get("tx", warp_data.get("to_x", 0)),
                to_y=warp_data.get("ty", warp_data.get("to_y", 0)),
                direction=warp_data.get("direction")
            ))
        
        # Parse triggers
        triggers = []
        for trigger_data in data.get("triggers", []):
            triggers.append(Trigger(
                x=trigger_data["x"],
                y=trigger_data["y"],
                event=trigger_data["event"],
                args=trigger_data.get("args", {})
            ))
        
        return MapData(
            id=data.get("id", map_id),
            name=data.get("name", map_id.replace("_", " ").title()),
            width=width,
            height=height,
            tile_size=tile_size,
            layers=layers,
            warps=warps,
            triggers=triggers,
            properties=data.get("properties", {}),
            tilesets=[]
        )
    
    @staticmethod
    def _load_tiled_map(map_id: str, data: Dict[str, Any]) -> MapData:
        """
        Load a map exported from Tiled in JSON format.
        
        Handles:
        - GID to tile ID conversion using firstgid
        - Layer types (tilelayer, objectgroup)
        - Tile flipping flags
        - Object warps and triggers
        """
        # Extract basic properties
        width = data["width"]
        height = data["height"]
        tile_width = data["tilewidth"]
        tile_height = data["tileheight"]
        
        # Load tilesets
        tilesets = data.get("tilesets", [])
        
        # Process layers
        layers = {}
        warps = []
        triggers = []
        
        for layer in data.get("layers", []):
            layer_name = layer["name"].lower()
            layer_type = layer.get("type", "tilelayer")
            
            if layer_type == "tilelayer":
                # Process tile layer
                if "data" in layer:
                    # Convert GIDs to local tile IDs
                    tile_data = MapLoader._convert_gids_to_tiles(
                        layer["data"], tilesets, width, height
                    )
                    layers[layer_name] = tile_data
                    
                    # Convert collision layer to binary
                    if layer_name == "collision":
                        layers[layer_name] = MapLoader._binarize_collision(tile_data)
            
            elif layer_type == "objectgroup":
                # Process object layer
                for obj in layer.get("objects", []):
                    # Convert pixel coords to tile coords
                    tile_x = int(obj["x"] // tile_width)
                    tile_y = int(obj["y"] // tile_height)
                    
                    obj_type = obj.get("type", "").lower()
                    obj_name = obj.get("name", "")
                    props = obj.get("properties", {})
                    
                    # Convert properties list to dict if needed
                    if isinstance(props, list):
                        props = {p["name"]: p["value"] for p in props}
                    
                    if obj_type == "warp":
                        warps.append(Warp(
                            x=tile_x,
                            y=tile_y,
                            to_map=props.get("to_map", ""),
                            to_x=props.get("to_x", 0),
                            to_y=props.get("to_y", 0),
                            direction=props.get("direction")
                        ))
                    elif obj_type == "trigger":
                        triggers.append(Trigger(
                            x=tile_x,
                            y=tile_y,
                            event=props.get("event", obj_name),
                            args=props
                        ))
        
        # Ensure required layers exist
        if "ground" not in layers:
            layers["ground"] = [[0] * width for _ in range(height)]
        if "collision" not in layers:
            layers["collision"] = [[0] * width for _ in range(height)]
        
        # Extract custom properties
        properties = {}
        if "properties" in data:
            props_list = data["properties"]
            if isinstance(props_list, list):
                properties = {p["name"]: p["value"] for p in props_list}
            else:
                properties = props_list
        
        return MapData(
            id=map_id,
            name=properties.get("name", map_id.replace("_", " ").title()),
            width=width,
            height=height,
            tile_size=tile_width,
            layers=layers,
            warps=warps,
            triggers=triggers,
            properties=properties,
            tilesets=tilesets
        )
    
    @staticmethod
    def _load_tmx_file(map_id: str) -> MapData:
        """
        Load a map directly from .tmx file.
        
        Args:
            map_id: Map identifier (filename without extension)
            
        Returns:
            Normalized MapData object
        """
        # Try to find .tmx file
        tmx_path = Path("data/maps") / f"{map_id}.tmx"
        if not tmx_path.exists():
            raise FileNotFoundError(f"TMX file not found: {tmx_path}")
        
        # Parse XML
        try:
            tree = ET.parse(tmx_path)
            root = tree.getroot()
        except ET.ParseError as e:
            raise ValueError(f"Invalid TMX file {map_id}: {e}")
        
        # Extract basic properties
        width = int(root.get('width', 32))
        height = int(root.get('height', 32))
        tile_width = int(root.get('tilewidth', 16))
        tile_height = int(root.get('tileheight', 16))
        
        # Load tilesets and create GID to tile name mapping
        tilesets = []
        gid_to_tile_mapping = {}
        
        for tileset_elem in root.findall('tileset'):
            tileset = {
                'firstgid': int(tileset_elem.get('firstgid', 1)),
                'source': tileset_elem.get('source', ''),
                'tilewidth': int(tileset_elem.get('tilewidth', 16)),
                'tileheight': int(tileset_elem.get('tileheight', 16))
            }
            tilesets.append(tileset)
            
            # Load the actual tileset file and create mapping
            tileset_mapping = MapLoader._load_tileset_mapping(tileset['source'])
            if tileset_mapping:
                for local_id, tile_name in tileset_mapping.items():
                    global_id = tileset['firstgid'] + local_id
                    gid_to_tile_mapping[global_id] = tile_name
        
        # Process layers
        layers = {}
        warps = []
        triggers = []
        
        for layer_elem in root.findall('layer'):
            layer_name = layer_elem.get('name', 'default').lower()
            
            # Process tile data
            data_elem = layer_elem.find('data')
            if data_elem is not None:
                encoding = data_elem.get('encoding', 'csv')
                if encoding == 'csv':
                    # Parse CSV data
                    csv_text = data_elem.text.strip()
                    tile_data = []
                    for line in csv_text.split('\n'):
                        if line.strip():
                            row = [int(x.strip()) for x in line.split(',') if x.strip()]
                            tile_data.append(row)
                    
                    # Convert GIDs to tile names using the mapping
                    tile_data = MapLoader._convert_gids_to_tile_names(
                        tile_data, gid_to_tile_mapping, width, height
                    )
                    
                    # Normalize layer names for better compatibility
                    normalized_name = MapLoader._normalize_layer_name(layer_name, map_id)
                    layers[normalized_name] = tile_data
                    
                    # Convert collision layer to binary if it's named collision
                    if 'collision' in normalized_name:
                        layers[normalized_name] = MapLoader._binarize_collision_from_names(tile_data)
        
        # Process object layers for warps and triggers
        for objectgroup_elem in root.findall('objectgroup'):
            group_name = objectgroup_elem.get('name', '').lower()
            
            for obj_elem in objectgroup_elem.findall('object'):
                obj_type = obj_elem.get('type', '').lower()
                obj_name = obj_elem.get('name', '')
                
                # Convert pixel coords to tile coords
                obj_x = int(float(obj_elem.get('x', 0)) // tile_width)
                obj_y = int(float(obj_elem.get('y', 0)) // tile_height)
                
                # Parse properties
                props = {}
                properties_elem = obj_elem.find('properties')
                if properties_elem is not None:
                    for prop_elem in properties_elem.findall('property'):
                        prop_name = prop_elem.get('name', '')
                        prop_value = prop_elem.get('value', '')
                        props[prop_name] = prop_value
                
                if obj_type == 'warp':
                    warps.append(Warp(
                        x=obj_x,
                        y=obj_y,
                        to_map=props.get('to_map', ''),
                        to_x=int(props.get('to_x', 0)),
                        to_y=int(props.get('to_y', 0)),
                        direction=props.get('direction')
                    ))
                elif obj_type == 'trigger':
                    triggers.append(Trigger(
                        x=obj_x,
                        y=obj_y,
                        event=props.get('event', obj_name),
                        args=props
                    ))
        
        # Ensure required layers exist
        if 'ground' not in layers:
            layers['ground'] = [['grass'] * width for _ in range(height)]
        if 'collision' not in layers:
            layers['collision'] = [[0] * width for _ in range(height)]
        
        # Extract custom properties from map
        properties = {}
        properties_elem = root.find('properties')
        if properties_elem is not None:
            for prop_elem in properties_elem.findall('property'):
                prop_name = prop_elem.get('name', '')
                prop_value = prop_elem.get('value', '')
                properties[prop_name] = prop_value
        
        return MapData(
            id=map_id,
            name=properties.get('name', map_id.replace('_', ' ').title()),
            width=width,
            height=height,
            tile_size=tile_width,
            layers=layers,
            warps=warps,
            triggers=triggers,
            properties=properties,
            tilesets=tilesets
        )

    @staticmethod
    def _load_tileset_mapping(tsx_source: str) -> Dict[int, str]:
        """
        Load tileset mapping from .tsx file and map to tile names.
        
        Args:
            tsx_source: Path to .tsx file
            
        Returns:
            Dictionary mapping local tile ID to tile name
        """
        try:
            # Try to find .tsx file in assets/gfx/tiles/
            tsx_path = Path("assets/gfx/tiles") / tsx_source
            if not tsx_path.exists():
                print(f"Warning: Tileset {tsx_source} not found at {tsx_path}")
                return {}
            
            # Parse .tsx file
            tree = ET.parse(tsx_path)
            root = tree.getroot()
            
            # Extract tileset info
            tile_count = int(root.get('tilecount', 0))
            columns = int(root.get('columns', 1))
            tileset_name = root.get('name', '').lower()
            
            # Create mapping based on tileset type
            mapping = {}
            for i in range(tile_count):
                # Map to common tile names based on tileset type
                tile_name = MapLoader._get_tile_name_from_tileset(i, tileset_name)
                mapping[i] = tile_name
            
            return mapping
            
        except Exception as e:
            print(f"Warning: Could not load tileset {tsx_source}: {e}")
            return {}

    @staticmethod
    def _get_tile_name_from_tileset(tile_id: int, tileset_name: str) -> str:
        """
        Get tile name based on tileset type and position.
        
        Args:
            tile_id: Local tile ID in tileset
            tileset_name: Name of the tileset
            
        Returns:
            Tile name that matches available sprites
        """
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
            # Fallback: use generic mapping
            return MapLoader._get_tile_name_from_position(tile_id, 12)

    @staticmethod
    def _get_tile_name_from_position(tile_id: int, columns: int) -> str:
        """
        Get tile name based on position in tileset.
        Maps to actual tile names that the SpriteManager can load.
        
        Args:
            tile_id: Local tile ID in tileset
            columns: Number of columns in tileset
            
        Returns:
            Tile name that matches available sprites
        """
        # Map tile positions to actual tile names based on the tileset layout
        # This mapping should correspond to the actual tile sprites available
        
        # Tileset 1: Ground tiles (grass, dirt, path, etc.)
        ground_tiles = [
            'grass_1', 'grass_2', 'grass_3', 'grass_4', 'grass',  # 0-4
            'dirt_1', 'dirt_2', 'dirt', 'path_1', 'path_2', 'path',  # 5-10
            'gravel_1', 'gravel_2', 'gravel', 'sand_1', 'sand_2', 'sand',  # 11-15
            'water_1', 'water_2', 'water', 'stone_1', 'stone_2', 'stone',  # 16-20
            'tree_small', 'bush', 'bush_1', 'bush_2'  # 21-23
        ]
        
        # Objects tileset: Furniture and objects
        object_tiles = [
            'barrel', 'bed', 'bookshelf', 'boulder', 'chair', 'crate',  # 0-5
            'door', 'fence_h', 'fence_v', 'gravestone', 'lamp_post', 'mailbox',  # 6-11
            'potted_plant', 'sign', 'table', 'tv', 'well', 'window'  # 12-17
        ]
        
        # Terrain tileset: Special terrain features
        terrain_tiles = [
            'cliff_face', 'flower_blue', 'flower_red', 'ledge', 'rock_1', 'rock_2',  # 0-5
            'rock', 'roof_blue', 'roof_red', 'roof_ridge', 'roof', 'stairs_h',  # 6-11
            'stairs_v', 'stairs', 'stone_floor', 'stump', 'tall_grass_1',  # 12-16
            'tall_grass_2', 'tall_grass', 'wall_brick', 'wall_plaster', 'wall',  # 17-21
            'warp_carpet', 'wood_floor'  # 22-23
        ]
        
        # Building tileset: Interior and building elements
        building_tiles = [
            'carpet', 'wall', 'window', 'door', 'stairs', 'roof',  # 0-5
            'floor', 'ceiling', 'pillar', 'arch', 'gate', 'bridge'  # 6-11
        ]
        
        # Return the appropriate tile name based on position
        if tile_id < len(ground_tiles):
            return ground_tiles[tile_id]
        elif tile_id < len(object_tiles):
            return object_tiles[tile_id]
        elif tile_id < len(terrain_tiles):
            return terrain_tiles[tile_id]
        elif tile_id < len(building_tiles):
            return building_tiles[tile_id]
        else:
            # Fallback to generic name
            return f"tile_{tile_id}"

    @staticmethod
    def _convert_gids_to_tile_names(tile_data: List[List[int]], 
                                   gid_to_tile_mapping: Dict[int, str],
                                   width: int, height: int) -> List[List[str]]:
        """
        Convert Tiled GIDs to tile names using the mapping.
        
        Args:
            tile_data: 2D array of GIDs from TMX
            gid_to_tile_mapping: Mapping from GID to tile name
            width: Map width in tiles
            height: Map height in tiles
            
        Returns:
            2D array of tile names
        """
        # Tile flipping flags in Tiled
        FLIPPED_HORIZONTALLY_FLAG = 0x80000000
        FLIPPED_VERTICALLY_FLAG = 0x40000000
        FLIPPED_DIAGONALLY_FLAG = 0x20000000
        
        result = []
        for row in tile_data:
            new_row = []
            for gid in row:
                # Clear flip flags to get actual GID
                actual_gid = gid & ~(FLIPPED_HORIZONTALLY_FLAG | 
                                    FLIPPED_VERTICALLY_FLAG | 
                                    FLIPPED_DIAGONALLY_FLAG)
                
                if actual_gid == 0:
                    new_row.append('grass')  # Default to grass for empty tiles
                    continue
                
                # Get tile name from mapping
                tile_name = gid_to_tile_mapping.get(actual_gid, 'grass')
                new_row.append(tile_name)
            
            result.append(new_row)
        
        return result
    
    @staticmethod
    def _binarize_collision(layer_data: List[List[int]]) -> List[List[int]]:
        """
        Convert collision layer to binary (0 or 1).
        
        Args:
            layer_data: 2D array of tile IDs
            
        Returns:
            2D array with 0 (passable) or 1 (solid)
        """
        result = []
        for row in layer_data:
            binary_row = [1 if tile > 0 else 0 for tile in row]
            result.append(binary_row)
        return result
    
    @staticmethod
    def _binarize_collision_from_names(tile_data: List[List[str]]) -> List[List[int]]:
        """
        Convert collision layer with tile names to binary (0 or 1).
        
        Args:
            tile_data: 2D array of tile names
            
        Returns:
            2D array with 0 (passable) or 1 (solid)
        """
        # Define which tiles are solid (collision)
        solid_tiles = {
            'wall', 'wall_brick', 'wall_plaster', 'tree', 'tree_small',
            'bush', 'bush_1', 'bush_2', 'rock', 'rock_1', 'rock_2',
            'boulder', 'fence_h', 'fence_v', 'door', 'window'
        }
        
        result = []
        for row in tile_data:
            binary_row = [1 if tile in solid_tiles else 0 for tile in row]
            result.append(binary_row)
        
        return result

    @staticmethod
    def _normalize_layer_name(layer_name: str, map_id: str) -> str:
        """
        Normalize layer names for better compatibility with the game system.
        
        Args:
            layer_name: Original layer name from TMX
            map_id: Map identifier for context
            
        Returns:
            Normalized layer name
        """
        layer_name = layer_name.lower().strip()
        
        # Common layer name mappings
        layer_mappings = {
            'tile layer 1': 'ground',
            'tile layer 2': 'decor',
            'tile layer 3': 'objects',
            'tile layer 4': 'overlay',
            'kies': 'ground',
            'rockundway': 'decor',
            'decor': 'decor',
            'objects': 'objects',
            'overlay': 'overlay',
            'collision': 'collision'
        }
        
        # Return mapped name if available, otherwise return original
        return layer_mappings.get(layer_name, layer_name)
    
    @staticmethod
    def _reshape_layer(flat_data: List[int], width: int, height: int) -> List[List[int]]:
        """
        Convert flat array to 2D array.
        
        Args:
            flat_data: 1D array of tiles
            width: Width in tiles
            height: Height in tiles
            
        Returns:
            2D array of tiles
        """
        if not flat_data:
            return [[0] * width for _ in range(height)]
        
        result = []
        for y in range(height):
            row = flat_data[y * width:(y + 1) * width]
            # Pad if necessary
            if len(row) < width:
                row.extend([0] * (width - len(row)))
            result.append(row)
        
        return result
    
    @staticmethod
    def validate_map(map_data: MapData) -> List[str]:
        """
        Validate map data for common issues.
        
        Args:
            map_data: MapData to validate
            
        Returns:
            List of warning/error messages
        """
        issues = []
        
        # Check dimensions
        if map_data.width <= 0 or map_data.height <= 0:
            issues.append(f"Invalid map dimensions: {map_data.width}x{map_data.height}")
        
        # Check layer dimensions
        for layer_name, layer_data in map_data.layers.items():
            if len(layer_data) != map_data.height:
                issues.append(f"Layer '{layer_name}' height mismatch")
            elif layer_data and len(layer_data[0]) != map_data.width:
                issues.append(f"Layer '{layer_name}' width mismatch")
        
        # Check warps
        for warp in map_data.warps:
            if warp.x < 0 or warp.x >= map_data.width:
                issues.append(f"Warp at ({warp.x},{warp.y}) out of X bounds")
            if warp.y < 0 or warp.y >= map_data.height:
                issues.append(f"Warp at ({warp.x},{warp.y}) out of Y bounds")
        
        # Check triggers
        for trigger in map_data.triggers:
            if trigger.x < 0 or trigger.x >= map_data.width:
                issues.append(f"Trigger at ({trigger.x},{trigger.y}) out of X bounds")
            if trigger.y < 0 or trigger.y >= map_data.height:
                issues.append(f"Trigger at ({trigger.x},{trigger.y}) out of Y bounds")
        
        return issues