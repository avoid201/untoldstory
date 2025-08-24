"""
Type System for Untold Story RPG
High-performance type effectiveness calculations using NumPy
OPTIMIERT: NumPy-Integration und Matrix-Caching
"""

import json
import time
import warnings
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from enum import IntEnum, Enum
from dataclasses import dataclass
from functools import lru_cache
import random

# OPTIMIERT: NumPy für Matrix-Operationen
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    warnings.warn("NumPy nicht verfügbar - verwende Fallback-Implementierung")

import logging
logger = logging.getLogger(__name__)

class TypeAttribute(IntEnum):
    """Special attributes that types can have."""
    NONE = 0
    LEGENDARY = 16
    CORRUPTED = 32

# Battle conditions that affect type effectiveness
class BattleCondition(Enum):
    """Special battle conditions that modify type effectiveness."""
    NORMAL = "normal"
    INVERSE = "inverse"  # Inverted type effectiveness
    CHAOS = "chaos"      # Random effectiveness modifiers
    PURE = "pure"        # Only STAB moves are effective

@dataclass
class TypeData:
    """Container for type information."""
    name: str
    id: int
    attributes: int = 0
    description: str = ""
    color: Tuple[int, int, int] = (255, 255, 255)
    
    def has_attribute(self, attr: TypeAttribute) -> bool:
        """Check if type has a specific attribute."""
        return bool(self.attributes & attr)

@dataclass
class TypeRelation:
    """Represents a relationship between two types."""
    attacker_id: int
    defender_id: int
    multiplier: float
    
    def inverse(self) -> 'TypeRelation':
        """Get inverse effectiveness."""
        if self.multiplier == 0:
            return TypeRelation(self.attacker_id, self.defender_id, 2.0)
        elif self.multiplier < 1:
            return TypeRelation(self.attacker_id, self.defender_id, 2.0)
        elif self.multiplier > 1:
            return TypeRelation(self.attacker_id, self.defender_id, 0.5)
        return self

class TypeChart:
    """
    High-performance type effectiveness chart using NumPy.
    Singleton pattern with extensive caching and optimization.
    OPTIMIERT: Vollständige NumPy-Integration und intelligentes Caching
    """
    
    _instance: Optional['TypeChart'] = None
    _performance_mode: bool = True  # Enable performance optimizations
    
    def __new__(cls) -> 'TypeChart':
        """Ensure singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, data_path: Optional[str] = None) -> None:
        """
        Initialize the type chart.
        
        Args:
            data_path: Path to types.json file
        """
        if self._initialized:
            return
        
        self._initialized = True
        self._init_time = time.time()
        
        # Configuration
        self.config = {
            'stab_multiplier': 1.2,
            'synergy_bonus': 1.15,
            'combo_cap': 3.0,
            'adaptive_rate': 0.05,
            'cache_size': 1000
        }
        
        # Core data structures
        self.types: Dict[str, TypeData] = {}
        self.type_names: List[str] = []
        self.type_ids: Dict[str, int] = {}
        
        # OPTIMIERT: NumPy-Matrix für effiziente Berechnungen
        if NUMPY_AVAILABLE:
            self.effectiveness_matrix: Optional[np.ndarray] = None
            self._matrix_initialized = False
        else:
            self.effectiveness_matrix = None
            self._matrix_initialized = False
        
        # Caching structures - OPTIMIERT: Erweiterte Cache-Strategien
        self.lookup_cache: Dict[Tuple[str, str, str], float] = {}
        self._cache_hits = 0
        self._cache_misses = 0
        self._cache_size_limit = 1000
        
        # Advanced mechanics
        self.synergies: Dict[Tuple[str, str], float] = {}
        self.combos: Dict[Tuple[str, ...], float] = {}
        self.adaptive_resistances: Dict[Tuple[str, str], float] = {}
        
        # Performance tracking
        self._calculation_times = []
        self._last_cleanup = time.time()
        
        # Load data
        self._load_type_data(data_path)
        self._build_matrix()
        
        # Precompute common operations if performance mode
        if self._performance_mode:
            self._precompute_common()
    
    def _load_type_data(self, data_path: Optional[str] = None) -> None:
        """
        Load type data from JSON file.
        
        Args:
            data_path: Optional path to types.json
        """
        if data_path is None:
            # Try to find types.json in standard locations
            possible_paths = [
                Path("data/types.json"),
                Path("../data/types.json"),
                Path("../../data/types.json"),
                Path("/Users/leon/Desktop/untold_story/data/types.json")
            ]
            
            for path in possible_paths:
                if path.exists():
                    data_path = str(path)
                    break
            else:
                # Use default data if file not found
                self._use_default_data()
                return
        
        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Parse types
            for i, type_name in enumerate(data.get('types', [])):
                self.types[type_name] = TypeData(
                    name=type_name,
                    id=i,
                    description=data.get('descriptions', {}).get(type_name, "")
                )
                self.type_names.append(type_name)
                self.type_ids[type_name] = i
            
            # Parse type chart - Handle both old and new format
            self.relations: List[TypeRelation] = []
            for entry in data.get('chart', []):
                # Support both field naming conventions
                attacker = entry.get('attacker') or entry.get('att')
                defender = entry.get('defender') or entry.get('def') 
                multiplier = entry.get('multiplier') or entry.get('x')
                
                if attacker and defender and multiplier is not None:
                    att_id = self.type_ids.get(attacker)
                    def_id = self.type_ids.get(defender)
                    if att_id is not None and def_id is not None:
                        self.relations.append(TypeRelation(att_id, def_id, multiplier))
            
            # Load configuration
            self.config['stab_multiplier'] = data.get('stab', 1.2)
            
            # Set legendary type attributes
            if 'Gottheit' in self.types:
                self.types['Gottheit'].attributes |= TypeAttribute.LEGENDARY
            if 'Teufel' in self.types:
                self.types['Teufel'].attributes |= TypeAttribute.CORRUPTED | TypeAttribute.CORRUPTED
                
        except Exception as e:
            warnings.warn(f"Error loading type data: {e}. Using defaults.")
            self._use_default_data()
    
    def _use_default_data(self) -> None:
        """Use default German type data if file loading fails."""
        default_types = [
            "Feuer", "Wasser", "Erde", "Luft", "Pflanze", "Bestie",
            "Energie", "Chaos", "Seuche", "Mystik", "Gottheit", "Teufel"
        ]
        
        for i, type_name in enumerate(default_types):
            self.types[type_name] = TypeData(name=type_name, id=i)
            self.type_names.append(type_name)
            self.type_ids[type_name] = i
        
        # Basic effectiveness relationships
        self.relations = [
            TypeRelation(self.type_ids["Feuer"], self.type_ids["Pflanze"], 2.0),
            TypeRelation(self.type_ids["Feuer"], self.type_ids["Wasser"], 0.5),
            TypeRelation(self.type_ids["Wasser"], self.type_ids["Feuer"], 2.0),
            TypeRelation(self.type_ids["Wasser"], self.type_ids["Erde"], 2.0),
            TypeRelation(self.type_ids["Erde"], self.type_ids["Energie"], 2.0),
            TypeRelation(self.type_ids["Luft"], self.type_ids["Erde"], 2.0),
            # Add more as needed
        ]
    
    def _build_matrix(self) -> None:
        """Build NumPy effectiveness matrix for fast lookups."""
        if not NUMPY_AVAILABLE:
            self._build_fallback_matrix()
            return
            
        n_types = len(self.types)
        
        # OPTIMIERT: Verwende float32 für bessere Performance
        self.effectiveness_matrix = np.ones((n_types, n_types), dtype=np.float32)
        
        # Apply type relations
        for relation in self.relations:
            self.effectiveness_matrix[relation.attacker_id, relation.defender_id] = relation.multiplier
        
        self._matrix_initialized = True
    
    def _build_fallback_matrix(self) -> None:
        """Fallback matrix implementation without NumPy."""
        n_types = len(self.types)
        self.effectiveness_matrix = [[1.0 for _ in range(n_types)] for _ in range(n_types)]
        
        # Apply type relations
        for relation in self.relations:
            self.effectiveness_matrix[relation.attacker_id][relation.defender_id] = relation.multiplier
        
        self._matrix_initialized = True
    
    def _precompute_common(self) -> None:
        """Precompute common type matchups for performance."""
        # Cache common single-type matchups
        common_types = ["Feuer", "Wasser", "Erde", "Luft", "Pflanze", "Bestie"]
        for att in common_types:
            for def_ in common_types:
                self.get_effectiveness(att, def_)
        
        # Cache common dual-type combinations
        common_dual = [
            ["Feuer", "Erde"], ["Wasser", "Pflanze"], ["Luft", "Energie"]
        ]
        for types in common_dual:
            for att in common_types:
                self.calculate_type_multiplier(att, types)
    
    def _cleanup_cache(self) -> None:
        """Clean up cache if it gets too large."""
        current_time = time.time()
        
        # Clean up every 5 minutes
        if current_time - self._last_cleanup > 300:
            if len(self.lookup_cache) > self._cache_size_limit:
                # Remove oldest entries
                items_to_remove = len(self.lookup_cache) - self._cache_size_limit
                oldest_keys = sorted(self.lookup_cache.keys(), 
                                   key=lambda k: self.lookup_cache.get(k, 0))[:items_to_remove]
                
                for key in oldest_keys:
                    self.lookup_cache.pop(key, None)
            
            self._last_cleanup = current_time
    
    @lru_cache(maxsize=256)
    def get_effectiveness(self, attacking_type: str, defending_type: str,
                         condition: BattleCondition = BattleCondition.NORMAL) -> float:
        """
        Get type effectiveness multiplier.
        OPTIMIERT: LRU-Cache und NumPy-Matrix-Lookups
        """
        start_time = time.time()
        
        # Check cache first
        cache_key = (attacking_type, defending_type, condition.value)
        if cache_key in self.lookup_cache:
            self._cache_hits += 1
            return self.lookup_cache[cache_key]
        
        self._cache_misses += 1
        
        # Get type IDs
        att_id = self.type_ids.get(attacking_type)
        def_id = self.type_ids.get(defending_type)
        
        if att_id is None or def_id is None:
            return 1.0
        
        # OPTIMIERT: NumPy-Matrix-Lookup wenn verfügbar
        if NUMPY_AVAILABLE and self._matrix_initialized:
            multiplier = float(self.effectiveness_matrix[att_id, def_id])
        else:
            # Fallback: Durchsuche Relations
            multiplier = 1.0
            for relation in self.relations:
                if relation.attacker_id == att_id and relation.defender_id == def_id:
                    multiplier = relation.multiplier
                    break
        
        # Apply battle conditions
        if condition == BattleCondition.INVERSE:
            if multiplier > 1:
                multiplier = 0.5
            elif multiplier < 1:
                multiplier = 2.0
        elif condition == BattleCondition.CHAOS:
            # Random effectiveness modifier
            multiplier *= random.uniform(0.5, 2.0)
        elif condition == BattleCondition.PURE:
            # Only STAB moves are effective
            if attacking_type != defending_type:
                multiplier = 0.5
        
        # Cache result
        self.lookup_cache[cache_key] = multiplier
        
        # Track performance
        calc_time = time.time() - start_time
        self._calculation_times.append(calc_time)
        
        # Cleanup cache if needed
        self._cleanup_cache()
        
        return multiplier
    
    def calculate_type_multiplier(self, attacking_type: str, defending_types: List[str]) -> float:
        """
        Calculate effectiveness against dual-type defenders.
        OPTIMIERT: NumPy-Vektoroperationen für bessere Performance
        """
        if not defending_types:
            return 1.0
        
        if len(defending_types) == 1:
            return self.get_effectiveness(attacking_type, defending_types[0])
        
        # OPTIMIERT: Batch-Berechnung mit NumPy wenn verfügbar
        if NUMPY_AVAILABLE and self._matrix_initialized:
            att_id = self.type_ids.get(attacking_type)
            if att_id is None:
                return 1.0
            
            # Hole alle Multiplikatoren auf einmal
            def_ids = [self.type_ids.get(t) for t in defending_types if self.type_ids.get(t) is not None]
            if not def_ids:
                return 1.0
            
            # OPTIMIERT: NumPy-Vektoroperation
            multipliers = self.effectiveness_matrix[att_id, def_ids]
            total_multiplier = np.prod(multipliers)
            
            # Cap at maximum
            return min(float(total_multiplier), self.config['combo_cap'])
        else:
            # Fallback: Einzelne Berechnungen
            total_multiplier = 1.0
            for def_type in defending_types:
                total_multiplier *= self.get_effectiveness(attacking_type, def_type)
            
            return min(total_multiplier, self.config['combo_cap'])
    
    def get_effectiveness_matrix(self) -> Optional[np.ndarray]:
        """Get the effectiveness matrix for external use."""
        return self.effectiveness_matrix.copy() if self._matrix_initialized else None
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        return {
            'cache_hits': self._cache_hits,
            'cache_misses': self._cache_misses,
            'cache_hit_rate': self._cache_hits / max(1, self._cache_hits + self._cache_misses),
            'avg_calculation_time': sum(self._calculation_times) / max(1, len(self._calculation_times)),
            'matrix_initialized': self._matrix_initialized,
            'numpy_available': NUMPY_AVAILABLE,
            'cache_size': len(self.lookup_cache)
        }
    
    def clear_cache(self) -> None:
        """Clear all caches."""
        self.lookup_cache.clear()
        self._cache_hits = 0
        self._cache_misses = 0
        self._calculation_times.clear()


class TypeSystemAPI:
    """
    High-level API for type system interactions.
    Provides convenient methods for game logic.
    """
    
    def __init__(self):
        """Initialize API with type chart."""
        self.chart = TypeChart()
        self.battle_condition = BattleCondition.NORMAL
    
    def set_battle_condition(self, condition: BattleCondition) -> None:
        """
        Set current battle condition.
        
        Args:
            condition: Battle condition to apply
        """
        self.battle_condition = condition
    
    def check_type_effectiveness(self, move_type: str, defender_types: List[str],
                                attacker_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Check type effectiveness with detailed information.
        
        Args:
            move_type: Type of the move
            defender_types: Defender's types
            attacker_types: Optional attacker types for STAB
            
        Returns:
            Detailed effectiveness information
        """
        multiplier = self.chart.calculate_type_multiplier(
            move_type, defender_types, self.battle_condition
        )
        
        # Check for STAB
        has_stab = False
        if attacker_types and move_type in attacker_types:
            has_stab = True
            multiplier *= self.chart.config['stab_multiplier']
        
        # Determine effectiveness category
        if multiplier == 0:
            category = "immune"
            message = "Hat keine Wirkung..."
            color = (128, 128, 128)
        elif multiplier < 0.5:
            category = "very_weak"
            message = "Kaum effektiv..."
            color = (150, 50, 50)
        elif multiplier < 1.0:
            category = "weak"
            message = "Nicht sehr effektiv..."
            color = (200, 100, 100)
        elif multiplier > 2.0:
            category = "super_strong"
            message = "Extrem effektiv!"
            color = (50, 255, 50)
        elif multiplier > 1.0:
            category = "strong"
            message = "Sehr effektiv!"
            color = (100, 200, 100)
        else:
            category = "neutral"
            message = "Normal effektiv"
            color = (255, 255, 255)
        
        if has_stab:
            message += " (STAB-Bonus!)"
        
        return {
            'multiplier': multiplier,
            'category': category,
            'message': message,
            'color': color,
            'has_stab': has_stab,
            'is_super_effective': multiplier > 1.0,
            'is_not_very_effective': 0 < multiplier < 1.0,
            'is_immune': multiplier == 0
        }
    
    def analyze_team_composition(self, team: List[List[str]]) -> Dict[str, Any]:
        """
        Analyze a team's type composition.
        
        Args:
            team: List of monster type combinations
            
        Returns:
            Team analysis
        """
        if not team:
            return {'offensive_coverage': {}, 'defensive_weaknesses': [], 
                   'synergy_score': 0, 'balance_score': 0}
        
        # Collect all unique move types
        all_types = set()
        for monster_types in team:
            all_types.update(monster_types)
        
        # Offensive coverage
        offensive_coverage = self.chart.get_type_coverage_analysis(list(all_types))
        
        # Defensive weaknesses
        all_weaknesses = {}
        for monster_types in team:
            profile = self.chart.get_defensive_profile(monster_types)
            for weakness in profile['weaknesses']:
                all_weaknesses[weakness] = all_weaknesses.get(weakness, 0) + 1
        
        # Find common weaknesses
        common_weaknesses = [w for w, count in all_weaknesses.items() 
                            if count >= len(team) / 2]
        
        # Calculate synergy score
        synergy_score = self._calculate_team_synergy(team)
        
        # Calculate balance score
        type_diversity = len(all_types) / len(self.chart.type_names)
        role_coverage = min(offensive_coverage['coverage_score'], 
                          1.0 - len(common_weaknesses) / len(self.chart.type_names))
        balance_score = (type_diversity + role_coverage + synergy_score) / 3
        
        return {
            'offensive_coverage': offensive_coverage,
            'defensive_weaknesses': common_weaknesses,
            'all_weaknesses': all_weaknesses,
            'synergy_score': synergy_score,
            'balance_score': balance_score,
            'type_diversity': type_diversity
        }
    
    def _calculate_team_synergy(self, team: List[List[str]]) -> float:
        """
        Calculate team synergy score.
        
        Args:
            team: List of monster type combinations
            
        Returns:
            Synergy score (0-1)
        """
        if len(team) < 2:
            return 1.0
        
        synergy_points = 0
        comparisons = 0
        
        # Check how well team members cover each other's weaknesses
        for i, types_i in enumerate(team):
            profile_i = self.chart.get_defensive_profile(types_i)
            
            for j, types_j in enumerate(team):
                if i == j:
                    continue
                
                # Check if j can handle i's weaknesses
                for weakness in profile_i['weaknesses']:
                    for type_j in types_j:
                        effectiveness = self.chart.get_effectiveness(weakness, type_j)
                        if effectiveness < 1.0:
                            synergy_points += 1
                
                comparisons += len(profile_i['weaknesses'])
        
        return synergy_points / comparisons if comparisons > 0 else 0.5
    
    def predict_matchup(self, attacker_types: List[str], 
                       defender_types: List[str]) -> Dict[str, Any]:
        """
        Predict matchup outcome.
        
        Args:
            attacker_types: Attacker's types
            defender_types: Defender's types
            
        Returns:
            Matchup prediction
        """
        # Calculate offensive advantage
        offensive_score = 0
        for att_type in attacker_types:
            effectiveness = self.chart.calculate_type_multiplier(att_type, defender_types)
            offensive_score += effectiveness
        offensive_score /= len(attacker_types) if attacker_types else 1
        
        # Calculate defensive advantage
        defensive_score = 0
        for def_type in defender_types:
            effectiveness = self.chart.calculate_type_multiplier(def_type, attacker_types)
            defensive_score += effectiveness
        defensive_score /= len(defender_types) if defender_types else 1
        
        # Determine advantage
        advantage_ratio = offensive_score / defensive_score if defensive_score > 0 else offensive_score
        
        if advantage_ratio > 1.2:
            advantage = "attacker"
            confidence = min((advantage_ratio - 1) * 100, 100)
        elif advantage_ratio < 0.8:
            advantage = "defender"
            confidence = min((1 / advantage_ratio - 1) * 100, 100)
        else:
            advantage = "neutral"
            confidence = 100 - abs(advantage_ratio - 1) * 100
        
        # Key factors
        key_factors = []
        
        for att_type in attacker_types:
            eff = self.chart.calculate_type_multiplier(att_type, defender_types)
            if eff >= 2.0:
                key_factors.append(f"{att_type} → {defender_types}: {eff}x")
        
        for def_type in defender_types:
            eff = self.chart.calculate_type_multiplier(def_type, attacker_types)
            if eff >= 2.0:
                key_factors.append(f"{def_type} → {attacker_types}: {eff}x")
        
        return {
            'advantage': advantage,
            'confidence': confidence,
            'offensive_score': offensive_score,
            'defensive_score': defensive_score,
            'advantage_ratio': advantage_ratio,
            'key_factors': key_factors[:3]  # Top 3 factors
        }


# Create global instances for convenience
type_chart = TypeChart()
type_api = TypeSystemAPI()