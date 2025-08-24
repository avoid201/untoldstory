"""
Battle Scene Phase Management.
Handles different battle phases and their transitions.
"""

from typing import TYPE_CHECKING
from engine.systems.battle.battle_system import BattlePhase

if TYPE_CHECKING:
    from .battle_scene_main import BattleScene


class BattlePhaseManager:
    """Manages battle phase transitions and updates."""
    
    def __init__(self, scene: 'BattleScene'):
        self.scene = scene
    
    def update_intro_phase(self, dt: float):
        """Handle intro animations and messages."""
        # Wait for intro message
        if self.scene.phase_timer > 2.0:  # 2 seconds intro
            self.scene.current_phase = BattlePhase.INPUT
            self.scene.waiting_for_input = True
            print("Intro phase complete - waiting for input")
    
    def update_input_phase(self, dt: float):
        """Handle player input phase."""
        # Wait for player input
        if not self.scene.waiting_for_input:
            # Player has made a choice, move to execution
            self.scene.current_phase = BattlePhase.RESOLVE
            self.scene.phase_timer = 0
            print("Moving to execution phase")
    
    def update_execution_phase(self, dt: float):
        """Handle action execution phase."""
        # Execute turn if actions are ready
        if self.scene.all_actions_ready():
            self.scene.execute_turn()
        else:
            # Wait for more actions
            pass
    
    def update_aftermath_phase(self, dt: float):
        """Handle end-of-turn effects."""
        # Process status effects, weather, etc.
        if self.scene.phase_timer > 1.0:  # 1 second aftermath
            # Check if battle should continue
            if self.scene.battle_state.is_valid():
                self.scene.current_phase = BattlePhase.INPUT
                self.scene.waiting_for_input = True
                print("Aftermath complete - waiting for input")
            else:
                self.scene.current_phase = BattlePhase.END
                print("Battle ending")
    
    def update_end_phase(self, dt: float):
        """Handle battle end."""
        # Process battle results
        if self.scene.phase_timer > 1.0:  # 1 second end
            self.scene.end_battle()
    
    def next_message(self):
        """Show next message in queue."""
        if hasattr(self.scene.battle_ui, 'message_queue') and self.scene.battle_ui.message_queue:
            self.scene.battle_ui._next_message()
        else:
            # No more messages, continue
            if self.scene.current_phase == BattlePhase.MESSAGE:
                self.scene.current_phase = BattlePhase.INPUT
                self.scene.waiting_for_input = True
