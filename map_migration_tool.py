#!/usr/bin/env python3
"""
Map Migration Tool für Untold Story
====================================
Dieses Tool migriert automatisch neue Tiled-Maps (.tmx) und übernimmt
NPCs, Dialoge und Warps aus den alten Maps.
"""

import json
import xml.etree.ElementTree as ET
import os
import shutil
import base64
import zlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from copy import deepcopy

@dataclass
class Warp:
    """Repräsentiert einen Warp-Punkt zwischen Maps"""
    x: int
    y: int
    to: str
    to_x: int
    to_y: int
    direction: str = "down"
    spawn_point: Optional[str] = None

@dataclass
class NPC:
    """Repräsentiert einen NPC mit Position und Dialog"""
    id: str
    name: str
    x: int
    y: int
    direction: str = "down"
    sprite: str = "npc_generic"
    dialogue: Dict[str, Any] = None
    movement_pattern: Optional[str] = None

@dataclass
class Trigger:
    """Repräsentiert einen Trigger (Schild, Examine-Objekt)"""
    x: int
    y: int
    event: str  # "sign", "interact", "examine"
    text: str
    condition: Optional[str] = None

class TMXParser:
    """Parser für Tiled TMX Dateien"""
    
    @staticmethod
    def decode_layer_data(data_text: str, encoding: str, compression: str = None) -> List[int]:
        """
        Dekodiert die Layer-Daten aus TMX
        
        Args:
            data_text: Die rohen Daten als String
            encoding: Encoding-Typ (csv, base64)
            compression: Kompressions-Typ (gzip, zlib, oder None)
        
        Returns:
            Liste mit Tile-IDs
        """
        if encoding == "csv":
            # CSV Format: einfach splitten und zu int konvertieren
            tiles = []
            for tile_id in data_text.strip().split(','):
                if tile_id.strip():
                    tiles.append(int(tile_id.strip()))
            return tiles
        
        elif encoding == "base64":
            # Base64 dekodieren
            raw_data = base64.b64decode(data_text.strip())
            
            # Dekomprimieren falls nötig
            if compression == "gzip":
                import gzip
                raw_data = gzip.decompress(raw_data)
            elif compression == "zlib":
                raw_data = zlib.decompress(raw_data)
            
            # Tiles als 32-bit integers lesen
            tiles = []
            for i in range(0, len(raw_data), 4):
                tile_id = int.from_bytes(raw_data[i:i+4], byteorder='little')
                # Tiled Global Tile IDs bereinigen (Flip-Bits entfernen)
                tile_id = tile_id & 0x0FFFFFFF
                tiles.append(tile_id)
            
            return tiles
        
        else:
            raise ValueError(f"Unbekanntes Encoding: {encoding}")
    
    @staticmethod
    def parse_tmx(filepath: Path) -> Dict[str, Any]:
        """
        Parst eine TMX-Datei und konvertiert sie in das JSON-Format
        
        Args:
            filepath: Pfad zur TMX-Datei
            
        Returns:
            Dictionary im JSON-Map-Format
        """
        tree = ET.parse(filepath)
        root = tree.getroot()
        
        # Map-Eigenschaften
        map_width = int(root.get('width', 0))
        map_height = int(root.get('height', 0))
        tile_width = int(root.get('tilewidth', 16))
        tile_height = int(root.get('tileheight', 16))
        
        # Basis-Struktur
        map_data = {
            "id": filepath.stem,
            "name": filepath.stem.replace('_', ' ').title(),
            "width": map_width,
            "height": map_height,
            "tile_size": tile_width,
            "layers": {},
            "warps": [],
            "npcs": [],
            "triggers": [],
            "spawn_points": {},
            "properties": {}
        }
        
        # Layer parsen
        for layer in root.findall('layer'):
            layer_name = layer.get('name', 'unnamed').lower()
            layer_width = int(layer.get('width', map_width))
            layer_height = int(layer.get('height', map_height))
            
            # Daten-Element finden
            data_elem = layer.find('data')
            if data_elem is not None:
                encoding = data_elem.get('encoding', 'csv')
                compression = data_elem.get('compression')
                
                # Layer-Daten dekodieren
                tiles = TMXParser.decode_layer_data(
                    data_elem.text,
                    encoding,
                    compression
                )
                
                # In 2D-Array konvertieren
                layer_2d = []
                for y in range(layer_height):
                    row = []
                    for x in range(layer_width):
                        idx = y * layer_width + x
                        if idx < len(tiles):
                            # Tiled verwendet 0 für leere Tiles, wir auch
                            # aber Tiled beginnt bei 1 zu zählen, also -1
                            tile_id = tiles[idx]
                            row.append(tile_id - 1 if tile_id > 0 else 0)
                        else:
                            row.append(0)
                    layer_2d.append(row)
                
                # Layer-Namen normalisieren
                if layer_name in ['ground', 'floor', 'base']:
                    map_data["layers"]["ground"] = layer_2d
                elif layer_name in ['decor', 'decoration', 'deco']:
                    map_data["layers"]["decor"] = layer_2d
                elif layer_name in ['collision', 'collisions', 'solid']:
                    map_data["layers"]["collision"] = layer_2d
                elif layer_name == 'furniture':
                    map_data["layers"]["furniture"] = layer_2d
                elif layer_name == 'decoration':
                    map_data["layers"]["decoration"] = layer_2d
                else:
                    map_data["layers"][layer_name] = layer_2d
        
        # Objekt-Layer parsen (für Warps, NPCs, Trigger)
        for objectgroup in root.findall('objectgroup'):
            group_name = objectgroup.get('name', '').lower()
            
            for obj in objectgroup.findall('object'):
                obj_type = obj.get('type', '').lower()
                obj_name = obj.get('name', '')
                
                # Position (Tiled verwendet Pixel, wir brauchen Tiles)
                x = int(float(obj.get('x', 0)) / tile_width)
                y = int(float(obj.get('y', 0)) / tile_height)
                
                # Properties auslesen
                properties = {}
                props_elem = obj.find('properties')
                if props_elem is not None:
                    for prop in props_elem.findall('property'):
                        prop_name = prop.get('name')
                        prop_value = prop.get('value')
                        # Versuche Zahlen zu konvertieren
                        try:
                            prop_value = int(prop_value)
                        except (ValueError, TypeError):
                            try:
                                prop_value = float(prop_value)
                            except (ValueError, TypeError):
                                pass
                        properties[prop_name] = prop_value
                
                # Je nach Typ verarbeiten
                if obj_type == 'warp' or group_name == 'warps':
                    warp = {
                        "x": x,
                        "y": y,
                        "to": properties.get('to', properties.get('to_map', '')),
                        "to_x": properties.get('to_x', 0),
                        "to_y": properties.get('to_y', 0),
                        "direction": properties.get('direction', 'down')
                    }
                    map_data["warps"].append(warp)
                
                elif obj_type == 'npc' or group_name == 'npcs':
                    npc = {
                        "id": obj_name or f"npc_{len(map_data['npcs'])}",
                        "name": properties.get('name', obj_name),
                        "x": x,
                        "y": y,
                        "direction": properties.get('direction', 'down'),
                        "sprite": properties.get('sprite', 'npc_generic'),
                        "dialogue": {
                            "default": properties.get('dialogue', "...")
                        }
                    }
                    map_data["npcs"].append(npc)
                
                elif obj_type in ['trigger', 'sign', 'examine'] or group_name == 'triggers':
                    trigger = {
                        "x": x,
                        "y": y,
                        "event": obj_type if obj_type != 'trigger' else properties.get('event', 'interact'),
                        "text": properties.get('text', properties.get('message', '...')),
                    }
                    if 'condition' in properties:
                        trigger["condition"] = properties['condition']
                    map_data["triggers"].append(trigger)
                
                elif obj_type == 'spawn' or obj_name.startswith('spawn_'):
                    spawn_name = obj_name.replace('spawn_', '') or 'default'
                    map_data["spawn_points"][spawn_name] = {
                        "x": x,
                        "y": y,
                        "direction": properties.get('direction', 'down')
                    }
        
        # Map-Properties
        props_elem = root.find('properties')
        if props_elem is not None:
            for prop in props_elem.findall('property'):
                map_data["properties"][prop.get('name')] = prop.get('value')
        
        return map_data

class MapMigrator:
    """Hauptklasse für die Map-Migration"""
    
    def __init__(self, 
                 old_maps_dir: str = "data/maps",
                 new_maps_dir: str = "untold_story_maps",
                 backup_dir: str = "data/maps_backup"):
        """
        Initialisiert den Map-Migrator
        
        Args:
            old_maps_dir: Verzeichnis mit den alten Maps
            new_maps_dir: Verzeichnis mit den neuen Tiled-Maps (.tmx)
            backup_dir: Verzeichnis für Backups
        """
        self.old_maps_dir = Path(old_maps_dir)
        self.new_maps_dir = Path(new_maps_dir)
        self.backup_dir = Path(backup_dir)
        self.tmx_parser = TMXParser()
        
        # Layer-Konfiguration für das neue System
        self.layer_config = {
            "render_order": ["ground", "decor", "furniture", "decoration"],
            "collision_layer": "collision",
            "new_layers": ["furniture", "decoration"]
        }
        
        # Tile-ID Mappings (anpassen an Ihr Tileset)
        self.furniture_tile_range = range(100, 200)  # Möbel-Tiles
        self.decoration_tile_range = range(200, 300)  # Deko-Tiles
        
    def backup_old_maps(self) -> None:
        """Erstellt ein Backup der alten Maps"""
        print(f"📦 Erstelle Backup in {self.backup_dir}...")
        
        if self.backup_dir.exists():
            # Nummeriertes Backup falls schon vorhanden
            i = 1
            while Path(f"{self.backup_dir}_{i}").exists():
                i += 1
            self.backup_dir = Path(f"{self.backup_dir}_{i}")
        
        shutil.copytree(self.old_maps_dir, self.backup_dir)
        print(f"✅ Backup erstellt: {self.backup_dir}")
    
    def load_map(self, filepath: Path) -> Dict[str, Any]:
        """Lädt eine Map-Datei (JSON oder TMX)"""
        if filepath.suffix == '.json':
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        elif filepath.suffix == '.tmx':
            return self.tmx_parser.parse_tmx(filepath)
        else:
            raise ValueError(f"Unbekanntes Dateiformat: {filepath.suffix}")
    
    def save_map(self, map_data: Dict[str, Any], filepath: Path) -> None:
        """Speichert eine Map als JSON"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(map_data, f, indent=2, ensure_ascii=False)
    
    def extract_game_data(self, old_map: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extrahiert NPCs, Warps und Trigger aus der alten Map
        
        Returns:
            Dictionary mit extrahierten Spieldaten
        """
        return {
            "npcs": old_map.get("npcs", []),
            "warps": old_map.get("warps", []),
            "triggers": old_map.get("triggers", []),
            "spawn_points": old_map.get("spawn_points", {}),
            "properties": old_map.get("properties", {})
        }
    
    def add_new_layers(self, map_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fügt die neuen Layer (furniture, decoration) zur Map hinzu falls nicht vorhanden
        """
        layers = map_data.get("layers", {})
        
        # Map-Dimensionen ermitteln
        if "ground" in layers and isinstance(layers["ground"], list):
            height = len(layers["ground"])
            width = len(layers["ground"][0]) if height > 0 else 0
        else:
            height = map_data.get("height", 0)
            width = map_data.get("width", 0)
        
        # Neue Layer hinzufügen falls nicht vorhanden
        for layer_name in self.layer_config["new_layers"]:
            if layer_name not in layers:
                layers[layer_name] = [[0] * width for _ in range(height)]
                print(f"   ➕ Layer '{layer_name}' hinzugefügt")
        
        map_data["layers"] = layers
        return map_data
    
    def reorganize_tiles(self, map_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Reorganisiert Tiles vom decor-Layer in furniture/decoration Layer
        """
        layers = map_data.get("layers", {})
        
        if "decor" not in layers:
            return map_data
        
        decor_layer = layers["decor"]
        furniture_layer = layers.get("furniture", [])
        decoration_layer = layers.get("decoration", [])
        
        moved_furniture = 0
        moved_decoration = 0
        
        for y, row in enumerate(decor_layer):
            for x, tile_id in enumerate(row):
                if tile_id == 0:
                    continue
                
                # Möbel-Tiles verschieben
                if tile_id in self.furniture_tile_range:
                    if y < len(furniture_layer) and x < len(furniture_layer[y]):
                        furniture_layer[y][x] = tile_id
                        decor_layer[y][x] = 0
                        moved_furniture += 1
                
                # Dekorations-Tiles verschieben
                elif tile_id in self.decoration_tile_range:
                    if y < len(decoration_layer) and x < len(decoration_layer[y]):
                        decoration_layer[y][x] = tile_id
                        decor_layer[y][x] = 0
                        moved_decoration += 1
        
        if moved_furniture > 0:
            print(f"   📦 {moved_furniture} Möbel-Tiles verschoben")
        if moved_decoration > 0:
            print(f"   🎨 {moved_decoration} Deko-Tiles verschoben")
        
        return map_data
    
    def merge_game_data(self, new_map: Dict[str, Any], old_game_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Intelligent merge der Spieldaten: Kombiniert alte und neue Daten
        """
        # Wenn die neue Map bereits eigene Daten hat, diese bevorzugen
        # aber fehlende Daten aus der alten Map ergänzen
        
        # NPCs: Merge basierend auf ID
        existing_npc_ids = {npc.get('id') for npc in new_map.get('npcs', [])}
        for old_npc in old_game_data.get('npcs', []):
            if old_npc.get('id') not in existing_npc_ids:
                new_map.setdefault('npcs', []).append(old_npc)
        
        # Warps: Intelligenter Merge
        if not new_map.get('warps'):
            new_map['warps'] = old_game_data.get('warps', [])
        else:
            # Prüfe ob alte Warps fehlen
            print(f"   ℹ️  Neue Map hat bereits {len(new_map['warps'])} Warps definiert")
        
        # Triggers: Ähnlich wie NPCs
        if not new_map.get('triggers'):
            new_map['triggers'] = old_game_data.get('triggers', [])
        
        # Spawn Points ergänzen
        old_spawns = old_game_data.get('spawn_points', {})
        new_map.setdefault('spawn_points', {}).update(old_spawns)
        
        # Properties merge
        old_props = old_game_data.get('properties', {})
        new_map.setdefault('properties', {}).update(old_props)
        
        return new_map
    
    def validate_positions(self, map_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validiert und korrigiert NPC/Warp-Positionen für die Map
        """
        collision_layer = map_data.get("layers", {}).get("collision", [])
        if not collision_layer:
            print("   ⚠️  Keine Collision-Layer gefunden, überspringe Positions-Validierung")
            return map_data
        
        map_height = len(collision_layer)
        map_width = len(collision_layer[0]) if map_height > 0 else 0
        
        # NPCs validieren
        valid_npcs = []
        for npc in map_data.get("npcs", []):
            x, y = npc.get("x", 0), npc.get("y", 0)
            
            # Prüfen ob Position innerhalb der Map
            if 0 <= x < map_width and 0 <= y < map_height:
                # Prüfen ob Position nicht blockiert ist
                if collision_layer[y][x] == 0:
                    valid_npcs.append(npc)
                else:
                    # Versuche nahegelegene freie Position zu finden
                    new_pos = self.find_nearby_free_position(x, y, collision_layer)
                    if new_pos:
                        npc["x"], npc["y"] = new_pos
                        valid_npcs.append(npc)
                        print(f"   ⚠️  NPC '{npc.get('name', 'unnamed')}' verschoben: ({x},{y}) → {new_pos}")
                    else:
                        print(f"   ❌ NPC '{npc.get('name', 'unnamed')}' konnte nicht platziert werden")
            else:
                print(f"   ❌ NPC '{npc.get('name', 'unnamed')}' außerhalb der Map ({x},{y})")
        
        map_data["npcs"] = valid_npcs
        
        return map_data
    
    def find_nearby_free_position(self, x: int, y: int, collision_layer: List[List[int]], 
                                   max_distance: int = 3) -> Optional[Tuple[int, int]]:
        """
        Findet eine freie Position in der Nähe der gegebenen Koordinaten
        """
        for dist in range(1, max_distance + 1):
            for dy in range(-dist, dist + 1):
                for dx in range(-dist, dist + 1):
                    if abs(dx) != dist and abs(dy) != dist:
                        continue
                    
                    new_x, new_y = x + dx, y + dy
                    
                    if (0 <= new_y < len(collision_layer) and 
                        0 <= new_x < len(collision_layer[0]) and
                        collision_layer[new_y][new_x] == 0):
                        return (new_x, new_y)
        
        return None
    
    def migrate_single_map(self, map_name: str) -> bool:
        """
        Migriert eine einzelne Map
        
        Returns:
            True bei Erfolg, False bei Fehler
        """
        print(f"\n🗺️  Migriere Map: {map_name}")
        
        old_map_path = self.old_maps_dir / f"{map_name}.json"
        
        # Suche nach neuer Map (TMX oder JSON)
        new_map_path = None
        for ext in ['.tmx', '.json']:
            test_path = self.new_maps_dir / f"{map_name}{ext}"
            if test_path.exists():
                new_map_path = test_path
                break
        
        if not new_map_path:
            print(f"   ❌ Neue Map nicht gefunden (gesucht: {map_name}.tmx oder .json)")
            return False
        
        print(f"   📂 Verwende neue Map: {new_map_path}")
        
        try:
            # Neue Map laden (TMX oder JSON)
            new_map = self.load_map(new_map_path)
            
            # Alte Map laden falls vorhanden
            old_game_data = {}
            if old_map_path.exists():
                print("   📋 Extrahiere Spieldaten aus alter Map...")
                old_map = self.load_map(old_map_path)
                old_game_data = self.extract_game_data(old_map)
            else:
                print("   ℹ️  Keine alte Map gefunden, verwende nur neue Daten")
            
            # Neue Layer hinzufügen
            print("   🔧 Füge neue Layer hinzu...")
            new_map = self.add_new_layers(new_map)
            
            # Tiles reorganisieren
            print("   🔄 Reorganisiere Tiles...")
            new_map = self.reorganize_tiles(new_map)
            
            # Daten zusammenführen
            if old_game_data:
                print("   🔀 Füge Spieldaten ein...")
                new_map = self.merge_game_data(new_map, old_game_data)
            
            # Positionen validieren
            print("   ✅ Validiere Positionen...")
            new_map = self.validate_positions(new_map)
            
            # Map speichern
            output_path = self.old_maps_dir / f"{map_name}.json"
            self.save_map(new_map, output_path)
            print(f"   ✅ Map gespeichert: {output_path}")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Fehler bei Migration: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def migrate_all_maps(self, map_list: Optional[List[str]] = None) -> None:
        """
        Migriert alle angegebenen Maps
        
        Args:
            map_list: Liste der zu migrierenden Maps (ohne Dateiendung)
                     Wenn None, werden alle TMX-Maps im new_maps_dir migriert
        """
        # Backup erstellen
        self.backup_old_maps()
        
        # Map-Liste ermitteln
        if map_list is None:
            # Suche alle TMX-Dateien
            tmx_files = list(self.new_maps_dir.glob("*.tmx"))
            json_files = list(self.new_maps_dir.glob("*.json"))
            map_list = [f.stem for f in tmx_files + json_files]
            # Duplikate entfernen
            map_list = list(set(map_list))
        
        print(f"\n🚀 Starte Migration von {len(map_list)} Maps...")
        print(f"   Suche in: {self.new_maps_dir}")
        
        success_count = 0
        failed_maps = []
        
        for map_name in map_list:
            if self.migrate_single_map(map_name):
                success_count += 1
            else:
                failed_maps.append(map_name)
        
        # Zusammenfassung
        print("\n" + "="*50)
        print("📊 MIGRATION ABGESCHLOSSEN")
        print("="*50)
        print(f"✅ Erfolgreich: {success_count}/{len(map_list)}")
        
        if failed_maps:
            print(f"❌ Fehlgeschlagen: {', '.join(failed_maps)}")
        
        print(f"\n💾 Backup gespeichert in: {self.backup_dir}")
        print("🔄 Bei Problemen können Sie das Backup wiederherstellen mit:")
        print(f"   cp -r {self.backup_dir}/* {self.old_maps_dir}/")

def main():
    """Hauptfunktion"""
    
    # Konfiguration
    maps_to_migrate = [
        "player_house",
        "rival_house", 
        "museum",
        "penny",
        "bergmannsheil",
        "kohlenstadt",
        "route1"
    ]
    
    # Migrator initialisieren
    migrator = MapMigrator(
        old_maps_dir="data/maps",
        new_maps_dir="untold_story_maps",
        backup_dir="data/maps_backup"
    )
    
    # Optional: Automatisch alle TMX-Dateien finden
    # migrator.migrate_all_maps()  # Ohne Parameter = alle TMX-Dateien
    
    # Oder: Spezifische Maps migrieren
    migrator.migrate_all_maps(maps_to_migrate)
    
    print("\n✨ Tipp: Testen Sie das Spiel nun gründlich!")
    print("   python main.py")
    print("\n📝 Nächste Schritte:")
    print("   1. Validieren Sie die Maps: python map_validator.py")
    print("   2. Öffnen Sie die Maps in Tiled um das Ergebnis zu prüfen")
    print("   3. Passen Sie ggf. die Tile-ID-Bereiche im Script an")

if __name__ == "__main__":
    main()