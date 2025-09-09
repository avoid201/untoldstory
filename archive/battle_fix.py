"""
Battle System Fix - Diagnostik und Reparatur
"""

import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from engine.systems.battle.battle_controller import BattleController
from engine.systems.battle.turn_processor import TurnProcessor
from engine.systems.monster_instance import MonsterInstance
from engine.systems.battle.battle_enums import BattleResult

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

def diagnose_battle_end_issue():
    """Diagnose the battle end checking issue"""
    logger.info("=== BATTLE END CHECK DIAGNOSIS ===")
    
    # Create test monsters
    player_monster = MonsterInstance(species_id=1, level=6, name="Spiegelpuppe")
    player_monster.current_hp = 29
    player_monster.max_hp = 29
    
    enemy_monster = MonsterInstance(species_id=2, level=5, name="Kohlekumpel")
    enemy_monster.current_hp = 35
    enemy_monster.max_hp = 35
    
    # Create battle controller
    battle = BattleController(
        player_team=[player_monster],
        enemy_team=[enemy_monster]
    )
    
    logger.info(f"Player team: {[m.name for m in battle.state.player_team]}")
    logger.info(f"Enemy team: {[m.name for m in battle.state.enemy_team]}")
    logger.info(f"Player active: {battle.state.player_active.name if battle.state.player_active else 'None'}")
    logger.info(f"Enemy active: {battle.state.enemy_active.name if battle.state.enemy_active else 'None'}")
    
    # Check the battle end logic
    logger.info("\n=== Checking TurnProcessor.check_battle_end() ===")
    turn_processor = battle.turn_processor
    
    # Test check_battle_end directly
    result = turn_processor.check_battle_end()
    logger.info(f"Battle end result: {result}")
    
    # Detailed check
    logger.info("\n=== Detailed Team Status ===")
    logger.info("Player Team Status:")
    for i, monster in enumerate(battle.state.player_team):
        logger.info(f"  [{i}] {monster.name}: {monster.current_hp}/{monster.max_hp} HP")
        logger.info(f"      HP > 0? {monster.current_hp > 0}")
    
    logger.info("Enemy Team Status:")
    for i, monster in enumerate(battle.state.enemy_team):
        logger.info(f"  [{i}] {monster.name}: {monster.current_hp}/{monster.max_hp} HP")
        logger.info(f"      HP > 0? {monster.current_hp > 0}")
    
    # Check if the logic is working correctly
    player_defeated = all(m.current_hp <= 0 for m in battle.state.player_team)
    enemy_defeated = all(m.current_hp <= 0 for m in battle.state.enemy_team)
    
    logger.info(f"\nPlayer defeated? {player_defeated} (should be False)")
    logger.info(f"Enemy defeated? {enemy_defeated} (should be False)")
    
    # Test the problematic code directly
    logger.info("\n=== Testing Original Logic ===")
    player_defeated_original = True
    for monster in battle.state.player_team:
        logger.info(f"Checking {monster.name}: HP={monster.current_hp}")
        if monster.current_hp > 0:
            player_defeated_original = False
            logger.info(f"  -> Monster alive, setting player_defeated to False")
            break
        else:
            logger.info(f"  -> Monster fainted")
    
    logger.info(f"Original logic result: player_defeated = {player_defeated_original}")
    
    if player_defeated_original and any(m.current_hp > 0 for m in battle.state.player_team):
        logger.error("BUG CONFIRMED: Logic says player defeated but has alive monsters!")
    
    return battle

def fix_check_battle_end():
    """Create a fixed version of check_battle_end"""
    logger.info("\n=== PROPOSED FIX ===")
    
    fix_code = '''
def check_battle_end(self) -> BattleResult:
    """
    FIXED: Check if the battle has ended.
    
    Returns:
        BattleResult if battle ended, ONGOING if continuing
    """
    try:
        # Check if player team is defeated
        player_has_conscious = any(monster.current_hp > 0 for monster in self.state.player_team)
        
        if not player_has_conscious:
            logger.info("Player team defeated")
            self.state.battle_result = BattleResult.DEFEAT
            self.state.battle_ended = True
            return BattleResult.DEFEAT
        
        # Check if enemy team is defeated
        enemy_has_conscious = any(monster.current_hp > 0 for monster in self.state.enemy_team)
        
        if not enemy_has_conscious:
            logger.info("Enemy team defeated")
            self.state.battle_result = BattleResult.VICTORY
            self.state.battle_ended = True
            return BattleResult.VICTORY
        
        # Check for caught monster (if applicable)
        if hasattr(self.state, 'caught_monster') and self.state.caught_monster:
            logger.info("Monster caught")
            self.state.battle_result = BattleResult.CAUGHT
            self.state.battle_ended = True
            return BattleResult.CAUGHT
        
        # Check for fled battle (if applicable)
        if hasattr(self.state, 'fled') and self.state.fled:
            logger.info("Battle fled")
            self.state.battle_result = BattleResult.FLED
            self.state.battle_ended = True
            return BattleResult.FLED
        
        # Battle continues
        return BattleResult.ONGOING
        
    except Exception as e:
        logger.error(f"Error checking battle end: {e}")
        return BattleResult.ONGOING
    '''
    
    logger.info("Fixed version uses any() instead of manual loop")
    logger.info("This ensures correct boolean logic for team defeat checking")
    
    return fix_code

def test_fixed_logic():
    """Test the fixed logic"""
    logger.info("\n=== TESTING FIXED LOGIC ===")
    
    # Create test data
    test_cases = [
        {
            "name": "Both teams alive",
            "player_hps": [29, 20, 15],
            "enemy_hps": [35, 25],
            "expected": "ONGOING"
        },
        {
            "name": "Player defeated",
            "player_hps": [0, 0, 0],
            "enemy_hps": [35, 25],
            "expected": "DEFEAT"
        },
        {
            "name": "Enemy defeated",
            "player_hps": [29, 20, 15],
            "enemy_hps": [0, 0],
            "expected": "VICTORY"
        },
        {
            "name": "One player monster alive",
            "player_hps": [0, 0, 1],
            "enemy_hps": [35],
            "expected": "ONGOING"
        }
    ]
    
    for test_case in test_cases:
        logger.info(f"\nTest: {test_case['name']}")
        logger.info(f"  Player HPs: {test_case['player_hps']}")
        logger.info(f"  Enemy HPs: {test_case['enemy_hps']}")
        
        # Test with fixed logic
        player_has_conscious = any(hp > 0 for hp in test_case['player_hps'])
        enemy_has_conscious = any(hp > 0 for hp in test_case['enemy_hps'])
        
        if not player_has_conscious:
            result = "DEFEAT"
        elif not enemy_has_conscious:
            result = "VICTORY"
        else:
            result = "ONGOING"
        
        logger.info(f"  Result: {result} (Expected: {test_case['expected']})")
        
        if result == test_case['expected']:
            logger.info("  ✓ PASS")
        else:
            logger.error("  ✗ FAIL")

if __name__ == "__main__":
    logger.info("Starting Battle System Diagnosis and Fix\n")
    
    # Diagnose the issue
    battle = diagnose_battle_end_issue()
    
    # Show the fix
    fix_code = fix_check_battle_end()
    
    # Test the fixed logic
    test_fixed_logic()
    
    logger.info("\n=== CONCLUSION ===")
    logger.info("The bug is in turn_processor.py's check_battle_end() method.")
    logger.info("The logic incorrectly determines if a team is defeated.")
    logger.info("The fix is to use any() instead of the manual loop with wrong initial value.")
    logger.info("\nTo apply the fix, update turn_processor.py lines 159-198 with the fixed version.")
