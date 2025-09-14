"""
Monster Species Database for Untold Story
Loads and manages all monster species data
"""

from typing import Dict, List, Optional, Any, Tuple
from engine.systems.monster_instance import MonsterSpecies, MonsterInstance, MonsterRank
from engine.systems.stats import GrowthCurve, BaseStats
from engine.core.resources import resources
import random
import weakref


class MonsterDatabase:
    """
    Central database for all monster species.
    Singleton that loads and caches species data.
    OPTIMIERT: Performance-Caching und erweiterte Indizierung
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
        
        # OPTIMIERT: Performance-Caching mit WeakRef
        self._instance_cache: Dict[Tuple[int, int], weakref.WeakValueDictionary] = {}  # (species_id, level) -> weakref dict
        self._cache_hits = 0
        self._cache_misses = 0
        self._max_cache_size = 1000
        
        # Trait System Integration
        self._trait_system = None
        
        # OPTIMIERT: Erweiterte Indizierung
        self.species_by_traits: Dict[str, List[int]] = {}
        self.species_by_capture_rate: Dict[str, List[int]] = {}  # "common", "uncommon", "rare", "legendary"
        self.species_by_growth_curve: Dict[str, List[int]] = {}
        
        # Performance tracking
        self._load_time = 0
        self._total_queries = 0
        
        # Load species data
        import time
        start_time = time.time()
        self._load_species_data()
        self._load_time = time.time() - start_time
        
        # Initialize trait system
        self._init_trait_system()
    
    def _load_species_data(self) -> None:
        """Load monster species data from JSON."""
        try:
            monster_data = resources.load_json("monsters.json")
            
            # Handle both list and dict formats
            if isinstance(monster_data, list):
                species_list = monster_data
            else:
                species_list = monster_data.get("monsters", [])
            
            for species_dict in species_list:
                species = self._create_species_from_dict(species_dict)
                self.register_species(species)
            
            # Identify special categories
            self._identify_special_categories()
            
        except Exception as e:
            print(f"Error loading monster data: {e}")
            # Create default starter if loading fails
            self._create_default_species()
    
    def _init_trait_system(self):
        """Initialize the trait system."""
        try:
            from engine.systems.battle.monster_traits import get_trait_system
            self._trait_system = get_trait_system()
            print("Trait system initialized successfully")
        except Exception as e:
            print(f"Error initializing trait system: {e}")
            self._trait_system = None
    
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
            types=data.get("types", ["Bestie"]),
            base_stats=BaseStats.from_dict(data["base_stats"]),
            rank=MonsterRank(data.get("rank", "E")),
            growth_curve=growth_curve,
            description=data.get("description", ""),
            traits=data.get("traits", []),  # DQM-spezifische Traits
            abilities=data.get("abilities", []),
            catch_rate=data.get("catch_rate", 128),
            era=data.get("era", "present")
        )
        
        return species
    
    def _create_default_species(self) -> None:
        """Create default starter species if loading fails."""
        glutkohle = MonsterSpecies(
            id="1",
            name="Glutkohle",
            types=["Feuer"],
            base_stats=BaseStats(45, 52, 43, 60, 50, 65),
            rank=MonsterRank.E,
            growth_curve=GrowthCurve.MEDIUM_FAST,
            description="Ein prähistorisches Feuermonster."
        )
        self.register_species(glutkohle)
        self.starters.append(1)
    
    def register_species(self, species: MonsterSpecies) -> None:
        """
        Register a species in the database.
        OPTIMIERT: Erweiterte Indizierung für bessere Performance
        
        Args:
            species: Species to register
        """
        self.species[species.id] = species
        self.species_by_name[species.name.lower()] = species
        
        # Index by era (default to "present" if not specified)
        era = getattr(species, 'era', 'present')
        if era not in self.species_by_era:
            self.species_by_era[era] = []
        self.species_by_era[era].append(species.id)
        
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
        
        # OPTIMIERT: Erweiterte Indizierung
        # Index by traits
        if hasattr(species, 'traits') and species.traits:
            for trait in species.traits:
                if trait not in self.species_by_traits:
                    self.species_by_traits[trait] = []
                self.species_by_traits[trait].append(species.id)
        
        # Index by capture rate
        capture_rate = getattr(species, 'catch_rate', 128)
        if capture_rate >= 200:
            rate_category = "common"
        elif capture_rate >= 100:
            rate_category = "uncommon"
        elif capture_rate >= 50:
            rate_category = "rare"
        else:
            rate_category = "legendary"
        
        if rate_category not in self.species_by_capture_rate:
            self.species_by_capture_rate[rate_category] = []
        self.species_by_capture_rate[rate_category].append(species.id)
        
        # Index by growth curve
        growth_curve = getattr(species, 'growth_curve', 'medium_fast')
        if hasattr(growth_curve, 'value'):
            curve_name = growth_curve.value
        else:
            curve_name = str(growth_curve)
        
        if curve_name not in self.species_by_growth_curve:
            self.species_by_growth_curve[curve_name] = []
        self.species_by_growth_curve[curve_name].append(species.id)
    
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
    
    def get_random_species(self) -> Optional[MonsterSpecies]:
        """
        Get a random species from the database.
        
        Returns:
            Random MonsterSpecies or None if database is empty
        """
        if not self.species:
            return None
        
        species_ids = list(self.species.keys())
        random_id = random.choice(species_ids)
        return self.species[random_id]
    
    def create_monster(self, species_id: int, level: int = 5,
                      nickname: Optional[str] = None) -> Optional[MonsterInstance]:
        """
        Create a new monster instance.
        OPTIMIERT: Intelligentes Caching für bessere Performance
        
        Args:
            species_id: Species ID
            level: Starting level
            nickname: Optional nickname
            
        Returns:
            MonsterInstance or None if species not found
        """
        self._total_queries += 1
        
        # OPTIMIERT: Cache-Check für Standard-Monster (ohne Nickname)
        if not nickname:
            cache_key = (species_id, level)
            if cache_key in self._instance_cache:
                weak_dict = self._instance_cache[cache_key]
                # Try to get a cached instance
                for cached_instance in weak_dict.values():
                    if cached_instance is not None:
                        self._cache_hits += 1
                        # Return cached instance (create copy to avoid mutations)
                        return MonsterInstance(cached_instance.species, level, nickname)
                # If all cached instances are gone, remove the weak dict
                del self._instance_cache[cache_key]
            
            self._cache_misses += 1
        
        species = self.get_species(species_id)
        if not species:
            return None
        
        instance = MonsterInstance(species, level, nickname)
        
        # OPTIMIERT: Cache nur Standard-Monster (ohne Nickname) mit WeakRef
        if not nickname and len(self._instance_cache) < self._max_cache_size:
            cache_key = (species_id, level)
            if cache_key not in self._instance_cache:
                self._instance_cache[cache_key] = weakref.WeakValueDictionary()
            self._instance_cache[cache_key][id(instance)] = instance
        
        return instance
    
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
    
    def get_species_by_traits(self, traits: List[str]) -> List[MonsterSpecies]:
        """
        Get species that have specific traits.
        
        Args:
            traits: List of trait names to search for
            
        Returns:
            List of species with any of the specified traits
        """
        matching_species = []
        for trait in traits:
            if trait in self.species_by_traits:
                for species_id in self.species_by_traits[trait]:
                    species = self.get_species(species_id)
                    if species and species not in matching_species:
                        matching_species.append(species)
        return matching_species
    
    def get_species_by_capture_rate(self, rate_category: str) -> List[MonsterSpecies]:
        """
        Get species by capture rate category.
        
        Args:
            rate_category: "common", "uncommon", "rare", or "legendary"
            
        Returns:
            List of species in the category
        """
        species_list = []
        if rate_category in self.species_by_capture_rate:
            for species_id in self.species_by_capture_rate[rate_category]:
                species = self.get_species(species_id)
                if species:
                    species_list.append(species)
        return species_list
    
    def get_species_by_growth_curve(self, curve_name: str) -> List[MonsterSpecies]:
        """
        Get species by growth curve.
        
        Args:
            curve_name: Growth curve name
            
        Returns:
            List of species with the specified growth curve
        """
        species_list = []
        if curve_name in self.species_by_growth_curve:
            for species_id in self.species_by_growth_curve[curve_name]:
                species = self.get_species(species_id)
                if species:
                    species_list.append(species)
        return species_list
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Get performance statistics for the database.
        
        Returns:
            Dictionary with performance metrics
        """
        cache_hit_rate = 0.0
        if self._cache_hits + self._cache_misses > 0:
            cache_hit_rate = self._cache_hits / (self._cache_hits + self._cache_misses)
        
        return {
            'total_species': len(self.species),
            'load_time': self._load_time,
            'total_queries': self._total_queries,
            'cache_hits': self._cache_hits,
            'cache_misses': self._cache_misses,
            'cache_hit_rate': cache_hit_rate,
            'cache_size': len(self._instance_cache),
            'max_cache_size': self._max_cache_size,
            'indexes': {
                'by_era': {era: len(species_ids) for era, species_ids in self.species_by_era.items()},
                'by_rank': {rank: len(species_ids) for rank, species_ids in self.species_by_rank.items()},
                'by_type': {monster_type: len(species_ids) for monster_type, species_ids in self.species_by_type.items()},
                'by_traits': {trait: len(species_ids) for trait, species_ids in self.species_by_traits.items()},
                'by_capture_rate': {rate: len(species_ids) for rate, species_ids in self.species_by_capture_rate.items()},
                'by_growth_curve': {curve: len(species_ids) for curve, species_ids in self.species_by_growth_curve.items()}
            }
        }
    
    def clear_cache(self) -> None:
        """Clear the instance cache."""
        self._instance_cache.clear()
        self._cache_hits = 0
        self._cache_misses = 0
    
    def get_trait_system(self):
        """Get the trait system instance."""
        return self._trait_system
    
    def apply_traits_to_species(self, species_id: int, traits: List[str]) -> bool:
        """Apply traits to a species."""
        try:
            species = self.get_species(species_id)
            if not species:
                return False
            
            # Validate traits
            if self._trait_system:
                valid_traits = []
                for trait_name in traits:
                    if self._trait_system.database.get_trait(trait_name):
                        valid_traits.append(trait_name)
                    else:
                        print(f"Warning: Unknown trait '{trait_name}' for species {species.name}")
                
                # Update species traits
                species.traits = valid_traits
                return True
            
            return False
            
        except Exception as e:
            print(f"Error applying traits to species {species_id}: {e}")
            return False
    
    def get_species_with_trait(self, trait_name: str) -> List[MonsterSpecies]:
        """Get all species that have a specific trait."""
        species_list = []
        for species in self.species.values():
            if hasattr(species, 'traits') and trait_name in species.traits:
                species_list.append(species)
        return species_list
    
    def validate_database(self) -> Dict[str, Any]:
        """
        Validate the integrity of the monster database.
        
        Returns:
            Validation results with any issues found
        """
        issues = []
        warnings = []
        
        # Check for missing species
        expected_species_count = 151
        if len(self.species) < expected_species_count:
            issues.append(f"Expected {expected_species_count} species, found {len(self.species)}")
        
        # Check for duplicate IDs
        seen_ids = set()
        for species_id in self.species.keys():
            if species_id in seen_ids:
                issues.append(f"Duplicate species ID: {species_id}")
            seen_ids.add(species_id)
        
        # Check for missing base stats
        for species_id, species in self.species.items():
            if not hasattr(species, 'base_stats') or not species.base_stats:
                issues.append(f"Species {species_id} ({species.name}) missing base stats")
            elif not hasattr(species.base_stats, 'hp') or species.base_stats.hp <= 0:
                issues.append(f"Species {species_id} ({species.name}) has invalid HP")
        
        # Check for missing types
        for species_id, species in self.species.items():
            if not hasattr(species, 'types') or not species.types:
                issues.append(f"Species {species_id} ({species.name}) missing types")
            elif len(species.types) == 0:
                issues.append(f"Species {species_id} ({species.name}) has empty types list")
        
        # Check for invalid ranks
        valid_ranks = {'F', 'E', 'D', 'C', 'B', 'A', 'S', 'SS', 'X'}
        for species_id, species in self.species.items():
            if not hasattr(species, 'rank') or species.rank.value not in valid_ranks:
                issues.append(f"Species {species_id} ({species.name}) has invalid rank: {getattr(species, 'rank', 'None')}")
        
        # Check for missing descriptions
        missing_descriptions = 0
        for species_id, species in self.species.items():
            if not hasattr(species, 'description') or not species.description or species.description.strip() == "":
                missing_descriptions += 1
        
        if missing_descriptions > 0:
            warnings.append(f"{missing_descriptions} species missing descriptions")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
            'total_species': len(self.species),
            'species_with_descriptions': len(self.species) - missing_descriptions
        }


# Global singleton instance
monster_db = MonsterDatabase()

def get_monster_database() -> MonsterDatabase:
    """
    Get the global monster database instance.
    This ensures proper singleton pattern usage.
    """
    return monster_db
