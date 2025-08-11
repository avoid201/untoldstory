"""
Sprite Manager für Untold Story
Lädt und verwaltet alle Sprites aus dem sprites/ Ordner
"""

import pygame
import os
import json
from pathlib import Path
from typing import Dict, Optional, Any, List
from dataclasses import dataclass

@dataclass
class TileInfo:
    """Informationen über eine Tile"""
    name: str
    tileset_id: int
    sprite_file: str
    description: str
    category: str

class SpriteManager:
    """Verwaltet alle Sprites und Tiles für das Spiel"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, resources=None):
        # Verhindere mehrfache Initialisierung
        if self._initialized:
            return
            
        self.sprite_cache: Dict[str, pygame.Surface] = {}
        self.tile_mappings: Dict[str, TileInfo] = {}
        self.monster_sprites: Dict[str, pygame.Surface] = {}
        self.npc_sprites: Dict[str, pygame.Surface] = {}
        self.resources = resources
        
        # Tile-Größe (64x64 Pixel)
        self.tile_size = 64
        
        # Basis-Pfad zum Projekt
        self.base_path = Path(__file__).resolve().parent.parent.parent
        self.sprites_path = self.base_path / "sprites"
        self.data_path = self.base_path / "data"
        
        # Lade alle Sprites nur einmal
        self.load_all_sprites()
        self._initialized = True
    
    def load_missing_sprites_for_maps(self) -> None:
        """Lädt fehlende Sprites für Maps - wird automatisch durch andere Methoden abgedeckt"""
        print("🔍 Prüfe fehlende Sprites für Maps...")
        
        # Diese Methode ist jetzt redundant, da alle Sprites bereits geladen werden
        # Aber wir können sie für Debug-Zwecke behalten
        missing_sprites = []
        
        # Prüfe alle Tile-IDs, die in den Maps verwendet werden
        map_tile_ids = {
            # Player House
            "1", "5", "7", "9", "10",
            # Kohlenstadt  
            "2", "4",
            # Constructed Sprites
            "21", "22", "23", "24", "25", "26", "27", "28", "29", "30", "31", "32",
            "33", "34", "35", "36", "37", "38"
        }
        
        for tile_id in map_tile_ids:
            if tile_id not in self.sprite_cache:
                missing_sprites.append(tile_id)
        
        if missing_sprites:
            print(f"⚠️  Fehlende Sprites für Tile-IDs: {missing_sprites}")
            # Erstelle Platzhalter für fehlende Sprites
            for tile_id in missing_sprites:
                placeholder = self._create_placeholder_sprite(tile_id)
                if placeholder:
                    self.sprite_cache[tile_id] = placeholder
                    print(f"⚠️  Platzhalter erstellt für fehlende Tile ID: {tile_id}")
        else:
            print("✅ Alle benötigten Sprites sind geladen")
    
    def _show_similar_files(self, base_name: str) -> None:
        """Zeigt ähnliche verfügbare Dateien an, um bei der Fehlersuche zu helfen"""
        print(f"   🔍 Suche nach ähnlichen Dateien für: {base_name}")
        
        # Suche im Hauptsprites-Ordner
        main_files = []
        for file_path in self.sprites_path.glob("*.png"):
            if base_name.lower().replace("_large", "").replace("-", "") in file_path.name.lower().replace("_large", "").replace("-", ""):
                main_files.append(file_path.name)
        
        # Suche im Constructed-Ordner
        constructed_files = []
        constructed_path = self.sprites_path / "Constructed"
        if constructed_path.exists():
            for file_path in constructed_path.glob("*.png"):
                if base_name.lower().replace("_large", "").replace("-", "") in file_path.name.lower().replace("_large", "").replace("-", ""):
                    constructed_files.append(file_path.name)
        
        if main_files:
            print(f"   📁 Hauptordner - Ähnliche Dateien: {main_files[:5]}")
        if constructed_files:
            print(f"   🏠 Constructed - Ähnliche Dateien: {constructed_files[:5]}")
        
        if not main_files and not constructed_files:
            print(f"   ❌ Keine ähnlichen Dateien gefunden")
    
    def load_all_sprites(self) -> None:
        """Lädt alle verfügbaren Sprites"""
        print("🔄 Lade alle Sprites...")
        
        # Lade Tile-Mappings
        self.load_tile_mappings()
        
        # Lade Basis-Tiles (Gras, Wege, Böden) - NEUE METHODE
        self.load_base_tiles()
        
        # Lade Constructed-Sprites
        self.load_constructed_sprites()
        
        # Lade alle Sprites basierend auf dem Tile-Mapping
        self.load_all_tile_sprites()
        
        # Lade fehlende Sprites für Maps
        self.load_missing_sprites_for_maps()
        
        # Lade Monster-Sprites
        self.load_monster_sprites()
        
        # Lade NPC-Sprites
        self.load_npc_sprites()
        
        # Lade Player-Sprite
        self.load_player_sprite()
        
        print(f"✅ Alle Sprites geladen: {len(self.sprite_cache)} Sprites im Cache")
        print(f"🎮 Player-Sprite Status: {'Geladen' if 'player' in self.sprite_cache else 'FEHLT!'}")
    
    def load_tile_mappings(self) -> None:
        """Lädt das Tile-Mapping aus der JSON-Datei"""
        mapping_path = self.data_path / "tile_mapping.json"
        if not mapping_path.exists():
            print("⚠️  Tile-Mapping-Datei nicht gefunden")
            return
            
        try:
            with open(mapping_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Das Tile-Mapping ist direkt im Hauptobjekt
            tile_mapping_data = data.get("tile_mappings", {})
            
            # Erstelle TileInfo-Objekte für jedes Mapping
            for tile_id_str, tile_data in tile_mapping_data.items():
                try:
                    tile_info = TileInfo(
                        name=tile_data.get("name", f"Tile_{tile_id_str}"),
                        tileset_id=tile_data.get("tileset_id", int(tile_id_str)),
                        sprite_file=tile_data.get("sprite_file", ""),
                        description=tile_data.get("description", ""),
                        category=tile_data.get("category", "unknown")
                    )
                    self.tile_mappings[tile_id_str] = tile_info
                except Exception as e:
                    print(f"⚠️  Fehler beim Parsen von Tile {tile_id_str}: {e}")
                    
            print(f"✅ {len(self.tile_mappings)} Tile-Mappings geladen")
            
        except Exception as e:
            print(f"❌ Fehler beim Laden des Tile-Mappings: {e}")
            self.tile_mappings = {}
    
    def load_all_tile_sprites(self) -> None:
        """Lädt alle Tile-Sprites basierend auf dem Tile-Mapping"""
        print("🔧 Lade alle Tile-Sprites...")
        
        if not self.tile_mappings:
            print("⚠️  Keine Tile-Mappings verfügbar")
            return
        
        loaded_count = 0
        missing_count = 0
        
        for tile_id_str, tile_info in self.tile_mappings.items():
            if not tile_info.sprite_file:
                continue
                
            # Versuche den Sprite zu laden
            sprite = self._load_sprite_safely(self.sprites_path / tile_info.sprite_file)
            
            if sprite:
                # Cache den Sprite unter verschiedenen Schlüsseln
                self.sprite_cache[tile_id_str] = sprite
                self.sprite_cache[tile_info.sprite_file] = sprite
                
                # Cache auch unter dem Dateinamen ohne Erweiterung
                sprite_name = Path(tile_info.sprite_file).stem
                self.sprite_cache[sprite_name] = sprite
                
                loaded_count += 1
                print(f"✅ Tile {tile_id_str} geladen: {tile_info.sprite_file}")
            else:
                missing_count += 1
                print(f"⚠️  Tile {tile_id_str} fehlt: {tile_info.sprite_file}")
        
        print(f"📊 Tile-Sprites geladen: {loaded_count}, fehlend: {missing_count}")
        
        # Erstelle Platzhalter für fehlende Tiles
        if missing_count > 0:
            print("🔧 Erstelle Platzhalter für fehlende Tiles...")
            for tile_id_str, tile_info in self.tile_mappings.items():
                if tile_id_str not in self.sprite_cache:
                    placeholder = self._create_placeholder_sprite(tile_id_str)
                    if placeholder:
                        self.sprite_cache[tile_id_str] = placeholder
                        print(f"✅ Platzhalter für Tile {tile_id_str} erstellt")
    
    def _create_placeholder_sprite(self, tile_id: str) -> Optional[pygame.Surface]:
        """Erstellt einen Platzhalter-Sprite für fehlende Tiles"""
        try:
            # Erstelle eine 64x64 Oberfläche (korrekte Tile-Größe)
            placeholder = pygame.Surface((self.tile_size, self.tile_size))
            placeholder.fill((255, 0, 0))  # Rot
            
            # Zeichne einen schwarzen Rahmen
            pygame.draw.rect(placeholder, (0, 0, 0), 
                           (0, 0, self.tile_size, self.tile_size), 2)
            
            # Zeichne die Tile-ID als Text
            try:
                font = pygame.font.Font(None, 24)  # Größere Schrift
                text = font.render(str(tile_id), True, (255, 255, 255))
                text_rect = text.get_rect(center=(self.tile_size // 2, self.tile_size // 2))
                placeholder.blit(text, text_rect)
            except:
                # Fallback wenn Font nicht funktioniert
                pass
            
            return placeholder
        except Exception as e:
            print(f"❌ Fehler beim Erstellen des Platzhalters für Tile {tile_id}: {e}")
            return None

    def load_base_tiles(self) -> None:
        """Lädt Basis-Tiles (Gras, Wege, Böden) basierend auf dem tile_mapping.json"""
        print("🌱 Lade Basis-Tiles...")
        
        # Verwende das tile_mapping.json für konsistente Sprite-Namen
        base_tile_ids = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13"]
        
        for tile_id in base_tile_ids:
            tile_info = self.tile_mappings.get(tile_id)
            if tile_info and tile_info.sprite_file:
                # Versuche den Sprite zu laden
                sprite = self._find_sprite_by_name(tile_info.sprite_file)
                if sprite:
                    # Cache den Sprite unter der Tile-ID für schnellen Zugriff
                    self.sprite_cache[tile_id] = sprite
                    # Cache auch unter dem Dateinamen für Konsistenz
                    self.sprite_cache[tile_info.sprite_file] = sprite
                    print(f"✅ Basis-Tile geladen: {tile_info.sprite_file} (ID: {tile_id})")
                else:
                    print(f"⚠️  Basis-Tile nicht geladen: {tile_info.sprite_file} (ID: {tile_id})")
                    # Erstelle einen Platzhalter-Sprite
                    placeholder = self._create_placeholder_sprite(tile_id)
                    if placeholder:
                        self.sprite_cache[tile_id] = placeholder
                        print(f"⚠️  Platzhalter erstellt für Basis-Tile ID: {tile_id}")
            else:
                print(f"⚠️  Kein Tile-Mapping für ID {tile_id} gefunden")
        
        print(f"✅ {len([k for k in self.sprite_cache.keys() if k.isdigit() and int(k) < 21])} Basis-Tiles geladen")
    
    def load_constructed_sprites(self) -> None:
        """Lädt Constructed-Sprites (Möbel, Deko, etc.) basierend auf dem tile_mapping.json"""
        print("🏠 Lade Constructed-Sprites...")
        
        # Verwende das tile_mapping.json für alle IDs >= 21
        for tile_id_str, tile_info in self.tile_mappings.items():
            tile_id = int(tile_id_str)
            if tile_id >= 21 and tile_info.sprite_file:
                # Versuche den Sprite zu laden
                sprite = self._find_sprite_by_name(tile_info.sprite_file)
                if sprite:
                    # Cache den Sprite unter der Tile-ID für schnellen Zugriff
                    self.sprite_cache[tile_id_str] = sprite
                    # Cache auch unter dem Dateinamen für Konsistenz
                    self.sprite_cache[tile_info.sprite_file] = sprite
                    print(f"✅ Constructed-Sprite geladen: {tile_info.sprite_file} (ID: {tile_id_str})")
                else:
                    print(f"⚠️  Constructed-Sprite nicht geladen: {tile_info.sprite_file} (ID: {tile_id_str})")
                    # Erstelle einen Platzhalter-Sprite
                    placeholder = self._create_placeholder_sprite(tile_id_str)
                    if placeholder:
                        self.sprite_cache[tile_id_str] = placeholder
                        print(f"⚠️  Platzhalter erstellt für Constructed-Sprite ID: {tile_id_str}")
        
        print(f"✅ {len([k for k in self.sprite_cache.keys() if k.isdigit() and int(k) >= 21])} Constructed-Sprites geladen")
    

    
    def load_monster_sprites(self) -> None:
        """Lädt Monster-Sprites"""
        monsters_path = self.sprites_path / "monsters"
        if not monsters_path.exists():
            print("⚠️  Monsters-Ordner nicht gefunden")
            return
        
        # Lade alle PNG-Dateien im monsters-Ordner
        for file_name in os.listdir(monsters_path):
            if file_name.endswith(".png"):
                sprite_path = monsters_path / file_name
                sprite = self._load_sprite_safely(sprite_path)
                if sprite:
                    # Entferne .png für den Cache-Schlüssel
                    cache_name = file_name[:-4]
                    self.monster_sprites[cache_name] = sprite
                    # NICHT in den allgemeinen Cache laden - das führt zu Verwirrung mit Tiles
                    # self.sprite_cache[cache_name] = sprite
                else:
                    print(f"❌ Konnte Monster {file_name} nicht laden")
        
        print(f"🐉 Monster-Sprites geladen: {len(self.monster_sprites)} Sprites")
    
    def load_npc_sprites(self) -> None:
        """Lädt NPC-Sprites"""
        npcs_path = self.sprites_path / "npcs"
        if not npcs_path.exists():
            print("⚠️  NPCs-Ordner nicht gefunden")
            return
        
        # Lade alle PNG-Dateien im npcs-Ordner
        for file_name in os.listdir(npcs_path):
            if file_name.endswith(".png"):
                sprite_path = npcs_path / file_name
                sprite = self._load_sprite_safely(sprite_path)
                if sprite:
                    # Entferne .png für den Cache-Schlüssel
                    cache_name = file_name[:-4]
                    self.npc_sprites[cache_name] = sprite
                    # NICHT in den allgemeinen Cache laden - das führt zu Verwirrung mit Tiles
                    # self.sprite_cache[cache_name] = sprite
                else:
                    print(f"❌ Konnte NPC {file_name} nicht laden")
        
        print(f"👥 NPC-Sprites geladen: {len(self.npc_sprites)} Sprites")
    
    def load_player_sprite(self) -> None:
        """Lädt den Player-Sprite"""
        print("🎮 Lade Player-Sprite...")
        
        # Versuche verschiedene Pfade für den Player-Sprite
        player_paths = [
            self.sprites_path / "player.png",
            self.sprites_path / "player_large.png",
            Path("sprites/player.png"),
            Path("sprites/player_large.png")
        ]
        
        for player_path in player_paths:
            if player_path.exists():
                sprite = self._load_sprite_safely(player_path)
                if sprite:
                    # Cache den Sprite nur unter spezifischen Schlüsseln, NICHT im allgemeinen Cache
                    # Das verhindert, dass der Player als Tile behandelt wird
                    self.sprite_cache["player"] = sprite
                    self.sprite_cache["player_sprite"] = sprite
                    print(f"✅ Player-Sprite geladen von: {player_path}")
                    print(f"   Sprite-Größe: {sprite.get_size()}")
                    return
                else:
                    print(f"⚠️  Player-Sprite konnte nicht geladen werden von: {player_path}")
            else:
                print(f"⚠️  Player-Sprite nicht gefunden unter: {player_path}")
        
        # Fallback: Erstelle einen Platzhalter-Sprite
        print("⚠️  Erstelle Platzhalter für Player-Sprite")
        placeholder = self._create_placeholder_sprite("player")
        if placeholder:
            self.sprite_cache["player"] = placeholder
            self.sprite_cache["player_sprite"] = placeholder
            print("⚠️  Platzhalter für Player-Sprite erstellt")
        else:
            print("❌ Konnte keinen Player-Sprite laden!")
    
    def get_tile_sprite(self, tile_id: int) -> Optional[pygame.Surface]:
        """Gibt den Sprite für eine Tile-ID zurück"""
        tile_id_str = str(tile_id)
        
        # Direkter Zugriff auf den Cache mit der Tile-ID
        if tile_id_str in self.sprite_cache:
            return self.sprite_cache[tile_id_str]
        
        # Fallback: Suche nach dem Sprite-Dateinamen aus dem Tile-Mapping
        tile_info = self.tile_mappings.get(tile_id_str)
        if tile_info and tile_info.sprite_file:
            # Versuche den Sprite über den Dateinamen zu finden
            sprite = self.sprite_cache.get(tile_info.sprite_file)
            if sprite:
                # Cache den Sprite auch unter der Tile-ID für schnelleren Zugriff
                self.sprite_cache[tile_id_str] = sprite
                print(f"✅ Tile {tile_id} über Dateinamen gefunden: {tile_info.sprite_file}")
                return sprite
            
            # Fallback: Suche nach ähnlichen Dateinamen
            base_name = tile_info.sprite_file.replace("_large.png", "").replace(".png", "")
            for sprite_name, sprite_surface in self.sprite_cache.items():
                if base_name in sprite_name:
                    # Cache den Sprite unter der Tile-ID
                    self.sprite_cache[tile_id_str] = sprite_surface
                    print(f"✅ Tile {tile_id} über ähnlichen Namen gefunden: {sprite_name}")
                    return sprite_surface
        
        # Wenn nichts gefunden wurde, erstelle einen Platzhalter
        print(f"⚠️  Kein Sprite für Tile ID {tile_id} gefunden, erstelle Platzhalter")
        placeholder = self._create_placeholder_sprite(tile_id_str)
        if placeholder:
            self.sprite_cache[tile_id_str] = placeholder
            return placeholder
        
        return None
        
    def _is_sprite_for_tile_id(self, sprite_name: str, tile_id: int) -> bool:
        """Prüft, ob ein Sprite für eine bestimmte Tile-ID bestimmt ist"""
        tile_info = self.tile_mappings.get(str(tile_id))
        if tile_info and tile_info.sprite_file:
            return tile_info.sprite_file == sprite_name
        return False
        

    
    def get_tile_info(self, tile_id: int) -> Optional[TileInfo]:
        """Holt Informationen über eine Tile"""
        return self.tile_mappings.get(str(tile_id))
    
    def get_monster_sprite(self, monster_id: str) -> Optional[pygame.Surface]:
        """Holt das Sprite für ein Monster"""
        return self.monster_sprites.get(monster_id)
    
    def get_npc_sprite(self, npc_id: str) -> Optional[pygame.Surface]:
        """Holt das Sprite für einen NPC"""
        return self.npc_sprites.get(npc_id)
    
    def get_player_sprite(self) -> Optional[pygame.Surface]:
        """Gibt den Player-Sprite zurück"""
        # Versuche verschiedene Schlüssel für den Player-Sprite
        player_keys = ["player", "player_sprite", "player.png", "player_large.png"]
        
        for key in player_keys:
            if key in self.sprite_cache:
                sprite = self.sprite_cache[key]
                if sprite:
                    print(f"✅ Player-Sprite gefunden unter Schlüssel '{key}': {sprite.get_size()}")
                    return sprite
        
        # Wenn kein Player-Sprite gefunden wurde, versuche ihn neu zu laden
        print("⚠️  Player-Sprite nicht im Cache gefunden, versuche neu zu laden...")
        self.load_player_sprite()
        
        # Versuche es nochmal nach dem Neuladen
        for key in player_keys:
            if key in self.sprite_cache:
                sprite = self.sprite_cache[key]
                if sprite:
                    print(f"✅ Player-Sprite nach Neuladen gefunden: {sprite.get_size()}")
                    return sprite
        
        print("❌ Player-Sprite konnte nicht geladen werden")
        return None
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Gibt Informationen über den Cache-Status zurück"""
        return {
            "total_sprites": len(self.sprite_cache),
            "tile_mappings": len(self.tile_mappings),
            "monster_sprites": len(self.monster_sprites),
            "npc_sprites": len(self.npc_sprites),
            "sprite_names": list(self.sprite_cache.keys())[:10],
            "tile_ids": list(self.tile_mappings.keys())[:10]
        }
    
    def get_sprite_by_name(self, sprite_name: str) -> Optional[pygame.Surface]:
        """Holt ein Sprite anhand des Namens"""
        return self.sprite_cache.get(sprite_name)
    
    def is_sprite_loaded(self, sprite_name: str) -> bool:
        """Prüft, ob ein Sprite geladen ist"""
        return sprite_name in self.sprite_cache
    
    def reload_sprites(self) -> None:
        """Lädt alle Sprites neu"""
        print("🔄 Lade alle Sprites neu...")
        self.sprite_cache.clear()
        self.monster_sprites.clear()
        self.npc_sprites.clear()
        self.load_all_sprites()

    def _load_sprite_safely(self, sprite_path: Path) -> Optional[pygame.Surface]:
        """Lädt einen Sprite sicher, auch ohne initialisierten pygame.display"""
        try:
            # Versuche zuerst mit convert_alpha()
            sprite = pygame.image.load(str(sprite_path)).convert_alpha()
            return sprite
        except pygame.error as e:
            if "convert" in str(e).lower():
                try:
                    # Fallback: Lade ohne convert_alpha()
                    sprite = pygame.image.load(str(sprite_path))
                    return sprite
                except pygame.error as e2:
                    print(f"❌ Konnte {sprite_path.name} nicht laden: {e2}")
                    return None
            else:
                print(f"❌ Fehler beim Laden von {sprite_path.name}: {e}")
                return None
        except Exception as e:
            print(f"❌ Unerwarteter Fehler beim Laden von {sprite_path.name}: {e}")
            return None

    def _find_sprite_by_name(self, sprite_name: str) -> Optional[pygame.Surface]:
        """Sucht nach einem Sprite mit dem angegebenen Namen in verschiedenen Ordnern"""
        # 1. Suche im Hauptsprites-Ordner
        sprite_path = self.sprites_path / sprite_name
        if sprite_path.exists():
            return self._load_sprite_safely(sprite_path)
            
        # 2. Suche im Constructed-Ordner
        constructed_path = self.sprites_path / "Constructed" / sprite_name
        if constructed_path.exists():
            return self._load_sprite_safely(constructed_path)
            
        # 3. Suche nach _large Variante (wenn normale Datei nicht gefunden wurde)
        if not sprite_name.endswith("_large.png"):
            large_name = sprite_name.replace(".png", "_large.png")
            large_path = self.sprites_path / large_name
            if large_path.exists():
                return self._load_sprite_safely(large_path)
                
            large_constructed_path = self.sprites_path / "Constructed" / large_name
            if large_constructed_path.exists():
                return self._load_sprite_safely(large_constructed_path)
                
        # 4. Suche nach normaler Variante (wenn _large Datei nicht gefunden wurde)
        elif sprite_name.endswith("_large.png"):
            normal_name = sprite_name.replace("_large.png", ".png")
            normal_path = self.sprites_path / normal_name
            if normal_path.exists():
                return self._load_sprite_safely(normal_path)
                
            normal_constructed_path = self.sprites_path / "Constructed" / normal_name
            if normal_constructed_path.exists():
                return self._load_sprite_safely(normal_constructed_path)
                
        return None
