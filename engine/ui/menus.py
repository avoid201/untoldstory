"""
Menu system for inventory, party management, quests, and more.
"""

import pygame
from typing import TYPE_CHECKING, Optional, List, Dict, Any, Callable
from dataclasses import dataclass
from enum import Enum, auto
from abc import ABC, abstractmethod

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
        self.font = pygame.font.Font(None, 14)
        self.small_font = pygame.font.Font(None, 12)
        self.selected_index = 0
        self.scroll_offset = 0
        self.items_per_page = 8
        
        # Colors
        self.bg_color = (20, 20, 30)
        self.border_color = (100, 100, 120)
        self.selected_color = (255, 255, 255)
        self.unselected_color = (150, 150, 150)
        self.disabled_color = (80, 80, 80)
        
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
        """Draw a window frame."""
        # Background
        window_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(surface, self.bg_color, window_rect)
        pygame.draw.rect(surface, self.border_color, window_rect, 2)
        
        # Title
        if title:
            title_surf = self.font.render(title, True, self.selected_color)
            title_rect = title_surf.get_rect(center=(x + width // 2, y + 12))
            surface.blit(title_surf, title_rect)
            
            # Title separator
            pygame.draw.line(surface, self.border_color,
                           (x + 10, y + 22), (x + width - 10, y + 22), 1)


class InventoryMenu(MenuBase):
    """Inventory management menu."""
    
    def __init__(self, game: 'Game'):
        """Initialize inventory menu."""
        super().__init__(game)
        self.inventory = game.inventory if hasattr(game, 'inventory') else None
        self.item_db = game.item_database if hasattr(game, 'item_database') else None
        self.items_list = []
        self.selected_item = None
        self.show_description = False
        self._refresh_items()
    
    def _refresh_items(self) -> None:
        """Refresh the items list."""
        if not self.inventory:
            return
        
        self.items_list = []
        for item_id, quantity in self.inventory.get_all_items():
            if self.item_db:
                item = self.item_db.get_item(item_id)
                if item:
                    self.items_list.append((item, quantity))
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle input events."""
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_w, pygame.K_UP]:
                if self.selected_index > 0:
                    self.selected_index -= 1
                    if self.selected_index < self.scroll_offset:
                        self.scroll_offset = self.selected_index
                return True
                
            elif event.key in [pygame.K_s, pygame.K_DOWN]:
                if self.selected_index < len(self.items_list) - 1:
                    self.selected_index += 1
                    if self.selected_index >= self.scroll_offset + self.items_per_page:
                        self.scroll_offset = self.selected_index - self.items_per_page + 1
                return True
                
            elif event.key in [pygame.K_e, pygame.K_RETURN, pygame.K_SPACE]:
                if self.items_list:
                    self.selected_item = self.items_list[self.selected_index]
                    self.show_description = not self.show_description
                return True
                
            elif event.key in [pygame.K_q, pygame.K_ESCAPE]:
                return False  # Let parent handle
                
        return False
    
    def update(self, dt: float) -> None:
        """Update inventory menu."""
        pass
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw inventory menu."""
        # Main window
        self.draw_window(surface, self.window_x, self.window_y,
                        self.window_width, self.window_height, "Inventar")
        
        if not self.items_list:
            # Empty inventory
            text = "Keine Items vorhanden"
            text_surf = self.font.render(text, True, self.disabled_color)
            text_rect = text_surf.get_rect(center=(self.window_x + self.window_width // 2,
                                                   self.window_y + self.window_height // 2))
            surface.blit(text_surf, text_rect)
            return
        
        # Item list
        y_offset = self.window_y + 30
        visible_items = self.items_list[self.scroll_offset:self.scroll_offset + self.items_per_page]
        
        for i, (item, quantity) in enumerate(visible_items):
            actual_index = self.scroll_offset + i
            is_selected = actual_index == self.selected_index
            
            # Selection highlight
            if is_selected:
                select_rect = pygame.Rect(self.window_x + 5, y_offset - 2,
                                         self.window_width - 10, 14)
                pygame.draw.rect(surface, (40, 40, 60), select_rect)
            
            # Item name and quantity
            text = f"{item.name} x{quantity}"
            color = self.selected_color if is_selected else self.unselected_color
            text_surf = self.small_font.render(text, True, color)
            surface.blit(text_surf, (self.window_x + 10, y_offset))
            
            y_offset += 14
        
        # Scroll indicator
        if len(self.items_list) > self.items_per_page:
            scroll_text = f"↑↓ {self.scroll_offset + 1}-{min(self.scroll_offset + self.items_per_page, len(self.items_list))}/{len(self.items_list)}"
            scroll_surf = self.small_font.render(scroll_text, True, self.disabled_color)
            surface.blit(scroll_surf, (self.window_x + self.window_width - 50,
                                      self.window_y + self.window_height - 15))
        
        # Item description window
        if self.show_description and self.selected_item:
            self._draw_item_description(surface, self.selected_item[0])
    
    def _draw_item_description(self, surface: pygame.Surface, item: 'Item') -> None:
        """Draw item description window."""
        desc_x = self.window_x
        desc_y = self.window_y + self.window_height + 5
        desc_width = self.window_width
        desc_height = 40
        
        self.draw_window(surface, desc_x, desc_y, desc_width, desc_height)
        
        # Item description
        desc_lines = self._wrap_text(item.description, desc_width - 20)
        y_offset = desc_y + 5
        
        for line in desc_lines[:2]:  # Max 2 lines
            line_surf = self.small_font.render(line, True, self.unselected_color)
            surface.blit(line_surf, (desc_x + 10, y_offset))
            y_offset += 12
        
        # Price
        price_text = f"Wert: {item.sell_price}€"
        price_surf = self.small_font.render(price_text, True, self.disabled_color)
        surface.blit(price_surf, (desc_x + desc_width - 60, desc_y + desc_height - 15))
    
    def _wrap_text(self, text: str, max_width: int) -> List[str]:
        """Wrap text to fit within width."""
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            if self.small_font.size(test_line)[0] > max_width:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
            else:
                current_line.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines


class PartyMenu(MenuBase):
    """Party management menu."""
    
    def __init__(self, game: 'Game'):
        """Initialize party menu."""
        super().__init__(game)
        self.party = game.party_manager.party if hasattr(game, 'party_manager') else None
        self.selected_monster = 0
        self.in_swap_mode = False
        self.swap_source = -1
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle input events."""
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_w, pygame.K_UP]:
                if self.selected_monster > 0:
                    self.selected_monster -= 1
                return True
                
            elif event.key in [pygame.K_s, pygame.K_DOWN]:
                if self.selected_monster < 5:
                    self.selected_monster += 1
                return True
                
            elif event.key in [pygame.K_e, pygame.K_RETURN, pygame.K_SPACE]:
                if self.in_swap_mode:
                    # Complete swap
                    if self.swap_source != self.selected_monster:
                        self.party.swap_positions(self.swap_source, self.selected_monster)
                    self.in_swap_mode = False
                    self.swap_source = -1
                else:
                    # Start swap
                    if self.party.members[self.selected_monster]:
                        self.in_swap_mode = True
                        self.swap_source = self.selected_monster
                return True
                
            elif event.key in [pygame.K_q, pygame.K_ESCAPE]:
                if self.in_swap_mode:
                    self.in_swap_mode = False
                    self.swap_source = -1
                    return True
                return False
                
        return False
    
    def update(self, dt: float) -> None:
        """Update party menu."""
        pass
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw party menu."""
        # Main window
        self.draw_window(surface, self.window_x, self.window_y,
                        self.window_width, self.window_height, "Team")
        
        if not self.party:
            return
        
        # Party slots
        y_offset = self.window_y + 30
        
        for i in range(6):
            monster = self.party.members[i]
            is_selected = i == self.selected_monster
            is_swap_source = i == self.swap_source and self.in_swap_mode
            
            # Slot background
            slot_rect = pygame.Rect(self.window_x + 10, y_offset - 2,
                                   self.window_width - 20, 18)
            
            if is_swap_source:
                pygame.draw.rect(surface, (60, 60, 30), slot_rect)
            elif is_selected:
                pygame.draw.rect(surface, (40, 40, 60), slot_rect)
            
            if monster:
                # Monster info
                name = monster.nickname or monster.species.name
                level = monster.level
                hp_percent = monster.current_hp / monster.max_hp
                
                # Name and level
                text = f"{i+1}. {name} Lv.{level}"
                color = self.selected_color if is_selected else self.unselected_color
                text_surf = self.small_font.render(text, True, color)
                surface.blit(text_surf, (self.window_x + 15, y_offset))
                
                # HP bar
                bar_x = self.window_x + 180
                bar_y = y_offset + 2
                bar_width = 80
                bar_height = 10
                
                # Background
                pygame.draw.rect(surface, (40, 40, 40),
                               (bar_x, bar_y, bar_width, bar_height))
                
                # Fill
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
                
                # HP text
                hp_text = f"{monster.current_hp}/{monster.max_hp}"
                hp_surf = self.small_font.render(hp_text, True, (255, 255, 255))
                hp_rect = hp_surf.get_rect(center=(bar_x + bar_width // 2, bar_y + 5))
                surface.blit(hp_surf, hp_rect)
                
                # Status icon
                if monster.status:
                    status_colors = {
                        'burn': (200, 50, 0),
                        'freeze': (100, 200, 255),
                        'paralysis': (200, 200, 0),
                        'poison': (150, 0, 200),
                        'sleep': (100, 100, 100)
                    }
                    # Handle status condition object properly
                    if hasattr(monster.status, 'name'):
                        status_name = monster.status.name
                    elif hasattr(monster.status, '__str__'):
                        status_name = str(monster.status)
                    else:
                        status_name = "OK"
                    
                    status_color = status_colors.get(status_name, (150, 150, 150))
                    status_rect = pygame.Rect(bar_x - 25, bar_y, 20, 10)
                    pygame.draw.rect(surface, status_color, status_rect)
                    
                    status_text = status_name[:3].upper() if len(status_name) >= 3 else status_name.upper()
                    status_surf = pygame.font.Font(None, 10).render(status_text, True, (255, 255, 255))
                    surface.blit(status_surf, (bar_x - 23, bar_y + 1))
            else:
                # Empty slot
                text = f"{i+1}. ---"
                color = self.disabled_color
                text_surf = self.small_font.render(text, True, color)
                surface.blit(text_surf, (self.window_x + 15, y_offset))
            
            y_offset += 20
        
        # Instructions
        if self.in_swap_mode:
            inst_text = "Wähle Position zum Tauschen (Q: Abbrechen)"
        else:
            inst_text = "E: Tauschen  Q: Zurück"
        
        inst_surf = self.small_font.render(inst_text, True, self.disabled_color)
        inst_rect = inst_surf.get_rect(center=(self.window_x + self.window_width // 2,
                                              self.window_y + self.window_height - 10))
        surface.blit(inst_surf, inst_rect)


class QuestMenu(MenuBase):
    """Quest log menu."""
    
    def __init__(self, game: 'Game'):
        """Initialize quest menu."""
        super().__init__(game)
        self.quest_manager = game.quest_manager if hasattr(game, 'quest_manager') else None
        self.active_quests = []
        self.selected_quest = None
        self.show_details = False
        self._refresh_quests()
    
    def _refresh_quests(self) -> None:
        """Refresh active quests list."""
        if self.quest_manager:
            self.active_quests = self.quest_manager.get_active_quests()
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle input events."""
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_w, pygame.K_UP]:
                if self.selected_index > 0:
                    self.selected_index -= 1
                    if self.selected_index < self.scroll_offset:
                        self.scroll_offset = self.selected_index
                return True
                
            elif event.key in [pygame.K_s, pygame.K_DOWN]:
                if self.selected_index < len(self.active_quests) - 1:
                    self.selected_index += 1
                    if self.selected_index >= self.scroll_offset + self.items_per_page:
                        self.scroll_offset = self.selected_index - self.items_per_page + 1
                return True
                
            elif event.key in [pygame.K_e, pygame.K_RETURN, pygame.K_SPACE]:
                if self.active_quests:
                    self.selected_quest = self.active_quests[self.selected_index]
                    self.show_details = not self.show_details
                return True
                
            elif event.key in [pygame.K_q, pygame.K_ESCAPE]:
                if self.show_details:
                    self.show_details = False
                    return True
                return False
                
        return False
    
    def update(self, dt: float) -> None:
        """Update quest menu."""
        pass
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw quest menu."""
        if self.show_details and self.selected_quest:
            self._draw_quest_details(surface)
        else:
            self._draw_quest_list(surface)
    
    def _draw_quest_list(self, surface: pygame.Surface) -> None:
        """Draw quest list."""
        self.draw_window(surface, self.window_x, self.window_y,
                        self.window_width, self.window_height, "Quests")
        
        if not self.active_quests:
            text = "Keine aktiven Quests"
            text_surf = self.font.render(text, True, self.disabled_color)
            text_rect = text_surf.get_rect(center=(self.window_x + self.window_width // 2,
                                                   self.window_y + self.window_height // 2))
            surface.blit(text_surf, text_rect)
            return
        
        # Quest list
        y_offset = self.window_y + 30
        visible_quests = self.active_quests[self.scroll_offset:self.scroll_offset + self.items_per_page]
        
        for i, quest in enumerate(visible_quests):
            actual_index = self.scroll_offset + i
            is_selected = actual_index == self.selected_index
            
            # Selection highlight
            if is_selected:
                select_rect = pygame.Rect(self.window_x + 5, y_offset - 2,
                                         self.window_width - 10, 14)
                pygame.draw.rect(surface, (40, 40, 60), select_rect)
            
            # Quest type indicator
            type_colors = {
                'MAIN': (255, 215, 0),
                'SIDE': (150, 150, 255),
                'DAILY': (100, 255, 100)
            }
            type_color = type_colors.get(quest.quest_type.name, (150, 150, 150))
            type_indicator = "●"
            type_surf = self.small_font.render(type_indicator, True, type_color)
            surface.blit(type_surf, (self.window_x + 10, y_offset))
            
            # Quest name
            text = quest.name
            color = self.selected_color if is_selected else self.unselected_color
            text_surf = self.small_font.render(text, True, color)
            surface.blit(text_surf, (self.window_x + 25, y_offset))
            
            # Completion percentage
            percent = int(quest.get_completion_percentage())
            percent_text = f"{percent}%"
            percent_color = (0, 200, 0) if percent == 100 else self.disabled_color
            percent_surf = self.small_font.render(percent_text, True, percent_color)
            surface.blit(percent_surf, (self.window_x + self.window_width - 35, y_offset))
            
            y_offset += 14
    
    def _draw_quest_details(self, surface: pygame.Surface) -> None:
        """Draw quest details."""
        quest = self.selected_quest
        
        self.draw_window(surface, self.window_x, self.window_y,
                        self.window_width, self.window_height, quest.name)
        
        y_offset = self.window_y + 30
        
        # Description
        desc_lines = self._wrap_text(quest.description, self.window_width - 20)
        for line in desc_lines[:2]:
            line_surf = self.small_font.render(line, True, self.unselected_color)
            surface.blit(line_surf, (self.window_x + 10, y_offset))
            y_offset += 12
        
        y_offset += 5
        
        # Objectives
        objectives_text = "Ziele:"
        obj_surf = self.font.render(objectives_text, True, self.selected_color)
        surface.blit(obj_surf, (self.window_x + 10, y_offset))
        y_offset += 15
        
        for obj in quest.get_active_objectives()[:3]:  # Max 3 visible
            # Checkbox
            check = "☑" if obj.is_complete() else "☐"
            check_surf = self.small_font.render(check, True, 
                                               (0, 200, 0) if obj.is_complete() else self.unselected_color)
            surface.blit(check_surf, (self.window_x + 15, y_offset))
            
            # Objective text
            obj_text = obj.get_progress_text()
            obj_surf = self.small_font.render(obj_text[:35], True, self.unselected_color)
            surface.blit(obj_surf, (self.window_x + 30, y_offset))
            y_offset += 12
        
        # Back instruction
        back_text = "Q: Zurück zur Liste"
        back_surf = self.small_font.render(back_text, True, self.disabled_color)
        surface.blit(back_surf, (self.window_x + 10, self.window_y + self.window_height - 15))
    
    def _wrap_text(self, text: str, max_width: int) -> List[str]:
        """Wrap text to fit within width."""
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            if self.small_font.size(test_line)[0] > max_width:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
            else:
                current_line.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines


class SaveMenu(MenuBase):
    """Save game menu."""
    
    def __init__(self, game: 'Game'):
        """Initialize save menu."""
        super().__init__(game)
        from engine.systems.save import SaveSystem
        self.save_system = SaveSystem()
        self.save_slots = self.save_system.get_all_saves()
        self.selected_slot = 0
        self.confirming = False
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle input events."""
        if event.type == pygame.KEYDOWN:
            if self.confirming:
                if event.key in [pygame.K_e, pygame.K_RETURN, pygame.K_SPACE]:
                    self._save_to_slot(self.selected_slot + 1)
                    self.confirming = False
                    return True
                elif event.key in [pygame.K_q, pygame.K_ESCAPE]:
                    self.confirming = False
                    return True
            else:
                if event.key in [pygame.K_w, pygame.K_UP]:
                    self.selected_slot = (self.selected_slot - 1) % 3
                    return True
                elif event.key in [pygame.K_s, pygame.K_DOWN]:
                    self.selected_slot = (self.selected_slot + 1) % 3
                    return True
                elif event.key in [pygame.K_e, pygame.K_RETURN, pygame.K_SPACE]:
                    self.confirming = True
                    return True
                elif event.key in [pygame.K_q, pygame.K_ESCAPE]:
                    return False
        return False
    
    def _save_to_slot(self, slot: int) -> None:
        """Save game to slot."""
        from engine.systems.save import GameStateSerializer
        game_data = GameStateSerializer.serialize(self.game)
        player_name = getattr(self.game, 'player_name', 'Player')
        
        if self.save_system.save_game(slot, game_data, player_name):
            # Refresh slots
            self.save_slots = self.save_system.get_all_saves()
    
    def update(self, dt: float) -> None:
        """Update save menu."""
        pass
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw save menu."""
        self.draw_window(surface, self.window_x, self.window_y,
                        self.window_width, self.window_height, "Speichern")
        
        y_offset = self.window_y + 30
        
        for i in range(3):
            metadata = self.save_slots[i]
            is_selected = i == self.selected_slot
            
            # Slot background
            slot_rect = pygame.Rect(self.window_x + 10, y_offset - 2,
                                   self.window_width - 20, 30)
            if is_selected:
                pygame.draw.rect(surface, (40, 40, 60), slot_rect)
                pygame.draw.rect(surface, self.selected_color, slot_rect, 1)
            
            if metadata:
                # Existing save
                line1 = f"Slot {i+1}: {metadata.name}"
                hours = int(metadata.playtime // 3600)
                minutes = int((metadata.playtime % 3600) // 60)
                line2 = f"Lv.{metadata.level} | {metadata.badges} Prüfungen | {hours:02d}:{minutes:02d}"
                
                color = self.selected_color if is_selected else self.unselected_color
                
                text1_surf = self.small_font.render(line1, True, color)
                surface.blit(text1_surf, (self.window_x + 15, y_offset))
                
                text2_surf = self.small_font.render(line2, True, self.disabled_color)
                surface.blit(text2_surf, (self.window_x + 15, y_offset + 12))
            else:
                # Empty slot
                text = f"Slot {i+1}: Leer"
                color = self.selected_color if is_selected else self.disabled_color
                text_surf = self.font.render(text, True, color)
                surface.blit(text_surf, (self.window_x + 15, y_offset + 6))
            
            y_offset += 35
        
        # Confirmation dialog
        if self.confirming:
            confirm_rect = pygame.Rect(self.window_x + 40, self.window_y + 50, 200, 60)
            pygame.draw.rect(surface, self.bg_color, confirm_rect)
            pygame.draw.rect(surface, self.selected_color, confirm_rect, 2)
            
            if self.save_slots[self.selected_slot]:
                text = "Überschreiben?"
            else:
                text = "Hier speichern?"
            
            text_surf = self.font.render(text, True, self.selected_color)
            text_rect = text_surf.get_rect(center=(confirm_rect.centerx, confirm_rect.centery - 10))
            surface.blit(text_surf, text_rect)
            
            inst_text = "E: Ja  Q: Nein"
            inst_surf = self.small_font.render(inst_text, True, self.unselected_color)
            inst_rect = inst_surf.get_rect(center=(confirm_rect.centerx, confirm_rect.centery + 10))
            surface.blit(inst_surf, inst_rect)


class ConfirmDialog(MenuBase):
    """Confirmation dialog."""
    
    def __init__(self, title: str, message: str,
                yes_callback: Callable, no_callback: Callable):
        """Initialize confirmation dialog."""
        super().__init__(None)  # No game reference needed
        self.title = title
        self.message = message
        self.yes_callback = yes_callback
        self.no_callback = no_callback
        self.selected = 0  # 0 = Yes, 1 = No
        
        # Center dialog
        self.window_width = 200
        self.window_height = 80
        self.window_x = 160 - self.window_width // 2
        self.window_y = 90 - self.window_height // 2
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle input events."""
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_a, pygame.K_LEFT, pygame.K_d, pygame.K_RIGHT]:
                self.selected = 1 - self.selected
                return True
            elif event.key in [pygame.K_e, pygame.K_RETURN, pygame.K_SPACE]:
                if self.selected == 0:
                    self.yes_callback()
                else:
                    self.no_callback()
                return True
            elif event.key in [pygame.K_q, pygame.K_ESCAPE]:
                self.no_callback()
                return True
        return False
    
    def update(self, dt: float) -> None:
        """Update dialog."""
        pass
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw confirmation dialog."""
        # Dialog background
        self.draw_window(surface, self.window_x, self.window_y,
                        self.window_width, self.window_height)
        
        # Title
        title_surf = self.font.render(self.title, True, self.selected_color)
        title_rect = title_surf.get_rect(center=(self.window_x + self.window_width // 2,
                                                self.window_y + 20))
        surface.blit(title_surf, title_rect)
        
        # Message
        if self.message:
            msg_surf = self.small_font.render(self.message[:30], True, self.unselected_color)
            msg_rect = msg_surf.get_rect(center=(self.window_x + self.window_width // 2,
                                                self.window_y + 35))
            surface.blit(msg_surf, msg_rect)
        
        # Options
        yes_color = self.selected_color if self.selected == 0 else self.unselected_color
        no_color = self.selected_color if self.selected == 1 else self.unselected_color
        
        yes_text = "Ja"
        yes_surf = self.font.render(yes_text, True, yes_color)
        yes_rect = yes_surf.get_rect(center=(self.window_x + 60, self.window_y + 55))
        surface.blit(yes_surf, yes_rect)
        
        no_text = "Nein"
        no_surf = self.font.render(no_text, True, no_color)
        no_rect = no_surf.get_rect(center=(self.window_x + 140, self.window_y + 55))
        surface.blit(no_surf, no_rect)
        
        # Selection indicator
        if self.selected == 0:
            indicator_x = self.window_x + 40
        else:
            indicator_x = self.window_x + 120
        
        indicator = ">"
        indicator_surf = self.font.render(indicator, True, self.selected_color)
        surface.blit(indicator_surf, (indicator_x, self.window_y + 50))