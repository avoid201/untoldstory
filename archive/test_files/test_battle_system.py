#!/usr/bin/env python3
"""
Battle System Test Script for Untold Story
Tests the complete battle system integration after refactoring
"""

import sys
import os
import pygame
import logging

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_battle_system():
    """Test the complete battle system."""
    print("\n" + "="*60)
    print("UNTOLD STORY - BATTLE SYSTEM TEST")
    print("="*60 + "\n")
    
    try:
        # Initialize pygame
        print("1. Initializing pygame...")
        pygame.init()
        screen = pygame.display.set_mode((640, 360))
        logical_surface = pygame.Surface((320, 180))
        pygame.display.set_caption("Battle System Test")
        
        # Import game components
        print("2. Importing game components...")
        from engine.core.game import Game
        from engine.scenes.battle_scene import BattleScene
        from engine.systems.monster_instance import MonsterInstance
        from engine.systems.monsters import MonsterSpecies, MonsterRank
        
        # Create game instance
        print("3. Creating game instance...")
        game = Game(
            screen=screen,
            logical_surface=logical_surface,
            logical_size=(320, 180),
            window_size=(640, 360),
            scale_factor=2
        )
        
        # Create test monsters
        print("4. Creating test monsters...")
        
        # Create player monster
        player_species = MonsterSpecies(
            id="test_slime",
            name="Test Slime",
            types=["water"],
            base_stats={
                'hp': 100,
                'atk': 50,
                'def': 40,
                'mag': 45,
                'res': 35,
                'spd': 60
            },
            rank=MonsterRank.D,
            description="A test slime for battle testing"
        )
        
        player_monster = MonsterInstance(
            species=player_species,
            level=10,
            nickname="Testy"
        )
        
        # Ensure monster has moves
        from engine.systems.moves import Move, MoveCategory, MoveTarget, MoveEffect, EffectKind
        tackle = Move(
            id="tackle",
            name="Tackle",
            type="Normal",
            category=MoveCategory.PHYSICAL,
            power=40,
            accuracy=100,
            priority=0,
            targeting=MoveTarget.ENEMY,
            effects=[MoveEffect(kind=EffectKind.DAMAGE, power=40)],
            description="A basic tackle attack"
        )
        player_monster.moves = [tackle]
        
        print(f"   Player Monster: {player_monster.name} Lv.{player_monster.level}")
        print(f"   HP: {player_monster.current_hp}/{player_monster.max_hp}")
        
        # Create enemy monster
        enemy_species = MonsterSpecies(
            id="test_dragon",
            name="Test Dragon",
            types=["fire"],
            base_stats={
                'hp': 80,
                'atk': 60,
                'def': 35,
                'mag': 55,
                'res': 40,
                'spd': 50
            },
            rank=MonsterRank.C,
            description="A test dragon for battle testing"
        )
        
        enemy_monster = MonsterInstance(
            species=enemy_species,
            level=8,
            nickname="Enemy"
        )
        enemy_monster.moves = [tackle]
        
        print(f"   Enemy Monster: {enemy_monster.name} Lv.{enemy_monster.level}")
        print(f"   HP: {enemy_monster.current_hp}/{enemy_monster.max_hp}")
        
        # Initialize Battle Scene
        print("\n5. Initializing Battle Scene...")
        battle_scene = BattleScene(game)
        
        # Start battle
        print("6. Starting battle...")
        battle_scene.on_enter(
            player_team=[player_monster],
            enemy_team=[enemy_monster],
            is_wild=True,
            can_flee=True
        )
        
        # Check battle state
        print("\n7. Checking battle state...")
        if battle_scene.battle_state:
            print("   ✓ Battle state created")
            print(f"   Player active: {battle_scene.battle_state.player_active.name if battle_scene.battle_state.player_active else 'None'}")
            print(f"   Enemy active: {battle_scene.battle_state.enemy_active.name if battle_scene.battle_state.enemy_active else 'None'}")
        else:
            print("   ✗ Battle state not created!")
            return False
        
        # Check battle controller
        print("\n8. Checking battle controller...")
        if battle_scene.battle_controller:
            print("   ✓ Battle controller created")
            state = battle_scene.battle_controller.get_battle_state()
            print(f"   Phase: {state.get('phase', 'Unknown')}")
            print(f"   Turn: {state.get('turn', 0)}")
        else:
            print("   ✗ Battle controller not created!")
            return False
        
        # Check processors
        print("\n9. Checking battle processors...")
        processors = [
            ('turn_processor', battle_scene.turn_processor),
            ('action_processor', battle_scene.action_processor),
            ('event_processor', battle_scene.event_processor),
            ('status_processor', battle_scene.status_processor)
        ]
        
        all_processors_ok = True
        for name, processor in processors:
            if processor:
                print(f"   ✓ {name} initialized")
            else:
                print(f"   ✗ {name} not initialized!")
                all_processors_ok = False
        
        # Check UI
        print("\n10. Checking battle UI...")
        if battle_scene.battle_ui:
            print("   ✓ Battle UI created")
            if hasattr(battle_scene.battle_ui, 'battle_state'):
                print("   ✓ UI connected to battle state")
            else:
                print("   ✗ UI not connected to battle state!")
        else:
            print("   ✗ Battle UI not created!")
            return False
        
        # Test AI action generation
        print("\n11. Testing AI action generation...")
        if battle_scene.battle_ai:
            enemy_action = battle_scene.battle_ai.choose_action(
                enemy_monster,
                player_monster,
                battle_scene.battle_state
            )
            if enemy_action:
                print(f"   ✓ AI generated action: {enemy_action.get('type', 'unknown')}")
                if 'move' in enemy_action and hasattr(enemy_action['move'], 'name'):
                    print(f"   Move: {enemy_action['move'].name}")
            else:
                print("   ✗ AI failed to generate action!")
        else:
            print("   ✗ Battle AI not initialized!")
        
        # Test reward system
        print("\n12. Testing reward system...")
        if battle_scene.reward_system:
            # Simulate victory
            enemy_monster.current_hp = 0
            enemy_monster.is_fainted = True
            
            rewards = battle_scene.reward_system.calculate_battle_rewards(
                battle_scene.battle_state,
                'normal'
            )
            
            if rewards:
                print(f"   ✓ Rewards calculated")
                print(f"   Money: {rewards.money_gained}")
                print(f"   EXP distribution: {len(rewards.exp_gained)} recipients")
            else:
                print("   ✗ Reward calculation failed!")
        else:
            print("   ✗ Reward system not initialized!")
        
        # Test event system
        print("\n13. Testing event system...")
        if battle_scene.event_processor:
            from engine.systems.battle.event_processor import BattleEvent, EventType
            
            # Create test event
            test_event = BattleEvent(
                event_type=EventType.MESSAGE_SHOW,
                data={'message': 'Test message'}
            )
            
            battle_scene.event_processor.queue_event(test_event)
            
            if battle_scene.event_processor.has_pending_events():
                print("   ✓ Event added to queue")
                events = battle_scene.event_processor.process_events()
                print(f"   Processed {len(events)} events")
            else:
                print("   ✗ Event not added to queue!")
        
        # Final summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        if all([
            battle_scene.battle_state,
            battle_scene.battle_controller,
            all_processors_ok,
            battle_scene.battle_ui,
            battle_scene.battle_ai,
            battle_scene.reward_system,
            battle_scene.event_processor
        ]):
            print("\n✅ ALL SYSTEMS OPERATIONAL!")
            print("The battle system is ready for use.")
            return True
        else:
            print("\n❌ SOME SYSTEMS FAILED!")
            print("Please check the errors above.")
            return False
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        pygame.quit()

if __name__ == "__main__":
    success = test_battle_system()
    sys.exit(0 if success else 1)
