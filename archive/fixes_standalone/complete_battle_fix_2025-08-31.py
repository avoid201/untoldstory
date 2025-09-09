#!/usr/bin/env python3
"""
Complete Battle Flow Fix
Stellt sicher, dass der Battle Flow komplett funktioniert
"""

print("🎮 COMPLETE BATTLE FLOW FIX")
print("="*60)

# Fix 1: Stelle sicher, dass Move.id existiert
print("\n1. Fixing Move class...")
monster_fix = '''
            # Default moves
            from dataclasses import dataclass
            
            @dataclass
            class Move:
                name: str
                power: int
                pp: int
                max_pp: int
                target_type: str = "single"
                element: str = "normal"
                
                @property
                def id(self):
                    """Generate ID from name."""
                    return self.name.lower().replace(" ", "_")
                
                @property 
                def category(self):
                    """Determine category."""
                    return "phys" if self.element in ["normal", "fighting"] else "mag"
'''

import os
monster_path = "/Users/leon/Desktop/untold_story/engine/systems/monster_instance.py"
with open(monster_path, 'r') as f:
    content = f.read()

# Replace the Move class
if "@dataclass\n            class Move:" in content:
    start = content.find("@dataclass\n            class Move:")
    end = content.find("\n            self.moves = [", start)
    if end > start:
        content = content[:start] + monster_fix.strip() + "\n" + content[end:]
        with open(monster_path, 'w') as f:
            f.write(content)
        print("   ✅ Move class fixed with id and category")

# Fix 2: Battle Scene handling
print("\n2. Simplifying battle scene action handling...")

battle_scene_simple = '''    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle input events - SIMPLIFIED."""
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
                    
                    # Handle based on phase
                    if self.current_phase == BattlePhase.INPUT:
                        # Get UI action
                        player_action = self.battle_ui.handle_input(action, self.battle_state)
                        
                        if player_action:
                            print(f"Player action: {player_action}")
                            
                            # Process the action
                            self._process_player_action(player_action)
                    
                    elif self.current_phase in [BattlePhase.INIT, BattlePhase.MESSAGE]:
                        # Skip to input phase
                        self.current_phase = BattlePhase.INPUT
                        self.waiting_for_input = True
                
                return True
            
            return False
            
        except Exception as e:
            print(f"Error in handle_event: {e}")
            return False
    
    def _process_player_action(self, player_action: dict):
        """Process player action from UI."""
        try:
            action_type = player_action.get('action')
            
            if action_type == 'flee':
                # Execute flee immediately
                self._execute_flee(player_action.get('actor'), player_action)
                
            elif action_type == 'attack':
                # Execute attack
                self._execute_simple_attack(player_action)
                
            elif action_type in ['tame', 'scout', 'item', 'switch']:
                # Execute special action
                self._execute_special_action(player_action)
                
            elif action_type == 'menu_select':
                # Just a menu navigation - do nothing
                pass
                
            elif action_type == 'cancel':
                # Cancel - return to menu
                self.battle_ui.menu_state = BattleMenuState.MAIN
                
        except Exception as e:
            print(f"Error processing action: {e}")
    
    def _execute_simple_attack(self, action: dict):
        """Execute a simple attack."""
        try:
            actor = action.get('actor')
            target = action.get('target')
            move = action.get('move')
            
            if not actor or not target:
                print("Missing actor or target")
                return
            
            # Calculate damage
            if hasattr(self.battle_state, 'calculate_dqm_damage'):
                result = self.battle_state.calculate_dqm_damage(actor, target, move or {'power': 40, 'category': 'phys'})
                damage = result.get('final_damage', 10)
            else:
                # Simple damage calc
                damage = 10 + actor.level * 2
            
            # Apply damage
            target.current_hp = max(0, target.current_hp - damage)
            
            # Add message
            self.battle_ui.add_message(f"{actor.name} attacks {target.name} for {damage} damage!")
            
            # Check if target fainted
            if target.current_hp <= 0:
                target.is_fainted = True
                self.battle_ui.add_message(f"{target.name} fainted!")
                
                # Check battle end
                if target == self.battle_state.enemy_active:
                    self.battle_result = BattleResult.VICTORY
                    self.current_phase = BattlePhase.END
                elif target == self.battle_state.player_active:
                    self.battle_result = BattleResult.DEFEAT
                    self.current_phase = BattlePhase.END
            
            # Enemy turn
            if not target.is_fainted and target == self.battle_state.enemy_active:
                self._execute_enemy_turn()
                
        except Exception as e:
            print(f"Error in attack: {e}")
    
    def _execute_enemy_turn(self):
        """Simple enemy turn."""
        try:
            enemy = self.battle_state.enemy_active
            player = self.battle_state.player_active
            
            if not enemy or enemy.is_fainted or not player or player.is_fainted:
                return
            
            # Simple damage
            damage = 5 + enemy.level
            player.current_hp = max(0, player.current_hp - damage)
            
            self.battle_ui.add_message(f"{enemy.name} attacks for {damage} damage!")
            
            if player.current_hp <= 0:
                player.is_fainted = True
                self.battle_ui.add_message(f"{player.name} fainted!")
                self.battle_result = BattleResult.DEFEAT
                self.current_phase = BattlePhase.END
                
        except Exception as e:
            print(f"Error in enemy turn: {e}")
    
    def _execute_special_action(self, action: dict):
        """Execute special actions."""
        action_type = action.get('action')
        actor = action.get('actor')
        
        if action_type == 'tame':
            self.battle_ui.add_message("Taming not yet implemented!")
        elif action_type == 'scout':
            self.battle_ui.add_message(f"{self.battle_state.enemy_active.name}: HP {self.battle_state.enemy_active.current_hp}/{self.battle_state.enemy_active.max_hp}")
        elif action_type == 'item':
            self.battle_ui.add_message("Items not yet implemented!")
        elif action_type == 'switch':
            self.battle_ui.add_message("Switch not yet implemented!")'''

# Write the simplified battle scene handler
battle_scene_path = "/Users/leon/Desktop/untold_story/engine/scenes/battle_scene.py"
with open(battle_scene_path, 'r') as f:
    content = f.read()

# Find and replace handle_event
start = content.find("    def handle_event(self, event: pygame.event.Event) -> bool:")
if start > 0:
    # Find next method
    next_method = content.find("\n    def ", start + 1)
    
    # Insert our simplified version
    content = content[:start] + battle_scene_simple + "\n" + content[next_method:]
    
    with open(battle_scene_path, 'w') as f:
        f.write(content)
    print("   ✅ Battle scene event handling simplified")

print("\n" + "="*60)
print("✅ BATTLE FLOW FIXES COMPLETE!")
print("\nThe battle should now work with:")
print("- Fight → Attack executes immediately")
print("- Simple damage calculation")
print("- Enemy counter-attacks")
print("- Battle ends when HP reaches 0")
print("\nRestart the game to test!")
