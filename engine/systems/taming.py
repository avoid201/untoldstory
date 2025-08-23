"""
Taming system for Untold Story.
Handles the capture/recruitment of wild monsters with DQM-style mechanics.
"""

import random
from typing import Optional, List, Tuple, Dict, Any, TYPE_CHECKING
from dataclasses import dataclass
from enum import Enum

from engine.systems.monster_instance import MonsterInstance

if TYPE_CHECKING:
    from engine.systems.monsters import MonsterSpecies


class TameResult(Enum):
    """Possible outcomes of a taming attempt."""
    SUCCESS = "success"
    FAILED = "failed"
    IRRITATED = "irritated"  # Monster already failed this battle
    INVALID = "invalid"  # Cannot tame (trainer battle, boss, etc.)


@dataclass
class TameModifier:
    """Modifier affecting tame chance."""
    name: str
    value: float
    description: str


def calculate_tame_chance(
    target: MonsterInstance,
    player_team: List[MonsterInstance],
    battle_state: any,
    item_used: Optional[str] = None
) -> float:
    """
    Calculate the chance to successfully tame a monster.
    
    DQM-style formula considering:
    - Target's current HP percentage (lower = better)
    - Target's rank (higher rank = harder)
    - Player team's offensive pressure
    - Status conditions on target
    - Special items used
    - Target's capture rate
    
    Returns a value between 0.0 and 1.0
    """
    
    # Base chance from capture rate
    base_chance = target.capture_rate / 255.0 if hasattr(target, 'capture_rate') else 0.15
    
    # HP factor (lower HP = higher chance)
    hp_factor = 1.0 - (target.current_hp / target.max_hp)
    hp_bonus = hp_factor * 0.4  # Max 40% bonus at 1 HP
    
    # Rank difficulty multiplier
    rank_multipliers = {
        'F': 1.2,   # Easier
        'E': 1.0,
        'D': 0.9,
        'C': 0.8,
        'B': 0.7,
        'A': 0.5,
        'S': 0.3,
        'SS': 0.2,
        'X': 0.1    # Very hard
    }
    rank_mult = rank_multipliers.get(target.rank, 0.5)
    
    # Status condition bonuses
    status_bonus = 0
    if target.status == 'sleep':
        status_bonus = 0.25  # 25% bonus
    elif target.status == 'paralysis':
        status_bonus = 0.15  # 15% bonus
    elif target.status == 'freeze':
        status_bonus = 0.20  # 20% bonus
    elif target.status in ['poison', 'burn']:
        status_bonus = 0.10  # 10% bonus
    elif target.status == 'confused':
        status_bonus = 0.05  # 5% bonus
    
    # Offensive pressure (team strength vs target defense)
    pressure_bonus = calculate_offensive_pressure(player_team, target)
    
    # Item bonuses
    item_bonus = 0
    if item_used:
        item_bonuses = {
            'meat': 0.10,           # Basic taming item
            'premium_meat': 0.20,   # Better taming item
            'golden_meat': 0.30,    # Best taming item
            'type_bait': 0.15,      # Type-specific bait
        }
        item_bonus = item_bonuses.get(item_used, 0)
    
    # Check for irritation (failed attempt this battle)
    irritation_penalty = 0
    if hasattr(target, 'buffs'):
        for buff in target.buffs:
            if buff.get('type') == 'irritated':
                irritation_penalty = 0.5  # 50% harder when irritated
    
    # Calculate final chance
    final_chance = (base_chance + hp_bonus + status_bonus + pressure_bonus + item_bonus) * rank_mult
    final_chance *= (1 - irritation_penalty)
    
    # Clamp between 0 and 95% (always a chance to fail)
    return max(0.0, min(0.95, final_chance))


def calculate_offensive_pressure(player_team: List[MonsterInstance], target: MonsterInstance) -> float:
    """
    Calculate how much offensive pressure the player team has on the target.
    Higher pressure = easier to tame.
    
    Returns a bonus between 0.0 and 0.2
    """
    if not player_team:
        return 0.0
    
    # Get active (non-fainted) team members
    active_team = [m for m in player_team if m and m.current_hp > 0]
    if not active_team:
        return 0.0
    
    # Calculate average offensive stats vs target's defenses
    avg_attack = sum(m.stats['atk'] for m in active_team) / len(active_team)
    avg_magic = sum(m.stats['mag'] for m in active_team) / len(active_team)
    
    # Compare to target's defenses
    phys_advantage = (avg_attack - target.stats['def']) / 100.0
    mag_advantage = (avg_magic - target.stats['res']) / 100.0
    
    # Best advantage counts
    pressure = max(phys_advantage, mag_advantage)
    
    # Convert to bonus (max 20%)
    return max(0.0, min(0.2, pressure * 0.1))


def attempt_tame(
    target: MonsterInstance,
    player_team: List[MonsterInstance], 
    battle_state: any,
    item_used: Optional[str] = None,
    show_chance: bool = True
) -> Tuple[TameResult, float, Optional[str]]:
    """
    Attempt to tame a wild monster.
    
    Returns:
        - Result enum
        - Calculated chance (for display)
        - Optional message
    """
    
    # Check if taming is valid
    if not battle_state.is_wild:
        return TameResult.INVALID, 0.0, "Dat geht nur bei wilden Monstern!"
    
    # Check for boss/legendary flags
    if hasattr(target, 'is_boss') and target.is_boss:
        return TameResult.INVALID, 0.0, "Bosse kann man nich zähmen, Kollege!"
    
    # Check if already irritated
    if hasattr(target, 'buffs'):
        for buff in target.buffs:
            if buff.get('type') == 'irritated':
                return TameResult.IRRITATED, 0.0, "Das Monster is schon genervt! Geht nich mehr!"
    
    # Calculate chance
    chance = calculate_tame_chance(target, player_team, battle_state, item_used)
    
    # Roll for success
    roll = random.random()
    
    if roll < chance:
        # Success!
        return TameResult.SUCCESS, chance, f"{target.species_name} lässt sich zähmen!"
    else:
        # Failed - apply irritation
        if not hasattr(target, 'buffs'):
            target.buffs = []
        
        target.buffs.append({
            'type': 'irritated',
            'duration': -1,  # Lasts whole battle
            'attacker_penalty': 0.1,  # -10% attack when irritated
            'defender_penalty': -0.1   # +10% defense when irritated (harder to damage)
        })
        
        # Flavor messages based on how close it was
        if roll < chance + 0.1:
            message = "Fast geschafft! Das Monster is aber noch nich überzeugt..."
        elif roll < chance + 0.25:
            message = "Das Monster überlegt... aber nee, doch nich!"
        else:
            message = "Das Monster hat gar kein Bock auf dich!"
        
        return TameResult.FAILED, chance, message


def get_tame_modifiers(
    target: MonsterInstance,
    player_team: List[MonsterInstance],
    battle_state: any,
    item_used: Optional[str] = None
) -> List[TameModifier]:
    """
    Get a breakdown of all modifiers affecting tame chance.
    Useful for UI display.
    """
    modifiers = []
    
    # Base capture rate
    base_rate = target.capture_rate / 255.0 if hasattr(target, 'capture_rate') else 0.15
    modifiers.append(TameModifier(
        "Basis-Fangrate",
        base_rate,
        f"Spezies-Grundwert: {int(base_rate * 100)}%"
    ))
    
    # HP factor
    hp_percent = target.current_hp / target.max_hp
    hp_factor = 1.0 - hp_percent
    hp_bonus = hp_factor * 0.4
    if hp_bonus > 0:
        modifiers.append(TameModifier(
            "Schwäche-Bonus",
            hp_bonus,
            f"Monster hat nur {int(hp_percent * 100)}% HP"
        ))
    
    # Rank penalty
    rank_multipliers = {
        'F': 1.2, 'E': 1.0, 'D': 0.9, 'C': 0.8,
        'B': 0.7, 'A': 0.5, 'S': 0.3, 'SS': 0.2, 'X': 0.1
    }
    rank_mult = rank_multipliers.get(target.rank, 0.5)
    if rank_mult != 1.0:
        modifiers.append(TameModifier(
            f"Rang {target.rank}",
            rank_mult - 1.0,  # Show as modifier
            "Höherer Rang = schwerer zu zähmen"
        ))
    
    # Status bonus
    status_bonuses = {
        'sleep': ('Schlaf', 0.25, "Schlafende Monster sind leichter zu fangen"),
        'paralysis': ('Paralyse', 0.15, "Paralysierte Monster können sich nich wehren"),
        'freeze': ('Eingefroren', 0.20, "Eingefrorene Monster sind hilflos"),
        'poison': ('Vergiftet', 0.10, "Gift schwächt den Widerstand"),
        'burn': ('Verbrennung', 0.10, "Verbrennungen lenken ab"),
        'confused': ('Verwirrt', 0.05, "Verwirrung macht kooperativer")
    }
    
    if target.status in status_bonuses:
        name, bonus, desc = status_bonuses[target.status]
        modifiers.append(TameModifier(name, bonus, desc))
    
    # Offensive pressure
    pressure = calculate_offensive_pressure(player_team, target)
    if pressure > 0:
        modifiers.append(TameModifier(
            "Team-Druck",
            pressure,
            "Dein Team macht ordentlich Druck!"
        ))
    
    # Item bonus
    if item_used:
        item_effects = {
            'meat': ('Fleisch', 0.10, "Leckeres Fleisch macht Monster zahm"),
            'premium_meat': ('Premium-Fleisch', 0.20, "Bestes Fleisch für anspruchsvolle Monster"),
            'golden_meat': ('Goldenes Fleisch', 0.30, "Legendäres Fleisch! Unwiderstehlich!"),
            'type_bait': ('Typ-Köder', 0.15, "Speziell für diesen Monster-Typ")
        }
        
        if item_used in item_effects:
            name, bonus, desc = item_effects[item_used]
            modifiers.append(TameModifier(name, bonus, desc))
    
    # Irritation penalty
    if hasattr(target, 'buffs'):
        for buff in target.buffs:
            if buff.get('type') == 'irritated':
                modifiers.append(TameModifier(
                    "Genervt",
                    -0.5,
                    "Fehlversuch! Monster is jetzt sauer!"
                ))
                break
    
    return modifiers


def calculate_display_chance(modifiers: List[TameModifier]) -> Tuple[float, str]:
    """
    Calculate final chance from modifiers and create display string.
    
    Returns:
        - Final chance (0.0 to 1.0)
        - Formatted display string
    """
    base = 0
    multiplier = 1.0
    
    for mod in modifiers:
        if "Rang" in mod.name:
            multiplier *= (1.0 + mod.value)
        else:
            base += mod.value
    
    final = max(0.0, min(0.95, base * multiplier))
    
    # Create display string
    display = f"Chance: {int(final * 100)}%"
    
    # Add color indicator
    if final >= 0.7:
        display += " [Sehr gut!]"
    elif final >= 0.5:
        display += " [Gut]"
    elif final >= 0.3:
        display += " [Okay]"
    elif final >= 0.15:
        display += " [Schwierig]"
    else:
        display += " [Sehr schwierig!]"
    
    return final, display


class TamingTips:
    """Helper class for taming tips and strategies."""
    
    @staticmethod
    def get_tips_for_monster(monster: MonsterInstance) -> List[str]:
        """Get taming tips for a specific monster."""
        tips = []
        
        # HP tip
        hp_percent = monster.current_hp / monster.max_hp
        if hp_percent > 0.5:
            tips.append("Schwäch das Monster erst mehr! (unter 50% HP)")
        elif hp_percent > 0.25:
            tips.append("Noch'n bisschen schwächen wär gut (unter 25% HP)")
        
        # Status tip
        if not monster.status:
            tips.append("Statuseffekte helfen beim Zähmen (Schlaf, Paralyse)")
        
        # Rank tip
        if monster.rank in ['S', 'SS', 'X']:
            tips.append(f"Rang {monster.rank} Monster sind echt schwer zu kriegen!")
        
        # Item tip
        tips.append("Fleisch-Items erhöhen die Chance deutlich!")
        
        return tips
    
    @staticmethod
    def get_general_tips() -> List[str]:
        """Get general taming tips."""
        return [
            "Schwäche Monster auf unter 25% HP für beste Chancen",
            "Schlaf is der beste Status zum Fangen (25% Bonus)",
            "Premium-Fleisch gibt 20% Extra-Chance",
            "Genervte Monster kann man nich nochmal versuchen",
            "Höhere Ränge sind schwerer zu zähmen",
            "Dein Team-Level beeinflusst die Erfolgschance",
            "Manche Bosse und Legendarys kann man gar nich zähmen"
        ]
