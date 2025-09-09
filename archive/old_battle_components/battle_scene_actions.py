# ARCHIVED: 2025-09-03 - Consolidated into engine/scenes/battle_scene_components.py
"""
Battle Scene Action Execution.
Handles execution of battle actions like attacks, items, fleeing, etc.
"""

import random
from typing import Optional, Dict, TYPE_CHECKING

from engine.systems.monster_instance import MonsterInstance

if TYPE_CHECKING:
    from engine.scenes.battle_scene import BattleScene


class BattleSceneActionHandler:
    """Handles battle action execution within the BattleScene context."""
    
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
        """Execute an attack action via BattleController."""
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
        
        # Execute against each target via BattleController
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
            
            # Create BattleAction and queue with controller
            from engine.systems.battle.turn_logic_clean import BattleAction, ActionType
            attack_action = BattleAction(
                actor=actor,
                action_type=ActionType.ATTACK,
                move=move_data,
                target=target
            )
            
            # Let BattleController handle execution
            if hasattr(self.scene, 'battle_controller'):
                self.scene.battle_controller.queue_action(attack_action)
            else:
                # Fallback: show message but don't execute
                self.battle_ui.show_message("Battle-Controller nicht verfügbar!")
    
    def execute_tame(self, actor: MonsterInstance, action: Dict):
        """Execute a taming attempt via BattleController."""
        # Only works on wild monsters
        if not self.scene.is_wild:
            self.battle_ui.show_message("Kannst du knicken bei Trainer-Monstern!")
            return
        
        # Get target (first enemy)
        target = self.battle_state.enemy_team[0] if self.battle_state.enemy_team else None
        if not target:
            return
        
        # Get meat bonus from action if available
        meat_bonus = action.get('meat_bonus', 0)
        
        # Create BattleAction and queue with controller
        from engine.systems.battle.turn_logic_clean import BattleAction, ActionType
        taming_action = BattleAction(
            actor=actor,
            action_type=ActionType.TAME,
            target=target,
            meat_bonus=meat_bonus
        )
        
        # Let BattleController handle execution
        if hasattr(self.scene, 'battle_controller'):
            self.scene.battle_controller.queue_action(taming_action)
        else:
            # Fallback: show message but don't execute
            self.battle_ui.show_message("Battle-Controller nicht verfügbar!")
    
    def execute_item(self, actor: MonsterInstance, action: Dict):
        """Execute item use via BattleController."""
        item_id = action.get('item_id')
        target_id = action.get('target')
        
        # Get target monster
        target = None
        if target_id.startswith('player'):
            idx = int(target_id.split('_')[1])
            target = self.battle_state.player_team[idx]
        else:
            idx = int(target_id.split('_')[1])
            target = self.battle_state.enemy_team[idx]
        
        if not target:
            self.battle_ui.show_message("Ziel nicht gefunden!")
            return
        
        # Create BattleAction and queue with controller
        from engine.systems.battle.turn_logic_clean import BattleAction, ActionType
        item_action = BattleAction(
            actor=actor,
            action_type=ActionType.ITEM,
            target=target,
            item_id=item_id
        )
        
        # Let BattleController handle execution
        if hasattr(self.scene, 'battle_controller'):
            self.scene.battle_controller.queue_action(item_action)
        else:
            # Fallback: show message but don't execute
            self.battle_ui.show_message("Battle-Controller nicht verfügbar!")
    
    def execute_flee(self, actor: MonsterInstance, action: Dict):
        """Attempt to flee from battle via BattleController."""
        if not self.scene.can_flee:
            self.battle_ui.show_message("Hier gibt's kein Entkommen!")
            return
        
        # Create BattleAction and queue with controller
        from engine.systems.battle.turn_logic_clean import BattleAction, ActionType
        flee_action = BattleAction(
            actor=actor,
            action_type=ActionType.FLEE
        )
        
        # Let BattleController handle execution
        if hasattr(self.scene, 'battle_controller'):
            self.scene.battle_controller.queue_action(flee_action)
        else:
            # Fallback: show message but don't execute
            self.battle_ui.show_message("Battle-Controller nicht verfügbar!")
