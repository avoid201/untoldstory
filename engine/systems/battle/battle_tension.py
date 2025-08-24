"""
DQM Tension/Psyche Up System
Manages tension states and damage multipliers for special attacks
"""

from dataclasses import dataclass, field
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


@dataclass
class TensionState:
    """DQM Tension/Psyche Up system."""
    level: int = 0  # 0-3 (Normal, Psyched, High Tension, Super High Tension)
    multipliers: List[float] = field(default_factory=lambda: [1.0, 1.5, 2.0, 2.5])
    
    def psyche_up(self) -> bool:
        """Increase tension level."""
        if self.level < 3:
            self.level += 1
            return True
        return False
    
    def get_multiplier(self) -> float:
        """Get current damage multiplier."""
        return self.multipliers[self.level]
    
    def reset(self) -> None:
        """Reset tension after attack."""
        self.level = 0


class TensionManager:
    """Manages tension states for all monsters in battle."""
    
    def __init__(self):
        """Initialize tension manager."""
        self.tension_states: Dict['MonsterInstance', TensionState] = {}
    
    def initialize_monster(self, monster: 'MonsterInstance') -> None:
        """Initialize tension state for a monster."""
        if monster not in self.tension_states:
            self.tension_states[monster] = TensionState()
    
    def psyche_up(self, monster: 'MonsterInstance') -> Dict[str, any]:
        """
        Execute PSYCHE_UP command - increase tension for next attack.
        
        Args:
            monster: The monster to psyche up
            
        Returns:
            Result dictionary with tension level and message
        """
        try:
            if not monster:
                return {'error': 'Kein Monster für PSYCHE_UP'}
            
            # Get or create TensionState for the monster
            if monster not in self.tension_states:
                self.initialize_monster(monster)
            
            tension_state = self.tension_states[monster]
            
            # Increase tension level
            success = tension_state.psyche_up()
            if success:
                new_level = tension_state.level
                multiplier = tension_state.get_multiplier()
                
                return {
                    'action': 'psyche_up_success',
                    'message': f"{monster.name} lädt sich auf! (Tension Level {new_level})",
                    'tension_level': new_level,
                    'damage_multiplier': multiplier,
                    'monster': monster.name
                }
            else:
                return {
                    'action': 'psyche_up_failed',
                    'message': f"{monster.name} ist bereits auf maximaler Tension!",
                    'monster': monster.name
                }
                
        except Exception as e:
            logger.error(f"Fehler bei PSYCHE_UP: {str(e)}")
            return {'error': str(e)}
    
    def get_multiplier(self, monster: 'MonsterInstance') -> float:
        """
        Get current tension multiplier for a monster.
        
        Args:
            monster: The monster to check
            
        Returns:
            Current damage multiplier (1.0 if no tension)
        """
        try:
            if monster in self.tension_states:
                return self.tension_states[monster].get_multiplier()
            return 1.0
        except Exception as e:
            logger.error(f"Fehler beim Abrufen des Tension-Multipliers: {str(e)}")
            return 1.0
    
    def reset_tension(self, monster: 'MonsterInstance') -> None:
        """
        Reset tension after monster attacks.
        
        Args:
            monster: The monster whose tension should be reset
        """
        try:
            if monster in self.tension_states and self.tension_states[monster].level > 0:
                self.tension_states[monster].reset()
                logger.info(f"{monster.name} Tension wurde zurückgesetzt!")
        except Exception as e:
            logger.error(f"Fehler beim Zurücksetzen der Tension: {str(e)}")
    
    def clear_all(self) -> None:
        """Clear all tension states."""
        self.tension_states.clear()
