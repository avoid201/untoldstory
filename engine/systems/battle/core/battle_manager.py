"""
Simplified Battle Manager for DQM-style battles.
Handles core battle flow with proper HP management and scene transitions.
"""

import pygame
import random
from typing import Optional, List, Dict, Any
from enum import Enum, auto


class BattlePhase(Enum):
    """Battle phases."""
    INIT = auto()
    INPUT = auto()
    EXECUTE = auto()
    END = auto()


class BattleResult(Enum):
    """Battle outcomes."""
    ONGOING = auto()
    VICTORY = auto()
    DEFEAT = auto()
    FLED = auto()


class SimpleBattleManager:
    """Simplified battle manager that actually works."""
    
    def __init__(self, game):
        self.game = game
        
        # Battle state
        self.player_team: List = []
        self.enemy_team: List = []
        self.player_active = None
        self.enemy_active = None
        
        # Battle config
        self.is_wild = True
        self.can_flee = True
        
        # Battle flow
        self.phase = BattlePhase.INIT
        self.result = BattleResult.ONGOING
        self.turn_count = 0
        
        # UI state
        self.waiting_for_input = False
        self.messages: List[str] = []
        
    def start_battle(self, player_team: List, enemy_team: List, **kwargs) -> bool:
        """Initialize battle with proper HP setup."""
        try:
            # Store teams
            self.player_team = player_team
            self.enemy_team = enemy_team
            
            # Battle config
            self.is_wild = kwargs.get('is_wild', True)
            self.can_flee = kwargs.get('can_flee', True) and self.is_wild
            
            # CRITICAL: Ensure all monsters have proper HP
            for monster in self.player_team + self.enemy_team:
                if not hasattr(monster, 'current_hp'):
                    monster.current_hp = getattr(monster, 'max_hp', 100)
                if not hasattr(monster, 'max_hp'):
                    monster.max_hp = 100
                    monster.current_hp = 100
                # Ensure HP is positive
                if monster.current_hp <= 0:
                    monster.current_hp = monster.max_hp
                # Add is_fainted flag
                monster.is_fainted = False
                
                print(f"Monster {monster.name}: HP {monster.current_hp}/{monster.max_hp}")
            
            # Set active monsters
            self.player_active = self.player_team[0] if self.player_team else None
            self.enemy_active = self.enemy_team[0] if self.enemy_team else None
            
            if not self.player_active or not self.enemy_active:
                print("ERROR: No active monsters!")
                return False
            
            # Reset battle state
            self.phase = BattlePhase.INPUT
            self.result = BattleResult.ONGOING
            self.turn_count = 0
            self.waiting_for_input = True
            
            # Initial message
            if self.is_wild:
                self.add_message(f"A wild {self.enemy_active.name} appeared!")
            else:
                self.add_message("Trainer battle started!")
            
            print(f"Battle started: {self.player_active.name} vs {self.enemy_active.name}")
            return True
            
        except Exception as e:
            print(f"Error starting battle: {e}")
            return False
    
    def handle_player_attack(self, move_index: int = 0) -> bool:
        """Execute player attack with visual feedback."""
        try:
            if not self.player_active or not self.enemy_active:
                return False
            
            # Get move
            move = None
            if hasattr(self.player_active, 'moves') and self.player_active.moves:
                if move_index < len(self.player_active.moves):
                    move = self.player_active.moves[move_index]
            
            move_name = move.name if move and hasattr(move, 'name') else "Tackle"
            move_power = move.power if move and hasattr(move, 'power') else 40
            
            # Show attack message
            self.add_message(f"{self.player_active.name} uses {move_name}!")
            
            # Calculate damage (simplified)
            level = getattr(self.player_active, 'level', 5)
            atk = self.player_active.stats.get('atk', 50) if hasattr(self.player_active, 'stats') else 50
            defense = self.enemy_active.stats.get('def', 50) if hasattr(self.enemy_active, 'stats') else 50
            
            # Simple damage formula
            damage = max(1, (move_power * atk // defense) + random.randint(1, level))
            
            # Apply damage
            old_hp = self.enemy_active.current_hp
            self.enemy_active.current_hp = max(0, self.enemy_active.current_hp - damage)
            
            # Show damage message
            self.add_message(f"{self.enemy_active.name} takes {damage} damage!")
            print(f"Damage dealt: {damage} ({old_hp} -> {self.enemy_active.current_hp})")
            
            # Check if enemy fainted
            if self.enemy_active.current_hp <= 0:
                self.enemy_active.is_fainted = True
                self.add_message(f"{self.enemy_active.name} fainted!")
                
                # Check for more enemies
                if not self.switch_enemy():
                    self.result = BattleResult.VICTORY
                    self.phase = BattlePhase.END
                    self.add_message("Victory! You won the battle!")
                    return True
            
            # Enemy turn
            self.execute_enemy_turn()
            
            return True
            
        except Exception as e:
            print(f"Error in player attack: {e}")
            return False
    
    def execute_enemy_turn(self) -> None:
        """Simple enemy AI turn."""
        try:
            if not self.enemy_active or self.enemy_active.is_fainted:
                return
            
            if not self.player_active or self.player_active.is_fainted:
                return
            
            # Simple attack
            level = getattr(self.enemy_active, 'level', 5)
            atk = self.enemy_active.stats.get('atk', 50) if hasattr(self.enemy_active, 'stats') else 50
            defense = self.player_active.stats.get('def', 50) if hasattr(self.player_active, 'stats') else 50
            
            damage = max(1, (40 * atk // defense) + random.randint(1, level))
            
            # Apply damage
            old_hp = self.player_active.current_hp
            self.player_active.current_hp = max(0, self.player_active.current_hp - damage)
            
            self.add_message(f"{self.enemy_active.name} attacks for {damage} damage!")
            print(f"Enemy damage: {damage} ({old_hp} -> {self.player_active.current_hp})")
            
            # Check if player fainted
            if self.player_active.current_hp <= 0:
                self.player_active.is_fainted = True
                self.add_message(f"{self.player_active.name} fainted!")
                
                # Check for more party members
                if not self.switch_player():
                    self.result = BattleResult.DEFEAT
                    self.phase = BattlePhase.END
                    self.add_message("Defeat! You lost the battle!")
            
        except Exception as e:
            print(f"Error in enemy turn: {e}")
    
    def handle_flee(self) -> bool:
        """Attempt to flee from battle."""
        if not self.can_flee:
            self.add_message("Can't escape!")
            return False
        
        # Simple flee chance
        flee_chance = 0.5
        if self.player_active and self.enemy_active:
            player_spd = self.player_active.stats.get('spd', 50) if hasattr(self.player_active, 'stats') else 50
            enemy_spd = self.enemy_active.stats.get('spd', 50) if hasattr(self.enemy_active, 'stats') else 50
            flee_chance = min(0.9, 0.3 + (player_spd / max(1, enemy_spd)) * 0.4)
        
        if random.random() < flee_chance:
            self.add_message("Got away safely!")
            self.result = BattleResult.FLED
            self.phase = BattlePhase.END
            return True
        else:
            self.add_message("Can't escape!")
            # Enemy gets a turn
            self.execute_enemy_turn()
            return False
    
    def handle_item(self, item_id: str = None) -> bool:
        """Use an item (placeholder)."""
        self.add_message("Items not yet implemented!")
        return False
    
    def handle_switch(self, monster_index: int = -1) -> bool:
        """Switch active monster."""
        if monster_index < 0 or monster_index >= len(self.player_team):
            # Show switch menu
            available = []
            for i, monster in enumerate(self.player_team):
                if monster and not monster.is_fainted and monster != self.player_active:
                    available.append((i, monster))
            
            if not available:
                self.add_message("No other monsters available!")
                return False
            
            # For now, switch to first available
            monster_index = available[0][0]
        
        new_monster = self.player_team[monster_index]
        if new_monster.is_fainted:
            self.add_message(f"{new_monster.name} has fainted!")
            return False
        
        if new_monster == self.player_active:
            self.add_message(f"{new_monster.name} is already in battle!")
            return False
        
        self.player_active = new_monster
        self.add_message(f"Go, {new_monster.name}!")
        
        # Enemy gets a turn after switch
        self.execute_enemy_turn()
        return True
    
    def switch_player(self) -> bool:
        """Auto-switch to next available monster."""
        for monster in self.player_team:
            if monster and not monster.is_fainted and monster != self.player_active:
                self.player_active = monster
                self.add_message(f"Go, {monster.name}!")
                return True
        return False
    
    def switch_enemy(self) -> bool:
        """Auto-switch to next enemy."""
        for monster in self.enemy_team:
            if monster and not monster.is_fainted and monster != self.enemy_active:
                self.enemy_active = monster
                self.add_message(f"Enemy sends out {monster.name}!")
                return True
        return False
    
    def add_message(self, message: str) -> None:
        """Add a battle message."""
        self.messages.append(message)
        print(f"Battle: {message}")
    
    def get_messages(self) -> List[str]:
        """Get and clear messages."""
        messages = self.messages.copy()
        self.messages.clear()
        return messages
    
    def update(self, dt: float) -> None:
        """Update battle state."""
        # Check battle end
        if self.result != BattleResult.ONGOING:
            self.phase = BattlePhase.END
    
    def is_battle_over(self) -> bool:
        """Check if battle has ended."""
        return self.result != BattleResult.ONGOING
    
    def get_result(self) -> BattleResult:
        """Get battle result."""
        return self.result
    
    def end_battle(self) -> Dict[str, Any]:
        """End battle and return results."""
        results = {
            'result': self.result,
            'turn_count': self.turn_count,
            'exp_gained': 0,
            'money_gained': 0
        }
        
        # Calculate rewards for victory
        if self.result == BattleResult.VICTORY:
            for monster in self.enemy_team:
                if monster:
                    level = getattr(monster, 'level', 5)
                    results['exp_gained'] += level * 10
                    results['money_gained'] += level * 5
        
        # Sync party HP
        if hasattr(self.game, 'party_manager'):
            for i, monster in enumerate(self.player_team):
                if i < len(self.game.party_manager.party.members):
                    party_mon = self.game.party_manager.party.members[i]
                    if party_mon:
                        party_mon.current_hp = monster.current_hp
                        if monster.is_fainted:
                            party_mon.status = 'fainted'
        
        print(f"Battle ended: {self.result.name}")
        return results
