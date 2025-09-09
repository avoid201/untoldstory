# ARCHIVED: 2025-01-03 - Replaced by engine/world/map_loader.py
# engine/world/enhanced_map_manager.py
"""
Enhanced Map Manager for Untold Story
Orchestrates loading of TMX visual data and JSON interaction data
Provides clean separation of concerns between visuals and game logic

FUNCTIONS MERGED INTO: engine/world/map_loader.py
- Enhanced functionality integrated into MapLoader class
- Interaction handling methods added
- Map transition callbacks preserved
"""

import pygame
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Optional, Tuple, List, Any
from engine.world.area import Area
from engine.world.map_loader import MapLoader, MapData
from engine.world.interaction_manager import InteractionManager, WarpData
from engine.world.npc_manager import NPCManager
from engine.world.tiles import TILE_SIZE
from engine.ui.dialogue import DialoguePage


class EnhancedMapManager:
    """
    Enhanced map management system that properly separates visual (TMX) 
    and logic (JSON) data for clean, maintainable map creation.
    """
    
    def __init__(self, game):
        """
        Initialize the Enhanced Map Manager.
        
        Args:
            game: Reference to main game object
        """
        self.game = game
        self.current_area: Optional[Area] = None
        self.current_map_id: str = ""
        
        # Sub-managers
        self.interaction_manager = InteractionManager(game)
        self.npc_manager = NPCManager(game)
        
        # Map transition callbacks
        self.on_map_enter_callbacks = {}
        self.on_map_exit_callbacks = {}
        
        # Object interaction handlers
        self.object_handlers = {
            'rest': self._handle_rest_object,
            'save': self._handle_save_object,
            'item': self._handle_item_object,
            'examine': self._handle_examine_object,
            'activate': self._handle_activate_object
        }
        
        print("[EnhancedMapManager] Initialized with separation of concerns")
    
    def load_map(self, map_id: str, spawn_x: int = None, spawn_y: int = None) -> Area:
        """
        Load a complete map with both visual (TMX) and interaction (JSON) data.
        
        Args:
            map_id: Map identifier
            spawn_x: Optional spawn X position in tiles
            spawn_y: Optional spawn Y position in tiles
            
        Returns:
            Fully configured Area object
        """
        print(f"\n[EnhancedMapManager] Loading map: {map_id}")
        print("=" * 50)
        
        # Call exit callback for previous map
        if self.current_map_id and self.current_map_id in self.on_map_exit_callbacks:
            self.on_map_exit_callbacks[self.current_map_id]()
        
        # Step 1: Load visual data from TMX
        print("[Step 1] Loading TMX visual data...")
        area = self._load_tmx_visuals(map_id)
        
        # Step 2: Load interaction data from JSON
        print("[Step 2] Loading JSON interaction data...")
        interactions = self.interaction_manager.load_interactions(map_id)
        
        # Step 3: Apply collision layer from TMX
        print("[Step 3] Setting up collision...")
        self._setup_collision(area)
        
        # Step 4: Spawn NPCs from interaction data
        print("[Step 4] Spawning NPCs...")
        self.npc_manager.spawn_npcs(interactions, area)
        
        # Step 5: Setup warps (store in area for easy access)
        print("[Step 5] Setting up warps...")
        area.warps = interactions.warps
        
        # Step 6: Setup interactive objects
        print("[Step 6] Setting up interactive objects...")
        area.objects = interactions.objects
        
        # Step 7: Setup triggers
        print("[Step 7] Setting up triggers...")
        area.triggers = interactions.triggers
        
        # Store references
        self.current_area = area
        self.current_map_id = map_id
        
        # Position player if coordinates provided
        if spawn_x is not None and spawn_y is not None and hasattr(self.game, 'player'):
            self.game.player.set_tile_position(spawn_x, spawn_y)
            print(f"[Step 8] Player positioned at ({spawn_x}, {spawn_y})")
        
        # Call enter callback for new map
        if map_id in self.on_map_enter_callbacks:
            self.on_map_enter_callbacks[map_id]()
        
        print(f"[EnhancedMapManager] Map '{map_id}' loaded successfully!")
        print("=" * 50 + "\n")
        
        return area
    
    def _load_tmx_visuals(self, map_id: str) -> Area:
        """
        Load only the visual components from TMX file.
        
        Args:
            map_id: Map identifier
            
        Returns:
            Area with visual layers loaded
        """
        # Use the existing Area class which handles TMX loading
        area = Area(map_id)
        
        # Ensure we have the visual layers
        if not hasattr(area, 'layer_surfaces') or not area.layer_surfaces:
            print(f"[EnhancedMapManager] Warning: No visual layers found for {map_id}")
            # Create a basic grass field as fallback
            self._create_fallback_visuals(area)
        
        return area
    
    def _create_fallback_visuals(self, area: Area):
        """Create fallback visual layers if TMX loading fails."""
        width = getattr(area, 'width', 20)
        height = getattr(area, 'height', 15)
        
        # Create a simple grass surface
        surface = pygame.Surface((width * TILE_SIZE, height * TILE_SIZE))
        surface.fill((34, 139, 34))  # Green grass color
        
        # Add some variation
        for y in range(height):
            for x in range(width):
                if (x + y) % 3 == 0:
                    rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    pygame.draw.rect(surface, (44, 149, 44), rect)
        
        area.layer_surfaces = {'ground': surface}
        print("[EnhancedMapManager] Created fallback visuals")
    
    def _setup_collision(self, area: Area):
        """Setup collision detection for the area."""
        # The collision should come from TMX collision layer
        if hasattr(area, 'map_data') and area.map_data:
            collision_layer = area.map_data.layers.get('collision', [])
            if collision_layer:
                # Store collision data in area for easy access
                area.collision_map = collision_layer
                print(f"  - Collision layer: {len(collision_layer)}x{len(collision_layer[0]) if collision_layer else 0}")
                return
        
        # Create empty collision map as fallback
        width = getattr(area, 'width', 20)
        height = getattr(area, 'height', 15)
        area.collision_map = [[0] * width for _ in range(height)]
        print("  - Created empty collision map")
    
    def check_interaction(self, tile_x: int, tile_y: int) -> bool:
        """
        Check for and execute interaction at a tile position.
        
        Args:
            tile_x: Tile X coordinate
            tile_y: Tile Y coordinate
            
        Returns:
            True if interaction was found and executed
        """
        # Check NPCs first
        npc = self.npc_manager.get_npc_at_position(tile_x, tile_y)
        if npc:
            self._interact_with_npc(npc)
            return True
        
        # Check interactive objects
        obj = self.interaction_manager.get_object_at(tile_x, tile_y)
        if obj:
            self._interact_with_object(obj)
            return True
        
        # Check manual triggers (non-auto)
        trigger = self.interaction_manager.get_trigger_at(tile_x, tile_y)
        if trigger and not trigger.auto:
            self._execute_trigger(trigger)
            return True
        
        return False
    
    def check_warp(self, tile_x: int, tile_y: int) -> bool:
        """
        Check for and execute warp at a tile position.
        
        Args:
            tile_x: Tile X coordinate
            tile_y: Tile Y coordinate
            
        Returns:
            True if warp was found and executed
        """
        warp = self.interaction_manager.get_warp_at(tile_x, tile_y)
        if warp:
            self._execute_warp(warp)
            return True
        return False
    
    def check_auto_trigger(self, tile_x: int, tile_y: int) -> bool:
        """
        Check for automatic triggers at a tile position.
        
        Args:
            tile_x: Tile X coordinate
            tile_y: Tile Y coordinate
            
        Returns:
            True if auto-trigger was found and executed
        """
        trigger = self.interaction_manager.get_trigger_at(tile_x, tile_y)
        if trigger and trigger.auto:
            self._execute_trigger(trigger)
            return True
        return False
    
    def _interact_with_npc(self, npc):
        """Handle interaction with an NPC."""
        print(f"[EnhancedMapManager] Interacting with NPC: {npc.npc_id}")
        
        # Prevent interaction if dialogue is already active
        if hasattr(self.game, 'current_scene') and hasattr(self.game.current_scene, 'dialogue_box'):
            if self.game.current_scene.dialogue_box.is_open():
                return
        
        # Get dialog pages
        pages = npc.get_dialogue_pages()
        
        # Show dialog
        if hasattr(self.game, 'current_scene') and hasattr(self.game.current_scene, 'dialogue_box'):
            # Lock player movement during dialog
            if hasattr(self.game.current_scene, 'player') and self.game.current_scene.player:
                self.game.current_scene.player.lock_movement(True)
            
            self.game.current_scene.dialogue_box.show_dialogue(
                                            pages,
                            callback=lambda result: self._on_npc_dialog_complete(npc.npc_id, result)
                        )
    
    def _interact_with_object(self, obj):
        """Handle interaction with an object."""
        print(f"[EnhancedMapManager] Interacting with object: {obj.id}")
        
        # Prevent interaction if dialogue is already active
        if hasattr(self.game, 'current_scene') and hasattr(self.game.current_scene, 'dialogue_box'):
            if self.game.current_scene.dialogue_box.is_open():
                return
        
        # Get handler for interaction type
        handler = self.object_handlers.get(obj.interaction, self._handle_examine_object)
        handler(obj)
        
        # Mark as used if one-time
        if obj.one_time:
            self.interaction_manager.mark_interaction_used(obj.id)
    
    def _execute_trigger(self, trigger):
        """Execute a trigger event."""
        print(f"[EnhancedMapManager] Executing trigger: {trigger.id}")
        
        # Prevent trigger execution if dialogue is already active
        if hasattr(self.game, 'current_scene') and hasattr(self.game.current_scene, 'dialogue_box'):
            if self.game.current_scene.dialogue_box.is_open():
                return
        
        if trigger.event == 'cutscene':
            self._start_cutscene(trigger.args.get('cutscene_id'))
        elif trigger.event == 'battle':
            self._start_battle(trigger.args)
        elif trigger.event == 'dialog':
            self._show_dialog(trigger.args.get('dialog_id'))
        
        # Mark as used if one-time
        if trigger.one_time:
            self.interaction_manager.mark_interaction_used(trigger.id)
    
    def _execute_warp(self, warp: WarpData):
        """Execute a warp to another map."""
        print(f"[EnhancedMapManager] Warping to {warp.destination_map}")
        
        # Prevent warp execution if dialogue is already active
        if hasattr(self.game, 'current_scene') and hasattr(self.game.current_scene, 'dialogue_box'):
            if self.game.current_scene.dialogue_box.is_open():
                return
        
        # Play warp sound if specified
        if warp.sound:
            # Play sound effect for interactions
            try:
                # Play appropriate sound based on interaction type
                sound_file = None
                if 'door' in trigger.trigger_type.lower():
                    sound_file = "door_open.wav"
                elif 'item' in trigger.trigger_type.lower() or 'pickup' in trigger.trigger_type.lower():
                    sound_file = "item_get.wav"
                elif 'warp' in trigger.trigger_type.lower() or 'transition' in trigger.trigger_type.lower():
                    sound_file = "warp.wav"
                elif 'switch' in trigger.trigger_type.lower():
                    sound_file = "switch.wav"
                else:
                    sound_file = "confirm.wav"  # Default interaction sound
                    
                # Try to play the sound
                if sound_file and hasattr(self.game, 'resources'):
                    sound = self.game.resources.load_sound(sound_file, volume=0.7)
                    if sound:
                        sound.play()
                        print(f"[SFX] Played sound: {sound_file}")
            except Exception as e:
                print(f"[SFX] Could not play interaction sound: {e}")
                # Silently continue if sound fails - nicht kritisch
        
        # Perform warp based on type
        if warp.type == 'instant':
            # Instant warp
            self.load_map(
                warp.destination_map,
                warp.destination_position[0],
                warp.destination_position[1]
            )
        else:
            # Transition warp (door, stairs, etc.)
            from engine.world.map_transition import MapTransition
            warp_data = {
                'target_map': warp.destination_map,
                'spawn_x': warp.destination_position[0],
                'spawn_y': warp.destination_position[1],
                'direction': warp.destination_facing,
                'transition_type': warp.type
            }
            MapTransition.execute_transition(self.game, warp_data)
    
    # Object interaction handlers
    def _handle_rest_object(self, obj):
        """Handle rest/healing object."""
        if hasattr(self.game, 'party_manager'):
            # Heal party
            for monster in self.game.party_manager.party.monsters:
                if monster:
                    monster.hp = monster.max_hp
            
            # Show message
            self._show_message("Your party has been fully healed!")
    
    def _handle_save_object(self, obj):
        """Handle save point object."""
        try:
            # Implementiere Speichersystem
            if hasattr(self.game, 'save_game'):
                save_success = self.game.save_game()
                if save_success:
                    self._show_message("Spiel erfolgreich gespeichert!")
                else:
                    self._show_message("Fehler beim Speichern des Spiels!")
            else:
                # Fallback: Verwende den StoryManager
                if hasattr(self.game, 'story_manager'):
                    self.game.story_manager.save_progress()
                    self._show_message("Spielstand gespeichert!")
                else:
                    self._show_message("Speichersystem nicht verfügbar!")
        except Exception as e:
            print(f"[EnhancedMapManager] Save error: {e}")
            self._show_message("Fehler beim Speichern!")
    
    def _handle_item_object(self, obj):
        """Handle item pickup."""
        if obj.item:
            # Add item to player's inventory using the complete Item system
            try:
                from engine.systems.items import ItemRegistry
                
                # Use item_registry directly instead of game.item_database
                from engine.systems.items import item_registry
                item_db = item_registry
                
                # Get the item
                item = item_db.get_item(obj.item)
                
                if item:
                    # Add to inventory
                    if hasattr(self.game, 'inventory') and self.game.inventory:
                        success = self.game.inventory.add_item(obj.item, 1)
                        if success:
                            self._show_message(f"Du hast {item.name} gefunden!")
                            # Remove item from map (mark as collected)
                            obj.collected = True
                        else:
                            self._show_message(f"Inventar voll! Konnte {item.name} nicht aufheben.")
                    else:
                        # Fallback: Just show message if no inventory system
                        self._show_message(f"Du hast {item.name} gefunden! (Kein Inventar-System)")
                else:
                    # Item not found in database - show generic message
                    self._show_message(f"Du hast {obj.item} gefunden!")
                    
            except Exception as e:
                # Graceful fallback if item system fails
                print(f"Item system error: {e}")
                self._show_message(f"Du hast etwas gefunden!")
    
    def _handle_examine_object(self, obj):
        """Handle examine/read object."""
        if obj.dialog:
            self._show_message(obj.dialog)
        else:
            self._show_message("There's nothing interesting here.")
    
    def _handle_activate_object(self, obj):
        """Handle activate/switch object with complete Action system."""
        if obj.action:
            # Execute action using the proper World State and Cutscene systems
            try:
                from engine.systems.world_state import world_state
                
                # Get current map ID
                current_map = getattr(self.game.current_scene, 'map_id', 'unknown')
                
                if obj.action == 'open_door':
                    # Get door ID from object properties
                    door_id = getattr(obj, 'id', f"door_{obj.x}_{obj.y}")
                    
                    # Check if door is already open
                    if world_state.is_door_open(current_map, door_id):
                        self._show_message("Die Tür ist bereits offen.")
                        return
                    
                    # Create and execute door open action
                    door_action = CutsceneAction(
                        action_type='open_door',
                        params={
                            'door_id': door_id,
                            'map_id': current_map,
                            'sound_file': getattr(obj, 'sound', 'door_open.wav')
                        }
                    )
                    
                    self._execute_immediate_action(door_action)
                    self._show_message("Die Tür öffnet sich.")
                    
                elif obj.action == 'toggle_switch':
                    # Get switch ID from object properties
                    switch_id = getattr(obj, 'id', f"switch_{obj.x}_{obj.y}")
                    
                    # Get current switch state
                    current_state = world_state.is_switch_on(current_map, switch_id)
                    
                    # Create and execute switch toggle action
                    switch_action = CutsceneAction(
                        action_type='toggle_switch',
                        params={
                            'switch_id': switch_id,
                            'map_id': current_map,
                            'sound_file': getattr(obj, 'sound', 'switch_toggle.wav'),
                            'effects': getattr(obj, 'effects', [])
                        }
                    )
                    
                    self._execute_immediate_action(switch_action)
                    
                    # Show appropriate message
                    new_state = world_state.is_switch_on(current_map, switch_id)
                    state_text = "eingeschaltet" if new_state else "ausgeschaltet"
                    self._show_message(f"Der Schalter wurde {state_text}.")
                    
                elif obj.action == 'close_door':
                    # Handle door closing
                    door_id = getattr(obj, 'id', f"door_{obj.x}_{obj.y}")
                    
                    # Check if door is already closed
                    if not world_state.is_door_open(current_map, door_id):
                        self._show_message("Die Tür ist bereits geschlossen.")
                        return
                    
                    # Create and execute door close action
                    door_action = CutsceneAction(
                        action_type='close_door',
                        params={
                            'door_id': door_id,
                            'map_id': current_map,
                            'sound_file': getattr(obj, 'sound', 'door_close.wav')
                        }
                    )
                    
                    self._execute_immediate_action(door_action)
                    self._show_message("Die Tür schließt sich.")
                
                else:
                    # Unknown action - show generic message
                    self._show_message(f"Du aktivierst {obj.action}.")
                    
            except Exception as e:
                print(f"Error handling activate object: {e}")
                self._show_message("Etwas ist schiefgelaufen.")
        
        # Show dialog if present (after action)
        elif obj.dialog:
            self._show_message(obj.dialog)
        else:
            self._show_message("Nichts passiert.")
    
    def _execute_immediate_action(self, action):
        """Execute a cutscene action immediately (for interactive objects)."""
        try:
            # Create a temporary cutscene for the action
            from engine.systems.cutscene import Cutscene
            
            temp_cutscene = Cutscene("temp_interactive")
            temp_cutscene.game = self.game  # Set game reference
            temp_cutscene.add_action(action)
            temp_cutscene.start()
            
            # Execute the action immediately (single frame)
            temp_cutscene.update(0.0)
            
        except Exception as e:
            print(f"Error executing immediate action: {e}")
    
    def _show_message(self, text: str):
        """Show a simple message dialog."""
        if hasattr(self.game, 'current_scene') and hasattr(self.game.current_scene, 'dialogue_box'):
            # Lock player movement during message
            if hasattr(self.game.current_scene, 'player') and self.game.current_scene.player:
                self.game.current_scene.player.lock_movement(True)
            
            # Show message as dialogue with callback to unlock movement
            from engine.ui.dialogue import DialoguePage
            self.game.current_scene.dialogue_box.show_dialogue([
                DialoguePage(text, None)
            ], callback=lambda _: self._on_message_complete())
    
    def _show_dialog(self, dialog_id: str):
        """Show a dialog sequence."""
        # Load dialog from file
        dialog_file = Path("data/dialogs/events") / f"{dialog_id}.json"
        if dialog_file.exists():
            try:
                with open(dialog_file, 'r', encoding='utf-8') as f:
                    dialog_data = json.load(f)
                
                pages = []
                for page in dialog_data.get('pages', []):
                    pages.append(DialoguePage(
                        page.get('text', '...'),
                        page.get('speaker')
                    ))
                
                if pages and hasattr(self.game, 'current_scene'):
                    # Lock player movement during dialog
                    if hasattr(self.game.current_scene, 'player') and self.game.current_scene.player:
                        self.game.current_scene.player.lock_movement(True)
                    
                    # Show dialog with callback to unlock movement
                    self.game.current_scene.dialogue_box.show_dialogue(
                        pages,
                        callback=lambda _: self._on_message_complete()
                    )
            except Exception as e:
                print(f"[EnhancedMapManager] Failed to load dialog {dialog_id}: {e}")
    
    def _start_cutscene(self, cutscene_id: str):
        """Start a cutscene."""
        # Prevent cutscene start if dialogue is already active
        if hasattr(self.game, 'current_scene') and hasattr(self.game.current_scene, 'dialogue_box'):
            if self.game.current_scene.dialogue_box.is_open():
                return
        
        if hasattr(self.game, 'cutscene_manager'):
            try:
                # Implementiere Cutscene-System
                cutscene = self.game.cutscene_manager.get_cutscene(cutscene_id)
                if cutscene:
                    self.game.cutscene_manager.start_cutscene(cutscene_id)
                    print(f"[EnhancedMapManager] Cutscene {cutscene_id} gestartet")
                else:
                    print(f"[EnhancedMapManager] Cutscene {cutscene_id} nicht gefunden")
            except Exception as e:
                print(f"[EnhancedMapManager] Cutscene error: {e}")
        else:
            print(f"[EnhancedMapManager] Cutscene {cutscene_id} kann nicht gestartet werden - kein CutsceneManager")
    
    def _start_battle(self, battle_args: Dict):
        """Start a battle."""
        # Prevent battle start if dialogue is already active
        if hasattr(self.game, 'current_scene') and hasattr(self.game.current_scene, 'dialogue_box'):
            if self.game.current_scene.dialogue_box.is_open():
                return
        
        # Integrate with battle system
        print(f"[EnhancedMapManager] Starting battle: {battle_args}")
        
        # Start battle using the game's battle system
        try:
            if hasattr(self.game, 'battle_manager'):
                # Use existing battle manager
                battle_result = self.game.battle_manager.start_battle(battle_args)
                print(f"[EnhancedMapManager] Battle started: {battle_result}")
            elif hasattr(self.game, 'scene_manager'):
                # Switch to battle scene
                from engine.scenes.battle_scene import BattleScene
                battle_scene = BattleScene(self.game)
                battle_scene.setup_battle(battle_args)
                self.game.push_scene(battle_scene)
                print("[EnhancedMapManager] Battle scene pushed")
            else:
                print("[EnhancedMapManager] No battle system available")
        except Exception as e:
            print(f"[EnhancedMapManager] Battle integration error: {e}")
    
    def _on_message_complete(self):
        """Handle message dialog completion - unlock movement and start cooldown."""
        # Unlock player movement
        if hasattr(self.game, 'current_scene') and hasattr(self.game.current_scene, 'player') and self.game.current_scene.player:
            self.game.current_scene.player.lock_movement(False)
            
        # Start input cooldown to prevent immediate re-triggering
        if hasattr(self.game, 'current_scene') and hasattr(self.game.current_scene, 'dialog_input_cooldown'):
            self.game.current_scene.dialog_input_cooldown = self.game.current_scene.dialog_cooldown_duration

    def _on_npc_dialog_complete(self, npc_id: str, result: Any):
        """Callback when NPC dialog completes."""
        print(f"[EnhancedMapManager] Dialog complete for {npc_id}: {result}")
        
        # Unlock player movement and start cooldown
        self._on_message_complete()
        
        # Handle special NPCs
        if npc_id == 'professor' and not self.game.story_manager.get_flag('has_starter'):
            # Go to starter selection
            from engine.scenes.starter_scene import StarterScene
            self.game.push_scene(StarterScene, game=self.game)
    
    def get_collision_at(self, x: int, y: int) -> bool:
        """
        Check collision at pixel coordinates.
        
        Args:
            x: X position in pixels
            y: Y position in pixels
            
        Returns:
            True if position is blocked
        """
        if not self.current_area:
            return True
        
        # Convert to tile coordinates
        tile_x = x // TILE_SIZE
        tile_y = y // TILE_SIZE
        
        # Check bounds
        if tile_x < 0 or tile_x >= self.current_area.width:
            return True
        if tile_y < 0 or tile_y >= self.current_area.height:
            return True
        
        # Check collision map
        if hasattr(self.current_area, 'collision_map'):
            if self.current_area.collision_map[tile_y][tile_x]:
                return True
        
        # Check NPC collisions
        npc = self.npc_manager.get_npc_at_position(tile_x, tile_y)
        if npc:
            return True
        
        return False
    
    def create_interaction_files_for_existing_maps(self):
        """Create default interaction files for all existing TMX maps."""
        maps_dir = Path("data/maps")
        
        for tmx_file in maps_dir.glob("*.tmx"):
            map_id = tmx_file.stem
            interaction_file = self.interaction_manager.interactions_path / f"{map_id}.json"
            
            if not interaction_file.exists():
                print(f"Creating interaction file for: {map_id}")
                self.interaction_manager.create_default_interaction_file(map_id)
