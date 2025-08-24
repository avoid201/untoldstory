"""
Vereinheitlichtes Map-Loading System für Untold Story
Flint Hammerhead räumt das Chaos auf!

Dieses Modul kümmert sich um ALLES was mit Map-Loading zu tun hat.
Keine doppelten Methoden mehr, nur noch EINE zentrale Stelle!
"""

import pygame
import json
import os
from typing import Optional, Dict, Any, Tuple, List
from dataclasses import dataclass

from engine.world.tiles import TILE_SIZE, tile_to_world
from engine.world.map_loader import MapLoader, MapData, Warp
from engine.world.area import Area
from engine.world.camera import Camera, CameraConfig
from engine.core.resources import resources


@dataclass
class MapLoadResult:
    """Ergebnis eines Map-Load Vorgangs."""
    area: Area
    map_data: MapData
    spawn_x: int
    spawn_y: int
    map_id: str
    success: bool = True
    error_msg: Optional[str] = None


class UnifiedMapSystem:
    """
    Das EINE Map-System für alles!
    Keine Duplikate mehr, keine Verwirrung!
    """
    
    def __init__(self, game):
        """
        Initialisiert das vereinheitlichte Map-System.
        
        Args:
            game: Game-Instanz
        """
        self.game = game
        self.current_area: Optional[Area] = None
        self.current_map_id: str = ""
        self.map_cache: Dict[str, MapData] = {}
        
        # Map-Konfig laden
        self.map_config = self._load_map_config()
        
        print("[MapSystem] Vereinheitlichtes Map-System initialisiert!")
    
    def _load_map_config(self) -> Dict[str, Any]:
        """Lädt die Map-Konfiguration."""
        config_path = "data/game_data/maps_config.json"
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def load_map(self, map_id: str, spawn_x: int = 5, spawn_y: int = 5, 
                 spawn_point: Optional[str] = None) -> MapLoadResult:
        """
        DIE EINE METHODE zum Map laden!
        
        Args:
            map_id: Map-ID (z.B. "player_house", "kohlenstadt")
            spawn_x: Spawn X-Position in Tiles
            spawn_y: Spawn Y-Position in Tiles
            spawn_point: Benannter Spawn-Punkt (optional)
            
        Returns:
            MapLoadResult mit allen wichtigen Infos
        """
        print(f"[MapSystem] Lade Map: {map_id}")
        
        try:
            # 1. Check ob Map gecached ist
            if map_id in self.map_cache:
                map_data = self.map_cache[map_id]
                print(f"[MapSystem] Map {map_id} aus Cache geladen")
            else:
                # 2. Lade Map-Daten (JSON oder TMX)
                map_data = self._load_map_data(map_id)
                self.map_cache[map_id] = map_data
            
            # 3. Erstelle Area-Objekt
            area = self._create_area(map_id, map_data)
            
            # 4. Spawn-Position bestimmen
            if spawn_point:
                spawn_x, spawn_y = self._get_spawn_point(map_data, spawn_point)
            
            # 5. Warps laden
            self._load_warps(area, map_id)
            
            # 6. NPCs laden
            self._load_npcs(area, map_id)
            
            # 7. Encounter-Daten laden
            self._load_encounters(area, map_id)
            
            # Erfolg!
            self.current_area = area
            self.current_map_id = map_id
            
            print(f"[MapSystem] Map {map_id} erfolgreich geladen!")
            print(f"  - Größe: {map_data.width}x{map_data.height}")
            print(f"  - Spawn: ({spawn_x}, {spawn_y})")
            print(f"  - Warps: {len(area.warps) if hasattr(area, 'warps') else 0}")
            print(f"  - NPCs: {len(area.entities) if hasattr(area, 'entities') else 0}")
            
            return MapLoadResult(
                area=area,
                map_data=map_data,
                spawn_x=spawn_x,
                spawn_y=spawn_y,
                map_id=map_id,
                success=True
            )
            
        except Exception as e:
            print(f"[MapSystem] FEHLER beim Laden von {map_id}: {e}")
            
            # Fallback: Leere Map erstellen
            empty_area, empty_data = self._create_empty_map()
            
            return MapLoadResult(
                area=empty_area,
                map_data=empty_data,
                spawn_x=5,
                spawn_y=5,
                map_id="empty",
                success=False,
                error_msg=str(e)
            )
    
    def _load_map_data(self, map_id: str) -> MapData:
        """
        Lädt Map-Daten aus JSON oder TMX.
        EINE Methode für ALLE Map-Formate!
        """
        # Erst JSON versuchen
        json_path = f"data/maps/{map_id}.json"
        if os.path.exists(json_path):
            print(f"[MapSystem] Lade JSON-Map: {json_path}")
            return MapLoader.load_map(map_id)
        
        # Dann TMX versuchen
        tmx_path = f"assets/maps/{map_id}.tmx"
        if os.path.exists(tmx_path):
            print(f"[MapSystem] Lade TMX-Map: {tmx_path}")
            # TODO: TMX-Loader implementieren wenn nötig
            # Momentan nutzen wir nur JSON
            pass
        
        # Fallback: Versuche direkt über MapLoader
        return MapLoader.load_map(map_id)
    
    def _create_area(self, map_id: str, map_data: MapData) -> Area:
        """Erstellt ein Area-Objekt aus Map-Daten."""
        # Die Area-Klasse lädt selbst die Map
        area = Area(map_id)
        
        # Map-Data setzen falls nicht vorhanden
        if not hasattr(area, 'map_data'):
            area.map_data = map_data
        
        # Entities-Liste sicherstellen
        if not hasattr(area, 'entities'):
            area.entities = []
        
        # Warps-Liste sicherstellen
        if not hasattr(area, 'warps'):
            area.warps = []
        
        return area
    
    def _get_spawn_point(self, map_data: MapData, spawn_point: str) -> Tuple[int, int]:
        """Bestimmt Spawn-Position anhand eines benannten Punkts."""
        # Check in Map-Properties
        if hasattr(map_data, 'properties') and 'spawns' in map_data.properties:
            spawns = map_data.properties['spawns']
            if spawn_point in spawns:
                spawn = spawns[spawn_point]
                return spawn['x'], spawn['y']
        
        # Spezielle Spawn-Points
        spawn_defaults = {
            'bed': (5, 5),
            'door': (10, 10),
            'entrance': (10, 15),
            'exit': (10, 5),
            'center': (map_data.width // 2, map_data.height // 2)
        }
        
        if spawn_point in spawn_defaults:
            return spawn_defaults[spawn_point]
        
        # Fallback: Mitte der Map
        return map_data.width // 2, map_data.height // 2
    
    def _load_warps(self, area: Area, map_id: str) -> None:
        """Lädt Warps für die Map."""
        warps_data = resources.load_json("game_data/warps.json")
        if not warps_data or map_id not in warps_data:
            return
        
        map_warps = warps_data[map_id]
        for warp_name, warp_info in map_warps.items():
            warp_pos = warp_info.get("position", [0, 0])
            dest_pos = warp_info.get("destination_position", [5, 5])
            
            warp = Warp(
                x=warp_pos[0],
                y=warp_pos[1],
                to_map=warp_info.get("destination_map"),
                to_x=dest_pos[0],
                to_y=dest_pos[1],
                direction=warp_info.get("direction"),
                transition_type=warp_info.get("type", "fade")
            )
            area.warps.append(warp)
        
        print(f"[MapSystem] {len(area.warps)} Warps geladen für {map_id}")
    
    def _load_npcs(self, area: Area, map_id: str) -> None:
        """Lädt NPCs für die Map - MIT PATHFINDING!"""
        from engine.world.npc import NPC
        
        npcs_data = resources.load_json("game_data/npcs.json")
        if not npcs_data or map_id not in npcs_data:
            return
        
        sprite_manager = self.game.sprite_manager if hasattr(self.game, 'sprite_manager') else None
        player = self.game.player if hasattr(self.game, 'player') else None
        
        map_npcs = npcs_data[map_id]
        for npc_name, npc_info in map_npcs.items():
            try:
                # Sprite laden
                sprite_name = npc_info.get("sprite", "villager_m")
                facing = npc_info.get("facing", "down")
                
                npc_sprite = None
                if sprite_manager:
                    npc_sprite = sprite_manager.get_npc_sprite(sprite_name, facing)
                
                # NPC erstellen
                npc = NPC.from_config_dict(
                    name=npc_name.replace('_', ' ').title(),
                    config_dict=npc_info,
                    sprite_surface=npc_sprite
                )
                
                # PATHFINDING: Area und Player setzen!
                npc.set_area(area)
                if player:
                    npc.set_player_reference(player)
                
                # Kollisions-Layer setzen
                if hasattr(area, 'collision_layer'):
                    npc.set_collision_layer(area.collision_layer)
                elif hasattr(area, 'map_data') and area.map_data.layers.get('collision'):
                    npc.set_collision_layer(area.map_data.layers['collision'])
                
                # Sprite-Manager setzen
                if sprite_manager:
                    npc.set_sprite_manager(sprite_manager)
                
                area.entities.append(npc)
                print(f"[MapSystem] NPC geladen: {npc.name} - Pattern: {npc_info.get('movement_pattern', 'static')}")
                
            except Exception as e:
                print(f"[MapSystem] Fehler beim Laden von NPC {npc_name}: {e}")
        
        print(f"[MapSystem] {len(area.entities)} NPCs geladen für {map_id}")
    
    def _load_encounters(self, area: Area, map_id: str) -> None:
        """Lädt Encounter-Daten für die Map."""
        # Encounter-Tabellen basierend auf Map-ID
        encounter_tables = {
            "route_1": {
                "rate": 0.12,
                "table": self._create_route_1_encounters()
            },
            "kohlenstadt": {
                "rate": 0.15,
                "table": [
                    {"species_id": 5, "name": "Rattfratz", "level_min": 2, "level_max": 4, "weight": 40},
                    {"species_id": 6, "name": "Taubsi", "level_min": 2, "level_max": 5, "weight": 30},
                    {"species_id": 7, "name": "Raupie", "level_min": 3, "level_max": 4, "weight": 20},
                    {"species_id": 8, "name": "Hornliu", "level_min": 3, "level_max": 5, "weight": 10},
                ]
            }
        }
        
        if map_id in encounter_tables:
            area.encounter_rate = encounter_tables[map_id]["rate"]
            area.encounter_table = encounter_tables[map_id]["table"]
            print(f"[MapSystem] Encounter-Tabelle geladen für {map_id}: {len(area.encounter_table)} Monster")
        else:
            area.encounter_rate = 0
            area.encounter_table = []
    
    def _create_route_1_encounters(self) -> List[Dict]:
        """Erstellt Encounter-Tabelle für Route 1."""
        # 95% F-Rang, 5% E-Rang Monster
        return [
            # F-Rang Monster (95% Gewicht)
            {"species_id": 1, "name": "Glutstummel", "level_min": 3, "level_max": 6, "weight": 10},
            {"species_id": 2, "name": "Böllerling", "level_min": 3, "level_max": 6, "weight": 10},
            {"species_id": 3, "name": "Urmolch", "level_min": 3, "level_max": 6, "weight": 10},
            {"species_id": 4, "name": "Bierlementar", "level_min": 3, "level_max": 6, "weight": 10},
            {"species_id": 5, "name": "Kohlekumpel", "level_min": 3, "level_max": 6, "weight": 10},
            {"species_id": 6, "name": "Kieselkrabbler", "level_min": 3, "level_max": 6, "weight": 10},
            {"species_id": 7, "name": "Flugratte", "level_min": 3, "level_max": 6, "weight": 10},
            {"species_id": 8, "name": "Wolkenfurz", "level_min": 3, "level_max": 6, "weight": 10},
            {"species_id": 9, "name": "Unkrautling", "level_min": 3, "level_max": 6, "weight": 10},
            {"species_id": 10, "name": "Pommespanzer", "level_min": 3, "level_max": 6, "weight": 5},
            
            # E-Rang Monster (5% Gewicht)
            {"species_id": 21, "name": "Flammimp", "level_min": 5, "level_max": 8, "weight": 1},
            {"species_id": 22, "name": "Feuermolch", "level_min": 5, "level_max": 8, "weight": 1},
            {"species_id": 23, "name": "Kloakrake", "level_min": 5, "level_max": 8, "weight": 1},
            {"species_id": 24, "name": "Sumpfschrecke", "level_min": 5, "level_max": 8, "weight": 1},
            {"species_id": 25, "name": "Felsfresser", "level_min": 5, "level_max": 8, "weight": 1},
        ]
    
    def _create_empty_map(self) -> Tuple[Area, MapData]:
        """Erstellt eine leere Fallback-Map."""
        empty_data = MapData(
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
        
        empty_area = Area("empty")
        empty_area.map_data = empty_data
        empty_area.entities = []
        empty_area.warps = []
        empty_area.encounter_rate = 0
        empty_area.encounter_table = []
        
        return empty_area, empty_data
    
    def execute_warp(self, warp: Warp) -> MapLoadResult:
        """
        Führt einen Warp aus und lädt die Ziel-Map.
        
        Args:
            warp: Warp-Objekt
            
        Returns:
            MapLoadResult der Ziel-Map
        """
        print(f"[MapSystem] Warp nach {warp.to_map} auf Position ({warp.to_x}, {warp.to_y})")
        return self.load_map(warp.to_map, warp.to_x, warp.to_y)
    
    def get_warp_at(self, tile_x: int, tile_y: int) -> Optional[Warp]:
        """Findet einen Warp an der angegebenen Position."""
        if not self.current_area or not hasattr(self.current_area, 'warps'):
            return None
        
        for warp in self.current_area.warps:
            if warp.x == tile_x and warp.y == tile_y:
                return warp
        
        return None
