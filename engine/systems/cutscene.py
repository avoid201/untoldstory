"""
Cutscene System für Untold Story
Verwaltet skriptbasierte Ereignisse und Sequenzen
"""

from typing import List, Dict, Any, Callable, Optional
from dataclasses import dataclass
import pygame

# Export CutsceneAction für andere Module
__all__ = ['Cutscene', 'CutsceneAction', 'CutsceneManager']


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
                fade_type = action.params.get('type', 'in')
                print(f"Fade {fade_type} für {action.duration}s")
                
                # Starte Fade-Effekt in der Scene
                if hasattr(self.game, 'current_scene') and self.game.current_scene:
                    if hasattr(self.game.current_scene, 'start_fade'):
                        self.game.current_scene.start_fade(fade_type, action.duration)
            
            self._fade_timer += dt
            if self._fade_timer >= action.duration:
                self._next_action()
                return False
        
        elif action.action_type == 'move':
            # Move-Action
            if not hasattr(self, '_move_started'):
                self._move_started = True
                entity_name = action.params.get('entity')
                target_pos = action.params.get('to')
                
                print(f"Move entity {entity_name} to {target_pos}")
                
                # Implementiere Entity-Bewegung
                if hasattr(self.game, 'current_scene') and self.game.current_scene:
                    if hasattr(self.game.current_scene, 'move_entity'):
                        success = self.game.current_scene.move_entity(entity_name, target_pos)
                        if success:
                            self._next_action()
                            return False
                        else:
                            # Warte bis Bewegung abgeschlossen ist
                            return False
                
                # Fallback: Bewegung sofort beenden
                self._next_action()
                return False
        
        elif action.action_type == 'spawn':
            # Spawn-Action
            if not hasattr(self, '_spawn_done'):
                self._spawn_done = True
                entity_name = action.params.get('entity')
                position = action.params.get('position')
                
                print(f"Spawn entity {entity_name} at {position}")
                
                # Implementiere Entity-Spawn
                if hasattr(self.game, 'current_scene') and self.game.current_scene:
                    if hasattr(self.game.current_scene, 'spawn_entity'):
                        success = self.game.current_scene.spawn_entity(entity_name, position)
                        if success:
                            print(f"Entity {entity_name} erfolgreich gespawnt")
                        else:
                            print(f"Fehler beim Spawnen von {entity_name}")
                
                self._next_action()
                return False
        
        elif action.action_type == 'scene_change':
            # Scene-Change-Action
            if not hasattr(self, '_scene_changed'):
                self._scene_changed = True
                target_scene = action.params.get('scene')
                
                print(f"Change to scene {target_scene}")
                
                # Implementiere Scene-Wechsel
                if hasattr(self.game, 'change_scene'):
                    try:
                        self.game.change_scene(target_scene)
                        print(f"Scene-Wechsel zu {target_scene} erfolgreich")
                    except Exception as e:
                        print(f"Fehler beim Scene-Wechsel: {e}")
                else:
                    print("Game hat keine change_scene Methode")
                
                self._next_action()
                return False
        
        elif action.action_type == 'open_door':
            # Door Open-Action
            if not hasattr(self, '_door_opened'):
                self._door_opened = True
                door_id = action.params.get('door_id')
                map_id = action.params.get('map_id')
                
                print(f"Opening door {door_id} on map {map_id}")
                
                # Update world state
                from engine.systems.world_state import world_state
                world_state.set_door_state(map_id, door_id, True)
                
                # Update map visuals if possible
                if hasattr(self.game, 'current_scene') and hasattr(self.game.current_scene, 'update_door_visual'):
                    self.game.current_scene.update_door_visual(door_id, True)
                
                self._next_action()
                return False
                
        elif action.action_type == 'close_door':
            # Door Close-Action
            if not hasattr(self, '_door_closed'):
                self._door_closed = True
                door_id = action.params.get('door_id')
                map_id = action.params.get('map_id')
                
                print(f"Closing door {door_id} on map {map_id}")
                
                # Update world state
                from engine.systems.world_state import world_state
                world_state.set_door_state(map_id, door_id, False)
                
                # Update map visuals if possible
                if hasattr(self.game, 'current_scene') and hasattr(self.game.current_scene, 'update_door_visual'):
                    self.game.current_scene.update_door_visual(door_id, False)
                
                self._next_action()
                return False
                
        elif action.action_type == 'toggle_switch':
            # Switch Toggle-Action
            if not hasattr(self, '_switch_toggled'):
                self._switch_toggled = True
                switch_id = action.params.get('switch_id')
                map_id = action.params.get('map_id')
                
                print(f"Toggling switch {switch_id} on map {map_id}")
                
                # Update world state
                from engine.systems.world_state import world_state
                new_state = world_state.toggle_switch(map_id, switch_id)
                
                print(f"Switch {switch_id} is now {'ON' if new_state else 'OFF'}")
                
                # Update map visuals if possible
                if hasattr(self.game, 'current_scene') and hasattr(self.game.current_scene, 'update_switch_visual'):
                    self.game.current_scene.update_switch_visual(switch_id, new_state)
                
                # Execute switch effects if configured
                switch_effects = action.params.get('effects', [])
                for effect in switch_effects:
                    self._execute_switch_effect(effect, new_state)
                
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
        if hasattr(self, '_door_opened'):
            delattr(self, '_door_opened')
        if hasattr(self, '_door_closed'):
            delattr(self, '_door_closed')
        if hasattr(self, '_switch_toggled'):
            delattr(self, '_switch_toggled')
    
    def complete(self):
        """Beendet die Cutscene"""
        self.active = False
        self.completed = True
        if self.on_complete:
            self.on_complete()
    
    def _execute_switch_effect(self, effect: Dict[str, Any], switch_state: bool):
        """Execute a switch effect based on the switch state."""
        try:
            effect_type = effect.get('type')
            
            if effect_type == 'door':
                # Switch controls a door
                door_id = effect.get('door_id')
                map_id = effect.get('map_id')
                
                if door_id and map_id:
                    from engine.systems.world_state import world_state
                    world_state.set_door_state(map_id, door_id, switch_state)
                    
                    if hasattr(self.game, 'current_scene'):
                        if hasattr(self.game.current_scene, 'update_door_visual'):
                            self.game.current_scene.update_door_visual(door_id, switch_state)
                    
                    state_text = "geöffnet" if switch_state else "geschlossen"
                    print(f"Door {door_id} wurde {state_text}")
            
            elif effect_type == 'bridge':
                # Switch controls a bridge
                bridge_id = effect.get('bridge_id')
                map_id = effect.get('map_id')
                
                if bridge_id and map_id:
                    from engine.systems.world_state import world_state
                    world_state.set_object_state(map_id, bridge_id, 'bridge', 'extended' if switch_state else 'retracted')
                    
                    state_text = "ausgefahren" if switch_state else "eingefahren"
                    print(f"Bridge {bridge_id} wurde {state_text}")
            
            elif effect_type == 'platform':
                # Switch controls a moving platform
                platform_id = effect.get('platform_id')
                map_id = effect.get('map_id')
                
                if platform_id and map_id:
                    from engine.systems.world_state import world_state
                    world_state.set_object_state(map_id, platform_id, 'platform', 'up' if switch_state else 'down')
                    
                    state_text = "oben" if switch_state else "unten"
                    print(f"Platform {platform_id} ist jetzt {state_text}")
            
            elif effect_type == 'message':
                # Switch shows a message
                message = effect.get('message', '')
                if message and hasattr(self.game, 'current_scene'):
                    if hasattr(self.game.current_scene, 'show_message'):
                        self.game.current_scene.show_message(message)
                        
            elif effect_type == 'sound':
                # Switch plays a sound
                sound_file = effect.get('sound_file')
                if sound_file:
                    try:
                        from engine.core.resources import resources
                        sound = resources.load_sound(sound_file, volume=0.7)
                        sound.play()
                    except:
                        pass  # Ignore sound errors
                        
        except Exception as e:
            print(f"Error executing switch effect: {e}")


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
