# Legacy Functions Cleanup - Backup Archive

This directory contains backups of all legacy functions that were removed from the active codebase during the cleanup process on 2025-09-03.

## Files in this Archive

### 1. `legacy_stats_damage_calculator.py`
- **Source**: `engine/systems/stats.py`
- **Removed**: `DamageCalculator` class
- **Reason**: DEPRECATED - Delegiert an UnifiedDamageCalculator
- **Replacement**: Use `UnifiedDamageCalculator` instead

### 2. `legacy_unified_damage_calculator_wrappers.py`
- **Source**: `engine/systems/unified_damage_calculator.py`
- **Removed**: 
  - `DQMCalculator` class
  - `DQMSkillCalculator` class
  - `DQMDamageStage` class
  - Legacy compatibility functions
- **Reason**: DEPRECATED - All delegate to UnifiedDamageCalculator
- **Replacement**: Use `UnifiedDamageCalculator` directly

### 3. `legacy_dqm_integration_functions.py`
- **Source**: `engine/systems/battle/dqm_integration.py`
- **Removed**:
  - `enable_dqm_formulas()` function
  - `disable_dqm_formulas()` function
  - `DQMIntegration.integrate_with_pipeline()` method
  - `DQMIntegration.rollback_integration()` method
- **Reason**: DEPRECATED - Use UnifiedDamageCalculator instead
- **Replacement**: Use `UnifiedDamageCalculator` directly

### 4. `legacy_monster_instance_methods.py`
- **Source**: `engine/systems/monster_instance.py`
- **Removed**:
  - `learn_move()` method
  - Legacy status system methods
- **Reason**: DEPRECATED - Moves werden über Talents gelernt
- **Replacement**: Use `learn_talent()` method instead

### 5. `legacy_battle_ui_compatibility.py`
- **Source**: `engine/ui/battle_ui.py`
- **Removed**:
  - `init_battle()` compatibility method
  - `set_menu_state()` compatibility method
  - `trigger_flash_effect()` compatibility method
  - `show_taming_result()` compatibility method
  - `init_demo_inventory()` compatibility method
  - Legacy sprite system
  - `BattleActionFactory` class
  - `get_standardized_action()` function
- **Reason**: DEPRECATED - Only for backward compatibility
- **Replacement**: Use new battle system components

## Cleanup Summary

All legacy functions have been successfully removed from the active codebase. The new system uses:

- **UnifiedDamageCalculator** for all damage calculations
- **Talent System** for move learning
- **New Battle System** for UI and battle management
- **Advanced Status System** for condition management

## Migration Notes

If you need to reference any of these legacy functions:

1. Check this archive for the original implementation
2. Update your code to use the new systems
3. The new systems provide better performance and more features
4. All legacy functionality is preserved in the new implementations

## Date of Cleanup

**2025-09-03 18:02:15**

This cleanup was performed to:
- Remove deprecated code
- Improve maintainability
- Reduce code complexity
- Ensure single source of truth for all systems
