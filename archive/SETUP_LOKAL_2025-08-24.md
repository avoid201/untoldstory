# Battle System - Lokales Setup

## 🚀 Schnellstart

Das Battle System ist jetzt vollständig funktionsfähig und AI-robust! Hier ist die einfachste Art, es lokal zu verwenden:

### 1. Basis Setup

```bash
# 1. Repository klonen/herunterladen
git clone <dein-repo-url>
cd untold-story

# 2. Virtuelle Umgebung erstellen
python3 -m venv venv

# 3. Virtuelle Umgebung aktivieren
source venv/bin/activate  # Linux/Mac
# oder
venv\Scripts\activate     # Windows

# 4. Abhängigkeiten installieren
pip install pygame-ce
```

### 2. Schnelltest

```bash
# Einfachster Test
python local_test.py

# Umfassender Test
python simple_test.py

# Bei Problemen
python run_local.py
```

## 🛠️ Fehlerbehebung

### Problem: .pyc Dateien verursachen Import-Probleme

**Lösung:**
```bash
# Automatisches Cleanup
python run_local.py

# Oder manuell:
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +
```

### Problem: Import-Fehler

**Lösung:**
```bash
# 1. .pyc Dateien löschen (siehe oben)
# 2. Virtuelle Umgebung neu starten
deactivate
source venv/bin/activate
# 3. Test erneut ausführen
python local_test.py
```

### Problem: pygame-ce fehlt

**Lösung:**
```bash
pip install pygame-ce
```

## 📁 Wichtige Dateien

### Test-Skripte
- `local_test.py` - Einfacher, direkter Test
- `simple_test.py` - Umfassender Test mit allen Features
- `run_local.py` - Setup und Troubleshooting
- `test_final_battle_system.py` - Vollständiger Test aller AI-Fixes

### Battle System Dateien
- `engine/systems/battle/battle.py` - Haupt-Battle-System
- `engine/systems/battle/turn_logic.py` - Turn-Order und Actions
- `engine/systems/monster_instance.py` - Monster-System
- `engine/systems/moves.py` - Move-System
- `engine/systems/stats.py` - Stats und Experience

## 🎯 Features

### ✅ Behobene AI-Probleme

1. **Robuste Enum-Behandlung**
   - `ActionType.from_string()` für flexible String-Konvertierung
   - Automatische Groß-/Kleinschreibung-Behandlung
   - Fallback-Werte bei ungültigen Inputs

2. **Verbesserte Validierung**
   - Umfassende Input-Validierung
   - Graceful Degradation bei Fehlern
   - Detaillierte Fehlerprotokollierung

3. **Deterministische Tests**
   - RNG-Seed-System implementiert
   - Reproduzierbare Test-Ergebnisse
   - Konsistente Verhalten

4. **Robuste Action-Queue**
   - Dict-zu-BattleAction-Konvertierung
   - Flexible Action-Formate
   - Action-Integritätsprüfung

5. **Umfassende Fehlerbehandlung**
   - Try-catch um alle kritischen Operationen
   - Fallback-Mechanismen
   - Logging-System

## 🧪 Beispiel-Code

### Einfacher Battle Test

```python
from engine.systems.battle.battle import BattleState, BattleType
from engine.systems.monster_instance import MonsterInstance, MonsterSpecies, MonsterRank
from engine.systems.stats import BaseStats, GrowthCurve
from engine.systems.moves import Move, MoveEffect, EffectKind, MoveCategory, MoveTarget

# Monster erstellen
base_stats = BaseStats(hp=100, atk=50, def_=50, mag=30, res=30, spd=70)
species = MonsterSpecies(
    id=1, name="TestMonster", era="present", rank=MonsterRank.E,
    types=["Bestie"], base_stats=base_stats, growth_curve=GrowthCurve.MEDIUM_FAST,
    base_exp_yield=64, capture_rate=45, traits=[], learnset=[],
    evolution=None, description="Test Monster"
)

player = MonsterInstance(species=species, level=5)
enemy = MonsterInstance(species=species, level=5)

# Move erstellen
effect = MoveEffect(kind=EffectKind.DAMAGE, power=40, chance=100.0)
move = Move(
    id="tackle", name="Tackle", type="Bestie", category=MoveCategory.PHYSICAL,
    power=40, accuracy=95, pp=15, max_pp=15, priority=0,
    targeting=MoveTarget.ENEMY, effects=[effect], description="Basic attack"
)

player.moves = [move]
enemy.moves = [move]

# Battle starten
battle = BattleState(
    player_team=[player],
    enemy_team=[enemy],
    battle_type=BattleType.WILD
)

battle.start_battle()

# Action ausführen
action = {
    'action_type': 'attack',
    'actor': player,
    'move': player.moves[0],
    'target': enemy
}

battle.queue_player_action(action)
result = battle.resolve_turn()

print(f"Turn {result['turn_count']} abgeschlossen!")
print(f"Spieler HP: {player.current_hp}/{player.max_hp}")
print(f"Gegner HP: {enemy.current_hp}/{enemy.max_hp}")
```

## 🔄 AI-Robuste Features

### Flexible String-Inputs
```python
# Alle diese Formate funktionieren:
action = {'action_type': 'attack', ...}    # lowercase
action = {'action_type': 'ATTACK', ...}    # uppercase  
action = {'action_type': 'Attack', ...}    # mixed case
```

### Automatische Validierung
```python
# System validiert automatisch:
- Monster-Integrität
- Move-Verfügbarkeit
- Action-Gültigkeit
- Battle-Status
```

### Fehler-Resilience
```python
# System fängt ab:
- Ungültige Inputs
- Fehlende Attribute
- Corrupted States
- Import-Probleme
```

## 📞 Support

Bei Problemen:

1. **Erste Hilfe:** `python run_local.py`
2. **.pyc Cleanup:** `python run_local.py` (macht automatisches Cleanup)
3. **Test-Status:** `python simple_test.py`
4. **Debug-Info:** Alle Skripte haben detaillierte Fehlerausgaben

## 🎉 Erfolg!

Wenn `python local_test.py` mit "🎉 BATTLE SYSTEM FUNKTIONIERT!" endet, ist alles korrekt eingerichtet!

Das System ist jetzt:
- ✅ AI-robust
- ✅ Lokal funktionsfähig  
- ✅ Vollständig getestet
- ✅ Einfach zu verwenden
