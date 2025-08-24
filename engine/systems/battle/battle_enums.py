"""
Battle Enums and Constants
Contains all battle-related enumerations and constant values
"""

from enum import Enum


class BattleType(Enum):
    """Types of battles."""
    WILD = "wild"              # Wild monster encounter
    TRAINER = "trainer"        # Trainer battle
    RIVAL = "rival"            # Rival battle (special trainer)
    GYM = "gym"               # Gym leader battle
    ELITE = "elite"           # Elite Four battle
    CHAMPION = "champion"      # Champion battle
    LEGENDARY = "legendary"    # Legendary monster battle
    STORY = "story"           # Story-critical battle


class BattlePhase(Enum):
    """Phases of battle."""
    INIT = "init"              # Battle initialization
    START = "start"            # Battle start animations
    INPUT = "input"            # Waiting for player input
    ORDER = "order"            # Determining turn order
    RESOLVE = "resolve"        # Executing actions
    AFTERMATH = "aftermath"    # Processing end-of-turn effects
    SWITCH = "switch"          # Monster switching
    MESSAGE = "message"        # Showing battle messages
    END = "end"               # Battle ending
    REWARD = "reward"         # Giving rewards
    COMPLETE = "complete"     # Battle complete


class BattleCommand(Enum):
    """DQM-style battle commands."""
    ATTACK = "attack"          # Normale Attacke
    SKILL = "skill"           # Skill/Magie verwenden
    DEFEND = "defend"         # Verteidigung (0.5x Schaden)
    SWITCH = "switch"         # Monster wechseln
    ITEM = "item"            # Item benutzen
    FLEE = "flee"            # Flucht versuchen
    
    # DQM Special Commands
    PSYCHE_UP = "psyche"      # Aufladen für nächste Runde (2x Schaden)
    MEDITATE = "meditate"     # MP wiederherstellen
    INTIMIDATE = "intimidate" # Gegner-Stats senken


class AIPersonality(Enum):
    """DQM AI personality types."""
    AGGRESSIVE = "aggressive"  # Fokus auf Angriff
    DEFENSIVE = "defensive"    # Fokus auf Verteidigung
    TACTICAL = "tactical"      # Ausgewogen
    WISE = "wise"             # Analysiert Typen-Effektivität
    HEALER = "healer"         # Priorisiert Heilung
    RECKLESS = "reckless"     # Hoher Schaden, ignoriert Verteidigung
