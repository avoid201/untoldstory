"""
Movement States für das Grid-basierte Movement System
Vermeidet zirkuläre Imports zwischen player.py und ledge_handler.py
"""

from enum import Enum


class MovementState(Enum):
    """Bewegungszustände des Spielers"""
    IDLE = "idle"           # Steht still
    TURNING = "turning"     # Dreht sich nur um
    WALKING = "walking"     # Läuft normal
    RUNNING = "running"     # Rennt (mit B-Taste)
    SLIDING = "sliding"     # Rutscht (Eis, etc.)
    JUMPING = "jumping"     # Springt über Kante
    WARPING = "warping"     # Teleportiert gerade
    LOCKED = "locked"       # Bewegung gesperrt (Cutscene, Dialog)
