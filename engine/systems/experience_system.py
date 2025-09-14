"""
Experience and Level System for Untold Story.
Handles EXP gain, level up, and stat growth.
Integrated with Talent System for DQM-style move learning.
"""

import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class GrowthCurve(Enum):
    """Different EXP growth curves (DQM style)."""
    FAST = "fast"          # Reaches level 100 at 800,000 EXP
    MEDIUM_FAST = "medium_fast"  # Reaches level 100 at 1,000,000 EXP
    MEDIUM_SLOW = "medium_slow"  # Reaches level 100 at 1,059,860 EXP
    SLOW = "slow"          # Reaches level 100 at 1,250,000 EXP
    ERRATIC = "erratic"    # Irregular growth pattern
    FLUCTUATING = "fluctuating"  # DQM-specific pattern


@dataclass
class LevelUpResult:
    """Result of a level up."""
    new_level: int
    old_level: int
    stat_gains: Dict[str, int]
    new_moves: List[str]
    evolution: Optional[str] = None
    talent_upgrades: List[Dict[str, Any]] = None
    talent_moves_learned: List[str] = None
    experience_gained: int = 0
    
    def __post_init__(self):
        """Initialize default values for new fields."""
        if self.talent_upgrades is None:
            self.talent_upgrades = []
        if self.talent_moves_learned is None:
            self.talent_moves_learned = []


class ExperienceSystem:
    """
    Manages experience points and leveling for monsters.
    Based on Dragon Quest Monsters formulas.
    """
    
    # Base EXP yield by monster rank (DQM style)
    RANK_EXP_MULTIPLIERS = {
        'F': 0.5,
        'E': 0.7,
        'D': 1.0,
        'C': 1.3,
        'B': 1.6,
        'A': 2.0,
        'S': 2.5,
        'SS': 3.0,
        'X': 4.0
    }
    
    # Battle type EXP modifiers
    BATTLE_TYPE_MODIFIERS = {
        'wild': 1.0,
        'trainer': 1.5,
        'boss': 2.0,
        'legendary': 3.0
    }
    
    @staticmethod
    def calculate_exp_for_level(level: int, growth_curve: GrowthCurve) -> int:
        """
        Calculate total EXP needed for a specific level.
        
        Args:
            level: Target level (1-100)
            growth_curve: Growth curve type
            
        Returns:
            Total EXP needed for that level
        """
        if level <= 1:
            return 0
        
        if growth_curve == GrowthCurve.FAST:
            # Fast: (4 * level^3) / 5
            return int((4 * level ** 3) / 5)
            
        elif growth_curve == GrowthCurve.MEDIUM_FAST:
            # Medium Fast: level^3
            return level ** 3
            
        elif growth_curve == GrowthCurve.MEDIUM_SLOW:
            # Medium Slow: (6 * level^3) / 5 - 15 * level^2 + 100 * level - 140
            return int((6 * level ** 3) / 5 - 15 * level ** 2 + 100 * level - 140)
            
        elif growth_curve == GrowthCurve.SLOW:
            # Slow: (5 * level^3) / 4
            return int((5 * level ** 3) / 4)
            
        elif growth_curve == GrowthCurve.ERRATIC:
            # Erratic: Special formula with different phases
            if level <= 50:
                return int((level ** 3 * (100 - level)) / 50)
            elif level <= 68:
                return int((level ** 3 * (150 - level)) / 100)
            elif level <= 98:
                return int((level ** 3 * ((1911 - 10 * level) / 3)) / 500)
            else:
                return int((level ** 3 * (160 - level)) / 100)
                
        elif growth_curve == GrowthCurve.FLUCTUATING:
            # Fluctuating: DQM-specific pattern
            if level <= 15:
                return int(level ** 3 * ((level + 1) / 3 + 24) / 50)
            elif level <= 36:
                return int(level ** 3 * (level + 14) / 50)
            else:
                return int(level ** 3 * ((level / 2) + 32) / 50)
        
        # Default to medium fast
        return level ** 3
    
    @staticmethod
    def calculate_exp_to_next_level(current_level: int, current_exp: int, growth_curve: GrowthCurve) -> int:
        """
        Calculate EXP needed to reach next level.
        
        Args:
            current_level: Current level
            current_exp: Current total EXP
            growth_curve: Growth curve type
            
        Returns:
            EXP needed for next level
        """
        if current_level >= 100:
            return 0  # Max level
        
        exp_for_next = ExperienceSystem.calculate_exp_for_level(current_level + 1, growth_curve)
        return max(0, exp_for_next - current_exp)
    
    @staticmethod
    def calculate_level_from_exp(total_exp: int, growth_curve: GrowthCurve) -> int:
        """
        Calculate level from total EXP.
        
        Args:
            total_exp: Total experience points
            growth_curve: Growth curve type
            
        Returns:
            Current level (1-100)
        """
        # Binary search for efficiency
        left, right = 1, 100
        result = 1
        
        while left <= right:
            mid = (left + right) // 2
            exp_needed = ExperienceSystem.calculate_exp_for_level(mid, growth_curve)
            
            if exp_needed <= total_exp:
                result = mid
                left = mid + 1
            else:
                right = mid - 1
        
        return result
    
    @staticmethod
    def calculate_battle_exp(defeated_monster, battle_type: str = 'wild', 
                           participated_monsters: int = 1, held_items: List[str] = None) -> int:
        """
        Calculate EXP gained from defeating a monster.
        
        Args:
            defeated_monster: The defeated monster instance
            battle_type: Type of battle (wild, trainer, boss, legendary)
            participated_monsters: Number of monsters that participated
            held_items: List of held items that might affect EXP
            
        Returns:
            Base EXP to be distributed
        """
        # Base EXP calculation (DQM formula)
        base_exp = 0
        
        # Get monster level
        level = defeated_monster.level if hasattr(defeated_monster, 'level') else 5
        
        # Get monster rank
        rank = 'D'  # Default
        if hasattr(defeated_monster, 'rank'):
            rank = defeated_monster.rank
        elif hasattr(defeated_monster, 'species') and hasattr(defeated_monster.species, 'rank'):
            rank = defeated_monster.species.rank
        
        # Base formula: (base_yield * level) / 7
        # Base yield depends on monster species, using level * 10 as default
        base_yield = level * 10
        
        # Apply rank multiplier
        rank_mult = ExperienceSystem.RANK_EXP_MULTIPLIERS.get(rank, 1.0)
        base_exp = int((base_yield * level * rank_mult) / 7)
        
        # Apply battle type modifier
        battle_mult = ExperienceSystem.BATTLE_TYPE_MODIFIERS.get(battle_type, 1.0)
        base_exp = int(base_exp * battle_mult)
        
        # Apply held item bonuses
        if held_items:
            for item in held_items:
                if item == 'exp_share':
                    base_exp = int(base_exp * 1.5)
                elif item == 'lucky_egg':
                    base_exp = int(base_exp * 1.5)
        
        # Minimum EXP is 1
        return max(1, base_exp)
    
    @staticmethod
    def distribute_exp(total_exp: int, participants: List[Any], exp_share: bool = False) -> Dict[Any, int]:
        """
        Distribute EXP among participating monsters.
        
        Args:
            total_exp: Total EXP to distribute
            participants: List of participating monsters
            exp_share: Whether EXP Share item is active
            
        Returns:
            Dictionary mapping each participant to their EXP gain
        """
        exp_distribution = {}
        
        if not participants:
            return exp_distribution
        
        if exp_share:
            # With EXP Share: 50% to active participants, 50% split among all
            active_count = len([p for p in participants if getattr(p, 'participated', True)])
            
            if active_count > 0:
                active_exp = total_exp // 2
                shared_exp = total_exp - active_exp
                
                # Active participants get their share of 50%
                active_share = active_exp // active_count if active_count > 0 else 0
                
                # Everyone gets a share of the other 50%
                shared_share = shared_exp // len(participants) if participants else 0
                
                for participant in participants:
                    if getattr(participant, 'participated', True):
                        exp_distribution[participant] = active_share + shared_share
                    else:
                        exp_distribution[participant] = shared_share
            else:
                # If no active participants, split evenly
                share = total_exp // len(participants)
                for participant in participants:
                    exp_distribution[participant] = share
        else:
            # Without EXP Share: only active participants get EXP
            active_participants = [p for p in participants if getattr(p, 'participated', True)]
            
            if active_participants:
                share = total_exp // len(active_participants)
                for participant in active_participants:
                    exp_distribution[participant] = share
        
        return exp_distribution
    
    @staticmethod
    def calculate_stat_gain(monster, stat: str, growth_rate: str = 'medium') -> int:
        """
        Calculate stat gain on level up.
        
        Args:
            monster: Monster instance
            stat: Stat to calculate gain for (hp, atk, def, mag, res, spd)
            growth_rate: Growth rate (slow, medium, fast)
            
        Returns:
            Stat gain amount
        """
        # Base stat gains by growth rate
        base_gains = {
            'slow': {'hp': 3, 'atk': 1, 'def': 1, 'mag': 1, 'res': 1, 'spd': 1},
            'medium': {'hp': 5, 'atk': 2, 'def': 2, 'mag': 2, 'res': 2, 'spd': 2},
            'fast': {'hp': 7, 'atk': 3, 'def': 3, 'mag': 3, 'res': 3, 'spd': 3}
        }
        
        base = base_gains.get(growth_rate, base_gains['medium']).get(stat, 1)
        
        # Add some randomness (DQM style)
        import random
        variance = random.randint(-1, 2)
        
        # Ensure minimum gain of 1
        return max(1, base + variance)
    
    @staticmethod
    def check_level_up(monster, exp_gained: int) -> Optional[LevelUpResult]:
        """
        Check if monster levels up and process it.
        
        Args:
            monster: Monster instance
            exp_gained: EXP gained from battle
            
        Returns:
            LevelUpResult if leveled up, None otherwise
        """
        if not hasattr(monster, 'total_exp'):
            monster.total_exp = 0
        if not hasattr(monster, 'level'):
            monster.level = 1
        
        # Get growth curve from species or use default
        if hasattr(monster, 'species') and hasattr(monster.species, 'growth_curve'):
            growth_curve = monster.species.growth_curve
        elif hasattr(monster, 'growth_curve'):
            growth_curve = monster.growth_curve
        else:
            growth_curve = GrowthCurve.MEDIUM_FAST
        
        old_level = monster.level
        old_exp = monster.total_exp
        
        # Add EXP
        monster.total_exp += exp_gained
        
        # Calculate new level
        new_level = ExperienceSystem.calculate_level_from_exp(
            monster.total_exp, 
            growth_curve
        )
        
        # Check if leveled up
        if new_level > old_level:
            # Process level up
            stat_gains = {}
            
            # Calculate stat gains for each level gained
            for level in range(old_level + 1, new_level + 1):
                for stat in ['hp', 'atk', 'def', 'mag', 'res', 'spd']:
                    gain = ExperienceSystem.calculate_stat_gain(monster, stat)
                    stat_gains[stat] = stat_gains.get(stat, 0) + gain
                    
                    # Apply stat gain
                    if hasattr(monster, 'stats') and isinstance(monster.stats, dict):
                        monster.stats[stat] = monster.stats.get(stat, 1) + gain
                    
                    # Special handling for HP
                    if stat == 'hp':
                        if hasattr(monster, 'max_hp'):
                            monster.max_hp += gain
                            monster.current_hp += gain  # Heal on level up
            
            # Update level
            monster.level = new_level
            
            # Check for new moves
            new_moves = ExperienceSystem.check_new_moves(monster, old_level, new_level)
            
            # Check for evolution
            evolution = ExperienceSystem.check_evolution(monster, new_level)
            
            # Check for talent-based moves
            talent_moves = ExperienceSystem.check_new_moves_from_talents(monster, old_level, new_level)
            
            # Add talent moves to new_moves list
            all_new_moves = new_moves + talent_moves
            
            return LevelUpResult(
                new_level=new_level,
                old_level=old_level,
                stat_gains=stat_gains,
                new_moves=all_new_moves,
                evolution=evolution,
                talent_moves_learned=talent_moves,
                experience_gained=exp_gained
            )
        
        return None
    
    
    @staticmethod
    def check_evolution(monster, level: int) -> Optional[str]:
        """
        Check if monster evolves at this level.
        
        Args:
            monster: Monster instance
            level: Current level
            
        Returns:
            Evolution species name if evolving, None otherwise
        """
        if hasattr(monster, 'species') and hasattr(monster.species, 'evolution'):
            evo_data = monster.species.evolution
            if isinstance(evo_data, dict):
                if evo_data.get('type') == 'level' and evo_data.get('level') == level:
                    return evo_data.get('into')
        
        return None
    
    @staticmethod
    def apply_level_up(monster, level_up_result: LevelUpResult) -> Dict[str, Any]:
        """
        Apply level up results to monster.
        
        Args:
            monster: Monster to level up
            level_up_result: Results from level up
            
        Returns:
            Summary of changes
        """
        summary = {
            'name': monster.name if hasattr(monster, 'name') else 'Monster',
            'old_level': level_up_result.old_level,
            'new_level': level_up_result.new_level,
            'stat_gains': level_up_result.stat_gains,
            'new_moves': level_up_result.new_moves,
            'evolution': level_up_result.evolution
        }
        
        # Apply talent level up
        talent_results = ExperienceSystem.apply_talent_level_up(monster, level_up_result)
        
        # Update summary with talent results
        summary['talent_upgrades'] = talent_results['talent_upgrades']
        summary['talent_moves_learned'] = talent_results['new_moves']
        summary['talent_messages'] = talent_results['messages']
        
        # Log the level up
        logger.info(f"{summary['name']} grew to level {summary['new_level']}!")
        
        for stat, gain in level_up_result.stat_gains.items():
            logger.info(f"  {stat.upper()} +{gain}")
        
        for move in level_up_result.new_moves:
            logger.info(f"  Learned {move}!")
        
        if level_up_result.evolution:
            logger.info(f"  Ready to evolve into {level_up_result.evolution}!")
        
        # Log talent upgrades
        for upgrade in talent_results['talent_upgrades']:
            logger.info(f"  {upgrade['talent_id']} upgraded to tier {upgrade['new_tier']}!")
        
        for move in talent_results['new_moves']:
            logger.info(f"  Learned {move} from talent!")
        
        return summary
    
    
    @staticmethod
    def add_talent_experience(monster, experience: int) -> Dict[str, Any]:
        """
        Füge Talent-Experience hinzu.
        
        Args:
            monster: Monster instance
            experience: Experience points to add
            
        Returns:
            Dictionary with talent upgrade results
        """
        results = {
            'talent_upgrades': [],
            'new_moves': [],
            'level_ups': []
        }
        
        try:
            # Prüfe ob Monster Talents hat
            if not hasattr(monster, 'talents'):
                return results
            
            # Verteile Experience auf alle gelernten Talents
            for talent_instance in monster.talents:
                if talent_instance.is_learned:
                    old_tier = talent_instance.current_tier
                    tier_upgraded = talent_instance.add_experience(experience)
                    
                    if tier_upgraded:
                        results['talent_upgrades'].append({
                            'talent_id': talent_instance.talent_id,
                            'old_tier': old_tier.value,
                            'new_tier': talent_instance.current_tier.value
                        })
                        
                        # Prüfe neue Moves für höhere Tier
                        new_moves = ExperienceSystem.get_new_moves_for_talent_tier(
                            talent_instance.talent_id, 
                            old_tier, 
                            talent_instance.current_tier,
                            monster.level
                        )
                        results['new_moves'].extend(new_moves)
            
            return results
            
        except Exception as e:
            logger.error(f"Fehler beim Hinzufügen von Talent-Experience: {e}")
            return results
    
    
    @staticmethod
    def apply_talent_level_up(monster, level_up_result: LevelUpResult) -> Dict[str, Any]:
        """
        Wende Talent-Level-Up an.
        
        Args:
            monster: Monster instance
            level_up_result: Level up result
            
        Returns:
            Dictionary with talent level up results
        """
        results = {
            'new_moves': [],
            'talent_upgrades': [],
            'messages': []
        }
        
        try:
            # Prüfe neue Moves durch Level-Up
            new_moves = ExperienceSystem.check_new_moves_from_talents(
                monster, 
                level_up_result.old_level, 
                level_up_result.new_level
            )
            
            if new_moves:
                # Lerne neue Moves
                learn_success = ExperienceSystem.learn_new_moves_from_talents(monster, new_moves)
                if learn_success:
                    results['new_moves'] = new_moves
                    
                    # Erstelle Nachrichten
                    for move_id in new_moves:
                        results['messages'].append(f"{monster.name} lernt {move_id}!")
            
            # Füge Talent-Experience hinzu
            talent_results = ExperienceSystem.add_talent_experience(monster, level_up_result.experience_gained)
            results['talent_upgrades'].extend(talent_results['talent_upgrades'])
            results['new_moves'].extend(talent_results['new_moves'])
            
            # Erstelle Nachrichten für Talent-Upgrades
            for upgrade in talent_results['talent_upgrades']:
                results['messages'].append(
                    f"{monster.name}'s {upgrade['talent_id']} wurde auf Stufe {upgrade['new_tier']} verbessert!"
                )
            
            return results
            
        except Exception as e:
            logger.error(f"Fehler beim Anwenden von Talent-Level-Up: {e}")
            return results
