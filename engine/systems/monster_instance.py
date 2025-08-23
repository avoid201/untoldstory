"""
Monster Instance System for Untold Story
Individual monster instances with stats, moves, and progression
"""

from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from enum import Enum
import random
import logging
from engine.systems.stats import BaseStats, StatCalculator, Experience, GrowthCurve, StatStages
from engine.systems.moves import Move, move_registry
from engine.core.resources import resources

# Logger für bessere Fehlerverfolgung
logger = logging.getLogger(__name__)

class StatusCondition(Enum):
    """Status conditions that can affect monsters."""
    NONE = "none"
    BURN = "burn"          # Feuer damage over time, halves ATK
    POISON = "poison"      # Seuche damage over time
    PARALYSIS = "paralysis"  # May skip turn, reduces SPD
    SLEEP = "sleep"        # Cannot act for 1-3 turns
    FREEZE = "freeze"      # Cannot act until thawed
    CONFUSION = "confusion"  # May hurt itself
    FLINCH = "flinch"      # Skip next turn only
    
    @classmethod
    def from_string(cls, value: str) -> 'StatusCondition':
        """Konvertiere String zu StatusCondition mit Fallback."""
        try:
            if isinstance(value, str):
                return cls(value.lower())
            return value
        except (ValueError, AttributeError):
            return cls.NONE
    
    def __str__(self) -> str:
        return self.value
    
    def __eq__(self, other) -> bool:
        """Verbesserte Gleichheit für verschiedene Datentypen."""
        if isinstance(other, StatusCondition):
            return self.value == other.value
        elif isinstance(other, str):
            return self.value == other.lower()
        return False


class MonsterRank(Enum):
    """Monster rarity/power ranks."""
    F = "F"   # Common fodder
    E = "E"   # Common
    D = "D"   # Uncommon  
    C = "C"   # Uncommon+
    B = "B"   # Rare
    A = "A"   # Rare+
    S = "S"   # Epic
    SS = "SS"  # Epic+
    X = "X"   # Legendary
    
    @classmethod
    def from_string(cls, value: str) -> 'MonsterRank':
        """Konvertiere String zu MonsterRank mit Fallback."""
        try:
            if isinstance(value, str):
                return cls(value.upper())
            return value
        except (ValueError, AttributeError):
            return cls.E
    
    @property
    def capture_difficulty(self) -> float:
        """Get capture difficulty modifier for this rank."""
        modifiers = {
            "F": 1.5, "E": 1.2, "D": 1.0, "C": 0.9,
            "B": 0.8, "A": 0.7, "S": 0.5, "SS": 0.3, "X": 0.1
        }
        return modifiers.get(self.value, 1.0)
    
    @property
    def exp_modifier(self) -> float:
        """Get experience yield modifier for this rank."""
        modifiers = {
            "F": 0.8, "E": 1.0, "D": 1.1, "C": 1.2,
            "B": 1.4, "A": 1.6, "S": 2.0, "SS": 2.5, "X": 3.0
        }
        return modifiers.get(self.value, 1.0)


@dataclass
class MonsterSpecies:
    """Monster species data - shared across all instances."""
    id: int
    name: str
    era: str = "present"
    rank: MonsterRank = MonsterRank.E
    types: List[str] = None
    base_stats: BaseStats = None
    growth_curve: GrowthCurve = GrowthCurve.MEDIUM_FAST
    base_exp_yield: int = 64
    capture_rate: int = 45
    traits: List[str] = None
    learnset: List[Tuple[int, str]] = None
    evolution: Optional[Dict[str, Any]] = None
    description: str = ""
    
    def __post_init__(self):
        """Validiere und setze Standardwerte nach der Initialisierung."""
        if self.types is None:
            self.types = ["Bestie"]
        if self.traits is None:
            self.traits = []
        if self.learnset is None:
            self.learnset = []
        
        # Validiere kritische Felder
        if not isinstance(self.id, int):
            raise ValueError("ID muss eine Ganzzahl sein")
        if not self.name or not isinstance(self.name, str):
            raise ValueError("Name muss ein nicht-leerer String sein")
        if not isinstance(self.rank, MonsterRank):
            self.rank = MonsterRank.from_string(str(self.rank))
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MonsterSpecies':
        """Create MonsterSpecies from dictionary data."""
        try:
            if not isinstance(data, dict):
                raise ValueError("Daten müssen ein Dictionary sein")
            
            if "id" not in data or "name" not in data:
                raise ValueError("ID und Name sind erforderlich")
            
            # Convert growth curve string to enum
            growth_curve = GrowthCurve.MEDIUM_FAST
            curve_str = data.get("growth", {}).get("curve", "medium_fast")
            try:
                growth_curve = GrowthCurve(curve_str)
            except ValueError:
                logger.warning(f"Ungültige Growth Curve: {curve_str}, verwende Standard")
            
            # Convert rank string to enum
            rank = MonsterRank.E
            rank_str = data.get("rank", "E")
            try:
                rank = MonsterRank.from_string(str(rank_str))
            except ValueError:
                logger.warning(f"Ungültiger Rank: {rank_str}, verwende E")
            
            return cls(
                id=data["id"],
                name=data["name"],
                era=data.get("era", "present"),
                rank=rank,
                types=data.get("types", ["Bestie"]),
                base_stats=BaseStats.from_dict(data["base_stats"]) if "base_stats" in data else None,
                growth_curve=growth_curve,
                base_exp_yield=data.get("growth", {}).get("yield", 64),
                capture_rate=data.get("capture_rate", 45),
                traits=data.get("traits", []),
                learnset=[(l["level"], l["move"]) for l in data.get("learnset", [])],
                evolution=data.get("evolution"),
                description=data.get("description", "")
            )
        except Exception as e:
            logger.error(f"Fehler beim Erstellen der MonsterSpecies aus Dict: {e}")
            raise


class MonsterInstance:
    """
    An individual monster with its own stats, moves, and state.
    """
    
    def __init__(self, species: 'MonsterSpecies', level: int = 5,
                 nickname: Optional[str] = None):
        """
        Create a monster instance.
        
        Args:
            species: The species data
            level: Starting level
            nickname: Optional nickname
        """
        # Validiere Input-Parameter
        if not species:
            raise ValueError("Species darf nicht None sein")
        if not isinstance(level, int) or level < 1:
            raise ValueError("Level muss eine positive Ganzzahl sein")
        
        self.species = species
        self.nickname = nickname
        self.level = level
        
        # RNG für deterministische Tests (muss vor _generate_ivs gesetzt werden)
        self.rng = random.Random()
        
        # Individual Values (IVs) - genetic potential (0-31)
        self.ivs = self._generate_ivs()
        
        # Effort Values (EVs) - training bonuses (0-255 per stat, 510 total)
        self.evs = {
            "hp": 0, "atk": 0, "def": 0,
            "mag": 0, "res": 0, "spd": 0
        }
        
        # Nature (affects stat growth)
        self.nature = self._generate_nature()
        
        # Calculate stats
        try:
            self.stats = self._calculate_stats()
            self.max_hp = self.stats["hp"]
            self.current_hp = self.max_hp
        except Exception as e:
            logger.error(f"Fehler bei der Stats-Berechnung: {e}")
            # Fallback-Stats
            self.stats = {"hp": 100, "atk": 50, "def": 50, "mag": 30, "res": 30, "spd": 70}
            self.max_hp = 100
            self.current_hp = 100
        
        # Battle stats (stages)
        self.stat_stages = StatStages()
        
        # Status
        self.status = StatusCondition.NONE
        self.status_turns = 0
        
        # Moves (max 4)
        self.moves: List[Move] = []
        self._learn_initial_moves()
        
        # Experience
        try:
            self.exp = Experience.get_exp_for_level(level, species.growth_curve)
        except Exception as e:
            logger.error(f"Fehler bei der EP-Berechnung: {e}")
            self.exp = 0
        
        # Traits/Abilities
        self.traits = species.traits.copy() if species.traits else []
        self.held_item: Optional[str] = None
        
        # Battle state
        self.is_fainted = False
        self.turns_in_battle = 0
        
        # Capture info
        self.original_trainer = None
        self.capture_location = None
        self.capture_level = level
    
    def set_random_seed(self, seed: int) -> None:
        """Setze RNG-Seed für deterministische Tests."""
        self.rng = random.Random(seed)
    
    @property
    def name(self) -> str:
        """Hole den Namen des Monsters (Nickname oder Spezies-Name)."""
        return self.nickname or self.species.name
    
    @property
    def id(self) -> int:
        """Hole die ID des Monsters."""
        return getattr(self.species, 'id', 0)
    
    def _generate_ivs(self) -> Dict[str, int]:
        """Generate random IVs for the monster."""
        try:
            return {
                "hp": self.rng.randint(0, 31),
                "atk": self.rng.randint(0, 31),
                "def": self.rng.randint(0, 31),
                "mag": self.rng.randint(0, 31),
                "res": self.rng.randint(0, 31),
                "spd": self.rng.randint(0, 31)
            }
        except Exception as e:
            logger.error(f"Fehler bei der IV-Generierung: {e}")
            return {"hp": 15, "atk": 15, "def": 15, "mag": 15, "res": 15, "spd": 15}
    
    def _generate_nature(self) -> str:
        """Generate a random nature for the monster."""
        try:
            natures = ["Hardy", "Lonely", "Brave", "Adamant", "Naughty",
                      "Bold", "Docile", "Relaxed", "Impish", "Lax",
                      "Timid", "Hasty", "Serious", "Jolly", "Naive",
                      "Modest", "Mild", "Quiet", "Bashful", "Rash",
                      "Calm", "Gentle", "Sassy", "Careful", "Quirky"]
            return self.rng.choice(natures)
        except Exception as e:
            logger.error(f"Fehler bei der Nature-Generierung: {e}")
            return "Hardy"
    
    def _calculate_stats(self) -> Dict[str, int]:
        """Calculate the monster's stats based on species, level, IVs, and EVs."""
        try:
            if not self.species.base_stats:
                raise ValueError("Keine Basis-Stats verfügbar")
            
            stats = {}
            for stat_name in ["hp", "atk", "def", "mag", "res", "spd"]:
                base_stat = getattr(self.species.base_stats, stat_name, 0)
                
                if stat_name == "hp":
                    # HP formula
                    stat_value = int((2 * base_stat + self.ivs[stat_name] + self.evs[stat_name] / 4) * self.level / 100 + self.level + 10)
                else:
                    # Other stats formula
                    stat_value = int((2 * base_stat + self.ivs[stat_name] + self.evs[stat_name] / 4) * self.level / 100 + 5)
                
                stats[stat_name] = max(1, stat_value)  # Mindestens 1
            
            return stats
        except Exception as e:
            logger.error(f"Fehler bei der Stats-Berechnung: {e}")
            # Fallback-Stats
            return {"hp": 100, "atk": 50, "def": 50, "mag": 30, "res": 30, "spd": 70}
    
    def _learn_initial_moves(self) -> None:
        """Learn initial moves based on species learnset."""
        try:
            if not self.species.learnset:
                return
            
            # Sortiere Moves nach Level
            available_moves = [(level, move_id) for level, move_id in self.species.learnset if level <= self.level]
            available_moves.sort(key=lambda x: x[0])
            
            # Lerne bis zu 4 Moves
            for level, move_id in available_moves[-4:]:
                try:
                    move = move_registry.get_move(move_id)
                    if move and move not in self.moves:
                        self.moves.append(move)
                except Exception as e:
                    logger.warning(f"Konnte Move {move_id} nicht laden: {e}")
        except Exception as e:
            logger.error(f"Fehler beim Lernen der initialen Moves: {e}")
    
    def process_status(self) -> Dict[str, Any]:
        """Process status effects at the start of turn."""
        try:
            if self.status == StatusCondition.NONE or self.is_fainted:
                return {"skip_turn": False, "message": ""}
            
            self.status_turns += 1
            
            if self.status == StatusCondition.SLEEP:
                if self.status_turns >= 3:
                    self.status = StatusCondition.NONE
                    self.status_turns = 0
                    return {"skip_turn": False, "message": f"{self.name} ist aufgewacht!"}
                else:
                    return {"skip_turn": True, "message": f"{self.name} schläft tief und fest."}
            
            elif self.status == StatusCondition.FREEZE:
                # 20% chance to thaw
                if self.rng.random() < 0.2:
                    self.status = StatusCondition.NONE
                    self.status_turns = 0
                    return {"skip_turn": False, "message": f"{self.name} ist aufgetaut!"}
                else:
                    return {"skip_turn": True, "message": f"{self.name} ist eingefroren!"}
            
            elif self.status == StatusCondition.PARALYSIS:
                # 25% chance to skip turn
                if self.rng.random() < 0.25:
                    return {"skip_turn": True, "message": f"{self.name} ist gelähmt und kann sich nicht bewegen!"}
                else:
                    return {"skip_turn": False, "message": ""}
            
            elif self.status == StatusCondition.CONFUSION:
                # Confusion lasts 2-5 turns
                if self.status_turns >= self.rng.randint(2, 5):
                    self.status = StatusCondition.NONE
                    self.status_turns = 0
                    return {"skip_turn": False, "message": f"{self.name} ist nicht mehr verwirrt!"}
                else:
                    # 50% chance to hurt itself
                    if self.rng.random() < 0.5:
                        damage = max(1, int(self.stats["atk"] * 0.4))
                        self.take_damage(damage)
                        return {"skip_turn": True, "message": f"{self.name} trifft sich selbst! ({damage} Schaden)"}
                    else:
                        return {"skip_turn": False, "message": ""}
            
            elif self.status == StatusCondition.FLINCH:
                # Flinch only affects one turn
                self.status = StatusCondition.NONE
                self.status_turns = 0
                return {"skip_turn": True, "message": f"{self.name} ist erschrocken!"}
            
            return {"skip_turn": False, "message": ""}
            
        except Exception as e:
            logger.error(f"Fehler bei der Status-Verarbeitung: {e}")
            return {"skip_turn": False, "message": ""}
    
    def take_damage(self, damage: int) -> int:
        """Take damage and return actual damage taken."""
        try:
            if damage <= 0:
                return 0
            
            old_hp = self.current_hp
            self.current_hp = max(0, self.current_hp - damage)
            actual_damage = old_hp - self.current_hp
            
            # Check if fainted
            if self.current_hp <= 0:
                self.is_fainted = True
                self.status = StatusCondition.NONE
                self.status_turns = 0
            
            return actual_damage
            
        except Exception as e:
            logger.error(f"Fehler beim Schaden nehmen: {e}")
            return 0
    
    def heal(self, amount: int) -> int:
        """Heal the monster and return actual healing done."""
        try:
            if amount <= 0 or self.is_fainted:
                return 0
            
            old_hp = self.current_hp
            self.current_hp = min(self.max_hp, self.current_hp + amount)
            actual_healing = self.current_hp - old_hp
            
            return actual_healing
            
        except Exception as e:
            logger.error(f"Fehler beim Heilen: {e}")
            return 0
    
    def gain_exp(self, exp_amount: int) -> Dict[str, Any]:
        """Gain experience and return level up information."""
        try:
            if exp_amount <= 0:
                return {"leveled_up": False}
            
            old_level = self.level
            self.exp += exp_amount
            
            # Check for level up
            new_level = Experience.get_level_for_exp(self.exp, self.species.growth_curve)
            
            if new_level > old_level:
                self.level = new_level
                
                # Recalculate stats
                self.stats = self._calculate_stats()
                old_max_hp = self.max_hp
                self.max_hp = self.stats["hp"]
                
                # Heal HP increase
                hp_increase = self.max_hp - old_max_hp
                self.current_hp += hp_increase
                
                # Check for new moves
                new_moves = []
                self._learn_initial_moves()
                
                return {
                    "leveled_up": True,
                    "new_level": new_level,
                    "new_moves": new_moves,
                    "hp_increase": hp_increase
                }
            
            return {"leveled_up": False}
            
        except Exception as e:
            logger.error(f"Fehler beim EP-Gewinn: {e}")
            return {"leveled_up": False, "error": str(e)}
    
    def get_catch_rate(self, hp_percent: float, status_bonus: float = 1.0) -> float:
        """Calculate catch rate based on HP and status."""
        try:
            if hp_percent <= 0:
                return 0.0
            
            # Base catch rate from species
            base_rate = self.species.capture_rate / 255.0
            
            # HP modifier
            hp_modifier = (3 * self.max_hp - 2 * self.current_hp) / (3 * self.max_hp)
            
            # Status bonus
            status_modifier = status_bonus
            
            # Final catch rate
            catch_rate = base_rate * hp_modifier * status_modifier
            
            return max(0.0, min(1.0, catch_rate))
            
        except Exception as e:
            logger.error(f"Fehler bei der Catch-Rate-Berechnung: {e}")
            return 0.1  # Fallback
    
    def is_valid(self) -> bool:
        """Validiere den Monster-Status."""
        try:
            # Prüfe grundlegende Eigenschaften
            if not self.species or not self.name:
                return False
            
            # Prüfe Stats
            if not self.stats or not isinstance(self.stats, dict):
                return False
            
            # Prüfe HP
            if self.current_hp < 0 or self.max_hp <= 0:
                return False
            
            # Prüfe Level
            if not isinstance(self.level, int) or self.level < 1:
                return False
            
            # Prüfe Status
            if not isinstance(self.status, StatusCondition):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Fehler bei der Monster-Validierung: {e}")
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary for saving."""
        return {
            "species_id": self.species.id,
            "nickname": self.nickname,
            "level": self.level,
            "exp": self.exp,
            "ivs": self.ivs,
            "evs": self.evs,
            "nature": self.nature,
            "current_hp": self.current_hp,
            "status": self.status.value,
            "moves": [{"id": m.id, "pp": m.pp} for m in self.moves],
            "traits": self.traits,
            "held_item": self.held_item,
            "original_trainer": self.original_trainer,
            "capture_location": self.capture_location,
            "capture_level": self.capture_level
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], species: MonsterSpecies) -> 'MonsterInstance':
        """Create from saved dictionary data."""
        instance = cls(species, data["level"], data.get("nickname"))
        instance.exp = data["exp"]
        instance.ivs = data["ivs"]
        instance.evs = data["evs"]
        instance.nature = data["nature"]
        instance.current_hp = data["current_hp"]
        instance.status = StatusCondition(data.get("status", "none"))
        instance.traits = data.get("traits", species.traits.copy())
        instance.held_item = data.get("held_item")
        instance.original_trainer = data.get("original_trainer")
        instance.capture_location = data.get("capture_location")
        instance.capture_level = data.get("capture_level", data["level"])
        
        # Restore moves with PP
        instance.moves = []
        for move_data in data.get("moves", []):
            move = move_registry.create_move_instance(move_data["id"])
            if move:
                move.pp = move_data.get("pp", move.max_pp)
                instance.moves.append(move)
        
        # Recalculate stats
        instance.stats = instance._calculate_stats()
        instance.max_hp = instance.stats["hp"]
        
        return instance