"""
Battle UI Coordinator
Hauptkoordinator für die modulare Battle UI
"""

import pygame
import logging
from typing import Optional, List, Dict, Any, Tuple

# Setup logger
logger = logging.getLogger(__name__)

# Import config constants
from engine.core.config import LOGICAL_WIDTH, LOGICAL_HEIGHT

# Import sub-UI components
from engine.ui.scout_display import ScoutDisplay
from engine.ui.battle_ui_utils import fonts, sprites

# Import battle system components
from engine.systems.battle.battle_state import BattleState

# Use TYPE_CHECKING to avoid circular imports
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from engine.systems.battle.battle_controller import BattleController
    from engine.systems.battle.event_processor import EventProcessor

# Import modular components
from ..battle_ui_state import BattleUIState, BattleMenuState, BattleSprite, DamageNumber
from ..battle_ui_renderer import BattleUIRenderer
from ..battle_ui_input import BattleUIInputHandler
from ..battle_ui_menus import BattleUIMenuManager
from ..battle_ui_events import BattleUIEventManager

# Constants
TILE_SIZE = 16
UI_SCALE = 1
FONT_SIZE = 8


class BattleUICoordinator:
    """
    Battle UI Coordinator - Koordiniert alle UI-Module.
    ENHANCED: Modular aufgebaut für bessere Wartbarkeit.
    """
    
    def __init__(self, game):
        self.game = game
        self.battle_state: Optional[BattleState] = None
        self.battle_controller: Optional['BattleController'] = None
        
        # Initialize UI components
        self.state = BattleUIState()
        self.renderer = BattleUIRenderer(self)
        self.input_handler = BattleUIInputHandler(self)
        self.menu_manager = BattleUIMenuManager(self)
        self.event_manager = BattleUIEventManager(self)
        
        # Scout display
        self.scout_display = ScoutDisplay()
        
        # Battle intro sequence
        self.intro_phase = None
        self.intro_timer = 0.0
        self.intro_duration = 3.0
        self.player_slide_progress = 0.0
        self.enemy_slide_progress = 0.0
        
        logger.debug("BattleUICoordinator initialized with modular components")
    
    # Property accessors for backward compatibility
    @property
    def current_menu_state(self):
        return self.state.menu_state
    
    @current_menu_state.setter
    def current_menu_state(self, value):
        self.state.menu_state = value
    
    @property
    def selected_option(self):
        return self.state.selected_option
    
    @selected_option.setter
    def selected_option(self, value):
        self.state.selected_option = value
    
    @property
    def selected_move(self):
        return self.state.selected_move
    
    @selected_move.setter
    def selected_move(self, value):
        self.state.selected_move = value
    
    @property
    def selected_item(self):
        return self.state.selected_item
    
    @selected_item.setter
    def selected_item(self, value):
        self.state.selected_item = value
    
    @property
    def selected_team_member(self):
        return self.state.selected_team_member
    
    @selected_team_member.setter
    def selected_team_member(self, value):
        self.state.selected_team_member = value
    
    @property
    def selected_move_category(self):
        return self.state.selected_move_category
    
    @selected_move_category.setter
    def selected_move_category(self, value):
        self.state.selected_move_category = value
    
    @property
    def waiting_for_input(self):
        return self.state.waiting_for_input
    
    @waiting_for_input.setter
    def waiting_for_input(self, value):
        self.state.waiting_for_input = value
    
    @property
    def current_message(self):
        return self.state.current_message
    
    @current_message.setter
    def current_message(self, value):
        self.state.current_message = value
    
    @property
    def message_timer(self):
        return self.state.message_timer
    
    @message_timer.setter
    def message_timer(self, value):
        self.state.message_timer = value
    
    def init_battle(self, player_team, enemy_team):
        """
        Initialize battle with teams.
        
        Args:
            player_team: List of player monsters
            enemy_team: List of enemy monsters
        """
        logger.debug(f"Initializing battle: {len(player_team)} vs {len(enemy_team)}")
        
        # Reset UI state
        self.state.reset()
        
        # Initialize scout display
        if enemy_team:
            self.scout_display.show_monster_analysis(enemy_team[0], None)
        
        # Initialize intro sequence
        self.intro_phase = "start"
        self.intro_timer = 0.0
        self.player_slide_progress = 0.0
        self.enemy_slide_progress = 0.0
        
        # Set initial menu state
        self.state.menu_state = BattleMenuState.MAIN
        self.state.waiting_for_input = True
        
        logger.debug("Battle initialized successfully")
    
    def start_battle_intro(self, player_team, enemy_team):
        """
        Start battle intro sequence.
        
        Args:
            player_team: List of player monsters
            enemy_team: List of enemy monsters
        """
        logger.debug("Starting battle intro sequence")
        
        # Initialize intro sequence
        self.intro_phase = "monster_slide_in"
        self.intro_timer = 0.0
        self.intro_duration = 2.0
        
        # Initialize slide animations
        self.player_slide_progress = 0.0
        self.enemy_slide_progress = 0.0
        
        # Set intro state
        self.state.waiting_for_input = False
        
        logger.debug("Battle intro sequence started")
    
    def _start_intro_phase(self, phase: str):
        """Start specific intro phase."""
        self.intro_phase = phase
        self.intro_timer = 0.0
        
        if phase == "monster_slide_in":
            self.intro_duration = 2.0
        elif phase == "hp_bars_appear":
            self.intro_duration = 1.0
        elif phase == "complete":
            self.intro_duration = 0.5
        
        logger.debug(f"Intro phase started: {phase}")
    
    def update_intro_sequence(self, dt: float):
        """Update intro sequence animations."""
        if not self.intro_phase:
            return
        
        self.intro_timer += dt
        
        # Update slide animations
        if self.intro_phase == "monster_slide_in":
            # Player slides in from left
            self.player_slide_progress = min(1.0, self.intro_timer / 1.0)
            
            # Enemy slides in from right (delayed)
            enemy_start_time = 0.5
            if self.intro_timer > enemy_start_time:
                self.enemy_slide_progress = min(1.0, (self.intro_timer - enemy_start_time) / 1.0)
        
        # Check for phase completion
        if self.intro_timer >= self.intro_duration:
            if self.intro_phase == "monster_slide_in":
                self._start_intro_phase("hp_bars_appear")
            elif self.intro_phase == "hp_bars_appear":
                self._start_intro_phase("complete")
            elif self.intro_phase == "complete":
                self.intro_phase = None
                self.state.waiting_for_input = True
                logger.debug("Intro sequence completed")
    
    def draw_intro_sequence(self, surface: pygame.Surface):
        """Draw intro sequence animations."""
        if not self.intro_phase:
            return
        
        # Draw monster slide animations
        self._draw_monster_slide_animation(surface)
        
        # Draw HP bars if in hp_bars_appear phase
        if self.intro_phase in ["hp_bars_appear", "complete"]:
            self._draw_intro_hp_bars(surface)
    
    def _draw_monster_slide_animation(self, surface: pygame.Surface):
        """Draw monster slide-in animations."""
        if not self.battle_state:
            return
        
        # Player monster slide
        if self.battle_state.player_active and self.player_slide_progress > 0:
            # Calculate slide position
            start_x = -100
            end_x = 50
            current_x = start_x + (end_x - start_x) * self.player_slide_progress
            
            # Draw player monster
            sprite = self._get_monster_sprite(self.battle_state.player_active)
            if sprite:
                surface.blit(sprite, (int(current_x), 120))
        
        # Enemy monster slide
        if self.battle_state.enemy_active and self.enemy_slide_progress > 0:
            # Calculate slide position
            start_x = LOGICAL_WIDTH + 100
            end_x = 200
            current_x = start_x + (end_x - start_x) * self.enemy_slide_progress
            
            # Draw enemy monster
            sprite = self._get_monster_sprite(self.battle_state.enemy_active)
            if sprite:
                surface.blit(sprite, (int(current_x), 60))
    
    def _draw_intro_hp_bars(self, surface: pygame.Surface):
        """Draw HP bars during intro sequence."""
        if not self.battle_state:
            return
        
        # Player HP bar
        if self.battle_state.player_active:
            self._draw_intro_hp_bar(surface, self.battle_state.player_active, (20, 180), True)
        
        # Enemy HP bar
        if self.battle_state.enemy_active:
            self._draw_intro_hp_bar(surface, self.battle_state.enemy_active, (180, 40), False)
    
    def _draw_intro_hp_bar(self, surface: pygame.Surface, monster, pos: Tuple[int, int], is_player: bool):
        """Draw single HP bar during intro sequence."""
        if not monster:
            return
        
        # HP bar dimensions
        bar_width = 100
        bar_height = 8
        
        # Calculate HP ratio
        hp_ratio = monster.current_hp / monster.max_hp if monster.max_hp > 0 else 0
        
        # HP bar background
        bg_rect = pygame.Rect(pos[0], pos[1], bar_width, bar_height)
        pygame.draw.rect(surface, (60, 60, 60), bg_rect)
        
        # HP bar fill
        fill_width = int(bar_width * hp_ratio)
        if fill_width > 0:
            fill_rect = pygame.Rect(pos[0], pos[1], fill_width, bar_height)
            hp_color = self._get_hp_color(hp_ratio)
            pygame.draw.rect(surface, hp_color, fill_rect)
        
        # HP bar border
        pygame.draw.rect(surface, (200, 200, 200), bg_rect, 1)
    
    def _get_hp_color(self, ratio: float) -> Tuple[int, int, int]:
        """Get HP bar color based on ratio."""
        if ratio > 0.6:
            return (0, 255, 0)  # Green
        elif ratio > 0.3:
            return (255, 255, 0)  # Yellow
        else:
            return (255, 0, 0)  # Red
    
    def update(self, dt):
        """Update all UI components."""
        # Update intro sequence
        if self.intro_phase:
            self.update_intro_sequence(dt)
            return
        
        # Update components
        self.state.update(dt)
        self.renderer.update(dt)
        self.input_handler.update(dt)
        self.menu_manager.update(dt)
        self.event_manager.update(dt)
    
    def draw(self, surface: pygame.Surface):
        """Draw all UI components."""
        # Draw intro sequence
        if self.intro_phase:
            self.draw_intro_sequence(surface)
            return
        
        # Draw main UI
        self.renderer.render(surface)
    
    def handle_event(self, event):
        """Handle input events."""
        if self.intro_phase:
            return False  # No input during intro
        
        return self.input_handler.handle_event(event)
    
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
        """Create fallback sprite with color based on species_id."""
        sprite = pygame.Surface((32, 32))
        
        # Color based on species_id hash
        color_hash = hash(species_id) % 360
        base_color = pygame.Color(0, 0, 0)
        base_color.hsva = (color_hash, 70, 80, 100)
        
        sprite.fill(base_color)
        
        # Add some pattern
        pygame.draw.rect(sprite, (255, 255, 255), (8, 8, 16, 16), 1)
        pygame.draw.circle(sprite, (255, 255, 255), (16, 16), 4)
        
        return sprite
