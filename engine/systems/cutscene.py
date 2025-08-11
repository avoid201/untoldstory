"""
Cutscene System für Untold Story
Verwaltet skriptbasierte Ereignisse und Sequenzen
"""

from typing import List, Dict, Any, Callable, Optional
from dataclasses import dataclass
import pygame


@dataclass
class CutsceneAction:
    """Eine einzelne Aktion in einer Cutscene"""
    action_type: str  # 'dialogue', 'move', 'fade', 'spawn', 'despawn', 'battle', 'give_item'
    params: Dict[str, Any]
    duration: float = 0.0
    blocking: bool = True


class Cutscene:
    """Eine skriptbasierte Ereignissequenz"""
    
    def __init__(self, scene_id: str):
        self.id = scene_id
        self.actions: List[CutsceneAction] = []
        self.current_action = 0
        self.active = False
        self.completed = False
        self.on_complete: Optional[Callable] = None
    
    def add_action(self, action: CutsceneAction):
        """Fügt eine Aktion zur Cutscene hinzu"""
        self.actions.append(action)
    
    def start(self):
        """Startet die Cutscene"""
        self.active = True
        self.current_action = 0
        self.completed = False
    
    def update(self, dt: float) -> bool:
        """Updated die Cutscene, gibt True zurück wenn fertig"""
        if not self.active or self.completed:
            return self.completed
        
        if self.current_action >= len(self.actions):
            self.complete()
            return True
        
        # Verarbeite aktuelle Aktion
        action = self.actions[self.current_action]
        
        # Action-Processing implementieren
        if action.action_type == 'dialogue':
            # Dialog-Action - wird von der Scene verarbeitet
            if not hasattr(self, '_dialogue_shown'):
                self._dialogue_shown = True
                # Trigger Dialog in der Scene
                if hasattr(self, 'game') and hasattr(self.game, 'current_scene'):
                    scene = self.game.current_scene
                    if hasattr(scene, 'dialogue_box'):
                        from engine.ui.dialogue import DialoguePage
                        if 'pages' in action.params:
                            # Mehrere Dialog-Seiten
                            pages = action.params['pages']
                            scene.dialogue_box.show_dialogue(pages, callback=lambda _: self._next_action())
                        else:
                            # Einzelner Dialog
                            page = DialoguePage(action.params.get('text', ''), action.params.get('speaker'))
                            scene.dialogue_box.show_dialogue([page], callback=lambda _: self._next_action())
                        return False  # Warte auf Dialog-Ende
        
        elif action.action_type == 'fade':
            # Fade-Action
            if not hasattr(self, '_fade_started'):
                self._fade_started = True
                self._fade_timer = 0.0
                # TODO: Implementiere Fade-Effekt in der Scene
                print(f"Fade {action.params.get('type', 'in')} für {action.duration}s")
            
            self._fade_timer += dt
            if self._fade_timer >= action.duration:
                self._next_action()
                return False
        
        elif action.action_type == 'move':
            # Move-Action
            if not hasattr(self, '_move_started'):
                self._move_started = True
                # TODO: Implementiere Entity-Bewegung
                print(f"Move entity {action.params.get('entity')} to {action.params.get('to')}")
                self._next_action()
                return False
        
        elif action.action_type == 'spawn':
            # Spawn-Action
            if not hasattr(self, '_spawn_done'):
                self._spawn_done = True
                # TODO: Implementiere Entity-Spawn
                print(f"Spawn entity {action.params.get('entity')} at {action.params.get('position')}")
                self._next_action()
                return False
        
        elif action.action_type == 'scene_change':
            # Scene-Change-Action
            if not hasattr(self, '_scene_changed'):
                self._scene_changed = True
                # TODO: Implementiere Scene-Wechsel
                print(f"Change to scene {action.params.get('scene')}")
                self._next_action()
                return False
        
        else:
            # Unbekannte Action - überspringe
            print(f"Unbekannte Cutscene-Action: {action.action_type}")
            self._next_action()
            return False
        
        return False
    
    def _next_action(self):
        """Geht zur nächsten Action über"""
        self.current_action += 1
        # Reset Action-spezifische Flags
        if hasattr(self, '_dialogue_shown'):
            delattr(self, '_dialogue_shown')
        if hasattr(self, '_fade_started'):
            delattr(self, '_fade_started')
        if hasattr(self, '_move_started'):
            delattr(self, '_move_started')
        if hasattr(self, '_spawn_done'):
            delattr(self, '_spawn_done')
        if hasattr(self, '_scene_changed'):
            delattr(self, '_scene_changed')
    
    def complete(self):
        """Beendet die Cutscene"""
        self.active = False
        self.completed = True
        if self.on_complete:
            self.on_complete()


class CutsceneManager:
    """Verwaltet alle Cutscenes im Spiel"""
    
    def __init__(self, game):
        self.game = game
        self.cutscenes: Dict[str, Cutscene] = {}
        self.active_cutscene: Optional[Cutscene] = None
        
        # Registriere alle Cutscenes
        self._register_cutscenes()
    
    def _register_cutscenes(self):
        """Registriert alle Spiel-Cutscenes"""
        
        # Spielbeginn - Aufwachen
        awakening = Cutscene("awakening")
        awakening.add_action(CutsceneAction(
            'fade', {'type': 'in', 'duration': 2.0}
        ))
        awakening.add_action(CutsceneAction(
            'dialogue', {
                'text': "Ein neuer Tag beginnt im Ruhrgebiet...",
                'speaker': None
            }
        ))
        awakening.add_action(CutsceneAction(
            'dialogue', {
                'text': "Du erwachst in deinem Zimmer. Heute beginnt deine große Reise!",
                'speaker': None
            }
        ))
        self.cutscenes['awakening'] = awakening
        
        # Starter-Erhalt
        receive_starter = Cutscene("receive_starter")
        receive_starter.add_action(CutsceneAction(
            'dialogue', {
                'text': "Professor Budde führt dich zu einem speziellen Gerät...",
                'speaker': None
            }
        ))
        receive_starter.add_action(CutsceneAction(
            'fade', {'type': 'out', 'duration': 0.5}
        ))
        receive_starter.add_action(CutsceneAction(
            'scene_change', {'scene': 'StarterScene'}
        ))
        self.cutscenes['receive_starter'] = receive_starter
        
        # Rivalen-Einführung
        rival_intro = Cutscene("rival_intro")
        rival_intro.add_action(CutsceneAction(
            'spawn', {
                'entity': 'rival_klaus',
                'position': (10, 8),
                'facing': 'up'
            }
        ))
        rival_intro.add_action(CutsceneAction(
            'move', {
                'entity': 'rival_klaus',
                'to': (10, 6),
                'speed': 2.0
            }
        ))
        rival_intro.add_action(CutsceneAction(
            'dialogue', {
                'speaker': 'Klaus',
                'pages': [
                    "Hey! Warte mal!",
                    "Du hast auch'n Monster vom Professor bekommen, oder?"
                ]
            }
        ))
        self.cutscenes['rival_intro'] = rival_intro
    
    def play(self, cutscene_id: str, on_complete: Callable = None):
        """Spielt eine Cutscene ab"""
        if cutscene_id in self.cutscenes:
            self.active_cutscene = self.cutscenes[cutscene_id]
            self.active_cutscene.on_complete = on_complete
            self.active_cutscene.start()
            
            # Pausiere Spieler-Input während Cutscene
            if hasattr(self.game, 'current_scene') and hasattr(self.game.current_scene, 'player'):
                self.game.current_scene.player.lock_movement(True)
    
    def update(self, dt: float):
        """Updated die aktive Cutscene"""
        if self.active_cutscene and self.active_cutscene.active:
            if self.active_cutscene.update(dt):
                # Cutscene beendet
                if hasattr(self.game, 'current_scene') and hasattr(self.game.current_scene, 'player'):
                    self.game.current_scene.player.lock_movement(False)
                self.active_cutscene = None
