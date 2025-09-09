"""
Battle System Integration Tests
Testing das komplette Battle-Flow mit DQM-Mechanics
Autor: Flint Hammerhead - Elite Ruhrpott Programmer
"""

import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from engine.systems.battle.battle_controller import BattleController, BattleState
from engine.systems.unified_damage_calculator import unified_damage_calculator
from engine.systems.monster_instance import MonsterInstance, MonsterSpecies
from engine.systems.stats import BaseStats
from engine.systems.battle.battle_enums import BattleType
from engine.systems.battle.meat_system import MeatSystem
from engine.systems.types import TypeChart


class TestBattleIntegration:
    """Umfassende Battle-System Integration Tests."""
    
    @pytest.fixture
    def test_monster_fire(self):
        """Erstelle Test-Feuer-Monster."""
        species = MonsterSpecies(
            id=1,
            name="Glutstummel",
            types=["Feuer"],
            base_stats=BaseStats(hp=40, atk=54, def_=38, mag=24, res=20, spd=44),
            rank="F",
            growth_curve="fast",
            description="Test Fire Monster"
        )
        return MonsterInstance(species, level=10)
    
    @pytest.fixture
    def test_monster_water(self):
        """Erstelle Test-Wasser-Monster."""
        species = MonsterSpecies(
            id=2,
            name="Wasserkumpel",
            types=["Wasser"],
            base_stats=BaseStats(hp=45, atk=48, def_=42, mag=30, res=25, spd=40),
            rank="F",
            growth_curve="medium_fast",
            description="Test Water Monster"
        )
        return MonsterInstance(species, level=10)
    
    @pytest.fixture
    def battle_state(self, test_monster_fire, test_monster_water):
        """Erstelle Test-Battle-State."""
        state = BattleState(
            player_team=[test_monster_fire],
            enemy_team=[test_monster_water],
            battle_type=BattleType.WILD
        )
        state.player_active = test_monster_fire
        state.enemy_active = test_monster_water
        return state
    
    def test_damage_calculator_consistency(self, test_monster_fire, test_monster_water):
        """Test: Alle Damage-Calculator müssen konsistente Ergebnisse liefern."""
        # Teste UnifiedDamageCalculator
        damage = unified_damage_calculator.calculate_damage(
            attacker=test_monster_fire,
            defender=test_monster_water,
            move_power=40,
            move_type="Feuer",
            is_physical=False
        )
        
        # Damage sollte > 0 sein
        assert damage > 0, "Damage muss größer 0 sein"
        
        # Type-Effectiveness sollte angewendet werden (Feuer vs Wasser = 0.5x)
        assert damage < 20, "Feuer vs Wasser sollte reduzierten Schaden machen"
    
    def test_type_effectiveness_loading(self):
        """Test: Type-Chart lädt korrekt aus types.json."""
        type_chart = TypeChart()
        
        # Teste bekannte Type-Matchups
        effectiveness = type_chart.get_effectiveness("Feuer", "Wasser")
        assert effectiveness == 0.5, "Feuer vs Wasser sollte 0.5x sein"
        
        effectiveness = type_chart.get_effectiveness("Wasser", "Feuer")
        assert effectiveness == 2.0, "Wasser vs Feuer sollte 2.0x sein"
        
        effectiveness = type_chart.get_effectiveness("Feuer", "Pflanze")
        assert effectiveness == 2.0, "Feuer vs Pflanze sollte 2.0x sein"
    
    def test_meat_system_integration(self, battle_state):
        """Test: Meat-System funktioniert mit Battle-Controller."""
        meat_system = MeatSystem()
        
        # Teste Fleisch-Anwendung
        success = meat_system.use_meat("Fleisch", battle_state)
        assert success == True, "Fleisch sollte erfolgreich angewendet werden"
        assert battle_state.meat_bonus == 20, "Fleisch sollte +20% Bonus geben"
        
        # Teste dass Fleisch-Bonus aktiv bleibt
        battle_state.turn_count += 1
        assert battle_state.meat_bonus == 20, "Fleisch-Bonus sollte aktiv bleiben"
        
        # Teste höherwertiges Fleisch
        success = meat_system.use_meat("Edelfleisch", battle_state)
        assert success == True, "Edelfleisch sollte erfolgreich angewendet werden"
        assert battle_state.meat_bonus == 40, "Edelfleisch sollte altes Fleisch überschreiben"
    
    def test_battle_flow_complete(self, battle_state):
        """Test: Vollständiger Battle-Flow ohne Crashes."""
        controller = BattleController(battle_state)
        
        # Teste Battle-Start
        controller.start_battle()
        assert battle_state.phase == "START", "Battle sollte in START-Phase sein"
        
        # Teste Turn-Order
        turn_order = controller.calculate_turn_order()
        assert len(turn_order) > 0, "Turn-Order sollte berechnet werden"
        
        # Teste Action-Queue
        action = {
            'action': 'attack',
            'actor': battle_state.player_active,
            'move': 'Kratzer',
            'target': battle_state.enemy_active
        }
        controller.queue_player_action(action)
        
        # Teste Turn-Execution (sollte nicht crashen)
        try:
            controller.execute_turn()
        except Exception as e:
            pytest.fail(f"Turn-Execution sollte nicht crashen: {e}")
    
    def test_taming_chance_calculation(self, battle_state, test_monster_water):
        """Test: Taming-Chance-Berechnung mit DQM-Formeln."""
        meat_system = MeatSystem()
        
        # Basis-Chance ohne Modifikatoren
        base_chance = meat_system.calculate_taming_chance(
            test_monster_water,
            meat_bonus=0
        )
        assert 0 <= base_chance <= 100, "Taming-Chance muss zwischen 0-100 sein"
        
        # Mit Fleisch-Bonus
        meat_chance = meat_system.calculate_taming_chance(
            test_monster_water,
            meat_bonus=20
        )
        assert meat_chance > base_chance, "Fleisch sollte Taming-Chance erhöhen"
        
        # Mit niedrigem HP
        test_monster_water.current_hp = 1
        low_hp_chance = meat_system.calculate_taming_chance(
            test_monster_water,
            meat_bonus=0
        )
        assert low_hp_chance > base_chance, "Niedriges HP sollte Chance erhöhen"
    
    def test_status_effects_application(self, test_monster_fire):
        """Test: Status-Effekte werden korrekt angewendet."""
        # Teste Burn-Status
        test_monster_fire.apply_status("burn")
        assert test_monster_fire.status == "burn", "Burn sollte angewendet werden"
        
        # Teste Status-Damage
        initial_hp = test_monster_fire.current_hp
        test_monster_fire.process_status_damage()
        assert test_monster_fire.current_hp < initial_hp, "Burn sollte Schaden verursachen"
    
    def test_battle_rewards(self, battle_state):
        """Test: Battle-Rewards werden korrekt berechnet."""
        controller = BattleController(battle_state)
        
        # Simuliere Victory
        battle_state.enemy_active.current_hp = 0
        rewards = controller.calculate_rewards()
        
        assert 'exp' in rewards, "Rewards sollten EXP enthalten"
        assert 'money' in rewards, "Rewards sollten Geld enthalten"
        assert rewards['exp'] > 0, "EXP sollte größer 0 sein"
        assert rewards['money'] > 0, "Geld sollte größer 0 sein"
    
    def test_no_circular_imports(self):
        """Test: Keine Circular Import Errors."""
        try:
            # Versuche alle Battle-Module zu importieren
            from engine.systems.battle import battle_controller
            from engine.systems.battle import battle_actions  
            from engine.systems.battle import battle_ai
            from engine.systems.battle import battle_events
            # from engine.systems.battle import damage_calc  # REMOVED - using unified_damage_calculator
            from engine.systems.battle import turn_logic_clean
            from engine.systems.battle import meat_system
            from engine.systems.battle import reward_system
            
            # Wenn wir hier ankommen, keine Circular Imports
            assert True, "Keine Circular Import Errors"
            
        except ImportError as e:
            pytest.fail(f"Circular Import gefunden: {e}")
    
    def test_save_during_battle(self, battle_state):
        """Test: Game kann während Battle gesaved werden."""
        from engine.systems.save import SaveSystem
        
        save_system = SaveSystem("test_saves")
        
        # Konvertiere Battle-State zu save-fähigem Format
        save_data = {
            'player': {'name': 'Test'},
            'party_manager': {},
            'story': {},
            'quests': {},
            'inventory': {},
            'battle_state': battle_state.__dict__  # Battle-State speichern
        }
        
        # Teste Save
        success = save_system.save_game(1, save_data, "TestSave")
        assert success == True, "Save während Battle sollte funktionieren"
        
        # Teste Load
        loaded_data = save_system.load_game(1)
        assert loaded_data is not None, "Load sollte funktionieren"
        assert 'battle_state' in loaded_data, "Battle-State sollte geladen werden"


class TestPerformance:
    """Performance-Tests für kritische Battle-Komponenten."""
    
    def test_damage_calculator_performance(self):
        """Test: Damage-Calculator Performance."""
        import time
        
        # Erstelle Test-Monster
        species = MonsterSpecies(
            id=1, name="Test", types=["Feuer"],
            base_stats=BaseStats(hp=40, atk=50, def_=40, mag=30, res=30, spd=40),
            rank="E", growth_curve="medium_fast", description="Test"
        )
        attacker = MonsterInstance(species, level=50)
        defender = MonsterInstance(species, level=50)
        
        # Teste 1000 Damage-Berechnungen
        start = time.time()
        for _ in range(1000):
            damage = unified_damage_calculator.calculate_damage(
                attacker=attacker,
                defender=defender,
                move_power=80,
                move_type="Feuer",
                is_physical=True
            )
        elapsed = time.time() - start
        
        # Sollte unter 100ms sein für 1000 Berechnungen
        assert elapsed < 0.1, f"Damage-Calculator zu langsam: {elapsed:.3f}s für 1000 Berechnungen"
    
    def test_type_chart_cache_performance(self):
        """Test: Type-Chart Cache funktioniert."""
        type_chart = TypeChart()
        
        # Erste Abfrage (Cache-Miss)
        import time
        start = time.time()
        for _ in range(100):
            type_chart.get_effectiveness("Feuer", "Wasser")
        first_time = time.time() - start
        
        # Zweite Abfrage (sollte gecached sein)
        start = time.time()
        for _ in range(100):
            type_chart.get_effectiveness("Feuer", "Wasser")
        cached_time = time.time() - start
        
        # Cached sollte mindestens 2x schneller sein
        assert cached_time < first_time / 2, "Cache sollte Performance verbessern"
        
        # Prüfe Cache-Stats
        stats = type_chart.get_performance_stats()
        assert stats['cache_hits'] > 0, "Cache sollte Hits haben"


if __name__ == "__main__":
    # Führe Tests aus
    pytest.main([__file__, "-v", "--tb=short"])
