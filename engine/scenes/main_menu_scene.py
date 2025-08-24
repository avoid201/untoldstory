"""
Main menu scene for game start, load, and options.
"""

import pygame
from typing import TYPE_CHECKING, Optional, List, Tuple
from enum import Enum, auto

from engine.core.scene_base import Scene
from engine.ui.transitions import FadeTransition
from engine.systems.save import SaveSystem, SaveMetadata

if TYPE_CHECKING:
    from engine.core.game import Game


class MenuOption(Enum):
    """Main menu options."""
    NEW_GAME = auto()
    CONTINUE = auto()
    LOAD_GAME = auto()
    OPTIONS = auto()
    QUIT = auto()


class MainMenuScene(Scene):
    """Main menu scene."""
    
    def __init__(self, game: 'Game'):
        """Initialize main menu scene."""
        super().__init__(game)
        
        # Menu state
        self.selected_option = 0
        self.menu_options = [
            MenuOption.NEW_GAME,
            MenuOption.CONTINUE,
            MenuOption.LOAD_GAME,
            MenuOption.OPTIONS,
            MenuOption.QUIT
        ]
        
        # Sub-menu states
        self.in_submenu = False
        self.submenu_type = None
        self.submenu_selection = 0
        
        # Options menu items
        self.options_menu_items = [
            "Musik: An",
            "Sound: An", 
            "Geschwindigkeit: Normal",
            "Zurück"
        ]
        
        # Save system
        self.save_system = SaveSystem()
        self.save_slots: List[Optional[SaveMetadata]] = []
        self.has_saves = False
        self._check_saves()
        
        # UI positioning
        self.menu_x = self.game.logical_size[0] // 2
        self.menu_y = self.game.logical_size[1] // 2
        
        # Fonts
        self.title_font = pygame.font.Font(None, 32)
        self.menu_font = pygame.font.Font(None, 20)
        self.small_font = pygame.font.Font(None, 14)
        
        # Colors
        self.bg_color = (20, 25, 40)
        self.title_color = (255, 215, 0)
        self.selected_color = (255, 255, 255)
        self.unselected_color = (150, 150, 150)
        self.disabled_color = (80, 80, 80)
        
        # Transition
        self.transition = None  # Wird bei Bedarf erstellt
        
        # Background animation
        self.bg_offset = 0
        self.bg_speed = 0.5
    
    def _check_saves(self) -> None:
        """Check for existing save files."""
        self.save_slots = self.save_system.get_all_saves()
        self.has_saves = any(slot is not None for slot in self.save_slots)
        
        # Disable continue if no saves
        if not self.has_saves and MenuOption.CONTINUE in self.menu_options:
            # Keep it but mark as disabled
            pass
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle input events."""
        if event.type == pygame.KEYDOWN:
            if self.in_submenu:
                return self._handle_submenu_input(event)
            else:
                return self._handle_main_menu_input(event)
        return False
    
    def _handle_main_menu_input(self, event: pygame.event.Event) -> bool:
        """Handle main menu input."""
        if event.key in [pygame.K_w, pygame.K_UP]:
            self.selected_option = (self.selected_option - 1) % len(self.menu_options)
            # Skip disabled options
            if self._is_option_disabled(self.menu_options[self.selected_option]):
                self.selected_option = (self.selected_option - 1) % len(self.menu_options)
            return True
            
        elif event.key in [pygame.K_s, pygame.K_DOWN]:
            self.selected_option = (self.selected_option + 1) % len(self.menu_options)
            # Skip disabled options
            if self._is_option_disabled(self.menu_options[self.selected_option]):
                self.selected_option = (self.selected_option + 1) % len(self.menu_options)
            return True
            
        elif event.key in [pygame.K_e, pygame.K_RETURN, pygame.K_SPACE]:
            self._select_option()
            return True
            
        elif event.key in [pygame.K_ESCAPE]:
            # Can't exit from main menu
            return True
            
        return False
    
    def _handle_submenu_input(self, event: pygame.event.Event) -> bool:
        """Handle submenu input."""
        if self.submenu_type == 'load':
            if event.key in [pygame.K_w, pygame.K_UP]:
                # Move through save slots
                self.submenu_selection = (self.submenu_selection - 1) % 4  # 3 slots + back
                return True
                
            elif event.key in [pygame.K_s, pygame.K_DOWN]:
                self.submenu_selection = (self.submenu_selection + 1) % 4
                return True
                
            elif event.key in [pygame.K_e, pygame.K_RETURN, pygame.K_SPACE]:
                if self.submenu_selection < 3:
                    # Load from slot
                    self._load_game(self.submenu_selection + 1)
                else:
                    # Back to main menu
                    self.in_submenu = False
                    self.submenu_type = None
                return True
                
            elif event.key in [pygame.K_q, pygame.K_ESCAPE]:
                self.in_submenu = False
                self.submenu_type = None
                return True
                
        elif self.submenu_type == 'new':
            # New game confirmation
            if event.key in [pygame.K_w, pygame.K_UP, pygame.K_s, pygame.K_DOWN]:
                self.submenu_selection = 1 - self.submenu_selection
                return True
                
            elif event.key in [pygame.K_e, pygame.K_RETURN, pygame.K_SPACE]:
                if self.submenu_selection == 0:
                    self._start_new_game()
                else:
                    self.in_submenu = False
                    self.submenu_type = None
                return True
                
            elif event.key in [pygame.K_q, pygame.K_ESCAPE]:
                self.in_submenu = False
                self.submenu_type = None
                return True
                
        elif self.submenu_type == 'options':
            # Options menu
            if event.key == pygame.K_UP:
                self.submenu_selection = max(0, self.submenu_selection - 1)
                return True
            elif event.key == pygame.K_DOWN:
                self.submenu_selection = min(len(self.options_menu_items) - 1, self.submenu_selection + 1)
                return True
            elif event.key == pygame.K_RETURN:
                self._handle_option_selection()
                return True
            elif event.key in [pygame.K_q, pygame.K_ESCAPE]:
                self.in_submenu = False
                self.submenu_type = None
                return True
                
        return False
    
    def _is_option_disabled(self, option: MenuOption) -> bool:
        """Check if a menu option is disabled."""
        if option == MenuOption.CONTINUE:
            return not self.has_saves
        return False
    
    def _select_option(self) -> None:
        """Select the current menu option."""
        option = self.menu_options[self.selected_option]
        
        if self._is_option_disabled(option):
            return
        
        if option == MenuOption.NEW_GAME:
            # Check if saves exist for confirmation
            if self.has_saves:
                self.in_submenu = True
                self.submenu_type = 'new'
                self.submenu_selection = 0
            else:
                self._start_new_game()
                
        elif option == MenuOption.CONTINUE:
            # Load most recent save
            self._continue_game()
            
        elif option == MenuOption.LOAD_GAME:
            self.in_submenu = True
            self.submenu_type = 'load'
            self.submenu_selection = 0
            
        elif option == MenuOption.OPTIONS:
            self.in_submenu = True
            self.submenu_type = 'options'
            self.submenu_selection = 0
            
        elif option == MenuOption.QUIT:
            self.game.running = False
    
    def _start_new_game(self) -> None:
        """Start a new game - Zeit, den Arsch hochzukriegen!"""
        # Reset story flags für neues Spiel
        if hasattr(self.game, 'story_manager'):
            self.game.story_manager.reset()
            self.game.story_manager.set_flag('game_started', True)
            self.game.story_manager.set_flag('first_awakening', True)  # Für Intro-Sequenz
        
        # Party leeren für frischen Start
        if hasattr(self.game, 'party_manager'):
            # Party hat keine clear() Methode - erstelle neue Party
            from engine.systems.party import Party
            self.game.party_manager.party = Party()
        
        # Ab ins Spielerhaus, direkt am Bett
        from engine.scenes.field_scene import FieldScene
        self.game.change_scene(
            FieldScene,
            map_id='player_house',
            spawn_point='bed',  # Aufwachen im Bett
            transition='fade_black'
        )
    
    def _continue_game(self) -> None:
        """Continue from most recent save."""
        # Find most recent save
        most_recent = None
        most_recent_slot = 0
        
        for i, metadata in enumerate(self.save_slots):
            if metadata:
                if most_recent is None or metadata.timestamp > most_recent.timestamp:
                    most_recent = metadata
                    most_recent_slot = i + 1
        
        if most_recent:
            self._load_game(most_recent_slot)
    
    def _load_game(self, slot: int) -> None:
        """Load a game from a save slot."""
        metadata = self.save_slots[slot - 1]
        if not metadata:
            return
        
        # Load game data
        game_data = self.save_system.load_game(slot)
        if game_data:
            # Apply loaded data to game
            from engine.systems.save import GameStateSerializer
            GameStateSerializer.deserialize(self.game, game_data)
            
            # Transition to field scene
            from engine.scenes.field_scene import FieldScene
            self.game.change_scene(FieldScene)
    
    def _handle_option_selection(self) -> None:
        """Handle option selection in options menu."""
        selected_item = self.options_menu_items[self.submenu_selection]
        
        if "Musik" in selected_item:
            # Toggle Musik
            if "An" in selected_item:
                self.options_menu_items[self.submenu_selection] = "Musik: Aus"
                # TODO: Implementiere Musik-Aus
            else:
                self.options_menu_items[self.submenu_selection] = "Musik: An"
                # TODO: Implementiere Musik-An
                
        elif "Sound" in selected_item:
            # Toggle Sound
            if "An" in selected_item:
                self.options_menu_items[self.submenu_selection] = "Sound: Aus"
                # TODO: Implementiere Sound-Aus
            else:
                self.options_menu_items[self.submenu_selection] = "Sound: An"
                # TODO: Implementiere Sound-An
                
        elif "Geschwindigkeit" in selected_item:
            # Cycle through speeds
            speeds = ["Langsam", "Normal", "Schnell"]
            current_speed = selected_item.split(": ")[1]
            current_index = speeds.index(current_speed)
            next_index = (current_index + 1) % len(speeds)
            self.options_menu_items[self.submenu_selection] = f"Geschwindigkeit: {speeds[next_index]}"
            # TODO: Implementiere Geschwindigkeits-Änderung
            
        elif "Zurück" in selected_item:
            # Return to main menu
            self.in_submenu = False
            self.submenu_type = None
    
    def update(self, dt: float) -> None:
        """Update main menu."""
        # Update transition
        if self.transition:
            self.transition.update(dt)
        
        # Update background animation
        self.bg_offset += self.bg_speed * dt * 60
        if self.bg_offset > 100:
            self.bg_offset -= 100
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw main menu."""
        # Background
        surface.fill(self.bg_color)
        
        # Animated background pattern
        self._draw_background_pattern(surface)
        
        # Title
        title_text = "UNTOLD STORY"
        title_surf = self.title_font.render(title_text, True, self.title_color)
        title_rect = title_surf.get_rect(center=(self.menu_x, 40))
        surface.blit(title_surf, title_rect)
        
        # Subtitle
        subtitle_text = "Eine Reise durch Zeit und Monster"
        subtitle_surf = self.small_font.render(subtitle_text, True, self.unselected_color)
        subtitle_rect = subtitle_surf.get_rect(center=(self.menu_x, 60))
        surface.blit(subtitle_surf, subtitle_rect)
        
        # Draw menu or submenu
        if self.in_submenu:
            self._draw_submenu(surface)
        else:
            self._draw_main_menu(surface)
        
        # Version info
        version_text = "v1.0.0"
        version_surf = self.small_font.render(version_text, True, self.disabled_color)
        surface.blit(version_surf, (5, self.game.logical_size[1] - 15))
        
        # Draw transition
        if self.transition and self.transition.active:
            self.transition.draw(surface)
    
    def _draw_main_menu(self, surface: pygame.Surface) -> None:
        """Draw main menu options."""
        menu_names = {
            MenuOption.NEW_GAME: "Neues Spiel",
            MenuOption.CONTINUE: "Fortsetzen",
            MenuOption.LOAD_GAME: "Spiel laden",
            MenuOption.OPTIONS: "Optionen",
            MenuOption.QUIT: "Beenden"
        }
        
        y_offset = 90
        
        for i, option in enumerate(self.menu_options):
            # Determine color
            if self._is_option_disabled(option):
                color = self.disabled_color
            elif i == self.selected_option:
                color = self.selected_color
            else:
                color = self.unselected_color
            
            # Draw option
            text = menu_names[option]
            text_surf = self.menu_font.render(text, True, color)
            text_rect = text_surf.get_rect(center=(self.menu_x, y_offset))
            surface.blit(text_surf, text_rect)
            
            # Draw selection indicator
            if i == self.selected_option and not self._is_option_disabled(option):
                indicator = ">"
                indicator_surf = self.menu_font.render(indicator, True, self.selected_color)
                indicator_rect = indicator_surf.get_rect(midright=(self.menu_x - 60, y_offset))
                surface.blit(indicator_surf, indicator_rect)
            
            y_offset += 25
    
    def _draw_submenu(self, surface: pygame.Surface) -> None:
        """Draw submenu."""
        if self.submenu_type == 'load':
            self._draw_load_menu(surface)
        elif self.submenu_type == 'new':
            self._draw_new_game_confirmation(surface)
        elif self.submenu_type == 'options':
            self._draw_options_menu(surface)
    
    def _draw_load_menu(self, surface: pygame.Surface) -> None:
        """Draw load game menu."""
        # Title
        title = "Spiel laden"
        title_surf = self.menu_font.render(title, True, self.selected_color)
        title_rect = title_surf.get_rect(center=(self.menu_x, 80))
        surface.blit(title_surf, title_rect)
        
        y_offset = 110
        
        # Draw save slots
        for i in range(3):
            metadata = self.save_slots[i]
            
            # Slot background
            slot_rect = pygame.Rect(self.menu_x - 120, y_offset - 10, 240, 35)
            if i == self.submenu_selection:
                pygame.draw.rect(surface, (40, 40, 60), slot_rect)
                pygame.draw.rect(surface, self.selected_color, slot_rect, 2)
            else:
                pygame.draw.rect(surface, (30, 30, 40), slot_rect)
                pygame.draw.rect(surface, self.disabled_color, slot_rect, 1)
            
            if metadata:
                # Save exists - show info
                # Line 1: Name and location
                line1 = f"Slot {i+1}: {metadata.name}"
                # Line 2: Level, badges, playtime
                hours = int(metadata.playtime // 3600)
                minutes = int((metadata.playtime % 3600) // 60)
                line2 = f"Lv.{metadata.level} | {metadata.badges} Prüfungen | {hours:02d}:{minutes:02d}"
                
                color = self.selected_color if i == self.submenu_selection else self.unselected_color
                
                text1_surf = self.small_font.render(line1, True, color)
                text1_rect = text1_surf.get_rect(midleft=(self.menu_x - 110, y_offset))
                surface.blit(text1_surf, text1_rect)
                
                text2_surf = self.small_font.render(line2, True, self.disabled_color)
                text2_rect = text2_surf.get_rect(midleft=(self.menu_x - 110, y_offset + 15))
                surface.blit(text2_surf, text2_rect)
            else:
                # Empty slot
                text = f"Slot {i+1}: Leer"
                color = self.disabled_color
                text_surf = self.small_font.render(text, True, color)
                text_rect = text_surf.get_rect(center=(self.menu_x, y_offset + 7))
                surface.blit(text_surf, text_rect)
            
            y_offset += 45
        
        # Back option
        back_color = self.selected_color if self.submenu_selection == 3 else self.unselected_color
        back_text = "Zurück"
        back_surf = self.menu_font.render(back_text, True, back_color)
        back_rect = back_surf.get_rect(center=(self.menu_x, y_offset + 10))
        surface.blit(back_surf, back_rect)
        
        if self.submenu_selection == 3:
            indicator = ">"
            indicator_surf = self.menu_font.render(indicator, True, self.selected_color)
            indicator_rect = indicator_surf.get_rect(midright=(self.menu_x - 40, y_offset + 10))
            surface.blit(indicator_surf, indicator_rect)
    
    def _draw_new_game_confirmation(self, surface: pygame.Surface) -> None:
        """Draw new game confirmation dialog."""
        # Dialog box
        dialog_rect = pygame.Rect(self.menu_x - 100, self.menu_y - 40, 200, 80)
        pygame.draw.rect(surface, (30, 30, 40), dialog_rect)
        pygame.draw.rect(surface, self.selected_color, dialog_rect, 2)
        
        # Text
        text1 = "Neues Spiel starten?"
        text1_surf = self.menu_font.render(text1, True, self.selected_color)
        text1_rect = text1_surf.get_rect(center=(self.menu_x, self.menu_y - 20))
        surface.blit(text1_surf, text1_rect)
        
        # Options
        yes_color = self.selected_color if self.submenu_selection == 0 else self.unselected_color
        no_color = self.selected_color if self.submenu_selection == 1 else self.unselected_color
        
        yes_text = "Ja"
        yes_surf = self.menu_font.render(yes_text, True, yes_color)
        yes_rect = yes_surf.get_rect(center=(self.menu_x - 40, self.menu_y + 10))
        surface.blit(yes_surf, yes_rect)
        
        no_text = "Nein"
        no_surf = self.menu_font.render(no_text, True, no_color)
        no_rect = no_surf.get_rect(center=(self.menu_x + 40, self.menu_y + 10))
        surface.blit(no_surf, no_rect)
        
        # Selection indicator
        if self.submenu_selection == 0:
            indicator_x = self.menu_x - 60
        else:
            indicator_x = self.menu_x + 20
        
        indicator = ">"
        indicator_surf = self.menu_font.render(indicator, True, self.selected_color)
        indicator_rect = indicator_surf.get_rect(midright=(indicator_x, self.menu_y + 10))
        surface.blit(indicator_surf, indicator_rect)
    
    def _draw_options_menu(self, surface: pygame.Surface) -> None:
        """Draw options menu."""
        # Title
        title = "Optionen"
        title_surf = self.menu_font.render(title, True, self.selected_color)
        title_rect = title_surf.get_rect(center=(self.menu_x, 80))
        surface.blit(title_surf, title_rect)
        
        # Placeholder text
        text = "Kommt bald..."
        text_surf = self.small_font.render(text, True, self.disabled_color)
        text_rect = text_surf.get_rect(center=(self.menu_x, self.menu_y))
        surface.blit(text_surf, text_rect)
        
        # Back instruction
        back_text = "Drücke Q zum Zurückkehren"
        back_surf = self.small_font.render(back_text, True, self.unselected_color)
        back_rect = back_surf.get_rect(center=(self.menu_x, self.menu_y + 30))
        surface.blit(back_surf, back_rect)
    
    def _draw_background_pattern(self, surface: pygame.Surface) -> None:
        """Draw animated background pattern."""
        # Simple moving grid pattern
        grid_color = (25, 30, 45)
        for x in range(0, self.game.logical_size[0], 20):
            x_pos = x + (self.bg_offset % 20)
            pygame.draw.line(surface, grid_color, (x_pos, 0), (x_pos, self.game.logical_size[1]), 1)
        
        for y in range(0, self.game.logical_size[1], 20):
            y_pos = y + (self.bg_offset % 20)
            pygame.draw.line(surface, grid_color, (0, y_pos), (self.game.logical_size[0], y_pos), 1)