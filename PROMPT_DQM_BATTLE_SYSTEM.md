# AI Prompt: Complete DQM-Style Battle System Implementation

## 🎮 PROJECT CONTEXT

You are tasked with completing and perfecting a Dragon Quest Monsters (DQM) style battle system for "Untold Story", a monster-collecting RPG built in Python with Pygame. The project already has a robust foundation that must be preserved and enhanced.

## 📁 EXISTING CODEBASE STRUCTURE

```
/Users/leon/Desktop/untold_story/
├── engine/
│   ├── systems/
│   │   ├── types.py          # ✅ Type System V2 (NumPy-optimized, German)
│   │   ├── monsters.py        # Monster species definitions
│   │   ├── monster_instance.py # Individual monster instances
│   │   ├── moves.py          # Move definitions
│   │   ├── party.py          # Party management
│   │   └── battle/
│   │       ├── battle.py     # Main battle logic
│   │       ├── damage_calc.py # ✅ Optimized damage calculator
│   │       ├── battle_ai.py  # AI decision making
│   │       └── turn_logic.py # Turn order and execution
│   └── ui/
│       └── battle_ui.py      # Battle interface
└── data/
    ├── types.json            # ✅ Enhanced type chart (12 German types)
    ├── monsters.json         # Monster database
    └── moves.json            # Move database
```

## 🔧 ALREADY IMPLEMENTED FEATURES

### ✅ Type System V2 (COMPLETED)
- **12 German Types**: Feuer, Wasser, Erde, Luft, Pflanze, Bestie, Energie, Chaos, Seuche, Mystik, Gottheit, Teufel
- **NumPy-optimized** effectiveness matrix with <1ms lookups
- **Advanced features**: Coverage analysis, defensive profiles, team synergy
- **Battle Conditions**: Normal, Inverse, Chaos, Pure
- **Damage Calculator Pipeline** with modular stages
- **Critical Hit Tiers**: Normal, Improved, Guaranteed, Devastating
- **German localization** for all battle messages

### ✅ Core Systems
- Monster stats: HP, ATK, DEF, MAG, RES, SPD
- Stat stages: -6 to +6 modifications
- Status effects framework
- STAB bonus (1.2x)
- Weather and terrain effects

## 🎯 REQUIRED: DQM-STYLE BATTLE SYSTEM

### 1. TURN-BASED COMBAT FLOW
```python
class BattleFlow:
    """
    DQM-style battle flow:
    1. Command Input Phase (all commands before any action)
    2. Turn Order Calculation (SPD-based)
    3. Action Execution Phase (in order)
    4. End-of-Turn Effects
    """
    
    def battle_loop(self):
        # Phase 1: Collect ALL commands first
        player_commands = self.collect_player_commands()  # For all party monsters
        enemy_commands = self.ai_decide_commands()        # AI decides for all
        
        # Phase 2: Calculate turn order
        turn_order = self.calculate_turn_order(all_monsters)
        
        # Phase 3: Execute in SPD order
        for actor in turn_order:
            if not actor.is_fainted():
                self.execute_action(actor, commands[actor])
        
        # Phase 4: End-of-turn
        self.process_end_of_turn()
```

### 2. DQM PARTY MECHANICS
- **3v3 battles** as standard (expandable to 4v4)
- **Switch mechanic**: Use turn to switch monsters
- **Party-wide buffs**: Some moves affect entire party
- **Combo attacks**: Monsters can combine moves
- **Formation bonuses**: Front/back row positioning

### 3. DQM COMMAND SYSTEM
```python
class BattleCommands:
    ATTACK = "attack"      # Basic physical attack
    SKILL = "skill"        # Use a skill/spell
    DEFEND = "defend"      # Reduce damage this turn (0.5x)
    SWITCH = "switch"      # Change monster
    ITEM = "item"         # Use item
    FLEE = "flee"         # Attempt escape
    
    # DQM Special Commands
    PSYCHE_UP = "psyche"   # Charge for next turn (2x damage)
    MEDITATE = "meditate"  # Restore MP
    INTIMIDATE = "intimidate" # Lower enemy stats
```

### 4. DQM SKILL/MAGIC SYSTEM
```python
class SkillCategories:
    # Physical Skills
    SLASH = "slash"        # Sword techniques
    STRIKE = "strike"      # Martial arts
    
    # Magic Schools (DQM-style)
    FIRE = "fire"         # Frizz, Frizzle, Kafrizz
    ICE = "ice"          # Crack, Crackle, Kacrack  
    THUNDER = "thunder"   # Zap, Zapple, Kazap
    WIND = "wind"        # Woosh, Swoosh, Kaswoosh
    HEAL = "heal"        # Heal, Midheal, Fullheal
    BUFF = "buff"        # Buff, Kabuff, etc.
    DEBUFF = "debuff"    # Sap, Kasap, etc.
    STATUS = "status"    # Sleep, Poison, Paralysis
```

### 5. DQM AI BEHAVIOR PATTERNS
```python
class AIPersonality:
    """DQM-style AI personalities"""
    
    AGGRESSIVE = {
        "attack": 0.6,
        "skill": 0.3,
        "defend": 0.05,
        "heal": 0.05
    }
    
    DEFENSIVE = {
        "attack": 0.2,
        "skill": 0.2,
        "defend": 0.4,
        "heal": 0.2
    }
    
    TACTICAL = {
        "attack": 0.3,
        "skill": 0.4,
        "defend": 0.1,
        "heal": 0.2
    }
    
    WISE = {
        # Analyzes type effectiveness
        # Uses best moves for situation
        # Heals at optimal times
    }
```

### 6. DQM STATUS EFFECTS
```python
class StatusEffects:
    # Standard Status
    POISON = "poison"         # Lose HP each turn
    PARALYSIS = "paralysis"   # May skip turn
    SLEEP = "sleep"          # Cannot act
    CONFUSION = "confusion"   # May attack allies
    BURN = "burn"            # Damage + reduced ATK
    FREEZE = "freeze"        # Cannot act, takes more damage
    
    # DQM Special Status
    DAZZLE = "dazzle"        # Cannot use magic
    CURSE = "curse"          # Reduced stats
    BERSERK = "berserk"      # Auto-attack with bonus
    BOUNCE = "bounce"        # Reflects magic
```

### 7. BATTLE UI REQUIREMENTS

```python
class BattleUI:
    """
    DQM-style battle interface:
    
    ┌─────────────────────────────────────┐
    │  Enemy Party (3 monsters)           │
    │  [HP/MP bars and status icons]      │
    ├─────────────────────────────────────┤
    │                                     │
    │     Battle Animation Area          │
    │                                     │
    ├─────────────────────────────────────┤
    │  Player Party (3 monsters)          │
    │  [HP/MP/EXP bars and status]        │
    ├─────────────────────────────────────┤
    │  Command Menu / Battle Log          │
    │  > Attack  Skill  Defend  Item      │
    └─────────────────────────────────────┘
    """
    
    def render_battle_screen(self):
        # Split screen layout
        # Enemy party top
        # Player party bottom
        # Commands/log at bottom
        # Smooth animations
        # Damage numbers pop-up
        # Type effectiveness indicators
```

### 8. VICTORY/REWARD SYSTEM
```python
class VictoryHandler:
    def process_victory(self):
        # EXP distribution (DQM-style)
        # All party members get EXP (even fainted)
        # Bonus EXP for participation
        # Level up notifications
        # Skill learning
        # Item drops
        # Gold rewards
        # Chance to recruit defeated monsters
```

### 9. SPECIAL DQM MECHANICS

```python
class SpecialMechanics:
    # Tension System
    tension_levels = [1.0, 1.5, 2.0, 2.5]  # Damage multipliers
    
    # Monster Traits
    traits = {
        "metal_body": "High DEF, immune to magic",
        "critical_master": "Higher crit chance",
        "early_bird": "Acts first regardless of SPD",
        "last_stand": "Damage up when HP low"
    }
    
    # Synthesis Skills
    # When specific monsters are in party together
    synthesis_combos = {
        ("FireDragon", "IceGolem"): "Scorch Blizzard",
        ("ThunderBird", "WindDancer"): "Storm Call"
    }
```

## 📋 IMPLEMENTATION REQUIREMENTS

### MUST MAINTAIN:
1. **Existing type system** (types.py) - Already optimized, don't modify core
2. **German type names** - All 12 types remain German
3. **Damage calculator pipeline** - Use existing optimized system
4. **File structure** - Keep current organization
5. **Save system compatibility** - Don't break existing saves

### MUST IMPLEMENT:
1. **Complete turn-based flow** with command collection phase
2. **3v3 party battles** with proper turn order
3. **DQM command menu** with all options
4. **Status effect system** with all DQM effects
5. **AI personality system** with multiple behaviors
6. **Battle animations** and visual feedback
7. **Victory/reward handler** with EXP distribution
8. **Sound integration** for attacks/effects
9. **Battle log** with scrolling text
10. **Escape mechanics** based on SPD comparison

### CODE QUALITY REQUIREMENTS:
```python
# Every class must have:
- Comprehensive docstrings
- Type hints for all methods
- Error handling
- Performance optimization
- Modular, testable design

# Example structure:
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

@dataclass
class BattleAction:
    """Represents a single battle action."""
    actor: MonsterInstance
    command: BattleCommand
    target: Optional[MonsterInstance]
    skill: Optional[Skill]
    priority: int = 0
    
    def execute(self) -> BattleResult:
        """Execute this battle action."""
        pass
```

### INTEGRATION POINTS:

1. **With Type System V2:**
```python
from engine.systems.types import type_chart, type_api
# Use for all type calculations
effectiveness = type_chart.calculate_type_multiplier(move_type, defender_types)
```

2. **With Damage Calculator:**
```python
from engine.systems.battle.damage_calc import DamageCalculator
calculator = DamageCalculator()
result = calculator.calculate(attacker, defender, move)
```

3. **With Monster System:**
```python
from engine.systems.monster_instance import MonsterInstance
# Ensure all stat modifications go through proper methods
monster.modify_stat_stage('atk', 1)  # Raise attack by 1 stage
```

## 🎨 UI/UX REQUIREMENTS

### Battle Screen Layout:
- **16:9 aspect ratio** optimized (1280x720 minimum)
- **Smooth transitions** between phases
- **Particle effects** for attacks
- **Screen shake** for critical hits
- **Floating damage numbers** with type colors
- **Status icon overlays** on monster sprites
- **HP/MP bars** with smooth depletion
- **Turn order indicator** showing upcoming turns

### Controls:
- **Keyboard**: Arrow keys + Z/X/C for confirm/cancel/menu
- **Mouse**: Full mouse support with hover tooltips
- **Gamepad**: Full controller support

## 📊 PERFORMANCE TARGETS

- Battle initialization: <100ms
- Turn calculation: <10ms
- Animation frame rate: 60 FPS
- Memory usage: <50MB for battle scene
- Save/load battle state: <500ms

## 🧪 TESTING REQUIREMENTS

Create comprehensive tests for:
1. Turn order calculation
2. Damage formulas
3. Status effect interactions
4. AI decision making
5. Victory conditions
6. Edge cases (all monsters fainted simultaneously)

## 📚 DOCUMENTATION NEEDED

1. **Battle Flow Diagram** (Mermaid/PlantUML)
2. **Command Reference** (all commands and effects)
3. **Status Effect Reference** (duration, effects, cures)
4. **AI Behavior Documentation**
5. **Integration Guide** for other systems

## 🎯 SUCCESS CRITERIA

The battle system is complete when:
- [ ] All DQM-style commands work correctly
- [ ] 3v3 battles run smoothly at 60 FPS
- [ ] AI makes intelligent decisions based on personality
- [ ] All status effects implemented and tested
- [ ] Victory/defeat conditions handle all edge cases
- [ ] Battle can be saved/loaded mid-combat
- [ ] Performance targets met
- [ ] Full keyboard/mouse/gamepad support
- [ ] Comprehensive test coverage (>80%)
- [ ] Documentation complete

## 💡 ADDITIONAL NOTES

- Prioritize game feel and responsiveness
- Ensure battles feel strategic, not random
- Balance speed vs tactical depth
- Make AI challenging but fair
- Include difficulty settings
- Consider accessibility features
- Plan for future multiplayer support

## 🚀 EXAMPLE IMPLEMENTATION START

```python
"""
Battle System - Main Controller
Implements DQM-style turn-based combat
"""

from typing import List, Dict, Optional, Tuple
from enum import Enum, auto
from dataclasses import dataclass, field
import pygame
from engine.systems.types import type_chart, type_api
from engine.systems.battle.damage_calc import DamageCalculator

class BattlePhase(Enum):
    """Battle flow phases."""
    INITIALIZATION = auto()
    COMMAND_INPUT = auto()
    TURN_ORDER = auto()
    ACTION_EXECUTION = auto()
    END_OF_TURN = auto()
    VICTORY = auto()
    DEFEAT = auto()

class BattleController:
    """
    Main battle controller implementing DQM-style combat.
    
    Manages the complete battle flow from initialization to victory/defeat.
    Handles 3v3 party battles with full command system.
    """
    
    def __init__(self, player_party: List[MonsterInstance], 
                 enemy_party: List[MonsterInstance]):
        """Initialize battle with both parties."""
        self.player_party = player_party[:3]  # Max 3 active
        self.enemy_party = enemy_party[:3]
        self.phase = BattlePhase.INITIALIZATION
        self.turn_count = 0
        self.battle_log: List[str] = []
        self.damage_calc = DamageCalculator()
        
    def run_battle(self) -> BattleResult:
        """Main battle loop."""
        while self.phase not in [BattlePhase.VICTORY, BattlePhase.DEFEAT]:
            self.process_phase()
        return self.generate_battle_result()
```

---

**END OF PROMPT**

Use this prompt to guide the AI in completing the DQM-style battle system. The AI should maintain all existing optimized systems while adding the missing DQM mechanics in a performant, well-documented manner.