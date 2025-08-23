"""
Party management system for monster teams.
Handles active party of 6 and storage boxes.
"""

from typing import TYPE_CHECKING, List, Optional, Dict, Tuple
from dataclasses import dataclass, field
import json

if TYPE_CHECKING:
    from engine.systems.monster_instance import MonsterInstance
    from engine.systems.monsters import MonsterSpecies


@dataclass
class Party:
    """Active party of up to 6 monsters."""
    
    MAX_SIZE = 6
    
    def __init__(self):
        """Initialize empty party."""
        self.members: List[Optional['MonsterInstance']] = [None] * self.MAX_SIZE
        self.active_index = 0  # Currently active monster in battle
    
    def add_monster(self, monster: 'MonsterInstance', 
                   position: Optional[int] = None) -> bool:
        """
        Add a monster to the party.
        
        Args:
            monster: Monster to add
            position: Specific position (0-5), or None for first available
            
        Returns:
            True if added successfully
        """
        if position is not None:
            # Add to specific position
            if 0 <= position < self.MAX_SIZE:
                if self.members[position] is None:
                    self.members[position] = monster
                    return True
                else:
                    # Position occupied
                    return False
            return False
        
        # Add to first available slot
        for i in range(self.MAX_SIZE):
            if self.members[i] is None:
                self.members[i] = monster
                return True
        
        # Party full
        return False
    
    def remove_monster(self, position: int) -> Optional['MonsterInstance']:
        """
        Remove a monster from the party.
        
        Args:
            position: Position to remove from (0-5)
            
        Returns:
            Removed monster or None
        """
        if 0 <= position < self.MAX_SIZE:
            monster = self.members[position]
            self.members[position] = None
            
            # Adjust active index if needed
            if self.active_index == position:
                self.active_index = self._find_next_valid()
            
            return monster
        return None
    
    def swap_positions(self, pos1: int, pos2: int) -> bool:
        """
        Swap two monsters' positions.
        
        Args:
            pos1: First position
            pos2: Second position
            
        Returns:
            True if swapped successfully
        """
        if 0 <= pos1 < self.MAX_SIZE and 0 <= pos2 < self.MAX_SIZE:
            self.members[pos1], self.members[pos2] = self.members[pos2], self.members[pos1]
            
            # Update active index if needed
            if self.active_index == pos1:
                self.active_index = pos2
            elif self.active_index == pos2:
                self.active_index = pos1
            
            return True
        return False
    
    def get_active(self) -> Optional['MonsterInstance']:
        """Get the currently active monster."""
        if 0 <= self.active_index < self.MAX_SIZE:
            return self.members[self.active_index]
        return None
    
    def set_active(self, position: int) -> bool:
        """
        Set the active monster.
        
        Args:
            position: Position to make active
            
        Returns:
            True if set successfully
        """
        if 0 <= position < self.MAX_SIZE and self.members[position] is not None:
            # Check if monster is conscious
            if self.members[position].current_hp > 0:
                self.active_index = position
                return True
        return False
    
    def switch_active(self, new_active: 'MonsterInstance') -> bool:
        """
        Switch to a specific monster.
        
        Args:
            new_active: Monster to switch to
            
        Returns:
            True if switched successfully
        """
        for i, member in enumerate(self.members):
            if member == new_active and member.current_hp > 0:
                self.active_index = i
                return True
        return False
    
    def get_next_valid(self) -> Optional['MonsterInstance']:
        """Get the next conscious monster."""
        start = (self.active_index + 1) % self.MAX_SIZE
        
        for i in range(self.MAX_SIZE):
            idx = (start + i) % self.MAX_SIZE
            if self.members[idx] and self.members[idx].current_hp > 0:
                return self.members[idx]
        
        return None
    
    def _find_next_valid(self) -> int:
        """Find index of next valid monster."""
        for i in range(self.MAX_SIZE):
            if self.members[i] and self.members[i].current_hp > 0:
                return i
        return -1
    
    def get_all_members(self) -> List['MonsterInstance']:
        """Get all non-None party members."""
        return [m for m in self.members if m is not None]
    
    def get_conscious_members(self) -> List['MonsterInstance']:
        """Get all conscious (HP > 0) party members."""
        return [m for m in self.members if m is not None and m.current_hp > 0]
    
    def is_full(self) -> bool:
        """Check if party is full."""
        return all(m is not None for m in self.members)
    
    def is_empty(self) -> bool:
        """Check if party is empty."""
        return all(m is None for m in self.members)
    
    def is_wiped(self) -> bool:
        """Check if all party members are fainted."""
        conscious = self.get_conscious_members()
        return len(conscious) == 0 and not self.is_empty()
    
    def heal_all(self) -> None:
        """Fully heal all party members."""
        for member in self.members:
            if member:
                member.full_heal()
    
    def get_average_level(self) -> float:
        """Get average level of party members."""
        members = self.get_all_members()
        if not members:
            return 0
        return sum(m.level for m in members) / len(members)
    
    def get_type_coverage(self) -> Dict[str, int]:
        """Get type coverage analysis of party."""
        coverage = {}
        for member in self.get_all_members():
            for monster_type in member.types:
                coverage[monster_type] = coverage.get(monster_type, 0) + 1
        return coverage
    
    def to_dict(self) -> Dict:
        """Convert party to dictionary for saving."""
        return {
            'members': [m.to_dict() if m else None for m in self.members],
            'active_index': self.active_index
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Party':
        """Create party from dictionary."""
        from engine.systems.monster_instance import MonsterInstance
        
        party = cls()
        party.active_index = data.get('active_index', 0)
        
        members_data = data.get('members', [])
        for i, member_data in enumerate(members_data):
            if member_data and i < cls.MAX_SIZE:
                party.members[i] = MonsterInstance.from_dict(member_data)
        
        return party


@dataclass
class StorageBox:
    """Storage box for extra monsters."""
    
    DEFAULT_CAPACITY = 30
    
    def __init__(self, box_id: int, name: str, capacity: int = DEFAULT_CAPACITY):
        """
        Initialize storage box.
        
        Args:
            box_id: Unique box identifier
            name: Box name
            capacity: Maximum capacity
        """
        self.id = box_id
        self.name = name
        self.capacity = capacity
        self.monsters: List[Optional['MonsterInstance']] = [None] * capacity
    
    def add_monster(self, monster: 'MonsterInstance', 
                   position: Optional[int] = None) -> bool:
        """
        Add a monster to the box.
        
        Args:
            monster: Monster to add
            position: Specific position, or None for first available
            
        Returns:
            True if added successfully
        """
        if position is not None:
            if 0 <= position < self.capacity and self.monsters[position] is None:
                self.monsters[position] = monster
                return True
            return False
        
        # Find first empty slot
        for i in range(self.capacity):
            if self.monsters[i] is None:
                self.monsters[i] = monster
                return True
        
        return False  # Box full
    
    def remove_monster(self, position: int) -> Optional['MonsterInstance']:
        """Remove a monster from the box."""
        if 0 <= position < self.capacity:
            monster = self.monsters[position]
            self.monsters[position] = None
            return monster
        return None
    
    def get_monster(self, position: int) -> Optional['MonsterInstance']:
        """Get a monster at specific position without removing."""
        if 0 <= position < self.capacity:
            return self.monsters[position]
        return None
    
    def get_all_monsters(self) -> List['MonsterInstance']:
        """Get all non-None monsters in box."""
        return [m for m in self.monsters if m is not None]
    
    def count(self) -> int:
        """Count monsters in box."""
        return sum(1 for m in self.monsters if m is not None)
    
    def is_full(self) -> bool:
        """Check if box is full."""
        return self.count() >= self.capacity
    
    def is_empty(self) -> bool:
        """Check if box is empty."""
        return self.count() == 0
    
    def organize(self) -> None:
        """Organize box by moving all monsters to front."""
        monsters = self.get_all_monsters()
        self.monsters = monsters + [None] * (self.capacity - len(monsters))
    
    def sort_by_level(self, reverse: bool = True) -> None:
        """Sort monsters by level."""
        monsters = self.get_all_monsters()
        monsters.sort(key=lambda m: m.level, reverse=reverse)
        self.monsters = monsters + [None] * (self.capacity - len(monsters))
    
    def sort_by_species(self) -> None:
        """Sort monsters by species ID."""
        monsters = self.get_all_monsters()
        monsters.sort(key=lambda m: m.species.id)
        self.monsters = monsters + [None] * (self.capacity - len(monsters))
    
    def sort_by_rank(self) -> None:
        """Sort monsters by rank (X > SS > S > A > B > C > D > E > F)."""
        rank_order = {'X': 9, 'SS': 8, 'S': 7, 'A': 6, 'B': 5, 
                     'C': 4, 'D': 3, 'E': 2, 'F': 1}
        monsters = self.get_all_monsters()
        monsters.sort(key=lambda m: rank_order.get(m.rank, 0), reverse=True)
        self.monsters = monsters + [None] * (self.capacity - len(monsters))
    
    def to_dict(self) -> Dict:
        """Convert box to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'capacity': self.capacity,
            'monsters': [m.to_dict() if m else None for m in self.monsters]
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'StorageBox':
        """Create box from dictionary."""
        from engine.systems.monster_instance import MonsterInstance
        
        box = cls(
            box_id=data['id'],
            name=data['name'],
            capacity=data.get('capacity', cls.DEFAULT_CAPACITY)
        )
        
        monsters_data = data.get('monsters', [])
        for i, monster_data in enumerate(monsters_data):
            if monster_data and i < box.capacity:
                box.monsters[i] = MonsterInstance.from_dict(monster_data)
        
        return box


class StorageSystem:
    """Manages all storage boxes."""
    
    MAX_BOXES = 16
    
    def __init__(self):
        """Initialize storage system."""
        self.boxes: List[StorageBox] = []
        self.current_box = 0
        
        # Create initial boxes with Ruhrpott names
        box_names = [
            "Bunker 1",      # Box 1
            "Zeche 2",       # Box 2  
            "Schacht 3",     # Box 3
            "Stollen 4"      # Box 4
        ]
        
        for i, name in enumerate(box_names):
            self.add_box(name)
    
    def add_box(self, name: str, capacity: int = StorageBox.DEFAULT_CAPACITY) -> bool:
        """
        Add a new storage box.
        
        Args:
            name: Box name
            capacity: Box capacity
            
        Returns:
            True if added successfully
        """
        if len(self.boxes) >= self.MAX_BOXES:
            return False
        
        box_id = len(self.boxes)
        new_box = StorageBox(box_id, name, capacity)
        self.boxes.append(new_box)
        return True
    
    def get_box(self, box_id: int) -> Optional[StorageBox]:
        """Get a specific box."""
        if 0 <= box_id < len(self.boxes):
            return self.boxes[box_id]
        return None
    
    def get_current_box(self) -> Optional[StorageBox]:
        """Get the currently selected box."""
        return self.get_box(self.current_box)
    
    def set_current_box(self, box_id: int) -> bool:
        """Set the current box."""
        if 0 <= box_id < len(self.boxes):
            self.current_box = box_id
            return True
        return False
    
    def deposit_monster(self, monster: 'MonsterInstance',
                       box_id: Optional[int] = None) -> Tuple[bool, str]:
        """
        Deposit a monster into storage.
        
        Args:
            monster: Monster to deposit
            box_id: Specific box, or None for current
            
        Returns:
            Tuple of (success, message)
        """
        if box_id is None:
            box_id = self.current_box
        
        box = self.get_box(box_id)
        if box:
            if box.add_monster(monster):
                return True, f"{monster.nickname or monster.species_name} wurde in {box.name} gepackt!"
        
        # Try other boxes if current is full
        for box in self.boxes:
            if box.add_monster(monster):
                return True, f"{monster.nickname or monster.species_name} wurde in {box.name} gepackt!"
        
        return False, "Alle Boxen sind voll, Kollege! Mach mal Platz!"
    
    def withdraw_monster(self, box_id: int, position: int) -> Optional['MonsterInstance']:
        """
        Withdraw a monster from storage.
        
        Args:
            box_id: Box ID
            position: Position in box
            
        Returns:
            Withdrawn monster or None
        """
        box = self.get_box(box_id)
        if box:
            return box.remove_monster(position)
        return None
    
    def transfer_monster(self, from_box: int, from_pos: int,
                        to_box: int, to_pos: Optional[int] = None) -> bool:
        """
        Transfer a monster between boxes.
        
        Args:
            from_box: Source box ID
            from_pos: Source position
            to_box: Destination box ID
            to_pos: Destination position (None for first available)
            
        Returns:
            True if transferred successfully
        """
        source = self.get_box(from_box)
        dest = self.get_box(to_box)
        
        if not source or not dest:
            return False
        
        monster = source.get_monster(from_pos)
        if not monster:
            return False
        
        # Check if destination is available
        if to_pos is not None:
            if dest.get_monster(to_pos) is not None:
                return False  # Position occupied
        
        # Perform transfer
        source.remove_monster(from_pos)
        return dest.add_monster(monster, to_pos)
    
    def find_monster(self, monster_id: str) -> Optional[Tuple[int, int]]:
        """
        Find a monster by its ID.
        
        Args:
            monster_id: Monster's unique ID
            
        Returns:
            Tuple of (box_id, position) or None
        """
        for box_id, box in enumerate(self.boxes):
            for pos, monster in enumerate(box.monsters):
                if monster and monster.id == monster_id:
                    return (box_id, pos)
        return None
    
    def count_total_monsters(self) -> int:
        """Count total monsters in all boxes."""
        return sum(box.count() for box in self.boxes)
    
    def get_all_monsters(self) -> List['MonsterInstance']:
        """Get all monsters from all boxes."""
        monsters = []
        for box in self.boxes:
            monsters.extend(box.get_all_monsters())
        return monsters
    
    def to_dict(self) -> Dict:
        """Convert storage system to dictionary."""
        return {
            'boxes': [box.to_dict() for box in self.boxes],
            'current_box': self.current_box
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'StorageSystem':
        """Create storage system from dictionary."""
        system = cls()
        system.boxes = []
        system.current_box = data.get('current_box', 0)
        
        for box_data in data.get('boxes', []):
            box = StorageBox.from_dict(box_data)
            system.boxes.append(box)
        
        # Ensure at least one box exists
        if not system.boxes:
            system.add_box("Bunker 1")
        
        return system


class PartyManager:
    """Manages party and storage together."""
    
    def __init__(self, game=None):
        """Initialize party manager."""
        self.game = game
        self.party = Party()
        self.storage = StorageSystem()
    
    def add_to_party(self, monster: 'MonsterInstance') -> Tuple[bool, str]:
        """
        Add a monster to party or storage if full.
        
        Returns:
            Tuple of (success, message)
        """
        if self.party.add_monster(monster):
            return True, f"{monster.nickname or monster.species_name} kommt in dein Team!"
        elif not self.party.is_full():
            return False, "Konnte nicht zum Team hinzufügen!"
        else:
            # Party full, try storage
            success, msg = self.storage.deposit_monster(monster)
            if success:
                return True, f"Team ist voll! {msg}"
            return False, msg
    
    def add_to_box(self, monster: 'MonsterInstance') -> Tuple[bool, str]:
        """Add a monster directly to storage."""
        return self.storage.deposit_monster(monster)
    
    def deposit_from_party(self, party_position: int) -> Tuple[bool, str]:
        """
        Deposit a monster from party to storage.
        
        Args:
            party_position: Position in party
            
        Returns:
            Tuple of (success, message)
        """
        # Can't deposit if it's the only conscious monster
        if len(self.party.get_conscious_members()) <= 1:
            monster = self.party.members[party_position]
            if monster and monster.current_hp > 0:
                return False, "Ey, das is dein letztes fittes Monster! Das bleibt hier!"
        
        monster = self.party.remove_monster(party_position)
        if monster:
            return self.storage.deposit_monster(monster)
        return False, "Da is kein Monster an der Position!"
    
    def withdraw_to_party(self, box_id: int, box_position: int,
                         party_position: Optional[int] = None) -> Tuple[bool, str]:
        """
        Withdraw a monster from storage to party.
        
        Args:
            box_id: Storage box ID
            box_position: Position in box
            party_position: Position in party (None for first available)
            
        Returns:
            Tuple of (success, message)
        """
        if self.party.is_full() and party_position is None:
            return False, "Dein Team is schon voll, Kollege!"
        
        # Get monster from storage
        box = self.storage.get_box(box_id)
        if not box:
            return False, "Die Box gibt's nich!"
        
        monster = box.get_monster(box_position)
        if not monster:
            return False, "Da is kein Monster!"
        
        # Try to add to party
        if party_position is not None:
            # Swap if position occupied
            if self.party.members[party_position]:
                # Deposit current monster first
                current = self.party.remove_monster(party_position)
                success, msg = self.storage.deposit_monster(current)
                if not success:
                    # Revert if deposit fails
                    self.party.add_monster(current, party_position)
                    return False, f"Tausch fehlgeschlagen: {msg}"
        
        # Remove from storage and add to party
        box.remove_monster(box_position)
        success = self.party.add_monster(monster, party_position)
        
        if not success:
            # Revert if add fails
            box.add_monster(monster, box_position)
            return False, "Konnte Monster nicht zum Team hinzufügen!"
        
        return True, f"{monster.nickname or monster.species_name} is jetzt im Team!"
    
    def heal_party_at_center(self) -> str:
        """Heal all party members (used at healing centers)."""
        self.party.heal_all()
        return "Deine Monster sind wieder topfit! Läuft bei dir!"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for saving."""
        return {
            'party': self.party.to_dict(),
            'storage': self.storage.to_dict()
        }
    
    @classmethod
    def from_dict(cls, data: Dict, game=None) -> 'PartyManager':
        """Create from dictionary."""
        manager = cls(game)
        manager.party = Party.from_dict(data['party'])
        manager.storage = StorageSystem.from_dict(data['storage'])
        return manager


class PartyManager:
    """Manages both active party and storage system."""
    
    def __init__(self, game=None):
        """Initialize party manager."""
        self.game = game
        self.party = Party()
        self.storage = StorageSystem()
    

