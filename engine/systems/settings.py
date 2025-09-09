"""
Settings System für Untold Story
Lädt und speichert Einstellungen aus/in settings.toml
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

# Fallback if toml not available
try:
    import toml
    TOML_AVAILABLE = True
except ImportError:
    TOML_AVAILABLE = False
    print("Warning: toml not available, using fallback settings")


class TextSpeed(Enum):
    """Text speed options."""
    SLOW = "slow"
    NORMAL = "normal"
    FAST = "fast"


@dataclass
class AudioSettings:
    """Audio configuration."""
    master_volume: float = 0.7
    bgm_volume: float = 0.5
    sfx_volume: float = 0.8
    ui_volume: float = 0.6
    music_enabled: bool = True
    sound_enabled: bool = True
    channels: int = 8
    bgm_fade_in: float = 1.0
    bgm_fade_out: float = 0.5


@dataclass
class DisplaySettings:
    """Display configuration."""
    logical_width: int = 320
    logical_height: int = 180
    window_scale: int = 4
    fullscreen: bool = False
    vsync: bool = True
    target_fps: int = 60
    
    @property
    def window_width(self) -> int:
        return self.logical_width * self.window_scale
    
    @property
    def window_height(self) -> int:
        return self.logical_height * self.window_scale


@dataclass
class GraphicsSettings:
    """Graphics configuration."""
    text_speed: TextSpeed = TextSpeed.NORMAL
    text_speed_multiplier: float = 1.0
    animation_speed: float = 0.15
    fade_duration: float = 0.5
    battle_swirl_duration: float = 1.0
    show_fps: bool = False
    show_grid: bool = False


@dataclass
class ControlsSettings:
    """Controls configuration."""
    move_up: list[str] = field(default_factory=lambda: ["w", "up"])
    move_down: list[str] = field(default_factory=lambda: ["s", "down"])
    move_left: list[str] = field(default_factory=lambda: ["a", "left"])
    move_right: list[str] = field(default_factory=lambda: ["d", "right"])
    confirm: list[str] = field(default_factory=lambda: ["e", "return", "space"])
    cancel: list[str] = field(default_factory=lambda: ["q", "escape"])
    run: list[str] = field(default_factory=lambda: ["lshift", "rshift"])
    pause: list[str] = field(default_factory=lambda: ["escape", "p"])
    debug: list[str] = field(default_factory=lambda: ["tab"])


@dataclass
class GameplaySettings:
    """Gameplay configuration."""
    difficulty: str = "normal"
    enemy_level_scaling: float = 1.0
    exp_multiplier: float = 1.0
    money_multiplier: float = 1.0
    grass_encounter_rate: float = 0.1
    cave_encounter_rate: float = 0.15
    water_encounter_rate: float = 0.2
    battle_animations: bool = True
    show_damage_numbers: bool = True
    auto_save_before_boss: bool = True


class SettingsManager:
    """Zentrale Settings-Verwaltung."""
    
    def __init__(self, settings_path: Optional[Path] = None):
        """
        Initialize settings manager.
        
        Args:
            settings_path: Path to settings.toml file
        """
        if settings_path is None:
            settings_path = Path(__file__).parent.parent.parent / "settings.toml"
        
        self.settings_path = settings_path
        
        # Initialize all settings with defaults
        self.audio = AudioSettings()
        self.display = DisplaySettings()
        self.graphics = GraphicsSettings()
        self.controls = ControlsSettings()
        self.gameplay = GameplaySettings()
        
        # Load settings from file
        self.load_settings()
    
    def load_settings(self) -> bool:
        """
        Load settings from TOML file.
        
        Returns:
            True if loaded successfully, False otherwise
        """
        if not TOML_AVAILABLE:
            print("TOML not available, using default settings")
            return False
        
        try:
            if not self.settings_path.exists():
                print(f"Settings file not found: {self.settings_path}")
                return False
            
            with open(self.settings_path, 'r', encoding='utf-8') as f:
                data = toml.load(f)
            
            # Load audio settings
            if 'audio' in data:
                audio_data = data['audio']
                self.audio.master_volume = audio_data.get('master_volume', 0.7)
                self.audio.bgm_volume = audio_data.get('bgm_volume', 0.5)
                self.audio.sfx_volume = audio_data.get('sfx_volume', 0.8)
                self.audio.channels = audio_data.get('channels', 8)
                self.audio.bgm_fade_in = audio_data.get('bgm_fade_in', 1.0)
                self.audio.bgm_fade_out = audio_data.get('bgm_fade_out', 0.5)
            
            # Load display settings
            if 'display' in data:
                display_data = data['display']
                self.display.logical_width = display_data.get('logical_width', 320)
                self.display.logical_height = display_data.get('logical_height', 180)
                self.display.window_scale = display_data.get('window_scale', 4)
                self.display.fullscreen = display_data.get('fullscreen', False)
                self.display.vsync = display_data.get('vsync', True)
                self.display.target_fps = display_data.get('target_fps', 60)
            
            # Load graphics settings
            if 'graphics' in data:
                graphics_data = data['graphics']
                text_speed_str = graphics_data.get('text_speed', 'normal')
                try:
                    self.graphics.text_speed = TextSpeed(text_speed_str)
                except ValueError:
                    self.graphics.text_speed = TextSpeed.NORMAL
                
                self.graphics.text_speed_multiplier = graphics_data.get('text_speed_multiplier', 1.0)
                self.graphics.animation_speed = graphics_data.get('animation_speed', 0.15)
                self.graphics.fade_duration = graphics_data.get('fade_duration', 0.5)
                self.graphics.battle_swirl_duration = graphics_data.get('battle_swirl_duration', 1.0)
                self.graphics.show_fps = graphics_data.get('show_fps', False)
                self.graphics.show_grid = graphics_data.get('show_grid', False)
            
            # Load controls settings
            if 'controls' in data:
                controls_data = data['controls']
                for key, value in controls_data.items():
                    if hasattr(self.controls, key):
                        setattr(self.controls, key, value)
            
            # Load gameplay settings  
            if 'gameplay' in data:
                gameplay_data = data['gameplay']
                for key, value in gameplay_data.items():
                    if hasattr(self.gameplay, key):
                        setattr(self.gameplay, key, value)
            
            print(f"Settings loaded from {self.settings_path}")
            return True
            
        except Exception as e:
            print(f"Error loading settings: {e}")
            return False
    
    def save_settings(self) -> bool:
        """
        Save current settings to TOML file.
        
        Returns:
            True if saved successfully, False otherwise
        """
        if not TOML_AVAILABLE:
            print("TOML not available, cannot save settings")
            return False
        
        try:
            # Create backup
            if self.settings_path.exists():
                backup_path = self.settings_path.with_suffix('.toml.backup')
                import shutil
                shutil.copy2(self.settings_path, backup_path)
            
            # Prepare data for saving
            data = {
                'game': {
                    'title': "Untold Story",
                    'version': "1.0.0", 
                    'author': "Ruhrpott Games",
                    'language': "de_DE"
                },
                'display': {
                    'logical_width': self.display.logical_width,
                    'logical_height': self.display.logical_height,
                    'window_scale': self.display.window_scale,
                    'fullscreen': self.display.fullscreen,
                    'vsync': self.display.vsync,
                    'target_fps': self.display.target_fps
                },
                'audio': {
                    'master_volume': self.audio.master_volume,
                    'bgm_volume': self.audio.bgm_volume,
                    'sfx_volume': self.audio.sfx_volume,
                    'channels': self.audio.channels,
                    'bgm_fade_in': self.audio.bgm_fade_in,
                    'bgm_fade_out': self.audio.bgm_fade_out
                },
                'graphics': {
                    'text_speed': self.graphics.text_speed.value,
                    'text_speed_multiplier': self.graphics.text_speed_multiplier,
                    'animation_speed': self.graphics.animation_speed,
                    'fade_duration': self.graphics.fade_duration,
                    'battle_swirl_duration': self.graphics.battle_swirl_duration,
                    'show_fps': self.graphics.show_fps,
                    'show_grid': self.graphics.show_grid
                },
                'controls': {
                    'move_up': self.controls.move_up,
                    'move_down': self.controls.move_down,
                    'move_left': self.controls.move_left,
                    'move_right': self.controls.move_right,
                    'confirm': self.controls.confirm,
                    'cancel': self.controls.cancel,
                    'run': self.controls.run,
                    'pause': self.controls.pause,
                    'debug': self.controls.debug
                },
                'gameplay': {
                    'difficulty': self.gameplay.difficulty,
                    'enemy_level_scaling': self.gameplay.enemy_level_scaling,
                    'exp_multiplier': self.gameplay.exp_multiplier,
                    'money_multiplier': self.gameplay.money_multiplier,
                    'grass_encounter_rate': self.gameplay.grass_encounter_rate,
                    'cave_encounter_rate': self.gameplay.cave_encounter_rate,
                    'water_encounter_rate': self.gameplay.water_encounter_rate,
                    'battle_animations': self.gameplay.battle_animations,
                    'show_damage_numbers': self.gameplay.show_damage_numbers,
                    'auto_save_before_boss': self.gameplay.auto_save_before_boss
                }
            }
            
            # Write to file
            with open(self.settings_path, 'w', encoding='utf-8') as f:
                toml.dump(data, f)
            
            print(f"Settings saved to {self.settings_path}")
            return True
            
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def toggle_music(self) -> bool:
        """
        Toggle music on/off.
        
        Returns:
            True if music is now enabled, False if disabled
        """
        self.audio.music_enabled = not self.audio.music_enabled
        return self.audio.music_enabled
    
    def toggle_sound(self) -> bool:
        """
        Toggle sound effects on/off.
        
        Returns:
            True if sound is now enabled, False if disabled
        """
        self.audio.sound_enabled = not self.audio.sound_enabled
        return self.audio.sound_enabled
    
    def set_text_speed(self, speed: TextSpeed) -> None:
        """Set text speed."""
        self.graphics.text_speed = speed
    
    def cycle_text_speed(self) -> TextSpeed:
        """
        Cycle through text speeds.
        
        Returns:
            New text speed
        """
        speeds = list(TextSpeed)
        current_index = speeds.index(self.graphics.text_speed)
        next_index = (current_index + 1) % len(speeds)
        self.graphics.text_speed = speeds[next_index]
        return self.graphics.text_speed
    
    def get_effective_music_volume(self) -> float:
        """Get effective music volume (accounting for enable state)."""
        if not self.audio.music_enabled:
            return 0.0
        return self.audio.master_volume * self.audio.bgm_volume
    
    def get_effective_sfx_volume(self) -> float:
        """Get effective SFX volume (accounting for enable state)."""
        if not self.audio.sound_enabled:
            return 0.0
        return self.audio.master_volume * self.audio.sfx_volume
    
    def get_effective_ui_volume(self) -> float:
        """Get effective UI volume (accounting for enable state)."""
        if not self.audio.sound_enabled:
            return 0.0
        return self.audio.master_volume * self.audio.ui_volume
    
    def apply_audio_settings(self, audio_manager) -> None:
        """
        Apply current audio settings to audio manager.
        
        Args:
            audio_manager: AudioManager instance
        """
        from engine.audio.audio_manager import AudioChannel
        
        # Set master volume
        audio_manager.set_master_volume(self.audio.master_volume)
        
        # Set channel volumes
        music_volume = self.audio.bgm_volume if self.audio.music_enabled else 0.0
        sfx_volume = self.audio.sfx_volume if self.audio.sound_enabled else 0.0
        ui_volume = self.audio.ui_volume if self.audio.sound_enabled else 0.0
        
        audio_manager.set_channel_volume(AudioChannel.MUSIC, music_volume)
        audio_manager.set_channel_volume(AudioChannel.SFX, sfx_volume)
        audio_manager.set_channel_volume(AudioChannel.UI, ui_volume)
        audio_manager.set_channel_volume(AudioChannel.VOICE, sfx_volume)
        audio_manager.set_channel_volume(AudioChannel.AMBIENT, sfx_volume * 0.6)
    
    def get_debug_info(self) -> Dict[str, Any]:
        """Get debug information about settings."""
        return {
            'settings_path': str(self.settings_path),
            'toml_available': TOML_AVAILABLE,
            'music_enabled': self.audio.music_enabled,
            'sound_enabled': self.audio.sound_enabled,
            'master_volume': self.audio.master_volume,
            'bgm_volume': self.audio.bgm_volume,
            'sfx_volume': self.audio.sfx_volume,
            'text_speed': self.graphics.text_speed.value,
            'window_size': f"{self.display.window_width}x{self.display.window_height}",
            'fullscreen': self.display.fullscreen
        }
