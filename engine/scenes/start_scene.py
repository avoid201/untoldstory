"""
Start Scene for Untold Story
Title screen with "Press Start" prompt
"""

import pygame
import math
from typing import Optional
from engine.core.scene_base import Scene
from engine.core.resources import resources


class StartScene(Scene):
    """
    Title screen scene with animated logo and press start prompt.
    """
    
    def __init__(self, game: 'Game') -> None:
        """
        Initialize the start scene.
        
        Args:
            game: Game instance
        """
        super().__init__(game)
        
        # Visual settings
        self.bg_color = (20, 25, 40)  # Dark blue background
        self.title_color = (255, 220, 100)  # Golden yellow
        self.subtitle_color = (200, 200, 220)  # Light gray-blue
        self.prompt_color = (255, 255, 255)  # White
        
        # Fonts
        self.title_font: Optional[pygame.font.Font] = None
        self.subtitle_font: Optional[pygame.font.Font] = None
        self.prompt_font: Optional[pygame.font.Font] = None
        self._load_fonts()
        
        # Text content
        self.title_text = "UNTOLD STORY"
        self.subtitle_text = "Eine Reise durch die Zeit"  # "A Journey Through Time" in German
        self.prompt_text = "Press ENTER to Start"
        self.version_text = "v0.1.0 Alpha"
        
        # Animation state
        self.animation_timer = 0.0
        self.prompt_alpha = 255
        self.prompt_fade_in = True
        self.title_offset_y = 0.0
        self.particles = []  # Background particles
        
        # Logo/title animation
        self.logo_scale = 0.0
        self.logo_target_scale = 1.0
        self.intro_complete = False
        
        # Sound
        self.played_intro_sound = False
        
        # Transition flag
        self.transitioning = False
        
        # Initialize particles for background effect
        self._init_particles()
    
    def _load_fonts(self) -> None:
        """Load fonts for the title screen."""
        try:
            self.title_font = pygame.font.Font(None, 32)
            self.subtitle_font = pygame.font.Font(None, 16)
            self.prompt_font = pygame.font.Font(None, 18)
        except:
            print("Warning: Could not load title screen fonts")
    
    def _init_particles(self) -> None:
        """Initialize background particle effects."""
        import random
        
        # Create floating particles
        for _ in range(30):
            self.particles.append({
                'x': random.randint(0, self.game.logical_size[0]),
                'y': random.randint(0, self.game.logical_size[1]),
                'speed': random.uniform(5, 15),
                'size': random.randint(1, 3),
                'brightness': random.uniform(0.3, 1.0)
            })
    
    def enter(self, **kwargs) -> None:
        """Called when scene becomes active."""
        super().enter(**kwargs)
        
        # Play title music
        try:
            resources.load_music("title_theme.ogg", loops=-1)
        except:
            pass  # No music available
        
        # Reset animation state
        self.animation_timer = 0.0
        self.logo_scale = 0.0
        self.intro_complete = False
        self.transitioning = False
    
    def exit(self) -> None:
        """Called when scene is exiting."""
        # Fade out music
        resources.stop_music(fade_ms=500)
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
                if not self.transitioning and self.intro_complete:
                    self._start_game()
                    return True
                elif not self.intro_complete:
                    # Skip intro animation
                    self.logo_scale = 1.0
                    self.intro_complete = True
                    return True
            
            elif event.key == pygame.K_ESCAPE:
                self.game.quit()
                return True
        
        return False
    
    def update(self, dt: float) -> None:
        """
        Update the scene.
        
        Args:
            dt: Delta time in seconds
        """
        self.animation_timer += dt
        
        # Update logo intro animation
        if not self.intro_complete:
            self.logo_scale += dt * 2.0  # Scale up over 0.5 seconds
            if self.logo_scale >= 1.0:
                self.logo_scale = 1.0
                self.intro_complete = True
                
                # Play sound when intro completes
                if not self.played_intro_sound:
                    self.played_intro_sound = True
                    try:
                        sound = resources.load_sound("menu_confirm.wav", volume=0.5)
                        sound.play()
                    except:
                        pass
        
        # Update title floating animation
        self.title_offset_y = math.sin(self.animation_timer * 2) * 3
        
        # Update prompt blinking
        if self.intro_complete:
            # Fade prompt in and out
            fade_speed = 150 * dt
            if self.prompt_fade_in:
                self.prompt_alpha += fade_speed
                if self.prompt_alpha >= 255:
                    self.prompt_alpha = 255
                    self.prompt_fade_in = False
            else:
                self.prompt_alpha -= fade_speed
                if self.prompt_alpha <= 100:
                    self.prompt_alpha = 100
                    self.prompt_fade_in = True
        
        # Update background particles
        self._update_particles(dt)
    
    def _update_particles(self, dt: float) -> None:
        """Update background particle positions."""
        for particle in self.particles:
            # Move particle upward
            particle['y'] -= particle['speed'] * dt
            
            # Wrap around when reaching top
            if particle['y'] < -particle['size']:
                particle['y'] = self.game.logical_size[1] + particle['size']
                particle['x'] = pygame.time.get_ticks() % self.game.logical_size[0]
    
    def draw(self, surface: pygame.Surface) -> None:
        """
        Render the scene.
        
        Args:
            surface: Surface to draw on
        """
        # Clear background
        surface.fill(self.bg_color)
        
        # Draw background particles
        self._draw_particles(surface)
        
        # Draw title with scaling effect
        if self.title_font and self.logo_scale > 0:
            # Create title surface
            title_surface = self.title_font.render(self.title_text, True, self.title_color)
            
            # Apply scaling if still in intro
            if self.logo_scale < 1.0:
                width = int(title_surface.get_width() * self.logo_scale)
                height = int(title_surface.get_height() * self.logo_scale)
                if width > 0 and height > 0:
                    title_surface = pygame.transform.scale(title_surface, (width, height))
            
            # Center and draw title
            title_rect = title_surface.get_rect()
            title_rect.centerx = surface.get_width() // 2
            title_rect.centery = 50 + self.title_offset_y
            surface.blit(title_surface, title_rect)
        
        # Draw subtitle (after intro)
        if self.subtitle_font and self.intro_complete:
            subtitle_surface = self.subtitle_font.render(self.subtitle_text, True, self.subtitle_color)
            subtitle_rect = subtitle_surface.get_rect()
            subtitle_rect.centerx = surface.get_width() // 2
            subtitle_rect.centery = 75
            surface.blit(subtitle_surface, subtitle_rect)
        
        # Draw prompt (with fade effect)
        if self.prompt_font and self.intro_complete:
            prompt_surface = self.prompt_font.render(self.prompt_text, True, self.prompt_color)
            prompt_surface.set_alpha(int(self.prompt_alpha))
            prompt_rect = prompt_surface.get_rect()
            prompt_rect.centerx = surface.get_width() // 2
            prompt_rect.centery = 130
            surface.blit(prompt_surface, prompt_rect)
        
        # Draw version in corner
        if self.subtitle_font:
            version_surface = self.subtitle_font.render(self.version_text, True, (100, 100, 120))
            surface.blit(version_surface, (5, surface.get_height() - 15))
        
        # Draw decorative frame
        self._draw_frame(surface)
    
    def _draw_particles(self, surface: pygame.Surface) -> None:
        """Draw background particle effects."""
        for particle in self.particles:
            # Calculate color based on brightness
            brightness = int(particle['brightness'] * 100)
            color = (brightness, brightness, brightness + 20)
            
            # Draw particle
            pygame.draw.circle(
                surface,
                color,
                (int(particle['x']), int(particle['y'])),
                particle['size']
            )
    
    def _draw_frame(self, surface: pygame.Surface) -> None:
        """Draw decorative frame around screen edges."""
        frame_color = (80, 80, 100)
        frame_width = 2
        
        # Top and bottom borders with pattern
        for x in range(0, surface.get_width(), 20):
            # Top
            pygame.draw.line(surface, frame_color, (x, 0), (x + 10, 0), frame_width)
            # Bottom
            pygame.draw.line(surface, frame_color, 
                           (x, surface.get_height() - 1), 
                           (x + 10, surface.get_height() - 1), frame_width)
        
        # Left and right borders with pattern
        for y in range(0, surface.get_height(), 20):
            # Left
            pygame.draw.line(surface, frame_color, (0, y), (0, y + 10), frame_width)
            # Right
            pygame.draw.line(surface, frame_color,
                           (surface.get_width() - 1, y),
                           (surface.get_width() - 1, y + 10), frame_width)
        
        # Corner decorations
        corner_size = 15
        corners = [
            (0, 0),  # Top-left
            (surface.get_width() - corner_size, 0),  # Top-right
            (0, surface.get_height() - corner_size),  # Bottom-left
            (surface.get_width() - corner_size, surface.get_height() - corner_size)  # Bottom-right
        ]
        
        for cx, cy in corners:
            # Draw corner triangle
            if cx == 0 and cy == 0:  # Top-left
                points = [(cx, cy), (cx + corner_size, cy), (cx, cy + corner_size)]
            elif cx > 0 and cy == 0:  # Top-right
                points = [(cx + corner_size, cy), (cx, cy), (cx + corner_size, cy + corner_size)]
            elif cx == 0 and cy > 0:  # Bottom-left
                points = [(cx, cy + corner_size), (cx + corner_size, cy + corner_size), (cx, cy)]
            else:  # Bottom-right
                points = [(cx + corner_size, cy + corner_size), (cx, cy + corner_size), (cx + corner_size, cy)]
            
            pygame.draw.lines(surface, frame_color, True, points, frame_width)
    
    def _start_game(self) -> None:
        """Transition to the main game."""
        if self.transitioning:
            return
        
        self.transitioning = True
        
        # Play confirmation sound
        try:
            sound = resources.load_sound("game_start.wav", volume=0.7)
            sound.play()
        except:
            pass
        
        # Transition to field scene
        from engine.scenes.field_scene import FieldScene
        
        # Create Field Scene and switch
        field_scene = FieldScene(self.game)
        self.game.replace_scene(field_scene)
        
        # Load player house and spawn at bed (fails gracefully via MapLoader)
        try:
            field_scene.enter(map_id="player_house", spawn_point="bed")
        except Exception as e:
            print(f"Warning: Could not enter player_house: {e}")
        
        # DEAKTIVIERT: Starte awakening-Cutscene - blockiert Player-Bewegung
        # if hasattr(self.game, 'cutscene_manager'):
        #     self.game.cutscene_manager.play('awakening', on_complete=self._on_awakening_complete)
        # else:
        #     # Fallback: Direkt zum Spiel
        print("Cutscene übersprungen - Player kann sich sofort bewegen")
    
    def _on_awakening_complete(self):
        """Callback wenn awakening-Cutscene beendet ist"""
        print("Awakening-Cutscene beendet - Spiel kann beginnen")
        # Hier könnte man weitere Story-Events triggern
