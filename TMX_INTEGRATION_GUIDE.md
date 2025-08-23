# TMX Map Integration - Implementation Guide

## Overview

The new TMX Map Integration system provides a clean separation between visual presentation (TMX files) and game logic (JSON files). This guide explains how to use the system and integrate it into your game.

## System Architecture

```
TMX Files (Visual Only)          JSON Files (Logic Only)
├── Tile layers                  ├── NPCs
├── Collision geometry           ├── Warps/Teleports  
├── Visual objects               ├── Interactive objects
└── Map properties               └── Triggers/Events
```

## File Structure

```
untold_story/
├── data/
│   ├── maps/                    # TMX files (visual only)
│   │   ├── player_house.tmx
│   │   ├── kohlenstadt.tmx
│   │   └── ...
│   ├── maps/interactions/       # Interaction data (logic)
│   │   ├── player_house.json
│   │   ├── kohlenstadt.json
│   │   └── ...
│   └── dialogs/                 # Dialog definitions
│       └── npcs/
│           ├── mom_dialog.json
│           ├── professor_dialog.json
│           └── ...
└── engine/
    └── world/
        ├── enhanced_map_manager.py   # Main orchestrator
        ├── interaction_manager.py    # Handles interactions
        └── npc_manager.py            # Manages NPCs
```

## Integration Steps

### 1. Update Your Field Scene

Replace the current map loading in `field_scene.py`:

```python
from engine.world.enhanced_map_manager import EnhancedMapManager

class FieldScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        # Initialize the enhanced map manager
        self.map_manager = EnhancedMapManager(game)
        # ... rest of initialization
    
    def load_map(self, map_name: str, spawn_x: int = 5, spawn_y: int = 5):
        """Load a map with the new system"""
        # Load map with visual and interaction data
        self.current_area = self.map_manager.load_map(map_name, spawn_x, spawn_y)
        
        # Update camera
        if self.camera:
            self.camera.set_world_size(
                self.current_area.width * TILE_SIZE,
                self.current_area.height * TILE_SIZE
            )
    
    def _handle_interaction(self, tile_pos: Tuple[int, int]):
        """Handle player interaction"""
        tile_x, tile_y = tile_pos
        # Use the map manager to check interactions
        self.map_manager.check_interaction(tile_x, tile_y)
    
    def _check_warp_at_position(self, tile_x: int, tile_y: int):
        """Check for warps"""
        self.map_manager.check_warp(tile_x, tile_y)
```

### 2. Create Interaction Files

For each TMX map, create a corresponding JSON file in `data/maps/interactions/`:

```json
{
  "map_id": "your_map_name",
  "npcs": [
    {
      "id": "npc_unique_id",
      "position": [tile_x, tile_y],
      "sprite": "npc_sprite.png",
      "dialog": "dialog_id",
      "movement": "static|random|patrol",
      "facing": "north|south|east|west",
      "conditions": {
        "flag": "story_flag_name"
      }
    }
  ],
  "warps": [
    {
      "id": "warp_id",
      "position": [tile_x, tile_y],
      "destination": {
        "map": "target_map",
        "position": [target_x, target_y],
        "facing": "south"
      },
      "type": "instant|door|stairs",
      "sound": "sound_effect_name"
    }
  ],
  "objects": [
    {
      "id": "object_id",
      "position": [tile_x, tile_y],
      "interaction": "examine|rest|save|item|activate",
      "dialog": "Text to display",
      "action": "action_name",
      "item": "item_name",
      "one_time": true
    }
  ],
  "triggers": [
    {
      "id": "trigger_id",
      "position": [tile_x, tile_y],
      "event": "dialog|cutscene|battle",
      "args": {
        "dialog_id": "dialog_name"
      },
      "conditions": {},
      "auto": true,
      "one_time": false
    }
  ]
}
```

### 3. Create Dialog Files

For each NPC dialog, create a JSON file in `data/dialogs/npcs/`:

```json
{
  "id": "dialog_id",
  "default": [
    {
      "text": "Default dialog text",
      "speaker": "NPC Name"
    }
  ],
  "branches": [
    {
      "conditions": {
        "flag": "story_flag"
      },
      "pages": [
        {
          "text": "Conditional dialog text",
          "speaker": "NPC Name"
        }
      ]
    }
  ]
}
```

## Using the System

### Loading a Map

```python
# Load a map with spawn position
area = map_manager.load_map('kohlenstadt', spawn_x=10, spawn_y=15)
```

### Checking Interactions

```python
# Check for interaction at player position
tile_x, tile_y = player.get_tile_position()
if map_manager.check_interaction(tile_x, tile_y):
    # Interaction handled
    pass
```

### Conditional NPCs

NPCs can have spawn conditions:

```json
{
  "id": "rival",
  "position": [20, 8],
  "conditions": {
    "flag": "has_starter",     // Only spawn if flag is true
    "flag": "!defeated_rival"  // Only spawn if flag is false (! prefix)
  }
}
```

### Movement Patterns

NPCs support three movement types:

1. **Static**: NPC doesn't move
2. **Random**: NPC moves randomly
3. **Patrol**: NPC follows a defined route

```json
{
  "movement": "patrol",
  "route": [[15, 8], [15, 10], [18, 10], [18, 8]]
}
```

## Best Practices

### 1. Keep TMX Files Visual-Only

✅ DO put in TMX:
- Tile layers (ground, decoration)
- Collision geometry
- Visual tile placement

❌ DON'T put in TMX:
- NPCs
- Warps
- Dialog triggers
- Game logic

### 2. Use Meaningful IDs

```json
// Good
"id": "professor_budde"
"id": "door_to_museum"
"id": "hidden_potion_forest"

// Bad
"id": "npc1"
"id": "warp_5"
"id": "obj_23"
```

### 3. Organize Dialogs

Create a folder structure for dialogs:
```
dialogs/
├── npcs/          # NPC dialogs
├── events/        # Event/cutscene dialogs
├── signs/         # Sign text
└── system/        # System messages
```

### 4. Test Conditions

Always test conditional spawning:
```python
# Set flag and reload map
game.story_manager.set_flag('has_starter', True)
area = map_manager.load_map('kohlenstadt')
# Check if conditional NPC spawned
```

## Migration from Old System

To migrate existing maps:

1. Keep your TMX files as-is
2. Create interaction JSON files for each map
3. Move NPC definitions from code to JSON
4. Move warp definitions from TMX objects to JSON
5. Update field_scene.py to use EnhancedMapManager

## Troubleshooting

### NPCs Not Spawning
- Check interaction file exists
- Verify position coordinates
- Check spawn conditions
- Ensure sprite file exists

### Warps Not Working
- Verify position matches player tile
- Check destination map exists
- Ensure destination coordinates are valid

### Dialogs Not Loading
- Check dialog file path
- Verify JSON syntax
- Check dialog ID matches

## Example: Complete Map Setup

### 1. TMX File (player_house.tmx)
- Contains visual tiles only
- Collision layer for walls
- No NPCs or warps

### 2. Interaction File (player_house.json)
```json
{
  "map_id": "player_house",
  "npcs": [{
    "id": "mom",
    "position": [5, 3],
    "sprite": "npc_woman_1.png",
    "dialog": "mom_dialog"
  }],
  "warps": [{
    "id": "door",
    "position": [4, 8],
    "destination": {
      "map": "kohlenstadt",
      "position": [10, 15]
    }
  }]
}
```

### 3. Dialog File (mom_dialog.json)
```json
{
  "id": "mom_dialog",
  "default": [{
    "text": "Good morning!",
    "speaker": "Mom"
  }]
}
```

## Benefits of This System

1. **Clean Separation**: Visual design separate from game logic
2. **Easy Editing**: Change NPCs/warps without touching TMX
3. **Version Control**: JSON files are diff-friendly
4. **Conditional Logic**: Easy to add story conditions
5. **Maintainable**: Clear structure and organization
6. **Extensible**: Easy to add new interaction types

## Next Steps

1. Integrate the system into your main game
2. Convert all existing maps to use interactions
3. Create dialog files for all NPCs
4. Test thoroughly with different story flags
5. Add more interaction types as needed

The system is designed to grow with your game while maintaining clean code and data separation!
