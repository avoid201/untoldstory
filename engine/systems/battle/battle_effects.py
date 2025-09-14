"""
Battle Effects System - Enhanced Visual Effects
==============================================
ENHANCED: Attack-Animationen und Visual-Effects für Battle-System

Verantwortlichkeiten:
- Attack-Animationen (Physical, Magic, Status)
- Status-Effect-Animationen
- Battle-Intro-Animationen
- Visual-Feedback-System
- Performance-optimierte Effekte
"""

import logging
import random
import math
from typing import Dict, Any, List, Tuple, Optional, TYPE_CHECKING
from dataclasses import dataclass
from enum import Enum, auto

if TYPE_CHECKING:
    from engine.systems.battle.battle_state import BattleState
    from engine.systems.monster_instance import MonsterInstance

logger = logging.getLogger(__name__)


class AttackType(Enum):
    """Attack animation types."""
    PHYSICAL = auto()
    MAGIC = auto()
    STATUS = auto()
    SPECIAL = auto()


class EffectType(Enum):
    """Visual effect types."""
    SPARKLE = auto()
    EXPLOSION = auto()
    HEAL = auto()
    POISON = auto()
    BURN = auto()
    FREEZE = auto()
    PARALYSIS = auto()
    SLEEP = auto()
    CONFUSION = auto()
    CRITICAL = auto()
    SUPER_EFFECTIVE = auto()


@dataclass
class AttackAnimation:
    """Attack animation data."""
    attacker_id: Any
    target_id: Any
    attack_type: AttackType
    move_name: str
    duration: float
    timer: float
    phase: int = 0  # 0: Wind-up, 1: Impact, 2: Follow-through
    intensity: float = 1.0
    color: Tuple[int, int, int] = (255, 255, 255)
    active: bool = True


@dataclass
class StatusEffectAnimation:
    """Status effect animation data."""
    target_id: Any
    effect_type: EffectType
    duration: float
    timer: float
    intensity: float = 1.0
    color: Tuple[int, int, int] = (255, 255, 255)
    active: bool = True


class BattleEffectsSystem:
    """Enhanced Battle Effects System mit Attack-Animationen."""
    
    def __init__(self, battle_state: 'BattleState' = None):
        self.battle_state = battle_state
        self.attack_animations: List[AttackAnimation] = []
        self.status_animations: List[StatusEffectAnimation] = []
        self.intro_animations: List[Dict[str, Any]] = []
        
        # Performance limits
        self.max_attack_animations = 5
        self.max_status_animations = 10
        self.max_intro_animations = 3
        
        # Animation timing
        self.attack_duration = 1.0
        self.status_duration = 2.0
        self.intro_duration = 3.0
        
        logger.info("🎬 Enhanced Battle Effects System initialized")
    
    def add_attack_animation(self, attacker_id: Any, target_id: Any, 
                           attack_type: AttackType, move_name: str,
                           intensity: float = 1.0) -> None:
        """Füge Attack-Animation hinzu."""
        if len(self.attack_animations) >= self.max_attack_animations:
            # Remove oldest animation
            self.attack_animations.pop(0)
        
        # Choose color based on attack type
        color_map = {
            AttackType.PHYSICAL: (255, 200, 100),  # Orange
            AttackType.MAGIC: (100, 100, 255),     # Blue
            AttackType.STATUS: (255, 100, 255),    # Magenta
            AttackType.SPECIAL: (255, 255, 100)    # Yellow
        }
        
        self.attack_animations.append(AttackAnimation(
            attacker_id=attacker_id,
            target_id=target_id,
            attack_type=attack_type,
            move_name=move_name,
            duration=self.attack_duration,
            timer=self.attack_duration,
            intensity=intensity,
            color=color_map.get(attack_type, (255, 255, 255))
        ))
        
        logger.debug(f"Attack animation added: {move_name} ({attack_type.name})")
    
    def add_status_effect_animation(self, target_id: Any, effect_type: EffectType,
                                  intensity: float = 1.0) -> None:
        """Füge Status-Effect-Animation hinzu."""
        if len(self.status_animations) >= self.max_status_animations:
            # Remove oldest animation
            self.status_animations.pop(0)
        
        # Choose color based on effect type
        color_map = {
            EffectType.POISON: (128, 0, 128),      # Purple
            EffectType.BURN: (255, 100, 0),        # Orange
            EffectType.FREEZE: (0, 255, 255),      # Cyan
            EffectType.PARALYSIS: (255, 255, 0),   # Yellow
            EffectType.SLEEP: (0, 0, 255),         # Blue
            EffectType.CONFUSION: (255, 0, 255),   # Magenta
            EffectType.CRITICAL: (255, 255, 0),    # Yellow
            EffectType.SUPER_EFFECTIVE: (255, 100, 0),  # Orange
            EffectType.HEAL: (0, 255, 0),          # Green
            EffectType.SPARKLE: (255, 255, 255),   # White
            EffectType.EXPLOSION: (255, 50, 0)     # Red-Orange
        }
        
        self.status_animations.append(StatusEffectAnimation(
            target_id=target_id,
            effect_type=effect_type,
            duration=self.status_duration,
            timer=self.status_duration,
            intensity=intensity,
            color=color_map.get(effect_type, (255, 255, 255))
        ))
        
        logger.debug(f"Status effect animation added: {effect_type.name}")
    
    def add_intro_animation(self, animation_type: str, duration: float = 3.0) -> None:
        """Füge Battle-Intro-Animation hinzu."""
        if len(self.intro_animations) >= self.max_intro_animations:
            # Remove oldest animation
            self.intro_animations.pop(0)
        
        self.intro_animations.append({
            'type': animation_type,
            'duration': duration,
            'timer': duration,
            'phase': 0,
            'active': True
        })
        
        logger.debug(f"Intro animation added: {animation_type}")
    
    def update_animations(self, dt: float) -> None:
        """Update alle Animationen."""
        # Update attack animations
        for anim in self.attack_animations[:]:
            anim.timer -= dt
            
            if anim.timer <= 0:
                anim.active = False
                self.attack_animations.remove(anim)
            else:
                # Update animation phase
                progress = 1.0 - (anim.timer / anim.duration)
                if progress < 0.3:
                    anim.phase = 0  # Wind-up
                elif progress < 0.7:
                    anim.phase = 1  # Impact
                else:
                    anim.phase = 2  # Follow-through
        
        # Update status animations
        for anim in self.status_animations[:]:
            anim.timer -= dt
            
            if anim.timer <= 0:
                anim.active = False
                self.status_animations.remove(anim)
        
        # Update intro animations
        for anim in self.intro_animations[:]:
            anim['timer'] -= dt
            
            if anim['timer'] <= 0:
                anim['active'] = False
                self.intro_animations.remove(anim)
            else:
                # Update intro phase
                progress = 1.0 - (anim['timer'] / anim['duration'])
                if progress < 0.5:
                    anim['phase'] = 0  # Fade in
                else:
                    anim['phase'] = 1  # Fade out
    
    def get_active_attack_animations(self) -> List[AttackAnimation]:
        """Hole alle aktiven Attack-Animationen."""
        return [anim for anim in self.attack_animations if anim.active]
    
    def get_active_status_animations(self) -> List[StatusEffectAnimation]:
        """Hole alle aktiven Status-Animationen."""
        return [anim for anim in self.status_animations if anim.active]
    
    def get_active_intro_animations(self) -> List[Dict[str, Any]]:
        """Hole alle aktiven Intro-Animationen."""
        return [anim for anim in self.intro_animations if anim['active']]
    
    def is_animating(self) -> bool:
        """Prüfe ob Animationen aktiv sind."""
        return (len(self.get_active_attack_animations()) > 0 or
                len(self.get_active_status_animations()) > 0 or
                len(self.get_active_intro_animations()) > 0)
    
    def clear_all_animations(self) -> None:
        """Lösche alle Animationen."""
        self.attack_animations.clear()
        self.status_animations.clear()
        self.intro_animations.clear()
        logger.debug("All battle effects animations cleared")
    
    def get_animation_stats(self) -> Dict[str, int]:
        """Hole Animation-Statistiken."""
        return {
            'attack_animations': len(self.attack_animations),
            'status_animations': len(self.status_animations),
            'intro_animations': len(self.intro_animations),
            'total_active': len(self.get_active_attack_animations()) + 
                           len(self.get_active_status_animations()) + 
                           len(self.get_active_intro_animations())
        }


# Legacy compatibility
class battleeffects(BattleEffectsSystem):
    """Legacy compatibility class."""
    
    def __init__(self, battle_state: 'BattleState' = None):
        super().__init__(battle_state)
        logger.info("battleeffects (legacy) initialized")
    
    def process(self) -> Dict[str, Any]:
        """Process operation (legacy compatibility)."""
        return {'success': True, 'message': 'Operation processed successfully'}
