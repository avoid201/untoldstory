"""
PathfindingMixin für NPCs - ENDLICH INTELLIGENTE BEWEGUNG!
Flint Hammerhead macht dat hier ordentlich, wa!
"""

from typing import Optional, List, Tuple
from engine.world.pathfinding import find_path
from engine.world.tiles import world_to_tile, tile_to_world
import random
import time


class PathfindingMixin:
    """
    Mixin für NPCs mit intelligenter Wegfindung.
    Erweitert die normale NPC-Klasse um A* Pathfinding.
    """
    
    def __init__(self):
        """Initialize pathfinding-specific attributes."""
        self.current_path: Optional[List[Tuple[int, int]]] = None
        self.path_index: int = 0
        self.path_target: Optional[Tuple[int, int]] = None
        self.path_stuck_counter: int = 0
        self.last_pathfind_time: float = 0
        self.pathfind_cooldown: float = 0.5  # Halbe Sekunde zwischen Pathfinding-Versuchen
        
    def find_path_to(self, target_x: int, target_y: int, area=None) -> bool:
        """
        Findet einen Pfad zum Ziel mit A* Algorithmus.
        
        Args:
            target_x: Ziel-Tile X
            target_y: Ziel-Tile Y
            area: Area-Objekt mit is_tile_solid() Methode
            
        Returns:
            True wenn Pfad gefunden, sonst False
        """
        # Cooldown checken - nich zu oft pathfinden, sonst raucht die CPU ab!
        current_time = time.time()
        if current_time - self.last_pathfind_time < self.pathfind_cooldown:
            return False
        self.last_pathfind_time = current_time
        
        # Aktuelle Position in Tiles
        current_x, current_y = world_to_tile(self.x, self.y)
        
        # Check ob wir schon da sind
        if (current_x, current_y) == (target_x, target_y):
            self.current_path = None
            return True
        
        # Area brauchen wir für Kollisionschecks
        if not area:
            if hasattr(self, 'current_area'):
                area = self.current_area
            else:
                print(f"[PathfindingMixin] Ey, keine Area zum Pathfinden da!")
                return False
        
        # Pfad finden mit A*
        try:
            path = find_path(
                area=area,
                start=(current_x, current_y),
                goal=(target_x, target_y),
                max_expansions=256  # Nich zu viele Nodes checken, sonst dauert's ewig
            )
            
            if path and len(path) > 1:
                # Ersten Punkt skippen (das is unsere aktuelle Position)
                self.current_path = path[1:]
                self.path_index = 0
                self.path_target = (target_x, target_y)
                self.path_stuck_counter = 0
                print(f"[PathfindingMixin] Pfad gefunden! {len(self.current_path)} Schritte zum Ziel")
                return True
            else:
                print(f"[PathfindingMixin] Kein Pfad gefunden, Mist!")
                self.current_path = None
                return False
                
        except Exception as e:
            print(f"[PathfindingMixin] Fehler beim Pathfinding: {e}")
            self.current_path = None
            return False
    
    def follow_path(self, dt: float) -> bool:
        """
        Folgt dem aktuellen Pfad Schritt für Schritt.
        
        Args:
            dt: Delta time
            
        Returns:
            True wenn noch auf'm Weg, False wenn angekommen oder kein Pfad
        """
        if not self.current_path or self.path_index >= len(self.current_path):
            self.current_path = None
            return False
        
        # Nächsten Wegpunkt holen
        next_tile = self.current_path[self.path_index]
        next_x, next_y = tile_to_world(next_tile[0], next_tile[1])
        
        # Check ob wir schon am nächsten Wegpunkt sind
        current_tile = world_to_tile(self.x, self.y)
        if current_tile == next_tile:
            # Wegpunkt erreicht, nächster!
            self.path_index += 1
            self.path_stuck_counter = 0
            
            # Check ob wir am Ziel sind
            if self.path_index >= len(self.current_path):
                print(f"[PathfindingMixin] Ziel erreicht, Alter!")
                self.current_path = None
                return False
            return True
        
        # Bewegung zum nächsten Wegpunkt starten (wenn nich schon am bewegen)
        if not self.is_moving:
            # Check ob der Weg noch frei is
            if self._can_move_to(next_tile[0], next_tile[1]):
                self._start_movement(next_tile[0], next_tile[1])
            else:
                # Weg blockiert! Neuen Pfad suchen
                self.path_stuck_counter += 1
                if self.path_stuck_counter > 3:
                    print(f"[PathfindingMixin] Stecke fest! Suche neuen Weg...")
                    if self.path_target:
                        self.find_path_to(self.path_target[0], self.path_target[1])
                    else:
                        self.current_path = None
                return False
        
        return True
    
    def wander_with_pathfinding(self, area, home_radius: int = 3) -> None:
        """
        Intelligentes Wandern mit Pathfinding statt random Movement.
        
        Args:
            area: Area-Objekt
            home_radius: Maximaler Radius um Home-Position
        """
        if self.current_path:
            # Schon auf'm Weg irgendwohin
            return
        
        # Zufälliges Ziel in der Nähe suchen
        home_x, home_y = self.home_position
        
        # 10 Versuche ein gutes Ziel zu finden
        for _ in range(10):
            # Zufällige Position im Radius
            offset_x = random.randint(-home_radius, home_radius)
            offset_y = random.randint(-home_radius, home_radius)
            
            target_x = home_x + offset_x
            target_y = home_y + offset_y
            
            # Check ob das Ziel begehbar is
            if area and not area.is_tile_solid(target_x, target_y):
                # Pfad dahin suchen
                if self.find_path_to(target_x, target_y, area):
                    print(f"[PathfindingMixin] Wandere zu ({target_x}, {target_y})")
                    break
    
    def follow_player(self, player, area, min_distance: int = 2, max_distance: int = 5) -> None:
        """
        Folgt dem Spieler mit Pathfinding.
        
        Args:
            player: Player-Objekt
            area: Area-Objekt
            min_distance: Minimaler Abstand zum Spieler
            max_distance: Maximaler Abstand bevor NPC losläuft
        """
        if not player:
            return
        
        # Spieler- und NPC-Position in Tiles
        player_tile = world_to_tile(player.x, player.y)
        npc_tile = world_to_tile(self.x, self.y)
        
        # Distanz berechnen (Manhattan-Distanz)
        distance = abs(player_tile[0] - npc_tile[0]) + abs(player_tile[1] - npc_tile[1])
        
        # Zu weit weg? Dann hinterher!
        if distance > max_distance:
            # Ziel-Position in der Nähe vom Spieler suchen (nich direkt drauf!)
            possible_targets = []
            
            for dx in range(-min_distance, min_distance + 1):
                for dy in range(-min_distance, min_distance + 1):
                    if abs(dx) + abs(dy) >= min_distance:  # Mindestabstand einhalten
                        target_x = player_tile[0] + dx
                        target_y = player_tile[1] + dy
                        
                        # Check ob begehbar
                        if area and not area.is_tile_solid(target_x, target_y):
                            possible_targets.append((target_x, target_y))
            
            # Zufälliges Ziel aus den möglichen wählen
            if possible_targets:
                target = random.choice(possible_targets)
                self.find_path_to(target[0], target[1], area)
        
        # Zu nah? Dann weg!
        elif distance < min_distance and distance > 0:
            # In die entgegengesetzte Richtung bewegen
            dx = npc_tile[0] - player_tile[0]
            dy = npc_tile[1] - player_tile[1]
            
            # Normalisieren und Schrittweite anwenden
            if dx != 0:
                dx = 1 if dx > 0 else -1
            if dy != 0:
                dy = 1 if dy > 0 else -1
            
            escape_x = npc_tile[0] + dx * 2
            escape_y = npc_tile[1] + dy * 2
            
            # Check ob begehbar
            if area and not area.is_tile_solid(escape_x, escape_y):
                self.find_path_to(escape_x, escape_y, area)
    
    def patrol_with_pathfinding(self, patrol_points: List[Tuple[int, int]], area) -> None:
        """
        Patrouilliert zwischen Punkten mit intelligentem Pathfinding.
        
        Args:
            patrol_points: Liste von Patrol-Punkten (Tile-Koordinaten)
            area: Area-Objekt
        """
        if not patrol_points or len(patrol_points) < 2:
            return
        
        # Check ob wir schon ein Ziel haben
        if not self.current_path:
            # Nächsten Patrol-Punkt ansteuern
            if not hasattr(self, 'patrol_index'):
                self.patrol_index = 0
                self.patrol_forward = True
            
            target_point = patrol_points[self.patrol_index]
            
            # Pfad zum nächsten Punkt suchen
            if self.find_path_to(target_point[0], target_point[1], area):
                # Nächsten Index vorbereiten für nächstes Mal
                if self.patrol_forward:
                    self.patrol_index += 1
                    if self.patrol_index >= len(patrol_points):
                        self.patrol_index = len(patrol_points) - 2
                        self.patrol_forward = False
                else:
                    self.patrol_index -= 1
                    if self.patrol_index < 0:
                        self.patrol_index = 1
                        self.patrol_forward = True
