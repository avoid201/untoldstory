"""
Verbesserte Menü-Struktur für Untold Story
Integriert moderne UI-Patterns und erhöht die Benutzerfreundlichkeit
"""

import pygame
import logging
from typing import TYPE_CHECKING, Optional, List, Dict, Any, Callable
from dataclasses import dataclass
from enum import Enum, auto
# ABC import removed - not used in this file

logger = logging.getLogger(__name__)

from .modern_ui_patterns import (
    ModernUIElement, AnimatedButton, TooltipManager, 
    UITransitionManager, Animation, AnimationType
)
from engine.core.config import Colors
# Import centralized font manager
from engine.ui.battle_ui_utils import fonts

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
        self.transition_manager = UITransitionManager()
        
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
        # Use centralized font manager
        font = fonts.large
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
            
            # Use centralized font manager
            font = fonts.normal
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
        # Use item_registry directly instead of game.item_database
        from engine.systems.items import item_registry
        self.item_db = item_registry
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
            logger.info(f"Item used: {self.selected_item.name}")
    
    def _equip_item(self) -> None:
        """Rüstet den ausgewählten Gegenstand aus."""
        if self.selected_item:
            logger.info(f"Item equipped: {self.selected_item.name}")
    
    def _drop_item(self) -> None:
        """Verwirft den ausgewählten Gegenstand."""
        if self.selected_item:
            logger.info(f"Item dropped: {self.selected_item.name}")
    
    def _sort_inventory(self) -> None:
        """Sortiert das Inventar."""
        logger.debug("Sorting inventory...")
        self._refresh_items()


class EnhancedPartyMenu(EnhancedMenuBase):
    """Verbessertes Team-Menü."""
    
    def __init__(self, game: 'Game'):
        super().__init__(game, "Team")
        # Korrekte Party-Referenz
        if hasattr(game, 'party_manager') and hasattr(game.party_manager, 'party'):
            self.party = game.party_manager.party
        elif hasattr(game, 'party'):
            self.party = game.party
        else:
            self.party = None
        
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
            text="Talente",
            shortcut="t",
            callback=self._show_talents,
            tooltip="Talent-Übersicht anzeigen"
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
    
    def _show_talents(self) -> None:
        """Zeigt die Talente des ausgewählten Monsters."""
        if not self.party:
            return
        
        monsters = self.party.get_all_members()
        if not monsters or self.selected_index >= len(monsters):
            return
        
        monster = monsters[self.selected_index]
        if not hasattr(monster, 'talents'):
            print("Monster hat keine Talente")
            return
        
        print(f"\n=== Talente von {monster.species.name} ===")
        
        try:
            from engine.systems.talent_system import get_talent_database
            talent_db = get_talent_database()
            
            for talent_instance in monster.talents:
                if talent_instance.is_learned:
                    talent = talent_db.get_talent(talent_instance.talent_id)
                    if talent:
                        tier_stars = '★' * talent_instance.current_tier.value
                        print(f"{talent.name} {tier_stars} (Tier {talent_instance.current_tier.value})")
                        print(f"  Beschreibung: {talent.description}")
                        
                        # Zeige verfügbare Moves
                        moves = talent.get_moves_for_tier(talent_instance.current_tier, monster.level)
                        if moves:
                            print(f"  Verfügbare Moves: {', '.join(moves)}")
                        
                        # Zeige passive Fähigkeiten
                        passive_abilities = talent.get_passive_abilities_for_tier(talent_instance.current_tier)
                        if passive_abilities:
                            print(f"  Passive Fähigkeiten:")
                            for ability in passive_abilities:
                                print(f"    - {ability['name']}: {ability['description']}")
                        
                        print()
                        
        except Exception as e:
            print(f"Fehler beim Laden der Talente: {e}")
    
    def _reorder_team(self) -> None:
        """Ändert die Team-Reihenfolge."""
        print("Ändere Team-Reihenfolge...")
    
    def _synthesis(self) -> None:
        """Startet die Synthese."""
        print("Starte Synthese...")
    
    def draw(self, surface: pygame.Surface) -> None:
        """Zeichnet das Party-Menü mit Monster-Liste."""
        if not self.is_visible:
            return
        
        # Basis-Menü zeichnen
        super().draw(surface)
        
        # Monster-Liste zeichnen
        self._draw_monster_list(surface)
    
    def _draw_monster_list(self, surface: pygame.Surface) -> None:
        """Zeichnet die Liste der Monster im Team."""
        if not self.party:
            no_party = fonts.normal.render("Kein Team gefunden", True, self.colors['disabled'])
            surface.blit(no_party, (self.rect.x + 10, self.rect.y + 60))
            return
        
        # Monster-Liste
        monsters = self.party.get_all_members()
        if not monsters:
            no_monsters = fonts.normal.render("Keine Monster im Team", True, self.colors['disabled'])
            surface.blit(no_monsters, (self.rect.x + 10, self.rect.y + 60))
            return
        
        # Monster zeichnen
        start_y = self.rect.y + 60
        for i, monster in enumerate(monsters):
            y = start_y + i * 25
            
            # Monster-Hintergrund
            monster_rect = pygame.Rect(self.rect.x + 5, y - 2, self.rect.width - 10, 22)
            if i == self.selected_index:
                pygame.draw.rect(surface, (*self.colors['selected'], 100), monster_rect, border_radius=3)
            else:
                pygame.draw.rect(surface, (*self.colors['unselected'], 30), monster_rect, border_radius=3)
            
            # Monster-Name und Level
            monster_name = getattr(monster, 'nickname', None) or getattr(monster.species, 'name', 'Unbekannt')
            level = getattr(monster, 'level', 1)
            name_text = f"{monster_name} Lv.{level}"
            
            # Talent-Info hinzufügen
            talent_info = ""
            if hasattr(monster, 'talents') and monster.talents:
                learned_talents = [t for t in monster.talents if t.is_learned]
                if learned_talents:
                    talent_count = len(learned_talents)
                    max_tier = max(t.current_tier.value for t in learned_talents)
                    talent_info = f" | {talent_count}T | ★{max_tier}"
            
            color = self.colors['selected'] if i == self.selected_index else self.colors['unselected']
            name_surf = fonts.normal.render(name_text, True, color)
            surface.blit(name_surf, (self.rect.x + 10, y))
            
            # Talent-Info anzeigen
            if talent_info:
                talent_surf = fonts.small.render(talent_info, True, (255, 255, 100))  # Gold für Talente
                surface.blit(talent_surf, (self.rect.x + 10, y + 15))
            
            # HP-Balken
            if hasattr(monster, 'current_hp') and hasattr(monster, 'max_hp'):
                hp_percent = monster.current_hp / monster.max_hp if monster.max_hp > 0 else 0
                hp_width = int((self.rect.width - 20) * hp_percent)
                
                # HP-Hintergrund
                hp_bg_rect = pygame.Rect(self.rect.x + 10, y + 12, self.rect.width - 20, 6)
                pygame.draw.rect(surface, (50, 50, 50), hp_bg_rect, border_radius=2)
                
                # HP-Balken
                if hp_width > 0:
                    hp_rect = pygame.Rect(self.rect.x + 10, y + 12, hp_width, 6)
                    hp_color = (0, 255, 0) if hp_percent > 0.5 else (255, 255, 0) if hp_percent > 0.25 else (255, 0, 0)
                    pygame.draw.rect(surface, hp_color, hp_rect, border_radius=2)
                
                # HP-Text
                hp_text = f"{monster.current_hp}/{monster.max_hp}"
                hp_surf = fonts.small.render(hp_text, True, color)
                surface.blit(hp_surf, (self.rect.x + 10, y + 20))
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Behandelt Party-spezifische Events."""
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_w, pygame.K_UP]:
                if self.selected_index > 0:
                    self.selected_index -= 1
                return True
            elif event.key in [pygame.K_s, pygame.K_DOWN]:
                if self.party and self.selected_index < len(self.party.get_all_members()) - 1:
                    self.selected_index += 1
                return True
        
        # Basis-Event-Handling
        return super().handle_event(event)


class EnhancedQuestMenu(EnhancedMenuBase):
    """Verbessertes Quest-Menü mit Animationen."""
    
    def __init__(self, game: 'Game'):
        super().__init__(game, "Quests")
        self.quests = game.quest_manager.quests if hasattr(game, 'quest_manager') else []
        self.selected_quest = 0
        self.show_details = False
        
        # Quest-spezifische Animationen
        self.quest_animations = []
        self.transition_manager = UITransitionManager()
        
        # Menü-Einträge
        self._setup_menu_items()
    
    def _setup_menu_items(self) -> None:
        """Richtet die Quest-Menü-Einträge ein."""
        self.add_menu_item(MenuItem(
            text="Details anzeigen",
            shortcut="d",
            callback=self._toggle_details,
            tooltip="Quest-Details ein-/ausblenden"
        ))
        self.add_menu_item(MenuItem(
            text="Zurück",
            shortcut="q",
            callback=self._handle_escape,
            tooltip="Zurück zum Hauptmenü"
        ))
    
    def _toggle_details(self) -> None:
        """Schaltet die Quest-Details um."""
        self.show_details = not self.show_details
        logger.info(f"Quest details toggled: {self.show_details}")
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Behandelt Quest-spezifische Events."""
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_w, pygame.K_UP]:
                if self.selected_quest > 0:
                    self.selected_quest -= 1
                return True
            elif event.key in [pygame.K_s, pygame.K_DOWN]:
                if self.selected_quest < len(self.quests) - 1:
                    self.selected_quest += 1
                return True
            elif event.key in [pygame.K_e, pygame.K_RETURN, pygame.K_SPACE]:
                self.show_details = not self.show_details
                return True
        
        # Basis-Event-Handling
        return super().handle_event(event)
    
    def draw(self, surface: pygame.Surface) -> None:
        """Zeichnet das Quest-Menü mit erweiterten Features."""
        if not self.is_visible:
            return
        
        # Basis-Menü zeichnen
        super().draw(surface)
        
        # Quest-spezifische Inhalte
        self._draw_quest_content(surface)
    
    def _draw_quest_content(self, surface: pygame.Surface) -> None:
        """Zeichnet den Quest-spezifischen Inhalt."""
        if not self.quests:
            no_quests = fonts.normal.render("Keine aktiven Quests", True, self.colors['disabled'])
            surface.blit(no_quests, (self.rect.x + 10, self.rect.y + 60))
            return
        
        # Quest-Liste zeichnen
        start_y = self.rect.y + 60
        for i, quest in enumerate(self.quests):
            y = start_y + i * 15
            
            if i == self.selected_quest:
                color = self.colors['selected']
                # Hervorhebung für ausgewählten Quest
                highlight_rect = pygame.Rect(self.rect.x + 5, y - 2, self.rect.width - 10, 14)
                pygame.draw.rect(surface, (*self.colors['selected'], 50), highlight_rect, border_radius=3)
            else:
                color = self.colors['unselected']
            
            # Quest-Name
            quest_text = quest.name if hasattr(quest, 'name') else f"Quest {i+1}"
            text_surf = fonts.normal.render(quest_text, True, color)
            surface.blit(text_surf, (self.rect.x + 10, y))
            
            # Quest-Status
            if hasattr(quest, 'completed') and quest.completed:
                status_text = "✓"
                status_color = (0, 255, 0)
            else:
                status_text = "○"
                status_color = (255, 255, 0)
            
            status_surf = fonts.normal.render(status_text, True, status_color)
            surface.blit(status_surf, (self.rect.x + self.rect.width - 20, y))


class EnhancedSaveMenu(EnhancedMenuBase):
    """Verbessertes Save/Load-Menü mit modernem UI."""
    
    def __init__(self, game: 'Game'):
        super().__init__(game, "Speichern/Laden")
        self.save_slots = 3
        self.selected_slot = 0
        self.mode = 'save'  # 'save' or 'load'
        
        # Save-spezifische Animationen
        self.save_animations = []
        self.transition_manager = UITransitionManager()
        
        # Menü-Einträge
        self._setup_menu_items()
    
    def _setup_menu_items(self) -> None:
        """Richtet die Save-Menü-Einträge ein."""
        self.add_menu_item(MenuItem(
            text="Bestätigen",
            shortcut="e",
            callback=self._perform_save_load,
            tooltip="Speichern/Laden bestätigen"
        ))
        self.add_menu_item(MenuItem(
            text="Zurück",
            shortcut="q",
            callback=self._handle_escape,
            tooltip="Zurück zum Hauptmenü"
        ))
    
    def _perform_save_load(self) -> None:
        """Führt das Speichern/Laden durch."""
        if self.mode == 'save':
            self.game.save_game(f"save_{self.selected_slot + 1}.sav")
            logger.info(f"Game saved to slot {self.selected_slot + 1}")
        else:
            self.game.load_game(f"save_{self.selected_slot + 1}.sav")
            logger.info(f"Game loaded from slot {self.selected_slot + 1}")
    
    def set_mode(self, mode: str) -> None:
        """Setzt den Modus (save/load)."""
        self.mode = mode
        self.title = "Speichern" if mode == 'save' else "Laden"
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Behandelt Save-spezifische Events."""
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_w, pygame.K_UP]:
                if self.selected_slot > 0:
                    self.selected_slot -= 1
                return True
            elif event.key in [pygame.K_s, pygame.K_DOWN]:
                if self.selected_slot < self.save_slots - 1:
                    self.selected_slot += 1
                return True
            elif event.key in [pygame.K_e, pygame.K_RETURN, pygame.K_SPACE]:
                self._perform_save_load()
                return False
        
        # Basis-Event-Handling
        return super().handle_event(event)
    
    def draw(self, surface: pygame.Surface) -> None:
        """Zeichnet das Save-Menü mit erweiterten Features."""
        if not self.is_visible:
            return
        
        # Basis-Menü zeichnen
        super().draw(surface)
        
        # Save-spezifische Inhalte
        self._draw_save_content(surface)
    
    def _draw_save_content(self, surface: pygame.Surface) -> None:
        """Zeichnet den Save-spezifischen Inhalt."""
        # Save-Slots zeichnen
        start_y = self.rect.y + 60
        for i in range(self.save_slots):
            y = start_y + i * 20
            
            if i == self.selected_slot:
                color = self.colors['selected']
                # Hervorhebung für ausgewählten Slot
                highlight_rect = pygame.Rect(self.rect.x + 5, y - 2, self.rect.width - 10, 18)
                pygame.draw.rect(surface, (*self.colors['selected'], 50), highlight_rect, border_radius=3)
            else:
                color = self.colors['unselected']
            
            slot_text = f"Slot {i + 1}"
            text_surf = fonts.normal.render(slot_text, True, color)
            surface.blit(text_surf, (self.rect.x + 10, y))
            
            # Prüfe ob Save existiert
            save_file = f"save_{i + 1}.sav"
            if hasattr(self.game, 'save_system') and self.game.save_system.save_exists(save_file):
                exists_text = "✓"
                exists_color = (0, 255, 0)
            else:
                exists_text = "○"
                exists_color = (100, 100, 100)
            
            exists_surf = fonts.normal.render(exists_text, True, exists_color)
            surface.blit(exists_surf, (self.rect.x + self.rect.width - 20, y))


class EnhancedConfirmDialog(EnhancedMenuBase):
    """Verbesserter Bestätigungs-Dialog mit Animationen."""
    
    def __init__(self, game: 'Game', message: str, callback: Callable[[bool], None]):
        super().__init__(game, "Bestätigung")
        self.message = message
        self.callback = callback
        self.selected_option = 0  # 0 = Yes, 1 = No
        
        # Dialog-spezifische Animationen
        self.dialog_animations = []
        self.transition_manager = UITransitionManager()
        
        # Menü-Einträge
        self._setup_menu_items()
    
    def _setup_menu_items(self) -> None:
        """Richtet die Dialog-Menü-Einträge ein."""
        self.add_menu_item(MenuItem(
            text="Ja",
            shortcut="y",
            callback=lambda: self._confirm(True),
            tooltip="Bestätigen"
        ))
        self.add_menu_item(MenuItem(
            text="Nein",
            shortcut="n",
            callback=lambda: self._confirm(False),
            tooltip="Abbrechen"
        ))
    
    def _confirm(self, result: bool) -> None:
        """Bestätigt die Auswahl."""
        self.callback(result)
        logger.info(f"Dialog confirmed: {result}")
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Behandelt Dialog-spezifische Events."""
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_a, pygame.K_LEFT]:
                self.selected_option = 0
                return True
            elif event.key in [pygame.K_d, pygame.K_RIGHT]:
                self.selected_option = 1
                return True
            elif event.key in [pygame.K_e, pygame.K_RETURN, pygame.K_SPACE]:
                self._confirm(self.selected_option == 0)
                return False
            elif event.key in [pygame.K_q, pygame.K_ESCAPE]:
                self._confirm(False)
                return False
        
        # Basis-Event-Handling
        return super().handle_event(event)
    
    def draw(self, surface: pygame.Surface) -> None:
        """Zeichnet den Dialog mit erweiterten Features."""
        if not self.is_visible:
            return
        
        # Basis-Menü zeichnen
        super().draw(surface)
        
        # Dialog-spezifische Inhalte
        self._draw_dialog_content(surface)
    
    def _draw_dialog_content(self, surface: pygame.Surface) -> None:
        """Zeichnet den Dialog-spezifischen Inhalt."""
        # Nachricht zeichnen
        message_surf = fonts.normal.render(self.message, True, self.colors['title'])
        message_rect = message_surf.get_rect(center=(self.rect.centerx, self.rect.y + 50))
        surface.blit(message_surf, message_rect)
        
        # Optionen zeichnen
        yes_x = self.rect.x + 50
        no_x = self.rect.x + 150
        option_y = self.rect.y + 80
        
        yes_color = self.colors['selected'] if self.selected_option == 0 else self.colors['unselected']
        no_color = self.colors['selected'] if self.selected_option == 1 else self.colors['unselected']
        
        yes_surf = fonts.normal.render("Ja", True, yes_color)
        no_surf = fonts.normal.render("Nein", True, no_color)
        
        surface.blit(yes_surf, (yes_x, option_y))
        surface.blit(no_surf, (no_x, option_y))


class MenuManager:
    """Verwaltet alle Menüs und Übergänge."""
    
    def __init__(self, game: 'Game'):
        self.game = game
        self.current_menu: Optional[EnhancedMenuBase] = None
        self.menu_stack: List[EnhancedMenuBase] = []
        self.transition_manager = UITransitionManager()
        
        # Menüs initialisieren
        self.inventory_menu = EnhancedInventoryMenu(game)
        self.party_menu = EnhancedPartyMenu(game)
        self.quest_menu = EnhancedQuestMenu(game)
        self.save_menu = EnhancedSaveMenu(game)
        
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
    
    def show_quests(self) -> None:
        """Zeigt das Quest-Menü."""
        self._push_menu(self.quest_menu)
    
    def show_save_menu(self, mode: str = 'save') -> None:
        """Zeigt das Save/Load-Menü."""
        self.save_menu.set_mode(mode)
        self._push_menu(self.save_menu)
    
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
