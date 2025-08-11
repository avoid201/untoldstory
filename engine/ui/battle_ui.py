"""
Battle UI system for Untold Story.
Handles all battle interface elements including menus, HP bars, and animations.
"""

import pygame
from dataclasses import dataclass
from typing import Optional, List, Tuple, Dict, Any
from enum import Enum, auto

from engine.core.config import (
    LOGICAL_WIDTH, LOGICAL_HEIGHT, 
    Colors, Fonts, UI
)


class BattleMenuState(Enum):
    """States for the battle menu system."""
    MAIN = auto()          # Fight/Tame/Item/Run
    MOVE_SELECT = auto()   # Selecting a move
    TARGET_SELECT = auto() # Selecting target
    ITEM_SELECT = auto()   # Selecting item
    PARTY_SELECT = auto()  # Selecting party member
    WAITING = auto()       # Waiting for animations
    MESSAGE = auto()       # Showing battle message


@dataclass
class BattleSprite:
    """Container for a battle sprite."""
    surface: pygame.Surface
    position: Tuple[int, int]
    is_player_side: bool
    shake_offset: Tuple[int, int] = (0, 0)
    flash_timer: float = 0
    fade_alpha: int = 255


class BattleUI:
    """Main battle UI manager."""
    
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.Font(None, 12)
        self.big_font = pygame.font.Font(None, 16)
        
        # Menu state
        self.menu_state = BattleMenuState.MAIN
        self.menu_index = 0
        self.move_index = 0
        self.target_index = 0
        self.item_index = 0
        
        # Battle message system
        self.message_queue: List[str] = []
        self.current_message = ""
        self.message_timer = 0
        self.message_speed = 30  # chars per second
        self.message_progress = 0
        
        # Animation timers
        self.hp_animations: Dict[str, Dict] = {}  # actor_id -> {current, target, speed}
        self.shake_timers: Dict[str, float] = {}
        self.flash_timers: Dict[str, float] = {}
        
        # UI element positions
        self.player_hp_pos = (LOGICAL_WIDTH - 100, LOGICAL_HEIGHT - 50)
        self.enemy_hp_pos = (10, 10)
        self.menu_pos = (10, LOGICAL_HEIGHT - 60)
        self.message_box_pos = (10, LOGICAL_HEIGHT - 40)
        
        # Battle sprites
        self.sprites: Dict[str, BattleSprite] = {}
        
    def init_battle(self, player_monsters: List, enemy_monsters: List):
        """Initialize UI for a new battle."""
        self.sprites.clear()
        self.hp_animations.clear()
        
        # Position player monsters (right side)
        for i, monster in enumerate(player_monsters):
            if monster and monster.current_hp > 0:
                sprite = self._create_monster_sprite(monster, True)
                sprite.position = (LOGICAL_WIDTH - 60, 80 + i * 30)
                self.sprites[f"player_{i}"] = sprite
                
                # Init HP animation
                self.hp_animations[f"player_{i}"] = {
                    'current': monster.current_hp,
                    'target': monster.current_hp,
                    'max': monster.max_hp,
                    'speed': 2.0
                }
        
        # Position enemy monsters (left side)
        for i, monster in enumerate(enemy_monsters):
            if monster and monster.current_hp > 0:
                sprite = self._create_monster_sprite(monster, False)
                sprite.position = (40, 30 + i * 30)
                self.sprites[f"enemy_{i}"] = sprite
                
                # Init HP animation
                self.hp_animations[f"enemy_{i}"] = {
                    'current': monster.current_hp,
                    'target': monster.current_hp,
                    'max': monster.max_hp,
                    'speed': 2.0
                }
    
    def _create_monster_sprite(self, monster, is_player_side: bool) -> BattleSprite:
        """Create a battle sprite for a monster."""
        # Try to get the actual monster sprite from the game's sprite manager
        if hasattr(self.game, 'sprite_manager') and self.game.sprite_manager:
            sprite_mgr = self.game.sprite_manager
            sprite_key = str(monster.species_id) if hasattr(monster, 'species_id') else str(monster.id)
            
            if sprite_key in sprite_mgr.monster_sprites:
                # Use the actual monster sprite
                monster_sprite = sprite_mgr.monster_sprites[sprite_key]
                print(f"Battle UI: Using real sprite for monster {sprite_key}")
                return BattleSprite(monster_sprite, (0, 0), is_player_side)
        
        # Fallback: Create a minimal placeholder surface
        size = 32 if is_player_side else 40
        surface = pygame.Surface((size, size))
        surface.fill((128, 128, 128))  # Gray placeholder
        
        # Add monster ID for debugging
        try:
            font = pygame.font.Font(None, 12)
            monster_id = getattr(monster, 'species_id', getattr(monster, 'id', '?'))
            id_text = font.render(str(monster_id), True, (255, 255, 255))
            text_rect = id_text.get_rect(center=(size//2, size//2))
            surface.blit(id_text, text_rect)
        except:
            pass
        
        print(f"Battle UI: Using placeholder for monster {getattr(monster, 'id', 'Unknown')}")
        return BattleSprite(surface, (0, 0), is_player_side)
    
    def show_message(self, message: str, wait: bool = True):
        """Add a message to the battle log."""
        self.message_queue.append(message)
        if not self.current_message:
            self._next_message()
    
    def _next_message(self):
        """Process next message in queue."""
        if self.message_queue:
            self.current_message = self.message_queue.pop(0)
            self.message_progress = 0
            self.message_timer = 0
            self.menu_state = BattleMenuState.MESSAGE
        else:
            self.current_message = ""
            self.menu_state = BattleMenuState.MAIN
    
    def set_hp(self, actor_id: str, new_hp: int):
        """Set target HP for animation."""
        if actor_id in self.hp_animations:
            self.hp_animations[actor_id]['target'] = max(0, new_hp)
    
    def shake_sprite(self, actor_id: str, duration: float = 0.3):
        """Start shake animation for sprite."""
        self.shake_timers[actor_id] = duration
    
    def flash_sprite(self, actor_id: str, duration: float = 0.2):
        """Start flash animation for sprite."""
        self.flash_timers[actor_id] = duration
    
    def update(self, dt: float):
        """Update all UI animations."""
        # Update HP animations
        for actor_id, hp_data in self.hp_animations.items():
            if hp_data['current'] != hp_data['target']:
                diff = hp_data['target'] - hp_data['current']
                change = min(abs(diff), hp_data['speed'] * dt * 60)
                if diff > 0:
                    hp_data['current'] += change
                else:
                    hp_data['current'] -= change
                    
                if abs(hp_data['current'] - hp_data['target']) < 1:
                    hp_data['current'] = hp_data['target']
        
        # Update shake animations
        for actor_id in list(self.shake_timers.keys()):
            self.shake_timers[actor_id] -= dt
            if self.shake_timers[actor_id] <= 0:
                del self.shake_timers[actor_id]
                if actor_id in self.sprites:
                    self.sprites[actor_id].shake_offset = (0, 0)
            else:
                # Apply shake
                import random
                if actor_id in self.sprites:
                    self.sprites[actor_id].shake_offset = (
                        random.randint(-2, 2),
                        random.randint(-2, 2)
                    )
        
        # Update flash animations  
        for actor_id in list(self.flash_timers.keys()):
            self.flash_timers[actor_id] -= dt
            if self.flash_timers[actor_id] <= 0:
                del self.flash_timers[actor_id]
        
        # Update message typewriter
        if self.current_message and self.menu_state == BattleMenuState.MESSAGE:
            self.message_timer += dt
            chars_to_show = int(self.message_timer * self.message_speed)
            self.message_progress = min(chars_to_show, len(self.current_message))
    
    def draw(self, surface: pygame.Surface, battle_state):
        """Draw all battle UI elements."""
        # Clear with battle background color
        surface.fill((50, 100, 50))  # Grass green for now
        
        # Note: Monster sprites are now drawn by BattleScene._draw_monster_sprites()
        # This method only draws UI elements (HP bars, menus, messages)
        
        # Draw HP bars
        self._draw_hp_bars(surface)
        
        # Draw menu or message
        if self.menu_state == BattleMenuState.MESSAGE:
            self._draw_message_box(surface)
        else:
            self._draw_battle_menu(surface, battle_state)
    
    def _draw_hp_bars(self, surface: pygame.Surface):
        """Draw HP bars for all monsters."""
        for actor_id, hp_data in self.hp_animations.items():
            if actor_id.startswith("player"):
                pos = self.player_hp_pos
            else:
                pos = self.enemy_hp_pos
                
            # Offset for multiple monsters
            idx = int(actor_id.split("_")[1])
            y_offset = idx * 25
            
            # Draw HP bar background
            bar_rect = pygame.Rect(pos[0], pos[1] + y_offset, 80, 6)
            pygame.draw.rect(surface, (50, 50, 50), bar_rect)
            
            # Draw HP fill
            hp_percent = hp_data['current'] / hp_data['max'] if hp_data['max'] > 0 else 0
            fill_width = int(78 * hp_percent)
            
            # Color based on HP percentage
            if hp_percent > 0.5:
                color = (50, 200, 50)
            elif hp_percent > 0.25:
                color = (255, 200, 0)
            else:
                color = (255, 50, 50)
            
            if fill_width > 0:
                fill_rect = pygame.Rect(pos[0] + 1, pos[1] + y_offset + 1, fill_width, 4)
                pygame.draw.rect(surface, color, fill_rect)
            
            # Draw HP text
            hp_text = f"{int(hp_data['current'])}/{hp_data['max']}"
            text_surface = self.font.render(hp_text, True, (255, 255, 255))
            surface.blit(text_surface, (pos[0], pos[1] + y_offset + 8))
    
    def _draw_battle_menu(self, surface: pygame.Surface, battle_state):
        """Draw the battle command menu."""
        # Menu background
        menu_rect = pygame.Rect(self.menu_pos[0], self.menu_pos[1], 
                                LOGICAL_WIDTH - 20, 50)
        pygame.draw.rect(surface, (20, 20, 40), menu_rect)
        pygame.draw.rect(surface, (255, 255, 255), menu_rect, 1)
        
        if self.menu_state == BattleMenuState.MAIN:
            # Main menu options
            options = ["Angriff", "Zähmen", "Item", "Flucht"]
            for i, option in enumerate(options):
                x = self.menu_pos[0] + 10 + (i % 2) * 60
                y = self.menu_pos[1] + 10 + (i // 2) * 15
                
                color = (255, 255, 100) if i == self.menu_index else (255, 255, 255)
                text = self.font.render(option, True, color)
                surface.blit(text, (x, y))
                
                if i == self.menu_index:
                    # Draw cursor
                    pygame.draw.polygon(surface, (255, 255, 100),
                                      [(x - 8, y + 3), (x - 3, y + 6), (x - 8, y + 9)])
        
        elif self.menu_state == BattleMenuState.MOVE_SELECT:
            # Move selection
            if battle_state and battle_state.player_team:
                monster = battle_state.player_team[0]  # Active monster
                if monster:
                    for i, move in enumerate(monster.moves[:4]):
                        x = self.menu_pos[0] + 10 + (i % 2) * 80
                        y = self.menu_pos[1] + 10 + (i // 2) * 15
                        
                        color = (255, 255, 100) if i == self.move_index else (255, 255, 255)
                        
                        # Show move name and PP
                        move_data = self.game.resources.get_move(move.move_id)
                        if move_data:
                            text = f"{move_data.name} {move.current_pp}/{move.max_pp}"
                            text_surface = self.font.render(text, True, color)
                            surface.blit(text_surface, (x, y))
                            
                            if i == self.move_index:
                                pygame.draw.polygon(surface, (255, 255, 100),
                                                  [(x - 8, y + 3), (x - 3, y + 6), (x - 8, y + 9)])
    
    def _draw_message_box(self, surface: pygame.Surface):
        """Draw battle message box."""
        # Message box background
        msg_rect = pygame.Rect(self.message_box_pos[0], self.message_box_pos[1],
                              LOGICAL_WIDTH - 20, 30)
        pygame.draw.rect(surface, (20, 20, 40), msg_rect)
        pygame.draw.rect(surface, (255, 255, 255), msg_rect, 1)
        
        # Draw message text with typewriter effect
        if self.current_message:
            display_text = self.current_message[:self.message_progress]
            
            # Word wrap
            words = display_text.split(' ')
            lines = []
            current_line = ""
            
            for word in words:
                test_line = current_line + " " + word if current_line else word
                if self.font.size(test_line)[0] < LOGICAL_WIDTH - 40:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
            
            if current_line:
                lines.append(current_line)
            
            # Draw lines
            for i, line in enumerate(lines[:2]):  # Max 2 lines
                text_surface = self.font.render(line, True, (255, 255, 255))
                surface.blit(text_surface, 
                           (self.message_box_pos[0] + 5, 
                            self.message_box_pos[1] + 5 + i * 12))
            
            # Show continue prompt if message complete
            if self.message_progress >= len(self.current_message):
                prompt = "▼"
                prompt_surface = self.font.render(prompt, True, (255, 255, 100))
                surface.blit(prompt_surface,
                           (LOGICAL_WIDTH - 25, self.message_box_pos[1] + 20))
    
    def handle_input(self, action: str, battle_state) -> Optional[Dict[str, Any]]:
        """Handle input and return action if confirmed."""
        if self.menu_state == BattleMenuState.MESSAGE:
            if action == 'confirm' and self.message_progress >= len(self.current_message):
                self._next_message()
                return None
        
        elif self.menu_state == BattleMenuState.MAIN:
            if action == 'up':
                self.menu_index = (self.menu_index - 2) % 4
            elif action == 'down':
                self.menu_index = (self.menu_index + 2) % 4
            elif action == 'left':
                if self.menu_index % 2 == 1:
                    self.menu_index -= 1
            elif action == 'right':
                if self.menu_index % 2 == 0:
                    self.menu_index += 1
            elif action == 'confirm':
                if self.menu_index == 0:  # Fight
                    self.menu_state = BattleMenuState.MOVE_SELECT
                    self.move_index = 0
                elif self.menu_index == 1:  # Tame
                    if battle_state and battle_state.is_wild:
                        return {'type': 'tame', 'actor': 'player_0'}
                    else:
                        self.show_message("Dat geht nur bei wilden Monstern, Jung!")
                elif self.menu_index == 2:  # Item
                    self.show_message("Items ham wa noch nich, Kollege!")
                elif self.menu_index == 3:  # Run
                    if battle_state and battle_state.is_wild:
                        return {'type': 'flee', 'actor': 'player_0'}
                    else:
                        self.show_message("Aus Trainerkämpfen kannste nich abhauen!")
        
        elif self.menu_state == BattleMenuState.MOVE_SELECT:
            if action == 'up':
                self.move_index = (self.move_index - 2) % 4
            elif action == 'down':
                self.move_index = (self.move_index + 2) % 4
            elif action == 'left':
                if self.move_index % 2 == 1:
                    self.move_index -= 1
            elif action == 'right':
                if self.move_index % 2 == 0:
                    self.move_index += 1
            elif action == 'confirm':
                # Return attack action
                if battle_state and battle_state.player_team:
                    monster = battle_state.player_team[0]
                    if monster and self.move_index < len(monster.moves):
                        move = monster.moves[self.move_index]
                        self.menu_state = BattleMenuState.MAIN
                        return {
                            'type': 'attack',
                            'actor': 'player_0',
                            'move_id': move.move_id,
                            'targets': ['enemy_0']  # Auto-target for now
                        }
            elif action == 'back':
                self.menu_state = BattleMenuState.MAIN
        
        return None
