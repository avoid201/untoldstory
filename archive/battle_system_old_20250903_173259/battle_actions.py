"""
Battle Actions Module
Handles execution of all battle actions
"""

import logging
import random
from typing import Dict, Any, Optional, List, TYPE_CHECKING
from dataclasses import dataclass
from engine.systems.monster_instance import MonsterInstance, StatusCondition
from engine.systems.battle.turn_logic_clean import BattleAction, ActionType
from engine.systems.battle.meat_system import MeatSystem, MeatType
from engine.systems.battle.battle_effects import ItemEffectHandler

# UNIFIED ACTION FORMAT - One Action Format to Rule Them All!
@dataclass
class UnifiedAction:
    """Einheitliches Action-Format für alle Battle-Actions."""
    type: str  # 'attack', 'item', 'switch', 'tame', 'scout', 'flee'
    actor: MonsterInstance
    target: Optional[MonsterInstance]
    data: dict  # move_id, item_id, etc.
    
    def to_battle_action(self) -> BattleAction:
        """Konvertiere UnifiedAction zu BattleAction für Controller."""
        action_type_map = {
            'attack': ActionType.ATTACK,
            'item': ActionType.ITEM,
            'switch': ActionType.SWITCH,
            'tame': ActionType.TAME,
            'scout': ActionType.SCOUT,
            'flee': ActionType.FLEE
        }
        
        return BattleAction(
            action_type=action_type_map.get(self.type, ActionType.PASS),
            actor=self.actor,
            target=self.target,
            move=self.data.get('move'),
            item_id=self.data.get('item_id'),
            meat_type=self.data.get('meat_type')
        )
# Import from the integrated skills system
try:
    from engine.systems.battle.skills_dqm_integrated import (
        SkillDatabase, SkillType, SkillElement, SkillTarget
    )
    def get_skill_database():
        return SkillDatabase()
except ImportError:
    # Fallback if skills system not available
    def get_skill_database():
        return {}
    
    class SkillType:
        """Fallback SkillType enum."""
        PHYSICAL = "physical"
        MAGICAL = "magical"
        SUPPORT = "support"
        HEALING = "healing"
        BUFF = "buff"
        DEBUFF = "debuff"
    
    class SkillElement:
        """Fallback SkillElement enum."""
        NORMAL = "normal"
        FIRE = "fire"
        ICE = "ice"
        THUNDER = "thunder"
        WIND = "wind"
        EARTH = "earth"
        WATER = "water"
        DARK = "dark"
        LIGHT = "light"
        NONE = "none"
    
    class SkillTarget:
        """Fallback SkillTarget enum."""
        ENEMY = "enemy"
        ALLY = "ally"
        SELF = "self"
        ALL_ENEMIES = "all_enemies"
        ALL_ALLIES = "all_allies"
        ALL = "all"
        RANDOM = "random"
# SINGLE SOURCE OF TRUTH: UnifiedDamageCalculator (Lazy Import to avoid circular dependency)

if TYPE_CHECKING:
    # Lazy imports für zirkuläre Dependencies

    from engine.systems.battle.battle_controller import BattleState

logger = logging.getLogger(__name__)


class BattleActionExecutor:
    """Executes battle actions."""
    
    def __init__(self):
        """Initialize action executor."""
        # Verwende UnifiedDamageCalculator als Single Source of Truth
        self.item_effects = ItemEffectHandler()
        self.skill_database = get_skill_database()
        self.battle_log: List[str] = []
    
    # Pipeline-Property entfernt - verwende UnifiedDamageCalculator
    
    def execute_action(self, action, battle_state: 'BattleState') -> Optional[Dict[str, Any]]:
        """
        Execute a single battle action.
        
        Args:
            action: The action to execute (BattleAction or dict)
            battle_state: Current battle state
            
        Returns:
            Result of the action or None on error
        """
        try:
            # Handle both BattleAction objects and dicts
            if isinstance(action, dict):
                # It's a dict from UI, extract the action type
                action_type = action.get('action')
                if action_type == 'attack':
                    # Create a BattleAction from dict
                    from engine.systems.battle.turn_logic_clean import BattleAction, ActionType
                    battle_action = BattleAction(
                        action_type=ActionType.ATTACK,
                        actor=action.get('actor'),
                        move=action.get('move'),
                        target=action.get('target')
                    )
                    action = battle_action
                else:
                    logger.error(f"Unsupported dict action type: {action_type}")
                    return None
            
            # Import ActionType at the top level to avoid scope issues
            from engine.systems.battle.turn_logic_clean import ActionType
            
            if action.action_type == ActionType.ATTACK:
                return self._execute_attack(action, battle_state)
            elif action.action_type == ActionType.TAME:
                return self._execute_tame(action, battle_state)
            elif action.action_type == ActionType.USE_MEAT:
                return self._execute_use_meat(action, battle_state)
            elif action.action_type == ActionType.ITEM:
                return self._execute_item(action, battle_state)
            elif action.action_type == ActionType.SWITCH:
                return self._execute_switch(action, battle_state)
            elif action.action_type == ActionType.FLEE:
                return self._execute_flee(action, battle_state)
            elif action.action_type == ActionType.SKILL:
                return self._execute_skill(action, battle_state)
            elif action.action_type == ActionType.SCOUT:
                return self._execute_scout(action, battle_state)
            else:
                logger.error(f"Unknown action type: {action.action_type}")
                return None
                
        except Exception as e:
            logger.error(f"Error executing action: {str(e)}")
            return None
    
    def _execute_attack(self, action: BattleAction, battle_state: 'BattleState') -> Dict[str, Any]:
        """Execute an attack action."""
        try:
            # Calculate damage using UnifiedDamageCalculator (SINGLE SOURCE OF TRUTH)
            try:
                # Use UnifiedDamageCalculator (Lazy Import)
                from engine.systems.unified_damage_calculator import unified_damage_calculator
                damage_result = unified_damage_calculator.calculate_damage(
                    attacker=action.actor,
                    defender=action.target,
                    move=action.move
                )
                
                # Handle both DamageResult object and dict results
                if hasattr(damage_result, 'damage'):
                    damage = damage_result.damage
                elif isinstance(damage_result, dict):
                    damage = damage_result.get('damage', 0)
                else:
                    damage = damage_result if isinstance(damage_result, (int, float)) else 0
                    
            except Exception as e:
                logger.warning(f"Error calculating damage with UnifiedDamageCalculator, using fallback: {str(e)}")
                # Fallback: Simple damage calculation
                damage = max(1, action.move.power // 2)
            
            # Apply damage
            action.target.take_damage(damage)
            
            # KRITISCHE VERBINDUNG: Check für Status-Apply nach Damage!
            status_applied = self._check_status_application(action, battle_state)
            
            # Log the attack
            self.battle_log.append(f"{action.actor.name} greift {action.target.name} an!")
            if status_applied:
                self.battle_log.append(f"Status-Effekt angewendet: {status_applied}")
            
            return {
                'type': 'attack',
                'attacker': action.actor.name,
                'target': action.target.name,
                'damage': damage,
                'target_fainted': action.target.is_fainted,
                'status_applied': status_applied
            }
            
        except Exception as e:
            logger.error(f"Error executing attack: {str(e)}")
            return {'error': str(e)}
    
    def _execute_tame(self, action: BattleAction, battle_state: 'BattleState') -> Dict[str, Any]:
        """Execute a taming action with meat system."""
        try:
            # Get meat system from battle state or action
            meat_system = None
            if hasattr(action, 'meat_system'):
                meat_system = action.meat_system
            elif hasattr(battle_state, 'meat_system'):
                meat_system = battle_state.meat_system
            else:
                # Fallback: create new meat system
                meat_system = MeatSystem()
            
            # Get monster info for calculation
            target = action.target
            hp_percent = target.current_hp / max(1, target.max_hp)
            
            # Get monster rank
            monster_rank = 'D'  # Default
            if hasattr(target, 'rank'):
                monster_rank = target.rank
            elif hasattr(target, 'species') and hasattr(target.species, 'rank'):
                monster_rank = target.species.rank
            
            # Get monster status
            monster_status = None
            if hasattr(target, 'status'):
                if hasattr(target.status, 'value'):
                    monster_status = target.status.value
                elif isinstance(target.status, str):
                    monster_status = target.status
            
            # Calculate taming chance with meat system
            tame_data = meat_system.calculate_taming_chance(
                base_chance=0.15,  # 15% base chance
                monster_hp_percent=hp_percent,
                monster_rank=monster_rank,
                monster_status=monster_status
            )
            
            final_chance = tame_data['final_chance']
            
            # Roll for taming success
            success = random.random() < final_chance
            
            if success:
                self.battle_log.append(f"{target.name} wurde erfolgreich gezähmt!")
                if tame_data['meat_active']:
                    self.battle_log.append(f"Das {tame_data['meat_name']} hat geholfen!")
                
                return {
                    'type': 'tame',
                    'success': True,
                    'monster': target.name,
                    'final_chance': final_chance,
                    'modifiers': tame_data['modifiers']
                }
            else:
                self.battle_log.append(f"Zähmversuch von {target.name} fehlgeschlagen!")
                # Monster might get angry
                if random.random() < 0.3:  # 30% chance to get angry
                    if hasattr(target, 'stat_stages'):
                        target.stat_stages['atk'] = min(6, target.stat_stages.get('atk', 0) + 1)
                        self.battle_log.append(f"{target.name} wird wütend! Angriff steigt!")
                
                return {
                    'type': 'tame',
                    'success': False,
                    'monster': target.name,
                    'final_chance': final_chance,
                    'modifiers': tame_data['modifiers']
                }
                
        except Exception as e:
            logger.error(f"Error executing taming: {str(e)}")
            return {'error': str(e)}
    
    def _execute_use_meat(self, action: BattleAction, battle_state: 'BattleState') -> Dict[str, Any]:
        """Execute meat usage action."""
        try:
            # Get meat system
            meat_system = None
            if hasattr(battle_state, 'meat_system'):
                meat_system = battle_state.meat_system
            else:
                meat_system = MeatSystem()
            
            # Get meat type from action
            meat_type = action.meat_type if hasattr(action, 'meat_type') else MeatType.NONE
            
            # Use the meat
            success, message = meat_system.use_meat(meat_type, battle_state)
            
            if success:
                self.battle_log.append(message)
                
                # Enemy gets a free turn after meat usage!
                return {
                    'type': 'use_meat',
                    'success': True,
                    'meat_type': meat_type.display_name if hasattr(meat_type, 'display_name') else str(meat_type),
                    'message': message,
                    'enemy_gets_turn': True  # Important: enemy attacks after meat use
                }
            else:
                return {
                    'type': 'use_meat',
                    'success': False,
                    'message': message
                }
                
        except Exception as e:
            logger.error(f"Error using meat: {str(e)}")
            return {'error': str(e)}
    
    def _execute_item(self, action: BattleAction, battle_state: 'BattleState') -> Dict[str, Any]:
        """Execute an item usage action."""
        try:
            result = self.item_effects.execute_item_effect(
                item=action.item,
                target=action.target,
                user=action.actor,
                battle=battle_state
            )
            
            if result['success']:
                self.battle_log.append(f"{action.actor.name} benutzt {action.item.name}!")
                
                return {
                    'type': 'item',
                    'user': action.actor.name,
                    'item': action.item.name,
                    'target': action.target.name,
                    'effect': result,
                    'messages': result.get('messages', [])
                }
            else:
                return {
                    'type': 'item',
                    'user': action.actor.name,
                    'item': action.item.name,
                    'target': action.target.name,
                    'error': result.get('message', 'Item effect failed')
                }
            
        except Exception as e:
            logger.error(f"Error executing item: {str(e)}")
            return {'error': str(e)}
    
    def _execute_switch(self, action: BattleAction, battle_state: 'BattleState') -> Dict[str, Any]:
        """Execute a monster switch action."""
        try:
            old_active = battle_state.player_active
            battle_state.player_active = action.target
            
            self.battle_log.append(f"{old_active.name} wurde durch {battle_state.player_active.name} ersetzt!")
            
            return {
                'type': 'switch',
                'old_monster': old_active.name,
                'new_monster': battle_state.player_active.name
            }
            
        except Exception as e:
            logger.error(f"Error executing switch: {str(e)}")
            return {'error': str(e)}
    
    def _execute_flee(self, action: BattleAction, battle_state: 'BattleState') -> Dict[str, Any]:
        """Execute a flee action."""
        try:
            if not battle_state.can_flee:
                self.battle_log.append("Fliehen ist in diesem Kampf nicht möglich!")
                return {
                    'type': 'flee',
                    'success': False,
                    'reason': 'not_allowed'
                }
            
            # Calculate flee chance using DQM formula with escape attempts
            flee_chance = self._calculate_flee_chance(
                battle_state.player_active.stats.get('spd', 1),
                battle_state.enemy_active.stats.get('spd', 1),
                battle_state.escape_attempts
            )
            
            # Roll for flee success
            success = random.random() < flee_chance
            
            if success:
                self.battle_log.append(f"{action.actor.name} ist erfolgreich geflohen!")
                return {
                    'type': 'flee',
                    'success': True
                }
            else:
                battle_state.escape_attempts += 1
                self.battle_log.append(f"Flucht von {action.actor.name} fehlgeschlagen!")
                return {
                    'type': 'flee',
                    'success': False,
                    'escape_attempts': battle_state.escape_attempts
                }
                
        except Exception as e:
            logger.error(f"Error executing flee: {str(e)}")
            return {'error': str(e)}
    
    def _calculate_flee_chance(self, player_speed: int, enemy_speed: int, escape_attempts: int = 0) -> float:
        """
        Calculate flee chance using DQM formulas.
        
        Args:
            player_speed: Player monster's speed
            enemy_speed: Enemy monster's speed
            escape_attempts: Number of previous escape attempts
            
        Returns:
            Flee chance as float between 0.0 and 1.0
        """
        try:
            # Use UnifiedDamageCalculator for escape calculation (SINGLE SOURCE OF TRUTH)
            from engine.systems.unified_damage_calculator import unified_damage_calculator
            escape_chance = unified_damage_calculator.calculate_escape_chance(
                runner_speed=player_speed,
                enemy_speed=enemy_speed,
                attempts=escape_attempts
            )
            
            return escape_chance
            
        except Exception as e:
            logger.error(f"Error calculating flee chance with DQM: {str(e)}")
            # Fallback to original formula
            base_chance = 0.5
            speed_factor = min(player_speed / max(1, enemy_speed), 2.0)
            flee_chance = base_chance * speed_factor
            flee_chance = max(0.1, min(0.95, flee_chance))
            return flee_chance
    
    def _execute_scout(self, action: BattleAction, battle_state: 'BattleState') -> Dict[str, Any]:
        """Execute scout action to analyze enemy monster."""
        try:
            target = action.target if action.target else battle_state.enemy_active
            
            if not target:
                return {'error': 'No target to scout'}
            
            # Scout provides information but costs a turn
            self.battle_log.append(f"{action.actor.name} späht {target.name} aus!")
            
            # Extract some basic info for the log
            info = []
            
            # HP info
            hp_percent = int((target.current_hp / max(1, target.max_hp)) * 100)
            info.append(f"HP: {hp_percent}%")
            
            # Types
            if hasattr(target, 'types') and target.types:
                info.append(f"Typ: {', '.join(target.types)}")
            
            # Rank
            if hasattr(target, 'rank'):
                info.append(f"Rang: {target.rank}")
            elif hasattr(target, 'species') and hasattr(target.species, 'rank'):
                info.append(f"Rang: {target.species.rank}")
            
            # Status
            if hasattr(target, 'status') and target.status:
                status_str = target.status
                if hasattr(target.status, 'value'):
                    status_str = target.status.value
                info.append(f"Status: {status_str}")
            
            # Add to battle log
            self.battle_log.append(f"Analyse: {' | '.join(info)}")
            
            return {
                'type': 'scout',
                'actor': action.actor.name,
                'target': target.name,
                'info': info,
                'costs_turn': True  # Important: scouting costs a turn
            }
            
        except Exception as e:
            logger.error(f"Error executing scout: {str(e)}")
            return {'error': str(e)}
    
    # Old _calculate_tame_chance removed - now using meat_system.calculate_taming_chance()
    
    def execute_special_command(self, command: str, monster: MonsterInstance, battle_state: 'BattleState') -> Dict[str, Any]:
        """
        Execute special DQM commands.
        
        Args:
            command: The command to execute
            monster: The monster executing the command
            battle_state: Current battle state
            
        Returns:
            Result of the command
        """
        try:
            logger.warning(f"Unknown special command: {command}")
            return {'error': f'Unknown command: {command}'}
                
        except Exception as e:
            logger.error(f"Error executing special command: {str(e)}")
            return {'error': str(e)}
    

    
    def _execute_skill(self, action: BattleAction, battle_state: 'BattleState') -> Dict[str, Any]:
        """Execute a DQM skill action."""
        try:
            skill_name = action.move.name if hasattr(action.move, 'name') else str(action.move)
            
            # Get skill from database
            skill_data = self.skill_database.get_skill_by_name(skill_name)
            if not skill_data:
                logger.error(f"Skill {skill_name} not found in database")
                return {'error': f'Unknown skill: {skill_name}'}
            
            family, skill = skill_data
            
            # Check MP cost
            if hasattr(action.actor, 'current_mp'):
                mp_cost = self.skill_database.calculate_mp_cost(
                    skill, 
                    action.actor.level if hasattr(action.actor, 'level') else 1
                )
                
                if action.actor.current_mp < mp_cost:
                    self.battle_log.append(f"{action.actor.name} hat nicht genug MP für {skill.name}!")
                    return {
                        'type': 'skill_failed',
                        'reason': 'insufficient_mp',
                        'skill': skill.name,
                        'mp_needed': mp_cost,
                        'mp_current': action.actor.current_mp
                    }
                
                # Deduct MP
                action.actor.current_mp -= mp_cost
            
            # Execute based on skill type
            if family.skill_type == SkillType.ATTACK:
                return self._execute_attack_skill(action, battle_state, family, skill)
            elif family.skill_type == SkillType.HEAL:
                return self._execute_heal_skill(action, battle_state, family, skill)
            elif family.skill_type == SkillType.BUFF:
                return self._execute_buff_skill(action, battle_state, family, skill)
            elif family.skill_type == SkillType.DEBUFF:
                return self._execute_debuff_skill(action, battle_state, family, skill)
            elif family.skill_type == SkillType.STATUS:
                return self._execute_status_skill(action, battle_state, family, skill)
            elif family.skill_type == SkillType.BREATH:
                return self._execute_breath_skill(action, battle_state, family, skill)
            else:
                logger.warning(f"Unhandled skill type: {family.skill_type}")
                # Fall back to regular attack
                return self._execute_attack_skill(action, battle_state, family, skill)
                
        except Exception as e:
            logger.error(f"Error executing skill: {str(e)}")
            return {'error': str(e)}
    
    def _execute_attack_skill(self, action, battle_state, family, skill):
        """Execute an attack-type skill."""
        try:
            # Get targets based on skill target type
            targets = self._get_skill_targets(action, battle_state, family.target)
            
            results = []
            total_damage = 0
            
            for target in targets:
                # Calculate damage with element modifier
                base_damage = skill.power
                
                # Apply element effectiveness
                if hasattr(target, 'element'):
                    element_mod = self.skill_database.get_element_modifier(
                        family.element, 
                        target.element if hasattr(target, 'element') else SkillElement.NORMAL
                    )
                    base_damage = int(base_damage * element_mod)
                
                # Apply attack formula
                if hasattr(action.actor, 'stats') and hasattr(target, 'stats'):
                    atk = action.actor.stats.get('mag', 50)  # Use MAG for skills
                    def_ = target.stats.get('res', 40)  # Use RES for magic defense
                    damage = max(1, (base_damage * atk // 100) - (def_ // 4))
                else:
                    damage = base_damage
                
                # Apply damage
                target.take_damage(damage)
                total_damage += damage
                
                results.append({
                    'target': target.name,
                    'damage': damage,
                    'fainted': target.is_fainted
                })
            
            # Log the skill use
            if len(targets) > 1:
                self.battle_log.append(f"{action.actor.name} wirkt {skill.name} auf alle Gegner!")
            else:
                self.battle_log.append(f"{action.actor.name} wirkt {skill.name} auf {targets[0].name}!")
            
            return {
                'type': 'skill_attack',
                'skill': skill.name,
                'element': family.element.value,
                'caster': action.actor.name,
                'targets': results,
                'total_damage': total_damage
            }
            
        except Exception as e:
            logger.error(f"Error in attack skill: {str(e)}")
            return {'error': str(e)}
    
    def _execute_heal_skill(self, action, battle_state, family, skill):
        """Execute a healing skill."""
        try:
            # Get targets
            targets = self._get_skill_targets(action, battle_state, family.target)
            
            results = []
            total_healed = 0
            
            for target in targets:
                # Calculate heal amount
                heal_amount = skill.power
                
                # Apply magic stat bonus
                if hasattr(action.actor, 'stats'):
                    mag = action.actor.stats.get('mag', 50)
                    heal_amount = int(heal_amount * (1 + mag / 200))  # Up to 50% bonus
                
                # Heal target
                if hasattr(target, 'heal'):
                    actual_heal = target.heal(heal_amount)
                else:
                    # Fallback healing
                    old_hp = target.current_hp
                    target.current_hp = min(target.max_hp, target.current_hp + heal_amount)
                    actual_heal = target.current_hp - old_hp
                
                total_healed += actual_heal
                
                results.append({
                    'target': target.name,
                    'healed': actual_heal,
                    'current_hp': target.current_hp,
                    'max_hp': target.max_hp
                })
            
            # Log
            if len(targets) > 1:
                self.battle_log.append(f"{action.actor.name} heilt alle Verbündeten mit {skill.name}!")
            else:
                self.battle_log.append(f"{action.actor.name} heilt {targets[0].name} mit {skill.name}!")
            
            return {
                'type': 'skill_heal',
                'skill': skill.name,
                'caster': action.actor.name,
                'targets': results,
                'total_healed': total_healed
            }
            
        except Exception as e:
            logger.error(f"Error in heal skill: {str(e)}")
            return {'error': str(e)}
    
    def _execute_buff_skill(self, action, battle_state, family, skill):
        """Execute a buff skill."""
        try:
            targets = self._get_skill_targets(action, battle_state, family.target)
            results = []
            
            for target in targets:
                stat = skill.effects.get('stat')
                stages = skill.effects.get('stages', 1)
                
                if stat and hasattr(target, 'stat_stages'):
                    # Apply stat buff
                    old_stage = target.stat_stages.get(stat, 0)
                    target.stat_stages[stat] = min(6, old_stage + stages)  # Max +6 stages
                    
                    results.append({
                        'target': target.name,
                        'stat': stat,
                        'new_stage': target.stat_stages[stat]
                    })
            
            self.battle_log.append(f"{action.actor.name} nutzt {skill.name}!")
            
            return {
                'type': 'skill_buff',
                'skill': skill.name,
                'caster': action.actor.name,
                'targets': results
            }
            
        except Exception as e:
            logger.error(f"Error in buff skill: {str(e)}")
            return {'error': str(e)}
    
    def _execute_debuff_skill(self, action, battle_state, family, skill):
        """Execute a debuff skill."""
        try:
            targets = self._get_skill_targets(action, battle_state, family.target)
            results = []
            
            for target in targets:
                # Check accuracy
                if random.random() > skill.accuracy:
                    results.append({
                        'target': target.name,
                        'missed': True
                    })
                    continue
                
                stat = skill.effects.get('stat')
                stages = skill.effects.get('stages', -1)
                
                if stat and hasattr(target, 'stat_stages'):
                    old_stage = target.stat_stages.get(stat, 0)
                    target.stat_stages[stat] = max(-6, old_stage + stages)  # Min -6 stages
                    
                    results.append({
                        'target': target.name,
                        'stat': stat,
                        'new_stage': target.stat_stages[stat]
                    })
            
            self.battle_log.append(f"{action.actor.name} nutzt {skill.name}!")
            
            return {
                'type': 'skill_debuff',
                'skill': skill.name,
                'caster': action.actor.name,
                'targets': results
            }
            
        except Exception as e:
            logger.error(f"Error in debuff skill: {str(e)}")
            return {'error': str(e)}
    
    def _execute_status_skill(self, action, battle_state, family, skill):
        """Execute a status effect skill."""
        try:
            targets = self._get_skill_targets(action, battle_state, family.target)
            results = []
            
            for target in targets:
                # Check accuracy
                if random.random() > skill.accuracy:
                    results.append({
                        'target': target.name,
                        'missed': True
                    })
                    continue
                
                status = skill.effects.get('status')
                if status and hasattr(target, 'apply_status'):
                    # Map string to StatusCondition
                    status_map = {
                        'sleep': StatusCondition.SLEEP,
                        'poison': StatusCondition.POISON,
                        'paralysis': StatusCondition.PARALYSIS,
                        'burn': StatusCondition.BURN,
                        'freeze': StatusCondition.FREEZE,
                        'confusion': StatusCondition.CONFUSION
                    }
                    
                    status_condition = status_map.get(status)
                    if status_condition:
                        success = target.apply_status(status_condition)
                        results.append({
                            'target': target.name,
                            'status': status,
                            'applied': success
                        })
            
            self.battle_log.append(f"{action.actor.name} nutzt {skill.name}!")
            
            return {
                'type': 'skill_status',
                'skill': skill.name,
                'caster': action.actor.name,
                'targets': results
            }
            
        except Exception as e:
            logger.error(f"Error in status skill: {str(e)}")
            return {'error': str(e)}
    
    def _execute_breath_skill(self, action, battle_state, family, skill):
        """Execute a breath attack (no MP cost, always hits all enemies)."""
        try:
            # Breath attacks always target all enemies
            if hasattr(battle_state, 'enemy_team'):
                targets = [m for m in battle_state.enemy_team if not m.is_fainted]
            else:
                targets = [battle_state.enemy_active] if battle_state.enemy_active else []
            
            results = []
            total_damage = 0
            
            for target in targets:
                # Breath damage is based on level, not stats
                base_damage = skill.power
                if hasattr(action.actor, 'level'):
                    base_damage = int(base_damage * (1 + action.actor.level / 50))
                
                # Apply element modifier
                if hasattr(target, 'element'):
                    element_mod = self.skill_database.get_element_modifier(
                        family.element,
                        target.element if hasattr(target, 'element') else SkillElement.NORMAL
                    )
                    base_damage = int(base_damage * element_mod)
                
                # Breath attacks partially ignore defense
                damage = max(1, base_damage - (target.stats.get('def', 0) // 8))
                
                target.take_damage(damage)
                total_damage += damage
                
                results.append({
                    'target': target.name,
                    'damage': damage,
                    'fainted': target.is_fainted
                })
            
            self.battle_log.append(f"{action.actor.name} atmet {skill.name}!")
            
            return {
                'type': 'skill_breath',
                'skill': skill.name,
                'element': family.element.value,
                'caster': action.actor.name,
                'targets': results,
                'total_damage': total_damage
            }
            
        except Exception as e:
            logger.error(f"Error in breath skill: {str(e)}")
            return {'error': str(e)}
    
    def _get_skill_targets(self, action, battle_state, target_type: SkillTarget) -> List:
        """Get targets for a skill based on its target type."""
        targets = []
        
        try:
            if target_type == SkillTarget.SINGLE_ENEMY:
                targets = [action.target] if action.target else []
            
            elif target_type == SkillTarget.ALL_ENEMIES:
                if hasattr(battle_state, 'enable_3v3') and battle_state.enable_3v3:
                    # 3v3 mode
                    if hasattr(battle_state, 'enemy_formation'):
                        targets = [slot.monster for slot in battle_state.enemy_formation.get_active_monsters()]
                else:
                    # 1v1 mode
                    targets = [battle_state.enemy_active] if battle_state.enemy_active else []
            
            elif target_type == SkillTarget.SINGLE_ALLY:
                targets = [action.target] if action.target else [action.actor]
            
            elif target_type == SkillTarget.ALL_ALLIES:
                if hasattr(battle_state, 'enable_3v3') and battle_state.enable_3v3:
                    # 3v3 mode
                    if hasattr(battle_state, 'player_formation'):
                        targets = [slot.monster for slot in battle_state.player_formation.get_active_monsters()]
                else:
                    # 1v1 mode
                    targets = [battle_state.player_active] if battle_state.player_active else []
            
            elif target_type == SkillTarget.SELF:
                targets = [action.actor]
            
            elif target_type == SkillTarget.RANDOM_ENEMIES:
                # Get 2-4 random enemies
                all_enemies = self._get_skill_targets(action, battle_state, SkillTarget.ALL_ENEMIES)
                num_targets = min(len(all_enemies), random.randint(2, 4))
                targets = random.sample(all_enemies, num_targets) if all_enemies else []
            
            # Filter out fainted targets
            targets = [t for t in targets if t and not t.is_fainted]
            
        except Exception as e:
            logger.error(f"Error getting skill targets: {str(e)}")
            targets = []
        
        return targets
    
    def _check_status_application(self, action: BattleAction, battle_state: 'BattleState') -> Optional[str]:
        """
        Check if a move should apply status effects after damage using DQM system.
        
        Args:
            action: The attack action
            battle_state: Current battle state
            
        Returns:
            Status effect name if applied, None otherwise
        """
        try:
            # Check if move has status effect
            move = action.move
            if not move or not hasattr(move, 'status_effect'):
                return None
            
            status_effect = move.status_effect
            if not status_effect:
                return None
            
            # TODO: Status system integration - temporarily disabled
            # The DQM status system was removed during cleanup
            # This needs to be reimplemented with the new status processor
            
            target = action.target
            
            # Simple status effect application (temporary solution)
            if hasattr(status_effect, 'value'):
                status_name = status_effect.value
            else:
                status_name = str(status_effect)
            
            # TODO: Implement proper status effect system
            # For now, just log the status effect attempt
            logger.info(f"Status effect attempt: {status_name} on {target.name}")
            
            # Check accuracy for status effect
            if hasattr(move, 'status_accuracy'):
                status_accuracy = move.status_accuracy
            else:
                status_accuracy = 0.3  # Default 30% chance
            
            # Roll for status application
            import random
            if random.random() > status_accuracy:
                logger.info(f"Status effect {status_name} missed")
                return None
            
            # TODO: Apply status effect using new status processor
            # For now, just return success
            logger.info(f"Status effect {status_name} applied to {target.name}")
            return {
                'type': 'status_effect',
                'status': status_name,
                'target': target,
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Error checking status application: {e}")
            return None
