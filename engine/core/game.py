"""
Main Game Loop and Scene Management for Untold Story
Handles the core game loop, input processing, scene stack, and rendering pipeline
"""

from typing import Optional, List, Dict, Any, Tuple, Type
from collections import deque
import pygame
import time


class Game:
    """
    Core game class that manages the main loop, scene stack, input, and rendering.
    """
    
    @property
    def current_scene(self) -> Optional['Scene']:
        """Get the current active scene from the top of the stack."""
        return self.scene_stack[-1] if self.scene_stack else None
    
    def __init__(self,
                 screen: pygame.Surface,
                 logical_surface: pygame.Surface,
                 logical_size: Tuple[int, int],
                 window_size: Tuple[int, int],
                 scale_factor: int) -> None:
        """
        Initialize the game instance.
        
        Args:
            screen: The main pygame display surface
            logical_surface: The logical resolution surface for rendering (320x180)
            logical_size: The logical resolution dimensions (width, height)
            window_size: The window dimensions (width, height)
            scale_factor: The scaling factor from logical to window size
        """
        self.screen = screen
        self.logical_surface = logical_surface
        self.logical_size = logical_size
        self.window_size = window_size
        self.scale_factor = scale_factor
        
        # Scene management
        self.scene_stack: List['Scene'] = []
        self.next_scene: Optional['Scene'] = None
        self.scene_transition: Optional['TransitionScene'] = None
        
        # Timing
        self.clock = pygame.time.Clock()
        self.target_fps = 60
        self.dt = 0.0
        self.total_time = 0.0
        self.frame_count = 0
        
        # Input state
        self.keys_pressed = pygame.key.get_pressed()
        self.keys_just_pressed: set[int] = set()
        self.keys_just_released: set[int] = set()
        self.mouse_pos = (0, 0)  # Logical coordinates
        self.mouse_buttons = pygame.mouse.get_pressed()
        
        # Initialize input system
        self.init_input_system()
        
        # Debug flags
        self.debug_overlay_enabled = False
        self.show_grid = False
        self.show_fps = True
        self.debug_mode = False  # Debug-Modus für erweiterte Debug-Funktionen
        
        # Game state
        self.running = False
        self.paused = False
        
        # Font for debug overlay
        self.debug_font: Optional[pygame.font.Font] = None
        try:
            self.debug_font = pygame.font.Font(None, 16)
        except:
            print("Warning: Could not load debug font")
        
        # Initialize managers
        from engine.systems.story_manager import StoryManager
        from engine.systems.party import PartyManager
        from engine.core.resources import ResourceManager
        from engine.systems.cutscene import CutsceneManager
        
        self.resources = ResourceManager()
        self.story_manager = StoryManager()
        self.party_manager = PartyManager(self)
        self.cutscene_manager = CutsceneManager(self)
        
        # Story-System für neues Spiel initialisieren
        self._init_story_system()
        
        # Initialize graphics system
        from engine.world.tiles import tileset_manager, TILE_SIZE
        
        def initialize_graphics():
            """Initialisiert das Grafik-System"""
            # Verbinde den SpriteManager mit dem TilesetManager
            if hasattr(self, 'sprite_manager'):
                tileset_manager.sprite_manager = self.sprite_manager
                print("SpriteManager mit TilesetManager verbunden")
            else:
                print("Warnung: Kein SpriteManager verfügbar")
        
        # Rufe die Grafik-Initialisierung auf
        initialize_graphics()
    
    def init_input_system(self):
        """Initialize the input management system"""
        from engine.core.input_manager import InputManager, InputConfig
        
        # Create input manager with default config
        self.input_manager = InputManager(InputConfig())
        
        # Create helper methods for scenes
        self.is_key_pressed = self.input_manager.is_pressed
        self.is_key_just_pressed = self.input_manager.is_just_pressed
        self.is_key_just_released = self.input_manager.is_just_released
        self.get_movement = self.input_manager.get_movement_vector
        
        print("Input system initialized")
    
    def _init_story_system(self):
        """Initialisiert das Story-System für neues Spiel"""
        # Setze initiale Story-Flags
        if self.story_manager:
            self.story_manager.set_flag('game_started', True)
            self.story_manager.set_flag('first_awakening', True)
            print("Story-System initialisiert - Neues Spiel gestartet")
    
    def set_sprite_manager(self, sprite_manager) -> None:
        """Setzt den SpriteManager für das Spiel"""
        self.sprite_manager = sprite_manager
        
        # Verbinde den SpriteManager mit dem TilesetManager
        from engine.world.tiles import tileset_manager
        tileset_manager.sprite_manager = sprite_manager
        
        # Erstelle den TileRenderer mit dem SpriteManager
        from engine.graphics.tile_renderer import TileRenderer
        self.tile_renderer = TileRenderer(sprite_manager)
        
        print(f"SpriteManager gesetzt: {len(sprite_manager.sprite_cache)} Sprites verfügbar")
        print(f"TilesetManager verbunden: {hasattr(tileset_manager, 'sprite_manager')}")
        
        # Lade das Tileset neu mit dem verbundenen SpriteManager
        tileset_manager.load_tileset("", 64)  # Leerer Pfad, da wir den SpriteManager verwenden
    
    def run(self) -> int:
        """
        Run the main game loop.
        
        Returns:
            Exit code (0 for success)
        """
        self.running = True
        
        # Initialize with start scene
        from engine.scenes.start_scene import StartScene
        self.push_scene(StartScene)
        
        # Main game loop
        while self.running:
            # Calculate delta time
            self.dt = self.clock.tick(self.target_fps) / 1000.0
            self.total_time += self.dt
            self.frame_count += 1
            
            # Process events
            self._process_events()
            
            # Update
            if not self.paused:
                self._update(self.dt)
            
            # Draw
            self._draw()
            
            # Present
            self._present()
        
        return 0
    
    def _process_events(self) -> None:
        """Process all pygame events and update input state."""
        # Store previous key state
        prev_keys = self.keys_pressed
        self.keys_just_pressed.clear()
        self.keys_just_released.clear()
        
        # Process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
                continue
            
            # Update key state tracking
            if event.type == pygame.KEYDOWN:
                self.keys_just_pressed.add(event.key)
                
                # Global debug toggle
                if event.key == pygame.K_TAB:
                    self.debug_overlay_enabled = not self.debug_overlay_enabled
                elif event.key == pygame.K_g and self.debug_overlay_enabled:
                    self.show_grid = not self.show_grid
            
            elif event.type == pygame.KEYUP:
                self.keys_just_released.add(event.key)
            
            # Convert mouse position to logical coordinates
            elif event.type == pygame.MOUSEMOTION:
                self.mouse_pos = self._screen_to_logical(event.pos)
            
            # Pass event to active scene
            if self.scene_stack:
                # Process from top to bottom until handled
                for scene in reversed(self.scene_stack):
                    if scene.is_active and scene.handle_event(event):
                        break
        
        # Update current key state
        self.keys_pressed = pygame.key.get_pressed()
        self.mouse_buttons = pygame.mouse.get_pressed()
    
    def _update(self, dt: float) -> None:
        """
        Update game logic.
        
        Args:
            dt: Delta time in seconds
        """
        # Update input manager first
        self.input_manager.update()
        
        # Update transition if active
        if self.scene_transition:
            self.scene_transition.update(dt)
            return
        
        # Update scenes from bottom to top until blocked
        for scene in self.scene_stack:
            if scene.is_active:
                scene.update(dt)
                if scene.blocks_update:
                    break
    
    def _draw(self) -> None:
        """Render the game to the logical surface."""
        # Clear the logical surface
        self.logical_surface.fill((20, 20, 30))  # Dark blue-gray
        
        # Draw transition if active
        if self.scene_transition:
            self.scene_transition.draw(self.logical_surface)
            return
        
        # Find the lowest visible scene that blocks drawing
        start_idx = 0
        for i in range(len(self.scene_stack) - 1, -1, -1):
            if self.scene_stack[i].blocks_draw:
                start_idx = i
                break
        
        # Draw scenes from bottom-most blocking scene upward
        for i in range(start_idx, len(self.scene_stack)):
            scene = self.scene_stack[i]
            if scene.is_visible:
                scene.draw(self.logical_surface)
        
        # Draw debug overlay
        if self.debug_overlay_enabled:
            self._draw_debug_overlay()
        
        # Draw FPS counter
        if self.show_fps and self.debug_font:
            fps_text = f"FPS: {self.clock.get_fps():.1f}"
            fps_surface = self.debug_font.render(fps_text, True, (255, 255, 0))
            self.logical_surface.blit(fps_surface, (2, 2))
    
    def _present(self) -> None:
        """Scale and present the logical surface to the screen."""
        # Calculate scaling to maintain aspect ratio
        window_w, window_h = self.screen.get_size()
        logical_w, logical_h = self.logical_size
        
        scale_x = window_w / logical_w
        scale_y = window_h / logical_h
        scale = min(scale_x, scale_y)
        
        # Calculate integer scale for pixel-perfect rendering
        int_scale = max(1, int(scale))
        
        # Calculate destination size and position for centered display
        dest_w = logical_w * int_scale
        dest_h = logical_h * int_scale
        dest_x = (window_w - dest_w) // 2
        dest_y = (window_h - dest_h) // 2
        
        # Clear screen with letterbox color
        self.screen.fill((0, 0, 0))
        
        # Scale and blit the logical surface
        scaled = pygame.transform.scale(self.logical_surface, (dest_w, dest_h))
        self.screen.blit(scaled, (dest_x, dest_y))
        
        # Flip the display
        pygame.display.flip()
    
    def _draw_debug_overlay(self) -> None:
        """Draw debug information overlay."""
        if not self.debug_font:
            return
        
        # Debug info
        debug_lines = [
            f"Scene: {self.scene_stack[-1].__class__.__name__ if self.scene_stack else 'None'}",
            f"Stack: {len(self.scene_stack)}",
            f"Time: {self.total_time:.1f}s",
            f"Frame: {self.frame_count}",
            f"Mouse: {self.mouse_pos}",
        ]
        
        # Draw debug text
        y = 20
        for line in debug_lines:
            text_surface = self.debug_font.render(line, True, (0, 255, 0))
            self.logical_surface.blit(text_surface, (2, y))
            y += 12
        
        # Draw grid if enabled
        if self.show_grid:
            self._draw_grid()
    
    def _draw_grid(self) -> None:
        """Draw a tile grid overlay."""
        TILE_SIZE = 16
        color = (255, 255, 255, 64)  # Semi-transparent white
        
        # Vertical lines
        for x in range(0, self.logical_size[0] + 1, TILE_SIZE):
            pygame.draw.line(self.logical_surface, color, 
                           (x, 0), (x, self.logical_size[1]), 1)
        
        # Horizontal lines
        for y in range(0, self.logical_size[1] + 1, TILE_SIZE):
            pygame.draw.line(self.logical_surface, color,
                           (0, y), (self.logical_size[0], y), 1)
    
    def _screen_to_logical(self, screen_pos: Tuple[int, int]) -> Tuple[int, int]:
        """
        Convert screen coordinates to logical coordinates.
        
        Args:
            screen_pos: Position in screen/window coordinates
            
        Returns:
            Position in logical coordinates
        """
        window_w, window_h = self.screen.get_size()
        logical_w, logical_h = self.logical_size
        
        scale_x = window_w / logical_w
        scale_y = window_h / logical_h
        scale = min(scale_x, scale_y)
        int_scale = max(1, int(scale))
        
        dest_w = logical_w * int_scale
        dest_h = logical_h * int_scale
        dest_x = (window_w - dest_w) // 2
        dest_y = (window_h - dest_h) // 2
        
        # Convert to logical coordinates
        logical_x = (screen_pos[0] - dest_x) // int_scale
        logical_y = (screen_pos[1] - dest_y) // int_scale
        
        # Clamp to logical bounds
        logical_x = max(0, min(logical_w - 1, logical_x))
        logical_y = max(0, min(logical_h - 1, logical_y))
        
        return (logical_x, logical_y)
    
    # Scene Management Methods
    
    def push_scene(self, scene_class: Type['Scene'], **kwargs: Any) -> None:
        """
        Push a new scene onto the stack.
        
        Args:
            scene_class: The scene class to instantiate
            **kwargs: Arguments to pass to the scene's enter() method
        """
        # Pause current scene if exists
        if self.scene_stack:
            self.scene_stack[-1].pause()
        
        # Create and initialize new scene
        new_scene = scene_class(self)
        new_scene.enter(**kwargs)
        self.scene_stack.append(new_scene)
    
    def pop_scene(self, result: Optional[Dict[str, Any]] = None) -> None:
        """
        Pop the top scene from the stack.
        
        Args:
            result: Optional data to pass to the underlying scene
        """
        if not self.scene_stack:
            return
        
        # Exit the current scene
        popped_scene = self.scene_stack.pop()
        popped_scene.exit()
        
        # Resume previous scene if exists
        if self.scene_stack:
            self.scene_stack[-1].resume()
            self.scene_stack[-1].handle_scene_result(result)
        else:
            # No more scenes - quit
            self.quit()
    
    def change_scene(self, scene_class: Type['Scene'], 
                    transition: Optional[str] = None,
                    **kwargs: Any) -> None:
        """
        Change to a new scene, replacing the current one.
        
        Args:
            scene_class: The scene class to transition to
            transition: Optional transition effect name
            **kwargs: Arguments to pass to the new scene's enter() method
        """
        # Create the new scene
        new_scene = scene_class(self)
        new_scene.enter(**kwargs)
        
        # Handle transition
        if transition and self.scene_stack:
            from engine.ui.transitions import FadeTransition
            # Create transition scene
            self.scene_transition = FadeTransition(
                self, self.scene_stack[-1], new_scene, duration=0.5
            )
        else:
            # Direct scene replacement
            self.replace_scene(new_scene)
    
    def replace_scene(self, new_scene: 'Scene') -> None:
        """
        Replace the current scene with a new one.
        
        Args:
            new_scene: The scene instance to switch to
        """
        # Clear any active transition
        self.scene_transition = None
        
        # Exit current scene if exists
        if self.scene_stack:
            old_scene = self.scene_stack.pop()
            old_scene.exit()
        
        # Add new scene
        self.scene_stack.append(new_scene)
    
    def is_key_pressed(self, action: str) -> bool:
        """
        Check if any key mapped to an action is currently pressed.
        
        Args:
            action: The action name from input_map
            
        Returns:
            True if any mapped key is pressed
        """
        # Legacy method - use input_manager.is_pressed() instead
        if hasattr(self, 'input_manager'):
            return self.input_manager.is_pressed(action)
        
        # Fallback to old system
        if action not in getattr(self, 'input_map', {}):
            return False
        return any(self.keys_pressed[key] for key in self.input_map[action])
    
    def is_key_just_pressed(self, action: str) -> bool:
        """
        Check if any key mapped to an action was just pressed this frame.
        
        Args:
            action: The action name from input_map
            
        Returns:
            True if any mapped key was just pressed
        """
        # Legacy method - use input_manager.is_just_pressed() instead
        if hasattr(self, 'input_manager'):
            return self.input_manager.is_just_pressed(action)
        
        # Fallback to old system
        if action not in getattr(self, 'input_map', {}):
            return False
        return any(key in self.keys_just_pressed for key in self.input_map[action])
    
    def quit(self) -> None:
        """Signal the game to quit."""
        self.running = False