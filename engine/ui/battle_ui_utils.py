"""
Battle UI Utilities - Zentrale Hilfsfunktionen für alle Battle UI-Komponenten.
Konsolidiert doppelte Funktionalitäten und stellt gemeinsame Services bereit.
"""

import pygame
import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass

from engine.core.config import Colors

logger = logging.getLogger(__name__)


@dataclass
class TypeInfo:
    """Type information with color and effectiveness data."""
    name: str
    color: Tuple[int, int, int]
    effectiveness: float = 1.0


class BattleUIFontManager:
    """Zentrale Font-Verwaltung für alle Battle UI-Komponenten."""
    
    _instance = None
    _fonts = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def get_font(self, size: int, bold: bool = False) -> pygame.font.Font:
        """Get font with lazy initialization and better pixel rendering."""
        font_key = f"{size}_{bold}"
        if font_key not in self._fonts:
            try:
                # Ensure pygame is initialized
                if not pygame.get_init():
                    pygame.init()
                
                # Simple, robust approach - use monospace with bold support
                try:
                    self._fonts[font_key] = pygame.font.SysFont("monospace", size, bold=bold)
                except pygame.error:
                    # Fallback to default font
                    if bold:
                        # For bold, use a slightly larger size to simulate boldness
                        self._fonts[font_key] = pygame.font.Font(None, int(size * 1.1))
                    else:
                        self._fonts[font_key] = pygame.font.Font(None, size)
                    
            except pygame.error:
                # Ultimate fallback
                self._fonts[font_key] = pygame.font.Font(None, size)
        
        return self._fonts[font_key]
    
    @property
    def tiny(self) -> pygame.font.Font:
        """Tiny font for very small text (8px)"""
        return self.get_font(8)
    
    @property
    def small(self) -> pygame.font.Font:
        """Small font for labels and small text (12px)"""
        return self.get_font(12)
    
    @property
    def normal(self) -> pygame.font.Font:
        """Normal font for regular text (16px)"""
        return self.get_font(16)
    
    @property
    def large(self) -> pygame.font.Font:
        """Large font for important text (20px)"""
        return self.get_font(20)
    
    @property
    def huge(self) -> pygame.font.Font:
        """Huge font for titles and important elements (24px)"""
        return self.get_font(24)
    
    @property
    def move_name(self) -> pygame.font.Font:
        """Special font for move names - optimized size (14px bold)"""
        return self.get_font(14, bold=True)
    
    @property
    def monster_name(self) -> pygame.font.Font:
        """Special font for monster names - large and bold (20px bold)"""
        return self.get_font(20, bold=True)
    
    @property
    def menu_title(self) -> pygame.font.Font:
        """Special font for menu titles - huge and bold (22px bold)"""
        return self.get_font(22, bold=True)
    
    def get_pixel_font(self, size: int) -> pygame.font.Font:
        """Get a pixel-perfect font for retro games."""
        font_key = f"pixel_{size}"
        if font_key not in self._fonts:
            try:
                # Use default font for pixel-perfect look
                self._fonts[font_key] = pygame.font.Font(None, size)
            except pygame.error:
                self._fonts[font_key] = pygame.font.SysFont("monospace", size)
        return self._fonts[font_key]


class BattleUITypeManager:
    """Zentrale Type-Verwaltung für alle Battle UI-Komponenten."""
    
    _instance = None
    _type_colors = {}
    _type_chart = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self._init_type_colors()
    
    def _init_type_colors(self):
        """Initialize type colors."""
        self._type_colors = {
            'Feuer': (255, 100, 50),
            'Wasser': (50, 150, 255),
            'Pflanze': (100, 255, 100),
            'Erde': (200, 150, 100),
            'Luft': (150, 200, 255),
            'Energie': (255, 255, 100),
            'Bestie': (180, 100, 50),
            'Chaos': (150, 50, 200),
            'Seuche': (150, 50, 150),
            'Mystik': (255, 100, 200),
            'Gottheit': (255, 255, 200),
            'Teufel': (100, 0, 100),
            'Normal': (150, 150, 150)
        }
    
    def get_type_color(self, type_name: str) -> Tuple[int, int, int]:
        """Get color for a type."""
        return self._type_colors.get(type_name, (100, 100, 100))
    
    def get_type_effectiveness(self, attacker_type: str, defender_types: List[str]) -> float:
        """Get type effectiveness using TypeChart."""
        try:
            if self._type_chart is None:
                from engine.systems.types import TypeChart
                self._type_chart = TypeChart()
            
            if not defender_types:
                return 1.0
            
            # Calculate combined effectiveness for multiple types
            total_effectiveness = 1.0
            for defender_type in defender_types:
                effectiveness = self._type_chart.get_effectiveness(attacker_type, defender_type)
                total_effectiveness *= effectiveness
            
            return total_effectiveness
            
        except Exception as e:
            logger.error(f"Error loading type effectiveness: {e}")
            return 1.0
    
    def calculate_weaknesses_and_resistances(self, monster_types: List[str]) -> Tuple[List[str], List[str]]:
        """Calculate weaknesses and resistances for monster types."""
        try:
            if self._type_chart is None:
                from engine.systems.types import TypeChart
                self._type_chart = TypeChart()
            
            weaknesses = set()
            resistances = set()
            
            # Get all available types
            all_types = self._type_chart.get_all_types()
            
            for monster_type in monster_types:
                for other_type in all_types:
                    effectiveness = self._type_chart.get_effectiveness(other_type, monster_type)
                    if effectiveness > 1.0:
                        weaknesses.add(other_type)
                    elif effectiveness < 1.0:
                        resistances.add(other_type)
            
            # Remove resistances that are also weaknesses
            resistances = resistances - weaknesses
            
            return list(weaknesses), list(resistances)
            
        except Exception as e:
            logger.error(f"Error calculating type effectiveness: {e}")
            return [], []
    
    def get_type_info(self, type_name: str, effectiveness: float = 1.0) -> TypeInfo:
        """Get complete type information."""
        return TypeInfo(
            name=type_name,
            color=self.get_type_color(type_name),
            effectiveness=effectiveness
        )


class BattleUISpriteManager:
    """Zentrale Sprite-Verwaltung für alle Battle UI-Komponenten."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def get_monster_sprite(self, monster, target_size: Tuple[int, int] = (56, 56), 
                          is_player_side: bool = True) -> pygame.Surface:
        """Get monster sprite with fallback."""
        try:
            from engine.core.resources import resources
            
            # Determine monster ID
            monster_id = self._get_monster_sprite_id(monster)
            
            # Load sprite via ResourceManager
            sprite_surface = resources.load_monster_sprite(
                monster_id=monster_id,
                target_size=target_size,
                is_player_side=is_player_side
            )
            
            return sprite_surface
            
        except Exception as e:
            logger.error(f"Error loading monster sprite: {e}")
            # Return fallback sprite
            return self._create_fallback_sprite(monster, target_size)
    
    def _get_monster_sprite_id(self, monster) -> int:
        """Determine sprite ID for a monster."""
        try:
            # Priority 1: Species ID
            if hasattr(monster, 'species') and hasattr(monster.species, 'id'):
                return monster.species.id
            
            # Priority 2: Monster ID directly
            if hasattr(monster, 'id'):
                return monster.id
            
            # Priority 3: Monster Name for lookup
            if hasattr(monster, 'name'):
                from engine.core.resources import resources
                monsters_data = resources.load_json("monsters.json")
                for m in monsters_data:
                    if m.get('name', '').lower() == monster.name.lower():
                        return m.get('id', 1)
            
            # Fallback: Default ID
            return 1
            
        except Exception as e:
            print(f"Fehler beim Bestimmen der Monster-Sprite-ID: {e}")
            return 1
    
    def _create_fallback_sprite(self, monster, target_size: Tuple[int, int]) -> pygame.Surface:
        """Create fallback sprite when loading fails."""
        sprite = pygame.Surface(target_size)
        
        # Determine color based on monster type
        if hasattr(monster, 'types') and monster.types:
            type_manager = BattleUITypeManager()
            color = type_manager.get_type_color(monster.types[0])
        else:
            color = (100, 100, 100)
        
        # Draw colored rectangle
        sprite.fill(color)
        pygame.draw.rect(sprite, (255, 255, 255), sprite.get_rect(), 2)
        
        return sprite


class BattleUIColorManager:
    """Zentrale Color-Verwaltung für alle Battle UI-Komponenten."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self._init_colors()
    
    def _init_colors(self):
        """Initialize color palette."""
        self.colors = {
            'bg_dark': (20, 20, 30),
            'bg_light': (40, 40, 60),
            'border': (100, 100, 150),
            'border_selected': (255, 200, 100),
            'text_white': (255, 255, 255),
            'text_gray': (150, 150, 150),
            'text_yellow': (255, 255, 100),
            'text_green': (100, 255, 100),
            'text_red': (255, 100, 100),
            'text_blue': (100, 150, 255),
            'hp_high': (100, 255, 100),
            'hp_med': (255, 255, 100),
            'hp_low': (255, 100, 100),
            'mp_blue': (100, 150, 255),
            'victory': (255, 215, 0),
            'exp': (100, 255, 100),
            'money': (255, 255, 100),
            'item': (150, 150, 255)
        }
    
    def get_color(self, color_name: str) -> Tuple[int, int, int]:
        """Get color by name."""
        return self.colors.get(color_name, (255, 255, 255))
    
    def get_hp_color(self, ratio: float) -> Tuple[int, int, int]:
        """Get HP bar color based on ratio."""
        if ratio > 0.5:
            return self.get_color('hp_high')
        elif ratio > 0.25:
            return self.get_color('hp_med')
        else:
            return self.get_color('hp_low')


class BattleUITextUtils:
    """Text utilities for Battle UI components."""
    
    @staticmethod
    def wrap_text(text: str, max_width: int, font: pygame.font.Font) -> List[str]:
        """Wrap text to fit within max_width."""
        if not text or not text.strip():
            return []
            
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            if font.size(test_line)[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    @staticmethod
    def draw_text_with_shadow(surface: pygame.Surface, text: str, font: pygame.font.Font, 
                            color: Tuple[int, int, int], pos: Tuple[int, int], 
                            shadow_color: Tuple[int, int, int] = (0, 0, 0)):
        """Draw text with shadow effect."""
        # Draw shadow
        shadow_surface = font.render(text, True, shadow_color)
        surface.blit(shadow_surface, (pos[0] + 1, pos[1] + 1))
        
        # Draw main text
        text_surface = font.render(text, True, color)
        surface.blit(text_surface, pos)


# Convenience instances
fonts = BattleUIFontManager()
types = BattleUITypeManager()
sprites = BattleUISpriteManager()
colors = BattleUIColorManager()
text_utils = BattleUITextUtils()
