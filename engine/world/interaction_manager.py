# engine/world/interaction_manager.py
"""
Interaction Manager for Untold Story
Manages all interactive elements loaded from JSON data files
Provides clean separation between visual TMX and game logic
"""

import json
import pygame
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from engine.world.tiles import TILE_SIZE


@dataclass
class NPCData:
    """Data structure for NPC configuration"""
    id: str
    position: Tuple[int, int]  # Tile coordinates
    sprite: str
    dialog: str
    movement: str = "static"  # static, random, patrol
    facing: str = "south"
    conditions: Dict[str, Any] = field(default_factory=dict)
    route: List[Tuple[int, int]] = field(default_factory=list)


@dataclass
class WarpData:
    """Data structure for warp points"""
    id: str
    position: Tuple[int, int]  # Tile coordinates
    destination_map: str
    destination_position: Tuple[int, int]
    destination_facing: str = "south"
    type: str = "instant"  # instant, door, stairs
    sound: Optional[str] = None
    conditions: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ObjectData:
    """Data structure for interactive objects"""
    id: str
    position: Tuple[int, int]  # Tile coordinates
    interaction: str  # examine, collect, activate
    sprite: Optional[str] = None
    dialog: Optional[str] = None
    action: Optional[str] = None
    item: Optional[str] = None
    conditions: Dict[str, Any] = field(default_factory=dict)
    one_time: bool = False


@dataclass
class TriggerData:
    """Data structure for event triggers"""
    id: str
    position: Tuple[int, int]  # Tile coordinates
    event: str  # cutscene, battle, dialog
    args: Dict[str, Any] = field(default_factory=dict)
    conditions: Dict[str, Any] = field(default_factory=dict)
    auto: bool = True  # Auto-trigger when stepped on
    one_time: bool = False


@dataclass
class InteractionData:
    """Complete interaction data for a map"""
    map_id: str
    npcs: List[NPCData] = field(default_factory=list)
    warps: List[WarpData] = field(default_factory=list)
    objects: List[ObjectData] = field(default_factory=list)
    triggers: List[TriggerData] = field(default_factory=list)


class InteractionManager:
    """
    Manages all interactive elements in the game world.
    Loads interaction data from JSON files separate from TMX visual data.
    """
    
    def __init__(self, game):
        """
        Initialize the Interaction Manager.
        
        Args:
            game: Reference to the main game object
        """
        self.game = game
        self.interactions_cache: Dict[str, InteractionData] = {}
        self.active_interactions: Optional[InteractionData] = None
        self.interaction_states: Dict[str, bool] = {}  # Track one-time interactions
        
        # Paths for data files
        self.interactions_path = Path("data/maps/interactions")
        self.dialogs_path = Path("data/dialogs")
        
        # Create directories if they don't exist
        self.interactions_path.mkdir(parents=True, exist_ok=True)
        self.dialogs_path.mkdir(parents=True, exist_ok=True)
        
    def load_interactions(self, map_id: str) -> InteractionData:
        """
        Load interaction data for a specific map.
        
        Args:
            map_id: The map identifier
            
        Returns:
            InteractionData object with all interactive elements
        """
        # Check cache first
        if map_id in self.interactions_cache:
            self.active_interactions = self.interactions_cache[map_id]
            return self.active_interactions
        
        # Load from JSON file
        interaction_file = self.interactions_path / f"{map_id}.json"
        
        if interaction_file.exists():
            try:
                with open(interaction_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                interactions = self._parse_interaction_data(map_id, data)
                self.interactions_cache[map_id] = interactions
                self.active_interactions = interactions
                
                print(f"[InteractionManager] Loaded interactions for {map_id}:")
                print(f"  - NPCs: {len(interactions.npcs)}")
                print(f"  - Warps: {len(interactions.warps)}")
                print(f"  - Objects: {len(interactions.objects)}")
                print(f"  - Triggers: {len(interactions.triggers)}")
                
                return interactions
                
            except Exception as e:
                print(f"[InteractionManager] Error loading {interaction_file}: {e}")
        else:
            print(f"[InteractionManager] No interaction file for {map_id}, creating empty")
        
        # Return empty interaction data
        empty = InteractionData(map_id=map_id)
        self.interactions_cache[map_id] = empty
        self.active_interactions = empty
        return empty
    
    def _parse_interaction_data(self, map_id: str, data: Dict) -> InteractionData:
        """
        Parse JSON data into InteractionData structure.
        
        Args:
            map_id: Map identifier
            data: Raw JSON data
            
        Returns:
            Parsed InteractionData object
        """
        interactions = InteractionData(map_id=map_id)
        
        # Parse NPCs
        for npc_data in data.get('npcs', []):
            npc = NPCData(
                id=npc_data['id'],
                position=tuple(npc_data['position']),
                sprite=npc_data.get('sprite', 'npc_01.png'),
                dialog=npc_data.get('dialog', ''),
                movement=npc_data.get('movement', 'static'),
                facing=npc_data.get('facing', 'south'),
                conditions=npc_data.get('conditions', {}),
                route=npc_data.get('route', [])
            )
            interactions.npcs.append(npc)
        
        # Parse Warps
        for warp_data in data.get('warps', []):
            warp = WarpData(
                id=warp_data['id'],
                position=tuple(warp_data['position']),
                destination_map=warp_data['destination']['map'],
                destination_position=tuple(warp_data['destination']['position']),
                destination_facing=warp_data['destination'].get('facing', 'south'),
                type=warp_data.get('type', 'instant'),
                sound=warp_data.get('sound'),
                conditions=warp_data.get('conditions', {})
            )
            interactions.warps.append(warp)
        
        # Parse Objects
        for obj_data in data.get('objects', []):
            obj = ObjectData(
                id=obj_data['id'],
                position=tuple(obj_data['position']),
                interaction=obj_data.get('interaction', 'examine'),
                sprite=obj_data.get('sprite'),
                dialog=obj_data.get('dialog'),
                action=obj_data.get('action'),
                item=obj_data.get('item'),
                conditions=obj_data.get('conditions', {}),
                one_time=obj_data.get('one_time', False)
            )
            interactions.objects.append(obj)
        
        # Parse Triggers
        for trigger_data in data.get('triggers', []):
            trigger = TriggerData(
                id=trigger_data['id'],
                position=tuple(trigger_data['position']),
                event=trigger_data['event'],
                args=trigger_data.get('args', {}),
                conditions=trigger_data.get('conditions', {}),
                auto=trigger_data.get('auto', True),
                one_time=trigger_data.get('one_time', False)
            )
            interactions.triggers.append(trigger)
        
        return interactions
    
    def check_conditions(self, conditions: Dict[str, Any]) -> bool:
        """
        Check if conditions are met for an interaction.
        
        Args:
            conditions: Dictionary of conditions to check
            
        Returns:
            True if all conditions are met
        """
        if not conditions:
            return True
        
        story = self.game.story_manager
        
        for condition_type, condition_value in conditions.items():
            if condition_type == 'flag':
                # Check story flag
                if isinstance(condition_value, str):
                    if condition_value.startswith('!'):
                        # Negative flag check
                        if story.get_flag(condition_value[1:]):
                            return False
                    else:
                        # Positive flag check
                        if not story.get_flag(condition_value):
                            return False
                            
            elif condition_type == 'item':
                # Check if player has item
                # TODO: Implement inventory check
                pass
                
            elif condition_type == 'variable':
                # Check game variable
                var_name, var_value = condition_value.split(':')
                if story.variables.get(var_name) != var_value:
                    return False
        
        return True
    
    def get_npc_at(self, tile_x: int, tile_y: int) -> Optional[NPCData]:
        """
        Get NPC at specific tile position.
        
        Args:
            tile_x: Tile X coordinate
            tile_y: Tile Y coordinate
            
        Returns:
            NPCData if found, None otherwise
        """
        if not self.active_interactions:
            return None
        
        for npc in self.active_interactions.npcs:
            if npc.position == (tile_x, tile_y):
                if self.check_conditions(npc.conditions):
                    return npc
        
        return None
    
    def get_warp_at(self, tile_x: int, tile_y: int) -> Optional[WarpData]:
        """
        Get warp at specific tile position.
        
        Args:
            tile_x: Tile X coordinate
            tile_y: Tile Y coordinate
            
        Returns:
            WarpData if found, None otherwise
        """
        if not self.active_interactions:
            return None
        
        for warp in self.active_interactions.warps:
            if warp.position == (tile_x, tile_y):
                if self.check_conditions(warp.conditions):
                    return warp
        
        return None
    
    def get_object_at(self, tile_x: int, tile_y: int) -> Optional[ObjectData]:
        """
        Get interactive object at specific tile position.
        
        Args:
            tile_x: Tile X coordinate
            tile_y: Tile Y coordinate
            
        Returns:
            ObjectData if found, None otherwise
        """
        if not self.active_interactions:
            return None
        
        for obj in self.active_interactions.objects:
            if obj.position == (tile_x, tile_y):
                if self.check_conditions(obj.conditions):
                    # Check if one-time interaction already used
                    if obj.one_time and self.interaction_states.get(f"{self.active_interactions.map_id}_{obj.id}"):
                        continue
                    return obj
        
        return None
    
    def get_trigger_at(self, tile_x: int, tile_y: int) -> Optional[TriggerData]:
        """
        Get trigger at specific tile position.
        
        Args:
            tile_x: Tile X coordinate
            tile_y: Tile Y coordinate
            
        Returns:
            TriggerData if found, None otherwise
        """
        if not self.active_interactions:
            return None
        
        for trigger in self.active_interactions.triggers:
            if trigger.position == (tile_x, tile_y):
                if self.check_conditions(trigger.conditions):
                    # Check if one-time trigger already used
                    if trigger.one_time and self.interaction_states.get(f"{self.active_interactions.map_id}_{trigger.id}"):
                        continue
                    return trigger
        
        return None
    
    def mark_interaction_used(self, interaction_id: str):
        """
        Mark a one-time interaction as used.
        
        Args:
            interaction_id: ID of the interaction
        """
        if self.active_interactions:
            key = f"{self.active_interactions.map_id}_{interaction_id}"
            self.interaction_states[key] = True
    
    def get_all_npcs(self) -> List[NPCData]:
        """Get all NPCs for current map."""
        if self.active_interactions:
            return [npc for npc in self.active_interactions.npcs 
                   if self.check_conditions(npc.conditions)]
        return []
    
    def get_all_objects(self) -> List[ObjectData]:
        """Get all interactive objects for current map."""
        if self.active_interactions:
            return [obj for obj in self.active_interactions.objects 
                   if self.check_conditions(obj.conditions)]
        return []
    
    def create_default_interaction_file(self, map_id: str):
        """
        Create a default interaction file for a map.
        
        Args:
            map_id: Map identifier
        """
        default_data = {
            "map_id": map_id,
            "npcs": [],
            "warps": [],
            "objects": [],
            "triggers": []
        }
        
        # Add example entries based on map
        if map_id == "player_house":
            default_data["npcs"] = [
                {
                    "id": "mom",
                    "position": [5, 3],
                    "sprite": "npc_woman_1.png",
                    "dialog": "mom_morning",
                    "movement": "static",
                    "facing": "south"
                }
            ]
            default_data["warps"] = [
                {
                    "id": "door_outside",
                    "position": [4, 8],
                    "destination": {
                        "map": "kohlenstadt",
                        "position": [10, 15],
                        "facing": "south"
                    },
                    "type": "door",
                    "sound": "door_open"
                }
            ]
            default_data["objects"] = [
                {
                    "id": "bed",
                    "position": [2, 2],
                    "interaction": "rest",
                    "dialog": "Would you like to rest?",
                    "action": "heal_party"
                }
            ]
        
        # Save to file
        interaction_file = self.interactions_path / f"{map_id}.json"
        with open(interaction_file, 'w', encoding='utf-8') as f:
            json.dump(default_data, f, indent=2)
        
        print(f"[InteractionManager] Created default interaction file: {interaction_file}")
