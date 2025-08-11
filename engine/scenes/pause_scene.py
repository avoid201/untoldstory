"""
Pause scene overlay for in-game menu.
"""

import pygame
from typing import TYPE_CHECKING, Optional, List
from enum import Enum, auto

from engine.core.scene_base import Scene

if TYPE_CHECKING:
    from engine.core.game import Game
    from engine.scenes.field_scene import FieldScene


class PauseOption(Enum):
    """Pause menu options."""
    RESUME = auto()
    INVENTORY = auto()
    PARTY = auto()
    QUESTS = auto()
    SAVE = auto()
    OPTIONS = auto()
    QUIT = auto()


class PauseScene(Scene):
    """Pause menu overlay scene."""
    
    def __init__(self, game: 'Game', parent_scene: Optional[Scene] = None):
        """
        Initialize pause scene.
        
        Args:
            game: Game instance
            parent_scene: Scene that was paused (optional)
        """
        super().__init__(game)
        self.parent_scene = parent_scene or game.scene_stack[-2] if len(game.scene_stack) > 1 else None
        
        # Menu state
        self.selected_option = 0
        self.menu_options = [
            PauseOption.RESUME,
            PauseOption.INVENTORY,
            PauseOption.PARTY,
            PauseOption.QUESTS,
            PauseOption.SAVE,
            PauseOption.OPTIONS,
            PauseOption.QUIT
        ]
        
        # Submenu state
        self.in_submenu = False
        self.submenu_type = None
        self.submenu = None
        
        # UI elements
        self.menu_width = 120
        self.menu_height = 160
        self.menu_x = self.game.logical_size[0] - self.menu_width - 10
        self.menu_y = 10
        
        # Status window
        self.status_width = 180
        self.status_height = 80
        self.status_x = 10
        self.status_y = 10
        
        # Fonts
        self.font = pygame.font.Font(None, 14)
        self.small_font = pygame.font.Font(None, 12)
        
        # Colors
        self.bg_color = (20, 20, 30)
        self.border_color = (100, 100, 120)
        self.selected_color = (255, 255, 255)
        self.unselected_color = (150, 150, 150)
        
        # Create overlay surface
        self.overlay = pygame.Surface((self.game.logical_size[0], self.game.logical_size[1]))
        self.overlay.set_alpha(128)
        self.overlay.fill((0, 0, 0))
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle input events."""
        if event.type == pygame.KEYDOWN:
            if self.in_submenu and self.submenu:
                # Let submenu handle input
                handled = self.submenu.handle_event(event)
                if not handled and event.key in [pygame.K_q, pygame.K_ESCAPE]:
                    self._close_submenu()
                    return True
                return handled
            else:
                return self._handle_menu_input(event)
        return False
    
    def _handle_menu_input(self, event: pygame.event.Event) -> bool:
        """Handle main pause menu input."""
        if event.key in [pygame.K_w, pygame.K_UP]:
            self.selected_option = (self.selected_option - 1) % len(self.menu_options)
            return True
            
        elif event.key in [pygame.K_s, pygame.K_DOWN]:
            self.selected_option = (self.selected_option + 1) % len(self.menu_options)
            return True
            
        elif event.key in [pygame.K_e, pygame.K_RETURN, pygame.K_SPACE]:
            self._select_option()
            return True
            
        elif event.key in [pygame.K_q, pygame.K_ESCAPE]:
            # Resume game
            self._resume_game()
            return True
            
        return False
    
    def _select_option(self) -> None:
        """Select current menu option."""
        option = self.menu_options[self.selected_option]
        
        if option == PauseOption.RESUME:
            self._resume_game()
            
        elif option == PauseOption.INVENTORY:
            self._open_inventory()
            
        elif option == PauseOption.PARTY:
            self._open_party()
            
        elif option == PauseOption.QUESTS:
            self._open_quests()
            
        elif option == PauseOption.SAVE:
            self._save_game()
            
        elif option == PauseOption.OPTIONS:
            self._open_options()
            
        elif option == PauseOption.QUIT:
            self._quit_to_menu()
    
    def _resume_game(self) -> None:
        """Resume the game."""
        self.game.pop_scene()
    
    def _open_inventory(self) -> None:
        """Open inventory submenu."""
        from engine.ui.menus import InventoryMenu
        self.submenu = InventoryMenu(self.game)
        self.in_submenu = True
        self.submenu_type = 'inventory'
    
    def _open_party(self) -> None:
        """Open party submenu."""
        from engine.ui.menus import PartyMenu
        self.submenu = PartyMenu(self.game)
        self.in_submenu = True
        self.submenu_type = 'party'
    
    def _open_quests(self) -> None:
        """Open quest log."""
        from engine.ui.menus import QuestMenu
        self.submenu = QuestMenu(self.game)
        self.in_submenu = True
        self.submenu_type = 'quests'
    
    def _save_game(self) -> None:
        """Open save menu."""
        from engine.ui.menus import SaveMenu
        self.submenu = SaveMenu(self.game)
        self.in_submenu = True
        self.submenu_type = 'save'
    
    def _open_options(self) -> None:
        """Open options menu."""
        # TODO: Implement options menu
        pass
    
    def _quit_to_menu(self) -> None:
        """Quit to main menu."""
        # Save confirmation dialog
        from engine.ui.menus import ConfirmDialog
        dialog = ConfirmDialog(
            "Zum Hauptmenü zurückkehren?",
            "Nicht gespeicherter Fortschritt geht verloren!",
            yes_callback=self._confirm_quit,
            no_callback=self._close_submenu
        )
        self.submenu = dialog
        self.in_submenu = True
        self.submenu_type = 'confirm'
    
    def _confirm_quit(self) -> None:
        """Confirm quit to main menu."""
        from engine.scenes.main_menu_scene import MainMenuScene
        main_menu = MainMenuScene(self.game)
        self.game.scene_manager.set_scene(main_menu)
    
    def _close_submenu(self) -> None:
        """Close current submenu."""
        self.in_submenu = False
        self.submenu_type = None
        self.submenu = None
    
    def update(self, dt: float) -> None:
        """Update pause scene."""
        if self.in_submenu and self.submenu:
            self.submenu.update(dt)
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw pause scene."""
        # Draw parent scene (frozen)
        self.parent_scene.draw(surface)
        
        # Draw darkened overlay
        surface.blit(self.overlay, (0, 0))
        
        if self.in_submenu and self.submenu:
            # Draw submenu
            self.submenu.draw(surface)
        else:
            # Draw pause menu
            self._draw_pause_menu(surface)
            self._draw_status_window(surface)
    
    def _draw_pause_menu(self, surface: pygame.Surface) -> None:
        """Draw main pause menu."""
        # Menu background
        menu_rect = pygame.Rect(self.menu_x, self.menu_y, self.menu_width, self.menu_height)
        pygame.draw.rect(surface, self.bg_color, menu_rect)
        pygame.draw.rect(surface, self.border_color, menu_rect, 2)
        
        # Menu title
        title = "PAUSE"
        title_surf = self.font.render(title, True, self.selected_color)
        title_rect = title_surf.get_rect(center=(self.menu_x + self.menu_width // 2, self.menu_y + 15))
        surface.blit(title_surf, title_rect)
        
        # Menu options
        option_names = {
            PauseOption.RESUME: "Fortsetzen",
            PauseOption.INVENTORY: "Inventar",
            PauseOption.PARTY: "Team",
            PauseOption.QUESTS: "Quests",
            PauseOption.SAVE: "Speichern",
            PauseOption.OPTIONS: "Optionen",
            PauseOption.QUIT: "Beenden"
        }
        
        y_offset = self.menu_y + 35
        
        for i, option in enumerate(self.menu_options):
            # Option text
            text = option_names[option]
            color = self.selected_color if i == self.selected_option else self.unselected_color
            
            text_surf = self.font.render(text, True, color)
            text_rect = text_surf.get_rect(midleft=(self.menu_x + 20, y_offset))
            surface.blit(text_surf, text_rect)
            
            # Selection indicator
            if i == self.selected_option:
                indicator = ">"
                indicator_surf = self.font.render(indicator, True, self.selected_color)
                indicator_rect = indicator_surf.get_rect(midright=(self.menu_x + 15, y_offset))
                surface.blit(indicator_surf, indicator_rect)
            
            y_offset += 18
    
    def _draw_status_window(self, surface: pygame.Surface) -> None:
        """Draw status window with game info."""
        # Status background
        status_rect = pygame.Rect(self.status_x, self.status_y, 
                                 self.status_width, self.status_height)
        pygame.draw.rect(surface, self.bg_color, status_rect)
        pygame.draw.rect(surface, self.border_color, status_rect, 2)
        
        # Get game info
        if hasattr(self.game, 'party_manager'):
            party = self.game.party_manager.party
            active_monster = party.get_active()
            
            if active_monster:
                # Monster name and level
                name_text = f"{active_monster.nickname or active_monster.species.name} Lv.{active_monster.level}"
                name_surf = self.font.render(name_text, True, self.selected_color)
                surface.blit(name_surf, (self.status_x + 10, self.status_y + 10))
                
                # HP
                hp_text = f"KP: {active_monster.current_hp}/{active_monster.max_hp}"
                hp_surf = self.small_font.render(hp_text, True, self.unselected_color)
                surface.blit(hp_surf, (self.status_x + 10, self.status_y + 28))
                
                # Party size
                party_size = len(party.get_all_members())
                party_text = f"Team: {party_size}/6"
                party_surf = self.small_font.render(party_text, True, self.unselected_color)
                surface.blit(party_surf, (self.status_x + 10, self.status_y + 43))
        
        # Money
        if hasattr(self.game, 'inventory'):
            money_text = f"Geld: {self.game.inventory.money}€"
            money_surf = self.small_font.render(money_text, True, self.unselected_color)
            surface.blit(money_surf, (self.status_x + 10, self.status_y + 58))
        
        # Playtime
        if hasattr(self.game, 'playtime'):
            hours = int(self.game.playtime // 3600)
            minutes = int((self.game.playtime % 3600) // 60)
            time_text = f"Zeit: {hours:02d}:{minutes:02d}"
            time_surf = self.small_font.render(time_text, True, self.unselected_color)
            surface.blit(time_surf, (self.status_x + 100, self.status_y + 58))
        
        # Location
        if hasattr(self.game, 'current_map'):
            location_text = self._get_location_name(self.game.current_map)
            loc_surf = self.small_font.render(location_text, True, self.unselected_color)
            surface.blit(loc_surf, (self.status_x + 100, self.status_y + 43))
    
    def _get_location_name(self, map_id: str) -> str:
        """Get display name for a map."""
        location_names = {
            'player_house': 'Zuhause',
            'kohlenstadt': 'Kohlenstadt',
            'route_1': 'Route 1',
            'zeche_zollverein': 'Zeche Zollverein',
            'museum_interior': 'Museum',
            'lab_interior': 'Labor',
            'ruhr_ufer': 'Ruhrufer',
            'industriepark': 'Industriepark',
            'bergwerk': 'Bergwerk'
        }
        return location_names.get(map_id, 'Unbekannt')
