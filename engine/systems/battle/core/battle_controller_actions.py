"""
Action handling methods - max 200 lines
Contains all action-related methods and battle execution logic.
"""

import logging
from typing import Dict, Any, Optional, List
from engine.systems.battle.battle_enums import BattlePhase, BattleResult
from engine.systems.battle.turn_logic import BattleAction

logger = logging.getLogger(__name__)


class BattleControllerActionsMixin:
    """
    Action handling methods extracted from main controller.
    Handles all action execution and validation.
    """
    
    def execute_turn(self, player_action, enemy_action) -> Dict[str, Any]:
        """
        Execute a complete turn with player and enemy actions.
        AGENT 3: Repariert Battle-Flow mit korrekten Phase-Transitions.
        
        Args:
            player_action: Player action (BattleAction or dict)
            enemy_action: Enemy action (BattleAction or dict)
            
        Returns:
            Dict with turn execution result
        """
        try:
            logger.info(f"=== TURN EXECUTION START ===")
            logger.info(f"Current phase: {self.state.phase.value}")
            logger.info(f"Player action: {player_action}")
            logger.info(f"Enemy action: {enemy_action}")
            
            # AGENT 3: Transition to EXECUTION phase when turn starts
            if self.state.phase == BattlePhase.INPUT:
                self.transition_phase(BattlePhase.EXECUTION)
                logger.info("✓ Transitioned to EXECUTION phase")
            
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
            
            # AGENT 3: Execute turn using TurnProcessor
            if self.turn_processor:
                actions = [player_battle_action, enemy_battle_action]
                
                # Calculate turn order
                turn_order = self.turn_processor.calculate_turn_order(actions)
                logger.info(f"Turn order calculated: {len(turn_order)} actions")
                
                # Execute turn with proper order
                turn_result = self.turn_processor.execute_turn(actions)
                logger.info(f"Turn execution result: {turn_result}")
                
                # AGENT 3: Check for battle end after turn execution
                if turn_result.get('battle_ended', False):
                    logger.info("Battle ended during turn execution")
                    self.state.battle_ended = True
                    # Ensure battle_result is a BattleResult Enum, not a string
                    battle_result = turn_result.get('battle_result')
                    if isinstance(battle_result, str):
                        # Convert string to BattleResult enum if needed
                        from engine.systems.battle.battle_enums import BattleResult
                        try:
                            self.state.battle_result = BattleResult(battle_result.lower())
                        except ValueError:
                            logger.warning(f"Unknown battle result: {battle_result}, defaulting to VICTORY")
                            self.state.battle_result = BattleResult.VICTORY
                    else:
                        self.state.battle_result = battle_result
                    self.transition_phase(BattlePhase.END)
                    return {
                        "success": True,
                        "turn": self.state.turn_count,
                        "phase": self.state.phase.value,
                        "battle_ended": True,
                        "battle_result": self.state.battle_result,
                        "result": turn_result
                    }
                
                # AGENT 3: Transition to AFTERMATH phase after execution
                self.transition_phase(BattlePhase.AFTERMATH)
                logger.info("✓ Transitioned to AFTERMATH phase")
                
                # AGENT 3: Process aftermath (status effects, etc.)
                self._process_aftermath()
                
                # AGENT 3: If battle continues, transition back to INPUT phase
                if not self.state.battle_ended:
                    self.transition_phase(BattlePhase.INPUT)
                    logger.info("✓ Transitioned back to INPUT phase")
                
                # AGENT 3: Increment turn count
                self.state.turn_count += 1
                
                return {
                    "success": True,
                    "turn": self.state.turn_count,
                    "phase": self.state.phase.value,
                    "battle_ended": self.state.battle_ended,
                    "battle_result": self.state.battle_result,
                    "result": turn_result
                }
            else:
                # Fallback to old method
                logger.warning("No TurnProcessor available, using fallback")
                self.turn_order.add_action(player_battle_action)
                self.turn_order.add_action(enemy_battle_action)
                result = self._execute_actions()
                self.state.turn_count += 1
                
                # AGENT 3: Apply phase transitions in fallback mode too
                self.transition_phase(BattlePhase.AFTERMATH)
                self._process_aftermath()
                if not self.state.battle_ended:
                    self.transition_phase(BattlePhase.INPUT)
                
                return {
                    "success": True,
                    "turn": self.state.turn_count,
                    "phase": self.state.phase.value,
                    "battle_ended": self.state.battle_ended,
                    "battle_result": self.state.battle_result,
                    "result": result
                }
            
        except Exception as e:
            logger.error(f"Fehler bei Turn-Ausführung: {e}")
            return {"success": False, "error": str(e)}
    
    def start_battle(self) -> Dict[str, Any]:
        """
        Start the battle - pure coordination.
        Delegates to turn_processor for initialization.
        """
        if not self.turn_processor:
            raise RuntimeError("TurnProcessor not set - call set_managers() first")
        
        logger.info("Starting battle")
        
        # Initialize turn processor and transition to START phase
        result = self.turn_processor.start_turn()
        
        # Transition to START phase
        self.state.phase = BattlePhase.START
        
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
            from engine.systems.moves import Move, MoveCategory, MoveTarget
            
            actor = self.state.player_active if is_player else self.state.enemy_active
            if not actor:
                logger.error(f"No active monster for {'player' if is_player else 'enemy'}")
                return None
            
            # Handle move data - convert dict to Move object if needed
            move_data = action_data.get('move')
            if isinstance(move_data, dict):
                # Create Move object from dict
                move = Move(
                    id=move_data.get('name', 'tackle').lower(),
                    name=move_data.get('name', 'Tackle'),
                    type=move_data.get('type', 'Normal'),
                    category=MoveCategory.PHYSICAL,
                    power=move_data.get('power', 40),
                    accuracy=move_data.get('accuracy', 100),
                    priority=move_data.get('priority', 0),
                    targeting=MoveTarget.ENEMY,
                    effects=move_data.get('effects', []),
                    description=move_data.get('description', 'Basic attack'),
                    contact=move_data.get('contact', True),
                    sound_based=move_data.get('sound_based', False),
                    punching=move_data.get('punching', False),
                    biting=move_data.get('biting', False),
                    pulse=move_data.get('pulse', False),
                    multi_hit=move_data.get('multi_hit'),
                    drain_percent=move_data.get('drain_percent', 0),
                    recoil_percent=move_data.get('recoil_percent', 0),
                    multi_hit_min=move_data.get('multi_hit_min', 1),
                    multi_hit_max=move_data.get('multi_hit_max', 1),
                    talent_id=move_data.get('talent_id'),
                    talent_tier=move_data.get('talent_tier'),
                    level_requirement=move_data.get('level_requirement', 1)
                )
            else:
                move = move_data
            
            # Determine target
            if is_player:
                target = self.state.enemy_active
            else:
                target = self.state.player_active
            
            # Use centralized action creation
            action_dict = {
                'action_type': action_data.get('action_type', 'ATTACK'),
                'actor': actor,
                'target': target,
                'move': move
            }
            
            return create_action_from_dict(action_dict)
            
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
    
    # Aftermath methods moved to battle_controller_aftermath.py
