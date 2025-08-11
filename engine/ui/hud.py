"""
HUD (Heads-Up Display) overlays for field and battle scenes.
"""

import pygame
from typing import TYPE_CHECKING, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum, auto

if TYPE_CHECKING:
    from engine.core.game import Game
    from engine.systems.monster_instance import MonsterInstance


class NotificationType(Enum):
    """Types of HUD notifications."""
    INFO = auto()
    SUCCESS = auto()
    WARNING = auto()
    ERROR = auto()
    QUEST = auto()
    ITEM = auto()
    LEVEL_UP = auto()


@dataclass
class Notification:
    """A HUD notification."""
    text: str
    notification_type: NotificationType
    duration: float
    position: Tuple[int, int]
    font_size: int = 14
    fade_time: float = 0.5
    current_time: float = 0.0
    alpha: int = 255


class FieldHUD:
    """HUD for the field/overworld."""
    
    def __init__(self, game: 'Game'):
        """Initialize field HUD."""
        self.game = game
        self.font = pygame.font.Font(None, 14)
        self.small_font = pygame.font.Font(None, 12)
        self.large_font = pygame.font.Font(None, 18)
        
        # HUD visibility
        self.show_location = True
        self.show_minimap = False
        self.show_party_status = False
        self.show_quest_tracker = False
        
        # Location display
        self.location_name = ""
        self.location_timer = 0.0
        self.location_fade_duration = 3.0
        
        # Notifications
        self.notifications: List[Notification] = []
        
        # Colors
        self.bg_color = (20, 20, 30, 200)
        self.border_color = (100, 100, 120)
        self.text_color = (255, 255, 255)
        
    def set_location(self, location_name: str) -> None:
        """Set and display location name."""
        self.location_name = location_name
        self.location_timer = self.location_fade_duration
    
    def add_notification(self, text: str, 
                        notification_type: NotificationType = NotificationType.INFO,
                        duration: float = 3.0) -> None:
        """Add a notification to display."""
        # Position notifications vertically
        y_offset = 100 + len(self.notifications) * 20
        
        notification = Notification(
            text=text,
            notification_type=notification_type,
            duration=duration,
            position=(10, y_offset)
        )
        self.notifications.append(notification)
    
    def update(self, dt: float) -> None:
        """Update HUD elements."""
        # Update location timer
        if self.location_timer > 0:
            self.location_timer -= dt
        
        # Update notifications
        for notification in self.notifications[:]:
            notification.current_time += dt
            
            # Calculate alpha for fade
            if notification.current_time < notification.fade_time:
                # Fade in
                notification.alpha = int(255 * (notification.current_time / notification.fade_time))
            elif notification.current_time > notification.duration - notification.fade_time:
                # Fade out
                remaining = notification.duration - notification.current_time
                notification.alpha = int(255 * (remaining / notification.fade_time))
            else:
                notification.alpha = 255
            
            # Remove expired notifications
            if notification.current_time >= notification.duration:
                self.notifications.remove(notification)
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw HUD elements."""
        # Location name
        if self.location_timer > 0 and self.location_name:
            self._draw_location(surface)
        
        # Party status bar
        if self.show_party_status:
            self._draw_party_status(surface)
        
        # Quest tracker
        if self.show_quest_tracker:
            self._draw_quest_tracker(surface)
        
        # Minimap
        if self.show_minimap:
            self._draw_minimap(surface)
        
        # Notifications
        for notification in self.notifications:
            self._draw_notification(surface, notification)
    
    def _draw_location(self, surface: pygame.Surface) -> None:
        """Draw location name display."""
        # Calculate alpha based on timer
        if self.location_timer > self.location_fade_duration - 0.5:
            # Fade in
            alpha = int(255 * ((self.location_fade_duration - self.location_timer) / 0.5))
        elif self.location_timer < 0.5:
            # Fade out
            alpha = int(255 * (self.location_timer / 0.5))
        else:
            alpha = 255
        
        # Create text surface
        text_surf = self.large_font.render(self.location_name, True, self.text_color)
        text_surf.set_alpha(alpha)
        
        # Position at top center
        text_rect = text_surf.get_rect(center=(self.game.logical_width // 2, 30))
        
        # Draw background
        bg_surf = pygame.Surface((text_rect.width + 40, text_rect.height + 10))
        bg_surf.fill((20, 20, 30))
        bg_surf.set_alpha(alpha * 0.7)
        bg_rect = bg_surf.get_rect(center=(self.game.logical_width // 2, 30))
        surface.blit(bg_surf, bg_rect)
        
        # Draw text
        surface.blit(text_surf, text_rect)
    
    def _draw_party_status(self, surface: pygame.Surface) -> None:
        """Draw party status bar."""
        if not hasattr(self.game, 'party_manager'):
            return
        
        party = self.game.party_manager.party
        members = party.get_all_members()
        
        if not members:
            return
        
        # Position at top right
        x = self.game.logical_width - 80
        y = 5
        
        # Background
        bg_rect = pygame.Rect(x - 5, y - 2, 75, 15 * len(members) + 4)
        bg_surf = pygame.Surface((bg_rect.width, bg_rect.height))
        bg_surf.fill((20, 20, 30))
        bg_surf.set_alpha(200)
        surface.blit(bg_surf, bg_rect)
        
        # Draw each party member
        for i, monster in enumerate(members):
            # Name
            name = (monster.nickname or monster.species.name)[:8]
            name_surf = self.small_font.render(name, True, self.text_color)
            surface.blit(name_surf, (x, y + i * 15))
            
            # HP bar
            bar_x = x + 40
            bar_y = y + i * 15 + 3
            bar_width = 30
            bar_height = 8
            
            # Background
            pygame.draw.rect(surface, (40, 40, 40),
                           (bar_x, bar_y, bar_width, bar_height))
            
            # Fill
            hp_percent = monster.current_hp / monster.max_hp
            fill_width = int(bar_width * hp_percent)
            
            if hp_percent > 0.5:
                color = (0, 200, 0)
            elif hp_percent > 0.25:
                color = (200, 200, 0)
            else:
                color = (200, 0, 0)
            
            if fill_width > 0:
                pygame.draw.rect(surface, color,
                               (bar_x, bar_y, fill_width, bar_height))
    
    def _draw_quest_tracker(self, surface: pygame.Surface) -> None:
        """Draw active quest tracker."""
        if not hasattr(self.game, 'quest_manager'):
            return
        
        active_quests = self.game.quest_manager.get_active_quests()
        if not active_quests:
            return
        
        # Show first active quest
        quest = active_quests[0]
        
        # Position at top left
        x = 10
        y = 50
        
        # Background
        objectives = quest.get_active_objectives()[:3]  # Max 3 objectives
        height = 30 + len(objectives) * 12
        
        bg_rect = pygame.Rect(x - 5, y - 5, 150, height)
        bg_surf = pygame.Surface((bg_rect.width, bg_rect.height))
        bg_surf.fill((20, 20, 30))
        bg_surf.set_alpha(200)
        surface.blit(bg_surf, bg_rect)
        
        # Quest name
        name_surf = self.font.render(quest.name[:20], True, (255, 215, 0))
        surface.blit(name_surf, (x, y))
        
        y += 15
        
        # Objectives
        for obj in objectives:
            # Checkbox
            check = "☑" if obj.is_complete() else "☐"
            check_surf = self.small_font.render(check, True,
                                               (0, 200, 0) if obj.is_complete() else self.text_color)
            surface.blit(check_surf, (x, y))
            
            # Objective text
            text = obj.description[:18]
            text_surf = self.small_font.render(text, True, (150, 150, 150))
            surface.blit(text_surf, (x + 15, y))
            
            y += 12
    
    def _draw_minimap(self, surface: pygame.Surface) -> None:
        """Draw minimap."""
        # Position at bottom right
        size = 60
        x = self.game.logical_width - size - 5
        y = self.game.logical_height - size - 5
        
        # Background
        minimap_rect = pygame.Rect(x, y, size, size)
        pygame.draw.rect(surface, (20, 20, 30), minimap_rect)
        pygame.draw.rect(surface, self.border_color, minimap_rect, 1)
        
        # TODO: Actually draw map data
        # For now, just show player position indicator
        center_x = x + size // 2
        center_y = y + size // 2
        pygame.draw.circle(surface, (255, 255, 0), (center_x, center_y), 2)
    
    def _draw_notification(self, surface: pygame.Surface, notification: Notification) -> None:
        """Draw a notification."""
        # Notification colors by type
        type_colors = {
            NotificationType.INFO: (255, 255, 255),
            NotificationType.SUCCESS: (0, 255, 0),
            NotificationType.WARNING: (255, 200, 0),
            NotificationType.ERROR: (255, 0, 0),
            NotificationType.QUEST: (255, 215, 0),
            NotificationType.ITEM: (100, 200, 255),
            NotificationType.LEVEL_UP: (255, 100, 255)
        }
        
        color = type_colors.get(notification.notification_type, (255, 255, 255))
        
        # Create text surface
        font = pygame.font.Font(None, notification.font_size)
        text_surf = font.render(notification.text, True, color)
        text_surf.set_alpha(notification.alpha)
        
        # Draw with background
        text_rect = text_surf.get_rect(topleft=notification.position)
        
        bg_surf = pygame.Surface((text_rect.width + 10, text_rect.height + 4))
        bg_surf.fill((20, 20, 30))
        bg_surf.set_alpha(notification.alpha * 0.7)
        bg_rect = bg_surf.get_rect(center=text_rect.center)
        
        surface.blit(bg_surf, bg_rect)
        surface.blit(text_surf, text_rect)


class BattleHUD:
    """HUD for battle scenes."""
    
    def __init__(self, game: 'Game'):
        """Initialize battle HUD."""
        self.game = game
        self.font = pygame.font.Font(None, 14)
        self.small_font = pygame.font.Font(None, 12)
        
        # Turn indicator
        self.current_turn = 0
        self.show_turn_order = False
        
        # Damage numbers
        self.damage_numbers: List[DamageNumber] = []
        
        # Status messages
        self.status_messages: List[str] = []
        self.message_timer = 0.0
        
    def add_damage_number(self, value: int, position: Tuple[int, int],
                         is_heal: bool = False, is_critical: bool = False) -> None:
        """Add a floating damage number."""
        damage_num = DamageNumber(
            value=value,
            position=position,
            is_heal=is_heal,
            is_critical=is_critical
        )
        self.damage_numbers.append(damage_num)
    
    def add_status_message(self, message: str) -> None:
        """Add a status message."""
        self.status_messages.append(message)
        self.message_timer = 2.0
    
    def update(self, dt: float) -> None:
        """Update HUD elements."""
        # Update damage numbers
        for damage_num in self.damage_numbers[:]:
            damage_num.update(dt)
            if damage_num.expired:
                self.damage_numbers.remove(damage_num)
        
        # Update message timer
        if self.message_timer > 0:
            self.message_timer -= dt
            if self.message_timer <= 0:
                self.status_messages.clear()
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw battle HUD elements."""
        # Turn counter
        self._draw_turn_counter(surface)
        
        # Turn order preview
        if self.show_turn_order:
            self._draw_turn_order(surface)
        
        # Damage numbers
        for damage_num in self.damage_numbers:
            damage_num.draw(surface, self.font)
        
        # Status messages
        if self.status_messages:
            self._draw_status_messages(surface)
    
    def _draw_turn_counter(self, surface: pygame.Surface) -> None:
        """Draw turn counter."""
        text = f"Runde {self.current_turn}"
        text_surf = self.font.render(text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(topleft=(5, 5))
        
        # Background
        bg_surf = pygame.Surface((text_rect.width + 10, text_rect.height + 4))
        bg_surf.fill((20, 20, 30))
        bg_surf.set_alpha(200)
        surface.blit(bg_surf, (text_rect.x - 5, text_rect.y - 2))
        
        surface.blit(text_surf, text_rect)
    
    def _draw_turn_order(self, surface: pygame.Surface) -> None:
        """Draw turn order preview."""
        # TODO: Get actual turn order from battle system
        pass
    
    def _draw_status_messages(self, surface: pygame.Surface) -> None:
        """Draw status messages."""
        y = 40
        for message in self.status_messages[-3:]:  # Show last 3 messages
            text_surf = self.small_font.render(message, True, (255, 255, 200))
            text_rect = text_surf.get_rect(center=(self.game.logical_width // 2, y))
            
            # Background
            bg_surf = pygame.Surface((text_rect.width + 20, text_rect.height + 4))
            bg_surf.fill((20, 20, 30))
            bg_surf.set_alpha(200)
            bg_rect = bg_surf.get_rect(center=text_rect.center)
            surface.blit(bg_surf, bg_rect)
            
            surface.blit(text_surf, text_rect)
            y += 20


@dataclass
class DamageNumber:
    """Floating damage number display."""
    value: int
    position: Tuple[int, int]
    is_heal: bool = False
    is_critical: bool = False
    velocity_y: float = -2.0
    lifetime: float = 1.5
    current_time: float = 0.0
    expired: bool = False
    
    def update(self, dt: float) -> None:
        """Update damage number animation."""
        self.current_time += dt
        
        # Move upward
        self.position = (self.position[0], 
                        self.position[1] + self.velocity_y)
        
        # Slow down
        self.velocity_y *= 0.95
        
        # Check expiration
        if self.current_time >= self.lifetime:
            self.expired = True
    
    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        """Draw damage number."""
        # Determine color
        if self.is_heal:
            color = (0, 255, 0)
        elif self.is_critical:
            color = (255, 255, 0)
        else:
            color = (255, 255, 255)
        
        # Calculate alpha
        if self.current_time > self.lifetime - 0.5:
            alpha = int(255 * ((self.lifetime - self.current_time) / 0.5))
        else:
            alpha = 255
        
        # Format text
        if self.is_critical:
            text = f"{self.value}!"
        else:
            text = str(self.value)
        
        # Render
        text_surf = font.render(text, True, color)
        text_surf.set_alpha(alpha)
        
        # Position
        text_rect = text_surf.get_rect(center=self.position)
        surface.blit(text_surf, text_rect)