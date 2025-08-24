#!/usr/bin/env python3
"""
Simplified Battle Flow Fix
Deaktiviert das Command Collection System vorerst für direktes UI-basiertes Gameplay
"""

print("🎮 SIMPLIFYING BATTLE FLOW")
print("="*60)

# Fix battle_scene.py to use simple direct action system
battle_scene_path = "/Users/leon/Desktop/untold_story/engine/scenes/battle_scene.py"

print("\n1. Disabling command collection system temporarily...")

# Read the file
with open(battle_scene_path, 'r') as f:
    content = f.read()

# Find and replace the _update_input_phase method
old_method = '''    def _update_input_phase(self, dt: float):
        """Handle player input phase with DQM command collection."""
        # Wenn bereits geflohen, direkt zur END-Phase
        if self.battle_result != BattleResult.ONGOING:
            self.current_phase = BattlePhase.END
            self.phase_timer = 0
            print("Battle ending due to result - moving to END phase")
            return
        
        # Start command collection if not already started
        if not self.commands_collected and self.command_collector:
            print("Starting DQM command collection phase...")
            # Collect all commands for this turn
            self.collected_commands = self.command_collector.collect_all_commands()
            
            if self.collected_commands:
                self.commands_collected = True
                print(f"Collected {len(self.collected_commands)} commands")
                # Move to execution phase
                self.current_phase = BattlePhase.RESOLVE
                self.phase_timer = 0
                print("Moving to execution phase with all commands")
            else:
                # Wait for commands
                print("Waiting for command collection...")
        
        # Wait for player input
        if not self.waiting_for_input:
            # Player has made a choice, move to execution
            self.current_phase = BattlePhase.RESOLVE
            self.phase_timer = 0
            print("Moving to execution phase")'''

new_method = '''    def _update_input_phase(self, dt: float):
        """Handle player input phase - SIMPLIFIED."""
        # Wenn bereits geflohen, direkt zur END-Phase
        if self.battle_result != BattleResult.ONGOING:
            self.current_phase = BattlePhase.END
            self.phase_timer = 0
            print("Battle ending due to result - moving to END phase")
            return
        
        # Just wait for player input through handle_event
        # No automatic command collection
        self.waiting_for_input = True'''

if old_method in content:
    content = content.replace(old_method, new_method)
    print("   ✅ Disabled command collection in update")

# Write back
with open(battle_scene_path, 'w') as f:
    f.write(content)

print("\n2. Making sure intro phase transitions correctly...")

# Find and update _update_intro_phase
old_intro = '''    def _update_intro_phase(self, dt: float):
        """Handle intro animations and messages."""
        # Wenn bereits geflohen, direkt zur END-Phase
        if self.battle_result != BattleResult.ONGOING:
            self.current_phase = BattlePhase.END
            self.phase_timer = 0
            print("Battle ending due to result - moving to END phase")
            return
        
        # Wait for intro message
        if self.phase_timer > 2.0:  # 2 seconds intro
            self.current_phase = BattlePhase.INPUT
            self.waiting_for_input = True
            print("Intro phase complete - waiting for input")'''

new_intro = '''    def _update_intro_phase(self, dt: float):
        """Handle intro animations and messages."""
        # Wenn bereits geflohen, direkt zur END-Phase
        if self.battle_result != BattleResult.ONGOING:
            self.current_phase = BattlePhase.END
            self.phase_timer = 0
            print("Battle ending due to result - moving to END phase")
            return
        
        # Shorter intro, immediately go to input
        if self.phase_timer > 0.5:  # 0.5 seconds intro
            self.current_phase = BattlePhase.INPUT
            self.waiting_for_input = True
            print("Intro phase complete - waiting for input")'''

if old_intro in content:
    content = content.replace(old_intro, new_intro)
    with open(battle_scene_path, 'w') as f:
        f.write(content)
    print("   ✅ Shortened intro phase")

print("\n" + "="*60)
print("✅ BATTLE FLOW SIMPLIFIED!")
print("\nThe battle should now respond to inputs immediately:")
print("- Press SPACE/ENTER to select options")
print("- Use WASD or Arrow keys to navigate")
print("- Combat actions execute immediately")
print("\nRestart the game to test!")
