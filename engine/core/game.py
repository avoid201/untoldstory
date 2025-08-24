"""
Main Game Loop and Scene Management for Untold Story - REFACTORED VERSION
Handles the core game loop, input processing, scene stack, and rendering pipeline
"""

from typing import Optional, List, Dict, Any, Tuple, Type
from collections import deque
import pygame
import time

# Import refactored components
from engine.core.event_processor import EventProcessor
from engine.core.debug_overlay import DebugOverlayManager


class Game:
    """
    Core game class that manages the main loop, scene stack, input, and rendering.
    Refactored to use EventProcessor and DebugOverlayManager.
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
        
        # Initialize refactored components
        self.event_processor = EventProcessor(self)
        self.debug_overlay_manager = DebugOverlayManager(self)
        
        # Debug flags
        self.debug_overlay_enabled = False
        self.show_grid = False
        self.show_fps = True
        self.debug_mode = False  # Debug-Modus für erweiterte Debug-Funktionen
        
        # Game state
        self.running = False
        self.paused = False
        
        # Font for debug overlay (legacy, wird durch DebugOverlayManager ersetzt)
        self.debug_font: Optional[pygame.font.Font] = None
        try:
            self.debug_font = pygame.font.Font(None, 16)
        except:
            print("Warning: Could not load debug font")
        
        # Initialize managers
        from engine.systems.story import StoryManager
        from engine.systems.party import PartyManager
        from engine.core.resources import ResourceManager
        from engine.systems.cutscene import CutsceneManager
        from engine.ui.transitions import TransitionManager
        # AudioManager is optional; provide a no-op fallback if missing
        from engine.audio.audio_manager import AudioManager
        
        self.resources = ResourceManager()
        self.story_manager = StoryManager()
        self.party_manager = PartyManager(self)
        self.cutscene_manager = CutsceneManager(self)
        # Provide a simple transition controller with a start() API
        class _SimpleTransitionManager:
            def __init__(self, game: 'Game') -> None:
                self.game = game

            def start(self, transition_type, duration: float = 0.5, to_scene: Optional['Scene'] = None) -> None:
                try:
                    # Use TransitionManager factory to create transition
                    from engine.ui.transitions import TransitionManager as _TM
                    current = self.game.current_scene
                    target = to_scene or current
                    if current is None or target is None:
                        return
                    self.game.scene_transition = _TM.create_transition(
                        transition_type=transition_type,
                        game=self.game,
                        from_scene=current,
                        to_scene=target,
                        duration=duration,
                    )
                except Exception as e:
                    print(f"Warning: Could not start transition: {e}")

            def create_transition(self, transition_type, game: 'Game', from_scene: Optional['Scene'], 
                                to_scene: 'Scene', duration: float = 0.5, **kwargs) -> Optional['TransitionScene']:
                """Create a transition using the TransitionManager factory."""
                try:
                    from engine.ui.transitions import TransitionManager as _TM
                    return _TM.create_transition(
                        transition_type=transition_type,
                        game=game,
                        from_scene=from_scene,
                        to_scene=to_scene,
                        duration=duration,
                        **kwargs
                    )
                except Exception as e:
                    print(f"Warning: Could not create transition: {e}")
                    return None
        
        self.transition_manager = _SimpleTransitionManager(self)
        self.audio_manager = AudioManager()
        
        # Story-System für neues Spiel initialisieren
        self._init_story_system()
        
        # Initialize graphics system
        from engine.world.tiles import TILE_SIZE
        
        def initialize_graphics():
            """Initialisiert das Grafik-System"""
            # Das Grafik-System wird jetzt komplett über den SpriteManager verwaltet
            print(f"Graphics system initialized with {TILE_SIZE}x{TILE_SIZE} tiles")
        
        # Rufe die Grafik-Initialisierung auf
        initialize_graphics()
    
    def init_input_system(self):
        """Initialize the input management system"""
        from engine.core.input_manager import InputManager, InputConfig
        
        # Create input manager with default config
        self.input_manager = InputManager(InputConfig())
        
        # Initialize extended input debugger
        try:
            from engine.devtools.input_debug import get_input_debugger
            self.input_debugger = get_input_debugger()
            print("🔍 INPUT DEBUGGER: Erweiterte Debug-Funktionen geladen")
        except ImportError as e:
            print(f"⚠️  WARNING: Erweiterte Input-Debug-Funktionen nicht verfügbar: {e}")
            self.input_debugger = None
        
        # Create helper methods for scenes - THESE ARE OVERRIDDEN BELOW!
        # self.is_key_pressed = self.input_manager.is_pressed
        # self.is_key_just_pressed = self.input_manager.is_just_pressed
        # self.is_key_just_released = self.input_manager.is_just_released
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
        
        # Erstelle den TileRenderer mit dem SpriteManager
        from engine.graphics.tile_renderer import TileRenderer
        self.tile_renderer = TileRenderer(sprite_manager)
        
        # Count loaded sprites
        total_sprites = (len(sprite_manager._tiles) + len(sprite_manager._objects) + 
                        len(sprite_manager._player_dir_map) + len(sprite_manager._npc_dir_map) + 
                        len(sprite_manager._monster))
        print(f"SpriteManager gesetzt: {total_sprites} Sprites verfügbar")
    
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
        # Delegate to EventProcessor
        self.event_processor.process_events()
    
    def _update(self, dt: float) -> None:
        """
        Update game logic.
        
        Args:
            dt: Delta time in seconds
        """
        # Update input manager first
        self.input_manager.update(dt)
        
        # Update audio manager
        self.audio_manager.update()
        
        # Update transition if active
        if self.scene_transition:
            self.scene_transition.update(dt)
            # Clean up finished transitions so normal update resumes
            try:
                if getattr(self.scene_transition, 'progress', 0.0) >= 1.0:
                    self.scene_transition = None
            except Exception:
                self.scene_transition = None
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
        
        # Draw debug overlay using DebugOverlayManager
        if self.debug_overlay_enabled:
            self.debug_overlay_manager.draw_debug_overlay(self.logical_surface)
        
        # Draw FPS counter using DebugOverlayManager
        if self.show_fps:
            self.debug_overlay_manager.draw_fps_counter(self.logical_surface)
    
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
    
    # Scene Management Methods
    
    def push_scene(self, scene_class: Type['Scene'], **kwargs: Any) -> None:
        """
        Push a new scene onto the stack.
        
        Args:
            scene_class: The scene class to instantiate
            **kwargs: Arguments to pass to the scene's enter() method
            
        Raises:
            Exception: If scene initialization fails
        """
        try:
            # Pause current scene if exists
            if self.scene_stack:
                self.scene_stack[-1].pause()
            
            # Create and initialize new scene
            new_scene = scene_class(self)
            new_scene.enter(**kwargs)
            
            # Call on_enter for specialized scenes like BattleScene
            if hasattr(new_scene, 'on_enter'):
                new_scene.on_enter(**kwargs)
            
            self.scene_stack.append(new_scene)
        except Exception as e:
            # Restore previous scene if initialization fails
            if self.scene_stack:
                self.scene_stack[-1].resume()
            print(f"Failed to initialize scene {scene_class.__name__}: {str(e)}")
            raise
    
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
            
        Raises:
            Exception: If scene initialization fails
        """
        try:
            # Create the new scene but don't initialize yet if using transition
            new_scene = scene_class(self)
            
            if transition and self.scene_stack:
                from engine.ui.transitions import FadeTransition
                # Create transition scene - new_scene will be initialized after transition
                self.scene_transition = FadeTransition(
                    self, self.scene_stack[-1], new_scene, duration=0.5,
                    scene_kwargs=kwargs
                )
            else:
                # Direct scene replacement - initialize now
                new_scene.enter(**kwargs)
                self.replace_scene(new_scene)
        except Exception as e:
            print(f"Failed to change to scene {scene_class.__name__}: {str(e)}")
            raise
    
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
        # Delegate to input manager
        if hasattr(self, 'input_manager'):
            return self.input_manager.is_pressed(action)
        
        # Fallback to old system (should not be used)
        print(f"⚠️ Warning: Using fallback input system for action '{action}'")
        return False
    
    def is_key_just_pressed(self, action: str) -> bool:
        """
        Check if any key mapped to an action was just pressed this frame.
        
        Args:
            action: The action name from input_map
            
        Returns:
            True if any mapped key was just pressed
        """
        # Delegate to input manager
        if hasattr(self, 'input_manager'):
            return self.input_manager.is_just_pressed(action)
        
        # Fallback to old system (should not be used)
        print(f"⚠️ Warning: Using fallback input system for action '{action}'")
        return False
    
    def start_transition(self, transition_type: str, duration: float = 0.5, **kwargs) -> None:
        """
        Start a scene transition effect.
        
        Args:
            transition_type: Type of transition ('fade', 'wipe_left', etc.)
            duration: Duration of transition in seconds
            **kwargs: Additional transition parameters
        """
        from engine.ui.transitions import TransitionType
        
        # Map string names to enum values
        transition_map = {
            'fade': TransitionType.FADE,
            'fade_black': TransitionType.FADE_TO_BLACK,
            'fade_white': TransitionType.FADE_TO_WHITE,
            'wipe_left': TransitionType.WIPE_LEFT,
            'wipe_right': TransitionType.WIPE_RIGHT,
            'wipe_up': TransitionType.WIPE_UP,
            'wipe_down': TransitionType.WIPE_DOWN,
            'radial': TransitionType.RADIAL,
            'battle_swirl': TransitionType.BATTLE_SWIRL
        }
        
        transition_enum = transition_map.get(transition_type, TransitionType.FADE)
        
        if self.scene_stack:
            current_scene = self.scene_stack[-1]
            # For now, create a simple transition without changing scenes
            self.scene_transition = self.transition_manager.create_transition(
                transition_enum, self, current_scene, current_scene, duration, **kwargs
            )

    def quit(self) -> None:
        """Signal the game to quit."""
        self.running = False
