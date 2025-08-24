"""
Battle UI system for Untold Story.
Handles all battle interface elements including menus, HP bars, and animations.
"""

import pygame
import math
import random
from dataclasses import dataclass
from typing import Optional, List, Tuple, Dict, Any
from enum import Enum, auto

from engine.core.config import (
    LOGICAL_WIDTH, LOGICAL_HEIGHT, 
    Colors, Fonts, UI
)


class BattleMenuState(Enum):
    """States for the battle menu system."""
    MAIN = auto()          # Fight/Tame/Item/Team/Run
    MOVE_SELECT = auto()   # Selecting a move
    TARGET_SELECT = auto() # Selecting target
    ITEM_SELECT = auto()   # Selecting item
    PARTY_SELECT = auto()  # Selecting party member
    SCOUT = auto()         # Scout monster info
    WAITING = auto()       # Waiting for animations
    MESSAGE = auto()       # Showing battle message


@dataclass
class BattleSprite:
    """Container for a battle sprite."""
    surface: pygame.Surface
    position: Tuple[int, int]
    is_player_side: bool
    shake_offset: Tuple[int, int] = (0, 0)
    flash_timer: float = 0
    fade_alpha: int = 255


@dataclass
class DamageNumber:
    """Floating damage number effect."""
    value: int
    position: Tuple[int, int]
    timer: float
    velocity: Tuple[float, float]
    color: Tuple[int, int, int]
    is_critical: bool = False
    is_super_effective: bool = False


class BattleHUD:
    """Heads-up display for monster information."""
    
    def __init__(self):
        self.font = pygame.font.Font(None, 12)
        self.big_font = pygame.font.Font(None, 16)
        self.small_font = pygame.font.Font(None, 10)
        
    def draw_monster_panel(self, surface: pygame.Surface, monster, position: Tuple[int, int], 
                          is_player_side: bool, is_active: bool = False):
        """Draw a complete monster information panel."""
        try:
            # Validierung des Monster-Objekts
            if not monster:
                # Zeichne leeres Panel bei ungültigem Monster
                self._draw_empty_panel(surface, position, is_player_side, is_active)
                return
            
            # Überprüfe erforderliche Attribute
            if not hasattr(monster, 'name') or not hasattr(monster, 'level'):
                print(f"WARNING: Monster hat ungültige Daten: {monster}")
                self._draw_empty_panel(surface, position, is_player_side, is_active)
                return
            
            x, y = position
            panel_width = 120
            panel_height = 60
            
            # Panel background
            bg_color = Colors.UI_BG if is_active else (30, 30, 40)
            border_color = Colors.UI_SELECTED if is_active else Colors.UI_BORDER
            
            pygame.draw.rect(surface, bg_color, (x, y, panel_width, panel_height))
            pygame.draw.rect(surface, border_color, (x, y, panel_width, panel_height), 2)
            
            # Monster name and level
            name_text = self.font.render(f"{monster.name} Lv.{monster.level}", True, Colors.WHITE)
            surface.blit(name_text, (x + 5, y + 5))
            
            # HP Bar - mit sicheren Zugriffen
            try:
                if hasattr(monster, 'current_hp') and hasattr(monster, 'max_hp'):
                    hp_percent = monster.current_hp / max(1, monster.max_hp)
                    hp_color = self._get_hp_color(hp_percent)
                    
                    hp_bar_width = 110
                    hp_bar_height = 8
                    hp_bar_x = x + 5
                    hp_bar_y = y + 25
                    
                    # HP bar background
                    pygame.draw.rect(surface, (50, 50, 50), (hp_bar_x, hp_bar_y, hp_bar_width, hp_bar_height))
                    
                    # HP bar fill
                    current_hp_width = int(hp_bar_width * hp_percent)
                    pygame.draw.rect(surface, hp_color, (hp_bar_x, hp_bar_y, current_hp_width, hp_bar_height))
                    
                    # HP text
                    hp_text = self.small_font.render(f"HP: {monster.current_hp}/{monster.max_hp}", True, Colors.WHITE)
                    surface.blit(hp_text, (x + 5, y + 35))
                else:
                    # Fallback wenn HP-Daten fehlen
                    hp_text = self.small_font.render("HP: ???", True, Colors.WHITE)
                    surface.blit(hp_text, (x + 5, y + 35))
                    
            except Exception as e:
                print(f"Fehler bei HP-Bar-Zeichnung: {str(e)}")
                # Fallback HP-Anzeige
                hp_text = self.small_font.render("HP: ERROR", True, (255, 0, 0))
                surface.blit(hp_text, (x + 5, y + 35))
            
            # PP Bar (if applicable)
            try:
                if hasattr(monster, 'moves') and monster.moves:
                    # Zeige PP für den ersten Move an
                    first_move = monster.moves[0] if monster.moves else None
                    if first_move and hasattr(first_move, 'pp') and hasattr(first_move, 'max_pp'):
                        pp_percent = first_move.pp / max(1, first_move.max_pp)
                        pp_color = (100, 150, 255) if pp_percent > 0.5 else (255, 150, 100) if pp_percent > 0.2 else (255, 100, 100)
                        
                        pp_bar_width = 110
                        pp_bar_height = 4
                        pp_bar_x = x + 5
                        pp_bar_y = y + 45
                        
                        # PP bar background
                        pygame.draw.rect(surface, (50, 50, 50), (pp_bar_x, pp_bar_y, pp_bar_width, pp_bar_height))
                        
                        # PP bar fill
                        current_pp_width = int(pp_bar_width * pp_percent)
                        pygame.draw.rect(surface, pp_color, (pp_bar_x, pp_bar_y, current_pp_width, pp_bar_height))
                        
                        # PP text
                        pp_text = self.small_font.render(f"PP: {first_move.pp}/{first_move.max_pp}", True, Colors.WHITE)
                        surface.blit(pp_text, (x + 5, y + 50))
                        
            except Exception as e:
                print(f"Fehler bei PP-Bar-Zeichnung: {str(e)}")
                # Keine PP-Anzeige bei Fehlern
                pass
                
        except Exception as e:
            print(f"KRITISCHER FEHLER bei Monster-Panel-Zeichnung: {str(e)}")
            # Zeichne Fehler-Panel
            self._draw_error_panel(surface, position, is_player_side)
    
    def _draw_empty_panel(self, surface: pygame.Surface, position: Tuple[int, int], 
                          is_player_side: bool, is_active: bool):
        """Zeichne leeres Panel wenn kein Monster vorhanden ist."""
        x, y = position
        panel_width = 120
        panel_height = 60
        
        # Graues Panel
        pygame.draw.rect(surface, (50, 50, 50), (x, y, panel_width, panel_height))
        pygame.draw.rect(surface, (100, 100, 100), (x, y, panel_width, panel_height), 2)
        
        # "Kein Monster" Text
        text = self.font.render("Kein Monster", True, (150, 150, 150))
        surface.blit(text, (x + 5, y + 20))
    
    def _draw_error_panel(self, surface: pygame.Surface, position: Tuple[int, int], 
                          is_player_side: bool):
        """Zeichne Fehler-Panel bei kritischen Problemen."""
        x, y = position
        panel_width = 120
        panel_height = 60
        
        # Rotes Fehler-Panel
        pygame.draw.rect(surface, (100, 0, 0), (x, y, panel_width, panel_height))
        pygame.draw.rect(surface, (255, 0, 0), (x, y, panel_width, panel_height), 2)
        
        # "FEHLER" Text
        text = self.font.render("FEHLER", True, (255, 255, 255))
        surface.blit(text, (x + 5, y + 20))
    
    def _get_hp_color(self, hp_percent: float) -> Tuple[int, int, int]:
        """Get HP bar color based on percentage."""
        if hp_percent > 0.5:
            return Colors.HP_HIGH
        elif hp_percent > 0.25:
            return Colors.HP_MED
        else:
            return Colors.HP_LOW
    
    def _get_status_color(self, status: str) -> Tuple[int, int, int]:
        """Get color for status condition."""
        status_colors = {
            'burn': Colors.STATUS_BURN,
            'freeze': Colors.STATUS_FREEZE,
            'paralysis': Colors.STATUS_PARALYSIS,
            'poison': Colors.STATUS_POISON,
            'sleep': Colors.STATUS_SLEEP,
            'confusion': Colors.STATUS_CONFUSION
        }
        return status_colors.get(status.lower(), Colors.YELLOW)


class BattleMenu:
    """Battle menu system with navigation and DQM features."""
    
    def __init__(self):
        self.font = pygame.font.Font(None, 14)
        self.selected_index = 0
        # Erweiterte Menüoptionen mit DQM-Features
        self.menu_options = [
            'Kämpfen', 'Zähmen', 'Items', 
            'Team', 'Spähen', 'Fliehen',
            'Psyche Up', 'Meditieren', 'Einschüchtern'
        ]
        self.menu_pos = (10, LOGICAL_HEIGHT - 100)
        self.menu_width = 280
        self.menu_height = 90
        
    def draw(self, surface: pygame.Surface):
        """Draw the main battle menu with improved design."""
        x, y = self.menu_pos
        
        # Verbessertes UI-Design
        menu_bg = (40, 40, 60)  # Dunklerer, professionellerer Hintergrund
        menu_border = (100, 150, 255)  # Blaue Umrandung statt gelb
        
        # Menu background
        pygame.draw.rect(surface, menu_bg, (x, y, self.menu_width, self.menu_height))
        pygame.draw.rect(surface, menu_border, (x, y, self.menu_width, self.menu_height), 2)
        
        # Menu options in 3x3 Grid
        for i, option in enumerate(self.menu_options):
            color = Colors.UI_SELECTED if i == self.selected_index else Colors.UI_UNSELECTED
            text = self.font.render(option, True, color)
            
            # Bessere Positionierung im 3x3 Grid
            option_x = x + 10 + (i % 3) * 90
            option_y = y + 10 + (i // 3) * 25
            
            surface.blit(text, (option_x, option_y))
            
            # Verbesserte Auswahl-Anzeige
            if i == self.selected_index:
                pygame.draw.rect(surface, Colors.UI_SELECTED, (option_x - 2, option_y - 2, 85, 20), 2)
    
    def handle_input(self, key: str, battle_state=None) -> Optional[str]:
        """Handle menu navigation input with DQM features."""
        try:
            # Handle both string and key input
            if isinstance(key, str):
                if key == 'up':
                    self.selected_index = max(0, self.selected_index - 3)
                elif key == 'down':
                    self.selected_index = min(len(self.menu_options) - 1, self.selected_index + 3)
                elif key == 'left':
                    if self.selected_index % 3 > 0:
                        self.selected_index -= 1
                elif key == 'right':
                    if self.selected_index % 3 < 2 and self.selected_index + 1 < len(self.menu_options):
                        self.selected_index += 1
                elif key == 'confirm':
                    # Map German menu options to English actions including DQM features
                    option = self.menu_options[self.selected_index]
                    if option == 'Kämpfen':
                        return 'fight'
                    elif option == 'Zähmen':
                        return 'tame'
                    elif option == 'Items':
                        return 'item'
                    elif option == 'Team':
                        return 'switch'
                    elif option == 'Spähen':
                        return 'scout'
                    elif option == 'Fliehen':
                        return 'run'
                    elif option == 'Psyche Up':
                        return 'psyche_up'
                    elif option == 'Meditieren':
                        return 'meditate'
                    elif option == 'Einschüchtern':
                        return 'intimidate'
                    else:
                        return option.lower()
            else:
                # Handle pygame key input (fallback)
                if key == pygame.K_UP:
                    self.selected_index = max(0, self.selected_index - 3)
                elif key == pygame.K_DOWN:
                    self.selected_index = min(len(self.menu_options) - 1, self.selected_index + 3)
                elif key == pygame.K_LEFT:
                    if self.selected_index % 3 > 0:
                        self.selected_index -= 1
                elif key == pygame.K_RIGHT:
                    if self.selected_index % 3 < 2 and self.selected_index + 1 < len(self.menu_options):
                        self.selected_index += 1
                elif key == pygame.K_RETURN:
                    # Map German menu options to English actions including DQM features
                    option = self.menu_options[self.selected_index]
                    if option == 'Kämpfen':
                        return 'fight'
                    elif option == 'Zähmen':
                        return 'tame'
                    elif option == 'Items':
                        return 'item'
                    elif option == 'Team':
                        return 'switch'
                    elif option == 'Spähen':
                        return 'scout'
                    elif option == 'Fliehen':
                        return 'run'
                    elif option == 'Psyche Up':
                        return 'psyche_up'
                    elif option == 'Meditieren':
                        return 'meditate'
                    elif option == 'Einschüchtern':
                        return 'intimidate'
                    else:
                        return option.lower()
            
            return None
            
        except Exception as e:
            print(f"Fehler bei der Menu-Input-Behandlung: {str(e)}")
            return None


class MoveSelector:
    """Move selection interface with type-colored display."""
    
    def __init__(self):
        self.font = pygame.font.Font(None, 12)
        self.selected_index = 0
        self.moves = []
        self.menu_pos = (LOGICAL_WIDTH - 150, LOGICAL_HEIGHT - 80)
        self.menu_width = 140
        self.menu_height = 80
        
    def set_moves(self, moves: List):
        """Set available moves for selection."""
        self.moves = moves
        self.selected_index = 0
    
    def draw(self, surface: pygame.Surface):
        """Draw the move selector."""
        if not self.moves:
            return
            
        x, y = self.menu_pos
        
        # Menu background
        pygame.draw.rect(surface, Colors.UI_BG, (x, y, self.menu_width, self.menu_height))
        pygame.draw.rect(surface, Colors.UI_BORDER, (x, y, self.menu_width, self.menu_height), 2)
        
        # Title
        title = self.font.render("Angriffe:", True, Colors.WHITE)
        surface.blit(title, (x + 5, y + 5))
        
        # Move options
        for i, move in enumerate(self.moves):
            if i >= 4:  # Max 4 moves displayed
                break
                
            color = Colors.UI_SELECTED if i == self.selected_index else Colors.UI_UNSELECTED
            
            # Move name with type color
            move_text = self.font.render(move.name, True, color)
            surface.blit(move_text, (x + 10, y + 25 + i * 15))
            
            # PP info
            pp_text = self.font.render(f"PP: {move.current_pp}/{move.max_pp}", True, Colors.LIGHT_BLUE)
            surface.blit(pp_text, (x + 80, y + 25 + i * 15))
            
            # Type indicator
            type_color = self._get_type_color(move.type)
            pygame.draw.rect(surface, type_color, (x + 5, y + 25 + i * 15, 3, 12))
            
            # Selection indicator
            if i == self.selected_index:
                pygame.draw.rect(surface, Colors.UI_SELECTED, (x + 8, y + 23 + i * 15, 120, 16), 1)
    
    def handle_input(self, key: str, battle_state=None) -> Optional[int]:
        """Handle move selection input."""
        try:
            # Handle both string and key input
            if isinstance(key, str):
                if key == 'up':
                    self.selected_index = max(0, self.selected_index - 1)
                elif key == 'down':
                    self.selected_index = min(len(self.moves) - 1, self.selected_index + 1)
                elif key == 'confirm':
                    return self.selected_index
                elif key == 'back':
                    return -1  # Cancel selection
            else:
                # Handle pygame key input (fallback)
                if key == pygame.K_UP:
                    self.selected_index = max(0, self.selected_index - 1)
                elif key == pygame.K_DOWN:
                    self.selected_index = min(len(self.moves) - 1, self.selected_index + 1)
                elif key == pygame.K_RETURN:
                    return self.selected_index
                elif key == pygame.K_ESCAPE:
                    return -1  # Cancel selection
            
            return None
            
        except Exception as e:
            print(f"Fehler bei der Move-Selector-Input-Behandlung: {str(e)}")
            return None
    
    def _get_type_color(self, move_type: str) -> Tuple[int, int, int]:
        """Get color for move type."""
        type_colors = {
            'normal': (150, 150, 150),
            'fire': (255, 100, 50),
            'water': (50, 100, 255),
            'grass': (100, 255, 100),
            'electric': (255, 255, 100),
            'ice': (150, 200, 255),
            'fighting': (200, 100, 100),
            'poison': (200, 100, 200),
            'ground': (200, 150, 100),
            'flying': (150, 200, 255),
            'psychic': (255, 100, 200),
            'bug': (150, 200, 100)
        }
        return type_colors.get(move_type.lower(), Colors.WHITE)


class TargetSelector:
    """Target selection interface with highlighting."""
    
    def __init__(self):
        self.font = pygame.font.Font(None, 12)
        self.selected_index = 0
        self.targets = []
        self.menu_pos = (LOGICAL_WIDTH - 150, LOGICAL_HEIGHT - 80)
        self.menu_width = 140
        self.menu_height = 80
        
    def set_targets(self, targets: List, is_player_side: bool):
        """Set available targets for selection."""
        self.targets = targets
        self.is_player_side = is_player_side
        self.selected_index = 0
    
    def draw(self, surface: pygame.Surface):
        """Draw the target selector."""
        if not self.targets:
            return
            
        x, y = self.menu_pos
        
        # Menu background
        pygame.draw.rect(surface, Colors.UI_BG, (x, y, self.menu_width, self.menu_height))
        pygame.draw.rect(surface, Colors.UI_BORDER, (x, y, self.menu_width, self.menu_height), 2)
        
        # Title
        side_text = "Dein Team:" if self.is_player_side else "Gegner:"
        title = self.font.render(side_text, True, Colors.WHITE)
        surface.blit(title, (x + 5, y + 5))
        
        # Target options
        for i, target in enumerate(self.targets):
            if i >= 4:  # Max 4 targets displayed
                break
                
            color = Colors.UI_SELECTED if i == self.selected_index else Colors.UI_UNSELECTED
            
            # Target name
            target_text = self.font.render(target.name, True, color)
            surface.blit(target_text, (x + 10, y + 25 + i * 15))
            
            # HP indicator
            hp_percent = target.current_hp / target.max_hp
            hp_color = self._get_hp_color(hp_percent)
            pygame.draw.rect(surface, hp_color, (x + 80, y + 25 + i * 15, 40, 8))
            
            # Selection indicator
            if i == self.selected_index:
                pygame.draw.rect(surface, Colors.UI_SELECTED, (x + 8, y + 23 + i * 15, 120, 16), 1)
    
    def handle_input(self, key: str, battle_state=None) -> Optional[int]:
        """Handle target selection input."""
        try:
            # Handle both string and key input
            if isinstance(key, str):
                if key == 'up':
                    self.selected_index = max(0, self.selected_index - 1)
                elif key == 'down':
                    self.selected_index = min(len(self.targets) - 1, self.selected_index + 1)
                elif key == 'confirm':
                    return self.selected_index
                elif key == 'back':
                    return -1  # Cancel selection
            else:
                # Handle pygame key input (fallback)
                if key == pygame.K_UP:
                    self.selected_index = max(0, self.selected_index - 1)
                elif key == pygame.K_DOWN:
                    self.selected_index = min(len(self.targets) - 1, self.selected_index + 1)
                elif key == pygame.K_RETURN:
                    return self.selected_index
                elif key == pygame.K_ESCAPE:
                    return -1  # Cancel selection
            
            return None
            
        except Exception as e:
            print(f"Fehler bei der Target-Selector-Input-Behandlung: {str(e)}")
            return None
    
    def _get_hp_color(self, hp_percent: float) -> Tuple[int, int, int]:
        """Get HP bar color based on percentage."""
        if hp_percent > 0.5:
            return Colors.HP_HIGH
        elif hp_percent > 0.25:
            return Colors.HP_MED
        else:
            return Colors.HP_LOW


class DamageNumbers:
    """Floating damage number effects."""
    
    def __init__(self):
        self.numbers: List[DamageNumber] = []
        
    def add_damage(self, value: int, position: Tuple[int, int], is_critical: bool = False, 
                   is_super_effective: bool = False):
        """Add a new damage number."""
        color = Colors.RED if value > 0 else Colors.GREEN
        if is_critical:
            color = Colors.YELLOW
        elif is_super_effective:
            color = Colors.MAGENTA
            
        number = DamageNumber(
            value=value,
            position=position,
            timer=2.0,  # 2 seconds lifetime
            velocity=(random.uniform(-20, 20), -50),  # Random horizontal, upward
            color=color,
            is_critical=is_critical,
            is_super_effective=is_super_effective
        )
        self.numbers.append(number)
    
    def update(self, dt: float):
        """Update all damage numbers."""
        for number in self.numbers[:]:
            number.timer -= dt
            number.position = (
                number.position[0] + number.velocity[0] * dt,
                number.position[1] + number.velocity[1] * dt
            )
            number.velocity = (
                number.velocity[0] * 0.95,  # Slow down horizontal movement
                number.velocity[1] + 100 * dt  # Gravity
            )
            
            if number.timer <= 0:
                self.numbers.remove(number)
    
    def draw(self, surface: pygame.Surface):
        """Draw all damage numbers."""
        font = pygame.font.Font(None, 16)
        
        for number in self.numbers:
            # Fade out effect
            alpha = int(255 * (number.timer / 2.0))
            color = (*number.color, alpha)
            
            # Create text surface with alpha
            text_surface = font.render(str(number.value), True, color)
            
            # Add effects
            if number.is_critical:
                # Critical hit effect - larger text
                text_surface = pygame.transform.scale(text_surface, 
                    (text_surface.get_width() * 1.5, text_surface.get_height() * 1.5))
            
            if number.is_super_effective:
                # Super effective effect - add glow
                glow_surface = font.render(str(number.value), True, Colors.WHITE)
                surface.blit(glow_surface, (number.position[0] + 1, number.position[1] + 1))
            
            surface.blit(text_surface, number.position)


class BattleUI:
    """Main battle UI manager."""
    
    def __init__(self, game):
        self.game = game
        
        # UI Components
        self.hud = BattleHUD()
        self.menu = BattleMenu()
        self.move_selector = MoveSelector()
        self.target_selector = TargetSelector()
        self.damage_numbers = DamageNumbers()
        
        # Menu state
        self.menu_state = BattleMenuState.MAIN
        self.menu_index = 0
        self.move_index = 0
        self.target_index = 0
        self.item_index = 0
        
        # Battle message system
        self.message_queue: List[str] = []
        self.current_message = ""
        self.message_timer = 0
        self.message_speed = 30  # chars per second
        self.message_progress = 0
        
        # Animation timers
        self.hp_animations: Dict[str, Dict] = {}  # actor_id -> {current, target, speed}
        self.shake_timers: Dict[str, float] = {}
        self.flash_timers: Dict[str, float] = {}
        
        # Visual effects flags
        self.screen_shake = False
        self.shake_intensity = 0
        self.shake_timer = 0
        self.flash_effect = False
        self.flash_timer = 0
        self.status_particle_effects = False
        
        # Battle sprites
        self.sprites: Dict[str, BattleSprite] = {}
        
    def init_battle(self, player_monsters: List, enemy_monsters: List):
        """Initialize UI for a new battle."""
        self.sprites.clear()
        self.hp_animations.clear()
        self.damage_numbers.numbers.clear()
        
        # Position player monsters (right side)
        for i, monster in enumerate(player_monsters):
            if monster and monster.current_hp > 0:
                sprite = self._create_monster_sprite(monster, True)
                sprite.position = (LOGICAL_WIDTH - 60, 80 + i * 30)
                self.sprites[f"player_{i}"] = sprite
                
                # Init HP animation
                self.hp_animations[f"player_{i}"] = {
                    'current': monster.current_hp,
                    'target': monster.current_hp,
                    'max': monster.max_hp,
                    'speed': 2.0
                }
        
        # Position enemy monsters (left side)
        for i, monster in enumerate(enemy_monsters):
            if monster and monster.current_hp > 0:
                sprite = self._create_monster_sprite(monster, False)
                sprite.position = (40, 30 + i * 30)
                self.sprites[f"enemy_{i}"] = sprite
                
                # Init HP animation
                self.hp_animations[f"enemy_{i}"] = {
                    'current': monster.current_hp,
                    'target': monster.current_hp,
                    'max': monster.max_hp,
                    'speed': 2.0
                }
    
    def _create_monster_sprite(self, monster, is_player_side: bool) -> BattleSprite:
        """Create a battle sprite for a monster."""
        try:
            # Versuche, echten Monster-Sprite zu laden
            if hasattr(monster, 'species') and hasattr(monster.species, 'name'):
                sprite_name = monster.species.name
            elif hasattr(monster, 'name'):
                sprite_name = monster.name
            else:
                sprite_name = "default"
            
            # Versuche, Sprite aus Assets zu laden
            sprite_path = f"assets/gfx/monster/{sprite_name}.png"
            try:
                sprite_surface = pygame.image.load(sprite_path)
                # Skaliere auf Battle-Größe (32x32)
                sprite_surface = pygame.transform.scale(sprite_surface, (32, 32))
                print(f"Monster-Sprite geladen: {sprite_path}")
            except Exception as e:
                print(f"Konnte Monster-Sprite nicht laden: {sprite_path}, verwende Platzhalter")
                # Fallback: Erstelle farbigen Platzhalter basierend auf Monster-Typ
                sprite_surface = pygame.Surface((32, 32))
                if hasattr(monster, 'types') and monster.types:
                    # Verwende Typ-basierte Farbe
                    type_colors = {
                        'fire': (255, 100, 50),
                        'water': (50, 100, 255),
                        'grass': (100, 255, 100),
                        'electric': (255, 255, 100),
                        'ice': (150, 200, 255),
                        'fighting': (200, 100, 100),
                        'poison': (200, 100, 200),
                        'ground': (200, 150, 100),
                        'flying': (150, 200, 255),
                        'psychic': (255, 100, 200),
                        'bug': (150, 200, 100),
                        'rock': (150, 150, 100),
                        'ghost': (100, 100, 150),
                        'dragon': (150, 100, 200),
                        'dark': (100, 100, 100),
                        'steel': (150, 150, 200),
                        'fairy': (255, 150, 200)
                    }
                    # Verwende ersten Typ für Farbe
                    first_type = monster.types[0].lower() if isinstance(monster.types[0], str) else str(monster.types[0]).lower()
                    color = type_colors.get(first_type, (100, 100, 100))
                else:
                    # Standard-Farbe basierend auf Seite
                    color = (100, 150, 255) if is_player_side else (255, 100, 100)
                
                sprite_surface.fill(color)
                
                # Füge Monster-Initialen hinzu
                font = pygame.font.Font(None, 16)
                if hasattr(monster, 'name') and monster.name:
                    initial = monster.name[0].upper()
                else:
                    initial = "?"
                
                text = font.render(initial, True, (255, 255, 255))
                text_rect = text.get_rect(center=(16, 16))
                sprite_surface.blit(text, text_rect)
        
        except Exception as e:
            print(f"Fehler beim Erstellen des Monster-Sprites: {str(e)}")
            # Fallback: Einfacher farbiger Block
            sprite_surface = pygame.Surface((32, 32))
            sprite_surface.fill((100, 100, 100) if is_player_side else (150, 100, 100))
        
        return BattleSprite(
            surface=sprite_surface,
            position=(0, 0),
            is_player_side=is_player_side
        )
    
    def update(self, dt: float):
        """Update UI animations and timers."""
        # Update damage numbers
        self.damage_numbers.update(dt)
        
        # Update HP animations
        for actor_id, anim in self.hp_animations.items():
            if anim['current'] != anim['target']:
                diff = anim['target'] - anim['current']
                anim['current'] += diff * anim['speed'] * dt
                
                if abs(diff) < 1:
                    anim['current'] = anim['target']
        
        # Update screen shake
        if self.screen_shake and self.shake_timer > 0:
            self.shake_timer -= dt
            if self.shake_timer <= 0:
                self.screen_shake = False
                self.shake_intensity = 0
        
        # Update flash effect
        if self.flash_effect and self.flash_timer > 0:
            self.flash_timer -= dt
            if self.flash_timer <= 0:
                self.flash_effect = False
        
        # Update message display
        if self.message_timer > 0:
            self.message_timer -= dt
            if self.message_timer <= 0:
                self._next_message()
    
    def draw(self, surface: pygame.Surface):
        """Draw the complete battle UI."""
        try:
            # Apply screen shake offset
            shake_offset = (0, 0)
            if self.screen_shake:
                shake_offset = (
                    random.randint(-self.shake_intensity, self.shake_intensity),
                    random.randint(-self.shake_intensity, self.shake_intensity)
                )
            
            # Draw battle sprites
            for sprite in self.sprites.values():
                if sprite and hasattr(sprite, 'surface') and hasattr(sprite, 'position'):
                    sprite_surface = sprite.surface.copy()
                    
                    # Apply effects
                    if hasattr(sprite, 'shake_offset') and sprite.shake_offset != (0, 0):
                        sprite_surface = pygame.transform.rotate(sprite_surface, 
                            random.randint(-5, 5))
                    
                    if hasattr(sprite, 'flash_timer') and sprite.flash_timer > 0:
                        sprite_surface.set_alpha(128 + int(127 * math.sin(sprite.flash_timer * 10)))
                    
                    # Draw with shake offset
                    pos = (sprite.position[0] + shake_offset[0], sprite.position[1] + shake_offset[1])
                    surface.blit(sprite_surface, pos)
            
            # Draw HUD panels
            self._draw_hud_panels(surface)
            
            # Draw UI based on current state
            if self.menu_state == BattleMenuState.MAIN:
                self.menu.draw(surface)
            elif self.menu_state == BattleMenuState.MOVE_SELECT:
                self.move_selector.draw(surface)
            elif self.menu_state == BattleMenuState.TARGET_SELECT:
                self.target_selector.draw(surface)
            
            # Draw damage numbers
            self.damage_numbers.draw(surface)
            
            # Draw message box
            self._draw_message_box(surface)
            
            # Draw flash effect
            if self.flash_effect:
                flash_surface = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT))
                flash_surface.set_alpha(int(100 * (self.flash_timer / 0.5)))
                flash_surface.fill(Colors.WHITE)
                surface.blit(flash_surface, (0, 0))
                
        except Exception as e:
            print(f"Fehler beim Zeichnen der Battle UI: {str(e)}")
    
    def _draw_hud_panels(self, surface: pygame.Surface):
        """Draw HUD panels for all monsters."""
        try:
            # Draw player monster panels
            for i, (actor_id, sprite) in enumerate(self.sprites.items()):
                if actor_id.startswith('player_'):
                    monster = self._get_monster_by_id(actor_id)
                    if monster:
                        self.hud.draw_monster_panel(surface, monster, 
                            (LOGICAL_WIDTH - 130, 60 + i * 70), True, i == 0)
            
            # Draw enemy monster panels
            for i, (actor_id, sprite) in enumerate(self.sprites.items()):
                if actor_id.startswith('enemy_'):
                    monster = self._get_monster_by_id(actor_id)
                    if monster:
                        self.hud.draw_monster_panel(surface, monster, 
                            (10, 10 + i * 70), False, i == 0)
                            
        except Exception as e:
            print(f"Fehler beim Zeichnen der HUD-Panels: {str(e)}")
    
    def _draw_message_box(self, surface: pygame.Surface):
        """Draw the battle message box."""
        try:
            if not self.current_message:
                return
                
            box_height = 40
            box_y = LOGICAL_HEIGHT - box_height - 10
            
            # Message box background
            pygame.draw.rect(surface, Colors.UI_BG, (10, box_y, LOGICAL_WIDTH - 20, box_height))
            pygame.draw.rect(surface, Colors.UI_BORDER, (10, box_y, LOGICAL_WIDTH - 20, box_height), 2)
            
            # Message text
            font = pygame.font.Font(None, 14)
            text = font.render(self.current_message, True, Colors.WHITE)
            surface.blit(text, (20, box_y + 10))
            
        except Exception as e:
            print(f"Fehler beim Zeichnen der Message Box: {str(e)}")
    
    def _get_monster_by_id(self, actor_id: str):
        """Get monster instance by actor ID."""
        # This would need to be implemented based on your monster data structure
        # For now, return a placeholder
        return None
    
    def handle_input(self, action: str, battle_state=None) -> Optional[Dict]:
        """Handle input based on current menu state."""
        try:
            print(f"BattleUI handling input: {action} in state {self.menu_state}")
            
            if self.menu_state == BattleMenuState.MAIN:
                result = self.menu.handle_input(action)
                if result:
                    print(f"Menu selection: {result}")
                    if result == 'fight':
                        self.menu_state = BattleMenuState.MOVE_SELECT
                        self.move_index = 0
                        return {'action': 'menu_select', 'option': result}
                    elif result == 'run':
                        return {'action': 'flee', 'actor': battle_state.player_active if battle_state else None}
                    elif result == 'item':
                        return {'action': 'item', 'actor': battle_state.player_active if battle_state else None}
                    elif result == 'switch':
                        return {'action': 'switch', 'actor': battle_state.player_active if battle_state else None}
                    elif result == 'psyche_up':
                        return {'action': 'psyche_up', 'actor': battle_state.player_active if battle_state else None}
                    elif result == 'meditate':
                        return {'action': 'meditate', 'actor': battle_state.player_active if battle_state else None}
                    elif result == 'intimidate':
                        return {'action': 'intimidate', 'actor': battle_state.player_active if battle_state else None}
                    elif result == 'tame':
                        return {'action': 'tame', 'actor': battle_state.player_active if battle_state else None}
                    elif result == 'scout':
                        return {'action': 'scout', 'actor': battle_state.player_active if battle_state else None}
            
            elif self.menu_state == BattleMenuState.MOVE_SELECT:
                result = self.move_selector.handle_input(action)
                if result is not None:
                    if result == -1:  # Cancel
                        self.menu_state = BattleMenuState.MAIN
                        return {'action': 'cancel'}
                    else:
                        # Get selected move
                        if battle_state and hasattr(battle_state, 'player_active'):
                            moves = battle_state.player_active.moves
                            if moves and result < len(moves):
                                move = moves[result]
                                print(f"Selected move: {move.name if hasattr(move, 'name') else 'Unknown'}")
                                self.menu_state = BattleMenuState.MAIN
                                return {
                                    'action': 'attack', 
                                    'actor': battle_state.player_active,
                                    'move_index': result,
                                    'move': move,
                                    'target': battle_state.enemy_active
                                }
                        return {
                            'action': 'attack', 
                            'move_index': result,
                            'actor': battle_state.player_active if battle_state else None,
                            'target': battle_state.enemy_active if battle_state else None
                        }
            
            elif self.menu_state == BattleMenuState.TARGET_SELECT:
                result = self.target_selector.handle_input(action)
                if result is not None:
                    if result == -1:  # Cancel
                        self.menu_state = BattleMenuState.MOVE_SELECT
                        return {'action': 'cancel'}
                    else:
                        return {'action': 'target_select', 'target_index': result}
            
            return None
            
        except Exception as e:
            print(f"Fehler bei der Input-Behandlung: {str(e)}")
            return None
    
    def add_message(self, message: str, wait: bool = True):
        """Add a message to the display queue."""
        self.message_queue.append(message)
        if not self.current_message and wait:
            self._next_message()
    
    def show_message(self, message: str):
        """Alias for add_message."""
        self.add_message(message)

    def _next_message(self):
        """Show next message in queue."""
        if self.message_queue:
            self.current_message = self.message_queue.pop(0)
            self.message_timer = len(self.current_message) / self.message_speed
        else:
            self.current_message = ""
    
    def trigger_screen_shake(self, intensity: int = 5, duration: float = 0.3):
        """Trigger screen shake effect."""
        self.screen_shake = True
        self.shake_intensity = intensity
        self.shake_timer = duration
    
    def trigger_flash_effect(self, duration: float = 0.5):
        """Trigger screen flash effect."""
        self.flash_effect = True
        self.flash_timer = duration
    
    def add_damage_number(self, value: int, position: Tuple[int, int], 
                         is_critical: bool = False, is_super_effective: bool = False):
        """Add a damage number effect."""
        self.damage_numbers.add_damage(value, position, is_critical, is_super_effective)
    
    def set_menu_state(self, state: BattleMenuState):
        """Change the current menu state."""
        self.menu_state = state
        
        # Reset indices when changing states
        if state == BattleMenuState.MOVE_SELECT:
            self.move_index = 0
        elif state == BattleMenuState.TARGET_SELECT:
            self.target_index = 0
