"""
Status Effect System Compatibility Wrapper
Provides unified interface for status effects
"""

from engine.systems.battle.status_effects_dqm import DQMStatusManager, DQMStatus, StatusEffect

class StatusEffectSystem:
    """Compatibility wrapper for DQMStatusManager."""
    
    def __init__(self):
        """Initialize without requiring a monster."""
        self.managers = {}
        
    def initialize_monster(self, monster):
        """Initialize status manager for a monster."""
        if monster not in self.managers:
            self.managers[monster] = DQMStatusManager(monster)
        return self.managers[monster]
        
    def apply_status(self, monster, status):
        """Apply status to a monster."""
        if monster not in self.managers:
            self.managers[monster] = DQMStatusManager(monster)
        
        # Convert string to DQMStatus if needed
        if isinstance(status, str):
            status = DQMStatus[status.upper()] if status.upper() in DQMStatus.__members__ else DQMStatus.NORMAL
        
        # Apply with default duration
        return self.managers[monster].apply_status(status, duration=3)
    
    def process_turn_end(self, monster):
        """Process end of turn for a monster."""
        if monster not in self.managers:
            self.managers[monster] = DQMStatusManager(monster)
        
        effects = self.managers[monster].process_turn_end()
        
        # Update monster's HP if damaged
        if 'damage' in effects:
            monster.current_hp = max(0, monster.current_hp - effects['damage'])
        
        return effects
    
    def can_monster_act(self, monster):
        """Check if monster can act this turn."""
        if monster not in self.managers:
            return True
        
        effects = self.managers[monster].process_turn_start()
        return not effects.get('skip_turn', False)

# Export
StatusType = DQMStatus
