"""
Verbessertes NPC-System mit Pathfinding und Bewegungsmustern
"""

import pygame
import random
from typing import Optional, List, Tuple, Dict
from enum import Enum
from dataclasses import dataclass
import time

from engine.world.tiles import TILE_SIZE
from engine.world.tile_manager import tile_manager
from engine.world.entity import Entity, EntitySprite, Direction
from engine.ui.dialogue import DialoguePage

class MovementPattern(Enum):
    """NPC-Bewegungsmuster"""
    STATIC = "static"           # Keine Bewegung
    RANDOM = "random"           # Zufällige Bewegung
    PATROL = "patrol"           # Festgelegte Route
    FOLLOW = "follow"           # Folgt dem Spieler
    FLEE = "flee"              # Flieht vor dem Spieler
    WANDER = "wander"          # Erkundet die Umgebung

class Direction(Enum):
    """Richtungen für NPCs"""
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    
    @classmethod
    def from_delta(cls, dx: int, dy: int):
        """Konvertiert Delta zu Direction"""
        if dx > 0:
            return cls.RIGHT
        elif dx < 0:
            return cls.LEFT
        elif dy > 0:
            return cls.DOWN
        elif dy < 0:
            return cls.UP
        return cls.DOWN  # Default

@dataclass
class NPCConfig:
    """Konfiguration für einen NPC"""
    npc_id: str
    sprite_name: str
    dialogue_id: str
    movement_pattern: MovementPattern
    movement_radius: int = 3
    patrol_path: List[Tuple[int, int]] = None
    move_speed: float = 2.0
    is_trainer: bool = False
    sight_range: int = 0
    facing: Direction = Direction.DOWN

class ImprovedNPC:
    """
    Verbesserter NPC mit Pathfinding und intelligenten Bewegungsmustern.
    
    Features:
    - Verschiedene Bewegungsmuster (static, random, patrol, follow, flee, wander)
    - A*-Pathfinding für intelligente Navigation
    - Smooth Movement zwischen Tiles
    - Dialog-System-Integration
    - Trainer-Funktionalität mit Sichtlinien
    - Animations-Support
    """
    
    def __init__(self, tile_x: int, tile_y: int, config: NPCConfig):
        """
        Initialisiert einen NPC.
        
        Args:
            tile_x: X-Position in Tiles
            tile_y: Y-Position in Tiles
            config: NPC-Konfiguration
        """
        # Position (in Pixeln für smooth movement)
        self.x = tile_x * TILE_SIZE
        self.y = tile_y * TILE_SIZE
        self.tile_x = tile_x
        self.tile_y = tile_y
        
        # Zielposition für Bewegung
        self.target_x = self.x
        self.target_y = self.y
        self.target_tile_x = tile_x
        self.target_tile_y = tile_y
        
        # Konfiguration
        self.config = config
        self.npc_id = config.npc_id
        self.sprite_name = config.sprite_name
        self.dialogue_id = config.dialogue_id
        self.movement_pattern = config.movement_pattern
        self.movement_radius = config.movement_radius
        self.move_speed = config.move_speed
        self.is_trainer = config.is_trainer
        self.sight_range = config.sight_range
        self.facing = config.facing
        
        # NPC-Typ für Kompatibilität
        self.npc_type = "trainer" if self.is_trainer else "npc"
        
        # Patrol-Pfad
        self.patrol_path = config.patrol_path or []
        self.patrol_index = 0
        self.patrol_forward = True
        
        # Pathfinding
        self.current_path: List[Tuple[int, int]] = []
        self.path_index = 0
        
        # Movement timing
        self.move_timer = 0.0
        self.move_cooldown = 1.0  # Sekunden zwischen Bewegungen
        self.last_move_time = 0.0
        
        # Animation
        self.animation_timer = 0.0
        self.animation_frame = 0
        self.is_moving = False
        
        # Interaktion
        self.is_interacting = False
        self.has_spotted_player = False
        
        # Wander-Modus
        self.wander_target = None
        self.visited_tiles = set()
        self.home_position = (tile_x, tile_y)
        
        # Sprite (Placeholder)
        self.sprite = self._load_sprite()
    
    def _load_sprite(self) -> pygame.Surface:
        """Lädt den NPC-Sprite"""
        try:
            # Versuche echten Sprite zu laden
            sprite_manager = SpriteManager.get()
            
            # Erstelle Sprite-Namen basierend auf NPC-Typ und ID
            if self.is_trainer:
                sprite_name = f"npc_trainer_{self.npc_id}"
            else:
                sprite_name = f"npc_{self.npc_id}"
            
            # Versuche Sprite zu laden
            sprite = sprite_manager.get_sprite(sprite_name)
            if sprite:
                return sprite
            
            # Fallback: Versuche generischen NPC-Sprite
            generic_sprite = sprite_manager.get_sprite("npc_generic")
            if generic_sprite:
                return generic_sprite
                
        except Exception as e:
            print(f"Fehler beim Laden des NPC-Sprites {self.npc_id}: {e}")
        
        # Fallback: Erstelle Placeholder-Sprite
        surface = pygame.Surface((TILE_SIZE, TILE_SIZE))
        
        # Farbe basierend auf Typ
        if self.is_trainer:
            color = (255, 100, 100)  # Rot für Trainer
        elif self.movement_pattern == MovementPattern.STATIC:
            color = (100, 100, 255)  # Blau für statische NPCs
        else:
            color = (100, 255, 100)  # Grün für bewegliche NPCs
        
        surface.fill(color)
        
        # Zeichne Richtungs-Indikator
        center = TILE_SIZE // 2
        if self.facing == Direction.UP:
            pygame.draw.polygon(surface, (255, 255, 255), 
                              [(center-3, 5), (center+3, 5), (center, 2)])
        elif self.facing == Direction.DOWN:
            pygame.draw.polygon(surface, (255, 255, 255),
                              [(center-3, TILE_SIZE-5), (center+3, TILE_SIZE-5), 
                               (center, TILE_SIZE-2)])
        elif self.facing == Direction.LEFT:
            pygame.draw.polygon(surface, (255, 255, 255),
                              [(5, center-3), (5, center+3), (2, center)])
        elif self.facing == Direction.RIGHT:
            pygame.draw.polygon(surface, (255, 255, 255),
                              [(TILE_SIZE-5, center-3), (TILE_SIZE-5, center+3), 
                               (center, TILE_SIZE-2)])
        
        return surface
    
    def update(self, dt: float, player_pos: Optional[Tuple[int, int]] = None):
        """
        Aktualisiert den NPC.
        
        Args:
            dt: Delta-Zeit in Sekunden
            player_pos: Position des Spielers in Tiles (für follow/flee)
        """
        # Smooth Movement
        if self.x != self.target_x or self.y != self.target_y:
            self._update_smooth_movement(dt)
        else:
            # Bewegung abgeschlossen, prüfe nächsten Schritt
            if self.current_path and self.path_index < len(self.current_path):
                self._move_along_path()
            elif not self.is_interacting:
                # Entscheide über nächste Bewegung
                self._decide_next_move(player_pos)
        
        # Animation Update
        self.animation_timer += dt
        if self.animation_timer > 0.2:  # Animation alle 200ms
            self.animation_timer = 0.0
            self.animation_frame = (self.animation_frame + 1) % 2
    
    def _update_smooth_movement(self, dt: float):
        """Aktualisiert die sanfte Bewegung zwischen Tiles"""
        speed = self.move_speed * TILE_SIZE * dt
        
        # X-Bewegung
        if self.x < self.target_x:
            self.x = min(self.x + speed, self.target_x)
        elif self.x > self.target_x:
            self.x = max(self.x - speed, self.target_x)
        
        # Y-Bewegung
        if self.y < self.target_y:
            self.y = min(self.y + speed, self.target_y)
        elif self.y > self.target_y:
            self.y = max(self.y - speed, self.target_y)
        
        # Update Tile-Position wenn Ziel erreicht
        if self.x == self.target_x and self.y == self.target_y:
            self.tile_x = self.target_tile_x
            self.tile_y = self.target_tile_y
            self.is_moving = False
    
    def _decide_next_move(self, player_pos: Optional[Tuple[int, int]]):
        """Entscheidet über die nächste Bewegung basierend auf dem Bewegungsmuster"""
        current_time = time.time()
        
        # Cooldown prüfen
        if current_time - self.last_move_time < self.move_cooldown:
            return
        
        if self.movement_pattern == MovementPattern.STATIC:
            # Keine Bewegung, nur Richtung ändern manchmal
            if random.random() < 0.1:  # 10% Chance
                self.facing = random.choice(list(Direction))
                
        elif self.movement_pattern == MovementPattern.RANDOM:
            self._move_random()
            
        elif self.movement_pattern == MovementPattern.PATROL:
            self._move_patrol()
            
        elif self.movement_pattern == MovementPattern.FOLLOW and player_pos:
            self._move_follow(player_pos)
            
        elif self.movement_pattern == MovementPattern.FLEE and player_pos:
            self._move_flee(player_pos)
            
        elif self.movement_pattern == MovementPattern.WANDER:
            self._move_wander()
        
        self.last_move_time = current_time
    
    def _move_random(self):
        """Zufällige Bewegung innerhalb des Radius"""
        # Wähle zufällige Richtung
        direction = random.choice(list(Direction))
        dx, dy = direction.value
        
        new_x = self.tile_x + dx
        new_y = self.tile_y + dy
        
        # Prüfe Radius
        dist_from_home = abs(new_x - self.home_position[0]) + abs(new_y - self.home_position[1])
        
        if dist_from_home <= self.movement_radius:
            # Prüfe Kollision
            tile_manager = TileManager.get_instance()
            if not tile_manager.is_collision(new_x, new_y):
                self._set_target(new_x, new_y)
                self.facing = direction
    
    def _move_patrol(self):
        """Bewegung entlang eines Patrol-Pfads"""
        if not self.patrol_path:
            return
        
        # Hole nächstes Ziel
        target = self.patrol_path[self.patrol_index]
        
        # Wenn am Ziel, wechsle zum nächsten
        if self.tile_x == target[0] and self.tile_y == target[1]:
            if self.patrol_forward:
                self.patrol_index += 1
                if self.patrol_index >= len(self.patrol_path):
                    self.patrol_index = len(self.patrol_path) - 2
                    self.patrol_forward = False
            else:
                self.patrol_index -= 1
                if self.patrol_index < 0:
                    self.patrol_index = 1
                    self.patrol_forward = True
            
            target = self.patrol_path[self.patrol_index]
        
        # Finde Pfad zum nächsten Patrol-Punkt
        tile_manager = TileManager.get_instance()
        if not tile_manager.find_path((self.tile_x, self.tile_y), target):
            return # Kein Pfad gefunden
        
        self.current_path = tile_manager.find_path((self.tile_x, self.tile_y), target)
        self.path_index = 0
        self._move_along_path()
    
    def _move_follow(self, player_pos: Tuple[int, int]):
        """Folgt dem Spieler"""
        dist = abs(player_pos[0] - self.tile_x) + abs(player_pos[1] - self.tile_y)
        
        # Nur folgen wenn Spieler in Reichweite
        if dist <= self.sight_range and dist > 1:
            tile_manager = TileManager.get_instance()
            if not tile_manager.find_path((self.tile_x, self.tile_y), player_pos):
                return # Kein Pfad gefunden
            
            path = tile_manager.find_path((self.tile_x, self.tile_y), player_pos)
            if path and len(path) > 1:  # Nicht direkt auf Spieler-Position
                self.current_path = path[:-1]  # Letzten Schritt weglassen
                self.path_index = 0
                self._move_along_path()
    
    def _move_flee(self, player_pos: Tuple[int, int]):
        """Flieht vor dem Spieler"""
        dist = abs(player_pos[0] - self.tile_x) + abs(player_pos[1] - self.tile_y)
        
        # Nur fliehen wenn Spieler zu nah
        if dist <= self.sight_range:
            # Finde entgegengesetzte Richtung
            dx = self.tile_x - player_pos[0]
            dy = self.tile_y - player_pos[1]
            
            # Normalisiere
            if abs(dx) > abs(dy):
                dx = 1 if dx > 0 else -1
                dy = 0
            else:
                dx = 0
                dy = 1 if dy > 0 else -1
            
            new_x = self.tile_x + dx
            new_y = self.tile_y + dy
            
            tile_manager = TileManager.get_instance()
            if not tile_manager.is_collision(new_x, new_y):
                self._set_target(new_x, new_y)
                self.facing = Direction.from_delta(dx, dy)
    
    def _move_wander(self):
        """Erkundet die Umgebung"""
        # Wenn kein Ziel, wähle eines
        if not self.wander_target:
            # Finde unbesuchte Tiles in Reichweite
            unvisited = []
            for dx in range(-self.movement_radius, self.movement_radius + 1):
                for dy in range(-self.movement_radius, self.movement_radius + 1):
                    x = self.home_position[0] + dx
                    y = self.home_position[1] + dy
                    
                    if (x, y) not in self.visited_tiles:
                        tile_manager = TileManager.get_instance()
                        if not tile_manager.is_collision(x, y):
                            unvisited.append((x, y))
            
            if unvisited:
                self.wander_target = random.choice(unvisited)
            else:
                # Alle besucht, zurücksetzen
                self.visited_tiles.clear()
                self.wander_target = self.home_position
        
        # Bewege zum Ziel
        if self.wander_target:
            if self.tile_x == self.wander_target[0] and self.tile_y == self.wander_target[1]:
                # Ziel erreicht
                self.visited_tiles.add(self.wander_target)
                self.wander_target = None
            else:
                # Finde Pfad
                tile_manager = TileManager.get_instance()
                if not tile_manager.find_path((self.tile_x, self.tile_y), self.wander_target):
                    return # Kein Pfad gefunden
                
                path = tile_manager.find_path((self.tile_x, self.tile_y), self.wander_target)
                if path:
                    self.current_path = path
                    self.path_index = 0
                    self._move_along_path()
                else:
                    # Kein Pfad, neues Ziel
                    self.wander_target = None
    
    def _move_along_path(self):
        """Bewegt sich entlang des aktuellen Pfads"""
        if self.path_index < len(self.current_path):
            next_pos = self.current_path[self.path_index]
            
            # Berechne Richtung
            dx = next_pos[0] - self.tile_x
            dy = next_pos[1] - self.tile_y
            
            # Setze Ziel
            self._set_target(next_pos[0], next_pos[1])
            self.facing = Direction.from_delta(dx, dy)
            
            # Nächster Pfad-Schritt
            self.path_index += 1
        else:
            # Pfad abgeschlossen
            self.current_path = []
            self.path_index = 0
    
    def _set_target(self, tile_x: int, tile_y: int):
        """Setzt eine neue Zielposition"""
        self.target_tile_x = tile_x
        self.target_tile_y = tile_y
        self.target_x = tile_x * TILE_SIZE
        self.target_y = tile_y * TILE_SIZE
        self.is_moving = True
    
    def check_trainer_sight(self, player_pos: Tuple[int, int]) -> bool:
        """
        Prüft ob ein Trainer den Spieler sieht.
        
        Args:
            player_pos: Position des Spielers in Tiles
            
        Returns:
            True wenn Spieler gesichtet wurde
        """
        if not self.is_trainer or self.has_spotted_player:
            return False
        
        # Prüfe Distanz
        dx = player_pos[0] - self.tile_x
        dy = player_pos[1] - self.tile_y
        
        # Prüfe ob in Sichtlinie basierend auf Richtung
        in_sight = False
        
        if self.facing == Direction.UP and dx == 0 and dy < 0 and abs(dy) <= self.sight_range:
            in_sight = True
        elif self.facing == Direction.DOWN and dx == 0 and dy > 0 and abs(dy) <= self.sight_range:
            in_sight = True
        elif self.facing == Direction.LEFT and dy == 0 and dx < 0 and abs(dx) <= self.sight_range:
            in_sight = True
        elif self.facing == Direction.RIGHT and dy == 0 and dx > 0 and abs(dx) <= self.sight_range:
            in_sight = True
        
        if in_sight:
            # Prüfe ob Sichtlinie frei ist (keine Hindernisse)
            tile_manager = TileManager.get_instance()
            if not tile_manager.find_path((self.tile_x, self.tile_y), player_pos):
                self.has_spotted_player = True
                return True
        
        return False
    
    def interact(self) -> Optional[Dict]:
        """
        Interagiert mit dem NPC.
        
        Returns:
            Dialog-Daten oder None
        """
        self.is_interacting = True
        
        # Spieler anschauen
        # TODO: Richtung zum Spieler berechnen
        
        # Dialog holen
        from engine.world.tile_manager import TileManager
        tile_manager = TileManager.get_instance()
        dialogue = tile_manager.get_dialogue(self.dialogue_id)
        return dialogue
    
    def end_interaction(self):
        """Beendet die Interaktion"""
        self.is_interacting = False
    
    def draw(self, screen: pygame.Surface, camera_x: int = 0, camera_y: int = 0):
        """
        Zeichnet den NPC.
        
        Args:
            screen: Ziel-Surface
            camera_x: Kamera X-Offset
            camera_y: Kamera Y-Offset
        """
        screen.blit(self.sprite, (self.x - camera_x, self.y - camera_y))
        
        # Debug: Zeichne Pfad
        if self.current_path and __debug__:
            for i, pos in enumerate(self.current_path[self.path_index:]):
                color = (255, 255, 0) if i == 0 else (255, 200, 0)
                pygame.draw.circle(screen, color,
                                 (pos[0] * TILE_SIZE + TILE_SIZE // 2 - camera_x,
                                  pos[1] * TILE_SIZE + TILE_SIZE // 2 - camera_y), 3)
        
        # Debug: Zeichne Sichtlinie für Trainer
        if self.is_trainer and __debug__:
            sight_color = (255, 0, 0, 50) if self.has_spotted_player else (255, 255, 0, 50)
            
            if self.facing == Direction.UP:
                for i in range(1, self.sight_range + 1):
                    rect = pygame.Rect(self.tile_x * TILE_SIZE - camera_x,
                                     (self.tile_y - i) * TILE_SIZE - camera_y,
                                     TILE_SIZE, TILE_SIZE)
                    pygame.draw.rect(screen, sight_color, rect, 1)
            elif self.facing == Direction.DOWN:
                for i in range(1, self.sight_range + 1):
                    rect = pygame.Rect(self.tile_x * TILE_SIZE - camera_x,
                                     (self.tile_y + i) * TILE_SIZE - camera_y,
                                     TILE_SIZE, TILE_SIZE)
                    pygame.draw.rect(screen, sight_color, rect, 1)
            elif self.facing == Direction.LEFT:
                for i in range(1, self.sight_range + 1):
                    rect = pygame.Rect((self.tile_x - i) * TILE_SIZE - camera_x,
                                     self.tile_y * TILE_SIZE - camera_y,
                                     TILE_SIZE, TILE_SIZE)
                    pygame.draw.rect(screen, sight_color, rect, 1)
            elif self.facing == Direction.RIGHT:
                for i in range(1, self.sight_range + 1):
                    rect = pygame.Rect((self.tile_x + i) * TILE_SIZE - camera_x,
                                     self.tile_y * TILE_SIZE - camera_y,
                                     TILE_SIZE, TILE_SIZE)
                    pygame.draw.rect(screen, sight_color, rect, 1)
    
    def get_save_data(self) -> Dict:
        """
        Holt Speicherdaten für den NPC.
        
        Returns:
            Dictionary mit Speicherdaten
        """
        return {
            'npc_id': self.npc_id,
            'tile_x': self.tile_x,
            'tile_y': self.tile_y,
            'facing': self.facing.name,
            'has_spotted_player': self.has_spotted_player,
            'visited_tiles': list(self.visited_tiles)
        }
    
    def load_save_data(self, data: Dict):
        """
        Lädt Speicherdaten für den NPC.
        
        Args:
            data: Dictionary mit Speicherdaten
        """
        self.tile_x = data.get('tile_x', self.tile_x)
        self.tile_y = data.get('tile_y', self.tile_y)
        self.x = self.tile_x * TILE_SIZE
        self.y = self.tile_y * TILE_SIZE
        self.facing = Direction[data.get('facing', 'DOWN')]
        self.has_spotted_player = data.get('has_spotted_player', False)
        self.visited_tiles = set(data.get('visited_tiles', []))

# RivalKlaus Klasse für die FieldScene
class RivalKlaus(ImprovedNPC):
    """Klaus - der Rivale des Spielers"""
    
    def __init__(self, x: float, y: float):
        # Konvertiere Pixel zu Tiles
        tile_x = int(x // TILE_SIZE)
        tile_y = int(y // TILE_SIZE)
        
        # Erstelle NPC-Konfiguration
        config = NPCConfig(
            npc_id="rival_klaus",
            sprite_name="rival.png",
            dialogue_id="rival_first_meeting",
            movement_pattern=MovementPattern.STATIC,
            is_trainer=True,
            sight_range=3
        )
        
        super().__init__(tile_x, tile_y, config)
        
        self.name = "Klaus"
        self.interactable = True
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