# ========================================
# 2. INPUT MANAGER - engine/core/input_manager.py
# ========================================

"""
Input Manager für Pokémon-style Controls
Verwaltet Tastenbelegung und Input-States
"""

import pygame
from typing import Dict, Set, Optional, Tuple
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
    """Manages input state and provides clean input API"""
    
    def __init__(self, config: Optional[InputConfig] = None):
        self.config = config or InputConfig()
        self.keys_pressed: Dict[int, bool] = {}
        self.keys_just_pressed: Set[int] = set()
        self.keys_just_released: Set[int] = set()
        
        # Input state tracking
        self.last_frame_keys: Dict[int, bool] = {}
        
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
    
    def update(self):
        """Update input state - call once per frame before processing events"""
        # Clear just pressed/released
        self.keys_just_pressed.clear()
        self.keys_just_released.clear()
        
        # Get current key state
        keys = pygame.key.get_pressed()
        
        # Check for just pressed/released
        for key in range(len(keys)):
            was_pressed = self.last_frame_keys.get(key, False)
            is_pressed = keys[key]
            
            if is_pressed and not was_pressed:
                self.keys_just_pressed.add(key)
            elif was_pressed and not is_pressed:
                self.keys_just_released.add(key)
            
            self.keys_pressed[key] = is_pressed
        
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
