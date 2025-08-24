"""
Battle System for Untold Story
Core battle state machine and management
"""

from typing import List, Optional, Dict, Any, Tuple, Union
from enum import Enum
from dataclasses import dataclass
import random
import logging

from engine.systems.monster_instance import MonsterInstance, StatusCondition
from engine.systems.moves import Move, MoveExecutor
from engine.systems.battle.turn_logic import BattleAction, ActionType

# Logger für bessere Fehlerverfolgung
logger = logging.getLogger(__name__)

class BattleType(Enum):
    """Types of battles."""
    WILD = "wild"          # Wild monster encounter
    TRAINER = "trainer"    # Trainer battle
    RIVAL = "rival"        # Rival battle (special trainer)
    GYM = "gym"           # Gym leader battle
    ELITE = "elite"       # Elite Four battle
    CHAMPION = "champion"  # Champion battle
    LEGENDARY = "legendary"  # Legendary monster battle
    STORY = "story"       # Story-critical battle


class BattlePhase(Enum):
    """Phases of battle."""
    INIT = "init"              # Battle initialization
    START = "start"            # Battle start animations
    INPUT = "input"            # Waiting for player input
    ORDER = "order"            # Determining turn order
    RESOLVE = "resolve"        # Executing actions
    AFTERMATH = "aftermath"    # Processing end-of-turn effects
    SWITCH = "switch"          # Monster switching
    MESSAGE = "message"        # Display battle messages
    END = "end"               # Battle ending
    REWARD = "reward"         # Giving rewards
    COMPLETE = "complete"     # Battle complete


class BattleState:
    """
    Complete battle state and logic.
    """
    
    def __init__(self, 
                 player_team: List[MonsterInstance],
                 enemy_team: List[MonsterInstance],
                 battle_type: BattleType = BattleType.WILD,
                 can_flee: bool = True,
                 can_catch: bool = True):
        """
        Initialize battle state.
        
        Args:
            player_team: Player's monster team
            enemy_team: Enemy monster team
            battle_type: Type of battle
            can_flee: Whether fleeing is allowed
            can_catch: Whether catching is allowed
        """
        # Validiere Input-Parameter
        if not player_team or not enemy_team:
            raise ValueError("Beide Teams müssen Monster enthalten")
        
        if not isinstance(battle_type, BattleType):
            raise ValueError("battle_type muss ein BattleType Enum sein")
        
        self.player_team = player_team.copy()  # Kopie um externe Änderungen zu verhindern
        self.enemy_team = enemy_team.copy()
        self.battle_type = battle_type
        self.can_flee = can_flee and battle_type == BattleType.WILD
        self.can_catch = can_catch and battle_type == BattleType.WILD
        
        # Active monsters (currently in battle)
        self.player_active: Optional[MonsterInstance] = None
        self.enemy_active: Optional[MonsterInstance] = None
        
        # Set first non-fainted monsters as active
        for monster in player_team:
            if monster and not monster.is_fainted:
                self.player_active = monster
                break
        
        for monster in enemy_team:
            if monster and not monster.is_fainted:
                self.enemy_active = monster
                break
        
        # Validiere, dass aktive Monster gefunden wurden
        if not self.player_active:
            raise ValueError("Kein aktives Spieler-Monster gefunden")
        if not self.enemy_active:
            raise ValueError("Kein aktiver Gegner gefunden")
        
        # Battle state
        self.phase = BattlePhase.INIT
        self.turn_count = 0
        self.action_queue: List[BattleAction] = []
        
        # Battle history/log
        self.battle_log: List[str] = []
        self.last_action_results: Optional[Dict[str, Any]] = None
        
        # Rewards
        self.exp_earned = 0
        self.money_earned = 0
        self.items_earned: List[str] = []
        
        # Field effects (weather, terrain, etc.)
        self.field_effects: Dict[str, Any] = {}
        
        # Escape attempts
        self.escape_attempts = 0
        
        # RNG für deterministische Tests
        self.rng = random.Random()
    
    def set_random_seed(self, seed: int) -> None:
        """Setze RNG-Seed für deterministische Tests."""
        self.rng = random.Random(seed)
    
    def is_valid(self) -> bool:
        """Check if battle can continue."""
        try:
            return (self.has_able_monsters(self.player_team) and 
                    self.has_able_monsters(self.enemy_team) and
                    self.player_active and not self.player_active.is_fainted and
                    self.enemy_active and not self.enemy_active.is_fainted)
        except Exception as e:
            logger.error(f"Fehler bei Battle-Validierung: {e}")
            return False
    
    def has_able_monsters(self, team: List[MonsterInstance]) -> bool:
        """Check if team has any non-fainted monsters."""
        try:
            return any(m and not m.is_fainted for m in team if m is not None)
        except Exception as e:
            logger.error(f"Fehler beim Prüfen der Team-Fähigkeit: {e}")
            return False
    
    def add_log(self, message: str) -> None:
        """Add message to battle log."""
        if message:
            self.battle_log.append(message)
            logger.info(f"[Battle] {message}")
            print(f"[Battle] {message}")  # Debug output
    
    def validate_battle_state(self) -> bool:
        """Validiere den aktuellen Battle-Status."""
        try:
            # Prüfe Teams
            if not self.player_team or not self.enemy_team:
                return False
            
            # Prüfe aktive Monster
            if not self.player_active or not self.enemy_active:
                return False
            
            # Prüfe Phase
            if not isinstance(self.phase, BattlePhase):
                return False
            
            # Prüfe Action-Queue
            if not isinstance(self.action_queue, list):
                return False
            
            return True
        except Exception as e:
            logger.error(f"Battle-Status-Validierung fehlgeschlagen: {e}")
            return False
    
    def start_battle(self) -> Dict[str, Any]:
        """
        Start the battle.
        
        Returns:
            Battle start information
        """
        try:
            self.phase = BattlePhase.START
            
            # Reset battle state for all monsters
            for monster in self.player_team + self.enemy_team:
                if monster:
                    monster.stat_stages.reset()
                    monster.turns_in_battle = 0
            
            # Battle start message
            if self.battle_type == BattleType.WILD:
                self.add_log(f"Ein wildes {self.enemy_active.name} erscheint!")
            elif self.battle_type == BattleType.TRAINER:
                self.add_log(f"Trainer möchte kämpfen!")
            
            self.add_log(f"Los, {self.player_active.name}!")
            
            self.phase = BattlePhase.INPUT
            
            return {
                "player_active": self.player_active,
                "enemy_active": self.enemy_active,
                "can_flee": self.can_flee,
                "can_catch": self.can_catch
            }
        except Exception as e:
            logger.error(f"Fehler beim Starten des Kampfes: {e}")
            self.phase = BattlePhase.END
            return {"error": str(e)}
    
    def queue_player_action(self, action: Union[Dict[str, Any], BattleAction]) -> bool:
        """
        Queue player's action for the turn.
        
        Args:
            action: Player's chosen action (dict or BattleAction)
            
        Returns:
            True if action was queued successfully
        """
        try:
            if self.phase != BattlePhase.INPUT:
                return False
            
            # Konvertiere dict zu BattleAction falls nötig
            if isinstance(action, dict):
                action = self._dict_to_battle_action(action)
            
            if not action:
                return False
            
            # Validate action
            if not self._validate_action(action):
                return False
            
            self.action_queue.append(action)
            
            # Queue enemy action (AI)
            self._queue_enemy_action()
            
            # Move to order phase
            self.phase = BattlePhase.ORDER
            return True
            
        except Exception as e:
            logger.error(f"Fehler beim Hinzufügen der Player-Action: {e}")
            return False
    
    def _dict_to_battle_action(self, action_dict: Dict[str, Any]) -> Optional[BattleAction]:
        """Konvertiere ein Action-Dict zu einem BattleAction-Objekt."""
        try:
            if 'action_type' not in action_dict:
                return None
            
            # Konvertiere action_type string zu Enum
            action_type_str = action_dict['action_type']
            if isinstance(action_type_str, str):
                try:
                    action_type = ActionType[action_type_str.upper()]
                except KeyError:
                    # Fallback für verschiedene Schreibweisen
                    action_type_map = {
                        'attack': ActionType.ATTACK,
                        'switch': ActionType.SWITCH,
                        'item': ActionType.ITEM,
                        'flee': ActionType.FLEE,
                        'tame': ActionType.TAME,
                        'pass': ActionType.PASS
                    }
                    action_type = action_type_map.get(action_type_str.lower(), ActionType.PASS)
            else:
                action_type = action_dict['action_type']
            
            return BattleAction(
                actor=action_dict.get('actor'),
                action_type=action_type,
                target=action_dict.get('target'),
                move=action_dict.get('move'),
                item_id=action_dict.get('item_id'),
                switch_to=action_dict.get('switch_to')
            )
        except Exception as e:
            logger.error(f"Fehler bei Action-Dict-Konvertierung: {e}")
            return None
    
    def _validate_action(self, action: BattleAction) -> bool:
        """Validiere eine Battle-Action."""
        try:
            if not action or not action.actor:
                return False
            
            if action.action_type == ActionType.ATTACK:
                if not action.move or not action.move.can_use():
                    return False
                if not action.target or action.target.is_fainted:
                    return False
            elif action.action_type == ActionType.SWITCH:
                if not action.switch_to or action.switch_to.is_fainted:
                    return False
                if action.switch_to not in self.player_team:
                    return False
            elif action.action_type == ActionType.ITEM:
                if not action.item_id:
                    return False
            elif action.action_type == ActionType.TAME:
                if not self.can_catch:
                    return False
                if not action.target:
                    return False
            
            return True
        except Exception as e:
            logger.error(f"Action-Validierung fehlgeschlagen: {e}")
            return False
    
    def _queue_enemy_action(self) -> None:
        """Queue AI action for enemy."""
        try:
            if not self.enemy_active or self.enemy_active.is_fainted:
                return
            
            # Simple AI: pick random usable move
            usable_moves = [m for m in self.enemy_active.moves if m and m.can_use()]
            
            if usable_moves:
                move = self.rng.choice(usable_moves)
                
                action = BattleAction(
                    actor=self.enemy_active,
                    action_type=ActionType.ATTACK,
                    move=move,
                    target=self.player_active
                )
                self.action_queue.append(action)
            else:
                # Struggle if no moves available
                self.add_log(f"{self.enemy_active.name} hat keine Attacken mehr!")
        except Exception as e:
            logger.error(f"Fehler beim Hinzufügen der Enemy-Action: {e}")
    
    def resolve_turn(self) -> Dict[str, Any]:
        """
        Resolve all queued actions for the turn.
        
        Returns:
            Turn results
        """
        try:
            if self.phase != BattlePhase.ORDER:
                return {"error": "Falsche Phase für Turn-Auflösung"}
            
            self.phase = BattlePhase.RESOLVE
            self.turn_count += 1
            turn_results = {
                "turn_count": self.turn_count,
                "turn_results": []
            }
            
            # Sort actions by priority and speed
            try:
                self.action_queue.sort(
                    key=lambda a: (a.priority, a.speed),
                    reverse=True
                )
            except Exception as e:
                logger.error(f"Fehler beim Sortieren der Actions: {e}")
                # Fallback: einfache Sortierung
                self.action_queue.sort(key=lambda a: a.priority, reverse=True)
            
            # Execute each action
            for action in self.action_queue:
                # Skip if actor fainted
                if not action.actor or action.actor.is_fainted:
                    continue
                
                # Check status effects that prevent action
                try:
                    status_result = action.actor.process_status()
                    if status_result.get("skip_turn", False):
                        self.add_log(status_result.get("message", "Status verhindert Aktion"))
                        continue
                except Exception as e:
                    logger.error(f"Fehler bei Status-Verarbeitung: {e}")
                    continue
                
                # Execute action
                try:
                    action_result = self._execute_action(action)
                    turn_results["turn_results"].append(action_result)
                except Exception as e:
                    logger.error(f"Fehler bei Action-Ausführung: {e}")
                    turn_results["turn_results"].append({
                        "type": "error",
                        "message": f"Action fehlgeschlagen: {str(e)}"
                    })
                
                # Check for battle end
                if not self.is_valid():
                    self.phase = BattlePhase.END
                    break
            
            # Clear action queue
            self.action_queue.clear()
            
            # Process end-of-turn effects
            if self.phase != BattlePhase.END:
                self.phase = BattlePhase.AFTERMATH
                self._process_aftermath()
            
            # Return to input phase if battle continues
            if self.phase == BattlePhase.AFTERMATH and self.is_valid():
                self.phase = BattlePhase.INPUT
            
            return turn_results
            
        except Exception as e:
            logger.error(f"Fehler bei Turn-Auflösung: {e}")
            return {"error": str(e)}
    
    def _execute_action(self, action: BattleAction) -> Dict[str, Any]:
        """Execute a single action."""
        result = {
            "actor": action.actor.name,
            "type": action.action_type.value,
            "success": False
        }
        
        if action.action_type == ActionType.ATTACK:
            result.update(self._execute_attack(action))
        elif action.action_type == ActionType.TAME:
            result.update(self._execute_tame(action))
        elif action.action_type == ActionType.ITEM:
            result.update(self._execute_item(action))
        elif action.action_type == ActionType.SWITCH:
            result.update(self._execute_switch(action))
        elif action.action_type == ActionType.FLEE:
            result.update(self._execute_flee(action))
        
        return result
    
    def _execute_attack(self, action: BattleAction) -> Dict[str, Any]:
        """Execute an attack action."""
        # Validate action
        if not action.move or not action.target:
            return {"success": False, "message": "Ungültige Attacke!"}
        
        # Check if target is valid
        if action.target.is_fainted:
            return {"success": False, "message": f"{action.target.name} ist bereits besiegt!"}
        
        try:
            # Use PP
            if not action.move.use():
                return {"success": False, "message": "Keine AP mehr übrig!"}
            
            self.add_log(f"{action.actor.name} setzt {action.move.name} ein!")
            
            # Execute move
            move_result = MoveExecutor.execute_move(
                action.move,
                action.actor,
                action.target,
                self
            )
            
            # Apply damage
            if move_result.get("damage", 0) > 0:
                actual_damage = action.target.take_damage(move_result["damage"])
                self.add_log(f"{action.target.name} nimmt {actual_damage} Schaden!")
                
                if action.target.is_fainted:
                    self.add_log(f"{action.target.name} wurde besiegt!")
                    self._handle_knockout(action.target)
            
            # Apply healing
            if move_result.get("healing", 0) > 0:
                actual_heal = action.target.heal(move_result["healing"])
                self.add_log(f"{action.target.name} heilt {actual_heal} HP!")
            
            move_result["success"] = True
            return move_result
            
        except Exception as e:
            self.add_log(f"Fehler bei der Attacke: {str(e)}")
            return {"success": False, "message": "Attacke fehlgeschlagen!"}
    
    def _execute_tame(self, action: BattleAction) -> Dict[str, Any]:
        """Execute a taming/capture attempt."""
        if not self.can_catch or not action.target:
            return {"success": False, "message": "Kann hier nicht fangen!"}
        
        # Calculate catch rate
        hp_percent = action.target.current_hp / action.target.max_hp
        
        # Status bonus
        status_bonus = 1.0
        if action.target.status == StatusCondition.SLEEP:
            status_bonus = 2.0
        elif action.target.status == StatusCondition.FREEZE:
            status_bonus = 2.0
        elif action.target.status == StatusCondition.PARALYSIS:
            status_bonus = 1.5
        elif action.target.status in [StatusCondition.BURN, StatusCondition.POISON]:
            status_bonus = 1.5
        
        catch_rate = action.target.get_catch_rate(hp_percent, status_bonus)
        
        # Add item bonus if using special ball
        if action.item:
            # Different ball types would have different bonuses
            catch_rate *= 1.5
        
        # Attempt capture
        success = self.rng.random() < catch_rate
        
        if success:
            self.add_log(f"Gotcha! {action.target.name} wurde gefangen!")
            # Would add to player's party/box here
            self.phase = BattlePhase.END
            return {"success": True, "caught": action.target}
        else:
            self.add_log(f"Oh nein! {action.target.name} hat sich befreit!")
            return {"success": False}
    
    def _execute_item(self, action: BattleAction) -> Dict[str, Any]:
        """Execute item use."""
        # Item system would be implemented here
        self.add_log(f"{action.actor.name} benutzt {action.item}!")
        return {"success": True, "item": action.item}
    
    def _execute_switch(self, action: BattleAction) -> Dict[str, Any]:
        """Execute monster switch."""
        if not action.switch_to:
            return {"success": False}
        
        old_monster = self.player_active
        self.player_active = action.switch_to
        
        self.add_log(f"Komm zurück, {old_monster.name}!")
        self.add_log(f"Los, {self.player_active.name}!")
        
        # Reset stat stages for withdrawn monster
        old_monster.stat_stages.reset_negative()
        
        return {"success": True, "switched_to": self.player_active}
    
    def _execute_flee(self, action: BattleAction) -> Dict[str, Any]:
        """Execute flee attempt."""
        if not self.can_flee:
            self.add_log("Flucht unmöglich!")
            return {"success": False, "message": "Flucht nicht erlaubt"}
        
        if not self.enemy_active:
            self.add_log("Du bist entkommen!")
            self.phase = BattlePhase.END
            return {"success": True, "fled": True}
        
        try:
            # Calculate flee chance
            self.escape_attempts += 1
            player_speed = max(1, self.player_active.stats["spd"])  # Mindestens 1
            enemy_speed = max(1, self.enemy_active.stats["spd"])    # Mindestens 1
            
            flee_chance = min(1.0, (player_speed * 32 / enemy_speed + 30 * self.escape_attempts) / 256)
            
            if self.rng.random() < flee_chance:
                self.add_log("Du bist entkommen!")
                self.phase = BattlePhase.END
                return {"success": True, "fled": True}
            else:
                self.add_log("Flucht gescheitert!")
                return {"success": False, "message": "Flucht fehlgeschlagen"}
                
        except Exception as e:
            self.add_log(f"Fehler bei der Flucht: {str(e)}")
            return {"success": False, "message": "Flucht fehlgeschlagen"}
    
    def _handle_knockout(self, monster: MonsterInstance) -> None:
        """Handle a monster being knocked out."""
        try:
            # Calculate experience
            if monster in self.enemy_team and self.player_active and not self.player_active.is_fainted:
                # Player defeated enemy
                from engine.systems.stats import Experience
                
                try:
                    base_exp = monster.species.base_exp_yield
                    exp_gained = Experience.calculate_exp_yield(
                        base_exp,
                        monster.level,
                        self.player_active.level,
                        self.battle_type == BattleType.WILD
                    )
                    
                    self.exp_earned += exp_gained
                    
                    # Give exp to active monster
                    exp_result = self.player_active.gain_exp(exp_gained)
                    self.add_log(f"{self.player_active.name} erhält {exp_gained} EP!")
                    
                    if exp_result.get("leveled_up", False):
                        self.add_log(f"{self.player_active.name} erreicht Level {exp_result.get('new_level', '?')}!")
                        
                        for move_id in exp_result.get("new_moves", []):
                            self.add_log(f"{self.player_active.name} möchte {move_id} lernen!")
                
                except Exception as e:
                    self.add_log(f"Fehler bei EP-Berechnung: {str(e)}")
                
                # Check for more enemies
                if not self.has_able_monsters(self.enemy_team):
                    self.phase = BattlePhase.END
            
            elif monster in self.player_team:
                # Enemy defeated player's monster
                # Check for more player monsters
                if not self.has_able_monsters(self.player_team):
                    self.phase = BattlePhase.END
                else:
                    # Force switch
                    self.phase = BattlePhase.SWITCH
        
        except Exception as e:
            self.add_log(f"Fehler bei Knockout-Verarbeitung: {str(e)}")
            # Sicherstellen, dass der Kampf nicht in einem ungültigen Zustand hängt
            if not self.is_valid():
                self.phase = BattlePhase.END
    
    def _process_aftermath(self) -> None:
        """Process end-of-turn effects."""
        # Process status damage for active monsters
        for monster in [self.player_active, self.enemy_active]:
            if monster and not monster.is_fainted:
                status_result = monster.process_status()
                if status_result["message"]:
                    self.add_log(status_result["message"])
                
                if monster.is_fainted:
                    self.add_log(f"{monster.name} wurde durch {monster.status.value} besiegt!")
                    self._handle_knockout(monster)
        
        # Process field effects
        # Weather, terrain, etc. would be processed here
    
    def get_battle_result(self) -> Dict[str, Any]:
        """
        Get the final battle result.
        
        Returns:
            Battle outcome and rewards
        """
        player_won = self.has_able_monsters(self.player_team)
        
        result = {
            "winner": "player" if player_won else "enemy",
            "exp_earned": self.exp_earned,
            "money_earned": self.money_earned,
            "items_earned": self.items_earned,
            "turns": self.turn_count
        }
        
        if player_won:
            # Calculate money reward
            if self.battle_type == BattleType.WILD:
                self.money_earned = 50 * self.enemy_active.level
            else:
                self.money_earned = 100 * self.enemy_active.level
            
            result["money_earned"] = self.money_earned
            self.add_log(f"Du erhältst {self.money_earned}€!")
        else:
            self.add_log("Du wurdest besiegt!")
            self.add_log("Du rennst zum Bergmannsheil...")
        
        return result

    def get_battle_status(self) -> Dict[str, Any]:
        """Hole den aktuellen Battle-Status."""
        try:
            return {
                "phase": self.phase.value,
                "turn_count": self.turn_count,
                "player_active": {
                    "name": self.player_active.name if self.player_active else "Kein Monster",
                    "current_hp": self.player_active.current_hp if self.player_active else 0,
                    "max_hp": self.player_active.max_hp if self.player_active else 0,
                    "status": self.player_active.status.value if self.player_active else "none"
                },
                "enemy_active": {
                    "name": self.enemy_active.name if self.enemy_active else "Kein Monster",
                    "current_hp": self.enemy_active.current_hp if self.enemy_active else 0,
                    "max_hp": self.enemy_active.max_hp if self.enemy_active else 0,
                    "status": self.enemy_active.status.value if self.enemy_active else "none"
                },
                "can_flee": self.can_flee,
                "can_catch": self.can_catch
            }
        except Exception as e:
            logger.error(f"Fehler beim Abrufen des Battle-Status: {e}")
            return {"error": str(e)}
    
    def get_available_moves(self, monster: MonsterInstance) -> List[Move]:
        """Hole verfügbare Moves für ein Monster."""
        try:
            if not monster or monster.is_fainted:
                return []
            return [move for move in monster.moves if move and move.can_use()]
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der verfügbaren Moves: {e}")
            return []
    
    def get_available_switches(self) -> List[MonsterInstance]:
        """Hole verfügbare Wechsel-Monster."""
        try:
            return [monster for monster in self.player_team 
                   if monster and not monster.is_fainted and monster != self.player_active]
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der verfügbaren Wechsel: {e}")
            return []