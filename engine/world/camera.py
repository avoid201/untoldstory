"""
Camera System for Untold Story
Handles viewport management, following targets, and smooth camera movement
"""

import pygame
from typing import Optional, Tuple
from dataclasses import dataclass
from ..core.config import CAMERA_DEADZONE_WIDTH, CAMERA_DEADZONE_HEIGHT, CAMERA_FOLLOW_SPEED


@dataclass
class CameraConfig:
    """Configuration for camera behavior."""
    smooth_follow: bool = True
    follow_speed: float = CAMERA_FOLLOW_SPEED  # Verwende Konstante aus config
    deadzone_width: int = CAMERA_DEADZONE_WIDTH  # Verwende Konstante aus config
    deadzone_height: int = CAMERA_DEADZONE_HEIGHT  # Verwende Konstante aus config
    shake_enabled: bool = True
    edge_buffer: int = 0  # Pixels to keep from map edge


class Camera:
    """
    2D camera for following entities and managing the viewport.
    """
    
    def __init__(self, 
                 viewport_width: int,
                 viewport_height: int,
                 world_width: int,
                 world_height: int,
                 config: Optional[CameraConfig] = None) -> None:
        """
        Initialize the camera.
        
        Args:
            viewport_width: Width of the viewport in pixels
            viewport_height: Height of the viewport in pixels
            world_width: Total world width in pixels
            world_height: Total world height in pixels
            config: Optional camera configuration
        """
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height
        self.world_width = world_width
        self.world_height = world_height
        
        # Camera position (top-left corner of viewport)
        self.x: float = 0.0
        self.y: float = 0.0
        
        # Target position for smooth following
        self.target_x: float = 0.0
        self.target_y: float = 0.0
        
        # Configuration
        self.config = config or CameraConfig()
        
        # Deadzone rectangle (relative to viewport)
        self._update_deadzone()
        
        # Camera shake
        self.shake_intensity: float = 0.0
        self.shake_duration: float = 0.0
        self.shake_offset_x: float = 0.0
        self.shake_offset_y: float = 0.0
        
        # Follow target
        self.follow_target: Optional[pygame.Rect] = None
        self.follow_entity = None  # NEU: Entity-Referenz
        self.follow_rect = None    # Fallback für Rect
        self.follow_offset_x: int = 0
        self.follow_offset_y: int = 0
        
        # Konfiguration wird jetzt über CameraConfig gehandhabt
    
    def _update_deadzone(self) -> None:
        """Update the deadzone rectangle based on current config."""
        center_x = self.viewport_width // 2
        center_y = self.viewport_height // 2
        
        self.deadzone = pygame.Rect(
            center_x - self.config.deadzone_width // 2,
            center_y - self.config.deadzone_height // 2,
            self.config.deadzone_width,
            self.config.deadzone_height
        )
    
    def set_position(self, x: float, y: float) -> None:
        """
        Set the camera position directly.
        
        Args:
            x: X position in world coordinates
            y: Y position in world coordinates
        """
        self.x = x
        self.y = y
        self.target_x = x
        self.target_y = y
        self._clamp_to_world()
    
    def center_on(self, x: float, y: float, immediate: bool = True) -> None:
        """Zentriert die Kamera auf eine Position"""
        target_x = x - self.viewport_width // 2
        target_y = y - self.viewport_height // 2
        
        if immediate:
            self.x = target_x
            self.y = target_y
        else:
            # Nutze smooth follow für sanften Übergang
            self.x += (target_x - self.x) * self.smooth_speed
            self.y += (target_y - self.y) * self.smooth_speed
            
        self._clamp_to_world()
    
    def set_follow_target(self, target):
        """Setzt das Ziel, dem die Kamera folgen soll"""
        # Prüfe ob Entity oder Rect übergeben wurde
        if hasattr(target, 'x') and hasattr(target, 'y'):
            # Es ist eine Entity
            self.follow_entity = target
            self.follow_rect = None
        else:
            # Es ist ein Rect
            self.follow_rect = target
            self.follow_entity = None
            
        # Setze Offset
        self.follow_offset_x = 0
        self.follow_offset_y = 0
    
    def update(self, dt: float) -> None:
        """
        Update camera position and effects.
        
        Args:
            dt: Delta time in seconds
        """
        # Update follow target
        if self.follow_entity or self.follow_rect:
            self._update_follow(dt)
        
        # Update camera shake
        if self.shake_duration > 0:
            self._update_shake(dt)
        
        # Clamp to world bounds
        self._clamp_to_world()
    
    def _update_follow(self, dt: float) -> None:
        """Folgt dem gesetzten Ziel"""
        # Hole aktuelle Zielposition
        if self.follow_entity:
            # Verwende Entity-Position (immer aktuell)
            target_x = self.follow_entity.x + self.follow_entity.width // 2
            target_y = self.follow_entity.y + self.follow_entity.height // 2
        elif self.follow_rect:
            # Verwende Rect-Position (statisch)
            target_x = self.follow_rect.centerx
            target_y = self.follow_rect.centery
        else:
            return
            
        # Berechne Ziel-Kameraposition (zentriert auf Target)
        target_cam_x = target_x - self.viewport_width // 2 + self.follow_offset_x
        target_cam_y = target_y - self.viewport_height // 2 + self.follow_offset_y
        
        if self.config.smooth_follow:
            # Sanftes Nachziehen mit konfigurierbarer Geschwindigkeit
            self.x += (target_cam_x - self.x) * (self.config.follow_speed / 60.0)  # 60 FPS als Basis
            self.y += (target_cam_y - self.y) * (self.config.follow_speed / 60.0)  # 60 FPS als Basis
        else:
            # Direktes Setzen
            self.x = target_cam_x
            self.y = target_cam_y
    
    def _update_shake(self, dt: float) -> None:
        """
        Update camera shake effect.
        
        Args:
            dt: Delta time in seconds
        """
        import random
        
        self.shake_duration -= dt
        if self.shake_duration <= 0:
            self.shake_duration = 0
            self.shake_intensity = 0
            self.shake_offset_x = 0
            self.shake_offset_y = 0
        else:
            # Random shake offset
            self.shake_offset_x = random.uniform(-1, 1) * self.shake_intensity
            self.shake_offset_y = random.uniform(-1, 1) * self.shake_intensity
            
            # Decay intensity
            self.shake_intensity *= 0.9
    
    def _clamp_to_world(self) -> None:
        """Verhindert, dass die Kamera über Weltgrenzen hinausgeht"""
        self.x = max(0, min(self.x, self.world_width - self.viewport_width))
        self.y = max(0, min(self.y, self.world_height - self.viewport_height))
    
    def start_shake(self, intensity: float, duration: float) -> None:
        """
        Start a camera shake effect.
        
        Args:
            intensity: Shake intensity in pixels
            duration: Shake duration in seconds
        """
        if self.config.shake_enabled:
            self.shake_intensity = intensity
            self.shake_duration = duration
    
    def get_offset(self) -> Tuple[float, float]:
        """
        Get the current camera offset for rendering.
        
        Returns:
            Tuple of (x_offset, y_offset) including shake
        """
        offset_x = -self.x + self.shake_offset_x
        offset_y = -self.y + self.shake_offset_y
        return (offset_x, offset_y)
    
    def get_position(self) -> Tuple[float, float]:
        """
        Get the current camera position.
        
        Returns:
            Tuple of (x, y) in world coordinates
        """
        return (self.x, self.y)
    
    def screen_to_world(self, screen_x: float, screen_y: float) -> Tuple[float, float]:
        """
        Convert screen coordinates to world coordinates.
        
        Args:
            screen_x: X position on screen
            screen_y: Y position on screen
            
        Returns:
            Tuple of (world_x, world_y)
        """
        world_x = screen_x + self.x - self.shake_offset_x
        world_y = screen_y + self.y - self.shake_offset_y
        return (world_x, world_y)
    
    def world_to_screen(self, world_x: float, world_y: float) -> Tuple[float, float]:
        """
        Convert world coordinates to screen coordinates.
        
        Args:
            world_x: X position in world
            world_y: Y position in world
            
        Returns:
            Tuple of (screen_x, screen_y)
        """
        screen_x = world_x - self.x + self.shake_offset_x
        screen_y = world_y - self.y + self.shake_offset_y
        return (screen_x, screen_y)
    
    def is_visible(self, rect: pygame.Rect, margin: int = 0) -> bool:
        """
        Check if a rectangle is visible in the viewport.
        
        Args:
            rect: Rectangle in world coordinates
            margin: Extra margin around viewport
            
        Returns:
            True if the rectangle is at least partially visible
        """
        viewport = pygame.Rect(
            self.x - margin,
            self.y - margin,
            self.viewport_width + margin * 2,
            self.viewport_height + margin * 2
        )
        return viewport.colliderect(rect)
    
    def get_visible_area(self, margin: int = 0) -> pygame.Rect:
        """
        Get the visible area rectangle in world coordinates.
        
        Args:
            margin: Extra margin around viewport
            
        Returns:
            Rectangle representing the visible area
        """
        return pygame.Rect(
            self.x - margin,
            self.y - margin,
            self.viewport_width + margin * 2,
            self.viewport_height + margin * 2
        )
    
    def resize_viewport(self, width: int, height: int) -> None:
        """
        Resize the camera viewport.
        
        Args:
            width: New viewport width
            height: New viewport height
        """
        self.viewport_width = width
        self.viewport_height = height
        self._update_deadzone()
        self._clamp_to_world()
    
    def set_world_size(self, width: int, height: int) -> None:
        """
        Update the world size.
        
        Args:
            width: New world width in pixels
            height: New world height in pixels
        """
        self.world_width = width
        self.world_height = height
        self._clamp_to_world()