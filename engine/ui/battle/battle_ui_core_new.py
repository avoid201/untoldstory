"""
Battle UI Core - Schlanke Hauptklasse
Delegiert an modulare Komponenten für bessere Wartbarkeit
"""

import pygame
import logging
from typing import Optional, List, Dict, Any, Tuple

# Setup logger
logger = logging.getLogger(__name__)

# Import config constants
from engine.core.config import LOGICAL_WIDTH, LOGICAL_HEIGHT

# Import modular components
from .core.battle_ui_coordinator import BattleUICoordinator

# Constants
TILE_SIZE = 16
UI_SCALE = 1
FONT_SIZE = 8


class BattleUI:
    """
    Battle UI - Schlanke Hauptklasse.
    ENHANCED: Delegiert an modulare Komponenten.
    """
    
    def __init__(self, game):
        self.game = game
        
        # Initialize coordinator
        self.coordinator = BattleUICoordinator(game)
        
        # Delegate properties to coordinator
        self._delegate_properties()
        
        logger.debug("BattleUI initialized with modular coordinator")
    
    def _delegate_properties(self):
        """Delegate properties to coordinator for backward compatibility."""
        # Battle state
        self.battle_state = self.coordinator.battle_state
        
        # UI components
        self.state = self.coordinator.state
        self.renderer = self.coordinator.renderer
        self.input_handler = self.coordinator.input_handler
        self.menu_manager = self.coordinator.menu_manager
        self.event_manager = self.coordinator.event_manager
        self.scout_display = self.coordinator.scout_display
        
        # Intro sequence
        self.intro_phase = self.coordinator.intro_phase
        self.intro_timer = self.coordinator.intro_timer
        self.intro_duration = self.coordinator.intro_duration
        self.player_slide_progress = self.coordinator.player_slide_progress
        self.enemy_slide_progress = self.coordinator.enemy_slide_progress
    
    # Property accessors for backward compatibility
    @property
    def current_menu_state(self):
        return self.coordinator.current_menu_state
    
    @current_menu_state.setter
    def current_menu_state(self, value):
        self.coordinator.current_menu_state = value
    
    @property
    def selected_option(self):
        return self.coordinator.selected_option
    
    @selected_option.setter
    def selected_option(self, value):
        self.coordinator.selected_option = value
    
    @property
    def selected_move(self):
        return self.coordinator.selected_move
    
    @selected_move.setter
    def selected_move(self, value):
        self.coordinator.selected_move = value
    
    @property
    def selected_item(self):
        return self.coordinator.selected_item
    
    @selected_item.setter
    def selected_item(self, value):
        self.coordinator.selected_item = value
    
    @property
    def selected_team_member(self):
        return self.coordinator.selected_team_member
    
    @selected_team_member.setter
    def selected_team_member(self, value):
        self.coordinator.selected_team_member = value
    
    @property
    def selected_move_category(self):
        return self.coordinator.selected_move_category
    
    @selected_move_category.setter
    def selected_move_category(self, value):
        self.coordinator.selected_move_category = value
    
    @property
    def waiting_for_input(self):
        return self.coordinator.waiting_for_input
    
    @waiting_for_input.setter
    def waiting_for_input(self, value):
        self.coordinator.waiting_for_input = value
    
    @property
    def current_message(self):
        return self.coordinator.current_message
    
    @current_message.setter
    def current_message(self, value):
        self.coordinator.current_message = value
    
    @property
    def message_timer(self):
        return self.coordinator.message_timer
    
    @message_timer.setter
    def message_timer(self, value):
        self.coordinator.message_timer = value
    
    # Main methods - delegate to coordinator
    def init_battle(self, player_team, enemy_team):
        """Initialize battle with teams."""
        return self.coordinator.init_battle(player_team, enemy_team)
    
    def start_battle_intro(self, player_team, enemy_team):
        """Start battle intro sequence."""
        return self.coordinator.start_battle_intro(player_team, enemy_team)
    
    def update(self, dt):
        """Update all UI components."""
        return self.coordinator.update(dt)
    
    def draw(self, surface: pygame.Surface):
        """Draw all UI components."""
        return self.coordinator.draw(surface)
    
    def handle_event(self, event):
        """Handle input events."""
        return self.coordinator.handle_event(event)
    
    # Utility methods - delegate to coordinator
    def _get_hp_color(self, ratio: float) -> Tuple[int, int, int]:
        """Get HP bar color based on ratio."""
        return self.coordinator._get_hp_color(ratio)
    
    def _create_fallback_sprite(self, species_id: str) -> pygame.Surface:
        """Create fallback sprite."""
        return self.coordinator._create_fallback_sprite(species_id)
    
    # Menu management methods
    def get_items_for_category(self, category: str) -> Dict[str, int]:
        """Get items for a specific category."""
        return self.menu_manager.get_items_for_category(category)
    
    def get_moves_by_category(self, moves: List, category: str) -> List:
        """Filter moves by category."""
        return self.menu_manager.get_moves_by_category(moves, category)
    
    def validate_menu_state(self) -> bool:
        """Validate current menu state."""
        return self.menu_manager.validate_menu_state()
    
    def transition_to_menu(self, target_menu, transition_time: float = 0.2) -> None:
        """Smoothly transition to a new menu state."""
        return self.menu_manager.transition_to_menu(target_menu, transition_time)
    
    # Animation methods
    def update_hp_bar(self, target, animated=True):
        """Update HP Bar - SOFORTIGE UI-UPDATES."""
        if not target:
            return
        
        # Sofort UI-State updaten für sofortige Anzeige
        monster_id = getattr(target, 'id', id(target))
        
        # Sofort UI-State updaten:
        self.state.animations["hp_bars"][monster_id] = {
            "active": True,
            "current": target.current_hp,
            "target": target.current_hp,
            "max_hp": target.max_hp,
            "timer": 0.0,
            "duration": 0.8,
            "speed": 2.0
        }
        
        logger.debug(f"HP bar updated immediately: {target.current_hp}/{target.max_hp}")
    
    def show_damage_number(self, target, damage: int, is_critical: bool = False, is_super_effective: bool = False):
        """Show damage number with animation."""
        return self.renderer.show_damage_number(target, damage, is_critical, is_super_effective)
    
    def show_healing_number(self, target, healing: int):
        """Show healing number with animation."""
        return self.renderer.show_healing_number(target, healing)
    
    def show_status_effect(self, target, status):
        """Show status effect animation."""
        return self.renderer.show_status_effect(target, status)
    
    def play_faint_animation(self, monster):
        """Play faint animation for monster."""
        return self.renderer.play_faint_animation(monster)
    
    def play_appear_animation(self, monster):
        """Play appear animation for monster."""
        return self.renderer.play_appear_animation(monster)
    
    def shake_camera(self, intensity: float = 1.0, duration: float = 0.5) -> None:
        """Shake camera with specified intensity and duration."""
        return self.renderer.shake_camera(intensity, duration)
    
    def flash_screen(self, color=(255, 255, 255), duration: float = 0.3) -> None:
        """Flash screen with specified color and duration."""
        return self.renderer.flash_screen(color, duration)
    
    def trigger_screen_flash(self, color: Tuple[int, int, int] = (255, 255, 255), 
                           intensity: float = 0.8, duration: float = 0.3) -> None:
        """Trigger screen flash effect."""
        return self.renderer.trigger_screen_flash(color, intensity, duration)
    
    def trigger_screen_shake(self, intensity: float = 5.0, duration: float = 0.3) -> None:
        """Trigger screen shake effect."""
        return self.renderer.trigger_screen_shake(intensity, duration)
    
    def clear_all_animations(self) -> None:
        """Clear all animations."""
        return self.renderer.clear_all_animations()
