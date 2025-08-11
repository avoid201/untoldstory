"""Tile rendering system for map display."""
import pygame
from typing import List, Optional, Tuple, Dict, Any
from .sprite_manager import SpriteManager

# Temporärer Import für den Test
try:
    from ..world.camera import Camera
except ImportError:
    # Fallback für Tests
    class Camera:
        def __init__(self):
            self.position = (0, 0)

class TileRenderer:
    """Rendert Tiles aus dem SpriteManager"""
    
    def __init__(self, sprite_manager: SpriteManager):
        """Initialisiert den TileRenderer"""
        self.sprite_manager = sprite_manager
        self.debug_mode = False
        # Hole die Tile-Größe vom SpriteManager
        self.tile_size = sprite_manager.tile_size
    
    def render_layer(self, screen: pygame.Surface, layer_data: List[List[int]], 
                    camera_offset: Tuple[int, int], layer_name: str = "default") -> None:
        """Rendert eine Map-Layer mit dem neuen Sprite-System"""
        if not layer_data:
            return
            
        # Hole die Kamera-Position
        camera_x, camera_y = camera_offset
        
        # Berechne die sichtbaren Tile-Bereiche
        start_tile_x = max(0, int(camera_x // self.tile_size))
        start_tile_y = max(0, int(camera_y // self.tile_size))
        end_tile_x = min(len(layer_data[0]), start_tile_x + (screen.get_width() // self.tile_size) + 2)
        end_tile_y = min(len(layer_data), start_tile_y + (screen.get_height() // self.tile_size) + 2)
        
        # Rendere nur sichtbare Tiles
        for y in range(start_tile_y, end_tile_y):
            for x in range(start_tile_x, end_tile_x):
                tile_id = layer_data[y][x]
                
                # Überspringe leere Tiles
                if tile_id <= 0:
                    continue
                
                # Berechne die Bildschirm-Position
                screen_x = x * self.tile_size - int(camera_x)
                screen_y = y * self.tile_size - int(camera_y)
                
                # Hole den Sprite für diese Tile-ID
                tile_sprite = self.sprite_manager.get_tile_sprite(tile_id)
                
                if tile_sprite:
                    # Zeichne den Tile-Sprite
                    screen.blit(tile_sprite, (screen_x, screen_y))
                else:
                    # Erstelle einen Platzhalter für fehlende Tiles
                    placeholder = self._create_placeholder_tile(tile_id)
                    if placeholder:
                        screen.blit(placeholder, (screen_x, screen_y))
                        print(f"⚠️  Platzhalter für Tile-ID {tile_id} erstellt")
    
    def _create_placeholder_tile(self, tile_id: int) -> Optional[pygame.Surface]:
        """Erstellt einen Platzhalter-Tile für fehlende Sprites"""
        try:
            placeholder = pygame.Surface((self.tile_size, self.tile_size))
            placeholder.fill((255, 0, 255))  # Magenta für fehlende Tiles
            
            # Zeichne einen schwarzen Rahmen
            pygame.draw.rect(placeholder, (0, 0, 0), 
                           (0, 0, self.tile_size, self.tile_size), 2)
            
            # Zeichne die Tile-ID als Text
            try:
                font = pygame.font.Font(None, 20)
                text = font.render(str(tile_id), True, (255, 255, 255))
                text_rect = text.get_rect(center=(self.tile_size // 2, self.tile_size // 2))
                placeholder.blit(text, text_rect)
            except:
                pass  # Ignoriere Font-Fehler
                
            return placeholder
        except Exception as e:
            print(f"❌ Fehler beim Erstellen des Platzhalter-Tiles: {e}")
            return None
    
    def set_debug(self, enabled: bool) -> None:
        """Aktiviert oder deaktiviert den Debug-Modus"""
        self.debug_mode = enabled
        if enabled:
            print(f"🔧 TileRenderer Debug-Modus: aktiviert")
    
    def set_debug_mode(self, enabled: bool) -> None:
        """Alias für set_debug für Kompatibilität"""
        self.set_debug(enabled)
    
    def _render_debug_info(self, screen: pygame.Surface, layer_name: str, 
                           start_col: int, start_row: int, end_col: int, end_row: int) -> None:
        """Rendert Debug-Informationen über die Layer"""
        if not self.debug_mode:
            return
            
        # Zeichne Debug-Info
        font = pygame.font.Font(None, 24)
        
        # Layer-Informationen
        info_text = f"Layer: {layer_name}"
        text_surface = font.render(info_text, True, (255, 255, 0))
        screen.blit(text_surface, (10, 10))
        
        # Sichtbarer Bereich
        area_text = f"Bereich: ({start_col},{start_row}) - ({end_col},{end_row})"
        text_surface = font.render(area_text, True, (255, 255, 0))
        screen.blit(text_surface, (10, 35))
        
        # Cache-Status
        cache_info = self.sprite_manager.get_cache_info()
        cache_text = f"Cache: {cache_info['total_sprites']} Sprites"
        text_surface = font.render(cache_text, True, (255, 255, 0))
        screen.blit(text_surface, (10, 60))
    
    def get_tile_at_position(self, world_x: int, world_y: int, 
                            layer_data: List[List[int]]) -> Optional[int]:
        """Ermittelt die Tile-ID an einer bestimmten Welt-Position"""
        if not layer_data:
            return None
            
        # Berechne die Grid-Position
        grid_x = int(world_x // self.sprite_manager.tile_size)
        grid_y = int(world_y // self.sprite_manager.tile_size)
        
        # Prüfe Grenzen
        if (0 <= grid_y < len(layer_data) and 
            0 <= grid_x < len(layer_data[grid_y])):
            return layer_data[grid_y][grid_x]
            
        return None
    
    def is_tile_walkable(self, tile_id: int) -> bool:
        """Prüft, ob eine Tile begehbar ist"""
        tile_info = self.sprite_manager.get_tile_info(tile_id)
        if tile_info:
            category = tile_info.category
            # Bestimmte Kategorien sind nicht begehbar
            non_walkable = ["furniture", "electronics", "decoration", "landscape", "water"]
            return category not in non_walkable
        
        # Standard: begehbar
        return True
    
    def get_missing_tiles(self) -> set:
        """Gibt alle fehlenden Tile-IDs zurück"""
        return self.missing_tiles.copy()
    
    def clear_missing_tiles(self) -> None:
        """Löscht die Liste der fehlenden Tiles"""
        self.missing_tiles.clear()

    def render_map(self, screen: pygame.Surface, map_data: Dict[str, Any], 
                   camera_offset: Tuple[int, int]) -> None:
        """Rendert eine komplette Map mit allen Layern"""
        if not map_data or "layers" not in map_data:
            return
            
        layers = map_data["layers"]
        
        # Rendere Layer in der richtigen Reihenfolge (Hintergrund zu Vordergrund)
        for layer_name, layer_data in layers.items():
            if isinstance(layer_data, list) and layer_data:
                self.render_layer(screen, layer_data, camera_offset, layer_name)
        
        # Rendere zusätzliche Möbel- und Dekorations-Layer
        self._render_furniture_placement(screen, map_data, camera_offset)
        self._render_decoration(screen, map_data, camera_offset)
                
        # Debug-Info anzeigen (falls aktiviert)
        if self.debug_mode:
            # Zeige Debug-Info für den ersten Layer
            first_layer = next(iter(layers.values()), [])
            if first_layer:
                start_col = max(0, int(camera_offset[0] // self.sprite_manager.tile_size))
                end_col = min(len(first_layer[0]), int((camera_offset[0] + screen.get_width()) // self.sprite_manager.tile_size) + 1)
                start_row = max(0, int(camera_offset[1] // self.sprite_manager.tile_size))
                end_row = min(len(first_layer), int((camera_offset[1] + screen.get_height()) // self.sprite_manager.tile_size) + 1)
                
                self._render_debug_info(screen, "Map", start_col, start_row, end_col, end_row)
    
    def _render_furniture_placement(self, screen: pygame.Surface, map_data: Dict[str, Any], 
                                   camera_offset: Tuple[int, int]) -> None:
        """Rendert Möbel-Platzierungen aus dem furniture_placement Array"""
        if "furniture_placement" not in map_data:
            return
            
        furniture_data = map_data["furniture_placement"]
        if not furniture_data:
            return
            
        tile_size = self.sprite_manager.tile_size
        camera_x, camera_y = camera_offset
        screen_width, screen_height = screen.get_size()
        
        for furniture in furniture_data:
            if not isinstance(furniture, dict):
                continue
                
            x = furniture.get("x", 0)
            y = furniture.get("y", 0)
            tile_id = furniture.get("tile_id", 0)
            
            if tile_id == 0:
                continue
                
            # Berechne die Welt-Position
            world_x = x * tile_size
            world_y = y * tile_size
            
            # Prüfe, ob das Möbel im sichtbaren Bereich liegt
            if (world_x < camera_x - tile_size or world_x > camera_x + screen_width + tile_size or
                world_y < camera_y - tile_size or world_y > camera_y + screen_height + tile_size):
                continue
                
            # Berechne die Bildschirm-Position
            screen_x = int(world_x - camera_x)
            screen_y = int(world_y - camera_y)
            
            # Hole den Sprite für diese Tile-ID
            sprite = self.sprite_manager.get_tile_sprite(tile_id)
            
            if sprite:
                # Zeichne den Sprite
                screen.blit(sprite, (screen_x, screen_y))
            else:
                # Fallback: Zeichne einen Platzhalter
                self._draw_placeholder_tile(screen, screen_x, screen_y, tile_size, tile_id)
    
    def _render_decoration(self, screen: pygame.Surface, map_data: Dict[str, Any], 
                          camera_offset: Tuple[int, int]) -> None:
        """Rendert Dekorationen aus dem decoration Array"""
        if "decoration" not in map_data:
            return
            
        decoration_data = map_data["decoration"]
        if not decoration_data:
            return
            
        tile_size = self.sprite_manager.tile_size
        camera_x, camera_y = camera_offset
        screen_width, screen_height = screen.get_size()
        
        for decoration in decoration_data:
            if not isinstance(decoration, dict):
                continue
                
            x = decoration.get("x", 0)
            y = decoration.get("y", 0)
            tile_id = decoration.get("tile_id", 0)
            
            if tile_id == 0:
                continue
                
            # Berechne die Welt-Position
            world_x = x * tile_size
            world_y = y * tile_size
            
            # Prüfe, ob die Dekoration im sichtbaren Bereich liegt
            if (world_x < camera_x - tile_size or world_x > camera_x + screen_width + tile_size or
                world_y < camera_y - tile_size or world_y > camera_y + screen_height + tile_size):
                continue
                
            # Berechne die Bildschirm-Position
            screen_x = int(world_x - camera_x)
            screen_y = int(world_y - camera_y)
            
            # Hole den Sprite für diese Tile-ID
            sprite = self.sprite_manager.get_tile_sprite(tile_id)
            
            if sprite:
                # Zeichne den Sprite
                screen.blit(sprite, (screen_x, screen_y))
            else:
                # Fallback: Zeichne einen Platzhalter
                self._draw_placeholder_tile(screen, screen_x, screen_y, tile_size, tile_id)
