"""
DQM Command Collection Phase
All players input commands before any action executes
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum, auto

from engine.systems.monster_instance import MonsterInstance
from engine.systems.battle.battle_enums import BattleCommand
from engine.systems.battle.battle_ai import BattleAI

logger = logging.getLogger(__name__)


class CommandPhase(Enum):
    """Phases of command collection."""
    WAITING = auto()
    PLAYER_INPUT = auto()
    AI_PROCESSING = auto()
    VALIDATION = auto()
    COMPLETE = auto()


class CommandType(Enum):
    """Types of commands that can be collected."""
    ATTACK = "attack"
    SKILL = "skill"
    ITEM = "item"
    SWITCH = "switch"
    FLEE = "flee"
    PSYCHE_UP = "psyche_up"
    DEFEND = "defend"
    MEDITATE = "meditate"
    INTIMIDATE = "intimidate"


@dataclass
class MonsterCommand:
    """Command for a single monster."""
    monster_id: str
    monster: MonsterInstance
    command_type: CommandType
    target_id: Optional[str] = None
    target: Optional[MonsterInstance] = None
    move_id: Optional[str] = None
    item_id: Optional[str] = None
    switch_to_id: Optional[str] = None
    priority: int = 0
    validated: bool = False
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class CommandCollector:
    """
    Manages the command input phase for all monsters.
    In DQM, you select actions for ALL your monsters before ANY execute.
    """
    
    def __init__(self, battle_state):
        """
        Initialize the command collector.
        
        Args:
            battle_state: Current battle state
        """
        self.battle_state = battle_state
        self.pending_commands: Dict[str, MonsterCommand] = {}
        self.command_history: List[Dict[str, MonsterCommand]] = []
        self.current_phase = CommandPhase.WAITING
        self.current_input_index = 0
        self.battle_ai = BattleAI()
        
        # Track which monsters need commands
        self.player_monsters_needing_commands: List[Tuple[str, MonsterInstance]] = []
        self.enemy_monsters_needing_commands: List[Tuple[str, MonsterInstance]] = []
        
        # UI callback for getting player input
        self.input_callback = None
        
    def collect_all_commands(self) -> Dict[str, MonsterCommand]:
        """
        Main collection phase - get commands for all active monsters.
        Returns only when ALL commands are collected.
        
        Returns:
            Dictionary of monster_id -> MonsterCommand
        """
        try:
            logger.info("Starting command collection phase")
            self.current_phase = CommandPhase.PLAYER_INPUT
            self.pending_commands.clear()
            
            # Identify all monsters that need commands
            self._identify_monsters_needing_commands()
            
            # Collect player commands
            player_commands = self._collect_player_commands()
            self.pending_commands.update(player_commands)
            
            # Collect AI commands
            self.current_phase = CommandPhase.AI_PROCESSING
            enemy_commands = self._collect_ai_commands()
            self.pending_commands.update(enemy_commands)
            
            # Validate all commands
            self.current_phase = CommandPhase.VALIDATION
            validation_success = self.validate_all_commands()
            
            if not validation_success:
                logger.warning("Command validation failed, retrying collection")
                # Retry collection for invalid commands
                return self._retry_invalid_commands()
            
            # Save to history
            self.command_history.append(self.pending_commands.copy())
            
            self.current_phase = CommandPhase.COMPLETE
            logger.info(f"Command collection complete: {len(self.pending_commands)} commands")
            
            return self.pending_commands
            
        except Exception as e:
            logger.error(f"Error in command collection: {str(e)}")
            return {}
    
    def _identify_monsters_needing_commands(self):
        """Identify which monsters need commands this turn."""
        self.player_monsters_needing_commands.clear()
        self.enemy_monsters_needing_commands.clear()
        
        # Check 3v3 mode
        if self.battle_state.enable_3v3 and self.battle_state.formation_manager:
            # Get active monsters from formations
            player_slots = self.battle_state.player_formation.get_active_monsters()
            enemy_slots = self.battle_state.enemy_formation.get_active_monsters()
            
            # Add player monsters that can act
            for slot in player_slots:
                if slot.can_act() and slot.monster and not slot.monster.is_fainted:
                    monster_id = f"player_{slot.position.value}"
                    self.player_monsters_needing_commands.append((monster_id, slot.monster))
            
            # Add enemy monsters that can act
            for slot in enemy_slots:
                if slot.can_act() and slot.monster and not slot.monster.is_fainted:
                    monster_id = f"enemy_{slot.position.value}"
                    self.enemy_monsters_needing_commands.append((monster_id, slot.monster))
        else:
            # Traditional 1v1 mode
            if self.battle_state.player_active and not self.battle_state.player_active.is_fainted:
                if self._can_monster_act(self.battle_state.player_active):
                    self.player_monsters_needing_commands.append(
                        ("player_0", self.battle_state.player_active)
                    )
            
            if self.battle_state.enemy_active and not self.battle_state.enemy_active.is_fainted:
                if self._can_monster_act(self.battle_state.enemy_active):
                    self.enemy_monsters_needing_commands.append(
                        ("enemy_0", self.battle_state.enemy_active)
                    )
        
        logger.info(f"Monsters needing commands - Player: {len(self.player_monsters_needing_commands)}, "
                   f"Enemy: {len(self.enemy_monsters_needing_commands)}")
    
    def _can_monster_act(self, monster: MonsterInstance) -> bool:
        """Check if a monster can act this turn."""
        if not monster or monster.is_fainted:
            return False
        
        # Check status conditions that prevent action
        if hasattr(monster, 'status'):
            status = monster.status
            if status in ['paralyzed', 'frozen', 'sleep']:
                # Check if they break free this turn
                if status == 'paralyzed':
                    # 25% chance to act when paralyzed
                    import random
                    return random.random() < 0.25
                elif status == 'frozen':
                    # 20% chance to thaw
                    import random
                    return random.random() < 0.20
                elif status == 'sleep':
                    # Will wake up, but can't act this turn
                    return False
        
        return True
    
    def _collect_player_commands(self) -> Dict[str, MonsterCommand]:
        """Collect commands for all player monsters."""
        player_commands = {}
        
        for monster_id, monster in self.player_monsters_needing_commands:
            # Get command for this monster
            command = self._get_player_command_for_monster(monster_id, monster)
            if command:
                player_commands[monster_id] = command
                logger.info(f"Player command collected for {monster.name}: {command.command_type.value}")
        
        return player_commands
    
    def _get_player_command_for_monster(self, monster_id: str, monster: MonsterInstance) -> Optional[MonsterCommand]:
        """
        Get player command for a specific monster.
        This should interface with the UI to get player input.
        
        Args:
            monster_id: ID of the monster
            monster: The monster instance
            
        Returns:
            MonsterCommand or None
        """
        # This is where we interface with the UI
        # For now, return a placeholder that would come from UI
        
        # If we have an input callback, use it
        if self.input_callback:
            command_data = self.input_callback(monster_id, monster)
            if command_data:
                return self._create_command_from_data(monster_id, monster, command_data)
        
        # Default command for testing
        return MonsterCommand(
            monster_id=monster_id,
            monster=monster,
            command_type=CommandType.ATTACK,
            target_id="enemy_0",
            priority=0
        )
    
    def _collect_ai_commands(self) -> Dict[str, MonsterCommand]:
        """Collect commands for all AI-controlled monsters."""
        enemy_commands = {}
        
        for monster_id, monster in self.enemy_monsters_needing_commands:
            command = self._get_ai_command_for_monster(monster_id, monster)
            if command:
                enemy_commands[monster_id] = command
                logger.info(f"AI command collected for {monster.name}: {command.command_type.value}")
        
        return enemy_commands
    
    def _get_ai_command_for_monster(self, monster_id: str, monster: MonsterInstance) -> Optional[MonsterCommand]:
        """
        Get AI-determined command for a monster.
        
        Args:
            monster_id: ID of the monster
            monster: The monster instance
            
        Returns:
            MonsterCommand or None
        """
        try:
            # Use BattleAI to determine action
            ai_action = self.battle_ai.choose_action(
                monster,
                self.battle_state.enemy_team,
                self.battle_state.player_team,
                self.battle_state
            )
            
            if not ai_action:
                # Default to basic attack
                return MonsterCommand(
                    monster_id=monster_id,
                    monster=monster,
                    command_type=CommandType.ATTACK,
                    target_id="player_0",
                    priority=0
                )
            
            # Convert AI action to MonsterCommand
            command_type = CommandType.ATTACK
            if ai_action.get('type') == 'skill':
                command_type = CommandType.SKILL
            elif ai_action.get('type') == 'item':
                command_type = CommandType.ITEM
            elif ai_action.get('type') == 'switch':
                command_type = CommandType.SWITCH
            
            return MonsterCommand(
                monster_id=monster_id,
                monster=monster,
                command_type=command_type,
                target_id=ai_action.get('target_id', 'player_0'),
                move_id=ai_action.get('move_id'),
                item_id=ai_action.get('item_id'),
                priority=ai_action.get('priority', 0)
            )
            
        except Exception as e:
            logger.error(f"Error getting AI command: {str(e)}")
            # Fallback to basic attack
            return MonsterCommand(
                monster_id=monster_id,
                monster=monster,
                command_type=CommandType.ATTACK,
                target_id="player_0",
                priority=0
            )
    
    def validate_all_commands(self) -> bool:
        """
        Ensure all commands are valid before execution.
        
        Returns:
            True if all commands are valid, False otherwise
        """
        all_valid = True
        
        for monster_id, command in self.pending_commands.items():
            if not self._validate_command(command):
                all_valid = False
                logger.warning(f"Invalid command for {monster_id}: {command.error_message}")
        
        return all_valid
    
    def _validate_command(self, command: MonsterCommand) -> bool:
        """
        Validate a single command.
        
        Args:
            command: Command to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Check monster can act
            if command.monster.is_fainted:
                command.error_message = "Monster is fainted"
                command.validated = False
                return False
            
            # Validate based on command type
            if command.command_type == CommandType.ATTACK:
                return self._validate_attack_command(command)
            elif command.command_type == CommandType.SKILL:
                return self._validate_skill_command(command)
            elif command.command_type == CommandType.ITEM:
                return self._validate_item_command(command)
            elif command.command_type == CommandType.SWITCH:
                return self._validate_switch_command(command)
            elif command.command_type == CommandType.FLEE:
                return self._validate_flee_command(command)
            elif command.command_type in [CommandType.PSYCHE_UP, CommandType.DEFEND, 
                                         CommandType.MEDITATE, CommandType.INTIMIDATE]:
                # These are always valid if monster can act
                command.validated = True
                return True
            
            command.error_message = f"Unknown command type: {command.command_type}"
            command.validated = False
            return False
            
        except Exception as e:
            logger.error(f"Error validating command: {str(e)}")
            command.error_message = str(e)
            command.validated = False
            return False
    
    def _validate_attack_command(self, command: MonsterCommand) -> bool:
        """Validate attack command."""
        # Check if monster has a basic attack move
        if not command.monster.moves:
            command.error_message = "Monster has no moves"
            command.validated = False
            return False
        
        # Check target is valid
        if not command.target_id:
            command.error_message = "No target specified"
            command.validated = False
            return False
        
        command.validated = True
        return True
    
    def _validate_skill_command(self, command: MonsterCommand) -> bool:
        """Validate skill command."""
        if not command.move_id:
            command.error_message = "No skill specified"
            command.validated = False
            return False
        
        # Check MP for skill
        # Find the move in monster's moves
        move = None
        for m in command.monster.moves:
            if hasattr(m, 'id') and m.id == command.move_id:
                move = m
                break
        
        if not move:
            command.error_message = "Monster doesn't know this skill"
            command.validated = False
            return False
        
        # Check MP cost
        if hasattr(move, 'mp_cost'):
            if command.monster.current_mp < move.mp_cost:
                command.error_message = "Not enough MP"
                command.validated = False
                return False
        
        command.validated = True
        return True
    
    def _validate_item_command(self, command: MonsterCommand) -> bool:
        """Validate item command."""
        if not command.item_id:
            command.error_message = "No item specified"
            command.validated = False
            return False
        
        # Check item availability in inventory
        # This would interface with inventory system
        # For now, assume valid
        command.validated = True
        return True
    
    def _validate_switch_command(self, command: MonsterCommand) -> bool:
        """Validate switch command."""
        if not command.switch_to_id:
            command.error_message = "No switch target specified"
            command.validated = False
            return False
        
        # Check if switch target is available
        available_switches = self.battle_state.get_available_switches()
        
        # Find the monster to switch to
        switch_target = None
        for monster in available_switches:
            if hasattr(monster, 'id') and str(monster.id) == command.switch_to_id:
                switch_target = monster
                break
        
        if not switch_target:
            command.error_message = "Invalid switch target"
            command.validated = False
            return False
        
        command.validated = True
        return True
    
    def _validate_flee_command(self, command: MonsterCommand) -> bool:
        """Validate flee command."""
        if not self.battle_state.can_flee:
            command.error_message = "Cannot flee from this battle"
            command.validated = False
            return False
        
        command.validated = True
        return True
    
    def _retry_invalid_commands(self) -> Dict[str, MonsterCommand]:
        """Retry collection for commands that failed validation."""
        retry_commands = {}
        
        for monster_id, command in self.pending_commands.items():
            if not command.validated:
                logger.info(f"Retrying command for {monster_id} due to: {command.error_message}")
                
                # Get new command
                if monster_id.startswith("player"):
                    new_command = self._get_player_command_for_monster(monster_id, command.monster)
                else:
                    new_command = self._get_ai_command_for_monster(monster_id, command.monster)
                
                if new_command and self._validate_command(new_command):
                    retry_commands[monster_id] = new_command
                else:
                    # Fall back to defend
                    retry_commands[monster_id] = MonsterCommand(
                        monster_id=monster_id,
                        monster=command.monster,
                        command_type=CommandType.DEFEND,
                        priority=10,
                        validated=True
                    )
            else:
                retry_commands[monster_id] = command
        
        return retry_commands
    
    def _create_command_from_data(self, monster_id: str, monster: MonsterInstance, 
                                 command_data: Dict[str, Any]) -> MonsterCommand:
        """Create a MonsterCommand from UI command data."""
        command_type_str = command_data.get('action', 'attack')
        
        # Map string to CommandType enum
        command_type_map = {
            'attack': CommandType.ATTACK,
            'skill': CommandType.SKILL,
            'item': CommandType.ITEM,
            'switch': CommandType.SWITCH,
            'flee': CommandType.FLEE,
            'psyche_up': CommandType.PSYCHE_UP,
            'defend': CommandType.DEFEND,
            'meditate': CommandType.MEDITATE,
            'intimidate': CommandType.INTIMIDATE
        }
        
        command_type = command_type_map.get(command_type_str, CommandType.ATTACK)
        
        return MonsterCommand(
            monster_id=monster_id,
            monster=monster,
            command_type=command_type,
            target_id=command_data.get('target_id'),
            move_id=command_data.get('move_id'),
            item_id=command_data.get('item_id'),
            switch_to_id=command_data.get('switch_to_id'),
            priority=command_data.get('priority', 0),
            metadata=command_data.get('metadata', {})
        )
    
    def set_input_callback(self, callback):
        """
        Set the callback function for getting player input.
        
        Args:
            callback: Function that takes (monster_id, monster) and returns command data
        """
        self.input_callback = callback
    
    def get_pending_command(self, monster_id: str) -> Optional[MonsterCommand]:
        """Get pending command for a specific monster."""
        return self.pending_commands.get(monster_id)
    
    def cancel_command(self, monster_id: str) -> bool:
        """
        Cancel a pending command.
        
        Args:
            monster_id: ID of the monster whose command to cancel
            
        Returns:
            True if command was cancelled, False if not found
        """
        if monster_id in self.pending_commands:
            del self.pending_commands[monster_id]
            logger.info(f"Command cancelled for {monster_id}")
            return True
        return False
    
    def modify_command(self, monster_id: str, new_command: MonsterCommand) -> bool:
        """
        Modify a pending command.
        
        Args:
            monster_id: ID of the monster
            new_command: New command to replace with
            
        Returns:
            True if modified, False if not found
        """
        if monster_id in self.pending_commands:
            if self._validate_command(new_command):
                self.pending_commands[monster_id] = new_command
                logger.info(f"Command modified for {monster_id}")
                return True
            else:
                logger.warning(f"New command invalid for {monster_id}: {new_command.error_message}")
        return False
    
    def get_command_summary(self) -> Dict[str, Any]:
        """Get a summary of all pending commands."""
        summary = {
            'phase': self.current_phase.value,
            'total_commands': len(self.pending_commands),
            'player_commands': sum(1 for k in self.pending_commands.keys() if k.startswith('player')),
            'enemy_commands': sum(1 for k in self.pending_commands.keys() if k.startswith('enemy')),
            'commands': []
        }
        
        for monster_id, command in self.pending_commands.items():
            summary['commands'].append({
                'monster_id': monster_id,
                'monster_name': command.monster.name,
                'command_type': command.command_type.value,
                'target': command.target_id,
                'validated': command.validated,
                'error': command.error_message
            })
        
        return summary
    
    def convert_to_battle_actions(self) -> List:
        """
        Convert collected commands to BattleActions for execution.
        
        Returns:
            List of BattleAction objects
        """
        from engine.systems.battle.turn_logic import BattleAction, ActionType
        
        battle_actions = []
        
        for monster_id, command in self.pending_commands.items():
            if not command.validated:
                continue
            
            # Map CommandType to ActionType
            action_type_map = {
                CommandType.ATTACK: ActionType.ATTACK,
                CommandType.SKILL: ActionType.ATTACK,  # Skills use attack type with move
                CommandType.ITEM: ActionType.ITEM,
                CommandType.SWITCH: ActionType.SWITCH,
                CommandType.FLEE: ActionType.FLEE,
                CommandType.PSYCHE_UP: ActionType.SPECIAL,
                CommandType.DEFEND: ActionType.SPECIAL,
                CommandType.MEDITATE: ActionType.SPECIAL,
                CommandType.INTIMIDATE: ActionType.SPECIAL
            }
            
            action_type = action_type_map.get(command.command_type, ActionType.ATTACK)
            
            # Get target monster if needed
            target = None
            if command.target_id:
                # Find target monster
                if command.target_id.startswith('player'):
                    idx = int(command.target_id.split('_')[1])
                    if idx < len(self.battle_state.player_team):
                        target = self.battle_state.player_team[idx]
                else:
                    idx = int(command.target_id.split('_')[1])
                    if idx < len(self.battle_state.enemy_team):
                        target = self.battle_state.enemy_team[idx]
            
            # Get move if it's an attack/skill
            move = None
            if command.command_type in [CommandType.ATTACK, CommandType.SKILL]:
                if command.move_id:
                    # Find move in monster's moveset
                    for m in command.monster.moves:
                        if hasattr(m, 'id') and m.id == command.move_id:
                            move = m
                            break
                else:
                    # Use first available move
                    if command.monster.moves:
                        move = command.monster.moves[0]
            
            # Create BattleAction
            battle_action = BattleAction(
                action_type=action_type,
                actor=command.monster,
                move=move,
                target=target or command.monster,  # Self-target if no target
                item=command.item_id,
                priority=command.priority
            )
            
            # Add metadata for special commands
            if command.command_type in [CommandType.PSYCHE_UP, CommandType.DEFEND, 
                                       CommandType.MEDITATE, CommandType.INTIMIDATE]:
                battle_action.special_command = command.command_type.value
            
            battle_actions.append(battle_action)
        
        return battle_actions
