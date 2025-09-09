# BATTLE SYSTEM MAP - Übersicht der Dateien und Verbindungen

## 🏗️ SYSTEM ARCHITEKTUR

### CORE BATTLE SYSTEM
```
engine/systems/battle/
├── battle_controller.py          # 🎯 HAUPTKONTROLLER
├── battle_state_manager.py       # 📊 STATE MANAGEMENT
├── battle_actions.py             # ⚔️ ACTION EXECUTION
├── battle_ai.py                  # 🤖 ENEMY AI
├── battle_enums.py               # 📋 ENUMS & CONSTANTS
├── battle_events.py              # 📡 EVENT SYSTEM
├── battle_validation.py          # ✅ VALIDATION
└── turn_logic_clean.py           # 🔄 TURN MANAGEMENT
```

### SPECIALIZED SYSTEMS
```
engine/systems/battle/
├── meat_system.py                # 🥩 TAMING SYSTEM
├── reward_system.py              # 💰 REWARDS
├── status_effects_dqm.py         # 🎭 STATUS EFFECTS
├── dqm_formulas.py               # 🧮 DQM CALCULATIONS
├── dqm_integration.py            # 🔗 DQM INTEGRATION
└── skills_dqm_integrated.py      # ⚡ SKILLS SYSTEM
```

### UI COMPONENTS
```
engine/ui/
├── battle_ui.py                  # 🖥️ MAIN BATTLE UI
├── battle_ui_utils.py            # 🛠️ UI UTILITIES
├── battle_ui_enhancements.py     # ✨ UI ENHANCEMENTS
├── battle_rewards_ui.py          # 🎁 REWARDS UI
├── battle_log.py                 # 📝 BATTLE LOG
├── battle_styles.py              # 🎨 UI STYLES
└── taming_ui.py                  # 🥩 TAMING UI
```

### SCENE MANAGEMENT
```
engine/scenes/
├── battle_scene.py               # 🎬 MAIN BATTLE SCENE
├── battle_scene_optimized.py     # ⚡ OPTIMIZED SCENE
└── battle/
    ├── battle_scene_phases.py    # 📋 PHASE MANAGEMENT
    ├── battle_scene_actions.py   # ⚔️ ACTION HANDLING
    ├── battle_scene_effects.py   # ✨ EFFECTS
    └── battle_scene_input.py     # ⌨️ INPUT HANDLING
```

## 🔗 VERBINDUNGEN & ABHÄNGIGKEITEN

### HAUPTFLUSS
```
BattleScene
    ↓
BattleController
    ↓
BattleStateManager
    ↓
BattleActionExecutor
    ↓
UnifiedDamageCalculator
```

### ACTION FLOW
```
UI Input → BattleAction → BattleActionExecutor → Damage/Effect → BattleState Update
```

### EVENT FLOW
```
Action Execution → BattleEvent → EventGenerator → UI Update
```

## 📋 DATEI-FUNKTIONEN

### 🎯 battle_controller.py
**Funktion:** Hauptkoordinator für alle Battle-Subsysteme
**Verbindungen:**
- BattleStateManager (State)
- BattleActionExecutor (Actions)
- BattleAI (Enemy Logic)
- MeatSystem (Taming)
- RewardSystem (Rewards)

**Wichtige Methoden:**
- `start_battle()` - Battle initialisieren
- `execute_turn()` - Turn ausführen
- `queue_player_action()` - Player Action hinzufügen
- `execute_enemy_turn()` - Enemy Turn ausführen

### 📊 battle_state_manager.py
**Funktion:** Battle State Management
**Verbindungen:**
- MonsterInstance (Teams)
- BattlePhase (Phases)
- BattleType (Types)

**Wichtige Methoden:**
- `validate_battle_state()` - State validieren
- `has_able_monsters()` - Fähige Monster prüfen
- `queue_player_action()` - Actions queue

### ⚔️ battle_actions.py
**Funktion:** Action Execution
**Verbindungen:**
- UnifiedDamageCalculator (Damage)
- MeatSystem (Taming)
- ItemEffectHandler (Items)
- StatusEffects (Status)

**Wichtige Methoden:**
- `execute_action()` - Action ausführen
- `_execute_attack()` - Attack ausführen
- `_execute_tame()` - Taming ausführen
- `_execute_use_meat()` - Meat verwenden

### 🤖 battle_ai.py
**Funktion:** Enemy AI Logic
**Verbindungen:**
- BattleState (State)
- MonsterInstance (Enemy)
- ActionType (Actions)

**Wichtige Methoden:**
- `choose_action()` - AI Action wählen
- `evaluate_threats()` - Bedrohungen bewerten
- `calculate_action_priority()` - Priorität berechnen

### 🥩 meat_system.py
**Funktion:** Taming System
**Verbindungen:**
- MeatType (Meat Types)
- BattleState (State)

**Wichtige Methoden:**
- `use_meat()` - Meat verwenden
- `calculate_taming_chance()` - Taming Chance berechnen
- `get_active_meat_name()` - Aktives Meat abrufen

### 💰 reward_system.py
**Funktion:** Battle Rewards
**Verbindungen:**
- BattleState (State)
- MonsterInstance (Monsters)
- ExperienceSystem (EXP)

**Wichtige Methoden:**
- `calculate_battle_rewards()` - Rewards berechnen
- `apply_rewards()` - Rewards anwenden

## 🚨 FEHLENDE VERBINDUNGEN

### ❌ NICHT IMPLEMENTIERT
1. **Status Effects Integration**
   - `status_effects_dqm.py` nicht mit BattleController verbunden
   - ConditionManager fehlt in MonsterInstance

2. **Skills System Integration**
   - `skills_dqm_integrated.py` nicht verwendet
   - Skill-Actions nicht implementiert

3. **Event System Integration**
   - `battle_events.py` nicht vollständig integriert
   - UI bekommt keine Events

4. **Validation System**
   - `battle_validation.py` nicht verwendet
   - Action-Validation fehlt

### ⚠️ TEILWEISE IMPLEMENTIERT
1. **Meat System**
   - Grundfunktionen vorhanden
   - Integration in BattleController defekt

2. **Reward System**
   - Berechnung vorhanden
   - Integration in BattleController fehlt

3. **AI System**
   - Grundlogik vorhanden
   - Integration in BattleController unvollständig

## 🔧 REPARATUR-PLAN

### PHASE 1: KRITISCHE FIXES
1. **Move Constructor** - `description` Parameter hinzufügen
2. **ConditionManager** - `active_conditions` Attribut hinzufügen
3. **BattleController** - Fehlende Methoden implementieren

### PHASE 2: SYSTEM INTEGRATION
1. **Status Effects** - Vollständige Integration
2. **Meat System** - BattleController Integration
3. **Reward System** - BattleController Integration
4. **Event System** - UI Integration

### PHASE 3: OPTIMIERUNG
1. **Performance** - Bottlenecks beheben
2. **Error Handling** - Try-catch Blöcke hinzufügen
3. **API Consistency** - Einheitliche Interfaces

## 📊 SYSTEM STATUS

### ✅ FUNKTIONIERT
- Battle Initialization
- Basic Action Execution
- Battle End Conditions
- Performance (unter 50ms)

### ❌ DEFEKT
- Move System (Constructor)
- Status Effects (Integration)
- Meat System (BattleController)
- Reward System (BattleController)
- Event System (UI)

### ⚠️ UNVOLLSTÄNDIG
- AI System (Integration)
- Skills System (Nicht verwendet)
- Validation System (Nicht verwendet)

## 🎯 NÄCHSTE SCHRITTE

1. **Kritische Fixes** (Phase 1)
2. **System Integration** (Phase 2)
3. **Performance Optimierung** (Phase 3)
4. **Vollständige Tests** (Phase 4)

## 📝 NOTIZEN

- Battle-System ist grundsätzlich funktionsfähig
- Hauptproblem: Fehlende Integration zwischen Komponenten
- Test-Suite deckt alle wichtigen Features ab
- Performance ist gut, aber Features sind defekt
- API-Inkonsistenzen erschweren Wartung
