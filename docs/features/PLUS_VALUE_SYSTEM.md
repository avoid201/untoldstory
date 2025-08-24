# 🎮 Plus-Value System - Untold Story RPG

## Übersicht
Das Plus-Value-System ist ein fortschrittliches Charakterentwicklungs-System, das Monster über das normale Level-100 hinaus stärker macht. Es ist inspiriert von Dragon Quest Monsters und bietet eine tiefere Progression.

## Funktionsweise

### Plus-Value Bereiche
- **Bereich**: 0 bis 99
- **Standard**: Alle Monster starten mit +0
- **Maximum**: +99 (höchste Stufe)

### Level-Cap Erhöhung
- **Basis**: Level 100 (Standard)
- **Bonus**: +5 Level pro +10 Plus-Value
- **Beispiele**:
  - +0: Max Level 100
  - +10: Max Level 105
  - +20: Max Level 110
  - +50: Max Level 125
  - +99: Max Level 149

### Stat-Verbesserungen

#### HP-Bonus (Flacher Bonus)
- **Formel**: +2 HP pro +10 Plus-Value
- **Beispiele**:
  - +10: +2 HP
  - +20: +4 HP
  - +50: +10 HP

#### Andere Stats (Prozentualer Bonus)
- **Formel**: +3% pro +10 Plus-Value
- **Beispiele**:
  - +10: +3% ATK/DEF/MAG/RES/SPD
  - +20: +6% ATK/DEF/MAG/RES/SPD
  - +50: +15% ATK/DEF/MAG/RES/SPD

## Automatische Plus-Value-Erhöhung

### Level-basierte Erhöhung
- **Trigger**: Alle 10 Level (10, 20, 30, 40, ...)
- **Bedingung**: Plus-Value < 99
- **Erhöhung**: +1 Plus-Value

### Beispiel-Level-Up
```
Level 9 → 10: +0 → +1 (erste Erhöhung)
Level 19 → 20: +1 → +2
Level 29 → 30: +2 → +3
...
Level 99 → 100: +9 → +10
```

## Technische Implementierung

### Neue Eigenschaften
```python
@property
def max_level(self) -> int:
    """Maximales Level basierend auf Plus-Value"""
    
@property
def plus_value_display(self) -> str:
    """Plus-Value als Anzeigestring (z.B. '+15')"""
```

### Neue Methoden
```python
def increase_plus_value(self, amount: int = 1) -> bool:
    """Plus-Value erhöhen"""
    
def decrease_plus_value(self, amount: int = 1) -> bool:
    """Plus-Value verringern"""
    
def calculate_stats(self) -> Dict[str, int]:
    """Stats mit Plus-Value-Boni berechnen"""
```

### Erweiterte gain_exp() Methode
```python
def gain_exp(self, amount: int) -> Dict[str, Any]:
    """Erfahrung gewinnen mit Plus-Value-Integration"""
    # Rückgabewerte:
    # - plus_value_increased: True wenn Plus-Value erhöht wurde
    # - max_level_reached: True wenn Level-Cap erreicht wurde
```

## Beispielcode

### Monster mit Plus-Value erstellen
```python
# Standard Monster
monster = MonsterInstance(species, level=50)

# Monster mit Plus-Value
power_monster = MonsterInstance(species, level=50, plus_value=25)

# Plus-Value manuell erhöhen
monster.increase_plus_value(5)  # +5
monster.decrease_plus_value(2)  # -2
```

### Plus-Value-Status abfragen
```python
# Maximales Level
max_level = monster.max_level  # z.B. 112 bei +24

# Plus-Value anzeigen
display = monster.plus_value_display  # z.B. "+24"

# Aktuelle Plus-Value
current = monster.plus_value  # z.B. 24
```

### Level-Up mit Plus-Value
```python
# Erfahrung gewinnen
result = monster.gain_exp(1000)

if result["plus_value_increased"]:
    print(f"Plus-Value erhöht auf +{monster.plus_value}!")

if result["max_level_reached"]:
    print(f"Maximales Level {monster.max_level} erreicht!")
```

## Speichern und Laden

### Kompatibilität
- **Neue Speicherdateien**: Enthalten `plus_value` Feld
- **Alte Speicherdateien**: Plus-Value wird auf 0 gesetzt
- **Rückwärtskompatibel**: Keine Datenverluste

### Speicherformat
```json
{
    "species_id": 1,
    "level": 85,
    "plus_value": 15,
    "exp": 45000,
    "ivs": {...},
    "evs": {...}
}
```

## Strategische Überlegungen

### Wann Plus-Value nutzen?
- **Frühe Spielphase**: Fokus auf Level, Plus-Value kommt später
- **Mittlere Spielphase**: Plus-Value für Lieblingsmonster
- **Späte Spielphase**: Maximale Plus-Value für Endgame-Team

### Plus-Value vs. Level
- **Plus-Value**: Langfristige Investition, permanente Boni
- **Level**: Sofortige Verbesserungen, temporär bis Level-Cap
- **Kombination**: Beide Systeme ergänzen sich optimal

## Debugging und Entwicklung

### Debug-Ausgabe
```python
print(monster)  # MonsterInstance(species=Schlamm, level=50, plus_value=15, hp=120/120)
```

### Plus-Value-Validierung
```python
# Plus-Value wird automatisch auf 0-99 begrenzt
monster.plus_value = 150  # Wird zu 99
monster.plus_value = -10  # Wird zu 0
```

### Stat-Berechnung überprüfen
```python
# Stats neu berechnen
monster.stats = monster.calculate_stats()

# Plus-Value-Boni anzeigen
bonus = monster._calculate_plus_value_bonus()
print(f"HP Bonus: +{bonus['hp']}")
print(f"ATK Bonus: +{bonus['atk']}%")
```

## Zukünftige Erweiterungen

### Geplante Features
- **Plus-Value-Items**: Spezielle Items zur Erhöhung
- **Plus-Value-Synthesis**: Kombination von Plus-Values
- **Plus-Value-Reset**: Zurücksetzen für andere Monster
- **Plus-Value-Trading**: Tausch zwischen Spielern

### Balance-Anpassungen
- **Plus-Value-Kosten**: Höhere Kosten für höhere Werte
- **Plus-Value-Limits**: Spezielle Limits für bestimmte Monster
- **Plus-Value-Bedingungen**: Spezielle Bedingungen für Erhöhung
