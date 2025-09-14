"""
Debug Monster Scene for Untold Story
Simple debug interface for monster selection and testing
"""

import pygame
from typing import Optional
from engine.core.scene_base import Scene
from engine.core.resources import resources


class DebugMonsterScene(Scene):
    """
    Debug scene for monster selection and testing.
    """
    
    def __init__(self, game: 'Game') -> None:
        """
        Initialize the debug monster scene.
        
        Args:
            game: Game instance
        """
        super().__init__(game)
        
        # Visual settings
        self.bg_color = (40, 20, 20)  # Dark red background for debug
        self.text_color = (255, 255, 255)  # White text
        self.highlight_color = (255, 200, 100)  # Yellow highlight
        
        # Fonts
        self.title_font: Optional[pygame.font.Font] = None
        self.text_font: Optional[pygame.font.Font] = None
        self._load_fonts()
        
        # Text content
        self.title_text = "DEBUG MODUS"
        self.subtitle_text = "Route 1 mit zufälligem Monster"
        self.instruction_text = "Drücke ENTER für Route 1 Testing"
        self.escape_text = "Drücke ESC für Start-Screen"
        
        # Animation
        self.animation_timer = 0.0
        self.text_alpha = 255
        self.fade_in = True
        
        # Transition flag
        self.transitioning = False
    
    def _load_fonts(self) -> None:
        """Load fonts for the debug scene."""
        try:
            self.title_font = pygame.font.Font(None, 36)
            self.text_font = pygame.font.Font(None, 20)
        except:
            print("Warning: Could not load debug scene fonts")
    
    def enter(self, **kwargs) -> None:
        """Called when scene becomes active."""
        super().enter(**kwargs)
        
        # Reset animation state
        self.animation_timer = 0.0
        self.text_alpha = 255
        self.fade_in = True
        self.transitioning = False
        
        print("[DebugMonsterScene] Debug-Modus aktiviert")
    
    def exit(self) -> None:
        """Called when scene is exiting."""
        return super().exit()
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle input events.
        
        Args:
            event: pygame event to process
            
        Returns:
            True if event was handled
        """
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_RETURN, pygame.K_SPACE, pygame.K_e]:
                if not self.transitioning:
                    self._go_to_main_menu()
                    return True
            
            elif event.key == pygame.K_ESCAPE:
                if not self.transitioning:
                    self._go_to_start_screen()
                    return True
        
        return False
    
    def update(self, dt: float) -> None:
        """
        Update the scene.
        
        Args:
            dt: Delta time in seconds
        """
        self.animation_timer += dt
        
        # Update text blinking
        fade_speed = 150 * dt
        if self.fade_in:
            self.text_alpha += fade_speed
            if self.text_alpha >= 255:
                self.text_alpha = 255
                self.fade_in = False
        else:
            self.text_alpha -= fade_speed
            if self.text_alpha <= 100:
                self.text_alpha = 100
                self.fade_in = True
    
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
            title_surface = self.title_font.render(self.title_text, True, self.highlight_color)
            title_rect = title_surface.get_rect()
            title_rect.centerx = surface.get_width() // 2
            title_rect.centery = 80
            surface.blit(title_surface, title_rect)
        
        # Draw subtitle
        if self.text_font:
            subtitle_surface = self.text_font.render(self.subtitle_text, True, self.text_color)
            subtitle_rect = subtitle_surface.get_rect()
            subtitle_rect.centerx = surface.get_width() // 2
            subtitle_rect.centery = 120
            surface.blit(subtitle_surface, subtitle_rect)
        
        # Draw instructions with fade effect
        if self.text_font:
            instruction_surface = self.text_font.render(self.instruction_text, True, self.text_color)
            instruction_surface.set_alpha(int(self.text_alpha))
            instruction_rect = instruction_surface.get_rect()
            instruction_rect.centerx = surface.get_width() // 2
            instruction_rect.centery = 180
            surface.blit(instruction_surface, instruction_rect)
            
            escape_surface = self.text_font.render(self.escape_text, True, self.text_color)
            escape_surface.set_alpha(int(self.text_alpha))
            escape_rect = escape_surface.get_rect()
            escape_rect.centerx = surface.get_width() // 2
            escape_rect.centery = 210
            surface.blit(escape_surface, escape_rect)
        
        # Draw debug info
        if self.text_font:
            debug_info = [
                "Debug-Modus aktiv",
                "Monster-System: Bereit",
                "Battle-System: Bereit",
                "Item-System: Bereit"
            ]
            
            for i, info in enumerate(debug_info):
                info_surface = self.text_font.render(info, True, (200, 200, 200))
                info_rect = info_surface.get_rect()
                info_rect.centerx = surface.get_width() // 2
                info_rect.centery = 280 + i * 25
                surface.blit(info_surface, info_rect)
    
    def _go_to_main_menu(self) -> None:
        """Transition to Route 1 with random monster for testing."""
        if self.transitioning:
            return
        
        self.transitioning = True
        
        # Play confirmation sound
        try:
            sound = resources.load_sound("menu_confirm.wav", volume=0.7)
            sound.play()
        except:
            pass
        
        # Füge zufälliges Monster zur Party hinzu für Debug-Testing
        self._add_random_monster_to_party()
        
        # Transition to Route 1 with random monster for testing
        from engine.scenes.field_scene import FieldScene
        
        # Create Field Scene and load Route 1
        field_scene = FieldScene(self.game)
        field_scene.load_map("route1", spawn_x=5, spawn_y=5)
        self.game.replace_scene(field_scene)
        
        print(f"[DebugMonsterScene] Starte Route 1 mit zufälligem Monster für Testing (Transition: {self.transitioning})")
    
    def _add_random_monster_to_party(self) -> None:
        """Fügt ein zufälliges Monster zur Party hinzu für Debug-Testing."""
        try:
            # Lade Monster-Daten
            from engine.systems.monsters import get_monster_database
            from engine.systems.monster_instance import MonsterInstance
            import random
            
            # Hole Monster-Datenbank
            monster_db = get_monster_database()
            
            # Lade verfügbare Monster (F und E Rang für Route 1)
            available_monsters = []
            for rank in ["F", "E"]:
                species_ids = monster_db.species_by_rank.get(rank, [])
                for species_id in species_ids:
                    species = monster_db.get_species(species_id)
                    if species and species.era == "present":
                        available_monsters.append(species)
            
            if not available_monsters:
                print("[DebugMonsterScene] Keine Monster verfügbar!")
                return
            
            # Wähle zufälliges Monster
            random_species = random.choice(available_monsters)
            
            # Erstelle Monster-Instanz
            monster_instance = MonsterInstance(
                species=random_species,
                level=random.randint(5, 15),  # Level 5-15 für Debug
                nickname=None
            )
            
            # Füge zur Party hinzu
            if hasattr(self.game, 'party_manager'):
                success, message = self.game.party_manager.add_to_party(monster_instance)
                if success:
                    print(f"[DebugMonsterScene] Zufälliges Monster '{monster_instance.name}' (Level {monster_instance.level}) zur Party hinzugefügt: {message}")
                else:
                    print(f"[DebugMonsterScene] Fehler beim Hinzufügen: {message}")
            else:
                print("[DebugMonsterScene] Kein Party-Manager gefunden!")
                
        except Exception as e:
            print(f"[DebugMonsterScene] Fehler beim Hinzufügen des zufälligen Monsters: {e}")
    
    def _go_to_start_screen(self) -> None:
        """Transition back to start screen."""
        if self.transitioning:
            return
        
        self.transitioning = True
        
        # Play cancel sound
        try:
            sound = resources.load_sound("menu_cancel.wav", volume=0.7)
            sound.play()
        except:
            pass
        
        # Transition to start scene
        from engine.scenes.start_scene import StartScene
        
        # Create Start Scene and switch
        start_scene = StartScene(self.game)
        self.game.replace_scene(start_scene)
        
        print(f"[DebugMonsterScene] Zurück zum Start-Screen (Transition: {self.transitioning})")
