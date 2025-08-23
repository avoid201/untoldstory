# engine/world/npc_manager.py
"""
NPC Manager for Untold Story
Handles spawning, management, and behavior of NPCs from interaction data
"""

import pygame
import json
import random
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from engine.world.entity import Entity, EntitySprite, Direction
from engine.world.tiles import TILE_SIZE
from engine.ui.dialogue import DialoguePage


class ManagedNPC(Entity):
    """
    An NPC entity managed by the NPC Manager.
    Created from data rather than hardcoded.
    """
    
    def __init__(self, npc_data, game):
        """
        Initialize a managed NPC from data.
        
        Args:
            npc_data: NPCData object with configuration
            game: Reference to game object
        """
        # Initialize entity at tile position
        x = npc_data.position[0] * TILE_SIZE
        y = npc_data.position[1] * TILE_SIZE
        
        # Create sprite config
        sprite_config = EntitySprite(
            sheet_path=npc_data.sprite,
            frame_width=16,
            frame_height=16
        )
        
        super().__init__(x, y, 14, 14, sprite_config)
        
        # Store NPC data
        self.npc_id = npc_data.id
        self.npc_data = npc_data
        self.game = game
        
        # Set properties
        self.name = npc_data.id.replace('_', ' ').title()
        self.interactable = True
        self.dialog_id = npc_data.dialog
        
        # Movement properties
        self.movement_type = npc_data.movement
        self.patrol_route = npc_data.route
        self.patrol_index = 0
        self.movement_timer = 0
        self.movement_cooldown = 2.0  # Seconds between movements
        
        # Set initial facing direction
        self.set_facing(npc_data.facing)
        
        # Load sprite
        self._load_npc_sprite()
    
    def _load_npc_sprite(self):
        """Load the NPC sprite using the sprite manager."""
        try:
            if hasattr(self.game, 'sprite_manager'):
                sprite = self.game.sprite_manager.get_npc_sprite(self.npc_data.sprite)
                if sprite:
                    self.sprite_surface = sprite
                    self.sprite_config.surface = sprite
        except Exception as e:
            print(f"[ManagedNPC] Failed to load sprite {self.npc_data.sprite}: {e}")
    
    def set_facing(self, direction_str: str):
        """Set the NPC's facing direction."""
        direction_map = {
            'north': Direction.UP,
            'south': Direction.DOWN,
            'east': Direction.RIGHT,
            'west': Direction.LEFT,
            'up': Direction.UP,
            'down': Direction.DOWN,
            'left': Direction.LEFT,
            'right': Direction.RIGHT
        }
        
        if direction_str.lower() in direction_map:
            self.direction = direction_map[direction_str.lower()]
    
    def update(self, dt: float):
        """Update NPC behavior."""
        super().update(dt)
        
        # Handle movement patterns
        if self.movement_type != 'static':
            self.movement_timer += dt
            
            if self.movement_timer >= self.movement_cooldown:
                self.movement_timer = 0
                self._execute_movement()
    
    def _execute_movement(self):
        """Execute movement based on NPC's movement type."""
        if self.movement_type == 'random':
            # Random movement in any direction
            directions = [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]
            direction = random.choice(directions)
            self._try_move(direction)
            
        elif self.movement_type == 'patrol' and self.patrol_route:
            # Follow patrol route
            if self.patrol_index < len(self.patrol_route):
                target = self.patrol_route[self.patrol_index]
                current_tile = (self.x // TILE_SIZE, self.y // TILE_SIZE)
                
                # Move towards target
                dx = target[0] - current_tile[0]
                dy = target[1] - current_tile[1]
                
                if dx > 0:
                    self._try_move(Direction.RIGHT)
                elif dx < 0:
                    self._try_move(Direction.LEFT)
                elif dy > 0:
                    self._try_move(Direction.DOWN)
                elif dy < 0:
                    self._try_move(Direction.UP)
                else:
                    # Reached waypoint, move to next
                    self.patrol_index = (self.patrol_index + 1) % len(self.patrol_route)
    
    def _try_move(self, direction: Direction):
        """Try to move in a direction with collision checking."""
        # Calculate new position
        dx, dy = 0, 0
        if direction == Direction.UP:
            dy = -TILE_SIZE
        elif direction == Direction.DOWN:
            dy = TILE_SIZE
        elif direction == Direction.LEFT:
            dx = -TILE_SIZE
        elif direction == Direction.RIGHT:
            dx = TILE_SIZE
        
        new_x = self.x + dx
        new_y = self.y + dy
        
        # TODO: Check collision with map
        # For now, just move and update direction
        self.x = new_x
        self.y = new_y
        self.direction = direction
    
    def get_dialogue_pages(self) -> List[DialoguePage]:
        """Get dialogue pages for this NPC."""
        if not self.dialog_id:
            return [DialoguePage("...", self.name)]
        
        # Load dialog from JSON
        dialog_file = Path("data/dialogs/npcs") / f"{self.dialog_id}.json"
        
        if dialog_file.exists():
            try:
                with open(dialog_file, 'r', encoding='utf-8') as f:
                    dialog_data = json.load(f)
                
                # Check conditions for different dialog branches
                pages = self._select_dialog_branch(dialog_data)
                return pages
                
            except Exception as e:
                print(f"[ManagedNPC] Failed to load dialog {dialog_file}: {e}")
        
        # Default dialog
        return [DialoguePage(f"Hello! I'm {self.name}.", self.name)]
    
    def _select_dialog_branch(self, dialog_data: Dict) -> List[DialoguePage]:
        """Select appropriate dialog branch based on conditions."""
        story = self.game.story_manager
        
        # Check for conditional branches
        if 'branches' in dialog_data:
            for branch in dialog_data['branches']:
                conditions = branch.get('conditions', {})
                if self._check_dialog_conditions(conditions):
                    return self._parse_dialog_pages(branch['pages'])
        
        # Use default pages
        if 'default' in dialog_data:
            return self._parse_dialog_pages(dialog_data['default'])
        
        return [DialoguePage("...", self.name)]
    
    def _check_dialog_conditions(self, conditions: Dict) -> bool:
        """Check if dialog conditions are met."""
        story = self.game.story_manager
        
        for cond_type, cond_value in conditions.items():
            if cond_type == 'flag':
                if isinstance(cond_value, str):
                    if cond_value.startswith('!'):
                        if story.get_flag(cond_value[1:]):
                            return False
                    else:
                        if not story.get_flag(cond_value):
                            return False
            elif cond_type == 'has_item':
                # TODO: Check inventory
                pass
        
        return True
    
    def _parse_dialog_pages(self, pages_data: List) -> List[DialoguePage]:
        """Parse dialog page data into DialoguePage objects."""
        pages = []
        for page in pages_data:
            if isinstance(page, str):
                # Simple text
                pages.append(DialoguePage(page, self.name))
            elif isinstance(page, dict):
                # Complex page with options
                text = page.get('text', '...')
                speaker = page.get('speaker', self.name)
                pages.append(DialoguePage(text, speaker))
        
        return pages


class NPCManager:
    """
    Manages all NPCs in the game world.
    Spawns NPCs from interaction data and handles their lifecycle.
    """
    
    def __init__(self, game):
        """
        Initialize the NPC Manager.
        
        Args:
            game: Reference to main game object
        """
        self.game = game
        self.active_npcs: List[ManagedNPC] = []
        self.npc_registry: Dict[str, ManagedNPC] = {}
        
    def spawn_npcs(self, interaction_data, area):
        """
        Spawn NPCs for a map from interaction data.
        
        Args:
            interaction_data: InteractionData object with NPC definitions
            area: The Area object to spawn NPCs in
        """
        # Clear existing NPCs
        self.clear_npcs()
        
        # Spawn each NPC from data
        for npc_data in interaction_data.npcs:
            # Check conditions
            if not self._check_spawn_conditions(npc_data.conditions):
                continue
            
            # Create NPC entity
            npc = ManagedNPC(npc_data, self.game)
            
            # Add to tracking
            self.active_npcs.append(npc)
            self.npc_registry[npc_data.id] = npc
            
            # Add to area
            area.entities.append(npc)
            area.npcs.append(npc)
            
            print(f"[NPCManager] Spawned NPC: {npc_data.id} at {npc_data.position}")
        
        print(f"[NPCManager] Total NPCs spawned: {len(self.active_npcs)}")
    
    def _check_spawn_conditions(self, conditions: Dict) -> bool:
        """Check if spawn conditions are met."""
        if not conditions:
            return True
        
        story = self.game.story_manager
        
        for cond_type, cond_value in conditions.items():
            if cond_type == 'flag':
                if isinstance(cond_value, str):
                    if cond_value.startswith('!'):
                        if story.get_flag(cond_value[1:]):
                            return False
                    else:
                        if not story.get_flag(cond_value):
                            return False
        
        return True
    
    def clear_npcs(self):
        """Clear all active NPCs."""
        self.active_npcs.clear()
        self.npc_registry.clear()
    
    def get_npc_by_id(self, npc_id: str) -> Optional[ManagedNPC]:
        """Get an NPC by its ID."""
        return self.npc_registry.get(npc_id)
    
    def get_npc_at_position(self, tile_x: int, tile_y: int) -> Optional[ManagedNPC]:
        """Get NPC at a specific tile position."""
        for npc in self.active_npcs:
            npc_tile_x = npc.x // TILE_SIZE
            npc_tile_y = npc.y // TILE_SIZE
            
            if npc_tile_x == tile_x and npc_tile_y == tile_y:
                return npc
        
        return None
    
    def update_all(self, dt: float):
        """Update all active NPCs."""
        for npc in self.active_npcs:
            npc.update(dt)
    
    def create_default_dialog_file(self, dialog_id: str):
        """Create a default dialog file for an NPC."""
        default_dialog = {
            "id": dialog_id,
            "default": [
                {
                    "text": "Hello there!",
                    "speaker": dialog_id.replace('_', ' ').title()
                }
            ],
            "branches": [
                {
                    "conditions": {
                        "flag": "example_flag"
                    },
                    "pages": [
                        {
                            "text": "Oh, you've done the thing!",
                            "speaker": dialog_id.replace('_', ' ').title()
                        }
                    ]
                }
            ]
        }
        
        # Ensure directory exists
        dialog_dir = Path("data/dialogs/npcs")
        dialog_dir.mkdir(parents=True, exist_ok=True)
        
        # Save dialog file
        dialog_file = dialog_dir / f"{dialog_id}.json"
        with open(dialog_file, 'w', encoding='utf-8') as f:
            json.dump(default_dialog, f, indent=2)
        
        print(f"[NPCManager] Created default dialog file: {dialog_file}")
