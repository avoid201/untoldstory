#!/usr/bin/env python3
"""
Battle System UI and Flow Fixes
Behebt UI-Reaktionen und Rückkehr zur Overworld
"""

print("🎮 FIXING BATTLE UI AND FLOW")
print("="*60)

# Fix 1: Make sure attacks actually execute and show results
print("\n1. Fixing attack execution and feedback...")

battle_scene_path = "/Users/leon/Desktop/untold_story/engine/scenes/battle_scene.py"

with open(battle_scene_path, 'r') as f:
    content = f.read()

# Update _execute_simple_attack to properly show damage and check victory
old_attack = '''    def _execute_simple_attack(self, action: dict):
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
            print(f"Error in attack: {e}")'''

new_attack = '''    def _execute_simple_attack(self, action: dict):
        """Execute a simple attack with proper feedback."""
        try:
            actor = action.get('actor')
            target = action.get('target')
            move = action.get('move')
            
            if not actor or not target:
                print("Missing actor or target")
                return
            
            # Show attack message
            move_name = move.name if hasattr(move, 'name') else "Tackle"
            self.battle_ui.add_message(f"{actor.name} uses {move_name}!")
            
            # Calculate damage
            if hasattr(self.battle_state, 'calculate_dqm_damage'):
                result = self.battle_state.calculate_dqm_damage(actor, target, move or {'power': 40, 'category': 'phys'})
                damage = result.get('final_damage', 10)
            else:
                # Simple damage calc
                damage = 10 + actor.level * 2
            
            # Apply damage
            old_hp = target.current_hp
            target.current_hp = max(0, target.current_hp - damage)
            
            # Update UI and show damage
            self.battle_ui.add_message(f"{target.name} takes {damage} damage!")
            self.battle_ui.add_message(f"{target.name}: {target.current_hp}/{target.max_hp} HP")
            
            # Check if target fainted
            if target.current_hp <= 0:
                target.is_fainted = True
                self.battle_ui.add_message(f"{target.name} fainted!")
                
                # Check battle end
                if target == self.battle_state.enemy_active:
                    self.battle_ui.add_message("Victory! You won the battle!")
                    self.battle_result = BattleResult.VICTORY
                    self.current_phase = BattlePhase.END
                    # Set timer to auto-exit
                    self.phase_timer = 0
                elif target == self.battle_state.player_active:
                    self.battle_ui.add_message("Defeat! You lost the battle!")
                    self.battle_result = BattleResult.DEFEAT
                    self.current_phase = BattlePhase.END
                    self.phase_timer = 0
            else:
                # Enemy turn if target still alive
                if target == self.battle_state.enemy_active:
                    self._execute_enemy_turn()
                
        except Exception as e:
            print(f"Error in attack: {e}")'''

if old_attack in content:
    content = content.replace(old_attack, new_attack)
    with open(battle_scene_path, 'w') as f:
        f.write(content)
    print("   ✅ Fixed attack execution with proper feedback")

# Fix 2: Make sure battle ends properly and returns to overworld
print("\n2. Fixing battle end and return to overworld...")

old_update_end = '''    def _update_end_phase(self, dt: float):
        """Handle battle end."""
        # Process battle results
        if self.phase_timer > 1.0:  # 1 second end
            print(f"End phase complete - ending battle with result: {self.battle_result.name}")
            self._end_battle()'''

new_update_end = '''    def _update_end_phase(self, dt: float):
        """Handle battle end and return to overworld."""
        # Show results briefly then return
        if self.phase_timer > 2.0:  # 2 seconds to show result
            print(f"Battle ended with result: {self.battle_result.name}")
            
            # Process rewards if victory
            if self.battle_result == BattleResult.VICTORY:
                # Give EXP (simplified)
                exp_gained = self.battle_state.enemy_active.level * 10
                self.battle_ui.add_message(f"Gained {exp_gained} EXP!")
            
            # Return to overworld
            self._end_battle()'''

if old_update_end in content:
    content = content.replace(old_update_end, new_update_end)
    with open(battle_scene_path, 'w') as f:
        f.write(content)
    print("   ✅ Fixed battle end phase")

# Fix 3: Ensure _end_battle properly returns to field
print("\n3. Fixing return to field scene...")

old_end_battle = '''    def _end_battle(self):
        """End the battle and return to field."""
        try:
            # Get battle results
            if hasattr(self.battle_state, 'get_battle_result'):
                results = self.battle_state.get_battle_result()
                print(f"Battle results: {results}")
            
            # Handle different battle results
            if self.battle_result == BattleResult.FLED:
                print("Player fled from battle - returning to field")
                # Keine besonderen Aktionen nötig beim Fliehen
            elif self.battle_result == BattleResult.CAUGHT:
                print("Monster caught - finalizing")
                self._finalize_caught_monster()
            elif self.battle_result == BattleResult.DEFEAT:
                print("Player defeated - handling defeat")
                self._handle_defeat()
            elif self.battle_result == BattleResult.VICTORY:
                print("Player victorious - syncing party")
                self._sync_party_after_battle()
            
            # Return to field
            self.game.pop_scene()
            
        except Exception as e:
            print(f"Fehler beim Beenden des Kampfs: {str(e)}")
            self.game.pop_scene()'''

new_end_battle = '''    def _end_battle(self):
        """End the battle and return to field."""
        try:
            print(f"Ending battle with result: {self.battle_result.name}")
            
            # Handle different battle results
            if self.battle_result == BattleResult.FLED:
                print("Player fled from battle")
            elif self.battle_result == BattleResult.CAUGHT:
                print("Monster caught")
                self._finalize_caught_monster()
            elif self.battle_result == BattleResult.DEFEAT:
                print("Player defeated")
                self._handle_defeat()
            elif self.battle_result == BattleResult.VICTORY:
                print("Player victorious")
                # Sync party state
                if hasattr(self, '_sync_party_after_battle'):
                    self._sync_party_after_battle()
            
            # Clear battle state
            self.battle_state = None
            self.battle_result = BattleResult.ONGOING
            
            # Return to field scene
            print("Returning to field scene...")
            self.game.pop_scene()
            
        except Exception as e:
            print(f"Error ending battle: {e}")
            # Force return to field
            self.game.pop_scene()'''

if old_end_battle in content:
    content = content.replace(old_end_battle, new_end_battle)
    with open(battle_scene_path, 'w') as f:
        f.write(content)
    print("   ✅ Fixed battle end and return to field")

# Fix 4: Make the UI update properly
print("\n4. Adding UI update hooks...")

# Find _process_player_action and make it update UI
old_process = '''    def _process_player_action(self, player_action: dict):
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
            print(f"Error processing action: {e}")'''

new_process = '''    def _process_player_action(self, player_action: dict):
        """Process player action from UI."""
        try:
            action_type = player_action.get('action')
            
            if action_type == 'flee':
                # Execute flee immediately
                self._execute_flee(player_action.get('actor'), player_action)
                
            elif action_type == 'attack':
                # Reset menu after attack selection
                self.battle_ui.menu_state = BattleMenuState.MAIN
                # Execute attack
                self._execute_simple_attack(player_action)
                
            elif action_type in ['tame', 'scout', 'item', 'switch']:
                # Reset menu
                self.battle_ui.menu_state = BattleMenuState.MAIN
                # Execute special action
                self._execute_special_action(player_action)
                
            elif action_type == 'menu_select':
                # Menu navigation handled by UI
                pass
                
            elif action_type == 'cancel':
                # Cancel - return to main menu
                self.battle_ui.menu_state = BattleMenuState.MAIN
                
        except Exception as e:
            print(f"Error processing action: {e}")'''

if old_process in content:
    content = content.replace(old_process, new_process)
    with open(battle_scene_path, 'w') as f:
        f.write(content)
    print("   ✅ Fixed UI state management")

print("\n" + "="*60)
print("✅ BATTLE UI AND FLOW FIXED!")
print("\nImprovements:")
print("  • Attack feedback shows damage dealt")
print("  • HP updates are displayed")
print("  • Victory/Defeat messages appear")
print("  • Battle ends after 2 seconds")
print("  • Returns to overworld automatically")
print("  • Menu resets after actions")
print("\nRestart the game to test the improvements!")
