"""
Phase transition methods - max 200 lines
Contains all phase transition and reward processing logic.
"""

import logging
from typing import Dict, Any, Optional
from engine.systems.battle.battle_enums import BattlePhase, BattleResult
from engine.systems.battle.event_processor import EventType

logger = logging.getLogger(__name__)


class BattleControllerPhasesMixin:
    """
    Phase transition methods extracted from main controller.
    Handles all phase transitions and battle end processing.
    """
    
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
    
    def process_battle_end_rewards(self) -> Dict[str, Any]:
        """
        DELEGATES to consolidated RewardSystem.process_battle_end_rewards().
        This method maintains compatibility while using the single source of truth.
        """
        from ..reward_system import RewardSystem
        reward_system = RewardSystem()
        return reward_system.process_battle_end_rewards(self.state)
    
    def get_talent_exp_reward(self, monster, base_exp: int, 
                            victory_bonus: float = 1.0) -> int:
        """
        DELEGATES to consolidated SkillsDQMIntegrated.get_talent_exp_reward().
        This method maintains compatibility while using the single source of truth.
        """
        from ..skills_dqm_integrated import SkillsDQMIntegrated
        skills_system = SkillsDQMIntegrated(self.battle_state)
        return skills_system.get_talent_exp_reward(monster, base_exp, victory_bonus)
