#!/usr/bin/env python3
"""
Test-Skript für das erweiterte Battle System
Testet alle implementierten Features
"""

import pygame
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.scenes.battle_scene import BattleScene
from engine.systems.monster_instance import MonsterInstance
from engine.systems.items import Inventory, ItemRegistry
from engine.ui.dqm_battle_ui import DQMBattleUI
import random

class TestMonster:
    """Test-Monster für Battle-Tests"""
    def __init__(self, name, level=5, types=None):
        self.name = name
        self.level = level
        self.types = types or ['Normal']
        self.max_hp = 50 + level * 10
        self.current_hp = self.max_hp
        self.rank = random.choice(['F', 'E', 'D', 'C', 'B', 'A'])
        self.status = None
        self.id = f"test_{name}_{random.randint(1000, 9999)}"
        
        # Stats
        self.stats = {
            'atk': 40 + level * 2,
            'def': 30 + level * 2,
            'mag': 35 + level * 2,
            'res': 30 + level * 2,
            'spd': 30 + level * 3,
            'acc': 100,
            'eva': 10
        }
        
        # Moves
        self.moves = self._generate_moves()
        
        # Experience
        self.exp = 0
        self.experience = 0
    
    def _generate_moves(self):
        """Generiere Test-Moves"""
        moves = []
        
        # Basic Attack
        move1 = type('Move', (), {
            'id': 'tackle',
            'name': 'Tackle',
            'power': 40,
            'type': 'Normal',
            'accuracy': 100,
            'current_pp': 35,
            'max_pp': 35
        })()
        moves.append(move1)
        
        # Type-specific move
        if 'Feuer' in self.types:
            move2 = type('Move', (), {
                'id': 'feuerball',
                'name': 'Feuerball',
                'power': 60,
                'type': 'Feuer',
                'accuracy': 95,
                'current_pp': 25,
                'max_pp': 25
            })()
            moves.append(move2)
        elif 'Wasser' in self.types:
            move2 = type('Move', (), {
                'id': 'wasserstrahl',
                'name': 'Wasserstrahl',
                'power': 60,
                'type': 'Wasser',
                'accuracy': 95,
                'current_pp': 25,
                'max_pp': 25
            })()
            moves.append(move2)
        elif 'Pflanze' in self.types:
            move2 = type('Move', (), {
                'id': 'rankenhieb',
                'name': 'Rankenhieb',
                'power': 60,
                'type': 'Pflanze',
                'accuracy': 95,
                'current_pp': 25,
                'max_pp': 25
            })()
            moves.append(move2)
        
        # Strong move
        move3 = type('Move', (), {
            'id': 'power_strike',
            'name': 'Power Strike',
            'power': 80,
            'type': self.types[0] if self.types else 'Normal',
            'accuracy': 85,
            'current_pp': 10,
            'max_pp': 10
        })()
        moves.append(move3)
        
        # Status move
        move4 = type('Move', (), {
            'id': 'growl',
            'name': 'Knurren',
            'power': 0,
            'type': 'Normal',
            'accuracy': 100,
            'current_pp': 40,
            'max_pp': 40
        })()
        moves.append(move4)
        
        return moves
    
    def gain_exp(self, amount):
        """Füge EXP hinzu"""
        self.exp += amount
        self.experience += amount
        
        # Simple level up
        exp_needed = self.level * 100
        while self.exp >= exp_needed:
            self.exp -= exp_needed
            self.level += 1
            old_hp = self.max_hp
            self.max_hp = 50 + self.level * 10
            self.current_hp += (self.max_hp - old_hp)
            print(f"{self.name} erreicht Level {self.level}!")
            exp_needed = self.level * 100

class TestGame:
    """Minimales Game-Objekt für Tests"""
    def __init__(self):
        pygame.init()
        
        # Display
        self.screen = pygame.display.set_mode((1280, 720))
        pygame.display.set_caption("Battle System Test")
        self.logical_size = (320, 180)
        
        # Clock
        self.clock = pygame.time.Clock()
        self.running = True
        self.debug_mode = True
        
        # Scenes
        self.scene_stack = []
        self.current_scene = None
        
        # Inventory
        self.inventory = Inventory()
        self.inventory.add_item('trank', 5)
        self.inventory.add_item('supertrank', 2)
        self.inventory.add_item('fleisch', 3)
        self.inventory.add_item('gegengift', 2)
        self.inventory.add_money(1000)
        
        # Player money
        self.player_money = 1000
        
        # Party Manager Mock
        self.party_manager = type('PartyManager', (), {
            'party': type('Party', (), {
                'members': [],
                'get_conscious_members': lambda: [],
                'get_all_members': lambda: [],
                'heal_all': lambda: None
            })(),
            'add_to_party': lambda monster: (True, f"{monster.name} wurde dem Team hinzugefügt!")
        })()
    
    def push_scene(self, scene_class, kwargs=None):
        """Füge neue Scene hinzu"""
        scene = scene_class(self)
        if kwargs:
            scene.on_enter(**kwargs)
        else:
            scene.on_enter()
        self.scene_stack.append(scene)
        self.current_scene = scene
    
    def pop_scene(self):
        """Entferne aktuelle Scene"""
        if self.scene_stack:
            scene = self.scene_stack.pop()
            if hasattr(scene, 'on_exit'):
                scene.on_exit()
            
            if self.scene_stack:
                self.current_scene = self.scene_stack[-1]
            else:
                self.current_scene = None
                self.running = False

def run_battle_test(test_type="wild"):
    """Führe Battle-Test aus"""
    game = TestGame()
    
    # Erstelle Test-Teams
    if test_type == "wild":
        # Wilder Kampf
        player_team = [
            TestMonster("Glumanda", level=10, types=['Feuer']),
            TestMonster("Schiggy", level=9, types=['Wasser'])
        ]
        enemy_team = [
            TestMonster("Bisasam", level=8, types=['Pflanze'])
        ]
        
        print("\n=== WILDER KAMPF TEST ===")
        print("Spieler-Team:")
        for m in player_team:
            print(f"  - {m.name} Lv.{m.level} ({', '.join(m.types)})")
        print("Gegner:")
        for m in enemy_team:
            print(f"  - {m.name} Lv.{m.level} ({', '.join(m.types)})")
        print("\nSteuerung:")
        print("  - Pfeiltasten/WASD: Navigation")
        print("  - Enter/Space: Bestätigen")
        print("  - ESC/Q: Zurück")
        print("\nMenü-Optionen:")
        print("  1. Angreifen - AI wählt besten Move")
        print("  2. Skill - Wähle Move manuell")
        print("  3. Zähmen - Versuche Monster zu fangen")
        print("  4. Verteidigen - +50% DEF")
        print("  5. Fliehen - Fluchtversuch")
        
        game.push_scene(BattleScene, {
            'player_team': player_team,
            'enemy_team': enemy_team,
            'is_wild': True,
            'can_flee': True,
            'background': 'grass'
        })
    
    elif test_type == "trainer":
        # Trainer-Kampf
        player_team = [
            TestMonster("Glurak", level=15, types=['Feuer', 'Luft']),
            TestMonster("Turtok", level=14, types=['Wasser']),
            TestMonster("Bisaflor", level=14, types=['Pflanze', 'Gift'])
        ]
        enemy_team = [
            TestMonster("Pikachu", level=13, types=['Energie']),
            TestMonster("Relaxo", level=15, types=['Normal'])
        ]
        
        print("\n=== TRAINER-KAMPF TEST ===")
        print("Spieler-Team:")
        for m in player_team:
            print(f"  - {m.name} Lv.{m.level} ({', '.join(m.types)})")
        print("Gegner-Team:")
        for m in enemy_team:
            print(f"  - {m.name} Lv.{m.level} ({', '.join(m.types)})")
        print("\nHinweis: In Trainer-Kämpfen kannst du nicht fliehen oder zähmen!")
        print("Stattdessen gibt es Items im 3. Menüpunkt.")
        
        game.push_scene(BattleScene, {
            'player_team': player_team,
            'enemy_team': enemy_team,
            'is_wild': False,
            'can_flee': False,
            'trainer_name': 'Rivale Gary',
            'background': 'arena'
        })
    
    elif test_type == "boss":
        # Boss-Kampf
        player_team = [
            TestMonster("Mega-Glurak", level=25, types=['Feuer', 'Teufel']),
            TestMonster("Mega-Turtok", level=24, types=['Wasser', 'Eis']),
            TestMonster("Mega-Bisaflor", level=24, types=['Pflanze', 'Erde'])
        ]
        enemy_team = [
            TestMonster("Boss-Drache", level=30, types=['Teufel', 'Feuer']),
        ]
        enemy_team[0].max_hp = 300
        enemy_team[0].current_hp = 300
        enemy_team[0].rank = 'X'
        
        print("\n=== BOSS-KAMPF TEST ===")
        print("Spieler-Team:")
        for m in player_team:
            print(f"  - {m.name} Lv.{m.level} ({', '.join(m.types)})")
        print("Boss:")
        for m in enemy_team:
            print(f"  - {m.name} Lv.{m.level} HP:{m.current_hp} Rang:{m.rank}")
        print("\nBoss-Kämpfe geben doppelte Belohnungen!")
        
        game.push_scene(BattleScene, {
            'player_team': player_team,
            'enemy_team': enemy_team,
            'is_wild': False,
            'can_flee': False,
            'trainer_name': 'Boss-Meister',
            'is_boss': True,
            'background': 'boss_arena'
        })
    
    # Game Loop
    while game.running and game.scene_stack:
        dt = game.clock.tick(60) / 1000.0
        
        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_F12:
                game.running = False
            elif game.current_scene:
                game.current_scene.handle_event(event)
        
        # Update
        if game.current_scene:
            game.current_scene.update(dt)
        
        # Draw
        game.screen.fill((0, 0, 0))
        if game.current_scene:
            # Scale logical size to screen
            temp_surface = pygame.Surface(game.logical_size)
            game.current_scene.draw(temp_surface)
            scaled = pygame.transform.scale(temp_surface, (1280, 720))
            game.screen.blit(scaled, (0, 0))
        
        # FPS Display
        fps = int(game.clock.get_fps())
        font = pygame.font.Font(None, 20)
        fps_text = font.render(f"FPS: {fps}", True, (255, 255, 0))
        game.screen.blit(fps_text, (10, 10))
        
        # Instructions
        inst_text = font.render("F12: Beenden | Debug-Mode aktiviert", True, (255, 255, 0))
        game.screen.blit(inst_text, (10, 30))
        
        pygame.display.flip()
    
    pygame.quit()
    print("\nTest beendet!")

if __name__ == "__main__":
    print("=" * 60)
    print("BATTLE SYSTEM TEST")
    print("=" * 60)
    print("\nWähle Test-Typ:")
    print("1. Wilder Kampf (mit Zähmen und Fliehen)")
    print("2. Trainer-Kampf (mit Items)")
    print("3. Boss-Kampf (erhöhte Belohnungen)")
    print("Q. Beenden")
    
    while True:
        choice = input("\nAuswahl (1/2/3/Q): ").strip().upper()
        
        if choice == '1':
            run_battle_test("wild")
        elif choice == '2':
            run_battle_test("trainer")
        elif choice == '3':
            run_battle_test("boss")
        elif choice == 'Q':
            print("Test beendet.")
            break
        else:
            print("Ungültige Auswahl!")
