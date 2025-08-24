"""
Interaktions-System für FieldScene
Kümmert sich um alle Spieler-Interaktionen mit NPCs und Objekten
"""

from typing import Optional, Tuple, List
from engine.ui.dialogue import DialogueBox, DialoguePage, DialogueChoice
from engine.core.resources import resources
from engine.world.tiles import world_to_tile
from engine.world.entity import Direction
from engine.world.map_loader import Trigger


class FieldInteractionSystem:
    """
    Verwaltet alle Interaktionen in der Field-Scene.
    NPCs, Schilder, Trigger, alles!
    """
    
    def __init__(self, field_scene):
        """
        Initialisiert das Interaktions-System.
        
        Args:
            field_scene: Referenz zur FieldScene
        """
        self.scene = field_scene
        self.dialogue_box = DialogueBox(x=10, y=120, width=300, height=50)
        self.dialog_input_cooldown = 0.0
        self.dialog_cooldown_duration = 0.3
        
        print("[InteractionSystem] Initialisiert!")
    
    def update(self, dt: float) -> None:
        """Update für Dialog-Cooldown."""
        if self.dialog_input_cooldown > 0.0:
            self.dialog_input_cooldown -= dt
            if self.dialog_input_cooldown < 0.0:
                self.dialog_input_cooldown = 0.0
        
        # Update DialogueBox
        self.dialogue_box.update(dt)
    
    def handle_interaction(self, tile_pos: Tuple[int, int]) -> None:
        """
        Hauptmethode für Interaktionen.
        
        Args:
            tile_pos: (tile_x, tile_y) Position für Interaktion
        """
        tile_x, tile_y = tile_pos
        
        # 1. Check NPCs
        if self._check_npc_interaction(tile_x, tile_y):
            return
        
        # 2. Check Triggers
        if self._check_trigger_interaction(tile_x, tile_y):
            return
        
        # 3. Check versteckte Items
        self._check_hidden_item(tile_x, tile_y)
    
    def _check_npc_interaction(self, tile_x: int, tile_y: int) -> bool:
        """Prüft und führt NPC-Interaktion aus."""
        if not self.scene.current_area:
            return False
        
        for entity in self.scene.current_area.entities:
            entity_tile = entity.get_tile_position()
            if entity_tile == (tile_x, tile_y) and entity.interactable:
                # NPC anschauen lassen
                if hasattr(entity, 'grid_x') and hasattr(entity, 'grid_y'):
                    dx = entity.grid_x - self.scene.player.grid_x
                    dy = entity.grid_y - self.scene.player.grid_y
                    entity.direction = Direction.from_vector(-dx, -dy)
                
                # NPC-spezifische Interaktion
                from engine.world.npc import NPC
                if isinstance(entity, NPC):
                    entity.on_interact(self.scene.player)
                
                # Dialog zeigen
                self._interact_with_entity(entity)
                return True
        
        return False
    
    def _check_trigger_interaction(self, tile_x: int, tile_y: int) -> bool:
        """Prüft und führt Trigger-Interaktion aus."""
        if not self.scene.current_area or not hasattr(self.scene.current_area, 'map_data'):
            return False
        
        if self.scene.current_area.map_data:
            for trigger in self.scene.current_area.map_data.triggers:
                if trigger.x == tile_x and trigger.y == tile_y:
                    self._execute_trigger(trigger)
                    return True
        
        return False
    
    def _check_hidden_item(self, tile_x: int, tile_y: int) -> None:
        """Prüft auf versteckte Items."""
        hidden_items = self.scene.game_variables.get('hidden_items', {})
        key = f"{self.scene.map_id}_{tile_x}_{tile_y}"
        
        if key in hidden_items and not hidden_items[key]['found']:
            item = hidden_items[key]
            self.show_text(
                f"Du hast {item['name']} gefunden!",
                callback=lambda _: self._collect_hidden_item(key, item)
            )
    
    def _collect_hidden_item(self, key: str, item: dict) -> None:
        """Sammelt ein verstecktes Item."""
        hidden_items = self.scene.game_variables.get('hidden_items', {})
        hidden_items[key]['found'] = True
        # TODO: Zu Inventar hinzufügen
    
    def _interact_with_entity(self, entity) -> None:
        """
        Interagiert mit einer Entity (NPC).
        
        Args:
            entity: Entity zum interagieren
        """
        # Dialog bereits offen? Dann nix machen
        if self.dialogue_box.is_open():
            return
        
        # Spieler-Movement sperren
        if self.scene.player:
            self.scene.player.lock_movement(True)
        
        # Dialog-ID verwenden falls vorhanden
        if hasattr(entity, 'dialogue_id') and entity.dialogue_id:
            self._show_npc_dialogue(entity.dialogue_id, entity.name)
            return
        
        # Spezielle NPCs behandeln
        if "professor" in entity.name.lower():
            self._handle_professor_interaction()
        else:
            # Standard-Dialog
            self._show_default_dialogue(entity.name)
    
    def _handle_professor_interaction(self) -> None:
        """Spezielle Interaktion mit Professor Budde."""
        if not self.scene.game.story_manager.get_flag('has_starter'):
            pages = [
                DialoguePage(
                    text="Ey Jung! Du brauchst'n Monster für deine Reise!",
                    speaker="Prof. Budde"
                ),
                DialoguePage(
                    text="Komm mal mit ins Labor, ich hab da wat für dich!",
                    speaker="Prof. Budde"
                )
            ]
            
            self.dialogue_box.show_dialogue(
                pages,
                callback=lambda _: self._go_to_starter_selection()
            )
        else:
            pages = [
                DialoguePage(
                    text="Na, wie läuft's mit deinem Monster?",
                    speaker="Prof. Budde"
                ),
                DialoguePage(
                    text="Pass gut auf's auf, ne?",
                    speaker="Prof. Budde"
                )
            ]
            
            self.dialogue_box.show_dialogue(
                pages,
                callback=lambda _: self._on_dialogue_complete()
            )
    
    def _show_npc_dialogue(self, dialogue_id: str, speaker_name: str) -> None:
        """Zeigt Dialog aus dialogues.json."""
        dialogues_data = resources.load_json("game_data/dialogues.json")
        if not dialogues_data or dialogue_id not in dialogues_data:
            self._show_default_dialogue(speaker_name)
            return
        
        dialogue_data = dialogues_data[dialogue_id]
        text_lines = dialogue_data.get("text", ["..."])
        responses = dialogue_data.get("responses")
        actions = dialogue_data.get("actions")
        
        # DialoguePages erstellen
        pages = []
        for line in text_lines:
            pages.append(DialoguePage(text=line, speaker=speaker_name))
        
        # Antwortmöglichkeiten hinzufügen
        if responses and len(responses) > 0:
            choices = []
            for i, response in enumerate(responses):
                if response:
                    action = actions[i] if actions and i < len(actions) else None
                    choices.append(DialogueChoice(text=response, value=action))
            
            if choices:
                pages[-1].choices = choices
        
        self.dialogue_box.show_dialogue(
            pages,
            callback=lambda _: self._on_dialogue_complete()
        )
    
    def _show_default_dialogue(self, speaker_name: str) -> None:
        """Zeigt Standard-Dialog."""
        pages = [DialoguePage(
            text="Moin! Schönet Wetter heut', wa?",
            speaker=speaker_name
        )]
        self.dialogue_box.show_dialogue(
            pages,
            callback=lambda _: self._on_dialogue_complete()
        )
    
    def _execute_trigger(self, trigger: Trigger) -> None:
        """Führt einen Trigger aus."""
        if trigger.event == "sign":
            # Schild-Text zeigen
            text = trigger.args.get('text', 'Ein Schild, aber nix drauf.')
            self.show_text(text)
            
        elif trigger.event == "dialogue":
            # Dialog-Sequenz zeigen
            pages = []
            for page_data in trigger.args.get('pages', []):
                pages.append(DialoguePage(
                    text=page_data.get('text', '...'),
                    speaker=page_data.get('speaker')
                ))
            if pages:
                self.dialogue_box.show_dialogue(pages)
                
        elif trigger.event == "cutscene":
            # Cutscene starten
            cutscene_id = trigger.args.get('id')
            if cutscene_id and hasattr(self.scene.game, 'cutscene_manager'):
                self.scene.game.cutscene_manager.start(cutscene_id)
    
    def show_text(self, text: str, callback=None) -> None:
        """Zeigt einfachen Text."""
        self.dialogue_box.show_text(text, callback=callback)
    
    def show_dialogue(self, pages: List[DialoguePage], callback=None) -> None:
        """Zeigt Dialog-Seiten."""
        self.dialogue_box.show_dialogue(pages, callback=callback)
    
    def show_internal_monologue(self, lines: List[str]) -> None:
        """Zeigt internen Monolog des Spielers."""
        if self.scene.player:
            self.scene.player.lock_movement(True)
        
        pages = [DialoguePage(line, None) for line in lines]
        self.dialogue_box.show_dialogue(
            pages,
            callback=lambda _: self._on_dialogue_complete()
        )
    
    def _on_dialogue_complete(self) -> None:
        """Callback wenn Dialog fertig ist."""
        # Spieler-Movement freigeben
        if self.scene.player:
            self.scene.player.lock_movement(False)
        
        # Cooldown starten
        self.dialog_input_cooldown = self.dialog_cooldown_duration
    
    def _go_to_starter_selection(self) -> None:
        """Wechselt zur Starter-Auswahl."""
        if self.scene.player:
            self.scene.player.lock_movement(False)
        
        from engine.scenes.starter_scene import StarterScene
        self.scene.game.push_scene(StarterScene)
    
    def is_dialogue_open(self) -> bool:
        """Prüft ob Dialog offen ist."""
        return self.dialogue_box.is_open()
    
    def handle_input(self, event) -> bool:
        """Verarbeitet Input für Dialoge."""
        return self.dialogue_box.handle_input(event)
    
    def draw(self, surface) -> None:
        """Zeichnet die DialogueBox."""
        if self.dialogue_box.is_open():
            self.dialogue_box.draw(surface)
