"""
Turn Processor - DQM-Authentic Implementation
============================================
Vollständige Turn-Verarbeitung mit DQM-Formeln und Speed-basierter Reihenfolge.
"""

import logging
import random
import time
from typing import Dict, Any, List, Tuple, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from engine.systems.battle.battle_state import BattleState
    from engine.systems.monster_instance import MonsterInstance
    from engine.systems.battle.turn_logic import BattleAction, ActionType
    from engine.systems.battle.event_processor import EventProcessor

from engine.systems.battle.events.event_types import EventType
from engine.systems.battle.turn_logic import ActionType

logger = logging.getLogger(__name__)


class TurnProcessor:
    """DQM-authentischer Turn Processor mit Speed-basierter Reihenfolge"""
    
    def __init__(self, battle_state: 'BattleState' = None):
        self.state = battle_state
        self.turn_count = 0
        self.action_processor = None
        self.current_turn_order: List[Tuple[int, 'BattleAction']] = []
        self.turn_history: List[Dict[str, Any]] = []
        self._rng = random.Random()
        
        logger.info("TurnProcessor initialized with DQM formulas")
    
    def set_action_processor(self, action_processor):
        """Set action processor."""
        self.action_processor = action_processor
        logger.debug("Action processor set")
    
    def calculate_turn_order(self, actions: List['BattleAction']) -> List[Tuple[int, 'BattleAction']]:
        """
        DQM Turn Order Calculation:
        1. Priority (Move priority)
        2. Speed + Random(0-255)
        3. Player advantage bei Gleichstand
        """
        turn_order = []
        
        for action in actions:
            if not action or not action.actor:
                continue
                
            # Get move priority (Quick attacks = +1, etc.)
            priority = self._get_action_priority(action)
            
            # DQM Formula: Speed + Random(0-255)
            base_speed = action.actor.stats.get('spd', 50)
            speed_roll = base_speed + self._rng.randint(0, 255)
            
            # Player gets +1 advantage bei Gleichstand
            if action.actor == self.state.player_active:
                speed_roll += 1
            
            # Store as (negative_priority, negative_speed, action) for heap
            turn_order.append((-priority, -speed_roll, action))
        
        # Sort by priority first, then speed
        turn_order.sort()
        return [(abs(speed), action) for _, speed, action in turn_order]
    
    def process_turn(self, player_action: 'BattleAction' = None, enemy_action: 'BattleAction' = None) -> Dict[str, Any]:
        """Vollständige Turn-Verarbeitung mit DQM-Regeln"""
        try:
            self.turn_count += 1
            results = {
                'turn': self.turn_count,
                'actions_executed': [],
                'battle_ended': False,
                'success': True
            }
            
            # Phase 1: TURN_START
            self._emit_turn_event(EventType.TURN_START, {'turn': self.turn_count})
            
            # Phase 2: Calculate Turn Order
            actions = [action for action in [player_action, enemy_action] if action]
            if not actions:
                logger.warning("No valid actions provided for turn")
                return {'success': False, 'error': 'No valid actions'}
            
            self.current_turn_order = self.calculate_turn_order(actions)
            
            # Phase 3: Execute Actions in Order
            for speed, action in self.current_turn_order:
                # Check if actor is still alive
                if action.actor.current_hp <= 0:
                    logger.debug(f"Skipping action for fainted {action.actor.name}")
                    continue
                
                # Check if battle already ended
                if self._check_battle_end():
                    results['battle_ended'] = True
                    break
                
                # Execute action
                action_result = self._execute_single_action(action)
                results['actions_executed'].append({
                    'actor': action.actor.name,
                    'action': action.action_type.name if hasattr(action.action_type, 'name') else str(action.action_type),
                    'result': action_result,
                    'speed': speed
                })
                
                # Check for battle end after each action
                if self._check_battle_end():
                    results['battle_ended'] = True
                    break
            
            # Phase 4: End of Turn Processing
            self._process_end_of_turn()
            
            # Phase 5: TURN_END
            self._emit_turn_event(EventType.TURN_END, {'turn': self.turn_count})
            
            # Save turn to history
            self._save_turn_to_history(results)
            
            return results
            
        except Exception as e:
            logger.error(f"Turn processing failed: {e}")
            return {'error': str(e), 'turn': self.turn_count, 'success': False}
    
    def process_multi_battle_turn(self, 
                                 player_actions: List['BattleAction'],
                                 enemy_actions: List['BattleAction']) -> Dict[str, Any]:
        """3v3 Battle Support (DQM-Style)"""
        try:
            all_actions = player_actions + enemy_actions
            turn_order = self.calculate_turn_order(all_actions)
            
            results = {
                'turn': self.turn_count + 1,
                'actions_executed': [],
                'battle_ended': False,
                'success': True
            }
            
            # Execute all actions in speed order
            for speed, action in turn_order:
                if action.actor.current_hp <= 0:
                    continue
                
                # Handle area attacks
                if action.move and hasattr(action.move, 'targeting'):
                    if action.move.targeting == 'all_enemies':
                        targets = self.state.enemy_team if action.actor in self.state.player_team else self.state.player_team
                        for target in targets:
                            if target.current_hp > 0:
                                self._execute_on_target(action, target)
                    else:
                        self._execute_single_action(action)
                else:
                    self._execute_single_action(action)
                
                if self._check_battle_end():
                    results['battle_ended'] = True
                    break
            
            return results
            
        except Exception as e:
            logger.error(f"Multi-battle turn processing failed: {e}")
            return {'error': str(e), 'success': False}
    
    def _get_action_priority(self, action: 'BattleAction') -> int:
        """Get action priority for turn order calculation."""
        if not action.move:
            return 0
        
        # Quick attacks have priority +1
        if hasattr(action.move, 'priority'):
            return action.move.priority
        
        return 0
    
    def _execute_single_action(self, action: 'BattleAction') -> Dict[str, Any]:
        """Execute a single action using the action processor."""
        try:
            if not self.action_processor:
                logger.error("No action processor available")
                return {'success': False, 'error': 'No action processor'}
            
            return self.action_processor.execute_action(action)
            
        except Exception as e:
            logger.error(f"Action execution failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _execute_on_target(self, action: 'BattleAction', target: 'MonsterInstance') -> Dict[str, Any]:
        """Execute action on specific target (for area attacks)."""
        try:
            # Create modified action with specific target
            modified_action = action
            modified_action.target = target
            return self._execute_single_action(modified_action)
            
        except Exception as e:
            logger.error(f"Target execution failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _process_end_of_turn(self):
        """Process status effects at end of turn"""
        try:
            # Process Poison/Burn damage
            for monster in [self.state.player_active, self.state.enemy_active]:
                if not monster or monster.current_hp <= 0:
                    continue
                
                if monster.status == 'poison':
                    damage = max(1, monster.max_hp // 16)  # DQM: 1/16 of max HP
                    monster.current_hp -= damage
                    self._emit_turn_event(EventType.STATUS_DAMAGE, {
                        'target': monster.name,
                        'status': 'poison',
                        'damage': damage
                    })
                
                if monster.status == 'burn':
                    damage = max(1, monster.max_hp // 8)  # Burn is worse
                    monster.current_hp -= damage
                    self._emit_turn_event(EventType.STATUS_DAMAGE, {
                        'target': monster.name,
                        'status': 'burn',
                        'damage': damage
                    })
                
                # Decrement status duration
                if hasattr(monster, 'status_turns') and monster.status_turns > 0:
                    monster.status_turns -= 1
                    if monster.status_turns == 0:
                        monster.status = None
                        self._emit_turn_event(EventType.STATUS_REMOVED, {
                            'target': monster.name,
                            'status': monster.status
                        })
                        
        except Exception as e:
            logger.error(f"End of turn processing failed: {e}")
    
    def _check_battle_end(self) -> bool:
        """Check if battle has ended."""
        try:
            if not self.state:
                return False
            
            # Check if player team is defeated
            player_alive = any(monster.current_hp > 0 for monster in self.state.player_team)
            enemy_alive = any(monster.current_hp > 0 for monster in self.state.enemy_team)
            
            return not player_alive or not enemy_alive
            
        except Exception as e:
            logger.error(f"Battle end check failed: {e}")
            return False
    
    def _emit_turn_event(self, event_type: EventType, data: Dict[str, Any]):
        """Emit turn-related event."""
        try:
            if self.state and hasattr(self.state, 'event_processor') and self.state.event_processor:
                self.state.event_processor.emit_event(event_type, data)
        except Exception as e:
            logger.error(f"Failed to emit turn event: {e}")
    
    def _save_turn_to_history(self, turn_data: Dict[str, Any]):
        """Save turn for replay/analysis"""
        try:
            self.turn_history.append({
                'turn': self.turn_count,
                'timestamp': time.time(),
                'actions': turn_data.get('actions_executed', []),
                'state_snapshot': self._create_state_snapshot()
            })
            
            # Keep only last 50 turns
            if len(self.turn_history) > 50:
                self.turn_history = self.turn_history[-50:]
                
        except Exception as e:
            logger.error(f"Failed to save turn history: {e}")
    
    def _create_state_snapshot(self) -> Dict[str, Any]:
        """Create a snapshot of current battle state."""
        try:
            return {
                'player_hp': self.state.player_active.current_hp if self.state.player_active else 0,
                'enemy_hp': self.state.enemy_active.current_hp if self.state.enemy_active else 0,
                'turn_count': self.turn_count
            }
        except Exception as e:
            logger.error(f"Failed to create state snapshot: {e}")
            return {}
    
    def get_turn_history(self) -> List[Dict[str, Any]]:
        """Get turn history for analysis."""
        return self.turn_history.copy()
    
    def reset_turn_count(self):
        """Reset turn counter."""
        self.turn_count = 0
        self.turn_history.clear()
        logger.info("Turn count reset")
