"""
Advanced Type System for Untold Story - Optimized Version 2.0
High-performance type effectiveness calculations with NumPy optimization
"""

import numpy as np
import json
from typing import List, Dict, Tuple, Optional, Set, Any, Union
from enum import Enum, IntEnum
from dataclasses import dataclass, field
from pathlib import Path
import time
from functools import lru_cache
import warnings


# Type attributes for advanced mechanics
class TypeAttribute(IntEnum):
    """Special attributes types can have."""
    PHYSICAL = 1
    MAGICAL = 2
    NATURAL = 4
    ARTIFICIAL = 8
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
        self.effectiveness_matrix: Optional[np.ndarray] = None
        
        # Caching structures
        self.lookup_cache: Dict[Tuple[str, str, str], float] = {}
        self._cache_hits = 0
        self._cache_misses = 0
        
        # Advanced mechanics
        self.synergies: Dict[Tuple[str, str], float] = {}
        self.combos: Dict[Tuple[str, ...], float] = {}
        self.adaptive_resistances: Dict[Tuple[str, str], float] = {}
        
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
                self.types['Teufel'].attributes |= TypeAttribute.LEGENDARY | TypeAttribute.CORRUPTED
                
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
        n_types = len(self.types)
        
        # Initialize with neutral effectiveness
        self.effectiveness_matrix = np.ones((n_types, n_types), dtype=np.float32)
        
        # Apply type relations
        for relation in self.relations:
            self.effectiveness_matrix[relation.attacker_id, relation.defender_id] = relation.multiplier
    
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
    
    @lru_cache(maxsize=256)
    def get_effectiveness(self, attacking_type: str, defending_type: str,
                         condition: BattleCondition = BattleCondition.NORMAL) -> float:
        """
        Get type effectiveness with caching.
        
        Args:
            attacking_type: Attacking type name
            defending_type: Defending type name
            condition: Battle condition modifier
            
        Returns:
            Effectiveness multiplier
        """
        # Check cache
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
        
        # Get base effectiveness
        effectiveness = float(self.effectiveness_matrix[att_id, def_id])
        
        # Apply battle condition
        if condition == BattleCondition.INVERSE:
            if effectiveness == 0:
                effectiveness = 2.0
            elif effectiveness < 1:
                effectiveness = 2.0
            elif effectiveness > 1:
                effectiveness = 0.5
        elif condition == BattleCondition.CHAOS:
            # Random modifier between 0.8x and 1.2x
            import random
            effectiveness *= random.uniform(0.8, 1.2)
        elif condition == BattleCondition.PURE:
            # Non-STAB moves are less effective
            effectiveness *= 0.7
        
        # Apply adaptive resistance if any
        resistance_key = (attacking_type, defending_type)
        if resistance_key in self.adaptive_resistances:
            effectiveness *= (1 - self.adaptive_resistances[resistance_key])
        
        # Cache result
        if len(self.lookup_cache) < self.config['cache_size']:
            self.lookup_cache[cache_key] = effectiveness
        
        return effectiveness
    
    def calculate_type_multiplier(self, move_type: str, defender_types: List[str],
                                 condition: BattleCondition = BattleCondition.NORMAL) -> float:
        """
        Calculate combined type effectiveness for multiple defender types.
        
        Args:
            move_type: Attacking move type
            defender_types: List of defender's types
            condition: Battle condition
            
        Returns:
            Combined effectiveness multiplier
        """
        if not defender_types:
            return 1.0
        
        # Use NumPy for efficient calculation
        multiplier = 1.0
        for def_type in defender_types:
            multiplier *= self.get_effectiveness(move_type, def_type, condition)
        
        # Apply combo cap
        multiplier = min(multiplier, self.config['combo_cap'])
        
        # Apply synergy bonus for dual types
        if len(defender_types) >= 2:
            synergy_bonus = self._calculate_synergy_bonus(defender_types)
            multiplier *= synergy_bonus
        
        return multiplier
    
    def _calculate_synergy_bonus(self, types: List[str]) -> float:
        """
        Calculate synergy bonus for type combinations.
        
        Args:
            types: List of types
            
        Returns:
            Synergy multiplier
        """
        if len(types) < 2:
            return 1.0
        
        # Check for known synergies
        type_pair = tuple(sorted(types[:2]))
        
        # Define synergistic type combinations
        synergies = {
            ("Erde", "Feuer"): 1.1,  # Volcanic synergy
            ("Luft", "Wasser"): 1.1,  # Storm synergy
            ("Mystik", "Energie"): 1.15,  # Techno-magic synergy
            ("Pflanze", "Wasser"): 1.1,  # Growth synergy
        }
        
        return synergies.get(type_pair, 1.0)
    
    def accumulate_adaptive_resistance(self, attacking_type: str, 
                                      defending_type: str) -> None:
        """
        Accumulate adaptive resistance (monster learns from repeated attacks).
        
        Args:
            attacking_type: Type that attacked
            defending_type: Type that defended
        """
        key = (attacking_type, defending_type)
        current = self.adaptive_resistances.get(key, 0.0)
        
        # Increase resistance with diminishing returns
        new_resistance = current + self.config['adaptive_rate'] * (1 - current)
        new_resistance = min(new_resistance, 0.5)  # Cap at 50% resistance
        
        self.adaptive_resistances[key] = new_resistance
    
    def reset_adaptive_resistances(self) -> None:
        """Reset all adaptive resistances."""
        self.adaptive_resistances.clear()
    
    def get_type_coverage_analysis(self, move_types: List[str]) -> Dict[str, Any]:
        """
        Analyze offensive type coverage using NumPy.
        
        Args:
            move_types: List of available move types
            
        Returns:
            Coverage analysis dictionary
        """
        if not move_types:
            return {'coverage_score': 0, 'super_effective': [], 'not_very_effective': [], 
                   'no_effect': [], 'recommendations': []}
        
        # Build coverage matrix
        move_ids = [self.type_ids.get(t, -1) for t in move_types]
        move_ids = [i for i in move_ids if i >= 0]
        
        if not move_ids:
            return {'coverage_score': 0, 'super_effective': [], 'not_very_effective': [], 
                   'no_effect': [], 'recommendations': []}
        
        # Get effectiveness for all type matchups
        coverage_matrix = self.effectiveness_matrix[move_ids, :]
        
        # Find best effectiveness against each type
        best_effectiveness = np.max(coverage_matrix, axis=0)
        
        # Categorize coverage
        super_effective = []
        not_very_effective = []
        no_effect = []
        
        for i, effectiveness in enumerate(best_effectiveness):
            type_name = self.type_names[i]
            if effectiveness >= 2.0:
                super_effective.append(type_name)
            elif effectiveness < 1.0 and effectiveness > 0:
                not_very_effective.append(type_name)
            elif effectiveness == 0:
                no_effect.append(type_name)
        
        # Calculate coverage score
        coverage_score = np.mean(np.minimum(best_effectiveness, 2.0)) / 2.0
        
        # Find recommended types to add
        recommendations = self._recommend_coverage_types(coverage_matrix)
        
        return {
            'coverage_score': float(coverage_score),
            'super_effective': super_effective,
            'not_very_effective': not_very_effective,
            'no_effect': no_effect,
            'recommendations': recommendations
        }
    
    def _recommend_coverage_types(self, current_coverage: np.ndarray) -> List[str]:
        """
        Recommend types to improve coverage.
        
        Args:
            current_coverage: Current coverage matrix
            
        Returns:
            List of recommended type names
        """
        # Find weak coverage points
        best_effectiveness = np.max(current_coverage, axis=0)
        weak_indices = np.where(best_effectiveness < 1.0)[0]
        
        if len(weak_indices) == 0:
            return []
        
        # Find types that would improve coverage
        recommendations = []
        improvement_scores = []
        
        for type_id, type_name in enumerate(self.type_names):
            if type_id in current_coverage:
                continue
            
            # Calculate improvement
            new_effectiveness = self.effectiveness_matrix[type_id, weak_indices]
            improvement = np.sum(np.maximum(new_effectiveness - best_effectiveness[weak_indices], 0))
            
            if improvement > 0:
                recommendations.append(type_name)
                improvement_scores.append(improvement)
        
        # Sort by improvement and return top 3
        if recommendations:
            sorted_recs = [x for _, x in sorted(zip(improvement_scores, recommendations), 
                                               reverse=True)]
            return sorted_recs[:3]
        
        return []
    
    def get_defensive_profile(self, monster_types: List[str]) -> Dict[str, Any]:
        """
        Analyze defensive strengths and weaknesses.
        
        Args:
            monster_types: Monster's types
            
        Returns:
            Defensive analysis
        """
        if not monster_types:
            return {'weaknesses': [], 'resistances': [], 'immunities': [], 
                   'defensive_score': 0.5}
        
        weaknesses = []
        resistances = []
        immunities = []
        
        # Check all attacking types
        for attacking_type in self.type_names:
            multiplier = self.calculate_type_multiplier(attacking_type, monster_types)
            
            if multiplier > 1.0:
                weaknesses.append((attacking_type, multiplier))
            elif 0 < multiplier < 1.0:
                resistances.append((attacking_type, multiplier))
            elif multiplier == 0:
                immunities.append(attacking_type)
        
        # Sort by severity
        weaknesses.sort(key=lambda x: x[1], reverse=True)
        resistances.sort(key=lambda x: x[1])
        
        # Calculate defensive score
        n_types = len(self.type_names)
        avg_damage_taken = sum(self.calculate_type_multiplier(t, monster_types) 
                              for t in self.type_names) / n_types
        defensive_score = 2.0 / (1.0 + avg_damage_taken)  # Higher score = better defense
        
        return {
            'weaknesses': [t for t, _ in weaknesses],
            'resistances': [t for t, _ in resistances],
            'immunities': immunities,
            'defensive_score': defensive_score,
            'weakness_details': weaknesses,
            'resistance_details': resistances
        }
    
    def validate_type_balance(self) -> Dict[str, Any]:
        """
        Validate type balance in the system.
        
        Returns:
            Balance analysis
        """
        type_scores = {}
        
        for type_name in self.type_names:
            # Offensive score
            offensive_score = 0
            for defender in self.type_names:
                effectiveness = self.get_effectiveness(type_name, defender)
                if effectiveness > 1:
                    offensive_score += effectiveness
                elif effectiveness < 1:
                    offensive_score -= (1 - effectiveness)
            
            # Defensive score
            defensive_score = 0
            for attacker in self.type_names:
                effectiveness = self.get_effectiveness(attacker, type_name)
                if effectiveness > 1:
                    defensive_score -= effectiveness
                elif effectiveness < 1:
                    defensive_score += (1 - effectiveness)
            
            type_scores[type_name] = {
                'offensive': offensive_score,
                'defensive': defensive_score,
                'total': offensive_score + defensive_score
            }
        
        # Find imbalanced types
        scores = [s['total'] for s in type_scores.values()]
        mean_score = np.mean(scores)
        std_score = np.std(scores)
        
        overpowered = [(t, s['total']) for t, s in type_scores.items() 
                      if s['total'] > mean_score + std_score]
        underpowered = [(t, s['total']) for t, s in type_scores.items() 
                       if s['total'] < mean_score - std_score]
        
        balance_score = 1.0 - (std_score / (abs(mean_score) + 1))
        
        return {
            'balance_score': balance_score,
            'type_scores': type_scores,
            'overpowered_types': overpowered,
            'underpowered_types': underpowered,
            'mean_score': mean_score,
            'std_deviation': std_score
        }
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Get performance statistics.
        
        Returns:
            Performance metrics
        """
        total_cache_ops = self._cache_hits + self._cache_misses
        cache_hit_rate = self._cache_hits / total_cache_ops if total_cache_ops > 0 else 0
        
        return {
            'cache_hits': self._cache_hits,
            'cache_misses': self._cache_misses,
            'cache_hit_rate': cache_hit_rate,
            'cache_size': len(self.lookup_cache),
            'matrix_memory_bytes': self.effectiveness_matrix.nbytes if self.effectiveness_matrix is not None else 0,
            'initialization_time': self._init_time,
            'adaptive_resistances': len(self.adaptive_resistances)
        }
    
    def export_matrix(self, path: str) -> None:
        """
        Export effectiveness matrix to file.
        
        Args:
            path: Export path
        """
        np.save(path, self.effectiveness_matrix)
    
    def import_matrix(self, path: str) -> None:
        """
        Import effectiveness matrix from file.
        
        Args:
            path: Import path
        """
        self.effectiveness_matrix = np.load(path)


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