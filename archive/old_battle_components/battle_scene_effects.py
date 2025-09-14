# ARCHIVED: 2025-09-03 - Consolidated into engine/scenes/battle_scene_components.py
"""
Battle Scene Effects and Rewards.
Handles status effects, experience distribution, and battle end conditions.
"""

from typing import TYPE_CHECKING
from engine.systems.monster_instance import MonsterInstance

if TYPE_CHECKING:
    from engine.scenes.battle_scene import BattleScene
    from engine.systems.battle.battle_enums import BattleResult


class BattleEffectsManager:
    """Manages battle effects and rewards."""
    
    def __init__(self, scene: 'BattleScene'):
        self.scene = scene
        self.game = scene.game
        self.battle_state = scene.battle_state
        self.battle_ui = scene.battle_ui
    
    def process_status_effects(self):
        """Process end-of-turn status effects via BattleController."""
        # Let BattleController handle status effects
        if hasattr(self.scene, 'battle_controller'):
            self.scene.battle_controller.process_status_effects()
        else:
            # Fallback: show message but don't process
            self.battle_ui.show_message("Battle-Controller nicht verfügbar für Status-Effekte!")
    
    def check_defeated(self):
        """Check for defeated monsters via BattleController."""
        # Let BattleController handle defeated monster checks
        if hasattr(self.scene, 'battle_controller'):
            self.scene.battle_controller.check_defeated_monsters()
        else:
            # Fallback: show message but don't process
            self.battle_ui.show_message("Battle-Controller nicht verfügbar für Defeat-Check!")
    
    def check_battle_end(self) -> 'BattleResult':
        """Check if battle should end via BattleController."""
        from engine.systems.battle.battle_enums import BattleResult
        
        # Let BattleController handle battle end checks
        if hasattr(self.scene, 'battle_controller'):
            return self.scene.battle_controller.check_battle_end()
        else:
            # Fallback: return ongoing
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
