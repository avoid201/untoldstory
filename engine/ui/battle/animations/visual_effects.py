"""
Visual Effects System
Verantwortlich für Screen-Effects, Camera-Shake und andere visuelle Effekte
"""

import pygame
import math
import random
from typing import Dict, Any, Tuple, Optional
from dataclasses import dataclass

# Setup logger
import logging
logger = logging.getLogger(__name__)


@dataclass
class VisualEffect:
    """Visual Effect für Screen-Effects."""
    effect_type: str
    timer: float
    duration: float
    intensity: float
    color: Tuple[int, int, int]
    position: Tuple[float, float]
    active: bool = True
    data: Dict[str, Any] = None


class VisualEffectsManager:
    """
    Visual Effects Manager für Screen-Effects und Camera-Shake.
    ENHANCED: Optimiert für 60 FPS Performance.
    """
    
    def __init__(self):
        self.effects: Dict[str, VisualEffect] = {}
        self.camera_shake = {
            "active": False,
            "intensity": 0.0,
            "duration": 0.0,
            "timer": 0.0,
            "offset": (0.0, 0.0)
        }
        
        # Effect types
        self.effect_types = {
            "screen_flash": self._update_screen_flash,
            "screen_shake": self._update_screen_shake,
            "particle_burst": self._update_particle_burst,
            "damage_flash": self._update_damage_flash
        }
    
    def trigger_screen_flash(self, color: Tuple[int, int, int] = (255, 255, 255), 
                           intensity: float = 0.8, duration: float = 0.3) -> None:
        """Trigger screen flash effect."""
        self.effects["screen_flash"] = VisualEffect(
            effect_type="screen_flash",
            timer=0.0,
            duration=duration,
            intensity=intensity,
            color=color,
            position=(0.0, 0.0),
            active=True
        )
        logger.debug(f"Screen flash triggered: color={color}, intensity={intensity}")
    
    def trigger_screen_shake(self, intensity: float = 5.0, duration: float = 0.3) -> None:
        """Trigger screen shake effect."""
        self.camera_shake.update({
            "active": True,
            "intensity": intensity,
            "duration": duration,
            "timer": 0.0,
            "offset": (0.0, 0.0)
        })
        logger.debug(f"Screen shake triggered: intensity={intensity}")
    
    def trigger_damage_flash(self, position: Tuple[int, int], color: Tuple[int, int, int] = (255, 100, 100),
                           intensity: float = 0.6, duration: float = 0.2) -> None:
        """Trigger damage flash at specific position."""
        effect_id = f"damage_flash_{len(self.effects)}"
        self.effects[effect_id] = VisualEffect(
            effect_type="damage_flash",
            timer=0.0,
            duration=duration,
            intensity=intensity,
            color=color,
            position=position,
            active=True
        )
    
    def trigger_particle_burst(self, position: Tuple[int, int], color: Tuple[int, int, int] = (255, 255, 255),
                             count: int = 10, duration: float = 1.0) -> None:
        """Trigger particle burst effect."""
        effect_id = f"particle_burst_{len(self.effects)}"
        self.effects[effect_id] = VisualEffect(
            effect_type="particle_burst",
            timer=0.0,
            duration=duration,
            intensity=1.0,
            color=color,
            position=position,
            active=True,
            data={"count": count, "particles": []}
        )
        
        # Generate particles
        particles = []
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(50, 150)
            particle = {
                "position": [float(position[0]), float(position[1])],
                "velocity": [math.cos(angle) * speed, math.sin(angle) * speed],
                "life": 1.0,
                "size": random.uniform(2, 5)
            }
            particles.append(particle)
        
        self.effects[effect_id].data["particles"] = particles
    
    def update(self, dt: float) -> None:
        """Update alle Visual Effects."""
        # Update camera shake
        if self.camera_shake["active"]:
            self.camera_shake["timer"] += dt
            
            if self.camera_shake["timer"] >= self.camera_shake["duration"]:
                self.camera_shake["active"] = False
                self.camera_shake["offset"] = (0.0, 0.0)
            else:
                # Generate shake offset
                intensity = self.camera_shake["intensity"] * (1.0 - self.camera_shake["timer"] / self.camera_shake["duration"])
                offset_x = random.uniform(-intensity, intensity)
                offset_y = random.uniform(-intensity, intensity)
                self.camera_shake["offset"] = (offset_x, offset_y)
        
        # Update effects
        for effect_id, effect in list(self.effects.items()):
            if not effect.active:
                continue
            
            effect.timer += dt
            
            # Update based on effect type
            if effect.effect_type in self.effect_types:
                self.effect_types[effect.effect_type](effect, dt)
            
            # Remove completed effects
            if effect.timer >= effect.duration:
                effect.active = False
                del self.effects[effect_id]
    
    def render(self, surface: pygame.Surface) -> None:
        """Render alle Visual Effects."""
        # Apply camera shake offset
        if self.camera_shake["active"]:
            shake_surface = surface.copy()
            surface.fill((0, 0, 0))
            surface.blit(shake_surface, self.camera_shake["offset"])
        
        # Render effects
        for effect in self.effects.values():
            if not effect.active:
                continue
            
            if effect.effect_type == "screen_flash":
                self._render_screen_flash(surface, effect)
            elif effect.effect_type == "damage_flash":
                self._render_damage_flash(surface, effect)
            elif effect.effect_type == "particle_burst":
                self._render_particle_burst(surface, effect)
    
    def get_camera_offset(self) -> Tuple[float, float]:
        """Get current camera shake offset."""
        return self.camera_shake["offset"]
    
    def clear_all_effects(self) -> None:
        """Clear alle Visual Effects."""
        self.effects.clear()
        self.camera_shake["active"] = False
        self.camera_shake["offset"] = (0.0, 0.0)
    
    # Private update methods
    def _update_screen_flash(self, effect: VisualEffect, dt: float) -> None:
        """Update screen flash effect."""
        # Flash intensity decreases over time
        effect.intensity = max(0.0, effect.intensity - dt * 2.0)
    
    def _update_screen_shake(self, effect: VisualEffect, dt: float) -> None:
        """Update screen shake effect."""
        # Shake intensity decreases over time
        effect.intensity = max(0.0, effect.intensity - dt * 2.0)
    
    def _update_damage_flash(self, effect: VisualEffect, dt: float) -> None:
        """Update damage flash effect."""
        # Flash intensity decreases over time
        effect.intensity = max(0.0, effect.intensity - dt * 3.0)
    
    def _update_particle_burst(self, effect: VisualEffect, dt: float) -> None:
        """Update particle burst effect."""
        if not effect.data or "particles" not in effect.data:
            return
        
        particles = effect.data["particles"]
        for particle in particles:
            # Update position
            particle["position"][0] += particle["velocity"][0] * dt
            particle["position"][1] += particle["velocity"][1] * dt
            
            # Update life
            particle["life"] -= dt / effect.duration
            
            # Apply gravity
            particle["velocity"][1] += 200 * dt
    
    # Private render methods
    def _render_screen_flash(self, surface: pygame.Surface, effect: VisualEffect) -> None:
        """Render screen flash effect."""
        if effect.intensity > 0:
            flash_surface = pygame.Surface(surface.get_size())
            flash_surface.set_alpha(int(effect.intensity * 255))
            flash_surface.fill(effect.color)
            surface.blit(flash_surface, (0, 0))
    
    def _render_damage_flash(self, surface: pygame.Surface, effect: VisualEffect) -> None:
        """Render damage flash effect."""
        if effect.intensity > 0:
            # Create flash circle
            radius = int(20 * effect.intensity)
            if radius > 0:
                flash_surface = pygame.Surface((radius * 2, radius * 2))
                flash_surface.set_alpha(int(effect.intensity * 255))
                pygame.draw.circle(flash_surface, effect.color, (radius, radius), radius)
                
                # Render at position
                render_pos = (
                    int(effect.position[0] - radius),
                    int(effect.position[1] - radius)
                )
                surface.blit(flash_surface, render_pos)
    
    def _render_particle_burst(self, surface: pygame.Surface, effect: VisualEffect) -> None:
        """Render particle burst effect."""
        if not effect.data or "particles" not in effect.data:
            return
        
        particles = effect.data["particles"]
        for particle in particles:
            if particle["life"] > 0:
                # Create particle surface
                size = int(particle["size"])
                particle_surface = pygame.Surface((size, size))
                particle_surface.set_alpha(int(particle["life"] * 255))
                particle_surface.fill(effect.color)
                
                # Render particle
                render_pos = (
                    int(particle["position"][0] - size // 2),
                    int(particle["position"][1] - size // 2)
                )
                surface.blit(particle_surface, render_pos)
