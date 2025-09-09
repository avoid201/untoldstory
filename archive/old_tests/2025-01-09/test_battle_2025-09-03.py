
import pygame
pygame.init()

from engine.core.game import Game
from engine.systems.monster_instance import MonsterInstance
from engine.systems.monsters import MonsterDatabase

# Erstelle Test-Monster
db = MonsterDatabase()
species = db.get_species_by_id(1)  # Glutstummel

if species:
    player_monster = species.create_instance(level=5)
    player_monster.name = "Test-Monster"
    enemy_monster = species.create_instance(level=4)
    enemy_monster.name = "Gegner"
    
    print(f"[TEST] Player: {player_monster.name} mit {len(player_monster.moves)} Moves")
    print(f"[TEST] Enemy: {enemy_monster.name}")
    
    # Zeige erste Moves
    if player_monster.moves:
        for i, move in enumerate(player_monster.moves[:3]):
            print(f"  Move {i}: {move.name if hasattr(move, 'name') else move}")
else:
    print("[TEST] Konnte keine Monster erstellen!")

pygame.quit()
