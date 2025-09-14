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
from typing import Optional, List, Tuple, Dict, Any, TYPE_CHECKING
from dataclasses import dataclass

# Setup logger
logger = logging.getLogger(__name__)

# Import the config constants
from engine.core.config import LOGICAL_WIDTH, LOGICAL_HEIGHT, Colors, Fonts, UI
from engine.core.resources import resources

# Import sub-UI components
from engine.ui.taming_ui import TamingUI, TamingUIState
from engine.ui.scout_display import ScoutDisplay, ScoutDisplayTab
from engine.ui.battle_ui_utils import fonts, types, sprites, colors, text_utils

# Import battle system components
from engine.systems.battle.battle_state import BattleState
from engine.systems.battle.battle_controller import BattleController
from engine.systems.battle.event_processor import EventProcessor, EventType, BattleEvent

# Import modular components
from .battle_ui_state import BattleUIState, BattleMenuState, BattleSprite, DamageNumber
from .battle_ui_renderer import BattleUIRenderer
from .battle_ui_input import BattleUIInputHandler
from .battle_ui_menus import BattleUIMenuManager

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
        self.battle_controller: Optional[BattleController] = None
        self.event_processor: Optional[EventProcessor] = None
        
        # Animation and effects (Core-specific, not in state)
        self.damage_numbers: List[DamageNumber] = []
        self.message_queue: List[str] = []
        
        # Monster sprites
        self.player_sprite: Optional[BattleSprite] = None
        self.enemy_sprite: Optional[BattleSprite] = None
        
        # Pending action
        self.pending_action: Optional[Dict[str, Any]] = None
        
        # Initialize state FIRST
        self.state = BattleUIState()
        
        # Initialize modular components
        self.renderer = BattleUIRenderer(self)
        self.input_handler = BattleUIInputHandler(self)
        self.menu_manager = BattleUIMenuManager(self)
        
        # Initialize sub-UI components
        self.taming_ui = TamingUI()
        self.scout_display = ScoutDisplay()
        
        # Demo inventory for testing
        self.demo_inventory = {}
        
        logger.info("Battle UI Core initialized with modular components")
    
    @property
    def _pending_action(self):
        """Compatibility property für BattleScene."""
        return self.pending_action
    
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
        """Initialisiere Battle mit Teams."""
        logger.info(f"Initializing battle: {len(player_team)} vs {len(enemy_team)}")
        
        # Reset UI state
        self.reset()
        
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
        
        logger.info("Battle initialization complete")
    
    def update(self, dt):
        """Update Battle UI und alle Komponenten."""
        # Update animations and effects
        self._update_animations(dt)
        
        # Update modular components
        self.renderer.update(dt)
        self.input_handler.update(dt)
        self.menu_manager.update(dt)
        
        # Update sub-UI components
        self.taming_ui.update(dt)
        self.scout_display.update(dt)
    
    def draw(self, surface: pygame.Surface):
        """Zeichne Battle UI - delegiert an Renderer."""
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
            if not monster or not hasattr(monster, 'species_id'):
                return self._create_fallback_sprite("unknown")
            
            # Try to get sprite from sprites utility
            sprite = sprites.get_monster_sprite(monster.species_id)
            if sprite:
                # Ensure sprite is correct size
                if sprite.get_size() != (32, 32):
                    sprite = pygame.transform.scale(sprite, (32, 32))
                return sprite
            
            # Try alternative sprite loading methods
            sprite = self._load_sprite_by_id(monster.species_id)
            if sprite:
                return sprite
            
            # Create fallback sprite
            return self._create_fallback_sprite(monster.species_id)
            
        except Exception as e:
            logger.warning(f"Could not load sprite for {getattr(monster, 'species_id', 'unknown')}: {e}")
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
    
    def _get_monster_position(self, monster, is_player):
        """Get monster position."""
        if is_player:
            return (80, 120)  # PLAYER_POS
        else:
            return (240, 80)  # ENEMY_POS
    
    def handle_input(self, action, battle_state=None):
        """Handle Input - delegiert an Input Handler."""
        return self.input_handler.handle_input(action, battle_state)
    
    def connect_event_handlers(self, event_processor: EventProcessor) -> None:
        """Verbinde Event Handler für Battle Events."""
        self.event_processor = event_processor
        
        # CRITICAL: Register all UI handlers at once
        if hasattr(event_processor, 'register_ui_handlers'):
            event_processor.register_ui_handlers(self)
            logger.info("✓ UI event handlers registered")
        else:
            logger.warning("EventProcessor has no register_ui_handlers method")
        
        logger.info("Event handlers connected")
    
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
        """Reset zu Hauptmenü."""
        self.current_menu_state = BattleMenuState.MAIN
        self.selected_option = 0
        self.waiting_for_input = True
        logger.info("Reset to main menu")
    
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
    
    # Helper methods for monster sprites and positions
    
    def _get_monster_position(self, monster, is_player):
        """Berechne Monster Position."""
        if is_player:
            return (LOGICAL_WIDTH // 4, LOGICAL_HEIGHT // 2)
        else:
            return (3 * LOGICAL_WIDTH // 4, LOGICAL_HEIGHT // 2)
    
    def _update_animations(self, dt):
        """Update Animationen und Effekte."""
        # Update damage numbers
        for damage_num in self.damage_numbers[:]:
            damage_num.timer -= dt
            damage_num.position = (
                damage_num.position[0] + damage_num.velocity[0] * dt,
                damage_num.position[1] + damage_num.velocity[1] * dt
            )
            if damage_num.timer <= 0:
                self.damage_numbers.remove(damage_num)
        
        # Update screen effects
        if self.screen_flash_timer > 0:
            self.screen_flash_timer -= dt
        
        if self.screen_shake_timer > 0:
            self.screen_shake_timer -= dt
        
        # Update message timer
        if self.message_timer > 0:
            self.message_timer -= dt
            if self.message_timer <= 0:
                self._next_message()
    
    def _next_message(self):
        """Nächste Nachricht aus Queue."""
        if self.message_queue:
            self.current_message = self.message_queue.pop(0)
            self.message_timer = 2.0  # 2 seconds per message
        else:
            self.current_message = ""
            self.waiting_for_input = True
    
    # Event processing methods
    def process_battle_event(self, event: dict):
        """Verarbeite Battle Event."""
        event_type = event.get('type')
        
        if event_type == 'message':
            self._handle_message_event(event)
        elif event_type == 'hp_update':
            self._handle_hp_update_event(event)
        elif event_type == 'damage':
            self._handle_damage_event(event)
        elif event_type == 'status':
            self._handle_status_event(event)
        elif event_type == 'healing':
            self._handle_healing_event(event)
        elif event_type == 'faint':
            self._handle_faint_event(event)
        elif event_type == 'switch':
            self._handle_switch_event(event)
        elif event_type == 'turn_start':
            self._handle_turn_start_event(event)
        elif event_type == 'turn_end':
            self._handle_turn_end_event(event)
        elif event_type == 'battle_end':
            self._handle_battle_end_event(event)
        elif event_type == 'animation':
            self._handle_animation_event(event)
        elif event_type == 'screen_flash':
            self._handle_screen_flash_event(event)
        elif event_type == 'screen_shake':
            self._handle_screen_shake_event(event)
        elif event_type == 'status_tick':
            self._handle_status_tick_event(event)
        elif event_type == 'phase_change':
            self._handle_phase_change_event(event)
    
    def _handle_message_event(self, event):
        """Handle Message Event."""
        message = event.get('message', '')
        if message:
            self.add_message(message)
    
    def _handle_hp_update_event(self, event):
        """Handle HP Update Event."""
        target = event.get('target')
        if target:
            self.update_hp_bar(target)
    
    def _handle_damage_event(self, event):
        """Handle Damage Event."""
        target = event.get('target')
        damage = event.get('damage', 0)
        is_critical = event.get('is_critical', False)
        if target and damage > 0:
            self.show_damage_number(target, damage, is_critical)
    
    def _handle_status_event(self, event):
        """Handle Status Event."""
        target = event.get('target')
        status = event.get('status')
        if target and status:
            self.show_status_effect(target, status)
    
    def _handle_healing_event(self, event):
        """Handle Healing Event."""
        target = event.get('target')
        healing = event.get('healing', 0)
        if target and healing > 0:
            self.show_healing_number(target, healing)
    
    def _handle_faint_event(self, event):
        """Handle Faint Event."""
        monster = event.get('monster')
        if monster:
            self.play_faint_animation(monster)
    
    def _handle_switch_event(self, event):
        """Handle Switch Event."""
        # Update monster sprites
        if 'player_active' in event:
            monster = event['player_active']
            if monster:
                self.player_sprite = BattleSprite(
                    surface=self._get_monster_sprite(monster),
                    position=self._get_monster_position(monster, True),
                    is_player_side=True
                )
    
    def _handle_turn_start_event(self, event):
        """Handle Turn Start Event."""
        self.waiting_for_input = True
    
    def _handle_turn_end_event(self, event):
        """Handle Turn End Event."""
        self.waiting_for_input = False
    
    def _handle_battle_end_event(self, event):
        """Handle Battle End Event."""
        self.waiting_for_input = False
        self.add_message("Battle beendet!")
    
    def _handle_animation_event(self, event):
        """Handle Animation Event."""
        # Animation handling delegated to renderer
        pass
    
    def _handle_screen_flash_event(self, event):
        """Handle Screen Flash Event."""
        intensity = event.get('intensity', 128)
        self.trigger_screen_flash(intensity)
    
    def _handle_screen_shake_event(self, event):
        """Handle Screen Shake Event."""
        intensity = event.get('intensity', 5)
        duration = event.get('duration', 0.3)
        self.trigger_screen_shake(intensity, duration)
    
    def _handle_status_tick_event(self, event):
        """Handle Status Tick Event."""
        # Status tick handling
        pass
    
    def _handle_phase_change_event(self, event):
        """Handle Phase Change Event."""
        phase = event.get('phase')
        if phase:
            self._handle_phase_change({'phase': phase})
    
    def _handle_phase_change(self, data):
        """Handle Phase Change."""
        phase = data.get('phase')
        if phase == 'input':
            self.waiting_for_input = True
        elif phase == 'execution':
            self.waiting_for_input = False
    
    # Utility methods
    def update_hp_bar(self, target, animated=True):
        """Update HP Bar."""
        # HP bar update delegated to renderer
        if self.renderer and hasattr(self.renderer, 'update_hp_bar'):
            self.renderer.update_hp_bar(target, animated)
    
    def show_damage_number(self, target, damage, is_critical=False, is_status=False):
        """Zeige Damage Number."""
        pos = self._get_monster_position(target, target == self.battle_state.player_active)
        color = (255, 0, 0) if not is_status else (255, 100, 100)
        
        damage_num = DamageNumber(
            value=damage,
            position=pos,
            timer=2.0,
            velocity=(0, -50),
            color=color,
            is_critical=is_critical
        )
        self.damage_numbers.append(damage_num)
    
    def show_status_effect(self, target, status):
        """Zeige Status Effect."""
        # Status effect display delegated to renderer
        if self.renderer and hasattr(self.renderer, 'show_status_effect'):
            self.renderer.show_status_effect(target, status)
        else:
            # Fallback: add message
            self.add_message(f"{target.name} ist {status}!")
    
    def play_faint_animation(self, monster):
        """Spiele Faint Animation."""
        # Faint animation delegated to renderer
        if self.renderer and hasattr(self.renderer, 'play_faint_animation'):
            self.renderer.play_faint_animation(monster)
        else:
            # Fallback: add message
            self.add_message(f"{monster.name} ist ohnmächtig!")
    
    def show_healing_number(self, target, healing):
        """Zeige Healing Number."""
        pos = self._get_monster_position(target, target == self.battle_state.player_active)
        
        damage_num = DamageNumber(
            value=healing,
            position=pos,
            timer=2.0,
            velocity=(0, -50),
            color=(0, 255, 0)
        )
        self.damage_numbers.append(damage_num)
    
    def play_appear_animation(self, monster):
        """Spiele Appear Animation."""
        # Appear animation delegated to renderer
        if self.renderer and hasattr(self.renderer, 'play_appear_animation'):
            self.renderer.play_appear_animation(monster)
        else:
            # Fallback: add message
            self.add_message(f"{monster.name} erscheint!")
    
    def show_message(self, message: str) -> None:
        """Zeige Nachricht."""
        self.current_message = message
        self.message_timer = 0.0
        self.message_wait = True
        self.state.menu_state = BattleMenuState.MESSAGE
    
    def add_message(self, message: str, wait: bool = True):
        """Füge Nachricht zur Queue hinzu."""
        self.show_message(message)
        if not wait:
            self.message_wait = False
    
    def add_damage_number(self, value: int, x: int, y: int, is_critical: bool = False, 
                         is_effective: bool = False, is_heal: bool = False, is_status: bool = False) -> None:
        """Füge Schadens-Nummer hinzu."""
        color = (255, 255, 255)  # Default color
        if is_critical:
            color = (255, 255, 0)  # Yellow
        elif is_effective:
            color = (255, 0, 0)  # Red
        elif is_heal:
            color = (0, 255, 0)  # Green
        elif is_status:
            color = (255, 0, 255)  # Magenta
        
        self.damage_numbers.append({
            "value": value,
            "x": x,
            "y": y,
            "timer": 1.0,
            "velocity": (0, -30),
            "color": color,
            "is_critical": is_critical,
            "is_effective": is_effective,
            "is_heal": is_heal,
            "is_status": is_status
        })
    
    def trigger_screen_flash(self, intensity=128):
        """Trigger Screen Flash."""
        self.screen_flash_timer = 0.2
        # Flash effect handled by renderer
    
    def trigger_screen_shake(self, intensity=5, duration=0.3):
        """Trigger Screen Shake."""
        self.screen_shake_timer = duration
        self.screen_shake_intensity = intensity
        self.screen_shake_intensity = intensity