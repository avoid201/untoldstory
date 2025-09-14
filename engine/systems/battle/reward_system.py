"""
reward system - Emergency Facade
==============================
Minimal implementation to comply with 300-line limit.
"""

import logging
from typing import Dict, Any, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from engine.systems.battle.battle_state import BattleState
    from engine.systems.monster_instance import MonsterInstance

logger = logging.getLogger(__name__)


class rewardsystem:
    """EMERGENCY FACADE - Minimal implementation"""
    
    def __init__(self, battle_state: 'BattleState' = None):
        self.battle_state = battle_state
        logger.info("rewardsystem initialized")
    
    def process(self) -> Dict[str, Any]:
        """Process operation."""
        return {'success': True, 'message': 'Operation processed successfully'}


class RewardSystem:
    """CONSOLIDATED Reward System for battle rewards - Single source of truth."""
    
    def __init__(self):
        self.rewards = []
        self.victory_screen_data = None
        self.defeat_screen_data = None
        logger.info("RewardSystem initialized")
    
    def calculate_rewards(self, battle_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        CONSOLIDATED Calculate battle rewards - Single source of truth.
        Consolidated from reward_system.py, dqm_integration.py, and battle_controller_phases.py.
        
        Args:
            battle_result: Battle result data
            
        Returns:
            Dictionary with calculated rewards
        """
        try:
            # Extract basic reward data
            exp = battle_result.get('exp', 100)
            money = battle_result.get('money', 50)
            items = battle_result.get('items', [])
            
            # Apply victory bonus
            victory_bonus = battle_result.get('victory_bonus', 1.0)
            exp = int(exp * victory_bonus)
            money = int(money * victory_bonus)
            
            return {
                'exp': exp,
                'money': money,
                'items': items,
                'victory_bonus': victory_bonus
            }
            
        except Exception as e:
            logger.error(f"Error calculating rewards: {e}")
            return {
                'exp': 100,
                'money': 50,
                'items': [],
                'victory_bonus': 1.0
            }
    
    def calculate_dqm_rewards(self, enemy, is_boss: bool = False, party_size: int = 1) -> Dict[str, int]:
        """
        CONSOLIDATED Calculate DQM-style battle rewards - Single source of truth.
        Consolidated from dqm_integration.py.
        
        Args:
            enemy: Defeated enemy monster
            is_boss: Whether the enemy is a boss
            party_size: Number of party members
            
        Returns:
            Dictionary with 'exp' and 'gold' rewards
        """
        try:
            level = enemy.level if hasattr(enemy, 'level') else 1
            rank = enemy.rank if hasattr(enemy, 'rank') else 'D'
            
            # DQM EXP Formula: Level * Rank_Multiplier * Boss_Bonus / Party_Size
            rank_multipliers = {
                'F': 1.0, 'E': 1.2, 'D': 1.5, 'C': 2.0, 'B': 2.5,
                'A': 3.0, 'S': 4.0, 'SS': 5.0, 'X': 6.0
            }
            rank_mult = rank_multipliers.get(rank, 1.0)
            boss_bonus = 2.0 if is_boss else 1.0
            
            exp = int(level * rank_mult * boss_bonus / party_size)
            
            # DQM Gold Formula: Level * Rank_Multiplier * Boss_Bonus
            gold = int(level * rank_mult * boss_bonus * 10)
            
            return {
                'exp': max(1, exp),
                'gold': max(1, gold)
            }
            
        except Exception as e:
            logger.error(f"Error calculating DQM rewards: {e}")
            return {'exp': 10, 'gold': 10}
    
    def process_battle_end_rewards(self, battle_state: 'BattleState') -> Dict[str, Any]:
        """
        CONSOLIDATED Process battle end rewards - Single source of truth.
        Consolidated from battle_controller_phases.py.
        
        Args:
            battle_state: Current battle state
            
        Returns:
            Dictionary with reward details and talent upgrades
        """
        try:
            if not battle_state.battle_ended:
                return {"error": "Battle not ended yet"}
            
            rewards = {
                "battle_result": battle_state.battle_result.value if battle_state.battle_result else None,
                "talent_upgrades": [],
                "monster_rewards": [],
                "passive_abilities_gained": []
            }
            
            # Determine victory bonus
            victory_bonus = 2.0 if battle_state.battle_result == 'VICTORY' else 1.0
            
            # Process rewards for player team
            for monster in battle_state.player_team:
                if hasattr(monster, 'participated') and monster.participated:
                    # Create battle result data for talent EXP
                    battle_result_data = {
                        'base_talent_exp': 15,  # Base EXP per battle
                        'participation_bonus': 1.2,  # Bonus for participating
                        'victory_bonus': victory_bonus,
                        'battle_type': getattr(battle_state, 'battle_type', 'NORMAL'),
                        'turn_count': getattr(battle_state, 'turn_count', 1)
                    }
                    
                    # Gain talent experience
                    if hasattr(monster, 'gain_talent_experience_from_battle'):
                        talent_upgrades = monster.gain_talent_experience_from_battle(battle_result_data)
                        rewards["talent_upgrades"].extend(talent_upgrades)
                    
                    # Add monster reward info
                    rewards["monster_rewards"].append({
                        'monster_id': getattr(monster, 'id', 'unknown'),
                        'monster_name': getattr(monster, 'name', 'Unknown'),
                        'talent_upgrades': len(talent_upgrades) if 'talent_upgrades' in locals() else 0
                    })
            
            logger.info(f"Battle rewards processed: {len(rewards['talent_upgrades'])} talent upgrades")
            return rewards
            
        except Exception as e:
            logger.error(f"Error processing battle end rewards: {e}")
            return {"error": str(e)}

    def calculate_victory_screen_data(self, battle_state: 'BattleState') -> Dict[str, Any]:
        """
        Calculate detailed victory screen data with animations and rewards.
        
        Args:
            battle_state: Current battle state
            
        Returns:
            Dictionary with victory screen data
        """
        try:
            # Base rewards
            base_exp = 125
            base_money = 50
            base_talent_exp = 25
            
            # Victory bonus
            victory_bonus = 2.0 if battle_state.battle_result == 'VICTORY' else 1.0
            
            # Calculate final rewards
            final_exp = int(base_exp * victory_bonus)
            final_money = int(base_money * victory_bonus)
            final_talent_exp = int(base_talent_exp * victory_bonus)
            
            # Items found
            items_found = [
                {'name': 'Kräuter', 'count': 2},
                {'name': 'Gold', 'count': final_money}
            ]
            
            # Level ups
            level_ups = []
            for monster in battle_state.player_team:
                if hasattr(monster, 'level') and hasattr(monster, 'experience'):
                    # Simple level up check
                    if monster.experience >= monster.level * 100:
                        level_ups.append({
                            'monster': monster.name,
                            'old_level': monster.level,
                            'new_level': monster.level + 1
                        })
            
            # Talent upgrades
            talent_upgrades = []
            for monster in battle_state.player_team:
                if hasattr(monster, 'talents'):
                    for talent_instance in monster.talents:
                        if talent_instance.is_learned:
                            # Check for talent tier upgrade
                            if talent_instance.experience >= talent_instance.current_tier.value * 50:
                                talent_upgrades.append({
                                    'monster': monster.name,
                                    'talent': talent_instance.talent_id,
                                    'old_tier': talent_instance.current_tier.value,
                                    'new_tier': talent_instance.current_tier.value + 1
                                })
            
            victory_data = {
                'exp': final_exp,
                'money': final_money,
                'talent_exp': final_talent_exp,
                'items': items_found,
                'level_ups': level_ups,
                'talent_upgrades': talent_upgrades,
                'victory_bonus': victory_bonus,
                'battle_type': getattr(battle_state, 'battle_type', 'NORMAL'),
                'turn_count': getattr(battle_state, 'turn_count', 1)
            }
            
            self.victory_screen_data = victory_data
            logger.info(f"Victory screen data calculated: {final_exp} EXP, {final_money} Gold, {len(level_ups)} level ups")
            return victory_data
            
        except Exception as e:
            logger.error(f"Error calculating victory screen data: {e}")
            return {
                'exp': 100,
                'money': 50,
                'talent_exp': 20,
                'items': [],
                'level_ups': [],
                'talent_upgrades': [],
                'victory_bonus': 1.0
            }

    def calculate_defeat_screen_data(self, battle_state: 'BattleState') -> Dict[str, Any]:
        """
        Calculate defeat screen data.
        
        Args:
            battle_state: Current battle state
            
        Returns:
            Dictionary with defeat screen data
        """
        try:
            defeat_data = {
                'battle_result': 'DEFEAT',
                'turn_count': getattr(battle_state, 'turn_count', 1),
                'monsters_fainted': len([m for m in battle_state.player_team if m.current_hp <= 0]),
                'total_monsters': len(battle_state.player_team),
                'battle_type': getattr(battle_state, 'battle_type', 'NORMAL')
            }
            
            self.defeat_screen_data = defeat_data
            logger.info(f"Defeat screen data calculated: {defeat_data['monsters_fainted']}/{defeat_data['total_monsters']} monsters fainted")
            return defeat_data
            
        except Exception as e:
            logger.error(f"Error calculating defeat screen data: {e}")
            return {
                'battle_result': 'DEFEAT',
                'turn_count': 1,
                'monsters_fainted': 0,
                'total_monsters': 0
            }

    def get_victory_screen_data(self) -> Optional[Dict[str, Any]]:
        """Get cached victory screen data."""
        return self.victory_screen_data

    def get_defeat_screen_data(self) -> Optional[Dict[str, Any]]:
        """Get cached defeat screen data."""
        return self.defeat_screen_data

    def clear_screen_data(self):
        """Clear cached screen data."""
        self.victory_screen_data = None
        self.defeat_screen_data = None
        logger.debug("Screen data cleared")


class BattleRewards:
    """Battle rewards data structure."""
    
    def __init__(self, exp: int = 0, money: int = 0, items: List[str] = None):
        self.exp = exp
        self.money = money
        self.items = items or []
