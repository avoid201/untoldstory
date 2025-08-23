"""
Starter Selection Scene für Untold Story
Hier wählt der Spieler sein erstes Monster
"""

import pygame
from engine.core.scene_base import Scene
from engine.ui.dialogue import DialogueBox, DialoguePage
from engine.systems.monster_instance import MonsterInstance
from engine.systems.party import Party
from typing import List, Optional, Callable


class StarterSelectionScene(Scene):
    """Szene für die Starter-Monster-Auswahl"""
    
    def __init__(self, game):
        super().__init__(game)
        self.selected_starter = None
        # Starter-Monster-Definitionen
        self.starter_options = [
            {
                'id': 1,
                'name': 'Feuerstarter',
                'description': 'Ein feuriger Drache',
                'sprite_path': 'monsters/1.png'  # Konsistenter Pfad ohne sprites/ Prefix
            },
            {
                'id': 2,
                'name': 'Wasserstarter',
                'description': 'Ein wässriger Drache',
                'sprite_path': 'monsters/2.png'  # Konsistenter Pfad ohne sprites/ Prefix
            },
            {
                'id': 3,
                'name': 'Pflanzenstarter',
                'description': 'Ein pflanzlicher Drache',
                'sprite_path': 'monsters/3.png'  # Konsistenter Pfad ohne sprites/ Prefix
            }
        ]
        
        # Lade Starter-Sprites
        self.starter_sprites = []
        for starter in self.starter_options:
            try:
                # Versuche zuerst den SpriteManager zu verwenden
                if hasattr(self.game, 'sprite_manager'):
                    sprite = self.game.sprite_manager.load_monster_sprite(str(starter['id']))
                    if sprite:
                        self.starter_sprites.append(sprite)
                        continue
                
                # Fallback: Lade direkt aus der Datei
                sprite = pygame.image.load(f"sprites/{starter['sprite_path']}")
                if sprite.get_size() != (16, 16):
                    sprite = pygame.transform.scale(sprite, (16, 16))
                self.starter_sprites.append(sprite)
            except Exception as e:
                print(f"Fehler beim Laden des Starter-Sprites {starter['name']}: {e}")
                # Erstelle Fallback-Sprite
                fallback = pygame.Surface((16, 16))
                fallback.fill((255, 0, 255))  # Magenta
                self.starter_sprites.append(fallback)
        
        # UI-Elemente
        self.dialogue_box = DialogueBox(game)
        self.selection_arrow = 0  # 0-2 für die drei Starter
        
        # Starte die Starter-Auswahl
        self._show_starter_intro()
    
    def _show_starter_intro(self):
        """Zeigt die Einführung zur Starter-Auswahl"""
        pages = [
            DialoguePage(
                "Hier sind meine neuesten Wiederbelebungen!",
                "Prof. Budde"
            ),
            DialoguePage(
                "Jedes hat seine eigenen Stärken und Schwächen.",
                "Prof. Budde"
            ),
            DialoguePage(
                "Wähle weise - dein Starter wird dein erster Partner sein!",
                "Prof. Budde"
            ),
            DialoguePage(
                "[Wähle dein Starter-Monster mit den Pfeiltasten und bestätige mit ENTER]",
                None
            )
        ]
        
        self.dialogue_box.show_dialogue(pages, callback=self._start_selection)
    
    def _start_selection(self, _):
        """Startet die Starter-Auswahl"""
        self.dialogue_box.hide()
        # Hier könnte man eine spezielle Auswahl-UI anzeigen
    
    def handle_input(self, event):
        """Behandelt Spieler-Input"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.selection_arrow = (self.selection_arrow - 1) % 3
            elif event.key == pygame.K_RIGHT:
                self.selection_arrow = (self.selection_arrow + 1) % 3
            elif event.key == pygame.K_RETURN:
                self._confirm_starter_selection()
            elif event.key == pygame.K_ESCAPE:
                # Zurück zum Professor
                self._go_back_to_professor()
    
    def _confirm_starter_selection(self):
        """Bestätigt die Starter-Auswahl"""
        selected = self.starter_options[self.selection_arrow]
        
        # Erstelle das Starter-Monster
        starter_monster = MonsterInstance.create_from_species(
            species=self.game.resources.get_monster_species(selected['id']),
            level=5
        )
        
        # Füge es zur Party hinzu
        self.game.party_manager.add_monster(starter_monster)
        
        # Setze Story-Flags
        self.game.story_manager.set_flag('has_starter', True)
        self.game.story_manager.set_flag('starter_chosen', True)
        
        # Zeige Bestätigungsdialog
        pages = [
            DialoguePage(
                f"Du hast {selected['name']} gewählt!",
                None
            ),
            DialoguePage(
                f"Ein {selected['type']}-Typ! Sehr gute Wahl!",
                "Prof. Budde"
            ),
            DialoguePage(
                "Pass gut darauf auf! Es wird dein treuer Begleiter sein!",
                "Prof. Budde"
            ),
            DialoguePage(
                "Jetzt kannst du auf Reisen gehen und andere Monster fangen!",
                "Prof. Budde"
            ),
            DialoguePage(
                "Viel Erfolg, junger Trainer!",
                "Prof. Budde"
            )
        ]
        
        self.dialogue_box.show_dialogue(pages, callback=self._return_to_museum)
    
    def _return_to_museum(self, _):
        """Kehrt zum Museum zurück"""
        from engine.scenes.field_scene import FieldScene
        
        # Erstelle neue Field Scene
        field_scene = FieldScene(self.game)
        self.game.change_scene(field_scene)
        
        # Lade Museum-Map
        field_scene.enter(map_id="museum", spawn_point="professor")
    
    def _go_back_to_professor(self):
        """Geht zurück zum Professor-Dialog"""
        self._return_to_museum(None)
    
    def update(self, dt: float):
        """Updated die Szene"""
        self.dialogue_box.update(dt)
    
    def render(self, screen):
        """Rendert die Szene"""
        # Fülle Hintergrund
        screen.fill((50, 50, 50))
        
        # Zeichne Starter-Optionen
        for i, starter in enumerate(self.starter_options):
            x = 100 + i * 200
            y = 200
            
            # Hintergrund für ausgewählten Starter
            if i == self.selection_arrow:
                pygame.draw.rect(screen, (255, 255, 100), (x-10, y-10, 84, 84), 3)
            
            # Starter-Sprite
            if i < len(self.starter_sprites):
                screen.blit(self.starter_sprites[i], (x, y))
            
            # Starter-Info
            font = pygame.font.Font(None, 24)
            name_text = font.render(starter['name'], True, (255, 255, 255))
            type_text = font.render(starter['type'], True, (200, 200, 200))
            
            screen.blit(name_text, (x, y + 70))
            screen.blit(type_text, (x, y + 95))
        
        # Anweisungen
        font = pygame.font.Font(None, 20)
        instructions = [
            "Pfeiltasten: Starter wählen",
            "ENTER: Bestätigen",
            "ESC: Zurück"
        ]
        
        for i, instruction in enumerate(instructions):
            text = font.render(instruction, True, (200, 200, 200))
            screen.blit(text, (50, 400 + i * 25))
        
        # Zeichne Dialogue Box falls aktiv
        self.dialogue_box.render(screen)
