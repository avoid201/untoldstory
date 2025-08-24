"""
Example: DQM Formula Integration
Shows how to integrate DQM formulas into the existing battle system
"""

import logging
from engine.systems.battle.battle_controller import BattleState
from engine.systems.battle.damage_calc import DamageCalculator
from engine.systems.battle.dqm_integration import enable_dqm_formulas, get_dqm_integration
from engine.systems.battle.turn_logic import TurnOrder
from engine.systems.monster_instance import MonsterInstance
from engine.systems.moves import Move

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_dqm_battle_system():
    """
    Configure the battle system to use DQM formulas.
    """
    # Get the damage calculator instance
    damage_calc = DamageCalculator()
    
    # Enable DQM formulas in the damage pipeline
    enable_dqm_formulas(damage_calc.pipeline)
    
    logger.info("DQM formulas enabled in damage calculation pipeline")
    
    # Get DQM integration instance for additional features
    dqm_integration = get_dqm_integration()
    
    return damage_calc, dqm_integration


def example_damage_calculation():
    """
    Example of damage calculation using DQM formulas.
    """
    logger.info("\n=== DQM Damage Calculation Example ===")
    
    # Create mock monsters
    class MockMonster:
        def __init__(self, name, stats):
            self.name = name
            self.stats = stats
            self.stat_stages = {'atk': 0, 'def': 0, 'mag': 0, 'res': 0, 'spd': 0}
            self.status = None
            self.tension = 0
            self.traits = []
            self.species = type('Species', (), {'types': ['Normal']})()
    
    attacker = MockMonster("Slime Knight", {
        'atk': 120,
        'def': 80,
        'mag': 60,
        'res': 50,
        'spd': 90
    })
    
    defender = MockMonster("Dracky", {
        'atk': 70,
        'def': 60,
        'mag': 95,
        'res': 75,
        'spd': 110
    })
    
    # Create a mock move
    class MockMove:
        def __init__(self, name, power, category):
            self.name = name
            self.power = power
            self.category = category
            self.type = 'Normal'
            self.accuracy = 95
            self.pp = 10
            self.priority = 1
    
    move = MockMove("Slash", 50, 'phys')
    
    # Calculate damage
    damage_calc, _ = setup_dqm_battle_system()
    result = damage_calc.calculate(attacker, defender, move)
    
    logger.info(f"Attack: {attacker.name} uses {move.name} on {defender.name}")
    logger.info(f"Damage dealt: {result.damage}")
    logger.info(f"Critical hit: {result.is_critical}")
    logger.info(f"Modifiers applied: {result.modifiers_applied}")
    
    return result


def example_turn_order():
    """
    Example of turn order calculation using DQM formula.
    """
    logger.info("\n=== DQM Turn Order Example ===")
    
    # Create mock battle actions
    class MockAction:
        def __init__(self, actor_name, speed):
            self.actor = type('Actor', (), {
                'name': actor_name,
                'stats': {'spd': speed},
                'stat_stages': {},
                'status': None
            })()
            self.action_type = 'ATTACK'
            self.priority = 1
        
        def get_speed(self):
            return self.actor.stats['spd']
    
    actions = [
        MockAction("Fast Monster", 120),
        MockAction("Medium Monster", 85),
        MockAction("Slow Monster", 50),
        MockAction("Another Medium", 85),
    ]
    
    # Calculate turn order with DQM formula
    turn_order = TurnOrder(seed=42)  # Fixed seed for consistent example
    for action in actions:
        turn_order.add_action(action)
    
    sorted_actions = turn_order.sort_actions(use_dqm_formula=True)
    
    logger.info("Turn order (with DQM formula - Speed + Random(0-255)):")
    for i, action in enumerate(sorted_actions, 1):
        logger.info(f"  {i}. {action.actor.name} (Speed: {action.actor.stats['spd']})")
    
    return sorted_actions


def example_escape_calculation():
    """
    Example of escape chance calculation.
    """
    logger.info("\n=== DQM Escape Chance Example ===")
    
    _, dqm_integration = setup_dqm_battle_system()
    
    # Create mock monsters
    class MockMonster:
        def __init__(self, name, speed):
            self.name = name
            self.stats = {'spd': speed}
    
    runner = MockMonster("Player's Slime", 75)
    enemy = MockMonster("Wild Dragon", 100)
    
    # Calculate escape chances
    attempts = [0, 1, 2, 3]
    for attempt in attempts:
        chance = dqm_integration.calculate_escape_chance(runner, enemy, attempt)
        logger.info(f"Attempt {attempt + 1}: {chance * 100:.1f}% chance to escape")
    
    return chance


def example_metal_body():
    """
    Example of Metal Body trait (metal slime defense).
    """
    logger.info("\n=== Metal Body Trait Example ===")
    
    class MockMonster:
        def __init__(self, name, stats, traits=None):
            self.name = name
            self.stats = stats
            self.stat_stages = {'atk': 0, 'def': 0, 'mag': 0, 'res': 0, 'spd': 0}
            self.status = None
            self.tension = 0
            self.traits = traits or []
            self.species = type('Species', (), {'types': ['Normal']})()
    
    attacker = MockMonster("Hero", {
        'atk': 200,
        'def': 100,
        'mag': 150,
        'res': 80,
        'spd': 110
    })
    
    # Metal Slime with Metal Body trait
    metal_slime = MockMonster("Metal Slime", {
        'atk': 50,
        'def': 999,  # Extremely high defense
        'mag': 30,
        'res': 999,
        'spd': 150
    }, traits=['Metal Body'])
    
    # Strong attack against metal slime
    class MockMove:
        def __init__(self, name, power):
            self.name = name
            self.power = power
            self.category = 'phys'
            self.type = 'Normal'
            self.accuracy = 95
            self.pp = 10
            self.priority = 1
    
    move = MockMove("Falcon Slash", 80)
    
    damage_calc, _ = setup_dqm_battle_system()
    
    # Need to manually apply Metal Body since it's not in the default pipeline yet
    from engine.systems.battle.dqm_formulas import DQMCalculator
    dqm_calc = DQMCalculator(rng_seed=42)
    
    result = dqm_calc.calculate_damage(
        attacker_stats=attacker.stats,
        defender_stats=metal_slime.stats,
        move_power=move.power,
        is_physical=True,
        defender_traits=metal_slime.traits
    )
    
    logger.info(f"Attack: {attacker.name} uses {move.name} on {metal_slime.name}")
    logger.info(f"Damage dealt: {result.damage} (Metal Body active!)")
    logger.info(f"Is metal slime damage: {result.is_metal_slime_damage}")
    
    return result


def example_rewards():
    """
    Example of experience and gold calculation.
    """
    logger.info("\n=== DQM Rewards Example ===")
    
    _, dqm_integration = setup_dqm_battle_system()
    
    # Mock defeated enemy
    class MockEnemy:
        def __init__(self, name, level, rank, is_boss=False):
            self.name = name
            self.level = level
            self.rank = rank
            self.is_boss = is_boss
    
    enemies = [
        MockEnemy("Slime", 5, 'F'),
        MockEnemy("Dracky", 10, 'E'),
        MockEnemy("Golem", 20, 'C'),
        MockEnemy("Dragon Lord", 50, 'S', is_boss=True),
    ]
    
    for enemy in enemies:
        rewards = dqm_integration.calculate_rewards(
            enemy, 
            is_boss=enemy.is_boss,
            party_size=3  # Party of 3 monsters
        )
        
        logger.info(f"\nDefeated: {enemy.name} (Lv.{enemy.level}, Rank {enemy.rank})")
        if enemy.is_boss:
            logger.info("  [BOSS BATTLE]")
        logger.info(f"  EXP per monster: {rewards['exp']}")
        logger.info(f"  Gold earned: {rewards['gold']}")
    
    return rewards


def main():
    """
    Run all examples.
    """
    logger.info("=" * 60)
    logger.info("DQM FORMULA INTEGRATION EXAMPLES")
    logger.info("=" * 60)
    
    # Run examples
    example_damage_calculation()
    example_turn_order()
    example_escape_calculation()
    example_metal_body()
    example_rewards()
    
    logger.info("\n" + "=" * 60)
    logger.info("All examples completed successfully!")
    logger.info("DQM formulas are ready for integration into the battle system.")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
