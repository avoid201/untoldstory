"""
Test Monster Factory für Ruhrpott-Monster
Erstellt realistische Test-Monster für alle Battle-Tests
"""

from typing import List, Dict, Any
from engine.systems.monster_instance import MonsterInstance, MonsterSpecies, StatusCondition
from engine.systems.moves import Move, MoveCategory, MoveTarget, EffectKind
from engine.systems.types import TypeSystem


class TestMonsters:
    """Realistische Test-Monster aus dem Ruhrpott."""
    
    @staticmethod
    def create_schachtschreck():
        """Tier 1 Monster - Anfänger."""
        return MonsterInstance(
            species_id="schachtschreck",
            name="Schachtschreck",
            level=5,
            stats={
                "hp": 45, "mp": 20,
                "atk": 35, "def": 30,
                "mag": 15, "res": 25,
                "spd": 40
            },
            moves=[
                Move(
                    name="Kohleschlag",
                    power=40,
                    pp=25,
                    category=MoveCategory.PHYSICAL,
                    target=MoveTarget.ENEMY,
                    type="earth"
                ),
                Move(
                    name="Grubengas",
                    power=30,
                    pp=15,
                    category=MoveCategory.MAGICAL,
                    target=MoveTarget.ENEMY,
                    type="dark",
                    effects=[MoveEffect(
                        kind=EffectKind.STATUS,
                        status="poison",
                        chance=30.0
                    )]
                ),
            ],
            types=["earth", "dark"],
            traits=["Zechen-Wut", "Staublunge"],
            rank="F"
        )
    
    @staticmethod
    def create_currywurst_phoenix():
        """Tier 2 Monster - Fortgeschritten."""
        return MonsterInstance(
            species_id="currywurst_phoenix",
            name="Currywurst-Phoenix",
            level=25,
            stats={
                "hp": 120, "mp": 80,
                "atk": 65, "def": 55,
                "mag": 90, "res": 70,
                "spd": 75
            },
            moves=[
                Move(
                    name="Scharfer Biss",
                    power=60,
                    pp=20,
                    category=MoveCategory.PHYSICAL,
                    target=MoveTarget.ENEMY,
                    type="normal"
                ),
                Move(
                    name="Curryfeuer",
                    power=80,
                    pp=10,
                    category=MoveCategory.MAGICAL,
                    target=MoveTarget.ENEMY,
                    type="fire"
                ),
                Move(
                    name="Pommes-Schwall",
                    power=50,
                    pp=15,
                    category=MoveCategory.MAGICAL,
                    target=MoveTarget.ALL_ENEMIES,
                    type="food",
                    effects=[MoveEffect(
                        kind=EffectKind.DAMAGE,
                        hits=2
                    )]
                ),
                Move(
                    name="Heilende Soße",
                    power=0,
                    pp=5,
                    category=MoveCategory.SUPPORT,
                    target=MoveTarget.ALLY,
                    type="normal",
                    effects=[MoveEffect(
                        kind=EffectKind.HEAL,
                        amount=50
                    )]
                )
            ],
            types=["fire", "food"],
            traits=["Imbiss-Immunität", "Scharfe Aura"],
            rank="C"
        )
    
    @staticmethod
    def create_ruhrpott_ritter():
        """Tier 3 Monster - Elite."""
        return MonsterInstance(
            species_id="ruhrpott_ritter",
            name="Ruhrpott-Ritter",
            level=50,
            stats={
                "hp": 200, "mp": 150,
                "atk": 120, "def": 110,
                "mag": 80, "res": 100,
                "spd": 95
            },
            moves=[
                Move(
                    name="Stahlschwert",
                    power=100,
                    pp=15,
                    category=MoveCategory.PHYSICAL,
                    target=MoveTarget.ENEMY,
                    type="steel"
                ),
                Move(
                    name="Industrie-Donner",
                    power=120,
                    pp=8,
                    category=MoveCategory.MAGICAL,
                    target=MoveTarget.ALL_ENEMIES,
                    type="electric"
                ),
                Move(
                    name="Schutzschild",
                    power=0,
                    pp=10,
                    category=MoveCategory.SUPPORT,
                    target=MoveTarget.SELF,
                    type="normal",
                    effects=[MoveEffect(
                        kind=EffectKind.BUFF,
                        stat="def",
                        stages=2
                    )]
                )
            ],
            types=["steel", "electric"],
            traits=["Stahlhaut", "Elektrische Aura"],
            rank="B"
        )
    
    @staticmethod
    def create_bergmann_meister():
        """Tier 4 Monster - Legendär."""
        return MonsterInstance(
            species_id="bergmann_meister",
            name="Bergmann-Meister",
            level=80,
            stats={
                "hp": 300, "mp": 250,
                "atk": 180, "def": 200,
                "mag": 160, "res": 180,
                "spd": 140
            },
            moves=[
                Move(
                    name="Tiefen-Schlag",
                    power=150,
                    pp=5,
                    category=MoveCategory.PHYSICAL,
                    target=MoveTarget.ENEMY,
                    type="earth"
                ),
                Move(
                    name="Kohle-Explosion",
                    power=200,
                    pp=3,
                    category=MoveCategory.MAGICAL,
                    target=MoveTarget.ALL_ENEMIES,
                    type="fire",
                    effects=[MoveEffect(
                        kind=EffectKind.RECOIL,
                        amount=25
                    )]
                ),
                Move(
                    name="Bergwerk-Heilung",
                    power=0,
                    pp=8,
                    category=MoveCategory.SUPPORT,
                    target=MoveTarget.ALL_ALLIES,
                    type="normal",
                    effects=[MoveEffect(
                        kind=EffectKind.HEAL,
                        amount=100,
                        percent=True
                    )]
                )
            ],
            types=["earth", "fire"],
            traits=["Bergwerk-Meister", "Unzerstörbar"],
            rank="S"
    )
    
    @staticmethod
    def create_weak_monster():
        """Sehr schwaches Monster für Edge-Case-Tests."""
        return MonsterInstance(
            species_id="schwaechling",
            name="Schwächling",
            level=1,
            stats={
                "hp": 10, "mp": 5,
                "atk": 5, "def": 5,
                "mag": 5, "res": 5,
                "spd": 5
            },
            moves=[
                Move(
                    name="Schwacher Schlag",
                    power=10,
                    pp=10,
                    category=MoveCategory.PHYSICAL,
                    target=MoveTarget.ENEMY,
                    type="normal"
                )
            ],
            types=["normal"],
            traits=[],
            rank="F"
        )
    
    @staticmethod
    def create_tank_monster():
        """Monster mit hoher Verteidigung für Tank-Tests."""
        return MonsterInstance(
            species_id="panzer_monster",
            name="Panzer-Monster",
            level=30,
            stats={
                "hp": 300, "mp": 50,
                "atk": 40, "def": 200,
                "mag": 30, "res": 180,
                "spd": 20
            },
            moves=[
                Move(
                    name="Panzer-Schlag",
                    power=30,
                    pp=20,
                    category=MoveCategory.PHYSICAL,
                    target=MoveTarget.ENEMY,
                    type="steel"
                ),
                Move(
                    name="Verteidigung",
                    power=0,
                    pp=15,
                    category=MoveCategory.SUPPORT,
                    target=MoveTarget.SELF,
                    type="normal",
                    effects=[MoveEffect(
                        kind=EffectKind.BUFF,
                        stat="def",
                        stages=3
                    )]
                )
            ],
            types=["steel"],
            traits=["Panzerhaut", "Unbeweglich"],
            rank="D"
        )
    
    @staticmethod
    def create_speed_monster():
        """Monster mit hoher Geschwindigkeit für Speed-Tests."""
        return MonsterInstance(
            species_id="blitz_monster",
            name="Blitz-Monster",
            level=25,
            stats={
                "hp": 80, "mp": 60,
                "atk": 70, "def": 40,
                "mag": 60, "res": 40,
                "spd": 200
            },
            moves=[
                Move(
                    name="Blitz-Angriff",
                    power=50,
                    pp=25,
                    category=MoveCategory.PHYSICAL,
                    target=MoveTarget.ENEMY,
                    type="electric"
                ),
                Move(
                    name="Schnelle Heilung",
                    power=0,
                    pp=10,
                    category=MoveCategory.SUPPORT,
                    target=MoveTarget.SELF,
                    type="normal",
                    effects=[MoveEffect(
                        kind=EffectKind.HEAL,
                        amount=30
                    )]
                )
            ],
            types=["electric"],
            traits=["Blitzschnell", "Flink"],
            rank="C"
        )
    
    @staticmethod
    def create_status_monster():
        """Monster mit vielen Status-Effekten."""
        return MonsterInstance(
            species_id="status_monster",
            name="Status-Monster",
            level=20,
            stats={
                "hp": 100, "mp": 120,
                "atk": 50, "def": 60,
                "mag": 100, "res": 70,
                "spd": 80
            },
            moves=[
                Move(
                    name="Gift-Pfeil",
                    power=40,
                    pp=20,
                    category=MoveCategory.MAGICAL,
                    target=MoveTarget.ENEMY,
                    type="poison",
                    effects=[MoveEffect(
                        kind=EffectKind.STATUS,
                        status="poison",
                        chance=80.0
                    )]
                ),
                Move(
                    name="Schlaf-Pulver",
                    power=0,
                    pp=15,
                    category=MoveCategory.SUPPORT,
                    target=MoveTarget.ENEMY,
                    type="normal",
                    effects=[MoveEffect(
                        kind=EffectKind.STATUS,
                        status="sleep",
                        chance=60.0
                    )]
                ),
                Move(
                    name="Verwirrung",
                    power=0,
                    pp=10,
                    category=MoveCategory.SUPPORT,
                    target=MoveTarget.ENEMY,
                    type="psychic",
                    effects=[MoveEffect(
                        kind=EffectKind.STATUS,
                        status="confusion",
                        chance=70.0
                    )]
                )
            ],
            types=["poison", "psychic"],
            traits=["Giftig", "Verwirrend"],
            rank="D"
        )
    
    @staticmethod
    def create_team_for_3v3():
        """Erstellt ein komplettes 3v3 Team."""
        return [
            TestMonsters.create_currywurst_phoenix(),
            TestMonsters.create_ruhrpott_ritter(),
            TestMonsters.create_tank_monster(),
            TestMonsters.create_speed_monster(),
            TestMonsters.create_status_monster(),
            TestMonsters.create_weak_monster()
        ]
    
    @staticmethod
    def create_balanced_team():
        """Erstellt ein ausgewogenes Team für Standard-Tests."""
        return [
            TestMonsters.create_currywurst_phoenix(),
            TestMonsters.create_ruhrpott_ritter(),
            TestMonsters.create_tank_monster()
        ]
    
    @staticmethod
    def create_monster_with_custom_stats(stats: Dict[str, int], **kwargs):
        """Erstellt ein Monster mit benutzerdefinierten Stats."""
        default_stats = {
            "hp": 100, "mp": 50,
            "atk": 50, "def": 50,
            "mag": 50, "res": 50,
            "spd": 50
        }
        
        # Überschreibe Standard-Stats
        for key, value in stats.items():
            if key in default_stats:
                default_stats[key] = value
        
        return MonsterInstance(
            species_id=kwargs.get("species_id", "custom_monster"),
            name=kwargs.get("name", "Custom Monster"),
            level=kwargs.get("level", 25),
            stats=default_stats,
            moves=kwargs.get("moves", []),
            types=kwargs.get("types", ["normal"]),
            traits=kwargs.get("traits", []),
            rank=kwargs.get("rank", "E")
        )
