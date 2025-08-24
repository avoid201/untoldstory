"""
Debug Overlay Manager für Untold Story
Verwaltet Debug-Informationen und Overlay-Rendering
"""

import pygame
from typing import Optional, List, Dict, Any
from dataclasses import dataclass


@dataclass
class DebugInfo:
    """Debug-Informationen für das Overlay"""
    scene_name: str
    stack_size: int
    total_time: float
    frame_count: int
    mouse_pos: tuple[int, int]
    pressed_keys: List[str]
    movement_vector: tuple[int, int]
    input_debug_status: str
    fps: float


class DebugOverlayManager:
    """Verwaltet Debug-Overlay und -Informationen"""
    
    def __init__(self, game: 'Game'):
        self.game = game
        self.font: Optional[pygame.font.Font] = None
        self._init_font()
    
    def _init_font(self) -> None:
        """Initialisiert die Debug-Font"""
        try:
            self.font = pygame.font.Font(None, 16)
        except Exception:
            print("Warning: Could not load debug font")
    
    def draw_debug_overlay(self, surface: pygame.Surface) -> None:
        """Zeichnet das Debug-Overlay"""
        if not self.game.debug_overlay_enabled or not self.font:
            return
        
        # Debug-Informationen sammeln
        debug_info = self._collect_debug_info()
        
        # Debug-Text zeichnen
        self._draw_debug_text(surface, debug_info)
        
        # Input-Debug Hotkey-Hilfe
        if hasattr(self.game, 'input_manager') and self.game.input_manager.debug_enabled:
            self._draw_debug_help(surface)
        
        # Grid zeichnen wenn aktiviert
        if self.game.show_grid:
            self._draw_grid(surface)
    
    def _collect_debug_info(self) -> DebugInfo:
        """Sammelt Debug-Informationen"""
        # Aktuelle gedrückte Tasten
        pressed_keys = []
        if hasattr(self.game, 'input_manager'):
            pressed_keys = [k for k, v in self.game.keys_pressed.items() if v]
            if pressed_keys:
                key_names = []
                for key in pressed_keys[:5]:  # Maximal 5 Tasten anzeigen
                    if hasattr(self.game.input_manager, '_get_key_name'):
                        key_names.append(self.game.input_manager._get_key_name(key))
                    else:
                        key_names.append(f"KEY_{key}")
                pressed_keys = key_names
        
        # Movement Vector
        movement = (0, 0)
        if hasattr(self.game, 'input_manager') and hasattr(self.game.input_manager, 'get_movement_vector'):
            movement = self.game.input_manager.get_movement_vector()
        
        # Input-Debug Status
        input_debug_status = "OFF"
        if hasattr(self.game, 'input_manager') and hasattr(self.game.input_manager, 'debug_enabled'):
            input_debug_status = "ON" if self.game.input_manager.debug_enabled else "OFF"
        
        return DebugInfo(
            scene_name=self.game.scene_stack[-1].__class__.__name__ if self.game.scene_stack else "None",
            stack_size=len(self.game.scene_stack),
            total_time=self.game.total_time,
            frame_count=self.game.frame_count,
            mouse_pos=self.game.mouse_pos,
            pressed_keys=pressed_keys,
            movement_vector=movement,
            input_debug_status=input_debug_status,
            fps=self.game.clock.get_fps()
        )
    
    def _draw_debug_text(self, surface: pygame.Surface, info: DebugInfo) -> None:
        """Zeichnet Debug-Text"""
        debug_lines = [
            f"Scene: {info.scene_name}",
            f"Stack: {info.stack_size}",
            f"Time: {info.total_time:.1f}s",
            f"Frame: {info.frame_count}",
            f"Mouse: {info.mouse_pos}",
        ]
        
        # Gedrückte Tasten hinzufügen
        if info.pressed_keys:
            debug_lines.append(f"Pressed: {', '.join(info.pressed_keys)}")
        
        # Movement Vector hinzufügen
        if info.movement_vector != (0, 0):
            debug_lines.append(f"Movement: {info.movement_vector}")
        
        # Input-Debug Status hinzufügen
        debug_lines.append(f"Input Debug: {info.input_debug_status}")
        
        # Debug-Text zeichnen
        y = 20
        for line in debug_lines:
            text_surface = self.font.render(line, True, (0, 255, 0))
            surface.blit(text_surface, (2, y))
            y += 12
    
    def _draw_debug_help(self, surface: pygame.Surface) -> None:
        """Zeichnet Debug-Hilfe"""
        help_lines = [
            "F1: Input-Log Summary",
            "F2: Clear Input-Log", 
            "F3: Toggle Input-Debug",
            "F4: Current Input-Status"
        ]
        
        # Erweiterte Debug-Funktionen hinzufügen
        if hasattr(self.game, 'input_debugger') and self.game.input_debugger:
            help_lines.extend([
                "F5: Export Input-Analysis",
                "F6: Find Unhandled Inputs",
                "F7: Find Performance Issues"
            ])
        
        # Hilfe am unteren Bildschirmrand zeichnen
        y_help = self.game.logical_size[1] - 60
        for help_line in help_lines:
            text_surface = self.font.render(help_line, True, (255, 255, 0))
            surface.blit(text_surface, (2, y_help))
            y_help += 12
    
    def _draw_grid(self, surface: pygame.Surface) -> None:
        """Zeichnet ein Tile-Grid-Overlay"""
        from engine.world.tiles import TILE_SIZE
        color = (255, 255, 255, 64)  # Semi-transparent white
        
        # Vertikale Linien
        for x in range(0, self.game.logical_size[0] + 1, TILE_SIZE):
            pygame.draw.line(surface, color, 
                           (x, 0), (x, self.game.logical_size[1]), 1)
        
        # Horizontale Linien
        for y in range(0, self.game.logical_size[1] + 1, TILE_SIZE):
            pygame.draw.line(surface, color,
                           (0, y), (self.game.logical_size[0], y), 1)
    
    def draw_fps_counter(self, surface: pygame.Surface) -> None:
        """Zeichnet FPS-Zähler"""
        if not self.game.show_fps or not self.font:
            return
        
        fps_text = f"FPS: {self.game.clock.get_fps():.1f}"
        fps_surface = self.font.render(fps_text, True, (255, 255, 0))
        surface.blit(fps_surface, (2, 2))
