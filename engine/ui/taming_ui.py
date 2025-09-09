"""
Taming UI component for the battle system.
Shows meat selection and taming chance calculation with visual feedback.
"""

import pygame
import math
from typing import Optional, Dict, List, Tuple, Any
from dataclasses import dataclass
from enum import Enum

from engine.core.config import LOGICAL_WIDTH, LOGICAL_HEIGHT, Colors
from engine.ui.battle_ui_utils import fonts, colors, text_utils
from engine.systems.battle.meat_system import MeatType, MeatSystem


class TamingUIState(Enum):
    """States for the taming UI flow."""
    HIDDEN = 0
    MEAT_SELECT = 1      # Selecting which meat to use
    CHANCE_DISPLAY = 2   # Showing taming chance breakdown
    ATTEMPTING = 3       # Animation during taming attempt
    RESULT = 4          # Show success/failure


@dataclass
class TamingAnimation:
    """Animation data for taming attempt."""
    timer: float = 0.0
    shake_intensity: float = 0.0
    flash_count: int = 0
    ball_position: Tuple[int, int] = (0, 0)
    ball_shakes: int = 0
    success: bool = False


class TamingUI:
    """
    Complete taming UI system with meat selection and chance display.
    Follows DQM style with detailed breakdown of modifiers.
    """
    
    def __init__(self):
        """Initialize the taming UI."""
        self.state = TamingUIState.HIDDEN
        
        # Use centralized font manager
        self.font_large = fonts.large
        self.font_normal = fonts.normal
        self.font_small = fonts.small
        self.font_tiny = fonts.tiny
        
        # UI positioning
        self.meat_menu_pos = (LOGICAL_WIDTH // 2 - 100, 40)
        self.meat_menu_size = (200, 120)
        
        self.chance_display_pos = (LOGICAL_WIDTH // 2 - 110, 30)
        self.chance_display_size = (220, 140)
        
        # Selection state
        self.selected_meat_index = 0
        self.available_meat = []
        self.meat_system: Optional[MeatSystem] = None
        
        # Target monster info
        self.target_monster = None
        self.chance_data = None
        
        # Animation
        self.animation = TamingAnimation()
        
        # Colors
        self.color_bg = (40, 40, 60)
        self.color_border = (100, 150, 255)
        self.color_selected = (255, 255, 100)
        self.color_unselected = (200, 200, 200)
        self.color_disabled = (100, 100, 100)
        
    def init_taming(self, meat_system: MeatSystem, target_monster, battle_state=None):
        """
        Initialize taming UI for a taming attempt.
        
        Args:
            meat_system: The meat system instance
            target_monster: The monster to tame
            battle_state: Current battle state (optional)
        """
        self.meat_system = meat_system
        self.target_monster = target_monster
        self.state = TamingUIState.MEAT_SELECT
        self.selected_meat_index = 0
        
        # Get available meat
        self.available_meat = []
        meat_inventory = meat_system.get_available_meat()
        
        # Always add "no meat" option
        self.available_meat.append({
            'type': MeatType.NONE,
            'count': -1,
            'name': 'Kein Fleisch',
            'bonus': 0
        })
        
        # Add available meat types
        for meat_type, count in meat_inventory.items():
            if meat_type != MeatType.NONE and count > 0:
                self.available_meat.append({
                    'type': meat_type,
                    'count': count,
                    'name': meat_type.display_name,
                    'bonus': int(meat_type.bonus * 100)
                })
    
    def show_meat_selection(self):
        """Show the meat selection menu."""
        self.state = TamingUIState.MEAT_SELECT
    
    def show_taming_chance(self, base_chance: float = 0.15):
        """
        Show the taming chance calculation screen.
        
        Args:
            base_chance: Base taming chance
        """
        if not self.meat_system or not self.target_monster:
            return
        
        # Calculate taming chance
        hp_percent = self.target_monster.current_hp / max(1, self.target_monster.max_hp)
        
        # Get monster rank
        monster_rank = 'D'  # Default
        if hasattr(self.target_monster, 'rank'):
            monster_rank = self.target_monster.rank
        elif hasattr(self.target_monster, 'species') and hasattr(self.target_monster.species, 'rank'):
            monster_rank = self.target_monster.species.rank
        
        # Get monster status
        monster_status = None
        if hasattr(self.target_monster, 'status'):
            if hasattr(self.target_monster.status, 'value'):
                monster_status = self.target_monster.status.value
            elif isinstance(self.target_monster.status, str):
                monster_status = self.target_monster.status
        
        # Calculate chance with meat system
        self.chance_data = self.meat_system.calculate_taming_chance(
            base_chance=base_chance,
            monster_hp_percent=hp_percent,
            monster_rank=monster_rank,
            monster_status=monster_status
        )
        
        self.state = TamingUIState.CHANCE_DISPLAY
    
    def start_taming_animation(self, success: bool):
        """
        Start the taming attempt animation.
        
        Args:
            success: Whether the taming will succeed
        """
        self.state = TamingUIState.ATTEMPTING
        self.animation = TamingAnimation(
            timer=3.0,  # 3 seconds animation
            shake_intensity=5.0,
            flash_count=3,
            ball_position=(LOGICAL_WIDTH // 2, LOGICAL_HEIGHT // 2),
            ball_shakes=3 if not success else 0,
            success=success
        )
    
    def update(self, dt: float):
        """
        Update the taming UI animations.
        
        Args:
            dt: Delta time in seconds
        """
        if self.state == TamingUIState.ATTEMPTING:
            self.animation.timer -= dt
            
            if self.animation.timer <= 0:
                self.state = TamingUIState.RESULT
                self.animation.timer = 2.0  # Show result for 2 seconds
            else:
                # Update shake animation
                if self.animation.ball_shakes > 0:
                    shake_interval = 0.5
                    if int(self.animation.timer * 2) % 2 == 0:
                        self.animation.shake_intensity = 10.0
                    else:
                        self.animation.shake_intensity = 0.0
        
        elif self.state == TamingUIState.RESULT:
            self.animation.timer -= dt
            if self.animation.timer <= 0:
                self.state = TamingUIState.HIDDEN
    
    def draw(self, surface: pygame.Surface):
        """
        Draw the taming UI.
        
        Args:
            surface: Surface to draw on
        """
        if self.state == TamingUIState.HIDDEN:
            return
        
        if self.state == TamingUIState.MEAT_SELECT:
            self._draw_meat_selection(surface)
        elif self.state == TamingUIState.CHANCE_DISPLAY:
            self._draw_chance_display(surface)
        elif self.state == TamingUIState.ATTEMPTING:
            self._draw_taming_animation(surface)
        elif self.state == TamingUIState.RESULT:
            self._draw_result(surface)
    
    def _draw_meat_selection(self, surface: pygame.Surface):
        """Draw the meat selection menu."""
        x, y = self.meat_menu_pos
        w, h = self.meat_menu_size
        
        # Background
        pygame.draw.rect(surface, self.color_bg, (x, y, w, h))
        pygame.draw.rect(surface, self.color_border, (x, y, w, h), 2)
        
        # Title
        title = self.font_large.render("FLEISCH VORBEREITUNG", True, Colors.WHITE)
        title_rect = title.get_rect(centerx=x + w // 2, y=y + 5)
        surface.blit(title, title_rect)
        
        # Subtitle
        subtitle = self.font_tiny.render("Monster schmackhaft machen?", True, Colors.LIGHT_GRAY)
        subtitle_rect = subtitle.get_rect(centerx=x + w // 2, y=y + 22)
        surface.blit(subtitle, subtitle_rect)
        
        # Meat options
        option_y = y + 40
        for i, meat_data in enumerate(self.available_meat):
            # Highlight selected
            if i == self.selected_meat_index:
                select_rect = pygame.Rect(x + 10, option_y - 2, w - 20, 18)
                pygame.draw.rect(surface, (80, 80, 100), select_rect)
                pygame.draw.rect(surface, self.color_selected, select_rect, 1)
            
            # Meat name
            color = self.color_selected if i == self.selected_meat_index else self.color_unselected
            if meat_data['count'] == 0:
                color = self.color_disabled
            
            name_text = meat_data['name']
            if meat_data['count'] > 0:
                name_text = f"{meat_data['name']} x{meat_data['count']}"
            elif meat_data['count'] == -1:  # "No meat" option
                name_text = meat_data['name']
            
            text = self.font_normal.render(name_text, True, color)
            surface.blit(text, (x + 15, option_y))
            
            # Bonus display
            if meat_data['bonus'] > 0:
                bonus_text = f"[+{meat_data['bonus']}%]"
                bonus = self.font_small.render(bonus_text, True, (100, 255, 100))
                surface.blit(bonus, (x + w - 50, option_y))
            
            option_y += 20
        
        # Warning text
        warning1 = self.font_tiny.render("⚠️ Fleisch wirkt für ALLE Zähmversuche!", True, Colors.YELLOW)
        warning2 = self.font_tiny.render("⚠️ Gegner erhält Gratisangriff!", True, Colors.YELLOW)
        surface.blit(warning1, (x + 10, y + h - 25))
        surface.blit(warning2, (x + 10, y + h - 15))
    
    def _draw_chance_display(self, surface: pygame.Surface):
        """Draw the taming chance breakdown."""
        if not self.chance_data:
            return
        
        x, y = self.chance_display_pos
        w, h = self.chance_display_size
        
        # Background
        pygame.draw.rect(surface, self.color_bg, (x, y, w, h))
        pygame.draw.rect(surface, self.color_border, (x, y, w, h), 2)
        
        # Title
        title = self.font_large.render("ZÄHMVERSUCH!", True, Colors.WHITE)
        title_rect = title.get_rect(centerx=x + w // 2, y=y + 5)
        surface.blit(title, title_rect)
        
        # Monster name
        if self.target_monster:
            monster_text = f"Monster: {self.target_monster.name}"
            if hasattr(self.target_monster, 'rank'):
                monster_text += f" (Rang {self.target_monster.rank})"
            elif hasattr(self.target_monster, 'species') and hasattr(self.target_monster.species, 'rank'):
                monster_text += f" (Rang {self.target_monster.species.rank})"
            
            monster = self.font_normal.render(monster_text, True, Colors.WHITE)
            surface.blit(monster, (x + 10, y + 25))
        
        # Modifiers breakdown
        mod_y = y + 45
        modifiers = self.chance_data.get('modifiers', {})
        
        # Base chance
        base = modifiers.get('base', 0)
        self._draw_modifier_line(surface, x + 10, mod_y, "Basis-Chance:", f"{int(base * 100)}%", Colors.WHITE)
        mod_y += 15
        
        # HP bonus
        hp_bonus = modifiers.get('hp_bonus', 0)
        if hp_bonus > 0:
            hp_bar_width = 80
            hp_percent = 1.0 - hp_bonus / 0.3  # Reverse calculation
            self._draw_modifier_line(surface, x + 10, mod_y, "HP niedrig:", f"+{int(hp_bonus * 100)}%", Colors.GREEN)
            
            # Draw HP bar
            bar_x = x + 100
            bar_y = mod_y + 2
            pygame.draw.rect(surface, (50, 50, 50), (bar_x, bar_y, hp_bar_width, 8))
            current_width = int(hp_bar_width * hp_percent)
            hp_color = Colors.HP_LOW if hp_percent < 0.25 else Colors.HP_MED if hp_percent < 0.5 else Colors.HP_HIGH
            pygame.draw.rect(surface, hp_color, (bar_x, bar_y, current_width, 8))
            mod_y += 15
        
        # Meat bonus
        meat_bonus = modifiers.get('meat_bonus', 0)
        if meat_bonus > 0:
            meat_name = self.chance_data.get('meat_name', 'Fleisch')
            self._draw_modifier_line(surface, x + 10, mod_y, f"{meat_name}:", f"+{int(meat_bonus * 100)}%", Colors.GREEN)
            surface.blit(self.font_tiny.render("[AKTIV]", True, Colors.YELLOW), (x + 150, mod_y))
            mod_y += 15
        
        # Rank bonus
        rank_bonus = modifiers.get('rank_bonus', 0)
        if rank_bonus != 0:
            color = Colors.GREEN if rank_bonus > 0 else Colors.RED
            sign = "+" if rank_bonus > 0 else ""
            self._draw_modifier_line(surface, x + 10, mod_y, "Rang-Modifikator:", f"{sign}{int(rank_bonus * 100)}%", color)
            mod_y += 15
        
        # Status bonus
        status_bonus = modifiers.get('status_bonus', 0)
        if status_bonus > 0:
            self._draw_modifier_line(surface, x + 10, mod_y, "Status-Effekt:", f"+{int(status_bonus * 100)}%", Colors.GREEN)
            mod_y += 15
        
        # Draw separator
        pygame.draw.line(surface, Colors.LIGHT_GRAY, (x + 10, mod_y + 2), (x + w - 10, mod_y + 2))
        mod_y += 8
        
        # Final chance
        final_chance = self.chance_data.get('final_chance', 0)
        final_text = self.font_large.render(f"FINALE CHANCE: {int(final_chance * 100)}%", True, Colors.YELLOW)
        surface.blit(final_text, (x + 10, mod_y))
        
        # Chance bar
        bar_y = mod_y + 20
        bar_width = w - 20
        bar_height = 12
        pygame.draw.rect(surface, (50, 50, 50), (x + 10, bar_y, bar_width, bar_height))
        
        # Fill based on chance
        fill_width = int(bar_width * final_chance)
        if final_chance > 0.7:
            bar_color = Colors.GREEN
        elif final_chance > 0.4:
            bar_color = Colors.YELLOW
        else:
            bar_color = Colors.RED
        
        pygame.draw.rect(surface, bar_color, (x + 10, bar_y, fill_width, bar_height))
        
        # Percentage markers
        for pct in [0.25, 0.5, 0.75]:
            marker_x = x + 10 + int(bar_width * pct)
            pygame.draw.line(surface, Colors.WHITE, (marker_x, bar_y - 2), (marker_x, bar_y + bar_height + 2))
            pct_text = self.font_tiny.render(f"{int(pct * 100)}%", True, Colors.LIGHT_GRAY)
            surface.blit(pct_text, (marker_x - 10, bar_y + bar_height + 3))
    
    def _draw_modifier_line(self, surface: pygame.Surface, x: int, y: int, 
                           label: str, value: str, color: Tuple[int, int, int]):
        """Draw a modifier line in the chance display."""
        label_text = self.font_small.render(label, True, Colors.LIGHT_GRAY)
        value_text = self.font_small.render(value, True, color)
        surface.blit(label_text, (x, y))
        surface.blit(value_text, (x + 80, y))
    
    def _draw_taming_animation(self, surface: pygame.Surface):
        """Draw the taming attempt animation."""
        # Draw a simple animation (can be enhanced with actual graphics)
        cx, cy = LOGICAL_WIDTH // 2, LOGICAL_HEIGHT // 2
        
        # Background fade
        fade_surface = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT))
        fade_surface.set_alpha(128)
        fade_surface.fill((0, 0, 0))
        surface.blit(fade_surface, (0, 0))
        
        # Draw "pokeball" placeholder
        ball_color = Colors.RED if self.animation.timer > 1.5 else Colors.YELLOW
        shake_x = 0
        if self.animation.shake_intensity > 0:
            shake_x = int(math.sin(self.animation.timer * 20) * self.animation.shake_intensity)
        
        pygame.draw.circle(surface, ball_color, (cx + shake_x, cy), 20)
        pygame.draw.circle(surface, Colors.WHITE, (cx + shake_x, cy), 20, 3)
        
        # Draw text
        text = self.font_large.render("Zähme...", True, Colors.WHITE)
        text_rect = text.get_rect(centerx=cx, y=cy + 40)
        surface.blit(text, text_rect)
    
    def _draw_result(self, surface: pygame.Surface):
        """Draw the taming result."""
        cx, cy = LOGICAL_WIDTH // 2, LOGICAL_HEIGHT // 2
        
        # Background
        result_bg = (0, 100, 0) if self.animation.success else (100, 0, 0)
        pygame.draw.rect(surface, result_bg, (cx - 100, cy - 30, 200, 60))
        pygame.draw.rect(surface, Colors.WHITE, (cx - 100, cy - 30, 200, 60), 3)
        
        # Result text
        if self.animation.success:
            text = "ZÄHMUNG ERFOLGREICH!"
            color = Colors.GREEN
        else:
            text = "ZÄHMUNG FEHLGESCHLAGEN!"
            color = Colors.RED
        
        result_text = self.font_large.render(text, True, Colors.WHITE)
        result_rect = result_text.get_rect(centerx=cx, centery=cy)
        surface.blit(result_text, result_rect)
    
    def handle_input(self, action: str) -> Optional[Dict[str, Any]]:
        """
        Handle input for the taming UI.
        
        Args:
            action: Input action string
            
        Returns:
            Action dictionary or None
        """
        if self.state == TamingUIState.MEAT_SELECT:
            if action == 'up':
                self.selected_meat_index = max(0, self.selected_meat_index - 1)
            elif action == 'down':
                self.selected_meat_index = min(len(self.available_meat) - 1, self.selected_meat_index + 1)
            elif action == 'confirm':
                # Select meat and proceed
                selected = self.available_meat[self.selected_meat_index]
                if selected['count'] != 0:  # Has meat or is "no meat" option
                    self.show_taming_chance()
                    return {
                        'action': 'use_meat',
                        'meat_type': selected['type']
                    }
            elif action == 'back':
                self.state = TamingUIState.HIDDEN
                return {'action': 'cancel_taming'}
        
        elif self.state == TamingUIState.CHANCE_DISPLAY:
            if action == 'confirm':
                # Proceed with taming
                return {
                    'action': 'confirm_taming',
                    'final_chance': self.chance_data.get('final_chance', 0)
                }
            elif action == 'back':
                # Go back to meat selection
                self.state = TamingUIState.MEAT_SELECT
        
        return None
    
    def hide(self):
        """Hide the taming UI."""
        self.state = TamingUIState.HIDDEN
    
    def is_visible(self) -> bool:
        """Check if the taming UI is visible."""
        return self.state != TamingUIState.HIDDEN
