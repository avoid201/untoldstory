"""
Tile System and Helper Functions for Untold Story
Defines tile constants, grid helpers, and tile-based collision utilities
"""

import pygame
from typing import Tuple, Optional, List, Set
from enum import IntEnum
import os
from pathlib import Path


class TilesetManager:
    """Verwaltet das Laden und Aufteilen von Tileset-Grafiken"""
    
    def __init__(self, sprite_manager=None):
        self.tile_surfaces = {}
        self.tileset_path = None
        self.sprite_manager = sprite_manager
        
    def load_tileset(self, filepath: str, tile_size: int = 64):
        """Lädt Tiles aus dem SpriteManager oder erstellt Placeholder"""
        import pygame
        import os
        
        # Aktualisiere die Tile-Größe
        self.tile_size = tile_size
        
        try:
            # Lade das Tile-Mapping zuerst
            self._load_tile_mapping()
            
            # Wenn wir einen SpriteManager haben, verwende dessen Sprites
            if self.sprite_manager and hasattr(self.sprite_manager, 'sprite_cache'):
                sprites_loaded = self._load_from_sprite_manager(tile_size)
                if sprites_loaded > 0:
                    print(f"Tileset geladen: {sprites_loaded} Sprites aus dem SpriteManager")
                    return True
            
            # Fallback: Lade einzelne Sprites basierend auf dem Mapping
            sprites_loaded = self._load_individual_sprites(tile_size)
            if sprites_loaded > 0:
                print(f"Tileset geladen: {sprites_loaded} Sprites aus dem sprites/ Verzeichnis")
                return True
            
            # Letzter Fallback: Fallback-Tiles
            print("Keine Sprites gefunden, verwende Fallback-Tiles")
            self._create_fallback_tiles(tile_size)
            return False
            
        except Exception as e:
            print(f"Fehler beim Laden des Tilesets: {e}")
            # Fallback zu Fallback-Tiles
            self._create_fallback_tiles(tile_size)
            return False
    
    def _load_from_sprite_manager(self, tile_size: int) -> int:
        """Lädt Tiles aus dem SpriteManager"""
        if not self.sprite_manager or not hasattr(self.sprite_manager, 'sprite_cache'):
            return 0
            
        sprites_loaded = 0
        
        # Mapping von Sprite-Namen zu Tile-IDs (verwende _large Versionen)
        sprite_to_tile_mapping = {
            # Grund-Tiles
            "Void_large.png": 0,
            "Grass-flat_large.png": 1,
            "Path_large.png": 2,
            "Flooring-type-01_large.png": 3,
            "Flooring-type-02_large.png": 9,
            
            # Bäume
            "Tree-short-00_large.png": 10,
            "Tree-short-01_large.png": 11,
            "Tree-short-02_large.png": 12,
            "Tree-short-03_large.png": 13,
            "Tree-tall-00_large.png": 14,
            "Tree-tall-01_large.png": 15,
            
            # Möbel
            "Table-type-1-00_large.png": 20,
            "Table-type-1-01_large.png": 21,
            "Table-type-1-02_large.png": 22,
            "Table-type-1-03_large.png": 23,
            "Table-type-1-04_large.png": 24,
            "Table-type-1-05_large.png": 25,
            "Table-type-1-06_large.png": 26,
            "Table-type-1-07_large.png": 27,
            "Table-type-1-08_large.png": 28,
            "Table-type-1-09_large.png": 29,
            "Table-type-1-10_large.png": 30,
            "Table-type-1-11_large.png": 31,
            
            "Stool-type-01-00_large.png": 32,
            "Stool-type-01-01_large.png": 33,
            "Stool-type-01-02_large.png": 34,
            "Stool-type-01-03_large.png": 35,
            "Stool-type-02-00_large.png": 36,
            "Stool-type-02-01_large.png": 37,
            "Stool-type-02-02_large.png": 38,
            "Stool-type-02-03_large.png": 39,
            
            "Stove-00_large.png": 40,
            "Stove-01_large.png": 41,
            "Stove-02_large.png": 42,
            "Stove-03_large.png": 43,
            
            "Sink-00_large.png": 44,
            "Sink-01_large.png": 45,
            
            "Fridge-type-01-00_large.png": 46,
            "Fridge-type-01-01_large.png": 47,
            "Fridge-type-01-02_large.png": 48,
            "Fridge-type-01-03_large.png": 49,
            "Fridge-type-01-04_large.png": 50,
            "Fridge-type-01-05_large.png": 51,
            
            "Computer-type-01-00_large.png": 52,
            "Computer-type-01-01_large.png": 53,
            "Computer-type-01-02_large.png": 54,
            "Computer-type-01-03_large.png": 55,
            "Computer-type-01-04_large.png": 56,
            "Computer-type-01-05_large.png": 57,
            
            "TV-type-01-00_large.png": 58,
            "TV-type-01-01_large.png": 59,
            "TV-type-01-02_large.png": 60,
            "TV-type-01-03_large.png": 61,
            
            "Radio-type-01-00_large.png": 62,
            "Radio-type-01-01_large.png": 63,
            "Radio-type-01-02_large.png": 64,
            "Radio-type-01-03_large.png": 65,
            "Radio-type-02-00_large.png": 66,
            "Radio-type-02-01_large.png": 67,
            "Radio-type-02-02_large.png": 68,
            "Radio-type-02-03_large.png": 69,
            
            "Bed-type-01-00_large.png": 70,
            "Bed-type-01-01_large.png": 71,
            "Bed-type-01-02_large.png": 72,
            "Bed-type-01-03_large.png": 73,
            "Bed-type-01-04_large.png": 74,
            "Bed-type-01-05_large.png": 75,
            "Bed-type-01-06_large.png": 76,
            "Bed-type-01-07_large.png": 77,
            
            "Bookshelf-type-01-00_large.png": 78,
            "Bookshelf-type-01-01_large.png": 79,
            "Bookshelf-type-01-02_large.png": 80,
            "Bookshelf-type-01-03_large.png": 81,
            "Bookshelf-type-01-04_large.png": 82,
            "Bookshelf-type-01-05_large.png": 83,
            "Bookshelf-type-01-06_large.png": 84,
            "Bookshelf-type-01-07_large.png": 85,
            
            "Indoor-plant-type-01-00_large.png": 86,
            "Indoor-plant-type-01-01_large.png": 87,
            "Indoor-plant-type-01-02_large.png": 88,
            "Indoor-plant-type-01-03_large.png": 89,
            "Indoor-plant-type-01-04_large.png": 90,
            "Indoor-plant-type-01-05_large.png": 91,
            "Indoor-plant-type-01-06_large.png": 92,
            "Indoor-plant-type-01-07_large.png": 93,
            
            "Flower-johto-00_large.png": 94,
            "Flower-johto-01_large.png": 95,
            
            # Gebäude
            "Back-wall-art-00_large.png": 100,
            "Back-wall-art-01_large.png": 101,
            "Back-wall-art-02_large.png": 102,
            "Back-wall-art-03_large.png": 103,
            "Back-wall-window-00_large.png": 104,
            "Back-wall-window-01_large.png": 105,
            "Back-wall-window-02_large.png": 106,
            "Back-wall-window-03_large.png": 107,
            "Back-wall-wood_large.png": 108,
            "Building-cladding-00_large.png": 109,
            "Building-cladding-01_large.png": 110,
            "Building-door-00_large.png": 111,
            "Building-door-01_large.png": 112,
            "Building-door-02_large.png": 113,
            "Building-door-03_large.png": 114,
            "Building-roof-flat-00_large.png": 115,
            "Building-roof-flat-01_large.png": 116,
            "Building-roof-flat-02_large.png": 117,
            "Building-roof-flat-03_large.png": 118,
            "Building-roof-flat-04_large.png": 119,
            "Building-roof-flat-05_large.png": 120,
            "Building-roof-flat-06_large.png": 121,
            "Building-roof-flat-07_large.png": 122,
            "Building-roof-flat-08_large.png": 123,
            "Building-wall-00_large.png": 124,
            "Building-wall-01_large.png": 125,
            "Building-wall-02_large.png": 126,
            "Building-wall-03_large.png": 127,
            "Building-wall-04_large.png": 128,
            "Building-window_large.png": 129,
            "Ridge-00_large.png": 130,
            "Ridge-01_large.png": 131,
            "Ridge-02_large.png": 132,
            "Ridge-03_large.png": 133,
            "Ridge-04_large.png": 134,
            "Ridge-05_large.png": 135,
            "Ridge-06_large.png": 136,
            "Ridge-07_large.png": 137,
            "Ridge-08_large.png": 138,
            "Sign-metal-00_large.png": 139,
            "Sign-metal-01_large.png": 140,
            "Sign-metal-02_large.png": 141,
            "Sign-metal-03_large.png": 142,
            
            # Wasser
            "Water-frame-00_large.png": 150,
            "Water-frame-01_large.png": 151,
            "Water-frame-02_large.png": 152,
            "Water-frame-03_large.png": 153,
        }
        
        # Lade Sprites aus dem SpriteManager
        for sprite_name, tile_id in sprite_to_tile_mapping.items():
            if sprite_name in self.sprite_manager.sprite_cache:
                sprite_surface = self.sprite_manager.sprite_cache[sprite_name]
                if sprite_surface:
                    # Skaliere das Sprite auf die gewünschte Tile-Größe
                    if sprite_surface.get_size() != (tile_size, tile_size):
                        sprite_surface = pygame.transform.scale(sprite_surface, (tile_size, tile_size))
                    
                    self.tile_surfaces[tile_id] = sprite_surface
                    sprites_loaded += 1
                    print(f"Tile {tile_id} geladen: {sprite_name} -> {sprite_surface.get_size()}")
        
        return sprites_loaded
    
    def _load_individual_sprites(self, tile_size: int) -> int:
        """Lädt einzelne Sprites basierend auf dem Mapping"""
        sprites_loaded = 0
        
        # Korrekte Sprite-Namen für die verfügbaren Sprites
        sprite_name_mapping = {
            "void": "Void.png",
            "grass": "Grass-flat.png", 
            "path_gravel": "Path-Gravel.png",
            "floor": "Flooring-type-01.png",
            "chest": "Building-cladding-00.png",  # Fallback
            "pc": "Computer-type-01-00.png",
            "tv": "TV-type-01-00.png",
            "tv2": "TV-type-01-01.png",
            "grass_flat": "Grass-flat.png",
            "grass_rustle_00": "Grass-rustle-00.png",
            "grass_rustle_01": "Grass-rustle-01.png", 
            "grass_tall": "Grass-tall.png",
            "flooring_type_01": "Flooring-type-01.png",
            "flooring_type_02": "Flooring-type-02.png",
            "tree_short_00": "Tree-short-00.png",
            "tree_short_01": "Tree-short-01.png",
            "tree_short_02": "Tree-short-02.png",
            "tree_short_03": "Tree-short-03.png",
            "tree_tall_00": "Tree-tall-00.png",
            "tree_tall_01": "Tree-tall-01.png",
            "table_type_1_00": "Table-type-1-00.png",
            "table_type_1_01": "Table-type-1-01.png",
            "table_type_1_02": "Table-type-1-02.png",
            "table_type_1_03": "Table-type-1-03.png",
            "table_type_1_04": "Table-type-1-04.png",
            "table_type_1_05": "Table-type-1-05.png",
            "table_type_1_06": "Table-type-1-06.png",
            "table_type_1_07": "Table-type-1-07.png",
            "table_type_1_08": "Table-type-1-08.png",
            "table_type_1_09": "Table-type-1-09.png",
            "table_type_1_10": "Table-type-1-10.png",
            "table_type_1_11": "Table-type-1-11.png",
            "stool_type_01_00": "Stool-type-01-00.png",
            "stool_type_01_01": "Stool-type-01-01.png",
            "stool_type_01_02": "Stool-type-01-02.png",
            "stool_type_01_03": "Stool-type-01-03.png",
            "stool_type_02_00": "Stool-type-02-00.png",
            "stool_type_02_01": "Stool-type-02-01.png",
            "stool_type_02_02": "Stool-type-02-02.png",
            "stool_type_02_03": "Stool-type-02-03.png",
            "stove_00": "Stove-00.png",
            "stove_01": "Stove-01.png",
            "stove_02": "Stove-02.png",
            "stove_03": "Stove-03.png",
            "sink_00": "Sink-00.png",
            "sink_01": "Sink-01.png",
            "fridge_type_01_00": "Fridge-type-01-00.png",
            "fridge_type_01_01": "Fridge-type-01-01.png",
            "fridge_type_01_02": "Fridge-type-01-02.png",
            "fridge_type_01_03": "Fridge-type-01-03.png",
            "fridge_type_01_04": "Fridge-type-01-04.png",
            "fridge_type_01_05": "Fridge-type-01-05.png",
            "computer_type_01_00": "Computer-type-01-00.png",
            "computer_type_01_01": "Computer-type-01-01.png",
            "computer_type_01_02": "Computer-type-01-02.png",
            "computer_type_01_03": "Computer-type-01-03.png",
            "computer_type_01_04": "Computer-type-01-04.png",
            "computer_type_01_05": "Computer-type-01-05.png",
            "tv_type_01_00": "TV-type-01-00.png",
            "tv_type_01_01": "TV-type-01-01.png",
            "tv_type_01_02": "TV-type-01-02.png",
            "tv_type_01_03": "TV-type-01-03.png",
            "radio_type_01_00": "Radio-type-01-00.png",
            "radio_type_01_01": "Radio-type-01-01.png",
            "radio_type_01_02": "Radio-type-01-02.png",
            "radio_type_01_03": "Radio-type-01-03.png",
            "radio_type_02_00": "Radio-type-02-00.png",
            "radio_type_02_01": "Radio-type-02-01.png",
            "radio_type_02_02": "Radio-type-02-02.png",
            "radio_type_02_03": "Radio-type-02-03.png",
            "bed_type_01_00": "Bed-type-01-00.png",
            "bed_type_01_01": "Bed-type-01-01.png",
            "bed_type_01_02": "Bed-type-01-02.png",
            "bed_type_01_03": "Bed-type-01-03.png",
            "bed_type_01_04": "Bed-type-01-04.png",
            "bed_type_01_05": "Bed-type-01-05.png",
            "bed_type_01_06": "Bed-type-01-06.png",
            "bed_type_01_07": "Bed-type-01-07.png",
            "bookshelf_type_01_00": "Bookshelf-type-01-00.png",
            "bookshelf_type_01_01": "Bookshelf-type-01-01.png",
            "bookshelf_type_01_02": "Bookshelf-type-01-02.png",
            "bookshelf_type_01_03": "Bookshelf-type-01-03.png",
            "bookshelf_type_01_04": "Bookshelf-type-01-04.png",
            "bookshelf_type_01_05": "Bookshelf-type-01-05.png",
            "bookshelf_type_01_06": "Bookshelf-type-01-06.png",
            "bookshelf_type_01_07": "Bookshelf-type-01-07.png",
            "indoor_plant_type_01_00": "Indoor-plant-type-01-00.png",
            "indoor_plant_type_01_01": "Indoor-plant-type-01-01.png",
            "indoor_plant_type_01_02": "Indoor-plant-type-01-02.png",
            "indoor_plant_type_01_03": "Indoor-plant-type-01-03.png",
            "indoor_plant_type_01_04": "Indoor-plant-type-01-04.png",
            "indoor_plant_type_01_05": "Indoor-plant-type-01-05.png",
            "indoor_plant_type_01_06": "Indoor-plant-type-01-06.png",
            "indoor_plant_type_01_07": "Indoor-plant-type-01-07.png",
            "flower_johto_00": "Flower-johto-00.png",
            "flower_johto_01": "Flower-johto-01.png",
            "ridge_00": "Ridge-00.png",
            "ridge_01": "Ridge-01.png",
            "ridge_02": "Ridge-02.png",
            "ridge_03": "Ridge-03.png",
            "ridge_04": "Ridge-04.png",
            "ridge_05": "Ridge-05.png",
            "ridge_06": "Ridge-06.png",
            "ridge_07": "Ridge-07.png",
            "ridge_08": "Ridge-08.png",
            "sign_metal_00": "Sign-metal-00.png",
            "sign_metal_01": "Sign-metal-01.png",
            "sign_metal_02": "Sign-metal-02.png",
            "sign_metal_03": "Sign-metal-03.png",
            "indoor_exit_mat_type_01_00": "Indoor-exit-mat-type-01-00.png",
            "indoor_exit_mat_type_01_01": "Indoor-exit-mat-type-01-01.png",
            "indoor_exit_mat_type_02_00": "Indoor-exit-mat-type-02-00.png",
            "indoor_exit_mat_type_02_01": "Indoor-exit-mat-type-02-01.png",
            "outdoor_exit_mat_type_01": "Outdoor-exit-mat.png",
            "outdoor_exit_mat_type_02": "Outdoor-exit-mat.png",
            "water_frame_00": "Water-frame-00.png",
            "water_frame_01": "Water-frame-01.png",
            "water_frame_02": "Water-frame-02.png",
            "water_frame_03": "Water-frame-03.png"
        }
        
        for mapping_id, tile_info in self.tile_mapping.items():
            # Verwende den korrekten Sprite-Namen
            tile_name = tile_info.get("name", "").lower().replace("-", "_").replace(" ", "_")
            sprite_name = sprite_name_mapping.get(tile_name, f"{mapping_id}.png")
            
            # Try to load using resource manager first
            try:
                from engine.core.resources import resources
                if hasattr(resources, 'load_sprite'):
                    sprite_surface = resources.load_sprite(sprite_name)
                    if sprite_surface:
                        # Skaliere auf die gewünschte Tile-Größe
                        if sprite_surface.get_size() != (tile_size, tile_size):
                            sprite_surface = pygame.transform.scale(sprite_surface, (tile_size, tile_size))
                        self.tile_surfaces[mapping_id] = sprite_surface
                        sprites_loaded += 1
                        continue
            except Exception as e:
                print(f"Fehler beim Laden von {sprite_name} über ResourceManager: {e}")
            
            # Fallback: direkte Pfad-Behandlung
            sprite_path = f"sprites/{sprite_name}"
            if os.path.exists(sprite_path):
                try:
                    sprite_surface = pygame.image.load(sprite_path).convert_alpha()
                    # Skaliere auf die gewünschte Tile-Größe
                    if sprite_surface.get_size() != (tile_size, tile_size):
                        sprite_surface = pygame.transform.scale(sprite_surface, (tile_size, tile_size))
                    self.tile_surfaces[mapping_id] = sprite_surface
                    sprites_loaded += 1
                except Exception as e:
                    print(f"Fehler beim Laden von {sprite_path}: {e}")
            else:
                print(f"Sprite nicht gefunden: {sprite_path}")
        
        return sprites_loaded
    
    def _create_fallback_tiles(self, tile_size: int = 64):
        """Erstellt Fallback-Tiles aus den echten Sprite-Dateien"""
        print(f"Lade Tiles aus dem Sprites-Ordner...")
        
        # Liste der verfügbaren Tile-Sprites
        sprite_files = [
            "Void.png", "Grass-flat.png", "Path.png", "Path-Gravel.png",
            "Flooring-type-01.png", "Flooring-type-02.png",
            "Building-wall-00.png", "Building-wall-01.png", "Building-wall-02.png",
            "Building-wall-03.png", "Building-wall-04.png",
            "Building-door-00.png", "Building-door-01.png", "Building-door-02.png", "Building-door-03.png",
            "Building-window.png", "Building-roof-flat-00.png", "Building-roof-flat-01.png",
            "Building-roof-flat-02.png", "Building-roof-flat-03.png", "Building-roof-flat-04.png",
            "Building-roof-flat-05.png", "Building-roof-flat-06.png", "Building-roof-flat-07.png", "Building-roof-flat-08.png",
            "Building-cladding-00.png", "Building-cladding-01.png",
            "Tree-tall-00.png", "Tree-tall-01.png", "Tree-short-00.png", "Tree-short-01.png",
            "Tree-short-02.png", "Tree-short-03.png",
            "Ridge-00.png", "Ridge-01.png", "Ridge-02.png", "Ridge-03.png",
            "Ridge-04.png", "Ridge-05.png", "Ridge-06.png", "Ridge-07.png", "Ridge-08.png",
            "Sign-metal-00.png", "Sign-metal-01.png", "Sign-metal-02.png", "Sign-metal-03.png",
            "Flower-johto-00.png", "Flower-johto-01.png"
        ]
        
        tile_id = 0
        for sprite_name in sprite_files:
            try:
                # Versuche zuerst über den ResourceManager zu laden
                if hasattr(self, 'sprite_manager') and self.sprite_manager:
                    sprite = self.sprite_manager.load_sprite(sprite_name)
                    if sprite:
                        # Skaliere Sprite auf Tile-Größe falls nötig
                        if sprite.get_size() != (tile_size, tile_size):
                            sprite = pygame.transform.scale(sprite, (tile_size, tile_size))
                        
                        self.tile_surfaces[tile_id] = sprite
                        print(f"Tile {tile_id} geladen: {sprite_name}")
                        tile_id += 1
                        continue
                
                # Fallback: direkte Pfad-Behandlung
                sprite_path = os.path.join("sprites", sprite_name)
                if os.path.exists(sprite_path):
                    sprite = pygame.image.load(sprite_path).convert_alpha()
                    if sprite:
                        # Skaliere Sprite auf Tile-Größe falls nötig
                        if sprite.get_size() != (tile_size, tile_size):
                            sprite = pygame.transform.scale(sprite, (tile_size, tile_size))
                        
                        self.tile_surfaces[tile_id] = sprite
                        print(f"Tile {tile_id} geladen: {sprite_name}")
                        tile_id += 1
                    else:
                        print(f"Fehler beim Laden des Sprites: {sprite_name}")
                else:
                    print(f"Sprite-Datei nicht gefunden: {sprite_name}")
            except Exception as e:
                print(f"Fehler beim Laden des Sprites {sprite_name}: {e}")
        
        # Falls nicht genug Tiles geladen wurden, erstelle einfache farbige
        if len(self.tile_surfaces) < 64:  # Minimum Tiles benötigt
            print(f"Nur {len(self.tile_surfaces)} Tiles geladen, erstelle einfache farbige...")
            for i in range(len(self.tile_surfaces), 64):
                tile_surface = pygame.Surface((tile_size, tile_size))
                
                # Verschiedene Farben für verschiedene Tile-Typen
                if i == 0:  # Void
                    color = (0, 0, 0, 0)  # Transparent
                elif i == 1:  # Grass
                    color = (34, 139, 34)  # Forest green
                elif i == 2:  # Path
                    color = (139, 69, 19)  # Saddle brown
                elif i == 3:  # Floor
                    color = (128, 128, 128)  # Gray
                elif i == 4:  # Water
                    color = (70, 130, 180)  # Steel blue
                elif i == 5:  # Wall
                    color = (105, 105, 105)  # Dim gray
                else:
                    # Zufällige Farbe für andere Tiles
                    import random
                    color = (random.randint(50, 200), random.randint(50, 200), random.randint(50, 200))
                
                tile_surface.fill(color)
                
                # Füge eine Nummer hinzu für bessere Identifikation
                if i > 0:
                    try:
                        font = pygame.font.Font(None, min(tile_size // 4, 24))
                        text = font.render(str(i), True, (255, 255, 255))
                        text_rect = text.get_rect(center=(tile_size // 2, tile_size // 2))
                        tile_surface.blit(text, text_rect)
                    except:
                        pass  # Ignoriere Font-Fehler
                
                self.tile_surfaces[i] = tile_surface
        
        print(f"Tileset erstellt: {len(self.tile_surfaces)} Tiles ({tile_size}x{tile_size})")
    
    def get_tile(self, tile_id: int):
        """Gibt die Surface für eine bestimmte Tile-ID zurück"""
        # Verwende das Mapping, falls verfügbar
        if hasattr(self, 'tile_mapping') and tile_id in self.tile_mapping:
            return self.tile_surfaces.get(tile_id, None)
        else:
            # Fallback: direkte ID
            return self.tile_surfaces.get(tile_id, None)
    
    def _load_tile_mapping(self):
        """Lädt das Tile-Mapping und erstellt die korrekten Tile-IDs"""
        try:
            # Verwende den korrekten Pfad
            mapping_path = "data/tile_mapping.json"
            if os.path.exists(mapping_path):
                import json
                with open(mapping_path, 'r', encoding='utf-8') as f:
                    mapping_data = json.load(f)
                
                if mapping_data and "tile_mapping" in mapping_data:
                    # Erstelle eine Mapping-Tabelle mit Sprite-Namen
                    self.tile_mapping = {}
                    for mapping_id, tile_info in mapping_data["tile_mapping"].items():
                        # Verwende den Namen als Sprite-Dateiname
                        sprite_name = f"{tile_info['name'].lower().replace('-', '_').replace(' ', '_')}.png"
                        self.tile_mapping[int(mapping_id)] = {
                            "sprite_name": sprite_name,
                            "name": tile_info["name"],
                            "category": tile_info.get("category", "unknown")
                        }
                    
                    print(f"Tile-Mapping geladen: {len(self.tile_mapping)} Tiles")
                else:
                    print("Kein Tile-Mapping gefunden, verwende sequenzielle IDs")
                    self.tile_mapping = {}
            else:
                print(f"Tile-Mapping Datei nicht gefunden: {mapping_path}")
                self.tile_mapping = {}
                
        except Exception as e:
            print(f"Fehler beim Laden des Tile-Mappings: {e}")
            self.tile_mapping = {}


# Globale Tileset-Manager-Instanz
tileset_manager = TilesetManager()


# Global tile size constant
TILE_SIZE = 64  # Sprites sind 64x64 Pixel


class TileType(IntEnum):
    """Common tile type IDs for collision and interaction."""
    EMPTY = 0
    SOLID = 1
    GRASS = 2
    WATER = 3
    WARP = 4
    TRIGGER = 5
    SIGN = 6
    DOOR = 7
    STAIRS = 8
    LEDGE_DOWN = 9
    LEDGE_LEFT = 10
    LEDGE_RIGHT = 11
    LEDGE_UP = 12


class TileLayer(IntEnum):
    """Layer indices for map rendering."""
    GROUND = 0
    DECOR = 1
    COLLISION = 2
    OVERHANG = 3
    OBJECTS = 4


def world_to_tile(x: float, y: float) -> Tuple[int, int]:
    """
    Convert world coordinates to tile coordinates.
    
    Args:
        x: World X position in pixels
        y: World Y position in pixels
        
    Returns:
        Tuple of (tile_x, tile_y)
    """
    return (int(x // TILE_SIZE), int(y // TILE_SIZE))


def tile_to_world(tile_x: int, tile_y: int) -> Tuple[float, float]:
    """
    Convert tile coordinates to world coordinates (top-left corner).
    
    Args:
        tile_x: Tile X coordinate
        tile_y: Tile Y coordinate
        
    Returns:
        Tuple of (world_x, world_y) for the tile's top-left corner
    """
    return (tile_x * TILE_SIZE, tile_y * TILE_SIZE)


def tile_center_to_world(tile_x: int, tile_y: int) -> Tuple[float, float]:
    """
    Convert tile coordinates to world coordinates (center of tile).
    
    Args:
        tile_x: Tile X coordinate
        tile_y: Tile Y coordinate
        
    Returns:
        Tuple of (world_x, world_y) for the tile's center
    """
    return (tile_x * TILE_SIZE + TILE_SIZE // 2, 
            tile_y * TILE_SIZE + TILE_SIZE // 2)


def rect_to_tiles(rect: pygame.Rect) -> List[Tuple[int, int]]:
    """
    Get all tile coordinates that a rectangle overlaps.
    
    Args:
        rect: Rectangle in world coordinates
        
    Returns:
        List of (tile_x, tile_y) tuples
    """
    min_x, min_y = world_to_tile(rect.left, rect.top)
    max_x, max_y = world_to_tile(rect.right - 1, rect.bottom - 1)
    
    tiles = []
    for ty in range(min_y, max_y + 1):
        for tx in range(min_x, max_x + 1):
            tiles.append((tx, ty))
    return tiles


def get_tile_rect(tile_x: int, tile_y: int) -> pygame.Rect:
    """
    Get the world-space rectangle for a tile.
    
    Args:
        tile_x: Tile X coordinate
        tile_y: Tile Y coordinate
        
    Returns:
        pygame.Rect in world coordinates
    """
    x, y = tile_to_world(tile_x, tile_y)
    return pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)


def is_tile_solid(collision_layer: List[List[int]], 
                  tile_x: int, tile_y: int,
                  width: int, height: int) -> bool:
    """
    Check if a tile is solid (blocks movement).
    
    Args:
        collision_layer: 2D array of collision values
        tile_x: Tile X coordinate to check
        tile_y: Tile Y coordinate to check
        width: Map width in tiles
        height: Map height in tiles
        
    Returns:
        True if the tile is solid or out of bounds
    """
    # Out of bounds is considered solid
    if tile_x < 0 or tile_x >= width or tile_y < 0 or tile_y >= height:
        return True
    
    # Check collision value
    return collision_layer[tile_y][tile_x] == TileType.SOLID


def is_rect_colliding(rect: pygame.Rect, 
                      collision_layer: List[List[int]],
                      width: int, height: int) -> bool:
    """
    Check if a rectangle collides with any solid tiles.
    
    Args:
        rect: Rectangle in world coordinates
        collision_layer: 2D array of collision values
        width: Map width in tiles
        height: Map height in tiles
        
    Returns:
        True if the rectangle overlaps any solid tiles
    """
    tiles = rect_to_tiles(rect)
    for tile_x, tile_y in tiles:
        if is_tile_solid(collision_layer, tile_x, tile_y, width, height):
            return True
    return False


def get_neighboring_tiles(tile_x: int, tile_y: int, 
                         include_diagonals: bool = False) -> List[Tuple[int, int]]:
    """
    Get the coordinates of neighboring tiles.
    
    Args:
        tile_x: Center tile X coordinate
        tile_y: Center tile Y coordinate
        include_diagonals: Whether to include diagonal neighbors
        
    Returns:
        List of (tile_x, tile_y) tuples for neighbors
    """
    neighbors = [
        (tile_x, tile_y - 1),  # North
        (tile_x + 1, tile_y),  # East
        (tile_x, tile_y + 1),  # South
        (tile_x - 1, tile_y),  # West
    ]
    
    if include_diagonals:
        neighbors.extend([
            (tile_x - 1, tile_y - 1),  # Northwest
            (tile_x + 1, tile_y - 1),  # Northeast
            (tile_x + 1, tile_y + 1),  # Southeast
            (tile_x - 1, tile_y + 1),  # Southwest
        ])
    
    return neighbors


def draw_grid(surface: pygame.Surface, 
              camera_x: float, camera_y: float,
              color: Tuple[int, int, int, int] = (255, 255, 255, 64)) -> None:
    """
    Draw a tile grid overlay on the surface.
    
    Args:
        surface: Surface to draw on
        camera_x: Camera X offset
        camera_y: Camera Y offset
        color: RGBA color for grid lines
    """
    width = surface.get_width()
    height = surface.get_height()
    
    # Calculate visible tile range
    start_x = int(camera_x // TILE_SIZE) * TILE_SIZE
    start_y = int(camera_y // TILE_SIZE) * TILE_SIZE
    
    # Draw vertical lines
    x = start_x - camera_x
    while x < width:
        pygame.draw.line(surface, color, (x, 0), (x, height), 1)
        x += TILE_SIZE
    
    # Draw horizontal lines
    y = start_y - camera_y
    while y < height:
        pygame.draw.line(surface, color, (0, y), (width, y), 1)
        y += TILE_SIZE


def draw_tile_highlight(surface: pygame.Surface,
                       tile_x: int, tile_y: int,
                       camera_x: float, camera_y: float,
                       color: Tuple[int, int, int, int] = (255, 255, 0, 128),
                       border_width: int = 2) -> None:
    """
    Draw a highlight around a specific tile.
    
    Args:
        surface: Surface to draw on
        tile_x: Tile X coordinate
        tile_y: Tile Y coordinate
        camera_x: Camera X offset
        camera_y: Camera Y offset
        color: RGBA color for highlight
        border_width: Width of the highlight border
    """
    x, y = tile_to_world(tile_x, tile_y)
    rect = pygame.Rect(x - camera_x, y - camera_y, TILE_SIZE, TILE_SIZE)
    
    # Draw filled rect with alpha
    s = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
    s.fill(color)
    surface.blit(s, rect.topleft)
    
    # Draw border
    if border_width > 0:
        pygame.draw.rect(surface, color[:3], rect, border_width)


class AutotileHelper:
    """
    Helper class for autotiling calculations.
    Determines which tile variant to use based on neighboring tiles.
    """
    
    # Bitmask values for neighbors (4-bit for cardinal directions)
    NORTH = 1
    EAST = 2
    SOUTH = 4
    WEST = 8
    
    @classmethod
    def calculate_bitmask(cls, collision_layer: List[List[int]],
                         tile_x: int, tile_y: int,
                         width: int, height: int,
                         match_value: int) -> int:
        """
        Calculate autotile bitmask for a tile based on matching neighbors.
        
        Args:
            collision_layer: 2D array to check
            tile_x: Tile X coordinate
            tile_y: Tile Y coordinate
            width: Map width in tiles
            height: Map height in tiles
            match_value: Value to match for connectivity
            
        Returns:
            4-bit bitmask value (0-15)
        """
        mask = 0
        
        # Check north
        if tile_y > 0 and collision_layer[tile_y - 1][tile_x] == match_value:
            mask |= cls.NORTH
        
        # Check east
        if tile_x < width - 1 and collision_layer[tile_y][tile_x + 1] == match_value:
            mask |= cls.EAST
        
        # Check south
        if tile_y < height - 1 and collision_layer[tile_y + 1][tile_x] == match_value:
            mask |= cls.SOUTH
        
        # Check west
        if tile_x > 0 and collision_layer[tile_y][tile_x - 1] == match_value:
            mask |= cls.WEST
        
        return mask
    
    @classmethod
    def calculate_bitmask_8bit(cls, collision_layer: List[List[int]],
                              tile_x: int, tile_y: int,
                              width: int, height: int,
                              match_value: int) -> int:
        """
        Calculate 8-bit autotile bitmask including diagonal neighbors.
        
        Args:
            collision_layer: 2D array to check
            tile_x: Tile X coordinate
            tile_y: Tile Y coordinate
            width: Map width in tiles
            height: Map height in tiles
            match_value: Value to match for connectivity
            
        Returns:
            8-bit bitmask value (0-255)
        """
        mask = 0
        
        # Cardinal directions (bits 0-3)
        if tile_y > 0 and collision_layer[tile_y - 1][tile_x] == match_value:
            mask |= 1  # North
        if tile_x < width - 1 and collision_layer[tile_y][tile_x + 1] == match_value:
            mask |= 2  # East
        if tile_y < height - 1 and collision_layer[tile_y + 1][tile_x] == match_value:
            mask |= 4  # South
        if tile_x > 0 and collision_layer[tile_y][tile_x - 1] == match_value:
            mask |= 8  # West
        
        # Diagonal directions (bits 4-7)
        if tile_x > 0 and tile_y > 0 and collision_layer[tile_y - 1][tile_x - 1] == match_value:
            mask |= 16  # Northwest
        if tile_x < width - 1 and tile_y > 0 and collision_layer[tile_y - 1][tile_x + 1] == match_value:
            mask |= 32  # Northeast
        if tile_x < width - 1 and tile_y < height - 1 and collision_layer[tile_y + 1][tile_x + 1] == match_value:
            mask |= 64  # Southeast
        if tile_x > 0 and tile_y < height - 1 and collision_layer[tile_y + 1][tile_x - 1] == match_value:
            mask |= 128  # Southwest
        
        return mask


def get_tile_terrain_type(tile_id: int) -> str:
    """
    Get the terrain type for encounter purposes.
    
    Args:
        tile_id: The tile ID or type
        
    Returns:
        Terrain type string ('grass', 'water', 'cave', etc.)
    """
    # Map tile types to terrain categories
    if tile_id == TileType.GRASS:
        return "grass"
    elif tile_id == TileType.WATER:
        return "water"
    elif tile_id in [TileType.STAIRS, TileType.DOOR]:
        return "indoor"
    else:
        return "normal"