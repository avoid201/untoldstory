#!/usr/bin/env python3
"""
Untold Story - Main Entry Point
A 2D top-down RPG inspired by Pokémon and Dragon Quest Monsters
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

import pygame
from engine.core.game import Game


def initialize_sprite_system():
    """Initialisiert das Sprite-System"""
    from engine.graphics.sprite_manager import SpriteManager
    from engine.world.tmx_init import initialize_tmx_support
    
    from engine.debug import debug_system_info
    # Initializing sprite system
    
    # Create sprite manager (aber NICHT _ensure_loaded aufrufen!)
    sprite_manager = SpriteManager.get()
    
    # WICHTIG: Zuerst TMX-Support initialisieren
    # Initializing TMX support FIRST
    initialize_tmx_support()
    
    # Dann erst den Rest laden
    sprite_manager._ensure_loaded()
    
    # Count loaded sprites
    total_sprites = (len(sprite_manager._tiles) + len(sprite_manager._objects) + 
                    len(sprite_manager._player_dir_map) + len(sprite_manager._npc_dir_map) + 
                    len(sprite_manager._monster))
    
    # Add GID count if available
    from engine.debug import debug_system_info
    if hasattr(sprite_manager, 'gid_to_surface'):
        gid_count = len(sprite_manager.gid_to_surface)
        debug_system_info("Sprite system initialized with {} sprites and {} TMX GIDs", total_sprites, gid_count)
    else:
        debug_system_info("Sprite system initialized with {} sprites", total_sprites)
    
    return sprite_manager


def initialize_tile_system():
    """Initialisiert das Tile-System mit Placeholder-Tiles"""
    from engine.world.tiles import TILE_SIZE
    from engine.debug import debug_system_info
    
    # Initializing tile system
    
    # Das Tile-System wird jetzt komplett über den SpriteManager verwaltet
    # Tile system initialized



def main() -> int:
    """
    Main entry point for Untold Story.
    Initializes pygame, creates the game instance, and runs the main loop.
    
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    # Initialize pygame modules
    pygame.init()
    
    # Set up display mode with logical resolution and scaling
    # Logical resolution: 320x180, scaled 4x to 1280x720
    LOGICAL_WIDTH = 320
    LOGICAL_HEIGHT = 180
    SCALE_FACTOR = 4
    WINDOW_WIDTH = LOGICAL_WIDTH * SCALE_FACTOR
    WINDOW_HEIGHT = LOGICAL_HEIGHT * SCALE_FACTOR
    
    # Create the display window
    screen = pygame.display.set_mode(
        (WINDOW_WIDTH, WINDOW_HEIGHT),
        pygame.SCALED | pygame.RESIZABLE
    )
    pygame.display.set_caption("Untold Story")
    
    # Create a logical backbuffer for pixel-perfect rendering
    logical_surface = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT))
    
    # Initialize sprite system BEFORE creating the game
    sprite_manager = initialize_sprite_system()
    
    # Initialize tile system
    initialize_tile_system()
    
    # Initialize the game
    try:
        game = Game(
            screen=screen,
            logical_surface=logical_surface,
            logical_size=(LOGICAL_WIDTH, LOGICAL_HEIGHT),
            window_size=(WINDOW_WIDTH, WINDOW_HEIGHT),
            scale_factor=SCALE_FACTOR
        )
        
        # Set the sprite manager in the game using the new method
        game.set_sprite_manager(sprite_manager)
        
        # Game initialized successfully
        
    except Exception as e:
        from engine.debug import debug_system_error
        debug_system_error("Failed to initialize game: {}", e)
        pygame.quit()
        return 1
    
    # Run the game
    try:
        exit_code = game.run()
    except KeyboardInterrupt:
        from engine.debug import debug_system_info
        debug_system_info("Game interrupted by user")
        exit_code = 0
    except Exception as e:
        from engine.debug import debug_system_error
        debug_system_error("Fatal error during game execution: {}", e)
        import traceback
        traceback.print_exc()
        exit_code = 1
    finally:
        # Clean shutdown
        pygame.quit()
    
    return exit_code


if __name__ == "__main__":
    # Check Python version
    if sys.version_info < (3, 13):
        from engine.debug import debug_system_error
        debug_system_error("Python 3.13+ required, found {}", sys.version)
        sys.exit(1)
    
    # Check pygame-ce version
    try:
        pygame_version = tuple(map(int, pygame.version.ver.split('.')[:2]))
        if pygame_version < (2, 5):
            debug_system_error("pygame-ce 2.5+ required, found {}", pygame.version.ver)
            sys.exit(1)
    except (AttributeError, ValueError):
        from engine.debug import debug_system_error
        debug_system_error("Warning: Could not verify pygame version")
    
    # Run the game
    sys.exit(main())
