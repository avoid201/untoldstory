"""Tile rendering system for map display."""
import pygame
from typing import List, Optional, Tuple, Dict, Any
from .sprite_manager import SpriteManager
from ..world.tiles import TILE_SIZE

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
        # Verwende die einheitliche TILE_SIZE
        self.tile_size = TILE_SIZE
        # Set zum Nachverfolgen fehlender Tiles, um doppelte Log-Ausgaben zu vermeiden
        self.missing_tiles: set[int] = set()
    
    def render_layer(self, screen: pygame.Surface, layer_data: List[List], 
                     camera_offset: Tuple[int, int], layer_name: str = "unknown") -> None:
        """
        Rendert eine Tile-Layer mit Kamera-Offset.
        
        Args:
            screen: Pygame-Surface zum Rendern
            layer_data: 2D-Array mit Tile-IDs oder Tile-Namen
            camera_offset: Kamera-Offset (x, y)
            layer_name: Name des Layers für Debug-Zwecke
        """
        if not layer_data or not layer_data[0]:
            return
        
        camera_x, camera_y = camera_offset
        
        # Berechne den sichtbaren Bereich
        start_tile_x = max(0, int(camera_x // self.tile_size))
        start_tile_y = max(0, int(camera_y // self.tile_size))
        end_tile_x = min(len(layer_data[0]), start_tile_x + (screen.get_width() // self.tile_size) + 2)
        end_tile_y = min(len(layer_data), start_tile_y + (screen.get_height() // self.tile_size) + 2)
        
        # Rendere nur sichtbare Tiles
        for y in range(start_tile_y, end_tile_y):
            for x in range(start_tile_x, end_tile_x):
                tile_data = layer_data[y][x]
                
                # Überspringe leere Tiles (0 oder "grass" für leere Bereiche)
                if self._is_empty_tile(tile_data):
                    continue
                
                # Berechne die Bildschirm-Position
                screen_x = x * self.tile_size - int(camera_x)
                screen_y = y * self.tile_size - int(camera_y)
                
                # Hole den Sprite für diese Tile-ID oder Tile-Name
                # Versuche zuerst GID-basiertes Loading für TMX-Maps
                if isinstance(tile_data, int) and tile_data > 0:
                    tile_sprite = self.sprite_manager.get_tile_by_gid(tile_data)
                else:
                    tile_sprite = self.sprite_manager.get_tile_sprite(tile_data)
                
                if tile_sprite:
                    # Zeichne den Tile-Sprite
                    screen.blit(tile_sprite, (screen_x, screen_y))
                else:
                    # Erstelle einen Platzhalter für fehlende Tiles
                    placeholder = self._create_placeholder_tile(tile_data)
                    if placeholder:
                        screen.blit(placeholder, (screen_x, screen_y))
                        print(f"⚠️  Platzhalter für Tile {tile_data} erstellt")
        
        # Debug-Informationen rendern
        if self.debug_mode:
            self._render_debug_info(screen, layer_name, start_tile_x, start_tile_y, end_tile_x, end_tile_y)

    def _create_placeholder_tile(self, tile_data) -> Optional[pygame.Surface]:
        """Erstellt einen Platzhalter-Tile für fehlende Sprites"""
        try:
            placeholder = pygame.Surface((self.tile_size, self.tile_size))
            placeholder.fill((255, 0, 255))  # Magenta für fehlende Tiles
            
            # Zeichne einen schwarzen Rahmen
            pygame.draw.rect(placeholder, (0, 0, 0), 
                           (0, 0, self.tile_size, self.tile_size), 2)
            
            # Zeichne die Tile-ID oder den Tile-Namen als Text
            try:
                font = pygame.font.Font(None, 20)
                if isinstance(tile_data, str):
                    # Für Tile-Namen: Zeige den ersten Buchstaben
                    display_text = tile_data[:3] if len(tile_data) > 3 else tile_data
                else:
                    # Für Tile-IDs: Zeige die ID
                    display_text = str(tile_data)
                
                text = font.render(display_text, True, (255, 255, 255))
                text_rect = text.get_rect(center=(self.tile_size // 2, self.tile_size // 2))
                placeholder.blit(text, text_rect)
            except:
                pass  # Ignoriere Font-Fehler

            # Tile-ID oder Tile-Name im Set der fehlenden Tiles vermerken
            self.missing_tiles.add(tile_data)
            
            return placeholder
        except Exception as e:
            print(f"❌ Fehler beim Erstellen des Platzhalter-Tiles: {e}")
            return None

    def _draw_placeholder_tile(self, screen: pygame.Surface, x: int, y: int, size: int, tile_id: int) -> None:
        """Zeichnet einen Platzhalter direkt auf den Screen (für Möbel/Dekoration)."""
        placeholder = self._create_placeholder_tile(tile_id)
        if placeholder:
            screen.blit(placeholder, (x, y))
    
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
        grid_x = int(world_x // self.tile_size)
        grid_y = int(world_y // self.tile_size)
        
        # Prüfe Grenzen
        if (0 <= grid_y < len(layer_data) and 
            0 <= grid_x < len(layer_data[grid_y])):
            return layer_data[grid_y][grid_x]
            
        return None
    
    def is_tile_walkable(self, tile_id: int) -> bool:
        """Prüft, ob eine Tile begehbar ist.

        Bevorzugt das Feld 'walkable' aus dem Tile-Mapping. Falls nicht vorhanden,
        nutzt eine Kategorie-Heuristik als Fallback.
        """
        tile_info = self.sprite_manager.get_tile_info(tile_id)
        if tile_info:
            # Mapping kann ein Dict sein
            walkable = tile_info.get("walkable") if isinstance(tile_info, dict) else None
            if isinstance(walkable, bool):
                return walkable
            # Fallback: Kategorie-basierte Heuristik
            category = tile_info.get("category") if isinstance(tile_info, dict) else None
            non_walkable = {"furniture", "electronics", "decoration", "landscape", "water", "void"}
            return category not in non_walkable if category is not None else True

        # Standard-Fallback
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
                start_col = max(0, int(camera_offset[0] // self.tile_size))
                end_col = min(len(first_layer[0]), int((camera_offset[0] + screen.get_width()) // self.tile_size) + 1)
                start_row = max(0, int(camera_offset[1] // self.tile_size))
                end_row = min(len(first_layer), int((camera_offset[1] + screen.get_height()) // self.tile_size) + 1)
                
                self._render_debug_info(screen, "Map", start_col, start_row, end_col, end_row)
    
    def _render_furniture_placement(self, screen: pygame.Surface, map_data: Dict[str, Any], 
                                   camera_offset: Tuple[int, int]) -> None:
        """Rendert Möbel-Platzierungen aus dem furniture_placement Array"""
        if "furniture_placement" not in map_data:
            return
            
        furniture_data = map_data["furniture_placement"]
        if not furniture_data:
            return
            
        tile_size = self.tile_size
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
            
        tile_size = self.tile_size
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

    def _is_empty_tile(self, tile_data) -> bool:
        """
        Prüft, ob ein Tile als leer betrachtet werden soll.
        
        Args:
            tile_data: Tile-ID (int) oder Tile-Name (str)
            
        Returns:
            True wenn das Tile leer ist
        """
        if isinstance(tile_data, int):
            return tile_data <= 0
        elif isinstance(tile_data, str):
            # Leere Tiles sind "grass" oder leere Strings
            return not tile_data or tile_data.lower() in ['grass', 'empty', '']
        else:
            return False
