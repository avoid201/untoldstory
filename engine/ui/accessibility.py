"""
Accessibility-System für Untold Story
Implementiert Keyboard-Shortcuts, Tooltips und visuelle Hilfen für bessere Benutzerfreundlichkeit
"""

import pygame
from typing import Dict, List, Tuple, Optional, Callable, Any
from dataclasses import dataclass
from enum import Enum, auto
from engine.core.config import Colors


class AccessibilityLevel(Enum):
    """Accessibility-Stufen."""
    BASIC = auto()
    ENHANCED = auto()
    FULL = auto()


class VisualAid(Enum):
    """Arten von visuellen Hilfen."""
    HIGHLIGHT = auto()
    OUTLINE = auto()
    GLOW = auto()
    PULSE = auto()
    ARROW = auto()


@dataclass
class KeyboardShortcut:
    """Ein Keyboard-Shortcut."""
    key: str
    description: str
    callback: Callable
    category: str
    enabled: bool = True


@dataclass
class VisualAidConfig:
    """Konfiguration für visuelle Hilfen."""
    aid_type: VisualAid
    color: Tuple[int, int, int]
    intensity: float
    duration: float
    enabled: bool = True


class AccessibilityManager:
    """Verwaltet alle Accessibility-Features."""
    
    def __init__(self):
        self.accessibility_level = AccessibilityLevel.ENHANCED
        self.keyboard_shortcuts: Dict[str, KeyboardShortcut] = {}
        self.visual_aids: Dict[str, VisualAidConfig] = {}
        self.tooltips_enabled = True
        self.high_contrast_mode = False
        self.large_text_mode = False
        self.sound_feedback = True
        
        # Standard-Shortcuts einrichten
        self._setup_default_shortcuts()
        self._setup_default_visual_aids()
    
    def _setup_default_shortcuts(self) -> None:
        """Richtet Standard-Keyboard-Shortcuts ein."""
        shortcuts = [
            ("i", "Inventar öffnen", self._open_inventory, "Navigation"),
            ("p", "Team anzeigen", self._open_party, "Navigation"),
            ("q", "Quest-Log öffnen", self._open_quests, "Navigation"),
            ("m", "Karte öffnen", self._open_map, "Navigation"),
            ("s", "Speichern", self._save_game, "Game"),
            ("l", "Laden", self._load_game, "Game"),
            ("ESC", "Zurück/Abbrechen", self._go_back, "Navigation"),
            ("TAB", "Debug-Info", self._toggle_debug, "Debug"),
            ("F1", "Hilfe", self._show_help, "Help"),
            ("F11", "Vollbild", self._toggle_fullscreen, "Display")
        ]
        
        for key, description, callback, category in shortcuts:
            self.add_shortcut(key, description, callback, category)
    
    def _setup_default_visual_aids(self) -> None:
        """Richtet Standard-visuelle Hilfen ein."""
        aids = [
            ("interactive_objects", VisualAid.GLOW, Colors.YELLOW, 0.8, 2.0),
            ("important_items", VisualAid.PULSE, Colors.RED, 1.0, 1.5),
            ("navigation_hints", VisualAid.ARROW, Colors.CYAN, 0.6, 3.0),
            ("danger_zones", VisualAid.OUTLINE, Colors.RED, 0.9, 1.0)
        ]
        
        for name, aid_type, color, intensity, duration in aids:
            self.add_visual_aid(name, aid_type, color, intensity, duration)
    
    def add_shortcut(self, key: str, description: str, callback: Callable, 
                     category: str) -> None:
        """Fügt einen Keyboard-Shortcut hinzu."""
        self.keyboard_shortcuts[key] = KeyboardShortcut(
            key=key, description=description, callback=callback, 
            category=category
        )
    
    def add_visual_aid(self, name: str, aid_type: VisualAid, color: Tuple[int, int, int],
                       intensity: float, duration: float) -> None:
        """Fügt eine visuelle Hilfe hinzu."""
        self.visual_aids[name] = VisualAidConfig(
            aid_type=aid_type, color=color, intensity=intensity, 
            duration=duration
        )
    
    def handle_keyboard_event(self, event: pygame.event.Event) -> bool:
        """Behandelt Keyboard-Events für Shortcuts."""
        if event.type != pygame.KEYDOWN:
            return False
        
        # Key identifizieren
        key_name = self._get_key_name(event)
        
        if key_name in self.keyboard_shortcuts:
            shortcut = self.keyboard_shortcuts[key_name]
            if shortcut.enabled:
                try:
                    shortcut.callback()
                    if self.sound_feedback:
                        self._play_shortcut_sound()
                    return True
                except Exception as e:
                    print(f"Fehler beim Ausführen von Shortcut {key_name}: {e}")
        
        return False
    
    def _get_key_name(self, event: pygame.event.Event) -> str:
        """Konvertiert ein pygame-Event zu einem Key-Namen."""
        if event.key == pygame.K_ESCAPE:
            return "ESC"
        elif event.key == pygame.K_TAB:
            return "TAB"
        elif event.key == pygame.K_F1:
            return "F1"
        elif event.key == pygame.K_F11:
            return "F11"
        else:
            return event.unicode.lower()
    
    def _play_shortcut_sound(self) -> None:
        """Spielt einen Sound für erfolgreiche Shortcuts ab."""
        # Einfacher Beep-Sound
        try:
            # Hier könnte ein echtes Sound-System integriert werden
            pass
        except:
            pass
    
    def get_shortcuts_by_category(self) -> Dict[str, List[KeyboardShortcut]]:
        """Gibt Shortcuts nach Kategorien gruppiert zurück."""
        categories = {}
        for shortcut in self.keyboard_shortcuts.values():
            if shortcut.category not in categories:
                categories[shortcut.category] = []
            categories[shortcut.category].append(shortcut)
        return categories
    
    def toggle_accessibility_level(self) -> None:
        """Wechselt zwischen Accessibility-Stufen."""
        levels = list(AccessibilityLevel)
        current_index = levels.index(self.accessibility_level)
        next_index = (current_index + 1) % len(levels)
        self.accessibility_level = levels[next_index]
        
        # Features entsprechend der Stufe aktivieren/deaktivieren
        self._update_accessibility_features()
    
    def _update_accessibility_features(self) -> None:
        """Aktualisiert Features basierend auf der Accessibility-Stufe."""
        if self.accessibility_level == AccessibilityLevel.BASIC:
            self.tooltips_enabled = False
            self.high_contrast_mode = False
            self.large_text_mode = False
        elif self.accessibility_level == AccessibilityLevel.ENHANCED:
            self.tooltips_enabled = True
            self.high_contrast_mode = False
            self.large_text_mode = False
        elif self.accessibility_level == AccessibilityLevel.FULL:
            self.tooltips_enabled = True
            self.high_contrast_mode = True
            self.large_text_mode = True
    
    # Standard-Shortcut-Callbacks
    def _open_inventory(self) -> None:
        print("Öffne Inventar...")
    
    def _open_party(self) -> None:
        print("Öffne Team...")
    
    def _open_quests(self) -> None:
        print("Öffne Quest-Log...")
    
    def _open_map(self) -> None:
        print("Öffne Karte...")
    
    def _save_game(self) -> None:
        print("Speichere Spiel...")
    
    def _load_game(self) -> None:
        print("Lade Spiel...")
    
    def _go_back(self) -> None:
        print("Gehe zurück...")
    
    def _toggle_debug(self) -> None:
        print("Debug-Modus umschalten...")
    
    def _show_help(self) -> None:
        print("Zeige Hilfe...")
    
    def _toggle_fullscreen(self) -> None:
        print("Vollbild umschalten...")


class VisualAidRenderer:
    """Rendert visuelle Hilfen."""
    
    def __init__(self, accessibility_manager: AccessibilityManager):
        self.accessibility_manager = accessibility_manager
        self.active_aids: Dict[str, Dict[str, Any]] = {}
        self.current_time = 0.0
    
    def add_visual_aid(self, name: str, position: Tuple[int, int], 
                       size: Tuple[int, int], aid_type: str) -> None:
        """Fügt eine aktive visuelle Hilfe hinzu."""
        if aid_type in self.accessibility_manager.visual_aids:
            config = self.accessibility_manager.visual_aids[aid_type]
            
            self.active_aids[name] = {
                'position': position,
                'size': size,
                'config': config,
                'start_time': self.current_time,
                'animation_progress': 0.0
            }
    
    def remove_visual_aid(self, name: str) -> None:
        """Entfernt eine visuelle Hilfe."""
        if name in self.active_aids:
            del self.active_aids[name]
    
    def update(self, dt: float) -> None:
        """Aktualisiert alle visuellen Hilfen."""
        self.current_time += dt
        
        for aid_name, aid_data in list(self.active_aids.items()):
            config = aid_data['config']
            elapsed_time = self.current_time - aid_data['start_time']
            
            # Animation-Progress berechnen
            if config.duration > 0:
                aid_data['animation_progress'] = (elapsed_time % config.duration) / config.duration
            else:
                aid_data['animation_progress'] = 0.0
    
    def draw(self, surface: pygame.Surface) -> None:
        """Zeichnet alle aktiven visuellen Hilfen."""
        for aid_name, aid_data in self.active_aids.items():
            config = aid_data['config']
            position = aid_data['position']
            size = aid_data['size']
            progress = aid_data['animation_progress']
            
            if config.aid_type == VisualAid.HIGHLIGHT:
                self._draw_highlight(surface, position, size, config, progress)
            elif config.aid_type == VisualAid.OUTLINE:
                self._draw_outline(surface, position, size, config, progress)
            elif config.aid_type == VisualAid.GLOW:
                self._draw_glow(surface, position, size, config, progress)
            elif config.aid_type == VisualAid.PULSE:
                self._draw_pulse(surface, position, size, config, progress)
            elif config.aid_type == VisualAid.ARROW:
                self._draw_arrow(surface, position, size, config, progress)
    
    def _draw_highlight(self, surface: pygame.Surface, position: Tuple[int, int],
                       size: Tuple[int, int], config: VisualAidConfig, progress: float) -> None:
        """Zeichnet eine Hervorhebung."""
        x, y = position
        width, height = size
        
        # Transparenz basierend auf Animation
        alpha = int(128 + 64 * math.sin(progress * 2 * math.pi))
        highlight_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        highlight_surface.fill((*config.color, alpha))
        
        surface.blit(highlight_surface, (x, y))
    
    def _draw_outline(self, surface: pygame.Surface, position: Tuple[int, int],
                     size: Tuple[int, int], config: VisualAidConfig, progress: float) -> None:
        """Zeichnet einen Rahmen."""
        x, y = position
        width, height = size
        
        # Rahmen-Dicke variiert mit Animation
        thickness = max(1, int(3 * (0.5 + 0.5 * math.sin(progress * 2 * math.pi))))
        
        pygame.draw.rect(surface, config.color, (x, y, width, height), thickness)
    
    def _draw_glow(self, surface: pygame.Surface, position: Tuple[int, int],
                  size: Tuple[int, int], config: VisualAidConfig, progress: float) -> None:
        """Zeichnet einen Glow-Effekt."""
        x, y = position
        width, height = size
        
        # Glow-Intensität variiert mit Animation
        intensity = int(config.intensity * 255 * (0.7 + 0.3 * math.sin(progress * 2 * math.pi)))
        
        # Mehrere Glow-Layer
        for i in range(3):
            glow_size = 10 + i * 5
            glow_alpha = intensity // (i + 1)
            
            glow_surface = pygame.Surface((width + glow_size * 2, height + glow_size * 2), pygame.SRCALPHA)
            glow_surface.fill((*config.color, glow_alpha))
            
            surface.blit(glow_surface, (x - glow_size, y - glow_size))
    
    def _draw_pulse(self, surface: pygame.Surface, position: Tuple[int, int],
                   size: Tuple[int, int], config: VisualAidConfig, progress: float) -> None:
        """Zeichnet einen Puls-Effekt."""
        x, y = position
        width, height = size
        
        # Skalierung variiert mit Animation
        scale = 1.0 + 0.2 * math.sin(progress * 2 * math.pi)
        scaled_width = int(width * scale)
        scaled_height = int(height * scale)
        
        # Zentrierte Position
        scaled_x = x + (width - scaled_width) // 2
        scaled_y = y + (height - scaled_height) // 2
        
        # Puls-Oberfläche
        pulse_surface = pygame.Surface((scaled_width, scaled_height), pygame.SRCALPHA)
        pulse_alpha = int(100 + 50 * math.sin(progress * 2 * math.pi))
        pulse_surface.fill((*config.color, pulse_alpha))
        
        surface.blit(pulse_surface, (scaled_x, scaled_y))
    
    def _draw_arrow(self, surface: pygame.Surface, position: Tuple[int, int],
                   size: Tuple[int, int], config: VisualAidConfig, progress: float) -> None:
        """Zeichnet einen Pfeil."""
        x, y = position
        width, height = size
        
        # Pfeil-Position variiert mit Animation
        arrow_x = x + int(width * progress)
        arrow_y = y + height // 2
        
        # Pfeil zeichnen
        arrow_points = [
            (arrow_x - 10, arrow_y - 5),
            (arrow_x, arrow_y),
            (arrow_x - 10, arrow_y + 5)
        ]
        
        pygame.draw.polygon(surface, config.color, arrow_points)


class AccessibilityUI:
    """UI für Accessibility-Einstellungen."""
    
    def __init__(self, accessibility_manager: AccessibilityManager):
        self.accessibility_manager = accessibility_manager
        self.font = pygame.font.Font(None, 16)
        self.small_font = pygame.font.Font(None, 14)
        
        # UI-Elemente
        self.buttons = []
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Richtet die UI-Elemente ein."""
        # Accessibility-Level Button
        level_button = {
            'rect': pygame.Rect(10, 10, 200, 30),
            'text': f"Accessibility: {self.accessibility_manager.accessibility_level.name}",
            'callback': self.accessibility_manager.toggle_accessibility_level
        }
        self.buttons.append(level_button)
        
        # Feature-Toggles
        toggles = [
            ("Tooltips", self.accessibility_manager.tooltips_enabled, self._toggle_tooltips),
            ("Hoher Kontrast", self.accessibility_manager.high_contrast_mode, self._toggle_high_contrast),
            ("Große Schrift", self.accessibility_manager.large_text_mode, self._toggle_large_text),
            ("Sound-Feedback", self.accessibility_manager.sound_feedback, self._toggle_sound_feedback)
        ]
        
        y_offset = 50
        for text, state, callback in toggles:
            toggle_button = {
                'rect': pygame.Rect(10, y_offset, 200, 25),
                'text': f"{text}: {'ON' if state else 'OFF'}",
                'callback': callback
            }
            self.buttons.append(toggle_button)
            y_offset += 30
    
    def _toggle_tooltips(self) -> None:
        """Schaltet Tooltips um."""
        self.accessibility_manager.tooltips_enabled = not self.accessibility_manager.tooltips_enabled
        self._update_button_texts()
    
    def _toggle_high_contrast(self) -> None:
        """Schaltet hohen Kontrast um."""
        self.accessibility_manager.high_contrast_mode = not self.accessibility_manager.high_contrast_mode
        self._update_button_texts()
    
    def _toggle_large_text(self) -> None:
        """Schaltet große Schrift um."""
        self.accessibility_manager.large_text_mode = not self.accessibility_manager.large_text_mode
        self._update_button_texts()
    
    def _toggle_sound_feedback(self) -> None:
        """Schaltet Sound-Feedback um."""
        self.accessibility_manager.sound_feedback = not self.accessibility_manager.sound_feedback
        self._update_button_texts()
    
    def _update_button_texts(self) -> None:
        """Aktualisiert die Button-Texte."""
        self.buttons[0]['text'] = f"Accessibility: {self.accessibility_manager.accessibility_level.name}"
        
        toggle_index = 1
        toggles = [
            self.accessibility_manager.tooltips_enabled,
            self.accessibility_manager.high_contrast_mode,
            self.accessibility_manager.large_text_mode,
            self.accessibility_manager.sound_feedback
        ]
        
        for i, state in enumerate(toggles):
            if toggle_index + i < len(self.buttons):
                button = self.buttons[toggle_index + i]
                if "Tooltips" in button['text']:
                    button['text'] = f"Tooltips: {'ON' if state else 'OFF'}"
                elif "Hoher Kontrast" in button['text']:
                    button['text'] = f"Hoher Kontrast: {'ON' if state else 'OFF'}"
                elif "Große Schrift" in button['text']:
                    button['text'] = f"Große Schrift: {'ON' if state else 'OFF'}"
                elif "Sound-Feedback" in button['text']:
                    button['text'] = f"Sound-Feedback: {'ON' if state else 'OFF'}"
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Behandelt UI-Events."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            scaled_pos = (mouse_pos[0] // 4, mouse_pos[1] // 4)
            
            for button in self.buttons:
                if button['rect'].collidepoint(scaled_pos):
                    button['callback']()
                    return True
        
        return False
    
    def draw(self, surface: pygame.Surface) -> None:
        """Zeichnet die Accessibility-UI."""
        # Hintergrund
        bg_rect = pygame.Rect(5, 5, 220, 200)
        pygame.draw.rect(surface, (0, 0, 0, 180), bg_rect, border_radius=8)
        pygame.draw.rect(surface, Colors.UI_BORDER, bg_rect, 2, border_radius=8)
        
        # Titel
        title_surface = self.font.render("Accessibility", True, Colors.WHITE)
        title_rect = title_surface.get_rect(center=(bg_rect.centerx, bg_rect.y + 15))
        surface.blit(title_surface, title_rect)
        
        # Buttons
        for button in self.buttons:
            # Button-Hintergrund
            button_color = Colors.UI_BG if button['rect'].collidepoint(pygame.mouse.get_pos()) else (30, 30, 40)
            pygame.draw.rect(surface, button_color, button['rect'], border_radius=4)
            pygame.draw.rect(surface, Colors.UI_BORDER, button['rect'], 1, border_radius=4)
            
            # Button-Text
            text_surface = self.small_font.render(button['text'], True, Colors.WHITE)
            text_rect = text_surface.get_rect(center=button['rect'].center)
            surface.blit(text_surface, text_rect)
