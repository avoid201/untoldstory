#!/usr/bin/env python3
"""
Patch to integrate the new TMX interaction system into the game
Run this to enable the new system in field_scene.py
"""

import sys
import os

def patch_field_scene():
    """Add the enhanced map manager to field scene"""
    
    print("Patching field_scene.py to use new TMX interaction system...")
    
    # Read the current field_scene.py
    field_scene_path = "engine/scenes/field_scene.py"
    with open(field_scene_path, 'r') as f:
        content = f.read()
    
    # Check if already patched
    if "EnhancedMapManager" in content:
        print("✅ Already patched!")
        return
    
    # Add import at the top
    import_line = "from engine.world.enhanced_map_manager import EnhancedMapManager"
    
    # Find where to insert the import
    import_pos = content.find("from engine.world.area import Area")
    if import_pos != -1:
        # Insert after the Area import
        end_of_line = content.find("\n", import_pos)
        content = content[:end_of_line+1] + import_line + "\n" + content[end_of_line+1:]
    
    # Add the enhanced map manager to __init__
    init_addition = """
        # NEW: Enhanced Map Manager for TMX/JSON separation
        self.use_enhanced_manager = True  # Set to False to use old system
        if self.use_enhanced_manager:
            try:
                self.map_manager = EnhancedMapManager(game)
                print("✅ Using Enhanced Map Manager with TMX/JSON separation")
            except Exception as e:
                print(f"⚠️ Enhanced Map Manager failed, using old system: {e}")
                self.use_enhanced_manager = False
"""
    
    # Find where to add in __init__
    init_pos = content.find("# Check if starter scene should be shown")
    if init_pos != -1:
        content = content[:init_pos] + init_addition + "\n        " + content[init_pos:]
    
    # Modify load_map to use new manager when available
    load_map_patch = """
        # NEW: Try to use Enhanced Map Manager if available
        if hasattr(self, 'use_enhanced_manager') and self.use_enhanced_manager and hasattr(self, 'map_manager'):
            try:
                print(f"[EnhancedMode] Loading map with new system: {map_name}")
                self.current_area = self.map_manager.load_map(map_name, spawn_x, spawn_y)
                self.map_id = map_name
                
                # Setup camera
                if not self.camera:
                    from engine.world.camera import Camera, CameraConfig
                    self.camera = Camera(
                        viewport_width=self.game.logical_size[0],
                        viewport_height=self.game.logical_size[1],
                        world_width=self.current_area.width * TILE_SIZE,
                        world_height=self.current_area.height * TILE_SIZE,
                        config=self.camera_config
                    )
                else:
                    self.camera.set_world_size(
                        self.current_area.width * TILE_SIZE,
                        self.current_area.height * TILE_SIZE
                    )
                
                # Create player if needed
                if not self.player:
                    self._initialize_player()
                
                # Set player position
                self.player.set_tile_position(spawn_x, spawn_y)
                
                # Center camera
                self.camera.center_on(
                    self.player.x + self.player.width // 2,
                    self.player.y + self.player.height // 2,
                    immediate=True
                )
                self.camera.set_follow_target(self.player)
                
                print(f"[EnhancedMode] Map loaded successfully!")
                return
                
            except Exception as e:
                print(f"[EnhancedMode] Failed to load with new system: {e}")
                print("[EnhancedMode] Falling back to old system...")
        
"""
    
    # Find where to insert in load_map
    load_map_pos = content.find('print(f"Loading map: {map_name}")')
    if load_map_pos != -1:
        end_of_line = content.find("\n", load_map_pos)
        content = content[:end_of_line+1] + "\n" + load_map_patch + content[end_of_line+1:]
    
    # Modify _handle_interaction to use new manager
    interaction_patch = """
        # NEW: Try enhanced interaction manager first
        if hasattr(self, 'use_enhanced_manager') and self.use_enhanced_manager and hasattr(self, 'map_manager'):
            if self.map_manager.check_interaction(tile_x, tile_y):
                return
        
"""
    
    # Find _handle_interaction method
    handle_pos = content.find("def _handle_interaction(self, tile_pos: Tuple[int, int])")
    if handle_pos != -1:
        # Find the first line after tile_x, tile_y = tile_pos
        tile_pos_line = content.find("tile_x, tile_y = tile_pos", handle_pos)
        if tile_pos_line != -1:
            end_of_line = content.find("\n", tile_pos_line)
            content = content[:end_of_line+1] + "\n" + interaction_patch + content[end_of_line+1:]
    
    # Write the patched file
    with open(field_scene_path, 'w') as f:
        f.write(content)
    
    print("✅ Patch applied successfully!")
    print("\nThe game will now:")
    print("1. Load visual data from TMX files")
    print("2. Load NPCs and interactions from JSON files")
    print("3. Use data-driven dialogs")
    print("\nYou can disable the new system by setting:")
    print("  self.use_enhanced_manager = False")
    print("in field_scene.py")

if __name__ == "__main__":
    patch_field_scene()
    print("\n🎮 Now run the game with: python3 main.py")
