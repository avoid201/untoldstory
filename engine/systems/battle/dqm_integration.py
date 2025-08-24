"""
DQM Integration Module
Integrates Dragon Quest Monsters formulas into the existing battle system
"""

import logging
from typing import Dict, Any, List, Optional
from engine.systems.battle.dqm_formulas import (
    DQMCalculator, 
    DQMDamageStage,
    DQMConstants,
    DQMSkillCalculator
)
from engine.systems.battle.damage_calc import DamageCalculationPipeline

logger = logging.getLogger(__name__)


class DQMIntegration:
    """
    Integration layer for DQM formulas into the existing battle system.
    This class modifies the damage calculation pipeline to use DQM formulas.
    """
    
    def __init__(self):
        """Initialize DQM integration."""
        self.dqm_calculator = DQMCalculator()
        self.dqm_skill_calc = DQMSkillCalculator()
        self.dqm_stage = DQMDamageStage()
        self._original_stages = {}
    
    def integrate_with_pipeline(self, pipeline: DamageCalculationPipeline) -> None:
        """
        Integrate DQM formulas into the existing damage pipeline.
        
        Args:
            pipeline: The damage calculation pipeline to modify
        """
        try:
            # Store original stages for potential rollback
            self._original_stages = {name: (func, priority) 
                                    for name, func, priority in pipeline.stages}
            
            # Replace base damage calculation with DQM formula
            pipeline.remove_stage("base_damage")
            pipeline.add_stage("base_damage", self._dqm_base_damage_stage, 1)
            
            # Modify critical stage to use DQM rates (already done in damage_calc.py)
            # But we can add additional DQM-specific critical logic here if needed
            
            # Add DQM-specific stages
            pipeline.add_stage("tension", self._tension_stage, 7)
            pipeline.add_stage("metal_body", self._metal_body_stage, 8)
            
            logger.info("DQM formulas successfully integrated into damage pipeline")
            
        except Exception as e:
            logger.error(f"Failed to integrate DQM formulas: {str(e)}")
            self.rollback_integration(pipeline)
    
    def rollback_integration(self, pipeline: DamageCalculationPipeline) -> None:
        """
        Rollback to original damage calculation.
        
        Args:
            pipeline: The pipeline to restore
        """
        try:
            # Clear all stages
            pipeline.stages.clear()
            
            # Restore original stages
            for name, (func, priority) in self._original_stages.items():
                pipeline.add_stage(name, func, priority)
            
            logger.info("Rolled back to original damage calculation")
            
        except Exception as e:
            logger.error(f"Failed to rollback integration: {str(e)}")
    
    def _dqm_base_damage_stage(self, context: Dict[str, Any]) -> None:
        """
        Calculate base damage using DQM formula.
        This replaces the standard base damage calculation.
        """
        if context['result'].missed:
            return
        
        move = context['move']
        attacker = context['attacker']
        defender = context['defender']
        
        # Support moves don't deal damage
        if move.category == 'support' or move.power <= 0:
            context['result'].damage = 0
            return
        
        # Get stats
        if move.category == 'phys':
            attack_stat = self._get_effective_stat(attacker, 'atk')
            defense_stat = self._get_effective_stat(defender, 'def')
        else:  # 'mag'
            attack_stat = self._get_effective_stat(attacker, 'mag')
            defense_stat = self._get_effective_stat(defender, 'res')
        
        # Store for critical hit stage
        context['attack_stat'] = attack_stat
        context['defense_stat'] = defense_stat
        
        # DQM damage formula (from SlimeBattleSystem)
        # Base Damage = power * (attack / 2)
        # Defense reduction = defense / 4
        base_damage = move.power * (attack_stat / 2)
        defense_reduction = defense_stat / 4
        
        # Calculate damage
        damage = base_damage - defense_reduction
        
        # Ensure minimum damage
        context['result'].damage = max(1, int(damage))
    
    def _tension_stage(self, context: Dict[str, Any]) -> None:
        """
        Apply DQM tension multiplier.
        Tension dramatically increases damage in DQM.
        """
        if context['result'].damage == 0:
            return
        
        attacker = context['attacker']
        
        # Check if attacker has tension
        if not hasattr(attacker, 'tension'):
            return
        
        tension = attacker.tension
        multiplier = self.dqm_calculator._calculate_tension_multiplier(tension)
        
        if multiplier > 1.0:
            context['result'].damage = int(context['result'].damage * multiplier)
            context['result'].modifiers_applied.append(f"Tension x{multiplier:.1f}")
    
    def _metal_body_stage(self, context: Dict[str, Any]) -> None:
        """
        Apply Metal Body trait (metal slime defense).
        Reduces almost all damage to 0-1.
        """
        if context['result'].damage == 0:
            return
        
        defender = context['defender']
        
        # Check for Metal Body trait
        if hasattr(defender, 'traits') and 'Metal Body' in defender.traits:
            original_damage = context['result'].damage
            reduced_damage = self.dqm_calculator._apply_metal_body(original_damage)
            
            context['result'].damage = reduced_damage
            context['result'].modifiers_applied.append("Metal Body")
            
            # Add special flag for UI feedback
            if hasattr(context['result'], 'is_metal_slime_damage'):
                context['result'].is_metal_slime_damage = True
    
    def _get_effective_stat(self, monster, stat: str) -> int:
        """Get effective stat with stages."""
        base_stat = monster.stats.get(stat, 100)
        stage = monster.stat_stages.get(stat, 0) if hasattr(monster, 'stat_stages') else 0
        
        # Use DQM stat stage multipliers
        multiplier = self.dqm_calculator.calculate_stat_stage_multiplier(stage)
        
        return int(base_stat * multiplier)
    
    def calculate_turn_order(self, actions: List[Any]) -> List[Any]:
        """
        Calculate turn order using DQM formula.
        
        Args:
            actions: List of battle actions
            
        Returns:
            Sorted list of actions in DQM turn order
        """
        # Convert actions to monster dictionaries for DQM calculator
        monsters = []
        for action in actions:
            if hasattr(action, 'actor'):
                monster_dict = {
                    'name': action.actor.name if hasattr(action.actor, 'name') else 'Unknown',
                    'stats': action.actor.stats if hasattr(action.actor, 'stats') else {},
                    'status': action.actor.status if hasattr(action.actor, 'status') else None,
                    '_original_action': action  # Store reference to original action
                }
                monsters.append(monster_dict)
        
        # Calculate DQM turn order
        sorted_monsters = self.dqm_calculator.calculate_turn_order(monsters)
        
        # Extract original actions in new order
        sorted_actions = [m['_original_action'] for m in sorted_monsters]
        
        return sorted_actions
    
    def calculate_escape_chance(self, runner, enemy, attempts: int = 0) -> float:
        """
        Calculate escape chance using DQM formula.
        
        Args:
            runner: The monster trying to escape
            enemy: The enemy monster
            attempts: Number of previous escape attempts
            
        Returns:
            Probability of successful escape (0.0 to 1.0)
        """
        runner_stats = runner.stats if hasattr(runner, 'stats') else {'spd': 50}
        enemy_stats = enemy.stats if hasattr(enemy, 'stats') else {'spd': 50}
        
        return self.dqm_calculator.calculate_escape_chance(
            runner_stats, enemy_stats, attempts
        )
    
    def calculate_rewards(self, enemy, is_boss: bool = False, party_size: int = 1) -> Dict[str, int]:
        """
        Calculate battle rewards using DQM formulas.
        
        Args:
            enemy: Defeated enemy monster
            is_boss: Whether the enemy is a boss
            party_size: Number of party members
            
        Returns:
            Dictionary with 'exp' and 'gold' rewards
        """
        level = enemy.level if hasattr(enemy, 'level') else 1
        rank = enemy.rank if hasattr(enemy, 'rank') else 'D'
        
        exp = self.dqm_calculator.calculate_exp_reward(level, rank, is_boss, party_size)
        gold = self.dqm_calculator.calculate_gold_reward(level, rank, is_boss)
        
        return {
            'exp': exp,
            'gold': gold
        }


# Global integration instance
_dqm_integration = None


def get_dqm_integration() -> DQMIntegration:
    """
    Get or create the global DQM integration instance.
    
    Returns:
        The DQM integration instance
    """
    global _dqm_integration
    if _dqm_integration is None:
        _dqm_integration = DQMIntegration()
    return _dqm_integration


def enable_dqm_formulas(pipeline: DamageCalculationPipeline) -> None:
    """
    Enable DQM formulas in the damage calculation pipeline.
    
    Args:
        pipeline: The pipeline to modify
    """
    integration = get_dqm_integration()
    integration.integrate_with_pipeline(pipeline)


def disable_dqm_formulas(pipeline: DamageCalculationPipeline) -> None:
    """
    Disable DQM formulas and restore original calculation.
    
    Args:
        pipeline: The pipeline to restore
    """
    integration = get_dqm_integration()
    integration.rollback_integration(pipeline)


# Export functions
__all__ = [
    'DQMIntegration',
    'get_dqm_integration', 
    'enable_dqm_formulas',
    'disable_dqm_formulas'
]
