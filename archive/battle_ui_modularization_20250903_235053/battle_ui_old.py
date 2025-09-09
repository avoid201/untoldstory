"""
Pixel JRPG Battle UI für Untold Story
DQM × Pokémon Hybrid mit deutschem Ruhrpott-Flair

UI-Hierarchie:
- BattleUI (Container)
  ├── TamingUI (DQM-spezifisches Taming)
  ├── ScoutDisplay (Monster-Informationen)
  ├── BattleRewardsUI (Belohnungen)
  └── BattleUIEnhancements (Verbesserte Menüs)
"""

import pygame
import random
import time
import logging
from dataclasses import dataclass
from typing import Optional, List, Tuple, Dict, Any, TYPE_CHECKING
from enum import Enum, auto

# Setup logger
logger = logging.getLogger(__name__)

# Import the config constants from the main config
from engine.core.config import (
    LOGICAL_WIDTH, LOGICAL_HEIGHT,
    Colors, Fonts, UI
)

# Import ResourceManager for sprite loading
from engine.core.resources import resources

# Import the sub-UI components
from engine.ui.taming_ui import TamingUI, TamingUIState
from engine.ui.scout_display import ScoutDisplay, ScoutDisplayTab
from engine.ui.battle_ui_utils import fonts, types, sprites, colors, text_utils

# Import enhanced UI components (merged from battle_ui_enhancements.py)

# Import item and move registries
from engine.systems.items import item_registry
from engine.systems.moves import move_registry

# Import new battle system components
from engine.systems.battle.battle_state import BattleState
from engine.systems.battle.battle_controller import BattleController
from engine.systems.battle.turn_processor import TurnProcessor
from engine.systems.battle.action_processor import ActionProcessor
from engine.systems.battle.event_processor import EventProcessor, EventType, BattleEvent
from engine.systems.battle.status_processor import StatusProcessor

# Constants for pixel-perfect UI
TILE_SIZE = 16
UI_SCALE = 1
FONT_SIZE = 8

# ENTFERNT: BattleActionFactory - ersetzt durch UnifiedAction
    


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

class BattleMenuState(Enum):
    """Battle menu states - DQM style."""
    MAIN = auto()           # Hauptmenü mit 6 Optionen
    MOVE_SELECT = auto()    # Move-Auswahl nach Kategorien
    ITEM_SELECT = auto()    # Item-Menü mit Kategorien
    SWITCH_SELECT = auto()  # Team-Wechsel
    TAME_MEAT = auto()      # Fleisch-Auswahl für Zähmen
    TAME_CONFIRM = auto()   # Zähm-Bestätigung mit Chancen
    SCOUT = auto()          # Monster-Analyse
    WAITING = auto()        # Warte auf Animation
    MESSAGE = auto()        # Zeige Nachricht
    SKILL_SELECT = auto()   # Erweiterte Skill-Auswahl
    ENHANCED_ITEM = auto()  # Erweiterte Item-Auswahl


class SkillMenu:
    """Skills-Untermenü für Battle System mit visuellen Highlights."""
    
    def __init__(self):
        self.selected_index = 0
        self.skills = []
        self.menu_pos = (10, 80)
        self.menu_width = 300  # Vergrößert für Details
        self.menu_height = 150  # Vergrößert für Details
        
        # Animations-Eigenschaften
        self.highlight_alpha = 0
        self.highlight_direction = 1
        self.pulse_timer = 0
        self.slide_offset = 0
    
    @property
    def font(self):
        """Get font using centralized font manager."""
        return fonts.small
    
    @property
    def detail_font(self):
        """Get detail font using centralized font manager."""
        return fonts.tiny
    
    @property
    def big_font(self):
        """Get big font using centralized font manager."""
        return fonts.normal
    
    def set_skills(self, monster):
        """Setze Skills vom aktiven Monster."""
        if monster and hasattr(monster, 'moves'):
            self.skills = monster.moves[:4]  # Max 4 Skills
        else:
            self.skills = []
        self.selected_index = 0
    
    def draw(self, surface):
        """Zeichne das Skills-Menü mit visuellen Highlights."""
        x, y = self.menu_pos
        
        # Update animations
        self._update_animations()
        
        # Haupthintergrund mit Verlauf
        self._draw_gradient_background(surface, x, y)
        
        # Animierter Rahmen
        border_color = (100 + int(self.highlight_alpha * 0.5), 150 + int(self.highlight_alpha * 0.3), 255)
        pygame.draw.rect(surface, border_color, (x, y, self.menu_width, self.menu_height), 3)
        
        # Titel mit Glow-Effekt
        title_color = (255, 255, 255 - int(self.highlight_alpha * 0.2))
        title = self.big_font.render("⚔️ Skills", True, title_color)
        surface.blit(title, (x + 10, y + 8))
        
        if not self.skills:
            no_skills = self.font.render("Keine Skills verfügbar!", True, colors.get_color('text_gray'))
            surface.blit(no_skills, (x + 10, y + 35))
            return
        
        # Skills Liste
        skills_start_y = y + 35
        for i, skill in enumerate(self.skills):
            skill_y = skills_start_y + i * 20
            is_selected = i == self.selected_index
            
            # Selektions-Highlight mit Animation
            if is_selected:
                highlight_width = self.menu_width - 20
                highlight_alpha = 100 + int(self.highlight_alpha)
                highlight_color = (255, 255, 100, highlight_alpha)
                
                # Erstelle Surface für Alpha-Blending
                highlight_surf = pygame.Surface((highlight_width, 18), pygame.SRCALPHA)
                highlight_surf.fill(highlight_color)
                surface.blit(highlight_surf, (x + 10, skill_y - 2))
            
            # Skill Name mit besserer Typographie
            skill_name = getattr(skill, 'name', f'Skill {i+1}')
            name_color = colors.get_color('text_white') if is_selected else (200, 200, 200)
            if is_selected:
                skill_text = self.font.render(f"► {skill_name}", True, name_color)
            else:
                skill_text = self.font.render(f"  {skill_name}", True, name_color)
            surface.blit(skill_text, (x + 15, skill_y))
            
            # Power/Damage Anzeige
            if hasattr(skill, 'power'):
                power_text = f"⚡{skill.power}"
                power_color = (255, 200, 100) if is_selected else (200, 150, 100)
                power_render = self.detail_font.render(power_text, True, power_color)
                surface.blit(power_render, (x + 140, skill_y + 2))
            
            # PP Bar statt nur Text
            if hasattr(skill, 'current_pp') and hasattr(skill, 'max_pp'):
                self._draw_pp_bar(surface, skill, x + 180, skill_y, is_selected)
            
            # Typ-Icon verbesserter
            if hasattr(skill, 'type'):
                self._draw_type_indicator(surface, skill.type, x + 240, skill_y, is_selected)
        
        # Detail-Panel für ausgewählten Skill
        if self.skills and 0 <= self.selected_index < len(self.skills):
            self._draw_skill_details(surface, self.skills[self.selected_index], x, y + self.menu_height + 10)
    
    def _update_animations(self):
        """Update animation properties."""
        import time
        self.pulse_timer += 0.1
        
        # Highlight pulsing animation
        self.highlight_alpha += self.highlight_direction * 5
        if self.highlight_alpha >= 100:
            self.highlight_direction = -1
        elif self.highlight_alpha <= 0:
            self.highlight_direction = 1
    
    def _draw_gradient_background(self, surface, x, y):
        """Zeichne Verlaufshintergrund."""
        # Einfacher Gradient-Effekt
        for i in range(self.menu_height):
            alpha = int(255 * (0.3 + 0.4 * (i / self.menu_height)))
            color = (40, 40, 60, alpha)
            
            # Erstelle Surface für jede Linie
            line_surf = pygame.Surface((self.menu_width, 1), pygame.SRCALPHA)
            line_surf.fill(color)
            surface.blit(line_surf, (x, y + i))
    
    def _draw_pp_bar(self, surface, skill, x, y, is_selected):
        """Zeichne PP als kleine Bar."""
        bar_width = 40
        bar_height = 6
        
        pp_percent = skill.current_pp / max(1, skill.max_pp)
        
        # Hintergrund
        pygame.draw.rect(surface, (60, 60, 60), (x, y + 5, bar_width, bar_height))
        
        # PP Bar
        pp_bar_width = int(bar_width * pp_percent)
        if pp_percent > 0.6:
            pp_color = (100, 255, 100)  # Grün
        elif pp_percent > 0.3:
            pp_color = (255, 255, 100)  # Gelb
        else:
            pp_color = (255, 100, 100)  # Rot
        
        if is_selected:
            # Hellere Farbe wenn ausgewählt
            pp_color = tuple(min(255, c + 50) for c in pp_color)
        
        pygame.draw.rect(surface, pp_color, (x, y + 5, pp_bar_width, bar_height))
        
        # PP Text
        pp_text = f"{skill.current_pp}/{skill.max_pp}"
        pp_text_color = colors.get_color('text_white') if is_selected else (200, 200, 200)
        pp_render = self.detail_font.render(pp_text, True, pp_text_color)
        surface.blit(pp_render, (x, y + 13))
    
    def _draw_type_indicator(self, surface, skill_type, x, y, is_selected):
        """Zeichne verbessertes Typ-Icon using centralized type manager."""
        type_color = types.get_type_color(skill_type)
        
        if is_selected:
            # Größerer, hellerer Indikator wenn ausgewählt
            pygame.draw.rect(surface, type_color, (x, y + 2, 20, 12))
            pygame.draw.rect(surface, colors.get_color('text_white'), (x, y + 2, 20, 12), 1)
            
            # Typ-Text
            type_text = self.detail_font.render(skill_type[:3], True, colors.get_color('text_white'))
            surface.blit(type_text, (x + 2, y + 4))
        else:
            # Kleinerer Indikator
            pygame.draw.rect(surface, type_color, (x, y + 4, 15, 8))
    
    def _draw_skill_details(self, surface, skill, x, y):
        """Zeichne detaillierte Skill-Informationen."""
        detail_width = self.menu_width
        detail_height = 80
        
        # Detail-Panel Hintergrund
        detail_bg = (30, 30, 50, 200)
        detail_surf = pygame.Surface((detail_width, detail_height), pygame.SRCALPHA)
        detail_surf.fill(detail_bg)
        surface.blit(detail_surf, (x, y))
        
        # Rahmen
        pygame.draw.rect(surface, (100, 150, 255), (x, y, detail_width, detail_height), 2)
        
        # Skill Name groß
        skill_name = getattr(skill, 'name', 'Unknown Skill')
        name_text = self.big_font.render(skill_name, True, colors.get_color('text_white'))
        surface.blit(name_text, (x + 10, y + 8))
        
        # Beschreibung (falls vorhanden)
        description = getattr(skill, 'description', 'Keine Beschreibung verfügbar.')
        desc_lines = self._wrap_text(description, detail_width - 20)
        
        for i, line in enumerate(desc_lines[:2]):  # Max 2 Zeilen
            desc_text = self.detail_font.render(line, True, (200, 200, 200))
            surface.blit(desc_text, (x + 10, y + 30 + i * 12))
        
        # Stats in unterer Reihe
        stats_y = y + detail_height - 20
        
        # Power
        if hasattr(skill, 'power'):
            power_text = f"Power: {skill.power}"
            power_render = self.detail_font.render(power_text, True, (255, 200, 100))
            surface.blit(power_render, (x + 10, stats_y))
        
        # Accuracy
        if hasattr(skill, 'accuracy'):
            acc_text = f"Accuracy: {skill.accuracy}%"
            acc_render = self.detail_font.render(acc_text, True, (150, 255, 150))
            surface.blit(acc_render, (x + 80, stats_y))
        
        # Category
        if hasattr(skill, 'category'):
            cat_text = f"Type: {skill.category}"
            cat_render = self.detail_font.render(cat_text, True, (150, 200, 255))
            surface.blit(cat_render, (x + 170, stats_y))
    
    def _wrap_text(self, text, max_width):
        """Wrap text to fit within width."""
        return text_utils.wrap_text(text, max_width, self.detail_font)
    
    def handle_input(self, action):
        """Handle Skills-Menü Input."""
        if action == 'up':
            self.selected_index = max(0, self.selected_index - 1)
        elif action == 'down':
            self.selected_index = min(len(self.skills) - 1, self.selected_index + 1)
        elif action == 'confirm':
            if self.skills and self.selected_index < len(self.skills):
                return self.skills[self.selected_index]
        elif action == 'back':
            return 'cancel'
        return None


class ItemMenu:
    """Items-Menü für Battle System mit Effekt-Anzeige."""
    
    def __init__(self):
        self.selected_index = 0
        self.items = []
        self.menu_pos = (10, 80)
        self.menu_width = 300  # Vergrößert für Details
        self.menu_height = 140  # Vergrößert für Details
        
        # Animation properties
        self.shimmer_offset = 0
        self.pulse_timer = 0
    
    @property
    def font(self):
        """Get font using centralized font manager."""
        return fonts.small
    
    @property
    def detail_font(self):
        """Get detail font using centralized font manager."""
        return fonts.tiny
    
    @property
    def big_font(self):
        """Get big font using centralized font manager."""
        return fonts.normal
    
    def set_items(self, items):
        """Setze verfügbare Items."""
        self.items = items[:4] if items else []  # Max 4 Items
        self.selected_index = 0
    
    def draw(self, surface):
        """Zeichne das Items-Menü mit Effekt-Anzeige."""
        x, y = self.menu_pos
        
        # Update animations
        self._update_animations()
        
        # Hintergrund mit warmem Gradient
        self._draw_warm_gradient_background(surface, x, y)
        
        # Glimmernder Rahmen für Items
        border_color = (255, 150 + int(30 * abs(self.shimmer_offset)), 100)
        pygame.draw.rect(surface, border_color, (x, y, self.menu_width, self.menu_height), 3)
        
        # Titel mit Item-Icon
        title_color = (255, 220, 180)
        title = self.big_font.render("🎒 Items", True, title_color)
        surface.blit(title, (x + 10, y + 8))
        
        if not self.items:
            no_items = self.font.render("Inventar ist leer!", True, (200, 150, 150))
            surface.blit(no_items, (x + 10, y + 35))
            return
        
        # Items Liste
        items_start_y = y + 35
        for i, item in enumerate(self.items):
            item_y = items_start_y + i * 20
            is_selected = i == self.selected_index
            
            # Selektions-Highlight
            if is_selected:
                highlight_alpha = 120 + int(20 * self.shimmer_offset)
                highlight_color = (255, 200, 100, highlight_alpha)
                
                highlight_surf = pygame.Surface((self.menu_width - 20, 18), pygame.SRCALPHA)
                highlight_surf.fill(highlight_color)
                surface.blit(highlight_surf, (x + 10, item_y - 2))
            
            # Item Icon (basierend auf Item-Typ)
            item_icon = self._get_item_icon(item)
            icon_color = (255, 255, 255) if is_selected else (200, 200, 200)
            
            # Item Name mit Icon
            item_name = getattr(item, 'name', f'Item {i+1}')
            name_color = colors.get_color('text_white') if is_selected else (200, 200, 200)
            
            if is_selected:
                item_text = self.font.render(f"{item_icon} {item_name}", True, name_color)
            else:
                item_text = self.font.render(f"{item_icon} {item_name}", True, name_color)
            surface.blit(item_text, (x + 15, item_y))
            
            # Quantity mit verbesserter Anzeige
            if hasattr(item, 'quantity'):
                qty_text = f"x{item.quantity}"
                qty_color = (150, 255, 150) if is_selected else (150, 200, 150)
                qty_render = self.detail_font.render(qty_text, True, qty_color)
                surface.blit(qty_render, (x + 180, item_y + 3))
            
            # Rarity/Quality Indikator
            rarity = getattr(item, 'rarity', 'common')
            self._draw_rarity_indicator(surface, rarity, x + 220, item_y, is_selected)
            
            # Quick Effect Preview
            if is_selected:
                effect_preview = self._get_effect_preview(item)
                if effect_preview:
                    effect_text = self.detail_font.render(effect_preview, True, (255, 255, 100))
                    surface.blit(effect_text, (x + 15, item_y + 12))
        
        # Detail-Panel für ausgewähltes Item
        if self.items and 0 <= self.selected_index < len(self.items):
            self._draw_item_details(surface, self.items[self.selected_index], x, y + self.menu_height + 10)
    
    def _update_animations(self):
        """Update animation properties."""
        import math
        self.pulse_timer += 0.1
        self.shimmer_offset = math.sin(self.pulse_timer) * 0.5
    
    def _draw_warm_gradient_background(self, surface, x, y):
        """Zeichne warmen Gradient für Items."""
        for i in range(self.menu_height):
            # Warm, einladender Gradient für Items
            progress = i / self.menu_height
            r = int(60 + 20 * progress)
            g = int(40 + 15 * progress)
            b = int(40 + 10 * progress)
            alpha = int(255 * (0.4 + 0.3 * progress))
            
            line_surf = pygame.Surface((self.menu_width, 1), pygame.SRCALPHA)
            line_surf.fill((r, g, b, alpha))
            surface.blit(line_surf, (x, y + i))
    
    def _get_item_icon(self, item):
        """Get appropriate icon for item type."""
        item_name = getattr(item, 'name', '').lower()
        item_type = getattr(item, 'type', '').lower()
        
        # Health items
        if 'heal' in item_name or 'potion' in item_name or 'herb' in item_name:
            return "🧪"
        elif 'revive' in item_name or 'phoenix' in item_name:
            return "⭐"
        elif 'antidote' in item_name or 'cure' in item_name:
            return "💊"
        # Stat boosters
        elif 'boost' in item_name or 'enhance' in item_name:
            return "⚡"
        # Battle items
        elif 'ball' in item_name or 'capture' in item_name:
            return "⚪"
        # Food/berries
        elif 'berry' in item_name or 'fruit' in item_name:
            return "🍓"
        # Tools
        elif 'tool' in item_name or 'device' in item_name:
            return "🔧"
        else:
            return "📦"  # Default
    
    def _draw_rarity_indicator(self, surface, rarity, x, y, is_selected):
        """Zeichne Seltenheits-Indikator."""
        rarity_colors = {
            'common': (150, 150, 150),
            'uncommon': (100, 255, 100),
            'rare': (100, 150, 255),
            'epic': (200, 100, 255),
            'legendary': (255, 200, 50),
            'mythic': (255, 100, 255),
        }
        
        rarity_color = rarity_colors.get(rarity.lower(), (150, 150, 150))
        
        if is_selected:
            # Größerer Indikator mit Glow
            pygame.draw.circle(surface, rarity_color, (x + 8, y + 8), 6)
            pygame.draw.circle(surface, (255, 255, 255), (x + 8, y + 8), 6, 1)
        else:
            # Kleinerer Indikator
            pygame.draw.circle(surface, rarity_color, (x + 6, y + 8), 4)
    
    def _get_effect_preview(self, item):
        """Get quick preview of item effect."""
        # Versuche Effekt-Informationen zu extrahieren
        if hasattr(item, 'effect_type'):
            effect_type = item.effect_type
            if hasattr(item, 'value'):
                value = item.value
                return f"{effect_type}: +{value}"
            else:
                return str(effect_type)
        
        # Fallback basierend auf Namen
        item_name = getattr(item, 'name', '').lower()
        if 'heal' in item_name:
            return "Heilt HP"
        elif 'revive' in item_name:
            return "Belebt wieder"
        elif 'boost' in item_name:
            return "Verstärkt Stats"
        elif 'antidote' in item_name:
            return "Heilt Gift"
        
        return None
    
    def _draw_item_details(self, surface, item, x, y):
        """Zeichne detaillierte Item-Informationen."""
        detail_width = self.menu_width
        detail_height = 90
        
        # Detail-Panel Hintergrund (warmer Ton für Items)
        detail_bg = (50, 30, 20, 220)
        detail_surf = pygame.Surface((detail_width, detail_height), pygame.SRCALPHA)
        detail_surf.fill(detail_bg)
        surface.blit(detail_surf, (x, y))
        
        # Rahmen
        pygame.draw.rect(surface, (255, 150, 100), (x, y, detail_width, detail_height), 2)
        
        # Item Name mit Icon
        item_name = getattr(item, 'name', 'Unknown Item')
        item_icon = self._get_item_icon(item)
        name_text = self.big_font.render(f"{item_icon} {item_name}", True, (255, 255, 255))
        surface.blit(name_text, (x + 10, y + 8))
        
        # Rarity
        rarity = getattr(item, 'rarity', 'common')
        rarity_color = {
            'common': (150, 150, 150),
            'uncommon': (100, 255, 100),
            'rare': (100, 150, 255),
            'epic': (200, 100, 255),
            'legendary': (255, 200, 50),
            'mythic': (255, 100, 255),
        }.get(rarity.lower(), (150, 150, 150))
        
        rarity_text = self.detail_font.render(f"[{rarity.upper()}]", True, rarity_color)
        surface.blit(rarity_text, (x + 200, y + 12))
        
        # Beschreibung
        description = getattr(item, 'description', 'Keine Beschreibung verfügbar.')
        desc_lines = self._wrap_text(description, detail_width - 20)
        
        for i, line in enumerate(desc_lines[:2]):  # Max 2 Zeilen
            desc_text = self.detail_font.render(line, True, (220, 200, 180))
            surface.blit(desc_text, (x + 10, y + 30 + i * 12))
        
        # Effekt-Details in unterer Reihe
        effects_y = y + detail_height - 25
        
        # Haupteffekt
        if hasattr(item, 'effect_type'):
            effect_text = f"Effect: {item.effect_type}"
            if hasattr(item, 'value'):
                effect_text += f" (+{item.value})"
            effect_render = self.detail_font.render(effect_text, True, (100, 255, 150))
            surface.blit(effect_render, (x + 10, effects_y))
        
        # Target
        if hasattr(item, 'target'):
            target_text = f"Target: {item.target}"
            target_render = self.detail_font.render(target_text, True, (150, 200, 255))
            surface.blit(target_render, (x + 10, effects_y + 12))
        
        # Usage Hinweis
        usage_text = "Press ENTER to use"
        usage_render = self.detail_font.render(usage_text, True, (255, 255, 100))
        surface.blit(usage_render, (x + 180, effects_y + 12))
    
    def _wrap_text(self, text, max_width):
        """Wrap text to fit within width."""
        return text_utils.wrap_text(text, max_width, self.detail_font)
    
    def handle_input(self, action):
        """Handle Items-Menü Input."""
        if action == 'up':
            self.selected_index = max(0, self.selected_index - 1)
        elif action == 'down':
            self.selected_index = min(len(self.items) - 1, self.selected_index + 1)
        elif action == 'confirm':
            if self.items and self.selected_index < len(self.items):
                return self.items[self.selected_index]
        elif action == 'back':
            return 'cancel'
        return None


class EnhancedMainBattleMenu:
    """Visuell verbessertes Haupt-Battle-Menü."""
    
    def __init__(self, is_wild_battle=True):
        self.selected_index = 0
        self.is_wild_battle = is_wild_battle
        self.menu_pos = (50, 120)
        self.menu_width = 220
        self.menu_height = 120
        
        # Animation properties
        self.glow_intensity = 0
        self.glow_direction = 1
        self.selection_offset = 0
        
        # Menu options basierend auf Battle-Typ
        if is_wild_battle:
            self.options = ["⚔️ Angreifen", "✨ Skills", "🎯 Zähmen", "🎒 Items", "🏃 Fliehen"]
        else:
            self.options = ["⚔️ Angreifen", "✨ Skills", "🎒 Items", "👥 Team", "🏳️ Aufgeben"]
    
    @property
    def font(self):
        """Get font using centralized font manager."""
        return fonts.normal
    
    @property
    def big_font(self):
        """Get big font using centralized font manager."""
        return fonts.large
    
    def set_battle_type(self, is_wild):
        """Update menu options based on battle type."""
        self.is_wild_battle = is_wild
        if is_wild:
            self.options = ["⚔️ Angreifen", "✨ Skills", "🎯 Zähmen", "🎒 Items", "🏃 Fliehen"]
        else:
            self.options = ["⚔️ Angreifen", "✨ Skills", "🎒 Items", "👥 Team", "🏳️ Aufgeben"]
        self.selected_index = min(self.selected_index, len(self.options) - 1)
    
    def draw(self, surface):
        """Zeichne das Haupt-Battle-Menü mit Animationen."""
        x, y = self.menu_pos
        
        # Update animations
        self._update_animations()
        
        # Haupt-Panel mit elegantem Design
        self._draw_elegant_background(surface, x, y)
        
        # Titel
        title_text = "Was soll dein Monster tun?"
        title_color = (255, 255, 200)
        title_render = self.font.render(title_text, True, title_color)
        title_x = x + (self.menu_width - title_render.get_width()) // 2
        surface.blit(title_render, (title_x, y + 8))
        
        # Menu Optionen mit verbesserter Darstellung
        options_start_y = y + 30
        for i, option in enumerate(self.options):
            option_y = options_start_y + i * 18
            is_selected = i == self.selected_index
            
            # Selection Glow/Highlight
            if is_selected:
                self._draw_selection_highlight(surface, x + 10, option_y - 2, self.menu_width - 20, 16)
            
            # Option Text mit verschiedenen Farben je nach Typ
            text_color = self._get_option_color(option, is_selected)
            
            if is_selected:
                # Bewegter Text für ausgewählte Option
                option_x = x + 15 + int(self.selection_offset)
            else:
                option_x = x + 20
            
            option_render = self.font.render(option, True, text_color)
            surface.blit(option_render, (option_x, option_y))
            
            # Hover-Beschreibung für ausgewählte Option
            if is_selected:
                description = self._get_option_description(option)
                if description:
                    desc_color = (200, 200, 150)
                    desc_render = fonts.tiny.render(description, True, desc_color)
                    surface.blit(desc_render, (x + 15, option_y + 14))
    
    def _update_animations(self):
        """Update animation properties."""
        # Glow animation
        self.glow_intensity += self.glow_direction * 3
        if self.glow_intensity >= 100:
            self.glow_direction = -1
        elif self.glow_intensity <= 0:
            self.glow_direction = 1
        
        # Selection offset animation
        import math
        self.selection_offset = math.sin(self.glow_intensity * 0.1) * 2
    
    def _draw_elegant_background(self, surface, x, y):
        """Zeichne eleganten Hintergrund für das Hauptmenü."""
        # Gradient background
        for i in range(self.menu_height):
            progress = i / self.menu_height
            r = int(30 + 20 * progress)
            g = int(30 + 25 * progress)
            b = int(50 + 30 * progress)
            alpha = int(255 * (0.85 + 0.1 * progress))
            
            line_surf = pygame.Surface((self.menu_width, 1), pygame.SRCALPHA)
            line_surf.fill((r, g, b, alpha))
            surface.blit(line_surf, (x, y + i))
        
        # Animated border
        border_intensity = 150 + int(self.glow_intensity * 0.5)
        border_color = (100, border_intensity, 200)
        pygame.draw.rect(surface, border_color, (x, y, self.menu_width, self.menu_height), 3)
        
        # Corner decorations
        corner_color = (255, 255, 255, 100)
        corner_surf = pygame.Surface((8, 8), pygame.SRCALPHA)
        corner_surf.fill(corner_color)
        
        # Top corners
        surface.blit(corner_surf, (x - 2, y - 2))
        surface.blit(corner_surf, (x + self.menu_width - 6, y - 2))
        
        # Bottom corners  
        surface.blit(corner_surf, (x - 2, y + self.menu_height - 6))
        surface.blit(corner_surf, (x + self.menu_width - 6, y + self.menu_height - 6))
    
    def _draw_selection_highlight(self, surface, x, y, width, height):
        """Zeichne Highlight für ausgewählte Option."""
        # Pulsing highlight
        alpha = 80 + int(self.glow_intensity * 0.8)
        highlight_color = (255, 255, 100, alpha)
        
        highlight_surf = pygame.Surface((width, height), pygame.SRCALPHA)
        highlight_surf.fill(highlight_color)
        surface.blit(highlight_surf, (x, y))
        
        # Selection border
        pygame.draw.rect(surface, (255, 255, 255), (x, y, width, height), 1)
    
    def _get_option_color(self, option, is_selected):
        """Get color for menu option based on type."""
        if is_selected:
            base_brightness = 255
        else:
            base_brightness = 200
        
        if "Angreifen" in option:
            return (base_brightness, 100, 100)  # Rot für Angriff
        elif "Skills" in option:
            return (100, 100, base_brightness)  # Blau für Skills
        elif "Zähmen" in option:
            return (100, base_brightness, 100)  # Grün für Zähmen
        elif "Items" in option:
            return (base_brightness, base_brightness, 100)  # Gelb für Items
        elif "Fliehen" in option or "Aufgeben" in option:
            return (150, 150, 150)  # Grau für Flucht/Aufgabe
        elif "Team" in option:
            return (200, 150, base_brightness)  # Lila für Team
        else:
            return (base_brightness, base_brightness, base_brightness)  # Weiß default
    
    def _get_option_description(self, option):
        """Get description for menu option."""
        if "Angreifen" in option:
            return "AI wählt besten Angriff"
        elif "Skills" in option:
            return "Wähle spezifischen Skill"
        elif "Zähmen" in option:
            return "Versuche Monster zu zähmen"
        elif "Items" in option:
            return "Nutze Items aus Inventar"
        elif "Fliehen" in option:
            return "Versuche zu fliehen"
        elif "Team" in option:
            return "Wechsle aktives Monster"
        elif "Aufgeben" in option:
            return "Gib den Kampf auf"
        return None
    
    def handle_input(self, action):
        """Handle menu navigation."""
        if action == 'up':
            self.selected_index = max(0, self.selected_index - 1)
            return True
        elif action == 'down':
            self.selected_index = min(len(self.options) - 1, self.selected_index + 1)
            return True
        elif action == 'confirm':
            return self.options[self.selected_index]
        elif action == 'back':
            return 'cancel'
        return None
    
    def get_selected_option(self):
        """Get currently selected option."""
        return self.options[self.selected_index] if 0 <= self.selected_index < len(self.options) else None


class BattleUI:
    """
    Pixel-perfect Battle UI im klassischen JRPG-Style.
    Basiert auf DQM × Pokémon Hybrid-System.
    """
    
    def __init__(self, game):
        self.game = game
        self.battle_state = None
        
        # Compatibility with old BattleUI
        self.sprites: Dict[str, BattleSprite] = {}
        self.hp_animations: Dict[str, Dict] = {}
        
        # CRITICAL FIX: Sprite caching to avoid loading every frame
        self.sprite_cache: Dict[str, pygame.Surface] = {}
        
        # Lazy-loaded sub-UI components for compatibility
        self._taming_ui: Optional['TamingUI'] = None
        self._scout_display: Optional['ScoutDisplay'] = None
        
        # Pixel font loading
        self._init_fonts()
        
        # UI State
        self.menu_state = BattleMenuState.MAIN
        self.cursor_pos = 0
        self.cursor_blink = 0
        
        # CRITICAL: Event system attributes
        self._pending_action = None
        self.event_processor = None
        
        # Menu layouts (2x3 grid für Hauptmenü)
        self.main_menu_layout = [
            ["ATTACKE", "ITEM"],
            ["WECHSEL", "ZÄHMEN"],
            ["SPÄHEN", "FLUCHT"]
        ]
        self.cursor_row = 0
        self.cursor_col = 0
        
        # Move categories for DQM-style unlimited moves
        self.move_categories = ["PHYSISCH", "MAGISCH", "STATUS"]
        self.current_category = 0
        self.moves_in_category = []
        self.move_cursor = 0
        
        # Item categories
        self.item_categories = ["HEILUNG", "KAMPF", "FLEISCH"]
        self.current_item_category = 0
        self.items_in_category = []
        self.item_cursor = 0
        
        # Meat system for taming
        self.meat_types = {
            "kein_fleisch": {"name": "Kein Fleisch", "bonus": 0},
            "fleisch": {"name": "Fleisch", "bonus": 20},
            "edelfleisch": {"name": "Edelfleisch", "bonus": 40},
            "goetterfleisch": {"name": "Götterfleisch", "bonus": 80}
        }
        self.selected_meat = "kein_fleisch"
        self.meat_effect_active = 0  # Current meat bonus
        
        # Messages
        self.message_queue = []
        self.current_message = ""
        self.message_timer = 0
        self.message_char_index = 0
        
        # Visual effects
        self.damage_numbers = []
        self.screen_flash = 0
        self.screen_shake = 0
        
        # Action tracking for controller integration
        self.last_action_type = None
        self.selected_move_id = None
        self.selected_item_id = None
        self.selected_target = None
        self.selected_monster_index = None
        self.selected_meat_id = None
        
        # Pending action for battle controller
        self._pending_action = None
        
        # Use centralized color manager
        self.colors = colors.colors
        
        # Event processor connection
        self.event_processor = None
    
    @property
    def taming_ui(self) -> 'TamingUI':
        """Lazy-loaded taming UI to avoid circular imports."""
        if self._taming_ui is None:
            self._taming_ui = TamingUI()
        return self._taming_ui
    
    @property
    def scout_display(self) -> 'ScoutDisplay':
        """Lazy-loaded scout display to avoid circular imports."""
        if self._scout_display is None:
            self._scout_display = ScoutDisplay()
        return self._scout_display
    
    def _init_fonts(self):
        """Initialize pixel fonts using centralized font manager."""
        self.font_small = fonts.small
        self.font_normal = fonts.normal
        self.font_large = fonts.large
    
    def draw(self, surface: pygame.Surface):
        """Main draw function."""
        # Draw battle field
        self._draw_battlefield(surface)
        
        # Draw monster sprites
        self._draw_monsters(surface)
        
        # Draw HP/Status panels
        self._draw_status_panels(surface)
        
        # Draw menu based on state
        if self.menu_state == BattleMenuState.MAIN:
            self._draw_main_menu(surface)
        elif self.menu_state == BattleMenuState.MOVE_SELECT:
            self._draw_move_menu(surface)
        elif self.menu_state == BattleMenuState.ITEM_SELECT:
            self._draw_item_menu(surface)
        elif self.menu_state == BattleMenuState.SWITCH_SELECT:
            self._draw_switch_menu(surface)
        elif self.menu_state == BattleMenuState.TAME_MEAT:
            self._draw_meat_menu(surface)
        elif self.menu_state == BattleMenuState.TAME_CONFIRM:
            self._draw_tame_confirm(surface)
        elif self.menu_state == BattleMenuState.SCOUT:
            self._draw_scout_display(surface)
        elif self.menu_state == BattleMenuState.MESSAGE:
            self._draw_message_box(surface)
        
        # Draw damage numbers
        self._draw_damage_numbers(surface)
        
        # Draw screen effects
        self._draw_screen_effects(surface)
    
    def _draw_battlefield(self, surface: pygame.Surface):
        """Draw the pixel art battlefield."""
        # Simple gradient background
        for y in range(0, 180, 2):
            color_val = 20 + (y // 4)
            color = (color_val, color_val, color_val + 10)
            pygame.draw.rect(surface, color, (0, y, 320, 2))
        
        # Battle platform lines
        # Player side
        pygame.draw.ellipse(surface, self.colors['border'], (200, 100, 80, 30), 2)
        # Enemy side
        pygame.draw.ellipse(surface, self.colors['border'], (40, 40, 80, 30), 2)
    
    def _draw_monsters(self, surface: pygame.Surface):
        """Draw monster sprites in pixel art style."""
        if not self.battle_state:
            return
        
        # Enemy monster (left side)
        if self.battle_state and self.battle_state.enemy_active:
            self._draw_monster_sprite(surface, self.battle_state.enemy_active, (80, 30), False)
        
        # Player monster (right side)
        if self.battle_state and self.battle_state.player_active:
            self._draw_monster_sprite(surface, self.battle_state.player_active, (240, 90), True)
    
    def _draw_monster_sprite(self, surface, monster, pos, is_player):
        """Draw a single monster sprite using centralized sprite manager with caching."""
        # CRITICAL FIX: Use sprite caching to avoid loading every frame
        cache_key = f"{monster.name}_{is_player}_56x56"
        
        if cache_key not in self.sprite_cache:
            # Load sprite only once and cache it
            sprite_surface = sprites.get_monster_sprite(
                monster=monster,
                target_size=(56, 56),  # Battle-Größe
                is_player_side=is_player
            )
            self.sprite_cache[cache_key] = sprite_surface
        else:
            sprite_surface = self.sprite_cache[cache_key]
        
        # Draw monster sprite
        sprite_rect = sprite_surface.get_rect(center=pos)
        surface.blit(sprite_surface, sprite_rect)
        
        # Monster name
        name_text = self.font_small.render(monster.name[:8], True, self.colors['text_white'])
        surface.blit(name_text, (pos[0] - name_text.get_width()//2, pos[1] - 10))
    

    
    def _draw_status_panels(self, surface):
        """Draw HP/Status panels for monsters."""
        if not self.battle_state:
            return
        
        # Enemy panel (top-left)
        if self.battle_state and self.battle_state.enemy_active:
            self._draw_single_status_panel(surface, self.battle_state.enemy_active, (10, 10), False)
        
        # Player panel (bottom-right)
        if self.battle_state and self.battle_state.player_active:
            self._draw_single_status_panel(surface, self.battle_state.player_active, (180, 100), True)
    
    def _draw_single_status_panel(self, surface, monster, pos, is_player):
        """Draw a single status panel."""
        panel_width = 130
        panel_height = 40
        
        # Panel background
        pygame.draw.rect(surface, self.colors['bg_dark'], (pos[0], pos[1], panel_width, panel_height))
        pygame.draw.rect(surface, self.colors['border'], (pos[0], pos[1], panel_width, panel_height), 1)
        
        # Monster name and level
        name_text = f"{monster.name[:10]} Lv.{monster.level}"
        text_surf = self.font_small.render(name_text, True, self.colors['text_white'])
        surface.blit(text_surf, (pos[0] + 3, pos[1] + 2))
        
        # HP Bar
        hp_ratio = monster.current_hp / max(1, monster.max_hp)
        hp_color = self._get_hp_color(hp_ratio)
        
        # HP bar background
        bar_x = pos[0] + 20
        bar_y = pos[1] + 14
        bar_width = 100
        bar_height = 6
        pygame.draw.rect(surface, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
        
        # HP bar fill
        fill_width = int(bar_width * hp_ratio)
        pygame.draw.rect(surface, hp_color, (bar_x, bar_y, fill_width, bar_height))
        
        # HP text
        hp_text = self.font_small.render("HP", True, self.colors['text_white'])
        surface.blit(hp_text, (pos[0] + 3, pos[1] + 12))
        
        # HP numbers
        hp_numbers = f"{monster.current_hp}/{monster.max_hp}"
        numbers_text = self.font_small.render(hp_numbers, True, self.colors['text_white'])
        surface.blit(numbers_text, (pos[0] + 65, pos[1] + 22))
        
        # Status conditions - KRITISCHE VERBINDUNG: DQM Status System!
        self._draw_status_conditions(surface, monster, pos)
    
    def _draw_status_conditions(self, surface, monster, pos):
        """Draw status condition icons - UNIFIED STATUS ACCESS."""
        try:
            # UNIFIED STATUS CHECK: Only use monster.status
            status_to_display = []
            
            if hasattr(monster, 'status') and monster.status:
                if hasattr(monster.status, 'value'):
                    status_name = monster.status.value
                elif hasattr(monster.status, 'name'):
                    status_name = monster.status.name
                else:
                    status_name = str(monster.status)
                if status_name and status_name.lower() not in ['none', 'normal', '']:
                    status_to_display.append(status_name)
            
            if not status_to_display:
                return
            
            # Status colors
            status_colors = {
                'poison': (150, 50, 150),
                'burn': (255, 100, 50),
                'freeze': (100, 200, 255),
                'sleep': (150, 150, 255),
                'paralysis': (255, 255, 100),
                'confusion': (200, 100, 200)
            }
            
            # Draw first status (space limited)
            if status_to_display:
                status_name = status_to_display[0]
                color = status_colors.get(status_name, (255, 255, 255))
                text = self.font_small.render(status_name.upper()[:4], True, color)
                surface.blit(text, (pos[0] + 3, pos[1] + 30))
                
        except Exception as e:
            logger.debug(f"Status display fallback: {e}")
            # Silent fallback - no status shown
    
    def _draw_main_menu(self, surface):
        """Draw the main battle menu (6 options in 2x3 grid)."""
        menu_x = 10
        menu_y = 140
        menu_width = 300
        menu_height = 35
        
        # Menu background
        pygame.draw.rect(surface, self.colors['bg_dark'], (menu_x, menu_y, menu_width, menu_height))
        pygame.draw.rect(surface, self.colors['border'], (menu_x, menu_y, menu_width, menu_height), 2)
        
        # Title
        title = f"Was soll {self.battle_state.player_active.name if self.battle_state and self.battle_state.player_active else 'Monster'} tun?"
        title_text = self.font_normal.render(title, True, self.colors['text_white'])
        surface.blit(title_text, (menu_x + 5, menu_y - 15))
        
        # Draw menu options in grid
        for row in range(3):
            for col in range(2):
                option = self.main_menu_layout[row][col]
                x = menu_x + 10 + col * 145
                y = menu_y + 5 + row * 10
                
                # Highlight selected option
                if row == self.cursor_row and col == self.cursor_col:
                    # Draw cursor
                    cursor_rect = (x - 8, y, 6, 8)
                    if self.cursor_blink < 15:
                        pygame.draw.polygon(surface, self.colors['text_yellow'], 
                                           [(x - 6, y + 2), (x - 2, y + 4), (x - 6, y + 6)])
                    color = self.colors['text_yellow']
                else:
                    color = self.colors['text_white']
                
                text = self.font_normal.render(option, True, color)
                surface.blit(text, (x, y))
    
    def _draw_move_menu(self, surface):
        """Draw move selection menu with categories (DQM style)."""
        menu_x = 10
        menu_y = 100
        menu_width = 300
        menu_height = 75
        
        # Menu background
        pygame.draw.rect(surface, self.colors['bg_dark'], (menu_x, menu_y, menu_width, menu_height))
        pygame.draw.rect(surface, self.colors['border'], (menu_x, menu_y, menu_width, menu_height), 2)
        
        # Title
        title_text = self.font_normal.render("Welche Attacke einsetzen?", True, self.colors['text_white'])
        surface.blit(title_text, (menu_x + 5, menu_y + 3))
        
        # Category tabs
        tab_y = menu_y + 15
        for i, category in enumerate(self.move_categories):
            x = menu_x + 5 + i * 100
            if i == self.current_category:
                pygame.draw.rect(surface, self.colors['border_selected'], (x - 2, tab_y - 2, 95, 12), 1)
                color = self.colors['text_yellow']
            else:
                color = self.colors['text_gray']
            
            text = self.font_small.render(category, True, color)
            surface.blit(text, (x, tab_y))
        
        # Moves in current category
        moves_y = tab_y + 15
        if self.battle_state and self.battle_state.player_active:
            monster = self.battle_state.player_active
            if hasattr(monster, 'moves'):
                # Filter moves by category
                category_moves = self._get_moves_by_category(monster.moves, self.move_categories[self.current_category])
                
                for i, move in enumerate(category_moves[:5]):  # Max 5 moves shown
                    y = moves_y + i * 10
                    
                    # Cursor for selected move
                    if i == self.move_cursor:
                        if self.cursor_blink < 15:
                            pygame.draw.polygon(surface, self.colors['text_yellow'],
                                              [(menu_x + 5, y + 2), (menu_x + 9, y + 4), (menu_x + 5, y + 6)])
                        color = self.colors['text_yellow']
                    else:
                        color = self.colors['text_white']
                    
                    # Move name and type
                    move_text = f"{move.name[:12]}"
                    text = self.font_small.render(move_text, True, color)
                    surface.blit(text, (menu_x + 15, y))
                    
                    # Move type indicator
                    type_text = f"[{move.type[:3]}]"
                    type_color = self._get_type_color(move.type)
                    text = self.font_small.render(type_text, True, type_color)
                    surface.blit(text, (menu_x + 120, y))
                    
                    # Move power (if applicable)
                    if hasattr(move, 'power') and move.power > 0:
                        power_text = f"PWR:{move.power}"
                        text = self.font_small.render(power_text, True, self.colors['text_gray'])
                        surface.blit(text, (menu_x + 180, y))
        
        # Back option
        back_text = "[X] Zurück"
        text = self.font_small.render(back_text, True, self.colors['text_gray'])
        surface.blit(text, (menu_x + 250, menu_y + menu_height - 10))
    
    def _draw_item_menu(self, surface):
        """Draw item selection menu with categories."""
        menu_x = 10
        menu_y = 100
        menu_width = 300
        menu_height = 75
        
        # Menu background
        pygame.draw.rect(surface, self.colors['bg_dark'], (menu_x, menu_y, menu_width, menu_height))
        pygame.draw.rect(surface, self.colors['border'], (menu_x, menu_y, menu_width, menu_height), 2)
        
        # Title
        title_text = self.font_normal.render("Welches Item verwenden?", True, self.colors['text_white'])
        surface.blit(title_text, (menu_x + 5, menu_y + 3))
        
        # Category tabs
        tab_y = menu_y + 15
        for i, category in enumerate(self.item_categories):
            x = menu_x + 5 + i * 100
            if i == self.current_item_category:
                pygame.draw.rect(surface, self.colors['border_selected'], (x - 2, tab_y - 2, 95, 12), 1)
                color = self.colors['text_yellow']
            else:
                color = self.colors['text_gray']
            
            text = self.font_small.render(category, True, color)
            surface.blit(text, (x, tab_y))
        
        # Items in current category
        items_y = tab_y + 15
        
        # Get items from actual inventory
        items = self._get_items_for_category(self.item_categories[self.current_item_category])
        
        # Store current category items for input handling
        self.items_in_category = items
        
        # Draw items
        for i, (item_id, item_name, count, effect) in enumerate(items[:5]):
            y = items_y + i * 10
            
            # Cursor for selected item
            if i == self.item_cursor:
                if self.cursor_blink < 15:
                    pygame.draw.polygon(surface, self.colors['text_yellow'],
                                      [(menu_x + 5, y + 2), (menu_x + 9, y + 4), (menu_x + 5, y + 6)])
                color = self.colors['text_yellow']
            else:
                color = self.colors['text_white'] if count > 0 else self.colors['text_gray']
            
            # Item name and count
            item_text = f"{item_name[:12]} x{count}"
            text = self.font_small.render(item_text, True, color)
            surface.blit(text, (menu_x + 15, y))
            
            # Effect
            effect_text = f"[{effect}]"
            text = self.font_small.render(effect_text, True, self.colors['text_gray'])
            surface.blit(text, (menu_x + 150, y))
        
        # Show if no items available
        if not items:
            no_items_text = "Keine Items verfügbar"
            text = self.font_small.render(no_items_text, True, self.colors['text_gray'])
            surface.blit(text, (menu_x + 15, items_y))
    
    def _draw_switch_menu(self, surface):
        """Draw team switch menu."""
        menu_x = 10
        menu_y = 80
        menu_width = 300
        menu_height = 95
        
        # Menu background
        pygame.draw.rect(surface, self.colors['bg_dark'], (menu_x, menu_y, menu_width, menu_height))
        pygame.draw.rect(surface, self.colors['border'], (menu_x, menu_y, menu_width, menu_height), 2)
        
        # Title
        title_text = self.font_normal.render("Zu welchem Monster wechseln?", True, self.colors['text_white'])
        surface.blit(title_text, (menu_x + 5, menu_y + 3))
        
        # Team list
        if self.battle_state and self.battle_state.player_team:
            team_y = menu_y + 18
            for i, monster in enumerate(self.battle_state.player_team[:6]):
                if not monster:
                    continue
                    
                y = team_y + i * 12
                
                # Cursor for selected monster
                if i == self.cursor_pos:
                    if self.cursor_blink < 15:
                        pygame.draw.polygon(surface, self.colors['text_yellow'],
                                          [(menu_x + 5, y + 2), (menu_x + 9, y + 4), (menu_x + 5, y + 6)])
                    color = self.colors['text_yellow']
                else:
                    color = self.colors['text_white'] if not monster.is_fainted else self.colors['text_gray']
                
                # Monster info
                info_text = f"{monster.name[:10]} Lv.{monster.level}"
                text = self.font_small.render(info_text, True, color)
                surface.blit(text, (menu_x + 15, y))
                
                # HP bar
                hp_ratio = monster.current_hp / max(1, monster.max_hp)
                hp_color = self._get_hp_color(hp_ratio)
                bar_x = menu_x + 120
                bar_width = 60
                bar_height = 4
                
                pygame.draw.rect(surface, (50, 50, 50), (bar_x, y + 2, bar_width, bar_height))
                fill_width = int(bar_width * hp_ratio)
                pygame.draw.rect(surface, hp_color, (bar_x, y + 2, fill_width, bar_height))
                
                # HP numbers
                hp_text = f"{monster.current_hp}/{monster.max_hp}"
                text = self.font_small.render(hp_text, True, self.colors['text_gray'])
                surface.blit(text, (menu_x + 190, y))
        
        # Current monster indicator
        if self.battle_state and self.battle_state.player_active:
            current_text = f"Aktuell: {self.battle_state.player_active.name}"
            text = self.font_small.render(current_text, True, self.colors['text_gray'])
            surface.blit(text, (menu_x + 5, menu_y + menu_height - 10))
    
    def _draw_meat_menu(self, surface):
        """Draw meat selection for taming (DQM style)."""
        menu_x = 40
        menu_y = 50
        menu_width = 240
        menu_height = 100
        
        # Menu background
        pygame.draw.rect(surface, self.colors['bg_dark'], (menu_x, menu_y, menu_width, menu_height))
        pygame.draw.rect(surface, self.colors['border_selected'], (menu_x, menu_y, menu_width, menu_height), 2)
        
        # Title
        title_text = self.font_normal.render("FLEISCH VORBEREITUNG", True, self.colors['text_yellow'])
        title_rect = title_text.get_rect(center=(160, menu_y + 10))
        surface.blit(title_text, title_rect)
        
        # Subtitle
        subtitle = "Monster schmackhaft machen?"
        subtitle_text = self.font_small.render(subtitle, True, self.colors['text_white'])
        subtitle_rect = subtitle_text.get_rect(center=(160, menu_y + 22))
        surface.blit(subtitle_text, subtitle_rect)
        
        # Meat options
        meat_y = menu_y + 35
        for i, (meat_id, meat_data) in enumerate(self.meat_types.items()):
            y = meat_y + i * 12
            
            # Cursor
            if i == self.cursor_pos:
                if self.cursor_blink < 15:
                    pygame.draw.polygon(surface, self.colors['text_yellow'],
                                      [(menu_x + 10, y + 2), (menu_x + 14, y + 4), (menu_x + 10, y + 6)])
                color = self.colors['text_yellow']
            else:
                color = self.colors['text_white']
            
            # Meat name and bonus
            text_str = f"{meat_data['name']:15} [+{meat_data['bonus']}% für Kampf]"
            text = self.font_small.render(text_str, True, color)
            surface.blit(text, (menu_x + 20, y))
        
        # Warnings
        warning1 = "⚠ Fleisch wirkt für ALLE Zähmversuche!"
        warning2 = "⚠ Gegner erhält Gratisangriff!"
        
        warn1_text = self.font_small.render(warning1, True, self.colors['text_yellow'])
        warn2_text = self.font_small.render(warning2, True, self.colors['text_yellow'])
        
        surface.blit(warn1_text, (menu_x + 5, menu_y + menu_height - 22))
        surface.blit(warn2_text, (menu_x + 5, menu_y + menu_height - 12))
    
    def _draw_tame_confirm(self, surface):
        """Draw taming confirmation with chance display."""
        if not self.battle_state or not self.battle_state.enemy_active:
            return
            
        enemy = self.battle_state.enemy_active
        
        menu_x = 40
        menu_y = 30
        menu_width = 240
        menu_height = 130
        
        # Menu background
        pygame.draw.rect(surface, self.colors['bg_dark'], (menu_x, menu_y, menu_width, menu_height))
        pygame.draw.rect(surface, self.colors['border_selected'], (menu_x, menu_y, menu_width, menu_height), 2)
        
        # Title
        title_text = self.font_large.render("ZÄHMVERSUCH!", True, self.colors['text_yellow'])
        title_rect = title_text.get_rect(center=(160, menu_y + 12))
        surface.blit(title_text, title_rect)
        
        # Monster info
        rank = 'F'  # Default rank
        if hasattr(enemy, 'species'):
            if hasattr(enemy.species, 'rank'):
                if hasattr(enemy.species.rank, 'value'):
                    rank = enemy.species.rank.value
                else:
                    rank = str(enemy.species.rank)
        info_text = f"Monster: {enemy.name} (Rang {rank})"
        text = self.font_small.render(info_text, True, self.colors['text_white'])
        surface.blit(text, (menu_x + 10, menu_y + 25))
        
        # Calculate taming chance
        base_chance = 15
        hp_bonus = int((1 - enemy.current_hp/enemy.max_hp) * 30)
        meat_bonus = self.meat_effect_active
        
        rank_bonuses = {"F": 10, "E": 5, "D": 0, "C": -5, "B": -10, "A": -15, "S": -20, "X": -30}
        rank = 'F'  # Default rank
        if hasattr(enemy, 'species'):
            if hasattr(enemy.species, 'rank'):
                if hasattr(enemy.species.rank, 'value'):
                    rank = enemy.species.rank.value
                else:
                    rank = str(enemy.species.rank)
        rank_bonus = rank_bonuses.get(rank, 0)
        
        status_bonus = 0
        if hasattr(enemy, 'status') and enemy.status:
            status_bonuses = {
                "sleep": 15, "paralysis": 10, "freeze": 10,
                "confusion": 5, "poison": 0
            }
            status_bonus = status_bonuses.get(enemy.status.value, 0)
        
        final_chance = min(95, base_chance + hp_bonus + meat_bonus + rank_bonus + status_bonus)
        
        # Display modifiers
        y = menu_y + 40
        modifiers = [
            ("Basis-Chance:", f"{base_chance}%"),
            ("HP niedrig:", f"+{hp_bonus}%"),
            ("Fleisch aktiv:", f"+{meat_bonus}%" if meat_bonus > 0 else "INAKTIV"),
            (f"Rang {rank}:", f"{rank_bonus:+d}%"),
            ("Status:", f"+{status_bonus}%" if status_bonus > 0 else "INAKTIV")
        ]
        
        for name, value in modifiers:
            name_text = self.font_small.render(name, True, self.colors['text_gray'])
            value_color = self.colors['text_white'] if "INAKTIV" not in value else self.colors['text_gray']
            value_text = self.font_small.render(value, True, value_color)
            
            surface.blit(name_text, (menu_x + 10, y))
            surface.blit(value_text, (menu_x + 120, y))
            y += 10
        
        # Final chance bar
        pygame.draw.line(surface, self.colors['border'], (menu_x + 10, y + 2), (menu_x + menu_width - 10, y + 2))
        y += 8
        
        final_text = self.font_normal.render(f"FINALE CHANCE: {final_chance}%", True, self.colors['text_yellow'])
        surface.blit(final_text, (menu_x + 10, y))
        
        # Chance bar visualization
        bar_y = y + 15
        bar_width = menu_width - 20
        bar_height = 8
        pygame.draw.rect(surface, (50, 50, 50), (menu_x + 10, bar_y, bar_width, bar_height))
        fill_width = int(bar_width * (final_chance / 100))
        bar_color = self.colors['hp_high'] if final_chance > 50 else self.colors['hp_med'] if final_chance > 25 else self.colors['hp_low']
        pygame.draw.rect(surface, bar_color, (menu_x + 10, bar_y, fill_width, bar_height))
        
        # Options
        options = ["Zähmen versuchen", "Abbrechen"]
        option_y = menu_y + menu_height - 25
        for i, option in enumerate(options):
            if i == self.cursor_pos:
                if self.cursor_blink < 15:
                    pygame.draw.polygon(surface, self.colors['text_yellow'],
                                      [(menu_x + 8, option_y + 2 + i*10), 
                                       (menu_x + 12, option_y + 4 + i*10), 
                                       (menu_x + 8, option_y + 6 + i*10)])
                color = self.colors['text_yellow']
            else:
                color = self.colors['text_white']
            
            text = self.font_small.render(option, True, color)
            surface.blit(text, (menu_x + 15, option_y + i*10))
    
    def _draw_scout_display(self, surface):
        """Draw monster analysis screen (Scout/Spähen)."""
        if not self.battle_state or not self.battle_state.enemy_active:
            return
            
        enemy = self.battle_state.enemy_active
        
        # Full screen overlay
        overlay = pygame.Surface((320, 180))
        overlay.fill(self.colors['bg_dark'])
        overlay.set_alpha(240)
        surface.blit(overlay, (0, 0))
        
        # Main panel
        panel_x = 20
        panel_y = 10
        panel_width = 280
        panel_height = 160
        
        pygame.draw.rect(surface, self.colors['bg_dark'], (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(surface, self.colors['border_selected'], (panel_x, panel_y, panel_width, panel_height), 2)
        
        # Title
        title = "MONSTER-ANALYSE"
        title_text = self.font_large.render(title, True, self.colors['text_yellow'])
        title_rect = title_text.get_rect(center=(160, panel_y + 10))
        surface.blit(title_text, title_rect)
        
        # Monster basic info
        y = panel_y + 25
        rank = 'F'  # Default rank
        if hasattr(enemy, 'species'):
            if hasattr(enemy.species, 'rank'):
                if hasattr(enemy.species.rank, 'value'):
                    rank = enemy.species.rank.value
                else:
                    rank = str(enemy.species.rank)
        
        info_lines = [
            f"Name: {enemy.name}",
            f"Rang: {rank} | Level: {enemy.level}",
            f"Typen: {', '.join(enemy.types) if hasattr(enemy, 'types') else 'Unbekannt'}"
        ]
        
        for line in info_lines:
            text = self.font_small.render(line, True, self.colors['text_white'])
            surface.blit(text, (panel_x + 10, y))
            y += 10
        
        # Stats
        y += 5
        stats_title = self.font_small.render("Stats (Aktuell/Max):", True, self.colors['text_gray'])
        surface.blit(stats_title, (panel_x + 10, y))
        y += 10
        
        # Stats in two columns
        stats_left = [
            f"HP:  {enemy.current_hp}/{enemy.max_hp}",
            f"ATK: {enemy.stats.get('atk', '?')}",
            f"DEF: {enemy.stats.get('def', '?')}"
        ]
        stats_right = [
            f"MAG: {enemy.stats.get('mag', '?')}",
            f"RES: {enemy.stats.get('res', '?')}",
            f"SPD: {enemy.stats.get('spd', '?')}"
        ]
        
        for i, (left, right) in enumerate(zip(stats_left, stats_right)):
            left_text = self.font_small.render(left, True, self.colors['text_white'])
            right_text = self.font_small.render(right, True, self.colors['text_white'])
            surface.blit(left_text, (panel_x + 10, y + i*10))
            surface.blit(right_text, (panel_x + 100, y + i*10))
        
        y += 35
        
        # Type effectiveness - Use centralized type manager
        if hasattr(enemy, 'types') and enemy.types:
            weaknesses, resistances = types.calculate_weaknesses_and_resistances(enemy.types)
            
            # Display weaknesses
            if weaknesses:
                weak_text = f"Schwächen: {', '.join(weaknesses[:3])}"
                text = self.font_small.render(weak_text, True, (255, 150, 150))
                surface.blit(text, (panel_x + 10, y))
                y += 10
            
            # Display resistances
            if resistances:
                resist_text = f"Resistenzen: {', '.join(resistances[:3])}"
                text = self.font_small.render(resist_text, True, (150, 255, 150))
                surface.blit(text, (panel_x + 10, y))
                y += 10
        
        # Traits
        if hasattr(enemy.species, 'traits') if hasattr(enemy, 'species') else False:
            traits_text = f"Traits: {', '.join(enemy.species.traits[:2])}"
        else:
            traits_text = "Traits: Keine bekannt"
        text = self.font_small.render(traits_text, True, self.colors['text_gray'])
        surface.blit(text, (panel_x + 10, y))
        y += 15
        
        # Taming chance preview
        base_chance = 15
        hp_bonus = int((1 - enemy.current_hp/enemy.max_hp) * 30)
        current_chance = min(95, base_chance + hp_bonus + self.meat_effect_active)
        
        chance_text = f"Zähm-Chance (aktuell): {current_chance}%"
        text = self.font_small.render(chance_text, True, self.colors['text_yellow'])
        surface.blit(text, (panel_x + 10, y))
        
        # Chance bar
        bar_y = y + 10
        bar_width = 100
        bar_height = 6
        pygame.draw.rect(surface, (50, 50, 50), (panel_x + 10, bar_y, bar_width, bar_height))
        fill_width = int(bar_width * (current_chance / 100))
        bar_color = self.colors['hp_high'] if current_chance > 50 else self.colors['hp_med'] if current_chance > 25 else self.colors['hp_low']
        pygame.draw.rect(surface, bar_color, (panel_x + 10, bar_y, fill_width, bar_height))
        
        # Exit hint
        exit_text = "[ENTER] Weiter"
        text = self.font_small.render(exit_text, True, self.colors['text_gray'])
        surface.blit(text, (panel_x + panel_width - 70, panel_y + panel_height - 15))
    
    def _draw_message_box(self, surface):
        """Draw message box for battle messages."""
        if not self.current_message:
            return
        
        box_x = 10
        box_y = 145
        box_width = 300
        box_height = 30
        
        # Box background
        pygame.draw.rect(surface, self.colors['bg_dark'], (box_x, box_y, box_width, box_height))
        pygame.draw.rect(surface, self.colors['border'], (box_x, box_y, box_width, box_height), 2)
        
        # Message text (with typewriter effect)
        displayed_text = self.current_message[:self.message_char_index]
        text = self.font_normal.render(displayed_text, True, self.colors['text_white'])
        surface.blit(text, (box_x + 5, box_y + 8))
        
        # Blinking cursor at end
        if self.message_char_index >= len(self.current_message) and self.cursor_blink < 15:
            cursor_x = box_x + 5 + text.get_width() + 2
            pygame.draw.rect(surface, self.colors['text_white'], (cursor_x, box_y + 8, 2, 10))
    
    def _draw_damage_numbers(self, surface):
        """Draw floating damage numbers."""
        for number in self.damage_numbers[:]:
            # Update position
            number['y'] -= number['velocity']
            number['velocity'] *= 0.95
            number['timer'] -= 1
            
            if number['timer'] <= 0:
                self.damage_numbers.remove(number)
                continue
            
            # Fade effect
            alpha = min(255, number['timer'] * 8)
            
            # Color based on type
            if number['is_critical']:
                color = (255, 255, 100)  # Yellow for critical
                size = self.font_large
            elif number['is_effective']:
                color = (255, 150, 150)  # Red for super effective
                size = self.font_normal
            elif number['is_heal']:
                color = (100, 255, 100)  # Green for healing
                size = self.font_normal
            elif number['is_status']:
                color = (255, 100, 255)  # Purple for status damage
                size = self.font_normal
            else:
                color = (255, 255, 255)  # White for normal
                size = self.font_normal
            
            # Draw number
            text = size.render(str(number['value']), True, color)
            text.set_alpha(alpha)
            surface.blit(text, (number['x'], int(number['y'])))
    
    def _draw_screen_effects(self, surface):
        """Draw screen-wide effects like flash and shake."""
        # Screen flash
        if self.screen_flash > 0:
            flash_surf = pygame.Surface((320, 180))
            flash_surf.fill((255, 255, 255))
            flash_surf.set_alpha(self.screen_flash)
            surface.blit(flash_surf, (0, 0))
            self.screen_flash = max(0, self.screen_flash - 10)
        
        # Screen shake would be handled by offsetting the entire surface
    
    def _get_hp_color(self, ratio):
        """Get HP bar color based on ratio."""
        if ratio > 0.5:
            return self.colors['hp_high']
        elif ratio > 0.25:
            return self.colors['hp_med']
        else:
            return self.colors['hp_low']
    
    def _get_type_color(self, type_name):
        """Get color for move type using centralized type manager."""
        return types.get_type_color(type_name)
    
    def _get_moves_by_category(self, moves, category):
        """Filter moves by category using move.category_string property."""
        if not moves:
            return []
        
        # Map German category names to English
        category_mapping = {
            'PHYSISCH': 'PHYSICAL',
            'MAGISCH': 'MAGICAL', 
            'STATUS': 'STATUS'
        }
        
        target_category = category_mapping.get(category, category)
        
        # Filter moves using category_string property
        filtered = []
        for move in moves:
            if move is None:
                continue
                
            try:
                # Use the new category_string property
                if hasattr(move, 'category_string'):
                    move_category = move.category_string
                else:
                    # Fallback for old moves without category_string
                    move_category = self._get_move_category_fallback(move)
                
                if move_category == target_category:
                    filtered.append(move)
                    
            except Exception as e:
                logger.error(f"Error filtering move {getattr(move, 'name', 'unknown')}: {e}")
                continue
        
        # Log for debugging
        logger.debug(f"Category {category} ({target_category}): {len(filtered)}/{len(moves)} moves")
        
        return filtered

    def _get_move_category_fallback(self, move):
        """Fallback method for moves without category_string property."""
        if not move:
            return "PHYSICAL"
            
        # Try different attribute names
        for attr in ['category', 'damage_type', 'move_type']:
            if hasattr(move, attr):
                value = getattr(move, attr)
                # Handle enum
                if hasattr(value, 'value'):
                    category_value = str(value.value).lower()
                elif hasattr(value, 'name'):
                    category_value = str(value.name).lower()
                elif value:
                    category_value = str(value).lower()
                else:
                    continue
                
                # Map to standardized categories
                if category_value in ['phys', 'physical', 'körperlich']:
                    return "PHYSICAL"
                elif category_value in ['mag', 'magical', 'special', 'magisch']:
                    return "MAGICAL"
                elif category_value in ['support', 'status', 'hilfe']:
                    return "STATUS"
        
        # Fallback based on move properties
        if hasattr(move, 'power') and move.power > 0:
            # Has power - determine if physical or magical
            if hasattr(move, 'type'):
                magic_types = ['feuer', 'wasser', 'pflanze', 'luft', 'energie', 'chaos', 'mystisch', 'gottheit', 'teufel']
                if any(magic_type in move.type.lower() for magic_type in magic_types):
                    return "MAGICAL"
            return "PHYSICAL"
        else:
            return "STATUS"
    
    def _get_items_for_category(self, category):
        """Get items from inventory - FIXED CATEGORIES."""
        items = []
        
        if not self.game or not hasattr(self.game, 'inventory'):
            return items
        
        inventory = self.game.inventory
        
        # Import item registry safely
        try:
            from engine.systems.items import item_registry
        except ImportError:
            logger.error("Could not import item_registry")
            return items
        
        # Updated category mapping to match actual ItemCategory enum
        category_map = {
            'HEILUNG': ['HEALING', 'MEDICINE', 'RECOVERY', 'healing', 'medicine'],
            'KAMPF': ['BATTLE', 'OFFENSIVE', 'BOOST', 'battle', 'offensive'],
            'FLEISCH': ['TAMING', 'MEAT', 'FOOD', 'taming', 'meat']
        }
        
        target_categories = category_map.get(category, [])
        
        # Get all items from inventory
        for item_id, quantity in inventory.get_all_items():
            if quantity <= 0:
                continue
                
            item = item_registry.get_item(item_id)
            if not item:
                continue
            
            # Check category with multiple methods
            item_category = None
            if hasattr(item, 'category'):
                if hasattr(item.category, 'name'):
                    item_category = item.category.name
                elif hasattr(item.category, 'value'):
                    item_category = item.category.value
                else:
                    item_category = str(item.category)
            
            # Check if category matches
            if item_category and item_category in target_categories:
                if not hasattr(item, 'use_in_battle') or item.use_in_battle:
                    effect = self._get_item_effect_description(item)
                    items.append((item_id, item.name, quantity, effect))
        
        # Sort and return
        items.sort(key=lambda x: x[1])
        return items
    
    def _get_item_effect_description(self, item):
        """Get a short description of item's effect."""
        if not item.effects:
            return "???"
        
        # Get first effect
        effect = item.effects[0]
        effect_type = effect.effect_type.name if hasattr(effect.effect_type, 'name') else str(effect.effect_type)
        
        # Format based on effect type
        if effect_type == 'HEAL_HP':
            value = effect.value
            if isinstance(value, float) and value <= 1.0:
                return f"+{int(value*100)}% HP"
            else:
                return f"+{value} HP"
        elif effect_type == 'HEAL_STATUS':
            return f"Heilt {effect.value}"
        elif effect_type == 'HEAL_ALL_STATUS':
            return "Heilt alle Status"
        elif effect_type == 'REVIVE':
            return f"Belebt mit {int(effect.value*100)}% HP"
        elif effect_type == 'BUFF_STAT':
            if isinstance(effect.value, tuple) and len(effect.value) == 2:
                stat, stages = effect.value
                return f"+{stages} {stat.upper()}"
            return "Stat-Boost"
        elif effect_type == 'TAMING_BONUS':
            return f"+{int((effect.value-1)*100)}% Zähm"
        else:
            return "Spezial"
    
    def update(self, dt):
        """Update UI animations."""
        # Update cursor blink
        self.cursor_blink = (self.cursor_blink + 1) % 30
        
        # Update message typewriter
        if self.current_message and self.message_char_index < len(self.current_message):
            self.message_char_index += 2  # 2 chars per frame for fast text
        
        # Update damage numbers
        for number in self.damage_numbers:
            number['timer'] -= 1
    
    def handle_input(self, action, battle_state=None):
        """Handle input for current menu state."""
        self.battle_state = battle_state
        
        # Call the appropriate handler
        result = None
        if self.menu_state == BattleMenuState.MAIN:
            result = self._handle_main_menu_input(action)
        elif self.menu_state == BattleMenuState.MOVE_SELECT:
            result = self._handle_move_menu_input(action)
        elif self.menu_state == BattleMenuState.ITEM_SELECT:
            result = self._handle_item_menu_input(action)
        elif self.menu_state == BattleMenuState.SWITCH_SELECT:
            result = self._handle_switch_menu_input(action)
        elif self.menu_state == BattleMenuState.TAME_MEAT:
            result = self._handle_meat_menu_input(action)
        elif self.menu_state == BattleMenuState.TAME_CONFIRM:
            result = self._handle_tame_confirm_input(action)
        elif self.menu_state == BattleMenuState.SCOUT:
            result = self._handle_scout_input(action)
        elif self.menu_state == BattleMenuState.MESSAGE:
            result = self._handle_message_input(action)
        
        # If the handler didn't return an action, check if we can generate one
        if result is None:
            # Check if we can generate an action from current state using ActionFactory
            if self.menu_state == BattleMenuState.MAIN and self.last_action_type:
                result = self.get_action_result()
        
        # If we have a result, set it as pending action
        if result:
            self._pending_action = result
        
        return result
    
    def connect_event_handlers(self, event_processor: 'EventProcessor') -> None:
        """Connect UI to EventProcessor - CRITICAL."""
        if not event_processor:
            logger.warning("No event processor provided to connect_event_handlers")
            return
            
        self.event_processor = event_processor
        
        try:
            from engine.systems.battle.event_processor import EventType
            
            # Register ALL handlers - CRITICAL!
            event_processor.register_handler(EventType.MESSAGE_SHOW, self._handle_message_event)
            event_processor.register_handler(EventType.HP_BAR_UPDATE, self._handle_hp_update_event)
            event_processor.register_handler(EventType.DAMAGE_DEALT, self._handle_damage_event)
            event_processor.register_handler(EventType.HEALING_DONE, self._handle_healing_event)
            event_processor.register_handler(EventType.STATUS_APPLIED, self._handle_status_event)
            event_processor.register_handler(EventType.STATUS_REMOVED, self._handle_status_event)
            event_processor.register_handler(EventType.STATUS_DAMAGE, self._handle_status_tick_event)
            event_processor.register_handler(EventType.MONSTER_FAINTED, self._handle_faint_event)
            event_processor.register_handler(EventType.MONSTER_SWITCH, self._handle_switch_event)
            event_processor.register_handler(EventType.TURN_START, self._handle_turn_start_event)
            event_processor.register_handler(EventType.TURN_END, self._handle_turn_end_event)
            event_processor.register_handler(EventType.BATTLE_END, self._handle_battle_end_event)
            event_processor.register_handler(EventType.ANIMATION_PLAY, self._handle_animation_event)
            event_processor.register_handler(EventType.SCREEN_FLASH, self._handle_screen_flash_event)
            event_processor.register_handler(EventType.CAMERA_SHAKE, self._handle_screen_shake_event)
            event_processor.register_handler(EventType.PHASE_CHANGE, self._handle_phase_change_event)
            
            logger.info("Successfully registered ALL event handlers with EventProcessor")
                
        except ImportError as e:
            logger.error(f"Failed to import EventType: {e}")
        except Exception as e:
            logger.error(f"Error registering event handlers: {e}")

    def apply_update(self, update: Dict[str, Any]) -> None:
        """Apply UI update from event processor."""
        try:
            # Handle both 'type' and 'update_type' for compatibility
            update_type = update.get('type') or update.get('update_type')
            
            # Get data from update or use update itself
            data = update.get('data', update)
            
            if update_type == 'hp_change' or update_type == 'hp_bar':
                target = data.get('target')
                if target:
                    self.update_hp_bar(target)
                    
            elif update_type == 'message':
                message = update.get('message')
                if message:
                    self.add_message(message)
                    
            elif update_type == 'status_change':
                target = update.get('target')
                if target:
                    # Trigger status display update - force redraw
                    logger.info(f"Status change detected for {target}")
                
            elif update_type == 'animation':
                anim_type = update.get('animation_type')
                if anim_type == 'damage':
                    self.show_damage_number(
                        update.get('target'),
                        update.get('value', 0),
                        update.get('is_critical', False)
                    )
                elif anim_type == 'screen_shake':
                    self.trigger_screen_shake(
                        update.get('intensity', 5),
                        update.get('duration', 0.3)
                    )
                    
        except Exception as e:
            logger.error(f"Failed to apply UI update: {e}")


    
    def clear_pending_action(self):
        """Clear the pending action after it has been processed."""
        self._pending_action = None
    
    def get_action_result(self):
        """IMMER BattleAction zurückgeben, NIE dict!"""
        from engine.systems.battle.turn_logic import BattleAction, ActionType
        
        # 1. Check pending action
        if hasattr(self, '_pending_action') and self._pending_action:
            action = self._pending_action
            self._pending_action = None  # CRITICAL: Reset!
            
            # Convert dict to BattleAction if needed
            if isinstance(action, dict):
                return self._dict_to_battle_action(action)
            return action
        
        # 2. Generate action from current state
        if not self.last_action_type or not self.battle_state:
            return None
        
        # 3. Create proper BattleAction based on type
        actor = self.battle_state.player_active
        if not actor:
            logger.error("No active player monster for action!")
            return None
        
        if self.last_action_type == 'attack':
            if not self.selected_move_id:
                logger.error("Attack without selected move!")
                return None
                
            # Get Move object
            from engine.systems.moves import move_registry
            move_obj = move_registry.get_move(self.selected_move_id)
            if not move_obj:
                # Try creating from name
                move_obj = move_registry.create_move_instance_by_name(self.selected_move_id)
            
            return BattleAction(
                action_type=ActionType.ATTACK,
                actor=actor,
                target=self.selected_target or self.battle_state.enemy_active,
                move=move_obj
            )
        
        elif self.last_action_type == 'item':
            return BattleAction(
                action_type=ActionType.ITEM,
                actor=actor,
                target=self.selected_target or actor,
                item_id=self.selected_item_id
            )
        
        elif self.last_action_type == 'switch':
            if self.selected_monster_index is None:
                return None
            
            switch_target = self.battle_state.player_team[self.selected_monster_index]
            return BattleAction(
                action_type=ActionType.SWITCH,
                actor=actor,
                switch_to=switch_target,
                target=switch_target  # Some code expects target
            )
        
        elif self.last_action_type == 'tame':
            return BattleAction(
                action_type=ActionType.TAME,
                actor=actor,
                target=self.battle_state.enemy_active,
                meat_bonus=self.meat_effect_active
            )
        
        elif self.last_action_type == 'flee':
            return BattleAction(
                action_type=ActionType.FLEE,
                actor=actor,
                target=actor  # Self-target for flee
            )
        
        elif self.last_action_type == 'scout':
            return BattleAction(
                action_type=ActionType.SCOUT,
                actor=actor,
                target=self.battle_state.enemy_active
            )
        
        logger.warning(f"Unknown action type: {self.last_action_type}")
        return None
    
    def _dict_to_battle_action(self, action_dict):
        """ROBUST dict to BattleAction conversion"""
        from engine.systems.battle.turn_logic import BattleAction, ActionType
        
        # Handle special cases
        if action_dict.get('action') == 'meat_selected':
            # This is internal UI state, not a battle action
            return None
        
        if action_dict.get('action') == 'message_complete':
            # UI-only event
            return None
        
        # Get action type (handle both 'action' and 'type' keys)
        action_type_str = action_dict.get('action') or action_dict.get('type')
        if not action_type_str:
            logger.error(f"No action type in dict: {action_dict}")
            return None
        
        # Convert to enum
        try:
            action_type = ActionType.from_string(action_type_str)
        except:
            logger.error(f"Invalid action type: {action_type_str}")
            return None
        
        # Get actor (required)
        actor = action_dict.get('actor') or self.battle_state.player_active
        if not actor:
            logger.error("No actor for action!")
            return None
        
        # Build BattleAction with all available data
        return BattleAction(
            action_type=action_type,
            actor=actor,
            target=action_dict.get('target'),
            move=action_dict.get('move'),
            item_id=action_dict.get('item_id'),
            switch_to=action_dict.get('switch_to'),
            meat_bonus=action_dict.get('meat_bonus', 0)
        )
    
    def process_battle_event(self, event: dict):
        """Process events from battle controller."""
        event_type = event.get('event_type')
        
        if event_type == 'MESSAGE_SHOW':
            self.show_message(event['data']['message'])
        
        elif event_type == 'HP_BAR_UPDATE':
            target = event['data']['target']
            self.update_hp_bar(target, animated=True)
        
        elif event_type == 'DAMAGE_DEALT':
            self.show_damage_number(
                event['data']['target'],
                event['data']['damage'],
                event['data']['is_critical']
            )
        
        elif event_type == 'STATUS_APPLIED':
            self.show_status_effect(
                event['data']['target'],
                event['data']['status']
            )
        
        elif event_type == 'MONSTER_FAINTED':
            self.play_faint_animation(event['data']['monster'])
        
        elif event_type == 'CRITICAL_HIT':
            self.trigger_screen_flash(128)
        
        elif event_type == 'SCREEN_SHAKE':
            self.trigger_screen_shake(event['data'].get('intensity', 5))
    
    def _handle_message_event(self, event):
        """Handle message event from EventProcessor."""
        message = event.data.get('message', '')
        if message:
            self.show_message(message)
    
    def _handle_hp_update_event(self, event):
        """Handle HP update event from EventProcessor."""
        target = event.data.get('target')
        if target:
            self.update_hp_bar(target, animated=True)
    
    def _handle_damage_event(self, event):
        """Handle damage event from EventProcessor."""
        target = event.data.get('target')
        damage = event.data.get('damage', 0)
        is_critical = event.data.get('is_critical', False)
        if target:
            self.show_damage_number(target, damage, is_critical)
    
    def _handle_status_event(self, event):
        """Handle status event from EventProcessor."""
        target = event.data.get('target')
        status = event.data.get('status')
        if target and status:
            self.show_status_effect(target, status)
    
    def _handle_healing_event(self, event):
        """Handle healing event from EventProcessor."""
        target = event.data.get('target')
        healing = event.data.get('healing', 0)
        if target:
            self.show_healing_number(target, healing)
            self.update_hp_bar(target, animated=True)
    
    def _handle_faint_event(self, event):
        """Handle monster faint event."""
        monster = event.data.get('monster')
        if monster:
            self.play_faint_animation(monster)
    
    def _handle_switch_event(self, event):
        """Handle monster switch event."""
        old_monster = event.data.get('old')
        new_monster = event.data.get('new')
        if new_monster:
            self.show_message(f"{new_monster.name if hasattr(new_monster, 'name') else 'Monster'} kommt in den Kampf!")
    
    def _handle_turn_start_event(self, event):
        """Handle turn start event."""
        turn_number = event.data.get('turn', 0)
        logger.debug(f"Turn {turn_number} started")
    
    def _handle_turn_end_event(self, event):
        """Handle turn end event."""
        # Reset UI for next turn
        if self.menu_state == BattleMenuState.WAITING:
            self.menu_state = BattleMenuState.MAIN
    
    def _handle_battle_end_event(self, event):
        """Handle battle end event."""
        result = event.data.get('result')
        if result:
            self.show_message(f"Kampf beendet: {result}")
    
    def _handle_animation_event(self, event):
        """Handle animation event from EventProcessor."""
        anim_type = event.data.get('animation_type')
        target = event.data.get('target')
        if anim_type and target:
            logger.debug(f"Playing animation {anim_type} for {target}")
    
    def _handle_screen_flash_event(self, event):
        """Handle screen flash event."""
        intensity = event.data.get('intensity', 128)
        self.trigger_screen_flash(intensity)
    
    def _handle_screen_shake_event(self, event):
        """Handle screen shake event."""
        intensity = event.data.get('intensity', 5)
        duration = event.data.get('duration', 0.3)
        self.trigger_screen_shake(intensity, duration)
    
    def _handle_status_tick_event(self, event):
        """Handle status damage tick event."""
        target = event.data.get('target')
        damage = event.data.get('damage', 0)
        status = event.data.get('status')
        if target:
            self.show_damage_number(target, damage, is_status=True)
            self.show_message(f"{target.name} nimmt {damage} {status}-Schaden!")
    
    def _handle_phase_change_event(self, event):
        """Handle battle phase changes."""
        if hasattr(event, 'data'):
            phase = event.data.get('phase')
            # Update UI state based on phase
            logger.debug(f"Battle phase changed to: {phase}")
    
    def _get_monster_position(self, monster):
        """Get screen position of monster for effects."""
        # Check if monster is player or enemy
        if self.battle_state:
            if monster == self.battle_state.player_active:
                return (240, 90)  # Player side
            elif monster == self.battle_state.enemy_active:
                return (80, 30)  # Enemy side
        return (160, 60)  # Default center
    
    def _update_status_display(self, data):
        """Update status condition display."""
        # Update visual status indicators
        target = data.get('target')
        status = data.get('status')
        if target and status:
            logger.debug(f"Status display updated for {target.name}: {status}")
    
    def _handle_phase_change(self, data):
        """Handle battle phase changes."""
        # Update menu state based on phase
        phase = data.get('phase')
        if phase:
            logger.debug(f"Handling phase change: {phase}")
    
    def update_hp_bar(self, target, animated=True):
        """Update HP bar for a monster with animation."""
        if not target:
            return
        
        # Store HP animation data
        if animated:
            self.hp_animations[target.name] = {
                'target': target,
                'start_hp': getattr(target, 'display_hp', target.current_hp),
                'end_hp': target.current_hp,
                'max_hp': target.max_hp,
                'timer': 0.0,
                'duration': 0.5
            }
        else:
            # Immediate update
            target.display_hp = target.current_hp
    
    def show_damage_number(self, target, damage, is_critical=False, is_status=False):
        """Show floating damage number."""
        if not target:
            return
        
        # Determine position based on target
        if hasattr(target, 'is_player_side') and target.is_player_side:
            x, y = 240, 90  # Player side
        else:
            x, y = 80, 30   # Enemy side
        
        self.add_damage_number(
            damage, x, y, 
            is_critical=is_critical,
            is_effective=damage > 50,  # Simple effectiveness check
            is_status=is_status
        )
    
    def show_status_effect(self, target, status):
        """Show status effect application with DQM status messages."""
        if not target or not status:
            return
        
        # DQM Status Messages (German Ruhrpott style)
        status_messages = {
            'burn': f"{target.name} brennt wie Zunder!",
            'poison': f"{target.name} ist vergiftet!",
            'paralysis': f"{target.name} ist gelähmt!",
            'sleep': f"{target.name} schläft tief und fest!",
            'freeze': f"{target.name} ist eingefroren!",
            'confusion': f"{target.name} ist total verwirrt!",
            'dazzle': f"{target.name} ist geblendet!",
            'curse': f"{target.name} ist verflucht!",
            'berserk': f"{target.name} rastet aus!",
            'bounce': f"{target.name} reflektiert Magie!",
            'silence': f"{target.name} ist stumm!",
            'blind': f"{target.name} kann nichts sehen!",
            'charm': f"{target.name} ist verzaubert!",
            'fear': f"{target.name} hat Angst!",
            'zombie': f"{target.name} ist ein Zombie!",
            'skip_turn': f"{target.name} kann nicht handeln!",
            'cured_poison': f"{target.name} ist nicht mehr vergiftet!",
            'cured_burn': f"{target.name} brennt nicht mehr!",
            'cured_sleep': f"{target.name} ist aufgewacht!",
            'cured_paralysis': f"{target.name} ist nicht mehr gelähmt!",
            'cured_freeze': f"{target.name} ist aufgetaut!",
            'cured_confusion': f"{target.name} ist nicht mehr verwirrt!"
        }
        
        message = status_messages.get(status, f"{target.name} wurde {status}!")
        self.show_message(message)
    
    def play_faint_animation(self, monster):
        """Play faint animation for a monster."""
        if not monster:
            return
        
        # Trigger screen flash and shake
        self.trigger_screen_flash(64)
        self.trigger_screen_shake(3, 0.3)
        
        # Show faint message
        self.show_message(f"{monster.name} ist ohnmächtig geworden!")
    
    def reset_to_main_menu(self):
        """Reset UI to main menu after action."""
        self.menu_state = BattleMenuState.MAIN
        self.cursor_row = 0
        self.cursor_col = 0
        self.selected_move_id = None
        self.selected_item_id = None
        self.selected_target = None
        self.selected_monster_index = None
        self.selected_meat_id = None
        self.last_action_type = None
        self.message_queue.clear()
        self.current_message = ""
        self.message_char_index = 0
    
    def is_waiting_for_input(self) -> bool:
        """Check if UI is ready for player input."""
        # UI is waiting for input if it's in any interactive state
        # and not showing messages or animations
        return (
            self.menu_state in [BattleMenuState.MAIN, BattleMenuState.MOVE_SELECT, 
                               BattleMenuState.ITEM_SELECT, BattleMenuState.SWITCH_SELECT,
                               BattleMenuState.TAME_MEAT, BattleMenuState.TAME_CONFIRM] and
            len(self.message_queue) == 0 and
            not self.current_message and
            self.screen_flash <= 0
        )
    
    def _handle_main_menu_input(self, action):
        """Handle main menu navigation."""
        if action == 'up':
            self.cursor_row = max(0, self.cursor_row - 1)
        elif action == 'down':
            self.cursor_row = min(2, self.cursor_row + 1)
        elif action == 'left':
            self.cursor_col = max(0, self.cursor_col - 1)
        elif action == 'right':
            self.cursor_col = min(1, self.cursor_col + 1)
        elif action == 'confirm':
            option = self.main_menu_layout[self.cursor_row][self.cursor_col]
            
            logger.debug(f"Menu option selected: {option}")
            
            if option == "ATTACKE":
                self.menu_state = BattleMenuState.MOVE_SELECT
                self.current_category = 0
                self.move_cursor = 0
                self.last_action_type = 'attack'
                # Lade Moves vom aktiven Monster
                if self.battle_state and self.battle_state.player_active:
                    self.moves_in_category = self._get_moves_by_category(
                        self.battle_state.player_active.moves if hasattr(self.battle_state.player_active, 'moves') else [],
                        self.move_categories[self.current_category]
                    )
                # Return None - Action wird in _handle_move_menu_input generiert
                return None
            elif option == "ITEM":
                self.menu_state = BattleMenuState.ITEM_SELECT
                self.current_item_category = 0
                self.item_cursor = 0
                self.last_action_type = 'item'
                # Return None - Action wird in _handle_item_menu_input generiert
                return None
            elif option == "WECHSEL":
                self.menu_state = BattleMenuState.SWITCH_SELECT
                self.cursor_pos = 0
                self.last_action_type = 'switch'
                # Return None - Action wird in _handle_switch_menu_input generiert
                return None
            elif option == "ZÄHMEN":
                self.menu_state = BattleMenuState.TAME_MEAT
                self.cursor_pos = 0
                self.last_action_type = 'tame'
                # Return None - Action wird in _handle_meat_menu_input generiert
                return None
            elif option == "SPÄHEN":
                self.menu_state = BattleMenuState.SCOUT
                self.last_action_type = 'scout'
                return None  # Action wird in get_action_result() generiert
            elif option == "FLUCHT":
                self.last_action_type = 'flee'
                return None  # Action wird in get_action_result() generiert
        elif action == 'back':
            # Im Hauptmenü gibt es kein Zurück
            pass
        
        # Reset action tracking when navigating
        if action in ['up', 'down', 'left', 'right']:
            self.last_action_type = None
        
        return None
    
    def _handle_move_menu_input(self, action):
        """Handle move selection input."""
        if action == 'left':
            self.current_category = max(0, self.current_category - 1)
            self.move_cursor = 0
            # Update moves for new category
            if self.battle_state and self.battle_state.player_active:
                self.moves_in_category = self._get_moves_by_category(
                    getattr(self.battle_state.player_active, 'moves', []),
                    self.move_categories[self.current_category]
                )
        elif action == 'right':
            self.current_category = min(len(self.move_categories) - 1, self.current_category + 1)
            self.move_cursor = 0
            # Update moves for new category
            if self.battle_state and self.battle_state.player_active:
                self.moves_in_category = self._get_moves_by_category(
                    getattr(self.battle_state.player_active, 'moves', []),
                    self.move_categories[self.current_category]
                )
        elif action == 'up':
            self.move_cursor = max(0, self.move_cursor - 1)
        elif action == 'down':
            # Get moves in current category
            if self.battle_state and self.battle_state.player_active:
                moves = self._get_moves_by_category(
                    getattr(self.battle_state.player_active, 'moves', []),
                    self.move_categories[self.current_category]
                )
                self.move_cursor = min(len(moves) - 1, self.move_cursor + 1)
        elif action == 'confirm':
            # Execute selected move
            if self.battle_state and self.battle_state.player_active:
                moves = self._get_moves_by_category(
                    getattr(self.battle_state.player_active, 'moves', []),
                    self.move_categories[self.current_category]
                )
                if moves and self.move_cursor < len(moves):
                    selected_move = moves[self.move_cursor]
                    self.selected_move_id = getattr(selected_move, 'id', selected_move.name if hasattr(selected_move, 'name') else str(selected_move))
                    self.selected_target = self.battle_state.enemy_active
                    self.menu_state = BattleMenuState.MAIN  # Zurück zum Hauptmenü
                    logger.debug(f"Move selected: {selected_move.name if hasattr(selected_move, 'name') else selected_move}")
                    
                    # Action wird in get_action_result() generiert
                    return None
        elif action == 'back':
            self.menu_state = BattleMenuState.MAIN
            return {'action': 'menu_change', 'new_state': 'main'}
        
        return None
    
    def _handle_scout_input(self, action):
        """Handle scout display input."""
        if action in ['confirm', 'back']:
            self.selected_target = self.battle_state.enemy_active if self.battle_state else None
            self.menu_state = BattleMenuState.MAIN
            return {'action': 'menu_change', 'new_state': 'main'}
        return None
    
    def _handle_meat_menu_input(self, action):
        """Handle meat selection for taming."""
        if action == 'up':
            self.cursor_pos = max(0, self.cursor_pos - 1)
        elif action == 'down':
            self.cursor_pos = min(len(self.meat_types) - 1, self.cursor_pos + 1)
        elif action == 'confirm':
            # Select meat type
            meat_keys = list(self.meat_types.keys())
            if self.cursor_pos < len(meat_keys):
                self.selected_meat = meat_keys[self.cursor_pos]
                self.selected_meat_id = self.selected_meat
                self.meat_effect_active = self.meat_types[self.selected_meat]['bonus']
                
                # Move to taming confirmation
                self.menu_state = BattleMenuState.TAME_CONFIRM
                self.cursor_pos = 0  # Reset cursor for confirm menu
                return {'action': 'meat_selected', 'meat': self.selected_meat, 'bonus': self.meat_effect_active}
        elif action == 'back':
            self.menu_state = BattleMenuState.MAIN
            return {'action': 'menu_change', 'new_state': 'main'}
        
        return None
    
    def _handle_tame_confirm_input(self, action):
        """Handle taming confirmation."""
        if action == 'up' or action == 'down':
            # Toggle between "Zähmen versuchen" and "Abbrechen"
            self.cursor_pos = 1 - self.cursor_pos  # Toggle between 0 and 1
        elif action == 'confirm':
            if self.cursor_pos == 0:  # "Zähmen versuchen"
                # Execute taming attempt
                self.selected_target = self.battle_state.enemy_active if self.battle_state else None
                self.menu_state = BattleMenuState.MAIN
                
                # Action wird in get_action_result() generiert
                return None
            else:  # "Abbrechen"
                self.menu_state = BattleMenuState.MAIN
                return {'action': 'cancel_taming'}
        elif action == 'back':
            # Go back to meat selection
            self.menu_state = BattleMenuState.TAME_MEAT
            self.cursor_pos = 0
            return {'action': 'menu_change', 'new_state': 'tame_meat'}
        
        return None
    
    def _handle_item_menu_input(self, action):
        """Handle item selection input."""
        if action == 'left':
            self.current_item_category = max(0, self.current_item_category - 1)
            self.item_cursor = 0
            # Update items for new category
            self.items_in_category = self._get_items_for_category(self.item_categories[self.current_item_category])
        elif action == 'right':
            self.current_item_category = min(len(self.item_categories) - 1, self.current_item_category + 1)
            self.item_cursor = 0
            # Update items for new category
            self.items_in_category = self._get_items_for_category(self.item_categories[self.current_item_category])
        elif action == 'up':
            self.item_cursor = max(0, self.item_cursor - 1)
        elif action == 'down':
            # Get actual item count for current category
            items = self._get_items_for_category(self.item_categories[self.current_item_category])
            if items:
                self.item_cursor = min(len(items) - 1, self.item_cursor + 1)
        elif action == 'confirm':
            # Use selected item
            items = self._get_items_for_category(self.item_categories[self.current_item_category])
            if items and self.item_cursor < len(items):
                item_id, item_name, count, effect = items[self.item_cursor]
                if count > 0:
                    self.selected_item_id = item_id
                    self.selected_target = self.battle_state.player_active if self.battle_state else None
                    self.menu_state = BattleMenuState.MAIN
                    
                    # Action wird in get_action_result() generiert
                    return None
                else:
                    self.show_message(f"Kein {item_name} mehr vorhanden!")
            else:
                self.show_message("Keine Items in dieser Kategorie!")
        elif action == 'back':
            self.menu_state = BattleMenuState.MAIN
            return {'action': 'menu_change', 'new_state': 'main'}
        
        return None
    
    def _handle_switch_menu_input(self, action):
        """Handle team switch input."""
        if action == 'up':
            self.cursor_pos = max(0, self.cursor_pos - 1)
        elif action == 'down':
            # Get team size
            if self.battle_state and self.battle_state.player_team:
                team_size = len(self.battle_state.player_team)
                self.cursor_pos = min(team_size - 1, self.cursor_pos + 1)
        elif action == 'confirm':
            # Switch to selected monster
            if self.battle_state and self.battle_state.player_team:
                if self.cursor_pos < len(self.battle_state.player_team):
                    selected_monster = self.battle_state.player_team[self.cursor_pos]
                    if selected_monster and not selected_monster.is_fainted:
                        self.selected_monster_index = self.cursor_pos
                        self.menu_state = BattleMenuState.MAIN
                        
                        # Action wird in get_action_result() generiert
                        return None
                    else:
                        self.show_message("Dieses Monster kann nicht kämpfen!")
        elif action == 'back':
            self.menu_state = BattleMenuState.MAIN
            return {'action': 'menu_change', 'new_state': 'main'}
        
        return None
    
    def _handle_message_input(self, action):
        """Handle message display input."""
        if action in ['confirm', 'back']:
            # Check if message is fully displayed
            if self.message_char_index >= len(self.current_message):
                # Move to next message or return to menu
                if self.message_queue:
                    self._next_message()
                else:
                    self.menu_state = BattleMenuState.MAIN
                    self.current_message = ""
                    return {'action': 'message_complete'}
            else:
                # Speed up message display
                self.message_char_index = len(self.current_message)
        
        return None
    
    def add_damage_number(self, value, x, y, is_critical=False, is_effective=False, is_heal=False, is_status=False):
        """Add a floating damage number."""
        self.damage_numbers.append({
            'value': value,
            'x': x,
            'y': y,
            'velocity': 2.0,
            'timer': 30,
            'is_critical': is_critical,
            'is_effective': is_effective,
            'is_heal': is_heal,
            'is_status': is_status
        })
    
    def show_message(self, message):
        """Show a battle message."""
        self.current_message = message
        self.message_char_index = 0
        self.menu_state = BattleMenuState.MESSAGE
    
    def trigger_screen_flash(self, intensity=128):
        """Trigger a screen flash effect."""
        self.screen_flash = intensity
    
    def trigger_screen_shake(self, intensity=5, duration=0.3):
        """Trigger screen shake (handled by scene)."""
        self.screen_shake = intensity
    
    # Legacy compatibility methods removed - use new battle system instead
    
    def add_message(self, message: str, wait: bool = True):
        """Add a message to the display queue (compatibility)."""
        self.message_queue.append(message)
        if not self.current_message and wait:
            self._next_message()
    
    def _next_message(self):
        """Show next message in queue."""
        if self.message_queue:
            self.current_message = self.message_queue.pop(0)
            self.message_char_index = 0
            self.message_timer = 2.0  # 2 seconds display time
        else:
            self.current_message = ""
    

    
    def init_battle(self, player_team, enemy_team):
        """Initialize battle UI with teams."""
        try:
            # Store team references
            self.player_team = player_team
            self.enemy_team = enemy_team
            
            # CRITICAL FIX: Initialize display_hp for all monsters
            for monster in player_team + enemy_team:
                if hasattr(monster, 'current_hp') and not hasattr(monster, 'display_hp'):
                    monster.display_hp = monster.current_hp
            
            # CRITICAL FIX: Clear sprite cache for new battle
            self.sprite_cache.clear()
            
            # Reset UI state
            self.reset_to_main_menu()
            
            # Clear any previous state - CRITICAL!
            self.message_queue.clear()
            self.damage_numbers.clear()
            self._pending_action = None
            
            # Initialize message queue if not exists
            if not hasattr(self, 'message_queue'):
                self.message_queue = []
            
            logger.info(f"Battle UI initialized with {len(player_team)} player and {len(enemy_team)} enemy monsters")
            
        except Exception as e:
            logger.error(f"Error initializing battle UI: {e}")

    def init_demo_inventory(self):
        """Initialize inventory with demo items for testing."""
        if self.game and hasattr(self.game, 'inventory'):
            inventory = self.game.inventory
            
            # Add some demo items
            inventory.add_item('trank', 5)  # Basic healing potions
            inventory.add_item('super_trank', 2)  # Super potions
            inventory.add_item('heilmittel', 3)  # Status cure
            inventory.add_item('fleisch', 2)  # Basic meat for taming
            
            logger.info("Demo inventory initialized with test items")
    
    def show_healing_number(self, target, healing):
        """Show healing number animation."""
        try:
            # Create healing number effect
            healing_number = DamageNumber(
                str(healing),
                target.position,
                color=(0, 255, 0),  # Green for healing
                duration=1.0
            )
            self.damage_numbers.append(healing_number)
            logger.debug(f"Showing healing number: {healing} for {target.name}")
        except Exception as e:
            logger.error(f"Error showing healing number: {e}")
    
    def play_appear_animation(self, monster):
        """Play monster appear animation."""
        try:
            # Simple appear animation - could be enhanced later
            logger.debug(f"Playing appear animation for {monster.name}")
            # For now, just show a message
            self.add_message(f"{monster.name} erscheint!")
        except Exception as e:
            logger.error(f"Error playing appear animation: {e}")

# Export classes for compatibility
__all__ = ['BattleUI', 'BattleMenuState', 'BattleSprite', 'DamageNumber', 'SkillMenu', 'ItemMenu', 'EnhancedMainBattleMenu']
