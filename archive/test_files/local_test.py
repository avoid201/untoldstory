#!/usr/bin/env python3
"""
Lokaler Battle System Test
Einfach auszuführen ohne komplexe Setups
"""

import sys
import os

# Pfad hinzufügen
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    try:
        # Teste Battle System
        from engine.systems.battle.battle import BattleState, BattleType
        from engine.systems.monster_instance import MonsterInstance, MonsterSpecies, MonsterRank
        from engine.systems.stats import BaseStats, GrowthCurve
        from engine.systems.moves import Move, MoveEffect, EffectKind, MoveCategory, MoveTarget
        
        print("✅ Imports erfolgreich")
        
        # Erstelle Test-Monster
        base_stats = BaseStats(hp=100, atk=50, def_=50, mag=30, res=30, spd=70)
        species = MonsterSpecies(
            id=1, name="TestMonster", era="present", rank=MonsterRank.E,
            types=["Bestie"], base_stats=base_stats, growth_curve=GrowthCurve.MEDIUM_FAST,
            base_exp_yield=64, capture_rate=45, traits=[], talents=[],
            evolution=None, description="Test"
        )
        
        player = MonsterInstance(species=species, level=5)
        enemy = MonsterInstance(species=species, level=5)
        
        # Erstelle Moves
        effect = MoveEffect(kind=EffectKind.DAMAGE, power=40, chance=100.0)
        move = Move(
            id="tackle", name="Tackle", type="Bestie", category=MoveCategory.PHYSICAL,
            power=40, accuracy=95, pp=15, max_pp=15, priority=0,
            targeting=MoveTarget.ENEMY, effects=[effect], description="Attack"
        )
        
        player.moves = [move]
        enemy.moves = [move]
        
        print(f"✅ Monster erstellt: {player.name} vs {enemy.name}")
        
        # Erstelle Battle
        battle = BattleState(
            player_team=[player],
            enemy_team=[enemy],
            battle_type=BattleType.WILD
        )
        
        print(f"✅ Battle erstellt (Phase: {battle.phase.value})")
        
        # Starte Battle
        battle.start_battle()
        print(f"✅ Battle gestartet (Phase: {battle.phase.value})")
        
        # Teste Action
        action = {
            'action_type': 'attack',
            'actor': player,
            'move': player.moves[0],
            'target': enemy
        }
        
        if battle.queue_player_action(action):
            print("✅ Action erfolgreich hinzugefügt")
            
            # Löse Turn auf
            result = battle.resolve_turn()
            if 'error' not in result:
                print(f"✅ Turn aufgelöst (Turn: {result['turn_count']})")
                print(f"   Spieler HP: {player.current_hp}/{player.max_hp}")
                print(f"   Gegner HP: {enemy.current_hp}/{enemy.max_hp}")
            else:
                print(f"❌ Turn Fehler: {result['error']}")
        else:
            print("❌ Action fehlgeschlagen")
        
        print("🎉 BATTLE SYSTEM FUNKTIONIERT!")
        
    except Exception as e:
        print(f"❌ Fehler: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

