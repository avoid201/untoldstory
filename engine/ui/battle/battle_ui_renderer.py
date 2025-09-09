"""
Battle UI Renderer - Alle Zeichen-Operationen
Verantwortlich für alle visuellen Darstellungen der Battle UI
"""

import pygame
import random
import logging
from typing import List, Tuple, Optional

from engine.core.config import LOGICAL_WIDTH, LOGICAL_HEIGHT, Colors
from engine.ui.battle_ui_utils import fonts, sprites
from .battle_ui_state import BattleMenuState

# Setup logger
logger = logging.getLogger(__name__)


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
        """Initialisiere Renderer."""
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
    
    def draw(self, surface: pygame.Surface) -> None:
        """Haupt-Zeichen-Methode - delegiert an spezifische Renderer."""
        # Apply screen shake from animation system
        shake_offset = (0, 0)
        if self.battle_ui.state and self.battle_ui.state.animations["screen_effects"]["shake"]["active"]:
            shake_data = self.battle_ui.state.animations["screen_effects"]["shake"]
            shake_offset = shake_data["offset"]
        
        # Apply shake to surface
        if shake_offset != (0, 0):
            surface = surface.subsurface(
                shake_offset[0], 
                shake_offset[1],
                LOGICAL_WIDTH, 
                LOGICAL_HEIGHT
            )
        
        # Draw all components
        self.draw_background(surface)
        self.draw_battlefield(surface)
        self.draw_monsters(surface)
        self.draw_status_panels(surface)
        self.draw_menus(surface)
        self.draw_visual_effects(surface)
        self.draw_screen_effects(surface)
    
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
        
        # Calculate HP ratio with animation from BattleUIState
        hp_ratio = monster.current_hp / monster.max_hp if monster.max_hp > 0 else 0
        
        # Check for animated HP update in BattleUIState
        if self.battle_ui.state and monster_id in self.battle_ui.state.animations["hp_bars"]:
            anim = self.battle_ui.state.animations["hp_bars"][monster_id]
            if anim["active"]:
                # Use animated HP value
                hp_ratio = anim["current"] / anim["max_hp"] if anim["max_hp"] > 0 else 0
        
        # HP Bar
        hp_color = self._get_hp_color(hp_ratio)
        hp_bar_rect = pygame.Rect(pos[0] + 4, pos[1] + 12, 112, 8)
        pygame.draw.rect(surface, (20, 20, 20), hp_bar_rect)
        pygame.draw.rect(surface, hp_color, (pos[0] + 4, pos[1] + 12, int(112 * hp_ratio), 8))
        
        # HP Text - show animated value if available
        display_hp = monster.current_hp
        if self.battle_ui.state and monster_id in self.battle_ui.state.animations["hp_bars"]:
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
        """Zeichne Status-Bedingungen."""
        if not monster:
            return
        
        # Get monster ID
        monster_id = monster.id if hasattr(monster, 'id') else id(monster)
        
        # Check for animated status effects
        if monster_id in self.state.animations["status_effects"]:
            effect = self.state.animations["status_effects"][monster_id]
            status = effect["status"]
            flash = effect["flash"]
            
            # Status icon
            status_icon = self._get_status_icon(status)
            if status_icon:
                icon_pos = (pos[0] - 20, pos[1] + 10)
                
                # Apply flash effect
                if flash:
                    status_icon = status_icon.copy()
                    status_icon.set_alpha(128)  # Dim when flashing
                
                surface.blit(status_icon, icon_pos)
        
        # Legacy support for monster.status
        elif hasattr(monster, 'status') and monster.status:
            status_icon = self._get_status_icon(monster.status)
            if status_icon:
                icon_pos = (pos[0] - 20, pos[1] + 10)
                surface.blit(status_icon, icon_pos)
    
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
        elif menu_state == BattleMenuState.TAME_MEAT:
            self.draw_meat_menu(surface)
        elif menu_state == BattleMenuState.TAME_CONFIRM:
            self.draw_tame_confirm(surface)
        elif menu_state == BattleMenuState.SCOUT:
            self.draw_scout_display(surface)
        elif menu_state == BattleMenuState.MESSAGE:
            self.draw_message_box(surface)
    
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
        """Zeichne Talent-basiertes Move-Menü."""
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
        
        # Talent-based Move list
        if self.state.player_active:
            # Hole Talent-Moves über Menu Manager
            talent_moves = self.battle_ui.menu_manager.get_talent_moves(self.state.player_active)
            talent_categories = self.battle_ui.menu_manager.get_talent_categories(talent_moves)
            
            # Filter nach aktueller Kategorie
            current_category = self.state.get_selected_move_category()
            moves = talent_categories.get(current_category, [])
            
            move_y = self.MENU_POS[1] + 20
            
            for i, move_data in enumerate(moves[:4]):  # Show max 4 moves
                if i == self.state.selected_move:
                    highlight_rect = pygame.Rect(self.MENU_POS[0] + 2, move_y + i * 12, self.MENU_SIZE[0] - 4, 10)
                    pygame.draw.rect(surface, (60, 60, 60), highlight_rect)
                
                # Move text mit Talent-Info
                move_font = fonts.move_name
                move = move_data['move']
                talent_name = move_data['talent_name']
                tier_stars = move_data['tier_stars']
                
                # DQM style: Talent-Name + Tier-Sterne + Move-Name
                move_text = f"{talent_name} {tier_stars} - {move.name}"
                power_text = f"Stärke: {move.power}" if hasattr(move, 'power') else ""
                
                # Zeichne Talent-Name und Tier-Sterne
                talent_text = f"{talent_name} {tier_stars}"
                talent_surface = move_font.render(talent_text, True, (255, 255, 100))  # Gold für Talent
                surface.blit(talent_surface, (self.MENU_POS[0] + 4, move_y + i * 12))
                
                # Zeichne Move-Name und Power
                move_info = f"{move.name} - {power_text}"
                move_surface = fonts.small.render(move_info, True, self.UI_COLOR)
                surface.blit(move_surface, (self.MENU_POS[0] + 4, move_y + i * 12 + 8))
    
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
    
    def draw_meat_menu(self, surface: pygame.Surface) -> None:
        """Zeichne Fleisch-Menü."""
        menu_rect = pygame.Rect(self.MENU_POS[0], self.MENU_POS[1], self.MENU_SIZE[0], self.MENU_SIZE[1])
        pygame.draw.rect(surface, (30, 30, 30), menu_rect)
        pygame.draw.rect(surface, (80, 80, 80), menu_rect, 1)
        
        # Title - use menu title font
        title_font = fonts.menu_title
        title_text = title_font.render("FLEISCH VORBEREITUNG", True, self.UI_COLOR)
        surface.blit(title_text, (self.MENU_POS[0] + 4, self.MENU_POS[1] + 4))
        
        # Meat options
        meat_options = [
            ("Fleisch", 3, "+20%"),
            ("Edelfleisch", 1, "+40%"),
            ("Götterfleisch", 0, "+80%"),
            ("Kein Fleisch", 999, "+0%")
        ]
        
        meat_y = self.MENU_POS[1] + 16
        for i, (name, count, bonus) in enumerate(meat_options):
            if i == self.state.selected_item:
                highlight_rect = pygame.Rect(self.MENU_POS[0] + 2, meat_y + i * 8, self.MENU_SIZE[0] - 4, 6)
                pygame.draw.rect(surface, (60, 60, 60), highlight_rect)
            
            # Meat text - use normal font for better readability
            meat_font = fonts.normal
            meat_text = f"{name} x{count} {bonus}"
            text = meat_font.render(meat_text, True, self.UI_COLOR)
            surface.blit(text, (self.MENU_POS[0] + 4, meat_y + i * 8))  # Increased line spacing
    
    def draw_tame_confirm(self, surface: pygame.Surface) -> None:
        """Zeichne Zähm-Bestätigung."""
        menu_rect = pygame.Rect(self.MENU_POS[0], self.MENU_POS[1], self.MENU_SIZE[0], self.MENU_SIZE[1])
        pygame.draw.rect(surface, (30, 30, 30), menu_rect)
        pygame.draw.rect(surface, (80, 80, 80), menu_rect, 1)
        
        # Title - use menu title font
        title_font = fonts.menu_title
        title_text = title_font.render("ZÄHMVERSUCH!", True, self.UI_COLOR)
        surface.blit(title_text, (self.MENU_POS[0] + 4, self.MENU_POS[1] + 4))
        
        # Taming chance - use normal font for better readability
        if self.state.taming_state["show_chance"]:
            chance_font = fonts.normal
            chance_text = f"Chance: {self.state.taming_state['taming_chance']}%"
            text = chance_font.render(chance_text, True, self.UI_COLOR)
            surface.blit(text, (self.MENU_POS[0] + 4, self.MENU_POS[1] + 20))
            
            # Options
            options = ["Zähmen versuchen", "Abbrechen"]
            option_y = self.MENU_POS[1] + 24
            
            for i, option in enumerate(options):
                if i == self.state.selected_option:
                    highlight_rect = pygame.Rect(self.MENU_POS[0] + 2, option_y + i * 10, self.MENU_SIZE[0] - 4, 8)
                    pygame.draw.rect(surface, (60, 60, 60), highlight_rect)
                
                option_text = chance_font.render(option, True, self.UI_COLOR)
                surface.blit(option_text, (self.MENU_POS[0] + 4, option_y + i * 10))  # Increased line spacing
    
    def draw_scout_display(self, surface: pygame.Surface) -> None:
        """Zeichne Spähen-Anzeige."""
        # Delegate to scout display component
        if self.battle_ui.scout_display:
            self.battle_ui.scout_display.draw(surface)
    
    def draw_message_box(self, surface: pygame.Surface) -> None:
        """Zeichne Nachrichten-Box - VERBESSERTE SICHTBARKEIT."""
        if not self.battle_ui.current_message:
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
        text = message_font.render(self.battle_ui.current_message, True, (255, 255, 255))  # Weißer Text
        
        # Text zentrieren
        text_rect = text.get_rect(center=(160, 156))  # Zentriert in der Box
        surface.blit(text, text_rect)
        
        # Blink-Effekt wenn Timer läuft
        if self.battle_ui.message_timer > 0:
            # Subtiler Blink-Effekt
            blink_alpha = int(128 + 127 * (self.battle_ui.message_timer % 0.5) / 0.5)
            blink_surface = pygame.Surface((304, 32), pygame.SRCALPHA)
            blink_surface.fill((255, 255, 255, blink_alpha))
            surface.blit(blink_surface, (8, 140), special_flags=pygame.BLEND_ALPHA_SDL2)
    
    def draw_visual_effects(self, surface: pygame.Surface) -> None:
        """Zeichne visuelle Effekte."""
        self.draw_damage_numbers(surface)
        self.draw_particle_effects(surface)
    
    def draw_damage_numbers(self, surface: pygame.Surface) -> None:
        """Zeichne Schadens-Nummern aus BattleUIState."""
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
    
    def draw_particle_effects(self, surface: pygame.Surface) -> None:
        """Zeichne Partikel-Effekte aus BattleUIState."""
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
        """Zeichne Bildschirm-Effekte aus BattleUIState."""
        # Screen flash from animation system
        if self.state.animations["screen_effects"]["flash"]["active"]:
            flash_data = self.state.animations["screen_effects"]["flash"]
            flash_surface = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT))
            flash_surface.fill(flash_data["color"])
            
            # Calculate alpha based on timer and intensity
            alpha = int(255 * flash_data["intensity"] * (flash_data["timer"] / 0.3))
            flash_surface.set_alpha(alpha)
            surface.blit(flash_surface, (0, 0))
        
        # Legacy screen flash support
        elif self.state.screen_flash_timer > 0:
            flash_surface = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT))
            flash_surface.fill((255, 255, 255))
            flash_surface.set_alpha(int(self.state.screen_flash_intensity * (self.state.screen_flash_timer / 0.2)))
            surface.blit(flash_surface, (0, 0))
    
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
    
    def _create_fallback_sprite(self, species_id: str) -> pygame.Surface:
        """Erstelle Fallback-Sprite."""
        sprite = pygame.Surface((32, 32))
        sprite.fill((100, 100, 100))
        pygame.draw.rect(sprite, (150, 150, 150), (8, 8, 16, 16))
        return sprite
    
    def _get_status_icon(self, status: str) -> Optional[pygame.Surface]:
        """Hole Status-Icon."""
        # Status icon mapping
        status_icons = {
            "BURN": self._create_status_icon((255, 100, 0), "BR"),      # Orange - Brennen
            "POISON": self._create_status_icon((128, 0, 128), "PS"),    # Purple - Gift
            "PARALYSIS": self._create_status_icon((255, 255, 0), "PR"), # Yellow - Paralyse
            "SLEEP": self._create_status_icon((0, 0, 255), "SL"),       # Blue - Schlaf
            "FREEZE": self._create_status_icon((0, 255, 255), "FR"),    # Cyan - Einfrieren
            "CONFUSION": self._create_status_icon((255, 0, 255), "CF"), # Magenta - Verwirrung
            "FLINCH": self._create_status_icon((255, 128, 128), "FL")   # Light Red - Zurückschrecken
        }
        
        return status_icons.get(status.upper())
    
    def _create_status_icon(self, color: Tuple[int, int, int], text: str) -> pygame.Surface:
        """Erstelle Status-Icon."""
        icon = pygame.Surface((16, 16))
        icon.fill(color)
        
        # Add text
        font = fonts.tiny
        text_surface = font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(8, 8))
        icon.blit(text_surface, text_rect)
        
        return icon
    
    def _get_hp_color(self, ratio: float) -> Tuple[int, int, int]:
        """Hole HP-Farbe basierend auf Verhältnis."""
        if ratio > 0.6:
            return (0, 255, 0)  # Green
        elif ratio > 0.3:
            return (255, 255, 0)  # Yellow
        else:
            return (255, 0, 0)  # Red
    
    def _get_moves_by_category(self, moves: List, category: str) -> List:
        """Hole Moves nach Kategorie."""
        if not moves:
            return []
        
        # Move category mapping basierend auf MoveCategory enum
        category_mapping = {
            "PHYSISCH": ["phys"],  # Physical moves
            "MAGISCH": ["mag"],    # Magical moves  
            "STATUS": ["support"]  # Support/Status moves
        }
        
        valid_categories = category_mapping.get(category.upper(), [])
        filtered_moves = []
        
        for move in moves:
            # Check move category (enum value)
            if hasattr(move, 'category'):
                if hasattr(move.category, 'value'):
                    # MoveCategory enum
                    if move.category.value in valid_categories:
                        filtered_moves.append(move)
                elif move.category in valid_categories:
                    # String category
                    filtered_moves.append(move)
            # Fallback: check by move type for physical/magical
            elif hasattr(move, 'type'):
                if category.upper() == "PHYSISCH" and move.type in ["Feuer", "Wasser", "Erde", "Luft", "Pflanze", "Bestie"]:
                    filtered_moves.append(move)
                elif category.upper() == "MAGISCH" and move.type in ["Energie", "Chaos", "Seuche", "Mystisch", "Gottheit", "Teufel"]:
                    filtered_moves.append(move)
        
        return filtered_moves
    
    def update_hp_bar(self, monster, animated=True):
        """MUSS implementiert sein!"""
        if not monster:
            return
        
        # Initialize hp_updates dict if needed
        if not hasattr(self, 'hp_updates'):
            self.hp_updates = {}
        
        # Get monster ID
        monster_id = getattr(monster, 'id', id(monster))
        
        # Store update for animated rendering
        self.hp_updates[monster_id] = {
            'current': monster.current_hp,
            'max': monster.max_hp,
            'animated': animated,
            'timer': 1.0 if animated else 0.0
        }
        
        # Also add to BattleUIState for integration
        if animated:
            self.state.add_hp_animation(monster_id, monster.current_hp, monster.current_hp, monster.max_hp)
        
        logger.debug(f"HP update queued for {monster.name}: {monster.current_hp}/{monster.max_hp}")
    
    def show_damage_number(self, target, damage: int, is_critical: bool = False) -> None:
        """Show damage number with animation."""
        if not target or damage <= 0:
            return
        
        # Get position based on target
        if target == self.state.player_active:
            pos = self.PLAYER_POS
        else:
            pos = self.ENEMY_POS
        
        # Add random offset
        pos = (pos[0] + random.randint(-10, 10), pos[1] - 20)
        
        # Determine color
        color = (255, 255, 0) if is_critical else (255, 255, 255)
        
        # Add damage number to BattleUIState
        self.state.add_damage_number(damage, pos, color, is_critical)
        logger.debug(f"Damage number created: {damage} {'(CRITICAL)' if is_critical else ''}")
    
    def show_status_effect(self, target, status):
        """MUSS implementiert sein!"""
        if not target or not status:
            return
        
        # Get target ID
        target_id = getattr(target, 'id', id(target))
        
        # Add status effect to BattleUIState
        self.state.add_status_effect(target_id, status, 2.0)
        
        logger.debug(f"Status effect {status} shown for {target.name}")
    
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
        """Update all animations using BattleUIState."""
        self.state.update_animations(dt)
    
    def _get_items_for_category(self, category: str) -> List:
        """Hole Items nach Kategorie."""
        # Placeholder - wird von Menu Manager implementiert
        return []