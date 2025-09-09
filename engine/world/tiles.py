# -*- coding: utf-8 -*-
from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, List
from enum import IntEnum
import pygame

# Einheitliche Tile-Kante in Pixeln (GBC-/Pokémon-Stil)
TILE_SIZE: int = 16

# Entity Movement Constants
ENTITY_SPEED: float = 60.0  # Standard-Geschwindigkeit für 16x16 Tiles
ENTITY_INTERACTION_RANGE: float = 1.5  # Multiplier for TILE_SIZE

# Player Movement Constants
PLAYER_MOVE_SPEED: float = 7.5  # Tiles pro Sekunde (Gehen)
PLAYER_RUN_MULTIPLIER: float = 1.5  # Running speed multiplier
PLAYER_JUMP_MULTIPLIER: float = 1.5  # Jump speed multiplier
PLAYER_JUMP_HEIGHT: float = 0.5  # Jump height as TILE_SIZE multiplier

# NPC Movement Constants
NPC_MOVEMENT_SPEED: float = 30.0  # Pixels per second (slower than player)
NPC_MOVEMENT_DELAY: float = 2.0   # Seconds between movements
NPC_MOVEMENT_COOLDOWN: float = 2.0  # Seconds between movements in manager

# Pathfinding Constants
PATHFINDING_COOLDOWN: float = 0.5  # Halbe Sekunde zwischen Pathfinding-Versuchen
PATHFINDING_MAX_EXPANSIONS: int = 256  # Max nodes to check

# Animation Constants
ANIMATION_SPEED_MULTIPLIER: float = 1.0  # Default animation speed
ANIMATION_SPEED_FAST: float = 1.5  # Fast animation speed

# Camera Constants
CAMERA_SHAKE_INTENSITY: float = 0.0  # Default shake intensity
CAMERA_SHAKE_DURATION: float = 0.0   # Default shake duration
CAMERA_LERP_FACTOR: float = 1.0      # Camera lerp factor

# Map Constants
MAP_CACHE_TTL: float = 300.0  # 5 Minuten Cache-Lebensdauer
MAP_RENDER_TIME: float = 0.0  # Default render time

# Sound Constants
SOUND_VOLUME_DEFAULT: float = 0.5  # Default sound volume


class TileType(IntEnum):
    """Common tile type IDs for collision and interaction."""
    EMPTY = 0
    SOLID = 1
    GRASS = 2
    WATER = 3
    WARP = 4
    TRIGGER = 5
    SIGN = 6
    DOOR = 7
    STAIRS = 8
    LEDGE_DOWN = 9
    LEDGE_LEFT = 10
    LEDGE_RIGHT = 11
    LEDGE_UP = 12


@dataclass(frozen=True)
class Vec2:
    x: int
    y: int

class TileLayer(IntEnum):
    """Layer indices for map rendering."""
    GROUND = 0
    DECOR = 1
    COLLISION = 2
    OVERHANG = 3
    OBJECTS = 4

def tile_to_world(tx: int, ty: int) -> Tuple[int, int]:
    """Tile-Koordinaten (Grid) -> Weltpixel."""
    return tx * TILE_SIZE, ty * TILE_SIZE

def world_to_tile(px: int, py: int) -> Tuple[int, int]:
    """Weltpixel -> Tile-Koordinaten (Grid)."""
    return px // TILE_SIZE, py // TILE_SIZE

def rect_from_tile(tx: int, ty: int, w_tiles: int = 1, h_tiles: int = 1) -> pygame.Rect:
    """Erzeuge einen Pixel-Rect aus Tile-Koordinaten und -Größe."""
    return pygame.Rect(tx * TILE_SIZE, ty * TILE_SIZE, w_tiles * TILE_SIZE, h_tiles * TILE_SIZE)

def draw_grid(surface: pygame.Surface, camera_x: int = 0, camera_y: int = 0) -> None:
    """Einfaches Debug-Grid in TILE_SIZE-Abständen."""
    w, h = surface.get_size()
    offx = -(camera_x % TILE_SIZE)
    offy = -(camera_y % TILE_SIZE)
    for x in range(offx, w, TILE_SIZE):
        pygame.draw.line(surface, (0, 0, 0), (x, 0), (x, h))
        pygame.draw.line(surface, (255, 255, 255), (x + 1, 0), (x + 1, h))
    for y in range(offy, h, TILE_SIZE):
        pygame.draw.line(surface, (0, 0, 0), (0, y), (w, y))
        pygame.draw.line(surface, (255, 255, 255), (0, y + 1), (w, y + 1))

def get_tile_rect(tile_x: int, tile_y: int) -> pygame.Rect:
    """Get the world-space rectangle for a tile."""
    x, y = tile_to_world(tile_x, tile_y)
    return pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)

def rect_to_tiles(rect: pygame.Rect) -> List[Tuple[int, int]]:
    """Get all tile coordinates that a rectangle overlaps."""
    min_x, min_y = world_to_tile(rect.left, rect.top)
    max_x, max_y = world_to_tile(rect.right - 1, rect.bottom - 1)
    
    tiles = []
    for ty in range(min_y, max_y + 1):
        for tx in range(min_x, max_x + 1):
            tiles.append((tx, ty))
    return tiles

def is_tile_solid(collision_layer: List[List[int]], 
                  tile_x: int, tile_y: int,
                  width: int, height: int) -> bool:
    """Check if a tile is solid (blocks movement)."""
    # Out of bounds is considered solid
    if tile_x < 0 or tile_x >= width or tile_y < 0 or tile_y >= height:
        return True
    
    # Check collision value
    return collision_layer[tile_y][tile_x] == TileType.SOLID

def is_rect_colliding(rect: pygame.Rect, 
                      collision_layer: List[List[int]],
                      width: int, height: int) -> bool:
    """Check if a rectangle collides with any solid tiles."""
    tiles = rect_to_tiles(rect)
    for tile_x, tile_y in tiles:
        if is_tile_solid(collision_layer, tile_x, tile_y, width, height):
            return True
    return False


