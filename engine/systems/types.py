"""
Type System for Untold Story
Handles type effectiveness, STAB, and type-based interactions
"""

from typing import List, Dict, Tuple, Optional
from enum import Enum
from engine.core.resources import resources


class MonsterType(Enum):
    """All monster types in the game."""
    FEUER = "Feuer"      # Fire
    WASSER = "Wasser"    # Water  
    ERDE = "Erde"        # Earth
    LUFT = "Luft"        # Air
    PFLANZE = "Pflanze"  # Plant
    BESTIE = "Bestie"    # Beast
    ENERGIE = "Energie"  # Energy
    CHAOS = "Chaos"      # Chaos
    SEUCHE = "Seuche"    # Plague
    MYSTIK = "Mystik"    # Mystic
    GOTTHEIT = "Gottheit"  # Deity (Legendary only)
    TEUFEL = "Teufel"    # Devil (Legendary only)


class TypeChart:
    """
    Manages type effectiveness calculations.
    Singleton class that loads and caches type matchup data.
    """
    
    _instance: Optional['TypeChart'] = None
    
    def __new__(cls) -> 'TypeChart':
        """Ensure singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self) -> None:
        """Initialize the type chart."""
        if self._initialized:
            return
        
        self._initialized = True
        self.chart: Dict[Tuple[str, str], float] = {}
        self.stab_multiplier: float = 1.2
        self.type_list: List[str] = []
        self.type_descriptions: Dict[str, str] = {}
        
        # Load type data from JSON
        self._load_type_data()
    
    def _load_type_data(self) -> None:
        """Load type effectiveness data from JSON."""
        try:
            type_data = resources.load_json("types.json")
            
            # Store type list
            self.type_list = type_data.get("types", [])
            
            # Build effectiveness chart
            for entry in type_data.get("chart", []):
                key = (entry["att"], entry["def"])
                self.chart[key] = entry["x"]
            
            # Get STAB multiplier
            self.stab_multiplier = type_data.get("stab", 1.2)
            
            # Get type descriptions
            self.type_descriptions = type_data.get("descriptions", {})
            
        except Exception as e:
            print(f"Error loading type data: {e}")
            # Set defaults
            self.type_list = [t.value for t in MonsterType]
            self.stab_multiplier = 1.2
    
    def get_effectiveness(self, attacking_type: str, defending_type: str) -> float:
        """
        Get the effectiveness multiplier for a type matchup.
        
        Args:
            attacking_type: The attacking move's type
            defending_type: The defending monster's type
            
        Returns:
            Effectiveness multiplier (0.25, 0.5, 1.0, 1.5, 2.0, etc.)
        """
        # Check for explicit matchup in chart
        key = (attacking_type, defending_type)
        if key in self.chart:
            return self.chart[key]
        
        # Default to neutral
        return 1.0
    
    def calculate_type_multiplier(self, move_type: str, 
                                 defender_types: List[str]) -> float:
        """
        Calculate total type effectiveness for a move against a monster.
        
        Args:
            move_type: Type of the attacking move
            defender_types: List of defender's types (1-3 types possible)
            
        Returns:
            Combined type effectiveness multiplier
        """
        if not defender_types:
            return 1.0
        
        multiplier = 1.0
        for def_type in defender_types:
            multiplier *= self.get_effectiveness(move_type, def_type)
        
        return multiplier
    
    def get_stab_multiplier(self, move_type: str, 
                           attacker_types: List[str]) -> float:
        """
        Calculate STAB (Same Type Attack Bonus).
        
        Args:
            move_type: Type of the move
            attacker_types: List of attacker's types
            
        Returns:
            STAB multiplier (1.0 or configured STAB value)
        """
        if move_type in attacker_types:
            return self.stab_multiplier
        return 1.0
    
    def get_type_matchup_description(self, multiplier: float) -> str:
        """
        Get a text description for a type effectiveness multiplier.
        
        Args:
            multiplier: The effectiveness multiplier
            
        Returns:
            Description string
        """
        if multiplier == 0:
            return "Hat keine Wirkung"
        elif multiplier < 0.5:
            return "Kaum effektiv"
        elif multiplier < 1.0:
            return "Nicht sehr effektiv"
        elif multiplier > 2.0:
            return "Extrem effektiv!"
        elif multiplier > 1.0:
            return "Sehr effektiv!"
        else:
            return "Normal effektiv"
    
    def is_immune(self, move_type: str, defender_types: List[str]) -> bool:
        """
        Check if defender is immune to the move type.
        
        Args:
            move_type: Type of the attacking move
            defender_types: List of defender's types
            
        Returns:
            True if defender is immune (0x effectiveness)
        """
        return self.calculate_type_multiplier(move_type, defender_types) == 0
    
    def get_weaknesses(self, monster_types: List[str]) -> List[str]:
        """
        Get all types that this monster is weak to.
        
        Args:
            monster_types: List of the monster's types
            
        Returns:
            List of type names that deal super effective damage
        """
        weaknesses = []
        
        for attacking_type in self.type_list:
            multiplier = self.calculate_type_multiplier(attacking_type, monster_types)
            if multiplier > 1.0:
                weaknesses.append(attacking_type)
        
        return weaknesses
    
    def get_resistances(self, monster_types: List[str]) -> List[str]:
        """
        Get all types that this monster resists.
        
        Args:
            monster_types: List of the monster's types
            
        Returns:
            List of type names that deal reduced damage
        """
        resistances = []
        
        for attacking_type in self.type_list:
            multiplier = self.calculate_type_multiplier(attacking_type, monster_types)
            if 0 < multiplier < 1.0:
                resistances.append(attacking_type)
        
        return resistances
    
    def get_immunities(self, monster_types: List[str]) -> List[str]:
        """
        Get all types that this monster is immune to.
        
        Args:
            monster_types: List of the monster's types
            
        Returns:
            List of type names that have no effect
        """
        immunities = []
        
        for attacking_type in self.type_list:
            if self.is_immune(attacking_type, monster_types):
                immunities.append(attacking_type)
        
        return immunities
    
    def get_offensive_coverage(self, move_types: List[str]) -> Dict[str, float]:
        """
        Calculate offensive coverage for a set of move types.
        
        Args:
            move_types: List of move types to analyze
            
        Returns:
            Dictionary mapping each type to best effectiveness against it
        """
        coverage = {}
        
        for defending_type in self.type_list:
            best_effectiveness = 0.0
            for move_type in move_types:
                effectiveness = self.get_effectiveness(move_type, defending_type)
                best_effectiveness = max(best_effectiveness, effectiveness)
            coverage[defending_type] = best_effectiveness
        
        return coverage
    
    def suggest_coverage_move(self, current_moves: List[str], 
                             monster_types: List[str]) -> Optional[str]:
        """
        Suggest a type for additional coverage.
        
        Args:
            current_moves: List of current move types
            monster_types: Monster's own types (for STAB consideration)
            
        Returns:
            Suggested type for best additional coverage
        """
        current_coverage = self.get_offensive_coverage(current_moves)
        
        # Find types with poor coverage
        weak_coverage = [t for t, e in current_coverage.items() if e < 1.0]
        
        if not weak_coverage:
            return None
        
        # Find best type to add
        best_type = None
        best_improvement = 0
        
        for potential_type in self.type_list:
            improvement = 0
            for weak_type in weak_coverage:
                effectiveness = self.get_effectiveness(potential_type, weak_type)
                if effectiveness > current_coverage[weak_type]:
                    improvement += effectiveness - current_coverage[weak_type]
            
            # Bonus for STAB
            if potential_type in monster_types:
                improvement *= 1.2
            
            if improvement > best_improvement:
                best_improvement = improvement
                best_type = potential_type
        
        return best_type


class TypeEffectivenessResult:
    """Result of a type effectiveness calculation."""
    
    def __init__(self, multiplier: float, move_type: str, 
                 defender_types: List[str], has_stab: bool = False):
        """
        Initialize type effectiveness result.
        
        Args:
            multiplier: Total effectiveness multiplier
            move_type: Type of the move
            defender_types: Defender's types
            has_stab: Whether STAB applies
        """
        self.multiplier = multiplier
        self.move_type = move_type
        self.defender_types = defender_types
        self.has_stab = has_stab
        
        # Categorize effectiveness
        self.is_immune = multiplier == 0
        self.is_not_very_effective = 0 < multiplier < 1.0
        self.is_neutral = multiplier == 1.0
        self.is_super_effective = multiplier > 1.0
        self.is_ultra_effective = multiplier >= 4.0
    
    def get_message(self) -> str:
        """Get a battle message for this effectiveness."""
        chart = TypeChart()
        base_msg = chart.get_type_matchup_description(self.multiplier)
        
        if self.has_stab:
            return f"{base_msg} (STAB-Bonus!)"
        return base_msg
    
    def get_color(self) -> Tuple[int, int, int]:
        """Get a color for displaying this effectiveness."""
        if self.is_immune:
            return (128, 128, 128)  # Gray
        elif self.is_not_very_effective:
            return (200, 100, 100)  # Red
        elif self.is_super_effective:
            return (100, 200, 100)  # Green
        else:
            return (255, 255, 255)  # White


# Global singleton instance
type_chart = TypeChart()