# -*- coding: utf-8 -*-
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, List, Tuple, Callable
import pygame

from engine.world.entity import Entity, Direction, EntitySprite
from engine.world.tiles import TILE_SIZE, world_to_tile
from engine.world.movement_states import MovementState
from engine.world.ledge_handler import LedgeHandler
from engine.items.running_shoes import RunningShoes

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
            frame_width=16,   # 16x16 Pixel Sprites
            frame_height=16,  # 16x16 Pixel Sprites
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
        super().__init__(x, y, width=14, height=14, sprite_config=sprite_config)  # 14x14 Pixel für 16x16 Tiles
        
        # Player properties
        self.name = "Player"
        self.movement_state = MovementState.IDLE
        
        # Grid-based movement
        self.grid_x = int(x // TILE_SIZE)  # Current tile X
        self.grid_y = int(y // TILE_SIZE)  # Current tile Y
        self.target_grid_x = self.grid_x   # Target tile X
        self.target_grid_y = self.grid_y   # Target tile Y
        
        # Movement timing (Pokémon Crystal Gefühl)
        # Crystal: ~8 Frames pro Tile bei ~60 FPS => ~0.133s pro Tile => ~7.5 Tiles/s
        self.move_progress = 0.0      # 0.0 = at current tile, 1.0 = at target tile
        self.move_speed = 7.5         # Tiles pro Sekunde (Gehen)
        # run_speed wird dynamisch über RunningShoes.get_running_speed_multiplier() berechnet
        # Turn-Verzögerung wird nicht erzwungen; kurzer Tap dreht nur
        self.turn_delay = 0.0
        self.turn_timer = 0.0
        
        # Input handling
        self.input_buffer = None      # Buffered input direction
        self.is_running = False       # B button held
        # Tap/Turn Handling wird über is_just_pressed vom Input-Manager umgesetzt
        
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
        
        # Game reference for RunningShoes
        self._game_ref = None
        
        # Load player sprite after initialization
        self._load_player_sprite()
    
    def _load_player_sprite(self) -> None:
        """Load the player sprite from the SpriteManager."""
        try:
            from engine.graphics.sprite_manager import SpriteManager
            
            sprite_manager = SpriteManager.get()
            
            # Lade das Standard-Sprite (nach unten blickend)
            player_sprite = sprite_manager.get_player("down")
            if player_sprite:
                self.sprite_config.surface = player_sprite
                self.sprite_surface = player_sprite
                print(f"✅ Player sprite geladen: {player_sprite.get_size()}")
            else:
                print("❌ Player sprite nicht im SpriteManager gefunden")
            
        except Exception as e:
            print(f"❌ Fehler beim Laden des Player-Sprites: {e}")
    
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
        # Store game reference for RunningShoes
        self._game_ref = game
        
        # Debug: Zeige dass handle_input aufgerufen wird
        if not hasattr(self, '_handle_input_called'):
            print(f"🎮 handle_input() wird aufgerufen! State={self.movement_state}")
            self._handle_input_called = True
        
        # Don't process input if locked
        if self.movement_state == MovementState.LOCKED:
            return
        

        
        # Check run button (über Input-Manager) - requires running shoes
        self.is_running = game.input_manager.is_pressed('run') and RunningShoes.can_run(game)
        
        # Check interaction button (A or Space)
        if game.input_manager.is_just_pressed('confirm'):
            self._try_interact()
            return
        
        # Get movement input (Pokémon-Style: Tap = drehen, Hold = sofort laufen)
        # Löse diagonale Eingaben zu einer Achse auf
        pressed_left = game.input_manager.is_pressed('move_left')
        pressed_right = game.input_manager.is_pressed('move_right')
        pressed_up = game.input_manager.is_pressed('move_up')
        pressed_down = game.input_manager.is_pressed('move_down')
        
        # Debug: Zeige Input wenn erkannt (reduziert)
        if pressed_left or pressed_right or pressed_up or pressed_down:
            if not hasattr(self, '_last_input_combo') or self._last_input_combo != (pressed_left, pressed_right, pressed_up, pressed_down):
                print(f"🎮 INPUT: ←{pressed_left} →{pressed_right} ↑{pressed_up} ↓{pressed_down}")
                self._last_input_combo = (pressed_left, pressed_right, pressed_up, pressed_down)
        
        # Helper: Prüfe, ob die jeweilige Richtung in diesem Frame getappt wurde
        just_left = game.input_manager.is_just_pressed('move_left')
        just_right = game.input_manager.is_just_pressed('move_right')
        just_up = game.input_manager.is_just_pressed('move_up')
        just_down = game.input_manager.is_just_pressed('move_down')
        
        def direction_just_pressed(dir_obj: Direction) -> bool:
            if dir_obj == Direction.LEFT:
                return just_left
            if dir_obj == Direction.RIGHT:
                return just_right
            if dir_obj == Direction.UP:
                return just_up
            if dir_obj == Direction.DOWN:
                return just_down
            return False
        
        def compute_axis_move() -> Tuple[int, int]:
            # Bestimme gewünschte Achse
            horiz = (pressed_left != pressed_right)  # genau eine der beiden
            vert = (pressed_up != pressed_down)      # genau eine der beiden
            # Bevorzugung: Wenn nur eine Achse aktiv, nimm diese. Wenn beide, entscheide nach Tap/letzter Richtung.
            if horiz and not vert:
                return (-1 if pressed_left else 1, 0)
            if vert and not horiz:
                return (0, -1 if pressed_up else 1)
            if horiz and vert:
                # Wenn genau eine Achse in diesem Frame neu gedrückt wurde, nimm diese
                horiz_just = just_left or just_right
                vert_just = just_up or just_down
                if horiz_just ^ vert_just:
                    if horiz_just:
                        return (-1 if pressed_left else 1, 0)
                    else:
                        return (0, -1 if pressed_up else 1)
                # Sonst: nimm die Achse der aktuellen Blickrichtung
                if self.direction in (Direction.LEFT, Direction.RIGHT):
                    return (-1 if pressed_left else 1, 0)
                else:
                    return (0, -1 if pressed_up else 1)
            # Keine Eingabe
            return (0, 0)
        
        move_x, move_y = compute_axis_move()
        input_held = (move_x != 0 or move_y != 0)
        
        # Process movement based on state
        if self.movement_state == MovementState.IDLE:
            if input_held:
                new_direction = Direction.from_vector(move_x, move_y)
                if new_direction != self.direction:
                    # Tap dreht nur (wenn gerade in diesem Frame gedrückt)
                    if direction_just_pressed(new_direction):
                        self.direction = new_direction
                        self._update_sprite_for_direction()
                        # Bleibe IDLE (kein Move bei Tap)
                    else:
                        # Taste wird gehalten: starte sofortige Bewegung
                        self._start_movement(move_x, move_y)
                else:
                    # Bereits ausgerichtet: starte Bewegung sofort
                    self._start_movement(move_x, move_y)
                

        
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
            self._update_sprite_for_direction()
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
            # Calculate movement speed - verwende RunningShoes Multiplier
            if self.movement_state == MovementState.RUNNING:
                # Hole Speed Multiplier von RunningShoes
                try:
                    from engine.core.game import Game
                    if hasattr(self, '_game_ref'):
                        multiplier = RunningShoes.get_running_speed_multiplier(self._game_ref)
                        current_speed = self.move_speed * multiplier
                    else:
                        # Fallback falls kein Game-Ref verfügbar
                        current_speed = self.move_speed * 1.5
                except:
                    # Fallback falls RunningShoes nicht verfügbar
                    current_speed = self.move_speed * 1.5
            else:
                current_speed = self.move_speed
            
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
                
                # Process buffered input or continue if key still held
                next_dx_dy = None
                if self.input_buffer:
                    next_dx_dy = self.input_buffer
                    self.input_buffer = None
                else:
                    # Falls keine Pufferung, setze Input auf None
                    # (compute_axis_move ist eine lokale Funktion in handle_input)
                    next_dx_dy = None
                
                if next_dx_dy:
                    self._start_movement(next_dx_dy[0], next_dx_dy[1])
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
            # Ledge jump uses faster movement - 50% faster than running
            try:
                if hasattr(self, '_game_ref'):
                    run_multiplier = RunningShoes.get_running_speed_multiplier(self._game_ref)
                    jump_speed = self.move_speed * run_multiplier * 1.5
                else:
                    jump_speed = self.move_speed * 1.5 * 1.5  # Fallback
            except:
                jump_speed = self.move_speed * 1.5 * 1.5  # Fallback
            
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
            self._update_sprite_for_direction()
        
        # Reset encounter counter
        self.steps_since_encounter = 0
    
    def _update_sprite_for_direction(self) -> None:
        """Update the player sprite based on current direction."""
        try:
            from engine.graphics.sprite_manager import SpriteManager
            
            sprite_manager = SpriteManager.get()
            direction_name = self.direction.name.lower()  # "up", "down", "left", "right"
            
            player_sprite = sprite_manager.get_player(direction_name)
            if player_sprite:
                self.sprite_config.surface = player_sprite
                self.sprite_surface = player_sprite
            
        except Exception as e:
            print(f"Fehler beim Aktualisieren des Player-Sprites: {e}")
    
    def draw(self, surface: pygame.Surface, camera_offset: Tuple[float, float]) -> None:
        """Custom draw method for player to bypass complex frame logic."""
        if not self.visible:
            return
            
        # Calculate screen position
        screen_x = int(self.x - camera_offset[0])
        screen_y = int(self.y - camera_offset[1])
        
        if self.sprite_surface:
            # Simple sprite drawing - no frame calculation
            surface.blit(self.sprite_surface, (screen_x, screen_y))
        else:
            # Fallback rectangle
            color = (0, 100, 255)  # Blue for player
            pygame.draw.rect(surface, color, (screen_x, screen_y, 16, 16))
    
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