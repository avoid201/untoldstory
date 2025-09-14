# 🎮 EXECUTIVE PROMPT: DQM-STYLE BATTLE SYSTEM

## CORE OBJECTIVE
Implement a complete Dragon Quest Monsters (DQM) style turn-based battle system for "Untold Story" that seamlessly integrates with the existing optimized Type System V2 and maintains the German localization.

## CRITICAL CONTEXT
- **Language**: Python 3.x with Pygame
- **Project Path**: `/Users/leon/Desktop/untold_story/`
- **Type System**: ✅ Already implemented (NumPy-optimized, 12 German types)
- **Damage Calculator**: ✅ Already implemented (Pipeline architecture)
- **DO NOT MODIFY**: types.py, damage_calc.py (use their APIs)

## DQM BATTLE SYSTEM SPECIFICATION

### 1. BATTLE FLOW (MOST IMPORTANT)
```
1. COMMAND PHASE: Collect ALL commands before ANY action
2. TURN ORDER: Sort by SPD stat
3. EXECUTION: Process actions in order
4. END TURN: Status effects, regeneration
```

### 2. CORE MECHANICS
- **3v3 Party Battles** (both sides)
- **Command Menu**: Attack, Skill, Defend, Item, Switch, Flee
- **Turn Order**: SPD-based with modifiers
- **Status Effects**: Poison, Paralysis, Sleep, Burn, Freeze, Confusion
- **AI Personalities**: Aggressive, Defensive, Tactical, Wise

### 3. KEY FEATURES TO IMPLEMENT

```python
# Battle Structure
class Battle:
    - player_party: List[MonsterInstance] (max 3)
    - enemy_party: List[MonsterInstance] (max 3)
    - turn_queue: List[BattleAction]
    - current_phase: BattlePhase
    
# Command System
class BattleCommand:
    - ATTACK: Basic physical
    - SKILL: Use MP for special moves
    - DEFEND: 50% damage reduction
    - SWITCH: Change active monster
    - ITEM: Use consumable
    - FLEE: Escape attempt
    
# Turn Execution
def execute_turn():
    1. Collect all commands
    2. Calculate turn order (SPD + priority)
    3. Execute each action
    4. Check victory/defeat
    5. Process end-of-turn effects
```

### 4. INTEGRATION REQUIREMENTS

```python
# Use existing Type System
from engine.systems.types import type_chart
effectiveness = type_chart.calculate_type_multiplier(move_type, defender_types)

# Use existing Damage Calculator  
from engine.systems.battle.damage_calc import DamageCalculator
calculator = DamageCalculator()
result = calculator.calculate(attacker, defender, move)

# German Messages
messages = {
    "super_effective": "Sehr effektiv!",
    "not_very_effective": "Nicht sehr effektiv...",
    "critical_hit": "Kritischer Treffer!"
}
```

### 5. UI LAYOUT

```
┌──────────────────────────┐
│   ENEMY PARTY (3 mons)   │ ← HP/MP bars, status icons
├──────────────────────────┤
│    BATTLEFIELD AREA      │ ← Animations, effects
├──────────────────────────┤
│   PLAYER PARTY (3 mons)  │ ← HP/MP/EXP, status
├──────────────────────────┤
│   COMMANDS │ BATTLE LOG  │ ← Menu and text output
└──────────────────────────┘
```

### 6. PRIORITY IMPLEMENTATION ORDER

1. **Phase 1: Core Loop**
   - Battle initialization
   - Command collection
   - Turn order calculation
   - Basic action execution

2. **Phase 2: Combat System**
   - Damage application
   - Status effects
   - Victory/defeat conditions
   - EXP/rewards

3. **Phase 3: AI System**
   - Basic AI decisions
   - Personality types
   - Tactical analysis

4. **Phase 4: UI/UX**
   - Battle screen layout
   - Animations
   - Sound effects
   - Visual feedback

5. **Phase 5: Polish**
   - Balance tuning
   - Edge cases
   - Performance optimization
   - Save/load states

## SUCCESS METRICS
- ✅ Commands collected before execution (DQM-style)
- ✅ 3v3 battles functional
- ✅ Turn order by SPD works
- ✅ All status effects implemented
- ✅ AI makes logical decisions
- ✅ German messages throughout
- ✅ 60 FPS performance
- ✅ Integration with Type System V2

## CONSTRAINTS
- MUST use existing type_chart for all type calculations
- MUST use existing DamageCalculator for damage
- MUST maintain German type names
- MUST support save/load mid-battle
- MUST run at 60 FPS on average hardware

## DELIVERABLES
1. `battle_controller.py` - Main battle logic
2. `battle_commands.py` - Command system
3. `battle_ai.py` - AI decision making
4. `battle_ui.py` - UI rendering
5. `test_battle_system.py` - Comprehensive tests
6. `BATTLE_SYSTEM_DOCS.md` - Full documentation

---

**START IMPLEMENTATION WITH:**

```python
"""
battle_controller.py
DQM-style battle system for Untold Story
"""

from typing import List, Optional
from enum import Enum, auto
from dataclasses import dataclass

from engine.systems.types import type_chart, type_api
from engine.systems.battle.damage_calc import DamageCalculator
from engine.systems.monster_instance import MonsterInstance

class BattlePhase(Enum):
    """Battle flow phases matching DQM style."""
    COMMAND_INPUT = auto()    # Collect all commands
    TURN_ORDER = auto()        # Sort by SPD
    EXECUTION = auto()         # Execute actions
    END_TURN = auto()         # Status/effects
    VICTORY = auto()          # Battle won
    DEFEAT = auto()           # Battle lost

@dataclass
class BattleAction:
    """Single action in battle."""
    actor: MonsterInstance
    command: str
    target: Optional[MonsterInstance] = None
    skill: Optional['Skill'] = None
    
    @property
    def priority(self) -> int:
        """Action priority for turn order."""
        priorities = {
            'flee': 6,
            'switch': 5,
            'item': 4,
            'defend': 3,
            'skill': 2,
            'attack': 1
        }
        return priorities.get(self.command, 0)
    
    @property
    def speed(self) -> int:
        """Effective speed for turn order."""
        return self.actor.stats['spd'] + (self.priority * 1000)

class BattleController:
    """Main DQM-style battle controller."""
    
    def __init__(self, player_party: List[MonsterInstance], 
                 enemy_party: List[MonsterInstance]):
        """Initialize 3v3 battle."""
        self.player_party = player_party[:3]
        self.enemy_party = enemy_party[:3]
        self.all_monsters = self.player_party + self.enemy_party
        
        self.phase = BattlePhase.COMMAND_INPUT
        self.turn_count = 0
        self.action_queue: List[BattleAction] = []
        
        self.damage_calc = DamageCalculator()
        self.battle_log: List[str] = []
        
    def run(self) -> 'BattleResult':
        """Main battle loop."""
        self.add_log("⚔️ Kampf beginnt!")
        
        while not self.is_battle_over():
            self.turn_count += 1
            self.add_log(f"\n--- Runde {self.turn_count} ---")
            
            # DQM-style: Collect ALL commands first
            self.phase = BattlePhase.COMMAND_INPUT
            self.collect_all_commands()
            
            # Calculate turn order by SPD
            self.phase = BattlePhase.TURN_ORDER
            self.sort_action_queue()
            
            # Execute all actions in order
            self.phase = BattlePhase.EXECUTION
            self.execute_all_actions()
            
            # End of turn effects
            self.phase = BattlePhase.END_TURN
            self.process_end_turn()
            
        return self.create_battle_result()
```

## 🎯 USE THIS PROMPT TO:
1. Complete the battle system implementation
2. Ensure DQM-style mechanics
3. Integrate with existing systems
4. Maintain German localization
5. Achieve 60 FPS performance

The AI should focus on creating a polished, strategic battle system that captures the essence of Dragon Quest Monsters while leveraging the already-optimized type and damage systems.