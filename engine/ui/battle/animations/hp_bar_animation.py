"""
HP Bar Animation System
Verantwortlich für smooth HP-Bar-Animationen mit Interpolation
"""

import pygame
import math
from typing import Any, Dict, Optional
from dataclasses import dataclass

# Setup logger
import logging
logger = logging.getLogger(__name__)


@dataclass
class HPBarAnimation:
    """HP-Bar Animation mit smooth interpolation."""
    monster_id: Any
    old_hp: int
    new_hp: int
    max_hp: int
    current_hp: int
    timer: float
    duration: float
    speed: float = 2.0  # HP per frame
    active: bool = True
    easing: str = "ease_out_cubic"  # Animation easing type


class HPBarAnimator:
    """
    HP-Bar Animator für smooth Animationen.
    ENHANCED: Optimiert für 60 FPS Performance.
    """
    
    def __init__(self):
        self.animations: Dict[Any, HPBarAnimation] = {}
        self.animation_speed = 2.0  # HP per frame
        self.easing_functions = {
            "linear": self._ease_linear,
            "ease_in": self._ease_in,
            "ease_out": self._ease_out,
            "ease_in_out": self._ease_in_out,
            "ease_out_cubic": self._ease_out_cubic,
            "bounce": self._ease_bounce
        }
    
    def add_animation(self, monster_id: Any, new_hp: int, max_hp: int, 
                     duration: float = 0.8, easing: str = "ease_out_cubic") -> None:
        """Füge neue HP-Animation hinzu."""
        if monster_id in self.animations:
            # Update existing animation
            anim = self.animations[monster_id]
            anim.old_hp = anim.current_hp
            anim.new_hp = new_hp
            anim.timer = 0.0
            anim.duration = duration
            anim.easing = easing
        else:
            # Create new animation
            self.animations[monster_id] = HPBarAnimation(
                monster_id=monster_id,
                old_hp=new_hp,
                new_hp=new_hp,
                max_hp=max_hp,
                current_hp=new_hp,
                timer=0.0,
                duration=duration,
                easing=easing
            )
    
    def update(self, dt: float) -> Dict[Any, float]:
        """Update alle HP-Animationen."""
        updated_ratios = {}
        
        for monster_id, anim in list(self.animations.items()):
            if not anim.active:
                continue
            
            # Update timer
            anim.timer += dt
            
            # Calculate progress (0.0 to 1.0)
            progress = min(anim.timer / anim.duration, 1.0)
            
            # Apply easing
            eased_progress = self.easing_functions.get(anim.easing, self._ease_linear)(progress)
            
            # Interpolate HP value
            anim.current_hp = int(anim.old_hp + (anim.new_hp - anim.old_hp) * eased_progress)
            
            # Calculate HP ratio for UI
            hp_ratio = anim.current_hp / anim.max_hp if anim.max_hp > 0 else 0
            updated_ratios[monster_id] = max(0.0, min(1.0, hp_ratio))
            
            # Remove completed animations
            if progress >= 1.0:
                anim.active = False
                del self.animations[monster_id]
        
        return updated_ratios
    
    def get_current_hp(self, monster_id: Any) -> Optional[int]:
        """Get current animated HP value."""
        if monster_id in self.animations:
            return self.animations[monster_id].current_hp
        return None
    
    def remove_animation(self, monster_id: Any) -> None:
        """Remove animation for specific monster."""
        if monster_id in self.animations:
            del self.animations[monster_id]
    
    def clear_all_animations(self) -> None:
        """Clear all animations."""
        self.animations.clear()
    
    # Easing functions
    def _ease_linear(self, t: float) -> float:
        return t
    
    def _ease_in(self, t: float) -> float:
        return t * t
    
    def _ease_out(self, t: float) -> float:
        return 1 - (1 - t) * (1 - t)
    
    def _ease_in_out(self, t: float) -> float:
        if t < 0.5:
            return 2 * t * t
        return 1 - 2 * (1 - t) * (1 - t)
    
    def _ease_out_cubic(self, t: float) -> float:
        """Smooth cubic easing out - perfect for HP bars."""
        return 1 - (1 - t) ** 3
    
    def _ease_bounce(self, t: float) -> float:
        """Bouncy easing - fun for special effects."""
        if t < 1/2.75:
            return 7.5625 * t * t
        elif t < 2/2.75:
            t -= 1.5/2.75
            return 7.5625 * t * t + 0.75
        elif t < 2.5/2.75:
            t -= 2.25/2.75
            return 7.5625 * t * t + 0.9375
        else:
            t -= 2.625/2.75
            return 7.5625 * t * t + 0.984375
