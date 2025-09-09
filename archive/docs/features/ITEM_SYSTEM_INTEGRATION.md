# Item-System Integration Guide

## Übersicht

Das neue Item-System für Untold Story bietet eine umfassende Lösung für alle Item-bezogenen Funktionen im Spiel. Es ist vollständig mit dem bestehenden Battle-System, Taming-System und Save/Load-System kompatibel.

## Hauptkomponenten

### 1. ItemRegistry (Singleton)
- Zentrale Registrierung aller Items im Spiel
- Lädt Standard-Items beim Start
- Kann Items aus JSON-Dateien laden
- Bietet Such- und Filterfunktionen

### 2. ItemEffectExecutor
- Führt Item-Effekte aus
- Validiert Item-Verwendung
- Behandelt alle Item-Typen (Healing, Status, Taming, etc.)
- Integriert mit dem Battle-System

### 3. Inventory
- Verwaltet Spieler-Inventar
- Stapel-Management (bis zu 99 Items pro Stapel)
- Geld-Management
- Key-Item-Verwaltung

## Integration mit dem Battle-System

### Battle-Effects Integration

Das Item-System ist vollständig in `battle_effects.py` integriert:

```python
from engine.systems.battle.battle_effects import EffectExecutor

# In der Battle-Scene
effect_executor = EffectExecutor(battle)

# Item verwenden
messages = effect_executor.execute_item_effects(item, target_monster)
```

### Item-Verwendung im Kampf

```python
# Item aus Inventar verwenden
if inventory.can_use_item(item_id, in_battle=True):
    messages = inventory.use_item(
        item_id, 
        target=target_monster, 
        battle=current_battle,
        in_battle=True
    )
    # Messages an UI weiterleiten
```

## Integration mit dem Taming-System

### Taming-Items

Taming-Items sind speziell für das bestehende Taming-System konfiguriert:

```python
# Taming-Bonus anwenden
if item.category == ItemCategory.TAMING:
    taming_bonus = item.effects[0].value
    # Integration mit taming.py
    success_chance = calculate_tame_chance(
        target, player_team, battle_state, 
        item_used=item.id
    )
```

### Taming-Item-Typen

- **Fleisch**: 1.5x Taming-Bonus
- **Lecker Fleisch**: 2.0x Taming-Bonus  
- **Edelfleisch**: 3.0x Taming-Bonus
- **Goldfleisch**: 5.0x Taming-Bonus

## Item-Kategorien

### 1. Healing Items
- **Trank**: 20 KP
- **Supertrank**: 50 KP
- **Hypertrank**: 100 KP
- **Top-Trank**: 100% KP
- **Wiederbelebung**: 50% KP
- **Top-Wiederbelebung**: 100% KP

### 2. Status Items
- **Gegengift**: Heilt Vergiftung
- **Brandsalbe**: Heilt Verbrennung
- **Auftaumittel**: Heilt Einfrierung
- **Aufwecker**: Weckt auf
- **Anti-Paralyse**: Heilt Paralyse
- **Totalheilung**: Heilt alle Status

### 3. Taming Items
- **Fleisch**: Basis-Taming
- **Lecker Fleisch**: Verbessertes Taming
- **Edelfleisch**: Premium-Taming
- **Goldfleisch**: Legendäres Taming

### 4. Battle Items
- **X-Angriff**: +1 Angriff
- **X-Verteidigung**: +1 Verteidigung
- **X-Tempo**: +1 Initiative
- **X-Magie**: +1 Magie
- **X-Genauigkeit**: +1 Genauigkeit

### 5. Special Items
- **Seltene Süßigkeit**: Level +1
- **Äther**: 10 AP wiederherstellen
- **Top-Äther**: Alle AP wiederherstellen
- **Fluchtseil**: Aus Höhlen flüchten
- **Repel**: Monster fernhalten (100 Schritte)
- **Super-Repel**: Monster fernhalten (200 Schritte)

## Rarity-System

### Rarity-Levels
- **COMMON**: Einfach zu finden, niedriger Preis
- **UNCOMMON**: Mäßig selten, mittlerer Preis
- **RARE**: Selten, hoher Preis
- **EPIC**: Sehr selten, sehr hoher Preis
- **LEGENDARY**: Extrem selten, höchster Preis

### Rarity-Beispiele
```python
# Seltene Items finden
rare_items = item_registry.get_items_by_rarity(ItemRarity.RARE)
epic_items = item_registry.get_items_by_rarity(ItemRarity.EPIC)
```

## Verwendung im Code

### Item aus Registry holen
```python
from engine.systems.items import ItemRegistry

registry = ItemRegistry()
item = registry.get_item('trank')
```

### Inventar verwalten
```python
from engine.systems.items import Inventory

inventory = Inventory()
inventory.add_item('trank', 5)
inventory.remove_item('trank', 1)
```

### Item verwenden
```python
# Im Feld
messages = inventory.use_item('trank', target=monster, in_battle=False)

# Im Kampf
messages = inventory.use_item('x_angriff', target=monster, in_battle=True)
```

## Save/Load Integration

### Inventar speichern
```python
# In save.py
save_data['inventory'] = inventory.to_dict()
```

### Inventar laden
```python
# In save.py
inventory = Inventory.from_dict(save_data['inventory'])
```

## UI-Integration

### Item-Menü
```python
# Items nach Kategorie gruppieren
healing_items = inventory.get_items_by_category(ItemCategory.HEALING)
battle_items = inventory.get_items_by_category(ItemCategory.BATTLE)

# Items nach Seltenheit gruppieren
rare_items = inventory.get_items_by_rarity(ItemRarity.RARE)
```

### Item-Informationen anzeigen
```python
item = registry.get_item(item_id)
print(f"Name: {item.name}")
print(f"Beschreibung: {item.description}")
print(f"Kategorie: {item.category.name}")
print(f"Seltenheit: {item.rarity.name}")
print(f"Preis: {item.price} Münzen")
```

## Erweiterte Funktionen

### Custom Items hinzufügen
```python
# Neues Item registrieren
custom_item = Item(
    id='custom_potion',
    name='Custom Trank',
    description='Ein spezieller Trank',
    category=ItemCategory.HEALING,
    rarity=ItemRarity.RARE,
    target=ItemTarget.SINGLE_ALLY,
    price=1000,
    sell_price=500,
    use_in_battle=True,
    use_in_field=True,
    consumable=True,
    effects=[ItemEffect(EffectType.HEAL_HP, 75)]
)

registry.items['custom_potion'] = custom_item
```

### Item-Effekte erweitern
```python
# Neuen Effekt-Typ hinzufügen
class CustomEffect(ItemEffect):
    def __init__(self, custom_value: str):
        super().__init__(EffectType.CUSTOM, custom_value)
        self.custom_value = custom_value
```

## Debug-Features

### TAB-Taste Features
```python
# Debug-Informationen anzeigen
if keys[pygame.K_TAB]:
    # Alle Items anzeigen
    all_items = registry.get_all_items()
    for item_id, item in all_items.items():
        print(f"{item_id}: {item.name} ({item.rarity.name})")
    
    # Inventar-Wert berechnen
    total_value = inventory.get_inventory_value()
    print(f"Inventar-Wert: {total_value} Münzen")
```

## Performance-Optimierungen

### Caching
- ItemRegistry ist ein Singleton
- Items werden nur einmal geladen
- Effekt-Executor wird wiederverwendet

### Memory Management
- Items werden nur bei Bedarf geladen
- Unused Items können aus Memory entfernt werden
- Stack-basierte Inventar-Verwaltung

## Fehlerbehandlung

### Graceful Degradation
```python
try:
    item = registry.get_item(item_id)
    if item:
        # Item verwenden
        pass
    else:
        print(f"Item {item_id} nicht gefunden!")
except Exception as e:
    print(f"Fehler beim Laden des Items: {e}")
    # Fallback-Verhalten
```

### Item-Validierung
```python
# Item-Verwendung validieren
if not inventory.can_use_item(item_id, in_battle=True):
    print("Item kann nicht im Kampf verwendet werden!")
    return

# Ziel-Validierung
if not target_monster:
    print("Kein gültiges Ziel ausgewählt!")
    return
```

## Testing

### Unit Tests
```python
def test_item_registry():
    registry = ItemRegistry()
    assert registry.get_item('trank') is not None
    assert registry.get_item('nonexistent') is None

def test_inventory():
    inventory = Inventory()
    assert inventory.add_item('trank', 5) == True
    assert inventory.get_item_count('trank') == 5
```

### Integration Tests
```python
def test_item_usage_in_battle():
    # Test Item-Verwendung im Kampf
    pass

def test_item_usage_in_field():
    # Test Item-Verwendung im Feld
    pass
```

## Bekannte Einschränkungen

1. **Battle-Integration**: Items müssen explizit für Kampf-Verwendung markiert sein
2. **Taming-Integration**: Taming-Bonus wird nur bei wilden Monstern angewendet
3. **Status-Immunitäten**: Nur grundlegende Typ-basierte Immunitäten implementiert
4. **Animation-Flags**: Item-Verbrauch-Animationen müssen separat implementiert werden

## Zukünftige Erweiterungen

1. **Equipment-System**: Getragene Items für Monster
2. **Synthesis-Integration**: Item-Effekte für Monster-Fusion
3. **Quest-Items**: Spezielle Items für Story-Fortschritt
4. **Crafting-System**: Items herstellen aus Materialien
5. **Trading-System**: Items zwischen Spielern tauschen

## Support

Bei Fragen oder Problemen mit dem Item-System:

1. Überprüfe die Logs auf Fehlermeldungen
2. Validiere Item-Daten in der JSON-Datei
3. Teste Item-Verwendung im Debug-Modus (TAB-Taste)
4. Überprüfe Inventar-Status und Item-Verfügbarkeit

Das Item-System ist so konzipiert, dass es einfach erweitert und angepasst werden kann, ohne bestehende Funktionalität zu beeinträchtigen.
