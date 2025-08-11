"""
Dialogue System for Untold Story
Handles dialogue boxes with typewriter effect, paging, and choices
"""

import pygame
from typing import List, Optional, Tuple, Callable, Dict, Any
from enum import Enum
from dataclasses import dataclass


class DialogueState(Enum):
    """States for dialogue box."""
    TYPING = "typing"
    WAITING = "waiting"
    CHOICE = "choice"
    CLOSING = "closing"
    CLOSED = "closed"


@dataclass
class DialoguePage:
    """Single page of dialogue."""
    text: str
    speaker: Optional[str] = None
    portrait: Optional[str] = None  # Path to portrait image
    speed: float = 30.0  # Characters per second
    auto_advance: bool = False
    auto_delay: float = 2.0  # Seconds before auto-advance


@dataclass
class DialogueChoice:
    """Choice option in dialogue."""
    text: str
    value: Any = None
    enabled: bool = True
    tooltip: Optional[str] = None


class DialogueBox:
    """
    Dialogue box UI component with typewriter effect and choices.
    """
    
    def __init__(self,
                 x: int = 10,
                 y: int = 120,
                 width: int = 300,
                 height: int = 50,
                 padding: int = 8) -> None:
        """
        Initialize the dialogue box.
        
        Args:
            x: X position on screen
            y: Y position on screen
            width: Box width in pixels
            height: Box height in pixels
            padding: Internal padding
        """
        # Position and size
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.padding = padding
        
        # Visual settings
        self.bg_color = (20, 20, 30, 230)  # Dark blue, semi-transparent
        self.border_color = (200, 200, 220)
        self.text_color = (255, 255, 255)
        self.speaker_color = (255, 220, 100)
        self.disabled_color = (128, 128, 128)
        self.border_width = 2
        
        # Font settings
        self.font: Optional[pygame.font.Font] = None
        self.speaker_font: Optional[pygame.font.Font] = None
        self._load_fonts()
        
        # Dialogue state
        self.state = DialogueState.CLOSED
        self.pages: List[DialoguePage] = []
        self.current_page_index = 0
        self.current_page: Optional[DialoguePage] = None
        
        # Typewriter effect
        self.displayed_text = ""
        self.full_text = ""
        self.char_index = 0
        self.type_timer = 0.0
        self.type_speed = 30.0  # Characters per second
        
        # Choice menu
        self.choices: List[DialogueChoice] = []
        self.selected_choice = 0
        self.choice_callback: Optional[Callable] = None
        
        # Animation
        self.visible = False
        self.animation_timer = 0.0
        self.target_height = height
        self.current_height = 0
        
        # Auto-advance
        self.auto_timer = 0.0
        
        # Sound effects (paths)
        self.type_sound: Optional[str] = "text_blip.wav"
        self.advance_sound: Optional[str] = "menu_select.wav"
        self.choice_sound: Optional[str] = "menu_move.wav"
        
        # Continue indicator
        self.show_continue = False
        self.continue_blink_timer = 0.0
    
    def _load_fonts(self) -> None:
        """Load fonts for dialogue rendering."""
        try:
            self.font = pygame.font.Font(None, 14)
            self.speaker_font = pygame.font.Font(None, 16)
        except:
            print("Warning: Could not load dialogue fonts")
    
    def show_dialogue(self, 
                      pages: List[DialoguePage],
                      callback: Optional[Callable] = None) -> None:
        """
        Display a sequence of dialogue pages.
        
        Args:
            pages: List of dialogue pages to display
            callback: Optional callback when dialogue completes
        """
        if not pages:
            return
        
        self.pages = pages
        self.current_page_index = 0
        self.choice_callback = callback
        self.state = DialogueState.TYPING
        self.visible = True
        
        # Start first page
        self._start_page(self.pages[0])
    
    def show_text(self, 
                  text: str,
                  speaker: Optional[str] = None,
                  callback: Optional[Callable] = None) -> None:
        """
        Display a single text message.
        
        Args:
            text: Text to display
            speaker: Optional speaker name
            callback: Optional callback when complete
        """
        page = DialoguePage(text=text, speaker=speaker)
        self.show_dialogue([page], callback)
    
    def show_choices(self,
                    prompt: str,
                    choices: List[DialogueChoice],
                    callback: Callable) -> None:
        """
        Display a choice menu.
        
        Args:
            prompt: Text prompt before choices
            choices: List of choice options
            callback: Callback with selected choice value
        """
        # Show prompt as dialogue
        page = DialoguePage(text=prompt)
        self.pages = [page]
        self.current_page_index = 0
        self.choices = choices
        self.selected_choice = 0
        self.choice_callback = callback
        self.state = DialogueState.TYPING
        self.visible = True
        
        self._start_page(page)
    
    def _start_page(self, page: DialoguePage) -> None:
        """
        Start displaying a dialogue page.
        
        Args:
            page: DialoguePage to display
        """
        self.current_page = page
        self.full_text = page.text
        self.displayed_text = ""
        self.char_index = 0
        self.type_timer = 0.0
        self.type_speed = page.speed
        self.show_continue = False
        self.auto_timer = 0.0
        
        # Wrap text to fit box
        if self.font:
            self.full_text = self._wrap_text(page.text)
    
    def _wrap_text(self, text: str) -> str:
        """
        Wrap text to fit within dialogue box width.
        
        Args:
            text: Text to wrap
            
        Returns:
            Wrapped text with newlines
        """
        if not self.font:
            return text
        
        words = text.split()
        lines = []
        current_line = []
        
        max_width = self.width - (self.padding * 2)
        
        for word in words:
            # Check if adding this word exceeds width
            test_line = ' '.join(current_line + [word])
            text_width = self.font.size(test_line)[0]
            
            if text_width > max_width and current_line:
                # Start new line
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                current_line.append(word)
        
        # Add remaining words
        if current_line:
            lines.append(' '.join(current_line))
        
        return '\n'.join(lines)
    
    def update(self, dt: float) -> None:
        """
        Update dialogue box state.
        
        Args:
            dt: Delta time in seconds
        """
        if self.state == DialogueState.CLOSED:
            return
        
        # Update animation
        if self.visible and self.current_height < self.target_height:
            self.current_height = min(
                self.target_height,
                self.current_height + self.target_height * 4 * dt
            )
        
        # Update typewriter effect
        if self.state == DialogueState.TYPING:
            self._update_typewriter(dt)
        
        # Update auto-advance
        elif self.state == DialogueState.WAITING and self.current_page:
            if self.current_page.auto_advance:
                self.auto_timer += dt
                if self.auto_timer >= self.current_page.auto_delay:
                    self.advance()
        
        # Update continue indicator blink
        if self.show_continue:
            self.continue_blink_timer += dt
    
    def _update_typewriter(self, dt: float) -> None:
        """
        Update typewriter text animation.
        
        Args:
            dt: Delta time in seconds
        """
        if self.char_index >= len(self.full_text):
            # Finished typing
            self.displayed_text = self.full_text
            
            if self.choices and self.current_page_index >= len(self.pages) - 1:
                # Show choices after last page
                self.state = DialogueState.CHOICE
            else:
                self.state = DialogueState.WAITING
                self.show_continue = True
            return
        
        # Add characters based on speed
        self.type_timer += dt
        chars_to_add = int(self.type_timer * self.type_speed)
        
        if chars_to_add > 0:
            self.type_timer = 0.0
            
            # Add characters
            for _ in range(chars_to_add):
                if self.char_index < len(self.full_text):
                    self.displayed_text += self.full_text[self.char_index]
                    self.char_index += 1
                    
                    # Play type sound occasionally
                    if self.char_index % 3 == 0 and self.type_sound:
                        self._play_sound(self.type_sound)
                else:
                    break
    
    def handle_input(self, event: pygame.event.Event) -> bool:
        """
        Handle input events for the dialogue box.
        
        Args:
            event: pygame event to process
            
        Returns:
            True if event was handled
        """
        if self.state == DialogueState.CLOSED:
            return False
        
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_e, pygame.K_RETURN, pygame.K_SPACE]:
                return self._handle_confirm()
            elif event.key in [pygame.K_q, pygame.K_ESCAPE]:
                return self._handle_cancel()
            elif self.state == DialogueState.CHOICE:
                if event.key in [pygame.K_w, pygame.K_UP]:
                    return self._handle_choice_navigation(-1)
                elif event.key in [pygame.K_s, pygame.K_DOWN]:
                    return self._handle_choice_navigation(1)
        
        return True  # Block input while dialogue is open
    
    def _handle_confirm(self) -> bool:
        """Handle confirm input."""
        if self.state == DialogueState.TYPING:
            # Skip to end of current text
            self.displayed_text = self.full_text
            self.char_index = len(self.full_text)
            
            if self.choices and self.current_page_index >= len(self.pages) - 1:
                self.state = DialogueState.CHOICE
            else:
                self.state = DialogueState.WAITING
                self.show_continue = True
            
        elif self.state == DialogueState.WAITING:
            self.advance()
            
        elif self.state == DialogueState.CHOICE:
            self._select_choice()
        
        return True
    
    def _handle_cancel(self) -> bool:
        """Handle cancel input."""
        if self.state == DialogueState.CHOICE:
            # Cancel closes without selection
            self.close()
        return True
    
    def _handle_choice_navigation(self, direction: int) -> bool:
        """
        Navigate choices.
        
        Args:
            direction: -1 for up, 1 for down
        """
        if not self.choices:
            return False
        
        # Find next enabled choice
        old_selection = self.selected_choice
        for _ in range(len(self.choices)):
            self.selected_choice = (self.selected_choice + direction) % len(self.choices)
            if self.choices[self.selected_choice].enabled:
                break
        
        if old_selection != self.selected_choice:
            self._play_sound(self.choice_sound)
        
        return True
    
    def _select_choice(self) -> None:
        """Select the current choice."""
        if not self.choices or self.selected_choice >= len(self.choices):
            return
        
        choice = self.choices[self.selected_choice]
        if not choice.enabled:
            return
        
        self._play_sound(self.advance_sound)
        
        # Call callback with choice value
        if self.choice_callback:
            self.choice_callback(choice.value)
        
        self.close()
    
    def advance(self) -> None:
        """Advance to the next dialogue page."""
        self.current_page_index += 1
        
        if self.current_page_index >= len(self.pages):
            # End of dialogue
            if self.choices:
                # Show choices
                self.state = DialogueState.CHOICE
            else:
                # Close dialogue
                if self.choice_callback:
                    self.choice_callback(None)
                self.close()
        else:
            # Show next page
            self._play_sound(self.advance_sound)
            self.state = DialogueState.TYPING
            self._start_page(self.pages[self.current_page_index])
    
    def close(self) -> None:
        """Close the dialogue box."""
        self.state = DialogueState.CLOSING
        self.visible = False
        self.current_height = 0
        self.pages = []
        self.choices = []
        self.state = DialogueState.CLOSED
    
    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the dialogue box.
        
        Args:
            surface: Surface to draw on
        """
        if self.state == DialogueState.CLOSED or self.current_height <= 0:
            return
        
        # Create box rect with current animation height
        box_rect = pygame.Rect(self.x, self.y, self.width, int(self.current_height))
        
        # Draw background
        bg_surface = pygame.Surface((self.width, int(self.current_height)), pygame.SRCALPHA)
        bg_surface.fill(self.bg_color)
        surface.blit(bg_surface, (self.x, self.y))
        
        # Draw border
        pygame.draw.rect(surface, self.border_color, box_rect, self.border_width)
        
        # Don't draw text until box is mostly open
        if self.current_height < self.target_height * 0.5:
            return
        
        # Draw speaker name if present
        y_offset = self.padding
        if self.current_page and self.current_page.speaker and self.speaker_font:
            speaker_surface = self.speaker_font.render(
                self.current_page.speaker,
                True,
                self.speaker_color
            )
            surface.blit(speaker_surface, (self.x + self.padding, self.y + y_offset))
            y_offset += 18
        
        # Draw dialogue text
        if self.font and self.displayed_text:
            lines = self.displayed_text.split('\n')
            for line in lines:
                if y_offset + 14 > self.current_height - self.padding:
                    break  # Don't draw text outside box
                
                text_surface = self.font.render(line, True, self.text_color)
                surface.blit(text_surface, (self.x + self.padding, self.y + y_offset))
                y_offset += 14
        
        # Draw choices if in choice state
        if self.state == DialogueState.CHOICE and self.choices:
            self._draw_choices(surface)
        
        # Draw continue indicator
        if self.show_continue and self.state == DialogueState.WAITING:
            self._draw_continue_indicator(surface)
    
    def _draw_choices(self, surface: pygame.Surface) -> None:
        """Draw choice menu."""
        if not self.font:
            return
        
        # Draw choices below main text
        choice_y = self.y + self.height + 5
        
        for i, choice in enumerate(self.choices):
            # Determine colors
            if not choice.enabled:
                color = self.disabled_color
            elif i == self.selected_choice:
                color = self.speaker_color
            else:
                color = self.text_color
            
            # Draw choice marker
            if i == self.selected_choice:
                marker = "▶ "
            else:
                marker = "  "
            
            # Draw choice text
            text = marker + choice.text
            text_surface = self.font.render(text, True, color)
            surface.blit(text_surface, (self.x + self.padding, choice_y))
            
            choice_y += 16
    
    def _draw_continue_indicator(self, surface: pygame.Surface) -> None:
        """Draw blinking continue indicator."""
        # Blink indicator
        if int(self.continue_blink_timer * 2) % 2 == 0:
            indicator = "▼"
            x = self.x + self.width - self.padding - 10
            y = self.y + self.current_height - self.padding - 10
            
            if self.font:
                indicator_surface = self.font.render(indicator, True, self.text_color)
                surface.blit(indicator_surface, (x, y))
    
    def _play_sound(self, sound_path: Optional[str]) -> None:
        """Play a sound effect."""
        if not sound_path:
            return
        
        try:
            from engine.core.resources import resources
            sound = resources.load_sound(sound_path, volume=0.3)
            sound.play()
        except:
            pass  # Ignore sound errors
    
    def is_open(self) -> bool:
        """Check if dialogue is currently open."""
        return self.state != DialogueState.CLOSED