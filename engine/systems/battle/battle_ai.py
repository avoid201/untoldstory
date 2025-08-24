"""
AI system for enemy battle decisions.
Implements heuristic-based decision making with difficulty levels.
"""

from typing import TYPE_CHECKING, List, Optional, Dict, Tuple
from dataclasses import dataclass
from enum import Enum, auto
import random

if TYPE_CHECKING:
    from engine.systems.monster_instance import MonsterInstance
    from engine.systems.moves import Move
    from engine.systems.battle.battle_controller import BattleState as Battle
    from engine.systems.battle.turn_logic import BattleAction


class AILevel(Enum):
    """AI difficulty levels."""
    RANDOM = auto()      # Completely random moves
    BASIC = auto()       # Basic type effectiveness
    SMART = auto()       # Type effectiveness + status consideration
    EXPERT = auto()      # Full heuristics + prediction
    PERFECT = auto()     # Optimal play (for boss battles)


@dataclass
class MoveScore:
    """Score for a potential move choice."""
    move: 'Move'
    target: 'MonsterInstance'
    score: float
    reasoning: List[str]
    
    def __repr__(self) -> str:
        return f"MoveScore({self.move.name}: {self.score:.2f})"


class BattleAI:
    """AI controller for enemy monsters in battle."""
    
    def __init__(self, level: AILevel = AILevel.SMART, seed: Optional[int] = None):
        """
        Initialize battle AI.
        
        Args:
            level: AI difficulty level
            seed: Random seed for deterministic behavior
        """
        self.level = level
        self.rng = random.Random(seed)
    
    def choose_action(self, actor: 'MonsterInstance',
                     enemy_team: List['MonsterInstance'],
                     player_team: List['MonsterInstance'],
                     battle_state) -> Dict:
        """Choose action for AI monster - compatibility method."""
        # Determine targets based on actor
        if actor in player_team:
            targets = [t for t in enemy_team if t.current_hp > 0]
        else:
            targets = [t for t in player_team if t.current_hp > 0]
        
        if not targets:
            return {
                'type': 'pass',
                'move_id': None,
                'targets': [],
                'actor': actor
            }
        
        # Simple AI: choose random move and target
        available_moves = [m for m in actor.moves if m and hasattr(m, 'current_pp') and m.current_pp > 0]
        if available_moves:
            move = available_moves[0]
            target = targets[0]
            return {
                'type': 'attack',
                'move_id': move.id if hasattr(move, 'id') else 'tackle',
                'targets': [target.id if hasattr(target, 'id') else 'enemy_0'],
                'actor': actor
            }
        else:
            return {
                'type': 'pass',
                'move_id': None,
                'targets': [],
                'actor': actor
            }
    
    def decide_action(self, battle: 'Battle', 
                     actor: 'MonsterInstance',
                     targets: List['MonsterInstance']) -> 'BattleAction':
        """
        Decide what action to take.
        
        Args:
            battle: Current battle state
            actor: Monster making the decision
            targets: Available targets
            
        Returns:
            BattleAction to perform
        """
        from engine.systems.battle.turn_logic import BattleAction, ActionType
        
        # Filter to valid targets (not fainted)
        valid_targets = [t for t in targets if t.current_hp > 0]
        if not valid_targets:
            # No valid targets, pass turn
            return BattleAction(actor=actor, action_type=ActionType.PASS)
        
        if self.level == AILevel.RANDOM:
            return self._random_action(actor, valid_targets)
        
        # Get available moves (have PP)
        available_moves = [m for m in actor.moves if m and m.current_pp > 0]
        if not available_moves:
            # No moves available, struggle or pass
            return BattleAction(actor=actor, action_type=ActionType.PASS)
        
        # Score all possible moves
        move_scores = []
        for move in available_moves:
            for target in valid_targets:
                score = self._score_move(battle, actor, target, move)
                move_scores.append(score)
        
        # Sort by score
        move_scores.sort(key=lambda x: x.score, reverse=True)
        
        # Select based on AI level
        if self.level == AILevel.BASIC:
            # Add some randomness to selection
            if move_scores and self.rng.random() < 0.8:  # 80% chance to pick best
                selected = move_scores[0]
            else:
                selected = self.rng.choice(move_scores) if move_scores else None
        elif self.level in [AILevel.SMART, AILevel.EXPERT]:
            # Usually pick best move
            if move_scores and self.rng.random() < 0.9:  # 90% chance to pick best
                selected = move_scores[0]
            else:
                # Pick from top 3
                top_moves = move_scores[:3]
                selected = self.rng.choice(top_moves) if top_moves else None
        else:  # PERFECT
            # Always pick optimal move
            selected = move_scores[0] if move_scores else None
        
        if selected:
            return BattleAction(
                actor=actor,
                action_type=ActionType.MOVE,
                move=selected.move,
                target=selected.target
            )
        
        return BattleAction(actor=actor, action_type=ActionType.PASS)
    
    def _random_action(self, actor: 'MonsterInstance', 
                      targets: List['MonsterInstance']) -> 'BattleAction':
        """
        Choose a completely random action.
        
        Args:
            actor: Monster making the decision
            targets: Available targets
            
        Returns:
            Random BattleAction
        """
        from engine.systems.battle.turn_logic import BattleAction, ActionType
        
        available_moves = [m for m in actor.moves if m and m.current_pp > 0]
        if not available_moves:
            return BattleAction(actor=actor, action_type=ActionType.PASS)
        
        move = self.rng.choice(available_moves)
        target = self.rng.choice(targets) if targets else None
        
        return BattleAction(
            actor=actor,
            action_type=ActionType.MOVE,
            move=move,
            target=target
        )
    
    def _score_move(self, battle: 'Battle',
                   actor: 'MonsterInstance',
                   target: 'MonsterInstance',
                   move: 'Move') -> MoveScore:
        """
        Score a potential move.
        
        Args:
            battle: Current battle state
            actor: Monster using the move
            target: Target monster
            move: Move to score
            
        Returns:
            MoveScore with calculated score and reasoning
        """
        score = 0.0
        reasoning = []
        
        # Base score from move power
        if move.category in ['phys', 'mag']:
            base_power = move.power / 100.0  # Normalize to 0-1 range
            score += base_power * 50
            reasoning.append(f"Base power: +{base_power * 50:.1f}")
        
        # Type effectiveness
        if hasattr(battle, 'type_system') and battle.type_system:
            effectiveness = battle.type_system.get_effectiveness(move.type, target.species.types)
            if effectiveness > 1.0:
                bonus = (effectiveness - 1.0) * 30
                score += bonus
                reasoning.append(f"Type advantage: +{bonus:.1f}")
            elif effectiveness < 1.0:
                penalty = (1.0 - effectiveness) * 40  # Penalize more than reward
                score -= penalty
                reasoning.append(f"Type disadvantage: -{penalty:.1f}")
        
        # STAB bonus
        if move.type in actor.species.types:
            score += 10
            reasoning.append("STAB: +10")
        
        # Accuracy consideration
        accuracy_factor = move.accuracy / 100.0 if move.accuracy > 0 else 1.0
        score *= accuracy_factor
        if accuracy_factor < 1.0:
            reasoning.append(f"Accuracy modifier: ×{accuracy_factor:.2f}")
        
        # Status move scoring
        if move.category == 'support':
            score += self._score_status_move(actor, target, move, reasoning)
        
        # Health-based decisions
        actor_hp_percent = actor.current_hp / actor.max_hp
        target_hp_percent = target.current_hp / target.max_hp
        
        # Prioritize finishing off low HP targets
        if target_hp_percent < 0.3:
            score += 20
            reasoning.append("Low HP target: +20")
        
        # Consider healing if low on health
        if actor_hp_percent < 0.3 and 'heal' in [e.get('kind') for e in move.effects]:
            score += 30
            reasoning.append("Need healing: +30")
        
        # PP conservation for high-level AI
        if self.level in [AILevel.EXPERT, AILevel.PERFECT]:
            if move.current_pp <= 2:
                score -= 10
                reasoning.append("Low PP: -10")
        
        # Speed advantage
        if actor.stats['spd'] > target.stats['spd']:
            score += 5
            reasoning.append("Speed advantage: +5")
        
        # Status consideration
        if target.status:
            if target.status in ['sleep', 'freeze']:
                score += 15  # Free hit
                reasoning.append(f"Target {target.status}: +15")
            elif target.status in ['burn', 'poison']:
                score += 5  # Already taking damage
                reasoning.append(f"Target {target.status}: +5")
        
        # Random factor for non-perfect AI
        if self.level != AILevel.PERFECT:
            random_factor = self.rng.uniform(0.8, 1.2)
            score *= random_factor
            reasoning.append(f"Random factor: ×{random_factor:.2f}")
        
        return MoveScore(move=move, target=target, score=score, reasoning=reasoning)
    
    def _score_status_move(self, actor: 'MonsterInstance',
                          target: 'MonsterInstance',
                          move: 'Move',
                          reasoning: List[str]) -> float:
        """
        Score a status/support move.
        
        Args:
            actor: Monster using the move
            target: Target monster
            move: Status move to score
            reasoning: List to append reasoning to
            
        Returns:
            Additional score for status move
        """
        score = 0.0
        
        for effect in move.effects:
            kind = effect.get('kind')
            
            if kind == 'status':
                # Don't use status if target already has one
                if not target.status:
                    status_value = {
                        'sleep': 35,
                        'paralysis': 30,
                        'burn': 25,
                        'poison': 20,
                        'freeze': 35,
                        'confusion': 15
                    }.get(effect.get('status'), 10)
                    score += status_value
                    reasoning.append(f"Status infliction: +{status_value}")
                else:
                    score -= 20
                    reasoning.append("Target already has status: -20")
            
            elif kind == 'stat_change':
                stat = effect.get('stat')
                stages = effect.get('stages', 1)
                
                # Buff moves
                if stages > 0:
                    # More valuable early in battle
                    if actor.current_hp > actor.max_hp * 0.7:
                        score += stages * 10
                        reasoning.append(f"Stat buff: +{stages * 10}")
                    else:
                        score += stages * 5
                        reasoning.append(f"Late buff: +{stages * 5}")
                # Debuff moves
                else:
                    score += abs(stages) * 8
                    reasoning.append(f"Stat debuff: +{abs(stages) * 8}")
            
            elif kind == 'heal':
                # Healing value based on current HP
                hp_percent = actor.current_hp / actor.max_hp
                if hp_percent < 0.3:
                    score += 40
                    reasoning.append("Critical heal: +40")
                elif hp_percent < 0.5:
                    score += 25
                    reasoning.append("Important heal: +25")
                elif hp_percent < 0.7:
                    score += 10
                    reasoning.append("Useful heal: +10")
        
        return score
    
    def should_switch(self, battle: 'Battle',
                     current: 'MonsterInstance',
                     opponent: 'MonsterInstance',
                     available: List['MonsterInstance']) -> Optional['MonsterInstance']:
        """
        Determine if AI should switch monsters.
        
        Args:
            battle: Current battle state
            current: Current active monster
            opponent: Opponent's active monster
            available: Available monsters to switch to
            
        Returns:
            Monster to switch to, or None if shouldn't switch
        """
        if self.level in [AILevel.RANDOM, AILevel.BASIC]:
            # Lower level AI doesn't switch strategically
            return None
        
        # Don't switch if no alternatives
        valid_switches = [m for m in available if m.current_hp > 0 and m != current]
        if not valid_switches:
            return None
        
        switch_score = 0
        
        # Type disadvantage
        if hasattr(battle, 'type_system') and battle.type_system:
            # Check opponent's moves against current monster
            for move in opponent.moves:
                if move and move.category in ['phys', 'mag']:
                    effectiveness = battle.type_system.get_effectiveness(
                        move.type, current.species.types
                    )
                    if effectiveness > 1.5:
                        switch_score += 30
        
        # Low HP
        hp_percent = current.current_hp / current.max_hp
        if hp_percent < 0.2:
            switch_score += 20
        
        # Bad status
        if current.status in ['sleep', 'freeze']:
            switch_score += 15
        
        # Only switch if score is high enough
        if switch_score >= 30:
            # Find best switch
            best_switch = None
            best_score = -float('inf')
            
            for candidate in valid_switches:
                score = self._score_switch_candidate(battle, candidate, opponent)
                if score > best_score:
                    best_score = score
                    best_switch = candidate
            
            return best_switch
        
        return None
    
    def _score_switch_candidate(self, battle: 'Battle',
                               candidate: 'MonsterInstance',
                               opponent: 'MonsterInstance') -> float:
        """
        Score a potential switch candidate.
        
        Args:
            battle: Current battle state
            candidate: Monster to potentially switch to
            opponent: Opponent's active monster
            
        Returns:
            Score for this switch
        """
        score = 0.0
        
        # HP consideration
        hp_percent = candidate.current_hp / candidate.max_hp
        score += hp_percent * 20
        
        # Type advantage
        if hasattr(battle, 'type_system') and battle.type_system:
            # Check candidate's moves against opponent
            for move in candidate.moves:
                if move and move.category in ['phys', 'mag']:
                    effectiveness = battle.type_system.get_effectiveness(
                        move.type, opponent.species.types
                    )
                    if effectiveness > 1.0:
                        score += (effectiveness - 1.0) * 30
        
        # Speed advantage
        if candidate.stats['spd'] > opponent.stats['spd']:
            score += 10
        
        # No status is better
        if not candidate.status:
            score += 5
        
        return score