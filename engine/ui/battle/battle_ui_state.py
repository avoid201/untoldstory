"""
Battle UI State - State Management für modulare Battle UI
Zerlegt aus der monolithischen battle_ui.py

Verantwortlichkeiten:
- BattleMenuState Enum
- BattleSprite und DamageNumber Dataclasses
- State Management Utilities
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Tuple, List, Optional, Dict, Any
import pygame
import time


class BattleMenuState(Enum):
    """Battle menu states - DQM style."""
    MAIN = auto()           # Hauptmenü mit 6 Optionen
    MOVE_SELECT = auto()    # Move-Auswahl nach Kategorien
    ITEM_SELECT = auto()    # Item-Menü mit Kategorien
    SWITCH_SELECT = auto()  # Team-Wechsel
    SCOUT = auto()          # Monster-Analyse
    WAITING = auto()        # Warte auf Animation
    MESSAGE = auto()        # Zeige Nachricht
    WAIT_FOR_INPUT = auto() # Warte auf SPACE/ENTER Input
    MESSAGE_DISPLAY = auto() # Zeige Message mit Prompt
    ACTION_ANIMATION = auto() # Attack-Animation läuft
    SKILL_SELECT = auto()   # Erweiterte Skill-Auswahl
    ENHANCED_ITEM = auto()  # Erweiterte Item-Auswahl
    BATTLE_RESULT = auto()  # Victory/Defeat Screen


@dataclass
class MessageQueue:
    """Message Queue System für sequenzielle Battle-Nachrichten."""
    
    messages: List[Dict[str, Any]] = field(default_factory=list)
    current_message: Optional[Dict[str, Any]] = None
    is_blocking: bool = False
    input_wait: bool = False
    
    def add_message(self, text: str, duration: float = 2.0, priority: str = "normal", 
                   style: str = "normal", blocking: bool = True) -> None:
        """Füge Message zur Queue hinzu."""
        message_data = {
            'text': text,
            'duration': duration,
            'priority': priority,
            'style': style,
            'blocking': blocking,
            'timestamp': time.time()
        }
        
        # Sortiere nach Priorität einfügen
        if priority == "critical":
            # Critical Messages am Anfang, aber in FIFO-Reihenfolge
            # Finde letzte Critical Message und füge danach ein
            insert_index = 0
            for i, msg in enumerate(self.messages):
                if msg['priority'] == "critical":
                    insert_index = i + 1
                else:
                    break
            self.messages.insert(insert_index, message_data)
        elif priority == "important":
            # Finde erste normale Message und füge davor ein
            insert_index = len(self.messages)
            for i, msg in enumerate(self.messages):
                if msg['priority'] == "normal":
                    insert_index = i
                    break
            self.messages.insert(insert_index, message_data)
        else:
            self.messages.append(message_data)
    
    def get_next_message(self) -> Optional[Dict[str, Any]]:
        """Hole nächste Message aus der Queue."""
        if self.messages:
            self.current_message = self.messages.pop(0)
            self.is_blocking = self.current_message.get('blocking', True)
            self.input_wait = self.is_blocking
            return self.current_message
        return None
    
    def has_pending_messages(self) -> bool:
        """Prüfe ob Messages in der Queue sind."""
        return len(self.messages) > 0 or self.current_message is not None
    
    def get_current_message(self) -> str:
        """Get current message text."""
        if self.current_message and isinstance(self.current_message, dict):
            return self.current_message.get('text', '')
        return ""
    
    def clear_all(self) -> None:
        """Lösche alle Messages."""
        self.messages.clear()
        self.current_message = None
        self.is_blocking = False
        self.input_wait = False
    
    def process_input(self, action: str) -> bool:
        """Verarbeite Input für Message-Queue."""
        if action in ["confirm", "cancel"] and self.input_wait:
            # Message bestätigt, current_message löschen
            self.current_message = None
            self.input_wait = False
            self.is_blocking = False
            return True
        return False


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


@dataclass
class BattleUIState:
    """Complete battle UI state management."""
    
    # Menu state
    menu_state: BattleMenuState = BattleMenuState.MAIN
    selected_option: int = 0
    selected_move: int = 0
    selected_item: int = 0
    selected_team_member: int = 0
    
    # Battle participants
    player_team: List = field(default_factory=list)
    enemy_team: List = field(default_factory=list)
    player_active: Optional[Any] = None
    enemy_active: Optional[Any] = None
    
    # Move categories
    current_move_category: int = 0  # 0: Physical, 1: Magic, 2: Status
    
    # Item categories  
    current_item_category: int = 0  # 0: Healing, 1: Battle, 2: Meat
    
    # Message system - NEW MESSAGE QUEUE SYSTEM
    current_message: str = ""
    message_timer: float = 0.0
    message_wait: bool = False
    message_queue_system: MessageQueue = field(default_factory=MessageQueue)
    
    # Input state
    waiting_for_input: bool = True
    
    # Screen effects
    screen_flash_timer: float = 0.0
    screen_flash_color: Tuple[int, int, int] = (255, 255, 255)
    screen_flash_intensity: float = 0.0
    screen_shake_timer: float = 0.0
    screen_shake_intensity: float = 0.0
    shake_offset: Tuple[int, int] = (0, 0)
    
    # Taming state - simplified for direct meat usage
    taming_state: Dict[str, Any] = field(default_factory=lambda: {
        "meat_bonus": 0.0,
        "animation_phase": 0
    })
    
    # NEUE Animation tracking structures
    animations: Dict[str, Any] = field(default_factory=lambda: {
        "hp_bars": {},  # monster_id -> animation data
        "damage_numbers": [],  # List of active damage numbers
        "status_effects": {},  # monster_id -> effect data
        "faint": {},  # monster_id -> faint animation timer
        "appear": {},  # monster_id -> appear animation timer
        "attacks": [],  # List of attack animations
        "particles": [],  # List of particle effects
        "screen_effects": {  # Global screen effects
            "flash": {"active": False, "color": (255, 255, 255), "timer": 0, "intensity": 0},
            "shake": {"active": False, "intensity": 0, "timer": 0, "offset": (0, 0)},
            "fade": {"active": False, "alpha": 0, "target_alpha": 0, "speed": 1.0}
        }
    })
    
    # Action tracking
    pending_action: Optional[Dict[str, Any]] = None
    last_action_time: float = 0.0
    action_cooldown: float = 0.5
    
    # Victory/Defeat screens
    show_victory_screen: bool = False
    show_defeat_screen: bool = False
    victory_screen_data: Optional[Dict[str, Any]] = None
    defeat_screen_data: Optional[Dict[str, Any]] = None
    
    # Performance tracking
    fps_counter: int = 0
    fps_timer: float = 0.0
    current_fps: int = 60
    
    def reset(self) -> None:
        """Reset state to initial values."""
        self.menu_state = BattleMenuState.MAIN
        self.selected_option = 0
        self.selected_move = 0
        self.selected_item = 0
        self.selected_team_member = 0
        
        self.player_team.clear()
        self.enemy_team.clear()
        self.player_active = None
        self.enemy_active = None
        
        self.current_message = ""
        self.message_timer = 0.0
        self.message_wait = False
        
        self.screen_flash_timer = 0.0
        self.screen_shake_timer = 0.0
        
        # Reset all animations
        self.animations["hp_bars"].clear()
        self.animations["damage_numbers"].clear()
        self.animations["status_effects"].clear()
        self.animations["faint"].clear()
        self.animations["appear"].clear()
        self.animations["attacks"].clear()
        self.animations["particles"].clear()
        
        self.pending_action = None
        self.last_action_time = 0.0
        
        # Reset Victory/Defeat screens
        self.show_victory_screen = False
        self.show_defeat_screen = False
        self.victory_screen_data = None
        self.defeat_screen_data = None
    
    def set_waiting_for_input(self, waiting: bool) -> None:
        """Set waiting for input state."""
        self.message_wait = waiting
    
    def is_waiting_for_input(self) -> bool:
        """Check if waiting for input."""
        return self.message_wait
    
    def set_phase(self, phase: str) -> None:
        """Set battle phase and update input state accordingly."""
        if phase in ['input', 'start']:
            self.message_wait = True
        elif phase in ['execution', 'end']:
            self.message_wait = False
    
    def validate_input_state(self) -> bool:
        """Validate that input state is consistent."""
        # Check if message_wait is properly set
        if not hasattr(self, 'message_wait'):
            self.message_wait = False
            return False
        
        # Check if menu state is valid
        if not hasattr(self, 'menu_state'):
            self.menu_state = BattleMenuState.MAIN
            return False
        
        return True
    
    def add_hp_animation(self, monster_id: Any, old_hp: int, new_hp: int, max_hp: int, duration: float = 0.5) -> None:
        """Add HP bar animation - OPTIMIERT FÜR SOFORTIGE UPDATES."""
        self.animations["hp_bars"][monster_id] = {
            "old_hp": old_hp,
            "new_hp": new_hp,
            "max_hp": max_hp,
            "current": old_hp,
            "timer": duration,
            "original_timer": duration,  # Für bessere Interpolation
            "active": True,
            "speed": 100  # Schnelle Animation
        }
    
    def add_damage_number(self, value: int, pos: Tuple[int, int], 
                         color: Tuple[int, int, int] = (255, 255, 255),
                         is_critical: bool = False) -> None:
        """Add damage number animation."""
        self.animations["damage_numbers"].append({
            "value": value,
            "pos": list(pos),  # Make mutable
            "velocity": [0, -50],  # Upward movement
            "color": color,
            "timer": 1.5,
            "is_critical": is_critical,
            "scale": 1.5 if is_critical else 1.0
        })
    
    def add_status_effect(self, monster_id: Any, status: str, duration: float = 2.0) -> None:
        """Add status effect indicator."""
        self.animations["status_effects"][monster_id] = {
            "status": status,
            "timer": duration,
            "flash": True,
            "flash_timer": 0.0
        }
    
    def start_faint_animation(self, monster_id: Any) -> None:
        """Start faint animation for monster."""
        self.animations["faint"][monster_id] = 1.0
    
    def start_appear_animation(self, monster_id: Any) -> None:
        """Start appear animation for monster."""
        self.animations["appear"][monster_id] = 1.0
    
    def add_attack_animation(self, attacker_id: Any, target_id: Any, 
                            attack_type: str = "physical") -> None:
        """Add attack animation."""
        self.animations["attacks"].append({
            "attacker": attacker_id,
            "target": target_id,
            "type": attack_type,
            "phase": 0,
            "timer": 1.0
        })
    
    def add_particle_effect(self, pos: Tuple[int, int], effect_type: str = "sparkle",
                           count: int = 10) -> None:
        """Add particle effect."""
        import random
        for _ in range(count):
            self.animations["particles"].append({
                "pos": list(pos),
                "velocity": [random.uniform(-50, 50), random.uniform(-50, 50)],
                "type": effect_type,
                "timer": random.uniform(0.5, 1.5),
                "size": random.uniform(2, 6),
                "color": (255, 255, random.randint(0, 255))
            })
    
    def trigger_screen_flash(self, color: Tuple[int, int, int] = (255, 255, 255),
                           intensity: float = 0.8, duration: float = 0.3) -> None:
        """Trigger screen flash effect."""
        self.animations["screen_effects"]["flash"] = {
            "active": True,
            "color": color,
            "timer": duration,
            "intensity": intensity
        }
    
    def trigger_screen_shake(self, intensity: float = 5.0, duration: float = 0.5) -> None:
        """Trigger screen shake effect."""
        self.animations["screen_effects"]["shake"] = {
            "active": True,
            "intensity": intensity,
            "timer": duration,
            "offset": (0, 0)
        }
    
    def update_animations(self, dt: float) -> None:
        """Update all animations - OPTIMIERT FÜR SOFORTIGE UPDATES."""
        # Update HP bar animations - verbesserte Interpolation
        for monster_id, anim in list(self.animations["hp_bars"].items()):
            if anim["active"]:
                anim["timer"] -= dt
                
                if anim["timer"] <= 0:
                    # Animation beendet - finale Werte setzen
                    anim["current"] = anim["new_hp"]
                    anim["active"] = False
                else:
                    # Verbesserte Interpolation für flüssigere Animation
                    original_timer = 1.0 if "original_timer" not in anim else anim["original_timer"]
                    progress = 1.0 - (anim["timer"] / original_timer)
                    
                    # Smooth interpolation mit easing
                    import math
                    eased_progress = 1.0 - math.pow(1.0 - progress, 3)  # Ease-out cubic
                    anim["current"] = anim["old_hp"] + (anim["new_hp"] - anim["old_hp"]) * eased_progress
        
        # Update damage numbers
        for damage in self.animations["damage_numbers"][:]:
            damage["pos"][0] += damage["velocity"][0] * dt
            damage["pos"][1] += damage["velocity"][1] * dt
            damage["timer"] -= dt
            
            if damage["timer"] <= 0:
                self.animations["damage_numbers"].remove(damage)
        
        # Update status effects
        for monster_id, effect in list(self.animations["status_effects"].items()):
            effect["timer"] -= dt
            effect["flash_timer"] += dt
            
            if effect["flash_timer"] > 0.2:
                effect["flash"] = not effect["flash"]
                effect["flash_timer"] = 0
            
            if effect["timer"] <= 0:
                del self.animations["status_effects"][monster_id]
        
        # Update faint animations
        for monster_id, timer in list(self.animations["faint"].items()):
            self.animations["faint"][monster_id] -= dt
            if self.animations["faint"][monster_id] <= 0:
                del self.animations["faint"][monster_id]
        
        # Update appear animations
        for monster_id, timer in list(self.animations["appear"].items()):
            self.animations["appear"][monster_id] -= dt
            if self.animations["appear"][monster_id] <= 0:
                del self.animations["appear"][monster_id]
        
        # Update attack animations
        for attack in self.animations["attacks"][:]:
            attack["timer"] -= dt
            if attack["timer"] <= 0:
                self.animations["attacks"].remove(attack)
        
        # Update particles
        for particle in self.animations["particles"][:]:
            particle["pos"][0] += particle["velocity"][0] * dt
            particle["pos"][1] += particle["velocity"][1] * dt
            particle["timer"] -= dt
            
            if particle["timer"] <= 0:
                self.animations["particles"].remove(particle)
        
        # Update screen effects
        if self.animations["screen_effects"]["flash"]["active"]:
            self.animations["screen_effects"]["flash"]["timer"] -= dt
            if self.animations["screen_effects"]["flash"]["timer"] <= 0:
                self.animations["screen_effects"]["flash"]["active"] = False
        
        if self.animations["screen_effects"]["shake"]["active"]:
            self.animations["screen_effects"]["shake"]["timer"] -= dt
            if self.animations["screen_effects"]["shake"]["timer"] <= 0:
                self.animations["screen_effects"]["shake"]["active"] = False
            else:
                # Calculate shake offset
                import random
                intensity = self.animations["screen_effects"]["shake"]["intensity"]
                self.animations["screen_effects"]["shake"]["offset"] = (
                    random.uniform(-intensity, intensity),
                    random.uniform(-intensity, intensity)
                )
    
    def get_selected_move_category(self) -> str:
        """Get selected move category as string."""
        categories = ["PHYSISCH", "MAGISCH", "STATUS"]
        return categories[self.current_move_category]
    
    def get_selected_item_category(self) -> str:
        """Get selected item category as string."""
        categories = ["HEILUNG", "KAMPF-ITEMS", "FLEISCH"]
        return categories[self.current_item_category]
    
    def is_animating(self) -> bool:
        """Check if any animations are active."""
        # Check all animation types
        if self.animations["damage_numbers"]:
            return True
        if any(anim["active"] for anim in self.animations["hp_bars"].values()):
            return True
        if self.animations["faint"] or self.animations["appear"]:
            return True
        if self.animations["attacks"] or self.animations["particles"]:
            return True
        if self.animations["screen_effects"]["flash"]["active"]:
            return True
        if self.animations["screen_effects"]["shake"]["active"]:
            return True
        
        return False
    
    # ===== MESSAGE QUEUE SYSTEM =====
    
    def clear_all_messages(self) -> None:
        """Clear all message queues."""
        self.current_message = ""
        self.message_timer = 0.0
        self.message_queue_system.clear_all()
    
    def add_message_to_queue(self, text: str, duration: float = 2.0, priority: str = "normal", 
                           style: str = "normal", blocking: bool = True) -> None:
        """Füge Message zur neuen Queue hinzu."""
        self.message_queue_system.add_message(text, duration, priority, style, blocking)
        
        # Sofort anzeigen wenn keine andere Message aktiv
        if not self.message_queue_system.current_message:
            self.message_queue_system.get_next_message()
            if self.message_queue_system.current_message:
                self.current_message = self.message_queue_system.current_message['text']
                self.message_timer = self.message_queue_system.current_message['duration']
                self.message_wait = self.message_queue_system.input_wait
                self.menu_state = BattleMenuState.MESSAGE_DISPLAY
    
    def process_message_input(self, action: str) -> bool:
        """Verarbeite Input für Message-Queue."""
        result = self.message_queue_system.process_input(action)
        
        # Wenn Input verarbeitet wurde, nächste Message laden
        if result and self.message_queue_system.has_pending_messages():
            self.message_queue_system.get_next_message()
            if self.message_queue_system.current_message:
                self.current_message = self.message_queue_system.current_message['text']
                self.message_timer = self.message_queue_system.current_message['duration']
                self.message_wait = self.message_queue_system.input_wait
                self.menu_state = BattleMenuState.MESSAGE_DISPLAY
        
        return result
    
    def get_current_message_data(self) -> Optional[Dict[str, Any]]:
        """Hole aktuelle Message-Daten."""
        return self.message_queue_system.current_message
    
    def get_next_message(self) -> Optional[Dict[str, Any]]:
        """Get next message from queue."""
        return self.message_queue_system.get_next_message()

    def has_pending_messages(self) -> bool:
        """Check if there are pending messages."""
        return self.message_queue_system.has_pending_messages()

    def update_message_timer(self, dt: float) -> None:
        """Update message timer and handle message transitions."""
        if self.message_timer > 0:
            self.message_timer -= dt
            if self.message_timer <= 0:
                # Current message finished, get next one
                next_message = self.get_next_message()
                if next_message:
                    self.current_message = next_message['text']
                    self.message_timer = next_message['duration']
                    self.message_wait = True
                    # CRITICAL: Keep menu state as MESSAGE_DISPLAY
                    self.menu_state = BattleMenuState.MESSAGE_DISPLAY
                else:
                    # No more messages, return to main menu
                    self.current_message = ""
                    self.message_wait = False
                    self.menu_state = BattleMenuState.MAIN


