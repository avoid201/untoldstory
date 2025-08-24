"""
🎮 DQM-Style Battle Formation System
Verwaltet 3v3 Monster-Formationen und Positionen im Kampf
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum, auto
import logging

logger = logging.getLogger(__name__)

class FormationPosition(Enum):
    """Position eines Monsters in der Formation"""
    FRONT_LEFT = (0, 0)
    FRONT_CENTER = (0, 1)
    FRONT_RIGHT = (0, 2)
    BACK_LEFT = (1, 0)
    BACK_CENTER = (1, 1)
    BACK_RIGHT = (1, 2)
    
    @property
    def row(self) -> int:
        return self.value[0]
    
    @property
    def column(self) -> int:
        return self.value[1]
    
    @property
    def is_front_row(self) -> bool:
        return self.row == 0
    
    @property
    def is_back_row(self) -> bool:
        return self.row == 1

class FormationType(Enum):
    """Vordefinierte Formations-Typen"""
    STANDARD = "standard"      # 3 vorne, 3 hinten
    OFFENSIVE = "offensive"     # Alle vorne
    DEFENSIVE = "defensive"     # 2 vorne, 4 hinten
    WEDGE = "wedge"            # V-Formation
    SPREAD = "spread"          # Weit verteilt

@dataclass
class MonsterSlot:
    """Ein Slot in der Formation"""
    position: FormationPosition
    monster: Optional[object] = None  # Monster-Instanz
    is_active: bool = True
    is_targetable: bool = True
    hp_percentage: float = 1.0
    
    @property
    def is_empty(self) -> bool:
        return self.monster is None
    
    @property
    def is_alive(self) -> bool:
        if self.is_empty:
            return False
        return self.monster.current_hp > 0
    
    def can_act(self) -> bool:
        """Prüft ob Monster handeln kann"""
        return self.is_alive and self.is_active and not self.is_empty

@dataclass
class BattleFormation:
    """
    Verwaltet die Formation eines Teams im Kampf
    Unterstützt bis zu 6 Monster (3 aktiv, 3 Bank)
    """
    team_id: str
    slots: Dict[FormationPosition, MonsterSlot] = field(default_factory=dict)
    formation_type: FormationType = FormationType.STANDARD
    max_active: int = 3
    max_bench: int = 3
    
    def __post_init__(self):
        """Initialisiere alle Positions-Slots"""
        if not self.slots:
            for position in FormationPosition:
                self.slots[position] = MonsterSlot(position=position)
                
        logger.info(f"Formation für Team {self.team_id} initialisiert")
    
    def add_monster(self, monster: object, position: Optional[FormationPosition] = None) -> bool:
        """
        Fügt ein Monster zur Formation hinzu
        
        Args:
            monster: Das Monster-Objekt
            position: Gewünschte Position (optional)
            
        Returns:
            True wenn erfolgreich platziert
        """
        # Wenn keine Position angegeben, finde erste freie
        if position is None:
            position = self._find_empty_slot()
            if position is None:
                logger.warning(f"Keine freie Position für Monster {monster.name}")
                return False
        
        # Prüfe ob Position frei ist
        if not self.slots[position].is_empty:
            logger.warning(f"Position {position} ist bereits belegt")
            return False
        
        # Platziere Monster
        self.slots[position].monster = monster
        self.slots[position].hp_percentage = monster.current_hp / monster.max_hp
        
        logger.info(f"Monster {monster.name} auf Position {position.name} platziert")
        return True
    
    def remove_monster(self, position: FormationPosition) -> Optional[object]:
        """Entfernt ein Monster von einer Position"""
        slot = self.slots[position]
        if slot.is_empty:
            return None
            
        monster = slot.monster
        slot.monster = None
        slot.hp_percentage = 1.0
        
        logger.info(f"Monster {monster.name} von Position {position.name} entfernt")
        return monster
    
    def switch_positions(self, pos1: FormationPosition, pos2: FormationPosition) -> bool:
        """Tauscht zwei Monster-Positionen"""
        # Beide Slots holen
        slot1 = self.slots[pos1]
        slot2 = self.slots[pos2]
        
        # Monster tauschen
        slot1.monster, slot2.monster = slot2.monster, slot1.monster
        slot1.hp_percentage, slot2.hp_percentage = slot2.hp_percentage, slot1.hp_percentage
        
        logger.info(f"Positionen {pos1.name} und {pos2.name} getauscht")
        return True
    
    def get_active_monsters(self) -> List[MonsterSlot]:
        """
        Gibt alle aktiven (lebenden) Monster zurück
        Maximal 3 gleichzeitig aktiv
        """
        active = []
        front_row = self._get_front_row()
        
        # Erst Front-Row prüfen
        for slot in front_row:
            if slot.can_act() and len(active) < self.max_active:
                active.append(slot)
        
        # Wenn Front-Row nicht voll, Back-Row nachrücken
        if len(active) < self.max_active:
            back_row = self._get_back_row()
            for slot in back_row:
                if slot.can_act() and len(active) < self.max_active:
                    active.append(slot)
                    
        return active
    
    def get_bench_monsters(self) -> List[MonsterSlot]:
        """Gibt alle Bank-Monster zurück (nicht aktiv aber lebendig)"""
        active_positions = {slot.position for slot in self.get_active_monsters()}
        bench = []
        
        for position, slot in self.slots.items():
            if position not in active_positions and slot.is_alive:
                bench.append(slot)
                
        return bench[:self.max_bench]
    
    def get_all_alive(self) -> List[MonsterSlot]:
        """Gibt alle lebenden Monster zurück"""
        return [slot for slot in self.slots.values() if slot.is_alive]
    
    def get_targetable_monsters(self, target_row: Optional[int] = None) -> List[MonsterSlot]:
        """
        Gibt alle angreifbaren Monster zurück
        
        Args:
            target_row: Optional - nur Monster aus dieser Reihe
        """
        targetable = []
        
        for slot in self.get_active_monsters():
            if not slot.is_targetable:
                continue
                
            if target_row is not None and slot.position.row != target_row:
                continue
                
            targetable.append(slot)
            
        return targetable
    
    def apply_formation(self, formation_type: FormationType):
        """
        Wendet eine vordefinierte Formation an
        Reorganisiert Monster-Positionen
        """
        self.formation_type = formation_type
        alive_monsters = [slot.monster for slot in self.get_all_alive()]
        
        # Alle Slots leeren
        for slot in self.slots.values():
            slot.monster = None
        
        # Monster nach Formation neu platzieren
        positions = self._get_formation_positions(formation_type)
        
        for monster, position in zip(alive_monsters, positions):
            self.add_monster(monster, position)
            
        logger.info(f"Formation {formation_type.value} angewendet")
    
    def update_slot_states(self):
        """Aktualisiert HP-Prozente und Status aller Slots"""
        for slot in self.slots.values():
            if not slot.is_empty:
                slot.hp_percentage = slot.monster.current_hp / slot.monster.max_hp
                slot.is_active = slot.monster.current_hp > 0
    
    def get_formation_bonus(self) -> Dict[str, float]:
        """
        Berechnet Formations-Boni basierend auf Typ
        
        Returns:
            Dict mit Multiplikatoren für verschiedene Stats
        """
        bonuses = {
            "atk": 1.0,
            "def": 1.0,
            "spd": 1.0,
            "accuracy": 1.0
        }
        
        if self.formation_type == FormationType.OFFENSIVE:
            bonuses["atk"] = 1.15  # +15% Angriff
            bonuses["def"] = 0.9   # -10% Verteidigung
            
        elif self.formation_type == FormationType.DEFENSIVE:
            bonuses["def"] = 1.2   # +20% Verteidigung
            bonuses["atk"] = 0.95  # -5% Angriff
            
        elif self.formation_type == FormationType.WEDGE:
            bonuses["spd"] = 1.1   # +10% Speed
            bonuses["accuracy"] = 1.1  # +10% Genauigkeit
            
        elif self.formation_type == FormationType.SPREAD:
            bonuses["def"] = 1.1   # +10% Verteidigung gegen Area-Attacks
            
        return bonuses
    
    def _find_empty_slot(self) -> Optional[FormationPosition]:
        """Findet erste freie Position (Front-Row bevorzugt)"""
        # Erst Front-Row
        for position in [FormationPosition.FRONT_LEFT, 
                        FormationPosition.FRONT_CENTER,
                        FormationPosition.FRONT_RIGHT]:
            if self.slots[position].is_empty:
                return position
        
        # Dann Back-Row
        for position in [FormationPosition.BACK_LEFT,
                        FormationPosition.BACK_CENTER, 
                        FormationPosition.BACK_RIGHT]:
            if self.slots[position].is_empty:
                return position
                
        return None
    
    def _get_front_row(self) -> List[MonsterSlot]:
        """Gibt alle Front-Row Slots zurück"""
        return [self.slots[pos] for pos in FormationPosition 
                if pos.is_front_row]
    
    def _get_back_row(self) -> List[MonsterSlot]:
        """Gibt alle Back-Row Slots zurück"""
        return [self.slots[pos] for pos in FormationPosition 
                if pos.is_back_row]
    
    def _get_formation_positions(self, formation_type: FormationType) -> List[FormationPosition]:
        """Gibt die Positions-Reihenfolge für eine Formation zurück"""
        if formation_type == FormationType.OFFENSIVE:
            # Alle vorne
            return [
                FormationPosition.FRONT_LEFT,
                FormationPosition.FRONT_CENTER,
                FormationPosition.FRONT_RIGHT,
                FormationPosition.BACK_LEFT,
                FormationPosition.BACK_CENTER,
                FormationPosition.BACK_RIGHT
            ]
            
        elif formation_type == FormationType.DEFENSIVE:
            # 2 vorne, 4 hinten
            return [
                FormationPosition.FRONT_LEFT,
                FormationPosition.FRONT_RIGHT,
                FormationPosition.BACK_LEFT,
                FormationPosition.BACK_CENTER,
                FormationPosition.BACK_RIGHT,
                FormationPosition.FRONT_CENTER
            ]
            
        elif formation_type == FormationType.WEDGE:
            # V-Formation
            return [
                FormationPosition.FRONT_CENTER,
                FormationPosition.FRONT_LEFT,
                FormationPosition.FRONT_RIGHT,
                FormationPosition.BACK_LEFT,
                FormationPosition.BACK_RIGHT,
                FormationPosition.BACK_CENTER
            ]
            
        elif formation_type == FormationType.SPREAD:
            # Weit verteilt
            return [
                FormationPosition.FRONT_LEFT,
                FormationPosition.BACK_RIGHT,
                FormationPosition.FRONT_RIGHT,
                FormationPosition.BACK_LEFT,
                FormationPosition.FRONT_CENTER,
                FormationPosition.BACK_CENTER
            ]
            
        else:  # STANDARD
            return [
                FormationPosition.FRONT_LEFT,
                FormationPosition.FRONT_CENTER,
                FormationPosition.FRONT_RIGHT,
                FormationPosition.BACK_LEFT,
                FormationPosition.BACK_CENTER,
                FormationPosition.BACK_RIGHT
            ]
    
    def get_position_display(self) -> str:
        """Gibt eine visuelle Darstellung der Formation zurück"""
        display = f"\n=== {self.team_id} Formation ({self.formation_type.value}) ===\n"
        display += "BACK ROW:  "
        
        # Back Row
        for pos in [FormationPosition.BACK_LEFT, 
                   FormationPosition.BACK_CENTER,
                   FormationPosition.BACK_RIGHT]:
            slot = self.slots[pos]
            if slot.is_empty:
                display += "[   LEER   ] "
            else:
                hp_bar = "█" * int(slot.hp_percentage * 10)
                hp_bar += "░" * (10 - len(hp_bar))
                name = slot.monster.name[:10].center(10)
                display += f"[{name}] "
        
        display += "\nFRONT ROW: "
        
        # Front Row
        for pos in [FormationPosition.FRONT_LEFT,
                   FormationPosition.FRONT_CENTER,
                   FormationPosition.FRONT_RIGHT]:
            slot = self.slots[pos]
            if slot.is_empty:
                display += "[   LEER   ] "
            else:
                name = slot.monster.name[:10].center(10)
                display += f"[{name}] "
                
        display += "\n"
        return display


class FormationManager:
    """
    Verwaltet Formationen für beide Teams im Kampf
    Koordiniert 3v3 Kämpfe
    """
    
    def __init__(self):
        self.formations: Dict[str, BattleFormation] = {}
        logger.info("FormationManager initialisiert")
    
    def create_formation(self, team_id: str, monsters: List[object],
                        formation_type: FormationType = FormationType.STANDARD) -> BattleFormation:
        """
        Erstellt eine neue Formation für ein Team
        
        Args:
            team_id: ID des Teams (player/opponent)
            monsters: Liste der Monster
            formation_type: Gewünschter Formations-Typ
        """
        formation = BattleFormation(team_id=team_id, formation_type=formation_type)
        
        # Monster hinzufügen
        for monster in monsters[:6]:  # Maximal 6 Monster
            formation.add_monster(monster)
        
        self.formations[team_id] = formation
        logger.info(f"Formation für {team_id} mit {len(monsters)} Monstern erstellt")
        
        return formation
    
    def get_all_active_monsters(self) -> List[Tuple[str, MonsterSlot]]:
        """
        Gibt alle aktiven Monster beider Teams zurück
        Format: [(team_id, MonsterSlot), ...]
        """
        all_active = []
        
        for team_id, formation in self.formations.items():
            for slot in formation.get_active_monsters():
                all_active.append((team_id, slot))
                
        return all_active
    
    def get_turn_order(self) -> List[Tuple[str, MonsterSlot]]:
        """
        Berechnet die Zugreihenfolge basierend auf Speed
        Verwendet DQM-Formel: Agility + Random(0-255)
        """
        active_monsters = self.get_all_active_monsters()
        
        # Sortiere nach Speed + Random
        import random
        def get_speed_value(entry):
            team_id, slot = entry
            base_speed = slot.monster.stats.get('agility', 50)
            return base_speed + random.randint(0, 255)
        
        sorted_monsters = sorted(active_monsters, key=get_speed_value, reverse=True)
        
        logger.debug(f"Turn Order berechnet: {len(sorted_monsters)} Monster")
        return sorted_monsters
    
    def apply_area_damage_reduction(self, damage: int, 
                                   main_target: MonsterSlot,
                                   side_target: MonsterSlot) -> int:
        """
        Reduziert Schaden für Seiten-Ziele bei Area-Attacks
        DQM-Style: Seiten-Ziele erhalten 75% des Schadens
        """
        if main_target.position.column == side_target.position.column:
            return damage  # Volles Schaden für Hauptziel
        else:
            return int(damage * 0.75)  # 75% für Seiten-Ziele
    
    def check_victory_conditions(self) -> Optional[str]:
        """
        Prüft ob ein Team gewonnen hat
        
        Returns:
            Team-ID des Gewinners oder None
        """
        for team_id, formation in self.formations.items():
            if not formation.get_all_alive():
                # Dieses Team hat keine lebenden Monster mehr
                # Das andere Team gewinnt
                winner = [tid for tid in self.formations.keys() if tid != team_id][0]
                logger.info(f"Team {winner} hat gewonnen!")
                return winner
                
        return None
    
    def display_all_formations(self) -> str:
        """Zeigt alle Formationen visuell an"""
        display = "\n" + "="*60 + "\n"
        display += "🎮 KAMPF-FORMATION 🎮\n"
        display += "="*60
        
        for team_id, formation in self.formations.items():
            display += formation.get_position_display()
            
        display += "="*60 + "\n"
        return display


# Beispiel-Nutzung für Tests
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    
    # Dummy Monster-Klasse für Tests
    class TestMonster:
        def __init__(self, name: str, hp: int = 100):
            self.name = name
            self.current_hp = hp
            self.max_hp = hp
            self.stats = {"agility": 50}
    
    # Test Formation Manager
    manager = FormationManager()
    
    # Spieler-Team
    player_monsters = [
        TestMonster("Slime"),
        TestMonster("Drache"),
        TestMonster("Golem"),
        TestMonster("Fairy"),
        TestMonster("Demon"),
        TestMonster("Bird")
    ]
    
    # Gegner-Team
    enemy_monsters = [
        TestMonster("Orc"),
        TestMonster("Goblin"),
        TestMonster("Troll")
    ]
    
    # Formationen erstellen
    player_formation = manager.create_formation("Player", player_monsters, FormationType.OFFENSIVE)
    enemy_formation = manager.create_formation("Enemy", enemy_monsters, FormationType.DEFENSIVE)
    
    # Anzeigen
    print(manager.display_all_formations())
    
    # Turn Order
    print("\nTurn Order:")
    for team_id, slot in manager.get_turn_order():
        print(f"  {team_id}: {slot.monster.name} (Position: {slot.position.name})")
