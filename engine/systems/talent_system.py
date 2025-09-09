"""
🎯 DQM Talent System - Dragon Quest Monsters Authentic Talent System
Implementiert das authentische DQM Talent-System für Move-Verfügbarkeit
"""

from typing import Dict, List, Optional, Any, Tuple, Set, TYPE_CHECKING
from enum import Enum, auto
from dataclasses import dataclass, field
import json
import logging
from pathlib import Path

if TYPE_CHECKING:
    from engine.systems.moves import Move, MoveCategory, MoveTarget, MoveEffect, EffectKind

logger = logging.getLogger(__name__)

class TalentCategory(Enum):
    """Talent-Kategorien basierend auf DQM"""
    ELEMENTAL = "elemental"      # Feuer, Eis, Blitz, etc.
    PHYSICAL = "physical"        # Kratzer, Biss, etc.
    HEALING = "healing"          # Heal, Multiheal, etc.
    SUPPORT = "support"          # Buff, Debuff, Status
    BREATH = "breath"           # Atem-Attacken
    SPECIAL = "special"         # Einzigartige Talents
    SYNTHESIS = "synthesis"     # Vererbungs-Talents

class TalentTier(Enum):
    """Talent-Stufen (wie in DQM)"""
    BASIC = 1       # Grundstufe
    INTERMEDIATE = 2 # Mittelstufe  
    ADVANCED = 3    # Fortgeschritten
    MASTER = 4      # Meisterstufe
    GRANDMASTER = 5 # Großmeister

@dataclass
class TalentMove:
    """Einzelner Move innerhalb eines Talents"""
    move_id: str
    tier_requirement: TalentTier
    level_requirement: int
    description: str = ""
    special_conditions: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PassiveAbility:
    """Passive Fähigkeit aus einem Talent"""
    name: str
    description: str
    effect_type: str  # "stat_boost", "damage_reduction", "status_immunity", etc.
    value: float
    conditions: List[str] = field(default_factory=list)  # Wann aktiv (z.B. "when_health_low")
    tier_requirement: TalentTier = TalentTier.BASIC

@dataclass
class Talent:
    """Einzelnes Talent (z.B. "Fire I", "Heal I")"""
    id: str
    name: str
    category: TalentCategory
    description: str
    moves: List[TalentMove] = field(default_factory=list)
    passive_abilities: List[PassiveAbility] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)  # Andere Talents die benötigt werden
    max_tier: TalentTier = TalentTier.MASTER
    is_inheritable: bool = True
    synthesis_bonus: float = 1.0  # Bonus bei Synthesis
    
    def get_moves_for_tier(self, tier: TalentTier, monster_level: int) -> List[str]:
        """Hole alle Moves die bei gegebener Tier und Level verfügbar sind"""
        available_moves = []
        for move in self.moves:
            if (move.tier_requirement.value <= tier.value and 
                monster_level >= move.level_requirement):
                available_moves.append(move.move_id)
        return available_moves
    
    def can_upgrade_to_tier(self, current_tier: TalentTier, monster_level: int) -> bool:
        """Prüfe ob Talent auf nächste Stufe upgraden kann"""
        if current_tier.value >= self.max_tier.value:
            return False
        
        next_tier = TalentTier(current_tier.value + 1)
        # Prüfe ob es Moves für die nächste Stufe gibt
        return bool(self.get_moves_for_tier(next_tier, monster_level))
    
    def get_passive_abilities_for_tier(self, tier: TalentTier) -> List[Dict[str, Any]]:
        """Hole alle passiven Fähigkeiten für gegebene Tier"""
        passive_abilities = []
        
        for ability in self.passive_abilities:
            if ability.tier_requirement.value <= tier.value:
                passive_abilities.append({
                    'name': ability.name,
                    'description': ability.description,
                    'effect_type': ability.effect_type,
                    'value': ability.value,
                    'conditions': ability.conditions,
                    'talent_id': self.id
                })
        
        return passive_abilities

@dataclass
class TalentInstance:
    """Individuelle Talent-Instanz eines Monsters"""
    talent_id: str
    current_tier: TalentTier = TalentTier.BASIC
    experience: int = 0
    is_learned: bool = False
    
    def get_experience_to_next_tier(self) -> int:
        """Berechne benötigte Erfahrung für nächste Stufe"""
        tier_costs = {
            TalentTier.BASIC: 0,
            TalentTier.INTERMEDIATE: 100,
            TalentTier.ADVANCED: 300,
            TalentTier.MASTER: 600,
            TalentTier.GRANDMASTER: 1000
        }
        
        if self.current_tier == TalentTier.GRANDMASTER:
            return 0
        
        next_tier = TalentTier(self.current_tier.value + 1)
        return tier_costs[next_tier] - self.experience
    
    def add_experience(self, amount: int) -> bool:
        """Füge Talent-Erfahrung hinzu. Returns True wenn Tier-Upgrade"""
        if not self.is_learned:
            return False
        
        self.experience += amount
        old_tier = self.current_tier
        
        # Prüfe Tier-Upgrades
        while (self.current_tier != TalentTier.GRANDMASTER and 
               self.experience >= self.get_experience_to_next_tier()):
            self.current_tier = TalentTier(self.current_tier.value + 1)
        
        return self.current_tier != old_tier

class TalentDatabase:
    """
    Zentrale Datenbank für alle DQM Talents
    Basiert auf authentischen Dragon Quest Monsters Talent-System
    """
    
    def __init__(self):
        self.talents: Dict[str, Talent] = {}
        self._move_registry = None
        self._initialize_default_talents()
        self._load_from_json()
        logger.info(f"Talent Database initialized with {len(self.talents)} talents")
    
    def _initialize_default_talents(self):
        """Initialisiere Standard-DQM Talents"""
        
        # ====== FEUER-TALENTS ======
        fire_talent = Talent(
            id="fire_i",
            name="Feuer I",
            category=TalentCategory.ELEMENTAL,
            description="Grundlegende Feuer-Attacken",
            moves=[
                TalentMove("funken", TalentTier.BASIC, 1, "Kleine Funken"),
                TalentMove("ember", TalentTier.BASIC, 3, "Glut"),
                TalentMove("feuerball", TalentTier.INTERMEDIATE, 10, "Feuerball"),
                TalentMove("flamethrower", TalentTier.ADVANCED, 25, "Flammenwurf")
            ],
            passive_abilities=[
                PassiveAbility(
                    name="Feuerresistenz",
                    description="Reduziert Feuerschaden um 10%",
                    effect_type="damage_reduction",
                    value=0.1,
                    conditions=["vs_fire"],
                    tier_requirement=TalentTier.BASIC
                ),
                PassiveAbility(
                    name="Verbrennungsschutz",
                    description="Immun gegen Verbrennung",
                    effect_type="status_immunity",
                    value=1.0,
                    conditions=["burn"],
                    tier_requirement=TalentTier.INTERMEDIATE
                )
            ]
        )
        self.talents["fire_i"] = fire_talent
        
        # Feuer-Gruppen-Attacken
        fire_group_talent = Talent(
            id="fire_group",
            name="Feuer-Gruppe",
            category=TalentCategory.ELEMENTAL,
            description="Feuer-Attacken gegen alle Gegner",
            moves=[
                TalentMove("sizz", TalentTier.BASIC, 5, "Feuerwelle auf alle"),
                TalentMove("sizzle", TalentTier.INTERMEDIATE, 15, "Größere Feuerwelle"),
                TalentMove("kasizz", TalentTier.ADVANCED, 30, "Mächtige Feuerwelle"),
                TalentMove("kasizzle", TalentTier.MASTER, 55, "Inferno auf alle")
            ]
        )
        self.talents["fire_group"] = fire_group_talent
        
        # ====== WASSER-TALENTS (Eis gibt's im Ruhrpott nicht) ======
        water_talent = Talent(
            id="water_i",
            name="Wasser I",
            category=TalentCategory.ELEMENTAL,
            description="Grundlegende Wasser-Attacken",
            moves=[
                TalentMove("blubber", TalentTier.BASIC, 1, "Blubberblasen"),
                TalentMove("water_gun", TalentTier.BASIC, 5, "Wasserpistole"),
                TalentMove("hydro_pump", TalentTier.ADVANCED, 25, "Hydropumpe")
            ]
        )
        self.talents["water_i"] = water_talent
        
        # ====== ENERGIE-TALENTS ======
        energy_talent = Talent(
            id="energy_i",
            name="Energie I",
            category=TalentCategory.ELEMENTAL,
            description="Grundlegende Energie-Attacken",
            moves=[
                TalentMove("funken", TalentTier.BASIC, 1, "Kleine Funken"),
                TalentMove("spark", TalentTier.BASIC, 5, "Funkensprung"),
                TalentMove("funkenschlag", TalentTier.INTERMEDIATE, 10, "Funkenschlag")
            ]
        )
        self.talents["energy_i"] = energy_talent
        
        # Blitz-Gruppen-Attacken
        thunder_group_talent = Talent(
            id="thunder_group",
            name="Blitz-Gruppe",
            category=TalentCategory.ELEMENTAL,
            description="Blitz-Attacken gegen alle Gegner",
            moves=[
                TalentMove("zammle", TalentTier.BASIC, 8, "Blitze auf alle"),
                TalentMove("thwack", TalentTier.INTERMEDIATE, 18, "Starke Blitze"),
                TalentMove("kathwack", TalentTier.ADVANCED, 35, "Gewitterfront")
            ]
        )
        self.talents["thunder_group"] = thunder_group_talent
        
        # ====== LUFT-TALENTS ======
        air_talent = Talent(
            id="air_i",
            name="Luft I",
            category=TalentCategory.ELEMENTAL,
            description="Luft-Attacken",
            moves=[
                TalentMove("gust", TalentTier.BASIC, 1, "Windstoß"),
                TalentMove("wirbelwind", TalentTier.INTERMEDIATE, 10, "Wirbelwind"),
                TalentMove("hurricane", TalentTier.ADVANCED, 25, "Orkan")
            ]
        )
        self.talents["air_i"] = air_talent
        
        # ====== ERDE-TALENTS ======
        earth_talent = Talent(
            id="earth_i",
            name="Erde I",
            category=TalentCategory.ELEMENTAL,
            description="Erd-Attacken",
            moves=[
                TalentMove("mud_slap", TalentTier.BASIC, 1, "Lehmklatscher"),
                TalentMove("lehmschuss", TalentTier.BASIC, 5, "Lehmschuss"),
                TalentMove("steinwurf", TalentTier.INTERMEDIATE, 10, "Steinwurf"),
                TalentMove("earthquake", TalentTier.ADVANCED, 25, "Erdbeben")
            ]
        )
        self.talents["earth_i"] = earth_talent
        
        # ====== CHAOS-TALENTS ======
        chaos_talent = Talent(
            id="chaos_i",
            name="Chaos I",
            category=TalentCategory.ELEMENTAL,
            description="Chaos-Attacken",
            moves=[
                TalentMove("confusion", TalentTier.BASIC, 5, "Verwirrung"),
                TalentMove("chaos_wave", TalentTier.INTERMEDIATE, 15, "Chaoswelle"),
                TalentMove("chaosblitz", TalentTier.ADVANCED, 25, "Chaosblitz")
            ]
        )
        self.talents["chaos_i"] = chaos_talent
        
        # ====== SEUCHE-TALENTS ======
        plague_talent = Talent(
            id="plague_i",
            name="Seuche I",
            category=TalentCategory.ELEMENTAL,
            description="Gift- und Seuchen-Attacken",
            moves=[
                TalentMove("poison_sting", TalentTier.BASIC, 1, "Giftstachel"),
                TalentMove("giftwolke", TalentTier.BASIC, 5, "Giftwolke"),
                TalentMove("pesthauch", TalentTier.INTERMEDIATE, 15, "Pesthauch")
            ]
        )
        self.talents["plague_i"] = plague_talent
        
        # ====== PFLANZE-TALENTS ======
        plant_talent = Talent(
            id="plant_i",
            name="Pflanze I",
            category=TalentCategory.ELEMENTAL,
            description="Pflanzen-Attacken",
            moves=[
                TalentMove("vine_whip", TalentTier.BASIC, 1, "Rankenhieb"),
                TalentMove("samenbombe", TalentTier.INTERMEDIATE, 10, "Samenbombe"),
                TalentMove("blattsturm", TalentTier.ADVANCED, 25, "Blattsturm")
            ]
        )
        self.talents["plant_i"] = plant_talent
        
        # ====== MYSTIK-TALENTS ======
        mystic_talent = Talent(
            id="mystic_i",
            name="Mystik I",
            category=TalentCategory.ELEMENTAL,
            description="Mystische Attacken",
            moves=[
                TalentMove("spukball", TalentTier.BASIC, 5, "Spukball"),
                TalentMove("hypnose", TalentTier.INTERMEDIATE, 10, "Hypnose"),
                TalentMove("fluch", TalentTier.INTERMEDIATE, 15, "Fluch"),
                TalentMove("schattenhieb", TalentTier.ADVANCED, 20, "Schattenhieb")
            ]
        )
        self.talents["mystic_i"] = mystic_talent
        
        # ====== HEIL-TALENTS ======
        heal_talent = Talent(
            id="heal_i",
            name="Heil I",
            category=TalentCategory.HEALING,
            description="Grundlegende Heilungs-Skills",
            moves=[
                TalentMove("heal", TalentTier.BASIC, 1, "Heilt 30 HP"),
                TalentMove("midheal", TalentTier.INTERMEDIATE, 12, "Heilt 75 HP"),
                TalentMove("fullheal", TalentTier.ADVANCED, 30, "Heilt alle HP"),
                TalentMove("omniheal", TalentTier.MASTER, 55, "Heilt alle HP aller Verbündeten")
            ]
        )
        self.talents["heal_i"] = heal_talent
        
        # Gruppen-Heilung
        multiheal_talent = Talent(
            id="multiheal",
            name="Multi-Heil",
            category=TalentCategory.HEALING,
            description="Heilung für alle Verbündeten",
            moves=[
                TalentMove("multiheal", TalentTier.BASIC, 8, "Heilt 25 HP aller Verbündeten"),
                TalentMove("moreheal", TalentTier.INTERMEDIATE, 20, "Heilt 50 HP aller Verbündeten"),
                TalentMove("omniheal", TalentTier.ADVANCED, 40, "Heilt 100 HP aller Verbündeten")
            ]
        )
        self.talents["multiheal"] = multiheal_talent
        
        # ====== BUFF-TALENTS ======
        buff_talent = Talent(
            id="buff_i",
            name="Verstärkung I",
            category=TalentCategory.SUPPORT,
            description="Stat-Verstärkungen für Verbündete",
            moves=[
                TalentMove("buff", TalentTier.BASIC, 2, "Erhöht ATK"),
                TalentMove("kabuff", TalentTier.BASIC, 2, "Erhöht DEF"),
                TalentMove("oomph", TalentTier.INTERMEDIATE, 15, "Verdoppelt ATK"),
                TalentMove("insulatle", TalentTier.INTERMEDIATE, 18, "Erhöht Feuer/Eis-Resistenz")
            ]
        )
        self.talents["buff_i"] = buff_talent
        
        # Speed-Buffs
        speed_talent = Talent(
            id="speed_buff",
            name="Geschwindigkeit",
            category=TalentCategory.SUPPORT,
            description="Speed-Verstärkungen",
            moves=[
                TalentMove("acceleratle", TalentTier.BASIC, 4, "Erhöht Speed aller Verbündeten"),
                TalentMove("accelerate", TalentTier.INTERMEDIATE, 16, "Erhöht Speed stark")
            ]
        )
        self.talents["speed_buff"] = speed_talent
        
        # ====== DEBUFF-TALENTS ======
        debuff_talent = Talent(
            id="debuff_i",
            name="Schwächung I",
            category=TalentCategory.SUPPORT,
            description="Stat-Schwächungen für Gegner",
            moves=[
                TalentMove("sap", TalentTier.BASIC, 3, "Senkt DEF eines Gegners"),
                TalentMove("kasap", TalentTier.INTERMEDIATE, 14, "Senkt DEF aller Gegner"),
                TalentMove("blunt", TalentTier.BASIC, 3, "Senkt ATK eines Gegners")
            ]
        )
        self.talents["debuff_i"] = debuff_talent
        
        # Speed-Debuffs
        slow_talent = Talent(
            id="slow_debuff",
            name="Verlangsamung",
            category=TalentCategory.SUPPORT,
            description="Speed-Schwächungen",
            moves=[
                TalentMove("decelerate", TalentTier.BASIC, 5, "Senkt Speed aller Gegner"),
                TalentMove("deceleratle", TalentTier.INTERMEDIATE, 17, "Senkt Speed stark")
            ]
        )
        self.talents["slow_debuff"] = slow_talent
        
        # ====== STATUS-TALENTS ======
        status_talent = Talent(
            id="status_i",
            name="Status I",
            category=TalentCategory.SUPPORT,
            description="Status-Effekte auf Gegner",
            moves=[
                TalentMove("snooze", TalentTier.BASIC, 6, "Versetzt Gegner in Schlaf"),
                TalentMove("kasnooze", TalentTier.INTERMEDIATE, 19, "Tiefschlaf für alle Gegner")
            ]
        )
        self.talents["status_i"] = status_talent
        
        # ====== ATEM-TALENTS ======
        fire_breath_talent = Talent(
            id="fire_breath",
            name="Feueratem",
            category=TalentCategory.BREATH,
            description="Feuer-Atem-Attacken (kostenlos)",
            moves=[
                TalentMove("fire_breath", TalentTier.BASIC, 1, "Feueratem auf alle Gegner"),
                TalentMove("flame_breath", TalentTier.INTERMEDIATE, 12, "Starker Feueratem"),
                TalentMove("inferno", TalentTier.ADVANCED, 28, "Höllisches Inferno"),
                TalentMove("scorch", TalentTier.MASTER, 50, "Alles verbrennender Atem")
            ]
        )
        self.talents["fire_breath"] = fire_breath_talent
        
        ice_breath_talent = Talent(
            id="ice_breath",
            name="Eisatem",
            category=TalentCategory.BREATH,
            description="Eis-Atem-Attacken (kostenlos)",
            moves=[
                TalentMove("cool_breath", TalentTier.BASIC, 1, "Eisiger Atem"),
                TalentMove("ice_breath", TalentTier.INTERMEDIATE, 13, "Frostiger Atem"),
                TalentMove("blizzard_breath", TalentTier.ADVANCED, 29, "Blizzard-Atem"),
                TalentMove("cold_breath", TalentTier.MASTER, 52, "Absolut null Atem")
            ]
        )
        self.talents["ice_breath"] = ice_breath_talent
        
        # ====== PHYSICAL-TALENTS ======
        physical_talent = Talent(
            id="physical_i",
            name="Körperlich I",
            category=TalentCategory.PHYSICAL,
            description="Grundlegende körperliche Attacken",
            moves=[
                TalentMove("kratzer", TalentTier.BASIC, 1, "Kratzer"),
                TalentMove("bite", TalentTier.BASIC, 3, "Biss"),
                TalentMove("kopfnuss", TalentTier.INTERMEDIATE, 8, "Kopfnuss"),
                TalentMove("tackle", TalentTier.BASIC, 1, "Rempler")
            ],
            passive_abilities=[
                PassiveAbility(
                    name="Körperkraft",
                    description="Erhöht physischen Angriff um 5%",
                    effect_type="stat_boost",
                    value=0.05,
                    conditions=["physical_attacks"],
                    tier_requirement=TalentTier.BASIC
                ),
                PassiveAbility(
                    name="Widerstandsfähigkeit",
                    description="Reduziert physischen Schaden um 5%",
                    effect_type="damage_reduction",
                    value=0.05,
                    conditions=["vs_physical"],
                    tier_requirement=TalentTier.INTERMEDIATE
                )
            ]
        )
        self.talents["physical_i"] = physical_talent
        
        # ====== SPECIAL-TALENTS ======
        dance_talent = Talent(
            id="dance",
            name="Tanz",
            category=TalentCategory.SPECIAL,
            description="Tanz-Skills mit zufälligen Effekten",
            moves=[
                TalentMove("sultry_dance", TalentTier.BASIC, 10, "Verführerischer Tanz"),
                TalentMove("hustle_dance", TalentTier.INTERMEDIATE, 25, "Heilt alle Verbündeten"),
                TalentMove("death_dance", TalentTier.ADVANCED, 45, "Todestanz - instant KO möglich")
            ]
        )
        self.talents["dance"] = dance_talent
        
        slash_talent = Talent(
            id="slash",
            name="Schnitt",
            category=TalentCategory.SPECIAL,
            description="Spezielle Schnitt-Attacken",
            moves=[
                TalentMove("dragon_slash", TalentTier.BASIC, 15, "Extra Schaden gegen Drachen"),
                TalentMove("metal_slash", TalentTier.BASIC, 12, "Durchdringt Metal-Verteidigung"),
                TalentMove("falcon_slash", TalentTier.INTERMEDIATE, 22, "Zwei schnelle Schläge"),
                TalentMove("gigaslash", TalentTier.ADVANCED, 40, "Mächtiger Schwerthieb mit Blitz")
            ]
        )
        self.talents["slash"] = slash_talent
    
    def _get_move_registry(self):
        """Lazy loading des Move-Registry"""
        if self._move_registry is None:
            from engine.systems.moves import move_registry
            self._move_registry = move_registry
        return self._move_registry
    
    def get_available_moves_from_talents(self, talent_instances: List[TalentInstance], 
                                       monster_level: int) -> List['Move']:
        """Lade verfügbare Moves aus gelernten Talents"""
        moves = []
        
        for talent_instance in talent_instances:
            if talent_instance.is_learned:
                talent = self.get_talent(talent_instance.talent_id)
                if talent:
                    move_ids = talent.get_moves_for_tier(
                        talent_instance.current_tier, 
                        monster_level
                    )
                    # Konvertiere move_ids zu Move-Objekten
                    moves.extend(self._convert_move_ids_to_objects(move_ids))
        
        return moves

    def _convert_move_ids_to_objects(self, move_ids: List[str]) -> List['Move']:
        """Konvertiere Move-IDs zu Move-Objekten"""
        moves = []
        
        for move_id in move_ids:
            move = self._create_move_from_id(move_id)
            if move:
                moves.append(move)
        
        return moves

    def _create_move_from_id(self, move_id: str) -> Optional['Move']:
        """Erstelle Move-Objekt aus Move-ID"""
        try:
            from engine.systems.moves import Move, MoveCategory, MoveTarget, MoveEffect, EffectKind
            
            # Versuche zuerst Move aus Registry zu laden
            move_registry = self._get_move_registry()
            existing_move = move_registry.get_move(move_id)
            if existing_move:
                return existing_move
            
            # Falls nicht gefunden, hole Move-Daten aus Talent
            move_data = self._get_move_data_from_talents(move_id)
            if not move_data:
                logger.warning(f"Move-Daten für {move_id} nicht gefunden in Talents")
                return None
            
            # Bestimme korrekte Kategorie basierend auf Talent
            category_str = self._get_category_from_talent_category(talent.category)
            try:
                category = MoveCategory(category_str)
            except ValueError:
                category = MoveCategory.PHYSICAL
            
            # Erstelle Move-Objekt
            move = Move(
                id=move_id,
                name=move_data.get('name', move_id),
                type=move_data.get('type', 'Normal'),
                category=category,
                power=move_data.get('power', 40),
                accuracy=move_data.get('accuracy', 100),
                priority=move_data.get('priority', 0),
                targeting=MoveTarget(move_data.get('targeting', 'ENEMY')),
                effects=self._create_move_effects(move_data.get('effects', [])),
                description=move_data.get('description', '')
            )
            
            return move
            
        except Exception as e:
            logger.error(f"Fehler beim Erstellen von Move {move_id}: {e}")
            return None

    def _get_move_data_from_talents(self, move_id: str) -> Optional[Dict[str, Any]]:
        """Hole Move-Daten aus Talent-System"""
        try:
            # Suche in allen Talents nach dem Move
            for talent in self.talents.values():
                for talent_move in talent.moves:
                    if talent_move.move_id == move_id:
                        # Erstelle Standard-Move-Daten basierend auf Talent-Kategorie
                        move_data = {
                            'name': talent_move.description or move_id,
                            'type': self._get_type_from_talent_category(talent.category),
                            'category': self._get_category_from_talent_category(talent.category),
                            'power': self._get_default_power_for_move(move_id, talent.category),
                            'accuracy': 100,
                            'priority': 0,
                            'targeting': 'ENEMY',
                            'effects': [],
                            'description': talent_move.description or f"Move aus {talent.name}"
                        }
                        return move_data
            
            return None
            
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Move-Daten für {move_id}: {e}")
            return None

    def _get_type_from_talent_category(self, category: TalentCategory) -> str:
        """Konvertiere Talent-Kategorie zu Move-Type"""
        type_mapping = {
            TalentCategory.ELEMENTAL: "Feuer",  # Default für Elemental
            TalentCategory.PHYSICAL: "Bestie",
            TalentCategory.HEALING: "Mystik",
            TalentCategory.SUPPORT: "Mystik",
            TalentCategory.BREATH: "Feuer",  # Default für Breath
            TalentCategory.SPECIAL: "Bestie",
            TalentCategory.SYNTHESIS: "Mystik"
        }
        return type_mapping.get(category, "Normal")

    def _get_category_from_talent_category(self, category: TalentCategory) -> str:
        """Konvertiere Talent-Kategorie zu Move-Kategorie"""
        category_mapping = {
            TalentCategory.ELEMENTAL: "MAGICAL",
            TalentCategory.PHYSICAL: "PHYSICAL", 
            TalentCategory.HEALING: "STATUS",
            TalentCategory.SUPPORT: "STATUS",
            TalentCategory.BREATH: "MAGICAL",
            TalentCategory.SPECIAL: "PHYSICAL",
            TalentCategory.SYNTHESIS: "STATUS"
        }
        return category_mapping.get(category, "PHYSICAL")

    def _get_default_power_for_move(self, move_id: str, category: TalentCategory) -> int:
        """Berechne Standard-Power für Move basierend auf ID und Kategorie"""
        # Einfache Heuristik basierend auf Move-ID
        if any(keyword in move_id.lower() for keyword in ['heal', 'buff', 'debuff', 'status']):
            return 0  # Support-Moves haben keine Power
        
        # Power basierend auf Kategorie
        power_mapping = {
            TalentCategory.ELEMENTAL: 65,
            TalentCategory.PHYSICAL: 60,
            TalentCategory.HEALING: 0,
            TalentCategory.SUPPORT: 0,
            TalentCategory.BREATH: 70,
            TalentCategory.SPECIAL: 80,
            TalentCategory.SYNTHESIS: 0
        }
        return power_mapping.get(category, 50)

    def _create_move_effects(self, effects_data: List[Dict[str, Any]]) -> List['MoveEffect']:
        """Erstelle MoveEffect-Objekte aus Daten"""
        try:
            from engine.systems.moves import MoveEffect, EffectKind
            
            effects = []
            for effect_data in effects_data:
                effect = MoveEffect(
                    kind=EffectKind.from_string(effect_data.get('kind', 'damage')),
                    chance=effect_data.get('chance', 100.0),
                    power=effect_data.get('power'),
                    stat=effect_data.get('stat'),
                    stages=effect_data.get('stages'),
                    status=effect_data.get('status'),
                    amount=effect_data.get('amount'),
                    percent=effect_data.get('percent', False),
                    duration=effect_data.get('duration')
                )
                effects.append(effect)
            
            return effects
            
        except Exception as e:
            logger.error(f"Fehler beim Erstellen der Move-Effects: {e}")
            return []

    def validate_talent_system(self) -> bool:
        """Validiere Talent-System gegen talents.json"""
        try:
            # Lade talents.json
            talents_data = self._load_talents_json()
            
            # Validiere alle Talents
            for talent in self.talents.values():
                if not self._validate_talent_against_json(talent, talents_data):
                    return False
            
            logger.info("Talent-System Validierung erfolgreich")
            return True
            
        except Exception as e:
            logger.error(f"Talent-System Validierung fehlgeschlagen: {e}")
            return False

    def _load_talents_json(self) -> Dict[str, Any]:
        """Lade talents.json für Validierung"""
        try:
            json_path = Path("data/talents.json")
            if json_path.exists():
                with open(json_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Fehler beim Laden von talents.json: {e}")
            return {}

    def _validate_talent_against_json(self, talent: Talent, json_data: Dict[str, Any]) -> bool:
        """Validiere einzelnes Talent gegen JSON-Daten"""
        try:
            # Suche Talent in JSON-Daten
            json_talents = json_data.get("talents", [])
            json_talent = None
            for t in json_talents:
                if t.get("id") == talent.id:
                    json_talent = t
                    break
            
            if not json_talent:
                logger.warning(f"Talent {talent.id} nicht in JSON gefunden")
                return True  # Nicht kritisch, da es Default-Talents geben kann
            
            # Validiere grundlegende Eigenschaften
            if json_talent.get("name") != talent.name:
                logger.warning(f"Name mismatch für Talent {talent.id}")
            
            if json_talent.get("category") != talent.category.value:
                logger.warning(f"Category mismatch für Talent {talent.id}")
            
            # Validiere Moves
            json_moves = json_talent.get("moves", [])
            for talent_move in talent.moves:
                move_found = any(
                    m.get("move_id") == talent_move.move_id 
                    for m in json_moves
                )
                if not move_found:
                    logger.warning(f"Move {talent_move.move_id} nicht in JSON für Talent {talent.id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Fehler bei der Talent-Validierung für {talent.id}: {e}")
            return False
    
    def _load_from_json(self):
        """Lade zusätzliche Talents aus JSON-Datei"""
        json_path = Path("data/talents.json")
        if json_path.exists():
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for talent_data in data.get("talents", []):
                    talent = self._create_talent_from_dict(talent_data)
                    if talent:
                        self.talents[talent.id] = talent
                
                logger.info(f"Loaded {len(data.get('talents', []))} additional talents from JSON")
            except Exception as e:
                logger.error(f"Error loading talents from JSON: {e}")
    
    def _create_talent_from_dict(self, data: Dict[str, Any]) -> Optional[Talent]:
        """Erstelle Talent aus Dictionary"""
        try:
            moves = []
            for move_data in data.get("moves", []):
                move = TalentMove(
                    move_id=move_data["move_id"],
                    tier_requirement=TalentTier(move_data["tier_requirement"]),
                    level_requirement=move_data["level_requirement"],
                    description=move_data.get("description", ""),
                    special_conditions=move_data.get("special_conditions", {})
                )
                moves.append(move)
            
            return Talent(
                id=data["id"],
                name=data["name"],
                category=TalentCategory(data["category"]),
                description=data["description"],
                moves=moves,
                prerequisites=data.get("prerequisites", []),
                max_tier=TalentTier(data.get("max_tier", 4)),
                is_inheritable=data.get("is_inheritable", True),
                synthesis_bonus=data.get("synthesis_bonus", 1.0)
            )
        except Exception as e:
            logger.error(f"Error creating talent from dict: {e}")
            return None
    
    def get_talent(self, talent_id: str) -> Optional[Talent]:
        """Hole Talent by ID"""
        return self.talents.get(talent_id)
    
    def get_talents_by_category(self, category: TalentCategory) -> List[Talent]:
        """Hole alle Talents einer Kategorie"""
        return [t for t in self.talents.values() if t.category == category]
    
    def get_available_moves(self, talent_instances: List[TalentInstance], 
                          monster_level: int) -> List[str]:
        """Hole alle verfügbaren Moves basierend auf Talent-Instanzen"""
        available_moves = set()
        
        for talent_instance in talent_instances:
            if not talent_instance.is_learned:
                continue
            
            talent = self.get_talent(talent_instance.talent_id)
            if talent:
                moves = talent.get_moves_for_tier(
                    talent_instance.current_tier, 
                    monster_level
                )
                available_moves.update(moves)
        
        return list(available_moves)
    
    def can_learn_talent(self, talent_id: str, 
                        current_talents: List[TalentInstance],
                        monster_level: int) -> bool:
        """Prüfe ob Monster ein Talent lernen kann"""
        talent = self.get_talent(talent_id)
        if not talent:
            return False
        
        # Prüfe ob bereits gelernt
        for t in current_talents:
            if t.talent_id == talent_id and t.is_learned:
                return False
        
        # Prüfe Prerequisites
        for prereq_id in talent.prerequisites:
            has_prereq = any(t.talent_id == prereq_id and t.is_learned 
                           for t in current_talents)
            if not has_prereq:
                return False
        
        # Prüfe Level-Requirement (mindestens ein Move muss verfügbar sein)
        basic_moves = talent.get_moves_for_tier(TalentTier.BASIC, monster_level)
        return bool(basic_moves)
    
    def get_learnable_talents(self, monster_types: List[str],
                            current_talents: List[TalentInstance],
                            monster_level: int) -> List[Talent]:
        """Hole alle lernbaren Talents für ein Monster"""
        learnable = []
        
        for talent in self.talents.values():
            if self.can_learn_talent(talent.id, current_talents, monster_level):
                # Prüfe Type-Kompatibilität
                if self._is_talent_compatible_with_types(talent, monster_types):
                    learnable.append(talent)
        
        return learnable
    
    def _is_talent_compatible_with_types(self, talent: Talent, 
                                       monster_types: List[str]) -> bool:
        """Prüfe ob Talent mit Monster-Types kompatibel ist"""
        # Elemental Talents müssen mit Monster-Types übereinstimmen
        if talent.category == TalentCategory.ELEMENTAL:
            type_mapping = {
                "Feuer": ["fire_i", "fire_group", "fire_breath"],
                "Eis": ["ice_i", "ice_breath"],
                "Blitz": ["thunder_i", "thunder_group"],
                "Wind": ["wind_i"],
                "Erde": ["explosion_i"],
                "Chaos": ["dark_i"]
            }
            
            for monster_type in monster_types:
                compatible_talents = type_mapping.get(monster_type, [])
                if talent.id in compatible_talents:
                    return True
            return False
        
        # Andere Talents sind für alle Types verfügbar
        return True
    
    def calculate_talent_inheritance(self, parent1_talents: List[TalentInstance],
                                   parent2_talents: List[TalentInstance]) -> List[str]:
        """Berechne Talent-Vererbung für Synthesis"""
        inherited = []
        
        # Regel 1: Gemeinsame Talents werden vererbt
        parent1_learned = [t.talent_id for t in parent1_talents if t.is_learned]
        parent2_learned = [t.talent_id for t in parent2_talents if t.is_learned]
        common_talents = set(parent1_learned) & set(parent2_learned)
        inherited.extend(list(common_talents)[:2])  # Max 2 gemeinsame
        
        # Regel 2: Zufällige Talents von Eltern
        all_parent_talents = list(set(parent1_learned + parent2_learned) - set(inherited))
        import random
        random.shuffle(all_parent_talents)
        
        # Füge bis zu 3 weitere Talents hinzu
        for talent_id in all_parent_talents:
            if len(inherited) >= 5:  # Maximum 5 Talents
                break
            if talent_id not in inherited:
                inherited.append(talent_id)
        
        return inherited[:5]
    
    def create_move_from_talent_data(self, move_id: str) -> Optional['Move']:
        """
        Erstelle Move-Objekt aus Talent-Daten.
        
        Args:
            move_id: ID des Moves
            
        Returns:
            Move-Objekt oder None
        """
        try:
            from engine.systems.moves import move_registry
            
            # Versuche Move aus Move-Registry zu holen
            move = move_registry.create_move_instance(move_id)
            if move:
                return move
            
            # Fallback: Erstelle Dummy-Move
            logger.warning(f"Move {move_id} nicht in Move-Registry gefunden, erstelle Dummy-Move")
            from engine.systems.moves import Move, MoveCategory, MoveTarget, MoveEffect, EffectKind
            
            return Move(
                id=move_id,
                name=move_id.replace('_', ' ').title(),
                type="Bestie",
                category=MoveCategory.PHYSICAL,
                power=40,
                accuracy=100,
                priority=0,
                targeting=MoveTarget.ENEMY,
                effects=[MoveEffect(kind=EffectKind.DAMAGE, power=40)],
                description=f"Talent-basierter Move: {move_id}",
                contact=False,
                sound_based=False,
                punching=False,
                biting=False,
                pulse=False,
                multi_hit=None,
                drain_percent=0,
                recoil_percent=0,
                multi_hit_min=1,
                multi_hit_max=1
            )
            
        except Exception as e:
            logger.error(f"Fehler beim Erstellen des Moves aus Talent-Daten: {e}")
            return None
    
    def export_to_json(self, filepath: str):
        """Exportiere Talent-Datenbank als JSON"""
        data = {
            "talents": []
        }
        
        for talent in self.talents.values():
            talent_data = {
                "id": talent.id,
                "name": talent.name,
                "category": talent.category.value,
                "description": talent.description,
                "moves": [
                    {
                        "move_id": move.move_id,
                        "tier_requirement": move.tier_requirement.value,
                        "level_requirement": move.level_requirement,
                        "description": move.description,
                        "special_conditions": move.special_conditions
                    }
                    for move in talent.moves
                ],
                "prerequisites": talent.prerequisites,
                "max_tier": talent.max_tier.value,
                "is_inheritable": talent.is_inheritable,
                "synthesis_bonus": talent.synthesis_bonus
            }
            data["talents"].append(talent_data)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Exported talent database to {filepath}")


# Singleton-Instanz
_talent_db_instance = None

def get_talent_database() -> TalentDatabase:
    """Hole Singleton-Instanz der Talent-Datenbank"""
    global _talent_db_instance
    if _talent_db_instance is None:
        _talent_db_instance = TalentDatabase()
    return _talent_db_instance


# Test-Code removed - use proper testing framework instead
