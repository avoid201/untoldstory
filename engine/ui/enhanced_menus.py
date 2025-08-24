"""
Verbesserte Menü-Struktur für Untold Story
Integriert moderne UI-Patterns und erhöht die Benutzerfreundlichkeit
"""

import pygame
from typing import TYPE_CHECKING, Optional, List, Dict, Any, Callable
from dataclasses import dataclass
from enum import Enum, auto
from abc import ABC, abstractmethod

from .modern_ui_patterns import (
    ModernUIElement, AnimatedButton, TooltipManager, 
    TransitionManager, Animation, AnimationType
)
from engine.core.config import Colors

if TYPE_CHECKING:
    from engine.core.game import Game
    from engine.systems.monster_instance import MonsterInstance
    from engine.systems.items import Item
    from engine.systems.quests import Quest


class MenuState(Enum):
    """Zustände des Hauptmenüs."""
    MAIN = auto()
    INVENTORY = auto()
    PARTY = auto()
    QUESTS = auto()
    SETTINGS = auto()
    SAVE_LOAD = auto()


class MenuTransition(Enum):
    """Übergangstypen zwischen Menüs."""
    SLIDE_LEFT = auto()
    SLIDE_RIGHT = auto()
    FADE = auto()
    SCALE = auto()


@dataclass
class MenuItem:
    """Ein Menü-Eintrag."""
    text: str
    icon: Optional[str] = None
    callback: Optional[Callable] = None
    enabled: bool = True
    shortcut: Optional[str] = None
    tooltip: Optional[str] = None


class EnhancedMenuBase(ModernUIElement):
    """Verbesserte Basis-Klasse für alle Menüs."""
    
    def __init__(self, game: 'Game', title: str = ""):
        super().__init__(0, 0, 300, 200)
        self.game = game
        self.title = title
        self.menu_items: List[MenuItem] = []
        self.selected_index = 0
        self.scroll_offset = 0
        self.items_per_page = 8
        
        # UI-Komponenten
        self.tooltip_manager = TooltipManager()
        self.transition_manager = TransitionManager()
        
        # Menü-spezifische Einstellungen
        self.show_scrollbar = True
        self.allow_keyboard_navigation = True
        self.animation_duration = 0.3
        
        # Farben und Styling
        self.colors = {
            'background': Colors.UI_BG,
            'border': Colors.UI_BORDER,
            'selected': Colors.UI_SELECTED,
            'unselected': Colors.UI_UNSELECTED,
            'disabled': Colors.UI_DISABLED,
            'title': Colors.WHITE,
            'scrollbar': (100, 100, 120, 150)
        }
        
        # Menü-Position anpassen
        self.rect.center = (160, 90)  # Zentriert auf 320x180
        
        # Animationen initialisieren
        self._setup_animations()
    
    def _setup_animations(self) -> None:
        """Richtet Standard-Animationen ein."""
        # Einblend-Animation
        self.add_animation("fade_in", Animation(
            AnimationType.FADE_IN, self.animation_duration, 0, 255, easing="ease_out"
        ))
        
        # Skalierungs-Animation
        self.add_animation("scale_in", Animation(
            AnimationType.SCALE_IN, self.animation_duration, 0.8, 1.0, easing="ease_out"
        ))
    
    def add_menu_item(self, item: MenuItem) -> None:
        """Fügt einen Menü-Eintrag hinzu."""
        self.menu_items.append(item)
        
        # Tooltip hinzufügen wenn vorhanden
        if item.tooltip:
            self.tooltip_manager.add_tooltip(self, item.tooltip)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Behandelt Eingabe-Events."""
        if event.type == pygame.KEYDOWN:
            return self._handle_keyboard(event)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            return self._handle_mouse_click(event)
        elif event.type == pygame.MOUSEMOTION:
            return self._handle_mouse_motion(event)
        
        return False
    
    def _handle_keyboard(self, event: pygame.event.Event) -> bool:
        """Behandelt Tastatur-Events."""
        if not self.allow_keyboard_navigation:
            return False
        
        if event.key == pygame.K_UP:
            self._select_previous()
            return True
        elif event.key == pygame.K_DOWN:
            self._select_next()
            return True
        elif event.key == pygame.K_RETURN:
            return self._activate_selected()
        elif event.key == pygame.K_ESCAPE:
            return self._handle_escape()
        
        # Shortcuts prüfen
        for i, item in enumerate(self.menu_items):
            if item.shortcut and event.unicode == item.shortcut:
                self.selected_index = i
                return self._activate_selected()
        
        return False
    
    def _handle_mouse_click(self, event: pygame.event.Event) -> None:
        """Behandelt Mausklicks."""
        if event.button == 1:  # Linksklick
            mouse_pos = event.pos
            # Skalierung berücksichtigen
            scaled_pos = (mouse_pos[0] // 4, mouse_pos[1] // 4)
            
            # Prüfe ob ein Menü-Eintrag geklickt wurde
            for i, item in enumerate(self.menu_items):
                item_rect = self._get_item_rect(i)
                if item_rect.collidepoint(scaled_pos) and item.enabled:
                    self.selected_index = i
                    self._activate_selected()
                    break
    
    def _handle_mouse_motion(self, event: pygame.event.Event) -> None:
        """Behandelt Mausbewegungen."""
        mouse_pos = event.pos
        scaled_pos = (mouse_pos[0] // 4, mouse_pos[1] // 4)
        
        # Hover-Effekte aktualisieren
        self.handle_hover(scaled_pos)
        
        # Tooltips aktualisieren
        self.tooltip_manager.update(0, scaled_pos)
    
    def _select_previous(self) -> None:
        """Wählt den vorherigen Eintrag aus."""
        if self.selected_index > 0:
            self.selected_index -= 1
            self._ensure_visible()
    
    def _select_next(self) -> None:
        """Wählt den nächsten Eintrag aus."""
        if self.selected_index < len(self.menu_items) - 1:
            self.selected_index += 1
            self._ensure_visible()
    
    def _ensure_visible(self) -> None:
        """Stellt sicher, dass der ausgewählte Eintrag sichtbar ist."""
        if self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        elif self.selected_index >= self.scroll_offset + self.items_per_page:
            self.scroll_offset = self.selected_index - self.items_per_page + 1
    
    def _activate_selected(self) -> bool:
        """Aktiviert den ausgewählten Eintrag."""
        if 0 <= self.selected_index < len(self.menu_items):
            item = self.menu_items[self.selected_index]
            if item.enabled and item.callback:
                item.callback()
                return True
        return False
    
    def _handle_escape(self) -> bool:
        """Behandelt ESC-Taste."""
        # Standard-Verhalten: Menü schließen
        return True
    
    def _get_item_rect(self, index: int) -> pygame.Rect:
        """Gibt das Rechteck für einen Menü-Eintrag zurück."""
        item_y = self.rect.y + 40 + (index - self.scroll_offset) * 20
        return pygame.Rect(self.rect.x + 10, item_y, self.rect.width - 20, 18)
    
    def update(self, dt: float) -> None:
        """Aktualisiert das Menü."""
        super().update(dt)
        self.transition_manager.update(dt)
    
    def draw(self, surface: pygame.Surface) -> None:
        """Zeichnet das Menü."""
        if not self.is_visible:
            return
        
        # Aktuelle Skalierung berechnen
        current_scale = self.get_hover_scale()
        
        # Menü-Hintergrund
        menu_rect = self.rect.copy()
        if current_scale != 1.0:
            menu_rect = menu_rect.inflate(
                int(self.rect.width * current_scale - self.rect.width),
                int(self.rect.height * current_scale - self.rect.height)
            )
        
        # Hintergrund mit Transparenz
        bg_surface = pygame.Surface(menu_rect.size, pygame.SRCALPHA)
        bg_surface.fill((*self.colors['background'], 230))
        surface.blit(bg_surface, menu_rect)
        
        # Rahmen
        pygame.draw.rect(surface, self.colors['border'], menu_rect, 2, border_radius=8)
        
        # Titel
        if self.title:
            self._draw_title(surface, menu_rect)
        
        # Menü-Einträge
        self._draw_menu_items(surface, menu_rect)
        
        # Scrollbar
        if self.show_scrollbar and len(self.menu_items) > self.items_per_page:
            self._draw_scrollbar(surface, menu_rect)
        
        # Tooltips
        mouse_pos = pygame.mouse.get_pos()
        scaled_mouse_pos = (mouse_pos[0] // 4, mouse_pos[1] // 4)
        self.tooltip_manager.draw(surface, scaled_mouse_pos)
    
    def _draw_title(self, surface: pygame.Surface, menu_rect: pygame.Rect) -> None:
        """Zeichnet den Menü-Titel."""
        font = pygame.font.Font(None, 18)
        title_surface = font.render(self.title, True, self.colors['title'])
        title_rect = title_surface.get_rect(center=(menu_rect.centerx, menu_rect.y + 15))
        surface.blit(title_surface, title_rect)
        
        # Trennlinie
        line_y = menu_rect.y + 30
        pygame.draw.line(surface, self.colors['border'],
                        (menu_rect.x + 10, line_y),
                        (menu_rect.right - 10, line_y), 1)
    
    def _draw_menu_items(self, surface: pygame.Surface, menu_rect: pygame.Rect) -> None:
        """Zeichnet die Menü-Einträge."""
        start_y = menu_rect.y + 40
        
        for i in range(self.scroll_offset, min(self.scroll_offset + self.items_per_page, len(self.menu_items))):
            item = self.menu_items[i]
            item_rect = pygame.Rect(menu_rect.x + 10, start_y, menu_rect.width - 20, 18)
            
            # Hintergrund für ausgewählten Eintrag
            if i == self.selected_index:
                pygame.draw.rect(surface, self.colors['selected'], item_rect, border_radius=4)
            
            # Text
            color = self.colors['disabled'] if not item.enabled else self.colors['unselected']
            if i == self.selected_index:
                color = Colors.BLACK
            
            font = pygame.font.Font(None, 14)
            text_surface = font.render(item.text, True, color)
            text_rect = text_surface.get_rect(midleft=(item_rect.x + 5, item_rect.centery))
            surface.blit(text_surface, text_rect)
            
            # Shortcut anzeigen
            if item.shortcut:
                shortcut_surface = font.render(f"[{item.shortcut}]", True, color)
                shortcut_rect = shortcut_surface.get_rect(midright=(item_rect.right - 5, item_rect.centery))
                surface.blit(shortcut_surface, shortcut_rect)
            
            start_y += 20
    
    def _draw_scrollbar(self, surface: pygame.Surface, menu_rect: pygame.Rect) -> None:
        """Zeichnet die Scrollbar."""
        scrollbar_width = 8
        scrollbar_x = menu_rect.right - scrollbar_width - 5
        
        # Scrollbar-Hintergrund
        scrollbar_bg_rect = pygame.Rect(
            scrollbar_x, menu_rect.y + 40,
            scrollbar_width, menu_rect.height - 50
        )
        pygame.draw.rect(surface, (*self.colors['scrollbar'][:3], 100), scrollbar_bg_rect, border_radius=4)
        
        # Scrollbar-Slider
        if len(self.menu_items) > self.items_per_page:
            slider_height = max(20, (self.items_per_page / len(self.menu_items)) * (menu_rect.height - 50))
            slider_y = menu_rect.y + 40 + (self.scroll_offset / (len(self.menu_items) - self.items_per_page)) * (menu_rect.height - 50 - slider_height)
            
            slider_rect = pygame.Rect(scrollbar_x, slider_y, scrollbar_width, slider_height)
            pygame.draw.rect(surface, self.colors['scrollbar'], slider_rect, border_radius=4)


class EnhancedInventoryMenu(EnhancedMenuBase):
    """Verbessertes Inventar-Menü."""
    
    def __init__(self, game: 'Game'):
        super().__init__(game, "Inventar")
        self.inventory = game.inventory if hasattr(game, 'inventory') else None
        self.item_db = game.item_database if hasattr(game, 'item_database') else None
        self.items_list = []
        self.selected_item = None
        self.show_description = False
        
        # Menü-Einträge
        self._setup_menu_items()
        self._refresh_items()
    
    def _setup_menu_items(self) -> None:
        """Richtet die Menü-Einträge ein."""
        self.add_menu_item(MenuItem(
            text="Verwenden",
            shortcut="v",
            callback=self._use_item,
            tooltip="Gegenstand verwenden"
        ))
        self.add_menu_item(MenuItem(
            text="Ausrüsten",
            shortcut="a",
            callback=self._equip_item,
            tooltip="Gegenstand ausrüsten"
        ))
        self.add_menu_item(MenuItem(
            text="Verwerfen",
            shortcut="d",
            callback=self._drop_item,
            tooltip="Gegenstand verwerfen"
        ))
        self.add_menu_item(MenuItem(
            text="Sortieren",
            shortcut="s",
            callback=self._sort_inventory,
            tooltip="Inventar sortieren"
        ))
    
    def _refresh_items(self) -> None:
        """Aktualisiert die Gegenstandsliste."""
        if not self.inventory:
            return
        
        self.items_list = []
        for item_id, quantity in self.inventory.get_all_items():
            if self.item_db:
                item = self.item_db.get_item(item_id)
                if item:
                    self.items_list.append((item, quantity))
    
    def _use_item(self) -> None:
        """Verwendet den ausgewählten Gegenstand."""
        if self.selected_item:
            print(f"Verwende: {self.selected_item.name}")
    
    def _equip_item(self) -> None:
        """Rüstet den ausgewählten Gegenstand aus."""
        if self.selected_item:
            print(f"Rüste aus: {self.selected_item.name}")
    
    def _drop_item(self) -> None:
        """Verwirft den ausgewählten Gegenstand."""
        if self.selected_item:
            print(f"Verwerfe: {self.selected_item.name}")
    
    def _sort_inventory(self) -> None:
        """Sortiert das Inventar."""
        print("Sortiere Inventar...")
        self._refresh_items()


class EnhancedPartyMenu(EnhancedMenuBase):
    """Verbessertes Team-Menü."""
    
    def __init__(self, game: 'Game'):
        super().__init__(game, "Team")
        self.party = game.party if hasattr(game, 'party') else None
        
        # Menü-Einträge
        self._setup_menu_items()
    
    def _setup_menu_items(self) -> None:
        """Richtet die Menü-Einträge ein."""
        self.add_menu_item(MenuItem(
            text="Status anzeigen",
            shortcut="s",
            callback=self._show_status,
            tooltip="Detaillierten Status anzeigen"
        ))
        self.add_menu_item(MenuItem(
            text="Fähigkeiten",
            shortcut="f",
            callback=self._show_moves,
            tooltip="Fähigkeiten anzeigen"
        ))
        self.add_menu_item(MenuItem(
            text="Team neu ordnen",
            shortcut="r",
            callback=self._reorder_team,
            tooltip="Team-Reihenfolge ändern"
        ))
        self.add_menu_item(MenuItem(
            text="Synthese",
            shortcut="y",
            callback=self._synthesis,
            tooltip="Monster fusionieren"
        ))
    
    def _show_status(self) -> None:
        """Zeigt den Status des ausgewählten Monsters."""
        print("Zeige Status...")
    
    def _show_moves(self) -> None:
        """Zeigt die Fähigkeiten des ausgewählten Monsters."""
        print("Zeige Fähigkeiten...")
    
    def _reorder_team(self) -> None:
        """Ändert die Team-Reihenfolge."""
        print("Ändere Team-Reihenfolge...")
    
    def _synthesis(self) -> None:
        """Startet die Synthese."""
        print("Starte Synthese...")


class MenuManager:
    """Verwaltet alle Menüs und Übergänge."""
    
    def __init__(self, game: 'Game'):
        self.game = game
        self.current_menu: Optional[EnhancedMenuBase] = None
        self.menu_stack: List[EnhancedMenuBase] = []
        self.transition_manager = TransitionManager()
        
        # Menüs initialisieren
        self.inventory_menu = EnhancedInventoryMenu(game)
        self.party_menu = EnhancedPartyMenu(game)
        
        # Standard-Menü
        self.show_main_menu()
    
    def show_main_menu(self) -> None:
        """Zeigt das Hauptmenü."""
        self.current_menu = None
        self.menu_stack.clear()
    
    def show_inventory(self) -> None:
        """Zeigt das Inventar-Menü."""
        self._push_menu(self.inventory_menu)
    
    def show_party(self) -> None:
        """Zeigt das Team-Menü."""
        self._push_menu(self.party_menu)
    
    def _push_menu(self, menu: EnhancedMenuBase) -> None:
        """Fügt ein Menü zum Stack hinzu."""
        self.menu_stack.append(menu)
        self.current_menu = menu
        
        # Übergangs-Animation starten
        self.transition_manager.start_fade("menu_transition", True, 0.3)
    
    def pop_menu(self) -> None:
        """Entfernt das oberste Menü vom Stack."""
        if self.menu_stack:
            self.menu_stack.pop()
            self.current_menu = self.menu_stack[-1] if self.menu_stack else None
            
            # Übergangs-Animation starten
            self.transition_manager.start_fade("menu_transition", False, 0.2)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Behandelt Events für alle Menüs."""
        if self.current_menu:
            if self.current_menu.handle_event(event):
                return True
            
            # ESC-Taste behandeln
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.pop_menu()
                return True
        
        return False
    
    def update(self, dt: float) -> None:
        """Aktualisiert alle Menüs."""
        if self.current_menu:
            self.current_menu.update(dt)
        
        self.transition_manager.update(dt)
    
    def draw(self, surface: pygame.Surface) -> None:
        """Zeichnet alle Menüs."""
        if self.current_menu:
            self.current_menu.draw(surface)
        
        self.transition_manager.draw(surface)
