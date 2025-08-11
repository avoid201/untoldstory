"""
Save/Load system using JSON and ZIP compression.
Includes checksum validation for save integrity.
"""

import json
import zipfile
import hashlib
import os
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class SaveMetadata:
    """Metadata for a save file."""
    slot: int
    name: str
    timestamp: float
    playtime: float
    location: str
    level: int
    badges: int
    monsters_caught: int
    version: str
    checksum: str
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'slot': self.slot,
            'name': self.name,
            'timestamp': self.timestamp,
            'playtime': self.playtime,
            'location': self.location,
            'level': self.level,
            'badges': self.badges,
            'monsters_caught': self.monsters_caught,
            'version': self.version,
            'checksum': self.checksum
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'SaveMetadata':
        """Create from dictionary."""
        return cls(
            slot=data['slot'],
            name=data['name'],
            timestamp=data['timestamp'],
            playtime=data['playtime'],
            location=data['location'],
            level=data['level'],
            badges=data['badges'],
            monsters_caught=data['monsters_caught'],
            version=data['version'],
            checksum=data['checksum']
        )


class SaveSystem:
    """Handles saving and loading game data."""
    
    SAVE_VERSION = "1.0.0"
    SAVE_DIR = "saves"
    MAX_SLOTS = 3
    MAX_BACKUPS = 3
    
    def __init__(self, save_directory: Optional[str] = None):
        """
        Initialize save system.
        
        Args:
            save_directory: Custom save directory path
        """
        self.save_dir = Path(save_directory or self.SAVE_DIR)
        self.save_dir.mkdir(parents=True, exist_ok=True)
        
        # Create backup directory
        self.backup_dir = self.save_dir / "backups"
        self.backup_dir.mkdir(exist_ok=True)
    
    def save_game(self, slot: int, game_data: Dict[str, Any],
                 player_name: str = "Player") -> bool:
        """
        Save the game to a slot.
        
        Args:
            slot: Save slot (1-3)
            game_data: Complete game state dictionary
            player_name: Player/save name
            
        Returns:
            True if save successful
        """
        if not 1 <= slot <= self.MAX_SLOTS:
            print(f"Invalid save slot: {slot}")
            return False
        
        try:
            # Backup existing save if it exists
            save_path = self._get_save_path(slot)
            if save_path.exists():
                self._backup_save(slot)
            
            # Prepare save data
            save_data = {
                'version': self.SAVE_VERSION,
                'metadata': self._create_metadata(slot, game_data, player_name),
                'game_data': game_data
            }
            
            # Convert to JSON
            json_str = json.dumps(save_data, indent=2)
            json_bytes = json_str.encode('utf-8')
            
            # Calculate checksum
            checksum = hashlib.sha256(json_bytes).hexdigest()
            save_data['metadata']['checksum'] = checksum
            
            # Re-encode with checksum
            json_str = json.dumps(save_data, indent=2)
            json_bytes = json_str.encode('utf-8')
            
            # Create ZIP file
            with zipfile.ZipFile(save_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                zf.writestr('save.json', json_bytes)
                
                # Add metadata separately for quick access
                metadata_json = json.dumps(save_data['metadata'], indent=2)
                zf.writestr('metadata.json', metadata_json)
                
                # Add screenshots if available
                # TODO: Add screenshot functionality
            
            print(f"Game saved to slot {slot}")
            return True
            
        except Exception as e:
            print(f"Failed to save game: {e}")
            return False
    
    def load_game(self, slot: int) -> Optional[Dict[str, Any]]:
        """
        Load a game from a slot.
        
        Args:
            slot: Save slot (1-3)
            
        Returns:
            Game data dictionary or None if load fails
        """
        if not 1 <= slot <= self.MAX_SLOTS:
            print(f"Invalid save slot: {slot}")
            return None
        
        save_path = self._get_save_path(slot)
        if not save_path.exists():
            print(f"No save file in slot {slot}")
            return None
        
        try:
            with zipfile.ZipFile(save_path, 'r') as zf:
                # Read save data
                json_bytes = zf.read('save.json')
                json_str = json_bytes.decode('utf-8')
                save_data = json.loads(json_str)
                
                # Verify version compatibility
                if not self._check_version_compatibility(save_data['version']):
                    print(f"Incompatible save version: {save_data['version']}")
                    return None
                
                # Verify checksum
                stored_checksum = save_data['metadata']['checksum']
                save_data['metadata']['checksum'] = ""
                verify_json = json.dumps(save_data, indent=2).encode('utf-8')
                calculated_checksum = hashlib.sha256(verify_json).hexdigest()
                
                if stored_checksum != calculated_checksum:
                    print("Save file corrupted (checksum mismatch)")
                    # Attempt to load anyway with warning
                    response = input("Save may be corrupted. Load anyway? (y/n): ")
                    if response.lower() != 'y':
                        return None
                
                print(f"Game loaded from slot {slot}")
                return save_data['game_data']
                
        except Exception as e:
            print(f"Failed to load game: {e}")
            return None
    
    def get_save_metadata(self, slot: int) -> Optional[SaveMetadata]:
        """
        Get metadata for a save slot without loading full save.
        
        Args:
            slot: Save slot (1-3)
            
        Returns:
            SaveMetadata or None if no save
        """
        save_path = self._get_save_path(slot)
        if not save_path.exists():
            return None
        
        try:
            with zipfile.ZipFile(save_path, 'r') as zf:
                if 'metadata.json' in zf.namelist():
                    metadata_json = zf.read('metadata.json').decode('utf-8')
                    metadata_dict = json.loads(metadata_json)
                    return SaveMetadata.from_dict(metadata_dict)
                else:
                    # Fallback: read from main save
                    json_bytes = zf.read('save.json')
                    save_data = json.loads(json_bytes.decode('utf-8'))
                    return SaveMetadata.from_dict(save_data['metadata'])
                    
        except Exception as e:
            print(f"Failed to read save metadata: {e}")
            return None
    
    def get_all_saves(self) -> List[Optional[SaveMetadata]]:
        """
        Get metadata for all save slots.
        
        Returns:
            List of SaveMetadata (None for empty slots)
        """
        saves = []
        for slot in range(1, self.MAX_SLOTS + 1):
            saves.append(self.get_save_metadata(slot))
        return saves
    
    def delete_save(self, slot: int) -> bool:
        """
        Delete a save file.
        
        Args:
            slot: Save slot (1-3)
            
        Returns:
            True if deleted successfully
        """
        save_path = self._get_save_path(slot)
        if save_path.exists():
            try:
                # Backup before deleting
                self._backup_save(slot)
                save_path.unlink()
                print(f"Save slot {slot} deleted")
                return True
            except Exception as e:
                print(f"Failed to delete save: {e}")
                return False
        return False
    
    def quick_save(self, game_data: Dict[str, Any]) -> bool:
        """
        Quick save to auto-save slot.
        
        Args:
            game_data: Game state to save
            
        Returns:
            True if saved successfully
        """
        auto_save_path = self.save_dir / "autosave.sav"
        
        try:
            json_str = json.dumps(game_data, indent=2)
            json_bytes = json_str.encode('utf-8')
            
            with zipfile.ZipFile(auto_save_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                zf.writestr('quicksave.json', json_bytes)
                zf.writestr('timestamp.txt', str(time.time()))
            
            return True
        except Exception as e:
            print(f"Quick save failed: {e}")
            return False
    
    def quick_load(self) -> Optional[Dict[str, Any]]:
        """
        Load from quick save.
        
        Returns:
            Game data or None
        """
        auto_save_path = self.save_dir / "autosave.sav"
        
        if not auto_save_path.exists():
            return None
        
        try:
            with zipfile.ZipFile(auto_save_path, 'r') as zf:
                json_bytes = zf.read('quicksave.json')
                return json.loads(json_bytes.decode('utf-8'))
        except Exception as e:
            print(f"Quick load failed: {e}")
            return None
    
    def _get_save_path(self, slot: int) -> Path:
        """Get path for a save slot."""
        return self.save_dir / f"save_{slot}.sav"
    
    def _backup_save(self, slot: int) -> None:
        """Create backup of existing save."""
        save_path = self._get_save_path(slot)
        if not save_path.exists():
            return
        
        # Create timestamped backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"save_{slot}_backup_{timestamp}.sav"
        backup_path = self.backup_dir / backup_name
        
        try:
            import shutil
            shutil.copy2(save_path, backup_path)
            
            # Clean old backups
            self._clean_old_backups(slot)
            
        except Exception as e:
            print(f"Failed to create backup: {e}")
    
    def _clean_old_backups(self, slot: int) -> None:
        """Remove old backups keeping only MAX_BACKUPS most recent."""
        pattern = f"save_{slot}_backup_*.sav"
        backups = sorted(self.backup_dir.glob(pattern))
        
        if len(backups) > self.MAX_BACKUPS:
            for old_backup in backups[:-self.MAX_BACKUPS]:
                try:
                    old_backup.unlink()
                except:
                    pass
    
    def _create_metadata(self, slot: int, game_data: Dict, 
                        player_name: str) -> Dict:
        """Create save metadata."""
        # Extract relevant info from game data
        player_data = game_data.get('player', {})
        party_data = game_data.get('party', {})
        story_data = game_data.get('story', {})
        
        # Calculate average party level
        party_members = party_data.get('members', [])
        levels = [m['level'] for m in party_members if m]
        avg_level = sum(levels) // len(levels) if levels else 1
        
        # Count completed trials
        trials_completed = sum(1 for i in range(1, 11) 
                    if story_data.get('flags', {}).get(f'trial_{i}_defeated'))
        
        # Count caught monsters
        storage_data = game_data.get('storage', {})
        monsters_caught = len(party_members)
        for box in storage_data.get('boxes', []):
            monsters_caught += sum(1 for m in box.get('monsters', []) if m)
        
        return {
            'slot': slot,
            'name': player_name,
            'timestamp': time.time(),
            'playtime': game_data.get('playtime', 0),
            'location': player_data.get('current_map', 'unknown'),
            'level': avg_level,
            'badges': trials_completed,
            'monsters_caught': monsters_caught,
            'version': self.SAVE_VERSION,
            'checksum': ""  # Will be filled later
        }
    
    def _check_version_compatibility(self, save_version: str) -> bool:
        """Check if save version is compatible."""
        # Simple version check - could be more sophisticated
        major_current = int(self.SAVE_VERSION.split('.')[0])
        major_save = int(save_version.split('.')[0])
        
        # Only major version needs to match
        return major_current == major_save
    
    def export_save(self, slot: int, export_path: str) -> bool:
        """
        Export a save file for sharing.
        
        Args:
            slot: Save slot to export
            export_path: Path to export to
            
        Returns:
            True if exported successfully
        """
        save_path = self._get_save_path(slot)
        if not save_path.exists():
            return False
        
        try:
            import shutil
            shutil.copy2(save_path, export_path)
            print(f"Save exported to {export_path}")
            return True
        except Exception as e:
            print(f"Failed to export save: {e}")
            return False
    
    def import_save(self, import_path: str, slot: int) -> bool:
        """
        Import a save file.
        
        Args:
            import_path: Path to save file to import
            slot: Slot to import into
            
        Returns:
            True if imported successfully
        """
        if not os.path.exists(import_path):
            print("Import file not found")
            return False
        
        # Validate save file
        try:
            with zipfile.ZipFile(import_path, 'r') as zf:
                if 'save.json' not in zf.namelist():
                    print("Invalid save file format")
                    return False
            
            # Backup existing save
            if self._get_save_path(slot).exists():
                self._backup_save(slot)
            
            # Copy to slot
            import shutil
            shutil.copy2(import_path, self._get_save_path(slot))
            print(f"Save imported to slot {slot}")
            return True
            
        except Exception as e:
            print(f"Failed to import save: {e}")
            return False


class GameStateSerializer:
    """Serializes and deserializes complete game state."""
    
    @staticmethod
    def serialize(game) -> Dict[str, Any]:
        """
        Serialize complete game state.
        
        Args:
            game: Game instance
            
        Returns:
            Serialized game state dictionary
        """
        from engine.systems.party import PartyManager
        from engine.systems.story import StoryManager
        from engine.systems.quests import QuestManager
        from engine.systems.items import Inventory
        
        state = {
            'version': SaveSystem.SAVE_VERSION,
            'timestamp': time.time(),
            'playtime': getattr(game, 'playtime', 0),
            
            # Player data
            'player': {
                'name': getattr(game, 'player_name', 'Player'),
                'position': getattr(game.player, 'position', (0, 0)) if hasattr(game, 'player') else (0, 0),
                'current_map': getattr(game, 'current_map', 'player_house'),
                'facing': getattr(game.player, 'facing', 'down') if hasattr(game, 'player') else 'down'
            },
            
            # Party and storage
            'party_manager': game.party_manager.to_dict() if hasattr(game, 'party_manager') else {},
            
            # Story and quests
            'story': game.story_manager.to_dict() if hasattr(game, 'story_manager') else {},
            'quests': game.quest_manager.to_dict() if hasattr(game, 'quest_manager') else {},
            
            # Inventory
            'inventory': game.inventory.to_dict() if hasattr(game, 'inventory') else {},
            
            # Settings
            'settings': {
                'music_volume': getattr(game, 'music_volume', 0.7),
                'sfx_volume': getattr(game, 'sfx_volume', 0.8),
                'text_speed': getattr(game, 'text_speed', 1.0)
            }
        }
        
        return state
    
    @staticmethod
    def deserialize(game, state: Dict[str, Any]) -> None:
        """
        Deserialize game state into game instance.
        
        Args:
            game: Game instance to load into
            state: Serialized state dictionary
        """
        from engine.systems.party import PartyManager
        from engine.systems.story import StoryManager
        from engine.systems.quests import QuestManager
        from engine.systems.items import Inventory
        
        # Restore player data
        player_data = state.get('player', {})
        game.player_name = player_data.get('name', 'Player')
        game.current_map = player_data.get('current_map', 'player_house')
        
        if hasattr(game, 'player'):
            game.player.position = player_data.get('position', (0, 0))
            game.player.facing = player_data.get('facing', 'down')
        
        # Restore party and storage
        if 'party_manager' in state:
            game.party_manager = PartyManager.from_dict(state['party_manager'])
        
        # Restore story
        if 'story' in state:
            game.story_manager = StoryManager.from_dict(state['story'])
        
        # Restore quests
        if 'quests' in state:
            game.quest_manager = QuestManager.from_dict(state['quests'])
        
        # Restore inventory
        if 'inventory' in state:
            game.inventory = Inventory.from_dict(state['inventory'])
        
        # Restore settings
        settings = state.get('settings', {})
        game.music_volume = settings.get('music_volume', 0.7)
        game.sfx_volume = settings.get('sfx_volume', 0.8)
        game.text_speed = settings.get('text_speed', 1.0)
        
        # Restore playtime
        game.playtime = state.get('playtime', 0)
