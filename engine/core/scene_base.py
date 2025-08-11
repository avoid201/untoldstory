"""
Base Scene Interface for Untold Story
Defines the abstract base class for all game scenes
"""

from abc import ABC, abstractmethod
from typing import Optional, Any, Dict
import pygame


class Scene(ABC):
    """
    Abstract base class for all game scenes.
    
    A scene represents a distinct game state (e.g., title screen, field, battle, menu).
    Scenes are managed by the Game class using a scene stack, allowing for
    scene transitions and overlays (e.g., pause menu over field).
    """
    
    def __init__(self, game: 'Game') -> None:
        """
        Initialize the scene with a reference to the game instance.
        
        Args:
            game: The main Game instance that manages this scene
        """
        self.game = game
        self.is_active: bool = True
        self.is_visible: bool = True
        self.blocks_update: bool = True  # If True, scenes below don't update
        self.blocks_draw: bool = True    # If True, scenes below don't draw
        
    def enter(self, **kwargs: Any) -> None:
        """
        Called when the scene becomes active (pushed to stack or resumed).
        Override to handle scene initialization or resumption.
        
        Args:
            **kwargs: Optional parameters passed from the previous scene
        """
        pass
    
    def exit(self) -> Optional[Dict[str, Any]]:
        """
        Called when the scene is about to be removed or paused.
        Override to handle cleanup or state preservation.
        
        Returns:
            Optional dictionary of data to pass to the next scene
        """
        return None
    
    def pause(self) -> None:
        """
        Called when another scene is pushed on top of this one.
        Override to pause animations, music, etc.
        """
        self.is_active = False
    
    def resume(self) -> None:
        """
        Called when this scene becomes the top scene again.
        Override to resume animations, music, etc.
        """
        self.is_active = True
    
    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Process a pygame event.
        
        Args:
            event: The pygame event to process
            
        Returns:
            True if the event was handled (stops propagation), False otherwise
        """
        pass
    
    @abstractmethod
    def update(self, dt: float) -> None:
        """
        Update the scene logic.
        
        Args:
            dt: Delta time in seconds since the last frame
        """
        pass
    
    @abstractmethod
    def draw(self, surface: pygame.Surface) -> None:
        """
        Render the scene to the given surface.
        
        Args:
            surface: The logical surface to draw on (320x180)
        """
        pass
    
    def handle_scene_result(self, result: Optional[Dict[str, Any]]) -> None:
        """
        Handle the result from a child scene that was popped.
        Override to process data returned from subscenes.
        
        Args:
            result: Data returned from the popped scene's exit() method
        """
        pass
    
    def request_transition(self, 
                          scene_class: type['Scene'],
                          transition: Optional[str] = None,
                          **kwargs: Any) -> None:
        """
        Request a transition to a new scene.
        Convenience method that delegates to the game's scene manager.
        
        Args:
            scene_class: The class of the scene to transition to
            transition: Optional transition effect name ('fade', 'wipe', etc.)
            **kwargs: Arguments to pass to the new scene's enter() method
        """
        self.game.change_scene(scene_class, transition=transition, **kwargs)
    
    def push_scene(self, 
                   scene_class: type['Scene'],
                   **kwargs: Any) -> None:
        """
        Push a new scene onto the stack (overlay).
        Convenience method that delegates to the game's scene manager.
        
        Args:
            scene_class: The class of the scene to push
            **kwargs: Arguments to pass to the new scene's enter() method
        """
        self.game.push_scene(scene_class, **kwargs)
    
    def pop_scene(self, result: Optional[Dict[str, Any]] = None) -> None:
        """
        Pop this scene from the stack.
        Convenience method that delegates to the game's scene manager.
        
        Args:
            result: Optional data to pass to the underlying scene
        """
        self.game.pop_scene(result)
    
    def quit_game(self) -> None:
        """
        Request the game to quit.
        Convenience method that delegates to the game instance.
        """
        self.game.quit()


class TransitionScene(Scene):
    """
    Base class for transition effects between scenes.
    Transitions are temporary scenes that animate between two states.
    """
    
    def __init__(self, 
                 game: 'Game',
                 from_scene: Optional[Scene],
                 to_scene: Scene,
                 duration: float = 0.5) -> None:
        """
        Initialize a transition scene.
        
        Args:
            game: The main Game instance
            from_scene: The scene transitioning from (None if starting fresh)
            to_scene: The scene transitioning to
            duration: Transition duration in seconds
        """
        super().__init__(game)
        self.from_scene = from_scene
        self.to_scene = to_scene
        self.duration = duration
        self.elapsed = 0.0
        self.progress = 0.0
        
        # Capture surfaces for transition effect
        self.from_surface: Optional[pygame.Surface] = None
        self.to_surface: Optional[pygame.Surface] = None
        
        if from_scene:
            self.from_surface = pygame.Surface(game.logical_size)
            from_scene.draw(self.from_surface)
        
        # Pre-render the target scene
        self.to_surface = pygame.Surface(game.logical_size)
        to_scene.draw(self.to_surface)
    
    def update(self, dt: float) -> None:
        """Update transition progress."""
        self.elapsed += dt
        self.progress = min(1.0, self.elapsed / self.duration)
        
        if self.progress >= 1.0:
            # Transition complete - replace with target scene
            self.game.replace_scene(self.to_scene)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Transitions typically consume all events."""
        return True