#!/usr/bin/env python3
"""
Complete TMX Integration System
Ersetzt die alten Rendering-Methoden durch ein sauberes TMX-basiertes System
"""

import pygame
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import json

# ============================================================================
# TMX MAP LOADER - Lädt und verwaltet TMX-Maps
# ============================================================================

class TMXMapLoader:
    """Lädt TMX-Maps mit korrektem Tileset-Handling"""
    
    def __init__(self):
        self.tile_size = 16
        self.gid_to_surface: Dict[int, pygame.Surface] = {}
        self.tilesets: List[Dict] = []
        
    def load_map(self, map_path: Path) -> 'TMXMap':
        """Lädt eine TMX-Map komplett"""
        tree = ET.parse(map_path)
        root = tree.getroot()
        
        # Map-Eigenschaften
        map_data = TMXMap()
        map_data.width = int(root.get('width', 32))
        map_data.height = int(root.get('height', 32))
        map_data.tile_width = int(root.get('tilewidth', 16))
        map_data.tile_height = int(root.get('tileheight', 16))
        map_data.map_path = map_path
        
        # Lade Tilesets
        self._load_tilesets(root, map_path)
        map_data.gid_to_surface = self.gid_to_surface.copy()
        
        # Lade Layers
        self._load_layers(root, map_data)
        
        # Lade Objects (NPCs, Warps, etc.)
        self._load_objects(root, map_data)
        
        return map_data
    
    def _load_tilesets(self, root, map_path: Path):
        """Lädt alle Tilesets aus der TMX"""
        self.gid_to_surface.clear()
        self.tilesets.clear()
        
        for tileset_elem in root.findall('tileset'):
            firstgid = int(tileset_elem.get('firstgid', 1))
            source = tileset_elem.get('source', '')
            
            if source:
                # Externe TSX-Datei
                tsx_path = map_path.parent / source
                if not tsx_path.exists():
                    # Versuche andere Pfade
                    tsx_path = Path("assets/gfx/tiles") / Path(source).name
                    if not tsx_path.exists():
                        tsx_path = Path("data/maps") / Path(source).name
                
                if tsx_path.exists():
                    self._load_tsx_tileset(tsx_path, firstgid)
    
    def _load_tsx_tileset(self, tsx_path: Path, firstgid: int):
        """Lädt ein einzelnes Tileset aus einer TSX-Datei"""
        try:
            tree = ET.parse(tsx_path)
            root = tree.getroot()
            
            tile_width = int(root.get('tilewidth', 16))
            tile_height = int(root.get('tileheight', 16))
            tile_count = int(root.get('tilecount', 0))
            columns = int(root.get('columns', 1))
            name = root.get('name', 'unknown')
            
            # Finde Bild
            image_elem = root.find('image')
            if not image_elem:
                print(f"[TMX] Kein Bild in {tsx_path.name}")
                return
            
            # Bildpfad konstruieren
            image_source = image_elem.get('source', '')
            if image_source.startswith('../../'):
                image_path = Path(image_source.replace('../../', ''))
            elif image_source.startswith('../'):
                image_path = Path(image_source.replace('../', 'assets/gfx/tiles/'))
            else:
                image_path = tsx_path.parent / image_source
            
            if not image_path.exists():
                # Versuche alternative Pfade
                image_path = Path("assets/gfx/tiles/tilesets") / Path(image_source).name
            
            if not image_path.exists():
                print(f"[TMX] Tileset-Bild nicht gefunden: {image_path}")
                return
            
            # Lade Tileset-Bild
            tileset_surface = pygame.image.load(str(image_path)).convert_alpha()
            
            # Tileset-Info speichern
            tileset_info = {
                'name': name,
                'firstgid': firstgid,
                'tile_count': tile_count,
                'columns': columns,
                'tile_width': tile_width,
                'tile_height': tile_height,
                'image_path': str(image_path)
            }
            self.tilesets.append(tileset_info)
            
            # Extrahiere einzelne Tiles
            for tile_id in range(tile_count):
                col = tile_id % columns
                row = tile_id // columns
                
                x = col * tile_width
                y = row * tile_height
                
                # Extrahiere Tile
                tile_surf = pygame.Surface((tile_width, tile_height), pygame.SRCALPHA)
                tile_surf.blit(tileset_surface, (0, 0), (x, y, tile_width, tile_height))
                
                # Skaliere auf Standard-Größe
                if tile_width != self.tile_size or tile_height != self.tile_size:
                    tile_surf = pygame.transform.scale(tile_surf, (self.tile_size, self.tile_size))
                
                # Speichere mit GID
                gid = firstgid + tile_id
                self.gid_to_surface[gid] = tile_surf
            
            print(f"[TMX] Tileset geladen: {name} - {tile_count} Tiles (firstgid={firstgid})")
            
        except Exception as e:
            print(f"[TMX] Fehler beim Laden von {tsx_path}: {e}")
    
    def _load_layers(self, root, map_data: 'TMXMap'):
        """Lädt alle Layer aus der TMX"""
        for layer_elem in root.findall('layer'):
            layer_name = layer_elem.get('name', 'default')
            layer_width = int(layer_elem.get('width', map_data.width))
            layer_height = int(layer_elem.get('height', map_data.height))
            
            # Parse Tile-Daten
            layer_tiles = []
            data_elem = layer_elem.find('data')
            
            if data_elem is not None:
                encoding = data_elem.get('encoding', 'csv')
                
                if encoding == 'csv':
                    csv_text = data_elem.text.strip()
                    for line in csv_text.split('\n'):
                        if not line.strip():
                            continue
                        row = []
                        for gid_str in line.split(','):
                            if gid_str.strip():
                                gid = int(gid_str.strip())
                                # Entferne Flip-Flags
                                clean_gid = gid & 0x0FFFFFFF
                                row.append(clean_gid)
                        if row:
                            layer_tiles.append(row)
            
            # Speichere Layer
            map_data.layers[layer_name] = layer_tiles
            print(f"[TMX] Layer geladen: {layer_name} ({len(layer_tiles)} Zeilen)")
    
    def _load_objects(self, root, map_data: 'TMXMap'):
        """Lädt Objekte aus der TMX"""
        for objectgroup in root.findall('objectgroup'):
            group_name = objectgroup.get('name', '')
            
            for obj in objectgroup.findall('object'):
                obj_type = obj.get('type', '').lower()
                obj_name = obj.get('name', '')
                obj_x = float(obj.get('x', 0)) // self.tile_size
                obj_y = float(obj.get('y', 0)) // self.tile_size
                
                obj_data = {
                    'type': obj_type,
                    'name': obj_name,
                    'x': int(obj_x),
                    'y': int(obj_y),
                    'properties': {}
                }
                
                # Lade Properties
                props = obj.find('properties')
                if props:
                    for prop in props.findall('property'):
                        prop_name = prop.get('name')
                        prop_value = prop.get('value')
                        obj_data['properties'][prop_name] = prop_value
                
                map_data.objects.append(obj_data)


# ============================================================================
# TMX MAP DATA - Speichert die geladenen Map-Daten
# ============================================================================

class TMXMap:
    """Repräsentiert eine geladene TMX-Map"""
    
    def __init__(self):
        self.width = 0
        self.height = 0
        self.tile_width = 16
        self.tile_height = 16
        self.map_path = None
        
        # Layers: Dict[name, List[List[gid]]]
        self.layers: Dict[str, List[List[int]]] = {}
        
        # Objects: List[Dict]
        self.objects: List[Dict] = []
        
        # GID zu Surface Mapping
        self.gid_to_surface: Dict[int, pygame.Surface] = {}
        
        # Gerenderte Layer-Surfaces (Cache)
        self._rendered_layers: Dict[str, pygame.Surface] = {}
    
    def render_layer(self, layer_name: str) -> pygame.Surface:
        """Rendert einen Layer zu einer Surface"""
        if layer_name in self._rendered_layers:
            return self._rendered_layers[layer_name]
        
        if layer_name not in self.layers:
            return None
        
        # Erstelle Surface
        surface = pygame.Surface(
            (self.width * self.tile_width, self.height * self.tile_height),
            pygame.SRCALPHA
        )
        
        # Rendere Tiles
        layer_data = self.layers[layer_name]
        for y, row in enumerate(layer_data):
            for x, gid in enumerate(row):
                if gid > 0 and gid in self.gid_to_surface:
                    tile_surf = self.gid_to_surface[gid]
                    surface.blit(tile_surf, (x * self.tile_width, y * self.tile_height))
        
        # Cache
        self._rendered_layers[layer_name] = surface
        return surface
    
    def get_collision_at(self, tile_x: int, tile_y: int) -> bool:
        """Prüft Kollision an einer Tile-Position"""
        # Prüfe Map-Grenzen
        if tile_x < 0 or tile_x >= self.width:
            return True
        if tile_y < 0 or tile_y >= self.height:
            return True
        
        # Prüfe Collision-Layer
        if 'collision' in self.layers:
            collision_layer = self.layers['collision']
            if tile_y < len(collision_layer) and tile_x < len(collision_layer[tile_y]):
                return collision_layer[tile_y][tile_x] > 0
        
        return False
    
    def get_object_at(self, tile_x: int, tile_y: int, obj_type: str = None) -> Optional[Dict]:
        """Holt ein Objekt an einer Position"""
        for obj in self.objects:
            if obj['x'] == tile_x and obj['y'] == tile_y:
                if obj_type is None or obj['type'] == obj_type:
                    return obj
        return None


# ============================================================================
# INTERACTION MANAGER - Verwaltet NPCs, Warps und Interaktionen
# ============================================================================

class InteractionManager:
    """Verwaltet alle Interaktionen auf einer Map"""
    
    def __init__(self, game):
        self.game = game
        self.map_id = ""
        self.interactions: Dict[str, Any] = {}
        self.npcs: List[Any] = []
        
    def load_interactions(self, map_id: str):
        """Lädt Interaktionen aus JSON"""
        self.map_id = map_id
        self.interactions.clear()
        self.npcs.clear()
        
        # Lade JSON-Datei
        json_path = Path("data/maps/interactions") / f"{map_id}.json"
        if json_path.exists():
            with open(json_path, 'r', encoding='utf-8') as f:
                self.interactions = json.load(f)
            print(f"[Interactions] Geladen für {map_id}: {len(self.interactions.get('npcs', []))} NPCs")
    
    def spawn_npcs(self) -> List:
        """Spawnt alle NPCs für diese Map"""
        npcs = []
        
        for npc_data in self.interactions.get('npcs', []):
            # Prüfe Bedingungen
            if not self._check_conditions(npc_data.get('conditions')):
                continue
            
            # Erstelle NPC
            from engine.world.entity import Entity
            npc = Entity(
                x=npc_data['position'][0] * 16,
                y=npc_data['position'][1] * 16,
                width=14,
                height=14
            )
            npc.name = npc_data.get('name', 'NPC')
            npc.interactable = True
            npc.dialog_id = npc_data.get('dialog')
            npc.sprite_id = npc_data.get('sprite')
            
            npcs.append(npc)
        
        self.npcs = npcs
        return npcs
    
    def check_warp(self, tile_x: int, tile_y: int) -> Optional[Dict]:
        """Prüft ob an Position ein Warp ist"""
        for warp in self.interactions.get('warps', []):
            if warp['position'][0] == tile_x and warp['position'][1] == tile_y:
                if self._check_conditions(warp.get('conditions')):
                    return warp
        return None
    
    def check_interaction(self, tile_x: int, tile_y: int) -> Optional[Dict]:
        """Prüft Interaktionen an einer Position"""
        # NPCs
        for npc in self.npcs:
            npc_tile_x = npc.x // 16
            npc_tile_y = npc.y // 16
            if npc_tile_x == tile_x and npc_tile_y == tile_y:
                return {'type': 'npc', 'entity': npc}
        
        # Objects
        for obj in self.interactions.get('objects', []):
            if obj['position'][0] == tile_x and obj['position'][1] == tile_y:
                if self._check_conditions(obj.get('conditions')):
                    return {'type': 'object', 'data': obj}
        
        # Triggers
        for trigger in self.interactions.get('triggers', []):
            if trigger['position'][0] == tile_x and trigger['position'][1] == tile_y:
                if self._check_conditions(trigger.get('conditions')):
                    return {'type': 'trigger', 'data': trigger}
        
        return None
    
    def _check_conditions(self, conditions: Dict) -> bool:
        """Prüft Bedingungen"""
        if not conditions:
            return True
        
        # Prüfe Story-Flags
        if 'flag' in conditions:
            flag = conditions['flag']
            if flag.startswith('!'):
                # Negierte Bedingung
                return not self.game.story_manager.get_flag(flag[1:])
            else:
                return self.game.story_manager.get_flag(flag)
        
        return True


# ============================================================================
# MODERNES MAP SYSTEM - Kombiniert TMX und Interaktionen
# ============================================================================

class ModernMapSystem:
    """Modernes Map-System mit TMX-Rendering und JSON-Interaktionen"""
    
    def __init__(self, game):
        self.game = game
        self.tmx_loader = TMXMapLoader()
        self.interaction_manager = InteractionManager(game)
        
        self.current_map: Optional[TMXMap] = None
        self.current_map_id = ""
        
    def load_map(self, map_id: str) -> TMXMap:
        """Lädt eine Map komplett"""
        print(f"\n[ModernMapSystem] Lade Map: {map_id}")
        
        # Lade TMX
        tmx_path = Path("data/maps") / f"{map_id}.tmx"
        if not tmx_path.exists():
            print(f"[ModernMapSystem] TMX nicht gefunden: {tmx_path}")
            return None
        
        self.current_map = self.tmx_loader.load_map(tmx_path)
        self.current_map_id = map_id
        
        # Lade Interaktionen
        self.interaction_manager.load_interactions(map_id)
        
        # Spawne NPCs
        npcs = self.interaction_manager.spawn_npcs()
        print(f"[ModernMapSystem] {len(npcs)} NPCs gespawnt")
        
        return self.current_map
    
    def render(self, screen: pygame.Surface, camera_x: int = 0, camera_y: int = 0):
        """Rendert die aktuelle Map"""
        if not self.current_map:
            return
        
        # Rendere Layer in korrekter Reihenfolge
        layer_order = [
            "Tile Layer 1",  # Boden
            "Tile Layer 2",  # Dekoration
            "Tile Layer 3",  # Objekte
            "Tile Layer 4",  # Overlay
        ]
        
        for layer_name in layer_order:
            if layer_name in self.current_map.layers:
                surface = self.current_map.render_layer(layer_name)
                if surface:
                    screen.blit(surface, (-camera_x, -camera_y))
    
    def check_collision(self, tile_x: int, tile_y: int) -> bool:
        """Prüft Kollision"""
        if self.current_map:
            return self.current_map.get_collision_at(tile_x, tile_y)
        return False
    
    def check_warp(self, tile_x: int, tile_y: int) -> Optional[Dict]:
        """Prüft Warp"""
        return self.interaction_manager.check_warp(tile_x, tile_y)
    
    def check_interaction(self, tile_x: int, tile_y: int) -> Optional[Dict]:
        """Prüft Interaktion"""
        return self.interaction_manager.check_interaction(tile_x, tile_y)
    
    def get_npcs(self) -> List:
        """Gibt alle NPCs zurück"""
        return self.interaction_manager.npcs


# ============================================================================
# INTEGRATION HELPER - Hilft bei der Integration ins Hauptspiel
# ============================================================================

def integrate_modern_map_system(field_scene):
    """Integriert das moderne Map-System in die FieldScene"""
    
    print("\n" + "="*60)
    print("🚀 INTEGRIERE MODERNES TMX-SYSTEM")
    print("="*60)
    
    # Erstelle modernes Map-System
    field_scene.map_system = ModernMapSystem(field_scene.game)
    
    # Überschreibe load_map Methode
    original_load_map = field_scene.load_map
    
    def modern_load_map(map_name: str, spawn_x: int = 5, spawn_y: int = 5):
        """Moderne Map-Loading Methode"""
        try:
            # Lade mit modernem System
            tmx_map = field_scene.map_system.load_map(map_name)
            
            if tmx_map:
                # Erstelle kompatible Area
                from engine.world.area import Area
                field_scene.current_area = Area(map_name)
                
                # Setze TMX-Daten
                field_scene.current_area.width = tmx_map.width
                field_scene.current_area.height = tmx_map.height
                field_scene.current_area.tmx_map = tmx_map
                
                # NPCs hinzufügen
                field_scene.current_area.npcs = field_scene.map_system.get_npcs()
                
                # Kamera setup
                if field_scene.camera:
                    field_scene.camera.set_world_size(
                        tmx_map.width * 16,
                        tmx_map.height * 16
                    )
                
                # Player positionieren
                if field_scene.player:
                    field_scene.player.set_tile_position(spawn_x, spawn_y)
                    field_scene.camera.center_on(
                        field_scene.player.x + 8,
                        field_scene.player.y + 8,
                        immediate=True
                    )
                
                print(f"✅ Map {map_name} mit modernem System geladen!")
                return
                
        except Exception as e:
            print(f"❌ Fehler beim modernen Loading: {e}")
            import traceback
            traceback.print_exc()
        
        # Fallback auf altes System
        print("⚠️ Fallback auf altes System...")
        original_load_map(map_name, spawn_x, spawn_y)
    
    # Ersetze Methode
    field_scene.load_map = modern_load_map
    
    # Überschreibe draw Methode
    original_draw = field_scene.draw
    
    def modern_draw(surface: pygame.Surface):
        """Moderne Draw-Methode"""
        if hasattr(field_scene, 'map_system') and field_scene.map_system.current_map:
            # Rendere mit modernem System
            camera_x = int(field_scene.camera.x) if field_scene.camera else 0
            camera_y = int(field_scene.camera.y) if field_scene.camera else 0
            
            # Rendere Map
            field_scene.map_system.render(surface, camera_x, camera_y)
            
            # Rendere Player
            if field_scene.player:
                field_scene.player.draw(surface, camera_x, camera_y)
            
            # Rendere NPCs
            for npc in field_scene.map_system.get_npcs():
                npc.draw(surface, camera_x, camera_y)
            
            # UI
            if field_scene.dialogue_box:
                field_scene.dialogue_box.draw(surface)
        else:
            # Fallback
            original_draw(surface)
    
    field_scene.draw = modern_draw
    
    print("✅ Modernes TMX-System integriert!")
    print("   - TMX-Maps werden korrekt geladen")
    print("   - Tilesets werden richtig gemappt")
    print("   - NPCs aus JSON werden gespawnt")
    print("   - Interaktionen funktionieren")
    print("="*60 + "\n")


# ============================================================================
# TEST & DEMO
# ============================================================================

def test_modern_system():
    """Testet das moderne Map-System"""
    import pygame
    pygame.init()
    
    screen = pygame.display.set_mode((320, 240))
    pygame.display.set_caption("TMX Modern System Test")
    
    # Fake Game-Objekt
    class FakeGame:
        def __init__(self):
            self.story_manager = type('obj', (object,), {
                'get_flag': lambda self, flag: False
            })()
    
    game = FakeGame()
    
    # Erstelle System
    map_system = ModernMapSystem(game)
    
    # Lade Map
    tmx_map = map_system.load_map("player_house")
    
    if tmx_map:
        print(f"\n✅ Map geladen: {tmx_map.width}x{tmx_map.height}")
        print(f"   Layers: {list(tmx_map.layers.keys())}")
        print(f"   Objects: {len(tmx_map.objects)}")
        print(f"   NPCs: {len(map_system.get_npcs())}")
        
        # Render-Test
        clock = pygame.time.Clock()
        running = True
        camera_x = 0
        camera_y = 0
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    # Kamera-Bewegung
                    elif event.key == pygame.K_LEFT:
                        camera_x -= 16
                    elif event.key == pygame.K_RIGHT:
                        camera_x += 16
                    elif event.key == pygame.K_UP:
                        camera_y -= 16
                    elif event.key == pygame.K_DOWN:
                        camera_y += 16
            
            # Clear
            screen.fill((0, 0, 0))
            
            # Render
            map_system.render(screen, camera_x, camera_y)
            
            # Info
            font = pygame.font.Font(None, 16)
            text = font.render(f"Map: player_house | Cam: ({camera_x}, {camera_y})", True, (255, 255, 255))
            screen.blit(text, (5, 5))
            
            pygame.display.flip()
            clock.tick(60)
    else:
        print("❌ Map konnte nicht geladen werden!")
    
    pygame.quit()


if __name__ == "__main__":
    print("TMX Integration System")
    print("=" * 60)
    print("\nDieses Skript integriert das moderne TMX-System ins Spiel.")
    print("\nVerwendung:")
    print("1. In field_scene.py importieren:")
    print("   from tmx_integration_complete import integrate_modern_map_system")
    print("\n2. In FieldScene.__init__ aufrufen:")
    print("   integrate_modern_map_system(self)")
    print("\n3. Fertig! TMX-Maps werden automatisch geladen.")
    print("\nTeste das System...")
    
    test_modern_system()
