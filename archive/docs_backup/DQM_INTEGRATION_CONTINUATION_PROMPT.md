# 🎮 FORTSETZUNG: Dragon Quest Monsters Battle System Integration - Phase 3-5

## 📋 ZUSAMMENFASSUNG DES BISHERIGEN FORTSCHRITTS

### ✅ Phase 1: DQM-Formeln (ABGESCHLOSSEN)
- **Implementierte Dateien:**
  - `engine/systems/battle/dqm_formulas.py` - Authentische DQM-Schadensberechnung
  - `engine/systems/battle/dqm_integration.py` - Nahtlose Integration
- **Features:**
  - DQM Schadensformel (ATK/2, DEF/4)
  - Critical Rate 1/32 (statt 1/16)
  - Damage Range 7/8 bis 9/8
  - Turn Order: Agility + Random(0-255)
  - Tension-System (1.0x bis 2.5x Multiplier)

### ✅ Phase 2: Event-System (ABGESCHLOSSEN)
- **Implementierte Dateien:**
  - `engine/systems/battle/battle_events.py` - Generator-basiertes Event-System
  - Modifiziert: `battle_controller.py` - Event-Integration
- **Features:**
  - 30+ Event-Typen
  - Yield-basierte Battle-Flows
  - Event-Queue mit Prioritäten
  - UI-Handler-Registrierung

## 🎯 NOCH ZU IMPLEMENTIEREN: PHASE 3-5

### 📌 PHASE 3: 3v3 Party Battle System [PRIORITÄT: HOCH]

**Ziel:** Implementiere Multi-Monster-Kämpfe wie in Dragon Quest Monsters

**Zu modifizierende Dateien:**
- `engine/systems/battle/battle_controller.py`
- `engine/systems/battle/battle_actions.py` 
- `engine/systems/battle/turn_logic.py`

**Neue Dateien zu erstellen:**
- `engine/systems/battle/battle_formation.py` - Formations-System
- `engine/systems/battle/target_system.py` - Multi-Target-Auswahl

**Referenz-Code aus Tuxemon** (https://github.com/Tuxemon/Tuxemon):
```python
# Von tuxemon/core/combat.py
class CombatState:
    def __init__(self):
        self.active_monsters = {
            'player': [],  # Bis zu 3 aktive Monster
            'opponent': []  # Bis zu 3 aktive Monster
        }
        self.bench_monsters = {
            'player': [],  # Reserve (Slot 4-6)
            'opponent': []  # Reserve
        }
    
    def get_combat_order(self):
        """Speed-basierte Turn Order für alle aktiven Monster"""
        all_active = (
            self.active_monsters['player'] + 
            self.active_monsters['opponent']
        )
        return sorted(all_active, 
                     key=lambda m: m.speed_stat, 
                     reverse=True)
    
    def execute_area_technique(self, user, technique):
        """Gruppen-Angriffe für 3v3"""
        if technique.target == 'all_foes':
            targets = self.active_monsters['opponent']
        elif technique.target == 'all_allies':
            targets = self.active_monsters['player']
            
        for target in targets:
            damage = self.calculate_damage(user, target, technique)
            target.current_hp -= damage
```

**Implementierungs-Details:**
1. Erweitere `BattleState` für multiple aktive Monster
2. Füge Formation-Positionen hinzu (Front/Back Row)
3. Implementiere Target-Typen:
   - Single Target
   - All Enemies
   - All Allies
   - Row Target
   - Random Targets
4. Area-Attack-Damage-Reduktion (75% für Seiten-Targets)
5. Switch-Mechanik zwischen aktiven und Bank-Monstern

### 📌 PHASE 4: DQM Skill System [PRIORITÄT: MITTEL]

**Ziel:** Implementiere das DQM Skill-Familie-System

**Neue Datei zu erstellen:**
- `engine/systems/battle/skills_dqm.py`
- `data/skills_dqm.json`

**Skill-Familien aus DQMonstersDB-API** (https://dqmonstersdb-api-743047725852.us-central1.run.app/docs):
```python
DQM_SKILL_FAMILIES = {
    # Feuer-Familie
    "Frizz": {"power": 10, "mp": 2, "element": "fire", "tier": 1},
    "Frizzle": {"power": 20, "mp": 4, "element": "fire", "tier": 2},
    "Kafrizz": {"power": 40, "mp": 8, "element": "fire", "tier": 3},
    "Kazfrizzle": {"power": 80, "mp": 16, "element": "fire", "tier": 4},
    
    # Eis-Familie
    "Crack": {"power": 12, "mp": 3, "element": "ice", "tier": 1},
    "Crackle": {"power": 25, "mp": 5, "element": "ice", "tier": 2},
    "Kacrack": {"power": 50, "mp": 10, "element": "ice", "tier": 3},
    "Kacrackle": {"power": 100, "mp": 20, "element": "ice", "tier": 4},
    
    # Blitz-Familie
    "Zap": {"power": 15, "mp": 4, "element": "thunder", "tier": 1},
    "Zapple": {"power": 30, "mp": 7, "element": "thunder", "tier": 2},
    "Kazap": {"power": 60, "mp": 15, "element": "thunder", "tier": 3},
    "Kazapple": {"power": 120, "mp": 30, "element": "thunder", "tier": 4},
    
    # Wind-Familie
    "Woosh": {"power": 8, "mp": 2, "element": "wind", "tier": 1},
    "Swoosh": {"power": 18, "mp": 4, "element": "wind", "tier": 2},
    "Kaswoosh": {"power": 35, "mp": 8, "element": "wind", "tier": 3},
    "Kaswooshle": {"power": 70, "mp": 16, "element": "wind", "tier": 4},
    
    # Explosion-Familie
    "Bang": {"power": 15, "mp": 4, "element": "explosion", "tier": 1},
    "Boom": {"power": 30, "mp": 8, "element": "explosion", "tier": 2},
    "Kaboom": {"power": 60, "mp": 15, "element": "explosion", "tier": 3},
    "Kaboomle": {"power": 120, "mp": 30, "element": "explosion", "tier": 4},
    
    # Heilung
    "Heal": {"power": 30, "mp": 3, "type": "heal", "tier": 1},
    "Midheal": {"power": 75, "mp": 6, "type": "heal", "tier": 2},
    "Fullheal": {"power": 999, "mp": 12, "type": "heal", "tier": 3},
    "Omniheal": {"power": 999, "mp": 20, "type": "heal_all", "tier": 4},
    
    # Buffs
    "Buff": {"effect": "atk_up", "mp": 3, "tier": 1},
    "Kabuff": {"effect": "def_up", "mp": 3, "tier": 1},
    "Acceleratle": {"effect": "spd_up", "mp": 2, "tier": 1},
    "Magic Barrier": {"effect": "mag_def_up", "mp": 4, "tier": 2},
    
    # Debuffs
    "Sap": {"effect": "def_down", "mp": 3, "tier": 1},
    "Kasap": {"effect": "def_down_all", "mp": 6, "tier": 2},
    "Decelerate": {"effect": "spd_down", "mp": 3, "tier": 1}
}
```

**Implementierungs-Details:**
1. Skill-Upgrade-System (Frizz → Frizzle → Kafrizz)
2. MP-System Integration
3. Element-Resistenzen
4. Skill-Vererbung bei Synthesis
5. Skill-Kategorien: Attack, Heal, Buff, Debuff, Status

### 📌 PHASE 5: Monster Traits [PRIORITÄT: NIEDRIG]

**Ziel:** Implementiere DQM-spezifische Monster-Eigenschaften

**Neue Dateien:**
- `engine/systems/battle/monster_traits.py`
- `data/traits.json`

**Trait-Liste aus DQM:**
```python
DQM_TRAITS = {
    # Combat Traits
    "Metal Body": {
        "effect": "reduce_damage_to_1",
        "description": "Reduziert fast allen Schaden auf 0-1"
    },
    "Critical Master": {
        "effect": "double_crit_rate",
        "description": "Verdoppelt kritische Trefferchance"
    },
    "Early Bird": {
        "effect": "wake_faster",
        "description": "Wacht schneller aus Schlaf auf"
    },
    "Agility Boost": {
        "effect": "speed_multiply_1.2",
        "description": "+20% Geschwindigkeit"
    },
    "Attack Boost": {
        "effect": "atk_multiply_1.1",
        "description": "+10% Angriff"
    },
    
    # Resistance Traits
    "Fire Breath Guard": {
        "effect": "fire_resist_50",
        "description": "50% Feuer-Resistenz"
    },
    "Ice Breath Guard": {
        "effect": "ice_resist_50",
        "description": "50% Eis-Resistenz"
    },
    "Bang Ward": {
        "effect": "explosion_resist_50",
        "description": "50% Explosions-Resistenz"
    },
    
    # Special Traits
    "Psycho": {
        "effect": "random_action_25",
        "description": "25% Chance auf zufällige Aktion"
    },
    "Counter": {
        "effect": "counter_physical_25",
        "description": "25% Chance auf Konter bei physischen Angriffen"
    },
    "Magic Counter": {
        "effect": "counter_magic_25",
        "description": "25% Chance auf Magie-Reflektion"
    },
    "HP Regeneration": {
        "effect": "regen_hp_turn",
        "description": "Regeneriert HP jede Runde"
    },
    "MP Regeneration": {
        "effect": "regen_mp_turn",
        "description": "Regeneriert MP jede Runde"
    }
}
```

**Integration in damage_calc.py Pipeline:**
```python
class TraitStage(PipelineStage):
    def process(self, context):
        attacker = context['attacker']
        defender = context['defender']
        
        # Check defender traits
        if 'Metal Body' in defender.traits:
            context['result'].damage = min(1, context['result'].damage)
        
        if 'Fire Breath Guard' in defender.traits and context['move'].element == 'fire':
            context['result'].damage *= 0.5
            
        # Check attacker traits  
        if 'Critical Master' in attacker.traits:
            # Already handled in critical stage, but could modify here
            pass
            
        return context
```

## 📁 PROJEKT-STRUKTUR

**Aktueller Pfad:** `/Users/leon/Desktop/untold_story/`

**Bereits implementierte Battle-System-Dateien:**
```
engine/systems/battle/
├── battle_controller.py    # Hauptkoordinator (modifiziert für Events)
├── battle_actions.py       # Action-Ausführung
├── battle_enums.py        # Enumerationen
├── battle_ai.py           # KI-System
├── battle_tension.py      # Tension-System
├── battle_validation.py  # Validierung
├── damage_calc.py         # Schadensberechnung (mit DQM-Formeln)
├── turn_logic.py          # Runden-Logik (mit DQM Turn-Order)
├── dqm_formulas.py        # ✅ NEU: DQM-Formeln
├── dqm_integration.py     # ✅ NEU: DQM-Integration
├── battle_events.py       # ✅ NEU: Event-System
└── core/                  # Core-Verzeichnis (leer)
```

## 🛠️ TECHNISCHE ANFORDERUNGEN

- **Python:** 3.13.5
- **Pygame-CE:** 2.5+
- **Architektur:** Modulares System mit Pipeline-Pattern
- **Performance:** 60 FPS während Kämpfen
- **Lokalisierung:** Deutsche Meldungen mit Ruhrpott-Dialekt

## 🎯 IMPLEMENTIERUNGS-REIHENFOLGE

1. **PHASE 3 ZUERST:** 3v3 Party Battles sind essentiell für DQM-Feeling
2. **PHASE 4 DANN:** Skills machen Kämpfe interessanter
3. **PHASE 5 OPTIONAL:** Traits für mehr Tiefe

## 💡 WICHTIGE HINWEISE

- **Backward Compatibility:** Alle Änderungen müssen optional sein
- **Event-Integration:** Nutze das Event-System aus Phase 2 für alle neuen Features
- **DQM-Formeln:** Verwende die Formeln aus `dqm_formulas.py`
- **Testing:** Erstelle Tests für jede neue Komponente
- **Performance:** Multi-Monster darf FPS nicht unter 60 drücken

## 🔗 REFERENZ-REPOSITORIES

1. **SlimeBattleSystem:** https://github.com/Joshalexjacobs/SlimeBattleSystem
   - C#/Unity DQM-Battle-System
   - MIT Lizenz
   
2. **Tuxemon:** https://github.com/Tuxemon/Tuxemon
   - Python/Pygame Monster-Taming-Spiel
   - GPLv3 Lizenz
   
3. **MRPG:** https://github.com/olehermanse/mrpg
   - Python Event-basiertes RPG
   - MIT Lizenz
   
4. **PyRPG_Mini:** https://github.com/crawsome/PyRPG_Mini
   - Python OOP Battle-System
   - MIT Lizenz
   
5. **DQMonstersDB-API:** https://github.com/cmsato09/DQMonstersDB-API
   - DQM Datenbank und API
   - MIT Lizenz

## 📝 PROMPT FÜR NÄCHSTE SESSION

Verwende diesen Prompt für die Fortsetzung mit Phase 3:

---

**AUFGABE:** Setze die Dragon Quest Monsters Battle-System-Integration mit Phase 3 (3v3 Party Battles) fort.

**KONTEXT:** 
- Projekt-Pfad: `/Users/leon/Desktop/untold_story/`
- Phase 1 (DQM-Formeln) und Phase 2 (Event-System) sind bereits implementiert
- Alle Dateien in `engine/systems/battle/` sind vorhanden und funktionsfähig

**PHASE 3 ZIEL:** Implementiere ein 3v3 Party-Battle-System wie in Dragon Quest Monsters

**ZU IMPLEMENTIEREN:**
1. Erweitere `BattleState` für 3 aktive + 3 Bank-Monster pro Team
2. Erstelle `battle_formation.py` für Formations-Management
3. Erstelle `target_system.py` für Multi-Target-Auswahl
4. Modifiziere `battle_actions.py` für Area-Attacks
5. Integriere mit dem bestehenden Event-System

**NUTZE DEN CODE AUS:** Tuxemon's combat.py (siehe oben) als Referenz

**BEACHTE:**
- Verwende das Event-System aus `battle_events.py` für alle UI-Updates
- Nutze DQM-Formeln aus `dqm_formulas.py` für Berechnungen
- Stelle Backward-Compatibility sicher (1v1 muss weiter funktionieren)
- Deutsche Kampf-Meldungen mit Ruhrpott-Dialekt
- Performance: 60 FPS auch mit 6 Monstern

**BEGINNE MIT:** Der Erstellung von `battle_formation.py` für das Formations-System.

---

## ✅ BEREIT FÜR FORTSETZUNG

Dieser Prompt enthält alle notwendigen Informationen für die Fortsetzung der DQM-Integration mit Phase 3. Die nächste Session kann direkt mit der Implementierung des 3v3 Party-Battle-Systems beginnen.
