"""
Menu system for inventory, party management, quests, and more.
CLEANED VERSION - Legacy duplicate menus removed.
"""

import pygame
from typing import TYPE_CHECKING, Optional, List, Dict, Any, Callable
from dataclasses import dataclass
from enum import Enum, auto
from abc import ABC, abstractmethod

# Import centralized font manager
from engine.ui.battle_ui_utils import fonts

if TYPE_CHECKING:
    from engine.core.game import Game
    from engine.systems.monster_instance import MonsterInstance
    from engine.systems.items import Item
    from engine.systems.quests import Quest


class MenuBase(ABC):
    """Base class for all menus."""
    
    def __init__(self, game: 'Game'):
        """Initialize menu base."""
        self.game = game
        # Use centralized font manager instead of creating new fonts
        self.font = fonts.normal
        self.small_font = fonts.small
        self.selected_index = 0
        self.scroll_offset = 0
        self.items_per_page = 8
        
        # Use centralized color manager instead of hardcoded colors
        from engine.ui.battle_ui_utils import colors
        self.bg_color = colors.get_color('bg_dark')
        self.border_color = colors.get_color('border')
        self.selected_color = colors.get_color('text_white')
        self.unselected_color = colors.get_color('text_gray')
        self.disabled_color = (80, 80, 80)  # Keep this as it's not in the color manager
        
        # Window dimensions
        self.window_x = 20
        self.window_y = 20
        self.window_width = 280
        self.window_height = 140
    
    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle input event."""
        pass
    
    @abstractmethod
    def update(self, dt: float) -> None:
        """Update menu."""
        pass
    
    @abstractmethod
    def draw(self, surface: pygame.Surface) -> None:
        """Draw menu."""
        pass
    
    def draw_window(self, surface: pygame.Surface, x: int, y: int, 
                   width: int, height: int, title: Optional[str] = None) -> None:
        """Draw a window with border and optional title."""
        # Background
        pygame.draw.rect(surface, self.bg_color, (x, y, width, height))
        
        # Border
        pygame.draw.rect(surface, self.border_color, (x, y, width, height), 2)
        
        # Title
        if title:
            title_surf = self.font.render(title, True, self.selected_color)
            surface.blit(title_surf, (x + 10, y + 5))
            
            # Title underline
            pygame.draw.line(surface, self.border_color,
                           (x + 10, y + 22), (x + width - 10, y + 22), 1)


# LEGACY: InventoryMenu removed - Use EnhancedInventoryMenu from enhanced_menus.py instead
# LEGACY: PartyMenu removed - Use EnhancedPartyMenu from enhanced_menus.py instead


class QuestMenu(MenuBase):
    """Quest log menu."""
    
    def __init__(self, game: 'Game'):
        """Initialize quest menu."""
        super().__init__(game)
        self.quests = game.quest_manager.quests if hasattr(game, 'quest_manager') else []
        self.selected_quest = 0
        self.show_details = False
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle input events."""
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_w, pygame.K_UP]:
                if self.selected_quest > 0:
                    self.selected_quest -= 1
                return True
                
            elif event.key in [pygame.K_s, pygame.K_DOWN]:
                if self.selected_quest < len(self.quests) - 1:
                    self.selected_quest += 1
                return True
                
            elif event.key in [pygame.K_e, pygame.K_RETURN, pygame.K_SPACE]:
                self.show_details = not self.show_details
                return True
                
            elif event.key in [pygame.K_q, pygame.K_ESCAPE]:
                return False
                
        return False
    
    def update(self, dt: float) -> None:
        """Update quest menu."""
        pass
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw quest menu."""
        # Draw window
        self.draw_window(surface, self.window_x, self.window_y, 
                        self.window_width, self.window_height, "Quests")
        
        if not self.quests:
            no_quests = self.font.render("Keine aktiven Quests", True, self.disabled_color)
            surface.blit(no_quests, (self.window_x + 10, self.window_y + 30))
            return
        
        # Draw quest list
        start_y = self.window_y + 30
        for i, quest in enumerate(self.quests):
            y = start_y + i * 15
            
            if i == self.selected_quest:
                color = self.selected_color
            else:
                color = self.unselected_color
            
            # Quest name
            quest_text = quest.name if hasattr(quest, 'name') else f"Quest {i+1}"
            text_surf = self.font.render(quest_text, True, color)
            surface.blit(text_surf, (self.window_x + 10, y))
            
            # Quest status
            if hasattr(quest, 'completed') and quest.completed:
                status_text = "✓"
                status_color = (0, 255, 0)
            else:
                status_text = "○"
                status_color = (255, 255, 0)
            
            status_surf = self.font.render(status_text, True, status_color)
            surface.blit(status_surf, (self.window_x + self.window_width - 20, y))
        
        # Instructions
        inst_text = "E: Details | ESC: Zurück"
        inst_surf = self.small_font.render(inst_text, True, (200, 200, 200))
        surface.blit(inst_surf, (self.window_x + 10, self.window_y + self.window_height - 15))


class SaveMenu(MenuBase):
    """Save/Load menu."""
    
    def __init__(self, game: 'Game'):
        """Initialize save menu."""
        super().__init__(game)
        self.save_slots = 3
        self.selected_slot = 0
        self.mode = 'save'  # 'save' or 'load'
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle input events."""
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_w, pygame.K_UP]:
                if self.selected_slot > 0:
                    self.selected_slot -= 1
                return True
                
            elif event.key in [pygame.K_s, pygame.K_DOWN]:
                if self.selected_slot < self.save_slots - 1:
                    self.selected_slot += 1
                return True
                
            elif event.key in [pygame.K_e, pygame.K_RETURN, pygame.K_SPACE]:
                # Perform save/load
                if self.mode == 'save':
                    self.game.save_game(f"save_{self.selected_slot + 1}.sav")
                else:
                    self.game.load_game(f"save_{self.selected_slot + 1}.sav")
                return False
                
            elif event.key in [pygame.K_q, pygame.K_ESCAPE]:
                return False
                
        return False
    
    def update(self, dt: float) -> None:
        """Update save menu."""
        pass
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw save menu."""
        title = "Speichern" if self.mode == 'save' else "Laden"
        self.draw_window(surface, self.window_x, self.window_y, 
                        self.window_width, self.window_height, title)
        
        # Draw save slots
        start_y = self.window_y + 30
        for i in range(self.save_slots):
            y = start_y + i * 20
            
            if i == self.selected_slot:
                color = self.selected_color
            else:
                color = self.unselected_color
            
            slot_text = f"Slot {i + 1}"
            text_surf = self.font.render(slot_text, True, color)
            surface.blit(text_surf, (self.window_x + 10, y))
            
            # Check if save exists
            save_file = f"save_{i + 1}.sav"
            if hasattr(self.game, 'save_system') and self.game.save_system.save_exists(save_file):
                exists_text = "✓"
                exists_color = (0, 255, 0)
            else:
                exists_text = "○"
                exists_color = (100, 100, 100)
            
            exists_surf = self.font.render(exists_text, True, exists_color)
            surface.blit(exists_surf, (self.window_x + self.window_width - 20, y))
        
        # Instructions
        inst_text = "E: Bestätigen | ESC: Zurück"
        inst_surf = self.small_font.render(inst_text, True, (200, 200, 200))
        surface.blit(inst_surf, (self.window_x + 10, self.window_y + self.window_height - 15))


class ConfirmDialog(MenuBase):
    """Confirmation dialog."""
    
    def __init__(self, game: 'Game', message: str, callback: Callable[[bool], None]):
        """Initialize confirmation dialog."""
        super().__init__(game)
        self.message = message
        self.callback = callback
        self.selected_option = 0  # 0 = Yes, 1 = No
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle input events."""
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_a, pygame.K_LEFT]:
                self.selected_option = 0
                return True
                
            elif event.key in [pygame.K_d, pygame.K_RIGHT]:
                self.selected_option = 1
                return True
                
            elif event.key in [pygame.K_e, pygame.K_RETURN, pygame.K_SPACE]:
                self.callback(self.selected_option == 0)
                return False
                
            elif event.key in [pygame.K_q, pygame.K_ESCAPE]:
                self.callback(False)
                return False
                
        return False
    
    def update(self, dt: float) -> None:
        """Update dialog."""
        pass
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw dialog."""
        # Draw window
        self.draw_window(surface, self.window_x, self.window_y, 
                        self.window_width, self.window_height, "Bestätigung")
        
        # Draw message
        message_surf = self.font.render(self.message, True, self.selected_color)
        surface.blit(message_surf, (self.window_x + 10, self.window_y + 30))
        
        # Draw options
        yes_x = self.window_x + 50
        no_x = self.window_x + 150
        option_y = self.window_y + 60
        
        yes_color = self.selected_color if self.selected_option == 0 else self.unselected_color
        no_color = self.selected_color if self.selected_option == 1 else self.unselected_color
        
        yes_surf = self.font.render("Ja", True, yes_color)
        no_surf = self.font.render("Nein", True, no_color)
        
        surface.blit(yes_surf, (yes_x, option_y))
        surface.blit(no_surf, (no_x, option_y))
        
        # Instructions
        inst_text = "A/D: Wählen | E: Bestätigen | ESC: Abbrechen"
        inst_surf = self.small_font.render(inst_text, True, (200, 200, 200))
        surface.blit(inst_surf, (self.window_x + 10, self.window_y + self.window_height - 15))
