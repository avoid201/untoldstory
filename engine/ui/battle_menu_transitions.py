"""
Battle Menu Transitions - Phase 2 UI Polish
Provides smooth visual transitions between menu states
"""

import pygame
import math
from typing import Optional, Tuple
from enum import Enum, auto


class TransitionType(Enum):
    """Types of menu transitions."""
    SLIDE_LEFT = auto()
    SLIDE_RIGHT = auto()
    SLIDE_UP = auto() 
    SLIDE_DOWN = auto()
    FADE_IN = auto()
    FADE_OUT = auto()
    SCALE_IN = auto()
    SCALE_OUT = auto()


class MenuTransitionManager:
    """Manages smooth transitions between battle menus."""
    
    def __init__(self):
        self.is_transitioning = False
        self.transition_type = None
        self.transition_progress = 0.0
        self.transition_duration = 0.3  # 300ms transitions
        self.transition_timer = 0.0
        
        # Transition surfaces for double-buffering
        self.from_surface = None
        self.to_surface = None
        
    def start_transition(self, transition_type: TransitionType, 
                        from_surface: pygame.Surface, 
                        to_surface: pygame.Surface):
        """Start a menu transition."""
        self.is_transitioning = True
        self.transition_type = transition_type
        self.transition_progress = 0.0
        self.transition_timer = 0.0
        
        # Store transition surfaces
        self.from_surface = from_surface.copy() if from_surface else None
        self.to_surface = to_surface.copy() if to_surface else None
    
    def update(self, dt: float) -> bool:
        """Update transition. Returns True if transition is complete."""
        if not self.is_transitioning:
            return True
        
        self.transition_timer += dt
        self.transition_progress = min(1.0, self.transition_timer / self.transition_duration)
        
        # Apply easing for smoother transitions
        self.transition_progress = self._ease_out_quad(self.transition_progress)
        
        # Check if transition is complete
        if self.transition_progress >= 1.0:
            self.is_transitioning = False
            return True
        
        return False
    
    def draw_transition(self, surface: pygame.Surface) -> None:
        """Draw the current transition state."""
        if not self.is_transitioning or not self.from_surface or not self.to_surface:
            return
        
        surface_width = surface.get_width()
        surface_height = surface.get_height()
        
        if self.transition_type == TransitionType.SLIDE_LEFT:
            # Slide left transition
            offset = int(surface_width * self.transition_progress)
            surface.blit(self.from_surface, (-offset, 0))
            surface.blit(self.to_surface, (surface_width - offset, 0))
            
        elif self.transition_type == TransitionType.SLIDE_RIGHT:
            # Slide right transition
            offset = int(surface_width * self.transition_progress)
            surface.blit(self.from_surface, (offset, 0))
            surface.blit(self.to_surface, (-(surface_width - offset), 0))
            
        elif self.transition_type == TransitionType.SLIDE_UP:
            # Slide up transition
            offset = int(surface_height * self.transition_progress)
            surface.blit(self.from_surface, (0, -offset))
            surface.blit(self.to_surface, (0, surface_height - offset))
            
        elif self.transition_type == TransitionType.SLIDE_DOWN:
            # Slide down transition  
            offset = int(surface_height * self.transition_progress)
            surface.blit(self.from_surface, (0, offset))
            surface.blit(self.to_surface, (0, -(surface_height - offset)))
            
        elif self.transition_type == TransitionType.FADE_IN:
            # Fade in transition
            alpha = int(255 * self.transition_progress)
            temp_surface = self.to_surface.copy()
            temp_surface.set_alpha(alpha)
            surface.blit(self.from_surface, (0, 0))
            surface.blit(temp_surface, (0, 0))
            
        elif self.transition_type == TransitionType.FADE_OUT:
            # Fade out transition
            alpha = int(255 * (1.0 - self.transition_progress))
            temp_surface = self.from_surface.copy()
            temp_surface.set_alpha(alpha)
            surface.blit(self.to_surface, (0, 0))
            surface.blit(temp_surface, (0, 0))
            
        elif self.transition_type == TransitionType.SCALE_IN:
            # Scale in transition
            scale = self.transition_progress
            scaled_width = int(surface_width * scale)
            scaled_height = int(surface_height * scale)
            
            if scaled_width > 0 and scaled_height > 0:
                scaled_surface = pygame.transform.scale(self.to_surface, (scaled_width, scaled_height))
                x = (surface_width - scaled_width) // 2
                y = (surface_height - scaled_height) // 2
                
                surface.blit(self.from_surface, (0, 0))
                surface.blit(scaled_surface, (x, y))
    
    def _ease_out_quad(self, t: float) -> float:
        """Easing function for smoother transitions."""
        return 1 - (1 - t) * (1 - t)


class MenuEffectManager:
    """Manages visual effects for menu interactions."""
    
    def __init__(self):
        self.active_effects = []
    
    def add_selection_sparkle(self, position: Tuple[int, int]):
        """Add sparkle effect when selecting menu items."""
        effect = {
            'type': 'sparkle',
            'position': position,
            'timer': 0.0,
            'duration': 0.5,
            'particles': self._create_sparkle_particles(position)
        }
        self.active_effects.append(effect)
    
    def add_confirmation_flash(self, rect: pygame.Rect):
        """Add flash effect when confirming selection."""
        effect = {
            'type': 'flash',
            'rect': rect,
            'timer': 0.0,
            'duration': 0.3,
            'intensity': 255
        }
        self.active_effects.append(effect)
    
    def update(self, dt: float):
        """Update all active effects."""
        for effect in self.active_effects[:]:  # Copy list to allow removal
            effect['timer'] += dt
            
            if effect['timer'] >= effect['duration']:
                self.active_effects.remove(effect)
            else:
                # Update effect-specific properties
                if effect['type'] == 'sparkle':
                    self._update_sparkle_particles(effect, dt)
                elif effect['type'] == 'flash':
                    # Fade out the flash
                    progress = effect['timer'] / effect['duration']
                    effect['intensity'] = int(255 * (1.0 - progress))
    
    def draw(self, surface: pygame.Surface):
        """Draw all active effects."""
        for effect in self.active_effects:
            if effect['type'] == 'sparkle':
                self._draw_sparkle_effect(surface, effect)
            elif effect['type'] == 'flash':
                self._draw_flash_effect(surface, effect)
    
    def _create_sparkle_particles(self, center_pos: Tuple[int, int]):
        """Create sparkle particles around a position."""
        import random
        particles = []
        
        for _ in range(8):  # 8 sparkle particles
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(20, 40)
            lifetime = random.uniform(0.3, 0.7)
            
            particle = {
                'x': center_pos[0],
                'y': center_pos[1],
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'life': lifetime,
                'max_life': lifetime,
                'size': random.randint(2, 4)
            }
            particles.append(particle)
        
        return particles
    
    def _update_sparkle_particles(self, effect, dt):
        """Update sparkle particle positions."""
        for particle in effect['particles']:
            particle['x'] += particle['vx'] * dt
            particle['y'] += particle['vy'] * dt
            particle['life'] -= dt
            
            # Gravity effect
            particle['vy'] += 50 * dt
    
    def _draw_sparkle_effect(self, surface, effect):
        """Draw sparkle particles."""
        for particle in effect['particles']:
            if particle['life'] > 0:
                # Calculate alpha based on remaining life
                alpha = int(255 * (particle['life'] / particle['max_life']))
                color = (255, 255, 100, alpha)
                
                # Create small surface for the particle
                particle_surf = pygame.Surface((particle['size'] * 2, particle['size'] * 2), pygame.SRCALPHA)
                pygame.draw.circle(particle_surf, color, (particle['size'], particle['size']), particle['size'])
                
                surface.blit(particle_surf, (int(particle['x']) - particle['size'], int(particle['y']) - particle['size']))
    
    def _draw_flash_effect(self, surface, effect):
        """Draw flash effect."""
        if effect['intensity'] > 0:
            flash_color = (255, 255, 255, effect['intensity'])
            flash_surf = pygame.Surface(effect['rect'].size, pygame.SRCALPHA)
            flash_surf.fill(flash_color)
            surface.blit(flash_surf, effect['rect'])


def create_menu_transition_system():
    """Create and return a complete menu transition system."""
    return {
        'transition_manager': MenuTransitionManager(),
        'effect_manager': MenuEffectManager()
    }
