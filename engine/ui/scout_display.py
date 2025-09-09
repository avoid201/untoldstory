"""
Scout Display component for the battle system.
Shows detailed monster analysis in DQM style.
"""

import pygame
import math
from typing import Optional, Dict, List, Tuple, Any
from dataclasses import dataclass
from enum import Enum

from engine.core.config import LOGICAL_WIDTH, LOGICAL_HEIGHT, Colors
from engine.ui.battle_ui_utils import fonts, types, sprites, colors, text_utils


class ScoutDisplayTab(Enum):
    """Tabs for the scout display."""
    STATS = 0
    TYPES = 1
    MOVES = 2
    TRAITS = 3
    TALENTS = 4
    TAMING = 5


@dataclass
class MonsterAnalysis:
    """Complete analysis data for a monster."""
    name: str
    level: int
    rank: str
    types: List[str]
    current_hp: int
    max_hp: int
    stats: Dict[str, int]  # atk, def, mag, res, spd
    moves: List[Dict[str, Any]]
    traits: List[str]
    status: Optional[str]
    weakness: List[str]
    resistance: List[str]
    taming_difficulty: str
    talents: List[Dict[str, Any]] = field(default_factory=list)  # Talent-Daten
    passive_abilities: List[Dict[str, Any]] = field(default_factory=list)  # Passive Fähigkeiten
    description: str = ""
    seen_count: int = 0
    caught_count: int = 0


class ScoutDisplay:
    """
    Monster analysis display system.
    Shows comprehensive information about the target monster.
    """
    
    def __init__(self):
        """Initialize the scout display."""
        # Use centralized font manager
        self.font_title = fonts.huge
        self.font_large = fonts.large
        self.font_normal = fonts.normal
        self.font_small = fonts.small
        self.font_tiny = fonts.tiny
        
        # Display state
        self.visible = False
        self.current_tab = ScoutDisplayTab.STATS
        self.monster_data: Optional[MonsterAnalysis] = None
        
        # UI positioning
        self.display_pos = (20, 20)
        self.display_size = (LOGICAL_WIDTH - 40, LOGICAL_HEIGHT - 40)
        
        # Tab positions
        self.tab_height = 25
        self.content_start_y = 50
        
        # Colors
        self.color_bg = (30, 30, 45)
        self.color_border = (80, 100, 150)
        self.color_tab_active = (60, 60, 80)
        self.color_tab_inactive = (40, 40, 55)
        self.color_selected = (255, 255, 100)
        self.color_text = (200, 200, 200)
        
        # Animation
        self.fade_alpha = 0
        self.fade_speed = 10
        
        # Monsterdex integration
        self.monsterdex_data = {}  # Store seen/caught info
        
    def show_monster_analysis(self, monster, battle_state=None):
        """
        Show analysis for a monster.
        
        Args:
            monster: The monster to analyze
            battle_state: Current battle state (optional)
        """
        if not monster:
            return
        
        # Extract monster data
        self.monster_data = self._analyze_monster(monster, battle_state)
        
        # Update Monsterdex
        monster_id = self._get_monster_id(monster)
        if monster_id not in self.monsterdex_data:
            self.monsterdex_data[monster_id] = {
                'seen': 0,
                'caught': 0,
                'first_seen': pygame.time.get_ticks()
            }
        self.monsterdex_data[monster_id]['seen'] += 1
        
        # Show display
        self.visible = True
        self.current_tab = ScoutDisplayTab.STATS
        self.fade_alpha = 0
    
    def _analyze_monster(self, monster, battle_state=None) -> MonsterAnalysis:
        """
        Analyze a monster and extract all data.
        
        Args:
            monster: Monster to analyze
            battle_state: Battle state for additional context
            
        Returns:
            MonsterAnalysis object with all data
        """
        # Basic info
        name = monster.name if hasattr(monster, 'name') else "???"
        level = monster.level if hasattr(monster, 'level') else 1
        
        # Rank
        rank = 'D'  # Default
        if hasattr(monster, 'rank'):
            rank = monster.rank
        elif hasattr(monster, 'species') and hasattr(monster.species, 'rank'):
            rank = monster.species.rank
        
        # Types
        types = []
        if hasattr(monster, 'types'):
            types = monster.types if isinstance(monster.types, list) else [monster.types]
        
        # HP
        current_hp = monster.current_hp if hasattr(monster, 'current_hp') else 0
        max_hp = monster.max_hp if hasattr(monster, 'max_hp') else 1
        
        # Talent-Analyse
        talents = []
        passive_abilities = []
        if hasattr(monster, 'talents'):
            try:
                from engine.systems.talent_system import get_talent_database
                talent_db = get_talent_database()
                
                for talent_instance in monster.talents:
                    if talent_instance.is_learned:
                        talent = talent_db.get_talent(talent_instance.talent_id)
                        if talent:
                            talents.append({
                                'id': talent.id,
                                'name': talent.name,
                                'tier': talent_instance.current_tier.value,
                                'tier_stars': '★' * talent_instance.current_tier.value,
                                'description': talent.description,
                                'category': talent.category.value,
                                'moves': talent.get_moves_for_tier(talent_instance.current_tier, level)
                            })
                            
                            # Passive Fähigkeiten sammeln
                            abilities = talent.get_passive_abilities_for_tier(talent_instance.current_tier)
                            for ability in abilities:
                                passive_abilities.append({
                                    'name': ability['name'],
                                    'description': ability['description'],
                                    'effect_type': ability['effect_type'],
                                    'value': ability['value'],
                                    'talent_name': talent.name
                                })
            except Exception as e:
                logger.error(f"Error analyzing talents: {e}")
        
        # Stats
        stats = {}
        if hasattr(monster, 'stats'):
            if isinstance(monster.stats, dict):
                stats = monster.stats.copy()
            else:
                # Extract from stats object
                for stat in ['atk', 'def', 'mag', 'res', 'spd']:
                    if hasattr(monster.stats, stat):
                        stats[stat] = getattr(monster.stats, stat)
        
        # Moves
        moves = []
        if hasattr(monster, 'moves'):
            for move in monster.moves[:6]:  # Show max 6 moves
                if hasattr(move, 'name'):
                    move_data = {
                        'name': move.name,
                        'type': move.type if hasattr(move, 'type') else '???',
                        'power': move.power if hasattr(move, 'power') else 0,
                        'pp': move.current_pp if hasattr(move, 'current_pp') else 0,
                        'max_pp': move.max_pp if hasattr(move, 'max_pp') else 0
                    }
                    moves.append(move_data)
        
        # Traits
        traits = []
        if hasattr(monster, 'traits'):
            traits = monster.traits if isinstance(monster.traits, list) else [monster.traits]
        elif hasattr(monster, 'species') and hasattr(monster.species, 'traits'):
            traits = monster.species.traits if isinstance(monster.species.traits, list) else []
        
        # Status
        status = None
        if hasattr(monster, 'status'):
            if hasattr(monster.status, 'value'):
                status = monster.status.value
            elif isinstance(monster.status, str):
                status = monster.status
        
        # Type effectiveness
        weakness, resistance = self._calculate_type_effectiveness(types)
        
        # Taming difficulty
        taming_difficulty = self._calculate_taming_difficulty(rank, level)
        
        # Description
        description = ""
        if hasattr(monster, 'species') and hasattr(monster.species, 'description'):
            description = monster.species.description
        elif hasattr(monster, 'description'):
            description = monster.description
        
        # Monsterdex data
        monster_id = self._get_monster_id(monster)
        seen_count = self.monsterdex_data.get(monster_id, {}).get('seen', 0)
        caught_count = self.monsterdex_data.get(monster_id, {}).get('caught', 0)
        
        return MonsterAnalysis(
            name=name,
            level=level,
            rank=rank,
            types=types,
            current_hp=current_hp,
            max_hp=max_hp,
            stats=stats,
            moves=moves,
            traits=traits,
            status=status,
            weakness=weakness,
            resistance=resistance,
            taming_difficulty=taming_difficulty,
            talents=talents,
            passive_abilities=passive_abilities,
            description=description,
            seen_count=seen_count,
            caught_count=caught_count
        )
    
    def _calculate_type_effectiveness(self, monster_types: List[str]) -> Tuple[List[str], List[str]]:
        """
        Calculate type weaknesses and resistances using centralized type manager.
        
        Args:
            monster_types: Monster's types
            
        Returns:
            Tuple of (weaknesses, resistances)
        """
        return types.calculate_weaknesses_and_resistances(monster_types)
    
    def _calculate_taming_difficulty(self, rank: str, level: int) -> str:
        """
        Calculate taming difficulty based on rank and level.
        
        Args:
            rank: Monster rank
            level: Monster level
            
        Returns:
            Difficulty string
        """
        rank_scores = {
            'F': 1, 'E': 2, 'D': 3, 'C': 4,
            'B': 5, 'A': 6, 'S': 7, 'SS': 8, 'X': 9
        }
        
        score = rank_scores.get(rank, 3) + (level // 10)
        
        if score <= 2:
            return "Sehr Leicht"
        elif score <= 4:
            return "Leicht"
        elif score <= 6:
            return "Mittel"
        elif score <= 8:
            return "Schwer"
        else:
            return "Sehr Schwer"
    
    def _get_monster_id(self, monster) -> str:
        """Get unique ID for a monster."""
        if hasattr(monster, 'species_id'):
            return str(monster.species_id)
        elif hasattr(monster, 'species') and hasattr(monster.species, 'id'):
            return str(monster.species.id)
        elif hasattr(monster, 'name'):
            return monster.name.lower().replace(' ', '_')
        else:
            return "unknown"
    
    def update(self, dt: float):
        """
        Update scout display animations.
        
        Args:
            dt: Delta time in seconds
        """
        if self.visible:
            # Fade in
            if self.fade_alpha < 255:
                self.fade_alpha = min(255, self.fade_alpha + self.fade_speed)
    
    def draw(self, surface: pygame.Surface):
        """
        Draw the scout display.
        
        Args:
            surface: Surface to draw on
        """
        if not self.visible or not self.monster_data:
            return
        
        # Create semi-transparent overlay
        overlay = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT))
        overlay.set_alpha(int(self.fade_alpha * 0.7))
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))
        
        x, y = self.display_pos
        w, h = self.display_size
        
        # Main background
        pygame.draw.rect(surface, self.color_bg, (x, y, w, h))
        pygame.draw.rect(surface, self.color_border, (x, y, w, h), 2)
        
        # Title bar
        title_text = f"MONSTER-ANALYSE: {self.monster_data.name}"
        title = self.font_title.render(title_text, True, Colors.WHITE)
        title_rect = title.get_rect(centerx=x + w // 2, y=y + 10)
        surface.blit(title, title_rect)
        
        # Draw tabs
        self._draw_tabs(surface, x, y + 30, w)
        
        # Draw content based on current tab
        content_y = y + self.content_start_y
        if self.current_tab == ScoutDisplayTab.STATS:
            self._draw_stats_tab(surface, x, content_y, w, h - self.content_start_y)
        elif self.current_tab == ScoutDisplayTab.TYPES:
            self._draw_types_tab(surface, x, content_y, w, h - self.content_start_y)
        elif self.current_tab == ScoutDisplayTab.MOVES:
            self._draw_moves_tab(surface, x, content_y, w, h - self.content_start_y)
        elif self.current_tab == ScoutDisplayTab.TRAITS:
            self._draw_traits_tab(surface, x, content_y, w, h - self.content_start_y)
        elif self.current_tab == ScoutDisplayTab.TALENTS:
            self._draw_talents_tab(surface, x, content_y, w, h - self.content_start_y)
        elif self.current_tab == ScoutDisplayTab.TAMING:
            self._draw_taming_tab(surface, x, content_y, w, h - self.content_start_y)
        
        # Draw close hint
        hint = self.font_tiny.render("[ESC] Schließen | [←/→] Tab wechseln", True, Colors.LIGHT_GRAY)
        surface.blit(hint, (x + 5, y + h - 15))
    
    def _draw_tabs(self, surface: pygame.Surface, x: int, y: int, width: int):
        """Draw tab headers."""
        tab_names = ["Stats", "Typen", "Attacken", "Traits", "Talente", "Zähmen"]
        tab_width = width // len(tab_names)
        
        for i, (tab, name) in enumerate(zip(ScoutDisplayTab, tab_names)):
            tab_x = x + i * tab_width
            
            # Tab background
            if tab == self.current_tab:
                color = self.color_tab_active
                text_color = self.color_selected
            else:
                color = self.color_tab_inactive
                text_color = self.color_text
            
            pygame.draw.rect(surface, color, (tab_x, y, tab_width - 2, self.tab_height))
            pygame.draw.rect(surface, self.color_border, (tab_x, y, tab_width - 2, self.tab_height), 1)
            
            # Tab text
            text = self.font_small.render(name, True, text_color)
            text_rect = text.get_rect(centerx=tab_x + tab_width // 2, centery=y + self.tab_height // 2)
            surface.blit(text, text_rect)
    
    def _draw_stats_tab(self, surface: pygame.Surface, x: int, y: int, w: int, h: int):
        """Draw stats tab content."""
        data = self.monster_data
        
        # Left column - Basic info
        col1_x = x + 10
        col1_y = y + 10
        
        # Monster sprite placeholder
        sprite_size = 48
        pygame.draw.rect(surface, (50, 50, 70), (col1_x, col1_y, sprite_size, sprite_size))
        pygame.draw.rect(surface, self.color_border, (col1_x, col1_y, sprite_size, sprite_size), 1)
        
        # Name and level
        info_x = col1_x + sprite_size + 10
        name_text = self.font_large.render(data.name, True, Colors.WHITE)
        surface.blit(name_text, (info_x, col1_y))
        
        level_text = self.font_normal.render(f"Level {data.level} | Rang {data.rank}", True, Colors.LIGHT_GRAY)
        surface.blit(level_text, (info_x, col1_y + 20))
        
        # HP Bar
        hp_y = col1_y + sprite_size + 10
        hp_label = self.font_small.render("HP:", True, Colors.WHITE)
        surface.blit(hp_label, (col1_x, hp_y))
        
        hp_bar_x = col1_x + 30
        hp_bar_width = 150
        hp_bar_height = 12
        hp_percent = data.current_hp / max(1, data.max_hp)
        
        # HP bar background
        pygame.draw.rect(surface, (40, 40, 40), (hp_bar_x, hp_y, hp_bar_width, hp_bar_height))
        
        # HP bar fill
        hp_color = Colors.HP_HIGH if hp_percent > 0.5 else Colors.HP_MED if hp_percent > 0.25 else Colors.HP_LOW
        pygame.draw.rect(surface, hp_color, (hp_bar_x, hp_y, int(hp_bar_width * hp_percent), hp_bar_height))
        pygame.draw.rect(surface, self.color_border, (hp_bar_x, hp_y, hp_bar_width, hp_bar_height), 1)
        
        # HP text
        hp_text = self.font_small.render(f"{data.current_hp}/{data.max_hp}", True, Colors.WHITE)
        surface.blit(hp_text, (hp_bar_x + hp_bar_width + 5, hp_y))
        
        # Stats
        stats_y = hp_y + 25
        stat_labels = {
            'atk': ('ATK', Colors.RED),
            'def': ('DEF', Colors.BLUE),
            'mag': ('MAG', Colors.MAGENTA),
            'res': ('RES', Colors.CYAN),
            'spd': ('SPD', Colors.GREEN)
        }
        
        for i, (stat_key, (label, color)) in enumerate(stat_labels.items()):
            stat_y = stats_y + i * 20
            stat_value = data.stats.get(stat_key, 0)
            
            # Label
            label_text = self.font_small.render(f"{label}:", True, color)
            surface.blit(label_text, (col1_x, stat_y))
            
            # Value
            value_text = self.font_normal.render(str(stat_value), True, Colors.WHITE)
            surface.blit(value_text, (col1_x + 40, stat_y))
            
            # Bar visualization
            bar_x = col1_x + 80
            bar_width = 100
            bar_height = 8
            bar_percent = min(1.0, stat_value / 100)  # Assume 100 is max for visualization
            
            pygame.draw.rect(surface, (40, 40, 40), (bar_x, stat_y + 2, bar_width, bar_height))
            pygame.draw.rect(surface, color, (bar_x, stat_y + 2, int(bar_width * bar_percent), bar_height))
            pygame.draw.rect(surface, self.color_border, (bar_x, stat_y + 2, bar_width, bar_height), 1)
        
        # Right column - Description
        col2_x = x + w // 2
        col2_y = y + 10
        
        desc_label = self.font_normal.render("Beschreibung:", True, Colors.WHITE)
        surface.blit(desc_label, (col2_x, col2_y))
        
        # Word wrap description
        if data.description:
            lines = self._wrap_text(data.description, w // 2 - 20, self.font_small)
            for i, line in enumerate(lines[:5]):  # Max 5 lines
                text = self.font_small.render(line, True, Colors.LIGHT_GRAY)
                surface.blit(text, (col2_x, col2_y + 20 + i * 15))
        
        # Monsterdex info
        dex_y = col2_y + 100
        seen_text = self.font_small.render(f"Gesehen: {data.seen_count}x", True, Colors.LIGHT_GRAY)
        caught_text = self.font_small.render(f"Gefangen: {data.caught_count}x", True, Colors.LIGHT_GRAY)
        surface.blit(seen_text, (col2_x, dex_y))
        surface.blit(caught_text, (col2_x, dex_y + 15))
    
    def _draw_types_tab(self, surface: pygame.Surface, x: int, y: int, w: int, h: int):
        """Draw types tab content."""
        data = self.monster_data
        
        # Monster types
        types_y = y + 10
        types_label = self.font_normal.render("Monster-Typen:", True, Colors.WHITE)
        surface.blit(types_label, (x + 10, types_y))
        
        for i, monster_type in enumerate(data.types):
            type_y = types_y + 25 + i * 25
            type_color = self._get_type_color(monster_type)
            
            # Type badge
            badge_rect = pygame.Rect(x + 20, type_y, 80, 20)
            pygame.draw.rect(surface, type_color, badge_rect)
            pygame.draw.rect(surface, Colors.WHITE, badge_rect, 1)
            
            type_text = self.font_normal.render(monster_type, True, Colors.WHITE)
            text_rect = type_text.get_rect(center=badge_rect.center)
            surface.blit(type_text, text_rect)
        
        # Weaknesses
        weak_y = types_y + 80
        weak_label = self.font_normal.render("Schwächen (2x Schaden):", True, Colors.RED)
        surface.blit(weak_label, (x + 10, weak_y))
        
        for i, weakness in enumerate(data.weakness[:4]):  # Max 4
            w_y = weak_y + 25 + i * 20
            w_color = self._get_type_color(weakness)
            
            # Weakness icon
            pygame.draw.circle(surface, w_color, (x + 25, w_y + 8), 6)
            
            w_text = self.font_small.render(weakness, True, Colors.WHITE)
            surface.blit(w_text, (x + 40, w_y))
        
        # Resistances
        resist_y = weak_y + 100
        resist_label = self.font_normal.render("Resistenzen (0.5x Schaden):", True, Colors.GREEN)
        surface.blit(resist_label, (x + 10, resist_y))
        
        for i, resistance in enumerate(data.resistance[:4]):  # Max 4
            r_y = resist_y + 25 + i * 20
            r_color = self._get_type_color(resistance)
            
            # Resistance icon
            pygame.draw.circle(surface, r_color, (x + 25, r_y + 8), 6)
            
            r_text = self.font_small.render(resistance, True, Colors.WHITE)
            surface.blit(r_text, (x + 40, r_y))
        
        # Type effectiveness chart (simplified)
        chart_x = x + w // 2
        chart_y = y + 10
        
        chart_label = self.font_normal.render("Typ-Effektivität:", True, Colors.WHITE)
        surface.blit(chart_label, (chart_x, chart_y))
        
        # Draw a simple effectiveness grid
        self._draw_type_chart(surface, chart_x, chart_y + 25, w // 2 - 20, h - 40)
    
    def _draw_moves_tab(self, surface: pygame.Surface, x: int, y: int, w: int, h: int):
        """Draw moves tab content."""
        data = self.monster_data
        
        moves_label = self.font_normal.render("Bekannte Attacken:", True, Colors.WHITE)
        surface.blit(moves_label, (x + 10, y + 10))
        
        if not data.moves:
            no_moves = self.font_small.render("Keine Attacken bekannt", True, Colors.LIGHT_GRAY)
            surface.blit(no_moves, (x + 20, y + 35))
            return
        
        # Move list
        for i, move in enumerate(data.moves):
            move_y = y + 35 + i * 35
            
            # Move background
            move_bg = pygame.Rect(x + 10, move_y, w - 20, 30)
            pygame.draw.rect(surface, (40, 40, 55), move_bg)
            pygame.draw.rect(surface, self.color_border, move_bg, 1)
            
            # Move name
            name_text = self.font_normal.render(move['name'], True, Colors.WHITE)
            surface.blit(name_text, (x + 20, move_y + 5))
            
            # Move type
            type_color = self._get_type_color(move['type'])
            type_badge = pygame.Rect(x + 150, move_y + 5, 60, 20)
            pygame.draw.rect(surface, type_color, type_badge)
            pygame.draw.rect(surface, Colors.WHITE, type_badge, 1)
            
            type_text = self.font_small.render(move['type'], True, Colors.WHITE)
            type_rect = type_text.get_rect(center=type_badge.center)
            surface.blit(type_text, type_rect)
            
            # Power
            if move['power'] > 0:
                power_text = self.font_small.render(f"Stärke: {move['power']}", True, Colors.YELLOW)
                surface.blit(power_text, (x + 220, move_y + 8))
            
            # PP system removed - DQM style has unlimited moves
    
    def _draw_traits_tab(self, surface: pygame.Surface, x: int, y: int, w: int, h: int):
        """Draw traits tab content."""
        data = self.monster_data
        
        traits_label = self.font_normal.render("Monster-Eigenschaften:", True, Colors.WHITE)
        surface.blit(traits_label, (x + 10, y + 10))
        
        if not data.traits:
            no_traits = self.font_small.render("Keine besonderen Eigenschaften", True, Colors.LIGHT_GRAY)
            surface.blit(no_traits, (x + 20, y + 35))
            return
        
        # Trait list
        for i, trait in enumerate(data.traits):
            trait_y = y + 35 + i * 60
            
            # Trait icon placeholder
            icon_rect = pygame.Rect(x + 15, trait_y, 30, 30)
            pygame.draw.rect(surface, (60, 60, 80), icon_rect)
            pygame.draw.rect(surface, self.color_border, icon_rect, 1)
            
            # Trait name
            name_text = self.font_normal.render(trait, True, Colors.YELLOW)
            surface.blit(name_text, (x + 55, trait_y))
            
            # Trait description (placeholder)
            desc = self._get_trait_description(trait)
            desc_lines = self._wrap_text(desc, w - 70, self.font_small)
            for j, line in enumerate(desc_lines[:2]):  # Max 2 lines
                line_text = self.font_small.render(line, True, Colors.LIGHT_GRAY)
                surface.blit(line_text, (x + 55, trait_y + 20 + j * 15))
        
        # Status condition if any
        if data.status:
            status_y = y + h - 60
            status_label = self.font_normal.render("Aktueller Status:", True, Colors.WHITE)
            surface.blit(status_label, (x + 10, status_y))
            
            status_color = self._get_status_color(data.status)
            status_text = self.font_large.render(data.status.upper(), True, status_color)
            surface.blit(status_text, (x + 20, status_y + 20))
    
    def _draw_taming_tab(self, surface: pygame.Surface, x: int, y: int, w: int, h: int):
        """Draw taming tab content."""
        data = self.monster_data
        
        taming_label = self.font_normal.render("Zähm-Information:", True, Colors.WHITE)
        surface.blit(taming_label, (x + 10, y + 10))
        
        # Taming difficulty
        diff_y = y + 35
        diff_label = self.font_normal.render("Schwierigkeit:", True, Colors.WHITE)
        surface.blit(diff_label, (x + 20, diff_y))
        
        diff_color = {
            "Sehr Leicht": Colors.GREEN,
            "Leicht": Colors.LIGHT_GREEN,
            "Mittel": Colors.YELLOW,
            "Schwer": Colors.ORANGE,
            "Sehr Schwer": Colors.RED
        }.get(data.taming_difficulty, Colors.WHITE)
        
        diff_text = self.font_large.render(data.taming_difficulty, True, diff_color)
        surface.blit(diff_text, (x + 120, diff_y - 2))
        
        # Base taming chance based on rank
        chance_y = diff_y + 30
        rank_chances = {
            'F': 25, 'E': 20, 'D': 15, 'C': 10,
            'B': 8, 'A': 5, 'S': 3, 'SS': 2, 'X': 1
        }
        base_chance = rank_chances.get(data.rank, 10)
        
        chance_label = self.font_small.render(f"Basis-Chance (Rang {data.rank}):", True, Colors.WHITE)
        surface.blit(chance_label, (x + 20, chance_y))
        
        chance_text = self.font_normal.render(f"{base_chance}%", True, Colors.YELLOW)
        surface.blit(chance_text, (x + 180, chance_y))
        
        # Taming tips
        tips_y = chance_y + 40
        tips_label = self.font_normal.render("Zähm-Tipps:", True, Colors.WHITE)
        surface.blit(tips_label, (x + 20, tips_y))
        
        tips = [
            "• HP reduzieren erhöht die Chance (+30% max)",
            "• Fleisch verwenden für Bonus (+20% bis +80%)",
            "• Statuseffekte helfen (Schlaf +15%)",
            "• Höheres Level des eigenen Monsters hilft"
        ]
        
        for i, tip in enumerate(tips):
            tip_text = self.font_small.render(tip, True, Colors.LIGHT_GRAY)
            surface.blit(tip_text, (x + 30, tips_y + 20 + i * 18))
        
        # Best meat recommendation
        meat_y = tips_y + 100
        meat_label = self.font_normal.render("Empfohlenes Fleisch:", True, Colors.WHITE)
        surface.blit(meat_label, (x + 20, meat_y))
        
        if data.rank in ['F', 'E', 'D']:
            meat_rec = "Normales Fleisch reicht aus"
            meat_color = Colors.GREEN
        elif data.rank in ['C', 'B', 'A']:
            meat_rec = "Edelfleisch empfohlen"
            meat_color = Colors.YELLOW
        else:
            meat_rec = "Götterfleisch stark empfohlen!"
            meat_color = Colors.RED
        
        meat_text = self.font_normal.render(meat_rec, True, meat_color)
        surface.blit(meat_text, (x + 30, meat_y + 20))
    
    def _get_type_color(self, type_name: str) -> Tuple[int, int, int]:
        """Get color for a type using centralized type manager."""
        return types.get_type_color(type_name)
    
    def _get_status_color(self, status: str) -> Tuple[int, int, int]:
        """Get color for a status condition."""
        status_colors = {
            'burn': Colors.RED,
            'poison': Colors.MAGENTA,
            'paralysis': Colors.YELLOW,
            'sleep': Colors.LIGHT_BLUE,
            'freeze': Colors.CYAN,
            'confusion': Colors.LIGHT_GRAY
        }
        return status_colors.get(status.lower(), Colors.WHITE)
    
    def _get_trait_description(self, trait: str) -> str:
        """Get description for a trait."""
        trait_descriptions = {
            'Entflammbar': 'Erhöht Feuer-Schaden um 20%, aber auch Feuer-Resistenz',
            'Stur': 'Verteidigung +10%, aber Initiative -10%',
            'Flink': 'Initiative +20%, kann Angriffen ausweichen',
            'Kraftprotz': 'Physische Angriffe +15%',
            'Magisch': 'Magische Angriffe +15%',
            'Robust': 'Alle Resistenzen +10%'
        }
        return trait_descriptions.get(trait, 'Besondere Eigenschaft dieses Monsters')
    
    def _draw_type_chart(self, surface: pygame.Surface, x: int, y: int, w: int, h: int):
        """Draw a simplified type effectiveness chart."""
        # This would show a grid of type matchups
        # For now, just show a placeholder
        chart_text = self.font_small.render("Typ-Interaktionen werden analysiert...", True, Colors.LIGHT_GRAY)
        surface.blit(chart_text, (x + 10, y + 20))
    
    def _wrap_text(self, text: str, max_width: int, font: pygame.font.Font) -> List[str]:
        """Wrap text to fit within max_width using centralized text utils."""
        return text_utils.wrap_text(text, max_width, font)
    
    def handle_input(self, action: str) -> bool:
        """
        Handle input for the scout display.
        
        Args:
            action: Input action string
            
        Returns:
            True if input was handled
        """
        if not self.visible:
            return False
        
        if action == 'back' or action == 'escape':
            self.hide()
            return True
        elif action == 'left':
            # Previous tab
            tabs = list(ScoutDisplayTab)
            current_index = tabs.index(self.current_tab)
            self.current_tab = tabs[(current_index - 1) % len(tabs)]
            return True
        elif action == 'right':
            # Next tab
            tabs = list(ScoutDisplayTab)
            current_index = tabs.index(self.current_tab)
            self.current_tab = tabs[(current_index + 1) % len(tabs)]
            return True
        
        return False
    
    def hide(self):
        """Hide the scout display."""
        self.visible = False
        self.fade_alpha = 0
    
    def is_visible(self) -> bool:
        """Check if scout display is visible."""
        return self.visible
    
    def update_monsterdex(self, monster_id: str, caught: bool = False):
        """
        Update Monsterdex data.
        
        Args:
            monster_id: Monster ID
            caught: Whether the monster was caught
        """
        if monster_id not in self.monsterdex_data:
            self.monsterdex_data[monster_id] = {
                'seen': 0,
                'caught': 0,
                'first_seen': pygame.time.get_ticks()
            }
        
        self.monsterdex_data[monster_id]['seen'] += 1
        if caught:
            self.monsterdex_data[monster_id]['caught'] += 1
    
    def _draw_talents_tab(self, surface: pygame.Surface, x: int, y: int, w: int, h: int):
        """Draw talents tab content."""
        data = self.monster_data
        
        if not data.talents:
            no_talents = self.font_normal.render("Keine Talente verfügbar", True, Colors.LIGHT_GRAY)
            surface.blit(no_talents, (x + 10, y + 10))
            return
        
        # Talent-Liste
        y_offset = 10
        for i, talent in enumerate(data.talents):
            if y_offset > h - 30:
                break
                
            # Talent-Name und Tier
            tier_stars = talent['tier_stars']
            talent_name = f"{talent['name']} {tier_stars}"
            
            # Farbe basierend auf Tier
            tier_colors = {
                1: (200, 200, 200),  # Grau für Basic
                2: (100, 255, 100),  # Grün für Intermediate
                3: (100, 100, 255),  # Blau für Advanced
                4: (255, 100, 255)   # Magenta für Master
            }
            color = tier_colors.get(talent['tier'], Colors.WHITE)
            
            # Talent-Name
            name_surf = self.font_normal.render(talent_name, True, color)
            surface.blit(name_surf, (x + 10, y + y_offset))
            y_offset += 20
            
            # Talent-Beschreibung
            desc_surf = self.font_small.render(talent['description'], True, Colors.LIGHT_GRAY)
            surface.blit(desc_surf, (x + 20, y + y_offset))
            y_offset += 15
            
            # Verfügbare Moves
            if talent['moves']:
                moves_text = f"Moves: {', '.join(talent['moves'])}"
                moves_surf = self.font_tiny.render(moves_text, True, Colors.GRAY)
                surface.blit(moves_surf, (x + 20, y + y_offset))
                y_offset += 12
            
            y_offset += 10
        
        # Passive Fähigkeiten
        if data.passive_abilities:
            y_offset += 10
            passive_title = self.font_normal.render("Passive Fähigkeiten:", True, Colors.YELLOW)
            surface.blit(passive_title, (x + 10, y + y_offset))
            y_offset += 20
            
            for ability in data.passive_abilities[:5]:  # Max 5 anzeigen
                if y_offset > h - 30:
                    break
                    
                ability_text = f"• {ability['name']}: {ability['description']}"
                ability_surf = self.font_small.render(ability_text, True, Colors.LIGHT_GRAY)
                surface.blit(ability_surf, (x + 20, y + y_offset))
                y_offset += 15
