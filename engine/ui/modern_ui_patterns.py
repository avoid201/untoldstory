"""
Moderne UI-Patterns für Untold Story
Implementiert Animationen, Hover-Effekte und visuelle Feedback-Mechanismen
"""

import pygame
import math
from typing import Dict, Tuple, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum, auto
from dataclasses import dataclass
from engine.core.config import Colors


class AnimationType(Enum):
    """Arten von UI-Animationen."""
    FADE_IN = auto()
    FADE_OUT = auto()
    SLIDE_IN = auto()
    SLIDE_OUT = auto()
    SCALE_IN = auto()
    SCALE_OUT = auto()
    BOUNCE = auto()
    SHAKE = auto()
    GLOW = auto()


class HoverState(Enum):
    """Hover-Zustände für UI-Elemente."""
    NORMAL = auto()
    HOVER = auto()
    ACTIVE = auto()
    DISABLED = auto()


@dataclass
class Animation:
    """Animation-Konfiguration."""
    animation_type: AnimationType
    duration: float
    start_value: float
    end_value: float
    current_time: float = 0.0
    easing: str = "linear"  # linear, ease_in, ease_out, ease_in_out
    
    def update(self, dt: float) -> float:
        """Aktualisiert die Animation und gibt den aktuellen Wert zurück."""
        self.current_time += dt
        progress = min(self.current_time / self.duration, 1.0)
        
        # Easing-Funktionen
        if self.easing == "ease_in":
            progress = progress * progress
        elif self.easing == "ease_out":
            progress = 1 - (1 - progress) * (1 - progress)
        elif self.easing == "ease_in_out":
            if progress < 0.5:
                progress = 2 * progress * progress
            else:
                progress = 1 - 2 * (1 - progress) * (1 - progress)
        
        return self.start_value + (self.end_value - self.start_value) * progress
    
    def is_finished(self) -> bool:
        """Prüft ob die Animation abgeschlossen ist."""
        return self.current_time >= self.duration


@dataclass
class HoverEffect:
    """Hover-Effekt-Konfiguration."""
    scale_factor: float = 1.05
    glow_intensity: int = 20
    color_shift: Tuple[int, int, int] = (20, 20, 20)
    animation_duration: float = 0.2


class ModernUIElement:
    """Basis-Klasse für moderne UI-Elemente mit Animationen und Hover-Effekten."""
    
    def __init__(self, x: int, y: int, width: int, height: int):
        self.rect = pygame.Rect(x, y, width, height)
        self.hover_state = HoverState.NORMAL
        self.animations: Dict[str, Animation] = {}
        self.hover_effect = HoverEffect()
        self.is_visible = True
        self.alpha = 255
        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0
        
        # Hover-Timer für verzögerte Hover-Effekte
        self.hover_timer = 0.0
        self.hover_delay = 0.1
        
    def add_animation(self, name: str, animation: Animation) -> None:
        """Fügt eine Animation hinzu."""
        self.animations[name] = animation
    
    def update(self, dt: float) -> None:
        """Aktualisiert alle Animationen."""
        for animation in list(self.animations.values()):
            animation.update(dt)
            
            # Animation abgeschlossen
            if animation.is_finished():
                if animation.animation_type == AnimationType.FADE_OUT:
                    self.is_visible = False
                del self.animations[animation.name]
    
    def handle_hover(self, mouse_pos: Tuple[int, int]) -> bool:
        """Behandelt Hover-Events und gibt True zurück wenn sich der Zustand geändert hat."""
        was_hovering = self.hover_state == HoverState.HOVER
        is_hovering = self.rect.collidepoint(mouse_pos)
        
        if is_hovering and not was_hovering:
            self.hover_state = HoverState.HOVER
            self.hover_timer = 0.0
            return True
        elif not is_hovering and was_hovering:
            self.hover_state = HoverState.NORMAL
            return True
        
        return False
    
    def get_hover_scale(self) -> float:
        """Gibt den aktuellen Hover-Skalierungsfaktor zurück."""
        if self.hover_state == HoverState.HOVER:
            return self.hover_effect.scale_factor
        return 1.0
    
    def get_hover_glow(self) -> int:
        """Gibt die aktuelle Hover-Glow-Intensität zurück."""
        if self.hover_state == HoverState.HOVER:
            return self.hover_effect.glow_intensity
        return 0


class AnimatedButton(ModernUIElement):
    """Animierter Button mit Hover-Effekten."""
    
    def __init__(self, x: int, y: int, width: int, height: int, text: str, 
                 callback: Optional[Callable] = None):
        super().__init__(x, y, width, height)
        self.text = text
        self.callback = callback
        self.font = pygame.font.Font(None, 16)
        self.is_pressed = False
        
        # Button-spezifische Farben
        self.colors = {
            HoverState.NORMAL: Colors.UI_BG,
            HoverState.HOVER: (40, 40, 50),
            HoverState.ACTIVE: (60, 60, 70),
            HoverState.DISABLED: (30, 30, 40)
        }
        
        # Hover-Effekt verstärken
        self.hover_effect.scale_factor = 1.08
        self.hover_effect.glow_intensity = 30
    
    def handle_click(self, mouse_pos: Tuple[int, int]) -> bool:
        """Behandelt Klick-Events."""
        if self.rect.collidepoint(mouse_pos) and self.callback:
            self.is_pressed = True
            # Klick-Animation starten
            self.add_animation("click", Animation(
                AnimationType.SCALE_OUT, 0.1, 1.0, 0.95
            ))
            return True
        return False
    
    def draw(self, surface: pygame.Surface) -> None:
        """Zeichnet den Button mit allen Effekten."""
        if not self.is_visible:
            return
        
        # Aktuelle Position und Skalierung berechnen
        current_scale = self.get_hover_scale()
        glow_intensity = self.get_hover_glow()
        
        # Button-Hintergrund mit Glow-Effekt
        if glow_intensity > 0:
            glow_rect = self.rect.inflate(glow_intensity * 2, glow_intensity * 2)
            glow_color = (*Colors.UI_SELECTED[:3], glow_intensity)
            pygame.draw.rect(surface, glow_color, glow_rect, border_radius=8)
        
        # Haupt-Button zeichnen
        button_rect = self.rect.copy()
        button_rect.center = (
            self.rect.centerx + int(self.offset_x),
            self.rect.centery + int(self.offset_y)
        )
        
        # Skalierung anwenden
        if current_scale != 1.0:
            scaled_width = int(self.rect.width * current_scale)
            scaled_height = int(self.rect.height * current_scale)
            button_rect = button_rect.inflate(
                scaled_width - self.rect.width,
                scaled_height - self.rect.height
            )
        
        # Hintergrund
        pygame.draw.rect(surface, self.colors[self.hover_state], button_rect, border_radius=6)
        pygame.draw.rect(surface, Colors.UI_BORDER, button_rect, 2, border_radius=6)
        
        # Text
        text_surface = self.font.render(self.text, True, Colors.WHITE)
        text_rect = text_surface.get_rect(center=button_rect.center)
        surface.blit(text_surface, text_rect)


class TooltipManager:
    """Verwaltet Tooltips für UI-Elemente."""
    
    def __init__(self):
        self.tooltips: Dict[ModernUIElement, str] = {}
        self.current_tooltip: Optional[str] = None
        self.tooltip_timer = 0.0
        self.tooltip_delay = 0.5
        self.font = pygame.font.Font(None, 12)
        
    def add_tooltip(self, element: ModernUIElement, text: str) -> None:
        """Fügt einen Tooltip zu einem UI-Element hinzu."""
        self.tooltips[element] = text
    
    def update(self, dt: float, mouse_pos: Tuple[int, int]) -> None:
        """Aktualisiert den Tooltip-Status."""
        self.current_tooltip = None
        
        for element, tooltip_text in self.tooltips.items():
            if element.rect.collidepoint(mouse_pos):
                if element.hover_state == HoverState.HOVER:
                    self.tooltip_timer += dt
                    if self.tooltip_timer >= self.tooltip_delay:
                        self.current_tooltip = tooltip_text
                else:
                    self.tooltip_timer = 0.0
                break
        else:
            self.tooltip_timer = 0.0
    
    def draw(self, surface: pygame.Surface, mouse_pos: Tuple[int, int]) -> None:
        """Zeichnet den aktuellen Tooltip."""
        if not self.current_tooltip:
            return
        
        # Tooltip-Position (über dem Mauszeiger)
        tooltip_x = mouse_pos[0] + 15
        tooltip_y = mouse_pos[1] - 30
        
        # Tooltip-Text rendern
        text_surface = self.font.render(self.current_tooltip, True, Colors.WHITE)
        text_rect = text_surface.get_rect(x=tooltip_x, y=tooltip_y)
        
        # Hintergrund mit Padding
        padding = 8
        bg_rect = text_rect.inflate(padding * 2, padding * 2)
        
        # Tooltip-Hintergrund
        pygame.draw.rect(surface, (0, 0, 0, 200), bg_rect, border_radius=4)
        pygame.draw.rect(surface, Colors.UI_BORDER, bg_rect, 1, border_radius=4)
        
        # Text
        surface.blit(text_surface, text_rect)


class TransitionManager:
    """Verwaltet Übergänge zwischen UI-Zuständen."""
    
    def __init__(self):
        self.transitions: Dict[str, Animation] = {}
        self.fade_surface = None
        
    def start_fade(self, name: str, fade_in: bool = True, duration: float = 0.5) -> None:
        """Startet einen Fade-Übergang."""
        self.transitions[name] = Animation(
            AnimationType.FADE_IN if fade_in else AnimationType.FADE_OUT,
            duration,
            0 if fade_in else 255,
            255 if fade_in else 0
        )
    
    def update(self, dt: float) -> None:
        """Aktualisiert alle Übergänge."""
        for transition in list(self.transitions.values()):
            transition.update(dt)
            if transition.is_finished():
                del self.transitions[transition.name]
    
    def draw(self, surface: pygame.Surface) -> None:
        """Zeichnet aktive Übergänge."""
        for transition in self.transitions.values():
            if transition.animation_type in [AnimationType.FADE_IN, AnimationType.FADE_OUT]:
                alpha = int(transition.current_time / transition.duration * 255)
                if transition.animation_type == AnimationType.FADE_OUT:
                    alpha = 255 - alpha
                
                fade_surface = pygame.Surface(surface.get_size())
                fade_surface.set_alpha(alpha)
                fade_surface.fill((0, 0, 0))
                surface.blit(fade_surface, (0, 0))
