"""
Ledge Handler für das Grid-basierte Movement System
Behandelt das Springen über Kanten (Ledges)
"""

from typing import List, Tuple, Optional
from engine.world.movement_states import MovementState
from engine.world.entity import Entity


class LedgeHandler:
    """Handles ledge jumping mechanics"""
    
    @staticmethod
    def can_jump_ledge(current_tile: Tuple[int, int], direction: 'Direction', 
                       collision_layer: List[List[int]]) -> bool:
        """
        Check if the player can jump over a ledge in the given direction.
        
        Args:
            current_tile: Current tile position (x, y)
            direction: Direction to jump
            collision_layer: Map collision data
            
        Returns:
            True if ledge jumping is possible
        """
        if not collision_layer:
            return False
        
        current_x, current_y = current_tile
        dx, dy = direction.vector
        
        # Check if target tile is solid (ledge)
        target_x = current_x + dx
        target_y = current_y + dy
        
        # Check bounds
        if (target_y < 0 or target_y >= len(collision_layer) or
            target_x < 0 or target_x >= len(collision_layer[0])):
            return False
        
        # Check if target tile is solid (ledge)
        if collision_layer[target_y][target_x] != 0:
            return False
        
        # Check if landing tile is walkable
        landing_x = current_x + (dx * 2)
        landing_y = current_y + (dy * 2)
        
        # Check bounds
        if (landing_y < 0 or landing_y >= len(collision_layer) or
            landing_x < 0 or landing_x >= len(collision_layer[0])):
            return False
        
        # Check if landing tile is walkable
        if collision_layer[landing_y][landing_x] != 0:
            return False
        
        return True
    
    @staticmethod
    def execute_ledge_jump(player: Entity, target_x: int, target_y: int) -> None:
        """
        Execute a ledge jump to the target position.
        
        Args:
            player: Player entity to move
            target_x: Target tile X
            target_y: Target tile Y
        """
        # Set target position (2 tiles away from current)
        current_x, current_y = player.get_tile_position()
        dx = target_x - current_x
        dy = target_y - current_y
        
        # Landing position is 2 tiles away
        landing_x = current_x + (dx * 2)
        landing_y = current_y + (dy * 2)
        
        # Set player to jumping state
        player.movement_state = MovementState.JUMPING
        player.target_grid_x = landing_x
        player.target_grid_y = landing_y
        player.move_progress = 0.0
        player.moving = True
