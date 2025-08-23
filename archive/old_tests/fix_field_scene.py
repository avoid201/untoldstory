#!/usr/bin/env python3
"""
Fix für die FieldScene-Area Kompatibilität
"""

from pathlib import Path
import shutil

def patch_field_scene():
    """Patcht die FieldScene für Kompatibilität mit der neuen Area-Klasse"""
    
    field_scene_path = Path("engine/scenes/field_scene.py")
    
    # Backup erstellen
    backup_path = field_scene_path.with_suffix('.py.backup2')
    if not backup_path.exists():
        shutil.copy(field_scene_path, backup_path)
        print(f"✅ Backup erstellt: {backup_path}")
    
    # Lese die aktuelle FieldScene
    with open(field_scene_path, 'r') as f:
        content = f.read()
    
    # Finde und ersetze die problematische Area-Initialisierung
    # ALT: Area mit vielen Parametern
    old_area_init = """            from engine.world.area import Area
            self.current_area = Area(
                id=map_data.id,
                name=map_data.name,
                width=map_data.width,
                height=map_data.height,
                layers=map_data.layers,
                properties=map_data.properties or {}
            )"""
    
    # NEU: Area nur mit map_id
    new_area_init = """            from engine.world.area import Area
            # Erstelle Area mit map_id - die neue Area-Klasse lädt alles selbst
            self.current_area = Area(map_name)"""
    
    # Ersetze den Code
    if old_area_init in content:
        content = content.replace(old_area_init, new_area_init)
        print("✅ Area-Initialisierung in FieldScene gepatcht")
    else:
        print("⚠️  Konnte Area-Initialisierung nicht finden - manueller Patch...")
        
        # Alternativer Patch-Ansatz
        # Suche nach dem load_map Methoden-Inhalt und patche ihn komplett
        import re
        
        # Pattern für die load_map Methode
        pattern = r'def load_map\(self, map_name: str.*?\n(?:.*?\n)*?.*?print\(f"Map \{map_name\} loaded successfully!"\)'
        
        # Neue load_map Methode
        new_load_map = '''def load_map(self, map_name: str, spawn_x: int = 5, spawn_y: int = 5):
        """Lädt eine neue Map und positioniert Spieler"""
        try:
            print(f"Loading map: {map_name}")
            
            # Erstelle Area mit der neuen Area-Klasse
            from engine.world.area import Area
            self.current_area = Area(map_name)
            self.map_id = map_name
            
            # Prüfe ob Area erfolgreich geladen wurde
            if not hasattr(self.current_area, 'width') or not hasattr(self.current_area, 'height'):
                # Fallback-Werte setzen
                self.current_area.width = 20
                self.current_area.height = 15
            
            # Füge fehlende Attribute hinzu falls nötig
            if not hasattr(self.current_area, 'map_data'):
                # Erstelle minimale map_data für Kompatibilität
                from engine.world.map_loader import MapData
                self.current_area.map_data = MapData(
                    id=map_name,
                    name=map_name.replace('_', ' ').title(),
                    width=getattr(self.current_area, 'width', 20),
                    height=getattr(self.current_area, 'height', 15),
                    tile_size=16,
                    layers=getattr(self.current_area, 'layers', {}),
                    warps=[],
                    triggers=[],
                    properties={},
                    tilesets=[]
                )
            
            # Füge weitere benötigte Attribute hinzu
            if not hasattr(self.current_area, 'entities'):
                self.current_area.entities = []
            if not hasattr(self.current_area, 'npcs'):
                self.current_area.npcs = []
            if not hasattr(self.current_area, 'encounter_rate'):
                self.current_area.encounter_rate = 0.1
            if not hasattr(self.current_area, 'encounter_table'):
                self.current_area.encounter_table = []
            
            # Füge Warp/Trigger-Methoden zur Area hinzu
            self.current_area = add_warp_methods_to_area(self.current_area)
            
            # Debug: Zeige Map-Informationen
            print(f"Map loaded: {map_name}")
            print(f"Map size: {self.current_area.width}x{self.current_area.height}")
            if hasattr(self.current_area, 'layer_surfaces'):
                print(f"Layers: {list(self.current_area.layer_surfaces.keys())}")
            
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
            
            # Set collision map for player (falls vorhanden)
            if hasattr(self.current_area, 'map_data') and hasattr(self.current_area.map_data, 'layers'):
                collision_layer = self.current_area.map_data.layers.get('collision', [])
                self.player.set_collision_map(
                    collision_layer,
                    self.current_area.width,
                    self.current_area.height
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
            
            print(f"Map {map_name} loaded successfully!")'''
        
        # Versuche Pattern-basiertes Ersetzen
        if re.search(pattern, content, re.DOTALL):
            content = re.sub(pattern, new_load_map, content, flags=re.DOTALL)
            print("✅ load_map Methode mit Regex gepatcht")
        else:
            print("⚠️  Konnte load_map nicht mit Regex patchen")
    
    # Schreibe die gepatchte Datei
    with open(field_scene_path, 'w') as f:
        f.write(content)
    
    print("✅ FieldScene gepatcht für Area-Kompatibilität")
    
    return True

def main():
    """Hauptfunktion"""
    print("=" * 60)
    print("FIELDSCENE-AREA KOMPATIBILITÄTS-FIX")
    print("=" * 60)
    
    if patch_field_scene():
        print("\n✅ Fix erfolgreich angewendet!")
        print("\n📋 Nächste Schritte:")
        print("1. Teste mit: python3 test_main_game.py")
        print("2. Starte das Spiel: python3 main.py")
    else:
        print("\n❌ Fix fehlgeschlagen")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
