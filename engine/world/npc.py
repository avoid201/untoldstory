"""
NPC System für Untold Story
Definiert alle wichtigen NPCs und ihre Dialoge
"""

from engine.world.entity import Entity, EntitySprite
from engine.ui.dialogue import DialoguePage
from typing import List, Callable, Optional, Dict, Any
import os


class NPC(Entity):
    """Basis-Klasse für alle NPCs"""
    
    def __init__(self, x: float, y: float, name: str, sprite_path: str = None):
        # Korrigiere den Standard-Sprite-Pfad
        default_sprite = "npc_01.png" if sprite_path is None else sprite_path
        
        sprite_config = EntitySprite(
            sheet_path=default_sprite,
            frame_width=64,  # Korrigiert: 64x64 Pixel Sprites
            frame_height=64  # Korrigiert: 64x64 Pixel Sprites
        )
        super().__init__(x, y, 56, 56, sprite_config)  # Korrigiert: 56x56 Pixel für 64x64 Tiles
        
        self.name = name
        self.interactable = True
        self.dialogue_pages: List[DialoguePage] = []
        self.interaction_callback: Optional[Callable] = None
        self.conditions: Dict[str, Any] = {}
        
        # Load sprite after initialization
        self._load_npc_sprite(sprite_path or "npc_01.png")
    
    def _load_npc_sprite(self, sprite_name: str) -> None:
        """Load the NPC sprite using the sprite manager or direct file loading."""
        try:
            # Versuche zuerst den SpriteManager zu verwenden
            if hasattr(self, 'game') and hasattr(self.game, 'sprite_manager'):
                sprite_manager = self.game.sprite_manager
                if sprite_manager:
                    sprite = sprite_manager.get_npc_sprite(sprite_name)
                    if sprite:
                        self.sprite_config.surface = sprite
                        self.sprite_surface = sprite
                        print(f"NPC sprite loaded via SpriteManager: {sprite_name}")
                        return
            
            # Fallback: Versuche direkt aus der Datei zu laden
            sprite_path = f"sprites/npcs/{sprite_name}"
            if os.path.exists(sprite_path):
                import pygame
                sprite = pygame.image.load(sprite_path).convert_alpha()
                if sprite:
                    self.sprite_config.surface = sprite
                    self.sprite_surface = sprite
                    print(f"NPC sprite loaded directly: {sprite_name} ({sprite.get_size()})")
                    return
            
            print(f"Failed to load NPC sprite: {sprite_name}")
        except Exception as e:
            print(f"Error loading NPC sprite {sprite_name}: {e}")
    
    def set_dialogue(self, pages: List[DialoguePage]):
        """Setzt die Dialog-Seiten für diesen NPC"""
        self.dialogue_pages = pages
    
    def get_dialogue(self, story_manager) -> List[DialoguePage]:
        """Gibt kontextabhängige Dialoge zurück"""
        # Überschreibe in Subklassen für dynamische Dialoge
        return self.dialogue_pages
    
    def on_interact(self, interactor: Entity) -> bool:
        """Wird aufgerufen wenn der Spieler interagiert"""
        if self.interaction_callback:
            self.interaction_callback(self, interactor)
        return True


class ProfessorBudde(NPC):
    """Professor Budde - gibt dem Spieler das erste Monster"""
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y, "Professor Budde", "elder.png")  # Verwendet den korrekten Dateipfad
        self.given_starter = False
    
    def get_dialogue(self, story_manager) -> List[DialoguePage]:
        """Gibt kontextabhängige Dialoge zurück"""
        
        # Spieler hat noch kein Starter
        if not story_manager.get_flag('has_starter'):
            if not story_manager.get_flag('met_professor'):
                # Erstes Treffen
                return [
                    DialoguePage(
                        "Ach, guten Tag! Du bist bestimmt der junge Mann aus der Nachbarschaft!",
                        "Prof. Budde"
                    ),
                    DialoguePage(
                        "Ich bin Professor Budde, der führende Fossil-Forscher im Ruhrgebiet!",
                        "Prof. Budde"
                    ),
                    DialoguePage(
                        "Ich hab gehört, du willst auf ne große Reise gehen, wat?",
                        "Prof. Budde"
                    ),
                    DialoguePage(
                        "Da brauchste aber'n Monster als Partner! Sonst wird dat nix!",
                        "Prof. Budde"
                    ),
                    DialoguePage(
                        "Komm, ich hab da wat für dich! Ein frisch wiedererwecktes Fossil-Monster!",
                        "Prof. Budde"
                    ),
                    DialoguePage(
                        "[Du erhältst dein erstes Monster!]",
                        None
                    )
                ]
            else:
                # Wiederholtes Gespräch vor Starter-Wahl
                return [
                    DialoguePage(
                        "Na, haste dir schon überlegt, welches Monster du willst?",
                        "Prof. Budde"
                    ),
                    DialoguePage(
                        "Nimm dir ruhig Zeit, dat is ne wichtige Entscheidung!",
                        "Prof. Budde"
                    )
                ]
        
        # Spieler hat bereits Starter
        else:
            return [
                DialoguePage(
                    f"Na, wie läuft's mit deinem Monster?",
                    "Prof. Budde"
                ),
                DialoguePage(
                    "Pass gut drauf auf! Diese Fossil-Monster sind was ganz Besonderes!",
                    "Prof. Budde"
                ),
                DialoguePage(
                    "Wenn de mehr Monster fangen willst, brauchste Monsterbälle.",
                    "Prof. Budde"
                ),
                DialoguePage(
                    "Die kannste im Laden kaufen. Viel Erfolg, Jung!",
                    "Prof. Budde"
                )
            ]


class RivalKlaus(NPC):
    """Klaus - der Rivale des Spielers"""
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y, "Klaus", "rival.png")  # Entferne sprites/ Prefix
        self.battle_ready = False
    
    def get_dialogue(self, story_manager) -> List[DialoguePage]:
        """Gibt kontextabhängige Dialoge zurück"""
        
        # Vor dem ersten Kampf
        if not story_manager.get_flag('rival_first_battle'):
            if not story_manager.get_flag('met_rival'):
                # Erstes Treffen
                return [
                    DialoguePage(
                        "Ey, warte mal! Du bist doch der aus der Nachbarschaft!",
                        "Klaus"
                    ),
                    DialoguePage(
                        "Ich bin Klaus! Ich hab auch grad mein erstes Monster vom Professor bekommen!",
                        "Klaus"
                    ),
                    DialoguePage(
                        "Ein Feuer-Typ! Voll stark, sach ich dir!",
                        "Klaus"
                    ),
                    DialoguePage(
                        "Lass uns kämpfen! Ich will sehen, wat dein Monster so drauf hat!",
                        "Klaus"
                    ),
                    DialoguePage(
                        "[Klaus fordert dich zu einem Kampf heraus!]",
                        None
                    )
                ]
            else:
                # Bereit zum Kampf
                return [
                    DialoguePage(
                        "Na, traust dich wohl nicht, wat?",
                        "Klaus"
                    ),
                    DialoguePage(
                        "Komm schon, lass uns kämpfen!",
                        "Klaus"
                    )
                ]
        
        # Nach dem ersten Kampf
        else:
            if story_manager.variables.get('rival_won_first', False):
                # Spieler hat verloren
                return [
                    DialoguePage(
                        "Haha! Ich hab's dir doch gesagt!",
                        "Klaus"
                    ),
                    DialoguePage(
                        "Mein Monster ist das stärkste!",
                        "Klaus"
                    ),
                    DialoguePage(
                        "Trainier mal'n bisschen, dann können wir nochmal kämpfen!",
                        "Klaus"
                    )
                ]
            else:
                # Spieler hat gewonnen
                return [
                    DialoguePage(
                        "Mann, du bist echt stark!",
                        "Klaus"
                    ),
                    DialoguePage(
                        "Aber wart's ab, beim nächsten Mal gewinne ich!",
                        "Klaus"
                    ),
                    DialoguePage(
                        "Ich werd trainieren und dann zeig ich's dir!",
                        "Klaus"
                    )
                ]
