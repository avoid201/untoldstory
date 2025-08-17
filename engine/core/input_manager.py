# ========================================
# 2. INPUT MANAGER - engine/core/input_manager.py
# ========================================

"""
Input Manager für Pokémon-style Controls
Verwaltet Tastenbelegung und Input-States
"""

import pygame
from typing import Dict, Set, Optional, Tuple, List
from dataclasses import dataclass


@dataclass
class InputConfig:
    """Konfiguration für Input-Mapping"""
    # Movement
    move_up: int = pygame.K_w
    move_down: int = pygame.K_s
    move_left: int = pygame.K_a
    move_right: int = pygame.K_d
    
    # Alternative arrow keys
    alt_up: int = pygame.K_UP
    alt_down: int = pygame.K_DOWN
    alt_left: int = pygame.K_LEFT
    alt_right: int = pygame.K_RIGHT
    
    # Action buttons (Pokémon-style)
    button_a: int = pygame.K_e        # Confirm/Interact
    button_b: int = pygame.K_q        # Cancel/Run
    button_x: int = pygame.K_x        # Menu
    button_y: int = pygame.K_c        # Quick Access
    
    # Alternative action buttons
    alt_confirm: int = pygame.K_SPACE
    alt_cancel: int = pygame.K_ESCAPE
    alt_run: int = pygame.K_LSHIFT
    
    # System
    pause: int = pygame.K_ESCAPE
    debug: int = pygame.K_TAB


class InputManager:
    """Enhanced input manager with responsiveness optimizations"""
    
    def __init__(self, config: Optional[InputConfig] = None):
        self.config = config or InputConfig()
        self.keys_pressed: Dict[int, bool] = {}
        self.keys_just_pressed: Set[int] = set()
        self.keys_just_released: Set[int] = set()
        
        # Input state tracking
        self.last_frame_keys: Dict[int, bool] = {}
        
        # Enhanced responsiveness features
        self.key_repeat_timers: Dict[int, float] = {}
        self.key_repeat_delay = 0.4  # Initial delay before repeat (seconds)
        self.key_repeat_rate = 0.1   # Repeat rate (seconds)
        self.input_buffer: Dict[str, float] = {}  # Input buffering
        self.buffer_window = 0.2  # Buffer window in seconds
        
        # Combo detection
        self.combo_buffer: List[Tuple[str, float]] = []
        self.combo_timeout = 0.5  # Combo timeout in seconds
        
        # Mapping for logical inputs
        self.input_map = {
            'move_up': [self.config.move_up, self.config.alt_up],
            'move_down': [self.config.move_down, self.config.alt_down],
            'move_left': [self.config.move_left, self.config.alt_left],
            'move_right': [self.config.move_right, self.config.alt_right],
            'confirm': [self.config.button_a, self.config.alt_confirm],
            'cancel': [self.config.button_b, self.config.alt_cancel],
            'run': [self.config.button_b, self.config.alt_run],
            'menu': [self.config.button_x],
            'quick': [self.config.button_y],
            'pause': [self.config.pause],
            'debug': [self.config.debug]
        }
    
    def update(self, dt: float = 0.016):
        """Update input state with enhanced features - call once per frame"""
        import time
        current_time = time.time()
        
        # Clear just pressed/released
        self.keys_just_pressed.clear()
        self.keys_just_released.clear()
        
        # Get current key state
        keys = pygame.key.get_pressed()
        
        # Check for just pressed/released and handle repeats
        for key in range(len(keys)):
            was_pressed = self.last_frame_keys.get(key, False)
            is_pressed = keys[key]
            
            if is_pressed and not was_pressed:
                self.keys_just_pressed.add(key)
                self.key_repeat_timers[key] = current_time + self.key_repeat_delay
            elif was_pressed and not is_pressed:
                self.keys_just_released.add(key)
                if key in self.key_repeat_timers:
                    del self.key_repeat_timers[key]
            elif is_pressed and key in self.key_repeat_timers:
                # Handle key repeat
                if current_time >= self.key_repeat_timers[key]:
                    self.keys_just_pressed.add(key)
                    self.key_repeat_timers[key] = current_time + self.key_repeat_rate
            
            self.keys_pressed[key] = is_pressed
        
        # Update input buffer - clean expired entries
        expired_inputs = []
        for input_name, timestamp in self.input_buffer.items():
            if current_time - timestamp > self.buffer_window:
                expired_inputs.append(input_name)
        for input_name in expired_inputs:
            del self.input_buffer[input_name]
        
        # Update combo buffer - clean expired entries
        self.combo_buffer = [(combo, timestamp) for combo, timestamp in self.combo_buffer 
                            if current_time - timestamp <= self.combo_timeout]
        
        # Store for next frame
        self.last_frame_keys = {k: v for k, v in self.keys_pressed.items()}
    
    def is_pressed(self, input_name: str) -> bool:
        """Check if a logical input is currently pressed"""
        if input_name in self.input_map:
            for key in self.input_map[input_name]:
                if self.keys_pressed.get(key, False):
                    return True
        return False
    
    def is_just_pressed(self, input_name: str) -> bool:
        """Check if a logical input was just pressed this frame"""
        if input_name in self.input_map:
            for key in self.input_map[input_name]:
                if key in self.keys_just_pressed:
                    return True
        return False
    
    def is_just_released(self, input_name: str) -> bool:
        """Check if a logical input was just released this frame"""
        if input_name in self.input_map:
            for key in self.input_map[input_name]:
                if key in self.keys_just_released:
                    return True
        return False
    
    def get_movement_vector(self) -> Tuple[int, int]:
        """Get the current movement input as a vector"""
        x = 0
        y = 0
        
        if self.is_pressed('move_left'):
            x = -1
        elif self.is_pressed('move_right'):
            x = 1
        
        if self.is_pressed('move_up'):
            y = -1
        elif self.is_pressed('move_down'):
            y = 1
        
        return (x, y)
    
    def buffer_input(self, input_name: str) -> None:
        """Buffer an input for responsive gameplay"""
        import time
        self.input_buffer[input_name] = time.time()
    
    def consume_buffered_input(self, input_name: str) -> bool:
        """Check and consume a buffered input"""
        if input_name in self.input_buffer:
            del self.input_buffer[input_name]
            return True
        return False
    
    def register_combo(self, input_name: str) -> None:
        """Register an input for combo detection"""
        import time
        self.combo_buffer.append((input_name, time.time()))
    
    def check_combo(self, combo_sequence: List[str]) -> bool:
        """Check if a combo sequence was input recently"""
        if len(self.combo_buffer) < len(combo_sequence):
            return False
        
        # Check last N inputs match the combo
        recent_inputs = [combo for combo, _ in self.combo_buffer[-len(combo_sequence):]]
        return recent_inputs == combo_sequence
    
    def set_repeat_settings(self, delay: float = 0.4, rate: float = 0.1) -> None:
        """Configure key repeat timing"""
        self.key_repeat_delay = delay
        self.key_repeat_rate = rate
    
    def get_input_debug_info(self) -> Dict:
        """Get debug information about current input state"""
        return {
            'pressed_keys': [k for k, v in self.keys_pressed.items() if v],
            'just_pressed': list(self.keys_just_pressed),
            'just_released': list(self.keys_just_released),
            'buffered_inputs': list(self.input_buffer.keys()),
            'combo_buffer': [combo for combo, _ in self.combo_buffer],
            'repeat_timers': len(self.key_repeat_timers)
        }
