"""
NPC - Non-Player Character System for Untold Story
Handles NPCs with different movement patterns and behaviors
"""

import pygame
import random
import time
from typing import Optional, List, Tuple, Dict, Any
from enum import Enum
from dataclasses import dataclass

from engine.world.entity import Entity, Direction
from engine.world.tiles import TILE_SIZE, world_to_tile, tile_to_world
from engine.world.pathfinding_mixin import PathfindingMixin


class MovementPattern(Enum):
    """Movement patterns for NPCs."""
    STATIC = "static"      # No movement
    RANDOM = "random"      # Random movement within radius
    PATROL = "patrol"      # Follow a patrol path
    WANDER = "wander"      # Intelligentes Wandern mit Pathfinding
    FOLLOW = "follow"      # Spieler folgen
    FLEE = "flee"         # Vor Spieler wegrennen


@dataclass
class NPCConfig:
    """Configuration for an NPC."""
    name: str
    sprite_name: str
    position: Tuple[int, int]  # Tile coordinates
    dialogue_id: str
    movement_pattern: MovementPattern = MovementPattern.STATIC
    facing: Optional[str] = "down"
    movement_radius: int = 2
    patrol_path: Optional[List[Tuple[int, int]]] = None
    movement_speed: float = 30.0  # Pixels per second (slower than player)
    movement_delay: float = 2.0   # Seconds between movements


class NPC(Entity, PathfindingMixin):
    """
    Non-Player Character with movement patterns and dialogue.
    Jetzt mit Pathfinding-Power! Die Kumpels können endlich intelligent rumlaufen!
    """
    
    def __init__(self, config: NPCConfig, sprite_surface: Optional[pygame.Surface] = None):
        """
        Initialize NPC.
        
        Args:
            config: NPC configuration
            sprite_surface: Pre-loaded sprite surface
        """
        # Convert tile position to world coordinates
        world_x, world_y = tile_to_world(config.position[0], config.position[1])
        
        # Initialize entity
        super().__init__(world_x, world_y)
        
        # Initialize PathfindingMixin - WICHTIG!
        PathfindingMixin.__init__(self)
        
        # NPC-specific properties
        self.config = config
        self.name = config.name
        self.dialogue_id = config.dialogue_id
        self.interactable = True
        self.sprite_surface = sprite_surface
        
        # Movement properties
        self.movement_pattern = config.movement_pattern
        self.movement_speed = config.movement_speed
        self.movement_delay = config.movement_delay
        self.movement_timer = 0.0
        self.next_movement_time = time.time() + random.uniform(1.0, 3.0)  # Random initial delay
        
        # Grid-based movement
        self.grid_x, self.grid_y = config.position
        self.target_x, self.target_y = self.x, self.y
        self.is_moving = False
        
        # Set initial direction
        if config.facing:
            direction_map = {
                "up": Direction.UP,
                "down": Direction.DOWN,
                "left": Direction.LEFT,
                "right": Direction.RIGHT
            }
            self.direction = direction_map.get(config.facing, Direction.DOWN)
        
        # Pattern-specific data
        self.home_position = config.position  # Original position for random movement
        self.patrol_index = 0  # Current patrol point index
        self.patrol_forward = True  # Patrol direction
        
        # Area reference für Pathfinding - WICHTIG!
        self.current_area = None
        
        # Collision detection
        self.collision_layer = None  # Will be set by FieldScene
        
        # Sprite manager reference (will be set by FieldScene)
        self.sprite_manager = None
        
        # Player reference für FOLLOW/FLEE patterns
        self.player_ref = None
    
    def set_collision_layer(self, collision_layer: List[List[int]]) -> None:
        """Set the collision layer for movement checking."""
        self.collision_layer = collision_layer
    
    def set_sprite_manager(self, sprite_manager) -> None:
        """Set the sprite manager for dynamic sprite loading."""
        self.sprite_manager = sprite_manager
    
    def set_area(self, area) -> None:
        """Setzt die Area-Referenz für Pathfinding. MUSS von FieldScene aufgerufen werden!"""
        self.current_area = area
        print(f"[NPC] {self.name} - Area gesetzt für Pathfinding!")
    
    def set_player_reference(self, player) -> None:
        """Setzt Player-Referenz für FOLLOW/FLEE patterns."""
        self.player_ref = player
    
    def update(self, dt: float) -> None:
        """
        Update NPC behavior mit Pathfinding-Logik.
        
        Args:
            dt: Delta time in seconds
        """
        super().update(dt)
        
        # Update movement timer
        self.movement_timer += dt
        
        # Pathfinding-Update wenn wir einen Pfad haben
        if self.current_path:
            self.follow_path(dt)
            # Wenn Pfad folgen, normale Movement-Patterns ignorieren
            return
        
        # Handle grid-based movement animation
        if self.is_moving:
            self._update_movement(dt)
        else:
            # Check if it's time for next movement
            current_time = time.time()
            if current_time >= self.next_movement_time:
                self._try_move()
                # Schedule next movement
                self.next_movement_time = current_time + random.uniform(
                    self.movement_delay * 0.8, 
                    self.movement_delay * 1.2
                )
    
    def _update_movement(self, dt: float) -> None:
        """Update smooth movement animation."""
        if not self.is_moving:
            return
        
        # Calculate movement progress
        move_distance = self.movement_speed * dt
        
        # Calculate direction to target
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance = (dx * dx + dy * dy) ** 0.5
        
        if distance <= move_distance:
            # Reached target
            self.x = self.target_x
            self.y = self.target_y
            self.is_moving = False
            self.moving = False
            
            # Update grid position
            self.grid_x, self.grid_y = world_to_tile(self.x, self.y)
        else:
            # Move towards target
            self.x += (dx / distance) * move_distance
            self.y += (dy / distance) * move_distance
            self.moving = True
    
    def _try_move(self) -> None:
        """Try to execute movement based on pattern - JETZT MIT PATHFINDING!"""
        if self.is_moving or self.current_path:
            return
        
        if self.movement_pattern == MovementPattern.STATIC:
            return
        elif self.movement_pattern == MovementPattern.RANDOM:
            self._try_random_movement()
        elif self.movement_pattern == MovementPattern.PATROL:
            self._try_patrol_movement()
        elif self.movement_pattern == MovementPattern.WANDER:
            # NEU: Intelligentes Wandern mit Pathfinding!
            if self.current_area:
                self.wander_with_pathfinding(
                    area=self.current_area, 
                    home_radius=self.config.movement_radius or 3
                )
        elif self.movement_pattern == MovementPattern.FOLLOW:
            # NEU: Spieler folgen!
            if self.player_ref and self.current_area:
                self.follow_player(
                    player=self.player_ref,
                    area=self.current_area,
                    min_distance=2,
                    max_distance=5
                )
        elif self.movement_pattern == MovementPattern.FLEE:
            # NEU: Vor Spieler wegrennen!
            if self.player_ref and self.current_area:
                player_tile = world_to_tile(self.player_ref.x, self.player_ref.y)
                npc_tile = world_to_tile(self.x, self.y)
                distance = abs(player_tile[0] - npc_tile[0]) + abs(player_tile[1] - npc_tile[1])
                
                # Zu nah am Spieler? Abhauen!
                if distance < 5:
                    dx = npc_tile[0] - player_tile[0]
                    dy = npc_tile[1] - player_tile[1]
                    
                    if dx == 0 and dy == 0:
                        dx = random.choice([-1, 0, 1])
                        dy = random.choice([-1, 0, 1])
                    else:
                        if dx != 0:
                            dx = 3 if dx > 0 else -3
                        if dy != 0:
                            dy = 3 if dy > 0 else -3
                    
                    flee_x = npc_tile[0] + dx
                    flee_y = npc_tile[1] + dy
                    
                    self.find_path_to(flee_x, flee_y, self.current_area)
    
    def _try_random_movement(self) -> None:
        """Try random movement within radius."""
        if not self.config.movement_radius or self.config.movement_radius <= 0:
            return
        
        # Generate random movement
        possible_moves = []
        
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                
                new_x = self.grid_x + dx
                new_y = self.grid_y + dy
                
                # Check if within radius from home
                home_distance = max(
                    abs(new_x - self.home_position[0]),
                    abs(new_y - self.home_position[1])
                )
                
                if home_distance <= self.config.movement_radius:
                    if self._can_move_to(new_x, new_y):
                        possible_moves.append((new_x, new_y))
        
        # Sometimes stay in place
        if random.random() < 0.3:  # 30% chance to stay
            return
        
        # Choose random movement
        if possible_moves:
            new_grid_x, new_grid_y = random.choice(possible_moves)
            self._start_movement(new_grid_x, new_grid_y)
    
    def _try_patrol_movement(self) -> None:
        """Try patrol movement along path."""
        if not self.config.patrol_path or len(self.config.patrol_path) < 2:
            return
        
        # Get next patrol point
        if self.patrol_forward:
            self.patrol_index += 1
            if self.patrol_index >= len(self.config.patrol_path):
                self.patrol_index = len(self.config.patrol_path) - 2
                self.patrol_forward = False
        else:
            self.patrol_index -= 1
            if self.patrol_index < 0:
                self.patrol_index = 1
                self.patrol_forward = True
        
        target_point = self.config.patrol_path[self.patrol_index]
        target_x, target_y = target_point
        
        if self._can_move_to(target_x, target_y):
            self._start_movement(target_x, target_y)
        else:
            # If blocked, reverse direction
            self.patrol_forward = not self.patrol_forward
    
    def _can_move_to(self, tile_x: int, tile_y: int) -> bool:
        """
        Check if NPC can move to target tile.
        
        Args:
            tile_x: Target tile X
            tile_y: Target tile Y
            
        Returns:
            True if movement is possible
        """
        # Check bounds
        if not self.collision_layer:
            return True
        
        if (tile_x < 0 or tile_y < 0 or 
            tile_y >= len(self.collision_layer) or 
            tile_x >= len(self.collision_layer[0])):
            return False
        
        # Check collision (0 = passable, 1 = blocked)
        if self.collision_layer[tile_y][tile_x] != 0:
            return False
        
        return True
    
    def _start_movement(self, target_grid_x: int, target_grid_y: int) -> None:
        """
        Start movement to target grid position.
        
        Args:
            target_grid_x: Target tile X
            target_grid_y: Target tile Y
        """
        # Set target world coordinates
        self.target_x, self.target_y = tile_to_world(target_grid_x, target_grid_y)
        
        # Update facing direction
        dx = target_grid_x - self.grid_x
        dy = target_grid_y - self.grid_y
        if dx != 0 or dy != 0:
            self.direction = Direction.from_vector(dx, dy)
            # Update sprite based on new direction
            self._update_sprite_for_direction()
        
        # Start movement
        self.is_moving = True
        self.moving = True
    
    def can_interact_with_player(self, player_pos: Tuple[int, int]) -> bool:
        """
        Check if player can interact with this NPC.
        
        Args:
            player_pos: Player tile position
            
        Returns:
            True if interaction is possible
        """
        # Check if player is adjacent
        dx = abs(player_pos[0] - self.grid_x)
        dy = abs(player_pos[1] - self.grid_y)
        
        return dx <= 1 and dy <= 1 and (dx + dy) <= 1  # Adjacent, not diagonal
    
    def on_interact(self, player: 'Entity') -> bool:
        """
        Handle player interaction.
        
        Args:
            player: Player entity
            
        Returns:
            True if interaction was handled
        """
        # Stop movement when interacted with
        if self.is_moving:
            self.x = self.target_x
            self.y = self.target_y
            self.is_moving = False
            self.moving = False
            self.grid_x, self.grid_y = world_to_tile(self.x, self.y)
        
        # Face towards player
        player_grid = world_to_tile(player.x, player.y)
        dx = player_grid[0] - self.grid_x
        dy = player_grid[1] - self.grid_y
        
        if dx != 0 or dy != 0:
            self.direction = Direction.from_vector(dx, dy)
        
        return True
    
    def _update_sprite_for_direction(self) -> None:
        """
        Update the NPC's sprite based on current direction.
        This method tries to load the appropriate directional sprite.
        """
        if not hasattr(self, 'sprite_manager') or not self.sprite_manager:
            return
        
        # Get direction string
        direction_str = self.direction.name.lower()
        
        # Try to get sprite for current direction
        new_sprite = self.sprite_manager.get_npc_sprite(self.config.sprite_name, direction_str)
        if new_sprite:
            self.sprite_surface = new_sprite
            print(f"[NPC] {self.name} updated sprite to {self.config.sprite_name}_{direction_str}")
        else:
            # Fallback: try to get any available direction
            for fallback_dir in ["down", "up", "left", "right"]:
                fallback_sprite = self.sprite_manager.get_npc_sprite(self.config.sprite_name, fallback_dir)
                if fallback_sprite:
                    self.sprite_surface = fallback_sprite
                    print(f"[NPC] {self.name} fallback sprite: {self.config.sprite_name}_{fallback_dir}")
                    break
    
    @classmethod
    def from_config_dict(cls, name: str, config_dict: Dict[str, Any], 
                        sprite_surface: Optional[pygame.Surface] = None) -> 'NPC':
        """
        Create NPC from configuration dictionary.
        
        Args:
            name: NPC name
            config_dict: Configuration data from JSON
            sprite_surface: Pre-loaded sprite
            
        Returns:
            NPC instance
        """
        # Parse movement pattern - ERWEITERT!
        pattern_str = config_dict.get("movement_pattern", "static")
        pattern_map = {
            "static": MovementPattern.STATIC,
            "random": MovementPattern.RANDOM,
            "patrol": MovementPattern.PATROL,
            "wander": MovementPattern.WANDER,  # NEU!
            "follow": MovementPattern.FOLLOW,  # NEU!
            "flee": MovementPattern.FLEE,      # NEU!
        }
        movement_pattern = pattern_map.get(pattern_str.lower(), MovementPattern.STATIC)
        
        # Create config
        config = NPCConfig(
            name=name,
            sprite_name=config_dict.get("sprite", "villager_m"),
            position=tuple(config_dict.get("position", [0, 0])),
            dialogue_id=config_dict.get("dialogue_id", "default_talk"),
            movement_pattern=movement_pattern,
            facing=config_dict.get("facing", "down"),
            movement_radius=config_dict.get("movement_radius", 2),
            patrol_path=[tuple(point) for point in config_dict.get("patrol_path", [])] if config_dict.get("patrol_path") else None,
            movement_speed=config_dict.get("movement_speed", 30.0),
            movement_delay=config_dict.get("movement_delay", 2.0)
        )
        
        return cls(config, sprite_surface)
