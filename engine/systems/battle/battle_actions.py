"""
Battle Actions Module
Handles execution of all battle actions
"""

import logging
import random
from typing import Dict, Any, Optional, List
from engine.systems.monster_instance import MonsterInstance, StatusCondition
from engine.systems.battle.turn_logic import BattleAction, ActionType
from engine.systems.battle.battle_effects import ItemEffectHandler
from engine.systems.battle.damage_calc import DamageCalculationPipeline
from engine.systems.battle.skills_dqm import (
    get_skill_database, SkillType, SkillElement, SkillTarget
)
from engine.systems.battle.dqm_formulas import DQMCalculator

logger = logging.getLogger(__name__)


class BattleActionExecutor:
    """Executes battle actions."""
    
    def __init__(self):
        """Initialize action executor."""
        self.damage_pipeline = DamageCalculationPipeline()
        self.item_effects = ItemEffectHandler()
        self.skill_database = get_skill_database()
        self.battle_log: List[str] = []
    
    def execute_action(self, action: BattleAction, battle_state: 'BattleState') -> Optional[Dict[str, Any]]:
        """
        Execute a single battle action.
        
        Args:
            action: The action to execute
            battle_state: Current battle state
            
        Returns:
            Result of the action or None on error
        """
        try:
            if action.action_type == ActionType.ATTACK:
                return self._execute_attack(action, battle_state)
            elif action.action_type == ActionType.TAME:
                return self._execute_tame(action, battle_state)
            elif action.action_type == ActionType.ITEM:
                return self._execute_item(action, battle_state)
            elif action.action_type == ActionType.SWITCH:
                return self._execute_switch(action, battle_state)
            elif action.action_type == ActionType.FLEE:
                return self._execute_flee(action, battle_state)
            elif action.action_type == ActionType.SKILL:
                return self._execute_skill(action, battle_state)
            else:
                logger.error(f"Unknown action type: {action.action_type}")
                return None
                
        except Exception as e:
            logger.error(f"Error executing action: {str(e)}")
            return None
    
    def _execute_attack(self, action: BattleAction, battle_state: 'BattleState') -> Dict[str, Any]:
        """Execute an attack action."""
        try:
            # Calculate damage
            try:
                # Create context for damage pipeline
                context = {
                    'attacker': action.actor,
                    'defender': action.target,
                    'move': action.move,
                    'rng': random,
                    'result': type('obj', (object,), {
                        'damage': 0,
                        'missed': False,
                        'blocked': False,
                        'is_critical': False,
                        'effectiveness': 1.0,
                        'type_text': ''
                    })()
                }
                
                # Apply tension multiplier if available
                if hasattr(battle_state, 'tension_manager'):
                    multiplier = battle_state.tension_manager.get_multiplier(action.actor)
                    context['tension_multiplier'] = multiplier
                
                damage_result = self.damage_pipeline.execute(context)
                damage = damage_result.damage
                
                # Reset tension after attack if applicable
                if hasattr(battle_state, 'tension_manager') and damage > 0:
                    battle_state.tension_manager.reset_tension(action.actor)
                    
            except Exception as e:
                logger.warning(f"Error calculating damage, using fallback: {str(e)}")
                # Fallback: Simple damage calculation
                damage = max(1, action.move.power // 2)
            
            # Apply damage
            action.target.take_damage(damage)
            
            # Log the attack
            self.battle_log.append(f"{action.actor.name} greift {action.target.name} an!")
            
            return {
                'type': 'attack',
                'attacker': action.actor.name,
                'target': action.target.name,
                'damage': damage,
                'target_fainted': action.target.is_fainted
            }
            
        except Exception as e:
            logger.error(f"Error executing attack: {str(e)}")
            return {'error': str(e)}
    
    def _execute_tame(self, action: BattleAction, battle_state: 'BattleState') -> Dict[str, Any]:
        """Execute a taming action."""
        try:
            # Calculate taming chance
            tame_chance = self._calculate_tame_chance(action.actor, action.target)
            
            # Roll for taming success
            success = random.random() < tame_chance
            
            if success:
                self.battle_log.append(f"{action.target.name} wurde erfolgreich gezähmt!")
                return {
                    'type': 'tame',
                    'success': True,
                    'monster': action.target.name
                }
            else:
                self.battle_log.append(f"Taming von {action.target.name} fehlgeschlagen!")
                return {
                    'type': 'tame',
                    'success': False,
                    'monster': action.target.name
                }
                
        except Exception as e:
            logger.error(f"Error executing taming: {str(e)}")
            return {'error': str(e)}
    
    def _execute_item(self, action: BattleAction, battle_state: 'BattleState') -> Dict[str, Any]:
        """Execute an item usage action."""
        try:
            result = self.item_effects.execute_item_effect(
                item=action.item,
                target=action.target,
                user=action.actor
            )
            
            self.battle_log.append(f"{action.actor.name} benutzt {action.item.name}!")
            
            return {
                'type': 'item',
                'user': action.actor.name,
                'item': action.item.name,
                'target': action.target.name,
                'effect': result
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
            # Use DQM escape formula
            dqm_calc = DQMCalculator()
            runner_stats = {'spd': player_speed}
            enemy_stats = {'spd': enemy_speed}
            
            escape_chance = dqm_calc.calculate_escape_chance(
                runner_stats=runner_stats,
                enemy_stats=enemy_stats,
                escape_attempts=escape_attempts
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
    
    def _calculate_tame_chance(self, tamer: MonsterInstance, target: MonsterInstance) -> float:
        """Calculate taming chance based on various factors."""
        try:
            if not tamer or not target:
                return 0.0
            
            # Base chance
            base_chance = 0.3  # 30%
            
            # Level difference (higher level = better chance)
            level_bonus = 0.0
            if hasattr(tamer, 'level') and hasattr(target, 'level'):
                level_diff = tamer.level - target.level
                level_bonus = min(0.4, max(-0.2, level_diff * 0.02))
            
            # HP difference (lower HP = better chance)
            hp_bonus = 0.0
            if hasattr(target, 'current_hp') and hasattr(target, 'max_hp'):
                hp_percent = target.current_hp / max(1, target.max_hp)
                hp_bonus = (1.0 - hp_percent) * 0.3  # 0% HP = +30%, 100% HP = +0%
            
            # Type compatibility
            type_bonus = 0.0
            if hasattr(tamer, 'types') and hasattr(target, 'types'):
                # Simple type compatibility
                if tamer.types and target.types:
                    if any(t in target.types for t in tamer.types):
                        type_bonus = 0.1  # Same types = +10%
            
            # Status effects
            status_bonus = 0.0
            if hasattr(target, 'status') and target.status != StatusCondition.NORMAL:
                if target.status in [StatusCondition.SLEEP, StatusCondition.FROZEN, StatusCondition.PARALYSIS]:
                    status_bonus = 0.15  # Status effects = +15%
            
            # Calculate final chance
            final_chance = base_chance + level_bonus + hp_bonus + type_bonus + status_bonus
            
            # Clamp to 0.0 to 0.95
            return max(0.0, min(0.95, final_chance))
            
        except Exception as e:
            logger.error(f"Error calculating taming chance: {str(e)}")
            return 0.3  # Fallback: 30%
    
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
            if command == 'meditate':
                return self._execute_meditate(monster)
            elif command == 'intimidate':
                return self._execute_intimidate(monster, battle_state.enemy_active)
            else:
                logger.warning(f"Unknown special command: {command}")
                return {'error': f'Unknown command: {command}'}
                
        except Exception as e:
            logger.error(f"Error executing special command: {str(e)}")
            return {'error': str(e)}
    
    def _execute_meditate(self, monster: MonsterInstance) -> Dict[str, Any]:
        """Execute MEDITATE command - restore MP and increase special stats."""
        try:
            if not monster:
                return {'error': 'No monster for MEDITATE'}
            
            # Check if monster has MP
            if hasattr(monster, 'current_mp') and hasattr(monster, 'max_mp'):
                current_mp = monster.current_mp
                max_mp = monster.max_mp
                
                if current_mp < max_mp:
                    # Restore MP (50% of max MP)
                    restore_amount = max(1, max_mp // 2)
                    monster.current_mp = min(max_mp, current_mp + restore_amount)
                    
                    self.battle_log.append(f"{monster.name} meditiert und stellt {restore_amount} MP wieder her!")
                    
                    return {
                        'action': 'meditate_success',
                        'message': f"{monster.name} meditiert und stellt {restore_amount} MP wieder her!",
                        'mp_restored': restore_amount,
                        'current_mp': monster.current_mp,
                        'max_mp': max_mp,
                        'monster': monster.name
                    }
                else:
                    return {
                        'action': 'meditate_failed',
                        'message': f"{monster.name} hat bereits volle MP!",
                        'monster': monster.name
                    }
            else:
                # Fallback: Increase stats
                return {
                    'action': 'meditate_no_effect',
                    'message': f"{monster.name} meditiert, aber es hat keine Wirkung!",
                    'monster': monster.name
                }
                    
        except Exception as e:
            logger.error(f"Error in MEDITATE: {str(e)}")
            return {'error': str(e)}
    
    def _execute_intimidate(self, monster: MonsterInstance, target: MonsterInstance) -> Dict[str, Any]:
        """Execute INTIMIDATE command - lower enemy stats."""
        try:
            if not monster or not target:
                return {'error': 'Missing monster or target for INTIMIDATE'}
            
            # Calculate success chance (based on level difference)
            success_chance = 0.7  # 70% base chance
            if hasattr(monster, 'level') and hasattr(target, 'level'):
                level_diff = monster.level - target.level
                success_chance = min(0.95, max(0.3, success_chance + level_diff * 0.05))
            
            # Roll for success
            success = random.random() < success_chance
            
            if success:
                # Lower enemy stats
                stats_lowered = []
                
                # Use stat_stages if available
                if hasattr(target, 'stat_stages'):
                    if 'atk' in target.stat_stages:
                        target.stat_stages['atk'] = max(-6, target.stat_stages['atk'] - 1)
                        stats_lowered.append('Attack')
                    if 'def' in target.stat_stages:
                        target.stat_stages['def'] = max(-6, target.stat_stages['def'] - 1)
                        stats_lowered.append('Defense')
                
                if stats_lowered:
                    self.battle_log.append(f"{monster.name} schüchtert {target.name} ein! {', '.join(stats_lowered)} gesenkt!")
                    
                    return {
                        'action': 'intimidate_success',
                        'message': f"{monster.name} schüchtert {target.name} ein!",
                        'stats_lowered': stats_lowered,
                        'target': target.name,
                        'monster': monster.name
                    }
                else:
                    return {
                        'action': 'intimidate_no_effect',
                        'message': f"{monster.name} schüchtert {target.name} ein, aber es hat keine Wirkung!",
                        'target': target.name,
                        'monster': monster.name
                    }
            else:
                return {
                    'action': 'intimidate_failed',
                    'message': f"{monster.name} versucht {target.name} einzuschüchtern, aber es misslingt!",
                    'target': target.name,
                    'monster': monster.name
                }
                
        except Exception as e:
            logger.error(f"Error in INTIMIDATE: {str(e)}")
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
