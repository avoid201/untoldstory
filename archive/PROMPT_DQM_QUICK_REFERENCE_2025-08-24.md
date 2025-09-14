# 🚀 QUICK REFERENCE: DQM BATTLE SYSTEM PROMPT

## 🎯 ONE-SENTENCE BRIEF
**Create a Dragon Quest Monsters style 3v3 turn-based battle system that collects all commands before execution, uses the existing Type System V2, and maintains German localization.**

## 📋 CHECKLIST FORMAT

### MUST HAVE (Core DQM Features)
- [ ] **Command Collection Phase** - Get ALL commands before ANY action
- [ ] **3v3 Party Battles** - Both player and enemy sides
- [ ] **SPD-based Turn Order** - Faster monsters act first
- [ ] **German Battle Messages** - "Sehr effektiv!", etc.
- [ ] **Status Effects** - Poison, Sleep, Paralysis, Burn, Freeze
- [ ] **Victory Screen** - EXP distribution, level ups, item drops

### MUST USE (Existing Systems)
- [ ] `type_chart.calculate_type_multiplier()` for type effectiveness
- [ ] `DamageCalculator.calculate()` for all damage
- [ ] German type names (Feuer, Wasser, etc.)
- [ ] Existing MonsterInstance class structure

### MUST NOT
- [ ] Modify types.py or damage_calc.py
- [ ] Change German type names
- [ ] Break save file compatibility
- [ ] Drop below 60 FPS

## 💻 CODE SKELETON

```python
# The AI should implement this structure:

class BattleController:
    """DQM-style battle system."""
    
    def battle_loop(self):
        """Core battle loop - THIS IS THE KEY PATTERN"""
        while not battle_over:
            # 1. COMMAND PHASE (DQM signature)
            player_commands = get_all_player_commands()  # ← ALL at once
            enemy_commands = get_all_ai_commands()       # ← ALL at once
            
            # 2. TURN ORDER
            all_actions = player_commands + enemy_commands
            all_actions.sort(key=lambda x: x.actor.spd, reverse=True)
            
            # 3. EXECUTION
            for action in all_actions:
                if not action.actor.is_fainted():
                    execute_action(action)
                    
            # 4. END TURN
            apply_status_damage()
            check_victory_conditions()
```

## 🎮 DQM COMMAND MENU

```
┌─────────────────┐
│ Was soll X tun? │  (What should X do?)
├─────────────────┤
│ ▶ Angriff       │  (Attack)
│   Fähigkeit     │  (Skill)
│   Verteidigen   │  (Defend)  
│   Gegenstand    │  (Item)
│   Wechseln      │  (Switch)
│   Flucht        │  (Flee)
└─────────────────┘
```

## 🤖 AI PERSONALITY QUICK RULES

```python
ai_personalities = {
    "aggressive": {"attack": 70%, "skill": 20%, "defend": 10%},
    "defensive":  {"attack": 30%, "defend": 40%, "heal": 30%},
    "tactical":   {"best_type_matchup": 60%, "status": 40%},
    "wise":       {"analyze_and_exploit_weakness": 100%}
}
```

## 📊 TURN ORDER FORMULA

```python
turn_priority = monster.spd + action_bonus + random(0, 10)

action_bonus = {
    "flee": +1000,    # Always first
    "switch": +500,   # Very high priority
    "item": +100,     # High priority
    "defend": +50,    # Medium priority
    "skill": 0,       # Normal
    "attack": 0       # Normal
}
```

## ✅ VALIDATION QUESTIONS

Ask yourself:
1. Do players input ALL commands before seeing ANY action? ✓
2. Can both sides have 3 active monsters? ✓
3. Does SPD determine turn order? ✓
4. Are messages in German? ✓
5. Does it feel like Dragon Quest Monsters? ✓

## 🎯 FINAL INSTRUCTION

**PROMPT TO AI:**
```
Implement a Dragon Quest Monsters (DQM) style battle system where:
1. Players choose all commands for their party BEFORE any action occurs
2. Turn order is determined by monster SPD stats
3. 3v3 party battles are the standard
4. All battle messages are in German
5. Use the existing type_chart and DamageCalculator - don't reinvent

Focus on the command-collection-first pattern that defines DQM combat.
The battle should feel tactical and deliberate, not reactive.
```

## 📁 EXPECTED OUTPUT FILES

1. `battle_controller.py` - Main logic (300-500 lines)
2. `battle_commands.py` - Command handlers (200 lines)
3. `battle_ai.py` - AI decisions (200 lines)
4. `battle_ui.py` - Interface (400 lines)
5. `battle_animations.py` - Visual effects (200 lines)

## 🏆 SUCCESS INDICATOR

The battle system is correct when:
- Players can't react to enemy actions (all commands chosen first)
- A slow monster with Flee command escapes before fast enemy attacks
- Status effects work across turns
- German messages appear for all battle events
- The game maintains 60 FPS during 3v3 battles

---

**TL;DR: Make it like Dragon Quest Monsters - collect all commands first, then execute by speed. Use existing systems, keep it German, make it smooth.**