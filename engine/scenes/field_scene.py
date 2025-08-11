"""
Field Scene for Untold Story
Main overworld gameplay scene with map, player, NPCs, and interactions
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


# ExtendedArea-Klasse entfernt - verursacht Konflikte!

def add_warp_methods_to_area(area):
    """Fügt die fehlenden Warp/Trigger-Methoden zur Area hinzu"""
    
    def get_warp_at(tile_x: int, tile_y: int):
        if hasattr(area, 'map_data') and hasattr(area.map_data, 'warps'):
            for warp in area.map_data.warps:
                if warp.x == tile_x and warp.y == tile_y:
                    return warp
        return None
    
    def get_trigger_at(tile_x: int, tile_y: int):
        if hasattr(area, 'map_data') and hasattr(area.map_data, 'triggers'):
            for trigger in area.map_data.triggers:
                if trigger.x == tile_x and trigger.y == tile_y:
                    return trigger
        return None
    
    def get_tile_type(tile_x: int, tile_y: int) -> int:
        if "ground" in area.layers:
            layer = area.layers["ground"]
            if 0 <= tile_y < len(layer) and 0 <= tile_x < len(layer[tile_y]):
                return layer[tile_y][tile_x]
        return 0
    
    # Füge Methoden zur Area-Instanz hinzu
    area.get_warp_at = get_warp_at
    area.get_trigger_at = get_trigger_at
    area.get_tile_type = get_tile_type
    
    # Debug: Zeige dass Methoden hinzugefügt wurden
    print(f"Added warp methods to area: {area.name}")
    print(f"  - get_warp_at: {hasattr(area, 'get_warp_at')}")
    print(f"  - get_trigger_at: {hasattr(area, 'get_trigger_at')}")
    print(f"  - get_tile_type: {hasattr(area, 'get_tile_type')}")
    
    return area

class FieldScene(Scene):
    """
    Main overworld gameplay scene.
    """
    
    def __init__(self, game: 'Game') -> None:
        """
        Initialize the field scene.
        
        Args:
            game: Game instance
        """
        super().__init__(game)
        
        # Initialize graphics systems
        self.sprite_manager = SpriteManager(self.game.resources)
        self.tile_renderer = TileRenderer(self.sprite_manager)
        
        # Enable debug output for tile rendering
        self.tile_renderer.set_debug(True)
        
        # Current area and map
        self.current_area: Optional[Area] = None
        self.map_id: str = ""
        
        # Player
        self.player: Optional[Player] = None
        
        # Camera
        self.camera: Optional[Camera] = None
        self.camera_config = CameraConfig()  # Verwende Standard-Konfiguration mit neuen Konstanten
        
        # UI elements
        self.dialogue_box = DialogueBox(
            x=10,
            y=120,
            width=300,
            height=50
        )
        
        # State flags
        self.show_debug = False
        self.show_grid = False
        self.show_collision = False
        self.show_entity_info = False
        self.show_tile_info = False
        self.show_camera_info = False
        self.show_performance_info = False
        self.paused = False
        self.in_battle = False
        
        # Encounter system
        self.encounter_enabled = True
        self.steps_since_encounter = 0
        self.min_steps_between_encounters = 10
        self.encounter_check_pending = False
        
        # Story flags and game state
        self.story_flags: Dict[str, bool] = {}
        self.game_variables: Dict[str, Any] = {}
        
        # Load graphics resources
        self._load_graphics()
        
        # Check if starter scene should be shown
        self._check_starter_requirement()
    
    def _load_graphics(self):
        """Load all graphical resources."""
        print("Loading graphics...")
        
        # Load tileset with smart scaling
        try:
            # Prüfe verschiedene Tile-Größen und skaliere entsprechend
            if self.game.resources.path_exists("tileset.png"):
                # Standard 16x16 tiles
                self.sprite_manager.load_tileset("tileset.png")
                print(f"Loaded {len(self.sprite_manager.tile_images)} tiles (16x16)")
            elif self.game.resources.path_exists("tiles_8x8/tileset.png"):
                # 8x8 tiles mit 2x scaling
                self.sprite_manager.load_tileset_scaled("tiles_8x8/tileset.png", 8, 16)
                print(f"Loaded {len(self.sprite_manager.tile_images)} tiles (8x8 -> 16x16)")
            elif self.game.resources.path_exists("tiles_64x64/tileset.png"):
                # 64x64 tiles mit downscaling
                self.sprite_manager.load_tileset_scaled("tiles_64x64/tileset.png", 64, 16)
                print(f"Loaded {len(self.sprite_manager.tile_images)} tiles (64x64 -> 16x16)")
            else:
                # Keine Fallback-Tiles mehr erstellen - verwende echte Sprites
                print("No tileset found, loading individual sprites")
                self._load_individual_sprites()
                
            # Debug: Zeige geladene Tiles
            print(f"Tiles loaded: {len(self.sprite_manager.tile_images)}")
            print(f"Tile IDs available: {list(self.sprite_manager.tile_images.keys())}")
            
        except Exception as e:
            print(f"Failed to load tileset: {e}")
            # Keine Fallback-Tiles mehr erstellen
            self._load_individual_sprites()
        
        # Load large tiles (64x64) - diese haben Priorität
        try:
            if self.sprite_manager.load_large_tiles():
                print(f"Large tiles loaded: {len([k for k in self.sprite_manager.sprite_cache.keys() if k.endswith('.png')])}")
            else:
                print("No large tiles found")
        except Exception as e:
            print(f"Failed to load large tiles: {e}")
        
        # Load tile mapping
        try:
            if self.game.resources.data_path_exists("tile_mapping.json"):
                # Tile mapping wird bereits vom TilesetManager geladen
                print("Tile mapping available via TilesetManager")
            else:
                print("Tile mapping not found, using default")
        except Exception as e:
            print(f"Failed to load tile mapping: {e}")
        
        # Load monster sprites
        try:
            with open('data/monsters.json', 'r', encoding='utf-8') as f:
                monster_data = json.load(f)
                # Monster sprites werden bereits vom SpriteManager geladen
                print(f"Monster data loaded: {len(monster_data)} monsters")
        except Exception as e:
            print(f"Failed to load monster data: {e}")
            # Continue without monster sprites
    
    def _load_individual_sprites(self):
        """Load individual sprites from the sprites directory."""
        print("Loading individual sprites...")
        
        # Preload wichtige Sprites
        self.preload_sprites = [
            "player.png",
            "Void_large.png",  # Verwende _large Version
            "Grass-flat_large.png",  # Verwende _large Version
            "Path_large.png",  # Verwende _large Version
            "Flooring-type-01_large.png"  # Verwende _large Version
        ]
        
        for sprite_path in self.preload_sprites:
            try:
                # Versuche zuerst über den SpriteManager zu laden
                if hasattr(self, 'sprite_manager') and self.sprite_manager:
                    sprite = self.sprite_manager.load_sprite(sprite_path)
                    if sprite:
                        print(f"  {sprite_path} geladen via SpriteManager")
                        continue
                
                # Fallback: Versuche direkt zu laden
                full_path = os.path.join("sprites", sprite_path)
                if os.path.exists(full_path):
                    sprite = pygame.image.load(full_path).convert_alpha()
                    if sprite:
                        # Wenn es ein _large Sprite ist, verwende ihn direkt
                        if "_large.png" in sprite_path:
                            print(f"  {sprite_path} direkt geladen: {sprite.get_size()}")
                        else:
                            # Versuche _large Version zu finden
                            normal_path = sprite_path.replace("_large.png", ".png")
                            large_path = sprite_path.replace(".png", "_large.png")
                            if os.path.exists(os.path.join("sprites", large_path)):
                                large_sprite = pygame.image.load(os.path.join("sprites", large_path)).convert_alpha()
                                if large_sprite:
                                    print(f"  {large_path} als _large Version geladen: {large_sprite.get_size()}")
                                else:
                                    print(f"  {sprite_path} geladen: {sprite.get_size()}")
                            else:
                                print(f"  {sprite_path} geladen: {sprite.get_size()}")
                        continue
                
                print(f"  {sprite_path} konnte nicht geladen werden")
                
            except Exception as e:
                print(f"  Fehler beim Laden von {sprite_path}: {e}")
    
    def _initialize_player(self):
        """Initialize the player with Pokémon-style movement"""
        from engine.world.player import Player
        from engine.world.tiles import TILE_SIZE
        
        # Create player at default position
        self.player = Player(5 * TILE_SIZE, 5 * TILE_SIZE)
        
        # Verbinde den Player mit dem Game-Objekt für Sprite-Zugriff
        self.player.game = self.game
        
        # Verbinde den Player mit dem SpriteManager der FieldScene
        if hasattr(self, 'sprite_manager'):
            self.player.sprite_manager = self.sprite_manager
            print(f"✅ Player mit FieldScene SpriteManager verbunden")
        else:
            print("⚠️  Kein SpriteManager in FieldScene verfügbar")
        
        # Set up callbacks
        self.player.set_interact_callback(self._handle_interaction)
        self.player.set_warp_callback(self._check_warp_at_position)
        self.player.set_encounter_callback(self._check_encounter)
        self.player.set_collision_callback(self._handle_collision_event)
        
        # Lade das Player-Sprite neu mit dem SpriteManager
        self.player._load_player_sprite()
        
        print(f"Player initialisiert: {self.player.name}")
        print(f"Player Position: ({self.player.x}, {self.player.y})")
        print(f"Player Sprite geladen: {self.player.sprite_surface is not None}")
    
    def _check_starter_requirement(self):
        """Check if player needs to choose a starter."""
        if not hasattr(self.game, 'party_manager'):
            return
            
        # Check if party is empty
        if self.game.party_manager.party.is_empty():
            # Check if this is first time
            if not self.game.story_manager.get_flag('has_starter'):
                # Need to choose starter!
                from engine.scenes.starter_scene import StarterScene
                self.game.push_scene(StarterScene, game=self.game)
    
    def enter(self, **kwargs) -> None:
        """
        Enter the field scene.
        
        Args:
            **kwargs: Scene parameters (map_id, spawn_point, etc.)
        """
        super().enter(**kwargs)
        
        # Verbinde den SpriteManager mit der Game-Klasse
        if hasattr(self.game, 'sprite_manager'):
            self.sprite_manager = self.game.sprite_manager
            print(f"✅ SpriteManager in FieldScene verbunden: {len(self.sprite_manager.sprite_cache)} Sprites")
        else:
            print("⚠️  Kein SpriteManager in Game verfügbar")
        
        # Get parameters
        map_id = kwargs.get('map_id', 'player_house')  # Start im Player House
        spawn_point = kwargs.get('spawn_point', 'bed')
        
        # Load the map
        self.load_map(map_id)
        
        # Position player at spawn point
        if spawn_point and self.player:
            self._position_player_at_spawn(spawn_point)
        
        # Reset encounter flag
        self.in_battle = False
        
        # Start area music if specified
        if self.current_area and self.current_area.map_data.properties.get('music'):
            try:
                music_file = self.current_area.map_data.properties['music']
                resources.load_music(music_file, loops=-1, fade_ms=1000)
            except:
                pass
    
    def load_map(self, map_name: str, spawn_x: int = 5, spawn_y: int = 5):
        """Lädt eine neue Map und positioniert Spieler"""
        try:
            print(f"Loading map: {map_name}")
            
            # Load map data
            from engine.world.map_loader import MapLoader
            map_data = MapLoader.load_map(map_name)
            
            # Validate map
            issues = MapLoader.validate_map(map_data)
            if issues:
                for issue in issues:
                    print(f"Map warning: {issue}")
            
            # Create area - Verwende die normale Area-Klasse aus area.py
            from engine.world.area import Area
            self.current_area = Area(
                id=map_data.id,
                name=map_data.name,
                width=map_data.width,
                height=map_data.height,
                layers=map_data.layers,
                properties=map_data.properties or {}
            )
            self.map_id = map_name
            
            # Füge zusätzliche Attribute hinzu die ExtendedArea hatte
            self.current_area.map_data = map_data
            self.current_area.entities = []
            self.current_area.npcs = []
            self.current_area.encounter_rate = 0.1
            self.current_area.encounter_table = []
            
            # Füge Warp/Trigger-Methoden zur Area hinzu
            self.current_area = add_warp_methods_to_area(self.current_area)
            
            # Debug: Zeige Map-Informationen
            print(f"Map loaded: {self.current_area.name}")
            print(f"Map size: {self.current_area.width}x{self.current_area.height}")
            print(f"Layers: {list(self.current_area.layers.keys())}")
            
            # Load encounter data for this area
            self._load_encounter_data()
            
            # Create or update camera
            from engine.world.tiles import TILE_SIZE
            if not self.camera:
                from engine.world.camera import Camera, CameraConfig
                self.camera = Camera(
                    viewport_width=self.game.logical_size[0],
                    viewport_height=self.game.logical_size[1],
                    world_width=self.current_area.width * TILE_SIZE,
                    world_height=self.current_area.height * TILE_SIZE,
                    config=self.camera_config
                )
            else:
                # Aktualisiere Kamera-Weltgröße
                world_width = self.current_area.width * TILE_SIZE
                world_height = self.current_area.height * TILE_SIZE
                self.camera.set_world_size(world_width, world_height)
            
            # Create player if doesn't exist
            if not self.player:
                self._initialize_player()
            
            # Set collision map for player
            collision_layer = map_data.layers.get('collision', [])
            self.player.set_collision_map(
                collision_layer,
                map_data.width,
                map_data.height
            )
            
            # Setze Spieler-Position
            self.player.set_tile_position(spawn_x, spawn_y)
            
            # Zentriere Kamera sofort auf Spieler
            self.camera.center_on(
                self.player.x + self.player.width // 2,
                self.player.y + self.player.height // 2,
                immediate=True
            )
            
            # Setze Kamera auf Spieler-Entity für kontinuierliches Follow
            self.camera.set_follow_target(self.player)
            
            # Debug output
            print(f"Player positioned at tile ({spawn_x}, {spawn_y})")
            print(f"Player world position: ({self.player.x}, {self.player.y})")
            print(f"Camera position: ({self.camera.x}, {self.camera.y})")
            
            # Load NPCs and entities for this area
            self._load_area_entities()
            
            print(f"Map {map_name} loaded successfully!")
            
        except Exception as e:
            print(f"Error loading map {map_name}: {e}")
            import traceback
            traceback.print_exc()
            # Load a fallback empty map
            self._create_empty_area()
    
    def _load_encounter_data(self):
        """Load encounter data for current area."""
        if not self.current_area:
            return
        
        # Default encounter table based on area
        if self.map_id == "kohlenstadt":
            # Kohlenstadt - starter area encounters
            self.current_area.encounter_table = [
                {"species_id": 5, "name": "Rattfratz", "level_min": 2, "level_max": 4, "weight": 40},
                {"species_id": 6, "name": "Taubsi", "level_min": 2, "level_max": 5, "weight": 30},
                {"species_id": 7, "name": "Raupie", "level_min": 3, "level_max": 4, "weight": 20},
                {"species_id": 8, "name": "Hornliu", "level_min": 3, "level_max": 5, "weight": 10},
            ]
            self.current_area.encounter_rate = 0.15  # 15% chance in grass
            
        elif self.map_id == "route_2":
            # Slightly harder area
            self.current_area.encounter_table = [
                {"species_id": 5, "name": "Rattfratz", "level_min": 4, "level_max": 6, "weight": 30},
                {"species_id": 9, "name": "Nidoran", "level_min": 4, "level_max": 6, "weight": 25},
                {"species_id": 10, "name": "Piepi", "level_min": 5, "level_max": 7, "weight": 20},
                {"species_id": 11, "name": "Pummeluff", "level_min": 5, "level_max": 7, "weight": 15},
                {"species_id": 12, "name": "Zubat", "level_min": 5, "level_max": 8, "weight": 10},
            ]
            self.current_area.encounter_rate = 0.12
    
    def _create_empty_area(self) -> None:
        """Create an empty fallback area."""
        from engine.world.map_loader import MapData
        from engine.world.tiles import TILE_SIZE
        
        # Create minimal map data
        empty_map = MapData(
            id="empty",
            name="Empty Area",
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
        self.current_area = Area(
            id=empty_map.id,
            name=empty_map.name,
            width=empty_map.width,
            height=empty_map.height,
            layers=empty_map.layers,
            properties=empty_map.properties or {}
        )
        
        # Füge zusätzliche Attribute hinzu
        self.current_area.map_data = empty_map
        self.current_area.entities = []
        self.current_area.npcs = []
        self.current_area.encounter_rate = 0.1
        self.current_area.encounter_table = []
    
    def _load_area_entities(self) -> None:
        """Load NPCs and other entities for the current area."""
        from engine.world.tiles import TILE_SIZE
        
        # This would load from data files
        # For now, create some test NPCs
        
        if self.map_id == "kohlenstadt":
            # Create Professor NPC if no starter yet
            if not self.game.story_manager.get_flag('has_starter'):
                prof = Entity(
                    x=8 * TILE_SIZE,
                    y=10 * TILE_SIZE,
                    width=14,
                    height=14
                )
                prof.name = "Professor Budde"
                prof.interactable = True
                self.current_area.add_entity(prof)
            
            # Create a test NPC
            npc = Entity(
                x=12 * TILE_SIZE,
                y=8 * TILE_SIZE,
                width=14,
                height=14
            )
            npc.name = "Ruhrpott Karl"
            npc.interactable = True
            self.current_area.add_entity(npc)
    
    def _position_player_at_spawn(self, spawn_point: str) -> None:
        """
        Position player at a named spawn point.
        
        Args:
            spawn_point: Name of spawn point or tile coordinates
        """
        if not self.player or not self.current_area:
            return
        
        # Check for named spawn points in map properties
        spawn_data = self.current_area.map_data.properties.get('spawns', {})
        
        if spawn_point in spawn_data:
            spawn = spawn_data[spawn_point]
            self.player.set_tile_position(spawn['x'], spawn['y'])
            if 'direction' in spawn:
                # Set facing direction
                from engine.world.entity import Direction
                self.player.direction = Direction[spawn['direction'].upper()]
        elif spawn_point == "door":
            # Default door position
            self.player.set_tile_position(10, 10)
        else:
            # Default center position
            self.player.set_tile_position(
                self.current_area.map_data.width // 2,
                self.current_area.map_data.height // 2
            )
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle input events.
        
        Args:
            event: pygame event to process
            
        Returns:
            True if event was handled
        """
        # Let dialogue handle input first
        if self.dialogue_box.is_open():
            return self.dialogue_box.handle_input(event)
        
        # Check for pause
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_ESCAPE, pygame.K_q]:
                self._toggle_pause()
                return True
            elif event.key == pygame.K_TAB:
                # Debug-Features umschalten
                self.show_debug = not self.show_debug
                if self.show_debug:
                    print("🔍 Debug-Modus aktiviert!")
                    print("  G - Grid anzeigen/verstecken")
                    print("  C - Kollision anzeigen/verstecken")
                    print("  E - Entity-Info anzeigen/verstecken")
                    print("  T - Tile-Info anzeigen/verstecken")
                    print("  V - Kamera-Info anzeigen/verstecken")
                    print("  P - Performance-Info anzeigen/verstecken")
                else:
                    print("🔍 Debug-Modus deaktiviert")
                return True
            elif event.key == pygame.K_g:
                self.show_grid = not self.show_grid
                print(f"📐 Grid: {'AN' if self.show_grid else 'AUS'}")
                return True
            elif event.key == pygame.K_c:
                self.show_collision = not self.show_collision
                print(f"🚫 Kollision: {'AN' if self.show_collision else 'AUS'}")
                return True
            elif event.key == pygame.K_e:
                self.show_entity_info = not self.show_entity_info
                print(f"👤 Entity-Info: {'AN' if self.show_entity_info else 'AUS'}")
                return True
            elif event.key == pygame.K_t:
                self.show_tile_info = not self.show_tile_info
                print(f"🧱 Tile-Info: {'AN' if self.show_tile_info else 'AUS'}")
                return True
            elif event.key == pygame.K_v:
                self.show_camera_info = not self.show_camera_info
                print(f"📷 Kamera-Info: {'AN' if self.show_camera_info else 'AUS'}")
                return True
            elif event.key == pygame.K_p:
                self.show_performance_info = not self.show_performance_info
                print(f"⚡ Performance-Info: {'AN' if self.show_performance_info else 'AUS'}")
                return True
            elif event.key == pygame.K_b and self.game.debug_mode:
                # Debug: Force battle
                self._start_battle()
                return True
        
        return False
    
    def update(self, dt: float) -> None:
        """Update the field scene."""
        # Update dialogue
        if hasattr(self, 'dialogue_box'):
            self.dialogue_box.update(dt)
            
            # Don't update gameplay if dialogue is open or paused
            if self.dialogue_box.is_open() or self.paused:
                return
        
        # Check for pending encounter
        if self.encounter_check_pending and not self.in_battle:
            self.encounter_check_pending = False
            self._execute_encounter_check()
        
        # Update player with input
        if self.player and not self.in_battle:
            self.player.handle_input(self.game, dt)
            self.player.update(dt)
        
        # WICHTIG: Update camera NACH Player-Update!
        if self.camera:
            self.camera.update(dt)
        
        # Update area entities
        if self.current_area and hasattr(self.current_area, 'entities'):
            for entity in self.current_area.entities:
                entity.update(dt)
        
        # Check for story events
        if hasattr(self, '_check_story_events'):
            self._check_story_events()
        
        # Update cutscene manager
        if hasattr(self.game, 'cutscene_manager') and self.game.cutscene_manager.active_cutscene:
            self.game.cutscene_manager.update(dt)
    
    def draw(self, surface: pygame.Surface) -> None:
        """Zeichnet die Szene mit korrekter Layer-Reihenfolge"""
        if not self.current_area:
            # Debug: Zeige Fehler wenn keine Area geladen
            font = pygame.font.Font(None, 24)
            text = font.render("FEHLER: Keine Area geladen!", True, (255, 0, 0))
            surface.blit(text, (50, 50))
            return
        
        # Verwende den neuen RenderManager für koordiniertes Rendering
        if not hasattr(self, 'render_manager'):
            from engine.graphics.render_manager import RenderManager
            self.render_manager = RenderManager()
            self.render_manager.player = self.player
        
        # Aktiviere Debug-Modus für RenderManager
        self.render_manager.set_debug_mode(True)
        
        # UI-Elemente sammeln
        ui_elements = []
        if hasattr(self, 'dialogue_box'):
            ui_elements.append(self.dialogue_box)
        
        # Rendere komplette Szene mit RenderManager
        self.render_manager.render_scene(surface, self.current_area, self.camera, ui_elements)
        
        # Optional: Debug-Grid
        if self.show_grid:
            from engine.world.tiles import draw_grid
            draw_grid(surface, int(self.camera.x), int(self.camera.y))
        
        # Debug-Info anzeigen wenn aktiviert
        if self.show_debug:
            self._draw_debug_info(surface)
        
        # Draw UI elements
        self._draw_ui(surface)
    
    def _draw_ui(self, surface: pygame.Surface) -> None:
        """Draw UI elements."""
        # Draw area name (fade in/out)
        if self.current_area:
            try:
                font = pygame.font.Font(None, 18)
                text = font.render(self.current_area.name, True, (255, 255, 255))
                text.set_alpha(200)
                surface.blit(text, (5, 5))
            except:
                pass
        
        # Draw pause indicator
        if self.paused:
            try:
                font = pygame.font.Font(None, 24)
                text = font.render("PAUSIERT", True, (255, 255, 0))
                rect = text.get_rect(center=(surface.get_width() // 2, 20))
                surface.blit(text, rect)
            except:
                pass
        
        # Draw encounter steps counter (debug)
        if self.game.debug_mode:
            try:
                font = pygame.font.Font(None, 12)
                text = font.render(f"Steps: {self.steps_since_encounter}", True, (255, 255, 0))
                surface.blit(text, (5, 25))
            except:
                pass
        
        # Draw debug information
        if self.show_debug:
            self._draw_debug_info(surface)
    
    def _draw_debug_info(self, surface: pygame.Surface) -> None:
        """Draw debug information overlay."""
        if not self.show_debug:
            return
            
        # Font für Debug-Info
        font = pygame.font.Font(None, 14)
        small_font = pygame.font.Font(None, 12)
        
        # Hintergrund für Debug-Info
        debug_surface = pygame.Surface((300, 200), pygame.SRCALPHA)
        debug_surface.fill((0, 0, 0, 180))
        
        y_offset = 10
        line_height = 16
        
        # Debug-Status
        status_text = f"🔍 DEBUG MODUS AKTIV"
        text = font.render(status_text, True, (255, 255, 0))
        debug_surface.blit(text, (10, y_offset))
        y_offset += line_height + 5
        
        # Player-Info
        if self.player:
            player_text = f"👤 Player: ({self.player.x}, {self.player.y})"
            text = small_font.render(player_text, True, (255, 255, 255))
            debug_surface.blit(text, (10, y_offset))
            y_offset += line_height
            
            tile_x, tile_y = self.player.get_tile_position()
            tile_text = f"   Tile: ({tile_x}, {tile_y})"
            text = small_font.render(tile_text, True, (200, 200, 200))
            debug_surface.blit(text, (10, y_offset))
            y_offset += line_height
        
        # Camera-Info
        if self.camera:
            cam_text = f"📷 Camera: ({self.camera.x}, {self.camera.y})"
            text = small_font.render(cam_text, True, (255, 255, 255))
            debug_surface.blit(text, (10, y_offset))
            y_offset += line_height
        
        # Area-Info
        if self.current_area:
            area_text = f"🗺️ Area: {self.current_area.name}"
            text = small_font.render(area_text, True, (255, 255, 255))
            debug_surface.blit(text, (10, y_offset))
            y_offset += line_height
            
            map_text = f"   Size: {self.current_area.map_data.width}x{self.current_area.map_data.height}"
            text = small_font.render(map_text, True, (200, 200, 200))
            debug_surface.blit(text, (10, y_offset))
            y_offset += line_height
            
            entity_text = f"   Entities: {len(self.current_area.entities)}"
            text = small_font.render(entity_text, True, (200, 200, 200))
            debug_surface.blit(text, (10, y_offset))
            y_offset += line_height
        
        # Debug-Features Status
        y_offset += 5
        features_text = "Debug-Features:"
        text = small_font.render(features_text, True, (255, 255, 0))
        debug_surface.blit(text, (10, y_offset))
        y_offset += line_height
        
        features = [
            ("Grid", self.show_grid, "G"),
            ("Kollision", self.show_collision, "C"),
            ("Entity-Info", self.show_entity_info, "E"),
            ("Tile-Info", self.show_tile_info, "T"),
            ("Kamera-Info", self.show_camera_info, "V"),
            ("Performance", self.show_performance_info, "P")
        ]
        
        for feature_name, is_active, key in features:
            status = "AN" if is_active else "AUS"
            color = (0, 255, 0) if is_active else (255, 100, 100)
            feature_text = f"   {key}: {feature_name} - {status}"
            text = small_font.render(feature_text, True, color)
            debug_surface.blit(text, (10, y_offset))
            y_offset += line_height
        
        # Debug-Info auf den Screen zeichnen
        surface.blit(debug_surface, (10, 50))
    
    def _check_warps(self) -> None:
        """Check if player is on a warp tile."""
        if not self.player or not self.current_area:
            return
        
        # Get player's current tile
        tile_x, tile_y = self.player.get_tile_position()
        
        # Check for warp
        warp = self.current_area.get_warp_at(tile_x, tile_y)
        if warp:
            self._execute_warp(warp)
    
    def _execute_warp(self, warp: Warp) -> None:
        """
        Execute a warp to another map with smooth transitions.
        
        Args:
            warp: Warp data
        """
        # Prepare warp data for transition system
        warp_data = {
            'target_map': warp.to_map,
            'spawn_x': warp.to_x,
            'spawn_y': warp.to_y,
            'direction': warp.direction,
            'transition_type': getattr(warp, 'transition_type', 'fade'),
            'spawn_point': getattr(warp, 'spawn_point', 'default')
        }
        
        # Execute transition based on warp type
        MapTransition.execute_transition(self.game, warp_data)
        
        # Note: The actual map loading and player positioning is now handled
        # by the transition system, so we don't need to do it here anymore
    
    def _check_triggers(self) -> None:
        """Check for automatic triggers at player position."""
        if not self.player or not self.current_area:
            return
        
        # Get player's current tile
        tile_x, tile_y = self.player.get_tile_position()
        
        # Check for trigger
        trigger = self.current_area.get_trigger_at(tile_x, tile_y)
        if trigger and trigger.event == "auto":
            self._execute_trigger(trigger)
    
    def _handle_interaction(self, tile_pos: Tuple[int, int]) -> None:
        """
        Handle player interaction at a tile position.
        
        Args:
            tile_pos: (tile_x, tile_y) position to interact with
        """
        tile_x, tile_y = tile_pos
        
        # Check for NPCs
        for entity in self.current_area.entities:
            entity_tile = entity.get_tile_position()
            if entity_tile == tile_pos and entity.interactable:
                # Face the NPC
                dx = entity.grid_x - self.player.grid_x
                dy = entity.grid_y - self.player.grid_y
                entity.direction = Direction.from_vector(-dx, -dy)
                
                # Interact
                self._interact_with_entity(entity)
                return
        
        # Check for triggers
        for trigger in self.current_area.map_data.triggers:
            if trigger.x == tile_x and trigger.y == tile_y:
                self._execute_trigger(trigger)
                return
        
        # Check for hidden items (optional)
        self._check_hidden_item(tile_x, tile_y)
    
    def _check_warp_at_position(self, tile_x: int, tile_y: int):
        """Check for warp at specific tile position"""
        if not self.current_area:
            return
        
        # Check for warp at this position
        for warp in self.current_area.map_data.warps:
            if warp.x == tile_x and warp.y == tile_y:
                self._execute_warp(warp)
                break
    
    def _handle_collision_event(self, tile_x: int, tile_y: int):
        """Handle collision with solid tile"""
        # Check if it's a sign or interactable solid object
        for trigger in self.current_area.map_data.triggers:
            if trigger.x == tile_x and trigger.y == tile_y:
                # Auto-interact with signs when walking into them
                if trigger.event == "sign":
                    self._execute_trigger(trigger)
                    break
    
    def _check_hidden_item(self, tile_x: int, tile_y: int):
        """Check for hidden items at position"""
        # Hidden items system (optional)
        hidden_items = self.game_variables.get('hidden_items', {})
        key = f"{self.map_id}_{tile_x}_{tile_y}"
        
        if key in hidden_items and not hidden_items[key]['found']:
            item = hidden_items[key]
            self.dialogue_box.show_text(
                f"Du hast {item['name']} gefunden!",
                callback=lambda _: self._collect_hidden_item(key, item)
            )
    
    def _collect_hidden_item(self, key: str, item: dict):
        """Collect a hidden item"""
        # Mark as found
        hidden_items = self.game_variables.get('hidden_items', {})
        hidden_items[key]['found'] = True
        
        # Add to inventory
        # self.game.inventory.add_item(item['id'], item.get('quantity', 1))
    
    def _execute_trigger(self, trigger: Trigger) -> None:
        """
        Execute a trigger event.
        
        Args:
            trigger: Trigger data
        """
        if trigger.event == "sign":
            # Show sign text
            text = trigger.args.get('text', 'Ein Schild, aber nix drauf.')
            self.dialogue_box.show_text(text)
            
        elif trigger.event == "dialogue":
            # Show dialogue sequence
            pages = []
            for page_data in trigger.args.get('pages', []):
                pages.append(DialoguePage(
                    text=page_data.get('text', '...'),
                    speaker=page_data.get('speaker')
                ))
            if pages:
                self.dialogue_box.show_dialogue(pages)
                
        elif trigger.event == "cutscene":
            # Start a cutscene
            cutscene_id = trigger.args.get('id')
            if cutscene_id:
                self._start_cutscene(cutscene_id)
    
    def _interact_with_entity(self, entity: Entity) -> None:
        """
        Interact with an entity.
        
        Args:
            entity: Entity to interact with
        """
        # Lock player movement during interaction
        if self.player:
            self.player.lock_movement(True)
        
        # Handle different NPCs
        if entity.name == "Professor Budde":
            if not self.game.story_manager.get_flag('has_starter'):
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
                    callback=lambda _: self.player.lock_movement(False) if self.player else None
                )
                
        elif entity.name == "Ruhrpott Karl":
            pages = [
                DialoguePage(
                    text="Ey, wat willze denn, Jung?",
                    speaker="Karl"
                ),
                DialoguePage(
                    text="Pass auf im hohen Gras! Da lauern wilde Monster!",
                    speaker="Karl"
                ),
                DialoguePage(
                    text="Wenn de eins fängst, kannze damit kämpfen!",
                    speaker="Karl"
                )
            ]
            
            self.dialogue_box.show_dialogue(
                pages,
                callback=lambda _: self.player.lock_movement(False) if self.player else None
            )
    
    def _go_to_starter_selection(self):
        """Go to starter selection scene."""
        if self.player:
            self.player.lock_movement(False)
        
        from engine.scenes.starter_scene import StarterScene
        self.game.push_scene(StarterScene, game=self.game)
    
    def _check_encounter(self, tile_x: int, tile_y: int, steps: int) -> None:
        """
        Check for random encounter.
        
        Args:
            tile_x: Current tile X
            tile_y: Current tile Y
            steps: Steps since last encounter
        """
        if not self.encounter_enabled or not self.current_area or self.in_battle:
            return
        
        # Increment step counter
        self.steps_since_encounter += 1
        
        # Check minimum steps
        if self.steps_since_encounter < self.min_steps_between_encounters:
            return
        
        # Get terrain type at current position  
        tile_type = self.current_area.get_tile_type(tile_x, tile_y)
        
        # Check if this is an encounter tile (grass = 5, tall grass = 2)
        if tile_type in [2, 5]:
            # Roll for encounter
            if random.random() < self.current_area.encounter_rate:
                # Delay encounter check to next frame to avoid movement issues
                self.encounter_check_pending = True
    
    def _execute_encounter_check(self):
        """Execute the actual encounter check."""
        if not self.game.party_manager.party.get_conscious_members():
            # No conscious monsters, can't battle
            return
        
        # Start battle!
        self._start_battle()
    
    def _start_battle(self) -> None:
        """Start a random battle encounter."""
        if self.in_battle:
            return
        
        # Check if party has monsters
        if not self.game.party_manager.party.get_conscious_members():
            self.dialogue_box.show_text(
                "Du hast keine kampffähigen Monster! Hol dir erst eins vom Professor!",
                callback=lambda _: None
            )
            return
        
        # Mark as in battle to prevent multiple triggers
        self.in_battle = True
        
        # Reset encounter steps
        self.steps_since_encounter = 0
        
        # Generate wild monster from encounter table
        wild_monster = self._generate_wild_monster()
        
        if not wild_monster:
            # No encounter data, show debug message
            self.dialogue_box.show_text(
                "Keine Monster in diesem Gebiet! (Encounter-Daten fehlen)",
                callback=lambda _: setattr(self, 'in_battle', False)
            )
            return
        
        # Show encounter message briefly
        self.dialogue_box.show_text(
            f"Ein wildes {wild_monster.species_name} erscheint!",
            callback=lambda _: self._transition_to_battle(wild_monster)
        )
    
    def _generate_wild_monster(self) -> Optional[MonsterInstance]:
        """Generate a wild monster from encounter table."""
        if not self.current_area or not self.current_area.encounter_table:
            # Fallback: Create a basic wild monster for testing
            species = self.game.resources.get_monster_species(5)  # Rattfratz
            if species:
                monster = MonsterInstance.create_from_species(
                    species=species,
                    level=random.randint(2, 5)
                )
                return monster
            return None
        
        # Calculate total weight
        total_weight = sum(enc['weight'] for enc in self.current_area.encounter_table)
        
        # Roll random number
        roll = random.randint(1, total_weight)
        
        # Find which monster to spawn
        current_weight = 0
        for encounter in self.current_area.encounter_table:
            current_weight += encounter['weight']
            if roll <= current_weight:
                # This is our monster!
                species = self.game.resources.get_monster_species(encounter['species_id'])
                if species:
                    level = random.randint(encounter['level_min'], encounter['level_max'])
                    monster = MonsterInstance.create_from_species(
                        species=species,
                        level=level
                    )
                    return monster
                else:
                    # Species not found, create fallback
                    monster = MonsterInstance(
                        species_id=encounter['species_id'],
                        species_name=encounter['name'],
                        level=random.randint(encounter['level_min'], encounter['level_max'])
                    )
                    # Set basic stats
                    monster.types = ['Normal']
                    monster.rank = 'F'
                    monster.base_stats = {
                        'hp': 15,
                        'attacker': 5,
                        'defender': 5,
                        'mag': 5,
                        'res': 5,
                        'spd': 5
                    }
                    monster.calculate_stats()
                    monster.current_hp = monster.max_hp
                    return monster
        
        return None
    
    def _transition_to_battle(self, wild_monster: MonsterInstance):
        """Transition to battle scene."""
        # Play battle transition effect
        self.game.transition_manager.start(TransitionType.BATTLE_SWIRL, duration=0.8)
        
        # Push battle scene
        from engine.scenes.battle_scene import BattleScene
        battle_scene = BattleScene(self.game)
        
        # Start battle with wild monster
        self.game.push_scene(
            battle_scene,
            player_team=None,  # Will use party manager
            enemy_team=[wild_monster],
            is_wild=True,
            background='grass'
        )
        
        # Reset in_battle flag when we return
        self.in_battle = False


def draw_grid(surface: pygame.Surface, camera_x: int, camera_y: int) -> None:
    """Draw a grid overlay for debugging."""
    from engine.world.tiles import TILE_SIZE
    
    # Grid color and alpha
    grid_color = (100, 100, 100, 100)
    
    # Get screen dimensions
    screen_width = surface.get_width()
    screen_height = surface.get_height()
    
    # Calculate grid offset based on camera position
    offset_x = camera_x % TILE_SIZE
    offset_y = camera_y % TILE_SIZE
    
    # Draw vertical lines
    for x in range(0, screen_width + TILE_SIZE, TILE_SIZE):
        line_x = x - offset_x
        if 0 <= line_x <= screen_width:
            pygame.draw.line(surface, grid_color, (line_x, 0), (line_x, screen_height), 1)
    
    # Draw horizontal lines
    for y in range(0, screen_height + TILE_SIZE, TILE_SIZE):
        line_y = y - offset_y
        if 0 <= line_y <= screen_height:
            pygame.draw.line(surface, grid_color, (0, line_y), (screen_width, line_y), 1)
    
    def _start_cutscene(self, cutscene_id: str) -> None:
        """Start a cutscene sequence."""
        # Placeholder for cutscene system
        pass
    
    def _toggle_pause(self) -> None:
        """Toggle pause state."""
        self.paused = not self.paused
        
        if self.paused:
            # Open pause menu
            from engine.scenes.pause_scene import PauseScene
            self.game.push_scene(PauseScene, game=self.game)
        else:
            # Resume
            pass
    
    def _check_story_events(self):
        """Prüft und triggert Story-Events basierend auf Position und Flags"""
        if not self.player or not self.game.story_manager:
            return
        
        tile_x, tile_y = self.player.get_tile_position()
        story = self.game.story_manager
        
        # Spieler verlässt das Haus zum ersten Mal
        if self.map_id == "kohlenstadt" and not story.get_flag('left_house_first_time'):
            story.set_flag('left_house_first_time', True)
            self.dialogue_box.show_text(
                "Kohlenstadt! Die Stadt, in der alles begann. Zeit, Professor Budde zu besuchen!"
            )
        
        # Spieler betritt Museum
        if self.map_id == "museum" and not story.get_flag('visited_museum'):
            story.set_flag('visited_museum', True)
            if not story.get_flag('has_starter'):
                # Trigger Professor-Cutscene
                self._start_professor_intro()
        
        # Spieler verlässt Museum mit Starter
        if self.map_id == "kohlenstadt" and story.get_flag('has_starter'):
            if not story.get_flag('met_rival') and story.should_spawn_rival():
                # Spawn Rivale vor dem Museum
                self._spawn_rival_outside_museum()
    
    def _start_professor_intro(self):
        """Startet die Professor-Einführung"""
        story = self.game.story_manager
        story.set_flag('met_professor', True)
        
        # Zeige Einführungsdialog
        pages = [
            DialoguePage(
                "Ach, du bist es! Ich hab schon auf dich gewartet!",
                "Prof. Budde"
            ),
            DialoguePage(
                "Ich bin Professor Budde, der führende Fossil-Forscher hier!",
                "Prof. Budde"
            ),
            DialoguePage(
                "Ich hab gehört, du willst auf Reisen gehen?",
                "Prof. Budde"
            ),
            DialoguePage(
                "Da brauchst du unbedingt ein Monster als Partner!",
                "Prof. Budde"
            ),
            DialoguePage(
                "Komm, ich zeig dir meine neuesten Wiederbelebungen!",
                "Prof. Budde"
            )
        ]
        
        self.dialogue_box.show_dialogue(
            pages,
            callback=lambda _: self._go_to_starter_selection()
        )
    
    def _go_to_starter_selection(self):
        """Wechselt zur Starter-Auswahl-Szene"""
        from engine.scenes.starter_selection_scene import StarterSelectionScene
        
        starter_scene = StarterSelectionScene(self.game)
        self.game.change_scene(starter_scene)
    
    def _spawn_rival_outside_museum(self):
        """Spawnt den Rivalen vor dem Museum"""
        story = self.game.story_manager
        story.set_flag('met_rival', True)
        
        # Erstelle Rivalen-NPC
        from engine.world.npc import RivalKlaus
        rival = RivalKlaus(20 * 16, 8 * 16)  # Vor dem Museum
        self.current_area.entities.append(rival)
        
        # Starte Rivalen-Dialog
        pages = rival.get_dialogue(story)
        self.dialogue_box.show_dialogue(
            pages,
            callback=lambda _: self._start_rival_battle()
        )
    
    def _start_rival_battle(self):
        """Startet den Kampf mit dem Rivalen"""
        # Erstelle Rivalen-Team basierend auf Spieler-Starter
        rival_monster = self._create_rival_starter()
        
        # Starte Battle Scene
        from engine.scenes.battle_scene import BattleScene
        battle_scene = BattleScene(self.game)
        
        self.game.push_scene(
            battle_scene,
            enemy_team=[rival_monster],
            is_trainer_battle=True,
            trainer_name="Klaus",
            on_victory=lambda: self._on_rival_victory(),
            on_defeat=lambda: self._on_rival_defeat()
        )
    
    def _create_rival_starter(self):
        """Erstellt das Starter-Monster des Rivalen"""
        # Rivale hat immer den Typ-Vorteil
        player_starter = self.game.party_manager.party.monsters[0]
        
        # Bestimme Rivalen-Monster basierend auf Spieler-Wahl
        rival_species_id = 1  # Default
        if player_starter.species_id == 1:  # Feuer
            rival_species_id = 2  # Wasser
        elif player_starter.species_id == 2:  # Wasser
            rival_species_id = 3  # Pflanze
        elif player_starter.species_id == 3:  # Pflanze
            rival_species_id = 1  # Feuer
        
        # Erstelle Monster
        from engine.systems.monster_instance import MonsterInstance
        rival_monster = MonsterInstance.create_from_species(
            species=self.game.resources.get_monster_species(rival_species_id),
            game=self.game
        )
        return rival_monster
    
    def _on_rival_victory(self):
        """Callback wenn Spieler den Rivalen besiegt"""
        story = self.game.story_manager
        story.set_flag('rival_first_battle', True)
        story.variables['rival_won_first'] = False
        
        self.dialogue_box.show_dialogue([
            DialoguePage("Mensch, du bist ja echt stark!", "Klaus"),
            DialoguePage("Aber wart's ab, ich werd trainieren!", "Klaus"),
            DialoguePage("Beim nächsten Mal gewinne ich!", "Klaus"),
            DialoguePage("[Klaus rennt davon]", None)
        ])
        
        # Entferne Rivalen-NPC
        self._remove_rival_npc()
    
    def _on_rival_defeat(self):
        """Callback wenn Spieler gegen Rivalen verliert"""
        story = self.game.story_manager
        story.set_flag('rival_first_battle', True)
        story.variables['rival_won_first'] = True
        
        self.dialogue_box.show_dialogue([
            DialoguePage("Haha! Ich hab's gewusst!", "Klaus"),
            DialoguePage("Mein Monster ist das Beste!", "Klaus"),
            DialoguePage("Du solltest erstmal trainieren gehen!", "Klaus"),
            DialoguePage("[Klaus geht stolz davon]", None)
        ])
        
        # Entferne Rivalen-NPC
        self._remove_rival_npc()
    
    def _remove_rival_npc(self):
        """Entfernt den Rivalen-NPC aus der aktuellen Area"""
        from engine.world.npc import RivalKlaus
        self.current_area.entities = [
            e for e in self.current_area.entities 
            if not isinstance(e, RivalKlaus)
        ]
