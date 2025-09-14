"""
DQM Integration Module
Integrates Dragon Quest Monsters formulas into the existing battle system
"""

import logging
from typing import Dict, Any, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    # Lazy imports für zirkuläre Dependencies
    from engine.systems.unified_damage_calculator import (
        UnifiedDamageCalculator
    )


logger = logging.getLogger(__name__)


class DQMIntegration:
    """
    Integration layer for DQM formulas into the existing battle system.
    This class modifies the damage calculation pipeline to use DQM formulas.
    """
    
    def __init__(self):
        """Initialize DQM integration."""
        # Lazy initialization to avoid circular imports
        self._unified_calculator: Optional['UnifiedDamageCalculator'] = None
        self._original_stages = {}
    
    @property
    def unified_calculator(self) -> 'UnifiedDamageCalculator':
        """Lazy-loaded unified calculator to avoid circular imports."""
        if self._unified_calculator is None:
            from engine.systems.unified_damage_calculator import unified_damage_calculator
            self._unified_calculator = unified_damage_calculator
        return self._unified_calculator
    
    
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
            reduced_damage = self.unified_calculator._apply_metal_body(original_damage)
            
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
        multiplier = self.unified_calculator.calculate_stat_stage_multiplier(stage)
        
        return int(base_stat * multiplier)
    
    def calculate_turn_order(self, actions: List[Any]) -> List[Any]:
        """
        DELEGATES to consolidated TurnOrder.calculate_turn_order().
        This method maintains compatibility while using the single source of truth.
        
        Args:
            actions: List of battle actions
            
        Returns:
            Sorted list of actions in DQM turn order
        """
        # Import consolidated turn order calculation
        from .turn_logic import TurnOrder
        
        # Use consolidated implementation
        return TurnOrder().calculate_turn_order(actions)
    
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
        
        return self.unified_calculator.calculate_escape_chance(
            runner_stats.get('spd', 50),
            enemy_stats.get('spd', 50),
            attempts
        )
    
    def calculate_rewards(self, enemy, is_boss: bool = False, party_size: int = 1) -> Dict[str, int]:
        """
        DELEGATES to consolidated RewardSystem.calculate_dqm_rewards().
        This method maintains compatibility while using the single source of truth.
        """
        from .reward_system import RewardSystem
        reward_system = RewardSystem()
        return reward_system.calculate_dqm_rewards(enemy, is_boss, party_size)


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




def setup_dqm_systems(game) -> None:
    """
    Setup all DQM systems for the game.
    This function initializes and connects all DQM-specific systems.
    
    Args:
        game: The main Game instance
    """
    try:
        logger.info("Setting up DQM systems...")
        
        # Initialize skill system
        from engine.systems.battle.skills_dqm_integrated import get_skill_database
        game.skill_system = get_skill_database()
        logger.info("Skill system initialized")
        
        # Meat system now integrated into battle state
        logger.info("Meat system integrated into battle state")
        
        # Verbinde mit Battle System
        if hasattr(game, 'battle_controller'):
            game.battle_controller.skill_system = game.skill_system
            logger.info("DQM systems connected to battle controller")
        
        # Initialize DQM integration
        dqm_integration = get_dqm_integration()
        logger.info("DQM integration initialized")
        
        # Initialize monster database with traits support
        from engine.systems.monsters import get_monster_database
        monster_db = get_monster_database()
        logger.info("Monster database with traits support initialized")
        
        # Integrate DQM skills with move system
        from engine.systems.moves import integrate_dqm_skills_with_moves
        integrate_dqm_skills_with_moves()
        logger.info("DQM skills integrated with move system")
        
        # Sync meat inventory with item system
        try:
            from engine.systems.items import item_registry
            # This will be called when the game starts
            logger.info("Meat-item bridge ready")
        except Exception as e:
            logger.warning(f"Could not initialize meat-item bridge: {e}")
        
        logger.info("DQM systems setup completed successfully")
        
    except Exception as e:
        logger.error(f"Error setting up DQM systems: {e}")
        raise


# Export functions
__all__ = [
    'DQMIntegration',
    'get_dqm_integration', 
    'setup_dqm_systems'
]
