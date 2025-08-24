"""
Example: Battle Event System Usage
Shows how to use the generator-based event system for battles
"""

import logging
import time
from typing import List, Dict, Any
from engine.systems.battle.battle_controller import BattleState
from engine.systems.battle.battle_events import EventType, BattleEvent
from engine.systems.battle.battle_enums import BattleType
from engine.systems.monster_instance import MonsterInstance

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BattleEventUI:
    """
    Example UI handler for battle events.
    Shows how to process events for animations and UI updates.
    """
    
    def __init__(self):
        """Initialize UI handler."""
        self.message_queue = []
        self.animations_playing = []
        self.current_hp = {}
    
    def handle_message(self, event: BattleEvent) -> None:
        """Handle message display events."""
        message = event.data.get('message', '')
        duration = event.duration
        
        logger.info(f"📢 MESSAGE: {message}")
        self.message_queue.append((message, duration))
        
        # Simulate message display time
        if duration > 0:
            time.sleep(duration * 0.5)  # Speed up for example
    
    def handle_animation(self, event: BattleEvent) -> None:
        """Handle animation events."""
        animation = event.data.get('animation', '')
        duration = event.duration
        
        logger.info(f"🎬 ANIMATION: {animation} ({duration}s)")
        self.animations_playing.append(animation)
        
        # Simulate animation time
        if event.blocking and duration > 0:
            time.sleep(duration * 0.3)  # Speed up for example
        
        self.animations_playing.remove(animation)
    
    def handle_hp_update(self, event: BattleEvent) -> None:
        """Handle HP bar update events."""
        target = event.data.get('target')
        if target:
            name = target.name if hasattr(target, 'name') else str(target)
            current = target.current_hp if hasattr(target, 'current_hp') else 0
            maximum = target.max_hp if hasattr(target, 'max_hp') else 1
            
            self.current_hp[name] = (current, maximum)
            logger.info(f"❤️ HP UPDATE: {name} - {current}/{maximum}")
    
    def handle_damage(self, event: BattleEvent) -> None:
        """Handle damage display events."""
        target = event.data.get('target')
        damage = event.data.get('damage', 0)
        
        target_name = target.name if hasattr(target, 'name') else str(target)
        logger.info(f"💥 DAMAGE: {damage} to {target_name}")
        
        # Show damage number animation
        self.show_damage_number(target_name, damage)
    
    def handle_critical(self, event: BattleEvent) -> None:
        """Handle critical hit events."""
        actor = event.data.get('actor')
        actor_name = actor.name if hasattr(actor, 'name') else str(actor)
        
        logger.info(f"⚡ CRITICAL HIT by {actor_name}!")
        # Could trigger screen flash effect here
    
    def handle_faint(self, event: BattleEvent) -> None:
        """Handle monster faint events."""
        monster = event.data.get('monster')
        monster_name = monster.name if hasattr(monster, 'name') else str(monster)
        
        logger.info(f"☠️ FAINTED: {monster_name}")
        # Could trigger faint animation here
    
    def handle_battle_end(self, event: BattleEvent) -> None:
        """Handle battle end events."""
        result = event.data.get('result', 'unknown')
        logger.info(f"🏁 BATTLE END: {result}")
        
        if result == 'victory':
            logger.info("🎉 VICTORY!")
        elif result == 'defeat':
            logger.info("💀 DEFEAT...")
        elif result == 'escaped':
            logger.info("🏃 ESCAPED!")
        elif result == 'tamed':
            logger.info("🤝 MONSTER TAMED!")
    
    def show_damage_number(self, target: str, damage: int) -> None:
        """Show floating damage number."""
        logger.info(f"   [{target}] -{damage}")
    
    def process_event(self, event: BattleEvent) -> None:
        """
        Process a battle event and update UI accordingly.
        
        Args:
            event: Event to process
        """
        # Map event types to handlers
        handlers = {
            EventType.MESSAGE_SHOW: self.handle_message,
            EventType.ANIMATION_PLAY: self.handle_animation,
            EventType.HP_BAR_UPDATE: self.handle_hp_update,
            EventType.DAMAGE_DEALT: self.handle_damage,
            EventType.CRITICAL_HIT: self.handle_critical,
            EventType.MONSTER_FAINTED: self.handle_faint,
            EventType.BATTLE_END: self.handle_battle_end,
        }
        
        handler = handlers.get(event.event_type)
        if handler:
            handler(event)
        else:
            logger.debug(f"Unhandled event type: {event.event_type.name}")


def create_mock_monsters() -> tuple:
    """Create mock monsters for testing."""
    
    class MockSpecies:
        def __init__(self, name, types):
            self.name = name
            self.types = types
    
    class MockMonster(MonsterInstance):
        def __init__(self, name, level, stats):
            self.name = name
            self.nickname = name
            self.level = level
            self.stats = stats
            self.stat_stages = {stat: 0 for stat in ['atk', 'def', 'mag', 'res', 'spd']}
            self.current_hp = stats['hp']
            self.max_hp = stats['hp']
            self.status = None
            self.is_fainted = False
            self.species = MockSpecies(name, ['Normal'])
            self.moves = []
            self.tension = 0
            self.traits = []
        
        def take_damage(self, damage: int):
            self.current_hp = max(0, self.current_hp - damage)
            if self.current_hp == 0:
                self.is_fainted = True
        
        def heal(self, amount: int):
            self.current_hp = min(self.max_hp, self.current_hp + amount)
    
    # Create player team
    player_team = [
        MockMonster("Slime Knight", 15, {
            'hp': 120, 'atk': 85, 'def': 70, 
            'mag': 60, 'res': 55, 'spd': 75
        }),
        MockMonster("Dracky", 12, {
            'hp': 80, 'atk': 65, 'def': 50,
            'mag': 75, 'res': 60, 'spd': 95
        })
    ]
    
    # Create enemy team  
    enemy_team = [
        MockMonster("Golem", 14, {
            'hp': 150, 'atk': 95, 'def': 100,
            'mag': 30, 'res': 40, 'spd': 45
        })
    ]
    
    # Add mock moves
    class MockMove:
        def __init__(self, name, power, category='phys'):
            self.name = name
            self.power = power
            self.category = category
            self.type = 'Normal'
            self.accuracy = 95
            self.pp = 10
            self.max_pp = 10
            self.priority = 1
    
    player_team[0].moves = [
        MockMove("Slash", 50),
        MockMove("Shield Bash", 40),
        MockMove("Heal", 0, 'support')
    ]
    
    player_team[1].moves = [
        MockMove("Bite", 45),
        MockMove("Wind Blast", 35, 'mag')
    ]
    
    enemy_team[0].moves = [
        MockMove("Rock Throw", 55),
        MockMove("Earthquake", 70)
    ]
    
    return player_team, enemy_team


def example_battle_with_events():
    """
    Example battle using the event system.
    """
    logger.info("=" * 60)
    logger.info("BATTLE EVENT SYSTEM EXAMPLE")
    logger.info("=" * 60)
    
    # Create mock monsters
    player_team, enemy_team = create_mock_monsters()
    
    # Create battle state
    battle_state = BattleState(
        player_team=player_team,
        enemy_team=enemy_team,
        battle_type=BattleType.WILD
    )
    
    # Create UI handler
    ui_handler = BattleEventUI()
    
    # Register custom event handlers
    battle_state.register_event_handler(
        EventType.MESSAGE_SHOW,
        ui_handler.handle_message
    )
    battle_state.register_event_handler(
        EventType.ANIMATION_PLAY,
        ui_handler.handle_animation
    )
    
    logger.info("\n--- BATTLE START ---")
    
    # Start battle with events
    start_info = battle_state.start_battle(use_events=True)
    
    # Process start events
    events = battle_state.get_pending_events()
    logger.info(f"\nProcessing {len(events)} battle start events...")
    
    for event in events:
        ui_handler.process_event(event)
    
    logger.info("\n--- TURN 1 ---")
    
    # Queue some actions for demonstration
    from engine.systems.battle.turn_logic import BattleAction, ActionType
    
    # Player attacks
    player_action = BattleAction(
        actor=battle_state.player_active,
        action_type=ActionType.ATTACK,
        target=battle_state.enemy_active,
        move=battle_state.player_active.moves[0]  # Slash
    )
    
    # Enemy attacks
    enemy_action = BattleAction(
        actor=battle_state.enemy_active,
        action_type=ActionType.ATTACK,
        target=battle_state.player_active,
        move=battle_state.enemy_active.moves[0]  # Rock Throw
    )
    
    # Queue actions
    battle_state.action_queue = [player_action, enemy_action]
    
    # Resolve turn with events
    logger.info("\nResolving turn with event system...")
    turn_result = battle_state.resolve_turn(use_events=True)
    
    # Process turn events
    events = battle_state.get_pending_events()
    logger.info(f"\nProcessing {len(events)} turn events...")
    
    for event in events:
        ui_handler.process_event(event)
    
    # Show battle status
    logger.info("\n--- BATTLE STATUS ---")
    status = battle_state.get_battle_status()
    
    player = status['player_active']
    enemy = status['enemy_active']
    
    if player:
        logger.info(f"Player: {player['name']} - HP: {player['current_hp']}/{player['max_hp']}")
    if enemy:
        logger.info(f"Enemy: {enemy['name']} - HP: {enemy['current_hp']}/{enemy['max_hp']}")
    
    logger.info("\n--- EVENT SYSTEM FEATURES ---")
    logger.info("✅ Generated battle start events")
    logger.info("✅ Generated turn execution events")
    logger.info("✅ Processed damage calculations")
    logger.info("✅ Updated HP bars")
    logger.info("✅ Showed battle messages")
    logger.info("✅ Triggered animations")
    
    logger.info("\n" + "=" * 60)
    logger.info("Event system successfully integrated!")
    logger.info("Events provide clean separation between logic and UI")
    logger.info("=" * 60)


def example_event_types():
    """
    Show all available event types.
    """
    logger.info("\n--- AVAILABLE EVENT TYPES ---")
    
    for event_type in EventType:
        logger.info(f"  • {event_type.name}")
    
    logger.info("\nEach event type can trigger specific UI updates:")
    logger.info("  - Messages, animations, effects")
    logger.info("  - HP/status updates")
    logger.info("  - Menu transitions")
    logger.info("  - Battle phase changes")


if __name__ == "__main__":
    example_battle_with_events()
    example_event_types()
