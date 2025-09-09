"""
Battle Rewards System for Untold Story.
Handles EXP distribution, item drops, and money rewards.
"""

import random
import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum

from engine.systems.experience_system import ExperienceSystem, LevelUpResult

logger = logging.getLogger(__name__)


class DropRarity(Enum):
    """Item drop rarity tiers."""
    COMMON = (0.5, "common")      # 50% chance
    UNCOMMON = (0.25, "uncommon")  # 25% chance
    RARE = (0.1, "rare")           # 10% chance
    VERY_RARE = (0.05, "very_rare") # 5% chance
    LEGENDARY = (0.01, "legendary") # 1% chance
    
    def __init__(self, chance: float, name: str):
        self.chance = chance
        self.display_name = name


@dataclass
class ItemDrop:
    """Represents a potential item drop."""
    item_id: str
    item_name: str
    quantity: int
    rarity: DropRarity
    chance_modifier: float = 1.0  # Additional modifier for this specific drop


@dataclass
class BattleRewards:
    """Complete battle rewards package."""
    exp_gained: Dict[Any, int]  # Monster -> EXP mapping
    money_gained: int
    items_gained: List[Tuple[str, int]]  # List of (item_id, quantity)
    level_ups: Dict[Any, LevelUpResult]  # Monster -> LevelUpResult mapping
    caught_monster: Optional[Any] = None
    bonus_rewards: Dict[str, Any] = None  # Special rewards


class RewardSystem:
    """
    Manages all battle rewards including EXP, money, and items.
    Based on Dragon Quest Monsters reward formulas.
    """
    
    # Money multipliers by rank
    RANK_MONEY_MULTIPLIERS = {
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
    
    # Default drop tables by monster type
    DEFAULT_DROP_TABLES = {
        'beast': [
            ItemDrop('fleisch', 'Fleisch', 1, DropRarity.COMMON),
            ItemDrop('hide', 'Fell', 1, DropRarity.UNCOMMON),
            ItemDrop('fang', 'Reißzahn', 1, DropRarity.RARE)
        ],
        'plant': [
            ItemDrop('herb', 'Kraut', 1, DropRarity.COMMON),
            ItemDrop('seed', 'Samen', 1, DropRarity.UNCOMMON),
            ItemDrop('leaf', 'Blatt', 2, DropRarity.UNCOMMON)
        ],
        'material': [
            ItemDrop('ore', 'Erz', 1, DropRarity.UNCOMMON),
            ItemDrop('crystal', 'Kristall', 1, DropRarity.RARE),
            ItemDrop('gem', 'Edelstein', 1, DropRarity.VERY_RARE)
        ],
        'dragon': [
            ItemDrop('scale', 'Schuppe', 1, DropRarity.UNCOMMON),
            ItemDrop('claw', 'Klaue', 1, DropRarity.RARE),
            ItemDrop('dragon_heart', 'Drachenherz', 1, DropRarity.LEGENDARY)
        ],
        'undead': [
            ItemDrop('bone', 'Knochen', 1, DropRarity.COMMON),
            ItemDrop('ectoplasm', 'Ektoplasma', 1, DropRarity.UNCOMMON),
            ItemDrop('soul_fragment', 'Seelenfragment', 1, DropRarity.RARE)
        ],
        'demon': [
            ItemDrop('dark_essence', 'Dunkle Essenz', 1, DropRarity.UNCOMMON),
            ItemDrop('demon_horn', 'Dämonenhorn', 1, DropRarity.RARE),
            ItemDrop('cursed_gem', 'Verfluchter Edelstein', 1, DropRarity.VERY_RARE)
        ]
    }
    
    def __init__(self):
        """Initialize the reward system."""
        self.exp_system = ExperienceSystem()
        self.drop_tables = {}  # Monster ID -> List[ItemDrop]
        self.initialize_drop_tables()
    
    def initialize_drop_tables(self):
        """Initialize monster-specific drop tables."""
        # Initialize with default drop tables
        self.drop_tables = self.DEFAULT_DROP_TABLES.copy()
        
        # Add some specific monster drops based on common patterns
        self.drop_tables.update({
            'fire_monster': [
                ItemDrop('ember', 'Glut', 1, DropRarity.COMMON),
                ItemDrop('fire_crystal', 'Feuerkristall', 1, DropRarity.UNCOMMON),
                ItemDrop('phoenix_feather', 'Phönixfeder', 1, DropRarity.RARE)
            ],
            'water_monster': [
                ItemDrop('water_orb', 'Wasserorb', 1, DropRarity.COMMON),
                ItemDrop('pearl', 'Perle', 1, DropRarity.UNCOMMON),
                ItemDrop('kraken_tentacle', 'Krakenarm', 1, DropRarity.RARE)
            ],
            'earth_monster': [
                ItemDrop('stone', 'Stein', 1, DropRarity.COMMON),
                ItemDrop('iron_ore', 'Eisenerz', 1, DropRarity.UNCOMMON),
                ItemDrop('diamond', 'Diamant', 1, DropRarity.VERY_RARE)
            ]
        })
        
        logger.info(f"Initialized drop tables for {len(self.drop_tables)} monster categories")
    
    def calculate_battle_rewards(self, battle_state, victory_type: str = 'normal') -> BattleRewards:
        """
        Calculate all rewards from a battle.
        
        Args:
            battle_state: The battle state object
            victory_type: Type of victory (normal, perfect, caught, fled)
            
        Returns:
            BattleRewards object with all rewards
        """
        rewards = BattleRewards(
            exp_gained={},
            money_gained=0,
            items_gained=[],
            level_ups={},
            bonus_rewards={}
        )
        
        # Only give rewards for victories and catches
        if victory_type not in ['normal', 'perfect', 'caught']:
            return rewards
        
        # Calculate rewards for each defeated enemy
        for enemy in battle_state.enemy_team:
            if enemy.is_fainted or victory_type == 'caught':
                # Calculate EXP
                exp = self._calculate_monster_exp(enemy, battle_state)
                
                # Calculate money
                money = self._calculate_monster_money(enemy, battle_state)
                rewards.money_gained += money
                
                # Calculate item drops
                items = self._calculate_item_drops(enemy, battle_state)
                rewards.items_gained.extend(items)
        
        # Distribute EXP among party
        total_exp = exp  # Simplified for single enemy
        participants = [m for m in battle_state.player_team if not m.is_fainted]
        exp_share = self._check_exp_share(battle_state)
        
        rewards.exp_gained = self.exp_system.distribute_exp(
            total_exp, 
            participants,
            exp_share
        )
        
        # Apply EXP and check for level ups  
        for monster, exp_amount in rewards.exp_gained.items():
            try:
                # Use gain_exp method
                if hasattr(monster, 'gain_exp'):
                    level_up_result = monster.gain_exp(exp_amount)
                    if level_up_result and hasattr(level_up_result, 'level_increased'):
                        rewards.level_ups[monster] = level_up_result
                elif hasattr(monster, 'current_exp'):
                    # Manual EXP addition
                    monster.current_exp += exp_amount
                    # Check for level up
                    if hasattr(monster, 'check_level_up'):
                        level_up_result = monster.check_level_up()
                        if level_up_result:
                            rewards.level_ups[monster] = level_up_result
                else:
                    logger.warning(f"Monster {monster.name} cannot gain EXP")
            except Exception as e:
                logger.error(f"Error applying EXP to {monster.name}: {e}")
        
        # Apply victory type bonuses
        if victory_type == 'perfect':
            rewards.money_gained = int(rewards.money_gained * 1.5)
            rewards.bonus_rewards['perfect_victory'] = True
        elif victory_type == 'caught':
            rewards.caught_monster = battle_state.enemy_active
            rewards.bonus_rewards['monster_caught'] = True
        
        return rewards
    
    def _calculate_monster_exp(self, monster, battle_state) -> int:
        """Calculate EXP from a single monster."""
        battle_type = 'wild'
        if hasattr(battle_state, 'battle_type'):
            if battle_state.battle_type.value == 'trainer':
                battle_type = 'trainer'
            elif battle_state.battle_type.value == 'boss':
                battle_type = 'boss'
        
        # Count participants
        participants = len([m for m in battle_state.player_team if getattr(m, 'participated', False)])
        if participants == 0:
            participants = 1  # At least one participated
        
        # Check for EXP-boosting items
        held_items = []
        if hasattr(battle_state.player_active, 'held_item'):
            held_items.append(battle_state.player_active.held_item)
        
        # Mark monster as participated
        if hasattr(monster, 'participated'):
            monster.participated = True
            
        return self.exp_system.calculate_battle_exp(
            monster,
            battle_type,
            participants,
            held_items
        )
    
    def _calculate_monster_money(self, monster, battle_state) -> int:
        """Calculate money reward from a single monster."""
        # Base money formula
        level = monster.level if hasattr(monster, 'level') else 5
        
        # Get rank
        rank = 'D'
        if hasattr(monster, 'rank'):
            rank = monster.rank
        elif hasattr(monster, 'species') and hasattr(monster.species, 'rank'):
            rank = monster.species.rank
        
        # Base money = level * rank_multiplier * random(8, 12)
        rank_mult = self.RANK_MONEY_MULTIPLIERS.get(rank, 1.0)
        base_money = int(level * rank_mult * random.randint(8, 12))
        
        # Battle type bonus
        if hasattr(battle_state, 'battle_type'):
            if battle_state.battle_type.value == 'trainer':
                base_money = int(base_money * 2.0)  # Trainers give double money
            elif battle_state.battle_type.value == 'boss':
                base_money = int(base_money * 3.0)  # Bosses give triple
        
        # Money-boosting items
        if hasattr(battle_state.player_active, 'held_item'):
            if battle_state.player_active.held_item == 'amulet_coin':
                base_money = int(base_money * 2.0)
            elif battle_state.player_active.held_item == 'luck_incense':
                base_money = int(base_money * 1.5)
        
        return max(1, base_money)
    
    def _calculate_item_drops(self, monster, battle_state) -> List[Tuple[str, int]]:
        """
        Calculate item drops from a defeated monster.
        
        Args:
            monster: Defeated monster
            battle_state: Current battle state
            
        Returns:
            List of (item_id, quantity) tuples
        """
        drops = []
        
        # Get monster's drop table
        drop_table = self._get_drop_table(monster)
        
        # Check each potential drop
        for drop in drop_table:
            # Calculate actual drop chance
            chance = drop.rarity.chance * drop.chance_modifier
            
            # Apply luck modifiers
            if hasattr(battle_state.player_active, 'held_item'):
                if battle_state.player_active.held_item == 'lucky_charm':
                    chance *= 1.5
            
            # Roll for drop
            if random.random() < chance:
                # Determine quantity (can be affected by abilities)
                quantity = drop.quantity
                if random.random() < 0.1:  # 10% chance for double drop
                    quantity *= 2
                
                drops.append((drop.item_id, quantity))
        
        # Guaranteed drops for certain conditions
        if hasattr(monster, 'rank'):
            if monster.rank in ['S', 'SS', 'X']:
                # High rank monsters always drop something
                if not drops:
                    drops.append(('rare_candy', 1))
        
        return drops
    
    def _get_drop_table(self, monster) -> List[ItemDrop]:
        """Get drop table for a specific monster."""
        # Check for specific monster drop table
        monster_id = None
        if hasattr(monster, 'species_id'):
            monster_id = monster.species_id
        elif hasattr(monster, 'species') and hasattr(monster.species, 'id'):
            monster_id = monster.species.id
        
        if monster_id and monster_id in self.drop_tables:
            return self.drop_tables[monster_id]
        
        # Use type-based drop table
        monster_type = 'beast'  # Default
        if hasattr(monster, 'types') and monster.types:
            first_type = monster.types[0].lower()
            
            # Map types to drop categories
            type_mapping = {
                'pflanze': 'plant',
                'bestie': 'beast',
                'teufel': 'demon',
                'gottheit': 'dragon',
                'seuche': 'undead',
                'chaos': 'demon',
                'mystik': 'material'
            }
            
            monster_type = type_mapping.get(first_type, 'beast')
        
        return self.DEFAULT_DROP_TABLES.get(monster_type, [])
    
    def _check_exp_share(self, battle_state) -> bool:
        """Check if EXP Share item is active."""
        # Check if any party member has EXP Share
        for monster in battle_state.player_team:
            if hasattr(monster, 'held_item') and monster.held_item == 'exp_share':
                return True
        
        # Check player inventory for active EXP Share
        if hasattr(battle_state, 'player_inventory'):
            return 'exp_share_active' in battle_state.player_inventory
        
        return False
    
    def apply_rewards(self, rewards: BattleRewards, game_state) -> Dict[str, Any]:
        """
        Apply rewards to the game state.
        
        Args:
            rewards: BattleRewards object
            game_state: Current game state
            
        Returns:
            Summary of applied rewards
        """
        summary = {
            'exp_gained': sum(rewards.exp_gained.values()),
            'money_gained': rewards.money_gained,
            'items_gained': rewards.items_gained,
            'level_ups': len(rewards.level_ups),
            'monsters_leveled': []
        }
        
        # Apply money
        if hasattr(game_state, 'player_money'):
            game_state.player_money += rewards.money_gained
        elif hasattr(game_state, 'player') and hasattr(game_state.player, 'money'):
            game_state.player.money += rewards.money_gained
        
        # Apply items to inventory
        if hasattr(game_state, 'inventory'):
            for item_id, quantity in rewards.items_gained:
                if item_id in game_state.inventory:
                    game_state.inventory[item_id] += quantity
                else:
                    game_state.inventory[item_id] = quantity
        
        # Process level ups
        for monster, level_up_result in rewards.level_ups.items():
            monster_name = monster.name if hasattr(monster, 'name') else 'Monster'
            summary['monsters_leveled'].append({
                'name': monster_name,
                'new_level': level_up_result.new_level,
                'stat_gains': level_up_result.stat_gains,
                'new_moves': level_up_result.new_moves
            })
        
        # Handle caught monster
        if rewards.caught_monster:
            summary['caught_monster'] = rewards.caught_monster.name if hasattr(rewards.caught_monster, 'name') else 'Monster'
        
        return summary
    
    def generate_treasure_chest_rewards(self, chest_tier: str = 'common') -> BattleRewards:
        """
        Generate rewards for opening a treasure chest.
        
        Args:
            chest_tier: Tier of chest (common, uncommon, rare, legendary)
            
        Returns:
            BattleRewards with chest contents
        """
        rewards = BattleRewards(
            exp_gained={},
            money_gained=0,
            items_gained=[],
            level_ups={}
        )
        
        # Money rewards by tier
        money_ranges = {
            'common': (10, 50),
            'uncommon': (50, 200),
            'rare': (200, 500),
            'legendary': (500, 2000)
        }
        
        min_money, max_money = money_ranges.get(chest_tier, (10, 50))
        rewards.money_gained = random.randint(min_money, max_money)
        
        # Item rewards
        item_counts = {
            'common': random.randint(1, 2),
            'uncommon': random.randint(2, 3),
            'rare': random.randint(2, 4),
            'legendary': random.randint(3, 5)
        }
        
        num_items = item_counts.get(chest_tier, 1)
        
        # Generate random items based on tier
        for _ in range(num_items):
            item = self._generate_random_item(chest_tier)
            if item:
                rewards.items_gained.append(item)
        
        return rewards
    
    def _generate_random_item(self, tier: str) -> Optional[Tuple[str, int]]:
        """Generate a random item based on tier."""
        # Item pools by tier
        item_pools = {
            'common': [
                ('trank', 1), ('kräuter', 2), ('fleisch', 1),
                ('gegengift', 1), ('brandsalbe', 1)
            ],
            'uncommon': [
                ('supertrank', 1), ('äther', 1), ('edelfleisch', 1),
                ('x_angriff', 1), ('x_verteidigung', 1)
            ],
            'rare': [
                ('hypertrank', 1), ('top_äther', 1), ('elixier', 1),
                ('seltene_süßigkeit', 1), ('meistertrank', 1)
            ],
            'legendary': [
                ('top_elixier', 1), ('götterfleisch', 1),
                ('meisterball', 1), ('goldnugget', 1)
            ]
        }
        
        pool = item_pools.get(tier, item_pools['common'])
        return random.choice(pool) if pool else None


# Global instance for easy access
_reward_system_instance = None

def get_reward_system() -> RewardSystem:
    """Get the global reward system instance."""
    global _reward_system_instance
    if _reward_system_instance is None:
        _reward_system_instance = RewardSystem()
    return _reward_system_instance
