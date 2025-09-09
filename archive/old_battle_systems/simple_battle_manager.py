"""
Simplified Battle Manager für direkte Integration
=================================================
"""

from enum import Enum, auto
from typing import Dict, List, Optional, Any


class BattlePhase(Enum):
    """Battle phases."""
    INIT = auto()
    START = auto()
    INPUT = auto()
    EXECUTE = auto()
    AFTERMATH = auto()
    END = auto()


class BattleResult(Enum):
    """Battle results."""
    ONGOING = auto()
    VICTORY = auto()
    DEFEAT = auto()
    FLED = auto()
    CAUGHT = auto()


class SimpleBattleManager:
    """Simplified battle manager for direct scene integration."""
    
    def __init__(self, game):
        """Initialize the simple battle manager."""
        self.game = game
        self.phase = BattlePhase.INIT
        self.result = BattleResult.ONGOING
        
        # Teams
        self.player_team = []
        self.enemy_team = []
        self.player_active = None
        self.enemy_active = None
        
        # Battle stats
        self.turn_count = 0
        self.exp_gained = 0
        self.money_gained = 0
        self.items_gained = []
        
    def start_battle(self, player_team: List, enemy_team: List, **kwargs) -> bool:
        """Start a new battle."""
        self.player_team = player_team
        self.enemy_team = enemy_team
        
        # Set active monsters
        self.player_active = self._get_first_conscious(player_team)
        self.enemy_active = self._get_first_conscious(enemy_team)
        
        if not self.player_active or not self.enemy_active:
            return False
        
        # Reset battle state
        self.phase = BattlePhase.START
        self.result = BattleResult.ONGOING
        self.turn_count = 0
        self.exp_gained = 0
        self.money_gained = 0
        self.items_gained = []
        
        return True
    
    def calculate_rewards(self, defeated_monster) -> Dict[str, Any]:
        """Calculate rewards for defeating a monster."""
        rewards = {
            'exp': 0,
            'money': 0,
            'items': []
        }
        
        # Base EXP calculation
        base_exp = defeated_monster.level * 10
        
        # Rank multiplier
        rank_multipliers = {
            'F': 0.5, 'E': 0.7, 'D': 0.9, 'C': 1.0,
            'B': 1.2, 'A': 1.5, 'S': 2.0, 'SS': 2.5, 'X': 3.0
        }
        
        # Get rank safely
        if hasattr(defeated_monster, 'rank'):
            rank = defeated_monster.rank
            if hasattr(rank, 'value'):
                rank_str = rank.value
            else:
                rank_str = str(rank)
        else:
            rank_str = 'E'
        
        rank_mult = rank_multipliers.get(rank_str, 1.0)
        
        # Calculate final EXP
        rewards['exp'] = int(base_exp * rank_mult)
        
        # Money calculation (simple)
        rewards['money'] = defeated_monster.level * 5
        
        # Random item chance (10%)
        import random
        if random.random() < 0.1:
            rewards['items'].append({'name': 'Potion', 'quantity': 1})
        
        return rewards
    
    def distribute_exp(self, exp_amount: int) -> List[Dict]:
        """Distribute EXP to party members."""
        results = []
        
        # Get conscious party members
        participants = [m for m in self.player_team if m and m.current_hp > 0]
        
        if not participants:
            return results
        
        # Split EXP
        exp_per_monster = exp_amount // len(participants)
        
        for monster in participants:
            old_level = monster.level
            
            # Add EXP
            if hasattr(monster, 'gain_exp'):
                exp_result = monster.gain_exp(exp_per_monster)
            else:
                # Manual EXP addition
                if not hasattr(monster, 'exp'):
                    monster.exp = 0
                monster.exp += exp_per_monster
                
                # Check level up
                exp_to_next = monster.level * 100
                if monster.exp >= exp_to_next:
                    monster.level += 1
                    # Recalculate stats if method exists
                    if hasattr(monster, '_calculate_stats'):
                        monster._calculate_stats()
                    monster.current_hp = monster.max_hp
                    exp_result = {'leveled_up': True, 'new_level': monster.level}
                else:
                    exp_result = {'leveled_up': False}
            
            results.append({
                'monster': monster.name,
                'exp_gained': exp_per_monster,
                'old_level': old_level,
                'new_level': monster.level,
                'leveled_up': monster.level > old_level
            })
        
        return results
    
    def process_victory(self) -> Dict[str, Any]:
        """Process victory and calculate all rewards."""
        total_rewards = {
            'exp': 0,
            'money': 0,
            'items': [],
            'level_ups': []
        }
        
        # Calculate rewards for each defeated enemy
        for enemy in self.enemy_team:
            if enemy:
                rewards = self.calculate_rewards(enemy)
                total_rewards['exp'] += rewards['exp']
                total_rewards['money'] += rewards['money']
                total_rewards['items'].extend(rewards['items'])
        
        # Distribute EXP
        if total_rewards['exp'] > 0:
            level_ups = self.distribute_exp(total_rewards['exp'])
            total_rewards['level_ups'] = level_ups
        
        # Store totals
        self.exp_gained = total_rewards['exp']
        self.money_gained = total_rewards['money']
        self.items_gained = total_rewards['items']
        
        # Add money to player
        if hasattr(self.game, 'player_money'):
            self.game.player_money += total_rewards['money']
        
        return total_rewards
    
    def _get_first_conscious(self, team: List) -> Optional[Any]:
        """Get first conscious monster from team."""
        for monster in team:
            if monster and monster.current_hp > 0:
                return monster
        return None
    
    def check_battle_end(self) -> BattleResult:
        """Check if battle should end."""
        # Check player team
        player_alive = any(m for m in self.player_team if m and m.current_hp > 0)
        if not player_alive:
            self.result = BattleResult.DEFEAT
            return self.result
        
        # Check enemy team
        enemy_alive = any(m for m in self.enemy_team if m and m.current_hp > 0)
        if not enemy_alive:
            self.result = BattleResult.VICTORY
            # Process victory rewards
            self.process_victory()
            return self.result
        
        return BattleResult.ONGOING
