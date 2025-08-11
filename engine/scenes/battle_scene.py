"""
Battle Scene for Untold Story.
Manages the flow of turn-based battles with full UI integration.
"""

import pygame
import random
from typing import Optional, List, Dict, Any
from enum import Enum, auto

from engine.core.scene_base import Scene
from engine.core.config import Colors, GameState
from engine.ui.battle_ui import BattleUI, BattleMenuState
from engine.systems.battle.battle import BattleState, BattlePhase
from engine.systems.battle.turn_logic import TurnManager
from engine.systems.battle.ai import BattleAI
from engine.systems.monster_instance import MonsterInstance
# from engine.ui.transitions import TransitionType  # Temporarily disabled


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
        self.turn_manager: Optional[TurnManager] = None
        self.battle_ai = BattleAI()
        
        # Battle configuration
        self.is_wild = False
        self.is_boss = False
        self.can_flee = True
        self.battle_bg = None  # Background type
        
        # Turn state
        self.current_phase = BattlePhase.INTRO
        self.action_queue: List[Dict] = []
        self.pending_actions: Dict[str, Dict] = {}
        self.turn_count = 0
        
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
        
    def on_enter(self, **kwargs):
        """Initialize battle from kwargs."""
        # Get player team from party manager - CRITICAL FIX!
        if not kwargs.get('player_team'):
            # Use actual party monsters
            player_team = self.game.party_manager.party.get_conscious_members()
            
            # Check if party has any conscious monsters
            if not player_team:
                print("ERROR: No conscious monsters in party!")
                self.game.pop_scene()
                return
        else:
            player_team = kwargs.get('player_team', [])
        
        # Get enemy team
        enemy_team = kwargs.get('enemy_team', [])
        if not enemy_team:
            print("ERROR: No enemy monsters provided!")
            self.game.pop_scene()
            return
        
        # Battle configuration
        self.is_wild = kwargs.get('is_wild', True)
        self.is_boss = kwargs.get('is_boss', False)
        self.can_flee = kwargs.get('can_flee', True) and self.is_wild
        self.battle_bg = kwargs.get('background', 'grass')
        
        # Trainer info if applicable
        self.trainer_name = kwargs.get('trainer_name', None)
        self.trainer_sprite = kwargs.get('trainer_sprite', None)
        
        # Initialize battle state with actual party
        self.battle_state = BattleState(
            player_team=player_team,
            enemy_team=enemy_team,
            is_wild=self.is_wild,
            weather=kwargs.get('weather', None),
            terrain=kwargs.get('terrain', None)
        )
        
        # Initialize turn manager
        self.turn_manager = TurnManager(self.game)
        
        # Initialize UI with monster sprites
        self.battle_ui.init_battle(player_team, enemy_team)
        
        # Get monster sprites from sprite manager
        self._init_monster_sprites(player_team, enemy_team)
        
        # Reset battle vars
        self.turn_count = 0
        self.action_queue.clear()
        self.pending_actions.clear()
        self.battle_result = BattleResult.ONGOING
        self.caught_monster = None
        
        # Start intro phase
        self.current_phase = BattlePhase.INTRO
        self.phase_timer = 0
        
        # Show intro message
        if self.is_wild:
            monster_name = enemy_team[0].species_name if enemy_team else "???"
            self.battle_ui.show_message(f"Ein wildes {monster_name} erscheint!")
    
    def _init_monster_sprites(self, player_team: List, enemy_team: List) -> None:
        """Initialize monster sprites from sprite manager."""
        # Get monster sprites from sprite manager
        if hasattr(self.game, 'sprite_manager') and self.game.sprite_manager:
            sprite_mgr = self.game.sprite_manager
            print(f"Loading monster sprites from sprite manager...")
            print(f"Available monster sprites: {len(sprite_mgr.monster_sprites)}")
            
            # Player monster sprites
            self.player_sprites = {}
            for i, monster in enumerate(player_team):
                if monster:
                    sprite_key = str(monster.species_id) if hasattr(monster, 'species_id') else str(monster.id)
                    if sprite_key in sprite_mgr.monster_sprites:
                        self.player_sprites[f"player_{i}"] = sprite_mgr.monster_sprites[sprite_key]
                        print(f"Loaded player monster {i} sprite: {sprite_key}")
                    else:
                        # Fallback to colored rectangle
                        print(f"Monster sprite not found for {sprite_key}, using fallback")
                        self.player_sprites[f"player_{i}"] = self._load_monster_sprite(monster)
                    
            # Enemy monster sprites  
            self.enemy_sprites = {}
            for i, monster in enumerate(enemy_team):
                if monster:
                    sprite_key = str(monster.species_id) if hasattr(monster, 'species_id') else str(monster.id)
                    if sprite_key in sprite_mgr.monster_sprites:
                        self.enemy_sprites[f"enemy_{i}"] = sprite_mgr.monster_sprites[sprite_key]
                        print(f"Loaded enemy monster {i} sprite: {sprite_key}")
                    else:
                        print(f"Monster sprite not found for {sprite_key}, using fallback")
                        self.enemy_sprites[f"enemy_{i}"] = self._load_monster_sprite(monster)
        else:
            # No sprite manager available, create fallback sprites
            print("No sprite manager available, creating fallback sprites")
            self.player_sprites = {}
            self.enemy_sprites = {}
            
            for i, monster in enumerate(player_team):
                if monster:
                    self.player_sprites[f"player_{i}"] = self._load_monster_sprite(monster)
                    
            for i, monster in enumerate(enemy_team):
                if monster:
                    self.enemy_sprites[f"enemy_{i}"] = self._load_monster_sprite(monster)
        
        print(f"Battle sprites initialized: {len(self.player_sprites)} player, {len(self.enemy_sprites)} enemy")
    
    def _load_monster_sprite(self, monster) -> pygame.Surface:
        """Load the actual monster sprite from the monsters directory."""
        try:
            # Get monster ID
            monster_id = getattr(monster, 'species_id', getattr(monster, 'id', 'Unknown'))
            
            # Load monster sprite
            sprite_path = os.path.join("sprites", "monsters", f"{monster_id}.png")
            if os.path.exists(sprite_path):
                try:
                    monster_sprite = pygame.image.load(sprite_path).convert_alpha()
                    if monster_sprite:
                        # Scale to 64x64 if needed
                        if monster_sprite.get_size() != (64, 64):
                            monster_sprite = pygame.transform.scale(monster_sprite, (64, 64))
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
            print(f"Error loading monster sprite: {e}")
            return self._create_fallback_sprite(monster)
    
    def _create_fallback_sprite(self, monster) -> pygame.Surface:
        """Create a simple fallback sprite when the real sprite can't be loaded."""
        # Simple colored circle based on primary type
        type_colors = {
            'Fire': (255, 100, 50),
            'Water': (50, 150, 255),
            'Earth': (150, 100, 50),
            'Air': (200, 200, 255),
            'Plant': (100, 200, 50),
            'Beast': (180, 140, 100),
            'Energy': (255, 255, 100),
            'Chaos': (150, 50, 150),
            'Plague': (100, 50, 100),
            'Mystic': (255, 150, 255),
            'Deity': (255, 255, 255),
            'Devil': (100, 0, 0),
            'Feuer': (255, 100, 50),      # German type names
            'Wasser': (50, 150, 255),
            'Erde': (150, 100, 50),
            'Luft': (200, 200, 255),
            'Pflanze': (100, 200, 50),
            'Tier': (180, 140, 100),
            'Energie': (255, 255, 100),
            'Chaos': (150, 50, 150),
            'Seuche': (100, 50, 100),
            'Mystisch': (255, 150, 255),
            'Göttlich': (255, 255, 255),
            'Teufel': (100, 0, 0)
        }
        
        monster_type = monster.types[0] if monster.types else 'Normal'
        color = type_colors.get(monster_type, (128, 128, 128))
        
        # Create simple circular sprite
        size = 48
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(surface, color, (size//2, size//2), size//2 - 2)
        pygame.draw.circle(surface, tuple(max(0, c - 50) for c in color), (size//2, size//2), size//2 - 4, 2)
        
        return surface
    
    def on_exit(self):
        """Clean up battle scene and apply battle results."""
        # Update party with battle results
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
        if self.caught_monster:
            success, message = self.game.party_manager.add_to_party(self.caught_monster)
            print(f"Monster caught: {message}")
    
    def _handle_defeat(self):
        """Handle player defeat."""
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
        """Handle input events."""
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
            
            if action and self.waiting_for_input:
                # Let UI handle input and get action
                player_action = self.battle_ui.handle_input(action, self.battle_state)
                
                if player_action:
                    # Store player action
                    self.pending_actions['player_0'] = player_action
                    self.waiting_for_input = False
                    
                    # Check if all actions collected
                    if self._all_actions_ready():
                        self._execute_turn()
            
            return True
        
        return False
    
    def update(self, dt: float):
        """Update battle logic and animations."""
        # Update UI animations
        self.battle_ui.update(dt)
        
        # Update phase timer
        self.phase_timer += dt
        
        # Update animation timer
        if self.animation_timer > 0:
            self.animation_timer -= dt
        
        # Handle current phase
        if self.current_phase == BattlePhase.INTRO:
            self._update_intro_phase(dt)
            
        elif self.current_phase == BattlePhase.INPUT:
            self._update_input_phase(dt)
            
        elif self.current_phase == BattlePhase.EXECUTION:
            self._update_execution_phase(dt)
            
        elif self.current_phase == BattlePhase.AFTERMATH:
            self._update_aftermath_phase(dt)
            
        elif self.current_phase == BattlePhase.END:
            self._update_end_phase(dt)
    
    def _update_intro_phase(self, dt: float):
        """Handle intro animations and messages."""
        # Wait for intro message
        if self.phase_timer > 2.0 or self.battle_ui.menu_state != BattleMenuState.MESSAGE:
            # Send out player monster
            if self.battle_state.player_team:
                monster = self.battle_state.player_team[0]
                self.battle_ui.show_message(f"Los geht's, {monster.nickname or monster.species_name}!")
            
            # Move to input phase after a delay
            if self.phase_timer > 3.0:
                self.current_phase = BattlePhase.INPUT
                self.phase_timer = 0
                self.turn_count += 1
                self._start_input_phase()
    
    def _update_input_phase(self, dt: float):
        """Handle action input collection."""
        # Check if we need AI actions
        if not self.waiting_for_input:
            for actor_id in self._get_active_actors():
                if actor_id not in self.pending_actions:
                    if actor_id.startswith('enemy'):
                        # Get AI action
                        ai_action = self._get_ai_action(actor_id)
                        if ai_action:
                            self.pending_actions[actor_id] = ai_action
                    elif actor_id.startswith('player'):
                        # Wait for player input
                        self.waiting_for_input = True
                        self.battle_ui.menu_state = BattleMenuState.MAIN
            
            # Check if all actions ready
            if not self.waiting_for_input and self._all_actions_ready():
                self._execute_turn()
    
    def _update_execution_phase(self, dt: float):
        """Execute queued actions."""
        # Process action queue
        if self.action_queue:
            # Get next action
            action = self.action_queue[0]
            
            # Check if action animation is done
            if self.animation_timer <= 0:
                # Execute the action
                self._execute_action(action)
                self.action_queue.pop(0)
                
                # Set animation timer for next action
                self.animation_timer = 1.0  # Default action duration
        else:
            # All actions executed, move to aftermath
            self.current_phase = BattlePhase.AFTERMATH
            self.phase_timer = 0
    
    def _update_aftermath_phase(self, dt: float):
        """Handle end-of-turn effects."""
        # Process status effects
        self._process_status_effects()
        
        # Check for defeated monsters
        self._check_defeated()
        
        # Check battle end conditions
        result = self._check_battle_end()
        if result != BattleResult.ONGOING:
            self.battle_result = result
            self.current_phase = BattlePhase.END
            self.phase_timer = 0
        else:
            # Continue to next turn
            self.current_phase = BattlePhase.INPUT
            self.phase_timer = 0
            self.turn_count += 1
            self._start_input_phase()
    
    def _update_end_phase(self, dt: float):
        """Handle battle conclusion."""
        if self.phase_timer == 0:
            # Show result message
            if self.battle_result == BattleResult.VICTORY:
                self.battle_ui.show_message("Sauber! Du hast gewonnen!")
                self._distribute_rewards()
            elif self.battle_result == BattleResult.DEFEAT:
                self.battle_ui.show_message("Scheiße... Du wurdest besiegt!")
            elif self.battle_result == BattleResult.FLED:
                self.battle_ui.show_message("Du bist abgehauen!")
            elif self.battle_result == BattleResult.CAUGHT:
                self.battle_ui.show_message("Monster gefangen! Läuft bei dir!")
        
        # Wait for message and transition
        if self.phase_timer > 3.0:
            # Return to field scene
            self.game.pop_scene()
            
            # Show transition (temporarily disabled)
            # if self.battle_result == BattleResult.VICTORY:
            #     self.game.transition_manager.start(TransitionType.FADE_IN, 0.5)
            # else:
            #     self.game.transition_manager.start(TransitionType.FADE_OUT, 0.5)
    
    def _start_input_phase(self):
        """Initialize input collection for the turn."""
        self.pending_actions.clear()
        self.waiting_for_input = False
        
        # Don't show turn indicator every turn, gets annoying
        if self.turn_count == 1 or self.turn_count % 5 == 0:
            self.battle_ui.show_message(f"Runde {self.turn_count}", wait=False)
    
    def _get_active_actors(self) -> List[str]:
        """Get list of actors that can act this turn."""
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
    
    def _all_actions_ready(self) -> bool:
        """Check if all active actors have submitted actions."""
        active = self._get_active_actors()
        return all(actor in self.pending_actions for actor in active)
    
    def _get_ai_action(self, actor_id: str) -> Optional[Dict]:
        """Get AI-determined action for an actor."""
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
    
    def _execute_turn(self):
        """Process all pending actions for this turn."""
        # Move to execution phase
        self.current_phase = BattlePhase.EXECUTION
        self.phase_timer = 0
        
        # Sort actions by priority and speed
        self.action_queue = self.turn_manager.sort_actions(
            list(self.pending_actions.values()),
            self.battle_state
        )
        
        # Clear pending actions
        self.pending_actions.clear()
        self.animation_timer = 0
    
    def _execute_action(self, action: Dict):
        """Execute a single action."""
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
            self._execute_flee(actor, action)
    
    def _execute_attack(self, actor: MonsterInstance, action: Dict):
        """Execute an attack action."""
        move_id = action['move_id']
        targets = action.get('targets', [])
        
        # Get move data
        move_data = self.game.resources.get_move(move_id)
        if not move_data:
            return
        
        # Show attack message
        self.battle_ui.show_message(
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
                        self.battle_ui.show_message("Volltreffer! Richtig effektiv!")
                    elif effectiveness > 1.0:
                        self.battle_ui.show_message("Effektiv!")
                    elif effectiveness < 0.5:
                        self.battle_ui.show_message("Kaum Wirkung...")
                    elif effectiveness < 1.0:
                        self.battle_ui.show_message("Nicht sehr effektiv...")
                    
                    # Check if critical
                    if result.get('critical'):
                        self.battle_ui.show_message("Kritischer Treffer!")
                
                # Apply status effects
                if result.get('status'):
                    target.status = result['status']
                    self.battle_ui.show_message(
                        f"{target.nickname or target.species_name} hat jetzt {result['status']}!"
                    )
            else:
                self.battle_ui.show_message("Daneben!")
    
    def _execute_tame(self, actor: MonsterInstance, action: Dict):
        """Execute a taming attempt."""
        # Only works on wild monsters
        if not self.is_wild:
            self.battle_ui.show_message("Kannst du knicken bei Trainer-Monstern!")
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
        self.battle_ui.show_message(f"Zähm-Chance: {int(chance * 100)}%")
        
        # Roll for success
        if random.random() < chance:
            # Success!
            self.battle_ui.show_message(f"{target.species_name} wurde gezähmt!")
            self.battle_result = BattleResult.CAUGHT
            
            # Store caught monster for later processing
            self.caught_monster = target
            
            # Show where it goes
            if len(self.game.party_manager.party.get_all_members()) < 6:
                self.battle_ui.show_message(f"{target.species_name} kommt in dein Team!")
            else:
                current_box = self.game.party_manager.storage.get_current_box()
                box_name = current_box.name if current_box else "Box"
                self.battle_ui.show_message(f"{target.species_name} wurde in {box_name} gepackt!")
        else:
            # Failed
            self.battle_ui.show_message("Mist! Hat nicht geklappt!")
            
            # Apply irritation
            if not hasattr(target, 'buffs'):
                target.buffs = []
            target.buffs.append({
                'type': 'irritated',
                'duration': -1
            })
    
    def _execute_item(self, actor: MonsterInstance, action: Dict):
        """Execute item use."""
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
                            self.battle_ui.show_message(
                                f"{target.nickname or target.species_name} wurde um {heal_amount} HP geheilt!"
                            )
                
                # Remove item from inventory
                self.game.inventory.remove_item(item_id, 1)
            else:
                self.battle_ui.show_message("Item nicht gefunden!")
        else:
            self.battle_ui.show_message("Items sind noch nicht implementiert!")
    
    def _execute_flee(self, actor: MonsterInstance, action: Dict):
        """Attempt to flee from battle."""
        if not self.can_flee:
            self.battle_ui.show_message("Hier gibt's kein Entkommen!")
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
            self.battle_ui.show_message("Du bist erfolgreich abgehauen!")
            self.battle_result = BattleResult.FLED
        else:
            self.battle_ui.show_message("Kannst nicht abhauen!")
    
    def _process_status_effects(self):
        """Process end-of-turn status effects."""
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
                self.battle_ui.show_message(
                    f"{monster.nickname or monster.species_name} leidet unter Verbrennung!"
                )
            
            elif monster.status == 'poison':
                damage = max(1, monster.max_hp // 8)
                monster.current_hp = max(0, monster.current_hp - damage)
                self.battle_ui.set_hp(actor_id, monster.current_hp)
                self.battle_ui.show_message(
                    f"{monster.nickname or monster.species_name} leidet unter Gift!"
                )
    
    def _check_defeated(self):
        """Check for defeated monsters and handle them."""
        # Check player team
        for i, monster in enumerate(self.battle_state.player_team):
            if monster and monster.current_hp <= 0 and monster.status != 'fainted':
                monster.status = 'fainted'
                self.battle_ui.show_message(
                    f"{monster.nickname or monster.species_name} wurde besiegt!"
                )
        
        # Check enemy team
        for i, monster in enumerate(self.battle_state.enemy_team):
            if monster and monster.current_hp <= 0 and monster.status != 'fainted':
                monster.status = 'fainted'
                self.battle_ui.show_message(
                    f"{monster.species_name} wurde besiegt!"
                )
                
                # Calculate experience
                exp = self._calculate_exp_reward(monster)
                self.exp_gained += exp
    
    def _check_battle_end(self) -> BattleResult:
        """Check if battle should end."""
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
        
        return BattleResult.ONGOING
    
    def _calculate_exp_reward(self, defeated: MonsterInstance) -> int:
        """Calculate experience points for defeating a monster."""
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
                    
                    self.battle_ui.show_message(
                        f"{monster.nickname or monster.species_name} kriegt {exp_per_monster} EXP!"
                    )
                    
                    # Check for level up
                    if monster.level > old_level:
                        self.battle_ui.show_message(
                            f"{monster.nickname or monster.species_name} ist jetzt Level {monster.level}!"
                        )
                        
                        # Check for new moves
                        if hasattr(monster, 'check_learned_moves'):
                            new_moves = monster.check_learned_moves()
                            for move_id in new_moves:
                                move = self.game.resources.get_move(move_id)
                                if move:
                                    self.battle_ui.show_message(
                                        f"{monster.nickname or monster.species_name} lernt {move.name}!"
                                    )
                                    
                                    # Track learned moves for sync
                                    if not hasattr(monster, 'new_moves_learned'):
                                        monster.new_moves_learned = []
                                    monster.new_moves_learned.append(move_id)
    
    def draw(self, surface: pygame.Surface):
        """Draw the battle scene."""
        # Draw battle UI (includes background)
        self.battle_ui.draw(surface, self.battle_state)
        
        # Draw monster sprites instead of rectangles
        self._draw_monster_sprites(surface)
        
        # Draw any additional overlays
        if self.game.debug_mode:
            self._draw_debug_info(surface)
    
    def _draw_monster_sprites(self, surface: pygame.Surface) -> None:
        """Draw monster sprites in battle."""
        # Draw enemy monster sprites
        if hasattr(self, 'enemy_sprites'):
            for sprite_id, sprite_surface in self.enemy_sprites.items():
                if sprite_id in self.battle_ui.sprites:
                    battle_sprite = self.battle_ui.sprites[sprite_id]
                    pos = battle_sprite.position
                    
                    # Apply shake effect
                    if sprite_id in self.battle_ui.shake_timers:
                        pos = (pos[0] + battle_sprite.shake_offset[0], 
                               pos[1] + battle_sprite.shake_offset[1])
                    
                    # Apply flash effect
                    if sprite_id in self.battle_ui.flash_timers:
                        flash_surface = sprite_surface.copy()
                        flash_surface.fill((255, 255, 255), special_flags=pygame.BLEND_ADD)
                        surface.blit(flash_surface, pos)
                    else:
                        surface.blit(sprite_surface, pos)
        
        # Draw player monster sprites
        if hasattr(self, 'player_sprites'):
            for sprite_id, sprite_surface in self.player_sprites.items():
                if sprite_id in self.battle_ui.sprites:
                    battle_sprite = self.battle_ui.sprites[sprite_id]
                    pos = battle_sprite.position
                    
                    # Apply shake effect
                    if sprite_id in self.battle_ui.shake_timers:
                        pos = (pos[0] + battle_sprite.shake_offset[0], 
                               pos[1] + battle_sprite.shake_offset[1])
                    
                    # Apply flash effect
                    if sprite_id in self.battle_ui.flash_timers:
                        flash_surface = sprite_surface.copy()
                        flash_surface.fill((255, 255, 255), special_flags=pygame.BLEND_ADD)
                        surface.blit(flash_surface, pos)
                    else:
                        surface.blit(sprite_surface, pos)
    
    def _draw_debug_info(self, surface: pygame.Surface):
        """Draw debug information."""
        font = pygame.font.Font(None, 10)
        y = 2
        
        debug_info = [
            f"Phase: {self.current_phase.name}",
            f"Turn: {self.turn_count}",
            f"Actions: {len(self.action_queue)}",
            f"Result: {self.battle_result.name}",
            f"Party Size: {len(self.game.party_manager.party.get_all_members())}"
        ]
        
        for info in debug_info:
            text = font.render(info, True, (255, 255, 0))
            surface.blit(text, (2, y))
            y += 10
