"""
World State Management System for Untold Story
Tracks persistent world states like doors, switches, items collected, etc.
"""

from typing import Dict, Set, Any, Optional
from dataclasses import dataclass, field
import json
import os


@dataclass
class MapObjectState:
    """Represents the state of an interactive map object."""
    object_id: str
    object_type: str  # 'door', 'switch', 'item', 'npc'
    state: str        # 'open'/'closed', 'on'/'off', 'collected', 'active'
    properties: Dict[str, Any] = field(default_factory=dict)
    

class WorldState:
    """Manages persistent world state across game sessions."""
    
    def __init__(self):
        """Initialize world state."""
        self.map_states: Dict[str, Dict[str, MapObjectState]] = {}  # map_id -> object_id -> state
        self.global_flags: Dict[str, bool] = {}
        self.global_variables: Dict[str, Any] = {}
        self.story_progress: Dict[str, int] = {}
        
    def set_object_state(self, map_id: str, object_id: str, object_type: str, state: str, properties: Optional[Dict[str, Any]] = None):
        """Set state of a map object."""
        if map_id not in self.map_states:
            self.map_states[map_id] = {}
        
        self.map_states[map_id][object_id] = MapObjectState(
            object_id=object_id,
            object_type=object_type,
            state=state,
            properties=properties or {}
        )
        
    def get_object_state(self, map_id: str, object_id: str) -> Optional[MapObjectState]:
        """Get state of a map object."""
        if map_id in self.map_states:
            return self.map_states[map_id].get(object_id)
        return None
    
    def is_door_open(self, map_id: str, door_id: str) -> bool:
        """Check if a door is open."""
        state = self.get_object_state(map_id, door_id)
        return state and state.state == 'open'
    
    def set_door_state(self, map_id: str, door_id: str, is_open: bool):
        """Set door open/closed state."""
        state = 'open' if is_open else 'closed'
        self.set_object_state(map_id, door_id, 'door', state)
        
    def is_switch_on(self, map_id: str, switch_id: str) -> bool:
        """Check if a switch is on."""
        state = self.get_object_state(map_id, switch_id)
        return state and state.state == 'on'
    
    def set_switch_state(self, map_id: str, switch_id: str, is_on: bool):
        """Set switch on/off state."""
        state = 'on' if is_on else 'off'
        self.set_object_state(map_id, switch_id, 'switch', state)
        
    def toggle_switch(self, map_id: str, switch_id: str) -> bool:
        """Toggle switch state and return new state."""
        current_on = self.is_switch_on(map_id, switch_id)
        new_state = not current_on
        self.set_switch_state(map_id, switch_id, new_state)
        return new_state
    
    def is_item_collected(self, map_id: str, item_id: str) -> bool:
        """Check if an item has been collected."""
        state = self.get_object_state(map_id, item_id)
        return state and state.state == 'collected'
    
    def set_item_collected(self, map_id: str, item_id: str):
        """Mark an item as collected."""
        self.set_object_state(map_id, item_id, 'item', 'collected')
        
    def set_global_flag(self, flag_name: str, value: bool):
        """Set a global flag."""
        self.global_flags[flag_name] = value
        
    def get_global_flag(self, flag_name: str, default: bool = False) -> bool:
        """Get a global flag."""
        return self.global_flags.get(flag_name, default)
    
    def set_global_variable(self, var_name: str, value: Any):
        """Set a global variable."""
        self.global_variables[var_name] = value
        
    def get_global_variable(self, var_name: str, default: Any = None) -> Any:
        """Get a global variable."""
        return self.global_variables.get(var_name, default)
    
    def set_story_progress(self, story_id: str, progress: int):
        """Set story progress for a specific storyline."""
        self.story_progress[story_id] = progress
        
    def get_story_progress(self, story_id: str, default: int = 0) -> int:
        """Get story progress for a specific storyline."""
        return self.story_progress.get(story_id, default)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert world state to dictionary for saving."""
        map_states_dict = {}
        for map_id, objects in self.map_states.items():
            map_states_dict[map_id] = {
                obj_id: {
                    'object_type': obj.object_type,
                    'state': obj.state,
                    'properties': obj.properties
                }
                for obj_id, obj in objects.items()
            }
        
        return {
            'map_states': map_states_dict,
            'global_flags': self.global_flags,
            'global_variables': self.global_variables,
            'story_progress': self.story_progress
        }
    
    def from_dict(self, data: Dict[str, Any]):
        """Load world state from dictionary."""
        # Load map states
        map_states_data = data.get('map_states', {})
        self.map_states = {}
        
        for map_id, objects in map_states_data.items():
            self.map_states[map_id] = {}
            for obj_id, obj_data in objects.items():
                self.map_states[map_id][obj_id] = MapObjectState(
                    object_id=obj_id,
                    object_type=obj_data['object_type'],
                    state=obj_data['state'],
                    properties=obj_data.get('properties', {})
                )
        
        # Load other data
        self.global_flags = data.get('global_flags', {})
        self.global_variables = data.get('global_variables', {})
        self.story_progress = data.get('story_progress', {})
    
    def save_to_file(self, filepath: str):
        """Save world state to file."""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving world state: {e}")
    
    def load_from_file(self, filepath: str) -> bool:
        """Load world state from file."""
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.from_dict(data)
                return True
        except Exception as e:
            print(f"Error loading world state: {e}")
        return False


# Global world state instance
world_state = WorldState()

# Export for external use
__all__ = ['WorldState', 'MapObjectState', 'world_state']
