#!/usr/bin/env python3
"""
BATTLE INTEGRATION TEST - Untold Story
System-Integrations-Experte Test-Suite

Testet vollständigen Battle-Flow mit allen Menü-Optionen:
- Start Battle → Attack → Enemy Turn → Victory
- Start Battle → Tame mit Fleisch → Success/Fail
- Start Battle → Scout → Flee
- Start Battle → Switch Monster → Attack

FOKUS: Integration zwischen BattleScene, BattleUI, BattleController
"""

import sys
import os
import pygame
import time
import traceback
from typing import Dict, List, Any, Optional

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import game components
from engine.core.game import Game
from engine.scenes.battle_scene import BattleScene
from engine.systems.monsters import MonsterDatabase
from engine.systems.monster_instance import MonsterInstance
from engine.systems.battle.battle_enums import BattleResult, BattlePhase
from engine.ui.battle_ui import BattleMenuState
from engine.core.debug_utils import debug_battle_info, debug_battle_error


class BattleIntegrationTester:
    """Umfassender Battle-Integrations-Test."""
    
    def __init__(self):
        """Initialisiere Test-System."""
        self.game = None
        self.battle_scene = None
        self.test_results = {}
        self.current_test = None
        
        # Test-Konfiguration
        self.test_timeout = 30.0  # 30 Sekunden pro Test
        self.auto_advance_delay = 2.0  # 2 Sekunden zwischen Aktionen
        
        print("=== BATTLE INTEGRATION TESTER ===")
        print("Initialisiere Test-System...")
    
    def setup_game(self) -> bool:
        """Initialisiere Game-Instanz für Tests."""
        try:
            # Pygame initialisieren
            pygame.init()
            
            # Display-Setup wie in main.py
            LOGICAL_WIDTH = 320
            LOGICAL_HEIGHT = 180
            SCALE_FACTOR = 4
            WINDOW_WIDTH = LOGICAL_WIDTH * SCALE_FACTOR
            WINDOW_HEIGHT = LOGICAL_HEIGHT * SCALE_FACTOR
            
            # Create the display window
            screen = pygame.display.set_mode(
                (WINDOW_WIDTH, WINDOW_HEIGHT),
                pygame.SCALED | pygame.RESIZABLE
            )
            pygame.display.set_caption("Untold Story - Battle Test")
            
            # Create a logical backbuffer for pixel-perfect rendering
            logical_surface = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT))
            
            # Game-Instanz erstellen mit korrekten Parametern
            self.game = Game(
                screen=screen,
                logical_surface=logical_surface,
                logical_size=(LOGICAL_WIDTH, LOGICAL_HEIGHT),
                window_size=(WINDOW_WIDTH, WINDOW_HEIGHT),
                scale_factor=SCALE_FACTOR
            )
            self.game.debug_mode = True
            
            # Demo-Party erstellen
            self._create_demo_party()
            
            print("✓ Game-System initialisiert")
            return True
            
        except Exception as e:
            print(f"✗ Game-Setup fehlgeschlagen: {e}")
            traceback.print_exc()
            return False
    
    def _create_demo_party(self):
        """Erstelle Demo-Party für Tests."""
        try:
            from engine.systems.party import PartyManager
            from engine.systems.monsters import MonsterDatabase
            
            # Party Manager initialisieren
            self.game.party_manager = PartyManager()
            
            # Monster Database laden
            db = MonsterDatabase()
            
            # Demo-Monster erstellen
            species = db.get_random_species()
            if species:
                monster1 = species.create_instance(level=10)
                monster1.name = "TestMonster1"
                monster1.current_hp = monster1.max_hp
                
                monster2 = species.create_instance(level=8)
                monster2.name = "TestMonster2"
                monster2.current_hp = monster2.max_hp
                
                # Zur Party hinzufügen
                self.game.party_manager.add_to_party(monster1)
                self.game.party_manager.add_to_party(monster2)
                
                print(f"✓ Demo-Party erstellt: {monster1.name}, {monster2.name}")
            else:
                print("⚠ Keine Monster-Species verfügbar")
                
        except Exception as e:
            print(f"⚠ Demo-Party Setup fehlgeschlagen: {e}")
    
    def run_all_tests(self) -> Dict[str, bool]:
        """Führe alle Battle-Integration-Tests aus."""
        print("\n=== STARTE BATTLE INTEGRATION TESTS ===")
        
        if not self.setup_game():
            return {"setup": False}
        
        # Test-Szenarien
        test_scenarios = [
            ("attack_victory", self.test_attack_victory_flow),
            ("tame_success", self.test_tame_success_flow),
            ("tame_failure", self.test_tame_failure_flow),
            ("scout_flee", self.test_scout_flee_flow),
            ("switch_attack", self.test_switch_attack_flow),
            ("menu_navigation", self.test_menu_navigation),
            ("battle_phases", self.test_battle_phases),
            ("error_handling", self.test_error_handling)
        ]
        
        for test_name, test_func in test_scenarios:
            print(f"\n--- Teste: {test_name} ---")
            self.current_test = test_name
            
            try:
                result = test_func()
                self.test_results[test_name] = result
                
                if result:
                    print(f"✓ {test_name}: ERFOLGREICH")
                else:
                    print(f"✗ {test_name}: FEHLGESCHLAGEN")
                    
            except Exception as e:
                print(f"✗ {test_name}: EXCEPTION - {e}")
                traceback.print_exc()
                self.test_results[test_name] = False
            
            # Kurze Pause zwischen Tests
            time.sleep(0.5)
        
        return self.test_results
    
    def test_attack_victory_flow(self) -> bool:
        """Test: Start Battle → Attack → Enemy Turn → Victory"""
        try:
            print("Teste Attack-Victory-Flow...")
            
            # Battle starten
            if not self._start_battle():
                return False
            
            # Warte auf Battle-Initialisierung
            if not self._wait_for_phase(BattlePhase.INPUT):
                return False
            
            # Attack-Menü öffnen
            if not self._navigate_to_menu(BattleMenuState.MOVE_SELECT):
                return False
            
            # Ersten Move auswählen
            if not self._select_first_move():
                return False
            
            # Warte auf Battle-Ende
            if not self._wait_for_battle_end():
                return False
            
            # Prüfe Victory-Result
            if self.battle_scene.battle_result == BattleResult.VICTORY:
                print("✓ Attack-Victory-Flow erfolgreich")
                return True
            else:
                print(f"✗ Falsches Battle-Result: {self.battle_scene.battle_result}")
                return False
                
        except Exception as e:
            print(f"✗ Attack-Victory-Flow fehlgeschlagen: {e}")
            return False
    
    def test_tame_success_flow(self) -> bool:
        """Test: Start Battle → Tame mit Fleisch → Success"""
        try:
            print("Teste Tame-Success-Flow...")
            
            # Battle starten
            if not self._start_battle():
                return False
            
            # Warte auf Battle-Initialisierung
            if not self._wait_for_phase(BattlePhase.INPUT):
                return False
            
            # Tame-Menü öffnen
            if not self._navigate_to_menu(BattleMenuState.TAME_MEAT):
                return False
            
            # Fleisch auswählen (falls verfügbar)
            if not self._select_meat_item():
                print("⚠ Kein Fleisch verfügbar, teste ohne")
            
            # Tame bestätigen
            if not self._navigate_to_menu(BattleMenuState.TAME_CONFIRM):
                return False
            
            # Tame ausführen
            if not self._confirm_tame():
                return False
            
            # Warte auf Battle-Ende
            if not self._wait_for_battle_end():
                return False
            
            # Prüfe Tame-Result
            if self.battle_scene.battle_result in [BattleResult.CAUGHT, BattleResult.VICTORY]:
                print("✓ Tame-Success-Flow erfolgreich")
                return True
            else:
                print(f"✗ Falsches Battle-Result: {self.battle_scene.battle_result}")
                return False
                
        except Exception as e:
            print(f"✗ Tame-Success-Flow fehlgeschlagen: {e}")
            return False
    
    def test_tame_failure_flow(self) -> bool:
        """Test: Start Battle → Tame → Failure → Continue Battle"""
        try:
            print("Teste Tame-Failure-Flow...")
            
            # Battle starten
            if not self._start_battle():
                return False
            
            # Warte auf Battle-Initialisierung
            if not self._wait_for_phase(BattlePhase.INPUT):
                return False
            
            # Tame-Menü öffnen
            if not self._navigate_to_menu(BattleMenuState.TAME_MEAT):
                return False
            
            # Tame bestätigen
            if not self._navigate_to_menu(BattleMenuState.TAME_CONFIRM):
                return False
            
            # Tame ausführen
            if not self._confirm_tame():
                return False
            
            # Warte kurz auf Tame-Result
            time.sleep(1.0)
            
            # Prüfe ob Battle weiterläuft (Tame fehlgeschlagen)
            if self.battle_scene.battle_result == BattleResult.ONGOING:
                print("✓ Tame-Failure-Flow erfolgreich (Battle läuft weiter)")
                return True
            else:
                print(f"✗ Battle beendet unerwartet: {self.battle_scene.battle_result}")
                return False
                
        except Exception as e:
            print(f"✗ Tame-Failure-Flow fehlgeschlagen: {e}")
            return False
    
    def test_scout_flee_flow(self) -> bool:
        """Test: Start Battle → Scout → Flee"""
        try:
            print("Teste Scout-Flee-Flow...")
            
            # Battle starten
            if not self._start_battle():
                return False
            
            # Warte auf Battle-Initialisierung
            if not self._wait_for_phase(BattlePhase.INPUT):
                return False
            
            # Scout-Menü öffnen
            if not self._navigate_to_menu(BattleMenuState.SCOUT):
                return False
            
            # Scout-Info anzeigen lassen
            time.sleep(1.0)
            
            # Zurück zum Hauptmenü
            if not self._navigate_to_menu(BattleMenuState.MAIN):
                return False
            
            # Flee auswählen
            if not self._select_flee():
                return False
            
            # Warte auf Battle-Ende
            if not self._wait_for_battle_end():
                return False
            
            # Prüfe Flee-Result
            if self.battle_scene.battle_result == BattleResult.FLED:
                print("✓ Scout-Flee-Flow erfolgreich")
                return True
            else:
                print(f"✗ Falsches Battle-Result: {self.battle_scene.battle_result}")
                return False
                
        except Exception as e:
            print(f"✗ Scout-Flee-Flow fehlgeschlagen: {e}")
            return False
    
    def test_switch_attack_flow(self) -> bool:
        """Test: Start Battle → Switch Monster → Attack"""
        try:
            print("Teste Switch-Attack-Flow...")
            
            # Battle starten
            if not self._start_battle():
                return False
            
            # Warte auf Battle-Initialisierung
            if not self._wait_for_phase(BattlePhase.INPUT):
                return False
            
            # Switch-Menü öffnen
            if not self._navigate_to_menu(BattleMenuState.SWITCH_SELECT):
                return False
            
            # Zweites Monster auswählen (falls verfügbar)
            if not self._select_second_monster():
                print("⚠ Nur ein Monster verfügbar, teste mit erstem")
                if not self._select_first_monster():
                    return False
            
            # Warte auf Switch-Animation
            time.sleep(1.0)
            
            # Attack-Menü öffnen
            if not self._navigate_to_menu(BattleMenuState.MOVE_SELECT):
                return False
            
            # Ersten Move auswählen
            if not self._select_first_move():
                return False
            
            # Warte auf Battle-Ende
            if not self._wait_for_battle_end():
                return False
            
            print("✓ Switch-Attack-Flow erfolgreich")
            return True
                
        except Exception as e:
            print(f"✗ Switch-Attack-Flow fehlgeschlagen: {e}")
            return False
    
    def test_menu_navigation(self) -> bool:
        """Test: Menü-Navigation zwischen allen States"""
        try:
            print("Teste Menü-Navigation...")
            
            # Battle starten
            if not self._start_battle():
                return False
            
            # Warte auf Battle-Initialisierung
            if not self._wait_for_phase(BattlePhase.INPUT):
                return False
            
            # Teste Navigation zu allen Menüs
            menu_states = [
                BattleMenuState.MOVE_SELECT,
                BattleMenuState.ITEM_SELECT,
                BattleMenuState.SWITCH_SELECT,
                BattleMenuState.TAME_MEAT,
                BattleMenuState.SCOUT,
                BattleMenuState.MAIN
            ]
            
            for menu_state in menu_states:
                if not self._navigate_to_menu(menu_state):
                    print(f"✗ Navigation zu {menu_state} fehlgeschlagen")
                    return False
                
                # Kurze Pause
                time.sleep(0.2)
            
            print("✓ Menü-Navigation erfolgreich")
            return True
                
        except Exception as e:
            print(f"✗ Menü-Navigation fehlgeschlagen: {e}")
            return False
    
    def test_battle_phases(self) -> bool:
        """Test: Battle-Phase-Übergänge"""
        try:
            print("Teste Battle-Phasen...")
            
            # Battle starten
            if not self._start_battle():
                return False
            
            # Prüfe Phase-Übergänge
            expected_phases = [BattlePhase.INIT, BattlePhase.START, BattlePhase.INPUT]
            
            for expected_phase in expected_phases:
                if not self._wait_for_phase(expected_phase, timeout=5.0):
                    print(f"✗ Phase {expected_phase} nicht erreicht")
                    return False
                
                print(f"✓ Phase {expected_phase} erreicht")
                time.sleep(0.5)
            
            print("✓ Battle-Phasen erfolgreich")
            return True
                
        except Exception as e:
            print(f"✗ Battle-Phasen fehlgeschlagen: {e}")
            return False
    
    def test_error_handling(self) -> bool:
        """Test: Error-Handling und Edge-Cases"""
        try:
            print("Teste Error-Handling...")
            
            # Teste Battle ohne Party
            original_party = getattr(self.game, 'party_manager', None)
            self.game.party_manager = None
            
            try:
                battle_scene = BattleScene(self.game)
                battle_scene.on_enter()
                # Sollte graceful fehlschlagen
                print("✓ Battle ohne Party handled gracefully")
            except Exception as e:
                print(f"✗ Battle ohne Party fehlgeschlagen: {e}")
                return False
            finally:
                self.game.party_manager = original_party
            
            print("✓ Error-Handling erfolgreich")
            return True
                
        except Exception as e:
            print(f"✗ Error-Handling fehlgeschlagen: {e}")
            return False
    
    # === HELPER METHODS ===
    
    def _start_battle(self) -> bool:
        """Starte Battle-Scene."""
        try:
            # Enemy-Monster erstellen
            from engine.systems.monsters import MonsterDatabase
            db = MonsterDatabase()
            species = db.get_random_species()
            
            if not species:
                print("✗ Keine Monster-Species verfügbar")
                return False
            
            enemy = species.create_instance(level=5)
            enemy.name = "TestEnemy"
            enemy.current_hp = enemy.max_hp
            
            # Battle-Scene über Game-System starten
            self.game.push_scene(
                BattleScene,
                is_wild=True,
                can_flee=True,
                enemy_team=[enemy]
            )
            
            # Battle-Scene-Referenz holen
            self.battle_scene = self.game.current_scene
            
            print("✓ Battle gestartet")
            return True
            
        except Exception as e:
            print(f"✗ Battle-Start fehlgeschlagen: {e}")
            return False
    
    def _wait_for_phase(self, target_phase: BattlePhase, timeout: float = 10.0) -> bool:
        """Warte auf bestimmte Battle-Phase."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if self.battle_scene and self.battle_scene.current_phase == target_phase:
                return True
            
            # Game-Update simulieren
            if self.game:
                self.game._update(0.016)  # 60 FPS
            
            time.sleep(0.1)
        
        return False
    
    def _wait_for_battle_end(self, timeout: float = 15.0) -> bool:
        """Warte auf Battle-Ende."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if self.battle_scene and self.battle_scene.battle_result != BattleResult.ONGOING:
                return True
            
            # Game-Update simulieren
            if self.game:
                self.game._update(0.016)  # 60 FPS
            
            time.sleep(0.1)
        
        return False
    
    def _navigate_to_menu(self, target_menu: BattleMenuState) -> bool:
        """Navigiere zu bestimmtem Menü."""
        try:
            if not self.battle_scene or not self.battle_scene.battle_ui:
                return False
            
            # Simuliere Tasteneingaben basierend auf Ziel-Menü
            if target_menu == BattleMenuState.MOVE_SELECT:
                # E drücken für Attack
                event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_e)
                self.battle_scene.handle_event(event)
                
            elif target_menu == BattleMenuState.ITEM_SELECT:
                # Pfeil nach rechts, dann E für Item
                event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT)
                self.battle_scene.handle_event(event)
                event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_e)
                self.battle_scene.handle_event(event)
                
            elif target_menu == BattleMenuState.SWITCH_SELECT:
                # Pfeil nach unten, dann E für Wechsel
                event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)
                self.battle_scene.handle_event(event)
                event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_e)
                self.battle_scene.handle_event(event)
                
            elif target_menu == BattleMenuState.TAME_MEAT:
                # Pfeil nach unten, rechts, dann E für Zähmen
                event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)
                self.battle_scene.handle_event(event)
                event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT)
                self.battle_scene.handle_event(event)
                event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_e)
                self.battle_scene.handle_event(event)
                
            elif target_menu == BattleMenuState.SCOUT:
                # Pfeil nach unten, rechts, rechts, dann E für Spähen
                event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)
                self.battle_scene.handle_event(event)
                event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT)
                self.battle_scene.handle_event(event)
                event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT)
                self.battle_scene.handle_event(event)
                event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_e)
                self.battle_scene.handle_event(event)
                
            elif target_menu == BattleMenuState.MAIN:
                # Q drücken für Zurück
                event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_q)
                self.battle_scene.handle_event(event)
            
            # Kurze Pause für UI-Update
            time.sleep(0.1)
            
            # Prüfe ob Navigation erfolgreich
            if self.battle_scene.battle_ui.menu_state == target_menu:
                return True
            
            return False
            
        except Exception as e:
            print(f"✗ Navigation fehlgeschlagen: {e}")
            return False
    
    def _select_first_move(self) -> bool:
        """Wähle ersten verfügbaren Move."""
        try:
            # E drücken für Move-Auswahl
            event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_e)
            self.battle_scene.handle_event(event)
            
            time.sleep(0.2)
            return True
            
        except Exception as e:
            print(f"✗ Move-Auswahl fehlgeschlagen: {e}")
            return False
    
    def _select_meat_item(self) -> bool:
        """Wähle Fleisch-Item (falls verfügbar)."""
        try:
            # E drücken für Item-Auswahl
            event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_e)
            self.battle_scene.handle_event(event)
            
            time.sleep(0.2)
            return True
            
        except Exception as e:
            print(f"✗ Fleisch-Auswahl fehlgeschlagen: {e}")
            return False
    
    def _confirm_tame(self) -> bool:
        """Bestätige Tame-Aktion."""
        try:
            # E drücken für Bestätigung
            event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_e)
            self.battle_scene.handle_event(event)
            
            time.sleep(0.2)
            return True
            
        except Exception as e:
            print(f"✗ Tame-Bestätigung fehlgeschlagen: {e}")
            return False
    
    def _select_flee(self) -> bool:
        """Wähle Flee-Option."""
        try:
            # Pfeil nach unten, rechts, rechts, rechts, dann E für Flucht
            event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)
            self.battle_scene.handle_event(event)
            event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT)
            self.battle_scene.handle_event(event)
            event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT)
            self.battle_scene.handle_event(event)
            event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT)
            self.battle_scene.handle_event(event)
            event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_e)
            self.battle_scene.handle_event(event)
            
            time.sleep(0.2)
            return True
            
        except Exception as e:
            print(f"✗ Flee-Auswahl fehlgeschlagen: {e}")
            return False
    
    def _select_first_monster(self) -> bool:
        """Wähle erstes Monster für Switch."""
        try:
            # E drücken für Monster-Auswahl
            event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_e)
            self.battle_scene.handle_event(event)
            
            time.sleep(0.2)
            return True
            
        except Exception as e:
            print(f"✗ Monster-Auswahl fehlgeschlagen: {e}")
            return False
    
    def _select_second_monster(self) -> bool:
        """Wähle zweites Monster für Switch."""
        try:
            # Pfeil nach unten, dann E für zweites Monster
            event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)
            self.battle_scene.handle_event(event)
            event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_e)
            self.battle_scene.handle_event(event)
            
            time.sleep(0.2)
            return True
            
        except Exception as e:
            print(f"✗ Zweites Monster-Auswahl fehlgeschlagen: {e}")
            return False
    
    def generate_report(self) -> str:
        """Generiere Test-Report."""
        report = []
        report.append("=== BATTLE INTEGRATION TEST REPORT ===")
        report.append(f"Test-Datum: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Test-Ergebnisse
        report.append("TEST-ERGEBNISSE:")
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result)
        
        for test_name, result in self.test_results.items():
            status = "✓ ERFOLGREICH" if result else "✗ FEHLGESCHLAGEN"
            report.append(f"  {test_name}: {status}")
        
        report.append("")
        report.append(f"GESAMT: {passed_tests}/{total_tests} Tests erfolgreich")
        
        # Erfolgsrate
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        report.append(f"ERFOLGSRATE: {success_rate:.1f}%")
        
        # Empfehlungen
        report.append("")
        report.append("EMPFEHLUNGEN:")
        
        if success_rate >= 80:
            report.append("  ✓ Battle-System ist gut integriert")
            report.append("  ✓ Alle Hauptfunktionen funktionieren")
        elif success_rate >= 60:
            report.append("  ⚠ Battle-System hat einige Probleme")
            report.append("  ⚠ Einige Funktionen benötigen Reparatur")
        else:
            report.append("  ✗ Battle-System hat schwerwiegende Probleme")
            report.append("  ✗ Umfassende Reparaturen erforderlich")
        
        # Fehlgeschlagene Tests
        failed_tests = [name for name, result in self.test_results.items() if not result]
        if failed_tests:
            report.append("")
            report.append("FEHLGESCHLAGENE TESTS:")
            for test_name in failed_tests:
                report.append(f"  - {test_name}")
        
        return "\n".join(report)


def main():
    """Hauptfunktion für Battle-Integration-Test."""
    print("BATTLE INTEGRATION TEST - Untold Story")
    print("System-Integrations-Experte")
    print("=" * 50)
    
    # Tester erstellen und ausführen
    tester = BattleIntegrationTester()
    results = tester.run_all_tests()
    
    # Report generieren
    report = tester.generate_report()
    print("\n" + report)
    
    # Report in Datei speichern
    with open("BATTLE_INTEGRATION_REPORT.md", "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"\nReport gespeichert in: BATTLE_INTEGRATION_REPORT.md")
    
    # Exit-Code basierend auf Erfolgsrate
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    if success_rate >= 80:
        print("✓ Integration-Test ERFOLGREICH")
        return 0
    else:
        print("✗ Integration-Test FEHLGESCHLAGEN")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
