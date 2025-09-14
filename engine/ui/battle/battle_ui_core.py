"""
Battle UI Core - Hauptklasse für modulare Battle UI
Zerlegt aus der monolithischen battle_ui.py (2029 Zeilen → ~400 Zeilen)

Verantwortlichkeiten:
- BattleUI Hauptklasse mit Koordination
- Initialisierung und Reset
- Delegation an spezialisierte Module
- Event-Handling Koordination
"""

import pygame
import logging
from typing import Optional, List, Dict, Any, Tuple

# Setup logger
logger = logging.getLogger(__name__)

# Import the config constants
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
from .battle_ui_state import BattleUIState, BattleMenuState, BattleSprite, DamageNumber
from .battle_ui_renderer import BattleUIRenderer
from .battle_ui_input import BattleUIInputHandler
from .battle_ui_menus import BattleUIMenuManager
from .battle_ui_events import BattleUIEventManager

# Constants
TILE_SIZE = 16
UI_SCALE = 1
FONT_SIZE = 8


class BattleUI:
    """
    Hauptklasse für modulare Battle UI.
    
    Koordiniert alle UI-Komponenten und delegiert an spezialisierte Module:
    - BattleUIRenderer: Alle draw_* Methoden
    - BattleUIInputHandler: Input handling
    - BattleUIMenuManager: Menu-spezifische Logic
    - BattleUIState: State management
    """
    
    def __init__(self, game):
        """Initialisiere Battle UI mit modularen Komponenten."""
        self.game = game
        self.surface = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT))
        
        # Battle state
        self.battle_state: Optional[BattleState] = None
        self.battle_controller: Optional['BattleController'] = None
        self.event_processor: Optional['EventProcessor'] = None
        
        # Animation and effects (Core-specific, not in state)
        self.damage_numbers: List[DamageNumber] = []
        self.message_queue: List[str] = []
        
        # Monster sprites
        self.player_sprite: Optional[BattleSprite] = None
        self.enemy_sprite: Optional[BattleSprite] = None
        
        # Pending action
        self.pending_action: Optional[Dict[str, Any]] = None
        
        # BATTLE INTRO SYSTEM
        self.intro_state = {
            'phase': 'none',  # none, fade_in, message, monster_slide, hp_bars, complete
            'timer': 0.0,
            'fade_alpha': 0,
            'monster_slide_progress': 0.0,
            'hp_bars_visible': False,
            'intro_complete': False
        }
        
        # Initialize state FIRST
        self.state = BattleUIState()
        
        # Initialize modular components
        self.renderer = BattleUIRenderer(self)
        self.input_handler = BattleUIInputHandler(self)
        self.menu_manager = BattleUIMenuManager(self)
        self.event_manager = BattleUIEventManager(self)
        
        # Initialize sub-UI components
        self.scout_display = ScoutDisplay()
        
        # Demo inventory for testing
        self.demo_inventory = {}
        
        logger.info("Battle UI Core initialized with modular components")
    
    # DEPRECATED: Removed on 2025-01-09 - _pending_action property no longer used
    
    # State Properties - delegieren an self.state
    @property
    def current_menu_state(self):
        """Menu state property."""
        return self.state.menu_state
    
    @current_menu_state.setter
    def current_menu_state(self, value):
        """Menu state setter."""
        self.state.menu_state = value
    
    @property
    def selected_option(self):
        """Selected option property."""
        return self.state.selected_option
    
    @selected_option.setter
    def selected_option(self, value):
        """Selected option setter."""
        self.state.selected_option = value
    
    @property
    def selected_move(self):
        """Selected move property."""
        return self.state.selected_move
    
    @selected_move.setter
    def selected_move(self, value):
        """Selected move setter."""
        self.state.selected_move = value
    
    @property
    def selected_item(self):
        """Selected item property."""
        return self.state.selected_item
    
    @selected_item.setter
    def selected_item(self, value):
        """Selected item setter."""
        self.state.selected_item = value
    
    @property
    def selected_team_member(self):
        """Selected team member property."""
        return self.state.selected_team_member
    
    @selected_team_member.setter
    def selected_team_member(self, value):
        """Selected team member setter."""
        self.state.selected_team_member = value
    
    @property
    def selected_move_category(self):
        """Selected move category property."""
        return self.state.current_move_category
    
    @selected_move_category.setter
    def selected_move_category(self, value):
        """Selected move category setter."""
        self.state.current_move_category = value
    
    @property
    def waiting_for_input(self):
        """Waiting for input property."""
        return self.state.message_wait
    
    @waiting_for_input.setter
    def waiting_for_input(self, value):
        """Waiting for input setter."""
        self.state.message_wait = value
    
    @property
    def current_message(self):
        """Current message property."""
        return self.state.current_message
    
    @current_message.setter
    def current_message(self, value):
        """Current message setter."""
        self.state.current_message = value
    
    @property
    def message_timer(self):
        """Message timer property."""
        return self.state.message_timer
    
    @message_timer.setter
    def message_timer(self, value):
        """Message timer setter."""
        self.state.message_timer = value
    
    def init_battle(self, player_team, enemy_team):
        """Initialisiere Battle mit Teams - ENHANCED Event-Handler Registration."""
        logger.info(f"Initializing battle: {len(player_team)} vs {len(enemy_team)}")
        
        # Reset UI state
        self.reset()
        
        # CRITICAL: Register event handlers EARLY
        if self.event_processor:
            self.connect_event_handlers(self.event_processor)
            logger.info("✓ Event handlers registered early in init_battle()")
        else:
            logger.warning("⚠️ No event_processor available for early registration")
        
        # Set up battle state
        # Battle state wird später initialisiert
        # self.battle_state = BattleState(player_team, enemy_team)
        
        # Initialize monster sprites
        if self.state.player_active:
            self.player_sprite = BattleSprite(
                surface=self._get_monster_sprite(self.state.player_active),
                position=self._get_monster_position(self.state.player_active, True),
                is_player_side=True
            )
        
        if self.state.enemy_active:
            self.enemy_sprite = BattleSprite(
                surface=self._get_monster_sprite(self.state.enemy_active),
                position=self._get_monster_position(self.state.enemy_active, False),
                is_player_side=False
            )
        
        # Initialize demo inventory
        self.init_demo_inventory()
        
        # Reset to main menu
        self.reset_to_main_menu()
        
        logger.info("✓ Battle initialization complete with early event handler registration")

    def start_battle_intro(self, player_team, enemy_team):
        """Starte Battle-Intro-Sequenz mit Animationen."""
        logger.info("🎬 Starting Battle Intro Sequence")
        
        # Reset intro state
        self.intro_state = {
            'phase': 'fade_in',
            'timer': 0.0,
            'fade_alpha': 0,
            'monster_slide_progress': 0.0,
            'hp_bars_visible': False,
            'intro_complete': False
        }
        
        # Set battle state
        self.battle_state = BattleState(player_team, enemy_team)
        
        # Initialize monster sprites for intro
        if player_team and len(player_team) > 0:
            self.player_sprite = BattleSprite(
                surface=self._get_monster_sprite(player_team[0]),
                position=self._get_monster_position(player_team[0], True),
                is_player_side=True
            )
        
        if enemy_team and len(enemy_team) > 0:
            self.enemy_sprite = BattleSprite(
                surface=self._get_monster_sprite(enemy_team[0]),
                position=self._get_monster_position(enemy_team[0], False),
                is_player_side=False
            )
        
        # Start intro sequence
        self._start_intro_phase('fade_in')
        
        logger.info("✅ Battle Intro started")

    def _start_intro_phase(self, phase: str):
        """Starte neue Intro-Phase."""
        self.intro_state['phase'] = phase
        self.intro_state['timer'] = 0.0
        
        if phase == 'fade_in':
            self.intro_state['fade_alpha'] = 0
        elif phase == 'message':
            # Show intro message
            enemy_name = self.battle_state.enemy_active.name if self.battle_state.enemy_active else "Unbekanntes Monster"
            self.add_message(f"Ein wildes {enemy_name} erscheint!", duration=2.0, priority="important")
        elif phase == 'monster_slide':
            self.intro_state['monster_slide_progress'] = 0.0
        elif phase == 'hp_bars':
            self.intro_state['hp_bars_visible'] = True
        elif phase == 'complete':
            self.intro_state['intro_complete'] = True
            self.reset_to_main_menu()
        
        logger.debug(f"Intro phase started: {phase}")

    def update_intro_sequence(self, dt: float):
        """Update Battle-Intro-Sequenz."""
        if self.intro_state['phase'] == 'none' or self.intro_state['intro_complete']:
            return
        
        self.intro_state['timer'] += dt
        
        if self.intro_state['phase'] == 'fade_in':
            # Fade in (0.2s) - FASTER
            progress = min(1.0, self.intro_state['timer'] / 0.2)
            self.intro_state['fade_alpha'] = int(255 * progress)
            
            if progress >= 1.0:
                self._start_intro_phase('message')
        
        elif self.intro_state['phase'] == 'message':
            # Message display (0.5s) - FASTER
            if self.intro_state['timer'] >= 0.5:
                self._start_intro_phase('monster_slide')
        
        elif self.intro_state['phase'] == 'monster_slide':
            # Monster slide-in (0.3s) - FASTER
            progress = min(1.0, self.intro_state['timer'] / 0.3)
            self.intro_state['monster_slide_progress'] = progress
            
            if progress >= 1.0:
                self._start_intro_phase('hp_bars')
        
        elif self.intro_state['phase'] == 'hp_bars':
            # HP bars appear (0.2s) - FASTER
            if self.intro_state['timer'] >= 0.2:
                self._start_intro_phase('complete')

    def draw_intro_sequence(self, surface: pygame.Surface):
        """Zeichne Battle-Intro-Sequenz."""
        if self.intro_state['phase'] == 'none' or self.intro_state['intro_complete']:
            return
        
        # Draw fade overlay
        if self.intro_state['phase'] in ['fade_in', 'message', 'monster_slide', 'hp_bars']:
            fade_surface = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT))
            fade_surface.fill((0, 0, 0))
            fade_surface.set_alpha(255 - self.intro_state['fade_alpha'])
            surface.blit(fade_surface, (0, 0))
        
        # Draw monster slide-in animation
        if self.intro_state['phase'] in ['monster_slide', 'hp_bars', 'complete']:
            self._draw_monster_slide_animation(surface)
        
        # Draw HP bars if visible
        if self.intro_state['hp_bars_visible']:
            self._draw_intro_hp_bars(surface)

    def _draw_monster_slide_animation(self, surface: pygame.Surface):
        """Zeichne Monster-Slide-In-Animation."""
        progress = self.intro_state['monster_slide_progress']
        
        # Player monster slides in from left
        if self.player_sprite:
            original_pos = self._get_monster_position(self.battle_state.player_active, True)
            slide_pos = (
                int(original_pos[0] - (1 - progress) * 100),  # Start 100px left
                original_pos[1]
            )
            
            # Apply slide animation
            sprite_copy = self.player_sprite.surface.copy()
            sprite_copy.set_alpha(int(255 * progress))  # Fade in
            surface.blit(sprite_copy, slide_pos)
        
        # Enemy monster slides in from right
        if self.enemy_sprite:
            original_pos = self._get_monster_position(self.battle_state.enemy_active, False)
            slide_pos = (
                int(original_pos[0] + (1 - progress) * 100),  # Start 100px right
                original_pos[1]
            )
            
            # Apply slide animation
            sprite_copy = self.enemy_sprite.surface.copy()
            sprite_copy.set_alpha(int(255 * progress))  # Fade in
            surface.blit(sprite_copy, slide_pos)

    def _draw_intro_hp_bars(self, surface: pygame.Surface):
        """Zeichne HP-Bars für Intro."""
        # Player HP bar
        if self.battle_state.player_active:
            self._draw_intro_hp_bar(surface, self.battle_state.player_active, (20, 160), True)
        
        # Enemy HP bar
        if self.battle_state.enemy_active:
            self._draw_intro_hp_bar(surface, self.battle_state.enemy_active, (180, 20), False)

    def _draw_intro_hp_bar(self, surface: pygame.Surface, monster, pos: Tuple[int, int], is_player: bool):
        """Zeichne einzelne HP-Bar für Intro."""
        # Panel background
        panel_rect = pygame.Rect(pos[0], pos[1], 100, 32)
        pygame.draw.rect(surface, (40, 40, 40), panel_rect)
        pygame.draw.rect(surface, (100, 100, 100), panel_rect, 1)
        
        # Monster name
        name_font = fonts.monster_name
        name_text = name_font.render(monster.name, True, (255, 255, 255))
        surface.blit(name_text, (pos[0] + 4, pos[1] + 2))
        
        # Level
        level_font = fonts.normal
        level_text = level_font.render(f"Lv.{monster.level}", True, (255, 255, 255))
        surface.blit(level_text, (pos[0] + 80, pos[1] + 2))
        
        # HP Bar
        hp_ratio = monster.current_hp / monster.max_hp if monster.max_hp > 0 else 0
        hp_color = self._get_hp_color(hp_ratio)
        hp_bar_rect = pygame.Rect(pos[0] + 4, pos[1] + 12, 92, 8)
        pygame.draw.rect(surface, (20, 20, 20), hp_bar_rect)
        pygame.draw.rect(surface, hp_color, (pos[0] + 4, pos[1] + 12, int(92 * hp_ratio), 8))
        
        # HP Text
        hp_font = fonts.small
        hp_text = hp_font.render(f"{monster.current_hp}/{monster.max_hp}", True, (255, 255, 255))
        surface.blit(hp_text, (pos[0] + 4, pos[1] + 22))

    def _get_hp_color(self, ratio: float) -> Tuple[int, int, int]:
        """Hole HP-Farbe basierend auf Verhältnis."""
        if ratio > 0.6:
            return (0, 255, 0)  # Green
        elif ratio > 0.3:
            return (255, 255, 0)  # Yellow
        else:
            return (255, 0, 0)  # Red
    
    def update(self, dt):
        """Update Battle UI und alle Komponenten - BEREINIGT mit Event-Processing."""
        # Update Battle Intro Sequence
        self.update_intro_sequence(dt)
        
        # BEHOBEN: Synchronisiere UI State mit Battle State
        self._sync_ui_state_with_battle_state()
        
        # Update animations and effects through BattleUIState
        self.state.update_animations(dt)
        self.state.update_message_timer(dt)
        
        # CRITICAL: Update message timer in core as well
        if self.message_timer > 0:
            self.message_timer -= dt
            if self.message_timer <= 0:
                self.message_timer = 0
                # Check if we should return to main menu
                if not self.state.has_pending_messages():
                    self.state.menu_state = BattleMenuState.MAIN
                    self.waiting_for_input = True
        
        # Process events from battle system
        if self.battle_controller and hasattr(self.battle_controller, 'event_processor'):
            try:
                # Process all pending events
                self.battle_controller.event_processor.process_events()
            except Exception as e:
                logger.error(f"Error processing events: {e}")
        
        # Update modular components
        self.renderer.update_animations(dt)
        self.input_handler.update(dt)
        self.menu_manager.update(dt)
        
        # Update sub-UI components
        self.scout_display.update(dt)
    
    def _sync_ui_state_with_battle_state(self):
        """BEHOBEN: Synchronisiere UI State mit Battle State für korrekte Move-Anzeige."""
        if self.battle_state:
            # Synchronisiere aktive Monster
            if self.battle_state.player_active and not self.state.player_active:
                self.state.player_active = self.battle_state.player_active
                logger.debug(f"Synced player_active: {self.state.player_active.name}")
            
            if self.battle_state.enemy_active and not self.state.enemy_active:
                self.state.enemy_active = self.battle_state.enemy_active
                logger.debug(f"Synced enemy_active: {self.state.enemy_active.name}")
            
            # Synchronisiere Teams
            if self.battle_state.player_team and not self.state.player_team:
                self.state.player_team = self.battle_state.player_team
                logger.debug(f"Synced player_team: {len(self.state.player_team)} monsters")
            
            if self.battle_state.enemy_team and not self.state.enemy_team:
                self.state.enemy_team = self.battle_state.enemy_team
                logger.debug(f"Synced enemy_team: {len(self.state.enemy_team)} monsters")
    
    def draw(self, surface: pygame.Surface):
        """Zeichne Battle UI - delegiert an Renderer."""
        # Draw Battle Intro Sequence if active
        if not self.intro_state['intro_complete']:
            self.draw_intro_sequence(surface)
        else:
            # Normal battle UI
            self.renderer.draw(surface)
    
    def reset(self):
        """Reset Battle UI zu initialem Zustand."""
        self.state.reset()
        
        # Clear core-specific effects
        self.damage_numbers.clear()
        self.message_queue.clear()
        
        # Clear sprites
        self.player_sprite = None
        self.enemy_sprite = None
        
        # Reset pending action
        self.pending_action = None
        
        logger.info("Battle UI reset complete")
    
    def _get_monster_sprite(self, monster):
        """Get monster sprite."""
        try:
            if not monster or not hasattr(monster, 'species'):
                return self._create_fallback_sprite("unknown")
            
            # Try to get sprite from sprites utility
            species_id = monster.species.id if hasattr(monster, 'species') and hasattr(monster.species, 'id') else str(id(monster))
            sprite = sprites.get_monster_sprite(species_id)
            if sprite:
                # Ensure sprite is correct size
                if sprite.get_size() != (32, 32):
                    sprite = pygame.transform.scale(sprite, (32, 32))
                return sprite
            
            # Try alternative sprite loading methods
            sprite = self._load_sprite_by_id(species_id)
            if sprite:
                return sprite
            
            # Create fallback sprite
            return self._create_fallback_sprite(species_id)
                
        except Exception as e:
            species_id = monster.species.id if hasattr(monster, 'species') and hasattr(monster.species, 'id') else 'unknown'
            logger.warning(f"Could not load sprite for {species_id}: {e}")
            return self._create_fallback_sprite("error")
    
    def _load_sprite_by_id(self, species_id: str) -> Optional[pygame.Surface]:
        """Lade Sprite nach Species ID."""
        try:
            # Try different sprite loading strategies
            sprite_paths = [
                f"assets/gfx/monsters/{species_id.lower()}.png",
                f"assets/gfx/monsters/{species_id.upper()}.png",
                f"assets/gfx/monsters/{species_id}.png",
                f"assets/gfx/creatures/{species_id.lower()}.png"
            ]
            
            for path in sprite_paths:
                try:
                    sprite = pygame.image.load(path)
                    # Resize to standard battle sprite size
                    sprite = pygame.transform.scale(sprite, (32, 32))
                    # Convert to display format if possible
                    try:
                        return sprite.convert_alpha()
                    except:
                        return sprite.convert()
                except pygame.error:
                    continue
            
            return None
            
        except Exception as e:
            logger.debug(f"Sprite loading failed for {species_id}: {e}")
            return None
    
    def _create_fallback_sprite(self, species_id: str) -> pygame.Surface:
        """Erstelle Fallback-Sprite."""
        sprite = pygame.Surface((32, 32))
        
        # Color based on species_id hash
        color_hash = hash(species_id) % 360
        base_color = pygame.Color(0, 0, 0)
        base_color.hsva = (color_hash, 70, 80, 100)
        
        sprite.fill(base_color)
        
        # Add simple shape
        center = (16, 16)
        pygame.draw.circle(sprite, (255, 255, 255), center, 12, 2)
        pygame.draw.circle(sprite, (200, 200, 200), center, 8, 1)
        
        # Add species_id text
        try:
            font = fonts.tiny
            text = font.render(species_id[:3].upper(), True, (255, 255, 255))
            text_rect = text.get_rect(center=center)
            sprite.blit(text, text_rect)
        except:
            pass
        
        return sprite
    
    # Legacy _get_monster_position removed - using enhanced version below
    
    def handle_input(self, action, battle_state=None):
        """Handle Input - delegiert an Input Handler."""
        result = self.input_handler.handle_input(action, battle_state)
        if result is True:
            # Input was handled but no action was created
            return True
        elif result is None:
            # Input was not handled
            return False
        else:
            # Input was handled and action was created
            return True
    
    def handle_event(self, event):
        """Handle pygame event - delegiert an Input Handler."""
        # Convert pygame event to action string
        action = self._convert_event_to_action(event)
        if action:
            result = self.input_handler.handle_input(action, self.battle_state)
            if result is True:
                # Input was handled but no action was created
                return True
            elif result is None:
                # Input was not handled
                return False
            else:
                # Input was handled and action was created
                return True
        return False
    
    def _convert_event_to_action(self, event):
        """Convert pygame event to action string."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                return "up"
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                return "down"
            elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                return "left"
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                return "right"
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                return "confirm"
            elif event.key == pygame.K_ESCAPE:
                return "cancel"
        return None
    
    def connect_event_handlers(self, event_processor: 'EventProcessor') -> None:
        """Verbinde Event Handler für Battle Events - ENHANCED UI INTEGRATION."""
        self.event_processor = event_processor
        
        # Import EventType for registration
        from engine.systems.battle.events.event_types import EventType
        
        # Register all UI event handlers
        self._register_ui_event_handlers(event_processor)
        
        logger.info("✓ UI Event Handlers registered successfully")
    
    def _register_ui_event_handlers(self, event_processor: 'EventProcessor') -> None:
        """Registriere alle UI Event Handler für smooth Animationen."""
        # Delegate to event manager
        self.event_manager.register_ui_event_handlers(event_processor)
    
    # ===== EVENT HANDLER IMPLEMENTATIONS =====
    
    def _on_hp_update(self, event) -> None:
        """Handle HP Bar Update Event - SMOOTH ANIMATION."""
        target = event.data.get('target')
        if not target:
            return
        
        # Get monster ID
        monster_id = getattr(target, 'id', id(target))
        old_hp = event.data.get('old_hp', target.current_hp)
        new_hp = target.current_hp
        max_hp = target.max_hp
        
        # Start smooth HP animation
        self.state.add_hp_animation(monster_id, old_hp, new_hp, max_hp, duration=0.5)
        
        # Update renderer
        if self.renderer:
            self.renderer.update_hp_bar(target, animated=True)
        
        logger.debug(f"HP update: {target.name} {old_hp} -> {new_hp}/{max_hp}")
    
    def _on_damage_dealt(self, event) -> None:
        """Handle Damage Dealt Event - FLOATING DAMAGE NUMBERS."""
        target = event.data.get('target')
        damage = event.data.get('damage', 0)
        is_critical = event.data.get('is_critical', False)
        is_super_effective = event.data.get('is_super_effective', False)
        
        if target and damage > 0:
            # Show damage number with enhanced effects via renderer
            if self.renderer:
                self.renderer.show_damage_number(target, damage, is_critical, is_super_effective)
            
            # Add screen shake for critical hits
            if is_critical:
                self.state.trigger_screen_shake(3.0, 0.2)
            
            logger.debug(f"Damage dealt: {damage} to {target.name} (critical: {is_critical})")
    
    def _on_message_show(self, event) -> None:
        """Handle Message Show Event - ENHANCED MESSAGE QUEUE SYSTEM."""
        message = event.data.get('message', '')
        duration = event.data.get('duration', 2.0)
        priority = event.data.get('priority', 'normal')
        blocking = event.data.get('blocking', True)
        
        if message:
            # Use new message queue system
            self.state.add_message_to_queue(message, duration, priority, "normal", blocking)
            
            # Update core properties for compatibility
            self.current_message = message
            self.message_wait = blocking
            self.message_timer = duration
            
            logger.debug(f"Message queued: '{message}' (priority: {priority}, blocking: {blocking})")
    
    def _on_turn_start(self, event) -> None:
        """Handle Turn Start Event - UI STATE UPDATE."""
        self.waiting_for_input = True
        self.state.message_wait = True
        logger.debug("Turn start: UI waiting for input")
    
    def _on_turn_end(self, event) -> None:
        """Handle Turn End Event - UI STATE UPDATE."""
        self.waiting_for_input = False
        self.state.message_wait = False
        logger.debug("Turn end: UI not waiting for input")
    
    def _on_phase_change(self, event) -> None:
        """Handle Phase Change Event - BATTLE FLOW."""
        # Handle both event objects and direct dicts
        if hasattr(event, 'data'):
            phase = event.data.get('phase')
            old_phase = event.data.get('old_phase', '')
        elif isinstance(event, dict):
            phase = event.get('phase')
            old_phase = event.get('old_phase', '')
        else:
            phase = None
            old_phase = ''
            
        if phase:
            # Handle phase change directly
            self._handle_phase_change({'phase': phase, 'old_phase': old_phase})
            logger.debug(f"Phase change: {old_phase} -> {phase}")
    
    def _handle_phase_change(self, phase_data: Dict[str, Any]) -> None:
        """Handle phase change - internal method."""
        try:
            phase = phase_data.get('phase')
            old_phase = phase_data.get('old_phase', '')
            
            if phase == 'input':
                self.waiting_for_input = True
                self.state.message_wait = False
                self.state.menu_state = BattleMenuState.MAIN
                # Clear any blocking messages
                self.state.current_message = ""
                logger.debug("Phase: INPUT - Waiting for player input")
            elif phase == 'execution':
                self.waiting_for_input = False
                self.state.message_wait = True
                self.state.menu_state = BattleMenuState.ACTION_ANIMATION
                logger.debug("Phase: EXECUTION - Processing actions")
            elif phase == 'aftermath':
                self.waiting_for_input = False
                self.state.message_wait = True
                self.state.menu_state = BattleMenuState.WAIT_FOR_INPUT
                logger.debug("Phase: AFTERMATH - Processing turn end")
            elif phase == 'end':
                self.waiting_for_input = False
                self.state.message_wait = False
                self.state.menu_state = BattleMenuState.BATTLE_RESULT
                logger.debug("Phase: END - Battle finished")
            
            # Update UI state based on phase
            self.state.current_phase = phase
            logger.debug(f"Phase transition: {old_phase} -> {phase}")
            
        except Exception as e:
            logger.error(f"Error handling phase change: {e}")
    
    def _on_battle_start(self, event) -> None:
        """Handle Battle Start Event - INITIALIZATION."""
        self.waiting_for_input = True
        self.state.message_wait = True
        logger.debug("Battle start: UI initialized")
    
    def _on_battle_end(self, event) -> None:
        """Handle Battle End Event - CLEANUP."""
        self.waiting_for_input = False
        self.state.message_wait = False
        
        # Get battle result from event data
        result = event.data.get('result')
        if hasattr(result, 'value'):
            result_value = result.value
        else:
            result_value = str(result) if result else 'unknown'
        
        # Add appropriate message based on result
        if result_value == 'victory':
            self.add_message("Du hast gewonnen!", priority="important")
        elif result_value == 'defeat':
            self.add_message("Du hast verloren!", priority="important")
        elif result_value == 'fled':
            self.add_message("Erfolgreich geflohen!", priority="normal")
        elif result_value == 'caught':
            self.add_message("Monster gefangen!", priority="important")
        else:
            self.add_message(f"Battle beendet: {result_value}", priority="normal")
        
        # Force UI to show battle result screen
        self.state.current_ui_state = "BATTLE_RESULT"
        
        logger.info(f"🏁 Battle end: {result_value}")
    
    def show_victory_message(self) -> None:
        """Show victory message and handle transition."""
        self.add_message("Du hast gewonnen!", priority="important")
        self.add_message("Belohnungen werden berechnet...", priority="normal")
        # Set flag for reward screen
        self.state.show_rewards = True
        
    def show_defeat_message(self) -> None:
        """Show defeat message and handle transition."""
        self.add_message("Du hast verloren!", priority="important")
        self.add_message("Du wirst ins Hauptmenü zurückgebracht...", priority="normal")
        # Set flag for defeat screen
        self.state.show_defeat = True
        
    def show_catch_success_message(self) -> None:
        """Show catch success message."""
        self.add_message("Monster gefangen!", priority="important")
        self.add_message("Es wurde zu deinem Team hinzugefügt!", priority="normal")
    
    def _on_monster_fainted(self, event) -> None:
        """Handle Monster Fainted Event - FAINT ANIMATION."""
        monster = event.data.get('monster')
        if monster:
            # Play faint animation via renderer
            if self.renderer:
                self.renderer.play_faint_animation(monster)
            else:
                # Fallback: add message
                self.add_message(f"{monster.name} ist ohnmächtig!")
            
            logger.debug(f"Monster fainted: {monster.name}")
    
    def _on_monster_switch(self, event) -> None:
        """Handle Monster Switch Event - APPEAR ANIMATION."""
        # Update monster sprites
        if 'player_active' in event.data:
            monster = event.data['player_active']
            if monster:
                self.player_sprite = BattleSprite(
                    surface=self._get_monster_sprite(monster),
                    position=self._get_monster_position(monster, True),
                    is_player_side=True
                )
                # Play appear animation via renderer
                if self.renderer:
                    self.renderer.play_appear_animation(monster)
                logger.debug(f"Player switch: {monster.name}")
        
        if 'enemy_active' in event.data:
            monster = event.data['enemy_active']
            if monster:
                self.enemy_sprite = BattleSprite(
                    surface=self._get_monster_sprite(monster),
                    position=self._get_monster_position(monster, False),
                    is_player_side=False
                )
                # Play appear animation via renderer
                if self.renderer:
                    self.renderer.play_appear_animation(monster)
                logger.debug(f"Enemy switch: {monster.name}")
    
    def _on_status_applied(self, event) -> None:
        """Handle Status Applied Event - STATUS INDICATOR."""
        target = event.data.get('target')
        status = event.data.get('status')
        
        if target and status:
            # Show status effect via renderer
            if self.renderer:
                self.renderer.show_status_effect(target, status)
            else:
                # Fallback: add message
                self.add_message(f"{target.name} ist {status}!")
            
            logger.debug(f"Status applied: {target.name} -> {status}")
    
    def _on_critical_hit(self, event) -> None:
        """Handle Critical Hit Event - SPECIAL EFFECTS."""
        target = event.data.get('target')
        if target:
            # Add critical hit effect
            pos = self._get_monster_position(target, target == self.battle_state.player_active)
            self.state.add_particle_effect(pos, 'critical', 15)
            
            # Screen flash for critical hits
            self.state.trigger_screen_flash((255, 255, 0), 0.5, 0.1)
            
            logger.debug(f"Critical hit: {target.name}")
    
    def _on_miss(self, event) -> None:
        """Handle Miss Event - MISS EFFECTS."""
        target = event.data.get('target')
        if target:
            # Add miss effect
            pos = self._get_monster_position(target, target == self.battle_state.player_active)
            self.state.add_particle_effect(pos, 'miss', 8)
            logger.debug(f"Miss: {target.name}")
    
    def _on_tame_attempt(self, event) -> None:
        """Handle Tame Attempt Event - TAMING UI."""
        target = event.data.get('target')
        success = event.data.get('success', False)
        
        if success:
            self.add_message("Monster erfolgreich gezähmt!", priority="important")
            # Add celebration effect
            if target:
                pos = self._get_monster_position(target, target == self.battle_state.player_active)
                self.state.add_particle_effect(pos, 'celebration', 20)
        else:
            self.add_message("Zähmversuch fehlgeschlagen!", priority="normal")
        
        logger.debug(f"Tame attempt: {target.name if target else 'unknown'} -> {success}")
    
    # === NEW EVENT HANDLERS FOR 45 EVENTS ===
    
    def _on_action_announce(self, event) -> None:
        """Handle Action Announce Event - ACTION PREVIEW."""
        action = event.data.get('action', '')
        actor = event.data.get('actor', '')
        
        if action and actor:
            self.add_message(f"{actor} bereitet {action} vor...", duration=1.0)
            logger.debug(f"Action announced: {actor} -> {action}")
    
    def _on_action_start(self, event) -> None:
        """Handle Action Start Event - ACTION BEGINNING."""
        action = event.data.get('action', '')
        actor = event.data.get('actor', '')
        
        if action and actor:
            logger.debug(f"Action started: {actor} -> {action}")
    
    def _on_action_execute(self, event) -> None:
        """Handle Action Execute Event - ACTION EXECUTION."""
        action = event.data.get('action', '')
        actor = event.data.get('actor', '')
        
        if action and actor:
            logger.debug(f"Action executing: {actor} -> {action}")
    
    def _on_action_end(self, event) -> None:
        """Handle Action End Event - ACTION COMPLETION."""
        action = event.data.get('action', '')
        actor = event.data.get('actor', '')
        
        if action and actor:
            logger.debug(f"Action ended: {actor} -> {action}")
    
    def _on_action_complete(self, event) -> None:
        """Handle Action Complete Event - ACTION FINISHED."""
        action = event.data.get('action', '')
        actor = event.data.get('actor', '')
        
        if action and actor:
            logger.debug(f"Action completed: {actor} -> {action}")
    
    def _on_stat_change(self, event) -> None:
        """Handle Stat Change Event - STAT MODIFICATION."""
        target = event.data.get('target')
        stat = event.data.get('stat', '')
        change = event.data.get('change', 0)
        
        if target and stat and change != 0:
            direction = "steigt" if change > 0 else "sinkt"
            self.add_message(f"{target.name}s {stat} {direction}!")
            logger.debug(f"Stat change: {target.name} {stat} {change:+d}")
    
    def _on_menu_open(self, event) -> None:
        """Handle Menu Open Event - MENU STATE."""
        menu_type = event.data.get('menu_type', 'main')
        self.state.menu_state = BattleMenuState(menu_type.upper())
        logger.debug(f"Menu opened: {menu_type}")
    
    def _on_menu_close(self, event) -> None:
        """Handle Menu Close Event - MENU STATE."""
        self.state.menu_state = BattleMenuState.MAIN
        logger.debug("Menu closed")
    
    def _on_dodge(self, event) -> None:
        """Handle Dodge Event - DODGE EFFECTS."""
        target = event.data.get('target')
        if target:
            pos = self._get_monster_position(target, target == self.battle_state.player_active)
            self.state.add_particle_effect(pos, 'dodge', 8)
            logger.debug(f"Dodge: {target.name}")
    
    def _on_block(self, event) -> None:
        """Handle Block Event - BLOCK EFFECTS."""
        target = event.data.get('target')
        if target:
            pos = self._get_monster_position(target, target == self.battle_state.player_active)
            self.state.add_particle_effect(pos, 'block', 10)
            logger.debug(f"Block: {target.name}")
    
    def _on_reflect(self, event) -> None:
        """Handle Reflect Event - REFLECT EFFECTS."""
        target = event.data.get('target')
        if target:
            pos = self._get_monster_position(target, target == self.battle_state.player_active)
            self.state.add_particle_effect(pos, 'reflect', 12)
            logger.debug(f"Reflect: {target.name}")
    
    def _on_absorb(self, event) -> None:
        """Handle Absorb Event - ABSORB EFFECTS."""
        target = event.data.get('target')
        if target:
            pos = self._get_monster_position(target, target == self.battle_state.player_active)
            self.state.add_particle_effect(pos, 'absorb', 15)
            logger.debug(f"Absorb: {target.name}")
    
    def _on_charge(self, event) -> None:
        """Handle Charge Event - CHARGE EFFECTS."""
        target = event.data.get('target')
        if target:
            pos = self._get_monster_position(target, target == self.battle_state.player_active)
            self.state.add_particle_effect(pos, 'charge', 20)
            logger.debug(f"Charge: {target.name}")
    
    def _on_discharge(self, event) -> None:
        """Handle Discharge Event - DISCHARGE EFFECTS."""
        target = event.data.get('target')
        if target:
            pos = self._get_monster_position(target, target == self.battle_state.player_active)
            self.state.add_particle_effect(pos, 'discharge', 25)
            logger.debug(f"Discharge: {target.name}")
    
    def _on_summon(self, event) -> None:
        """Handle Summon Event - SUMMON EFFECTS."""
        target = event.data.get('target')
        if target:
            pos = self._get_monster_position(target, target == self.battle_state.player_active)
            self.state.add_particle_effect(pos, 'summon', 30)
            logger.debug(f"Summon: {target.name}")
    
    def _on_banish(self, event) -> None:
        """Handle Banish Event - BANISH EFFECTS."""
        target = event.data.get('target')
        if target:
            pos = self._get_monster_position(target, target == self.battle_state.player_active)
            self.state.add_particle_effect(pos, 'banish', 25)
            logger.debug(f"Banish: {target.name}")
    
    def _on_escape_attempt(self, event) -> None:
        """Handle Escape Attempt Event - ESCAPE UI."""
        success = event.data.get('success', False)
        
        if success:
            self.add_message("Flucht erfolgreich!", priority="important")
        else:
            self.add_message("Flucht unmöglich!", priority="normal")
        
        logger.debug(f"Escape attempt: {success}")
    
    def _on_item_use(self, event) -> None:
        """Handle Item Use Event - ITEM UI."""
        item = event.data.get('item', '')
        target = event.data.get('target')
        
        if item and target:
            self.add_message(f"{item} wurde verwendet!", duration=1.5)
            logger.debug(f"Item used: {item} on {target.name}")
    
    def _on_dialog_show(self, event) -> None:
        """Handle Dialog Show Event - DIALOG UI."""
        message = event.data.get('message', '')
        if message:
            self.add_message(message, duration=3.0, priority="dialog")
            logger.debug(f"Dialog shown: {message}")
    
    def _on_dialog_choice(self, event) -> None:
        """Handle Dialog Choice Event - DIALOG UI."""
        choice = event.data.get('choice', '')
        if choice:
            logger.debug(f"Dialog choice: {choice}")
    
    def _on_weather_effect(self, event) -> None:
        """Handle Weather Effect Event - WEATHER UI."""
        weather = event.data.get('weather', '')
        if weather:
            self.add_message(f"Wetter-Effekt: {weather}!", duration=2.0)
            logger.debug(f"Weather effect: {weather}")
    
    def _on_terrain_effect(self, event) -> None:
        """Handle Terrain Effect Event - TERRAIN UI."""
        terrain = event.data.get('terrain', '')
        if terrain:
            self.add_message(f"Terrain-Effekt: {terrain}!", duration=2.0)
            logger.debug(f"Terrain effect: {terrain}")
    
    def _on_wait(self, event) -> None:
        """Handle Wait Event - WAIT UI."""
        duration = event.data.get('duration', 1.0)
        logger.debug(f"Wait: {duration}s")
    
    def _on_wait_for_input(self, event) -> None:
        """Handle Wait For Input Event - INPUT WAIT."""
        self.waiting_for_input = True
        logger.debug("Waiting for input")
    
    def _on_wait_for_animation(self, event) -> None:
        """Handle Wait For Animation Event - ANIMATION WAIT."""
        duration = event.data.get('duration', 1.0)
        logger.debug(f"Waiting for animation: {duration}s")
    
    def _on_level_up(self, event) -> None:
        """Handle Level Up Event - LEVEL UP UI."""
        monster = event.data.get('monster')
        new_level = event.data.get('new_level', 0)
        
        if monster and new_level > 0:
            self.add_message(f"{monster.name} erreicht Level {new_level}!", priority="important")
            # Add level up effect
            pos = self._get_monster_position(monster, monster == self.battle_state.player_active)
            self.state.add_particle_effect(pos, 'levelup', 40)
            logger.debug(f"Level up: {monster.name} -> Level {new_level}")
    
    def _on_super_effective(self, event) -> None:
        """Handle Super Effective Event - TYPE EFFECTIVENESS."""
        target = event.data.get('target')
        if target:
            pos = self._get_monster_position(target, target == self.battle_state.player_active)
            self.state.add_particle_effect(pos, 'super_effective', 15)
            logger.debug(f"Super effective: {target.name}")
    
    def _on_not_effective(self, event) -> None:
        """Handle Not Effective Event - TYPE EFFECTIVENESS."""
        target = event.data.get('target')
        if target:
            pos = self._get_monster_position(target, target == self.battle_state.player_active)
            self.state.add_particle_effect(pos, 'not_effective', 10)
            logger.debug(f"Not effective: {target.name}")
    
    def _on_not_very_effective(self, event) -> None:
        """Handle Not Very Effective Event - TYPE EFFECTIVENESS."""
        target = event.data.get('target')
        if target:
            pos = self._get_monster_position(target, target == self.battle_state.player_active)
            self.state.add_particle_effect(pos, 'not_very_effective', 8)
            logger.debug(f"Not very effective: {target.name}")
    
    def _on_no_effect(self, event) -> None:
        """Handle No Effect Event - TYPE EFFECTIVENESS."""
        target = event.data.get('target')
        if target:
            pos = self._get_monster_position(target, target == self.battle_state.player_active)
            self.state.add_particle_effect(pos, 'no_effect', 5)
            logger.debug(f"No effect: {target.name}")
    
    def _on_immune(self, event) -> None:
        """Handle Immune Event - TYPE EFFECTIVENESS."""
        target = event.data.get('target')
        if target:
            pos = self._get_monster_position(target, target == self.battle_state.player_active)
            self.state.add_particle_effect(pos, 'immune', 12)
            logger.debug(f"Immune: {target.name}")
    
    # ENHANCED: Visual Effects Event Handlers
    def _on_animation_play(self, event) -> None:
        """Handle Animation Play Event - VISUAL EFFECTS."""
        animation_type = event.data.get('type', 'default')
        target = event.data.get('target')
        if target:
            pos = self._get_monster_position(target, target == self.battle_state.player_active)
            self.renderer.visual_effects.add_effect(animation_type, pos)
            logger.debug(f"Animation play: {animation_type} for {target.name}")
    
    def _on_heal(self, event) -> None:
        """Handle Heal Event - VISUAL EFFECTS."""
        target = event.data.get('target')
        healing = event.data.get('healing', 0)
        if target and healing > 0:
            pos = self._get_monster_position(target, target == self.battle_state.player_active)
            self.renderer.show_healing_number(target, healing)
            self.renderer.visual_effects.add_effect('heal', pos)
            logger.debug(f"Heal: {target.name} +{healing} HP")
    
    def _on_revive(self, event) -> None:
        """Handle Revive Event - VISUAL EFFECTS."""
        target = event.data.get('target')
        if target:
            pos = self._get_monster_position(target, target == self.battle_state.player_active)
            self.renderer.visual_effects.add_effect('heal', pos, 2.0)
            logger.debug(f"Revive: {target.name}")
    
    def _on_transform(self, event) -> None:
        """Handle Transform Event - VISUAL EFFECTS."""
        target = event.data.get('target')
        if target:
            pos = self._get_monster_position(target, target == self.battle_state.player_active)
            self.renderer.visual_effects.add_effect('sparkle', pos, 1.5)
            logger.debug(f"Transform: {target.name}")
    
    def _on_copy(self, event) -> None:
        """Handle Copy Event - VISUAL EFFECTS."""
        target = event.data.get('target')
        if target:
            pos = self._get_monster_position(target, target == self.battle_state.player_active)
            self.renderer.visual_effects.add_effect('sparkle', pos)
            logger.debug(f"Copy: {target.name}")
    
    def _on_steal(self, event) -> None:
        """Handle Steal Event - VISUAL EFFECTS."""
        target = event.data.get('target')
        if target:
            pos = self._get_monster_position(target, target == self.battle_state.player_active)
            self.renderer.visual_effects.add_effect('sparkle', pos)
            logger.debug(f"Steal: {target.name}")
    
    def _on_swap(self, event) -> None:
        """Handle Swap Event - VISUAL EFFECTS."""
        target = event.data.get('target')
        if target:
            pos = self._get_monster_position(target, target == self.battle_state.player_active)
            self.renderer.visual_effects.add_effect('sparkle', pos)
            logger.debug(f"Swap: {target.name}")
    
    def _on_trap(self, event) -> None:
        """Handle Trap Event - VISUAL EFFECTS."""
        target = event.data.get('target')
        if target:
            pos = self._get_monster_position(target, target == self.battle_state.player_active)
            self.renderer.visual_effects.add_effect('explosion', pos, 0.8)
            logger.debug(f"Trap: {target.name}")
    
    def apply_update(self, update: Dict[str, Any]) -> None:
        """Wende Battle Update an."""
        if not update:
            return
        
        # Update battle state
        if 'battle_state' in update:
            self.battle_state = update['battle_state']
        
        # Update monster sprites
        if 'player_active' in update:
            monster = update['player_active']
            if monster:
                self.player_sprite = BattleSprite(
                    surface=self._get_monster_sprite(monster),
                    position=self._get_monster_position(monster, True),
                    is_player_side=True
                )
        
        if 'enemy_active' in update:
            monster = update['enemy_active']
            if monster:
                self.enemy_sprite = BattleSprite(
                    surface=self._get_monster_sprite(monster),
                    position=self._get_monster_position(monster, False),
                    is_player_side=False
                )
        
        # Update UI state
        if 'menu_state' in update:
            self.current_menu_state = update['menu_state']
        
        if 'waiting_for_input' in update:
            self.waiting_for_input = update['waiting_for_input']
    
    def clear_pending_action(self):
        """Lösche pending action."""
        self.pending_action = None
        self.state.pending_action = None
    
    def queue_action(self, action: Dict[str, Any]) -> bool:
        """Queue action mit cooldown check."""
        import time
        current_time = time.time()
        if current_time - self.state.last_action_time < self.state.action_cooldown:
            logger.debug("Action ignored - cooldown active")
            return False
        
        self.pending_action = action
        self.state.pending_action = action
        self.state.last_action_time = current_time
        logger.info(f"Action queued: {action.get('type', 'unknown')}")
        return True
    
    def get_action_result(self):
        """Hole und lösche pending action atomisch."""
        if self.pending_action:
            action = self.pending_action
            self.pending_action = None  # Clear sofort
            self.state.pending_action = None  # Clear state auch
            logger.debug(f"Returning pending action: {action}")
            return action
        return None
    
    def is_waiting_for_input(self) -> bool:
        """Prüfe ob UI auf Input wartet."""
        return self.waiting_for_input
    
    def reset_to_main_menu(self):
        """PROFESSIONAL RESET zu Hauptmenü mit detailliertem Debug."""
        logger.info("🔄 PROFESSIONAL UI RESET: Starting complete reset")
        
        # PROFESSIONAL DEBUG: Log current state
        logger.info(f"   Before reset: waiting_for_input={self.waiting_for_input}")
        logger.info(f"   Before reset: menu_state={getattr(self, 'current_menu_state', 'UNKNOWN')}")
        logger.info(f"   Before reset: selected_option={getattr(self, 'selected_option', 'UNKNOWN')}")
        logger.info(f"   Before reset: pending_action={getattr(self, '_pending_action', 'UNKNOWN')}")
        
        # PROFESSIONAL RESET: Complete state reset
        self.menu_manager.show_main_menu()
        self.waiting_for_input = True
        self.current_menu_state = BattleMenuState.MAIN
        self.selected_option = 0
        self._pending_action = None
        self.current_message = None
        self.message_timer = 0
        
        # PROFESSIONAL DEBUG: Verify reset
        logger.info(f"   After reset: waiting_for_input={self.waiting_for_input}")
        logger.info(f"   After reset: menu_state={getattr(self, 'current_menu_state', 'UNKNOWN')}")
        logger.info(f"   After reset: selected_option={getattr(self, 'selected_option', 'UNKNOWN')}")
        logger.info("✅ PROFESSIONAL UI RESET COMPLETE - ready for next turn")
    
    def init_demo_inventory(self):
        """Initialisiere Demo-Inventar für Tests."""
        self.demo_inventory = {
            "Kräuter": 5,
            "Starkkräuter": 2,
            "Antidot": 3,
            "Kraftpulver": 1,
            "Eisenpulver": 1,
            "Fleisch": 3,
            "Edelfleisch": 1,
            "Götterfleisch": 0
        }
    
    # Menu Management Methods - Delegation an MenuManager
    def show_main_menu(self):
        """Zeige Hauptmenü."""
        self.menu_manager.show_main_menu()
    
    def show_move_menu(self):
        """Zeige Move-Menü."""
        self.menu_manager.show_move_menu()
    
    def show_item_menu(self):
        """Zeige Item-Menü."""
        self.menu_manager.show_item_menu()
    
    def show_team_menu(self):
        """Zeige Team-Menü."""
        self.menu_manager.show_team_menu()
    
    def show_meat_menu(self):
        """Zeige Meat-Menü."""
        self.menu_manager.show_meat_menu()
    
    def show_tame_confirm_menu(self):
        """Zeige Tame-Confirm-Menü."""
        self.menu_manager.show_tame_confirm_menu()
    
    def show_scout_display(self):
        """Zeige Scout Display."""
        self.menu_manager.show_scout_display()
    
    def show_message_display(self):
        """Zeige Message Display."""
        self.menu_manager.show_message_display()
    
    def go_back(self):
        """Gehe zurück zum vorherigen Menü."""
        self.menu_manager.go_back()
    
    def get_items_for_category(self, category: str) -> Dict[str, int]:
        """Get items for a specific category."""
        return self.menu_manager.get_items_for_category(category)
    
    def get_moves_by_category(self, moves: List, category: str) -> List:
        """Filter moves by category."""
        return self.menu_manager.get_moves_by_category(moves, category)
    
    def validate_menu_state(self) -> bool:
        """Validate current menu state."""
        return self.menu_manager.validate_menu_state()
    
    def transition_to_menu(self, target_menu: BattleMenuState, transition_time: float = 0.2) -> None:
        """Smoothly transition to a new menu state."""
        self.menu_manager.transition_to_menu(target_menu, transition_time)
    
    def get_menu_options(self, menu_state: BattleMenuState) -> List[str]:
        """Get available options for a menu state."""
        return self.menu_manager.get_menu_options(menu_state)
    
    # Helper methods for monster sprites and positions
    
    def _get_monster_position(self, monster, is_player):
        """Berechne Monster Position."""
        if is_player:
            return (LOGICAL_WIDTH // 4, LOGICAL_HEIGHT // 2)
        else:
            return (3 * LOGICAL_WIDTH // 4, LOGICAL_HEIGHT // 2)
    
    # ===== REDUNDANT METHODS REMOVED =====
    # _update_animations() and _next_message() are now handled by:
    # - BattleUIState.update_animations() for animations
    # - BattleUIState.update_message_timer() for message queue
    
    # Event processing methods - LEGACY VERSION REMOVED
    
    # ===== LEGACY EVENT HANDLERS REMOVED =====
    # These methods have been replaced by the new _on_* event handlers
    # that are automatically registered with the EventProcessor system.
    
    # Utility methods
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
            "speed": 50 if animated else 1000,  # Schnelle Animation
            "timer": 0.5 if animated else 0.0,  # Kürzere Animationszeit
            "old_hp": target.current_hp,  # Für Animation
            "new_hp": target.current_hp   # Für Animation
        }
        
        # HP bar update delegated to renderer
        if self.renderer and hasattr(self.renderer, 'update_hp_bar'):
            self.renderer.update_hp_bar(target, animated)
        else:
            # Fallback: direct HP bar update
            logger.debug(f"HP bar update fallback for {target.name if target else 'None'}")
        
        logger.info(f"✓ HP bar updated immediately: {target.name} {target.current_hp}/{target.max_hp}")
    
    # ===== REDUNDANT METHODS REMOVED =====
    # These methods are now handled by the Event System:
    # - show_damage_number() -> _on_damage_dealt()
    # - show_healing_number() -> _on_healing_done()
    # - show_status_effect() -> _on_status_applied()
    # - play_faint_animation() -> _on_monster_fainted()
    # - play_appear_animation() -> _on_monster_appear()
    
    def get_current_message(self) -> str:
        """Get current message from message queue."""
        if self.state and self.state.message_queue_system:
            return self.state.message_queue_system.get_current_message()
        return ""
    
    def show_message(self, message: str) -> None:
        """Zeige Nachricht - ENHANCED."""
        # CRITICAL: Set current_message IMMEDIATELY
        self.current_message = message
        self.state.current_message = message
        
        # CRITICAL: Set message_wait and menu_state
        self.message_wait = True
        self.state.message_wait = True
        self.state.menu_state = BattleMenuState.MESSAGE
        
        # Set timer for auto-advance
        self.message_timer = 2.0
        self.state.message_timer = 2.0
        
        logger.info(f"Message displayed: {message}")
    
    def add_message(self, message: str, wait: bool = True, duration: float = 2.0, priority: str = "normal"):
        """Füge Nachricht zur Queue hinzu - ENHANCED mit Priority-System."""
        # Use new message queue system
        self.state.add_message_to_queue(message, duration, priority, "normal", wait)
        
        # Update core properties for compatibility
        self.current_message = message
        self.message_wait = wait
        self.message_timer = duration
        
        logger.info(f"✓ Message queued: '{message}' (duration: {duration}s, priority: {priority})")
    
    def process_message_input(self, action: str) -> bool:
        """Verarbeite Input für Message-Queue."""
        return self.state.process_message_input(action)
    
    def get_current_message_data(self) -> Optional[Dict[str, Any]]:
        """Hole aktuelle Message-Daten."""
        return self.state.get_current_message_data()
    
    # ===== REDUNDANT METHODS REMOVED =====
    # These methods are now handled by the Event System:
    # - add_damage_number() -> _on_damage_dealt() + _on_healing_done()
    # - trigger_screen_flash() -> _on_screen_flash() + renderer methods
    # - trigger_screen_shake() -> _on_camera_shake() + renderer methods