"""
Battle Scene Action Execution.
Handles execution of battle actions like attacks, items, fleeing, etc.
"""

import random
from typing import Optional, Dict, TYPE_CHECKING

from engine.systems.monster_instance import MonsterInstance

if TYPE_CHECKING:
    from .battle_scene_main import BattleScene


class BattleActionExecutor:
    """Handles execution of battle actions."""
    
    def __init__(self, scene: 'BattleScene'):
        self.scene = scene
        self.game = scene.game
        self.battle_state = scene.battle_state
        self.battle_ui = scene.battle_ui
    
    def execute_action(self, action: Dict):
        """Execute a single action."""
        actor_id = action['actor']
        action_type = action['type']
        
        # Get actor monster
        if actor_id.startswith('player'):
            idx = int(actor_id.split('_')[1])
            actor = self.battle_state.player_team[idx]
        else:
            idx = int(actor_id.split('_')[1])
            actor = self.battle_state.enemy_team[idx]
        
        if not actor or actor.current_hp <= 0:
            return
        
        # Execute based on type
        if action_type == 'attack':
            self.execute_attack(actor, action)
        elif action_type == 'tame':
            self.execute_tame(actor, action)
        elif action_type == 'item':
            self.execute_item(actor, action)
        elif action_type == 'flee':
            self.execute_flee(actor, action)
    
    def execute_attack(self, actor: MonsterInstance, action: Dict):
        """Execute an attack action."""
        move_id = action['move_id']
        targets = action.get('targets', [])
        
        # Get move data
        move_data = self.game.resources.get_move(move_id)
        if not move_data:
            return
        
        # Show attack message
        self.battle_ui.show_message(
            f"{actor.nickname or actor.species_name} setzt {move_data.name} ein!"
        )
        
        # Execute against each target
        for target_id in targets:
            # Get target monster
            if target_id.startswith('player'):
                idx = int(target_id.split('_')[1])
                target = self.battle_state.player_team[idx]
            else:
                idx = int(target_id.split('_')[1])
                target = self.battle_state.enemy_team[idx]
            
            if not target or target.current_hp <= 0:
                continue
            
            # Calculate damage
            result = self.scene.turn_manager.execute_move(
                actor, target, move_data, self.battle_state
            )
            
            # Apply damage
            if result['hit']:
                damage = result.get('damage', 0)
                if damage > 0:
                    target.current_hp = max(0, target.current_hp - damage)
                    
                    # Update UI
                    self.battle_ui.set_hp(target_id, target.current_hp)
                    self.battle_ui.shake_sprite(target_id)
                    
                    # Show damage message
                    effectiveness = result.get('effectiveness', 1.0)
                    if effectiveness > 1.5:
                        self.battle_ui.show_message("Volltreffer! Richtig effektiv!")
                    elif effectiveness > 1.0:
                        self.battle_ui.show_message("Effektiv!")
                    elif effectiveness < 0.5:
                        self.battle_ui.show_message("Kaum Wirkung...")
                    elif effectiveness < 1.0:
                        self.battle_ui.show_message("Nicht sehr effektiv...")
                    
                    # Check if critical
                    if result.get('critical'):
                        self.battle_ui.show_message("Kritischer Treffer!")
                
                # Apply status effects
                if result.get('status'):
                    target.status = result['status']
                    self.battle_ui.show_message(
                        f"{target.nickname or target.species_name} hat jetzt {result['status']}!"
                    )
            else:
                self.battle_ui.show_message("Daneben!")
    
    def execute_tame(self, actor: MonsterInstance, action: Dict):
        """Execute a taming attempt."""
        # Only works on wild monsters
        if not self.scene.is_wild:
            self.battle_ui.show_message("Kannst du knicken bei Trainer-Monstern!")
            return
        
        # Get target (first enemy)
        target = self.battle_state.enemy_team[0] if self.battle_state.enemy_team else None
        if not target:
            return
        
        # Calculate taming chance
        from engine.systems.taming import calculate_tame_chance
        chance = calculate_tame_chance(
            target,
            self.battle_state.player_team,
            self.battle_state
        )
        
        # Show chance
        self.battle_ui.show_message(f"Zähm-Chance: {int(chance * 100)}%")
        
        # Roll for success
        if random.random() < chance:
            # Success!
            self.battle_ui.show_message(f"{target.species_name} wurde gezähmt!")
            from ..battle_scene_main import BattleResult
            self.scene.battle_result = BattleResult.CAUGHT
            
            # Store caught monster for later processing
            self.scene.caught_monster = target
            
            # Show where it goes
            if len(self.game.party_manager.party.get_all_members()) < 6:
                self.battle_ui.show_message(f"{target.species_name} kommt in dein Team!")
            else:
                current_box = self.game.party_manager.storage.get_current_box()
                box_name = current_box.name if current_box else "Box"
                self.battle_ui.show_message(f"{target.species_name} wurde in {box_name} gepackt!")
        else:
            # Failed
            self.battle_ui.show_message("Mist! Hat nicht geklappt!")
            
            # Apply irritation
            if not hasattr(target, 'buffs'):
                target.buffs = []
            target.buffs.append({
                'type': 'irritated',
                'duration': -1
            })
    
    def execute_item(self, actor: MonsterInstance, action: Dict):
        """Execute item use."""
        item_id = action.get('item_id')
        target_id = action.get('target')
        
        # Get item from inventory
        if hasattr(self.game, 'inventory'):
            item = self.game.inventory.get_item(item_id)
            if item:
                # Use item effect
                if item.type == 'healing':
                    # Heal target
                    if target_id.startswith('player'):
                        idx = int(target_id.split('_')[1])
                        target = self.battle_state.player_team[idx]
                        if target:
                            heal_amount = item.value
                            target.current_hp = min(target.max_hp, target.current_hp + heal_amount)
                            self.battle_ui.set_hp(target_id, target.current_hp)
                            self.battle_ui.show_message(
                                f"{target.nickname or target.species_name} wurde um {heal_amount} HP geheilt!"
                            )
                
                # Remove item from inventory
                self.game.inventory.remove_item(item_id, 1)
            else:
                self.battle_ui.show_message("Item nicht gefunden!")
        else:
            self.battle_ui.show_message("Items sind noch nicht implementiert!")
    
    def execute_flee(self, actor: MonsterInstance, action: Dict):
        """Attempt to flee from battle."""
        if not self.scene.can_flee:
            self.battle_ui.show_message("Hier gibt's kein Entkommen!")
            return
        
        # Calculate flee chance based on speed
        flee_chance = 0.5  # Base chance
        
        if self.battle_state.enemy_team:
            enemy_speed = max(m.stats['spd'] for m in self.battle_state.enemy_team if m)
            player_speed = actor.stats['spd']
            
            speed_ratio = player_speed / enemy_speed if enemy_speed > 0 else 1
            flee_chance = min(0.95, 0.3 + 0.4 * speed_ratio)
        
        # Roll for flee
        if random.random() < flee_chance:
            self.battle_ui.show_message("Du bist erfolgreich abgehauen!")
            from ..battle_scene_main import BattleResult
            self.scene.battle_result = BattleResult.FLED
        else:
            self.battle_ui.show_message("Kannst nicht abhauen!")
