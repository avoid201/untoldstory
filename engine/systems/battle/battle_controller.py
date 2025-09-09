"""
Battle Controller - Central Battle Coordination
Handles high-level battle flow and coordination.
Integrates turn logic and action validation.
"""

import logging
from typing import List, Optional, Dict, Any, Callable, TYPE_CHECKING

from engine.systems.monster_instance import MonsterInstance
from engine.systems.battle.battle_enums import BattleType, BattlePhase, BattleResult
from engine.systems.battle.battle_state import BattleState
from engine.systems.battle.turn_logic import BattleAction, ActionType, TurnOrder
from engine.systems.battle.event_processor import EventType
from engine.systems.unified_damage_calculator import unified_damage_calculator
from engine.systems.talent_system import get_talent_database

if TYPE_CHECKING:
    from engine.systems.battle.turn_processor import TurnProcessor
    from engine.systems.battle.action_processor import ActionProcessor
    from engine.systems.battle.event_processor import EventProcessor
    from engine.systems.battle.status_processor import StatusProcessor
    from engine.systems.conditions import StatusCondition

logger = logging.getLogger(__name__)


class BattleController:
    """
    Central battle coordination class.
    Handles high-level battle flow and integrates turn logic with action validation.
    """
    
    def __init__(self, 
                 player_team: List[MonsterInstance],
                 enemy_team: List[MonsterInstance],
                 battle_type: BattleType = BattleType.WILD,
                 can_flee: bool = True,
                 can_catch: bool = True):
        """Initialize battle controller with battle state and turn order system."""
        
        # Create battle state
        self.state = BattleState(
            player_team=player_team,
            enemy_team=enemy_team,
            battle_type=battle_type,
            can_flee=can_flee,
            can_catch=can_catch
        )
        
        # Initialize turn order system
        self.turn_order = TurnOrder()
        
        # Initialize specialized managers (will be injected by other agents)
        self.turn_processor: Optional['TurnProcessor'] = None
        self.action_processor: Optional['ActionProcessor'] = None
        self.event_processor: Optional['EventProcessor'] = None
        self.status_processor: Optional['StatusProcessor'] = None
        self.ui_sync_callback: Optional[Callable] = None  # FIX: Add missing callback
        
        # Talent System Integration
        self.talent_database = get_talent_database()
        
        # FIXED: Auto-create managers if not injected
        self._auto_initialize_managers()
        
        logger.info(f"BattleController initialized for {battle_type.value} battle")
    
    def set_managers(self, 
                    turn_processor: 'TurnProcessor',
                    action_processor: 'ActionProcessor',
                    event_processor: 'EventProcessor',
                    status_processor: 'StatusProcessor'):
        """Inject specialized managers (called by battle scene setup)."""
        self.turn_processor = turn_processor
        self.action_processor = action_processor
        self.event_processor = event_processor
        self.status_processor = status_processor
        
        # Connect processors
        if self.turn_processor and self.action_processor:
            self.turn_processor.set_action_processor(self.action_processor)
        
        logger.info("Specialized managers injected into BattleController")
    
    def _auto_initialize_managers(self) -> None:
        """Auto-create AND properly connect managers."""
        try:
            # Import all managers
            from engine.systems.battle.event_processor import EventProcessor
            from engine.systems.battle.action_processor import ActionProcessor
            from engine.systems.battle.turn_processor import TurnProcessor
            from engine.systems.battle.status_processor import StatusProcessor
            
            # 1. Create EventProcessor FIRST (most important)
            if not self.event_processor:
                self.event_processor = EventProcessor(self.state)
                logger.info("✓ EventProcessor created")
            
            # 2. Create others
            if not self.action_processor:
                self.action_processor = ActionProcessor(self.state)
                logger.info("✓ ActionProcessor created")
            
            if not self.turn_processor:
                self.turn_processor = TurnProcessor(self.state)
                logger.info("✓ TurnProcessor created")
            
            if not self.status_processor:
                self.status_processor = StatusProcessor(self.state)
                logger.info("✓ StatusProcessor created")
            
            # 3. CRITICAL CONNECTIONS
            if self.turn_processor and self.action_processor:
                self.turn_processor.set_action_processor(self.action_processor)
                logger.info("✓ TurnProcessor ← ActionProcessor connected")
            
            # 4. CRITICAL: Connect EventProcessor to battle state
            if self.event_processor:
                self.state.event_processor = self.event_processor
                logger.info("✓ EventProcessor connected to BattleState")
            
            # CRITICAL: Verbinde EventProcessor mit BattleState
            if self.event_processor and self.state:
                self.state.event_processor = self.event_processor
                logger.info("✓ EventProcessor connected to BattleState")
            
            # 5. Verify all set
            if not all([self.event_processor, self.action_processor, 
                       self.turn_processor, self.status_processor]):
                raise RuntimeError("Failed to initialize all managers!")
                
            logger.info("✓✓✓ All managers initialized and connected!")
            
        except Exception as e:
            logger.error(f"❌ CRITICAL: Manager initialization failed: {e}")
            raise
    
    def initialize(self, player_team: List[MonsterInstance], enemy_team: List[MonsterInstance]) -> Dict[str, Any]:
        """
        Initialize battle with teams.
        
        Args:
            player_team: List of player monsters
            enemy_team: List of enemy monsters
            
        Returns:
            Dict with initialization result
        """
        try:
            # Update state with teams
            self.state.player_team = player_team
            self.state.enemy_team = enemy_team
            
            # Set active monsters
            if player_team:
                self.state.player_active = player_team[0]
            if enemy_team:
                self.state.enemy_active = enemy_team[0]
            
            # Initialize turn order
            self.turn_order.clear()
            
            # Set initial phase
            self.state.phase = BattlePhase.START
            self.state.turn_count = 0
            self.state.battle_ended = False
            self.state.battle_result = None
            
            # FIXED: Automatischer Übergang START → INPUT nach Initialisierung
            self._transition_to_input_phase()
            
            logger.info(f"Battle initialized: {len(player_team)} vs {len(enemy_team)}")
            
            return {
                "success": True,
                "player_active": self.state.player_active.name if self.state.player_active else None,
                "enemy_active": self.state.enemy_active.name if self.state.enemy_active else None,
                "phase": self.state.phase.value
            }
            
        except Exception as e:
            logger.error(f"Fehler bei Battle-Initialisierung: {e}")
            return {"success": False, "error": str(e)}
    
    def get_player_monster(self) -> Optional[MonsterInstance]:
        """Get current active player monster."""
        return self.state.player_active
    
    def get_enemy_monster(self) -> Optional[MonsterInstance]:
        """Get current active enemy monster."""
        return self.state.enemy_active
    
    def execute_turn(self, player_action, enemy_action) -> Dict[str, Any]:
        """
        Execute a complete turn with player and enemy actions.
        AGENT 4: Implements proper phase transitions: INPUT → EXECUTION → AFTERMATH → INPUT
        
        Args:
            player_action: Player action (BattleAction or dict)
            enemy_action: Enemy action (BattleAction or dict)
            
        Returns:
            Dict with turn execution result
        """
        try:
            # AGENT 4: Transition to EXECUTION phase when turn starts
            if self.state.phase == BattlePhase.INPUT:
                self._transition_to_execution_phase()
            
            # Convert to BattleAction if needed
            if isinstance(player_action, dict):
                player_battle_action = self._create_battle_action(player_action, is_player=True)
            else:
                player_battle_action = player_action
                
            if isinstance(enemy_action, dict):
                enemy_battle_action = self._create_battle_action(enemy_action, is_player=False)
            else:
                enemy_battle_action = enemy_action
            
            # Validate actions
            if not player_battle_action:
                logger.warning("Ungültige Player-Action: Failed to create BattleAction")
                return {"success": False, "error": "Invalid player action"}
            
            if not enemy_battle_action:
                logger.warning("Ungültige Enemy-Action: Failed to create BattleAction")
                return {"success": False, "error": "Invalid enemy action"}
            
            # FIXED: Events werden NUR im TurnProcessor emittiert
            # Keine doppelten Event-Emissionen mehr
            
            # Use TurnProcessor for proper turn execution
            if self.turn_processor:
                actions = [player_battle_action, enemy_battle_action]
                # CRITICAL FIX: Ensure actions are properly queued
                self.turn_processor.turn_order.clear()
                for action in actions:
                    self.turn_processor.turn_order.add_action(action)
                battle_result = self.turn_processor.execute_turn(actions)
                
                # AGENT 4: Transition to AFTERMATH phase after execution
                self._transition_to_aftermath_phase()
                
                # Update state with result
                if battle_result != BattleResult.ONGOING:
                    self.state.battle_ended = True
                    self.state.battle_result = battle_result
                else:
                    # AGENT 4: If battle continues, transition back to INPUT phase
                    self._transition_aftermath_to_input()
                
                # FIXED: TURN_END Events werden NUR im TurnProcessor emittiert
                # Keine doppelten Event-Emissionen mehr
                
                # CRITICAL FIX: Sync state with UI after turn execution
                if hasattr(self, 'ui_sync_callback') and self.ui_sync_callback:
                    self.ui_sync_callback({
                        'battle_state': self.state,
                        'player_active': self.state.player_active,
                        'enemy_active': self.state.enemy_active,
                        'battle_ended': self.state.battle_ended,
                        'battle_result': battle_result.value if battle_result else None
                    })
                
                return {
                    "success": True,
                    "turn": self.state.turn_count,
                    "phase": self.state.phase.value,
                    "battle_ended": self.state.battle_ended,
                    "battle_result": self.state.battle_result.value if self.state.battle_result else None,
                    "result": {"battle_result": battle_result.value if battle_result else None}
                }
            else:
                # Fallback to old method
                self.turn_order.add_action(player_battle_action)
                self.turn_order.add_action(enemy_battle_action)
                result = self._execute_actions()
                self.state.turn_count += 1
                
                # AGENT 4: Apply phase transitions in fallback mode too
                self._transition_to_aftermath_phase()
                if not self.state.battle_ended:
                    self._transition_aftermath_to_input()
                
                return {
                    "success": True,
                    "turn": self.state.turn_count,
                    "phase": self.state.phase.value,
                    "battle_ended": self.state.battle_ended,
                    "battle_result": self.state.battle_result.value if self.state.battle_result else None,
                    "result": result
                }
            
        except Exception as e:
            logger.error(f"Fehler bei Turn-Ausführung: {e}")
            return {"success": False, "error": str(e)}
    
    def get_state_info(self, detail_level: str = 'full') -> Dict[str, Any]:
        """
        CONSOLIDATED STATE GETTER - Single source of truth for all state information.
        Replaces get_battle_state(), get_battle_status(), and get_current_phase_info().
        
        Args:
            detail_level: 'minimal', 'basic', 'full', 'complete'
                - minimal: Just phase and turn
                - basic: Phase, turn, active monsters
                - full: All battle data
                - complete: All data including logs and rewards
        
        Returns:
            Dict with battle state information
        """
        try:
            # Base information (always included)
            base_info = {
                "phase": self.state.phase.value,
                "turn": self.state.turn_count,
                "battle_ended": self.state.battle_ended,
                "battle_result": self.state.battle_result.value if self.state.battle_result else None
            }
            
            # Minimal level - just return base
            if detail_level == 'minimal':
                return base_info
            
            # Basic level - add active monsters
            if detail_level in ['basic', 'full', 'complete']:
                base_info.update({
                    "player_active": self._get_monster_info(self.state.player_active),
                    "enemy_active": self._get_monster_info(self.state.enemy_active),
                    "waiting_for_input": self.state.waiting_for_input,
                    "is_player_turn": self.state.phase == BattlePhase.INPUT,
                    "is_execution": self.state.phase == BattlePhase.EXECUTION,
                    "is_aftermath": self.state.phase == BattlePhase.AFTERMATH
                })
            
            # Full level - add battle configuration
            if detail_level in ['full', 'complete']:
                base_info.update({
                    "battle_type": self.state.battle_type.value,
                    "can_flee": self.state.can_flee,
                    "can_catch": self.state.can_catch
                })
            
            # Complete level - add logs and rewards
            if detail_level == 'complete':
                base_info.update({
                    "battle_log": self.state.battle_log[-10:],  # Last 10 messages
                    "exp_earned": self.state.exp_earned,
                    "money_earned": self.state.money_earned,
                    "items_earned": self.state.items_earned,
                    "player_team": [self._get_monster_info(monster) for monster in self.state.player_team],
                    "enemy_team": [self._get_monster_info(monster) for monster in self.state.enemy_team]
                })
            
            return base_info
            
        except Exception as e:
            logger.error(f"Error getting state info: {e}")
            return {"error": str(e)}
    
    def _get_monster_info(self, monster) -> Dict[str, Any]:
        """Helper method to get monster information."""
        if not monster:
            return None
        
        return {
            "name": monster.name,
            "hp": monster.current_hp,
            "max_hp": monster.max_hp,
            "status": getattr(monster, 'status_condition', None),
            "level": getattr(monster, 'level', 1),
            "is_fainted": getattr(monster, 'is_fainted', False)
        }
    
    
    def start_battle(self) -> Dict[str, Any]:
        """
        Start the battle - pure coordination.
        Delegates to turn_processor for initialization.
        """
        if not self.turn_processor:
            raise RuntimeError("TurnProcessor not set - call set_managers() first")
        
        logger.info("Starting battle")
        
        # Delegate to turn processor
        result = self.turn_processor.initialize_battle(self.state)
        
        return {
            "player_active": self.state.player_active.name if self.state.player_active else None,
            "enemy_active": self.state.enemy_active.name if self.state.enemy_active else None,
            "battle_type": self.state.battle_type.value,
            "turn": self.state.turn_count,
            "phase": self.state.phase.value,
            "result": result
        }
    
    def process_player_input(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process player input - pure coordination.
        Delegates to action_processor for execution.
        """
        if not self.action_processor:
            raise RuntimeError("ActionProcessor not set - call set_managers() first")
        
        logger.info(f"Processing player input: {action.get('type', 'unknown')}")
        
        # Delegate to action processor
        result = self.action_processor.process_player_action(self.state, action)
        
        return {
            "result": result,
            "phase": self.state.phase.value,
            "turn": self.state.turn_count,
            "battle_ended": self.state.battle_ended,
            "battle_result": self.state.battle_result.value if self.state.battle_result else None
        }
    
    def process_enemy_turn(self) -> Dict[str, Any]:
        """
        Process enemy turn - pure coordination.
        Delegates to turn_processor for enemy AI decisions.
        """
        if not self.turn_processor:
            raise RuntimeError("TurnProcessor not set - call set_managers() first")
        
        logger.info("Processing enemy turn")
        
        # Delegate to turn processor
        result = self.turn_processor.process_enemy_turn(self.state)
        
        return {
            "result": result,
            "phase": self.state.phase.value,
            "turn": self.state.turn_count,
            "battle_ended": self.state.battle_ended,
            "battle_result": self.state.battle_result.value if self.state.battle_result else None
        }
    
    
    def get_available_actions(self) -> List[str]:
        """
        Get available actions for current phase - pure data access.
        Returns available actions based on current state.
        """
        if self.state.phase != BattlePhase.INPUT:
            return []
        
        actions = ["attack", "switch", "item"]
        
        if self.state.can_flee:
            actions.append("flee")
        
        return actions
    
    def get_available_moves_for_monster(self, monster: MonsterInstance) -> List[Dict[str, Any]]:
        """
        Get available moves for a monster based on its talents.
        
        Args:
            monster: Monster to get moves for
            
        Returns:
            List of move dictionaries with talent information
        """
        try:
            if not monster or not hasattr(monster, 'talents'):
                return []
            
            available_moves = []
            
            # Get moves from all learned talents
            for talent_instance in monster.talents:
                if not talent_instance.is_learned:
                    continue
                
                talent = self.talent_database.get_talent(talent_instance.talent_id)
                if not talent:
                    continue
                
                # Get moves for current talent tier and monster level
                move_ids = talent.get_moves_for_tier(
                    talent_instance.current_tier,
                    monster.level
                )
                
                for move_id in move_ids:
                    move = self.talent_database.create_move_from_talent_data(move_id)
                    if move:
                        move_info = {
                            'id': move.id,
                            'name': move.name,
                            'type': move.type,
                            'category': move.category.value,
                            'power': move.power,
                            'accuracy': move.accuracy,
                            'description': move.description,
                            'talent_id': talent_instance.talent_id,
                            'talent_name': talent.name,
                            'talent_tier': talent_instance.current_tier.value
                        }
                        available_moves.append(move_info)
            
            return available_moves
            
        except Exception as e:
            logger.error(f"Error getting available moves for monster {monster.name}: {e}")
            return []
    
    def get_passive_abilities_for_monster(self, monster: MonsterInstance) -> List[Dict[str, Any]]:
        """
        Get passive abilities for a monster based on its talents.
        
        Args:
            monster: Monster to get passive abilities for
            
        Returns:
            List of passive ability dictionaries
        """
        try:
            if not monster or not hasattr(monster, 'talents'):
                return []
            
            passive_abilities = []
            
            # Get passive abilities from all learned talents
            for talent_instance in monster.talents:
                if not talent_instance.is_learned:
                    continue
                
                talent = self.talent_database.get_talent(talent_instance.talent_id)
                if not talent:
                    continue
                
                # Get passive abilities for current talent tier
                talent_passives = talent.get_passive_abilities_for_tier(talent_instance.current_tier)
                passive_abilities.extend(talent_passives)
            
            return passive_abilities
            
        except Exception as e:
            logger.error(f"Error getting passive abilities for monster {monster.name}: {e}")
            return []
    
    def can_monster_use_move(self, monster: MonsterInstance, move_id: str) -> bool:
        """
        Check if a monster can use a specific move based on its talents.
        
        Args:
            monster: Monster to check
            move_id: Move ID to check
            
        Returns:
            True if monster can use the move
        """
        try:
            if not monster or not hasattr(monster, 'talents'):
                return False
            
            # Check if move is available through any learned talent
            for talent_instance in monster.talents:
                if not talent_instance.is_learned:
                    continue
                
                talent = self.talent_database.get_talent(talent_instance.talent_id)
                if not talent:
                    continue
                
                move_ids = talent.get_moves_for_tier(
                    talent_instance.current_tier,
                    monster.level
                )
                
                if move_id in move_ids:
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking if monster can use move {move_id}: {e}")
            return False
    
    def is_battle_over(self) -> bool:
        """Check if battle is over - pure data access."""
        return self.state.battle_ended
    
    def get_battle_result(self) -> Optional[BattleResult]:
        """Get battle result - pure data access."""
        return self.state.battle_result
    
    def process_battle_end_rewards(self) -> Dict[str, Any]:
        """
        Process rewards and experience after battle ends.
        Includes Talent-EXP for all participating monsters.
        
        Returns:
            Dictionary with reward details and talent upgrades
        """
        try:
            if not self.state.battle_ended:
                return {"error": "Battle not ended yet"}
            
            rewards = {
                "battle_result": self.state.battle_result.value if self.state.battle_result else None,
                "talent_upgrades": [],
                "monster_rewards": [],
                "passive_abilities_gained": []
            }
            
            # Determine victory bonus
            victory_bonus = 2.0 if self.state.battle_result == BattleResult.VICTORY else 1.0
            
            # Process rewards for player team
            for monster in self.state.player_team:
                if monster.participated:
                    # Create battle result data for talent EXP
                    battle_result_data = {
                        'base_talent_exp': 15,  # Base EXP per battle
                        'participation_bonus': 1.2,  # Bonus for participating
                        'victory_bonus': victory_bonus,
                        'battle_type': self.state.battle_type.value,
                        'turn_count': self.state.turn_count
                    }
                    
                    # Gain talent experience
                    talent_upgrades = monster.gain_talent_experience_from_battle(battle_result_data)
                    
                    if talent_upgrades:
                        rewards["talent_upgrades"].extend(talent_upgrades)
                    
                    # Check for new passive abilities gained
                    new_passive_abilities = self.get_passive_abilities_for_monster(monster)
                    if new_passive_abilities:
                        rewards["passive_abilities_gained"].extend([
                            {
                                'monster_name': monster.name,
                                'ability_name': ability['name'],
                                'talent_id': ability['talent_id'],
                                'description': ability['description']
                            }
                            for ability in new_passive_abilities
                        ])
                    
                    # Store monster rewards
                    monster_reward = {
                        'monster_name': monster.name,
                        'species': monster.species_name,
                        'level': monster.level,
                        'talent_upgrades': len(talent_upgrades),
                        'new_moves': [],
                        'passive_abilities': len(new_passive_abilities)
                    }
                    
                    # Collect new moves from upgrades
                    for upgrade in talent_upgrades:
                        monster_reward['new_moves'].extend(upgrade.get('new_moves', []))
                    
                    rewards["monster_rewards"].append(monster_reward)
            
            logger.info(f"Battle rewards processed: {len(rewards['talent_upgrades'])} talent upgrades, {len(rewards['passive_abilities_gained'])} passive abilities")
            return rewards
            
        except Exception as e:
            logger.error(f"Error processing battle end rewards: {e}")
            return {"error": str(e)}
    
    def get_talent_exp_reward(self, monster: 'MonsterInstance', base_exp: int, 
                            victory_bonus: float = 1.0) -> int:
        """
        Calculate talent EXP reward for a monster.
        
        Args:
            monster: Monster receiving talent EXP
            base_exp: Base experience points
            victory_bonus: Victory bonus multiplier
            
        Returns:
            Talent EXP reward
        """
        try:
            if not monster or not hasattr(monster, 'talents'):
                return 0
            
            # Base talent EXP is 10% of monster EXP
            talent_exp = int(base_exp * 0.1 * victory_bonus)
            
            # Apply talent-specific bonuses
            for talent_instance in monster.talents:
                if hasattr(talent_instance, 'talent_id'):
                    talent_data = self.talent_database.get_talent(talent_instance.talent_id)
                    if talent_data:
                        exp_bonus = talent_data.get('exp_bonus', 1.0)
                        talent_exp = int(talent_exp * exp_bonus)
            
            return max(1, talent_exp)
            
        except Exception as e:
            logger.error(f"Error calculating talent EXP reward: {e}")
            return 0
    
    def validate_action(self, action_data: Dict[str, Any], is_player: bool = True, detailed: bool = False):
        """
        CONSOLIDATED ACTION VALIDATION - Single source of truth.
        Replaces _validate_action() and validate_action_with_errors().
        
        Args:
            action_data: Action data to validate
            is_player: Whether this is a player action
            detailed: If True, returns detailed error information
            
        Returns:
            If detailed=False: bool (is_valid)
            If detailed=True: dict with 'valid', 'errors', 'warnings' keys
        """
        from engine.systems.battle.battle_validation import BattleValidator
        return BattleValidator.validate_action_complete(action_data, self.state, is_player, detailed)
    
    def _create_battle_action(self, action_data: Dict[str, Any], is_player: bool) -> Optional[BattleAction]:
        """
        Create BattleAction from action data.
        DELEGATED: Use turn_logic.create_action_from_dict for consistency.
        
        Args:
            action_data: Action data
            is_player: Whether this is a player action
            
        Returns:
            BattleAction or None if creation fails
        """
        try:
            from engine.systems.battle.turn_logic import create_action_from_dict
            
            actor = self.state.player_active if is_player else self.state.enemy_active
            if not actor:
                logger.error(f"No active monster for {'player' if is_player else 'enemy'}")
                return None
            
            # Use centralized action creation
            return create_action_from_dict(
                action_dict=action_data,
                actor=actor,
                target=action_data.get('target'),
                move=action_data.get('move')
            )
            
        except Exception as e:
            logger.error(f"Fehler beim Erstellen der BattleAction: {e}")
            return None
    
    def _execute_actions(self) -> Dict[str, Any]:
        """
        Execute all actions in turn order.
        DELEGATED: Use ActionProcessor for all action execution.
        
        Returns:
            Dict with execution result
        """
        try:
            if not self.action_processor:
                logger.error("No ActionProcessor available for execution")
                return {'error': 'No ActionProcessor available'}
            
            # Sort actions by priority and speed
            sorted_actions = self.turn_order.sort_actions()
            
            results = []
            for action in sorted_actions:
                # Delegate to ActionProcessor
                result = self.action_processor.execute_action(action)
                results.append(result)
                
                # Mark action as executed
                self.turn_order.execute_action(action)
            
            return {
                "actions_executed": len(results),
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Fehler bei Action-Ausführung: {e}")
            return {"error": str(e)}
    
    def transition_phase(self, to_phase: BattlePhase, force: bool = False) -> bool:
        """
        UNIVERSAL PHASE TRANSITION HANDLER - Single source of truth for all phase transitions.
        Replaces all _transition_to_*_phase() methods.
        
        Args:
            to_phase: Target phase to transition to
            force: If True, skip validation and force transition
            
        Returns:
            True if transition successful, False otherwise
        """
        try:
            from_phase = self.state.phase
            
            # Validate transition unless forced
            if not force and not self.validate_phase_transition(from_phase, to_phase):
                logger.error(f"Invalid phase transition: {from_phase.value} → {to_phase.value}")
                return False
            
            # Check for unexpected transitions
            if not force and not self._is_expected_transition(from_phase, to_phase):
                logger.warning(f"Unexpected phase transition: {from_phase.value} → {to_phase.value}")
            
            # Perform transition
            self.state.phase = to_phase
            
            # Update state based on target phase
            if to_phase == BattlePhase.INPUT:
                self.state.waiting_for_input = True
            elif to_phase == BattlePhase.EXECUTION:
                self.state.waiting_for_input = False
            elif to_phase == BattlePhase.AFTERMATH:
                self.state.waiting_for_input = False
            
            # Emit phase change event
            if self.event_processor:
                self.event_processor.emit_event(
                    EventType.PHASE_CHANGE,
                    {
                        'old_phase': from_phase.value,
                        'new_phase': to_phase.value,
                        'turn': self.state.turn_count,
                        'forced': force
                    }
                )
            
            logger.info(f"✓ Battle phase transitioned: {from_phase.value} → {to_phase.value}")
            return True
            
        except Exception as e:
            logger.error(f"Error transitioning phase {self.state.phase.value} → {to_phase.value}: {e}")
            # Fallback: Force transition
            if not force:
                return self.transition_phase(to_phase, force=True)
            return False
    
    def _is_expected_transition(self, from_phase: BattlePhase, to_phase: BattlePhase) -> bool:
        """Check if phase transition is expected/normal."""
        expected_transitions = {
            BattlePhase.START: [BattlePhase.INPUT],
            BattlePhase.INPUT: [BattlePhase.EXECUTION, BattlePhase.END],
            BattlePhase.EXECUTION: [BattlePhase.AFTERMATH, BattlePhase.END],
            BattlePhase.AFTERMATH: [BattlePhase.INPUT, BattlePhase.END],
            BattlePhase.END: []
        }
        return to_phase in expected_transitions.get(from_phase, [])
    
    
    
    
    
    def sync_state_with_ui(self, ui_component) -> None:
        """Synchronize state with UI component."""
        if ui_component and self.state:
            ui_component.battle_state = self.state
            ui_component.battle_controller = self
            if self.event_processor:
                ui_component.event_processor = self.event_processor
            logger.info("✓ State and Controller synchronized with UI")
    
    
    def validate_phase_transition(self, from_phase: BattlePhase, to_phase: BattlePhase) -> bool:
        """
        Validate if a phase transition is allowed.
        AGENT 4: Ensures proper phase flow.
        """
        valid_transitions = {
            BattlePhase.INIT: [BattlePhase.START],
            BattlePhase.START: [BattlePhase.INPUT],
            BattlePhase.INPUT: [BattlePhase.EXECUTION, BattlePhase.END],
            BattlePhase.EXECUTION: [BattlePhase.AFTERMATH, BattlePhase.END],
            BattlePhase.AFTERMATH: [BattlePhase.INPUT, BattlePhase.END],
            BattlePhase.END: [BattlePhase.REWARD, BattlePhase.COMPLETE]
        }
        
        return to_phase in valid_transitions.get(from_phase, [])
