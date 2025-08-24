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
                tile_sprite = self._get_tile_sprite(tile_data)
                
                if tile_sprite:
                    # Zeichne den Tile-Sprite
                    screen.blit(tile_sprite, (screen_x, screen_y))
                else:
                    # Erstelle einen Platzhalter für fehlende Tiles
                    placeholder = self._create_placeholder_tile(tile_data)
                    if placeholder:
                        screen.blit(placeholder, (screen_x, screen_y))
                        # Log nur einmal pro Tile-ID
                        if tile_data not in self.missing_tiles:
                            print(f"⚠️  Platzhalter für Tile {tile_data} erstellt")
                            self.missing_tiles.add(tile_data)
        
        # Debug-Informationen rendern
        if self.debug_mode:
            self._render_debug_info(screen, layer_name, start_tile_x, start_tile_y, end_tile_x, end_tile_y)

    def _get_tile_sprite(self, tile_data: Any) -> Optional[pygame.Surface]:
        """
        Holt einen Tile-Sprite basierend auf den verfügbaren Daten.
        
        Unterstützt:
        - int: GID aus JSON-Maps (neue Struktur)
        - str: Tile-Name (direkter Zugriff)
        - Mapping über tile_mapping.json
        """
        if tile_data is None or tile_data == 0:
            return None
        
        # Versuche zuerst den Sprite direkt zu holen
        tile_sprite = self.sprite_manager.get_tile_sprite(tile_data)
        if tile_sprite is not None:
            return tile_sprite
        
        # Falls es eine numerische ID ist, versuche das Mapping
        if isinstance(tile_data, int) and tile_data > 0:
            # Versuche über das Tile-Mapping
            tile_sprite = self.sprite_manager.get_tile_by_mapping(str(tile_data))
            if tile_sprite is not None:
                return tile_sprite
            
            # Fallback: Versuche GID-basiertes Loading
            tile_sprite = self.sprite_manager.get_tile_by_gid(tile_data)
            if tile_sprite is not None:
                return tile_sprite
        
        # Falls es ein String ist, versuche verschiedene Varianten
        if isinstance(tile_data, str):
            # Versuche verschiedene Schreibweisen
            variations = [
                tile_data.lower(),
                tile_data.replace("_", ""),
                tile_data.split("_")[0] if "_" in tile_data else tile_data
            ]
            
            for variation in variations:
                tile_sprite = self.sprite_manager.get_tile(variation)
                if tile_sprite is not None:
                    return tile_sprite
        
        return None

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
                    # Für numerische IDs: Zeige die ID
                    display_text = str(tile_data)[:3]
                
                text_surface = font.render(display_text, True, (0, 0, 0))
                text_rect = text_surface.get_rect(center=(self.tile_size // 2, self.tile_size // 2))
                placeholder.blit(text_surface, text_rect)
                
            except Exception as e:
                # Falls Text-Rendering fehlschlägt, zeichne ein X
                pygame.draw.line(placeholder, (0, 0, 0), (2, 2), (self.tile_size - 2, self.tile_size - 2), 2)
                pygame.draw.line(placeholder, (0, 0, 0), (self.tile_size - 2, 2), (2, self.tile_size - 2), 2)
            
            return placeholder
            
        except Exception as e:
            print(f"Fehler beim Erstellen des Platzhalter-Tiles: {e}")
            return None

    def _is_empty_tile(self, tile_data: Any) -> bool:
        """Prüft, ob ein Tile leer ist (nicht gerendert werden soll)"""
        if tile_data is None:
            return True
        if tile_data == 0:
            return True
        if isinstance(tile_data, str) and tile_data.lower() in ["", "empty", "none"]:
            return True
        return False

    def _render_debug_info(self, screen: pygame.Surface, layer_name: str, 
                          start_x: int, start_y: int, end_x: int, end_y: int) -> None:
        """Rendert Debug-Informationen über den sichtbaren Bereich"""
        try:
            font = pygame.font.Font(None, 24)
            
            # Debug-Text
            debug_text = [
                f"Layer: {layer_name}",
                f"Visible: ({start_x},{start_y}) to ({end_x},{end_y})",
                f"Tiles: {len(range(start_x, end_x))}x{len(range(start_y, end_y))}"
            ]
            
            y_offset = 10
            for text in debug_text:
                text_surface = font.render(text, True, (255, 255, 255))
                screen.blit(text_surface, (10, y_offset))
                y_offset += 25
                
        except Exception as e:
            # Ignoriere Font-Fehler
            pass

    def set_debug_mode(self, enabled: bool) -> None:
        """Aktiviert/Deaktiviert den Debug-Modus"""
        self.debug_mode = enabled

    def clear_missing_tiles_cache(self) -> None:
        """Löscht den Cache der fehlenden Tiles"""
        self.missing_tiles.clear()
