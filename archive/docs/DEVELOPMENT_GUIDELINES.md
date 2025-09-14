# 🛠️ Entwicklungsrichtlinien - Untold Story

> **Offizielle Entwicklungsstandards und Best Practices für das Projekt**

[![Zurück zur Hauptdokumentation](README.md)](README.md) | [📚 Dokumentations-Index](README.md#-dokumentations-index)

---

## 📋 Inhaltsverzeichnis

- [🎯 Überblick](#-überblick)
- [🐍 Python-Standards](#-python-standards)
- [🏗️ Architektur-Prinzipien](#️-architektur-prinzipien)
- [📝 Code-Standards](#-code-standards)
- [🎨 Asset-Standards](#-asset-standards)
- [🧪 Testing-Standards](#-testing-standards)
- [📚 Dokumentations-Standards](#-dokumentations-standards)
- [🔧 Debugging & Entwicklung](#-debugging--entwicklung)
- [🚀 Performance-Optimierung](#-performance-optimierung)
- [🤝 Zusammenarbeit](#-zusammenarbeit)
- [📋 Checklisten](#-checklisten)

---

## 🎯 Überblick

Diese Entwicklungsrichtlinien definieren die **offiziellen Standards** für alle Entwickler, die an **Untold Story** arbeiten. Sie stellen sicher, dass der Code konsistent, wartbar und von hoher Qualität ist.

### 🎯 Ziele

- **Konsistenz**: Einheitliche Code-Struktur und -Stil
- **Wartbarkeit**: Langfristig wartbarer Code
- **Qualität**: Hohe Code-Qualität und Zuverlässigkeit
- **Teamarbeit**: Effiziente Zusammenarbeit im Team
- **Performance**: Optimierte Spielleistung

### 📋 Anwendungsbereich

- **Alle Python-Dateien** im Projekt
- **Alle Assets** (Grafik, Audio, Daten)
- **Alle Dokumentation** und README-Dateien
- **Alle Tests** und Validierungen

---

## 🐍 Python-Standards

### 🐍 Python-Version

**Untold Story** verwendet **Python 3.13.5+** mit modernen Python-Features.

#### ✅ Erlaubte Features
- **Type Hints**: Vollständige Typisierung
- **Dataclasses**: Für Datenstrukturen
- **Pathlib**: Moderne Pfad-Behandlung
- **Async/Await**: Asynchrone Programmierung
- **Pattern Matching**: Strukturierte Datenverarbeitung
- **F-Strings**: Moderne String-Formatierung

#### ❌ Verbotene Features
- **Python 2.x**: Keine Legacy-Unterstützung
- **Deprecated Features**: Keine veralteten Funktionen
- **Global Variables**: Minimale Verwendung
- **Hardcoded Values**: Keine hartcodierten Werte

### 📝 Code-Formatierung

#### 🎨 PEP 8 Compliance
```python
# ✅ Korrekt
def calculate_damage(attacker: Monster, defender: Monster, 
                    attack_type: AttackType) -> int:
    """Berechnet den Schaden eines Angriffs.
    
    Args:
        attacker: Angreifendes Monster
        defender: Verteidigendes Monster
        attack_type: Art des Angriffs
        
    Returns:
        Berechneter Schadenswert
    """
    base_damage = attacker.strength * attack_type.multiplier
    defense_reduction = defender.defense * 0.5
    final_damage = max(1, base_damage - defense_reduction)
    
    return int(final_damage)

# ❌ Falsch
def calcDmg(atk,def,x):
    dmg=atk*x-def*.5
    if dmg<1:dmg=1
    return dmg
```

#### 🔤 Namensgebung
- **Klassen**: PascalCase (`MonsterManager`, `BattleSystem`)
- **Funktionen**: snake_case (`calculate_damage`, `load_monster_data`)
- **Variablen**: snake_case (`monster_level`, `battle_state`)
- **Konstanten**: UPPER_SNAKE_CASE (`MAX_PARTY_SIZE`, `DEFAULT_FPS`)
- **Private Methoden**: Leading underscore (`_internal_calculation`)

### 🏗️ Struktur-Standards

#### 📁 Datei-Organisation
```python
# ✅ Korrekte Datei-Struktur
"""
Standard-Header für alle Python-Dateien
"""

# Imports
import pygame
from typing import List, Optional, Dict
from pathlib import Path

# Lokale Imports
from engine.core.resource_manager import ResourceManager
from engine.systems.monster_system import MonsterSystem

# Konstanten
MAX_MONSTER_LEVEL = 100
DEFAULT_MONSTER_STATS = {
    "health": 100,
    "strength": 50,
    "defense": 30
}

# Typ-Definitionen
class MonsterData:
    """Datenstruktur für Monster-Informationen."""
    
    def __init__(self, name: str, level: int):
        self.name = name
        self.level = level

# Hauptklassen
class MonsterManager:
    """Verwaltet alle Monster im Spiel."""
    
    def __init__(self):
        self.monsters: List[MonsterData] = []
    
    def add_monster(self, monster: MonsterData) -> None:
        """Fügt ein Monster hinzu."""
        self.monsters.append(monster)

# Hauptfunktionen
def main():
    """Hauptfunktion der Datei."""
    manager = MonsterManager()
    return manager

# Ausführung
if __name__ == "__main__":
    main()
```

---

## 🏗️ Architektur-Prinzipien

### 🎯 Design-Prinzipien

#### 🔧 SOLID-Prinzipien
1. **Single Responsibility**: Jede Klasse hat eine Verantwortlichkeit
2. **Open/Closed**: Offen für Erweiterung, geschlossen für Modifikation
3. **Liskov Substitution**: Unterklassen sind austauschbar
4. **Interface Segregation**: Kleine, spezifische Interfaces
5. **Dependency Inversion**: Abhängigkeiten von Abstraktionen

#### 🏗️ Architektur-Patterns
- **Component Pattern**: Wiederverwendbare Komponenten
- **Observer Pattern**: Event-basierte Kommunikation
- **Factory Pattern**: Objekt-Erstellung
- **State Pattern**: Zustandsverwaltung
- **Command Pattern**: Aktionen und Undo/Redo

### 🎮 Engine-Architektur

#### 🔄 Hauptschleife
```python
class GameLoop:
    """Hauptspielschleife mit FPS-Kontrolle."""
    
    def __init__(self, target_fps: int = 60):
        self.target_fps = target_fps
        self.clock = pygame.time.Clock()
        self.running = False
    
    def run(self) -> None:
        """Hauptspielschleife."""
        self.running = True
        
        while self.running:
            # Event-Verarbeitung
            self.handle_events()
            
            # Update-Logik
            self.update()
            
            # Rendering
            self.render()
            
            # FPS-Kontrolle
            self.clock.tick(self.target_fps)
    
    def handle_events(self) -> None:
        """Verarbeitet alle Spiel-Events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
    
    def update(self) -> None:
        """Aktualisiert die Spiel-Logik."""
        pass
    
    def render(self) -> None:
        """Rendert den aktuellen Spielzustand."""
        pass
```

#### 🎭 Szenen-Management
```python
class SceneManager:
    """Verwaltet verschiedene Spielszenen."""
    
    def __init__(self):
        self.scenes: Dict[str, Scene] = {}
        self.current_scene: Optional[Scene] = None
    
    def add_scene(self, name: str, scene: Scene) -> None:
        """Fügt eine neue Szene hinzu."""
        self.scenes[name] = scene
    
    def switch_scene(self, name: str) -> None:
        """Wechselt zu einer anderen Szene."""
        if name in self.scenes:
            if self.current_scene:
                self.current_scene.exit()
            
            self.current_scene = self.scenes[name]
            self.current_scene.enter()
    
    def update(self, dt: float) -> None:
        """Aktualisiert die aktuelle Szene."""
        if self.current_scene:
            self.current_scene.update(dt)
    
    def render(self, screen: pygame.Surface) -> None:
        """Rendert die aktuelle Szene."""
        if self.current_scene:
            self.current_scene.render(screen)
```

---

## 📝 Code-Standards

### 🎯 Funktions-Standards

#### 📝 Funktions-Definition
```python
def calculate_monster_experience(
    base_exp: int,
    level_difference: int,
    monster_rarity: MonsterRarity,
    battle_multiplier: float = 1.0
) -> int:
    """Berechnet die Erfahrungspunkte für ein Monster.
    
    Diese Funktion berücksichtigt den Level-Unterschied, die Seltenheit
    des Monsters und eventuelle Kampf-Multiplikatoren.
    
    Args:
        base_exp: Basis-Erfahrungspunkte
        level_difference: Level-Unterschied zum Gegner
        monster_rarity: Seltenheit des Monsters
        battle_multiplier: Multiplikator für spezielle Kämpfe
        
    Returns:
        Berechnete Erfahrungspunkte
        
    Raises:
        ValueError: Wenn base_exp negativ ist
        TypeError: Wenn monster_rarity ungültig ist
        
    Example:
        >>> exp = calculate_monster_experience(100, 2, MonsterRarity.RARE, 1.5)
        >>> print(exp)
        225
    """
    # Validierung der Eingabeparameter
    if base_exp < 0:
        raise ValueError("Basis-Erfahrung darf nicht negativ sein")
    
    if not isinstance(monster_rarity, MonsterRarity):
        raise TypeError("monster_rarity muss vom Typ MonsterRarity sein")
    
    # Erfahrungsberechnung
    rarity_multiplier = monster_rarity.value
    level_bonus = max(1.0, 1.0 + (level_difference * 0.1))
    
    final_exp = int(base_exp * rarity_multiplier * level_bonus * battle_multiplier)
    
    return max(1, final_exp)  # Mindestens 1 EP
```

#### 🔄 Klassen-Standards
```python
from dataclasses import dataclass
from typing import Optional, List
from enum import Enum

class MonsterType(Enum):
    """Monster-Typen mit Effektivitäts-Multiplikatoren."""
    FIRE = "fire"
    WATER = "water"
    ELECTRIC = "electric"
    EARTH = "earth"
    AIR = "air"
    ICE = "ice"
    PLANT = "plant"
    POISON = "poison"
    FIGHTING = "fighting"
    PSYCHIC = "psychic"
    GHOST = "ghost"
    NORMAL = "normal"

@dataclass
class MonsterStats:
    """Statistiken eines Monsters."""
    health: int
    strength: int
    defense: int
    speed: int
    intelligence: int
    
    def __post_init__(self):
        """Validiert die Statistiken nach der Initialisierung."""
        if any(stat < 0 for stat in [self.health, self.strength, 
                                    self.defense, self.speed, self.intelligence]):
            raise ValueError("Alle Statistiken müssen positiv sein")

class Monster:
    """Repräsentiert ein Monster im Spiel."""
    
    def __init__(self, name: str, monster_type: MonsterType, 
                 stats: MonsterStats, level: int = 1):
        self.name = name
        self.monster_type = monster_type
        self.stats = stats
        self.level = level
        self.experience = 0
        self._validate_inputs()
    
    def _validate_inputs(self) -> None:
        """Validiert die Eingabeparameter."""
        if not name or not name.strip():
            raise ValueError("Monster-Name darf nicht leer sein")
        
        if level < 1:
            raise ValueError("Level muss mindestens 1 sein")
    
    @property
    def max_health(self) -> int:
        """Maximale Gesundheit des Monsters."""
        return self.stats.health + (self.level - 1) * 10
    
    def gain_experience(self, exp: int) -> bool:
        """Gewinnt Erfahrungspunkte und levelt auf wenn möglich.
        
        Args:
            exp: Zu gewinnende Erfahrungspunkte
            
        Returns:
            True wenn das Monster auflevelt, False sonst
        """
        if exp <= 0:
            return False
        
        self.experience += exp
        required_exp = self._calculate_required_exp()
        
        if self.experience >= required_exp:
            self._level_up()
            return True
        
        return False
    
    def _calculate_required_exp(self) -> int:
        """Berechnet die für das nächste Level benötigten EP."""
        return self.level * 100 + (self.level - 1) * 50
    
    def _level_up(self) -> None:
        """Levelt das Monster auf."""
        self.level += 1
        self._increase_stats()
        self.experience = 0
    
    def _increase_stats(self) -> None:
        """Erhöht die Statistiken beim Aufleveln."""
        self.stats.health += 10
        self.stats.strength += 5
        self.stats.defense += 3
        self.stats.speed += 2
        self.stats.intelligence += 2
    
    def __str__(self) -> str:
        """String-Repräsentation des Monsters."""
        return f"{self.name} (Level {self.level}, {self.monster_type.value})"
    
    def __repr__(self) -> str:
        """Detaillierte String-Repräsentation."""
        return (f"Monster(name='{self.name}', type={self.monster_type}, "
                f"level={self.level}, exp={self.experience})")
```

### 🎯 Error-Handling

#### 🚨 Exception-Handling
```python
class MonsterLoadError(Exception):
    """Fehler beim Laden von Monster-Daten."""
    pass

class MonsterValidationError(Exception):
    """Fehler bei der Monster-Validierung."""
    pass

def load_monster_from_file(file_path: Path) -> Monster:
    """Lädt Monster-Daten aus einer Datei.
    
    Args:
        file_path: Pfad zur Monster-Datei
        
    Returns:
        Geladenes Monster-Objekt
        
    Raises:
        MonsterLoadError: Wenn das Laden fehlschlägt
        FileNotFoundError: Wenn die Datei nicht existiert
        MonsterValidationError: Wenn die Daten ungültig sind
    """
    try:
        if not file_path.exists():
            raise FileNotFoundError(f"Monster-Datei nicht gefunden: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # Daten-Validierung
        if not _validate_monster_data(data):
            raise MonsterValidationError(f"Ungültige Monster-Daten in {file_path}")
        
        # Monster-Erstellung
        monster = _create_monster_from_data(data)
        return monster
        
    except json.JSONDecodeError as e:
        raise MonsterLoadError(f"Ungültiges JSON-Format: {e}")
    except Exception as e:
        raise MonsterLoadError(f"Unerwarteter Fehler beim Laden: {e}")

def _validate_monster_data(data: Dict) -> bool:
    """Validiert Monster-Daten."""
    required_fields = ['name', 'type', 'stats', 'level']
    
    # Prüfe erforderliche Felder
    if not all(field in data for field in required_fields):
        return False
    
    # Prüfe Datentypen
    if not isinstance(data['name'], str):
        return False
    
    if not isinstance(data['level'], int):
        return False
    
    # Prüfe Wertebereiche
    if data['level'] < 1 or data['level'] > 100:
        return False
    
    return True
```

---

## 🎨 Asset-Standards

### 🖼️ Grafik-Standards

#### 📐 Auflösung und Format
- **Logische Auflösung**: 320×180 Pixel
- **Skalierung**: 4x auf 1280×720
- **Format**: PNG für Transparenz, JPG für Hintergründe
- **Farbpalette**: 256-Farben für Retro-Look
- **Tile-Größe**: 16×16 Pixel

#### 🎨 Sprite-Standards
```python
# Sprite-Definition
class Sprite:
    """Repräsentiert ein Grafik-Sprite."""
    
    def __init__(self, image_path: Path, frame_width: int, frame_height: int):
        self.image = pygame.image.load(str(image_path))
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.frames = self._extract_frames()
    
    def _extract_frames(self) -> List[pygame.Surface]:
        """Extrahiert Einzelbilder aus dem Sprite-Sheet."""
        frames = []
        image_width, image_height = self.image.get_size()
        
        for y in range(0, image_height, self.frame_height):
            for x in range(0, image_width, self.frame_width):
                frame = pygame.Surface((self.frame_width, self.frame_height))
                frame.blit(self.image, (0, 0), (x, y, self.frame_width, self.frame_height))
                frames.append(frame)
        
        return frames
```

### 🔊 Audio-Standards

#### 🎵 Audio-Spezifikationen
- **Format**: OGG für Musik, WAV für Soundeffekte
- **Qualität**: 44.1 kHz, 16-bit
- **Komprimierung**: Vorbis für Musik
- **Länge**: Musik max. 5 Minuten, SFX max. 10 Sekunden

#### 🔊 Audio-Management
```python
class AudioManager:
    """Verwaltet alle Audio-Assets."""
    
    def __init__(self):
        self.music: Dict[str, pygame.mixer.Sound] = {}
        self.sfx: Dict[str, pygame.mixer.Sound] = {}
        self.current_music: Optional[str] = None
    
    def load_music(self, name: str, file_path: Path) -> None:
        """Lädt Musik-Assets."""
        try:
            self.music[name] = pygame.mixer.Sound(str(file_path))
        except Exception as e:
            print(f"Fehler beim Laden von Musik {name}: {e}")
    
    def play_music(self, name: str, loop: bool = True) -> None:
        """Spielt Musik ab."""
        if name in self.music:
            if self.current_music != name:
                pygame.mixer.music.stop()
                pygame.mixer.music.load(str(self.music[name]))
                pygame.mixer.music.play(-1 if loop else 0)
                self.current_music = name
```

---

## 🧪 Testing-Standards

### 🧪 Test-Struktur

#### 📁 Test-Organisation
```python
# tests/unit/test_monster_system.py
import pytest
from unittest.mock import Mock, patch
from engine.systems.monster_system import MonsterSystem, Monster

class TestMonsterSystem:
    """Tests für das Monster-System."""
    
    def setup_method(self):
        """Setup vor jedem Test."""
        self.monster_system = MonsterSystem()
        self.test_monster = Monster("TestMonster", MonsterType.FIRE, 
                                  MonsterStats(100, 50, 30, 20, 25))
    
    def test_monster_creation(self):
        """Testet die Monster-Erstellung."""
        assert self.test_monster.name == "TestMonster"
        assert self.test_monster.level == 1
        assert self.test_monster.experience == 0
    
    def test_monster_level_up(self):
        """Testet das Aufleveln von Monstern."""
        initial_level = self.test_monster.level
        initial_health = self.test_monster.stats.health
        
        # Genug EP für Level-Up geben
        self.test_monster.gain_experience(150)
        
        assert self.test_monster.level == initial_level + 1
        assert self.test_monster.stats.health > initial_health
    
    def test_invalid_monster_data(self):
        """Testet die Validierung ungültiger Daten."""
        with pytest.raises(ValueError):
            Monster("", MonsterType.FIRE, MonsterStats(100, 50, 30, 20, 25))
        
        with pytest.raises(ValueError):
            Monster("TestMonster", MonsterType.FIRE, 
                   MonsterStats(-100, 50, 30, 20, 25))
    
    @patch('pygame.mixer.Sound')
    def test_monster_sound_loading(self, mock_sound):
        """Testet das Laden von Monster-Sounds."""
        mock_sound.return_value = Mock()
        
        # Test-Implementation
        result = self.monster_system.load_monster_sounds()
        
        assert result is True
        mock_sound.assert_called()
```

### 🧪 Test-Coverage

#### 📊 Coverage-Anforderungen
- **Unit Tests**: Mindestens 80% Code-Coverage
- **Integration Tests**: Alle System-Interaktionen
- **Performance Tests**: Kritische Performance-Pfade
- **Edge Cases**: Alle Grenzfälle und Fehlerszenarien

---

## 📚 Dokumentations-Standards

### 📝 Dokumentations-Format

#### 🏷️ Markdown-Standards
```markdown
# 🎯 Titel der Dokumentation

> **Kurze Beschreibung des Inhalts**

[![Zurück zur Hauptdokumentation](README.md)](README.md) | [📚 Dokumentations-Index](README.md#-dokumentations-index)

---

## 📋 Inhaltsverzeichnis

- [🎯 Abschnitt 1](#-abschnitt-1)
- [🔧 Abschnitt 2](#️-abschnitt-2)
- [📚 Abschnitt 3](#-abschnitt-3)

---

## 🎯 Abschnitt 1

Beschreibung des ersten Abschnitts.

### 🎮 Unterabschnitt

Detaillierte Informationen zum Unterabschnitt.

#### 📊 Beispiel

```python
# Code-Beispiel
def example_function():
    return "Beispiel"
```

---

## 🔧 Abschnitt 2

Beschreibung des zweiten Abschnitts.

---

**Zurück zur [Hauptdokumentation](README.md)** | **📚 [Dokumentations-Index](README.md#-dokumentations-index)**
```

### 📝 Code-Dokumentation

#### 🐍 Docstring-Standards
```python
def complex_function(param1: str, param2: int, 
                   optional_param: bool = False) -> Dict[str, Any]:
    """Kurze Beschreibung der Funktion.
    
    Detaillierte Beschreibung der Funktion, ihrer Funktionsweise
    und der verwendeten Algorithmen.
    
    Args:
        param1: Beschreibung des ersten Parameters
        param2: Beschreibung des zweiten Parameters
        optional_param: Beschreibung des optionalen Parameters
        
    Returns:
        Beschreibung des Rückgabewerts
        
    Raises:
        ValueError: Beschreibung wann dieser Fehler auftritt
        TypeError: Beschreibung wann dieser Fehler auftritt
        
    Example:
        >>> result = complex_function("test", 42, True)
        >>> print(result)
        {'param1': 'test', 'param2': 42, 'optional': True}
        
    Note:
        Wichtige Hinweise zur Verwendung der Funktion.
        
    See Also:
        :func:`related_function`: Verwandte Funktion
        :class:`RelatedClass`: Verwandte Klasse
    """
    # Implementation
    pass
```

---

## 🔧 Debugging & Entwicklung

### 🐛 Debug-System

#### 🔧 Debug-Funktionen
```python
class DebugSystem:
    """Debug-System für Entwickler."""
    
    def __init__(self):
        self.enabled = False
        self.debug_info = {}
    
    def toggle(self) -> None:
        """Schaltet den Debug-Modus um."""
        self.enabled = not self.enabled
        print(f"Debug-Modus: {'Aktiviert' if self.enabled else 'Deaktiviert'}")
    
    def log(self, category: str, message: str) -> None:
        """Loggt eine Debug-Nachricht."""
        if self.enabled:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[DEBUG {timestamp}] {category}: {message}")
    
    def show_info(self, screen: pygame.Surface) -> None:
        """Zeigt Debug-Informationen auf dem Bildschirm an."""
        if not self.enabled:
            return
        
        font = pygame.font.Font(None, 24)
        y_offset = 10
        
        for key, value in self.debug_info.items():
            text = f"{key}: {value}"
            surface = font.render(text, True, (255, 255, 0))
            screen.blit(surface, (10, y_offset))
            y_offset += 25
```

### 🎮 Entwicklungs-Tools

#### 🔧 Utility-Funktionen
```python
def performance_monitor(func):
    """Decorator für Performance-Monitoring."""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        execution_time = end_time - start_time
        if execution_time > 0.016:  # Mehr als 16ms (60 FPS)
            print(f"Performance-Warnung: {func.__name__} brauchte {execution_time:.3f}s")
        
        return result
    return wrapper

def memory_monitor():
    """Überwacht den Speicherverbrauch."""
    import psutil
    process = psutil.Process()
    memory_info = process.memory_info()
    
    print(f"Speicherverbrauch: {memory_info.rss / 1024 / 1024:.1f} MB")
    return memory_info.rss
```

---

## 🚀 Performance-Optimierung

### ⚡ Optimierungs-Strategien

#### 🎨 Rendering-Optimierung
```python
class OptimizedRenderer:
    """Optimierter Renderer für bessere Performance."""
    
    def __init__(self):
        self.sprite_cache = {}
        self.texture_atlas = None
        self.batch_renderer = None
    
    def cache_sprite(self, sprite_id: str, sprite: pygame.Surface) -> None:
        """Cached ein Sprite für bessere Performance."""
        self.sprite_cache[sprite_id] = sprite
    
    def batch_render(self, sprites: List[Tuple[str, pygame.Rect]]) -> None:
        """Rendert mehrere Sprites in einem Batch."""
        # Batch-Rendering-Implementation
        pass
    
    def use_texture_atlas(self, atlas_path: Path) -> None:
        """Verwendet ein Texture-Atlas für bessere Performance."""
        self.texture_atlas = pygame.image.load(str(atlas_path))
```

#### 💾 Speicher-Optimierung
```python
class MemoryManager:
    """Verwaltet den Speicherverbrauch."""
    
    def __init__(self):
        self.asset_cache = {}
        self.max_cache_size = 100 * 1024 * 1024  # 100 MB
    
    def cache_asset(self, asset_id: str, asset_data: Any) -> None:
        """Cached ein Asset mit Größenbeschränkung."""
        if self._get_cache_size() > self.max_cache_size:
            self._cleanup_cache()
        
        self.asset_cache[asset_id] = asset_data
    
    def _get_cache_size(self) -> int:
        """Berechnet die aktuelle Cache-Größe."""
        # Implementation
        return 0
    
    def _cleanup_cache(self) -> None:
        """Bereinigt den Cache."""
        # Entferne alte Assets
        pass
```

---

## 🤝 Zusammenarbeit

### 🔄 Git-Workflow

#### 📝 Commit-Standards
```bash
# ✅ Korrekte Commit-Messages
feat: füge Monster-Synthese-System hinzu
fix: korrigiere Kampf-Bug bei Level-Überschreitung
docs: aktualisiere Entwicklungsrichtlinien
refactor: vereinfache Monster-Statistik-Berechnung
test: füge Tests für Item-System hinzu
style: korrigiere Code-Formatierung

# ❌ Falsche Commit-Messages
fixed bug
update
stuff
```

#### 🔀 Branch-Strategie
- **main**: Stabile Hauptversion
- **develop**: Entwicklungsversion
- **feature/**: Neue Features
- **bugfix/**: Bug-Fixes
- **hotfix/**: Kritische Fixes

### 📋 Code-Review

#### 🔍 Review-Checkliste
- [ ] Code folgt den definierten Standards
- [ ] Alle Tests laufen erfolgreich
- [ ] Dokumentation ist aktualisiert
- [ ] Performance ist akzeptabel
- [ ] Sicherheit ist gewährleistet
- [ ] Edge Cases sind behandelt

---

## 📋 Checklisten

### 🚀 Neue Feature-Entwicklung

#### 📋 Vor der Implementierung
- [ ] Feature in Dokumentation definiert
- [ ] Anforderungen klar spezifiziert
- [ ] Architektur-Entscheidungen getroffen
- [ ] Tests geplant

#### 📋 Während der Implementierung
- [ ] Code folgt den Standards
- [ ] Regelmäßige Commits
- [ ] Tests parallel geschrieben
- [ ] Dokumentation aktualisiert

#### 📋 Nach der Implementierung
- [ ] Alle Tests laufen erfolgreich
- [ ] Code-Review durchgeführt
- [ ] Dokumentation vollständig
- [ ] Performance getestet

### 🧪 Testing-Checkliste

#### 📋 Unit Tests
- [ ] Alle Funktionen getestet
- [ ] Edge Cases abgedeckt
- [ ] Error-Handling getestet
- [ ] Mock-Objekte verwendet

#### 📋 Integration Tests
- [ ] System-Interaktionen getestet
- [ ] Daten-Flows validiert
- [ ] Performance getestet
- [ ] Fehlerszenarien abgedeckt

### 📚 Dokumentations-Checkliste

#### 📋 Code-Dokumentation
- [ ] Alle Funktionen dokumentiert
- [ ] Type Hints vorhanden
- [ ] Beispiele hinzugefügt
- [ ] Edge Cases beschrieben

#### 📋 Projekt-Dokumentation
- [ ] README aktualisiert
- [ ] Änderungen dokumentiert
- [ ] Beispiele hinzugefügt
- [ ] Links korrekt

---

## 🎯 Nächste Schritte

1. **Lies die [Architektur-Dokumentation](technical/ENGINE_ARCHITECTURE.md)**
2. **Folge den [Entwicklungs-Guides](guides/)**
3. **Schau dir die [Code-Beispiele](examples/) an**
4. **Starte mit dem [Anfänger-Guide](guides/BEGINNER_GUIDE.md)**

---

**Zurück zur [Hauptdokumentation](README.md)** | **📚 [Dokumentations-Index](README.md#-dokumentations-index)**

---

*"Dat is ja mal ne richtig durchdachte Entwicklungsrichtlinie, wa? Jetzt kannste richtig professionell entwickeln!"* 🛠️✨
