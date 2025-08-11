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
    
    print("Initializing sprite system...")
    
    # Create sprite manager
    sprite_manager = SpriteManager()
    
    print(f"Sprite system initialized with {len(sprite_manager.sprite_cache)} sprites")
    
    return sprite_manager


def initialize_tile_system():
    """Initialisiert das Tile-System mit Placeholder-Tiles"""
    from engine.world.tiles import tileset_manager, TILE_SIZE
    
    print("Initializing tile system...")
    
    # Versuche echtes Tileset zu laden
    tileset_loaded = False
    
    # Prüfe verschiedene mögliche Pfade
    possible_paths = [
        "assets/gfx/tileset.png",  # Korrigiert: assets/gfx statt assets/graphics
        "assets/tilesets/overworld.png", 
        "graphics/tilesets/overworld.png",
        "tileset.png"
    ]
    
    for path in possible_paths:
        if tileset_manager.load_tileset(path, TILE_SIZE):
            print(f"Loaded tileset from {path}")
            tileset_loaded = True
            break
    
    if not tileset_loaded:
        print("No tileset found, creating fallback tiles")
        tileset_manager._create_fallback_tiles(TILE_SIZE)
    
    print(f"Tile system initialized with {len(tileset_manager.tile_surfaces)} tiles")


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
        
        # Test ob Manager existieren
        print(f"Story Manager: {hasattr(game, 'story_manager')}")
        print(f"Party Manager: {hasattr(game, 'party_manager')}")
        print(f"Sprite Manager: {hasattr(game, 'sprite_manager')}")
        print(f"Graphics Manager: {hasattr(game, 'graphics_manager')}")
        print(f"Tile Renderer: {hasattr(game, 'tile_renderer')}")
        
    except Exception as e:
        print(f"Failed to initialize game: {e}", file=sys.stderr)
        pygame.quit()
        return 1
    
    # Run the game
    try:
        exit_code = game.run()
    except KeyboardInterrupt:
        print("\nGame interrupted by user")
        exit_code = 0
    except Exception as e:
        print(f"Fatal error during game execution: {e}", file=sys.stderr)
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
        print(f"Python 3.13+ required, found {sys.version}", file=sys.stderr)
        sys.exit(1)
    
    # Check pygame-ce version
    try:
        pygame_version = tuple(map(int, pygame.version.ver.split('.')[:2]))
        if pygame_version < (2, 5):
            print(f"pygame-ce 2.5+ required, found {pygame.version.ver}", file=sys.stderr)
            sys.exit(1)
    except (AttributeError, ValueError):
        print("Warning: Could not verify pygame version", file=sys.stderr)
    
    # Run the game
    sys.exit(main())
