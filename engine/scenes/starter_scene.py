"""
Starter selection scene for Untold Story.
Player chooses their first monster from Professor Budde's fossils.
"""

import pygame
import math
import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from engine.core.scene_base import Scene
from engine.core.config import LOGICAL_WIDTH, LOGICAL_HEIGHT, Colors
from engine.systems.monster_instance import MonsterInstance
from engine.ui.dialogue import DialogueBox


@dataclass
class ManagerStatus:
    """Status information for a manager."""
    available: bool
    error_message: Optional[str] = None
    fallback_active: bool = False


class StarterScene(Scene):
    """Scene for selecting starter monster."""
    
    def __init__(self, game):
        super().__init__(game)
        
        # Initialize logger
        self.logger = logging.getLogger(__name__)
        
        # UI components
        self.dialogue_box = DialogueBox(
            x=10,
            y=120,
            width=300,
            height=50
        )
        
        # Starter monsters data (E-rank fossils at level 5)
        self.starters = []
        self.starter_data = [
            {
                'id': 24,
                'name': 'Sumpfschrecke',
                'types': ['Wasser'],
                'description': 'Ein prähistorischer Wasserdrache aus der Urzeit. Schwimmt elegant durch die Tiefen!',
                'color': (50, 150, 255)
            },
            {
                'id': 26,
                'name': 'Kraterkröte',
                'types': ['Erde'],
                'description': 'Eine uralte Erdkaiserin mit Granitpanzer. Steht fest wie ein Berg!',
                'color': (150, 100, 50)
            },
            {
                'id': 32,
                'name': 'Säbelzahnkaninchen',
                'types': ['Bestie'],
                'description': 'Ein wildes Urzeit-Kaninchen mit messerscharfen Zähnen. Schnell und tödlich!',
                'color': (200, 150, 100)
            },
            {
                'id': 40,
                'name': 'Irrlicht',
                'types': ['Mystisch'],
                'description': 'Ein mystischer Geist aus der Urzeit. Kontrolliert die Schatten der Vergangenheit!',
                'color': (100, 50, 150)
            }
        ]
        
        # Selection state
        self.selected_index = 0
        self.state = 'intro'  # intro, selecting, confirming, done
        self.confirm_choice = False
        
        # Visual settings
        self.card_width = 60
        self.card_height = 80
        self.card_spacing = 10
        
        # Enhanced animation
        self.hover_offset = pygame.math.Vector2(0, 0)
        self.hover_timer = 0
        self.selection_pulse = 0
        self.card_glow_intensity = 0
        
        # Enhanced fonts with fallbacks
        self.font = None
        self.big_font = None
        self.hint_font = None
        self._load_fonts_with_fallbacks()
        
        # Manager status tracking
        self.manager_status: Dict[str, ManagerStatus] = {}
        self._check_manager_availability()
        
        # UI state tracking
        self.last_input_time = 0
        self.input_cooldown = 0.15  # Prevent rapid input
        self.show_help = False
        self.help_timer = 0
        
        # Enhanced visual feedback
        self.selection_highlight_color = (255, 255, 0)  # Bright yellow
        self.card_glow_color = (100, 200, 255)  # Light blue glow
        self.error_color = (255, 100, 100)  # Red for errors
        
        # Monster sprite cache
        self.monster_sprite_cache = {}
        
        # Log manager status
        self.log_manager_status()
    
    def _load_fonts_with_fallbacks(self) -> None:
        """Load fonts with robust fallback system."""
        font_sizes = {
            'font': 12,
            'big_font': 16,
            'hint_font': 10
        }
        
        for font_name, size in font_sizes.items():
            font = None
            
            # Try multiple font loading strategies
            try:
                # First try: System default font
                font = pygame.font.Font(None, size)
                print(f"[StarterScene] Font {font_name} geladen (System)")
            except:
                try:
                    # Second try: Arial if available
                    font = pygame.font.Font("arial.ttf", size)
                    print(f"[StarterScene] Font {font_name} geladen (Arial)")
                except:
                    try:
                        # Third try: Any available font
                        available_fonts = pygame.font.get_fonts()
                        if available_fonts:
                            first_font = available_fonts[0]
                            font = pygame.font.Font(first_font, size)
                            print(f"[StarterScene] Font {font_name} geladen ({first_font})")
                        else:
                            # Last resort: Create a basic font
                            font = pygame.font.Font(None, 16)
                            print(f"[StarterScene] Font {font_name} geladen (Fallback)")
                    except Exception as e:
                        print(f"[StarterScene] Kritischer Font-Fehler für {font_name}: {e}")
                        # Create a minimal font object to prevent crashes
                        font = pygame.font.Font(None, 16)
            
            setattr(self, font_name, font)
    
    def _check_manager_availability(self) -> None:
        """Check availability of all required managers and set fallbacks."""
        self.manager_status = {}
        
        # Check ResourceManager
        try:
            if hasattr(self.game, 'resources') and self.game.resources:
                self.manager_status['resources'] = ManagerStatus(available=True)
                self.logger.info("ResourceManager verfügbar")
            else:
                self.manager_status['resources'] = ManagerStatus(
                    available=False, 
                    error_message="ResourceManager nicht in Game-Instanz gefunden",
                    fallback_active=True
                )
                self.logger.warning("ResourceManager nicht verfügbar - Fallback aktiv")
        except Exception as e:
            self.manager_status['resources'] = ManagerStatus(
                available=False, 
                error_message=f"Fehler beim Zugriff auf ResourceManager: {e}",
                fallback_active=True
            )
            self.logger.error(f"Fehler beim Zugriff auf ResourceManager: {e}")
        
        # Check PartyManager
        try:
            if hasattr(self.game, 'party_manager') and self.game.party_manager:
                self.manager_status['party'] = ManagerStatus(available=True)
                self.logger.info("PartyManager verfügbar")
            else:
                self.manager_status['party'] = ManagerStatus(
                    available=False, 
                    error_message="PartyManager nicht in Game-Instanz gefunden",
                    fallback_active=True
                )
                self.logger.warning("PartyManager nicht verfügbar - Fallback aktiv")
        except Exception as e:
            self.manager_status['party'] = ManagerStatus(
                available=False, 
                error_message=f"Fehler beim Zugriff auf PartyManager: {e}",
                fallback_active=True
            )
            self.logger.error(f"Fehler beim Zugriff auf PartyManager: {e}")
        
        # Check StoryManager
        try:
            if hasattr(self.game, 'story_manager') and self.game.story_manager:
                self.manager_status['story'] = ManagerStatus(available=True)
                self.logger.info("StoryManager verfügbar")
            else:
                self.manager_status['story'] = ManagerStatus(
                    available=False, 
                    error_message="StoryManager nicht in Game-Instanz gefunden",
                    fallback_active=True
                )
                self.logger.warning("StoryManager nicht verfügbar - Fallback aktiv")
        except Exception as e:
            self.manager_status['story'] = ManagerStatus(
                available=False, 
                error_message=f"Fehler beim Zugriff auf StoryManager: {e}",
                fallback_active=True
            )
            self.logger.error(f"❌ Fehler beim Zugriff auf StoryManager: {e}")
        
        # Check SpriteManager
        try:
            if hasattr(self.game, 'sprite_manager') and self.game.sprite_manager:
                self.manager_status['sprite'] = ManagerStatus(available=True)
                self.logger.info("SpriteManager verfügbar")
            else:
                self.manager_status['sprite'] = ManagerStatus(
                    available=False, 
                    error_message="SpriteManager nicht in Game-Instanz gefunden",
                    fallback_active=True
                )
                self.logger.warning("SpriteManager nicht verfügbar - Fallback aktiv")
        except Exception as e:
            self.manager_status['sprite'] = ManagerStatus(
                available=False, 
                error_message=f"Fehler beim Zugriff auf SpriteManager: {e}",
                fallback_active=True
            )
            self.logger.error(f"Fehler beim Zugriff auf SpriteManager: {e}")
    
    def _log_manager_status(self) -> None:
        """Log the status of all managers."""
        print("\n=== StarterScene Manager Status ===")
        for manager_name, status in self.manager_status.items():
            if status.available:
                print(f"✅ {manager_name}: Verfügbar")
            else:
                print(f"❌ {manager_name}: Nicht verfügbar")
                if status.error_message:
                    print(f"   Fehler: {status.error_message}")
                if status.fallback_active:
                    print(f"   Fallback: Aktiv")
        print("===================================\n")
    
    def _safe_get_monster_species(self, monster_id: int) -> Optional[Any]:
        """Safely get monster species data with robust fallback."""
        if not self.manager_status.get('resources', ManagerStatus(available=False)).available:
            print(f"[StarterScene] ⚠️  ResourceManager nicht verfügbar für Monster {monster_id}")
            return None
        
        try:
            species_data = self.game.resources.get_monster_species(monster_id)
            
            if species_data:
                # Validate species data
                required_fields = ['id', 'name', 'types', 'base_stats']
                missing_fields = [field for field in required_fields if field not in species_data]
                
                if missing_fields:
                    print(f"[StarterScene] ⚠️  Monster {monster_id} hat fehlende Felder: {missing_fields}")
                    return None
                
                # Validate base_stats
                if 'base_stats' in species_data:
                    base_stats = species_data['base_stats']
                    required_stats = ['hp', 'atk', 'def', 'mag', 'res', 'spd']
                    missing_stats = [stat for stat in required_stats if stat not in base_stats]
                    
                    if missing_stats:
                        print(f"[StarterScene] ⚠️  Monster {monster_id} hat fehlende BaseStats: {missing_stats}")
                        return None
                
                print(f"[StarterScene] ✅ Monster {monster_id} erfolgreich aus Datenbank geladen")
                return species_data
            else:
                print(f"[StarterScene] ⚠️  Monster {monster_id} nicht in Datenbank gefunden")
                return None
                
        except Exception as e:
            print(f"[StarterScene] ❌ Fehler beim Laden der Monster-Species {monster_id}: {e}")
            return None
    
    def _safe_get_monster_sprite(self, monster_id: int) -> Optional[pygame.Surface]:
        """Safely get monster sprite with robust fallback system."""
        # Versuche zuerst aus dem lokalen Cache
        monster_id_str = str(monster_id)
        if monster_id_str in self.monster_sprite_cache:
            return self.monster_sprite_cache[monster_id_str]
        
        # Fallback: Versuche über SpriteManager
        if not self.manager_status.get('sprite', ManagerStatus(available=False)).available:
            return None
        
        try:
            sprite_mgr = self.game.sprite_manager
            sprite = None
            
            # Verschiedene Zugriffswege versuchen
            if hasattr(sprite_mgr, 'monster_sprites') and monster_id_str in sprite_mgr.monster_sprites:
                sprite = sprite_mgr.monster_sprites[monster_id_str]
                print(f"[StarterScene] Monster-Sprite {monster_id} über monster_sprites geladen")
            
            elif hasattr(sprite_mgr, '_monster') and monster_id_str in sprite_mgr._monster:
                sprite = sprite_mgr._monster[monster_id_str]
                print(f"[StarterScene] Monster-Sprite {monster_id} über _monster geladen")
            
            elif hasattr(sprite_mgr, 'sprite_cache'):
                sprite_key = f"monster_{monster_id_str}"
                if sprite_key in sprite_mgr.sprite_cache:
                    sprite = sprite_mgr.sprite_cache[sprite_key]
                    print(f"[StarterScene] Monster-Sprite {monster_id} über sprite_cache geladen")
            
            # Wenn Sprite gefunden, skaliere und cache ihn
            if sprite:
                try:
                    scaled_sprite = pygame.transform.scale(sprite, (40, 40))
                    self.monster_sprite_cache[monster_id_str] = scaled_sprite
                    return scaled_sprite
                except Exception as e:
                    print(f"[StarterScene] Fehler beim Skalieren des Sprites {monster_id}: {e}")
                    return None
            else:
                print(f"[StarterScene] Monster-Sprite {monster_id} nicht in SpriteManager gefunden")
                return None
                
        except Exception as e:
            print(f"[StarterScene] Fehler beim Laden des Monster-Sprites {monster_id}: {e}")
            return None
    
    def _create_placeholder_sprite(self, monster_id: int, color: tuple) -> pygame.Surface:
        """Create a placeholder sprite when real sprite is not available."""
        try:
            # Create a 40x40 surface
            sprite = pygame.Surface((40, 40))
            sprite.fill(color)
            
            # Add a border
            pygame.draw.rect(sprite, (0, 0, 0), sprite.get_rect(), 2)
            
            # Add monster ID for debugging
            try:
                font = pygame.font.Font(None, 16)
                id_text = font.render(str(monster_id), True, (255, 255, 255))
                text_rect = id_text.get_rect(center=sprite.get_rect().center)
                sprite.blit(id_text, text_rect)
            except:
                pass
            
            self.logger.debug(f"Placeholder-Sprite für Monster {monster_id} erstellt")
            return sprite
            
        except Exception as e:
            self.logger.error(f"Fehler beim Erstellen des Placeholder-Sprites für Monster {monster_id}: {e}")
            # Return a basic colored rectangle as last resort
            fallback = pygame.Surface((40, 40))
            fallback.fill(color)
            return fallback
    
    def _load_monster_sprites(self):
        """Lade Monster-Sprites in den Cache für die Starter-Auswahl."""
        try:
            self.logger.info("Lade Monster-Sprites für Starter-Auswahl...")
            
            # Versuche Monster-Sprites über den SpriteManager zu laden
            if hasattr(self.game, 'sprite_manager') and self.game.sprite_manager:
                sprite_manager = self.game.sprite_manager
                
                # Lade Sprites für alle Starter-Monster
                for data in self.starter_data:
                    monster_id = data['id']
                    try:
                        # Versuche den Monster-Sprite zu laden
                        if hasattr(sprite_manager, 'get_monster_sprite'):
                            sprite = sprite_manager.get_monster_sprite(monster_id)
                            if sprite:
                                self.logger.info(f"✅ Monster-Sprite {monster_id} geladen")
                            else:
                                self.logger.warning(f"⚠️  Monster-Sprite {monster_id} nicht gefunden")
                        else:
                            self.logger.warning("SpriteManager hat keine get_monster_sprite Methode")
                    except Exception as e:
                        self.logger.warning(f"⚠️  Fehler beim Laden von Monster-Sprite {monster_id}: {e}")
                
                self.logger.info("Monster-Sprites geladen")
            else:
                self.logger.warning("SpriteManager nicht verfügbar - überspringe Monster-Sprite-Laden")
                
        except Exception as e:
            self.logger.error(f"Fehler beim Laden der Monster-Sprites: {e}")
    
    def enter(self, **kwargs):
        """Initialize the scene."""
        self.logger.info("Initialisiere Starter-Auswahl")
        
        # Lade Monster-Sprites in den Cache
        self._load_monster_sprites()
        
        # Create starter monster instances with robust fallback system
        self.starters = []
        for data in self.starter_data:
            monster = self._create_starter_monster(data)
            self.starters.append(monster)
        
        # Validate all starter monsters
        if not self._validate_starter_monsters():
            self.logger.warning("Monster-Validierung fehlgeschlagen, versuche Notfall-Fallbacks...")
            if not self._handle_monster_creation_failure():
                self.logger.error("KRITISCHER FEHLER: Konnte keine Starter-Monster erstellen!")
                # Create at least one basic monster to prevent crash
                self._create_minimal_fallback()
        
        # Start with intro
        self.state = 'intro'
        self.show_intro_dialogue()
        
        self.logger.info(f"{len(self.starters)} Starter bereit")
    
    def _create_starter_monster(self, data: dict) -> MonsterInstance:
        """Create a starter monster with Talent-System integration."""
        monster = None
        
        # Try to load from database first using safe method
        species_data = self._safe_get_monster_species(data['id'])
        
        if species_data:
            self.logger.info(f"Lade Monster aus Datenbank: {data['name']} (ID: {data['id']})")
            try:
                monster = MonsterInstance.create_from_species(
                    species_data,
                    5
                )
                self.logger.info(f"Erfolgreich geladen: {monster.species_name}")
                
                # Validiere Talents
                if not monster.validate_talents():
                    self.logger.warning(f"Talent-Validierung für {monster.name} fehlgeschlagen")
                
                # Validiere Moves
                if not monster.moves:
                    self.logger.warning(f"Keine Moves für {monster.name} geladen")
                    monster.moves = [monster._create_fallback_move()]
                
                self.logger.info(f"Starter-Monster {monster.name} mit {len(monster.talents)} Talents und {len(monster.moves)} Moves erstellt")
                
            except Exception as e:
                self.logger.error(f"Fehler beim Erstellen von Monster {data['name']}: {e}")
        else:
            self.logger.info(f"Monster {data['name']} (ID: {data['id']}) nicht in Datenbank gefunden")
        
        # Use fallback if database loading failed
        if not monster:
            self.logger.info(f"Nutze Fallback für: {data['name']} (ID: {data['id']})")
            monster = self._create_fallback_starter(data)
        
        # species_name wird automatisch aus species.name geholt
        
        # Validate monster creation
        if not monster:
            self.logger.error(f"KRITISCHER FEHLER: Konnte Monster {data['name']} nicht erstellen!")
            monster = self._create_emergency_fallback(data)
        
        return monster
    
    def _add_default_moves(self, monster: MonsterInstance) -> None:
        """Entferne - Moves kommen jetzt über Talents."""
        # Diese Methode kann entfernt werden
        self.logger.debug("_add_default_moves() aufgerufen - nicht mehr benötigt mit Talent-System")
        pass
    
    def _create_dummy_moves(self, monster: MonsterInstance) -> None:
        """Create dummy moves as last resort."""
        try:
            # Create a simple dummy move class
            class DummyMove:
                def __init__(self, name: str):
                    self.name = name
                    self.power = 10
                    self.accuracy = 90
                    self.type = "Bestie"
                    self.description = f"Ein {name} Move"
            
            monster.moves = [
                DummyMove("Rempler"),
                DummyMove("Kratzer")
            ]
            self.logger.info(f"✅ Dummy-Moves für {monster.species_name} erstellt")
            
        except Exception as e:
            self.logger.error(f"❌ Fehler beim Erstellen von Dummy-Moves: {e}")
            monster.moves = []
    
    def _validate_starter_monsters(self) -> bool:
        """Validate that all starter monsters were created correctly."""
        self.logger.info("🔍 Validiere Starter-Monster...")
        
        all_valid = True
        for i, monster in enumerate(self.starters):
            if not monster:
                self.logger.error(f"❌ Starter {i} ist None!")
                all_valid = False
                continue
            
            # Check basic properties
            if not hasattr(monster, 'species_name') or not monster.species_name:
                self.logger.warning(f"⚠️  Starter {i} hat keinen species_name")
                # species_name wird automatisch aus species.name geholt
            
            if not hasattr(monster, 'level') or monster.level != 5:
                self.logger.warning(f"⚠️  Starter {i} hat falsches Level: {getattr(monster, 'level', 'N/A')}")
                monster.level = 5
            
            if not hasattr(monster, 'max_hp') or monster.max_hp < 10:
                self.logger.warning(f"⚠️  Starter {i} hat zu niedrige HP: {getattr(monster, 'max_hp', 'N/A')}")
            
            # Check and fix moves
            if not hasattr(monster, 'moves') or not monster.moves:
                self.logger.warning(f"⚠️  Starter {i} hat keine Moves, füge Standard-Moves hinzu")
                self._add_default_moves(monster)
            
            # Validate moves are usable
            if hasattr(monster, 'moves') and monster.moves:
                valid_moves = []
                for move in monster.moves:
                    if hasattr(move, 'name') and move.name:
                        valid_moves.append(move)
                    else:
                        self.logger.warning(f"⚠️  Ungültiger Move in Starter {i} gefunden")
                
                if len(valid_moves) < len(monster.moves):
                    self.logger.info(f"🔧 Korrigiere Moves für Starter {i}")
                    monster.moves = valid_moves
                
                if not monster.moves:
                    self.logger.warning(f"⚠️  Starter {i} hat immer noch keine gültigen Moves")
                    self._add_default_moves(monster)
            
            # Final validation
            if hasattr(monster, 'moves') and monster.moves:
                self.logger.info(f"✅ Starter {i} ({monster.species_name}): Level {monster.level}, HP {monster.max_hp}, {len(monster.moves)} Moves")
                # List moves for debugging
                for j, move in enumerate(monster.moves):
                    move_name = getattr(move, 'name', f'Unbekannter Move {j}')
                    self.logger.debug(f"   - Move {j+1}: {move_name}")
            else:
                self.logger.error(f"❌ Starter {i} ({monster.species_name}): Level {monster.level}, HP {monster.max_hp}, KEINE MOVES!")
                all_valid = False
        
        if all_valid:
            self.logger.info("✅ Alle Starter-Monster sind gültig und einsatzbereit")
        else:
            self.logger.warning("⚠️  Einige Starter-Monster haben Probleme - Fallbacks aktiv")
        
        # Display detailed statistics for debugging
        self._display_monster_statistics()
        
        return all_valid
    
    def _display_monster_statistics(self) -> None:
        """Display detailed statistics of all starter monsters for debugging."""
        self.logger.info("\n=== STARTER-MONSTER STATISTIKEN ===")
        
        for i, monster in enumerate(self.starters):
            if not monster:
                self.logger.error(f"Starter {i}: ❌ Nicht erstellt")
                continue
            
            self.logger.info(f"\n--- Starter {i}: {getattr(monster, 'species_name', 'Unbekannt')} ---")
            
            # Basic info
            level = getattr(monster, 'level', 'N/A')
            hp = getattr(monster, 'max_hp', 'N/A')
            current_hp = getattr(monster, 'current_hp', 'N/A')
            self.logger.info(f"Level: {level}, HP: {current_hp}/{hp}")
            
            # Stats
            if hasattr(monster, 'stats') and monster.stats:
                stats_str = "Stats: " + " ".join([f"{stat_name}: {stat_value}" for stat_name, stat_value in monster.stats.items()])
                self.logger.info(stats_str)
            else:
                self.logger.info("Stats: Nicht verfügbar")
            
            # Moves
            if hasattr(monster, 'moves') and monster.moves:
                moves_str = f"Moves ({len(monster.moves)}): " + ", ".join([getattr(move, 'name', f'Move{i}') for i, move in enumerate(monster.moves)])
                self.logger.info(moves_str)
            else:
                self.logger.info("Moves: Keine verfügbar")
            
            # Species info
            if hasattr(monster, 'species') and monster.species:
                species = monster.species
                types = getattr(species, 'types', ['Unbekannt'])
                rank = getattr(species, 'rank', 'Unbekannt')
                era = getattr(species, 'era', 'Unbekannt')
                self.logger.info(f"Typ: {types}, Rang: {rank}, Ära: {era}")
            else:
                self.logger.info("Species-Info: Nicht verfügbar")
        
        self.logger.info("=====================================\n")
    
    def _handle_monster_creation_failure(self) -> bool:
        """Handle complete failure of monster creation with emergency fallbacks."""
        self.logger.error("🚨 KRITISCHER FEHLER: Monster-Erstellung fehlgeschlagen!")
        self.logger.info("🔄 Erstelle Notfall-Fallbacks...")
        
        try:
            # Create emergency monsters with minimal data
            self.starters = []
            for i, data in enumerate(self.starter_data):
                emergency_monster = self._create_emergency_fallback(data)
                if emergency_monster:
                    self.starters.append(emergency_monster)
                    self.logger.info(f"✅ Notfall-Monster {i} erstellt: {emergency_monster.species_name}")
                else:
                    # Last resort: create a completely basic monster
                    basic_monster = self._create_basic_monster(data)
                    if basic_monster:
                        self.starters.append(basic_monster)
                        self.logger.info(f"✅ Basis-Monster {i} erstellt: {basic_monster.species_name}")
                    else:
                        self.logger.error(f"❌ Konnte auch Basis-Monster {i} nicht erstellen!")
                        return False
            
            # Validate emergency monsters
            if len(self.starters) == len(self.starter_data):
                self.logger.info("✅ Alle Notfall-Monster erfolgreich erstellt")
                return True
            else:
                self.logger.error(f"❌ Nur {len(self.starters)} von {len(self.starter_data)} Notfall-Monstern erstellt")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Fehler bei Notfall-Monster-Erstellung: {e}")
            return False
    
    def _create_minimal_fallback(self) -> None:
        """Create minimal fallback monsters to prevent complete failure."""
        self.logger.error("🚨 Erstelle minimale Fallback-Monster...")
        
        try:
            self.starters = []
            for i, data in enumerate(self.starter_data):
                # Create the most basic possible monster
                basic_monster = self._create_basic_monster(data)
                if basic_monster:
                    self.starters.append(basic_monster)
                    self.logger.info(f"✅ Minimales Fallback-Monster {i} erstellt: {basic_monster.species_name}")
                else:
                    # Absolute last resort: create a dummy monster
                    dummy_monster = self._create_dummy_monster(data, i)
                    self.starters.append(dummy_monster)
                    self.logger.info(f"✅ Dummy-Monster {i} erstellt: {dummy_monster.species_name}")
            
            self.logger.info(f"✅ {len(self.starters)} minimale Fallback-Monster erstellt")
            
        except Exception as e:
            self.logger.error(f"❌ Fehler bei minimaler Fallback-Erstellung: {e}")
            # Create at least one monster to prevent crash
            self._create_crash_prevention_monster()
    
    def _create_dummy_monster(self, data: dict, index: int) -> MonsterInstance:
        """Create a completely dummy monster as absolute last resort."""
        try:
            from engine.systems.monster_instance import MonsterSpecies, MonsterInstance, MonsterRank
            from engine.systems.stats import BaseStats, GrowthCurve
            
            # Minimal stats
            base_stats = BaseStats(hp=20, atk=15, def_=15, mag=15, res=15, spd=15)
            
            species = MonsterSpecies(
                id=data['id'],
                name=data['name'],
                types=data['types'],
                base_stats=base_stats,
                rank=MonsterRank.E,
                growth_curve=GrowthCurve.MEDIUM_FAST,
                description="Ein Monster."
            )
            
            monster = MonsterInstance(species, level=5)
            # species_name wird automatisch aus species.name geholt
            
            # Add dummy moves
            self._create_dummy_moves(monster)
            
            return monster
            
        except Exception as e:
            self.logger.error(f"❌ Fehler bei Dummy-Monster-Erstellung: {e}")
            return self._create_crash_prevention_monster()
    
    def _create_crash_prevention_monster(self) -> MonsterInstance:
        """Create a monster to prevent complete crash."""
        self.logger.error("🚨 Erstelle Crash-Prevention-Monster...")
        
        try:
            # Create a completely basic monster class
            class CrashPreventionMonster:
                def __init__(self):
                    self.species_name = "Unbekanntes Monster"
                    self.level = 5
                    self.max_hp = 20
                    self.current_hp = 20
                    self.stats = {'hp': 20, 'atk': 15, 'def': 15, 'mag': 15, 'res': 15, 'spd': 15}
                    self.moves = []
                    self.species = type('obj', (object,), {
                        'name': 'Unbekanntes Monster',
                        'types': ['Bestie'],
                        'rank': 'E'
                    })()
            
            monster = CrashPreventionMonster()
            self.logger.info("✅ Crash-Prevention-Monster erstellt")
            return monster
            
        except Exception as e:
            self.logger.error(f"❌ KRITISCHER FEHLER: Konnte auch Crash-Prevention-Monster nicht erstellen: {e}")
            # Return None and let the scene handle it
            return None
    
    def _create_emergency_fallback(self, data: dict) -> MonsterInstance:
        """Create a minimal monster as last resort."""
        try:
            self.logger.info(f"Erstelle Notfall-Fallback für {data['name']}")
            
            # Minimal viable monster
            base_stats = BaseStats(hp=30, atk=25, def_=25, mag=25, res=25, spd=25)
            
            species = MonsterSpecies(
                id=data['id'],
                name=data['name'],
                types=data['types'],
                base_stats=base_stats,
                rank=MonsterRank.E,
                growth_curve=GrowthCurve.MEDIUM_FAST,
                description=data['description']
            )
            
            monster = MonsterInstance(species, level=5)
            # species_name wird automatisch aus species.name geholt
            
            self.logger.info(f"Notfall-Fallback erstellt: {monster.species_name}")
            return monster
            
        except Exception as e:
            self.logger.error(f"KRITISCHER FEHLER: Konnte auch Notfall-Fallback nicht erstellen: {e}")
            # Return a completely basic monster
            return self._create_basic_monster(data)
    
    def _create_basic_monster(self, data: dict) -> MonsterInstance:
        """Create the most basic possible monster."""
        try:
            # Absolute minimal monster
            base_stats = BaseStats(hp=20, atk=20, def_=20, mag=20, res=20, spd=20)
            
            species = MonsterSpecies(
                id=data['id'],
                name=data['name'],
                types=['Bestie'],
                base_stats=base_stats,
                rank=MonsterRank.E,
                growth_curve=GrowthCurve.MEDIUM_FAST,
                description="Ein Monster."
            )
            
            monster = MonsterInstance(species, level=5)
            # species_name wird automatisch aus species.name geholt
            
            self.logger.info(f"Basis-Monster erstellt: {monster.species_name}")
            return monster
            
        except Exception as e:
            self.logger.error(f"UNBEHEBBARER FEHLER: {e}")
            # This should never happen, but if it does, return None
            return None
    
    def _create_fallback_starter(self, data):
        """Create a basic starter if not in database."""
        from engine.systems.monster_instance import MonsterSpecies, MonsterInstance
        from engine.systems.stats import BaseStats, GrowthCurve
        from engine.systems.monster_instance import MonsterRank
        
        # Angepasste Stats basierend auf dem Monster-Typ für bessere Starter
        if data['name'] == 'Sumpfschrecke':
            base_stats = BaseStats(hp=45, atk=28, def_=50, mag=25, res=33, spd=30)
            talents = [{"talent_id": "water_i", "learned_at_level": 1, "current_tier": 1, "experience": 0}]
        elif data['name'] == 'Kraterkröte':
            base_stats = BaseStats(hp=52, atk=27, def_=51, mag=29, res=28, spd=19)
            talents = [{"talent_id": "earth_i", "learned_at_level": 1, "current_tier": 1, "experience": 0}]
        elif data['name'] == 'Säbelzahnkaninchen':
            base_stats = BaseStats(hp=48, atk=54, def_=23, mag=22, res=26, spd=36)
            talents = [{"talent_id": "physical_i", "learned_at_level": 1, "current_tier": 1, "experience": 0}]
        elif data['name'] == 'Irrlicht':
            base_stats = BaseStats(hp=28, atk=23, def_=33, mag=46, res=31, spd=31)
            talents = [{"talent_id": "mystic_i", "learned_at_level": 1, "current_tier": 1, "experience": 0}]
        else:
            # Generic fallback
            base_stats = BaseStats(hp=45, atk=28, def_=50, mag=25, res=33, spd=30)
            talents = [{"talent_id": "physical_i", "learned_at_level": 1, "current_tier": 1, "experience": 0}]
        
        species = MonsterSpecies(
            id=data['id'],
            name=data['name'],
            types=data['types'],
            base_stats=base_stats,
            rank=MonsterRank.E,
            growth_curve=GrowthCurve.MEDIUM_FAST,
            talents=talents,  # Verwende Talents statt learnset
            description=data['description']
        )
        
        # Create monster instance
        monster = MonsterInstance(species, level=5)
        
        # Validiere Talents
        if not monster.validate_talents():
            self.logger.warning(f"Talent-Validierung für {monster.name} fehlgeschlagen")
        
        # Validiere Moves
        if not monster.moves:
            self.logger.warning(f"Keine Moves für {monster.name} geladen")
            monster.moves = [monster._create_fallback_move()]
        
        self.logger.info(f"Fallback-Monster erstellt: {monster.species_name} mit {len(monster.talents)} Talents und {len(monster.moves)} Moves")
        return monster
    
    def show_intro_dialogue(self):
        """Show Professor Budde's introduction."""
        from engine.ui.dialogue import DialoguePage
        
        pages = [
            DialoguePage("Also pass auf, du Knallkopf. Ich hab hier vier verschiedene Viecher:", "Prof. Budde"),
            DialoguePage("Die sind alle aus'm Kohleflöz ausgegraben und wiederbelebt!", "Prof. Budde"),
            DialoguePage("Jedes hat seine eigenen Stärken und Schwächen.", "Prof. Budde"),
            DialoguePage("Aber alle sind verdammt stark für Anfänger-Monster!", "Prof. Budde"),
            DialoguePage("Such dir eins aus - aber überleg gut!", "Prof. Budde"),
            DialoguePage("Das Viech begleitet dich durch dick und dünn!", "Prof. Budde")
        ]
        
        self.dialogue_box.show_dialogue(pages)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle input events with improved input handling and cooldown."""
        current_time = pygame.time.get_ticks() / 1000.0
        
        # Input cooldown to prevent rapid input
        if current_time - self.last_input_time < self.input_cooldown:
            return False
        
        # Let dialogue handle input first if active
        if self.dialogue_box.is_open():
            handled = self.dialogue_box.handle_input(event)
            # Check if dialogue finished
            if not self.dialogue_box.is_open():
                if self.state == 'intro':
                    self.logger.info("Intro beendet, wechsle zu 'selecting'")
                    self.state = 'selecting'
                    self.hover_timer = 0  # Reset animation
                elif self.state == 'confirming' and self.confirm_choice:
                    # After confirmation dialogue, show the final choice dialogue
                    self.logger.info(f"Bestätigung beendet, wähle Starter {self.selected_index}")
                    self.choose_starter()
                elif self.state == 'done':
                    # After final dialogue, immediately exit to museum
                    self.logger.info("Finaler Dialog beendet, wechsle sofort zurück ins Museum")
                    self._return_to_field_scene()
            return handled
        
        if event.type == pygame.KEYDOWN:
            # Update input time for cooldown
            self.last_input_time = current_time
            
            if self.state == 'selecting':
                if event.key == pygame.K_a:  # Left
                    self.selected_index = (self.selected_index - 1) % 4
                    self.hover_timer = 0
                    self.logger.info(f"Links gewählt: Starter {self.selected_index}")
                    
                elif event.key == pygame.K_d:  # Right
                    self.selected_index = (self.selected_index + 1) % 4
                    self.hover_timer = 0
                    self.logger.info(f"Rechts gewählt: Starter {self.selected_index}")
                    
                elif event.key in [pygame.K_e, pygame.K_RETURN, pygame.K_SPACE]:  # Confirm
                    self.logger.info(f"Starter {self.selected_index} ausgewählt, wechsle zu 'confirming'")
                    self.state = 'confirming'
                    self.show_confirm_dialogue()
                    
                elif event.key == pygame.K_h:  # Help
                    self.show_help = not self.show_help
                    self.help_timer = 0
                    self.logger.info(f"Hilfe {'eingeschaltet' if self.show_help else 'ausgeschaltet'}")
                    
            elif self.state == 'confirming':
                if event.key in [pygame.K_j, pygame.K_y]:  # Ja/Yes
                    # YES - Choose this starter immediately
                    self.logger.info(f"Ja gedrückt, wähle Starter {self.selected_index} sofort")
                    self.confirm_choice = True
                    # Force dialogue to close and proceed
                    from engine.ui.dialogue import DialogueState
                    self.dialogue_box.state = DialogueState.CLOSED
                    self.dialogue_box.visible = False
                    self.choose_starter()
                elif event.key in [pygame.K_n, pygame.K_ESCAPE]:  # Nein/No
                    # NO - Go back to selection
                    self.logger.info("Nein gedrückt, gehe zurück zur Auswahl")
                    from engine.ui.dialogue import DialogueState
                    self.dialogue_box.state = DialogueState.CLOSED
                    self.dialogue_box.visible = False
                    self.state = 'selecting'
                    self.confirm_choice = False
            
            return True
        
        return False
    
    def show_confirm_dialogue(self):
        """Show confirmation dialogue for selected starter."""
        from engine.ui.dialogue import DialoguePage
        
        starter = self.starters[self.selected_index]
        data = self.starter_data[self.selected_index]
        
        # Spezifische Erklärungen für jedes Fossil
        explanations = {
            'Sumpfschrecke': [
                "Das hier is'n Sumpfschrecke - ein prähistorischer Wasserdrache!",
                "War mal'n Meeresungeheuer in der Urzeit, vor paar Millionen Jahren.",
                "Jetzt isses'n wandelnder Tsunami. Perfekt für Wasserköpfe wie dich!"
            ],
            'Kraterkröte': [
                "Kraterkröte - das Ding hat Vulkanausbrüche überlebt!",
                "Hat in irgend'nem Urzeitkrater gehockt und is versteinert.",
                "Aber unterschätz das Teil nich - kann dich zerquetschen wie'n Bergsturz!"
            ],
            'Säbelzahnkaninchen': [
                "Säbelzahnkaninchen - wild wie'n Bergmann nach Doppelschicht!",
                "Das Viech hat Eiszeiten überlebt, Dinosaurier, den ganzen Kram.",
                "Haut rein wie'n Presslufthammer mit Zähnen!"
            ],
            'Irrlicht': [
                "Irrlicht - sieht aus wie nix, aber hat's faustdick hinter den Schatten!",
                "War mal'n mystischer Geist in der Urzeit oder sowat.",
                "Schneller als du 'Scheiße' sagen kannst - und unsichtbar!"
            ]
        }
        
        pages = []
        messages = explanations.get(data['name'], [f"{data['name']}! Interessante Wahl!"])
        for msg in messages:
            pages.append(DialoguePage(msg, "Prof. Budde"))
        
        pages.append(DialoguePage(f"Bist du sicher, dass du {data['name']} als Partner willst?", "Prof. Budde"))
        pages.append(DialoguePage("[J] Ja, das is meins!  [N] Nee, lass mich nochmal gucken.", None))
        
        self.dialogue_box.show_dialogue(pages)
        self.confirm_choice = False  # Reset to false, will be set to true when J/Y is pressed
    
    def choose_starter(self):
        """Finalize starter choice and add to party."""
        self.logger.info(f"choose_starter() aufgerufen für Starter {self.selected_index}")
        starter = self.starters[self.selected_index]
        data = self.starter_data[self.selected_index]
        
        # Add to party
        success, message = self._safe_add_to_party(starter)
        
        if success:
            # Set story flags
            self._safe_set_story_flags({
                'has_starter': True,
                'starter_choice': data['id'],
                'professor_intro_done': True
            })
            
            # Show success message
            from engine.ui.dialogue import DialoguePage
            
            pages = [
                DialoguePage("Gute Wahl! Oder auch nich, ist mir scheißegal!", "Prof. Budde"),
                DialoguePage(f"{data['name']} gehört jetzt dir. Pass bloß auf das Viech auf!", "Prof. Budde"),
                DialoguePage("Hier, nimm noch die Monsterbälle. Damit fängste wilde Viecher.", "Prof. Budde"),
                DialoguePage("Ach ja, dein Kumpel Klaus war auch schon hier.", "Prof. Budde"),
                DialoguePage("Der Pisser hat sich auch eins geholt und meint, er wär jetzt der Größte.", "Prof. Budde"),
                DialoguePage("Zeig dem Idioten mal, wo der Hammer hängt!", "Prof. Budde"),
                DialoguePage("Und jetzt raus hier! Ich hab zu tun!", "Prof. Budde")
            ]
            
            self.dialogue_box.show_dialogue(pages)
            self.state = 'done'
        else:
            # Should not happen, but handle error
            from engine.ui.dialogue import DialoguePage
            
            pages = [
                DialoguePage("Hmm, irgendwat is schiefgelaufen...", "Prof. Budde"),
                DialoguePage("Versuch's nochmal!", "Prof. Budde")
            ]
            
            self.dialogue_box.show_dialogue(pages)
            self.state = 'selecting'
    
    def _safe_add_to_party(self, monster: MonsterInstance) -> tuple[bool, str]:
        """Sichere Methode zum Hinzufügen des Monsters zur Party."""
        try:
            if not hasattr(self.game, 'party_manager') or not self.game.party_manager:
                self.logger.warning("⚠️  Kein Party-Manager verfügbar!")
                return False, "Kein Party-Manager verfügbar"
            
            success, message = self.game.party_manager.add_to_party(monster)
            
            if success:
                self.logger.info(f"✅ Monster {monster.species_name} erfolgreich zur Party hinzugefügt")
                # Aktualisiere den Manager-Status
                self.manager_status['party'] = ManagerStatus(True)
            else:
                self.logger.error(f"❌ Fehler beim Hinzufügen zur Party: {message}")
                self.manager_status['party'] = ManagerStatus(False, message)
            
            return success, message
            
        except Exception as e:
            error_msg = f"Unerwarteter Fehler: {e}"
            self.logger.error(f"❌ {error_msg}")
            self.manager_status['party'] = ManagerStatus(False, error_msg)
            return False, error_msg
    
    def _safe_set_story_flags(self, flags: dict) -> bool:
        """Sichere Methode zum Setzen von Story-Flags."""
        try:
            if not hasattr(self.game, 'story_manager') or not self.game.story_manager:
                self.logger.warning("⚠️  Kein Story-Manager verfügbar!")
                # Erstelle Fallback Story-Manager
                self._create_fallback_story_manager()
                if not hasattr(self.game, 'story_manager') or not self.game.story_manager:
                    self.logger.error("❌ Konnte auch keinen Fallback Story-Manager erstellen!")
                    return False
            
            story = self.game.story_manager
            flags_set = 0
            
            # Setze alle Flags
            for flag_id, value in flags.items():
                try:
                    story.set_flag(flag_id, value)
                    flags_set += 1
                    self.logger.info(f"✅ Flag gesetzt: {flag_id} = {value}")
                except Exception as e:
                    self.logger.warning(f"⚠️  Konnte Flag {flag_id} nicht setzen: {e}")
            
            # Zusätzliche Flags für Story-Fortschritt
            try:
                story.set_flag('met_professor', True)
                story.set_flag('can_leave_town', True)
                story.set_flag('game_started', True)
                flags_set += 3
                self.logger.info("✅ Zusätzliche Story-Flags gesetzt")
            except Exception as e:
                self.logger.warning(f"⚠️  Konnte zusätzliche Flags nicht setzen: {e}")
            
            # Quest-Fortschritt (falls verfügbar)
            if hasattr(story, 'advance_quest'):
                try:
                    story.advance_quest('starter_quest')
                    self.logger.info("✅ Starter-Quest fortgeschritten")
                except Exception as e:
                    self.logger.warning(f"⚠️  Konnte Starter-Quest nicht fortsetzen: {e}")
            
            # Story-Phase-Update (falls verfügbar)
            if hasattr(story, '_check_phase_progression'):
                try:
                    story._check_phase_progression()
                    self.logger.info("✅ Story-Phase-Update durchgeführt")
                except Exception as e:
                    self.logger.warning(f"⚠️  Konnte Story-Phase nicht aktualisieren: {e}")
            
            self.logger.info(f"✅ {flags_set} Story-Flags erfolgreich gesetzt")
            self.manager_status['story'] = ManagerStatus(True)
            return True
            
        except Exception as e:
            error_msg = f"Unerwarteter Fehler beim Setzen der Story-Flags: {e}"
            self.logger.error(f"❌ {error_msg}")
            self.manager_status['story'] = ManagerStatus(False, error_msg)
            return False
    
    def _create_fallback_story_manager(self):
        """Erstellt einen minimalen Story-Manager als Fallback."""
        try:
            from engine.systems.story import StoryManager
            self.game.story_manager = StoryManager()
            self.logger.info("✅ Fallback Story-Manager erstellt")
            self.manager_status['story'] = ManagerStatus(True, fallback_active=True)
        except Exception as e:
            self.logger.error(f"❌ Fehler beim Erstellen des Fallback Story-Managers: {e}")
            # Erstelle einen Dummy-Manager
            class DummyStoryManager:
                def set_flag(self, flag_id: str, value: Any = True):
                    self.logger.debug(f"[DummyStoryManager] Setze Flag: {flag_id} = {value}")
                def get_flag(self, flag_id: str):
                    return False
                def advance_quest(self, quest_id: str):
                    self.logger.debug(f"[DummyStoryManager] Quest fortgeschritten: {quest_id}")
                def _check_phase_progression(self):
                    self.logger.debug("[DummyStoryManager] Story-Phase-Update durchgeführt")
            
            self.game.story_manager = DummyStoryManager()
            self.manager_status['story'] = ManagerStatus(True, fallback_active=True)
            self.logger.info("✅ Dummy Story-Manager als Fallback erstellt")
    
    def _return_to_field_scene(self):
        """Kehrt korrekt zur FieldScene zurück."""
        try:
            self.logger.info("🔄 Kehre zur FieldScene zurück...")
            
            # Pop current scene (StarterScene)
            self.game.pop_scene()
            
            # Stelle sicher, dass der Spieler wieder beweglich ist
            if hasattr(self.game, 'current_scene') and self.game.current_scene:
                if hasattr(self.game.current_scene, 'player') and self.game.current_scene.player:
                    self.game.current_scene.player.lock_movement(False)
                    self.logger.info("✅ Spieler-Bewegung freigegeben")
            
            self.logger.info("✅ Erfolgreich zur FieldScene zurückgekehrt")
            
        except Exception as e:
            self.logger.error(f"❌ Fehler beim Zurückkehren zur FieldScene: {e}")
            # Fallback: Direkt zur FieldScene wechseln
            try:
                from engine.scenes.field_scene import FieldScene
                self.game.pop_scene()
                self.game.push_scene(FieldScene, map_id='museum', spawn_point='entrance')
                self.logger.info("✅ Fallback-Wechsel zur FieldScene erfolgreich")
            except Exception as fallback_error:
                self.logger.error(f"❌ Auch Fallback fehlgeschlagen: {fallback_error}")
    
    def _check_manager_availability(self) -> None:
        """Check availability of all required managers and set fallbacks."""
        self.manager_status = {}
        
        # Check ResourceManager
        try:
            if hasattr(self.game, 'resources') and self.game.resources:
                self.manager_status['resources'] = ManagerStatus(available=True)
                self.logger.info("ResourceManager verfügbar")
            else:
                self.manager_status['resources'] = ManagerStatus(
                    available=False, 
                    error_message="ResourceManager nicht in Game-Instanz gefunden",
                    fallback_active=True
                )
                self.logger.warning("ResourceManager nicht verfügbar - Fallback aktiv")
        except Exception as e:
            self.manager_status['resources'] = ManagerStatus(
                available=False, 
                error_message=f"Fehler beim Zugriff auf ResourceManager: {e}",
                fallback_active=True
            )
            self.logger.error(f"Fehler beim Zugriff auf ResourceManager: {e}")
        
        # Check PartyManager
        try:
            if hasattr(self.game, 'party_manager') and self.game.party_manager:
                self.manager_status['party'] = ManagerStatus(available=True)
                self.logger.info("PartyManager verfügbar")
            else:
                self.manager_status['party'] = ManagerStatus(
                    available=False, 
                    error_message="PartyManager nicht in Game-Instanz gefunden",
                    fallback_active=True
                )
                self.logger.warning("PartyManager nicht verfügbar - Fallback aktiv")
        except Exception as e:
            self.manager_status['party'] = ManagerStatus(
                available=False, 
                error_message=f"Fehler beim Zugriff auf PartyManager: {e}",
                fallback_active=True
            )
            self.logger.error(f"Fehler beim Zugriff auf PartyManager: {e}")
        
        # Check StoryManager
        try:
            if hasattr(self.game, 'story_manager') and self.game.story_manager:
                self.manager_status['story'] = ManagerStatus(available=True)
                self.logger.info("StoryManager verfügbar")
            else:
                self.manager_status['story'] = ManagerStatus(
                    available=False, 
                    error_message="StoryManager nicht in Game-Instanz gefunden",
                    fallback_active=True
                )
                self.logger.warning("StoryManager nicht verfügbar - Fallback aktiv")
        except Exception as e:
            self.manager_status['story'] = ManagerStatus(
                available=False, 
                error_message=f"Fehler beim Zugriff auf StoryManager: {e}",
                fallback_active=True
            )
            self.logger.error(f"❌ Fehler beim Zugriff auf StoryManager: {e}")
        
        # Check SpriteManager
        try:
            if hasattr(self.game, 'sprite_manager') and self.game.sprite_manager:
                self.manager_status['sprite'] = ManagerStatus(available=True)
                self.logger.info("SpriteManager verfügbar")
            else:
                self.manager_status['sprite'] = ManagerStatus(
                    available=False, 
                    error_message="SpriteManager nicht in Game-Instanz gefunden",
                    fallback_active=True
                )
                self.logger.warning("SpriteManager nicht verfügbar - Fallback aktiv")
        except Exception as e:
            self.manager_status['sprite'] = ManagerStatus(
                available=False, 
                error_message=f"Fehler beim Zugriff auf SpriteManager: {e}",
                fallback_active=True
            )
            self.logger.error(f"Fehler beim Zugriff auf SpriteManager: {e}")
    
    def log_manager_status(self):
        """Loggt den Status aller Manager für Debugging."""
        self.logger.info("\n=== Manager-Status in StarterScene ===")
        for manager_name, status in self.manager_status.items():
            if status.available:
                fallback_info = " (Fallback aktiv)" if status.fallback_active else ""
                self.logger.info(f"✅ {manager_name}: Verfügbar{fallback_info}")
            else:
                error_info = f" - {status.error_message}" if status.error_message else ""
                self.logger.error(f"❌ {manager_name}: Nicht verfügbar{error_info}")
        self.logger.info("=====================================\n")
    
    def update(self, dt: float):
        """Update the scene with enhanced animations."""
        # Update dialogue
        if self.dialogue_box.is_open():
            self.dialogue_box.update(dt)
        
        # Update hover animation
        if self.state == 'selecting':
            self.hover_timer += dt
            self.hover_offset = pygame.math.Vector2(0, -abs(math.sin(self.hover_timer * 3)) * 5)
            
            # Update selection pulse
            self.selection_pulse += dt * 4
            if self.selection_pulse > 2 * math.pi:
                self.selection_pulse = 0
        
        # Update help timer
        if self.show_help:
            self.help_timer += dt
    
    def draw(self, surface: pygame.Surface):
        """Draw the scene with enhanced visual feedback."""
        # Background - Professor's lab
        surface.fill((40, 35, 30))  # Dark brown lab
        
        # Draw lab details
        self._draw_lab_background(surface)
        
        # Draw starter cards if selecting
        if self.state in ['selecting', 'confirming']:
            self._draw_starter_cards(surface)
        
        # Draw dialogue box
        if self.dialogue_box.is_open():
            self.dialogue_box.draw(surface)
        
        # Draw title
        if self.state != 'done':
            if self.big_font:
                title = self.big_font.render("Wähle dein Starter-Monster!", True, Colors.WHITE)
                title_rect = title.get_rect(center=(LOGICAL_WIDTH // 2, 20))
                surface.blit(title, title_rect)
        
        # Draw help overlay
        if self.show_help:
            self._draw_help_overlay(surface)
        
        # Draw enhanced control hints
        self._draw_control_hints(surface)
    
    def _draw_lab_background(self, surface: pygame.Surface):
        """Draw laboratory background elements."""
        # Draw some lab equipment as rectangles
        
        # Fossil machine
        pygame.draw.rect(surface, (60, 55, 50), (10, 40, 30, 40))
        pygame.draw.rect(surface, (80, 75, 70), (10, 40, 30, 40), 2)
        
        # Computer
        pygame.draw.rect(surface, (30, 30, 40), (LOGICAL_WIDTH - 40, 40, 30, 20))
        pygame.draw.rect(surface, (100, 200, 255), (LOGICAL_WIDTH - 38, 42, 26, 16))
        
        # Table
        pygame.draw.rect(surface, (90, 70, 50), (0, 100, LOGICAL_WIDTH, 20))
        pygame.draw.rect(surface, (70, 50, 30), (0, 100, LOGICAL_WIDTH, 20), 2)
    
    def _draw_starter_cards(self, surface: pygame.Surface):
        """Draw the starter selection cards with enhanced visual feedback."""
        # Calculate total width
        total_width = (self.card_width * 4) + (self.card_spacing * 3)
        start_x = (LOGICAL_WIDTH - total_width) // 2
        y = 50
        
        for i, (monster, data) in enumerate(zip(self.starters, self.starter_data)):
            x = start_x + (self.card_width + self.card_spacing) * i
            
            # Apply hover effect to selected card
            offset_y = 0
            if i == self.selected_index and self.state == 'selecting':
                offset_y = self.hover_offset.y
            
            # Draw card background
            card_rect = pygame.Rect(x, y + offset_y, self.card_width, self.card_height)
            
            # Enhanced highlight for selected card
            if i == self.selected_index:
                # Pulsing glow effect
                glow_intensity = abs(math.sin(self.selection_pulse)) * 0.5 + 0.5
                glow_color = tuple(int(c * glow_intensity) for c in self.selection_highlight_color)
                pygame.draw.rect(surface, glow_color, card_rect.inflate(6, 6))
                pygame.draw.rect(surface, self.selection_highlight_color, card_rect.inflate(4, 4))
            
            # Card background
            pygame.draw.rect(surface, (50, 45, 40), card_rect)
            pygame.draw.rect(surface, Colors.WHITE, card_rect, 2)
            
            # Draw monster sprite (try real sprite first, fallback to colored rectangle)
            sprite_rect = pygame.Rect(x + 10, y + 5 + offset_y, 40, 40)
            
            # Try to get real monster sprite with robust fallback
            monster_sprite = self._safe_get_monster_sprite(data.get('id', i + 1))
            
            if monster_sprite:
                # Draw real monster sprite
                surface.blit(monster_sprite, sprite_rect)
            else:
                # Create and use placeholder sprite
                placeholder_sprite = self._create_placeholder_sprite(data.get('id', i + 1), data['color'])
                surface.blit(placeholder_sprite, sprite_rect)
            
            # Draw monster name
            if self.font:
                name_text = self.font.render(data['name'], True, Colors.WHITE)
                name_rect = name_text.get_rect(centerx=x + self.card_width // 2, 
                                              y=y + 48 + offset_y)
                surface.blit(name_text, name_rect)
                
                # Draw type
                type_text = self.font.render(data['types'][0], True, data['color'])
                type_rect = type_text.get_rect(centerx=x + self.card_width // 2,
                                              y=y + 60 + offset_y)
                surface.blit(type_text, type_rect)
                
                # Draw level
                level_text = self.font.render("Lv.5", True, Colors.WHITE)
                level_rect = level_text.get_rect(centerx=x + self.card_width // 2,
                                               y=y + 70 + offset_y)
                surface.blit(level_text, level_rect)
    
    def _draw_control_hints(self, surface: pygame.Surface):
        """Draw control hints based on current state."""
        if not self.font:
            return
        
        # State-specific hints
        if self.state == 'selecting':
            hint = self.font.render("[A/D] Wählen  [E] Bestätigen  [H] Hilfe", True, Colors.WHITE)
            hint_rect = hint.get_rect(center=(LOGICAL_WIDTH // 2, LOGICAL_HEIGHT - 20))
            surface.blit(hint, hint_rect)
            
            # Additional info
            info = self.font.render(f"Starter {self.selected_index + 1} von 4 ausgewählt", True, Colors.YELLOW)
            info_rect = info.get_rect(center=(LOGICAL_WIDTH // 2, LOGICAL_HEIGHT - 35))
            surface.blit(info, info_rect)
            
        elif self.state == 'confirming':
            hint = self.font.render("[J] Ja, das is meins!  [N] Nee, lass mich nochmal gucken", True, Colors.WHITE)
            hint_rect = hint.get_rect(center=(LOGICAL_WIDTH // 2, LOGICAL_HEIGHT - 20))
            surface.blit(hint, hint_rect)
            
        elif self.state == 'done':
            hint = self.font.render("Drücke [E] um fortzufahren...", True, Colors.WHITE)
            hint_rect = hint.get_rect(center=(LOGICAL_WIDTH // 2, LOGICAL_HEIGHT - 20))
            surface.blit(hint, hint_rect)
    
    def _draw_help_overlay(self, surface: pygame.Surface):
        """Draw help overlay with control information."""
        if not self.font:
            return
            
        # Semi-transparent overlay
        overlay = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))
        
        # Help content
        help_lines = [
            "=== HILFE ===",
            "",
            "Steuerung:",
            "[A/D] - Starter auswählen",
            "[E] - Bestätigen",
            "[H] - Hilfe ein/ausschalten",
            "[ESC] - Zurück",
            "",
            "Tipps:",
            "- Wähle dein Starter-Monster sorgfältig!",
            "- Jedes Monster hat eigene Stärken",
            "- Du kannst deine Wahl nicht rückgängig machen",
            "",
            "Drücke [H] um Hilfe zu schließen"
        ]
        
        y_offset = 20
        for line in help_lines:
            if line.startswith("==="):
                color = Colors.YELLOW
            elif line.startswith("[") and line.endswith("]"):
                color = Colors.CYAN
            elif line.startswith("-"):
                color = Colors.LIGHT_GREEN
            else:
                color = Colors.WHITE
            
            text = self.font.render(line, True, color)
            text_rect = text.get_rect(center=(LOGICAL_WIDTH // 2, y_offset))
            surface.blit(text, text_rect)
            y_offset += 15 
