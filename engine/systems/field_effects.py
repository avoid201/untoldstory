"""
Field Effects System for Untold Story
Handles weather, terrain, and special battlefield modifiers
"""

from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum, auto
import random
import json


class EffectCategory(Enum):
    """Categories of field effects."""
    WEATHER = "weather"
    TERRAIN = "terrain"
    SPECIAL = "special"


class WeatherType(Enum):
    """Available weather conditions."""
    CLEAR = "clear"
    SUNNY = "sunny"
    RAIN = "rain"
    SANDSTORM = "sandstorm"
    HAIL = "hail"
    FOG = "fog"


class TerrainType(Enum):
    """Available terrain types."""
    NORMAL = "normal"
    GRASSY = "grassy"
    ELECTRIC = "electric"
    PSYCHIC = "psychic"
    MISTY = "misty"


class SpecialEffectType(Enum):
    """Special battlefield effects."""
    ZEITRISS = "zeitriss"
    GRAVITY = "gravity"
    TRICK_ROOM = "trick_room"


@dataclass
class FieldEffect:
    """Base class for all field effects."""
    effect_id: str
    category: EffectCategory
    name: str
    description: str
    duration: int = 5
    turns_remaining: int = 5
    is_indoor_restricted: bool = False
    visual_effects: List[str] = field(default_factory=list)
    
    def is_active(self) -> bool:
        """Check if effect is still active."""
        return self.turns_remaining > 0
    
    def advance_turn(self) -> None:
        """Advance effect by one turn."""
        if self.turns_remaining > 0:
            self.turns_remaining -= 1
    
    def extend_duration(self, additional_turns: int) -> None:
        """Extend effect duration."""
        self.duration += additional_turns
        self.turns_remaining += additional_turns
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "effect_id": self.effect_id,
            "category": self.category.value,
            "name": self.name,
            "description": self.description,
            "duration": self.duration,
            "turns_remaining": self.turns_remaining,
            "is_indoor_restricted": self.is_indoor_restricted,
            "visual_effects": self.visual_effects
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FieldEffect':
        """Create from dictionary."""
        data["category"] = EffectCategory(data["category"])
        return cls(**data)


@dataclass
class WeatherEffect(FieldEffect):
    """Weather-based field effect."""
    weather_type: WeatherType
    damage_modifiers: Dict[str, float] = field(default_factory=dict)
    accuracy_modifiers: Dict[str, float] = field(default_factory=dict)
    immunity_types: Set[str] = field(default_factory=set)
    end_turn_damage: float = 0.0
    end_turn_damage_types: Set[str] = field(default_factory=set)
    
    def __post_init__(self):
        """Initialize weather-specific properties."""
        self.category = EffectCategory.WEATHER
        self._setup_weather_properties()
    
    def _setup_weather_properties(self):
        """Setup weather-specific modifiers and effects."""
        if self.weather_type == WeatherType.SUNNY:
            self.damage_modifiers = {"feuer": 1.5, "wasser": 0.5}
            self.visual_effects = ["bright_overlay", "sun_rays"]
            
        elif self.weather_type == WeatherType.RAIN:
            self.damage_modifiers = {"wasser": 1.5, "feuer": 0.5}
            self.visual_effects = ["rain_drops", "dark_overlay"]
            
        elif self.weather_type == WeatherType.SANDSTORM:
            self.damage_modifiers = {"erde": 1.2}
            self.immunity_types = {"erde"}
            self.end_turn_damage = 1/16  # 1/16 max HP
            self.end_turn_damage_types = {"feuer", "wasser", "pflanze", "luft", "energie", "mystik", "chaos", "zeit"}
            self.visual_effects = ["sand_particles", "brown_overlay"]
            
        elif self.weather_type == WeatherType.HAIL:
            self.damage_modifiers = {"luft": 1.2}
            self.immunity_types = {"luft"}
            self.end_turn_damage = 1/16  # 1/16 max HP
            self.end_turn_damage_types = {"feuer", "wasser", "pflanze", "erde", "energie", "mystik", "chaos", "zeit"}
            self.visual_effects = ["hail_particles", "white_overlay"]
            
        elif self.weather_type == WeatherType.FOG:
            self.accuracy_modifiers = {"all": 0.8}  # -20% accuracy
            self.visual_effects = ["fog_overlay", "reduced_visibility"]
    
    def modify_damage(self, base_damage: int, move_type: str) -> int:
        """Modify damage based on weather."""
        if move_type in self.damage_modifiers:
            return int(base_damage * self.damage_modifiers[move_type])
        return base_damage
    
    def modify_accuracy(self, base_accuracy: float, move_type: str) -> float:
        """Modify accuracy based on weather."""
        if "all" in self.accuracy_modifiers:
            return base_accuracy * self.accuracy_modifiers["all"]
        if move_type in self.accuracy_modifiers:
            return base_accuracy * self.accuracy_modifiers[move_type]
        return base_accuracy
    
    def check_immunity(self, monster_type: str) -> bool:
        """Check if monster type is immune to weather damage."""
        return monster_type in self.immunity_types
    
    def get_end_turn_damage(self, monster_type: str, max_hp: int) -> int:
        """Calculate end-turn damage for non-immune types."""
        if monster_type in self.immunity_types:
            return 0
        if monster_type in self.end_turn_damage_types:
            return int(max_hp * self.end_turn_damage)
        return 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        base_dict = super().to_dict()
        base_dict.update({
            "weather_type": self.weather_type.value,
            "damage_modifiers": self.damage_modifiers,
            "accuracy_modifiers": self.accuracy_modifiers,
            "immunity_types": list(self.immunity_types),
            "end_turn_damage": self.end_turn_damage,
            "end_turn_damage_types": list(self.end_turn_damage_types)
        })
        return base_dict


@dataclass
class TerrainEffect(FieldEffect):
    """Terrain-based field effect."""
    terrain_type: TerrainType
    damage_modifiers: Dict[str, float] = field(default_factory=dict)
    status_immunities: Set[str] = field(default_factory=set)
    priority_block: bool = False
    hp_regen_percent: float = 0.0
    move_restrictions: Set[str] = field(default_factory=set)
    
    def __post_init__(self):
        """Initialize terrain-specific properties."""
        self.category = EffectCategory.TERRAIN
        self._setup_terrain_properties()
    
    def _setup_terrain_properties(self):
        """Setup terrain-specific modifiers and effects."""
        if self.terrain_type == TerrainType.GRASSY:
            self.damage_modifiers = {"pflanze": 1.3}
            self.hp_regen_percent = 0.0625  # 1/16 max HP per turn
            self.visual_effects = ["grass_particles", "green_glow"]
            
        elif self.terrain_type == TerrainType.ELECTRIC:
            self.damage_modifiers = {"energie": 1.3}
            self.status_immunities = {"sleep"}
            self.visual_effects = ["electric_sparks", "yellow_glow"]
            
        elif self.terrain_type == TerrainType.PSYCHIC:
            self.damage_modifiers = {"mystik": 1.3}
            self.priority_block = True
            self.visual_effects = ["psychic_waves", "purple_glow"]
            
        elif self.terrain_type == TerrainType.MISTY:
            self.damage_modifiers = {"chaos": 0.5}
            self.status_immunities = {"sleep", "poison", "burn", "freeze", "paralyze"}
            self.visual_effects = ["mist_particles", "pink_glow"]
    
    def modify_damage(self, base_damage: int, move_type: str) -> int:
        """Modify damage based on terrain."""
        if move_type in self.damage_modifiers:
            return int(base_damage * self.damage_modifiers[move_type])
        return base_damage
    
    def check_status_immunity(self, status: str) -> bool:
        """Check if terrain provides immunity to status."""
        return status in self.status_immunities
    
    def get_hp_regen(self, max_hp: int) -> int:
        """Calculate HP regeneration from terrain."""
        if self.hp_regen_percent > 0:
            return int(max_hp * self.hp_regen_percent)
        return 0
    
    def blocks_priority(self) -> bool:
        """Check if terrain blocks priority moves."""
        return self.priority_block
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        base_dict = super().to_dict()
        base_dict.update({
            "terrain_type": self.terrain_type.value,
            "damage_modifiers": self.damage_modifiers,
            "status_immunities": list(self.status_immunities),
            "priority_block": self.priority_block,
            "hp_regen_percent": self.hp_regen_percent,
            "move_restrictions": list(self.move_restrictions)
        })
        return base_dict


@dataclass
class SpecialEffect(FieldEffect):
    """Special battlefield effect."""
    effect_type: SpecialEffectType
    effect_data: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize special effect properties."""
        self.category = EffectCategory.SPECIAL
        self._setup_special_properties()
    
    def _setup_special_properties(self):
        """Setup special effect properties."""
        if self.effect_type == SpecialEffectType.ZEITRISS:
            self.description = "Ein Zeitriss öffnet sich! Die Realität verzerrt sich..."
            self.visual_effects = ["time_distortion", "reality_shift", "future_monsters"]
            self.effect_data = {
                "type_changes": True,
                "future_monsters": True,
                "random_effects": True
            }
            
        elif self.effect_type == SpecialEffectType.GRAVITY:
            self.description = "Schwere Gravitation! Flug-Immunitäten werden aufgehoben."
            self.visual_effects = ["gravity_pull", "heavy_air"]
            self.effect_data = {
                "flying_immunity_removed": True,
                "ground_moves_effective": True
            }
            
        elif self.effect_type == SpecialEffectType.TRICK_ROOM:
            self.description = "Ein Trick Room! Die Geschwindigkeits-Reihenfolge wird umgekehrt."
            self.visual_effects = ["room_distortion", "speed_reversal"]
            self.effect_data = {
                "speed_reversed": True,
                "priority_ignored": True
            }
    
    def apply_special_effect(self, battle_context: Any) -> Dict[str, Any]:
        """Apply special effect to battle context."""
        if self.effect_type == SpecialEffectType.ZEITRISS:
            return self._apply_zeitriss_effect(battle_context)
        elif self.effect_type == SpecialEffectType.GRAVITY:
            return self._apply_gravity_effect(battle_context)
        elif self.effect_type == SpecialEffectType.TRICK_ROOM:
            return self._apply_trick_room_effect(battle_context)
        return {}
    
    def _apply_zeitriss_effect(self, battle_context: Any) -> Dict[str, Any]:
        """Apply Zeitriss special effects."""
        effects = {}
        
        # Random type changes (story progression dependent)
        if battle_context.get("story_progress", 0) >= 50:  # Mid-game
            effects["type_changes"] = True
            effects["message"] = "Die Typen der Monster verändern sich!"
        
        # Future monsters appear (late-game)
        if battle_context.get("story_progress", 0) >= 80:
            effects["future_monsters"] = True
            effects["message"] = "Monster aus der Zukunft erscheinen!"
        
        return effects
    
    def _apply_gravity_effect(self, battle_context: Any) -> Dict[str, Any]:
        """Apply Gravity special effects."""
        return {
            "flying_immunity_removed": True,
            "ground_moves_effective": True,
            "message": "Flug-Immunitäten sind aufgehoben!"
        }
    
    def _apply_trick_room_effect(self, battle_context: Any) -> Dict[str, Any]:
        """Apply Trick Room special effects."""
        return {
            "speed_reversed": True,
            "priority_ignored": True,
            "message": "Die Geschwindigkeits-Reihenfolge ist umgekehrt!"
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        base_dict = super().to_dict()
        base_dict.update({
            "effect_type": self.effect_type.value,
            "effect_data": self.effect_data
        })
        return base_dict


class FieldEffectManager:
    """Manages all active field effects in battle."""
    
    def __init__(self):
        """Initialize field effect manager."""
        self.active_effects: Dict[EffectCategory, Optional[FieldEffect]] = {
            EffectCategory.WEATHER: None,
            EffectCategory.TERRAIN: None,
            EffectCategory.SPECIAL: None
        }
        self.effect_history: List[FieldEffect] = []
        self.is_indoor_battle: bool = False
    
    def add_effect(self, effect: FieldEffect) -> bool:
        """
        Add a new field effect.
        
        Args:
            effect: Field effect to add
            
        Returns:
            True if effect was added successfully
        """
        # Check indoor restrictions
        if effect.is_indoor_restricted and self.is_indoor_battle:
            return False
        
        # Replace existing effect of same category
        if effect.category in self.active_effects:
            old_effect = self.active_effects[effect.category]
            if old_effect:
                self.effect_history.append(old_effect)
        
        self.active_effects[effect.category] = effect
        return True
    
    def remove_effect(self, category: EffectCategory) -> Optional[FieldEffect]:
        """
        Remove a field effect.
        
        Args:
            category: Category of effect to remove
            
        Returns:
            Removed effect or None
        """
        effect = self.active_effects.get(category)
        if effect:
            self.active_effects[category] = None
            self.effect_history.append(effect)
        return effect
    
    def get_effect(self, category: EffectCategory) -> Optional[FieldEffect]:
        """Get active effect of specified category."""
        return self.active_effects.get(category)
    
    def get_weather(self) -> Optional[WeatherEffect]:
        """Get current weather effect."""
        effect = self.active_effects.get(EffectCategory.WEATHER)
        return effect if isinstance(effect, WeatherEffect) else None
    
    def get_terrain(self) -> Optional[TerrainEffect]:
        """Get current terrain effect."""
        effect = self.active_effects.get(EffectCategory.TERRAIN)
        return effect if isinstance(effect, TerrainEffect) else None
    
    def get_special_effect(self) -> Optional[SpecialEffect]:
        """Get current special effect."""
        effect = self.active_effects.get(EffectCategory.SPECIAL)
        return effect if isinstance(effect, SpecialEffect) else None
    
    def advance_turn(self) -> List[FieldEffect]:
        """Advance all effects by one turn and return expired effects."""
        expired_effects = []
        
        for category, effect in self.active_effects.items():
            if effect:
                effect.advance_turn()
                if not effect.is_active():
                    expired_effects.append(effect)
                    self.active_effects[category] = None
        
        return expired_effects
    
    def modify_damage(self, base_damage: int, move_type: str) -> int:
        """Apply all damage modifiers from active effects."""
        damage = base_damage
        
        # Weather damage modifier
        weather = self.get_weather()
        if weather:
            damage = weather.modify_damage(damage, move_type)
        
        # Terrain damage modifier
        terrain = self.get_terrain()
        if terrain:
            damage = terrain.modify_damage(damage, move_type)
        
        return damage
    
    def modify_accuracy(self, base_accuracy: float, move_type: str) -> float:
        """Apply all accuracy modifiers from active effects."""
        accuracy = base_accuracy
        
        # Weather accuracy modifier
        weather = self.get_weather()
        if weather:
            accuracy = weather.modify_accuracy(accuracy, move_type)
        
        return accuracy
    
    def check_immunities(self, monster_type: str, status: str = None) -> Dict[str, bool]:
        """Check all immunities from active effects."""
        immunities = {
            "weather_damage": False,
            "status": False
        }
        
        # Weather immunity
        weather = self.get_weather()
        if weather:
            immunities["weather_damage"] = weather.check_immunity(monster_type)
        
        # Terrain status immunity
        terrain = self.get_terrain()
        if terrain and status:
            immunities["status"] = terrain.check_status_immunity(status)
        
        return immunities
    
    def apply_end_turn_effects(self, monster_type: str, max_hp: int) -> Dict[str, int]:
        """Apply end-of-turn effects from active effects."""
        effects = {
            "damage": 0,
            "healing": 0
        }
        
        # Weather end-turn damage
        weather = self.get_weather()
        if weather:
            effects["damage"] += weather.get_end_turn_damage(monster_type, max_hp)
        
        # Terrain HP regeneration
        terrain = self.get_terrain()
        if terrain:
            effects["healing"] += terrain.get_hp_regen(max_hp)
        
        return effects
    
    def get_visual_effects(self) -> List[str]:
        """Get all active visual effects."""
        visual_effects = []
        
        for effect in self.active_effects.values():
            if effect:
                visual_effects.extend(effect.visual_effects)
        
        return visual_effects
    
    def set_indoor_battle(self, is_indoor: bool) -> None:
        """Set whether current battle is indoors."""
        self.is_indoor_battle = is_indoor
        
        # Remove indoor-restricted effects
        if is_indoor:
            for category, effect in self.active_effects.items():
                if effect and effect.is_indoor_restricted:
                    self.remove_effect(category)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "active_effects": {
                cat.value: effect.to_dict() if effect else None
                for cat, effect in self.active_effects.items()
            },
            "effect_history": [effect.to_dict() for effect in self.effect_history],
            "is_indoor_battle": self.is_indoor_battle
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FieldEffectManager':
        """Create from dictionary."""
        manager = cls()
        
        # Restore active effects
        for cat_str, effect_data in data.get("active_effects", {}).items():
            if effect_data:
                category = EffectCategory(cat_str)
                effect = manager._create_effect_from_data(effect_data)
                if effect:
                    manager.active_effects[category] = effect
        
        # Restore effect history
        for effect_data in data.get("effect_history", []):
            effect = manager._create_effect_from_data(effect_data)
            if effect:
                manager.effect_history.append(effect)
        
        manager.is_indoor_battle = data.get("is_indoor_battle", False)
        return manager
    
    def _create_effect_from_data(self, data: Dict[str, Any]) -> Optional[FieldEffect]:
        """Create effect instance from dictionary data."""
        try:
            category = EffectCategory(data["category"])
            
            if category == EffectCategory.WEATHER:
                data["weather_type"] = WeatherType(data["weather_type"])
                data["immunity_types"] = set(data.get("immunity_types", []))
                data["end_turn_damage_types"] = set(data.get("end_turn_damage_types", []))
                return WeatherEffect(**data)
                
            elif category == EffectCategory.TERRAIN:
                data["terrain_type"] = TerrainType(data["terrain_type"])
                data["status_immunities"] = set(data.get("status_immunities", []))
                data["move_restrictions"] = set(data.get("move_restrictions", []))
                return TerrainEffect(**data)
                
            elif category == EffectCategory.SPECIAL:
                data["effect_type"] = SpecialEffectType(data["effect_type"])
                return SpecialEffect(**data)
                
        except (KeyError, ValueError) as e:
            print(f"Fehler beim Wiederherstellen des Feld-Effekts: {e}")
            return None
        
        return None


# Factory functions for creating common effects
def create_sunny_weather(duration: int = 5) -> WeatherEffect:
    """Create sunny weather effect."""
    return WeatherEffect(
        effect_id="sunny_weather",
        weather_type=WeatherType.SUNNY,
        name="Sonnenschein",
        description="Die Sonne scheint hell! Feuer-Attacken sind verstärkt, Wasser-Attacken geschwächt.",
        duration=duration
    )


def create_rain_weather(duration: int = 5) -> WeatherEffect:
    """Create rain weather effect."""
    return WeatherEffect(
        effect_id="rain_weather",
        weather_type=WeatherType.RAIN,
        name="Regen",
        description="Es regnet! Wasser-Attacken sind verstärkt, Feuer-Attacken geschwächt.",
        duration=duration
    )


def create_sandstorm_weather(duration: int = 5) -> WeatherEffect:
    """Create sandstorm weather effect."""
    return WeatherEffect(
        effect_id="sandstorm_weather",
        weather_type=WeatherType.SANDSTORM,
        name="Sandsturm",
        description="Ein Sandsturm tobt! Erd-Typen sind immun, andere nehmen Schaden.",
        duration=duration
    )


def create_grassy_terrain(duration: int = 5) -> TerrainEffect:
    """Create grassy terrain effect."""
    return TerrainEffect(
        effect_id="grassy_terrain",
        terrain_type=TerrainType.GRASSY,
        name="Gras-Terrain",
        description="Gras bedeckt das Feld! Pflanzen-Attacken sind verstärkt, HP-Regeneration aktiv.",
        duration=duration
    )


def create_electric_terrain(duration: int = 5) -> TerrainEffect:
    """Create electric terrain effect."""
    return TerrainEffect(
        effect_id="electric_terrain",
        terrain_type=TerrainType.ELECTRIC,
        name="Elektro-Terrain",
        description="Elektrische Energie durchströmt das Feld! Energie-Attacken sind verstärkt, Schlaf-Immunität.",
        duration=duration
    )


def create_zeitriss_effect(duration: int = 3) -> SpecialEffect:
    """Create Zeitriss special effect."""
    return SpecialEffect(
        effect_id="zeitriss_effect",
        effect_type=SpecialEffectType.ZEITRISS,
        name="Zeitriss",
        description="Ein Zeitriss öffnet sich! Die Realität verzerrt sich...",
        duration=duration
    )
