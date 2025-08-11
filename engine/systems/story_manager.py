"""
Story Manager für Untold Story
Verwaltet Story-Flags, Quest-Fortschritt und Spielereignisse
"""

import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict


@dataclass
class Quest:
    """Repräsentiert eine Quest im Spiel"""
    id: str
    name: str
    description: str
    objectives: List[str]
    current_objective: int = 0
    completed: bool = False
    rewards: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.rewards is None:
            self.rewards = {}
    
    def advance_objective(self):
        """Schreitet zur nächsten Quest-Objective fort"""
        if self.current_objective < len(self.objectives) - 1:
            self.current_objective += 1
        else:
            self.completed = True
    
    def get_current_objective(self) -> str:
        """Gibt das aktuelle Ziel zurück"""
        if self.current_objective < len(self.objectives):
            return self.objectives[self.current_objective]
        return "Quest abgeschlossen!"


class StoryManager:
    """Verwaltet den Story-Fortschritt und Events"""
    
    def __init__(self):
        self.flags: Dict[str, bool] = {}
        self.variables: Dict[str, Any] = {}
        self.quests: Dict[str, Quest] = {}
        self.current_chapter = "prologue"
        
        # Initialisiere Haupt-Story-Flags
        self._init_story_flags()
        
        # Initialisiere Quests
        self._init_quests()
    
    def _init_story_flags(self):
        """Initialisiert die wichtigsten Story-Flags"""
        self.flags = {
            # Spielbeginn
            'game_started': False,
            'first_awakening': False,
            'left_house_first_time': False,
            
            # Professor & Starter
            'met_professor': False,
            'professor_intro_done': False,
            'has_starter': False,
            'starter_chosen': False,
            
            # Rivale
            'met_rival': False,
            'rival_first_battle': False,
            'rival_battles_won': 0,
            
            # Tutorial
            'tutorial_movement': False,
            'tutorial_battle': False,
            'tutorial_catching': False,
            
            # Orte besucht
            'visited_kohlenstadt': False,
            'visited_museum': False,
            'visited_route1': False,
            
            # Items erhalten
            'received_pokeballs': False,
            'received_pokedex': False,
        }
    
    def _init_quests(self):
        """Initialisiert die Hauptquests"""
        self.quests = {
            'main_story': Quest(
                id='main_story',
                name='Die Reise beginnt',
                description='Beginne deine Reise als Monster-Trainer im Ruhrgebiet!',
                objectives=[
                    'Verlasse dein Haus',
                    'Besuche Professor Budde im Museum',
                    'Wähle dein Starter-Monster',
                    'Besiege deinen Rivalen Klaus',
                    'Erreiche Route 1'
                ],
                current_objective=0
            ),
            
            'starter_quest': Quest(
                id='starter_quest',
                name='Dein erstes Monster',
                description='Professor Budde hat ein wiedererwecktes Fossil-Monster für dich!',
                objectives=[
                    'Gehe zum Museum in Kohlenstadt',
                    'Sprich mit Professor Budde',
                    'Wähle dein Starter-Monster'
                ],
                rewards={'items': ['pokeball', 5], 'money': 500}
            )
        }
    
    def get_flag(self, flag_name: str) -> bool:
        """Gibt den Wert eines Story-Flags zurück"""
        return self.flags.get(flag_name, False)
    
    def set_flag(self, flag_name: str, value: bool = True):
        """Setzt einen Story-Flag"""
        self.flags[flag_name] = value
        print(f"Story Flag gesetzt: {flag_name} = {value}")
        
        # Trigger Story-Events basierend auf Flags
        self._check_story_triggers(flag_name)
    
    def _check_story_triggers(self, flag_name: str):
        """Prüft ob Story-Events getriggert werden sollten"""
        # Spieler hat das Haus zum ersten Mal verlassen
        if flag_name == 'left_house_first_time' and self.get_flag('left_house_first_time'):
            self.advance_quest('main_story')
            self.set_flag('visited_kohlenstadt', True)
        
        # Spieler hat Starter erhalten
        elif flag_name == 'has_starter' and self.get_flag('has_starter'):
            self.complete_quest('starter_quest')
            self.advance_quest('main_story')
            self.advance_quest('main_story')  # Skip "Besuche Professor"
            self.advance_quest('main_story')  # Skip "Wähle Monster"
        
        # Spieler hat Rivalen besiegt
        elif flag_name == 'rival_first_battle' and self.get_flag('rival_first_battle'):
            self.advance_quest('main_story')
    
    def advance_quest(self, quest_id: str):
        """Schreitet in einer Quest voran"""
        if quest_id in self.quests:
            self.quests[quest_id].advance_objective()
            print(f"Quest '{quest_id}' fortgeschritten!")
    
    def complete_quest(self, quest_id: str):
        """Schließt eine Quest ab"""
        if quest_id in self.quests:
            self.quests[quest_id].completed = True
            print(f"Quest '{quest_id}' abgeschlossen!")
            
            # Gebe Belohnungen
            rewards = self.quests[quest_id].rewards
            if rewards:
                print(f"Belohnungen erhalten: {rewards}")
                # TODO: Tatsächlich Belohnungen geben
    
    def get_current_objective(self) -> str:
        """Gibt das aktuelle Hauptziel zurück"""
        main_quest = self.quests.get('main_story')
        if main_quest and not main_quest.completed:
            return main_quest.get_current_objective()
        return "Erkunde die Welt!"
    
    def should_spawn_rival(self) -> bool:
        """Prüft ob der Rivale spawnen sollte"""
        return (self.get_flag('has_starter') and 
                not self.get_flag('rival_first_battle') and
                self.get_flag('visited_museum'))
    
    def save(self) -> Dict[str, Any]:
        """Speichert den Story-Fortschritt"""
        return {
            'flags': self.flags,
            'variables': self.variables,
            'quests': {qid: asdict(quest) for qid, quest in self.quests.items()},
            'chapter': self.current_chapter
        }
    
    def load(self, data: Dict[str, Any]):
        """Lädt den Story-Fortschritt"""
        self.flags = data.get('flags', {})
        self.variables = data.get('variables', {})
        self.current_chapter = data.get('chapter', 'prologue')
        
        # Lade Quests
        quests_data = data.get('quests', {})
        for qid, qdata in quests_data.items():
            self.quests[qid] = Quest(**qdata)
