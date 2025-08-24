"""
Story Event System für FieldScene
Verwaltet alle Story-bezogenen Events und Trigger
"""

from typing import List
from engine.ui.dialogue import DialoguePage
from engine.systems.monster_instance import MonsterInstance
from engine.world.npc import NPC
from engine.world.tiles import TILE_SIZE
from engine.world.entity import Direction


class FieldStorySystem:
    """
    Verwaltet Story-Events in der Field-Scene.
    Cutscenes, Story-Trigger, Boss-Kämpfe, alles!
    """
    
    def __init__(self, field_scene):
        """
        Initialisiert das Story-System.
        
        Args:
            field_scene: Referenz zur FieldScene
        """
        self.scene = field_scene
        print("[StorySystem] Initialisiert!")
    
    def check_story_events(self) -> None:
        """
        Prüft auf Story-Events.
        Hier passiert der ganze verrückte Scheiß!
        """
        if not self.scene.player or not hasattr(self.scene.game, 'story_manager'):
            return
        
        # Dialog bereits offen? Dann nix machen
        if self.scene.interaction_system.is_dialogue_open():
            return
        
        story = self.scene.game.story_manager
        
        # Debug: Map-Wechsel tracken
        if hasattr(self.scene.player, 'last_map'):
            if self.scene.player.last_map != self.scene.map_id:
                print(f"[Story] Map-Wechsel: {self.scene.player.last_map} → {self.scene.map_id}")
        
        # Event 1: Erstes Mal Haus verlassen
        if self._check_first_house_leave(story):
            return
        
        # Event 2: Museum betreten ohne Starter
        if self._check_museum_entry(story):
            return
        
        # Event 3: Zeitrisse (später im Spiel)
        if self._check_timerift_event(story):
            return
    
    def _check_first_house_leave(self, story) -> bool:
        """Prüft ob Spieler das erste Mal das Haus verlässt."""
        if (self.scene.map_id == "kohlenstadt" and 
            not story.get_flag('left_house_first_time')):
            
            if (hasattr(self.scene.player, 'last_map') and 
                self.scene.player.last_map == "player_house"):
                
                print("[Story] Triggere: Erstes Mal Haus verlassen")
                story.set_flag('left_house_first_time', True)
                
                self.scene.interaction_system.show_internal_monologue([
                    "Kohlenstadt... wat für'n Drecksloch.",
                    "Aber hey, hier is alles angefangen. Die alten Zechen, die Fossilien...",
                    "Mal gucken wat der durchgeknallte Professor diesmal ausgegraben hat."
                ])
                return True
        
        return False
    
    def _check_museum_entry(self, story) -> bool:
        """Prüft Museum-Betreten ohne Starter."""
        if (self.scene.map_id == "museum" and 
            not story.get_flag('has_starter')):
            
            if not story.get_flag('professor_intro_started'):
                print("[Story] Triggere: Professor-Intro")
                story.set_flag('professor_intro_started', True)
                self._trigger_professor_fossil_intro()
                return True
        
        return False
    
    def _check_timerift_event(self, story) -> bool:
        """Prüft auf Zeitriss-Events (Mid-Game)."""
        if (story.trials_completed >= 5 and 
            not story.get_flag('timerifts_started')):
            
            story.set_flag('timerifts_started', True)
            self._trigger_timerift_event()
            return True
        
        return False
    
    def _trigger_professor_fossil_intro(self) -> None:
        """Professor Budde's verrückte Fossil-Präsentation."""
        if self.scene.player:
            self.scene.player.lock_movement(True)
        
        # Professor anschauen lassen
        professor = self._find_npc_by_name("professor_budde")
        if professor:
            # Zum Spieler schauen
            px, py = self.scene.player.get_tile_position()
            nx, ny = professor.get_tile_position()
            
            if px < nx:
                professor.direction = Direction.LEFT
            elif px > nx:
                professor.direction = Direction.RIGHT
            elif py < ny:
                professor.direction = Direction.UP
            else:
                professor.direction = Direction.DOWN
        
        # Derber Professor-Dialog
        dialogue_pages = [
            DialoguePage("Ach, da bisse ja endlich, du Schlafmütze!", "Prof. Budde"),
            DialoguePage("Weißte wat? Ich hab's geschafft! Ich hab die verdammten Viecher wiederbelebt!", "Prof. Budde"),
            DialoguePage("Jahrmillionen alte Monster-Fossilien aus'm Kohleflöz!", "Prof. Budde"),
            DialoguePage("Die Dinger sind der absolute Hammer! Stärker als der ganze moderne Dreck!", "Prof. Budde"),
            DialoguePage("Hör zu, Junge - du willst doch diese bescheuerten Trials machen, oder?", "Prof. Budde"),
            DialoguePage("Ohne Monster kommste da nich weit. Die anderen Zähmer fressen dich zum Frühstück!", "Prof. Budde"),
            DialoguePage("Ich geb dir eins von meinen Babys. Aber pass gefälligst drauf auf!", "Prof. Budde"),
            DialoguePage("Die sind verdammt wertvoll und ich hab keine Lust, noch mehr auszubuddeln!", "Prof. Budde")
        ]
        
        self.scene.interaction_system.show_dialogue(
            dialogue_pages,
            callback=lambda _: self._go_to_fossil_selection()
        )
    
    def _go_to_fossil_selection(self) -> None:
        """Ab zur Fossil-Auswahl - endlich Action!"""
        if self.scene.player:
            self.scene.player.lock_movement(False)
        
        print("[Story] Wechsel zur Starter-Auswahl")
        from engine.scenes.starter_scene import StarterScene
        self.scene.game.push_scene(StarterScene)
    
    def trigger_klaus_battle(self) -> None:
        """Klaus spawnt und will sich kloppen."""
        # Klaus vor Museum spawnen
        rival_x, rival_y = 19, 22  # Position anpassen
        
        rival_sprite = self.scene.sprite_manager.get_npc_sprite("rival", "down")
        
        klaus = NPC(
            x=rival_x * TILE_SIZE,
            y=rival_y * TILE_SIZE,
            name="Klaus",
            sprite=rival_sprite,
            dialogue_id="klaus_first_battle"
        )
        
        if self.scene.current_area:
            self.scene.current_area.entities.append(klaus)
        
        # Auto-Dialog triggern
        self._klaus_provocation(klaus)
    
    def _klaus_provocation(self, klaus) -> None:
        """Klaus provoziert zum Kampf."""
        dialogue_pages = [
            DialoguePage("Ey, Alter! Na, auch endlich wach geworden?", "Klaus"),
            DialoguePage("Der olle Professor hat mir erzählt, dass du auch so'n Fossil kriegst.", "Klaus"),
            DialoguePage("Haha, meins is auf jeden Fall stärker als dein Schrott!", "Klaus"),
            DialoguePage("Komm, lass uns kloppen! Ich mach dich fertig!", "Klaus"),
            DialoguePage("Danach kannste direkt wieder nach Hause zu Mutti heulen!", "Klaus")
        ]
        
        self.scene.interaction_system.show_dialogue(
            dialogue_pages,
            callback=lambda _: self._start_klaus_battle()
        )
    
    def _start_klaus_battle(self) -> None:
        """Startet den Kampf mit Klaus."""
        rival_monster = self._create_rival_monster()
        
        self.scene.encounter_system.start_trainer_battle(
            trainer_name="Klaus",
            enemy_team=[rival_monster],
            on_victory=lambda: self._on_klaus_victory(),
            on_defeat=lambda: self._on_klaus_defeat()
        )
    
    def _create_rival_monster(self) -> MonsterInstance:
        """Klaus' Monster hat immer Typ-Vorteil - der Pisser."""
        if (not hasattr(self.scene.game, 'party_manager') or 
            self.scene.game.party_manager.party.is_empty()):
            # Fallback
            species = self.scene.game.resources.get_monster_species(1)
            return MonsterInstance.create_from_species(species, level=5)
        
        player_starter = self.scene.game.party_manager.party.monsters[0]
        
        # Typ-Vorteil System
        type_advantages = {
            'Feuer': 'Wasser',    # Glutkohle → Tropfstein
            'Wasser': 'Erde',     # Tropfstein → Lehmling  
            'Erde': 'Luft',      # Lehmling → Windei
            'Luft': 'Feuer'      # Windei → Glutkohle
        }
        
        # Klaus kriegt immer das Monster mit Vorteil
        player_type = player_starter.types[0] if player_starter.types else 'Feuer'
        rival_type = type_advantages.get(player_type, 'Feuer')
        
        # Monster basierend auf Typ
        rival_monster_id = {
            'Feuer': 1,   # Glutkohle
            'Wasser': 2,  # Tropfstein
            'Erde': 3,    # Lehmling
            'Luft': 4     # Windei
        }.get(rival_type, 1)
        
        species = self.scene.game.resources.get_monster_species(rival_monster_id)
        rival_monster = MonsterInstance.create_from_species(
            species=species,
            level=5
        )
        
        return rival_monster
    
    def _on_klaus_victory(self) -> None:
        """Spieler hat gegen Klaus gewonnen."""
        story = self.scene.game.story_manager
        story.set_flag('rival_battle_1', True)
        story.rival_battles_won += 1
        
        dialogue_pages = [
            DialoguePage("Scheiße, Mann! Das war nur Glück!", "Klaus"),
            DialoguePage("Wart's ab, ich trainier das Viech und dann sehen wir weiter!", "Klaus"),
            DialoguePage("Beim nächsten Mal mach ich dich platt!", "Klaus"),
            DialoguePage("[Klaus haut ab]", None)
        ]
        
        self.scene.interaction_system.show_dialogue(
            dialogue_pages,
            callback=lambda _: self._remove_klaus_npc()
        )
    
    def _on_klaus_defeat(self) -> None:
        """Spieler hat gegen Klaus verloren."""
        story = self.scene.game.story_manager
        story.set_flag('rival_battle_1', True)
        
        dialogue_pages = [
            DialoguePage("HAHAHA! Hab ich's dir nich gesagt?", "Klaus"),
            DialoguePage("Du bist'n Anfänger, Mann! Geh erstmal trainieren!", "Klaus"),
            DialoguePage("Ich geh jetzt die erste Trial rocken. Viel Glück, Loser!", "Klaus"),
            DialoguePage("[Klaus stolziert davon]", None)
        ]
        
        self.scene.interaction_system.show_dialogue(
            dialogue_pages,
            callback=lambda _: self._remove_klaus_npc()
        )
    
    def _remove_klaus_npc(self) -> None:
        """Entfernt Klaus aus der Area."""
        if self.scene.current_area and hasattr(self.scene.current_area, 'entities'):
            self.scene.current_area.entities = [
                e for e in self.scene.current_area.entities
                if not (hasattr(e, 'name') and e.name == "Klaus")
            ]
            self.scene.interaction_system._on_dialogue_complete()
    
    def _trigger_timerift_event(self) -> None:
        """Zeitrisse erscheinen - Scheiße wird ernst!"""
        # TODO: Implementiere später für Mid-Game
        print("[Story] Zeitriss-Event - noch nicht implementiert")
    
    def _find_npc_by_name(self, name: str):
        """Findet einen NPC nach Namen."""
        if not self.scene.current_area or not hasattr(self.scene.current_area, 'entities'):
            return None
        
        for entity in self.scene.current_area.entities:
            if hasattr(entity, 'name') and name.lower() in entity.name.lower():
                return entity
        return None
