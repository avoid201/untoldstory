"""
Area/Map Rendering System for Untold Story
Handles rendering of map layers with tile graphics and camera culling
"""

import pygame
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from ..graphics.sprite_manager import SpriteManager

@dataclass
class Area:
    """Represents a game area with multiple layers and rendering capabilities."""
    
    id: str
    name: str
    width: int = None  # In tiles
    height: int = None  # In tiles
    size: Dict[str, int] = None  # Legacy format: {"w": 10, "h": 8, "tile": 64}
    layers: Dict[str, List[List[int]]] = None  # Layer name -> 2D tile array
    warps: List[Dict[str, Any]] = None  # Warp points
    triggers: List[Dict[str, Any]] = None  # Event triggers
    properties: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.properties is None:
            self.properties = {}
        if self.warps is None:
            self.warps = []
        if self.triggers is None:
            self.triggers = []
        
        # Konvertiere legacy size-Format zu width/height
        if self.size and (self.width is None or self.height is None):
            self.width = self.size.get("w", 10)
            self.height = self.size.get("h", 8)
        
        # Fallback-Werte
        if self.width is None:
            self.width = 10
        if self.height is None:
            self.height = 8
        
        # Initialisiere nur den SpriteManager
        self.sprite_manager = SpriteManager()
        
        # RenderManager wird bei Bedarf geladen
        self._render_manager = None
        
        # Entities-Liste initialisieren
        if not hasattr(self, 'entities'):
            self.entities = []
    
    @property
    def render_manager(self):
        """Lazy loading des RenderManagers"""
        if self._render_manager is None:
            from ..graphics.render_manager import RenderManager
            self._render_manager = RenderManager()
        return self._render_manager
    
    def render(self, surface: pygame.Surface, camera_x: int = 0, camera_y: int = 0):
        """Rendert alle sichtbaren Layer der Area mit dem neuen RenderManager."""
        # Erstelle eine temporäre Camera-Instanz für den RenderManager
        from .camera import Camera
        temp_camera = Camera()
        temp_camera.x = camera_x
        temp_camera.y = camera_y
        temp_camera.viewport_width = surface.get_width()
        temp_camera.viewport_height = surface.get_height()
        
        # Verwende den RenderManager für das Rendering
        self.render_manager.render_scene(surface, self, temp_camera)
    
    def _render_layer(self, surface: pygame.Surface, layer_name: str, 
                      camera_x: int = 0, camera_y: int = 0):
        """Veraltete Methode - wird durch RenderManager ersetzt"""
        print(f"Warnung: _render_layer wird nicht mehr verwendet. Verwende RenderManager.")
    
    def get_tile_at(self, x: int, y: int, layer_name: str = "collision") -> int:
        """Gibt die Tile-ID an einer bestimmten Position zurück."""
        if layer_name not in self.layers:
            return 0
        
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.layers[layer_name][y][x]
        return 0
    
    def add_entity(self, entity) -> None:
        """Fügt eine Entity zur Area hinzu"""
        if entity not in self.entities:
            self.entities.append(entity)
    
    def remove_entity(self, entity) -> None:
        """Entfernt eine Entity aus der Area"""
        if entity in self.entities:
            self.entities.remove(entity)
    
    def is_tile_solid(self, x: int, y: int) -> bool:
        """Prüft, ob ein Tile an der Position solid (undurchlässig) ist."""
        # Verwende den TileRenderer für die Kollisionsprüfung
        tile_id = self.get_tile_at(x, y, "collision")
        if tile_id > 0:
            return not self.render_manager.tile_renderer.is_tile_walkable(tile_id)
        return False  # 0 = durchlässig
    
    def get_visible_tiles(self, camera_x: int, camera_y: int, 
                          surface_width: int, surface_height: int) -> List[Tuple[int, int]]:
        """Gibt alle sichtbaren Tile-Koordinaten zurück."""
        from engine.world.tiles import TILE_SIZE
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

    # --- Pathfinding helpers ---
    def find_path(self, start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Finde einen Pfad (A*) von `start` nach `goal` in Tile-Koordinaten.

        Gibt eine Liste von Tile-Positionen inkl. Start/Goal zurück. Leere Liste, wenn kein Pfad existiert.
        """
        from .pathfinding import find_path as a_star_find_path

        return a_star_find_path(self, start, goal)
    
    def render_debug_info(self, surface: pygame.Surface, camera_x: int, camera_y: int):
        """Rendert Debug-Informationen über die Area."""
        font = pygame.font.Font(None, 24)
        
        # Area-Info
        info_text = f"Area: {self.name} ({self.width}x{self.height})"
        text_surface = font.render(info_text, True, (255, 255, 255))
        surface.blit(text_surface, (10, 10))
        
        # Camera-Info
        camera_text = f"Camera: ({camera_x}, {camera_y})"
        text_surface = font.render(camera_text, True, (255, 255, 255))
        surface.blit(text_surface, (10, 35))
        
        # Sichtbare Tiles
        visible_count = len(self.get_visible_tiles(camera_x, camera_y, 
                                                  surface.get_width(), surface.get_height()))
        visible_text = f"Visible Tiles: {visible_count}"
        text_surface = font.render(visible_text, True, (255, 255, 255))
        surface.blit(text_surface, (10, 60))
        
        # Sprite-Cache-Info
        cache_info = self.sprite_manager.get_cache_info()
        cache_text = f"Sprites: {cache_info['total_sprites']}"
        text_surface = font.render(cache_text, True, (255, 255, 255))
        surface.blit(text_surface, (10, 85))
        
        # Tile-Mapping-Info
        mapping_text = f"Tile-Mappings: {cache_info['tile_mappings']}"
        text_surface = font.render(mapping_text, True, (255, 255, 255))
        surface.blit(text_surface, (10, 110))
    
    def get_tile_info(self, x: int, y: int, layer_name: str = "ground") -> Optional[Dict]:
        """Gibt Informationen über eine Tile an einer bestimmten Position zurück."""
        tile_id = self.get_tile_at(x, y, layer_name)
        if tile_id > 0:
            return self.sprite_manager.get_tile_info(tile_id)
        return None
    
    def is_tile_walkable(self, x: int, y: int, layer_name: str = "ground") -> bool:
        """Prüft, ob eine Tile an der Position begehbar ist."""
        tile_id = self.get_tile_at(x, y, layer_name)
        if tile_id > 0:
            return self.render_manager.tile_renderer.is_tile_walkable(tile_id)
        return True  # Leere Tiles sind begehbar
