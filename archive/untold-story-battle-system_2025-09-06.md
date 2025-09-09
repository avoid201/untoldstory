# 🎮 Untold Story - Battle System Design Document v6.0
## DQM × Pokémon Hybrid - AI-Optimized Reference (Aktualisiert 2025-09-06)

---

## 📊 **CORE BATTLE MECHANICS**

### System Overview
```yaml
battle_format: 1v1  # Pokémon-style
team_size: 6        # Pokémon-style  
turn_order: Speed-based (Pokémon)
stats: HP, ATK, DEF, MAG, RES, SPD  # DQM-style
moves: Unlimited (DQM-style, no 4-move limit)
talents: Move-learning system (DQM)
taming: Meat system (DQM, pre-applied)
synthesis: External (post-battle lab)
```

### Stats System (from monsters.json)
```python
base_stats = {
    "hp": 40,   # Health Points
    "atk": 54,  # Physical Attack
    "def": 38,  # Physical Defense  
    "mag": 24,  # Magic Attack
    "res": 20,  # Magic Resistance
    "spd": 44   # Speed (determines turn order)
}
```

---

## 🏗️ **BATTLE SYSTEM ARCHITECTURE**

### 📁 **Core Battle Files (45 files, 13,822 lines)**

#### **Battle Controller & State Management**
- **`engine/systems/battle/battle_controller.py`** (466 lines, 1 class)
  - `BattleController` - Central battle coordination
  - **Key Methods:**
    - `__init__(player_team, enemy_team, battle_type, can_flee, can_catch)`
    - `initialize(player_team, enemy_team) -> Dict[str, Any]`
    - `execute_turn(player_action, enemy_action) -> Dict[str, Any]`
    - `start_battle() -> Dict[str, Any]`
    - `process_player_input(action) -> Dict[str, Any]`
    - `process_enemy_turn() -> Dict[str, Any]`
    - `get_battle_state() -> Dict[str, Any]`
    - `get_battle_status() -> Dict[str, Any]`
    - `is_battle_over() -> bool`
    - `get_battle_result() -> Optional[BattleResult]`

- **`engine/systems/battle/battle_state.py`** (86 lines, 1 class)
  - `BattleState` - Pure data container
  - **Key Fields:**
    - `player_team: List[MonsterInstance]`
    - `enemy_team: List[MonsterInstance]`
    - `player_active: Optional[MonsterInstance]`
    - `enemy_active: Optional[MonsterInstance]`
    - `phase: BattlePhase`
    - `turn_count: int`
    - `battle_type: BattleType`
    - `can_flee: bool`
    - `can_catch: bool`

#### **Turn Processing & Action Management**
- **`engine/systems/battle/turn_processor.py`** (239 lines, 1 class)
  - `TurnProcessor` - Handles turn order and execution
  - **Key Methods:**
    - `process_turn(actions) -> Dict[str, Any]`
    - `calculate_turn_order(monsters) -> List[MonsterInstance]`
    - `execute_action(action) -> Dict[str, Any]`

- **`engine/systems/battle/action_processor.py`** (405 lines, 1 class)
  - `ActionProcessor` - Processes individual battle actions
  - **Key Methods:**
    - `process_action(action) -> Dict[str, Any]`
    - `validate_action(action) -> bool`
    - `execute_move_action(action) -> Dict[str, Any]`
    - `execute_switch_action(action) -> Dict[str, Any]`
    - `execute_item_action(action) -> Dict[str, Any]`
    - `execute_tame_action(action) -> Dict[str, Any]`

- **`engine/systems/battle/turn_logic.py`** (395 lines, 3 classes)
  - `BattleAction` - Action data structure
  - `ActionType` - Enum for action types
  - `TurnOrder` - Turn order calculation
  - **Key Methods:**
    - `TurnOrder.calculate_order(monsters) -> List[MonsterInstance]`
    - `TurnOrder.get_priority(action_type) -> int`

#### **Event & Status Processing**
- **`engine/systems/battle/event_processor.py`** (499 lines, 4 classes)
  - `EventType` - Battle event types enum
  - `BattleEvent` - Event data structure
  - `EventProcessor` - Event management
  - **Key Methods:**
    - `emit_event(event_type, data) -> None`
    - `process_events() -> List[BattleEvent]`
    - `add_event(event) -> None`

- **`engine/systems/battle/status_processor.py`** (288 lines, 2 classes)
  - `StatusProcessor` - Status effect management
  - **Key Methods:**
    - `apply_status(monster, status) -> bool`
    - `process_status_effects() -> None`
    - `remove_status(monster, status) -> bool`

#### **Battle AI & Validation**
- **`engine/systems/battle/battle_ai.py`** (339 lines, 3 classes)
  - `BattleAI` - Enemy AI system
  - `AIPersonality` - AI personality types
  - **Key Methods:**
    - `choose_action(battle_state) -> BattleAction`
    - `evaluate_moves(monster, target) -> List[float]`
    - `choose_switch(monster) -> Optional[MonsterInstance]`

- **`engine/systems/battle/battle_validation.py`** (347 lines, 1 class)
  - `BattleValidator` - Battle state validation
  - **Key Methods:**
    - `validate_battle_state(state) -> bool`
    - `validate_action(action) -> bool`
    - `validate_team(team) -> bool`

#### **DQM Integration & Specialized Systems**
- **`engine/systems/battle/meat_system.py`** (424 lines, 3 classes)
  - `MeatType` - Meat types enum
  - `MeatEffect` - Active meat effect
  - `MeatSystem` - DQM-style meat management
  - **Key Methods:**
    - `use_meat(meat_type) -> Tuple[bool, str]`
    - `get_taming_bonus() -> float`
    - `calculate_taming_chance(base_chance, hp_percent, rank, status) -> Dict`

- **`engine/systems/battle/dqm_integration.py`** (181 lines, 1 class)
  - `DQMIntegration` - DQM-specific mechanics
  - **Key Methods:**
    - `apply_dqm_rules(battle_state) -> None`
    - `calculate_dqm_damage(attacker, defender, move) -> int`

- **`engine/systems/battle/skills_dqm_integrated.py`** (303 lines, 6 classes)
  - DQM skill system integration
  - **Key Classes:**
    - `SkillType`, `SkillCategory`, `SkillEffect`
    - `SkillSystem`, `SkillValidator`, `SkillExecutor`

#### **Battle Effects & Rewards**
- **`engine/systems/battle/battle_effects.py`** (324 lines, 4 classes)
  - Battle visual and audio effects
  - **Key Classes:**
    - `BattleEffect`, `ScreenEffect`, `MonsterEffect`, `EffectManager`

- **`engine/systems/battle/reward_system.py`** (368 lines, 4 classes)
  - `RewardSystem` - Battle rewards management
  - `BattleRewards` - Reward data structure
  - **Key Methods:**
    - `calculate_rewards(battle_result) -> BattleRewards`
    - `distribute_exp(monsters, exp) -> None`
    - `generate_items(difficulty) -> List[str]`

#### **Battle Enums & Constants**
- **`engine/systems/battle/battle_enums.py`** (53 lines, 5 classes)
  - `BattleType` - Battle types (WILD, TRAINER, BOSS, STORY)
  - `BattlePhase` - Battle phases (INIT, START, INPUT, EXECUTION, AFTERMATH, END)
  - `BattleCommand` - Available commands
  - `AIPersonality` - AI personality types
  - `BattleResult` - Battle outcomes

---

## 🎨 **BATTLE UI SYSTEM (18 files)**

### **Core Battle UI**
- **`engine/ui/battle/battle_ui_core.py`** (586 lines, 1 class)
  - `BattleUI` - Main battle UI coordinator
  - **Key Methods:**
    - `__init__(game)`
    - `update(dt) -> None`
    - `draw(surface) -> None`
    - `handle_event(event) -> bool`
    - `set_battle_state(state) -> None`
    - `set_battle_controller(controller) -> None`

### **Modular UI Components**
- **`engine/ui/battle/battle_ui_state.py`** (312 lines, 4 classes)
  - `BattleMenuState` - Menu states enum
  - `BattleSprite` - Sprite data structure
  - `DamageNumber` - Damage number effect
  - `BattleUIState` - Complete UI state management
  - **Key States:**
    - `MAIN`, `MOVE_SELECT`, `ITEM_SELECT`, `SWITCH_SELECT`
    - `TAME_MEAT`, `TAME_CONFIRM`, `SCOUT`, `WAITING`, `MESSAGE`

- **`engine/ui/battle/battle_ui_renderer.py`** (517 lines, 1 class)
  - `BattleUIRenderer` - All rendering logic
  - **Key Methods:**
    - `draw_main_menu(surface) -> None`
    - `draw_move_menu(surface) -> None`
    - `draw_item_menu(surface) -> None`
    - `draw_switch_menu(surface) -> None`
    - `draw_monster_info(surface, monster, is_player) -> None`
    - `draw_hp_bars(surface) -> None`
    - `draw_damage_numbers(surface) -> None`

- **`engine/ui/battle/battle_ui_input.py`** (371 lines, 1 class)
  - `BattleUIInputHandler` - Input processing
  - **Key Methods:**
    - `handle_keyboard_input(event) -> bool`
    - `handle_main_menu_input(key) -> bool`
    - `handle_move_menu_input(key) -> bool`
    - `handle_item_menu_input(key) -> bool`
    - `handle_switch_menu_input(key) -> bool`

- **`engine/ui/battle/battle_ui_menus.py`** (258 lines, 1 class)
  - `BattleUIMenuManager` - Menu-specific logic
  - **Key Methods:**
    - `show_main_menu() -> None`
    - `show_move_menu() -> None`
    - `show_item_menu() -> None`
    - `show_switch_menu() -> None`
    - `navigate_menu(direction) -> None`

### **Specialized UI Components**
- **`engine/ui/taming_ui.py`** (485 lines, 3 classes)
  - `TamingUIState` - Taming UI states
  - `TamingAnimation` - Animation data
  - `TamingUI` - Complete taming interface
  - **Key Methods:**
    - `init_taming(meat_system, target_monster) -> None`
    - `show_meat_selection() -> None`
    - `show_taming_chance(base_chance) -> None`
    - `start_taming_animation() -> None`

- **`engine/ui/scout_display.py`** (555 lines, 3 classes)
  - `ScoutDisplayTab` - Analysis tabs
  - `MonsterAnalysis` - Analysis data
  - `ScoutDisplay` - Monster analysis display
  - **Key Methods:**
    - `show_monster_analysis(monster) -> None`
    - `_analyze_monster(monster) -> MonsterAnalysis`
    - `_calculate_type_effectiveness(monster) -> Dict`

- **`engine/ui/battle_rewards_ui.py`** (421 lines, 3 classes)
  - `RewardUIState` - Reward UI states
  - `RewardAnimation` - Animation data
  - `BattleRewardsUI` - Rewards display
  - **Key Methods:**
    - `show_rewards(rewards) -> None`
    - `update(dt) -> None`
    - `_setup_exp_animation(monster, exp_gained) -> None`

### **UI Utilities & Styling**
- **`engine/ui/battle_ui_utils.py`** (257 lines, 6 classes)
  - `BattleUIFontManager` - Font management (Singleton)
  - `BattleUITypeManager` - Type color management (Singleton)
  - `BattleUISpriteManager` - Sprite management (Singleton)
  - `BattleUIColorManager` - Color management (Singleton)
  - `BattleUITextUtils` - Text utilities
  - **Key Methods:**
    - `fonts.get_font(size) -> pygame.Font`
    - `types.get_type_color(type_name) -> Tuple[int, int, int]`
    - `sprites.get_monster_sprite(monster) -> pygame.Surface`
    - `colors.get_hp_color(hp_percent) -> Tuple[int, int, int]`

- **`engine/ui/battle_styles.py`** (198 lines, 3 classes)
  - `BattleStyle` - Style configuration
  - `BattleThemes` - Predefined themes
  - `StyleUtils` - Style utilities
  - **Key Methods:**
    - `BattleThemes.default() -> BattleStyle`
    - `StyleUtils.get_hp_color(hp_percent) -> Tuple[int, int, int]`

- **`engine/ui/battle_menu_transitions.py`** (187 lines, 3 classes)
  - `TransitionType` - Transition types
  - `MenuTransitionManager` - Transition management
  - `MenuEffectManager` - Visual effects
  - **Key Methods:**
    - `start_transition(from_state, to_state) -> None`
    - `update(dt) -> None`
    - `draw_transition(surface) -> None`

---

## ⚔️ **BATTLE SCENE SYSTEM**

### **Main Battle Scene**
- **`engine/scenes/battle_scene.py`** (717 lines, 2 classes)
  - `BattleScene` - Main battle scene
  - **Key Methods:**
    - `__init__(game)`
    - `on_enter() -> None`
    - `on_exit() -> None`
    - `update(dt) -> None`
    - `draw(surface) -> None`
    - `handle_event(event) -> bool`
    - `start_battle(player_team, enemy_team) -> None`

### **Battle Scene Components**
- **`engine/scenes/battle_scene_components.py`** (616 lines, 5 classes)
  - `BattleScenePhases` - Phase management
  - `BattleSceneEffects` - Visual effects
  - `BattleSceneInput` - Input handling
  - `BattleSceneActions` - Action processing
  - `BattleSceneIntegration` - System integration

---

## 🎯 **HAUPTMENÜ-OPTIONEN (Battle Main Menu)**

```
┌─────────────────────────────────────────────┐
│  Was soll [Monster Name] tun?               │
│                                              │
│  > ATTACKE     ITEM                         │
│    WECHSEL     ZÄHMEN                       │
│    SPÄHEN      FLUCHT                       │
└─────────────────────────────────────────────┘
```

### **Menu State Management**
- **File:** `engine/ui/battle/battle_ui_state.py`
- **Class:** `BattleMenuState` (Enum)
- **States:**
  - `MAIN` - Hauptmenü mit 6 Optionen
  - `MOVE_SELECT` - Move-Auswahl nach Kategorien
  - `ITEM_SELECT` - Item-Menü mit Kategorien
  - `SWITCH_SELECT` - Team-Wechsel
  - `TAME_MEAT` - Fleisch-Auswahl für Zähmen
  - `TAME_CONFIRM` - Zähm-Bestätigung mit Chancen
  - `SCOUT` - Monster-Analyse
  - `WAITING` - Warte auf Animation
  - `MESSAGE` - Zeige Nachricht

---

## ⚔️ **1. ATTACKE (Attack Menu)**

### **Move Selection System**
- **File:** `engine/ui/battle/battle_ui_menus.py`
- **Method:** `show_move_menu()`
- **Categories:**
  - **PHYSISCH** - Physical moves (uses ATK vs DEF)
  - **MAGISCH** - Magic moves (uses MAG vs RES)
  - **STATUS** - Support moves (buffs/debuffs/status)

### **Move Execution**
- **File:** `engine/systems/battle/action_processor.py`
- **Method:** `execute_move_action(action) -> Dict[str, Any]`
- **File:** `engine/systems/moves.py`
- **Class:** `MoveExecutor`
- **Method:** `execute(attacker, move, target, battle_state) -> Dict[str, Any]`

### **Damage Calculation**
- **File:** `engine/systems/unified_damage_calculator.py`
- **Class:** `UnifiedDamageCalculator` (Singleton)
- **Method:** `calculate_damage(attacker, defender, move, **kwargs) -> DamageResult`
- **DQM Formula:**
  ```python
  # Physical Damage
  damage = ((atk * 2 - def) * power / 50 + 2) * type_mult * random(0.85, 1.0)
  
  # Magic Damage  
  damage = ((mag * 2 - res) * power / 50 + 2) * type_mult * random(0.85, 1.0)
  ```

---

## 🍖 **2. ITEM (Item Menu)**

### **Item Selection System**
- **File:** `engine/ui/battle/battle_ui_menus.py`
- **Method:** `show_item_menu()`
- **Categories:**
  - **HEILUNG** - Healing items
  - **KAMPF-ITEMS** - Battle items (stat boosts)
  - **FLEISCH** - Meat for taming (DQM-style)

### **Meat System (DQM-Style)**
- **File:** `engine/systems/battle/meat_system.py`
- **Class:** `MeatSystem`
- **Key Methods:**
  - `use_meat(meat_type) -> Tuple[bool, str]`
  - `get_taming_bonus() -> float`
  - `calculate_taming_chance(base_chance, hp_percent, rank, status) -> Dict`
- **Meat Types:**
  - `NORMAL` - +20% taming chance, costs 50 gold
  - `SUPER` - +40% taming chance, costs 200 gold
  - `DIVINE` - +80% taming chance, costs 1000 gold

---

## 🔄 **3. WECHSEL (Switch Monster)**

### **Switch System**
- **File:** `engine/systems/battle/action_processor.py`
- **Method:** `execute_switch_action(action) -> Dict[str, Any]`
- **File:** `engine/ui/battle/battle_ui_menus.py`
- **Method:** `show_switch_menu()`

---

## 🥩 **4. ZÄHMEN (Taming) - DQM Style**

### **Taming UI System**
- **File:** `engine/ui/taming_ui.py`
- **Class:** `TamingUI`
- **Key Methods:**
  - `init_taming(meat_system, target_monster) -> None`
  - `show_meat_selection() -> None`
  - `show_taming_chance(base_chance) -> None`
  - `start_taming_animation() -> None`

### **Taming Formula (DQM-Style)**
```python
base_chance = 15  # Basis
hp_bonus = (1 - current_hp/max_hp) * 30  # 0-30%
meat_bonus = active_meat_effect  # 0/20/40/80%
rank_bonus = {
    "F": 10, "E": 5, "D": 0, "C": -5,
    "B": -10, "A": -15, "S": -20, "X": -30
}
status_bonus = {
    "sleep": 15, "paralysis": 10, "freeze": 10,
    "confusion": 5, "poison": 0
}
final_chance = min(95, base + hp + meat + rank + status)
```

---

## 🔍 **5. SPÄHEN (Scout/Analyze)**

### **Scout Display System**
- **File:** `engine/ui/scout_display.py`
- **Class:** `ScoutDisplay`
- **Key Methods:**
  - `show_monster_analysis(monster) -> None`
  - `_analyze_monster(monster) -> MonsterAnalysis`
  - `_calculate_type_effectiveness(monster) -> Dict`

---

## 🏃 **6. FLUCHT (Flee)**

### **Flee Calculation**
```python
flee_chance = (your_spd * 32) / (enemy_spd / 4) + 30 + (attempts * 30)
```

---

## ⚡ **BATTLE FLOW**

### **Turn Order System**
- **File:** `engine/systems/battle/turn_logic.py`
- **Class:** `TurnOrder`
- **Method:** `calculate_order(monsters) -> List[MonsterInstance]`
- **DQM Formula:**
  ```python
  initiative = monster.stats['spd'] + random.randint(0, 255)
  ```

### **Battle Phases**
- **File:** `engine/systems/battle/battle_enums.py`
- **Enum:** `BattlePhase`
- **Phases:**
  - `INIT` - Battle initialization
  - `START` - Battle start animations
  - `INPUT` - Player input phase
  - `EXECUTION` - Action execution
  - `AFTERMATH` - Status effects, level ups
  - `END` - Battle completion

---

## 📋 **TYPE CHART (12 Types)**

### **Type System**
- **File:** `engine/systems/types.py`
- **Class:** `TypeChart` (Singleton)
- **Key Methods:**
  - `get_effectiveness(attacking_type, defending_type) -> float`
  - `calculate_type_multiplier(attacking_type, defending_types) -> float`

### **Type Effectiveness**
```
Feuer → Pflanze (2x), Wasser (0.5x)
Wasser → Feuer (2x), Erde (2x)
Erde → Energie (2x), Luft (0.5x)
Luft → Erde (2x), Energie (0.5x)
Pflanze → Wasser (2x), Feuer (0.5x)
Bestie → Pflanze (2x), Erde (0.5x)
Energie → Wasser (2x), Erde (0.5x)
Chaos → Mystisch (2x), Ordnung (0.5x)
Seuche → Pflanze (2x), Feuer (0.5x)
Mystisch → Bestie (2x), Chaos (0.5x)
Gottheit → Teufel (2x), Gottheit (0.5x)
Teufel → Gottheit (2x), Teufel (0.5x)
```

---

## 🏆 **POST-BATTLE REWARDS**

### **Reward System**
- **File:** `engine/systems/battle/reward_system.py`
- **Class:** `RewardSystem`
- **Key Methods:**
  - `calculate_rewards(battle_result) -> BattleRewards`
  - `distribute_exp(monsters, exp) -> None`
  - `generate_items(difficulty) -> List[str]`

### **Rewards UI**
- **File:** `engine/ui/battle_rewards_ui.py`
- **Class:** `BattleRewardsUI`
- **Key Methods:**
  - `show_rewards(rewards) -> None`
  - `_setup_exp_animation(monster, exp_gained) -> None`

---

## 🤖 **AI SYSTEM**

### **Battle AI**
- **File:** `engine/systems/battle/battle_ai.py`
- **Class:** `BattleAI`
- **Key Methods:**
  - `choose_action(battle_state) -> BattleAction`
  - `evaluate_moves(monster, target) -> List[float]`
  - `choose_switch(monster) -> Optional[MonsterInstance]`

### **AI Personalities**
- **File:** `engine/systems/battle/battle_enums.py`
- **Enum:** `AIPersonality`
- **Types:**
  - `RANDOM` - Completely random moves
  - `BASIC` - Basic type effectiveness
  - `SMART` - Type + status consideration
  - `EXPERT` - Full heuristics + prediction
  - `PERFECT` - Optimal moves (boss battles only)

---

## 🔧 **KEY INTEGRATION POINTS**

### **Critical File Dependencies**
```yaml
battle_controller:
  needs: [turn_processor, action_processor, event_processor, status_processor]
  provides: [BattleController, battle coordination]
  
battle_scene:
  needs: [battle_controller, battle_ui, battle_rewards_ui]
  provides: [Scene management, event handling]
  
battle_ui:
  needs: [battle_controller state, ResourceManager]
  provides: [Visual interface, user input]
  
unified_damage_calculator:
  needs: [TypeChart, move data, monster stats]
  provides: [All damage calculations]
```

### **Main Workflow**
```
Game.run() → Scene.update() → BattleController.update()
BattleController → DamageCalculator → TypeChart
BattleScene → BattleUI → ResourceManager
MeatSystem → ItemSystem → BattleController
```

---

## 📊 **PERFORMANCE & OPTIMIZATION**

### **Singleton Patterns**
- `UnifiedDamageCalculator` - Single damage calculation instance
- `TypeChart` - Single type effectiveness instance
- `BattleUIFontManager` - Single font management instance
- `BattleUITypeManager` - Single type color management instance

### **Caching Systems**
- Type effectiveness caching in `TypeChart`
- Sprite caching in `BattleUISpriteManager`
- Font caching in `BattleUIFontManager`

---

## 🎮 **DEVELOPMENT GUIDELINES**

### **Adding New Battle Features**
1. **New Moves:** Add to `data/moves.json`, update `MoveRegistry`
2. **New Monsters:** Add to `data/monsters.json`, update `MonsterDatabase`
3. **New UI Elements:** Extend `BattleUIRenderer` and `BattleUIState`
4. **New Battle Effects:** Add to `BattleEffects` system

### **Testing Checklist**
- Can start battle without errors?
- Can execute basic attack?
- Can switch monsters?
- Can use items?
- Can tame monsters with meat?
- Battle ends correctly on victory/defeat?
- No memory leaks (scenes properly removed)?

---

*"So Junge, jetzt haste alles wat de brauchst für'n ordentliches Battle-System! Besser als die ganzen Pokémon-Klone, wa?" - Entwickler-Notiz*

**Letzte Aktualisierung:** 2025-09-06
**Version:** 6.0
**Dateien:** 45 Battle-System-Dateien, 18 UI-Dateien
**Gesamtzeilen:** 13,822 Battle-System + 3,500 UI-System
