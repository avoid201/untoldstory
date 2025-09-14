# ARCHIVED: 2025-09-03 - Consolidated into engine/scenes/battle_scene_components.py
"""
Battle Scene Input Handler.
Manages input during battle and converts it to battle actions.
"""

import pygame
from typing import Optional, Dict, TYPE_CHECKING

from engine.systems.battle.battle_enums import BattlePhase

if TYPE_CHECKING:
    from engine.scenes.battle_scene import BattleScene


class BattleInputHandler:
    """Handles input during battle."""
    
    def __init__(self, scene: 'BattleScene'):
        self.scene = scene
        self.battle_state = scene.battle_state
        self.battle_ui = scene.battle_ui
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle input events."""
        try:
            if event.type == pygame.KEYDOWN:
                # Map keys to actions
                action = None
                
                if event.key in [pygame.K_e, pygame.K_RETURN, pygame.K_SPACE]:
                    action = 'confirm'
                elif event.key in [pygame.K_q, pygame.K_ESCAPE]:
                    action = 'back'
                elif event.key == pygame.K_w:
                    action = 'up'
                elif event.key == pygame.K_s:
                    action = 'down'
                elif event.key == pygame.K_a:
                    action = 'left'
                elif event.key == pygame.K_d:
                    action = 'right'
                
                if action:
                    print(f"Battle Input: {action}")
                    
                    # Handle different battle phases
                    if self.scene.current_phase == BattlePhase.INPUT:
                        # Let UI handle input and get action
                        player_action = self.battle_ui.handle_input(action, self.battle_state)
                        
                        if player_action:
                            print(f"Player action: {player_action}")
                            # Store player action
                            self.scene.pending_actions['player_0'] = player_action
                            self.scene.waiting_for_input = False
                            
                            # Check if all actions collected
                            if self.scene.all_actions_ready():
                                self.scene.execute_turn()
                    
                    elif self.scene.current_phase == BattlePhase.MESSAGE:
                        # Skip message on any key
                        self.scene.phase_manager.next_message()
                    
                    elif self.scene.current_phase == BattlePhase.INIT:
                        # Skip intro on any key
                        self.scene.current_phase = BattlePhase.INPUT
                        self.scene.waiting_for_input = True
                        print("Battle started - waiting for input")
                
                return True
            
            return False
            
        except Exception as e:
            print(f"Fehler bei der Input-Verarbeitung: {str(e)}")
            return False
    
    def create_battle_action(self, player_action: dict) -> Optional['BattleAction']:
        """Create a BattleAction from player input."""
        try:
            from engine.systems.battle.turn_logic_clean import BattleAction, ActionType
            
            action_type = player_action.get('action')
            if action_type == 'attack':
                # Get selected move
                move_index = player_action.get('move_index', 0)
                if hasattr(self.battle_state, 'player_active') and self.battle_state.player_active:
                    moves = self.battle_state.player_active.moves
                    if moves and move_index < len(moves):
                        move = moves[move_index]
                        return BattleAction(
                            actor=self.battle_state.player_active,
                            action_type=ActionType.ATTACK,
                            move=move,
                            target=self.battle_state.enemy_active
                        )
            
            elif action_type == 'flee':
                return BattleAction(
                    actor=self.battle_state.player_active,
                    action_type=ActionType.FLEE
                )
            
            elif action_type == 'tame':
                # Get meat bonus if available
                meat_bonus = player_action.get('meat_bonus', 0)
                return BattleAction(
                    actor=self.battle_state.player_active,
                    action_type=ActionType.TAME,
                    target=self.battle_state.enemy_active,
                    meat_bonus=meat_bonus
                )
            
            elif action_type == 'switch':
                # Handle monster switching using the complete Party system
                try:
                    switch_target_id = player_action.get('target_monster')
                    if not switch_target_id:
                        print("ERROR: No target monster specified for switch")
                        return None
                    
                    # Get party manager
                    if not hasattr(self.scene.game, 'party_manager') or not self.scene.game.party_manager:
                        print("ERROR: No party manager available for switching")
                        return None
                    
                    party = self.scene.game.party_manager.party
                    
                    # Find the target monster in the party
                    target_monster = None
                    for monster in party.get_conscious_members():
                        if hasattr(monster, 'id') and monster.id == switch_target_id:
                            target_monster = monster
                            break
                        elif monster.name == switch_target_id:  # Fallback to name matching
                            target_monster = monster
                            break
                    
                    if not target_monster:
                        print(f"ERROR: Target monster {switch_target_id} not found or fainted")
                        return None
                    
                    # Check if already active
                    current_active = party.get_active()
                    if current_active and current_active == target_monster:
                        print(f"ERROR: {target_monster.name} is already the active monster")
                        return None
                    
                    # Create switch battle action
                    return BattleAction(
                        actor=self.battle_state.player_active,
                        action_type=ActionType.SWITCH,
                        switch_to=target_monster
                    )
                    
                except Exception as e:
                    print(f"ERROR in switch action: {e}")
                    return None
            
            print(f"Unknown action type: {action_type}")
            return None
            
        except Exception as e:
            print(f"Fehler beim Erstellen der BattleAction: {str(e)}")
            return None
    
    def get_ai_action(self, actor_id: str) -> Optional[Dict]:
        """Get AI-determined action for an actor."""
        # Get the monster
        idx = int(actor_id.split('_')[1])
        monster = self.battle_state.enemy_team[idx]
        
        if not monster or monster.current_hp <= 0:
            return None
        
        # Use AI to determine action
        action = self.scene.battle_ai.choose_action(
            monster,
            self.battle_state.enemy_team,
            self.battle_state.player_team,
            self.battle_state
        )
        
        # Add actor ID
        if action:
            action['actor'] = actor_id
        
        return action
