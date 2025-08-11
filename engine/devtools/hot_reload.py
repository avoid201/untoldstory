"""
Hot reload system for development.
Automatically reloads assets and data when files change.
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, Set, Callable, Any, Optional
from dataclasses import dataclass
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent

from engine.core.config import DATA_DIR, ASSETS_DIR


@dataclass
class FileWatcher:
    """Watches a file for changes."""
    filepath: Path
    last_modified: float
    callback: Callable
    file_type: str


class HotReloadHandler(FileSystemEventHandler):
    """Handles file system events for hot reload."""
    
    def __init__(self, hot_reloader: 'HotReloader'):
        """
        Initialize handler.
        
        Args:
            hot_reloader: Reference to hot reloader
        """
        self.hot_reloader = hot_reloader
    
    def on_modified(self, event: FileModifiedEvent) -> None:
        """Handle file modification event."""
        if not event.is_directory:
            filepath = Path(event.src_path)
            self.hot_reloader.file_changed(filepath)


class HotReloader:
    """Hot reload system for game assets and data."""
    
    def __init__(self, game):
        """
        Initialize hot reloader.
        
        Args:
            game: Game instance
        """
        self.game = game
        self.enabled = False
        self.watchers: Dict[str, FileWatcher] = {}
        self.observer: Optional[Observer] = None
        self.reload_callbacks: Dict[str, Callable] = {}
        
        # File type handlers
        self.file_handlers = {
            '.json': self._reload_json,
            '.png': self._reload_image,
            '.jpg': self._reload_image,
            '.wav': self._reload_sound,
            '.ogg': self._reload_sound,
            '.mp3': self._reload_sound,
            '.toml': self._reload_config
        }
        
        # Directories to watch
        self.watch_dirs = [
            DATA_DIR,
            ASSETS_DIR,
            DATA_DIR / "maps",
            DATA_DIR / "dialogs",
            ASSETS_DIR / "gfx",
            ASSETS_DIR / "sfx",
            ASSETS_DIR / "bgm"
        ]
    
    def start(self) -> None:
        """Start hot reload monitoring."""
        if self.enabled:
            return
        
        self.enabled = True
        
        # Create observer
        self.observer = Observer()
        handler = HotReloadHandler(self)
        
        # Add watches for each directory
        for directory in self.watch_dirs:
            if directory.exists():
                self.observer.schedule(handler, str(directory), recursive=True)
                print(f"Watching directory: {directory}")
        
        # Start observer thread
        self.observer.start()
        print("Hot reload enabled")
    
    def stop(self) -> None:
        """Stop hot reload monitoring."""
        if not self.enabled:
            return
        
        self.enabled = False
        
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
        
        print("Hot reload disabled")
    
    def file_changed(self, filepath: Path) -> None:
        """
        Handle file change event.
        
        Args:
            filepath: Path to changed file
        """
        if not self.enabled:
            return
        
        # Get file extension
        ext = filepath.suffix.lower()
        
        # Check if we have a handler for this file type
        if ext in self.file_handlers:
            handler = self.file_handlers[ext]
            
            # Debounce - wait a bit to ensure file write is complete
            time.sleep(0.1)
            
            try:
                handler(filepath)
                print(f"Reloaded: {filepath.name}")
                
                # Call any registered callbacks
                self._trigger_callbacks(filepath)
                
            except Exception as e:
                print(f"Failed to reload {filepath.name}: {e}")
    
    def _reload_json(self, filepath: Path) -> None:
        """Reload JSON data file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Determine data type from filename
            filename = filepath.stem
            
            if "types" in filename:
                self._reload_types_data(data)
            elif "moves" in filename:
                self._reload_moves_data(data)
            elif "monsters" in filename:
                self._reload_monsters_data(data)
            elif "items" in filename:
                self._reload_items_data(data)
            elif filepath.parent.name == "maps":
                self._reload_map_data(filename, data)
            elif filepath.parent.name == "dialogs":
                self._reload_dialog_data(filename, data)
                
        except json.JSONDecodeError as e:
            print(f"JSON parse error in {filepath.name}: {e}")
    
    def _reload_types_data(self, data: Dict) -> None:
        """Reload type system data."""
        if hasattr(self.game, 'type_system'):
            # Update type chart
            if 'chart' in data:
                self.game.type_system.reload_chart(data['chart'])
    
    def _reload_moves_data(self, data: Dict) -> None:
        """Reload moves database."""
        if hasattr(self.game, 'move_database'):
            # Clear and reload moves
            self.game.move_database.clear()
            for move_data in data.get('moves', []):
                self.game.move_database.add_move(move_data)
    
    def _reload_monsters_data(self, data: Dict) -> None:
        """Reload monsters database."""
        if hasattr(self.game, 'monster_database'):
            # Update monster database
            self.game.monster_database.reload(data.get('monsters', []))
    
    def _reload_items_data(self, data: Dict) -> None:
        """Reload items database."""
        if hasattr(self.game, 'item_database'):
            # Reload items
            self.game.item_database._load_from_data(data.get('items', []))
    
    def _reload_map_data(self, map_id: str, data: Dict) -> None:
        """Reload map data."""
        # Check if this is the current map
        if hasattr(self.game, 'current_map') and self.game.current_map == map_id:
            if hasattr(self.game, 'current_scene'):
                scene = self.game.current_scene
                if hasattr(scene, 'reload_map'):
                    scene.reload_map(data)
    
    def _reload_dialog_data(self, dialog_id: str, data: Dict) -> None:
        """Reload dialog data."""
        if hasattr(self.game, 'dialogue_manager'):
            self.game.dialogue_manager.reload_dialogue(dialog_id, data)
    
    def _reload_image(self, filepath: Path) -> None:
        """Reload image asset."""
        if hasattr(self.game, 'resource_manager'):
            # Get relative path from assets directory
            try:
                rel_path = filepath.relative_to(ASSETS_DIR)
                resource_key = str(rel_path).replace('\\', '/')
                
                # Clear from cache
                self.game.resource_manager.clear_image(resource_key)
                
                # Reload if currently used
                if hasattr(self.game, 'current_scene'):
                    scene = self.game.current_scene
                    if hasattr(scene, 'reload_sprites'):
                        scene.reload_sprites()
                        
            except ValueError:
                pass  # Not in assets directory
    
    def _reload_sound(self, filepath: Path) -> None:
        """Reload sound asset."""
        if hasattr(self.game, 'resource_manager'):
            try:
                rel_path = filepath.relative_to(ASSETS_DIR)
                resource_key = str(rel_path).replace('\\', '/')
                
                # Clear from cache
                self.game.resource_manager.clear_sound(resource_key)
                
            except ValueError:
                pass
    
    def _reload_config(self, filepath: Path) -> None:
        """Reload configuration file."""
        if filepath.name == "settings.toml":
            try:
                import toml
                with open(filepath, 'r', encoding='utf-8') as f:
                    settings = toml.load(f)
                
                # Apply settings
                self._apply_settings(settings)
                
            except Exception as e:
                print(f"Failed to reload settings: {e}")
    
    def _apply_settings(self, settings: Dict) -> None:
        """Apply reloaded settings."""
        # Update audio settings
        if 'audio' in settings:
            audio = settings['audio']
            if hasattr(self.game, 'audio_manager'):
                self.game.audio_manager.set_master_volume(audio.get('master_volume', 0.7))
                self.game.audio_manager.set_bgm_volume(audio.get('bgm_volume', 0.5))
                self.game.audio_manager.set_sfx_volume(audio.get('sfx_volume', 0.8))
        
        # Update graphics settings
        if 'graphics' in settings:
            graphics = settings['graphics']
            if 'text_speed' in graphics:
                self.game.text_speed = graphics['text_speed']
        
        # Update debug settings
        if 'debug' in settings:
            debug = settings['debug']
            if hasattr(self.game, 'debug_overlay'):
                self.game.debug_overlay.enabled = debug.get('show_fps', False)
                self.game.debug_overlay.show_grid = debug.get('show_grid', False)
                self.game.debug_overlay.show_collision = debug.get('show_collision', False)
    
    def register_callback(self, pattern: str, callback: Callable) -> None:
        """
        Register a callback for file changes.
        
        Args:
            pattern: File pattern to match (e.g., "*.json", "maps/*.json")
            callback: Function to call when matching file changes
        """
        self.reload_callbacks[pattern] = callback
    
    def _trigger_callbacks(self, filepath: Path) -> None:
        """Trigger registered callbacks for a file."""
        for pattern, callback in self.reload_callbacks.items():
            if self._match_pattern(filepath, pattern):
                try:
                    callback(filepath)
                except Exception as e:
                    print(f"Callback error for {filepath.name}: {e}")
    
    def _match_pattern(self, filepath: Path, pattern: str) -> bool:
        """Check if filepath matches pattern."""
        import fnmatch
        return fnmatch.fnmatch(str(filepath), pattern)
    
    def reload_all(self) -> None:
        """Force reload all assets and data."""
        print("Reloading all assets and data...")
        
        # Reload JSON data
        for data_file in DATA_DIR.glob("*.json"):
            self._reload_json(data_file)
        
        # Reload maps
        maps_dir = DATA_DIR / "maps"
        if maps_dir.exists():
            for map_file in maps_dir.glob("*.json"):
                self._reload_json(map_file)
        
        # Clear resource caches
        if hasattr(self.game, 'resource_manager'):
            self.game.resource_manager.clear_all_caches()
        
        print("Reload complete")


class AssetCache:
    """Cache for hot-reloadable assets."""
    
    def __init__(self):
        """Initialize asset cache."""
        self.images: Dict[str, Any] = {}
        self.sounds: Dict[str, Any] = {}
        self.data: Dict[str, Any] = {}
        self.timestamps: Dict[str, float] = {}
    
    def get(self, key: str, loader: Callable) -> Any:
        """
        Get asset from cache or load it.
        
        Args:
            key: Asset key
            loader: Function to load asset if not cached
            
        Returns:
            Loaded asset
        """
        # Check if needs reload
        if self._needs_reload(key):
            asset = loader()
            self.set(key, asset)
            return asset
        
        # Return from cache
        return self.data.get(key) or loader()
    
    def set(self, key: str, value: Any) -> None:
        """Store asset in cache."""
        self.data[key] = value
        self.timestamps[key] = time.time()
    
    def clear(self, key: str) -> None:
        """Clear specific asset from cache."""
        self.data.pop(key, None)
        self.timestamps.pop(key, None)
    
    def clear_all(self) -> None:
        """Clear entire cache."""
        self.data.clear()
        self.timestamps.clear()
    
    def _needs_reload(self, key: str) -> bool:
        """Check if asset needs reloading."""
        # For now, always use cache unless explicitly cleared
        return key not in self.data