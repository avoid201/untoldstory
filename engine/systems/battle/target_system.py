"""
🎯 DQM-Style Target System
Verwaltet Ziel-Auswahl für Single-, Multi- und Area-Targets
"""

from typing import List, Optional, Set, Dict, Callable
from enum import Enum, auto
from dataclasses import dataclass
import random
import logging

from .battle_formation import MonsterSlot, FormationPosition, BattleFormation

logger = logging.getLogger(__name__)

class TargetType(Enum):
    """Verschiedene Ziel-Typen für Skills und Angriffe"""
    SINGLE = "single"                # Ein einzelnes Ziel
    ALL_ENEMIES = "all_enemies"      # Alle Gegner
    ALL_ALLIES = "all_allies"        # Alle Verbündeten
    RANDOM_ENEMY = "random_enemy"    # Zufälliger Gegner
    RANDOM_ALLY = "random_ally"      # Zufälliger Verbündeter
    ROW_ENEMY = "row_enemy"          # Eine Gegner-Reihe
    ROW_ALLY = "row_ally"            # Eine Verbündeten-Reihe
    SELF = "self"                    # Nur sich selbst
    SPREAD = "spread"                # 2-4 zufällige Gegner
    PIERCE = "pierce"                # Durchbohrt Reihe (Front + Back gleiche Spalte)
    ADJACENT = "adjacent"            # Ziel + benachbarte Monster
    ALL = "all"                      # Alle auf dem Feld

class TargetScope(Enum):
    """Reichweite des Ziels"""
    MELEE = "melee"        # Nahkampf - nur Front Row
    RANGED = "ranged"      # Fernkampf - alle erreichbar
    SUPPORT = "support"    # Unterstützung - nur Verbündete
    FIELD = "field"        # Ganzes Feld

@dataclass
class TargetingRule:
    """Regel für Ziel-Validierung"""
    name: str
    condition: Callable[[MonsterSlot], bool]
    priority: int = 0
    
    def check(self, target: MonsterSlot) -> bool:
        """Prüft ob Ziel die Regel erfüllt"""
        return self.condition(target)

@dataclass
class TargetSelection:
    """Resultat einer Ziel-Auswahl"""
    primary_target: Optional[MonsterSlot] = None
    all_targets: List[MonsterSlot] = None
    target_type: TargetType = TargetType.SINGLE
    damage_modifiers: Dict[MonsterSlot, float] = None
    
    def __post_init__(self):
        if self.all_targets is None:
            self.all_targets = []
        if self.damage_modifiers is None:
            self.damage_modifiers = {}
    
    def get_damage_modifier(self, target: MonsterSlot) -> float:
        """Gibt Schadensmodifikator für ein Ziel zurück"""
        return self.damage_modifiers.get(target, 1.0)

class TargetingSystem:
    """
    Hauptsystem für Ziel-Auswahl in 3v3 Kämpfen
    Verwaltet alle Targeting-Logik und Validierung
    """
    
    def __init__(self, player_formation: BattleFormation, 
                 enemy_formation: BattleFormation):
        self.player_formation = player_formation
        self.enemy_formation = enemy_formation
        self.targeting_rules: List[TargetingRule] = []
        self._setup_default_rules()
        
        logger.info("TargetingSystem initialisiert")
    
    def _setup_default_rules(self):
        """Setzt Standard-Targeting-Regeln"""
        # Regel: Nur lebende Monster können Ziel sein
        self.add_rule(TargetingRule(
            name="alive_only",
            condition=lambda slot: slot.is_alive,
            priority=100
        ))
        
        # Regel: Nur angreifbare Monster
        self.add_rule(TargetingRule(
            name="targetable_only",
            condition=lambda slot: slot.is_targetable,
            priority=90
        ))
    
    def add_rule(self, rule: TargetingRule):
        """Fügt eine Targeting-Regel hinzu"""
        self.targeting_rules.append(rule)
        self.targeting_rules.sort(key=lambda r: r.priority, reverse=True)
    
    def get_valid_targets(self, attacker_team: str, 
                         target_type: TargetType,
                         scope: TargetScope = TargetScope.RANGED) -> TargetSelection:
        """
        Ermittelt gültige Ziele basierend auf Typ und Scope
        
        Args:
            attacker_team: Team des Angreifers ("player" oder "enemy")
            target_type: Art des Ziels
            scope: Reichweite des Angriffs
            
        Returns:
            TargetSelection mit allen gültigen Zielen
        """
        selection = TargetSelection(target_type=target_type)
        
        # Bestimme Ziel-Formation
        if attacker_team == "player":
            enemy_formation = self.enemy_formation
            ally_formation = self.player_formation
        else:
            enemy_formation = self.player_formation
            ally_formation = self.enemy_formation
        
        # Je nach Target-Type Ziele sammeln
        if target_type == TargetType.SINGLE:
            targets = self._get_single_targets(enemy_formation, scope)
            
        elif target_type == TargetType.ALL_ENEMIES:
            targets = self._get_all_enemies(enemy_formation)
            selection.damage_modifiers = self._calculate_area_modifiers(targets)
            
        elif target_type == TargetType.ALL_ALLIES:
            targets = self._get_all_allies(ally_formation)
            
        elif target_type == TargetType.RANDOM_ENEMY:
            targets = self._get_random_enemy(enemy_formation)
            
        elif target_type == TargetType.RANDOM_ALLY:
            targets = self._get_random_ally(ally_formation)
            
        elif target_type == TargetType.ROW_ENEMY:
            targets = self._get_row_targets(enemy_formation)
            selection.damage_modifiers = self._calculate_row_modifiers(targets)
            
        elif target_type == TargetType.SELF:
            # Angreifer selbst als Ziel
            targets = []  # Wird vom BattleController gesetzt
            
        elif target_type == TargetType.SPREAD:
            targets = self._get_spread_targets(enemy_formation)
            selection.damage_modifiers = self._calculate_spread_modifiers(targets)
            
        elif target_type == TargetType.PIERCE:
            targets = self._get_pierce_targets(enemy_formation)
            selection.damage_modifiers = self._calculate_pierce_modifiers(targets)
            
        elif target_type == TargetType.ADJACENT:
            # Benötigt primäres Ziel - wird später gesetzt
            targets = []
            
        elif target_type == TargetType.ALL:
            targets = self._get_all_targets(enemy_formation, ally_formation)
            selection.damage_modifiers = self._calculate_all_modifiers(targets)
            
        else:
            targets = []
            logger.warning(f"Unbekannter TargetType: {target_type}")
        
        # Regeln anwenden
        valid_targets = self._apply_rules(targets)
        selection.all_targets = valid_targets
        
        # Primäres Ziel setzen (erstes gültiges)
        if valid_targets:
            selection.primary_target = valid_targets[0]
        
        return selection
    
    def select_specific_target(self, selection: TargetSelection, 
                              chosen_target: MonsterSlot) -> TargetSelection:
        """
        Wählt ein spezifisches Ziel aus der Selection
        Wichtig für SINGLE und ADJACENT Typen
        """
        if selection.target_type == TargetType.SINGLE:
            selection.primary_target = chosen_target
            selection.all_targets = [chosen_target]
            
        elif selection.target_type == TargetType.ADJACENT:
            # Primäres Ziel + benachbarte
            selection.primary_target = chosen_target
            adjacent = self._get_adjacent_targets(chosen_target)
            selection.all_targets = [chosen_target] + adjacent
            selection.damage_modifiers = self._calculate_adjacent_modifiers(
                chosen_target, adjacent
            )
            
        return selection
    
    def _get_single_targets(self, formation: BattleFormation, 
                           scope: TargetScope) -> List[MonsterSlot]:
        """Ermittelt einzelne angreifbare Ziele"""
        if scope == TargetScope.MELEE:
            # Nur Front Row
            return [slot for slot in formation.get_active_monsters() 
                   if slot.position.is_front_row]
        else:
            # Alle aktiven Monster
            return formation.get_active_monsters()
    
    def _get_all_enemies(self, formation: BattleFormation) -> List[MonsterSlot]:
        """Alle aktiven Gegner"""
        return formation.get_active_monsters()
    
    def _get_all_allies(self, formation: BattleFormation) -> List[MonsterSlot]:
        """Alle aktiven Verbündeten"""
        return formation.get_active_monsters()
    
    def _get_random_enemy(self, formation: BattleFormation) -> List[MonsterSlot]:
        """Ein zufälliger Gegner"""
        active = formation.get_active_monsters()
        if active:
            return [random.choice(active)]
        return []
    
    def _get_random_ally(self, formation: BattleFormation) -> List[MonsterSlot]:
        """Ein zufälliger Verbündeter"""
        active = formation.get_active_monsters()
        if active:
            return [random.choice(active)]
        return []
    
    def _get_row_targets(self, formation: BattleFormation) -> List[MonsterSlot]:
        """Eine komplette Reihe (Front oder Back)"""
        active = formation.get_active_monsters()
        
        # Prüfe welche Reihe mehr Monster hat
        front_count = sum(1 for s in active if s.position.is_front_row)
        back_count = sum(1 for s in active if s.position.is_back_row)
        
        if front_count >= back_count:
            return [s for s in active if s.position.is_front_row]
        else:
            return [s for s in active if s.position.is_back_row]
    
    def _get_spread_targets(self, formation: BattleFormation) -> List[MonsterSlot]:
        """2-4 zufällige Gegner"""
        active = formation.get_active_monsters()
        if not active:
            return []
            
        # Anzahl: 2-4 oder alle wenn weniger
        num_targets = min(len(active), random.randint(2, 4))
        return random.sample(active, num_targets)
    
    def _get_pierce_targets(self, formation: BattleFormation) -> List[MonsterSlot]:
        """Durchbohrt eine Spalte (Front + Back)"""
        active = formation.get_active_monsters()
        if not active:
            return []
        
        # Wähle zufällige Spalte mit mindestens einem Monster
        columns_with_monsters = {}
        for slot in active:
            col = slot.position.column
            if col not in columns_with_monsters:
                columns_with_monsters[col] = []
            columns_with_monsters[col].append(slot)
        
        if columns_with_monsters:
            chosen_column = random.choice(list(columns_with_monsters.keys()))
            return columns_with_monsters[chosen_column]
        
        return []
    
    def _get_adjacent_targets(self, primary: MonsterSlot) -> List[MonsterSlot]:
        """Findet benachbarte Monster zum primären Ziel"""
        adjacent = []
        primary_pos = primary.position
        
        # Bestimme Formation des primären Ziels
        if primary in self.player_formation.get_active_monsters():
            formation = self.player_formation
        else:
            formation = self.enemy_formation
        
        # Prüfe links/rechts in gleicher Reihe
        for slot in formation.get_active_monsters():
            if slot == primary:
                continue
                
            slot_pos = slot.position
            # Gleiche Reihe und benachbarte Spalte
            if (slot_pos.row == primary_pos.row and 
                abs(slot_pos.column - primary_pos.column) == 1):
                adjacent.append(slot)
        
        return adjacent
    
    def _get_all_targets(self, enemy_formation: BattleFormation,
                        ally_formation: BattleFormation) -> List[MonsterSlot]:
        """Alle Monster auf dem Feld"""
        return (enemy_formation.get_active_monsters() + 
                ally_formation.get_active_monsters())
    
    def _apply_rules(self, targets: List[MonsterSlot]) -> List[MonsterSlot]:
        """Wendet alle Targeting-Regeln auf die Ziele an"""
        valid_targets = []
        
        for target in targets:
            valid = True
            for rule in self.targeting_rules:
                if not rule.check(target):
                    valid = False
                    logger.debug(f"Target {target.monster.name if not target.is_empty else 'Empty'} "
                               f"failed rule: {rule.name}")
                    break
            
            if valid:
                valid_targets.append(target)
        
        return valid_targets
    
    def _calculate_area_modifiers(self, targets: List[MonsterSlot]) -> Dict[MonsterSlot, float]:
        """
        Berechnet Schadensmodifikatoren für Area-Attacks
        Weniger Schaden bei mehr Zielen
        """
        modifiers = {}
        num_targets = len(targets)
        
        if num_targets <= 2:
            # Voller Schaden bei 1-2 Zielen
            for target in targets:
                modifiers[target] = 1.0
        elif num_targets <= 4:
            # 85% Schaden bei 3-4 Zielen
            for target in targets:
                modifiers[target] = 0.85
        else:
            # 70% Schaden bei 5+ Zielen
            for target in targets:
                modifiers[target] = 0.70
        
        return modifiers
    
    def _calculate_row_modifiers(self, targets: List[MonsterSlot]) -> Dict[MonsterSlot, float]:
        """Schadensmodifikatoren für Row-Attacks"""
        modifiers = {}
        
        # Mittleres Monster erhält vollen Schaden
        # Seiten-Monster erhalten 80%
        for target in targets:
            if target.position.column == 1:  # Mitte
                modifiers[target] = 1.0
            else:  # Seiten
                modifiers[target] = 0.8
        
        return modifiers
    
    def _calculate_spread_modifiers(self, targets: List[MonsterSlot]) -> Dict[MonsterSlot, float]:
        """Schadensmodifikatoren für Spread-Attacks"""
        modifiers = {}
        
        # Zufällige Variation im Schaden
        for target in targets:
            modifiers[target] = random.uniform(0.7, 1.0)
        
        return modifiers
    
    def _calculate_pierce_modifiers(self, targets: List[MonsterSlot]) -> Dict[MonsterSlot, float]:
        """Schadensmodifikatoren für Pierce-Attacks"""
        modifiers = {}
        
        # Front Row erhält vollen Schaden, Back Row 75%
        for target in targets:
            if target.position.is_front_row:
                modifiers[target] = 1.0
            else:
                modifiers[target] = 0.75
        
        return modifiers
    
    def _calculate_adjacent_modifiers(self, primary: MonsterSlot, 
                                     adjacent: List[MonsterSlot]) -> Dict[MonsterSlot, float]:
        """Schadensmodifikatoren für Adjacent-Attacks"""
        modifiers = {primary: 1.0}  # Hauptziel voller Schaden
        
        # Benachbarte erhalten 60% Schaden
        for target in adjacent:
            modifiers[target] = 0.6
        
        return modifiers
    
    def _calculate_all_modifiers(self, targets: List[MonsterSlot]) -> Dict[MonsterSlot, float]:
        """Schadensmodifikatoren für All-Target-Attacks"""
        modifiers = {}
        
        # Jeder erhält reduzierten Schaden basierend auf Gesamtzahl
        base_modifier = max(0.5, 1.0 - (len(targets) * 0.1))
        
        for target in targets:
            modifiers[target] = base_modifier
        
        return modifiers
    
    def get_auto_target(self, attacker_team: str, 
                       target_type: TargetType) -> Optional[MonsterSlot]:
        """
        Wählt automatisch ein Ziel (für KI oder Auto-Battle)
        Verwendet intelligente Heuristiken
        """
        selection = self.get_valid_targets(attacker_team, target_type)
        
        if not selection.all_targets:
            return None
        
        if target_type == TargetType.SINGLE:
            # Priorisiere Monster mit wenig HP
            weakest = min(selection.all_targets, 
                         key=lambda s: s.hp_percentage)
            
            # Aber bevorzuge Front Row
            front_row = [s for s in selection.all_targets 
                        if s.position.is_front_row]
            
            if front_row:
                front_weakest = min(front_row, key=lambda s: s.hp_percentage)
                # Greife Front Row an wenn Unterschied nicht zu groß
                if front_weakest.hp_percentage <= weakest.hp_percentage * 1.5:
                    return front_weakest
            
            return weakest
        
        return selection.primary_target
    
    def validate_target(self, attacker: MonsterSlot, 
                       target: MonsterSlot,
                       skill_range: TargetScope) -> bool:
        """
        Validiert ob ein Ziel gültig ist
        
        Args:
            attacker: Angreifendes Monster
            target: Ziel-Monster
            skill_range: Reichweite des Skills
            
        Returns:
            True wenn Ziel gültig
        """
        # Prüfe ob Ziel lebt
        if not target.is_alive:
            return False
        
        # Prüfe ob Ziel angreifbar
        if not target.is_targetable:
            return False
        
        # Prüfe Reichweite bei Melee
        if skill_range == TargetScope.MELEE:
            # Attacker muss in Front Row sein
            if not attacker.position.is_front_row:
                return False
            
            # Target muss in gegnerischer Front Row sein
            if not target.position.is_front_row:
                return False
        
        # Alle Regeln prüfen
        for rule in self.targeting_rules:
            if not rule.check(target):
                return False
        
        return True
    
    def get_target_description(self, target_type: TargetType) -> str:
        """Gibt eine Beschreibung des Target-Typs zurück"""
        descriptions = {
            TargetType.SINGLE: "Einzelnes Ziel",
            TargetType.ALL_ENEMIES: "Alle Gegner",
            TargetType.ALL_ALLIES: "Alle Verbündeten", 
            TargetType.RANDOM_ENEMY: "Zufälliger Gegner",
            TargetType.RANDOM_ALLY: "Zufälliger Verbündeter",
            TargetType.ROW_ENEMY: "Gegnerische Reihe",
            TargetType.ROW_ALLY: "Verbündete Reihe",
            TargetType.SELF: "Selbst",
            TargetType.SPREAD: "2-4 zufällige Gegner",
            TargetType.PIERCE: "Durchbohrt Spalte",
            TargetType.ADJACENT: "Ziel + Benachbarte",
            TargetType.ALL: "Gesamtes Kampffeld"
        }
        return descriptions.get(target_type, "Unbekannt")


# Test-Code
if __name__ == "__main__":
    from .battle_formation import BattleFormation, FormationType
    
    logging.basicConfig(level=logging.DEBUG)
    
    # Dummy Monster für Tests
    class TestMonster:
        def __init__(self, name: str, hp: int = 100):
            self.name = name
            self.current_hp = hp
            self.max_hp = hp
            self.stats = {"agility": 50}
    
    # Formationen erstellen
    player_form = BattleFormation("player")
    enemy_form = BattleFormation("enemy")
    
    # Monster hinzufügen
    for i in range(3):
        player_form.add_monster(TestMonster(f"Hero_{i+1}"))
        enemy_form.add_monster(TestMonster(f"Enemy_{i+1}"))
    
    # Targeting System
    targeting = TargetingSystem(player_form, enemy_form)
    
    # Teste verschiedene Target-Typen
    print("\n=== TARGETING TESTS ===\n")
    
    for target_type in TargetType:
        selection = targeting.get_valid_targets("player", target_type)
        print(f"{target_type.value}: {len(selection.all_targets)} Ziele")
        if selection.all_targets:
            for target in selection.all_targets:
                modifier = selection.get_damage_modifier(target)
                print(f"  - {target.monster.name} (Modifier: {modifier:.0%})")
    
    # Auto-Target Test
    print("\n=== AUTO-TARGET TEST ===")
    auto_target = targeting.get_auto_target("player", TargetType.SINGLE)
    if auto_target:
        print(f"Auto-gewähltes Ziel: {auto_target.monster.name}")
