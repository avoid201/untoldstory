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
    transition_type: str = "fade"  # Transition effect type
    spawn_point: str = "default"  # Spawn point identifier


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
        # Try loading from data/maps/ as JSON (Tiled export format)
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
            print(f"Could not load JSON map for {map_id}: {e}")
        
        # Try loading .tmx file as fallback (legacy)
        try:
            return MapLoader._load_tmx_file(map_id)
        except (FileNotFoundError, ValueError) as e:
            print(f"Could not load .tmx file for {map_id}: {e}")
        
        raise ValueError(f"Could not load map {map_id} in any format")
    
    @staticmethod
    def _load_simple_map(map_id: str, data: Dict[str, Any]) -> MapData:
        """
        Load a map in simple internal format.
        
        Expected format:
        {
            "name": "Map Name",
            "grid": [["W","F","F"], ["W","F","F"]],  # W=Wall, F=Floor, D=Door
            "start_x": 1,
            "start_y": 1
        }
        """
        # Parse grid to determine dimensions
        grid = data.get("grid", [])
        if not grid:
            raise ValueError(f"Map {map_id} has no grid data")
        
        height = len(grid)
        width = len(grid[0]) if grid else 0
        
        if width == 0:
            raise ValueError(f"Map {map_id} has invalid grid dimensions")
        
        # Convert grid to tile layers
        layers = {}
        
        # Ground layer (all tiles are floor by default)
        ground_layer = []
        for y in range(height):
            row = []
            for x in range(width):
                tile_type = grid[y][x] if y < len(grid) and x < len(grid[y]) else "F"
                # Convert tile types to numeric IDs
                if tile_type == "W":  # Wall
                    row.append(43)  # wall.png
                elif tile_type == "D":  # Door
                    row.append(62)  # door.png
                elif tile_type == "F":  # Floor
                    row.append(34)  # stone_floor.png
                else:
                    row.append(0)  # Empty
            ground_layer.append(row)
        
        layers["ground"] = ground_layer
        
        return MapData(
            id=map_id,
            name=data.get("name", map_id),
            width=width,
            height=height,
            tile_size=TILE_SIZE,
            layers=layers,
            warps=MapLoader._parse_warps(data.get("warps", [])),
            triggers=MapLoader._parse_triggers(data.get("triggers", [])),
            properties=data.get("properties", {}),
            tilesets=[]
        )
    
    @staticmethod
    def _load_tiled_map(map_id: str, data: Dict[str, Any]) -> MapData:
        """
        Load a map exported from Tiled in JSON format.
        
        This handles the new JSON format with individual tile loading.
        """
        width = data.get("width", 0)
        height = data.get("height", 0)
        tile_size = data.get("tilewidth", TILE_SIZE)
        
        if width == 0 or height == 0:
            raise ValueError(f"Invalid map dimensions: {width}x{height}")
        
        # Parse layers
        layers = {}
        for layer in data.get("layers", []):
            layer_name = layer.get("name", "unknown")
            layer_type = layer.get("type", "tilelayer")
            
            if layer_type == "tilelayer":
                # Handle tile data
                tile_data = layer.get("data", [])
                if tile_data:
                    # Convert 1D array to 2D
                    layer_2d = []
                    for y in range(height):
                        row = []
                        for x in range(width):
                            index = y * width + x
                            if index < len(tile_data):
                                # Handle GID with flip flags
                                gid = tile_data[index]
                                # Remove flip flags for now (can be added later if needed)
                                clean_gid = gid & 0x1FFFFFFF  # Remove flip flags
                                row.append(clean_gid)
                            else:
                                row.append(0)
                        layer_2d.append(row)
                    layers[layer_name] = layer_2d
            
            elif layer_type == "objectgroup":
                # Handle object layers (warps, triggers, etc.)
                objects = layer.get("objects", [])
                if layer_name.lower() == "warps":
                    warps = MapLoader._parse_tiled_warps(objects)
                elif layer_name.lower() == "triggers":
                    triggers = MapLoader._parse_tiled_triggers(objects)
        
        # Parse properties
        properties = {}
        for prop in data.get("properties", []):
            properties[prop.get("name", "")] = prop.get("value", "")
        
        return MapData(
            id=map_id,
            name=data.get("name", map_id),
            width=width,
            height=height,
            tile_size=tile_size,
            layers=layers,
            warps=MapLoader._parse_warps(data.get("warps", [])),
            triggers=MapLoader._parse_triggers(data.get("triggers", [])),
            properties=properties,
            tilesets=data.get("tilesets", [])
        )
    
    @staticmethod
    def _load_tmx_file(map_id: str) -> MapData:
        """
        Load a TMX file (legacy support).
        
        This is kept for backward compatibility but the new JSON format is preferred.
        """
        try:
            import xml.etree.ElementTree as ET
            
            tmx_path = Path(f"data/maps/{map_id}.tmx")
            if not tmx_path.exists():
                raise FileNotFoundError(f"TMX file not found: {tmx_path}")
            
            tree = ET.parse(tmx_path)
            root = tree.getroot()
            
            width = int(root.get("width", 0))
            height = int(root.get("height", 0))
            tile_size = int(root.get("tilewidth", TILE_SIZE))
            
            if width == 0 or height == 0:
                raise ValueError(f"Invalid TMX dimensions: {width}x{height}")
            
            # Parse layers
            layers = {}
            for layer in root.findall("layer"):
                layer_name = layer.get("name", "unknown")
                data_elem = layer.find("data")
                
                if data_elem is not None:
                    # Parse CSV or XML data
                    data_text = data_elem.text.strip() if data_elem.text else ""
                    if data_text:
                        # Handle CSV format
                        tile_ids = [int(x) for x in data_text.split(",") if x.strip()]
                        
                        # Convert to 2D array
                        layer_2d = []
                        for y in range(height):
                            row = []
                            for x in range(width):
                                index = y * width + x
                                if index < len(tile_ids):
                                    gid = tile_ids[index]
                                    # Remove flip flags
                                    clean_gid = gid & 0x1FFFFFFF
                                    row.append(clean_gid)
                                else:
                                    row.append(0)
                            layer_2d.append(row)
                        layers[layer_name] = layer_2d
            
            # Parse object layers for warps and triggers
            warps = []
            triggers = []
            for objgroup in root.findall("objectgroup"):
                group_name = objgroup.get("name", "").lower()
                
                for obj in objgroup.findall("object"):
                    obj_type = obj.get("type", "")
                    x = int(obj.get("x", 0)) // tile_size
                    y = int(obj.get("y", 0)) // tile_size
                    
                    if group_name == "warps" or obj_type == "warp":
                        # Parse warp properties
                        warp_props = {}
                        for prop in obj.findall("properties/property"):
                            name = prop.get("name", "")
                            value = prop.get("value", "")
                            warp_props[name] = value
                        
                        warps.append(Warp(
                            x=x, y=y,
                            to_map=warp_props.get("to_map", ""),
                            to_x=int(warp_props.get("to_x", 0)),
                            to_y=int(warp_props.get("to_y", 0)),
                            direction=warp_props.get("direction")
                        ))
                    
                    elif group_name == "triggers" or obj_type == "trigger":
                        # Parse trigger properties
                        trigger_props = {}
                        for prop in obj.findall("properties/property"):
                            name = prop.get("name", "")
                            value = prop.get("value", "")
                            trigger_props[name] = value
                        
                        triggers.append(Trigger(
                            x=x, y=y,
                            event=trigger_props.get("event", "unknown"),
                            args=trigger_props
                        ))
            
            return MapData(
                id=map_id,
                name=root.get("name", map_id),
                width=width,
                height=height,
                tile_size=tile_size,
                layers=layers,
                warps=warps,
                triggers=triggers,
                properties={},
                tilesets=[]
            )
            
        except Exception as e:
            raise ValueError(f"Failed to parse TMX file: {e}")
    
    @staticmethod
    def _parse_warps(warp_data: List[Dict[str, Any]]) -> List[Warp]:
        """Parse warp data from various formats."""
        warps = []
        for warp in warp_data:
            if isinstance(warp, dict):
                warps.append(Warp(
                    x=warp.get("x", 0),
                    y=warp.get("y", 0),
                    to_map=warp.get("to_map", ""),
                    to_x=warp.get("to_x", 0),
                    to_y=warp.get("to_y", 0),
                    direction=warp.get("direction")
                ))
        return warps
    
    @staticmethod
    def _parse_triggers(trigger_data: List[Dict[str, Any]]) -> List[Trigger]:
        """Parse trigger data from various formats."""
        triggers = []
        for trigger in trigger_data:
            if isinstance(trigger, dict):
                triggers.append(Trigger(
                    x=trigger.get("x", 0),
                    y=trigger.get("y", 0),
                    event=trigger.get("event", "unknown"),
                    args=trigger.get("args", {})
                ))
        return triggers
    
    @staticmethod
    def _parse_tiled_warps(objects: List[Dict[str, Any]]) -> List[Warp]:
        """Parse warps from Tiled object layer."""
        warps = []
        for obj in objects:
            if obj.get("type", "") == "warp":
                # Parse warp properties
                properties = {}
                for prop in obj.get("properties", []):
                    properties[prop.get("name", "")] = prop.get("value", "")
                
                warps.append(Warp(
                    x=int(obj.get("x", 0)) // TILE_SIZE,
                    y=int(obj.get("y", 0)) // TILE_SIZE,
                    to_map=properties.get("to_map", ""),
                    to_x=int(properties.get("to_x", 0)),
                    to_y=int(properties.get("to_y", 0)),
                    direction=properties.get("direction")
                ))
        return warps
    
    @staticmethod
    def _parse_tiled_triggers(objects: List[Dict[str, Any]]) -> List[Trigger]:
        """Parse triggers from Tiled object layer."""
        triggers = []
        for obj in objects:
            if obj.get("type", "") == "trigger":
                # Parse trigger properties
                properties = {}
                for prop in obj.get("properties", []):
                    properties[prop.get("name", "")] = prop.get("value", "")
                
                triggers.append(Trigger(
                    x=int(obj.get("x", 0)) // TILE_SIZE,
                    y=int(obj.get("y", 0)) // TILE_SIZE,
                    event=properties.get("event", "unknown"),
                    args=properties
                ))
        return triggers