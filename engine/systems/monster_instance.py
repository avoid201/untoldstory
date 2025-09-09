"""
Monster Instance System
Handles individual monster instances with stats, status, and battle mechanics
"""

from enum import Enum
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
import random
import logging
from engine.systems.stats import BaseStats, StatCalculator, StatStages
from engine.systems.experience_system import GrowthCurve
from engine.systems.moves import Move, move_registry
from engine.core.resources import resources
from engine.systems.experience_system import ExperienceSystem, LevelUpResult
from engine.systems.talent_system import TalentInstance, TalentDatabase, get_talent_database, TalentTier
from engine.systems.talent_manager import get_talent_manager

# Logger für bessere Fehlerverfolgung
logger = logging.getLogger(__name__)

# Import StatusCondition from the unified DQM status system
from engine.systems.conditions import StatusCondition

class MonsterRank(Enum):
    """Monster Rank für Balance/Tiers."""
    F = "F"    # Weakest
    E = "E"
    D = "D"
    C = "C"
    B = "B"
    A = "A"
    S = "S"
    SS = "SS"
    X = "X"    # Strongest/Legendary

    def __lt__(self, other):
        """Ermögliche Vergleiche zwischen Rängen."""
        if not isinstance(other, MonsterRank):
            return NotImplemented
        rank_order = ['F', 'E', 'D', 'C', 'B', 'A', 'S', 'SS', 'X']
        return rank_order.index(self.value) < rank_order.index(other.value)

    def __le__(self, other):
        return self < other or self == other

    def __gt__(self, other):
        return not self <= other

    def __ge__(self, other):
        return not self < other

@dataclass
class MonsterSpecies:
    """Defines a monster species with base stats and characteristics."""
    id: str
    name: str
    types: List[str]
    base_stats: BaseStats
    rank: MonsterRank = MonsterRank.F
    growth_curve: GrowthCurve = GrowthCurve.MEDIUM_FAST
    abilities: Optional[List[str]] = None
    traits: Optional[List[str]] = None  # DQM-spezifische Traits
    talents: Optional[List[Dict[str, Any]]] = None  # Talent-System Integration
    evolution_requirements: Optional[Dict[str, Any]] = None
    catch_rate: int = 128
    size: int = 1  # Grid slots required (always 1 for now)
    description: str = ""
    era: str = "present"  # "past", "present", "future" - für Encounter-System
    
    def __post_init__(self):
        """Validiere und setze Standardwerte nach der Initialisierung."""
        if self.abilities is None:
            self.abilities = []
        if self.traits is None:
            self.traits = []
        if self.talents is None:
            self.talents = []
        if self.types is None:
            self.types = []
        
        # Validiere types
        if not isinstance(self.types, list) or len(self.types) == 0:
            logger.error(f"Species {self.name} hat keine gültigen Typen")
            self.types = ["Normal"]
        
        # Validiere base_stats
        if not isinstance(self.base_stats, BaseStats):
            if isinstance(self.base_stats, dict):
                # Konvertiere Dictionary zu BaseStats
                try:
                    self.base_stats = BaseStats(
                        hp=self.base_stats.get('hp', 40),
                        atk=self.base_stats.get('atk', 40),
                        def_=self.base_stats.get('def', 40),
                        mag=self.base_stats.get('mag', 40),
                        res=self.base_stats.get('res', 40),
                        spd=self.base_stats.get('spd', 40)
                    )
                except Exception as e:
                    logger.error(f"Fehler beim Konvertieren der base_stats für {self.name}: {e}")
                    self.base_stats = BaseStats(40, 40, 40, 40, 40, 40)
            else:
                logger.error(f"Species {self.name} hat keine gültigen base_stats")
                # Erstelle Standard-BaseStats falls nötig
                self.base_stats = BaseStats(40, 40, 40, 40, 40, 40)
    
    def create_instance(self, level: int = 1, nickname: Optional[str] = None) -> 'MonsterInstance':
        """
        Create a MonsterInstance from this species.
        
        Args:
            level: Starting level for the monster
            nickname: Optional nickname for the monster
            
        Returns:
            MonsterInstance created from this species
        """
        return MonsterInstance(species=self, level=level, nickname=nickname)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'MonsterSpecies':
        """Erstelle MonsterSpecies aus Dict mit verbessertem Error-Handling."""
        try:
            # Base stats verarbeiten
            base_stats_data = data.get("base_stats", {})
            if isinstance(base_stats_data, dict):
                base_stats = BaseStats(
                    hp=base_stats_data.get("hp", 40),
                    atk=base_stats_data.get("atk", 40),
                    def_=base_stats_data.get("def", 40),
                    mag=base_stats_data.get("mag", 40),
                    res=base_stats_data.get("res", 40),
                    spd=base_stats_data.get("spd", 40)
                )
            else:
                base_stats = BaseStats(40, 40, 40, 40, 40, 40)
            
            # Rank verarbeiten
            rank_value = data.get("rank", "F")
            try:
                rank = MonsterRank(rank_value)
            except ValueError:
                rank = MonsterRank.F
            
            # Growth curve verarbeiten
            growth_curve_value = data.get("growth_curve", "MEDIUM_FAST")
            try:
                growth_curve = GrowthCurve[growth_curve_value.upper()]
            except (KeyError, AttributeError):
                growth_curve = GrowthCurve.MEDIUM_FAST
            
            return cls(
                id=str(data.get("id", "unknown")),
                name=data.get("name", "Unknown"),
                types=data.get("types", ["Normal"]),
                base_stats=base_stats,
                rank=rank,
                growth_curve=growth_curve,
                abilities=data.get("abilities", []),
                talents=data.get("talents", []),
                evolution_requirements=data.get("evolution", None),
                catch_rate=data.get("catch_rate", 128),
                size=data.get("size", 1),
                description=data.get("description", "")
            )
        except Exception as e:
            logger.error(f"Fehler beim Erstellen der MonsterSpecies aus Dict: {e}")
            raise

class MonsterInstance:
    """Monster instance for battle system"""
    
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
        self.name = nickname or species.name
        
        # Experience system - simplified
        self.total_exp = 0
        
        # RNG für deterministische Tests
        self.rng = random.Random()
        
        # Individual Values (IVs) - genetic potential
        self.ivs = self._generate_ivs()
        
        # Nature affects stat growth
        self.nature = self._generate_nature()
        
        # Calculate stats
        self.current_stats = self._calculate_stats()
        
        # HP management
        self.max_hp = self.current_stats.hp
        self.current_hp = self.max_hp
        
        # Status management - UNIFIED SYSTEM
        self.status = None  # Current primary status (StatusCondition enum)
        self.status_turns = 0  # Duration for temporary status effects
        

        
        # Battle state
        self.stat_stages = StatStages()
        
        # Talents (DQM-System)
        self.talents = self._initialize_talents()
        
        # Moves (basierend auf Talents)
        self.moves = self._initialize_moves()
        
        # Battle flags
        self.has_acted_this_turn = False
        self.damage_taken_this_turn = 0
        self.participated = False  # For EXP distribution
        self.total_exp = 0  # Total EXP earned
        self.held_item = None  # Held item
        
        # Capture info
        self.original_trainer = None
        self.catch_location = None
        self.friendship = 50
    

    
    @property
    def types(self) -> List[str]:
        """Get monster types from species."""
        if self.species and hasattr(self.species, 'types'):
            return self.species.types
        elif self.species and hasattr(self.species, 'type'):
            return [self.species.type]
        return ["Normal"]  # Fallback
    
    @property
    def stats(self) -> Dict[str, int]:
        """Get current stats as dict."""
        return {
            'hp': self.current_stats.hp if hasattr(self.current_stats, 'hp') else self.max_hp,
            'atk': self.current_stats.atk if hasattr(self.current_stats, 'atk') else 50,
            'def': self.current_stats.def_ if hasattr(self.current_stats, 'def_') else 40,
            'mag': self.current_stats.mag if hasattr(self.current_stats, 'mag') else 45,
            'res': self.current_stats.res if hasattr(self.current_stats, 'res') else 35,
            'spd': self.current_stats.spd if hasattr(self.current_stats, 'spd') else 60
        }
    
    @property
    def species_name(self) -> str:
        """Get species name."""
        if self.species:
            if hasattr(self.species, 'name'):
                return self.species.name
            elif isinstance(self.species, dict):
                return self.species.get('name', 'Unknown')
        return "Unknown"
        
    def _generate_ivs(self) -> BaseStats:
        """Generate Individual Values (0-31 for each stat)."""
        return BaseStats(
            hp=self.rng.randint(0, 31),
            atk=self.rng.randint(0, 31),
            def_=self.rng.randint(0, 31),
            mag=self.rng.randint(0, 31),
            res=self.rng.randint(0, 31),
            spd=self.rng.randint(0, 31)
        )
    
    def _generate_nature(self) -> str:
        """Generate a random nature (simplified)."""
        natures = ["Hardy", "Bold", "Modest", "Adamant", "Timid"]
        return self.rng.choice(natures)
    
    def _calculate_stats(self) -> BaseStats:
        """Calculate current stats based on level, IVs, and nature."""
        from engine.systems.stats import StatCalculator
        
        # Convert IVs dict to match expected format
        ivs_dict = {
            "hp": getattr(self.ivs, 'hp', 0),
            "atk": getattr(self.ivs, 'atk', 0), 
            "def": getattr(self.ivs, 'def_', 0),
            "mag": getattr(self.ivs, 'mag', 0),
            "res": getattr(self.ivs, 'res', 0),
            "spd": getattr(self.ivs, 'spd', 0)
        }
        
        # Use the static method from the StatCalculator class
        calculated_stats = StatCalculator.calculate_all_stats(
            base_stats=self.species.base_stats,
            level=self.level,
            ivs=ivs_dict,
            evs={"hp": 0, "atk": 0, "def": 0, "mag": 0, "res": 0, "spd": 0},
            nature="Hardy"
        )
        
        # Convert back to BaseStats
        return BaseStats(
            hp=calculated_stats["hp"],
            atk=calculated_stats["atk"], 
            def_=calculated_stats["def"],
            mag=calculated_stats["mag"],
            res=calculated_stats["res"],
            spd=calculated_stats["spd"]
        )
    
    def _initialize_talents(self) -> List[TalentInstance]:
        """Initialize talents based on species data and level."""
        talents = []
        
        try:
            # Lade Talent-Datenbank
            talent_db = get_talent_database()
            
            # 1. Lade Talents aus Species-Daten (falls vorhanden)
            if hasattr(self.species, 'talents') and self.species.talents:
                for talent_data in self.species.talents:
                    if isinstance(talent_data, dict):
                        talent_id = talent_data.get('talent_id')
                        learned_at_level = talent_data.get('learned_at_level', 1)
                        current_tier = talent_data.get('current_tier', 1)
                        experience = talent_data.get('experience', 0)
                        
                        # Prüfe ob Talent bereits gelernt werden kann
                        if self.level >= learned_at_level:
                            talent_instance = TalentInstance(
                                talent_id=talent_id,
                                current_tier=TalentTier(current_tier),
                                experience=experience,
                                is_learned=True
                            )
                            talents.append(talent_instance)
            
            # 2. Fallback: Bestimme Start-Talents basierend auf Monster-Types
            if not talents:
                start_talents = self._get_start_talents_for_types()
                for talent_id in start_talents:
                    talent_instance = TalentInstance(talent_id, is_learned=True)
                    talents.append(talent_instance)
            
            # 3. Validiere alle Talents
            validated_talents = []
            for talent_instance in talents:
                if talent_db.get_talent(talent_instance.talent_id):
                    validated_talents.append(talent_instance)
                else:
                    logger.warning(f"Talent {talent_instance.talent_id} nicht in Datenbank gefunden")
            
            return validated_talents if validated_talents else [self._create_fallback_talent()]
            
        except Exception as e:
            logger.error(f"Fehler beim Initialisieren der Talents: {e}")
            return [self._create_fallback_talent()]
    
    def _get_start_talents_for_types(self) -> List[str]:
        """Bestimme Start-Talents basierend auf Monster-Types"""
        start_talents = []
        
        # Jedes Monster bekommt Physical I als Basis
        start_talents.append("physical_i")
        
        # Type-spezifische Talents (angepasst an Ruhrpott-Monster)
        type_talent_mapping = {
            "Feuer": ["fire_i"],
            "Wasser": ["water_i"],
            "Erde": ["earth_i"],
            "Luft": ["air_i"],
            "Pflanze": ["plant_i"],
            "Bestie": ["physical_i"],  # Bestien sind körperlich
            "Energie": ["energy_i"],
            "Chaos": ["chaos_i"],
            "Seuche": ["plague_i"],
            "Mystisch": ["mystic_i"],
            "Gottheit": ["heal_i"],  # Gottheit = Heilung
            "Teufel": ["chaos_i"]  # Teufel = Chaos
        }
        
        for monster_type in self.types:
            if monster_type in type_talent_mapping:
                start_talents.extend(type_talent_mapping[monster_type])
        
        # Entferne Duplikate
        return list(set(start_talents))
    
    def _create_fallback_talent(self) -> TalentInstance:
        """Erstelle Fallback-Talent falls keine Talents gefunden werden"""
        return TalentInstance(
            talent_id="physical_i",
            current_tier=TalentTier.BASIC,
            experience=0,
            is_learned=True
        )
    
    def get_available_moves(self) -> List['Move']:
        """Hole alle verfügbaren Moves aus den Talents"""
        return self.moves
    
    def get_passive_abilities(self) -> List[Dict[str, Any]]:
        """Hole alle passiven Fähigkeiten aus den Talents"""
        try:
            talent_manager = get_talent_manager()
            return talent_manager.get_passive_abilities(self)
        except Exception as e:
            logger.error(f"Fehler beim Laden der passiven Fähigkeiten: {e}")
            return []
    
    def can_learn_talent(self, talent_id: str) -> bool:
        """Prüfe ob Monster ein Talent lernen kann"""
        try:
            talent_manager = get_talent_manager()
            return talent_manager.can_learn_talent(self, talent_id)
        except Exception as e:
            logger.error(f"Fehler beim Prüfen des Talent-Lernens: {e}")
            return False
    
    def learn_talent(self, talent_id: str) -> bool:
        """Lerne ein neues Talent"""
        try:
            talent_manager = get_talent_manager()
            return talent_manager.learn_talent(self, talent_id)
        except Exception as e:
            logger.error(f"Fehler beim Lernen des Talents {talent_id}: {e}")
            return False
    
    def upgrade_talent(self, talent_id: str) -> bool:
        """Upgrade ein bestehendes Talent"""
        try:
            talent_manager = get_talent_manager()
            return talent_manager.upgrade_talent(self, talent_id)
        except Exception as e:
            logger.error(f"Fehler beim Upgraden des Talents {talent_id}: {e}")
            return False
    
    def get_learnable_talents(self) -> List[str]:
        """Hole alle Talents die das Monster lernen kann"""
        try:
            talent_manager = get_talent_manager()
            return talent_manager.get_learnable_talents(self)
        except Exception as e:
            logger.error(f"Fehler beim Laden der lernbaren Talents: {e}")
            return []
    
    def get_talent_info(self, talent_id: str) -> Optional[Dict[str, Any]]:
        """Hole Informationen über ein Talent"""
        try:
            talent_manager = get_talent_manager()
            return talent_manager.get_talent_info(self, talent_id)
        except Exception as e:
            logger.error(f"Fehler beim Laden der Talent-Info: {e}")
            return None
    
    def _initialize_moves(self) -> List['Move']:
        """Load moves from monster's talents with validation"""
        moves = []
        
        try:
            # Lade Talent-Datenbank
            talent_db = get_talent_database()
            
            for talent_instance in self.talents:
                if not talent_instance.is_learned:
                    continue
                    
                talent = talent_db.get_talent(talent_instance.talent_id)
                if not talent:
                    logger.warning(f"Talent {talent_instance.talent_id} not found")
                    continue
                    
                move_ids = talent.get_moves_for_tier(
                    talent_instance.current_tier, 
                    self.level
                )
                
                for move_id in move_ids:
                    move = talent_db.create_move_from_talent_data(move_id)
                    if move and self._validate_move(move):
                        moves.append(move)
            
            # ALWAYS return at least one move
            return moves if moves else [self._create_fallback_move()]
            
        except Exception as e:
            logger.error(f"Fehler beim Initialisieren der Moves: {e}")
            # Fallback: Mindestens einen Move zurückgeben
            return [self._create_fallback_move()]
    
    def _validate_move(self, move: 'Move') -> bool:
        """Validiere Move bevor es hinzugefügt wird"""
        try:
            if not move:
                return False
            
            # Prüfe grundlegende Move-Eigenschaften
            if not hasattr(move, 'id') or not move.id:
                logger.warning("Move hat keine ID")
                return False
            
            if not hasattr(move, 'name') or not move.name:
                logger.warning(f"Move {move.id} hat keinen Namen")
                return False
            
            # Prüfe ob Move bereits vorhanden ist (vermeide Duplikate)
            if hasattr(self, 'moves') and self.moves:
                for existing_move in self.moves:
                    if existing_move.id == move.id:
                        logger.debug(f"Move {move.id} bereits vorhanden, überspringe")
                        return False
            
            # Prüfe Move-Kategorie (flexibler)
            if not hasattr(move, 'category'):
                logger.warning(f"Move {move.id} hat keine Kategorie, setze PHYSICAL")
                from engine.systems.moves import MoveCategory
                move.category = MoveCategory.PHYSICAL
            
            # Prüfe Power (kann 0 sein für Support-Moves)
            if hasattr(move, 'power') and move.power < 0:
                logger.warning(f"Move {move.id} hat negative Power: {move.power}")
                return False
            
            # Prüfe Accuracy (flexibler)
            if hasattr(move, 'accuracy'):
                if move.accuracy < 0 or move.accuracy > 100:
                    logger.warning(f"Move {move.id} hat ungültige Accuracy: {move.accuracy}, setze 100")
                    move.accuracy = 100
            
            return True
            
        except Exception as e:
            logger.error(f"Fehler bei der Move-Validierung: {e}")
            return False
    
    def _create_fallback_move(self) -> 'Move':
        """Erstelle Fallback-Move wenn keine Talents verfügbar"""
        from engine.systems.moves import Move, MoveCategory, MoveTarget, MoveEffect, EffectKind
        
        return Move(
            id="struggle",
            name="Verzweifler",
            type="Bestie",
            category=MoveCategory.PHYSICAL,
            power=50,
            accuracy=100,
            priority=0,
            targeting=MoveTarget.ENEMY,
            effects=[MoveEffect(kind=EffectKind.DAMAGE, power=50)],
            description="Letzter Ausweg wenn keine Moves verfügbar",
            contact=True,
            sound_based=False,
            punching=True,
            biting=False,
            pulse=False,
            multi_hit=None,
            drain_percent=0,
            recoil_percent=0,
            multi_hit_min=1,
            multi_hit_max=1
        )
    def take_damage(self, damage: int) -> Dict[str, Any]:
        """
        Take damage and return detailed result.
        
        Args:
            damage: Damage amount
            
        Returns:
            Dict with damage details and battle state changes
        """
        if self.is_fainted:
            return {
                'damage_dealt': 0,
                'remaining_hp': self.current_hp,
                'fainted': False,
                'was_already_fainted': True,
                'status_cleared': False
            }
        
        old_hp = self.current_hp
        actual_damage = min(damage, self.current_hp)
        self.current_hp -= actual_damage
        self.damage_taken_this_turn += actual_damage
        
        result = {
            'damage_dealt': actual_damage,
            'remaining_hp': self.current_hp,
            'fainted': False,
            'was_already_fainted': False,
            'status_cleared': False
        }
        
        if self.current_hp <= 0:
            self.current_hp = 0
            result['fainted'] = True
            
            # Clear status on faint (DQM-style)
            if self.status is not None:
                self.status = None
                self.status_turns = 0
                result['status_cleared'] = True
        
        return result
    
    def heal(self, amount: int) -> int:
        """
        Heal HP and return actual amount healed.
        
        Args:
            amount: Heal amount
            
        Returns:
            Actual amount healed
        """
        if self.is_fainted:
            return 0
        
        old_hp = self.current_hp
        self.current_hp = min(self.current_hp + amount, self.max_hp)
        return self.current_hp - old_hp
    
    def apply_status(self, status_name: str, duration: int = -1) -> bool:
        """Apply a status effect to this monster.
        
        Args:
            status_name: Name of the status effect
            duration: Duration in turns (-1 for permanent)
        
        Returns:
            True if status was applied successfully
        """
        try:
            if self.is_fainted:
                return False
            
            # Convert to StatusCondition enum
            status_condition = StatusCondition.from_string(status_name)
            
            # Only apply if no status exists or if it's a different status
            if self.status is None or self.status != status_condition:
                self.status = status_condition
                self.status_turns = duration if duration > 0 else 0
                
                logger.debug(f"{self.name} gained status: {status_condition.value}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to apply status {status_name}: {e}")
            return False
    
    def process_status_effects(self) -> bool:
        """
        Process status effects at end of turn.
        
        Returns:
            True if monster can act, False if prevented by status
        """
        if self.is_fainted:
            return False
        
        if self.status is None:
            return True
        
        # Process status effects based on type
        if self.status == StatusCondition.SLEEP:
            if self.status_turns <= 0 or self.rng.random() < 0.25:  # 25% chance to wake up
                self.status = None
                return True
            else:
                self.status_turns -= 1
                return False
        
        elif self.status == StatusCondition.FREEZE:
            if self.rng.random() < 0.20:  # 20% chance to thaw
                self.status = None
                return True
            else:
                return False
        
        elif self.status == StatusCondition.PARALYSIS:
            if self.rng.random() < 0.25:  # 25% chance to be fully paralyzed
                return False
        
        elif self.status == StatusCondition.CONFUSION:
            if self.rng.random() < 0.50:  # 50% chance to hurt self
                self_damage = max(1, self.current_stats.atk // 4)
                self.take_damage(self_damage)
                if self.status_turns <= 0:
                    self.status = None
                return False
        
        elif self.status == StatusCondition.FLINCH:
            self.status = None
            return False
        
        return True
    
    def apply_status_damage(self):
        """Apply damage-over-time status effects."""
        if self.is_fainted or self.status is None:
            return
        
        damage = 0
        if self.status == StatusCondition.BURN:
            damage = max(1, self.max_hp // 8)  # 12.5% max HP
        elif self.status == StatusCondition.POISON:
            damage = max(1, self.max_hp // 8)  # 12.5% max HP
        elif self.status == StatusCondition.BADLY_POISONED:
            # Escalating poison damage
            damage = max(1, self.max_hp // 16 * (self.status_turns + 1))
        
        if damage > 0:
            self.take_damage(damage)
            # Clear status if fainted
            if self.current_hp <= 0:
                self.status = None
    
    def get_stat_with_stages(self, stat_name: str) -> int:
        """Get a stat modified by stat stages."""
        base_value = getattr(self.current_stats, stat_name, 0)
        multiplier = self.get_stat_multiplier(stat_name)
        return int(base_value * multiplier)
    

    
    def modify_stat_stage(self, stat: str, amount: int):
        """
        Modify a stat stage (-6 to +6).
        
        Args:
            stat: Stat name (atk, def, mag, res, spd, acc, eva)
            amount: Amount to change (positive or negative)
        """
        from engine.systems.stats import Stat
        try:
            stat_enum = Stat(stat)
            self.stat_stages.modify_stage(stat_enum, amount)
        except ValueError:
            logger.warning(f"Invalid stat name: {stat}")
    
    def get_stat_multiplier(self, stat: str) -> float:
        """
        Get multiplier for stat based on stage.
        
        Args:
            stat: Stat name
            
        Returns:
            Multiplier value (0.25 to 4.0)
        """
        from engine.systems.stats import Stat
        try:
            stat_enum = Stat(stat)
            return self.stat_stages.get_multiplier(stat_enum)
        except ValueError:
            return 1.0
    
    def clear_status(self, status_name: str = None):
        """Clear status effect(s).
        
        Args:
            status_name: Specific status to clear, or None to clear all
        """
        if status_name:
            status_condition = StatusCondition.from_string(status_name)
            if self.status == status_condition:
                self.status = None
                self.status_turns = 0
        else:
            self.status = None
            self.status_turns = 0
    
    def remove_status(self, status_name: str = None) -> bool:
        """Remove a status effect.
        
        Args:
            status_name: Specific status to remove, or None to clear all
        
        Returns:
            True if status was removed
        """
        try:
            if status_name:
                status_condition = StatusCondition.from_string(status_name)
                if self.status == status_condition:
                    self.status = None
                    self.status_turns = 0
                    logger.debug(f"{self.name} lost status: {status_name}")
                    return True
            else:
                # Clear all statuses
                self.status = None
                self.status_turns = 0
                logger.debug(f"{self.name} cleared all statuses")
                return True
                
        except Exception as e:
            logger.error(f"Failed to remove status: {e}")
            return False
    
    def has_status(self, status_name: str) -> bool:
        """Check if monster has a specific status.
        
        Args:
            status_name: Status to check for
        
        Returns:
            True if monster has this status
        """
        if self.status is None:
            return False
        
        status_condition = StatusCondition.from_string(status_name)
        return self.status == status_condition
    
    def update_status_durations(self) -> List[str]:
        """Update status effect durations (call at turn end).
        
        Returns:
            List of expired status names
        """
        expired = []
        
        if self.status is not None and self.status_turns > 0:
            self.status_turns -= 1
            if self.status_turns <= 0:
                expired.append(self.status.value)
                self.status = None
        
        return expired
    
    @property
    def is_fainted(self) -> bool:
        """Check if monster is fainted."""
        return self.current_hp <= 0
    
    def cure_status(self):
        """Cure current status condition."""
        self.clear_status()
    
    def full_heal(self):
        """Fully heal monster (HP and status)."""
        self.current_hp = self.max_hp
        self.status = None
        self.status_turns = 0
    
    def reset_battle_state(self):
        """Reset state for new battle."""
        self.has_acted_this_turn = False
        self.damage_taken_this_turn = 0
        self.stat_stages.reset()
        
        # Keep status conditions - they persist between battles
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        # Handle both object and dict species
        species_id = None
        if self.species:
            if hasattr(self.species, 'id'):
                species_id = self.species.id
            elif isinstance(self.species, dict):
                species_id = self.species.get('id')
        
        return {
            'species_id': species_id,
            'nickname': self.nickname,
            'level': self.level,
            'experience': self.total_exp,
            'current_hp': self.current_hp,
            'status': self.status,
            'friendship': self.friendship,
            'total_exp': self.total_exp,
            'held_item': self.held_item,
            'ivs': {
                'hp': self.ivs.hp,
                'atk': self.ivs.atk,
                'def': self.ivs.def_,
                'mag': self.ivs.mag,
                'res': self.ivs.res,
                'spd': self.ivs.spd
            },
            'nature': self.nature
        }
    
    @classmethod
    def create_from_species(cls, species: 'MonsterSpecies', level: int = 1, nickname: Optional[str] = None) -> 'MonsterInstance':
        """
        Create a MonsterInstance from a MonsterSpecies.
        
        Args:
            species: The MonsterSpecies to create instance from
            level: Starting level for the monster
            nickname: Optional nickname for the monster
            
        Returns:
            MonsterInstance created from the species
        """
        return cls(species=species, level=level, nickname=nickname)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], species: 'MonsterSpecies') -> 'MonsterInstance':
        """Create MonsterInstance from dictionary."""
        instance = cls(species, data.get('level', 5), data.get('nickname'))
        
        # Restore saved state
        instance.total_exp = data.get('experience', 0)
        instance.current_hp = data.get('current_hp', instance.max_hp)
        instance.status = data.get('status', None)
        instance.friendship = data.get('friendship', 50)
        instance.nature = data.get('nature', 'Hardy')
        instance.total_exp = data.get('total_exp', 0)
        instance.held_item = data.get('held_item', None)
        
        # Restore IVs if available
        if 'ivs' in data:
            iv_data = data['ivs']
            instance.ivs = BaseStats(
                hp=iv_data.get('hp', 15),
                atk=iv_data.get('atk', 15),
                def_=iv_data.get('def', 15),
                mag=iv_data.get('mag', 15),
                res=iv_data.get('res', 15),
                spd=iv_data.get('spd', 15)
            )
        
        # Recalculate stats
        instance.current_stats = instance._calculate_stats()
        
        return instance
    
    def gain_exp(self, exp_amount: int) -> Optional[LevelUpResult]:
        """Gain experience points and potentially level up.
        
        Args:
            exp_amount: Amount of EXP to gain
            
        Returns:
            LevelUpResult if leveled up, None otherwise
        """
        # Store total exp
        self.total_exp += exp_amount
        
        # Check for level up using the experience system
        result = ExperienceSystem.check_level_up(self, exp_amount)
        
        if result:
            # Apply the level up
            ExperienceSystem.apply_level_up(self, result)
            # Recalculate stats after level up
            self.current_stats = self._calculate_stats()
            # Update max HP
            old_max_hp = self.max_hp
            self.max_hp = self.current_stats.hp
            # Heal the HP gain
            self.current_hp += (self.max_hp - old_max_hp)
            
        return result
    
    def learn_talent(self, talent_id: str) -> bool:
        """Lerne ein neues Talent.
        
        Args:
            talent_id: ID des zu lernenden Talents
            
        Returns:
            True wenn Talent gelernt wurde, False sonst
        """
        talent_db = get_talent_database()
        
        # Prüfe ob bereits gelernt
        for talent in self.talents:
            if talent.talent_id == talent_id and talent.is_learned:
                return False
        
        # Prüfe ob lernbar
        if not talent_db.can_learn_talent(talent_id, self.talents, self.level):
            return False
        
        # Erstelle neue Talent-Instanz
        new_talent = TalentInstance(talent_id, is_learned=True)
        self.talents.append(new_talent)
        
        # Aktualisiere Moves
        self._update_moves_from_talents()
        
        logger.info(f"{self.species_name} lernte Talent: {talent_id}")
        return True
    
    def add_talent_experience(self, talent_id: str, amount: int) -> bool:
        """Füge Talent-Erfahrung hinzu.
        
        Args:
            talent_id: ID des Talents
            amount: Erfahrungsmenge
            
        Returns:
            True wenn Talent-Tier erhöht wurde
        """
        for talent in self.talents:
            if talent.talent_id == talent_id and talent.is_learned:
                tier_upgraded = talent.add_experience(amount)
                if tier_upgraded:
                    # Aktualisiere Moves bei Tier-Upgrade
                    self._update_moves_from_talents()
                    logger.info(f"{self.species_name} Talent {talent_id} auf Tier {talent.current_tier.value} erhöht!")
                return tier_upgraded
        
        return False
    
    def gain_talent_experience_from_battle(self, battle_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Gewinne Talent-Erfahrung basierend auf Battle-Ergebnis
        
        Args:
            battle_result: Ergebnis des Battles mit Details
            
        Returns:
            Liste der Talent-Upgrades die stattfanden
        """
        upgrades = []
        
        try:
            # Berechne Talent-EXP basierend auf Battle-Performance
            base_exp = battle_result.get('base_talent_exp', 10)
            participation_bonus = battle_result.get('participation_bonus', 1.0)
            victory_bonus = battle_result.get('victory_bonus', 1.0)
            
            # Jedes gelernte Talent bekommt EXP
            for talent in self.talents:
                if talent.is_learned:
                    # Berechne EXP für dieses Talent
                    talent_exp = int(base_exp * participation_bonus * victory_bonus)
                    
                    # Füge kleine Zufallskomponente hinzu
                    import random
                    talent_exp += random.randint(-2, 3)
                    talent_exp = max(1, talent_exp)
                    
                    # Füge EXP hinzu
                    old_tier = talent.current_tier
                    tier_upgraded = talent.add_experience(talent_exp)
                    
                    if tier_upgraded:
                        # Aktualisiere Moves
                        self._update_moves_from_talents()
                        
                        upgrade_info = {
                            'talent_id': talent.talent_id,
                            'old_tier': old_tier.value,
                            'new_tier': talent.current_tier.value,
                            'exp_gained': talent_exp,
                            'new_moves': self._get_new_moves_for_talent(talent.talent_id)
                        }
                        upgrades.append(upgrade_info)
                        
                        logger.info(f"{self.species_name} Talent {talent.talent_id} auf Tier {talent.current_tier.value} erhöht!")
                    else:
                        logger.debug(f"{self.species_name} Talent {talent.talent_id} +{talent_exp} EXP")
            
            return upgrades
            
        except Exception as e:
            logger.error(f"Fehler beim Talent-EXP Gewinn: {e}")
            return []
    
    def _get_new_moves_for_talent(self, talent_id: str) -> List[str]:
        """Hole neue Moves die durch Talent-Tier-Upgrade freigeschaltet wurden"""
        try:
            from engine.systems.talent_system import get_talent_database
            
            talent_db = get_talent_database()
            talent = talent_db.get_talent(talent_id)
            
            if not talent:
                return []
            
            # Finde Talent-Instanz
            talent_instance = None
            for t in self.talents:
                if t.talent_id == talent_id:
                    talent_instance = t
                    break
            
            if not talent_instance:
                return []
            
            # Hole alle verfügbaren Moves für aktuelles Tier
            available_moves = talent.get_moves_for_tier(
                talent_instance.current_tier,
                self.level
            )
            
            return available_moves
            
        except Exception as e:
            logger.error(f"Fehler beim Abrufen neuer Moves: {e}")
            return []
    
    def _update_moves_from_talents(self):
        """Aktualisiere Moves basierend auf aktuellen Talents."""
        self.moves = self._initialize_moves()
        
        # Sicherstelle dass mindestens ein Move vorhanden ist
        if not self.moves:
            logger.warning(f"{self.species_name} hat keine Moves, füge Fallback hinzu")
            self.moves = [self._create_fallback_move()]
    
    
    def get_available_talents(self) -> List[str]:
        """Hole alle verfügbaren Talents die gelernt werden können."""
        talent_db = get_talent_database()
        learnable_talents = talent_db.get_learnable_talents(
            self.types, self.talents, self.level
        )
        return [talent.id for talent in learnable_talents]
    
    def get_talent_info(self, talent_id: str) -> Optional[Dict[str, Any]]:
        """Hole Informationen über ein Talent."""
        talent_manager = get_talent_manager()
        return talent_manager.get_talent_info(self, talent_id)
    
    
    def can_battle(self) -> bool:
        """Check if monster can participate in battle."""
        return not self.is_fainted and self.current_hp > 0
    

    
    def __repr__(self) -> str:
        """String representation for debugging."""
        status_str = f" [{self.status}]" if self.status is not None else ""
        return f"{self.name} (Lv.{self.level}) - {self.current_hp}/{self.max_hp} HP{status_str}"
    
    def get_effective_stats(self) -> Dict[str, int]:
        """
        Get current stats modified by stat stages.
        
        Returns:
            Dictionary of effective stats
        """
        return {
            'hp': self.max_hp,  # HP is not affected by stat stages
            'atk': self.get_stat_with_stages('atk'),
            'def': self.get_stat_with_stages('def'),
            'mag': self.get_stat_with_stages('mag'),
            'res': self.get_stat_with_stages('res'),
            'spd': self.get_stat_with_stages('spd')
        }
    
    def get_battle_summary(self) -> Dict[str, Any]:
        """Get comprehensive battle summary."""
        return {
            'name': self.name,
            'species_name': self.species_name,
            'level': self.level,
            'types': self.types,
            'hp': {
                'current': self.current_hp,
                'max': self.max_hp,
                'percentage': (self.current_hp / self.max_hp) * 100 if self.max_hp > 0 else 0
            },
            'stats': self.get_effective_stats(),
            'status': {'condition': self.status, 'turns': self.status_turns},
            'is_fainted': self.is_fainted,
            'can_battle': self.can_battle(),
            'moves_count': len(self.moves),
            'talents_count': len(self.talents)
        }
    
    def evolve(self, new_species: 'MonsterSpecies') -> bool:
        """
        Evolve the monster to a new species.
        
        Args:
            new_species: The new species to evolve to
            
        Returns:
            True if evolution was successful
        """
        if not new_species:
            return False
        
        # Store old species info
        old_species = self.species
        old_name = self.name
        
        # Update species
        self.species = new_species
        
        # Update name if no nickname
        if not self.nickname:
            self.name = new_species.name
        
        # Recalculate stats with new base stats
        self.current_stats = self._calculate_stats()
        
        # Update max HP and heal the difference
        old_max_hp = self.max_hp
        self.max_hp = self.current_stats.hp
        hp_gain = self.max_hp - old_max_hp
        self.current_hp += hp_gain
        
        # Update moves based on new species
        self._update_moves_from_talents()
        
        logger.info(f"{old_name} evolved into {self.name}!")
        return True
    
    def can_evolve(self) -> bool:
        """
        Check if the monster can evolve.
        
        Returns:
            True if evolution is possible
        """
        if not hasattr(self.species, 'evolution_requirements') or not self.species.evolution_requirements:
            return False
        
        # Check level requirement
        required_level = self.species.evolution_requirements.get('level')
        if required_level and self.level < required_level:
            return False
        
        # Check friendship requirement
        required_friendship = self.species.evolution_requirements.get('friendship')
        if required_friendship and self.friendship < required_friendship:
            return False
        
        # Check item requirement
        required_item = self.species.evolution_requirements.get('item')
        if required_item and self.held_item != required_item:
            return False
        
        return True
    
    def get_evolution_info(self) -> Optional[Dict[str, Any]]:
        """
        Get information about possible evolution.
        
        Returns:
            Evolution info or None if not possible
        """
        if not self.can_evolve():
            return None
        
        evolution_data = self.species.evolution_requirements
        return {
            'can_evolve': True,
            'requirements': evolution_data,
            'current_level': self.level,
            'current_friendship': self.friendship,
            'held_item': self.held_item,
            'meets_requirements': {
                'level': not evolution_data.get('level') or self.level >= evolution_data['level'],
                'friendship': not evolution_data.get('friendship') or self.friendship >= evolution_data['friendship'],
                'item': not evolution_data.get('item') or self.held_item == evolution_data['item']
            }
        }
    
    def increase_friendship(self, amount: int = 1) -> int:
        """
        Increase friendship value.
        
        Args:
            amount: Amount to increase
            
        Returns:
            Actual amount increased
        """
        old_friendship = self.friendship
        self.friendship = min(255, self.friendship + amount)
        return self.friendship - old_friendship
    
    def decrease_friendship(self, amount: int = 1) -> int:
        """
        Decrease friendship value.
        
        Args:
            amount: Amount to decrease
            
        Returns:
            Actual amount decreased
        """
        old_friendship = self.friendship
        self.friendship = max(0, self.friendship - amount)
        return old_friendship - self.friendship
    
    def get_friendship_level(self) -> str:
        """
        Get friendship level description.
        
        Returns:
            Friendship level string
        """
        if self.friendship >= 200:
            return "Sehr zufrieden"
        elif self.friendship >= 150:
            return "Zufrieden"
        elif self.friendship >= 100:
            return "Neutral"
        elif self.friendship >= 50:
            return "Unzufrieden"
        else:
            return "Sehr unzufrieden"
    

    
    def get_type_effectiveness_against(self, target_types: List[str]) -> Dict[str, float]:
        """
        Get type effectiveness of this monster's moves against target types.
        
        Args:
            target_types: List of target's types
            
        Returns:
            Dictionary of move type -> effectiveness
        """
        from engine.systems.types import type_chart
        
        effectiveness = {}
        for move in self.moves:
            if move.type not in effectiveness:
                effectiveness[move.type] = type_chart.calculate_type_multiplier(move.type, target_types)
        
        return effectiveness
    
    def get_defensive_effectiveness(self) -> Dict[str, float]:
        """
        Get defensive effectiveness against all types.
        
        Returns:
            Dictionary of attacking type -> effectiveness against this monster
        """
        from engine.systems.types import type_chart
        
        effectiveness = {}
        all_types = type_chart.get_all_types()
        
        for attacking_type in all_types:
            effectiveness[attacking_type] = type_chart.calculate_type_multiplier(attacking_type, self.types)
        
        return effectiveness
    
    def get_defensive_analysis(self) -> Dict[str, List[str]]:
        """
        Get complete defensive analysis (weaknesses, resistances, immunities).
        
        Returns:
            Dictionary with 'weaknesses', 'resistances', 'immunities' lists
        """
        defensive_effectiveness = self.get_defensive_effectiveness()
        
        weaknesses = []
        resistances = []
        immunities = []
        
        for type_name, effectiveness in defensive_effectiveness.items():
            if effectiveness > 1.0:
                weaknesses.append(type_name)
            elif 0 < effectiveness < 1.0:
                resistances.append(type_name)
            elif effectiveness == 0:
                immunities.append(type_name)
        
        return {
            'weaknesses': weaknesses,
            'resistances': resistances,
            'immunities': immunities
        }
    
    def get_weaknesses(self) -> List[str]:
        """Get types that are super effective against this monster."""
        return self.get_defensive_analysis()['weaknesses']
    
    def get_resistances(self) -> List[str]:
        """Get types that are not very effective against this monster."""
        return self.get_defensive_analysis()['resistances']
    
    def get_immunities(self) -> List[str]:
        """Get types that have no effect against this monster."""
        return self.get_defensive_analysis()['immunities']
    
    def get_optimal_moves_against(self, target_types: List[str]) -> List['Move']:
        """
        Get moves that are most effective against target types.
        
        Args:
            target_types: List of target's types
            
        Returns:
            List of moves sorted by effectiveness (best first)
        """
        effectiveness = self.get_type_effectiveness_against(target_types)
        
        # Sort moves by effectiveness and power
        def move_score(move):
            type_eff = effectiveness.get(move.type, 1.0)
            return type_eff * move.power
        
        return sorted(self.moves, key=move_score, reverse=True)
    
    def get_move(self, move_identifier: str) -> Optional['Move']:
        """
        Get a move by name or ID.
        
        Args:
            move_identifier: Name or ID of the move
            
        Returns:
            Move object or None if not found
        """
        for move in self.moves:
            if move.name.lower() == move_identifier.lower() or move.id == move_identifier:
                return move
        return None
    
    def has_move(self, move_identifier: str) -> bool:
        """
        Check if monster has a specific move.
        
        Args:
            move_identifier: Name or ID of the move
            
        Returns:
            True if monster has the move
        """
        return self.get_move(move_identifier) is not None
    
    def get_talent(self, talent_id: str) -> Optional[TalentInstance]:
        """
        Get a talent by ID.
        
        Args:
            talent_id: ID of the talent
            
        Returns:
            TalentInstance or None if not found
        """
        for talent in self.talents:
            if talent.talent_id == talent_id:
                return talent
        return None
    
    def has_talent(self, talent_id: str) -> bool:
        """
        Check if monster has a specific talent.
        
        Args:
            talent_id: ID of the talent
            
        Returns:
            True if monster has the talent
        """
        return self.get_talent(talent_id) is not None
    
    def get_learned_talents(self) -> List[TalentInstance]:
        """
        Get all learned talents.
        
        Returns:
            List of learned talents
        """
        return [talent for talent in self.talents if talent.is_learned]
    
    def get_available_talent_slots(self) -> int:
        """
        Get number of available talent slots.
        
        Returns:
            Number of available slots
        """
        # DQM-style: unlimited talent slots
        return 999
    
    def get_talent_progress(self, talent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get progress information for a talent.
        
        Args:
            talent_id: ID of the talent
            
        Returns:
            Progress info or None if talent not found
        """
        talent = self.get_talent(talent_id)
        if not talent:
            return None
        
        talent_info = self.get_talent_info(talent_id)
        if not talent_info:
            return None
        
        return {
            'talent_id': talent_id,
            'name': talent_info['name'],
            'current_tier': talent.current_tier.value,
            'experience': talent.experience,
            'is_learned': talent.is_learned,
            'progress_to_next_tier': talent.get_progress_to_next_tier()
        }
    
    def validate_talents(self) -> bool:
        """Validiere alle Talents des Monsters"""
        try:
            from engine.systems.talent_system import get_talent_database
            talent_db = get_talent_database()
            
            for talent_instance in self.talents:
                if talent_instance.is_learned:
                    talent = talent_db.get_talent(talent_instance.talent_id)
                    if not talent:
                        logger.warning(f"Talent {talent_instance.talent_id} nicht gefunden")
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Fehler bei der Talent-Validierung: {e}")
            return False