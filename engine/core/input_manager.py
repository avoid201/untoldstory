"""
Refactored Input Manager für Untold Story
Vereinfachte Version ohne Code-Duplikation
"""

import pygame
from typing import Dict, Set, Optional, Tuple, List
from dataclasses import dataclass, field


@dataclass
class InputConfig:
    """Konfiguration für Input-Mapping"""
    # Movement
    move_up: int = pygame.K_w
    move_down: int = pygame.K_s
    move_left: int = pygame.K_a
    move_right: int = pygame.K_d
    
    # Alternative arrow keys
    alt_up: int = pygame.K_UP
    alt_down: int = pygame.K_DOWN
    alt_left: int = pygame.K_LEFT
    alt_right: int = pygame.K_RIGHT
    
    # Action buttons (Pokémon-style)
    button_a: int = pygame.K_e        # Confirm/Interact
    button_b: int = pygame.K_q        # Cancel/Run
    button_x: int = pygame.K_x        # Menu
    button_y: int = pygame.K_c        # Quick Access
    
    # Alternative action buttons
    alt_confirm: int = pygame.K_SPACE
    alt_cancel: int = pygame.K_ESCAPE
    alt_run: int = pygame.K_LSHIFT
    
    # System
    pause: int = pygame.K_ESCAPE
    debug: int = pygame.K_TAB


@dataclass
class InputState:
    """Zentraler Input-Status"""
    keys_pressed: Dict[int, bool] = field(default_factory=dict)
    keys_just_pressed: Set[int] = field(default_factory=set)
    keys_just_released: Set[int] = field(default_factory=set)
    mouse_pos: Tuple[int, int] = (0, 0)
    mouse_buttons: Tuple[bool, bool, bool] = (False, False, False)


class InputManager:
    """Vereinfachter Input-Manager ohne Code-Duplikation"""
    
    def __init__(self, config: Optional[InputConfig] = None):
        self.config = config or InputConfig()
        self.state = InputState()
        self.input_map = self._build_input_map()
        self.key_names = self._create_key_name_mapping()
        
        # Enhanced features
        self.key_repeat_timers: Dict[int, float] = {}
        self.key_repeat_delay = 0.4
        self.key_repeat_rate = 0.1
        self.input_buffer: Dict[str, float] = {}
        self.buffer_window = 0.2
        self.combo_buffer: List[Tuple[str, float]] = []
        self.combo_timeout = 0.5
        
        # Debug system
        self.debug_enabled = True
        self.input_log: List[Dict] = []
        self.max_log_entries = 100
        self.ignored_keys: Set[int] = set()
        
        print("🔍 INPUT DEBUG: Vollständiger Keyboard-Input-Debug aktiviert!")
    
    def _build_input_map(self) -> Dict[str, List[int]]:
        """Baut das Input-Mapping auf"""
        return {
            'move_up': [self.config.move_up, self.config.alt_up],
            'move_down': [self.config.move_down, self.config.alt_down],
            'move_left': [self.config.move_left, self.config.alt_left],
            'move_right': [self.config.move_right, self.config.alt_right],
            'confirm': [self.config.button_a, self.config.alt_confirm],
            'cancel': [self.config.button_b, self.config.alt_cancel],
            'run': [self.config.button_b, self.config.alt_run],
            'menu': [self.config.button_x],
            'quick': [self.config.button_y],
            'pause': [self.config.pause],
            'debug': [self.config.debug]
        }
    
    def _create_key_name_mapping(self) -> Dict[int, str]:
        """Erstellt eine Mapping von Key-Codes zu lesbaren Namen"""
        key_names = {}
        
        # Standard-Tasten
        for key_name in dir(pygame):
            if key_name.startswith('K_'):
                try:
                    key_code = getattr(pygame, key_name)
                    key_names[key_code] = key_name[2:]  # Entferne 'K_' Prefix
                except:
                    pass
        
        # Spezielle Tasten hinzufügen
        key_names[pygame.K_UNKNOWN] = "UNKNOWN"
        
        return key_names
    
    def _get_key_name(self, key_code: int) -> str:
        """Gibt den lesbaren Namen einer Taste zurück"""
        return self.key_names.get(key_code, f"KEY_{key_code}")
    
    def _log_input(self, event_type: str, key_code: int, action: str = "") -> None:
        """Loggt einen Input-Event für Debug-Zwecke"""
        if key_code in self.ignored_keys:
            return
            
        key_name = self._get_key_name(key_code)
        timestamp = pygame.time.get_ticks()
        
        log_entry = {
            'timestamp': timestamp,
            'event_type': event_type,
            'key_code': key_code,
            'key_name': key_name,
            'action': action,
            'frame': pygame.time.get_ticks() // 16
        }
        
        self.input_log.append(log_entry)
        
        # Log-Einträge begrenzen
        if len(self.input_log) > self.max_log_entries:
            self.input_log.pop(0)
        
        # Konsolen-Ausgabe
        action_text = f" -> {action}" if action else ""
        print(f"🔍 INPUT: {event_type:8} | {key_name:12} (Code: {key_code:3}){action_text}")
    
    def _check_action_for_key(self, key_code: int) -> str:
        """Prüft ob eine Taste eine Aktion auslöst und gibt den Aktionstyp zurück"""
        actions = []
        
        # Movement prüfen
        if key_code in [self.config.move_up, self.config.alt_up]:
            actions.append("MOVE_UP")
        if key_code in [self.config.move_down, self.config.alt_down]:
            actions.append("MOVE_DOWN")
        if key_code in [self.config.move_left, self.config.alt_left]:
            actions.append("MOVE_LEFT")
        if key_code in [self.config.move_right, self.config.alt_right]:
            actions.append("MOVE_RIGHT")
        
        # Action buttons prüfen
        if key_code in [self.config.button_a, self.config.alt_confirm]:
            actions.append("CONFIRM/INTERACT")
        if key_code in [self.config.button_b, self.config.alt_cancel]:
            actions.append("CANCEL/RUN")
        if key_code == self.config.button_x:
            actions.append("MENU")
        if key_code == self.config.button_y:
            actions.append("QUICK_ACCESS")
        
        # System buttons
        if key_code == self.config.pause:
            actions.append("PAUSE")
        if key_code == self.config.debug:
            actions.append("DEBUG_TOGGLE")
        
        if not actions:
            return "KEINE_AKTION"
        
        return " + ".join(actions)
    
    def update(self, dt: float = 0.016) -> None:
        """Update input state with enhanced features - call once per frame"""
        import time
        current_time = time.time()
        
        # Clear just pressed/released
        self.state.keys_just_pressed.clear()
        self.state.keys_just_released.clear()
        
        # Get current key state
        keys = pygame.key.get_pressed()
        
        # Check for just pressed/released and handle repeats
        for key in range(len(keys)):
            was_pressed = self.state.keys_pressed.get(key, False)
            is_pressed = keys[key]
            
            if is_pressed and not was_pressed:
                self.state.keys_just_pressed.add(key)
                self.key_repeat_timers[key] = current_time + self.key_repeat_delay
                
                # Debug-Log für gedrückte Taste
                action = self._check_action_for_key(key)
                self._log_input("KEYDOWN", key, action)
                
            elif was_pressed and not is_pressed:
                self.state.keys_just_released.add(key)
                if key in self.key_repeat_timers:
                    del self.key_repeat_timers[key]
                
                # Debug-Log für losgelassene Taste
                self._log_input("KEYUP", key, "RELEASED")
                
            elif is_pressed and key in self.key_repeat_timers:
                # Handle key repeat
                if current_time >= self.key_repeat_timers[key]:
                    self.state.keys_just_pressed.add(key)
                    self.key_repeat_timers[key] = current_time + self.key_repeat_rate
                    
                    # Debug-Log für wiederholte Taste
                    action = self._check_action_for_key(key)
                    self._log_input("REPEAT", key, f"REPEAT: {action}")
            
            self.state.keys_pressed[key] = is_pressed
        
        # Update input buffer - clean expired entries
        expired_inputs = []
        for input_name, timestamp in self.input_buffer.items():
            if current_time - timestamp > self.buffer_window:
                expired_inputs.append(input_name)
        for input_name in expired_inputs:
            del self.input_buffer[input_name]
        
        # Update combo buffer - clean expired entries
        self.combo_buffer = [(combo, timestamp) for combo, timestamp in self.combo_buffer 
                            if current_time - timestamp <= self.combo_timeout]
    
    def is_pressed(self, input_name: str) -> bool:
        """Check if a logical input is currently pressed"""
        if input_name in self.input_map:
            for key in self.input_map[input_name]:
                if self.state.keys_pressed.get(key, False):
                    return True
        return False
    
    def is_just_pressed(self, input_name: str) -> bool:
        """Check if a logical input was just pressed this frame"""
        if input_name in self.input_map:
            for key in self.input_map[input_name]:
                if key in self.state.keys_just_pressed:
                    return True
        return False
    
    def is_just_released(self, input_name: str) -> bool:
        """Check if a logical input was just released this frame"""
        if input_name in self.input_map:
            for key in self.input_map[input_name]:
                if key in self.state.keys_just_released:
                    return True
        return False
    
    def get_movement_vector(self) -> Tuple[int, int]:
        """Get the current movement input as a vector"""
        x = 0
        y = 0
        
        if self.is_pressed('move_left'):
            x = -1
        elif self.is_pressed('move_right'):
            x = 1
        
        if self.is_pressed('move_up'):
            y = -1
        elif self.is_pressed('move_down'):
            y = 1
        
        return (x, y)
    
    def buffer_input(self, input_name: str) -> None:
        """Buffer an input for responsive gameplay"""
        import time
        self.input_buffer[input_name] = time.time()
    
    def consume_buffered_input(self, input_name: str) -> bool:
        """Check and consume a buffered input"""
        if input_name in self.input_buffer:
            del self.input_buffer[input_name]
            return True
        return False
    
    def register_combo(self, input_name: str) -> None:
        """Register an input for combo detection"""
        import time
        self.combo_buffer.append((input_name, time.time()))
    
    def check_combo(self, combo_sequence: List[str]) -> bool:
        """Check if a combo sequence was input recently"""
        if len(self.combo_buffer) < len(combo_sequence):
            return False
        
        # Check last N inputs match the combo
        recent_inputs = [combo for combo, _ in self.combo_buffer[-len(combo_sequence):]]
        return recent_inputs == combo_sequence
    
    def set_repeat_settings(self, delay: float = 0.4, rate: float = 0.1) -> None:
        """Configure key repeat timing"""
        self.key_repeat_delay = delay
        self.key_repeat_rate = rate
    
    def get_input_debug_info(self) -> Dict:
        """Get debug information about current input state"""
        return {
            'pressed_keys': [k for k, v in self.state.keys_pressed.items() if v],
            'just_pressed': list(self.state.keys_just_pressed),
            'just_released': list(self.state.keys_just_released),
            'buffered_inputs': list(self.input_buffer.keys()),
            'combo_buffer': [combo for combo, _ in self.combo_buffer],
            'repeat_timers': len(self.key_repeat_timers)
        }

    def add_ignored_key(self, key_code: int) -> None:
        """Fügt eine Taste zur Ignore-Liste hinzu (wird nicht geloggt)"""
        self.ignored_keys.add(key_code)
        print(f"🔍 INPUT DEBUG: Taste {self._get_key_name(key_code)} wird ignoriert")
    
    def remove_ignored_key(self, key_code: int) -> None:
        """Entfernt eine Taste von der Ignore-Liste"""
        if key_code in self.ignored_keys:
            self.ignored_keys.remove(key_code)
            print(f"🔍 INPUT DEBUG: Taste {self._get_key_name(key_code)} wird wieder geloggt")
    
    def get_input_log_summary(self) -> Dict:
        """Gibt eine Zusammenfassung des Input-Logs zurück"""
        if not self.input_log:
            return {"message": "Keine Inputs geloggt"}
        
        # Gruppiere nach Event-Typ
        event_counts = {}
        action_counts = {}
        
        for entry in self.input_log:
            event_type = entry['event_type']
            action = entry['action']
            
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
            action_counts[action] = action_counts.get(action, 0) + 1
        
        return {
            'total_events': len(self.input_log),
            'event_counts': event_counts,
            'action_counts': action_counts,
            'recent_events': self.input_log[-10:] if len(self.input_log) >= 10 else self.input_log
        }
    
    def clear_input_log(self) -> None:
        """Löscht den Input-Log"""
        self.input_log.clear()
        print("🔍 INPUT DEBUG: Input-Log gelöscht")
    
    def print_input_log_summary(self) -> None:
        """Gibt eine Zusammenfassung des Input-Logs in der Konsole aus"""
        summary = self.get_input_log_summary()
        
        print("\n" + "="*50)
        print("🔍 INPUT DEBUG - ZUSAMMENFASSUNG")
        print("="*50)
        
        if 'message' in summary:
            print(summary['message'])
        else:
            print(f"Gesamtanzahl Events: {summary['total_events']}")
            print("\nEvent-Typen:")
            for event_type, count in summary['event_counts'].items():
                print(f"  {event_type}: {count}")
            
            print("\nAktionen:")
            for action, count in summary['action_counts'].items():
                print(f"  {action}: {count}")
            
            print("\nLetzte 10 Events:")
            for entry in summary['recent_events']:
                print(f"  Frame {entry['frame']}: {entry['event_type']} {entry['key_name']} -> {entry['action']}")
        
        print("="*50 + "\n")
