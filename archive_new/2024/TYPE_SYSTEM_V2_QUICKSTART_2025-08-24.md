# Type System V2 - Quick Start Guide

## 🚀 Sofort loslegen

### Basic Usage

```python
# Import the new system
from engine.systems.types import type_chart, type_api
from engine.systems.battle.damage_calc import DamageCalculator

# Check type effectiveness
effectiveness = type_chart.get_effectiveness("Feuer", "Wasser")  # 0.5

# Calculate damage
calculator = DamageCalculator()
result = calculator.calculate(attacker, defender, move)
print(f"Damage: {result.damage}, Effectiveness: {result.effectiveness}x")
```

### Advanced Features

#### 1. Type Coverage Analysis
```python
# Analyze offensive coverage for a moveset
move_types = ["Feuer", "Wasser", "Pflanze", "Energie"]
coverage = type_chart.get_type_coverage_analysis(move_types)

print(f"Coverage Score: {coverage['coverage_score']:.1%}")
print(f"Super effective against: {coverage['super_effective']}")
print(f"Recommended additions: {coverage['recommendations']}")
```

#### 2. Defensive Profile
```python
# Analyze defensive strengths/weaknesses
monster_types = ["Feuer", "Erde"]  # Dual type
profile = type_chart.get_defensive_profile(monster_types)

print(f"Weaknesses: {profile['weaknesses']}")
print(f"Resistances: {profile['resistances']}")
print(f"Defensive Score: {profile['defensive_score']:.2f}")
```

#### 3. Team Composition Analysis
```python
# Analyze team synergy
team = [
    ["Feuer", "Erde"],    # Monster 1
    ["Wasser", "Pflanze"], # Monster 2
    ["Luft", "Energie"]    # Monster 3
]

analysis = type_api.analyze_team_composition(team)
print(f"Team Balance: {analysis['balance_score']:.1%}")
print(f"Common Weaknesses: {analysis['defensive_weaknesses']}")
print(f"Synergy Score: {analysis['synergy_score']:.1%}")
```

#### 4. Battle Matchup Prediction
```python
# Predict battle outcome
attacker_types = ["Feuer", "Erde"]
defender_types = ["Pflanze", "Wasser"]

prediction = type_api.predict_matchup(attacker_types, defender_types)
print(f"Advantage: {prediction['advantage']}")
print(f"Confidence: {prediction['confidence']:.0f}%")
print(f"Key Factors: {prediction['key_factors']}")
```

#### 5. Battle Conditions
```python
from engine.systems.types import BattleCondition

# Normal battle
type_api.set_battle_condition(BattleCondition.NORMAL)

# Inverse battle (type effectiveness reversed)
type_api.set_battle_condition(BattleCondition.INVERSE)

# Chaos battle (random modifiers)
type_api.set_battle_condition(BattleCondition.CHAOS)

# Pure battle (only STAB moves effective)
type_api.set_battle_condition(BattleCondition.PURE)
```

#### 6. Adaptive Resistance
```python
# Monster learns to resist repeated attacks
type_chart.accumulate_adaptive_resistance("Feuer", "Pflanze")

# After 10 Feuer attacks on Pflanze type:
# Effectiveness reduces from 2.0x → ~1.5x

# Reset for new battle
type_chart.reset_adaptive_resistances()
```

#### 7. Damage Preview (No RNG)
```python
# Preview damage range before attacking
preview = calculator.preview_damage(attacker, defender, move)

print(f"Damage Range: {preview['min']}-{preview['max']}")
print(f"Average: {preview['average']:.0f}")
print(f"Can Critical: {preview['can_critical']}")
```

#### 8. Multi-Hit Moves
```python
# Calculate multi-hit move damage
result = calculator.calculate_multi_hit(
    attacker, defender, move,
    hit_count=3  # Or None for random 2-5 hits
)

print(f"Total Damage: {result.get_total_damage()}")
print(f"Hits: {result.hit_count}")
print(f"Per Hit: {result.individual_damages}")
```

## 🎮 Battle Integration

### Update Battle State
```python
class BattleState:
    def __init__(self):
        self.damage_calc = DamageCalculator()
        
    def execute_move(self, attacker, defender, move):
        # Calculate damage with all modifiers
        result = self.damage_calc.calculate(
            attacker, defender, move,
            weather=self.weather,
            terrain=self.terrain
        )
        
        # Apply damage
        defender.current_hp -= result.damage
        
        # Show message
        if result.effectiveness >= 2.0:
            self.show_message(f"{result.effectiveness_text}")
        
        # Check critical
        if result.is_critical:
            tier_name = result.critical_tier.name
            self.show_message(f"Kritischer Treffer! ({tier_name})")
```

### Custom Damage Modifiers
```python
from engine.systems.battle.damage_calc import DamageModifier

# Add weather boost
sunny_boost = DamageModifier(
    name="Sunny Day",
    multiplier=1.5,
    condition=lambda ctx: ctx['move'].type == "Feuer",
    priority=5
)

calculator.add_global_modifier(sunny_boost)

# Remove when weather changes
calculator.remove_global_modifier("Sunny Day")
```

## 📊 Performance Tips

### 1. Warm Up Cache
```python
# At game start
type_chart._precompute_common()
```

### 2. Monitor Performance
```python
# Check cache effectiveness
stats = type_chart.get_performance_stats()
if stats['cache_hit_rate'] < 0.7:
    print("Warning: Low cache hit rate")
```

### 3. Batch Operations
```python
# For AI calculations, batch multiple checks
types_to_check = ["Feuer", "Wasser", "Pflanze"]
results = {}

for move_type in types_to_check:
    results[move_type] = type_chart.calculate_type_multiplier(
        move_type, defender.types
    )

best_move = max(results, key=results.get)
```

## 🐛 Debugging

### Check Type Data
```python
# List all types
print(type_chart.type_names)

# Check specific matchup
eff = type_chart.get_effectiveness("Feuer", "Wasser")
print(f"Feuer vs Wasser: {eff}x")

# View effectiveness matrix
import numpy as np
np.set_printoptions(precision=1)
print(type_chart.effectiveness_matrix)
```

### Performance Profiling
```python
import time

# Profile type lookups
start = time.perf_counter()
for _ in range(10000):
    type_chart.get_effectiveness("Feuer", "Wasser")
elapsed = time.perf_counter() - start
print(f"10k lookups: {elapsed:.3f}s ({elapsed/10:.6f}s each)")

# Profile damage calculations
start = time.perf_counter()
for _ in range(1000):
    calculator.calculate(attacker, defender, move)
elapsed = time.perf_counter() - start
print(f"1k calcs: {elapsed:.3f}s ({elapsed:.6f}s each)")
```

## ⚠️ Common Pitfalls

### 1. Type Names sind Deutsch!
```python
# ❌ WRONG
effectiveness = type_chart.get_effectiveness("Fire", "Water")

# ✅ CORRECT
effectiveness = type_chart.get_effectiveness("Feuer", "Wasser")
```

### 2. Reset Adaptive Resistance
```python
# After each battle
type_chart.reset_adaptive_resistances()
```

### 3. Use Singleton Instance
```python
# ❌ WRONG - Creates new instance
chart = TypeChart()

# ✅ CORRECT - Use global singleton
from engine.systems.types import type_chart
```

## 📚 API Reference

### TypeChart Methods
- `get_effectiveness(attacker, defender, condition)` - Get single matchup
- `calculate_type_multiplier(move_type, defender_types)` - Multi-type calc
- `get_type_coverage_analysis(move_types)` - Offensive coverage
- `get_defensive_profile(monster_types)` - Defensive analysis
- `accumulate_adaptive_resistance(att, def)` - Build resistance
- `validate_type_balance()` - Check system balance

### TypeSystemAPI Methods
- `check_type_effectiveness(move, def_types, att_types)` - Full check with STAB
- `analyze_team_composition(team)` - Team synergy analysis
- `predict_matchup(att_types, def_types)` - Battle prediction
- `set_battle_condition(condition)` - Change battle rules

### DamageCalculator Methods
- `calculate(attacker, defender, move, **kwargs)` - Standard damage
- `calculate_multi_hit(attacker, defender, move, hits)` - Multi-hit
- `preview_damage(attacker, defender, move)` - Damage range
- `add_global_modifier(modifier)` - Add custom modifier
- `get_performance_stats()` - Performance metrics

## 🎉 That's it!

You're ready to use the new Type System V2. Happy coding! 🚀