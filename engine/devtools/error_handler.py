"""
Zentrales Fehlerbehandlungssystem für Untold Story.
Protokolliert Fehler, zeigt Warnungen an und ermöglicht Fehleranalyse.
"""

import sys
import traceback
import logging
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from pathlib import Path
from enum import Enum
import pygame


class ErrorSeverity(Enum):
    """Schweregrade für Fehler."""
    INFO = "info"           # Informative Meldung
    WARNING = "warning"     # Warnung, Spiel läuft weiter
    ERROR = "error"         # Schwerer Fehler, Funktion fehlgeschlagen
    CRITICAL = "critical"   # Kritischer Fehler, Spiel muss beendet werden


@dataclass
class ErrorEntry:
    """Ein protokollierter Fehler."""
    timestamp: float
    severity: ErrorSeverity
    message: str
    details: str
    source: str
    handled: bool = False


class ErrorHandler:
    """Zentrales Fehlerbehandlungssystem."""
    
    def __init__(self, game):
        """
        Initialisiere Fehlerbehandlung.
        
        Args:
            game: Spielinstanz
        """
        self.game = game
        self.error_log: List[ErrorEntry] = []
        self.max_log_size = 1000
        self.show_overlay = False
        
        # Fehlerstatistiken
        self.error_stats = {
            ErrorSeverity.INFO: 0,
            ErrorSeverity.WARNING: 0,
            ErrorSeverity.ERROR: 0,
            ErrorSeverity.CRITICAL: 0
        }
        
        # UI-Elemente
        self.font = pygame.font.Font(None, 14)
        self.small_font = pygame.font.Font(None, 12)
        
        # Logging einrichten
        self._setup_logging()
        
        # Exception Handler registrieren
        sys.excepthook = self.handle_exception
    
    def _setup_logging(self) -> None:
        """Richte Logging-System ein."""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Logging-Datei mit Zeitstempel
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"error_log_{timestamp}.txt"
        
        # Logging-Format
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # File Handler
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        
        # Logger konfigurieren
        self.logger = logging.getLogger('UntoldStory')
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(file_handler)
    
    def log_error(self, 
                  severity: ErrorSeverity,
                  message: str,
                  details: str = "",
                  source: str = "") -> None:
        """
        Protokolliere einen Fehler.
        
        Args:
            severity: Schweregrad des Fehlers
            message: Fehlermeldung
            details: Detaillierte Fehlerbeschreibung
            source: Fehlerquelle (Datei/Funktion)
        """
        # Erstelle Fehlereintrag
        error = ErrorEntry(
            timestamp=time.time(),
            severity=severity,
            message=message,
            details=details,
            source=source
        )
        
        # Aktualisiere Statistiken
        self.error_stats[severity] += 1
        
        # Füge zum Log hinzu
        self.error_log.append(error)
        if len(self.error_log) > self.max_log_size:
            self.error_log.pop(0)
        
        # Ins Logfile schreiben
        log_level = {
            ErrorSeverity.INFO: logging.INFO,
            ErrorSeverity.WARNING: logging.WARNING,
            ErrorSeverity.ERROR: logging.ERROR,
            ErrorSeverity.CRITICAL: logging.CRITICAL
        }[severity]
        
        self.logger.log(log_level, f"{message} - {details}")
        
        # Bei kritischen Fehlern Spiel beenden
        if severity == ErrorSeverity.CRITICAL:
            self.handle_critical_error(error)
    
    def handle_exception(self, 
                        exc_type: type,
                        exc_value: Exception,
                        exc_traceback: traceback.TracebackType) -> None:
        """
        Behandle unbehandelte Ausnahmen.
        
        Args:
            exc_type: Ausnahmetyp
            exc_value: Ausnahmewert
            exc_traceback: Traceback
        """
        # Erstelle Fehlermeldung
        error_msg = f"{exc_type.__name__}: {str(exc_value)}"
        error_details = "".join(traceback.format_tb(exc_traceback))
        
        # Protokolliere Fehler
        self.log_error(
            severity=ErrorSeverity.CRITICAL,
            message=error_msg,
            details=error_details,
            source=f"{exc_traceback.tb_frame.f_code.co_filename}:{exc_traceback.tb_lineno}"
        )
    
    def handle_critical_error(self, error: ErrorEntry) -> None:
        """
        Behandle kritische Fehler.
        
        Args:
            error: Der aufgetretene Fehler
        """
        # Zeige Fehlermeldung
        print("\n=== KRITISCHER FEHLER ===")
        print(f"Meldung: {error.message}")
        print(f"Details: {error.details}")
        print(f"Quelle: {error.source}")
        print("Das Spiel wird beendet.")
        
        # Spiel beenden
        if hasattr(self.game, 'quit'):
            self.game.quit()
        else:
            sys.exit(1)
    
    def draw_overlay(self, surface: pygame.Surface) -> None:
        """
        Zeichne Fehlerüberlagerung.
        
        Args:
            surface: Zeichenfläche
        """
        if not self.show_overlay:
            return
        
        # Hintergrund
        width = 300
        height = 200
        x = surface.get_width() - width - 10
        y = 10
        
        bg_surf = pygame.Surface((width, height))
        bg_surf.fill((0, 0, 0))
        bg_surf.set_alpha(200)
        surface.blit(bg_surf, (x, y))
        
        # Titel
        title = "=== FEHLERÜBERWACHUNG ==="
        title_surf = self.font.render(title, True, (255, 255, 0))
        surface.blit(title_surf, (x + 5, y + 5))
        
        # Statistiken
        y_offset = y + 25
        for severity, count in self.error_stats.items():
            color = {
                ErrorSeverity.INFO: (255, 255, 255),
                ErrorSeverity.WARNING: (255, 255, 0),
                ErrorSeverity.ERROR: (255, 128, 0),
                ErrorSeverity.CRITICAL: (255, 0, 0)
            }[severity]
            
            text = f"{severity.value}: {count}"
            text_surf = self.small_font.render(text, True, color)
            surface.blit(text_surf, (x + 5, y_offset))
            y_offset += 15
        
        # Letzte Fehler
        y_offset += 10
        text_surf = self.font.render("Letzte Fehler:", True, (255, 255, 255))
        surface.blit(text_surf, (x + 5, y_offset))
        y_offset += 20
        
        for error in reversed(self.error_log[-5:]):
            color = {
                ErrorSeverity.INFO: (255, 255, 255),
                ErrorSeverity.WARNING: (255, 255, 0),
                ErrorSeverity.ERROR: (255, 128, 0),
                ErrorSeverity.CRITICAL: (255, 0, 0)
            }[error.severity]
            
            text = f"{error.severity.value}: {error.message}"
            text_surf = self.small_font.render(text, True, color)
            surface.blit(text_surf, (x + 5, y_offset))
            y_offset += 12
    
    def toggle_overlay(self) -> None:
        """Schalte Fehlerüberlagerung um."""
        self.show_overlay = not self.show_overlay
    
    def get_error_summary(self) -> Dict[str, Any]:
        """
        Erstelle Fehlerzusammenfassung.
        
        Returns:
            Zusammenfassung der Fehlerstatistiken
        """
        return {
            "total_errors": sum(self.error_stats.values()),
            "by_severity": self.error_stats,
            "recent_errors": [
                {
                    "time": time.strftime("%H:%M:%S", time.localtime(e.timestamp)),
                    "severity": e.severity.value,
                    "message": e.message
                }
                for e in self.error_log[-10:]
            ]
        }
