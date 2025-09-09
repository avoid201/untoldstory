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
from typing import Optional, List, Dict, Any

# Setup logger
logger = logging.getLogger(__name__)

# Import the config constants
from engine.core.config import LOGICAL_WIDTH, LOGICAL_HEIGHT

# Import sub-UI components
from engine.ui.taming_ui import TamingUI
from engine.ui.scout_display import ScoutDisplay
from engine.ui.battle_ui_utils import fonts, sprites

# Import battle system components
from engine.systems.battle.battle_state import BattleState
from engine.systems.battle.battle_controller import BattleController
from engine.systems.battle.event_processor import EventProcessor

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
    
    def update(self, dt):
        """Update Battle UI und alle Komponenten."""
        # Update animations and effects
        self._update_animations(dt)
        
        # Update modular components
        self.renderer.update_animations(dt)
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
        self.menu_manager.show_main_menu()
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
    
    def _update_animations(self, dt):
        """Update Animationen und Effekte using BattleUIState."""
        # Update all animations through BattleUIState
        self.state.update_animations(dt)
        
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
    
    # Event processing methods - LEGACY VERSION REMOVED
    
    def _handle_message_event(self, event):
        """Handle Message Event - ENHANCED Priority-System."""
        message = event.get('message', '')
        duration = event.get('duration', 2.0)  # Erhöhte Standard-Dauer
        priority = event.get('priority', 'normal')  # Message-Priorität
        
        if message:
            # Sofortige Message-Anzeige mit Priority-System
            self.add_message(message, wait=True, duration=duration, priority=priority)
            
            # Zusätzliche Timer-Überprüfung für Priority-System
            if priority == "important" and self.message_timer < 3.0:
                self.message_timer = 3.0
            elif priority == "critical" and self.message_timer < 4.0:
                self.message_timer = 4.0
            elif priority == "quick" and self.message_timer > 1.0:
                self.message_timer = 1.0
            
            logger.info(f"✓ Message displayed immediately: '{message}' (priority: {priority}, duration: {self.message_timer}s)")
    
    def _handle_hp_update_event(self, event):
        """Handle HP Update Event - OPTIMIERTE SOFORTIGE UI-UPDATES."""
        target = event.get('target')
        if target:
            # IMMEDIATE update - keine Verzögerung
            self.update_hp_bar(target, animated=True)
            
            # Get monster ID
            if hasattr(target, 'id'):
                monster_id = target.id
            else:
                monster_id = id(target)
            
            old_hp = event.get('old_hp', target.current_hp)
            new_hp = target.current_hp
            max_hp = target.max_hp
            
            # Start smooth animation immediately
            self.state.add_hp_animation(monster_id, old_hp, new_hp, max_hp, duration=0.4)
            
            # Sofortige UI-State-Aktualisierung für sofortige Anzeige
            self.state.animations["hp_bars"][monster_id] = {
                "active": True,
                "current": new_hp,  # Sofort aktueller Wert
                "target": new_hp,
                "max_hp": max_hp,
                "speed": 150,  # Schnellere Animation
                "timer": 0.4,  # Kürzere Animationszeit
                "original_timer": 0.4,  # Für bessere Interpolation
                "old_hp": old_hp,
                "new_hp": new_hp
            }
            
            logger.info(f"✓ HP update processed immediately: {target.name} {old_hp} -> {new_hp}/{max_hp}")
    
    def _handle_damage_event(self, event):
        """Handle Damage Event - ENHANCED."""
        target = event.get('target')
        damage = event.get('damage', 0)
        is_critical = event.get('is_critical', False)
        is_super_effective = event.get('is_super_effective', False)
        
        if target and damage > 0:
            # Show damage number with enhanced effects
            self.show_damage_number(target, damage, is_critical, is_super_effective)
            
            # Add damage number to state for animation
            pos = self._get_monster_position(target, target == self.battle_state.player_active)
            color = (255, 0, 0) if not is_super_effective else (255, 100, 0)
            if is_critical:
                color = (255, 255, 0)
            
            self.state.add_damage_number(damage, pos, color, is_critical)
            logger.info(f"Damage event: {target.name} takes {damage} damage (critical: {is_critical})")
    
    def _handle_status_event(self, event):
        """Handle Status Event - ENHANCED."""
        target = event.get('target')
        status = event.get('status')
        applied = event.get('applied', True)
        
        if target and status:
            if applied:
                # Show status effect applied
                self.show_status_effect(target, status)
                
                # Add status effect to state for animation
                if hasattr(target, 'id'):
                    monster_id = target.id
                else:
                    monster_id = id(target)
                
                self.state.add_status_effect(monster_id, status, 2.0)
                logger.info(f"Status applied: {target.name} -> {status}")
            else:
                # Status removed
                logger.info(f"Status removed: {target.name} -> {status}")
    
    def _handle_healing_event(self, event):
        """Handle Healing Event - ENHANCED."""
        target = event.get('target')
        healing = event.get('healing', 0)
        
        if target and healing > 0:
            # Show healing number
            self.show_healing_number(target, healing)
            
            # Add healing number to state for animation
            pos = self._get_monster_position(target, target == self.battle_state.player_active)
            self.state.add_damage_number(healing, pos, (0, 255, 0), False)
            logger.info(f"Healing event: {target.name} healed for {healing}")
    
    def _handle_faint_event(self, event):
        """Handle Faint Event - ENHANCED."""
        monster = event.get('monster')
        if monster:
            # Play faint animation
            self.play_faint_animation(monster)
            
            # Add faint animation to state
            if hasattr(monster, 'id'):
                monster_id = monster.id
            else:
                monster_id = id(monster)
            
            self.state.start_faint_animation(monster_id)
            logger.info(f"Faint event: {monster.name} fainted")
    
    def _handle_switch_event(self, event):
        """Handle Switch Event - ENHANCED."""
        # Update monster sprites
        if 'player_active' in event:
            monster = event['player_active']
            if monster:
                self.player_sprite = BattleSprite(
                    surface=self._get_monster_sprite(monster),
                    position=self._get_monster_position(monster, True),
                    is_player_side=True
                )
                
                # Add appear animation
                if hasattr(monster, 'id'):
                    monster_id = monster.id
                else:
                    monster_id = id(monster)
                
                self.state.start_appear_animation(monster_id)
                logger.info(f"Switch event: {monster.name} appeared")
        
        if 'enemy_active' in event:
            monster = event['enemy_active']
            if monster:
                self.enemy_sprite = BattleSprite(
                    surface=self._get_monster_sprite(monster),
                    position=self._get_monster_position(monster, False),
                    is_player_side=False
                )
                
                # Add appear animation
                if hasattr(monster, 'id'):
                    monster_id = monster.id
                else:
                    monster_id = id(monster)
                
                self.state.start_appear_animation(monster_id)
                logger.info(f"Switch event: {monster.name} appeared")
    
    def _handle_turn_start_event(self, event):
        """Handle Turn Start Event - ENHANCED."""
        self.waiting_for_input = True
        self.state.message_wait = True
        logger.info("Turn start: UI waiting for input")
    
    def _handle_turn_end_event(self, event):
        """Handle Turn End Event - ENHANCED."""
        self.waiting_for_input = False
        self.state.message_wait = False
        logger.info("Turn end: UI not waiting for input")
    
    def _handle_battle_end_event(self, event):
        """Handle Battle End Event - ENHANCED."""
        self.waiting_for_input = False
        self.state.message_wait = False
        
        result = event.get('result', 'unknown')
        if result == 'victory':
            self.add_message("Du hast gewonnen!")
        elif result == 'defeat':
            self.add_message("Du hast verloren!")
        elif result == 'fled':
            self.add_message("Erfolgreich geflohen!")
        elif result == 'caught':
            self.add_message("Monster gefangen!")
        else:
            self.add_message("Battle beendet!")
        
        logger.info(f"Battle end event: {result}")
    
    def _handle_animation_event(self, event):
        """Handle Animation Event - ENHANCED."""
        animation_type = event.get('animation_type', 'generic')
        target = event.get('target')
        
        if animation_type == 'attack' and target:
            # Add attack animation
            if hasattr(target, 'id'):
                target_id = target.id
            else:
                target_id = id(target)
            
            self.state.add_attack_animation(target_id, target_id, 'physical')
            logger.info(f"Attack animation: {target.name}")
        
        elif animation_type == 'particle' and target:
            # Add particle effect
            pos = self._get_monster_position(target, target == self.battle_state.player_active)
            self.state.add_particle_effect(pos, 'sparkle', 10)
            logger.info(f"Particle effect: {target.name}")
    
    def _handle_screen_flash_event(self, event):
        """Handle Screen Flash Event - ENHANCED."""
        intensity = event.get('intensity', 128)
        color = event.get('color', (255, 255, 255))
        duration = event.get('duration', 0.3)
        
        self.trigger_screen_flash(intensity)
        self.state.trigger_screen_flash(color, intensity / 255.0, duration)
        logger.info(f"Screen flash: intensity={intensity}, color={color}")
    
    def _handle_screen_shake_event(self, event):
        """Handle Screen Shake Event - ENHANCED."""
        intensity = event.get('intensity', 5)
        duration = event.get('duration', 0.3)
        
        self.trigger_screen_shake(intensity, duration)
        self.state.trigger_screen_shake(intensity, duration)
        logger.info(f"Screen shake: intensity={intensity}, duration={duration}")
    
    def _handle_status_tick_event(self, event):
        """Handle Status Tick Event - ENHANCED."""
        target = event.get('target')
        status = event.get('status')
        damage = event.get('damage', 0)
        
        if target and status:
            if damage > 0:
                # Show status damage
                self.show_damage_number(target, damage, False, True)
                logger.info(f"Status tick: {target.name} takes {damage} {status} damage")
            else:
                logger.info(f"Status tick: {target.name} {status} effect")
    
    def _handle_phase_change_event(self, event):
        """Handle Phase Change Event - ENHANCED."""
        phase = event.get('phase')
        if phase:
            self._handle_phase_change({'phase': phase})
            logger.info(f"Phase change event processed: {phase}")
    
    def _handle_phase_change(self, data):
        """Handle Phase Change - ROBUST IMPLEMENTATION."""
        phase = data.get('phase')
        logger.info(f"Phase change event received: {phase}")
        
        # Import BattlePhase if not already imported
        try:
            from engine.systems.battle.battle_enums import BattlePhase
        except ImportError:
            # Fallback if import fails
            class BattlePhase:
                INPUT = 'input'
                EXECUTION = 'execution'
                START = 'start'
                END = 'end'
        
        if phase == 'input' or phase == BattlePhase.INPUT:
            self.waiting_for_input = True
            self.state.message_wait = True
            logger.info("✓ UI set to waiting for input")
        elif phase == 'execution' or phase == BattlePhase.EXECUTION:
            self.waiting_for_input = False
            self.state.message_wait = False
            logger.info("✓ UI set to not waiting for input")
        elif phase == 'start' or phase == BattlePhase.START:
            self.waiting_for_input = True
            self.state.message_wait = True
            logger.info("✓ UI set to waiting for input (battle start)")
        elif phase == 'end' or phase == BattlePhase.END:
            self.waiting_for_input = False
            self.state.message_wait = False
            logger.info("✓ UI set to not waiting for input (battle end)")
    
    # Additional Event Handlers for Complete Coverage
    def _handle_critical_hit_event(self, event):
        """Handle Critical Hit Event."""
        target = event.get('target')
        if target:
            # Add critical hit effect
            pos = self._get_monster_position(target, target == self.battle_state.player_active)
            self.state.add_particle_effect(pos, 'critical', 15)
            logger.info(f"Critical hit: {target.name}")
    
    def _handle_miss_event(self, event):
        """Handle Miss Event."""
        target = event.get('target')
        if target:
            # Add miss effect
            pos = self._get_monster_position(target, target == self.battle_state.player_active)
            self.state.add_particle_effect(pos, 'miss', 8)
            logger.info(f"Miss: {target.name}")
    
    def _handle_stat_change_event(self, event):
        """Handle Stat Change Event."""
        target = event.get('target')
        stat = event.get('stat')
        change = event.get('change', 0)
        
        if target and stat and change != 0:
            direction = "increased" if change > 0 else "decreased"
            self.add_message(f"{target.name}'s {stat} {direction}!")
            logger.info(f"Stat change: {target.name} {stat} {change:+d}")
    
    # Enhanced Event Processing with Complete Coverage
    def process_battle_event(self, event: dict):
        """Verarbeite Battle Event - ENHANCED VERSION."""
        event_type = event.get('type')
        
        # Enhanced event routing with all EventTypes
        if event_type == 'message':
            self._handle_message_event(event)
        elif event_type == 'hp_update' or event_type == 'hp_bar':
            self._handle_hp_update_event(event)
        elif event_type == 'damage':
            self._handle_damage_event(event)
        elif event_type == 'status_change' or event_type == 'status':
            self._handle_status_event(event)
        elif event_type == 'healing':
            self._handle_healing_event(event)
        elif event_type == 'monster_faint' or event_type == 'faint':
            self._handle_faint_event(event)
        elif event_type == 'monster_switch' or event_type == 'switch':
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
        elif event_type == 'camera_shake' or event_type == 'screen_shake':
            self._handle_screen_shake_event(event)
        elif event_type == 'status_tick':
            self._handle_status_tick_event(event)
        elif event_type == 'phase_change':
            self._handle_phase_change_event(event)
        elif event_type == 'critical':
            self._handle_critical_hit_event(event)
        elif event_type == 'miss':
            self._handle_miss_event(event)
        elif event_type == 'stat_change':
            self._handle_stat_change_event(event)
        else:
            logger.warning(f"Unknown event type: {event_type}")
    
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
    
    def show_damage_number(self, target, damage, is_critical=False, is_status=False, is_super_effective=False):
        """Zeige Damage Number - VERBESSERTE POSITIONIERUNG."""
        pos = self._get_monster_position(target, target == self.battle_state.player_active)
        
        # Verbesserte Positionierung - zentriert über Monster
        if target == self.battle_state.player_active:
            # Player side - zentriert über Monster
            pos = (pos[0] + 16, pos[1] - 10)  # 16 = halbe Sprite-Breite
        else:
            # Enemy side - zentriert über Monster
            pos = (pos[0] + 16, pos[1] - 10)
        
        # Enhanced color logic
        if is_critical:
            color = (255, 255, 0)  # Yellow for critical
        elif is_super_effective:
            color = (255, 100, 0)  # Orange for super effective
        elif is_status:
            color = (255, 100, 100)  # Light red for status
        else:
            color = (255, 0, 0)  # Red for normal damage
        
        damage_num = DamageNumber(
            value=damage,
            position=pos,
            timer=2.0,
            velocity=(0, -50),
            color=color,
            is_critical=is_critical
        )
        self.damage_numbers.append(damage_num)
        
        # Also add to state for animation
        self.state.add_damage_number(damage, pos, color, is_critical)
        
        logger.info(f"✓ Damage number: {damage} at {pos} (critical: {is_critical})")
    
    def show_status_effect(self, target, status):
        """Zeige Status Effect - ENHANCED."""
        # Status effect display delegated to renderer
        if self.renderer and hasattr(self.renderer, 'show_status_effect'):
            self.renderer.show_status_effect(target, status)
        else:
            # Fallback: add message
            self.add_message(f"{target.name} ist {status}!")
        
        # Add status effect to state for animation
        if hasattr(target, 'id'):
            monster_id = target.id
        else:
            monster_id = id(target)
        
        self.state.add_status_effect(monster_id, status, 2.0)
    
    def play_faint_animation(self, monster):
        """Spiele Faint Animation - ENHANCED."""
        # Faint animation delegated to renderer
        if self.renderer and hasattr(self.renderer, 'play_faint_animation'):
            self.renderer.play_faint_animation(monster)
        else:
            # Fallback: add message
            self.add_message(f"{monster.name} ist ohnmächtig!")
        
        # Add faint animation to state
        if hasattr(monster, 'id'):
            monster_id = monster.id
        else:
            monster_id = id(monster)
        
        self.state.start_faint_animation(monster_id)
    
    def show_healing_number(self, target, healing):
        """Zeige Healing Number - ENHANCED."""
        pos = self._get_monster_position(target, target == self.battle_state.player_active)
        
        damage_num = DamageNumber(
            value=healing,
            position=pos,
            timer=2.0,
            velocity=(0, -50),
            color=(0, 255, 0)
        )
        self.damage_numbers.append(damage_num)
        
        # Also add to state for animation
        self.state.add_damage_number(healing, pos, (0, 255, 0), False)
    
    def play_appear_animation(self, monster):
        """Spiele Appear Animation - ENHANCED."""
        # Appear animation delegated to renderer
        if self.renderer and hasattr(self.renderer, 'play_appear_animation'):
            self.renderer.play_appear_animation(monster)
        else:
            # Fallback: add message
            self.add_message(f"{monster.name} erscheint!")
        
        # Add appear animation to state
        if hasattr(monster, 'id'):
            monster_id = monster.id
        else:
            monster_id = id(monster)
        
        self.state.start_appear_animation(monster_id)
    
    def show_message(self, message: str) -> None:
        """Zeige Nachricht - ENHANCED."""
        self.current_message = message
        self.message_timer = 0.0
        self.message_wait = True
        # Don't set to MESSAGE state if we're in MAIN
        if self.state.menu_state != BattleMenuState.MAIN:
            self.state.menu_state = BattleMenuState.MESSAGE
        
        logger.info(f"Message displayed: {message}")
    
    def add_message(self, message: str, wait: bool = True, duration: float = 2.0, priority: str = "normal"):
        """Füge Nachricht zur Queue hinzu - ENHANCED mit Priority-System."""
        # Sofort anzeigen
        self.show_message(message)
        
        # Priority-basierte Duration
        if priority == "important":
            duration = 3.0  # 3 Sekunden für wichtige Messages
        elif priority == "critical":
            duration = 4.0  # 4 Sekunden für kritische Messages
        elif priority == "quick":
            duration = 1.0  # 1 Sekunde für schnelle Messages
        
        # Timer für automatisches Weiterschalten setzen
        self.message_timer = duration
        
        if not wait:
            self.message_wait = False
        
        logger.info(f"✓ Message displayed: '{message}' (duration: {duration}s, priority: {priority})")
    
    def add_damage_number(self, value: int, x: int, y: int, is_critical: bool = False, 
                         is_effective: bool = False, is_heal: bool = False, is_status: bool = False) -> None:
        """Füge Schadens-Nummer hinzu - ENHANCED."""
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
        
        # Also add to state for animation
        self.state.add_damage_number(value, (x, y), color, is_critical)
    
    def trigger_screen_flash(self, intensity=128):
        """Trigger Screen Flash - ENHANCED."""
        self.screen_flash_timer = 0.2
        # Flash effect handled by renderer
        self.state.trigger_screen_flash((255, 255, 255), intensity / 255.0, 0.2)
    
    def trigger_screen_shake(self, intensity=5, duration=0.3):
        """Trigger Screen Shake - ENHANCED."""
        self.screen_shake_timer = duration
        self.screen_shake_intensity = intensity
        self.state.trigger_screen_shake(intensity, duration)