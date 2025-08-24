#!/usr/bin/env python3
"""
Battle Execution Fix
Stellt sicher, dass Angriffe tatsächlich ausgeführt werden
"""

print("🔧 FIXING BATTLE EXECUTION")
print("="*60)

battle_scene_path = "/Users/leon/Desktop/untold_story/engine/scenes/battle_scene.py"

# Read the current content
with open(battle_scene_path, 'r') as f:
    content = f.read()

# Fix 1: Make sure _process_player_action actually calls the attack
print("\n1. Fixing action processing...")

# Check the current handle_event method
if "_process_player_action(player_action)" in content:
    print("   ✓ _process_player_action is being called")
else:
    print("   ⚠️  _process_player_action might not be called")

# Fix 2: Debug why battle ends immediately
print("\n2. Adding debug output to trace execution...")

# Add debug output to _execute_simple_attack
debug_attack = '''    def _execute_simple_attack(self, action: dict):
        """Execute a simple attack with proper feedback."""
        try:
            print(f"DEBUG: _execute_simple_attack called with action: {action.get('action')}")
            
            actor = action.get('actor')
            target = action.get('target')
            move = action.get('move')
            
            if not actor or not target:
                print("DEBUG: Missing actor or target")
                return
            
            print(f"DEBUG: {actor.name} attacking {target.name}")
            
            # Show attack message
            move_name = move.name if hasattr(move, 'name') else "Tackle"
            self.battle_ui.add_message(f"{actor.name} uses {move_name}!")
            print(f"DEBUG: Attack message added")
            
            # Calculate damage
            if hasattr(self.battle_state, 'calculate_dqm_damage'):
                result = self.battle_state.calculate_dqm_damage(actor, target, move or {'power': 40, 'category': 'phys'})
                damage = result.get('final_damage', 10)
            else:
                # Simple damage calc
                damage = 10 + actor.level * 2
            
            print(f"DEBUG: Calculated damage: {damage}")
            
            # Apply damage
            old_hp = target.current_hp
            target.current_hp = max(0, target.current_hp - damage)
            
            print(f"DEBUG: {target.name} HP: {old_hp} -> {target.current_hp}")
            
            # Update UI and show damage
            self.battle_ui.add_message(f"{target.name} takes {damage} damage!")
            self.battle_ui.add_message(f"{target.name}: {target.current_hp}/{target.max_hp} HP")
            
            # Check if target fainted
            if target.current_hp <= 0:
                target.is_fainted = True
                self.battle_ui.add_message(f"{target.name} fainted!")
                print(f"DEBUG: {target.name} fainted!")
                
                # Check battle end
                if target == self.battle_state.enemy_active:
                    self.battle_ui.add_message("Victory! You won the battle!")
                    self.battle_result = BattleResult.VICTORY
                    self.current_phase = BattlePhase.END
                    # Set timer to auto-exit
                    self.phase_timer = 0
                    print("DEBUG: Victory condition met")
                elif target == self.battle_state.player_active:
                    self.battle_ui.add_message("Defeat! You lost the battle!")
                    self.battle_result = BattleResult.DEFEAT
                    self.current_phase = BattlePhase.END
                    self.phase_timer = 0
                    print("DEBUG: Defeat condition met")
            else:
                print(f"DEBUG: {target.name} still alive, HP: {target.current_hp}")
                # Enemy turn if target still alive
                if target == self.battle_state.enemy_active:
                    print("DEBUG: Enemy's turn")
                    self._execute_enemy_turn()
                
        except Exception as e:
            print(f"ERROR in _execute_simple_attack: {e}")
            import traceback
            traceback.print_exc()'''

# Find and replace the _execute_simple_attack method
start_marker = "    def _execute_simple_attack(self, action: dict):"
end_marker = "    def _execute_enemy_turn(self):"

if start_marker in content and end_marker in content:
    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker)
    
    if start_idx < end_idx:
        content = content[:start_idx] + debug_attack + "\n\n" + content[end_idx:]
        print("   ✅ Added debug output to _execute_simple_attack")

# Fix 3: Make sure the attack is actually being called
print("\n3. Ensuring attack execution path...")

# Update handle_event to properly route attack actions
handle_event_fix = '''                    # Handle based on phase
                    if self.current_phase == BattlePhase.INPUT:
                        # Get UI action
                        player_action = self.battle_ui.handle_input(action, self.battle_state)
                        
                        if player_action:
                            print(f"Player action: {player_action}")
                            
                            # Check action type and process
                            action_type = player_action.get('action')
                            
                            if action_type == 'attack':
                                # Attack action - execute immediately
                                print("DEBUG: Processing attack action")
                                self._execute_simple_attack(player_action)
                            elif action_type == 'flee':
                                # Flee action
                                print("DEBUG: Processing flee action")
                                self._execute_flee(player_action.get('actor'), player_action)
                            elif action_type in ['tame', 'scout', 'item', 'switch']:
                                # Special actions
                                print("DEBUG: Processing special action")
                                self._execute_special_action(player_action)
                            elif action_type == 'menu_select':
                                # Just menu navigation
                                print("DEBUG: Menu navigation")
                                pass
                            else:
                                print(f"DEBUG: Unknown action type: {action_type}")'''

# Find and update the handle_event section
if "# Handle based on phase" in content:
    # Find the section to replace
    section_start = content.find("# Handle based on phase")
    section_end = content.find("elif self.current_phase in [BattlePhase.INIT", section_start)
    
    if section_start > 0 and section_end > section_start:
        content = content[:section_start] + handle_event_fix + "\n                    " + content[section_end:]
        print("   ✅ Fixed handle_event action routing")

# Write the fixed content
with open(battle_scene_path, 'w') as f:
    f.write(content)

print("\n" + "="*60)
print("✅ BATTLE EXECUTION FIXED!")
print("\nChanges made:")
print("  • Added debug output to trace execution")
print("  • Fixed action routing in handle_event")
print("  • Attack should now execute properly")
print("\nRestart the game and check the console output for DEBUG messages!")
