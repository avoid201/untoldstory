"""
Monster synthesis/fusion system.
Combines two parent monsters to create a new offspring with inherited traits.
"""

from typing import TYPE_CHECKING, Optional, List, Tuple, Dict, Set
from dataclasses import dataclass
import random
import math

if TYPE_CHECKING:
    from engine.systems.monster_instance import MonsterInstance
    from engine.systems.monsters import MonsterSpecies
    from engine.systems.moves import Move


@dataclass
class SynthesisResult:
    """Result of a synthesis attempt."""
    offspring_species: 'MonsterSpecies'
    inherited_moves: List['Move']
    inherited_traits: List[str]
    plus_value: int
    parent1_consumed: bool
    parent2_consumed: bool
    special_fusion: bool
    description: str


class SynthesisRules:
    """Rules and formulas for monster synthesis."""
    
    # Rank progression table
    RANK_VALUES = {
        'F': 1,
        'E': 2,
        'D': 3,
        'C': 4,
        'B': 5,
        'A': 6,
        'S': 7,
        'SS': 8,
        'X': 9
    }
    
    RANK_FROM_VALUE = {v: k for k, v in RANK_VALUES.items()}
    
    # Special fusion recipes (specific combinations)
    SPECIAL_RECIPES = {
        # Format: (parent1_id, parent2_id): result_id
        ('001', '002'): '020',  # Example: Glutkohle + Tropfstein = Special
        ('140', '141'): '150',  # Two legendaries = Ultimate legendary
        # Add more specific recipes
    }
    
    # Family-based fusion rules
    FAMILY_COMBINATIONS = {
        # (family1, family2): result_family
        ('beast', 'plant'): 'nature',
        ('fire', 'earth'): 'lava',
        ('water', 'air'): 'storm',
        ('energy', 'chaos'): 'void',
        ('holy', 'demon'): 'balance'
    }
    
    @staticmethod
    def can_synthesize(parent1: 'MonsterInstance', 
                       parent2: 'MonsterInstance') -> Tuple[bool, str]:
        """
        Check if two monsters can be synthesized.
        
        Args:
            parent1: First parent monster
            parent2: Second parent monster
            
        Returns:
            Tuple of (can_synthesize, reason_if_not)
        """
        # Can't fuse with itself
        if parent1 == parent2:
            return False, "Kann nicht mit sich selbst fusionieren!"
        
        # Level requirement (both must be at least level 10)
        if parent1.level < 10 or parent2.level < 10:
            return False, "Beide Monster müssen mindestens Level 10 sein!"
        
        # Check for synthesis lock flag
        if hasattr(parent1, 'synthesis_locked') and parent1.synthesis_locked:
            return False, f"{parent1.nickname or parent1.species.name} kann nicht fusioniert werden!"
        if hasattr(parent2, 'synthesis_locked') and parent2.synthesis_locked:
            return False, f"{parent2.nickname or parent2.species.name} kann nicht fusioniert werden!"
        
        # Special monsters might have restrictions
        if hasattr(parent1.species, 'no_synthesis') and parent1.species.no_synthesis:
            return False, f"{parent1.species.name} kann nicht für Synthese verwendet werden!"
        if hasattr(parent2.species, 'no_synthesis') and parent2.species.no_synthesis:
            return False, f"{parent2.species.name} kann nicht für Synthese verwendet werden!"
        
        return True, ""


class SynthesisCalculator:
    """Calculates synthesis results."""
    
    def __init__(self, monster_database: Dict[str, 'MonsterSpecies']):
        """
        Initialize synthesis calculator.
        
        Args:
            monster_database: Dictionary of all monster species
        """
        self.monster_db = monster_database
        self.rng = random.Random()
    
    def synthesize(self, parent1: 'MonsterInstance',
                  parent2: 'MonsterInstance',
                  seed: Optional[int] = None) -> Optional[SynthesisResult]:
        """
        Perform monster synthesis.
        
        Args:
            parent1: First parent
            parent2: Second parent
            seed: Random seed for deterministic results
            
        Returns:
            SynthesisResult or None if synthesis fails
        """
        if seed is not None:
            self.rng.seed(seed)
        
        # Check if synthesis is possible
        can_do, reason = SynthesisRules.can_synthesize(parent1, parent2)
        if not can_do:
            return None
        
        # Check for special recipe first
        special_result = self._check_special_recipe(parent1, parent2)
        if special_result:
            return special_result
        
        # Calculate offspring species
        offspring_species = self._calculate_offspring_species(parent1, parent2)
        if not offspring_species:
            return None
        
        # Calculate plus value
        plus_value = self._calculate_plus_value(parent1, parent2)
        
        # Inherit moves
        inherited_moves = self._inherit_moves(parent1, parent2, offspring_species)
        
        # Inherit traits
        inherited_traits = self._inherit_traits(parent1, parent2)
        
        # Determine if parents are consumed
        parent1_consumed = True  # Standard synthesis consumes both
        parent2_consumed = True
        
        # Create result
        return SynthesisResult(
            offspring_species=offspring_species,
            inherited_moves=inherited_moves,
            inherited_traits=inherited_traits,
            plus_value=plus_value,
            parent1_consumed=parent1_consumed,
            parent2_consumed=parent2_consumed,
            special_fusion=False,
            description=self._generate_description(parent1, parent2, offspring_species)
        )
    
    def _check_special_recipe(self, parent1: 'MonsterInstance',
                             parent2: 'MonsterInstance') -> Optional[SynthesisResult]:
        """Check for special fusion recipes."""
        # Check both orderings
        key1 = (parent1.species.id, parent2.species.id)
        key2 = (parent2.species.id, parent1.species.id)
        
        result_id = None
        if key1 in SynthesisRules.SPECIAL_RECIPES:
            result_id = SynthesisRules.SPECIAL_RECIPES[key1]
        elif key2 in SynthesisRules.SPECIAL_RECIPES:
            result_id = SynthesisRules.SPECIAL_RECIPES[key2]
        
        if result_id and result_id in self.monster_db:
            offspring_species = self.monster_db[result_id]
            
            # Special fusions get bonus inherited moves and traits
            inherited_moves = self._inherit_moves(parent1, parent2, offspring_species, bonus=2)
            inherited_traits = self._inherit_traits(parent1, parent2, special=True)
            plus_value = self._calculate_plus_value(parent1, parent2) + 10  # Bonus
            
            return SynthesisResult(
                offspring_species=offspring_species,
                inherited_moves=inherited_moves,
                inherited_traits=inherited_traits,
                plus_value=plus_value,
                parent1_consumed=True,
                parent2_consumed=True,
                special_fusion=True,
                description=f"Spezielle Fusion! {offspring_species.name} erscheint!"
            )
        
        return None
    
    def _calculate_offspring_species(self, parent1: 'MonsterInstance',
                                    parent2: 'MonsterInstance') -> Optional['MonsterSpecies']:
        """Calculate the resulting species from synthesis."""
        # Get parent ranks
        rank1 = SynthesisRules.RANK_VALUES.get(parent1.species.rank, 4)
        rank2 = SynthesisRules.RANK_VALUES.get(parent2.species.rank, 4)
        
        # Calculate target rank (average + bonus for high plus values)
        plus_bonus = (getattr(parent1, 'plus_value', 0) + 
                     getattr(parent2, 'plus_value', 0)) // 20
        target_rank_value = (rank1 + rank2) // 2 + plus_bonus
        target_rank_value = max(1, min(9, target_rank_value))
        target_rank = SynthesisRules.RANK_FROM_VALUE[target_rank_value]
        
        # Get parent types
        types1 = set(parent1.species.types)
        types2 = set(parent2.species.types)
        
        # Determine result types (combination or dominant)
        if types1 & types2:  # Common type
            result_types = list(types1 & types2)
        else:
            # Take one type from each parent
            result_types = [
                self.rng.choice(list(types1)),
                self.rng.choice(list(types2))
            ]
        
        # Find candidates with matching rank and compatible types
        candidates = []
        for species in self.monster_db.values():
            # Skip special/legendary monsters
            if hasattr(species, 'no_synthesis_result') and species.no_synthesis_result:
                continue
            
            # Check rank
            if species.rank != target_rank:
                continue
            
            # Check type compatibility
            species_types = set(species.types)
            if any(t in species_types for t in result_types):
                candidates.append(species)
        
        if not candidates:
            # Fallback: find any monster of target rank
            candidates = [s for s in self.monster_db.values() 
                         if s.rank == target_rank and 
                         not (hasattr(s, 'no_synthesis_result') and s.no_synthesis_result)]
        
        if candidates:
            # Prefer monsters from same era
            era_candidates = [c for c in candidates 
                             if hasattr(c, 'era') and c.era == parent1.species.era]
            if era_candidates:
                return self.rng.choice(era_candidates)
            return self.rng.choice(candidates)
        
        return None
    
    def _calculate_plus_value(self, parent1: 'MonsterInstance',
                             parent2: 'MonsterInstance') -> int:
        """Calculate plus value for offspring."""
        # Get parent plus values
        plus1 = getattr(parent1, 'plus_value', 0)
        plus2 = getattr(parent2, 'plus_value', 0)
        
        # Base calculation: average + small increase
        base_plus = (plus1 + plus2) // 2 + self.rng.randint(1, 5)
        
        # Bonus for high level parents
        level_bonus = (parent1.level + parent2.level) // 20
        
        # Bonus for same species
        species_bonus = 5 if parent1.species.id == parent2.species.id else 0
        
        # Cap at 99
        return min(99, base_plus + level_bonus + species_bonus)
    
    def _inherit_moves(self, parent1: 'MonsterInstance',
                      parent2: 'MonsterInstance',
                      offspring_species: 'MonsterSpecies',
                      bonus: int = 0) -> List['Move']:
        """Determine inherited moves."""
        inherited = []
        
        # Get all parent moves
        parent_moves = []
        for move in parent1.moves:
            if move and move not in parent_moves:
                parent_moves.append(move)
        for move in parent2.moves:
            if move and move not in parent_moves:
                parent_moves.append(move)
        
        # Number of moves to inherit (usually 1-2, more with bonus)
        num_inherited = min(4, self.rng.randint(1, 2) + bonus)
        
        # Prioritize powerful or rare moves
        parent_moves.sort(key=lambda m: m.power if m.category in ['phys', 'mag'] else 0, 
                         reverse=True)
        
        # Select moves
        for move in parent_moves[:num_inherited]:
            # Check if offspring can learn this move
            can_learn = self._can_species_learn_move(offspring_species, move)
            if can_learn:
                inherited.append(move)
        
        return inherited
    
    def _can_species_learn_move(self, species: 'MonsterSpecies', move: 'Move') -> bool:
        """Check if a species can learn a move."""
        # Check type compatibility
        if move.type in species.types:
            return True
        
        # Check if in natural learnset
        if hasattr(species, 'learnset'):
            for learn_data in species.learnset:
                if learn_data['move'] == move.id:
                    return True
        
        # Special moves might have restrictions
        if hasattr(move, 'inheritable') and not move.inheritable:
            return False
        
        # 50% chance for off-type moves
        return self.rng.random() < 0.5
    
    def _inherit_traits(self, parent1: 'MonsterInstance',
                       parent2: 'MonsterInstance',
                       special: bool = False) -> List[str]:
        """Determine inherited traits."""
        inherited = []
        
        # Get parent traits
        traits1 = getattr(parent1, 'traits', [])
        traits2 = getattr(parent2, 'traits', [])
        all_traits = traits1 + traits2
        
        if not all_traits:
            return []
        
        # Number of traits to inherit
        max_traits = 3 if special else 2
        num_inherited = min(max_traits, len(all_traits))
        
        # Remove duplicates and select
        unique_traits = list(set(all_traits))
        self.rng.shuffle(unique_traits)
        inherited = unique_traits[:num_inherited]
        
        # Chance for trait mutation (new random trait)
        if self.rng.random() < 0.1:  # 10% chance
            inherited.append(self._generate_random_trait())
        
        return inherited[:max_traits]  # Ensure we don't exceed max
    
    def _generate_random_trait(self) -> str:
        """Generate a random trait."""
        traits = [
            'sturdy',      # Takes less damage
            'aggressive',  # +10% attack
            'defensive',   # +10% defense
            'swift',       # +10% speed
            'lucky',       # +10% crit chance
            'healthy',     # +10% HP
            'magical',     # +10% magic attack
            'resistant',   # +10% magic defense
            'intimidating', # Lowers enemy attack on entry
            'inspiring',   # Boosts ally stats
        ]
        return self.rng.choice(traits)
    
    def _generate_description(self, parent1: 'MonsterInstance',
                             parent2: 'MonsterInstance',
                             offspring: 'MonsterSpecies') -> str:
        """Generate synthesis description."""
        p1_name = parent1.nickname or parent1.species.name
        p2_name = parent2.nickname or parent2.species.name
        
        return f"{p1_name} und {p2_name} verschmelzen zu {offspring.name}!"


class SynthesisPreview:
    """Preview synthesis results without consuming monsters."""
    
    @staticmethod
    def preview(parent1: 'MonsterInstance',
               parent2: 'MonsterInstance',
               calculator: SynthesisCalculator) -> Dict[str, any]:
        """
        Preview synthesis result without performing it.
        
        Args:
            parent1: First parent
            parent2: Second parent
            calculator: Synthesis calculator
            
        Returns:
            Preview information
        """
        # Check if possible
        can_do, reason = SynthesisRules.can_synthesize(parent1, parent2)
        if not can_do:
            return {
                'possible': False,
                'reason': reason
            }
        
        # Simulate synthesis with fixed seed for consistency
        seed = hash((parent1.species.id, parent2.species.id))
        result = calculator.synthesize(parent1, parent2, seed=seed)
        
        if not result:
            return {
                'possible': False,
                'reason': 'Synthese nicht möglich!'
            }
        
        return {
            'possible': True,
            'offspring_species': result.offspring_species.name,
            'offspring_rank': result.offspring_species.rank,
            'offspring_types': result.offspring_species.types,
            'estimated_plus': f"+{result.plus_value}",
            'special': result.special_fusion,
            'inherited_moves_count': len(result.inherited_moves),
            'inherited_traits_count': len(result.inherited_traits)
        }


class TraitEffects:
    """Effects of inherited traits."""
    
    TRAIT_MODIFIERS = {
        'sturdy': {
            'description': 'Reduziert erlittenen Schaden um 10%',
            'damage_reduction': 0.1
        },
        'aggressive': {
            'description': 'Erhöht Angriff um 10%',
            'stat_modifier': {'atk': 1.1}
        },
        'defensive': {
            'description': 'Erhöht Verteidigung um 10%',
            'stat_modifier': {'def': 1.1}
        },
        'swift': {
            'description': 'Erhöht Initiative um 10%',
            'stat_modifier': {'spd': 1.1}
        },
        'lucky': {
            'description': 'Erhöht kritische Trefferchance',
            'crit_bonus': 0.1
        },
        'healthy': {
            'description': 'Erhöht maximale KP um 10%',
            'stat_modifier': {'hp': 1.1}
        },
        'magical': {
            'description': 'Erhöht Magie-Angriff um 10%',
            'stat_modifier': {'mag': 1.1}
        },
        'resistant': {
            'description': 'Erhöht Magie-Verteidigung um 10%',
            'stat_modifier': {'res': 1.1}
        },
        'intimidating': {
            'description': 'Senkt gegnerischen Angriff beim Einwechseln',
            'on_switch_in': 'lower_enemy_attack'
        },
        'inspiring': {
            'description': 'Erhöht Werte von Verbündeten',
            'ally_boost': {'atk': 1.05, 'def': 1.05}
        }
    }
    
    @staticmethod
    def apply_trait_modifiers(base_stats: Dict[str, int], 
                             traits: List[str]) -> Dict[str, int]:
        """
        Apply trait modifiers to base stats.
        
        Args:
            base_stats: Base stat dictionary
            traits: List of trait IDs
            
        Returns:
            Modified stats
        """
        modified_stats = base_stats.copy()
        
        for trait in traits:
            if trait not in TraitEffects.TRAIT_MODIFIERS:
                continue
            
            modifiers = TraitEffects.TRAIT_MODIFIERS[trait]
            if 'stat_modifier' in modifiers:
                for stat, multiplier in modifiers['stat_modifier'].items():
                    if stat in modified_stats:
                        modified_stats[stat] = int(modified_stats[stat] * multiplier)
        
        return modified_stats