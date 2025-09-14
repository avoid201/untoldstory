"""
Attack action processing with robust error recovery - max 250 lines
Handles attack actions with triple-layer fallback mechanisms
"""

import logging
from typing import Dict, Any, TYPE_CHECKING

from engine.systems.battle.processors.action_processor_base import ActionProcessorBase
from engine.systems.battle.turn_logic import BattleAction, ActionType
from engine.systems.battle.event_processor import EventType

if TYPE_CHECKING:
    from engine.systems.battle.battle_state import BattleState
    from engine.systems.monster_instance import MonsterInstance
    from engine.systems.moves import Move

logger = logging.getLogger(__name__)


class AttackActionProcessor(ActionProcessorBase):
    """Handles attack actions with fallback mechanisms"""
    
    def can_handle(self, action: BattleAction) -> bool:
        """Check if this processor can handle attack actions"""
        # Handle both BattleAction objects and ActionType enums
        if hasattr(action, 'action_type'):
            return action.action_type == ActionType.ATTACK
        elif isinstance(action, dict):
            return action.get('action_type') == 'ATTACK'
        elif action == ActionType.ATTACK:
            return True
        return False
    
    def execute(self, action: BattleAction) -> Dict[str, Any]:
        """Execute attack with triple-layer fallback"""
        try:
            # Layer 1: Normal damage calculation with unified calculator
            return self._execute_with_calculator(action)
        except Exception as e:
            logger.warning(f"Primary calc failed: {e}, trying fallback")
            try:
                # Layer 2: Simplified calculation
                return self._execute_simple_damage(action)
            except Exception as e2:
                logger.error(f"Secondary calc failed: {e2}, using minimum")
                # Layer 3: Minimum guaranteed damage
                return self._execute_minimum_damage(action)
    
    def _execute_with_calculator(self, action: BattleAction) -> Dict[str, Any]:
        """Primary execution using unified damage calculator"""
        try:
            # Validate inputs before damage calculation
            if not action.actor or not action.target or not action.move:
                return self.create_error_result(
                    'attack', 
                    'Missing actor, target, or move',
                    damage=0, is_critical=False, effectiveness=1.0
                )
            
            # Check if target is already fainted
            if getattr(action.target, 'is_fainted', False):
                return self.create_error_result(
                    'attack',
                    'Target already fainted',
                    damage=0, is_critical=False, effectiveness=1.0
                )
            
            # Emit move announcement event
            self._emit_move_announcement(action)
            
            # Apply talent-based passive abilities before damage calculation
            self._apply_talent_passives(action)
            
            # Use unified damage calculator
            from engine.systems.unified_damage_calculator import unified_damage_calculator
            calc = unified_damage_calculator
            damage_result = calc.calculate_damage(
                attacker=action.actor,
                defender=action.target,
                move=action.move
            )
            
            # Validate damage result
            if not damage_result or not hasattr(damage_result, 'damage'):
                logger.warning("Damage calculation returned invalid result, using fallback")
                return self._execute_simple_damage(action)
            
            # Ensure damage is non-negative
            actual_damage = max(0, getattr(damage_result, 'damage', 0))
            
            # Apply damage with safety checks
            actual_damage = self.safe_hp_reduction(action.target, actual_damage)
            
            # CRITICAL: Log damage application for debugging
            logger.info(f"Damage applied: {action.actor.name} -> {action.target.name}: {actual_damage} damage (HP: {action.target.current_hp + actual_damage} -> {action.target.current_hp})")
            
            # Emit damage events
            self._emit_damage_events(action, actual_damage, damage_result)
            
            # Check if monster fainted after damage application
            monsters_fainted = 0
            if action.target.current_hp <= 0:
                print(f"[DEBUG] Monster {action.target.name} fainted! HP: {action.target.current_hp}")
                self._emit_monster_fainted_event(action.target)
                monsters_fainted = 1
            
            return self.create_success_result(
                'attack',
                getattr(damage_result, 'get_message', lambda: "Attack successful")(),
                damage=actual_damage,
                damage_dealt=actual_damage,
                monsters_fainted=monsters_fainted,
                is_critical=getattr(damage_result, 'is_critical', False),
                effectiveness=getattr(damage_result, 'effectiveness', 1.0)
            )
            
        except Exception as e:
            logger.error(f"Error in primary attack execution: {e}")
            raise  # Re-raise to trigger fallback
    
    def _execute_simple_damage(self, action: BattleAction) -> Dict[str, Any]:
        """Fallback: Simple damage formula without complex calculations"""
        try:
            base_damage = action.move.power if action.move else 40
            damage = max(1, base_damage // 2)
            
            actual_damage = self.safe_hp_reduction(action.target, damage)
            
            # Check if monster fainted after damage
            monsters_fainted = 0
            if action.target.current_hp <= 0:
                monsters_fainted = 1
            
            return self.create_success_result(
                'attack',
                'Fallback damage applied',
                damage=actual_damage,
                damage_dealt=actual_damage,
                monsters_fainted=monsters_fainted,
                is_critical=False,
                effectiveness=1.0
            )
            
        except Exception as e:
            logger.error(f"Error in simple damage calculation: {e}")
            raise  # Re-raise to trigger minimum damage fallback
    
    def _execute_minimum_damage(self, action: BattleAction) -> Dict[str, Any]:
        """Final fallback: Minimum guaranteed damage"""
        try:
            # Absolute minimum damage to ensure something happens
            damage = 1
            
            actual_damage = self.safe_hp_reduction(action.target, damage)
            
            # Check if monster fainted after damage
            monsters_fainted = 0
            if action.target.current_hp <= 0:
                monsters_fainted = 1
            
            return self.create_success_result(
                'attack',
                'Minimum damage applied',
                damage=actual_damage,
                damage_dealt=actual_damage,
                monsters_fainted=monsters_fainted,
                is_critical=False,
                effectiveness=1.0
            )
            
        except Exception as e:
            logger.error(f"Error in minimum damage calculation: {e}")
            # Ultimate fallback - return error but don't crash
            return self.create_error_result(
                'attack',
                f'All damage calculations failed: {e}',
                damage=0, is_critical=False, effectiveness=1.0
            )
    
    def _emit_move_announcement(self, action: BattleAction) -> None:
        """Emit move announcement event"""
        try:
            if hasattr(self.state, 'event_processor') and self.state.event_processor:
                self.state.event_processor.emit_event(
                    EventType.MESSAGE_SHOW,
                    {'message': f"{action.actor.name} setzt {action.move.name} ein!", 'duration': 1.5}
                )
        except Exception as e:
            logger.warning(f"Failed to emit move announcement: {e}")
    
    def _emit_damage_events(self, action: BattleAction, actual_damage: int, damage_result) -> None:
        """Emit damage-related events"""
        try:
            if not hasattr(self.state, 'event_processor') or not self.state.event_processor:
                return
            
            # HP bar update event - SOFORTIGE UI-UPDATES
            self.state.event_processor.emit_event(
                EventType.HP_BAR_UPDATE,
                {
                    'target': action.target, 
                    'old_hp': action.target.current_hp + actual_damage, 
                    'new_hp': action.target.current_hp,
                    'max_hp': action.target.max_hp,
                    'animated': True
                }
            )
            
            # Damage dealt event for damage numbers
            self.state.event_processor.emit_event(
                EventType.DAMAGE_DEALT,
                {
                    'target': action.target, 
                    'damage': actual_damage, 
                    'is_critical': getattr(damage_result, 'is_critical', False),
                    'is_super_effective': getattr(damage_result, 'effectiveness', 1.0) > 1.0,
                    'attacker': action.actor
                }
            )
            
        except Exception as e:
            logger.warning(f"Failed to emit damage events: {e}")
    
    def _emit_monster_fainted_event(self, monster: 'MonsterInstance') -> None:
        """Emit monster fainted event"""
        try:
            if hasattr(self.state, 'event_processor') and self.state.event_processor:
                self.state.event_processor.emit_event(
                    EventType.MONSTER_FAINTED,
                    {'monster': monster}
                )
                logger.debug(f"Monster fainted event emitted for {monster.name}")
        except Exception as e:
            logger.warning(f"Failed to emit monster fainted event: {e}")
    
    def _apply_talent_passives(self, action: BattleAction) -> None:
        """Apply passive abilities from talents before action execution"""
        try:
            # Get talent database
            from engine.systems.talent_system import get_talent_database
            talent_db = get_talent_database()
            
            # Apply passive abilities from attacker's talents
            if hasattr(action.actor, 'talents') and action.actor.talents:
                for talent_instance in action.actor.talents:
                    if not talent_instance.is_learned:
                        continue
                        
                    talent_data = talent_db.get_talent(talent_instance.talent_id)
                    if not talent_data:
                        continue
                    
                    # Get passive abilities for current tier
                    passive_abilities = talent_data.get_passive_abilities_for_tier(talent_instance.current_tier)
                    
                    # Apply each passive ability
                    for ability in passive_abilities:
                        ability_type = ability.get('effect_type', '')
                        value = ability.get('value', 1.0)
                        
                        if ability_type == 'stat_boost':
                            # Apply stat boosts to monster
                            stat_type = ability.get('stat', '')
                            if stat_type and hasattr(action.actor, 'stats'):
                                current_value = action.actor.stats.get(stat_type, 0)
                                action.actor.stats[stat_type] = int(current_value * value)
                        
                        elif ability_type == 'move_power_boost':
                            # Apply move power boost
                            if action.move and hasattr(action.move, 'power'):
                                action.move.power = int(action.move.power * value)
                        
                        elif ability_type == 'accuracy_boost':
                            # Apply accuracy boost
                            if action.move and hasattr(action.move, 'accuracy'):
                                action.move.accuracy = min(100, int(action.move.accuracy * value))
                        
                        elif ability_type == 'crit_boost':
                            # Apply critical hit boost
                            if hasattr(action.actor, 'crit_rate'):
                                action.actor.crit_rate = min(100, int(action.actor.crit_rate * value))
            
        except Exception as e:
            logger.error(f"Error applying talent passives: {e}")
