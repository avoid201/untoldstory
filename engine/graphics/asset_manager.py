"""
Asset-Manager für Untold Story
Verbessert Asset-Organisation und -Qualität
"""

import pygame
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, Set
from dataclasses import dataclass
from enum import Enum, auto
import json
import hashlib
from PIL import Image
import io

from engine.core.config import ASSETS_DIR, GFX_DIR, SFX_DIR, BGM_DIR


class AssetType(Enum):
    """Arten von Assets."""
    SPRITE = auto()
    TILE = auto()
    UI = auto()
    AUDIO = auto()
    FONT = auto()
    MAP = auto()


class AssetQuality(Enum):
    """Qualitätsstufen für Assets."""
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    OPTIMAL = auto()


@dataclass
class AssetInfo:
    """Metadaten für ein Asset."""
    path: Path
    asset_type: AssetType
    size: Tuple[int, int]
    file_size: int
    format: str
    quality: AssetQuality
    tags: List[str]
    last_modified: float
    hash: str
    is_optimized: bool = False


class AssetValidator:
    """Validiert Asset-Qualität und -Konsistenz."""
    
    def __init__(self):
        self.quality_standards = {
            AssetType.SPRITE: {
                'min_size': (16, 16),
                'max_size': (256, 256),
                'preferred_formats': ['PNG'],
                'max_file_size': 1024 * 1024  # 1MB
            },
            AssetType.TILE: {
                'min_size': (16, 16),
                'max_size': (64, 64),
                'preferred_formats': ['PNG'],
                'max_file_size': 512 * 1024  # 512KB
            },
            AssetType.UI: {
                'min_size': (8, 8),
                'max_size': (512, 512),
                'preferred_formats': ['PNG'],
                'max_file_size': 2 * 1024 * 1024  # 2MB
            }
        }
    
    def validate_asset(self, asset_path: Path, asset_type: AssetType) -> Dict[str, Any]:
        """Validiert ein Asset und gibt Qualitätsinformationen zurück."""
        try:
            # Datei-Informationen
            file_size = asset_path.stat().st_size
            last_modified = asset_path.stat().st_mtime
            
            # Bild laden und analysieren
            if asset_path.suffix.lower() in ['.png', '.jpg', '.jpeg', '.bmp']:
                with Image.open(asset_path) as img:
                    size = img.size
                    format_name = img.format
                    
                    # Qualität bewerten
                    quality_score = self._calculate_quality_score(
                        asset_type, size, file_size, format_name
                    )
                    
                    # Tags generieren
                    tags = self._generate_tags(asset_type, size, format_name)
                    
                    # Hash berechnen
                    file_hash = self._calculate_file_hash(asset_path)
                    
                    return {
                        'valid': True,
                        'size': size,
                        'file_size': file_size,
                        'format': format_name,
                        'quality_score': quality_score,
                        'tags': tags,
                        'last_modified': last_modified,
                        'hash': file_hash,
                        'issues': []
                    }
            
            return {
                'valid': False,
                'issues': ['Unsupported file format']
            }
            
        except Exception as e:
            return {
                'valid': False,
                'issues': [f'Error loading asset: {str(e)}']
            }
    
    def _calculate_quality_score(self, asset_type: AssetType, size: Tuple[int, int], 
                                file_size: int, format_name: str) -> AssetQuality:
        """Berechnet einen Qualitäts-Score für ein Asset."""
        standards = self.quality_standards.get(asset_type, {})
        
        score = 0
        
        # Größe bewerten
        min_size = standards.get('min_size', (1, 1))
        max_size = standards.get('max_size', (9999, 9999))
        
        if min_size[0] <= size[0] <= max_size[0] and min_size[1] <= size[1] <= max_size[1]:
            score += 2
        elif size[0] < min_size[0] or size[1] < min_size[1]:
            score -= 1
        
        # Dateigröße bewerten
        max_file_size = standards.get('max_file_size', float('inf'))
        if file_size <= max_file_size:
            score += 1
        
        # Format bewerten
        preferred_formats = standards.get('preferred_formats', [])
        if format_name.upper() in preferred_formats:
            score += 1
        
        # Qualitätsstufe bestimmen
        if score >= 3:
            return AssetQuality.OPTIMAL
        elif score >= 2:
            return AssetQuality.HIGH
        elif score >= 1:
            return AssetQuality.MEDIUM
        else:
            return AssetQuality.LOW
    
    def _generate_tags(self, asset_type: AssetType, size: Tuple[int, int], 
                       format_name: str) -> List[str]:
        """Generiert Tags für ein Asset."""
        tags = [asset_type.name.lower(), format_name.lower()]
        
        # Größen-Tags
        if size[0] == size[1]:
            tags.append('square')
        if size[0] <= 32 and size[1] <= 32:
            tags.append('small')
        elif size[0] <= 128 and size[1] <= 128:
            tags.append('medium')
        else:
            tags.append('large')
        
        return tags
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Berechnet den Hash einer Datei."""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()


class AssetOptimizer:
    """Optimiert Assets für bessere Performance."""
    
    def __init__(self):
        self.optimization_settings = {
            'sprite_compression': True,
            'tile_compression': True,
            'ui_compression': False,  # UI sollte scharf bleiben
            'max_colors': 256,
            'dithering': True
        }
    
    def optimize_sprite(self, image_path: Path, output_path: Path) -> bool:
        """Optimiert ein Sprite für bessere Performance."""
        try:
            with Image.open(image_path) as img:
                # Konvertiere zu optimalem Format
                if img.mode in ['RGBA', 'LA']:
                    # Behalte Transparenz
                    optimized = img.convert('RGBA')
                else:
                    # Konvertiere zu RGB
                    optimized = img.convert('RGB')
                
                # Größe optimieren wenn nötig
                if optimized.size[0] > 256 or optimized.size[1] > 256:
                    optimized.thumbnail((256, 256), Image.Resampling.LANCZOS)
                
                # Speichern
                optimized.save(output_path, 'PNG', optimize=True)
                return True
                
        except Exception as e:
            print(f"Fehler beim Optimieren von {image_path}: {e}")
            return False
    
    def create_sprite_atlas(self, sprite_paths: List[Path], 
                           output_path: Path, max_size: int = 2048) -> bool:
        """Erstellt einen Sprite-Atlas aus mehreren Sprites."""
        try:
            sprites = []
            max_width = max_height = 0
            
            # Alle Sprites laden
            for sprite_path in sprite_paths:
                with Image.open(sprite_path) as img:
                    sprites.append(img.copy())
                    max_width = max(max_width, img.width)
                    max_height = max(max_height, img.height)
            
            if not sprites:
                return False
            
            # Atlas-Layout berechnen
            sprites_per_row = int((len(sprites) ** 0.5) + 0.5)
            sprites_per_col = (len(sprites) + sprites_per_row - 1) // sprites_per_row
            
            atlas_width = sprites_per_row * max_width
            atlas_height = sprites_per_col * max_height
            
            # Atlas-Größe begrenzen
            if atlas_width > max_size or atlas_height > max_size:
                scale_factor = min(max_size / atlas_width, max_size / atlas_height)
                atlas_width = int(atlas_width * scale_factor)
                atlas_height = int(atlas_height * scale_factor)
                max_width = int(max_width * scale_factor)
                max_height = int(max_height * scale_factor)
            
            # Atlas erstellen
            atlas = Image.new('RGBA', (atlas_width, atlas_height), (0, 0, 0, 0))
            
            # Sprites zum Atlas hinzufügen
            for i, sprite in enumerate(sprites):
                row = i // sprites_per_row
                col = i % sprites_per_row
                
                x = col * max_width
                y = row * max_height
                
                # Sprite skalieren wenn nötig
                if sprite.size != (max_width, max_height):
                    sprite = sprite.resize((max_width, max_height), Image.Resampling.LANCZOS)
                
                atlas.paste(sprite, (x, y), sprite)
            
            # Atlas speichern
            atlas.save(output_path, 'PNG', optimize=True)
            return True
            
        except Exception as e:
            print(f"Fehler beim Erstellen des Sprite-Atlas: {e}")
            return False


class AssetManager:
    """Hauptklasse für Asset-Verwaltung."""
    
    def __init__(self):
        self.assets: Dict[str, AssetInfo] = {}
        self.validator = AssetValidator()
        self.optimizer = AssetOptimizer()
        self.asset_cache: Dict[str, pygame.Surface] = {}
        
        # Asset-Verzeichnisse
        self.directories = {
            AssetType.SPRITE: GFX_DIR / "sprites",
            AssetType.TILE: GFX_DIR / "tiles",
            AssetType.UI: GFX_DIR / "ui",
            AssetType.AUDIO: SFX_DIR,
            AssetType.BGM: BGM_DIR
        }
        
        # Verzeichnisse erstellen
        for directory in self.directories.values():
            directory.mkdir(parents=True, exist_ok=True)
        
        # Assets scannen
        self.scan_assets()
    
    def scan_assets(self) -> None:
        """Scannt alle Asset-Verzeichnisse."""
        for asset_type, directory in self.directories.items():
            if directory.exists():
                self._scan_directory(directory, asset_type)
    
    def _scan_directory(self, directory: Path, asset_type: AssetType) -> None:
        """Scannt ein Verzeichnis nach Assets."""
        for file_path in directory.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in ['.png', '.jpg', '.jpeg', '.bmp', '.wav', '.mp3', '.ogg']:
                # Asset validieren
                validation_result = self.validator.validate_asset(file_path, asset_type)
                
                if validation_result['valid']:
                    # Asset-Info erstellen
                    asset_info = AssetInfo(
                        path=file_path,
                        asset_type=asset_type,
                        size=validation_result['size'],
                        file_size=validation_result['file_size'],
                        format=validation_result['format'],
                        quality=validation_result['quality_score'],
                        tags=validation_result['tags'],
                        last_modified=validation_result['last_modified'],
                        hash=validation_result['hash']
                    )
                    
                    # Zum Asset-Dictionary hinzufügen
                    asset_key = str(file_path.relative_to(ASSETS_DIR))
                    self.assets[asset_key] = asset_info
    
    def get_asset(self, asset_path: str) -> Optional[pygame.Surface]:
        """Lädt ein Asset (gecacht)."""
        if asset_path in self.asset_cache:
            return self.asset_cache[asset_path]
        
        full_path = ASSETS_DIR / asset_path
        if full_path.exists() and full_path.suffix.lower() in ['.png', '.jpg', '.jpeg', '.bmp']:
            try:
                surface = pygame.image.load(str(full_path))
                self.asset_cache[asset_path] = surface
                return surface
            except Exception as e:
                print(f"Fehler beim Laden von {asset_path}: {e}")
        
        return None
    
    def optimize_assets(self, asset_type: AssetType = None) -> Dict[str, bool]:
        """Optimiert Assets eines bestimmten Typs."""
        results = {}
        
        for asset_key, asset_info in self.assets.items():
            if asset_type and asset_info.asset_type != asset_type:
                continue
            
            if asset_info.asset_type in [AssetType.SPRITE, AssetType.TILE, AssetType.UI]:
                # Optimierten Pfad erstellen
                optimized_path = asset_info.path.parent / f"optimized_{asset_info.path.name}"
                
                # Asset optimieren
                if asset_info.asset_type == AssetType.SPRITE:
                    success = self.optimizer.optimize_sprite(asset_info.path, optimized_path)
                else:
                    success = self.optimizer.optimize_sprite(asset_info.path, optimized_path)
                
                results[asset_key] = success
                
                if success:
                    # Asset-Info aktualisieren
                    asset_info.path = optimized_path
                    asset_info.is_optimized = True
        
        return results
    
    def create_sprite_atlas(self, sprite_type: str, output_path: Path) -> bool:
        """Erstellt einen Sprite-Atlas für einen bestimmten Typ."""
        sprite_paths = []
        
        for asset_key, asset_info in self.assets.items():
            if (asset_info.asset_type == AssetType.SPRITE and 
                sprite_type in asset_info.tags):
                sprite_paths.append(asset_info.path)
        
        if sprite_paths:
            return self.optimizer.create_sprite_atlas(sprite_paths, output_path)
        
        return False
    
    def get_asset_stats(self) -> Dict[str, Any]:
        """Gibt Statistiken über alle Assets zurück."""
        stats = {
            'total_assets': len(self.assets),
            'by_type': {},
            'by_quality': {},
            'total_size': 0,
            'optimized_count': 0
        }
        
        for asset_info in self.assets.values():
            # Nach Typ gruppieren
            asset_type = asset_info.asset_type.name
            if asset_type not in stats['by_type']:
                stats['by_type'][asset_type] = 0
            stats['by_type'][asset_type] += 1
            
            # Nach Qualität gruppieren
            quality = asset_info.quality.name
            if quality not in stats['by_quality']:
                stats['by_quality'][quality] = 0
            stats['by_quality'][quality] += 1
            
            # Gesamtgröße
            stats['total_size'] += asset_info.file_size
            
            # Optimierte Assets zählen
            if asset_info.is_optimized:
                stats['optimized_count'] += 1
        
        return stats
    
    def export_asset_report(self, output_path: Path) -> bool:
        """Exportiert einen Asset-Report als JSON."""
        try:
            report = {
                'scan_timestamp': pygame.time.get_ticks(),
                'assets': {},
                'statistics': self.get_asset_stats()
            }
            
            for asset_key, asset_info in self.assets.items():
                report['assets'][asset_key] = {
                    'type': asset_info.asset_type.name,
                    'size': asset_info.size,
                    'file_size': asset_info.file_size,
                    'format': asset_info.format,
                    'quality': asset_info.quality.name,
                    'tags': asset_info.tags,
                    'is_optimized': asset_info.is_optimized,
                    'hash': asset_info.hash
                }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"Fehler beim Exportieren des Asset-Reports: {e}")
            return False
