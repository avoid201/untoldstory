"""
Effect executor for battle system.
Handles all move effects, status conditions, stat changes, and item effects.
"""

from typing import TYPE_CHECKING, Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum, auto
import random
import logging

if TYPE_CHECKING:
    from engine.systems.monster_instance import MonsterInstance
    from engine.systems.battle.battle_system import BattleState as Battle
    from engine.systems.items import Item, ItemEffect

logger = logging.getLogger(__name__)


class EffectType(Enum):
    """Types of effects that can occur in battle."""
    DAMAGE = auto()
    HEAL = auto()
    STATUS = auto()
    STAT_CHANGE = auto()
    WEATHER = auto()
    TERRAIN = auto()
    PROTECT = auto()
    RECOIL = auto()
    DRAIN = auto()
    FLINCH = auto()
    CONFUSE = auto()
    TRAP = auto()
    SUBSTITUTE = auto()
    REFLECT = auto()
    LIGHT_SCREEN = auto()
    # Item-specific effects
    ITEM_HEAL = auto()
    ITEM_STATUS = auto()
    ITEM_STAT = auto()
    ITEM_SPECIAL = auto()


@dataclass
class EffectResult:
    """Result of applying an effect."""
    success: bool
    message: str
    value: Optional[int] = None
    prevented_by: Optional[str] = None


class ItemEffectHandler:
    """Handles item effects in battle context."""
    
    def __init__(self):
        """Initialize item effect handler."""
        self.rng = random.Random()
    
    def execute_item_effect(self, item: 'Item', target: 'MonsterInstance', 
                          battle: Optional['Battle'] = None) -> List[str]:
        """
        Execute item effects in battle context.
        
        Args:
            item: Item being used
            target: Target monster
            battle: Current battle state
            
        Returns:
            List of result messages
        """
        messages = []
        
        try:
            # Validierung der Eingabeparameter
            if not item:
                messages.append("Kein Item angegeben!")
                return messages
            
            if not target:
                messages.append("Kein Ziel angegeben!")
                return messages
            
            # Check if item can be used in battle
            if not hasattr(item, 'use_in_battle') or not item.use_in_battle:
                messages.append(f"{item.name if hasattr(item, 'name') else 'Item'} kann nicht im Kampf verwendet werden!")
                return messages
            
            # Check effectiveness
            if hasattr(item, 'get_effectiveness_message'):
                try:
                    effectiveness_msg = item.get_effectiveness_message(target)
                    if effectiveness_msg:
                        messages.append(effectiveness_msg)
                        return messages
                except Exception as e:
                    logger.warning(f"Fehler bei der Effektivitätsprüfung: {str(e)}")
                    # Fahre mit der Ausführung fort
            
            # Execute each effect
            if hasattr(item, 'effects') and item.effects:
                for effect in item.effects:
                    if not effect:
                        continue
                        
                    try:
                        if self.rng.random() > effect.chance:
                            continue
                        
                        result = self._apply_item_effect(effect, target, battle)
                        if result:
                            messages.append(result)
                    except Exception as e:
                        logger.error(f"Fehler bei der Effektausführung: {str(e)}")
                        messages.append(f"Effekt fehlgeschlagen: {str(e)}")
            else:
                messages.append("Item hat keine Effekte!")
            
        except Exception as e:
            logger.error(f"Kritischer Fehler bei der Item-Effektausführung: {str(e)}")
            messages.append(f"Item-Verwendung fehlgeschlagen: {str(e)}")
        
        return messages
    
    def _apply_item_effect(self, effect: 'ItemEffect', target: 'MonsterInstance', 
                          battle: Optional['Battle']) -> Optional[str]:
        """Apply a single item effect."""
        
        # Map item effect types to battle effect types
        if effect.effect_type.name == 'HEAL_HP':
            return self._heal_hp_effect(effect, target)
        
        elif effect.effect_type.name == 'HEAL_STATUS':
            return self._heal_status_effect(effect, target)
        
        elif effect.effect_type.name == 'HEAL_ALL_STATUS':
            return self._heal_all_status_effect(target)
        
        elif effect.effect_type.name == 'REVIVE':
            return self._revive_effect(effect, target)
        
        elif effect.effect_type.name == 'BUFF_STAT':
            return self._buff_stat_effect(effect, target)
        
        elif effect.effect_type.name == 'DEBUFF_STAT':
            return self._debuff_stat_effect(effect, target)
        
        elif effect.effect_type.name == 'TAMING_BONUS':
            return self._taming_bonus_effect(effect, target, battle)
        
        elif effect.effect_type.name == 'ESCAPE':
            return self._escape_effect(battle)
        
        return effect.message if effect.message else None
    
    def _heal_hp_effect(self, effect: 'ItemEffect', target: 'MonsterInstance') -> str:
        """Heal HP effect from item."""
        if not target:
            return "Kein Ziel ausgewählt!"
        
        if isinstance(effect.value, float):
            # Percentage heal
            amount = int(target.max_hp * effect.value)
        else:
            # Fixed heal
            amount = effect.value
        
        actual = min(amount, target.max_hp - target.current_hp)
        target.current_hp += actual
        
        if actual > 0:
            return f"{target.nickname or target.species.name} heilt {actual} KP!"
        else:
            return f"{target.nickname or target.species.name} hat bereits volle KP!"
    
    def _heal_status_effect(self, effect: 'ItemEffect', target: 'MonsterInstance') -> str:
        """Heal status condition effect from item."""
        if not target or not target.status:
            return "Kein Statusproblem vorhanden!"
        
        if target.status == effect.value:
            old_status = target.status
            target.status = None
            target.status_turns = 0
            return f"{target.nickname or target.species.name} wurde von {old_status} geheilt!"
        
        return f"Dieses Item heilt nicht {target.status}!"
    
    def _heal_all_status_effect(self, target: 'MonsterInstance') -> str:
        """Heal all status conditions effect from item."""
        if not target or not target.status:
            return "Kein Statusproblem vorhanden!"
        
        old_status = target.status
        target.status = None
        target.status_turns = 0
        return f"{target.nickname or target.species.name} wurde von {old_status} geheilt!"
    
    def _revive_effect(self, effect: 'ItemEffect', target: 'MonsterInstance') -> str:
        """Revive effect from item."""
        if not target or target.current_hp > 0:
            return "Das Monster lebt noch!"
        
        if isinstance(effect.value, float):
            # Percentage revive
            target.current_hp = int(target.max_hp * effect.value)
        else:
            # Fixed HP revive
            target.current_hp = min(effect.value, target.max_hp)
        
        return f"{target.nickname or target.species.name} wurde wiederbelebt!"
    
    def _buff_stat_effect(self, effect: 'ItemEffect', target: 'MonsterInstance') -> str:
        """Buff stat effect from item."""
        if not target:
            return "Kein Ziel ausgewählt!"
        
        stat, stages = effect.value
        current = target.stat_stages.get(stat, 0)
        new_stage = max(-6, min(6, current + stages))
        
        if new_stage == current:
            return f"{target.nickname or target.species.name}'s {stat} kann nicht weiter erhöht werden!"
        
        target.stat_stages[stat] = new_stage
        
        stat_names = {
            'atk': 'Angriff', 'def': 'Verteidigung',
            'mag': 'Magie', 'res': 'Resistenz',
            'spd': 'Initiative', 'acc': 'Genauigkeit', 'eva': 'Fluchtwert'
        }
        
        return f"{target.nickname or target.species.name}'s {stat_names.get(stat, stat)} steigt!"
    
    def _debuff_stat_effect(self, effect: 'ItemEffect', target: 'MonsterInstance') -> str:
        """Debuff stat effect from item."""
        if not target:
            return "Kein Ziel ausgewählt!"
        
        stat, stages = effect.value
        current = target.stat_stages.get(stat, 0)
        new_stage = max(-6, min(6, current - stages))
        
        if new_stage == current:
            return f"{target.nickname or target.species.name}'s {stat} kann nicht weiter gesenkt werden!"
        
        target.stat_stages[stat] = new_stage
        
        stat_names = {
            'atk': 'Angriff', 'def': 'Verteidigung',
            'mag': 'Magie', 'res': 'Resistenz',
            'spd': 'Initiative', 'acc': 'Genauigkeit', 'eva': 'Fluchtwert'
        }
        
        return f"{target.nickname or target.species.name}'s {stat_names.get(stat, stat)} sinkt!"
    
    def _taming_bonus_effect(self, effect: 'ItemEffect', target: 'MonsterInstance', 
                            battle: Optional['Battle']) -> str:
        """Apply taming bonus effect from item."""
        if not battle or not battle.is_wild:
            return "Taming-Bonus funktioniert nur bei wilden Monstern!"
        
        # This would integrate with the taming system
        return f"Taming-Bonus von {effect.value}x angewendet!"
    
    def _escape_effect(self, battle: Optional['Battle']) -> str:
        """Escape effect from item."""
        if not battle:
            return "Nicht im Kampf!"
        
        # This would trigger battle escape
        return "Fluchtversuch gestartet!"


class StatusEffects:
    """Handles status condition effects."""
    
    # Status condition immunities by type
    TYPE_IMMUNITIES = {
        'burn': ['feuer'],
        'freeze': ['feuer', 'luft'],
        'poison': ['seuche', 'teufel'],
        'paralysis': ['energie']
    }
    
    @staticmethod
    def can_apply_status(target: 'MonsterInstance', status: str) -> Tuple[bool, str]:
        """
        Check if a status can be applied.
        
        Args:
            target: Target monster
            status: Status to apply
            
        Returns:
            Tuple of (can_apply, reason_if_not)
        """
        # Already has a status
        if target.status:
            return False, f"{target.nickname or target.species.name} hat bereits eine Statusveränderung!"
        
        # Check type immunity
        if status in StatusEffects.TYPE_IMMUNITIES:
            immune_types = StatusEffects.TYPE_IMMUNITIES[status]
            for monster_type in target.species.types:
                if monster_type in immune_types:
                    return False, f"{target.nickname or target.species.name} ist immun gegen {status}!"
        
        return True, ""
    
    @staticmethod
    def apply_status(target: 'MonsterInstance', status: str, duration: int = -1) -> EffectResult:
        """
        Apply a status condition.
        
        Args:
            target: Target monster
            status: Status to apply
            duration: Duration in turns (-1 for permanent)
            
        Returns:
            EffectResult
        """
        can_apply, reason = StatusEffects.can_apply_status(target, status)
        if not can_apply:
            return EffectResult(success=False, message=reason)
        
        target.status = status
        target.status_turns = duration
        
        status_messages = {
            'burn': "wurde verbrannt!",
            'freeze': "wurde eingefroren!",
            'paralysis': "wurde paralysiert!",
            'poison': "wurde vergiftet!",
            'sleep': "ist eingeschlafen!",
            'confusion': "wurde verwirrt!"
        }
        
        message = f"{target.nickname or target.species.name} {status_messages.get(status, 'erhielt einen Status!')}"
        return EffectResult(success=True, message=message)
    
    @staticmethod
    def process_status_damage(target: 'MonsterInstance') -> EffectResult:
        """
        Process end-of-turn status damage.
        
        Args:
            target: Monster with status
            
        Returns:
            EffectResult with damage dealt
        """
        if not target.status:
            return EffectResult(success=False, message="")
        
        damage = 0
        message = ""
        
        if target.status == 'burn':
            damage = max(1, target.max_hp // 8)
            message = f"{target.nickname or target.species.name} leidet unter der Verbrennung!"
        elif target.status == 'poison':
            damage = max(1, target.max_hp // 8)
            message = f"{target.nickname or target.species.name} leidet unter der Vergiftung!"
        elif target.status == 'badly_poisoned':
            # Increases each turn
            if not hasattr(target, 'poison_counter'):
                target.poison_counter = 1
            damage = max(1, (target.max_hp * target.poison_counter) // 16)
            target.poison_counter += 1
            message = f"{target.nickname or target.species.name} leidet schwer unter der Vergiftung!"
        
        if damage > 0:
            target.current_hp = max(0, target.current_hp - damage)
            return EffectResult(success=True, message=message, value=damage)
        
        return EffectResult(success=False, message="")


class StatChangeEffects:
    """Handles stat stage changes."""
    
    STAT_NAMES = {
        'atk': 'Angriff',
        'def': 'Verteidigung', 
        'mag': 'Magie',
        'res': 'Resistenz',
        'spd': 'Initiative',
        'acc': 'Genauigkeit',
        'eva': 'Fluchtwert'
    }
    
    @staticmethod
    def change_stat(target: 'MonsterInstance', stat: str, stages: int) -> EffectResult:
        """
        Change a stat stage.
        
        Args:
            target: Target monster
            stat: Stat to change
            stages: Number of stages to change (positive or negative)
            
        Returns:
            EffectResult
        """
        if stat not in StatChangeEffects.STAT_NAMES:
            return EffectResult(success=False, message="Unbekannter Wert!")
        
        current_stage = target.stat_stages.get(stat, 0)
        new_stage = max(-6, min(6, current_stage + stages))
        
        # No change possible
        if new_stage == current_stage:
            if stages > 0 and current_stage == 6:
                message = f"{target.nickname or target.species.name}'s {StatChangeEffects.STAT_NAMES[stat]} kann nicht weiter erhöht werden!"
            elif stages < 0 and current_stage == -6:
                message = f"{target.nickname or target.species.name}'s {StatChangeEffects.STAT_NAMES[stat]} kann nicht weiter gesenkt werden!"
            else:
                message = "Keine Veränderung!"
            return EffectResult(success=False, message=message)
        
        target.stat_stages[stat] = new_stage
        actual_change = new_stage - current_stage
        
        # Generate message
        stat_name = StatChangeEffects.STAT_NAMES[stat]
        if actual_change > 0:
            if actual_change == 1:
                change_text = "stieg"
            elif actual_change == 2:
                change_text = "stieg stark"
            else:
                change_text = "stieg drastisch"
        else:
            if actual_change == -1:
                change_text = "sank"
            elif actual_change == -2:
                change_text = "sank stark"
            else:
                change_text = "sank drastisch"
        
        message = f"{target.nickname or target.species.name}'s {stat_name} {change_text}!"
        return EffectResult(success=True, message=message, value=actual_change)


class EffectExecutor:
    """Main effect executor for battle."""
    
    def __init__(self, battle: Optional['Battle'] = None, seed: Optional[int] = None):
        """
        Initialize effect executor.
        
        Args:
            battle: Reference to battle state
            seed: Random seed for deterministic behavior
        """
        self.battle = battle
        self.rng = random.Random(seed)
        self.status_effects = StatusEffects()
        self.stat_changes = StatChangeEffects()
        self.item_effects = ItemEffectHandler()
    
    def execute_effect(self, effect: Dict[str, Any], 
                      user: 'MonsterInstance',
                      target: 'MonsterInstance') -> List[EffectResult]:
        """
        Execute a single effect.
        
        Args:
            effect: Effect dictionary from move data
            user: Monster using the move
            target: Target monster
            
        Returns:
            List of EffectResults
        """
        results = []
        effect_type = effect.get('kind', 'damage')
        
        # Check if effect triggers (chance-based effects)
        chance = effect.get('chance', 100)
        if chance < 100 and self.rng.uniform(0, 100) >= chance:
            return []  # Effect didn't trigger
        
        if effect_type == 'status':
            status = effect.get('status')
            duration = effect.get('duration', -1)
            result = self.status_effects.apply_status(target, status, duration)
            results.append(result)
            
        elif effect_type == 'stat_change':
            stat = effect.get('stat')
            stages = effect.get('stages', 1)
            result = self.stat_changes.change_stat(target, stat, stages)
            results.append(result)
            
        elif effect_type == 'heal':
            amount = effect.get('amount', 50)
            if effect.get('percent', False):
                heal = int(target.max_hp * (amount / 100))
            else:
                heal = amount
            
            actual_heal = min(heal, target.max_hp - target.current_hp)
            target.current_hp += actual_heal
            
            message = f"{target.nickname or target.species.name} heilte {actual_heal} KP!"
            results.append(EffectResult(success=True, message=message, value=actual_heal))
            
        elif effect_type == 'recoil':
            # Recoil is calculated based on damage dealt
            percent = effect.get('percent', 25)
            # This would be calculated after damage is dealt
            results.append(EffectResult(
                success=True, 
                message="Rückstoß-Schaden wird berechnet...",
                value=percent
            ))
            
        elif effect_type == 'drain':
            # Drain heals user based on damage dealt
            percent = effect.get('percent', 50)
            results.append(EffectResult(
                success=True,
                message="Absorbiert Lebenspunkte...",
                value=percent
            ))
            
        elif effect_type == 'weather':
            weather = effect.get('weather')
            duration = effect.get('duration', 5)
            if self.battle:
                self.battle.weather = weather
                self.battle.weather_turns = duration
                
            weather_messages = {
                'sunny': "Die Sonne scheint hell!",
                'rain': "Es beginnt zu regnen!",
                'sandstorm': "Ein Sandsturm zieht auf!",
                'hail': "Es beginnt zu hageln!"
            }
            message = weather_messages.get(weather, "Das Wetter ändert sich!")
            results.append(EffectResult(success=True, message=message))
            
        elif effect_type == 'flinch':
            # Flinch prevents action this turn
            if hasattr(target, 'flinched'):
                target.flinched = True
            message = f"{target.nickname or target.species.name} ist zurückgeschreckt!"
            results.append(EffectResult(success=True, message=message))
            
        elif effect_type == 'protect':
            # Protection for one turn
            if hasattr(user, 'protected'):
                user.protected = True
            message = f"{user.nickname or user.species.name} schützt sich!"
            results.append(EffectResult(success=True, message=message))
        
        return results
    
    def execute_item_effects(self, item: 'Item', target: 'MonsterInstance') -> List[str]:
        """
        Execute item effects in battle context.
        
        Args:
            item: Item being used
            target: Target monster
            
        Returns:
            List of result messages
        """
        return self.item_effects.execute_item_effect(item, target, self.battle)
    
    def execute_move_effects(self, move_data: Dict[str, Any],
                            user: 'MonsterInstance',
                            targets: List['MonsterInstance']) -> Dict[str, List[EffectResult]]:
        """
        Execute all effects of a move.
        
        Args:
            move_data: Move data dictionary
            user: Monster using the move
            targets: List of target monsters
            
        Returns:
            Dictionary mapping target to list of effects
        """
        results = {}
        
        effects = move_data.get('effects', [])
        
        for target in targets:
            target_results = []
            
            # Check if target is protected
            if hasattr(target, 'protected') and target.protected:
                target_results.append(EffectResult(
                    success=False,
                    message=f"{target.nickname or target.species.name} schützt sich!",
                    prevented_by='protect'
                ))
                results[target] = target_results
                continue
            
            # Execute each effect
            for effect in effects:
                effect_results = self.execute_effect(effect, user, target)
                target_results.extend(effect_results)
            
            results[target] = target_results
        
        return results
    
    def clear_turn_flags(self, monster: 'MonsterInstance') -> None:
        """
        Clear single-turn flags from a monster.
        
        Args:
            monster: Monster to clear flags from
        """
        flags_to_clear = ['protected', 'flinched', 'moved_this_turn']
        for flag in flags_to_clear:
            if hasattr(monster, flag):
                delattr(monster, flag)
    
    def process_end_of_turn(self, monster: 'MonsterInstance') -> List[EffectResult]:
        """
        Process end-of-turn effects for a monster.
        
        Args:
            monster: Monster to process
            
        Returns:
            List of EffectResults
        """
        results = []
        
        # Process status damage
        status_result = self.status_effects.process_status_damage(monster)
        if status_result.success:
            results.append(status_result)
        
        # Process status duration
        if monster.status and monster.status_turns > 0:
            monster.status_turns -= 1
            if monster.status_turns == 0:
                old_status = monster.status
                monster.status = None
                
                recovery_messages = {
                    'sleep': "ist aufgewacht!",
                    'freeze': "ist aufgetaut!",
                    'confusion': "ist nicht mehr verwirrt!"
                }
                
                message = f"{monster.nickname or monster.species.name} {recovery_messages.get(old_status, 'hat sich erholt!')}"
                results.append(EffectResult(success=True, message=message))
        
        # Clear turn flags
        self.clear_turn_flags(monster)
        
        return results