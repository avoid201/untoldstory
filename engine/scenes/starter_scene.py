"""
Starter selection scene for Untold Story.
Player chooses their first monster from Professor Budde's fossils.
"""

import pygame
from typing import Optional, List
from engine.core.scene_base import Scene
from engine.core.config import LOGICAL_WIDTH, LOGICAL_HEIGHT, Colors
from engine.systems.monster_instance import MonsterInstance
from engine.ui.dialogue import DialogueBox
# from engine.ui.transitions import TransitionType  # Temporarily disabled


class StarterScene(Scene):
    """Scene for selecting starter monster."""
    
    def __init__(self, game):
        super().__init__(game)
        
        # UI components
        self.dialogue = DialogueBox(game)
        
        # Starter monsters data (E-rank fossils at level 5)
        self.starters = []
        self.starter_data = [
            {
                'id': 1,
                'name': 'Glutkohle',
                'types': ['Fire'],
                'description': 'Ein feuriges Fossil aus der Kohlezeit. Heizt ordentlich ein!',
                'color': (255, 100, 50)
            },
            {
                'id': 2,
                'name': 'Tropfstein',
                'types': ['Water'],
                'description': 'Ein uraltes Wasser-Fossil. Tropft schon seit Jahrmillionen!',
                'color': (50, 150, 255)
            },
            {
                'id': 3,
                'name': 'Lehmling',
                'types': ['Earth'],
                'description': 'Ein stabiles Erd-Fossil. Steht fest wie die Zeche Zollverein!',
                'color': (150, 100, 50)
            },
            {
                'id': 4,
                'name': 'Windei',
                'types': ['Air'],
                'description': 'Ein luftiges Fossil. Weht durch die Schächte wie\'n Grubenwetter!',
                'color': (200, 200, 255)
            }
        ]
        
        # Selection state
        self.selected_index = 0
        self.state = 'intro'  # intro, selecting, confirming, done
        self.confirm_choice = False
        
        # Visual settings
        self.card_width = 60
        self.card_height = 80
        self.card_spacing = 10
        
        # Animation
        self.hover_offset = 0
        self.hover_timer = 0
        
        # Font
        self.font = pygame.font.Font(None, 12)
        self.big_font = pygame.font.Font(None, 16)
        
    def on_enter(self, **kwargs):
        """Initialize the scene."""
        # Create starter monster instances
        self.starters = []
        for data in self.starter_data:
            # For now, always use fallback since get_monster_species doesn't exist yet
            monster = self._create_fallback_starter(data)
            self.starters.append(monster)
        
        # Start with intro
        self.state = 'intro'
        self.show_intro_dialogue()
        
        # Transition in (temporarily disabled)
        # self.game.transition_manager.start(TransitionType.FADE_IN, duration=0.5)
    
    def _create_fallback_starter(self, data):
        """Create a basic starter if not in database."""
        from engine.systems.monster_instance import MonsterSpecies, MonsterInstance
        from engine.systems.stats import BaseStats, GrowthCurve
        from engine.systems.monster_instance import MonsterRank
        
        # Create a basic species for fallback
        base_stats = BaseStats(
            hp=20, attacker=8, defender=6, mag=6, res=6, spd=7
        )
        
        species = MonsterSpecies(
            id=data['id'],
            name=data['name'],
            era='past',
            rank=MonsterRank.E,
            types=data['types'],
            base_stats=base_stats,
            growth_curve=GrowthCurve.NORMAL,
            base_exp_yield=50,
            capture_rate=200,
            traits=[],
            learnset=[],
            evolution=None,
            description=f"Ein {data['types'][0]}-Fossil aus der Kohlezeit."
        )
        
        # Create monster instance
        monster = MonsterInstance(species, level=5)
        
        return monster
    
    def show_intro_dialogue(self):
        """Show Professor Budde's introduction."""
        messages = [
            "Prof. Budde: Willkommen in meinem Labor!",
            "Ich bin Professor Budde, der führende Fossilienforscher im Ruhrgebiet.",
            "Durch meine Technologie kann ich uralte Monster-Fossilien wiederbeleben!",
            "Diese vier Fossilien hier stammen aus der Kohlezeit.",
            "Such dir eins aus - das wird dein Partner auf deiner Reise!",
            "Aber wähl weise, Jung! Das is 'ne Entscheidung fürs Leben!"
        ]
        
        self.dialogue.queue_messages(messages)
        self.dialogue.show()
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle input events."""
        # Let dialogue handle input first if active
        if self.dialogue.is_active():
            if self.dialogue.handle_event(event):
                # Check if dialogue finished
                if not self.dialogue.is_active() and self.state == 'intro':
                    self.state = 'selecting'
                return True
        
        if event.type == pygame.KEYDOWN:
            if self.state == 'selecting':
                if event.key == pygame.K_a:  # Left
                    self.selected_index = (self.selected_index - 1) % 4
                    self.hover_timer = 0
                    
                elif event.key == pygame.K_d:  # Right
                    self.selected_index = (self.selected_index + 1) % 4
                    self.hover_timer = 0
                    
                elif event.key in [pygame.K_e, pygame.K_RETURN, pygame.K_SPACE]:  # Confirm
                    self.state = 'confirming'
                    self.show_confirm_dialogue()
                    
            elif self.state == 'confirming':
                if self.dialogue.is_active():
                    self.dialogue.handle_event(event)
                elif self.confirm_choice:
                    if event.key in [pygame.K_e, pygame.K_RETURN, pygame.K_SPACE]:
                        # YES - Choose this starter
                        self.choose_starter()
                    elif event.key in [pygame.K_q, pygame.K_ESCAPE]:
                        # NO - Go back to selection
                        self.state = 'selecting'
                        self.confirm_choice = False
            
            return True
        
        return False
    
    def show_confirm_dialogue(self):
        """Show confirmation dialogue for selected starter."""
        starter = self.starters[self.selected_index]
        data = self.starter_data[self.selected_index]
        
        messages = [
            f"Prof. Budde: Ah, {data['name']}! Gute Wahl!",
            data['description'],
            f"Bist du sicher, dass du {data['name']} als Partner willst?",
            "[E] Ja, ich will {data['name']}!  [Q] Nee, lass mich nochmal gucken."
        ]
        
        self.dialogue.queue_messages(messages)
        self.dialogue.show()
        self.confirm_choice = True
    
    def choose_starter(self):
        """Finalize starter choice and add to party."""
        starter = self.starters[self.selected_index]
        data = self.starter_data[self.selected_index]
        
        # Add to party
        success, message = self.game.party_manager.add_to_party(starter)
        
        if success:
            # Set story flags
            self.game.story_manager.set_flag('has_starter', True)
            self.game.story_manager.set_flag('starter_choice', data['id'])
            self.game.story_manager.set_flag('professor_intro_done', True)
            
            # Show success message
            messages = [
                f"Prof. Budde: Perfekt! {data['name']} gehört jetzt zu dir!",
                "Pass gut auf dein Monster auf!",
                "Dein Rivale Klaus wartet schon draußen auf dich.",
                "Er hat sich auch ein Fossil-Monster ausgesucht.",
                "Zeig ihm mal, wat du drauf hast!",
                "Viel Erfolg auf deiner Reise, Jung!"
            ]
            
            self.dialogue.queue_messages(messages)
            self.dialogue.show()
            self.state = 'done'
        else:
            # Should not happen, but handle error
            self.dialogue.queue_messages([
                "Prof. Budde: Hmm, irgendwat is schiefgelaufen...",
                "Versuch's nochmal!"
            ])
            self.dialogue.show()
            self.state = 'selecting'
    
    def update(self, dt: float):
        """Update the scene."""
        # Update dialogue
        if self.dialogue.is_active():
            self.dialogue.update(dt)
            
            # Check if we should transition after final dialogue
            if self.state == 'done' and not self.dialogue.is_active():
                # Transition to field scene
                self.game.transition_manager.start(TransitionType.FADE_OUT, duration=0.5)
                # Wait a moment then switch scene
                if not hasattr(self, 'exit_timer'):
                    self.exit_timer = 0
                self.exit_timer += dt
                if self.exit_timer > 0.6:
                    self.game.pop_scene()  # Return to field
        
        # Update hover animation
        if self.state == 'selecting':
            self.hover_timer += dt
            self.hover_offset = pygame.math.Vector2(0, -abs(pygame.math.sin(self.hover_timer * 3)) * 5)
    
    def draw(self, surface: pygame.Surface):
        """Draw the scene."""
        # Background - Professor's lab
        surface.fill((40, 35, 30))  # Dark brown lab
        
        # Draw lab details
        self._draw_lab_background(surface)
        
        # Draw starter cards if selecting
        if self.state in ['selecting', 'confirming']:
            self._draw_starter_cards(surface)
        
        # Draw dialogue box
        if self.dialogue.is_active():
            self.dialogue.draw(surface)
        
        # Draw title
        if self.state != 'done':
            title = self.big_font.render("Wähle dein Starter-Monster!", True, Colors.WHITE)
            title_rect = title.get_rect(center=(LOGICAL_WIDTH // 2, 20))
            surface.blit(title, title_rect)
    
    def _draw_lab_background(self, surface: pygame.Surface):
        """Draw laboratory background elements."""
        # Draw some lab equipment as rectangles
        
        # Fossil machine
        pygame.draw.rect(surface, (60, 55, 50), (10, 40, 30, 40))
        pygame.draw.rect(surface, (80, 75, 70), (10, 40, 30, 40), 2)
        
        # Computer
        pygame.draw.rect(surface, (30, 30, 40), (LOGICAL_WIDTH - 40, 40, 30, 20))
        pygame.draw.rect(surface, (100, 200, 255), (LOGICAL_WIDTH - 38, 42, 26, 16))
        
        # Table
        pygame.draw.rect(surface, (90, 70, 50), (0, 100, LOGICAL_WIDTH, 20))
        pygame.draw.rect(surface, (70, 50, 30), (0, 100, LOGICAL_WIDTH, 20), 2)
    
    def _draw_starter_cards(self, surface: pygame.Surface):
        """Draw the starter selection cards."""
        # Calculate total width
        total_width = (self.card_width * 4) + (self.card_spacing * 3)
        start_x = (LOGICAL_WIDTH - total_width) // 2
        y = 50
        
        for i, (monster, data) in enumerate(zip(self.starters, self.starter_data)):
            x = start_x + (self.card_width + self.card_spacing) * i
            
            # Apply hover effect to selected card
            offset_y = 0
            if i == self.selected_index and self.state == 'selecting':
                offset_y = self.hover_offset.y
            
            # Draw card background
            card_rect = pygame.Rect(x, y + offset_y, self.card_width, self.card_height)
            
            # Highlight selected card
            if i == self.selected_index:
                pygame.draw.rect(surface, Colors.YELLOW, card_rect.inflate(4, 4))
            
            # Card background
            pygame.draw.rect(surface, (50, 45, 40), card_rect)
            pygame.draw.rect(surface, Colors.WHITE, card_rect, 2)
            
            # Draw monster sprite (try real sprite first, fallback to colored rectangle)
            sprite_rect = pygame.Rect(x + 10, y + 5 + offset_y, 40, 40)
            
            # Try to get real monster sprite
            monster_sprite = None
            if hasattr(self.game, 'sprite_manager') and self.game.sprite_manager:
                sprite_mgr = self.game.sprite_manager
                sprite_key = str(data.get('id', i + 1))
                if sprite_key in sprite_mgr.monster_sprites:
                    monster_sprite = sprite_mgr.monster_sprites[sprite_key]
                    # Scale sprite to fit card
                    if monster_sprite.get_size() != (40, 40):
                        monster_sprite = pygame.transform.scale(monster_sprite, (40, 40))
            
            if monster_sprite:
                # Draw real monster sprite
                surface.blit(monster_sprite, sprite_rect)
            else:
                # Fallback to colored rectangle
                pygame.draw.rect(surface, data['color'], sprite_rect)
                pygame.draw.rect(surface, (0, 0, 0), sprite_rect, 2)
                
                # Add monster ID for debugging
                try:
                    font = pygame.font.Font(None, 16)
                    id_text = font.render(str(data.get('id', i + 1)), True, (255, 255, 255))
                    text_rect = id_text.get_rect(center=sprite_rect.center)
                    surface.blit(id_text, text_rect)
                except:
                    pass
            
            # Draw monster name
            name_text = self.font.render(data['name'], True, Colors.WHITE)
            name_rect = name_text.get_rect(centerx=x + self.card_width // 2, 
                                          y=y + 48 + offset_y)
            surface.blit(name_text, name_rect)
            
            # Draw type
            type_text = self.font.render(data['types'][0], True, data['color'])
            type_rect = type_text.get_rect(centerx=x + self.card_width // 2,
                                          y=y + 60 + offset_y)
            surface.blit(type_text, type_rect)
            
            # Draw level
            level_text = self.font.render("Lv.5", True, Colors.WHITE)
            level_rect = level_text.get_rect(centerx=x + self.card_width // 2,
                                           y=y + 70 + offset_y)
            surface.blit(level_text, level_rect)
        
        # Draw selection hint
        if self.state == 'selecting':
            hint = self.font.render("[A/D] Wählen  [E] Bestätigen", True, Colors.WHITE)
            hint_rect = hint.get_rect(center=(LOGICAL_WIDTH // 2, LOGICAL_HEIGHT - 20))
            surface.blit(hint, hint_rect)
