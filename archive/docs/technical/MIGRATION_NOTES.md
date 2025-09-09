# Migration Notes - Type System V2

## Date: 2025-01-19

## Current System Analysis

### Type System Structure
- **12 Types Total**: Feuer, Wasser, Erde, Luft, Pflanze, Bestie, Energie, Chaos, Seuche, Mystik, Gottheit, Teufel
- **Legendary Types**: Gottheit (Deity) and Teufel (Devil) - reserved for legendary monsters
- **STAB Multiplier**: 1.2x

### Key Observations from Legacy Code

1. **types.py Structure**:
   - Singleton TypeChart pattern implemented
   - Type effectiveness loaded from JSON
   - Support for dual-type monsters
   - Coverage analysis and suggestion methods
   - TypeEffectivenessResult class for battle messages

2. **damage_calc.py Structure**:
   - DamageCalculator class with seed support
   - Critical hit mechanics (1/16 base chance, 1.5x damage)
   - STAB implementation (1.2x)
   - Random damage spread (85-100%)
   - Weather and terrain modifiers
   - Status effect interactions (burn, paralysis)

3. **types.json Format**:
   - Uses "attacker", "defender", "multiplier" fields (NOT "att", "def", "x")
   - Contains type descriptions in German
   - Comprehensive type matchup chart

### Custom Modifications to Preserve

1. **German Type Names**: All types use German names (Feuer, Wasser, etc.)
2. **Legendary Type System**: Gottheit and Teufel for legendary monsters only
3. **Extended Type Interactions**: Complex relationships between 12 types
4. **Battle Messages in German**: "Sehr effektiv!", "Nicht sehr effektiv...", etc.

### Dependencies Identified

- `engine.core.resources` for JSON loading
- `engine.systems.monster_instance.MonsterInstance`
- `engine.systems.moves.Move`

### Performance Baseline (Legacy System)
- Type lookups: ~50-100ms (estimated, needs measurement)
- Damage calculations: ~100-200ms (estimated, needs measurement)
- Memory usage: Unknown (needs measurement)

## Migration Strategy

### Phase 1: ✅ Backup Complete
- `types_legacy.py` saved
- `damage_calc_legacy.py` saved
- `types_legacy.json` saved

### Phase 2: Install New System (In Progress)
- Need to adapt type_refactored.py for German names
- Need to fix JSON field mapping (attacker/defender/multiplier)
- Need to preserve battle messages in German

### Phase 3-8: Pending

## Critical Adaptations Required

1. **JSON Field Mapping**:
   - Old: "attacker", "defender", "multiplier"
   - New expected: "att", "def", "x"
   - Solution: Modify loader to handle both formats

2. **German Language Support**:
   - Keep all type names in German
   - Maintain German battle messages
   - Update documentation in German where appropriate

3. **Integration Points**:
   - Update imports in battle.py
   - Update battle_ai.py for new API
   - Ensure save file compatibility

## Next Steps
1. Create adapted type_refactored.py with German support
2. Create optimized damage_calc_optimized.py
3. Update types.json to enhanced format
4. Run initial tests
5. Profile performance improvements