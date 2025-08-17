"""
Map Loading and Normalization for Untold Story
Handles both simple internal JSON format and Tiled JSON export format
"""

import json
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
        # Try loading from data/maps/
        map_path = f"maps/{map_id}.json"
        map_json = resources.load_json(map_path)
        
        if not map_json:
            raise ValueError(f"Could not load map: {map_id}")
        
        # Detect format and normalize
        if "tiledversion" in map_json:
            return MapLoader._load_tiled_map(map_id, map_json)
        else:
            return MapLoader._load_simple_map(map_id, map_json)
    
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
    def _convert_gids_to_tiles(gid_data: List[int], 
                               tilesets: List[Dict[str, Any]],
                               width: int, height: int) -> List[List[int]]:
        """
        Convert Tiled GIDs to local tile IDs.
        
        Args:
            gid_data: Flat array of GIDs from Tiled
            tilesets: List of tileset definitions
            width: Map width in tiles
            height: Map height in tiles
            
        Returns:
            2D array of tile IDs
        """
        # Tile flipping flags in Tiled
        FLIPPED_HORIZONTALLY_FLAG = 0x80000000
        FLIPPED_VERTICALLY_FLAG = 0x40000000
        FLIPPED_DIAGONALLY_FLAG = 0x20000000
        
        tiles = []
        for y in range(height):
            row = []
            for x in range(width):
                gid = gid_data[y * width + x]
                
                # Clear flip flags to get actual GID
                actual_gid = gid & ~(FLIPPED_HORIZONTALLY_FLAG | 
                                    FLIPPED_VERTICALLY_FLAG | 
                                    FLIPPED_DIAGONALLY_FLAG)
                
                if actual_gid == 0:
                    row.append(0)
                    continue
                
                # Find which tileset this GID belongs to
                tile_id = 0
                for tileset in tilesets:
                    firstgid = tileset.get("firstgid", 1)
                    tile_count = tileset.get("tilecount", 0)
                    
                    if firstgid <= actual_gid < firstgid + tile_count:
                        # Convert to local tile ID within this tileset
                        tile_id = actual_gid - firstgid
                        break
                
                row.append(tile_id)
            tiles.append(row)
        
        return tiles
    
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