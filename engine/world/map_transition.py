"""
Map Transition System für smooth Übergänge zwischen Maps
Behandelt das Laden neuer Maps und Positionierung des Spielers
"""

from typing import Dict, Any, Optional
from engine.world.entity import Direction


class MapTransition:
    """Handles smooth transitions between maps"""
    
    @staticmethod
    def execute_transition(game, warp_data: Dict[str, Any]) -> None:
        """
        Execute a map transition with smooth effects.
        
        Args:
            game: Game instance
            warp_data: Warp information including target map and spawn position
        """
        target_map = warp_data.get('target_map')
        spawn_x = warp_data.get('spawn_x', 5)
        spawn_y = warp_data.get('spawn_y', 5)
        direction = warp_data.get('direction')
        transition_type = warp_data.get('transition_type', 'fade')
        spawn_point = warp_data.get('spawn_point', 'default')
        
        if not target_map:
            print("Warning: No target map specified for transition")
            return
        
        # Play warp sound (optional)
        try:
            sound = game.resources.load_sound("warp.wav", volume=0.5)
            sound.play()
        except:
            pass
        
        # Load new map
        if hasattr(game.current_scene, 'load_map'):
            game.current_scene.load_map(target_map, spawn_x, spawn_y)
        
        # Position player at target
        if hasattr(game.current_scene, 'player') and game.current_scene.player:
            player = game.current_scene.player
            player.set_tile_position(spawn_x, spawn_y)
            
            # Set direction if specified
            if direction:
                try:
                    player.direction = Direction[direction.upper()]
                except (KeyError, AttributeError):
                    pass  # Invalid direction, keep current
