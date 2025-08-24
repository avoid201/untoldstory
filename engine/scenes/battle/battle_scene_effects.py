"""
Battle Scene Effects and Rewards.
Handles status effects, experience distribution, and battle end conditions.
"""

from typing import TYPE_CHECKING
from engine.systems.monster_instance import MonsterInstance

if TYPE_CHECKING:
    from .battle_scene_main import BattleScene, BattleResult


class BattleEffectsManager:
    """Manages battle effects and rewards."""
    
    def __init__(self, scene: 'BattleScene'):
        self.scene = scene
        self.game = scene.game
        self.battle_state = scene.battle_state
        self.battle_ui = scene.battle_ui
    
    def process_status_effects(self):
        """Process end-of-turn status effects."""
        # Process all monsters
        all_monsters = [
            (f'player_{i}', m) for i, m in enumerate(self.battle_state.player_team) if m
        ] + [
            (f'enemy_{i}', m) for i, m in enumerate(self.battle_state.enemy_team) if m
        ]
        
        for actor_id, monster in all_monsters:
            if monster.current_hp <= 0:
                continue
            
            # Process status
            if monster.status == 'burn':
                damage = max(1, monster.max_hp // 16)
                monster.current_hp = max(0, monster.current_hp - damage)
                self.battle_ui.set_hp(actor_id, monster.current_hp)
                self.battle_ui.show_message(
                    f"{monster.nickname or monster.species_name} leidet unter Verbrennung!"
                )
            
            elif monster.status == 'poison':
                damage = max(1, monster.max_hp // 8)
                monster.current_hp = max(0, monster.current_hp - damage)
                self.battle_ui.set_hp(actor_id, monster.current_hp)
                self.battle_ui.show_message(
                    f"{monster.nickname or monster.species_name} leidet unter Gift!"
                )
    
    def check_defeated(self):
        """Check for defeated monsters and handle them."""
        # Check player team
        for i, monster in enumerate(self.battle_state.player_team):
            if monster and monster.current_hp <= 0 and monster.status != 'fainted':
                monster.status = 'fainted'
                self.battle_ui.show_message(
                    f"{monster.nickname or monster.species_name} wurde besiegt!"
                )
        
        # Check enemy team
        for i, monster in enumerate(self.battle_state.enemy_team):
            if monster and monster.current_hp <= 0 and monster.status != 'fainted':
                monster.status = 'fainted'
                self.battle_ui.show_message(
                    f"{monster.species_name} wurde besiegt!"
                )
                
                # Calculate experience
                exp = self.calculate_exp_reward(monster)
                self.scene.exp_gained += exp
    
    def check_battle_end(self) -> 'BattleResult':
        """Check if battle should end."""
        from ..battle_scene_main import BattleResult
        
        # Check if all player monsters fainted
        player_alive = any(
            m and m.current_hp > 0 
            for m in self.battle_state.player_team
        )
        
        if not player_alive:
            return BattleResult.DEFEAT
        
        # Check if all enemy monsters fainted
        enemy_alive = any(
            m and m.current_hp > 0 
            for m in self.battle_state.enemy_team
        )
        
        if not enemy_alive:
            return BattleResult.VICTORY
        
        return BattleResult.ONGOING
    
    def calculate_exp_reward(self, defeated: MonsterInstance) -> int:
        """Calculate experience points for defeating a monster."""
        # Base EXP based on level and rank
        rank_multipliers = {
            'F': 0.5, 'E': 0.7, 'D': 0.9, 'C': 1.0,
            'B': 1.2, 'A': 1.5, 'S': 2.0, 'SS': 2.5, 'X': 3.0
        }
        
        base_exp = defeated.level * 10
        rank_mult = rank_multipliers.get(defeated.rank, 1.0)
        
        # Wild vs trainer bonus
        trainer_mult = 1.5 if not self.scene.is_wild else 1.0
        
        # Boss bonus
        boss_mult = 2.0 if self.scene.is_boss else 1.0
        
        return int(base_exp * rank_mult * trainer_mult * boss_mult)
    
    def distribute_rewards(self):
        """Distribute EXP and items to party."""
        if self.scene.exp_gained > 0:
            # Distribute to all participating monsters
            participants = [
                m for m in self.battle_state.player_team 
                if m and m.current_hp > 0
            ]
            
            if participants:
                exp_per_monster = self.scene.exp_gained // len(participants)
                
                for monster in participants:
                    old_level = monster.level
                    monster.gain_exp(exp_per_monster)
                    
                    self.battle_ui.show_message(
                        f"{monster.nickname or monster.species_name} kriegt {exp_per_monster} EXP!"
                    )
                    
                    # Check for level up
                    if monster.level > old_level:
                        self.battle_ui.show_message(
                            f"{monster.nickname or monster.species_name} ist jetzt Level {monster.level}!"
                        )
                        
                        # Check for new moves
                        if hasattr(monster, 'check_learned_moves'):
                            new_moves = monster.check_learned_moves()
                            for move_id in new_moves:
                                move = self.game.resources.get_move(move_id)
                                if move:
                                    self.battle_ui.show_message(
                                        f"{monster.nickname or monster.species_name} lernt {move.name}!"
                                    )
                                    
                                    # Track learned moves for sync
                                    if not hasattr(monster, 'new_moves_learned'):
                                        monster.new_moves_learned = []
                                    monster.new_moves_learned.append(move_id)
    
    def sync_party_after_battle(self):
        """Sync party monsters with battle state changes."""
        # Update party monsters with battle changes (HP, EXP, status, new moves)
        for i, battle_monster in enumerate(self.battle_state.player_team):
            if battle_monster and i < len(self.game.party_manager.party.members):
                party_monster = self.game.party_manager.party.members[i]
                if party_monster and party_monster.id == battle_monster.id:
                    # Sync HP and status
                    party_monster.current_hp = battle_monster.current_hp
                    party_monster.status = battle_monster.status
                    
                    # Sync EXP and level
                    party_monster.experience = battle_monster.experience
                    party_monster.level = battle_monster.level
                    
                    # Sync PP for moves
                    party_monster.moves = battle_monster.moves
                    
                    # Sync any new moves learned
                    if hasattr(battle_monster, 'new_moves_learned'):
                        for move_id in battle_monster.new_moves_learned:
                            party_monster.learn_move(move_id)
    
    def finalize_caught_monster(self):
        """Add caught monster to party or storage."""
        if self.scene.caught_monster:
            success, message = self.game.party_manager.add_to_party(self.scene.caught_monster)
            print(f"Monster caught: {message}")
    
    def handle_defeat(self):
        """Handle player defeat."""
        # Heal party and return to last heal point
        self.game.party_manager.party.heal_all()
        
        # Set player position to last heal point
        if hasattr(self.game, 'last_heal_point'):
            # Return to last saved position
            pass
        else:
            # Return to player house as default
            self.game.current_map = 'player_house'
            self.game.player_pos = (5, 5)
