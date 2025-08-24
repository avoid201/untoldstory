"""
Base Entity System for Untold Story
Defines the base class for all game entities (player, NPCs, objects)
"""

import pygame
from typing import Optional, Tuple, Dict, Any, List
from enum import Enum
from dataclasses import dataclass
from engine.world.tiles import TILE_SIZE, world_to_tile, tile_to_world
import os


class Direction(Enum):
    """Cardinal directions for entity facing."""
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    
    @property
    def vector(self) -> Tuple[int, int]:
        """Get the direction as a unit vector."""
        return self.value
    
    @staticmethod
    def from_vector(dx: float, dy: float) -> 'Direction':
        """
        Get the closest cardinal direction from a vector.
        
        Args:
            dx: X component of direction
            dy: Y component of direction
            
        Returns:
            Closest Direction enum value
        """
        if abs(dx) > abs(dy):
            return Direction.RIGHT if dx > 0 else Direction.LEFT
        else:
            return Direction.DOWN if dy > 0 else Direction.UP


@dataclass
class EntitySprite:
    """Sprite configuration for an entity."""
    sheet_path: str = None  # Path to sprite sheet
    surface: pygame.Surface = None  # For pre-loaded sprites
    frame_width: int = 16   # 16x16 Pixel Sprites (GBC-Stil)
    frame_height: int = 16  # 16x16 Pixel Sprites (GBC-Stil)
    animations: Dict[str, List[int]] = None  # Animation name -> frame indices
    frame_duration: float = 0.1  # Seconds per frame
    
    def __post_init__(self):
        if self.animations is None:
            # Default animations for 4-directional character
            self.animations = {
                'idle_down': [0],
                'idle_up': [4],
                'idle_left': [8],
                'idle_right': [12],
                'walk_down': [0, 1, 2, 3],
                'walk_up': [4, 5, 6, 7],
                'walk_left': [8, 9, 10, 11],
                'walk_right': [12, 13, 14, 15],
            }


class Entity:
    """
    Base class for all world entities.
    Provides position, collision, sprite rendering, and basic physics.
    """
    
    def __init__(self,
                 x: float,
                 y: float,
                 width: int = 14,  # 14 Pixel für 16x16 Tiles (etwas kleiner als Tile für Bewegung)
                 height: int = 14, # 14 Pixel für 16x16 Tiles (etwas kleiner als Tile für Bewegung)
                 sprite_config: Optional[EntitySprite] = None) -> None:
        """
        Initialize an entity.
        
        Args:
            x: Initial X position in world coordinates
            y: Initial Y position in world coordinates
            width: Collision box width in pixels
            height: Collision box height in pixels
            sprite_config: Optional sprite configuration
        """
        # Position and physics
        self.x = x
        self.y = y
        self.speed = 60.0  # Standard-Geschwindigkeit für 16x16 Tiles
        
        # Collision
        self.width = width
        self.height = height
        self.solid = True  # Whether this entity blocks movement
        self.collidable = True  # Whether this entity can collide
        
        # Calculate collision box offset to center it
        self.collision_offset_x = (TILE_SIZE - width) // 2
        self.collision_offset_y = (TILE_SIZE - height) // 2
        
        # Direction and state
        self.direction = Direction.DOWN
        self.moving = False
        self.interactable = False
        self.interaction_range = TILE_SIZE * 1.5
        
        # Sprite and animation
        self.sprite_config = sprite_config
        self.sprite_surface: Optional[pygame.Surface] = None
        # Animation state
        self.current_animation = 'idle_down'  # Standardmäßig idle_down
        self.animation_frame = 0
        self.animation_timer = 0.0
        
        # Load sprite if configured
        if sprite_config and sprite_config.sheet_path:
            self._load_sprite(sprite_config.sheet_path)
        
        # Entity properties
        self.name = "Entity"
        self.properties: Dict[str, Any] = {}
        self.active = True
        self.visible = True
        self.moving = False
        self.direction = Direction.DOWN  # Standardmäßig nach unten schauen
    
    def _load_sprite(self, sprite_path: str) -> bool:
        """Load sprite from path."""
        try:
            # Versuche zuerst den SpriteManager zu verwenden
            if hasattr(self, 'game') and hasattr(self.game, 'sprite_manager'):
                sprite_manager = self.game.sprite_manager
                if sprite_manager:
                    # Versuche, den Sprite aus dem Cache zu laden
                    sprite = sprite_manager.load_sprite(sprite_path)
                    if sprite:
                        self.sprite_config.surface = sprite
                        self.sprite_surface = sprite
                        print(f"Entity-Sprite geladen via SpriteManager: {sprite_path} ({sprite.get_size()})")
                        return True
            
            # Fallback: Lade den Sprite direkt
            if os.path.exists(sprite_path):
                sprite = pygame.image.load(sprite_path).convert_alpha()
                if sprite:
                    # Sprites sind 16x16, keine Skalierung nötig
                    self.sprite_config.surface = sprite
                    self.sprite_surface = sprite
                    print(f"Entity-Sprite direkt geladen: {sprite_path} ({sprite.get_size()})")
                    return True
                else:
                    print(f"Entity-Sprite konnte nicht geladen werden: {sprite_path}")
                    return False
            else:
                print(f"Entity-Sprite-Datei nicht gefunden: {sprite_path}")
                return False
                
        except Exception as e:
            print(f"Fehler beim Laden des Entity-Sprites {sprite_path}: {e}")
            return False
    
    def get_rect(self) -> pygame.Rect:
        """
        Get the collision rectangle in world coordinates.
        
        Returns:
            pygame.Rect representing the collision box
        """
        return pygame.Rect(
            self.x + self.collision_offset_x,
            self.y + self.collision_offset_y,
            self.width,
            self.height
        )
    
    def get_center(self) -> Tuple[float, float]:
        """
        Get the center position of the entity.
        
        Returns:
            Tuple of (center_x, center_y) in world coordinates
        """
        rect = self.get_rect()
        return (rect.centerx, rect.centery)
    
    def get_tile_position(self) -> Tuple[int, int]:
        """
        Get the tile coordinates of the entity's center.
        
        Returns:
            Tuple of (tile_x, tile_y)
        """
        center_x, center_y = self.get_center()
        return world_to_tile(center_x, center_y)
    
    def set_position(self, x: float, y: float) -> None:
        """
        Set the entity's position.
        
        Args:
            x: New X position in world coordinates
            y: New Y position in world coordinates
        """
        self.x = x
        self.y = y
    
    def set_tile_position(self, tile_x: int, tile_y: int) -> None:
        """
        Set the entity's position by tile coordinates.
        
        Args:
            tile_x: Tile X coordinate
            tile_y: Tile Y coordinate
        """
        self.x, self.y = tile_to_world(tile_x, tile_y)
    
    def move(self, dx: float, dy: float) -> None:
        """
        Move the entity by a delta amount.
        
        Args:
            dx: X movement in pixels
            dy: Y movement in pixels
        """
        self.x += dx
        self.y += dy
        
        # Update facing direction if moving
        if dx != 0 or dy != 0:
            self.direction = Direction.from_vector(dx, dy)
            self.moving = True
        else:
            self.moving = False
    
    def update(self, dt: float) -> None:
        """
        Update the entity.
        
        Args:
            dt: Delta time in seconds
        """
        # Update animation
        if self.sprite_config:
            self._update_animation(dt)
    
    def _update_animation(self, dt: float) -> None:
        """
        Update sprite animation.
        
        Args:
            dt: Delta time in seconds
        """
        if not self.sprite_config or not self.sprite_config.animations:
            return
        
        # Determine current animation based on state
        anim_name = self._get_animation_name()
        
        # Change animation if needed
        if anim_name != self.current_animation:
            self.current_animation = anim_name
            self.animation_frame = 0
            self.animation_timer = 0.0
        
        # Advance animation frame
        frames = self.sprite_config.animations.get(self.current_animation, [0])
        if len(frames) > 1:
            self.animation_timer += dt
            if self.animation_timer >= self.sprite_config.frame_duration:
                self.animation_timer -= self.sprite_config.frame_duration
                self.animation_frame = (self.animation_frame + 1) % len(frames)
    
    def _get_animation_name(self) -> str:
        """
        Get the current animation name based on entity state.
        
        Returns:
            Animation name string
        """
        # Build animation name from state and direction
        state = 'walk' if self.moving else 'idle'
        direction = self.direction.name.lower()
        return f'{state}_{direction}'
    
    def draw(self, surface: pygame.Surface, camera_offset: Tuple[float, float]) -> None:
        """Draw the entity."""
        if not self.visible:
            return
            
        # Calculate screen position
        screen_x = int(self.x - camera_offset[0])
        screen_y = int(self.y - camera_offset[1])
        
        if self.sprite_surface:
            # Draw sprite (either with or without sprite_config)
            self._draw_sprite(surface, camera_offset)
        else:
            # Draw fallback
            self._draw_fallback(surface, screen_x, screen_y)
    
    def _draw_sprite(self, surface: pygame.Surface, camera_offset: Tuple[float, float]) -> None:
        """Draw the entity sprite."""
        if not self.visible or not self.sprite_surface:
            return
            
        try:
            # Berechne die Position relativ zur Kamera
            screen_x = int(self.x - camera_offset[0])
            screen_y = int(self.y - camera_offset[1])
            
            # Für NPCs: Zeichne einfach den kompletten Sprite
            if self.sprite_config and self.sprite_config.animations:
                # Komplex: Sprite-Sheet mit Animationen
                anim_name = self._get_animation_name()
                frames = self.sprite_config.animations.get(anim_name, [0])
                if frames:
                    current_frame = frames[self.animation_frame % len(frames)]
                    
                    # Berechne die Position des Frames im Sprite-Sheet
                    frame_x = (current_frame % 4) * self.sprite_config.frame_width  # 4 Spalten
                    frame_y = (current_frame // 4) * self.sprite_config.frame_height  # Reihen
                    
                    # Erstelle ein Rechteck für den Frame
                    frame_rect = pygame.Rect(
                        frame_x, frame_y,
                        self.sprite_config.frame_width,
                        self.sprite_config.frame_height
                    )
                    
                    # Zeichne nur den aktuellen Frame
                    surface.blit(self.sprite_surface, (screen_x, screen_y), frame_rect)
                else:
                    # Fallback: Zeichne den ersten Frame
                    surface.blit(self.sprite_surface, (screen_x, screen_y))
            else:
                # Einfach: Einzelner Sprite (NPCs)
                surface.blit(self.sprite_surface, (screen_x, screen_y))
            
            # Debug-Informationen (nur wenn Debug aktiviert ist)
            if hasattr(self, 'game') and hasattr(self.game, 'debug_mode') and self.game.debug_mode:
                # Zeichne Debug-Rahmen
                debug_color = (255, 0, 0)  # Rot
                debug_rect = pygame.Rect(
                    screen_x - self.sprite_config.frame_width // 2,
                    screen_y - self.sprite_config.frame_height // 2,
                    self.sprite_config.frame_width,
                    self.sprite_config.frame_height
                )
                pygame.draw.rect(surface, debug_color, debug_rect, 2)
                
                # Zeichne Debug-Text
                debug_font = pygame.font.Font(None, 24)
                debug_text = f"ID: {self.entity_id}, Pos: ({self.x:.1f}, {self.y:.1f})"
                debug_surface = debug_font.render(debug_text, True, debug_color)
                surface.blit(debug_surface, (debug_rect.x, debug_rect.y - 20))
                
        except Exception as e:
            print(f"Fehler beim Zeichnen des Entity-Sprites: {e}")
            # Zeichne einen Fallback-Rechteck
            fallback_rect = pygame.Rect(screen_x - 8, screen_y - 8, 16, 16)
            pygame.draw.rect(surface, (255, 0, 255), fallback_rect)  # Magenta
    
    def _draw_fallback(self, surface: pygame.Surface, x: float, y: float) -> None:
        """
        Draw a fallback representation for the entity when sprite loading fails.
        
        Args:
            surface: Surface to draw on
            x: Screen X position
            y: Screen Y position
        """
        # Draw entity box with better colors
        color = (100, 200, 100) if self.interactable else (200, 100, 100)
        pygame.draw.rect(surface, color, (x, y, TILE_SIZE, TILE_SIZE), 2)
        
        # Draw collision box
        pygame.draw.rect(
            surface,
            (255, 255, 0),
            (x + self.collision_offset_x, y + self.collision_offset_y,
             self.width, self.height),
            1
        )
        
        # Draw direction indicator
        center_x = x + TILE_SIZE // 2
        center_y = y + TILE_SIZE // 2
        dir_x, dir_y = self.direction.vector
        pygame.draw.line(
            surface,
            (255, 255, 255),
            (center_x, center_y),
            (center_x + dir_x * 6, center_y + dir_y * 6),
            2
        )
        
        # Add entity type indicator
        entity_type = "NPC" if self.interactable else "OBJ"
        try:
            font = pygame.font.Font(None, 16)
            text_surf = font.render(entity_type, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=(center_x, center_y + 20))
            surface.blit(text_surf, text_rect)
        except:
            pass  # Ignore font errors
    
    def check_collision(self, other: 'Entity') -> bool:
        """
        Check collision with another entity.
        
        Args:
            other: Another entity to check collision with
            
        Returns:
            True if entities are colliding
        """
        if not self.collidable or not other.collidable:
            return False
        
        return self.get_rect().colliderect(other.get_rect())
    
    def get_interaction_point(self) -> Tuple[int, int]:
        """
        Get the tile position this entity would interact with.
        
        Returns:
            Tuple of (tile_x, tile_y) for interaction point
        """
        center_x, center_y = self.get_center()
        dir_x, dir_y = self.direction.vector
        
        # Check one tile in facing direction
        check_x = center_x + dir_x * TILE_SIZE
        check_y = center_y + dir_y * TILE_SIZE
        
        return world_to_tile(check_x, check_y)
    
    def can_interact_with(self, other: 'Entity') -> bool:
        """
        Check if this entity can interact with another.
        
        Args:
            other: Another entity to check interaction with
            
        Returns:
            True if interaction is possible
        """
        if not other.interactable:
            return False
        
        # Check distance
        my_center = self.get_center()
        other_center = other.get_center()
        
        dx = my_center[0] - other_center[0]
        dy = my_center[1] - other_center[1]
        distance = (dx * dx + dy * dy) ** 0.5
        
        return distance <= self.interaction_range
    
    def on_interact(self, interactor: 'Entity') -> bool:
        """
        Called when another entity interacts with this one.
        Override in subclasses to define interaction behavior.
        
        Args:
            interactor: The entity initiating interaction
            
        Returns:
            True if interaction was handled
        """
        return False
    
    def on_collision(self, other: 'Entity') -> None:
        """
        Called when this entity collides with another.
        Override in subclasses to define collision behavior.
        
        Args:
            other: The entity collided with
        """
        pass