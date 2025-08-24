"""
Encounter & Battle System für FieldScene
Verwaltet Zufallsbegegnungen und Kampf-Initialisierung
"""

import random
from typing import Optional
from engine.systems.monster_instance import MonsterInstance


class FieldEncounterSystem:
    """
    Verwaltet das Encounter-System in der Field-Scene.
    Wilde Monster, Trainer-Kämpfe, alles!
    """
    
    def __init__(self, field_scene):
        """
        Initialisiert das Encounter-System.
        
        Args:
            field_scene: Referenz zur FieldScene
        """
        self.scene = field_scene
        self.encounter_enabled = True
        self.steps_since_encounter = 0
        self.min_steps_between_encounters = 10
        self.encounter_check_pending = False
        self.in_battle = False
        
        print("[EncounterSystem] Initialisiert!")
    
    def check_encounter(self, tile_x: int, tile_y: int, steps: int = 1) -> None:
        """
        Prüft auf Zufalls-Encounter.
        
        Args:
            tile_x: Aktuelle Tile X-Position
            tile_y: Aktuelle Tile Y-Position
            steps: Schritte seit letztem Encounter
        """
        if not self.encounter_enabled or not self.scene.current_area or self.in_battle:
            return
        
        # Schritte erhöhen
        self.steps_since_encounter += steps
        
        # Minimum-Schritte prüfen
        if self.steps_since_encounter < self.min_steps_between_encounters:
            return
        
        # Terrain-Typ prüfen (Gras = 2 oder 5)
        tile_type = self._get_tile_type(tile_x, tile_y)
        
        if tile_type in [2, 5]:  # Gras-Tiles
            # Würfeln für Encounter
            if random.random() < self.scene.current_area.encounter_rate:
                # Encounter im nächsten Frame ausführen (vermeidet Movement-Probleme)
                self.encounter_check_pending = True
    
    def _get_tile_type(self, tile_x: int, tile_y: int) -> int:
        """Holt den Tile-Typ an Position."""
        if not self.scene.current_area:
            return 0
        
        # Versuche verschiedene Methoden
        if hasattr(self.scene.current_area, 'get_tile_type'):
            return self.scene.current_area.get_tile_type(tile_x, tile_y)
        
        if hasattr(self.scene.current_area, 'map_data') and self.scene.current_area.map_data:
            layers = self.scene.current_area.map_data.layers
            if "ground" in layers:
                layer = layers["ground"]
                if 0 <= tile_y < len(layer) and 0 <= tile_x < len(layer[tile_y]):
                    return layer[tile_y][tile_x]
        
        return 0
    
    def execute_encounter_check(self) -> None:
        """Führt den tatsächlichen Encounter-Check aus."""
        if not self.scene.game.party_manager.party.get_conscious_members():
            # Keine kampffähigen Monster
            return
        
        # Kampf starten!
        self.start_wild_battle()
    
    def start_wild_battle(self) -> None:
        """Startet einen Wildkampf."""
        if self.in_battle:
            return
        
        # Party prüfen
        if not self.scene.game.party_manager.party.get_conscious_members():
            self.scene.interaction_system.show_text(
                "Du hast keine kampffähigen Monster! Hol dir erst eins vom Professor!",
                callback=lambda _: None
            )
            return
        
        # In-Battle Flag setzen
        self.in_battle = True
        
        # Schritte zurücksetzen
        self.steps_since_encounter = 0
        
        # Wildes Monster generieren
        wild_monster = self._generate_wild_monster()
        
        if not wild_monster:
            # Keine Encounter-Daten
            self.scene.interaction_system.show_text(
                "Keine Monster in diesem Gebiet! (Encounter-Daten fehlen)",
                callback=lambda _: setattr(self, 'in_battle', False)
            )
            return
        
        # Encounter-Nachricht zeigen
        self.scene.interaction_system.show_text(
            f"Ein wildes {wild_monster.species_name} erscheint!",
            callback=lambda _: self._transition_to_battle(wild_monster)
        )
    
    def _generate_wild_monster(self) -> Optional[MonsterInstance]:
        """Generiert ein wildes Monster aus der Encounter-Tabelle."""
        if not self.scene.current_area or not self.scene.current_area.encounter_table:
            # Fallback für Tests
            species = self.scene.game.resources.get_monster_species(5)  # Rattfratz
            if species:
                monster = MonsterInstance.create_from_species(
                    species=species,
                    level=random.randint(2, 5)
                )
                return monster
            return None
        
        # Gesamt-Gewicht berechnen
        total_weight = sum(enc['weight'] for enc in self.scene.current_area.encounter_table)
        
        # Zufallszahl würfeln
        roll = random.randint(1, total_weight)
        
        # Monster finden
        current_weight = 0
        for encounter in self.scene.current_area.encounter_table:
            current_weight += encounter['weight']
            if roll <= current_weight:
                # Dieses Monster spawnen!
                species = self.scene.game.resources.get_monster_species(encounter['species_id'])
                if species:
                    level = random.randint(encounter['level_min'], encounter['level_max'])
                    monster = MonsterInstance.create_from_species(
                        species=species,
                        level=level
                    )
                    return monster
                else:
                    # Fallback mit Minimal-Species
                    placeholder_species = self._create_placeholder_species(encounter)
                    level = random.randint(encounter['level_min'], encounter['level_max'])
                    return MonsterInstance.create_from_species(placeholder_species, level=level)
        
        return None
    
    def _create_placeholder_species(self, encounter: dict) -> dict:
        """Erstellt eine Placeholder-Species für fehlende Monster."""
        return {
            "id": encounter['species_id'],
            "name": encounter['name'],
            "era": "present",
            "rank": encounter.get('rank', 'F'),
            "types": ["Normal"],
            "base_stats": {
                "hp": 15,
                "atk": 5,
                "def": 5,
                "mag": 5,
                "res": 5,
                "spd": 5
            },
            "growth": {"curve": "medium_fast", "yield": 40},
            "capture_rate": 255,
            "traits": [],
            "learnset": []
        }
    
    def _transition_to_battle(self, wild_monster: MonsterInstance) -> None:
        """Übergang zur Kampf-Szene."""
        # Battle-Transition-Effekt
        self.scene.game.start_transition('battle_swirl', duration=0.8)
        
        # Battle-Scene erstellen
        from engine.scenes.battle_scene import BattleScene
        
        # Kampf nach kurzer Verzögerung starten
        def start_battle_after_transition():
            self.scene.game.push_scene(
                BattleScene,
                player_team=None,  # Nutzt Party Manager
                enemy_team=[wild_monster],
                is_wild=True,
                background='grass'
            )
            # In-Battle Flag zurücksetzen wenn wir zurückkommen
            self.in_battle = False
        
        # Kampf nach Transition starten
        import threading
        threading.Timer(0.4, start_battle_after_transition).start()
    
    def start_trainer_battle(self, trainer_name: str, enemy_team: list, 
                           on_victory=None, on_defeat=None) -> None:
        """
        Startet einen Trainer-Kampf.
        
        Args:
            trainer_name: Name des Trainers
            enemy_team: Liste von gegnerischen Monstern
            on_victory: Callback bei Sieg
            on_defeat: Callback bei Niederlage
        """
        from engine.scenes.battle_scene import BattleScene
        
        self.scene.game.push_scene(
            BattleScene,
            enemy_team=enemy_team,
            is_trainer_battle=True,
            trainer_name=trainer_name,
            on_victory=on_victory,
            on_defeat=on_defeat
        )
    
    def force_battle_debug(self) -> None:
        """Debug-Funktion um Kampf zu erzwingen."""
        self.start_wild_battle()
    
    def reset_encounter_counter(self) -> None:
        """Setzt den Encounter-Zähler zurück."""
        self.steps_since_encounter = 0
    
    def set_encounter_enabled(self, enabled: bool) -> None:
        """Aktiviert/Deaktiviert Encounters."""
        self.encounter_enabled = enabled
        print(f"[EncounterSystem] Encounters {'aktiviert' if enabled else 'deaktiviert'}")
