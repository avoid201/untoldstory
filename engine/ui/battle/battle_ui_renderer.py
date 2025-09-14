"""
Battle UI Renderer - Alle Zeichen-Operationen
Verantwortlich für alle visuellen Darstellungen der Battle UI

ENHANCED: HP-Bar Animation & Visual Effects System
- Smooth HP-Bar-Animationen mit Interpolation
- Damage-Numbers mit float-up Animationen
- Visual-Effects-Integration
- 60 FPS Performance-optimiert
"""

import pygame
import random
import math
import logging
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass

from engine.core.config import LOGICAL_WIDTH, LOGICAL_HEIGHT, Colors
from engine.ui.battle_ui_utils import fonts, sprites
from .battle_ui_state import BattleMenuState

# Setup logger
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


@dataclass
class DamageNumberAnimation:
    """Damage-Number mit float-up Animation."""
    value: int
    position: Tuple[float, float]
    velocity: Tuple[float, float]
    color: Tuple[int, int, int]
    timer: float
    duration: float = 1.5
    scale: float = 1.0
    is_critical: bool = False
    is_super_effective: bool = False
    alpha: int = 255
    active: bool = True


@dataclass
class VisualEffect:
    """Visual Effect für Battle-Animationen."""
    effect_type: str
    position: Tuple[float, float]
    timer: float
    duration: float
    intensity: float = 1.0
    color: Tuple[int, int, int] = (255, 255, 255)
    active: bool = True


class HPBarAnimator:
    """HP-Bar Animation System mit smooth interpolation."""
    
    def __init__(self):
        self.animations: Dict[Any, HPBarAnimation] = {}
        self.animation_speed = 2.0  # HP per frame (konfigurierbar)
        self.max_animations = 10  # Performance-Limit
    
    def add_animation(self, monster_id: Any, old_hp: int, new_hp: int, 
                     max_hp: int, duration: float = 0.5) -> None:
        """Füge HP-Bar-Animation hinzu."""
        if len(self.animations) >= self.max_animations:
            # Remove oldest animation
            oldest_id = min(self.animations.keys(), 
                          key=lambda k: self.animations[k].timer)
            del self.animations[oldest_id]
        
        self.animations[monster_id] = HPBarAnimation(
            monster_id=monster_id,
            old_hp=old_hp,
            new_hp=new_hp,
            max_hp=max_hp,
            current_hp=old_hp,
            timer=duration,
            duration=duration,
            speed=self.animation_speed
        )
        
        logger.debug(f"HP animation added: {monster_id} {old_hp}→{new_hp}")
    
    def update_animations(self, dt: float) -> None:
        """Update alle HP-Bar-Animationen."""
        for monster_id, anim in list(self.animations.items()):
            if not anim.active:
                continue
                
            anim.timer -= dt
            
            if anim.timer <= 0:
                # Animation beendet
                anim.current_hp = anim.new_hp
                anim.active = False
                del self.animations[monster_id]
            else:
                # Smooth interpolation mit easing
                progress = 1.0 - (anim.timer / anim.duration)
                eased_progress = self._apply_easing(progress, anim.easing)
                
                anim.current_hp = int(anim.old_hp + 
                                    (anim.new_hp - anim.old_hp) * eased_progress)
    
    def get_animated_hp(self, monster_id: Any, current_hp: int, max_hp: int) -> int:
        """Hole animierten HP-Wert für Monster."""
        if monster_id in self.animations:
            anim = self.animations[monster_id]
            if anim.active:
                return anim.current_hp
        return current_hp
    
    def is_animating(self, monster_id: Any) -> bool:
        """Prüfe ob Monster HP-Animation hat."""
        return monster_id in self.animations and self.animations[monster_id].active
    
    def _apply_easing(self, progress: float, easing_type: str) -> float:
        """Wende Easing-Funktion an."""
        if easing_type == "ease_out_cubic":
            return 1.0 - math.pow(1.0 - progress, 3)
        elif easing_type == "ease_in_out_cubic":
            if progress < 0.5:
                return 4 * progress * progress * progress
            else:
                return 1 - math.pow(-2 * progress + 2, 3) / 2
        elif easing_type == "ease_out_quad":
            return 1 - (1 - progress) * (1 - progress)
        else:
            return progress  # Linear fallback


class DamageNumberRenderer:
    """Damage-Number Rendering System mit float-up Animationen."""
    
    def __init__(self):
        self.animations: List[DamageNumberAnimation] = []
        self.max_animations = 20  # Performance-Limit
        self.gravity = -50  # Upward force
        self.fade_speed = 1.0  # Alpha fade speed
    
    def add_damage_number(self, value: int, position: Tuple[int, int], 
                         color: Tuple[int, int, int] = (255, 255, 255),
                         is_critical: bool = False, 
                         is_super_effective: bool = False) -> None:
        """Füge Damage-Number hinzu."""
        if len(self.animations) >= self.max_animations:
            # Remove oldest animation
            self.animations.pop(0)
        
        # Random offset für natürlichen Look
        offset_x = random.randint(-15, 15)
        offset_y = random.randint(-10, 10)
        
        # Velocity basierend auf Typ
        if is_critical:
            velocity = (random.uniform(-20, 20), random.uniform(-80, -60))
            scale = 1.5
            duration = 2.0
        elif is_super_effective:
            velocity = (random.uniform(-15, 15), random.uniform(-70, -50))
            scale = 1.2
            duration = 1.8
        else:
            velocity = (random.uniform(-10, 10), random.uniform(-60, -40))
            scale = 1.0
            duration = 1.5
        
        self.animations.append(DamageNumberAnimation(
            value=value,
            position=(position[0] + offset_x, position[1] + offset_y),
            velocity=velocity,
            color=color,
            timer=duration,
            duration=duration,
            scale=scale,
            is_critical=is_critical,
            is_super_effective=is_super_effective
        ))
        
        logger.debug(f"Damage number added: {value} at {position} (critical: {is_critical})")
    
    def update_animations(self, dt: float) -> None:
        """Update alle Damage-Number-Animationen."""
        for anim in self.animations[:]:
            if not anim.active:
                self.animations.remove(anim)
                continue
                
            # Update position
            anim.position = (
                anim.position[0] + anim.velocity[0] * dt,
                anim.position[1] + anim.velocity[1] * dt
            )
            
            # Apply gravity
            anim.velocity = (
                anim.velocity[0] * 0.98,  # Air resistance
                anim.velocity[1] + self.gravity * dt
            )
            
            # Update timer and alpha
            anim.timer -= dt
            progress = 1.0 - (anim.timer / anim.duration)
            anim.alpha = int(255 * (1.0 - progress))
            
            if anim.timer <= 0 or anim.alpha <= 0:
                anim.active = False
                self.animations.remove(anim)
    
    def get_active_animations(self) -> List[DamageNumberAnimation]:
        """Hole alle aktiven Animationen."""
        return [anim for anim in self.animations if anim.active]


class VisualEffectsManager:
    """Visual Effects Manager für Battle-Animationen."""
    
    def __init__(self):
        self.effects: List[VisualEffect] = []
        self.max_effects = 50  # Performance-Limit
        self.effect_types = {
            "sparkle": {"duration": 1.0, "color": (255, 255, 0)},
            "explosion": {"duration": 0.8, "color": (255, 100, 0)},
            "heal": {"duration": 1.2, "color": (0, 255, 0)},
            "poison": {"duration": 1.5, "color": (128, 0, 128)},
            "burn": {"duration": 1.0, "color": (255, 100, 0)},
            "freeze": {"duration": 1.3, "color": (0, 255, 255)},
            "paralysis": {"duration": 1.0, "color": (255, 255, 0)},
            "sleep": {"duration": 1.5, "color": (0, 0, 255)},
            "confusion": {"duration": 1.2, "color": (255, 0, 255)}
        }
    
    def add_effect(self, effect_type: str, position: Tuple[int, int], 
                   intensity: float = 1.0, custom_color: Optional[Tuple[int, int, int]] = None) -> None:
        """Füge Visual Effect hinzu."""
        if len(self.effects) >= self.max_effects:
            # Remove oldest effect
            self.effects.pop(0)
        
        effect_data = self.effect_types.get(effect_type, 
                                          {"duration": 1.0, "color": (255, 255, 255)})
        
        color = custom_color if custom_color else effect_data["color"]
        
        self.effects.append(VisualEffect(
            effect_type=effect_type,
            position=position,
            timer=effect_data["duration"],
            duration=effect_data["duration"],
            intensity=intensity,
            color=color
        ))
        
        logger.debug(f"Visual effect added: {effect_type} at {position}")
    
    def update_effects(self, dt: float) -> None:
        """Update alle Visual Effects."""
        for effect in self.effects[:]:
            effect.timer -= dt
            
            if effect.timer <= 0:
                effect.active = False
                self.effects.remove(effect)
    
    def get_active_effects(self) -> List[VisualEffect]:
        """Hole alle aktiven Effects."""
        return [effect for effect in self.effects if effect.active]


class BattleUIRenderer:
    """
    Renderer für alle Battle UI Komponenten.
    
    Verantwortlichkeiten:
    - Alle draw_* Methoden
    - Visual Effects
    - Animationen
    - Sprite Rendering
    """
    
    def __init__(self, battle_ui):
        """Initialisiere Renderer mit Enhanced Animation Systems."""
        self.battle_ui = battle_ui
        self.state = battle_ui.state
        
        # Rendering Constants - optimized for 320x180 resolution
        self.TILE_SIZE = 16
        self.UI_SCALE = 1
        self.FONT_SIZE = 8
        
        # Colors
        self.BG_COLOR = Colors.BLACK
        self.UI_COLOR = Colors.WHITE
        self.HP_COLOR = Colors.GREEN
        self.MP_COLOR = Colors.BLUE
        
        # Positions - optimized for 320x180
        self.PLAYER_POS = (60, 100)
        self.ENEMY_POS = (220, 60)
        self.MENU_POS = (10, 120)  # Moved up to fit better
        self.STATUS_PANEL_SIZE = (100, 32)  # Smaller panels
        self.MENU_SIZE = (300, 56)  # Optimized menu size
        
        # ENHANCED: Animation Systems
        self.hp_animator = HPBarAnimator()
        self.damage_renderer = DamageNumberRenderer()
        self.visual_effects = VisualEffectsManager()
        
        # Performance tracking
        self.frame_count = 0
        self.target_fps = 60
        self.animation_queue_limit = 100
        
        # Performance optimization
        self.performance_mode = "normal"  # normal, high_performance, low_power
        self.frame_skip_threshold = 0.016  # 60 FPS = 16.67ms per frame
        self.last_frame_time = 0.0
        self.frame_times = []
        self.max_frame_times = 60  # Keep last 60 frame times
        
        # Animation culling
        self.cull_off_screen_animations = True
        self.screen_bounds = pygame.Rect(0, 0, LOGICAL_WIDTH, LOGICAL_HEIGHT)
        
        logger.info("🎨 Enhanced Battle UI Renderer initialized with Animation Systems & Performance Optimization")
    
    def draw(self, surface: pygame.Surface) -> None:
        """Haupt-Zeichen-Methode mit Enhanced Animation Systems."""
        # Check for Victory/Defeat screens
        if self.state.show_victory_screen:
            self.render_victory_screen(surface)
            return
        elif self.state.show_defeat_screen:
            self.render_defeat_screen(surface)
            return
        
        # Create temporary surface for drawing
        temp_surface = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT))
        
        # Draw all components to temp surface
        self.draw_background(temp_surface)
        self.draw_battlefield(temp_surface)
        self.draw_monsters(temp_surface)
        self.draw_status_panels(temp_surface)
        self.draw_menus(temp_surface)
        
        # ENHANCED: Draw new animation systems
        self.draw_visual_effects(temp_surface)
        
        # Apply screen shake if active
        final_surface = self.apply_screen_shake(temp_surface)
        
        # Blit final surface to main surface
        surface.blit(final_surface, (0, 0))
        
        # Draw screen effects on top (flash, etc.)
        self.draw_screen_effects(surface)
        
        # Update frame counter for performance tracking
        self.frame_count += 1
    
    def draw_background(self, surface: pygame.Surface) -> None:
        """Zeichne Battle-Hintergrund."""
        surface.fill(self.BG_COLOR)
        
        # Draw battle arena background
        arena_rect = pygame.Rect(20, 20, 280, 140)
        pygame.draw.rect(surface, (20, 20, 20), arena_rect)
        pygame.draw.rect(surface, (60, 60, 60), arena_rect, 2)
    
    def draw_battlefield(self, surface: pygame.Surface) -> None:
        """Zeichne Battle-Feld."""
        # Draw arena elements
        self._draw_arena_elements(surface)
    
    def draw_monsters(self, surface: pygame.Surface) -> None:
        """Zeichne Monster-Sprites."""
        # Get monsters from battle_ui state
        player_active = self.battle_ui.battle_state.player_active if self.battle_ui.battle_state else None
        enemy_active = self.battle_ui.battle_state.enemy_active if self.battle_ui.battle_state else None
        
        if player_active:
            self.draw_monster_sprite(surface, player_active, self.PLAYER_POS, True)
        
        if enemy_active:
            self.draw_monster_sprite(surface, enemy_active, self.ENEMY_POS, False)
    
    def draw_monster_sprite(self, surface: pygame.Surface, monster, pos: Tuple[int, int], is_player: bool) -> None:
        """Draw monster sprite with animations."""
        if not monster:
            return
        
        # Get monster sprite
        species_id = monster.species.id if hasattr(monster, 'species') and hasattr(monster.species, 'id') else str(id(monster))
        sprite = sprites.get_monster_sprite(species_id)
        if not sprite:
            sprite = self._create_fallback_sprite(species_id)
        
        # Copy sprite for modifications
        sprite_copy = sprite.copy()
        
        # Apply animations from BattleUIState
        final_pos = list(pos)
        monster_id = monster.id if hasattr(monster, 'id') else id(monster)
        
        # Faint animation
        if self.battle_ui.state and monster_id in self.battle_ui.state.animations["faint"]:
            timer = self.battle_ui.state.animations["faint"][monster_id]
            if timer > 0:
                # Fade out and fall down
                alpha = int(255 * timer)
                sprite_copy.set_alpha(alpha)
                final_pos[1] += int((1 - timer) * 20)  # Fall down
        
        # Appear animation
        elif self.battle_ui.state and monster_id in self.battle_ui.state.animations["appear"]:
            timer = self.battle_ui.state.animations["appear"][monster_id]
            if timer > 0:
                # Fade in and scale up
                progress = 1.0 - timer
                alpha = int(255 * progress)
                sprite_copy.set_alpha(alpha)
                
                # Scale effect
                if progress < 0.5:
                    scale = 0.5 + progress
                    size = sprite_copy.get_size()
                    sprite_copy = pygame.transform.scale(
                        sprite_copy,
                        (int(size[0] * scale), int(size[1] * scale))
                    )
                    # Center the scaled sprite
                    final_pos[0] += (size[0] - sprite_copy.get_width()) // 2
                    final_pos[1] += (size[1] - sprite_copy.get_height()) // 2
        
        # Draw sprite
        surface.blit(sprite_copy, final_pos)
        
        # Draw status effects
        self.draw_status_conditions(surface, monster, pos)
    
    def draw_hp_bars(self, surface: pygame.Surface) -> None:
        """Draw HP bars for all monsters."""
        if not self.battle_ui or not self.battle_ui.battle_state:
            return
        
        # Draw HP bars for player and enemy
        player_active = self.battle_ui.battle_state.player_active
        enemy_active = self.battle_ui.battle_state.enemy_active
        
        if player_active:
            self.draw_single_hp_bar(surface, player_active, (20, 180), True)
        
        if enemy_active:
            self.draw_single_hp_bar(surface, enemy_active, (180, 40), False)
    
    def draw_single_hp_bar(self, surface: pygame.Surface, monster, pos: Tuple[int, int], is_player: bool) -> None:
        """Draw single HP bar with animation."""
        if not monster:
            return
        
        # HP bar dimensions
        bar_width = 100
        bar_height = 8
        
        # Calculate HP ratio
        hp_ratio = monster.current_hp / monster.max_hp if monster.max_hp > 0 else 0
        
        # HP bar background
        bg_rect = pygame.Rect(pos[0], pos[1], bar_width, bar_height)
        pygame.draw.rect(surface, (60, 60, 60), bg_rect)
        
        # HP bar fill
        fill_width = int(bar_width * hp_ratio)
        if fill_width > 0:
            fill_rect = pygame.Rect(pos[0], pos[1], fill_width, bar_height)
            # Color based on HP percentage
            if hp_ratio > 0.5:
                color = (0, 255, 0)  # Green
            elif hp_ratio > 0.25:
                color = (255, 255, 0)  # Yellow
            else:
                color = (255, 0, 0)  # Red
            pygame.draw.rect(surface, color, fill_rect)
        
        # HP bar border
        pygame.draw.rect(surface, (200, 200, 200), bg_rect, 1)
    
    def _get_hp_color(self, ratio: float) -> Tuple[int, int, int]:
        """Get HP bar color based on HP ratio."""
        if ratio > 0.6:
            return (0, 255, 0)  # Green
        elif ratio > 0.3:
            return (255, 255, 0)  # Yellow
        else:
            return (255, 0, 0)  # Red
    
    def _create_fallback_sprite(self, species_id: str) -> pygame.Surface:
        """Create fallback sprite for missing monster sprites."""
        sprite = pygame.Surface((32, 32))
        sprite.fill((100, 100, 100))
        pygame.draw.rect(sprite, (150, 150, 150), (8, 8, 16, 16))
        return sprite
    
    def draw_status_panels(self, surface: pygame.Surface) -> None:
        """Zeichne Status-Panels."""
        # Get monsters from battle_ui state
        player_active = self.battle_ui.battle_state.player_active if self.battle_ui.battle_state else None
        enemy_active = self.battle_ui.battle_state.enemy_active if self.battle_ui.battle_state else None
        
        if player_active:
            self.draw_single_status_panel(surface, player_active, (20, 160), True)
        
        if enemy_active:
            self.draw_single_status_panel(surface, enemy_active, (180, 20), False)
    
    def draw_single_status_panel(self, surface: pygame.Surface, monster, pos: Tuple[int, int], is_player: bool) -> None:
        """Draw status panel with animated HP bar."""
        if not monster:
            return
        
        # Get monster ID
        monster_id = monster.id if hasattr(monster, 'id') else id(monster)
        
        # Panel background
        panel_rect = pygame.Rect(pos[0], pos[1], self.STATUS_PANEL_SIZE[0], self.STATUS_PANEL_SIZE[1])
        pygame.draw.rect(surface, (40, 40, 40), panel_rect)
        pygame.draw.rect(surface, (100, 100, 100), panel_rect, 1)
        
        # Monster name - use larger, bold font
        name_font = fonts.monster_name
        name_text = name_font.render(monster.name, True, self.UI_COLOR)
        surface.blit(name_text, (pos[0] + 4, pos[1] + 2))
        
        # Level - use normal font
        level_font = fonts.normal
        level_text = level_font.render(f"Lv.{monster.level}", True, self.UI_COLOR)
        surface.blit(level_text, (pos[0] + 100, pos[1] + 2))
        
        # ENHANCED: Calculate HP ratio with new animation system
        hp_ratio = monster.current_hp / monster.max_hp if monster.max_hp > 0 else 0
        
        # Check for animated HP update in new HP animator
        if self.hp_animator.is_animating(monster_id):
            animated_hp = self.hp_animator.get_animated_hp(monster_id, monster.current_hp, monster.max_hp)
            hp_ratio = animated_hp / monster.max_hp if monster.max_hp > 0 else 0
        
        # Fallback: Check for animated HP update in BattleUIState (legacy support)
        elif self.battle_ui.state and monster_id in self.battle_ui.state.animations["hp_bars"]:
            anim = self.battle_ui.state.animations["hp_bars"][monster_id]
            if anim["active"]:
                # Use animated HP value
                hp_ratio = anim["current"] / anim["max_hp"] if anim["max_hp"] > 0 else 0
        
        # HP Bar
        hp_color = self._get_hp_color(hp_ratio)
        hp_bar_rect = pygame.Rect(pos[0] + 4, pos[1] + 12, 112, 8)
        pygame.draw.rect(surface, (20, 20, 20), hp_bar_rect)
        pygame.draw.rect(surface, hp_color, (pos[0] + 4, pos[1] + 12, int(112 * hp_ratio), 8))
        
        # ENHANCED: HP Text - show animated value from new system
        display_hp = monster.current_hp
        if self.hp_animator.is_animating(monster_id):
            display_hp = int(self.hp_animator.get_animated_hp(monster_id, monster.current_hp, monster.max_hp))
        # Fallback: Check for animated HP update in BattleUIState (legacy support)
        elif self.battle_ui.state and monster_id in self.battle_ui.state.animations["hp_bars"]:
            anim = self.battle_ui.state.animations["hp_bars"][monster_id]
            if anim["active"]:
                display_hp = int(anim["current"])
        
        # HP text - use small font for better readability
        hp_font = fonts.small
        hp_text = hp_font.render(f"{display_hp}/{monster.max_hp}", True, self.UI_COLOR)
        surface.blit(hp_text, (pos[0] + 4, pos[1] + 22))
        
        # MP Bar (if applicable)
        if hasattr(monster, 'current_mp') and hasattr(monster, 'max_mp'):
            mp_ratio = monster.current_mp / monster.max_mp if monster.max_mp > 0 else 0
            mp_bar_rect = pygame.Rect(pos[0] + 4, pos[1] + 30, 112, 6)
            pygame.draw.rect(surface, (20, 20, 20), mp_bar_rect)
            pygame.draw.rect(surface, self.MP_COLOR, (pos[0] + 4, pos[1] + 30, int(112 * mp_ratio), 6))
    
    def draw_status_conditions(self, surface: pygame.Surface, monster, pos: Tuple[int, int]) -> None:
        """Zeichne Status-Bedingungen mit Enhanced Animationen."""
        if not monster:
            return
        
        # Get monster ID
        monster_id = monster.id if hasattr(monster, 'id') else id(monster)
        
        # Check for animated status effects
        if monster_id in self.state.animations["status_effects"]:
            effect = self.state.animations["status_effects"][monster_id]
            status = effect["status"]
            flash = effect["flash"]
            
            # Enhanced status icon with animation
            status_icon = self._get_enhanced_status_icon(status, flash)
            if status_icon:
                icon_pos = (pos[0] - 20, pos[1] + 10)
                surface.blit(status_icon, icon_pos)
                
                # Add pulsing effect for active status
                if flash:
                    self._draw_status_pulse_effect(surface, icon_pos, status)
        
        # Legacy support for monster.status
        elif hasattr(monster, 'status') and monster.status:
            status_icon = self._get_enhanced_status_icon(monster.status, False)
            if status_icon:
                icon_pos = (pos[0] - 20, pos[1] + 10)
                surface.blit(status_icon, icon_pos)
    
    def _get_enhanced_status_icon(self, status: str, is_flashing: bool = False) -> Optional[pygame.Surface]:
        """Hole Enhanced Status-Icon mit Animationen."""
        # Status icon mapping with enhanced visuals
        status_icons = {
            "BURN": self._create_enhanced_status_icon((255, 100, 0), "BR", is_flashing),      # Orange - Brennen
            "POISON": self._create_enhanced_status_icon((128, 0, 128), "PS", is_flashing),    # Purple - Gift
            "PARALYSIS": self._create_enhanced_status_icon((255, 255, 0), "PR", is_flashing), # Yellow - Paralyse
            "SLEEP": self._create_enhanced_status_icon((0, 0, 255), "SL", is_flashing),       # Blue - Schlaf
            "FREEZE": self._create_enhanced_status_icon((0, 255, 255), "FR", is_flashing),    # Cyan - Einfrieren
            "CONFUSION": self._create_enhanced_status_icon((255, 0, 255), "CF", is_flashing), # Magenta - Verwirrung
            "FLINCH": self._create_enhanced_status_icon((255, 128, 128), "FL", is_flashing)   # Light Red - Zurückschrecken
        }
        
        return status_icons.get(status.upper())
    
    def _create_enhanced_status_icon(self, color: Tuple[int, int, int], text: str, is_flashing: bool = False) -> pygame.Surface:
        """Erstelle Enhanced Status-Icon mit Animationen."""
        icon = pygame.Surface((20, 20), pygame.SRCALPHA)  # Larger icon
        
        # Create gradient background
        for i in range(20):
            alpha = int(255 * (1 - i / 20))
            gradient_color = (*color, alpha)
            pygame.draw.line(icon, gradient_color, (0, i), (19, i))
        
        # Add border
        pygame.draw.rect(icon, (255, 255, 255), (0, 0, 20, 20), 2)
        
        # Add text
        font = fonts.tiny
        text_surface = font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(10, 10))
        icon.blit(text_surface, text_rect)
        
        # Apply flash effect
        if is_flashing:
            flash_alpha = int(128 + 127 * (pygame.time.get_ticks() % 500) / 500)
            flash_surface = pygame.Surface((20, 20), pygame.SRCALPHA)
            flash_surface.fill((255, 255, 255, flash_alpha))
            icon.blit(flash_surface, (0, 0), special_flags=pygame.BLEND_ALPHA_SDL2)
        
        return icon
    
    def _draw_status_pulse_effect(self, surface: pygame.Surface, pos: Tuple[int, int], status: str) -> None:
        """Zeichne Status-Pulse-Effekt."""
        # Create pulsing circle around status icon
        pulse_radius = int(15 + 5 * (pygame.time.get_ticks() % 1000) / 1000)
        pulse_alpha = int(100 * (1 - (pygame.time.get_ticks() % 1000) / 1000))
        
        pulse_surface = pygame.Surface((pulse_radius * 2, pulse_radius * 2), pygame.SRCALPHA)
        pulse_color = self._get_status_color(status)
        pygame.draw.circle(pulse_surface, (*pulse_color, pulse_alpha), (pulse_radius, pulse_radius), pulse_radius, 2)
        
        # Center the pulse effect
        pulse_pos = (pos[0] + 10 - pulse_radius, pos[1] + 10 - pulse_radius)
        surface.blit(pulse_surface, pulse_pos)
    
    def _get_status_color(self, status: str) -> Tuple[int, int, int]:
        """Hole Status-Farbe."""
        status_colors = {
            'BURN': (255, 100, 0),
            'POISON': (128, 0, 128),
            'PARALYSIS': (255, 255, 0),
            'SLEEP': (0, 0, 255),
            'FREEZE': (0, 255, 255),
            'CONFUSION': (255, 0, 255),
            'FLINCH': (255, 128, 128)
        }
        return status_colors.get(status.upper(), (255, 255, 255))
    
    def draw_menus(self, surface: pygame.Surface) -> None:
        """Zeichne Menüs basierend auf aktuellem State."""
        # Get menu state from battle_ui
        menu_state = self.battle_ui.state.menu_state if self.battle_ui.state else BattleMenuState.MAIN
        
        if menu_state == BattleMenuState.MAIN:
            self.draw_main_menu(surface)
        elif menu_state == BattleMenuState.MOVE_SELECT:
            self.draw_move_menu(surface)
        elif menu_state == BattleMenuState.ITEM_SELECT:
            self.draw_item_menu(surface)
        elif menu_state == BattleMenuState.SWITCH_SELECT:
            self.draw_switch_menu(surface)
        elif menu_state == BattleMenuState.SCOUT:
            self.draw_scout_display(surface)
        elif menu_state == BattleMenuState.MESSAGE:
            self.draw_message_box(surface)
        
        # Always draw turn counter (except on scout display where it's integrated)
        if menu_state != BattleMenuState.SCOUT:
            self.render_turn_counter(surface)
    
    def draw_main_menu(self, surface: pygame.Surface) -> None:
        """Zeichne Hauptmenü."""
        menu_rect = pygame.Rect(self.MENU_POS[0], self.MENU_POS[1], 280, 40)
        pygame.draw.rect(surface, (30, 30, 30), menu_rect)
        pygame.draw.rect(surface, (80, 80, 80), menu_rect, 1)
        
        # Menu options
        options = ["ATTACKE", "ITEM", "WECHSEL", "ZÄHMEN", "SPÄHEN", "FLUCHT"]
        option_width = 280 // 3
        option_height = 40 // 2
        
        for i, option in enumerate(options):
            x = self.MENU_POS[0] + (i % 3) * option_width
            y = self.MENU_POS[1] + (i // 3) * option_height
            
            # Highlight selected option
            selected_option = self.battle_ui.state.selected_option if self.battle_ui.state else 0
            if i == selected_option:
                highlight_rect = pygame.Rect(x + 2, y + 2, option_width - 4, option_height - 4)
                pygame.draw.rect(surface, (60, 60, 60), highlight_rect)
            
            # Draw option text - use normal font for better readability
            option_font = fonts.normal
            text = option_font.render(option, True, self.UI_COLOR)
            text_rect = text.get_rect(center=(x + option_width // 2, y + option_height // 2))
            surface.blit(text, text_rect)
    
    def draw_move_menu(self, surface: pygame.Surface) -> None:
        """Zeichne Talent-basiertes Move-Menü - BEHOBEN für bessere Lesbarkeit."""
        menu_rect = pygame.Rect(self.MENU_POS[0], self.MENU_POS[1], self.MENU_SIZE[0], self.MENU_SIZE[1])
        pygame.draw.rect(surface, (30, 30, 30), menu_rect)
        pygame.draw.rect(surface, (80, 80, 80), menu_rect, 1)
        
        # Category tabs - optimized for smaller UI
        categories = ["PHYSISCH", "MAGISCH", "STATUS"]
        tab_width = self.MENU_SIZE[0] // 3
        
        for i, category in enumerate(categories):
            x = self.MENU_POS[0] + i * tab_width
            y = self.MENU_POS[1]
            
            # Highlight active category
            if i == self.state.current_move_category:
                tab_rect = pygame.Rect(x + 1, y + 1, tab_width - 2, 18)
                pygame.draw.rect(surface, (60, 60, 60), tab_rect)
            
            # Draw category text - use small font
            category_font = fonts.small
            text = category_font.render(category, True, self.UI_COLOR)
            text_rect = text.get_rect(center=(x + tab_width // 2, y + 9))
            surface.blit(text, text_rect)
        
        # Talent-based Move list - BEHOBEN für bessere Initialisierung
        player_active = self.state.player_active or (self.battle_ui.battle_state.player_active if self.battle_ui.battle_state else None)
        
        if player_active:
            try:
                # Hole Talent-Moves über Menu Manager
                talent_moves = self.battle_ui.menu_manager.get_talent_moves(player_active)
                talent_categories = self.battle_ui.menu_manager.get_talent_categories(talent_moves)
                
                # Filter nach aktueller Kategorie
                current_category = self.state.get_selected_move_category()
                moves = talent_categories.get(current_category, [])
                
                move_y = self.MENU_POS[1] + 20
                
                # BEHOBEN: Bessere Schriftgrößen und Positionierung
                for i, move_data in enumerate(moves[:4]):  # Show max 4 moves
                    if i == self.state.selected_move:
                        highlight_rect = pygame.Rect(self.MENU_POS[0] + 2, move_y + i * 14, self.MENU_SIZE[0] - 4, 12)
                        pygame.draw.rect(surface, (60, 60, 60), highlight_rect)
                    
                    # Move text mit Talent-Info - BEHOBEN: Kleinere Schrift
                    move = move_data['move']
                    talent_name = move_data['talent_name']
                    tier_stars = move_data['tier_stars']
                    
                    # BEHOBEN: Verwende normale Schrift statt move_name (18px) für bessere Lesbarkeit
                    talent_text = f"{talent_name} {tier_stars}"
                    talent_surface = fonts.normal.render(talent_text, True, (255, 255, 100))  # Gold für Talent
                    surface.blit(talent_surface, (self.MENU_POS[0] + 4, move_y + i * 14))
                    
                    # BEHOBEN: Move-Name und Power mit kleiner Schrift
                    power_text = f"Stärke: {move.power}" if hasattr(move, 'power') else ""
                    move_info = f"{move.name} - {power_text}"
                    move_surface = fonts.small.render(move_info, True, self.UI_COLOR)
                    surface.blit(move_surface, (self.MENU_POS[0] + 4, move_y + i * 14 + 10))
                    
            except Exception as e:
                # BEHOBEN: Fallback wenn Talent-Moves nicht geladen werden können
                logger.warning(f"Error loading talent moves: {e}")
                fallback_font = fonts.normal
                fallback_text = "Keine Moves verfügbar"
                fallback_surface = fallback_font.render(fallback_text, True, self.UI_COLOR)
                surface.blit(fallback_surface, (self.MENU_POS[0] + 4, self.MENU_POS[1] + 20))
        else:
            # BEHOBEN: Fallback wenn kein player_active
            fallback_font = fonts.normal
            fallback_text = "Kein Monster ausgewählt"
            fallback_surface = fallback_font.render(fallback_text, True, self.UI_COLOR)
            surface.blit(fallback_surface, (self.MENU_POS[0] + 4, self.MENU_POS[1] + 20))
    
    def draw_talent_status(self, surface: pygame.Surface, monster) -> None:
        """Zeichne Talent-Status für ein Monster."""
        if not monster or not hasattr(monster, 'talents'):
            return
        
        # Talent-Status Panel
        panel_rect = pygame.Rect(10, 10, 200, 100)
        pygame.draw.rect(surface, (20, 20, 40), panel_rect)
        pygame.draw.rect(surface, (100, 150, 255), panel_rect, 2)
        
        # Titel
        title_font = fonts.normal
        title_text = title_font.render("Talente", True, (255, 255, 255))
        surface.blit(title_text, (panel_rect.x + 5, panel_rect.y + 5))
        
        # Talent-Liste
        y_offset = 25
        for i, talent_instance in enumerate(monster.talents[:3]):  # Max 3 Talente anzeigen
            if talent_instance.is_learned:
                try:
                    from engine.systems.talent_system import get_talent_database
                    talent_db = get_talent_database()
                    talent = talent_db.get_talent(talent_instance.talent_id)
                    
                    if talent:
                        # Talent-Name und Tier
                        tier_stars = '★' * talent_instance.current_tier.value
                        talent_text = f"{talent.name} {tier_stars}"
                        
                        # Farbe basierend auf Tier
                        tier_colors = {
                            1: (200, 200, 200),  # Grau für Basic
                            2: (100, 255, 100),  # Grün für Intermediate
                            3: (100, 100, 255),  # Blau für Advanced
                            4: (255, 100, 255)   # Magenta für Master
                        }
                        color = tier_colors.get(talent_instance.current_tier.value, (255, 255, 255))
                        
                        talent_surface = fonts.small.render(talent_text, True, color)
                        surface.blit(talent_surface, (panel_rect.x + 5, panel_rect.y + y_offset))
                        
                        # Passive Fähigkeiten anzeigen
                        passive_abilities = talent.get_passive_abilities_for_tier(talent_instance.current_tier)
                        if passive_abilities:
                            ability_text = f"  +{len(passive_abilities)} Passive"
                            ability_surface = fonts.tiny.render(ability_text, True, (150, 150, 150))
                            surface.blit(ability_surface, (panel_rect.x + 5, panel_rect.y + y_offset + 10))
                            y_offset += 20
                        else:
                            y_offset += 15
                            
                except Exception as e:
                    logger.error(f"Error drawing talent status: {e}")
    
    def draw_item_menu(self, surface: pygame.Surface) -> None:
        """Zeichne Item-Menü."""
        menu_rect = pygame.Rect(self.MENU_POS[0], self.MENU_POS[1], self.MENU_SIZE[0], self.MENU_SIZE[1])
        pygame.draw.rect(surface, (30, 30, 30), menu_rect)
        pygame.draw.rect(surface, (80, 80, 80), menu_rect, 1)
        
        # Category tabs
        categories = ["HEILUNG", "KAMPF-ITEMS", "FLEISCH"]
        tab_width = self.MENU_SIZE[0] // 3
        
        for i, category in enumerate(categories):
            x = self.MENU_POS[0] + i * tab_width
            y = self.MENU_POS[1]
            
            # Highlight active category
            if i == self.state.current_item_category:
                tab_rect = pygame.Rect(x + 1, y + 1, tab_width - 2, 18)
                pygame.draw.rect(surface, (60, 60, 60), tab_rect)
            
            # Draw category text - use small font
            category_font = fonts.small
            text = category_font.render(category, True, self.UI_COLOR)
            text_rect = text.get_rect(center=(x + tab_width // 2, y + 9))
            surface.blit(text, text_rect)
        
        # Item list
        items = self._get_items_for_category(self.state.get_selected_item_category())
        item_y = self.MENU_POS[1] + 20
        
        for i, item in enumerate(items[:4]):  # Show max 4 items
            if i == self.state.selected_item:
                highlight_rect = pygame.Rect(self.MENU_POS[0] + 2, item_y + i * 8, self.MENU_SIZE[0] - 4, 6)
                pygame.draw.rect(surface, (60, 60, 60), highlight_rect)
            
            # Item text - use normal font for better readability
            item_font = fonts.normal
            item_text = f"{item['name']} x{item['count']}"
            text = item_font.render(item_text, True, self.UI_COLOR)
            surface.blit(text, (self.MENU_POS[0] + 4, item_y + i * 8))  # Increased line spacing
    
    def draw_switch_menu(self, surface: pygame.Surface) -> None:
        """Zeichne Team-Wechsel-Menü."""
        menu_rect = pygame.Rect(self.MENU_POS[0], self.MENU_POS[1], self.MENU_SIZE[0], self.MENU_SIZE[1])
        pygame.draw.rect(surface, (30, 30, 30), menu_rect)
        pygame.draw.rect(surface, (80, 80, 80), menu_rect, 1)
        
        # Team list
        team_y = self.MENU_POS[1] + 4
        
        for i, monster in enumerate(self.state.player_team[:6]):  # Max 6 team members
            if i == self.state.selected_team_member:
                highlight_rect = pygame.Rect(self.MENU_POS[0] + 2, team_y + i * 8, self.MENU_SIZE[0] - 4, 6)
                pygame.draw.rect(surface, (60, 60, 60), highlight_rect)
            
            # Monster info - use normal font for better readability
            monster_font = fonts.normal
            hp_ratio = monster.current_hp / monster.max_hp
            hp_bar = "█" * int(hp_ratio * 8) + "░" * (8 - int(hp_ratio * 8))
            monster_text = f"{monster.name} Lv.{monster.level} HP:{hp_bar}"
            text = monster_font.render(monster_text, True, self.UI_COLOR)
            surface.blit(text, (self.MENU_POS[0] + 4, team_y + i * 8))  # Increased line spacing
    
    
    
    def draw_scout_display(self, surface: pygame.Surface) -> None:
        """Zeichne Spähen-Anzeige."""
        # Delegate to scout display component
        if self.battle_ui.scout_display:
            self.battle_ui.scout_display.draw(surface)
    
    def render_turn_counter(self, surface: pygame.Surface) -> None:
        """
        Render Turn Counter Display.
        
        Args:
            surface: Pygame surface to draw on
        """
        if not self.battle_ui.battle_state:
            return
        
        # Get turn count from battle state
        turn_count = getattr(self.battle_ui.battle_state, 'turn_count', 1)
        
        # Position: Top right corner (Ruhrpott-Theme)
        counter_x = LOGICAL_WIDTH - 100
        counter_y = 10
        
        # Background with Ruhrpott styling
        counter_rect = pygame.Rect(counter_x, counter_y, 90, 25)
        pygame.draw.rect(surface, (40, 30, 20), counter_rect)  # Brown background
        pygame.draw.rect(surface, (120, 80, 40), counter_rect, 2)  # Gold border
        
        # Turn counter text with Ruhrpott styling
        counter_font = fonts.normal
        counter_text = f"Runde {turn_count}"
        text_surface = counter_font.render(counter_text, True, (255, 220, 100))  # Gold text
        text_rect = text_surface.get_rect(center=counter_rect.center)
        surface.blit(text_surface, text_rect)
        
        # Add subtle animation for turn changes
        if hasattr(self.battle_ui.battle_state, '_turn_changed') and self.battle_ui.battle_state._turn_changed:
            # Flash effect for new turn
            flash_alpha = int(128 + 127 * (pygame.time.get_ticks() % 1000) / 1000)
            flash_surface = pygame.Surface(counter_rect.size, pygame.SRCALPHA)
            flash_surface.fill((255, 255, 0, flash_alpha))
            surface.blit(flash_surface, counter_rect, special_flags=pygame.BLEND_ALPHA_SDL2)
    
    def draw_message_box(self, surface: pygame.Surface) -> None:
        """Zeichne Nachrichten-Box - VERBESSERTE SICHTBARKEIT."""
        # CRITICAL: Check both current_message sources
        message = self.battle_ui.current_message or self.state.current_message
        if not message:
            return
        
        # Message box - größer und besser sichtbar für 320x180
        message_rect = pygame.Rect(8, 140, 304, 32)  # Größer und zentrierter
        
        # Hintergrund mit besserem Kontrast
        pygame.draw.rect(surface, (10, 10, 10), message_rect)  # Dunkler Hintergrund
        pygame.draw.rect(surface, (100, 100, 100), message_rect, 2)  # Dickerer Rand
        
        # Innerer Rahmen für bessere Definition
        inner_rect = pygame.Rect(10, 142, 300, 28)
        pygame.draw.rect(surface, (30, 30, 30), inner_rect)
        pygame.draw.rect(surface, (60, 60, 60), inner_rect, 1)
        
        # Message text - größere Schrift für bessere Lesbarkeit
        message_font = fonts.large  # Größere Schrift
        text = message_font.render(message, True, (255, 255, 255))  # Weißer Text
        
        # Text zentrieren
        text_rect = text.get_rect(center=(160, 156))  # Zentriert in der Box
        surface.blit(text, text_rect)
        
        # Blink-Effekt wenn Timer läuft
        timer = self.battle_ui.message_timer or self.state.message_timer
        if timer > 0:
            # Subtiler Blink-Effekt
            blink_alpha = int(128 + 127 * (timer % 0.5) / 0.5)
            blink_surface = pygame.Surface((304, 32), pygame.SRCALPHA)
            blink_surface.fill((255, 255, 255, blink_alpha))
            surface.blit(blink_surface, (8, 140), special_flags=pygame.BLEND_ALPHA_SDL2)
    
    def draw_visual_effects(self, surface: pygame.Surface) -> None:
        """ENHANCED: Zeichne neue Animation-Systeme."""
        # Draw enhanced damage numbers
        self.draw_enhanced_damage_numbers(surface)
        
        # Draw visual effects
        self.draw_enhanced_particle_effects(surface)
        
        # Draw attack animations
        self.draw_attack_animations(surface)
        
        # Legacy support - draw old damage numbers if any exist
        self.draw_legacy_damage_numbers(surface)
        self.draw_legacy_particle_effects(surface)
    
    def draw_enhanced_damage_numbers(self, surface: pygame.Surface) -> None:
        """ENHANCED: Zeichne Damage-Numbers mit neuen Animation-Systemen."""
        for anim in self.damage_renderer.get_active_animations():
            if not anim.active:
                continue
                
            # Choose font based on type
            if anim.is_critical:
                damage_font = fonts.huge
            elif anim.is_super_effective:
                damage_font = fonts.large
            else:
                damage_font = fonts.normal
            
            # Render damage number with scale
            text = damage_font.render(str(anim.value), True, anim.color)
            
            # Apply scale for critical hits
            if anim.scale != 1.0:
                size = text.get_size()
                scaled_size = (int(size[0] * anim.scale), int(size[1] * anim.scale))
                text = pygame.transform.scale(text, scaled_size)
            
            # Apply alpha
            text.set_alpha(anim.alpha)
            
            # Draw with position
            surface.blit(text, (int(anim.position[0]), int(anim.position[1])))
    
    def draw_enhanced_particle_effects(self, surface: pygame.Surface) -> None:
        """ENHANCED: Zeichne Particle Effects mit neuen Animation-Systemen."""
        for effect in self.visual_effects.get_active_effects():
            if not effect.active:
                continue
                
            # Calculate alpha based on timer
            progress = 1.0 - (effect.timer / effect.duration)
            alpha = int(255 * (1.0 - progress) * effect.intensity)
            
            # Draw effect based on type
            if effect.effect_type == "sparkle":
                self._draw_sparkle_effect(surface, effect, alpha)
            elif effect.effect_type == "explosion":
                self._draw_explosion_effect(surface, effect, alpha)
            elif effect.effect_type == "heal":
                self._draw_heal_effect(surface, effect, alpha)
            elif effect.effect_type in ["poison", "burn", "freeze", "paralysis", "sleep", "confusion"]:
                self._draw_status_effect(surface, effect, alpha)
    
    def draw_attack_animations(self, surface: pygame.Surface) -> None:
        """Zeichne Attack-Animationen."""
        # Basic attack animation implementation
        for attack in self.state.animations["attacks"]:
            if attack["timer"] > 0:
                # Draw attack effect
                self._draw_attack_effect(surface, attack)
    
    def _draw_sparkle_effect(self, surface: pygame.Surface, effect: VisualEffect, alpha: int) -> None:
        """Zeichne Sparkle-Effekt."""
        for i in range(8):
            angle = (effect.timer * 360 + i * 45) % 360
            radius = 10 + i * 2
            x = effect.position[0] + math.cos(math.radians(angle)) * radius
            y = effect.position[1] + math.sin(math.radians(angle)) * radius
            
            # Create sparkle surface
            sparkle_surface = pygame.Surface((4, 4), pygame.SRCALPHA)
            pygame.draw.circle(sparkle_surface, (*effect.color, alpha), (2, 2), 2)
            surface.blit(sparkle_surface, (int(x), int(y)))
    
    def _draw_explosion_effect(self, surface: pygame.Surface, effect: VisualEffect, alpha: int) -> None:
        """Zeichne Explosion-Effekt."""
        # Draw expanding circle
        radius = int(20 * (1.0 - effect.timer / effect.duration))
        if radius > 0:
            explosion_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(explosion_surface, (*effect.color, alpha), (radius, radius), radius)
            surface.blit(explosion_surface, (int(effect.position[0] - radius), int(effect.position[1] - radius)))
    
    def _draw_heal_effect(self, surface: pygame.Surface, effect: VisualEffect, alpha: int) -> None:
        """Zeichne Heal-Effekt."""
        # Draw upward floating particles
        for i in range(5):
            offset_y = -i * 10 - (1.0 - effect.timer / effect.duration) * 30
            particle_surface = pygame.Surface((3, 3), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, (*effect.color, alpha), (1, 1), 1)
            surface.blit(particle_surface, (int(effect.position[0] + i * 2), int(effect.position[1] + offset_y)))
    
    def _draw_status_effect(self, surface: pygame.Surface, effect: VisualEffect, alpha: int) -> None:
        """Zeichne Status-Effekt."""
        # Draw pulsing circle
        pulse = math.sin(effect.timer * 10) * 0.5 + 0.5
        radius = int(8 + pulse * 4)
        if radius > 0:
            status_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(status_surface, (*effect.color, alpha), (radius, radius), radius, 2)
            surface.blit(status_surface, (int(effect.position[0] - radius), int(effect.position[1] - radius)))
    
    def _draw_attack_effect(self, surface: pygame.Surface, attack: Dict[str, Any]) -> None:
        """Zeichne Attack-Effekt."""
        # Basic attack effect - can be expanded
        if attack["phase"] == 0:
            # Draw attack line
            pygame.draw.line(surface, (255, 255, 0), 
                           (100, 100), (200, 100), 3)
        elif attack["phase"] == 1:
            # Draw impact effect
            pygame.draw.circle(surface, (255, 100, 0), (200, 100), 10)
    
    def draw_legacy_damage_numbers(self, surface: pygame.Surface) -> None:
        """Legacy: Zeichne Schadens-Nummern aus BattleUIState."""
        for damage in self.state.animations["damage_numbers"]:
            if damage["timer"] > 0:
                # Damage number - use larger fonts for better visibility
                damage_font = fonts.large
                color = damage["color"]
                
                # Scale for critical hits
                if damage["is_critical"]:
                    damage_font = fonts.huge  # Even larger font for criticals
                
                text = damage_font.render(str(damage["value"]), True, color)
                
                # Position with animation
                x = int(damage["pos"][0])
                y = int(damage["pos"][1])
                
                # Fade out
                alpha = int(255 * (damage["timer"] / 1.5))  # Normalize to 1.5s duration
                text.set_alpha(alpha)
                
                surface.blit(text, (x, y))
    
    def draw_legacy_particle_effects(self, surface: pygame.Surface) -> None:
        """Legacy: Zeichne Partikel-Effekte aus BattleUIState."""
        for particle in self.state.animations["particles"]:
            if particle["timer"] > 0:
                # Particle position
                x = int(particle["pos"][0])
                y = int(particle["pos"][1])
                
                # Particle color and size
                color = particle["color"]
                size = int(particle["size"])
                
                # Fade out
                alpha = int(255 * (particle["timer"] / 1.5))  # Normalize to 1.5s duration
                
                # Draw particle as small circle
                particle_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(particle_surface, (*color, alpha), (size, size), size)
                surface.blit(particle_surface, (x - size, y - size))
    
    def draw_screen_effects(self, surface: pygame.Surface) -> None:
        """Zeichne Bildschirm-Effekte aus BattleUIState - ENHANCED SCREEN EFFECTS."""
        # Screen flash from animation system
        if self.state.animations["screen_effects"]["flash"]["active"]:
            flash_data = self.state.animations["screen_effects"]["flash"]
            flash_surface = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT))
            flash_surface.fill(flash_data["color"])
            
            # Calculate alpha based on timer and intensity with smooth fade
            progress = 1.0 - (flash_data["timer"] / 0.3)  # Normalize to 0.3s duration
            alpha = int(255 * flash_data["intensity"] * progress)
            flash_surface.set_alpha(max(0, min(255, alpha)))
            surface.blit(flash_surface, (0, 0))
        
        # Legacy screen flash support
        elif self.state.screen_flash_timer > 0:
            flash_surface = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT))
            flash_surface.fill(self.state.screen_flash_color)
            alpha = int(self.state.screen_flash_intensity * (self.state.screen_flash_timer / 0.2))
            flash_surface.set_alpha(max(0, min(255, alpha)))
            surface.blit(flash_surface, (0, 0))
    
    def apply_screen_shake(self, surface: pygame.Surface) -> pygame.Surface:
        """Apply screen shake effect - ENHANCED CAMERA SHAKE."""
        if self.state.animations["screen_effects"]["shake"]["active"]:
            shake_data = self.state.animations["screen_effects"]["shake"]
            offset = shake_data["offset"]
            
            # Create shaken surface
            shaken_surface = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT))
            shaken_surface.blit(surface, offset)
            return shaken_surface
        
        return surface
    
    def trigger_screen_flash(self, color: Tuple[int, int, int] = (255, 255, 255), 
                           intensity: float = 0.8, duration: float = 0.3) -> None:
        """Trigger screen flash effect - ENHANCED VISUAL IMPACT."""
        self.state.trigger_screen_flash(color, intensity, duration)
        logger.debug(f"Screen flash triggered: color={color}, intensity={intensity}")
    
    def trigger_screen_shake(self, intensity: float = 5.0, duration: float = 0.3) -> None:
        """Trigger screen shake effect - ENHANCED IMPACT EFFECTS."""
        self.state.trigger_screen_shake(intensity, duration)
        logger.debug(f"Screen shake triggered: intensity={intensity}, duration={duration}")
    
    def trigger_damage_flash(self, target, damage: int, is_critical: bool = False) -> None:
        """Trigger damage-specific screen effects - CONTEXTUAL EFFECTS."""
        if is_critical:
            # Critical hit - yellow flash with shake
            self.trigger_screen_flash((255, 255, 0), 0.6, 0.2)
            self.trigger_screen_shake(4.0, 0.25)
        elif damage > 50:
            # High damage - red flash with shake
            self.trigger_screen_flash((255, 100, 100), 0.4, 0.15)
            self.trigger_screen_shake(2.0, 0.15)
        else:
            # Normal damage - subtle white flash
            self.trigger_screen_flash((255, 255, 255), 0.2, 0.1)
    
    def trigger_healing_flash(self, healing: int) -> None:
        """Trigger healing-specific screen effects - POSITIVE FEEDBACK."""
        if healing > 30:
            # High healing - green flash
            self.trigger_screen_flash((0, 255, 0), 0.3, 0.15)
        else:
            # Normal healing - subtle green flash
            self.trigger_screen_flash((0, 255, 0), 0.15, 0.1)
    
    def trigger_status_flash(self, status: str) -> None:
        """Trigger status-specific screen effects - STATUS FEEDBACK."""
        status_colors = {
            "BURN": (255, 100, 0),      # Orange
            "POISON": (128, 0, 128),    # Purple
            "PARALYSIS": (255, 255, 0), # Yellow
            "SLEEP": (0, 0, 255),       # Blue
            "FREEZE": (0, 255, 255),    # Cyan
            "CONFUSION": (255, 0, 255), # Magenta
            "FLINCH": (255, 128, 128)   # Light Red
        }
        
        color = status_colors.get(status.upper(), (255, 255, 255))
        self.trigger_screen_flash(color, 0.4, 0.2)
        logger.debug(f"Status flash: {status} -> {color}")
    
    # Helper Methods
    
    def _draw_arena_elements(self, surface: pygame.Surface) -> None:
        """Zeichne Arena-Elemente."""
        # Draw arena decorations
        arena_rect = pygame.Rect(20, 20, 280, 140)
        
        # Arena floor pattern
        for x in range(20, 300, 16):
            for y in range(20, 160, 16):
                if (x + y) % 32 == 0:
                    tile_rect = pygame.Rect(x, y, 16, 16)
                    pygame.draw.rect(surface, (30, 30, 30), tile_rect)
        
        # Arena border decorations
        pygame.draw.rect(surface, (80, 80, 80), arena_rect, 2)
        
        # Corner pillars
        pillar_positions = [(25, 25), (275, 25), (25, 135), (275, 135)]
        for pos in pillar_positions:
            pillar_rect = pygame.Rect(pos[0], pos[1], 8, 8)
            pygame.draw.rect(surface, (100, 100, 100), pillar_rect)
            pygame.draw.rect(surface, (120, 120, 120), pillar_rect, 1)
        
        # Arena center circle
        center_x, center_y = 160, 90
        pygame.draw.circle(surface, (40, 40, 40), (center_x, center_y), 20, 2)
        pygame.draw.circle(surface, (60, 60, 60), (center_x, center_y), 15, 1)
    
    # _create_fallback_sprite method removed - using enhanced version from battle_ui_core.py
    
    # Legacy status icon methods removed - using enhanced versions above
    
    # _get_hp_color method removed - using version from battle_ui_core.py
    
    # ===== REDUNDANT METHODS REMOVED =====
    # _get_moves_by_category() is now handled by MenuManager
    
    def update_hp_bar(self, monster, animated=True):
        """Update HP Bar with Enhanced Animation System."""
        if not monster:
            return
        
        # Get monster ID
        monster_id = getattr(monster, 'id', id(monster))
        
        # Calculate HP percentage
        hp_percentage = monster.current_hp / monster.max_hp if monster.max_hp > 0 else 0
        hp_percentage = max(0, min(1, hp_percentage))  # Clamp between 0 and 1
        
        # ENHANCED: Start smooth HP animation with new system
        if animated:
            # Get old HP value if animating
            old_hp = monster.current_hp
            if self.hp_animator.is_animating(monster_id):
                old_hp = self.hp_animator.get_animated_hp(monster_id, monster.current_hp, monster.max_hp)
            
            # Add animation with enhanced system
            self.hp_animator.add_animation(monster_id, old_hp, monster.current_hp, monster.max_hp, duration=0.5)
            
            # Fallback: Also add to legacy system for compatibility
            self.state.add_hp_animation(monster_id, old_hp, monster.current_hp, monster.max_hp, duration=0.5)
        
        logger.info(f"🎯 Enhanced HP bar updated: {monster.name} {monster.current_hp}/{monster.max_hp} ({hp_percentage:.1%})")
    
    def show_damage_number(self, target, damage: int, is_critical: bool = False, is_super_effective: bool = False) -> None:
        """Show damage number with Enhanced Animation System."""
        if not target or damage <= 0:
            return
        
        # Get position based on target
        if target == self.state.player_active:
            pos = self.PLAYER_POS
        else:
            pos = self.ENEMY_POS
        
        # Enhanced color logic
        if is_critical:
            color = (255, 255, 0)  # Yellow for critical
        elif is_super_effective:
            color = (255, 100, 0)  # Orange for super effective
        else:
            color = (255, 255, 255)  # White for normal
        
        # ENHANCED: Add damage number with new animation system
        self.damage_renderer.add_damage_number(damage, pos, color, is_critical, is_super_effective)
        
        # Fallback: Also add to legacy system for compatibility
        self.state.add_damage_number(damage, pos, color, is_critical)
        
        # Add visual effects
        if is_critical:
            self.visual_effects.add_effect("explosion", pos, 1.5)
            self.state.trigger_screen_shake(2.0, 0.15)
        elif is_super_effective:
            self.visual_effects.add_effect("sparkle", pos, 1.0)
        
        logger.debug(f"Enhanced damage number: {damage} at {pos} (critical: {is_critical}, super: {is_super_effective})")
    
    def show_healing_number(self, target, healing: int) -> None:
        """Show healing number with Enhanced Animation System."""
        if not target or healing <= 0:
            return
        
        # Get position based on target
        if target == self.state.player_active:
            pos = self.PLAYER_POS
        else:
            pos = self.ENEMY_POS
        
        # Green color for healing
        color = (0, 255, 0)
        
        # ENHANCED: Add healing number with new animation system
        self.damage_renderer.add_damage_number(healing, pos, color, False, False)
        
        # Fallback: Also add to legacy system for compatibility
        self.state.add_damage_number(healing, pos, color, False)
        
        # Add healing visual effect
        self.visual_effects.add_effect("heal", pos, 1.2)
        
        # Gentle screen flash for healing
        self.state.trigger_screen_flash((0, 255, 0), 0.2, 0.1)
        
        logger.debug(f"Enhanced healing number: {healing} at {pos}")
    
    def show_status_effect(self, target, status):
        """Show status effect with Enhanced Animation System."""
        if not target or not status:
            return
        
        # Get target ID
        target_id = getattr(target, 'id', id(target))
        
        # Get position based on target
        if target == self.state.player_active:
            pos = self.PLAYER_POS
        else:
            pos = self.ENEMY_POS
        
        # ENHANCED: Add status effect with new animation system
        self.visual_effects.add_effect(status.lower(), pos, 1.0)
        
        # Fallback: Also add to legacy system for compatibility
        self.state.add_status_effect(target_id, status, 2.0)
        
        logger.debug(f"Enhanced status effect {status} shown for {target.name}")
    
    def play_faint_animation(self, monster):
        """MUSS implementiert sein!"""
        if not monster:
            return
        
        # Get monster ID
        monster_id = getattr(monster, 'id', id(monster))
        
        # Start faint animation in BattleUIState
        self.state.start_faint_animation(monster_id)
        
        logger.debug(f"Faint animation started for {monster.name}")
    
    def play_appear_animation(self, monster):
        """MUSS implementiert sein!"""
        if not monster:
            return
        
        # Get monster ID
        monster_id = getattr(monster, 'id', id(monster))
        
        # Start appear animation in BattleUIState
        self.state.start_appear_animation(monster_id)
        
        logger.debug(f"Appear animation started for {monster.name}")
    
    def shake_camera(self, intensity: float = 1.0, duration: float = 0.5) -> None:
        """Shake camera effect."""
        # Trigger screen shake in BattleUIState
        self.state.trigger_screen_shake(intensity * 5, duration)
        
        logger.debug(f"Camera shake: intensity={intensity}, duration={duration}")
    
    def flash_screen(self, color=(255, 255, 255), duration: float = 0.3) -> None:
        """Flash screen effect."""
        # Trigger screen flash in BattleUIState
        self.state.trigger_screen_flash(color, 0.8, duration)
        
        logger.debug(f"Screen flash: color={color}, duration={duration}")
    
    def update_animations(self, dt: float) -> None:
        """Update all animations using Enhanced Animation Systems with Performance Optimization."""
        # Update frame timing
        self.update_frame_timing(dt)
        
        # Skip animation updates if frame time is too high (performance optimization)
        if dt > self.frame_skip_threshold and self.performance_mode != "low_power":
            # Skip some animation updates to maintain FPS
            if self.frame_count % 2 == 0:  # Update every other frame
                self.hp_animator.update_animations(dt)
                self.damage_renderer.update_animations(dt)
            else:
                self.visual_effects.update_effects(dt)
        else:
            # Normal update
            self.hp_animator.update_animations(dt)
            self.damage_renderer.update_animations(dt)
            self.visual_effects.update_effects(dt)
        
        # Update legacy animations
        self.state.update_animations(dt)
        
        # Performance monitoring
        if self.frame_count % 60 == 0:  # Every 60 frames
            self._log_performance_stats()
        
        # Animation culling (remove off-screen animations)
        if self.cull_off_screen_animations:
            self._cull_off_screen_animations()
    
    def _log_performance_stats(self) -> None:
        """Log performance statistics for animation systems."""
        hp_animations = len(self.hp_animator.animations)
        damage_animations = len(self.damage_renderer.animations)
        visual_effects = len(self.visual_effects.effects)
        
        # Calculate average FPS
        if self.frame_times:
            avg_frame_time = sum(self.frame_times) / len(self.frame_times)
            current_fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 0
        else:
            current_fps = 0
        
        logger.debug(f"🎨 Animation Stats: HP={hp_animations}, Damage={damage_animations}, Effects={visual_effects}, FPS={current_fps:.1f}")
        
        # Check for performance issues
        total_animations = hp_animations + damage_animations + visual_effects
        if total_animations > self.animation_queue_limit:
            logger.warning(f"⚠️ High animation count: {total_animations} (limit: {self.animation_queue_limit})")
        
        # Check FPS performance
        if current_fps < 45:  # Below 45 FPS
            logger.warning(f"⚠️ Low FPS detected: {current_fps:.1f} (target: {self.target_fps})")
            self._optimize_performance()
    
    def _optimize_performance(self) -> None:
        """Optimize performance by reducing animation quality."""
        if self.performance_mode == "normal":
            self.performance_mode = "high_performance"
            # Reduce animation limits
            self.hp_animator.max_animations = 5
            self.damage_renderer.max_animations = 10
            self.visual_effects.max_effects = 25
            logger.info("🔧 Performance mode: HIGH_PERFORMANCE")
        elif self.performance_mode == "high_performance":
            self.performance_mode = "low_power"
            # Further reduce animation limits
            self.hp_animator.max_animations = 3
            self.damage_renderer.max_animations = 5
            self.visual_effects.max_effects = 10
            logger.info("🔧 Performance mode: LOW_POWER")
    
    def update_frame_timing(self, dt: float) -> None:
        """Update frame timing for performance monitoring."""
        self.frame_times.append(dt)
        if len(self.frame_times) > self.max_frame_times:
            self.frame_times.pop(0)
        
        self.last_frame_time = dt
    
    def _cull_off_screen_animations(self) -> None:
        """Remove animations that are off-screen to improve performance."""
        # Cull damage numbers that are off-screen
        for anim in self.damage_renderer.animations[:]:
            if not self.screen_bounds.collidepoint(anim.position):
                anim.active = False
                self.damage_renderer.animations.remove(anim)
        
        # Cull visual effects that are off-screen
        for effect in self.visual_effects.effects[:]:
            if not self.screen_bounds.collidepoint(effect.position):
                effect.active = False
                self.visual_effects.effects.remove(effect)
    
    def set_performance_mode(self, mode: str) -> None:
        """Set performance mode (normal, high_performance, low_power)."""
        if mode in ["normal", "high_performance", "low_power"]:
            self.performance_mode = mode
            logger.info(f"🔧 Performance mode set to: {mode}")
        else:
            logger.warning(f"Invalid performance mode: {mode}")
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics."""
        if self.frame_times:
            avg_frame_time = sum(self.frame_times) / len(self.frame_times)
            current_fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 0
        else:
            current_fps = 0
        
        return {
            'fps': current_fps,
            'target_fps': self.target_fps,
            'performance_mode': self.performance_mode,
            'hp_animations': len(self.hp_animator.animations),
            'damage_animations': len(self.damage_renderer.animations),
            'visual_effects': len(self.visual_effects.effects),
            'total_animations': (len(self.hp_animator.animations) + 
                               len(self.damage_renderer.animations) + 
                               len(self.visual_effects.effects)),
            'animation_queue_limit': self.animation_queue_limit,
            'frame_count': self.frame_count
        }
    
    def render_victory_screen(self, surface: pygame.Surface) -> None:
        """Render Victory Screen mit detaillierten Belohnungen."""
        # Background
        surface.fill((0, 20, 0))  # Dark green background
        
        # Victory title
        victory_font = fonts.huge
        victory_text = victory_font.render("SIEG!", True, (255, 255, 0))  # Gold
        victory_rect = victory_text.get_rect(center=(LOGICAL_WIDTH // 2, 40))
        surface.blit(victory_text, victory_rect)
        
        # Get battle rewards
        rewards = self._get_battle_rewards()
        
        # EXP display
        y_pos = 70
        exp_font = fonts.large
        exp_text = exp_font.render(f"EXP erhalten: {rewards.get('exp', 0)}", True, (255, 255, 255))
        surface.blit(exp_text, (20, y_pos))
        y_pos += 25
        
        # Talent EXP display
        talent_exp = rewards.get('talent_exp', 0)
        if talent_exp > 0:
            talent_font = fonts.normal
            talent_text = talent_font.render(f"Talent-EXP: {talent_exp}", True, (200, 200, 255))
            surface.blit(talent_text, (20, y_pos))
            y_pos += 20
        
        # Level ups
        level_ups = rewards.get('level_ups', [])
        if level_ups:
            level_font = fonts.normal
            for level_up in level_ups:
                level_text = level_font.render(f"{level_up['monster']} → Level {level_up['new_level']}!", True, (0, 255, 0))
                surface.blit(level_text, (20, y_pos))
                y_pos += 20
        
        # Items found
        items = rewards.get('items', [])
        if items:
            item_font = fonts.normal
            item_text = item_font.render("Items gefunden:", True, (255, 255, 255))
            surface.blit(item_text, (20, y_pos))
            y_pos += 20
            
            for item in items:
                item_info = f"  - {item['name']} x{item['count']}"
                item_surface = item_font.render(item_info, True, (200, 200, 200))
                surface.blit(item_surface, (20, y_pos))
                y_pos += 15
        
        # Money gained
        money = rewards.get('money', 0)
        if money > 0:
            money_font = fonts.normal
            money_text = money_font.render(f"Gold erhalten: {money}", True, (255, 255, 0))
            surface.blit(money_text, (20, y_pos))
            y_pos += 25
        
        # Continue prompt
        continue_font = fonts.normal
        continue_text = continue_font.render("[SPACE] Weiter", True, (255, 255, 255))
        continue_rect = continue_text.get_rect(center=(LOGICAL_WIDTH // 2, LOGICAL_HEIGHT - 20))
        surface.blit(continue_text, continue_rect)
        
        # Blink effect
        if int(pygame.time.get_ticks() / 500) % 2:
            pygame.draw.rect(surface, (255, 255, 255), continue_rect, 2)

    def render_defeat_screen(self, surface: pygame.Surface) -> None:
        """Render Defeat Screen."""
        # Background
        surface.fill((20, 0, 0))  # Dark red background
        
        # Defeat title
        defeat_font = fonts.huge
        defeat_text = defeat_font.render("NIEDERLAGE!", True, (255, 100, 100))  # Red
        defeat_rect = defeat_text.get_rect(center=(LOGICAL_WIDTH // 2, 60))
        surface.blit(defeat_text, defeat_rect)
        
        # Defeat message
        message_font = fonts.large
        message_text = message_font.render("Alle deine Monster sind ohnmächtig!", True, (255, 255, 255))
        message_rect = message_text.get_rect(center=(LOGICAL_WIDTH // 2, 100))
        surface.blit(message_text, message_rect)
        
        # Return to main menu prompt
        continue_font = fonts.normal
        continue_text = continue_font.render("[SPACE] Hauptmenü", True, (255, 255, 255))
        continue_rect = continue_text.get_rect(center=(LOGICAL_WIDTH // 2, LOGICAL_HEIGHT - 20))
        surface.blit(continue_text, continue_rect)
        
        # Blink effect
        if int(pygame.time.get_ticks() / 500) % 2:
            pygame.draw.rect(surface, (255, 255, 255), continue_rect, 2)

    def _get_battle_rewards(self) -> Dict[str, Any]:
        """Hole Battle-Belohnungen."""
        if not self.battle_ui.battle_state:
            return {'exp': 0, 'money': 0, 'items': [], 'talent_exp': 0, 'level_ups': []}
        
        # Basic rewards
        rewards = {
            'exp': 125,  # Base EXP
            'money': 50,  # Base money
            'items': [
                {'name': 'Kräuter', 'count': 2},
                {'name': 'Gold', 'count': 50}
            ],
            'talent_exp': 25,  # 10% of monster EXP + bonus
            'level_ups': []
        }
        
        # Check for level ups
        if self.battle_ui.battle_state.player_active:
            monster = self.battle_ui.battle_state.player_active
            if hasattr(monster, 'level') and hasattr(monster, 'experience'):
                # Simulate level up check
                if monster.experience >= monster.level * 100:  # Simple level up formula
                    rewards['level_ups'].append({
                        'monster': monster.name,
                        'new_level': monster.level + 1
                    })
        
        return rewards

    # ===== REDUNDANT METHODS REMOVED =====
    # _get_items_for_category() is now handled by MenuManager