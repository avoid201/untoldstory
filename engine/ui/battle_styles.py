"""
Battle UI Style Configuration for Untold Story.
CSS-like styling system for battle interface elements.
"""

from typing import Dict, Tuple, Any
from dataclasses import dataclass
from engine.core.config import Colors


@dataclass
class BattleStyle:
    """Style configuration for battle UI elements."""
    
    # Colors
    background_color: Tuple[int, int, int] = Colors.UI_BG
    border_color: Tuple[int, int, int] = Colors.UI_BORDER
    text_color: Tuple[int, int, int] = Colors.WHITE
    selected_color: Tuple[int, int, int] = Colors.UI_SELECTED
    unselected_color: Tuple[int, int, int] = Colors.UI_UNSELECTED
    disabled_color: Tuple[int, int, int] = Colors.UI_DISABLED
    
    # HP Bar Colors
    hp_high_color: Tuple[int, int, int] = Colors.HP_HIGH
    hp_medium_color: Tuple[int, int, int] = Colors.HP_MED
    hp_low_color: Tuple[int, int, int] = Colors.HP_LOW
    
    # PP Bar Colors
    pp_color: Tuple[int, int, int] = Colors.LIGHT_BLUE
    pp_background_color: Tuple[int, int, int] = (50, 50, 50)
    
    # Status Colors
    status_burn_color: Tuple[int, int, int] = Colors.STATUS_BURN
    status_freeze_color: Tuple[int, int, int] = Colors.STATUS_FREEZE
    status_paralysis_color: Tuple[int, int, int] = Colors.STATUS_PARALYSIS
    status_poison_color: Tuple[int, int, int] = Colors.STATUS_POISON
    status_sleep_color: Tuple[int, int, int] = Colors.STATUS_SLEEP
    status_confusion_color: Tuple[int, int, int] = Colors.STATUS_CONFUSION
    
    # Move Type Colors
    type_colors: Dict[str, Tuple[int, int, int]] = None
    
    # Dimensions
    panel_width: int = 120
    panel_height: int = 60
    menu_width: int = 200
    menu_height: int = 70
    move_selector_width: int = 140
    move_selector_height: int = 80
    target_selector_width: int = 140
    target_selector_height: int = 80
    log_width: int = 300
    log_height: int = 100
    
    # Spacing
    padding: int = 5
    margin: int = 10
    line_height: int = 14
    item_spacing: int = 15
    
    # Borders
    border_width: int = 2
    corner_radius: int = 0
    
    # Fonts
    title_font_size: int = 16
    normal_font_size: int = 14
    small_font_size: int = 12
    tiny_font_size: int = 10
    
    # Animation
    animation_speed: float = 2.0
    fade_duration: float = 0.3
    shake_intensity: int = 5
    shake_duration: float = 0.3
    flash_duration: float = 0.5
    
    def __post_init__(self):
        """Initialize default type colors if not provided."""
        if self.type_colors is None:
            self.type_colors = {
                'normal': (150, 150, 150),
                'fire': (255, 100, 50),
                'water': (50, 100, 255),
                'grass': (100, 255, 100),
                'electric': (255, 255, 100),
                'ice': (150, 200, 255),
                'fighting': (200, 100, 100),
                'poison': (200, 100, 200),
                'ground': (200, 150, 100),
                'flying': (150, 200, 255),
                'psychic': (255, 100, 200),
                'bug': (150, 200, 100)
            }


# Predefined style themes
class BattleThemes:
    """Predefined battle UI themes."""
    
    @staticmethod
    def default() -> BattleStyle:
        """Default battle theme."""
        return BattleStyle()
    
    @staticmethod
    def dark() -> BattleStyle:
        """Dark theme with high contrast."""
        return BattleStyle(
            background_color=(10, 10, 15),
            border_color=(80, 80, 100),
            text_color=(220, 220, 220),
            selected_color=(255, 255, 255),
            unselected_color=(120, 120, 140),
            disabled_color=(60, 60, 80)
        )
    
    @staticmethod
    def light() -> BattleStyle:
        """Light theme for bright environments."""
        return BattleStyle(
            background_color=(240, 240, 245),
            border_color=(180, 180, 200),
            text_color=(30, 30, 40),
            selected_color=(0, 0, 0),
            unselected_color=(100, 100, 120),
            disabled_color=(200, 200, 210)
        )
    
    @staticmethod
    def retro() -> BattleStyle:
        """Retro gaming theme."""
        return BattleStyle(
            background_color=(0, 0, 0),
            border_color=(0, 255, 0),
            text_color=(0, 255, 0),
            selected_color=(255, 255, 0),
            unselected_color=(0, 200, 0),
            disabled_color=(0, 100, 0),
            type_colors={
                'normal': (255, 255, 255),
                'fire': (255, 0, 0),
                'water': (0, 0, 255),
                'grass': (0, 255, 0),
                'electric': (255, 255, 0),
                'ice': (0, 255, 255),
                'fighting': (255, 128, 0),
                'poison': (255, 0, 255),
                'ground': (128, 64, 0),
                'flying': (128, 128, 255),
                'psychic': (255, 128, 255),
                'bug': (128, 255, 0)
            }
        )
    
    @staticmethod
    def modern() -> BattleStyle:
        """Modern flat design theme."""
        return BattleStyle(
            background_color=(45, 45, 55),
            border_color=(70, 70, 90),
            text_color=(255, 255, 255),
            selected_color=(100, 150, 255),
            unselected_color=(150, 150, 170),
            disabled_color=(80, 80, 100),
            corner_radius=8,
            padding=8,
            margin=12
        )


# Style utilities
class StyleUtils:
    """Utility functions for battle UI styling."""
    
    @staticmethod
    def get_hp_color(style: BattleStyle, hp_percent: float) -> Tuple[int, int, int]:
        """Get HP bar color based on percentage and style."""
        if hp_percent > 0.5:
            return style.hp_high_color
        elif hp_percent > 0.25:
            return style.hp_medium_color
        else:
            return style.hp_low_color
    
    @staticmethod
    def get_status_color(style: BattleStyle, status: str) -> Tuple[int, int, int]:
        """Get status condition color based on style."""
        status_colors = {
            'burn': style.status_burn_color,
            'freeze': style.status_freeze_color,
            'paralysis': style.status_paralysis_color,
            'poison': style.status_poison_color,
            'sleep': style.status_sleep_color,
            'confusion': style.status_confusion_color
        }
        return status_colors.get(status.lower(), style.text_color)
    
    @staticmethod
    def get_type_color(style: BattleStyle, move_type: str) -> Tuple[int, int, int]:
        """Get move type color based on style."""
        return style.type_colors.get(move_type.lower(), style.text_color)
    
    @staticmethod
    def apply_style_variations(base_style: BattleStyle, variations: Dict[str, Any]) -> BattleStyle:
        """Apply style variations to a base style."""
        new_style = BattleStyle()
        
        # Copy base style
        for field in base_style.__dataclass_fields__:
            setattr(new_style, field, getattr(base_style, field))
        
        # Apply variations
        for key, value in variations.items():
            if hasattr(new_style, key):
                setattr(new_style, key, value)
        
        return new_style


# Global style instance
current_battle_style = BattleThemes.default()


def set_battle_theme(theme_name: str) -> None:
    """Set the current battle theme."""
    global current_battle_style
    
    theme_methods = {
        'default': BattleThemes.default,
        'dark': BattleThemes.dark,
        'light': BattleThemes.light,
        'retro': BattleThemes.retro,
        'modern': BattleThemes.modern
    }
    
    if theme_name in theme_methods:
        current_battle_style = theme_methods[theme_name]()
    else:
        print(f"Warning: Unknown theme '{theme_name}', using default")


def get_current_style() -> BattleStyle:
    """Get the current battle style."""
    return current_battle_style


def customize_style(**kwargs) -> None:
    """Customize the current battle style."""
    global current_battle_style
    current_battle_style = StyleUtils.apply_style_variations(current_battle_style, kwargs)
