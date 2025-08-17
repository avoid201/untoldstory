"""
Grid-based A* pathfinding for 16x16 tile maps.

- Four-directional movement (no diagonals)
- Uses `Area.is_tile_solid(x, y)` to determine walkability
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple
import heapq


GridPos = Tuple[int, int]


@dataclass(order=False)
class Node:
    position: GridPos
    g_cost: int  # Cost from start
    h_cost: int  # Heuristic to goal
    parent: Optional[GridPos]

    @property
    def f_cost(self) -> int:
        return self.g_cost + self.h_cost


def manhattan(a: GridPos, b: GridPos) -> int:
    ax, ay = a
    bx, by = b
    return abs(ax - bx) + abs(ay - by)


def reconstruct_path(came_from: Dict[GridPos, GridPos], current: GridPos) -> List[GridPos]:
    path: List[GridPos] = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    path.reverse()
    return path


def in_bounds(area, x: int, y: int) -> bool:
    return 0 <= x < int(area.width) and 0 <= y < int(area.height)


def get_neighbors(area, pos: GridPos) -> List[GridPos]:
    x, y = pos
    neighbors: List[GridPos] = []
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nx, ny = x + dx, y + dy
        if not in_bounds(area, nx, ny):
            continue
        # Solid tiles are not walkable
        if area.is_tile_solid(nx, ny):
            continue
        neighbors.append((nx, ny))
    return neighbors


def find_path(area, start: GridPos, goal: GridPos, *, max_expansions: int = 8192) -> List[GridPos]:
    """
    Compute a path on the area grid using A*.

    Args:
        area: Area providing `width`, `height`, and `is_tile_solid(x, y)`
        start: Start tile (x, y)
        goal: Goal tile (x, y)
        max_expansions: Safety limit to avoid infinite loops on malformed maps

    Returns:
        List of tiles from start to goal (inclusive). Empty if no path.
    """
    sx, sy = start
    gx, gy = goal

    # Early validations
    if not in_bounds(area, sx, sy) or not in_bounds(area, gx, gy):
        return []

    if area.is_tile_solid(sx, sy):
        # Start position blocked
        return []

    if start == goal:
        return [start]

    # If the goal is blocked, try to route to the closest walkable neighbor of goal
    effective_goals: Set[GridPos] = set()
    if not area.is_tile_solid(gx, gy):
        effective_goals.add(goal)
    else:
        for n in get_neighbors(area, goal):
            effective_goals.add(n)
        if not effective_goals:
            return []

    # Open set priority queue: (f_cost, h_cost, tie_breaker, position)
    open_heap: List[Tuple[int, int, int, GridPos]] = []
    tie: int = 0

    g_score: Dict[GridPos, int] = {start: 0}
    h0 = min(manhattan(start, g) for g in effective_goals)
    heapq.heappush(open_heap, (h0, h0, tie, start))
    tie += 1

    came_from: Dict[GridPos, GridPos] = {}
    closed: Set[GridPos] = set()

    expansions = 0
    while open_heap and expansions < max_expansions:
        _, _, _, current = heapq.heappop(open_heap)
        if current in closed:
            continue
        closed.add(current)
        expansions += 1

        if current in effective_goals:
            return reconstruct_path(came_from, current)

        for neighbor in get_neighbors(area, current):
            tentative_g = g_score[current] + 1
            if neighbor in g_score and tentative_g >= g_score[neighbor]:
                continue

            came_from[neighbor] = current
            g_score[neighbor] = tentative_g
            # Use the best (minimum) heuristic among multiple effective goals
            h = min(manhattan(neighbor, g) for g in effective_goals)
            f = tentative_g + h
            heapq.heappush(open_heap, (f, h, tie, neighbor))
            tie += 1

    # No path found within expansion budget
    return []


