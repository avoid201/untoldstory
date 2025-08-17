"""
Debug overlay for development and testing.
Shows FPS, position, tile info, and other debug information.
"""

import pygame
import psutil
import time
from typing import TYPE_CHECKING, Optional, List, Dict, Any
from dataclasses import dataclass

from engine.core.config import DebugConfig, Colors, TILE_SIZE

if TYPE_CHECKING:
    from engine.core.game import Game


@dataclass
class PerformanceMetrics:
    """Performance metrics tracking."""
    fps: float = 0.0
    frame_time: float = 0.0
    update_time: float = 0.0
    draw_time: float = 0.0
    memory_usage: float = 0.0
    cpu_usage: float = 0.0
    entity_count: int = 0
    
    # History for graphs
    fps_history: List[float] = None
    memory_history: List[float] = None
    
    def __post_init__(self):
        if self.fps_history is None:
            self.fps_history = [0.0] * 60
        if self.memory_history is None:
            self.memory_history = [0.0] * 60


class DebugOverlay:
    """Debug overlay for showing game information."""
    
    def __init__(self, game: 'Game'):
        """
        Initialize debug overlay.
        
        Args:
            game: Game instance
        """
        self.game = game
        self.enabled = DebugConfig.SHOW_FPS
        self.extended_view = False
        
        # Fonts
        self.font = pygame.font.Font(None, 12)
        self.small_font = pygame.font.Font(None, 10)
        
        # Colors
        self.text_color = Colors.WHITE
        self.bg_color = (0, 0, 0, 180)
        self.grid_color = (50, 50, 50, 100)
        self.collision_color = (255, 0, 0, 100)
        
        # Performance tracking
        self.metrics = PerformanceMetrics()
        self.last_update = time.time()
        self.update_interval = 0.25  # Update 4 times per second
        
        # Grid overlay
        self.show_grid = DebugConfig.SHOW_GRID
        self.show_collision = DebugConfig.SHOW_COLLISION
        self.show_coordinates = DebugConfig.SHOW_COORDINATES
        
        # Process handle for CPU usage
        self.process = psutil.Process()
    
    def toggle(self) -> None:
        """Toggle debug overlay on/off."""
        self.enabled = not self.enabled
    
    def toggle_extended(self) -> None:
        """Toggle extended debug view."""
        self.extended_view = not self.extended_view
    
    def toggle_grid(self) -> None:
        """Toggle grid overlay."""
        self.show_grid = not self.show_grid
    
    def toggle_collision(self) -> None:
        """Toggle collision overlay."""
        self.show_collision = not self.show_collision
    
    def update(self, dt: float) -> None:
        """
        Update debug overlay.
        
        Args:
            dt: Delta time
        """
        if not self.enabled:
            return
        
        # Update metrics periodically
        current_time = time.time()
        if current_time - self.last_update >= self.update_interval:
            self._update_metrics()
            self.last_update = current_time
    
    def _update_metrics(self) -> None:
        """Update performance metrics."""
        # FPS
        if hasattr(self.game, 'clock'):
            self.metrics.fps = self.game.clock.get_fps()
            self.metrics.frame_time = 1000.0 / max(1, self.metrics.fps)
        
        # Memory usage
        memory_info = self.process.memory_info()
        self.metrics.memory_usage = memory_info.rss / 1024 / 1024  # MB
        
        # CPU usage
        try:
            self.metrics.cpu_usage = self.process.cpu_percent(interval=0.1)
        except:
            self.metrics.cpu_usage = 0.0
        
        # Entity count
        if hasattr(self.game, 'current_scene'):
            scene = self.game.current_scene
            if hasattr(scene, 'entities'):
                self.metrics.entity_count = len(scene.entities)
        
        # Update history
        self.metrics.fps_history.append(self.metrics.fps)
        self.metrics.fps_history.pop(0)
        
        self.metrics.memory_history.append(self.metrics.memory_usage)
        self.metrics.memory_history.pop(0)
    
    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw debug overlay.
        
        Args:
            surface: Surface to draw on
        """
        if not self.enabled:
            return
        
        try:
            # Draw grid first (under everything)
            if self.show_grid:
                self._draw_grid(surface)
            
            # Draw collision overlay
            if self.show_collision:
                self._draw_collision(surface)
            
            # Draw debug info panel
            if self.extended_view:
                self._draw_extended_info(surface)
            else:
                self._draw_basic_info(surface)
            
            # Draw coordinates at mouse
            if self.show_coordinates:
                self._draw_mouse_info(surface)
            
            # Draw error overlay if enabled
            if hasattr(self.game, 'error_handler'):
                self.game.error_handler.draw_overlay(surface)
            
        except Exception as e:
            # Minimale Fehleranzeige wenn Debug-Overlay selbst fehlschlägt
            try:
                error_text = f"Debug Overlay Error: {str(e)}"
                error_surf = self.font.render(error_text, True, (255, 0, 0))
                surface.blit(error_surf, (10, 10))
            except:
                pass  # Selbst minimale Fehleranzeige fehlgeschlagen
    
    def _draw_basic_info(self, surface: pygame.Surface) -> None:
        """Draw basic debug information."""
        # Create info lines
        info_lines = [
            f"FPS: {self.metrics.fps:.1f}",
            f"Frame: {self.metrics.frame_time:.1f}ms",
        ]
        
        # Add player position if available
        if hasattr(self.game, 'player'):
            player = self.game.player
            if hasattr(player, 'position'):
                x, y = player.position
                tile_x = int(x // TILE_SIZE)
                tile_y = int(y // TILE_SIZE)
                info_lines.append(f"Pos: ({x:.0f}, {y:.0f})")
                info_lines.append(f"Tile: ({tile_x}, {tile_y})")
        
        # Add current map
        if hasattr(self.game, 'current_map'):
            info_lines.append(f"Map: {self.game.current_map}")
        
        # Background
        padding = 5
        line_height = 12
        width = 100
        height = len(info_lines) * line_height + padding * 2
        
        bg_surf = pygame.Surface((width, height))
        bg_surf.fill((0, 0, 0))
        bg_surf.set_alpha(180)
        surface.blit(bg_surf, (5, 5))
        
        # Draw text
        y = 5 + padding
        for line in info_lines:
            text_surf = self.font.render(line, True, self.text_color)
            surface.blit(text_surf, (5 + padding, y))
            y += line_height
    
    def _draw_extended_info(self, surface: pygame.Surface) -> None:
        """Draw extended debug information."""
        # Left panel - Performance
        self._draw_performance_panel(surface, 5, 5)
        
        # Right panel - Game state
        self._draw_game_state_panel(surface, surface.get_width() - 155, 5)
        
        # Bottom panel - Graphs
        if self.metrics.fps_history:
            self._draw_fps_graph(surface, 5, surface.get_height() - 65)
    
    def _draw_performance_panel(self, surface: pygame.Surface, x: int, y: int) -> None:
        """Draw performance metrics panel."""
        info_lines = [
            "=== PERFORMANCE ===",
            f"FPS: {self.metrics.fps:.1f}",
            f"Frame: {self.metrics.frame_time:.1f}ms",
            f"Update: {self.metrics.update_time:.1f}ms",
            f"Draw: {self.metrics.draw_time:.1f}ms",
            f"Memory: {self.metrics.memory_usage:.1f}MB",
            f"CPU: {self.metrics.cpu_usage:.1f}%",
            f"Entities: {self.metrics.entity_count}",
        ]
        
        # Background
        width = 150
        height = len(info_lines) * 10 + 10
        
        bg_surf = pygame.Surface((width, height))
        bg_surf.fill((0, 0, 0))
        bg_surf.set_alpha(200)
        surface.blit(bg_surf, (x, y))
        
        # Draw text
        y_offset = y + 5
        for line in info_lines:
            color = Colors.YELLOW if "===" in line else self.text_color
            text_surf = self.small_font.render(line, True, color)
            surface.blit(text_surf, (x + 5, y_offset))
            y_offset += 10
    
    def _draw_game_state_panel(self, surface: pygame.Surface, x: int, y: int) -> None:
        """Draw game state panel."""
        info_lines = ["=== GAME STATE ==="]
        
        # Player info
        if hasattr(self.game, 'player'):
            player = self.game.player
            if hasattr(player, 'position'):
                px, py = player.position
                tile_x = int(px // TILE_SIZE)
                tile_y = int(py // TILE_SIZE)
                info_lines.extend([
                    f"Player: ({px:.0f}, {py:.0f})",
                    f"Tile: ({tile_x}, {tile_y})",
                    f"Facing: {getattr(player, 'facing', 'unknown')}",
                ])
        
        # Scene info
        if hasattr(self.game, 'scene_manager'):
            scene_count = len(self.game.scene_manager.scene_stack)
            current_scene = self.game.scene_manager.current_scene
            if current_scene:
                scene_name = current_scene.__class__.__name__
                info_lines.extend([
                    f"Scene: {scene_name}",
                    f"Stack: {scene_count}",
                ])
        
        # Map info
        if hasattr(self.game, 'current_map'):
            info_lines.append(f"Map: {self.game.current_map}")
        
        # Story phase
        if hasattr(self.game, 'story_manager'):
            phase = self.game.story_manager.phase.name
            info_lines.append(f"Phase: {phase}")
        
        # Party info
        if hasattr(self.game, 'party_manager'):
            party_size = len(self.game.party_manager.party.get_all_members())
            info_lines.append(f"Party: {party_size}/6")
        
        # Draw panel
        width = 150
        height = len(info_lines) * 10 + 10
        
        bg_surf = pygame.Surface((width, height))
        bg_surf.fill((0, 0, 0))
        bg_surf.set_alpha(200)
        surface.blit(bg_surf, (x, y))
        
        y_offset = y + 5
        for line in info_lines:
            color = Colors.YELLOW if "===" in line else self.text_color
            text_surf = self.small_font.render(line, True, color)
            surface.blit(text_surf, (x + 5, y_offset))
            y_offset += 10
    
    def _draw_fps_graph(self, surface: pygame.Surface, x: int, y: int) -> None:
        """Draw FPS history graph."""
        width = 120
        height = 60
        
        # Background
        bg_surf = pygame.Surface((width, height))
        bg_surf.fill((0, 0, 0))
        bg_surf.set_alpha(200)
        surface.blit(bg_surf, (x, y))
        
        # Draw border
        pygame.draw.rect(surface, Colors.UI_BORDER, (x, y, width, height), 1)
        
        # Draw title
        title_surf = self.small_font.render("FPS History", True, Colors.YELLOW)
        surface.blit(title_surf, (x + 5, y + 2))
        
        # Draw graph
        if self.metrics.fps_history:
            max_fps = max(self.metrics.fps_history + [60])
            
            points = []
            for i, fps in enumerate(self.metrics.fps_history[-width+10:]):
                px = x + 5 + i
                py = y + height - 5 - int((fps / max_fps) * (height - 20))
                points.append((px, py))
            
            if len(points) > 1:
                pygame.draw.lines(surface, Colors.GREEN, False, points, 1)
            
            # Draw target line (60 FPS)
            target_y = y + height - 5 - int((60 / max_fps) * (height - 20))
            pygame.draw.line(surface, (100, 100, 100), 
                           (x + 5, target_y), (x + width - 5, target_y), 1)
    
    def _draw_grid(self, surface: pygame.Surface) -> None:
        """Draw tile grid overlay."""
        # Get visible area
        if hasattr(self.game, 'camera'):
            camera = self.game.camera
            offset_x = -camera.x % TILE_SIZE
            offset_y = -camera.y % TILE_SIZE
        else:
            offset_x = 0
            offset_y = 0
        
        # Draw vertical lines
        for x in range(0, surface.get_width() + TILE_SIZE, TILE_SIZE):
            pygame.draw.line(surface, self.grid_color,
                           (x + offset_x, 0),
                           (x + offset_x, surface.get_height()), 1)
        
        # Draw horizontal lines
        for y in range(0, surface.get_height() + TILE_SIZE, TILE_SIZE):
            pygame.draw.line(surface, self.grid_color,
                           (0, y + offset_y),
                           (surface.get_width(), y + offset_y), 1)
    
    def _draw_collision(self, surface: pygame.Surface) -> None:
        """Draw collision overlay."""
        if not hasattr(self.game, 'current_scene'):
            return
        
        scene = self.game.current_scene
        if not hasattr(scene, 'area'):
            return
        
        area = scene.area
        if not hasattr(area, 'collision_map'):
            return
        
        # Get camera offset
        if hasattr(self.game, 'camera'):
            cam_x = self.game.camera.x
            cam_y = self.game.camera.y
        else:
            cam_x = cam_y = 0
        
        # Draw collision tiles
        collision_surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
        collision_surf.fill((255, 0, 0))
        collision_surf.set_alpha(100)
        
        for y in range(len(area.collision_map)):
            for x in range(len(area.collision_map[y])):
                if area.collision_map[y][x]:
                    screen_x = x * TILE_SIZE - cam_x
                    screen_y = y * TILE_SIZE - cam_y
                    
                    # Only draw if on screen
                    if -TILE_SIZE < screen_x < surface.get_width() and \
                       -TILE_SIZE < screen_y < surface.get_height():
                        surface.blit(collision_surf, (screen_x, screen_y))
    
    def _draw_mouse_info(self, surface: pygame.Surface) -> None:
        """Draw information at mouse position."""
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # Scale mouse position to logical coordinates
        scale = getattr(self.game, 'scale', 1)
        logical_x = mouse_x // scale
        logical_y = mouse_y // scale
        
        # Calculate tile position
        if hasattr(self.game, 'camera'):
            world_x = logical_x + self.game.camera.x
            world_y = logical_y + self.game.camera.y
        else:
            world_x = logical_x
            world_y = logical_y
        
        tile_x = world_x // TILE_SIZE
        tile_y = world_y // TILE_SIZE
        
        # Create info text
        info_text = f"({tile_x}, {tile_y})"
        text_surf = self.small_font.render(info_text, True, Colors.YELLOW)
        
        # Draw with background
        text_rect = text_surf.get_rect()
        bg_surf = pygame.Surface((text_rect.width + 4, text_rect.height + 2))
        bg_surf.fill((0, 0, 0))
        bg_surf.set_alpha(180)
        
        # Position near mouse
        draw_x = min(logical_x + 10, surface.get_width() - text_rect.width - 10)
        draw_y = min(logical_y + 10, surface.get_height() - text_rect.height - 10)
        
        surface.blit(bg_surf, (draw_x - 2, draw_y - 1))
        surface.blit(text_surf, (draw_x, draw_y))