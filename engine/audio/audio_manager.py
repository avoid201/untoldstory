"""
Audio Manager für Untold Story
Erweiterte Audio-Verwaltung mit Kanälen, Fading und Mix-Kontrolle
"""

import pygame
import threading
from typing import Dict, Optional, List, Tuple
from pathlib import Path
from enum import Enum


class AudioChannel(Enum):
    """Audio channel types for organization"""
    MUSIC = "music"
    SFX = "sfx" 
    VOICE = "voice"
    AMBIENT = "ambient"
    UI = "ui"


class AudioManager:
    """Enhanced audio manager with channel mixing and advanced features"""
    
    def __init__(self, frequency: int = 44100, channels: int = 2, buffer_size: int = 512):
        """
        Initialize audio manager.
        
        Args:
            frequency: Audio frequency in Hz
            channels: Number of audio channels (1=mono, 2=stereo)
            buffer_size: Audio buffer size
        """
        # Initialize pygame mixer
        try:
            pygame.mixer.pre_init(frequency=frequency, size=-16, channels=channels, buffer=buffer_size)
            pygame.mixer.init()
            print(f"Audio Manager initialized: {frequency}Hz, {channels}ch, buffer={buffer_size}")
        except pygame.error as e:
            print(f"Warning: Audio initialization failed: {e}")
            self.audio_available = False
            return
        
        self.audio_available = True
        
        # Audio settings
        self.master_volume = 1.0
        self.channel_volumes = {
            AudioChannel.MUSIC: 0.7,
            AudioChannel.SFX: 0.8,
            AudioChannel.VOICE: 0.9,
            AudioChannel.AMBIENT: 0.5,
            AudioChannel.UI: 0.6
        }
        
        # Sound cache and channel management
        self.sound_cache: Dict[str, pygame.mixer.Sound] = {}
        self.music_queue: List[str] = []
        self.current_music: Optional[str] = None
        self.music_looping = True
        
        # Reserve pygame channels for different purposes
        self.reserved_channels = {
            AudioChannel.SFX: list(range(0, 4)),      # 4 SFX channels
            AudioChannel.VOICE: [4],                   # 1 voice channel
            AudioChannel.AMBIENT: [5],                 # 1 ambient channel
            AudioChannel.UI: [6, 7]                    # 2 UI channels
        }
        
        # Channel states
        self.channel_states: Dict[int, Dict] = {}
        
        # Fade states
        self.fade_threads: Dict[str, threading.Thread] = {}
        
        # Audio paths
        from engine.core.resources import ResourceManager
        self.resources = ResourceManager()
        
        print(f"Audio channels available: {pygame.mixer.get_num_channels()}")
    
    def set_master_volume(self, volume: float) -> None:
        """Set master volume (0.0 to 1.0)"""
        self.master_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.master_volume * self.channel_volumes[AudioChannel.MUSIC])
    
    def set_channel_volume(self, channel: AudioChannel, volume: float) -> None:
        """Set volume for a specific audio channel"""
        self.channel_volumes[channel] = max(0.0, min(1.0, volume))
        
        # Update music volume if it's the music channel
        if channel == AudioChannel.MUSIC and self.current_music:
            pygame.mixer.music.set_volume(self.master_volume * volume)
    
    def get_effective_volume(self, channel: AudioChannel) -> float:
        """Calculate effective volume combining master and channel volume"""
        return self.master_volume * self.channel_volumes[channel]
    
    def load_sound(self, path: str, cache: bool = True) -> Optional[pygame.mixer.Sound]:
        """
        Load a sound effect with caching.
        
        Args:
            path: Relative path from sfx directory
            cache: Whether to cache the sound
            
        Returns:
            pygame Sound object or None if failed
        """
        if not self.audio_available:
            return None
        
        # Check cache first
        if cache and path in self.sound_cache:
            return self.sound_cache[path]
        
        try:
            sound = self.resources.load_sound(path)
            if cache:
                self.sound_cache[path] = sound
            return sound
        except Exception as e:
            print(f"Failed to load sound {path}: {e}")
            return None
    
    def play_sound(self, path: str, channel: AudioChannel = AudioChannel.SFX, 
                   volume: float = 1.0, loops: int = 0, fade_in: float = 0.0) -> Optional[pygame.mixer.Channel]:
        """
        Play a sound effect on specified channel.
        
        Args:
            path: Sound file path
            channel: Audio channel type
            volume: Sound volume (0.0 to 1.0)
            loops: Number of loops (0 = play once)
            fade_in: Fade in duration in seconds
            
        Returns:
            pygame Channel object or None
        """
        if not self.audio_available:
            return None
        
        sound = self.load_sound(path)
        if not sound:
            return None
        
        # Get available channel for this type
        pygame_channel = self._get_available_channel(channel)
        if not pygame_channel:
            return None
        
        # Set volume
        effective_volume = self.get_effective_volume(channel) * volume
        sound.set_volume(effective_volume)
        
        try:
            if fade_in > 0:
                pygame_channel.play(sound, loops=loops, fade_ms=int(fade_in * 1000))
            else:
                pygame_channel.play(sound, loops=loops)
            
            # Track channel state
            self.channel_states[pygame_channel.get_channel()] = {
                'type': channel,
                'path': path,
                'volume': volume
            }
            
            return pygame_channel
            
        except Exception as e:
            print(f"Failed to play sound {path}: {e}")
            return None
    
    def play_music(self, path: str, loops: int = -1, fade_in: float = 0.0, 
                   queue: bool = False) -> bool:
        """
        Play background music.
        
        Args:
            path: Music file path
            loops: Number of loops (-1 = infinite)
            fade_in: Fade in duration in seconds
            queue: Add to queue instead of playing immediately
            
        Returns:
            True if successful
        """
        if not self.audio_available:
            return False
        
        if queue:
            self.music_queue.append(path)
            return True
        
        try:
            # Stop current music if playing
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
            
            # Load and play new music
            music_path = self.resources.bgm_path / path
            if not music_path.exists():
                print(f"Music file not found: {music_path}")
                return False
            
            pygame.mixer.music.load(str(music_path))
            
            # Set volume
            volume = self.get_effective_volume(AudioChannel.MUSIC)
            pygame.mixer.music.set_volume(volume)
            
            # Play with fade in
            if fade_in > 0:
                pygame.mixer.music.play(loops, fade_ms=int(fade_in * 1000))
            else:
                pygame.mixer.music.play(loops)
            
            self.current_music = path
            self.music_looping = (loops != 0)
            return True
            
        except Exception as e:
            print(f"Failed to play music {path}: {e}")
            return False
    
    def stop_music(self, fade_out: float = 0.0) -> None:
        """Stop background music with optional fade out"""
        if not self.audio_available:
            return
        
        if fade_out > 0:
            pygame.mixer.music.fadeout(int(fade_out * 1000))
        else:
            pygame.mixer.music.stop()
        
        self.current_music = None
    
    def pause_music(self) -> None:
        """Pause background music"""
        if self.audio_available and pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
    
    def unpause_music(self) -> None:
        """Unpause background music"""
        if self.audio_available:
            pygame.mixer.music.unpause()
    
    def stop_all_sounds(self, channel: Optional[AudioChannel] = None, fade_out: float = 0.0) -> None:
        """
        Stop all sounds on specified channel or all channels.
        
        Args:
            channel: Specific channel to stop (None = all)
            fade_out: Fade out duration in seconds
        """
        if not self.audio_available:
            return
        
        if channel is None:
            # Stop all channels
            if fade_out > 0:
                pygame.mixer.fadeout(int(fade_out * 1000))
            else:
                pygame.mixer.stop()
        else:
            # Stop specific channel type
            for channel_id in self.reserved_channels.get(channel, []):
                pygame_channel = pygame.mixer.Channel(channel_id)
                if pygame_channel.get_busy():
                    if fade_out > 0:
                        pygame_channel.fadeout(int(fade_out * 1000))
                    else:
                        pygame_channel.stop()
    
    def _get_available_channel(self, channel_type: AudioChannel) -> Optional[pygame.mixer.Channel]:
        """Get an available pygame channel for the specified type"""
        reserved = self.reserved_channels.get(channel_type, [])
        
        # Try reserved channels first
        for channel_id in reserved:
            pygame_channel = pygame.mixer.Channel(channel_id)
            if not pygame_channel.get_busy():
                return pygame_channel
        
        # If no reserved channel available, try any channel
        return pygame.mixer.find_channel()
    
    def update(self) -> None:
        """Update audio manager state - call once per frame"""
        # Check if music ended and handle queue
        if (self.audio_available and not pygame.mixer.music.get_busy() and 
            self.current_music and not self.music_looping and self.music_queue):
            next_track = self.music_queue.pop(0)
            self.play_music(next_track)
        
        # Clean up finished channel states
        finished_channels = []
        for channel_id, state in self.channel_states.items():
            pygame_channel = pygame.mixer.Channel(channel_id)
            if not pygame_channel.get_busy():
                finished_channels.append(channel_id)
        
        for channel_id in finished_channels:
            del self.channel_states[channel_id]
    
    def get_audio_info(self) -> Dict:
        """Get debug information about audio state"""
        return {
            'audio_available': self.audio_available,
            'master_volume': self.master_volume,
            'channel_volumes': {ch.value: vol for ch, vol in self.channel_volumes.items()},
            'current_music': self.current_music,
            'music_queue_length': len(self.music_queue),
            'active_channels': len(self.channel_states),
            'cached_sounds': len(self.sound_cache)
        }
    
    def preload_sounds(self, sound_list: List[str]) -> None:
        """Preload a list of sounds for faster playback"""
        for sound_path in sound_list:
            self.load_sound(sound_path, cache=True)
        print(f"Preloaded {len(sound_list)} sounds")
    
    def clear_cache(self) -> None:
        """Clear the sound cache to free memory"""
        self.sound_cache.clear()
        print("Sound cache cleared")
