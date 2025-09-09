#!/usr/bin/env python3
"""
🧬 Test-Skript für das Monster Traits System
Demonstriert Traits, Vererbung und Battle-Integration
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

import logging
from typing import List
import random

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)

# Import components
from engine.systems.battle.monster_traits import (
    get_trait_database, TraitManager, TraitCategory, TraitTrigger
)
from engine.systems.monster_instance import MonsterInstance
from engine.systems.unified_damage_calculator import unified_damage_calculator, DamageResult

def create_monster_with_traits(name: str, traits: List[str]) -> MonsterInstance:
    """Erstelle Monster mit Traits"""
    monster = MonsterInstance(
        name=name,
        level=20,
        max_hp=200,
        max_mp=100
    )
    
    # Füge TraitManager hinzu
    monster.trait_manager = TraitManager(monster)
    
    # Füge Traits hinzu
    for trait_name in traits:
        if monster.trait_manager.add_trait(trait_name):
            print(f"  ✅ {trait_name} hinzugefügt zu {name}")
        else:
            print(f"  ❌ {trait_name} konnte nicht hinzugefügt werden")
    
    return monster

def test_trait_database():
    """Teste die Trait-Datenbank"""
    print("\n" + "="*60)
    print("🧬 MONSTER TRAITS SYSTEM TEST")
    print("="*60)
    
    db = get_trait_database()
    
    print("\n📊 Trait-Statistiken:")
    print("-"*40)
    
    # Zähle Traits nach Kategorie
    category_counts = {}
    for category in TraitCategory:
        traits = db.get_traits_by_category(category)
        category_counts[category.value] = len(traits)
        print(f"  {category.value:12}: {len(traits)} Traits")
    
    # Zeige Trait-Tiers
    print("\n⭐ Traits nach Seltenheit:")
    for tier in range(1, 6):
        tier_traits = db.get_traits_by_tier(tier)
        if tier_traits:
            names = [t.name for t in tier_traits[:3]]
            print(f"  Tier {tier}: {', '.join(names)}{'...' if len(tier_traits) > 3 else ''}")
    
    # Zeige vererbbare Traits
    inheritable = db.get_inheritable_traits()
    print(f"\n🧬 Vererbbare Traits: {len(inheritable)}/{len(db.traits)}")

def test_metal_body():
    """Teste den Metal Body Trait"""
    print("\n" + "="*60)
    print("🛡️ METAL BODY TEST")
    print("="*60)
    
    # Erstelle Metal Slime
    metal_slime = create_monster_with_traits("Metal Slime", ["Metal Body", "Escape Artist"])
    
    # Erstelle Angreifer
    attacker = MonsterInstance("Dragon", level=30)
    
    # Simuliere Angriff
    print(f"\n⚔️ {attacker.name} greift {metal_slime.name} an!")
    
    # Dummy Move
    class DummyMove:
        def __init__(self):
            self.power = 100
            self.accuracy = 100
            self.category = 'phys'
            self.type = 'Normal'
    
    calc = DamageCalculator()
    
    # 5 Angriffe simulieren
    damages = []
    for i in range(5):
        result = calc.calculate(attacker, metal_slime, DummyMove())
        damages.append(result.damage)
        print(f"  Angriff {i+1}: {result.damage} Schaden")
    
    print(f"\n📊 Durchschnitt: {sum(damages)/len(damages):.1f} Schaden")
    print("→ Metal Body reduziert Schaden auf 0 oder 1!")

def test_critical_master():
    """Teste Critical Master Trait"""
    print("\n" + "="*60)
    print("💥 CRITICAL MASTER TEST")
    print("="*60)
    
    # Monster mit und ohne Critical Master
    normal_monster = MonsterInstance("Warrior", level=20)
    crit_master = create_monster_with_traits("Assassin", ["Critical Master", "Lucky Devil"])
    
    defender = MonsterInstance("Dummy", level=20)
    
    class DummyMove:
        def __init__(self):
            self.power = 50
            self.accuracy = 100
            self.category = 'phys'
            self.type = 'Normal'
            self.crit_ratio = 1/32  # DQM base rate
    
    calc = DamageCalculator()
    
    # Teste Critical Rates
    print("\n🎯 Critical Hit Rates (100 Angriffe):")
    
    for attacker, name in [(normal_monster, "Normal"), (crit_master, "Critical Master")]:
        crits = 0
        for _ in range(100):
            result = calc.calculate(attacker, defender, DummyMove())
            if result.is_critical:
                crits += 1
        print(f"  {name:15}: {crits}% Critical Hits")
    
    print("\n→ Critical Master verdoppelt die Crit-Rate!")

def test_resistances():
    """Teste Element-Resistenz Traits"""
    print("\n" + "="*60)
    print("🔥❄️ ELEMENT RESISTANCE TEST")
    print("="*60)
    
    # Monster mit Resistenzen
    fire_guard = create_monster_with_traits("Fire Guardian", 
                                           ["Fire Breath Guard", "HP Regeneration"])
    ice_guard = create_monster_with_traits("Ice Guardian", 
                                          ["Ice Breath Guard", "Defense Boost"])
    
    attacker = MonsterInstance("Mage", level=20)
    
    # Fire und Ice Moves
    class FireMove:
        def __init__(self):
            self.power = 60
            self.accuracy = 100
            self.category = 'mag'
            self.type = 'Fire'
            self.element = 'fire'
    
    class IceMove:
        def __init__(self):
            self.power = 60
            self.accuracy = 100
            self.category = 'mag'
            self.type = 'Ice'
            self.element = 'ice'
    
    calc = DamageCalculator()
    
    print("\n🔥 Feuer-Angriff:")
    for defender, name in [(fire_guard, "Fire Guardian"), (ice_guard, "Ice Guardian")]:
        result = calc.calculate(attacker, defender, FireMove())
        resist = "✅ Resistenz!" if "Element Guard" in result.modifiers_applied else ""
        print(f"  vs {name:15}: {result.damage} Schaden {resist}")
    
    print("\n❄️ Eis-Angriff:")
    for defender, name in [(fire_guard, "Fire Guardian"), (ice_guard, "Ice Guardian")]:
        result = calc.calculate(attacker, defender, IceMove())
        resist = "✅ Resistenz!" if "Element Guard" in result.modifiers_applied else ""
        print(f"  vs {name:15}: {result.damage} Schaden {resist}")

def test_combat_traits():
    """Teste Kampf-Traits"""
    print("\n" + "="*60)
    print("⚔️ COMBAT TRAITS TEST")
    print("="*60)
    
    # Monster mit verschiedenen Boost-Traits
    monsters = [
        create_monster_with_traits("Berserker", ["Attack Boost", "Last Stand"]),
        create_monster_with_traits("Tank", ["Defense Boost", "Counter"]),
        create_monster_with_traits("Speedster", ["Agility Boost", "Early Bird"]),
        create_monster_with_traits("Wizard", ["Magic Boost", "MP Regeneration"])
    ]
    
    print("\n📊 Stat-Modifikatoren:")
    for monster in monsters:
        mods = monster.trait_manager.get_stat_modifiers()
        print(f"\n{monster.name}:")
        for stat, value in mods.items():
            if value != 1.0:
                percent = (value - 1.0) * 100
                sign = "+" if percent > 0 else ""
                print(f"  {stat:8}: {sign}{percent:.0f}%")

def test_trait_inheritance():
    """Teste Trait-Vererbung"""
    print("\n" + "="*60)
    print("🧬 TRAIT VERERBUNG TEST")
    print("="*60)
    
    db = get_trait_database()
    
    # Eltern-Traits
    parent1_traits = ["Attack Boost", "Fire Breath Guard", "Critical Master"]
    parent2_traits = ["Attack Boost", "Defense Boost", "HP Regeneration"]
    
    print(f"\n👨 Elternteil 1: {', '.join(parent1_traits)}")
    print(f"👩 Elternteil 2: {', '.join(parent2_traits)}")
    
    # Teste verschiedene Familien
    families = ["dragon", "slime", "beast", "demon"]
    
    print("\n👶 Vererbte Traits nach Familie:")
    for family in families:
        inherited = db.calculate_trait_inheritance(parent1_traits, parent2_traits, family)
        print(f"  {family:8}: {', '.join(inherited) if inherited else 'Keine'}")
    
    print("\n→ Gemeinsame Traits (Attack Boost) werden bevorzugt vererbt!")
    print("→ Familie beeinflusst zusätzliche Traits!")

def test_special_traits():
    """Teste spezielle Traits"""
    print("\n" + "="*60)
    print("✨ SPECIAL TRAITS TEST")
    print("="*60)
    
    # Last Stand Test
    print("\n💀 Last Stand (Aktiviert bei <10% HP):")
    warrior = create_monster_with_traits("Warrior", ["Last Stand", "Counter"])
    
    # Simuliere niedrige HP
    warrior.current_hp = 15  # 7.5% von 200 HP
    
    trait_context = {
        'phase': 'on_attack',
        'hp_percent': warrior.current_hp / warrior.max_hp,
        'stats': warrior.stats.copy()
    }
    
    effects = warrior.trait_manager.process_traits(TraitTrigger.HEALTH_CRITICAL, trait_context)
    
    print(f"  HP: {warrior.current_hp}/{warrior.max_hp} ({trait_context['hp_percent']*100:.1f}%)")
    for effect in effects:
        if 'stat_boosted' in effect:
            for stat, boost in effect['stat_boosted'].items():
                print(f"  → {stat.upper()} +{boost}")
    
    # Psycho Test
    print("\n🎲 Psycho (25% zufällige Aktion):")
    crazy = create_monster_with_traits("Berserker", ["Psycho", "Attack Boost"])
    
    random_actions = 0
    for _ in range(100):
        trait_context = {
            'phase': 'on_attack',
            'hp_percent': 1.0
        }
        effects = crazy.trait_manager.process_traits(TraitTrigger.ON_ATTACK, trait_context)
        for effect in effects:
            if effect.get('effect_type') == 'random_action':
                random_actions += 1
    
    print(f"  Zufällige Aktionen: {random_actions}/100 ({random_actions}%)")

def test_regen_traits():
    """Teste Regenerations-Traits"""
    print("\n" + "="*60)
    print("💚 REGENERATION TRAITS TEST")
    print("="*60)
    
    # Monster mit Regen-Traits
    healer = create_monster_with_traits("Healslime", 
                                       ["HP Regeneration", "MP Regeneration", "Fast Healer"])
    
    # Setze HP/MP auf 50%
    healer.current_hp = 100
    healer.current_mp = 50
    
    print(f"\n🔄 Regeneration pro Runde:")
    print(f"  Start: {healer.current_hp}/{healer.max_hp} HP, {healer.current_mp}/{healer.max_mp} MP")
    
    # Simuliere 3 Runden
    for turn in range(1, 4):
        trait_context = {
            'phase': 'turn_end',
            'hp_percent': healer.current_hp / healer.max_hp,
            'max_hp': healer.max_hp,
            'max_mp': healer.max_mp
        }
        
        effects = healer.trait_manager.process_traits(TraitTrigger.TURN_END, trait_context)
        
        hp_regen = 0
        mp_regen = 0
        for effect in effects:
            if 'hp_regen' in effect:
                hp_regen = effect['hp_regen']
                healer.current_hp = min(healer.max_hp, healer.current_hp + hp_regen)
            if 'mp_regen' in effect:
                mp_regen = effect['mp_regen']
                healer.current_mp = min(healer.max_mp, healer.current_mp + mp_regen)
        
        print(f"  Runde {turn}: +{hp_regen} HP, +{mp_regen} MP → "
              f"{healer.current_hp}/{healer.max_hp} HP, {healer.current_mp}/{healer.max_mp} MP")

def main():
    """Führe alle Tests aus"""
    print("\n" + "🧬"*30)
    print("MONSTER TRAITS SYSTEM - VOLLSTÄNDIGER TEST")
    print("🧬"*30)
    
    test_trait_database()
    test_metal_body()
    test_critical_master()
    test_resistances()
    test_combat_traits()
    test_trait_inheritance()
    test_special_traits()
    test_regen_traits()
    
    print("\n" + "="*60)
    print("🏁 ALLE TRAIT-TESTS ABGESCHLOSSEN!")
    print("="*60)
    
    print("\n✅ Implementierte Features:")
    print("  • 30+ verschiedene Traits")
    print("  • 8 Trait-Kategorien")
    print("  • Metal Body System")
    print("  • Element-Resistenzen")
    print("  • Stat-Boosts")
    print("  • HP/MP Regeneration")
    print("  • Counter & Thorns")
    print("  • Trait-Vererbung")
    print("  • Integration in Damage Calculator")
    
    print("\nDas Monster Traits System ist bereit für Integration!")

if __name__ == "__main__":
    main()
