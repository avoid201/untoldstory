# ARCHIVED: 2025-09-03 - Debug-only scene removed from main codebase
"""
Debug Monster Selection Scene for Untold Story
Allows selecting a monster from the database to start on Route 1
"""

import pygame
from typing import Optional, List, Dict, Any
from engine.core.scene_base import Scene
from engine.core.resources import resources
from engine.systems.monsters import MonsterDatabase
from engine.systems.monster_instance import MonsterInstance


class DebugMonsterScene(Scene):
    """
    Debug scene for selecting a monster to start with on Route 1.
    """
    
    def __init__(self, game: 'Game') -> None:
        """
        Initialize the debug monster selection scene.
        
        Args:
            game: Game instance
        """
        super().__init__(game)
        
        # Visual settings
        self.bg_color = (20, 25, 40)  # Dark blue background
        self.title_color = (255, 220, 100)  # Golden yellow
        self.text_color = (255, 255, 255)  # White
        self.highlight_color = (100, 200, 255)  # Light blue
        self.selected_color = (255, 200, 100)  # Orange
        
        # Fonts
        self.title_font: Optional[pygame.font.Font] = None
        self.monster_font: Optional[pygame.font.Font] = None
        self.info_font: Optional[pygame.font.Font] = None
        self._load_fonts()
        
        # Monster database
        self.monster_db = MonsterDatabase()
        self.available_monsters: List[Dict[str, Any]] = []
        self.selected_index = 0
        self.scroll_offset = 0
        self.monsters_per_page = 8
        
        # Load available monsters
        self._load_monsters()
        
        # UI state
        self.transitioning = False
        
    def _load_fonts(self) -> None:
        """Load fonts for the debug scene."""
        try:
            self.title_font = pygame.font.Font(None, 24)
            self.monster_font = pygame.font.Font(None, 16)
            self.info_font = pygame.font.Font(None, 14)
        except:
            print("Warning: Could not load debug scene fonts")
    
    def _load_monsters(self) -> None:
        """Load available monsters from database."""
        self.available_monsters = []
        
        for species_id, species in self.monster_db.species.items():
            monster_info = {
                'id': species_id,
                'name': species.name,
                'types': species.types,
                'rank': species.rank.value,
                'species': species
            }
            self.available_monsters.append(monster_info)
        
        # Sort by ID for consistent ordering
        self.available_monsters.sort(key=lambda x: int(x['id']))
        
        # Debug-Output nur bei aktiviertem Debug-Modus
        # print(f"🐛 Debug: Loaded {len(self.available_monsters)} monsters for selection")
    
    def enter(self, **kwargs) -> None:
        """Called when scene becomes active."""
        super().enter(**kwargs)
        self.transitioning = False
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle input events.
        
        Args:
            event: pygame event to process
            
        Returns:
            True if event was handled
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Return to title screen
                from engine.scenes.start_scene import StartScene
                start_scene = StartScene(self.game)
                self.game.replace_scene(start_scene)
                return True
            
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                # Select current monster and start
                self._select_monster_and_start()
                return True
            
            elif event.key == pygame.K_UP:
                # Move selection up
                if self.selected_index > 0:
                    self.selected_index -= 1
                    self._update_scroll()
                return True
            
            elif event.key == pygame.K_DOWN:
                # Move selection down
                if self.selected_index < len(self.available_monsters) - 1:
                    self.selected_index += 1
                    self._update_scroll()
                return True
            
            elif event.key == pygame.K_PAGEUP:
                # Page up
                self.selected_index = max(0, self.selected_index - self.monsters_per_page)
                self._update_scroll()
                return True
            
            elif event.key == pygame.K_PAGEDOWN:
                # Page down
                self.selected_index = min(len(self.available_monsters) - 1, 
                                        self.selected_index + self.monsters_per_page)
                self._update_scroll()
                return True
        
        return False
    
    def _update_scroll(self) -> None:
        """Update scroll offset based on selection."""
        if self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        elif self.selected_index >= self.scroll_offset + self.monsters_per_page:
            self.scroll_offset = self.selected_index - self.monsters_per_page + 1
    
    def _select_monster_and_start(self) -> None:
        """Select the current monster and start on Route 1."""
        if self.transitioning or not self.available_monsters:
            return
        
        self.transitioning = True
        
        try:
            # Get selected monster
            selected_monster_info = self.available_monsters[self.selected_index]
            species = selected_monster_info['species']
            
            # Create monster instance
            debug_monster = MonsterInstance(species, level=5, nickname="Debug-Kumpel")
            
            # Add to party
            success, message = self.game.party_manager.add_to_party(debug_monster)
            # Debug-Output nur bei aktiviertem Debug-Modus
            # print(f"🐛 Debug monster added: {message}")
            # print(f"🐛 Monster: {debug_monster.species.name} (Level {debug_monster.level})")
            
            # Set active monster
            self.game.party_manager.party.set_active(0)
            
            # Start on Route 1
            from engine.scenes.field_scene import FieldScene
            field_scene = FieldScene(self.game)
            field_scene.load_map("route1", spawn_x=5, spawn_y=5)
            self.game.replace_scene(field_scene)
            
            # Debug-Output nur bei aktiviertem Debug-Modus
            # print(f"🐛 DEBUG: Started on Route 1 with {debug_monster.species.name}!")
            
        except Exception as e:
            # Debug-Output nur bei aktiviertem Debug-Modus
            # print(f"🐛 DEBUG: Error starting with selected monster: {e}")
            import traceback
            traceback.print_exc()
            self.transitioning = False
    
    def update(self, dt: float) -> None:
        """Update the scene."""
        pass  # No animation needed
    
    def draw(self, surface: pygame.Surface) -> None:
        """
        Render the scene.
        
        Args:
            surface: Surface to draw on
        """
        # Clear background
        surface.fill(self.bg_color)
        
        # Draw title
        if self.title_font:
            title_surface = self.title_font.render("🐛 DEBUG MODUS - Monster auswählen", True, self.title_color)
            title_rect = title_surface.get_rect()
            title_rect.centerx = surface.get_width() // 2
            title_rect.y = 10
            surface.blit(title_surface, title_rect)
        
        # Draw instructions
        if self.info_font:
            instructions = [
                "Wähle ein Monster mit ↑↓ und bestätige mit ENTER",
                "ESC = Zurück zum Titelbildschirm"
            ]
            for i, instruction in enumerate(instructions):
                inst_surface = self.info_font.render(instruction, True, self.text_color)
                surface.blit(inst_surface, (10, 40 + i * 15))
        
        # Draw monster list
        self._draw_monster_list(surface)
        
        # Draw selection info
        self._draw_selection_info(surface)
    
    def _draw_monster_list(self, surface: pygame.Surface) -> None:
        """Draw the list of available monsters."""
        if not self.monster_font or not self.available_monsters:
            return
        
        start_y = 80
        line_height = 20
        
        # Calculate visible range
        start_idx = self.scroll_offset
        end_idx = min(start_idx + self.monsters_per_page, len(self.available_monsters))
        
        for i in range(start_idx, end_idx):
            monster_info = self.available_monsters[i]
            y_pos = start_y + (i - start_idx) * line_height
            
            # Determine color based on selection
            if i == self.selected_index:
                color = self.selected_color
                # Draw selection background
                pygame.draw.rect(surface, (50, 50, 80), (5, y_pos - 2, surface.get_width() - 10, line_height))
            else:
                color = self.text_color
            
            # Format monster info
            types_str = "/".join(monster_info['types'])
            monster_text = f"#{monster_info['id']:03d} {monster_info['name']} ({types_str}) [{monster_info['rank']}]"
            
            # Draw monster text
            monster_surface = self.monster_font.render(monster_text, True, color)
            surface.blit(monster_surface, (10, y_pos))
    
    def _draw_selection_info(self, surface: pygame.Surface) -> None:
        """Draw information about the selected monster."""
        if not self.info_font or not self.available_monsters or self.selected_index >= len(self.available_monsters):
            return
        
        monster_info = self.available_monsters[self.selected_index]
        species = monster_info['species']
        
        # Draw monster details
        info_y = surface.get_height() - 60
        details = [
            f"Name: {species.name}",
            f"Typen: {'/'.join(species.types)}",
            f"Rang: {species.rank.value}",
            f"HP: {species.base_stats.hp} | ATK: {species.base_stats.atk} | DEF: {species.base_stats.def_}",
            f"MAG: {species.base_stats.mag} | RES: {species.base_stats.res} | SPD: {species.base_stats.spd}"
        ]
        
        for i, detail in enumerate(details):
            detail_surface = self.info_font.render(detail, True, self.highlight_color)
            surface.blit(detail_surface, (10, info_y + i * 12))
