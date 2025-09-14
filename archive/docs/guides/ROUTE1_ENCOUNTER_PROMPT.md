# 🎮 UNTOLD STORY - ROUTE 1 ENCOUNTER IMPLEMENTATION PROMPT

## 📋 CONTEXT AND MISSION

You are Claude Opus 4.1, an expert game developer specializing in Python, pygame, and RPG mechanics. You need to help implement functional wild monster encounters on Route 1 in the "Untold Story" RPG game.

### Current Situation:
- The game is a 2D top-down RPG inspired by Pokémon and Dragon Quest Monsters
- The encounter system is partially implemented but NOT working on Route 1
- Players should encounter wild monsters when walking through grass tiles
- The game uses a tile-based movement system with 16x16 pixel tiles

## 🔍 TECHNICAL ANALYSIS

### PROBLEM 1: Map Name Mismatch
**Current Code (field_scene.py line 246):**
```python
if self.map_id == "route_1":
```

**Actual Map File:** `route1.json` (without underscore)

### PROBLEM 2: Grass Tile ID Mismatch
**Current Code (field_scene.py line 895):**
```python
# Check für Gras-Tiles (2, 5)
if tile_type in [2, 5]:
```

**Actual Grass Tiles in route1.json:** Tile ID 29 (based on map data analysis)

### PROBLEM 3: Area.get_tile_type() Method Missing
The method `self.current_area.get_tile_type(tile_x, tile_y)` is called but not implemented in the Area class.

## 🎯 IMPLEMENTATION REQUIREMENTS

### 1. Fix Map Name Recognition
Change all references from `"route_1"` to `"route1"` to match the actual file name.

### 2. Implement get_tile_type() Method
Add to `engine/world/area.py`:
```python
def get_tile_type(self, tile_x: int, tile_y: int) -> int:
    """
    Get the tile type at the specified tile coordinates.
    Returns the tile ID from the ground layer.
    """
    if not self.map_data:
        return 0
    
    # Check bounds
    if tile_x < 0 or tile_y < 0 or tile_x >= self.map_data.width or tile_y >= self.map_data.height:
        return 0
    
    # Get ground layer
    ground_layer = self.map_data.layers.get('Tile Layer 1', [])
    if not ground_layer:
        return 0
    
    # Calculate index
    index = tile_y * self.map_data.width + tile_x
    if index < len(ground_layer):
        return ground_layer[index]
    
    return 0
```

### 3. Update Grass Tile Detection
Change the grass tile check to use the correct tile ID:
```python
# Check for grass tiles (29 is grass in route1)
GRASS_TILES = [29]  # Add at class level
if tile_type in GRASS_TILES:
```

### 4. Ensure Encounter Table Creation
The `_create_route_1_encounter_table()` should properly load monsters from `data/monsters.json`:

```python
def _create_route_1_encounter_table(self):
    """Create encounter table for Route 1 with F and E rank monsters."""
    try:
        # Load monster data
        monsters_data = self.game.resources.load_json("monsters.json", from_data=True)
        if not monsters_data:
            print("[DEBUG] No monsters.json found!")
            return self._get_fallback_encounter_table()
        
        # Filter by rank
        f_rank = [m for m in monsters_data if m.get("rank") == "F"]
        e_rank = [m for m in monsters_data if m.get("rank") == "E"]
        
        if not f_rank or not e_rank:
            print(f"[DEBUG] Missing ranks: F={len(f_rank)}, E={len(e_rank)}")
            return self._get_fallback_encounter_table()
        
        # Select monsters for encounters
        selected_f = random.sample(f_rank, min(8, len(f_rank)))
        selected_e = random.sample(e_rank, min(2, len(e_rank)))
        
        encounter_table = []
        
        # 95% chance for F-rank (distribute weight)
        for monster in selected_f:
            encounter_table.append({
                "species_id": monster["id"],
                "name": monster["name"],
                "level_min": 3,
                "level_max": 6,
                "weight": 12,  # ~95% total for F-rank
                "rank": "F"
            })
        
        # 5% chance for E-rank
        for monster in selected_e:
            encounter_table.append({
                "species_id": monster["id"],
                "name": monster["name"],
                "level_min": 5,
                "level_max": 8,
                "weight": 2,  # ~5% total for E-rank
                "rank": "E"
            })
        
        print(f"[DEBUG] Route 1 encounters: {len(selected_f)} F-rank, {len(selected_e)} E-rank")
        return encounter_table
        
    except Exception as e:
        print(f"[ERROR] Failed to create encounter table: {e}")
        import traceback
        traceback.print_exc()
        return self._get_fallback_encounter_table()
```

### 5. Adjust Encounter Rate
Increase the encounter rate for better testing:
```python
if self.map_id == "route1":  # Fixed name
    self.current_area.encounter_table = self._create_route_1_encounter_table()
    self.current_area.encounter_rate = 0.25  # 25% chance (was 12%)
```

## 📝 FILES TO MODIFY

1. **engine/scenes/field_scene.py**
   - Line 246: Change `"route_1"` to `"route1"`
   - Line 895: Update grass tile IDs to `[29]`
   - Line 248: Increase encounter rate to 0.25
   - Update `_create_route_1_encounter_table()` method

2. **engine/world/area.py**
   - Add `get_tile_type()` method implementation

3. **data/game_data/warps.json** (if needed)
   - Add warp from kohlenstadt to route1

## 🧪 TESTING PROCEDURE

1. Start the game: `python3 main.py`
2. Complete the starter selection
3. Navigate to Route 1 (might need to add a warp)
4. Walk on grass tiles (the darker green areas)
5. Verify encounters trigger after ~4 steps on average
6. Check console for debug messages

## 🐛 DEBUG HELPERS

Add these debug prints to verify functionality:

```python
# In _check_encounter()
print(f"[DEBUG] Tile ({tile_x}, {tile_y}) = Type {tile_type}")
print(f"[DEBUG] Steps: {self.steps_since_encounter}, Rate: {self.current_area.encounter_rate}")

# In _generate_wild_monster()
print(f"[DEBUG] Encounter table size: {len(self.current_area.encounter_table)}")
print(f"[DEBUG] Generated: {wild_monster.species_name} Lv.{wild_monster.level}")
```

## ✅ SUCCESS CRITERIA

- [ ] Walking on grass tiles (ID 29) triggers encounter checks
- [ ] Encounters occur roughly every 4 steps (25% chance)
- [ ] 95% of encounters are F-rank monsters (levels 3-6)
- [ ] 5% of encounters are E-rank monsters (levels 5-8)
- [ ] Battle scene loads correctly with wild monster
- [ ] No crashes or errors in console

## 💡 ADDITIONAL NOTES

- The Ruhrpott dialect should be maintained in any dialog additions
- Monster data is stored in `data/monsters.json`
- The game uses a weighted random system for encounter selection
- Consider adding a visual indicator (like rustling grass) in future iterations

## 🚀 IMPLEMENTATION STRATEGY

1. **First:** Fix the map name mismatch (route_1 → route1)
2. **Second:** Implement the missing get_tile_type() method
3. **Third:** Update grass tile IDs to match the actual map
4. **Fourth:** Test basic encounters work
5. **Fifth:** Fine-tune encounter rates and monster distribution

Please implement these changes step by step, testing after each modification to ensure stability. Focus on getting basic encounters working first before optimizing the experience.

---

**Remember:** The game should feel like classic Dragon Quest Monsters with Pokémon-style wild encounters, set in the German Ruhrpott region with appropriate dialect and atmosphere.