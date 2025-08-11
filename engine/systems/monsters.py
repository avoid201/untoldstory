"""
Monster Species Database for Untold Story
Loads and manages all monster species data
"""

from typing import Dict, List, Optional, Any
from engine.systems.monster_instance import MonsterSpecies, MonsterInstance, MonsterRank
from engine.systems.stats import GrowthCurve, BaseStats
from engine.core.resources import resources
import random


class MonsterDatabase:
    """
    Central database for all monster species.
    Singleton that loads and caches species data.
    """
    
    _instance: Optional['MonsterDatabase'] = None
    
    def __new__(cls) -> 'MonsterDatabase':
        """Ensure singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self) -> None:
        """Initialize the monster database."""
        if self._initialized:
            return
        
        self._initialized = True
        self.species: Dict[int, MonsterSpecies] = {}
        self.species_by_name: Dict[str, MonsterSpecies] = {}
        self.species_by_era: Dict[str, List[int]] = {
            "past": [],
            "present": [],
            "future": []
        }
        self.species_by_rank: Dict[str, List[int]] = {}
        self.species_by_type: Dict[str, List[int]] = {}
        
        # Special categories
        self.starters: List[int] = []
        self.legendaries: List[int] = []
        self.fossils: List[int] = []
        
        # Load species data
        self._load_species_data()
    
    def _load_species_data(self) -> None:
        """Load monster species data from JSON."""
        try:
            monster_data = resources.load_json("monsters.json")
            
            for species_dict in monster_data.get("monsters", []):
                species = self._create_species_from_dict(species_dict)
                self.register_species(species)
            
            # Identify special categories
            self._identify_special_categories()
            
        except Exception as e:
            print(f"Error loading monster data: {e}")
            # Create default starter if loading fails
            self._create_default_species()
    
    def _create_species_from_dict(self, data: Dict[str, Any]) -> MonsterSpecies:
        """Create a MonsterSpecies from dictionary data."""
        # Convert growth curve string to enum
        growth_curve = GrowthCurve.MEDIUM_FAST
        curve_str = data.get("growth", {}).get("curve", "medium_fast")
        try:
            growth_curve = GrowthCurve(curve_str)
        except ValueError:
            pass
        
        # Create species
        species = MonsterSpecies(
            id=data["id"],
            name=data["name"],
            era=data.get("era", "present"),
            rank=MonsterRank(data.get("rank", "E")),
            types=data.get("types", ["Bestie"]),
            base_stats=BaseStats.from_dict(data["base_stats"]),
            growth_curve=growth_curve,
            base_exp_yield=data.get("growth", {}).get("yield", 64),
            capture_rate=data.get("capture_rate", 45),
            traits=data.get("traits", []),
            learnset=[(l["level"], l["move"]) for l in data.get("learnset", [])],
            evolution=data.get("evolution"),
            description=data.get("description", "")
        )
        
        return species
    
    def _create_default_species(self) -> None:
        """Create default starter species if loading fails."""
        glutkohle = MonsterSpecies(
            id=1,
            name="Glutkohle",
            era="past",
            rank=MonsterRank.E,
            types=["Feuer"],
            base_stats=BaseStats(45, 52, 43, 60, 50, 65),
            growth_curve=GrowthCurve.MEDIUM_FAST,
            base_exp_yield=64,
            capture_rate=45,
            traits=["Brennbar"],
            learnset=[(1, "tackle"), (5, "ember")],
            evolution={"level": 16, "to": 5},
            description="Ein prähistorisches Feuermonster."
        )
        self.register_species(glutkohle)
        self.starters.append(1)
    
    def register_species(self, species: MonsterSpecies) -> None:
        """
        Register a species in the database.
        
        Args:
            species: Species to register
        """
        self.species[species.id] = species
        self.species_by_name[species.name.lower()] = species
        
        # Index by era
        if species.era not in self.species_by_era:
            self.species_by_era[species.era] = []
        self.species_by_era[species.era].append(species.id)
        
        # Index by rank
        rank_str = species.rank.value
        if rank_str not in self.species_by_rank:
            self.species_by_rank[rank_str] = []
        self.species_by_rank[rank_str].append(species.id)
        
        # Index by type
        for monster_type in species.types:
            if monster_type not in self.species_by_type:
                self.species_by_type[monster_type] = []
            self.species_by_type[monster_type].append(species.id)
    
    def _identify_special_categories(self) -> None:
        """Identify special monster categories."""
        # Starters (ID 1-4, E rank fossils)
        self.starters = [1, 2, 3, 4]
        
        # Fossils (all past era monsters)
        self.fossils = self.species_by_era.get("past", [])
        
        # Legendaries (ID 140-151, S/SS/X rank)
        self.legendaries = []
        for species_id in range(140, 152):
            if species_id in self.species:
                self.legendaries.append(species_id)
    
    def get_species(self, species_id: int) -> Optional[MonsterSpecies]:
        """
        Get a species by ID.
        
        Args:
            species_id: Species ID number
            
        Returns:
            MonsterSpecies or None if not found
        """
        return self.species.get(species_id)
    
    def get_species_by_name(self, name: str) -> Optional[MonsterSpecies]:
        """
        Get a species by name (case-insensitive).
        
        Args:
            name: Species name
            
        Returns:
            MonsterSpecies or None if not found
        """
        return self.species_by_name.get(name.lower())
    
    def create_monster(self, species_id: int, level: int = 5,
                      nickname: Optional[str] = None) -> Optional[MonsterInstance]:
        """
        Create a new monster instance.
        
        Args:
            species_id: Species ID
            level: Starting level
            nickname: Optional nickname
            
        Returns:
            MonsterInstance or None if species not found
        """
        species = self.get_species(species_id)
        if not species:
            return None
        
        return MonsterInstance(species, level, nickname)
    
    def create_wild_monster(self, area: str = "route1", 
                          player_level: int = 5) -> Optional[MonsterInstance]:
        """
        Create a random wild monster for an area.
        
        Args:
            area: Area identifier
            player_level: Player's highest monster level (for scaling)
            
        Returns:
            Random wild MonsterInstance
        """
        # Get available species for the area
        # For now, use present-era common monsters
        available = []
        
        if area == "route1":
            # Early game area - F and E rank present monsters
            for rank in ["F", "E"]:
                species_ids = self.species_by_rank.get(rank, [])
                for sid in species_ids:
                    species = self.species.get(sid)
                    if species and species.era == "present":
                        available.append(sid)
        
        if not available:
            # Fallback to any present-era monster
            available = self.species_by_era.get("present", [])
        
        if not available:
            return None
        
        # Pick random species
        species_id = random.choice(available)
        
        # Determine level (near player level with some variance)
        min_level = max(2, player_level - 3)
        max_level = min(100, player_level + 2)
        level = random.randint(min_level, max_level)
        
        return self.create_monster(species_id, level)
    
    def get_evolution_chain(self, species_id: int) -> List[int]:
        """
        Get the complete evolution chain for a species.
        
        Args:
            species_id: Starting species ID
            
        Returns:
            List of species IDs in evolution order
        """
        chain = [species_id]
        current = self.get_species(species_id)
        
        # Follow evolution forward
        while current and current.evolution:
            next_id = current.evolution.get("to")
            if next_id and next_id not in chain:  # Prevent loops
                chain.append(next_id)
                current = self.get_species(next_id)
            else:
                break
        
        # Find pre-evolutions
        for sid, species in self.species.items():
            if species.evolution and species.evolution.get("to") == species_id:
                if sid not in chain:
                    chain.insert(0, sid)
        
        return chain
    
    def get_species_by_criteria(self, era: Optional[str] = None,
                               rank: Optional[str] = None,
                               monster_type: Optional[str] = None,
                               can_evolve: Optional[bool] = None) -> List[MonsterSpecies]:
        """
        Get species matching certain criteria.
        
        Args:
            era: Filter by era (past/present/future)
            rank: Filter by rank (F-X)
            monster_type: Filter by type
            can_evolve: Filter by whether they can evolve
            
        Returns:
            List of matching species
        """
        results = []
        
        for species in self.species.values():
            # Check era
            if era and species.era != era:
                continue
            
            # Check rank
            if rank and species.rank.value != rank:
                continue
            
            # Check type
            if monster_type and monster_type not in species.types:
                continue
            
            # Check evolution
            if can_evolve is not None:
                has_evolution = species.evolution is not None
                if has_evolution != can_evolve:
                    continue
            
            results.append(species)
        
        return results
    
    def get_starter_options(self) -> List[MonsterSpecies]:
        """Get available starter monsters."""
        starters = []
        for species_id in self.starters:
            species = self.get_species(species_id)
            if species:
                starters.append(species)
        return starters
    
    def get_legendary_monsters(self) -> List[MonsterSpecies]:
        """Get all legendary monsters."""
        legendaries = []
        for species_id in self.legendaries:
            species = self.get_species(species_id)
            if species:
                legendaries.append(species)
        return legendaries
    
    def get_fossil_monsters(self) -> List[MonsterSpecies]:
        """Get all fossil (past era) monsters."""
        fossils = []
        for species_id in self.fossils:
            species = self.get_species(species_id)
            if species:
                fossils.append(species)
        return fossils
    
    def calculate_encounter_rate(self, species: MonsterSpecies, 
                                area_type: str = "grass") -> float:
        """
        Calculate encounter rate for a species in an area type.
        
        Args:
            species: Monster species
            area_type: Type of area (grass, cave, water, etc.)
            
        Returns:
            Encounter rate (0.0-1.0)
        """
        base_rate = 1.0
        
        # Adjust by rank (rarer = lower rate)
        rank_rates = {
            "F": 0.3, "E": 0.25, "D": 0.2, "C": 0.15,
            "B": 0.1, "A": 0.08, "S": 0.05, "SS": 0.02, "X": 0.01
        }
        base_rate *= rank_rates.get(species.rank.value, 0.1)
        
        # Adjust by era
        if species.era == "past":
            base_rate *= 0.3  # Fossils are rare in wild
        elif species.era == "future":
            base_rate *= 0.5  # Future monsters less common
        
        # Adjust by area type
        if area_type == "water" and "Wasser" in species.types:
            base_rate *= 2.0
        elif area_type == "cave" and "Erde" in species.types:
            base_rate *= 1.5
        
        return min(1.0, base_rate)


# Global singleton instance
monster_db = MonsterDatabase()
