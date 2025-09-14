"""
Damage Number Animation System
Verantwortlich für float-up Damage-Numbers mit Animationen
"""

import pygame
import random
import math
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass

# Setup logger
import logging
logger = logging.getLogger(__name__)


@dataclass
class DamageNumberAnimation:
    """Damage-Number mit float-up Animation."""
    value: int
    position: Tuple[float, float]
    velocity: Tuple[float, float]
    color: Tuple[int, int, int]
    timer: float
    duration: float = 1.5
    alpha: int = 255
    scale: float = 1.0
    active: bool = True
    animation_type: str = "float_up"  # float_up, bounce, fade


class DamageNumberRenderer:
    """
    Damage-Number Renderer für float-up Animationen.
    ENHANCED: Optimiert für 60 FPS Performance.
    """
    
    def __init__(self):
        self.animations: List[DamageNumberAnimation] = []
        self.font = pygame.font.Font(None, 24)
        self.critical_font = pygame.font.Font(None, 28)
        
        # Animation settings
        self.float_speed = 30.0  # pixels per second
        self.fade_speed = 200.0  # alpha per second
        self.scale_speed = 0.5   # scale per second
        
        # Color schemes
        self.color_schemes = {
            "damage": (255, 100, 100),      # Red
            "critical": (255, 255, 0),      # Yellow
            "super_effective": (255, 200, 0), # Orange
            "healing": (100, 255, 100),     # Green
            "miss": (200, 200, 200),        # Gray
            "status": (255, 150, 255)       # Magenta
        }
    
    def add_damage_number(self, value: int, position: Tuple[int, int], 
                         is_critical: bool = False, is_super_effective: bool = False,
                         is_healing: bool = False, is_miss: bool = False) -> None:
        """Füge Damage-Number hinzu."""
        # Determine color
        if is_miss:
            color = self.color_schemes["miss"]
            value = "MISS"
        elif is_healing:
            color = self.color_schemes["healing"]
        elif is_critical and is_super_effective:
            color = self.color_schemes["super_effective"]
        elif is_critical:
            color = self.color_schemes["critical"]
        elif is_super_effective:
            color = self.color_schemes["super_effective"]
        else:
            color = self.color_schemes["damage"]
        
        # Random velocity for natural movement
        velocity = (
            random.uniform(-20, 20),  # Horizontal drift
            -self.float_speed - random.uniform(0, 20)  # Upward movement
        )
        
        # Create animation
        anim = DamageNumberAnimation(
            value=value,
            position=(float(position[0]), float(position[1])),
            velocity=velocity,
            color=color,
            timer=0.0,
            duration=1.5,
            alpha=255,
            scale=1.0,
            active=True,
            animation_type="float_up"
        )
        
        self.animations.append(anim)
        logger.debug(f"Added damage number: {value} at {position}")
    
    def update(self, dt: float) -> None:
        """Update alle Damage-Number Animationen."""
        for anim in list(self.animations):
            if not anim.active:
                continue
            
            # Update timer
            anim.timer += dt
            
            # Update position
            anim.position = (
                anim.position[0] + anim.velocity[0] * dt,
                anim.position[1] + anim.velocity[1] * dt
            )
            
            # Update alpha (fade out)
            anim.alpha = max(0, int(255 - (anim.timer * self.fade_speed)))
            
            # Update scale (grow then shrink)
            if anim.timer < 0.3:
                # Grow phase
                anim.scale = 1.0 + (anim.timer / 0.3) * 0.5
            else:
                # Shrink phase
                remaining_time = anim.duration - anim.timer
                if remaining_time > 0:
                    anim.scale = 1.5 - ((anim.timer - 0.3) / (anim.duration - 0.3)) * 0.5
                else:
                    anim.scale = 1.0
            
            # Remove completed animations
            if anim.timer >= anim.duration or anim.alpha <= 0:
                anim.active = False
                self.animations.remove(anim)
    
    def render(self, surface: pygame.Surface) -> None:
        """Render alle aktiven Damage-Numbers."""
        for anim in self.animations:
            if not anim.active or anim.alpha <= 0:
                continue
            
            # Choose font based on value
            font = self.critical_font if isinstance(anim.value, int) and anim.value > 50 else self.font
            
            # Create text surface with alpha
            text_surface = font.render(str(anim.value), True, anim.color)
            
            # Apply scale
            if anim.scale != 1.0:
                new_size = (int(text_surface.get_width() * anim.scale), 
                           int(text_surface.get_height() * anim.scale))
                if new_size[0] > 0 and new_size[1] > 0:
                    text_surface = pygame.transform.scale(text_surface, new_size)
            
            # Apply alpha
            if anim.alpha < 255:
                text_surface.set_alpha(anim.alpha)
            
            # Render with offset for centering
            render_pos = (
                int(anim.position[0] - text_surface.get_width() / 2),
                int(anim.position[1] - text_surface.get_height() / 2)
            )
            
            surface.blit(text_surface, render_pos)
    
    def clear_all(self) -> None:
        """Clear alle Damage-Numbers."""
        self.animations.clear()
    
    def get_active_count(self) -> int:
        """Get Anzahl aktiver Animationen."""
        return len([anim for anim in self.animations if anim.active])
