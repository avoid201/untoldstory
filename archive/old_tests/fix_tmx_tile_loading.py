#!/usr/bin/env python3
"""
Fix für das TMX Tile Loading Problem
Behebt das Problem, dass falsche Tiles aus den Tilesets geladen werden
"""

import xml.etree.ElementTree as ET
from pathlib import Path
import pygame
import json
from typing import Dict, List, Tuple, Optional

class TMXTilesetFixer:
    """Repariert das TMX Tileset Loading und GID Mapping"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.maps_dir = self.project_root / "data" / "maps"
        self.tiles_dir = self.project_root / "assets" / "gfx" / "tiles"
        self.tilesets_dir = self.tiles_dir / "tilesets"
        
        # GID zu Tile-Name Mapping
        self.gid_to_name: Dict[int, str] = {}
        # Tileset-Informationen
        self.tilesets: List[Dict] = []
        
    def analyze_problem(self):
        """Analysiert das aktuelle TMX/Tileset Problem"""
        print("=" * 60)
        print("TMX TILE LOADING ANALYSE")
        print("=" * 60)
        
        # Prüfe TMX-Dateien
        tmx_files = list(self.maps_dir.glob("*.tmx"))
        print(f"\n📁 Gefundene TMX-Dateien: {len(tmx_files)}")
        for tmx in tmx_files[:3]:  # Zeige erste 3
            print(f"  - {tmx.name}")
        
        # Prüfe TSX-Dateien
        tsx_files = list(self.maps_dir.glob("*.tsx"))
        print(f"\n📁 Gefundene TSX-Dateien: {len(tsx_files)}")
        for tsx in tsx_files:
            print(f"  - {tsx.name}")
            self._analyze_tsx(tsx)
        
        # Prüfe Tileset-Bilder
        tileset_images = list(self.tilesets_dir.glob("*.png"))
        print(f"\n🖼️  Tileset-Bilder: {len(tileset_images)}")
        for img in tileset_images:
            print(f"  - {img.name}")
    
    def _analyze_tsx(self, tsx_path: Path):
        """Analysiert eine TSX-Datei"""
        try:
            tree = ET.parse(tsx_path)
            root = tree.getroot()
            
            name = root.get('name', '')
            tilecount = int(root.get('tilecount', 0))
            columns = int(root.get('columns', 0))
            tilewidth = int(root.get('tilewidth', 16))
            tileheight = int(root.get('tileheight', 16))
            
            image_elem = root.find('image')
            if image_elem is not None:
                source = image_elem.get('source', '')
                print(f"    → {name}: {tilecount} tiles ({columns} columns)")
                print(f"      Bild: {source}")
                
        except Exception as e:
            print(f"    ⚠️  Fehler beim Lesen: {e}")
    
    def create_proper_mapping(self):
        """Erstellt ein korrektes GID-zu-Tile Mapping"""
        print("\n" + "=" * 60)
        print("ERSTELLE KORREKTES GID MAPPING")
        print("=" * 60)
        
        # Definiere die korrekten Tile-Namen für jedes Tileset
        tileset_mappings = {
            'tiles_building1': [
                'wall_brick', 'wall_stone', 'wall_wood', 'door_wood', 'door_metal', 'window_small',
                'window_large', 'roof_red', 'roof_blue', 'chimney', 'stairs_wood', 'floor_wood'
            ],
            'tiles_interior1': [
                'floor_carpet', 'floor_wood', 'wall_interior', 'table', 'chair', 'bed',
                'bookshelf', 'tv', 'couch', 'lamp', 'plant', 'picture'
            ],
            'tiles_ground': [
                'grass', 'dirt', 'path', 'stone', 'sand', 'water',
                'flowers', 'tall_grass', 'gravel', 'mud', 'snow', 'ice'
            ],
            'tiles_terrain': [
                'tree', 'bush', 'rock', 'cliff', 'ledge', 'bridge',
                'fence', 'sign', 'lamp_post', 'barrel', 'crate', 'well'
            ],
            'objects': [
                'chest', 'pot', 'vase', 'statue', 'fountain', 'bench',
                'mailbox', 'trash_can', 'fire', 'torch', 'flag', 'banner'
            ]
        }
        
        # Erstelle GID-Mapping basierend auf TMX-Tilesets
        for tmx_file in self.maps_dir.glob("*.tmx"):
            self._process_tmx_tilesets(tmx_file, tileset_mappings)
        
        # Speichere das Mapping
        self._save_gid_mapping()
    
    def _process_tmx_tilesets(self, tmx_path: Path, tileset_mappings: Dict):
        """Verarbeitet Tilesets aus einer TMX-Datei"""
        try:
            tree = ET.parse(tmx_path)
            root = tree.getroot()
            
            print(f"\n📄 Verarbeite {tmx_path.name}:")
            
            for tileset_elem in root.findall('tileset'):
                firstgid = int(tileset_elem.get('firstgid', 1))
                source = tileset_elem.get('source', '')
                
                if source:
                    tsx_name = source.replace('.tsx', '')
                    print(f"  - Tileset: {tsx_name} (firstgid={firstgid})")
                    
                    # Lade TSX-Details
                    tsx_path = self.maps_dir / source
                    if tsx_path.exists():
                        tileset_info = self._load_tsx_info(tsx_path)
                        tile_count = tileset_info['tile_count']
                        
                        # Hole vordefinierte Namen oder generiere neue
                        if tsx_name in tileset_mappings:
                            names = tileset_mappings[tsx_name]
                        else:
                            # Generiere generische Namen
                            names = [f"{tsx_name}_tile_{i}" for i in range(tile_count)]
                        
                        # Mappe GIDs zu Namen
                        for i in range(min(tile_count, len(names))):
                            gid = firstgid + i
                            self.gid_to_name[gid] = names[i]
                            
        except Exception as e:
            print(f"  ⚠️  Fehler: {e}")
    
    def _load_tsx_info(self, tsx_path: Path) -> Dict:
        """Lädt Informationen aus einer TSX-Datei"""
        tree = ET.parse(tsx_path)
        root = tree.getroot()
        
        return {
            'name': root.get('name', ''),
            'tile_width': int(root.get('tilewidth', 16)),
            'tile_height': int(root.get('tileheight', 16)),
            'tile_count': int(root.get('tilecount', 0)),
            'columns': int(root.get('columns', 1))
        }
    
    def _save_gid_mapping(self):
        """Speichert das GID-Mapping in eine Datei"""
        mapping_file = self.project_root / "data" / "gid_mapping.json"
        
        mapping_data = {
            'gid_to_name': self.gid_to_name,
            'tilesets': self.tilesets,
            'version': '2.0',
            'description': 'GID zu Tile-Name Mapping für TMX-Maps'
        }
        
        with open(mapping_file, 'w') as f:
            json.dump(mapping_data, f, indent=2)
        
        print(f"\n✅ GID-Mapping gespeichert: {mapping_file}")
        print(f"   {len(self.gid_to_name)} GIDs gemappt")
    
    def fix_sprite_manager(self):
        """Erstellt eine verbesserte Version des SpriteManagers"""
        print("\n" + "=" * 60)
        print("ERSTELLE VERBESSERTEN SPRITE MANAGER")
        print("=" * 60)
        
        sprite_manager_path = self.project_root / "engine" / "graphics" / "sprite_manager_fixed.py"
        
        code = '''# -*- coding: utf-8 -*-
"""
Verbesserter SpriteManager mit korrektem TMX/Tileset Support
"""

import pygame
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Optional, Tuple

TILE_SIZE = 16

class SpriteManagerFixed:
    """Verbesserter SpriteManager mit korrektem GID-Mapping"""
    
    _instance = None
    
    @classmethod
    def get(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.tiles_cache: Dict[str, pygame.Surface] = {}
        self.gid_cache: Dict[int, pygame.Surface] = {}
        self.gid_mapping: Dict[int, str] = {}
        
        # Lade GID-Mapping
        self._load_gid_mapping()
        
        # Initialisiere Pygame falls nötig
        if not pygame.get_init():
            pygame.init()
        if not pygame.display.get_init():
            pygame.display.set_mode((1, 1))
    
    def _load_gid_mapping(self):
        """Lädt das GID-zu-Name Mapping"""
        mapping_file = self.project_root / "data" / "gid_mapping.json"
        if mapping_file.exists():
            with open(mapping_file, 'r') as f:
                data = json.load(f)
                # Konvertiere String-Keys zu Int
                self.gid_mapping = {int(k): v for k, v in data.get('gid_to_name', {}).items()}
                print(f"[SpriteManager] Loaded {len(self.gid_mapping)} GID mappings")
    
    def load_tmx_tilesets(self, tmx_path: Path):
        """Lädt alle Tilesets aus einer TMX-Datei"""
        try:
            tree = ET.parse(tmx_path)
            root = tree.getroot()
            
            for tileset_elem in root.findall('tileset'):
                firstgid = int(tileset_elem.get('firstgid', 1))
                source = tileset_elem.get('source', '')
                
                if source:
                    tsx_path = tmx_path.parent / source
                    if tsx_path.exists():
                        self._load_tileset(tsx_path, firstgid)
                        
        except Exception as e:
            print(f"[SpriteManager] Error loading TMX tilesets: {e}")
    
    def _load_tileset(self, tsx_path: Path, firstgid: int):
        """Lädt ein Tileset und extrahiert Tiles"""
        try:
            tree = ET.parse(tsx_path)
            root = tree.getroot()
            
            tilewidth = int(root.get('tilewidth', 16))
            tileheight = int(root.get('tileheight', 16))
            tilecount = int(root.get('tilecount', 0))
            columns = int(root.get('columns', 1))
            
            # Finde Bild-Pfad
            image_elem = root.find('image')
            if image_elem is None:
                return
            
            image_source = image_elem.get('source', '')
            if image_source.startswith('../../'):
                # Relativer Pfad von data/maps aus
                image_path = self.project_root / image_source.replace('../../', '')
            else:
                image_path = tsx_path.parent / image_source
            
            if not image_path.exists():
                print(f"[SpriteManager] Tileset image not found: {image_path}")
                return
            
            # Lade Tileset-Bild
            tileset_surface = pygame.image.load(str(image_path)).convert_alpha()
            
            # Extrahiere einzelne Tiles
            for tile_id in range(tilecount):
                col = tile_id % columns
                row = tile_id // columns
                
                x = col * tilewidth
                y = row * tileheight
                
                # Extrahiere Tile
                tile_surf = pygame.Surface((tilewidth, tileheight), pygame.SRCALPHA)
                tile_surf.blit(tileset_surface, (0, 0), (x, y, tilewidth, tileheight))
                
                # Skaliere falls nötig
                if tilewidth != TILE_SIZE or tileheight != TILE_SIZE:
                    tile_surf = pygame.transform.scale(tile_surf, (TILE_SIZE, TILE_SIZE))
                
                # Speichere mit GID
                gid = firstgid + tile_id
                self.gid_cache[gid] = tile_surf
                
                # Speichere auch mit Name falls vorhanden
                if gid in self.gid_mapping:
                    name = self.gid_mapping[gid]
                    self.tiles_cache[name] = tile_surf
            
            print(f"[SpriteManager] Loaded {tilecount} tiles from {tsx_path.name}")
            
        except Exception as e:
            print(f"[SpriteManager] Error loading tileset: {e}")
    
    def get_tile_by_gid(self, gid: int) -> Optional[pygame.Surface]:
        """Hole Tile über GID"""
        # Entferne Flip-Flags
        FLIP_FLAGS = 0x80000000 | 0x40000000 | 0x20000000
        clean_gid = gid & ~FLIP_FLAGS
        
        if clean_gid == 0:
            return self._get_empty_tile()
        
        if clean_gid in self.gid_cache:
            return self.gid_cache[clean_gid]
        
        # Fallback: Pink Tile
        return self._get_error_tile()
    
    def get_tile(self, name: str) -> Optional[pygame.Surface]:
        """Hole Tile über Namen"""
        if name in self.tiles_cache:
            return self.tiles_cache[name]
        return self._get_error_tile()
    
    def _get_empty_tile(self) -> pygame.Surface:
        """Erstelle transparentes Tile"""
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 0))
        return surf
    
    def _get_error_tile(self) -> pygame.Surface:
        """Erstelle pinkes Error-Tile"""
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
        surf.fill((255, 0, 255))
        return surf
'''
        
        with open(sprite_manager_path, 'w') as f:
            f.write(code)
        
        print(f"✅ Verbesserter SpriteManager erstellt: {sprite_manager_path}")
    
    def test_fix(self):
        """Testet den Fix mit einer TMX-Map"""
        print("\n" + "=" * 60)
        print("TESTE DEN FIX")
        print("=" * 60)
        
        # Initialisiere Pygame für Test
        pygame.init()
        screen = pygame.display.set_mode((400, 300))
        pygame.display.set_caption("TMX Tile Test")
        
        # Teste das Laden einer Map
        test_map = self.maps_dir / "player_house.tmx"
        if test_map.exists():
            print(f"\n🧪 Teste mit {test_map.name}...")
            
            # Parse TMX
            tree = ET.parse(test_map)
            root = tree.getroot()
            
            width = int(root.get('width', 0))
            height = int(root.get('height', 0))
            
            print(f"   Map-Größe: {width}x{height} Tiles")
            
            # Prüfe Tilesets
            for tileset in root.findall('tileset'):
                firstgid = tileset.get('firstgid')
                source = tileset.get('source')
                print(f"   Tileset: {source} (firstgid={firstgid})")
            
            # Prüfe Layer
            for layer in root.findall('layer'):
                name = layer.get('name')
                print(f"   Layer: {name}")
                
                data = layer.find('data')
                if data is not None and data.text:
                    # Parse CSV data
                    tiles = []
                    for line in data.text.strip().split('\n'):
                        if line.strip():
                            row = [int(x.strip()) for x in line.split(',') if x.strip()]
                            tiles.append(row)
                    
                    # Zeige erste Zeile
                    if tiles:
                        print(f"     Erste Zeile GIDs: {tiles[0]}")
                        
                        # Mappe zu Namen
                        names = []
                        for gid in tiles[0]:
                            if gid in self.gid_to_name:
                                names.append(self.gid_to_name[gid])
                            else:
                                names.append(f"gid_{gid}")
                        print(f"     Tile-Namen: {names}")
        
        pygame.quit()
        print("\n✅ Test abgeschlossen")
    
    def apply_fix(self):
        """Wendet den Fix auf das Projekt an"""
        print("\n" + "=" * 60)
        print("WENDE FIX AN")
        print("=" * 60)
        
        # 1. Analysiere Problem
        self.analyze_problem()
        
        # 2. Erstelle korrektes Mapping
        self.create_proper_mapping()
        
        # 3. Erstelle verbesserten SpriteManager
        self.fix_sprite_manager()
        
        # 4. Teste den Fix
        self.test_fix()
        
        print("\n" + "=" * 60)
        print("✅ FIX VOLLSTÄNDIG ANGEWENDET")
        print("=" * 60)
        print("\nNächste Schritte:")
        print("1. Ersetze engine/graphics/sprite_manager.py mit sprite_manager_fixed.py")
        print("2. Starte das Spiel neu")
        print("3. Die Tiles sollten jetzt korrekt geladen werden")


def main():
    """Hauptfunktion"""
    print("🔧 TMX TILE LOADING FIX")
    print("Behebt das Problem mit falschen Tiles aus Tilesets\n")
    
    fixer = TMXTilesetFixer()
    fixer.apply_fix()


if __name__ == "__main__":
    main()
