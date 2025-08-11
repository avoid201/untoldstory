# ========================================
# POKÉMON-STYLE MOVEMENT SYSTEM
# ========================================

# ========================================
# 1. PLAYER.PY - Komplettes Grid-Movement System
# ========================================

"""
Grid-based Player Controller für Untold Story
Pokémon-style tile-basiertes Movement mit allen Features
"""

import pygame
from typing import Optional, List, Tuple, Callable
from engine.world.entity import Entity, Direction, EntitySprite
from engine.world.tiles import TILE_SIZE, world_to_tile, is_rect_colliding
from engine.world.movement_states import MovementState
from engine.world.ledge_handler import LedgeHandler
from engine.items.running_shoes import RunningShoes
import os


class Player(Entity):
    """
    Pokémon-style grid-based Player Controller
    - Tile-zu-Tile Bewegung
    - Smooth animations zwischen Tiles
    - Turn-in-place bei kurzem Tastendruck
    - Running mit B-Taste
    - Auto-interact beim Laufen gegen NPCs/Objekte
    """
    
    def __init__(self, x: float, y: float) -> None:
        """
        Initialize the player at a tile position.
        
        Args:
            x: Initial X position in world coordinates
            y: Initial Y position in world coordinates
        """
        # Create player sprite config
        sprite_config = EntitySprite(
            sheet_path=None,  # Wird später gesetzt
            surface=None,     # Wird später gesetzt
            frame_width=64,   # Korrigiert: 64x64 Pixel Sprites
            frame_height=64,  # Korrigiert: 64x64 Pixel Sprites
            animations={
                'idle_down': [0],
                'idle_up': [4],
                'idle_left': [8],
                'idle_right': [12],
                'walk_down': [0, 1, 2, 3],
                'walk_up': [4, 5, 6, 7],
                'walk_left': [8, 9, 10, 11],
                'walk_right': [12, 13, 14, 15],
                'run_down': [0, 1, 2, 3],  # Gleiche Frames, aber schneller
                'run_up': [4, 5, 6, 7],
                'run_left': [8, 9, 10, 11],
                'run_right': [12, 13, 14, 15],
            },
            frame_duration=0.1
        )
        
        # Initialize base entity
        super().__init__(x, y, width=56, height=56, sprite_config=sprite_config)  # Korrigiert: 56x56 Pixel
        
        # Player properties
        self.name = "Player"
        self.movement_state = MovementState.IDLE
        
        # Grid-based movement
        self.grid_x = int(x // TILE_SIZE)  # Current tile X
        self.grid_y = int(y // TILE_SIZE)  # Current tile Y
        self.target_grid_x = self.grid_x   # Target tile X
        self.target_grid_y = self.grid_y   # Target tile Y
        
        # Movement timing
        self.move_progress = 0.0      # 0.0 = at current tile, 1.0 = at target tile
        self.move_speed = 16.0        # Korrigiert: 4x schneller für 64x64 Tiles (4.0 * 4)
        self.run_speed = 24.0         # Korrigiert: 4x schneller für 64x64 Tiles (6.0 * 4)
        self.turn_delay = 0.1         # Seconds before moving after turning
        self.turn_timer = 0.0         # Current turn delay timer
        
        # Input handling
        self.input_buffer = None      # Buffered input direction
        self.is_running = False       # B button held
        self.last_tap_time = 0.0     # Time of last direction tap
        self.tap_threshold = 0.15    # Max time for "tap" vs "hold"
        
        # Collision detection
        self.collision_layer: Optional[List[List[int]]] = None
        self.map_width = 0
        self.map_height = 0
        
        # Callbacks
        self.interact_callback: Optional[Callable] = None
        self.warp_callback: Optional[Callable] = None
        self.encounter_callback: Optional[Callable] = None
        self.collision_callback: Optional[Callable] = None
        
        # Encounter tracking
        self.steps_taken = 0
        self.steps_since_encounter = 0
        
        # Animation
        self.footstep_frame = 0
        self.animation_speed_multiplier = 1.0
        
        # Load player sprite after initialization
        self._load_player_sprite()
    
    def _load_player_sprite(self) -> None:
        """Load the player sprite from the sprite manager."""
        try:
            print("🎮 Lade Player-Sprite...")
            
            # Versuche zuerst den SpriteManager direkt zu verwenden
            if hasattr(self, 'sprite_manager') and self.sprite_manager:
                sprite_manager = self.sprite_manager
                print(f"✅ SpriteManager verfügbar mit {len(sprite_manager.sprite_cache)} Sprites")
                print(f"🔍 Verfügbare Sprites: {list(sprite_manager.sprite_cache.keys())[:10]}")
                
                # Versuche verschiedene Schlüssel für den Player-Sprite
                player_sprite = None
                for key in ["player", "player_sprite"]:
                    player_sprite = sprite_manager.get_player_sprite()
                    if player_sprite:
                        break
                
                if player_sprite:
                    self.sprite_config.surface = player_sprite
                    self.sprite_surface = player_sprite
                    print(f"✅ Player sprite geladen vom SpriteManager: {player_sprite.get_size()}")
                    return
                else:
                    print("⚠️  Player sprite nicht im SpriteManager gefunden")
                    print(f"🔍 Verfügbare Player-Schlüssel: {[k for k in sprite_manager.sprite_cache.keys() if 'player' in k.lower()]}")
            
            # Fallback: Versuche den SpriteManager aus dem Game-Objekt zu holen
            if hasattr(self, 'game') and hasattr(self.game, 'sprite_manager'):
                sprite_manager = self.game.sprite_manager
                if sprite_manager:
                    print(f"✅ SpriteManager aus Game verfügbar mit {len(sprite_manager.sprite_cache)} Sprites")
                    
                    # Versuche verschiedene Schlüssel für den Player-Sprite
                    player_sprite = None
                    for key in ["player", "player_sprite"]:
                        player_sprite = sprite_manager.get_player_sprite()
                        if player_sprite:
                            break
                    
                    if player_sprite:
                        self.sprite_config.surface = player_sprite
                        self.sprite_surface = player_sprite
                        print(f"✅ Player sprite geladen vom Game SpriteManager: {player_sprite.get_size()}")
                        return
                    else:
                        print("⚠️  Player sprite nicht im Game SpriteManager gefunden")
            
            # Fallback: Versuche direkt aus der Datei zu laden
            sprite_paths = [
                "sprites/player.png",
                "sprites/player_large.png",
                os.path.join("sprites", "player.png"),
                os.path.join("sprites", "player_large.png")
            ]
            
            for sprite_path in sprite_paths:
                if os.path.exists(sprite_path):
                    import pygame
                    player_sprite = pygame.image.load(sprite_path).convert_alpha()
                    if player_sprite:
                        self.sprite_config.surface = player_sprite
                        self.sprite_surface = player_sprite
                        print(f"✅ Player sprite geladen von {sprite_path}: {player_sprite.get_size()}")
                        return
                    else:
                        print(f"⚠️  Player sprite konnte nicht geladen werden von {sprite_path}")
                else:
                    print(f"⚠️  Player sprite nicht gefunden unter {sprite_path}")
            
            # Wenn alles fehlschlägt, verwende Standard-Sprite
            print("⚠️  Player-Sprite konnte nicht geladen werden, verwende Standard-Sprite")
            self._load_default_sprite()
            
        except Exception as e:
            print(f"❌ Fehler beim Laden des Player-Sprites: {e}")
            self._load_default_sprite()
    
    def _load_default_sprite(self) -> None:
        """Lade den Standard-Player-Sprite."""
        try:
            # Versuche den Standard-Sprite aus dem sprites-Verzeichnis zu laden
            default_path = os.path.join("sprites", "player.png")
            if os.path.exists(default_path):
                import pygame
                default_sprite = pygame.image.load(default_path).convert_alpha()
                if default_sprite:
                    self.sprite_config.surface = default_sprite
                    self.sprite_surface = default_sprite
                    print(f"Standard-Player-Sprite geladen: {default_sprite.get_size()}")
                    return
            
            # Keine Fallback-Sprites mehr erstellen - verwende echte Sprites
            print("Player-Sprite nicht gefunden, verwende Void-Sprite als Fallback")
            void_path = os.path.join("sprites", "Void_large.png")  # Verwende _large Version
            if os.path.exists(void_path):
                void_sprite = pygame.image.load(void_path).convert_alpha()
                if void_sprite:
                    # Keine Skalierung mehr nötig - _large Sprites sind bereits 64x64
                    self.sprite_config.surface = void_sprite
                    self.sprite_surface = void_sprite
                    print("Void_large-Sprite als Player-Fallback geladen")
                    return
            
            # Versuche normale Version ohne _large
            void_normal_path = os.path.join("sprites", "Void.png")
            if os.path.exists(void_normal_path):
                void_sprite = pygame.image.load(void_normal_path).convert_alpha()
                if void_sprite:
                    # Skaliere auf 64x64 falls nötig
                    if void_sprite.get_size() != (64, 64):
                        void_sprite = pygame.transform.scale(void_sprite, (64, 64))
                    self.sprite_config.surface = void_sprite
                    self.sprite_surface = void_sprite
                    print("Void-Sprite als Player-Fallback geladen und skaliert")
                    return
            
            print("Keine Sprites gefunden - Player wird nicht angezeigt")
            
        except Exception as e:
            print(f"Fehler beim Laden des Standard-Sprites: {e}")
            print("Keine Sprites verfügbar - Player wird nicht angezeigt")
    
    def set_collision_map(self, collision_layer: List[List[int]], 
                         width: int, height: int) -> None:
        """Set the collision map for movement checking."""
        self.collision_layer = collision_layer
        self.map_width = width
        self.map_height = height
    
    def handle_input(self, game: 'Game', dt: float) -> None:
        """
        Process player input for Pokémon-style movement.
        
        Args:
            game: Game instance for input checking
            dt: Delta time in seconds
        """
        # Don't process input if locked
        if self.movement_state == MovementState.LOCKED:
            return
        
        # Update turn timer
        if self.turn_timer > 0:
            self.turn_timer -= dt
        
        # Check run button (B or Shift) - requires running shoes
        run_key_pressed = game.is_key_pressed('run') or game.keys_pressed[pygame.K_LSHIFT]
        self.is_running = run_key_pressed and RunningShoes.can_run(game)
        
        # Check interaction button (A or Space)
        if game.is_key_just_pressed('confirm'):
            self._try_interact()
            return
        
        # Get movement input
        move_x = 0
        move_y = 0
        input_held = False
        
        if game.is_key_pressed('move_left'):
            move_x = -1
            input_held = True
        elif game.is_key_pressed('move_right'):
            move_x = 1
            input_held = True
        elif game.is_key_pressed('move_up'):
            move_y = -1
            input_held = True
        elif game.is_key_pressed('move_down'):
            move_y = 1
            input_held = True
        
        # Process movement based on state
        if self.movement_state == MovementState.IDLE:
            if input_held:
                # Determine if this is a tap (turn only) or hold (move)
                new_direction = Direction.from_vector(move_x, move_y)
                
                if new_direction != self.direction:
                    # Need to turn first
                    self.direction = new_direction
                    self.turn_timer = self.turn_delay
                    self.movement_state = MovementState.TURNING
                elif self.turn_timer <= 0:
                    # Already facing right direction, start moving
                    self._start_movement(move_x, move_y)
                # else: still in turn delay, wait
                
        elif self.movement_state == MovementState.TURNING:
            if not input_held:
                # Released key while turning - just turn, don't move
                self.movement_state = MovementState.IDLE
                self.turn_timer = 0.0
            elif self.turn_timer <= 0:
                # Turn delay finished, start moving
                direction = Direction.from_vector(move_x, move_y)
                if direction == self.direction:
                    self._start_movement(move_x, move_y)
                else:
                    # Changed direction again
                    self.direction = direction
                    self.turn_timer = self.turn_delay
        
        elif self.movement_state in [MovementState.WALKING, MovementState.RUNNING]:
            # Currently moving between tiles
            if input_held:
                # Buffer next input
                self.input_buffer = (move_x, move_y)
            else:
                # Clear buffer if no input
                self.input_buffer = None
    
    def _start_movement(self, dx: int, dy: int) -> None:
        """
        Start moving to the next tile.
        
        Args:
            dx: Direction X (-1, 0, 1)
            dy: Direction Y (-1, 0, 1)
        """
        # Calculate target tile
        target_x = self.grid_x + dx
        target_y = self.grid_y + dy
        
        # Check if target is valid
        if self._can_move_to_tile(target_x, target_y):
            # Start moving
            self.target_grid_x = target_x
            self.target_grid_y = target_y
            self.move_progress = 0.0
            
            # Set movement state
            if self.is_running:
                self.movement_state = MovementState.RUNNING
                self.animation_speed_multiplier = 1.5
            else:
                self.movement_state = MovementState.WALKING
                self.animation_speed_multiplier = 1.0
            
            # Update direction
            self.direction = Direction.from_vector(dx, dy)
            self.moving = True
            
        else:
            # Check if we can jump over a ledge
            if self._can_jump_ledge(dx, dy):
                self._execute_ledge_jump(dx, dy)
            else:
                # Can't move - check for collision events
                self._handle_collision(target_x, target_y)
    
    def _can_move_to_tile(self, tile_x: int, tile_y: int) -> bool:
        """
        Check if the player can move to a tile.
        
        Args:
            tile_x: Target tile X
            tile_y: Target tile Y
            
        Returns:
            True if movement is allowed
        """
        # Check map bounds
        if tile_x < 0 or tile_x >= self.map_width:
            return False
        if tile_y < 0 or tile_y >= self.map_height:
            return False
        
        # Check collision layer
        if self.collision_layer:
            if self.collision_layer[tile_y][tile_x] != 0:
                return False
        
        return True
    
    def _handle_collision(self, tile_x: int, tile_y: int) -> None:
        """
        Handle collision with a tile.
        
        Args:
            tile_x: Collided tile X
            tile_y: Collided tile Y
        """
        # Play bump sound (optional)
        # resources.play_sound("bump.wav")
        
        # Check if it's an interactable
        if self.collision_callback:
            self.collision_callback(tile_x, tile_y)
        
        # Auto-interact with NPCs/Objects when walking into them
        if self.interact_callback:
            self.interact_callback((tile_x, tile_y))
    
    def _can_jump_ledge(self, dx: int, dy: int) -> bool:
        """
        Check if the player can jump over a ledge in the given direction.
        
        Args:
            dx: Direction X (-1, 0, 1)
            dy: Direction Y (-1, 0, 1)
            
        Returns:
            True if ledge jumping is possible
        """
        if not self.collision_layer:
            return False
        
        # Get current tile position
        current_tile = (self.grid_x, self.grid_y)
        direction = Direction.from_vector(dx, dy)
        
        # Check if we can jump over this ledge
        return LedgeHandler.can_jump_ledge(current_tile, direction, self.collision_layer)
    
    def _execute_ledge_jump(self, dx: int, dy: int) -> None:
        """
        Execute a ledge jump in the given direction.
        
        Args:
            dx: Direction X (-1, 0, 1)
            dy: Direction Y (-1, 0, 1)
        """
        # Calculate target tile (the ledge tile)
        target_x = self.grid_x + dx
        target_y = self.grid_y + dy
        
        # Execute the ledge jump using LedgeHandler
        LedgeHandler.execute_ledge_jump(self, target_x, target_y)
    
    def update(self, dt: float) -> None:
        """
        Update player movement and animation.
        
        Args:
            dt: Delta time in seconds
        """
        # Update movement between tiles
        if self.movement_state in [MovementState.WALKING, MovementState.RUNNING]:
            # Calculate movement speed
            current_speed = self.run_speed if self.movement_state == MovementState.RUNNING else self.move_speed
            
            # Update progress
            self.move_progress += current_speed * dt
            
            if self.move_progress >= 1.0:
                # Reached target tile
                self.move_progress = 1.0
                
                # Update grid position
                self.grid_x = self.target_grid_x
                self.grid_y = self.target_grid_y
                
                # Snap to tile position
                self.x = self.grid_x * TILE_SIZE
                self.y = self.grid_y * TILE_SIZE
                
                # Increment step counters
                self.steps_taken += 1
                self.steps_since_encounter += 1
                
                # Check for events at new position
                self._check_tile_events()
                
                # Process buffered input or stop
                if self.input_buffer:
                    dx, dy = self.input_buffer
                    self._start_movement(dx, dy)
                    self.input_buffer = None
                else:
                    # No more input, stop
                    self.movement_state = MovementState.IDLE
                    self.moving = False
                    self.move_progress = 0.0
            else:
                # Interpolate position between tiles
                start_x = self.grid_x * TILE_SIZE
                start_y = self.grid_y * TILE_SIZE
                end_x = self.target_grid_x * TILE_SIZE
                end_y = self.target_grid_y * TILE_SIZE
                
                # Smooth interpolation (ease-in-out optional)
                t = self.move_progress
                # t = self._ease_in_out(t)  # Optional smoothing
                
                self.x = start_x + (end_x - start_x) * t
                self.y = start_y + (end_y - start_y) * t
        
        # Update ledge jumping
        elif self.movement_state == MovementState.JUMPING:
            # Ledge jump uses faster movement
            jump_speed = self.run_speed * 1.5  # 50% faster than running
            
            # Update progress
            self.move_progress += jump_speed * dt
            
            if self.move_progress >= 1.0:
                # Reached landing tile
                self.move_progress = 1.0
                
                # Update grid position to landing position
                self.grid_x = self.target_grid_x
                self.grid_y = self.target_grid_y
                
                # Snap to tile position
                self.x = self.grid_x * TILE_SIZE
                self.y = self.grid_y * TILE_SIZE
                
                # Increment step counters
                self.steps_taken += 1
                self.steps_since_encounter += 1
                
                # Check for events at new position
                self._check_tile_events()
                
                # Return to idle state
                self.movement_state = MovementState.IDLE
                self.moving = False
                self.move_progress = 0.0
            else:
                # Interpolate position for jump (with arc effect)
                start_x = (self.grid_x - self.direction.vector[0]) * TILE_SIZE
                start_y = (self.grid_y - self.direction.vector[1]) * TILE_SIZE
                end_x = self.target_grid_x * TILE_SIZE
                end_y = self.target_grid_y * TILE_SIZE
                
                # Jump arc effect (parabolic)
                t = self.move_progress
                arc_height = TILE_SIZE * 0.5  # Jump height
                
                # Linear interpolation for X and Y
                self.x = start_x + (end_x - start_x) * t
                self.y = start_y + (end_y - start_y) * t
                
                # Add arc effect (jump up and down)
                arc_t = 4 * t * (1 - t)  # Parabolic curve
                self.y -= arc_height * arc_t
        
        # Update animation
        if self.sprite_config:
            self._update_animation(dt * self.animation_speed_multiplier)
    
    def _ease_in_out(self, t: float) -> float:
        """
        Smooth ease-in-out curve for movement.
        
        Args:
            t: Progress (0.0 to 1.0)
            
        Returns:
            Smoothed progress
        """
        if t < 0.5:
            return 2 * t * t
        else:
            return 1 - pow(-2 * t + 2, 2) / 2
    
    def _check_tile_events(self) -> None:
        """Check for events at the current tile position."""
        # Check for warps
        if self.warp_callback:
            self.warp_callback(self.grid_x, self.grid_y)
        
        # Check for random encounters
        if self.encounter_callback:
            self.encounter_callback(self.grid_x, self.grid_y, self.steps_since_encounter)
    
    def _try_interact(self) -> None:
        """Try to interact with the tile in front of the player."""
        # Get the tile we're facing
        dx, dy = self.direction.vector
        interact_x = self.grid_x + dx
        interact_y = self.grid_y + dy
        
        # Call interaction callback
        if self.interact_callback:
            self.interact_callback((interact_x, interact_y))
    
    def get_tile_position(self) -> Tuple[int, int]:
        """Get the current tile coordinates."""
        return (self.grid_x, self.grid_y)
    
    def set_tile_position(self, tile_x: int, tile_y: int) -> None:
        """
        Set the player's position by tile coordinates.
        
        Args:
            tile_x: Tile X coordinate
            tile_y: Tile Y coordinate
        """
        self.grid_x = tile_x
        self.grid_y = tile_y
        self.target_grid_x = tile_x
        self.target_grid_y = tile_y
        self.x = tile_x * TILE_SIZE
        self.y = tile_y * TILE_SIZE
        self.move_progress = 0.0
        self.movement_state = MovementState.IDLE
    
    def lock_movement(self, locked: bool = True) -> None:
        """
        Lock or unlock player movement.
        
        Args:
            locked: Whether movement should be locked
        """
        if locked:
            self.movement_state = MovementState.LOCKED
            self.moving = False
            self.input_buffer = None
        else:
            self.movement_state = MovementState.IDLE
    
    def teleport(self, x: float, y: float, direction: Optional[Direction] = None) -> None:
        """
        Instantly move the player to a new position.
        
        Args:
            x: Target X position in world coordinates
            y: Target Y position in world coordinates
            direction: Optional direction to face after teleport
        """
        # Calculate tile position
        self.grid_x = int(x // TILE_SIZE)
        self.grid_y = int(y // TILE_SIZE)
        self.target_grid_x = self.grid_x
        self.target_grid_y = self.grid_y
        
        # Set pixel position
        self.x = x
        self.y = y
        
        # Reset movement
        self.move_progress = 0.0
        self.movement_state = MovementState.IDLE
        self.moving = False
        self.input_buffer = None
        
        if direction:
            self.direction = direction
        
        # Reset encounter counter
        self.steps_since_encounter = 0
    
    def _get_animation_name(self) -> str:
        """Get the current animation name based on state."""
        state_prefix = 'idle'
        
        if self.movement_state == MovementState.WALKING:
            state_prefix = 'walk'
        elif self.movement_state == MovementState.RUNNING:
            state_prefix = 'run'
        elif self.moving:
            state_prefix = 'walk'
        
        direction_suffix = self.direction.name.lower()
        return f'{state_prefix}_{direction_suffix}'
    
    def set_interact_callback(self, callback: Callable) -> None:
        """Set the callback for interaction events."""
        self.interact_callback = callback
    
    def set_warp_callback(self, callback: Callable) -> None:
        """Set the callback for warp events."""
        self.warp_callback = callback
    
    def set_encounter_callback(self, callback: Callable) -> None:
        """Set the callback for encounter checks."""
        self.encounter_callback = callback
    
    def set_collision_callback(self, callback: Callable) -> None:
        """Set the callback for collision events."""
        self.collision_callback = callback

# ========================================
# 6. RUNNING SHOES ITEM - Optional
# ========================================

class RunningShoes:
    """Running shoes item that enables running"""
    
    @staticmethod
    def give_running_shoes(game):
        """Give the player running shoes"""
        game.story_manager.set_flag('has_running_shoes', True)
        game.current_scene.dialogue_box.show_text(
            "Du hast die TURBOSCHUHE erhalten! Halte B gedrückt zum Rennen!"
        )
    
    @staticmethod
    def can_run(game) -> bool:
        """Check if player can run"""
        # Can always run, or require running shoes
        return True  # or: return game.story_manager.get_flag('has_running_shoes')