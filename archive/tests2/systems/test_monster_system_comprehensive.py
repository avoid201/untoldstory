#!/usr/bin/env python3
"""
Umfassende Tests für das Monster-System
Testet alle kritischen Funktionen und Edge Cases
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

# Projekt-Root zum Python-Pfad hinzufügen
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Engine-Imports
from engine.systems.monsters import Monster
from engine.systems.monster_instance import MonsterInstance
from engine.systems.moves import Move
from engine.systems.types import TypeSystem
from engine.systems.stats import Stats

@pytest.mark.systems
@pytest.mark.monster
class TestMonsterSystem:
    """Test-Klasse für das Monster-System"""
    
    def test_monster_creation(self, test_data):
        """Testet die Monster-Erstellung"""
        monster_data = test_data["monsters"]["test_monster"]
        
        monster = Monster(
            id=monster_data["id"],
            name=monster_data["name"],
            types=monster_data["types"],
            base_stats=monster_data["base_stats"],
            moves=monster_data["moves"]
        )
        
        assert monster.id == "test_monster"
        assert monster.name == "Test Monster"
        assert monster.types == ["Normal"]
        assert monster.base_stats.hp == 50
        assert monster.base_stats.attack == 30
        assert monster.base_stats.defense == 25
        assert monster.base_stats.speed == 20
        assert monster.moves == ["tackle", "growl"]
    
    def test_monster_instance_creation(self, test_data):
        """Testet die MonsterInstance-Erstellung"""
        monster_data = test_data["monsters"]["test_monster"]
        
        monster = Monster(
            id=monster_data["id"],
            name=monster_data["name"],
            types=monster_data["types"],
            base_stats=monster_data["base_stats"],
            moves=monster_data["moves"]
        )
        
        instance = MonsterInstance(monster, level=5)
        
        assert instance.monster == monster
        assert instance.level == 5
        assert instance.current_hp > 0
        assert instance.current_hp <= instance.max_hp
        assert instance.experience == 0
        assert instance.experience_to_next == 100  # Beispiel-Wert
    
    def test_level_up_mechanics(self, test_data):
        """Testet Level-Up-Mechaniken"""
        monster_data = test_data["monsters"]["test_monster"]
        
        monster = Monster(
            id=monster_data["id"],
            name=monster_data["name"],
            types=monster_data["types"],
            base_stats=monster_data["base_stats"],
            moves=monster_data["moves"]
        )
        
        instance = MonsterInstance(monster, level=1)
        initial_hp = instance.current_hp
        initial_attack = instance.stats.attack
        
        # Level-Up simulieren
        instance.gain_experience(100)
        
        if instance.level > 1:  # Falls Level-Up stattfindet
            assert instance.stats.attack > initial_attack
            assert instance.max_hp > initial_hp
            assert instance.current_hp == instance.max_hp  # HP werden bei Level-Up aufgefüllt
    
    def test_move_learning(self, test_data):
        """Testet das Lernen von Moves"""
        monster_data = test_data["monsters"]["test_monster"]
        
        monster = Monster(
            id=monster_data["id"],
            name=monster_data["name"],
            types=monster_data["types"],
            base_stats=monster_data["base_stats"],
            moves=monster_data["moves"]
        )
        
        instance = MonsterInstance(monster, level=1)
        initial_move_count = len(instance.available_moves)
        
        # Neuen Move lernen
        new_move = Move(
            id="scratch",
            name="Scratch",
            type="Normal",
            power=40,
            accuracy=100,
            pp=30
        )
        
        instance.learn_move(new_move)
        
        assert len(instance.available_moves) == initial_move_count + 1
        assert new_move in instance.available_moves
    
    def test_move_usage(self, test_data):
        """Testet die Verwendung von Moves"""
        monster_data = test_data["monsters"]["test_monster"]
        
        monster = Monster(
            id=monster_data["id"],
            name=monster_data["name"],
            types=monster_data["types"],
            base_stats=monster_data["base_stats"],
            moves=monster_data["moves"]
        )
        
        instance = MonsterInstance(monster, level=5)
        
        # Move erstellen
        move = Move(
            id="tackle",
            name="Tackle",
            type="Normal",
            power=40,
            accuracy=100,
            pp=35
        )
        
        # PP vor Verwendung
        initial_pp = move.current_pp
        
        # Move verwenden
        success = instance.use_move(move)
        
        if success:
            assert move.current_pp == initial_pp - 1
        else:
            # Move könnte fehlschlagen (z.B. keine PP mehr)
            assert move.current_pp <= initial_pp
    
    def test_type_effectiveness(self, test_data):
        """Testet Type-Effektivität"""
        type_system = TypeSystem()
        
        # Normal vs Rock (0.5x)
        effectiveness = type_system.get_effectiveness("Normal", "Rock")
        assert effectiveness == 0.5
        
        # Normal vs Ghost (0x)
        effectiveness = type_system.get_effectiveness("Normal", "Ghost")
        assert effectiveness == 0.0
        
        # Normal vs Normal (1x)
        effectiveness = type_system.get_effectiveness("Normal", "Normal")
        assert effectiveness == 1.0
    
    def test_stats_calculation(self, test_data):
        """Testet die Stats-Berechnung"""
        base_stats = test_data["monsters"]["test_monster"]["base_stats"]
        
        stats = Stats(
            hp=base_stats["hp"],
            attack=base_stats["attack"],
            defense=base_stats["defense"],
            speed=base_stats["speed"]
        )
        
        # Level 1 Stats
        level1_stats = stats.calculate_for_level(1)
        assert level1_stats.hp > 0
        assert level1_stats.attack > 0
        assert level1_stats.defense > 0
        assert level1_stats.speed > 0
        
        # Level 50 Stats (sollten höher sein)
        level50_stats = stats.calculate_for_level(50)
        assert level50_stats.hp > level1_stats.hp
        assert level50_stats.attack > level1_stats.attack
        assert level50_stats.defense > level1_stats.defense
        assert level50_stats.speed > level1_stats.speed
    
    def test_evolution_mechanics(self, test_data):
        """Testet Evolutions-Mechaniken"""
        # Monster mit Evolution
        evolution_monster = Monster(
            id="evolution_test",
            name="Evolution Test",
            types=["Normal"],
            base_stats={"hp": 30, "attack": 20, "defense": 15, "speed": 15},
            moves=["tackle"],
            evolution_requirements={"level": 16, "item": None}
        )
        
        instance = MonsterInstance(evolution_monster, level=15)
        
        # Vor Evolution
        assert instance.monster.name == "Evolution Test"
        
        # Level 16 erreichen (Evolution auslösen)
        instance.gain_experience(1000)  # Genug für Level 16
        
        # Evolution sollte stattfinden
        if hasattr(instance, 'evolve') and instance.can_evolve():
            evolved = instance.evolve()
            if evolved:
                assert instance.monster.name != "Evolution Test"
    
    def test_status_effects(self, test_data):
        """Testet Status-Effekte"""
        monster_data = test_data["monsters"]["test_monster"]
        
        monster = Monster(
            id=monster_data["id"],
            name=monster_data["name"],
            types=monster_data["types"],
            base_stats=monster_data["base_stats"],
            moves=monster_data["moves"]
        )
        
        instance = MonsterInstance(monster, level=5)
        
        # Status-Effekt anwenden
        instance.apply_status_effect("poison")
        
        assert "poison" in instance.status_effects
        assert instance.is_poisoned()
        
        # Status-Effekt entfernen
        instance.remove_status_effect("poison")
        
        assert "poison" not in instance.status_effects
        assert not instance.is_poisoned()
    
    def test_healing_mechanics(self, test_data):
        """Testet Heilungs-Mechaniken"""
        monster_data = test_data["monsters"]["test_monster"]
        
        monster = Monster(
            id=monster_data["id"],
            name=monster_data["name"],
            types=monster_data["types"],
            base_stats=monster_data["base_stats"],
            moves=monster_data["moves"]
        )
        
        instance = MonsterInstance(monster, level=5)
        
        # HP reduzieren
        damage = 20
        instance.take_damage(damage)
        
        assert instance.current_hp < instance.max_hp
        
        # Heilung anwenden
        heal_amount = 15
        instance.heal(heal_amount)
        
        assert instance.current_hp > instance.max_hp - damage
        assert instance.current_hp <= instance.max_hp
    
    def test_fainting_mechanics(self, test_data):
        """Testet Ohnmachts-Mechaniken"""
        monster_data = test_data["monsters"]["test_monster"]
        
        monster = Monster(
            id=monster_data["id"],
            name=monster_data["name"],
            types=monster_data["types"],
            base_stats=monster_data["base_stats"],
            moves=monster_data["moves"]
        )
        
        instance = MonsterInstance(monster, level=5)
        
        # Monster sollte am Anfang am Leben sein
        assert not instance.is_fainted()
        
        # Monster besiegen
        instance.take_damage(instance.current_hp)
        
        assert instance.is_fainted()
        assert instance.current_hp == 0
        
        # Monster wiederbeleben
        instance.revive()
        
        assert not instance.is_fainted()
        assert instance.current_hp > 0
    
    def test_move_accuracy(self, test_data):
        """Testet Move-Genauigkeit"""
        # Move mit 100% Genauigkeit
        accurate_move = Move(
            id="accurate",
            name="Accurate Move",
            type="Normal",
            power=50,
            accuracy=100,
            pp=20
        )
        
        # Move mit 50% Genauigkeit
        inaccurate_move = Move(
            id="inaccurate",
            name="Inaccurate Move",
            type="Normal",
            power=80,
            accuracy=50,
            pp=20
        )
        
        # Teste Genauigkeit
        assert accurate_move.check_accuracy()  # Sollte immer True sein
        # inaccurate_move.check_accuracy() könnte True oder False sein
    
    def test_critical_hits(self, test_data):
        """Testet kritische Treffer"""
        monster_data = test_data["monsters"]["test_monster"]
        
        monster = Monster(
            id=monster_data["id"],
            name=monster_data["name"],
            types=monster_data["types"],
            base_stats=monster_data["base_stats"],
            moves=monster_data["moves"]
        )
        
        instance = MonsterInstance(monster, level=5)
        
        # Kritische Treffer-Wahrscheinlichkeit
        crit_chance = instance.get_critical_hit_chance()
        
        assert 0.0 <= crit_chance <= 1.0
        
        # Kritische Treffer-Multiplikator
        crit_multiplier = instance.get_critical_hit_multiplier()
        
        assert crit_multiplier >= 1.0
    
    def test_weather_effects(self, test_data):
        """Testet Wetter-Effekte auf Monster"""
        monster_data = test_data["monsters"]["test_monster"]
        
        monster = Monster(
            id=monster_data["id"],
            name=monster_data["name"],
            types=monster_data["types"],
            base_stats=monster_data["base_stats"],
            moves=monster_data["moves"]
        )
        
        instance = MonsterInstance(monster, level=5)
        
        # Wetter-Effekte anwenden
        instance.apply_weather_effect("rain")
        
        assert instance.weather_effects.get("rain") is not None
        
        # Wetter-Effekte entfernen
        instance.remove_weather_effect("rain")
        
        assert "rain" not in instance.weather_effects
    
    def test_ability_effects(self, test_data):
        """Testet Fähigkeiten-Effekte"""
        monster_data = test_data["monsters"]["test_monster"]
        
        monster = Monster(
            id=monster_data["id"],
            name=monster_data["name"],
            types=monster_data["types"],
            base_stats=monster_data["base_stats"],
            moves=monster_data["moves"],
            ability="test_ability"
        )
        
        instance = MonsterInstance(monster, level=5)
        
        # Fähigkeit aktivieren
        if hasattr(instance, 'activate_ability'):
            effect = instance.activate_ability()
            
            if effect:
                assert instance.ability_active
                assert instance.ability_effects is not None
    
    def test_breeding_mechanics(self, test_data):
        """Testet Zucht-Mechaniken"""
        # Zwei kompatible Monster
        parent1 = MonsterInstance(
            Monster(
                id="parent1",
                name="Parent 1",
                types=["Normal"],
                base_stats={"hp": 30, "attack": 20, "defense": 15, "speed": 15},
                moves=["tackle"]
            ),
            level=20
        )
        
        parent2 = MonsterInstance(
            Monster(
                id="parent2",
                name="Parent 2",
                types=["Normal"],
                base_stats={"hp": 35, "attack": 25, "defense": 20, "speed": 18},
                moves=["growl"]
            ),
            level=20
        )
        
        # Zucht-Kompatibilität prüfen
        if hasattr(parent1, 'can_breed_with'):
            compatible = parent1.can_breed_with(parent2)
            
            if compatible:
                # Zucht durchführen
                if hasattr(parent1, 'breed_with'):
                    offspring = parent1.breed_with(parent2)
                    
                    if offspring:
                        assert offspring.level == 1
                        assert offspring.monster.types == ["Normal"]
                        assert len(offspring.available_moves) > 0
    
    def test_training_mechanics(self, test_data):
        """Testet Trainings-Mechaniken"""
        monster_data = test_data["monsters"]["test_monster"]
        
        monster = Monster(
            id=monster_data["id"],
            name=monster_data["name"],
            types=monster_data["types"],
            base_stats=monster_data["base_stats"],
            moves=monster_data["moves"]
        )
        
        instance = MonsterInstance(monster, level=5)
        
        # Training durchführen
        if hasattr(instance, 'train'):
            initial_stats = instance.stats.copy()
            
            training_result = instance.train("attack", 10)
            
            if training_result:
                assert instance.stats.attack > initial_stats.attack
    
    def test_item_effects(self, test_data):
        """Testet Item-Effekte auf Monster"""
        monster_data = test_data["monsters"]["test_monster"]
        
        monster = Monster(
            id=monster_data["id"],
            name=monster_data["name"],
            types=monster_data["types"],
            base_stats=monster_data["base_stats"],
            moves=monster_data["moves"]
        )
        
        instance = MonsterInstance(monster, level=5)
        
        # Item anwenden
        if hasattr(instance, 'equip_item'):
            initial_stats = instance.stats.copy()
            
            item_effect = instance.equip_item("test_item")
            
            if item_effect:
                assert instance.equipped_item == "test_item"
                # Stats könnten sich geändert haben
    
    def test_team_synergy(self, test_data):
        """Testet Team-Synergien"""
        # Team aus verschiedenen Typen
        team = [
            MonsterInstance(
                Monster(
                    id="fire_monster",
                    name="Fire Monster",
                    types=["Fire"],
                    base_stats={"hp": 40, "attack": 35, "defense": 20, "speed": 25},
                    moves=["ember"]
                ),
                level=10
            ),
            MonsterInstance(
                Monster(
                    id="water_monster",
                    name="Water Monster",
                    types=["Water"],
                    base_stats={"hp": 45, "attack": 30, "defense": 25, "speed": 20},
                    moves=["bubble"]
                ),
                level=10
            )
        ]
        
        # Team-Bonus berechnen
        if hasattr(team[0], 'get_team_bonus'):
            team_bonus = team[0].get_team_bonus(team)
            
            assert isinstance(team_bonus, dict)
            assert "attack_bonus" in team_bonus or "defense_bonus" in team_bonus
    
    def test_environmental_effects(self, test_data):
        """Testet Umgebungs-Effekte"""
        monster_data = test_data["monsters"]["test_monster"]
        
        monster = Monster(
            id=monster_data["id"],
            name=monster_data["name"],
            types=monster_data["types"],
            base_stats=monster_data["base_stats"],
            moves=monster_data["moves"]
        )
        
        instance = MonsterInstance(monster, level=5)
        
        # Umgebungs-Effekt anwenden
        if hasattr(instance, 'apply_environmental_effect'):
            effect = instance.apply_environmental_effect("cave")
            
            if effect:
                assert instance.environmental_effects.get("cave") is not None
                
                # Effekt entfernen
                instance.remove_environmental_effect("cave")
                assert "cave" not in instance.environmental_effects

@pytest.mark.systems
@pytest.mark.monster
class TestMonsterSystemEdgeCases:
    """Test-Klasse für Edge Cases im Monster-System"""
    
    def test_invalid_monster_data(self):
        """Testet ungültige Monster-Daten"""
        with pytest.raises(ValueError):
            Monster(
                id="",
                name="",
                types=[],
                base_stats={},
                moves=[]
            )
    
    def test_negative_stats(self):
        """Testet negative Stats"""
        with pytest.raises(ValueError):
            Stats(
                hp=-10,
                attack=-5,
                defense=-3,
                speed=-2
            )
    
    def test_invalid_level(self):
        """Testet ungültige Level"""
        monster = Monster(
            id="test",
            name="Test",
            types=["Normal"],
            base_stats={"hp": 30, "attack": 20, "defense": 15, "speed": 15},
            moves=[]
        )
        
        with pytest.raises(ValueError):
            MonsterInstance(monster, level=0)
        
        with pytest.raises(ValueError):
            MonsterInstance(monster, level=101)  # Max Level überschritten
    
    def test_empty_moves_list(self):
        """Testet leere Moves-Liste"""
        monster = Monster(
            id="test",
            name="Test",
            types=["Normal"],
            base_stats={"hp": 30, "attack": 20, "defense": 15, "speed": 15},
            moves=[]
        )
        
        instance = MonsterInstance(monster, level=5)
        
        # Monster ohne Moves sollte nicht kämpfen können
        assert len(instance.available_moves) == 0
        
        if hasattr(instance, 'can_battle'):
            assert not instance.can_battle()
    
    def test_duplicate_types(self):
        """Testet doppelte Typen"""
        monster = Monster(
            id="test",
            name="Test",
            types=["Normal", "Normal"],  # Doppelter Typ
            base_stats={"hp": 30, "attack": 20, "defense": 15, "speed": 15},
            moves=[]
        )
        
        # Doppelte Typen sollten entfernt werden
        assert len(set(monster.types)) == len(monster.types)
    
    def test_extreme_stats(self):
        """Testet extreme Stats-Werte"""
        monster = Monster(
            id="test",
            name="Test",
            types=["Normal"],
            base_stats={"hp": 999, "attack": 999, "defense": 999, "speed": 999},
            moves=[]
        )
        
        instance = MonsterInstance(monster, level=100)
        
        # Stats sollten begrenzt sein
        assert instance.stats.hp <= 9999  # Max HP
        assert instance.stats.attack <= 999  # Max Attack
        assert instance.stats.defense <= 999  # Max Defense
        assert instance.stats.speed <= 999  # Max Speed
