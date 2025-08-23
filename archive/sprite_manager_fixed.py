# -*- coding: utf-8 -*-
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
