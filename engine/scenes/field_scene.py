"""
Field Scene for Untold Story - AUFGERÄUMT VON FLINT!
Main overworld gameplay scene mit Map, Player, NPCs und Interaktionen
Jetzt ohne den ganzen überflüssigen Scheiß!
"""

import pygame
import random
import json
from typing import Optional, List, Dict, Any, Tuple

from engine.core.scene_base import Scene
from engine.core.resources import resources
from engine.world.tiles import TILE_SIZE, world_to_tile, tile_to_world, draw_grid
from engine.world.map_loader import MapLoader, MapData, Warp, Trigger
from engine.world.camera import Camera, CameraConfig
from engine.world.entity import Entity, Direction
from engine.world.player import Player
from engine.ui.dialogue import DialogueBox, DialoguePage, DialogueChoice
from engine.world.map_transition import MapTransition
from engine.systems.monster_instance import MonsterInstance
from engine.ui.transitions import TransitionType
from engine.graphics.sprite_manager import SpriteManager
from engine.graphics.tile_renderer import TileRenderer
from engine.world.area import Area
import os


class FieldScene(Scene):
    """
    Main overworld gameplay scene - jetzt aufgeräumt!
    """
    
    def __init__(self, game) -> None:
        """Initialize the field scene."""
        super().__init__(game)
        
        # Graphics systems
        self.sprite_manager = self.game.sprite_manager if hasattr(self.game, 'sprite_manager') else SpriteManager.get()
        self.tile_renderer = TileRenderer(self.sprite_manager)
        
        # Current area and map
        self.current_area: Optional[Area] = None
        self.map_id: str = ""
        
        # Player
        self.player: Optional[Player] = None
        
        # Camera
        self.camera: Optional[Camera] = None
        self.camera_config = CameraConfig()
        
        # UI elements
        self.dialogue_box = DialogueBox(x=10, y=120, width=300, height=50)
        
        # State flags
        self.show_debug = False
        self.show_grid = False
        self.paused = False
        self.in_battle = False
        
        # Dialog cooldown
        self.dialog_input_cooldown: float = 0.0
        self.dialog_cooldown_duration: float = 0.3
        
        # Encounter system
        self.encounter_enabled = True
        self.steps_since_encounter = 0
        self.min_steps_between_encounters = 3  # Reduziert für besseres Testing
        self.encounter_check_pending = False
        
        # Story flags
        self.story_flags: Dict[str, bool] = {}
        self.game_variables: Dict[str, Any] = {}
        
        # Load graphics
        self._load_graphics()
        
        # Check für Starter-Requirement
        self._check_starter_requirement()
    
    def _load_graphics(self):
        """Lade Grafik-Ressourcen."""
        print("[Flint] Lade Grafiken...")
        
        # SpriteManager lädt alles lazy
        try:
            cache_info = self.sprite_manager.get_cache_info()
            print(f"[Flint] Sprite-Cache bereit: {cache_info['total_sprites']} Sprites")
        except Exception as e:
            print(f"[Flint] Cache warm-up fehlgeschlagen: {e}")
        
        # Lade Monster-Daten
        try:
            data = self.game.resources.load_json('monsters.json', from_data=True)
            if isinstance(data, list):
                print(f"[Flint] Monster geladen: {len(data)} Viecher")
        except Exception as e:
            print(f"[Flint] Monster laden fehlgeschlagen: {e}")
    
    def _initialize_player(self):
        """Initialisiere den Player mit Grid-Movement."""
        from engine.world.player import Player
        from engine.world.tiles import TILE_SIZE
        
        # Erstelle Player
        self.player = Player(5 * TILE_SIZE, 5 * TILE_SIZE)
        
        # Verbinde mit Game und SpriteManager
        self.player.game = self.game
        if hasattr(self, 'sprite_manager'):
            self.player.sprite_manager = self.sprite_manager
            print(f"[Flint] Player mit SpriteManager verbunden")
        
        # Setze Callbacks
        self.player.set_interact_callback(self._handle_interaction)
        self.player.set_warp_callback(self._check_warp_at_position)
        self.player.set_encounter_callback(self._check_encounter)
        self.player.set_collision_callback(self._handle_collision_event)
        
        # Lade Player-Sprite
        self.player._load_player_sprite()
        
        print(f"[Flint] Player initialisiert: {self.player.name}")
        print(f"[Flint] Position: ({self.player.x}, {self.player.y})")
    
    def _check_starter_requirement(self):
        """Check ob der Spieler'n Starter braucht."""
        if not hasattr(self.game, 'party_manager'):
            return
            
        if self.game.party_manager.party.is_empty():
            if not self.game.story_manager.get_flag('has_starter'):
                # Ab zur Starter-Auswahl!
                from engine.scenes.starter_scene import StarterScene
                self.game.push_scene(StarterScene)
    
    def enter(self, **kwargs) -> None:
        """Enter the field scene."""
        super().enter(**kwargs)
        
        # Verbinde SpriteManager
        if hasattr(self.game, 'sprite_manager'):
            self.sprite_manager = self.game.sprite_manager
            print(f"[Flint] SpriteManager verbunden: {len(self.sprite_manager.sprite_cache)} Sprites")
        
        # Get parameters
        map_id = kwargs.get('map_id', 'player_house')
        spawn_point = kwargs.get('spawn_point', 'bed')
        
        # Lade Map
        self.load_map(map_id)
        
        # Position player
        if spawn_point and self.player:
            self._position_player_at_spawn(spawn_point)
        
        # Reset battle flag
        self.in_battle = False
        
        # Starte Map-Musik falls vorhanden
        if self.current_area:
            music_file = None
            if hasattr(self.current_area, 'map_data') and self.current_area.map_data:
                music_file = self.current_area.map_data.properties.get('music')
            
            if music_file:
                try:
                    resources.load_music(music_file, loops=-1, fade_ms=1000)
                except:
                    pass
    
    def load_map(self, map_name: str, spawn_x: int = 5, spawn_y: int = 5):
        """Lädt eine Map - VEREINFACHT!"""
        print(f"[Flint] Lade Map: {map_name}")
        
        # Speichere vorherige Map für Story-Events
        if self.player and self.map_id:
            self.player.last_map = self.map_id
        
        try:
            # Lade Map-Daten
            from engine.world.map_loader import MapLoader
            map_data = MapLoader.load_map(map_name)
            
            # Initialisiere Camera falls nötig
            if not self.camera:
                from engine.world.camera import Camera, CameraConfig
                self.camera = Camera(
                    viewport_width=self.game.logical_size[0],
                    viewport_height=self.game.logical_size[1],
                    world_width=map_data.width * 16,
                    world_height=map_data.height * 16,
                    config=self.camera_config
                )
            
            # Erstelle Area
            from engine.world.area import Area
            self.current_area = Area(map_name)
            self.map_id = map_name
            
            # Setze map_data falls Area sie nicht hat
            if not hasattr(self.current_area, 'map_data'):
                self.current_area.map_data = map_data
            
            # Debug-Info
            print(f"[Flint] Map geladen: {map_name}")
            print(f"[Flint] Größe: {map_data.width}x{map_data.height}")
            
            # Lade Encounter-Daten
            self._load_encounter_data()
            
            # Update Camera
            if self.camera:
                world_width = map_data.width * 16
                world_height = map_data.height * 16
                self.camera.set_world_size(world_width, world_height)
            
            # Erstelle Player falls nicht vorhanden
            if not self.player:
                self._initialize_player()
            
            # Setze Collision-Map für Player
            collision_layer = map_data.layers.get('collision', [])
            self.player.set_collision_map(
                collision_layer,
                map_data.width,
                map_data.height
            )
            
            # Positioniere Player
            self.player.set_tile_position(spawn_x, spawn_y)
            
            # Zentriere Camera auf Player
            self.camera.center_on(
                self.player.x + self.player.width // 2,
                self.player.y + self.player.height // 2,
                immediate=True
            )
            self.camera.set_follow_target(self.player)
            
            # Lade NPCs
            self._load_area_entities()
            
            print(f"[Flint] Map {map_name} erfolgreich geladen!")
            
        except Exception as e:
            print(f"[Flint] Fehler beim Map-Laden: {e}")
            import traceback
            traceback.print_exc()
            self._create_empty_area()
    
    def _load_encounter_data(self):
        """Lade Encounter-Daten für die Area."""
        if not self.current_area:
            return
        
        if self.map_id == "route1":  # Fixed: route1 ohne Unterstrich!
            # Route 1 mit F und E Rang Monstern
            self.current_area.encounter_table = self._create_route_1_encounter_table()
            self.current_area.encounter_rate = 0.25  # Erhöht für besseres Testing
        elif self.map_id == "kohlenstadt":
            # Starter-Area
            self.current_area.encounter_table = [
                {"species_id": 5, "name": "Kohlekumpel", "level_min": 2, "level_max": 4, "weight": 40},
                {"species_id": 6, "name": "Kieselkrabbler", "level_min": 2, "level_max": 5, "weight": 30},
                {"species_id": 7, "name": "Flugratte", "level_min": 3, "level_max": 4, "weight": 20},
                {"species_id": 8, "name": "Wolkenfurz", "level_min": 3, "level_max": 5, "weight": 10},
            ]
            self.current_area.encounter_rate = 0.15
        else:
            # Keine Encounters
            self.current_area.encounter_table = []
            self.current_area.encounter_rate = 0
    
    def _create_empty_area(self) -> None:
        """Erstelle eine leere Fallback-Area."""
        from engine.world.map_loader import MapData
        from engine.world.tiles import TILE_SIZE
        
        empty_map = MapData(
            id="empty",
            name="Leere Area",
            width=20,
            height=20,
            tile_size=TILE_SIZE,
            layers={
                'ground': [[1] * 20 for _ in range(20)],
                'collision': [[0] * 20 for _ in range(20)]
            },
            warps=[],
            triggers=[],
            properties={},
            tilesets=[]
        )
        
        from engine.world.area import Area
        self.current_area = Area("empty")
        self.current_area.map_data = empty_map
        self.current_area.entities = []
        self.current_area.npcs = []
        self.current_area.encounter_rate = 0
        self.current_area.encounter_table = []
    
    def _load_area_entities(self) -> None:
        """Lade NPCs für die aktuelle Area - MIT PATHFINDING!"""
        from engine.world.tiles import TILE_SIZE
        
        # Lade NPC-Daten
        npcs_data = resources.load_json("game_data/npcs.json")
        if not npcs_data:
            print(f"[Flint] Keine NPC-Daten gefunden")
            return
        
        current_map_npcs = npcs_data.get(self.map_id, {})
        
        for npc_name, npc_info in current_map_npcs.items():
            try:
                # Bestimme Sprite
                sprite_name = npc_info.get("sprite", "villager_m")
                facing = npc_info.get("facing", "down")
                
                # Lade Sprite
                npc_sprite = self.sprite_manager.get_npc_sprite(sprite_name, facing)
                if not npc_sprite:
                    # Fallback
                    for fallback_dir in ["down", "up", "left", "right"]:
                        if fallback_dir != facing:
                            npc_sprite = self.sprite_manager.get_npc_sprite(sprite_name, fallback_dir)
                            if npc_sprite:
                                break
                
                # Erstelle NPC
                from engine.world.npc import NPC
                npc = NPC.from_config_dict(
                    name=npc_name.replace('_', ' ').title(),
                    config_dict=npc_info,
                    sprite_surface=npc_sprite
                )
                
                # WICHTIG: Setze Pathfinding-Komponenten!
                if hasattr(self.current_area, 'map_data') and self.current_area.map_data:
                    collision_layer = self.current_area.map_data.layers.get('collision', [])
                    npc.set_collision_layer(collision_layer)
                    
                    # Aktiviere Pathfinding für NPCs mit Movement-Pattern
                    movement_pattern = npc_info.get('movement_pattern', 'static')
                    if movement_pattern != 'static':
                        # TODO: Pathfinding hier integrieren!
                        print(f"[Flint] NPC {npc_name} braucht Pathfinding für Pattern: {movement_pattern}")
                
                # Setze SpriteManager
                npc.set_sprite_manager(self.sprite_manager)
                
                # WICHTIG: Setze Area und Player-Referenz für Pathfinding!
                npc.set_area(self.current_area)
                npc.set_player_reference(self.player)
                
                # Füge zur Area hinzu
                self.current_area.entities.append(npc)
                print(f"[Flint] NPC hinzugefügt: {npc.name} - Pattern: {npc_info.get('movement_pattern', 'static')}")
                
            except Exception as e:
                print(f"[Flint] Fehler beim NPC-Laden {npc_name}: {e}")
        
        print(f"[Flint] {len(current_map_npcs)} NPCs geladen für {self.map_id}")
    
    def _on_dialogue_complete(self) -> None:
        """Dialog fertig - Movement wieder freigeben."""
        if self.player:
            self.player.lock_movement(False)
        self.dialog_input_cooldown = self.dialog_cooldown_duration
    
    def _position_player_at_spawn(self, spawn_point: str) -> None:
        """Positioniere Player am Spawn-Point."""
        if not self.player or not self.current_area:
            return
        
        # Check für benannte Spawn-Points
        if hasattr(self.current_area, 'map_data') and self.current_area.map_data:
            spawn_data = self.current_area.map_data.properties.get('spawns', {})
            
            if spawn_point in spawn_data:
                spawn = spawn_data[spawn_point]
                self.player.set_tile_position(spawn['x'], spawn['y'])
                if 'direction' in spawn:
                    from engine.world.entity import Direction
                    self.player.direction = Direction[spawn['direction'].upper()]
                return
        
        # Spezielle Spawn-Points
        if spawn_point == "bed":
            if self.map_id == "player_house":
                self.player.set_tile_position(5, 5)
                from engine.world.entity import Direction
                self.player.direction = Direction.DOWN
            else:
                self.player.set_tile_position(5, 5)
        elif spawn_point == "door":
            self.player.set_tile_position(10, 10)
        else:
            # Default center
            if hasattr(self.current_area, 'width') and hasattr(self.current_area, 'height'):
                self.player.set_tile_position(
                    self.current_area.width // 2,
                    self.current_area.height // 2
                )
            else:
                self.player.set_tile_position(10, 10)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle Input-Events."""
        # Dialog first
        if self.dialogue_box.is_open():
            return self.dialogue_box.handle_input(event)
        
        # Check für Pause und Debug
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_ESCAPE, pygame.K_q]:
                self._toggle_pause()
                return True
            elif event.key == pygame.K_TAB:
                self.show_debug = not self.show_debug
                if self.show_debug:
                    print("[Flint] 🔍 Debug-Modus AN!")
                else:
                    print("[Flint] 🔍 Debug-Modus AUS")
                return True
            elif event.key == pygame.K_g:
                self.show_grid = not self.show_grid
                print(f"[Flint] Grid: {'AN' if self.show_grid else 'AUS'}")
                return True
            elif event.key == pygame.K_b and self.game.debug_mode:
                # Debug: Force battle
                self._start_battle()
                return True
        
        return False
    
    def _toggle_pause(self) -> None:
        """Pause umschalten."""
        self.paused = not self.paused
        
        if self.paused:
            from engine.scenes.pause_scene import PauseScene
            self.game.push_scene(PauseScene, game=self.game)
    
    def update(self, dt: float) -> None:
        """Update der Scene."""
        # Update Dialog-Cooldown
        if self.dialog_input_cooldown > 0.0:
            self.dialog_input_cooldown -= dt
            if self.dialog_input_cooldown < 0.0:
                self.dialog_input_cooldown = 0.0
        
        # Update Dialog
        if hasattr(self, 'dialogue_box'):
            self.dialogue_box.update(dt)
            
            if self.dialogue_box.is_open() or self.paused:
                # Update Cutscene trotzdem
                if hasattr(self.game, 'cutscene_manager') and self.game.cutscene_manager.active_cutscene:
                    self.game.cutscene_manager.update(dt)
                return
        
        # Check für Encounter
        if self.encounter_check_pending and not self.in_battle:
            self.encounter_check_pending = False
            self._execute_encounter_check()
        
        # Update Cutscene Manager
        if hasattr(self.game, 'cutscene_manager') and self.game.cutscene_manager.active_cutscene:
            self.game.cutscene_manager.update(dt)
        
        # Update Player
        if self.player and not self.in_battle:
            self.player.handle_input(self.game, dt)
            self.player.update(dt)
        
        # Update Camera NACH Player!
        if self.camera:
            self.camera.update(dt)
        
        # Update NPCs - HIER KOMMT PATHFINDING REIN!
        if self.current_area and hasattr(self.current_area, 'entities'):
            for entity in self.current_area.entities:
                entity.update(dt)
                # TODO: Pathfinding-Update für bewegende NPCs
        
        # Check Story-Events
        self._check_story_events()
    
    def draw(self, surface: pygame.Surface) -> None:
        """Zeichne die Scene."""
        if not self.current_area:
            font = pygame.font.Font(None, 24)
            text = font.render("FEHLER: Keine Area geladen!", True, (255, 0, 0))
            surface.blit(text, (50, 50))
            return
        
        # Verwende RenderManager
        if not hasattr(self, 'render_manager'):
            from engine.graphics.render_manager import RenderManager
            self.render_manager = RenderManager()
        
        # Setze Player-Referenz
        self.render_manager.player = self.player
        
        # UI-Elemente
        ui_elements = []
        if hasattr(self, 'dialogue_box'):
            ui_elements.append(self.dialogue_box)
        
        # Rendere Scene
        self.render_manager.render_scene(surface, self.current_area, self.camera, ui_elements)
        
        # Debug-Grid
        if self.show_grid:
            from engine.world.tiles import draw_grid
            draw_grid(surface, int(self.camera.x), int(self.camera.y))
        
        # Debug-Info
        if self.show_debug:
            self._draw_debug_info(surface)
        
        # UI
        self._draw_ui(surface)
    
    def _draw_ui(self, surface: pygame.Surface) -> None:
        """Zeichne UI-Elemente."""
        # Area-Name
        if self.current_area:
            try:
                font = pygame.font.Font(None, 18)
                text = font.render(self.current_area.name, True, (255, 255, 255))
                text.set_alpha(200)
                surface.blit(text, (5, 5))
            except:
                pass
        
        # Pause-Indikator
        if self.paused:
            try:
                font = pygame.font.Font(None, 24)
                text = font.render("PAUSIERT", True, (255, 255, 0))
                rect = text.get_rect(center=(surface.get_width() // 2, 20))
                surface.blit(text, rect)
            except:
                pass
    
    def _draw_debug_info(self, surface: pygame.Surface) -> None:
        """Debug-Info zeichnen."""
        if not self.show_debug:
            return
            
        font = pygame.font.Font(None, 14)
        small_font = pygame.font.Font(None, 12)
        
        debug_surface = pygame.Surface((300, 150), pygame.SRCALPHA)
        debug_surface.fill((0, 0, 0, 180))
        
        y_offset = 10
        line_height = 16
        
        # Debug-Status
        text = font.render("🔍 DEBUG MODUS - FLINT", True, (255, 255, 0))
        debug_surface.blit(text, (10, y_offset))
        y_offset += line_height + 5
        
        # Player-Info
        if self.player:
            tile_x, tile_y = self.player.get_tile_position()
            text = small_font.render(f"Player: Tile ({tile_x}, {tile_y})", True, (255, 255, 255))
            debug_surface.blit(text, (10, y_offset))
            y_offset += line_height
        
        # Camera-Info
        if self.camera:
            text = small_font.render(f"Camera: ({int(self.camera.x)}, {int(self.camera.y)})", True, (255, 255, 255))
            debug_surface.blit(text, (10, y_offset))
            y_offset += line_height
        
        # Area-Info
        if self.current_area:
            text = small_font.render(f"Area: {self.current_area.name}", True, (255, 255, 255))
            debug_surface.blit(text, (10, y_offset))
            y_offset += line_height
            
            if hasattr(self.current_area, 'entities'):
                text = small_font.render(f"NPCs: {len(self.current_area.entities)}", True, (200, 200, 200))
                debug_surface.blit(text, (10, y_offset))
                y_offset += line_height
        
        # Encounter-Info
        text = small_font.render(f"Steps: {self.steps_since_encounter}", True, (200, 200, 200))
        debug_surface.blit(text, (10, y_offset))
        
        surface.blit(debug_surface, (10, 50))

    # === STORY-EVENTS ===
    
    def _check_story_events(self):
        """Check für Story-Events - hier passiert die Action!"""
        if not self.player or not hasattr(self.game, 'story_manager') or not self.game.story_manager:
            return

        if self.dialogue_box.is_open():
            return

        story = self.game.story_manager
        
        # Debug Map-Wechsel
        if hasattr(self.player, 'last_map'):
            if self.player.last_map != self.map_id:
                print(f"[Flint] Map-Wechsel: {self.player.last_map} → {self.map_id}")
        
        # Event 1: Erstes Mal Haus verlassen
        if self.map_id == "kohlenstadt" and not story.get_flag('left_house_first_time'):
            if hasattr(self.player, 'last_map') and self.player.last_map == "player_house":
                print("[Flint] Story-Event: Erstes Mal Haus verlassen!")
                story.set_flag('left_house_first_time', True)
                self._show_internal_monologue([
                    "Kohlenstadt... wat für'n Drecksloch.",
                    "Aber hey, hier is alles angefangen. Die alten Zechen, die Fossilien...",
                    "Mal gucken wat der durchgeknallte Professor diesmal ausgegraben hat."
                ])
                return
        
        # Event 2: Museum betreten ohne Starter
        if self.map_id == "museum" and not story.get_flag('has_starter'):
            if not story.get_flag('professor_intro_started'):
                print("[Flint] Story-Event: Professor-Intro!")
                story.set_flag('professor_intro_started', True)
                self._trigger_professor_fossil_intro()
                return
    
    def _show_internal_monologue(self, lines: List[str]):
        """Zeigt internen Monolog."""
        if self.player:
            self.player.lock_movement(True)
        
        pages = [DialoguePage(line, None) for line in lines]
        self.dialogue_box.show_dialogue(
            pages,
            callback=lambda _: self._on_dialogue_complete()
        )
    
    def _trigger_professor_fossil_intro(self):
        """Professor Budde's verrückte Fossil-Show!"""
        if self.player:
            self.player.lock_movement(True)
        
        dialogue_pages = [
            DialoguePage("Ach, da bisse ja endlich, du Schlafmütze!", "Prof. Budde"),
            DialoguePage("Weißte wat? Ich hab's geschafft! Die verdammten Viecher sind wieder da!", "Prof. Budde"),
            DialoguePage("Jahrmillionen alte Monster aus'm Kohleflöz!", "Prof. Budde"),
            DialoguePage("Hör ma, du willst doch die Trials machen, wa?", "Prof. Budde"),
            DialoguePage("Ohne Monster kommste da nich weit, Junge!", "Prof. Budde"),
            DialoguePage("Ich geb dir eins von meinen Babys. Aber pass drauf auf!", "Prof. Budde")
        ]
        
        self.dialogue_box.show_dialogue(
            dialogue_pages,
            callback=lambda _: self._go_to_fossil_selection()
        )
    
    def _go_to_fossil_selection(self):
        """Ab zur Fossil-Auswahl!"""
        if self.player:
            self.player.lock_movement(False)
        
        print("[Flint] Wechsel zur Starter-Auswahl")
        from engine.scenes.starter_scene import StarterScene
        self.game.push_scene(StarterScene)
    
    # === INTERAKTIONEN ===
    
    def _handle_interaction(self, tile_pos: Tuple[int, int]) -> None:
        """Handle Interaktion an Tile-Position."""
        tile_x, tile_y = tile_pos
        
        # Check NPCs
        for entity in self.current_area.entities:
            entity_tile = entity.get_tile_position()
            if entity_tile == tile_pos and entity.interactable:
                from engine.world.npc import NPC
                if isinstance(entity, NPC):
                    entity.on_interact(self.player)
                
                # Face NPC
                if hasattr(entity, 'grid_x') and hasattr(entity, 'grid_y'):
                    dx = entity.grid_x - self.player.grid_x
                    dy = entity.grid_y - self.player.grid_y
                    entity.direction = Direction.from_vector(-dx, -dy)
                
                self._interact_with_entity(entity)
                return
        
        # Check Triggers
        if hasattr(self.current_area, 'map_data') and self.current_area.map_data:
            for trigger in self.current_area.map_data.triggers:
                if trigger.x == tile_x and trigger.y == tile_y:
                    self._execute_trigger(trigger)
                    return
    
    def _interact_with_entity(self, entity: Entity) -> None:
        """Interagiere mit Entity."""
        if self.dialogue_box.is_open():
            return
            
        if self.player:
            self.player.lock_movement(True)
        
        # Verwende dialogue_id falls vorhanden
        if hasattr(entity, 'dialogue_id') and entity.dialogue_id:
            self._show_npc_dialogue(entity.dialogue_id, entity.name)
            return
        
        # Fallback-Dialog
        pages = [DialoguePage(
            text="Ey, wat willze?",
            speaker=entity.name
        )]
        self.dialogue_box.show_dialogue(
            pages,
            callback=lambda _: self._on_dialogue_complete()
        )
    
    def _show_npc_dialogue(self, dialogue_id: str, speaker_name: str) -> None:
        """Zeige Dialog aus dialogues.json."""
        dialogues_data = resources.load_json("game_data/dialogues.json")
        if not dialogues_data or dialogue_id not in dialogues_data:
            pages = [DialoguePage(
                text="Moin! Alles klar bei dir?",
                speaker=speaker_name
            )]
            self.dialogue_box.show_dialogue(
                pages,
                callback=lambda _: self._on_dialogue_complete()
            )
            return
        
        dialogue_data = dialogues_data[dialogue_id]
        text_lines = dialogue_data.get("text", ["..."])
        
        pages = []
        for line in text_lines:
            pages.append(DialoguePage(text=line, speaker=speaker_name))
        
        self.dialogue_box.show_dialogue(
            pages,
            callback=lambda _: self._on_dialogue_complete()
        )
    
    # === WARPS ===
    
    def _check_warp_at_position(self, tile_x: int, tile_y: int):
        """Check für Warp an Position."""
        if not self.current_area:
            return
        
        # Lade Warps aus warps.json
        warps_data = resources.load_json("game_data/warps.json")
        if not warps_data:
            return
        
        current_map_warps = warps_data.get(self.map_id, {})
        
        for warp_name, warp_info in current_map_warps.items():
            warp_pos = warp_info.get("position", [])
            if len(warp_pos) == 2 and warp_pos[0] == tile_x and warp_pos[1] == tile_y:
                from engine.world.map_loader import Warp
                warp = Warp(
                    x=tile_x,
                    y=tile_y,
                    to_map=warp_info.get("destination_map"),
                    to_x=warp_info.get("destination_position", [5, 5])[0],
                    to_y=warp_info.get("destination_position", [5, 5])[1],
                    direction=warp_info.get("direction"),
                    transition_type=warp_info.get("type", "fade")
                )
                self._execute_warp(warp)
                return
    
    def _execute_warp(self, warp: Warp) -> None:
        """Führe Warp aus."""
        warp_data = {
            'target_map': warp.to_map,
            'spawn_x': warp.to_x,
            'spawn_y': warp.to_y,
            'direction': warp.direction,
            'transition_type': getattr(warp, 'transition_type', 'fade'),
            'spawn_point': getattr(warp, 'spawn_point', 'default')
        }
        
        MapTransition.execute_transition(self.game, warp_data)
    
    def _execute_trigger(self, trigger: Trigger) -> None:
        """Führe Trigger aus."""
        if trigger.event == "sign":
            text = trigger.args.get('text', 'Ein Schild, aber nix drauf.')
            self.dialogue_box.show_text(text)
        elif trigger.event == "dialogue":
            pages = []
            for page_data in trigger.args.get('pages', []):
                pages.append(DialoguePage(
                    text=page_data.get('text', '...'),
                    speaker=page_data.get('speaker')
                ))
            if pages:
                self.dialogue_box.show_dialogue(pages)
    
    def _handle_collision_event(self, tile_x: int, tile_y: int):
        """Handle Kollision mit Tile."""
        if hasattr(self.current_area, 'map_data') and self.current_area.map_data:
            for trigger in self.current_area.map_data.triggers:
                if trigger.x == tile_x and trigger.y == tile_y:
                    if trigger.event == "sign":
                        self._execute_trigger(trigger)
                        break
    
    # === ENCOUNTERS ===
    
    def _check_encounter(self, tile_x: int, tile_y: int, steps: int) -> None:
        """Check für Random Encounter."""
        if not self.encounter_enabled or not self.current_area or self.in_battle:
            return
        
        self.steps_since_encounter += 1
        
        if self.steps_since_encounter < self.min_steps_between_encounters:
            return
        
        # Get Terrain-Typ aus der Map
        tile_type = None
        if hasattr(self.current_area, 'map_data') and self.current_area.map_data:
            # Check Tile Layer 1 (main terrain layer)
            if 'Tile Layer 1' in self.current_area.map_data.layers:
                layer = self.current_area.map_data.layers['Tile Layer 1']
                if 0 <= tile_y < len(layer) and 0 <= tile_x < len(layer[tile_y]):
                    tile_type = layer[tile_y][tile_x]
                    print(f"[DEBUG] Tile at ({tile_x}, {tile_y}) - Tile ID: {tile_type}")
        
        # Check für Gras-Tiles nur auf Route 1
        if self.map_id == "route1" and tile_type == 29:  # NUR Tile ID 29 ist hohes Gras auf Route 1
            print(f"[DEBUG] Grass tile at ({tile_x}, {tile_y})")
            if random.random() < self.current_area.encounter_rate:
                print(f"[Flint] Encounter triggered auf Grass-Tile {tile_type}!")
                self.encounter_check_pending = True
        elif self.map_id == "kohlenstadt" and tile_type in [2, 5]:  # Fallback für Kohlenstadt
            if random.random() < self.current_area.encounter_rate:
                print(f"[Flint] Encounter triggered auf Grass-Tile {tile_type}!")
                self.encounter_check_pending = True
    
    def _execute_encounter_check(self):
        """Führe Encounter aus."""
        if not self.game.party_manager.party.get_conscious_members():
            return
        
        self._start_battle()
    
    def _start_battle(self) -> None:
        """Starte Kampf!"""
        if self.in_battle:
            return
        
        if not self.game.party_manager.party.get_conscious_members():
            self.dialogue_box.show_text(
                "Du hast keine kampffähigen Monster! Hol dir erst eins vom Professor!",
                callback=lambda _: None
            )
            return
        
        self.in_battle = True
        self.steps_since_encounter = 0
        
        wild_monster = self._generate_wild_monster()
        
        if not wild_monster:
            self.dialogue_box.show_text(
                "Keine Monster hier! (Encounter-Daten fehlen)",
                callback=lambda _: setattr(self, 'in_battle', False)
            )
            return
        
        self.dialogue_box.show_text(
            f"Ein wildes {wild_monster.species_name} erscheint!",
            callback=lambda _: self._transition_to_battle(wild_monster)
        )
    
    def _generate_wild_monster(self) -> Optional[MonsterInstance]:
        """Generiere wildes Monster."""
        if not self.current_area or not self.current_area.encounter_table:
            # Fallback für Tests
            from engine.systems.monster_instance import MonsterInstance
            level = random.randint(2, 5)
            monster = MonsterInstance(
                species_id="5",
                name="Kohlekumpel",
                level=level,
                stats={'hp': 100, 'atk': 50, 'def': 40, 'mag': 35, 'res': 35, 'spd': 40}
            )
            # Set species as dict for compatibility
            monster.species = {'id': 5, 'name': 'Kohlekumpel'}
            # Initialize stat_stages
            monster.stat_stages = {'atk': 0, 'def': 0, 'mag': 0, 'res': 0, 'spd': 0}
            return monster
        
        total_weight = sum(enc['weight'] for enc in self.current_area.encounter_table)
        roll = random.randint(1, total_weight)
        
        current_weight = 0
        for encounter in self.current_area.encounter_table:
            current_weight += encounter['weight']
            if roll <= current_weight:
                from engine.systems.monster_instance import MonsterInstance
                level = random.randint(encounter['level_min'], encounter['level_max'])
                
                # Create monster with all required stats
                base_stat = 40 + level * 2
                stats = {
                    'hp': base_stat + 20,  # HP should be higher
                    'atk': base_stat,
                    'def': base_stat - 5,
                    'mag': base_stat - 10,
                    'res': base_stat - 10,
                    'spd': base_stat
                }
                
                # Calculate HP based on level
                hp_value = stats['hp'] + (level * 10)
                
                monster = MonsterInstance(
                    species_id=str(encounter['species_id']),
                    name=encounter['name'],
                    level=level,
                    stats=stats,
                    max_hp=hp_value,
                    current_hp=hp_value
                )
                
                # Set species as dict for compatibility
                monster.species = {
                    'id': encounter['species_id'],
                    'name': encounter['name'],
                    'rank': encounter.get('rank', 'F')
                }
                
                # Initialize stat_stages  
                monster.stat_stages = {'atk': 0, 'def': 0, 'mag': 0, 'res': 0, 'spd': 0}
                
                return monster
        
        return None
    
    def _create_route_1_encounter_table(self):
        """Route 1 Encounter-Tabelle mit F und E Rang."""
        try:
            monsters_data = self.game.resources.load_json("data/monsters.json")
            if not monsters_data:
                print("[Flint] monsters.json nicht gefunden")
                return self._get_fallback_encounter_table()
            
            f_rank = [m for m in monsters_data if m.get("rank") == "F"]
            e_rank = [m for m in monsters_data if m.get("rank") == "E"]
            
            selected_f = random.sample(f_rank, min(10, len(f_rank)))
            selected_e = random.sample(e_rank, min(10, len(e_rank)))
            
            encounter_table = []
            
            # 95% F-Rang
            f_weight = 95 // len(selected_f) if selected_f else 0
            for monster in selected_f:
                encounter_table.append({
                    "species_id": monster["id"],
                    "name": monster["name"],
                    "level_min": 3,
                    "level_max": 6,
                    "weight": f_weight,
                    "rank": "F"
                })
            
            # 5% E-Rang
            e_weight = max(1, 5 // len(selected_e)) if selected_e else 0
            for monster in selected_e:
                encounter_table.append({
                    "species_id": monster["id"],
                    "name": monster["name"],
                    "level_min": 5,
                    "level_max": 8,
                    "weight": e_weight,
                    "rank": "E"
                })
            
            print(f"[Flint] Route 1: {len(selected_f)} F-Rang, {len(selected_e)} E-Rang Monster")
            return encounter_table
            
        except Exception as e:
            print(f"[Flint] Fehler bei Encounter-Tabelle: {e}")
            return self._get_fallback_encounter_table()
    
    def _get_fallback_encounter_table(self):
        """Fallback Encounter-Tabelle."""
        return [
            {"species_id": 1, "name": "Glutstummel", "level_min": 3, "level_max": 6, "weight": 20, "rank": "F"},
            {"species_id": 5, "name": "Kohlekumpel", "level_min": 3, "level_max": 6, "weight": 20, "rank": "F"},
            {"species_id": 6, "name": "Kieselkrabbler", "level_min": 3, "level_max": 6, "weight": 20, "rank": "F"},
            {"species_id": 7, "name": "Flugratte", "level_min": 3, "level_max": 6, "weight": 20, "rank": "F"},
            {"species_id": 8, "name": "Wolkenfurz", "level_min": 3, "level_max": 6, "weight": 15, "rank": "F"},
            {"species_id": 21, "name": "Flammimp", "level_min": 5, "level_max": 8, "weight": 5, "rank": "E"},
        ]
    
    def _transition_to_battle(self, wild_monster: MonsterInstance):
        """Übergang zum Kampf."""
        monster_name = wild_monster.species.get('name', 'Unknown') if isinstance(wild_monster.species, dict) else getattr(wild_monster.species, 'name', wild_monster.name)
        print(f"[Flint] Starte Battle Transition zu {monster_name}")
        
        from engine.scenes.battle_scene import BattleScene
        
        # Direkt zur Battle Scene wechseln
        self.game.push_scene(
            BattleScene,
            player_team=None,
            enemy_team=[wild_monster],
            is_wild=True,
            background='grass'
        )
        
        self.in_battle = False
        print(f"[Flint] Battle Scene gestartet!")

# Ey, jetzt is der Code sauber! - Flint