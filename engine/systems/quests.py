"""
Quest system for tracking objectives, side quests, and rewards.
"""

from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass, field
from enum import Enum, auto
import json


class QuestType(Enum):
    """Types of quests."""
    MAIN = auto()          # Main story quests
    SIDE = auto()          # Optional side quests
    DAILY = auto()         # Daily repeatable quests
    COLLECTION = auto()    # Collection/completion quests
    TIMED = auto()         # Time-limited quests


class QuestStatus(Enum):
    """Status of a quest."""
    LOCKED = auto()        # Not yet available
    AVAILABLE = auto()     # Can be started
    ACTIVE = auto()        # Currently in progress
    COMPLETE = auto()      # Objectives complete, ready to turn in
    FINISHED = auto()      # Turned in and rewarded


@dataclass
class QuestObjective:
    """A single quest objective."""
    id: str
    description: str
    target: int = 1
    current: int = 0
    hidden: bool = False
    optional: bool = False
    
    def is_complete(self) -> bool:
        """Check if objective is complete."""
        return self.current >= self.target
    
    def update(self, amount: int = 1) -> bool:
        """
        Update objective progress.
        
        Returns:
            True if objective was just completed
        """
        was_incomplete = not self.is_complete()
        self.current = min(self.current + amount, self.target)
        return was_incomplete and self.is_complete()
    
    def get_progress_text(self) -> str:
        """Get progress display text."""
        if self.hidden and not self.is_complete():
            return "???"
        return f"{self.description} ({self.current}/{self.target})"


@dataclass
class QuestReward:
    """Reward for completing a quest."""
    money: int = 0
    exp: int = 0
    items: Dict[str, int] = field(default_factory=dict)  # item_id -> quantity
    monsters: List[Dict[str, Any]] = field(default_factory=list)  # Monster data
    unlock_flags: List[str] = field(default_factory=list)
    unlock_quests: List[str] = field(default_factory=list)


@dataclass
class Quest:
    """A quest definition."""
    id: str
    name: str
    description: str
    quest_type: QuestType
    giver: str  # NPC who gives the quest
    prerequisites: List[str] = field(default_factory=list)  # Required quests/flags
    objectives: List[QuestObjective] = field(default_factory=list)
    rewards: QuestReward = field(default_factory=QuestReward)
    status: QuestStatus = QuestStatus.LOCKED
    repeatable: bool = False
    time_limit: Optional[float] = None  # Time limit in game hours
    level_requirement: int = 0
    dialogue_start: str = ""
    dialogue_progress: str = ""
    dialogue_complete: str = ""
    
    def is_available(self) -> bool:
        """Check if quest is available to start."""
        return self.status == QuestStatus.AVAILABLE
    
    def is_active(self) -> bool:
        """Check if quest is active."""
        return self.status == QuestStatus.ACTIVE
    
    def is_complete(self) -> bool:
        """Check if all objectives are complete."""
        required_objectives = [obj for obj in self.objectives if not obj.optional]
        return all(obj.is_complete() for obj in required_objectives)
    
    def get_active_objectives(self) -> List[QuestObjective]:
        """Get list of active (visible, incomplete) objectives."""
        return [obj for obj in self.objectives 
                if not obj.hidden and not obj.is_complete()]
    
    def get_completion_percentage(self) -> float:
        """Get quest completion percentage."""
        if not self.objectives:
            return 0.0
        
        total = sum(obj.target for obj in self.objectives if not obj.optional)
        current = sum(min(obj.current, obj.target) for obj in self.objectives if not obj.optional)
        
        return (current / total * 100) if total > 0 else 0.0


class QuestManager:
    """Manages all quests in the game."""
    
    def __init__(self):
        """Initialize quest manager."""
        self.quests: Dict[str, Quest] = {}
        self.active_quests: List[str] = []
        self.completed_quests: Set[str] = set()
        self.quest_counters: Dict[str, int] = {}  # For tracking global counters
        
        self._load_quests()
    
    def _load_quests(self) -> None:
        """Load quest definitions."""
        # Main story quests
        self.add_quest(Quest(
            id='main_starter',
            name='Dein erstes Monster',
            description='Hol dir dein erstes Monster von Professor Budde!',
            quest_type=QuestType.MAIN,
            giver='auto',
            objectives=[
                QuestObjective('meet_professor', 'Triff Professor Budde im Museum'),
                QuestObjective('choose_starter', 'Wähle dein Starter-Monster')
            ],
            rewards=QuestReward(
                money=500,
                items={'potion': 5, 'map': 1}
            ),
            dialogue_start='Zeit für dein erstes Monster!',
            dialogue_complete='Glückwunsch zu deinem ersten Monster!'
        ))
        
        self.add_quest(Quest(
            id='main_first_trial',
            name='Die erste Prüfung',
            description='Bestehe die erste Prüfung!',
            quest_type=QuestType.MAIN,
            giver='auto',
            prerequisites=['main_starter'],
            objectives=[
                QuestObjective('find_trial_1', 'Finde den Ort der ersten Prüfung'),
                QuestObjective('defeat_trial_boss_1', 'Besiege das Boss-Monster der ersten Prüfung')
            ],
            rewards=QuestReward(
                money=1000,
                exp=500,
                items={'super_potion': 3}
            )
        ))
        
        self.add_quest(Quest(
            id='main_time_rifts',
            name='Zeitrisse untersuchen',
            description='Untersuche die mysteriösen Zeitrisse mit Professor Budde',
            quest_type=QuestType.MAIN,
            giver='professor_budde',
            prerequisites=['main_first_trial'],
            objectives=[
                QuestObjective('find_rift', 'Finde einen Zeitriss'),
                QuestObjective('scan_rift', 'Scanne den Zeitriss mit dem Zeitscanner'),
                QuestObjective('close_rift', 'Schließe den Zeitriss', target=3)
            ],
            rewards=QuestReward(
                money=2000,
                items={'time_scanner': 1},
                unlock_flags=['can_close_rifts']
            ),
            dialogue_start='Diese Zeitrisse... die müssen wir untersuchen!',
            dialogue_progress='Haste schon Zeitrisse gefunden?',
            dialogue_complete='Gut gemacht! Jetzt verstehen wir die Risse besser!'
        ))
        
        # Side quests
        self.add_quest(Quest(
            id='side_monster_collector',
            name='Monster-Sammler',
            description='Fange 10 verschiedene Monster-Arten',
            quest_type=QuestType.SIDE,
            giver='npc_collector',
            objectives=[
                QuestObjective('catch_unique', 'Fange verschiedene Monster', target=10)
            ],
            rewards=QuestReward(
                money=1500,
                items={'gold_fleisch': 1, 'rare_candy': 1}
            ),
            repeatable=False,
            dialogue_start='Ich sammel Daten über Monster! Hilf mir dabei!',
            dialogue_complete='Wow, so viele verschiedene Monster!'
        ))
        
        self.add_quest(Quest(
            id='side_delivery',
            name='Eilige Lieferung',
            description='Bringe das Paket zu Ali in der Dönerbude',
            quest_type=QuestType.SIDE,
            giver='shop_keeper',
            objectives=[
                QuestObjective('get_package', 'Nimm das Paket'),
                QuestObjective('deliver_package', 'Liefere es bei Ali ab')
            ],
            rewards=QuestReward(
                money=300,
                items={'potion': 2}
            ),
            dialogue_start='Kannste mal eben wat zu Ali bringen?',
            dialogue_complete='Danke! Hier, für deine Mühe!'
        ))
        
        self.add_quest(Quest(
            id='side_lost_fossil',
            name='Das verlorene Fossil',
            description='Finde das seltene Fossil in der Zeche',
            quest_type=QuestType.SIDE,
            giver='professor_budde',
            prerequisites=['main_starter'],
            objectives=[
                QuestObjective('enter_mine', 'Betrete die Zeche Zollverein'),
                QuestObjective('find_fossil', 'Finde das seltene Fossil'),
                QuestObjective('return_fossil', 'Bringe es zu Professor Budde')
            ],
            rewards=QuestReward(
                money=2000,
                monsters=[{'species': 'ancient_rex', 'level': 15}]
            ),
            level_requirement=10,
            dialogue_start='In der Zeche soll\'n seltenes Fossil sein!',
            dialogue_complete='Dat is ja das legendäre Fossil! Ich erweck es für dich!'
        ))
        
        # Collection quests
        self.add_quest(Quest(
            id='collect_all_starters',
            name='Starter-Komplettist',
            description='Besitze alle vier Starter-Monster',
            quest_type=QuestType.COLLECTION,
            giver='auto',
            objectives=[
                QuestObjective('have_glutkohle', 'Besitze Glutkohle'),
                QuestObjective('have_tropfstein', 'Besitze Tropfstein'),
                QuestObjective('have_lehmling', 'Besitze Lehmling'),
                QuestObjective('have_windei', 'Besitze Windei')
            ],
            rewards=QuestReward(
                items={'master_ball': 1},
                unlock_flags=['starter_master']
            )
        ))
        
        # Daily quests
        self.add_quest(Quest(
            id='daily_battles',
            name='Tägliche Kämpfe',
            description='Gewinne 5 Kämpfe heute',
            quest_type=QuestType.DAILY,
            giver='auto',
            objectives=[
                QuestObjective('win_battles', 'Gewinne Kämpfe', target=5)
            ],
            rewards=QuestReward(
                money=500,
                exp=200,
                items={'potion': 3}
            ),
            repeatable=True
        ))
        
        self.add_quest(Quest(
            id='daily_catch',
            name='Fang des Tages',
            description='Fange 3 Monster heute',
            quest_type=QuestType.DAILY,
            giver='auto',
            objectives=[
                QuestObjective('catch_monsters', 'Fange Monster', target=3)
            ],
            rewards=QuestReward(
                money=400,
                items={'fleisch': 5}
            ),
            repeatable=True
        ))
    
    def add_quest(self, quest: Quest) -> None:
        """Add a quest to the manager."""
        self.quests[quest.id] = quest
    
    def get_quest(self, quest_id: str) -> Optional[Quest]:
        """Get a quest by ID."""
        return self.quests.get(quest_id)
    
    def start_quest(self, quest_id: str) -> bool:
        """
        Start a quest.
        
        Returns:
            True if quest was started
        """
        quest = self.get_quest(quest_id)
        if not quest or not quest.is_available():
            return False
        
        quest.status = QuestStatus.ACTIVE
        self.active_quests.append(quest_id)
        
        # Reset objectives if repeatable
        if quest.repeatable:
            for obj in quest.objectives:
                obj.current = 0
        
        return True
    
    def complete_quest(self, quest_id: str) -> Optional[QuestReward]:
        """
        Complete and turn in a quest.
        
        Returns:
            Rewards if quest was completed
        """
        quest = self.get_quest(quest_id)
        if not quest or not quest.is_complete():
            return None
        
        quest.status = QuestStatus.FINISHED
        if quest_id in self.active_quests:
            self.active_quests.remove(quest_id)
        self.completed_quests.add(quest_id)
        
        # Unlock follow-up quests
        for unlock_id in quest.rewards.unlock_quests:
            if unlock_id in self.quests:
                self.quests[unlock_id].status = QuestStatus.AVAILABLE
        
        # Reset if repeatable
        if quest.repeatable:
            quest.status = QuestStatus.AVAILABLE
        
        return quest.rewards
    
    def update_objective(self, objective_type: str, amount: int = 1) -> List[str]:
        """
        Update objectives across all active quests.
        
        Args:
            objective_type: Type of objective to update
            amount: Amount to add to progress
            
        Returns:
            List of quest IDs that were completed
        """
        completed = []
        
        for quest_id in self.active_quests:
            quest = self.get_quest(quest_id)
            if not quest:
                continue
            
            for obj in quest.objectives:
                if obj.id == objective_type and not obj.is_complete():
                    was_incomplete = not quest.is_complete()
                    obj.update(amount)
                    
                    # Check if quest was just completed
                    if was_incomplete and quest.is_complete():
                        quest.status = QuestStatus.COMPLETE
                        completed.append(quest_id)
        
        return completed
    
    def check_prerequisites(self, story_flags: Dict[str, Any]) -> None:
        """
        Check and update quest availability based on prerequisites.
        
        Args:
            story_flags: Current story flags
        """
        for quest in self.quests.values():
            if quest.status == QuestStatus.LOCKED:
                # Check if prerequisites are met
                prereqs_met = all(
                    self.is_quest_complete(prereq) or 
                    story_flags.get(prereq, False)
                    for prereq in quest.prerequisites
                )
                
                if prereqs_met:
                    quest.status = QuestStatus.AVAILABLE
    
    def is_quest_complete(self, quest_id: str) -> bool:
        """Check if a quest is complete."""
        return quest_id in self.completed_quests
    
    def get_active_quests(self) -> List[Quest]:
        """Get all active quests."""
        return [self.quests[qid] for qid in self.active_quests if qid in self.quests]
    
    def get_available_quests(self) -> List[Quest]:
        """Get all available quests."""
        return [q for q in self.quests.values() if q.is_available()]
    
    def reset_daily_quests(self) -> None:
        """Reset all daily quests."""
        for quest in self.quests.values():
            if quest.quest_type == QuestType.DAILY:
                quest.status = QuestStatus.AVAILABLE
                for obj in quest.objectives:
                    obj.current = 0
                if quest.id in self.active_quests:
                    self.active_quests.remove(quest.id)
                if quest.id in self.completed_quests:
                    self.completed_quests.remove(quest.id)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for saving."""
        quest_data = {}
        for quest_id, quest in self.quests.items():
            quest_data[quest_id] = {
                'status': quest.status.name,
                'objectives': [
                    {'id': obj.id, 'current': obj.current}
                    for obj in quest.objectives
                ]
            }
        
        return {
            'quests': quest_data,
            'active': self.active_quests.copy(),
            'completed': list(self.completed_quests),
            'counters': self.quest_counters.copy()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'QuestManager':
        """Create from dictionary."""
        manager = cls()
        
        # Restore quest states
        quest_data = data.get('quests', {})
        for quest_id, qdata in quest_data.items():
            if quest_id in manager.quests:
                quest = manager.quests[quest_id]
                quest.status = QuestStatus[qdata['status']]
                
                # Restore objective progress
                for obj_data in qdata.get('objectives', []):
                    for obj in quest.objectives:
                        if obj.id == obj_data['id']:
                            obj.current = obj_data['current']
        
        manager.active_quests = data.get('active', []).copy()
        manager.completed_quests = set(data.get('completed', []))
        manager.quest_counters = data.get('counters', {}).copy()
        
        return manager
