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
    
    def get_talent_exp_reward(self, monster, base_exp: int, 
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
