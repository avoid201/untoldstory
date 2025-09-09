"""
LEGACY BACKUP: DamageCalculator from stats.py
This file contains the deprecated DamageCalculator class that was removed.
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class DamageCalculator:
    """
    DEPRECATED: Legacy Damage Calculator für Backward Compatibility.
    Delegiert an UnifiedDamageCalculator.
    """
    
    @staticmethod
    def calculate_damage(attacker_level: int,
                        power: int,
                        attack_stat: int,
                        defense_stat: int,
                        type_effectiveness: float = 1.0,
                        stab: float = 1.0,
                        critical: bool = False,
                        random_factor: float = 1.0,
                        other_modifiers: float = 1.0) -> int:
        """
        DEPRECATED: Legacy damage calculation.
        Delegiert an UnifiedDamageCalculator.
        
        Args:
            attacker_level: Level of attacking monster
            power: Move power
            attack_stat: Attack or Magic stat (with stages applied)
            defense_stat: Defense or Resistance stat (with stages applied)
            type_effectiveness: Type matchup multiplier
            stab: Same-type attack bonus
            critical: Whether the hit is critical
            random_factor: Random multiplier (0.85-1.0)
            other_modifiers: Any other multipliers (weather, abilities, etc.)
            
        Returns:
            Final damage value
        """
        logger.warning("DamageCalculator.calculate_damage is DEPRECATED. Use UnifiedDamageCalculator instead.")
        
        try:
            # Erstelle Mock-Objekte für UnifiedDamageCalculator
            class MockMove:
                def __init__(self, power):
                    self.power = power
                    self.type = "Normal"
                    self.category = type('Category', (), {'value': 'phys'})()

            class MockMonster:
                def __init__(self, stats, types=None, traits=None):
                    self.stats = stats
                    self.types = types or ['Normal']
                    self.traits = traits or []

            # Erstelle Mock-Objekte
            mock_move = MockMove(power)
            mock_attacker = MockMonster({'atk': attack_stat, 'mag': attack_stat, 'spd': 100})
            mock_defender = MockMonster({'def': defense_stat, 'res': defense_stat, 'spd': 100})

            # Verwende UnifiedDamageCalculator
            from engine.systems.unified_damage_calculator import unified_damage_calculator
            result = unified_damage_calculator.calculate_damage(mock_attacker, mock_defender, mock_move)

            # Wende zusätzliche Modifikatoren an (die nicht im UnifiedCalculator sind)
            final_damage = result.damage * type_effectiveness * stab
            if critical:
                final_damage *= 2.0
            final_damage *= random_factor * other_modifiers

            return max(1, int(final_damage))

        except Exception as e:
            logger.error(f"Error in legacy calculate_damage: {e}")

            # Fallback zu einfacher Formel
            base_damage = ((attack_stat * 2 - defense_stat) * power / 50) + 2
            damage = base_damage * type_effectiveness * stab
            if critical:
                damage *= 2.0
            damage *= random_factor * other_modifiers
            return max(1, int(damage))
