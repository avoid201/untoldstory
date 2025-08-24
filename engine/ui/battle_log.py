"""
Battle Logging System for Untold Story.
Handles battle message history, categorization, and export functionality.
"""

import pygame
import json
import time
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from enum import Enum, auto
from pathlib import Path

from engine.core.config import Colors, LOGICAL_WIDTH, LOGICAL_HEIGHT


class MessagePriority(Enum):
    """Message priority levels."""
    CRITICAL = auto()  # Critical hits, fainting, etc.
    NORMAL = auto()    # Regular battle events
    DETAIL = auto()    # Detailed information
    DEBUG = auto()     # Debug information


class MessageCategory(Enum):
    """Message categories for organization."""
    ATTACK = auto()        # Attack messages
    DAMAGE = auto()        # Damage dealt/taken
    STATUS = auto()        # Status effects
    HEALING = auto()       # Healing and recovery
    TAMING = auto()        # Taming attempts
    ITEMS = auto()         # Item usage
    SWITCHING = auto()     # Monster switching
    BATTLE_EVENTS = auto() # General battle events
    SYSTEM = auto()        # System messages


@dataclass
class BattleMessage:
    """Individual battle message with metadata."""
    text: str
    timestamp: float
    priority: MessagePriority
    category: MessageCategory
    actor: Optional[str] = None
    target: Optional[str] = None
    value: Optional[int] = None
    is_critical: bool = False
    is_super_effective: bool = False
    is_miss: bool = False
    is_fainted: bool = False


class BattleLog:
    """Comprehensive battle logging system."""
    
    def __init__(self, max_messages: int = 100):
        self.messages: List[BattleMessage] = []
        self.max_messages = max_messages
        self.scroll_position = 0
        self.auto_scroll = True
        
        # Message templates for Ruhrpott slang
        self.message_templates = self._init_message_templates()
        
        # Color coding by message type
        self.priority_colors = {
            MessagePriority.CRITICAL: Colors.RED,
            MessagePriority.NORMAL: Colors.WHITE,
            MessagePriority.DETAIL: Colors.LIGHT_BLUE,
            MessagePriority.DEBUG: Colors.YELLOW
        }
        
        # Category icons (simple text representations)
        self.category_icons = {
            MessageCategory.ATTACK: "⚔️",
            MessageCategory.DAMAGE: "💥",
            MessageCategory.STATUS: "🔮",
            MessageCategory.HEALING: "💚",
            MessageCategory.TAMING: "🎯",
            MessageCategory.ITEMS: "📦",
            MessageCategory.SWITCHING: "🔄",
            MessageCategory.BATTLE_EVENTS: "⚡",
            MessageCategory.SYSTEM: "ℹ️"
        }
        
        # Font setup
        self.font = pygame.font.Font(None, 12)
        self.small_font = pygame.font.Font(None, 10)
        
        # Display settings
        self.log_position = (10, LOGICAL_HEIGHT - 120)
        self.log_width = LOGICAL_WIDTH - 20
        self.log_height = 100
        self.line_height = 14
        self.visible_lines = self.log_height // self.line_height
        
        # Export settings
        self.export_dir = Path("logs/battles")
        self.export_dir.mkdir(parents=True, exist_ok=True)
    
    def _init_message_templates(self) -> Dict[str, str]:
        """Initialize Ruhrpott slang message templates."""
        return {
            # Attack messages
            'attack_start': [
                "{actor} greift {target} mit {move} an!",
                "{actor} macht sich bereit für {move} gegen {target}!",
                "Los geht's! {actor} nutzt {move}!"
            ],
            'attack_hit': [
                "{actor} trifft {target} mit {move}!",
                "Volltreffer! {move} von {actor} trifft {target}!",
                "Bam! {actor} hat {target} mit {move} erwischt!"
            ],
            'attack_miss': [
                "{actor} verfehlt {target} mit {move}!",
                "Daneben! {move} von {actor} geht ins Leere!",
                "Verpasst! {actor} hat {target} nicht getroffen!"
            ],
            
            # Damage messages
            'damage_dealt': [
                "{target} erleidet {damage} Schaden!",
                "Das hat gesessen! {damage} Schaden für {target}!",
                "Voll ins Schwarze! {target} bekommt {damage} ab!"
            ],
            'critical_hit': [
                "KRITISCHER TREFFER! {target} erleidet {damage} Schaden!",
                "Volltreffer! {target} bekommt {damage} Schaden!",
                "Das war heftig! Kritischer Treffer mit {damage} Schaden!"
            ],
            'super_effective': [
                "Das war sehr effektiv! {target} erleidet {damage} Schaden!",
                "Voll ins Schwarze! Sehr effektiv gegen {target}!",
                "Perfekt! {damage} Schaden durch Typ-Vorteil!"
            ],
            'not_very_effective': [
                "Das war nicht sehr effektiv... {target} erleidet {damage} Schaden.",
                "Schwacher Treffer! Nur {damage} Schaden für {target}.",
                "Nicht optimal... {damage} Schaden durch Typ-Nachteil."
            ],
            
            # Status messages
            'status_applied': [
                "{target} ist jetzt {status}!",
                "{status} hat {target} erwischt!",
                "Status-Effekt! {target} leidet unter {status}!"
            ],
            'status_healed': [
                "{target} ist von {status} geheilt!",
                "Gut gemacht! {target} ist wieder fit!",
                "Status weg! {target} ist wieder gesund!"
            ],
            
            # Taming messages
            'taming_attempt': [
                "{actor} versucht {target} zu zähmen!",
                "Zähmungsversuch! {actor} will {target} überzeugen!",
                "Los geht's! {actor} versucht {target} zu gewinnen!"
            ],
            'taming_success': [
                "Erfolg! {target} wurde erfolgreich gezähmt!",
                "Geschafft! {target} ist jetzt Teil des Teams!",
                "Perfekt! {target} hat sich dem Team angeschlossen!"
            ],
            'taming_failure': [
                "{target} hat den Zähmungsversuch abgelehnt!",
                "Nicht geschafft! {target} bleibt wild!",
                "Schade! {target} will nicht mitkommen!"
            ],
            
            # Item messages
            'item_used': [
                "{actor} benutzt {item}!",
                "Item aktiviert! {actor} nutzt {item}!",
                "Los geht's! {item} wird von {actor} eingesetzt!"
            ],
            'item_healing': [
                "{target} wurde um {amount} HP geheilt!",
                "Heilung! {target} bekommt {amount} HP zurück!",
                                "Gut gemacht! {target} ist wieder fit!"
            ],
            
            # Battle events
            'monster_fainted': [
                "{monster} ist besiegt!",
                "Das war's! {monster} ist am Ende!",
                "Game Over für {monster}!"
            ],
            'monster_switched': [
                "{old_monster} wird durch {new_monster} ersetzt!",
                "Wechsel! {new_monster} kommt ins Rennen!",
                "Neuer Spieler! {new_monster} übernimmt!"
            ],
            'battle_won': [
                "Du hast den Kampf gewonnen!",
                "Geschafft! Der Sieg gehört dir!",
                "Perfekt! Du bist der Gewinner!"
            ],
            'battle_lost': [
                "Du hast den Kampf verloren...",
                "Schade! Das war nichts...",
                "Nächstes Mal! Du warst nicht stark genug!"
            ]
        }
    
    def add_message(self, text: str, priority: MessagePriority = MessagePriority.NORMAL,
                   category: MessageCategory = MessageCategory.BATTLE_EVENTS,
                   actor: Optional[str] = None, target: Optional[str] = None,
                   value: Optional[int] = None, **kwargs) -> None:
        """Add a new message to the battle log."""
        message = BattleMessage(
            text=text,
            timestamp=time.time(),
            priority=priority,
            category=category,
            actor=actor,
            target=target,
            value=value,
            **kwargs
        )
        
        self.messages.append(message)
        
        # Maintain maximum message limit
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)
        
        # Auto-scroll to bottom for new messages
        if self.auto_scroll:
            self.scroll_to_bottom()
    
    def add_template_message(self, template_key: str, priority: MessagePriority = MessagePriority.NORMAL,
                           category: MessageCategory = MessageCategory.BATTLE_EVENTS,
                           **kwargs) -> None:
        """Add a message using a template."""
        if template_key in self.message_templates:
            import random
            template = random.choice(self.message_templates[template_key])
            text = template.format(**kwargs)
            self.add_message(text, priority, category, **kwargs)
        else:
            # Fallback to direct text
            self.add_message(str(template_key), priority, category, **kwargs)
    
    def add_attack_message(self, actor: str, target: str, move: str, damage: int,
                          is_critical: bool = False, is_super_effective: bool = False,
                          is_miss: bool = False) -> None:
        """Add an attack-related message."""
        if is_miss:
            self.add_template_message('attack_miss', MessagePriority.NORMAL, 
                                   MessageCategory.ATTACK, actor=actor, target=target, move=move)
        else:
            self.add_template_message('attack_hit', MessagePriority.NORMAL, 
                                   MessageCategory.ATTACK, actor=actor, target=target, move=move)
            
            # Add damage message
            if is_critical:
                self.add_template_message('critical_hit', MessagePriority.CRITICAL, 
                                       MessageCategory.DAMAGE, target=target, damage=damage)
            elif is_super_effective:
                self.add_template_message('super_effective', MessagePriority.NORMAL, 
                                       MessageCategory.DAMAGE, target=target, damage=damage)
            else:
                self.add_template_message('damage_dealt', MessagePriority.NORMAL, 
                                       MessageCategory.DAMAGE, target=target, damage=damage)
    
    def add_status_message(self, target: str, status: str, is_applied: bool = True) -> None:
        """Add a status effect message."""
        if is_applied:
            self.add_template_message('status_applied', MessagePriority.NORMAL, 
                                   MessageCategory.STATUS, target=target, status=status)
        else:
            self.add_template_message('status_healed', MessagePriority.NORMAL, 
                                   MessageCategory.HEALING, target=target, status=status)
    
    def add_taming_message(self, actor: str, target: str, success: bool) -> None:
        """Add a taming attempt message."""
        if success:
            self.add_template_message('taming_success', MessagePriority.CRITICAL, 
                                   MessageCategory.TAMING, target=target)
        else:
            self.add_template_message('taming_failure', MessagePriority.NORMAL, 
                                   MessageCategory.TAMING, target=target)
    
    def add_item_message(self, actor: str, item: str, target: Optional[str] = None,
                        healing_amount: Optional[int] = None) -> None:
        """Add an item usage message."""
        if healing_amount:
            self.add_template_message('item_healing', MessagePriority.NORMAL, 
                                   MessageCategory.HEALING, target=target, amount=healing_amount)
        else:
            self.add_template_message('item_used', MessagePriority.NORMAL, 
                                   MessageCategory.ITEMS, actor=actor, item=item)
    
    def scroll_up(self) -> None:
        """Scroll the log up."""
        self.scroll_position = max(0, self.scroll_position - 1)
        self.auto_scroll = False
    
    def scroll_down(self) -> None:
        """Scroll the log down."""
        max_scroll = max(0, len(self.messages) - self.visible_lines)
        self.scroll_position = min(max_scroll, self.scroll_position + 1)
        self.auto_scroll = False
    
    def scroll_to_bottom(self) -> None:
        """Scroll to the bottom of the log."""
        self.scroll_position = max(0, len(self.messages) - self.visible_lines)
        self.auto_scroll = True
    
    def handle_input(self, key: int) -> None:
        """Handle input for log navigation."""
        if key == pygame.K_UP:
            self.scroll_up()
        elif key == pygame.K_DOWN:
            self.scroll_down()
        elif key == pygame.K_PAGEUP:
            self.scroll_position = max(0, self.scroll_position - self.visible_lines)
            self.auto_scroll = False
        elif key == pygame.K_PAGEDOWN:
            max_scroll = max(0, len(self.messages) - self.visible_lines)
            self.scroll_position = min(max_scroll, self.scroll_position + self.visible_lines)
            self.auto_scroll = False
        elif key == pygame.K_HOME:
            self.scroll_position = 0
            self.auto_scroll = False
        elif key == pygame.K_END:
            self.scroll_to_bottom()
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the battle log interface."""
        x, y = self.log_position
        
        # Log background
        pygame.draw.rect(surface, Colors.UI_BG, (x, y, self.log_width, self.log_height))
        pygame.draw.rect(surface, Colors.UI_BORDER, (x, y, self.log_width, self.log_height), 2)
        
        # Title bar
        title = self.font.render("Kampf-Log", True, Colors.WHITE)
        surface.blit(title, (x + 5, y + 2))
        
        # Scroll indicator
        if len(self.messages) > self.visible_lines:
            scroll_percent = self.scroll_position / max(1, len(self.messages) - self.visible_lines)
            scroll_y = y + 20 + int(scroll_percent * (self.log_height - 40))
            pygame.draw.rect(surface, Colors.UI_SELECTED, (x + self.log_width - 8, scroll_y, 6, 20))
        
        # Messages
        start_idx = self.scroll_position
        end_idx = min(start_idx + self.visible_lines, len(self.messages))
        
        for i, message in enumerate(self.messages[start_idx:end_idx]):
            line_y = y + 20 + (i * self.line_height)
            
            # Category icon
            icon = self.category_icons.get(message.category, "ℹ️")
            icon_surface = self.small_font.render(icon, True, Colors.WHITE)
            surface.blit(icon_surface, (x + 5, line_y))
            
            # Message text with priority color
            color = self.priority_colors.get(message.priority, Colors.WHITE)
            text_surface = self.font.render(message.text, True, color)
            
            # Truncate text if too long
            if text_surface.get_width() > self.log_width - 30:
                # Find last space before cutoff
                text = message.text
                while text and self.font.render(text + "...", True, color).get_width() > self.log_width - 30:
                    text = text[:-1]
                    if text.rfind(' ') > 0:
                        text = text[:text.rfind(' ')]
                text += "..."
                text_surface = self.font.render(text, True, color)
            
            surface.blit(text_surface, (x + 20, line_y))
            
            # Special effect indicators
            if message.is_critical:
                crit_indicator = self.small_font.render("CRIT!", True, Colors.YELLOW)
                surface.blit(crit_indicator, (x + self.log_width - 40, line_y))
            elif message.is_super_effective:
                se_indicator = self.small_font.render("SE!", True, Colors.MAGENTA)
                surface.blit(se_indicator, (x + self.log_width - 30, line_y))
    
    def export_to_file(self, filename: Optional[str] = None) -> str:
        """Export the battle log to a text file."""
        if not filename:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"battle_log_{timestamp}.txt"
        
        filepath = self.export_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("=== UNTOLD STORY - BATTLE LOG ===\n")
            f.write(f"Exportiert am: {time.strftime('%d.%m.%Y %H:%M:%S')}\n")
            f.write("=" * 50 + "\n\n")
            
            for message in self.messages:
                timestamp = time.strftime("%H:%M:%S", time.localtime(message.timestamp))
                category = message.category.name
                priority = message.priority.name
                
                f.write(f"[{timestamp}] [{category}/{priority}] {message.text}\n")
                
                if message.actor or message.target or message.value:
                    details = []
                    if message.actor:
                        details.append(f"Akteur: {message.actor}")
                    if message.target:
                        details.append(f"Ziel: {message.target}")
                    if message.value is not None:
                        details.append(f"Wert: {message.value}")
                    if message.is_critical:
                        details.append("KRITISCHER TREFFER")
                    if message.is_super_effective:
                        details.append("SEHR EFFEKTIV")
                    
                    f.write(f"  Details: {', '.join(details)}\n")
                
                f.write("\n")
        
        return str(filepath)
    
    def export_to_json(self, filename: Optional[str] = None) -> str:
        """Export the battle log to a JSON file."""
        if not filename:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"battle_log_{timestamp}.json"
        
        filepath = self.export_dir / filename
        
        # Convert messages to serializable format
        export_data = {
            'export_timestamp': time.time(),
            'export_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_messages': len(self.messages),
            'messages': []
        }
        
        for message in self.messages:
            export_data['messages'].append({
                'text': message.text,
                'timestamp': message.timestamp,
                'priority': message.priority.name,
                'category': message.category.name,
                'actor': message.actor,
                'target': message.target,
                'value': message.value,
                'is_critical': message.is_critical,
                'is_super_effective': message.is_super_effective,
                'is_miss': message.is_miss,
                'is_fainted': message.is_fainted
            })
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        return str(filepath)
    
    def clear(self) -> None:
        """Clear all messages from the log."""
        self.messages.clear()
        self.scroll_position = 0
        self.auto_scroll = True
    
    def get_message_count(self) -> int:
        """Get the total number of messages."""
        return len(self.messages)
    
    def get_messages_by_category(self, category: MessageCategory) -> List[BattleMessage]:
        """Get all messages of a specific category."""
        return [msg for msg in self.messages if msg.category == category]
    
    def get_messages_by_priority(self, priority: MessagePriority) -> List[BattleMessage]:
        """Get all messages of a specific priority."""
        return [msg for msg in self.messages if msg.priority == priority]
    
    def search_messages(self, search_term: str) -> List[BattleMessage]:
        """Search messages by text content."""
        search_term = search_term.lower()
        return [msg for msg in self.messages if search_term in msg.text.lower()]
