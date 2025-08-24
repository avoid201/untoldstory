"""
Beispiele für die Verwendung des Item-Systems in Untold Story.
Demonstriert alle Hauptfunktionen und Integrationsmöglichkeiten.
"""

from engine.systems.items import (
    ItemRegistry, Inventory, ItemCategory, ItemRarity, 
    ItemTarget, EffectType, ItemEffect, Item
)
from engine.systems.monster_instance import MonsterInstance
from engine.systems.party import Party


def basic_item_usage_example():
    """Grundlegende Item-Verwendung demonstrieren."""
    print("=== Grundlegende Item-Verwendung ===")
    
    # ItemRegistry initialisieren
    registry = ItemRegistry()
    
    # Item abrufen
    potion = registry.get_item('trank')
    if potion:
        print(f"Item gefunden: {potion.name}")
        print(f"Beschreibung: {potion.description}")
        print(f"Kategorie: {potion.category.name}")
        print(f"Seltenheit: {potion.rarity.name}")
        print(f"Preis: {potion.price} Münzen")
        print(f"Kann im Kampf verwendet werden: {potion.use_in_battle}")
        print(f"Kann im Feld verwendet werden: {potion.use_in_field}")
        print(f"Verbrauchbar: {potion.consumable}")
        print()


def inventory_management_example():
    """Inventar-Verwaltung demonstrieren."""
    print("=== Inventar-Verwaltung ===")
    
    # Inventar erstellen
    inventory = Inventory()
    
    # Items hinzufügen
    print("Items zum Inventar hinzufügen...")
    inventory.add_item('trank', 5)
    inventory.add_item('supertrank', 3)
    inventory.add_item('gegengift', 2)
    inventory.add_item('fleisch', 10)
    
    # Inventar anzeigen
    print("Aktuelles Inventar:")
    for item_id, quantity in inventory.get_all_items():
        item = inventory.item_registry.get_item(item_id)
        if item:
            print(f"  {item.name}: {quantity}x")
    
    print(f"Geld: {inventory.money} Münzen")
    print(f"Inventar-Wert: {inventory.get_inventory_value()} Münzen")
    print()


def item_categorization_example():
    """Item-Kategorisierung demonstrieren."""
    print("=== Item-Kategorisierung ===")
    
    registry = ItemRegistry()
    
    # Items nach Kategorie gruppieren
    categories = [
        ItemCategory.HEALING,
        ItemCategory.STATUS,
        ItemCategory.TAMING,
        ItemCategory.BATTLE,
        ItemCategory.SPECIAL
    ]
    
    for category in categories:
        items = registry.get_items_by_category(category)
        print(f"{category.name} Items ({len(items)}):")
        for item in items[:3]:  # Zeige nur die ersten 3
            print(f"  - {item.name} ({item.rarity.name})")
        if len(items) > 3:
            print(f"  ... und {len(items) - 3} weitere")
        print()


def rarity_system_example():
    """Rarity-System demonstrieren."""
    print("=== Rarity-System ===")
    
    registry = ItemRegistry()
    
    rarities = [
        ItemRarity.COMMON,
        ItemRarity.UNCOMMON,
        ItemRarity.RARE,
        ItemRarity.EPIC,
        ItemRarity.LEGENDARY
    ]
    
    for rarity in rarities:
        items = registry.get_items_by_rarity(rarity)
        print(f"{rarity.name} Items ({len(items)}):")
        for item in items[:2]:  # Zeige nur die ersten 2
            print(f"  - {item.name}: {item.price} Münzen")
        if len(items) > 2:
            print(f"  ... und {len(items) - 2} weitere")
        print()


def item_validation_example():
    """Item-Validierung demonstrieren."""
    print("=== Item-Validierung ===")
    
    inventory = Inventory()
    registry = ItemRegistry()
    
    # Test-Items hinzufügen
    inventory.add_item('trank', 1)
    inventory.add_item('x_angriff', 1)
    inventory.add_item('fluchtseil', 1)
    
    test_scenarios = [
        ('trank', True, False),      # Healing Item - kann im Kampf und Feld
        ('x_angriff', True, False),  # Battle Item - nur im Kampf
        ('fluchtseil', False, True), # Special Item - nur im Feld
        ('nonexistent', False, False) # Nicht existierendes Item
    ]
    
    for item_id, can_use_in_battle, can_use_in_field in test_scenarios:
        print(f"Item: {item_id}")
        print(f"  Verfügbar: {inventory.has_item(item_id)}")
        print(f"  Kann im Kampf verwendet werden: {inventory.can_use_item(item_id, in_battle=True)}")
        print(f"  Kann im Feld verwendet werden: {inventory.can_use_item(item_id, in_battle=False)}")
        
        if item_id != 'nonexistent':
            item = registry.get_item(item_id)
            if item:
                print(f"  Ziel-Typ: {item.target.name}")
                print(f"  Verbrauchbar: {item.consumable}")
        print()


def item_effects_example():
    """Item-Effekte demonstrieren."""
    print("=== Item-Effekte ===")
    
    registry = ItemRegistry()
    
    # Verschiedene Item-Typen mit ihren Effekten
    effect_items = [
        'trank',           # HEAL_HP
        'gegengift',       # HEAL_STATUS
        'totalheilung',    # HEAL_ALL_STATUS
        'wiederbelebung',  # REVIVE
        'x_angriff',       # BUFF_STAT
        'fleisch',         # TAMING_BONUS
        'seltene_suessigkeit', # LEVEL_UP
        'aether'           # RESTORE_PP
    ]
    
    for item_id in effect_items:
        item = registry.get_item(item_id)
        if item:
            print(f"{item.name}:")
            for effect in item.effects:
                print(f"  Effekt: {effect.effect_type.name}")
                print(f"  Wert: {effect.value}")
                print(f"  Chance: {effect.chance * 100}%")
                print(f"  Ziel: {effect.target_type.name}")
            print()


def custom_item_creation_example():
    """Custom Item-Erstellung demonstrieren."""
    print("=== Custom Item-Erstellung ===")
    
    # Neues Custom Item erstellen
    custom_potion = Item(
        id='custom_potion',
        name='Custom Trank',
        description='Ein spezieller Trank mit einzigartigen Eigenschaften',
        category=ItemCategory.HEALING,
        rarity=ItemRarity.RARE,
        target=ItemTarget.SINGLE_ALLY,
        price=1500,
        sell_price=750,
        use_in_battle=True,
        use_in_field=True,
        consumable=True,
        stack_size=50,
        sprite_index=100,
        flavor_text='Ein mystischer Trank aus alten Rezepten',
        unlock_level=12,
        effects=[
            ItemEffect(EffectType.HEAL_HP, 75),
            ItemEffect(EffectType.HEAL_STATUS, 'poison', chance=0.8)
        ]
    )
    
    print("Custom Item erstellt:")
    print(f"  ID: {custom_potion.id}")
    print(f"  Name: {custom_potion.name}")
    print(f"  Kategorie: {custom_potion.category.name}")
    print(f"  Seltenheit: {custom_potion.rarity.name}")
    print(f"  Preis: {custom_potion.price} Münzen")
    print(f"  Freischalt-Level: {custom_potion.unlock_level}")
    print(f"  Effekte: {len(custom_potion.effects)}")
    
    for i, effect in enumerate(custom_potion.effects):
        print(f"    Effekt {i+1}: {effect.effect_type.name} - {effect.value}")
    
    print()


def search_and_filter_example():
    """Such- und Filterfunktionen demonstrieren."""
    print("=== Such- und Filterfunktionen ===")
    
    registry = ItemRegistry()
    
    # Nach Text suchen
    search_queries = ['trank', 'fleisch', 'angriff', 'heilt']
    
    for query in search_queries:
        results = registry.search_items(query)
        print(f"Suche nach '{query}': {len(results)} Ergebnisse")
        for item in results[:3]:  # Zeige nur die ersten 3
            print(f"  - {item.name}: {item.description[:50]}...")
        if len(results) > 3:
            print(f"    ... und {len(results) - 3} weitere")
        print()
    
    # Nach Ziel-Typ filtern
    target_types = [
        ItemTarget.SINGLE_ALLY,
        ItemTarget.SINGLE_ENEMY,
        ItemTarget.NONE
    ]
    
    for target_type in target_types:
        items = registry.get_items_by_target(target_type)
        print(f"Items mit Ziel {target_type.name}: {len(items)}")
        for item in items[:2]:  # Zeige nur die ersten 2
            print(f"  - {item.name}")
        if len(items) > 2:
            print(f"    ... und {len(items) - 2} weitere")
        print()


def battle_integration_example():
    """Battle-Integration demonstrieren."""
    print("=== Battle-Integration ===")
    
    from engine.systems.battle.battle_effects import EffectExecutor
    
    # EffectExecutor initialisieren (ohne echte Battle-Instanz)
    effect_executor = EffectExecutor()
    
    registry = ItemRegistry()
    
    # Battle-Items finden
    battle_items = registry.get_items_by_category(ItemCategory.BATTLE)
    
    print(f"Battle-Items gefunden: {len(battle_items)}")
    for item in battle_items:
        print(f"  {item.name}:")
        print(f"    Kann im Kampf verwendet werden: {item.use_in_battle}")
        print(f"    Kann im Feld verwendet werden: {item.use_in_field}")
        print(f"    Ziel: {item.target.name}")
        
        # Effekte anzeigen
        for effect in item.effects:
            print(f"    Effekt: {effect.effect_type.name} - {effect.value}")
        print()


def taming_integration_example():
    """Taming-Integration demonstrieren."""
    print("=== Taming-Integration ===")
    
    registry = ItemRegistry()
    
    # Taming-Items finden
    taming_items = registry.get_items_by_category(ItemCategory.TAMING)
    
    print(f"Taming-Items gefunden: {len(taming_items)}")
    for item in taming_items:
        print(f"  {item.name}:")
        print(f"    Preis: {item.price} Münzen")
        print(f"    Seltenheit: {item.rarity.name}")
        print(f"    Ziel: {item.target.name}")
        
        # Taming-Bonus anzeigen
        for effect in item.effects:
            if effect.effect_type == EffectType.TAMING_BONUS:
                print(f"    Taming-Bonus: {effect.value}x")
        print()


def save_load_compatibility_example():
    """Save/Load-Kompatibilität demonstrieren."""
    print("=== Save/Load-Kompatibilität ===")
    
    # Inventar mit Items erstellen
    inventory = Inventory()
    inventory.add_item('trank', 5)
    inventory.add_item('supertrank', 3)
    inventory.add_money(5000)
    inventory.add_key_item('map')
    
    # Zu Dictionary konvertieren (für Speichern)
    save_data = inventory.to_dict()
    print("Inventar-Daten für Speichern:")
    print(f"  Items: {save_data['items']}")
    print(f"  Key Items: {save_data['key_items']}")
    print(f"  Geld: {save_data['money']}")
    
    # Neues Inventar aus Dictionary erstellen (für Laden)
    loaded_inventory = Inventory.from_dict(save_data)
    print("\nGeladenes Inventar:")
    print(f"  Items: {loaded_inventory.get_all_items()}")
    print(f"  Key Items: {loaded_inventory.key_items}")
    print(f"  Geld: {loaded_inventory.money}")
    
    # Verifizierung
    print(f"\nVerifizierung:")
    print(f"  Items identisch: {inventory.items == loaded_inventory.items}")
    print(f"  Key Items identisch: {inventory.key_items == loaded_inventory.key_items}")
    print(f"  Geld identisch: {inventory.money == loaded_inventory.money}")


def main():
    """Alle Beispiele ausführen."""
    print("Untold Story - Item-System Beispiele")
    print("=" * 50)
    print()
    
    try:
        basic_item_usage_example()
        inventory_management_example()
        item_categorization_example()
        rarity_system_example()
        item_validation_example()
        item_effects_example()
        custom_item_creation_example()
        search_and_filter_example()
        battle_integration_example()
        taming_integration_example()
        save_load_compatibility_example()
        
        print("Alle Beispiele erfolgreich ausgeführt!")
        
    except Exception as e:
        print(f"Fehler beim Ausführen der Beispiele: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
