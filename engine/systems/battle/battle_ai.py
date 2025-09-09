"""
AI system for enemy battle decisions.
Implements heuristic-based decision making with difficulty levels.
"""

from typing import TYPE_CHECKING, List, Optional, Dict, Tuple, Any
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
    
    def choose_action(self, enemy_monster: 'MonsterInstance',
                     player_monster: 'MonsterInstance', 
                     battle_state: 'Battle') -> 'BattleAction':
        """Generate enemy action - returns BattleAction for consistency."""
        try:
            from engine.systems.battle.turn_logic import BattleAction, ActionType
            
            # Safety checks
            if not enemy_monster or enemy_monster.current_hp <= 0:
                return BattleAction(actor=enemy_monster, action_type=ActionType.PASS)
            
            if not player_monster or player_monster.current_hp <= 0:
                return BattleAction(actor=enemy_monster, action_type=ActionType.PASS)
            
            # Get available moves with robust fallback
            available_moves = self._get_available_moves_with_fallback(enemy_monster)
            
            if not available_moves:
                # Ultimate fallback: Create basic tackle move
                available_moves = [self._create_basic_move()]
            
            # AI-Logik basierend auf Level
            if self.level == AILevel.RANDOM:
                move = self.rng.choice(available_moves)
            else:
                # Smart AI: Wähle besten Move
                move = self._select_best_move(available_moves, enemy_monster, player_monster)
            
            # Return as BattleAction for consistency
            return BattleAction(
                actor=enemy_monster,
                action_type=ActionType.ATTACK,
                move=move,
                target=player_monster
            )
            
        except Exception as e:
            logger.error(f"AI action generation failed: {e}")
            # Ultimate fallback: Return PASS action
            try:
                from engine.systems.battle.turn_logic import BattleAction, ActionType
                return BattleAction(actor=enemy_monster, action_type=ActionType.PASS)
            except Exception:
                # If even this fails, return None and let the system handle it
                return None
    
    def _get_available_moves_with_fallback(self, enemy_monster: 'MonsterInstance') -> List['Move']:
        """
        Get available moves with comprehensive fallback system.
        
        Args:
            enemy_monster: Monster to get moves for
            
        Returns:
            List of available moves (never empty)
        """
        try:
            available_moves = []
            
            # Try to get moves from monster
            if hasattr(enemy_monster, 'moves') and enemy_monster.moves:
                for move in enemy_monster.moves:
                    if self._can_use_move(move, enemy_monster):
                        available_moves.append(move)
            
            # If no moves found, try MoveRegistry fallback
            if not available_moves:
                try:
                    from engine.systems.moves import MoveRegistry
                    registry = MoveRegistry()
                    fallback_move = registry.get_move("tackle")
                    if fallback_move:
                        available_moves.append(fallback_move)
                except Exception as e:
                    logger.warning(f"MoveRegistry fallback failed: {e}")
            
            # If still no moves, create basic move
            if not available_moves:
                available_moves = [self._create_basic_move()]
            
            return available_moves
            
        except Exception as e:
            logger.error(f"Error getting available moves: {e}")
            # Ultimate fallback
            return [self._create_basic_move()]
    
    def _create_basic_move(self) -> 'Move':
        """
        Create a basic fallback move when no moves are available.
        
        Returns:
            Basic Move object
        """
        try:
            from engine.systems.moves import Move, MoveCategory, MoveTarget, MoveEffect, EffectKind
            
            return Move(
                id="fallback_tackle",
                name="Tackle",
                type="Normal",
                category=MoveCategory.PHYSICAL,
                power=40,
                accuracy=100,
                priority=0,
                targeting=MoveTarget.ENEMY,
                effects=[MoveEffect(kind=EffectKind.DAMAGE, power=40)],
                description="Ein einfacher Angriff.",
                contact=True,
                sound_based=False,
                punching=False,
                biting=False,
                pulse=False,
                multi_hit=None,
                drain_percent=0,
                recoil_percent=0,
                multi_hit_min=1,
                multi_hit_max=1
            )
        except Exception as e:
            logger.error(f"Error creating basic move: {e}")
            # Create minimal move object
            return type('Move', (), {
                'name': 'Tackle',
                'power': 40,
                'accuracy': 100,
                'type': 'Normal',
                'category': 'phys',
                'can_use': lambda: True,
                'id': 'fallback_tackle'
            })()
    
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
        try:
            from engine.systems.battle.turn_logic import BattleAction, ActionType
            
            # Filter to valid targets (not fainted)
            valid_targets = [t for t in targets if t.current_hp > 0]
            if not valid_targets:
                # No valid targets, pass turn
                return BattleAction(actor=actor, action_type=ActionType.PASS)
            
            if self.level == AILevel.RANDOM:
                return self._random_action(actor, valid_targets)
            
            # Get available moves with fallback
            available_moves = self._get_available_moves_with_fallback(actor)
            
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
                    action_type=ActionType.ATTACK,  # Use ATTACK instead of MOVE
                    move=selected.move,
                    target=selected.target
                )
            
            return BattleAction(actor=actor, action_type=ActionType.PASS)
            
        except Exception as e:
            logger.error(f"Error in decide_action: {e}")
            # Fallback to PASS action
            try:
                from engine.systems.battle.turn_logic import BattleAction, ActionType
                return BattleAction(actor=actor, action_type=ActionType.PASS)
            except Exception:
                return None
    
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
        try:
            from engine.systems.battle.turn_logic import BattleAction, ActionType
            
            available_moves = self._get_available_moves_with_fallback(actor)
            if not available_moves:
                return BattleAction(actor=actor, action_type=ActionType.PASS)
            
            move = self.rng.choice(available_moves)
            target = self.rng.choice(targets) if targets else None
            
            return BattleAction(
                actor=actor,
                action_type=ActionType.ATTACK,  # Use ATTACK instead of MOVE
                move=move,
                target=target
            )
        except Exception as e:
            logger.error(f"Error in _random_action: {e}")
            try:
                from engine.systems.battle.turn_logic import BattleAction, ActionType
                return BattleAction(actor=actor, action_type=ActionType.PASS)
            except Exception:
                return None
    
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
        try:
            score = 0.0
            reasoning = []
            
            # Base score from move power
            if hasattr(move, 'category') and move.category in ['phys', 'mag']:
                base_power = getattr(move, 'power', 40) / 100.0  # Normalize to 0-1 range
                score += base_power * 50
                reasoning.append(f"Base power: +{base_power * 50:.1f}")
            
            # Type effectiveness
            if hasattr(battle, 'type_system') and battle.type_system:
                try:
                    effectiveness = battle.type_system.get_effectiveness(move.type, target.species.types)
                    if effectiveness > 1.0:
                        bonus = (effectiveness - 1.0) * 30
                        score += bonus
                        reasoning.append(f"Type advantage: +{bonus:.1f}")
                    elif effectiveness < 1.0:
                        penalty = (1.0 - effectiveness) * 40  # Penalize more than reward
                        score -= penalty
                        reasoning.append(f"Type disadvantage: -{penalty:.1f}")
                except Exception as e:
                    logger.warning(f"Type effectiveness calculation failed: {e}")
            
            # STAB bonus
            if hasattr(actor, 'species') and hasattr(actor.species, 'types'):
                if move.type in actor.species.types:
                    score += 10
                    reasoning.append("STAB: +10")
            
            # Accuracy consideration
            accuracy_factor = getattr(move, 'accuracy', 100) / 100.0 if getattr(move, 'accuracy', 100) > 0 else 1.0
            score *= accuracy_factor
            if accuracy_factor < 1.0:
                reasoning.append(f"Accuracy modifier: ×{accuracy_factor:.2f}")
            
            # Status move scoring
            if hasattr(move, 'category') and move.category == 'support':
                score += self._score_status_move(actor, target, move, reasoning)
            
            # Health-based decisions
            try:
                actor_hp_percent = actor.current_hp / actor.max_hp
                target_hp_percent = target.current_hp / target.max_hp
                
                # Prioritize finishing off low HP targets
                if target_hp_percent < 0.3:
                    score += 20
                    reasoning.append("Low HP target: +20")
                
                # Consider healing if low on health
                if actor_hp_percent < 0.3 and hasattr(move, 'effects'):
                    for effect in move.effects:
                        if hasattr(effect, 'kind') and effect.kind == 'heal':
                            score += 30
                            reasoning.append("Need healing: +30")
                            break
            except Exception as e:
                logger.warning(f"Health-based scoring failed: {e}")
            
            # Speed advantage
            try:
                if hasattr(actor, 'stats') and hasattr(target, 'stats'):
                    actor_speed = getattr(actor.stats, 'spd', 50)
                    target_speed = getattr(target.stats, 'spd', 50)
                    if actor_speed > target_speed:
                        score += 5
                        reasoning.append("Speed advantage: +5")
            except Exception as e:
                logger.warning(f"Speed comparison failed: {e}")
            
            # Status consideration
            try:
                if hasattr(target, 'status') and target.status:
                    if target.status in ['sleep', 'freeze']:
                        score += 15  # Free hit
                        reasoning.append(f"Target {target.status}: +15")
                    elif target.status in ['burn', 'poison']:
                        score += 5  # Already taking damage
                        reasoning.append(f"Target {target.status}: +5")
            except Exception as e:
                logger.warning(f"Status consideration failed: {e}")
            
            # Random factor for non-perfect AI
            if self.level != AILevel.PERFECT:
                random_factor = self.rng.uniform(0.8, 1.2)
                score *= random_factor
                reasoning.append(f"Random factor: ×{random_factor:.2f}")
            
            return MoveScore(move=move, target=target, score=score, reasoning=reasoning)
            
        except Exception as e:
            logger.error(f"Error scoring move: {e}")
            # Return minimal score
            return MoveScore(move=move, target=target, score=0.0, reasoning=["Error in scoring"])
    
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
        try:
            score = 0.0
            
            if not hasattr(move, 'effects'):
                return score
            
            for effect in move.effects:
                if not hasattr(effect, 'kind'):
                    continue
                    
                kind = effect.kind
                
                if kind == 'status':
                    # Don't use status if target already has one
                    if not hasattr(target, 'status') or not target.status:
                        status_value = {
                            'sleep': 35,
                            'paralysis': 30,
                            'burn': 25,
                            'poison': 20,
                            'freeze': 35,
                            'confusion': 15
                        }.get(getattr(effect, 'status', ''), 10)
                        score += status_value
                        reasoning.append(f"Status infliction: +{status_value}")
                    else:
                        score -= 20
                        reasoning.append("Target already has status: -20")
                
                elif kind == 'stat_change':
                    stat = getattr(effect, 'stat', '')
                    stages = getattr(effect, 'stages', 1)
                    
                    # Buff moves
                    if stages > 0:
                        # More valuable early in battle
                        if hasattr(actor, 'current_hp') and hasattr(actor, 'max_hp'):
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
                    if hasattr(actor, 'current_hp') and hasattr(actor, 'max_hp'):
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
            
        except Exception as e:
            logger.error(f"Error scoring status move: {e}")
            return 0.0
    
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
        try:
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
                if hasattr(opponent, 'moves'):
                    for move in opponent.moves:
                        if move and hasattr(move, 'category') and move.category in ['phys', 'mag']:
                            try:
                                effectiveness = battle.type_system.get_effectiveness(
                                    move.type, current.species.types
                                )
                                if effectiveness > 1.5:
                                    switch_score += 30
                            except Exception as e:
                                logger.warning(f"Type effectiveness check failed: {e}")
            
            # Low HP
            if hasattr(current, 'current_hp') and hasattr(current, 'max_hp'):
                hp_percent = current.current_hp / current.max_hp
                if hp_percent < 0.2:
                    switch_score += 20
            
            # Bad status
            if hasattr(current, 'status') and current.status in ['sleep', 'freeze']:
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
            
        except Exception as e:
            logger.error(f"Error in should_switch: {e}")
            return None
    
    def _can_use_move(self, move: 'Move', monster: 'MonsterInstance') -> bool:
        """Prüfe ob Monster Move verwenden kann"""
        try:
            # Basis-Validierung
            if not move or not monster:
                return False
            
            # Prüfe ob Monster nicht ohnmächtig ist
            if monster.current_hp <= 0:
                return False
            
            # Prüfe Status-Effekte
            if hasattr(monster, 'status'):
                try:
                    from engine.systems.conditions import StatusCondition
                    if monster.status == StatusCondition.SLEEP:
                        return False
                except Exception as e:
                    logger.warning(f"Status check failed: {e}")
            
            # DQM-style: Moves haben unbegrenzte Verwendung (kein PP-System)
            # Prüfe nur ob Move grundsätzlich verwendbar ist
            if hasattr(move, 'can_use'):
                return move.can_use()
            
            # Fallback: Move ist verwendbar wenn es existiert
            return True
            
        except Exception as e:
            logger.error(f"Fehler bei Move-Validierung: {e}")
            return False
    
    def _select_best_move(self, available_moves: List['Move'], 
                         actor: 'MonsterInstance', 
                         target: 'MonsterInstance') -> 'Move':
        """Wähle besten Move basierend auf AI-Level"""
        try:
            if not available_moves:
                return self._create_basic_move()
            
            if self.level == AILevel.BASIC:
                # Wähle Move mit höchster Power
                return max(available_moves, key=lambda m: getattr(m, 'power', 40))
            
            elif self.level in [AILevel.SMART, AILevel.EXPERT]:
                # Berücksichtige Typ-Effektivität
                best_move = None
                best_score = 0
                
                for move in available_moves:
                    score = self._calculate_move_score(move, actor, target)
                    if score > best_score:
                        best_score = score
                        best_move = move
                
                return best_move or available_moves[0]
            
            else:
                # Fallback: Zufälliger Move
                return self.rng.choice(available_moves)
                
        except Exception as e:
            logger.error(f"Fehler bei Move-Auswahl: {e}")
            return available_moves[0] if available_moves else self._create_basic_move()
    
    def _calculate_move_score(self, move: 'Move', actor: 'MonsterInstance', target: 'MonsterInstance') -> float:
        """Berechne Score für einen Move"""
        try:
            score = 0.0
            
            # Base score from move power
            if hasattr(move, 'power'):
                base_power = move.power / 100.0  # Normalize to 0-1 range
                score += base_power * 50
            
            # Type effectiveness (simplified)
            if hasattr(move, 'type') and hasattr(target, 'species'):
                # Simple type advantage check
                if hasattr(target.species, 'types'):
                    if move.type in target.species.types:
                        score += 20  # STAB bonus
                    # Add more sophisticated type effectiveness here
            
            # Accuracy consideration
            if hasattr(move, 'accuracy'):
                accuracy_factor = move.accuracy / 100.0 if move.accuracy > 0 else 1.0
                score *= accuracy_factor
            
            # Health-based decisions
            if hasattr(target, 'current_hp') and hasattr(target, 'max_hp'):
                target_hp_percent = target.current_hp / target.max_hp
                if target_hp_percent < 0.3:
                    score += 20  # Prioritize finishing off low HP targets
            
            return score
            
        except Exception as e:
            logger.error(f"Fehler bei Move-Score-Berechnung: {e}")
            return 0.0
    
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
        try:
            score = 0.0
            
            # HP consideration
            if hasattr(candidate, 'current_hp') and hasattr(candidate, 'max_hp'):
                hp_percent = candidate.current_hp / candidate.max_hp
                score += hp_percent * 20
            
            # Type advantage
            if hasattr(battle, 'type_system') and battle.type_system:
                # Check candidate's moves against opponent
                if hasattr(candidate, 'moves'):
                    for move in candidate.moves:
                        if move and hasattr(move, 'category') and move.category in ['phys', 'mag']:
                            try:
                                effectiveness = battle.type_system.get_effectiveness(
                                    move.type, opponent.species.types
                                )
                                if effectiveness > 1.0:
                                    score += (effectiveness - 1.0) * 30
                            except Exception as e:
                                logger.warning(f"Type effectiveness check failed: {e}")
            
            # Speed advantage
            if hasattr(candidate, 'stats') and hasattr(opponent, 'stats'):
                candidate_speed = getattr(candidate.stats, 'spd', 50)
                opponent_speed = getattr(opponent.stats, 'spd', 50)
                if candidate_speed > opponent_speed:
                    score += 10
            
            # No status is better
            if not hasattr(candidate, 'status') or not candidate.status:
                score += 5
            
            return score
            
        except Exception as e:
            logger.error(f"Error scoring switch candidate: {e}")
            return 0.0