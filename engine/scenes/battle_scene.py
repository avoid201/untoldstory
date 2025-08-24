"""
Battle Scene for Untold Story.
Manages the flow of turn-based battles with full UI integration.
"""

import pygame
import random
import os
from typing import Optional, List, Dict, Any
from enum import Enum, auto

from engine.core.scene_base import Scene
from engine.core.config import Colors, GameState
from engine.ui.battle_ui import BattleUI, BattleMenuState
from engine.systems.battle.battle_controller import BattleState, BattlePhase, BattleType
from engine.systems.battle.turn_logic import TurnOrder
from engine.systems.battle.battle_ai import BattleAI
from engine.systems.monster_instance import MonsterInstance
from engine.systems.battle.command_collection import (
    CommandCollector, CommandPhase, CommandType, MonsterCommand
)
# from engine.ui.transitions import TransitionType  # Temporarily disabled

# Import our new simplified battle manager
try:
    from engine.systems.battle.core.battle_manager import SimpleBattleManager, BattlePhase as SimpleBattlePhase, BattleResult as SimpleBattleResult
    from engine.systems.battle.actions.dqm_damage_calc import DQMDamageCalculator
    USE_SIMPLE_BATTLE = True
except ImportError:
    print("WARNING: SimpleBattleManager not found, using legacy system")
    USE_SIMPLE_BATTLE = False


class BattleResult(Enum):
    """Possible battle outcomes."""
    ONGOING = auto()
    VICTORY = auto()
    DEFEAT = auto()
    FLED = auto()
    CAUGHT = auto()


class BattleScene(Scene):
    """Main battle scene managing combat flow."""
    
    def __init__(self, game):
        super().__init__(game)
        
        # Battle components
        self.battle_ui = BattleUI(game)
        self.battle_state: Optional[BattleState] = None
        self.turn_order: Optional[TurnOrder] = None
        self.battle_ai = BattleAI()
        self.command_collector: Optional[CommandCollector] = None
        
        # Use simplified battle manager if available
        if USE_SIMPLE_BATTLE:
            self.simple_battle = SimpleBattleManager(game)
            self.damage_calc = DQMDamageCalculator()
        else:
            self.simple_battle = None
            self.damage_calc = None
        
        # Battle configuration
        self.is_wild = False
        self.is_boss = False
        self.can_flee = True
        self.battle_bg = None  # Background type
        
        # Turn state
        self.current_phase = BattlePhase.INIT
        self.action_queue: List[Dict] = []
        self.pending_actions: Dict[str, Dict] = {}
        self.turn_count = 0
        self.collected_commands: Dict[str, MonsterCommand] = {}
        self.commands_collected = False
        
        # Animation & timing
        self.phase_timer = 0
        self.animation_timer = 0
        self.waiting_for_input = False
        self.battle_result = BattleResult.ONGOING
        
        # Rewards
        self.exp_gained = 0
        self.items_gained = []
        self.money_gained = 0
        
        # Track caught monster
        self.caught_monster = None
        
        # Monster sprites cache
        self.monster_sprites = {}
        
    def on_enter(self, **kwargs):
        """Initialize battle from kwargs."""
        try:
            # Reset battle result
            self.battle_result = BattleResult.ONGOING
            
            # Use simplified battle if available
            if USE_SIMPLE_BATTLE and self.simple_battle:
            
            # Get player team from party manager - CRITICAL FIX!
            if not kwargs.get('player_team'):
                # Use actual party monsters
                if not hasattr(self.game, 'party_manager') or not self.game.party_manager:
                    print("ERROR: Kein Party Manager verfügbar!")
                    self.game.pop_scene()
                    return
                
                player_team = self.game.party_manager.party.get_conscious_members()
                
                # Check if party has any conscious monsters
                if not player_team:
                    print("ERROR: Keine kampffähigen Monster im Team!")
                    self.game.pop_scene()
                    return
            else:
                player_team = kwargs.get('player_team', [])
            
            # Validierung des Spieler-Teams
            if not isinstance(player_team, list) or len(player_team) == 0:
                print("ERROR: Ungültiges Spieler-Team!")
                self.game.pop_scene()
                return
            
            # Überprüfe jedes Monster im Team
            valid_player_team = []
            for monster in player_team:
                if monster and hasattr(monster, 'current_hp') and monster.current_hp > 0:
                    valid_player_team.append(monster)
                else:
                    print(f"WARNING: Monster {getattr(monster, 'name', 'Unknown')} ist besiegt oder ungültig!")
            
            if not valid_player_team:
                print("ERROR: Keine kampffähigen Monster im Spieler-Team!")
                self.game.pop_scene()
                return
            
            player_team = valid_player_team
            
            # Get enemy team
            enemy_team = kwargs.get('enemy_team', [])
            if not enemy_team:
                print("ERROR: Kein Gegner-Team angegeben!")
                self.game.pop_scene()
                return
            
            # Überprüfe jedes Monster im Gegner-Team
            valid_enemy_team = []
            for monster in enemy_team:
                if monster and hasattr(monster, 'current_hp') and monster.current_hp > 0:
                    valid_enemy_team.append(monster)
                else:
                    print(f"WARNING: Gegner-Monster {getattr(monster, 'name', 'Unknown')} ist besiegt oder ungültig!")
            
            if not valid_enemy_team:
                print("ERROR: Keine gültigen Monster im Gegner-Team!")
                self.game.pop_scene()
                return
            
            enemy_team = valid_enemy_team
            
            # Battle configuration
            self.is_wild = kwargs.get('is_wild', True)
            self.is_boss = kwargs.get('is_boss', False)
            self.can_flee = kwargs.get('can_flee', True) and self.is_wild
            self.battle_bg = kwargs.get('background', 'grass')
            
            # Trainer info if applicable
            self.trainer_name = kwargs.get('trainer_name', None)
            
            print(f"Battle initialisiert: {len(player_team)} vs {len(enemy_team)} Monster")
            print(f"Can flee: {self.can_flee}, Is wild: {self.is_wild}")
            
        except Exception as e:
            print(f"KRITISCHER FEHLER bei der Battle-Initialisierung: {str(e)}")
            self.game.pop_scene()
            return
        
        # Initialize battle state with actual party
        battle_type = BattleType.WILD if self.is_wild else BattleType.TRAINER
        self.battle_state = BattleState(
            player_team=player_team,
            enemy_team=enemy_team,
            battle_type=battle_type,
            can_flee=self.can_flee,
            can_catch=self.is_wild
        )
        
        # Initialize turn manager
        self.turn_order = TurnOrder()
        
        # Initialize command collector
        self.command_collector = CommandCollector(self.battle_state)
        self.command_collector.set_input_callback(self._get_player_command_callback)
        
        # Initialize UI with monster sprites
        self.battle_ui.init_battle(player_team, enemy_team)
        
        # Get monster sprites from sprite manager
        self._init_monster_sprites(player_team, enemy_team)
        
        # Reset battle vars
        self.turn_count = 0
        self.action_queue.clear()
        self.pending_actions.clear()
        self.caught_monster = None
        
        # Start intro phase
        self.current_phase = BattlePhase.INIT
        self.phase_timer = 0
        self.waiting_for_input = False
        
        # Show intro message
        if self.is_wild:
            monster_name = enemy_team[0].name if enemy_team and hasattr(enemy_team[0], 'name') else "???"
            self.battle_ui.add_message(f"Ein wildes {monster_name} erscheint!")
        
        # Set UI to main menu state
        self.battle_ui.menu_state = BattleMenuState.MAIN
        print("Battle Scene initialisiert - Intro Phase")
    
    def _init_monster_sprites(self, player_team: List, enemy_team: List) -> None:
        """Initialize monster sprites from sprite manager."""
        # Wenn bereits geflohen, keine Sprites mehr initialisieren
        if self.battle_result != BattleResult.ONGOING:
            return
        
        # Die BattleUI verwaltet bereits die Monster-Sprites
        # Hier müssen wir nichts mehr tun, da die BattleUI.init_battle() bereits aufgerufen wurde
        print(f"Monster sprites will be managed by BattleUI")
        print(f"Player team size: {len(player_team)}")
        print(f"Enemy team size: {len(enemy_team)}")
    
    def _load_monster_sprite(self, monster) -> pygame.Surface:
        """Load the actual monster sprite from the monsters directory."""
        # Wenn bereits geflohen, keine Sprites mehr laden
        if self.battle_result != BattleResult.ONGOING:
            return None
        
        try:
            # Get monster ID
            monster_id = getattr(monster, 'species_id', getattr(monster, 'id', 'Unknown'))
            
            # Load monster sprite
            sprite_path = os.path.join("sprites", "monsters", f"{monster_id}.png")
            if os.path.exists(sprite_path):
                try:
                    monster_sprite = pygame.image.load(sprite_path).convert_alpha()
                    if monster_sprite:
                        # Scale to 16x16 if needed
                        if monster_sprite.get_size() != (16, 16):
                            monster_sprite = pygame.transform.scale(monster_sprite, (16, 16))
                        self.monster_sprites[monster_id] = monster_sprite
                        print(f"Monster sprite loaded: {sprite_path}")
                        return monster_sprite
                    else:
                        print(f"Failed to load monster sprite: {sprite_path}")
                except Exception as e:
                    print(f"Error loading monster sprite {sprite_path}: {e}")
            else:
                print(f"Monster sprite not found: {sprite_path}")
            
            return None
            
        except Exception as e:
            print(f"Error in _load_monster_sprite: {e}")
            return None
    
    def _create_fallback_sprite(self, monster) -> pygame.Surface:
        """Create a fallback sprite when monster sprite cannot be loaded."""
        # Wenn bereits geflohen, keine Fallback-Sprites mehr erstellen
        if self.battle_result != BattleResult.ONGOING:
            return None
        
        # Create a simple colored circle as fallback
        size = 16
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Use monster type color or default
        try:
            if hasattr(monster, 'type') and monster.type:
                type_colors = {
                    'fire': (255, 100, 100),
                    'water': (100, 100, 255),
                    'grass': (100, 255, 100),
                    'electric': (255, 255, 100),
                    'ice': (200, 200, 255),
                    'fighting': (255, 150, 100),
                    'poison': (200, 100, 200),
                    'ground': (200, 150, 100),
                    'flying': (200, 200, 255),
                    'psychic': (255, 100, 200),
                    'bug': (200, 255, 100),
                    'rock': (150, 150, 100)
                }
                color = type_colors.get(monster.type, (150, 150, 150))
            else:
                color = (150, 150, 150)  # Default gray
        except:
            color = (150, 150, 150)  # Default gray
        
        pygame.draw.circle(surface, color, (size//2, size//2), size//2 - 2)
        pygame.draw.circle(surface, tuple(max(0, c - 50) for c in color), (size//2, size//2), size//2 - 4, 2)
        
        return surface
    
    def on_exit(self):
        """Clean up battle scene and apply battle results."""
        # Update party with battle results (nur wenn nicht geflohen)
        if self.battle_result != BattleResult.FLED:
            self._sync_party_after_battle()
        
        # Handle caught monster
        if self.caught_monster:
            self._finalize_caught_monster()
        
        # Handle defeat
        if self.battle_result == BattleResult.DEFEAT:
            self._handle_defeat()
        
        # Stop battle music and return to field music
        # self.game.audio.stop_bgm()
    
    def _sync_party_after_battle(self):
        """Sync party monsters with battle state changes."""
        # Wenn geflohen, keine Party-Synchronisation nötig
        if self.battle_result == BattleResult.FLED:
            print("Player fled - no party sync needed")
            return
        
        # Update party monsters with battle changes (HP, EXP, status, new moves)
        for i, battle_monster in enumerate(self.battle_state.player_team):
            if battle_monster and i < len(self.game.party_manager.party.members):
                party_monster = self.game.party_manager.party.members[i]
                if party_monster and party_monster.id == battle_monster.id:
                    # Sync HP and status
                    party_monster.current_hp = battle_monster.current_hp
                    party_monster.status = battle_monster.status
                    
                    # Sync EXP and level
                    party_monster.experience = battle_monster.experience
                    party_monster.level = battle_monster.level
                    
                    # Sync PP for moves
                    party_monster.moves = battle_monster.moves
                    
                    # Sync any new moves learned
                    if hasattr(battle_monster, 'new_moves_learned'):
                        for move_id in battle_monster.new_moves_learned:
                            party_monster.learn_move(move_id)
    
    def _finalize_caught_monster(self):
        """Add caught monster to party or storage."""
        # Wenn geflohen, kein Monster gefangen
        if self.battle_result == BattleResult.FLED:
            print("Player fled - no monster caught")
            return
        
        if self.caught_monster:
            success, message = self.game.party_manager.add_to_party(self.caught_monster)
            print(f"Monster caught: {message}")
    
    def _handle_defeat(self):
        """Handle player defeat."""
        # Wenn geflohen, keine Niederlage
        if self.battle_result == BattleResult.FLED:
            print("Player fled - no defeat handling needed")
            return
        
        # Heal party and return to last heal point
        self.game.party_manager.party.heal_all()
        
        # Set player position to last heal point
        if hasattr(self.game, 'last_heal_point'):
            # Return to last saved position
            pass
        else:
            # Return to player house as default
            self.game.current_map = 'player_house'
            self.game.player_pos = (5, 5)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle input events - SIMPLIFIED."""
        try:
            if event.type == pygame.KEYDOWN:
                # Map keys to actions
                action = None
                
                if event.key in [pygame.K_e, pygame.K_RETURN, pygame.K_SPACE]:
                    action = 'confirm'
                elif event.key in [pygame.K_q, pygame.K_ESCAPE]:
                    action = 'back'
                elif event.key == pygame.K_w:
                    action = 'up'
                elif event.key == pygame.K_s:
                    action = 'down'
                elif event.key == pygame.K_a:
                    action = 'left'
                elif event.key == pygame.K_d:
                    action = 'right'
                
                if action:
                    print(f"Battle Input: {action}")
                    
                                        # Handle based on phase
                    if self.current_phase == BattlePhase.INPUT:
                        # Get UI action
                        player_action = self.battle_ui.handle_input(action, self.battle_state)
                        
                        if player_action:
                            print(f"Player action: {player_action}")
                            
                            # Check action type and process
                            action_type = player_action.get('action')
                            
                            if action_type == 'attack':
                                # Attack action - execute immediately
                                print("DEBUG: Processing attack action")
                                self._execute_simple_attack(player_action)
                            elif action_type == 'flee':
                                # Flee action
                                print("DEBUG: Processing flee action")
                                self._execute_flee(player_action.get('actor'), player_action)
                            elif action_type in ['tame', 'scout', 'item', 'switch']:
                                # Special actions
                                print("DEBUG: Processing special action")
                                self._execute_special_action(player_action)
                            elif action_type == 'menu_select':
                                # Just menu navigation
                                print("DEBUG: Menu navigation")
                                pass
                            else:
                                print(f"DEBUG: Unknown action type: {action_type}")
                    elif self.current_phase in [BattlePhase.INIT, BattlePhase.MESSAGE]:
                        # Skip to input phase
                        self.current_phase = BattlePhase.INPUT
                        self.waiting_for_input = True
                
                return True
            
            return False
            
        except Exception as e:
            print(f"Error in handle_event: {e}")
            return False
    
    def _process_player_action(self, player_action: dict):
        """Process player action from UI."""
        try:
            action_type = player_action.get('action')
            
            if action_type == 'flee':
                # Execute flee immediately
                self._execute_flee(player_action.get('actor'), player_action)
                
            elif action_type == 'attack':
                # Reset menu after attack selection
                self.battle_ui.menu_state = BattleMenuState.MAIN
                # Execute attack
                self._execute_simple_attack(player_action)
                
            elif action_type in ['tame', 'scout', 'item', 'switch']:
                # Reset menu
                self.battle_ui.menu_state = BattleMenuState.MAIN
                # Execute special action
                self._execute_special_action(player_action)
                
            elif action_type == 'menu_select':
                # Menu navigation handled by UI
                pass
                
            elif action_type == 'cancel':
                # Cancel - return to main menu
                self.battle_ui.menu_state = BattleMenuState.MAIN
                
        except Exception as e:
            print(f"Error processing action: {e}")
    
    def _execute_simple_attack(self, action: dict):
        """Execute a simple attack with proper feedback."""
        try:
            print(f"DEBUG: _execute_simple_attack called with action: {action.get('action')}")
            
            actor = action.get('actor')
            target = action.get('target')
            move = action.get('move')
            
            if not actor or not target:
                print("DEBUG: Missing actor or target")
                return
            
            print(f"DEBUG: {actor.name} attacking {target.name}")
            
            # Show attack message
            move_name = move.name if hasattr(move, 'name') else "Tackle"
            self.battle_ui.add_message(f"{actor.name} uses {move_name}!")
            print(f"DEBUG: Attack message added")
            
            # Calculate damage
            if hasattr(self.battle_state, 'calculate_dqm_damage'):
                result = self.battle_state.calculate_dqm_damage(actor, target, move or {'power': 40, 'category': 'phys'})
                damage = result.get('final_damage', 10)
            else:
                # Simple damage calc
                damage = 10 + actor.level * 2
            
            print(f"DEBUG: Calculated damage: {damage}")
            
            # Apply damage
            old_hp = target.current_hp
            target.current_hp = max(0, target.current_hp - damage)
            
            print(f"DEBUG: {target.name} HP: {old_hp} -> {target.current_hp}")
            
            # Update UI and show damage
            self.battle_ui.add_message(f"{target.name} takes {damage} damage!")
            self.battle_ui.add_message(f"{target.name}: {target.current_hp}/{target.max_hp} HP")
            
            # Check if target fainted
            if target.current_hp <= 0:
                target.is_fainted = True
                self.battle_ui.add_message(f"{target.name} fainted!")
                print(f"DEBUG: {target.name} fainted!")
                
                # Check battle end
                if target == self.battle_state.enemy_active:
                    self.battle_ui.add_message("Victory! You won the battle!")
                    self.battle_result = BattleResult.VICTORY
                    self.current_phase = BattlePhase.END
                    # Set timer to auto-exit
                    self.phase_timer = 0
                    print("DEBUG: Victory condition met")
                elif target == self.battle_state.player_active:
                    self.battle_ui.add_message("Defeat! You lost the battle!")
                    self.battle_result = BattleResult.DEFEAT
                    self.current_phase = BattlePhase.END
                    self.phase_timer = 0
                    print("DEBUG: Defeat condition met")
            else:
                print(f"DEBUG: {target.name} still alive, HP: {target.current_hp}")
                # Enemy turn if target still alive
                if target == self.battle_state.enemy_active:
                    print("DEBUG: Enemy's turn")
                    self._execute_enemy_turn()
                
        except Exception as e:
            print(f"ERROR in _execute_simple_attack: {e}")
            import traceback
            traceback.print_exc()

    def _execute_enemy_turn(self):
        """Simple enemy turn."""
        try:
            enemy = self.battle_state.enemy_active
            player = self.battle_state.player_active
            
            if not enemy or enemy.is_fainted or not player or player.is_fainted:
                return
            
            # Simple damage
            damage = 5 + enemy.level
            player.current_hp = max(0, player.current_hp - damage)
            
            self.battle_ui.add_message(f"{enemy.name} attacks for {damage} damage!")
            
            if player.current_hp <= 0:
                player.is_fainted = True
                self.battle_ui.add_message(f"{player.name} fainted!")
                self.battle_result = BattleResult.DEFEAT
                self.current_phase = BattlePhase.END
                
        except Exception as e:
            print(f"Error in enemy turn: {e}")
    
    def _execute_special_action(self, action: dict):
        """Execute special actions."""
        action_type = action.get('action')
        actor = action.get('actor')
        
        if action_type == 'tame':
            self.battle_ui.add_message("Taming not yet implemented!")
        elif action_type == 'scout':
            self.battle_ui.add_message(f"{self.battle_state.enemy_active.name}: HP {self.battle_state.enemy_active.current_hp}/{self.battle_state.enemy_active.max_hp}")
        elif action_type == 'item':
            self.battle_ui.add_message("Items not yet implemented!")
        elif action_type == 'switch':
            self.battle_ui.add_message("Switch not yet implemented!")

    def update(self, dt: float) -> None:
        """Update battle logic."""
        # Sicherheitsprüfung: battle_state muss existieren
        if not hasattr(self, 'battle_state') or self.battle_state is None:
            print("WARNING: battle_state is None, initializing...")
            self.on_enter()
            return
        
        # Überprüfe battle_result - wenn nicht mehr ONGOING, beende den Kampf
        if self.battle_result != BattleResult.ONGOING:
            self.current_phase = BattlePhase.END
            self.phase_timer = 0
            print(f"Battle ending due to result: {self.battle_result.name}")
            return
        
        # Update phase timer
        self.phase_timer += dt
        
        # Update current phase
        if self.current_phase == BattlePhase.INIT:
            self._update_intro_phase(dt)
        elif self.current_phase == BattlePhase.INPUT:
            self._update_input_phase(dt)
        elif self.current_phase == BattlePhase.RESOLVE:
            self._update_execution_phase(dt)
        elif self.current_phase == BattlePhase.AFTERMATH:
            self._update_aftermath_phase(dt)
        elif self.current_phase == BattlePhase.END:
            self._update_end_phase(dt)
    
    def _update_intro_phase(self, dt: float):
        """Handle intro animations and messages."""
        # Wenn bereits geflohen, direkt zur END-Phase
        if self.battle_result != BattleResult.ONGOING:
            self.current_phase = BattlePhase.END
            self.phase_timer = 0
            print("Battle ending due to result - moving to END phase")
            return
        
        # Shorter intro, immediately go to input
        if self.phase_timer > 0.5:  # 0.5 seconds intro
            self.current_phase = BattlePhase.INPUT
            self.waiting_for_input = True
            print("Intro phase complete - waiting for input")
    
    def _update_input_phase(self, dt: float):
        """Handle player input phase - SIMPLIFIED."""
        # Wenn bereits geflohen, direkt zur END-Phase
        if self.battle_result != BattleResult.ONGOING:
            self.current_phase = BattlePhase.END
            self.phase_timer = 0
            print("Battle ending due to result - moving to END phase")
            return
        
        # Just wait for player input through handle_event
        # No automatic command collection
        self.waiting_for_input = True
    
    def _update_execution_phase(self, dt: float):
        """Handle action execution phase."""
        # Wenn bereits geflohen, direkt zur END-Phase
        if self.battle_result != BattleResult.ONGOING:
            self.current_phase = BattlePhase.END
            self.phase_timer = 0
            print("Battle ending due to result - moving to END phase")
            return
        
        # Execute turn if actions are ready
        if self._all_actions_ready():
            self._execute_turn()
        else:
            # Wait for more actions
            pass
    
    def _update_aftermath_phase(self, dt: float):
        """Handle end-of-turn effects."""
        # Wenn bereits geflohen, direkt zur END-Phase
        if self.battle_result != BattleResult.ONGOING:
            self.current_phase = BattlePhase.END
            self.phase_timer = 0
            print("Battle ending due to result - moving to END phase")
            return
        
        # Process status effects, weather, etc.
        if self.phase_timer > 1.0:  # 1 second aftermath
            # Reset command collection for next turn
            self.commands_collected = False
            self.collected_commands.clear()
            
            # Check if battle should continue
            if self.battle_state.is_valid():
                self.current_phase = BattlePhase.INPUT
                self.waiting_for_input = True
                print("Aftermath complete - waiting for input")
            else:
                self.current_phase = BattlePhase.END
                print("Battle ending")
    
    def _update_end_phase(self, dt: float):
        """Handle battle end and return to overworld."""
        # Show results briefly then return
        if self.phase_timer > 2.0:  # 2 seconds to show result
            print(f"Battle ended with result: {self.battle_result.name}")
            
            # Process rewards if victory
            if self.battle_result == BattleResult.VICTORY:
                # Give EXP (simplified)
                exp_gained = self.battle_state.enemy_active.level * 10
                self.battle_ui.add_message(f"Gained {exp_gained} EXP!")
            
            # Return to overworld
            self._end_battle()
    
    def _next_message(self):
        """Show next message in queue."""
        # Wenn bereits geflohen, direkt zur END-Phase
        if self.battle_result != BattleResult.ONGOING:
            self.current_phase = BattlePhase.END
            self.phase_timer = 0
            print("Battle ending due to result - moving to END phase")
            return
        
        if hasattr(self.battle_ui, 'message_queue') and self.battle_ui.message_queue:
            self.battle_ui._next_message()
        else:
            # No more messages, continue
            if self.current_phase == BattlePhase.MESSAGE:
                self.current_phase = BattlePhase.INPUT
                self.waiting_for_input = True
    
    def _all_actions_ready(self) -> bool:
        """Check if all required actions are ready."""
        # Wenn bereits geflohen, sind keine weiteren Aktionen nötig
        if self.battle_result != BattleResult.ONGOING:
            return True
        
        # For now, just check if player action is ready
        return 'player_0' in self.pending_actions
    
    def _get_player_command_callback(self, monster_id: str, monster: MonsterInstance) -> Dict:
        """Callback for command collector to get player input."""
        # This would normally interface with the UI to get player input
        # For now, return the pending action if available
        if monster_id in self.pending_actions:
            return self.pending_actions[monster_id]
        
        # Default to attack for testing
        return {
            'action': 'attack',
            'target_id': 'enemy_0',
            'move_id': monster.moves[0].id if monster.moves else None
        }
    
    def _execute_turn(self):
        """Execute the current turn with DQM command system."""
        try:
            print("Executing turn with DQM commands...")
            
            # Wenn bereits geflohen, nichts mehr ausführen
            if self.battle_result != BattleResult.ONGOING:
                print("Battle already ended - skipping turn execution")
                return
            
            # Check if we have collected commands
            if self.commands_collected and self.collected_commands:
                # Convert commands to battle actions
                battle_actions = self.command_collector.convert_to_battle_actions()
                
                if battle_actions:
                    print(f"Executing {len(battle_actions)} battle actions")
                    
                    # Queue all actions
                    for action in battle_actions:
                        self.battle_state.action_queue.append(action)
                    
                    # Resolve turn with all actions
                    turn_results = self.battle_state.resolve_turn()
                    print(f"Turn results: {turn_results}")
                    
                    # Reset for next turn
                    self.commands_collected = False
                    self.collected_commands.clear()
                    
                    # Check battle end
                    if not self.battle_state.is_valid():
                        self.current_phase = BattlePhase.END
                        print("Battle ended")
                    else:
                        # Continue to next turn
                        self.current_phase = BattlePhase.AFTERMATH
                        self.phase_timer = 0
                        self.waiting_for_input = True
                        self.pending_actions.clear()
                        print("Turn complete - waiting for next input")
                    return
            
            # Get player action
            player_action = self.pending_actions.get('player_0')
            if not player_action:
                print("No player action found!")
                # Keine Action vorhanden - zurück zum Input
                self.current_phase = BattlePhase.INPUT
                self.waiting_for_input = True
                return
            
            # Verarbeite UI-Aktionen direkt
            if player_action.get('action') == 'menu_select':
                # UI-Aktion wird direkt verarbeitet
                print(f"Processing UI action: {player_action}")
                # Zeige Nachricht an, falls vorhanden
                if 'message' in player_action:
                    self.battle_ui.add_message(player_action['message'])
                
                # Zurück zum Input für weitere Aktionen
                self.current_phase = BattlePhase.INPUT
                self.waiting_for_input = True
                self.pending_actions.clear()
                return
            
            # Normale Battle-Aktion verarbeiten
            battle_action = self._create_battle_action(player_action)
            if battle_action:
                # Queue player action
                success = self.battle_state.queue_player_action(battle_action)
                if success:
                    print("Player action queued successfully")
                    
                    # Resolve turn
                    turn_results = self.battle_state.resolve_turn()
                    print(f"Turn results: {turn_results}")
                    
                    # Check battle end
                    if not self.battle_state.is_valid():
                        self.current_phase = BattlePhase.END
                        print("Battle ended")
                    else:
                        # Continue to next turn
                        self.current_phase = BattlePhase.AFTERMATH
                        self.phase_timer = 0
                        self.waiting_for_input = True
                        self.pending_actions.clear()
                        print("Turn complete - waiting for input")
                else:
                    print("Failed to queue player action")
                    # Reset to input phase
                    self.current_phase = BattlePhase.INPUT
                    self.waiting_for_input = True
            else:
                print("Could not create battle action")
                # Reset to input phase
                self.current_phase = BattlePhase.INPUT
                self.waiting_for_input = True
            
        except Exception as e:
            print(f"Fehler bei der Zugausführung: {str(e)}")
            # Reset to input phase
            self.current_phase = BattlePhase.INPUT
            self.waiting_for_input = True
    
    def _create_battle_action(self, player_action: dict) -> Optional[Dict]:
        """Create a simplified battle action from player input."""
        try:
            action_type = player_action.get('action')
            
            # Handle different action types
            if action_type == 'attack':
                return {
                    'action': 'attack',
                    'actor': player_action.get('actor'),
                    'move': player_action.get('move'),
                    'target': player_action.get('target'),
                    'move_index': player_action.get('move_index', 0)
                }
            elif action_type == 'flee':
                return {
                    'action': 'flee',
                    'actor': player_action.get('actor')
                }
            elif action_type in ['tame', 'scout', 'switch', 'item']:
                return {
                    'action': action_type,
                    'actor': player_action.get('actor')
                }
            elif action_type == 'menu_select':
                # UI action - open submenu
                return None
            elif action_type == 'cancel':
                # Cancel action
                return None
            
            return None
            
        except Exception as e:
            print(f"Error creating battle action: {e}")
            return None
    def _end_battle(self):
        """End the battle and return to field."""
        try:
            print(f"Ending battle with result: {self.battle_result.name}")
            
            # Handle different battle results
            if self.battle_result == BattleResult.FLED:
                print("Player fled from battle")
            elif self.battle_result == BattleResult.CAUGHT:
                print("Monster caught")
                self._finalize_caught_monster()
            elif self.battle_result == BattleResult.DEFEAT:
                print("Player defeated")
                self._handle_defeat()
            elif self.battle_result == BattleResult.VICTORY:
                print("Player victorious")
                # Sync party state
                if hasattr(self, '_sync_party_after_battle'):
                    self._sync_party_after_battle()
            
            # Clear battle state
            self.battle_state = None
            self.battle_result = BattleResult.ONGOING
            
            # Return to field scene
            print("Returning to field scene...")
            self.game.pop_scene()
            
        except Exception as e:
            print(f"Error ending battle: {e}")
            # Force return to field
            self.game.pop_scene()
    
    def _get_active_actors(self) -> List[str]:
        """Get list of actors that can act this turn."""
        # Wenn bereits geflohen, keine Akteure mehr
        if self.battle_result != BattleResult.ONGOING:
            return []
        
        actors = []
        
        # Add player monsters
        for i, monster in enumerate(self.battle_state.player_team):
            if monster and monster.current_hp > 0 and monster.can_act():
                actors.append(f'player_{i}')
        
        # Add enemy monsters
        for i, monster in enumerate(self.battle_state.enemy_team):
            if monster and monster.current_hp > 0 and monster.can_act():
                actors.append(f'enemy_{i}')
        
        return actors
    
    def _get_ai_action(self, actor_id: str) -> Optional[Dict]:
        """Get AI-determined action for an actor."""
        # Wenn bereits geflohen, keine AI-Aktionen mehr
        if self.battle_result != BattleResult.ONGOING:
            return None
        
        # Get the monster
        idx = int(actor_id.split('_')[1])
        monster = self.battle_state.enemy_team[idx]
        
        if not monster or monster.current_hp <= 0:
            return None
        
        # Use AI to determine action
        action = self.battle_ai.choose_action(
            monster,
            self.battle_state.enemy_team,
            self.battle_state.player_team,
            self.battle_state
        )
        
        # Add actor ID
        if action:
            action['actor'] = actor_id
        
        return action
    
    def _execute_action(self, action: Dict):
        """Execute a single action."""
        # Wenn bereits geflohen, nichts mehr ausführen
        if self.battle_result != BattleResult.ONGOING:
            print("Battle already ended - skipping action execution")
            return
        
        actor_id = action['actor']
        action_type = action['type']
        
        # Get actor monster
        if actor_id.startswith('player'):
            idx = int(actor_id.split('_')[1])
            actor = self.battle_state.player_team[idx]
        else:
            idx = int(actor_id.split('_')[1])
            actor = self.battle_state.enemy_team[idx]
        
        if not actor or actor.current_hp <= 0:
            return
        
        # Execute based on type
        if action_type == 'attack':
            self._execute_attack(actor, action)
        elif action_type == 'tame':
            self._execute_tame(actor, action)
        elif action_type == 'item':
            self._execute_item(actor, action)
        elif action_type == 'flee':
            # Fliehen wird direkt in _execute_flee behandelt
            # Hier sollte es nicht mehr ankommen
            print("Warning: Flee action reached _execute_action - this should not happen")
            pass
    
    def _execute_attack(self, actor: MonsterInstance, action: Dict):
        """Execute an attack action."""
        # Wenn bereits geflohen, nichts mehr ausführen
        if self.battle_result != BattleResult.ONGOING:
            print("Battle already ended - skipping attack execution")
            return
        
        move_id = action['move_id']
        targets = action.get('targets', [])
        
        # Get move data
        move_data = self.game.resources.get_move(move_id)
        if not move_data:
            return
        
        # Show attack message
        self.battle_ui.add_message(
            f"{actor.nickname or actor.species_name} setzt {move_data.name} ein!"
        )
        
        # Execute against each target
        for target_id in targets:
            # Get target monster
            if target_id.startswith('player'):
                idx = int(target_id.split('_')[1])
                target = self.battle_state.player_team[idx]
            else:
                idx = int(target_id.split('_')[1])
                target = self.battle_state.enemy_team[idx]
            
            if not target or target.current_hp <= 0:
                continue
            
            # Calculate damage
            result = self.turn_manager.execute_move(
                actor, target, move_data, self.battle_state
            )
            
            # Apply damage
            if result['hit']:
                damage = result.get('damage', 0)
                if damage > 0:
                    target.current_hp = max(0, target.current_hp - damage)
                    
                    # Update UI
                    self.battle_ui.set_hp(target_id, target.current_hp)
                    self.battle_ui.shake_sprite(target_id)
                    
                    # Show damage message
                    effectiveness = result.get('effectiveness', 1.0)
                    if effectiveness > 1.5:
                        self.battle_ui.add_message("Volltreffer! Richtig effektiv!")
                    elif effectiveness > 1.0:
                        self.battle_ui.add_message("Effektiv!")
                    elif effectiveness < 0.5:
                        self.battle_ui.add_message("Kaum Wirkung...")
                    elif effectiveness < 1.0:
                        self.battle_ui.add_message("Nicht sehr effektiv...")
                    
                    # Check if critical
                    if result.get('critical'):
                        self.battle_ui.add_message("Kritischer Treffer!")
                
                # Apply status effects
                if result.get('status'):
                    target.status = result['status']
                    self.battle_ui.add_message(
                        f"{target.nickname or target.species_name} hat jetzt {result['status']}!"
                    )
            else:
                self.battle_ui.add_message("Daneben!")
    
    def _execute_tame(self, actor: MonsterInstance, action: Dict):
        """Execute a taming attempt."""
        # Wenn bereits geflohen, nichts mehr ausführen
        if self.battle_result != BattleResult.ONGOING:
            print("Battle already ended - skipping tame execution")
            return
        
        # Only works on wild monsters
        if not self.is_wild:
            self.battle_ui.add_message("Kannst du knicken bei Trainer-Monstern!")
            return
        
        # Get target (first enemy)
        target = self.battle_state.enemy_team[0] if self.battle_state.enemy_team else None
        if not target:
            return
        
        # Calculate taming chance
        from engine.systems.taming import calculate_tame_chance
        chance = calculate_tame_chance(
            target,
            self.battle_state.player_team,
            self.battle_state
        )
        
        # Show chance
        self.battle_ui.add_message(f"Zähm-Chance: {int(chance * 100)}%")
        
        # Roll for success
        if random.random() < chance:
            # Success!
            self.battle_ui.add_message(f"{target.species_name} wurde gezähmt!")
            self.battle_result = BattleResult.CAUGHT
            
            # Store caught monster for later processing
            self.caught_monster = target
            
            # Show where it goes
            if len(self.game.party_manager.party.get_all_members()) < 6:
                self.battle_ui.add_message(f"{target.species_name} kommt in dein Team!")
            else:
                current_box = self.game.party_manager.storage.get_current_box()
                box_name = current_box.name if current_box else "Box"
                self.battle_ui.add_message(f"{target.species_name} wurde in {box_name} gepackt!")
        else:
            # Failed
            self.battle_ui.add_message("Mist! Hat nicht geklappt!")
            
            # Apply irritation
            if not hasattr(target, 'buffs'):
                target.buffs = []
            target.buffs.append({
                'type': 'irritated',
                'duration': -1
            })
    
    def _execute_item(self, actor: MonsterInstance, action: Dict):
        """Execute item use."""
        # Wenn bereits geflohen, nichts mehr ausführen
        if self.battle_result != BattleResult.ONGOING:
            print("Battle already ended - skipping item execution")
            return
        
        item_id = action.get('item_id')
        target_id = action.get('target')
        
        # Get item from inventory
        if hasattr(self.game, 'inventory'):
            item = self.game.inventory.get_item(item_id)
            if item:
                # Use item effect
                if item.type == 'healing':
                    # Heal target
                    if target_id.startswith('player'):
                        idx = int(target_id.split('_')[1])
                        target = self.battle_state.player_team[idx]
                        if target:
                            heal_amount = item.value
                            target.current_hp = min(target.max_hp, target.current_hp + heal_amount)
                            self.battle_ui.set_hp(target_id, target.current_hp)
                            self.battle_ui.add_message(
                                f"{target.nickname or target.species_name} wurde um {heal_amount} HP geheilt!"
                            )
                
                # Remove item from inventory
                self.game.inventory.remove_item(item_id, 1)
            else:
                self.battle_ui.add_message("Item nicht gefunden!")
        else:
            self.battle_ui.add_message("Items sind noch nicht implementiert!")
    
    def _execute_flee(self, actor: MonsterInstance, action: Dict):
        """Attempt to flee from battle."""
        if not self.can_flee:
            self.battle_ui.add_message("Hier gibt's kein Entkommen!")
            return
        
        # Calculate flee chance based on speed
        flee_chance = 0.5  # Base chance
        
        if self.battle_state.enemy_team:
            enemy_speed = max(m.stats['spd'] for m in self.battle_state.enemy_team if m)
            player_speed = actor.stats['spd']
            
            speed_ratio = player_speed / enemy_speed if enemy_speed > 0 else 1
            flee_chance = min(0.95, 0.3 + 0.4 * speed_ratio)
        
        # Roll for flee
        if random.random() < flee_chance:
            self.battle_ui.add_message("Du bist erfolgreich abgehauen!")
            self.battle_result = BattleResult.FLED
            # Sofort zur END-Phase wechseln
            self.current_phase = BattlePhase.END
            self.phase_timer = 0
            print("Flee successful - ending battle")
        else:
            self.battle_ui.add_message("Kannst nicht abhauen!")
            # Zurück zum Input für weitere Aktionen
            self.current_phase = BattlePhase.INPUT
            self.waiting_for_input = True
            self.pending_actions.clear()
    
    def _process_status_effects(self):
        """Process end-of-turn status effects."""
        # Wenn bereits geflohen, nichts mehr ausführen
        if self.battle_result != BattleResult.ONGOING:
            print("Battle already ended - skipping status effects")
            return
        
        # Process all monsters
        all_monsters = [
            (f'player_{i}', m) for i, m in enumerate(self.battle_state.player_team) if m
        ] + [
            (f'enemy_{i}', m) for i, m in enumerate(self.battle_state.enemy_team) if m
        ]
        
        for actor_id, monster in all_monsters:
            if monster.current_hp <= 0:
                continue
            
            # Process status
            if monster.status == 'burn':
                damage = max(1, monster.max_hp // 16)
                monster.current_hp = max(0, monster.current_hp - damage)
                self.battle_ui.set_hp(actor_id, monster.current_hp)
                self.battle_ui.add_message(
                    f"{monster.nickname or monster.species_name} leidet unter Verbrennung!"
                )
            
            elif monster.status == 'poison':
                damage = max(1, monster.max_hp // 8)
                monster.current_hp = max(0, monster.current_hp - damage)
                self.battle_ui.set_hp(actor_id, monster.current_hp)
                self.battle_ui.add_message(
                    f"{monster.nickname or monster.species_name} leidet unter Gift!"
                )
    
    def _check_defeated(self):
        """Check for defeated monsters and handle them."""
        # Wenn bereits geflohen, nichts mehr ausführen
        if self.battle_result != BattleResult.ONGOING:
            print("Battle already ended - skipping defeated check")
            return
        
        # Check player team
        for i, monster in enumerate(self.battle_state.player_team):
            if monster and monster.current_hp <= 0 and monster.status != 'fainted':
                monster.status = 'fainted'
                self.battle_ui.add_message(
                    f"{monster.nickname or monster.species_name} wurde besiegt!"
                )
        
        # Check enemy team
        for i, monster in enumerate(self.battle_state.enemy_team):
            if monster and monster.current_hp <= 0 and monster.status != 'fainted':
                monster.status = 'fainted'
                self.battle_ui.add_message(
                    f"{monster.species_name} wurde besiegt!"
                )
                
                # Calculate experience
                exp = self._calculate_exp_reward(monster)
                self.exp_gained += exp
    
    def _check_battle_end(self) -> BattleResult:
        """Check if battle should end."""
        # Wenn bereits geflohen, nichts mehr ausführen
        if self.battle_result != BattleResult.ONGOING:
            return self.battle_result
        
        # Check if all player monsters fainted
        player_alive = any(
            m and m.current_hp > 0 
            for m in self.battle_state.player_team
        )
        
        if not player_alive:
            return BattleResult.DEFEAT
        
        # Check if all enemy monsters fainted
        enemy_alive = any(
            m and m.current_hp > 0 
            for m in self.battle_state.enemy_team
        )
        
        if not enemy_alive:
            return BattleResult.VICTORY
        
        # Battle continues
        return BattleResult.ONGOING
    
    def _calculate_exp_reward(self, defeated: MonsterInstance) -> int:
        """Calculate experience points for defeating a monster."""
        # Wenn geflohen, keine EXP
        if self.battle_result == BattleResult.FLED:
            return 0
        
        # Base EXP based on level and rank
        rank_multipliers = {
            'F': 0.5, 'E': 0.7, 'D': 0.9, 'C': 1.0,
            'B': 1.2, 'A': 1.5, 'S': 2.0, 'SS': 2.5, 'X': 3.0
        }
        
        base_exp = defeated.level * 10
        rank_mult = rank_multipliers.get(defeated.rank, 1.0)
        
        # Wild vs trainer bonus
        trainer_mult = 1.5 if not self.is_wild else 1.0
        
        # Boss bonus
        boss_mult = 2.0 if self.is_boss else 1.0
        
        return int(base_exp * rank_mult * trainer_mult * boss_mult)
    
    def _distribute_rewards(self):
        """Distribute EXP and items to party."""
        # Wenn geflohen, keine Belohnungen
        if self.battle_result == BattleResult.FLED:
            print("Player fled - no rewards distributed")
            return
        
        if self.exp_gained > 0:
            # Distribute to all participating monsters
            participants = [
                m for m in self.battle_state.player_team 
                if m and m.current_hp > 0
            ]
            
            if participants:
                exp_per_monster = self.exp_gained // len(participants)
                
                for monster in participants:
                    old_level = monster.level
                    monster.gain_exp(exp_per_monster)
                    
                    self.battle_ui.add_message(
                        f"{monster.nickname or monster.species_name} kriegt {exp_per_monster} EXP!"
                    )
                    
                    # Check for level up
                    if monster.level > old_level:
                        self.battle_ui.add_message(
                            f"{monster.nickname or monster.species_name} ist jetzt Level {monster.level}!"
                        )
                        
                        # Check for new moves
                        if hasattr(monster, 'check_learned_moves'):
                            new_moves = monster.check_learned_moves()
                            for move_id in new_moves:
                                move = self.game.resources.get_move(move_id)
                                if move:
                                    self.battle_ui.add_message(
                                        f"{monster.nickname or monster.species_name} lernt {move.name}!"
                                    )
                                    
                                    # Track learned moves for sync
                                    if not hasattr(monster, 'new_moves_learned'):
                                        monster.new_moves_learned = []
                                    monster.new_moves_learned.append(move_id)
    
    def draw(self, surface: pygame.Surface):
        """Draw the battle scene."""
        # Wenn bereits geflohen, nur UI zeichnen
        if self.battle_result != BattleResult.ONGOING:
            # Zeichne nur die UI, keine Monster mehr
            self.battle_ui.draw(surface)
            if self.game.debug_mode:
                self._draw_debug_info(surface)
            return
        
        # Draw battle UI (includes background)
        self.battle_ui.draw(surface)
        
        # Draw monster sprites instead of rectangles
        self._draw_monster_sprites(surface)
        
        # Draw any additional overlays
        if self.game.debug_mode:
            self._draw_debug_info(surface)
    
    def _draw_monster_sprites(self, surface: pygame.Surface) -> None:
        """Draw monster sprites in battle."""
        # Wenn bereits geflohen, nichts mehr zeichnen
        if self.battle_result != BattleResult.ONGOING:
            return
        
        # Die BattleUI verwaltet bereits alle Monster-Sprites
        # Hier müssen wir nichts mehr zeichnen, da die BattleUI.draw() das bereits macht
        pass
    
    def _draw_debug_info(self, surface: pygame.Surface):
        """Draw debug information."""
        font = pygame.font.Font(None, 10)
        y = 2
        
        debug_info = [
            f"Phase: {self.current_phase.name}",
            f"Turn: {self.turn_count}",
            f"Actions: {len(self.action_queue)}",
            f"Result: {self.battle_result.name}",
            f"Party Size: {len(self.game.party_manager.party.get_all_members())}",
            f"Can Flee: {self.can_flee}",
            f"Is Wild: {self.is_wild}"
        ]
        
        for info in debug_info:
            text = font.render(info, True, (255, 255, 0))
            surface.blit(text, (2, y))
            y += 10
