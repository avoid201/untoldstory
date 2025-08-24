"""
Weather System for Untold Story
Handles weather transitions, animations, and ability interactions
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum, auto
import random
import json

from .field_effects import WeatherEffect, WeatherType, FieldEffectManager


class WeatherTransition(Enum):
    """Types of weather transitions."""
    INSTANT = "instant"
    FADE_IN = "fade_in"
    GRADUAL = "gradual"
    STORM_BUILDUP = "storm_buildup"


@dataclass
class WeatherAnimation:
    """Weather animation configuration."""
    animation_id: str
    duration_frames: int
    particle_count: int
    color_scheme: List[str]
    sound_effect: Optional[str] = None
    screen_overlay: Optional[str] = None


class WeatherSystem:
    """Manages weather mechanics and transitions."""
    
    def __init__(self):
        """Initialize weather system."""
        self.weather_animations: Dict[WeatherType, WeatherAnimation] = {}
        self.weather_setters: Dict[str, WeatherType] = {}
        self.indoor_restrictions: Dict[str, bool] = {}
        self._setup_default_animations()
        self._setup_weather_setters()
    
    def _setup_default_animations(self):
        """Setup default weather animations."""
        self.weather_animations = {
            WeatherType.SUNNY: WeatherAnimation(
                animation_id="sunny_animation",
                duration_frames=120,
                particle_count=20,
                color_scheme=["#FFD700", "#FFA500", "#FFFF00"],
                sound_effect="sunny_ambience.ogg",
                screen_overlay="bright_overlay"
            ),
            WeatherType.RAIN: WeatherAnimation(
                animation_id="rain_animation",
                duration_frames=90,
                particle_count=100,
                color_scheme=["#4169E1", "#1E90FF", "#87CEEB"],
                sound_effect="rain_ambience.ogg",
                screen_overlay="dark_overlay"
            ),
            WeatherType.SANDSTORM: WeatherAnimation(
                animation_id="sandstorm_animation",
                duration_frames=60,
                particle_count=150,
                color_scheme=["#D2B48C", "#CD853F", "#8B4513"],
                sound_effect="sandstorm_ambience.ogg",
                screen_overlay="brown_overlay"
            ),
            WeatherType.HAIL: WeatherAnimation(
                animation_id="hail_animation",
                duration_frames=75,
                particle_count=80,
                color_scheme=["#F0F8FF", "#E6E6FA", "#FFFFFF"],
                sound_effect="hail_ambience.ogg",
                screen_overlay="white_overlay"
            ),
            WeatherType.FOG: WeatherAnimation(
                animation_id="fog_animation",
                duration_frames=180,
                particle_count=50,
                color_scheme=["#C0C0C0", "#A9A9A9", "#808080"],
                sound_effect="fog_ambience.ogg",
                screen_overlay="fog_overlay"
            )
        }
    
    def _setup_weather_setters(self):
        """Setup monsters that can set weather."""
        self.weather_setters = {
            "sonnenkönig": WeatherType.SUNNY,
            "regenherr": WeatherType.RAIN,
            "sandsturm": WeatherType.SANDSTORM,
            "eisriese": WeatherType.HAIL,
            "nebelgeist": WeatherType.FOG
        }
    
    def get_weather_animation(self, weather_type: WeatherType) -> Optional[WeatherAnimation]:
        """Get animation configuration for weather type."""
        return self.weather_animations.get(weather_type)
    
    def can_set_weather(self, monster_species: str) -> Optional[WeatherType]:
        """Check if monster can set weather and what type."""
        return self.weather_setters.get(monster_species.lower())
    
    def is_weather_restricted(self, location: str) -> bool:
        """Check if weather is restricted at location."""
        return self.indoor_restrictions.get(location, False)
    
    def set_indoor_restriction(self, location: str, restricted: bool):
        """Set weather restriction for a location."""
        self.indoor_restrictions[location] = restricted
    
    def calculate_weather_damage(self, 
                               base_damage: int, 
                               move_type: str, 
                               weather: Optional[WeatherEffect]) -> int:
        """Calculate weather-modified damage."""
        if not weather:
            return base_damage
        
        return weather.modify_damage(base_damage, move_type)
    
    def calculate_weather_accuracy(self, 
                                 base_accuracy: float, 
                                 move_type: str, 
                                 weather: Optional[WeatherEffect]) -> float:
        """Calculate weather-modified accuracy."""
        if not weather:
            return base_accuracy
        
        return weather.modify_accuracy(base_accuracy, move_type)
    
    def get_weather_immunity(self, 
                           monster_type: str, 
                           weather: Optional[WeatherEffect]) -> bool:
        """Check if monster type is immune to weather damage."""
        if not weather:
            return False
        
        return weather.check_immunity(monster_type)
    
    def get_end_turn_weather_damage(self, 
                                   monster_type: str, 
                                   max_hp: int, 
                                   weather: Optional[WeatherEffect]) -> int:
        """Calculate end-turn weather damage."""
        if not weather:
            return 0
        
        return weather.get_end_turn_damage(monster_type, max_hp)
    
    def create_weather_effect(self, 
                            weather_type: WeatherType, 
                            duration: int = 5,
                            is_legendary: bool = False) -> WeatherEffect:
        """Create a weather effect with appropriate duration."""
        # Legendary monsters set longer-lasting weather
        if is_legendary:
            duration = max(duration, 8)
        
        return WeatherEffect(
            effect_id=f"{weather_type.value}_weather",
            weather_type=weather_type,
            name=self._get_weather_name(weather_type),
            description=self._get_weather_description(weather_type),
            duration=duration
        )
    
    def _get_weather_name(self, weather_type: WeatherType) -> str:
        """Get German name for weather type."""
        names = {
            WeatherType.CLEAR: "Klar",
            WeatherType.SUNNY: "Sonnenschein",
            WeatherType.RAIN: "Regen",
            WeatherType.SANDSTORM: "Sandsturm",
            WeatherType.HAIL: "Hagel",
            WeatherType.FOG: "Nebel"
        }
        return names.get(weather_type, "Unbekannt")
    
    def _get_weather_description(self, weather_type: WeatherType) -> str:
        """Get German description for weather type."""
        descriptions = {
            WeatherType.CLEAR: "Das Wetter ist klar und normal.",
            WeatherType.SUNNY: "Die Sonne scheint hell! Feuer-Attacken sind verstärkt, Wasser-Attacken geschwächt.",
            WeatherType.RAIN: "Es regnet! Wasser-Attacken sind verstärkt, Feuer-Attacken geschwächt.",
            WeatherType.SANDSTORM: "Ein Sandsturm tobt! Erd-Typen sind immun, andere nehmen Schaden.",
            WeatherType.HAIL: "Es hagelt! Luft-Typen sind immun, andere nehmen Schaden.",
            WeatherType.FOG: "Nebel liegt über dem Feld! Alle Attacken haben -20% Genauigkeit."
        }
        return descriptions.get(weather_type, "Unbekanntes Wetter.")
    
    def get_weather_transition_type(self, 
                                  old_weather: Optional[WeatherType], 
                                  new_weather: WeatherType) -> WeatherTransition:
        """Determine transition type between weather states."""
        if not old_weather:
            return WeatherTransition.INSTANT
        
        if new_weather == WeatherType.CLEAR:
            return WeatherTransition.FADE_IN
        
        if new_weather in [WeatherType.SANDSTORM, WeatherType.HAIL]:
            return WeatherTransition.STORM_BUILDUP
        
        return WeatherTransition.GRADUAL
    
    def get_weather_particles(self, 
                            weather_type: WeatherType, 
                            frame_count: int) -> List[Dict[str, Any]]:
        """Generate particle positions for weather animation."""
        particles = []
        animation = self.weather_animations.get(weather_type)
        
        if not animation:
            return particles
        
        for i in range(animation.particle_count):
            particle = {
                "x": random.randint(0, 320),  # Logical resolution width
                "y": random.randint(0, 180),  # Logical resolution height
                "speed_x": random.uniform(-1, 1),
                "speed_y": random.uniform(1, 3),
                "life": random.randint(30, 90),
                "color": random.choice(animation.color_scheme),
                "size": random.randint(1, 3)
            }
            particles.append(particle)
        
        return particles
    
    def get_weather_sound_effect(self, weather_type: WeatherType) -> Optional[str]:
        """Get sound effect filename for weather type."""
        animation = self.weather_animations.get(weather_type)
        return animation.sound_effect if animation else None
    
    def get_weather_overlay(self, weather_type: WeatherType) -> Optional[str]:
        """Get screen overlay for weather type."""
        animation = self.weather_animations.get(weather_type)
        return animation.screen_overlay if animation else None
    
    def is_weather_beneficial(self, 
                            weather_type: WeatherType, 
                            monster_type: str) -> bool:
        """Check if weather is beneficial for monster type."""
        beneficial_combinations = {
            WeatherType.SUNNY: ["feuer"],
            WeatherType.RAIN: ["wasser"],
            WeatherType.SANDSTORM: ["erde"],
            WeatherType.HAIL: ["luft"]
        }
        
        return monster_type in beneficial_combinations.get(weather_type, [])
    
    def is_weather_harmful(self, 
                          weather_type: WeatherType, 
                          monster_type: str) -> bool:
        """Check if weather is harmful for monster type."""
        harmful_combinations = {
            WeatherType.SUNNY: ["wasser"],
            WeatherType.RAIN: ["feuer"],
            WeatherType.SANDSTORM: ["feuer", "wasser", "pflanze", "luft", "energie", "mystik", "chaos", "zeit"],
            WeatherType.HAIL: ["feuer", "wasser", "pflanze", "erde", "energie", "mystik", "chaos", "zeit"]
        }
        
        return monster_type in harmful_combinations.get(weather_type, [])
    
    def get_weather_intensity(self, 
                            weather_type: WeatherType, 
                            is_legendary: bool = False) -> float:
        """Get weather intensity multiplier."""
        base_intensity = 1.0
        
        if weather_type == WeatherType.SANDSTORM:
            base_intensity = 1.2
        elif weather_type == WeatherType.HAIL:
            base_intensity = 1.1
        
        if is_legendary:
            base_intensity *= 1.5
        
        return base_intensity
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "weather_animations": {
                weather.value: {
                    "animation_id": anim.animation_id,
                    "duration_frames": anim.duration_frames,
                    "particle_count": anim.particle_count,
                    "color_scheme": anim.color_scheme,
                    "sound_effect": anim.sound_effect,
                    "screen_overlay": anim.screen_overlay
                }
                for weather, anim in self.weather_animations.items()
            },
            "weather_setters": self.weather_setters,
            "indoor_restrictions": self.indoor_restrictions
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WeatherSystem':
        """Create from dictionary."""
        system = cls()
        
        # Restore weather animations
        for weather_str, anim_data in data.get("weather_animations", {}).items():
            try:
                weather_type = WeatherType(weather_str)
                animation = WeatherAnimation(**anim_data)
                system.weather_animations[weather_type] = animation
            except (KeyError, ValueError):
                continue
        
        # Restore other data
        system.weather_setters = data.get("weather_setters", {})
        system.indoor_restrictions = data.get("indoor_restrictions", {})
        
        return system


# Weather effect factory functions
def create_weather_from_move(move_name: str, duration: int = 5) -> Optional[WeatherEffect]:
    """Create weather effect from move name."""
    weather_moves = {
        "sonnentag": WeatherType.SUNNY,
        "regentanz": WeatherType.RAIN,
        "sandsturm": WeatherType.SANDSTORM,
        "hagelsturm": WeatherType.HAIL,
        "nebelwand": WeatherType.FOG
    }
    
    weather_type = weather_moves.get(move_name.lower())
    if weather_type:
        system = WeatherSystem()
        return system.create_weather_effect(weather_type, duration)
    
    return None


def create_weather_from_ability(ability_name: str, duration: int = 8) -> Optional[WeatherEffect]:
    """Create weather effect from ability name."""
    weather_abilities = {
        "dürre": WeatherType.SUNNY,
        "regenguss": WeatherType.RAIN,
        "sandsturm": WeatherType.SANDSTORM,
        "schneesturm": WeatherType.HAIL
    }
    
    weather_type = weather_abilities.get(ability_name.lower())
    if weather_type:
        system = WeatherSystem()
        return system.create_weather_effect(weather_type, duration, is_legendary=True)
    
    return None
