"""
Story system for managing plot progression, flags, and cutscenes.
"""

from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass, field
from enum import Enum, auto
import json


class StoryPhase(Enum):
    """Main story phases."""
    PROLOGUE = auto()          # Getting starter
    EARLY_GAME = auto()        # First 3 Trias
    MID_GAME = auto()          # Trias 4-6, time rifts appear
    LATE_GAME = auto()         # Trias 7-10, antagonist revealed
    ENDGAME = auto()           # Final confrontation
    POSTGAME = auto()          # After main story


@dataclass
class StoryFlag:
    """A single story flag."""
    id: str
    name: str
    description: str
    value: Any = False
    persistent: bool = True  # Survives save/load
    
    def set(self, value: Any = True) -> None:
        """Set flag value."""
        self.value = value
    
    def get(self) -> Any:
        """Get flag value."""
        return self.value
    
    def toggle(self) -> None:
        """Toggle boolean flag."""
        if isinstance(self.value, bool):
            self.value = not self.value


@dataclass 
class CutsceneScript:
    """Script for a cutscene."""
    id: str
    name: str
    trigger_flag: Optional[str] = None
    required_flags: List[str] = field(default_factory=list)
    forbidden_flags: List[str] = field(default_factory=list)
    commands: List[Dict[str, Any]] = field(default_factory=list)
    sets_flags: List[str] = field(default_factory=list)
    one_time: bool = True


class StoryManager:
    """Manages story progression and flags."""
    
    def __init__(self):
        """Initialize story manager."""
        self.flags: Dict[str, StoryFlag] = {}
        self.phase = StoryPhase.PROLOGUE
        self.scripts: Dict[str, CutsceneScript] = {}
        self.completed_scripts: Set[str] = set()
        self.trials_completed = 0
        self.rival_battles_won = 0
        self.time_rifts_closed = 0
        
        # Initialize core flags
        self._init_core_flags()
        self._init_scripts()
    
    def reset(self) -> None:
        """Reset all story flags for new game."""
        self.flags.clear()
        self.phase = StoryPhase.PROLOGUE
        self.completed_scripts.clear()
        self.trials_completed = 0
        self.rival_battles_won = 0
        self.time_rifts_closed = 0
        self._init_core_flags()
        self._init_scripts()
    
    def _init_core_flags(self) -> None:
        """Initialize core story flags."""
        # Prologue flags
        self.add_flag('intro_complete', 'Intro abgeschlossen', 
                     'Spieler hat das Intro gesehen')
        self.add_flag('has_starter', 'Starter erhalten',
                     'Spieler hat sein erstes Monster')
        self.add_flag('starter_choice', 'Starter-Wahl',
                     'ID des gewählten Starters', value='')
        self.add_flag('met_professor', 'Professor getroffen',
                     'Spieler hat Professor Budde getroffen')
        self.add_flag('can_leave_town', 'Kann Stadt verlassen',
                     'Spieler darf Kohlenstadt verlassen')
        self.add_flag('left_house_first_time', 'Haus zum ersten Mal verlassen',
                     'Spieler hat das Haus zum ersten Mal verlassen')
        self.add_flag('game_started', 'Spiel gestartet',
                     'Spieler hat ein neues Spiel gestartet')
        self.add_flag('first_awakening', 'Erstes Aufwachen',
                     'Spieler wacht zum ersten Mal auf')
        self.add_flag('professor_intro_started', 'Professor Intro gestartet',
                     'Der Professor hat seine Einführung begonnen')
        self.add_flag('rival_first_encounter', 'Erste Begegnung mit Rivalen',
                     'Spieler hat Klaus zum ersten Mal getroffen')
        
        # Trial flags (10 trials/challenges)
        for i in range(1, 11):
            self.add_flag(f'trial_{i}_available', f'Prüfung {i} verfügbar',
                         f'Prüfung {i} kann angetreten werden')
            self.add_flag(f'trial_{i}_defeated', f'Prüfung {i} bestanden',
                         f'Spieler hat Prüfung {i} bestanden')
        
        # Time rift flags
        self.add_flag('time_rifts_discovered', 'Zeitrisse entdeckt',
                     'Erste Zeitrisse sind aufgetaucht')
        self.add_flag('timerifts_started', 'Zeitrisse gestartet',
                     'Zeitrisse sind aktiv')
        self.add_flag('future_monsters_appearing', 'Zukunftsmonster erscheinen',
                     'Monster aus der Zukunft tauchen auf')
        self.add_flag('antagonist_revealed', 'Antagonist enthüllt',
                     'Identität des Antagonisten bekannt')
        self.add_flag('professor_kidnapped', 'Professor entführt',
                     'Professor Budde wurde entführt')
        self.add_flag('professor_rescued', 'Professor gerettet',
                     'Professor Budde wurde gerettet')
        
        # Rival flags
        self.add_flag('rival_name', 'Name des Rivalen',
                     'Name des Rivalen', value='Kai')
        self.add_flag('rival_intro', 'Rivale vorgestellt',
                     'Spieler hat Rivalen getroffen')
        for i in range(1, 6):
            self.add_flag(f'rival_battle_{i}', f'Rivalenkampf {i}',
                         f'Rivalenkampf {i} gewonnen')
        
        # Location access flags
        locations = [
            'route_1', 'zeche_zollverein', 'ruhr_ufer', 
            'industriepark', 'signal_iduna_park', 'baldeneysee',
            'botanischer_garten', 'bergwerk', 'zukunfts_portal'
        ]
        for loc in locations:
            self.add_flag(f'{loc}_unlocked', f'{loc} freigeschaltet',
                         f'Zugang zu {loc}')
        
        # Item flags
        self.add_flag('has_map', 'Karte erhalten',
                     'Spieler hat die Regionskarte')
        self.add_flag('has_time_scanner', 'Zeitscanner erhalten',
                     'Kann Zeitrisse aufspüren')
        self.add_flag('has_master_ball', 'Meisterball erhalten',
                     'Hat den Meisterball')
        
        # Special events
        self.add_flag('legendary_quest_started', 'Legendäre Quest gestartet',
                     'Quest für legendäre Monster begonnen')
        self.add_flag('secret_lab_discovered', 'Geheimlabor entdeckt',
                     'Antagonisten-Labor gefunden')
        self.add_flag('time_machine_activated', 'Zeitmaschine aktiviert',
                     'Zeitmaschine wurde aktiviert')
    
    def _init_scripts(self) -> None:
        """Initialize cutscene scripts."""
        # Prologue scripts
        self.add_script(CutsceneScript(
            id='intro_cutscene',
            name='Spielbeginn',
            commands=[
                {'type': 'dialogue', 'speaker': 'Professor Budde', 
                 'text': 'Ey, willkommen in der Welt der Monster, wa!'},
                {'type': 'dialogue', 'speaker': 'Professor Budde',
                 'text': 'Ich bin Professor Budde, der Experte für fossile Monster hier im Pott.'},
                {'type': 'fade', 'duration': 1.0},
                {'type': 'move_player', 'to': 'player_house'}
            ],
            sets_flags=['intro_complete'],
            one_time=True
        ))
        
        self.add_script(CutsceneScript(
            id='get_starter',
            name='Starter erhalten',
            required_flags=['met_professor'],
            forbidden_flags=['has_starter'],
            commands=[
                {'type': 'dialogue', 'speaker': 'Professor Budde',
                 'text': 'So, jetzt wirds ernst! Such dir eins von den Fossilien aus!'},
                {'type': 'choice', 'options': [
                    'Glutkohle - Feuer-Typ',
                    'Tropfstein - Wasser-Typ', 
                    'Lehmling - Erde-Typ',
                    'Windei - Luft-Typ'
                ]},
                {'type': 'give_monster', 'species': '{choice}', 'level': 5},
                {'type': 'dialogue', 'speaker': 'Professor Budde',
                 'text': 'Gute Wahl! Pass gut auf dein Monster auf, ne!'}
            ],
            sets_flags=['has_starter', 'can_leave_town'],
            one_time=True
        ))
        
        self.add_script(CutsceneScript(
            id='rival_intro',
            name='Rivale trifft ein',
            required_flags=['has_starter'],
            forbidden_flags=['rival_intro'],
            commands=[
                {'type': 'dialogue', 'speaker': '???',
                 'text': 'Ey, warte mal! Du hast auch\'n Monster bekommen?'},
                {'type': 'dialogue', 'speaker': 'Kai',
                 'text': 'Ich bin Kai! Lass uns kämpfen, dann seh ich wie stark du bist!'},
                {'type': 'battle', 'trainer': 'rival_1'},
                {'type': 'dialogue', 'speaker': 'Kai',
                 'text': 'Boah, dat war ja ma voll krass! Wir sehn uns!'}
            ],
            sets_flags=['rival_intro'],
            one_time=True
        ))
        
        # Mid-game scripts
        self.add_script(CutsceneScript(
            id='time_rifts_appear',
            name='Zeitrisse erscheinen',
            required_flags=['trial_3_defeated'],
            forbidden_flags=['time_rifts_discovered'],
            commands=[
                {'type': 'shake_screen', 'duration': 2.0},
                {'type': 'dialogue', 'speaker': 'System',
                 'text': 'Der Himmel reißt auf! Seltsame Portale erscheinen!'},
                {'type': 'spawn_object', 'type': 'time_rift', 'location': 'current'},
                {'type': 'dialogue', 'speaker': 'Professor Budde',
                 'text': 'Wat is dat denn?! Ruf mich ma an, ich muss dat untersuchen!'}
            ],
            sets_flags=['time_rifts_discovered', 'future_monsters_appearing'],
            one_time=True
        ))
        
        self.add_script(CutsceneScript(
            id='antagonist_reveal',
            name='Antagonist Enthüllung',
            required_flags=['trial_6_defeated', 'time_rifts_discovered'],
            forbidden_flags=['antagonist_revealed'],
            commands=[
                {'type': 'dialogue', 'speaker': 'Mysteriöse Gestalt',
                 'text': 'Ihr versteht nicht, was auf dem Spiel steht!'},
                {'type': 'dialogue', 'speaker': 'Dr. Schatten',
                 'text': 'Die Monster der Zukunft sind stärker! Wir brauchen sie JETZT!'},
                {'type': 'dialogue', 'speaker': 'Dr. Schatten',
                 'text': 'Team Temporal wird die Zeitlinie neu schreiben!'},
                {'type': 'battle', 'trainer': 'temporal_admin_1'}
            ],
            sets_flags=['antagonist_revealed'],
            one_time=True
        ))
        
        # Endgame scripts
        self.add_script(CutsceneScript(
            id='final_confrontation',
            name='Finaler Kampf',
            required_flags=['trial_10_defeated', 'professor_rescued'],
            commands=[
                {'type': 'dialogue', 'speaker': 'Dr. Schatten',
                 'text': 'Du hast meine Pläne durchkreuzt, aber es ist zu spät!'},
                {'type': 'dialogue', 'speaker': 'Dr. Schatten',
                 'text': 'Die Zeitmaschine ist aktiv! Die Zukunft wird die Gegenwart verschlingen!'},
                {'type': 'battle', 'trainer': 'dr_schatten_final'},
                {'type': 'dialogue', 'speaker': 'Professor Budde',
                 'text': 'Du hast es geschafft! Die Zeitlinie ist gerettet!'},
                {'type': 'credits'}
            ],
            sets_flags=['main_story_complete'],
            one_time=True
        ))
    
    def add_flag(self, flag_id: str, name: str, description: str,
                 value: Any = False, persistent: bool = True) -> None:
        """Add a story flag."""
        self.flags[flag_id] = StoryFlag(
            id=flag_id,
            name=name,
            description=description,
            value=value,
            persistent=persistent
        )
    
    def get_flag(self, flag_id: str) -> Any:
        """Get a flag value."""
        if flag_id in self.flags:
            return self.flags[flag_id].get()
        return None
    
    def set_flag(self, flag_id: str, value: Any = True) -> None:
        """Set a flag value."""
        if flag_id in self.flags:
            self.flags[flag_id].set(value)
            self._check_phase_progression()
    
    def has_flag(self, flag_id: str, value: Any = True) -> bool:
        """Check if a flag has a specific value."""
        return self.get_flag(flag_id) == value
    
    def add_script(self, script: CutsceneScript) -> None:
        """Add a cutscene script."""
        self.scripts[script.id] = script
    
    def can_trigger_script(self, script_id: str) -> bool:
        """Check if a script can be triggered."""
        if script_id not in self.scripts:
            return False
        
        script = self.scripts[script_id]
        
        # Check if already completed and one-time only
        if script.one_time and script_id in self.completed_scripts:
            return False
        
        # Check required flags
        for flag in script.required_flags:
            if not self.has_flag(flag):
                return False
        
        # Check forbidden flags
        for flag in script.forbidden_flags:
            if self.has_flag(flag):
                return False
        
        return True
    
    def trigger_script(self, script_id: str) -> Optional[CutsceneScript]:
        """
        Trigger a cutscene script.
        
        Args:
            script_id: Script to trigger
            
        Returns:
            Script if triggered, None otherwise
        """
        if not self.can_trigger_script(script_id):
            return None
        
        script = self.scripts[script_id]
        
        # Mark as completed
        if script.one_time:
            self.completed_scripts.add(script_id)
        
        # Set flags
        for flag in script.sets_flags:
            self.set_flag(flag, True)
        
        return script
    
    def _check_phase_progression(self) -> None:
        """Check and update story phase."""
        # Count completed trials
        self.trials_completed = sum(1 for i in range(1, 11) 
                                  if self.has_flag(f'trial_{i}_defeated'))
        
        # Determine phase
        if not self.has_flag('has_starter'):
            self.phase = StoryPhase.PROLOGUE
        elif self.trials_completed < 3:
            self.phase = StoryPhase.EARLY_GAME
        elif self.trials_completed < 6:
            self.phase = StoryPhase.MID_GAME
        elif self.trials_completed < 10:
            self.phase = StoryPhase.LATE_GAME
        elif self.has_flag('main_story_complete'):
            self.phase = StoryPhase.POSTGAME
        else:
            self.phase = StoryPhase.ENDGAME
    
    def get_next_objective(self) -> str:
        """Get the next story objective."""
        if self.phase == StoryPhase.PROLOGUE:
            if not self.has_flag('met_professor'):
                return "Geh zum Museum und triff Professor Budde!"
            elif not self.has_flag('has_starter'):
                return "Wähle dein erstes Monster!"
            else:
                return "Verlasse Kohlenstadt und beginne dein Abenteuer!"
        
        elif self.phase == StoryPhase.EARLY_GAME:
            for i in range(1, 4):
                if not self.has_flag(f'trial_{i}_defeated'):
                    return f"Bestehe die {i}. Prüfung!"
            return "Erkunde die Region!"
        
        elif self.phase == StoryPhase.MID_GAME:
            if not self.has_flag('time_rifts_discovered'):
                return "Setze deine Prüfungen fort!"
            else:
                return "Untersuche die mysteriösen Zeitrisse!"
        
        elif self.phase == StoryPhase.LATE_GAME:
            if self.has_flag('professor_kidnapped') and not self.has_flag('professor_rescued'):
                return "Rette Professor Budde!"
            else:
                return f"Bestehe die restlichen Prüfungen! ({self.trials_completed}/10)"
        
        elif self.phase == StoryPhase.ENDGAME:
            return "Konfrontiere Dr. Schatten und rette die Zeitlinie!"
        
        else:  # POSTGAME
            return "Erkunde die Welt und fange legendäre Monster!"
    
    def unlock_location(self, location: str) -> None:
        """Unlock a location."""
        self.set_flag(f'{location}_unlocked', True)
    
    def is_location_unlocked(self, location: str) -> bool:
        """Check if a location is unlocked."""
        return self.has_flag(f'{location}_unlocked')
    
    def complete_trial(self, trial_number: int) -> None:
        """Mark a trial as completed."""
        self.set_flag(f'trial_{trial_number}_defeated', True)
        
        # Unlock next areas based on progression
        if trial_number == 1:
            self.unlock_location('route_2')
            self.unlock_location('zeche_zollverein')
        elif trial_number == 3:
            self.unlock_location('industriepark')
            self.unlock_location('ruhr_ufer')
        elif trial_number == 5:
            self.unlock_location('baldeneysee')
        elif trial_number == 7:
            self.unlock_location('bergwerk')
        elif trial_number == 9:
            self.unlock_location('zukunfts_portal')
    
    def close_time_rift(self) -> None:
        """Close a time rift."""
        self.time_rifts_closed += 1
        
        # Special events at certain milestones
        if self.time_rifts_closed == 3:
            self.set_flag('time_scanner_upgraded', True)
        elif self.time_rifts_closed == 5:
            self.set_flag('legendary_quest_started', True)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for saving."""
        return {
            'flags': {fid: f.value for fid, f in self.flags.items() if f.persistent},
            'phase': self.phase.name,
            'completed_scripts': list(self.completed_scripts),
            'trials_completed': self.trials_completed,
            'rival_battles_won': self.rival_battles_won,
            'time_rifts_closed': self.time_rifts_closed
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'StoryManager':
        """Create from dictionary."""
        manager = cls()
        
        # Restore flags
        for flag_id, value in data.get('flags', {}).items():
            if flag_id in manager.flags:
                manager.flags[flag_id].value = value
        
        # Restore phase
        phase_name = data.get('phase', 'PROLOGUE')
        manager.phase = StoryPhase[phase_name]
        
        # Restore completed scripts
        manager.completed_scripts = set(data.get('completed_scripts', []))
        
        # Restore counters
        manager.trials_completed = data.get('trials_completed', 0)
        manager.rival_battles_won = data.get('rival_battles_won', 0)
        manager.time_rifts_closed = data.get('time_rifts_closed', 0)
        
        return manager


class DialogueManager:
    """Manages NPC dialogues based on story progression."""
    
    def __init__(self, story_manager: StoryManager):
        """
        Initialize dialogue manager.
        
        Args:
            story_manager: Reference to story manager
        """
        self.story = story_manager
        self.dialogues: Dict[str, List[Dict]] = {}
        self._load_dialogues()
    
    def _load_dialogues(self) -> None:
        """Load NPC dialogues."""
        # Professor Budde
        self.dialogues['professor_budde'] = [
            {
                'conditions': [],
                'text': "Ey, willkommen im Labor! Ich bin Professor Budde, wa!"
            },
            {
                'conditions': ['has_starter'],
                'text': "Na, wie läuft's mit deinem Monster? Passt auf euch auf, ne!"
            },
            {
                'conditions': ['time_rifts_discovered'],
                'text': "Diese Zeitrisse... dat is nich normal! Da stimmt wat nich!"
            },
            {
                'conditions': ['professor_rescued'],
                'text': "Danke, dass du mich gerettet hast! Du bist'n echter Held!"
            }
        ]
        
        # Rival Kai
        self.dialogues['rival_kai'] = [
            {
                'conditions': [],
                'text': "Ey, ich bin Kai! Lass uns kämpfen!"
            },
            {
                'conditions': ['rival_battle_1'],
                'text': "Du wirst immer stärker! Aber ich auch, pass auf!"
            },
            {
                'conditions': ['antagonist_revealed'],
                'text': "Team Temporal... die sind echt gefährlich. Wir müssen sie stoppen!"
            }
        ]
        
        # Random NPCs
        self.dialogues['npc_town_1'] = [
            {
                'conditions': [],
                'text': "Willkommen in Kohlenstadt! Hier hat alles mit dem Bergbau angefangen!"
            },
            {
                'conditions': ['has_starter'],
                'text': "Oh, du hast ein Monster! Pass auf, draußen ist es gefährlich!"
            },
            {
                'conditions': ['time_rifts_discovered'],
                'text': "Haste die komischen Risse am Himmel gesehen? Dat macht mir Angst!"
            }
        ]
        
        self.dialogues['npc_town_2'] = [
            {
                'conditions': [],
                'text': "Früher war hier alles voller Kohle. Jetzt haben wir Monster!"
            },
            {
                'conditions': ['trias_1_defeated'],
                'text': "Du hast die erste Prüfung bestanden? Respekt, Alter!"
            }
        ]
        
        # Shop keeper
        self.dialogues['shop_keeper'] = [
            {
                'conditions': [],
                'text': "Tach auch! Brauchste wat aus'm Laden?"
            },
            {
                'conditions': ['trial_3_defeated'],
                'text': "Für'n Champion wie dich hab ich Rabatt! 10% auf alles!"
            }
        ]
        
        # Nurse (Healing center)
        self.dialogues['nurse'] = [
            {
                'conditions': [],
                'text': "Willkommen im Bergmannsheil! Soll ich deine Monster heilen?"
            },
            {
                'conditions': ['time_rifts_discovered'],
                'text': "Mit den Zeitrissen kommen immer mehr verletzte Monster... Pass auf dich auf!"
            }
        ]
    
    def get_dialogue(self, npc_id: str) -> str:
        """
        Get appropriate dialogue for an NPC.
        
        Args:
            npc_id: NPC identifier
            
        Returns:
            Dialogue text
        """
        if npc_id not in self.dialogues:
            return "..."
        
        dialogues = self.dialogues[npc_id]
        
        # Find the best matching dialogue
        for dialogue in reversed(dialogues):
            conditions = dialogue.get('conditions', [])
            
            # Check if all conditions are met
            if all(self.story.has_flag(cond) for cond in conditions):
                return dialogue['text']
        
        # Return first dialogue as fallback
        return dialogues[0]['text'] if dialogues else "..."
    
    def add_dialogue(self, npc_id: str, conditions: List[str], text: str) -> None:
        """Add a dialogue option for an NPC."""
        if npc_id not in self.dialogues:
            self.dialogues[npc_id] = []
        
        self.dialogues[npc_id].append({
            'conditions': conditions,
            'text': text
        })


class CutscenePlayer:
    """Plays cutscene scripts."""
    
    def __init__(self, game_context: Any):
        """
        Initialize cutscene player.
        
        Args:
            game_context: Reference to game context for executing commands
        """
        self.game = game_context
        self.current_script: Optional[CutsceneScript] = None
        self.command_index = 0
        self.waiting = False
        self.wait_timer = 0
    
    def start_cutscene(self, script: CutsceneScript) -> None:
        """Start playing a cutscene."""
        self.current_script = script
        self.command_index = 0
        self.waiting = False
        self.wait_timer = 0
    
    def update(self, dt: float) -> None:
        """Update cutscene playback."""
        if not self.current_script:
            return
        
        # Handle wait timer
        if self.waiting and self.wait_timer > 0:
            self.wait_timer -= dt
            if self.wait_timer <= 0:
                self.waiting = False
                self.command_index += 1
            return
        
        # Execute commands
        while self.command_index < len(self.current_script.commands):
            command = self.current_script.commands[self.command_index]
            
            if self._execute_command(command):
                # Command requires waiting
                break
            
            self.command_index += 1
        
        # Check if cutscene is complete
        if self.command_index >= len(self.current_script.commands):
            self.end_cutscene()
    
    def _execute_command(self, command: Dict) -> bool:
        """
        Execute a single command.
        
        Returns:
            True if command requires waiting
        """
        cmd_type = command['type']
        
        if cmd_type == 'dialogue':
            # Show dialogue box
            speaker = command.get('speaker', '')
            text = command['text']
            # TODO: Show dialogue and wait for player input
            return True
        
        elif cmd_type == 'fade':
            duration = command.get('duration', 1.0)
            # TODO: Start fade transition
            self.waiting = True
            self.wait_timer = duration
            return True
        
        elif cmd_type == 'move_player':
            destination = command['to']
            # TODO: Move player to destination
            return False
        
        elif cmd_type == 'give_monster':
            species_id = command['species']
            level = command.get('level', 5)
            # TODO: Add monster to party
            return False
        
        elif cmd_type == 'battle':
            trainer_id = command['trainer']
            # TODO: Start battle
            return True
        
        elif cmd_type == 'choice':
            options = command['options']
            # TODO: Show choice menu and wait for selection
            return True
        
        elif cmd_type == 'wait':
            duration = command.get('duration', 1.0)
            self.waiting = True
            self.wait_timer = duration
            return True
        
        return False
    
    def skip(self) -> None:
        """Skip current waiting state."""
        if self.waiting:
            self.waiting = False
            self.wait_timer = 0
            self.command_index += 1
    
    def end_cutscene(self) -> None:
        """End the current cutscene."""
        self.current_script = None
        self.command_index = 0
        self.waiting = False
        self.wait_timer = 0
    
    def is_playing(self) -> bool:
        """Check if a cutscene is playing."""
        return self.current_script is not None
