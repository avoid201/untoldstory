"""
Resource Loading and Caching System for Untold Story
Handles loading and caching of images, JSON data, sounds, and other assets
"""

import json
import pygame
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, Union
from enum import Enum
from functools import lru_cache


class ResourceType(Enum):
    """Types of resources that can be loaded."""
    IMAGE = "image"
    JSON = "json"
    SOUND = "sound"
    MUSIC = "music"
    FONT = "font"


class ResourceManager:
    """
    Singleton resource manager for loading and caching game assets.
    Provides centralized access to all game resources with automatic caching.
    """
    
    _instance: Optional['ResourceManager'] = None
    
    def __new__(cls) -> 'ResourceManager':
        """Ensure singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self) -> None:
        """Initialize the resource manager."""
        if self._initialized:
            return
        
        self._initialized = True
        
        # Set up paths relative to project root
        self.project_root = Path(__file__).parent.parent.parent
        self.assets_path = self.project_root / "assets"
        self.data_path = self.project_root / "data"
        self.sprites_path = self.project_root / "sprites"  # Neuer Pfad für Sprites
        
        # Create subdirectory paths
        self.gfx_path = self.assets_path / "gfx"
        self.sfx_path = self.assets_path / "sfx"
        self.bgm_path = self.assets_path / "bgm"
        
        # Resource caches with size limits
        self.MAX_CACHE_SIZE = {
            'image': 100 * 1024 * 1024,  # 100MB für Bilder
            'sound': 50 * 1024 * 1024,   # 50MB für Sounds
            'json': 10 * 1024 * 1024     # 10MB für JSON
        }
        
        self._image_cache: Dict[str, Tuple[pygame.Surface, int, float]] = {}  # Surface, size, last_used
        self._json_cache: Dict[str, Tuple[Any, int, float]] = {}  # Data, size, last_used
        self._sound_cache: Dict[str, Tuple[pygame.mixer.Sound, int, float]] = {}  # Sound, size, last_used
        self._music_loaded: Optional[str] = None
        self._font_cache: Dict[Tuple[Optional[str], int], pygame.font.Font] = {}
        # Data caches
        self._monster_index: Optional[Dict[int, Any]] = None
        
        # Priority assets that should not be unloaded
        self._priority_assets = set()
        
        # Current cache sizes
        self._cache_sizes = {
            'image': 0,
            'sound': 0,
            'json': 0
        }
        
        # Placeholder resources for missing assets
        self._placeholder_image: Optional[pygame.Surface] = None
        self._placeholder_sound: Optional[pygame.mixer.Sound] = None
        
        # Initialize pygame mixer for audio
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        except pygame.error as e:
            print(f"Warning: Could not initialize audio: {e}")

        # Control logging for missing audio assets (suppress by default)
        self._audio_warning_enabled = False
        
        # Load essential assets
        self._load_essential_assets()
    
    def path_exists(self, path: str) -> bool:
        """Prüfe ob Pfad existiert."""
        full_path = self.gfx_path / path
        return full_path.exists()
    
    def data_path_exists(self, path: str) -> bool:
        """Prüfe ob Data-Pfad existiert."""
        full_path = self.data_path / path
        return full_path.exists()
    
    def sprite_path_exists(self, path: str) -> bool:
        """Prüfe ob Sprite-Pfad existiert."""
        full_path = self.sprites_path / path
        return full_path.exists()
    
    def load_sprite(self, path: str, 
                   colorkey: Optional[Tuple[int, int, int]] = None,
                   alpha: bool = True) -> pygame.Surface:
        """
        Load a sprite from the sprites/ directory.
        
        Args:
            path: Relative path from sprites/ to the sprite file
            colorkey: Optional color to treat as transparent
            alpha: Whether to convert with alpha channel support
            
        Returns:
            The loaded pygame Surface, or a placeholder if not found
        """
        # Check cache
        cache_key = f"sprite:{path}:{colorkey}:{alpha}"
        if cache_key in self._image_cache:
            return self._image_cache[cache_key]
        
        # Build full path
        full_path = self.sprites_path / path
        
        if not full_path.exists():
            print(f"[Resources] Sprite not found: {full_path}")
            # Return placeholder surface
            placeholder = pygame.Surface((16, 16))
            placeholder.fill((255, 0, 255))  # Magenta für fehlende Textur
            return placeholder
        
        try:
            # Load the image
            image = pygame.image.load(str(full_path))
            
            # Convert for performance
            if alpha:
                image = image.convert_alpha()
            else:
                image = image.convert()
            
            # Apply colorkey if specified
            if colorkey is not None:
                if colorkey == -1:
                    colorkey = image.get_at((0, 0))
                image.set_colorkey(colorkey)
            
            # Cache and return
            self._image_cache[cache_key] = image
            return image
            
        except Exception as e:
            print(f"[Resources] Error loading sprite {path}: {e}")
            placeholder = pygame.Surface((16, 16))
            placeholder.fill((255, 0, 255))  # Magenta für fehlende Textur
            return placeholder
    
    def load_image(self, path: str, 
                   colorkey: Optional[Tuple[int, int, int]] = None,
                   alpha: bool = True,
                   priority: bool = False) -> pygame.Surface:
        """
        Load an image from the assets/gfx directory.
        
        Args:
            path: Relative path from assets/gfx/ to the image file
            colorkey: Optional color to treat as transparent
            alpha: Whether to convert with alpha channel support
            priority: Whether this is a priority asset that shouldn't be unloaded
            
        Returns:
            The loaded pygame Surface, or a placeholder if not found
        """
        import time
        
        # Check cache
        cache_key = f"{path}:{colorkey}:{alpha}"
        if cache_key in self._image_cache:
            surface, size, _ = self._image_cache[cache_key]
            # Update last used time
            self._image_cache[cache_key] = (surface, size, time.time())
            return surface
        
        # Build full path
        full_path = self.gfx_path / path
        
        if not full_path.exists():
            print(f"[Resources] Image not found: {full_path}")
            # Return placeholder surface
            placeholder = pygame.Surface((16, 16))
            placeholder.fill((255, 0, 255))  # Magenta für fehlende Textur
            return placeholder
        
        try:
            # Check file integrity
            if not self._verify_image_file(full_path):
                raise ValueError("Korrupte Bilddatei")
            
            # Load the image
            image = pygame.image.load(str(full_path))
            
            # Convert for performance
            if alpha:
                image = image.convert_alpha()
            else:
                image = image.convert()
            
            # Apply colorkey if specified
            if colorkey is not None:
                if colorkey == -1:
                    colorkey = image.get_at((0, 0))
                image.set_colorkey(colorkey)
            
            # Calculate size in bytes
            size = image.get_width() * image.get_height() * 4  # Approximation for RGBA
            
            # Check cache size and make room if needed
            if not priority:
                self._ensure_cache_space('image', size)
            
            # Cache and return
            self._image_cache[cache_key] = (image, size, time.time())
            self._cache_sizes['image'] += size
            
            # Mark as priority if needed
            if priority:
                self._priority_assets.add(cache_key)
            
            return image
            
        except Exception as e:
            print(f"[Resources] Error loading {path}: {e}")
            placeholder = pygame.Surface((16, 16))
            placeholder.fill((255, 0, 255))  # Magenta für fehlende Textur
            return placeholder
    
    def _verify_image_file(self, path: Path) -> bool:
        """Verify image file integrity."""
        try:
            # Check file size
            if path.stat().st_size == 0:
                return False
            
            # Try to open and verify header
            with open(path, 'rb') as f:
                header = f.read(8)
                # Check PNG signature
                if path.suffix.lower() == '.png':
                    return header.startswith(b'\x89PNG\r\n\x1a\n')
                # Add more formats as needed
                return True
        except Exception:
            return False
    
    def _ensure_cache_space(self, cache_type: str, needed_size: int) -> None:
        """
        Ensure there's enough space in cache for a new item.
        Uses LRU (Least Recently Used) eviction.
        """
        if needed_size > self.MAX_CACHE_SIZE[cache_type]:
            print(f"Warning: Asset size ({needed_size/1024/1024:.1f}MB) exceeds cache limit!")
            return
        
        cache_dict = {
            'image': self._image_cache,
            'sound': self._sound_cache,
            'json': self._json_cache
        }[cache_type]
        
        while (self._cache_sizes[cache_type] + needed_size > self.MAX_CACHE_SIZE[cache_type]):
            # Find least recently used non-priority item
            lru_key = None
            lru_time = float('inf')
            
            for key, (_, size, last_used) in cache_dict.items():
                if key not in self._priority_assets and last_used < lru_time:
                    lru_key = key
                    lru_time = last_used
            
            if lru_key:
                # Remove item
                _, size, _ = cache_dict.pop(lru_key)
                self._cache_sizes[cache_type] -= size
            else:
                # Only priority items in cache
                print(f"Warning: Cache full of priority items!")
                break
    
    def load_json(self, path: str, from_data: bool = True, **_: Any) -> Any:
        """
        Load JSON data from either the data/ or assets/ directory.
        
        Args:
            path: Relative path to the JSON file
            from_data: If True, load from data/, otherwise from assets/
            
        Returns:
            The parsed JSON data, or an empty dict if not found
        """
        # Check cache
        cache_key = f"{from_data}:{path}"
        if cache_key in self._json_cache:
            return self._json_cache[cache_key]
        
        # Build full path
        base_path = self.data_path if from_data else self.assets_path
        full_path = base_path / path
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Cache and return
            self._json_cache[cache_key] = data
            return data
            
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Warning: Could not load JSON '{path}': {e}")
            return {}

    # ---------------------- Game Data Helpers ----------------------
    def _ensure_monster_index(self) -> None:
        """Lazy-load and index monsters.json by id."""
        if self._monster_index is not None:
            return
        try:
            data = self.load_json("monsters.json", from_data=True)
            index: Dict[int, Any] = {}
            if isinstance(data, list):
                for entry in data:
                    try:
                        idx = int(entry.get("id"))
                        index[idx] = entry
                    except Exception:
                        continue
            self._monster_index = index
        except Exception as e:
            print(f"Warning: Could not index monsters.json: {e}")
            self._monster_index = {}

    def get_monster_species(self, species_id: int | str) -> Optional[Dict[str, Any]]:
        """Return monster species dict by id. Fails gracefully.

        Args:
            species_id: numeric id or numeric string
        Returns:
            Dict with species data or None if missing
        """
        try:
            sid = int(species_id)
        except Exception:
            return None
        self._ensure_monster_index()
        if not self._monster_index:
            return None
        return self._monster_index.get(sid)
    
    def load_sound(self, path: str, volume: float = 1.0, **_: Any) -> pygame.mixer.Sound:
        """
        Load a sound effect from the assets/sfx directory.
        
        Args:
            path: Relative path from assets/sfx/ to the sound file
            volume: Volume level (0.0 to 1.0)
            
        Returns:
            The loaded pygame Sound, or a placeholder if not found
        """
        # Check cache
        if path in self._sound_cache:
            sound = self._sound_cache[path]
            sound.set_volume(volume)
            return sound
        
        # Build full path
        full_path = self.sfx_path / path
        
        try:
            sound = pygame.mixer.Sound(str(full_path))
            sound.set_volume(volume)
            
            # Cache and return
            self._sound_cache[path] = sound
            return sound
            
        except (pygame.error, FileNotFoundError) as e:
            # Optionally warn once per path and cache placeholder to avoid spam
            if self._audio_warning_enabled:
                print(f"Warning: Could not load sound '{path}': {e}")
            placeholder = self._get_placeholder_sound()
            # Cache placeholder so repeated requests don't reattempt disk IO
            self._sound_cache[path] = placeholder
            placeholder.set_volume(volume)
            return placeholder
    
    def load_music(self, path: str, loops: int = -1, 
                   start: float = 0.0, fade_ms: int = 0) -> bool:
        """
        Load and play background music from the assets/bgm directory.
        
        Args:
            path: Relative path from assets/bgm/ to the music file
            loops: Number of loops (-1 for infinite)
            start: Start position in seconds
            fade_ms: Fade in duration in milliseconds
            
        Returns:
            True if successfully loaded and playing, False otherwise
        """
        # Check if already playing this track
        if self._music_loaded == path and pygame.mixer.music.get_busy():
            return True
        
        # Build full path
        full_path = self.bgm_path / path
        
        try:
            pygame.mixer.music.load(str(full_path))
            
            if fade_ms > 0:
                pygame.mixer.music.play(loops, start, fade_ms)
            else:
                pygame.mixer.music.play(loops, start)
            
            self._music_loaded = path
            return True
            
        except (pygame.error, FileNotFoundError) as e:
            if self._audio_warning_enabled:
                print(f"Warning: Could not load music '{path}': {e}")
            return False

    def enable_audio_warnings(self, enabled: bool = True) -> None:
        """Enable or disable logging for missing audio assets."""
        self._audio_warning_enabled = enabled
    
    def stop_music(self, fade_ms: int = 0) -> None:
        """
        Stop the currently playing music.
        
        Args:
            fade_ms: Fade out duration in milliseconds
        """
        if fade_ms > 0:
            pygame.mixer.music.fadeout(fade_ms)
        else:
            pygame.mixer.music.stop()
        self._music_loaded = None
    
    def load_font(self, name: Optional[str] = None, size: int = 16) -> pygame.font.Font:
        """
        Load a font for text rendering.
        
        Args:
            name: Font name or path (None for default system font)
            size: Font size in pixels
            
        Returns:
            The loaded pygame Font
        """
        cache_key = (name, size)
        if cache_key in self._font_cache:
            return self._font_cache[cache_key]
        
        try:
            if name and (self.assets_path / "fonts" / name).exists():
                font_path = self.assets_path / "fonts" / name
                font = pygame.font.Font(str(font_path), size)
            else:
                font = pygame.font.Font(name, size)
            
            self._font_cache[cache_key] = font
            return font
            
        except pygame.error as e:
            print(f"Warning: Could not load font '{name}': {e}")
            # Return default font
            if (None, size) not in self._font_cache:
                self._font_cache[(None, size)] = pygame.font.Font(None, size)
            return self._font_cache[(None, size)]
    
    def create_surface(self, size: Tuple[int, int], 
                      color: Optional[Tuple[int, int, int, int]] = None) -> pygame.Surface:
        """
        Create a new surface with optional fill color.
        
        Args:
            size: Surface dimensions (width, height)
            color: Optional RGBA color to fill (alpha channel optional)
            
        Returns:
            A new pygame Surface
        """
        surface = pygame.Surface(size, pygame.SRCALPHA)
        if color:
            surface.fill(color)
        return surface
    
    def _get_fallback_image(self) -> pygame.Surface:
        """
        Get or create a fallback image for missing assets.
        
        Returns:
            A simple colored surface with asset type indicator
        """
        if self._placeholder_image is None:
            # Create a 32x32 colored surface with asset type indicator
            self._placeholder_image = pygame.Surface((32, 32), pygame.SRCALPHA)
            # Use a neutral gray color
            self._placeholder_image.fill((128, 128, 128, 200))
            # Add a simple pattern
            pygame.draw.rect(self._placeholder_image, (64, 64, 64), (4, 4, 24, 24), 2)
        return self._placeholder_image
    
    def _get_placeholder_sound(self) -> pygame.mixer.Sound:
        """
        Get or create a placeholder sound for missing audio.
        
        Returns:
            A silent sound object
        """
        if self._placeholder_sound is None:
            # Create a silent sound
            try:
                # Create a small silent buffer
                import array
                silent_buffer = array.array('h', [0] * 100)
                self._placeholder_sound = pygame.mixer.Sound(silent_buffer)
            except:
                # If that fails, create from an empty bytes object
                self._placeholder_sound = pygame.mixer.Sound(buffer=bytes(200))
        return self._placeholder_sound
    
    def clear_cache(self, resource_type: Optional[ResourceType] = None) -> None:
        """
        Clear resource caches to free memory.
        
        Args:
            resource_type: Specific type to clear, or None to clear all
        """
        if resource_type is None or resource_type == ResourceType.IMAGE:
            self._image_cache.clear()
        if resource_type is None or resource_type == ResourceType.JSON:
            self._json_cache.clear()
        if resource_type is None or resource_type == ResourceType.SOUND:
            self._sound_cache.clear()
        if resource_type is None or resource_type == ResourceType.FONT:
            self._font_cache.clear()
    
    def preload_images(self, paths: list[str]) -> None:
        """
        Preload multiple images into cache.
        
        Args:
            paths: List of image paths to preload
        """
        for path in paths:
            self.load_image(path)
    
    def preload_sounds(self, paths: list[str]) -> None:
        """
        Preload multiple sounds into cache.
        
        Args:
            paths: List of sound paths to preload
        """
        for path in paths:
            self.load_sound(path)
    
    def get_monster_species(self, species_id: int) -> Optional[Dict[str, Any]]:
        """
        Get monster species data by ID.
        
        Args:
            species_id: The ID of the monster species to get
            
        Returns:
            Dictionary with monster species data, or None if not found
        """
        try:
            monsters_data = self.load_json("monsters.json")
            
            # Search for monster by ID
            for monster in monsters_data:
                if monster.get('id') == species_id:
                    return monster
            
            print(f"Warning: Monster species {species_id} not found")
            return None
            
        except Exception as e:
            print(f"Error loading monster species {species_id}: {e}")
            return None

    def _load_essential_assets(self) -> None:
        """Load essential assets that should always be available."""
        # UI-Elemente
        essential_images = [
            'ui/dialog_box.png',
            'ui/menu_background.png',
            'ui/button.png',
            'ui/health_bar.png'
        ]
        
        # Platzhalter und Fehlertexturen
        placeholder_images = [
            'placeholders/missing_texture.png',
            'placeholders/loading.png',
            'placeholders/error.png'
        ]
        
        # Wichtige Soundeffekte
        essential_sounds = [
            'ui/select.wav',
            'ui/cancel.wav',
            'ui/error.wav'
        ]
        
        # Lade alle essentiellen Assets als Prioritäts-Assets
        for path in essential_images:
            try:
                self.load_image(path, priority=True)
            except Exception as e:
                print(f"Fehler beim Laden von essentiellem Bild {path}: {e}")
        
        for path in placeholder_images:
            try:
                self.load_image(path, priority=True)
            except Exception as e:
                print(f"Fehler beim Laden von Platzhalterbild {path}: {e}")
        
        for path in essential_sounds:
            try:
                self.load_sound(path, priority=True)
            except Exception as e:
                print(f"Fehler beim Laden von essentiellem Sound {path}: {e}")
        
        # Lade wichtige JSON-Daten
        essential_data = [
            'monsters.json',
            'moves.json',
            'types.json'
        ]
        
        for path in essential_data:
            try:
                self.load_json(path, priority=True)
            except Exception as e:
                print(f"Fehler beim Laden von essentiellen Daten {path}: {e}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get detailed statistics about cached resources.
        
        Returns:
            Dictionary with cache information
        """
        return {
            "counts": {
                "images": len(self._image_cache),
                "json": len(self._json_cache),
                "sounds": len(self._sound_cache),
                "fonts": len(self._font_cache),
                "priority": len(self._priority_assets)
            },
            "sizes": {
                "images": self._cache_sizes['image'] / 1024 / 1024,  # MB
                "json": self._cache_sizes['json'] / 1024 / 1024,     # MB
                "sound": self._cache_sizes['sound'] / 1024 / 1024    # MB
            },
            "limits": {
                "images": self.MAX_CACHE_SIZE['image'] / 1024 / 1024,  # MB
                "json": self.MAX_CACHE_SIZE['json'] / 1024 / 1024,     # MB
                "sound": self.MAX_CACHE_SIZE['sound'] / 1024 / 1024    # MB
            }
        }


# Global singleton instance
resources = ResourceManager()