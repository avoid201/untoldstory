"""
Optimierter Renderer für Untold Story
Implementiert verbessertes Caching, Asset-Atlasierung und effizientes Font-Rendering
"""

import pygame
import weakref
from typing import Dict, List, Tuple, Optional, Any, Set
from dataclasses import dataclass
from pathlib import Path
import json
import hashlib
from engine.core.config import LOGICAL_WIDTH, LOGICAL_HEIGHT, TILE_SIZE


@dataclass
class CachedSurface:
    """Gecachte Oberfläche mit Metadaten."""
    surface: pygame.Surface
    last_used: float
    access_count: int
    size: Tuple[int, int]
    hash_key: str


@dataclass
class AtlasRegion:
    """Region in einem Texture-Atlas."""
    x: int
    y: int
    width: int
    height: int
    surface: pygame.Surface


class TextureAtlas:
    """Texture-Atlas für effizientes Rendering."""
    
    def __init__(self, max_size: int = 2048):
        self.max_size = max_size
        self.atlas_surface = pygame.Surface((max_size, max_size), pygame.SRCALPHA)
        self.regions: Dict[str, AtlasRegion] = {}
        self.next_x = 0
        self.next_y = 0
        self.row_height = 0
        self.used_space = 0
        
    def add_texture(self, key: str, surface: pygame.Surface) -> bool:
        """Fügt eine Textur zum Atlas hinzu."""
        if key in self.regions:
            return True  # Bereits vorhanden
        
        width, height = surface.get_size()
        
        # Neue Zeile beginnen wenn nötig
        if self.next_x + width > self.max_size:
            self.next_x = 0
            self.next_y += self.row_height
            self.row_height = 0
        
        # Prüfen ob Atlas voll ist
        if self.next_y + height > self.max_size:
            return False  # Atlas voll
        
        # Textur zum Atlas hinzufügen
        self.atlas_surface.blit(surface, (self.next_x, self.next_y))
        
        region = AtlasRegion(
            x=self.next_x,
            y=self.next_y,
            width=width,
            height=height,
            surface=surface
        )
        self.regions[key] = region
        
        # Position für nächste Textur aktualisieren
        self.next_x += width
        self.row_height = max(self.row_height, height)
        self.used_space += width * height
        
        return True
    
    def get_region(self, key: str) -> Optional[AtlasRegion]:
        """Gibt eine Atlas-Region zurück."""
        return self.regions.get(key)
    
    def get_atlas_surface(self) -> pygame.Surface:
        """Gibt die Atlas-Oberfläche zurück."""
        return self.atlas_surface
    
    def get_usage_percentage(self) -> float:
        """Gibt den Nutzungsgrad des Atlas zurück."""
        return (self.used_space / (self.max_size * self.max_size)) * 100


class FontCache:
    """Cache für gerenderte Font-Texturen."""
    
    def __init__(self):
        self.cached_texts: Dict[str, CachedSurface] = {}
        self.font_cache: Dict[Tuple[str, int], pygame.font.Font] = {}
        self.max_cache_size = 1000
        self.current_time = 0.0
        
    def get_font(self, font_name: str, size: int) -> pygame.font.Font:
        """Gibt eine Font zurück (gecacht)."""
        key = (font_name, size)
        if key not in self.font_cache:
            try:
                if font_name == "None":
                    self.font_cache[key] = pygame.font.Font(None, size)
                else:
                    self.font_cache[key] = pygame.font.Font(font_name, size)
            except:
                # Fallback auf Standard-Font
                self.font_cache[key] = pygame.font.Font(None, size)
        
        return self.font_cache[key]
    
    def render_text(self, text: str, font_name: str, size: int, 
                   color: Tuple[int, int, int], 
                   antialias: bool = True) -> pygame.Surface:
        """Rendert Text mit Caching."""
        # Cache-Key erstellen
        cache_key = f"{text}_{font_name}_{size}_{color}_{antialias}"
        
        if cache_key in self.cached_texts:
            cached = self.cached_texts[cache_key]
            cached.last_used = self.current_time
            cached.access_count += 1
            return cached.surface
        
        # Text rendern
        font = self.get_font(font_name, size)
        surface = font.render(text, antialias, color)
        
        # Zum Cache hinzufügen
        cached_surface = CachedSurface(
            surface=surface,
            last_used=self.current_time,
            access_count=1,
            size=surface.get_size(),
            hash_key=cache_key
        )
        
        self.cached_texts[cache_key] = cached_surface
        
        # Cache-Größe begrenzen
        self._cleanup_cache()
        
        return surface
    
    def _cleanup_cache(self) -> None:
        """Bereinigt den Cache wenn er zu groß wird."""
        if len(self.cached_texts) <= self.max_cache_size:
            return
        
        # Sortiere nach Nutzung (selten genutzte zuerst)
        sorted_items = sorted(
            self.cached_texts.items(),
            key=lambda x: (x[1].access_count, x[1].last_used)
        )
        
        # Entferne die Hälfte der selten genutzten Einträge
        items_to_remove = len(sorted_items) // 2
        for i in range(items_to_remove):
            del self.cached_texts[sorted_items[i][0]]
    
    def update(self, dt: float) -> None:
        """Aktualisiert den Cache."""
        self.current_time += dt


class OptimizedRenderer:
    """Optimierter Renderer mit verbesserten Performance-Features."""
    
    def __init__(self):
        self.texture_atlas = TextureAtlas()
        self.font_cache = FontCache()
        self.surface_cache: Dict[str, CachedSurface] = {}
        self.render_stats = {
            'frames_rendered': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'atlas_usage': 0.0
        }
        
        # Viewport-Culling
        self.viewport = pygame.Rect(0, 0, LOGICAL_WIDTH, LOGICAL_HEIGHT)
        self.culling_enabled = True
        
        # Batch-Rendering
        self.render_batches: Dict[str, List[Tuple[pygame.Surface, Tuple[int, int]]]] = {}
        
    def add_to_atlas(self, key: str, surface: pygame.Surface) -> bool:
        """Fügt eine Textur zum Atlas hinzu."""
        success = self.texture_atlas.add_texture(key, surface)
        if success:
            self.render_stats['atlas_usage'] = self.texture_atlas.get_usage_percentage()
        return success
    
    def render_text(self, text: str, font_name: str, size: int, 
                   color: Tuple[int, int, int], 
                   antialias: bool = True) -> pygame.Surface:
        """Rendert Text mit optimiertem Caching."""
        return self.font_cache.render_text(text, font_name, size, color, antialias)
    
    def render_sprite(self, surface: pygame.Surface, position: Tuple[int, int], 
                     batch_key: str = "default") -> None:
        """Fügt ein Sprite zum Render-Batch hinzu."""
        if batch_key not in self.render_batches:
            self.render_batches[batch_key] = []
        
        self.render_batches[batch_key].append((surface, position))
    
    def render_batch(self, target_surface: pygame.Surface, batch_key: str = "default") -> None:
        """Rendert einen kompletten Batch."""
        if batch_key not in self.render_batches:
            return
        
        batch = self.render_batches[batch_key]
        
        # Sortiere nach Y-Position für korrekte Z-Order
        batch.sort(key=lambda x: x[1][1])
        
        # Batch rendern
        for surface, position in batch:
            if self.culling_enabled and not self._is_in_viewport(position, surface.get_size()):
                continue
            
            target_surface.blit(surface, position)
        
        # Batch leeren
        self.render_batches[batch_key].clear()
    
    def _is_in_viewport(self, position: Tuple[int, int], size: Tuple[int, int]) -> bool:
        """Prüft ob ein Objekt im Viewport sichtbar ist."""
        x, y = position
        width, height = size
        
        obj_rect = pygame.Rect(x, y, width, height)
        return obj_rect.colliderect(self.viewport)
    
    def set_viewport(self, x: int, y: int, width: int, height: int) -> None:
        """Setzt den aktuellen Viewport für Culling."""
        self.viewport = pygame.Rect(x, y, width, height)
    
    def clear_caches(self) -> None:
        """Leert alle Caches."""
        self.surface_cache.clear()
        self.font_cache.cached_texts.clear()
        self.render_batches.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Gibt Render-Statistiken zurück."""
        return {
            **self.render_stats,
            'atlas_usage': self.texture_atlas.get_usage_percentage(),
            'font_cache_size': len(self.font_cache.cached_texts),
            'surface_cache_size': len(self.surface_cache),
            'batch_count': len(self.render_batches)
        }
    
    def update(self, dt: float) -> None:
        """Aktualisiert den Renderer."""
        self.font_cache.update(dt)
        self.render_stats['frames_rendered'] += 1


class RenderOptimizer:
    """Optimiert Rendering-Operationen."""
    
    def __init__(self):
        self.optimizations = {
            'culling': True,
            'batching': True,
            'atlas': True,
            'font_caching': True,
            'surface_caching': True
        }
        
    def optimize_surface(self, surface: pygame.Surface) -> pygame.Surface:
        """Optimiert eine Oberfläche für bessere Performance."""
        # Konvertiere zu optimalem Format
        if surface.get_alpha() is None:
            # Keine Transparenz - konvertiere zu RGB
            optimized = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            optimized.blit(surface, (0, 0))
        else:
            # Behalte Transparenz
            optimized = surface
        
        return optimized
    
    def create_sprite_sheet(self, sprites: List[pygame.Surface], 
                           sprite_size: Tuple[int, int]) -> Tuple[pygame.Surface, List[pygame.Rect]]:
        """Erstellt ein Sprite-Sheet aus mehreren Sprites."""
        if not sprites:
            return pygame.Surface((0, 0)), []
        
        # Optimalen Sheet-Layout berechnen
        sprites_per_row = int((len(sprites) ** 0.5) + 0.5)
        sprites_per_col = (len(sprites) + sprites_per_row - 1) // sprites_per_row
        
        sheet_width = sprites_per_row * sprite_size[0]
        sheet_height = sprites_per_col * sprite_size[1]
        
        # Sheet erstellen
        sheet = pygame.Surface((sheet_width, sheet_height), pygame.SRCALPHA)
        sprite_rects = []
        
        for i, sprite in enumerate(sprites):
            row = i // sprites_per_row
            col = i % sprites_per_row
            
            x = col * sprite_size[0]
            y = row * sprite_size[1]
            
            sheet.blit(sprite, (x, y))
            sprite_rects.append(pygame.Rect(x, y, sprite_size[0], sprite_size[1]))
        
        return sheet, sprite_rects
