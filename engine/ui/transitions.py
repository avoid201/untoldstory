"""
Screen Transition Effects for Untold Story
Provides fade, wipe, and other transition effects between scenes
"""

import pygame
import math
from typing import Optional, Tuple
from enum import Enum
from engine.core.scene_base import TransitionScene, Scene


class TransitionType(Enum):
    """Types of transition effects."""
    FADE = "fade"
    FADE_TO_BLACK = "fade_to_black"
    FADE_TO_WHITE = "fade_to_white"
    WIPE_LEFT = "wipe_left"
    WIPE_RIGHT = "wipe_right"
    WIPE_UP = "wipe_up"
    WIPE_DOWN = "wipe_down"
    RADIAL = "radial"
    PIXELATE = "pixelate"
    BATTLE_SWIRL = "battle_swirl"


class FadeTransition(TransitionScene):
    """
    Fade transition between two scenes.
    """
    
    def __init__(self,
                 game: 'Game',
                 from_scene: Optional[Scene],
                 to_scene: Scene,
                 duration: float = 0.5,
                 fade_color: Tuple[int, int, int] = (0, 0, 0),
                 scene_kwargs: Optional[dict] = None) -> None:
        """
        Initialize fade transition.
        
        Args:
            game: Game instance
            from_scene: Scene transitioning from
            to_scene: Scene transitioning to
            duration: Transition duration in seconds
            fade_color: Color to fade through
            scene_kwargs: Arguments to pass to to_scene.enter() when transition completes
        """
        super().__init__(game, from_scene, to_scene, duration)
        self.fade_color = fade_color
        self.scene_kwargs = scene_kwargs or {}
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the fade transition."""
        if self.progress < 0.5:
            # First half: fade out from scene
            if self.from_surface:
                surface.blit(self.from_surface, (0, 0))
            
            # Draw fade overlay
            alpha = int(self.progress * 2 * 255)
            fade_surface = pygame.Surface(surface.get_size())
            fade_surface.fill(self.fade_color)
            fade_surface.set_alpha(alpha)
            surface.blit(fade_surface, (0, 0))
        else:
            # Second half: fade in to scene
            if self.to_surface:
                surface.blit(self.to_surface, (0, 0))
            
            # Draw fade overlay
            alpha = int((1.0 - (self.progress - 0.5) * 2) * 255)
            fade_surface = pygame.Surface(surface.get_size())
            fade_surface.fill(self.fade_color)
            fade_surface.set_alpha(alpha)
            surface.blit(fade_surface, (0, 0))


class WipeTransition(TransitionScene):
    """
    Wipe transition that reveals the new scene progressively.
    """
    
    def __init__(self,
                 game: 'Game',
                 from_scene: Optional[Scene],
                 to_scene: Scene,
                 duration: float = 0.5,
                 direction: str = "right") -> None:
        """
        Initialize wipe transition.
        
        Args:
            game: Game instance
            from_scene: Scene transitioning from
            to_scene: Scene transitioning to
            duration: Transition duration in seconds
            direction: Wipe direction (left, right, up, down)
        """
        super().__init__(game, from_scene, to_scene, duration)
        self.direction = direction
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the wipe transition."""
        width = surface.get_width()
        height = surface.get_height()
        
        # Draw base scene
        if self.from_surface:
            surface.blit(self.from_surface, (0, 0))
        
        if not self.to_surface:
            return
        
        # Calculate wipe position based on direction
        if self.direction == "right":
            wipe_x = int(self.progress * width)
            clip_rect = pygame.Rect(0, 0, wipe_x, height)
        elif self.direction == "left":
            wipe_x = int((1.0 - self.progress) * width)
            clip_rect = pygame.Rect(wipe_x, 0, width - wipe_x, height)
        elif self.direction == "down":
            wipe_y = int(self.progress * height)
            clip_rect = pygame.Rect(0, 0, width, wipe_y)
        elif self.direction == "up":
            wipe_y = int((1.0 - self.progress) * height)
            clip_rect = pygame.Rect(0, wipe_y, width, height - wipe_y)
        else:
            clip_rect = pygame.Rect(0, 0, width, height)
        
        # Draw the wiped portion of the new scene
        if clip_rect.width > 0 and clip_rect.height > 0:
            subsurface = self.to_surface.subsurface(clip_rect)
            surface.blit(subsurface, clip_rect.topleft)
        
        # Draw wipe edge effect
        self._draw_wipe_edge(surface, clip_rect)
    
    def _draw_wipe_edge(self, surface: pygame.Surface, clip_rect: pygame.Rect) -> None:
        """Draw an edge effect for the wipe."""
        edge_color = (255, 255, 255)
        edge_width = 2
        
        if self.direction == "right" and clip_rect.width > 0:
            pygame.draw.line(surface, edge_color,
                           (clip_rect.right - 1, 0),
                           (clip_rect.right - 1, clip_rect.height),
                           edge_width)
        elif self.direction == "left" and clip_rect.x < surface.get_width():
            pygame.draw.line(surface, edge_color,
                           (clip_rect.left, 0),
                           (clip_rect.left, clip_rect.height),
                           edge_width)
        elif self.direction == "down" and clip_rect.height > 0:
            pygame.draw.line(surface, edge_color,
                           (0, clip_rect.bottom - 1),
                           (clip_rect.width, clip_rect.bottom - 1),
                           edge_width)
        elif self.direction == "up" and clip_rect.y < surface.get_height():
            pygame.draw.line(surface, edge_color,
                           (0, clip_rect.top),
                           (clip_rect.width, clip_rect.top),
                           edge_width)


class RadialTransition(TransitionScene):
    """
    Radial/iris transition that opens or closes in a circle.
    """
    
    def __init__(self,
                 game: 'Game',
                 from_scene: Optional[Scene],
                 to_scene: Scene,
                 duration: float = 0.7,
                 center: Optional[Tuple[int, int]] = None,
                 opening: bool = True) -> None:
        """
        Initialize radial transition.
        
        Args:
            game: Game instance
            from_scene: Scene transitioning from
            to_scene: Scene transitioning to
            duration: Transition duration in seconds
            center: Center point of the circle (None for screen center)
            opening: If True, circle opens; if False, circle closes
        """
        super().__init__(game, from_scene, to_scene, duration)
        
        if center is None:
            self.center = (game.logical_size[0] // 2, game.logical_size[1] // 2)
        else:
            self.center = center
        
        self.opening = opening
        
        # Calculate maximum radius needed
        max_dist_x = max(self.center[0], game.logical_size[0] - self.center[0])
        max_dist_y = max(self.center[1], game.logical_size[1] - self.center[1])
        self.max_radius = math.sqrt(max_dist_x ** 2 + max_dist_y ** 2)
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the radial transition."""
        # Draw base scene
        if self.opening:
            # Opening: show from scene, reveal to scene
            if self.from_surface:
                surface.blit(self.from_surface, (0, 0))
            base_surface = self.to_surface
        else:
            # Closing: show to scene, reveal from scene
            if self.to_surface:
                surface.blit(self.to_surface, (0, 0))
            base_surface = self.from_surface
        
        if not base_surface:
            return
        
        # Calculate current radius
        if self.opening:
            radius = int(self.progress * self.max_radius)
        else:
            radius = int((1.0 - self.progress) * self.max_radius)
        
        # Create a mask surface
        mask = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        mask.fill((0, 0, 0, 0))
        
        # Draw circle on mask
        pygame.draw.circle(mask, (255, 255, 255, 255), self.center, radius)
        
        # Apply mask to reveal scene
        reveal_surface = base_surface.copy()
        reveal_surface.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        
        # Draw the revealed portion
        surface.blit(reveal_surface, (0, 0))
        
        # Draw circle edge
        if 0 < radius < self.max_radius:
            pygame.draw.circle(surface, (255, 255, 255), self.center, radius, 2)


class BattleSwirlTransition(TransitionScene):
    """
    Swirling transition effect commonly used for battle encounters.
    """
    
    def __init__(self,
                 game: 'Game',
                 from_scene: Optional[Scene],
                 to_scene: Scene,
                 duration: float = 1.0) -> None:
        """
        Initialize battle swirl transition.
        
        Args:
            game: Game instance
            from_scene: Scene transitioning from
            to_scene: Scene transitioning to
            duration: Transition duration in seconds
        """
        super().__init__(game, from_scene, to_scene, duration)
        self.swirl_intensity = 0.0
    
    def update(self, dt: float) -> None:
        """Update the transition."""
        super().update(dt)
        
        # Calculate swirl intensity
        if self.progress < 0.5:
            # Increase swirl
            self.swirl_intensity = self.progress * 2
        else:
            # Decrease swirl
            self.swirl_intensity = (1.0 - self.progress) * 2
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the battle swirl transition."""
        width = surface.get_width()
        height = surface.get_height()
        
        # Choose which scene to distort
        if self.progress < 0.5:
            base_surface = self.from_surface
        else:
            base_surface = self.to_surface
        
        if not base_surface:
            surface.fill((0, 0, 0))
            return
        
        # Create distorted surface
        distorted = pygame.Surface((width, height))
        
        # Apply swirl distortion
        for y in range(0, height, 2):  # Sample every 2 pixels for performance
            # Calculate swirl offset for this row
            offset = int(math.sin(y * 0.1 + self.elapsed * 10) * 
                        self.swirl_intensity * 20)
            
            # Get source row
            src_rect = pygame.Rect(0, y, width, 2)
            if src_rect.bottom <= base_surface.get_height():
                row = base_surface.subsurface(src_rect)
                
                # Draw row with offset
                dest_x = offset % width
                distorted.blit(row, (dest_x, y))
                
                # Wrap around if needed
                if dest_x > 0:
                    distorted.blit(row, (dest_x - width, y))
        
        surface.blit(distorted, (0, 0))
        
        # Add flash effect at peak
        if 0.45 < self.progress < 0.55:
            flash_alpha = int(255 * (1.0 - abs(self.progress - 0.5) * 20))
            flash = pygame.Surface((width, height))
            flash.fill((255, 255, 255))
            flash.set_alpha(flash_alpha)
            surface.blit(flash, (0, 0))


class TransitionManager:
    """
    Factory for creating transitions.
    """
    
    @staticmethod
    def create_transition(transition_type: TransitionType,
                         game: 'Game',
                         from_scene: Optional[Scene],
                         to_scene: Scene,
                         duration: float = 0.5,
                         **kwargs) -> TransitionScene:
        """
        Create a transition of the specified type.
        
        Args:
            transition_type: Type of transition to create
            game: Game instance
            from_scene: Scene transitioning from
            to_scene: Scene transitioning to
            duration: Transition duration
            **kwargs: Additional transition-specific parameters
            
        Returns:
            TransitionScene instance
        """
        if transition_type == TransitionType.FADE:
            return FadeTransition(game, from_scene, to_scene, duration,
                                 fade_color=kwargs.get('fade_color', (0, 0, 0)))
        
        elif transition_type == TransitionType.FADE_TO_BLACK:
            return FadeTransition(game, from_scene, to_scene, duration,
                                 fade_color=(0, 0, 0))
        
        elif transition_type == TransitionType.FADE_TO_WHITE:
            return FadeTransition(game, from_scene, to_scene, duration,
                                 fade_color=(255, 255, 255))
        
        elif transition_type in [TransitionType.WIPE_LEFT, TransitionType.WIPE_RIGHT,
                                TransitionType.WIPE_UP, TransitionType.WIPE_DOWN]:
            direction = transition_type.value.split('_')[1]
            return WipeTransition(game, from_scene, to_scene, duration, direction)
        
        elif transition_type == TransitionType.RADIAL:
            return RadialTransition(game, from_scene, to_scene, duration,
                                   center=kwargs.get('center'),
                                   opening=kwargs.get('opening', True))
        
        elif transition_type == TransitionType.BATTLE_SWIRL:
            return BattleSwirlTransition(game, from_scene, to_scene, duration)
        
        else:
            # Default to fade
            return FadeTransition(game, from_scene, to_scene, duration)