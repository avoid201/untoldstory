"""
Battle Rewards UI for displaying victory rewards.
Shows EXP gain, level ups, money, and item drops with animations.
"""

import pygame
import math
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum

from engine.core.config import LOGICAL_WIDTH, LOGICAL_HEIGHT, Colors
from engine.ui.battle_ui_utils import fonts, colors, text_utils


class RewardUIState(Enum):
    """States for the reward UI flow."""
    HIDDEN = 0
    VICTORY_MESSAGE = 1
    EXP_GAIN = 2
    LEVEL_UP = 3
    MONEY_GAIN = 4
    ITEM_DROPS = 5
    COMPLETE = 6


@dataclass
class RewardAnimation:
    """Animation data for rewards."""
    current_value: float = 0
    target_value: float = 0
    speed: float = 1.0
    timer: float = 0
    
    def update(self, dt: float) -> bool:
        """Update animation. Returns True when complete."""
        if self.current_value != self.target_value:
            diff = self.target_value - self.current_value
            change = diff * self.speed * dt
            
            # Snap to target if close enough
            if abs(diff) < 1:
                self.current_value = self.target_value
                return True
            else:
                self.current_value += change
                return False
        return True


class BattleRewardsUI:
    """
    UI for displaying battle rewards with animations.
    Shows EXP, level ups, money, and items gained.
    """
    
    def __init__(self):
        """Initialize the rewards UI."""
        self.state = RewardUIState.HIDDEN
        
        # Use centralized font manager
        self.font_huge = fonts.huge
        self.font_large = fonts.large
        self.font_normal = fonts.normal
        self.font_small = fonts.small
        
        # Rewards data
        self.rewards_data = None
        self.current_monster_index = 0
        self.monsters_to_show = []
        
        # Animations
        self.exp_animation = RewardAnimation()
        self.money_animation = RewardAnimation()
        self.fade_alpha = 0
        self.state_timer = 0
        
        # UI positioning
        self.box_pos = (LOGICAL_WIDTH // 2 - 120, 30)
        self.box_size = (240, 140)
        
        # Use centralized color manager
        self.color_bg = colors.colors['bg_light']
        self.color_border = colors.colors['border']
        self.color_victory = (255, 215, 0)  # Gold
        self.color_exp = colors.colors['text_green']
        self.color_money = colors.colors['text_yellow']
        self.color_item = colors.colors['text_blue']
    
    def show_rewards(self, rewards_data: Dict[str, Any]):
        """
        Start showing battle rewards.
        
        Args:
            rewards_data: Dictionary containing all reward information
        """
        self.rewards_data = rewards_data if rewards_data else {}
        self.state = RewardUIState.VICTORY_MESSAGE
        self.state_timer = 1.5  # Show victory message for 1.5 seconds
        self.fade_alpha = 0
        
        # Setup monster list for EXP display
        if rewards_data and 'exp_gained' in rewards_data and rewards_data['exp_gained']:
            self.monsters_to_show = list(rewards_data['exp_gained'].keys())
            self.current_monster_index = 0
        else:
            self.monsters_to_show = []
            self.current_monster_index = 0
        
        # Setup animations
        if rewards_data and 'money_gained' in rewards_data and rewards_data['money_gained'] > 0:
            self.money_animation.target_value = rewards_data['money_gained']
            self.money_animation.current_value = 0
            self.money_animation.speed = 3.0
        else:
            self.money_animation.target_value = 0
            self.money_animation.current_value = 0
    
    def update(self, dt: float) -> bool:
        """
        Update the rewards UI.
        
        Args:
            dt: Delta time in seconds
            
        Returns:
            True when all rewards have been shown
        """
        if self.state == RewardUIState.HIDDEN:
            return True
        
        # Fade in/out
        if self.state != RewardUIState.COMPLETE:
            if self.fade_alpha < 255:
                self.fade_alpha = min(255, self.fade_alpha + 500 * dt)
        else:
            if self.fade_alpha > 0:
                self.fade_alpha = max(0, self.fade_alpha - 500 * dt)
            else:
                self.state = RewardUIState.HIDDEN
                return True
        
        # State timer
        if self.state_timer > 0:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self._next_state()
        
        # Update animations
        if self.state == RewardUIState.EXP_GAIN:
            if self.exp_animation.update(dt):
                # Check for level up
                if self._check_level_up():
                    self.state = RewardUIState.LEVEL_UP
                    self.state_timer = 3.0
                else:
                    # Move to next monster or next state
                    if self._next_monster():
                        self.state_timer = 0.5
                    else:
                        self._next_state()
        
        elif self.state == RewardUIState.MONEY_GAIN:
            if self.money_animation.update(dt):
                self.state_timer = 1.5
        
        return False
    
    def _next_state(self):
        """Move to the next reward state."""
        if self.state == RewardUIState.VICTORY_MESSAGE:
            # Check if there's anything to show
            has_exp = self.monsters_to_show and len(self.monsters_to_show) > 0
            has_money = self.rewards_data and self.rewards_data.get('money_gained', 0) > 0
            has_items = self.rewards_data and self.rewards_data.get('items_gained') and len(self.rewards_data.get('items_gained')) > 0
            
            if has_exp:
                self.state = RewardUIState.EXP_GAIN
                self._setup_exp_animation()
            elif has_money:
                self.state = RewardUIState.MONEY_GAIN
            elif has_items:
                self.state = RewardUIState.ITEM_DROPS
                self.state_timer = 3.0
            else:
                # Nothing to show, go directly to complete
                self.state = RewardUIState.COMPLETE
                self.state_timer = 0.5  # Brief pause before allowing close
        
        elif self.state == RewardUIState.EXP_GAIN:
            if not self._next_monster():
                if self.rewards_data.get('money_gained', 0) > 0:
                    self.state = RewardUIState.MONEY_GAIN
                elif self.rewards_data.get('items_gained'):
                    self.state = RewardUIState.ITEM_DROPS
                    self.state_timer = 3.0
                else:
                    self.state = RewardUIState.COMPLETE
        
        elif self.state == RewardUIState.LEVEL_UP:
            # Return to EXP gain for next monster
            if self._next_monster():
                self.state = RewardUIState.EXP_GAIN
                self._setup_exp_animation()
            else:
                self._next_state()
        
        elif self.state == RewardUIState.MONEY_GAIN:
            if self.rewards_data.get('items_gained'):
                self.state = RewardUIState.ITEM_DROPS
                self.state_timer = 3.0
            else:
                self.state = RewardUIState.COMPLETE
                self.state_timer = 0.1  # Very brief pause before allowing input
        
        elif self.state == RewardUIState.ITEM_DROPS:
            self.state = RewardUIState.COMPLETE
        
        elif self.state == RewardUIState.COMPLETE:
            pass  # Will fade out
    
    def _setup_exp_animation(self):
        """Setup EXP animation for current monster."""
        if self.current_monster_index < len(self.monsters_to_show):
            monster = self.monsters_to_show[self.current_monster_index]
            exp_amount = self.rewards_data['exp_gained'].get(monster, 0)
            
            self.exp_animation.current_value = 0
            self.exp_animation.target_value = exp_amount
            self.exp_animation.speed = 3.0
    
    def _next_monster(self) -> bool:
        """Move to next monster. Returns True if there are more monsters."""
        self.current_monster_index += 1
        if self.current_monster_index < len(self.monsters_to_show):
            self._setup_exp_animation()
            return True
        return False
    
    def _check_level_up(self) -> bool:
        """Check if current monster leveled up."""
        if self.current_monster_index < len(self.monsters_to_show):
            monster = self.monsters_to_show[self.current_monster_index]
            if 'level_ups' in self.rewards_data:
                return monster in self.rewards_data['level_ups']
        return False
    
    def draw(self, surface: pygame.Surface):
        """Draw the rewards UI."""
        if self.state == RewardUIState.HIDDEN:
            return
        
        # Semi-transparent background
        overlay = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT))
        overlay.set_alpha(int(self.fade_alpha * 0.7))
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))
        
        x, y = self.box_pos
        w, h = self.box_size
        
        # Main box
        box_surface = pygame.Surface((w, h))
        box_surface.set_alpha(self.fade_alpha)
        pygame.draw.rect(box_surface, self.color_bg, (0, 0, w, h))
        pygame.draw.rect(box_surface, self.color_border, (0, 0, w, h), 2)
        
        # Draw content based on state
        if self.state == RewardUIState.VICTORY_MESSAGE:
            self._draw_victory_message(box_surface, w, h)
        elif self.state == RewardUIState.EXP_GAIN:
            self._draw_exp_gain(box_surface, w, h)
        elif self.state == RewardUIState.LEVEL_UP:
            self._draw_level_up(box_surface, w, h)
        elif self.state == RewardUIState.MONEY_GAIN:
            self._draw_money_gain(box_surface, w, h)
        elif self.state == RewardUIState.ITEM_DROPS:
            self._draw_item_drops(box_surface, w, h)
        elif self.state == RewardUIState.COMPLETE:
            self._draw_complete(box_surface, w, h)
        
        surface.blit(box_surface, (x, y))
    
    def _draw_victory_message(self, surface: pygame.Surface, w: int, h: int):
        """Draw victory message."""
        # Check for caught monster
        is_caught = False
        monster_name = ""
        if self.rewards_data:
            # Check if this was a caught battle
            if self.rewards_data.get('caught_monster'):
                is_caught = True
                monster_name = self.rewards_data.get('caught_monster_name', 'Monster')
        
        # Title
        if is_caught:
            title = self.font_huge.render("GEZÄHMT!", True, self.color_victory)
        else:
            title = self.font_huge.render("SIEG!", True, self.color_victory)
        title_rect = title.get_rect(centerx=w // 2, y=20)
        surface.blit(title, title_rect)
        
        # Subtitle
        if is_caught and monster_name:
            subtitle = self.font_normal.render(f"{monster_name} wurde gezähmt!", True, Colors.WHITE)
        else:
            subtitle = self.font_normal.render("Du hast gewonnen!", True, Colors.WHITE)
        subtitle_rect = subtitle.get_rect(centerx=w // 2, y=50)
        surface.blit(subtitle, subtitle_rect)
        
        # Victory animation (pulsing star)
        pulse = abs(math.sin(pygame.time.get_ticks() * 0.003))
        star_size = int(20 + pulse * 10)
        star_color = (255, int(215 + pulse * 40), 0)
        
        # Draw simple star
        cx, cy = w // 2, 90
        points = []
        for i in range(10):
            angle = math.pi * i / 5
            if i % 2 == 0:
                radius = star_size
            else:
                radius = star_size // 2
            x = cx + radius * math.cos(angle - math.pi / 2)
            y = cy + radius * math.sin(angle - math.pi / 2)
            points.append((x, y))
        
        if len(points) >= 3:
            pygame.draw.polygon(surface, star_color, points)
    
    def _draw_exp_gain(self, surface: pygame.Surface, w: int, h: int):
        """Draw EXP gain animation."""
        if self.current_monster_index >= len(self.monsters_to_show):
            return
        
        monster = self.monsters_to_show[self.current_monster_index]
        monster_name = monster.name if hasattr(monster, 'name') else 'Monster'
        
        # Title
        title = self.font_large.render(f"{monster_name}", True, Colors.WHITE)
        title_rect = title.get_rect(centerx=w // 2, y=15)
        surface.blit(title, title_rect)
        
        # EXP text
        exp_text = self.font_normal.render("erhält EXP:", True, Colors.LIGHT_GRAY)
        exp_rect = exp_text.get_rect(centerx=w // 2, y=40)
        surface.blit(exp_text, exp_rect)
        
        # Animated EXP value
        current_exp = int(self.exp_animation.current_value)
        exp_value = self.font_huge.render(f"+{current_exp}", True, self.color_exp)
        exp_value_rect = exp_value.get_rect(centerx=w // 2, y=60)
        surface.blit(exp_value, exp_value_rect)
        
        # EXP bar (simplified)
        bar_width = 180
        bar_height = 12
        bar_x = (w - bar_width) // 2
        bar_y = 95
        
        # Background
        pygame.draw.rect(surface, (40, 40, 40), (bar_x, bar_y, bar_width, bar_height))
        
        # Fill (animated)
        if self.exp_animation.target_value > 0:
            fill_percent = self.exp_animation.current_value / self.exp_animation.target_value
            fill_width = int(bar_width * fill_percent)
            pygame.draw.rect(surface, self.color_exp, (bar_x, bar_y, fill_width, bar_height))
        
        # Border
        pygame.draw.rect(surface, Colors.WHITE, (bar_x, bar_y, bar_width, bar_height), 1)
    
    def _draw_level_up(self, surface: pygame.Surface, w: int, h: int):
        """Draw level up screen."""
        if self.current_monster_index >= len(self.monsters_to_show):
            return
        
        monster = self.monsters_to_show[self.current_monster_index]
        monster_name = monster.name if hasattr(monster, 'name') else 'Monster'
        
        # Get level up data
        level_up_data = None
        if 'level_ups' in self.rewards_data:
            level_up_data = self.rewards_data['level_ups'].get(monster)
        
        if not level_up_data:
            return
        
        # Title with animation
        pulse = abs(math.sin(pygame.time.get_ticks() * 0.005))
        title_color = (255, int(200 + pulse * 55), int(100 + pulse * 155))
        title = self.font_large.render("LEVEL UP!", True, title_color)
        title_rect = title.get_rect(centerx=w // 2, y=10)
        surface.blit(title, title_rect)
        
        # Monster name and new level
        name_text = self.font_normal.render(f"{monster_name}", True, Colors.WHITE)
        name_rect = name_text.get_rect(centerx=w // 2, y=35)
        surface.blit(name_text, name_rect)
        
        level_text = self.font_large.render(f"Level {level_up_data.new_level}!", True, Colors.YELLOW)
        level_rect = level_text.get_rect(centerx=w // 2, y=55)
        surface.blit(level_text, level_rect)
        
        # Stat gains
        y_offset = 80
        for stat, gain in level_up_data.stat_gains.items():
            if gain > 0:
                stat_text = self.font_small.render(f"{stat.upper()} +{gain}", True, Colors.GREEN)
                surface.blit(stat_text, (w // 2 - 40, y_offset))
                y_offset += 15
        
        # New moves
        if level_up_data.new_moves:
            for move in level_up_data.new_moves[:2]:  # Show max 2 moves
                move_text = self.font_small.render(f"Neue Attacke: {move}!", True, Colors.CYAN)
                surface.blit(move_text, (w // 2 - 60, y_offset))
                y_offset += 15
    
    def _draw_money_gain(self, surface: pygame.Surface, w: int, h: int):
        """Draw money gain animation."""
        # Title
        title = self.font_large.render("Preisgeld erhalten!", True, Colors.WHITE)
        title_rect = title.get_rect(centerx=w // 2, y=20)
        surface.blit(title, title_rect)
        
        # Animated money value with coin icon
        current_money = int(self.money_animation.current_value)
        
        # Draw coin icon (simple circle)
        coin_x = w // 2 - 50
        coin_y = 55
        pygame.draw.circle(surface, self.color_money, (coin_x, coin_y), 8)
        pygame.draw.circle(surface, (200, 200, 100), (coin_x, coin_y), 8, 2)
        
        # Money amount
        money_text = self.font_huge.render(f"${current_money}", True, self.color_money)
        money_rect = money_text.get_rect(centerx=w // 2 + 10, y=45)
        surface.blit(money_text, money_rect)
        
        # Sparkle effect
        if self.money_animation.current_value > 0:
            sparkle_count = min(5, int(current_money / 100) + 1)
            for i in range(sparkle_count):
                angle = (pygame.time.get_ticks() * 0.002 + i * 1.256) % (2 * math.pi)
                sx = w // 2 + int(40 * math.cos(angle))
                sy = 80 + int(20 * math.sin(angle))
                pygame.draw.circle(surface, Colors.WHITE, (sx, sy), 2)
    
    def _draw_item_drops(self, surface: pygame.Surface, w: int, h: int):
        """Draw item drops."""
        # Title
        title = self.font_large.render("Items erhalten!", True, Colors.WHITE)
        title_rect = title.get_rect(centerx=w // 2, y=10)
        surface.blit(title, title_rect)
        
        # Draw items
        y_offset = 35
        if self.rewards_data and 'items_gained' in self.rewards_data:
            for item_id, quantity in self.rewards_data['items_gained'][:4]:  # Max 4 items
                # Item icon placeholder
                icon_rect = pygame.Rect(w // 2 - 60, y_offset, 16, 16)
                pygame.draw.rect(surface, self.color_item, icon_rect)
                pygame.draw.rect(surface, Colors.WHITE, icon_rect, 1)
                
                # Item name and quantity
                item_name = self._get_item_name(item_id)
                if quantity > 1:
                    item_text = self.font_small.render(f"{item_name} x{quantity}", True, Colors.WHITE)
                else:
                    item_text = self.font_small.render(f"{item_name}", True, Colors.WHITE)
                surface.blit(item_text, (w // 2 - 35, y_offset + 2))
                
                y_offset += 22
        
        # Treasure chest animation
        chest_y = 100
        chest_size = 20
        chest_x = w // 2 - chest_size // 2
        
        # Chest body
        pygame.draw.rect(surface, (139, 69, 19), (chest_x, chest_y, chest_size, chest_size // 2))
        
        # Chest lid (animated)
        lid_angle = abs(math.sin(pygame.time.get_ticks() * 0.003)) * 30
        lid_y = chest_y - int(lid_angle / 10)
        pygame.draw.rect(surface, (160, 82, 45), (chest_x, lid_y, chest_size, chest_size // 3))
    
    def _draw_complete(self, surface: pygame.Surface, w: int, h: int):
        """Draw completion message."""
        # Simple complete message
        text = self.font_normal.render("Weiter mit [ENTER]", True, Colors.LIGHT_GRAY)
        text_rect = text.get_rect(centerx=w // 2, centery=h // 2)
        surface.blit(text, text_rect)
    
    def _get_item_name(self, item_id: str) -> str:
        """Get display name for an item."""
        # Item name mapping
        item_names = {
            'fleisch': 'Fleisch',
            'edelfleisch': 'Edelfleisch',
            'götterfleisch': 'Götterfleisch',
            'trank': 'Trank',
            'supertrank': 'Supertrank',
            'hypertrank': 'Hypertrank',
            'äther': 'Äther',
            'elixier': 'Elixier',
            'gegengift': 'Gegengift',
            'brandsalbe': 'Brandsalbe',
            'kräuter': 'Kräuter',
            'hide': 'Fell',
            'fang': 'Reißzahn',
            'scale': 'Schuppe',
            'claw': 'Klaue',
            'bone': 'Knochen',
            'ore': 'Erz',
            'crystal': 'Kristall',
            'gem': 'Edelstein',
            'seed': 'Samen',
            'leaf': 'Blatt',
            'rare_candy': 'Seltene Süßigkeit'
        }
        
        return item_names.get(item_id, item_id.replace('_', ' ').title())
    
    def handle_input(self, action: str) -> bool:
        """
        Handle input for the rewards UI.
        
        Args:
            action: Input action
            
        Returns:
            True if input was handled
        """
        if self.state == RewardUIState.HIDDEN:
            return False
        
        # Skip current animation/state with confirm
        if action == 'confirm' or action == 'escape':
            # Debug removed - use logging system for debugging
            
            if self.state == RewardUIState.VICTORY_MESSAGE:
                self.state_timer = 0
                # Force immediate state transition
                self._next_state()
            elif self.state == RewardUIState.EXP_GAIN:
                self.exp_animation.current_value = self.exp_animation.target_value
            elif self.state == RewardUIState.MONEY_GAIN:
                self.money_animation.current_value = self.money_animation.target_value
                self.state_timer = 0
                self._next_state()
            elif self.state in [RewardUIState.LEVEL_UP, RewardUIState.ITEM_DROPS]:
                self.state_timer = 0
                self._next_state()
            elif self.state == RewardUIState.COMPLETE:
                # Debug removed - use logging system for debugging
                self.fade_alpha = 0
                self.state = RewardUIState.HIDDEN
            return True
        
        return False
    
    def is_complete(self) -> bool:
        """Check if rewards display is complete."""
        return self.state == RewardUIState.HIDDEN
