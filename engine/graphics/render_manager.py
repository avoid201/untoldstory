"""
Render Manager für Untold Story
Koordinierte Rendering-Operationen mit korrekter Z-Order-Behandlung
"""

import pygame
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from ..world.area import Area
from ..world.entity import Entity
from ..world.camera import Camera
from .tile_renderer import TileRenderer
from .sprite_manager import SpriteManager

@dataclass
class RenderLayer:
    """Repräsentiert eine Rendering-Ebene mit Z-Index."""
    name: str
    z_index: int
    visible: bool = True
    entities: List[Entity] = None
    
    def __post_init__(self):
        if self.entities is None:
            self.entities = []

class RenderManager:
    """Verwaltet alle Rendering-Operationen mit korrekter Z-Order-Behandlung."""
    
    def __init__(self):
        self.layers: Dict[str, RenderLayer] = {}
        self._setup_default_layers()
        self.debug_mode = False
        
        # Initialisiere SpriteManager und TileRenderer
        self.sprite_manager = SpriteManager()
        self.tile_renderer = TileRenderer(self.sprite_manager)
        
        # Debug-Modus für TileRenderer aktivieren
        if self.debug_mode:
            self.tile_renderer.set_debug_mode(True)
        
        # Debug-Modus für SpriteManager aktivieren
        print(f"SpriteManager initialisiert: {len(self.sprite_manager.sprite_cache)} Sprites geladen")
    
    def _setup_default_layers(self):
        """Richtet die Standard-Rendering-Layer ein."""
        self.add_layer("background", 0)      # Hintergrund
        self.add_layer("ground", 100)        # Boden
        self.add_layer("decor", 200)         # Dekoration
        self.add_layer("furniture", 300)     # Möbel
        self.add_layer("entities", 400)      # Spieler, NPCs
        self.add_layer("overhang", 500)      # Überhang (Bäume, etc.)
        self.add_layer("decoration", 600)    # Dekoration
        self.add_layer("ui", 1000)           # UI-Elemente
        self.add_layer("dialogue", 1100)     # Dialog-Boxen
    
    def add_layer(self, name: str, z_index: int) -> None:
        """Fügt einen neuen Rendering-Layer hinzu."""
        self.layers[name] = RenderLayer(name, z_index)
    
    def add_entity_to_layer(self, entity: Entity, layer_name: str) -> None:
        """Fügt eine Entity zu einem spezifischen Layer hinzu."""
        if layer_name in self.layers:
            self.layers[layer_name].entities.append(entity)
    
    def remove_entity_from_layer(self, entity: Entity, layer_name: str) -> None:
        """Entfernt eine Entity aus einem Layer."""
        if layer_name in self.layers:
            if entity in self.layers[layer_name].entities:
                self.layers[layer_name].entities.remove(entity)
    
    def render_scene(self, surface: pygame.Surface, area: Area, 
                    camera: Camera, ui_elements: List[Any] = None) -> None:
        """Rendert die komplette Szene mit korrekter Z-Order-Behandlung."""
        if not area:
            return
        
        # Lösche alle Entity-Layer
        for layer in self.layers.values():
            if layer.name in ["entities", "overhang"]:
                layer.entities.clear()
        
        # Sammle alle Entities aus der Area
        if hasattr(area, 'entities'):
            for entity in area.entities:
                if entity.visible:
                    self.add_entity_to_layer(entity, "entities")
        
        # Füge Spieler hinzu falls vorhanden
        if hasattr(self, 'player') and self.player:
            self.add_entity_to_layer(self.player, "entities")
        
        # Rendere alle Layer in Z-Order
        sorted_layers = sorted(self.layers.values(), key=lambda l: l.z_index)
        
        for layer in sorted_layers:
            if not layer.visible:
                continue
            
            if layer.name == "background":
                self._render_background(surface, area, camera)
            elif layer.name == "ground":
                self._render_ground_layer(surface, area, camera)
            elif layer.name == "decor":
                self._render_decor_layer(surface, area, camera)
            elif layer.name == "furniture":
                self._render_furniture_layer(surface, area, camera)
            elif layer.name == "entities":
                self._render_entities_layer(surface, layer, camera)
            elif layer.name == "overhang":
                self._render_overhang_layer(surface, area, camera)
            elif layer.name == "decoration":
                self._render_decoration_layer(surface, area, camera)
            elif layer.name == "ui" and ui_elements:
                self._render_ui_elements(surface, ui_elements)
    
    def _render_background(self, surface: pygame.Surface, area: Area, camera: Camera) -> None:
        """Rendert den Hintergrund."""
        # Fülle mit Hintergrundfarbe
        surface.fill((20, 20, 30))
    
    def _render_ground_layer(self, surface: pygame.Surface, area: Area, camera: Camera) -> None:
        """Rendert den Boden-Layer."""
        if "ground" in area.layers:
            self._render_tile_layer(surface, area.layers["ground"], camera, "ground")
    
    def _render_decor_layer(self, surface: pygame.Surface, area: Area, camera: Camera) -> None:
        """Rendert den Dekorations-Layer."""
        if "decor" in area.layers:
            self._render_tile_layer(surface, area.layers["decor"], camera, "decor")
    
    def _render_furniture_layer(self, surface: pygame.Surface, area: Area, camera: Camera) -> None:
        """Rendert den Möbel-Layer."""
        if "furniture" in area.layers:
            self._render_tile_layer(surface, area.layers["furniture"], camera, "furniture")
    
    def _render_overhang_layer(self, surface: pygame.Surface, area: Area, camera: Camera) -> None:
        """Rendert den Überhang-Layer."""
        if "overhang" in area.layers:
            self._render_tile_layer(surface, area.layers["overhang"], camera, "overhang")
    
    def _render_decoration_layer(self, surface: pygame.Surface, area: Area, camera: Camera) -> None:
        """Rendert den Dekorations-Layer."""
        if "decoration" in area.layers:
            self._render_tile_layer(surface, area.layers["decoration"], camera, "decoration")
    
    def _render_tile_layer(self, surface: pygame.Surface, layer_data: List[List[int]], 
                          camera: Camera, layer_name: str) -> None:
        """Rendert einen Tile-Layer mit dem neuen TileRenderer."""
        if not layer_data:
            return
        
        # Verwende den neuen TileRenderer
        camera_offset = (int(camera.x), int(camera.y))
        self.tile_renderer.render_layer(surface, layer_data, camera_offset, layer_name)
    
    def _render_entities_layer(self, surface: pygame.Surface, layer: RenderLayer, camera: Camera) -> None:
        """Rendert alle Entities in einem Layer mit Tiefensortierung."""
        # Sortiere Entities nach Y-Position für korrekte Tiefensortierung
        sorted_entities = sorted(layer.entities, key=lambda e: e.y if hasattr(e, 'y') else 0)
        
        for entity in sorted(layer.entities):
            if entity and entity.visible and hasattr(entity, 'draw'):
                # Zeichne Entity mit korrigierter Kamera-Position
                entity.draw(surface, (camera.x, camera.y))
    
    def _render_ui_elements(self, surface: pygame.Surface, ui_elements: List[Any]) -> None:
        """Rendert UI-Elemente."""
        for ui_element in ui_elements:
            if hasattr(ui_element, 'draw'):
                ui_element.draw(surface)
    
    def set_debug_mode(self, enabled: bool) -> None:
        """Aktiviert/Deaktiviert den Debug-Modus."""
        self.debug_mode = enabled
        self.tile_renderer.set_debug_mode(enabled)
    
    def get_sprite_cache_info(self) -> Dict:
        """Gibt Informationen über den Sprite-Cache zurück."""
        return self.sprite_manager.get_cache_info()
