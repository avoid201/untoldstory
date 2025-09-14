"""
Battle UI Renderer - Schlanke Haupt-Renderer-Klasse
Verantwortlich für die Koordination aller visuellen Darstellungen

ENHANCED: Modular aufgebaut mit separaten Animation-Systemen
- Delegiert an spezialisierte Animation-Manager
- 60 FPS Performance-optimiert
- Saubere Trennung der Verantwortlichkeiten
"""

import pygame
import logging
from typing import List, Tuple, Optional, Dict, Any

from engine.core.config import LOGICAL_WIDTH, LOGICAL_HEIGHT, Colors
from engine.ui.battle_ui_utils import fonts, sprites
from .battle_ui_state import BattleMenuState
from .animations import HPBarAnimator, DamageNumberRenderer, VisualEffectsManager

# Setup logger
logger = logging.getLogger(__name__)


class BattleUIRenderer:
    """
    Battle UI Renderer - Koordiniert alle visuellen Darstellungen.
    ENHANCED: Modular aufgebaut mit separaten Animation-Systemen.
    """
    
    def __init__(self, battle_ui):
        self.battle_ui = battle_ui
        self.state = battle_ui.state
        
        # Animation systems
        self.hp_animator = HPBarAnimator()
        self.damage_renderer = DamageNumberRenderer()
        self.visual_effects = VisualEffectsManager()
        
        # UI settings
        self.arena_bg_color = (30, 30, 30)
        self.panel_bg_color = (20, 20, 20)
        self.border_color = (100, 100, 100)
        
        logger.debug("BattleUIRenderer initialized with modular animation systems")
    
    def update(self, dt: float) -> None:
        """Update alle Animation-Systeme."""
        # Update HP animations
        hp_updates = self.hp_animator.update(dt)
        
        # Update damage numbers
        self.damage_renderer.update(dt)
        
        # Update visual effects
        self.visual_effects.update(dt)
        
        # Update UI state with HP changes
        if hp_updates and hasattr(self.state, 'animations'):
            for monster_id, hp_ratio in hp_updates.items():
                if monster_id in self.state.animations.get("hp_bars", {}):
                    self.state.animations["hp_bars"][monster_id]["current"] = hp_ratio
    
    def render(self, surface: pygame.Surface) -> None:
        """Haupt-Render-Methode - koordiniert alle visuellen Elemente."""
        # Clear surface
        surface.fill(self.arena_bg_color)
        
        # Render arena background
        self._draw_arena_background(surface)
        
        # Render monsters
        self.draw_monsters(surface)
        
        # Render UI elements
        self.draw_ui_elements(surface)
        
        # Render menus
        self.draw_menus(surface)
        
        # Render visual effects (last - on top)
        self.visual_effects.render(surface)
        
        # Render damage numbers (last - on top of everything)
        self.damage_renderer.render(surface)
    
    def _draw_arena_background(self, surface: pygame.Surface) -> None:
        """Draw arena background elements."""
        # Arena center circle
        center_x, center_y = 160, 90
        pygame.draw.circle(surface, (40, 40, 40), (center_x, center_y), 20, 2)
        pygame.draw.circle(surface, (60, 60, 60), (center_x, center_y), 15, 1)
    
    def draw_monsters(self, surface: pygame.Surface) -> None:
        """Draw player and enemy monsters."""
        if not self.battle_ui.battle_state:
            return
        
        # Draw player monster
        player_active = self.battle_ui.battle_state.player_active
        if player_active:
            self.draw_single_monster(surface, player_active, (50, 120), True)
        
        # Draw enemy monster
        enemy_active = self.battle_ui.battle_state.enemy_active
        if enemy_active:
            self.draw_single_monster(surface, enemy_active, (200, 60), False)
    
    def draw_single_monster(self, surface: pygame.Surface, monster, pos: Tuple[int, int], is_player: bool) -> None:
        """Draw single monster with sprite and status."""
        if not monster:
            return
        
        # Get monster sprite
        sprite = self._get_monster_sprite(monster)
        if sprite:
            surface.blit(sprite, pos)
        
        # Draw status effects
        self.draw_status_conditions(surface, monster, pos)
    
    def draw_status_conditions(self, surface: pygame.Surface, monster, pos: Tuple[int, int]) -> None:
        """Draw status conditions with enhanced animations."""
        if not monster:
            return
        
        # Get monster ID
        monster_id = monster.id if hasattr(monster, 'id') else id(monster)
        
        # Check for animated status effects
        if hasattr(self.state, 'animations') and monster_id in self.state.animations.get("status_effects", {}):
            effect = self.state.animations["status_effects"][monster_id]
            status = effect["status"]
            flash = effect.get("flash", False)
            
            # Enhanced status icon with animation
            status_icon = self._get_enhanced_status_icon(status, flash)
            if status_icon:
                icon_pos = (pos[0] - 20, pos[1] + 10)
                surface.blit(status_icon, icon_pos)
    
    def _get_enhanced_status_icon(self, status: str, flash: bool = False) -> Optional[pygame.Surface]:
        """Get enhanced status icon with animation support."""
        # Status icon mapping with enhanced visuals
        status_icons = {
            "BURN": self._create_enhanced_status_icon((255, 100, 0), "BR", flash),      # Orange - Brennen
            "POISON": self._create_enhanced_status_icon((128, 0, 128), "PS", flash),    # Purple - Gift
            "PARALYSIS": self._create_enhanced_status_icon((255, 255, 0), "PR", flash), # Yellow - Paralyse
            "SLEEP": self._create_enhanced_status_icon((0, 0, 255), "SL", flash),       # Blue - Schlaf
            "FREEZE": self._create_enhanced_status_icon((0, 255, 255), "FR", flash),    # Cyan - Einfrieren
            "CONFUSION": self._create_enhanced_status_icon((255, 0, 255), "CF", flash), # Magenta - Verwirrung
            "FLINCH": self._create_enhanced_status_icon((255, 128, 128), "FL", flash)   # Light Red - Zurückschrecken
        }
        
        return status_icons.get(status.upper())
    
    def _create_enhanced_status_icon(self, color: Tuple[int, int, int], text: str, flash: bool = False) -> pygame.Surface:
        """Create enhanced status icon with animation support."""
        icon_size = 16
        icon = pygame.Surface((icon_size, icon_size))
        
        # Apply flash effect
        if flash:
            # Pulsing effect
            import time
            pulse = (1 + 0.3 * abs(pygame.math.Vector2(0, 1).rotate(time.time() * 360))) / 1.3
            color = tuple(int(c * pulse) for c in color)
        
        # Draw icon background
        pygame.draw.circle(icon, color, (icon_size // 2, icon_size // 2), icon_size // 2)
        
        # Draw border
        pygame.draw.circle(icon, (255, 255, 255), (icon_size // 2, icon_size // 2), icon_size // 2, 1)
        
        # Draw text
        font = pygame.font.Font(None, 10)
        text_surface = font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(icon_size // 2, icon_size // 2))
        icon.blit(text_surface, text_rect)
        
        return icon
    
    def _get_monster_sprite(self, monster) -> Optional[pygame.Surface]:
        """Get monster sprite with fallback."""
        if not monster:
            return None
        
        # Try to get sprite from resource manager
        if hasattr(monster, 'species_id'):
            sprite = sprites.get_monster_sprite(monster.species_id)
            if sprite:
                return sprite
        
        # Fallback sprite
        return self._create_fallback_sprite(getattr(monster, 'species_id', 'unknown'))
    
    def _create_fallback_sprite(self, species_id: str) -> pygame.Surface:
        """Create fallback sprite - delegates to battle_ui_core."""
        # Use enhanced version from battle_ui_core
        if hasattr(self.battle_ui, '_create_fallback_sprite'):
            return self.battle_ui._create_fallback_sprite(species_id)
        
        # Simple fallback
        sprite = pygame.Surface((32, 32))
        sprite.fill((100, 100, 100))
        pygame.draw.rect(sprite, (150, 150, 150), (8, 8, 16, 16))
        return sprite
    
    def draw_ui_elements(self, surface: pygame.Surface) -> None:
        """Draw UI elements like HP bars, turn counter, etc."""
        # Draw HP bars
        self.draw_hp_bars(surface)
        
        # Draw turn counter
        self.render_turn_counter(surface)
        
        # Draw status panels
        self.draw_status_panels(surface)
    
    def draw_hp_bars(self, surface: pygame.Surface) -> None:
        """Draw HP bars for all monsters."""
        if not self.battle_ui.battle_state:
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
        
        # Calculate HP ratio (use animated value if available)
        monster_id = monster.id if hasattr(monster, 'id') else id(monster)
        animated_hp = self.hp_animator.get_current_hp(monster_id)
        
        if animated_hp is not None:
            hp_ratio = animated_hp / monster.max_hp if monster.max_hp > 0 else 0
        else:
            hp_ratio = monster.current_hp / monster.max_hp if monster.max_hp > 0 else 0
        
        # HP bar background
        bg_rect = pygame.Rect(pos[0], pos[1], bar_width, bar_height)
        pygame.draw.rect(surface, (60, 60, 60), bg_rect)
        
        # HP bar fill
        fill_width = int(bar_width * hp_ratio)
        if fill_width > 0:
            fill_rect = pygame.Rect(pos[0], pos[1], fill_width, bar_height)
            # Color based on HP percentage
            hp_color = self._get_hp_color(hp_ratio)
            pygame.draw.rect(surface, hp_color, fill_rect)
        
        # HP bar border
        pygame.draw.rect(surface, (200, 200, 200), bg_rect, 1)
    
    def _get_hp_color(self, ratio: float) -> Tuple[int, int, int]:
        """Get HP bar color based on HP ratio - delegates to battle_ui_core."""
        # Use version from battle_ui_core
        if hasattr(self.battle_ui, '_get_hp_color'):
            return self.battle_ui._get_hp_color(ratio)
        
        # Simple fallback
        if ratio > 0.6:
            return (0, 255, 0)  # Green
        elif ratio > 0.3:
            return (255, 255, 0)  # Yellow
        else:
            return (255, 0, 0)  # Red
    
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
        
        # Turn counter position (top right)
        counter_x = LOGICAL_WIDTH - 120
        counter_y = 10
        
        # Background panel
        panel_rect = pygame.Rect(counter_x - 5, counter_y - 5, 110, 25)
        pygame.draw.rect(surface, (40, 30, 20), panel_rect)  # Brown background
        pygame.draw.rect(surface, (139, 69, 19), panel_rect, 2)  # Brown border
        
        # Turn counter text
        font = fonts.get_font("normal")
        turn_text = f"Runde {turn_count}"
        text_surface = font.render(turn_text, True, (255, 215, 0))  # Gold text
        
        # Center text in panel
        text_rect = text_surface.get_rect(center=panel_rect.center)
        surface.blit(text_surface, text_rect)
        
        # Flash effect on turn change
        if hasattr(self.state, 'animations') and "turn_flash" in self.state.animations:
            flash_anim = self.state.animations["turn_flash"]
            if flash_anim.get("active", False):
                # Flash overlay
                flash_surface = pygame.Surface((110, 25))
                flash_alpha = int(100 * (1 - flash_anim.get("timer", 0) / flash_anim.get("duration", 0.5)))
                flash_surface.set_alpha(flash_alpha)
                flash_surface.fill((255, 255, 255))
                surface.blit(flash_surface, (counter_x - 5, counter_y - 5))
    
    def draw_status_panels(self, surface: pygame.Surface) -> None:
        """Draw status panels for monsters."""
        if not self.battle_ui.battle_state:
            return
        
        # Draw player status panel
        player_active = self.battle_ui.battle_state.player_active
        if player_active:
            self.draw_single_status_panel(surface, player_active, (10, 200), True)
        
        # Draw enemy status panel
        enemy_active = self.battle_ui.battle_state.enemy_active
        if enemy_active:
            self.draw_single_status_panel(surface, enemy_active, (170, 10), False)
    
    def draw_single_status_panel(self, surface: pygame.Surface, monster, pos: Tuple[int, int], is_player: bool) -> None:
        """Draw single status panel with enhanced information."""
        if not monster:
            return
        
        # Panel dimensions
        panel_width = 120
        panel_height = 80
        
        # Panel background
        panel_rect = pygame.Rect(pos[0], pos[1], panel_width, panel_height)
        pygame.draw.rect(surface, self.panel_bg_color, panel_rect)
        pygame.draw.rect(surface, self.border_color, panel_rect, 1)
        
        # Monster name
        font = fonts.get_font("small")
        name_text = getattr(monster, 'name', 'Unknown')
        name_surface = font.render(name_text, True, Colors.WHITE)
        surface.blit(name_surface, (pos[0] + 5, pos[1] + 5))
        
        # HP information
        hp_text = f"HP: {monster.current_hp}/{monster.max_hp}"
        hp_surface = font.render(hp_text, True, Colors.WHITE)
        surface.blit(hp_surface, (pos[0] + 5, pos[1] + 20))
        
        # HP bar in panel
        hp_ratio = monster.current_hp / monster.max_hp if monster.max_hp > 0 else 0
        hp_color = self._get_hp_color(hp_ratio)
        hp_bar_rect = pygame.Rect(pos[0] + 4, pos[1] + 35, 112, 8)
        pygame.draw.rect(surface, (20, 20, 20), hp_bar_rect)
        pygame.draw.rect(surface, hp_color, (pos[0] + 4, pos[1] + 35, int(112 * hp_ratio), 8))
        
        # Level and rank
        level_text = f"Lv.{getattr(monster, 'level', 1)}"
        rank_text = getattr(monster, 'rank', 'F')
        level_surface = font.render(level_text, True, Colors.WHITE)
        rank_surface = font.render(rank_text, True, (255, 215, 0))  # Gold
        surface.blit(level_surface, (pos[0] + 5, pos[1] + 50))
        surface.blit(rank_surface, (pos[0] + 80, pos[1] + 50))
    
    def draw_menus(self, surface: pygame.Surface) -> None:
        """Draw menus based on current state."""
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
    
    def draw_main_menu(self, surface: pygame.Surface) -> None:
        """Draw main battle menu."""
        # Menu background
        menu_rect = pygame.Rect(10, LOGICAL_HEIGHT - 80, LOGICAL_WIDTH - 20, 70)
        pygame.draw.rect(surface, self.panel_bg_color, menu_rect)
        pygame.draw.rect(surface, self.border_color, menu_rect, 2)
        
        # Menu options
        font = fonts.get_font("normal")
        options = ["Kampf", "Item", "Wechseln", "Spähen"]
        for i, option in enumerate(options):
            text_surface = font.render(option, True, Colors.WHITE)
            x = menu_rect.x + 20 + (i * 80)
            y = menu_rect.y + 25
            surface.blit(text_surface, (x, y))
    
    def draw_move_menu(self, surface: pygame.Surface) -> None:
        """Draw move selection menu."""
        # Menu background
        menu_rect = pygame.Rect(10, LOGICAL_HEIGHT - 120, LOGICAL_WIDTH - 20, 110)
        pygame.draw.rect(surface, self.panel_bg_color, menu_rect)
        pygame.draw.rect(surface, self.border_color, menu_rect, 2)
        
        # Move options
        font = fonts.get_font("normal")
        moves = ["Tackle", "Growl", "Vine Whip", "Razor Leaf"]
        for i, move in enumerate(moves):
            text_surface = font.render(move, True, Colors.WHITE)
            x = menu_rect.x + 20 + ((i % 2) * 150)
            y = menu_rect.y + 20 + ((i // 2) * 30)
            surface.blit(text_surface, (x, y))
    
    def draw_item_menu(self, surface: pygame.Surface) -> None:
        """Draw item selection menu."""
        # Menu background
        menu_rect = pygame.Rect(10, LOGICAL_HEIGHT - 120, LOGICAL_WIDTH - 20, 110)
        pygame.draw.rect(surface, self.panel_bg_color, menu_rect)
        pygame.draw.rect(surface, self.border_color, menu_rect, 2)
        
        # Item options
        font = fonts.get_font("normal")
        items = ["Trank", "Beleber", "Antidot", "Aufwecker"]
        for i, item in enumerate(items):
            text_surface = font.render(item, True, Colors.WHITE)
            x = menu_rect.x + 20 + ((i % 2) * 150)
            y = menu_rect.y + 20 + ((i // 2) * 30)
            surface.blit(text_surface, (x, y))
    
    def draw_switch_menu(self, surface: pygame.Surface) -> None:
        """Draw monster switch menu."""
        # Menu background
        menu_rect = pygame.Rect(10, LOGICAL_HEIGHT - 120, LOGICAL_WIDTH - 20, 110)
        pygame.draw.rect(surface, self.panel_bg_color, menu_rect)
        pygame.draw.rect(surface, self.border_color, menu_rect, 2)
        
        # Switch options
        font = fonts.get_font("normal")
        monsters = ["Bulbasaur", "Charmander", "Squirtle", "Pikachu"]
        for i, monster in enumerate(monsters):
            text_surface = font.render(monster, True, Colors.WHITE)
            x = menu_rect.x + 20 + ((i % 2) * 150)
            y = menu_rect.y + 20 + ((i // 2) * 30)
            surface.blit(text_surface, (x, y))
    
    def draw_scout_display(self, surface: pygame.Surface) -> None:
        """Draw scout display."""
        # Delegate to scout display component
        if self.battle_ui.scout_display:
            self.battle_ui.scout_display.draw(surface)
    
    def draw_message_box(self, surface: pygame.Surface) -> None:
        """Draw message box."""
        # Message box background
        msg_rect = pygame.Rect(10, LOGICAL_HEIGHT - 100, LOGICAL_WIDTH - 20, 90)
        pygame.draw.rect(surface, self.panel_bg_color, msg_rect)
        pygame.draw.rect(surface, self.border_color, msg_rect, 2)
        
        # Message text
        font = fonts.get_font("normal")
        message = "Wähle eine Aktion..."
        text_surface = font.render(message, True, Colors.WHITE)
        surface.blit(text_surface, (msg_rect.x + 20, msg_rect.y + 30))
    
    # Animation trigger methods
    def show_damage_number(self, target, damage: int, is_critical: bool = False, is_super_effective: bool = False) -> None:
        """Show damage number with animation."""
        # Get target position
        if hasattr(target, 'battle_position'):
            position = target.battle_position
        else:
            # Default position
            position = (160, 90)
        
        self.damage_renderer.add_damage_number(
            damage, position, is_critical, is_super_effective
        )
        
        # Trigger damage flash
        self.visual_effects.trigger_damage_flash(position)
        
        logger.debug(f"Damage number shown: {damage} at {position}")
    
    def show_healing_number(self, target, healing: int) -> None:
        """Show healing number with animation."""
        # Get target position
        if hasattr(target, 'battle_position'):
            position = target.battle_position
        else:
            # Default position
            position = (160, 90)
        
        self.damage_renderer.add_damage_number(
            healing, position, is_healing=True
        )
        
        logger.debug(f"Healing number shown: {healing} at {position}")
    
    def show_status_effect(self, target, status):
        """Show status effect animation."""
        # Get target position
        if hasattr(target, 'battle_position'):
            position = target.battle_position
        else:
            # Default position
            position = (160, 90)
        
        # Trigger particle burst for status effect
        status_colors = {
            'BURN': (255, 100, 0),
            'POISON': (128, 0, 128),
            'PARALYSIS': (255, 255, 0),
            'SLEEP': (0, 0, 255),
            'FREEZE': (0, 255, 255),
            'CONFUSION': (255, 0, 255)
        }
        
        color = status_colors.get(status, (255, 255, 255))
        self.visual_effects.trigger_particle_burst(position, color, count=15)
        
        logger.debug(f"Status effect shown: {status} at {position}")
    
    def play_faint_animation(self, monster):
        """Play faint animation for monster."""
        # Trigger screen shake
        self.visual_effects.trigger_screen_shake(intensity=3.0, duration=0.5)
        
        # Trigger screen flash
        self.visual_effects.trigger_screen_flash(color=(255, 0, 0), intensity=0.6, duration=0.3)
        
        logger.debug(f"Faint animation played for {getattr(monster, 'name', 'monster')}")
    
    def play_appear_animation(self, monster):
        """Play appear animation for monster."""
        # Get monster position
        if hasattr(monster, 'battle_position'):
            position = monster.battle_position
        else:
            # Default position
            position = (160, 90)
        
        # Trigger particle burst
        self.visual_effects.trigger_particle_burst(position, (255, 255, 255), count=20)
        
        logger.debug(f"Appear animation played for {getattr(monster, 'name', 'monster')}")
    
    def shake_camera(self, intensity: float = 1.0, duration: float = 0.5) -> None:
        """Shake camera with specified intensity and duration."""
        self.visual_effects.trigger_screen_shake(intensity, duration)
    
    def flash_screen(self, color=(255, 255, 255), duration: float = 0.3) -> None:
        """Flash screen with specified color and duration."""
        self.visual_effects.trigger_screen_flash(color, duration=duration)
    
    def trigger_screen_flash(self, color: Tuple[int, int, int] = (255, 255, 255), 
                           intensity: float = 0.8, duration: float = 0.3) -> None:
        """Trigger screen flash effect - ENHANCED VISUAL IMPACT."""
        self.visual_effects.trigger_screen_flash(color, intensity, duration)
        logger.debug(f"Screen flash triggered: color={color}, intensity={intensity}")
    
    def trigger_screen_shake(self, intensity: float = 5.0, duration: float = 0.3) -> None:
        """Trigger screen shake effect - ENHANCED IMPACT EFFECTS."""
        self.visual_effects.trigger_screen_shake(intensity, duration)
        logger.debug(f"Screen shake triggered: intensity={intensity}, duration={duration}")
    
    def update_hp_bar(self, target, animated=True):
        """Update HP Bar with Enhanced Animation System."""
        if not target:
            return
        
        # Get monster ID
        monster_id = getattr(target, 'id', id(target))
        
        # Add HP animation
        if animated:
            self.hp_animator.add_animation(monster_id, target.current_hp, target.max_hp)
        
        logger.debug(f"HP bar updated for {getattr(target, 'name', 'monster')}: {target.current_hp}/{target.max_hp}")
    
    def clear_all_animations(self) -> None:
        """Clear all animations."""
        self.hp_animator.clear_all_animations()
        self.damage_renderer.clear_all()
        self.visual_effects.clear_all_effects()
        logger.debug("All animations cleared")
